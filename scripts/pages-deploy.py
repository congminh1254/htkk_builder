"""Deploy each verified HTKK artifact under its own Pages build version and prove it is live.

actions/deploy-pages@v4 sends GITHUB_SHA (the builder commit) as pages_build_version; the Pages
deployment ID is that SHA, so a second release on an unchanged builder reports success while the
site keeps the previous content (Pages 108/109). A version that is not a repository commit is
rejected with HTTP 404 (Pages 111). Each deployment therefore gets a real, unique commit: a marker
on the orphan branch `pages-deploy-log` (never merged into main) holding only provenance JSON.

  expect  read the validated artifact's public sourceSha (job output, SHA only)
  marker  create and push the marker commit (contents: write job, no artifact checkout)
  deploy  POST /repos/{repo}/pages/deployments with pages_build_version = marker SHA, poll
  verify  poll https://hotrokekhai.net/build.json until it serves the artifact sourceSha

Logs carry only SHAs, run IDs, status words and a filtered, bounded API error message.
"""
import base64,json,os,pathlib,re,subprocess,sys,tempfile,time,urllib.error,urllib.parse,urllib.request
BUILDER='congminh1254/htkk_builder'
REMOTE='https://github.com/'+BUILDER+'.git'
LOG_BRANCH='pages-deploy-log'
LOG_REF='refs/heads/'+LOG_BRANCH
MARKER_FILE='pages-deployment.json'
MARKER_MESSAGE='Pages deployment marker'
BOT=('github-actions[bot]','41898282+github-actions[bot]@users.noreply.github.com')
SITE='https://hotrokekhai.net'
API='https://api.github.com/repos/'+BUILDER
DEPLOY_TIMEOUT=600
VERIFY_TIMEOUT=600
POLL=30
DEPLOY_POLL=5
# Same final states as actions/deploy-pages@v4; deployment_attempt_error is retried by Pages.
FAILED=('deployment_failed','deployment_perms_error','deployment_content_failed','deployment_cancelled','deployment_lost')
MAX_STATUS_ERRORS=10
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args):return None
def sha(value):
 if not isinstance(value,str) or not re.fullmatch('[0-9a-f]{40}',value):raise ValueError('SHA')
 return value
def number(value):
 if not isinstance(value,str) or not re.fullmatch('[1-9][0-9]{0,19}',value):raise ValueError('RUN')
 return value
def env_out(name,line):
 path=os.environ.get(name)
 if path:
  with open(path,'a') as handle:handle.write(line+'\n')
def trusted_context():
 if os.environ.get('GITHUB_REPOSITORY')!=BUILDER or os.environ.get('GITHUB_REF')!='refs/heads/main':raise ValueError('BUILDER')
# ---- provenance marker -------------------------------------------------------------------
def provenance(pages_commit,source_sha,builder_sha,run_id,run_attempt):
 return {'pagesCommit':sha(pages_commit),'sourceSha':sha(source_sha),'builderSha':sha(builder_sha),'runId':number(run_id),'runAttempt':number(run_attempt),'workflow':'.github/workflows/pages.yml'}
def provenance_bytes(record):
 return (json.dumps(record,sort_keys=True,indent=1)+'\n').encode()
def push_args(commit,old,remote=REMOTE):
 # Lease: the branch must still be at `old` (or absent when old is empty); only the log ref moves.
 return ['push','--porcelain','--force-with-lease='+LOG_REF+':'+(old or ''),remote,sha(commit)+':'+LOG_REF]
def auth_env(token):
 if not token:raise ValueError('TOKEN')
 header='AUTHORIZATION: basic '+base64.b64encode(('x-access-token:'+token).encode()).decode()
 return {'GIT_CONFIG_COUNT':'1','GIT_CONFIG_KEY_0':'http.https://github.com/.extraheader','GIT_CONFIG_VALUE_0':header}
def git(repo,*args,data=None,env=None):
 base={k:v for k,v in os.environ.items() if not k.startswith('GIT_CONFIG_')}
 base.update(GIT_TERMINAL_PROMPT='0',GIT_AUTHOR_NAME=BOT[0],GIT_AUTHOR_EMAIL=BOT[1],GIT_COMMITTER_NAME=BOT[0],GIT_COMMITTER_EMAIL=BOT[1],**(env or {}))
 result=subprocess.run(['git','-C',repo,*args],input=data,capture_output=True,env=base,timeout=120)
 if result.returncode:raise ValueError('GIT_'+re.sub('[^A-Z]','_',args[0].upper()))
 return result.stdout.decode().strip()
def remote_head(repo,remote=REMOTE):
 line=git(repo,'ls-remote',remote,LOG_REF)
 return sha(line.split()[0]) if line else ''
def make_marker(repo,record,old,remote=REMOTE):
 if old:git(repo,'fetch','--quiet','--depth=1',remote,LOG_REF)
 blob=git(repo,'hash-object','-w','--stdin',data=provenance_bytes(record))
 tree=git(repo,'mktree',data=('100644 blob '+sha(blob)+'\t'+MARKER_FILE+'\n').encode())
 return sha(git(repo,'commit-tree',sha(tree),*(['-p',old] if old else []),'-m',MARKER_MESSAGE))
