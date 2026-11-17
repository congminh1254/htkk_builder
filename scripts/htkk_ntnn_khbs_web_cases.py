"""Input contract of the kê khai bổ sung (KHBS) cases of 01/NTNN TT80 (menu I9) and 01/NTNN, NCCNN TT89 (menu Y8).

The htkk_web producer scripts/generate-htkk-web-ntnn-khbs-reference.mjs (docs/KE-KHAI-BO-SUNG-01-NTNN.md there) stages per
case: declaration-original.xml (the lần đầu C0 HTKK must import and save first), declaration-prior.xml (bổ sung lần N-1,
lần 2 only, imported, summarised and saved before lần N) and declaration-web.xml (the bổ sung to import, summarise with
"Tổng hợp KHBS", export and compare), plus manifest.json. Every file is synthetic and was reviewed byte for byte: the
contract pins each file's size and SHA-256, so any other value is refused before it can reach a Windows runner. The
structural checks below repeat what the pins already imply in a form that fails with a bounded code (namespace, no comment,
web service identity, synthetic NNT/signer, declaration identity, loaiTKhai/soLan of each file).

This repository is public, so the reviewed files never enter it: only their pins do (tests pin synthetic in-memory files of their
own, ntnn_khbs_test_support.py). Registered cases of driver mode declaration-amendment-khbs-inspect (HtkkDeclarationKhbs.cs),
non-gating, HTKK 5.8.2; the native B export is checked against the staged files themselves (validate_native_output).
No value, path or text of a file is ever reported; errors are bounded codes.

The same driver mode runs the 05/KK-TNCN KHBS cases (L7, Z8): their pins and per-case settings (producer, exporter, PLuc parts
before the KHBS fragments, input mode) live in htkk_kk05_khbs_web_cases.py and are merged into CASES, MENUS and PERIODS here,
so every reader of this contract (fetch, publishers, probe lists) covers them with the same checks. The 01/CNKD KHBS cases (U5)
are merged the same way from htkk_cnkd_khbs_web_cases.py; their B files carry no KHBS fragment (per-case khbsParts empty: U5 has
KieuKHBS "" in HTKK 5.8.2, so its bổ sung is the declaration itself with loaiTKhai B). The 02/QTT-TNCN KHBS cases (B8, KieuKHBS
3, 02-1/BK-QTT-TNCN before the two fragments) are merged the same way from htkk_qtt02_khbs_web_cases.py, the 05/QTT-TNCN ones
(B9, 05-1 and 05-3 before the fragments) from htkk_qtt05_khbs_web_cases.py, and the 03/TNDN KHBS
cases (N8, KieuKHBS 3, 03-1A/TNDN before the two fragments) from htkk_tndn03_khbs_web_cases.py, and the 03/NTNN KHBS cases (J1,
KieuKHBS 3 like I9, no annex; every import completed by the rates typed again) from htkk_ntnn03_khbs_web_cases.py."""
import hashlib
import importlib.util
import io
import pathlib
import re
import xml.etree.ElementTree as ET

