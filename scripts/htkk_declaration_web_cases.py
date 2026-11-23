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
# The 5.8.3 Y1 case (đến ngày 07/10/2026) has the same annex row.
CHECK_KEYS['04NTNN-TT89-one-subcontractor-to-07-10-2026'] = CHECK_KEYS['04NTNN-TT89-one-subcontractor-2026']
CHECK_KEYS['04NTNN-TT89-one-subcontractor-from-01-06-2026'] = CHECK_KEYS['04NTNN-TT89-one-subcontractor-2026']


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
GTGT04_NAME = 'TỜ KHAI THUẾ GIÁ TRỊ GIA TĂNG (Mẫu số 04/GTGT)'
GTGT04_TT89_SCHEMA = 'Validate/04_GTGT_TT89_309_htkk582.xsd'
# 01/GTGT TT89 (Z5, HTKK 5.8.4 only): the web publishes the 5.8.4 schema under its own file name (no 5.8.1/5.8.2 copy).
GTGT01_TT89_SCHEMA = 'Validate/01_GTGT_TT89_309.xsd'
GTGT01_NAME = 'TỜ KHAI THUẾ GIÁ TRỊ GIA TĂNG (Mẫu số 01/GTGT)'
GTGT01_ACTIVITY = 'Hoạt động sản xuất kinh doanh thông thường'
# Web schema ids that publish an HTKK file under another name (the compiled plans pin the HTKK file itself).
SCHEMA_SOURCES = {GTGT04_TT89_SCHEMA: 'Validate/04_GTGT_TT89_309.xsd'}
TEMPLATE_TT40 = '(Ban hành kèm theo Thông tư số 40/2021/TT-BTC ngày 01/6/2021 của Bộ trưởng Bộ Tài Chính)'
# 01/TTS mã hợp đồng (TinhMaHopDong): maCQT_MST(000)_ddMMyyyy(từ ngày)_NN of the synthetic profile.
TTS_CODE = '10129_9999999997000_'
# 01/TTS row and hidden-header texts that every G7 case carries.
# The control XML spells three of the hidden header defaults with combining marks (not NFC); kept exactly.
# 01/TTS [18] (E190, text control MaxLength 50, exported as Cell.Text): address - ward - province kept within 50
# characters (runs 43678758282, 43686726527: the full 74-character text differed from the original re-export).
TTS_ORGANIZATION_ADDRESS = (ADDRESS + ' - Phường Sơn Tây - Thành phố Hà Nội')[:50]
TTS_TEXTS = ('Hợp đồng', 'Kỳ thanh toán', 'Kỳ thanh toán cuối cùng', 'Hợp đồng khai lần đầu', 'Phường Sơn Tây', 'H\xf4\u0323 chi\xea\u0301u', 'Gi\xe2\u0301y th\xf4ng ha\u0300nh', 'CMT biên giới', 'Gi\xe2\u0301y t\u01a1\u0300 kh\xe1c')
TCKT_NAME = 'TỜ KHAI THUẾ CỦA TỔ CHỨC KHAI THAY'
TCKT_310_SCHEMA = 'Validate/01_TCKT_TT89_310.xsd'
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
# PL 01-6/GTGT of Z5: the rows of the three cases (synthetic units and branch MSTs; catalogue names of lib/htkk-catalogue.ts).
PL016_HP = ('10309019', 'Phường Đồ Sơn', '103', 'Thành phố Hải Phòng', '10309', 'Thuế cơ sở 6 Thành phố Hải Phòng')
PL016_HP_CUC = ('10309019', 'Phường Đồ Sơn', '103', 'Thành phố Hải Phòng', '10300', 'Thuế Thành phố Hải Phòng')
PL016_TN = ('21501001', 'Phường Phan Đình Phùng', '215', 'Tỉnh Thái Nguyên', '21501', 'Thuế cơ sở 1 tỉnh Thái Nguyên')
PL016_TEXTS = ['CO SO GIA LAP %d - KHONG NOP' % n for n in (1, 2, 3)] + ['9999999997-00%d' % n for n in (1, 2, 3)] + sorted({x for place in (PL016_HP, PL016_HP_CUC, PL016_TN) for x in place[1::2]})
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
    # B8 02/QTT-TNCN năm 2025 with hoàn trả qua chuyển khoản (HTKK 5.8.2 oracle, non-gating): the dependants case's texts, the
    # account holder (tên chủ tài khoản = RemoveDiacritics(tenNNT).ToUpper() = the synthetic NAME) and the DM_Tinh_NganHang name
    # of bank 01204003 (MaTinh 101); the fictitious account number is a digit run.
    '02QTT-refund-transfer-Y2025': _case('tncn02qtt-refund-transfer-y2025', 'B8', '952', '2.7.3', 'Validate/02_QTT_TNCN_TT80_273.xsd', ('Y', '2025', '', ''), None, '2026-10-27', '2026-10-27', 130, ['PLuc_02_1_BK_QTT_TNCN'], WORKBOOK_SERVICE,
                                         ['TỜ KHAI QUYẾT TOÁN THUẾ THU NHẬP CÁ NHÂN (Mẫu 02/QTT-TNCN)', TEMPLATE_TT80, ADDRESS, 'Quyết toán theo năm dương lịch', 'NGUOI PHU THUOC A', 'NGUOI PHU THUOC B',
                                          'Thẻ CCCD', 'Giấy khai sinh', 'GKS-0001', 'Con', 'Hà Nội', 'Quận Ba Đình',
                                          'Ngân hàng Nông nghiệp và Phát triển Nông thôn Việt Nam - Chi nhánh Hà Nội']),
    # B8 năm 2026 (HTKK 5.8.2 oracle, non-gating): the two cases above with every month in 2026. The period dialog opens on
    # Now.Year - 1, so the driver types 2026 and selects on the annex list that typing leaves visible. Ngày lập 01/12/2026: the
    # web, like HTKK (CheckTuThangDenThang 0471), refuses đến tháng 12/2026 before that day; the registry defers them (notBefore).
    '02QTT-dependants-Y2026': _case('tncn02qtt-dependants-y2026', 'B8', '952', '2.7.3', 'Validate/02_QTT_TNCN_TT80_273.xsd', ('Y', '2026', '', ''), None, '2026-10-27', '2026-12-01', 130, ['PLuc_02_1_BK_QTT_TNCN'], WORKBOOK_SERVICE,
                                    ['TỜ KHAI QUYẾT TOÁN THUẾ THU NHẬP CÁ NHÂN (Mẫu 02/QTT-TNCN)', TEMPLATE_TT80, ADDRESS, 'Quyết toán theo năm dương lịch', 'NGUOI PHU THUOC A', 'NGUOI PHU THUOC B',
                                     'Thẻ CCCD', 'Giấy khai sinh', 'GKS-0001', 'Con',
                                     # [08]/[07] NNT tỉnh/huyện (02!F23/N23, Catalogue_Dia_Ban_Tinh/Huyen 101/10101):
                                     # Header!B53/B54 refused the empty pair with 0016 (release 227, run 42302323087).
                                     'Hà Nội', 'Quận Ba Đình']),
    '02QTT-refund-transfer-Y2026': _case('tncn02qtt-refund-transfer-y2026', 'B8', '952', '2.7.3', 'Validate/02_QTT_TNCN_TT80_273.xsd', ('Y', '2026', '', ''), None, '2026-10-27', '2026-12-01', 130, ['PLuc_02_1_BK_QTT_TNCN'], WORKBOOK_SERVICE,
                                         ['TỜ KHAI QUYẾT TOÁN THUẾ THU NHẬP CÁ NHÂN (Mẫu 02/QTT-TNCN)', TEMPLATE_TT80, ADDRESS, 'Quyết toán theo năm dương lịch', 'NGUOI PHU THUOC A', 'NGUOI PHU THUOC B',
                                          'Thẻ CCCD', 'Giấy khai sinh', 'GKS-0001', 'Con', 'Hà Nội', 'Quận Ba Đình',
                                          'Ngân hàng Nông nghiệp và Phát triển Nông thôn Việt Nam - Chi nhánh Hà Nội']),
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
    '04NTNN-TT80-one-subcontractor-to-06-10-2026': _case('ntnn04-tt80-one-subcontractor-to-06-10-2026', 'D6', '922', '3.0.8', 'Validate/04_NTNN_TT80_308.xsd', ('Y', '2026', '01/01/2026', '06/10/2026'), None, '2026-10-27', '2026-10-27', 79, ['PL02_2_NTNN'], WORKBOOK_SERVICE,
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
    # HTKK 5.8.3 observation cases (registry htkkVersion 5.8.3, non-gating): X9/Y1 with đến ngày 07/10/2026, the first day 5.8.3
    # accepts for a TT89 quyết toán (frmHTKKPeriod.CheckHLToKhaiTT80 0718); same contracts and texts as the 30/09/2026 cases.
    '04NTNN-TT89-one-subcontractor-to-07-10-2026': _case('ntnn04-tt89-one-subcontractor-to-07-10-2026', 'Y1', '2015', '3.0.9', 'Validate/04_NTNN_TT89_309.xsd', ('Y', '2026', '01/07/2026', '07/10/2026'), None, '2026-10-27', '2026-10-27', 79, ['PL02_2_NTNN'], WORKBOOK_SERVICE,
                                                ['TỜ KHAI QUYẾT TOÁN THUẾ NHÀ THẦU NƯỚC NGOÀI - MẪU SỐ 04/NTNN', TEMPLATE_TT89, ADDRESS, 'HD-GL-040', 'HD-GL-041', 'Kết thúc hợp đồng nhà thầu',
                                                 'NHA THAU PHU VIET NAM A - GIẢ LẬP', 'NHA THAU NUOC NGOAI B - GIẢ LẬP', 'Dịch vụ, cho thuê máy móc thiết bị, bảo hiểm']),
    '04NTNN-TT89-one-subcontractor-from-01-06-2026': _case('ntnn04-tt89-one-subcontractor-from-01-06-2026', 'Y1', '2015', '3.0.9', 'Validate/04_NTNN_TT89_309.xsd', ('Y', '2026', '01/06/2026', '07/10/2026'), None, '2026-10-27', '2026-10-27', 79, ['PL02_2_NTNN'], WORKBOOK_SERVICE,
                                                ['TỜ KHAI QUYẾT TOÁN THUẾ NHÀ THẦU NƯỚC NGOÀI - MẪU SỐ 04/NTNN', TEMPLATE_TT89, ADDRESS, 'HD-GL-040', 'HD-GL-041', 'Kết thúc hợp đồng nhà thầu',
                                                 'NHA THAU PHU VIET NAM A - GIẢ LẬP', 'NHA THAU NUOC NGOAI B - GIẢ LẬP', 'Dịch vụ, cho thuê máy móc thiết bị, bảo hiểm']),
    '02NTNN-TT89-two-annexes-to-07-10-2026': _case('ntnn02-tt89-two-annexes-to-07-10-2026', 'X9', '2013', '3.0.9', 'Validate/02_NTNN_TT89_309.xsd', ('Y', '2026', '01/07/2026', '07/10/2026'), None, '2026-10-27', '2026-10-27', 112, ['PL02_1_NTNN', 'PL02_2_NTNN'], WORKBOOK_SERVICE,
                                          ['TỜ KHAI QUYẾT TOÁN THUẾ NHÀ THẦU NƯỚC NGOÀI (Mẫu số 02/NTNN)', TEMPLATE_TT89, ADDRESS, 'HD-GL-020', 'HD-GL-021', 'HD-GL-022', 'Kết thúc hợp đồng nhà thầu',
                                           'NHA THAU NUOC NGOAI E - GIẢ LẬP', 'NHA THAU PHU VIET NAM F - GIẢ LẬP', 'JP', 'Nhật',
                                           'Dịch vụ, cho thuê máy móc thiết bị, bảo hiểm', 'Xây dựng, lắp đặt không bao thầu nguyên vật liệu, máy móc, thiết bị']),
    # HTKK 5.8.3 Y8 (original entry, htkkVersion 5.8.3): part II chosen with only II-I (ThueNCCNN) or only II-II (ThueCNKCT);
    # Ntnn01TT89Nckt309.checkTKChinh skips the empty table when the other has data (5.8.2 required both). Texts of that part only.
    '02NTNN-TT89-two-annexes-from-01-06-2026': _case('ntnn02-tt89-two-annexes-from-01-06-2026', 'X9', '2013', '3.0.9', 'Validate/02_NTNN_TT89_309.xsd', ('Y', '2026', '01/06/2026', '07/10/2026'), None, '2026-10-27', '2026-10-27', 112, ['PL02_1_NTNN', 'PL02_2_NTNN'], WORKBOOK_SERVICE,
                                          ['TỜ KHAI QUYẾT TOÁN THUẾ NHÀ THẦU NƯỚC NGOÀI (Mẫu số 02/NTNN)', TEMPLATE_TT89, ADDRESS, 'HD-GL-020', 'HD-GL-021', 'HD-GL-022', 'Kết thúc hợp đồng nhà thầu',
                                           'NHA THAU NUOC NGOAI E - GIẢ LẬP', 'NHA THAU PHU VIET NAM F - GIẢ LẬP', 'JP', 'Nhật',
                                           'Dịch vụ, cho thuê máy móc thiết bị, bảo hiểm', 'Xây dựng, lắp đặt không bao thầu nguyên vật liệu, máy móc, thiết bị']),
    '01NTNN-NCCNN-entry-part-II1-M10-2026': _case('ntnn01-nccnn-entry-part-ii1-m10-2026', 'Y8', '2012', '3.0.9', 'Validate/01_NTNN_NCCNN_TT89_309.xsd', ('M', '10/2026', '01/10/2026', '31/10/2026'), None, '2026-10-27', '2026-10-27', 107, [], WORKBOOK_SERVICE,
                                         ['TỜ KHAI THUẾ NHÀ THẦU NƯỚC NGOÀI; NHÀ CUNG CẤP NƯỚC NGOÀI, CÁ NHÂN KHÔNG CƯ TRÚ CÓ HOẠT ĐỘNG KINH DOANH TRỂN NỀN TẢNG THƯƠNG MẠI ĐIỆN TỬ, NỀN TẢNG SỐ KHÁC - MẪU SỐ 01/NTNN, NCCNN',
                                          TEMPLATE_TT89, ADDRESS, 'NHA CUNG CAP NUOC NGOAI C - GIẢ LẬP', 'HD-GL-003', 'Dịch vụ, cho thuê máy móc thiết bị, bảo hiểm']),
    '01NTNN-NCCNN-entry-part-II2-M10-2026': _case('ntnn01-nccnn-entry-part-ii2-m10-2026', 'Y8', '2012', '3.0.9', 'Validate/01_NTNN_NCCNN_TT89_309.xsd', ('M', '10/2026', '01/10/2026', '31/10/2026'), None, '2026-10-27', '2026-10-27', 107, [], WORKBOOK_SERVICE,
                                         ['TỜ KHAI THUẾ NHÀ THẦU NƯỚC NGOÀI; NHÀ CUNG CẤP NƯỚC NGOÀI, CÁ NHÂN KHÔNG CƯ TRÚ CÓ HOẠT ĐỘNG KINH DOANH TRỂN NỀN TẢNG THƯƠNG MẠI ĐIỆN TỬ, NỀN TẢNG SỐ KHÁC - MẪU SỐ 01/NTNN, NCCNN',
                                          TEMPLATE_TT89, ADDRESS, 'CA NHAN KHONG CU TRU D - GIẢ LẬP', 'HD-GL-004', 'Hoạt động kinh doanh khác']),
    # HTKK 5.8.5 Y8 (original entry, htkkVersion 5.8.5): the entry case with both contracts dated 31/12/2027, after any run day.
    # Ntnn01TT89Nckt309.checkTKChinh 5.8.5 no longer tests a given (4) ngày hợp đồng (5.8.4: E_33 format, E_36 not before today); own contract numbers HD-GL-007 / HD-GL-008.
    '01NTNN-NCCNN-entry-future-contract-M10-2026': _case('ntnn01-nccnn-entry-future-contract-m10-2026', 'Y8', '2012', '3.0.9', 'Validate/01_NTNN_NCCNN_TT89_309.xsd', ('M', '10/2026', '01/10/2026', '31/10/2026'), None, '2026-10-27', '2026-10-27', 107, [], WORKBOOK_SERVICE,
                                         ['TỜ KHAI THUẾ NHÀ THẦU NƯỚC NGOÀI; NHÀ CUNG CẤP NƯỚC NGOÀI, CÁ NHÂN KHÔNG CƯ TRÚ CÓ HOẠT ĐỘNG KINH DOANH TRỂN NỀN TẢNG THƯƠNG MẠI ĐIỆN TỬ, NỀN TẢNG SỐ KHÁC - MẪU SỐ 01/NTNN, NCCNN',
                                          TEMPLATE_TT89, ADDRESS, 'NHA CUNG CAP NUOC NGOAI C - GIẢ LẬP', 'CA NHAN KHONG CU TRU D - GIẢ LẬP', 'HD-GL-007', 'HD-GL-008',
                                          'Dịch vụ, cho thuê máy móc thiết bị, bảo hiểm', 'Hoạt động kinh doanh khác']),
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
    '02NTNN-TT80-two-annexes-to-06-10-2026': _case('ntnn02-tt80-two-annexes-to-06-10-2026', 'C9', '921', '2.5.1', 'Validate/02_NTNN_TT80_251.xsd', ('Y', '2026', '01/01/2026', '06/10/2026'), None, '2026-10-27', '2026-10-27', 115, ['PL02_1_NTNN', 'PL02_2_NTNN'], WORKBOOK_SERVICE,
                                          ['TỜ KHAI QUYẾT TOÁN THUẾ NHÀ THẦU NƯỚC NGOÀI (Mẫu số 02/NTNN)', TEMPLATE_TT80, ADDRESS, 'HD-GL-030', 'Kết thúc hợp đồng nhà thầu',
                                           'NHA THAU NUOC NGOAI G - GIẢ LẬP', 'NHA THAU PHU VIET NAM H - GIẢ LẬP', 'JP', 'Nhật', 'Thành phố Hà Nội', 'Thành phố Hải Phòng',
                                           'Dịch vụ, cho thuê máy móc thiết bị, bảo hiểm', 'Xây dựng, lắp đặt không bao thầu nguyên vật liệu, máy móc, thiết bị']),
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
    # G7 01/TTS TT40 2.8.3 (non-gating, HTKK 5.8.2 oracle): KieuKy 42; cá nhân trực tiếp khai năm 2025 with 01-1/BK-TTS,
    # tổ chức khai thay quý 3/2026 and tháng 10/2026 with 01-2/BK-TTS. Catalogue names: Catalogue_HopDongVaKy,
    # Catalogue_DM_Muc_dich_SD, Catalogue_DM_trang_thai_HD; the hidden header controls export their control Value.
    '01TTS-individual-one-contract-Y2025': _case('tts01-individual-one-contract-y2025', 'G7', '470', '2.8.3', 'Validate/01_TTS_TT40_283.xsd', ('Y', '2025', '01/01/2025', '31/12/2025'), None, '2026-10-27', '2026-10-27', 210, ['PLuc_01_BK_TTS'], WORKBOOK_SERVICE,
                                                 ['TỜ KHAI THUẾ ĐỐI VỚI HOẠT ĐỘNG CHO THUÊ TÀI SẢN (01/TTS)', TEMPLATE_TT40, ADDRESS, *TTS_TEXTS, 'BEN THUE TAI SAN A - GIẢ LẬP', 'HD-TTS-GL-01', TTS_CODE + '01012025_01', 'SO 1 DUONG GIA LAP', 'Văn phòng']),
    '01TTS-individual-two-contracts-Y2025': _case('tts01-individual-two-contracts-y2025', 'G7', '470', '2.8.3', 'Validate/01_TTS_TT40_283.xsd', ('Y', '2025', '01/01/2025', '31/12/2025'), None, '2026-10-27', '2026-10-27', 274, ['PLuc_01_BK_TTS'], WORKBOOK_SERVICE,
                                                  ['TỜ KHAI THUẾ ĐỐI VỚI HOẠT ĐỘNG CHO THUÊ TÀI SẢN (01/TTS)', TEMPLATE_TT40, ADDRESS, *TTS_TEXTS, 'BEN THUE TAI SAN B - GIẢ LẬP', 'BEN THUE TAI SAN C - GIẢ LẬP', 'HD-TTS-GL-02', 'HD-TTS-GL-03', TTS_CODE + '01012025_01', TTS_CODE + '01072025_02', 'SO 2 DUONG GIA LAP', 'Cửa hàng', 'Trả tiền 1 lần cho cả hợp đồng']),
    # Tổ chức khai thay: [16]–[21] are the profile (LockUnlockTheoLoaiNopThue: name, MST, "địa chỉ - huyện - tỉnh").
    '01TTS-organization-two-individuals-Q3-2026': _case('tts01-organization-two-individuals-q3-2026', 'G7', '470', '2.8.3', 'Validate/01_TTS_TT40_283.xsd', ('Q', '3/2026', '01/07/2026', '30/09/2026'), None, '2026-10-27', '2026-10-27', 386, ['PLuc_02_BK_TTS'], WORKBOOK_SERVICE,
                                                        ['TỜ KHAI THUẾ ĐỐI VỚI HOẠT ĐỘNG CHO THUÊ TÀI SẢN (01/TTS)', TEMPLATE_TT40, ADDRESS, *TTS_TEXTS, TTS_ORGANIZATION_ADDRESS, 'CA NHAN CHO THUE A - GIẢ LẬP', 'CA NHAN CHO THUE B - GIẢ LẬP', 'BEN THUE TAI SAN D - GIẢ LẬP', 'BEN THUE TAI SAN E - GIẢ LẬP', 'HD-TTS-GL-04', 'HD-TTS-GL-05', TTS_CODE + '01012026_01', TTS_CODE + '01072026_02', 'SO 4 DUONG GIA LAP', 'Văn phòng']),
    '01TTS-organization-monthly-M10-2026': _case('tts01-organization-monthly-m10-2026', 'G7', '470', '2.8.3', 'Validate/01_TTS_TT40_283.xsd', ('M', '10/2026', '01/10/2026', '31/10/2026'), None, '2026-10-27', '2026-10-27', 216, ['PLuc_02_BK_TTS'], WORKBOOK_SERVICE,
                                                 ['TỜ KHAI THUẾ ĐỐI VỚI HOẠT ĐỘNG CHO THUÊ TÀI SẢN (01/TTS)', TEMPLATE_TT40, ADDRESS, *TTS_TEXTS, TTS_ORGANIZATION_ADDRESS, 'CA NHAN CHO THUE A - GIẢ LẬP', 'BEN THUE TAI SAN F - GIẢ LẬP', 'HD-TTS-GL-06', TTS_CODE + '01102026_01', 'SO 6 DUONG GIA LAP', 'Để ở']),
    # D4 04/GTGT TT80 2.7.4 (non-gating, HTKK 5.8.2 oracle): KieuKy 21, tháng/quý đến 09/2026 (CheckToKhaiHetHieuLuc).
    # Texts: the form name, TT80 description and, for PL 01-3 (PL_NQ142_GTGT), the synthetic goods names.
    '04GTGT-TT80-one-group-M09-2026': _case('gtgt04-tt80-one-group-m09-2026', 'D4', '847', '2.7.4', 'Validate/04_GTGT_TT80_274.xsd', ('M', '09/2026', '01/09/2026', '30/09/2026'), None, '2026-10-27', '2026-10-27', 63, [], WORKBOOK_SERVICE,
                                            [GTGT04_NAME, TEMPLATE_TT80, ADDRESS]),
    '04GTGT-TT80-quarter-Q3-2026': _case('gtgt04-tt80-quarter-q3-2026', 'D4', '847', '2.7.4', 'Validate/04_GTGT_TT80_274.xsd', ('Q', '3/2026', '01/07/2026', '30/09/2026'), None, '2026-10-27', '2026-10-27', 63, [], WORKBOOK_SERVICE,
                                         [GTGT04_NAME, TEMPLATE_TT80, ADDRESS]),
    '04GTGT-TT80-four-groups-rounding-M08-2026': _case('gtgt04-tt80-four-groups-rounding-m08-2026', 'D4', '847', '2.7.4', 'Validate/04_GTGT_TT80_274.xsd', ('M', '08/2026', '01/08/2026', '31/08/2026'), None, '2026-10-27', '2026-10-27', 63, [], WORKBOOK_SERVICE,
                                                       [GTGT04_NAME, TEMPLATE_TT80, ADDRESS]),
    '04GTGT-TT80-reduction-annex-Q2-2026': _case('gtgt04-tt80-reduction-annex-q2-2026', 'D4', '847', '2.7.4', 'Validate/04_GTGT_TT80_274.xsd', ('Q', '2/2026', '01/04/2026', '30/06/2026'), None, '2026-10-27', '2026-10-27', 96, ['PL_NQ142_GTGT'], WORKBOOK_SERVICE,
                                                 [GTGT04_NAME, TEMPLATE_TT80, ADDRESS, 'HANG HOA A - GIẢ LẬP', 'DICH VU B - GIẢ LẬP', 'SAN XUAT C - GIẢ LẬP', 'HOAT DONG D - GIẢ LẬP', 'HANG HOA E - GIẢ LẬP']),
    # Z3 04/GTGT TT89 3.0.9 (non-gating, HTKK 5.8.2 only): KieuKy 21, tháng/quý từ 10/2026; PL 01-1 = PL_NQ204_GTGT. The
    # web publishes the 5.8.2 schema under its own id (the 5.8.1 file of the same name differs: no Header/DiaChiBds).
    '04GTGT-TT89-one-group-M10-2026': _case('gtgt04-tt89-one-group-m10-2026', 'Z3', '2035', '3.0.9', GTGT04_TT89_SCHEMA, ('M', '10/2026', '01/10/2026', '31/10/2026'), None, '2026-10-27', '2026-10-27', 74, [], WORKBOOK_SERVICE,
                                            [GTGT04_NAME, TEMPLATE_TT89, ADDRESS]),
    '04GTGT-TT89-quarter-Q4-2026': _case('gtgt04-tt89-quarter-q4-2026', 'Z3', '2035', '3.0.9', GTGT04_TT89_SCHEMA, ('Q', '4/2026', '01/10/2026', '31/12/2026'), None, '2026-10-27', '2026-10-27', 74, [], WORKBOOK_SERVICE,
                                         [GTGT04_NAME, TEMPLATE_TT89, ADDRESS]),
    '04GTGT-TT89-four-groups-rounding-M10-2026': _case('gtgt04-tt89-four-groups-rounding-m10-2026', 'Z3', '2035', '3.0.9', GTGT04_TT89_SCHEMA, ('M', '10/2026', '01/10/2026', '31/10/2026'), None, '2026-10-27', '2026-10-27', 74, [], WORKBOOK_SERVICE,
                                                       [GTGT04_NAME, TEMPLATE_TT89, ADDRESS]),
    '04GTGT-TT89-reduction-annex-M10-2026': _case('gtgt04-tt89-reduction-annex-m10-2026', 'Z3', '2035', '3.0.9', GTGT04_TT89_SCHEMA, ('M', '10/2026', '01/10/2026', '31/10/2026'), None, '2026-10-27', '2026-10-27', 107, ['PL_NQ204_GTGT'], WORKBOOK_SERVICE,
                                                  [GTGT04_NAME, TEMPLATE_TT89, ADDRESS, 'HANG HOA A - GIẢ LẬP', 'DICH VU B - GIẢ LẬP', 'SAN XUAT C - GIẢ LẬP', 'HOAT DONG D - GIẢ LẬP', 'HANG HOA E - GIẢ LẬP']),
    # Z5 01/GTGT TT89 3.0.9 (non-gating, HTKK 5.8.4 only): KieuKy 19, tháng/quý từ 10/2026, tờ khai without phụ lục, activity
    # 00 (ten_NganhNghe from Catalogue_DM_NNKD, tiểu mục 1701); 104 leaves (ct*_Cqt / ct*_Ghichu included).
    '01GTGT-TT89-zero-M10-2026': _case('gtgt01-tt89-zero-m10-2026', 'Z5', '2032', '3.0.9', GTGT01_TT89_SCHEMA, ('M', '10/2026', '01/10/2026', '31/10/2026'), None, '2026-10-27', '2026-10-27', 104, [], WORKBOOK_SERVICE,
                                       [GTGT01_NAME, TEMPLATE_TT89, ADDRESS, GTGT01_ACTIVITY]),
    '01GTGT-TT89-sale10-M10-2026': _case('gtgt01-tt89-sale10-m10-2026', 'Z5', '2032', '3.0.9', GTGT01_TT89_SCHEMA, ('M', '10/2026', '01/10/2026', '31/10/2026'), None, '2026-10-27', '2026-10-27', 104, [], WORKBOOK_SERVICE,
                                         [GTGT01_NAME, TEMPLATE_TT89, ADDRESS, GTGT01_ACTIVITY]),
    '01GTGT-TT89-quarter-Q4-2026': _case('gtgt01-tt89-quarter-q4-2026', 'Z5', '2032', '3.0.9', GTGT01_TT89_SCHEMA, ('Q', '4/2026', '01/10/2026', '31/12/2026'), None, '2026-10-27', '2026-10-27', 104, [], WORKBOOK_SERVICE,
                                         [GTGT01_NAME, TEMPLATE_TT89, ADDRESS, GTGT01_ACTIVITY]),
    '01GTGT-TT89-no-activity-M11-2026': _case('gtgt01-tt89-no-activity-m11-2026', 'Z5', '2032', '3.0.9', GTGT01_TT89_SCHEMA, ('M', '11/2026', '01/11/2026', '30/11/2026'), None, '2026-10-27', '2026-10-27', 104, [], WORKBOOK_SERVICE,
                                              [GTGT01_NAME, TEMPLATE_TT89, ADDRESS, GTGT01_ACTIVITY]),
    '01GTGT-TT89-full-M12-2026': _case('gtgt01-tt89-full-m12-2026', 'Z5', '2032', '3.0.9', GTGT01_TT89_SCHEMA, ('M', '12/2026', '01/12/2026', '31/12/2026'), None, '2026-10-27', '2026-10-27', 104, [], WORKBOOK_SERVICE,
                                       [GTGT01_NAME, TEMPLATE_TT89, ADDRESS, GTGT01_ACTIVITY]),
    '01GTGT-TT89-full-M10-2026': _case('gtgt01-tt89-full-m10-2026', 'Z5', '2032', '3.0.9', GTGT01_TT89_SCHEMA, ('M', '10/2026', '01/10/2026', '31/10/2026'), None, '2026-10-27', '2026-10-27', 104, [], WORKBOOK_SERVICE,
                                       [GTGT01_NAME, TEMPLATE_TT89, ADDRESS, GTGT01_ACTIVITY]),
    # PL 204/2025/QH15 attached (Menu sheet 01_11, XML PLuc/PL_NQ142_GTGT): 104 + 18 annex leaves (one purchase row, two sale rows).
    '01GTGT-TT89-nq204-M12-2026': _case('gtgt01-tt89-nq204-m12-2026', 'Z5', '2032', '3.0.9', GTGT01_TT89_SCHEMA, ('M', '12/2026', '01/12/2026', '31/12/2026'), None, '2026-10-27', '2026-10-27', 122, ['PL_NQ142_GTGT'], WORKBOOK_SERVICE,
                                        [GTGT01_NAME, TEMPLATE_TT89, ADDRESS, GTGT01_ACTIVITY, 'VAT TU A - GIẢ LẬP', 'HANG HOA B - GIẢ LẬP', 'DICH VU C - GIẢ LẬP']),
    '01GTGT-TT89-nq204-M10-2026': _case('gtgt01-tt89-nq204-m10-2026', 'Z5', '2032', '3.0.9', GTGT01_TT89_SCHEMA, ('M', '10/2026', '01/10/2026', '31/10/2026'), None, '2026-10-27', '2026-10-27', 122, ['PL_NQ142_GTGT'], WORKBOOK_SERVICE,
                                        [GTGT01_NAME, TEMPLATE_TT89, ADDRESS, GTGT01_ACTIVITY, 'VAT TU A - GIẢ LẬP', 'HANG HOA B - GIẢ LẬP', 'DICH VU C - GIẢ LẬP']),
    # PL 01-6/GTGT of Z5 (Menu sheets 01_6 / 01_6_2, XML PLuc/Pluc_01_6_GTGT_CSSX / _DVVT; htkk_web lib/htkk-gtgt01-tt89-annex16.ts,
    # draft field pl016): 104 + 61 annex leaves (4 head, 3 rows x 15, 2 provinces x 4, 4 totals). Texts: the synthetic unit names and
    # branch MSTs, and the catalogue names of the two provinces, wards and offices (Hải Phòng, Thái Nguyên).
    '01GTGT-TT89-pl016-cssx-M10-2026': _case('gtgt01-tt89-pl016-cssx-m10-2026', 'Z5', '2032', '3.0.9', GTGT01_TT89_SCHEMA, ('M', '10/2026', '01/10/2026', '31/10/2026'), None, '2026-10-27', '2026-10-27', 165, ['Pluc_01_6_GTGT_CSSX'], WORKBOOK_SERVICE,
                                             [GTGT01_NAME, TEMPLATE_TT89, ADDRESS, GTGT01_ACTIVITY] + PL016_TEXTS),
    '01GTGT-TT89-pl016-cssx-ratio-M10-2026': _case('gtgt01-tt89-pl016-cssx-ratio-m10-2026', 'Z5', '2032', '3.0.9', GTGT01_TT89_SCHEMA, ('M', '10/2026', '01/10/2026', '31/10/2026'), None, '2026-10-27', '2026-10-27', 165, ['Pluc_01_6_GTGT_CSSX'], WORKBOOK_SERVICE,
                                                   [GTGT01_NAME, TEMPLATE_TT89, ADDRESS, GTGT01_ACTIVITY] + PL016_TEXTS),
    '01GTGT-TT89-pl016-dtvt-M10-2026': _case('gtgt01-tt89-pl016-dtvt-m10-2026', 'Z5', '2032', '3.0.9', GTGT01_TT89_SCHEMA, ('M', '10/2026', '01/10/2026', '31/10/2026'), None, '2026-10-27', '2026-10-27', 165, ['Pluc_01_6_GTGT_DVVT'], WORKBOOK_SERVICE,
                                             [GTGT01_NAME, TEMPLATE_TT89, ADDRESS, GTGT01_ACTIVITY] + PL016_TEXTS),
    # Y7 01/TCKT TT89 3.0.9 (non-gating, HTKK 5.8.1 oracle): KieuKy 21, one bảng kê per tờ khai: 01/BK-KTHTKD (PLuc_HKD_CNKD,
    # quý 4/2026; nhóm ngành names of DM_DUNG_CHUNG DC_185) or 02/BK-KTBĐS (PLuc_CANHAN_TTS, tháng 10/2026 and lần phát sinh
    # 15/10/2026; DiaChi_BDS xã/tỉnh = the synthetic profile ward).
    '01TCKT-hop-tac-kd-two-individuals-Q4-2026': _case('tckt01-hop-tac-kd-two-individuals-q4-2026', 'Y7', '2007', '3.0.9', 'Validate/01_TCKT_TT89_309.xsd', ('Q', '4/2026', '01/10/2026', '31/12/2026'), None, '2026-10-27', '2026-10-27', 65, ['PLuc_HKD_CNKD'], WORKBOOK_SERVICE,
                                                       [TCKT_NAME, TEMPLATE_TT89, ADDRESS, 'CA NHAN HOP TAC A - GIẢ LẬP', 'CA NHAN HOP TAC B - GIẢ LẬP', 'Dịch vụ, xây dựng không bao thầu  nguyên vật liệu', 'Hoạt động kinh doanh khác']),
    '01TCKT-bds-three-lessors-M10-2026': _case('tckt01-bds-three-lessors-m10-2026', 'Y7', '2007', '3.0.9', 'Validate/01_TCKT_TT89_309.xsd', ('M', '10/2026', '01/10/2026', '31/10/2026'), None, '2026-10-27', '2026-10-27', 79, ['PLuc_CANHAN_TTS'], WORKBOOK_SERVICE,
                                               [TCKT_NAME, TEMPLATE_TT89, ADDRESS, 'CA NHAN CHO THUE A - GIẢ LẬP', 'CA NHAN CHO THUE B - GIẢ LẬP', 'CA NHAN CHO THUE C - GIẢ LẬP', 'SO 1 DUONG GIA LAP', 'SO 2 DUONG GIA LAP', 'SO 3 DUONG GIA LAP']),
    '01TCKT-bds-occurrence-D15-10-2026': _case('tckt01-bds-occurrence-d15-10-2026', 'Y7', '2007', '3.0.9', 'Validate/01_TCKT_TT89_309.xsd', ('D', '15/10/2026', '15/10/2026', '15/10/2026'), None, '2026-10-27', '2026-10-27', 63, ['PLuc_CANHAN_TTS'], WORKBOOK_SERVICE,
                                               [TCKT_NAME, TEMPLATE_TT89, ADDRESS, 'CA NHAN CHO THUE D - GIẢ LẬP', 'SO 4 DUONG GIA LAP']),
    # Y7 01/TCKT TT89 3.1.0 (non-gating, HTKK 5.8.2 oracle; Tckt01TT89Nckt310, schema 01_TCKT_TT89_310, sources byte-identical in
    # 5.8.3): the three 3.0.9 designs (rows carry ct09a / ct12a = 0) and 01/BK-KTHTKD with PL 01-3 "PL NQ 43/2026/QH16"
    # (PLuc_giamthue_NQ43: one row per ticked bảng kê row, ct09_ten = the DC_185 name of the row).
    '01TCKT-310-hop-tac-kd-two-individuals-Q4-2026': _case('tckt01-310-hop-tac-kd-two-individuals-q4-2026', 'Y7', '2007', '3.1.0', TCKT_310_SCHEMA, ('Q', '4/2026', '01/10/2026', '31/12/2026'), None, '2026-10-27', '2026-10-27', 67, ['PLuc_HKD_CNKD'], WORKBOOK_SERVICE,
                                                           [TCKT_NAME, TEMPLATE_TT89, ADDRESS, 'CA NHAN HOP TAC A - GIẢ LẬP', 'CA NHAN HOP TAC B - GIẢ LẬP', 'Dịch vụ, xây dựng không bao thầu  nguyên vật liệu', 'Hoạt động kinh doanh khác']),
    '01TCKT-310-bds-three-lessors-M10-2026': _case('tckt01-310-bds-three-lessors-m10-2026', 'Y7', '2007', '3.1.0', TCKT_310_SCHEMA, ('M', '10/2026', '01/10/2026', '31/10/2026'), None, '2026-10-27', '2026-10-27', 82, ['PLuc_CANHAN_TTS'], WORKBOOK_SERVICE,
                                                   [TCKT_NAME, TEMPLATE_TT89, ADDRESS, 'CA NHAN CHO THUE A - GIẢ LẬP', 'CA NHAN CHO THUE B - GIẢ LẬP', 'CA NHAN CHO THUE C - GIẢ LẬP', 'SO 1 DUONG GIA LAP', 'SO 2 DUONG GIA LAP', 'SO 3 DUONG GIA LAP']),
    '01TCKT-310-bds-occurrence-D15-10-2026': _case('tckt01-310-bds-occurrence-d15-10-2026', 'Y7', '2007', '3.1.0', TCKT_310_SCHEMA, ('D', '15/10/2026', '15/10/2026', '15/10/2026'), None, '2026-10-27', '2026-10-27', 64, ['PLuc_CANHAN_TTS'], WORKBOOK_SERVICE,
                                                   [TCKT_NAME, TEMPLATE_TT89, ADDRESS, 'CA NHAN CHO THUE D - GIẢ LẬP', 'SO 4 DUONG GIA LAP']),
    '01TCKT-310-pl-nq43-hop-tac-kd-Q4-2026': _case('tckt01-310-pl-nq43-hop-tac-kd-q4-2026', 'Y7', '2007', '3.1.0', TCKT_310_SCHEMA, ('Q', '4/2026', '01/10/2026', '31/12/2026'), None, '2026-10-27', '2026-10-27', 90, ['PLuc_HKD_CNKD', 'PLuc_giamthue_NQ43'], WORKBOOK_SERVICE,
                                                   [TCKT_NAME, TEMPLATE_TT89, ADDRESS, 'CA NHAN HOP TAC A - GIẢ LẬP', 'CA NHAN HOP TAC B - GIẢ LẬP', 'CA NHAN HOP TAC C - GIẢ LẬP', 'Hoạt động kinh doanh khác', 'Hoạt động cho thuê tài sản trừ bất động sản', 'Hoạt động cung cấp sản phẩm nội dung thông tin số về giải trí, trò chơi điện tử, phim số, ảnh số, nhạc số, quảng cáo số']),
}
_workbook_expected = {c['caseId']: c['expected'] for c in workbook_design.PLAN['cases'] + workbook_design.PLAN_582['cases']}
_descriptor_expected = {c['caseId']: (c['expectedLeaves'], c.get('expectedRows', {})) for c in descriptor_design.DESIGN['cases']}
# Leaves the ORIGINAL export fills with the export day (HtkkDeclarationCasePlans.ExportDatePaths):
# A2 has no control bound to TKhaiThue/ngayKy, so TTinChung.ngayKy keeps DateTime.Now.
EXPORT_DATES = {'BCTC133-B01a-basic-Y2025': (TK + 'ngayKy',)}
# Y7 (01/TCKT TT89, 3.0.9 and 3.1.0) likewise: HTKK 5.8.1 and 5.8.2 wrote the export day into TKhaiThue/ngayKy in all seven
# cases (runs of release web d2acec02c, builder c0ab30e: the only differing leaf, tree mask 2, every tax leaf equal).
EXPORT_DATES.update({_id: (TK + 'ngayKy',) for _id in ('01TCKT-hop-tac-kd-two-individuals-Q4-2026', '01TCKT-bds-three-lessors-M10-2026', '01TCKT-bds-occurrence-D15-10-2026', '01TCKT-310-hop-tac-kd-two-individuals-Q4-2026', '01TCKT-310-bds-three-lessors-M10-2026', '01TCKT-310-bds-occurrence-D15-10-2026', '01TCKT-310-pl-nq43-hop-tac-kd-Q4-2026')})
for _id, _c in CASES.items():
    _c['caseId'] = _id
    _c['exportDates'] = EXPORT_DATES.get(_id, ())
    _c['family'] = 'cnkd' if _id in hkd_design.CASES else 'descriptor' if _id in _descriptor_expected else 'workbook'
    if _c['family'] == 'workbook' and _id not in _workbook_expected:
        raise ValueError('DECLARATION_CASE_POLICY')


