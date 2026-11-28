"""Counted GitHub REST requests one release makes against the private web repository.

Real publisher, reader, dispatcher, callback-guard and cohort code runs against offline fakes; every request
to the web repository is counted per stage, and the whole release must stay under REQUEST_BUDGET on one token.
Also the contracts the lower count rests on: one verified cohort commit, one verified commit archive per read,
the fetch-once digest, create-first append-only tags and the combined-status guard.
"""
import contextlib,datetime,hashlib,importlib.util,io,json,math,os,pathlib,subprocess,tarfile,tempfile,unittest,urllib.error
from unittest.mock import patch
from sandbox_test_support import Sandbox

ROOT=pathlib.Path(__file__).resolve().parent
def load(name,file):
 spec=importlib.util.spec_from_file_location(name,ROOT/file);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
fx=load('budget_publisher_fixtures','test_htkk_web_input_publisher.py');p=fx.p;reader=p.reader;gits=fx.gits;registry=reader.case_registry
web_t=load('budget_web_native','test_htkk_web_native_output.py')
khbs_t=load('budget_khbs_native','test_khbs_native_case.py')
decl_t=load('budget_declaration_native','test_declaration_native_cases.py')
d=load('budget_dispatch','dispatch-native-cases.py')
guard=load('budget_guard','callback_guard.py')
batch=load('budget_batch','native_batch.py')
TOKEN='synthetic-token';SOURCE=fx.SHA;REQUEST='4242'
REQUEST_BUDGET=3000 # One release on one token: 60% of GitHub's 5000-per-hour primary limit, leaving room for retries and other jobs. About 15 requests per case; cut requests per case before raising this again.
def http_error(code):return urllib.error.HTTPError('https://api.github.com/',code,'SECRET PRIVATE REMOTE BODY',{},None)

def source_plan():
 rows=[]
 for case,c in registry.CASES.items():
  a=registry.ADAPTERS[c['adapterId']];rows.append({**{k:c[k] for k in ('adapterId','producerCase','unit')},'caseId':case,'producer':a['producer'],'profilePolicy':a['profilePolicy'],'coverageGranted':False,'descriptorFingerprint':'a'*64})
 return {'format':'htkk-case-plan-v1','htkkVersion':'5.8.1','nativeQualified':False,'filingEnabled':False,'nativeCases':rows}
_RELEASE=None
def release():
 """The input publication of one release (with its plan and immutable anchor), recorded once."""
 global _RELEASE
 if _RELEASE is None:
  base,calls,commits=fx.fake_api();plan=source_plan();raw=json.dumps(plan).encode()
  def api(path,token,payload=None,method=None):
   if path.startswith('/contents/data/htkk-case-plan.json?ref='):calls.append((path,token,payload,method));return fx.contents(raw,'htkk-case-plan.json','data/htkk-case-plan.json')
   # The cohort's append-only tag is absent until created (only an explicit GET 404 permits creating it).
   if path.startswith('/git/ref/tags/'):calls.append((path,token,payload,method));raise http_error(404)
   return base(path,token,payload,method)
  result=p.publish(fx.fixtures(),SOURCE,TOKEN,api,request_id=REQUEST,plan=plan,retain_immutable=True)
  tree=base.git.trees[commits[0]['tree']];artifact=result['cases'][0]['artifactCommit']
  _RELEASE=(result,list(calls),tree,artifact,gits.tarball(artifact,tree))
 return _RELEASE

def fetch_case(case,archive_body=None,commit_tree=None):
 """The native job's fetch of one case from the published cohort; returns (files, requests)."""
 result,_,tree,artifact,body=release();requests=[]
 def get(path,token):
  requests.append(path)
  if path=='/git/commits/'+artifact:return {'sha':artifact,'tree':{'sha':commit_tree or gits.tree_id(tree)}}
  if path=='/git/commits/'+SOURCE:return {'sha':SOURCE}
  raise AssertionError('Unexpected fixed API path')
 def archive(commit,token):requests.append('tarball/'+commit);return archive_body or body
 files=reader.download(TOKEN,fetch=get,archive=archive,expected_source=SOURCE,expected_case=case,artifact_commit=artifact,context={'requestId':REQUEST,'planSha256':result['planSha256']},check_private=False,check_source=False)
 return files,requests

