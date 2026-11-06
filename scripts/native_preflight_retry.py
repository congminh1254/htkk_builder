"""One classified retry before tax execution; never retries mismatches or weakens evidence."""
import json,pathlib,re
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
# Pre-HTKK Windows process/Job boundary self-tests (probe-htkk-windows.yml, in order). Each
# spawns only its own synthetic fixture processes; they run before the synthetic web XML fetch,
# the supplier download and any HTKK launch, so no web input, tax data or output exists yet.
# Pure contract/policy self-tests (deterministic), the Framework UIA step (its own classified
# categories need its boundary record) and the web-tax comparison step are deliberately excluded.
SELFTEST_STEPS=('Check bounded native process and clean environment','Check bounded compiler diagnostics and complete cleanup',
 'Check bounded oracle Job cleanup and environment','Check supplier Job cleanup and retained identity boundary','Check UIA cleanup and bounded result boundary')
# The only JSON a readiness log may hold this early: the builder unittest step's source-update
# trust-check lines (metadata only, never ready). Any other record (supplier/probe report,
# Framework boundary, retained output, web or tax fields) means it is not this failure.
SELFTEST_NOISE_KEYS=frozenset(('result','failureCode','trustRequested','ready','trustStatus','credentialsSafe'))
def _selftest_noise(x):
 return type(x)is dict and set(x)<=SELFTEST_NOISE_KEYS and type(x.get('result'))is str and x.get('ready')is False and x.get('trustRequested',False)is False and all(v is None or type(v)in (bool,str)for v in x.values())
def _selftest_fixture_failed(job,records):
 # Exactly one readiness step failed and it is a listed self-test; every earlier step succeeded,
 # every later step (fetch, probe, retain, report) was skipped; only the runner's own post
 # steps may run afterwards. Attempt 1 only.
 steps=job.get('steps',[])
 if job.get('run_attempt')!=1 or type(job.get('run_attempt'))is not int or not steps:return False
 numbers=[s.get('number')for s in steps]
 if any(type(n)is not int for n in numbers)or numbers!=sorted(set(numbers)):return False
 failed=[i for i,s in enumerate(steps)if s.get('conclusion')!='success'and s.get('conclusion')!='skipped']
 if len(failed)!=1 or steps[failed[0]].get('conclusion')!='failure'or steps[failed[0]].get('name')not in SELFTEST_STEPS:return False
 i=failed[0]
 if any(s.get('conclusion')!='success'or s.get('status')!='completed'for s in steps[:i]):return False
 later=[s for s in steps[i+1:]if not(s.get('name','').startswith('Post ')or s.get('name')=='Complete job')]
 if any(s.get('conclusion')!='skipped'for s in later):return False
 if any(s.get('conclusion')!='success'for s in steps[i+1:]if s not in later):return False
 names=[s.get('name')for s in later]
 if any(names.count(n)!=1 for n in (PROBE,RETAIN,DECLARATION_RETAIN)):return False
 return all(_selftest_noise(x)for x in records)
# ---- gui-pre-export-timeout: one general, invariant-defined pre-tax timing category ----
# A bounded helper ran out of time before any native export file existed. It is defined by
# invariants instead of an exact stage so new GUI timing shapes need no new category: the helper
# result is 'timed-out' with failureCategory 'none' (the probe only reports 'timed-out' when the
# last valid result was neither matched nor terminal, and every mismatch/rejection stage is
# terminal), no export/output file or hash exists, no original HTKK message or dialog cue was
# seen, no import/re-export/web or declaration comparison progressed, every money or identity
# check that ran matched, and no private evidence was retained. Nothing exists that could
# mismatch, so a rerun can only reproduce the same fully verified evidence path.
REGISTRY=json.loads(pathlib.Path(__file__).with_name('htkk-native-automation-registry.json').read_text(encoding='utf-8'))
FIELDS=REGISTRY['resultFields'];STAGE_CATEGORIES={s['id']:s['category']for s in REGISTRY['stages']}
GUI_TIMEOUT_REQUIRED={'status':'timed-out','failureCategory':'none','format':'htkk-gui-reference-automation-v1','runtime':'clr2-x86-custom-reference',
 'sourcePinsVerified':True,'mstBoxesMatched':True,'initialRequiredTextBlank':True,'editingApiAvailable':True,'spreadCount':1,'performedInputCount':7,
 'originalSaveInvoked':True,'savedHeaderExists':True,'savedHeaderChecksMatched':True,'savedHeaderCheckedFieldCount':8,'saveDialogKind':'success-0002',
 'savedHeaderMismatchMask':0,'profileClosed':True,'mainMenuObserved':True,'webInputVerified':True,'realTaxpayerDataUsed':False,'runtimeRoundTrip':False,
 'exportFileExists':False,'exportBytes':0,'exportSha256':'','exportScopedFileCount':0,'exportScopedXmlCount':0,'exportRejectedMessageId':0,'importRejectedMessageId':0}
