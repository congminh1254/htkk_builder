"""Verify immutable private static output before publishing on the public builder."""
import json,os,pathlib,re,time,urllib.request
SOURCE='htkk-net/htkk_web'
BUILDER='congminh1254/htkk_builder'
CONTEXTS=tuple('htkk-native/'+x for x in ('zero','sale10','sale10-half','sale10-manual','sale5-half','sale5-manual','noactivity-zero','noactivity-reset-sale10','noactivity-cancel-sale10','noactivity-uncheck-sale10','noactivity-keep-credit','quarter-zero','native-import-sale10'))
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args):return None
def api(repo,path):
 token=os.environ['SOURCE_READ_TOKEN'] if repo==SOURCE else os.environ['GH_TOKEN']
 req=urllib.request.Request('https://api.github.com/repos/'+repo+'/'+path,headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','User-Agent':'HTKK-Verified-Pages/1.0'})
 with urllib.request.build_opener(NoRedirect()).open(req,timeout=30) as response:
  body=response.read(2_000_001)
  if len(body)>2_000_000:raise ValueError('API_SIZE')
  return json.loads(body)
def sha(value):
 if not isinstance(value,str) or not re.fullmatch('[0-9a-f]{40}',value):raise ValueError('SHA')
 return value
def validate(metadata,public,current,pages,expected,run):
 source=sha(metadata.get('sourceSha'));sha(pages);sha(expected)
 if pages!=expected or source!=current or public.get('sourceSha')!=source or metadata.get('checks')!='passed' or metadata.get('builderRepository')!=BUILDER:raise ValueError('STALE_OR_INVALID_ARTIFACT')
 run_id=metadata.get('builderRunId')
 if not isinstance(run_id,str) or not re.fullmatch('[1-9][0-9]*',run_id):raise ValueError('RUN_ID')
 if run.get('id')!=int(run_id) or run.get('repository',{}).get('full_name')!=BUILDER or run.get('path')!='.github/workflows/build.yml' or run.get('head_branch')!='main' or run.get('event')!='workflow_dispatch' or run.get('display_title')!='HTKK release' or run.get('status')!='completed' or run.get('conclusion')!='success':raise ValueError('UNVERIFIED_BUILD')
 sha(run.get('head_sha'))
 return source
def native_ready(statuses,builder_sha,get=api):
 latest={s['context']:s for s in reversed(statuses)}
 for context in CONTEXTS:
  status=latest.get(context,{})
  if status.get('state') in ('failure','error'):raise ValueError('NATIVE_FAILED')
  if status.get('state')!='success':return False
  url=status.get('target_url','')
  match=re.fullmatch(r'https://github\.com/congminh1254/htkk_builder/actions/runs/([1-9][0-9]*)',url)
  if not match:raise ValueError('NATIVE_PROVENANCE')
  run=get(BUILDER,'actions/runs/'+match[1])
  if run.get('path')!='.github/workflows/probe-htkk-windows.yml' or run.get('head_branch')!='main' or run.get('head_sha')!=builder_sha or run.get('status')!='completed' or run.get('conclusion')!='success':raise ValueError('NATIVE_PROVENANCE')
 return True
def static_tree(site):
 if not site.is_dir() or site.is_symlink():raise ValueError('SITE')
 for p in site.rglob('*'):
  if p.is_symlink() or any(x in ('.git','.github','node_modules') for x in p.relative_to(site).parts) or p.suffix in ('.map','.ts','.tsx','.py','.ps1'):raise ValueError('NON_STATIC_OUTPUT')
 if (site/'downloads').exists() or not (site/'index.html').is_file() or not (site/'dashboard/index.html').is_file() or (site/'CNAME').read_text().strip()!='hotrokekhai.net':raise ValueError('SITE')
def main():
 if os.environ.get('GITHUB_REPOSITORY')!=BUILDER or os.environ.get('GITHUB_REF')!='refs/heads/main':raise ValueError('BUILDER')
 root=pathlib.Path('output');metadata=json.loads((root/'.htkk-build.json').read_text());public=json.loads((root/'site/build.json').read_text());expected=sha(os.environ['PAGES_COMMIT'])
 run_id=metadata.get('builderRunId','')
 if not isinstance(run_id,str) or not re.fullmatch('[1-9][0-9]*',run_id):raise ValueError('RUN_ID')
 run=api(BUILDER,'actions/runs/'+run_id)
 source=validate(metadata,public,api(SOURCE,'commits/main')['sha'],api(SOURCE,'commits/pages-output')['sha'],expected,run)
 event_run=os.environ.get('EXPECTED_BUILD_RUN','')
 if event_run and event_run!=run_id:raise ValueError('EVENT_ARTIFACT_MISMATCH')
 static_tree(root/'site')
 deadline=time.monotonic()+1200
 while not native_ready(api(SOURCE,'commits/'+source+'/status?per_page=100')['statuses'],run['head_sha']):
  if time.monotonic()>=deadline:raise ValueError('NATIVE_TIMEOUT')
  print('Waiting for all 13 immutable native regression workflows.',flush=True);time.sleep(15)
 # Recheck after waiting, immediately before artifact upload.
 if api(SOURCE,'commits/main')['sha']!=source or api(SOURCE,'commits/pages-output')['sha']!=expected:raise ValueError('SUPERSEDED')
 print('Verified current-main static artifact and all 13 native regression workflows.')
if __name__=='__main__':
 try:main()
 except Exception:raise SystemExit('Pages provenance, static-output or native regression gate failed; no deployment authorized.')