NS = 'http://kekhaithue.gdt.gov.vn/TKhaiThue'
XSI = 'http://www.w3.org/2001/XMLSchema-instance'
WEB_NAME, ORIGINAL_NAME, PRIOR_NAME, MANIFEST_NAME = 'declaration-web.xml', 'declaration-original.xml', 'declaration-prior.xml', 'manifest.json'
PRODUCER = 'scripts/generate-htkk-web-ntnn-khbs-reference.mjs'
EXPORTER = 'lib/htkk-ntnn01-khbs.ts'
PREAMBLE = '<?xml version="1.0" encoding="UTF-8"?>\n<HSoThueDTu '
MAX_XML = 262144
FIXED_DATE = '2026-11-13'
SERVICE = ('CCKK', 'Công cụ Kê khai', '0.9.2', 'hotrokekhai.net — Công cụ Kê khai, công cụ độc lập')
MST, NAME, SIGNER = '9999999997', 'NNT KIEM THU GIA LAP - KHONG NOP', 'NGUOI KY GIA LAP'
MENUS = {'I9': ('838', '2.5.1'), 'Y8': ('2012', '3.0.9')}
CODES = frozenset(('CASE', 'NAMES', 'MANIFEST', 'SIZE', 'HASH', 'ENCODING', 'DECLARATION', 'PARSE', 'NAMESPACE', 'SERVICE', 'IDENTITY', 'AMENDMENT'))
# kieuKy, kyKKhai, kyKKhaiTuNgay, kyKKhaiDenNgay of every file of a menu's cases.
PERIODS = {'I9': ('M', '09/2026', '01/09/2026', '30/09/2026'), 'Y8': ('M', '10/2026', '01/10/2026', '31/10/2026')}
CASES = {
    '01NTNN-khbs-grossup-lan1-M09-2026': {'producerCase': 'ntnn01-khbs-grossup-lan1-m09-2026', 'menuId': 'I9', 'soLan': 1, 'web': (7585, 'd91fa8e927d1fe263b3cdaeab60c75ea776c9f46d42bd4baf2fbed2be547b6b6'), 'original': (2256, '98ff814c3aa9d0449b3fd5d9f6c69877d9f0a3433916003bb45034d8d7fb6ff4'), 'prior': None,
        'leafTarget': 216, 'expected': {'rows': ['(5)', '(7)', '(9)', '(10)', '(13)', '(14)'], 'subitems': [['1701', '540166'], ['1052', '540166']], 'ct10': '1080332', 'ct3a_1': '2026-11-13', 'ct3a_2': '24', 'ct3b': '7778'}},
    '01NTNN-khbs-lan2-M09-2026': {'producerCase': 'ntnn01-khbs-lan2-m09-2026', 'menuId': 'I9', 'soLan': 2, 'web': (6135, '4a9895019abed4cba91715765dffe258c58462892652303328bafe4e6bcc8a6a'), 'original': (2256, '98ff814c3aa9d0449b3fd5d9f6c69877d9f0a3433916003bb45034d8d7fb6ff4'), 'prior': (7585, 'd91fa8e927d1fe263b3cdaeab60c75ea776c9f46d42bd4baf2fbed2be547b6b6'),
        'leafTarget': 174, 'expected': {'rows': ['(10)', '(13)', '(14)'], 'subitems': [['1052', '459834']], 'ct10': '459834', 'ct3a_1': '2026-11-13', 'ct3a_2': '24', 'ct3b': '3311'}},
    '01NTNN-khbs-decrease-M09-2026': {'producerCase': 'ntnn01-khbs-decrease-m09-2026', 'menuId': 'I9', 'soLan': 1, 'web': (6173, 'db4660ab21a6d56084e17aba8b9599584ba820d8851e4f5c456f8bf96635588e'), 'original': (2256, '98ff814c3aa9d0449b3fd5d9f6c69877d9f0a3433916003bb45034d8d7fb6ff4'), 'prior': None,
        'leafTarget': 174, 'expected': {'rows': ['(12)', '(13)', '(14)'], 'subitems': [['1052', '-1000000']], 'ct10': '-1000000', 'ct3a_1': '2026-11-13', 'ct3a_2': '24', 'ct3b': '-7200'}},
    '01NTNN-NCCNN-khbs-part1-M10-2026': {'producerCase': 'ntnn01-nccnn-khbs-part1-m10-2026', 'menuId': 'Y8', 'soLan': 1, 'web': (9307, '349aec81f924153b9c0a4d57bca8f026d57e5698504083e0a22f9c1a5a9e412d'), 'original': (3742, '84942b95573d8c64dc60c9c765674765ec253b340716320a3fb0908ff688dd03'), 'prior': None,
        'leafTarget': 265, 'expected': {'rows': ['(5)', '(7)', '(9)', '(10)', '(13)', '(14)'], 'subitems': [['1701', '1000000'], ['1052', '1000000']], 'ct10': '2000000', 'ct3a_1': '2026-11-13', 'ct3a_2': '0', 'ct3b': '0'}},
    '01NTNN-NCCNN-khbs-part2-M10-2026': {'producerCase': 'ntnn01-nccnn-khbs-part2-m10-2026', 'menuId': 'Y8', 'soLan': 1, 'web': (8748, 'b289ac26290d25dd376ee1951d0ae4cc8496bef481d12f66b681cf50f304f5e6'), 'original': (3940, 'c12296c09bd11817f5dfa2e07ba76d1c530034a4d909ae3bccbaea0d0ec97ff0'), 'prior': None,
        'leafTarget': 249, 'expected': {'rows': ['(7)', '(9)', '(10)', '(13)', '(14)'], 'subitems': [['1052', '4000000']], 'ct10': '4000000', 'ct3a_1': '2026-11-13', 'ct3a_2': '0', 'ct3b': '0'}},
    '01NTNN-NCCNN-khbs-lan2-M10-2026': {'producerCase': 'ntnn01-nccnn-khbs-lan2-m10-2026', 'menuId': 'Y8', 'soLan': 2, 'web': (7918, '0b55fe92318e50f6918a404436e903382847d871c1ba09147ae795b152e4e130'), 'original': (3742, '84942b95573d8c64dc60c9c765674765ec253b340716320a3fb0908ff688dd03'), 'prior': (9307, '349aec81f924153b9c0a4d57bca8f026d57e5698504083e0a22f9c1a5a9e412d'),
        'leafTarget': 223, 'expected': {'rows': ['(10)', '(13)', '(14)'], 'subitems': [['1052', '1000000']], 'ct10': '1000000', 'ct3a_1': '2026-11-13', 'ct3a_2': '0', 'ct3b': '0'}},
}
for _spec in CASES.values():
    _spec.setdefault('annexParts', ())
    _spec.setdefault('inputMode', 'khbs-original-entry-export' if _spec['menuId'] == 'Y8' else 'khbs-web-xml-import-reexport')
    _spec['producer'], _spec['exporter'] = PRODUCER, EXPORTER
