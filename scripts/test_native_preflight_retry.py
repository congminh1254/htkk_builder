import copy,json,pathlib,unittest
import native_preflight_retry as retry
SOURCE='a'*40;BUILDER='b'*40;INPUT='c'*40
class NativePreflightRetry(unittest.TestCase):
 def fixture(self,kind='framework'):
  run={'id':123,'repository':{'full_name':retry.BUILDER},'path':'.github/workflows/probe-htkk-windows.yml','event':'workflow_dispatch','head_branch':'main','head_sha':BUILDER,'run_attempt':1,'status':'completed','conclusion':'failure'}
  steps=[{'name':retry.FRAMEWORK,'conclusion':'failure'},{'name':retry.PROBE,'conclusion':'skipped'}]
  records=[{'format':'htkk-framework-uia-boundary-v1','status':'process-timeout','timedOut':True,'processStopped':True,'exitCode':None,'phase':'complete'}]
  if kind=='startup':
   steps=[{'name':retry.PROBE,'conclusion':'failure'},{'name':retry.RETAIN,'conclusion':'failure'}]
   records=[dict(guiAutomationPermitBoundary={'uniquePathVerified':True,'initiallyAbsent':True,'authorizationAttempted':False,'absentAfterCleanup':True},guiReferenceAutomationMode='gtgt-web-import-inspect',version='5.8.1',stage='blocked',blockedReason='SYNTHETIC_LOGIN_NOT_VERIFIED',guiReferenceAutomation=None,referenceHostResult={'status':'original-starting'},sourceHashesVerified=True,originalSourcesUnmodified=True,officialDistributionFilesVerified=True,msiAuthenticodeValid=True,nativeHelperJobsStopped=True,hostOutboundBlocked=True,originalOutboundBlocked=True,taxDataUsed=False,runtimeRoundTrip=False,supplierProcessBoundary={k:True for k in ('cleanupVerified','supplierStopped','rootStopped','jobEmpty')},syntheticLogin={'status':'next-window-not-yet-identified','fixtureDirectoryPreexisting':False,'fixtureDirectoryCreated':True,'syntheticIdentifierOnly':True,'realTaxpayerDataUsed':False,'inputVerified':True,'loginClicked':True,'loginHidden':True,'profileWindowObserved':False,'runtimeRoundTrip':False})]
  jobs={'total_count':2,'jobs':[{'name':'readiness','id':456,'conclusion':'failure','steps':steps},{'name':'report_failure','conclusion':'success'}]}
  status={'state':'failure','description':'failed input:'+INPUT,'target_url':'https://github.com/congminh1254/htkk_builder/actions/runs/123'};calls=[];state=set()
  def get(repo,path):return records if path.endswith('/logs')else jobs if '/jobs?'in path else run
  def send(*args):calls.append(args)
  def recover():return retry.recover(status,'htkk-native/zero',SOURCE,BUILDER,INPUT,get,lambda x:x,send,'actions-placeholder','status-placeholder',state)
  return locals()
 def test_only_two_known_pre_tax_failures_retry_once_and_do_not_qualify(self):
  for kind in ['framework','startup']:
   f=self.fixture(kind);self.assertTrue(f['recover']());self.assertEqual(len(f['calls']),2);self.assertIn('/rerun-failed-jobs',f['calls'][0][0]);self.assertEqual(f['calls'][1][2]['state'],'pending')
   self.assertTrue(f['recover']());self.assertEqual(len(f['calls']),2)
   f['run'].update(run_attempt=2,status='in_progress',conclusion=None);self.assertTrue(f['recover']());self.assertEqual(len(f['calls']),2)
   f['run'].update(status='completed',conclusion='failure');self.assertFalse(f['recover']());self.assertEqual(len(f['calls']),2)
 def test_rejects_unknown_boundary_failed_cleanup_completed_tax_or_retry2(self):
  for kind in ['other-step','phase','stopped','type','callback','branch','builder','attempt','input','url']:
   f=self.fixture()
   if kind=='other-step':f['steps'][0]['name']='Tax comparison failed'
   if kind=='phase':f['records'][0]['phase']='unknown'
   if kind=='stopped':f['records'][0]['processStopped']=False
   if kind=='type':f['records'][0]['timedOut']=1
   if kind=='callback':f['jobs']['jobs'][1]['conclusion']='failure'
   if kind=='branch':f['run']['head_branch']='other'
   if kind=='builder':f['run']['head_sha']='d'*40
   if kind=='attempt':f['run']['run_attempt']=2
   if kind=='input':f['status']['description']='failed input:'+'d'*40
   if kind=='url':f['status']['target_url']='https://example.com/runs/123'
   self.assertFalse(f['recover'](),kind);self.assertEqual(f['calls'],[])
  for kind in ['gui','money','profile','cleanup','source','signature','unknown-login','mode']:
   f=self.fixture('startup');r=f['records'][0]
   if kind=='mode':r['guiReferenceAutomationMode']='gtgt-annex12-row-inspect'
   if kind=='gui':r['guiReferenceAutomation']={'status':'failed','stage':'tax-comparison'}
   if kind=='money':r['taxDataUsed']=True
   if kind=='profile':r['syntheticLogin']['profileWindowObserved']=True
   if kind=='cleanup':r['supplierProcessBoundary']['rootStopped']=False
   if kind=='source':r['originalSourcesUnmodified']=False
   if kind=='signature':r['msiAuthenticodeValid']=False
   if kind=='unknown-login':r['syntheticLogin']['status']='other'
   self.assertFalse(f['recover'](),kind);self.assertEqual(f['calls'],[])
 def test_action_post_failure_does_not_claim_pending_or_retry_and_status_failure_cannot_double_post(self):
  f=self.fixture();calls=[]
  def fail(*args):calls.append(args);raise RuntimeError('fixed-test-failure')
  args=(f['status'],'htkk-native/zero',SOURCE,BUILDER,INPUT,f['get'],lambda x:x,fail,'actions-placeholder','status-placeholder',f['state'])
  with self.assertRaises(RuntimeError):retry.recover(*args)
  self.assertEqual(len(calls),1);self.assertEqual(f['state'],set())

 def test_failure_discovery_waits_for_retry_but_never_publishes_or_accepts_failed_evidence(self):
  import test_caseflow_batch as original
  f=original.fixture();f['statuses'][0].update(state='failure',description='failed input:'+f['publication']['cases'][0]['artifactCommit'])
  called=[]
  self.assertIsNone(original.batch.discover(f['publication'],original.BUILDER,f['statuses'],f['get'],retry=lambda *args:called.append(args)or True));self.assertEqual(len(called),1)
  with self.assertRaises(ValueError):original.batch.discover(f['publication'],original.BUILDER,f['statuses'],f['get'],retry=lambda *args:False)
  f['statuses'][0]['state']='success';f['runs'][100]['conclusion']='failure'
  with self.assertRaises(ValueError):original.batch.discover(f['publication'],original.BUILDER,f['statuses'],f['get'],retry=lambda *args:True)
 def test_pending_post_failure_preserves_single_action_attempt(self):
  f=self.fixture();calls=[]
  def send(*args):
   calls.append(args)
   if len(calls)==2:raise RuntimeError('fixed-status-failure')
  with self.assertRaises(RuntimeError):retry.recover(f['status'],'htkk-native/zero',SOURCE,BUILDER,INPUT,f['get'],lambda x:x,send,'actions-placeholder','status-placeholder',f['state'])
  self.assertEqual(f['state'],{'123'});self.assertEqual(len(calls),2);self.assertTrue(f['recover']());self.assertEqual(f['calls'],[])

 def test_missing_or_inconsistent_permission_attestation_cannot_retry_unknown_gui_progress(self):
  for key in ['missing','uniquePathVerified','initiallyAbsent','authorizationAttempted','absentAfterCleanup','type']:
   f=self.fixture('startup');r=f['records'][0]
   if key=='missing':del r['guiAutomationPermitBoundary']
   elif key=='type':r['guiAutomationPermitBoundary']['authorizationAttempted']=0
   else:r['guiAutomationPermitBoundary'][key]=not r['guiAutomationPermitBoundary'][key]
   self.assertFalse(f['recover'](),key);self.assertEqual(f['calls'],[])
 def test_permission_attestation_is_after_identity_before_launch_and_before_owned_path_removal(self):
  root=pathlib.Path(__file__).parent;source=(root/'probe-htkk-windows.ps1').read_text()
  self.assertLess(source.index("$report.syntheticLogin.status -ne 'synthetic-profile-window-observed'"),source.index('$report.guiAutomationPermitBoundary.authorizationAttempted=$true'))
  self.assertLess(source.index('$report.guiAutomationPermitBoundary.authorizationAttempted=$true'),source.index("[IO.File]::WriteAllText($referencePreparation.guiAutomationPermitPath,'profile-save'"))
  self.assertLess(source.index('guiAutomationPermitBoundary.absentAfterCleanup=-not'),source.index('foreach($owned in $referenceOwnedFiles)'))
  self.assertTrue("WaitingForProfileSavePermit" in (root/'HtkkGuiReferenceAutomation.cs').read_text())

 def test_failure_callback_while_workflow_cleanup_is_running_waits_without_rerun(self):
  f=self.fixture();f['run'].update(status='in_progress',conclusion=None);self.assertTrue(f['recover']());self.assertEqual(f['calls'],[])
  f['run'].update(status='completed',conclusion='failure');self.assertTrue(f['recover']());self.assertEqual(len(f['calls']),2)
 def test_discovery_scans_failures_but_never_fetches_case_proofs_until_all_statuses_ready(self):
  import test_caseflow_batch as original
  f=original.fixture();f['statuses'][-1]['state']='pending';calls=[]
  def no_read(*args):calls.append(args);raise AssertionError('No evidence reads while cohort pending')
  self.assertIsNone(original.batch.discover(f['publication'],original.BUILDER,f['statuses'],no_read));self.assertEqual(calls,[])
  f['statuses'][0]['state']='pending';f['statuses'][-1].update(state='failure',description='failed input:'+f['publication']['cases'][-1]['artifactCommit']);retries=[]
  self.assertIsNone(original.batch.discover(f['publication'],original.BUILDER,f['statuses'],no_read,retry=lambda *args:retries.append(args)or True));self.assertEqual(len(retries),1);self.assertEqual(calls,[])

 def test_no_log_or_artifact_download_while_last_success_callback_still_has_poststeps_running(self):
  import test_caseflow_batch as original
  f=original.fixture();f['runs'][112]['status']='in_progress';calls=[]
  def metadata_only(repo,path):
   calls.append(path)
   if not path.startswith('actions/runs/')or '/jobs' in path:raise AssertionError('No heavy evidence reads before all runs complete')
   return f['get'](repo,path)
  self.assertIsNone(original.batch.discover(f['publication'],original.BUILDER,f['statuses'],metadata_only));self.assertEqual(len(calls),13)
