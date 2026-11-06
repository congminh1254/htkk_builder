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
import datetime, importlib.util, io, pathlib, re
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
VALUE_SHAPES = frozenset(('empty', 'whitespace-variant', 'case-variant', 'bool-titlecase', 'grouped-number', 'date-like', 'numeric-other', 'text-other'))


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
    return 'text-other'


def _where(items, path, value=None, allowed=()):
    """Context for the first leaf at ``path`` (ordinal is 1-based; 0 if absent)."""
    ordinal = next((i + 1 for i, (p, _) in enumerate(items) if p == path), 0)
    section = next((bit for name, bit in SECTIONS.items() if '/' + name + '/' in path + '/'), 32)
    context = {'leafOrdinal': ordinal, 'section': section}
    if value is not None:
        context['valueShape'] = value_shape(value, allowed)
    return context


# The exact synthetic profile the Windows harness saves (HtkkGuiReferenceAutomation.cs).
MST = '9999999997'
NAME = 'NNT KIEM THU GIA LAP - KHONG NOP'
ADDRESS = 'DU LIEU GIA LAP KIEM THU KHONG SU DUNG'
SIGNER = 'NGUOI KY GIA LAP'
# Texts the original profile/period dialog may legitimately add on a native re-export.
PROFILE_TEXTS = frozenset((NAME, ADDRESS, SIGNER, 'Thành phố Hà Nội', 'Phường Sơn Tây', 'Thuế Thành phố Hà Nội', 'Thuế cơ sở 16 Thành phố Hà Nội'))
NATIVE_SERVICE = ('HTKK', 'HỖ TRỢ KÊ KHAI THUẾ', '5.8.1')
COMMENT = '<!-- BẢN NHÁP; KHÔNG NỘP THUẾ; CHƯA KIỂM CHỨNG VỚI HTKK WINDOWS. -->'
PREAMBLE = '<?xml version="1.0" encoding="UTF-8"?>\n' + COMMENT + '\n'
SERVICE_PATH = 'HSoThueDTu/HSoKhaiThue/TTinChung/TTinDVu/'
SERVICE_NAMES = ('maDVu', 'tenDVu', 'pbanDVu', 'ttinNhaCCapDVu')
CREATION_PATH = 'HSoThueDTu/HSoKhaiThue/TTinChung/TTinTKhaiThue/TKhaiThue/ngayLapTKhai'
TK = 'HSoThueDTu/HSoKhaiThue/TTinChung/TTinTKhaiThue/TKhaiThue/'
NNT = 'HSoThueDTu/HSoKhaiThue/TTinChung/TTinTKhaiThue/NNT/'
NUMBER = re.compile(r'-?(0|[1-9][0-9]{0,17})(\.[0-9]{1,6})?\Z')
DATE = re.compile(r'([0-9]{2}/[0-9]{2}/[0-9]{4}|[0-9]{4}-[0-9]{2}-[0-9]{2}|[0-9]{1,2}/[0-9]{4}|[0-9]{2}/[0-9]{2})\Z')
CODE = re.compile(r'[0-9]{1,18}\Z')
TEMPLATE_TT80 = '(Ban hành kèm theo Thông tư số 80/2021/TT-BTC ngày 29 tháng 9 năm 2021 của Bộ trưởng Bộ Tài chính)'
WEB_TOOL = 'hotrokekhai.net — Công cụ Kê khai, công cụ độc lập'
MISMATCH_ORDINALS = 8
SECTIONS = {'TTinDVu': 1, 'TKhaiThue': 2, 'NNT': 4, 'CTieuTKhaiChinh': 8, 'PLuc': 16}


def _case(producer, menu, ma, version, schema, period, dates, sign, created, leaves, annexes, service, texts):
    kieu, ky, tu, den = period
    return {'producerCase': producer, 'menuId': menu, 'maTKhai': ma, 'xmlVersion': version, 'schemaId': schema,
            'kieuKy': kieu, 'kyKKhai': ky, 'tuNgay': tu, 'denNgay': den, 'ngayKy': sign, 'createdDate': created,
            'leafCount': leaves, 'annexElements': tuple(annexes), 'webService': ('CCKK-DRAFT', service, '0.9.2', WEB_TOOL),
            'texts': frozenset(texts) | {'C', kieu, version, NAME, SIGNER, 'CCKK-DRAFT', service, '0.9.2', WEB_TOOL}, 'dates': dates}


