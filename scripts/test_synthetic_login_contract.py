import pathlib,re,shutil,subprocess,tempfile,unittest
import native_preflight_retry as retry
import test_native_preflight_retry as base
ROOT=pathlib.Path(__file__).parent
LOGIN=(ROOT/'Invoke-HtkkSyntheticLogin.ps1').read_text(encoding='utf-8')
PROBE=(ROOT/'probe-htkk-windows.ps1').read_text(encoding='utf-8')
SAMPLE_KEYS=('atSeconds','loginHidden','profileRecognized','mainCaptionForms','profileCaptionForms','emptyCaptionForms','unreadCaptionForms','otherCaptionForms','nativeDialogs','managedWindows','statics','buttons','truncated')
def native_source():
 start=LOGIN.index("@'\n")+3;return LOGIN[start:LOGIN.index("\n'@",start)]
class SyntheticLoginContract(unittest.TestCase):
 # Release-blocking flake (e.g. run 42291169925 attempts 1+2): every failing attempt today had
 # startupWaitSeconds 17-43 (mostly >=27) while successful runs had 11-17 (a few 22-33), i.e.
 # slow runners were still loading the new profile when the fixed 20 s post-login budget ended.
 def test_post_login_deadline_is_bounded_and_longer_than_former_20_seconds(self):
  self.assertIn('[ValidateRange(5,90)][int]$PostLoginDeadlineSeconds=60',LOGIN)
  self.assertIn('}while($clock.Elapsed.TotalSeconds -lt $deadline)',LOGIN)
  self.assertNotIn('-lt 20)',LOGIN)
  # A recognized profile still ends the wait immediately; the root exiting ends it too.
  loop=LOGIN[LOGIN.index('  do {\n   if($retained.HasExited)'):LOGIN.index('}while($clock.Elapsed.TotalSeconds -lt $deadline)')]
  self.assertIn("if($safe.loginHidden -and $safe.profileWindowObserved){break}",loop)
  self.assertIn("if($retained.HasExited){$safe.status='root-exited';return $safe}",loop)
  self.assertLess(loop.index('Sample($RootProcessId)'),loop.index('){break}'))
 def test_timeline_is_bounded_change_only_and_fixed_schema(self):
  self.assertIn('if($signature -cne $lastSignature){if($timeline.Count -lt 24){$timeline.Add($sample)}else{$safe.postLoginTimelineTruncated=$true};$lastSignature=$signature}',LOGIN)
  self.assertIn("Where-Object { $_ -ne 'atSeconds' }",LOGIN)
  sample=re.search(r"\[ordered\]@\{(atSeconds=[^}]*)\}",LOGIN).group(1)
  self.assertEqual(tuple(p.split('=')[0]for p in sample.split(';')),SAMPLE_KEYS)
  # Only integers/booleans: every sample value is a fixed native counter or a bool parameter.
  for part in sample.split(';')[3:]:self.assertRegex(part.split('=')[1],r'^\$n::Sample[A-Za-z]+$')
  for key in ('postLoginDeadlineSeconds=0','postLoginWaitSeconds=0','postLoginPollCount=0','profileRecognitionSeconds=-1','postLoginTimeline=@()','postLoginTimelineTruncated=$false'):self.assertIn(key,LOGIN)
 def test_native_sample_reports_caption_categories_never_text(self):
  source=native_source();body=source[source.index('public static void Sample('):source.index('public static void CountAfter(')]
  self.assertNotIn('public static string',body)
  for counter in ('SampleMain++','SampleProfile++','SampleEmpty++','SampleUnread++','SampleOther++','SampleNativeDialogs++'):self.assertIn(counter,body)
  self.assertIn('if(!TryText(window,out caption))SampleUnread++;',body)
  self.assertIn('if(++count>2048||clock.ElapsedMilliseconds>2000){SampleTruncated=true;return false;}',body)
 @unittest.skipUnless(shutil.which('mcs'),'mono mcs not installed')
 def test_native_helper_compiles(self):
  with tempfile.TemporaryDirectory()as folder:
   path=pathlib.Path(folder)/'L.cs';path.write_text(native_source(),encoding='utf-8')
   subprocess.run(['mcs','-target:library','-warn:0','-out:'+str(pathlib.Path(folder)/'L.dll'),str(path)],check=True,capture_output=True)
 def test_probe_records_reference_stage_without_changing_failure_contract(self):
  at=PROBE.index("if ($report.syntheticLogin.status -ne 'synthetic-profile-window-observed') {")
  block=PROBE[at:PROBE.index("throw 'SYNTHETIC_LOGIN_NOT_VERIFIED'",at)]
  self.assertIn("$report.syntheticLogin['referenceAutomationStageAtLoginFailure']=$loginGui.stage",block)
  self.assertIn("$loginGui.status -eq 'valid'",block)
  self.assertNotIn('guiReferenceAutomation=',block);self.assertNotIn('$report.guiReferenceAutomation',block);self.assertNotIn('WriteAllText',block)
  self.assertLess(at,PROBE.index('$report.guiAutomationPermitBoundary.authorizationAttempted=$true'))
 def test_startup_retry_still_applies_with_new_diagnostics(self):
  f=base.NativePreflightRetry.fixture(base.NativePreflightRetry(),'startup')
  sample=dict(zip(SAMPLE_KEYS,(0,True,False,0,0,0,2,0,0,8,4,2,False)))
  f['records'][0]['syntheticLogin'].update(newIdClicked=True,nextOwnedWindowObserved=True,profileMainCaptionMatched=False,postLoginDeadlineSeconds=60,postLoginWaitSeconds=60,postLoginPollCount=30,profileRecognitionSeconds=-1,postLoginTimeline=[sample],postLoginTimelineTruncated=False,referenceAutomationStageAtLoginFailure='waiting-for-profile')
  self.assertEqual(retry.classify(f['jobs'],f['records']),'synthetic-profile-startup-not-observed')
if __name__=='__main__':unittest.main()
