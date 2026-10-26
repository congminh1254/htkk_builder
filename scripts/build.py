"""Keep private source diagnostics off the public Actions console."""
import os,pathlib,subprocess,shutil,json,re,datetime
source=pathlib.Path('source').resolve()
log=pathlib.Path(os.environ['RUNNER_TEMP'])/'htkk-builder-log.txt'
allowed=('PATH','HOME','TMPDIR','RUNNER_TEMP','RUNNER_TOOL_CACHE','LANG')
env={key:os.environ[key] for key in allowed if key in os.environ}
env.update(CI='1',NEXT_TELEMETRY_DISABLED='1',NEXT_PUBLIC_ADSENSE_ENABLED='true' if os.environ.get('ADSENSE_ENABLED') == 'true' else 'false')
def run(command):
 with log.open('ab') as output:
  result=subprocess.run(command,cwd=source,env=env,stdout=output,stderr=subprocess.STDOUT)
 if result.returncode:raise RuntimeError()
try:
 for command in (['npm','ci'],['npm','run','typecheck'],['npm','test'],['npm','run','test:schemas'],['npm','audit','--omit=dev','--audit-level=high'],['npm','run','build']):run(command)
 browser=next((shutil.which(name) for name in ('google-chrome','chromium','chromium-browser') if shutil.which(name)),None)
 if not browser:
  run(['npx','playwright','install','--with-deps','chromium'])
  # Capture resolution output instead of emitting source-controlled output.
  with log.open('ab') as output:
   browser=subprocess.run(['node','-e','process.stdout.write(require("@playwright/test").chromium.executablePath())'],cwd=source,env=env,stdout=subprocess.PIPE,stderr=output,check=True).stdout.decode()
 env['CHROMIUM_PATH']=browser
 run(['npm','run','test:e2e'])
 if os.environ['BUILD_MODE']=='release':
  # Actual source producer runs only after all CI checks, without credentials.
  # These eight directories contain fixed synthetic XML only; trusted publication
  # independently revalidates the entire allowlist before any authenticated I/O.
  reference_env=dict(env);reference_env['TMPDIR']=os.environ['RUNNER_TEMP']
  for case,suffix in (('zero','zero'),('sale10','sale10'),('sale10-half','sale10-half'),('sale10-manual','sale10-manual'),('sale5-half','sale5-half'),('sale5-manual','sale5-manual'),('noactivity-zero', 'noactivity-zero'),('noactivity-reset-sale10', 'noactivity-reset-sale10')):
   destination=pathlib.Path(os.environ['RUNNER_TEMP'])/('htkk-web-reference-'+suffix+'-input')
   if destination.exists() or destination.is_symlink():raise RuntimeError()
   with log.open('ab') as output:
    result=subprocess.run(['node','scripts/generate-htkk-web-reference.mjs','--case',case,str(destination)],cwd=source,env=reference_env,stdout=output,stderr=subprocess.STDOUT)
   if result.returncode:raise RuntimeError()
  # Public provenance only; no source files or diagnostics enter this manifest.
  sha=subprocess.run(['git','rev-parse','HEAD'],cwd=source,env=env,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,check=True).stdout.decode().strip()
  version=json.loads((source/'package.json').read_text())['version']
  if not re.fullmatch('[0-9a-f]{40}',sha) or not isinstance(version,str) or not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?',version):raise RuntimeError()
  (source/'out/build.json').write_text(json.dumps({'sourceSha':sha,'version':version,'builtAt':datetime.datetime.now(datetime.timezone.utc).isoformat()},separators=(',',':'))+'\n')
  # Portable distribution is retired. Never carry stale download output forward.
  shutil.rmtree(source/'out/downloads',ignore_errors=True)
except Exception:raise SystemExit('Build or verification failed. Private diagnostics were not published.')
print('Build and verification passed.')
