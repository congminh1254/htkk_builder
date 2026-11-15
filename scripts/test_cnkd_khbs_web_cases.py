"""Input contract of the 01/CNKD kê khai bổ sung cases (htkk_cnkd_khbs_web_cases.py, merged into htkk_ntnn_khbs_web_cases.py).
U5 has KieuKHBS "" in HTKK 5.8.2: its B files carry no KHBS fragment and its rounds run no "Tổng hợp KHBS". Synthetic checks only;
the reviewed producer files stay private (only their sizes and SHA-256 are pinned). Byte-level checks run on a second module
instance pinned to synthetic in-memory files (ntnn_khbs_test_support.py)."""
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


m = load('htkk_ntnn_khbs_web_cases_cnkd', 'htkk_ntnn_khbs_web_cases.py')
cnkd = load('htkk_cnkd_khbs_web_cases_test', 'htkk_cnkd_khbs_web_cases.py')
support = load('ntnn_khbs_test_support_cnkd', 'ntnn_khbs_test_support.py')
sm = support.pin(load('htkk_ntnn_khbs_web_cases_cnkd_pinned', 'htkk_ntnn_khbs_web_cases.py'))
registry = load('htkk_native_cases_cnkd', 'htkk_native_cases.py')
CASES = ('01CNKD-khbs-increase-Q3-2026', '01CNKD-khbs-decrease-Q3-2026', '01CNKD-khbs-lan2-Q3-2026', '01CNKD-PL01-khbs-Q3-2026')
LAN2 = '01CNKD-khbs-lan2-Q3-2026'
PL01 = '01CNKD-PL01-khbs-Q3-2026'


def manifest(case_id, module):
    c = module.CASES[case_id]
    value = dict(module.manifest_fields(case_id), sourceCommit='0' * 40, producerSha256='1' * 64, bytes=c['web'][0], xmlSha256=c['web'][1],
                 originalBytes=c['original'][0], originalXmlSha256=c['original'][1])
    if c['prior']:
        value.update(priorBytes=c['prior'][0], priorXmlSha256=c['prior'][1])
    return value


class CnkdKhbsWebCases(unittest.TestCase):
    def test_four_cases_merged_with_their_own_producer_menu_and_period(self):
        self.assertEqual(m.CNKD_CASES, CASES)
        self.assertEqual(set(cnkd.CASES), set(CASES))
        self.assertFalse((set(m.NTNN_CASES) | set(m.KK05_CASES)) & set(CASES))
        self.assertEqual(m.MENUS['U5'], ('1266', '3.1.0'))
        self.assertEqual(m.PERIODS['U5'], ('Q', '3/2026', '01/07/2026', '30/09/2026'))
        for case_id in CASES:
            c = m.CASES[case_id]
            self.assertEqual(m.producer(case_id), 'scripts/generate-htkk-web-cnkd-khbs-reference.mjs')
            self.assertEqual(m.manifest_fields(case_id)['exporter'], 'lib/htkk-cnkd01-khbs.ts')
            self.assertEqual(m.names(case_id), (m.ORIGINAL_NAME,) + ((m.PRIOR_NAME,) if case_id == LAN2 else ()) + (m.WEB_NAME, m.MANIFEST_NAME))
            self.assertEqual(m.input_mode(case_id), 'khbs-web-xml-import-tick-reexport' if case_id == PL01 else 'khbs-web-xml-import-reexport')
            self.assertEqual(c['annexParts'], ('PLuc_01_GiamTNCN_NQ43',) if case_id == PL01 else ())
            # No KHBS fragment and no summary step for U5; every other KHBS case keeps both.
            self.assertEqual(c['khbsParts'], ())
            self.assertFalse(m.khbs_summary(case_id))
            self.assertEqual(m.validate_manifest(manifest(case_id, m))['caseId'], case_id)
            self.assertEqual(set(c['expected']), {'lines', 'total'})
        for case_id in m.NTNN_CASES + m.KK05_CASES:
            self.assertEqual(m.CASES[case_id]['khbsParts'], ('PL01_KHBS', 'PL01_1_KHBS'))
            self.assertTrue(m.khbs_summary(case_id))
        # Lần 2 starts from the lần-1 file of the increase case; the three plain cases share one lần đầu.
        self.assertEqual(m.CASES[LAN2]['prior'], m.CASES['01CNKD-khbs-increase-Q3-2026']['web'])
        self.assertEqual(len({m.CASES[c]['original'] for c in CASES if c != PL01}), 1)
        self.assertEqual(m.tax_leaf_count(PL01), 295)
        self.assertEqual({m.tax_leaf_count(c) for c in CASES if c != PL01}, {271})

    def test_registered_as_observation_cases_without_summary(self):
        for case_id in CASES:
            row = registry.CASES[case_id]
            self.assertIs(row['releaseGate'], False)
            self.assertEqual(registry.htkk_version(case_id), '5.8.2')
            self.assertEqual(registry.driver(case_id), 'declaration-amendment-khbs-inspect')
            self.assertEqual(row['format'], m.manifest_fields(case_id)['format'])
            self.assertEqual(row['unit']['amendmentOrder'], m.CASES[case_id]['soLan'])
            self.assertEqual((row['unit']['menuId'], row['unit']['adapterVersion'], row['unit']['periodType'], row['unit']['periodValue']), ('U5', '3.1.0', 'quarter', '3/2026'))
            self.assertEqual(row['unit']['annexes'], ['01-4'] if case_id == PL01 else [])
        self.assertEqual(registry.NTNN_KHBS_NO_SUMMARY_CASES, CASES)
        self.assertIn(PL01, registry.NTNN_KHBS_TICK_CASES)
        self.assertNotIn(PL01, registry.DECLARATION_TICK_CASES)

    def test_pinned_synthetic_files_validate_and_a_khbs_fragment_is_refused(self):
        for case_id in CASES:
            files = support.files(sm, case_id)
            self.assertEqual(sm.validate_files(files, manifest(case_id, sm))['amendmentLeafTarget'], sm.CASES[case_id]['leafTarget'])
            self.assertNotIn(b'PL01_KHBS', files[sm.WEB_NAME])
        # A U5 B file WITH a KHBS fragment, or a PL 01 B file without its annex, is refused (pins switched off for the check).
        body = support.files(sm, PL01)[sm.WEB_NAME].decode('utf-8')
        annex = re.search('<PLuc_01_GiamTNCN_NQ43>.*?</PLuc_01_GiamTNCN_NQ43>', body).group(0)
        fragment = '<PL01_KHBS><Header><soLan>1</soLan><mst>%s</mst></Header></PL01_KHBS>' % sm.MST
        for changed in (body.replace(annex, ''), body.replace('</PLuc>', fragment + '</PLuc>')):
            raw = changed.encode('utf-8')
            saved = sm.CASES[PL01]['web']
            try:
                sm.CASES[PL01]['web'] = (len(raw), hashlib.sha256(raw).hexdigest())
                with self.assertRaises(sm.NtnnKhbsWebCaseError) as error:
                    sm.validate_xml(raw, PL01, 'web')
                self.assertEqual(error.exception.code, 'AMENDMENT')
            finally:
                sm.CASES[PL01]['web'] = saved
        # The real pins refuse every synthetic file.
        with self.assertRaises(m.NtnnKhbsWebCaseError):
            m.validate_xml(support.files(sm, PL01)[m.WEB_NAME], PL01, 'web')


