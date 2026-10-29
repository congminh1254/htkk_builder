"""Authenticate one immutable input cohort; statuses are discovery hints, not proof."""
import importlib.util,json,os,pathlib,re,time
_spec=importlib.util.spec_from_file_location('batch_evidence_collector',pathlib.Path(__file__).with_name('collect-scoped-evidence.py'));collector=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(collector)
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

def discover(publication,builder,statuses,get=collector.api):
 source=publication['sourceCommit'];latest={s['context']:s for s in reversed(statuses)};result=[];seen=set()
 for item in publication['cases']:
  case=item['caseId'];check(case in registry.CASES);status=latest.get(registry.CASES[case]['statusContext'],{})
  if status.get('state')in ('failure','error'):
   if 'input:'+item['artifactCommit']in status.get('description',''):raise ValueError('NATIVE_FAILED')
   return None
  if status.get('state')!='success':return None
  match=re.fullmatch(r'https://github\.com/congminh1254/htkk_builder/actions/runs/([1-9][0-9]*)',status.get('target_url',''));check(match and match[1]not in seen);seen.add(match[1])
  proof=verify_case(case,source,builder,item['artifactCommit'],match[1],get)
  if proof is None:return None
  result.append(proof)
 return {'format':'htkk-native-batch-v1','sourceCommit':source,'builderCommit':builder,'cases':result,'qualificationGranted':False}

def verify_pinned(batch,source,builder,get=collector.api):
 check(type(batch)is dict and batch.get('format')=='htkk-native-batch-v1'and batch.get('sourceCommit')==source and batch.get('builderCommit')==builder and batch.get('qualificationGranted')is False)
 cases=batch.get('cases');check(type(cases)is list and [c.get('caseId')for c in cases]==list(registry.CASES))
 check(len({c.get('runId')for c in cases})==len(cases))
 for proof in cases:check(verify_case(proof['caseId'],source,builder,proof['inputCommit'],proof['runId'],get)==proof)
 return True

def main():
 temp=pathlib.Path(os.environ['RUNNER_TEMP']);publication=collector.cases.publication((temp/'htkk-web-input-publication.json').read_bytes(),os.environ['COMMIT_SHA']);deadline=time.monotonic()+1200
 while True:
  check(collector.api(SOURCE,'commits/main')['sha']==publication['sourceCommit'])
  statuses=collector.api(SOURCE,'commits/'+publication['sourceCommit']+'/status?per_page=100')['statuses'];batch=discover(publication,os.environ['GITHUB_SHA'],statuses)
  if batch is not None:break
  if time.monotonic()>=deadline:raise ValueError('NATIVE_TIMEOUT')
  print('Waiting for the exact immutable native input cohort.',flush=True);time.sleep(15)
 check(collector.api(SOURCE,'commits/main')['sha']==publication['sourceCommit'])
 with (temp/'htkk-native-batch-verification.json').open('x')as stream:stream.write(json.dumps(batch,separators=(',',':'))+'\n')
 print('Whole native cohort authenticated; qualification remains disabled.')
if __name__=='__main__':
 try:main()
 except Exception:raise SystemExit('Native cohort rejected; private evidence and credentials suppressed.')
