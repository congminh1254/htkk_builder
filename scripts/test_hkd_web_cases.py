"""Offline contract tests for the candidate 01/CNKD TT50 web->HTKK cases.

The XML built here is synthetic, assembled in memory from the contract itself;
it is not a captured web or original export and passing is never native evidence.
"""
import importlib.util, json, pathlib, unittest
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).parent


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / file); value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value); return value


hkd = load('hkd_web_cases', 'htkk_hkd_web_cases.py')
NS = hkd.NS
A = '01CNKD-TT50-revenue-two-groups-Q3-2026'
B = '01CNKD-TT50-profit-two-locations-annex13-M10-2026'
C = '01CNKD-TT50-310-pl01-three-groups-Q3-2026'
D = '01CNKD-TT50-310-pl03-two-groups-Q3-2026'


def synthetic(case_id, override=None):
    """Minimal namespaced document carrying exactly the leaves the validator inspects."""
    exp = dict(hkd.expected(case_id)); exp.update(override or {})
    case = hkd.CASES[case_id]
    ET.register_namespace('', NS)
    root = ET.Element('{%s}HSoThueDTu' % NS)
    def add(parent, name, text=None):
        node = ET.SubElement(parent, '{%s}%s' % (NS, name))
        if text is not None:
            node.text = text
        return node
    hs = add(root, 'HSoKhaiThue'); tk = add(hs, 'TKhaiThue')
    for name, value in (('maTKhai', hkd.MA_TKHAI), ('pbanTKhaiXML', case.get('xmlVersion', hkd.XML_VERSION)), ('loaiTKhai', 'C'), ('soLan', '0'), ('kieuKy', case['period'][0]), ('kyKKhai', case['kyKKhai'])):
        add(tk, name, value)
    nnt = add(hs, 'NNT'); add(nnt, 'mst', hkd.FAKE_MST); add(nnt, 'tenNNT', 'HO KINH DOANH GIA LAP - KHONG NOP')
    main = add(hs, 'CTieuTKhaiChinh'); add(main, 'mst_cu', hkd.FAKE_MST)
    for i in range(len(exp['ct14_soThue'])):
        r = add(main, 'CTietDoanhThu')
        add(r, 'ct10', exp['ct10'][i]); add(r, 'ct14_soThue', exp['ct14_soThue'][i]); add(r, 'ct17_soThue', exp['ct17_soThue'][i])
    default = add(main, 'CTietDoanhThu'); add(default, 'ct10', ''); add(default, 'ct14_soThue', '0'); add(default, 'ct17_soThue', '0')
    add(main, 'soThueGTGT_ct14', exp['soThueGTGT_ct14'][0]); add(main, 'soThueTNCN_ct17', exp['soThueTNCN_ct17'][0])
    for i in range(len(exp['ct40'])):
        d = add(main, 'ChiTietThongTinNopTHue')
        for name in ('ct38_ma', 'ct40', 'ct42_ma', 'ct46'):
            add(d, name, exp[name][i])
    add(main, 'tongTienCT47', exp['tongTienCT47'][0])
    for value in exp['thueGTGTDuocGiam']:
        add(add(main, 'BangKeTenHHDV'), 'thueGTGTDuocGiam', value)
    if case.get('pl03'):
        pl = add(add(hs, 'PLuc'), 'PLuc_03_PhaiNop_NQ43'); i = 0
        for table, listed in (('CTiethoKD_tuKeKhai', case['pl03']['self']), ('CTiethoKD_keKhaiThay', case['pl03']['agent'])):
            for _ in listed:
                r = add(pl, table)
                for name in ('ma_nhomNNKD', 'soThueTNCN_duocGiam', 'soThueTNCN_phaiNop'):
                    add(r, name, exp[name][i])
                i += 1
        total = add(pl, 'TongCong'); add(total, 'tongSoThueTNCN_phaiNop', exp['tongSoThueTNCN_phaiNop'][0]); add(total, 'tongsoThueTNCN_duocGiam', exp['tongsoThueTNCN_duocGiam'][0])
    elif 'soThueTNCN_phaiNop' in exp:
        pl = add(add(hs, 'PLuc'), 'PLuc_01_GiamTNCN_NQ43')
        for i in range(len(exp['soThueTNCN_phaiNop'])):
            r = add(pl, 'CTietGiamTNCN')
            for name in ('ma_hoatDongSXKD', 'ma_nhomNNKD', 'soThueTNCN_phaiNop', 'soThueTNCN_duocGiam'):
                add(r, name, exp[name][i])
        total = add(pl, 'TongCong'); add(total, 'tongSoThueTNCN_phaiNop', exp['tongSoThueTNCN_phaiNop'][0]); add(total, 'tongsoThueTNCN_duocGiam', exp['tongsoThueTNCN_duocGiam'][0])
    return ET.tostring(root, encoding='utf-8')


