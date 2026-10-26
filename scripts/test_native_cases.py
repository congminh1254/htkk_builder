"""Offline trusted dispatch/callback contracts; no network or native evidence."""
import importlib.util,pathlib,json,unittest,urllib.error
from unittest.mock import patch
ROOT=pathlib.Path(__file__).parent
def load(name,file):
 spec=importlib.util.spec_from_file_location(name,ROOT/file);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
d=load('native_dispatch_test','dispatch-native-cases.py');r=load('native_report_test','report-native-case.py')
def document():return {'format':'htkk-web-input-publication-v1','sourceCommit':'a'*40,'cases':[{'caseId':case,'artifactCommit':letter*40} for case,letter in zip(d.CASES,('b','c','d','e'))]}
class NativeCases(unittest.TestCase):
 def test_fixed_four_cases_and_separate_tokens_pending_before_dispatch(self):
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
