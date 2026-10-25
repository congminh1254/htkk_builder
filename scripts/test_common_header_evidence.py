"""Offline privacy and publication boundary tests; no supplier runtime or network."""
import base64,datetime,importlib.util,json,pathlib,tempfile,unittest,urllib.error
import xml.etree.ElementTree as ET
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('common_header_evidence',pathlib.Path(__file__).with_name('publish-common-header-evidence.py'))
evidence=importlib.util.module_from_spec(spec);spec.loader.exec_module(evidence)
TODAY=datetime.date(2026,10,25)

def synthetic(index):
 root=ET.Element('TTinChung')
 for path,value in evidence.LEAVES.items():
  node=root
  for part in path.split('/'):
   child=node.find(part)
   if child is None:child=ET.SubElement(node,part)
   node=child
  if path.endswith('/loaiTKhai'):value=('C','B')[index]
  elif path.endswith('/soLan'):value=str(index)
  elif path.endswith('/ngayKy'):value='25/10/2026'
  node.text=value
 return ET.tostring(root,encoding='utf-8',xml_declaration=True)

class EvidenceFilesTests(unittest.TestCase):
 def setUp(self):
  self.temporary=tempfile.TemporaryDirectory();self.directory=pathlib.Path(self.temporary.name)
  for index,name in enumerate(evidence.NAMES):(self.directory/name).write_bytes(synthetic(index))
 def tearDown(self):self.temporary.cleanup()
 def read(self):return evidence.read_evidence(self.directory,'40190903143','a'*40,TODAY)
 def test_preserves_original_bytes_and_records_narrow_scope_with_provenance(self):
  result=self.read()
  for index,name in enumerate(evidence.NAMES):self.assertEqual(result[name],synthetic(index))
  manifest=json.loads(result['manifest.json']);self.assertTrue(manifest['inputsSynthetic']);self.assertFalse(manifest['fullRoundTrip']);self.assertFalse(manifest['guiExportInvoked']);self.assertEqual(manifest['sourceVersion'],'5.8.1');self.assertEqual(manifest['builderCommit'],'a'*40)
  self.assertEqual(set(manifest['helperSha256']),{'scripts/'+name for name in evidence.HELPERS});self.assertEqual(set(manifest['files']),set(evidence.NAMES))
 def test_rejects_extra_files_oversize_and_symlink(self):
  extra=self.directory/'private-source.log';extra.write_text('must never publish')
  with self.assertRaises(ValueError):self.read()
  extra.unlink();first=self.directory/evidence.NAMES[0];first.write_bytes(b'x'*65537)
  with self.assertRaises(ValueError):self.read()
  first.unlink();target=self.directory.parent/(self.directory.name+'-target');target.write_bytes(synthetic(0))
  try:
   first.symlink_to(target)
   with self.assertRaises(ValueError):self.read()
  finally:target.unlink()
 def test_rejects_real_taxpayer_values_unknown_nodes_attributes_and_duplicate_leaves(self):
  original=synthetic(0)
  bad=[original.replace(b'9999999997',b'1234567890'),original.replace(b'SYNTHETIC SIGNER',b'PRIVATE_PERSON'),original.replace(b'</TTinChung>',b'<credentials>secret</credentials></TTinChung>'),original.replace(b'<TTinChung>',b'<TTinChung token="secret">'),original.replace(b'<mst>9999999997</mst>',b'<mst>9999999997</mst><mst>9999999997</mst>')]
  for item in bad:
   with self.subTest(item=item[:30]),self.assertRaises(ValueError):evidence.validate_xml(item,0,TODAY)
 def test_rejects_dtd_entities_comments_processing_instructions_and_invalid_date(self):
  original=synthetic(0)
  bad=[b'<!DOCTYPE TTinChung [<!ENTITY x SYSTEM "https://example.com/secret">]>'+original,original.replace(b'<TTinChung>',b'<TTinChung><!-- private -->'),original.replace(b'<TTinChung>',b'<TTinChung><?private secret?>'),original.replace(b'25/10/2026',b'31/02/2026'),original.replace(b'25/10/2026',b'25/10/2020')]
  for item in bad:
   with self.assertRaises(ValueError):evidence.validate_xml(item,0,TODAY)
 def test_requires_correct_declaration_mode_and_exact_version(self):
  for changed in [synthetic(0).replace(b'<maTKhai>842',b'<maTKhai>999'),synthetic(0).replace(b'2.8.3',b'2.8.4'),synthetic(1)]:
   with self.assertRaises(ValueError):evidence.validate_xml(changed,0,TODAY)
 def test_rejects_wrong_run_or_commit_and_inconsistent_dates(self):
  for run,commit in [('1;bad','a'*40),('42','main')]:
   with self.assertRaises(ValueError):evidence.read_evidence(self.directory,run,commit,TODAY)
  second=self.directory/evidence.NAMES[1];second.write_bytes(synthetic(1).replace(b'25/10/2026',b'24/10/2026'))
  with self.assertRaises(ValueError):self.read()

