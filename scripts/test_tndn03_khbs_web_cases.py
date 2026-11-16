"""Input contract of the 03/TNDN kê khai bổ sung cases (htkk_tndn03_khbs_web_cases.py, merged into htkk_ntnn_khbs_web_cases.py).
N8 has KieuKHBS 3 in HTKK 5.8.2: its B files carry the 03-1A/TNDN annex, then PL01_KHBS / PL01_1_KHBS, and its rounds run
"Tổng hợp KHBS". Synthetic checks only; the reviewed producer files stay private (only their sizes and SHA-256 are pinned).
Byte-level checks run on a second module instance pinned to synthetic in-memory files (ntnn_khbs_test_support.py)."""
import hashlib
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


m = load('htkk_ntnn_khbs_web_cases_tndn03', 'htkk_ntnn_khbs_web_cases.py')
tndn03 = load('htkk_tndn03_khbs_web_cases_test', 'htkk_tndn03_khbs_web_cases.py')
support = load('ntnn_khbs_test_support_tndn03', 'ntnn_khbs_test_support.py')
sm = support.pin(load('htkk_ntnn_khbs_web_cases_tndn03_pinned', 'htkk_ntnn_khbs_web_cases.py'))
registry = load('htkk_native_cases_tndn03', 'htkk_native_cases.py')
CASES = ('03TNDN-khbs-increase-Y2025', '03TNDN-khbs-lan2-Y2025', '03TNDN-khbs-decrease-Y2025', '03TNDN-khbs-rate15-Y2025')
INCREASE, LAN2, RATE15 = '03TNDN-khbs-increase-Y2025', '03TNDN-khbs-lan2-Y2025', '03TNDN-khbs-rate15-Y2025'
ANNEX = 'PLuc_03_1A_TNDN'


def manifest(case_id, module):
    c = module.CASES[case_id]
    value = dict(module.manifest_fields(case_id), sourceCommit='0' * 40, producerSha256='1' * 64, bytes=c['web'][0], xmlSha256=c['web'][1],
                 originalBytes=c['original'][0], originalXmlSha256=c['original'][1])
    if c['prior']:
        value.update(priorBytes=c['prior'][0], priorXmlSha256=c['prior'][1])
    return value