# Navigation/identity checks that precede the verified web input in each family.
GUI_TIMEOUT_NAVIGATION={'gtgt-web-import-inspect':('d1MenuClicked','gtgtPeriodObserved','periodConfirmInvoked','gtgtWorkbookPinsVerified','gtgtMenuVersionMatched',
  'gtgtPeriodModelMatched','gtgtSheetObserved','gtgtSheetNameMatched','gtgtDimensionsMatched','gtgtIdentityMatched'),
 DECLARATION_MODE:('declarationMenuClicked',)}
# Stage families that follow the verified web input (never profile lifecycle, menu or period).
GUI_TIMEOUT_STAGE_CATEGORIES={'gtgt-web-import-inspect':('sheet','annex12','export-roundtrip'),DECLARATION_MODE:('declaration',)}
# The only export flags that may have progressed: command, selector, button and dialog, each
# requiring the previous one. Submission, filename, path, file, XML, ack and hashes may not.
PRE_FILE_EXPORT=('exportCommandInvoked','exportSelectorMatched','exportButtonInvoked','exportDialogMatched')
PRE_FILE_EXPORT_PINS=('exportSchemaPinnedVerified','exportDestinationFresh')
WEB_INPUT_HASHES={'webImportInputSha256':64,'webSourceSha':40}
COMPARISON_PREFIXES=('roundtrip','declarationImport','declarationCell','declarationSchema','declarationServiceIdentity','declarationCreationDate','declarationXml',
 'declarationTree','annex12Web','annex12Export','annex12Nonzero','amendment')
COMPARISON_FIELDS=('webTaxValuesMatched','webCreationDateMatchedNativeBaseline','webServiceIdentityMatched','webTaxLeafCount')
# Stage words that mean an original message, a mismatch, an output being written/checked, a
# saved declaration, or a later import/re-export/comparison phase.
GUI_TIMEOUT_STAGE_WORDS=('mismatch','not-matched','unmatched','rejected','not-unique','hidden','missing','unavailable','invalid','not-verified','not-established',
 'preexists','success','inspected','saved','save','writing','validating','import','reexport','roundtrip','amendment','lifecycle')
def _field_ok(k,v):
 spec=FIELDS.get(k)
 if spec is None:return False
 kind=spec['kind']
 if kind=='boolean':return type(v)is bool
 if kind=='integer':return type(v)is int and spec.get('minimum',0)<=v<=spec.get('maximum',v)
 if kind=='hex':return type(v)is str and (v==''or re.fullmatch('[0-9a-f]{%d}'%spec['length'],v)is not None)
 if kind=='string':return type(v)is str and len(v)<=spec.get('maximumLength',4096)
 if kind=='enum':return type(v)is str and (v in spec['values']if 'values'in spec else True)
 if kind=='object':return type(v)is dict and all(type(a)is str and (type(b)is int or(type(b)is dict and all(type(x)is str and type(y)in(bool,int,str)for x,y in b.items())))for a,b in v.items())
 return False
def _must_stay_default(k):
 low=k.lower()
 if 'export'in low and 'beforeexport'not in low and k not in PRE_FILE_EXPORT+PRE_FILE_EXPORT_PINS:return True
 if k.startswith(COMPARISON_PREFIXES)or k in COMPARISON_FIELDS or 'AfterImport'in k or 'Reexport'in k:return True
 if 'mismatch'in low or 'FailureMask'in k or 'RejectedMessageId'in k or 'Cue'in k:return True
 return (FIELDS[k]['kind']=='hex'and k not in WEB_INPUT_HASHES)or k.endswith(('Bytes','FileExists','FileCount','XmlCount'))
