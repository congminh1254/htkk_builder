"""Offline contracts only: fabricated API records never qualify a Windows execution."""
import base64,copy,hashlib,importlib.util,json,pathlib,re,tempfile,unittest,urllib.error
ROOT=pathlib.Path(__file__).parent
def load(name,file):
 s=importlib.util.spec_from_file_location(name,ROOT/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
batch=load('native_batch_contract','native_batch.py');refs=load('immutable_ref_contract','immutable_case_refs.py');producer=load('producer_batch_contract','produce_case_batch.py');guard=load('callback_guard_contract','callback_guard.py')
SOURCE='a'*40;BUILDER='b'*40

def fixture():
 runs={};jobs={};reports={};publications={};manifests={};inputs={};statuses=[]
 for index,case in enumerate(batch.registry.CASES):
  rid=100+index;input_id=hashlib.sha1(('input'+case).encode()).hexdigest();native_id=hashlib.sha1(('native'+case).encode()).hexdigest();inputs[case]=input_id
  runs[rid]={'id':rid,'repository':{'full_name':batch.BUILDER},'path':'.github/workflows/probe-htkk-windows.yml','event':'workflow_dispatch','head_branch':'main','head_sha':BUILDER,'run_attempt':1,'status':'completed','conclusion':'success'}
  jobs[rid]={'total_count':2,'jobs':[{'id':rid+1000,'name':'readiness','conclusion':'success'},{'id':rid+2000,'name':'report_failure','conclusion':'skipped'}]}
  oracle=lambda n:{'status':'matched','cases':n,'matched':n,'compilerJobCleanupVerified':True,'oracleJobCleanupVerified':True}
  gui={'webSourceSha':SOURCE,'webCaseId':case,'webTaxLeafCount':70,**{k:True for k in ('gtgtCaseMoneyMatched','webTaxValuesMatched','roundtripReexportSucceeded','exportSchemaPinnedVerified','roundtripXmlExactMatched','webSigningDateEdited','webSigningDateReady')},'webSigningDateLocked':False,'webSigningDateCellKind':4,'exportSha256':'e'*64,'roundtripReexportSha256':'f'*64}
  reports[rid]={'stage':'synthetic-original-gtgt-web-import-inspected',**{k:True for k in ('originalSourcesUnmodified','officialDistributionFilesVerified','nativeHelperJobsStopped','uiaHelpersStopped')},'mirrorUsed':False,'supplierProcessBoundary':{k:True for k in ('cleanupVerified','supplierStopped','rootStopped','jobEmpty')},'taxIdOracle':oracle(30),'profileAliasOracle':oracle(12),'commonHeaderOracle':oracle(43),'guiReferenceAutomation':gui}
  publications[rid]={'format':'htkk-web-native-output-publication-status-v1','status':'published','sourceCommit':SOURCE,'caseId':case,'artifactCommit':native_id,'nativeOutputSha256':'f'*64}
  manifests[native_id]={'format':'htkk-web-native-output-reference-v3','provenance':{'sourceCommit':SOURCE,'builderCommit':BUILDER,'runId':str(rid),'runAttempt':1,'caseId':case,'originalProcessStopped':True,'originalSourcesUnmodified':True},'input':{'artifactCommit':input_id},'files':{'01GTGT-initial.xml':{'sha256':'e'*64},'01GTGT-native.xml':{'sha256':'f'*64}}}
  statuses.append({'context':batch.registry.CASES[case]['statusContext'],'state':'success','target_url':'https://github.com/'+batch.BUILDER+'/actions/runs/'+str(rid)})
 def get(repo,path):
  if path.startswith('contents/manifest.json?ref='):
   value=manifests[path.split('=')[-1]];body=json.dumps(value).encode();return {'type':'file','path':'manifest.json','encoding':'base64','content':base64.b64encode(body).decode(),'size':len(body),'sha':hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest()}
  m=re.fullmatch(r'actions/runs/(\d+)',path)
  if m:return runs[int(m[1])]
  m=re.fullmatch(r'actions/runs/(\d+)/attempts/1/jobs\?per_page=100',path)
  if m:return jobs[int(m[1])]
  m=re.fullmatch(r'actions/jobs/(\d+)/logs',path)
  if m:
   rid=int(m[1])-1000;return json.dumps(reports[rid])+'\n'+json.dumps(publications[rid])
  raise AssertionError('Unexpected test API path')
 publication={'sourceCommit':SOURCE,'cases':[{'caseId':c,'artifactCommit':v}for c,v in inputs.items()]}
 return {'get':get,'runs':runs,'jobs':jobs,'reports':reports,'manifests':manifests,'statuses':statuses,'publication':publication}

class NativeCohortTests(unittest.TestCase):
 def test_whole_cohort_and_pinned_revalidation_ignore_mutable_status_after_discovery(self):
  f=fixture();proof=batch.discover(f['publication'],BUILDER,f['statuses'],f['get']);self.assertEqual(len(proof['cases']),13);self.assertFalse(proof['qualificationGranted']);self.assertTrue(batch.verify_pinned(proof,SOURCE,BUILDER,f['get']))
 def test_pending_and_other_release_inputs_never_qualify_new_cohort(self):
  f=fixture();f['statuses'][0]['state']='pending';self.assertIsNone(batch.discover(f['publication'],BUILDER,f['statuses'],f['get']))
  f=fixture();f['publication']['cases'][0]['artifactCommit']='0'*40;self.assertIsNone(batch.discover(f['publication'],BUILDER,f['statuses'],f['get']))
 def test_stale_failure_is_not_current_failure(self):
  f=fixture();f['statuses'][0].update(state='failure',description='old input:'+'0'*40);self.assertIsNone(batch.discover(f['publication'],BUILDER,f['statuses'],f['get']))
  f['statuses'][0]['description']='failed input:'+f['publication']['cases'][0]['artifactCommit']
  with self.assertRaises(ValueError):batch.discover(f['publication'],BUILDER,f['statuses'],f['get'])
 def test_wrong_case_failed_poststeps_attempt_cleanup_and_borrowed_run_reject(self):
  for kind in ('case','failed-run','poststeps','attempt','cleanup','borrowed','date'):
   f=fixture()
   if kind=='case':f['reports'][100]['guiReferenceAutomation']['webCaseId']='other'
   if kind=='failed-run':f['runs'][100]['conclusion']='failure'
   if kind=='poststeps':f['jobs'][100]['jobs'][0]['conclusion']='failure'
   if kind=='attempt':f['runs'][100]['run_attempt']=2
   if kind=='cleanup':f['reports'][100]['supplierProcessBoundary']['jobEmpty']=False
   if kind=='borrowed':f['statuses'][1]['target_url']=f['statuses'][0]['target_url']
   if kind=='date':f['reports'][100]['guiReferenceAutomation']['webSigningDateReady']=False
   with self.subTest(kind=kind),self.assertRaises((ValueError,AssertionError)):batch.discover(f['publication'],BUILDER,f['statuses'],f['get'])

class ImmutableRefTests(unittest.TestCase):
 def test_get404_only_creates_and_existing_correct_ref_is_idempotent(self):
  calls=[];saved={}
  def api(path,token,payload=None):
   calls.append((path,payload))
   if payload:saved['value']={'ref':payload['ref'],'object':{'type':'commit','sha':payload['sha']}};return saved['value']
   if not saved:raise urllib.error.HTTPError('https://api.github.com',404,'test',{},None)
   return saved['value']
  first=refs.retain(api,'fake','input',SOURCE,'case','c'*40);self.assertEqual(refs.retain(api,'fake','input',SOURCE,'case','c'*40),first);self.assertEqual(sum(p is not None for _,p in calls),1)
 def test_auth422_and_other_errors_never_fall_back_to_create(self):
  for status in (401,403,422,500):
   calls=[]
   def api(path,token,payload=None):calls.append(payload);raise urllib.error.HTTPError('https://api.github.com',status,'private response',{},None)
   with self.assertRaises(urllib.error.HTTPError):refs.retain(api,'fake','output',SOURCE,'case','c'*40)
   self.assertEqual(calls,[None])

class ProducerAndCallbackTests(unittest.TestCase):
 def test_children_receive_no_source_actions_or_relay_credentials(self):
  environment={'PATH':'bin','HOME':'test','GH_TOKEN':'fake','SOURCE_READ_TOKEN':'fake','AGENT_AUTH_TOKEN':'fake','ACTIONS_RUNTIME_TOKEN':'fake','NODE_OPTIONS':'unsafe'}
  self.assertEqual(producer.child_environment(environment),{'PATH':'bin','HOME':'test'})
  with tempfile.TemporaryDirectory()as temp:
   source=pathlib.Path(temp)/'source';source.mkdir();calls=[]
   def execute(command,**kw):calls.append((command,kw['env']));return type('Result',(),{'returncode':0})()
   self.assertEqual(producer.produce(source,temp,environment,pathlib.Path(temp)/'log',execute),13)
   self.assertTrue(all(set(env)<=set(producer.ALLOWED_ENV)for _,env in calls));self.assertTrue(all(cmd[1]=='scripts/generate-htkk-web-reference.mjs'for cmd,_ in calls))
 def test_superseded_source_attempt_newer_run_or_queued_input_are_ignored(self):
  def get(repo,path,token):
   if path=='commits/main':return {'sha':SOURCE}
   if path=='actions/runs/100':return {'run_attempt':2}
   return [{'context':'htkk-native/zero','state':'success','target_url':'https://github.com/'+batch.BUILDER+'/actions/runs/101'}]
  self.assertFalse(guard.allowed('0'*40,'htkk-native/zero','100','2','fake','fake',get))
  self.assertFalse(guard.allowed(SOURCE,'htkk-native/zero','100','1','fake','fake',get))
  self.assertFalse(guard.allowed(SOURCE,'htkk-native/zero','100','2','fake','fake',get))

class InputContextTests(unittest.TestCase):
 def test_each_input_has_source_case_request_context_and_append_only_anchor(self):
  fixtures=load('caseflow_input_fixture','test_htkk_web_input_publisher.py');publisher=fixtures.p;base,calls,_=fixtures.fake_api();contexts=[];refs_created=[]
  def api(path,token,payload=None,method=None):
   if path.startswith('/git/ref/tags/'):raise urllib.error.HTTPError('https://api.github.com',404,'test',{},None)
   if path=='/git/blobs':
    body=base64.b64decode(payload['content'])
    if body.startswith(b'{'):
     value=json.loads(body)
     if value.get('format')=='htkk-case-context-v1':contexts.append(value)
   if path=='/git/refs'and payload['ref'].startswith('refs/tags/'):refs_created.append(payload)
   return base(path,token,payload,method)
  result=publisher.publish(fixtures.fixtures(),fixtures.SHA,'fake',api,request_id='1234',retain_immutable=True)
  self.assertEqual(len(result['cases']),13);self.assertEqual(len(contexts),13);self.assertEqual(len(refs_created),13)
  for ctx in contexts:self.assertEqual(ctx['sourceCommit'],fixtures.SHA);self.assertEqual(ctx['requestId'],'1234');self.assertEqual(ctx['unit'],batch.registry.CASES[ctx['caseId']]['unit'])
 def test_mixed_profile_plan_is_rejected_before_authenticated_io(self):
  fixtures=load('caseflow_input_bad_plan','test_htkk_web_input_publisher.py');publisher=fixtures.p
  plan={'format':'htkk-case-plan-v1','htkkVersion':'5.8.1','nativeQualified':False,'filingEnabled':False,'nativeCases':[]}
  calls=[]
  with self.assertRaises(ValueError):publisher.publish(fixtures.fixtures(),fixtures.SHA,'fake',lambda *args:calls.append(args),plan=plan)
  self.assertEqual(calls,[])
 def test_queued_new_input_prevents_old_callback_from_overwriting_status_hint(self):
  def get(repo,path,token):
   if path=='commits/main':return {'sha':SOURCE}
   if path=='actions/runs/100':return {'run_attempt':1}
   return [{'context':'htkk-native/zero','state':'pending','description':'queued input:'+'c'*40}]
  self.assertFalse(guard.allowed(SOURCE,'htkk-native/zero','100','1','fake','fake',get,input_commit='d'*40))
  self.assertTrue(guard.allowed(SOURCE,'htkk-native/zero','100','1','fake','fake',get,input_commit='c'*40))

class PlanBindingTests(unittest.TestCase):
 def test_source_plan_blob_is_bound_before_any_ref_mutation(self):
  fixtures=load('plan_binding_fixtures','test_htkk_web_input_publisher.py');publisher=fixtures.p
  rows=[]
  for case,c in batch.registry.CASES.items():
   a=batch.registry.ADAPTERS[c['adapterId']];rows.append({**{k:c[k]for k in ('adapterId','producerCase','unit')},'caseId':case,'producer':a['producer'],'profilePolicy':a['profilePolicy'],'coverageGranted':False,'descriptorFingerprint':'a'*64})
  plan={'format':'htkk-case-plan-v1','htkkVersion':'5.8.1','nativeQualified':False,'filingEnabled':False,'nativeCases':rows}
  for mismatch in (False,True):
   base,calls,_=fixtures.fake_api();contexts=[];remote=copy.deepcopy(plan)
   if mismatch:remote['nativeCases'][0]['descriptorFingerprint']='b'*64
   raw=json.dumps(remote).encode()
   def api(path,token,payload=None,method=None):
    if path.startswith('/contents/data/htkk-case-plan.json?ref='):return fixtures.contents(raw,'htkk-case-plan.json','data/htkk-case-plan.json')
    if path=='/git/blobs':
     value=json.loads(base64.b64decode(payload['content']))if base64.b64decode(payload['content']).startswith(b'{')else {}
     if value.get('format')=='htkk-case-context-v1':contexts.append(value)
    return base(path,token,payload,method)
   if mismatch:
    with self.assertRaises(publisher.PublicationError):publisher.publish(fixtures.fixtures(),fixtures.SHA,'fake',api,request_id='1234',plan=plan)
    self.assertFalse(any(path.startswith('/git/refs')for path,_,_,_ in calls))
   else:
    publisher.publish(fixtures.fixtures(),fixtures.SHA,'fake',api,request_id='1234',plan=plan)
    self.assertEqual(len(contexts),13);self.assertTrue(all(c['planSha256']==hashlib.sha256(raw).hexdigest()for c in contexts))
