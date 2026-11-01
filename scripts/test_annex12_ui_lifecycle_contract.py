from pathlib import Path
import json
import unittest
ROOT=Path(__file__).resolve().parent
class Annex12UiLifecycleContract(unittest.TestCase):
 def test_real_original_ui_sequence_is_fixed_and_never_forces_rows_or_business_outputs(self):
  text=(ROOT/'HtkkGtgtPeriodAndSheet.cs').read_text()
  source=text.split('// Fixed original-UI lifecycle sequence;',1)[1].split('// Fixed synthetic input scenario,',1)[0]
  for marker in ['SendKeys.SendWait(key)','StartCellEditing','StopCellEditing','pnF5','pnF7','OriginalMessageVisible','GetForegroundWindow','annex12LifecycleObservedMask==1023','annex12LifecycleActionCount==9','annex12LifecycleEditCount==1','new int[]{2,1,1}']:
   self.assertIn(marker,source)
  for forbidden in ['SetValue(', 'InsertTableRowNoSView', 'GetMethod("InsertTable"', 'GetMethod("RemoveTable"', 'CalculateSumByGroup','ExecuteAssembly','WriteAllText','Exception.Message']:
   self.assertNotIn(forbidden,source)
  self.assertEqual(source.count('Annex12LifecycleKey(grid,annex,'),9)
  self.assertIn('mode!="gtgt-annex12-row-inspect"',source)
 def test_typed_bounded_results_only_activate_for_row_inspection(self):
  registry=json.loads((ROOT/'htkk-native-automation-registry.json').read_text())
  for key,maximum in [('annex12LifecycleActionCount',9),('annex12LifecycleEditCount',1),('annex12LifecycleObservedMask',1023)]:
   field=registry['resultFields'][key]
   self.assertEqual(field['activeModes'],['gtgt-annex12-row-inspect']);self.assertEqual(field['minimum'],0);self.assertEqual(field['maximum'],maximum);self.assertEqual(field['default'],0)
  gate=(ROOT/'probe-htkk-windows.ps1').read_text()
  self.assertIn("if($GuiAutomation -eq 'gtgt-annex12-row-inspect'){$matched=$matched -and $lastGui.annex12LifecycleMatched",gate)
