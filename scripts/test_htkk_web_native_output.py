"""Synthetic parser/transport tests, never substitute for native execution."""
import base64,copy,datetime,hashlib,importlib.util,json,pathlib,tempfile,unittest,urllib.error
from unittest.mock import patch
import xml.etree.ElementTree as ET

ROOT=pathlib.Path(__file__).parent
spec=importlib.util.spec_from_file_location('native_output',ROOT/'publish-htkk-web-native-output.py');n=importlib.util.module_from_spec(spec);spec.loader.exec_module(n)
spec=importlib.util.spec_from_file_location('native_output_web_fixtures',ROOT/'test_htkk_web_input.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
TODAY=datetime.date(2026,10,26)
SOURCE='a'*40
ARTIFACT='b'*40
BUILDER_SHA='c'*40

def fixture(case='01GTGT-zero-M10-2026'):
 root=ET.fromstring(f.sale_fixture(case) if case!='01GTGT-zero-M10-2026' else f.web_fixture());ns='{'+n.privacy.NS+'}'
 root.find('.//'+ns+'ct21').text='0'
 web=(n.reader.PREAMBLE+ET.tostring(root,encoding='unicode')).encode('utf-8')
 for name,value in n.SERVICE.items():root.find('.//'+ns+name).text=value
 root.find('.//'+ns+'ttinNhaCCapDVu').text='A'*32
 root.find('.//'+ns+'ngayLapTKhai').text='2026-10-26'
 native=ET.tostring(root,encoding='utf-8',xml_declaration=True)
 input_manifest=f.manifest(web);input_manifest.update(caseId=case,format=n.reader.CASES[case])
 provenance={'format':'htkk-web-native-output-staging-v1','builderRepository':n.BUILDER,'builderCommit':BUILDER_SHA,'runId':'123','sourceRepository':n.REPO,'sourceCommit':SOURCE,'sourceVersion':'5.8.1','runtimeHost':'clr2-x86-reference','caseId':case,'inputsSynthetic':True,'originalProcessStopped':True,'originalSourcesUnmodified':True,'originalExportSucceeded':True,'originalImportSucceeded':True,'originalReexportSucceeded':True,'originalExporterValidatedSchema':True,'webTaxComparisonPassed':True,'webTaxCheckedLeafCount':70,'webImportInputSha256':hashlib.sha256(web).hexdigest(),'originalOutputSha256':hashlib.sha256(native).hexdigest(),'originalOutputBytes':len(native),'artifactCommit':ARTIFACT,'creationDateRule':'native-export-current-date','fullRoundTrip':False}
 return web,native,input_manifest,provenance

def changed(body,name,value):
 root=ET.fromstring(body);root.find('.//{'+n.privacy.NS+'}'+name).text=value;return ET.tostring(root,encoding='utf-8')

def fake_api(web,manifest,info=None,existing=True):
 calls=[]
 def fetch(path,token,payload=None,method=None):
  calls.append((path,token,payload,method))
  if path=='':return info if info is not None else {'private':True,'full_name':n.REPO}
  if path in ('/git/commits/'+SOURCE,'/git/commits/'+ARTIFACT):return {'sha':path.rsplit('/',1)[1]}
  if path=='/contents/manifest.json?ref='+ARTIFACT:return f.envelope(json.dumps(manifest,ensure_ascii=False).encode(),'manifest.json')
  if path=='/contents/01GTGT-web.xml?ref='+ARTIFACT:return f.envelope(web,'01GTGT-web.xml')
  if path=='/git/blobs':
   body=base64.b64decode(payload['content']);return {'sha':hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest()}
  if path=='/git/trees':return {'sha':'d'*40}
  if path=='/git/commits':return {'sha':'e'*40}
  if path.startswith('/git/ref/heads/'):
   if not existing:raise urllib.error.HTTPError('https://api.github.com/',404,'SECRET PRIVATE REMOTE TEXT',{},None)
   return {'ref':'refs/heads/'+path.rsplit('/',1)[1],'object':{'type':'commit','sha':'f'*40}}
  if path.startswith('/git/refs/heads/'):return {'ref':'refs/heads/'+path.rsplit('/',1)[1],'object':{'type':'commit','sha':payload['sha']}}
  if path=='/git/refs':return {'ref':payload['ref'],'object':{'type':'commit','sha':payload['sha']}}
  raise AssertionError('Unexpected fixed API path')
 return fetch,calls

class NativePrivacyTests(unittest.TestCase):
 def test_rounding_and_manual_native_outputs_reject_wrong_tax_or_wrong_case(self):
  for case in ('01GTGT-sale10-half-M10-2026','01GTGT-sale10-manual-M10-2026','01GTGT-sale5-half-M10-2026','01GTGT-sale5-manual-M10-2026'):
   _,native,_,_=fixture(case)
   self.assertTrue(n.validate_native(native,case,TODAY)['privacyValuesVerified'])
   for name in (('ct31' if 'sale5-' in case else 'ct33'),'ct40'):
    with self.subTest(case=case,field=name),self.assertRaises(n.OutputError):n.validate_native(changed(native,name,'0'),case,TODAY)

 def test_five_percent_raw_bytes_cannot_be_relabelled_as_ten_percent(self):
  for five,ten in (('01GTGT-sale5-half-M10-2026','01GTGT-sale10-half-M10-2026'),('01GTGT-sale5-manual-M10-2026','01GTGT-sale10-manual-M10-2026')):
   for source,target in ((five,ten),(ten,five)):
    _,native,_,_=fixture(source)
    with self.subTest(source=source,target=target),self.assertRaises(n.OutputError):n.validate_native(native,target,TODAY)

 def test_both_cases_original_identity_historical_signature_fresh_created(self):
  for case in n.BRANCHES:
   web,native,_,_=fixture(case);raw=bytes(native)
   checked=n.validate_native(native,case,TODAY);self.assertEqual(checked['leafCount'],74);self.assertTrue(checked['nativeServiceIdentityVerified']);self.assertEqual(native,raw)
   self.assertTrue(n.compare_tax(web,native)['allTaxValuesMatched'])
 def test_unknown_comments_pi_dtd_and_entity_rejected_before_parser(self):
  native=fixture()[1]
  for extra in (b'<!-- secret -->',b'<?private x?>',b'<!DOCTYPE root>',b'<!ENTITY x "secret">'):
   with self.subTest(extra=extra),self.assertRaises(n.OutputError):n.validate_native(native+extra,next(iter(n.BRANCHES)),TODAY)
 def test_unknown_namespace_attribute_extra_leaf_and_private_values_rejected(self):
  native=fixture()[1]
  mutations=(native.replace(b'<HSoThueDTu ',b'<HSoThueDTu xmlns:secret="https://private.invalid/" '),native.replace(b'<ct22>',b'<ct22 private="secret">'),native.replace(b'</HSoKhaiThue>',b'<private>secret</private></HSoKhaiThue>'),changed(native,'tenNNT','PRIVATE CUSTOMER'))
  for body in mutations:
   with self.assertRaises((n.OutputError,n.privacy.EvidenceError)):n.validate_native(body,next(iter(n.BRANCHES)),TODAY)
 def test_service_identity_and_md5_shape_strict(self):
  native=fixture()[1]
  for name,value in (('maDVu','HTKK-WEB-DRAFT'),('tenDVu','PRIVATE'),('pbanDVu','5.8.2'),('ttinNhaCCapDVu','a'*32),('ttinNhaCCapDVu','A'*31)):
   with self.subTest(name=name),self.assertRaises(n.OutputError):n.validate_native(changed(native,name,value),next(iter(n.BRANCHES)),TODAY)
 def test_dates_fixed_signature_and_valid_fresh_iso_creation(self):
  native=fixture()[1]
  for name,value in (('ngayKy','2026-10-26'),('ngayKy','25/10/2026'),('ngayLapTKhai','2026-10-23'),('ngayLapTKhai','2026-02-31'),('ngayLapTKhai','26/10/2026'),('ngayLapTKhai','')):
   with self.subTest(name=name,value=value),self.assertRaises(n.OutputError):n.validate_native(changed(native,name,value),next(iter(n.BRANCHES)),TODAY)
  n.validate_native(changed(native,'ngayLapTKhai','2026-10-25'),next(iter(n.BRANCHES)),TODAY)
  n.validate_native(changed(native,'ngayLapTKhai','2026-10-27'),next(iter(n.BRANCHES)),TODAY)
 def test_exact_fixed_amounts_not_arbitrary_nonzero_or_zero_representations(self):
  for case in n.BRANCHES:
   native=fixture(case)[1]
   for name,value in (('ct22','1'),('ct32','999999'),('ct33','100001'),('ct43','0.0'),('ct21','false')):
    with self.subTest(case=case,name=name),self.assertRaises(n.OutputError):n.validate_native(changed(native,name,value),case,TODAY)
 def test_independent_full_tax_comparison_rejects_other_privacy_allowed_geography(self):
  web,native,_,_=fixture();native=changed(native,'maHuyenNNT','10129')
  n.validate_native(native,next(iter(n.BRANCHES)),TODAY)
  with self.assertRaises(n.OutputError) as error:n.compare_tax(web,native)
  self.assertEqual(error.exception.code,'COMPARE')
 def test_size_encoding_and_case_rejected(self):
  for body in (b'',b'x'*(n.reader.MAX_XML+1),b'\xff'):
   with self.assertRaises(n.OutputError):n.validate_native(body,next(iter(n.BRANCHES)),TODAY)
  with self.assertRaises(n.OutputError):n.validate_native(fixture()[1],'unknown',TODAY)

class ProvenanceTests(unittest.TestCase):
 def read(self,directory,**overrides):
  args={'run_id':'123','builder_commit':BUILDER_SHA,'source_commit':SOURCE,'case_id':next(iter(n.BRANCHES)),'artifact_commit':ARTIFACT,'today':TODAY};args.update(overrides)
  return n.read_evidence(directory,**args)
 def staged(self,directory,provenance=None,native=None):
  _,default,_,metadata=fixture();(directory/'01GTGT-native.xml').write_bytes(default if native is None else native);(directory/'provenance.json').write_text(json.dumps(metadata if provenance is None else provenance));return metadata
 def test_exact_raw_bytes_and_24_keys(self):
  with tempfile.TemporaryDirectory() as temporary:
   directory=pathlib.Path(temporary);metadata=self.staged(directory);body,observed=self.read(directory)
   self.assertEqual(body,fixture()[1]);self.assertEqual(observed,metadata);self.assertEqual(len(metadata),24)
 def test_missing_extra_false_wrong_typed_and_incomplete_provenance_rejected(self):
  base=fixture()[3]
  mutations=[]
  for name,value in base.items():
   if type(value) is bool:mutations.append({**base,name:not value});mutations.append({**base,name:int(value)})
  mutations.extend(({**base,'extra':'PRIVATE'},{k:v for k,v in base.items() if k!='originalProcessStopped'},{**base,'webTaxCheckedLeafCount':69},{**base,'originalOutputBytes':True},{**base,'creationDateRule':'ignore-any-date'},{**base,'sourceVersion':'5.8.2'}))
  for metadata in mutations:
   with tempfile.TemporaryDirectory() as temporary:
    directory=pathlib.Path(temporary);self.staged(directory,metadata)
    with self.assertRaises(n.OutputError):self.read(directory)
 def test_env_source_builder_run_case_artifact_and_raw_hash_pinned(self):
  for key,value in (('source_commit','d'*40),('builder_commit','d'*40),('run_id','124'),('case_id','01GTGT-sale10-M10-2026'),('artifact_commit','d'*40)):
   with self.subTest(key=key),tempfile.TemporaryDirectory() as temporary:
    directory=pathlib.Path(temporary);self.staged(directory)
    with self.assertRaises(n.OutputError):self.read(directory,**{key:value})
  with tempfile.TemporaryDirectory() as temporary:
   directory=pathlib.Path(temporary);self.staged(directory);(directory/'01GTGT-native.xml').write_bytes(changed(fixture()[1],'ct22','1'))
   with self.assertRaises(n.OutputError):self.read(directory)
 def test_stage_whitelist_symlink_and_oversize_files_rejected(self):
  for mutation in ('extra','missing','symlink','oversize'):
   with self.subTest(mutation=mutation),tempfile.TemporaryDirectory() as temporary:
    root=pathlib.Path(temporary);directory=root/'stage';directory.mkdir();self.staged(directory)
    if mutation=='extra':(directory/'PRIVATE').write_text('secret')
    elif mutation=='missing':(directory/'provenance.json').unlink()
    elif mutation=='oversize':(directory/'provenance.json').write_bytes(b'x'*(n.reader.MAX_MANIFEST+1))
    else:
     source=directory/'01GTGT-native.xml';target=root/'target';source.rename(target);source.symlink_to(target)
    with self.assertRaises((n.OutputError,n.transport.PublicationError)):self.read(directory)

class PublishTests(unittest.TestCase):
 def test_each_case_immutable_input_checked_before_byte_exact_orphan_publication(self):
  for case,branch in n.BRANCHES.items():
   web,native,metadata,provenance=fixture(case);fetch,calls=fake_api(web,metadata);result=n.publish(native,provenance,'synthetic-token',fetch,TODAY)
   self.assertEqual(result['artifactCommit'],'e'*40);self.assertEqual(result['nativeOutputSha256'],hashlib.sha256(native).hexdigest())
   blobs=[base64.b64decode(body['content']) for path,_,body,_ in calls if path=='/git/blobs'];self.assertEqual(blobs[0],native)
   manifest=json.loads(blobs[1]);self.assertEqual(manifest['provenance'],provenance);self.assertEqual(manifest['sourcePins'],n.PINS);self.assertFalse(manifest['independentSchemaVerification']);self.assertFalse(manifest['fullRoundTrip']);self.assertEqual(manifest['comparison']['checkedTaxLeafCount'],70)
   self.assertIn(('/git/commits/'+ARTIFACT,'synthetic-token',None,None),calls)
   self.assertTrue(all('?ref='+ARTIFACT in path for path,_,_,_ in calls if path.startswith('/contents/')))
   commit=next(body for path,_,body,_ in calls if path=='/git/commits');self.assertEqual(commit['parents'],[])
   self.assertIn(('/git/refs/heads/'+branch,'synthetic-token',{'sha':'e'*40,'force':True},'PATCH'),calls)
   self.assertNotIn('synthetic-token',json.dumps(result));self.assertNotIn('NNT KIEM',json.dumps(result))
 def test_get404_creates_but_never_patch_fallback_on422_or_auth(self):
  web,native,metadata,provenance=fixture();fetch,calls=fake_api(web,metadata,existing=False);n.publish(native,provenance,'synthetic-token',fetch,TODAY)
  self.assertTrue(any(path=='/git/refs' for path,_,_,_ in calls));self.assertFalse(any(method=='PATCH' for _,_,_,method in calls))
  for code in (401,403,404,422,500):
   fetch,calls=fake_api(web,metadata)
   def denied(path,token,payload=None,method=None):
    if method=='PATCH':calls.append((path,token,payload,method));raise urllib.error.HTTPError('https://api.github.com/',code,'PRIVATE REMOTE TEXT',{},None)
    return fetch(path,token,payload,method)
   with self.subTest(code=code),self.assertRaises(urllib.error.HTTPError):n.publish(native,provenance,'synthetic-token',denied,TODAY)
   self.assertEqual(sum(method=='PATCH' for _,_,_,method in calls),1);self.assertFalse(any(path=='/git/refs' for path,_,_,_ in calls))
 def test_public_or_wrong_repo_no_source_read_or_writes(self):
  web,native,metadata,provenance=fixture()
  for info in ({'private':False,'full_name':n.REPO},{'private':True,'full_name':'wrong/repo'}):
   fetch,calls=fake_api(web,metadata,info=info)
   with self.assertRaises(n.reader.InputError):n.publish(native,provenance,'synthetic-token',fetch,TODAY)
   self.assertEqual(len(calls),1)
 def test_immutable_input_source_case_and_hash_must_match_before_writes(self):
  web,native,metadata,provenance=fixture()
  for mutation in ('source','case','hash','artifact'):
   changed_metadata=dict(metadata);changed_provenance=dict(provenance)
   if mutation=='source':changed_metadata['sourceCommit']='d'*40
   elif mutation=='case':changed_metadata.update(caseId='01GTGT-sale10-M10-2026',format='htkk-web-sale10-input-v1')
   elif mutation=='hash':changed_provenance['webImportInputSha256']='f'*64
   fetch,calls=fake_api(web,changed_metadata)
   def altered(path,token,payload=None,method=None):
    if mutation=='artifact' and path=='/git/commits/'+ARTIFACT:return {'sha':'f'*40}
    return fetch(path,token,payload,method)
   with self.subTest(mutation=mutation),self.assertRaises((n.OutputError,n.reader.InputError)):n.publish(native,changed_provenance,'synthetic-token',altered,TODAY)
   self.assertFalse(any(payload is not None for _,_,payload,_ in calls))
 def test_native_tax_difference_rejected_before_publication_despite_provenance_flags(self):
  web,native,metadata,provenance=fixture();native=changed(native,'maHuyenNNT','10129');provenance.update(originalOutputSha256=hashlib.sha256(native).hexdigest(),originalOutputBytes=len(native));fetch,calls=fake_api(web,metadata)
  with self.assertRaises(n.OutputError) as error:n.publish(native,provenance,'synthetic-token',fetch,TODAY)
  self.assertEqual(error.exception.code,'COMPARE');self.assertFalse(any(payload is not None for _,_,payload,_ in calls))
 def test_invalid_native_or_incomplete_flags_rejected_before_network(self):
  web,native,metadata,provenance=fixture()
  for mutation in ('flag','xml'):
   observed=dict(provenance);body=native;fetch,calls=fake_api(web,metadata)
   if mutation=='flag':observed['originalProcessStopped']=False
   else:body=native+b'<!-- secret -->';observed.update(originalOutputSha256=hashlib.sha256(body).hexdigest(),originalOutputBytes=len(body))
   with self.assertRaises(n.OutputError):n.publish(body,observed,'synthetic-token',fetch,TODAY)
   self.assertFalse(calls)
 def test_auth_not_retried_and_errors_never_publish_remote_body_or_credentials(self):
  web,native,metadata,provenance=fixture();calls=[]
  def denied(*args):calls.append(args);raise urllib.error.HTTPError('https://api.github.com/',403,'SECRET PRIVATE REMOTE BODY',{},None)
  with self.assertRaises(urllib.error.HTTPError) as error:n.publish(native,provenance,'synthetic-token',denied,TODAY)
  self.assertEqual(len(calls),1);report=json.dumps(n.safe_failure(error.exception));self.assertNotIn('SECRET',report);self.assertNotIn('synthetic-token',report)
  self.assertIsNone(n.transport.NoRedirect().redirect_request(None,None,None,None,None,None))
 def test_default_api_is_bounded_no_redirect_shared_transport(self):
  web,native,metadata,provenance=fixture();fetch,_=fake_api(web,metadata)
  with patch.object(n.transport,'api',side_effect=fetch) as api:n.publish(native,provenance,'synthetic-token',today=TODAY)
  self.assertEqual(api.call_args_list[0].args,('', 'synthetic-token'))

if __name__=='__main__':unittest.main()
