"""Synthetic offline parser/transport fixtures, never native execution evidence."""
import base64,copy,datetime,hashlib,importlib.util,json,pathlib,tempfile,unittest,urllib.error
from unittest.mock import patch
import xml.etree.ElementTree as ET
ROOT=pathlib.Path(__file__).parent
spec=importlib.util.spec_from_file_location('web_input',ROOT/'fetch-htkk-web-input.py');w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
spec=importlib.util.spec_from_file_location('native_parser_fixtures',ROOT/'test_gtgt_export_evidence.py');n=importlib.util.module_from_spec(spec);spec.loader.exec_module(n)
TODAY=datetime.date(2026,10,25)
def web_fixture():
 root=ET.fromstring(n.parser_fixture());ns='{'+w.privacy.NS+'}';service=root.find('./'+ns+'HSoKhaiThue/'+ns+'TTinChung/'+ns+'TTinDVu')
 for child in service:child.text=w.SERVICE[child.tag[len(ns):]]
 for name in ('ngayLapTKhai','ngayKy'):root.find('./'+ns+'HSoKhaiThue/'+ns+'TTinChung/'+ns+'TTinTKhaiThue/'+ns+'TKhaiThue/'+ns+name).text='2026-10-25'
 return (w.PREAMBLE+ET.tostring(root,encoding='unicode')).encode('utf-8')
def sale_fixture(case="01GTGT-sale10-M10-2026"):
 root=ET.fromstring(web_fixture().decode().replace(w.COMMENT,''));ns='{'+w.privacy.NS+'}'
 for name,value in w.CASE_MONEY[case].items():root.find('.//'+ns+name).text=value
 return (w.PREAMBLE+ET.tostring(root,encoding='unicode')).encode('utf-8')
def manifest(body):return {'format':'htkk-web-zero-input-v1','sourceRepository':w.REPO,'sourceCommit':'a'*40,'sourceVersion':'0.9.2','caseId':'01GTGT-zero-M10-2026','inputsSynthetic':True,'exporter':'lib/htkk-xml.ts','producerSha256':'c'*64,'xmlSha256':hashlib.sha256(body).hexdigest(),'bytes':len(body)}
def envelope(body,name):return {'type':'file','name':name,'path':name,'encoding':'base64','size':len(body),'content':base64.encodebytes(body).decode(),'sha':hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest()}
def fake_fetch(body,metadata=None,info=None):
 calls=[];metadata=manifest(body) if metadata is None else metadata
 def fetch(path,token):
  calls.append((path,token))
  if path=='':return info if info is not None else {'private':True,'full_name':w.REPO}
  if path=='/git/ref/heads/'+w.BRANCH:return {'ref':'refs/heads/'+w.BRANCH,'object':{'type':'commit','sha':'b'*40}}
  if path=='/git/commits/'+'a'*40:return {'sha':'a'*40}
  if path=='/contents/manifest.json?ref='+'b'*40:return envelope(json.dumps(metadata,ensure_ascii=False).encode(),'manifest.json')
  if path=='/contents/01GTGT-web.xml?ref='+'b'*40:return envelope(body,'01GTGT-web.xml')
  raise AssertionError('Unexpected fixed API path')
 return fetch,calls
