"""Privacy allowlist and independent oracle for declaration-family web->HTKK native cases.

Cases (one per form) are registered in htkk-native-cases.json with driver
``declaration-web-import-inspect``. Their input XML comes from the htkk_web product producer
``scripts/generate-htkk-declaration-reference.mjs`` (DeclarationEngine), never from this repo.

This module never executes application code and never writes XML. It:

* pins each case's declaration identity (Menu.xml 5.8.1 MaToKhai/VersionXML), period,
  synthetic NNT, web draft service identity, dates, annex elements and leaf count;
* accepts only leaf texts that are numbers/dates/booleans or belong to the case's reviewed
  synthetic/template text allowlist (no free text can carry real taxpayer data);
* re-checks the case expectations from the INDEPENDENT design oracles already reviewed in
  this repo (htkk-workbook-native-cases.json, htkk-descriptor-native-cases.json and the
  Decimal recomputation in htkk_hkd_web_cases.py), not from the TypeScript engine;
* validates a native re-export (native service identity, current creation date, synthetic
  identity, bounded texts) and compares it with the web input over the whole tree. Only the
  creation date and the four service-identity leaves follow the proven native rules.
"""
import datetime, decimal, importlib.util, io, pathlib, re
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).parent
NS = 'http://kekhaithue.gdt.gov.vn/TKhaiThue'
XSI = 'http://www.w3.org/2001/XMLSchema-instance'
MAX_XML = 262144
CODES = frozenset(('CASE', 'SIZE', 'ENCODING', 'DECLARATION', 'PARSE', 'NAMESPACE', 'ATTRIBUTES', 'STRUCTURE',
                   'IDENTITY', 'PERIOD', 'SERVICE', 'DATE', 'PRIVACY', 'LEAF_COUNT', 'VALUE', 'MANIFEST'))


def _load(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / file)
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value); return value


workbook_design = _load('declaration_workbook_design', 'htkk_workbook_native_cases.py')
descriptor_design = _load('declaration_descriptor_design', 'htkk_descriptor_native_cases.py')
hkd_design = _load('declaration_hkd_design', 'htkk_hkd_web_cases.py')


# Bounded, value-free description of a rejected leaf (never its text). A rejected native export is
# never retained, so these let the next run name the cause: the rule, the leaf's 1-based ordinal in
# document order (the same tree as the private web input), its section bit and a coarse shape.
# 'allowed-text-concat' / 'allowed-text-concat-date': the value is two or more pieces glued together, each an exact
# allowed text of the case or a digit run (the '-date' variant also holds a dd/MM/yyyy or yyyy-MM-dd piece), e.g. a
# check-key formula such as Y1 01-2!CR49 = TRIM(E49)&TRIM(R49)&TRIM(AG49)&TRIM(AM49)&TRIM(AR49)&TRIM(AW49) written into
# a code leaf. Diagnostic only: the value is still rejected and never retained.
VALUE_SHAPES = frozenset(('empty', 'whitespace-variant', 'case-variant', 'bool-titlecase', 'grouped-number', 'date-like', 'numeric-other',
                          'allowed-text-concat', 'allowed-text-concat-date', 'text-other'))
_PIECE_DATE = re.compile(r'[0-9]{2}/[0-9]{2}/[0-9]{4}|[0-9]{4}-[0-9]{2}-[0-9]{2}')
_PIECE_DIGITS = re.compile(r'[0-9]+')


def _concat_shape(value, allowed):
    """Bounded test: can ``value`` be split into >= 2 pieces, each an exact allowed text (as TRIM leaves it) or
    a digit run / date? Returns the shape name or None; never the pieces."""
    texts = sorted({a.strip() for a in allowed if a and a.strip()}, key=len, reverse=True)
    if len(value) > 2048 or not texts:
        return None
    best = {0: (0, False)}  # position -> (pieces, saw a date piece)
    for i in range(len(value)):
        if i not in best:
            continue
        count, dated = best[i]
        steps = [(i + len(a), False) for a in texts if value.startswith(a, i)]
        for pattern, is_date in ((_PIECE_DATE, True), (_PIECE_DIGITS, False)):
            match = pattern.match(value, i)
            if match:
                steps.append((match.end(), is_date))
        for end, is_date in steps:
            state = (count + 1, dated or is_date)
            if end not in best or state > best[end]:
                best[end] = state
    if len(value) not in best or best[len(value)][0] < 2:
        return None
    return 'allowed-text-concat-date' if best[len(value)][1] else 'allowed-text-concat'


# Value-free layout of a rejected concatenation (diagnostic only; the value is still rejected and never retained):
# the fewest pieces, each a named part of the case's check key (its column letter), another allowed text of the case
# ('a' + index into the sorted allowed texts), a dd/MM/yyyy ('dmy') or yyyy-MM-dd ('iso') piece, or a digit run
# ('n' + length). A date or digit piece equal to an encoding of the case's own synthetic inputs carries that encoding's
# id ('=ddMMyyyy', '=oadate', '=code', ...), never the digits. E.g. 'E.R.AG.AR.n8=ddMMyyyy'.
LAYOUT_ENCODINGS = ('ddMMyyyy', 'yyyyMMdd', 'MMddyyyy', 'ddMMyy', 'oadate', 'code', 'index')
LAYOUT_TOKEN = r'(?:[A-Z]{1,3}|a[0-9]{1,3}|(?:dmy|iso)(?:=AW)?|n[0-9]{1,4}(?:=(?:%s))?)' % '|'.join(LAYOUT_ENCODINGS)
LAYOUT = re.compile(r'%s(?:\.%s){1,31}\Z' % (LAYOUT_TOKEN, LAYOUT_TOKEN))


def _date_encodings(text):
    """Candidate digit/date renderings of one synthetic dd/MM/yyyy input (FarPoint OADate: days since 1899-12-30)."""
    day = datetime.datetime.strptime(text, '%d/%m/%Y').date()
    return {'ddMMyyyy': day.strftime('%d%m%Y'), 'yyyyMMdd': day.strftime('%Y%m%d'), 'MMddyyyy': day.strftime('%m%d%Y'),
            'ddMMyy': day.strftime('%d%m%y'), 'oadate': str((day - datetime.date(1899, 12, 30)).days)}


def concat_layout(value, allowed, parts=None):
    """Bounded, value-free decomposition of ``value`` (see LAYOUT) or None. ``parts`` is the case's check-key input
    (CHECK_KEYS): named texts, the date column and the combobox code."""
    parts = parts or {}
    named = [(column, text.strip()) for column, text in parts.get('texts', ()) if text.strip()]
    texts = sorted({a.strip() for a in allowed if a and a.strip()})
    others = sorted(((t, 'a%d' % i) for i, t in enumerate(texts)), key=lambda x: (-len(x[0]), x[0]))
    digits = {}
    if parts.get('date'):
        digits.update({v: k for k, v in _date_encodings(parts['date']).items()})
    if parts.get('code'):
        digits.setdefault(parts['code'], 'code'); digits.setdefault(str(int(parts['code']) - 1), 'index')
    if len(value) > 2048 or not (named or texts):
        return None
    seen, frontier = {0: ()}, [0]
    while frontier:
        following = []
        for i in frontier:
            tokens = seen[i]
            steps = [(i + len(t), c) for c, t in named if value.startswith(t, i)]
            steps += [(i + len(t), tag) for t, tag in others if value.startswith(t, i)]
            match = _PIECE_DATE.match(value, i)
            if match:
                piece = match.group(0)
                tag = 'dmy' if '/' in piece else 'iso'
                if parts.get('date') and piece == (parts['date'] if tag == 'dmy' else '-'.join(reversed(parts['date'].split('/')))):
                    tag += '=AW'
                steps.append((match.end(), tag))
            match = _PIECE_DIGITS.match(value, i)
            if match:
                run = match.group(0)
                steps.append((match.end(), 'n%d' % len(run) + ('=' + digits[run] if run in digits else '')))
            for end, tag in steps:
                if end not in seen:
                    seen[end] = tokens + (tag,); following.append(end)
        if len(value) in seen:
            break
        frontier = following
    tokens = seen.get(len(value))
    if not tokens or len(tokens) < 2 or len(tokens) > 32:
        return None
    layout = '.'.join(tokens)
    return layout if LAYOUT.match(layout) else None


# Y1 04/NTNN TT89, annex 02-2/NTNN (04_1_NTNN_TT89_309.xml binds ct6_ma to column CR): HTKK writes ct6_ma as the value of
# the LOCKED check-key formula of sheet 01-2 (XLS 04_NTNN_TT89_309.xls sha256 3326d1ab...ca61, CR49), kept on import
# (WinSpreadProcess.fpSpBindDataCell 0x60001a8) and exported from the grid value (WinDoWorkEvent.ExportDataTableToTableNode
# 0x6000050). Each part renders as the original grid holds it (DECLARATION-NATIVE-CASES.md, "Y1, chuỗi CR49"):
# E, R, AR plain text; AG the combobox item text (WinInsertCombox 0x60001be: ComboBoxCellType, EditorValue never set ->
# Item, ComboBoxCellType.Parse returns the text); AM not bound by the control template (blank); AW the value of the
# MaskCellType "00/00/0000" that InsertDateCell 0x60001af creates: Cell.set_Text -> EditBaseCellType.Parse ->
# MaskFormatter.FromFormattedString keeps only the mask's placeholder positions (h.f), so "15/03/2026" -> "15032026".
# TRIM is FarPoint's TrimFunctionInfo (.NET Trim, inner whitespace runs kept as their first character).
CHECK_KEY_FORMULA = 'TRIM(E49)&TRIM(R49)&TRIM(AG49)&TRIM(AM49)&TRIM(AR49)&TRIM(AW49)'
CHECK_KEY_PATH = 'HSoThueDTu/HSoKhaiThue/PLuc/PL02_2_NTNN/BKCacNTPhu/CTietBKCacNTPhu/ct6_ma'
CHECK_KEYS = {
    # The case's own synthetic inputs (htkk_web scripts/generate-htkk-descriptor-reference.mjs, row 01-2): AG is the
    # DM_NNKD_NTNN item 01 the web draft selects; AM is unbound; AW is ngày hợp đồng.
    '04NTNN-TT89-one-subcontractor-2026': {'texts': (('E', 'NHA THAU PHU VIET NAM A - GIẢ LẬP'), ('R', 'NHA THAU NUOC NGOAI B - GIẢ LẬP'),
                                                     ('AG', 'Dịch vụ, cho thuê máy móc thiết bị, bảo hiểm'), ('AM', ''), ('AR', 'HD-GL-041')),
                                           'date': '15/03/2026', 'code': '01', 'dateColumn': 'AW'},
}