class HkdOracle(unittest.TestCase):
    def test_hand_computed_values_case_a(self):
        e = hkd.expected(A)
        self.assertEqual(e['ct14_soThue'], ['3000000', '7000000'])  # 300tr×1%, (150tr−10tr)×5%
        self.assertEqual(e['ct17_soThue'], ['1500000', '3000000'])  # 300tr×0,5%, 150tr×2%
        self.assertEqual(e['soThueGTGT_ct14'], ['10000000']); self.assertEqual(e['soThueTNCN_ct17'], ['4500000'])
        self.assertEqual(e['ct40'], ['10000000', '4500000']); self.assertEqual(e['ct42_ma'], ['1701', '1003'])
        self.assertEqual(e['ct46'], ['2026-10-30', '2026-10-30']); self.assertEqual(e['tongTienCT47'], ['14500000'])
        self.assertEqual(e['thueGTGTDuocGiam'], [])

    def test_hand_computed_values_case_b(self):
        e = hkd.expected(B)
        # 140tr×5% − 1,4tr (PL 01-3: J=5, G=4, H=140tr×1%); 123.456.789×2% = 2.469.135,78; 100tr×1%
        self.assertEqual(e['ct14_soThue'], ['5600000', '2469136', '1000000'])
        self.assertEqual(e['ct17_soThue'], ['2800000', '1000000', '500000'])
        self.assertEqual(e['soThueGTGT_ct14'], ['9069136']); self.assertEqual(e['soThueTNCN_ct17'], ['4300000'])
        # Mục D: TNCN of the branch is folded into the head office (ô (2)).
        self.assertEqual(list(zip(e['ct38_ma'], e['ct42_ma'], e['ct40'])), [('00001', '1701', '8069136'), ('00002', '1701', '1000000'), ('00001', '1003', '4300000')])
        self.assertEqual(e['tongTienCT47'], ['13369136']); self.assertEqual(e['thueGTGTDuocGiam'], ['1400000'])
        self.assertEqual(e['ct46'], ['2026-11-20'] * 3)

    def test_hand_computed_values_case_c_310_pl01(self):
        e = hkd.expected(C)
        # Rows 01, 04 (ticked), 02. CE = 300tr×0,5% = 1,5tr; 200tr×1,5% = 3tr; 150tr×2% = 3tr. PL 01 on 01 and 04: H = CE×30% = 450.000 / 900.000.
        self.assertEqual(e['ct17_soThue'], ['1050000', '2100000', '3000000'])
        self.assertEqual(e['ct14_soThue'], ['3000000', '6000000', '7000000'])
        self.assertEqual(e['soThueTNCN_ct17'], ['6150000']); self.assertEqual(e['soThueGTGT_ct14'], ['16000000'])
        self.assertEqual(e['ct40'], ['16000000', '6150000']); self.assertEqual(e['tongTienCT47'], ['22150000'])
        self.assertEqual(e['soThueTNCN_phaiNop'], ['1500000', '3000000']); self.assertEqual(e['soThueTNCN_duocGiam'], ['450000', '900000'])
        self.assertEqual(e['ma_nhomNNKD'], ['01', '04'])
        # Totals as 01_43_1_CNKD_HKD_TT50_310.xml binds them: H_22 -> tongSoThueTNCN_phaiNop, G_22 -> tongsoThueTNCN_duocGiam.
        self.assertEqual(e['tongSoThueTNCN_phaiNop'], ['1350000']); self.assertEqual(e['tongsoThueTNCN_duocGiam'], ['4500000'])

    def test_hand_computed_values_case_d_310_pl03(self):
        e = hkd.expected(D)
        # Header (1); rows 01 (300tr) and 04 (200tr): CE 1,5tr / 3tr, [14] 3tr / 6tr. PL 03 mục A one row, group 04, 300.000
        # (one row per section: HTKK 5.8.2 cannot export two, run 43162952097): capNhatToKhai CF = H of the first mục A row
        # with the same location and group, so row 01 gets 0 and row 04 300.000; mục B default row (no group) adds nothing.
        self.assertEqual(e['ct17_soThue'], ['1500000', '3300000']); self.assertEqual(e['ct14_soThue'], ['3000000', '6000000'])
        self.assertEqual(e['soThueTNCN_ct17'], ['4800000']); self.assertEqual(e['soThueGTGT_ct14'], ['9000000'])
        self.assertEqual(e['ct40'], ['9000000', '4800000']); self.assertEqual(e['tongTienCT47'], ['13800000'])
        self.assertEqual(e['soThueTNCN_duocGiam'], ['300000', '0']); self.assertEqual(e['soThueTNCN_phaiNop'], ['300000', '0'])
        self.assertEqual(e['ma_nhomNNKD'], ['04', ''])
        self.assertEqual([len(t) for t in (hkd.CASES[D]['pl03']['self'], hkd.CASES[D]['pl03']['agent'])], [1, 1])
        # 01_43_3_CNKD_HKD_TT50_310.xml: H_28 -> tongSoThueTNCN_phaiNop, G_28 -> tongsoThueTNCN_duocGiam (H = G).
        self.assertEqual((e['tongSoThueTNCN_phaiNop'], e['tongsoThueTNCN_duocGiam']), (['300000'], ['300000']))
        # The oracle refuses a layout the case does not cover (header (2), a row without group).
        broken = dict(hkd.CASES[D], header={'c1': True, 'c2': True})
        with self.assertRaises(hkd.HkdWebCaseError):
            hkd.pl03_cf(broken, broken['locations'][0], broken['locations'][0]['rows'][0])

    def test_rates_cover_every_source_group(self):
        self.assertEqual(sorted(hkd.GROUPS), ['01', '02', '03', '04', '05', '06'])
        for code, (gtgt, _tncn, _letter) in hkd.GROUPS.items():
            self.assertEqual(hkd.ANNEX_RATE[code], round(float(gtgt) * 100))


