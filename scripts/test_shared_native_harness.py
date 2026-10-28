"""Shared control policies and compile-time stage boundary; no native parity claims."""
import os
import pathlib
import re
import subprocess
import unittest
from native_contract_test_support import registry, assert_compile_input
ROOT=pathlib.Path(__file__).parent

class SharedNativeHarness(unittest.TestCase):
 def test_all_controller_stage_assignments_are_typed_including_ternaries_and_editor_parameters(self):
  stage_names={s['enumName'] for s in registry()['stages']}
  controller_files=[]
  for file in ROOT.glob('Htkk*.cs'):
   text=file.read_text()
   if 'partial class HtkkGuiReferenceAutomation' not in text:continue
   controller_files.append(file)
   self.assertNotRegex(text,r'\bstage\s*=')
   self.assertNotIn('string nextStage',text)
   referenced=set(re.findall(r'HtkkAutomationStage\.([A-Za-z0-9_]+)',text))
   self.assertFalse(referenced-stage_names,(file.name,referenced-stage_names))
   for expression in re.findall(r'SetStage\(([^;]+)\);',text):
    self.assertNotRegex(expression,r'(?:^|[?:])\s*"',(file.name,expression))
  self.assertGreater(len(controller_files),5)
  main=(ROOT/'HtkkGuiReferenceAutomation.cs').read_text()
  self.assertIn('HtkkAutomationStage[] codeStages=',main)
  self.assertNotIn('set{currentStage=',main)

 def test_adapter_business_inputs_do_not_reside_in_shared_profile_editor(self):
  main=(ROOT/'HtkkGuiReferenceAutomation.cs').read_text()
  edit=main[main.index(' private void Edit('):main.index(' private static void SetPublic(')]
  self.assertNotIn('webCase',edit);self.assertNotIn('CreditCt21',edit)
  self.assertIn('HtkkNativeUiHarness.BeginCellEdit',edit)
  self.assertIn('HtkkNativeUiHarness.SelectCombo',edit)
  shared=(ROOT/'HtkkNativeUiHarness.cs').read_text()
  for forbidden in ('D1','GTGT','webCase','GetMethod("Calculate','File.Write','XmlDocument','.Visible=','.Locked='):
   self.assertNotIn(forbidden,shared)
  for mode in registry()['modes']:
   assert_compile_input(self,mode,'HtkkNativeUiHarness.cs')

 def test_original_profile_lifecycle_owns_close_state_outside_adapter(self):
  nav=(ROOT/'HtkkGtgtReferenceNavigation.cs').read_text()
  self.assertIn('profileLifecycle.Bind(profileOwner,closeButton,spread)',nav)
  self.assertIn('profileLifecycle.RequestClose()',nav)
  self.assertNotIn('pendingProfileClose',nav);self.assertNotIn('closingProfileForm',nav)
  self.assertLess(nav.index('ReadSavedHeader();if('),nav.index('profileLifecycle.RequestClose()'))

 def test_dialog_resolver_is_shared_and_preserves_pid_owner_editor_identity_guards(self):
  shared=(ROOT/'HtkkNativeUiHarness.cs').read_text()
  export=(ROOT/'HtkkGtgtExportInspection.cs').read_text()
  self.assertIn('HtkkNativeFileDialog.Find(expectedTitle)',export)
  for required in ('pid==own','ownerPid!=own','dialogs.Count!=1','edits.Count!=1','id==1001||id==1148','parentClass!="ComboBox"&&parentClass!="ComboBoxEx32"'):
   self.assertIn(required,shared)
  # The controller retains artifact/focus/typing/submission checks; lookup alone cannot approve a file.
  for required in ('Hash(desiredPath)!=RoundtripInputHash()','filenameFocusGate.Observe(dialog,edit,ownsFocus)','GetForegroundWindow()!=dialog||GetFocus()!=edit','NativeText(edit,false)!=desiredPath','NativeText(dialog,false)!=expectedTitle'):
   self.assertIn(required,export)

 def test_actual_production_profile_policy_handles_dirty_foreign_and_asynchronous_closes(self):
  pwsh=os.environ.get('HTKK_PWSH')
  if not pwsh:
   import shutil
   pwsh=shutil.which('pwsh')
  if not pwsh and pathlib.Path('/tmp/htkk-pwsh/runtime/pwsh').is_file():pwsh='/tmp/htkk-pwsh/runtime/pwsh'
  if not pwsh:self.skipTest('PowerShell unavailable; Windows boundary suite runs policy fixture')
  env={key:value for key,value in os.environ.items() if key in ('PATH','HOME','LANG','TMPDIR','SystemRoot','WINDIR','TEMP','TMP')}
  env.update(POWERSHELL_TELEMETRY_OPTOUT='1',POWERSHELL_UPDATECHECK='Off')
  run=subprocess.run([pwsh,'-NoProfile','-File',str(ROOT/'Test-HtkkNativeProfileLifecycle.ps1')],env=env,capture_output=True,text=True,timeout=40)
  self.assertEqual(run.returncode,0,run.stdout+run.stderr)
  self.assertIn('PASS: original profile lifecycle',run.stdout)
