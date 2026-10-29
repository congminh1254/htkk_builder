"""Trusted private fixed-case collection. Never execute private code or print API data."""
import base64,hashlib,importlib.util,json,os,pathlib,re,shutil,urllib.request,urllib.error,urllib.parse
SOURCE='htkk-net/htkk_web';BUILDER='congminh1254/htkk_builder'
_spec=importlib.util.spec_from_file_location('dispatch_cases',pathlib.Path(__file__).with_name('dispatch-native-cases.py'))
cases=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(cases)
_spec=importlib.util.spec_from_file_location('native_retention',pathlib.Path(__file__).with_name('publish-htkk-web-native-output.py'))
retention=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(retention)
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args):return None
def check(value):
 if not value:raise ValueError('EVIDENCE_REJECTED')
def sha(value):check(isinstance(value,str) and re.fullmatch('[a-f0-9]{40}',value));return value
def api(repo,path):
 check(repo in (SOURCE,BUILDER) and isinstance(path,str) and re.fullmatch(r'[A-Za-z0-9_./?=&%-]+',path) and '..' not in path)
 token=(os.environ.get('SOURCE_READ_TOKEN') or os.environ['GH_TOKEN']) if repo==SOURCE else os.environ['GH_TOKEN']
 req=urllib.request.Request('https://api.github.com/repos/'+repo+'/'+path,headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','User-Agent':'HTKK-Scoped-Evidence/1.0'})
 try:response=urllib.request.build_opener(NoRedirect()).open(req,timeout=30)
 except urllib.error.HTTPError as error:
  if error.code!=302 or not path.endswith('/logs'):raise
  url=error.headers.get('Location','');parsed=urllib.parse.urlsplit(url)
  check(parsed.scheme=='https' and parsed.hostname and any(parsed.hostname.endswith(s) for s in ('.blob.core.windows.net','.actions.githubusercontent.com','.githubusercontent.com')) and not parsed.username and not parsed.password)
  response=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'HTKK-Scoped-Evidence/1.0'}),timeout=30)
 with response:
  body=response.read(2_000_001);check(len(body)<=2_000_000)
  return body.decode('utf-8') if path.endswith('/logs') else json.loads(body)
def raw(get,path,commit):
 sha(commit);value=get(SOURCE,'contents/'+path+'?ref='+commit)
 check(value.get('type')=='file' and value.get('encoding')=='base64' and isinstance(value.get('content'),str))
 body=base64.b64decode(''.join(value['content'].split()),validate=True)
 check(len(body)==value.get('size') and len(body)<=2_000_000 and hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest()==value.get('sha'))
 return body
def records(log):
 check(isinstance(log,str) and len(log)<=2_000_000)
 text='\n'.join(re.sub(r'^\d{4}-\d\d-\d\dT\S+\s','',line) for line in log.splitlines());decoder=json.JSONDecoder();offset=0;result=[]
 while True:
  start=text.find('{',offset)
  if start<0:return result
  try:value,end=decoder.raw_decode(text,start);offset=end
  except ValueError:offset=start+1;continue
  if isinstance(value,dict):result.append(value)
def validate_run(run,source_builder,run_id):
 check(run.get('id')==int(run_id) and run.get('repository',{}).get('full_name')==BUILDER and run.get('path')=='.github/workflows/probe-htkk-windows.yml' and run.get('event')=='workflow_dispatch' and run.get('head_branch')=='main' and run.get('head_sha')==source_builder and type(run.get('run_attempt')) is int and run['run_attempt']>=1 and run.get('status')=='completed' and run.get('conclusion')=='success')
