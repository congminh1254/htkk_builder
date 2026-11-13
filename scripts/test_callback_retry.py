import contextlib,email.message,http.client,importlib.util,io,json,os,pathlib,socket,unittest,urllib.error
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parent
def load(name,file):
 spec=importlib.util.spec_from_file_location(name,ROOT/file);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
report=load('callback_retry_report_test','report-native-case.py');failure=load('callback_retry_failure_test','report-native-failure.py')
guard=report.guard;retry=guard.retry;RealBudget=retry.Budget
SOURCE='a'*40;TOKEN='fake-secret-value'
def headers(**values):
 message=email.message.Message()
 for key,value in values.items():message[key.replace('_','-')]=str(value)
 return message
def http_error(code,body=b'{"message":"unpublished"}',**extra):
 return urllib.error.HTTPError('https://api.github.com/x?token='+TOKEN,code,'unpublished',headers(**extra),io.BytesIO(body))
class Response:
 def __init__(self,status,body=b''):self.status=status;self.body=body
 def read(self,limit=-1):return self.body
 def __enter__(self):return self
 def __exit__(self,*args):return False
class FakeGitHub:
 """Answers the guard reads and the status POST; POST outcomes are scripted in order."""
 def __init__(self,post_outcomes,read_outcomes=()):
  self.post_outcomes=list(post_outcomes);self.read_outcomes=list(read_outcomes);self.posts=[];self.reads=[]
 def open(self,request,timeout=None):
  if request.get_method()=='POST':
   self.posts.append(json.loads(request.data));outcome=self.post_outcomes.pop(0)
   if isinstance(outcome,BaseException):raise outcome
   return Response(outcome)
  url=request.full_url;self.reads.append(url)
  if self.read_outcomes:
   outcome=self.read_outcomes.pop(0)
   if isinstance(outcome,BaseException):raise outcome
  if url.endswith('/git/ref/heads/main'):value={'object':{'sha':SOURCE}}
  elif '/actions/runs/' in url:value={'run_attempt':1}
  else:value=[]
  return Response(200,json.dumps(value).encode())
class Clock:
 def __init__(self):self.now=0.0;self.sleeps=[]
 def __call__(self):return self.now
 def sleep(self,seconds):self.sleeps.append(seconds);self.now+=seconds
def env():
 case=report.dispatch.CASES[0]
 return {'GITHUB_REPOSITORY':report.dispatch.BUILDER,'COMMIT_SHA':SOURCE,'WEB_CASE_ID':case,'PROBE_RESULT':'success','GITHUB_SERVER_URL':'https://github.com','GITHUB_RUN_ID':'5','GITHUB_RUN_ATTEMPT':'1','SOURCE_STATUS_TOKEN':TOKEN,'SOURCE_READ_TOKEN':TOKEN,'GH_TOKEN':TOKEN}