def farpoint_trim(text):
    """FarPoint.CalcEngine TrimFunctionInfo.Evaluate (0x60008da): String.Trim, then each run of whitespace keeps
    only its first character."""
    out, keep = [], True
    for ch in text.strip():
        if not ch.isspace():
            out.append(ch); keep = True
        elif keep:
            out.append(ch); keep = False
    return ''.join(out)


def mask_value(text, mask='00/00/0000'):
    """Value of a FarPoint MaskCellType cell whose Text is ``text``: the characters at the mask's placeholder
    positions (MaskFormatter h.f keeps codes >= 6; '0' is a placeholder, '/' a literal), trailing spaces trimmed."""
    if set(mask) - set('0/'):
        raise ValueError('Unreviewed mask')
    return ''.join(ch for ch, m in zip(text, mask) if m == '0').rstrip(' ')


def check_key(case_id):
    """Exact ct6_ma of the case recomputed from its own synthetic inputs (the CR49 formula, column by column)."""
    parts = CHECK_KEYS[case_id]
    columns = re.findall(r'TRIM\(([A-Z]{1,3})49\)', CHECK_KEY_FORMULA)
    if '&'.join('TRIM(%s49)' % c for c in columns) != CHECK_KEY_FORMULA:
        raise ValueError('Unreviewed check-key formula')
    values = dict(parts['texts']); values[parts['dateColumn']] = mask_value(parts['date'])
    if list(values) != columns:
        raise ValueError('Check-key parts drift')
    return ''.join(farpoint_trim(values[c]) for c in columns)


class DeclarationWebCaseError(ValueError):
    def __init__(self, code, context=None):
        if code not in CODES:
            raise ValueError('Invalid bounded declaration diagnostic')
        self.code = code
        self.context = context or {}
        super().__init__(code)


def reject(code, context=None):
    raise DeclarationWebCaseError(code, context)


def value_shape(value, allowed=()):
    if value == '':
        return 'empty'
    folded = ' '.join(value.split())
    if any(' '.join(a.split()) == folded for a in allowed):
        return 'whitespace-variant'
    if any(' '.join(a.split()).casefold() == folded.casefold() for a in allowed):
        return 'case-variant'
    if value in ('True', 'False', 'TRUE', 'FALSE'):
        return 'bool-titlecase'
    if re.fullmatch(r'-?[0-9]{1,3}([.,][0-9]{3})+([.,][0-9]+)?', value):
        return 'grouped-number'
    if re.fullmatch(r'[0-9]{1,4}[-./][0-9]{1,2}([-./][0-9]{1,4})?( .*)?', value):
        return 'date-like'
    if re.fullmatch(r'[-+(]?[0-9.,E+\- )]+', value):
        return 'numeric-other'
    return _concat_shape(value, allowed) or 'text-other'


def _where(items, path, value=None, allowed=(), parts=None):
    """Context for the first leaf at ``path`` (ordinal is 1-based; 0 if absent)."""
    ordinal = next((i + 1 for i, (p, _) in enumerate(items) if p == path), 0)
    section = next((bit for name, bit in SECTIONS.items() if '/' + name + '/' in path + '/'), 32)
    context = {'leafOrdinal': ordinal, 'section': section}
    if value is not None:
        context['valueShape'] = value_shape(value, allowed)
        if context['valueShape'] in ('allowed-text-concat', 'allowed-text-concat-date'):
            layout = concat_layout(value, allowed, parts)
            if layout:
                context['concatLayout'] = layout
    return context


# The exact synthetic profile the Windows harness saves (HtkkGuiReferenceAutomation.cs).
MST = '9999999997'
NAME = 'NNT KIEM THU GIA LAP - KHONG NOP'
ADDRESS = 'DU LIEU GIA LAP KIEM THU KHONG SU DUNG'
SIGNER = 'NGUOI KY GIA LAP'
# Texts the original profile/period dialog may legitimately add on a native re-export.
PROFILE_TEXTS = frozenset((NAME, ADDRESS, SIGNER, 'Thành phố Hà Nội', 'Phường Sơn Tây', 'Thuế Thành phố Hà Nội', 'Thuế cơ sở 16 Thành phố Hà Nội'))
NATIVE_SERVICE = ('HTKK', 'HỖ TRỢ KÊ KHAI THUẾ', '5.8.1')


def native_service(service_version=None):
    """The original's service identity; pbanDVu is the release of the selected oracle (default 5.8.1)."""
    return NATIVE_SERVICE if service_version is None else NATIVE_SERVICE[:2] + (service_version,)
# Every case form is verified against HTKK, so the web exporters (htkk_web lib/export-labelling.ts) write
# no pre-root comment and the neutral tool identity WEB_CODE/WORKBOOK_SERVICE. The earlier draft
# disclaimer (COMMENT) is now rejected like any other comment.
COMMENT = '<!-- BẢN NHÁP; KHÔNG NỘP THUẾ; CHƯA KIỂM CHỨNG VỚI HTKK WINDOWS. -->'
PREAMBLE = '<?xml version="1.0" encoding="UTF-8"?>\n'
SERVICE_PATH = 'HSoThueDTu/HSoKhaiThue/TTinChung/TTinDVu/'
SERVICE_NAMES = ('maDVu', 'tenDVu', 'pbanDVu', 'ttinNhaCCapDVu')
CREATION_PATH = 'HSoThueDTu/HSoKhaiThue/TTinChung/TTinTKhaiThue/TKhaiThue/ngayLapTKhai'
TK = 'HSoThueDTu/HSoKhaiThue/TTinChung/TTinTKhaiThue/TKhaiThue/'
NNT = 'HSoThueDTu/HSoKhaiThue/TTinChung/TTinTKhaiThue/NNT/'
NUMBER = re.compile(r'-?(0|[1-9][0-9]{0,17})(\.[0-9]{1,6})?\Z')
DATE = re.compile(r'([0-9]{2}/[0-9]{2}/[0-9]{4}|[0-9]{4}-[0-9]{2}-[0-9]{2}|[0-9]{1,2}/[0-9]{4}|[0-9]{2}/[0-9]{2})\Z')
CODE = re.compile(r'[0-9]{1,18}\Z')
TEMPLATE_TT80 = '(Ban hành kèm theo Thông tư số 80/2021/TT-BTC ngày 29 tháng 9 năm 2021 của Bộ trưởng Bộ Tài chính)'
TEMPLATE_TT89 = '(Kèm theo Thông tư số 89/2026/TT-BTC ngày 30 tháng 6 năm 2026 của Bộ trưởng Bộ Tài chính)'
WEB_TOOL = 'hotrokekhai.net — Công cụ Kê khai, công cụ độc lập'
WEB_CODE = 'CCKK'
MISMATCH_ORDINALS = 8
SECTIONS = {'TTinDVu': 1, 'TKhaiThue': 2, 'NNT': 4, 'CTieuTKhaiChinh': 8, 'PLuc': 16}


def _case(producer, menu, ma, version, schema, period, dates, sign, created, leaves, annexes, service, texts):
    kieu, ky, tu, den = period
    return {'producerCase': producer, 'menuId': menu, 'maTKhai': ma, 'xmlVersion': version, 'schemaId': schema,
            'kieuKy': kieu, 'kyKKhai': ky, 'tuNgay': tu, 'denNgay': den, 'ngayKy': sign, 'createdDate': created,
            'leafCount': leaves, 'annexElements': tuple(annexes), 'webService': (WEB_CODE, service, '0.9.2', WEB_TOOL),
            'texts': frozenset(texts) | {'C', kieu, version, NAME, SIGNER, WEB_CODE, service, '0.9.2', WEB_TOOL}, 'dates': dates}


