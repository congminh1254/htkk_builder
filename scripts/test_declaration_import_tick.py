"""Offline contracts for native-case mode web-xml-import-tick-reexport of the declaration driver.

U5 01/CNKD TT50 3.1.0 (HTKK 5.8.2 only): the XML carries no chonGiamThue (AJ) / ct17_soThueGiam (CD), so after
the original "Nhap tu XML" the NQ 43 reduction is lost (runs 43127371885, 43130173107: cell mask 40 = AE291/AE293).
The case keeps the original import and then performs fixed original actions: edits of L291/L292 through the original
editor (CellChange_0 -> SetCacDongCon fills the child-row keys) and SPACE on AJ291/AJ292 (ButtonClick_0 ->
daySangPLGiamThue rebuilds PL 01 and CD). Passing these tests is never native evidence.
"""
import copy, importlib.util, json, pathlib, re, shutil, subprocess, tempfile, unittest
from decimal import Decimal

ROOT = pathlib.Path(__file__).parent


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / file); value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value); return value


registry = load('tick_registry_test', 'htkk_native_cases.py')
hkd = load('tick_hkd_design_test', 'htkk_hkd_web_cases.py')
generator = load('tick_baseline_generator_test', 'generate-htkk-oracle-baselines.py')
automation = json.loads((ROOT / 'htkk-native-automation-registry.json').read_text())
BASELINES = json.loads((ROOT / 'htkk-oracle-baselines.json').read_text(encoding='utf-8'))
PLANS = (ROOT / 'HtkkDeclarationCasePlans.cs').read_text(encoding='utf-8')
ENTRY = (ROOT / 'HtkkDeclarationOriginalEntry.cs').read_text(encoding='utf-8')
IMPORT = (ROOT / 'HtkkDeclarationWebImport.cs').read_text(encoding='utf-8')
PROBE = (ROOT / 'probe-htkk-windows.ps1').read_text(encoding='utf-8')
TICK = ENTRY[ENTRY.index(' // ==== Native-case mode web-xml-import-tick-reexport'):]
CODE = re.sub(r'//[^\n]*', '', TICK)
CASE = '01CNKD-TT50-310-pl01-three-groups-Q3-2026'
# U5 3.1.0 with PL 03 (Mẫu 03): the same mode with edits only (capNhatToKhai writes the thuế bù CF; nothing is ticked).
PL03 = '01CNKD-TT50-310-pl03-two-groups-Q3-2026'
MODE = 'declaration-web-import-inspect'
FIRST_ROW = 291  # 01_CNKD_HKD_TT50_310.xml table_1 DataLocationTemplateRowStart


def tick_block(case_id=CASE):
    start = PLANS.index(' internal static HtkkDeclarationTickPlan ImportTick(string caseId){')
    body = PLANS[start:PLANS.index('\n }\n', start)]
    if case_id == PL03:
        head = '  if(caseId=="' + PL03 + '")return new HtkkDeclarationTickPlan('
        return body[body.index(head):body.index('  if(caseId!="' + CASE + '")return null;')]
    return body[body.index('  if(caseId!="' + CASE + '")return null;'):]


def string_array(block, ordinal):
    arrays = re.findall(r'new string\[\]\{(.*?)\}', block, re.S)
    return re.findall(r'"((?:[^"\\]|\\.)*)"', arrays[ordinal])


def plan_block(case_id):
    return re.search(r'case "' + re.escape(case_id) + r'":return new HtkkDeclarationCasePlan\((.*?)\);\n', PLANS, re.S).group(1)


class Registration(unittest.TestCase):
    def test_u5_310_is_the_only_tick_case_non_gating_on_the_5_8_2_oracle(self):
        self.assertEqual(registry.DECLARATION_TICK_CASES, (CASE, PL03))
        self.assertEqual(registry.input_mode(PL03), registry.IMPORT_TICK_MODE); self.assertEqual(registry.htkk_version(PL03), '5.8.2')
        self.assertIs(registry.CASES[PL03]['releaseGate'], False); self.assertEqual(registry.CASES[PL03]['adapterId'], '01-cnkd-hkd-3.1.0-pl03')
        self.assertEqual(registry.input_mode(CASE), registry.IMPORT_TICK_MODE)
        self.assertEqual(registry.IMPORT_TICK_MODE, 'web-xml-import-tick-reexport')
        self.assertEqual(registry.driver(CASE), MODE)
        self.assertEqual(registry.htkk_version(CASE), '5.8.2')
        self.assertIs(registry.CASES[CASE]['releaseGate'], False)
        self.assertNotIn(CASE, registry.DECLARATION_ENTRY_CASES)
        formats = (ROOT / 'HtkkNativeCaseFormats.ps1').read_text()
        self.assertIn("$HtkkDeclarationTickCases=@('" + CASE + "','" + PL03 + "')", formats)
        # Same adapter, producer case and branches as before: the web input does not change.
        self.assertEqual(registry.CASES[CASE]['adapterId'], '01-cnkd-hkd-3.1.0-pl01')
        self.assertEqual(registry.CASES[CASE]['producerCase'], 'cnkd01-310-pl01-three-groups-q3-2026')


