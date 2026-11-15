"""Input contract of the kê khai bổ sung (KHBS) cases of 01/NTNN TT80 (menu I9) and 01/NTNN, NCCNN TT89 (menu Y8).

The htkk_web producer scripts/generate-htkk-web-ntnn-khbs-reference.mjs (docs/KE-KHAI-BO-SUNG-01-NTNN.md there) stages per
case: declaration-original.xml (the lần đầu C0 HTKK must import and save first), declaration-prior.xml (bổ sung lần N-1,
lần 2 only, imported, summarised and saved before lần N) and declaration-web.xml (the bổ sung to import, summarise with
"Tổng hợp KHBS", export and compare), plus manifest.json. Every file is synthetic and was reviewed byte for byte: the
contract pins each file's size and SHA-256, so any other value is refused before it can reach a Windows runner. The
structural checks below repeat what the pins already imply in a form that fails with a bounded code (namespace, no comment,
web service identity, synthetic NNT/signer, declaration identity, loaiTKhai/soLan of each file).

NOT REGISTERED YET: the Windows driver mode these cases need (KHBS-NATIVE-CASE.md, section "01/NTNN") does not exist, so
htkk-native-cases.json carries no such case and nothing dispatches them. This module is the reviewed input half.
No value, path or text of a file is ever reported; errors are bounded codes."""
import hashlib
import io
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
CASES = {
    '01NTNN-khbs-grossup-lan1-M09-2026': {'producerCase': 'ntnn01-khbs-grossup-lan1-m09-2026', 'menuId': 'I9', 'soLan': 1, 'web': (7582, '412889221ab533e07874e40de04c1fc8789568eeddf6d8184d9429c739bc0e6a'), 'original': (2256, '98ff814c3aa9d0449b3fd5d9f6c69877d9f0a3433916003bb45034d8d7fb6ff4'), 'prior': None,
        'leafTarget': 216, 'expected': {'rows': ['(5)', '(7)', '(9)', '(10)', '(13)', '(14)'], 'subitems': [['1701', '540166'], ['1052', '540166']], 'ct10': '1080332', 'ct3a_1': '2026-11-13', 'ct3a_2': '24', 'ct3b': '0'}},
    '01NTNN-khbs-lan2-M09-2026': {'producerCase': 'ntnn01-khbs-lan2-m09-2026', 'menuId': 'I9', 'soLan': 2, 'web': (6135, '4a9895019abed4cba91715765dffe258c58462892652303328bafe4e6bcc8a6a'), 'original': (2256, '98ff814c3aa9d0449b3fd5d9f6c69877d9f0a3433916003bb45034d8d7fb6ff4'), 'prior': (7582, '412889221ab533e07874e40de04c1fc8789568eeddf6d8184d9429c739bc0e6a'),
        'leafTarget': 174, 'expected': {'rows': ['(10)', '(13)', '(14)'], 'subitems': [['1052', '459834']], 'ct10': '459834', 'ct3a_1': '2026-11-13', 'ct3a_2': '24', 'ct3b': '3311'}},
    '01NTNN-khbs-decrease-M09-2026': {'producerCase': 'ntnn01-khbs-decrease-m09-2026', 'menuId': 'I9', 'soLan': 1, 'web': (6173, 'db4660ab21a6d56084e17aba8b9599584ba820d8851e4f5c456f8bf96635588e'), 'original': (2256, '98ff814c3aa9d0449b3fd5d9f6c69877d9f0a3433916003bb45034d8d7fb6ff4'), 'prior': None,
        'leafTarget': 174, 'expected': {'rows': ['(12)', '(13)', '(14)'], 'subitems': [['1052', '-1000000']], 'ct10': '-1000000', 'ct3a_1': '2026-11-13', 'ct3a_2': '24', 'ct3b': '-7200'}},
    '01NTNN-NCCNN-khbs-part1-M10-2026': {'producerCase': 'ntnn01-nccnn-khbs-part1-m10-2026', 'menuId': 'Y8', 'soLan': 1, 'web': (9307, '349aec81f924153b9c0a4d57bca8f026d57e5698504083e0a22f9c1a5a9e412d'), 'original': (3742, '84942b95573d8c64dc60c9c765674765ec253b340716320a3fb0908ff688dd03'), 'prior': None,
        'leafTarget': 265, 'expected': {'rows': ['(5)', '(7)', '(9)', '(10)', '(13)', '(14)'], 'subitems': [['1701', '1000000'], ['1052', '1000000']], 'ct10': '2000000', 'ct3a_1': '2026-11-13', 'ct3a_2': '0', 'ct3b': '0'}},
    '01NTNN-NCCNN-khbs-part2-M10-2026': {'producerCase': 'ntnn01-nccnn-khbs-part2-m10-2026', 'menuId': 'Y8', 'soLan': 1, 'web': (8748, 'b289ac26290d25dd376ee1951d0ae4cc8496bef481d12f66b681cf50f304f5e6'), 'original': (3940, 'c12296c09bd11817f5dfa2e07ba76d1c530034a4d909ae3bccbaea0d0ec97ff0'), 'prior': None,
        'leafTarget': 249, 'expected': {'rows': ['(7)', '(9)', '(10)', '(13)', '(14)'], 'subitems': [['1052', '4000000']], 'ct10': '4000000', 'ct3a_1': '2026-11-13', 'ct3a_2': '0', 'ct3b': '0'}},
}


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
            'caseId': case_id, 'menuId': spec['menuId'], 'htkkVersion': '5.8.2', 'exporter': EXPORTER, 'producer': PRODUCER,
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
    expected = ('C', '0') if role == 'original' else ('B', str(spec['soLan'] - (1 if role == 'prior' else 0)))
    if (_leaf(root, tk + 'loaiTKhai'), _leaf(root, tk + 'soLan')) != expected:
        reject('AMENDMENT')
    pluc = [child for child in root.find('{%s}HSoKhaiThue' % NS) if _local(child) == 'PLuc']
    parts = [_local(child) for item in pluc for child in item]
    if parts != ([] if role == 'original' else ['PL01_KHBS', 'PL01_1_KHBS']):
        reject('AMENDMENT')
    for part in ([] if role == 'original' else ['PL01_KHBS', 'PL01_1_KHBS']):
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
