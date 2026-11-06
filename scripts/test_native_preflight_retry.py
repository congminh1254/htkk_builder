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
  if kind=='profile-close':
   steps=[{'name':retry.PROBE,'conclusion':'failure'},{'name':retry.RETAIN,'conclusion':'failure'}]
   gui=dict(retry.PROFILE_SAVED,editorKind='combo',visibleForms=1,sheetRows=75,sheetColumns=22,controlKinds={'form':1,'spread':1},webCaseId='01GTGT-zero-M10-2026',waitSeconds=60,periodControls={},mainMenuObserved=False,d1MenuClicked=False,gtgtPeriodObserved=False,menuClickCount=0,periodConfirmInvoked=False,gtgtSheetObserved=False,webInputVerified=False,webTaxValuesMatched=False,webCaseEditCount=0,gtgtCaseMoneyCount=0,gtgtCaseMismatchMask=0,gtgtCaseMoneyMatched=False,exportCommandInvoked=False,exportSha256='',exportFilenameParentKind='not-observed',roundtripImportSucceeded=False,roundtripXmlExactMatched=False)
   login={'status':'synthetic-profile-window-observed','fixtureDirectoryPreexisting':False,'fixtureDirectoryCreated':True,'syntheticIdentifierOnly':True,'realTaxpayerDataUsed':False,'newIdClicked':True,'inputVerified':True,'loginClicked':True,'loginHidden':True,'profileWindowObserved':True,'nextOwnedWindowObserved':True,'profileMainCaptionMatched':True,'profileSaveCloseMatched':True,'runtimeRoundTrip':False}
   records=[{'format':'htkk-framework-uia-boundary-v1','status':'exited','timedOut':False,'processStopped':True,'exitCode':0,'phase':'complete'},dict(guiAutomationPermitBoundary={'uniquePathVerified':True,'initiallyAbsent':True,'authorizationAttempted':True,'absentAfterCleanup':False},guiReferenceAutomationMode='gtgt-web-import-inspect',version='5.8.1',stage='blocked',blockedReason='GUI_REFERENCE_AUTOMATION_NOT_VERIFIED',guiReferenceAutomation=gui,referenceHostResult={'status':'original-starting'},sourceHashesVerified=True,originalSourcesUnmodified=True,officialDistributionFilesVerified=True,msiAuthenticodeValid=True,nativeHelperJobsStopped=True,hostOutboundBlocked=True,originalOutboundBlocked=True,taxDataUsed=False,runtimeRoundTrip=False,supplierProcessBoundary={k:True for k in ('cleanupVerified','supplierStopped','rootStopped','jobEmpty')},syntheticLogin=login),{'format':'htkk-web-native-output-publication-status-v1','status':'rejected','code':'FILES'}]
  if kind=='framework-phase':records[0]['phase']='cmdlets'
  if kind=='export':
   steps=[{'name':retry.PROBE,'conclusion':'failure'},{'name':retry.RETAIN,'conclusion':'failure'}]
   records=self.export_records()
  jobs={'total_count':2,'jobs':[{'name':'readiness','id':456,'conclusion':'failure','steps':steps},{'name':'report_failure','conclusion':'success'}]}
  status={'state':'failure','description':'failed input:'+INPUT,'target_url':'https://github.com/congminh1254/htkk_builder/actions/runs/123'};calls=[];state=set()
  def get(repo,path):return records if path.endswith('/logs')else jobs if '/jobs?'in path else run
  def send(*args):calls.append(args)
  def recover():return retry.recover(status,'htkk-native/zero',SOURCE,BUILDER,INPUT,get,lambda x:x,send,'actions-placeholder','status-placeholder',state)
  return locals()
 def export_records(self):
  # Shape of run42223236597 (01GTGT-noactivity-zero-M10-2026): original Kết xuất clicked once,
  # the selector never appeared before the 60s GUI budget; no file, message or comparison.
  gui=dict(retry.EXPORT_PENDING,editorKind='combo',visibleForms=1,sheetRows=75,sheetColumns=22,controlKinds={'form':1,'spread':1},webCaseId='01GTGT-noactivity-zero-M10-2026',waitSeconds=60,
   menuRowCount=314,menuClickCount=1,periodControlCount=137,periodControls={'btnDongY':{'kind':'button','visible':True}},periodYearMonthMatched=True,periodNoAnnexMatched=True,periodAnnex12Matched=False,
   gtgtCt21Ready=True,gtgtCt21CaseMatched=True,gtgtCt21BeforeExportMatched=True,gtgtCt21UncheckMatched=False,gtgtMonetaryZero=True,gtgtSheetRows=72,gtgtSheetColumns=24,gtgtSheetCount=11,
   gtgtEmptyMonetaryCount=0,gtgtCt42BeforeExportObserved=True,gtgtCt42LockedBeforeExport=False,gtgtCt42Locked=False,gtgtCaseMoneyCount=27,gtgtCaseNonzeroMask=0,
   webImportInputSha256='a'*64,webSourceSha='b'*40,webCaseEditCount=1,webSigningDateEdited=True,webSigningDateReady=True,webSigningDateLocked=False,webSigningDateCellKind=4,
   annex12NumericCount=0,annex12SheetObserved=False,annex12NumericSnapshots='',amendmentPriorFileSha256='',amendmentLifecycleVerified=False,annexSelectedCount=0,
   declarationMenuClicked=False,declarationCellMismatchMask=0,roundtripImportCommandInvoked=False,roundtripImportDialogMatched=False,roundtripImportSucceeded=False,
   roundtripReexportCommandInvoked=False,roundtripReexportSucceeded=False,roundtripXmlExactMatched=False,roundtripImportCheckedMoneyCount=0,roundtripReexportBytes=0,roundtripReexportSha256='')
  login={'status':'synthetic-profile-window-observed','fixtureDirectoryPreexisting':False,'fixtureDirectoryCreated':True,'syntheticIdentifierOnly':True,'realTaxpayerDataUsed':False,'newIdClicked':True,'inputVerified':True,'loginClicked':True,'loginHidden':True,'profileWindowObserved':True,'nextOwnedWindowObserved':True,'profileMainCaptionMatched':True,'profileSaveCloseMatched':True,'runtimeRoundTrip':False}
  report=dict(guiAutomationPermitBoundary={'uniquePathVerified':True,'initiallyAbsent':True,'authorizationAttempted':True,'absentAfterCleanup':False},guiReferenceAutomationMode='gtgt-web-import-inspect',version='5.8.1',stage='blocked',blockedReason='GUI_REFERENCE_AUTOMATION_NOT_VERIFIED',guiReferenceAutomation=gui,referenceHostResult={'status':'original-starting'},sourceHashesVerified=True,originalSourcesUnmodified=True,officialDistributionFilesVerified=True,msiAuthenticodeValid=True,nativeHelperJobsStopped=True,hostOutboundBlocked=True,originalOutboundBlocked=True,taxDataUsed=False,runtimeRoundTrip=False,supplierProcessBoundary={k:True for k in ('cleanupVerified','supplierStopped','rootStopped','jobEmpty')},syntheticLogin=login,nativeDialogCueCounts={},privateGtgtExportEvidence=None,privateWebNativeOutputEvidence=None)
  return [{'format':'htkk-framework-uia-boundary-v1','status':'exited','timedOut':False,'processStopped':True,'exitCode':0,'phase':'complete'},report,{'format':'htkk-web-native-output-publication-status-v1','status':'rejected','code':'FILES'}]
 def test_only_known_pre_tax_failures_retry_once_and_do_not_qualify(self):
  for kind in ['framework','framework-phase','startup','profile-close','export']:
   f=self.fixture(kind);self.assertTrue(f['recover']());self.assertEqual(len(f['calls']),2);self.assertIn('/rerun-failed-jobs',f['calls'][0][0]);self.assertEqual(f['calls'][1][2]['state'],'pending')
   self.assertTrue(f['recover']());self.assertEqual(len(f['calls']),2)
   f['run'].update(run_attempt=2,status='in_progress',conclusion=None);self.assertTrue(f['recover']());self.assertEqual(len(f['calls']),2)
   f['run'].update(status='completed',conclusion='failure');self.assertFalse(f['recover']());self.assertEqual(len(f['calls']),2)
 def declaration_startup(self):
  # Shape of release 216 r1372/r1376/r1377 (03TNDN, 05QTT, 01CNKD): HTKK stayed at
  # original-starting, no profile window, no permit; the declaration retain step succeeded
  # with exactly 'not-staged', so only the probe step failed.
  f=self.fixture('startup');r=f['records'][0];r['guiReferenceAutomationMode']=retry.DECLARATION_MODE
  f['steps'][:]=[{'name':retry.PROBE,'conclusion':'failure'},{'name':retry.DECLARATION_RETAIN,'conclusion':'success'}]
  f['records'].append(dict(retry.DECLARATION_NOT_STAGED))
  return f
 def test_declaration_startup_flake_retries_once_before_any_tax_step(self):
  f=self.declaration_startup();self.assertEqual(retry.classify(f['jobs'],f['records']),'synthetic-profile-startup-not-observed')
  self.assertTrue(f['recover']());self.assertEqual(len(f['calls']),2);self.assertIn('/rerun-failed-jobs',f['calls'][0][0])
  self.assertTrue(f['recover']());self.assertEqual(len(f['calls']),2)
  f['run'].update(run_attempt=2,status='completed',conclusion='failure');self.assertFalse(f['recover']());self.assertEqual(len(f['calls']),2)
  for kind in ['staged','published','retain-failed','retain-missing','gui','permit','profile','host','mode','reason','extra-step','money','cleanup']:
   f=self.declaration_startup();r=f['records'][0]
   if kind=='staged':f['records'][-1]={'format':retry.DECLARATION_NOT_STAGED['format'],'status':'rejected','code':'XML_PRIVACY'}
   if kind=='published':f['records'].append({'format':retry.DECLARATION_NOT_STAGED['format'],'status':'published'})
   if kind=='retain-failed':f['steps'][1]['conclusion']='failure'
   if kind=='retain-missing':del f['steps'][1]
   if kind=='gui':r['guiReferenceAutomation']={'stage':'declaration-export-not-matched'}
   if kind=='permit':r['guiAutomationPermitBoundary']['authorizationAttempted']=True
   if kind=='profile':r['syntheticLogin']['profileWindowObserved']=True
   if kind=='host':r['referenceHostResult']['status']='complete'
   if kind=='mode':r['guiReferenceAutomationMode']='gtgt-annex12-export-nonzero'
   if kind=='reason':r['blockedReason']='GUI_REFERENCE_AUTOMATION_NOT_VERIFIED'
   if kind=='extra-step':f['steps'].append({'name':'Tax comparison failed','conclusion':'failure'})
   if kind=='money':r['taxDataUsed']=True
   if kind=='cleanup':r['supplierProcessBoundary']['jobEmpty']=False
   self.assertIsNone(retry.classify(f['jobs'],f['records']),kind);self.assertFalse(f['recover'](),kind);self.assertEqual(f['calls'],[],kind)
 def test_candidate_failures_get_the_retry_but_never_gate_or_block_the_cohort(self):
  import test_caseflow_batch as original
  f=original.fixture();registry=original.batch.registry
  candidates=[c for c in f['publication']['cases'] if not registry.CASES[c['caseId']]['releaseGate']];self.assertTrue(candidates)
  for c in candidates:f['statuses'].append({'context':registry.CASES[c['caseId']]['statusContext'],'state':'failure','description':'failed input:'+c['artifactCommit'],'target_url':'https://github.com/'+original.batch.BUILDER+'/actions/runs/9'})
  for outcome in (True,False,'raise'):
   called=[]
   def candidate_retry(*args):
    called.append(args[1])
    if outcome=='raise':raise RuntimeError('fixed-test-failure')
    return outcome
   proof=original.batch.discover(f['publication'],original.BUILDER,f['statuses'],f['get'],retry=candidate_retry)
   self.assertEqual([c['caseId'] for c in proof['cases']],list(registry.GATE_CASES),outcome)
   self.assertEqual(sorted(called),sorted(registry.CASES[c['caseId']]['statusContext'] for c in candidates),outcome)
  # A stale candidate failure for another input is not retried; no retry callback, no retry.
  for st in f['statuses'][-len(candidates):]:st['description']='failed input:'+'d'*40
  called=[];original.batch.discover(f['publication'],original.BUILDER,f['statuses'],f['get'],retry=lambda *a:called.append(a));self.assertEqual(called,[])
  self.assertEqual(len(original.batch.discover(f['publication'],original.BUILDER,f['statuses'],f['get'])['cases']),len(registry.GATE_CASES))
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
  f['statuses'][0]['state']='pending';f['statuses'][-1].update(state='failure',description='failed input:'+f['publication']['cases'][len(original.batch.registry.GATE_CASES)-1]['artifactCommit']);retries=[]
  self.assertIsNone(original.batch.discover(f['publication'],original.BUILDER,f['statuses'],no_read,retry=lambda *args:retries.append(args)or True));self.assertEqual(len(retries),1);self.assertEqual(calls,[])

 def test_no_log_or_artifact_download_while_last_success_callback_still_has_poststeps_running(self):
  import test_caseflow_batch as original
  f=original.fixture();f['runs'][112]['status']='in_progress';calls=[]
  def metadata_only(repo,path):
   calls.append(path)
   if not path.startswith('actions/runs/')or '/jobs' in path:raise AssertionError('No heavy evidence reads before all runs complete')
   return f['get'](repo,path)
  self.assertIsNone(original.batch.discover(f['publication'],original.BUILDER,f['statuses'],metadata_only));self.assertEqual(len(calls),13)

 def test_profile_close_timeout_retries_only_before_any_tax_navigation_or_comparison(self):
  # Run42148832165 (case 01GTGT-sale5-half-M10-2026): synthetic profile saved and verified,
  # one original Close requested, owner still visible after the fixed 60s budget.
  f=self.fixture('profile-close');self.assertEqual(retry.classify(f['jobs'],f['records']),'synthetic-profile-close-not-observed')
  mutations={
   'menu':('mainMenuObserved',True),'d1':('d1MenuClicked',True),'period':('gtgtPeriodObserved',True),'clicks':('menuClickCount',1),
   'sheet':('gtgtSheetObserved',True),'web-input':('webInputVerified',True),'tax-match':('webTaxValuesMatched',True),
   'tax-mismatch':('gtgtCaseMismatchMask',1),'money':('gtgtCaseMoneyCount',3),'edits':('webCaseEditCount',1),
   'export':('exportCommandInvoked',True),'export-hash':('exportSha256','a'*64),'export-kind':('exportFilenameParentKind','combo'),
   'import':('roundtripImportSucceeded',True),'xml':('roundtripXmlExactMatched',True),'unknown-progress':('futureProgressFlag',True),
   'unknown-type':('futureProgressFlag',None),'period-controls':('periodControls',{'cbo':{}}),
   'stage-terminal':('stage','gtgt-profile-preconditions-not-matched'),'stage-later':('stage','waiting-main-menu'),
   'status-failed':('status','failed'),'status-exited':('status','root-exited'),'category':('failureCategory','dialog'),
   'closed':('profileClosed',True),'header-mask':('savedHeaderMismatchMask',1),'header':('savedHeaderChecksMatched',False),
   'header-count':('savedHeaderCheckedFieldCount',7),'dialog':('saveDialogKind','other'),'save':('originalSaveInvoked',False),
   'inputs':('performedInputCount',8),'pins':('sourcePinsVerified',False),'budget':('waitSeconds',30),'budget-type':('waitSeconds',60.0),
   'mode':('mode','gtgt-roundtrip-inspect'),'real-data':('realTaxpayerDataUsed',True),
  }
  for name,(key,value) in mutations.items():
   f=self.fixture('profile-close');f['records'][1]['guiReferenceAutomation'][key]=value
   self.assertFalse(f['recover'](),name);self.assertEqual(f['calls'],[],name)
  for name in ['gui-none','permit-unissued','permit-absent','permit-missing','reason','top-mode','tax','roundtrip','cleanup','helpers','source','login','retention-compare','retention-missing','retention-extra','other-step']:
   f=self.fixture('profile-close');r=f['records'][1]
   if name=='gui-none':r['guiReferenceAutomation']=None
   if name=='permit-unissued':r['guiAutomationPermitBoundary']['authorizationAttempted']=False
   if name=='permit-absent':r['guiAutomationPermitBoundary']['absentAfterCleanup']=True
   if name=='permit-missing':del r['guiAutomationPermitBoundary']
   if name=='reason':r['blockedReason']='HOST_NETWORK_OR_TOOL_FAILURE'
   if name=='top-mode':r['guiReferenceAutomationMode']='gtgt-roundtrip-inspect'
   if name=='tax':r['taxDataUsed']=True
   if name=='roundtrip':r['runtimeRoundTrip']=True
   if name=='cleanup':r['supplierProcessBoundary']['jobEmpty']=False
   if name=='helpers':r['nativeHelperJobsStopped']=False
   if name=='source':r['sourceHashesVerified']=False
   if name=='login':r['syntheticLogin']['profileWindowObserved']=False
   if name=='retention-compare':f['records'][2]['code']='COMPARE'
   if name=='retention-missing':del f['records'][2]
   if name=='retention-extra':f['records'].append(dict(f['records'][2]))
   if name=='other-step':f['steps'].append({'name':'Retain native-first harness sample and report its separate status privately','conclusion':'failure'})
   self.assertFalse(f['recover'](),name);self.assertEqual(f['calls'],[],name)
 def test_profile_close_classification_matches_harness_contract(self):
  root=pathlib.Path(__file__).parent;probe=(root/'probe-htkk-windows.ps1').read_text(encoding='utf-8')
  nav=(root/'HtkkGtgtReferenceNavigation.cs').read_text(encoding='utf-8');ui=(root/'HtkkNativeUiHarness.cs').read_text(encoding='utf-8')
  self.assertIn("if($GuiAutomation -in @('gtgt-roundtrip-inspect','gtgt-web-import-inspect','gtgt-amendment-open-inspect')){%d}"%retry.PROFILE_CLOSE_LIMIT,probe)
  self.assertRegex(probe,r"\$automationLimit=if\(")
  self.assertIn('case HtkkAutomationStage.WaitingProfileClose: return "waiting-profile-close";',(root/'HtkkNativeAutomationEnums.cs').read_text(encoding='utf-8'))
  # The close wait is reached only after the original save, header checks and one close request.
  self.assertIn('if(!headerMatched||headerChecks!=8||headerMismatchMask!=0||!successAcknowledged||!profileLifecycle.IsBound)',nav)
  self.assertLess(nav.index('if(!profileLifecycle.CloseRequested)'),nav.index('if(!profileClosed){SetStage(HtkkAutomationStage.WaitingProfileClose)'))
  self.assertLess(nav.index('if(!profileClosed){SetStage(HtkkAutomationStage.WaitingProfileClose)'),nav.index('List<Form> menus=new List<Form>()'))
  self.assertIn('internal void RequestClose(){if(requested||!Ready||!Clean)throw new InvalidOperationException();requested=true;close.PerformClick();}',ui)
  # Permit issuance precedes the GUI result; owned permit removal follows the absence check.
  self.assertLess(probe.index('$report.guiAutomationPermitBoundary.authorizationAttempted=$true'),probe.index('$automationClock=[Diagnostics.Stopwatch]::StartNew()'))
  self.assertIn("fail('FILES')",(root/'publish-htkk-web-native-output.py').read_text(encoding='utf-8'))
  self.assertNotIn('waiting-main-menu',retry.PROFILE_SAVED.values())

 def test_framework_process_timeout_in_any_valid_running_phase_retries_once(self):
  # Run42226715731: the clean Framework UIA child timed out in phase 'cmdlets', before HTKK starts.
  for phase in retry.FRAMEWORK_RUNNING_PHASES:
   f=self.fixture('framework-phase');f['records'][0]['phase']=phase
   self.assertEqual(retry.classify(f['jobs'],f['records']),'framework-uia-process-timeout',phase)
  self.assertEqual(retry.classify(self.fixture()['jobs'],self.fixture()['records']),'framework-uia-exit-timeout')
  for name,(key,value) in {'invalid':('phase','invalid'),'unavailable':('phase','unavailable'),'phase-type':('phase',None),'exited':('status','exited'),
   'not-timed-out':('timedOut',False),'running':('processStopped',False),'exit-code':('exitCode',0)}.items():
   f=self.fixture('framework-phase');f['records'][0][key]=value
   self.assertFalse(f['recover'](),name);self.assertEqual(f['calls'],[],name)
  f=self.fixture('framework-phase');del f['records'][0]['phase'];self.assertFalse(f['recover']());self.assertEqual(f['calls'],[])
  f=self.fixture('framework-phase');f['records'].append(dict(f['records'][0]));self.assertFalse(f['recover']());self.assertEqual(f['calls'],[])
  root=pathlib.Path(__file__).parent;ps=(root/'Test-HtkkFrameworkUiaAssemblyLoad.ps1').read_text(encoding='utf-8')
  self.assertIn("@('"+"','".join(retry.FRAMEWORK_RUNNING_PHASES+('complete',))+"')",ps)
  self.assertIn('No HTKK, taxpayer fixture',ps)

 def test_original_starting_startup_with_observed_owner_window_still_retries(self):
  # Runs42223226362/42226667771: HTKK stayed at original-starting; the owned post-login window
  # appeared but the profile main window was never identified, and no GUI permit was issued.
  f=self.fixture('startup');f['records'][0]['syntheticLogin'].update(newIdClicked=True,nextOwnedWindowObserved=True,profileRecognition='not-verified',profileMainCaptionMatched=False)
  self.assertEqual(retry.classify(f['jobs'],f['records']),'synthetic-profile-startup-not-observed')
  for name in ['host','permit','gui']:
   f=self.fixture('startup');r=f['records'][0]
   if name=='host':r['referenceHostResult']['status']='original-exited'
   if name=='permit':r['guiAutomationPermitBoundary']['authorizationAttempted']=True
   if name=='gui':r['guiReferenceAutomation']=dict(retry.EXPORT_PENDING)
   self.assertFalse(f['recover'](),name);self.assertEqual(f['calls'],[],name)

 def test_export_selector_not_observed_retries_only_without_any_export_message_or_comparison(self):
  f=self.fixture('export');self.assertEqual(retry.classify(f['jobs'],f['records']),'gtgt-export-selector-not-observed')
  mutations={
   'tax-mismatch':('gtgtCaseMismatchMask',4),'money-unmatched':('gtgtCaseMoneyMatched',False),'web-input':('webInputVerified',False),
   'rejected':('exportRejectedMessageId',16),'import-rejected':('importRejectedMessageId',478),'rejected-stage':('stage','gtgt-export-original-message-rejected'),
   'success-stage':('stage','gtgt-export-success-file-checking'),'file':('exportFileExists',True),'bytes':('exportBytes',10),'sha':('exportSha256','a'*64),
   'scoped':('exportScopedFileCount',1),'scoped-xml':('exportScopedXmlCount',1),'button':('exportButtonInvoked',True),
   'dialog':('exportDialogMatched',True),'submitted':('exportDialogSubmitted',True),'ack':('exportSuccessAcknowledged',True),'xml-root':('exportXmlRootMatched',True),
   'filename':('exportFilenameKeyboardCommitted',True),'parent':('exportFilenameParentKind','combo'),'path':('exportOriginalPathMatched',True),
   'not-invoked':('exportCommandInvoked',False),'destination':('exportDestinationFresh',False),'schema':('exportSchemaPinnedVerified',False),
   'roundtrip-import':('roundtripImportSucceeded',True),'roundtrip-command':('roundtripImportCommandInvoked',True),'reexport':('roundtripReexportSucceeded',True),
   'xml':('roundtripXmlExactMatched',True),'reexport-sha':('roundtripReexportSha256','a'*64),'web-tax':('webTaxValuesMatched',True),'web-leaf':('webTaxLeafCount',3),
   'web-identity':('webServiceIdentityMatched',True),'after-import':('gtgtCt42AfterImportObserved',True),'ct21-after':('gtgtCt21AfterImportMatched',True),
   'future-after-import':('gtgtCt99AfterImportMatched',True),'future-mismatch':('webFutureMismatchMask',2),'future-rejected':('periodRejectedMessageId',16),'annex':('annex12SheetObserved',True),'annex-count':('annex12NumericCount',1),
   'declaration':('declarationMenuClicked',True),'declaration-mask':('declarationCellMismatchMask',1),'amendment':('amendmentLifecycleVerified',True),
   'unknown':('futureProgressFlag',True),'unknown-type':('futureProgressFlag',None),'pre-export-type':('gtgtCaseMoneyCount',None),
   'status':('status','failed'),'category':('failureCategory','dialog'),'budget':('waitSeconds',30),'budget-type':('waitSeconds',60.0),'case-type':('webCaseId',None),
   'mode':('mode','gtgt-roundtrip-inspect'),'real-data':('realTaxpayerDataUsed',True),'roundtrip-flag':('runtimeRoundTrip',True),'profile-open':('profileClosed',False),
   'menu':('mainMenuObserved',False),'sheet':('gtgtSheetObserved',False),'identity':('gtgtIdentityMatched',False),
  }
  for name,(key,value) in mutations.items():
   f=self.fixture('export');f['records'][1]['guiReferenceAutomation'][key]=value
   self.assertFalse(f['recover'](),name);self.assertEqual(f['calls'],[],name)
  # A matched selector (no file yet) is no longer this exact shape; the general pre-export
  # timeout category subsumes it, so it retries under that name instead.
  f=self.fixture('export');f['records'][1]['guiReferenceAutomation']['exportSelectorMatched']=True
  self.assertEqual(retry.classify(f['jobs'],f['records']),'gui-pre-export-timeout')
  for name in ['dialog-cue','dialog-cue-missing','export-evidence','output-evidence','evidence-missing','published','retention-missing','tax','permit','login','reason','attempt2','other-step']:
   f=self.fixture('export');r=f['records'][1]
   if name=='dialog-cue':r['nativeDialogCueCounts']={'message':1}
   if name=='dialog-cue-missing':del r['nativeDialogCueCounts']
   if name=='export-evidence':r['privateGtgtExportEvidence']={'status':'retained'}
   if name=='output-evidence':r['privateWebNativeOutputEvidence']={'status':'retained'}
   if name=='evidence-missing':del r['privateGtgtExportEvidence']
   if name=='published':f['records'][2].update(status='published',code='OK')
   if name=='retention-missing':del f['records'][2]
   if name=='tax':r['taxDataUsed']=True
   if name=='permit':r['guiAutomationPermitBoundary']['absentAfterCleanup']=True
   if name=='login':r['syntheticLogin']['profileSaveCloseMatched']=False
   if name=='reason':r['blockedReason']='SYNTHETIC_LOGIN_NOT_VERIFIED'
   if name=='attempt2':f['run']['run_attempt']=2
   if name=='other-step':f['steps'].append({'name':'Retain verified synthetic GTGT export privately','conclusion':'failure'})
   self.assertFalse(f['recover'](),name);self.assertEqual(f['calls'],[],name)
 def test_export_selector_classification_matches_harness_contract(self):
  root=pathlib.Path(__file__).parent;export=(root/'HtkkGtgtExportInspection.cs').read_text(encoding='utf-8')
  self.assertIn('case HtkkAutomationStage.GtgtExportCommandInvoking: return "gtgt-export-command-invoking";',(root/'HtkkNativeAutomationEnums.cs').read_text(encoding='utf-8'))
  # The stage is recorded once immediately before the single original click; any frmMessage
  # (rejection or success) moves the stage on before the selector is ever examined.
  invoke=export.index('SetStage(HtkkAutomationStage.GtgtExportCommandInvoking);exportCommandInvoked=true;Record();')
  self.assertLess(invoke,export.index('command.PerformClick();',invoke))
  self.assertEqual(export.count('SetStage(HtkkAutomationStage.GtgtExportCommandInvoking)'),1)
  rejected=export.index('exportRejectedMessageId=OriginalMessageCatalogueId(labels[0].Text);SetStage(HtkkAutomationStage.GtgtExportOriginalMessageRejected)')
  self.assertLess(export.index('SetStage(HtkkAutomationStage.GtgtExportSuccessFileChecking)'),export.index('if(!exportButtonInvoked){List<Form> selectors'))
  self.assertLess(rejected,export.index('if(!exportButtonInvoked){List<Form> selectors'))
  self.assertNotIn('waiting-main-menu',retry.EXPORT_PENDING.values())
 # Exact readiness step structure of run42265022235 (01GTGT-sale10-M10-2026, release 217):
 # Test-HtkkSupplierJobBoundary.ps1 failed ("Own supplier root fixture failed") before the
 # web XML fetch, supplier download or HTKK probe; every later step was skipped.
 SELFTEST_RUN_STEPS=[('Set up job','success'),('Run actions/checkout@11d5960a326750d5838078e36cf38b85af677262','success'),
  ('Check generated native automation contract is synchronized','success'),('Check trusted case registry is synchronized','success'),
  ('Test complete builder contracts without network','success'),('Check generated typed flags counters defaults and mode ranges','success'),
  ('Check safe reference-result boundary','success'),('Check classified pinned download and attempt limits','success'),
  ('Check bounded native process and clean environment','success'),('Check bounded compiler diagnostics and complete cleanup','success'),
  ('Check bounded oracle Job cleanup and environment','success'),('Check supplier Job cleanup and retained identity boundary','failure'),
  ('Check UIA cleanup and bounded result boundary','skipped'),('Check clean Framework UIA assembly readiness','skipped'),
  ('Check actual C# web-tax comparison boundaries','skipped'),('Test private GUI XML evidence boundaries without network','skipped'),
  ('Test private synthetic web input boundaries without network','skipped'),('Test fixed original annex export boundaries without network','skipped'),
  ('Test fixed annex web cases and nonzero export boundaries without network','skipped'),('Test declaration-family native cases and boundaries without network','skipped'),
  ('Fetch fixed synthetic web XML privately','skipped'),('Queue separate native harness sample status before supplier launch','skipped'),
  ('Kiểm tra nguồn và điều kiện Windows','skipped'),('Publish supplier startup window privately','skipped'),
  ('Retain synthetic common-header reference privately','skipped'),('Retain verified synthetic GTGT export privately','skipped'),
  ('Retain fixed original 01-2 GTGT export privately','skipped'),('Retain fixed original nonzero 01-2 GTGT exports privately','skipped'),
  ('Retain verified raw native web reexport privately','skipped'),('Retain raw native declaration export privately','skipped'),
  ('Retain native-first harness sample and report its separate status privately','skipped'),('Report unsuccessful native harness sample after verified cleanup','skipped'),
  ('Report fixed native-case status privately','skipped'),('Post Run actions/checkout@11d5960a326750d5838078e36cf38b85af677262','success'),('Complete job','success')]
 # Every JSON object collector.records() extracts from that job log (builder unittest output only).
 SELFTEST_RUN_RECORDS=[{'result':'metadata-only','failureCode':None,'trustRequested':False,'ready':False}]*2+[{'result':'unchanged','trustStatus':'not-run','ready':False,'credentialsSafe':True}]+[
  {'result':'metadata-only','failureCode':None,'trustRequested':False,'ready':False},{'result':'unchanged','trustStatus':'not-run','ready':False,'credentialsSafe':True}]*5+[
  {'result':'blocked','failureCode':'TLS','trustRequested':False,'ready':False},{'result':'blocked','failureCode':'HTTP_DENIED','trustRequested':False,'ready':False},
  {'result':'blocked','failureCode':'HTTP_DENIED','trustRequested':False,'ready':False},{'result':'metadata-only','failureCode':None,'trustRequested':False,'ready':False},
  {'result':'unchanged','trustStatus':'not-run','ready':False,'credentialsSafe':True},{'result':'blocked','failureCode':'UNREVIEWED_VERSION','trustRequested':False,'ready':False},
  {'result':'review-required','trustStatus':'not-run','ready':False,'credentialsSafe':True}]
 def selftest_fixture(self):
  f=self.fixture()
  numbers=list(range(1,34))+[66,67]
  f['steps'][:]=[{'name':n,'status':'completed','conclusion':c,'number':k}for (n,c),k in zip(self.SELFTEST_RUN_STEPS,numbers)]
  f['records'][:]=copy.deepcopy(self.SELFTEST_RUN_RECORDS)
  f['jobs']['jobs'][0].update(id=128054583707,run_attempt=1,status='completed')
  return f
 def step(self,f,name):return next(s for s in f['steps']if s['name']==name)
 def test_selftest_fixture_flake_retries_once_before_any_htkk_or_web_step(self):
  f=self.selftest_fixture()
  self.assertEqual(retry.classify(f['jobs'],f['records']),'windows-selftest-fixture-failed')
  self.assertTrue(f['recover']());self.assertEqual(len(f['calls']),2);self.assertIn('/rerun-failed-jobs',f['calls'][0][0]);self.assertEqual(f['calls'][1][2]['state'],'pending')
  self.assertTrue(f['recover']());self.assertEqual(len(f['calls']),2)
  f['run'].update(run_attempt=2,status='completed',conclusion='failure');self.assertFalse(f['recover']());self.assertEqual(len(f['calls']),2)
  for name in retry.SELFTEST_STEPS:
   # Same structure with any listed self-test as the single failure (earlier ones succeeded).
   g=self.selftest_fixture();i=[s['name']for s in g['steps']].index(name)
   for k,s in enumerate(g['steps'][:-2]):s['conclusion']='success'if k<i else 'failure'if k==i else 'skipped'
   self.assertEqual(retry.classify(g['jobs'],g['records']),'windows-selftest-fixture-failed',name)
  g=self.selftest_fixture();g['records'][:]=[];self.assertEqual(retry.classify(g['jobs'],g['records']),'windows-selftest-fixture-failed')
 def test_selftest_retry_never_applies_after_htkk_web_or_retain_progress(self):
  supplier=self.fixture('startup')['records'][0]
  cases={
   'probe-ran':lambda f:self.step(f,retry.PROBE).update(conclusion='success'),
   'probe-failed':lambda f:self.step(f,retry.PROBE).update(conclusion='failure'),
   'retain-ran':lambda f:self.step(f,retry.RETAIN).update(conclusion='success'),
   'declaration-retain-ran':lambda f:self.step(f,retry.DECLARATION_RETAIN).update(conclusion='success'),
   'fetch-ran':lambda f:self.step(f,'Fetch fixed synthetic web XML privately').update(conclusion='success'),
   'report-ran':lambda f:self.step(f,'Report fixed native-case status privately').update(conclusion='success'),
   'later-selftest-ran':lambda f:self.step(f,'Check UIA cleanup and bounded result boundary').update(conclusion='success'),
   'probe-missing':lambda f:f['steps'].remove(self.step(f,retry.PROBE)),
   'retain-missing':lambda f:f['steps'].remove(self.step(f,retry.RETAIN)),
   'earlier-skipped':lambda f:self.step(f,'Check bounded oracle Job cleanup and environment').update(conclusion='skipped'),
   'post-failed':lambda f:self.step(f,'Complete job').update(conclusion='failure'),
   'cancelled':lambda f:self.step(f,'Check supplier Job cleanup and retained identity boundary').update(conclusion='cancelled'),
   'multiple-failed':lambda f:self.step(f,'Check UIA cleanup and bounded result boundary').update(conclusion='failure'),
   'multiple-selftests-failed':lambda f:self.step(f,'Check bounded oracle Job cleanup and environment').update(conclusion='failure'),
   'contract-step-failed':lambda f:self.step(f,'Test complete builder contracts without network').update(conclusion='failure'),
   'different-failed-step':lambda f:(self.step(f,'Check supplier Job cleanup and retained identity boundary').update(conclusion='success'),self.step(f,'Check actual C# web-tax comparison boundaries').update(conclusion='failure'),self.step(f,'Check UIA cleanup and bounded result boundary').update(conclusion='success'),self.step(f,retry.FRAMEWORK).update(conclusion='success')),
   'framework-failed':lambda f:(self.step(f,'Check supplier Job cleanup and retained identity boundary').update(conclusion='success'),self.step(f,'Check UIA cleanup and bounded result boundary').update(conclusion='success'),self.step(f,retry.FRAMEWORK).update(conclusion='failure')),
   'job-attempt-2':lambda f:f['jobs']['jobs'][0].update(run_attempt=2),
   'job-attempt-missing':lambda f:f['jobs']['jobs'][0].pop('run_attempt'),
   'step-order':lambda f:f['steps'].reverse(),
   'number-missing':lambda f:self.step(f,retry.PROBE).pop('number'),
   'supplier-report':lambda f:f['records'].append(copy.deepcopy(supplier)),
   'framework-record':lambda f:f['records'].append({'format':'htkk-framework-uia-boundary-v1','status':'process-timeout','timedOut':True,'processStopped':True,'exitCode':None,'phase':'complete'}),
   'retained-output':lambda f:f['records'].append({'format':'htkk-web-native-output-publication-status-v1','status':'rejected','code':'FILES'}),
   'declaration-output':lambda f:f['records'].append(dict(retry.DECLARATION_NOT_STAGED)),
   'web-progress':lambda f:f['records'].append({'webInputVerified':True,'webCaseId':'01GTGT-sale10-M10-2026'}),
   'tax-progress':lambda f:f['records'].append({'result':'metadata-only','ready':False,'taxDataUsed':True}),
   'ready-record':lambda f:f['records'].append({'result':'staged','ready':True}),
   'nested-record':lambda f:f['records'].append({'result':'metadata-only','ready':False,'failureCode':{'stage':'gtgt'}}),
   'callback-failed':lambda f:f['jobs']['jobs'][1].update(conclusion='failure'),
  }
  for kind,mutate in cases.items():
   f=self.selftest_fixture();mutate(f)
   self.assertIsNone(retry.classify(f['jobs'],f['records']),kind);self.assertFalse(f['recover'](),kind);self.assertEqual(f['calls'],[],kind)
  f=self.selftest_fixture();f['run']['run_attempt']=2
  self.assertFalse(f['recover']());self.assertEqual(f['calls'],[])
 def test_selftest_steps_match_workflow_and_precede_any_fetch_or_htkk_probe(self):
  wf=(pathlib.Path(__file__).parent.parent/'.github/workflows/probe-htkk-windows.yml').read_text(encoding='utf-8')
  scripts=('BoundedNativeProcess','BoundedCompiler','BoundedJobProcess','SupplierJobBoundary','UiaProcessBoundary')
  for name,script in zip(retry.SELFTEST_STEPS,scripts):
   block='      - name: '+name+'\n        shell: pwsh\n        run: ./scripts/Test-Htkk'+script+'.ps1\n'
   self.assertEqual(wf.count(block),1,name);self.assertEqual(wf.count('- name: '+name+'\n'),1,name)
   self.assertLess(wf.index(block),wf.index('- name: Fetch fixed synthetic web XML privately'))
   self.assertLess(wf.index(block),wf.index('- name: '+retry.PROBE))
  order=[wf.index('- name: '+n+'\n')for n in retry.SELFTEST_STEPS];self.assertEqual(order,sorted(order))
  self.assertNotIn(retry.FRAMEWORK,retry.SELFTEST_STEPS)
  for name,_ in self.SELFTEST_RUN_STEPS[2:-2]:self.assertIn('- name: '+name+'\n',wf)

