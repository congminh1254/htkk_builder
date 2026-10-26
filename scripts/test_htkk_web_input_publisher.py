"""Offline publication contracts; synthetic fixtures are not Windows evidence."""
import base64,copy,hashlib,importlib.util,json,pathlib,tempfile,unittest,urllib.error
from unittest.mock import patch

ROOT=pathlib.Path(__file__).parent
spec=importlib.util.spec_from_file_location('web_publisher',ROOT/'publish-htkk-web-inputs.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
spec=importlib.util.spec_from_file_location('web_input_fixtures',ROOT/'test_htkk_web_input.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
SHA='a'*40
PRODUCER=b'// Fixed synthetic test producer, never executed.\n'

def fixtures():
 result=[]
 for case,_,branch in p.CASES:
  body=f.web_fixture() if case=='01GTGT-zero-M10-2026' else f.sale_fixture(case)
  metadata=f.manifest(body);metadata.update(format=p.reader.CASES[case],caseId=case,producerSha256=hashlib.sha256(PRODUCER).hexdigest())
  files={'01GTGT-web.xml':body,'manifest.json':(json.dumps(metadata,ensure_ascii=False)+'\n').encode()}
  result.append((case,branch,files,metadata))
 return result

def contents(body,name,path=None):
 result=f.envelope(body,name)
 if path is not None:result['path']=path
 return result

def fake_api(info=None,main=SHA,existing=True):
 calls=[];commits=[]
 def fetch(path,token,payload=None,method=None):
  calls.append((path,token,payload,method))
  if path=='':return info if info is not None else {'private':True,'full_name':p.REPO}
  if path=='/git/commits/'+SHA:return {'sha':SHA}
  if path=='/git/ref/heads/main':return {'ref':'refs/heads/main','object':{'type':'commit','sha':main}}
  if path=='/contents/'+p.PRODUCER+'?ref='+SHA:return contents(PRODUCER,'generate-htkk-web-reference.mjs',p.PRODUCER)
  if path=='/contents/package.json?ref='+SHA:return contents(b'{"version":"0.9.2"}','package.json')
  if path=='/git/blobs':
   body=base64.b64decode(payload['content']);return {'sha':hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest()}
  if path=='/git/trees':return {'sha':'c'*40}
  if path=='/git/commits':
   self_sha=('d','e','f','1','2','3')[len(commits)]*40;commits.append(payload);return {'sha':self_sha}
  if path.startswith('/git/ref/heads/'):
   if not existing:raise urllib.error.HTTPError('https://api.github.com/',404,'PRIVATE REMOTE TEXT',{},None)
   return {'ref':'refs/heads/'+path.rsplit('/',1)[1],'object':{'type':'commit','sha':'f'*40}}
  if path.startswith('/git/refs/heads/'):
   if not existing:raise AssertionError('Missing branch must be created after GET 404; never PATCH')
   return {'ref':'refs/heads/'+path.rsplit('/',1)[1],'object':{'type':'commit','sha':payload['sha']}}
  if path=='/git/refs':return {'ref':payload['ref'],'object':{'type':'commit','sha':payload['sha']}}
  raise AssertionError('Unexpected fixed GitHub path')
 return fetch,calls,commits

def write_staged(parent,inputs=None):
 for (_,directory,_),item in zip(p.CASES,inputs or fixtures()):
  folder=pathlib.Path(parent)/directory;folder.mkdir()
  for name,body in item[2].items():(folder/name).write_bytes(body)

class StagingTests(unittest.TestCase):
 def test_both_fixed_cases_preserved_and_revalidated(self):
  with tempfile.TemporaryDirectory() as temporary:
   write_staged(temporary);result=p.read_inputs(temporary,SHA)
   self.assertEqual(result,fixtures());self.assertIn(b'<ct32>1000000</ct32>',result[1][2]['01GTGT-web.xml'])
 def test_missing_extra_or_swapped_case_file_rejected(self):
  for mutation in ('missing','extra','wrongcase'):
   with self.subTest(mutation=mutation),tempfile.TemporaryDirectory() as temporary:
    write_staged(temporary);folder=pathlib.Path(temporary)/p.CASES[0][1]
    if mutation=='missing':(folder/'01GTGT-web.xml').unlink()
    elif mutation=='extra':(folder/'PRIVATE.txt').write_text('secret')
    else:(folder/'manifest.json').write_bytes(fixtures()[1][2]['manifest.json'])
    with self.assertRaises((p.PublicationError,p.reader.InputError)):p.read_inputs(temporary,SHA)
 def test_hash_source_producer_and_privacy_rejected(self):
  for mutation in ('hash','source','producer','private'):
   with self.subTest(mutation=mutation),tempfile.TemporaryDirectory() as temporary:
    inputs=copy.deepcopy(fixtures());case,branch,files,metadata=inputs[0]
    if mutation=='hash':metadata['xmlSha256']='f'*64
    elif mutation=='source':metadata['sourceCommit']='b'*40
    elif mutation=='producer':metadata['producerSha256']='f'*64
    else:
     files['01GTGT-web.xml']=files['01GTGT-web.xml'].replace(b'NNT KIEM THU GIA LAP - KHONG NOP',b'PRIVATE CUSTOMER')
     metadata['bytes']=len(files['01GTGT-web.xml']);metadata['xmlSha256']=hashlib.sha256(files['01GTGT-web.xml']).hexdigest()
    files['manifest.json']=json.dumps(metadata).encode();write_staged(temporary,inputs)
    with self.assertRaises((p.PublicationError,p.reader.InputError)):p.read_inputs(temporary,SHA)
 def test_oversize_xml_and_manifest_rejected(self):
  for name,maximum in (('01GTGT-web.xml',p.reader.MAX_XML),('manifest.json',p.reader.MAX_MANIFEST)):
   with self.subTest(name=name),tempfile.TemporaryDirectory() as temporary:
    write_staged(temporary);(pathlib.Path(temporary)/p.CASES[0][1]/name).write_bytes(b'x'*(maximum+1))
    with self.assertRaises(p.PublicationError):p.read_inputs(temporary,SHA)
 def test_symlink_file_folder_and_ancestor_rejected(self):
  for kind in ('file','folder','ancestor'):
   with self.subTest(kind=kind),tempfile.TemporaryDirectory() as temporary:
    root=pathlib.Path(temporary);real=root/'real';real.mkdir();write_staged(real)
    if kind=='file':
     item=real/p.CASES[0][1]/'01GTGT-web.xml';target=root/'target';item.rename(target);item.symlink_to(target)
    elif kind=='folder':
     item=real/p.CASES[0][1];target=root/'target';item.rename(target);item.symlink_to(target,target_is_directory=True)
    else:
     alias=root/'alias';alias.symlink_to(real,target_is_directory=True);real=alias
    with self.assertRaises(p.PublicationError):p.read_inputs(real,SHA)

class PublicationTests(unittest.TestCase):
 def test_orphan_private_publication_preserves_bytes_and_metadata_only_result(self):
  inputs=fixtures();fetch,calls,commits=fake_api();result=p.publish(inputs,SHA,'synthetic-token',fetch)
  self.assertEqual(result,{'format':'htkk-web-input-publication-v1','sourceCommit':SHA,'cases':[{'caseId':case[0],'artifactCommit':letter*40} for case,letter in zip(p.CASES,('d','e','f','1','2','3'))]})
  self.assertTrue(all(item['parents']==[] for item in commits));self.assertTrue(all(token=='synthetic-token' for _,token,_,_ in calls))
  blobs=[base64.b64decode(payload['content']) for path,_,payload,_ in calls if path=='/git/blobs']
  self.assertEqual(blobs,[item[2][name] for item in inputs for name in p.reader.NAMES])
  patches=[(path,payload) for path,_,payload,method in calls if method=='PATCH']
  self.assertEqual([path for path,_ in patches],['/git/refs/heads/'+case[2] for case in p.CASES]);self.assertTrue(all(payload['force'] is True for _,payload in patches))
  self.assertNotIn('synthetic-token',json.dumps(result));self.assertNotIn('xml',json.dumps(result))
 def test_missing_branches_created_only_after_404(self):
  fetch,calls,_=fake_api(existing=False);p.publish(fixtures(),SHA,'synthetic-token',fetch)
  self.assertEqual(len([path for path,_,_,_ in calls if path=='/git/refs']),len(p.CASES))
  self.assertFalse(any(method=='PATCH' for _,_,_,method in calls))
  for case,_,branch in p.CASES:
   get_index=next(i for i,(path,_,_,_) in enumerate(calls) if path=='/git/ref/heads/'+branch)
   post_index=next(i for i,(path,_,body,_) in enumerate(calls) if path=='/git/refs' and body['ref']=='refs/heads/'+branch)
   self.assertLess(get_index,post_index)
 def test_get_ref_auth_or_validation_error_never_creates_or_patches(self):
  for code in (401,403,422,500):
   fetch,calls,_=fake_api()
   def denied(path,token,payload=None,method=None):
    if path=='/git/ref/heads/'+p.CASES[0][2]:
     calls.append((path,token,payload,method));raise urllib.error.HTTPError('https://api.github.com/',code,'PRIVATE REMOTE TEXT',{},None)
    return fetch(path,token,payload,method)
   with self.subTest(code=code),self.assertRaises(urllib.error.HTTPError):p.publish(fixtures(),SHA,'synthetic-token',denied)
   self.assertFalse(any(path=='/git/refs' or method=='PATCH' for path,_,_,method in calls))
 def test_failed_patch_never_falls_back_to_create_or_retries(self):
  for code in (401,403,404,422,500):
   fetch,calls,_=fake_api()
   def denied(path,token,payload=None,method=None):
    if method=='PATCH':
     calls.append((path,token,payload,method));raise urllib.error.HTTPError('https://api.github.com/',code,'PRIVATE REMOTE TEXT',{},None)
    return fetch(path,token,payload,method)
   with self.subTest(code=code),self.assertRaises(urllib.error.HTTPError):p.publish(fixtures(),SHA,'synthetic-token',denied)
   self.assertEqual(len([1 for _,_,_,method in calls if method=='PATCH']),1)
   self.assertFalse(any(path=='/git/refs' for path,_,_,_ in calls))
 def test_malformed_existing_ref_rejected_without_mutation(self):
  for value in (None,{'ref':'refs/heads/main','object':{'type':'commit','sha':'f'*40}},{'ref':'refs/heads/'+p.CASES[0][2],'object':{'type':'tag','sha':'f'*40}},{'ref':'refs/heads/'+p.CASES[0][2],'object':{'type':'commit','sha':'invalid'}}):
   fetch,calls,_=fake_api()
   def malformed(path,token,payload=None,method=None):
    if path=='/git/ref/heads/'+p.CASES[0][2]:return value
    return fetch(path,token,payload,method)
   with self.subTest(value=value),self.assertRaises(p.PublicationError):p.publish(fixtures(),SHA,'synthetic-token',malformed)
   self.assertFalse(any(path=='/git/refs' or method=='PATCH' for path,_,_,method in calls))
 def test_private_identity_checked_before_any_source_or_write(self):
  for info in ({'private':False,'full_name':p.REPO},{'private':True,'full_name':'other/repo'}):
   fetch,calls,_=fake_api(info=info)
   with self.assertRaises(p.PublicationError) as error:p.publish(fixtures(),SHA,'synthetic-token',fetch)
   self.assertEqual(error.exception.code,'PRIVATE_REPO');self.assertEqual(len(calls),1)
 def test_stale_source_fails_before_writes(self):
  fetch,calls,_=fake_api(main='b'*40)
  with self.assertRaises(p.PublicationError) as error:p.publish(fixtures(),SHA,'synthetic-token',fetch)
  self.assertEqual(error.exception.code,'STALE_SOURCE');self.assertFalse(any(payload is not None for _,_,payload,_ in calls))
 def test_new_main_during_publish_prevents_branch_update_and_result(self):
  fetch,calls,_=fake_api();checks=0
  def moving(path,token,payload=None,method=None):
   nonlocal checks
   if path=='/git/ref/heads/main':
    checks+=1
    if checks>1:return {'ref':'refs/heads/main','object':{'type':'commit','sha':'b'*40}}
   return fetch(path,token,payload,method)
  with self.assertRaises(p.PublicationError) as error:p.publish(fixtures(),SHA,'synthetic-token',moving)
  self.assertEqual(error.exception.code,'STALE_SOURCE');self.assertFalse(any(method=='PATCH' for _,_,_,method in calls))
 def test_producer_source_hash_and_package_version_verified_before_writes(self):
  for mutation in ('producer','version','path','source'):
   fetch,calls,_=fake_api()
   def altered(path,token,payload=None,method=None):
    if mutation=='producer' and path.startswith('/contents/scripts/'):return contents(b'other producer','generate-htkk-web-reference.mjs',p.PRODUCER)
    if mutation=='version' and path.startswith('/contents/package.json'):return contents(b'{"version":"0.0.1"}','package.json')
    if mutation=='path' and path.startswith('/contents/scripts/'):return contents(PRODUCER,'generate-htkk-web-reference.mjs','other/path')
    if mutation=='source' and path=='/git/commits/'+SHA:return {'sha':'b'*40}
    return fetch(path,token,payload,method)
   with self.subTest(mutation=mutation),self.assertRaises(p.PublicationError):p.publish(fixtures(),SHA,'synthetic-token',altered)
   self.assertFalse(any(payload is not None for _,_,payload,_ in calls))
 def test_wrong_case_or_changed_xml_rejected_before_network(self):
  for mutation in ('case','hash'):
   inputs=copy.deepcopy(fixtures());fetch,calls,_=fake_api()
   if mutation=='case':inputs.reverse()
   else:inputs[0][2]['01GTGT-web.xml']+=b'PRIVATE'
   with self.subTest(mutation=mutation),self.assertRaises((p.PublicationError,p.reader.InputError)):p.publish(inputs,SHA,'synthetic-token',fetch)
   self.assertFalse(calls)
 def test_blob_identity_and_ref_response_rejected(self):
  for mutation in ('blob','ref'):
   fetch,_,_=fake_api()
   def altered(path,token,payload=None,method=None):
    if mutation=='blob' and path=='/git/blobs':return {'sha':'f'*40}
    if mutation=='ref' and path.startswith('/git/refs/heads/'):return {'ref':'refs/heads/main','object':{'type':'commit','sha':'d'*40}}
    return fetch(path,token,payload,method)
   with self.subTest(mutation=mutation),self.assertRaises(p.PublicationError):p.publish(fixtures(),SHA,'synthetic-token',altered)
 def test_auth_http_failures_not_retried_and_remote_text_not_exposed(self):
  for code in (401,403,422,500):
   calls=[]
   def denied(*args):calls.append(args);raise urllib.error.HTTPError('https://api.github.com/',code,'SECRET PRIVATE REMOTE BODY',{},None)
   with self.subTest(code=code),self.assertRaises(urllib.error.HTTPError) as error:p.publish(fixtures(),SHA,'synthetic-token',denied)
   self.assertEqual(len(calls),1);report=json.dumps(p.safe_failure(error.exception));self.assertNotIn('SECRET',report);self.assertNotIn('synthetic-token',report)
 def test_no_redirect_and_api_bounded_response(self):
  self.assertIsNone(p.NoRedirect().redirect_request(None,None,None,None,None,None))
  class Response:
   status=200
   def __enter__(self):return self
   def __exit__(self,*args):pass
   def read(self,size):self.size=size;return b'x'*(p.reader.MAX_API+1)
  response=Response()
  class Opener:
   def open(self,request,timeout):
    self.request=request;self.timeout=timeout;return response
  opener=Opener()
  with patch.object(p.urllib.request,'build_opener',return_value=opener) as constructor:
   with self.assertRaises(p.PublicationError) as error:p.api('', 'synthetic-token')
  self.assertEqual(error.exception.code,'API_SIZE');self.assertIsInstance(constructor.call_args.args[0],p.NoRedirect);self.assertEqual(response.size,p.reader.MAX_API+1)
  self.assertEqual(opener.request.full_url,'https://api.github.com/repos/'+p.REPO);self.assertEqual(opener.request.get_header('Authorization'),'Bearer synthetic-token')
 def test_result_fresh_fixed_path_and_no_overwrite(self):
  fetch,_,_=fake_api();result=p.publish(fixtures(),SHA,'synthetic-token',fetch)
  with tempfile.TemporaryDirectory() as temporary:
   p.save_result(result,temporary);path=pathlib.Path(temporary)/p.OUTPUT
   self.assertEqual(json.loads(path.read_bytes()),result)
   with self.assertRaises(p.PublicationError):p.save_result(result,temporary)
   self.assertEqual(json.loads(path.read_bytes()),result)

if __name__=='__main__':unittest.main()
