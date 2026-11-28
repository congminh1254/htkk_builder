"""Z5 PL 01-2/GTGT import diagnostic (01GTGT-TT89-pl012-M10-2026, run 46107139838: declarationCellZeroMask 70).

Value-free masks of the 01-2 sheet after the original import; they never change what the case needs to pass. The post-failure edit
probe of run 46112620593 re-entered the import phase through SendKeys' message pumping (no declarationEntryBusy guard) and is gone.
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
          'declarationAnnex12CellZeroMask': 16777215, 'declarationAnnex12TotalMask': 8191}


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
        for name in ('declarationCellMismatchMask', 'declarationCellCheckCount', 'declarationImportSheetMatched', 'roundtripImportSheetMatched', 'DeclarationTerminal', 'SetStage('):
            self.assertNotIn(name, inspect)
        # Every read is guarded: a failed read is a bit, never an exception of the run.
        self.assertIn('}catch(Exception){total|=4096;}', inspect)

    def test_no_edit_is_made_after_the_import(self):
        # The diagnostic reads only: no original editor, key, tab click or cell write, and the failure branch is the plain one.
        self.assertNotIn('ProbeDeclarationAnnex12Recompute', DRIVER)
        self.assertNotIn('declarationAnnex12ProbeMask', DRIVER)
        self.assertNotIn('declarationAnnex12ProbeMask', REGISTRY['keys'])
        inspect = method('private void InspectDeclarationAnnex12(Control grid){')
        for forbidden in ('SendKeys', 'BeginCellEdit', 'DeclarationTickActivate', 'DeclarationEntrySelect', 'set_Value', 'SetValue(', 'Invoke('):
            self.assertNotIn(forbidden, inspect)
        self.assertIn('if(!declarationImportSheetMatched&&declarationClock.Elapsed.TotalSeconds<3)return;\n   if(!declarationImportSheetMatched){DeclarationTerminal(HtkkAutomationStage.DeclarationImportSheetNotMatched);return;}', DRIVER)

    def test_cell_positions_match_the_pinned_sheet(self):
        self.assertIn('Annex12ColumnB=1,Annex12ColumnC=2,Annex12ColumnT=19,Annex12ColumnU=20,Annex12ColumnX=23,Annex12ColumnAG=32,Annex12ColumnAO=40;', DRIVER)
        inspect = method('private void InspectDeclarationAnnex12(Control grid){')
        self.assertIn('Annex12FormulaNames(Cell(sheet,6,35),Annex12A1(r13,c13))', inspect)  # 01_2!AJ7 = T46
        self.assertIn('Annex12FormulaNames(Cell(main,19,15),Annex12A1(r14,c14))', inspect)  # 01!P20 = IF(P19=1, 01_2!X46)
        self.assertIn('x!=Math.Round(u*ao/100m,0,MidpointRounding.AwayFromZero)', inspect)  # Z5 X44 = ROUND(U44*AO44/100.0,0.0)


if __name__ == '__main__':
    unittest.main()