class TickPlan(unittest.TestCase):
    def test_edits_ticks_and_clear_cells_follow_the_design_case(self):
        block = tick_block()
        self.assertIn('if(caseId!="' + CASE + '")return null;', block)
        edits, ticks, unticked, readbacks = (string_array(block, i) for i in range(4))
        rows = hkd.CASES[CASE]['locations'][0]['rows']
        self.assertEqual(len(hkd.CASES[CASE]['locations']), 1)
        # One real change of [11] on every reduced row (0, then the web value): CellChange_0 re-derives that row's AJ lock
        # (release run 43136692872: AJ293, never edited, was not an open checkbox after the import, code 3).
        reduced = [(FIRST_ROW + i, r) for i, r in enumerate(rows) if r.get('reduce')]
        self.assertEqual(edits, [e for row, r in reduced for e in ('number|L%d|0' % row, 'number|L%d|%s' % (row, r['ct11']))])
        for _, r in reduced:
            self.assertEqual(r['ct15'], r['ct11'])  # column L also copies L into U
        # Sheet order, each tick after its row's edits.
        self.assertEqual(ticks, ['AJ%d' % row for row, _ in reduced])
        self.assertEqual(unticked, ['AJ%d' % (FIRST_ROW + i) for i, r in enumerate(rows) if not r.get('reduce')])
        self.assertEqual(ticks, ['AJ291', 'AJ292'])
        # HTKK 5.8.2 daySangPLGiamThue does not advance past an unticked row (run 43138236726): every ticked row comes
        # before every clear row in the design case, or HTKK leaves CD = 0 on a ticked row.
        flags = [bool(r.get('reduce')) for r in rows]
        self.assertEqual(flags, sorted(flags, reverse=True))
        code = hkd.CASES[CASE]['locations'][0]['code']
        self.assertEqual(readbacks, ['BN%d|%s' % (FIRST_ROW + i, code) for i in range(3)] + ['CA%d|%s' % (FIRST_ROW + i, hkd.FAKE_MST) for i in range(3)])
        self.assertIn('HtkkOracleBaseline.TickMethodPins()', block)
        # Nothing is typed into a computed, key or reduction cell; only L is edited and only AJ is ticked.
        for edit in edits:
            self.assertRegex(edit.split('|')[1], r'\AL[0-9]+\Z')

    def test_sheet_checks_after_the_ticks_are_the_decimal_oracle(self):
        expected = hkd.expected(CASE)
        checks = {c.split('|')[0] + '|' + c.split('|')[1]: c.split('|')[2] for c in string_array(plan_block(CASE), 3)}
        rows = hkd.CASES[CASE]['locations'][0]['rows']
        for i, r in enumerate(rows):
            ce = (Decimal(r['ct15']) - Decimal(r['ct16'])) * Decimal(hkd.GROUPS[r['group']][1])
            cd = ce * hkd.PL01_RATE if r.get('reduce') else Decimal(0)
            self.assertEqual(checks['01|U%d' % (FIRST_ROW + i)], r['ct15'])
            self.assertEqual(checks['01|AE%d' % (FIRST_ROW + i)], expected['ct17_soThue'][i])
            self.assertEqual(checks['01|CD%d' % (FIRST_ROW + i)], hkd.display(cd))
        self.assertEqual(expected['soThueTNCN_phaiNop'], [checks['01-4|G20'], checks['01-4|G21']])
        self.assertEqual(expected['soThueTNCN_duocGiam'], [checks['01-4|H20'], checks['01-4|H21']])
        self.assertEqual(len(checks), 13)