NTNN_CASES = tuple(CASES)
_kk05_spec = importlib.util.spec_from_file_location('htkk_kk05_khbs_web_cases_data', pathlib.Path(__file__).with_name('htkk_kk05_khbs_web_cases.py'))
kk05 = importlib.util.module_from_spec(_kk05_spec)
_kk05_spec.loader.exec_module(kk05)
if set(kk05.CASES) & set(CASES) or set(kk05.MENUS) & set(MENUS):
    raise ValueError('CASE_POLICY')
CASES.update(kk05.CASES)
MENUS.update(kk05.MENUS)
PERIODS.update(kk05.PERIODS)
KK05_CASES = tuple(kk05.CASES)
_cnkd_spec = importlib.util.spec_from_file_location('htkk_cnkd_khbs_web_cases_data', pathlib.Path(__file__).with_name('htkk_cnkd_khbs_web_cases.py'))
cnkd = importlib.util.module_from_spec(_cnkd_spec)
_cnkd_spec.loader.exec_module(cnkd)
if set(cnkd.CASES) & set(CASES) or set(cnkd.MENUS) & set(MENUS):
    raise ValueError('CASE_POLICY')
CASES.update(cnkd.CASES)
MENUS.update(cnkd.MENUS)
PERIODS.update(cnkd.PERIODS)
CNKD_CASES = tuple(cnkd.CASES)
_qtt02_spec = importlib.util.spec_from_file_location('htkk_qtt02_khbs_web_cases_data', pathlib.Path(__file__).with_name('htkk_qtt02_khbs_web_cases.py'))
qtt02 = importlib.util.module_from_spec(_qtt02_spec)
_qtt02_spec.loader.exec_module(qtt02)
if set(qtt02.CASES) & set(CASES) or set(qtt02.MENUS) & set(MENUS):
    raise ValueError('CASE_POLICY')
