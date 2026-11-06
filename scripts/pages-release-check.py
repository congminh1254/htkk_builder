"""Guards around actions/deploy-pages for the verified HTKK website.

actions/deploy-pages@v4 sends GITHUB_SHA (the builder commit) as pages_build_version, and the
Pages deployment ID is that SHA. A second release on an unchanged builder commit reuses the ID:
the action reports success while the site keeps the previous content (run 42179175364).
A non-commit version is rejected by the Pages API with HTTP 404 (run 42183141113), so the
version cannot simply be made unique. Instead:

- guard:  fail before upload when a previous pages.yml run on this builder SHA already succeeded,
          with an explicit message, instead of a silent no-op deployment;
- expect: record the artifact's public build.json sourceSha;
- verify: after deployment, poll https://hotrokekhai.net/build.json (cache-busted, bounded) until
          it serves that sourceSha, else fail. Independent of how the deployment was made.
Logs carry only SHAs, run IDs and fixed words.
"""
import json,os,pathlib,re,sys,time,urllib.parse,urllib.request
BUILDER='congminh1254/htkk_builder'
WORKFLOW='pages.yml'
SITE='https://hotrokekhai.net'
VERIFY_TIMEOUT=600
POLL=30
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args):return None
def sha(value):
 if not isinstance(value,str) or not re.fullmatch('[0-9a-f]{40}',value):raise ValueError('SHA')
 return value
def number(value):
 if not isinstance(value,str) or not re.fullmatch('[1-9][0-9]{0,19}',value):raise ValueError('RUN')
 return value
def request(url,token=None,limit=2_000_000):
 headers={'Accept':'application/vnd.github+json','User-Agent':'HTKK-Verified-Pages/1.0','Cache-Control':'no-cache','Pragma':'no-cache'}
 if token:headers['Authorization']='Bearer '+token;headers['X-GitHub-Api-Version']='2022-11-28'
 with urllib.request.build_opener(NoRedirect()).open(urllib.request.Request(url,headers=headers),timeout=30) as response:
  content=response.read(limit+1)
  if len(content)>limit:raise ValueError('RESPONSE_SIZE')
  return content
def previous_deployments(runs,builder_sha,current_run):
 """IDs of other successful pages.yml runs on main for this builder SHA (each already used it as Pages version)."""
 sha(builder_sha);current=int(number(current_run));found=[]
 for run in runs:
  if run.get('id')==current or run.get('head_sha')!=builder_sha:continue
  if run.get('path')!='.github/workflows/'+WORKFLOW or run.get('head_branch')!='main':continue
  if run.get('status')=='completed' and run.get('conclusion')=='success':found.append(run['id'])
 return sorted(found)
def guard_message(builder_sha,runs):
 return ('Builder '+builder_sha+' was already deployed to GitHub Pages by run(s) '+', '.join(str(r) for r in runs)+'. '
  'actions/deploy-pages uses the builder SHA as the deployment ID, so this artifact would be dropped silently. '
  'Land a real builder change on main, then re-dispatch this workflow with the same pages_commit.')
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
def env_out(name,line):
 path=os.environ.get(name)
 if path:
  with open(path,'a') as handle:handle.write(line+'\n')
def guard():
 if os.environ.get('GITHUB_REPOSITORY')!=BUILDER or os.environ.get('GITHUB_REF')!='refs/heads/main':raise ValueError('BUILDER')
 builder=sha(os.environ['GITHUB_SHA']);current=number(os.environ['GITHUB_RUN_ID'])
 url='https://api.github.com/repos/'+BUILDER+'/actions/workflows/'+WORKFLOW+'/runs?'+urllib.parse.urlencode({'head_sha':builder,'status':'success','per_page':'100'})
 runs=json.loads(request(url,os.environ['GH_TOKEN'])).get('workflow_runs')
 if not isinstance(runs,list):raise ValueError('RUNS')
 found=previous_deployments(runs,builder,current)
 if found:
  print('::error title=Builder SHA already deployed::'+guard_message(builder,found))
  raise ValueError('BUILDER_SHA_ALREADY_DEPLOYED')
 print('Builder '+builder+' has not been used as a Pages deployment version yet.')
def expect():
 value=sha(json.loads(pathlib.Path('output/site/build.json').read_text()).get('sourceSha'))
 env_out('GITHUB_ENV','EXPECTED_SOURCE_SHA='+value)
 print('Artifact sourceSha: '+value)
def verify():
 expected=sha(os.environ['EXPECTED_SOURCE_SHA'])
 token=sha(os.environ['PAGES_COMMIT'])+'-'+number(os.environ['GITHUB_RUN_ID'])+'-'+number(os.environ['GITHUB_RUN_ATTEMPT'])
 attempts=wait_public(lambda attempt:request(probe_url(SITE,token,attempt),limit=200_000),expected)
 print('Public site serves artifact sourceSha '+expected+' after '+str(attempts)+' probe(s).')
def main(argv):
 {'guard':guard,'expect':expect,'verify':verify}[argv[1]]()
if __name__=='__main__':
 try:main(sys.argv)
 except Exception as error:
  code=str(error) if re.fullmatch('[A-Z_]{2,40}',str(error)) else type(error).__name__+(' '+str(error.code) if isinstance(getattr(error,'code',None),int) else '')
  raise SystemExit('Pages release check failed: '+code)