# Exact readiness steps of runs 42268915757 / 42268930430 (release 218, attempt 1): only the probe
# and the gtgt retain step failed; every other retain/publish step was skipped.
REAL_PROBE_STEPS=[(n,'success')for n,_ in NativePreflightRetry.SELFTEST_RUN_STEPS[:21]]+[('Queue separate native harness sample status before supplier launch','skipped'),
 (retry.PROBE,'failure'),('Publish supplier startup window privately','skipped'),('Retain synthetic common-header reference privately','skipped'),
 ('Retain verified synthetic GTGT export privately','skipped'),('Retain fixed original 01-2 GTGT export privately','skipped'),
 ('Retain fixed original nonzero 01-2 GTGT exports privately','skipped'),(retry.RETAIN,'failure'),(retry.DECLARATION_RETAIN,'skipped'),
 ('Retain native-first harness sample and report its separate status privately','skipped'),('Report unsuccessful native harness sample after verified cleanup','skipped'),
 ('Report fixed native-case status privately','success'),('Post Run actions/checkout@11d5960a326750d5838078e36cf38b85af677262','success'),('Complete job','success')]
FILES={'format':'htkk-web-native-output-publication-status-v1','status':'rejected','code':'FILES'}
class GuiPreExportTimeout(unittest.TestCase):
 def fixture(self,kind='gui'):
  base=NativePreflightRetry();f=base.fixture('export')
  f['steps'][:]=[{'number':i+1,'name':n,'conclusion':c,'status':'completed'}for i,(n,c)in enumerate(REAL_PROBE_STEPS)]
  r=f['records'][1];gui=r['guiReferenceAutomation']
  # Run 42268915757 (01GTGT-noactivity-zero-M10-2026): web input verified, money matched,
  # original Kết xuất clicked, selector matched and its button pressed; the file dialog never
  # appeared within the 60s budget. No file, hash, message, import, re-export or comparison.
  gui.update(stage='gtgt-export-file-dialog-waiting',exportSelectorMatched=True,exportButtonInvoked=True,declarationPeriodRejectedMessageId=0,
   annex12WebHeadAuthorityComboMask=0,annex12WebHeadAuthorityFailureMask=0,gtgtAutoCalculationReady=True,gtgtBusinessInstanceMatched=True,
   gtgtCt21ConfirmationMatched=True,gtgtCt21LocksMatched=True,periodFirstDeclarationMatched=True,periodActivityMatched=True,periodGeographyMatched=True,
   declarationXmlMismatchMask=0,declarationTreeMismatchMask=0,controlKinds={'form':1,'button':18,'combo':3,'text':2,'spread':1,'other':18})
  del gui['annex12NumericSnapshots'] # Absent keys are fine; only present ones are judged.
  if kind=='oracle':
   # Run 42268930430 (01GTGT-noactivity-uncheck-sale10-M10-2026): the tax-id oracle compiler
   # timed out after HTKK started but before login; no permit, profile, web input or GUI.
   r.update(blockedReason='TAX_ID_ORACLE_NOT_VERIFIED',syntheticLogin=None,guiReferenceAutomation=None,
    guiAutomationPermitBoundary={'uniquePathVerified':True,'initiallyAbsent':True,'authorizationAttempted':False,'absentAfterCleanup':True},
    taxIdOracle={'status':'compile-timeout','cases':0,'matched':0,'mismatches':0,'runtime':'unknown','compilerExitCode':None,'compilerErrorCodes':[],
     'compilerJobCleanupVerified':True,'oracleExitCode':None,'oracleJobCleanupVerified':True,'dllHashVerified':True,'originalMethodInvoked':False,'fullRoundTrip':False,'userDataUsed':False},
    profileAliasOracle={'status':'matched','cases':12,'matched':12,'mismatches':0,'compilerExitCode':0,'compilerErrorCodes':[],'compilerJobCleanupVerified':True,
     'oracleExitCode':0,'oracleJobCleanupVerified':True,'originalMethodInvoked':True,'userDataUsed':False},
    commonHeaderOracle={'status':'matched','cases':43,'matched':43,'failedCaseIndices':[],'compilerExitCode':0,'compilerErrorCodes':[],'compilerJobCleanupVerified':True,
     'oracleExitCode':0,'oracleJobCleanupVerified':True,'userDataUsed':False})
  if kind in ('declaration','declaration-oracle'):
   f['steps'][28]['conclusion']='skipped';f['steps'][29]['conclusion']='success';r['guiReferenceAutomationMode']=retry.DECLARATION_MODE
   f['records'][2]=dict(retry.DECLARATION_NOT_STAGED)
   gui.clear();gui.update(retry.GUI_TIMEOUT_REQUIRED,mode=retry.DECLARATION_MODE,stage='declaration-web-input-checking',waitSeconds=120,webCaseId='03TNDN-profit20-Y2025',
    webImportInputSha256='a'*64,webSourceSha='b'*40,declarationMenuClicked=True,declarationPeriodObserved=True,declarationPeriodMatched=True,declarationAnnexMatched=True,
    declarationSheetObserved=True,declarationIdentityMatched=True,declarationSourcePinsMatched=True,declarationSheetCount=2,declarationPeriodRejectedMessageId=0,
    declarationCellMismatchMask=0,declarationXmlMismatchMask=0,declarationTreeMismatchMask=0,roundtripImportCommandInvoked=False,roundtripImportSucceeded=False,
    exportCommandInvoked=False,exportSelectorMatched=False,exportDialogSubmitted=False,declarationTreeMatched=False,periodConfirmInvoked=True)
   if kind=='declaration-oracle':
    o=GuiPreExportTimeout().fixture('oracle')['records'][1]
    r.update({k:copy.deepcopy(o[k])for k in ('blockedReason','syntheticLogin','guiReferenceAutomation','guiAutomationPermitBoundary','taxIdOracle','profileAliasOracle','commonHeaderOracle')})
  return f
 def assertRetried(self,f,name='',reasons=('gui-pre-export-timeout',)):
  self.assertIn(retry.classify(f['jobs'],f['records']),reasons,name)
  self.assertTrue(f['recover'](),name);self.assertEqual(len(f['calls']),2,name);self.assertIn('/rerun-failed-jobs',f['calls'][0][0])
  self.assertEqual(f['calls'][1][2]['state'],'pending');self.assertTrue(f['recover']());self.assertEqual(len(f['calls']),2)
  f['run'].update(run_attempt=2,status='completed',conclusion='failure');self.assertFalse(f['recover'](),name);self.assertEqual(len(f['calls']),2,name)
 def assertRejected(self,f,name):
  if f['run']['run_attempt']==1:self.assertNotEqual(retry.classify(f['jobs'],f['records']),'gui-pre-export-timeout',name)
  self.assertFalse(f['recover'](),name);self.assertEqual(f['calls'],[],name)
 def test_real_release_218_shapes_retry_once_on_attempt_one_only(self):
  for kind in ('gui','oracle','declaration','declaration-oracle'):self.assertRetried(self.fixture(kind),kind)
 def test_other_gui_timing_shapes_before_any_file_are_subsumed(self):
  # Run 42223236597's exact shape (selector never appeared) also satisfies the general invariants.
  self.assertTrue(retry._gui_pre_export_timeout(NativePreflightRetry().export_records()[1]['guiReferenceAutomation'],'gtgt-web-import-inspect'))
  variants={'command-only':dict(stage='gtgt-export-command-invoking',exportSelectorMatched=False,exportButtonInvoked=False),
   'dialog-matched':dict(exportDialogMatched=True),'before-export':dict(stage='gtgt-case-editing',exportCommandInvoked=False,exportSelectorMatched=False,exportButtonInvoked=False),
   'focus-wait':dict(stage='gtgt-export-filename-focus-waiting',exportDialogMatched=True),'longer-budget':dict(waitSeconds=120)}
  for name,update in variants.items():
   # The exact older selector shape keeps its own specific name; both retry identically.
   f=self.fixture();f['records'][1]['guiReferenceAutomation'].update(update);self.assertRetried(f,name,('gui-pre-export-timeout','gtgt-export-selector-not-observed')if name=='command-only'else('gui-pre-export-timeout',))
  f=self.fixture('oracle');f['records'][1]['taxIdOracle'].update(status='oracle-timeout',compilerExitCode=0);self.assertRetried(f,'oracle-run-timeout')
  f=self.fixture('oracle');r=f['records'][1];r['taxIdOracle']['status']='matched';r['commonHeaderOracle'].update(status='compile-timeout',cases=0,matched=0,compilerExitCode=None,oracleExitCode=None)
  r['blockedReason']='COMMON_HEADER_ORACLE_NOT_VERIFIED';self.assertRetried(f,'common-header-timeout')
 def test_any_export_output_message_mismatch_or_comparison_is_never_retried(self):
  mutations={
   'file':('exportFileExists',True),'bytes':('exportBytes',10),'sha':('exportSha256','a'*64),'scoped':('exportScopedFileCount',1),'scoped-xml':('exportScopedXmlCount',1),
   'export-rejected':('exportRejectedMessageId',16),'import-rejected':('importRejectedMessageId',478),'period-rejected':('declarationPeriodRejectedMessageId',12),
   'money-mismatch':('gtgtCaseMismatchMask',4),'money-unmatched':('gtgtCaseMoneyMatched',False),'money-not-run':('gtgtCaseMoneyCount',0),
   'header-mismatch':('savedHeaderMismatchMask',1),'cell-mismatch':('declarationCellMismatchMask',1),'xml-mismatch':('declarationXmlMismatchMask',2),
   'tree-mismatch':('declarationTreeMismatchMask',1),'annex-authority':('annex12WebHeadAuthorityFailureMask',1),
   'roundtrip-command':('roundtripImportCommandInvoked',True),'roundtrip-import':('roundtripImportSucceeded',True),'reexport':('roundtripReexportSucceeded',True),
   'reexport-bytes':('roundtripReexportBytes',100),'xml-exact':('roundtripXmlExactMatched',True),'web-tax':('webTaxValuesMatched',True),'web-leaf':('webTaxLeafCount',3),
   'web-identity':('webServiceIdentityMatched',True),'web-date':('webCreationDateMatchedNativeBaseline',True),'tree':('declarationTreeMatched',True),
   'annex-web':('annex12WebImportSheetMatched',True),'after-import':('gtgtCt42AfterImportObserved',True),'amendment-file':('amendmentPriorFileBytes',10),
   'submitted':('exportDialogSubmitted',True),'filename':('exportFilenameKeyboardCommitted',True),'ack':('exportSuccessAcknowledged',True),
   'xml-root':('exportXmlRootMatched',True),'path':('exportOriginalPathMatched',True),'path-kind':('exportOriginalPathKind','expected-path'),
   'status-failed':('status','failed'),'status-exited':('status','root-exited'),'status-matched':('status','matched'),'status-none':('status','no-valid-result'),
   'category':('failureCategory','io'),'stage-rejected':('stage','gtgt-export-original-message-rejected'),'stage-success':('stage','gtgt-export-success-file-checking'),
   'stage-writing':('stage','gtgt-export-original-writing'),'stage-import':('stage','gtgt-import-file-dialog-waiting'),'stage-reexport':('stage','gtgt-reexport-command-invoking'),
   'stage-saved':('stage','gtgt-original-declaration-save-invoking'),'stage-unknown':('stage','gtgt-export-future-waiting'),'stage-profile':('stage','waiting-profile-close'),'stage-period':('stage','gtgt-period-configuring'),'stage-menu':('stage','gtgt-menu-click-D1'),'stage-declaration':('stage','declaration-sheet-waiting'),
   'order-button':('exportSelectorMatched',False),'no-command':('exportCommandInvoked',False),'destination':('exportDestinationFresh',False),'schema':('exportSchemaPinnedVerified',False),
   'web-input':('webInputVerified',False),'identity':('gtgtIdentityMatched',False),'menu':('mainMenuObserved',False),'profile':('profileClosed',False),
   'annex-on-no-annex':('annex12SheetObserved',True),'declaration-on-gtgt':('declarationMenuClicked',True),'lifecycle':('annex12LifecycleMatched',True),
   'unknown':('futureProgressFlag',True),'type':('gtgtCaseMoneyCount',None),'range':('menuClickCount',9),'hex':('webImportInputSha256','A'*64),'enum':('saveDialogKind','other'),
   'budget':('waitSeconds',30),'budget-type':('waitSeconds',60.0),'mode':('mode','gtgt-roundtrip-inspect'),'real-data':('realTaxpayerDataUsed',True),
   'roundtrip-flag':('runtimeRoundTrip',True),'pins':('sourcePinsVerified',False),'cue':('nativeDialogCueCount',1),
  }
  for name,(key,value) in mutations.items():
   f=self.fixture();f['records'][1]['guiReferenceAutomation'][key]=value;self.assertRejected(f,name)
  f=self.fixture();del f['records'][1]['guiReferenceAutomation']['webInputVerified'];self.assertRejected(f,'web-input-missing')
  f=self.fixture('declaration');f['records'][1]['guiReferenceAutomation'].update(stage='declaration-import-ready-waiting');self.assertRejected(f,'declaration-import')
  f=self.fixture('declaration');f['records'][1]['guiReferenceAutomation'].update(roundtripImportCommandInvoked=True);self.assertRejected(f,'declaration-roundtrip')
  f=self.fixture('declaration');f['records'][1]['guiReferenceAutomation'].update(declarationCellCheckCount=3);self.assertRejected(f,'declaration-cells')
 def test_retained_evidence_dialog_cues_report_or_attempt_mismatches_are_never_retried(self):
  for kind in ('gui','oracle','declaration','declaration-oracle'):
   for name in ['cue','export-evidence','output-evidence','evidence-missing','published','retention-missing','retention-extra','retention-other-family','retain-success','other-retain',
     'other-retain-failed','cancelled','tax','cleanup','host','attempt2','callback','reason','permit','login-gui']:
    f=self.fixture(kind);r=f['records'][1];decl=kind.startswith('declaration')
    if name=='cue':r['nativeDialogCueCounts']={'message':1}
    if name=='export-evidence':r['privateGtgtExportEvidence']={'status':'retained'}
    if name=='output-evidence':r['privateWebNativeOutputEvidence']={'status':'retained'}
    if name=='evidence-missing':del r['privateWebNativeOutputEvidence']
    if name=='published':f['records'][2]=dict(f['records'][2],status='published')
    if name=='retention-missing':del f['records'][2]
    if name=='retention-extra':f['records'].append(dict(f['records'][2]))
    if name=='retention-other-family':f['records'].append(dict(FILES)if decl else dict(retry.DECLARATION_NOT_STAGED))
    if name=='retain-success':f['steps'][28]['conclusion']='failure'if decl else 'success'
    if name=='other-retain':f['steps'][25]['conclusion']='success'
    if name=='other-retain-failed':f['steps'][25]['conclusion']='failure'
    if name=='cancelled':f['steps'][31]['conclusion']='cancelled'
    if name=='tax':r['taxDataUsed']=True
    if name=='cleanup':r['supplierProcessBoundary']['jobEmpty']=False
    if name=='host':r['hostOutboundBlocked']=False
    if name=='attempt2':f['run']['run_attempt']=2
    if name=='callback':f['jobs']['jobs'][1]['conclusion']='failure'
    if name=='reason':r['blockedReason']='HOST_NETWORK_OR_TOOL_FAILURE'
    if name=='permit':r['guiAutomationPermitBoundary']['authorizationAttempted']=not r['guiAutomationPermitBoundary']['authorizationAttempted']
    if name=='login-gui':
     if r['syntheticLogin']is None:r['syntheticLogin']={'status':'synthetic-profile-window-observed'}
     else:r['syntheticLogin']['profileSaveCloseMatched']=False
    self.assertRejected(f,kind+':'+name)
 def test_oracle_mismatch_or_completed_case_is_never_retried(self):
  for name in ['mismatch-status','runtime-blocked','tool-failure','compile-failed','cases','matched','mismatches','invoked','compiler-errors','exit-code','compile-cleanup',
    'oracle-cleanup','user-data','other-mismatch','other-mismatch-count','other-failed-case','reason-order','gui-present','login-present','missing-oracle']:
   f=self.fixture('oracle');r=f['records'][1];o=r['taxIdOracle']
   if name=='mismatch-status':o['status']='mismatch'
   if name=='runtime-blocked':o['status']='oracle-runtime-blocked'
   if name=='tool-failure':o['status']='host-or-tool-failure'
   if name=='compile-failed':o['status']='compile-failed'
   if name=='cases':o['cases']=30
   if name=='matched':o['matched']=1
   if name=='mismatches':o['mismatches']=1
   if name=='invoked':o['originalMethodInvoked']=True
   if name=='compiler-errors':o['compilerErrorCodes']=['CS0103']
   if name=='exit-code':o['oracleExitCode']=2
   if name=='compile-cleanup':o['compilerJobCleanupVerified']=False
   if name=='oracle-cleanup':o['oracleJobCleanupVerified']=False
   if name=='user-data':o['userDataUsed']=True
   if name=='other-mismatch':r['profileAliasOracle']['status']='mismatch'
   if name=='other-mismatch-count':r['profileAliasOracle']['mismatches']=1
   if name=='other-failed-case':r['commonHeaderOracle']['failedCaseIndices']=[3]
   if name=='reason-order':r['blockedReason']='PROFILE_ALIAS_ORACLE_NOT_VERIFIED'
   if name=='gui-present':r['guiReferenceAutomation']=copy.deepcopy(self.fixture()['records'][1]['guiReferenceAutomation'])
   if name=='login-present':r['syntheticLogin']={'status':'next-window-not-yet-identified'}
   if name=='missing-oracle':del r['commonHeaderOracle']
   self.assertRejected(f,name)
 def test_classification_matches_probe_and_oracle_contracts(self):
  root=pathlib.Path(__file__).parent;probe=(root/'probe-htkk-windows.ps1').read_text(encoding='utf-8')
  # 'timed-out' is only reported when the last valid result was neither matched nor terminal;
  # a non-'none' failureCategory or any mismatch/rejection stage is terminal ('failed').
  self.assertIn("$lastGui.status=if($matched){'matched'}elseif($terminal){'failed'}elseif($automationRootExited){'root-exited'}else{'timed-out'}",probe)
  self.assertIn("$terminal=$nextGui.failureCategory -ne 'none' -or $nextGui.stage -in @(",probe)
  # Oracles run and are checked after install, before synthetic login, permit and GUI.
  login=probe.index('$report.syntheticLogin = Invoke-HtkkSyntheticLogin')
  for key,reason in retry.ORACLES:
   self.assertLess(probe.index('$report.'+key+' = Invoke-Htkk'),login);self.assertLess(probe.index("throw '"+reason+"'"),login)
  for script in ('Test-HtkkTaxIdOracle.ps1','Test-HtkkProfileAliasOracle.ps1','Test-HtkkCommonHeaderOracle.ps1'):
   self.assertIn("if($compilerRun.timedOut){$safe.status='compile-timeout';return $safe}",(root/script).read_text(encoding='utf-8'))
  self.assertLess(login,probe.index('$report.guiAutomationPermitBoundary.authorizationAttempted=$true'))
  for k in retry.GUI_TIMEOUT_REQUIRED:self.assertTrue(k=='status'or k in retry.FIELDS,k)
  for mode,categories in retry.GUI_TIMEOUT_STAGE_CATEGORIES.items():self.assertNotIn('lifecycle',categories,mode)
  for k in retry.PRE_FILE_EXPORT+retry.PRE_FILE_EXPORT_PINS+tuple(retry.WEB_INPUT_HASHES)+retry.COMPARISON_FIELDS:self.assertIn(k,retry.FIELDS)
  self.assertTrue(all(any(k.startswith(p)for k in retry.FIELDS)for p in retry.COMPARISON_PREFIXES))
  # Every output/hash/rejection/mismatch field the harness reports must stay at its default.
  for k in retry.FIELDS:
   if k.endswith(('Bytes','Sha256','RejectedMessageId','MismatchMask','FileExists'))and k!='webImportInputSha256':self.assertTrue(retry._must_stay_default(k),k)

