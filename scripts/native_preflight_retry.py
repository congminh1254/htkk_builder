"""One classified retry before tax execution; never retries mismatches or weakens evidence."""
import re
BUILDER='congminh1254/htkk_builder';SOURCE='htkk-net/htkk_web'
FRAMEWORK='Check clean Framework UIA assembly readiness'
PROBE='Kiểm tra nguồn và điều kiện Windows'
RETAIN='Retain verified raw native web reexport privately'
# Declaration families retain through their own step; with nothing staged it succeeds and
# reports exactly 'not-staged' (no original export existed), so only the probe step fails.
DECLARATION_MODE='declaration-web-import-inspect'
DECLARATION_RETAIN='Retain raw native declaration export privately'
DECLARATION_NOT_STAGED={'format':'htkk-declaration-native-output-publication-status-v1','status':'not-staged'}
STARTUP_MODES=('gtgt-web-import-inspect',DECLARATION_MODE)
PROFILE_CLOSE_LIMIT=60
# Valid child phases short of 'complete'; 'invalid'/'unavailable' never qualify.
FRAMEWORK_RUNNING_PHASES=('not-started','client-loading','types-loading','modules-loading','cmdlets','result-writing')
# Exact pre-close progress of the timed-out GUI helper; every other field must still be unprogressed.
PROFILE_SAVED={'status':'timed-out','format':'htkk-gui-reference-automation-v1','mode':'gtgt-web-import-inspect','stage':'waiting-profile-close','failureCategory':'none','runtime':'clr2-x86-custom-reference','sourcePinsVerified':True,'spreadCount':1,'mstBoxesMatched':True,'initialRequiredTextBlank':True,'editingApiAvailable':True,'performedInputCount':7,'originalSaveInvoked':True,'savedHeaderExists':True,'savedHeaderChecksMatched':True,'savedHeaderCheckedFieldCount':8,'saveDialogKind':'success-0002','savedHeaderMismatchMask':0,'profileClosed':False,'realTaxpayerDataUsed':False,'runtimeRoundTrip':False}
DESCRIPTIVE=frozenset(('editorKind','visibleForms','sheetRows','sheetColumns','controlKinds','webCaseId','waitSeconds'))
UNPROGRESSED=(False,0,'','not-observed')
def _exact(value,expected):return all(type(value.get(k))is type(v)and value.get(k)==v for k,v in expected.items())
def _profile_close_not_observed(gui):
 # The original profile Save succeeded and one Close was requested, but the retained
 # owner never hid within the fixed budget. No menu, period, sheet, web input, money,
 # export, import or comparison progressed; a mismatch or terminal stage never matches.
 if type(gui)is not dict or not _exact(gui,PROFILE_SAVED):return False
 if type(gui.get('waitSeconds'))is not int or gui['waitSeconds']<PROFILE_CLOSE_LIMIT or type(gui.get('webCaseId'))is not str:return False
 if type(gui.get('periodControls'))is not dict or gui['periodControls']:return False
 for k,v in gui.items():
  if k in PROFILE_SAVED or k in DESCRIPTIVE or k=='periodControls':continue
  if type(v)not in (bool,int,str)or not any(type(v)is type(u)and v==u for u in UNPROGRESSED):return False
 return True
# Original export selector never appeared within the fixed GUI budget: the synthetic web
# input was verified and the pre-export money check matched, one original Kết xuất click was
# made, then nothing else happened. No selector, dialog, file, original HTKK message, import,
# re-export or web/XML comparison progressed, so no tax output exists that could mismatch.
EXPORT_PENDING=dict({k:v for k,v in PROFILE_SAVED.items() if k not in ('stage','profileClosed')},stage='gtgt-export-command-invoking',profileClosed=True,
 mainMenuObserved=True,d1MenuClicked=True,gtgtPeriodObserved=True,periodConfirmInvoked=True,gtgtSheetObserved=True,gtgtWorkbookPinsVerified=True,
 gtgtMenuVersionMatched=True,gtgtPeriodModelMatched=True,gtgtSheetNameMatched=True,gtgtDimensionsMatched=True,gtgtIdentityMatched=True,
 gtgtSignatureReady=True,gtgtCaseMoneyMatched=True,gtgtCaseMismatchMask=0,webInputVerified=True,
 webTaxValuesMatched=False,webCreationDateMatchedNativeBaseline=False,webServiceIdentityMatched=False,webTaxLeafCount=0,
 gtgtCt21AfterImportMatched=False,gtgtCt42AfterImportObserved=False,gtgtCt42LockedAfterImport=False,
 exportCommandInvoked=True,exportSchemaPinnedVerified=True,exportDestinationFresh=True,exportSelectorMatched=False,exportButtonInvoked=False,
 exportDialogMatched=False,exportDialogSubmitted=False,exportFileExists=False,exportXmlRootMatched=False,exportSyntheticIdentityMatched=False,
 exportSuccessAcknowledged=False,exportFilenameKeyboardCommitted=False,exportFilenameParentKind='not-observed',exportOriginalPathMatched=False,
 exportOriginalPathKind='not-observed',exportScopedFileCount=0,exportScopedXmlCount=0,exportBytes=0,exportSha256='',
 exportRejectedMessageId=0,importRejectedMessageId=0)