CASES.update(qtt02.CASES)
MENUS.update(qtt02.MENUS)
PERIODS.update(qtt02.PERIODS)
QTT02_CASES = tuple(qtt02.CASES)
_qtt05_spec = importlib.util.spec_from_file_location('htkk_qtt05_khbs_web_cases_data', pathlib.Path(__file__).with_name('htkk_qtt05_khbs_web_cases.py'))
qtt05 = importlib.util.module_from_spec(_qtt05_spec)
_qtt05_spec.loader.exec_module(qtt05)
if set(qtt05.CASES) & set(CASES) or set(qtt05.MENUS) & set(MENUS):
    raise ValueError('CASE_POLICY')
CASES.update(qtt05.CASES)
MENUS.update(qtt05.MENUS)
PERIODS.update(qtt05.PERIODS)
QTT05_CASES = tuple(qtt05.CASES)
_tndn03_spec = importlib.util.spec_from_file_location('htkk_tndn03_khbs_web_cases_data', pathlib.Path(__file__).with_name('htkk_tndn03_khbs_web_cases.py'))
tndn03 = importlib.util.module_from_spec(_tndn03_spec)
_tndn03_spec.loader.exec_module(tndn03)
if set(tndn03.CASES) & set(CASES) or set(tndn03.MENUS) & set(MENUS):
    raise ValueError('CASE_POLICY')
CASES.update(tndn03.CASES)
MENUS.update(tndn03.MENUS)
PERIODS.update(tndn03.PERIODS)
TNDN03_CASES = tuple(tndn03.CASES)
_ntnn03_spec = importlib.util.spec_from_file_location('htkk_ntnn03_khbs_web_cases_data', pathlib.Path(__file__).with_name('htkk_ntnn03_khbs_web_cases.py'))
ntnn03 = importlib.util.module_from_spec(_ntnn03_spec)
_ntnn03_spec.loader.exec_module(ntnn03)
if set(ntnn03.CASES) & set(CASES) or set(ntnn03.MENUS) & set(MENUS):
    raise ValueError('CASE_POLICY')
CASES.update(ntnn03.CASES)
MENUS.update(ntnn03.MENUS)
PERIODS.update(ntnn03.PERIODS)
NTNN03_CASES = tuple(ntnn03.CASES)
KHBS_FRAGMENTS = ('PL01_KHBS', 'PL01_1_KHBS')
for _spec in CASES.values():
    _spec.setdefault('khbsParts', KHBS_FRAGMENTS)


class NtnnKhbsWebCaseError(ValueError):
    def __init__(self, code):
        if code not in CODES:
            raise ValueError('Invalid bounded code')
        self.code = code
        super().__init__(code)


def reject(code):
    raise NtnnKhbsWebCaseError(code)


def is_case(case_id):
    return case_id in CASES


def case(case_id):
    if case_id not in CASES:
        reject('CASE')
    return CASES[case_id]


def names(case_id):
    """Exactly the staged names of a case, in import order (lần đầu, previous bổ sung, this bổ sung)."""
    spec = case(case_id)
    return (ORIGINAL_NAME,) + ((PRIOR_NAME,) if spec['prior'] else ()) + (WEB_NAME, MANIFEST_NAME)


def manifest_fields(case_id):
    """The fixed manifest values of the producer (manifestFor); sourceCommit, producerSha256 and the sizes/hashes vary."""
    spec = case(case_id)
    return {'format': 'htkk-web-' + spec['producerCase'] + '-input-v1', 'sourceRepository': 'htkk-net/htkk_web', 'sourceVersion': '0.9.2',
            'caseId': case_id, 'menuId': spec['menuId'], 'htkkVersion': '5.8.2', 'exporter': spec['exporter'], 'producer': spec['producer'],
            'soLan': spec['soLan'], 'ngayLapKHBS': FIXED_DATE, 'expected': spec['expected'], 'inputsSynthetic': True, 'nativeAmendmentVerified': False}