WORKBOOK_SERVICE = 'Công cụ Kê khai'
PBT_TEXTS = ['TRU SO CHINH GIA LAP', 'CHI NHANH GIA LAP', 'Thành phố Hà Nội', 'Phường Sơn Tây', 'Thuế cơ sở 16 Thành phố Hà Nội', 'Thành phố Hải Phòng', 'Phường Đồ Sơn', 'Thuế cơ sở 6 Thành phố Hải Phòng']
CASES = {
    '03TNDN-profit20-Y2025': _case('tndn03-profit20-y2025', 'N8', '892', '2.9.4', 'Validate/03_TNDN_TT80_294.xsd', ('Y', '2025', '01/01/2025', '31/12/2025'), None, '2026-03-20', '2026-03-20', 147, ['PLuc_03_1A_TNDN'], WORKBOOK_SERVICE,
                                   # Period default settlement case (AutoBindData_0) and the reviewed industry code (Header B25/B26).
                                   ['TỜ KHAI QUYẾT TOÁN THUẾ THU NHẬP DOANH NGHIỆP (Mẫu số 03/TNDN)', TEMPLATE_TT80, '+ Thu nhập tính thuế áp dụng thuế suất 20%', 'QT định kỳ', 'C10', 'C10 - Sản xuất, chế biến thực phẩm']),
    # 03/TNDN with the C7 rate chosen in the DC_184 combobox (HTKK 5.8.2 oracle, non-gating; same N8 form, template and
    # class as 5.8.1; AutoBindData_0 unlocks C66 from year 2025). The rate name is the DM_DUNG_CHUNG DC_184 item text.
    '03TNDN-rate15-Y2025': _case('tndn03-rate15-y2025', 'N8', '892', '2.9.4', 'Validate/03_TNDN_TT80_294.xsd', ('Y', '2025', '01/01/2025', '31/12/2025'), None, '2026-03-20', '2026-03-20', 147, ['PLuc_03_1A_TNDN'], WORKBOOK_SERVICE,
                                 ['TỜ KHAI QUYẾT TOÁN THUẾ THU NHẬP DOANH NGHIỆP (Mẫu số 03/TNDN)', TEMPLATE_TT80, '+ Thu nhập tính thuế áp dụng thuế suất 15%', 'QT định kỳ', 'C10', 'C10 - Sản xuất, chế biến thực phẩm']),
    '03TNDN-rate17-Y2025': _case('tndn03-rate17-y2025', 'N8', '892', '2.9.4', 'Validate/03_TNDN_TT80_294.xsd', ('Y', '2025', '01/01/2025', '31/12/2025'), None, '2026-03-20', '2026-03-20', 147, ['PLuc_03_1A_TNDN'], WORKBOOK_SERVICE,
                                 ['TỜ KHAI QUYẾT TOÁN THUẾ THU NHẬP DOANH NGHIỆP (Mẫu số 03/TNDN)', TEMPLATE_TT80, '+ Thu nhập tính thuế áp dụng thuế suất 17%', 'QT định kỳ', 'C10', 'C10 - Sản xuất, chế biến thực phẩm']),
    'BCTC133-B01a-basic-Y2025': _case('bctc133-basic-y2025', 'A2', '683', '2.3.2', 'Validate/133_B01A_DNN_BCTC_232.xsd', ('Y', '2025', '01/01/2025', '31/12/2025'), None, '2026-03-20', '2026-03-20', 975, ['PL_KQHDSXKD', 'PL_CDTK'], WORKBOOK_SERVICE,
                                      ['Bộ báo cáo tài chính (B01a - DNN)(TT133/2016/TT-BTC)', '(Ban hành theo Thông tư số 133/2016/TT-BTC ngày 26/8/2016 của Bộ Tài chính)']),
    'BCTC200-LT-basic-Y2025': _case('bctc200-lt-basic-y2025', '78', '402', '2.2.6', 'Validate/200_01_CDKT_226.xsd', ('Y', '2025', '01/01/2025', '31/12/2025'), None, '2026-03-20', '2026-03-20', 570, ['PL_KQHDSXKD', 'PL_LCTTGT'], WORKBOOK_SERVICE,
                                    ['Báo cáo tài chính (TT200/2014/TT-BTC)', '(Ban hành theo Thông tư số 200/2014/TT-BTC Ngày 22/12/2014 của Bộ Tài chính)', 'Người lập giả lập', 'Kế toán giả lập']),
    '05KK-withheld-Q3-2026': _case('tncn05kk-withheld-q3-2026', 'L7', '864', '2.9.3', 'Validate/05_KK_TNCN_TT80_293.xsd', ('Q', '3/2026', '01/07/2026', '30/09/2026'), None, '2026-10-27', '2026-10-27', 56, [], WORKBOOK_SERVICE,
                                    ['TK khấu trừ thuế thu nhập cá nhân Mẫu 05/KK-TNCN (TT80/2021)', TEMPLATE_TT80, ADDRESS]),
    # Z8 05/KK-TNCN TT89 (HTKK 5.8.2 only): KieuKy 14 = SetLayoutToKhaiQuy, StartDate 01/10/2026.
    '05KK-TT89-withheld-Q4-2026': _case('tncn05kk-tt89-withheld-q4-2026', 'Z8', '2036', '3.0.9', 'Validate/05_KK_TNCN_TT89_309.xsd', ('Q', '4/2026', '01/10/2026', '31/12/2026'), None, '2026-10-27', '2026-10-27', 69, [], WORKBOOK_SERVICE,
                                         ['TK khấu trừ thuế thu nhập cá nhân Mẫu 05/KK-TNCN (TT89/2026)', TEMPLATE_TT89, ADDRESS]),
    # 05/KK-TNCN with bảng 05-1/PBT-KK-TNCN (HTKK 5.8.2 oracle, mode web-xml-import-tick-reexport with combo edits): [15]
    # (L7) / [14] (Z8) and two rows of the tiền lương table; texts = the synthetic unit names and the catalogue names
    # (Catalogue_Dia_Ban_Tinh_Moi / _Xa_Moi / Catalogue_CQT_Dia_Ban) of the two wards.
    '05KK-PBT-two-provinces-Q3-2026': _case('tncn05kk-pbt-two-provinces-q3-2026', 'L7', '864', '2.9.3', 'Validate/05_KK_TNCN_TT80_293.xsd', ('Q', '3/2026', '01/07/2026', '30/09/2026'), None, '2026-10-27', '2026-10-27', 110, ['PLuc_05_1_PBT_KK_TNCN'], WORKBOOK_SERVICE,
                                             ['TK khấu trừ thuế thu nhập cá nhân Mẫu 05/KK-TNCN (TT80/2021)', TEMPLATE_TT80, ADDRESS] + PBT_TEXTS),
    '05KK-TT89-PBT-two-provinces-Q4-2026': _case('tncn05kk-tt89-pbt-two-provinces-q4-2026', 'Z8', '2036', '3.0.9', 'Validate/05_KK_TNCN_TT89_309.xsd', ('Q', '4/2026', '01/10/2026', '31/12/2026'), None, '2026-10-27', '2026-10-27', 117, ['PLuc_05_1_PBT_KK_TNCN'], WORKBOOK_SERVICE,
                                                  ['TK khấu trừ thuế thu nhập cá nhân Mẫu 05/KK-TNCN (TT89/2026)', TEMPLATE_TT89, ADDRESS] + PBT_TEXTS),
    # KieuKy 12 (B9/B8): frmHTKKPeriod_Load → SetLayoutToKhaiNamTuThangDenThang hides pnTuNgay/pnDenNgay,
    # so GetPeriodInfo gives TTinChung kyKKhaiTuNgay = kyKKhaiDenNgay = '' and WinDoWorkImportFormXml
    # refuses a file with any other value (0437, releases 224/225). The months come from the driver plan.
    '05QTT-two-employees-Y2025': _case('tncn05qtt-two-employees-y2025', 'B9', '953', '2.9.3', 'Validate/05_QTT_TNCN_TT80_293.xsd', ('Y', '2025', '', ''), None, '2026-10-27', '2026-10-27', 162, ['PLuc_05_1_BK_QTT', 'PLuc_05_3_BK_QTT'], WORKBOOK_SERVICE,
                                       # Two 05-3 rows: FinishImportXML recomputes 05-1 [16]/BF only for more than one
                                       # 05-3 row; with one row Validate_1 E_52 refused 05-1!W24 (release 231, run 42316192917).
                                       ['TỜ KHAI QUYẾT TOÁN THUẾ THU NHẬP CÁ NHÂN (Mẫu số 05/QTT-TNCN)', TEMPLATE_TT80, ADDRESS, 'NGUOI LAO DONG A', 'NGUOI LAO DONG B', 'NGUOI PHU THUOC A', 'NGUOI PHU THUOC B', 'Con', 'Thẻ CCCD/Số định danh cá nhân', 'QT định kỳ']),
    # B8 02/QTT-TNCN (non-gating): the descriptor design case with two dependants (annex 02-1).
    '02QTT-dependants-Y2025': _case('tncn02qtt-dependants-y2025', 'B8', '952', '2.7.3', 'Validate/02_QTT_TNCN_TT80_273.xsd', ('Y', '2025', '', ''), None, '2026-10-27', '2026-10-27', 130, ['PLuc_02_1_BK_QTT_TNCN'], WORKBOOK_SERVICE,
                                    ['TỜ KHAI QUYẾT TOÁN THUẾ THU NHẬP CÁ NHÂN (Mẫu 02/QTT-TNCN)', TEMPLATE_TT80, ADDRESS, 'Quyết toán theo năm dương lịch', 'NGUOI PHU THUOC A', 'NGUOI PHU THUOC B',
                                     'Thẻ CCCD', 'Giấy khai sinh', 'GKS-0001', 'Con',
                                     # [08]/[07] NNT tỉnh/huyện (02!F23/N23, Catalogue_Dia_Ban_Tinh/Huyen 101/10101):
                                     # Header!B53/B54 refused the empty pair with 0016 (release 227, run 42302323087).
                                     'Hà Nội', 'Quận Ba Đình']),
    # I9 01/NTNN TT80 (non-gating): KieuKy 18 month 09/2026 (HTKK 5.8.2 refuses I9 after 09/2026), two synthetic
    # foreign contractors without MST.
    '01NTNN-two-contractors-M09-2026': _case('ntnn01-two-contractors-m09-2026', 'I9', '838', '2.5.1', 'Validate/01_NTNN_TT80_251.xsd', ('M', '09/2026', '01/09/2026', '30/09/2026'), None, '2026-10-27', '2026-10-27', 74, [], WORKBOOK_SERVICE,
                                             ['Tờ khai thuế nhà thầu nước ngoài - MẪU SỐ 01/NTNN', TEMPLATE_TT80, ADDRESS, 'NHA THAU NUOC NGOAI A - GIẢ LẬP', 'NHA THAU NUOC NGOAI B - GIẢ LẬP', 'HD-GL-001', 'HD-GL-002',
                                              # DM_NNKD_NTNN.xml items 01/02 (ct1b name, ct1b_ma code).
                                              'Dịch vụ, cho thuê máy móc thiết bị, bảo hiểm', 'Xây dựng, lắp đặt không bao thầu nguyên vật liệu, máy móc, thiết bị']),
    # Y8 01/NTNN, NCCNN TT89 (non-gating, mode original-entry-export): part II chosen (nopThayNCCNN), one supplier
    # and one non-resident individual (design case 01NTNN-NCCNN-two-parts-M10-2026); the driver types the rows into
    # HTKK instead of importing them (the import-based case was removed: HTKK resets the tables on import).
    '01NTNN-NCCNN-entry-M10-2026': _case('ntnn01-nccnn-entry-m10-2026', 'Y8', '2012', '3.0.9', 'Validate/01_NTNN_NCCNN_TT89_309.xsd', ('M', '10/2026', '01/10/2026', '31/10/2026'), None, '2026-10-27', '2026-10-27', 107, [], WORKBOOK_SERVICE,
                                         ['TỜ KHAI THUẾ NHÀ THẦU NƯỚC NGOÀI; NHÀ CUNG CẤP NƯỚC NGOÀI, CÁ NHÂN KHÔNG CƯ TRÚ CÓ HOẠT ĐỘNG KINH DOANH TRỂN NỀN TẢNG THƯƠNG MẠI ĐIỆN TỬ, NỀN TẢNG SỐ KHÁC - MẪU SỐ 01/NTNN, NCCNN',
                                          TEMPLATE_TT89, ADDRESS, 'NHA CUNG CAP NUOC NGOAI C - GIẢ LẬP', 'CA NHAN KHONG CU TRU D - GIẢ LẬP', 'HD-GL-003', 'HD-GL-004',
                                          'Dịch vụ, cho thuê máy móc thiết bị, bảo hiểm', 'Hoạt động kinh doanh khác']),
    # J1 03/NTNN 3.0.8 (non-gating): KieuKy 18 month 10/2026, two synthetic rows with rate [9] = 0 so that
    # Ntnn03TT80Nckt308.FinishImportXML (BU := getThuSuatByMa(CR, "DC_97") = "") changes nothing.
    '03NTNN-no-rate-M10-2026': _case('ntnn03-no-rate-m10-2026', 'J1', '840', '3.0.8', 'Validate/03_NTNN_TT80_308.xsd', ('M', '10/2026', '01/10/2026', '31/10/2026'), None, '2026-10-27', '2026-10-27', 65, [], WORKBOOK_SERVICE,
                                     ['Tờ khai thuế nhà thầu nước ngoài - MẪU SỐ 03/NTNN', TEMPLATE_TT89, ADDRESS, 'TU VAN KY THUAT A - GIẢ LẬP', 'LAP DAT THIET BI B - GIẢ LẬP', 'NHA THAU PHU A - GIẢ LẬP', 'HD-GL-031', 'HD-GL-032',
                                      'Dịch vụ, cho thuê máy móc thiết bị, bảo hiểm', 'Xây dựng, lắp đặt không bao thầu nguyên vật liệu, máy móc, thiết bị']),
    # D6/Y1 04/NTNN quyết toán (non-gating): KieuKy 22, GetPeriodInfo KieuKy D_D; xmlExportTTinChung writes
    # kieuKy "Y", kyKKhai = year of the to-date and the two dates. One subcontractor row in annex 02-2/NTNN.
    '04NTNN-TT80-one-subcontractor-2026': _case('ntnn04-tt80-one-subcontractor-2026', 'D6', '922', '3.0.8', 'Validate/04_NTNN_TT80_308.xsd', ('Y', '2026', '01/01/2026', '30/09/2026'), None, '2026-10-27', '2026-10-27', 79, ['PL02_2_NTNN'], WORKBOOK_SERVICE,
                                                ['TỜ KHAI QUYẾT TOÁN THUẾ NHÀ THẦU NƯỚC NGOÀI - MẪU SỐ 04/NTNN', TEMPLATE_TT80, ADDRESS, 'HD-GL-050', 'Kết thúc hợp đồng nhà thầu',
                                                 'NHA THAU PHU VIET NAM C - GIẢ LẬP', 'NHA THAU NUOC NGOAI D - GIẢ LẬP',
                                                 # DM_NNKD_NTNN item 02 (ct6_ten) and Catalogue_Dia_Ban_Tinh 101 (ct7_ten, control 5).
                                                 'Xây dựng, lắp đặt không bao thầu nguyên vật liệu, máy móc, thiết bị', 'Hà Nội']),
    '04NTNN-TT89-one-subcontractor-2026': _case('ntnn04-tt89-one-subcontractor-2026', 'Y1', '2015', '3.0.9', 'Validate/04_NTNN_TT89_309.xsd', ('Y', '2026', '01/07/2026', '30/09/2026'), None, '2026-10-27', '2026-10-27', 79, ['PL02_2_NTNN'], WORKBOOK_SERVICE,
                                                ['TỜ KHAI QUYẾT TOÁN THUẾ NHÀ THẦU NƯỚC NGOÀI - MẪU SỐ 04/NTNN', TEMPLATE_TT89, ADDRESS, 'HD-GL-040', 'HD-GL-041', 'Kết thúc hợp đồng nhà thầu',
                                                 'NHA THAU PHU VIET NAM A - GIẢ LẬP', 'NHA THAU NUOC NGOAI B - GIẢ LẬP', 'Dịch vụ, cho thuê máy móc thiết bị, bảo hiểm']),
    # X9 02/NTNN quyết toán TT89 (non-gating): KieuKy 22 like Y1; annexes 02-1 (one foreign contractor, nước cư trú
    # Nhật / JP, control 56) and 02-2 (one Vietnamese subcontractor).
    '02NTNN-TT89-two-annexes-2026': _case('ntnn02-tt89-two-annexes-2026', 'X9', '2013', '3.0.9', 'Validate/02_NTNN_TT89_309.xsd', ('Y', '2026', '01/07/2026', '30/09/2026'), None, '2026-10-27', '2026-10-27', 112, ['PL02_1_NTNN', 'PL02_2_NTNN'], WORKBOOK_SERVICE,
                                          ['TỜ KHAI QUYẾT TOÁN THUẾ NHÀ THẦU NƯỚC NGOÀI (Mẫu số 02/NTNN)', TEMPLATE_TT89, ADDRESS, 'HD-GL-020', 'HD-GL-021', 'HD-GL-022', 'Kết thúc hợp đồng nhà thầu',
                                           'NHA THAU NUOC NGOAI E - GIẢ LẬP', 'NHA THAU PHU VIET NAM F - GIẢ LẬP', 'JP', 'Nhật',
                                           'Dịch vụ, cho thuê máy móc thiết bị, bảo hiểm', 'Xây dựng, lắp đặt không bao thầu nguyên vật liệu, máy móc, thiết bị']),
    # C9 02/NTNN quyết toán TT80 (non-gating): KieuKy 22 like D6 (Menu.xml EndDate 01/10/2026); annexes 02-1 (one foreign
    # contractor: nước cư trú Nhật / JP, control 56; địa điểm Thành phố Hà Nội / 101, control 100) and 02-2 (one Vietnamese
    # subcontractor, địa điểm Thành phố Hải Phòng / 103). 02-1 ct10 is the labour count (5), not an amount.
    '02NTNN-TT80-two-annexes-2026': _case('ntnn02-tt80-two-annexes-2026', 'C9', '921', '2.5.1', 'Validate/02_NTNN_TT80_251.xsd', ('Y', '2026', '01/01/2026', '30/09/2026'), None, '2026-10-27', '2026-10-27', 115, ['PL02_1_NTNN', 'PL02_2_NTNN'], WORKBOOK_SERVICE,
                                          ['TỜ KHAI QUYẾT TOÁN THUẾ NHÀ THẦU NƯỚC NGOÀI (Mẫu số 02/NTNN)', TEMPLATE_TT80, ADDRESS, 'HD-GL-030', 'Kết thúc hợp đồng nhà thầu',
                                           'NHA THAU NUOC NGOAI G - GIẢ LẬP', 'NHA THAU PHU VIET NAM H - GIẢ LẬP', 'JP', 'Nhật', 'Thành phố Hà Nội', 'Thành phố Hải Phòng',
                                           'Dịch vụ, cho thuê máy móc thiết bị, bảo hiểm', 'Xây dựng, lắp đặt không bao thầu nguyên vật liệu, máy móc, thiết bị']),
    # Kỳ lần phát sinh (KieuKy 18, chkTKLanPS; non-gating): GetPeriodInfo (0x60004e2, KieuKy table index 16) gives KieuKy D
    # and TuNgay = DenNgay = kyKKhai = the day 20/10/2026; xmlExportTTinChung (0x6000049) keeps kieuKy D. Same synthetic
    # rows as the monthly cases. I9/J1 by import (AutoBindData_0 writes the day into ct6/ct7 and locks it; the web XML
    # carries that day), Y8 by original entry (AutoBindData_0's AE is reset by LockUnlock; the plan types the day).
    # I9 lần phát sinh on 20/09/2026 (HTKK 5.8.2 refuses an I9 day after 30/09/2026); Y8/J1 keep 20/10/2026.
    '01NTNN-occurrence-D20-09-2026': _case('ntnn01-occurrence-d20-09-2026', 'I9', '838', '2.5.1', 'Validate/01_NTNN_TT80_251.xsd', ('D', '20/09/2026', '20/09/2026', '20/09/2026'), None, '2026-10-27', '2026-10-27', 74, [], WORKBOOK_SERVICE,
                                           ['Tờ khai thuế nhà thầu nước ngoài - MẪU SỐ 01/NTNN', TEMPLATE_TT80, ADDRESS, 'NHA THAU NUOC NGOAI A - GIẢ LẬP', 'NHA THAU NUOC NGOAI B - GIẢ LẬP', 'HD-GL-001', 'HD-GL-002',
                                            'Dịch vụ, cho thuê máy móc thiết bị, bảo hiểm', 'Xây dựng, lắp đặt không bao thầu nguyên vật liệu, máy móc, thiết bị']),
    '01NTNN-NCCNN-occurrence-D20-10-2026': _case('ntnn01-nccnn-occurrence-d20-10-2026', 'Y8', '2012', '3.0.9', 'Validate/01_NTNN_NCCNN_TT89_309.xsd', ('D', '20/10/2026', '20/10/2026', '20/10/2026'), None, '2026-10-27', '2026-10-27', 107, [], WORKBOOK_SERVICE,
                                                 ['TỜ KHAI THUẾ NHÀ THẦU NƯỚC NGOÀI; NHÀ CUNG CẤP NƯỚC NGOÀI, CÁ NHÂN KHÔNG CƯ TRÚ CÓ HOẠT ĐỘNG KINH DOANH TRỂN NỀN TẢNG THƯƠNG MẠI ĐIỆN TỬ, NỀN TẢNG SỐ KHÁC - MẪU SỐ 01/NTNN, NCCNN',
                                                  TEMPLATE_TT89, ADDRESS, 'NHA CUNG CAP NUOC NGOAI C - GIẢ LẬP', 'CA NHAN KHONG CU TRU D - GIẢ LẬP', 'HD-GL-003', 'HD-GL-004',
                                                  'Dịch vụ, cho thuê máy móc thiết bị, bảo hiểm', 'Hoạt động kinh doanh khác']),
    '03NTNN-occurrence-D20-10-2026': _case('ntnn03-occurrence-d20-10-2026', 'J1', '840', '3.0.8', 'Validate/03_NTNN_TT80_308.xsd', ('D', '20/10/2026', '20/10/2026', '20/10/2026'), None, '2026-10-27', '2026-10-27', 65, [], WORKBOOK_SERVICE,
                                           ['Tờ khai thuế nhà thầu nước ngoài - MẪU SỐ 03/NTNN', TEMPLATE_TT89, ADDRESS, 'TU VAN KY THUAT A - GIẢ LẬP', 'LAP DAT THIET BI B - GIẢ LẬP', 'NHA THAU PHU A - GIẢ LẬP', 'HD-GL-031', 'HD-GL-032',
                                            'Dịch vụ, cho thuê máy móc thiết bị, bảo hiểm', 'Xây dựng, lắp đặt không bao thầu nguyên vật liệu, máy móc, thiết bị']),
    '01CNKD-TT50-revenue-two-groups-Q3-2026': _case('cnkd01-revenue-two-groups-q3-2026', 'U5', '1266', '2.9.8', 'Validate/01_CNKD_HKD_TT50_298.xsd', ('Q', '3/2026', '01/07/2026', '30/09/2026'), None, '2026-10-27', '2026-10-27', 261, [], WORKBOOK_SERVICE,
                                                    ['TỜ KHAI THUẾ ĐỐI VỚI HỘ KINH DOANH, CÁ NHÂN KINH DOANH', '(Kèm theo Thông tư số 50/2026/TT-BTC ngày 05/3/2026 của Bộ trưởng Bộ Tài chính)', '(a)', '(b)', 'CUA HANG GIA LAP', 'DIA CHI GIA LAP', ADDRESS,
                                                     'Phân phối, cung cấp hàng hóa', 'Dịch vụ, xây dựng không bao thầu  nguyên vật liệu', 'Phường Sơn Tây', 'Thành phố Hà Nội', 'Thuế cơ sở 16 Thành phố Hà Nội',
                                                     '10129 - Thuế cơ sở 16 Thành phố Hà Nội', '1140759 - Phường Sơn Tây - Thuế cơ sở 16 Thành phố Hà Nội',
                                                     'Thuế giá trị gia tăng hàng sản xuất, kinh doanh trong nước (gồm cả dịch vụ trong lĩnh vực dầu khí)', 'Thuế thu nhập từ hoạt động sản xuất, kinh doanh của cá nhân']),
    # U5 3.1.0 on the HTKK 5.8.2 oracle (non-gating, htkkVersion 5.8.2): Menu.xml 5.8.2 VersionXML 3.1.0, PL 01 of
    # NQ 43/2026/QH16 (sheet 01-4, PLuc_01_GiamTNCN_NQ43) ticked on groups 01 and 04; Decimal oracle in htkk_hkd_web_cases.py.
    '01CNKD-TT50-310-pl01-three-groups-Q3-2026': _case('cnkd01-310-pl01-three-groups-q3-2026', 'U5', '1266', '3.1.0', 'Validate/01_CNKD_HKD_TT50_310.xsd', ('Q', '3/2026', '01/07/2026', '30/09/2026'), None, '2026-10-27', '2026-10-27', 299, ['PLuc_01_GiamTNCN_NQ43'], WORKBOOK_SERVICE,
                                                       ['TỜ KHAI THUẾ ĐỐI VỚI HỘ KINH DOANH, CÁ NHÂN KINH DOANH', '(Kèm theo Thông tư số 50/2026/TT-BTC ngày 05/3/2026 của Bộ trưởng Bộ Tài chính)', '(a)', '(b)', '(d)', 'CUA HANG GIA LAP', 'DIA CHI GIA LAP', ADDRESS,
                                                        'Phân phối, cung cấp hàng hóa', 'Dịch vụ, xây dựng không bao thầu  nguyên vật liệu', 'Sản xuất, vận tải, dịch vụ có gắn với hàng hóa, xây dựng có bao thầu nguyên vật liệu',
                                                        'Hoạt động sản xuất, kinh doanh hàng hóa, cung cấp dịch vụ có địa điểm kinh doanh cố định',
                                                        'Phường Sơn Tây', 'Thành phố Hà Nội', 'Thuế cơ sở 16 Thành phố Hà Nội',
                                                        '10129 - Thuế cơ sở 16 Thành phố Hà Nội', '1140759 - Phường Sơn Tây - Thuế cơ sở 16 Thành phố Hà Nội',
                                                        'Thuế giá trị gia tăng hàng sản xuất, kinh doanh trong nước (gồm cả dịch vụ trong lĩnh vực dầu khí)', 'Thuế thu nhập từ hoạt động sản xuất, kinh doanh của cá nhân']),
    # U5 3.1.0 with PL 03 of NQ 43/2026/QH16 (Mẫu 03, sheet 01-5, PLuc_03_PhaiNop_NQ43; HTKK 5.8.2, non-gating): groups 01
    # and 04, one mục A row on group 04 (thuế bù CF of capNhatToKhai); Decimal oracle in htkk_hkd_web_cases.py.
    '01CNKD-TT50-310-pl03-two-groups-Q3-2026': _case('cnkd01-310-pl03-two-groups-q3-2026', 'U5', '1266', '3.1.0', 'Validate/01_CNKD_HKD_TT50_310.xsd', ('Q', '3/2026', '01/07/2026', '30/09/2026'), None, '2026-10-27', '2026-10-27', 285, ['PLuc_03_PhaiNop_NQ43'], WORKBOOK_SERVICE,
                                                       ['TỜ KHAI THUẾ ĐỐI VỚI HỘ KINH DOANH, CÁ NHÂN KINH DOANH', '(Kèm theo Thông tư số 50/2026/TT-BTC ngày 05/3/2026 của Bộ trưởng Bộ Tài chính)', '(a)', '(d)', 'CUA HANG GIA LAP', 'DIA CHI GIA LAP', ADDRESS,
                                                        'Phân phối, cung cấp hàng hóa', 'Sản xuất, vận tải, dịch vụ có gắn với hàng hóa, xây dựng có bao thầu nguyên vật liệu',
                                                        'Hoạt động sản xuất, kinh doanh hàng hóa, cung cấp dịch vụ có địa điểm kinh doanh cố định',
                                                        'Phường Sơn Tây', 'Thành phố Hà Nội', 'Thuế cơ sở 16 Thành phố Hà Nội',
                                                        '10129 - Thuế cơ sở 16 Thành phố Hà Nội', '1140759 - Phường Sơn Tây - Thuế cơ sở 16 Thành phố Hà Nội',
                                                        'Thuế giá trị gia tăng hàng sản xuất, kinh doanh trong nước (gồm cả dịch vụ trong lĩnh vực dầu khí)', 'Thuế thu nhập từ hoạt động sản xuất, kinh doanh của cá nhân']),
}
_workbook_expected = {c['caseId']: c['expected'] for c in workbook_design.PLAN['cases'] + workbook_design.PLAN_582['cases']}
_descriptor_expected = {c['caseId']: (c['expectedLeaves'], c.get('expectedRows', {})) for c in descriptor_design.DESIGN['cases']}
# Leaves the ORIGINAL export fills with the export day (HtkkDeclarationCasePlans.ExportDatePaths):
# A2 has no control bound to TKhaiThue/ngayKy, so TTinChung.ngayKy keeps DateTime.Now.
EXPORT_DATES = {'BCTC133-B01a-basic-Y2025': (TK + 'ngayKy',)}
for _id, _c in CASES.items():
    _c['caseId'] = _id
    _c['exportDates'] = EXPORT_DATES.get(_id, ())
    _c['family'] = 'cnkd' if _id in hkd_design.CASES else 'descriptor' if _id in _descriptor_expected else 'workbook'
    if _c['family'] == 'workbook' and _id not in _workbook_expected:
        raise ValueError('DECLARATION_CASE_POLICY')