# Pre-export navigation/input state that legitimately varies per synthetic case; every
# other field (roundtrip, import, annex, declaration, amendment, unknown) must be unprogressed.
PRE_EXPORT_PREFIXES=('menu','period','gtgt','web')
def _export_selector_not_observed(gui):
 if type(gui)is not dict or not _exact(gui,EXPORT_PENDING):return False
 if type(gui.get('waitSeconds'))is not int or gui['waitSeconds']<PROFILE_CLOSE_LIMIT or type(gui.get('webCaseId'))is not str:return False
 for k,v in gui.items():
  if k in EXPORT_PENDING or k in DESCRIPTIVE:continue
  if k.startswith(PRE_EXPORT_PREFIXES)and not any(w in k for w in ('AfterImport','Reexport','Mismatch','Rejected')):
   if type(v)in (bool,int,str)or (k=='periodControls'and type(v)is dict):continue
   return False
  if type(v)not in (bool,int,str)or not any(type(v)is type(u)and v==u for u in UNPROGRESSED):return False
 return True
def _supplier_boundary(r,modes=('gtgt-web-import-inspect',)):
 boundary=r.get('supplierProcessBoundary',{})
 if r.get('guiReferenceAutomationMode')not in modes or r.get('stage')!='blocked':return False
 if r.get('referenceHostResult',{}).get('status')!='original-starting':return False
 if any(r.get(k)is not True for k in ('sourceHashesVerified','originalSourcesUnmodified','officialDistributionFilesVerified','msiAuthenticodeValid','nativeHelperJobsStopped','hostOutboundBlocked','originalOutboundBlocked')):return False
 if any(boundary.get(k)is not True for k in ('cleanupVerified','supplierStopped','rootStopped','jobEmpty')):return False
 return r.get('taxDataUsed')is False and r.get('runtimeRoundTrip')is False
LOGIN={'fixtureDirectoryPreexisting':False,'fixtureDirectoryCreated':True,'syntheticIdentifierOnly':True,'realTaxpayerDataUsed':False,'inputVerified':True,'loginClicked':True,'loginHidden':True,'runtimeRoundTrip':False}
PERMIT_KEYS={'uniquePathVerified','initiallyAbsent','authorizationAttempted','absentAfterCleanup'}
def classify(jobs,records):
 ready=[j for j in jobs.get('jobs',[])if j.get('name')=='readiness']
 if len(ready)!=1 or ready[0].get('conclusion')!='failure':return None
 if len(jobs.get('jobs',[]))!=2 or not any(j.get('name')=='report_failure'and j.get('conclusion')=='success'for j in jobs['jobs']):return None
 steps=ready[0].get('steps',[]);failed={s.get('name')for s in steps if s.get('conclusion')=='failure'}
 if failed=={FRAMEWORK} and any(s.get('name')==PROBE and s.get('conclusion')=='skipped'for s in steps):
  bounds=[r for r in records if r.get('format')=='htkk-framework-uia-boundary-v1']
  if len(bounds)==1 and _exact(bounds[0],{'status':'process-timeout','timedOut':True,'processStopped':True,'exitCode':None}):
   # The Framework readiness child runs before HTKK, web input or any tax data exists.
   if _exact(bounds[0],{'phase':'complete'}):return 'framework-uia-exit-timeout'
   if bounds[0].get('phase')in FRAMEWORK_RUNNING_PHASES and type(bounds[0].get('phase'))is str:return 'framework-uia-process-timeout'
 suppliers=[r for r in records if r.get('version')=='5.8.1'and 'supplierProcessBoundary'in r]
 if len(suppliers)!=1:return None
 r=suppliers[0];login=r.get('syntheticLogin',{});permit=r.get('guiAutomationPermitBoundary',{})
 if failed=={PROBE} and r.get('guiReferenceAutomationMode')==DECLARATION_MODE:
  # Declaration startup flake: HTKK never reached its main window (original-starting), the
  # synthetic login saw no profile window, no permit was issued, nothing was staged.
  if type(login)is not dict or type(permit)is not dict or set(permit)!=PERMIT_KEYS or not _supplier_boundary(r,(DECLARATION_MODE,)):return None
  if not any(s.get('name')==DECLARATION_RETAIN and s.get('conclusion')=='success'for s in steps):return None
  declared=[x for x in records if x.get('format')==DECLARATION_NOT_STAGED['format']]
  if len(declared)!=1 or not _exact(declared[0],DECLARATION_NOT_STAGED) or set(declared[0])!=set(DECLARATION_NOT_STAGED):return None
  if r.get('blockedReason')!='SYNTHETIC_LOGIN_NOT_VERIFIED' or r.get('guiReferenceAutomation')is not None:return None
  if not _exact(permit,{'uniquePathVerified':True,'initiallyAbsent':True,'authorizationAttempted':False,'absentAfterCleanup':True}):return None
  if not _exact(login,dict(LOGIN,status='next-window-not-yet-identified',profileWindowObserved=False)):return None
  return 'synthetic-profile-startup-not-observed'
 if failed!={PROBE,RETAIN}:return None
 if type(login)is not dict or type(permit)is not dict or set(permit)!=PERMIT_KEYS or not _supplier_boundary(r):return None
 if r.get('blockedReason')=='SYNTHETIC_LOGIN_NOT_VERIFIED':
  if not _exact(permit,{'uniquePathVerified':True,'initiallyAbsent':True,'authorizationAttempted':False,'absentAfterCleanup':True}):return None
  if r.get('guiReferenceAutomation')is not None:return None
  if not _exact(login,dict(LOGIN,status='next-window-not-yet-identified',profileWindowObserved=False)):return None
  return 'synthetic-profile-startup-not-observed'
 if r.get('blockedReason')=='GUI_REFERENCE_AUTOMATION_NOT_VERIFIED':
  # The permit was issued (only the synthetic profile may be saved); it is still on disk
  # when checked before owned-file deletion, so absentAfterCleanup is false by design.
  if not _exact(permit,{'uniquePathVerified':True,'initiallyAbsent':True,'authorizationAttempted':True,'absentAfterCleanup':False}):return None
  if not _exact(login,dict(LOGIN,status='synthetic-profile-window-observed',profileWindowObserved=True,newIdClicked=True,nextOwnedWindowObserved=True,profileMainCaptionMatched=True,profileSaveCloseMatched=True)):return None
  retained=[x for x in records if x.get('format')=='htkk-web-native-output-publication-status-v1']
  if retained!=[{'format':'htkk-web-native-output-publication-status-v1','status':'rejected','code':'FILES'}]:return None
  gui=r.get('guiReferenceAutomation')
  if _profile_close_not_observed(gui):return 'synthetic-profile-close-not-observed'
  # No native dialog cue and no retained private export/output evidence may exist.
  if any(k not in r or r[k]is not None for k in ('privateGtgtExportEvidence','privateWebNativeOutputEvidence'))or r.get('nativeDialogCueCounts')!={}:return None
  if _export_selector_not_observed(gui):return 'gtgt-export-selector-not-observed'
  return None
 return None