def retaining(fetch,source,calls):
 """A publisher fake plus the main ref and the append-only tag (absent until created); every request is recorded."""
 def api(path,token,payload=None,method=None):
  if path=='/git/ref/heads/main' or path.startswith('/git/ref/tags/') or (path=='/git/refs' and payload['ref'].startswith('refs/tags/')):calls.append((path,token,payload,method))
  if path.startswith('/git/ref/tags/'):raise urllib.error.HTTPError('https://api.github.com/',404,'SECRET',{},None)
  if path=='/git/ref/heads/main':return {'ref':'refs/heads/main','object':{'type':'commit','sha':source}}
  if path=='/git/refs' and payload['ref'].startswith('refs/tags/'):return {'ref':payload['ref'],'object':{'type':'commit','sha':payload['sha']}}
  return fetch(path,token,payload,method)
 return api

def publications():
 """One retained output per publisher used by a release: (publisher module, native, provenance, inputs, fake, today)."""
 web,native,manifest,provenance=web_t.fixture();inputs={'01GTGT-web.xml':web,'manifest.json':json.dumps(manifest,ensure_ascii=False).encode()}
 fetch,calls=web_t.fake_api(web,manifest);yield web_t.n,native,provenance,inputs,fetch,calls,web_t.TODAY,web_t.n.oracle.DEFAULT
 case=khbs_t.CASE;web=khbs_t.f.sale_fixture(case);manifest=khbs_t.f.case_manifest(web,case);native=khbs_t.native_of(web)
 inputs={reader.xml_name(case):web,'manifest.json':json.dumps(manifest,ensure_ascii=False).encode()}
 fetch,calls=khbs_t.NativeOutput.fake_api(None,web,manifest);yield khbs_t.out,native,khbs_t.NativeOutput.provenance(None,web,native,case),inputs,fetch,calls,khbs_t.TODAY,'5.8.2'
 case=decl_t.CASES[0];web=decl_t.dfx.declaration_fixture(case);manifest=decl_t.dfx.declaration_manifest(web,case,source=decl_t.SOURCE);native=decl_t.export_day_of(decl_t.native_of(web,case),case)
 inputs={reader.xml_name(case):web,'manifest.json':json.dumps(manifest,ensure_ascii=False).encode()}
 fetch,calls=decl_t.NativeOutput.fake_api(None,web,manifest);yield decl_t.out,native,decl_t.NativeOutput.provenance(None,web,native,case),inputs,fetch,calls,decl_t.TODAY,decl_t.out.oracle.DEFAULT

def combined(contexts,per_page=100):
 """A combined-status reader over these contexts; records every page read."""
 pages=[]
 def get(repo,path,token=None):
  if path=='git/ref/heads/main':pages.append(path);return {'object':{'sha':SOURCE}}
  if path.startswith('actions/runs/'):return {'run_attempt':1}
  page=int(path.rsplit('page=',1)[1]);pages.append(path)
  return {'statuses':contexts[(page-1)*per_page:page*per_page],'total_count':len(contexts)}
 return get,pages

class GitIds(unittest.TestCase):
 def test_local_git_ids_match_git(self):
  # Ids computed by git itself (git init; git add; git rev-parse HEAD^{tree} and HEAD:a-b), including a
  # directory sorting before a same-named file ('c' versus 'c.txt') and CRLF/UTF-8 bytes.
  files={'a-b/m.json':b'x\r\n\xc3\xa9','a-b/z.xml':b'y','c/case-context.json':b'q','c.txt':b'w'}
  self.assertEqual(reader.files_tree_sha(files),'72a17234538d403bd298a26b2e8004fd29f1bc36')
  self.assertEqual(p.flat_tree_sha({'m.json':b'x\r\n\xc3\xa9','z.xml':b'y'}),'ab92eda19940b1f9e03f3d11fde332c8ad07a382')
  self.assertEqual(gits.tree_id(files),'72a17234538d403bd298a26b2e8004fd29f1bc36')
  box=Sandbox.for_test(self);directory=box.root/'repo';directory.mkdir()
  try:
   for path,body in files.items():(directory/path).parent.mkdir(parents=True,exist_ok=True);(directory/path).write_bytes(body)
   def git(*args):
    command=['git','-c','core.autocrlf=false',*args];box.check_git(command,cwd=directory)
    return subprocess.run(command,cwd=directory,check=True,capture_output=True,text=True).stdout.strip()
   git('init','-q');git('add','-A');tree=git('write-tree')
  except (OSError,subprocess.CalledProcessError):self.skipTest('git unavailable')
  self.assertEqual(tree,reader.files_tree_sha(files))

