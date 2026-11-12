"""Candidate synthetic 01/CNKD TT50 (menu U5, XML 2.9.8; 3.1.0 on the HTKK 5.8.2 oracle) web->HTKK cases.

NOT native proof and NOT registered in htkk-native-cases.json: no Windows driver
exists yet for menu U5 (see HKD-WEB-CASES.md). This module is the independent
oracle and privacy allowlist the future driver must use:

* the inputs are the fixed synthetic drafts committed in htkk_web
  ``tests/fixtures/htkk-hkd-cases/cases.json`` (fake NNT 9999999997);
* expected tax leaves are recomputed here from those inputs with Decimal
  arithmetic and half-away-from-zero display rounding, independently of the
  application's TypeScript engine;
* ``validate_case_xml`` checks one XML (web input or native re-export) against
  the allowlist: namespace, identity, period, fake NNT and every money leaf.

No network, no XML writes, no original binaries.
"""
from decimal import Decimal, ROUND_HALF_UP
import xml.etree.ElementTree as ET

NS = 'http://kekhaithue.gdt.gov.vn/TKhaiThue'
MENU_ID = 'U5'
MA_TKHAI = '1266'
XML_VERSION = '2.9.8'
# HTKK 5.8.2 Menu.xml U5 VersionXML (CnkdHkd01TT50Nckt310). A 3.1.0 case may tick PL 01 of NQ 43/2026/QH16
# (01_43_1_CNKD_HKD_TT50_310): CE = the 2.9.8 AE, PL 01 H = G*30% (H20), [17] = CE - CD + CF (AE291), CD = H.
XML_VERSION_310 = '3.1.0'
PL01_RATE = Decimal('0.3')
FAKE_MST = '9999999997'
# XLS 01_CNKD_HKD_TT50_298 BZ291/AE291 (GTGT/TNCN) and I291 (ct10) by ct09_ma.
GROUPS = {
    '01': ('0.01', '0.005', '(a)'), '02': ('0.05', '0.02', '(b)'), '03': ('0.05', '0.05', '(c)'),
    '04': ('0.03', '0.015', '(d)'), '05': ('0.05', '0.05', '(e)'), '06': ('0.02', '0.01', '(f)'),
}
ANNEX_RATE = {'01': 1, '02': 5, '03': 5, '04': 3, '05': 5, '06': 2}
WARD_NAMES = {'10129087': 'Phường Sơn Tây', '10129088': 'Phường Tùng Thiện'}
CODES = frozenset(('NAMESPACE', 'IDENTITY', 'PERIOD', 'PRIVACY', 'VALUE', 'CASE', 'STRUCTURE'))


class HkdWebCaseError(ValueError):
    def __init__(self, code, field=''):
        if code not in CODES:
            raise ValueError('Invalid bounded HKD diagnostic')
        self.code = code; self.field = field
        super().__init__(code if not field else code + ':' + field)


def reject(code, field=''):
    raise HkdWebCaseError(code, field)


def row(group, ct11, ct12='0', ct13='0', ct15=None, ct16='0', reduce=False):
    value = {'group': group, 'ct11': ct11, 'ct12': ct12, 'ct13': ct13, 'ct15': ct11 if ct15 is None else ct15, 'ct16': ct16}
    if reduce:
        value['reduce'] = True  # 3.1.0 chonGiamThue (AJ): the row goes to PL 01
    return value