class PrivacyTests(unittest.TestCase):
 def test_round_half_and_manual_override_exact_cases_accept_only_known_amount_vectors(self):
  for case in ('01GTGT-sale10-half-M10-2026','01GTGT-sale10-manual-M10-2026','01GTGT-sale5-half-M10-2026','01GTGT-sale5-manual-M10-2026'):
   body=sale_fixture(case)
   self.assertTrue(w.validate_web_xml(body,TODAY,case)['privacyValuesVerified'])
   for name,value in w.CASE_MONEY[case].items():
    changed=body.replace(('<'+name+'>'+value+'</'+name+'>').encode(),('<'+name+'>'+str(int(value)+1)+'</'+name+'>').encode())
    with self.subTest(case=case,field=name),self.assertRaises(w.InputError):w.validate_web_xml(changed,TODAY,case)
 def test_new_amount_cases_cannot_be_relabelled_as_each_other(self):
  a='01GTGT-sale10-half-M10-2026';b='01GTGT-sale10-manual-M10-2026'
  for body,case in ((sale_fixture(a),b),(sale_fixture(b),a),(sale_fixture(a),'01GTGT-sale10-M10-2026')):
   with self.assertRaises(w.InputError):w.validate_web_xml(body,TODAY,case)

 def test_five_percent_cases_reject_ten_percent_relabelling_and_unexpected_amounts(self):
  for five,ten in (('01GTGT-sale5-half-M10-2026','01GTGT-sale10-half-M10-2026'),('01GTGT-sale5-manual-M10-2026','01GTGT-sale10-manual-M10-2026')):
   for source,target in ((five,ten),(ten,five)):
    with self.subTest(source=source,target=target),self.assertRaises(w.InputError):w.validate_web_xml(sale_fixture(source),TODAY,target)

 def setUp(self):self.body=web_fixture()
 def reject(self,body,code):
  with self.assertRaises(w.InputError) as error:w.validate_web_xml(body,TODAY)
  self.assertEqual(error.exception.code,code)
 def test_exact_web_identity_comment_and_zero_case_accepted(self):
  result=w.validate_web_xml(self.body,TODAY);self.assertEqual(result,{'privacyValuesVerified':True,'serviceIdentity':'web-draft','nativeProvenance':False})
 def test_historical_case_is_repeatable_but_created_and_signing_dates_are_fixed(self):
  self.assertTrue(w.validate_web_xml(self.body,datetime.date(2027,10,25))['privacyValuesVerified'])
  for name in ('ngayLapTKhai','ngayKy'):
   old=('<'+name+'>2026-10-25</'+name+'>').encode()
   for date in ('2026-10-24','2026-10-26','2027-10-25'):
    self.reject(self.body.replace(old,('<'+name+'>'+date+'</'+name+'>').encode()),'XML_PRIVACY')
 def test_native_service_impersonation_and_modified_service_rejected(self):
  for name,value in (('maDVu','HTKK'),('ttinNhaCCapDVu','0'*32),('pbanDVu','0.9.3'),('tenDVu','PRIVATE')):
   before=w.SERVICE[name].encode();self.reject(self.body.replace(before,value.encode(),1),'XML_SERVICE')
 def test_other_comment_dtd_entity_pi_or_comment_position_rejected(self):
  for body in (self.body.replace(w.COMMENT.encode(),b'<!-- PRIVATE -->'),self.body+w.COMMENT.encode(),self.body+b'<!-- extra -->',self.body+b'<!DOCTYPE x>',self.body+b'<?secret raw?>',self.body+b'<!ENTITY x "secret">',self.body.replace(w.COMMENT.encode()+b'\n',b'')+w.COMMENT.encode()):
   self.reject(body,'XML_DECLARATION')
 def test_unknown_attributes_private_taxpayer_and_extra_node_rejected(self):
  self.reject(self.body.replace(b'<HSoKhaiThue id="ID_1"',b'<HSoKhaiThue private="secret" id="ID_1"'),'XML_PRIVACY')
  self.reject(self.body.replace(b'NNT KIEM THU GIA LAP - KHONG NOP',b'PRIVATE CUSTOMER'),'XML_PRIVACY')
  self.reject(self.body.replace(b'</HSoKhaiThue>',b'<extra>PRIVATE</extra></HSoKhaiThue>'),'XML_PRIVACY')
 def test_unused_namespace_cannot_be_lost_during_in_memory_conversion(self):
  self.reject(self.body.replace(b'<HSoThueDTu ',b'<HSoThueDTu xmlns:secret="https://private.invalid/" '),'XML_PRIVACY')
 def test_nonzero_or_wrong_period_not_covered_by_service_adapter(self):
  self.reject(self.body.replace(b'<ct22>0</ct22>',b'<ct22>1</ct22>'),'XML_PRIVACY')
  self.reject(self.body.replace(b'2026-10-01',b'2026-10-02'),'XML_PRIVACY')
 def test_size_and_utf8_rejected(self):
  self.reject(b'x'*(w.MAX_XML+1),'XML_SIZE');self.reject(b'\xff','XML_ENCODING')
class SaleCaseTests(unittest.TestCase):
 def test_sale_case_exact_numbers_allowed_without_changing_original_bytes(self):
  body=sale_fixture();digest=hashlib.sha256(body).hexdigest()
  self.assertTrue(w.validate_web_xml(body,datetime.date(2027,10,25),'01GTGT-sale10-M10-2026')['privacyValuesVerified'])
  self.assertEqual(hashlib.sha256(body).hexdigest(),digest)
 def test_cases_cannot_be_mixed_or_arbitrary_amounts_inserted(self):
  for body,case in ((sale_fixture(),'01GTGT-zero-M10-2026'),(web_fixture(),'01GTGT-sale10-M10-2026'),(sale_fixture().replace(b'<ct40>100000</ct40>',b'<ct40>100001</ct40>'),'01GTGT-sale10-M10-2026'),(sale_fixture().replace(b'<ct42>0</ct42>',b'<ct42>1</ct42>'),'01GTGT-sale10-M10-2026')):
   with self.assertRaises(w.InputError):w.validate_web_xml(body,TODAY,case)
 def test_manifest_case_format_pair_and_requested_case_are_pinned(self):
  body=sale_fixture();metadata=manifest(body);metadata.update(caseId='01GTGT-sale10-M10-2026',format='htkk-web-sale10-input-v1')
  fetch,_=fake_fetch(body,metadata)
  self.assertEqual(w.download('synthetic-token',fetch,TODAY,expected_case='01GTGT-sale10-M10-2026')['01GTGT-web.xml'],body)
  with self.assertRaises(w.InputError):w.download('synthetic-token',fetch,TODAY,expected_case='01GTGT-zero-M10-2026')
  metadata['format']='htkk-web-zero-input-v1'
  with self.assertRaises(w.InputError):w.validate_manifest(json.dumps(metadata).encode())