class CohortRoundTrip(unittest.TestCase):
 def test_every_case_is_read_back_from_the_one_cohort_with_its_context(self):
  result,_,tree,artifact,_=release()
  self.assertEqual({c['artifactCommit'] for c in result['cases']},{artifact})
  for case,_,files,_ in fx.fixtures():
   with self.subTest(case=case):
    read,requests=fetch_case(case)
    self.assertEqual(read,files);self.assertEqual(requests,['/git/commits/'+artifact,'tarball/'+artifact])
 def test_archive_must_be_the_pinned_commit_byte_for_byte(self):
  result,_,tree,artifact,body=release();case=fx.fixtures()[0][0]
  wrong_commit=gits.tarball(('e' if artifact[0]!='e' else 'f')*40,tree)
  altered=dict(tree);name=case+'/manifest.json';altered[name]=altered[name]+b' '
  for archive_body,commit_tree,code in ((wrong_commit,None,'SOURCE_COMMIT'),(gits.tarball(artifact,altered),None,'HASH'),(body,'e'*40,'HASH'),
    (gits.tarball(artifact,tree,extra=(('htkk-net-htkk_web-'+artifact[:7]+'/.gitattributes',b'* text=auto'),)),None,'API_SHAPE'),
    (gits.tarball(artifact,tree,extra=(('htkk-net-htkk_web-'+artifact[:7]+'/link',None,tarfile.SYMTYPE),)),None,'API_SHAPE'),
    (gits.tarball(artifact,tree,extra=(('other-root/x',b'x'),)),None,'API_SHAPE'),(b'not an archive',None,'API_SHAPE')):
   with self.subTest(code=code),self.assertRaises(reader.InputError) as error:fetch_case(case,archive_body,commit_tree)
   self.assertEqual(error.exception.code,code)
  executable=io.BytesIO()
  with tarfile.open(fileobj=executable,mode='w:gz',format=tarfile.PAX_FORMAT,pax_headers={'comment':artifact}) as archive:
   for name,body_ in (('r/',None),('r/x',b'x')):
    info=tarfile.TarInfo(name);info.type=tarfile.DIRTYPE if body_ is None else tarfile.REGTYPE;info.mode=0o775
    if body_ is None:archive.addfile(info)
    else:info.size=1;archive.addfile(info,io.BytesIO(body_))
  with self.assertRaises(reader.InputError) as error:reader.archive_tree(executable.getvalue(),artifact,reader.files_tree_sha({'x':b'x'}))
  self.assertEqual(error.exception.code,'API_SHAPE')
 def test_case_directory_must_hold_exactly_its_files_and_context(self):
  result,_,tree,artifact,_=release();case=fx.fixtures()[0][0]
  for change,code in ((lambda t:t.update({case+'/unexpected.xml':b'x'}),'API_SHAPE'),(lambda t:t.pop(case+'/case-context.json'),'CONTEXT_MISSING'),(lambda t:t.pop(case+'/manifest.json'),'API_SHAPE'),(lambda t:t.update({case+'/deeper/x':b'x'}),'API_SHAPE')):
   altered=dict(tree);change(altered)
   with self.subTest(code=code),self.assertRaises(reader.InputError) as error:fetch_case(case,gits.tarball(artifact,altered),gits.tree_id(altered))
   self.assertEqual(error.exception.code,code)
  context=json.loads(tree[case+'/case-context.json']);context['requestId']='1';altered=dict(tree);altered[case+'/case-context.json']=(json.dumps(context,sort_keys=True,separators=(',',':'))+'\n').encode()
  with self.assertRaises(reader.InputError) as error:fetch_case(case,gits.tarball(artifact,altered),gits.tree_id(altered))
  self.assertEqual(error.exception.code,'CONTEXT_REQUEST')
 def test_a_per_case_root_artifact_is_still_read(self):
  case,_,files,_=fx.fixtures()[0];artifact='d'*40;requests=[]
  def get(path,token):
   requests.append(path)
   if path=='/git/commits/'+artifact:return {'sha':artifact,'tree':{'sha':gits.tree_id(files)}}
   if path=='/git/commits/'+SOURCE:return {'sha':SOURCE}
   raise AssertionError('Unexpected fixed API path')
  read=reader.download(TOKEN,fetch=get,archive=lambda commit,token:gits.tarball(artifact,files),expected_source=SOURCE,expected_case=case,artifact_commit=artifact,check_private=False)
  self.assertEqual(read,files)