CASES = {
    '01CNKD-TT50-revenue-two-groups-Q3-2026': {
        'period': ('Q', 3, 2026), 'kyKKhai': '3/2026', 'due': '2026-10-30', 'header': {'c1': True, 'c2': False},
        'locations': [{'headOffice': True, 'code': '00001', 'ward': '10129087', 'rows': [row('01', '300000000'), row('02', '150000000', ct12='10000000')]}],
        'annexSales': [],
    },
    '01CNKD-TT50-profit-two-locations-annex13-M10-2026': {
        'period': ('M', 10, 2026), 'kyKKhai': '10/2026', 'due': '2026-11-20', 'header': {'c1': False, 'c2': True},
        'locations': [
            {'headOffice': True, 'code': '00001', 'ward': '10129087', 'rows': [row('02', '140000000'), row('06', '123456789', ct16='23456789')]},
            {'headOffice': False, 'code': '00002', 'ward': '10129088', 'rows': [row('01', '100000000')]},
        ],
        'annexSales': [{'section': 'I', 'group': '02', 'revenue': '140000000'}],
    },
    # 3.1.0 on the HTKK 5.8.2 oracle (non-gating): the revenue case with a third group and PL 01 ticked on 01 and 04.
    '01CNKD-TT50-310-pl01-three-groups-Q3-2026': {
        'xmlVersion': XML_VERSION_310, 'period': ('Q', 3, 2026), 'kyKKhai': '3/2026', 'due': '2026-10-30', 'header': {'c1': True, 'c2': False},
        # Reduced rows first, the unticked group last: HTKK 5.8.2 daySangPLGiamThue never reaches a row after an unticked
        # one (DECLARATION-NATIVE-CASES.md, run 43138236726), so 01, 04 (ticked) then 02. Totals do not depend on the order.
        'locations': [{'headOffice': True, 'code': '00001', 'ward': '10129087', 'rows': [row('01', '300000000', reduce=True), row('04', '200000000', reduce=True), row('02', '150000000', ct12='10000000')]}],
        'annexSales': [], 'pl01': True,
    },
    # 3.1.0 with PL 03 of NQ 43/2026/QH16 (Mẫu 03, thuế phải nộp bù; HTKK 5.8.2, non-gating): header (1), rows 01 and 04,
    # mục A (tự kê khai) one row per industry row of the same location, mục B (khai thay) its default row.
    '01CNKD-TT50-310-pl03-two-groups-Q3-2026': {
        'xmlVersion': XML_VERSION_310, 'period': ('Q', 3, 2026), 'kyKKhai': '3/2026', 'due': '2026-10-30', 'header': {'c1': True, 'c2': False},
        'locations': [{'headOffice': True, 'code': '00001', 'ward': '10129087', 'rows': [row('01', '300000000'), row('04', '200000000')]}],
        'annexSales': [],
        'pl03': {'self': [('00001', '01', '600000'), ('00001', '04', '300000')], 'agent': [('', '', '0')]},
    },
}


def pl03_cf(case, loc, r):
    """CF (thuế bù) of one industry row: CnkdHkd01TT50Nckt310.capNhatToKhai with header (1) only (the reviewed case).
    Mục A (tự kê khai): H of the FIRST row with the same location code (D = BN) and group (K = BM); mục B (khai thay):
    only on the head office, every row with the same group, summed. A row without code or group is never reached here."""
    pl03 = case.get('pl03')
    if not pl03:
        return Decimal(0)
    if case['header']['c2'] or not case['header']['c1'] or not loc['code'] or not r['group']:
        raise HkdWebCaseError('CASE')
    cf = Decimal(0)
    for code, group, amount in pl03['self']:
        if code == loc['code'] and group == r['group']:
            cf += Decimal(amount); break
    if loc['headOffice']:
        cf += sum((Decimal(a) for _, g, a in pl03['agent'] if g == r['group']), Decimal(0))
    return cf


def display(value):
    """FarPoint 0-decimal text: half away from zero."""
    return str(value.quantize(Decimal('1'), rounding=ROUND_HALF_UP))