# Cases whose web manifest names the HTKK oracle ('htkkVersion', htkk_web generate-htkk-declaration-reference.mjs writes
# it only for a case whose spec carries it). The value must equal the registry case htkkVersion (fetch validate_manifest).
MANIFEST_HTKK_VERSION_CASES = frozenset({'05KK-TT89-withheld-Q4-2026', '03TNDN-rate15-Y2025', '03TNDN-rate17-Y2025', '05KK-PBT-two-provinces-Q3-2026', '05KK-TT89-PBT-two-provinces-Q4-2026'})


def is_case(case_id):
    return case_id in CASES


def case(case_id):
    if case_id not in CASES:
        reject('CASE')
    return CASES[case_id]


def tax_leaf_count(case_id):
    """Compared leaves excluding the four service-identity leaves (C# webTaxLeafCount)."""
    return case(case_id)['leafCount'] - len(SERVICE_NAMES)


def _local(node):
    if not isinstance(node.tag, str) or not node.tag.startswith('{' + NS + '}'):
        reject('NAMESPACE')
    return node.tag[len(NS) + 2:]


def _parse(body, web):
    if not isinstance(body, (bytes, bytearray)) or not 0 < len(body) <= MAX_XML:
        reject('SIZE')
    try:
        text = bytes(body).decode('utf-8-sig' if not web else 'utf-8')
    except UnicodeError:
        reject('ENCODING')
    if web:
        # Every family exporter emits the XML declaration and then the root; no comment
        # (the old draft disclaimer included) is accepted anywhere.
        if not text.startswith(PREAMBLE + '<HSoThueDTu '):
            reject('DECLARATION')
    if re.search(r'<!|<\?(?!xml\s)', text, re.I) or text.count('<?') > 1:
        reject('DECLARATION')
    data = text.encode('utf-8')
    try:
        for _, (prefix, uri) in ET.iterparse(io.BytesIO(data), events=('start-ns',)):
            if (prefix, uri) not in (('', NS), ('xsi', XSI)):
                reject('NAMESPACE')
        root = ET.fromstring(data)
    except ET.ParseError:
        reject('PARSE')
    if _local(root) != 'HSoThueDTu':
        reject('STRUCTURE')
    return root