class SafeDiagnosticTests(unittest.TestCase):
 def test_value_failure_exposes_only_enum_fixed_leaf_index_and_file_index(self):
  secret='private-token-and-person'
  body=synthetic(0).replace(b'SYNTHETIC SIGNER',secret.encode())
  with self.assertRaises(evidence.EvidenceError) as rejected:evidence.validate_xml(body,0,TODAY)
  safe=evidence.safe_failure(rejected.exception,'read')
  self.assertEqual(safe['reason'],'VALUE_MISMATCH');self.assertEqual(safe['leafIndex'],list(evidence.LEAVES).index('TTinTKhaiThue/TKhaiThue/nguoiKy')+1)
  self.assertNotIn(secret,json.dumps(safe));self.assertNotIn('nguoiKy',json.dumps(safe))
 def test_unknown_xml_names_or_malformed_contents_never_appear_in_diagnostic(self):
  for body in [synthetic(0).replace(b'</TTinChung>',b'<SECRET_NODE>PRIVATE_VALUE</SECRET_NODE></TTinChung>'),b'<TTinChung><SECRET_NODE>PRIVATE_VALUE</wrong>']:
   with self.assertRaises(evidence.EvidenceError) as rejected:evidence.validate_xml(body,0,TODAY)
   text=json.dumps(evidence.safe_failure(rejected.exception,'read'));self.assertNotIn('SECRET_NODE',text);self.assertNotIn('PRIVATE_VALUE',text)
 def test_date_diagnostics_reveal_shape_only_not_original_date_or_parser_exception(self):
  for raw,reason,shape in [(b'2026-10-25','DATE_FORMAT','yyyy-mm-dd'),(b'31/02/2026','DATE_VALUE','dd-mm-yyyy-slashes'),(b'PRIVATE_DATE','DATE_FORMAT','other')]:
   with self.assertRaises(evidence.EvidenceError) as rejected:evidence.validate_xml(synthetic(0).replace(b'25/10/2026',raw),0,TODAY)
   safe=evidence.safe_failure(rejected.exception,'read');self.assertEqual(safe['reason'],reason);self.assertEqual(safe['dateShape'],shape);self.assertNotIn(raw.decode(),json.dumps(safe))
 def test_arbitrary_exceptions_api_errors_and_tampered_context_cannot_log_strings(self):
  error=urllib.error.HTTPError('https://example.test/PRIVATE_TOKEN',403,'PRIVATE_MESSAGE',{},None)
  safe=evidence.safe_failure(error,'publish');self.assertEqual(safe['reason'],'API_AUTH');self.assertEqual(safe['httpStatus'],403);self.assertNotIn('PRIVATE',json.dumps(safe))
  self.assertEqual(evidence.safe_failure(ValueError('PRIVATE_VALUE'),'PRIVATE_STAGE')['reason'],'INTERNAL')
  error=evidence.EvidenceError('STRUCTURE',leafIndex=1);error.reason=['PRIVATE_VALUE'];error.context={'leafIndex':'PRIVATE','dateShape':{},'arbitrary':'PRIVATE','observedLeafCount':99999}
  safe=evidence.safe_failure(error,'read');self.assertEqual(safe['reason'],'INTERNAL');self.assertNotIn('PRIVATE',json.dumps(safe));self.assertNotIn('observedLeafCount',safe)

class PublicationTests(unittest.TestCase):
 def files(self):return {**{name:synthetic(index) for index,name in enumerate(evidence.NAMES)},'manifest.json':b'{"scope":"test"}'}
 def test_public_or_wrong_repository_denied_before_any_blob_write(self):
  for info in [{'private':False,'full_name':evidence.REPO},{'private':True,'full_name':'attacker/repo'},{'private':'true','full_name':evidence.REPO}]:
   with patch.object(evidence,'api',return_value=info) as api,self.assertRaises(ValueError):evidence.publish(self.files(),'synthetic-token')
   api.assert_called_once_with('','synthetic-token')
 def test_only_dedicated_fixed_branch_can_be_updated_and_commit_is_orphan(self):
  calls=[]
  def api(path,token,payload=None,method=None):
   calls.append((path,payload,method))
   if path=='':return {'private':True,'full_name':evidence.REPO}
   return {'sha':'b'*40}
  with patch.object(evidence,'api',api):self.assertEqual(evidence.publish(self.files(),'synthetic-token'),'b'*40)
  self.assertEqual(calls[-1],('/git/refs/heads/common-header-reference-evidence',{'sha':'b'*40,'force':True},'PATCH'))
  commit=next(payload for path,payload,_ in calls if path=='/git/commits');self.assertEqual(commit['parents'],[])
  tree=next(payload for path,payload,_ in calls if path=='/git/trees');self.assertEqual({entry['path'] for entry in tree['tree']},set(evidence.NAMES)|{'manifest.json'})
  self.assertTrue(all('main' not in path and 'pages-output' not in path for path,_,_ in calls))
 def test_branch_created_only_on_404_and_invalid_files_never_reach_api(self):
  calls=[]
  def api(path,token,payload=None,method=None):
   calls.append((path,payload))
   if path=='':return {'private':True,'full_name':evidence.REPO}
   if path=='/git/ref/heads/'+evidence.BRANCH:raise urllib.error.HTTPError('https://api.github.com/fixed',404,'not found',{},None)
   return {'sha':'c'*40}
  with patch.object(evidence,'api',api):evidence.publish(self.files(),'synthetic-token')
  self.assertEqual(calls[-1],('/git/refs',{'ref':'refs/heads/common-header-reference-evidence','sha':'c'*40}))
  for files in [{'private.log':b'secret'},{**self.files(),'manifest.json':b'x'*65537}]:
   with patch.object(evidence,'api') as remote,self.assertRaises(ValueError):evidence.publish(files,'synthetic-token')
   remote.assert_not_called()
if __name__=='__main__':unittest.main()