WORKBOOK_SERVICE = 'Công cụ Kê khai — bản nháp'
CASES = {
    '03TNDN-profit20-Y2025': _case('tndn03-profit20-y2025', 'N8', '892', '2.9.4', 'Validate/03_TNDN_TT80_294.xsd', ('Y', '2025', '01/01/2025', '31/12/2025'), None, '2026-03-20', '2026-03-20', 147, ['PLuc_03_1A_TNDN'], WORKBOOK_SERVICE,
                                   # Period default settlement case (AutoBindData_0) and the reviewed industry code (Header B25/B26).
                                   ['TỜ KHAI QUYẾT TOÁN THUẾ THU NHẬP DOANH NGHIỆP (Mẫu số 03/TNDN)', TEMPLATE_TT80, '+ Thu nhập tính thuế áp dụng thuế suất 20%', 'QT định kỳ', 'C10', 'C10 - Sản xuất, chế biến thực phẩm']),
    'BCTC133-B01a-basic-Y2025': _case('bctc133-basic-y2025', 'A2', '683', '2.3.2', 'Validate/133_B01A_DNN_BCTC_232.xsd', ('Y', '2025', '01/01/2025', '31/12/2025'), None, '2026-03-20', '2026-03-20', 975, ['PL_KQHDSXKD', 'PL_CDTK'], WORKBOOK_SERVICE,
                                      ['Bộ báo cáo tài chính (B01a - DNN)(TT133/2016/TT-BTC)', '(Ban hành theo Thông tư số 133/2016/TT-BTC ngày 26/8/2016 của Bộ Tài chính)']),
    'BCTC200-LT-basic-Y2025': _case('bctc200-lt-basic-y2025', '78', '402', '2.2.6', 'Validate/200_01_CDKT_226.xsd', ('Y', '2025', '01/01/2025', '31/12/2025'), None, '2026-03-20', '2026-03-20', 570, ['PL_KQHDSXKD', 'PL_LCTTGT'], WORKBOOK_SERVICE,
                                    ['Báo cáo tài chính (TT200/2014/TT-BTC)', '(Ban hành theo Thông tư số 200/2014/TT-BTC Ngày 22/12/2014 của Bộ Tài chính)', 'Người lập giả lập', 'Kế toán giả lập']),
    '05KK-withheld-Q3-2026': _case('tncn05kk-withheld-q3-2026', 'L7', '864', '2.9.3', 'Validate/05_KK_TNCN_TT80_293.xsd', ('Q', '3/2026', '01/07/2026', '30/09/2026'), None, '2026-10-27', '2026-10-27', 56, [], WORKBOOK_SERVICE,
                                    ['TK khấu trừ thuế thu nhập cá nhân Mẫu 05/KK-TNCN (TT80/2021)', TEMPLATE_TT80, ADDRESS]),
    '05QTT-two-employees-Y2025': _case('tncn05qtt-two-employees-y2025', 'B9', '953', '2.9.3', 'Validate/05_QTT_TNCN_TT80_293.xsd', ('Y', '2025', '01/01/2025', '31/12/2025'), None, '2026-10-27', '2026-10-27', 149, ['PLuc_05_1_BK_QTT', 'PLuc_05_3_BK_QTT'], WORKBOOK_SERVICE,
                                       ['TỜ KHAI QUYẾT TOÁN THUẾ THU NHẬP CÁ NHÂN (Mẫu số 05/QTT-TNCN)', TEMPLATE_TT80, ADDRESS, 'NGUOI LAO DONG A', 'NGUOI LAO DONG B', 'NGUOI PHU THUOC A', 'Con', 'Thẻ CCCD/Số định danh cá nhân', 'QT định kỳ']),
    # B8 02/QTT-TNCN (non-gating): the descriptor design case with two dependants (annex 02-1).
    '02QTT-dependants-Y2025': _case('tncn02qtt-dependants-y2025', 'B8', '952', '2.7.3', 'Validate/02_QTT_TNCN_TT80_273.xsd', ('Y', '2025', '01/01/2025', '31/12/2025'), None, '2026-10-27', '2026-10-27', 130, ['PLuc_02_1_BK_QTT_TNCN'], WORKBOOK_SERVICE,
                                    ['TỜ KHAI QUYẾT TOÁN THUẾ THU NHẬP CÁ NHÂN (Mẫu 02/QTT-TNCN)', TEMPLATE_TT80, ADDRESS, 'Quyết toán theo năm dương lịch', 'NGUOI PHU THUOC A', 'NGUOI PHU THUOC B',
                                     'Thẻ CCCD', 'Giấy khai sinh', 'GKS-0001', 'Con']),
    '01CNKD-TT50-revenue-two-groups-Q3-2026': _case('cnkd01-revenue-two-groups-q3-2026', 'U5', '1266', '2.9.8', 'Validate/01_CNKD_HKD_TT50_298.xsd', ('Q', '3/2026', '01/07/2026', '30/09/2026'), None, '2026-10-27', '2026-10-27', 261, [], 'Công cụ Kê khai — bản nháp',
                                                    ['TỜ KHAI THUẾ ĐỐI VỚI HỘ KINH DOANH, CÁ NHÂN KINH DOANH', '(Kèm theo Thông tư số 50/2026/TT-BTC ngày 05/3/2026 của Bộ trưởng Bộ Tài chính)', '(a)', '(b)', 'CUA HANG GIA LAP', 'DIA CHI GIA LAP', ADDRESS,
                                                     'Phân phối, cung cấp hàng hóa', 'Dịch vụ, xây dựng không bao thầu  nguyên vật liệu', 'Phường Sơn Tây', 'Thành phố Hà Nội', 'Thuế cơ sở 16 Thành phố Hà Nội',
                                                     '10129 - Thuế cơ sở 16 Thành phố Hà Nội', '1140759 - Phường Sơn Tây - Thuế cơ sở 16 Thành phố Hà Nội',
                                                     'Thuế giá trị gia tăng hàng sản xuất, kinh doanh trong nước (gồm cả dịch vụ trong lĩnh vực dầu khí)', 'Thuế thu nhập từ hoạt động sản xuất, kinh doanh của cá nhân']),
}
_workbook_expected = {c['caseId']: c['expected'] for c in workbook_design.PLAN['cases']}
_descriptor_expected = {c['caseId']: (c['expectedLeaves'], c.get('expectedRows', {})) for c in descriptor_design.DESIGN['cases']}
# Leaves the ORIGINAL export fills with the export day (HtkkDeclarationCasePlans.ExportDatePaths):
# A2 has no control bound to TKhaiThue/ngayKy, so TTinChung.ngayKy keeps DateTime.Now.
EXPORT_DATES = {'BCTC133-B01a-basic-Y2025': (TK + 'ngayKy',)}
for _id, _c in CASES.items():
    _c['exportDates'] = EXPORT_DATES.get(_id, ())
    _c['family'] = 'cnkd' if _id in hkd_design.CASES else 'descriptor' if _id in _descriptor_expected else 'workbook'
    if _c['family'] == 'workbook' and _id not in _workbook_expected:
        raise ValueError('DECLARATION_CASE_POLICY')


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
        # Workbook/CNKD exporters emit exactly this disclaimer before the root; the
        # descriptor exporter emits none. No other comment is accepted anywhere.
        if text.startswith(PREAMBLE) and text.count(COMMENT) == 1:
            text = text.replace(COMMENT, '', 1)
        elif not text.startswith('<?xml version="1.0" encoding="UTF-8"?>\n<HSoThueDTu ') or COMMENT in text:
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
            if not ((key == 'id' and re.fullmatch(r'ID_[1-9][0-9]{0,3}', value)) or (key == '{' + XSI + '}nil' and value == 'true' and len(node) == 0 and not (node.text or ''))):
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


