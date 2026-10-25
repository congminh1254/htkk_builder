"""Publish only static web output to a private orphan branch."""
import os,pathlib,re,shutil,subprocess,json,urllib.request,datetime
sha=os.environ['COMMIT_SHA']
if not re.fullmatch('[0-9a-f]{40}',sha):raise SystemExit('Invalid source SHA.')
root=pathlib.Path(os.environ['RUNNER_TEMP'])/'htkk-pages-output'
log=pathlib.Path(os.environ['RUNNER_TEMP'])/'htkk-builder-log.txt'
def safe_copy(source,target):
 for path in source.rglob('*'):
  if path.is_symlink() or '.git' in path.parts or path.suffix=='.map':raise ValueError('Unexpected output')
 shutil.copytree(source,target)
def run(args,env):
 with log.open('ab') as output:subprocess.run(args,cwd=root,env=env,stdout=output,stderr=subprocess.STDOUT,check=True)
try:
 shutil.rmtree(root,ignore_errors=True);root.mkdir()
 safe_copy(pathlib.Path('source/out'),root/'site')
 if (root/'site/downloads').exists():raise ValueError('Retired downloads must not be published')
 (root/'site/.nojekyll').touch()
 (root/'.htkk-build.json').write_text(json.dumps({'sourceSha':sha,'checks':'passed','builtAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'builderRepository':os.environ.get('GITHUB_REPOSITORY',''),'builderRunId':os.environ.get('GITHUB_RUN_ID','')}))
 env={key:os.environ[key] for key in ('PATH','HOME','RUNNER_TEMP') if key in os.environ}
 env.update(GIT_TERMINAL_PROMPT='0',GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL='/dev/null')
 run(['git','init','-b','pages-output'],env)
 run(['git','config','user.name','HTKK Builder'],env);run(['git','config','user.email','builder@users.noreply.github.com'],env)
 run(['git','add','site','.htkk-build.json'],env);run(['git','commit','-m','Publish verified static output'],env)
 # Credential appears only in an ephemeral HTTP header configuration, never in URL/argv.
 env.update(GIT_CONFIG_COUNT='1',GIT_CONFIG_KEY_0='http.https://github.com/.extraheader')
 import base64
 env['GIT_CONFIG_VALUE_0']='AUTHORIZATION: basic '+base64.b64encode(('x-access-token:'+os.environ['SOURCE_PUBLISH_TOKEN']).encode()).decode()
 def api(path,payload=None):
  request=urllib.request.Request('https://api.github.com/repos/congminh1254/htkk_web/'+path,data=json.dumps(payload).encode() if payload is not None else None,headers={'Authorization':'Bearer '+os.environ['SOURCE_PUBLISH_TOKEN'],'Accept':'application/vnd.github+json'},method='POST' if payload is not None else 'GET')
  with urllib.request.urlopen(request,timeout=30) as response:
   content=response.read()
   return json.loads(content) if content else None
 if api('branches/main')['commit']['sha']!=sha:raise ValueError('Release superseded')
 run(['git','push','--force','https://github.com/congminh1254/htkk_web.git','HEAD:refs/heads/pages-output'],env)
 pages_commit=subprocess.run(['git','rev-parse','HEAD'],cwd=root,env=env,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,check=True).stdout.decode().strip()
 if not re.fullmatch('[0-9a-f]{40}',pages_commit):raise ValueError()
 api('dispatches',{'event_type':'htkk-pages-ready','client_payload':{'pages_commit':pages_commit,'source_sha':sha}})
except Exception:raise SystemExit('Private output publication failed; diagnostics were not published.')
finally:shutil.rmtree(root,ignore_errors=True)
print('Static output published to private branch.')
