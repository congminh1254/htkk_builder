"""Offline contracts for native-case mode original-entry-export of the declaration driver.

The Y8 entry case types a FIXED compiled plan into HTKK's own grid instead of importing the web XML
(HTKK 5.8.1 resets the Y8 tables on import, release 238). Passing these tests is never native
evidence: they pin the plan to the independent Decimal oracle, keep the driver to original
controls and keyboard input, and keep the case non-gating with value-free diagnostics.
"""
import decimal, importlib.util, json, pathlib, re, shutil, subprocess, tempfile, unittest

ROOT = pathlib.Path(__file__).parent


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / file); value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value); return value


registry = load('entry_registry_test', 'htkk_native_cases.py')
dfx = load('entry_fixture_test', 'declaration_test_support.py')
d = dfx.d
reader = load('entry_reader_test', 'fetch-htkk-web-input.py')
design = load('entry_descriptor_design_test', 'htkk_descriptor_native_cases.py')
automation = json.loads((ROOT / 'htkk-native-automation-registry.json').read_text())
PLANS = (ROOT / 'HtkkDeclarationCasePlans.cs').read_text(encoding='utf-8')
ENTRY = (ROOT / 'HtkkDeclarationOriginalEntry.cs').read_text(encoding='utf-8')
IMPORT = (ROOT / 'HtkkDeclarationWebImport.cs').read_text(encoding='utf-8')
CODE = re.sub(r'//[^\n]*', '', ENTRY)  # entry driver without comments
CASE = '01NTNN-NCCNN-entry-M10-2026'
# Lần phát sinh (KieuKy 18, kieuKy D) of the same rows: the second entry case, with (6) AE typed as the period day.
OCCURRENCE = '01NTNN-NCCNN-occurrence-D20-10-2026'
BASE = '01NTNN-NCCNN-two-parts-M10-2026'
MODE = 'declaration-web-import-inspect'


def plan_block(case_id):
    return re.search(r'case "' + re.escape(case_id) + r'":return new HtkkDeclarationCasePlan\((.*?)\);\n', PLANS, re.S).group(1)


def entry_block():
    return PLANS[PLANS.index(' internal static HtkkDeclarationEntryPlan Entry(string caseId){'):]


def string_array(block, ordinal):
    """The ordinal-th `new string[]{...}` literal of a block, as Python strings."""
    arrays = re.findall(r'new string\[\]\{(.*?)\}', block, re.S)
    return re.findall(r'"((?:[^"\\]|\\.)*)"', arrays[ordinal])


def entries():
    return string_array(entry_block(), 2)


class Registration(unittest.TestCase):
    def test_entry_case_is_the_only_y8_case_non_gating_and_of_its_own_mode(self):
        self.assertEqual(registry.DECLARATION_ENTRY_CASES, (CASE, OCCURRENCE))
        self.assertIn(CASE, registry.DECLARATION_CASES)
        self.assertIs(registry.CASES[CASE]['releaseGate'], False)
        self.assertNotIn(CASE, registry.GATE_CASES)
        self.assertEqual(registry.input_mode(CASE), registry.ENTRY_MODE)
        self.assertEqual(registry.driver(CASE), MODE)
        self.assertEqual(registry.CASES[CASE]['producerCase'], 'ntnn01-nccnn-entry-m10-2026')
        # The import-based Y8 case was removed after release 242 (HTKK resets the tables on import).
        self.assertEqual([c for c, v in registry.CASES.items() if v['unit']['menuId'] == 'Y8'], [CASE, OCCURRENCE])
        self.assertEqual(registry.input_mode(OCCURRENCE), registry.ENTRY_MODE); self.assertIs(registry.CASES[OCCURRENCE]['releaseGate'], False)
        self.assertNotIn(BASE, registry.CASES); self.assertNotIn(BASE, d.CASES); self.assertNotIn('01-ntnn-nccnn-tt89-3.0.9', registry.TRUSTED_ADAPTERS)
        self.assertNotIn(BASE, automation['resultFields']['webCaseId']['values'])
        adapters = {a['adapterId']: a['mode'] for a in design.DESIGN['adapters']}
        self.assertEqual(adapters['01-ntnn-nccnn-tt89-3.0.9-entry'], 'original-entry-export')
        formats = (ROOT / 'HtkkNativeCaseFormats.ps1').read_text()
        self.assertIn("$HtkkDeclarationEntryCases=@('" + CASE + "','" + OCCURRENCE + "')", formats); self.assertNotIn(BASE, formats)

    def test_entry_input_is_the_reviewed_design_case(self):
        designs = {c['caseId']: c['expectedLeaves'] for c in design.DESIGN['cases']}
        self.assertEqual(designs[CASE], designs[BASE])  # BASE stays as the reviewed design case only
        body = dfx.declaration_fixture(CASE)
        reader.validate_web_xml(body, case_id=CASE)
        own = json.dumps(dfx.declaration_manifest(body, CASE), ensure_ascii=False).encode()
        self.assertEqual(reader.validate_manifest(own)['caseId'], CASE)


