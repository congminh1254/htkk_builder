"""Offline parser/publication fixtures only, never native output evidence."""
import base64,copy,datetime,hashlib,importlib.util,json,pathlib,tempfile,unittest,urllib.error
from unittest.mock import patch

def module(name,file):
 spec=importlib.util.spec_from_file_location(name,pathlib.Path(__file__).with_name(file));value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
p=module('sample_under_test','publish-htkk-native-sample.py')
f=module('sample_parser_fixtures','test_gtgt_export_evidence.py')
TODAY=f.TODAY
class SampleTests(unittest.TestCase):
 def fixture(self):
  body=f.parser_fixture();files={name:body for name in p.XMLS}
  schema={'format':'htkk-native-sample-schema-v1','valid':True,'engine':'System.Xml.Schema/PowerShell7','schemaPins':p.annex.SCHEMA_PINS,'files':p.describe(files)}
  return files,p.expected(files,'a'*40,'b'*40,'123','2',schema)
 def test_complete_tree_and_money_checked_without_normalization(self):
  files,metadata=self.fixture();before=copy.deepcopy(files);result=p.validate(files,metadata,TODAY)
  self.assertTrue(result['allLeavesMatched']);self.assertEqual(result['normalizations'],[]);self.assertEqual(result['moneyCount'],27);self.assertEqual(files,before)
  self.assertFalse(metadata['fullCompatibilityVerified']);self.assertFalse(metadata['filingReady'])
 def test_every_original_leaf_is_revalidated_not_just_schema_or_hash(self):
  files,_=self.fixture()
  for name,value in (('mst','1234567890'),('ct22','1'),('nguoiKy','PRIVATE'),('ngayKy','2026-10-24'),('ttinNhaCCapDVu','B'*32)):
   with self.subTest(name=name):
    altered=dict(files);altered[p.XMLS[1]]=f.change(altered[p.XMLS[1]],name,value)
    schema={'format':'htkk-native-sample-schema-v1','valid':True,'engine':'System.Xml.Schema/PowerShell7','schemaPins':p.annex.SCHEMA_PINS,'files':p.describe(altered)}
    metadata=p.expected(altered,'a'*40,'b'*40,'123','2',schema)
    with self.assertRaises((p.SampleError,p.privacy.EvidenceError)):p.validate(altered,metadata,TODAY)
 def test_false_numeric_unknown_or_mismatched_provenance_rejected(self):
  files,metadata=self.fixture()
  for key,value in (('supplierStopped',False),('originalImportSucceeded',1),('runAttempt','0'),('sourceCommit','x'*40),('filingReady',True),('extra','PRIVATE')):
   with self.subTest(key=key):
    altered=copy.deepcopy(metadata);altered[key]=value
    with self.assertRaises(p.SampleError):p.validate(files,altered,TODAY)
 def test_schema_report_false_or_hash_mismatch_rejected(self):
  files,metadata=self.fixture()
  for edit in (lambda v:v.update(valid=1),lambda v:v.update(valid=False),lambda v:v['files'][p.XMLS[0]].update(sha256='c'*64),lambda v:v.update(extra='PRIVATE')):
   altered=copy.deepcopy(metadata);edit(altered['schema'])
   with self.assertRaises(p.SampleError):p.validate(files,altered,TODAY)
 def test_read_exact_run_attempt_no_extra_files_or_symlink(self):
  files,metadata=self.fixture()
  with tempfile.TemporaryDirectory() as temporary:
   d=pathlib.Path(temporary)
   for name,body in {**files,'provenance.json':json.dumps(metadata).encode()}.items():(d/name).write_bytes(body)
   self.assertEqual(p.read(d,'a'*40,'b'*40,'123','2',TODAY),(files,metadata))
   with self.assertRaises(p.SampleError):p.read(d,'a'*40,'b'*40,'123','1',TODAY)
   (d/'extra').write_text('PRIVATE')
   with self.assertRaises(p.SampleError):p.read(d,'a'*40,'b'*40,'123','2',TODAY)
   (d/'extra').unlink();(d/p.XMLS[0]).unlink();(d/p.XMLS[0]).symlink_to(d/p.XMLS[1])
   with self.assertRaises(Exception):p.read(d,'a'*40,'b'*40,'123','2',TODAY)
 def test_unsafe_metadata_rejected_before_first_network_request(self):
  files,metadata=self.fixture();metadata['supplierStopped']=False
  with patch.object(p.transport,'api') as fetch:
   with self.assertRaises(p.SampleError):p.publish(files,metadata,'TEST',today=TODAY)
   fetch.assert_not_called()
 def fake_api(self,public=False,stale=False,corrupt=False,ref_error=None):
  calls=[];blobs={};tree='d'*40;artifact='e'*40
  def fetch(path,token,body=None,method=None):
   calls.append((path,body,method))
   if path=='':return {'private':not public,'full_name':p.REPO}
   if path=='/git/ref/heads/main':return {'ref':'refs/heads/main','object':{'sha':('f' if stale else 'a')*40,'type':'commit'}}
   if path=='/git/blobs':
    raw=base64.b64decode(body['content']);digest=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest();blobs[digest]=raw;return {'sha':digest}
   if path=='/git/trees':return {'sha':tree}
   if path=='/git/commits':return {'sha':artifact}
   if path=='/git/ref/heads/'+p.BRANCH:
    if ref_error:raise urllib.error.HTTPError('https://api.github.com/',ref_error,'',{},None)
    return {'ref':'refs/heads/'+p.BRANCH,'object':{'sha':'c'*40,'type':'commit'}}
   if path in ('/git/refs/heads/'+p.BRANCH,'/git/refs'):return {'ref':'refs/heads/'+p.BRANCH,'object':{'sha':artifact,'type':'commit'}}
   if path=='/git/commits/'+artifact:return {'sha':artifact,'tree':{'sha':tree}}
   if path.startswith('/git/blobs/'):
    raw=blobs[path.rsplit('/',1)[1]]
    return {'encoding':'base64','content':base64.b64encode(raw+(b'BAD' if corrupt else b'')).decode()}
   if path=='/statuses/'+'a'*40:return {}
   raise AssertionError(path)
  return fetch,calls
 def test_private_publication_rereads_blobs_before_separate_status(self):
  files,metadata=self.fixture();fetch,calls=self.fake_api();result=p.publish(files,metadata,'TEST',fetch,TODAY)
  self.assertEqual(result['status'],'published');self.assertEqual(calls[-1][0],'/statuses/'+'a'*40);self.assertEqual(calls[-1][1]['context'],p.CONTEXT)
  self.assertEqual(sum(path.startswith('/git/blobs/') for path,_,_ in calls),3)
 def test_public_or_stale_source_never_writes_objects_or_status(self):
  files,metadata=self.fixture()
  for kwargs in ({'public':True},{'stale':True}):
   fetch,calls=self.fake_api(**kwargs)
   with self.assertRaises(p.SampleError):p.publish(files,metadata,'TEST',fetch,TODAY)
   self.assertFalse(any(body is not None for _,body,_ in calls))
 def test_corrupt_retention_cannot_report_success(self):
  files,metadata=self.fixture();fetch,calls=self.fake_api(corrupt=True)
  with self.assertRaises(p.SampleError):p.publish(files,metadata,'TEST',fetch,TODAY)
  self.assertFalse(any(path.startswith('/statuses/') for path,_,_ in calls))
 def test_only_404_allows_create_ref(self):
  files,metadata=self.fixture()
  for status in (401,403,422,500):
   fetch,calls=self.fake_api(ref_error=status)
   with self.assertRaises(urllib.error.HTTPError):p.publish(files,metadata,'TEST',fetch,TODAY)
   self.assertFalse(any(path=='/git/refs' or path.startswith('/statuses/') for path,_,_ in calls))
  fetch,calls=self.fake_api(ref_error=404);p.publish(files,metadata,'TEST',fetch,TODAY)
  self.assertTrue(any(path=='/git/refs' for path,_,_ in calls))
 def test_workflow_and_probe_keep_new_helpers_before_credentials(self):
  root=pathlib.Path(__file__).resolve().parents[1];probe=(root/'scripts/probe-htkk-windows.ps1').read_text();workflow=(root/'.github/workflows/probe-htkk-windows.yml').read_text()
  self.assertLess(probe.index("'Test-HtkkNativeSampleSchema.ps1'"),probe.index("'credentials_safe='"))
  self.assertIn('-TimeoutMilliseconds 30000',probe);self.assertIn('steps.native_probe.outcome == \'success\'',workflow)
  self.assertIn('steps.native_probe.outputs.supplier_stopped == \'true\'',workflow)
  script=(root/'scripts/Test-HtkkNativeSampleSchema.ps1').read_text()
  for requirement in ('DtdProcessing]::Prohibit','XmlResolver=$null','MaxCharactersInDocument=262144','Schema=$signature','Schema=$common','ValidationType=[Xml.ValidationType]::Schema'):
   self.assertIn(requirement,script)

class SampleStatusTests(unittest.TestCase):
 def test_pending_failure_only_exact_private_current_source_and_attempt(self):
  report=module('sample_status_test','report-native-sample.py')
  for state in ('pending','failure'):
   calls=[]
   def fetch(path,token,body=None):
    calls.append((path,body))
    if path=='':return {'private':True,'full_name':p.REPO}
    if path=='/git/ref/heads/main':return {'ref':'refs/heads/main','object':{'type':'commit','sha':'a'*40}}
    return {}
   report.report(state,'a'*40,'b'*40,'123','2','TEST',fetch)
   self.assertEqual(calls[-1][1]['state'],state);self.assertEqual(calls[-1][1]['context'],p.CONTEXT);self.assertTrue(calls[-1][1]['target_url'].endswith('/123/attempts/2'))
   self.assertIn('bbbbbbbbbbbb',calls[-1][1]['description'])
  for state in ('success','error',None):
   with self.assertRaises(report.p.SampleError):report.report(state,'a'*40,'b'*40,'123','2','TEST',fetch)

if __name__=='__main__':unittest.main()
