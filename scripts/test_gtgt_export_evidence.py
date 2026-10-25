"""Offline synthetic PARSER fixtures only; never represent native HTKK output."""
import copy,datetime,hashlib,importlib.util,json,pathlib,tempfile,unittest,urllib.error
from unittest.mock import patch
import xml.etree.ElementTree as ET
spec=importlib.util.spec_from_file_location('gtgt_evidence',pathlib.Path(__file__).with_name('publish-gtgt-export-evidence.py'))
e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
TODAY=datetime.date(2026,10,25)
def parser_fixture(keep_optional=False):
 root=ET.Element('{'+e.NS+'}HSoThueDTu');ET.register_namespace('',e.NS);ET.register_namespace('xsi',e.XSI)
 def children(node,path):
  for name in e.SHAPE.get(path,()):
   child_path=path+'/'+name if path else name
   if child_path in e.OPTIONAL and not keep_optional:continue
   child=ET.SubElement(node,'{'+e.NS+'}'+name)
   if child_path=='HSoKhaiThue':child.set('id','ID_1')
   if child_path in e.SHAPE:children(child,child_path)
   elif child_path=='HSoKhaiThue/PLuc':pass
   else:
    allowed=e.EXPECTED[child_path]
    child.text='A'*32 if '@SOURCE_MD5' in allowed else TODAY.isoformat() if '@DATE' in allowed else '' if '@OPTIONAL_DATE' in allowed else '0' if '@ZERO' in allowed else allowed[0]
 children(root,'');return ET.tostring(root,encoding='utf-8',xml_declaration=True)
def change(body,name,value):
 root=ET.fromstring(body);node=root.find('.//{'+e.NS+'}'+name);node.text=value;return ET.tostring(root,encoding='utf-8')
def stage(directory,body):
 p={'format':'htkk-gtgt-export-staging-v1','builderRepository':e.BUILDER,'builderCommit':'a'*40,'runId':'123','sourceVersion':'5.8.1','runtimeHost':'clr2-x86-reference','originalSourcesUnmodified':True,'inputsSynthetic':True,'guiExportInvoked':True,'originalExportSucceeded':True,'originalExporterValidatedSchema':True,'fullRoundTrip':False,'originalOutputSha256':hashlib.sha256(body).hexdigest(),'originalOutputBytes':len(body)}
 (directory/'01GTGT.xml').write_bytes(body);(directory/'provenance.json').write_text(json.dumps(p));return p
class XmlPrivacyTests(unittest.TestCase):
 def setUp(self):self.body=parser_fixture()
 def reject(self,body,reason=None):
  with self.assertRaises(e.EvidenceError) as caught:e.validate_xml(body,TODAY)
  if reason:self.assertEqual(caught.exception.reason,reason)
 def test_zero_parser_fixture_and_optional_empty_branches(self):
  self.assertTrue(e.validate_xml(self.body,TODAY)['privacyValuesVerified'])
  self.assertGreater(e.validate_xml(parser_fixture(True),TODAY)['leafCount'],e.validate_xml(self.body,TODAY)['leafCount'])
 def test_unchanged_bytes_preserved_by_staging(self):
  with tempfile.TemporaryDirectory() as temporary:
   directory=pathlib.Path(temporary);stage(directory,self.body)
   files=e.read_evidence(directory,'123','a'*40,TODAY);self.assertEqual(files['01GTGT.xml'],self.body)
   manifest=json.loads(files['manifest.json']);self.assertFalse(manifest['fullRoundTrip']);self.assertFalse(manifest['independentSchemaVerification']);self.assertFalse(manifest['htkkImportPassed']);self.assertTrue(manifest['guiExportInvoked'])
 def test_real_taxpayer_value_rejected(self):
  for name in ('mst','tenNNT','dchiNNT','nguoiKy','emailNNT','ma_NganhNghe'):
   with self.subTest(name=name):self.reject(change(self.body,name,'PRIVATE UNEXPECTED VALUE'),'VALUE_MISMATCH')
 def test_nonzero_and_true_rejected(self):
  for name,value in (('ct22','1'),('ct43','-0'),('ct24','1e-999'),('ct21','true')):
   with self.subTest(name=name):self.reject(change(self.body,name,value),'VALUE_MISMATCH')
 def test_supplier_must_be_uppercase_md5_shape(self):
  for value in ('A'*31,'a'*32,'arbitrary vendor text','A'*33):self.reject(change(self.body,'ttinNhaCCapDVu',value),'VALUE_MISMATCH')
 def test_dates_valid_fresh_and_no_implicit_rollover(self):
  for value,reason in (('2026-02-31','DATE_VALUE'),('2026-10-20','DATE_STALE'),('yesterday','DATE_VALUE')):self.reject(change(self.body,'ngayKy',value),reason)
  e.validate_xml(change(self.body,'ngayKy','25/10/2026'),TODAY)
 def test_dtd_entities_comments_pi_rejected(self):
  for fragment in (b'<!DOCTYPE x>',b'<!-- secret -->',b'<?secret raw?>',b'<!ENTITY x "private">'):
   self.reject(fragment+self.body,'DECLARATION')
 def test_unknown_namespace_attribute_and_node_rejected(self):
  root=ET.fromstring(self.body);root.set('private','raw');self.reject(ET.tostring(root),'ATTRIBUTES')
  root=ET.fromstring(self.body);ET.SubElement(root,'{'+e.NS+'}private').text='secret';self.reject(ET.tostring(root),'STRUCTURE')
  self.reject(self.body.replace(e.NS.encode(),b'https://attacker.invalid/ns'),'NAMESPACE')
 def test_duplicate_reorder_and_nonempty_container_rejected(self):
  root=ET.fromstring(self.body);root.append(copy.deepcopy(root[0]));self.reject(ET.tostring(root),'STRUCTURE')
  root=ET.fromstring(self.body);root[0][0],root[0][1]=root[0][1],root[0][0];self.reject(ET.tostring(root),'STRUCTURE')
  root=ET.fromstring(self.body);root.text='secret';self.reject(ET.tostring(root),'XML_CONTENT')
 def test_size_encoding_and_mixed_tail_rejected(self):
  self.reject(b'x'*(e.MAX_XML+1),'SIZE');self.reject(b'\xff','ENCODING')
  root=ET.fromstring(self.body);root[0].tail='secret';self.reject(ET.tostring(root),'XML_CONTENT')
 def test_empty_leaf_indentation_allowed_only_for_expected_empty(self):
  e.validate_xml(change(self.body,'emailNNT','\n  '),TODAY)
  self.reject(change(self.body,'tenNNT','\n  '),'VALUE_MISMATCH')
