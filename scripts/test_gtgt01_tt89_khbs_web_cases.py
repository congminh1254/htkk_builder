"""Input contract of the 01/GTGT TT89/2026 kê khai bổ sung cases (htkk_gtgt01_tt89_khbs_web_cases.py, merged into
htkk_ntnn_khbs_web_cases.py). Z5 has KieuKHBS 3 and VersionKHBS 3.0.9 in HTKK 5.8.4: its B files carry PL01_KHBS / PL01_1_KHBS
(no phụ lục in these cases), its rounds run "Tổng hợp KHBS", and the cases run on the HTKK 5.8.4 oracle. Synthetic checks only;
the reviewed producer files stay private (only their sizes and SHA-256 are pinned). Byte-level checks run on a second module
instance pinned to synthetic in-memory files (ntnn_khbs_test_support.py)."""
import importlib.util
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).parent


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


m = load('htkk_ntnn_khbs_web_cases_gtgt01_tt89', 'htkk_ntnn_khbs_web_cases.py')
z5 = load('htkk_gtgt01_tt89_khbs_web_cases_test', 'htkk_gtgt01_tt89_khbs_web_cases.py')
support = load('ntnn_khbs_test_support_gtgt01_tt89', 'ntnn_khbs_test_support.py')
sm = support.pin(load('htkk_ntnn_khbs_web_cases_gtgt01_tt89_pinned', 'htkk_ntnn_khbs_web_cases.py'))
registry = load('htkk_native_cases_gtgt01_tt89', 'htkk_native_cases.py')
INCREASE, DECREASE = '01GTGT-TT89-khbs-increase-M10-2026', '01GTGT-TT89-khbs-decrease-M10-2026'
LAN2_INCREASE, LAN2_DECREASE = '01GTGT-TT89-khbs-lan2-increase-M10-2026', '01GTGT-TT89-khbs-lan2-decrease-M10-2026'
LAN1 = (INCREASE, DECREASE)
LAN2 = (LAN2_INCREASE, LAN2_DECREASE)
CASES = LAN1 + LAN2
PRIOR_OF = {LAN2_INCREASE: INCREASE, LAN2_DECREASE: DECREASE}
# Not yet run: kỳ quý 4/2026 lần 1 and lần 2, and the hoạt động khác tỉnh [09]-[11] lần 1 (registry taxpayerProfile / periodLocation).
QUARTER, QUARTER_LAN2 = '01GTGT-TT89-khbs-increase-Q4-2026', '01GTGT-TT89-khbs-lan2-increase-Q4-2026'
OTHER_PROVINCE = '01GTGT-TT89-khbs-other-province-M10-2026'
NEW = (QUARTER, QUARTER_LAN2, OTHER_PROVINCE)
ALL = CASES + NEW
Q4 = ('Q', '4/2026', '01/10/2026', '31/12/2026')


def manifest(case_id, module):
    c = module.CASES[case_id]
    prior = {'priorBytes': c['prior'][0], 'priorXmlSha256': c['prior'][1]} if c['prior'] else {}
    return dict(module.manifest_fields(case_id), sourceCommit='0' * 40, producerSha256='1' * 64, bytes=c['web'][0], xmlSha256=c['web'][1],
                originalBytes=c['original'][0], originalXmlSha256=c['original'][1], **prior)