# Non-default GUI fields of the real failing results (all other registry fields at defaults).
# Run 42270894541 (release 219, 01GTGT-noactivity-cancel-sale10): the original Save dialog was
# matched and the path typed, but focus/read-back failed -> operation-not-established, no file.
DIALOG_FAILURE_GUI={
 'status':'failed','format':'htkk-gui-reference-automation-v1','mode':'gtgt-web-import-inspect','stage':'gtgt-export-filename-keyboard-typed',
 'failureCategory':'operation-not-established','editorKind':'other-control','runtime':'clr2-x86-custom-reference','sourcePinsVerified':True,'visibleForms':1,'spreadCount':1,
 'sheetRows':75,'sheetColumns':22,'mstBoxesMatched':True,'initialRequiredTextBlank':True,'editingApiAvailable':True,'performedInputCount':7,'originalSaveInvoked':True,
 'savedHeaderExists':True,'savedHeaderChecksMatched':True,'savedHeaderCheckedFieldCount':8,'saveDialogKind':'success-0002','profileClosed':True,'mainMenuObserved':True,
 'd1MenuClicked':True,'gtgtPeriodObserved':True,'menuRowCount':314,'menuClickCount':1,'periodControlCount':137,'periodYearMonthMatched':True,'periodFirstDeclarationMatched':True,
 'periodActivityMatched':True,'periodGeographyMatched':True,'periodNoAnnexMatched':True,'periodConfirmInvoked':True,'gtgtWorkbookPinsVerified':True,'gtgtMenuVersionMatched':True,
 'gtgtPeriodModelMatched':True,'gtgtSheetObserved':True,'gtgtSheetNameMatched':True,'gtgtDimensionsMatched':True,'gtgtIdentityMatched':True,'gtgtCt21Ready':True,
 'gtgtCt21CaseMatched':True,'gtgtCt21ConfirmationMatched':True,'gtgtCt21LocksMatched':True,'gtgtCt21BeforeExportMatched':True,'gtgtSignatureReady':True,'gtgtSheetRows':72,
 'gtgtSheetColumns':24,'gtgtSheetCount':11,'exportCommandInvoked':True,'exportSelectorMatched':True,'exportButtonInvoked':True,'exportDialogMatched':True,
 'exportDestinationFresh':True,'exportSchemaPinnedVerified':True,'exportFilenameParentKind':'combobox','gtgtCt42BeforeExportObserved':True,'gtgtCt42LockedBeforeExport':True,
 'gtgtAutoCalculationReady':True,'gtgtBusinessInstanceMatched':True,'gtgtCaseMoneyMatched':True,'gtgtCt42Locked':True,'webInputVerified':True,
 'webImportInputSha256':'b8b7b6c01c51282a5492d698754e4d0adeef1d25a48d9e346ad2a0318a1af4de','webSourceSha':'7c01e635a426bb3d4c4a295fb05f311cf3d9fd24',
 'webCaseId':'01GTGT-noactivity-cancel-sale10-M10-2026','webCaseEditCount':2,'gtgtCaseMoneyCount':27,'gtgtCaseNonzeroMask':10727808,
 'controlKinds':{'form': 1, 'button': 18, 'combo': 3, 'text': 2, 'spread': 1, 'other': 18},'webSigningDateEdited':True,'webSigningDateReady':True,'webSigningDateCellKind':4,
 'waitSeconds':22,}
