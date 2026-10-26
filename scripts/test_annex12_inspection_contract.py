"""Mode routing and bounded metadata contracts; no synthetic test is native proof."""
import ast,pathlib,re,unittest
ROOT=pathlib.Path(__file__).parent
MODES=('inspect','profile-save','gtgt-inspect','gtgt-sheet-inspect','gtgt-annex12-inspect','gtgt-export-inspect','gtgt-roundtrip-inspect','gtgt-web-import-inspect')
class AnnexInspectionContract(unittest.TestCase):
 def test_actual_csharp_start_rejects_unknown_modes_and_accepts_every_existing_mode(self):
  text=(ROOT/'HtkkGuiReferenceAutomation.cs').read_text()
  expression=re.search(r'if\((requestedMode[^\n]+)\)throw new ArgumentException\(\)',text).group(1).replace('&&',' and ').replace('||',' or ')
  parsed=ast.parse(expression,mode='eval')
  for node in ast.walk(parsed):self.assertIsInstance(node,(ast.Expression,ast.BoolOp,ast.And,ast.Or,ast.Compare,ast.Eq,ast.NotEq,ast.Name,ast.Load,ast.Constant))
  for mode in (*MODES,'none','unknown','gtgt-annex12-inspect-extra'):
   self.assertEqual(eval(compile(parsed,'<original helper mode guard>','eval'),{'__builtins__':{}},{'requestedMode':mode}),mode not in MODES)
 def test_annex_metadata_keys_are_unique_typed_and_defaulted_in_real_powershell_fixture(self):
  text=(ROOT/'Get-HtkkSafeGuiReferenceResult.ps1').read_text();fixture=(ROOT/'Test-HtkkSafeGuiReferenceResult.ps1').read_text()
  keys=re.findall(r"'([^']+)'",re.search(r'\$keys=@\(([^\n]+)\)',text).group(1));self.assertEqual(len(keys),len(set(keys)))
  for key in ('periodAnnex12Matched','annex12SourcePinsMatched','annex12SheetObserved','annex12StructureMatched','annex12GroupMetadataMatched','annex12SttMatched','annex12LocksMatched'):
   self.assertIn(key,keys);self.assertIn(key+'=$false;',fixture)
  for key,maximum in {'annex12SelectionActionCount':1,'annex12NumericCount':8,'annex12NumericNonzeroMask':255,'annex12NumericEmptyMask':255,'annex12FirstGroupId':10000}.items():
   self.assertIn(key,keys);self.assertIn(key+'='+str(maximum)+';',text);self.assertIn(key+'=0;',fixture)
  self.assertIn("$annex.mode='gtgt-annex12-inspect'",fixture);self.assertIn("@('annex12FirstGroupId',10001)",fixture)
 def test_annex_mode_is_inspection_only_with_separate_period_predicate(self):
  probe=(ROOT/'probe-htkk-windows.ps1').read_text()
  line=next(line for line in probe.splitlines() if "if($GuiAutomation -eq 'gtgt-annex12-inspect'){$matched=" in line)
  for term in ('$lastGui.annexSelectedCount -eq 1','$lastGui.annex12SelectionActionCount -eq 1','$lastGui.annex12StructureMatched','-not $lastGui.exportCommandInvoked','-not $lastGui.webInputVerified'):self.assertIn(term,line)
  self.assertIn("if($GuiAutomation -eq 'gtgt-annex12-inspect'){$lastGui.periodAnnex12Matched}else{$lastGui.periodNoAnnexMatched}",probe)
  for line in probe.splitlines():
   if '$nativeEvidenceCreated=' in line or "if($GuiAutomation -eq 'gtgt-web-import-inspect' -and $report.stage" in line:self.assertNotIn('gtgt-annex12-inspect',line)

 def test_dispatch_choices_and_actual_workflow_entry_guard_accept_the_same_modes(self):
  workflow=(ROOT.parent/'.github/workflows/probe-htkk-windows.yml').read_text()
  choices=re.search(r'gui_automation:\n.*?options: \[([^\]]+)\]',workflow,re.S).group(1)
  declared={item.strip() for item in choices.split(',')}
  guarded=set(re.findall(r"'([^']+)'",re.search(r'\$guiAutomation -notin @\(([^)]+)\)',workflow).group(1)))
  self.assertEqual(declared,{'none',*MODES})
  self.assertEqual(guarded,declared)

 def test_annex_selector_uses_both_original_checkbox_captions_not_a_label_column(self):
  source=(ROOT/'HtkkGtgtPeriodAndSheet.cs').read_text()
  expression=re.search(r'bool Annex12CaptionMatched\([^)]*\)\{return ([^;]+);\}',source).group(1).replace('&&',' and ')
  tree=ast.parse(expression,mode='eval')
  for node in ast.walk(tree):self.assertIsInstance(node,(ast.Expression,ast.BoolOp,ast.And,ast.Compare,ast.Eq,ast.Name,ast.Load,ast.Constant))
  valid={'typeName':'FarPoint.Win.Spread.CellType.CheckBoxCellType','uncheckedText':'01-2/GTGT','checkedText':'01-2/GTGT'}
  self.assertTrue(eval(compile(tree,'<real annex selector>','eval'),{'__builtins__':{}},valid))
  for key in valid:
   bad={**valid,key:'unmatched'}
   self.assertFalse(eval(compile(tree,'<real annex selector>','eval'),{'__builtins__':{}},bad))
  self.assertIn('columnCount<1||columnCount>16',source)