class CnkdKhbsDriverWiring(unittest.TestCase):
    def test_case_plans_use_the_u5_310_plan_with_the_khbs_schema_and_web_leaf_counts(self):
        plans = (ROOT / 'HtkkDeclarationCasePlans.cs').read_text(encoding='utf-8')
        ids = set(re.findall('"([^"]+)"', re.search(r'KhbsCaseIds=new string\[\]\{(.*?)\};', plans, re.S).group(1)))
        self.assertTrue(set(CASES) <= ids)
        self.assertRegex(plans, r'KhbsSoLan\(string caseId\)\{return [^;]*caseId=="01CNKD-khbs-lan2-Q3-2026"\?2:')
        self.assertIn('internal static bool KhbsSummary(string caseId){return Array.IndexOf(KhbsCaseIds,caseId)>=0&&!caseId.StartsWith("01CNKD-",StringComparison.Ordinal);}', plans)
        body = plans[plans.index('private static HtkkDeclarationCasePlan CnkdKhbsPlan('):]
        body = body[:body.index('\n }\n')]
        self.assertIn('"Validate/KHBS_01_CNKD_HKD_TT50_310.xsd","c55ba118b03c859ed20f6bcf2cadfde89c2450a9869b00a36e075af917f75aff"', body)
        self.assertIn('CnkdService,pl01?%d:%d,new string[0],new string[0]' % (m.tax_leaf_count(PL01) + 4, m.tax_leaf_count(CASES[0]) + 4), body)
        self.assertIn('pl01?new string[]{"PL 01 43/2026/QH16"}:new string[0]', body)
        self.assertIn('caseId=="01CNKD-PL01-khbs-Q3-2026"?ImportTick("01CNKD-TT50-310-pl01-three-groups-Q3-2026")', plans)
        for case_id in CASES:
            self.assertIn('case "%s":' % case_id, plans)

    def test_rounds_skip_the_summary_and_keep_the_saved_annexes(self):
        khbs = (ROOT / 'HtkkDeclarationKhbs.cs').read_text(encoding='utf-8')
        web = (ROOT / 'HtkkDeclarationWebImport.cs').read_text(encoding='utf-8')
        done = khbs[khbs.index('private void DeclarationKhbsInputDone()'):khbs.index('private void DeclarationKhbsExported(')]
        self.assertIn('if(declarationKhbsRound>0&&!HtkkDeclarationCasePlans.KhbsSummary(webCaseId)){', done)
        self.assertIn('declarationKhbsStepMask|=2048', done)
        self.assertNotIn('PerformClick', done)
        self.assertIn('if(!grid.Visible&&DeclarationKhbsMode()&&declarationKhbsRound>0&&!HtkkDeclarationCasePlans.KhbsSummary(webCaseId)){declarationAnnexListMask|=4096;declarationAnnexMatched=true;Record();return;}', web)

    def test_probe_lists_and_step_mask(self):
        probe = (ROOT / 'probe-htkk-windows.ps1').read_text(encoding='utf-8')
        formats = (ROOT / 'HtkkNativeCaseFormats.ps1').read_text(encoding='utf-8')
        self.assertIn("$HtkkNtnnKhbsNoSummaryCases=@(%s)" % ','.join("'%s'" % c for c in CASES), formats)
        self.assertIn('if($env:EXPECTED_WEB_CASE_ID -cin $HtkkNtnnKhbsNoSummaryCases){$khbsSteps=$khbsSteps-32+2048}', probe)


if __name__ == '__main__':
    unittest.main()