def leaf_text(node):
    """Leaf text as the .NET XmlDocument reader sees it (PreserveWhitespace=false): a text that is
    only XML whitespace (space, tab, CR, LF) is insignificant and reads as empty. The original
    export writes an empty non-self-closed leaf as '<x>' CRLF indent '</x>' (release 222: A2/78
    leaf 20, GiaHan/maLyDoGiaHan); HTKK's own import and the harness tree comparison read ''.
    Any other character, including NBSP, is kept and compared/privacy-checked exactly."""
    value = node.text or ''
    return '' if value.strip(' \t\r\n') == '' else value


def leaves(root):
    out = []

    def visit(node, path):
        name = _local(node)
        for key, value in node.attrib.items():
            # Row ids: "id" in most templates, "ID" in 01/NTNN ThueNTNN (01_NTNN_TT80_xml_251.xml / XSD).
            # 01_NTNN_NCCNN_TT89_xml_309.xml carries HSoKhaiThue id="ID1" (no underscore), kept as in the template.
            if not ((key in ('id', 'ID') and re.fullmatch(r'ID_?[1-9][0-9]{0,3}', value)) or (key == '{' + XSI + '}nil' and value == 'true' and len(node) == 0 and not (node.text or ''))):
                reject('ATTRIBUTES')
        current = path + '/' + name if path else name
        children = list(node)
        if (node.text or '').strip() and children:
            reject('STRUCTURE')
        for child in children:
            if (child.tail or '').strip():
                reject('STRUCTURE')
        if not children:
            out.append((current, leaf_text(node)))
        for child in children:
            visit(child, current)
    visit(root, '')
    if len(out) > 4096:
        reject('LEAF_COUNT')
    return out