def _texts(items, allowed):
    for path, value in items:
        if value == '' or NUMBER.match(value) or CODE.match(value) or DATE.match(value) or value in ('true', 'false'):
            continue
        if value not in allowed:
            reject('PRIVACY', _where(items, path, value, allowed))


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
            found = [(n.text or '') for n in main.iter('{%s}%s' % (NS, name))]
            if found != [value]:
                reject('VALUE')
        for key, count in rows.items():
            annex, row = key.split('/')
            if len(root.findall('./{%s}HSoKhaiThue/{%s}PLuc/{%s}%s/{%s}%s' % (NS, NS, NS, annex, NS, row))) != count:
                reject('VALUE')
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
    _texts(items, spec['texts'] | PROFILE_TEXTS)
    raw = bytes(body).decode('utf-8').replace(COMMENT, '', 1).encode('utf-8')  # disclaimer only
    _expected(case_id, spec, root, items, raw)
    if manifest is not None and manifest.get('leafCount') != spec['leafCount']:
        reject('MANIFEST')
    return {'privacyValuesVerified': True, 'leafCount': len(items), 'serviceIdentity': 'web-draft', 'nativeProvenance': False}


def validate_native_output(body, case_id, today=None):
    """Native re-export: original service identity, fresh creation date, synthetic data only."""
    spec = case(case_id)
    root = _parse(body, False)
    items = leaves(root)
    service = tuple(_one(items, SERVICE_PATH + name) for name in SERVICE_NAMES)
    if service[:3] != NATIVE_SERVICE or not re.fullmatch(r'[0-9A-F]{32}', service[3]):
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
    _texts(items, spec['texts'] | PROFILE_TEXTS | set(service))
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
