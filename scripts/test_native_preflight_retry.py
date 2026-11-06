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
   'scoped':('exportScopedFileCount',1),'scoped-xml':('exportScopedXmlCount',1),'selector':('exportSelectorMatched',True),'button':('exportButtonInvoked',True),
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
