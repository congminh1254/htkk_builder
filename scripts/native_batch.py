"""Authenticate one immutable input cohort; statuses are discovery hints, not proof."""
import importlib.util,json,os,pathlib,re,time
_spec=importlib.util.spec_from_file_location('batch_evidence_collector',pathlib.Path(__file__).with_name('collect-scoped-evidence.py'));collector=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(collector)
_retry_spec=importlib.util.spec_from_file_location('native_preflight_retry',pathlib.Path(__file__).with_name('native_preflight_retry.py'));preflight=importlib.util.module_from_spec(_retry_spec);_retry_spec.loader.exec_module(preflight)
registry=collector.cases.case_registry
SOURCE=collector.SOURCE;BUILDER=collector.BUILDER

def check(v):
 if not v:raise ValueError('NATIVE_BATCH')

def verify_case(case,source,builder,input_commit,run_id,get=collector.api):
 collector.sha(source);collector.sha(builder);collector.sha(input_commit);check(re.fullmatch('[1-9][0-9]*',str(run_id)))
 run=get(BUILDER,'actions/runs/'+str(run_id))
 if run.get('status')in ('queued','pending','in_progress','waiting','requested'):return None
 collector.validate_run(run,builder,str(run_id))
 jobs=get(BUILDER,'actions/runs/'+str(run_id)+'/attempts/'+str(run['run_attempt'])+'/jobs?per_page=100')
 check(type(jobs.get('jobs'))is list and jobs.get('total_count')==len(jobs['jobs']))
 check(all(j.get('conclusion')in ('success','skipped')for j in jobs['jobs']))
 ready=[j for j in jobs['jobs']if j.get('name')=='readiness'];check(len(ready)==1 and ready[0]['conclusion']=='success')
 records=collector.records(get(BUILDER,'actions/jobs/'+str(ready[0]['id'])+'/logs'))
 reports=[r for r in records if 'guiReferenceAutomation'in r];check(len(reports)==1);gui=collector.validate_report(reports[0],source,case)
 publications=[r for r in records if r.get('format')=='htkk-web-native-output-publication-status-v1'and r.get('status')=='published'and r.get('caseId')==case and r.get('sourceCommit')==source];check(len(publications)==1)
 artifact=collector.sha(publications[0].get('artifactCommit'));retained=json.loads(collector.raw(get,'manifest.json',artifact));p=retained.get('provenance',{})
 check(retained.get('format')=='htkk-web-native-output-reference-v3'and p.get('sourceCommit')==source and p.get('builderCommit')==builder and p.get('runId')==str(run_id)and p.get('runAttempt')==run['run_attempt']and p.get('caseId')==case)
 # A stale callback from a different release cannot qualify the new cohort.
 if retained.get('input',{}).get('artifactCommit')!=input_commit:return None
 check(p.get('originalProcessStopped')is True and p.get('originalSourcesUnmodified')is True)
 check(gui.get('roundtripXmlExactMatched')is True and gui.get('webSigningDateEdited')is True and gui.get('webSigningDateReady')is True and gui.get('webSigningDateLocked')is False and gui.get('webSigningDateCellKind')==4)
 check(retained.get('files',{}).get('01GTGT-initial.xml',{}).get('sha256')==gui.get('exportSha256')and retained.get('files',{}).get('01GTGT-native.xml',{}).get('sha256')==gui.get('roundtripReexportSha256')==publications[0].get('nativeOutputSha256'))
 return {'caseId':case,'runId':str(run_id),'runAttempt':run['run_attempt'],'inputCommit':input_commit,'nativeCommit':artifact}

