"""Candidate web->HTKK cases for descriptor-workbook declarations (03/TNDN N8, BCTC A2/78).

The file is a pinned copy of htkk_web data/htkk-workbook-native-cases.json. It is NOT part
of the dispatchable registry (htkk-native-cases.json): no workflow option, producer or
driver may read it until a reviewed Windows driver for these menus exists. This module only
validates the plan offline: synthetic identity, Menu.xml unit, bounded inputs and expected
leaves. It never executes application code and grants no coverage.
"""
import json, pathlib, re
ROOT = pathlib.Path(__file__).parent
PLAN_FILE = ROOT / 'htkk-workbook-native-cases.json'
# Reviewed Menu.xml HTKK 5.8.1 identities (MaToKhai / VersionXML / KieuKy) for each menu.
UNITS = {
    'N8': {'xmlVersion': '2.9.4', 'maTKhai': '892', 'kieuKy': '11', 'menuChain': ['101', '101_2', 'N8'],
           'appendices': {'03-1A', '03-1B', '03-1C', '03-2', '03-5'}, 'xsd': 'Validate/03_TNDN_TT80_294.xsd'},
    'A2': {'xmlVersion': '2.3.2', 'maTKhai': '683', 'kieuKy': '26', 'menuChain': ['101', '101_6', 'A2'],
           'appendices': {'01-1', '01-2', '01-3'}, 'xsd': 'Validate/133_B01A_DNN_BCTC_232.xsd'},
    '78': {'xmlVersion': '2.2.6', 'maTKhai': '402', 'kieuKy': '26', 'menuChain': ['101', '101_6', '78'],
           'appendices': {'01-1', '01-2', '01-3'}, 'xsd': 'Validate/200_01_CDKT_226.xsd'},
}
SYNTHETIC = {'taxId': '9999999997', 'taxpayerName': 'DỮ LIỆU GIẢ LẬP — KHÔNG NỘP THUẾ', 'signer': 'Người thử nghiệm', 'signDate': '20/03/2026'}

def check(value, reason='WORKBOOK_CASE_POLICY'):
    if not value: raise ValueError(reason)

def no_duplicate_keys(pairs):
    keys = [k for k, _ in pairs]; check(len(keys) == len(set(keys)), 'WORKBOOK_CASE_DUPLICATE_KEY'); return dict(pairs)

def validate(raw: bytes):
    check(len(raw) <= 65536, 'WORKBOOK_CASE_SIZE')
    plan = json.loads(raw.decode('utf-8'), object_pairs_hook=no_duplicate_keys)
    check(set(plan) == {'format', 'htkkVersion', 'nativeQualified', 'filingEnabled', 'driverImplemented', 'scope', 'header', 'createdDate', 'cases'})
    check(plan['format'] == 'htkk-workbook-native-case-plan-v1' and plan['htkkVersion'] == '5.8.1')
    check(plan['nativeQualified'] is False and plan['filingEnabled'] is False and plan['driverImplemented'] is False, 'WORKBOOK_CASE_GATE')
    check(plan['header'] == SYNTHETIC, 'WORKBOOK_CASE_PRIVACY')
    check(re.fullmatch(r'\d{4}-\d{2}-\d{2}', plan['createdDate']))
    cases = plan['cases']; check(type(cases) is list and 0 < len(cases) <= 32)
    seen = set()
    for case in cases:
        check(set(case) == {'caseId', 'menuId', 'xmlVersion', 'period', 'selected', 'overrides', 'expected'})
        check(re.fullmatch(r'[A-Za-z0-9-]{1,80}', case['caseId']) and case['caseId'] not in seen); seen.add(case['caseId'])
        unit = UNITS.get(case['menuId']); check(unit, 'WORKBOOK_CASE_MENU')
        check(case['xmlVersion'] == unit['xmlVersion'])
        period = case['period']
        check(period == {'year': 2025, 'fromDate': '01/01/2025', 'toDate': '31/12/2025'}, 'WORKBOOK_CASE_PERIOD')
        check(type(case['selected']) is list and len(set(case['selected'])) == len(case['selected']) and set(case['selected']) <= unit['appendices'])
        check(type(case['overrides']) is dict)
        for sheet, cells in case['overrides'].items():
            check(re.fullmatch(r'[0-9A-Z-]{1,16}', sheet) and type(cells) is dict and 0 < len(cells) <= 64)
            for cell, value in cells.items():
                check(re.fullmatch(r'[A-Z]{1,3}[1-9][0-9]{0,4}', cell) and type(value) is str and len(value) <= 64)
                # Money inputs are exact integers; text inputs must be marked synthetic.
                check(re.fullmatch(r'(0|[1-9][0-9]{0,15})', value) or 'giả lập' in value, 'WORKBOOK_CASE_PRIVACY')
        check(type(case['expected']) is dict and 0 < len(case['expected']) <= 32)
        for path, value in case['expected'].items():
            check(re.fullmatch(r'HSoThueDTu/HSoKhaiThue/(CTieuTKhaiChinh|PLuc)(/[A-Za-z0-9_]{1,64}){1,4}', path) and type(value) is str and len(value) <= 64)
    check(sum(1 for c in cases if c['menuId'] == 'N8') >= 2 and {c['menuId'] for c in cases} == set(UNITS), 'WORKBOOK_CASE_COVERAGE')
    return plan

PLAN = validate(PLAN_FILE.read_bytes())