class HkdValidator(unittest.TestCase):
    def test_accepts_exact_synthetic_documents(self):
        for case_id in hkd.CASES:
            self.assertTrue(hkd.validate_case_xml(case_id, synthetic(case_id)))

    def test_rejects_money_period_identity_and_privacy_drift(self):
        with self.assertRaises(hkd.HkdWebCaseError) as ctx:
            hkd.validate_case_xml(A, synthetic(A, {'soThueGTGT_ct14': ['10000001']}))
        self.assertEqual(ctx.exception.code, 'VALUE')
        with self.assertRaises(hkd.HkdWebCaseError) as ctx:
            hkd.validate_case_xml(C, synthetic(C).replace(b'<pbanTKhaiXML>3.1.0<', b'<pbanTKhaiXML>2.9.8<'))
        self.assertEqual(ctx.exception.code, 'IDENTITY')
        with self.assertRaises(hkd.HkdWebCaseError) as ctx:
            hkd.validate_case_xml(C, synthetic(C, {'soThueTNCN_duocGiam': ['450001', '900000']}))
        self.assertEqual(ctx.exception.code, 'VALUE')
        body = synthetic(A)
        for old, new, code in ((b'<kyKKhai>3/2026<', b'<kyKKhai>4/2026<', 'PERIOD'), (b'<maTKhai>1266<', b'<maTKhai>1240<', 'IDENTITY'), (b'<mst>9999999997<', b'<mst>0101234567<', 'PRIVACY')):
            with self.assertRaises(hkd.HkdWebCaseError) as ctx:
                hkd.validate_case_xml(A, body.replace(old, new))
            self.assertEqual(ctx.exception.code, code)

    def test_rejects_unknown_case_dtd_and_foreign_namespace(self):
        with self.assertRaises(hkd.HkdWebCaseError):
            hkd.validate_case_xml('01CNKD-unknown', synthetic(A))
        with self.assertRaises(hkd.HkdWebCaseError):
            hkd.validate_case_xml(A, b'<!DOCTYPE x><x/>')
        with self.assertRaises(hkd.HkdWebCaseError):
            hkd.validate_case_xml(A, synthetic(A).replace(NS.encode(), b'urn:other'))

    def test_not_registered_as_native_or_gate_case(self):
        registry = json.loads((ROOT / 'htkk-native-cases.json').read_text())
        promoted = {c['caseId']: c for c in registry['cases'] if c['caseId'] in hkd.CASES}
        # Cases A, C and D are promoted (declaration driver, never a release gate); B stays design-only.
        # C and D (3.1.0) run only on the HTKK 5.8.2 oracle.
        self.assertEqual(set(promoted), {A, C, D})
        self.assertEqual((promoted[D]['adapterId'], promoted[D]['htkkVersion'], promoted[D]['unit']['annexes'], promoted[D]['releaseGate']), ('01-cnkd-hkd-3.1.0-pl03', '5.8.2', ['01-5'], False))
        self.assertIs(promoted[A]['releaseGate'], False)
        self.assertEqual(promoted[A]['adapterId'], '01-cnkd-hkd-2.9.8')
        self.assertIs(promoted[C]['releaseGate'], False)
        self.assertEqual((promoted[C]['adapterId'], promoted[C]['htkkVersion'], promoted[C]['unit']['annexes']), ('01-cnkd-hkd-3.1.0-pl01', '5.8.2', ['01-4']))
        adapter = [a for a in registry['adapters'] if a['adapterId'] == '01-cnkd-hkd-3.1.0-pl01']
        self.assertEqual([(a['htkkVersion'], a['xmlVersion']) for a in adapter], [('5.8.2', '3.1.0')])
        self.assertNotIn(B, json.dumps(registry))


if __name__ == '__main__':
    unittest.main()
