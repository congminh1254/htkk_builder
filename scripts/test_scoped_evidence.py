"""Contract fixtures only; no wrapper or mocked approval is production evidence."""
import base64,copy,hashlib,importlib.util,json,pathlib,tempfile,unittest
ROOT=pathlib.Path(__file__).parent
def module(name,file):
 spec=importlib.util.spec_from_file_location(name,ROOT/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
c=module('scoped_collector_tests','collect-scoped-evidence.py');p=module('scoped_publisher_tests','publish-scoped-evidence.py');prepare=module('scoped_prepare_tests','prepare-scoped-evidence.py')
SOURCE='a'*40;BUILDER='b'*40
class CollectorTests(unittest.TestCase):
 def test_authentic_run_shape_and_rejected_wrong_attempt_source_workflow_or_conclusion(self):
  run={'id':123,'repository':{'full_name':c.BUILDER},'path':'.github/workflows/probe-htkk-windows.yml','event':'workflow_dispatch','head_branch':'main','head_sha':BUILDER,'run_attempt':1,'status':'completed','conclusion':'success'}
  c.validate_run(run,BUILDER,'123')
  for key,value in (('head_sha','f'*40),('head_branch','fork'),('path','.github/workflows/build.yml'),('run_attempt',0),('run_attempt',True),('status','in_progress'),('conclusion','failure')):
   with self.subTest(key=key),self.assertRaises(ValueError):c.validate_run({**run,key:value},BUILDER,'123')
 def test_multiline_timestamped_logs_and_unrelated_braces(self):
  record={'guiReferenceAutomation':{'value':'braces { } and quotes "'}}
  text='\n'.join('2026-10-29T00:00:00Z '+line for line in json.dumps(record,indent=2).splitlines())
  self.assertEqual(c.records('noise\n'+text),[record])
 def test_github_blob_hash_and_size_checked(self):
  body=b'CONTRACT TEST ONLY';blob={'type':'file','encoding':'base64','content':base64.b64encode(body).decode(),'size':len(body),'sha':hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest()}
  self.assertEqual(c.raw(lambda *args:blob,'producer.mjs',SOURCE),body)
  for key,value in (('sha','f'*40),('size',1),('encoding','other')):
   with self.subTest(key=key),self.assertRaises(ValueError):c.raw(lambda *args:{**blob,key:value},'producer.mjs',SOURCE)
 def test_collection_refuses_existing_workspace_and_cleans_new_partial_failure(self):
  with tempfile.TemporaryDirectory() as temp:
   root=pathlib.Path(temp);existing=root/'existing';existing.mkdir();(existing/'keep').write_text('local work')
   with self.assertRaises(FileExistsError):c.collect(SOURCE,BUILDER,existing,get=lambda *args:{})
   self.assertEqual((existing/'keep').read_text(),'local work')
   new=root/'new'
   with self.assertRaises(ValueError):c.collect(SOURCE,BUILDER,new,get=lambda *args:{})
   self.assertFalse(new.exists())
 def test_cleanup_oracle_and_gui_flags_are_all_required(self):
  oracle=lambda n:{'status':'matched','cases':n,'matched':n,'compilerJobCleanupVerified':True,'oracleJobCleanupVerified':True}
  report={'stage':'synthetic-original-gtgt-web-import-inspected','originalSourcesUnmodified':True,'officialDistributionFilesVerified':True,'mirrorUsed':False,'nativeHelperJobsStopped':True,'uiaHelpersStopped':True,'supplierProcessBoundary':dict.fromkeys(('cleanupVerified','supplierStopped','rootStopped','jobEmpty'),True),'taxIdOracle':oracle(30),'profileAliasOracle':oracle(12),'commonHeaderOracle':oracle(43),'guiReferenceAutomation':{'webSourceSha':SOURCE,'webCaseId':c.cases.CASES[0],'webTaxLeafCount':70,'gtgtCaseMoneyMatched':True,'webTaxValuesMatched':True,'roundtripReexportSucceeded':True,'exportSchemaPinnedVerified':True}}
  c.validate_report(report,SOURCE,c.cases.CASES[0])
  for key in ('cleanupVerified','supplierStopped','rootStopped','jobEmpty'):
   changed=copy.deepcopy(report);changed['supplierProcessBoundary'][key]=False
   with self.subTest(key=key),self.assertRaises(ValueError):c.validate_report(changed,SOURCE,c.cases.CASES[0])
 def test_manual_request_keeps_assessment_code_main_separate_from_historical_producer(self):
  values=prepare.prepare({}, {'source':SOURCE,'builder':BUILDER},get=lambda *args:{'sha':'c'*40})
  self.assertEqual(values,{'CODE_SOURCE_SHA':'c'*40,'EVIDENCE_SOURCE_SHA':SOURCE,'NATIVE_BUILDER_SHA':BUILDER})
 def test_auto_request_rejects_failed_or_foreign_pages_workflow(self):
  for run in ({'conclusion':'failure'},{'repository':{'full_name':'fork/repo'}}):
   def get(repo,path):return {'sha':SOURCE} if path=='commits/main' else run
   with self.assertRaises(ValueError):prepare.prepare({'workflow_run':{'id':12}}, {},get)
class PublicationTests(unittest.TestCase):
 def test_private_repo_required_before_any_blob_write(self):
  calls=[]
  def api(path,*args):calls.append(path);return {'private':False,'full_name':c.SOURCE}
  with self.assertRaises(ValueError):p.publish({'assessment.json':b'{}'},SOURCE,'TEST-TOKEN-PLACEHOLDER',api)
  self.assertEqual(calls,[''])
 def test_publisher_checks_git_blob_response_and_uses_only_fixed_private_branch(self):
  calls=[]
  def api(path,token,payload=None,method=None):
   calls.append((path,payload,method))
   if path=='':return {'private':True,'full_name':c.SOURCE}
   if path=='/git/blobs':
    body=base64.b64decode(payload['content']);return {'sha':hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest()}
   if path=='/git/trees':return {'sha':'c'*40}
   if path=='/git/commits':return {'sha':'d'*40}
   if path=='/git/ref/heads/'+p.BRANCH:return {'ref':'refs/heads/'+p.BRANCH,'object':{'type':'commit','sha':'e'*40}}
   if path=='/git/refs/heads/'+p.BRANCH:return {'ref':'refs/heads/'+p.BRANCH,'object':{'sha':'d'*40}}
   raise AssertionError('Unexpected path')
  self.assertEqual(p.publish({'assessment.json':b'{}'},SOURCE,'TEST-TOKEN-PLACEHOLDER',api),'d'*40)
  self.assertEqual(calls[-1][0],'/git/refs/heads/gtgt-scoped-evidence-candidates')
 def test_source_execution_is_separated_from_credentials_and_public_artifact_uploads(self):
  workflow=(ROOT.parent/'.github/workflows/evidence.yml').read_text()
  assessment=workflow.split('- name: Assess byte-exact evidence without credentials')[1].split('- name:')[0]
  self.assertNotIn('secrets.',assessment);self.assertNotIn('upload-artifact',workflow)
  runner=(ROOT/'assess-scoped-evidence.py').read_text()
  self.assertIn('start_new_session=True',runner);self.assertIn('os.killpg',runner)
  self.assertNotIn("'GH_TOKEN'",runner);self.assertIn('actions: read',workflow)
if __name__=='__main__':unittest.main()