class ProvenanceAndPublicationTests(unittest.TestCase):
 def setUp(self):self.body=parser_fixture()
 def test_false_or_numeric_attestations_hash_and_unknown_fields_rejected(self):
  for key,value in (('originalExportSucceeded',False),('inputsSynthetic',1),('originalOutputSha256','b'*64),('fullRoundTrip',True),('extra','secret')):
   with self.subTest(key=key),tempfile.TemporaryDirectory() as temporary:
    d=pathlib.Path(temporary);p=stage(d,self.body);p[key]=value;(d/'provenance.json').write_text(json.dumps(p))
    with self.assertRaises(e.EvidenceError):e.read_evidence(d,'123','a'*40,TODAY)
 def test_extra_missing_or_symlink_file_rejected(self):
  with tempfile.TemporaryDirectory() as temporary:
   d=pathlib.Path(temporary);stage(d,self.body);(d/'extra.txt').write_text('secret')
   with self.assertRaises(e.EvidenceError):e.read_evidence(d,'123','a'*40,TODAY)
   (d/'extra.txt').unlink();(d/'01GTGT.xml').unlink();(d/'01GTGT.xml').symlink_to(d/'provenance.json')
   with self.assertRaises(e.EvidenceError):e.read_evidence(d,'123','a'*40,TODAY)
 def files(self):
  with tempfile.TemporaryDirectory() as temporary:
   d=pathlib.Path(temporary);stage(d,self.body);return e.read_evidence(d,'123','a'*40,TODAY)
 def test_public_or_wrong_repo_never_writes_git_objects(self):
  for info in ({'private':False,'full_name':e.REPO},{'private':True,'full_name':'other/repo'}):
   with self.subTest(info=info),patch.object(e,'validate_xml',return_value={'leafCount':74,'privacyValuesVerified':True}):
    files=self.files();privacy=json.loads(files['manifest.json'])['privacyCheck']
    with patch.object(e,'validate_xml',return_value=privacy),patch.object(e,'api',return_value=info) as api:
     with self.assertRaises(e.EvidenceError):e.publish(files,'synthetic-token')
     self.assertEqual(api.call_count,1);self.assertEqual(api.call_args.args[0],'')
 def test_manifest_injection_rejected_before_network(self):
  files=self.files();m=json.loads(files['manifest.json']);m['secret']='PRIVATE';files['manifest.json']=json.dumps(m).encode()
  with patch.object(e,'validate_xml',return_value=m['privacyCheck']),patch.object(e,'api') as api:
   with self.assertRaises(e.EvidenceError):e.publish(files,'synthetic-token')
   api.assert_not_called()
 def test_private_orphan_branch_only_preserves_original_bytes(self):
  files=self.files();privacy=json.loads(files['manifest.json'])['privacyCheck'];calls=[]
  def api(path,token,payload=None,method=None):
   calls.append((path,payload,method));self.assertEqual(token,'synthetic-token')
   if path=='':return {'private':True,'full_name':e.REPO}
   if path.startswith('/git/ref/heads/'):raise urllib.error.HTTPError('https://api.github.com/',404,'not found',{},None)
   return {'sha':'b'*40}
  with patch.object(e,'validate_xml',return_value=privacy),patch.object(e,'api',side_effect=api):self.assertEqual(e.publish(files,'synthetic-token'),'b'*40)
  self.assertEqual(calls[-1][1],{'ref':'refs/heads/'+e.BRANCH,'sha':'b'*40})
  self.assertEqual(next(x[1]['parents'] for x in calls if x[0]=='/git/commits'),[])
  self.assertFalse(any('main' in path or 'pages-output' in path for path,_,_ in calls))
 def test_safe_failure_never_contains_values_or_raw_remote_message(self):
  error=e.EvidenceError('VALUE_MISMATCH',leafIndex=3,valueShape='other',raw='PRIVATE')
  self.assertNotIn('PRIVATE',json.dumps(e.safe_failure(error,'read')))
  self.assertEqual(e.safe_failure(ValueError('PRIVATE TOKEN XML PATH'),'publish')['reason'],'INTERNAL')
if __name__=='__main__':unittest.main()