def _one(items, path):
    found = [value for p, value in items if p == path]
    if len(found) != 1:
        reject('STRUCTURE')
    return found[0]


def _texts(items, allowed, case_id=None):
    # Per-case exact leaf (Y1 ct6_ma only): this one path of this one case accepts exactly the value the oracle
    # recomputes from the case's own synthetic inputs; any other value there is checked like every other leaf.
    exact = {CHECK_KEY_PATH: check_key(case_id)} if case_id in CHECK_KEYS else {}
    for path, value in items:
        if value == '' or NUMBER.match(value) or CODE.match(value) or DATE.match(value) or value in ('true', 'false'):
            continue
        if path in exact and value == exact[path]:
            continue
        if value not in allowed:
            reject('PRIVACY', _where(items, path, value, allowed, CHECK_KEYS.get(case_id)))


def _common(items, spec, created):
    for name, expected in (('maTKhai', spec['maTKhai']), ('pbanTKhaiXML', spec['xmlVersion']), ('loaiTKhai', 'C'), ('soLan', '0')):
        if _one(items, TK + name) != expected:
            reject('IDENTITY', _where(items, TK + name, _one(items, TK + name)))
    for name, key in (('kieuKy', 'kieuKy'), ('kyKKhai', 'kyKKhai'), ('kyKKhaiTuNgay', 'tuNgay'), ('kyKKhaiDenNgay', 'denNgay')):
        if _one(items, TK + 'KyKKhaiThue/' + name) != spec[key]:
            reject('PERIOD', _where(items, TK + 'KyKKhaiThue/' + name, _one(items, TK + 'KyKKhaiThue/' + name)))
    for path, expected in ((NNT + 'mst', MST), (NNT + 'tenNNT', NAME), (TK + 'nguoiKy', SIGNER)):
        if _one(items, path) != expected:
            reject('PRIVACY', _where(items, path, _one(items, path), (expected,)))
    # Every TIN-like leaf carries only the synthetic MST or is empty.
    for path, value in items:
        if re.search(r'(^|/)(mst|mst_cu|mstDLyThue)$', path) and value not in ('', MST):
            reject('PRIVACY', _where(items, path))
    if not created:
        return
    if _one(items, TK + 'ngayKy') != spec['ngayKy']:
        reject('DATE')


def _pluc(root):
    return [_local(child) for p in root.findall('./{%s}HSoKhaiThue/{%s}PLuc' % (NS, NS)) for child in p]


# Independent 01/NTNN oracle (I9): the reviewed synthetic contractor rows of the design case and a
# Decimal recomputation of the source XLS row-55 formulas (never the TypeScript engine):
# ct9 = ROUND(ct7*ct8/100, 0), ct13 = MAX(0, ROUND(ct10*ct11/100, 0) - ct12), ct14 = ct9 + ct13;
# tong_ctN = SUM of the column. ROUND is half away from zero (FarPoint/Excel).
# One entry per table: (row path, totals parent, totals prefix, reviewed rows[, formula '03' for 03/NTNN]). Y8 keeps part I locked
# and empty (one default template row); CNKCT holds TNCN in ThueTNCN/ct10..13.
_MAIN = 'HSoKhaiThue/CTieuTKhaiChinh'
# A zero rate is "0", not "0.00": GeneralFunctions.GetValueExportXML (0x6002617) replaces every Controltype-16
# value equal to 0 by "0" before formatting (release 240 run 42353849411: J1 ct9 "0" in the native re-export).
_EMPTY_ROW = {'ct1b_ma': '', 'ct5': '0', 'ct7': '0', 'ct8': '0', 'ct10': '0', 'ct11': '0', 'ct12': '0'}
NTNN_ROWS = {
    '01NTNN-two-contractors-M09-2026': ((_MAIN + '/BKThueNTNN/ThueNTNN', _MAIN, 'tong_', (
        {'ct1b_ma': '01', 'ct5': '1000000000', 'ct7': '1000000000', 'ct8': '5.00', 'ct10': '1000000000', 'ct11': '5.00', 'ct12': '0'},
        {'ct1b_ma': '02', 'ct5': '500000000', 'ct7': '500000000', 'ct8': '3.00', 'ct10': '500000000', 'ct11': '2.00', 'ct12': '2000000'},
    )),),
    # Y8 (original entry): the reviewed rows of the design case; the driver's fixed entry plan is checked against them.
    '01NTNN-NCCNN-entry-M10-2026': (
        (_MAIN + '/BKThueNTNN/ThueNTNN', _MAIN, 'mucI_tong_', (_EMPTY_ROW,)),
        (_MAIN + '/ThueNCCNN_CNKCT/BKThueNCCNN/ThueNCCNN', _MAIN + '/ThueNCCNN_CNKCT', 'mucI_tong_', (
            {'ct1b_ma': '01', 'ct5': '200000000', 'ct7': '200000000', 'ct8': '5.00', 'ct10': '200000000', 'ct11': '5.00', 'ct12': '0'},)),
        (_MAIN + '/ThueNCCNN_CNKCT/BKThueCNKCT/ThueCNKCT', _MAIN + '/ThueNCCNN_CNKCT', 'mucII_tong_', (
            {'ct1b_ma': '05', 'ct5': '100000000', 'ct7': '100000000', 'ct8': '5.00', 'ct10': '100000000', 'ct11': '2.00', 'ct12': '0'},)),
    ),
    # J1 03/NTNN (formula '03'): ct11 = IF(ct8*ct9/100 - ct10 < 0, 0, ROUND(ct8*ct9/100 - ct10, 0)); totals
    # tongct6/8/10/11. Rate ct9 = 0 (FinishImportXML clears every imported rate), so ct11 = 0.
    '03NTNN-no-rate-M10-2026': ((_MAIN + '/BKThueNTNN/ThueNTNN', _MAIN, 'tong', (
        {'ct1b_ma': '01', 'ct6': '800000000', 'ct8': '800000000', 'ct9': '0', 'ct10': '0'},
        {'ct1b_ma': '02', 'ct6': '300000000', 'ct8': '300000000', 'ct9': '0', 'ct10': '0'},
    ), '03'),),
}
# Lần phát sinh: the same reviewed rows; the payment date of every row is the period day in the XML date form
# (01/NTNN ct6, 03/NTNN ct7 = '2026-10-20': AutoBindData_0 for I9/J1, the entry plan for Y8 ThueNCCNN/ThueCNKCT).
# I9 uses 20/09/2026 (its last valid day period on HTKK 5.8.2 is 30/09/2026).
_OCCURRENCE_DAY = '2026-10-20'
_I9_OCCURRENCE_DAY = '2026-09-20'
NTNN_ROWS['01NTNN-occurrence-D20-09-2026'] = tuple((path, parent, prefix, tuple(dict(row, ct6=_I9_OCCURRENCE_DAY) for row in rows), *rest)
                                                for path, parent, prefix, rows, *rest in NTNN_ROWS['01NTNN-two-contractors-M09-2026'])
