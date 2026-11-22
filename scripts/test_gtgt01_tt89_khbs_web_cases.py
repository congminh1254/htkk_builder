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
CASES = (INCREASE, DECREASE)


def manifest(case_id, module):
    c = module.CASES[case_id]
    return dict(module.manifest_fields(case_id), sourceCommit='0' * 40, producerSha256='1' * 64, bytes=c['web'][0], xmlSha256=c['web'][1],
                originalBytes=c['original'][0], originalXmlSha256=c['original'][1])


class Gtgt01Tt89KhbsWebCases(unittest.TestCase):
    def test_two_cases_merged_with_their_own_producer_menu_period_and_oracle(self):
        self.assertEqual(m.GTGT01_TT89_CASES, CASES)
        self.assertEqual(set(z5.CASES), set(CASES))
        self.assertFalse((set(m.NTNN_CASES) | set(m.KK05_CASES) | set(m.CNKD_CASES) | set(m.QTT02_CASES) | set(m.QTT05_CASES) | set(m.TNDN03_CASES) | set(m.NTNN03_CASES) | set(m.TCKT01_CASES)) & set(CASES))
        self.assertEqual(m.MENUS['Z5'], ('2032', '3.0.9'))
        self.assertEqual(m.PERIODS['Z5'], ('M', '10/2026', '01/10/2026', '31/10/2026'))
        for case_id in CASES:
            c = m.CASES[case_id]
            self.assertEqual(m.producer(case_id), 'scripts/generate-htkk-web-gtgt01-tt89-khbs-reference.mjs')
            self.assertEqual(m.manifest_fields(case_id)['exporter'], 'lib/htkk-gtgt01-tt89-khbs.ts')
            self.assertEqual(m.manifest_fields(case_id)['htkkVersion'], '5.8.4')
            self.assertEqual(m.names(case_id), (m.ORIGINAL_NAME, m.WEB_NAME, m.MANIFEST_NAME))
            self.assertEqual(m.input_mode(case_id), 'khbs-web-xml-import-reexport')
            self.assertEqual((c['annexParts'], c['khbsParts'], c['soLan'], c['prior']), ((), ('PL01_KHBS', 'PL01_1_KHBS'), 1, None))
            self.assertTrue(m.khbs_summary(case_id))
            self.assertEqual(m.validate_manifest(manifest(case_id, m))['caseId'], case_id)
            self.assertEqual(set(c['expected']), {'rows', 'subitems', 'tongCong7', 'tongCong8', 'ct10', 'ct3a_1', 'ct3a_2', 'ct3b'})
            # The web reading: no tiểu mục on [40] / [43] (MapMCT_TieuMuc path_1 has no Z5 cell), so Muc_I.1 / Muc_II stay empty.
            self.assertEqual((c['expected']['subitems'], c['expected']['ct10'], c['expected']['ct3a_1'], c['expected']['ct3a_2'], c['expected']['ct3b']), ([], '0', '', '0', '0'))
        self.assertEqual(m.CASES[INCREASE]['original'], m.CASES[DECREASE]['original'])
        self.assertEqual(m.CASES[INCREASE]['expected']['rows'][-1], '[40]')
        self.assertEqual(m.CASES[DECREASE]['expected']['rows'], ['[23]', '[23a]', '[25]', '[36]', '[40a]', '[40]', '[41]', '[43]'])
        self.assertEqual((m.CASES[DECREASE]['expected']['tongCong7'], m.CASES[DECREASE]['expected']['tongCong8']), ('-100000', '100000'))
        self.assertEqual([m.tax_leaf_count(c) for c in CASES], [304, 291])

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
            self.assertEqual(row['adapterId'], '01-gtgt-tt89-3.0.9-khbs')
            self.assertEqual(row['format'], m.manifest_fields(case_id)['format'])
            self.assertEqual(row['unit'], {'menuId': 'Z5', 'adapterVersion': '3.0.9', 'periodType': 'month', 'periodValue': '10/2026', 'activityCode': '00', 'annexes': [], 'amendmentOrder': 1})
        self.assertTrue(set(CASES) <= set(registry.NTNN_KHBS_CASES))
        self.assertFalse(set(CASES) & set(registry.NTNN_KHBS_NO_SUMMARY_CASES))
        self.assertFalse(set(CASES) & set(registry.NTNN_KHBS_TICK_CASES))
        # Every other KHBS case of this driver stays on 5.8.2.
        self.assertEqual({registry.htkk_version(c) for c in registry.NTNN_KHBS_CASES if c not in CASES}, {'5.8.2'})

    def test_pinned_synthetic_files_validate_and_a_phu_luc_is_refused(self):
        for case_id in CASES:
            files = support.files(sm, case_id)
            self.assertEqual(sm.validate_files(files, manifest(case_id, sm))['amendmentLeafTarget'], sm.CASES[case_id]['leafTarget'])
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
        self.assertTrue(set(CASES) <= ids)
        self.assertNotRegex(plans, r'KhbsSoLan\(string caseId\)\{return [^;]*01GTGT-TT89-khbs-')
        self.assertIn('if(caseId.StartsWith("01GTGT-TT89-khbs-",StringComparison.Ordinal))return Gtgt01Tt89KhbsPlan(caseId);', plans)
        body = plans[plans.index('private static HtkkDeclarationCasePlan Gtgt01Tt89KhbsPlan('):]
        body = body[:body.index('\n }\n')]
        # KHBS_01_GTGT_TT89_309.xsd has the same bytes as 01_GTGT_TT89_309.xsd (HTKK 5.8.4 and 5.8.5).
        self.assertIn('"Validate/KHBS_01_GTGT_TT89_309.xsd","8481f7c98ca9e008742552bda4f7ecc814cb91d453584b179fdf2d7767d9da19"', body)
        self.assertIn('int leaves=caseId=="%s"?%d:%d;' % (DECREASE, m.tax_leaf_count(DECREASE) + 4, m.tax_leaf_count(INCREASE) + 4), body)
        self.assertIn('new HtkkDeclarationCasePlan(caseId,"Z5","3.0.9","2032","Gtgt01TT89Nckt309",new string[]{"101","101_1","Z5"},"month","19","2026","10","01/10/2026","31/10/2026",false,', body)
        first = plans[plans.index('case "01GTGT-TT89-sale10-M10-2026":'):]
        first = first[:first.index(';\n')]
        for pin in ('"InterfaceTemplates/excel/01_GTGT_TT89_309.xls","5370eb12c05cc2770e85ccc1bee7e6a7dc6138065f4c0fc4e0a418d3d9ee4585"', '"InterfaceTemplates/xml/01_GTGT_TT89_309.xml","ba96834481a4b5b8a1c803572d10fafb669538402ed06f80a504c3212488638a"'):
            self.assertIn(pin, first)
            self.assertIn(pin, body)
        self.assertIn('new string[0],new string[]{"01|Tờ khai"},', body)
        for case_id in CASES:
            self.assertIn('case "%s":' % case_id, plans)

    def test_probe_lists(self):
        formats = (ROOT / 'HtkkNativeCaseFormats.ps1').read_text(encoding='utf-8')
        listed = re.search(r"\$HtkkNtnnKhbsCases=@\((.*?)\)\n", formats).group(1)
        self.assertTrue(set(CASES) <= set(re.findall("'([^']+)'", listed)))
        self.assertFalse(set(CASES) & set(re.findall("'([^']+)'", re.search(r"\$HtkkNtnnKhbsLan2Cases=@\((.*?)\)\n", formats).group(1))))
        registry_text = (ROOT / 'htkk-native-automation-registry.json').read_text(encoding='utf-8')
        reader = (ROOT / 'Get-HtkkSafeGuiReferenceResult.ps1').read_text(encoding='utf-8')
        workflow = (ROOT.parent / '.github/workflows/probe-htkk-windows.yml').read_text(encoding='utf-8')
        for case_id in CASES:
            self.assertIn('"%s"' % case_id, registry_text)
            self.assertIn("'%s'" % case_id, reader)
            self.assertIn(case_id, workflow)


if __name__ == '__main__':
    unittest.main()