class CallbackRetry(unittest.TestCase):
 def run_callback(self,api,total=retry.TOTAL):
  clock=Clock();out=io.StringIO()
  budget=lambda:RealBudget(total,sleep=clock.sleep,rand=lambda:0.0,clock=clock)
  with patch.dict(os.environ,env(),clear=True),patch('urllib.request.build_opener',return_value=api),patch.object(guard.retry,'Budget',side_effect=budget),contextlib.redirect_stdout(out):
   try:report.main();code=None
   except SystemExit as exit:code=exit.code
  text=out.getvalue()+(code or '');self.assertNotIn(TOKEN,text);self.assertNotIn('unpublished',text);self.assertNotIn('api.github.com',text)
  return code,text,clock
 def test_transient_post_failures_are_retried_until_created(self):
  api=FakeGitHub([http_error(502),http_error(429,Retry_After=7),http_error(403,b'{"message":"You have exceeded a secondary rate limit"}'),ConnectionResetError(),201])
  code,text,clock=self.run_callback(api)
  self.assertIsNone(code);self.assertIn('Fixed native-case status reported privately.',text)
  self.assertEqual(len(api.posts),5);self.assertTrue(all(post==api.posts[0] for post in api.posts))
  self.assertEqual(api.posts[0]['state'],'success');self.assertEqual(clock.sleeps,[2,7,8,16])
  for kind in ('HTTP 502','HTTP 429','HTTP 403 rate limit','connection'):self.assertIn('('+kind+') on status post',text)
 def test_transient_guard_reads_are_retried(self):
  api=FakeGitHub([201],[http_error(503),socket.timeout(),http.client.RemoteDisconnected('closed')])
  code,text,clock=self.run_callback(api)
  self.assertIsNone(code);self.assertEqual(len(api.posts),1);self.assertEqual(len(clock.sleeps),3);self.assertIn('on callback guard read',text)
 def test_validation_and_auth_errors_are_never_retried(self):
  for error in (http_error(422),http_error(401),http_error(404),http_error(403,b'{"message":"Resource not accessible by integration"}')):
   api=FakeGitHub([error,201]);code,text,clock=self.run_callback(api)
   self.assertEqual(code,'Native-case callback failed; no raw response or credential published.')
   self.assertEqual(len(api.posts),1);self.assertEqual(clock.sleeps,[]);self.assertIn('error class: HTTPError '+str(error.code),text)
  api=FakeGitHub([201],[http_error(404)]);code,text,clock=self.run_callback(api)
  self.assertIsNotNone(code);self.assertEqual(api.posts,[]);self.assertEqual(len(api.reads),1)
 def test_total_wait_is_bounded(self):
  api=FakeGitHub([http_error(502)]*20);code,text,clock=self.run_callback(api)
  self.assertIsNotNone(code);self.assertIn('error class: HTTPError 502',text)
  self.assertLessEqual(clock.now,retry.TOTAL);self.assertLessEqual(len(api.posts),len(retry.BACKOFF)+1)
  self.assertLessEqual(sum(base*1.5 for base in retry.BACKOFF[:-1]),retry.TOTAL+60)
  api=FakeGitHub([http_error(502)]*20);code,text,clock=self.run_callback(api,total=10)
  self.assertIsNotNone(code);self.assertIn('retry budget exhausted',text);self.assertLessEqual(clock.now,10)
 def test_long_retry_after_is_not_waited_for(self):
  api=FakeGitHub([http_error(429,Retry_After=retry.MAX_RETRY_AFTER+1),201]);code,text,clock=self.run_callback(api)
  self.assertIsNotNone(code);self.assertEqual(clock.sleeps,[]);self.assertEqual(len(api.posts),1)
 def test_classification(self):
  for error in (http_error(500),http_error(504),http_error(429),http_error(403,Retry_After=1),http_error(403,X_RateLimit_Remaining=0),TimeoutError(),ConnectionResetError(),urllib.error.URLError(ConnectionRefusedError()),http.client.IncompleteRead(b'')):
   self.assertIsNotNone(retry.classify(error),error)
  for error in (http_error(400),http_error(401),http_error(403),http_error(404),http_error(409),http_error(422),ValueError('HTTP'),RuntimeError(),urllib.error.URLError('certificate verify failed')):
   self.assertIsNone(retry.classify(error),error)
  self.assertEqual(retry.server_wait(http_error(429,Retry_After=3)),3.0)
  self.assertEqual(retry.server_wait(http_error(403,X_RateLimit_Remaining=0,X_RateLimit_Reset=110),now=lambda:100),11.0)
  self.assertIsNone(retry.server_wait(http_error(502)))
 def test_failure_callback_shares_the_retrying_publish(self):
  self.assertIs(failure.callback.publish_status.__code__.co_filename,report.publish_status.__code__.co_filename)
  self.assertIn('guard.retry.call(lambda:dispatch.post(',(ROOT/'report-native-case.py').read_text())
  workflow=(ROOT.parent/'.github/workflows/probe-htkk-windows.yml').read_text()
  job=workflow[workflow.index('  report_failure:'):]
  self.assertGreaterEqual(int(job.split('timeout-minutes: ',1)[1].split('\n',1)[0])*60,retry.TOTAL+120)
if __name__=='__main__':unittest.main()