NTNN_ROWS['01NTNN-NCCNN-occurrence-D20-10-2026'] = tuple((path, parent, prefix, tuple(row if row is _EMPTY_ROW else dict(row, ct6=_OCCURRENCE_DAY) for row in rows), *rest)
                                                      for path, parent, prefix, rows, *rest in NTNN_ROWS['01NTNN-NCCNN-entry-M10-2026'])
NTNN_ROWS['03NTNN-occurrence-D20-10-2026'] = tuple((path, parent, prefix, tuple(dict(row, ct7=_OCCURRENCE_DAY) for row in rows), *rest)
                                                for path, parent, prefix, rows, *rest in NTNN_ROWS['03NTNN-no-rate-M10-2026'])


def _round(value):
    return value.quantize(decimal.Decimal(1), rounding=decimal.ROUND_HALF_UP)


def _computed03(row):
    # ct7 (03/NTNN) is the payment date, not an amount.
    n = {k: decimal.Decimal(v) for k, v in row.items() if k not in ('ct1b_ma', 'ct7')}
    base = n['ct8'] * n['ct9'] / 100 - n['ct10']
    return {**row, 'ct11': str(decimal.Decimal(0) if base < 0 else _round(base))}


def _computed(row):
    # ct6 (01/NTNN) is the payment date, not an amount.
    n = {k: decimal.Decimal(v) for k, v in row.items() if k not in ('ct1b_ma', 'ct6')}
    ct9 = _round(n['ct7'] * n['ct8'] / 100)
    ct13 = max(decimal.Decimal(0), _round(n['ct10'] * n['ct11'] / 100) - n['ct12'])
    return {**row, 'ct9': str(ct9), 'ct13': str(ct13), 'ct14': str(ct9 + ct13)}


def ntnn_tables(case_id):
    """Per table: row path, totals parent, computed rows and column totals of a 01/NTNN design case."""
    out = []
    for row_path, parent, prefix, rows, *formula in NTNN_ROWS[case_id]:
        j1 = formula == ['03']
        computed = [(_computed03 if j1 else _computed)(row) for row in rows]
        columns = ('ct6', 'ct8', 'ct10', 'ct11') if j1 else ('ct5', 'ct7', 'ct9', 'ct10', 'ct12', 'ct13', 'ct14')
        totals = {prefix + k: str(sum(decimal.Decimal(r[k]) for r in computed)) for k in columns}
        out.append((row_path, parent, computed, totals))
    return out


def ntnn_expected(case_id):
    """Rows and totals of the first table (01/NTNN TT80 has one)."""
    _, _, rows, totals = ntnn_tables(case_id)[0]
    return rows, totals


def _xpath(path):
    return './' + '/'.join('{%s}%s' % (NS, n) for n in path.split('/'))


def _ntnn(case_id, root):
    for row_path, parent_path, rows, totals in ntnn_tables(case_id):
        found = root.findall(_xpath(row_path))
        if len(found) != len(rows):
            reject('VALUE')
        for node, row in zip(found, rows):
            values = {_local(leaf): (leaf.text or '') for leaf in node.iter() if len(leaf) == 0}
            if any(values.get(k) != v for k, v in row.items()):
                reject('VALUE')
        parent = root.find(_xpath(parent_path))
        for name, value in totals.items():
            if parent is None or [(n.text or '') for n in parent.findall('{%s}%s' % (NS, name))] != [value]:
                reject('VALUE')


# Independent 04/NTNN oracle (D6/Y1): the reviewed synthetic inputs of the design cases and a Decimal
# recomputation of the source XLS (sheet 01 rows 32-39; never the TypeScript engine). With annex 02-2/NTNN
# attached, CellChange_1/Refresh_1 make [4] quyết toán of rows 1-2 the annex totals (AB32 = BD32 = SUM ct9,
# AB33 = BD33 = SUM ct10); [5] chênh lệch = [4] - [3]; row 4 = IF(row2 - row3 > 0, row2 - row3, 0) per column;
# row 7 = IF(r5 - r6 < 0, 0, r5 - r6), row 8 = IF(r6 - r5 > 0, r6 - r5, 0) on the quyết toán column.
# Row element names per menu (D6 rows 2/4: DThuChuaGomGTGT/DThuTinhThue, Y1: DThuTinhThue/DThuTinhThueNTNN).
_NTNN04_ROWS = {'D6': ('GiaTriHDong', 'DThuChuaGomGTGT', 'DThuNTPhu', 'DThuTinhThue', 'SoThueTNDNPNop'),
                'Y1': ('GiaTriHDong', 'DThuTinhThue', 'DThuNTPhu', 'DThuTinhThueNTNN', 'SoThueTNDNPNop')}
NTNN04 = {
    # (menu, kê khai [3] of rows 1, 2, 3, 5; quyết toán [4] of rows 3, 5, 6; annex rows (ct9, ct10))
    '04NTNN-TT80-one-subcontractor-2026': ('D6', ('2500000000', '2400000000', '0', '96000000'), ('400000000', '100000000', '96000000'), (('2500000000', '2400000000'),)),
    '04NTNN-TT89-one-subcontractor-2026': ('Y1', ('2000000000', '1800000000', '0', '72000000'), ('300000000', '75000000', '72000000'), (('2000000000', '1800000000'),)),
}


def ntnn04_expected(case_id):
    """Leaves under CTieuTKhaiChinh (Group/leaf -> text) and the annex totals of a 04/NTNN design case."""
    menu, declared, settled, annex = NTNN04[case_id]
    D = decimal.Decimal
    t1, t2, t3, t5 = (D(v) for v in declared)
    a3, a5, a6 = (D(v) for v in settled)
    ct9, ct10 = sum(D(r[0]) for r in annex), sum(D(r[1]) for r in annex)
    a1, a2 = ct9, ct10
    pos = lambda v: v if v > 0 else D(0)
    t4, a4 = pos(t2 - t3), pos(a2 - a3)
    names = _NTNN04_ROWS[menu]
    out = {}
    for name, kk, qt in zip(names, (t1, t2, t3, t4, t5), (a1, a2, a3, a4, a5)):
        out[name + '/keKhai'], out[name + '/quyetToan'], out[name + '/chenhLech'] = str(kk), str(qt), str(qt - kk)
    out['SoThueDaNop/quyetToan'] = str(a6)
    out['SoThueConPNop/quyetToan'] = str(D(0) if a5 - a6 < 0 else a5 - a6)
    out['SoThueNopThua/quyetToan'] = str(pos(a6 - a5))
    return out, {'tong_ct9': str(ct9), 'tong_ct10': str(ct10)}


# X9 02/NTNN TT89 (XLS sheet 01 rows 34-49): AF34/AF35 = BO34/BO35 = 02-1 totals [8]/[9] + 02-2 totals [9]/[10]
# (tinhGiaTriHDCt4_tk / tinhDoanhThuChuaThueCt4_tk); row 37 = IF(r35 - r36 > 0, .., 0) per column; 38 = 39 + 40;
# AO = AF - W (rows 34-40); 41 = 42 + 43; 44-46 = IF(r5 - r6 < 0, 0, r5 - r6); 47-49 = IF(r5 - r6 >= 0, 0, ABS(..)).
_NTNN02_DECLARED = ('GiaTriHDong', 'DThuTinhThue', 'DThuTinhThueNTPhu', 'DThuTinhThueNTNN', 'SoThuePhaiNopNTNN', 'ThueGTGTPhaiNop', 'ThueTNDNPhaiNop')
NTNN02 = {
    # (kê khai W34, W35, W36, W39, W40; quyết toán AF36, AF39, AF40, AF42, AF43; 02-1 rows (ct8, ct9); 02-2 rows (ct9, ct10))
    '02NTNN-TT89-two-annexes-2026': (('3000000000', '2800000000', '1000000000', '90000000', '36000000'), ('1000000000', '90000000', '40000000', '90000000', '36000000'),
                                     (('2000000000', '1800000000'),), (('1000000000', '1000000000'),)),
    # C9 (TT80 2.5.1): 02-1 rows (ct8, ct9, ct10 = số lượng lao động); AF34/AF35 are the XLS formulas =BK34/=BK35 with
    # BK34 = 02-1 BG27 (tổng ct8) + 02-2 BD26 (tổng ct9), BK35 = 02-1 BY27 (tổng ct9) + 02-2 BS26 (tổng ct10).
    '02NTNN-TT80-two-annexes-2026': (('3000000000', '2800000000', '1000000000', '90000000', '36000000'), ('1000000000', '90000000', '40000000', '90000000', '36000000'),
                                     (('2000000000', '1800000000', '5'),), (('1000000000', '1000000000'),)),
}
# The TT80 form (C9) names row 2 DThuChuaGomGTGT (TT89: DThuTinhThue) and its 02-1 rows carry ct10 (số lượng lao động).
_NTNN02_TT80 = frozenset({'02NTNN-TT80-two-annexes-2026'})


