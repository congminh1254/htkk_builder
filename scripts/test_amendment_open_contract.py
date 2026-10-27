"""Bounded B1 routing and publication contracts; not original Windows proof."""
import pathlib,re,unittest
ROOT=pathlib.Path(__file__).parent
MODE='gtgt-amendment-open-inspect'
FLAGS=('amendmentOpenCloseInvoked','amendmentOpenPriorClosed','amendmentOpenDefaultsMatched','amendmentOpenConfirmInvoked','amendmentOpenPeriodMatched','amendmentOpenSourcesMatched','amendmentOpenKhbsSheetsObserved','amendmentOpenPriorUnchanged')
COUNTS={'amendmentOpenKhbsRows':10000,'amendmentOpenKhbsColumns':512,'amendmentOpenExplanationRows':10000,'amendmentOpenExplanationColumns':512}
class AmendmentOpeningContract(unittest.TestCase):
 def test_mode_routes_to_original_prior_save_then_clean_close_and_original_b1_controls(self):
  source=(ROOT/'HtkkGtgtAmendmentOpenInspection.cs').read_text();prior=(ROOT/'HtkkGtgtAmendmentInspection.cs').read_text();period=(ROOT/'HtkkGtgtPeriodAndSheet.cs').read_text();navigation=(ROOT/'HtkkGtgtReferenceNavigation.cs').read_text()
  self.assertIn('mode=="'+MODE+'"',source);self.assertIn('if(mode=="'+MODE+'"){CloseOriginalPriorForAmendment();return;}',prior)
  self.assertIn('if(AmendmentReopening()){ConfigureOriginalAmendmentOpen(period);return;}',period)
  self.assertIn('navigationPhase=="waiting-amendment-sheet"',navigation)
  for name in ('"cmdExit"','"isDataChanged"','close.PerformClick()','SetCheck(Named(period,"OptBosung"),true)','"txtLan"','"mskNgayLapKHBS"','number.Text.Trim()=="1"','confirm.PerformClick()'):
   self.assertIn(name,source)
  self.assertNotIn('SetText(',source);self.assertNotIn('.SetValue(',source);self.assertNotIn('File.Write',source)
  self.assertNotIn('GetMethod("GetPeriodInfo"',source);self.assertNotIn('GetMethod("OpenToKhai"',source)
 def test_every_own_stage_is_allowlisted_and_only_complete_open_is_terminal(self):
  source=(ROOT/'HtkkGtgtAmendmentOpenInspection.cs').read_text();reader=(ROOT/'Get-HtkkSafeGuiReferenceResult.ps1').read_text();probe=(ROOT/'probe-htkk-windows.ps1').read_text()
  allowed=set(re.findall(r"'([^']+)'",re.search(r'\$stages=@\(([^\n]+)\)',reader).group(1)))
  emitted=set(re.findall(r'"([^\"]+)"',' '.join(re.findall(r'\bstage\s*=\s*([^;]+);',source))))
  self.assertFalse(emitted-allowed)
  terminal=next(line for line in probe.splitlines() if '$terminal=$nextGui.failureCategory' in line)
  self.assertIn("'gtgt-amendment-open-inspected'",terminal)
  for pending in emitted-{'gtgt-amendment-open-inspected'}:self.assertNotIn("'"+pending+"'",terminal)
 def test_reader_exact_keys_bounds_and_default_scope_keep_all_old_modes_closed(self):
  reader=(ROOT/'Get-HtkkSafeGuiReferenceResult.ps1').read_text();fixture=(ROOT/'Test-HtkkSafeGuiReferenceResult.ps1').read_text()
  keys=re.findall(r"'([^']+)'",re.search(r'\$keys=@\(([^\n]+)\)',reader).group(1));self.assertEqual(len(keys),len(set(keys)))
  for flag in FLAGS:self.assertIn(flag,keys);self.assertIn(flag+'=$false;',fixture)
  for key,maximum in COUNTS.items():self.assertIn(key,keys);self.assertIn(key+'='+str(maximum)+';',reader);self.assertIn(key+'=0;',fixture)
  self.assertIn("$ExpectedMode -cne 'gtgt-amendment-open-inspect' -and (",reader)
  self.assertIn("throw 'Unsafe B1 opening accepted'",fixture)
  self.assertIn('or $value.amendmentLifecycleVerified)',reader)
 def test_open_success_requires_every_original_stage_and_preserves_no_export_gate(self):
  probe=(ROOT/'probe-htkk-windows.ps1').read_text()
  line=next(line for line in probe.splitlines() if "if($GuiAutomation -eq '"+MODE+"'){$matched=" in line)
  for flag in FLAGS:self.assertIn(' -and $lastGui.'+flag,line)
  for key in COUNTS:self.assertIn('$lastGui.'+key+' -gt 0',line)
  for required in ('amendmentPriorSaveSuccessAcknowledged','amendmentPriorDirtyCleared','amendmentPriorSavedMoneyCount -eq 27','-not $lastGui.amendmentLifecycleVerified','-not $lastGui.exportCommandInvoked','-not $lastGui.webInputVerified'):self.assertIn(required,line)
 def test_khbs_source_and_actual_active_tabs_are_observed_without_forcing_sheet_visibility(self):
  source=(ROOT/'HtkkGtgtAmendmentOpenInspection.cs').read_text()
  self.assertEqual(source.count('Hash(Path.Combine(root,"InterfaceTemplates/'),5)
  for resource in ('KHBS_01_TT80_DIA_BAN_283.xml','KHBS_01_DIA_BAN_xml.xml','KHBS_01_1_TT80_283.xml','KHBS_01_1_TT80_xml.xml','KHBS_01_GTGT_TT80_283.xsd'):self.assertIn(resource,source)
  self.assertIn('Get(info,"Active")',source);self.assertIn('GetSheetTabRectangle',source)
  self.assertIn('Get(period,"LoaiToKhai"),CultureInfo.InvariantCulture)=="B"',source)
  self.assertIn('Get(period,"SoLan"),CultureInfo.InvariantCulture)=="1"',source)
  self.assertIn('parsed.Date==DateTime.Now.Date',source)
  self.assertIn('InspectOriginalPriorFile();ReadSavedHeader()',source)
  self.assertNotIn('Visible=',source);self.assertNotIn('ActiveSheetIndex',source)
 def test_new_partial_is_an_actual_compiler_input_and_old_prior_mode_still_routes(self):
  host=(ROOT/'New-HtkkX86ReferenceHost.ps1').read_text();source=(ROOT/'HtkkGtgtAmendmentInspection.cs').read_text()
  self.assertIn("$amendmentOpenSource=Join-Path $directory 'HtkkGtgtAmendmentOpenInspection.cs'",host)
  self.assertIn('$amendmentSource,$amendmentOpenSource,$annexExportSource)',host)
  self.assertIn('!AmendmentInspectionMode()',source);self.assertIn('gtgt-original-declaration-saved-inspected',source)

