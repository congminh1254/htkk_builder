"""Trusted fixed-case dispatch only; never executes private source code."""
import datetime,http.client,json,os,pathlib,re,time,urllib.parse,urllib.request,urllib.error
REPO='htkk-net/htkk_web'
BUILDER='congminh1254/htkk_builder'
import importlib.util
_spec=importlib.util.spec_from_file_location('trusted_case_metadata',pathlib.Path(__file__).with_name('htkk_native_cases.py'));case_registry=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(case_registry)
CASES=tuple(case_registry.CASES)
_rate_spec=importlib.util.spec_from_file_location('dispatch_github_rate_limit',pathlib.Path(__file__).with_name('github_rate_limit.py'));rate=importlib.util.module_from_spec(_rate_spec);_rate_spec.loader.exec_module(rate)
# Release/Pages/evidence cohort. Candidate cases still get their own dispatch and status.
GATE_CASES=tuple(case_registry.GATE_CASES)
CONTEXTS={id:c['statusContext']for id,c in case_registry.CASES.items()}
# Per-case oracle: a case's registry htkkVersion (absent = default 5.8.1). Only a non-default case gets
# the probe input, the ' [HTKK x.y.z]' run title and the '@htkkxyz' status context; a default case keeps
# the exact inputs, title and context it had before the field existed.
def version(case):return case_registry.htkk_version(case)
def context(case):return case_registry.status_context(case)
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args):return None
def sha(value):
 if not isinstance(value,str) or not re.fullmatch('[0-9a-f]{40}',value):raise ValueError('SHA')
 return value
def publication(body,expected):
 sha(expected)
 if not isinstance(body,bytes) or len(body)>case_registry.PUBLICATION_MAX_BYTES:raise ValueError('PUBLICATION')
 def unique(pairs):
  value={}
  for key,item in pairs:
   if key in value:raise ValueError('PUBLICATION')
   value[key]=item
  return value
 value=json.loads(body.decode('utf-8'),object_pairs_hook=unique)
 if type(value) is not dict or set(value)!= {'format','sourceCommit','requestId','planSha256','cases'} or value['format']!='htkk-web-input-publication-v2' or type(value['requestId']) is not str or not re.fullmatch('[1-9][0-9]{0,19}',value['requestId']) or not (value['planSha256'] is None or (type(value['planSha256']) is str and re.fullmatch('[0-9a-f]{64}',value['planSha256']))) or value['sourceCommit']!=expected or type(value['cases']) is not list or len(value['cases'])!=len(CASES):raise ValueError('PUBLICATION')
 for item,case in zip(value['cases'],CASES):
  if type(item) is not dict or set(item)!={'caseId','artifactCommit'} or item['caseId']!=case:raise ValueError('PUBLICATION')
  sha(item['artifactCommit'])
 return value