# Narrow sibling: the original GTGT export Save dialog was matched (its filename editor sits in
# the verified common-dialog combo) and keyboard focus/typing into that editor could not be
# established (HtkkGtgtExportInspection.TrySubmitOriginalFileDialog throws
# InvalidOperationException -> 'operation-not-established' when focus is lost, the focus gate
# times out, or the typed text does not read back). It fails before the filename is committed
# or Save is pressed, so no file can exist. Only these six generated export filename stages
# qualify: never the import dialog, annex12, declaration, period, sheet or any later stage.
EXPORT_DIALOG_STAGES=tuple(REGISTRY['dynamicStageMappings']['filenameDialog']['export'].values())
EXPORT_DIALOG_FAILURE={'status':'failed','failureCategory':'operation-not-established','exportDialogMatched':True,'exportFilenameKeyboardCommitted':False,'exportDialogSubmitted':False}
EXPORT_DIALOG_EDITOR_KINDS=('combobox','combobox-ex')
def _export_dialog_not_established(gui,mode):
 return mode=='gtgt-web-import-inspect'and _exact(gui,EXPORT_DIALOG_FAILURE)and gui.get('stage')in EXPORT_DIALOG_STAGES and gui.get('exportFilenameParentKind')in EXPORT_DIALOG_EDITOR_KINDS
def _gui_pre_export_timeout(gui,mode):
 if type(gui)is not dict or mode not in GUI_TIMEOUT_NAVIGATION:return False
 dialog=_export_dialog_not_established(gui,mode)
 required=dict(GUI_TIMEOUT_REQUIRED,mode=mode)
 if dialog:required.update(status='failed',failureCategory='operation-not-established')
 if not _exact(gui,required):return False
 # A timeout spent the whole budget; a dialog failure ends early (terminal), at any time.
 if type(gui.get('waitSeconds'))is not int or gui['waitSeconds']<(0 if dialog else PROFILE_CLOSE_LIMIT):return False
 stage=gui.get('stage')
 if type(stage)is not str or STAGE_CATEGORIES.get(stage)not in GUI_TIMEOUT_STAGE_CATEGORIES[mode]or any(w in stage for w in GUI_TIMEOUT_STAGE_WORDS):return False
 for k,v in gui.items():
  if k in ('status','waitSeconds'):continue
  if not _field_ok(k,v):return False # Unknown keys or out-of-contract values never qualify.
  default=FIELDS[k]['default'];active=FIELDS[k].get('activeModes')
  # The editor's parent class is recorded just before the dialog is marked matched.
  if k=='exportFilenameParentKind'and gui.get('exportDialogMatched')is True and v in EXPORT_DIALOG_EDITOR_KINDS:continue
  if (_must_stay_default(k)or(active is not None and mode not in active))and not(type(v)is type(default)and v==default):return False
 if any(gui.get(k)is not True for k in GUI_TIMEOUT_NAVIGATION[mode]):return False
 if any(type(gui.get(k,''))is not str or not re.fullmatch('[0-9a-f]{%d}'%n,gui.get(k,''))for k,n in WEB_INPUT_HASHES.items()):return False
 if type(gui.get('webCaseId'))is not str:return False
 flags=[gui.get(k,False)for k in PRE_FILE_EXPORT]
 if any(type(x)is not bool for x in flags)or any(flags[i]and not flags[i-1]for i in range(1,len(flags))):return False
 if flags[0]and any(gui.get(k)is not True for k in PRE_FILE_EXPORT_PINS):return False
 if stage.startswith(('gtgt-export-','declaration-export-'))and not flags[0]:return False
 if mode=='gtgt-web-import-inspect':
  # Pre-export money check: it ran (and must have matched) before any export command.
  money=gui.get('gtgtCaseMoneyCount',0)
  if (flags[0]or money)and(gui.get('gtgtCaseMoneyMatched')is not True or not money):return False
  if gui.get('periodNoAnnexMatched')is True and any(k.startswith(('annex12','annexSelected'))and gui[k]!=FIELDS[k]['default']for k in gui if k in FIELDS):return False
 return True
# Pre-GUI equivalent: one bounded original-DLL oracle helper (compile or run) timed out before
# login, permit, web input or GUI; no oracle case ran, and every other oracle matched or also
# only timed out (a mismatch is never retried).
ORACLES=(('taxIdOracle','TAX_ID_ORACLE_NOT_VERIFIED'),('profileAliasOracle','PROFILE_ALIAS_ORACLE_NOT_VERIFIED'),('commonHeaderOracle','COMMON_HEADER_ORACLE_NOT_VERIFIED'))
ORACLE_TIMEOUTS=('compile-timeout','oracle-timeout')
def _oracle_clean(o):
 return type(o)is dict and o.get('mismatches',0)==0 and type(o.get('mismatches',0))is int and o.get('failedCaseIndices',[])==[] and o.get('userDataUsed')is False and o.get('compilerJobCleanupVerified')is True and o.get('oracleJobCleanupVerified')is True