# Run 42268954396 (release 218, 01GTGT-annex12-two-plants-nonzero): operation-not-established
# while checking the imported annex12 after a real export and import. Never retryable.
ANNEX12_FAILURE_GUI={
 'status':'failed','annex12ExportMainZeroMatched':True,'annex12WebImportSheetMatched':True,'annex12WebBaselineSchemaVerified':True,'annex12WebImportGroupCount':2,
 'annex12WebImportRowCount':5,'annex12WebImportDisplayEmptyMask':8659208,'annex12WebHeadAuthorityRepairCount':3,'annex12WebHeadAuthorityFailureMask':2116,
 'annex12WebHeadAuthorityComboMask':1899,'annex12InputReadOnlyIdentityMatched':True,'annex12InputIdentityMatched':True,'annex12InputTypesMatched':True,
 'annex12InputGeographyMatched':True,'annex12InputTaxAuthoritiesMatched':True,'annex12InputPercentagesMatched':True,'annex12InputZeroTaxMatched':True,'annex12InputActionCount':14,
 'format':'htkk-gui-reference-automation-v1','mode':'gtgt-web-import-inspect','stage':'gtgt-annex12-web-import-checking','failureCategory':'operation-not-established',
 'editorKind':'combo','runtime':'clr2-x86-custom-reference','sourcePinsVerified':True,'visibleForms':1,'spreadCount':1,'sheetRows':75,'sheetColumns':22,'mstBoxesMatched':True,
 'initialRequiredTextBlank':True,'editingApiAvailable':True,'performedInputCount':7,'originalSaveInvoked':True,'savedHeaderExists':True,'savedHeaderChecksMatched':True,
 'savedHeaderCheckedFieldCount':8,'saveDialogKind':'success-0002','profileClosed':True,'mainMenuObserved':True,'d1MenuClicked':True,'gtgtPeriodObserved':True,'menuRowCount':314,
 'menuClickCount':1,'periodControlCount':137,'periodYearMonthMatched':True,'periodFirstDeclarationMatched':True,'periodActivityMatched':True,'periodGeographyMatched':True,
 'periodConfirmInvoked':True,'gtgtWorkbookPinsVerified':True,'gtgtMenuVersionMatched':True,'gtgtPeriodModelMatched':True,'gtgtSheetObserved':True,'gtgtSheetNameMatched':True,
 'gtgtDimensionsMatched':True,'gtgtIdentityMatched':True,'gtgtCt21Ready':True,'gtgtSignatureReady':True,'periodAnnex12Matched':True,'annex12SourcePinsMatched':True,
 'annex12SheetObserved':True,'annex12StructureMatched':True,'annex12GroupMetadataMatched':True,'annex12SttMatched':True,'annex12LocksMatched':True,'annex12SelectionActionCount':1,
 'annex12SheetRows':66,'annex12SheetColumns':45,'annex12NumericCount':8,'annex12GroupCount':1,'annex12FirstGroupId':1,'annex12FirstGroupRows':1,'annex12RowTabClickInvoked':True,
 'annex12F5Visible':True,'annex12F5Invoked':True,'annex12RowBeforeMatched':True,'annex12RowAfterMatched':True,'annex12RowSttMatched':True,'annex12RowLocksMatched':True,
 'annex12RowBeforeRows':66,'annex12RowAfterRows':67,'annex12RowBeforeGroupRows':1,'annex12RowAfterGroupRows':2,'annex12RowAfterGroupId':1,'annex12RowInsertActionCount':1,
 'annexSelectedCount':1,'gtgtSheetRows':72,'gtgtSheetColumns':24,'gtgtSheetCount':11,'exportCommandInvoked':True,'exportSelectorMatched':True,'exportButtonInvoked':True,
 'exportDialogMatched':True,'exportDestinationFresh':True,'exportDialogSubmitted':True,'exportFileExists':True,'exportXmlRootMatched':True,'exportSyntheticIdentityMatched':True,
 'exportSuccessAcknowledged':True,'exportSchemaPinnedVerified':True,'exportFilenameKeyboardCommitted':True,'exportFilenameParentKind':'combobox','exportOriginalPathMatched':True,
 'exportOriginalPathKind':'expected-path','exportScopedFileCount':1,'exportScopedXmlCount':1,'exportBytes':5426,
 'exportSha256':'b7db30d17185dc86bdb4d048f82ddd9167c6aca950a7ea2298ca43ca20e3f348','roundtripImportCommandInvoked':True,'roundtripImportDialogMatched':True,
 'roundtripImportKeyboardCommitted':True,'roundtripImportDialogSubmitted':True,'roundtripImportPathMatched':True,'roundtripImportSheetMatched':True,'roundtripImportSucceeded':True,
 'roundtripImportCheckedMoneyCount':27,'gtgtCt42BeforeExportObserved':True,'gtgtCt42LockedBeforeExport':True,'gtgtCt42AfterImportObserved':True,'gtgtCt42LockedAfterImport':True,
 'gtgtAutoCalculationReady':True,'gtgtBusinessInstanceMatched':True,'gtgtCaseMoneyMatched':True,'gtgtCt42Locked':True,'webInputVerified':True,
 'webImportInputSha256':'a17f2b51b92b4eded8230dbec5df81f5757578dce28027bb32a343830ec69cae','webSourceSha':'09c8e71879fd7fb1f3f4a8f9cf53aa889f72dca0',
 'webCaseId':'01GTGT-annex12-two-plants-nonzero-M10-2026','webCaseEditCount':1,'gtgtCaseMoneyCount':27,'gtgtCaseNonzeroMask':10727808,
 'controlKinds':{'form': 1, 'button': 18, 'combo': 3, 'text': 2, 'spread': 1, 'other': 18},'webSigningDateEdited':True,'webSigningDateReady':True,'webSigningDateCellKind':4,
 'waitSeconds':31,}