def validate_manifest(manifest):
    if type(manifest) is not dict:
        reject('MANIFEST')
    spec = case(manifest.get('caseId'))
    fixed = manifest_fields(manifest['caseId'])
    variable = {'sourceCommit', 'producerSha256', 'bytes', 'xmlSha256', 'originalBytes', 'originalXmlSha256'} | ({'priorBytes', 'priorXmlSha256'} if spec['prior'] else set())
    if set(manifest) != set(fixed) | variable or any(type(manifest[k]) is not type(v) or manifest[k] != v for k, v in fixed.items()):
        reject('MANIFEST')
    if not (isinstance(manifest['sourceCommit'], str) and re.fullmatch('[0-9a-f]{40}', manifest['sourceCommit']) and isinstance(manifest['producerSha256'], str) and re.fullmatch('[0-9a-f]{64}', manifest['producerSha256'])):
        reject('MANIFEST')
    for prefix, key in (('', 'web'), ('original', 'original'), ('prior', 'prior')):
        if not spec[key]:
            continue
        size, digest = spec[key]
        size_key, sha_key = (prefix + 'Bytes', prefix + 'XmlSha256') if prefix else ('bytes', 'xmlSha256')
        if manifest[size_key] != size or manifest[sha_key] != digest:
            reject('HASH')
    return manifest


def _local(node):
    if not node.tag.startswith('{' + NS + '}'):
        reject('NAMESPACE')
    return node.tag[len(NS) + 2:]


def _leaf(root, path):
    node = root
    for name in path.split('/'):
        found = [child for child in node if _local(child) == name]
        if len(found) != 1:
            reject('DECLARATION')
        node = found[0]
    if len(node):
        reject('DECLARATION')
    return node.text or ''


def validate_xml(body, case_id, role):
    """One staged file of a case: its pinned bytes, then the bounded structural reading of them."""
    spec = case(case_id)
    if role not in ('web', 'original', 'prior') or not spec[role]:
        reject('NAMES')
    size, digest = spec[role]
    if not isinstance(body, bytes) or not 0 < len(body) <= MAX_XML or len(body) != size:
        reject('SIZE')
    if hashlib.sha256(body).hexdigest() != digest:
        reject('HASH')
    try:
        text = body.decode('utf-8')
    except UnicodeError:
        reject('ENCODING')
    if not text.startswith(PREAMBLE) or re.search(r'<!|<\?(?!xml\s)', text, re.I) or text.count('<?') != 1:
        reject('DECLARATION')
    try:
        for _event, (prefix, uri) in ET.iterparse(io.BytesIO(body), events=('start-ns',)):
            if (prefix, uri) not in (('', NS), ('xsi', XSI)):
                reject('NAMESPACE')
        root = ET.fromstring(text)
    except ET.ParseError:
        reject('PARSE')
    if _local(root) != 'HSoThueDTu':
        reject('NAMESPACE')
    info = 'HSoKhaiThue/TTinChung/'
    if tuple(_leaf(root, info + 'TTinDVu/' + name) for name in ('maDVu', 'tenDVu', 'pbanDVu', 'ttinNhaCCapDVu')) != SERVICE:
        reject('SERVICE')
    tk = info + 'TTinTKhaiThue/TKhaiThue/'
    if (_leaf(root, info + 'TTinTKhaiThue/NNT/mst'), _leaf(root, info + 'TTinTKhaiThue/NNT/tenNNT'), _leaf(root, tk + 'nguoiKy')) != (MST, NAME, SIGNER):
        reject('IDENTITY')
    if (_leaf(root, tk + 'maTKhai'), _leaf(root, tk + 'pbanTKhaiXML')) != MENUS[spec['menuId']] or _leaf(root, tk + 'ngayLapTKhai') != FIXED_DATE:
        reject('IDENTITY')
    if tuple(_leaf(root, tk + 'KyKKhaiThue/' + name) for name in ('kieuKy', 'kyKKhai', 'kyKKhaiTuNgay', 'kyKKhaiDenNgay')) != period_of(spec):
        reject('IDENTITY')
    expected = ('C', '0') if role == 'original' else ('B', str(spec['soLan'] - (1 if role == 'prior' else 0)))
    if (_leaf(root, tk + 'loaiTKhai'), _leaf(root, tk + 'soLan')) != expected:
        reject('AMENDMENT')
    pluc = [child for child in root.find('{%s}HSoKhaiThue' % NS) if _local(child) == 'PLuc']
    parts = [_local(child) for item in pluc for child in item]
    # The case's own annexes (05/KK-TNCN: 05-1/PBT-KK-TNCN; 01/CNKD: PL 01 NQ 43) precede the KHBS fragments of a B file (none for U5).
    # 05/QTT-TNCN: a B file carries every bảng kê of B9 (HTKK writes the missing ones as default sheets), the lần đầu only its own
    # (originalAnnexParts); every other case has the same annexes in all files.
    fragments = [] if role == 'original' else list(spec['khbsParts'])
    annexes = spec.get('originalAnnexParts', spec['annexParts']) if role == 'original' else spec['annexParts']
    if parts != list(annexes) + fragments:
        reject('AMENDMENT')
    for part in fragments:
        if _leaf(root, 'HSoKhaiThue/PLuc/' + part + '/Header/soLan') != expected[1] or _leaf(root, 'HSoKhaiThue/PLuc/' + part + '/Header/mst') != MST:
            reject('AMENDMENT')
    return {'privacyValuesVerified': True, 'serviceIdentity': 'web-tool', 'nativeProvenance': False}