def _oracle_helper_timeout(r):
 states=[r.get(k)for k,_ in ORACLES]
 if not all(_oracle_clean(o)and o.get('status')in ('matched',)+ORACLE_TIMEOUTS for o in states):return False
 first=[i for i,o in enumerate(states)if o['status']!='matched']
 if not first or r.get('blockedReason')!=ORACLES[first[0]][1]:return False
 for o in (states[i]for i in first):
  if o.get('cases',0)!=0 or o.get('matched',0)!=0 or o.get('originalMethodInvoked',False)is not False or o.get('compilerErrorCodes',[])!=[]:return False
  if o.get('oracleExitCode')is not None or(o['status']=='compile-timeout'and o.get('compilerExitCode')is not None)or(o['status']=='oracle-timeout'and o.get('compilerExitCode')!=0):return False
 return r.get('syntheticLogin')is None and 'syntheticLogin'in r and 'guiReferenceAutomation'in r and r['guiReferenceAutomation']is None
EVIDENCE_STEP_PREFIXES=('Retain ','Publish ')
def _no_retained_evidence(steps,own,conclusion):
 # Every other retain/publish step after the probe was skipped; only the mode's own retain step
 # ran, with the fixed no-output conclusion. No step was cancelled or otherwise unknown.
 names=[s.get('name')for s in steps]
 if names.count(PROBE)!=1 or names.count(own)!=1 or names.index(own)<names.index(PROBE):return False
 if any(s.get('conclusion')not in ('success','skipped','failure')for s in steps):return False
 for s in steps[names.index(PROBE)+1:]:
  if s.get('name')==own:
   if s.get('conclusion')!=conclusion:return False
  elif str(s.get('name')).startswith(EVIDENCE_STEP_PREFIXES)and s.get('conclusion')!='skipped':return False
 return True
def _declaration_status(records):return any(x.get('format')==DECLARATION_NOT_STAGED['format']for x in records)
def _pre_export_report(r,mode):
 return all(k in r and r[k]is None for k in ('privateGtgtExportEvidence','privateWebNativeOutputEvidence'))and r.get('nativeDialogCueCounts',{})=={} and r.get('taxDataUsed')is False and _supplier_boundary(r,(mode,))
def _gui_pre_export_branch(r,mode,permit,login):
 if not _pre_export_report(r,mode):return False
 if r.get('blockedReason')=='GUI_REFERENCE_AUTOMATION_NOT_VERIFIED':
  if not _exact(permit,{'uniquePathVerified':True,'initiallyAbsent':True,'authorizationAttempted':True,'absentAfterCleanup':False}):return False
  if type(login)is not dict or not _exact(login,dict(LOGIN,status='synthetic-profile-window-observed',profileWindowObserved=True,newIdClicked=True,nextOwnedWindowObserved=True,profileMainCaptionMatched=True,profileSaveCloseMatched=True)):return False
  return _gui_pre_export_timeout(r.get('guiReferenceAutomation'),mode)and r['guiReferenceAutomation'].get('mode')==r.get('guiReferenceAutomationMode')
 if any(r.get('blockedReason')==reason for _,reason in ORACLES):
  return _exact(permit,{'uniquePathVerified':True,'initiallyAbsent':True,'authorizationAttempted':False,'absentAfterCleanup':True})and _oracle_helper_timeout(r)
 return False
# Pre-login startup flake (run 42293586893, also 42250602039): the clean HTKK root stayed alive
# at original-starting with only hidden windows until the bounded startup wait ran out. No login,
# UIA scan, permit, GUI automation, web input, tax data or export existed; all oracles matched.
STARTUP_WAIT_FLOOR=45
STARTUP_REPORT={'processStarted':True,'processAliveAfterWait':True,'windowObserved':False,'rootAppWindowObserved':False,'mainWindowHandlePresent':False,
 'startupContext':'only-hidden-app-windows','appVisibleWindowCount':0,'childProcessCount':0,'childVisibleWindowCount':0,'preexistingHtkkProcessCount':0,
 'loginReady':False,'uiaStatus':'not-probed','registrationNonzeroExitCount':0,'registrationUnverifiedExitCount':0,'registrationPostFailureCount':0,
 'registrationAcknowledgementLimitReached':False,'syntheticLoginRequested':True,'nativeDialogCueCounts':{}}