def validate_report(report,source,case):
 check(report.get('stage')=='synthetic-original-gtgt-web-import-inspected' and report.get('originalSourcesUnmodified') is True and report.get('officialDistributionFilesVerified') is True and report.get('mirrorUsed') is False and report.get('nativeHelperJobsStopped') is True and report.get('uiaHelpersStopped') is True)
 boundary=report.get('supplierProcessBoundary',{});check(all(boundary.get(k) is True for k in ('cleanupVerified','supplierStopped','rootStopped','jobEmpty')))
 for name,count in (('taxIdOracle',30),('profileAliasOracle',12),('commonHeaderOracle',43)):
  oracle=report.get(name,{});check(oracle.get('status')=='matched' and oracle.get('cases')==oracle.get('matched')==count and oracle.get('compilerJobCleanupVerified') is True and oracle.get('oracleJobCleanupVerified') is True)
 gui=report.get('guiReferenceAutomation',{});check(gui.get('webSourceSha')==source and gui.get('webCaseId')==case and gui.get('webTaxLeafCount')==70)
 check(all(gui.get(k) is True for k in ('gtgtCaseMoneyMatched','webTaxValuesMatched','roundtripReexportSucceeded','exportSchemaPinnedVerified')))
 return gui
def collect(source,builder,directory,get=api,progress=lambda done,total:None):
 sha(source);sha(builder);directory=pathlib.Path(directory);directory.mkdir(mode=0o700)
 complete=False
 try:
  statuses=get(SOURCE,'commits/'+source+'/status?per_page=100');check(isinstance(statuses.get('statuses'),list))
  latest={s['context']:s for s in reversed(statuses['statuses'])}
  producer=raw(get,'scripts/generate-htkk-web-reference.mjs',source);producer_sha=hashlib.sha256(producer).hexdigest()
  index={'format':'htkk-native-evidence-bundle-v1','sourceCommit':source,'builderCommit':builder,'cases':[],'nativeQualified':False,'filingEnabled':False}
  for case in cases.CASES:
   status=latest.get(cases.CONTEXTS[case],{});check(status.get('state')=='success')
   match=re.fullmatch(r'https://github\.com/congminh1254/htkk_builder/actions/runs/([1-9][0-9]*)',status.get('target_url',''));check(match);run_id=match[1]
   run=get(BUILDER,'actions/runs/'+run_id);validate_run(run,builder,run_id)
   jobs=get(BUILDER,'actions/runs/'+run_id+'/attempts/'+str(run['run_attempt'])+'/jobs?per_page=100')
   check(type(jobs.get('jobs')) is list and jobs.get('total_count')==len(jobs['jobs']) and len(jobs['jobs'])<100)
   ready=[j for j in jobs['jobs'] if j.get('name')=='readiness'];check(len(ready)==1 and ready[0].get('conclusion')=='success' and all(j.get('name')=='readiness' or j.get('conclusion')=='skipped' for j in jobs['jobs']))
   job=ready[0]
   for name in ('Retain verified raw native web reexport privately','Report fixed native-case status privately'):check(any(s.get('name')==name and s.get('conclusion')=='success' for s in job.get('steps',[])))
   docs=records(get(BUILDER,'actions/jobs/'+str(job['id'])+'/logs'))
   reports=[d for d in docs if d.get('guiReferenceAutomation',{}).get('webCaseId')==case and d.get('guiReferenceAutomation',{}).get('webSourceSha')==source];check(len(reports)==1);report=reports[0];gui=validate_report(report,source,case)
   publications=[d for d in docs if d.get('format')=='htkk-web-native-output-publication-status-v1' and d.get('status')=='published' and d.get('caseId')==case and d.get('sourceCommit')==source];check(len(publications)==1)
   commit=sha(publications[0].get('artifactCommit'));retained_bytes=raw(get,'manifest.json',commit);metadata=json.loads(retained_bytes);p=metadata.get('provenance',{});input_commit=sha(metadata.get('input',{}).get('artifactCommit'))
   check(metadata.get('format') in ('htkk-web-native-output-reference-v2','htkk-web-native-output-reference-v3') and p.get('sourceCommit')==source and p.get('builderCommit')==builder and p.get('runId')==run_id and p.get('runAttempt')==run['run_attempt'] and p.get('caseId')==case)
   initial=raw(get,'01GTGT-initial.xml',commit);native=raw(get,'01GTGT-native.xml',commit);web=raw(get,'01GTGT-web.xml',input_commit);input_bytes=raw(get,'manifest.json',input_commit);input_manifest=retention.reader.validate_manifest(input_bytes)
   aligned=metadata['format']=='htkk-web-native-output-reference-v3'
   if aligned:check(gui.get('webSigningDateReady') is True and gui.get('webSigningDateEdited') is True and gui.get('webSigningDateLocked') is False and gui.get('webSigningDateCellKind') in (1,2,3) and gui.get('roundtripXmlExactMatched') is True)
   retention.validate_provenance(json.dumps(p).encode(),native,run_id,builder,source,case,input_commit,initial,str(run['run_attempt']),aligned=aligned)
   # Recheck fixed synthetic privacy using the authenticated run's capture date, not today's date.
   import datetime
   captured=datetime.date.fromisoformat(run['created_at'][:10]);retention.validate_native(initial,case,captured,initial=True,aligned=aligned);retention.validate_native(native,case,captured);retention.compare_tax(web,native)
   if aligned:check(retention.compare_native_roundtrip(initial,native)['allLeafValuesMatched'] is True)
   check(input_manifest['sourceCommit']==source and input_manifest['caseId']==case and input_manifest['producerSha256']==producer_sha==metadata['input']['producerSha256'] and input_manifest['xmlSha256']==hashlib.sha256(web).hexdigest()==p['webImportInputSha256'])
   check(hashlib.sha256(initial).hexdigest()==gui['exportSha256']==metadata['files']['01GTGT-initial.xml']['sha256'] and hashlib.sha256(native).hexdigest()==gui['roundtripReexportSha256']==publications[0]['nativeOutputSha256']==metadata['files']['01GTGT-native.xml']['sha256'])
   files={'retained.json':retained_bytes,'input-manifest.json':input_bytes,'initial.xml':initial,'native.xml':native,'web.xml':web,'producer.mjs':producer,'gui-report.json':json.dumps(report).encode(),'run.json':json.dumps(run).encode()}
   def artifact(name):return {'path':case+'/'+name,'sha256':hashlib.sha256(files[name]).hexdigest()}
   provenance={'sourceCommit':source,'builderCommit':builder,'builderRepository':BUILDER,'runId':run_id,'runAttempt':run['run_attempt'],'runtimeHost':'clr2-x86-reference','inputsSynthetic':True,'genuineExecution':True}
   item={'caseId':case,'provenance':provenance,'retention':{'caseId':case,'nativeCommit':commit,'inputCommit':input_commit},'input':artifact('web.xml'),'htkkOutput':artifact('initial.xml'),'webOutput':artifact('web.xml'),'reexport':artifact('native.xml'),'producer':artifact('producer.mjs'),'retained':artifact('retained.json'),'inputManifest':artifact('input-manifest.json'),'auditArtifacts':[artifact('gui-report.json'),artifact('run.json')]}
   folder=directory/case;folder.mkdir(mode=0o700)
   for name,body in files.items():
    with (folder/name).open('xb') as out:out.write(body)
   index['cases'].append(item);progress(len(index['cases']),len(cases.CASES))
  with (directory/'bundle.json').open('x') as out:json.dump(index,out)
  complete=True;return index
 finally:
  if not complete:shutil.rmtree(directory)
if __name__=='__main__':
 try:
  check(os.environ.get('GITHUB_REPOSITORY')==BUILDER and os.environ.get('GITHUB_REF')=='refs/heads/main')
  index=collect(os.environ['EVIDENCE_SOURCE_SHA'],os.environ['NATIVE_BUILDER_SHA'],pathlib.Path(os.environ['RUNNER_TEMP'])/'htkk-scoped-evidence')
  print('Collected '+str(len(index['cases']))+' authenticated fixed cases privately; qualification unchanged.')
 except Exception:raise SystemExit('Evidence collection failed; API data, paths, XML and credentials suppressed.')
