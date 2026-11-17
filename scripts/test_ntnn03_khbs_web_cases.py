"""Input contract of the 03/NTNN kê khai bổ sung cases (htkk_ntnn03_khbs_web_cases.py, merged into htkk_ntnn_khbs_web_cases.py).
J1 has KieuKHBS 3 like I9: its B files carry PL01_KHBS / PL01_1_KHBS after no annex, and its rounds run "Tổng hợp KHBS". Its
original import clears every rate [9], so each import is completed by the rates typed again (KhbsImportTick). Synthetic checks only;
the reviewed producer files stay private (only their sizes and SHA-256 are pinned). Byte-level checks run on a second module
instance pinned to synthetic in-memory files (ntnn_khbs_test_support.py)."""
import importlib.util
import pathlib
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).parent


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


m = load('htkk_ntnn_khbs_web_cases_ntnn03', 'htkk_ntnn_khbs_web_cases.py')
ntnn03 = load('htkk_ntnn03_khbs_web_cases_test', 'htkk_ntnn03_khbs_web_cases.py')
support = load('ntnn_khbs_test_support_ntnn03', 'ntnn_khbs_test_support.py')
sm = support.pin(load('htkk_ntnn_khbs_web_cases_ntnn03_pinned', 'htkk_ntnn_khbs_web_cases.py'))
registry = load('htkk_native_cases_ntnn03', 'htkk_native_cases.py')
baseline = load('htkk_oracle_baselines_ntnn03', 'generate-htkk-oracle-baselines.py')
CASES = ('03NTNN-khbs-increase-M09-2026', '03NTNN-khbs-lan2-M09-2026', '03NTNN-khbs-decrease-M09-2026')
INCREASE, LAN2, DECREASE = CASES


def manifest(case_id, module):
    c = module.CASES[case_id]
    value = dict(module.manifest_fields(case_id), sourceCommit='0' * 40, producerSha256='1' * 64, bytes=c['web'][0], xmlSha256=c['web'][1],
                 originalBytes=c['original'][0], originalXmlSha256=c['original'][1])
    if c['prior']:
        value.update(priorBytes=c['prior'][0], priorXmlSha256=c['prior'][1])
    return value


class Ntnn03KhbsWebCases(unittest.TestCase):
    def test_three_cases_merged_with_their_own_producer_menu_and_period(self):
        self.assertEqual(m.NTNN03_CASES, CASES)
        self.assertEqual(set(ntnn03.CASES), set(CASES))
        self.assertFalse((set(m.NTNN_CASES) | set(m.KK05_CASES) | set(m.CNKD_CASES) | set(m.QTT02_CASES) | set(m.QTT05_CASES) | set(m.TNDN03_CASES)) & set(CASES))
        self.assertEqual(m.MENUS['J1'], ('840', '3.0.8'))
        self.assertEqual(m.PERIODS['J1'], ('M', '09/2026', '01/09/2026', '30/09/2026'))
        for case_id in CASES:
            c = m.CASES[case_id]
            self.assertEqual(m.producer(case_id), 'scripts/generate-htkk-web-ntnn03-khbs-reference.mjs')
            self.assertEqual(m.manifest_fields(case_id)['exporter'], 'lib/htkk-ntnn01-khbs.ts')
            self.assertEqual(m.manifest_fields(case_id)['htkkVersion'], '5.8.2')
            self.assertEqual(m.names(case_id), (m.ORIGINAL_NAME,) + ((m.PRIOR_NAME,) if case_id == LAN2 else ()) + (m.WEB_NAME, m.MANIFEST_NAME))
            self.assertEqual(m.input_mode(case_id), 'khbs-web-xml-import-tick-reexport')
            self.assertEqual(c['annexParts'], ())
            self.assertEqual(c['khbsParts'], ('PL01_KHBS', 'PL01_1_KHBS'))
            self.assertTrue(m.khbs_summary(case_id))
            self.assertEqual(m.validate_manifest(manifest(case_id, m))['caseId'], case_id)
            self.assertEqual(set(c['expected']), {'rows', 'subitems', 'ct10', 'ct3a_1', 'ct3a_2', 'ct3b'})
            # Kỳ 09/2026 is due 20/10/2026 (GetHanNopToKhai, kỳ tháng): 24 days to ngày lập 13/11/2026; (11) is tiểu mục 1052.
            self.assertEqual((c['expected']['ct3a_1'], c['expected']['ct3a_2']), ('2026-11-13', '24'))
            self.assertEqual([s[0] for s in c['expected']['subitems']], ['1052'])
            self.assertEqual(c['expected']['rows'][-1], '(11)')
            self.assertEqual(m.tax_leaf_count(case_id), 168)
            self.assertEqual(m.catalogue_texts(case_id, [], frozenset()), ntnn03.CATALOGUE_TEXTS)
        for text in ('03/NTNN', '(11)', 'Thuế TNDN phải nộp', '(11) - Thuế TNDN phải nộp', '(9) - Tỷ lệ % thuế TNDN'):
            self.assertIn(text, ntnn03.CATALOGUE_TEXTS)
        # No retention exception for the key: the web files carry the key trimmed as HTKK exports it (run 44101960535).
        self.assertFalse(any('keyTrailingTrim' in c for c in m.CASES.values()))
        self.assertEqual([m.CASES[c]['web'][0] for c in CASES], [5933, 5936, 5968])
        self.assertEqual(m.CASES[LAN2]['prior'], m.CASES[INCREASE]['web'])
        self.assertEqual(len({m.CASES[c]['original'] for c in CASES}), 1)

    def test_registered_as_observation_tick_cases_with_summary(self):
        for case_id in CASES:
            row = registry.CASES[case_id]
            self.assertIs(row['releaseGate'], False)
            self.assertEqual(registry.htkk_version(case_id), '5.8.2')
            self.assertEqual(registry.driver(case_id), 'declaration-amendment-khbs-inspect')
            self.assertEqual(row['format'], m.manifest_fields(case_id)['format'])
            self.assertEqual(row['unit']['amendmentOrder'], m.CASES[case_id]['soLan'])
            self.assertEqual((row['unit']['menuId'], row['unit']['adapterVersion'], row['unit']['periodType'], row['unit']['periodValue']), ('J1', '3.0.8', 'month', '09/2026'))
            self.assertEqual(row['unit']['annexes'], [])
        self.assertTrue(set(CASES) <= set(registry.NTNN_KHBS_CASES))
        self.assertTrue(set(CASES) <= set(registry.NTNN_KHBS_TICK_CASES))
        self.assertFalse(set(CASES) & set(registry.NTNN_KHBS_NO_SUMMARY_CASES))

    def test_pinned_synthetic_files_validate(self):
        for case_id in CASES:
            files = support.files(sm, case_id)
            self.assertEqual(sm.validate_files(files, manifest(case_id, sm))['amendmentLeafTarget'], sm.CASES[case_id]['leafTarget'])
            self.assertNotIn(b'<PLuc>', files[sm.ORIGINAL_NAME])
        with self.assertRaises(m.NtnnKhbsWebCaseError):
            m.validate_xml(support.files(sm, INCREASE)[m.WEB_NAME], INCREASE, 'web')


