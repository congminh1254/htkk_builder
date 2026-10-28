"""Mode routing and bounded metadata contracts; no synthetic test is native proof."""
import ast,pathlib,re,unittest
ROOT=pathlib.Path(__file__).parent
MODES=('inspect','profile-save','gtgt-inspect','gtgt-sheet-inspect','gtgt-amendment-inspect','gtgt-amendment-open-inspect','gtgt-annex12-inspect','gtgt-annex12-row-inspect','gtgt-annex12-input-inspect','gtgt-annex12-numeric-inspect','gtgt-annex12-export-inspect','gtgt-export-inspect','gtgt-roundtrip-inspect','gtgt-web-import-inspect')
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
  line=next(line for line in probe.splitlines() if "if($GuiAutomation -in @('gtgt-annex12-inspect','gtgt-annex12-row-inspect','gtgt-annex12-input-inspect','gtgt-annex12-numeric-inspect','gtgt-annex12-export-inspect')){$matched=" in line)
  for term in ('$lastGui.annexSelectedCount -eq 1','$lastGui.annex12SelectionActionCount -eq 1','$lastGui.annex12StructureMatched','else{-not $lastGui.exportCommandInvoked}','-not $lastGui.webInputVerified'):self.assertIn(term,line)
  self.assertIn("if($GuiAutomation -in @('gtgt-annex12-inspect','gtgt-annex12-row-inspect','gtgt-annex12-input-inspect','gtgt-annex12-numeric-inspect','gtgt-annex12-export-inspect')){$lastGui.periodAnnex12Matched}else{$lastGui.periodNoAnnexMatched}",probe)
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
  for key in ('annex12RowTabClickInvoked','annex12F5Visible','annex12F5Invoked','annex12RowBeforeMatched','annex12RowAfterMatched','annex12RowSttMatched','annex12RowLocksMatched'):
   self.assertIn(key,keys);self.assertIn(key+'=$false;',fixture)
  for key,maximum in {'annex12RowBeforeRows':10000,'annex12RowAfterRows':10000,'annex12RowBeforeGroupRows':10000,'annex12RowAfterGroupRows':10000,'annex12RowAfterGroupId':10000,'annex12RowInsertActionCount':1}.items():
   self.assertIn(key,keys);self.assertIn(key+'=0;',fixture);self.assertIn(key+'='+str(maximum)+';',reader)
  line=next(line for line in probe.splitlines() if "if($GuiAutomation -in @('gtgt-annex12-row-inspect','gtgt-annex12-input-inspect','gtgt-annex12-numeric-inspect','gtgt-annex12-export-inspect')){$matched=" in line)
  for term in ('$lastGui.annex12F5Visible','$lastGui.annex12F5Invoked','$lastGui.annex12RowBeforeMatched','$lastGui.annex12RowAfterMatched','$lastGui.annex12RowAfterRows -eq 67','$lastGui.annex12RowAfterGroupRows -eq 2','$lastGui.annex12RowInsertActionCount -eq 1'):self.assertIn(term,line)
  self.assertIn("@('annex12RowInsertActionCount',2)",fixture);self.assertIn("$row.mode='gtgt-annex12-row-inspect'",fixture)

class AnnexOriginalTabClickContract(unittest.TestCase):
 def test_mouse_click_uses_guarded_public_tab_geometry_and_precedes_original_f5_context(self):
  source=(ROOT/'HtkkGtgtPeriodAndSheet.cs').read_text()
  block=source[source.index(' private void ClickOriginalAnnex12Tab('):source.index(' private void InspectOriginalAnnex12Row(')]
  for term in ('GetMethod("GetSheetTabRectangle",new Type[]{typeof(int)})','geometry.IsPublic','Get(grid,"ClientRectangle")','GetWindowThreadProcessId(grid.Handle','GetForegroundWindow()','grid.ContainsFocus','PostMessage(grid.Handle,0x0201','PostMessage(grid.Handle,0x0202','annex12RowTabClickInvoked=true;Application.DoEvents()'):
   self.assertIn(term,block)
  self.assertNotRegex(block,r'GetMethod\("(?:SheetTabClick|InsertTable)');self.assertNotIn('.Visible=true',block)
  guard=re.search(r'if\((left<0[^;]+)\)throw new InvalidOperationException\(\)',block).group(1).replace('(long)','').replace('||',' or ')
  parsed=ast.parse(guard,mode='eval')
  for node in ast.walk(parsed):self.assertIsInstance(node,(ast.Expression,ast.BoolOp,ast.Or,ast.Compare,ast.Lt,ast.Gt,ast.BinOp,ast.Add,ast.Name,ast.Load,ast.Constant))
  base={'left':4,'top':4,'width':10,'height':12,'clientWidth':100,'clientHeight':100}
  for mutate,rejected in (({},False),({'left':-1},True),({'top':-1},True),({'width':0},True),({'height':0},True),({'left':95},True),({'top':95},True),({'clientWidth':32768},True),({'left':2147483647},True)):
   values={**base,**mutate};self.assertEqual(eval(compile(parsed,'<original tab geometry guard>','eval'),{'__builtins__':{}},values),rejected)
  row=source[source.index(' private void InspectOriginalAnnex12Row('):source.index(' private static bool Annex12CaptionMatched')]
  self.assertLess(row.index('ClickOriginalAnnex12Tab(grid,annex,owner)'),row.index('new object[]{43,20}'))
  self.assertLess(row.index('new object[]{43,20}'),row.index('owner.Controls.Find("pnF5",true)'))
  self.assertLess(row.index('owner.Controls.Find("pnF5",true)'),row.index('SendKeys.SendWait("{F5}")'))
  probe=(ROOT/'probe-htkk-windows.ps1').read_text();line=next(line for line in probe.splitlines() if "if($GuiAutomation -in @('gtgt-annex12-row-inspect','gtgt-annex12-input-inspect','gtgt-annex12-numeric-inspect','gtgt-annex12-export-inspect')){$matched=" in line)
  self.assertIn('$lastGui.annex12RowTabClickInvoked',line)