class AmendmentReaderTypeBoundaryTests(unittest.TestCase):
 def test_opening_flags_are_individually_boolean_typed_not_just_allowlisted(self):
  text=(ROOT/'Get-HtkkSafeGuiReferenceResult.ps1').read_text()
  boolean_line=next(line for line in text.splitlines() if '$value[$key] -isnot [bool]' in line)
  typed=set(re.findall(r"'([^']+)'",boolean_line))
  self.assertTrue(set(FLAGS)<=typed,set(FLAGS)-typed)
 def test_string_field_validation_does_not_gain_a_leading_array_element_during_merge(self):
  text=(ROOT/'Get-HtkkSafeGuiReferenceResult.ps1').read_text()
  self.assertNotRegex(text,r'@\(\s*,')
  line=next(line for line in text.splitlines() if '$value[$key] -isnot [string]' in line and 'foreach($key' in line)
  self.assertEqual(re.findall(r"'([^']+)'",line),['format','mode','stage','failureCategory','editorKind','runtime','saveDialogKind','invalid'])

 def test_second_menu_traversal_budget_is_restricted_to_the_new_b1_mode(self):
  reader=(ROOT/'Get-HtkkSafeGuiReferenceResult.ps1').read_text();fixture=(ROOT/'Test-HtkkSafeGuiReferenceResult.ps1').read_text()
  self.assertIn("menuClickCount=$(if($ExpectedMode -ceq 'gtgt-amendment-open-inspect'){6}else{3})",reader)
  self.assertIn('$open.menuClickCount=4',fixture)
  self.assertIn("@{key='menuClickCount';value=7}",fixture)

class OriginalCleanCloseTimingTests(unittest.TestCase):
 def test_close_is_invoked_once_then_observed_across_ui_turns_without_forcing_state(self):
  text=(ROOT/'HtkkGtgtAmendmentOpenInspection.cs').read_text();navigation=(ROOT/'HtkkGtgtReferenceNavigation.cs').read_text()
  block=text[text.index(' private void ObserveOriginalAmendmentPriorClosed()'):text.index(' private static bool CurrentOriginalAmendmentDate')]
  self.assertIn('if(!amendmentOpenPriorClosed){stage="gtgt-amendment-prior-close-waiting";Record();return;}',block)
  self.assertNotIn('PerformClick',block);self.assertNotIn('SetValue',block);self.assertNotIn('Visible=',block)
  self.assertIn('if(navigationPhase=="waiting-amendment-prior-close"){ObserveOriginalAmendmentPriorClosed();return;}',navigation)
