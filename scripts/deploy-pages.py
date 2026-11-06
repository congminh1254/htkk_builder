"""Deploy a verified Pages artifact with a unique build version, then prove the public site serves it.

actions/deploy-pages@v4 always sends GITHUB_SHA (the builder commit) as pages_build_version.
Two releases on one builder commit then reuse one deployment ID and GitHub Pages keeps the
previous content while still reporting success. This script calls the same REST endpoint with
a version bound to the immutable private artifact commit plus this run attempt, and refuses to
call the deployment done until https://hotrokekhai.net/build.json reports the artifact source SHA.
Logs carry only SHAs, run numbers and status words.
"""
import json,os,pathlib,re,sys,time,urllib.parse,urllib.request
BUILDER='congminh1254/htkk_builder'
SITE='https://hotrokekhai.net'
API='https://api.github.com/repos/'+BUILDER+'/pages/deployments'
DEPLOY_TIMEOUT=600
VERIFY_TIMEOUT=600
POLL=30
SUCCESS='succeed'
# Same final states as actions/deploy-pages@v4; deployment_attempt_error is retried by Pages itself.
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
def build_version(pages_commit,run_id,run_attempt):
 # Unique per artifact and per attempt: a new release on an unchanged builder and a manual
 # retry of the same artifact both get a fresh deployment instead of a deduplicated one.
 return sha(pages_commit)+'-'+number(run_id)+'-'+number(run_attempt)
def payload(artifact_id,version,oidc_token):
 if not isinstance(artifact_id,str) or not re.fullmatch('[1-9][0-9]{0,19}',artifact_id):raise ValueError('ARTIFACT_ID')
 if not isinstance(oidc_token,str) or not oidc_token:raise ValueError('OIDC')
 return {'artifact_id':int(artifact_id),'pages_build_version':version,'oidc_token':oidc_token}
def classify(status):
 if status==SUCCESS:return True
 if status in FAILED:raise ValueError('DEPLOYMENT_FAILED')
 return False
def observed(body):
 """Return sourceSha from a public build.json body, or None when it is absent or malformed."""
 try:value=json.loads(body).get('sourceSha')
 except (ValueError,AttributeError):return None
 return value if isinstance(value,str) and re.fullmatch('[0-9a-f]{40}',value) else None
def probe_url(base,version,attempt):
 return base+'/build.json?'+urllib.parse.urlencode({'deploy':version,'probe':str(attempt)})
def request(method,url,token=None,data=None,limit=200_000):
 headers={'Accept':'application/vnd.github+json','User-Agent':'HTKK-Verified-Pages/1.0','Cache-Control':'no-cache','Pragma':'no-cache'}
 if token:headers['Authorization']='Bearer '+token;headers['X-GitHub-Api-Version']='2022-11-28'
 body=None if data is None else json.dumps(data).encode()
 if body is not None:headers['Content-Type']='application/json'
 req=urllib.request.Request(url,data=body,method=method,headers=headers)
 with urllib.request.build_opener(NoRedirect()).open(req,timeout=30) as response:
  content=response.read(limit+1)
  if len(content)>limit:raise ValueError('RESPONSE_SIZE')
  return content
def oidc_token():
 url=os.environ['ACTIONS_ID_TOKEN_REQUEST_URL'];token=os.environ['ACTIONS_ID_TOKEN_REQUEST_TOKEN']
 req=urllib.request.Request(url,headers={'Authorization':'bearer '+token,'Accept':'application/json','User-Agent':'HTKK-Verified-Pages/1.0'})
 with urllib.request.build_opener(NoRedirect()).open(req,timeout=30) as response:value=json.loads(response.read(100_000)).get('value')
 if not isinstance(value,str) or not value:raise ValueError('OIDC')
 return value
def wait_deployment(get_status,timeout=DEPLOY_TIMEOUT,poll=POLL,sleep=time.sleep,clock=time.monotonic):
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
def env_out(name,line):
 path=os.environ.get(name)
 if path:
  with open(path,'a') as handle:handle.write(line+'\n')
def expect():
 site=pathlib.Path('output/site/build.json')
 value=sha(json.loads(site.read_text()).get('sourceSha'))
 env_out('GITHUB_ENV','EXPECTED_SOURCE_SHA='+value)
 print('Artifact sourceSha: '+value)
def deploy():
 if os.environ.get('GITHUB_REPOSITORY')!=BUILDER or os.environ.get('GITHUB_REF')!='refs/heads/main':raise ValueError('BUILDER')
 version=build_version(os.environ['PAGES_COMMIT'],os.environ['GITHUB_RUN_ID'],os.environ['GITHUB_RUN_ATTEMPT'])
 token=os.environ['GH_TOKEN']
 created=json.loads(request('POST',API,token,payload(os.environ.get('ARTIFACT_ID',''),version,oidc_token())))
 status_tail=str(created.get('status_url') or '').rstrip('/').split('/')[-1]
 deployment=str(created.get('id') or status_tail or version)
 if not re.fullmatch('[0-9a-zA-Z_.-]{1,120}',deployment):raise ValueError('DEPLOYMENT_ID')
 print('Created Pages deployment '+deployment+' for build version '+version)
 if deployment==os.environ.get('GITHUB_SHA'):raise ValueError('DEPLOYMENT_ID_IS_BUILDER_SHA')
 status_url=API+'/'+urllib.parse.quote(deployment,safe='')
 try:wait_deployment(lambda:json.loads(request('GET',status_url,token)).get('status'))
 except Exception:
  try:request('POST',status_url+'/cancel',token,{})
  except Exception:pass
  raise
 page_url=created.get('page_url')
 env_out('GITHUB_OUTPUT','page_url='+(page_url if isinstance(page_url,str) and re.fullmatch(r'https://[A-Za-z0-9./_-]{1,200}',page_url) else SITE+'/'))
 env_out('GITHUB_ENV','PAGES_BUILD_VERSION='+version)
def verify():
 expected=sha(os.environ['EXPECTED_SOURCE_SHA']);version=os.environ.get('PAGES_BUILD_VERSION','')
 if not re.fullmatch('[0-9a-f]{40}-[0-9]+-[0-9]+',version):raise ValueError('VERSION')
 attempts=wait_public(lambda attempt:request('GET',probe_url(SITE,version,attempt)),expected)
 print('Public site serves artifact sourceSha '+expected+' after '+str(attempts)+' probe(s).')
def main(argv):
 {'expect':expect,'deploy':deploy,'verify':verify}[argv[1]]()
if __name__=='__main__':
 try:main(sys.argv)
 except Exception as error:
  code=str(error) if re.fullmatch('[A-Z_]{2,40}',str(error)) else type(error).__name__+(' '+str(error.code) if isinstance(getattr(error,'code',None),int) else '')
  raise SystemExit('Pages deployment or public verification failed: '+code)