def recover(status,case,source,builder,input_commit,get,records,send,actions_token,status_token,retried):
 if not actions_token or not status_token:return False
 if status.get('state')not in ('failure','error')or not re.fullmatch(r'htkk-native/[a-z0-9-]+',case):return False
 if not re.fullmatch('[a-f0-9]{40}',source)or not re.fullmatch('[a-f0-9]{40}',builder)or not re.fullmatch('[a-f0-9]{40}',input_commit):return False
 if 'input:'+input_commit not in status.get('description',''):return False
 match=re.fullmatch(r'https://github\.com/congminh1254/htkk_builder/actions/runs/([1-9][0-9]*)',status.get('target_url',''))
 if not match:return False
 rid=match[1];run=get(BUILDER,'actions/runs/'+rid)
 if run.get('id')!=int(rid)or run.get('repository',{}).get('full_name')!=BUILDER or run.get('path')!='.github/workflows/probe-htkk-windows.yml'or run.get('event')!='workflow_dispatch'or run.get('head_branch')!='main'or run.get('head_sha')!=builder:return False
 if type(run.get('run_attempt'))is not int or run['run_attempt']not in (1,2):return False
 # A failure callback can precede final job cleanup; wait for complete evidence.
 if run.get('status')in ('queued','pending','in_progress','waiting','requested'):return True
 if run.get('status')=='completed'and run.get('conclusion')=='success':return True
 if rid in retried:
  return run.get('run_attempt')in (1,2)and (run.get('run_attempt')==1 or run.get('status')!='completed'or run.get('conclusion')=='success')
 if run.get('run_attempt')!=1 or run.get('status')!='completed'or run.get('conclusion')!='failure':return False
 jobs=get(BUILDER,'actions/runs/'+rid+'/attempts/1/jobs?per_page=100')
 if jobs.get('total_count')!=len(jobs.get('jobs',[])):return False
 ready=[j for j in jobs.get('jobs',[])if j.get('name')=='readiness']
 if len(ready)!=1:return False
 reason=classify(jobs,records(get(BUILDER,'actions/jobs/'+str(ready[0]['id'])+'/logs')))
 if reason is None:return False
 send('https://api.github.com/repos/'+BUILDER+'/actions/runs/'+rid+'/rerun-failed-jobs',actions_token,{})
 retried.add(rid) # Prevent duplicate POSTs during eventual-consistency delays.
 send('https://api.github.com/repos/'+SOURCE+'/statuses/'+source,status_token,{'state':'pending','context':case,'target_url':status['target_url'],'description':'One classified pre-tax retry input:'+input_commit})
 print('One classified pre-tax retry queued ('+reason+'); whole evidence verification remains required.',flush=True)
 return True