def validate_files(files, manifest):
    """Every staged file of the case (exact name set), each against its pin and the structural reading."""
    validate_manifest(manifest)
    case_id = manifest['caseId']
    if type(files) is not dict or set(files) != set(names(case_id)) - {MANIFEST_NAME}:
        reject('NAMES')
    for name, role in ((ORIGINAL_NAME, 'original'), (PRIOR_NAME, 'prior'), (WEB_NAME, 'web')):
        if name in files:
            validate_xml(files[name], case_id, role)
    return {'privacyValuesVerified': True, 'serviceIdentity': 'web-tool', 'nativeProvenance': False, 'amendmentLeafTarget': case(case_id)['leafTarget']}


# ---- Native re-export (publish-htkk-declaration-native-output.py) ----
# The original B export of the last bổ sung round is read with the declaration contract's parser, leaf walk, privacy rule
# and whole-tree comparison (htkk_declaration_web_cases.py): its errors and bounded diagnostics are reused unchanged.
_declaration = None


def declaration():
    global _declaration
    if _declaration is None:
        import importlib.util
        spec = importlib.util.spec_from_file_location('ntnn_khbs_declaration_contract', pathlib.Path(__file__).with_name('htkk_declaration_web_cases.py'))
        _declaration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_declaration)
    return _declaration


def input_texts(files):
    """Every leaf text of the case's staged files (lần đầu, previous bổ sung, this bổ sung), already validated by the caller."""
    d = declaration()
    return frozenset(value for name in (ORIGINAL_NAME, PRIOR_NAME, WEB_NAME) if name in files for _, value in d.leaves(d._parse(files[name], True)))


def period_of(spec):
    """kieuKy, kyKKhai, kyKKhaiTuNgay, kyKKhaiDenNgay of a case's files: its own period when it has one (05/KK-TNCN kỳ tháng),
    else its menu's."""
    return spec.get('period') or PERIODS[spec['menuId']]


def producer(case_id):
    """The reviewed htkk_web producer of a case."""
    return case(case_id)['producer']


def khbs_summary(case_id):
    """Whether the bổ sung rounds run the original "Tổng hợp KHBS" (not for U5, whose KieuKHBS is empty)."""
    return bool(case(case_id)['khbsParts'])


def input_mode(case_id):
    """How the driver puts the case's files into HTKK: imported, imported then completed in the grid, or typed (Y8)."""
    return case(case_id)['inputMode']


def tax_leaf_count(case_id):
    """Compared leaves of the web B file excluding the four service-identity leaves (C# KhbsPlan leaf counts minus 4)."""
    return case(case_id)['leafTarget']