def ntnn02_expected(case_id):
    """Leaves under CTieuTKhaiChinh and the annex tables (element, table, row, leaves, rows, totals) of an X9 or C9 case."""
    D = decimal.Decimal
    declared, settled, rows1, rows2 = NTNN02[case_id]
    w34, w35, w36, w39, w40 = (D(v) for v in declared)
    a36, a39, a40, a42, a43 = (D(v) for v in settled)
    t1 = (sum(D(r[0]) for r in rows1), sum(D(r[1]) for r in rows1))
    t2 = (sum(D(r[0]) for r in rows2), sum(D(r[1]) for r in rows2))
    pos = lambda v: v if v > 0 else D(0)
    a34, a35 = t1[0] + t2[0], t1[1] + t2[1]
    kk = (w34, w35, w36, pos(w35 - w36), w39 + w40, w39, w40)
    qt = (a34, a35, a36, pos(a35 - a36), a39 + a40, a39, a40)
    out = {}
    tt80 = case_id in _NTNN02_TT80
    declared_names = tuple('DThuChuaGomGTGT' if tt80 and n == 'DThuTinhThue' else n for n in _NTNN02_DECLARED)
    for name, k, q in zip(declared_names, kk, qt):
        out[name + '/keKhai'], out[name + '/quyetToan'], out[name + '/chenhLech'] = str(k), str(q), str(q - k)
    a41 = a42 + a43
    for name, value in (('SoThueDaNop', a41), ('ThueGTGTDaNop', a42), ('ThueTNDNDaNop', a43),
                        ('SoThueConPhaiNop', D(0) if qt[4] - a41 < 0 else qt[4] - a41), ('ThueGTGTConPNop', D(0) if a39 - a42 < 0 else a39 - a42), ('ThueTNDNConPNop', D(0) if a40 - a43 < 0 else a40 - a43),
                        ('SoThueNopThua', D(0) if qt[4] - a41 >= 0 else abs(qt[4] - a41)), ('ThueGTGTNopThua', D(0) if a39 - a42 >= 0 else abs(a39 - a42)), ('ThueTNDNNopThua', D(0) if a40 - a43 >= 0 else abs(a40 - a43))):
        out[name + '/quyetToan'] = str(value)
    first = (('ct8', 'ct9', 'ct10'), {'tong_ct8': str(t1[0]), 'tong_ct9': str(t1[1]), 'tong_ct10': str(sum(D(r[2]) for r in rows1))}) if tt80 else (('ct8', 'ct9'), {'tong_ct8': str(t1[0]), 'tong_ct9': str(t1[1])})
    annexes = (('PL02_1_NTNN', 'BKCacNTNN', 'CTietBKCacNTNN', first[0], rows1, first[1]),
               ('PL02_2_NTNN', 'BKCacNTPhu', 'CTietBKCacNTPhu', ('ct9', 'ct10'), rows2, {'tong_ct9': str(t2[0]), 'tong_ct10': str(t2[1])}))
    return out, annexes


def ntnn_qt_expected(case_id):
    """04/NTNN or 02/NTNN TT89 settlement: (main leaves, annex tables) of the Decimal oracle."""
    if case_id in NTNN04:
        main, totals = ntnn04_expected(case_id)
        if case_id in CHECK_KEYS:  # Y1: each annex row also carries ct6_ma = the CR49 check key (one reviewed row)
            if len(NTNN04[case_id][3]) != 1:
                raise ValueError('DECLARATION_CASE_POLICY')
            return main, (('PL02_2_NTNN', 'BKCacNTPhu', 'CTietBKCacNTPhu', ('ct6_ma', 'ct9', 'ct10'), tuple((check_key(case_id),) + tuple(r) for r in NTNN04[case_id][3]), totals),)
        return main, (('PL02_2_NTNN', 'BKCacNTPhu', 'CTietBKCacNTPhu', ('ct9', 'ct10'), NTNN04[case_id][3], totals),)
    return ntnn02_expected(case_id)


def _ntnn_qt(case_id, root):
    main, annexes = ntnn_qt_expected(case_id)
    for path, value in main.items():
        if [(n.text or '') for n in root.findall(_xpath(_MAIN + '/' + path))] != [value]:
            reject('VALUE')
    for element, table, row, leaves, rows, totals in annexes:
        annex = root.find(_xpath('HSoKhaiThue/PLuc/' + element))
        found = root.findall(_xpath('HSoKhaiThue/PLuc/%s/%s/%s' % (element, table, row)))
        if annex is None or len(found) != len(rows):
            reject('VALUE')
        for node, values in zip(found, rows):
            for leaf, value in zip(leaves, values):
                if [(n.text or '') for n in node.findall('{%s}%s' % (NS, leaf))] != [value]:
                    reject('VALUE')
        for name, value in totals.items():
            if [(n.text or '') for n in annex.findall('{%s}%s' % (NS, name))] != [value]:
                reject('VALUE')


def _expected(case_id, spec, root, items, raw):
    family = spec['family']
    if family == 'workbook':
        for path, value in _workbook_expected[case_id].items():
            if _one(items, path) != value:
                reject('VALUE')
    elif family == 'descriptor':
        values, rows = _descriptor_expected[case_id]
        main = root.find('./{%s}HSoKhaiThue/{%s}CTieuTKhaiChinh' % (NS, NS))
        if main is None:
            reject('STRUCTURE')
        for name, value in values.items():
            # 'Group/leaf' (04/NTNN rows keKhai/quyetToan/chenhLech) is a direct path under CTieuTKhaiChinh.
            nodes = main.findall(_xpath(name)) if '/' in name else main.iter('{%s}%s' % (NS, name))
            found = [(n.text or '') for n in nodes]
            if found != [value]:
                reject('VALUE')
        for key, count in rows.items():
            if len(root.findall(_xpath('HSoKhaiThue/PLuc/' + key))) != count:
                reject('VALUE')
        if case_id in NTNN_ROWS:
            _ntnn(case_id, root)
        if case_id in NTNN04 or case_id in NTNN02:
            _ntnn_qt(case_id, root)
    else:
        try:
            hkd_design.validate_case_xml(case_id, raw)
        except hkd_design.HkdWebCaseError:
            reject('VALUE')


def validate_web_input(body, case_id, manifest=None):
    """Fail closed unless the web XML is exactly this reviewed synthetic case."""
    spec = case(case_id)
    root = _parse(body, True)
    items = leaves(root)
    if len(items) != spec['leafCount']:
        reject('LEAF_COUNT')
    if tuple(_one(items, SERVICE_PATH + name) for name in SERVICE_NAMES) != spec['webService']:
        reject('SERVICE')
    _common(items, spec, True)
    if _one(items, CREATION_PATH) != spec['createdDate']:
        reject('DATE')
    if tuple(_pluc(root)) != spec['annexElements']:
        reject('STRUCTURE')
    # The web draft now carries the synthetic profile leaves original export copies (release 213).
    _texts(items, spec['texts'] | PROFILE_TEXTS, spec['caseId'])
    raw = bytes(body)
    _expected(case_id, spec, root, items, raw)
    if manifest is not None and manifest.get('leafCount') != spec['leafCount']:
        reject('MANIFEST')
    return {'privacyValuesVerified': True, 'leafCount': len(items), 'serviceIdentity': 'web-tool', 'nativeProvenance': False}


def validate_native_output(body, case_id, today=None, service_version=None):
    """Native re-export: original service identity, fresh creation date, synthetic data only."""
    spec = case(case_id)
    root = _parse(body, False)
    items = leaves(root)
    service = tuple(_one(items, SERVICE_PATH + name) for name in SERVICE_NAMES)
    if service[:3] != native_service(service_version) or not re.fullmatch(r'[0-9A-F]{32}', service[3]):
        reject('SERVICE')
    _common(items, spec, False)
    created = _one(items, CREATION_PATH)
    try:
        created_date = datetime.date.fromisoformat(created) if re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', created) else None
    except ValueError:
        created_date = None
    today = today or datetime.datetime.now(datetime.timezone.utc).date()
    if created_date is None or abs((today - created_date).days) > 1:
        reject('DATE')
    _texts(items, spec['texts'] | PROFILE_TEXTS | set(service), spec['caseId'])
    return {'privacyValuesVerified': True, 'leafCount': len(items), 'nativeServiceIdentityVerified': True, 'creationDateRule': 'native-export-current-date'}


def compare_tree(input_body, native_body, export_dates=()):
    """Whole-tree comparison. Normalized in memory only: creation date and 4 service leaves.
    Each ``export_dates`` leaf must equal its own document's creation date (never ignored).

    Returns a bounded diagnostic: matched flag, compared leaf count and a section mask
    (1 TTinDVu, 2 TKhaiThue, 4 NNT, 8 CTieuTKhaiChinh, 16 PLuc, 32 structure), plus the 1-based
    document-order ordinals (the privacy diagnostic's numbering) of the first mismatching leaves."""
    left, right = _parse(input_body, True), _parse(native_body, False)
    state = {'leaves': 0, 'mask': 0, 'ordinal': 0, 'ordinals': []}
    if len(export_dates) > 4:
        reject('CASE')
    created = [dict(leaves(root)).get(CREATION_PATH) for root in (left, right)]

    def section(path):
        for name, bit in SECTIONS.items():
            if '/' + name + '/' in path + '/':
                return bit
        return 32

    def leaf_bits(a, b, path):
        """Mismatch bits of one leaf (0 when it matches)."""
        if path.startswith(SERVICE_PATH):
            return 0 if path[len(SERVICE_PATH):] in SERVICE_NAMES else 32
        state['leaves'] += 1
        if path in export_dates:
            return 0 if None not in created and leaf_text(a) == created[0] and leaf_text(b) == created[1] else section(path)
        return section(path) if path != CREATION_PATH and leaf_text(a) != leaf_text(b) else 0

    def walk(a, b, path):
        if _local(a) != _local(b) or a.attrib != b.attrib or len(a) != len(b):
            state['mask'] |= 32 | section(path)
            return
        if len(a) == 0:
            state['ordinal'] += 1
            bits = leaf_bits(a, b, path)
            state['mask'] |= bits
            if bits and len(state['ordinals']) < MISMATCH_ORDINALS:
                state['ordinals'].append(state['ordinal'])
            return
        for x, y in zip(a, b):
            walk(x, y, path + '/' + _local(x))
    walk(left, right, 'HSoThueDTu')
    return {'allTaxValuesMatched': state['mask'] == 0, 'checkedTaxLeafCount': state['leaves'], 'mismatchSectionMask': state['mask'], 'mismatchLeafOrdinals': state['ordinals'],
            'normalizedInMemory': ['ngayLapTKhai', *SERVICE_NAMES], 'rawBytesPreserved': True}