def post(url,token,payload):
 if not isinstance(token,str) or not token:raise ValueError('AUTH')
 request=urllib.request.Request(url,data=json.dumps(payload,separators=(',',':')).encode(),headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','Content-Type':'application/json','User-Agent':'HTKK-Fixed-Native-Dispatch/1.0'},method='POST')
 with urllib.request.build_opener(NoRedirect()).open(request,timeout=30) as response:
  if response.status not in (201,204):raise ValueError('HTTP')

PROBE='.github/workflows/probe-htkk-windows.yml'
RETRY_DELAYS=(2,5) # At most two bounded retries per POST.
CLOCK_SKEW=datetime.timedelta(seconds=30)
def transient(error):
 # HTTPError is an OSError/URLError; only a server-side 5xx may be retried, never 4xx.
 if isinstance(error,urllib.error.HTTPError):return error.code in (500,502,503,504)
 return isinstance(error,(OSError,urllib.error.URLError,TimeoutError,http.client.RemoteDisconnected))

def get_json(url,token):
 if not isinstance(token,str) or not token:raise ValueError('AUTH')
 request=urllib.request.Request(url,headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','User-Agent':'HTKK-Fixed-Native-Dispatch/1.0'})
 with urllib.request.build_opener(NoRedirect()).open(request,timeout=30) as response:
  body=response.read(2_000_001)
  if response.status!=200 or len(body)>2_000_000:raise ValueError('HTTP')
  return json.loads(body)

def run_title(case):
 # Mirrors probe-htkk-windows.yml run-name, rendered from the same web_case_id/gui_automation
 # inputs the run later binds into its status context and retained provenance (caseId).
 # A non-default oracle adds the run-name suffix of the workflow (' [HTKK 5.8.2]').
 v=version(case)
 return 'HTKK native case '+case+' ('+gui(case)+')'+('' if v==case_registry.oracle.DEFAULT else ' [HTKK '+v+']')
def gui(case):return case_registry.ADAPTERS[case_registry.CASES[case]['adapterId']]['driver']

def created(case,builder,started,token,get):
 """True if a probe run for this case exists since the attempt start; None if ambiguous."""
 since=(started-CLOCK_SKEW).astimezone(datetime.timezone.utc)
 query=urllib.parse.urlencode({'event':'workflow_dispatch','branch':'main','head_sha':builder,'created':'>='+since.strftime('%Y-%m-%dT%H:%M:%SZ'),'per_page':'100'})
 value=get('https://api.github.com/repos/'+BUILDER+'/actions/workflows/probe-htkk-windows.yml/runs?'+query,token)
 runs=value.get('workflow_runs') if type(value) is dict else None
 if type(runs) is not list or type(value.get('total_count')) is not int or value['total_count']>len(runs):return None
 found=False;unknown=False
 for run in runs:
  if type(run) is not dict:return None
  # The same run identity native_batch/collect-scoped-evidence validate.
  if run.get('path')!=PROBE or run.get('event')!='workflow_dispatch' or run.get('head_branch')!='main' or run.get('head_sha')!=builder or run.get('repository',{}).get('full_name')!=BUILDER:continue
  try:at=datetime.datetime.strptime(run.get('created_at',''),'%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=datetime.timezone.utc)
  except (TypeError,ValueError):return None
  if at<since:continue
  title=run.get('display_title')
  if title==run_title(case):found=True
  elif not isinstance(title,str) or not title.startswith('HTKK native case '):unknown=True
 if found:return True
 # A fresh probe run whose case cannot be identified may be ours: never risk a duplicate.
 return None if unknown else False

def deliver(send,url,token,payload,sleep,confirm=None,budget=None):
 """POST with bounded retries; confirm() is checked before re-sending a non-idempotent POST.

 A rate-limit refusal (429, or 403 with Retry-After / X-RateLimit-Remaining: 0) waits within the
 rate-limit budget instead of the short 5xx backoff; any other 4xx fails at once."""
 budget=budget or rate.Budget(sleep=sleep);attempt=0
 while True:
  try:send(url,token,payload);return
  except Exception as error:
   if rate.rate_limited(error):
    if not budget.wait(error):raise
   else:
    if not transient(error) or attempt==len(RETRY_DELAYS):raise
    sleep(RETRY_DELAYS[attempt]);attempt+=1
   if confirm is not None:
    try:state=confirm()
    except Exception as check:
     if not transient(check):raise
     state=None
    if state is True:print('Native-case dispatch transient error; the run already exists, not re-dispatched.',flush=True);return
    if state is None:raise error # Unknown whether the run exists; fail closed rather than duplicate.
   if not rate.rate_limited(error):print('Transient native-case API error; bounded retry '+str(attempt)+' of '+str(len(RETRY_DELAYS))+'.',flush=True)

def inputs(source,item,request_id,plan_sha256):
 case=item['caseId'];value={'install_and_probe':True,'synthetic_login':True,'acknowledge_registration':True,'runtime_host':'clr2-x86-reference','gui_automation':gui(case),'web_source_sha':source,'web_case_id':case,'web_artifact_commit':item['artifactCommit']}
 # The release's case context (request id, plan sha256 or 'none'): the probe checks case-context.json against it.
 value.update(web_request_id=request_id,web_plan_sha256=plan_sha256 or 'none')
 # htkk_version is sent only for a non-default case.
 if version(case)!=case_registry.oracle.DEFAULT:value['htkk_version']=version(case)
 return value

def deferred(case,at):
 """notBefore of a case whose period HTKK refuses at `at` (UTC day of the dispatch), else None."""
 return case_registry.deferred_until(case,at.astimezone(datetime.timezone.utc).date())

def dispatch(value,actions_token,status_token,send=None,builder=None,get=None,sleep=None,now=None):
 send=send or post;get=get or get_json;sleep=sleep or time.sleep;now=now or (lambda:datetime.datetime.now(datetime.timezone.utc))
 if builder is not None:sha(builder)
 # One rate-limit budget for the whole dispatch process.
 count=0;budget=rate.Budget(sleep=sleep)
 for item in value['cases']:
  # A deferred case (registry notBefore) is neither dispatched nor given a status: never reported as a success.
  until=deferred(item['caseId'],now())
  if until is not None:print('Native case '+item['caseId']+' deferred until '+until+' (HTKK refuses its period before that day); not dispatched, no status.',flush=True);continue
  count+=1
  status='https://api.github.com/repos/'+REPO+'/statuses/'+value['sourceCommit']
  # Commit statuses are last-writer hints, so a blind retry of the same pending status is safe.
  deliver(send,status,status_token,{'state':'pending','context':context(item['caseId']),'description':'Fixed synthetic native case queued input:'+item['artifactCommit']},sleep,budget=budget)
  started=now()
  # workflow_dispatch is not idempotent: only re-send once the exact case run is proven absent.
  confirm=None if builder is None else (lambda case=item['caseId'],started=started:created(case,builder,started,actions_token,get))
  try:
   deliver(send,'https://api.github.com/repos/'+BUILDER+'/actions/workflows/probe-htkk-windows.yml/dispatches',actions_token,{'ref':'main','inputs':inputs(value['sourceCommit'],item,value['requestId'],value['planSha256'])},sleep,confirm,budget)
  except Exception:
   deliver(send,status,status_token,{'state':'failure','context':context(item['caseId']),'description':'Fixed synthetic native case dispatch failed'},sleep,budget=budget)
   raise
 return count

def main():
 try:
  if os.environ.get('GITHUB_REPOSITORY')!=BUILDER:raise ValueError('BUILDER')
  path=pathlib.Path(os.environ['RUNNER_TEMP'])/'htkk-web-input-publication.json'
  if path.is_symlink() or not path.is_file() or path.stat().st_size>case_registry.PUBLICATION_MAX_BYTES:raise ValueError('PUBLICATION')
  value=publication(path.read_bytes(),os.environ['COMMIT_SHA'])
  # Written by publish-htkk-web-inputs.py earlier in this same run: its request id is this run's id.
  if value['requestId']!=os.environ.get('GITHUB_RUN_ID'):raise ValueError('PUBLICATION')
  count=dispatch(value,os.environ.get('BUILDER_ACTIONS_TOKEN'),os.environ.get('SOURCE_STATUS_TOKEN'),builder=sha(os.environ.get('GITHUB_SHA')))
  print(str(count)+' immutable synthetic native cases dispatched'+('' if count==len(CASES) else ', '+str(len(CASES)-count)+' deferred (no status)')+'; results use separate commit statuses.')
 except Exception:raise SystemExit('Native-case dispatch failed; no raw response, input, path or credential published.')
if __name__=='__main__':main()
