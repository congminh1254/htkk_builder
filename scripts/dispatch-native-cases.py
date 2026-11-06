"""Trusted fixed-case dispatch only; never executes private source code."""
import datetime,http.client,json,os,pathlib,re,time,urllib.parse,urllib.request,urllib.error
REPO='htkk-net/htkk_web'
BUILDER='congminh1254/htkk_builder'
import importlib.util
_spec=importlib.util.spec_from_file_location('trusted_case_metadata',pathlib.Path(__file__).with_name('htkk_native_cases.py'));case_registry=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(case_registry)
CASES=tuple(case_registry.CASES)
# Release/Pages/evidence cohort. Candidate cases still get their own dispatch and status.
GATE_CASES=tuple(case_registry.GATE_CASES)
CONTEXTS={id:c['statusContext']for id,c in case_registry.CASES.items()}
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args):return None
def sha(value):
 if not isinstance(value,str) or not re.fullmatch('[0-9a-f]{40}',value):raise ValueError('SHA')
 return value
def publication(body,expected):
 sha(expected)
 if not isinstance(body,bytes) or len(body)>16384:raise ValueError('PUBLICATION')
 def unique(pairs):
  value={}
  for key,item in pairs:
   if key in value:raise ValueError('PUBLICATION')
   value[key]=item
  return value
 value=json.loads(body.decode('utf-8'),object_pairs_hook=unique)
 if type(value) is not dict or set(value)!= {'format','sourceCommit','cases'} or value['format']!='htkk-web-input-publication-v1' or value['sourceCommit']!=expected or type(value['cases']) is not list or len(value['cases'])!=len(CASES):raise ValueError('PUBLICATION')
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
 return 'HTKK native case '+case+' ('+gui(case)+')'
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

def deliver(send,url,token,payload,sleep,confirm=None):
 """POST with bounded retries; confirm() is checked before re-sending a non-idempotent POST."""
 for attempt in range(len(RETRY_DELAYS)+1):
  try:send(url,token,payload);return
  except Exception as error:
   if not transient(error) or attempt==len(RETRY_DELAYS):raise
   sleep(RETRY_DELAYS[attempt])
   if confirm is not None:
    try:state=confirm()
    except Exception as check:
     if not transient(check):raise
     state=None
    if state is True:print('Native-case dispatch transient error; the run already exists, not re-dispatched.',flush=True);return
    if state is None:raise error # Unknown whether the run exists; fail closed rather than duplicate.
   print('Transient native-case API error; bounded retry '+str(attempt+1)+' of '+str(len(RETRY_DELAYS))+'.',flush=True)

def dispatch(value,actions_token,status_token,send=None,builder=None,get=None,sleep=None,now=None):
 send=send or post;get=get or get_json;sleep=sleep or time.sleep;now=now or (lambda:datetime.datetime.now(datetime.timezone.utc))
 if builder is not None:sha(builder)
 for item in value['cases']:
  status='https://api.github.com/repos/'+REPO+'/statuses/'+value['sourceCommit']
  # Commit statuses are last-writer hints, so a blind retry of the same pending status is safe.
  deliver(send,status,status_token,{'state':'pending','context':CONTEXTS[item['caseId']],'description':'Fixed synthetic native case queued input:'+item['artifactCommit']},sleep)
  started=now()
  # workflow_dispatch is not idempotent: only re-send once the exact case run is proven absent.
  confirm=None if builder is None else (lambda case=item['caseId'],started=started:created(case,builder,started,actions_token,get))
  try:
   deliver(send,'https://api.github.com/repos/'+BUILDER+'/actions/workflows/probe-htkk-windows.yml/dispatches',actions_token,{'ref':'main','inputs':{'install_and_probe':True,'synthetic_login':True,'acknowledge_registration':True,'runtime_host':'clr2-x86-reference','gui_automation':gui(item['caseId']),'web_source_sha':value['sourceCommit'],'web_case_id':item['caseId'],'web_artifact_commit':item['artifactCommit']}},sleep,confirm)
  except Exception:
   deliver(send,status,status_token,{'state':'failure','context':CONTEXTS[item['caseId']],'description':'Fixed synthetic native case dispatch failed'},sleep)
   raise

def main():
 try:
  if os.environ.get('GITHUB_REPOSITORY')!=BUILDER:raise ValueError('BUILDER')
  path=pathlib.Path(os.environ['RUNNER_TEMP'])/'htkk-web-input-publication.json'
  if path.is_symlink() or not path.is_file() or path.stat().st_size>16384:raise ValueError('PUBLICATION')
  value=publication(path.read_bytes(),os.environ['COMMIT_SHA'])
  dispatch(value,os.environ.get('BUILDER_ACTIONS_TOKEN'),os.environ.get('SOURCE_STATUS_TOKEN'),builder=sha(os.environ.get('GITHUB_SHA')))
  print(str(len(CASES))+' immutable synthetic native cases dispatched; results use separate commit statuses.')
 except Exception:raise SystemExit('Native-case dispatch failed; no raw response, input, path or credential published.')
if __name__=='__main__':main()
