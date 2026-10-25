"""Keep private source diagnostics off the public Actions console."""
import os,pathlib,subprocess,shutil
source=pathlib.Path('source').resolve()
log=pathlib.Path(os.environ['RUNNER_TEMP'])/'htkk-builder-log.txt'
allowed=('PATH','HOME','TMPDIR','RUNNER_TEMP','RUNNER_TOOL_CACHE','LANG')
env={key:os.environ[key] for key in allowed if key in os.environ}
env.update(CI='1',NEXT_TELEMETRY_DISABLED='1')
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
  env['HTKK_NODE_CACHE']=str(pathlib.Path(os.environ['RUNNER_TEMP'])/'htkk-node-runtime')
  run(['python3','scripts/fetch-node-runtime.py'])
  run(['node','scripts/package-portable.mjs'])
  downloads=source/'out/downloads';downloads.mkdir(exist_ok=True)
  for name in ('hotrokekhai-portable.zip','SHA256SUMS'):
   shutil.copy2(source/'dist'/name,downloads/name)
except Exception:raise SystemExit('Build or verification failed. Private diagnostics were not published.')
print('Build and verification passed.')