class Tndn03KhbsWebCases(unittest.TestCase):
    def test_four_cases_merged_with_their_own_producer_menu_and_period(self):
        self.assertEqual(m.TNDN03_CASES, CASES)
        self.assertEqual(set(tndn03.CASES), set(CASES))
        self.assertFalse((set(m.NTNN_CASES) | set(m.KK05_CASES) | set(m.CNKD_CASES) | set(m.QTT02_CASES)) & set(CASES))
        self.assertEqual(m.MENUS['N8'], ('892', '2.9.4'))
        self.assertEqual(m.PERIODS['N8'], ('Y', '2025', '01/01/2025', '31/12/2025'))
        for case_id in CASES:
            c = m.CASES[case_id]
            self.assertEqual(m.producer(case_id), 'scripts/generate-htkk-web-tndn03-khbs-reference.mjs')
            self.assertEqual(m.manifest_fields(case_id)['exporter'], 'lib/htkk-tndn03-khbs.ts')
            self.assertEqual(m.names(case_id), (m.ORIGINAL_NAME,) + ((m.PRIOR_NAME,) if case_id == LAN2 else ()) + (m.WEB_NAME, m.MANIFEST_NAME))
            self.assertEqual(m.input_mode(case_id), 'khbs-web-xml-import-reexport')
            self.assertEqual(c['annexParts'], (ANNEX,))
            self.assertEqual(c['khbsParts'], ('PL01_KHBS', 'PL01_1_KHBS'))
            self.assertTrue(m.khbs_summary(case_id))
            self.assertEqual(m.validate_manifest(manifest(case_id, m))['caseId'], case_id)
            self.assertEqual(set(c['expected']), {'rows', 'subitems', 'ct10', 'ct3a_1', 'ct3a_2', 'ct3b'})
            # Năm 2025 is due 31/03/2026 (GetHanNopToKhai, N8 branch): 227 days to ngày lập 13/11/2026.
            self.assertEqual((c['expected']['ct3a_1'], c['expected']['ct3a_2']), ('2026-11-13', '227'))
            self.assertEqual(c['expected']['subitems'][0][0], '1052')
            self.assertEqual(m.tax_leaf_count(case_id), 421)
        self.assertEqual(m.CASES[LAN2]['prior'], m.CASES[INCREASE]['web'])
        self.assertEqual(len({m.CASES[c]['original'] for c in CASES if c != RATE15}), 1)
        self.assertNotEqual(m.CASES[RATE15]['original'], m.CASES[INCREASE]['original'])

    def test_registered_as_observation_cases_with_summary(self):
        for case_id in CASES:
            row = registry.CASES[case_id]
            self.assertIs(row['releaseGate'], False)
            self.assertEqual(registry.htkk_version(case_id), '5.8.2')
            self.assertEqual(registry.driver(case_id), 'declaration-amendment-khbs-inspect')
            self.assertEqual(row['format'], m.manifest_fields(case_id)['format'])
            self.assertEqual(row['unit']['amendmentOrder'], m.CASES[case_id]['soLan'])
            self.assertEqual((row['unit']['menuId'], row['unit']['adapterVersion'], row['unit']['periodType'], row['unit']['periodValue']), ('N8', '2.9.4', 'year', '2025'))
            self.assertEqual(row['unit']['annexes'], ['03-1A'])
        self.assertTrue(set(CASES) <= set(registry.NTNN_KHBS_CASES))
        self.assertFalse(set(CASES) & set(registry.NTNN_KHBS_NO_SUMMARY_CASES))
        self.assertFalse(set(CASES) & set(registry.NTNN_KHBS_TICK_CASES))

    def test_pinned_synthetic_files_validate_and_the_annex_order_is_enforced(self):
        for case_id in CASES:
            files = support.files(sm, case_id)
            self.assertEqual(sm.validate_files(files, manifest(case_id, sm))['amendmentLeafTarget'], sm.CASES[case_id]['leafTarget'])
            self.assertIn(b'<' + ANNEX.encode() + b'>', files[sm.ORIGINAL_NAME])
        body = support.files(sm, INCREASE)[sm.WEB_NAME].decode('utf-8')
        annex = re.search('<%s>.*?</%s>' % (ANNEX, ANNEX), body).group(0)
        for changed in (body.replace(annex, ''), body.replace(annex, '').replace('</PLuc>', annex + '</PLuc>')):
            raw = changed.encode('utf-8')
            saved = sm.CASES[INCREASE]['web']
            try:
                sm.CASES[INCREASE]['web'] = (len(raw), hashlib.sha256(raw).hexdigest())
                with self.assertRaises(sm.NtnnKhbsWebCaseError) as error:
                    sm.validate_xml(raw, INCREASE, 'web')
                self.assertEqual(error.exception.code, 'AMENDMENT')
            finally:
                sm.CASES[INCREASE]['web'] = saved
        with self.assertRaises(m.NtnnKhbsWebCaseError):
            m.validate_xml(support.files(sm, INCREASE)[m.WEB_NAME], INCREASE, 'web')