def _pre_login_clean(r,mode,permit):
 # Shared pre-login evidence: no permit, login, GUI automation, export/output evidence, crash
 # event, dialog cue or unexpected process/window kind; all oracles matched; clean supplier.
 if not _exact(permit,{'uniquePathVerified':True,'initiallyAbsent':True,'authorizationAttempted':False,'absentAfterCleanup':True}):return False
 if any(k not in r or r[k]is not None for k in ('syntheticLogin','guiReferenceAutomation','privateGtgtExportEvidence','privateWebNativeOutputEvidence','privateSyntheticLoginDiagnostic')):return False
 if not all(_oracle_clean(r.get(k))and r[k].get('status')=='matched' for k,_ in ORACLES):return False
 events=r.get('applicationEvents')
 if type(events)is not dict or events.get('matchedEventCount')!=0 or type(events.get('matchedEventCount'))is not int:return False
 # Only (hidden) WinForms windows of the root may exist; no dialog or other window kind.
 owned=r.get('ownedWindowKinds')
 if type(owned)is not dict or set(owned)-{'winforms'} or any(type(v)is not int or v<0 for v in owned.values()):return False
 kinds=r.get('descendantProcessKinds')
 if type(kinds)is not dict or any(type(v)is not int or v!=0 for v in kinds.values()):return False
 return _supplier_boundary(r,(mode,))
def _startup_window_not_observed(r,mode,permit):
 if r.get('blockedReason')!='STARTUP_WINDOW_NOT_OBSERVED' or not _exact(r,STARTUP_REPORT):return False
 if type(r.get('startupWaitSeconds'))is not int or r['startupWaitSeconds']<STARTUP_WAIT_FLOOR:return False
 if type(r.get('appHiddenWindowCount'))is not int or r['appHiddenWindowCount']<1:return False
 return _pre_login_clean(r,mode,permit)
# Login-not-ready flake (run 42310240317 attempt 2, 01GTGT-zero-M10-2026): the first visible root
# window appeared at 27 s while the original UI thread was still busy, so the bounded UIA login
# scan timed out (or, after rescans, still saw no ready login form). No login was attempted.
LOGIN_NOT_READY_REPORT={'processStarted':True,'processAliveAfterWait':True,'windowObserved':True,'rootAppWindowObserved':True,'startupContext':'visible-app-or-child-window',
 'childProcessCount':0,'childVisibleWindowCount':0,'preexistingHtkkProcessCount':0,'loginReady':False,'registrationNonzeroExitCount':0,'registrationUnverifiedExitCount':0,
 'registrationPostFailureCount':0,'registrationAcknowledgementLimitReached':False,'syntheticLoginRequested':True,'nativeDialogCueCounts':{},'uiaHelpersStopped':True,
 'uiaProviderProcessMismatchCount':0,'uiaHelperParseErrorCount':0}
LOGIN_NOT_READY_UIA=(('uia-timeout','helper-timeout'),('scanned','none'),('bounded-partial','none'))
def _login_not_ready(r,mode,permit):
 if r.get('blockedReason')!='SYNTHETIC_LOGIN_NOT_READY' or not _exact(r,LOGIN_NOT_READY_REPORT):return False
 if (r.get('uiaStatus'),r.get('uiaHelperFailureCategory'))not in LOGIN_NOT_READY_UIA or any(type(r.get(k))is not str for k in ('uiaStatus','uiaHelperFailureCategory')):return False
 if type(r.get('appVisibleWindowCount'))is not int or r['appVisibleWindowCount']<1 or type(r.get('startupWaitSeconds'))is not int:return False
 return _pre_login_clean(r,mode,permit)