def expected(case_id):
    if case_id not in CASES:
        reject('CASE')
    case = CASES[case_id]
    reductions = {}
    sale_leaves = []
    for sale in case['annexSales']:
        j = Decimal(ANNEX_RATE[sale['group']])
        g = (j * Decimal(80) / Decimal(100)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
        h = (Decimal(sale['revenue']) * (j - g) / Decimal(100)).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        reductions[(sale['section'], sale['group'])] = reductions.get((sale['section'], sale['group']), Decimal(0)) + h
        sale_leaves.append(str(h))
    rows = []
    for loc in case['locations']:
        for r in loc['rows']:
            gt, tn, letter = GROUPS[r['group']]
            ct14 = (Decimal(r['ct11']) - Decimal(r['ct12']) - Decimal(r['ct13'])) * Decimal(gt) - reductions.get(('I', r['group']), Decimal(0))
            ce = (Decimal(r['ct15']) - Decimal(r['ct16'])) * Decimal(tn)
            # 3.1.0 PL 01: a ticked row with CE > 0 gets CD = H = CE x 30% (daySangPLGiamThue); CF = 0 without PL 03.
            cd = ce * PL01_RATE if case.get('pl01') and r.get('reduce') and ce > 0 else Decimal(0)
            cf = pl03_cf(case, loc, r)
            ct17 = ce - cd + cf
            rows.append({'loc': loc, 'ct10': letter, 'ct14': ct14, 'ct17': ct17, 'bt': ct17, 'ce': ce, 'cd': cd, 'cf': cf, 'reduced': bool(cd), 'group': r['group']})
    if case['header']['c2']:
        others = sum((r['bt'] for r in rows if not r['loc']['headOffice']), Decimal(0))
        if rows and rows[0]['loc']['headOffice']:
            rows[0]['bt'] += others
    keys = []; sums = {}
    for r in rows:
        key = (r['loc']['code'], r['loc']['ward'], '1701')
        if key not in sums:
            keys.append(key); sums[key] = Decimal(0)
        sums[key] += r['ct14']
    for r in rows:
        if case['header']['c2'] and not r['loc']['headOffice']:
            continue
        key = (r['loc']['code'], r['loc']['ward'], '1003')
        if key not in sums:
            keys.append(key); sums[key] = Decimal(0)
        sums[key] += r['bt']
    total14 = sum((r['ct14'] for r in rows), Decimal(0)); total17 = sum((r['ct17'] for r in rows), Decimal(0))
    pl01 = [r for r in rows if r['reduced']]
    extra = {}
    if case.get('pl01'):
        # One PL 01 row per ticked row (G = CE, H = CE x 30%). 01_43_1_CNKD_HKD_TT50_310.xml binds H_22 (sum of H) to
        # tongSoThueTNCN_phaiNop and G_22 (sum of G) to tongsoThueTNCN_duocGiam: the totals follow that binding.
        extra = {'soThueTNCN_phaiNop': [display(r['ce']) for r in pl01], 'soThueTNCN_duocGiam': [display(r['cd']) for r in pl01],
                 'ma_nhomNNKD': [r['group'] for r in pl01], 'ma_hoatDongSXKD': ['01' for _ in pl01],
                 'tongSoThueTNCN_phaiNop': [display(sum((r['cd'] for r in pl01), Decimal(0)))], 'tongsoThueTNCN_duocGiam': [display(sum((r['ce'] for r in pl01), Decimal(0)))]}
    if case.get('pl03'):
        # PL 03 rows as declared (H = G, XLS H22/H26); 01_43_3_CNKD_HKD_TT50_310.xml binds H_28 to tongSoThueTNCN_phaiNop and
        # G_28 to tongsoThueTNCN_duocGiam.
        listed = case['pl03']['self'] + case['pl03']['agent']
        total = sum((Decimal(a) for _, _, a in listed), Decimal(0))
        extra = {'soThueTNCN_duocGiam': [display(Decimal(a)) for _, _, a in listed], 'soThueTNCN_phaiNop': [display(Decimal(a)) for _, _, a in listed],
                 'ma_nhomNNKD': [g for _, g, _ in listed], 'tongSoThueTNCN_phaiNop': [display(total)], 'tongsoThueTNCN_duocGiam': [display(total)]}
    return {**extra,
        'ct10': [r['ct10'] for r in rows], 'ct14_soThue': [display(r['ct14']) for r in rows], 'ct17_soThue': [display(r['ct17']) for r in rows],
        'soThueGTGT_ct14': [display(total14)], 'soThueTNCN_ct17': [display(total17)],
        'ct38_ma': [k[0] for k in keys], 'ct42_ma': [k[2] for k in keys], 'ct40': [display(sums[k]) for k in keys],
        'ct46': [case['due'] for _ in keys], 'tongTienCT47': [display(sum(sums.values(), Decimal(0)))],
        'thueGTGTDuocGiam': sale_leaves,
    }


def _local(node):
    if not isinstance(node.tag, str) or not node.tag.startswith('{' + NS + '}'):
        reject('NAMESPACE')
    return node.tag[len(NS) + 2:]


def _texts(root, name):
    return [(n.text or '').strip() for n in root.iter('{' + NS + '}' + name)]


def validate_case_xml(case_id, xml_bytes):
    """Fail closed unless the XML carries this case's identity, fake NNT and exact money leaves."""
    if case_id not in CASES:
        reject('CASE')
    if not isinstance(xml_bytes, (bytes, bytearray)) or len(xml_bytes) > 500_000 or b'<!DOCTYPE' in xml_bytes or b'<!ENTITY' in xml_bytes:
        reject('STRUCTURE')
    root = ET.fromstring(xml_bytes)
    if _local(root) != 'HSoThueDTu':
        reject('STRUCTURE')
    for node in root.iter():
        _local(node)
    case = CASES[case_id]
    if _texts(root, 'maTKhai') != [MA_TKHAI] or _texts(root, 'pbanTKhaiXML') != [case.get('xmlVersion', XML_VERSION)] or _texts(root, 'loaiTKhai') != ['C'] or _texts(root, 'soLan') != ['0']:
        reject('IDENTITY')
    if _texts(root, 'kieuKy') != [case['period'][0]] or _texts(root, 'kyKKhai') != [case['kyKKhai']]:
        reject('PERIOD')
    if _texts(root, 'mst') != [FAKE_MST] or _texts(root, 'mst_cu') != [FAKE_MST] or 'GIA LAP' not in ''.join(_texts(root, 'tenNNT')):
        reject('PRIVACY')
    for name, values in expected(case_id).items():
        got = _texts(root, name)
        if name in ('ct10', 'ct14_soThue', 'ct17_soThue'):
            got = got[:len(values)]  # A.II/A.III default rows follow
        if got != values:
            reject('VALUE', name)
    return True