class Pl03Plan(unittest.TestCase):
    def test_pl03_edits_only_and_sheet_checks_are_the_decimal_oracle(self):
        block = tick_block(PL03)
        edits, ticks, unticked, readbacks = string_array(block, 0), [], [], string_array(block, 1)
        self.assertIn('new string[0],new string[0]', block)
        rows = hkd.CASES[PL03]['locations'][0]['rows']
        self.assertEqual(edits, ['number|L%d|0' % FIRST_ROW, 'number|L%d|%s' % (FIRST_ROW, rows[0]['ct11'])])
        self.assertTrue(all(not r.get('reduce') for r in rows))
        code = hkd.CASES[PL03]['locations'][0]['code']
        self.assertEqual(readbacks, ['BN%d|%s' % (FIRST_ROW + i, code) for i in range(2)] + ['CA%d|%s' % (FIRST_ROW + i, hkd.FAKE_MST) for i in range(2)])
        self.assertIn('HtkkOracleBaseline.TickMethodPins()', block)
        # The plan may carry no tick, never no edit; a plan without ticks goes straight to the read-back.
        self.assertIn('if(edits.Length<1||edits.Length>4||ticks.Length>4||', PLANS)
        self.assertIn('if(declarationTickPlan.Ticks.Length==0){declarationPhase="tick-inspect";declarationTickClock=Stopwatch.StartNew();}else declarationPhase="tick-ticks";', TICK)
        expected = hkd.expected(PL03)
        checks = {c.split('|')[0] + '|' + c.split('|')[1]: c.split('|')[2] for c in string_array(plan_block(PL03), 3)}
        for i, r in enumerate(rows):
            ce = (Decimal(r['ct15']) - Decimal(r['ct16'])) * Decimal(hkd.GROUPS[r['group']][1])
            cf = hkd.pl03_cf(hkd.CASES[PL03], hkd.CASES[PL03]['locations'][0], r)
            self.assertEqual(checks['01|U%d' % (FIRST_ROW + i)], r['ct15'])
            self.assertEqual(checks['01|CF%d' % (FIRST_ROW + i)], hkd.display(cf)); self.assertEqual(checks['01|CD%d' % (FIRST_ROW + i)], '0')
            self.assertEqual(checks['01|AE%d' % (FIRST_ROW + i)], expected['ct17_soThue'][i]); self.assertEqual(hkd.display(ce + cf), expected['ct17_soThue'][i])
        # PL 03 mục A row 22 only (G = H, XLS H22 = G22; one row per section, HTKK 5.8.2 cannot export two); the totals row
        # is checked in the XML.
        self.assertEqual(checks['01-5|G22'], expected['soThueTNCN_duocGiam'][0]); self.assertEqual(checks['01-5|H22'], expected['soThueTNCN_phaiNop'][0])
        self.assertEqual([checks['01|CF%d' % FIRST_ROW], checks['01|CF%d' % (FIRST_ROW + 1)]], ['0', '300000'])
        self.assertNotIn('01-5|G23', checks); self.assertEqual(len(checks), 10)
        self.assertIn('new string[]{"PL 03 43/2026/QH16"},new string[]{"01|Tờ khai","01-5|PL 03 43/2026/QH16"}', plan_block(PL03))

    @unittest.skipUnless(shutil.which('mcs') and shutil.which('mono'), 'local CLR plan smoke test needs mono')
    def test_compiled_pl03_plan_has_no_tick(self):
        program = ('using System;class P{static void Main(){HtkkOracleBaseline.Select("5.8.2");HtkkDeclarationTickPlan t=HtkkDeclarationCasePlans.ImportTick("' + PL03 + '");'
                   'Console.WriteLine(t.Edits.Length+" "+t.Ticks.Length+" "+t.Unticked.Length+" "+t.Readbacks.Length+" "+t.MethodPins.Length+" "+(HtkkDeclarationCasePlans.Find("' + PL03 + '")!=null));}}')
        with tempfile.TemporaryDirectory() as directory:
            folder = pathlib.Path(directory); (folder / 'P.cs').write_text(program)
            subprocess.run(['mcs', '-langversion:ISO-2', '-warn:0', '-out:' + str(folder / 'p.exe'), str(folder / 'P.cs'), str(ROOT / 'HtkkOracleBaseline.cs'), str(ROOT / 'HtkkDeclarationCasePlans.cs')], check=True, capture_output=True)
            out = subprocess.run(['mono', str(folder / 'p.exe')], check=True, capture_output=True, text=True).stdout.split('\n')
        self.assertEqual(out[0], '2 0 0 4 13 True')