class Ntnn03KhbsDriverWiring(unittest.TestCase):
    def test_case_plans_use_the_j1_plan_with_the_khbs_schema_web_leaf_counts_and_rate_edits(self):
        plans = (ROOT / 'HtkkDeclarationCasePlans.cs').read_text(encoding='utf-8')
        ids = set(re.findall('"([^"]+)"', re.search(r'KhbsCaseIds=new string\[\]\{(.*?)\};', plans, re.S).group(1)))
        self.assertTrue(set(CASES) <= ids)
        self.assertRegex(plans, r'KhbsSoLan\(string caseId\)\{return [^;]*caseId=="03NTNN-khbs-lan2-M09-2026"[^;]*\?2:')
        self.assertIn('if(caseId.StartsWith("03NTNN-khbs-",StringComparison.Ordinal))return Ntnn03KhbsPlan(caseId);', plans)
        body = plans[plans.index('private static HtkkDeclarationCasePlan Ntnn03KhbsPlan('):]
        body = body[:body.index('\n }\n')]
        self.assertIn('"Validate/KHBS_03_NTNN_TT80_308.xsd","c99ad92ba68a08a8e319e52e6c617970d978882885bd746be01a67f8425d7272"', body)
        self.assertIn('WorkbookService,%d,new string[0],new string[0]' % (m.tax_leaf_count(INCREASE) + 4), body)
        self.assertIn('new HtkkDeclarationCasePlan(caseId,"J1","3.0.8","840","Ntnn03TT80Nckt308",new string[]{"101","101_8","J1"},"month","18","2026","09","01/09/2026","30/09/2026",false,', body)
        # The lần đầu J1 plan (03NTNN-no-rate-M10-2026) and the KHBS plan share the workbook and layout pins.
        first = plans[plans.index('case "03NTNN-no-rate-M10-2026":'):]
        first = first[:first.index(';\n')]
        for pin in ('"InterfaceTemplates/excel/03_NTNN_TT80_308.xls","ef4451f19a8a74ad667add7fd580ac83be149f7d35e65bbbe12aa42ccad11142"', '"InterfaceTemplates/xml/03_NTNN_TT80_308.xml","41c8c6c92a684485aff87790739958948c94bf966cc5e56b6150a17f6beac550"'):
            self.assertIn(pin, first)
            self.assertIn(pin, body)
        for case_id in CASES:
            self.assertIn('case "%s":' % case_id, plans)
        # Every round: the two rates of the case files typed again after the import, then the summary.
        tick = plans[plans.index('private static HtkkDeclarationTickPlan Ntnn03KhbsRateTick('):]
        tick = tick[:tick.index('\n }\n')]
        for case_id in CASES:
            self.assertIn('"%s"' % case_id, tick)
        self.assertIn('new HtkkDeclarationTickPlan(new string[]{"number|BU34|5","number|BU35|2"},new string[0],new string[0],new string[0],HtkkOracleBaseline.Ntnn03KhbsRateMethodPins());', tick)
        self.assertIn(':Ntnn03KhbsRateTick(caseId);}', plans)

    def test_rate_edit_pins_are_the_reviewed_editor_path_bodies(self):
        data = baseline.load()
        self.assertEqual([x for x in data['versions']['5.8.1']['methods'] if x['id'].startswith(baseline.NTNN03_PREFIX)], [])
        for version in ('5.8.2', '5.8.3'):
            methods = {x['id']: x for x in data['versions'][version]['methods']}
            for name, twin in (('grid-cellchange', 'grid-cellchange'), ('enter-cell', 'enter-cell'), ('dowork-cellchange', 'dowork-cellchange')):
                x, y = methods['ntnn03-582-' + name], methods['gtgt04tt89-582-' + twin]
                self.assertEqual((x['assembly'], x['type'], x['method'], x['token'], x['ilBytes'], x['ilSha256']), (y['assembly'], y['type'], y['method'], y['token'], y['ilBytes'], y['ilSha256']))
                self.assertEqual(x['status'], 'added-reviewed')
        cs = (ROOT / 'HtkkOracleBaseline.cs').read_text(encoding='utf-8')
        self.assertIn('internal static string[] Ntnn03KhbsRateMethodPins(){if(Ntnn03[Current].Length==0)throw new InvalidOperationException("HTKK_ORACLE_NTNN03_UNPINNED");', cs)

    @unittest.skipUnless(shutil.which('mcs') and shutil.which('mono'), 'local CLR plan smoke test needs mono')
    def test_compiled_rate_edits_need_the_5_8_2_pins(self):
        program = ('using System;class P{static void Main(string[] a){HtkkOracleBaseline.Select(a[0]);'
                   'foreach(string id in new string[]{"' + '","'.join(CASES) + '"}){'
                   'Console.WriteLine(HtkkDeclarationCasePlans.KhbsSoLan(id)+" "+HtkkDeclarationCasePlans.KhbsSummary(id)+" "+(HtkkDeclarationCasePlans.Find(id)!=null));'
                   'try{HtkkDeclarationTickPlan t=HtkkDeclarationCasePlans.KhbsImportTick(id);Console.WriteLine(t.Edits.Length+" "+t.Ticks.Length+" "+t.Unticked.Length+" "+t.Readbacks.Length+" "+t.MethodPins.Length);}'
                   'catch(InvalidOperationException e){Console.WriteLine(e.Message);}}'
                   'Console.WriteLine(HtkkDeclarationCasePlans.KhbsImportTick("01NTNN-khbs-grossup-lan1-M09-2026")==null);}}')
        with tempfile.TemporaryDirectory() as directory:
            folder = pathlib.Path(directory); (folder / 'P.cs').write_text(program)
            subprocess.run(['mcs', '-langversion:ISO-2', '-warn:0', '-out:' + str(folder / 'p.exe'), str(folder / 'P.cs'), str(ROOT / 'HtkkOracleBaseline.cs'), str(ROOT / 'HtkkDeclarationCasePlans.cs')], check=True, capture_output=True)
            new = subprocess.run(['mono', str(folder / 'p.exe'), '5.8.2'], check=True, capture_output=True, text=True).stdout.split('\n')
            newer = subprocess.run(['mono', str(folder / 'p.exe'), '5.8.3'], check=True, capture_output=True, text=True).stdout.split('\n')
            old = subprocess.run(['mono', str(folder / 'p.exe'), '5.8.1'], capture_output=True, text=True).stdout.split('\n')
        expected = ['1 True True', '2 0 0 0 3', '2 True True', '2 0 0 0 3', '1 True True', '2 0 0 0 3', 'True']
        self.assertEqual(new[:7], expected)
        self.assertEqual(newer[:7], expected)
        # 5.8.1 carries no rate-edit pins: the plan refuses to run there.
        self.assertEqual(old[1], 'HTKK_ORACLE_NTNN03_UNPINNED')

    def test_probe_lists(self):
        formats = (ROOT / 'HtkkNativeCaseFormats.ps1').read_text(encoding='utf-8')
        listed = re.search(r"\$HtkkNtnnKhbsCases=@\((.*?)\)\n", formats).group(1)
        self.assertTrue(set(CASES) <= set(re.findall("'([^']+)'", listed)))
        self.assertEqual(re.findall("'(03NTNN-[^']+)'", re.search(r"\$HtkkNtnnKhbsLan2Cases=@\((.*?)\)\n", formats).group(1)), [LAN2])
        self.assertEqual(set(re.findall("'(03NTNN-[^']+)'", re.search(r"\$HtkkNtnnKhbsTickCases=@\((.*?)\)\n", formats).group(1))), set(CASES))
        registry_text = (ROOT / 'htkk-native-automation-registry.json').read_text(encoding='utf-8')
        reader = (ROOT / 'Get-HtkkSafeGuiReferenceResult.ps1').read_text(encoding='utf-8')
        for case_id in CASES:
            self.assertIn('"%s"' % case_id, registry_text)
            self.assertIn("'%s'" % case_id, reader)


if __name__ == '__main__':
    unittest.main()
