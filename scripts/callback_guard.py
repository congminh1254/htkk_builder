"""Ignore superseded status hints; immutable cohort proofs remain authoritative."""
import json,re,urllib.request
SOURCE='htkk-net/htkk_web';BUILDER='congminh1254/htkk_builder'
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args):return None
def read(repo,path,token):
 if repo not in (SOURCE,BUILDER)or not token or not re.fullmatch(r'[A-Za-z0-9_./?=&%-]+',path)or '..'in path:raise ValueError('CALLBACK_API')
 req=urllib.request.Request('https://api.github.com/repos/'+repo+'/'+path,headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','User-Agent':'HTKK-Callback-Guard/1.0'})
 with urllib.request.build_opener(NoRedirect()).open(req,timeout=30)as response:
  body=response.read(1_000_001)
  if len(body)>1_000_000:raise ValueError('CALLBACK_SIZE')
  return json.loads(body)
def allowed(source,context,run_id,attempt,source_token,actions_token,get=read,input_commit=None):
 if not re.fullmatch('[a-f0-9]{40}',source)or not re.fullmatch('[1-9][0-9]*',str(run_id))or not re.fullmatch('[1-9][0-9]*',str(attempt)):raise ValueError('CALLBACK_ID')
 if get(SOURCE,'commits/main',source_token).get('sha')!=source:return False
 run=get(BUILDER,'actions/runs/'+str(run_id),actions_token)
 if run.get('run_attempt')!=int(attempt):return False
 for page in range(1,11):
  statuses=get(SOURCE,'commits/'+source+'/statuses?per_page=100&page='+str(page),source_token)
  if type(statuses)is not list:raise ValueError('CALLBACK_STATUSES')
  for status in statuses:
   if status.get('context')!=context:continue
   marker=re.search(r'input:([a-f0-9]{40})',status.get('description',''))
   if status.get('state')=='pending'and marker and marker[1]!=input_commit:return False
   url=status.get('target_url')
   if not url:return True
   match=re.fullmatch(r'https://github\.com/congminh1254/htkk_builder/actions/runs/([1-9][0-9]*)',url)
   if not match:raise ValueError('CALLBACK_PROVENANCE')
   return int(match[1])<=int(run_id)
  if len(statuses)<100:return True
 raise ValueError('CALLBACK_TRUNCATED')
