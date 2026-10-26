"""Mode routing and bounded metadata contracts; no synthetic test is native proof."""
import ast,pathlib,re,unittest
ROOT=pathlib.Path(__file__).parent
MODES=('inspect','profile-save','gtgt-inspect','gtgt-sheet-inspect','gtgt-annex12-inspect','gtgt-annex12-row-inspect','gtgt-export-inspect','gtgt-roundtrip-inspect','gtgt-web-import-inspect')
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
  line=next(line for line in probe.splitlines() if "if($GuiAutomation -in @('gtgt-annex12-inspect','gtgt-annex12-row-inspect')){$matched=" in line)
  for term in ('$lastGui.annexSelectedCount -eq 1','$lastGui.annex12SelectionActionCount -eq 1','$lastGui.annex12StructureMatched','-not $lastGui.exportCommandInvoked','-not $lastGui.webInputVerified'):self.assertIn(term,line)
  self.assertIn("if($GuiAutomation -in @('gtgt-annex12-inspect','gtgt-annex12-row-inspect')){$lastGui.periodAnnex12Matched}else{$lastGui.periodNoAnnexMatched}",probe)
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

class AnnexRowInspectionContract(unittest.TestCase):
 def test_scalar_powershell_comparisons_never_receive_comma_separated_mode_literals(self):
  for file in ('probe-htkk-windows.ps1','New-HtkkX86ReferenceHost.ps1','Get-HtkkSafeGuiReferenceResult.ps1'):
   text=(ROOT/file).read_text()
   self.assertIsNone(re.search(r"-(?:c?eq|c?ne)\s+'[^']+'\s*,\s*'",text),file)
 def test_row_mode_has_bounded_real_f5_and_keeps_the_original_inspection_branch(self):
  source=(ROOT/'HtkkGtgtPeriodAndSheet.cs').read_text()
  self.assertIn('mode=="gtgt-annex12-row-inspect"',source)
  self.assertIn('owner.Controls.Find("pnF5",true)',source)
  self.assertIn('SendKeys.SendWait("{F5}")',source)
  block=source[source.index(' private void InspectOriginalAnnex12Row('):source.index(' private static bool Annex12CaptionMatched')]
  self.assertNotIn('GetMethod("InsertTable',block);self.assertNotIn('SetValue',block)
  for term in ('GetForegroundWindow()','grid.ContainsFocus','OriginalMessageVisible()','annex12RowBeforeRows==66','annex12RowAfterRows==67','annex12RowBeforeGroupRows==1','annex12RowAfterGroupRows==2','annex12RowInsertActionCount==1'):
   self.assertIn(term,block)
  self.assertIn('finished=true;stage="gtgt-annex12-inspected";Record();',source)
 def test_row_metadata_is_exactly_typed_bounded_and_required_by_success_predicate(self):
  reader=(ROOT/'Get-HtkkSafeGuiReferenceResult.ps1').read_text();fixture=(ROOT/'Test-HtkkSafeGuiReferenceResult.ps1').read_text();probe=(ROOT/'probe-htkk-windows.ps1').read_text()
  keys=re.findall(r"'([^']+)'",re.search(r'\$keys=@\(([^\n]+)\)',reader).group(1));self.assertEqual(len(keys),len(set(keys)))
  for key in ('annex12F5Visible','annex12F5Invoked','annex12RowBeforeMatched','annex12RowAfterMatched','annex12RowSttMatched','annex12RowLocksMatched'):
   self.assertIn(key,keys);self.assertIn(key+'=$false;',fixture)
  for key,maximum in {'annex12RowBeforeRows':10000,'annex12RowAfterRows':10000,'annex12RowBeforeGroupRows':10000,'annex12RowAfterGroupRows':10000,'annex12RowAfterGroupId':10000,'annex12RowInsertActionCount':1}.items():
   self.assertIn(key,keys);self.assertIn(key+'=0;',fixture);self.assertIn(key+'='+str(maximum)+';',reader)
  line=next(line for line in probe.splitlines() if "if($GuiAutomation -eq 'gtgt-annex12-row-inspect'){$matched=" in line)
  for term in ('$lastGui.annex12F5Visible','$lastGui.annex12F5Invoked','$lastGui.annex12RowBeforeMatched','$lastGui.annex12RowAfterMatched','$lastGui.annex12RowAfterRows -eq 67','$lastGui.annex12RowAfterGroupRows -eq 2','$lastGui.annex12RowInsertActionCount -eq 1'):self.assertIn(term,line)
  self.assertIn("@('annex12RowInsertActionCount',2)",fixture);self.assertIn("$row.mode='gtgt-annex12-row-inspect'",fixture)