class Tndn03KhbsNativeRetention(unittest.TestCase):
    def test_catalogue_texts_of_n8_from_the_start(self):
        extra = m.catalogue_texts(INCREASE, [], frozenset())
        self.assertEqual(extra, tndn03.CATALOGUE_TEXTS)
        for text in ('Tờ khai', '03/TNDN', '03-1A/TNDN', '03-5/TNDN', 'E1_PN', 'E5_PN', 'C7', 'B14',
                     '1052 - Số phải nộp/Thuế TNDN của hoạt động sản xuất kinh doanh', 'Thuế thu nhập doanh nghiệp khác',
                     '[12] - Số thuế TNDN phải nộp cho từng tỉnh', 'Số thuế TNDN phải nộp cho từng tỉnh'):
            self.assertIn(text, extra)
        self.assertNotIn('Tờ khai', m.catalogue_texts('05KK-khbs-increase-Q3-2026', [], frozenset()))


class Tndn03KhbsDriverWiring(unittest.TestCase):
    def test_case_plans_use_the_n8_plan_with_the_khbs_schema_and_web_leaf_counts(self):
        plans = (ROOT / 'HtkkDeclarationCasePlans.cs').read_text(encoding='utf-8')
        ids = set(re.findall('"([^"]+)"', re.search(r'KhbsCaseIds=new string\[\]\{(.*?)\};', plans, re.S).group(1)))
        self.assertTrue(set(CASES) <= ids)
        self.assertRegex(plans, r'KhbsSoLan\(string caseId\)\{return [^;]*caseId=="03TNDN-khbs-lan2-Y2025"[^;]*\?2:')
        self.assertIn('if(caseId.StartsWith("03TNDN-khbs-",StringComparison.Ordinal))return Tndn03KhbsPlan(caseId);', plans)
        body = plans[plans.index('private static HtkkDeclarationCasePlan Tndn03KhbsPlan('):]
        body = body[:body.index('\n }\n')]
        self.assertIn('"Validate/KHBS_03_TNDN_TT80_294.xsd","42f72f6af7b53d74113c7005a1284ba1dacfd9267eae5ca50ad1d0b4f9558ba2"', body)
        self.assertIn('WorkbookService,%d,new string[0],new string[0]' % (m.tax_leaf_count(INCREASE) + 4), body)
        self.assertIn('new HtkkDeclarationCasePlan(caseId,"N8","2.9.4","892","Tndn03TT80Nckt294",new string[]{"101","101_2","N8"},"year","11","2025","","01/01/2025","31/12/2025",false,', body)
        self.assertIn('new string[]{"03-1A/TNDN"},new string[]{"03|Tờ khai","03-1A|03-1A/TNDN"},', body)
        first = plans[plans.index('case "03TNDN-profit20-Y2025":'):]
        first = first[:first.index(';\n')]
        for pin in ('"InterfaceTemplates/excel/03_TNDN_TT80_294.xls","f7482448c4628bb56120eaa0cda5c245474c45f770b1d9f1c1b4caf31c319476"', '"InterfaceTemplates/xml/03_TNDN_TT80_294.xml","cc05576d5356323c4f76e486814b72a3d48dd597523c1a0c11fba956e18be568"'):
            self.assertIn(pin, first)
            self.assertIn(pin, body)
        for case_id in CASES:
            self.assertIn('case "%s":' % case_id, plans)

    def test_probe_lists(self):
        formats = (ROOT / 'HtkkNativeCaseFormats.ps1').read_text(encoding='utf-8')
        listed = re.search(r"\$HtkkNtnnKhbsCases=@\((.*?)\)\n", formats).group(1)
        self.assertTrue(set(CASES) <= set(re.findall("'([^']+)'", listed)))
        self.assertIn("'03TNDN-khbs-lan2-Y2025'", re.search(r"\$HtkkNtnnKhbsLan2Cases=@\((.*?)\)\n", formats).group(1))
        registry_text = (ROOT / 'htkk-native-automation-registry.json').read_text(encoding='utf-8')
        reader = (ROOT / 'Get-HtkkSafeGuiReferenceResult.ps1').read_text(encoding='utf-8')
        for case_id in CASES:
            self.assertIn('"%s"' % case_id, registry_text)
            self.assertIn("'%s'" % case_id, reader)


if __name__ == '__main__':
    unittest.main()
