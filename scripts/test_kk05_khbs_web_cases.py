"""Input contract of the 05/KK-TNCN kê khai bổ sung cases (htkk_kk05_khbs_web_cases.py, merged into htkk_ntnn_khbs_web_cases.py).
Synthetic checks only; the reviewed producer files stay private (only their sizes and SHA-256 are pinned). Byte-level checks run on
a second module instance pinned to synthetic in-memory files (ntnn_khbs_test_support.py)."""
import importlib.util
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).parent


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


m = load('htkk_ntnn_khbs_web_cases_kk05', 'htkk_ntnn_khbs_web_cases.py')
kk05 = load('htkk_kk05_khbs_web_cases_test', 'htkk_kk05_khbs_web_cases.py')
support = load('ntnn_khbs_test_support_kk05', 'ntnn_khbs_test_support.py')
sm = support.pin(load('htkk_ntnn_khbs_web_cases_kk05_pinned', 'htkk_ntnn_khbs_web_cases.py'))
registry = load('htkk_native_cases_kk05', 'htkk_native_cases.py')
CASES = ('05KK-khbs-increase-Q3-2026', '05KK-khbs-lan2-Q3-2026', '05KK-khbs-decrease-Q3-2026', '05KK-TT89-khbs-increase-Q4-2026', '05KK-khbs-increase-M03-2026', '05KK-PBT-khbs-Q3-2026')
MONTH = '05KK-khbs-increase-M03-2026'
PBT = '05KK-PBT-khbs-Q3-2026'


def manifest(case_id, module):
    c = module.CASES[case_id]
    value = dict(module.manifest_fields(case_id), sourceCommit='0' * 40, producerSha256='1' * 64, bytes=c['web'][0], xmlSha256=c['web'][1],
                 originalBytes=c['original'][0], originalXmlSha256=c['original'][1])
    if c['prior']:
        value.update(priorBytes=c['prior'][0], priorXmlSha256=c['prior'][1])
    return value


