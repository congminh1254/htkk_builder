"""Offline contracts for the bounded publication-transport retry (no network)."""
import http.client,importlib.util,json,pathlib,socket,ssl,unittest,urllib.error
from unittest.mock import patch

ROOT=pathlib.Path(__file__).parent
spec=importlib.util.spec_from_file_location('retry_web_publisher',ROOT/'publish-htkk-web-inputs.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
spec=importlib.util.spec_from_file_location('retry_native_output',ROOT/'publish-htkk-web-native-output.py');native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)
TOKEN='synthetic-token'
SHA='c'*40

def http_error(code):return urllib.error.HTTPError('https://api.github.com/SECRET-URL',code,'SECRET PRIVATE REMOTE BODY',{},None)

class Script:
 """Replaces one HTTP attempt: each step is an exception to raise or a value to return."""
 def __init__(self,*steps):self.steps=list(steps);self.calls=[]
 def __call__(self,path,token,payload=None,method=None):
  self.calls.append((path,payload,method))
  step=self.steps.pop(0)
  if isinstance(step,BaseException):raise step
  return step

class TransportRetry(unittest.TestCase):
 def run_api(self,script,*args):
  with patch.object(p,'api_once',script),patch.object(p.time,'sleep') as sleep:
   try:return p.api(*args),sleep
   except BaseException as error:error.sleep=sleep;raise

 def test_transient_then_success_for_each_idempotent_request(self):
  requests=(('/git/blobs',(TOKEN,{'content':'eA==','encoding':'base64'})),('/git/trees',(TOKEN,{'tree':[]})),('/git/commits',(TOKEN,{'message':'m','tree':SHA,'parents':[]})),('/git/ref/heads/main',(TOKEN,)),('/git/refs/heads/x',(TOKEN,{'sha':SHA,'force':True},'PATCH')))
  failures=(ConnectionResetError(),http.client.RemoteDisconnected(),socket.timeout(),TimeoutError(),urllib.error.URLError(ConnectionResetError()),http_error(502),http_error(503),http_error(504),http_error(500),http.client.IncompleteRead(b''))
  for path,args in requests:
   for failure in failures:
    with self.subTest(path=path,failure=type(failure).__name__):
     script=Script(failure,{'sha':SHA});value,sleep=self.run_api(script,path,*args)
     self.assertEqual(value,{'sha':SHA});self.assertEqual(len(script.calls),2);self.assertEqual([c.args for c in sleep.call_args_list],[(2,)])

 def test_two_retries_with_short_backoff_then_success(self):
  script=Script(OSError(),http_error(504),{'sha':SHA});value,sleep=self.run_api(script,'/git/blobs',TOKEN,{'content':'eA==','encoding':'base64'})
  self.assertEqual(value,{'sha':SHA});self.assertEqual(len(script.calls),3);self.assertEqual([c.args for c in sleep.call_args_list],[(2,),(5,)])

 def test_persistent_transient_keeps_the_same_safe_code(self):
  for failure,code in ((ConnectionResetError('SECRET reset /home/runner'),'IO'),(urllib.error.URLError('SECRET host'),'NETWORK'),(http_error(504),'HTTP')):
   with self.subTest(code=code):
    script=Script(failure,failure,failure)
    with self.assertRaises(type(failure)) as raised:self.run_api(script,'/git/commits',TOKEN,{'message':'m','tree':SHA,'parents':[]})
    self.assertEqual(len(script.calls),3);self.assertEqual(raised.exception.sleep.call_count,2)
    report=p.safe_failure(raised.exception);self.assertEqual(report['code'],code)
    text=json.dumps(report)
    for secret in ('SECRET','synthetic-token','api.github.com','/home/'):self.assertNotIn(secret,text)
    native_report=native.safe_failure(raised.exception);self.assertEqual(native_report['code'],code);self.assertNotIn('SECRET',json.dumps(native_report))

 def test_client_errors_and_validation_failures_are_never_retried(self):
  for failure in (http_error(400),http_error(401),http_error(403),http_error(404),http_error(409),http_error(422),p.PublicationError('API_SIZE'),p.PublicationError('API_JSON'),p.PublicationError('HTTP'),urllib.error.URLError(ssl.SSLCertVerificationError()),ssl.SSLCertVerificationError(),ValueError('x')):
   with self.subTest(failure=repr(failure)):
    script=Script(failure,{'sha':SHA})
    with self.assertRaises(type(failure)) as raised:self.run_api(script,'/git/blobs',TOKEN,{'content':'eA==','encoding':'base64'})
    self.assertEqual(len(script.calls),1);raised.exception.sleep.assert_not_called()

 def test_non_idempotent_requests_are_never_retried(self):
  for args in (('/git/refs/heads/x',TOKEN,{'force':True},'PATCH'),('/git/refs/heads/x',TOKEN,{'sha':'not-a-sha'},'PATCH'),('/issues',TOKEN,{'title':'t'}),('/git/refs',TOKEN,{'ref':'heads/x','sha':SHA}),('/git/blobs',TOKEN,{'content':''},'DELETE')):
   with self.subTest(args=args):
    script=Script(ConnectionResetError(),{'sha':SHA})
    with self.assertRaises(ConnectionResetError):self.run_api(script,*args)
    self.assertEqual(len(script.calls),1)

 def test_ref_create_retry_succeeds_without_race(self):
  ref={'ref':'refs/heads/x','object':{'type':'commit','sha':SHA}}
  script=Script(http_error(502),ref);value,_=self.run_api(script,'/git/refs',TOKEN,{'ref':'refs/heads/x','sha':SHA})
  self.assertEqual(value,ref);self.assertEqual([c[0] for c in script.calls],['/git/refs','/git/refs'])

 def test_ref_create_422_after_ambiguous_failure_resolved_only_on_exact_sha(self):
  payload={'ref':'refs/tags/htkk-case-output/'+'a'*40+'/case/'+SHA,'sha':SHA}
  matched={'ref':payload['ref'],'object':{'type':'commit','sha':SHA}}
  script=Script(ConnectionResetError(),http_error(422),matched);value,_=self.run_api(script,'/git/refs',TOKEN,payload)
  self.assertEqual(value,matched);self.assertEqual(script.calls[2],('/git/ref/tags/htkk-case-output/'+'a'*40+'/case/'+SHA,None,None))
  for existing in ({'ref':payload['ref'],'object':{'type':'commit','sha':'d'*40}},{'ref':'refs/heads/other','object':{'type':'commit','sha':SHA}},{'ref':payload['ref'],'object':{'type':'tag','sha':SHA}},{'ref':payload['ref']},[]):
   with self.subTest(existing=existing):
    script=Script(http_error(504),http_error(422),existing)
    with self.assertRaises(urllib.error.HTTPError) as raised:self.run_api(script,'/git/refs',TOKEN,payload)
    self.assertEqual(raised.exception.code,422);self.assertEqual(len(script.calls),3)
    self.assertEqual(p.safe_failure(raised.exception)['code'],'HTTP')

 def test_ref_create_422_without_prior_ambiguity_is_not_reinterpreted(self):
  script=Script(http_error(422),{'ref':'refs/heads/x','object':{'type':'commit','sha':SHA}})
  with self.assertRaises(urllib.error.HTTPError) as raised:self.run_api(script,'/git/refs',TOKEN,{'ref':'refs/heads/x','sha':SHA})
  self.assertEqual(raised.exception.code,422);self.assertEqual(len(script.calls),1)

 def test_transport_retry_through_urlopen_layer(self):
  class Response:
   status=201
   def __enter__(self):return self
   def __exit__(self,*args):pass
   def read(self,size):return json.dumps({'sha':SHA}).encode()
  class Opener:
   def __init__(self):self.count=0
   def open(self,request,timeout):
    self.count+=1
    if self.count==1:raise http.client.RemoteDisconnected('SECRET')
    return Response()
  opener=Opener()
  with patch.object(p.urllib.request,'build_opener',return_value=opener),patch.object(p.time,'sleep') as sleep:
   self.assertEqual(p.api('/git/trees',TOKEN,{'tree':[]}),{'sha':SHA})
  self.assertEqual(opener.count,2);sleep.assert_called_once_with(2)

 def test_publishers_share_the_retrying_transport(self):
  self.assertEqual(native.transport.RETRY_DELAYS,(2,5));self.assertTrue(callable(native.transport.api_once))

if __name__=='__main__':unittest.main()