def discover(publication,builder,statuses,get=collector.api,retry=None):
 source=publication['sourceCommit'];latest={s['context']:s for s in reversed(statuses)};result=[];seen=set();ready=[];pending=False
 for item in publication['cases']:
  case=item['caseId'];check(case in registry.CASES)
  # Candidate cases report their own status but never gate this cohort. A failed candidate
  # gets the same classified, at-most-one, pre-tax-only retry; its outcome (or any error
  # while classifying it) never makes the cohort pending, failed or ready.
  if not registry.CASES[case]['releaseGate']:
   status=latest.get(registry.CASES[case]['statusContext'],{})
   if retry is not None and status.get('state')in ('failure','error')and 'input:'+item['artifactCommit']in status.get('description',''):
    try:retry(status,registry.CASES[case]['statusContext'],source,builder,item['artifactCommit'])
    except Exception:pass
   continue
  status=latest.get(registry.CASES[case]['statusContext'],{})
  if status.get('state')in ('failure','error'):
   if 'input:'+item['artifactCommit']in status.get('description',''):
    if retry is not None and retry(status,registry.CASES[case]['statusContext'],source,builder,item['artifactCommit']):pending=True;continue
    raise ValueError('NATIVE_FAILED')
   pending=True;continue
  if status.get('state')!='success':pending=True;continue
  match=re.fullmatch(r'https://github\.com/congminh1254/htkk_builder/actions/runs/([1-9][0-9]*)',status.get('target_url',''));check(match and match[1]not in seen);seen.add(match[1])
  ready.append((case,item['artifactCommit'],match[1]))
 # Do not repeatedly download completed logs/artifacts while another case is pending.
 if pending:return None
 for _,_,run_id in ready:
  run=get(BUILDER,'actions/runs/'+run_id)
  if run.get('status')in ('queued','pending','in_progress','waiting','requested'):return None
  collector.validate_run(run,builder,run_id)
 for case,input_commit,run_id in ready:
  proof=verify_case(case,source,builder,input_commit,run_id,get)
  if proof is None:return None
  result.append(proof)
 return {'format':'htkk-native-batch-v1','sourceCommit':source,'builderCommit':builder,'cases':result,'qualificationGranted':False}

def verify_pinned(batch,source,builder,get=collector.api):
 check(type(batch)is dict and batch.get('format')=='htkk-native-batch-v1'and batch.get('sourceCommit')==source and batch.get('builderCommit')==builder and batch.get('qualificationGranted')is False)
 cases=batch.get('cases');check(type(cases)is list and [c.get('caseId')for c in cases]==list(registry.GATE_CASES))
 check(len({c.get('runId')for c in cases})==len(cases))
 for proof in cases:check(verify_case(proof['caseId'],source,builder,proof['inputCommit'],proof['runId'],get)==proof)
 return True

def main():
 temp=pathlib.Path(os.environ['RUNNER_TEMP']);publication=collector.cases.publication((temp/'htkk-web-input-publication.json').read_bytes(),os.environ['COMMIT_SHA']);deadline=time.monotonic()+1200
 retried=set();declined=set()
 def retry(status,context,source,builder,artifact):
  # A run already classified as not retryable is not re-read every poll (candidate cases keep
  # their failure status while the gating cohort is awaited).
  key=status.get('target_url','')
  if key in declined:return False
  result=preflight.recover(status,context,source,builder,artifact,collector.api,collector.records,collector.cases.post,os.environ.get('BUILDER_ACTIONS_TOKEN'),os.environ.get('SOURCE_STATUS_TOKEN'),retried)
  if result is False:declined.add(key)
  return result
 while True:
  check(collector.api(SOURCE,'commits/main')['sha']==publication['sourceCommit'])
  statuses=collector.api(SOURCE,'commits/'+publication['sourceCommit']+'/status?per_page=100')['statuses'];batch=discover(publication,os.environ['GITHUB_SHA'],statuses,retry=retry)
  if batch is not None:break
  if time.monotonic()>=deadline:raise ValueError('NATIVE_TIMEOUT')
  print('Waiting for the exact immutable native input cohort.',flush=True);time.sleep(15)
 check(collector.api(SOURCE,'commits/main')['sha']==publication['sourceCommit'])
 with (temp/'htkk-native-batch-verification.json').open('x')as stream:stream.write(json.dumps(batch,separators=(',',':'))+'\n')
 print('Whole native cohort authenticated; qualification remains disabled.')
if __name__=='__main__':
 try:main()
 except Exception:raise SystemExit('Native cohort rejected; private evidence and credentials suppressed.')