class ArchiveTransport(unittest.TestCase):
 class Response:
  def __init__(self,status,body=b''):self.status=status;self.body=body
  def read(self,limit=-1):return self.body
  def __enter__(self):return self
  def __exit__(self,*args):return False
 def redirect(self,location):
  return urllib.error.HTTPError('https://api.github.com/x',302,'Found',{'Location':location},io.BytesIO(b''))
 def test_one_api_request_then_an_uncredentialed_codeload_download(self):
  requests=[]
  class Opener:
   def __init__(self,steps):self.steps=steps
   def open(self,request,timeout=None):
    requests.append((request.full_url,request.get_header('Authorization')));step=self.steps.pop(0)
    if isinstance(step,BaseException):raise step
    return step
  steps=[self.redirect('https://codeload.github.com/htkk-net/htkk_web/legacy.tar.gz/'+'d'*40+'?token=SECRET'),self.Response(200,b'archive')]
  with patch.object(reader.urllib.request,'build_opener',return_value=Opener(steps)):self.assertEqual(reader.fetch_archive('d'*40,TOKEN),b'archive')
  self.assertEqual(requests[0],('https://api.github.com/repos/'+reader.REPO+'/tarball/'+'d'*40,'Bearer '+TOKEN))
  self.assertEqual(requests[1][1],None);self.assertTrue(requests[1][0].startswith('https://codeload.github.com/'))
  for location in ('https://evil.example/x','http://codeload.github.com/x','https://user:pw@codeload.github.com/x','https://codeload.github.com:8443/x',''):
   with self.subTest(location=location),patch.object(reader.urllib.request,'build_opener',return_value=Opener([self.redirect(location)])),self.assertRaises(reader.InputError) as error:reader.fetch_archive('d'*40,TOKEN)
   self.assertEqual(error.exception.code,'API_SHAPE')
  with patch.object(reader.urllib.request,'build_opener',return_value=Opener([http_error(403)])),self.assertRaises(urllib.error.HTTPError) as error:reader.fetch_archive('d'*40,TOKEN)
  self.assertEqual(reader.safe_failure(error.exception)['code'],'AUTH')
  with patch.object(reader.urllib.request,'build_opener',return_value=Opener([self.redirect('https://codeload.github.com/x'),self.Response(200,b'x'*(reader.MAX_ARCHIVE+1))])),self.assertRaises(reader.InputError) as error:reader.fetch_archive('d'*40,TOKEN)
  self.assertEqual(error.exception.code,'API_SIZE')