class Kk05KhbsWebCases(unittest.TestCase):
    def test_five_cases_merged_with_their_own_producer_menus_and_periods(self):
        self.assertEqual(m.KK05_CASES, CASES)
        self.assertEqual(set(kk05.CASES), set(CASES))
        self.assertFalse(set(m.NTNN_CASES) & set(CASES))
        self.assertEqual((m.MENUS['L7'], m.MENUS['Z8']), (('864', '2.9.3'), ('2036', '3.0.9')))
        self.assertEqual(m.PERIODS['L7'], ('Q', '3/2026', '01/07/2026', '30/09/2026'))
        self.assertEqual(m.PERIODS['Z8'], ('Q', '4/2026', '01/10/2026', '31/12/2026'))
        # The kỳ tháng case carries its own period; every other case takes its menu's.
        self.assertEqual(m.period_of(m.CASES[MONTH]), ('M', '03/2026', '01/03/2026', '31/03/2026'))
        self.assertEqual({m.period_of(m.CASES[c]) for c in CASES if c != MONTH and m.CASES[c]['menuId'] == 'L7'}, {m.PERIODS['L7']})
        for case_id in CASES:
            c = m.CASES[case_id]
            self.assertEqual(m.producer(case_id), 'scripts/generate-htkk-web-kk05-khbs-reference.mjs')
            self.assertEqual(m.manifest_fields(case_id)['exporter'], 'lib/htkk-kk05-khbs.ts')
            self.assertEqual(m.names(case_id), (m.ORIGINAL_NAME,) + ((m.PRIOR_NAME,) if c['soLan'] == 2 else ()) + (m.WEB_NAME, m.MANIFEST_NAME))
            self.assertEqual(m.input_mode(case_id), 'khbs-web-xml-import-tick-reexport' if case_id == PBT else 'khbs-web-xml-import-reexport')
            self.assertEqual(c['annexParts'], ('PLuc_05_1_PBT_KK_TNCN',) if case_id == PBT else ())
            self.assertEqual(m.validate_manifest(manifest(case_id, m))['caseId'], case_id)
        # Lần 2 starts from the lần-1 file of the increase case; every plain L7 case from the same lần đầu.
        self.assertEqual(m.CASES['05KK-khbs-lan2-Q3-2026']['prior'], m.CASES['05KK-khbs-increase-Q3-2026']['web'])
        self.assertEqual(len({m.CASES[c]['original'] for c in CASES if m.CASES[c]['menuId'] == 'L7' and c not in (PBT, MONTH)}), 1)
        # The NTNN cases keep their own producer and input modes.
        self.assertEqual({m.producer(c) for c in m.NTNN_CASES}, {'scripts/generate-htkk-web-ntnn-khbs-reference.mjs'})
        self.assertEqual({m.input_mode(c) for c in m.NTNN_CASES}, {'khbs-web-xml-import-reexport', 'khbs-original-entry-export'})

    def test_registered_as_observation_cases_of_the_khbs_declaration_mode(self):
        for case_id in CASES:
            row = registry.CASES[case_id]
            self.assertIs(row['releaseGate'], False)
            self.assertEqual(registry.htkk_version(case_id), '5.8.2')
            self.assertEqual(registry.driver(case_id), 'declaration-amendment-khbs-inspect')
            self.assertEqual(row['format'], m.manifest_fields(case_id)['format'])
            self.assertEqual(row['unit']['amendmentOrder'], m.CASES[case_id]['soLan'])
            self.assertEqual((row['unit']['periodType'], row['unit']['periodValue']), ('month', '03/2026') if case_id == MONTH else ('quarter', '4/2026' if row['unit']['menuId'] == 'Z8' else '3/2026'))
            self.assertEqual(row['unit']['annexes'], ['01-1'] if case_id == PBT else [])
        self.assertTrue(set(CASES) <= set(registry.NTNN_KHBS_CASES))
        self.assertEqual([c for c in registry.NTNN_KHBS_TICK_CASES if c in CASES], [PBT])
        self.assertNotIn(PBT, registry.DECLARATION_TICK_CASES)

    def test_pinned_synthetic_files_validate_and_the_annex_order_is_enforced(self):
        for case_id in CASES:
            files = support.files(sm, case_id)
            self.assertEqual(sm.validate_files(files, manifest(case_id, sm))['amendmentLeafTarget'], sm.CASES[case_id]['leafTarget'])
        # A PBT B file without its annex, or with the annex after the KHBS fragments, is refused (pins switched off for the check).
        body = support.files(sm, PBT)[sm.WEB_NAME].decode('utf-8')
        annex = re.search('<PLuc_05_1_PBT_KK_TNCN>.*?</PLuc_05_1_PBT_KK_TNCN>', body).group(0)
        for changed in (body.replace(annex, ''), body.replace(annex, '').replace('</PLuc>', annex + '</PLuc>')):
            raw = changed.encode('utf-8')
            saved = sm.CASES[PBT]['web']
            try:
                sm.CASES[PBT]['web'] = (len(raw), __import__('hashlib').sha256(raw).hexdigest())
                with self.assertRaises(sm.NtnnKhbsWebCaseError) as error:
                    sm.validate_xml(raw, PBT, 'web')
                self.assertEqual(error.exception.code, 'AMENDMENT')
            finally:
                sm.CASES[PBT]['web'] = saved
        # The real pins refuse every synthetic file.
        with self.assertRaises(m.NtnnKhbsWebCaseError):
            m.validate_xml(support.files(sm, PBT)[m.WEB_NAME], PBT, 'web')