class ExportDialogNotEstablished(unittest.TestCase):
 def fixture(self,gui=DIALOG_FAILURE_GUI):
  f=GuiPreExportTimeout().fixture();r=f['records'][1]
  shape={k:copy.deepcopy(v['default'])for k,v in retry.FIELDS.items()}
  shape.update(copy.deepcopy(gui),periodControls=copy.deepcopy(r['guiReferenceAutomation']['periodControls']))
  r['guiReferenceAutomation']=shape;return f
 def test_real_export_dialog_focus_failure_retries_once_on_attempt_one(self):
  f=self.fixture();self.assertEqual(retry.classify(f['jobs'],f['records']),'gui-pre-export-timeout')
  GuiPreExportTimeout.assertRetried(self,f,'real')
  for stage in retry.EXPORT_DIALOG_STAGES:
   f=self.fixture();f['records'][1]['guiReferenceAutomation']['stage']=stage;GuiPreExportTimeout.assertRetried(self,f,stage)
  f=self.fixture();f['records'][1]['guiReferenceAutomation']['exportFilenameParentKind']='combobox-ex';GuiPreExportTimeout.assertRetried(self,f,'combobox-ex')
 def test_operation_not_established_outside_the_export_save_dialog_is_never_retried(self):
  f=self.fixture(ANNEX12_FAILURE_GUI);GuiPreExportTimeout.assertRejected(self,f,'annex12-real')
  f=self.fixture(ANNEX12_FAILURE_GUI);f['records'][1]['guiReferenceAutomation']['stage']='gtgt-export-filename-keyboard-typed';GuiPreExportTimeout.assertRejected(self,f,'annex12-real-at-dialog-stage')
  stages=['gtgt-import-filename-focus-waiting','gtgt-import-filename-focus-timeout','gtgt-import-filename-keyboard-typed','gtgt-import-file-dialog-waiting',
   'gtgt-import-original-reading','gtgt-annex12-web-import-checking','gtgt-annex12-input-editing','gtgt-annex12-nonzero-reexport-invoking','declaration-export-file-dialog-waiting',
   'gtgt-period-configuring','gtgt-period-confirm-invoking','waiting-gtgt-sheet','gtgt-case-editing','gtgt-noactivity-confirming','gtgt-export-command-invoking',
   'gtgt-export-file-dialog-waiting','gtgt-export-original-writing','gtgt-export-success-file-checking','gtgt-export-original-message-rejected','gtgt-reexport-command-invoking',
   'gtgt-reexport-ready-waiting','gtgt-web-import-ready-waiting','gtgt-roundtrip-inspected','waiting-profile-close','gtgt-menu-click-D1']
  self.assertTrue(set(stages)<=set(retry.STAGE_CATEGORIES))
  for stage in stages:
   f=self.fixture();f['records'][1]['guiReferenceAutomation']['stage']=stage;GuiPreExportTimeout.assertRejected(self,f,stage)
  mutations={'io':('failureCategory','io'),'com':('failureCategory','com'),'argument':('failureCategory','argument'),'reflection':('failureCategory','reflection-invocation'),
   'other':('failureCategory','other-standard'),'status-timeout':('status','timed-out'),'status-exited':('status','root-exited'),'dialog-unmatched':('exportDialogMatched',False),
   'editor-other':('exportFilenameParentKind','other'),'editor-unobserved':('exportFilenameParentKind','not-observed'),'committed':('exportFilenameKeyboardCommitted',True),
   'submitted':('exportDialogSubmitted',True),'file':('exportFileExists',True),'bytes':('exportBytes',5426),'sha':('exportSha256','b'*64),'scoped':('exportScopedFileCount',1),
   'path':('exportOriginalPathKind','expected-path'),'ack':('exportSuccessAcknowledged',True),'export-rejected':('exportRejectedMessageId',16),'import-rejected':('importRejectedMessageId',478),
   'money-unmatched':('gtgtCaseMoneyMatched',False),'money-mismatch':('gtgtCaseMismatchMask',2),'header-mismatch':('savedHeaderMismatchMask',1),
   'roundtrip':('roundtripImportCommandInvoked',True),'reexport':('roundtripReexportCommandInvoked',True),'web-tax':('webTaxValuesMatched',True),
   'annex-web':('annex12WebImportSheetMatched',True),'after-import':('gtgtCt42AfterImportObserved',True),'web-input':('webInputVerified',False),'selector':('exportSelectorMatched',False),
   'destination':('exportDestinationFresh',False),'mode':('mode','gtgt-roundtrip-inspect'),'unknown':('futureProgressFlag',True),'wait-type':('waitSeconds',22.0)}
  for name,(key,value) in mutations.items():
   f=self.fixture();f['records'][1]['guiReferenceAutomation'][key]=value;GuiPreExportTimeout.assertRejected(self,f,name)
  for name in ['cue','evidence','published','attempt2','declaration-mode']:
   f=self.fixture();r=f['records'][1]
   if name=='cue':r['nativeDialogCueCounts']={'message':1}
   if name=='evidence':r['privateGtgtExportEvidence']={'status':'retained'}
   if name=='published':f['records'][2]=dict(FILES,status='published')
   if name=='attempt2':f['run']['run_attempt']=2
   if name=='declaration-mode':self.assertFalse(retry._gui_pre_export_timeout(dict(r['guiReferenceAutomation'],mode=retry.DECLARATION_MODE,stage='declaration-export-file-dialog-waiting'),retry.DECLARATION_MODE));continue
   GuiPreExportTimeout.assertRejected(self,f,name)
  # A dialog-stage timeout keeps the original rule: the full budget must have elapsed.
  f=self.fixture();f['records'][1]['guiReferenceAutomation'].update(status='timed-out',failureCategory='none');GuiPreExportTimeout.assertRejected(self,f,'short-timeout')
  f=self.fixture();f['records'][1]['guiReferenceAutomation'].update(status='timed-out',failureCategory='none',waitSeconds=60);GuiPreExportTimeout.assertRetried(self,f,'dialog-timeout')
 def test_dialog_stages_match_the_original_export_dialog_driver(self):
  root=pathlib.Path(__file__).parent;export=(root/'HtkkGtgtExportInspection.cs').read_text(encoding='utf-8')
  enums=(root/'HtkkNativeAutomationEnums.cs').read_text(encoding='utf-8');gui=(root/'HtkkGuiReferenceAutomation.cs').read_text(encoding='utf-8')
  self.assertEqual(set(retry.EXPORT_DIALOG_STAGES),{s for s in retry.STAGE_CATEGORIES if s.startswith('gtgt-export-filename-')})
  self.assertEqual(len(retry.EXPORT_DIALOG_STAGES),6)
  for stage in retry.EXPORT_DIALOG_STAGES:self.assertIn('return "'+stage+'";',enums)
  self.assertIn('error is InvalidOperationException?"operation-not-established"',gui)
  body=export[export.index('private bool TrySubmitOriginalFileDialog('):export.index('private int OriginalMessageCatalogueId(')]
  # The editor parent kind is recorded, then the dialog marked matched, before any focus stage;
  # the filename is committed and Save posted only after the last keyboard stage.
  kind=body.index('exportFilenameParentKind=parentClass==');matched=body.index('else exportDialogMatched=true;')
  self.assertLess(kind,matched);self.assertLess(matched,body.index('HtkkFilenameDialogAction.FocusTimeout'))
  typed=body.index('HtkkFilenameDialogAction.KeyboardTyped');committed=body.index('else exportFilenameKeyboardCommitted=true;')
  submitted=body.index('else exportDialogSubmitted=true;');post=body.index('PostMessage(save,245')
  self.assertLess(typed,committed);self.assertLess(committed,submitted);self.assertLess(submitted,post)
  self.assertIn('if(File.Exists(desiredPath))throw new InvalidOperationException();',body)