def validate_native_output(body, case_id, today=None, service_version=None, files=None):
    """Native B re-export: original service identity, fresh creation date, this case's identity, period and lần, synthetic NNT.
    With ``files`` (the case's staged files, each validated against its pin here) every text must also be a leaf text of those
    files, the synthetic profile or the service identity; the publisher checks that before anything is retained."""
    import datetime
    d, spec = declaration(), case(case_id)
    root = d._parse(body, False)
    items = d.leaves(root)
    service = tuple(d._one(items, d.SERVICE_PATH + name) for name in d.SERVICE_NAMES)
    if service[:3] != d.native_service(service_version) or not re.fullmatch(r'[0-9A-F]{32}', service[3]):
        d.reject('SERVICE')
    if files is not None:
        if type(files) is not dict or set(files) != set(names(case_id)) - {MANIFEST_NAME}:
            reject('NAMES')
        for name, role in ((ORIGINAL_NAME, 'original'), (PRIOR_NAME, 'prior'), (WEB_NAME, 'web')):
            if name in files:
                validate_xml(files[name], case_id, role)
    ma, version = MENUS[spec['menuId']]
    for name, expected in (('maTKhai', ma), ('pbanTKhaiXML', version), ('loaiTKhai', 'B'), ('soLan', str(spec['soLan']))):
        if d._one(items, d.TK + name) != expected:
            d.reject('IDENTITY', d._where(items, d.TK + name, d._one(items, d.TK + name)))
    for name, expected in zip(('kieuKy', 'kyKKhai', 'kyKKhaiTuNgay', 'kyKKhaiDenNgay'), period_of(spec)):
        path = d.TK + 'KyKKhaiThue/' + name
        if d._one(items, path) != expected:
            d.reject('PERIOD', d._where(items, path, d._one(items, path)))
    for path, expected in ((d.NNT + 'mst', MST), (d.NNT + 'tenNNT', NAME), (d.TK + 'nguoiKy', SIGNER)):
        if d._one(items, path) != expected:
            d.reject('PRIVACY', d._where(items, path, d._one(items, path), (expected,)))
    for path, value in items:
        if re.search(r'(^|/)(mst|mst_cu|mstDLyThue)$', path) and value not in ('', MST):
            d.reject('PRIVACY', d._where(items, path))
    created = d._one(items, d.CREATION_PATH)
    try:
        created_date = datetime.date.fromisoformat(created) if re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', created) else None
    except ValueError:
        created_date = None
    today = today or datetime.datetime.now(datetime.timezone.utc).date()
    if created_date is None or abs((today - created_date).days) > 1:
        d.reject('DATE')
    if files is None:
        return {'privacyValuesVerified': False, 'leafCount': len(items), 'nativeServiceIdentityVerified': True, 'creationDateRule': 'native-export-current-date'}
    allowed = input_texts(files) | d.PROFILE_TEXTS | set(service)
    d._texts(items, allowed | catalogue_texts(case_id, items, allowed))
    return {'privacyValuesVerified': True, 'leafCount': len(items), 'nativeServiceIdentityVerified': True, 'creationDateRule': 'native-export-current-date'}


KEY_PATH_SUFFIX = 'PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_2_ten'


def catalogue_texts(case_id, items, allowed):
    """Extra texts a case's native export may carry (02/QTT-TNCN, 03/TNDN and 03/NTNN only, ``catalogueTexts``): the public HTKK catalogue texts of the
    menu, and on the 01-1/KHBS row key leaf a ' - '-joined key whose every piece is empty, a text of the case's files or a bounded
    number/code/date shape. Every other case gets none."""
    spec = case(case_id)
    texts = spec.get('catalogueTexts')
    if not texts:
        return frozenset()
    d = declaration()
    shaped = lambda piece: piece == '' or piece in allowed or bool(d.NUMBER.match(piece) or d.CODE.match(piece) or d.DATE.match(piece))
    keys = {value for path, value in items if path.endswith(KEY_PATH_SUFFIX) and ' - ' in value and len(value) <= 512 and all(shaped(piece) for piece in value.split(' - '))}
    return frozenset(texts) | frozenset(keys)


def compare_tree(web_body, native_body, case_id):
    """Whole-tree comparison of the native B export with the case's web B file, checked against its pin first (declaration rule:
    creation date and the four service leaves normalised in memory; every other leaf, ngày lập KHBS and late days included, exact)."""
    validate_xml(web_body, case_id, 'web')
    return declaration().compare_tree(web_body, native_body, ())