class Gtgt01Tt89KhbsWebCases(unittest.TestCase):
    def test_four_cases_merged_with_their_own_producer_menu_period_and_oracle(self):
        self.assertEqual(m.GTGT01_TT89_CASES, ALL)
        self.assertEqual(set(z5.CASES), set(ALL))
        self.assertFalse((set(m.NTNN_CASES) | set(m.KK05_CASES) | set(m.CNKD_CASES) | set(m.QTT02_CASES) | set(m.QTT05_CASES) | set(m.TNDN03_CASES) | set(m.NTNN03_CASES) | set(m.TCKT01_CASES)) & set(ALL))
        self.assertEqual(m.MENUS['Z5'], ('2032', '3.0.9'))
        self.assertEqual(m.PERIODS['Z5'], ('M', '10/2026', '01/10/2026', '31/10/2026'))
        for case_id in CASES:
            c = m.CASES[case_id]
            self.assertEqual(m.producer(case_id), 'scripts/generate-htkk-web-gtgt01-tt89-khbs-reference.mjs')
            self.assertEqual(m.manifest_fields(case_id)['exporter'], 'lib/htkk-gtgt01-tt89-khbs.ts')
            self.assertEqual(m.manifest_fields(case_id)['htkkVersion'], '5.8.4')
            self.assertEqual(m.input_mode(case_id), 'khbs-web-xml-import-reexport')
            if case_id in LAN1:
                self.assertEqual(m.names(case_id), (m.ORIGINAL_NAME, m.WEB_NAME, m.MANIFEST_NAME))
                self.assertEqual((c['annexParts'], c['khbsParts'], c['soLan'], c['prior']), ((), ('PL01_KHBS', 'PL01_1_KHBS'), 1, None))
            else:
                # Lần 2: the previous version is the lần 1 web file of the case it builds on, byte for byte.
                self.assertEqual(m.names(case_id), (m.ORIGINAL_NAME, m.PRIOR_NAME, m.WEB_NAME, m.MANIFEST_NAME))
                self.assertEqual((c['annexParts'], c['khbsParts'], c['soLan'], c['prior']), ((), ('PL01_KHBS', 'PL01_1_KHBS'), 2, m.CASES[PRIOR_OF[case_id]]['web']))
            self.assertTrue(m.khbs_summary(case_id))
            self.assertEqual(m.validate_manifest(manifest(case_id, m))['caseId'], case_id)
            self.assertEqual(set(c['expected']), {'rows', 'subitems', 'tongCong7', 'tongCong8', 'ct10', 'ct3a_1', 'ct3a_2', 'ct3b'})
            # The web reading: no tiểu mục on [40] / [43] (MapMCT_TieuMuc path_1 has no Z5 cell), so Muc_I.1 / Muc_II stay empty.
            self.assertEqual((c['expected']['subitems'], c['expected']['ct10'], c['expected']['ct3a_1'], c['expected']['ct3a_2'], c['expected']['ct3b']), ([], '0', '', '0', '0'))
        self.assertEqual({m.CASES[c]['original'] for c in CASES}, {m.CASES[INCREASE]['original']})
        self.assertEqual(m.CASES[INCREASE]['expected']['rows'][-1], '[40]')
        self.assertEqual(m.CASES[DECREASE]['expected']['rows'], ['[23]', '[23a]', '[25]', '[36]', '[40a]', '[40]', '[41]', '[43]'])
        self.assertEqual((m.CASES[DECREASE]['expected']['tongCong7'], m.CASES[DECREASE]['expected']['tongCong8']), ('-100000', '100000'))
        self.assertEqual([m.tax_leaf_count(c) for c in CASES], [304, 291, 304, 265])
        # Lần 2 is compared with lần 1 (GetFileNameLoadKhbs bs<N-1>): no [40a] / [40] row when both lần have 0 there.
        self.assertEqual(m.CASES[LAN2_INCREASE]['expected']['rows'], m.CASES[INCREASE]['expected']['rows'])
        self.assertEqual(m.CASES[LAN2_DECREASE]['expected']['rows'], ['[23]', '[23a]', '[25]', '[36]', '[41]', '[43]'])
        self.assertEqual((m.CASES[LAN2_DECREASE]['expected']['tongCong7'], m.CASES[LAN2_DECREASE]['expected']['tongCong8']), ('0', '-100000'))

    def test_quarter_and_other_province_cases(self):
        for case_id in NEW:
            c = m.CASES[case_id]
            self.assertEqual((m.producer(case_id), m.manifest_fields(case_id)['htkkVersion'], m.input_mode(case_id)), ('scripts/generate-htkk-web-gtgt01-tt89-khbs-reference.mjs', '5.8.4', 'khbs-web-xml-import-reexport'))
            self.assertEqual((c['annexParts'], c['khbsParts']), ((), ('PL01_KHBS', 'PL01_1_KHBS')))
            self.assertEqual(m.validate_manifest(manifest(case_id, m))['caseId'], case_id)
            self.assertEqual((c['expected']['subitems'], c['expected']['ct10'], c['expected']['ct3a_1'], c['expected']['ct3a_2'], c['expected']['ct3b']), ([], '0', '', '0', '0'))
        # Quý 4/2026: own period on every file; lần 2 builds on the quý lần 1 web file, byte for byte.
        self.assertEqual([m.period_of(m.CASES[c]) for c in NEW], [Q4, Q4, m.PERIODS['Z5']])
        self.assertEqual((m.CASES[QUARTER]['soLan'], m.CASES[QUARTER]['prior'], m.CASES[QUARTER_LAN2]['soLan'], m.CASES[QUARTER_LAN2]['prior']), (1, None, 2, m.CASES[QUARTER]['web']))
        self.assertEqual(m.CASES[QUARTER]['original'], m.CASES[QUARTER_LAN2]['original'])
        self.assertEqual(m.names(QUARTER_LAN2), (m.ORIGINAL_NAME, m.PRIOR_NAME, m.WEB_NAME, m.MANIFEST_NAME))
        self.assertEqual(m.CASES[QUARTER]['expected']['rows'], ['[27]', '[28]', '[32]', '[33]', '[34]', '[35]', '[36]', '[40a]', '[40]', '[41]', '[43]'])
        self.assertEqual((m.CASES[QUARTER]['expected']['tongCong7'], m.CASES[QUARTER]['expected']['tongCong8']), ('5000000', '-10000000'))
        self.assertEqual(m.CASES[QUARTER_LAN2]['expected']['rows'], m.CASES[INCREASE]['expected']['rows'])
        # [09]-[11] give no 01-1/KHBS row (MapMCT Z5 has no item for them): the nine rows of the increase case.
        self.assertEqual(m.CASES[OTHER_PROVINCE]['expected']['rows'], m.CASES[INCREASE]['expected']['rows'])
        self.assertNotEqual(m.CASES[OTHER_PROVINCE]['original'], m.CASES[INCREASE]['original'])
        self.assertEqual([m.tax_leaf_count(c) for c in NEW], [330, 304, 304])

    def test_another_oracle_in_the_manifest_is_refused(self):
        value = manifest(INCREASE, m)
        value['htkkVersion'] = '5.8.2'
        with self.assertRaises(m.NtnnKhbsWebCaseError) as error:
            m.validate_manifest(value)
        self.assertEqual(error.exception.code, 'MANIFEST')
        # The other KHBS cases keep 5.8.2.
        self.assertEqual(m.manifest_fields('01TCKT-310-khbs-hop-tac-kd-Q4-2026')['htkkVersion'], '5.8.2')

    def test_registered_as_observation_cases_with_summary_on_584(self):
        for case_id in CASES:
            row = registry.CASES[case_id]
            self.assertIs(row['releaseGate'], False)
            self.assertNotIn('notBefore', row)
            self.assertEqual(registry.htkk_version(case_id), '5.8.4')
            self.assertEqual(registry.driver(case_id), 'declaration-amendment-khbs-inspect')
            lan2 = case_id in LAN2
            self.assertEqual(row['adapterId'], '01-gtgt-tt89-3.0.9-khbs-lan2' if lan2 else '01-gtgt-tt89-3.0.9-khbs')
            self.assertEqual(row['format'], m.manifest_fields(case_id)['format'])
            self.assertEqual(row['unit'], {'menuId': 'Z5', 'adapterVersion': '3.0.9', 'periodType': 'month', 'periodValue': '10/2026', 'activityCode': '00', 'annexes': [], 'amendmentOrder': 2 if lan2 else 1})
        for case_id in NEW:
            row = registry.CASES[case_id]
            self.assertIs(row['releaseGate'], False)
            self.assertEqual((registry.htkk_version(case_id), registry.driver(case_id)), ('5.8.4', 'declaration-amendment-khbs-inspect'))
            lan2 = case_id == QUARTER_LAN2
            self.assertEqual(row['adapterId'], '01-gtgt-tt89-3.0.9-khbs-lan2' if lan2 else '01-gtgt-tt89-3.0.9-khbs')
            self.assertEqual(row['format'], m.manifest_fields(case_id)['format'])
            period = ('quarter', '4/2026') if case_id != OTHER_PROVINCE else ('month', '10/2026')
            self.assertEqual(row['unit'], {'menuId': 'Z5', 'adapterVersion': '3.0.9', 'periodType': period[0], 'periodValue': period[1], 'activityCode': '00', 'annexes': [], 'amendmentOrder': 2 if lan2 else 1})
        self.assertEqual(registry.GEOGRAPHY_CASES, ('01GTGT-TT89-other-province-M10-2026', OTHER_PROVINCE))
        self.assertTrue(set(NEW) <= set(registry.NTNN_KHBS_CASES))
        self.assertEqual(registry.TRUSTED_ADAPTERS['01-gtgt-tt89-3.0.9-khbs-lan2']['htkkVersion'], '5.8.4')
        self.assertEqual(registry.TRUSTED_ADAPTERS['01-gtgt-tt89-3.0.9-khbs-lan2']['amendmentOrder'], 2)
        self.assertTrue(set(CASES) <= set(registry.NTNN_KHBS_CASES))
        self.assertFalse(set(CASES) & set(registry.NTNN_KHBS_NO_SUMMARY_CASES))
        self.assertFalse(set(CASES) & set(registry.NTNN_KHBS_TICK_CASES))
        # Every other KHBS case of this driver stays on 5.8.2, but the HTKK 5.8.5 Y8 observation cases.
        y8_585 = {c for c in registry.NTNN_KHBS_CASES if registry.CASES[c]['adapterId'] == '01-ntnn-nccnn-tt89-3.0.9-khbs-585'}
        self.assertEqual(y8_585, {'01NTNN-NCCNN-khbs-part2-585-M10-2026', '01NTNN-NCCNN-khbs-part2-tncn-585-M10-2026', '01NTNN-NCCNN-khbs-part1-future-contract-M10-2026'})
        self.assertEqual({registry.htkk_version(c) for c in y8_585}, {'5.8.5'})
        self.assertEqual({registry.htkk_version(c) for c in registry.NTNN_KHBS_CASES if c not in ALL and c not in y8_585}, {'5.8.2'})

    def test_pinned_synthetic_files_validate_and_a_phu_luc_is_refused(self):
        for case_id in ALL:
            files = support.files(sm, case_id)
            self.assertEqual(sm.validate_files(files, manifest(case_id, sm))['amendmentLeafTarget'], sm.CASES[case_id]['leafTarget'])
        # A lần 2 case without its previous version, or with a lần 1 file where the prior belongs, is refused.
        files = support.files(sm, LAN2_INCREASE)
        with self.assertRaises(sm.NtnnKhbsWebCaseError) as error:
            sm.validate_files({k: v for k, v in files.items() if k != sm.PRIOR_NAME}, manifest(LAN2_INCREASE, sm))
        self.assertEqual(error.exception.code, 'NAMES')
        with self.assertRaises(sm.NtnnKhbsWebCaseError):
            sm.validate_files(dict(files, **{sm.PRIOR_NAME: files[sm.WEB_NAME]}), manifest(LAN2_INCREASE, sm))
        body = support.files(sm, INCREASE)[sm.WEB_NAME].decode('utf-8')
        changed = body.replace('<PLuc>', '<PLuc><PL_NQ142_GTGT><ct14>0</ct14></PL_NQ142_GTGT>').encode('utf-8')
        import hashlib
        saved = sm.CASES[INCREASE]['web']
        try:
            sm.CASES[INCREASE]['web'] = (len(changed), hashlib.sha256(changed).hexdigest())
            with self.assertRaises(sm.NtnnKhbsWebCaseError) as error:
                sm.validate_xml(changed, INCREASE, 'web')
            self.assertEqual(error.exception.code, 'AMENDMENT')
        finally:
            sm.CASES[INCREASE]['web'] = saved
        with self.assertRaises(m.NtnnKhbsWebCaseError):
            m.validate_xml(support.files(sm, INCREASE)[m.WEB_NAME], INCREASE, 'web')