def marker():
 trusted_context()
 record=provenance(os.environ['PAGES_COMMIT'],os.environ['EXPECTED_SOURCE_SHA'],os.environ['GITHUB_SHA'],os.environ['GITHUB_RUN_ID'],os.environ['GITHUB_RUN_ATTEMPT'])
 with tempfile.TemporaryDirectory() as repo:
  git(repo,'init','--quiet','--bare')
  old=remote_head(repo)
  commit=make_marker(repo,record,old)
  git(repo,*push_args(commit,old),env=auth_env(os.environ['GH_TOKEN']))
 env_out('GITHUB_OUTPUT','marker_sha='+commit)
 print('Pushed Pages marker '+commit+' on '+LOG_BRANCH+' (parent '+(old or 'none')+')')
def check_marker(record,expected):
 if record!=expected:raise ValueError('MARKER_PROVENANCE')
# ---- deployment -------------------------------------------------------------------------
TOKENISH=re.compile(r'(gh[pousr]_[A-Za-z0-9_]{10,}|github_pat_[A-Za-z0-9_]{10,}|eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_.-]+|[A-Za-z0-9+/=_-]{40,})')
def api_error(status,body):
 """Bounded diagnostic for a failed Pages API call: status, filtered message and docs URL only."""
 try:data=json.loads(body[:4096])
 except (ValueError,TypeError):data={}
 if not isinstance(data,dict):data={}
 parts=[]
 for key in ('message','documentation_url'):
  value=data.get(key)
  if isinstance(value,str):parts.append(key+'='+TOKENISH.sub('[redacted]',re.sub(r'[^A-Za-z0-9 .,:;()/_#?=&-]','',value))[:200])
 return 'HTTP '+str(int(status))+(' '+' '.join(parts) if parts else '')
def request(method,url,token=None,data=None,limit=200_000):
 headers={'Accept':'application/vnd.github+json','User-Agent':'HTKK-Verified-Pages/1.0','Cache-Control':'no-cache','Pragma':'no-cache'}
 if token:headers['Authorization']='Bearer '+token;headers['X-GitHub-Api-Version']='2022-11-28'
 body=None if data is None else json.dumps(data).encode()
 if body is not None:headers['Content-Type']='application/json'
 req=urllib.request.Request(url,data=body,method=method,headers=headers)
 try:
  with urllib.request.build_opener(NoRedirect()).open(req,timeout=30) as response:
   content=response.read(limit+1)
 except urllib.error.HTTPError as error:
  try:detail=error.read(4096)
  except Exception:detail=b''
  print('Pages API '+method+' failed: '+api_error(error.code,detail))
  raise ValueError('API_HTTP_'+str(int(error.code)))
 if len(content)>limit:raise ValueError('RESPONSE_SIZE')
 return content
def payload(artifact_id,version,oidc_token):
 if not isinstance(artifact_id,str) or not re.fullmatch('[1-9][0-9]{0,19}',artifact_id):raise ValueError('ARTIFACT_ID')
 if not isinstance(oidc_token,str) or not oidc_token:raise ValueError('OIDC')
 return {'artifact_id':int(artifact_id),'pages_build_version':sha(version),'oidc_token':oidc_token}
def deployment_id(created,version):
 tail=str(created.get('status_url') or '').rstrip('/').split('/')[-1]
 value=str(created.get('id') or tail or version)
 if not re.fullmatch('[0-9a-zA-Z_.-]{1,120}',value):raise ValueError('DEPLOYMENT_ID')
 return value
def classify(status):
 if status=='succeed':return True
 if status in FAILED:raise ValueError('DEPLOYMENT_FAILED')
 return False
def wait_deployment(get_status,timeout=DEPLOY_TIMEOUT,poll=DEPLOY_POLL,sleep=time.sleep,clock=time.monotonic):
 deadline=clock()+timeout;errors=0
 while True:
  try:status=get_status();errors=0
  except Exception:
   status=None;errors+=1
   if errors>=MAX_STATUS_ERRORS:raise ValueError('DEPLOYMENT_STATUS_UNAVAILABLE')
  print('Pages deployment status: '+(status if isinstance(status,str) and re.fullmatch('[a-z_]{1,40}',status) else 'unknown'))
  if classify(status):return
  if clock()+poll>deadline:raise ValueError('DEPLOYMENT_TIMEOUT')
  sleep(poll)
def oidc_token():
 url=os.environ['ACTIONS_ID_TOKEN_REQUEST_URL'];token=os.environ['ACTIONS_ID_TOKEN_REQUEST_TOKEN']
 req=urllib.request.Request(url,headers={'Authorization':'Bearer '+token,'Accept':'application/json','User-Agent':'actions/oidc-client'})
 try:
  with urllib.request.build_opener(NoRedirect()).open(req,timeout=30) as response:value=json.loads(response.read(100_000)).get('value')
 except urllib.error.HTTPError as error:
  print('OIDC token request failed: HTTP '+str(int(error.code)));raise ValueError('OIDC_HTTP_'+str(int(error.code)))
 if not isinstance(value,str) or not value:raise ValueError('OIDC')
 return value