class Pins(unittest.TestCase):
    def test_tick_pins_are_5_8_2_only_added_reviewed_and_complete(self):
        v1, v2 = BASELINES['versions']['5.8.1']['methods'], BASELINES['versions']['5.8.2']['methods']
        self.assertFalse([m for m in v1 if m['id'].startswith('u5-310-tick-')])
        tick = [m for m in v2 if m['id'].startswith('u5-310-tick-')]
        self.assertEqual(tuple(m['id'] for m in tick), generator.TICK_IDS)
        self.assertTrue(all(m['status'] == 'added-reviewed' and 'reviewedToken581' not in m and 'change' not in m and len(m['review']) >= 20 for m in tick))
        names = {(m['type'], m['method']) for m in tick}
        for required in (('CnkdHkd01TT50Nckt310', 'ButtonClick_0'), ('CnkdHkd01TT50Nckt310', 'CellChange_0'), ('CnkdHkd01TT50Nckt310', 'daySangPLGiamThue'),
                         ('CnkdHkd01TT50Nckt310', 'capNhatToKhai'), ('CnkdHkd01TT50Nckt310', 'SetCacDongCon'), ('CnkdHkd01TT50Nckt310', 'lockUnLockA_TK'),
                         ('GeneralFunctions', 'CopyTableToTable5'), ('frmWinToKhai', 'winFpSpread_ButtonClicked'), ('WinDoWorkEvent', 'ButtonClick'),
                         ('frmWinToKhai', 'winFpSpread_CellChange'), ('WinDoWorkEvent', 'CellChange')):
            self.assertIn(required, names)
        pins = {(m['type'], m['method']): (m['token'], m['ilBytes'], m['ilSha256']) for m in tick}
        self.assertEqual(pins[('CnkdHkd01TT50Nckt310', 'ButtonClick_0')], ('0x0600092b', 399, 'cdcc0084cc4702ce6df3ebaa99b24583b3b77867cb7a33be3b5a3ef8e75b6ca8'))
        self.assertEqual(pins[('CnkdHkd01TT50Nckt310', 'daySangPLGiamThue')], ('0x06000927', 1274, 'cbc9edf6ff15ddbcd1c1a3c0152bcdd98e02f015465f2c267f2b460eca5d8d37'))
        self.assertEqual(pins[('CnkdHkd01TT50Nckt310', 'CellChange_0')], ('0x06000926', 2816, '2d8a1b22805dc6b00f66de7b3ccaa831ac279351370b4fe828458593d534f796'))
        self.assertEqual(pins[('CnkdHkd01TT50Nckt310', 'capNhatToKhai')], ('0x0600092a', 1314, 'c4f36b5de6505db04af9883971bd02ef847865ee740f30c54ec95949f937e0fd'))
        # The shared HTKK.exe bodies are the same 5.8.2 bodies the Y8 entry pins already carry.
        y8 = {(m['type'], m['method']): (m['token'], m['ilBytes'], m['ilSha256']) for m in v2 if m['id'].startswith('y8-entry-')}
        for key in (('frmWinToKhai', 'winFpSpread_ButtonClicked'), ('WinDoWorkEvent', 'ButtonClick'), ('frmWinToKhai', 'winFpSpread_CellChange')):
            self.assertEqual(pins[key], y8[key])
        self.assertEqual(generator.tick_pins(BASELINES['versions']['5.8.1']), [])
        self.assertEqual(len(generator.tick_pins(BASELINES['versions']['5.8.2'])), 13)

    def test_validation_refuses_partial_misplaced_or_default_tick_pins(self):
        def broken(mutate):
            data = copy.deepcopy(BASELINES); mutate(data)
            with self.assertRaises(generator.BaselineError): generator.validate(data)
        def first(data):
            return next(i for i, m in enumerate(data['versions']['5.8.2']['methods']) if m['id'].startswith('u5-310-tick-'))
        broken(lambda d: d['versions']['5.8.2']['methods'].pop(first(d)))
        broken(lambda d: d['versions']['5.8.2']['methods'][first(d)].pop('review'))
        broken(lambda d: d['versions']['5.8.2']['methods'][first(d)].update(status='token-renumbered'))
        broken(lambda d: d['versions']['5.8.2']['methods'][first(d)].update(reviewedToken581='0x06000001'))
        broken(lambda d: d['versions']['5.8.2']['methods'][first(d)].update(id='y8-entry-extra'))
        broken(lambda d: d['versions']['5.8.1']['methods'].append(copy.deepcopy(d['versions']['5.8.2']['methods'][first(d)])))
        broken(lambda d: d['versions']['5.8.2']['methods'].insert(first(d), d['versions']['5.8.2']['methods'].pop(first(d) + 1)))

    @unittest.skipUnless(shutil.which('mcs') and shutil.which('mono'), 'local CLR plan smoke test needs mono')
    def test_compiled_tick_plan_needs_the_5_8_2_pins(self):
        program = ('using System;class P{static void Main(string[] a){HtkkOracleBaseline.Select(a[0]);'
                   'Console.WriteLine(HtkkDeclarationCasePlans.ImportTick("01NTNN-NCCNN-entry-M10-2026")==null);'
                   'try{HtkkDeclarationTickPlan t=HtkkDeclarationCasePlans.ImportTick("' + CASE + '");Console.WriteLine(t.Edits.Length+" "+t.Ticks.Length+" "+t.Unticked.Length+" "+t.Readbacks.Length+" "+t.MethodPins.Length);}'
                   'catch(InvalidOperationException e){Console.WriteLine(e.Message);}'
                   'foreach(string id in HtkkDeclarationCasePlans.CaseIds)if(HtkkDeclarationCasePlans.ImportTick(id)!=null&&HtkkDeclarationCasePlans.Entry(id)!=null)Console.WriteLine("both "+id);}}')
        with tempfile.TemporaryDirectory() as directory:
            folder = pathlib.Path(directory); (folder / 'P.cs').write_text(program)
            subprocess.run(['mcs', '-langversion:ISO-2', '-warn:0', '-out:' + str(folder / 'p.exe'), str(folder / 'P.cs'), str(ROOT / 'HtkkOracleBaseline.cs'), str(ROOT / 'HtkkDeclarationCasePlans.cs')], check=True, capture_output=True)
            new = subprocess.run(['mono', str(folder / 'p.exe'), '5.8.2'], check=True, capture_output=True, text=True).stdout.split('\n')
            old = subprocess.run(['mono', str(folder / 'p.exe'), '5.8.1'], capture_output=True, text=True).stdout.split('\n')
        self.assertEqual(new[:2], ['True', '4 2 1 6 13'])
        self.assertNotIn('both', '\n'.join(new))
        # 5.8.1 has no CnkdHkd01TT50Nckt310: the plan refuses to run there.
        self.assertEqual(old[:2], ['True', 'HTKK_ORACLE_TICK_UNPINNED'])