class EntryPlan(unittest.TestCase):
    def test_plan_identity_pins_and_xml_checks(self):
        entry = plan_block(CASE)
        self.assertIn('"Y8","3.0.9","2012","Ntnn01TT89Nckt309",new string[]{"101","101_8","Y8"},"month","18","2026","10","01/10/2026","31/10/2026",false', entry)
        self.assertIn('"53630634bd02cc412ddde0682c2557226547737fceed792f595709a2fd0eafe1"', entry)
        leaves = {k: v for k, v in d._descriptor_expected[CASE][0].items()}
        self.assertEqual({c.split('|')[0].rsplit('/', 1)[-1]: c.split('|')[1] for c in string_array(entry, 3)}, leaves)
        self.assertNotIn('"' + BASE + '"', PLANS.split('internal static readonly string[] CaseIds=')[1].split('\n')[0])
        self.assertIn('"' + CASE + '"', PLANS.split('internal static readonly string[] CaseIds=')[1].split('\n')[0])

    def test_typed_values_are_the_reviewed_rows_of_the_decimal_oracle(self):
        rows = {row: computed for (_, _, computed_rows, _), row in zip(d.ntnn_tables(CASE)[1:], (78, 86)) for computed in computed_rows}
        texts = d.case(CASE)['texts']
        columns = {'Y': 'ct5', 'AJ': 'ct7', 'AN': 'ct8', 'AZ': 'ct10', 'BD': 'ct11'}
        seen = set()
        for entry in entries():
            parts = entry.split('|'); kind = parts[0]
            cell = re.fullmatch(r'([A-Z]+)([0-9]+)', parts[1]); column, row = cell.group(1), int(cell.group(2))
            seen.add(parts[1])
            if row == 98:
                self.assertEqual((kind, column, parts[2]), ('date-optional', 'AY', '27/10/2026'))
                self.assertEqual(d.case(CASE)['ngayKy'], '2026-10-27')
                continue
            oracle = rows[row]
            if kind == 'number':
                self.assertEqual(decimal.Decimal(parts[2]), decimal.Decimal(oracle[columns[column]]), entry)
            elif kind == 'combo':
                self.assertEqual(column, 'L'); self.assertEqual(parts[5], 'BX' + str(row)); self.assertEqual(parts[6], oracle['ct1b_ma'])
                self.assertIn(parts[4], texts); self.assertEqual(parts[3], parts[4][0])
                self.assertEqual(int(parts[2]), int(parts[6]) - 1)  # DM_NNKD_NTNN.xml file order (01 -> 0, 05 -> 4)
            elif kind == 'text':
                self.assertIn(column, ('C', 'S')); self.assertIn(parts[2], texts)
            else:
                self.assertEqual(kind, 'date'); self.assertIn(column, ('W', 'AE')); self.assertRegex(parts[2], r'\A[0-3][0-9]/(09|10)/2026\Z')
                if column == 'AE':
                    self.assertTrue(parts[2].endswith('/10/2026'))  # checkTKChinh E_27: payment inside the period
        # Every value column of both rows, BH (relief) stays its default 0 as in the oracle.
        for row in (78, 86):
            self.assertEqual({c for c in seen if c.endswith(str(row))}, {c + str(row) for c in ('C', 'L', 'S', 'W', 'Y', 'AE', 'AJ', 'AN', 'AZ', 'BD')})
            self.assertEqual(rows[row]['ct12'], '0')
        self.assertEqual(len(entries()), 21)
        # Nothing is typed into a computed, locked-part, choice or button cell.
        for entry in entries():
            cell = entry.split('|')[1]
            self.assertNotRegex(cell, r'\A(AV|BN|BR|BX|CA|M|B)[0-9]+\Z')
            self.assertNotIn(cell, ('M6', 'M8', 'C10', 'C9'))
            self.assertFalse(cell.endswith('60') or cell.endswith('62') or cell.endswith('80') or cell.endswith('88'))

    def test_sheet_checks_are_the_decimal_oracle_row_taxes_and_table_totals(self):
        checks = {c.split('|')[1]: c.split('|')[2] for c in string_array(plan_block(CASE), 2)}
        expected = {'BR62': '0'}
        for (_, _, rows, totals), row, total, prefix in zip(d.ntnn_tables(CASE)[1:], (78, 86), (80, 88), ('mucI_tong_', 'mucII_tong_')):
            self.assertEqual(len(rows), 1)
            expected.update({'AV%d' % row: rows[0]['ct9'], 'BN%d' % row: rows[0]['ct13'], 'BR%d' % row: rows[0]['ct14']})
            expected.update({'Y%d' % total: totals[prefix + 'ct5'], 'AV%d' % total: totals[prefix + 'ct9'], 'BN%d' % total: totals[prefix + 'ct13'], 'BR%d' % total: totals[prefix + 'ct14']})
        self.assertEqual(checks, expected)
        self.assertEqual((checks['BR80'], checks['BR88'], checks['AV78'], checks['BN78'], checks['AV86'], checks['BN86']), ('20000000', '7000000', '10000000', '10000000', '5000000', '2000000'))

    def test_part_choice_tables_and_lock_columns_follow_the_source(self):
        block = entry_block()
        self.assertIn('HtkkDeclarationEntryPlan entry=new HtkkDeclarationEntryPlan("M8","M6","AY96","InterfaceIni/DM_NNKD_NTNN.xml","3aed1aea293f423271461892319217e33fc5dab32288dd708e6192a515802d17",', block)
        self.assertEqual(string_array(block, 0), ['ThueNTNN|60|1|1', 'ThueNCCNN|78|1|0', 'ThueCNKCT|86|1|0'])
        # Ntnn01TT89Nckt309.getCols literal "C###L###M###S###W###Y###AE###AJ###AN###AZ###BD###BH".
        self.assertEqual(string_array(block, 1), 'C###L###M###S###W###Y###AE###AJ###AN###AZ###BD###BH'.split('###'))

    def test_method_pins_name_token_size_and_il_hash(self):
        pins = string_array(entry_block(), 3)
        self.assertEqual(len(pins), 14)
        names = set()
        for pin in pins:
            assembly, type_name, method, token, size, digest = pin.split('|')
            self.assertIn(assembly, ('B', 'H')); self.assertRegex(token, r'\A0x060[0-9a-f]{5}\Z'); self.assertRegex(size, r'\A[1-9][0-9]{0,5}\Z'); self.assertRegex(digest, r'\A[0-9a-f]{64}\Z')
            names.add((type_name, method))
        for required in (('Ntnn01TT89Nckt309', 'ButtonClick_0'), ('Ntnn01TT89Nckt309', 'LockUnlock'), ('Ntnn01TT89Nckt309', 'AutoBindData_0'), ('GeneralFunctions', 'LockUnLockColsInTable'),
                         ('frmWinToKhai', 'winFpSpread_ButtonClicked'), ('WinDoWorkEvent', 'ButtonClick'), ('frmWinToKhai', 'winFpSpread_CellChange'), ('WinSpreadProcess', 'DMNnkdNtnn'), ('frmWinToKhai', 'ProcessCmdKey')):
            self.assertIn(required, names)
        self.assertIn('module.ResolveMethod(', ENTRY); self.assertIn('GetILAsByteArray()', ENTRY)

    @unittest.skipUnless(shutil.which('mcs') and shutil.which('mono'), 'local CLR plan smoke test needs mono')
    def test_compiled_plans_construct_and_select_the_entry_mode(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = pathlib.Path(directory)
            (folder / 'P.cs').write_text('using System;class P{static void Main(){foreach(string id in HtkkDeclarationCasePlans.CaseIds){HtkkDeclarationCasePlan p=HtkkDeclarationCasePlans.Find(id);HtkkDeclarationEntryPlan e=HtkkDeclarationCasePlans.Entry(id);Console.WriteLine(id+" "+(p!=null)+" "+(e==null?0:e.Entries.Length)+" "+(e==null?0:e.MethodPins.Length));}foreach(string id in new string[]{"01NTNN-NCCNN-entry-M10-2026","01NTNN-NCCNN-occurrence-D20-10-2026"})Console.Error.WriteLine(id+"\t"+String.Join("\t",HtkkDeclarationCasePlans.Entry(id).Entries));}}')
            subprocess.run(['mcs', '-langversion:ISO-2', '-warn:0', '-out:' + str(folder / 'p.exe'), str(folder / 'P.cs'), str(ROOT / 'HtkkDeclarationCasePlans.cs')], check=True, capture_output=True)
            run = subprocess.run(['mono', str(folder / 'p.exe')], check=True, capture_output=True, text=True); lines = run.stdout.split('\n')
        typed = {line.split('\t')[0]: line.split('\t')[1:] for line in run.stderr.split('\n') if line}
        # The lần phát sinh entry types the same values except (6) AE, which is the period day (E_27).
        for monthly, occurrence in zip(typed[CASE], typed[OCCURRENCE]):
            self.assertEqual(occurrence, monthly if not monthly.startswith('date|AE') else monthly.rsplit('|', 1)[0] + '|20/10/2026')
        self.assertEqual([e for e in typed[OCCURRENCE] if e.startswith('date|AE')], ['date|AE78|20/10/2026', 'date|AE86|20/10/2026'])
        rows = {line.split()[0]: line.split()[1:] for line in lines if line}
        self.assertEqual(list(rows), list(registry.DECLARATION_CASES))
        for case, (found, count, pins) in rows.items():
            self.assertEqual(found, 'True')
            self.assertEqual((count, pins), ('21', '14') if case in (CASE, OCCURRENCE) else ('0', '0'))


class Driver(unittest.TestCase):
    def test_entry_acts_only_through_original_editors_keys_and_checkbox(self):
        for forbidden in ('SetPublic(', 'SetValue(', 'set_Value', '"Value",', '.Text=', 'PerformClick', 'InsertTableRow', 'InvokeMember', 'XmlWriter', 'GetMethod("Tinh', 'LockUnLockColsInTable(', 'ButtonClick_0(', 'Process.Start', '"C10"'):
            self.assertNotIn(forbidden, CODE, forbidden)
        for original in ('SendKeys.SendWait(" ")', 'SendKeys.SendWait("{F5}")', 'SendKeys.SendWait("^a")', 'SendKeys.SendWait("{TAB}")', 'SendKeys.SendWait(key)', 'HtkkNativeUiHarness.BeginCellEdit(grid,sheet,row,column,true)', 'FindVendorCombo(editor,0)', '"pnF5"', 'OriginalMessageVisible()'):
            self.assertIn(original, ENTRY, original)
        # Combo selection state is only READ; any write of SelectedIndex/DroppedDown is absent.
        self.assertNotRegex(ENTRY, r'"(SelectedIndex|DroppedDown)",\s*(true|false|[0-9a-z]+)\)')
        # Unicode text is real keyboard input to the focused editor (KEYEVENTF_UNICODE), never WM_SETTEXT.
        self.assertIn('[DllImport("user32.dll",EntryPoint="SendInput",SetLastError=true)]', ENTRY)
        self.assertIn('inputs[0].Flags=0x0004', ENTRY); self.assertNotIn('WM_SETTEXT', ENTRY); self.assertNotIn('0x000C', ENTRY)
        # The part choice comes before the rows and every value; values one per UI turn.
        order = [ENTRY.index('if(declarationPhase=="entry-' + phase + '")') for phase in ('ready', 'choice', 'rows', 'values', 'inspect')]
        self.assertEqual(order, sorted(order))
        self.assertIn('EditDeclarationEntry(declarationEntryActionCount);if(finished)return;', ENTRY)

    def test_import_driver_routes_only_entry_plans_to_the_entry_phases(self):
        self.assertIn('declarationEntryPlan=HtkkDeclarationCasePlans.Entry(declarationPlan.CaseId);', IMPORT)
        self.assertIn('declarationPhase=declarationEntryPlan!=null?"entry-ready":"import-ready"', IMPORT)
        self.assertIn('if(declarationPhase.StartsWith("entry-",StringComparison.Ordinal)){ContinueDeclarationEntry();return;}', IMPORT)
        self.assertIn('if(exportFilenameEditing||declarationEntryBusy)return;', IMPORT)
        self.assertIn('DeclarationTerminal(matched?(declarationEntryPlan!=null?HtkkAutomationStage.DeclarationOriginalEntryExported:HtkkAutomationStage.DeclarationWebImportInspected):HtkkAutomationStage.DeclarationExportNotMatched)', IMPORT)
        self.assertIn('return json.ToString()+DeclarationEntryJson();', IMPORT)

    def test_diagnostics_are_typed_bounded_and_value_free(self):
        fields = automation['resultFields']
        names = re.findall(r'"(declarationEntry[A-Za-z0-9]+)"', ENTRY[ENTRY.index('private string DeclarationEntryJson(){'):ENTRY.index('private bool DeclarationEntryCase(){')])
        self.assertEqual(len(names), 25)
        for name in names:
            self.assertIn(name, automation['keys'])
            self.assertEqual(fields[name]['activeModes'], [MODE])
            self.assertIn(fields[name]['kind'], ('boolean', 'integer'))
        self.assertIn(CASE, fields['webCaseId']['values'])
        stages = {s['id'] for s in automation['stages']}
        for stage in ('declaration-entry-ready-waiting', 'declaration-entry-pins-checking', 'declaration-entry-choice-invoking', 'declaration-entry-rows-inserting', 'declaration-entry-editing', 'declaration-entry-sheet-checking', 'declaration-entry-not-matched', 'declaration-original-entry-exported'):
            self.assertIn(stage, stages)
        for mode in automation['modes'].values():
            self.assertIn('HtkkDeclarationOriginalEntry.cs', mode['orderedCompileInputs'])
        probe = (ROOT / 'probe-htkk-windows.ps1').read_text(encoding='utf-8')
        terminal = re.search(r"\$terminal=\$nextGui\.failureCategory -ne 'none' -or \$nextGui\.stage -in @\(([^)]*)\)", probe).group(1)
        self.assertIn("'declaration-entry-not-matched'", terminal); self.assertIn("'declaration-original-entry-exported'", terminal)

    def test_probe_success_and_raw_retention_name_the_entry_mode(self):
        probe = (ROOT / 'probe-htkk-windows.ps1').read_text(encoding='utf-8')
        self.assertIn("$declarationEntryCase=$env:EXPECTED_WEB_CASE_ID -cin $HtkkDeclarationEntryCases", probe)
        self.assertIn("$lastGui.stage -eq $(if($declarationEntryCase){'declaration-original-entry-exported'}else{'declaration-web-import-inspected'})", probe)
        self.assertIn('-not $lastGui.roundtripImportCommandInvoked -and -not $lastGui.roundtripImportSucceeded', probe)
        self.assertIn('$lastGui.declarationEntryActionCount -eq $lastGui.declarationEntryPlannedCount', probe)
        self.assertIn("@('declaration-web-import-inspected','declaration-original-entry-exported','declaration-export-not-matched')", probe)
        self.assertIn("inputMode=$(if($declarationEntryCase){'original-entry-export'}else{'web-xml-import-reexport'});originalImportSucceeded=(-not $declarationEntryCase)", probe)
        publisher = (ROOT / 'publish-htkk-declaration-native-output.py').read_text(encoding='utf-8')
        self.assertIn("'inputMode':reader.case_registry.input_mode(case_id)", publisher)


if __name__ == '__main__':
    unittest.main()