LOGIN={'fixtureDirectoryPreexisting':False,'fixtureDirectoryCreated':True,'syntheticIdentifierOnly':True,'realTaxpayerDataUsed':False,'inputVerified':True,'loginClicked':True,'loginHidden':True,'runtimeRoundTrip':False}
PERMIT_KEYS={'uniquePathVerified','initiallyAbsent','authorizationAttempted','absentAfterCleanup'}
def classify(jobs,records):
 ready=[j for j in jobs.get('jobs',[])if j.get('name')=='readiness']
 if len(ready)!=1 or ready[0].get('conclusion')!='failure':return None
 if len(jobs.get('jobs',[]))!=2 or not any(j.get('name')=='report_failure'and j.get('conclusion')=='success'for j in jobs['jobs']):return None
 steps=ready[0].get('steps',[]);failed={s.get('name')for s in steps if s.get('conclusion')=='failure'}
 if failed&set(SELFTEST_STEPS):
  return 'windows-selftest-fixture-failed'if _selftest_fixture_failed(ready[0],records)else None
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
  if type(permit)is not dict or set(permit)!=PERMIT_KEYS or not _supplier_boundary(r,(DECLARATION_MODE,)):return None
  if not any(s.get('name')==DECLARATION_RETAIN and s.get('conclusion')=='success'for s in steps):return None
  declared=[x for x in records if x.get('format')==DECLARATION_NOT_STAGED['format']]
  if len(declared)!=1 or not _exact(declared[0],DECLARATION_NOT_STAGED) or set(declared[0])!=set(DECLARATION_NOT_STAGED):return None
  if r.get('blockedReason')=='STARTUP_WINDOW_NOT_OBSERVED':
   if not _no_retained_evidence(steps,DECLARATION_RETAIN,'success')or any(x.get('format')=='htkk-web-native-output-publication-status-v1'for x in records):return None
   return 'startup-window-not-observed'if _startup_window_not_observed(r,DECLARATION_MODE,permit)else None
  if r.get('blockedReason')=='SYNTHETIC_LOGIN_NOT_READY':
   if not _no_retained_evidence(steps,DECLARATION_RETAIN,'success')or any(x.get('format')=='htkk-web-native-output-publication-status-v1'for x in records):return None
   return 'synthetic-login-not-ready'if _login_not_ready(r,DECLARATION_MODE,permit)else None
  if r.get('blockedReason')!='SYNTHETIC_LOGIN_NOT_VERIFIED':
   if not _no_retained_evidence(steps,DECLARATION_RETAIN,'success')or any(x.get('format')=='htkk-web-native-output-publication-status-v1'for x in records):return None
   return 'gui-pre-export-timeout'if _gui_pre_export_branch(r,DECLARATION_MODE,permit,login if type(login)is dict else None)else None
  # Declaration startup flake: HTKK never reached its main window (original-starting), the
  # synthetic login saw no profile window, no permit was issued, nothing was staged.
  if type(login)is not dict:return None
  if r.get('blockedReason')!='SYNTHETIC_LOGIN_NOT_VERIFIED' or r.get('guiReferenceAutomation')is not None:return None
  if not _exact(permit,{'uniquePathVerified':True,'initiallyAbsent':True,'authorizationAttempted':False,'absentAfterCleanup':True}):return None
  if not _exact(login,dict(LOGIN,status='next-window-not-yet-identified',profileWindowObserved=False)):return None
  return 'synthetic-profile-startup-not-observed'
 if failed!={PROBE,RETAIN}:return None
 if type(permit)is not dict or set(permit)!=PERMIT_KEYS or not _supplier_boundary(r):return None
 if any(r.get('blockedReason')==reason for _,reason in ORACLES):
  retained=[x for x in records if x.get('format')=='htkk-web-native-output-publication-status-v1']
  if retained!=[{'format':'htkk-web-native-output-publication-status-v1','status':'rejected','code':'FILES'}]or not _no_retained_evidence(steps,RETAIN,'failure')or _declaration_status(records):return None
  return 'gui-pre-export-timeout'if _gui_pre_export_branch(r,'gtgt-web-import-inspect',permit,None)else None
 if r.get('blockedReason')=='STARTUP_WINDOW_NOT_OBSERVED':
  retained=[x for x in records if x.get('format')=='htkk-web-native-output-publication-status-v1']
  if retained!=[{'format':'htkk-web-native-output-publication-status-v1','status':'rejected','code':'FILES'}]or not _no_retained_evidence(steps,RETAIN,'failure')or _declaration_status(records):return None
  return 'startup-window-not-observed'if _startup_window_not_observed(r,'gtgt-web-import-inspect',permit)else None
 if r.get('blockedReason')=='SYNTHETIC_LOGIN_NOT_READY':
  retained=[x for x in records if x.get('format')=='htkk-web-native-output-publication-status-v1']
  if retained!=[{'format':'htkk-web-native-output-publication-status-v1','status':'rejected','code':'FILES'}]or not _no_retained_evidence(steps,RETAIN,'failure')or _declaration_status(records):return None
  return 'synthetic-login-not-ready'if _login_not_ready(r,'gtgt-web-import-inspect',permit)else None
 if type(login)is not dict:return None
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
  if _no_retained_evidence(steps,RETAIN,'failure')and not _declaration_status(records)and _gui_pre_export_branch(r,'gtgt-web-import-inspect',permit,login):return 'gui-pre-export-timeout'
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
