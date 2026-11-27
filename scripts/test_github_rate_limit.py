"""Offline contracts for the bounded GitHub rate-limit retry (fake responses, no network)."""
import contextlib,email.message,email.utils,importlib.util,io,json,pathlib,unittest,urllib.error
from unittest.mock import patch

ROOT=pathlib.Path(__file__).resolve().parent
def load(name,file):
 spec=importlib.util.spec_from_file_location(name,ROOT/file);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
p=load('rate_web_publisher','publish-htkk-web-inputs.py');w=p.reader;rate=p.rate
declaration=load('rate_declaration_output','publish-htkk-declaration-native-output.py')
khbs=load('rate_khbs_output','publish-htkk-khbs-native-output.py')
native=load('rate_web_native_output','publish-htkk-web-native-output.py')
annex=load('rate_annex12_export','publish-htkk-annex12-export.py')
nonzero=load('rate_annex12_nonzero_export','publish-htkk-annex12-nonzero-export.py')
d=load('rate_dispatch','dispatch-native-cases.py')
collector=load('rate_collector','collect-scoped-evidence.py')
report=load('rate_callback','report-native-case.py')
TOKEN='synthetic-token';SHA='c'*40;NOW=1_800_000_000
PRIVATE=('SECRET','synthetic-token','api.github.com','htkk_web','/home/')

def headers(**values):
 message=email.message.Message()
 for key,value in values.items():message[key.replace('_','-')]=str(value)
 return message
def http_error(code,**extra):
 return urllib.error.HTTPError('https://api.github.com/repos/htkk-net/htkk_web/SECRET-PATH?token='+TOKEN,code,'SECRET PRIVATE REMOTE BODY',headers(**extra),io.BytesIO(b'{"message":"SECRET PRIVATE REMOTE BODY"}'))
def limited(code=403,wait=7):return http_error(code,Retry_After=wait)

class Clock:
 def __init__(self):self.sleeps=[];self.lines=[]
 def sleep(self,seconds):self.sleeps.append(seconds)
 def budget(self,**kw):return rate.Budget(sleep=self.sleep,now=lambda:NOW,log=self.lines.append,**kw)

class Script:
 """One fake HTTP attempt per step: an exception to raise or a value to return."""
 def __init__(self,*steps):self.steps=list(steps);self.calls=[]
 def __call__(self,path,token,payload=None,method=None):
  self.calls.append((path,payload,method));step=self.steps.pop(0)
  if isinstance(step,BaseException):raise step
  return step

class Classification(unittest.TestCase):
 def test_only_429_or_403_with_rate_limit_headers_is_rate_limited(self):
  for error in (http_error(429),http_error(403,Retry_After=1),http_error(403,X_RateLimit_Remaining=0),http_error(403,X_RateLimit_Remaining=' 0 ',X_RateLimit_Reset=NOW+5)):
   self.assertTrue(rate.rate_limited(error),error.headers.items())
  for error in (http_error(401),http_error(403),http_error(403,X_RateLimit_Remaining=4999),http_error(401,Retry_After=1),http_error(404),http_error(409),http_error(422),http_error(500,Retry_After=1),ConnectionResetError(),ValueError('AUTH')):
   self.assertFalse(rate.rate_limited(error),error)
 def test_requested_wait_honours_retry_after_then_reset(self):
  now=lambda:NOW
  self.assertEqual(rate.requested_wait(http_error(429,Retry_After=3),now),3.0)
  date=email.utils.formatdate(NOW+20,usegmt=True)
  self.assertEqual(rate.requested_wait(http_error(403,Retry_After=date),now),20.0)
  self.assertEqual(rate.requested_wait(http_error(403,X_RateLimit_Remaining=0,X_RateLimit_Reset=NOW+10),now),11.0)
  self.assertEqual(rate.requested_wait(http_error(403,X_RateLimit_Remaining=0,X_RateLimit_Reset=NOW-50),now),1.0)
  self.assertIsNone(rate.requested_wait(http_error(429),now));self.assertIsNone(rate.requested_wait(http_error(403,Retry_After='soon'),now))

