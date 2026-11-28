"""Z5 PL 01-2/GTGT import diagnostic (01GTGT-TT89-pl012-M10-2026, run 46107139838: declarationCellZeroMask 70).

Value-free masks of the 01-2 sheet after the original import and, only after the case has already failed, one bounded probe of
whether an original edit of a plant's [10] recomputes [13] / [14]. Neither changes what the case needs to pass.
"""
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).parent
DRIVER = (ROOT / 'HtkkDeclarationWebImport.cs').read_text(encoding='utf-8')
PLANS = (ROOT / 'HtkkDeclarationCasePlans.cs').read_text(encoding='utf-8')
REGISTRY = json.loads((ROOT / 'htkk-native-automation-registry.json').read_text(encoding='utf-8'))
FIELDS = {'declarationAnnex12ImportPathMask': 63, 'declarationAnnex12TableShape': 65535, 'declarationAnnex12HeaderMask': 4095,
          'declarationAnnex12CellZeroMask': 16777215, 'declarationAnnex12TotalMask': 8191, 'declarationAnnex12ProbeMask': 4095}


def method(name):
    start = DRIVER.index(name)
    end = DRIVER.index('\n }\n', start)
    return DRIVER[start:end]


class Annex12ImportDiagnostic(unittest.TestCase):
    def test_fields_are_registered_bounded_and_emitted_in_order(self):
        for name, maximum in FIELDS.items():
            self.assertIn(name, REGISTRY['keys'])
            self.assertEqual(REGISTRY['resultFields'][name], {'kind': 'integer', 'default': 0, 'minimum': 0, 'maximum': maximum,
                                                             'activeModes': ['declaration-web-import-inspect', 'declaration-amendment-khbs-inspect']})
        body = method('private string DeclarationAnnex12Json(){')
        self.assertIn('string[] names=new string[]{' + ','.join('"%s"' % name for name in FIELDS) + '};', body)
        self.assertIn('int[] counts=new int[]{' + ','.join(FIELDS) + '};', body)
        # Counters only: no text, amount or formula leaves the process.
        self.assertEqual(body.count('json.Append('), 1)
        self.assertIn('counts[index].ToString(CultureInfo.InvariantCulture)', body)

    def test_only_the_z5_plans_with_the_01_2_sheet_are_inspected(self):
        self.assertIn('if(declarationPlan==null||declarationPlan.MenuId!="Z5")return false;', DRIVER)
        self.assertIn('foreach(string pair in declarationPlan.SheetNames)if(pair.Split(\'|\')[0]=="01_2")return true;', DRIVER)
        # Each plan from its "case" up to the next one; only the Z5 PL 01-2 plan names the 01_2 sheet of Z5 (D1 and Z3 are not Z5).
        starts = [m.start() for m in re.finditer(r'\n   case "[^"]+":return new HtkkDeclarationCasePlan\(', PLANS)]
        plans = {re.match(r'\n   case "([^"]+)"', PLANS[i:]).group(1): PLANS[i:(starts + [len(PLANS)])[k + 1]] for k, i in enumerate(starts)}
        z5 = [case for case, text in plans.items() if text.split('HtkkDeclarationCasePlan(caseId,', 1)[1].startswith('"Z5"') and '"01_2|01-2/GTGT"' in text]
        self.assertEqual(z5, ['01GTGT-TT89-pl012-M10-2026'])

    def test_the_pass_criteria_are_unchanged(self):
        grid = method('private bool InspectDeclarationGrid(){')
        self.assertIn('bool matched=declarationCellMismatchMask==0&&declarationCellCheckCount==checks.Length;\n  if(DeclarationAnnex12Case())InspectDeclarationAnnex12(grids[0]);\n  return matched;', grid)
        inspect = method('private void InspectDeclarationAnnex12(Control grid){')
        probe = method('private void ProbeDeclarationAnnex12Recompute(){')
        for body in (inspect, probe):
            for name in ('declarationCellMismatchMask', 'declarationCellCheckCount', 'declarationImportSheetMatched', 'roundtripImportSheetMatched', 'DeclarationTerminal', 'SetStage('):
                self.assertNotIn(name, body)
        # Every read is guarded: a failed read is a bit, never an exception of the run.
        self.assertIn('}catch(Exception){total|=4096;}', inspect)
        self.assertIn('}catch(Exception){mask|=32;}', probe)

    def test_the_probe_runs_only_after_the_case_failed_and_ends_it(self):
        self.assertEqual(DRIVER.count('ProbeDeclarationAnnex12Recompute();'), 1)
        self.assertIn('if(!declarationImportSheetMatched&&declarationClock.Elapsed.TotalSeconds<3)return;\n   if(!declarationImportSheetMatched){if(DeclarationAnnex12Case()&&!DeclarationKhbsMode())ProbeDeclarationAnnex12Recompute();DeclarationTerminal(HtkkAutomationStage.DeclarationImportSheetNotMatched);return;}', DRIVER)

    def test_the_probe_edits_only_plant_1_amount_through_the_original_editor(self):
        probe = method('private void ProbeDeclarationAnnex12Recompute(){')
        self.assertIn('Control grid;object sheet=DeclarationTickSheet("01_2",out grid);', probe)
        self.assertIn('DataLocationTemplateRowStart"))-2,column=Annex12ColumnT;', probe)
        self.assertIn('if(DeclarationTickActivate(grid,sheet)!=0)', probe)
        self.assertIn('Control editor=HtkkNativeUiHarness.BeginCellEdit(grid,sheet,row,column,true);', probe)
        self.assertIn('SendKeys.SendWait("^a");SendKeys.SendWait(texts[step]);SendKeys.SendWait("{TAB}");HtkkNativeUiHarness.CommitCellEdit(grid);', probe)
        self.assertIn('string[] texts=new string[]{"0",shown};', probe)
        # The typed amount is the cell's own whole number in invariant digits, never the shown text with separators.
        self.assertIn('string shown=original.ToString("0",CultureInfo.InvariantCulture);', probe)
        self.assertIn('if(OriginalMessageVisible()){mask|=16;break;}', probe)
        # No cell value is assigned directly and no business routine is called.
        for forbidden in ('"Value",', 'set_Value', 'TinhLaiTongCot10_12_PL01_2(', 'Invoke(', 'SetValue('):
            self.assertNotIn(forbidden, probe)
        self.assertEqual(probe.count('SendKeys.SendWait(texts[step])'), 1)

    def test_cell_positions_match_the_pinned_sheet(self):
        self.assertIn('Annex12ColumnB=1,Annex12ColumnC=2,Annex12ColumnT=19,Annex12ColumnU=20,Annex12ColumnX=23,Annex12ColumnAG=32,Annex12ColumnAO=40;', DRIVER)
        inspect = method('private void InspectDeclarationAnnex12(Control grid){')
        self.assertIn('Annex12FormulaNames(Cell(sheet,6,35),Annex12A1(r13,c13))', inspect)  # 01_2!AJ7 = T46
        self.assertIn('Annex12FormulaNames(Cell(main,19,15),Annex12A1(r14,c14))', inspect)  # 01!P20 = IF(P19=1, 01_2!X46)
        self.assertIn('x!=Math.Round(u*ao/100m,0,MidpointRounding.AwayFromZero)', inspect)  # Z5 X44 = ROUND(U44*AO44/100.0,0.0)


if __name__ == '__main__':
    unittest.main()