class Driver(unittest.TestCase):
    def test_ticks_act_only_through_original_editor_keys_and_checkbox(self):
        for forbidden in ('SetPublic(', 'SetValue(', 'set_Value', '"Value",', '.Text=', 'PerformClick', 'InsertTableRow', 'InvokeMember', 'XmlWriter', 'GetMethod(',
                          'ButtonClick_0(', 'daySangPLGiamThue(', 'CopyTableToTable5(', 'SetCacDongCon(', 'Process.Start', '"Locked",'):
            self.assertNotIn(forbidden, CODE, forbidden)
        for original in ('SendKeys.SendWait(" ")', 'SendKeys.SendWait("^a")', 'SendKeys.SendWait("{TAB}")', 'HtkkNativeUiHarness.BeginCellEdit(grid,sheet,row,column,true)',
                         'HtkkNativeUiHarness.CommitCellEdit(grid)', 'OriginalMessageVisible()', 'DeclarationEntryGuard(grid)', 'DeclarationMethodPinMask(declarationTickPlan.MethodPins)'):
            self.assertIn(original, TICK, original)
        # Pins, then every edit, then every tick, then the read-back; one action per UI turn.
        order = [TICK.index('if(declarationPhase=="tick-' + phase + '")') for phase in ('pins', 'edits', 'ticks', 'inspect')]
        self.assertEqual(order, sorted(order))
        self.assertIn('EditDeclarationTick(declarationTickActionCount);if(finished)return;', TICK)
        self.assertIn('TickDeclarationImport(declarationTickActionCount-declarationTickPlan.Edits.Length);if(finished)return;', TICK)
        # A tick needs an open, unticked, visible original checkbox; the read-back then sends the case to the shared sheet checks.
        self.assertIn('int precondition=DeclarationEntryCellKind(cell)!="FarPoint.Win.Spread.CellType.CheckBoxCellType"?3:Convert.ToBoolean(Get(cell,"Locked"))?7:Selected(Get(cell,"Value"))?12:!RowVisible(sheet,at[0])?14:0;', TICK)
        self.assertIn('if(precondition!=0){declarationTickMismatchMask|=1<<action;DeclarationTickFail(precondition);return;}', TICK)
        self.assertIn('declarationPhase="import-inspect";declarationClock=Stopwatch.StartNew();SetStage(HtkkAutomationStage.DeclarationImportSheetChecking);', TICK)

    def test_import_driver_routes_the_tick_plan_after_the_original_import(self):
        self.assertIn('declarationTickPlan=HtkkDeclarationCasePlans.ImportTick(declarationPlan.CaseId);if(declarationEntryPlan!=null&&declarationTickPlan!=null)throw new InvalidOperationException();', IMPORT)
        self.assertIn('if(declarationPhase.StartsWith("tick-",StringComparison.Ordinal)){ContinueDeclarationTick();return;}', IMPORT)
        self.assertIn('if(declarationTickPlan!=null){declarationPhase="tick-pins";SetStage(HtkkAutomationStage.DeclarationImportTickReadyWaiting);}', IMPORT)
        self.assertIn('if(declarationTickPlan!=null)matched=matched&&declarationImportSheetMatched&&DeclarationTickSucceeded();', IMPORT)
        self.assertIn('if(declarationTickPlan==null||declarationEntryPlan!=null||!roundtripImportSucceeded)throw new InvalidOperationException();', TICK)
        # The import itself is unchanged: the sheet checks still run, after the ticks.
        self.assertIn('declarationImportSheetMatched=InspectDeclarationGrid();', IMPORT)

    def test_diagnostics_are_typed_bounded_and_value_free(self):
        fields = automation['resultFields']
        names = re.findall(r'"(declarationTick[A-Za-z0-9]+)"', TICK[TICK.index('private string DeclarationTickJson(){'):TICK.index('private void DeclarationTickFail(')])
        self.assertEqual(len(names), 10)
        for name in names:
            self.assertIn(name, automation['keys'])
            self.assertEqual(fields[name]['activeModes'], [MODE])
            self.assertIn(fields[name]['kind'], ('boolean', 'integer'))
        self.assertEqual(fields['declarationTickActionCount']['maximum'], 8)
        stages = {s['id'] for s in automation['stages']}
        for stage in ('declaration-import-tick-ready-waiting', 'declaration-import-tick-pins-checking', 'declaration-import-tick-editing', 'declaration-import-tick-invoking',
                      'declaration-import-tick-readback-checking', 'declaration-import-tick-not-matched', 'declaration-import-tick-exported'):
            self.assertIn(stage, stages)

    def test_probe_success_and_raw_retention_name_the_tick_mode(self):
        self.assertIn('$declarationTickCase=$env:EXPECTED_WEB_CASE_ID -cin $HtkkDeclarationTickCases', PROBE)
        self.assertIn('$lastGui.declarationTickActionCount -eq $lastGui.declarationTickPlannedCount -and $lastGui.declarationTickFailureCode -eq 0 -and $lastGui.declarationTickMismatchMask -eq 0', PROBE)
        self.assertIn('else{$matched=$matched -and $lastGui.declarationTickPlannedCount -eq 0 -and $lastGui.declarationTickActionCount -eq 0}', PROBE)
        self.assertIn("elseif($declarationTickCase){@('roundtripImportSucceeded','roundtripImportPathMatched','declarationTickMethodPinsMatched','declarationTickEditsMatched','declarationTickTicksMatched')}", PROBE)
        self.assertIn("elseif($declarationTickCase){'web-xml-import-tick-reexport'}", PROBE)
        publisher = (ROOT / 'publish-htkk-declaration-native-output.py').read_text(encoding='utf-8')
        self.assertIn('in (reader.case_registry.IMPORT_MODE,reader.case_registry.IMPORT_TICK_MODE)', publisher)


if __name__ == '__main__':
    unittest.main()