class ReadAndStageTests(unittest.TestCase):
 def setUp(self):self.body=web_fixture()
 def test_private_download_pins_artifact_commit_checks_source_and_preserves_bytes(self):
  fetch,calls=fake_fetch(self.body);files=w.download('synthetic-token',fetch,TODAY)
  self.assertEqual(files['01GTGT-web.xml'],self.body);self.assertTrue(all(token=='synthetic-token' for _,token in calls));self.assertEqual(calls[0][0],'')
  self.assertTrue(all('?ref='+'b'*40 in path for path,_ in calls if '/contents/' in path));self.assertIn(('/git/commits/'+'a'*40,'synthetic-token'),calls)
  with tempfile.TemporaryDirectory() as temporary:
   destination=w.stage(files,temporary,TODAY);self.assertEqual(set(path.name for path in destination.iterdir()),set(w.NAMES));self.assertEqual((destination/'01GTGT-web.xml').read_bytes(),self.body);self.assertIn(b'HTKK-WEB-DRAFT',(destination/'01GTGT-web.xml').read_bytes());self.assertEqual((destination/'manifest.json').read_bytes(),files['manifest.json'])
 def test_immutable_artifact_commit_does_not_follow_mutable_branch(self):
  fetch,calls=fake_fetch(self.body)
  def pinned(path,token):
   if path=='/git/commits/'+'b'*40:return {'sha':'b'*40}
   return fetch(path,token)
  self.assertEqual(w.download('synthetic-token',pinned,TODAY,artifact_commit='b'*40)['01GTGT-web.xml'],self.body)
  self.assertFalse(any('/git/ref/' in path for path,_ in calls))
  calls.clear()
  with self.assertRaises(w.InputError):w.download('synthetic-token',pinned,TODAY,artifact_commit='bad')
  self.assertEqual(calls,[])
 def test_expected_source_required_shape_before_network_and_matches_manifest(self):
  fetch,calls=fake_fetch(self.body)
  with self.assertRaises(w.InputError):w.download('synthetic-token',fetch,TODAY,expected_source='bad')
  self.assertEqual(calls,[])
  with self.assertRaises(w.InputError):w.download('synthetic-token',fetch,TODAY,expected_source='c'*40)
  self.assertFalse(any('/contents/01GTGT-web.xml' in path for path,_ in calls))
  self.assertEqual(w.download('synthetic-token',fetch,TODAY,expected_source='a'*40)['01GTGT-web.xml'],self.body)
 def test_public_or_wrong_repo_stops_before_reading_files(self):
  for info in ({'private':False,'full_name':w.REPO},{'private':True,'full_name':'other/repo'}):
   fetch,calls=fake_fetch(self.body,info=info)
   with self.assertRaises(w.InputError) as error:w.download('synthetic-token',fetch,TODAY)
   self.assertEqual(error.exception.code,'PRIVATE_REPO');self.assertEqual(len(calls),1)
 def test_manifest_extra_wrong_typed_false_or_invalid_hash_rejected(self):
  for key,value in (('extra','PRIVATE'),('inputsSynthetic',1),('inputsSynthetic',False),('sourceRepository','other/repo'),('sourceCommit','$(bad)'),('producerSha256','a'*63),('bytes',True),('sourceVersion','0.9.3')):
   metadata=manifest(self.body);metadata[key]=value;fetch,calls=fake_fetch(self.body,metadata)
   with self.subTest(key=key,value=value),self.assertRaises(w.InputError) as error:w.download('synthetic-token',fetch,TODAY)
   self.assertEqual(error.exception.code,'MANIFEST')
 def test_manifest_duplicate_keys_rejected(self):
  body=json.dumps(manifest(self.body)).replace('"inputsSynthetic": true','"inputsSynthetic": false,"inputsSynthetic": true').encode()
  with self.assertRaises(w.InputError):w.validate_manifest(body)
 def test_xml_hash_mismatch_rejected(self):
  metadata=manifest(self.body);metadata['xmlSha256']='d'*64;fetch,calls=fake_fetch(self.body,metadata)
  with self.assertRaises(w.InputError) as error:w.download('synthetic-token',fetch,TODAY)
  self.assertEqual(error.exception.code,'HASH')
 def test_unknown_source_commit_rejected(self):
  fetch,calls=fake_fetch(self.body)
  def wrong(path,token):return {'sha':'d'*40} if path.startswith('/git/commits/') else fetch(path,token)
  with self.assertRaises(w.InputError) as error:w.download('synthetic-token',wrong,TODAY)
  self.assertEqual(error.exception.code,'SOURCE_COMMIT')
 def test_bad_content_encoding_blob_hash_file_type_size_and_base64_rejected(self):
  for key,value in (('type','symlink'),('encoding','none'),('sha','d'*40),('size',True),('size',w.MAX_XML+1),('content','not!base64'),('name','wrong.xml'),('path','../01GTGT-web.xml')):
   data=envelope(self.body,'01GTGT-web.xml');data[key]=value
   with self.subTest(key=key),self.assertRaises(w.InputError):w.content_file(data,'01GTGT-web.xml',w.MAX_XML)
 def test_missing_token_no_call_auth_error_no_retry(self):
  fetch,calls=fake_fetch(self.body)
  with self.assertRaises(w.InputError):w.download('',fetch,TODAY)
  self.assertFalse(calls)
  def denied(path,token):calls.append(path);raise urllib.error.HTTPError('https://api.github.com/',403,'SECRET REMOTE MESSAGE',{},None)
  with self.assertRaises(urllib.error.HTTPError) as error:w.download('synthetic-token',denied,TODAY)
  self.assertEqual(len(calls),1);self.assertEqual(w.safe_failure(error.exception)['code'],'AUTH');self.assertNotIn('SECRET',json.dumps(w.safe_failure(error.exception)))
 def test_staging_existing_directory_untouched_and_partial_error_cleaned(self):
  fetch,_=fake_fetch(self.body);files=w.download('synthetic-token',fetch,TODAY)
  with tempfile.TemporaryDirectory() as temporary:
   destination=pathlib.Path(temporary)/'htkk-web-reference-input';destination.mkdir();(destination/'existing').write_text('keep')
   with self.assertRaises(w.InputError):w.stage(files,temporary,TODAY)
   self.assertEqual((destination/'existing').read_text(),'keep')
  with tempfile.TemporaryDirectory() as temporary:
   original=pathlib.Path.open
   def fail_manifest(path,*args,**kwargs):
    if path.name=='manifest.json':raise OSError('PRIVATE PATH')
    return original(path,*args,**kwargs)
   with patch.object(pathlib.Path,'open',fail_manifest),self.assertRaises(OSError):w.stage(files,temporary,TODAY)
   self.assertEqual(list(pathlib.Path(temporary).iterdir()),[])
 def test_api_get_fixed_origin_bearer_and_no_redirect_handler(self):
  seen={}
  class Response:
   status=200
   def __enter__(self):return self
   def __exit__(self,*args):pass
   def read(self,size):seen['bound']=size;return b'{"private":true}'
  class Opener:
   def open(self,request,timeout):seen['request']=request;seen['timeout']=timeout;return Response()
  def build(*handlers):seen['handlers']=handlers;return Opener()
  with patch.object(w.urllib.request,'build_opener',side_effect=build):self.assertEqual(w.api('','synthetic-token'),{'private':True})
  request=seen['request'];self.assertEqual(request.full_url,'https://api.github.com/repos/'+w.REPO);self.assertEqual(request.get_method(),'GET');self.assertIsNone(request.data);self.assertEqual(request.get_header('Authorization'),'Bearer synthetic-token');self.assertEqual(seen['bound'],w.MAX_API+1)
  self.assertIsNone(seen['handlers'][0].redirect_request(None,None,302,'',{},'https://other.invalid/'))
 def test_api_oversize_and_raw_failure_sanitized(self):
  class Response:
   status=200
   def __enter__(self):return self
   def __exit__(self,*args):pass
   def read(self,size):return b'x'*size
  class Opener:
   def open(self,*args,**kwargs):return Response()
  with patch.object(w.urllib.request,'build_opener',return_value=Opener()),self.assertRaises(w.InputError) as error:w.api('','synthetic-token')
  self.assertEqual(error.exception.code,'API_SIZE')
  self.assertNotIn('PRIVATE',json.dumps(w.safe_failure(ValueError('PRIVATE XML PATH TOKEN'))))
if __name__=='__main__':unittest.main()