class AnnexFixedInputsInspectionContract(unittest.TestCase):
 def test_input_edits_are_fixed_fake_ui_inputs_without_hidden_or_derived_assignment(self):
  source=(ROOT/'HtkkGtgtPeriodAndSheet.cs').read_text()
  block=source[source.index(' private void EditAnnex12FixedInput('):source.index(' private static bool Annex12NumberMatched(')]
  coordinates=re.search(r'int\[,] locations=new int\[,]\{([^;]+)\};',block).group(1)
  pairs=[tuple(map(int,pair)) for pair in re.findall(r'\{(\d+),(\d+)\}',coordinates)]
  self.assertEqual(pairs,[(42,4),(42,9),(43,2),(43,12),(43,16),(43,17),(43,18),(43,20),(44,2),(44,12),(44,16),(44,17),(44,18),(44,20)])
  # No ct10, computed subtotal, hidden code, XML or runtime model is assigned.
  self.assertNotIn('SetValue',block);self.assertNotIn('editor.Text=',block)
  self.assertNotRegex(block,r'SetPublic\([^,]+,"(?:Value|Text|Formula|Locked)"')
  for term in ('9999999997-001','NHA MAY GIA LAP - KHONG NOP','FindVendorCombo(editor,0)','SetPublic(vendor,"SelectedIndex",selected)','EscapeSendKeys(value)','SendKeys.SendWait(keys)','annex12InputActionCount++','index!=annex12InputActionCount','"Locked"','!editor.ContainsFocus'):
   self.assertIn(term,block)
 def test_input_observations_are_independent_reads_and_do_not_enable_export(self):
  source=(ROOT/'HtkkGtgtPeriodAndSheet.cs').read_text()
  block=source[source.index(' private void InspectOriginalAnnex12Inputs('):source.index(' private static bool Annex12CaptionMatched')]
  for term in ('CellText(annex,43,32)=="01"','CellText(annex,44,32)=="02"','CellText(annex,row,33)!="101"','CellText(annex,row,42)!="10129087"','CellText(annex,row,35)!="10100"','CellText(annex,row,36)!="10129"','Annex12NumberMatched(annex,42,20,100)','stage="gtgt-annex12-input-inspected"'):
   self.assertIn(term,block)
  self.assertIn('if(mode=="gtgt-annex12-export-inspect"){StartOriginalAnnex12Export(grid,annex);return;}',block);self.assertNotIn('Save',block)
  probe=(ROOT/'probe-htkk-windows.ps1').read_text()
  line=next(x for x in probe.splitlines() if "if($GuiAutomation -in @('gtgt-annex12-input-inspect','gtgt-annex12-numeric-inspect','gtgt-annex12-export-inspect')){$matched=" in x)
  for term in ('annex12InputActionCount -eq 14','annex12InputReadOnlyIdentityMatched','annex12InputIdentityMatched','annex12InputTypesMatched','annex12InputGeographyMatched','annex12InputTaxAuthoritiesMatched','annex12InputPercentagesMatched','annex12InputZeroTaxMatched'):self.assertIn(term,line)
 def test_input_report_is_bounded_and_rejected_outside_its_own_mode(self):
  reader=(ROOT/'Get-HtkkSafeGuiReferenceResult.ps1').read_text();fixture=(ROOT/'Test-HtkkSafeGuiReferenceResult.ps1').read_text()
  self.assertIn('annex12InputActionCount=14;',reader)
  for key in ('annex12InputReadOnlyIdentityMatched','annex12InputIdentityMatched','annex12InputTypesMatched','annex12InputGeographyMatched','annex12InputTaxAuthoritiesMatched','annex12InputPercentagesMatched','annex12InputZeroTaxMatched'):
   self.assertIn(key+'=$false;',fixture)
  self.assertIn("$ExpectedMode -notin @('gtgt-annex12-input-inspect','gtgt-annex12-numeric-inspect','gtgt-annex12-export-inspect')",reader)
  self.assertIn("@('annex12InputActionCount',15)",fixture)
  self.assertLess(fixture.index('$inputCase=[ordered]'),fixture.index('}finally{'))

 def test_source_locked_child_identity_is_observed_without_unlock_or_input(self):
  source=(ROOT/'HtkkGtgtPeriodAndSheet.cs').read_text()
  block=source[source.index(' private void InspectOriginalAnnex12Inputs('):source.index(' private static bool Annex12CaptionMatched')]
  self.assertIn('for(int row=43;row<=44;row++)foreach(int column in new int[]{4,9})',block)
  self.assertIn('!Convert.ToBoolean(Get(Cell(annex,row,column),"Locked"))||CellText(annex,row,column)!=String.Empty',block)
  self.assertIn('annex12InputReadOnlyIdentityMatched=false',block)
  self.assertNotIn('SetPublic',block);self.assertNotIn('SetValue',block)
  documentation=(ROOT.parent/'ANNEX12-INPUT-PROBE.md').read_text()
  self.assertIn('E44:H44 (ct05)',documentation);self.assertIn('J44:L44',documentation)