class FetchOnce(unittest.TestCase):
 def staged(self,directory,files):
  folder=pathlib.Path(directory)/p.STAGED_INPUT;folder.mkdir()
  for name,body in files.items():(folder/name).write_bytes(body)
  return folder
 def test_retention_accepts_only_the_staged_files_its_fetch_step_verified(self):
  case,_,files,_=fx.fixtures()[0];artifact='d'*40;digest=reader.input_digest(files,artifact,case)
  with tempfile.TemporaryDirectory() as directory:
   folder=self.staged(directory,files);self.assertEqual(p.staged_inputs(directory,case,artifact,digest,SOURCE),files)
   for other in ('e'*40,):
    with self.assertRaises(p.PublicationError) as error:p.staged_inputs(directory,case,other,digest,SOURCE)
    self.assertEqual(error.exception.code,'HASH')
   name=reader.xml_name(case);(folder/name).write_bytes(files[name]+b' ')
   with self.assertRaises(p.PublicationError) as error:p.staged_inputs(directory,case,artifact,digest,SOURCE)
   self.assertEqual(error.exception.code,'HASH')
   (folder/name).write_bytes(files[name]);(folder/'extra.xml').write_bytes(b'x')
   with self.assertRaises(p.PublicationError) as error:p.staged_inputs(directory,case,artifact,digest,SOURCE)
   self.assertEqual(error.exception.code,'STAGING')
   for bad in ('','0'*63,'z'*64):
    with self.assertRaises(p.PublicationError):p.staged_inputs(directory,case,artifact,bad,SOURCE)
  with patch.dict(os.environ,{'WEB_INPUT_DIGEST':''}):self.assertIsNone(p.job_inputs({'caseId':case,'artifactCommit':artifact,'sourceCommit':SOURCE}))
 def test_fetch_step_writes_the_digest_of_what_it_staged(self):
  case,_,files,_=fx.fixtures()[0];artifact='d'*40
  with tempfile.TemporaryDirectory() as directory:
   output=pathlib.Path(directory)/'output';output.write_text('')
   env={'GITHUB_REPOSITORY':reader.BUILDER,'SOURCE_READ_TOKEN':TOKEN,'EXPECTED_WEB_SOURCE_SHA':SOURCE,'EXPECTED_WEB_CASE_ID':case,'WEB_ARTIFACT_COMMIT':artifact,'EXPECTED_WEB_REQUEST_ID':REQUEST,'EXPECTED_WEB_PLAN_SHA256':'none','RUNNER_TEMP':directory,'GITHUB_OUTPUT':str(output)}
   with patch.dict(os.environ,env,clear=True),patch.object(reader,'download',return_value=files) as download,contextlib.redirect_stdout(io.StringIO()):reader.main()
   self.assertEqual(output.read_text(),'input_digest='+reader.input_digest(files,artifact,case)+'\n')
   # The pinned fetch writes nothing: privacy and main == source are checked by the step that writes.
   self.assertIs(download.call_args.kwargs['check_private'],False);self.assertIs(download.call_args.kwargs['check_source'],False)
  workflow=(ROOT.parent/'.github/workflows/probe-htkk-windows.yml').read_text()
  self.assertIn('- name: Fetch fixed synthetic web XML privately\n        id: web_input\n',workflow)
  for script in ('publish-htkk-web-native-output.py','publish-htkk-declaration-native-output.py','publish-htkk-khbs-native-output.py'):
   step=workflow.split('run: python ./scripts/'+script,1)[0].rsplit('- name:',1)[1]
   self.assertIn('WEB_INPUT_DIGEST: ${{ steps.web_input.outputs.input_digest }}',step,script)
 def test_retention_checks_privacy_and_source_before_any_write(self):
  for module,native,provenance,inputs,fetch,calls,today,version in publications():
   with self.subTest(publisher=module.__name__):
    for info in ({'private':False,'full_name':p.REPO},{'private':True,'full_name':'other/repo'}):
     def answer(path,token,payload=None,method=None,info=info):
      if path=='':calls.append((path,token,payload,method));return info
      return retaining(fetch,provenance['sourceCommit'],calls)(path,token,payload,method)
     del calls[:]
     with self.assertRaises(Exception) as error:module.publish(native,provenance,TOKEN,answer,today,retain_immutable=True,version=version,inputs=inputs)
     self.assertEqual(module.safe_failure(error.exception)['code'],'PRIVATE_REPO');self.assertEqual(len(calls),1)
    del calls[:]
    with self.assertRaises(Exception) as error:module.publish(native,provenance,TOKEN,retaining(fetch,'f'*40,calls),today,retain_immutable=True,version=version,inputs=inputs)
    self.assertEqual(module.safe_failure(error.exception)['code'],'STALE_SOURCE');self.assertFalse(any(path.startswith('/git/refs') for path,*_ in calls))
    altered=dict(inputs);name=next(n for n in inputs if n!='manifest.json');altered[name]=inputs[name]+b' '
    del calls[:]
    with self.assertRaises(Exception) as error:module.publish(native,provenance,TOKEN,retaining(fetch,provenance['sourceCommit'],calls),today,retain_immutable=True,version=version,inputs=altered)
    self.assertEqual(module.safe_failure(error.exception)['code'],'HASH');self.assertFalse(any(path in ('/git/trees','/git/commits') or path.startswith('/git/refs') for path,*_ in calls))

