"""Offline trusted dispatch/callback contracts; no network or native evidence."""
import ast,importlib.util,pathlib,json,re,unittest,urllib.error
from unittest.mock import patch
ROOT=pathlib.Path(__file__).parent
def load(name,file):
 spec=importlib.util.spec_from_file_location(name,ROOT/file);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
d=load('native_dispatch_test','dispatch-native-cases.py');r=load('native_report_test','report-native-case.py')
def document():return {'format':'htkk-web-input-publication-v1','sourceCommit':'a'*40,'cases':[{'caseId':case,'artifactCommit':letter*40} for case,letter in zip(d.CASES,('b','c','d','e','f','1','2','3','4','5','6'))]}
class NativeCases(unittest.TestCase):
 def test_fixed_eleven_cases_and_separate_tokens_pending_before_dispatch(self):
  value=d.publication(json.dumps(document()).encode(),'a'*40);calls=[]
  d.dispatch(value,'builder-token','source-token',lambda *args:calls.append(args))
  self.assertEqual(len(calls),2*len(d.CASES))
  for index,case in enumerate(d.CASES):
   status,dispatch=calls[index*2:index*2+2]
   self.assertEqual(status[0],'https://api.github.com/repos/'+d.REPO+'/statuses/'+'a'*40);self.assertEqual(status[1],'source-token');self.assertEqual(status[2]['context'],d.CONTEXTS[case]);self.assertEqual(status[2]['state'],'pending')
   self.assertEqual(dispatch[1],'builder-token');self.assertEqual(dispatch[2]['inputs']['web_case_id'],case);self.assertEqual(dispatch[2]['inputs']['web_artifact_commit'],document()['cases'][index]['artifactCommit']);self.assertEqual(dispatch[2]['inputs']['web_source_sha'],'a'*40)
 def test_dispatch_failure_sets_failure_status_without_retrying_action(self):
  calls=[]
  def send(url,token,payload):
   calls.append((url,payload))
   if '/dispatches' in url:raise RuntimeError('unpublished remote error')
  with self.assertRaises(RuntimeError):d.dispatch(document(),'builder','source',send)
  self.assertEqual(len(calls),3);self.assertEqual(calls[-1][1]['state'],'failure');self.assertEqual(sum('/dispatches' in url for url,_ in calls),1)
 def test_publication_rejects_extra_duplicate_stale_mixed_cases_or_bad_sha(self):
  for mutate in (lambda x:x.update(extra='secret'),lambda x:x.update(sourceCommit='b'*40),lambda x:x['cases'].reverse(),lambda x:x['cases'][0].update(extra='private'),lambda x:x['cases'][0].update(artifactCommit='invalid')):
   value=document();mutate(value)
   with self.assertRaises(ValueError):d.publication(json.dumps(value).encode(),'a'*40)
  with self.assertRaises(ValueError):d.publication(b'{"format":"a","format":"b"}','a'*40)
  with self.assertRaises(ValueError):d.publication(b'x'*16385,'a'*40)
 def test_callback_success_is_only_actual_probe_success_other_outcomes_fail(self):
  for result in ('success','failure','cancelled','skipped'):
   payload=r.payload(d.CASES[0],result,'https://github.com','123')
   self.assertEqual(payload['state'],'success' if result=='success' else 'failure');self.assertEqual(payload['context'],'htkk-native/zero')
  for case,result,server,run in (('private','success','https://github.com','123'),(d.CASES[0],'pending','https://github.com','123'),(d.CASES[0],'success','https://evil.invalid','123'),(d.CASES[0],'success','https://github.com','private')):
   with self.assertRaises(ValueError):r.payload(case,result,server,run)
 def test_authenticated_post_has_no_redirects_or_error_body_logging(self):
  class Response:
   status=204
   def __enter__(self):return self
   def __exit__(self,*args):return False
  class Opener:
   def open(self,request,timeout):
    self_test.assertEqual(request.get_header('Authorization'),'Bearer fake-token');self_test.assertEqual(timeout,30);return Response()
  self_test=self
  with patch.object(d.urllib.request,'build_opener',return_value=Opener()) as build:d.post('https://api.github.com/repos/'+d.BUILDER+'/actions/workflows/probe-htkk-windows.yml/dispatches','fake-token',{})
  self.assertIsInstance(build.call_args.args[0],d.NoRedirect);self.assertIsNone(d.NoRedirect().redirect_request(None,None,None,None,None))
  with self.assertRaises(ValueError):d.post('https://api.github.com/','',{})


class NativeWorkflowCredentials(unittest.TestCase):
 def test_parallel_web_cases_skip_shared_references_but_keep_scoped_raw_and_status(self):
  # Exercise the workflow conditions, including their process/credential gates.
  # This verifies the real publication routing rather than a duplicated helper.
  text=(ROOT.parent/'.github/workflows/probe-htkk-windows.yml').read_text()
  conditions=dict(re.findall(r"      - name: ([^\n]+)\n        if: ([^\n]+)",text))
  def enabled(name,mode,install=True,safe='true',stopped='true',artifact='a'*40):
   expression=conditions[name].replace('always()','True').replace('&&',' and ')
   values={'inputs.install_and_probe':install,'inputs.gui_automation':mode,'steps.native_probe.outputs.credentials_safe':safe,'steps.native_probe.outputs.supplier_stopped':stopped,'inputs.web_artifact_commit':artifact}
   for key,value in values.items():expression=expression.replace(key,repr(value))
   parsed=ast.parse(expression,mode='eval')
   for node in ast.walk(parsed):
    self.assertIsInstance(node,(ast.Expression,ast.BoolOp,ast.And,ast.Compare,ast.Eq,ast.NotEq,ast.Constant))
   return eval(compile(parsed,'<fixed workflow condition>','eval'),{'__builtins__':{}},{})
  shared=('Publish supplier startup window privately','Retain synthetic common-header reference privately')
  raw='Retain verified raw native web reexport privately';status='Report fixed native-case status privately'
  for mode in ('none','profile-save','gtgt-export-inspect','gtgt-web-import-inspect'):
   web=mode=='gtgt-web-import-inspect'
   for name in shared:self.assertEqual(enabled(name,mode),not web)
   self.assertEqual(enabled(raw,mode),web);self.assertEqual(enabled(status,mode),web)
   for name in (*shared,raw,status):
    self.assertFalse(enabled(name,mode,install=False));self.assertFalse(enabled(name,mode,safe='false'))
  self.assertFalse(enabled(raw,'gtgt-web-import-inspect',stopped='false'))
  self.assertFalse(enabled(raw,'gtgt-web-import-inspect',artifact=''))

class NativeManifestFormatRouting(unittest.TestCase):
 def test_powershell_staging_routes_every_fixed_case_to_its_exact_manifest(self):
  reader=load('native_manifest_reader_test','fetch-htkk-web-input.py')
  script=(ROOT/'probe-htkk-windows.ps1').read_text()
  table=re.search(r'\$expectedFormats=@\{(.*?)\n      \}',script,re.S)
  self.assertIsNotNone(table)
  pairs=re.findall(r"'([^']+)'='([^']+)'",table.group(1))
  self.assertEqual(len(pairs),len(reader.CASES))
  self.assertEqual(dict(pairs),reader.CASES)
  self.assertIn('$expectedFormat=$expectedFormats[$env:EXPECTED_WEB_CASE_ID]',script)
