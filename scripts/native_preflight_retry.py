"""One classified retry before tax execution; never retries mismatches or weakens evidence."""
import re
BUILDER='congminh1254/htkk_builder';SOURCE='htkk-net/htkk_web'
FRAMEWORK='Check clean Framework UIA assembly readiness'
PROBE='Kiểm tra nguồn và điều kiện Windows'
RETAIN='Retain verified raw native web reexport privately'
def classify(jobs,records):
 ready=[j for j in jobs.get('jobs',[])if j.get('name')=='readiness']
 if len(ready)!=1 or ready[0].get('conclusion')!='failure':return None
 if len(jobs.get('jobs',[]))!=2 or not any(j.get('name')=='report_failure'and j.get('conclusion')=='success'for j in jobs['jobs']):return None
 steps=ready[0].get('steps',[]);failed={s.get('name')for s in steps if s.get('conclusion')=='failure'}
 if failed=={FRAMEWORK} and any(s.get('name')==PROBE and s.get('conclusion')=='skipped'for s in steps):
  bounds=[r for r in records if r.get('format')=='htkk-framework-uia-boundary-v1']
  if len(bounds)==1 and all(type(bounds[0].get(k))is type(v)and bounds[0].get(k)==v for k,v in {'status':'process-timeout','timedOut':True,'processStopped':True,'exitCode':None,'phase':'complete'}.items()):return 'framework-uia-exit-timeout'
 if failed!={PROBE,RETAIN}:return None
 suppliers=[r for r in records if r.get('version')=='5.8.1'and 'supplierProcessBoundary'in r]
 if len(suppliers)!=1:return None
 r=suppliers[0];login=r.get('syntheticLogin',{});boundary=r.get('supplierProcessBoundary',{})
 permit=r.get('guiAutomationPermitBoundary',{})
 if set(permit)!={'uniquePathVerified','initiallyAbsent','authorizationAttempted','absentAfterCleanup'}or any(type(permit.get(k))is not bool or permit[k]is not v for k,v in {'uniquePathVerified':True,'initiallyAbsent':True,'authorizationAttempted':False,'absentAfterCleanup':True}.items()):return None
 if r.get('guiReferenceAutomationMode')!='gtgt-web-import-inspect':return None
 if r.get('stage')!='blocked'or r.get('blockedReason')!='SYNTHETIC_LOGIN_NOT_VERIFIED'or r.get('guiReferenceAutomation')is not None:return None
 if r.get('referenceHostResult',{}).get('status')!='original-starting':return None
 if any(r.get(k)is not True for k in ('sourceHashesVerified','originalSourcesUnmodified','officialDistributionFilesVerified','msiAuthenticodeValid','nativeHelperJobsStopped','hostOutboundBlocked','originalOutboundBlocked')):return None
 if any(boundary.get(k)is not True for k in ('cleanupVerified','supplierStopped','rootStopped','jobEmpty')):return None
 if r.get('taxDataUsed')is not False or r.get('runtimeRoundTrip')is not False:return None
 expected={'status':'next-window-not-yet-identified','fixtureDirectoryPreexisting':False,'fixtureDirectoryCreated':True,'syntheticIdentifierOnly':True,'realTaxpayerDataUsed':False,'inputVerified':True,'loginClicked':True,'loginHidden':True,'profileWindowObserved':False,'runtimeRoundTrip':False}
 if any(type(login.get(k))is not type(v)or login.get(k)!=v for k,v in expected.items()):return None
 return 'synthetic-profile-startup-not-observed'

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