class CombinedStatusGuard(unittest.TestCase):
 def test_latest_status_of_the_context_is_found_on_either_page(self):
  contexts=[{'context':'other/'+str(i),'state':'success'} for i in range(159)]
  for index,pages in ((0,1),(99,1),(100,2),(158,2)):
   listing=[dict(c) for c in contexts];listing[index]={'context':'htkk-native/zero','state':'pending','description':'queued input:'+'c'*40}
   get,read=combined(listing)
   with self.subTest(index=index):
    self.assertFalse(guard.allowed(SOURCE,'htkk-native/zero','5','1',TOKEN,TOKEN,get=get,input_commit='d'*40))
    self.assertEqual(len(read),1+pages)
  get,read=combined(contexts);self.assertTrue(guard.allowed(SOURCE,'htkk-native/zero','5','1',TOKEN,TOKEN,get=get));self.assertEqual(len(read),1+2)
  for body in ([],{'statuses':None},None):
   with self.subTest(body=body),self.assertRaises(ValueError):
    guard.allowed(SOURCE,'htkk-native/zero','5','1',TOKEN,TOKEN,get=lambda repo,path,token,body=body:{'object':{'sha':SOURCE}} if path=='git/ref/heads/main' else {'run_attempt':1} if path.startswith('actions/') else body)

class ReleaseBudget(unittest.TestCase):
 """Every web-repository request of one release, by stage, on the code as it runs."""
 def counts(self):
  result,calls,_,_,_=release();counts={'input publication':len(calls)}
  # Dispatch: one pending status per dispatched case (the workflow dispatch is a builder-repository request).
  sent=[]
  value=dict(result)
  d.dispatch(value,'actions','status',send=lambda url,token,payload:sent.append(url),builder='c'*40,get=lambda url,token:{'total_count':0,'workflow_runs':[]},sleep=lambda s:None,now=lambda:datetime.datetime(2026,12,2,tzinfo=datetime.timezone.utc))
  counts['dispatch']=sum(url.startswith('https://api.github.com/repos/'+d.REPO+'/') for url in sent);counts['dispatched']=sum('/dispatches' in url for url in sent)
  # Per native job: the fetch, the retention of its output and its status callback.
  counts['job fetch']={len(fetch_case(case)[1]) for case,_,_,_ in fx.fixtures()}
  publish=set()
  for module,native,provenance,inputs,fetch,calls_,today,version in publications():
   del calls_[:];module.publish(native,provenance,TOKEN,retaining(fetch,provenance['sourceCommit'],calls_),today,retain_immutable=True,version=version,inputs=inputs)
   publish.add(tuple('/git/ref/tags/<tag>' if path.startswith('/git/ref/tags/') else path if not path.startswith('/git/ref/heads/') or path.endswith('/main') else '/git/ref/heads/<branch>' for path,*_ in calls_))
  counts['job retention']=publish
  contexts=[{'context':'other/'+str(i),'state':'success'} for i in range(len(registry.CASES)+3)]
  get,read=combined(contexts);guard.allowed(SOURCE,'htkk-native/zero','5','1',TOKEN,TOKEN,get=get)
  counts['job callback']=len(read)+1 # guard reads of the web repository, then the status POST
  # Cohort gate: each poll reads the main ref and every combined-status page; then one main check and one
  # retained manifest per gating case.
  pages=[];batch.collector.combined_statuses(lambda repo,path:pages.append(path) or {'statuses':contexts[(len(pages)-1)*100:len(pages)*100]},SOURCE)
  counts['gate poll']=1+len(pages);counts['gate polls']=math.ceil(batch.DEADLINE/batch.POLL)+1
  counts['gate verify']=1+len(registry.GATE_CASES)
  return counts
 def test_one_release_fits_the_request_budget(self):
  c=self.counts()
  self.assertEqual(c['dispatched'],len(registry.CASES));self.assertEqual(c['dispatch'],len(registry.CASES))
  self.assertEqual(c['job fetch'],{2}) # pinned commit, commit archive
  self.assertEqual({len(sequence) for sequence in c['job retention']},{8})
  for sequence in c['job retention']:self.assertEqual(sequence[:6],('','/git/trees','/git/commits','/git/ref/heads/main','/git/ref/tags/<tag>','/git/refs'))
  self.assertEqual(c['job callback'],4)
  producers=len(set(p.CASE_PRODUCERS.values()))
  # repository, source commit, main, producers, package, plan; at most 3 cohort trees; commit; main; tag read and create; branch read and write; main.
  self.assertLessEqual(c['input publication'],5+producers+3+1+1+2+2+1)
  job=max(c['job fetch'])+8+c['job callback']
  total=c['input publication']+c['dispatch']+len(registry.CASES)*job+c['gate poll']*c['gate polls']+c['gate verify']
  self.assertLess(total,REQUEST_BUDGET,c)

if __name__=='__main__':unittest.main()
