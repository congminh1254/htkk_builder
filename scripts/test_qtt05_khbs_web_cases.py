"""Input contract of the 05/QTT-TNCN kê khai bổ sung cases (htkk_qtt05_khbs_web_cases.py, merged into htkk_ntnn_khbs_web_cases.py).
B9 has KieuKHBS 3 in HTKK 5.8.2: its B files carry the 05-1 and 05-3 annexes, then PL01_KHBS / PL01_1_KHBS, and its rounds run
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


m = load('htkk_ntnn_khbs_web_cases_qtt05', 'htkk_ntnn_khbs_web_cases.py')
qtt05 = load('htkk_qtt05_khbs_web_cases_test', 'htkk_qtt05_khbs_web_cases.py')
support = load('ntnn_khbs_test_support_qtt05', 'ntnn_khbs_test_support.py')
sm = support.pin(load('htkk_ntnn_khbs_web_cases_qtt05_pinned', 'htkk_ntnn_khbs_web_cases.py'))
registry = load('htkk_native_cases_qtt05', 'htkk_native_cases.py')
CASES = ('05QTT-khbs-increase-Y2025', '05QTT-khbs-lan2-Y2025', '05QTT-khbs-decrease-Y2025')
LAN2, DECREASE = '05QTT-khbs-lan2-Y2025', '05QTT-khbs-decrease-Y2025'
ANNEXES = ('PLuc_05_1_BK_QTT', 'PLuc_05_3_BK_QTT')


def manifest(case_id, module):
    c = module.CASES[case_id]
    value = dict(module.manifest_fields(case_id), sourceCommit='0' * 40, producerSha256='1' * 64, bytes=c['web'][0], xmlSha256=c['web'][1],
                 originalBytes=c['original'][0], originalXmlSha256=c['original'][1])
    if c['prior']:
        value.update(priorBytes=c['prior'][0], priorXmlSha256=c['prior'][1])
    return value


class Qtt05KhbsWebCases(unittest.TestCase):
    def test_three_cases_merged_with_their_own_producer_menu_and_period(self):
        self.assertEqual(m.QTT05_CASES, CASES)
        self.assertEqual(set(qtt05.CASES), set(CASES))
        self.assertFalse((set(m.NTNN_CASES) | set(m.KK05_CASES) | set(m.CNKD_CASES) | set(m.QTT02_CASES)) & set(CASES))
        self.assertEqual(m.MENUS['B9'], ('953', '2.9.3'))
        self.assertEqual(m.PERIODS['B9'], ('Y', '2025', '', ''))
        for case_id in CASES:
            c = m.CASES[case_id]
            self.assertEqual(m.producer(case_id), 'scripts/generate-htkk-web-qtt05-khbs-reference.mjs')
            self.assertEqual(m.manifest_fields(case_id)['exporter'], 'lib/htkk-qtt05-khbs.ts')
            self.assertEqual(m.names(case_id), (m.ORIGINAL_NAME,) + ((m.PRIOR_NAME,) if case_id == LAN2 else ()) + (m.WEB_NAME, m.MANIFEST_NAME))
            self.assertEqual(m.input_mode(case_id), 'khbs-web-xml-import-reexport')
            self.assertEqual(c['annexParts'], ANNEXES)
            self.assertEqual(c['khbsParts'], ('PL01_KHBS', 'PL01_1_KHBS'))
            self.assertTrue(m.khbs_summary(case_id))
            self.assertEqual(m.validate_manifest(manifest(case_id, m))['caseId'], case_id)
            self.assertEqual(set(c['expected']), {'rows', 'subitems', 'ct10', 'ct3a_1', 'ct3a_2', 'ct3b'})
            self.assertEqual((c['expected']['ct3a_1'], c['expected']['ct3a_2']), ('2026-11-13', '227'))
        self.assertEqual(m.CASES[LAN2]['prior'], m.CASES['05QTT-khbs-increase-Y2025']['web'])
        self.assertEqual(len({m.CASES[c]['original'] for c in CASES}), 1)
        self.assertEqual(m.tax_leaf_count(DECREASE), 319)
        self.assertEqual({m.tax_leaf_count(c) for c in CASES if c != DECREASE}, {371})

    def test_registered_as_observation_cases_with_summary(self):
        for case_id in CASES:
            row = registry.CASES[case_id]
            self.assertIs(row['releaseGate'], False)
            self.assertEqual(registry.htkk_version(case_id), '5.8.2')
            self.assertEqual(registry.driver(case_id), 'declaration-amendment-khbs-inspect')
            self.assertEqual(row['format'], m.manifest_fields(case_id)['format'])
            self.assertEqual(row['unit']['amendmentOrder'], m.CASES[case_id]['soLan'])
            self.assertEqual((row['unit']['menuId'], row['unit']['adapterVersion'], row['unit']['periodType'], row['unit']['periodValue']), ('B9', '2.9.3', 'year', '2025'))
            self.assertEqual(row['unit']['annexes'], ['05-1', '05-3'])
        self.assertTrue(set(CASES) <= set(registry.NTNN_KHBS_CASES))
        self.assertFalse(set(CASES) & (set(registry.NTNN_KHBS_NO_SUMMARY_CASES) | set(registry.NTNN_KHBS_TICK_CASES)))

    def test_pinned_synthetic_files_validate_and_the_annex_order_is_enforced(self):
        for case_id in CASES:
            files = support.files(sm, case_id)
            self.assertEqual(sm.validate_files(files, manifest(case_id, sm))['amendmentLeafTarget'], sm.CASES[case_id]['leafTarget'])
        body = support.files(sm, DECREASE)[sm.WEB_NAME].decode('utf-8')
        annex = re.search('<PLuc_05_3_BK_QTT>.*?</PLuc_05_3_BK_QTT>', body).group(0)
        for changed in (body.replace(annex, ''), body.replace(annex, '').replace('</PLuc>', annex + '</PLuc>')):
            raw = changed.encode('utf-8')
            saved = sm.CASES[DECREASE]['web']
            try:
                sm.CASES[DECREASE]['web'] = (len(raw), hashlib.sha256(raw).hexdigest())
                with self.assertRaises(sm.NtnnKhbsWebCaseError) as error:
                    sm.validate_xml(raw, DECREASE, 'web')
                self.assertEqual(error.exception.code, 'AMENDMENT')
            finally:
                sm.CASES[DECREASE]['web'] = saved
        with self.assertRaises(m.NtnnKhbsWebCaseError):
            m.validate_xml(support.files(sm, DECREASE)[m.WEB_NAME], DECREASE, 'web')


class Qtt05KhbsNativeRetention(unittest.TestCase):
    def test_public_b9_catalogue_texts_from_the_first_run(self):
        for text in ('05/QTT-TNCN', '05-1/BK-TNCN', '05-2/BK-TNCN', '05-3/BK-TNCN', '05-1/BK-QTT-TNCN', 'Tờ khai', '[31.1]', '[20.1]', '[42]',
                     'Tổng số thuế thu nhập cá nhân đã nộp thừa [41]', 'Tổng số thuế TNCN đã khấu trừ'):
            self.assertIn(text, qtt05.CATALOGUE_TEXTS)
        extra = m.catalogue_texts(DECREASE, [], frozenset())
        self.assertEqual(extra, qtt05.CATALOGUE_TEXTS)
        # Every catalogue text is public HTKK wording: no synthetic person, MST or amount.
        for text in qtt05.CATALOGUE_TEXTS:
            self.assertNotRegex(text, r'NGUOI|GIA LAP|9999999997|[0-9]{6}')


class Qtt05KhbsDriverWiring(unittest.TestCase):
    def test_case_plans_use_the_b9_plan_with_the_khbs_schema_and_web_leaf_counts(self):
        plans = (ROOT / 'HtkkDeclarationCasePlans.cs').read_text(encoding='utf-8')
        ids = set(re.findall('"([^"]+)"', re.search(r'KhbsCaseIds=new string\[\]\{(.*?)\};', plans, re.S).group(1)))
        self.assertTrue(set(CASES) <= ids)
        self.assertRegex(plans, r'KhbsSoLan\(string caseId\)\{return [^;]*caseId=="05QTT-khbs-lan2-Y2025"[^;]*\?2:')
        self.assertIn('if(caseId.StartsWith("05QTT-",StringComparison.Ordinal))return Qtt05KhbsPlan(caseId);', plans)
        body = plans[plans.index('private static HtkkDeclarationCasePlan Qtt05KhbsPlan('):]
        body = body[:body.index('\n }\n')]
        self.assertIn('"Validate/KHBS_05_QTT_TNCN_TT80_293.xsd","8f885a0f5c6abc500b1c6268891fdfcc78ffb7b96146ec088908c4c4f579931d",TKhaiThueDbhc,TKhaiThueDbhcSha256', body)
        self.assertIn('WorkbookService,caseId=="05QTT-khbs-decrease-Y2025"?%d:%d,new string[0],new string[0]' % (m.tax_leaf_count(DECREASE) + 4, m.tax_leaf_count(CASES[0]) + 4), body)
        self.assertIn('new HtkkDeclarationCasePlan(caseId,"B9","2.9.3","953","TncnQtt05TT80Nckt293",new string[]{"101","101_11","B9"},"year","12","2025","","01/2025","12/2025",false,', body)
        first = plans[plans.index('case "05QTT-two-employees-Y2025":'):]
        first = first[:first.index(';\n')]
        for pin in ('new string[]{"05-1/BK-TNCN|05-1/BK-QTT-TNCN","05-3/BK-TNCN|05-3/BK-QTT-TNCN"},new string[]{"05|Tờ khai","05-1|05-1/BK-TNCN"},',
                    '"InterfaceTemplates/excel/05_QTT_TNCN_TT80_293.xls","eb948994ab364965b6545cda88294e011605a643a88bb9c5cf5412bdd6008e11"',
                    '"InterfaceTemplates/xml/05_QTT_TNCN_TT80_293.xml","3f8791819f9fe088b939fec20c7d4deeb46931f3e20534dc434a86abd63bd250"'):
            self.assertIn(pin, first)
            self.assertIn(pin, body)
        for case_id in CASES:
            self.assertIn('case "%s":' % case_id, plans)

    def test_probe_lists_and_reader(self):
        formats = (ROOT / 'HtkkNativeCaseFormats.ps1').read_text(encoding='utf-8')
        listed = re.search(r"\$HtkkNtnnKhbsCases=@\((.*?)\)\n", formats).group(1)
        self.assertTrue(set(CASES) <= set(re.findall("'([^']+)'", listed)))
        self.assertIn("'05QTT-khbs-lan2-Y2025'", re.search(r"\$HtkkNtnnKhbsLan2Cases=@\((.*?)\)\n", formats).group(1))
        reader = (ROOT / 'Get-HtkkSafeGuiReferenceResult.ps1').read_text(encoding='utf-8')
        for case_id in CASES:
            self.assertIn("'%s'" % case_id, reader)


if __name__ == '__main__':
    unittest.main()