# Cases whose web manifest names the HTKK oracle ('htkkVersion', htkk_web generate-htkk-declaration-reference.mjs writes
# it only for a case whose spec carries it). The value must equal the registry case htkkVersion (fetch validate_manifest).
MANIFEST_HTKK_VERSION_CASES = frozenset({'01GTGT-TT89-full-M10-2026', '01GTGT-TT89-nq204-M10-2026', '01GTGT-TT89-pl016-cssx-M10-2026', '01GTGT-TT89-pl016-cssx-ratio-M10-2026', '01GTGT-TT89-pl016-dtvt-M10-2026', '01GTGT-TT89-nq204-M12-2026', '05KK-TT89-withheld-Q4-2026', '03TNDN-rate15-Y2025', '03TNDN-rate17-Y2025', '05KK-PBT-two-provinces-Q3-2026', '05KK-TT89-PBT-two-provinces-Q4-2026', '02QTT-refund-transfer-Y2025', '02QTT-dependants-Y2026', '02QTT-refund-transfer-Y2026', '01TTS-individual-one-contract-Y2025', '01TTS-individual-two-contracts-Y2025', '01TTS-organization-two-individuals-Q3-2026', '01TTS-organization-monthly-M10-2026', '04GTGT-TT80-one-group-M09-2026', '04GTGT-TT80-quarter-Q3-2026', '04GTGT-TT80-four-groups-rounding-M08-2026', '04GTGT-TT80-reduction-annex-Q2-2026', '04GTGT-TT89-one-group-M10-2026', '04GTGT-TT89-quarter-Q4-2026', '04GTGT-TT89-four-groups-rounding-M10-2026', '04GTGT-TT89-reduction-annex-M10-2026', '01GTGT-TT89-zero-M10-2026', '01GTGT-TT89-sale10-M10-2026', '01GTGT-TT89-quarter-Q4-2026', '01GTGT-TT89-no-activity-M11-2026', '01GTGT-TT89-full-M12-2026', '02NTNN-TT89-two-annexes-to-07-10-2026', '04NTNN-TT89-one-subcontractor-to-07-10-2026', '01NTNN-NCCNN-entry-part-II1-M10-2026', '01NTNN-NCCNN-entry-part-II2-M10-2026', '01NTNN-NCCNN-entry-future-contract-M10-2026', '02NTNN-TT80-two-annexes-to-06-10-2026', '04NTNN-TT80-one-subcontractor-to-06-10-2026', '02NTNN-TT89-two-annexes-from-01-06-2026', '04NTNN-TT89-one-subcontractor-from-01-06-2026', '01TCKT-310-hop-tac-kd-two-individuals-Q4-2026', '01TCKT-310-bds-three-lessors-M10-2026', '01TCKT-310-bds-occurrence-D15-10-2026', '01TCKT-310-pl-nq43-hop-tac-kd-Q4-2026'})


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
    # Y8 (original entry): the reviewed rows of the design case; the driver's fixed entry plan is checked against them. (4) ngày hợp
    # đồng ct4 is checked too (W78 01/09/2026, W86 02/09/2026; the HTKK 5.8.5 future-contract case differs only there and in ct3).
    '01NTNN-NCCNN-entry-M10-2026': (
        (_MAIN + '/BKThueNTNN/ThueNTNN', _MAIN, 'mucI_tong_', (_EMPTY_ROW,)),
        (_MAIN + '/ThueNCCNN_CNKCT/BKThueNCCNN/ThueNCCNN', _MAIN + '/ThueNCCNN_CNKCT', 'mucI_tong_', (
            {'ct1b_ma': '01', 'ct4': '2026-09-01', 'ct5': '200000000', 'ct7': '200000000', 'ct8': '5.00', 'ct10': '200000000', 'ct11': '5.00', 'ct12': '0'},)),
        (_MAIN + '/ThueNCCNN_CNKCT/BKThueCNKCT/ThueCNKCT', _MAIN + '/ThueNCCNN_CNKCT', 'mucII_tong_', (
            {'ct1b_ma': '05', 'ct4': '2026-09-02', 'ct5': '100000000', 'ct7': '100000000', 'ct8': '5.00', 'ct10': '100000000', 'ct11': '2.00', 'ct12': '0'},)),
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
# HTKK 5.8.3 Y8 one-part cases: the other part II table keeps its default template row (as part I), so HTKK exports it empty.
_Y8_ENTRY = NTNN_ROWS['01NTNN-NCCNN-entry-M10-2026']
NTNN_ROWS['01NTNN-NCCNN-entry-part-II1-M10-2026'] = (_Y8_ENTRY[0], _Y8_ENTRY[1], _Y8_ENTRY[2][:3] + ((_EMPTY_ROW,),))
NTNN_ROWS['01NTNN-NCCNN-entry-part-II2-M10-2026'] = (_Y8_ENTRY[0], _Y8_ENTRY[1][:3] + ((_EMPTY_ROW,),), _Y8_ENTRY[2])
# HTKK 5.8.5 Y8 entry with both contracts dated 31/12/2027: the entry rows, (4) ngày hợp đồng checked in the XML date form.
_FUTURE_CONTRACT = '2027-12-31'
NTNN_ROWS['01NTNN-NCCNN-entry-future-contract-M10-2026'] = tuple((path, parent, prefix, tuple(row if row is _EMPTY_ROW else dict(row, ct4=_FUTURE_CONTRACT) for row in rows), *rest)
                                                              for path, parent, prefix, rows, *rest in _Y8_ENTRY)
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
    # ct4 / ct6 (01/NTNN) are the contract and payment dates, not amounts.
    n = {k: decimal.Decimal(v) for k, v in row.items() if k not in ('ct1b_ma', 'ct4', 'ct6')}
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
NTNN04['04NTNN-TT89-one-subcontractor-to-07-10-2026'] = NTNN04['04NTNN-TT89-one-subcontractor-2026']
NTNN04['04NTNN-TT89-one-subcontractor-from-01-06-2026'] = NTNN04['04NTNN-TT89-one-subcontractor-2026']
# HTKK 5.8.3: the TT80 contracts with đến ngày 06/10/2026 (0719) keep their 30/09/2026 values.
NTNN04['04NTNN-TT80-one-subcontractor-to-06-10-2026'] = NTNN04['04NTNN-TT80-one-subcontractor-2026']


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
NTNN02['02NTNN-TT89-two-annexes-to-07-10-2026'] = NTNN02['02NTNN-TT89-two-annexes-2026']
NTNN02['02NTNN-TT89-two-annexes-from-01-06-2026'] = NTNN02['02NTNN-TT89-two-annexes-2026']
NTNN02['02NTNN-TT80-two-annexes-to-06-10-2026'] = NTNN02['02NTNN-TT80-two-annexes-2026']
# The TT80 form (C9) names row 2 DThuChuaGomGTGT (TT89: DThuTinhThue) and its 02-1 rows carry ct10 (số lượng lao động).
_NTNN02_TT80 = frozenset({'02NTNN-TT80-two-annexes-2026', '02NTNN-TT80-two-annexes-to-06-10-2026'})


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


# Independent 01/TTS oracle (G7): the reviewed synthetic rows of the design cases and a Decimal recomputation of
# Tts01TT40Nckt283.CellChange_1/2 for whole-month periods inside one year (never the TypeScript engine):
# period months = (yTo-yFrom)*12 + mTo - mFrom + 1, value = months * giá; contract row = sums; DT bình quân =
# Math.Round(value / months) half to even, on the contract and its periods; DT trong năm = sum of the period values of
# the year (01-2: per individual MST); taxable when > 100.000.000; DT tính thuế = value when taxable; GTGT = TNCN =
# ROUND(DT tính thuế * 5%) half away from zero; [23]/[24] = sums over the periods starting in the declared period
# (năm, tháng or quý of từ ngày); [25] = [26] = ROUND([24] * 5%); [28] = ROUND([27] * 5%); [29] = [26] + [28].
# Rows: (code, MST of the individual or '', từ ngày, đến ngày, giá 1 tháng) in table order.
TTS_ROWS = {
    '01TTS-individual-one-contract-Y2025': (('Y', 2025, None), '0', (('01', '', '01/01/2025', '31/12/2025', '0'), ('02', '', '01/01/2025', '30/06/2025', '10000000'), ('03', '', '01/07/2025', '31/12/2025', '10000000')), '10000010'),
    '01TTS-individual-two-contracts-Y2025': (('Y', 2025, None), '0', (('01', '', '01/01/2025', '30/06/2025', '0'), ('04', '', '01/01/2025', '30/06/2025', '8000000'), ('01', '', '01/07/2025', '31/12/2025', '0'), ('02', '', '01/07/2025', '30/09/2025', '5000000'), ('03', '', '01/10/2025', '31/12/2025', '5000000')), '0'),
    '01TTS-organization-two-individuals-Q3-2026': (('Q', 2026, 3), '0', (('01', '9999999901', '01/01/2026', '31/12/2026', '0'),) + tuple(('02' if i < 3 else '03', '', f, t, '15000010') for i, (f, t) in enumerate((('01/01/2026', '31/03/2026'), ('01/04/2026', '30/06/2026'), ('01/07/2026', '30/09/2026'), ('01/10/2026', '31/12/2026')))) + (('01', '9999999919', '01/07/2026', '31/12/2026', '0'), ('02', '', '01/07/2026', '30/09/2026', '5000000'), ('03', '', '01/10/2026', '31/12/2026', '5000000')), '0'),
    '01TTS-organization-monthly-M10-2026': (('M', 2026, 10), '0', (('01', '9999999901', '01/10/2026', '30/11/2026', '0'), ('02', '', '01/10/2026', '31/10/2026', '50000001'), ('03', '', '01/11/2026', '30/11/2026', '50000000')), '0'),
}
TTS_THRESHOLD = decimal.Decimal(100000000)
TTS_02_LEAVES = {'ct20': 'ct22', 'ct21': 'ct23', 'ct22': 'ct24', 'ct22a': 'ct24a', 'ct23': 'ct25', 'ct24': 'ct26', 'ct25': 'ct27', 'ct26': 'ct28'}


def _half_even(value):
    return value.quantize(decimal.Decimal(1), rounding=decimal.ROUND_HALF_EVEN)


def tts_expected(case_id):
    """Per-row leaves (ct20, ct21, ct22, ct22a, ct23, ct24, ct25, ct26) and CaNhanKeKhai of a G7 design case."""
    (kind, year, number), _, table, ct27 = TTS_ROWS[case_id]
    D = decimal.Decimal
    groups = []
    for code, mst, start, end, price in table:
        d1, m1, y1 = (int(x) for x in start.split('/'))
        d2, m2, y2 = (int(x) for x in end.split('/'))
        if code == '01':
            groups.append({'mst': mst, 'periods': []})
            continue
        months = (y2 - y1) * 12 + m2 - m1 + 1
        groups[-1]['periods'].append({'year': y1, 'month': m1, 'months': D(months), 'value': D(months) * D(price)})
    totals = {}
    for g in groups:
        for p in g['periods']:
            key = (g['mst'], p['year'])
            totals[key] = totals.get(key, D(0)) + p['value']
    rows, ct23, ct24 = [], D(0), D(0)
    for g in groups:
        months = sum((p['months'] for p in g['periods']), D(0))
        value = sum((p['value'] for p in g['periods']), D(0))
        average = _half_even(value / months) if months else D(0)
        cells = []
        for p in g['periods']:
            year_total = totals[(g['mst'], p['year'])]
            taxable = year_total > TTS_THRESHOLD
            revenue = p['value'] if taxable else D(0)
            tax = _round(revenue * D('0.05'))
            cells.append({'ct20': '0', 'ct21': str(p['value']), 'ct22': str(average), 'ct22a': str(year_total), 'ct23': '1' if taxable else '0', 'ct24': str(revenue), 'ct25': str(tax), 'ct26': str(tax)})
            inside = p['year'] == year and (kind == 'Y' or (kind == 'M' and p['month'] == number) or (kind == 'Q' and (p['month'] - 1) // 3 + 1 == number))
            if inside:
                ct23 += p['value']
                ct24 += revenue
        hd_revenue = sum((D(c['ct24']) for c in cells), D(0))
        hd_tax = _round(hd_revenue * D('0.05'))
        # The month leaf is the hidden column BA = IF(contract months<>0, ...); the contract months column has a path_
        # leaf the file never carries, so the original re-export of an imported file writes 0 (runs 43678752516,
        # 43678754348: 12 and 6 in, 0 out); the web file writes the same.
        rows.append({'ct20': '0', 'ct21': str(value), 'ct22': str(average), 'ct22a': '0', 'ct23': '0', 'ct24': str(hd_revenue), 'ct25': str(hd_tax), 'ct26': str(hd_tax)})
        rows.extend(cells)
    ct25 = _round(ct24 * D('0.05'))
    ct28 = _round(D(ct27) * D('0.05'))
    main = {'ct23': str(ct23), 'ct24': str(ct24), 'ct25': str(ct25), 'ct26': str(ct25), 'ct27': ct27, 'ct28': str(ct28), 'ct29': str(ct25 + ct28)}
    return rows, main


def _tts(case_id, root):
    rows, main = tts_expected(case_id)
    found = root.findall(_xpath('HSoKhaiThue/PLuc/*/CTietBKeHDongTTS'))
    if len(found) != len(rows):
        reject('VALUE')
    # 01-2/BK-TTS (PLuc_02_BK_TTS) numbers the same columns two places later (ct22 months … ct28 TNCN).
    names = TTS_02_LEAVES if root.find(_xpath('HSoKhaiThue/PLuc/PLuc_02_BK_TTS')) is not None else {}
    for node, row in zip(found, rows):
        for name, value in row.items():
            if [(n.text or '') for n in node.findall('{%s}%s' % (NS, names.get(name, name)))] != [value]:
                reject('VALUE')
    block = root.find(_xpath('HSoKhaiThue/CTieuTKhaiChinh'))
    if block is None:
        reject('STRUCTURE')
    for name, value in main.items():  # ct23..ct29 occur once under CTieuTKhaiChinh (CaNhanKeKhai)
        if [(n.text or '') for n in block.iter('{%s}%s' % (NS, name))] != [value]:
            reject('VALUE')


# Independent 04/GTGT oracle (D4, Gtgt04TT80Nckt274; never the TypeScript engine): the reviewed synthetic inputs of the
# design cases and a Decimal recomputation. Without PL 01-3, TinhLaiChiTieu23_25_27_29Default: [23] = ROUND([22] x 1%),
# [25] = ROUND([24] x 5%), [27] = ROUND([26] x 3%), [29] = ROUND([28] x 2%). With PL 01-3 (part II rows: name, value,
# rate): F = ROUND(rate x 80/100, 1), G = ROUND(D x (rate - F)/100); TinhLaiChiTieu22_den_28_TK sets [22]/[24]/[26]/[28] to
# the sum of D at 1/5/3/2 %, TheoPL01_3 [23]... = ROUND(sum x rate/100 - sum of G at that rate). [30] = sum of revenue,
# [31] = sum of tax, [32] = [21] + [30]; ct9 = sum of G - part I tax (no part I rows). ROUND = half away from zero.
# Mục B (khai riêng thu hộ) stays locked (lockMucAhoacB): one empty row, every amount 0.
GTGT04_GROUPS = (('PPhoiCCapHHoa', 'ct22', 'ct23', '1'), ('DVuXDungKoBaoThauNVL', 'ct24', 'ct25', '5'),
                 ('HHoaXDungCoBaoThauNVL', 'ct26', 'ct27', '3'), ('HDongKDoanhKhac', 'ct28', 'ct29', '2'))
GTGT04_ROWS = {
    '04GTGT-TT80-one-group-M09-2026': ('5000000', {'1': '200000000'}, None),
    '04GTGT-TT80-quarter-Q3-2026': ('0', {'5': '150000000', '2': '30000000'}, None),
    '04GTGT-TT80-four-groups-rounding-M08-2026': ('1000000', {'1': '123456750', '5': '50000010', '3': '33333350', '2': '77777775'}, None),
    '04GTGT-TT80-reduction-annex-Q2-2026': ('1000000', None, (('HANG HOA A - GIẢ LẬP', '123456750', '1'), ('DICH VU B - GIẢ LẬP', '50000010', '5'),
                                                              ('SAN XUAT C - GIẢ LẬP', '33333350', '3'), ('HOAT DONG D - GIẢ LẬP', '77777775', '2'),
                                                              ('HANG HOA E - GIẢ LẬP', '1250', '1'))),
    # Z3 (TT89): ([21a] không chịu thuế, [21b] thuế suất 0%) instead of [21]; [30a] = [21b] + [30], [32] = [21a] + [30a].
    '04GTGT-TT89-one-group-M10-2026': (('5000000', '0'), {'1': '200000000'}, None),
    '04GTGT-TT89-quarter-Q4-2026': (('0', '10000000'), {'5': '150000000', '2': '30000000'}, None),
    '04GTGT-TT89-four-groups-rounding-M10-2026': (('1000000', '0'), {'1': '123456750', '5': '50000010', '3': '33333350', '2': '77777775'}, None),
    '04GTGT-TT89-reduction-annex-M10-2026': (('1000000', '0'), None, (('HANG HOA A - GIẢ LẬP', '123456750', '1'), ('DICH VU B - GIẢ LẬP', '50000010', '5'),
                                                               ('SAN XUAT C - GIẢ LẬP', '33333350', '3'), ('HOAT DONG D - GIẢ LẬP', '77777775', '2'),
                                                               ('HANG HOA E - GIẢ LẬP', '1250', '1'))),
}


def gtgt04_tt89(case_id):
    return isinstance(GTGT04_ROWS[case_id][0], tuple)


def gtgt04_annex(case_id):
    """PLuc element of the reduction annex: PL 01-3 of D4 (NQ 142/174/204), PL 01-1 of Z3 (NQ 204/2025)."""
    return 'PL_NQ204_GTGT' if gtgt04_tt89(case_id) else 'PL_NQ142_GTGT'


def gtgt04_expected(case_id):
    """(main leaves by path under KhaiThueTPPTTTDT, PL 01-3 sale rows, PL 01-3 totals) of a D4 design case."""
    ct21, groups, annex = GTGT04_ROWS[case_id]
    D = decimal.Decimal
    rows, revenue, reduced = [], {}, {}
    if annex is not None:
        for name, value, rate in annex:
            after = (D(rate) * 80 / 100).quantize(D('0.1'), rounding=decimal.ROUND_HALF_UP)
            cut = _round(D(value) * (D(rate) - after) / 100)
            rows.append({'tenHHDV': name, 'giaTriHHDV': value, 'thueSuatTheoQuyDinh': rate, 'thueSuatSauGiam': str(after), 'thueGTGTDuocGiam': str(cut)})
            revenue[rate] = revenue.get(rate, D(0)) + D(value)
            reduced[rate] = reduced.get(rate, D(0)) + cut
    else:
        revenue = {rate: D(value) for rate, value in groups.items()}
    tt89 = isinstance(ct21, tuple)
    main, total, tax = ({'ct21a': ct21[0], 'ct21b': ct21[1]} if tt89 else {'ct21': ct21}), D(0), D(0)
    for group, rev_leaf, tax_leaf, rate in GTGT04_GROUPS:
        value = revenue.get(rate, D(0))
        amount = _round(value * D(rate) / 100 - reduced.get(rate, D(0)))
        main[group + '/' + rev_leaf], main[group + '/' + tax_leaf] = str(value), str(amount)
        total, tax = total + value, tax + amount
    main['DoanhThuVaSoThuePNop/ct30'], main['DoanhThuVaSoThuePNop/ct31'] = str(total), str(tax)
    if tt89:
        main['ct30a'] = str(D(ct21[1]) + total)
        main['ct32'] = str(D(ct21[0]) + D(ct21[1]) + total)
    else:
        main['ct32'] = str(D(ct21) + total)
    totals = {'tongCongGiaTriHHDV': str(sum((D(r['giaTriHHDV']) for r in rows), D(0))), 'tongCongThueGTGTDuocGiam': str(sum((D(r['thueGTGTDuocGiam']) for r in rows), D(0)))} if rows else {}
    return main, rows, totals


def _gtgt04(case_id, root):
    main, rows, totals = gtgt04_expected(case_id)
    block = root.find(_xpath('HSoKhaiThue/CTieuTKhaiChinh'))
    if block is None:
        reject('STRUCTURE')
    for path, value in main.items():
        if [(n.text or '') for n in block.findall(_xpath('KhaiThueTPPTTTDT/' + path))] != [value]:
            reject('VALUE')
    flags = ('hdKhaiRieng', 'batDongSan', 'taiSanKhac') if gtgt04_tt89(case_id) else ('khaiRiengThuHo',)
    for flag in flags:  # D4 khai riêng thu hộ; Z3 kê khai riêng, bất động sản, tài sản khác: unticked in the period dialog
        if [(n.text or '') for n in block.findall(_xpath('Header/' + flag))] != ['0']:
            reject('VALUE')
    thu_ho = block.findall(_xpath('KhaiRiengDoiVoiKhoanThuHo/KhoanThuHoCTGTGT'))
    if len(thu_ho) != 1 or [(n.text or '') for n in thu_ho[0]] != ['', '0', '0', '0']:
        reject('VALUE')
    sale = root.findall(_xpath('HSoKhaiThue/PLuc/%s/HH_DV_BanRaTrongKy/BangKeTenHHDV' % gtgt04_annex(case_id)))
    if len(sale) != len(rows):
        reject('VALUE')
    for node, row in zip(sale, rows):
        for name, value in row.items():
            if [(n.text or '') for n in node.findall('{%s}%s' % (NS, name))] != [value]:
                reject('VALUE')
    if rows:
        part = root.find(_xpath('HSoKhaiThue/PLuc/' + gtgt04_annex(case_id)))
        for name, value in totals.items():
            if [(n.text or '') for n in part.findall(_xpath('HH_DV_BanRaTrongKy/' + name))] != [value]:
                reject('VALUE')
        if [(n.text or '') for n in part.findall(_xpath('HH_DV_MuaVaoTrongKy/tongCongThueGTGTHHDV'))] != ['0']:
            reject('VALUE')
        if [(n.text or '') for n in part.findall(_xpath('ChenhLech/ct9'))] != [totals['tongCongThueGTGTDuocGiam']]:
            reject('VALUE')


# Independent 01/TCKT oracle (Y7, Tckt01TT89Nckt309 and the XLS formulas of 01_TCKT_TT89_309; never the TypeScript engine).
# 01/BK-KTHTKD rows (MST, nhóm ngành, [07] G, [08] H): K = rate of the nhóm (IF(J="01",0.5%,"02",2%,"03",5%,"04",1.5%,"05",5%,
# "06",1%)), I = H x K (no ROUND), ct06_tyLe = K with the 2 places of the control DefaultValue "0,00"; totals ct11..ct13.
# 02/BK-KTBĐS rows ([08] L, [09] M, [10] N): O = 0 if N else ROUND(L x 5 / 100), P = 0 if N else ROUND((L - M) x 5 / 100),
# half away from zero; totals. CTieuTKhaiChinh ct7..ct9 / ct11..ct13 come from the expected leaves of the design case.
TCKT_RATES = {'01': '0.005', '02': '0.02', '03': '0.05', '04': '0.015', '05': '0.05', '06': '0.01'}
TCKT_ROWS = {
    '01TCKT-hop-tac-kd-two-individuals-Q4-2026': ('01-1', (('9999999901', '02', '300000000', '300000000'), ('9999999919', '06', '120000000', '110000000'))),
    '01TCKT-bds-three-lessors-M10-2026': ('01-2', (('9999999901', '60000010', '10', False), ('9999999919', '1200000001', '200000000', False), ('9999999926', '300000000', '0', True))),
    '01TCKT-bds-occurrence-D15-10-2026': ('01-2', (('9999999933', '80000000', '20000000', False),)),
    # 3.1.0 (Tckt01TT89Nckt310, 01_TCKT_TT89_310): a fifth element is the NQ 43/2026/QH16 tick (ct09a / ct12a).
    '01TCKT-310-hop-tac-kd-two-individuals-Q4-2026': ('01-1', (('9999999901', '02', '300000000', '300000000', False), ('9999999919', '06', '120000000', '110000000', False))),
    '01TCKT-310-bds-three-lessors-M10-2026': ('01-2', (('9999999901', '60000010', '10', False, False), ('9999999919', '1200000001', '200000000', False, False), ('9999999926', '300000000', '0', True, False))),
    '01TCKT-310-bds-occurrence-D15-10-2026': ('01-2', (('9999999933', '80000000', '20000000', False, False),)),
    '01TCKT-310-pl-nq43-hop-tac-kd-Q4-2026': ('01-1', (('9999999901', '06', '500000000', '500000000', True), ('9999999919', '03', '200000000', '200000000', True), ('9999999926', '05', '100000000', '80000000', False))),
}


# 01/GTGT TT89 (Z5, 01_GTGT_TT89_309 sheet 01 of HTKK 5.8.4): Decimal recomputation of the source XLS formulas and the
# Gtgt01TT89Nckt309 handlers (never the TypeScript engine). Inputs are the synthetic design inputs of each case:
# CellChange_0 writes [31] = ROUND([30] x 5/100) and [33] = R61 = ROUND([32] x 10/100) (no PL 204/2025/QH15, V19 = 0);
# XuLyCheckboxCt21 sets 13 cells to 0 when [21] is ticked; [32b] J63 is locked at 0; J58 [27] = [29] + [30] + [32] + [32a] -
# [32b], L58 [28] = [31] + [33], J65 [34] = [26] + [27] + [34a], L65 [35] = [28], L69 [36] = [35] - [25]; P = [36] - [22] + [37]
# - [38] - [39a]: L78 [40a] = max(P, 0), L80 [40] = max([40a] - [40b], 0), L81 [41] = max(-P, 0), L83 [43] = max([41] - [42], 0).
GTGT01_TT89_INPUTS = {
    '01GTGT-TT89-zero-M10-2026': {},
    '01GTGT-TT89-sale10-M10-2026': {'ct32': '1000000'},
    '01GTGT-TT89-quarter-Q4-2026': {'ct23': '200000000', 'ct24': '20000000', 'ct25': '20000000', 'ct26': '10000000', 'ct30': '100000000', 'ct32': '50000000'},
    '01GTGT-TT89-no-activity-M11-2026': {'ct21': '1', 'ct22': '5000000', 'ct38': '1000000'},
    '01GTGT-TT89-full-M12-2026': {'ct22': '3000000', 'ct23': '40000000', 'ct24': '4000000', 'ct23a': '10000000', 'ct24a': '1000000', 'ct25': '4000000', 'ct26': '2000000', 'ct29': '5000000',
                                  'ct30': '100000010', 'ct32': '200000005', 'ct32a': '1000000', 'ct34a': '700000', 'ct37': '200000', 'ct38': '100000', 'ct39a': '50000', 'ct40b': '40000'},
    '01GTGT-TT89-full-M10-2026': {'ct22': '3000000', 'ct23': '40000000', 'ct24': '4000000', 'ct23a': '10000000', 'ct24a': '1000000', 'ct25': '4000000', 'ct26': '2000000', 'ct29': '5000000',
                                  'ct30': '100000010', 'ct32': '200000005', 'ct32a': '1000000', 'ct34a': '700000', 'ct37': '200000', 'ct38': '100000', 'ct39a': '50000', 'ct40b': '40000'},
    '01GTGT-TT89-nq204-M12-2026': {'ct23': '50000000', 'ct24': '4000000', 'ct25': '4000000'},
    '01GTGT-TT89-nq204-M10-2026': {'ct23': '50000000', 'ct24': '4000000', 'ct25': '4000000'},
    '01GTGT-TT89-pl016-cssx-M10-2026': {'ct30': '400000000', 'ct32': '600000000'},
    '01GTGT-TT89-pl016-cssx-ratio-M10-2026': {'ct30': '2000000000', 'ct32': '6000000000'},
    '01GTGT-TT89-pl016-dtvt-M10-2026': {'ct32': '600000000'},
}
# PL 01-6/GTGT of a Z5 case: (sheet, [06], [07], rows (place, [14], [15])). Same formulas as D1's 01-6 (htkk_web
# data/htkk-01-gtgt-tt89-annex16-contract.json): [16] = [14] + [15]; formula [17] = ROUND([14] x 1%) + ROUND([15] x 2%); CSSX:
# when [06] >= sum of [17] (TinhCot_17_21_Pl_01_6CSSX) [17] stays, [21] = 0, else [17] = 0 and [21] = ROUND([06] x [16] / [07]);
# one province row per tỉnh in order of first appearance ([18] / [22] sums); [19] / [23] their sums, [20] = [06] - [19], [24] =
# [06] - [23]. ĐTVT has no [21] branch.
GTGT01_TT89_PL016 = {
    '01GTGT-TT89-pl016-cssx-M10-2026': ('CSSX', '50000000', '900000000', ((PL016_HP, '100000050', '200000050'), (PL016_TN, '0', '150000075'), (PL016_HP_CUC, '50', '0'))),
    '01GTGT-TT89-pl016-cssx-ratio-M10-2026': ('CSSX', '70000001', '7000000000', ((PL016_HP, '1000000000', '2000000001'), (PL016_TN, '0', '1500000000'), (PL016_HP_CUC, '333333333', '0'))),
    '01GTGT-TT89-pl016-dtvt-M10-2026': ('DVVT', '30000000', '0', ((PL016_HP, '0', '200000050'), (PL016_TN, '0', '150000075'), (PL016_HP_CUC, '0', '50'))),
}
# PL 204/2025/QH15 (workbook sheet 01_10, XML PL_NQ142_GTGT) of a Z5 case: (purchase rows, sale rows) as (name, value). Table I:
# (4) = ROUND(D x 8/100); table II: (4) = 10, (5) = ROUND(10 x 80/100, 1) = 8, (6) = ROUND(D x (10 - 8)/100); [05]..[08] are the
# column sums and [09] = [08] - [06]. CellChange_9 (column D) sets [32] := J9 = SUM(D) of table II and [33] := R61 =
# ROUND([32] x 10/100 - I9, 0) with I9 = [08] (TinhLaiChiTieu32_TK, TinhCt33TrenToKhai, V19 = 1).
GTGT01_TT89_NQ204 = {
    '01GTGT-TT89-nq204-M12-2026': ((('VAT TU A - GIẢ LẬP', '50000000'),), (('HANG HOA B - GIẢ LẬP', '200000000'), ('DICH VU C - GIẢ LẬP', '100000025'))),
    '01GTGT-TT89-nq204-M10-2026': ((('VAT TU A - GIẢ LẬP', '50000000'),), (('HANG HOA B - GIẢ LẬP', '200000000'), ('DICH VU C - GIẢ LẬP', '100000025'))),
}
GTGT01_TT89_NO_ACTIVITY = ('ct23', 'ct24', 'ct23a', 'ct24a', 'ct25', 'ct26', 'ct29', 'ct30', 'ct31', 'ct32', 'ct33', 'ct32a', 'ct34a')
GTGT01_TT89_LEAVES = ('ct22', 'ct23', 'ct24', 'ct23a', 'ct24a', 'ct25', 'ct26', 'ct27', 'ct28', 'ct29', 'ct30', 'ct31', 'ct32', 'ct33', 'ct32a', 'ct32b', 'ct34a',
                      'ct34', 'ct35', 'ct36', 'ct37', 'ct38', 'ct39a', 'ct40a', 'ct40b', 'ct40', 'ct41', 'ct42', 'ct43')


def gtgt01_tt89_expected(case_id):
    """Every tax leaf of CTieuTKhaiChinh of a Z5 design case (ct21 as the exporter writes the checkbox: 1 / 0)."""
    raw = GTGT01_TT89_INPUTS[case_id]
    D = decimal.Decimal
    v = {k: D(x) for k, x in raw.items() if k != 'ct21'}
    g = lambda k: v.get(k, D(0))
    ticked = raw.get('ct21') == '1'
    if ticked:
        for k in GTGT01_TT89_NO_ACTIVITY:
            v[k] = D(0)
    elif case_id in GTGT01_TT89_NQ204:
        sale = gtgt01_tt89_nq204_expected(case_id)[3]
        v['ct32'] = D(sale['tongCongGiaTriHHDV'])
        v['ct31'], v['ct33'] = _round(g('ct30') * 5 / 100), _round(g('ct32') * 10 / 100 - D(sale['tongCongThueGTGTDuocGiam']))
    else:
        v['ct31'], v['ct33'] = _round(g('ct30') * 5 / 100), _round(g('ct32') * 10 / 100)
    v['ct32b'] = D(0)
    v['ct27'] = g('ct29') + g('ct30') + g('ct32') + g('ct32a') - g('ct32b')
    v['ct28'] = g('ct31') + g('ct33')
    v['ct34'], v['ct35'] = g('ct26') + g('ct27') + g('ct34a'), g('ct28')
    v['ct36'] = g('ct35') - g('ct25')
    position = g('ct36') - g('ct22') + g('ct37') - g('ct38') - g('ct39a')
    v['ct40a'] = max(position, D(0)); v['ct40'] = max(g('ct40a') - g('ct40b'), D(0))
    v['ct41'] = max(-position, D(0)); v['ct43'] = max(g('ct41') - g('ct42'), D(0))
    return {'ct21': '1' if ticked else '0', **{k: str(g(k)) for k in GTGT01_TT89_LEAVES}}


def gtgt01_tt89_nq204_expected(case_id):
    """PL_NQ142_GTGT of a Z5 case: (purchase rows, purchase totals, sale rows, sale totals, ct9) from the XLS formulas."""
    D = decimal.Decimal
    purchases, sales = GTGT01_TT89_NQ204[case_id]
    p_rows = [{'tenHHDVMuaVao': n, 'giaTriHHDVMuaVao': x, 'thueGTGTHHDV': str(_round(D(x) * 8 / 100))} for n, x in purchases]
    s_rows = [{'tenHHDV': n, 'giaTriHHDV': x, 'thueSuatTheoQuyDinh': '10', 'thueSuatSauGiam': '8', 'thueGTGTDuocGiam': str(_round(D(x) * (10 - 8) / 100))} for n, x in sales]
    p_tot = {'tongCongGiaTriHHDVMuaVao': str(sum(D(r['giaTriHHDVMuaVao']) for r in p_rows)), 'tongCongThueGTGTHHDV': str(sum(D(r['thueGTGTHHDV']) for r in p_rows))}
    s_tot = {'tongCongGiaTriHHDV': str(sum(D(r['giaTriHHDV']) for r in s_rows)), 'tongCongThueGTGTDuocGiam': str(sum(D(r['thueGTGTDuocGiam']) for r in s_rows))}
    return p_rows, p_tot, s_rows, s_tot, str(D(s_tot['tongCongThueGTGTDuocGiam']) - D(p_tot['tongCongThueGTGTHHDV']))


def gtgt01_tt89_pl016_expected(case_id):
    """Pluc_01_6_GTGT_<sheet> of a Z5 case: (node, head, rows, provinces, totals) from the XLS formulas, exact decimals."""
    D = decimal.Decimal
    sheet, ct06, ct07, table = GTGT01_TT89_PL016[case_id]
    o15, o16 = D(ct06), D(ct07)
    base = [(place, D(k), D(l), D(k) + D(l), _round(D(k) * 1 / 100) + _round(D(l) * 2 / 100)) for place, k, l in table]
    formula = sheet == 'DVVT' or o15 - sum(row[4] for row in base) >= 0
    rows, order = [], []
    for n, (place, k, l, m, z) in enumerate(base, 1):
        ct21 = D(0) if formula else _round(o15 * m / o16)
        rows.append({'ct09': 'CO SO GIA LAP %d - KHONG NOP' % n, 'ct10': '9999999997-00%d' % n, 'ma_xa': place[0], 'ten_xa': place[1], 'ct11_huyen_ma': '', 'ct11_huyen_ten': '',
                     'ct12_tinh_ma': place[2], 'ct12_tinh_ten': place[3], 'ct13_cqt_ma': place[4], 'ct13_cqt_ten': place[5], 'ct14': str(k), 'ct15': str(l), 'ct16': str(m),
                     'ct17': str(z if formula else D(0)), 'ct21': str(ct21)})
        if (place[2], place[3]) not in order:
            order.append((place[2], place[3]))
    provinces = [{'ct18': str(sum(D(r['ct17']) for r in rows if r['ct12_tinh_ma'] == code)), 'ct22': str(sum(D(r['ct21']) for r in rows if r['ct12_tinh_ma'] == code)), 'ct18_tinh_ma': code, 'ct18_tinh_ten': name} for code, name in order]
    ct19, ct23 = sum(D(p['ct18']) for p in provinces), sum(D(p['ct22']) for p in provinces)
    totals = {'ct19': str(ct19), 'ct23': str(ct23), 'ct20': str(o15 - ct19 if formula else D(0)), 'ct24': str(D(0) if formula else o15 - ct23)}
    head = {'ct10a_csxs': '1' if sheet == 'CSSX' else '0', 'ct10a_dvvt': '0' if sheet == 'CSSX' else '1', 'ct06': ct06, 'ct07': ct07}
    return 'Pluc_01_6_GTGT_' + sheet, head, rows, provinces, totals


def _gtgt01_tt89_pl016(case_id, root):
    node, head, rows, provinces, totals = gtgt01_tt89_pl016_expected(case_id)
    annex = root.find(_xpath('HSoKhaiThue/PLuc/' + node))
    if annex is None:
        reject('STRUCTURE')
    for name, value in head.items():
        if [(n.text or '') for n in annex.findall('{%s}%s' % (NS, name))] != [value]:
            reject('VALUE')
    for table, expected in (('NoiDungBangPhanBo', rows), ('cong_ct18', provinces)):
        found = annex.findall('{%s}%s' % (NS, table))
        if len(found) != len(expected):
            reject('VALUE')
        for k, (element, row) in enumerate(zip(found, expected), 1):
            if element.attrib != {'id': 'ID_%d' % k}:
                reject('VALUE')
            for name, value in row.items():
                if [(n.text or '') for n in element.findall('{%s}%s' % (NS, name))] != [value]:
                    reject('VALUE')
    for group, names in (('CongCacTinh', ('ct19', 'ct23')), ('SoThuePhaiNop', ('ct20', 'ct24'))):
        for name in names:
            if [(n.text or '') for n in annex.findall(_xpath(group + '/' + name))] != [totals[name]]:
                reject('VALUE')


def _gtgt01_tt89(case_id, root):
    main = root.find('./{%s}HSoKhaiThue/{%s}CTieuTKhaiChinh' % (NS, NS))
    for name, value in gtgt01_tt89_expected(case_id).items():
        if [(n.text or '') for n in main.iter('{%s}%s' % (NS, name))] != [value]:
            reject('VALUE')
    if case_id in GTGT01_TT89_NQ204:
        p_rows, p_tot, s_rows, s_tot, ct9 = gtgt01_tt89_nq204_expected(case_id)
        annex = root.find(_xpath('HSoKhaiThue/PLuc/PL_NQ142_GTGT'))
        if annex is None:
            reject('STRUCTURE')
        for table, rows, totals in (('HH_DV_MuaVaoTrongKy', p_rows, p_tot), ('HH_DV_BanRaTrongKy', s_rows, s_tot)):
            nodes = annex.findall(_xpath(table + '/BangKeTenHHDV'))
            if len(nodes) != len(rows):
                reject('VALUE')
            for node, row in zip(nodes, rows):
                for name, value in row.items():
                    if [(n.text or '') for n in node.findall('{%s}%s' % (NS, name))] != [value]:
                        reject('VALUE')
            for name, value in totals.items():
                if [(n.text or '') for n in annex.findall(_xpath(table + '/' + name))] != [value]:
                    reject('VALUE')
        if [(n.text or '') for n in annex.findall(_xpath('ChenhLech/ct9'))] != [ct9]:
            reject('VALUE')
    if case_id in GTGT01_TT89_PL016:
        _gtgt01_tt89_pl016(case_id, root)


def tckt_expected(case_id):
    """Per-row leaves and totals of a Y7 design case. 3.1.0 rows (a fifth element, the NQ 43 tick) follow the 310 workbook:
    01-1 I = ROUND(H x K - H x K x 0,3) when ticked, else ROUND(H x K); 01-2 P = ROUND(AB - AB x 0,3) when ticked, else AB (the
    3.0.9 P); ct09a / ct12a = the tick."""
    sheet, table = TCKT_ROWS[case_id]
    D = decimal.Decimal
    rows = []
    if sheet == '01-1':
        sums = [D(0), D(0), D(0)]
        for row in table:
            mst, code, revenue, taxable = row[:4]
            rate = D(TCKT_RATES[code])
            tax = D(taxable) * rate
            if len(row) == 5:
                tax = _round(tax - tax * D('0.3')) if row[4] else _round(tax)
            if tax != tax.to_integral_value() or rate != rate.quantize(D('0.01')):
                reject('VALUE')
            rows.append({'ct05': mst, 'ct06_ma': code, 'ct06_tyLe': str(rate.quantize(D('0.01'))), 'ct07': revenue, 'ct08': taxable, 'ct09': str(int(tax)), **({'ct09a': '1' if row[4] else '0'} if len(row) == 5 else {})})
            sums = [sums[0] + D(revenue), sums[1] + D(taxable), sums[2] + tax]
        return 'PLuc_HKD_CNKD', 'CTietBKeHKD_CNKD', rows, {'ct11': str(int(sums[0])), 'ct12': str(int(sums[1])), 'ct13': str(int(sums[2]))}
    sums = [D(0), D(0), D(0), D(0)]
    for row in table:
        mst, revenue, deducted, exempt = row[:4]
        vat = D(0) if exempt else _round(D(revenue) * 5 / 100)
        pit = D(0) if exempt else _round((D(revenue) - D(deducted)) * 5 / 100)
        if len(row) == 5 and row[4]:
            pit = _round(pit - pit * D('0.3'))
        rows.append({'ct06': mst, 'ct08': revenue, 'ct09': deducted, 'ct10': '1' if exempt else '0', 'ct11': str(vat), 'ct12': str(pit), **({'ct12a': '1' if row[4] else '0'} if len(row) == 5 else {})})
        sums = [sums[0] + D(revenue), sums[1] + D(deducted), sums[2] + vat, sums[3] + pit]
    return 'PLuc_CANHAN_TTS', 'CTietBKeCNTTS', rows, {'tong_doanhThu': str(sums[0]), 'tong_duocTru': str(sums[1]), 'tong_thueGTGT': str(sums[2]), 'tong_thueTNCN': str(sums[3])}


def tckt_reduction_expected(case_id):
    """PL 01-3 "PL NQ 43/2026/QH16" (PLuc_giamthue_NQ43) of a 3.1.0 case: one row per ticked bảng kê row, in order
    (daySangPLGiamThue_PL01_1/2 -> CopyTableToTable5): ct08 MST, ct09_ma the nhóm (01-2: 07), ct10 the unreduced TNCN (01-1
    AD = H x K, 01-2 AB), ct11 = ct10 x 0,3 (giam_thue J45 = I45*0.3); totals ct12 / ct13. None without ticked rows."""
    sheet, table = TCKT_ROWS[case_id]
    D = decimal.Decimal
    rows = []
    for row in table:
        if len(row) != 5 or not row[4]:
            continue
        if sheet == '01-1':
            mst, code, _, taxable = row[:4]
            base = D(taxable) * D(TCKT_RATES[code])
        else:
            mst, revenue, deducted, exempt = row[:4]
            code, base = '07', D(0) if exempt else _round((D(revenue) - D(deducted)) * 5 / 100)
        cut = base * D('0.3')
        if base != base.to_integral_value() or cut != cut.to_integral_value():
            reject('VALUE')
        rows.append({'ct08': mst, 'ct09_ma': code, 'ct10': str(int(base)), 'ct11': str(int(cut))})
    if not rows:
        return None
    return 'PLuc_giamthue_NQ43', 'CTietGiamThue', rows, {'ct12': str(sum(int(r['ct10']) for r in rows)), 'ct13': str(sum(int(r['ct11']) for r in rows))}


def _tckt(case_id, root):
    reduction = tckt_reduction_expected(case_id)
    if (reduction is None) != (root.find(_xpath('HSoKhaiThue/PLuc/PLuc_giamthue_NQ43')) is None):
        reject('VALUE')
    for element, table, rows, totals in [tckt_expected(case_id)] + ([reduction] if reduction else []):
        annex = root.find(_xpath('HSoKhaiThue/PLuc/' + element))
        found = root.findall(_xpath('HSoKhaiThue/PLuc/%s/%s' % (element, table)))
        if annex is None or len(found) != len(rows):
            reject('VALUE')
        for node, row in zip(found, rows):
            for name, value in row.items():
                if [(n.text or '') for n in node.findall('{%s}%s' % (NS, name))] != [value]:
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
        if case_id in TTS_ROWS:
            _tts(case_id, root)
        if case_id in GTGT04_ROWS:
            _gtgt04(case_id, root)
        if case_id in TCKT_ROWS:
            _tckt(case_id, root)
        if case_id in GTGT01_TT89_INPUTS:
            _gtgt01_tt89(case_id, root)
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