class BudgetLimits(unittest.TestCase):
 def test_waits_are_capped_per_wait_in_count_and_in_total(self):
  clock=Clock();b=clock.budget()
  self.assertTrue(b.wait(limited(wait=rate.MAX_WAIT)));self.assertEqual(clock.sleeps,[rate.MAX_WAIT])
  self.assertFalse(clock.budget().wait(limited(wait=rate.MAX_WAIT+1)))
  self.assertFalse(clock.budget().wait(http_error(403,X_RateLimit_Remaining=0,X_RateLimit_Reset=NOW+3600)))
  # A 429 without any wait header waits GitHub's one minute default.
  clock=Clock();self.assertTrue(clock.budget().wait(http_error(429)));self.assertEqual(clock.sleeps,[rate.DEFAULT_WAIT])
  clock=Clock();b=clock.budget()
  while b.wait(limited(wait=1)):pass
  self.assertEqual(len(clock.sleeps),rate.MAX_RETRIES)
  clock=Clock();b=clock.budget()
  while b.wait(limited(wait=50)):pass
  self.assertLessEqual(sum(clock.sleeps),rate.TOTAL);self.assertEqual(clock.sleeps,[50,50])
  self.assertFalse(Clock().budget().wait(http_error(403)))
 def test_log_lines_are_fixed_words_and_numbers_only(self):
  clock=Clock();b=clock.budget()
  b.wait(limited(wait=2));b.wait(limited(429,wait=999))
  self.assertEqual(clock.lines,['GitHub API rate limit (HTTP 403); waiting 2 s, bounded retry 1 of 3.','GitHub API rate limit (HTTP 429); the wait does not fit the bounded retry budget, not retried.'])
 def test_budget_fits_the_native_job_timeouts(self):
  workflow=(ROOT.parent/'.github/workflows/probe-htkk-windows.yml').read_text()
  readiness=int(workflow[workflow.index('  readiness:'):].split('timeout-minutes: ',1)[1].split('\n',1)[0])*60
  # One readiness job runs three API processes in turn: the input fetch and the output publish (each with
  # this budget) and the status callback (its own callback_retry budget). Seven minutes stay reserved for
  # the offline contract tests, the pinned install and the native run (about five to six minutes observed).
  self.assertLessEqual(2*rate.TOTAL+report.guard.retry.TOTAL+420,readiness)
  self.assertLessEqual(rate.MAX_WAIT,rate.TOTAL);self.assertLessEqual(rate.DEFAULT_WAIT,rate.MAX_WAIT)
  build=(ROOT.parent/'.github/workflows/build.yml').read_text()
  # The release job runs the input publish, the dispatch and the cohort collection with one budget each:
  # together they stay within a tenth of its timeout.
  self.assertLessEqual(3*rate.TOTAL,int(build.split('timeout-minutes: ',1)[1].split('\n',1)[0])*60//10)

class PublicationTransport(unittest.TestCase):
 def run_api(self,script,*args):
  clock=Clock()
  with patch.object(p,'api_once',script),patch.object(p.time,'sleep',clock.sleep),patch.object(rate,'_PROCESS',clock.budget()):
   try:return p.api(*args),clock
   except BaseException as error:error.clock=clock;raise
 def test_rate_limited_reads_and_idempotent_writes_wait_then_succeed(self):
  requests=(('',(TOKEN,)),('/git/ref/heads/main',(TOKEN,)),('/git/blobs',(TOKEN,{'content':'eA==','encoding':'base64'})),('/git/trees',(TOKEN,{'tree':[]})),('/git/commits',(TOKEN,{'message':'m','tree':SHA,'parents':[]})),('/git/refs/heads/x',(TOKEN,{'sha':SHA,'force':True},'PATCH')),('/git/refs',(TOKEN,{'ref':'refs/heads/x','sha':SHA})))
  for path,args in requests:
   for failure,wait in ((limited(403,7),7),(limited(429,3),3),(http_error(429),rate.DEFAULT_WAIT),(http_error(403,X_RateLimit_Remaining=0,X_RateLimit_Reset=NOW+5),6)):
    with self.subTest(path=path,code=failure.code,wait=wait):
     script=Script(failure,{'sha':SHA});value,clock=self.run_api(script,path,*args)
     self.assertEqual(value,{'sha':SHA});self.assertEqual(len(script.calls),2);self.assertTrue(all(c==script.calls[0] for c in script.calls))
     self.assertEqual(len(clock.sleeps),1)
     if wait is not None:self.assertEqual(clock.sleeps,[wait])
 def test_real_auth_failures_fail_fast_as_auth(self):
  for failure in (http_error(401),http_error(403),http_error(403,X_RateLimit_Remaining=17)):
   with self.subTest(code=failure.code):
    script=Script(failure,{'sha':SHA})
    with self.assertRaises(urllib.error.HTTPError) as raised:self.run_api(script,'/git/blobs',TOKEN,{'content':'eA==','encoding':'base64'})
    self.assertEqual(len(script.calls),1);self.assertEqual(raised.exception.clock.sleeps,[])
    self.assertEqual(p.safe_failure(raised.exception)['code'],'AUTH')
 def test_exhausted_or_long_rate_limit_reports_rate_limit_without_private_text(self):
  for steps,sleeps in (((limited(wait=50),)*4,[50,50]),((http_error(403,X_RateLimit_Remaining=0,X_RateLimit_Reset=NOW+3600),),[]),((limited(429,wait=rate.MAX_WAIT+1),),[])):
   with self.subTest(sleeps=sleeps):
    script=Script(*steps,{'sha':SHA})
    with self.assertRaises(urllib.error.HTTPError) as raised:self.run_api(script,'/git/commits',TOKEN,{'message':'m','tree':SHA,'parents':[]})
    self.assertEqual(raised.exception.clock.sleeps,sleeps);self.assertEqual(len(script.calls),len(sleeps)+1)
    status=p.mark_step(raised.exception,'commit')
    for module,format in ((p,'htkk-web-input-publication-status-v1'),(declaration,'htkk-declaration-native-output-publication-status-v1'),(khbs,'htkk-khbs-native-output-publication-status-v1'),(native,'htkk-web-native-output-publication-status-v1')):
     result=module.safe_failure(status);self.assertEqual((result['format'],result['status'],result['code']),(format,'rejected','RATE_LIMIT'))
     text=json.dumps(result)
     for secret in PRIVATE:self.assertNotIn(secret,text)
    self.assertEqual(p.safe_failure(status),{'format':'htkk-web-input-publication-status-v1','status':'rejected','code':'RATE_LIMIT','httpStatus':raised.exception.code,'step':'commit'})
    for module in (annex,nonzero):self.assertEqual(module.safe_failure(status)['code'],'RATE_LIMIT')
    for line in raised.exception.clock.lines:
     for secret in PRIVATE:self.assertNotIn(secret,line)
 def test_every_consumer_code_set_accepts_rate_limit(self):
  for codes in (w.CODES,p.CODES,declaration.CODES,khbs.CODES,native.CODES,annex.CODES,nonzero.CODES):self.assertIn('RATE_LIMIT',codes)
  self.assertEqual(declaration.OutputError('RATE_LIMIT').code,'RATE_LIMIT');self.assertEqual(p.PublicationError('RATE_LIMIT').code,'RATE_LIMIT')
 def test_non_idempotent_writes_are_never_retried_even_when_rate_limited(self):
  for args in (('/issues',TOKEN,{'title':'t'}),('/git/refs/heads/x',TOKEN,{'force':True},'PATCH'),('/git/refs',TOKEN,{'ref':'heads/x','sha':SHA})):
   with self.subTest(args=args):
    script=Script(limited(wait=1),{'sha':SHA})
    with self.assertRaises(urllib.error.HTTPError) as raised:self.run_api(script,*args)
    self.assertEqual(len(script.calls),1);self.assertEqual(raised.exception.clock.sleeps,[]);self.assertEqual(p.safe_failure(raised.exception)['code'],'RATE_LIMIT')
 def test_ref_create_422_after_rate_limit_adopts_only_the_exact_ref(self):
  payload={'ref':'refs/heads/x','sha':SHA};ref={'ref':'refs/heads/x','object':{'type':'commit','sha':SHA}}
  script=Script(limited(wait=2),http_error(422),ref);value,clock=self.run_api(script,'/git/refs',TOKEN,payload)
  self.assertEqual(value,ref);self.assertEqual(clock.sleeps,[2]);self.assertEqual(script.calls[2],('/git/ref/heads/x',None,None))
  for existing in ({'ref':'refs/heads/x','object':{'type':'commit','sha':'d'*40}},{'ref':'refs/heads/x','object':{'type':'tag','sha':SHA}},[]):
   with self.subTest(existing=existing):
    script=Script(limited(wait=2),http_error(422),existing)
    with self.assertRaises(urllib.error.HTTPError) as raised:self.run_api(script,'/git/refs',TOKEN,payload)
    self.assertEqual(raised.exception.code,422);self.assertEqual(len(script.calls),3);self.assertEqual(p.safe_failure(raised.exception)['code'],'HTTP')
  # Without any earlier refused or failed attempt a 422 stays a plain conflict: no adoption read.
  script=Script(http_error(422),ref)
  with self.assertRaises(urllib.error.HTTPError):self.run_api(script,'/git/refs',TOKEN,payload)
  self.assertEqual(len(script.calls),1)
 def test_rate_limit_and_transient_retries_are_counted_apart(self):
  script=Script(http_error(502),limited(wait=4),http_error(503),limited(429,wait=1),{'sha':SHA})
  value,clock=self.run_api(script,'/git/blobs',TOKEN,{'content':'eA==','encoding':'base64'})
  self.assertEqual(value,{'sha':SHA});self.assertEqual(clock.sleeps,[2,4,5,1])
 def test_one_budget_spans_every_call_of_the_process(self):
  clock=Clock();budget=clock.budget()
  with patch.object(p,'api_once',Script(limited(wait=50),{'sha':SHA},limited(wait=50),{'sha':SHA},limited(wait=50),{'sha':SHA})),patch.object(rate,'_PROCESS',budget):
   p.api('',TOKEN);p.api('',TOKEN)
   with self.assertRaises(urllib.error.HTTPError):p.api('',TOKEN)
  self.assertEqual(clock.sleeps,[50,50]);self.assertIs(p.rate,w.rate);self.assertIs(declaration.transport.rate,declaration.reader.rate)

class Response:
 def __init__(self,status,body):self.status=status;self.body=body
 def read(self,limit=-1):return self.body
 def __enter__(self):return self
 def __exit__(self,*args):return False
class Opener:
 def __init__(self,*steps):self.steps=list(steps);self.urls=[]
 def open(self,request,timeout=None):
  self.urls.append(request.full_url);step=self.steps.pop(0)
  if isinstance(step,BaseException):raise step
  return step

class ReadTransports(unittest.TestCase):
 def test_input_fetch_waits_on_rate_limit_and_keeps_auth_fail_fast(self):
  clock=Clock();body=json.dumps({'private':True}).encode()
  with patch.object(w.urllib.request,'build_opener',return_value=Opener(limited(wait=9),Response(200,body))),patch.object(w.rate,'_PROCESS',clock.budget()):
   self.assertEqual(w.api('',TOKEN),{'private':True})
  self.assertEqual(clock.sleeps,[9])
  for failure,code,sleeps in ((http_error(403),'AUTH',[]),(http_error(401),'AUTH',[]),(limited(429,wait=rate.MAX_WAIT+1),'RATE_LIMIT',[])):
   clock=Clock();opener=Opener(failure,Response(200,body))
   with patch.object(w.urllib.request,'build_opener',return_value=opener),patch.object(w.rate,'_PROCESS',clock.budget()):
    with self.assertRaises(urllib.error.HTTPError) as raised:w.api('',TOKEN)
   self.assertEqual(len(opener.urls),1);self.assertEqual(clock.sleeps,sleeps)
   result=w.safe_failure(raised.exception);self.assertEqual(result,{'format':'htkk-web-reference-input-fetch-status-v1','status':'rejected','code':code,'httpStatus':failure.code})
 def test_cohort_collector_reads_wait_on_rate_limit_only(self):
  clock=Clock();opener=Opener(limited(wait=3),Response(200,b'{"object":{"sha":"x"}}'))
  with patch.dict(collector.os.environ,{'SOURCE_READ_TOKEN':TOKEN,'GH_TOKEN':TOKEN}),patch.object(collector.urllib.request,'build_opener',return_value=opener),patch.object(collector.cases.rate,'_PROCESS',clock.budget()):
   self.assertEqual(collector.api(collector.SOURCE,'git/ref/heads/main'),{'object':{'sha':'x'}})
   self.assertEqual(clock.sleeps,[3]);self.assertEqual(len(opener.urls),2)
   opener=Opener(http_error(403),Response(200,b'{}'))
   with patch.object(collector.urllib.request,'build_opener',return_value=opener):
    with self.assertRaises(urllib.error.HTTPError):collector.api(collector.SOURCE,'git/ref/heads/main')
   self.assertEqual(len(opener.urls),1);self.assertEqual(clock.sleeps,[3])

class Dispatch(unittest.TestCase):
 def test_status_post_waits_on_rate_limit_and_real_auth_fails_fast(self):
  sleeps=[];sent=[]
  def send(url,token,payload):
   sent.append(payload)
   if len(sent)==1:raise limited(429,wait=6)
  with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()) as err:d.deliver(send,'u',TOKEN,{'state':'pending'},sleeps.append)
  self.assertEqual(sleeps,[6]);self.assertEqual(len(sent),2);self.assertNotIn('SECRET',err.getvalue())
  for failure in (http_error(401),http_error(403)):
   sleeps=[];calls=[]
   def deny(url,token,payload,failure=failure):calls.append(1);raise failure
   with self.assertRaises(urllib.error.HTTPError):d.deliver(deny,'u',TOKEN,{},sleeps.append)
   self.assertEqual((len(calls),sleeps),(1,[]))
 def test_rate_limited_dispatch_is_resent_only_after_proving_absence(self):
  for state,expected in ((False,2),(True,1)):
   sleeps=[];calls=[]
   def send(url,token,payload):
    calls.append(1)
    if len(calls)==1:raise limited(wait=4)
   with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):d.deliver(send,'u',TOKEN,{},sleeps.append,confirm=lambda state=state:state)
   self.assertEqual((len(calls),sleeps),(expected,[4]))
  calls=[]
  def send(url,token,payload):calls.append(1);raise limited(wait=4)
  with contextlib.redirect_stderr(io.StringIO()),self.assertRaises(urllib.error.HTTPError):d.deliver(send,'u',TOKEN,{},[].append,confirm=lambda:None)
  self.assertEqual(len(calls),1)
 def test_dispatch_budget_is_shared_and_bounded(self):
  sleeps=[];budget=rate.Budget(sleep=sleeps.append,log=lambda line:None)
  def send(url,token,payload):raise limited(wait=50)
  for _ in range(3):
   with self.assertRaises(urllib.error.HTTPError):d.deliver(send,'u',TOKEN,{},sleeps.append,budget=budget)
  self.assertEqual(sleeps,[50,50]);self.assertLessEqual(sum(sleeps),rate.TOTAL)

class Callback(unittest.TestCase):
 def test_failure_class_names_rate_limit_apart_from_auth(self):
  self.assertEqual(report.failure_class(http_error(403)),'HTTPError 403')
  self.assertEqual(report.failure_class(http_error(401)),'HTTPError 401')
  self.assertEqual(report.failure_class(http_error(403,X_RateLimit_Remaining=0,X_RateLimit_Reset=NOW)),'HTTPError 403 rate limit')
  self.assertEqual(report.failure_class(http_error(429)),'HTTPError 429 rate limit')

if __name__=='__main__':unittest.main()