def retry(function,attempts=4,delay=5,sleep=time.sleep):
 # A just-pushed commit can take a moment to become visible to the REST API.
 for attempt in range(attempts):
  try:return function()
  except Exception:
   if attempt==attempts-1:raise
   sleep(delay)
def fallback_allowed(code):
 return code in ('API_HTTP_400','API_HTTP_404','API_HTTP_422')
def deploy():
 trusted_context()
 version=sha(os.environ['MARKER_SHA']);token=os.environ['GH_TOKEN']
 if version==os.environ.get('GITHUB_SHA'):raise ValueError('MARKER_IS_BUILDER_SHA')
 # The marker must be the commit this run pushed, with this run's provenance.
 expected=provenance(os.environ['PAGES_COMMIT'],os.environ['EXPECTED_SOURCE_SHA'],os.environ['GITHUB_SHA'],os.environ['GITHUB_RUN_ID'],os.environ['GITHUB_RUN_ATTEMPT'])
 content=retry(lambda:json.loads(request('GET',API+'/contents/'+MARKER_FILE+'?ref='+version,token)))
 if content.get('encoding')!='base64':raise ValueError('MARKER_PROVENANCE')
 check_marker(json.loads(base64.b64decode(content.get('content',''))),expected)
 artifact=os.environ.get('ARTIFACT_ID','');oidc=oidc_token()
 print('Creating Pages deployment for marker '+version+' (artifact '+artifact+')')
 try:created=json.loads(request('POST',API+'/pages/deployments',token,payload(artifact,version,oidc)))
 except ValueError as error:
  # Diagnostic fallback only: if Pages refuses a marker version, deploy as actions/deploy-pages
  # does. That works whenever the builder SHA is new; otherwise `verify` still fails the run.
  if not fallback_allowed(str(error)):raise
  version=sha(os.environ['GITHUB_SHA'])
  print('::warning title=Pages marker version refused::'+str(error)+'; retrying with builder SHA '+version+' (deploy-pages behaviour). The verify step decides.')
  created=json.loads(request('POST',API+'/pages/deployments',token,payload(artifact,version,oidc)))
 deployment=deployment_id(created,version)
 print('Created Pages deployment '+deployment+' for build version '+version)
 status_url=API+'/pages/deployments/'+urllib.parse.quote(deployment,safe='')
 try:wait_deployment(lambda:json.loads(request('GET',status_url,token)).get('status'))
 except Exception:
  try:request('POST',status_url+'/cancel',token,{})
  except Exception:pass
  raise
 page_url=created.get('page_url')
 env_out('GITHUB_OUTPUT','page_url='+(page_url if isinstance(page_url,str) and re.fullmatch(r'https://[A-Za-z0-9./_-]{1,200}',page_url) else SITE+'/'))
# ---- public verification ----------------------------------------------------------------
def observed(body):
 """Return sourceSha from a public build.json body, or None when it is absent or malformed."""
 try:value=json.loads(body).get('sourceSha')
 except (ValueError,AttributeError):return None
 return value if isinstance(value,str) and re.fullmatch('[0-9a-f]{40}',value) else None
def probe_url(base,token,attempt):
 return base+'/build.json?'+urllib.parse.urlencode({'deploy':token,'probe':str(attempt)})
def wait_public(fetch,expected,timeout=VERIFY_TIMEOUT,poll=POLL,sleep=time.sleep,clock=time.monotonic):
 """Poll the public build.json until it carries the expected source SHA; fail on deadline."""
 sha(expected);deadline=clock()+timeout;attempt=0
 while True:
  attempt+=1
  try:seen=observed(fetch(attempt))
  except Exception:seen=None
  print('Public build.json sourceSha: '+(seen or 'unavailable')+' (expected '+expected+')')
  if seen==expected:return attempt
  if clock()+poll>deadline:raise ValueError('PUBLIC_SITE_STALE')
  sleep(poll)
def expect():
 value=sha(json.loads(pathlib.Path('output/site/build.json').read_text()).get('sourceSha'))
 env_out('GITHUB_OUTPUT','source_sha='+value)
 print('Artifact sourceSha: '+value)
def verify():
 expected=sha(os.environ['EXPECTED_SOURCE_SHA']);version=sha(os.environ['MARKER_SHA'])
 attempts=wait_public(lambda attempt:request('GET',probe_url(SITE,version,attempt)),expected)
 print('Public site serves artifact sourceSha '+expected+' after '+str(attempts)+' probe(s).')
def main(argv):
 {'expect':expect,'marker':marker,'deploy':deploy,'verify':verify}[argv[1]]()
if __name__=='__main__':
 try:main(sys.argv)
 except Exception as error:
  code=str(error) if re.fullmatch('[A-Z0-9_]{2,40}',str(error)) else type(error).__name__
  raise SystemExit('Pages '+(sys.argv[1] if len(sys.argv)>1 and sys.argv[1] in ('expect','marker','deploy','verify') else 'step')+' failed: '+code)
