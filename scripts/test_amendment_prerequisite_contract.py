"""Offline mode, metadata and publication gates; not original Windows evidence."""
import pathlib,re,unittest
ROOT=pathlib.Path(__file__).parent
MODE='gtgt-amendment-inspect'
FLAGS=('amendmentPriorSaveInvoked','amendmentPriorSaveSuccessAcknowledged','amendmentPriorDirtyCleared','amendmentPriorFileFresh','amendmentPriorFileScopeMatched','amendmentPriorXmlParsed','amendmentPriorMoneyZero','amendmentPriorSavedMoneyZero')
class AmendmentPrerequisiteContract(unittest.TestCase):
 def test_fixed_mode_reaches_all_actual_entry_guards_and_compiler_inputs(self):
  for file in ('New-HtkkX86ReferenceHost.ps1','probe-htkk-windows.ps1','Get-HtkkSafeGuiReferenceResult.ps1'):
   text=(ROOT/file).read_text();self.assertIn(MODE,re.search(r'\[ValidateSet\(([^\n]+)\)',text).group(1),file)
  workflow=(ROOT.parent/'.github/workflows/probe-htkk-windows.yml').read_text()
  self.assertIn(MODE,re.search(r'options: \[([^\n]+)\]',workflow).group(1))
  guard=re.search(r'if \(\$guiAutomation -notin @\(([^\n]+)\)',workflow).group(1);self.assertIn("'"+MODE+"'",guard)
  host=(ROOT/'New-HtkkX86ReferenceHost.ps1').read_text()
  self.assertIn("$amendmentSource=Join-Path $directory 'HtkkGtgtAmendmentInspection.cs'",host)
  self.assertIn('$webComparisonSource,$amendmentSource)',host)
 def test_actual_success_condition_requires_all_saved_file_checks_and_closed_amendment_gate(self):
  text=(ROOT/'probe-htkk-windows.ps1').read_text()
  terminal=next(line for line in text.splitlines() if '$terminal=$nextGui.failureCategory' in line)
  self.assertIn("'gtgt-original-declaration-saved-inspected'",terminal)
  line=next(line for line in text.splitlines() if "if($GuiAutomation -eq 'gtgt-amendment-inspect'){$matched=" in line)
  conditions=line.split('{$matched=$matched -and ',1)[1][:-1].split(' -and ')
  def accepted(values):
   for term in conditions:
    if term.startswith('-not $lastGui.'):
     if values[term[len('-not $lastGui.'):]]:return False
    elif ' -gt ' in term:
     key,number=term[len('$lastGui.'):].split(' -gt ')
     if not values[key]>int(number):return False
    elif ' -eq ' in term:
     key,number=term[len('$lastGui.'):].split(' -eq ')
     if values[key]!=int(number):return False
    elif ' -cmatch ' in term:
     key,pattern=term[len('$lastGui.'):].split(' -cmatch ')
     if not re.fullmatch(pattern.strip("'"),values[key]):return False
    else:
     self.assertTrue(term.startswith('$lastGui.'))
     if not values[term[len('$lastGui.'):]]:return False
   return True
  values={key:True for key in FLAGS+('gtgtSignatureReady','gtgtMonetaryZero','gtgtAutoCalculationReady','gtgtBusinessInstanceMatched')}
  values.update(amendmentPriorSavedMoneyCount=27,amendmentPriorFileBytes=100,amendmentPriorFileSha256='a'*64,gtgtEmptyMonetaryCount=0,amendmentLifecycleVerified=False,exportCommandInvoked=False,webInputVerified=False)
  self.assertTrue(accepted(values))
  for key in FLAGS:
   changed=dict(values);changed[key]=False;self.assertFalse(accepted(changed),key)
  for key,value in (('amendmentLifecycleVerified',True),('exportCommandInvoked',True),('webInputVerified',True),('amendmentPriorFileSha256','raw private XML'),('amendmentPriorFileBytes',0)):
   changed=dict(values);changed[key]=value;self.assertFalse(accepted(changed),key)
 def test_new_metadata_is_unique_typed_defaulted_and_cannot_claim_full_amendment(self):
  text=(ROOT/'Get-HtkkSafeGuiReferenceResult.ps1').read_text();fixture=(ROOT/'Test-HtkkSafeGuiReferenceResult.ps1').read_text()
  keys=re.findall(r"'([^']+)'",re.search(r'\$keys=@\(([^\n]+)\)',text).group(1));self.assertEqual(len(keys),len(set(keys)))
  for key in (*FLAGS,'amendmentLifecycleVerified'):
   self.assertIn(key,keys);self.assertIn(key+'=$false;',fixture)
  self.assertIn('amendmentPriorFileBytes=262144;',text)
  self.assertIn('or $value.amendmentLifecycleVerified)',text)
  self.assertIn("$ExpectedMode -cne 'gtgt-amendment-inspect'",text)
 def test_original_save_uses_button_and_read_only_bounded_internal_file_observation(self):
  source=(ROOT/'HtkkGtgtAmendmentInspection.cs').read_text()
  # Loaded workbook sheets are not selected annexes: the real no-annex D1 has11.
  self.assertIn('gtgtSheets!=11||!periodNoAnnexMatched||annexSelected!=0',source)
  self.assertNotIn('gtgtSheets!=1||',source)
  self.assertIn('Named(owner,"cmdSave")',source);self.assertIn('save.PerformClick();',source)
  self.assertIn('Đã ghi dữ liệu thành công!',source);self.assertIn('isDataChanged',source)
  self.assertIn('OriginalPriorCandidates().Length!=0',source);self.assertIn('files.Length!=1',source)
  self.assertIn('SearchOption.TopDirectoryOnly',source);self.assertIn('settings.ProhibitDtd=true;settings.XmlResolver=null',source)
  for forbidden in ('File.Write','File.Create','SetValue(','WinDoWorkSave','Invoke('):self.assertNotIn(forbidden,source)
  self.assertIn('amendmentLifecycleVerified',source);self.assertIn('gtgt-original-declaration-saved-inspected',source)

 def test_diagnostics_are_fixed_stages_without_native_message_or_path_content(self):
  source=(ROOT/'HtkkGtgtAmendmentInspection.cs').read_text()
  for stage in ('save-modal-observed','save-modal-content-checking','save-modal-button-checking','save-modal-matched','prior-file-enumerating','prior-file-missing','prior-file-not-unique','prior-file-size-checking','prior-file-parsing','prior-money-checking'):
   self.assertIn('"gtgt-amendment-'+stage+'"',source)
  self.assertNotRegex(source,r'stage\s*=\s*(form|file|labels|amendmentPriorDirectory)\b')

 def test_prior_candidate_uses_exact_geographic_source_filename_for_this_fixed_case(self):
  source=(ROOT/'HtkkGtgtAmendmentInspection.cs').read_text()
  actual=re.search(r'OriginalPriorFileName="([^"]+)"',source).group(1)
  # Source060000A3 maps NopTheoTinhCQT3 to CQTQL+authority;060000A2
  # monthlyD1 concatenates code, tax item, month+year and dotless XMLversion.
  expected='01_GTGT_TT80'+'_CQTQL'+'10129'+'_'+'1701'+'_'+'10'+'2026'+'_'+'2.8.3'.replace('.','')+'.xml'
  self.assertEqual(actual,expected)
  self.assertIn('String.Equals(file.Name,OriginalPriorFileName,StringComparison.Ordinal)',source)
  self.assertNotIn('Regex.IsMatch(file.Name',source)
  for wrong in ('01_GTGT_TT80_1701_102026_283.xml',expected.replace('10129','10100'),expected.replace('_102026_','_092026_'),'bs1_'+expected,expected+'.bak'):
   self.assertNotEqual(actual,wrong)

 def test_all_emitted_fixed_amendment_stages_are_accepted_by_actual_reader(self):
  source=(ROOT/'HtkkGtgtAmendmentInspection.cs').read_text()
  reader=(ROOT/'Get-HtkkSafeGuiReferenceResult.ps1').read_text()
  allowed=set(re.findall(r"'([^']+)'",re.search(r'\$stages=@\(([^\n]+)\)',reader).group(1)))
  assignments=' '.join(re.findall(r'\bstage\s*=\s*([^;]+);',source))
  emitted=set(re.findall(r'"([^"]+)"',assignments))
  self.assertGreater(len(emitted),10)
  self.assertFalse(emitted-allowed,'Reader would hide diagnostic stage: '+str(emitted-allowed))