class Kk05KhbsDriverWiring(unittest.TestCase):
    def test_case_plans_name_every_case_with_the_web_leaf_count_and_the_khbs_schema(self):
        plans = (ROOT / 'HtkkDeclarationCasePlans.cs').read_text(encoding='utf-8')
        ids = re.search(r'KhbsCaseIds=new string\[\]\{(.*?)\};', plans, re.S).group(1)
        self.assertEqual(set(re.findall('"([^"]+)"', ids)), set(registry.NTNN_KHBS_CASES))
        self.assertRegex(plans, r'KhbsSoLan\(string caseId\)\{return [^;]*caseId=="05KK-khbs-lan2-Q3-2026"[^;]*\?2:')
        counts = re.search(r'int leaves=caseId=="05KK-khbs-increase-Q3-2026"\|\|caseId=="05KK-khbs-increase-M03-2026"\?(\d+):caseId=="05KK-TT89-khbs-increase-Q4-2026"\?(\d+):caseId=="05KK-PBT-khbs-Q3-2026"\?(\d+):(\d+);', plans)
        self.assertIsNotNone(counts)
        expected = [m.tax_leaf_count(c) + 4 for c in ('05KK-khbs-increase-Q3-2026', '05KK-TT89-khbs-increase-Q4-2026', PBT)]
        self.assertEqual([int(x) for x in counts.groups()[:3]], expected)
        self.assertEqual(m.tax_leaf_count(MONTH) + 4, int(counts.group(1)))
        self.assertIn('month?"month":"quarter","19","2026",month?"03":"3",month?"01/03/2026":"01/07/2026",month?"31/03/2026":"30/09/2026"', plans)
        self.assertEqual({m.tax_leaf_count(c) + 4 for c in ('05KK-khbs-lan2-Q3-2026', '05KK-khbs-decrease-Q3-2026')}, {int(counts.group(4))})
        self.assertIn('"Validate/KHBS_05_KK_TNCN_TT80_293.xsd","91a2d625d1ddeaf5fe71fb5ca0413d25d063d3adb99e9b975e322d95a56d8ec4"', plans)
        self.assertIn('"Validate/KHBS_05_KK_TNCN_TT89_309.xsd","619a2ecf3228d80742e9dbea5c3939308f74fea55a94073e33bbc7efb23bdf97"', plans)
        self.assertIn('internal static HtkkDeclarationTickPlan KhbsImportTick(string caseId){return caseId=="05KK-PBT-khbs-Q3-2026"?ImportTick("05KK-PBT-two-provinces-Q3-2026"):', plans)

    def test_driver_runs_the_tick_plan_in_every_khbs_round_and_resets_it(self):
        web = (ROOT / 'HtkkDeclarationWebImport.cs').read_text(encoding='utf-8')
        khbs = (ROOT / 'HtkkDeclarationKhbs.cs').read_text(encoding='utf-8')
        self.assertIn('declarationTickPlan=DeclarationKhbsMode()?HtkkDeclarationCasePlans.KhbsImportTick(declarationPlan.CaseId):HtkkDeclarationCasePlans.ImportTick(declarationPlan.CaseId);', web)
        reset = khbs[khbs.index('private void BeginDeclarationKhbsRound()'):]
        for field in ('declarationTickPlannedCount=0', 'declarationTickActionCount=0', 'declarationTickMethodPinsMatched=false', 'declarationTickEditsMatched=false', 'declarationTickTicksMatched=false'):
            self.assertIn(field, reset)

    def test_probe_lists_and_success_predicate(self):
        probe = (ROOT / 'probe-htkk-windows.ps1').read_text(encoding='utf-8')
        formats = (ROOT / 'HtkkNativeCaseFormats.ps1').read_text(encoding='utf-8')
        self.assertIn("$HtkkNtnnKhbsLan2Cases=@('01NTNN-khbs-lan2-M09-2026','05KK-khbs-lan2-Q3-2026','01CNKD-khbs-lan2-Q3-2026','02QTT-khbs-lan2-Y2025','05QTT-khbs-lan2-Y2025')", formats)
        self.assertIn("$HtkkNtnnKhbsTickCases=@('05KK-PBT-khbs-Q3-2026','01CNKD-PL01-khbs-Q3-2026')", formats)
        self.assertIn('$khbsLan2=$env:EXPECTED_WEB_CASE_ID -cin $HtkkNtnnKhbsLan2Cases', probe)
        self.assertIn('$khbsTickCase=$env:EXPECTED_WEB_CASE_ID -cin $HtkkNtnnKhbsTickCases', probe)
        self.assertIn('if($khbsTickCase){$matched=$matched -and $lastGui.declarationTickMethodPinsMatched', probe)
        self.assertIn("$declarationTickCase=$gui.webCaseId -cin $(if($declarationKhbs){$HtkkNtnnKhbsTickCases}else{$HtkkDeclarationTickCases})", probe)


if __name__ == '__main__':
    unittest.main()