class Gtgt01Tt89KhbsNativeRetention(unittest.TestCase):
    def test_catalogue_texts_of_z5_from_the_start(self):
        extra = m.catalogue_texts(INCREASE, [], frozenset())
        self.assertEqual(extra, z5.CATALOGUE_TEXTS)
        for text in ('Tờ khai', '01/GTGT', '0026', '[23a]', '[40]', 'Trong đó: Giá trị hàng hóa, dịch vụ hàng hóa nhập khẩu',
                     'Thuế giá trị gia tăng còn phải nộp trong kỳ ([40]=[40a]-[40b])',
                     'Thuế giá trị gia tăng hàng sản xuất, kinh doanh trong nước (gồm cả dịch vụ trong lĩnh vực dầu khí)'):
            self.assertIn(text, extra)
        self.assertEqual(len([t for t in z5.CATALOGUE_TEXTS if re.fullmatch(r'\[[0-9]{2}[ab]?\]', t)]), 30)
        self.assertNotIn('0026', m.catalogue_texts('05KK-khbs-increase-Q3-2026', [], frozenset()))


class Gtgt01Tt89KhbsDriverWiring(unittest.TestCase):
    def test_case_plans_use_the_lan_dau_plan_with_the_khbs_schema_and_web_leaf_counts(self):
        plans = (ROOT / 'HtkkDeclarationCasePlans.cs').read_text(encoding='utf-8')
        ids = set(re.findall('"([^"]+)"', re.search(r'KhbsCaseIds=new string\[\]\{(.*?)\};', plans, re.S).group(1)))
        self.assertTrue(set(ALL) <= ids)
        self.assertNotRegex(plans, r'KhbsSoLan\(string caseId\)\{return [^;]*01GTGT-TT89-khbs-(increase|decrease)-')
        for case_id in LAN2 + (QUARTER_LAN2,):
            self.assertRegex(plans, r'KhbsSoLan\(string caseId\)\{return [^;]*caseId=="%s"[^;]*\?2:' % case_id)
        self.assertIn('if(caseId.StartsWith("01GTGT-TT89-khbs-",StringComparison.Ordinal))return Gtgt01Tt89KhbsPlan(caseId);', plans)
        body = plans[plans.index('private static HtkkDeclarationCasePlan Gtgt01Tt89KhbsPlan('):]
        body = body[:body.index('\n }\n')]
        # KHBS_01_GTGT_TT89_309.xsd has the same bytes as 01_GTGT_TT89_309.xsd (HTKK 5.8.4 and 5.8.5).
        self.assertIn('"Validate/KHBS_01_GTGT_TT89_309.xsd","8481f7c98ca9e008742552bda4f7ecc814cb91d453584b179fdf2d7767d9da19"', body)
        self.assertIn('int leaves=caseId=="%s"?%d:caseId=="%s"?%d:caseId=="%s"?%d:%d;' % (DECREASE, m.tax_leaf_count(DECREASE) + 4, LAN2_DECREASE, m.tax_leaf_count(LAN2_DECREASE) + 4, QUARTER, m.tax_leaf_count(QUARTER) + 4, m.tax_leaf_count(INCREASE) + 4), body)
        for case_id in (LAN2_INCREASE, QUARTER_LAN2, OTHER_PROVINCE):
            self.assertEqual(m.tax_leaf_count(case_id), m.tax_leaf_count(INCREASE))
        # Quý 4/2026 takes the period of the lần đầu case 01GTGT-TT89-quarter-Q4-2026 (KieuKy 19, quarter 4).
        self.assertIn('bool quarter=caseId.EndsWith("-Q4-2026",StringComparison.Ordinal);', body)
        self.assertIn('new HtkkDeclarationCasePlan(caseId,"Z5","3.0.9","2032","Gtgt01TT89Nckt309",new string[]{"101","101_1","Z5"},quarter?"quarter":"month","19","2026",quarter?"4":"10","01/10/2026",quarter?"31/12/2026":"31/10/2026",false,', body)
        self.assertIn('case "01GTGT-TT89-quarter-Q4-2026":return new HtkkDeclarationCasePlan(caseId,"Z5","3.0.9","2032","Gtgt01TT89Nckt309",new string[]{"101","101_1","Z5"},"quarter","19","2026","4","01/10/2026","31/12/2026",false,', plans)
        first = plans[plans.index('case "01GTGT-TT89-sale10-M10-2026":'):]
        first = first[:first.index(';\n')]
        for pin in ('"InterfaceTemplates/excel/01_GTGT_TT89_309.xls","5370eb12c05cc2770e85ccc1bee7e6a7dc6138065f4c0fc4e0a418d3d9ee4585"', '"InterfaceTemplates/xml/01_GTGT_TT89_309.xml","ba96834481a4b5b8a1c803572d10fafb669538402ed06f80a504c3212488638a"'):
            self.assertIn(pin, first)
            self.assertIn(pin, body)
        self.assertIn('new string[0],new string[]{"01|Tờ khai"},', body)
        for case_id in ALL:
            self.assertIn('case "%s":' % case_id, plans)

    def test_probe_lists(self):
        formats = (ROOT / 'HtkkNativeCaseFormats.ps1').read_text(encoding='utf-8')
        listed = re.search(r"\$HtkkNtnnKhbsCases=@\((.*?)\)\n", formats).group(1)
        self.assertTrue(set(ALL) <= set(re.findall("'([^']+)'", listed)))
        lan2_listed = set(re.findall("'([^']+)'", re.search(r"\$HtkkNtnnKhbsLan2Cases=@\((.*?)\)\n", formats).group(1)))
        self.assertFalse((set(LAN1) | {QUARTER, OTHER_PROVINCE}) & lan2_listed)
        self.assertTrue(set(LAN2) | {QUARTER_LAN2} <= lan2_listed)
        registry_text = (ROOT / 'htkk-native-automation-registry.json').read_text(encoding='utf-8')
        reader = (ROOT / 'Get-HtkkSafeGuiReferenceResult.ps1').read_text(encoding='utf-8')
        workflow = (ROOT.parent / '.github/workflows/probe-htkk-windows.yml').read_text(encoding='utf-8')
        for case_id in ALL:
            self.assertIn('"%s"' % case_id, registry_text)
            self.assertIn("'%s'" % case_id, reader)
            self.assertIn(case_id, workflow)


if __name__ == '__main__':
    unittest.main()
