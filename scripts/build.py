"""Keep private source diagnostics off the public Actions console."""
import os,pathlib,subprocess,shutil,json,re,datetime,importlib.util
source=pathlib.Path('source').resolve()
log=pathlib.Path(os.environ['RUNNER_TEMP'])/'htkk-builder-log.txt'
allowed=('PATH','HOME','TMPDIR','RUNNER_TEMP','RUNNER_TOOL_CACHE','LANG')
env={key:os.environ[key] for key in allowed if key in os.environ}
env.update(CI='1',NEXT_TELEMETRY_DISABLED='1',NEXT_PUBLIC_ADSENSE_ENABLED='true' if os.environ.get('ADSENSE_ENABLED') == 'true' else 'false')
STAGES={'npm ci':'install','npm run typecheck':'typecheck','npm test':'unit','npm run test:schemas':'schemas','npm audit --omit=dev --audit-level=high':'audit','npm run build':'build','npx playwright install --with-deps chromium':'browser-install','npm run test:e2e':'e2e','npm run test:e2e -- --reporter=line,json':'e2e','node scripts/check-htkk-source-cases.mjs':'source-cases'}
stage='setup';code='none'
def run(command):
 global stage,code
 stage=STAGES.get(' '.join(command),'cmd%d'%(len(command)))
 code='running'
 with log.open('ab') as output:
  result=subprocess.run(command,cwd=source,env=env,stdout=output,stderr=subprocess.STDOUT)
 code=str(result.returncode) if result.returncode>=0 else 'signal%d'%(-result.returncode)
 if result.returncode:raise RuntimeError()
def e2e_failure_locations():
 """Failing e2e specs as numbers only: index in the sorted list of spec files, test line, and @ the failing assertion lines. No names, titles or output."""
 try:
  report=json.loads((pathlib.Path(os.environ['RUNNER_TEMP'])/'htkk-e2e-report.json').read_text())
  files=sorted(p.name for p in (source/'tests/e2e').glob('*.spec.ts'))
  found=[]
  def walk(suite):
   for spec in suite.get('specs',[]):
    name=pathlib.PurePosixPath(str(spec.get('file',''))).name
    if spec.get('ok') is False and name in files and isinstance(spec.get('line'),int):
     # Line of the failing assertion inside the same spec file (numbers only), e.g. 6:117@140.
     lines=sorted({e['location']['line'] for t in spec.get('tests',[]) for r in t.get('results',[]) for e in r.get('errors',[]) if isinstance(e,dict) and isinstance(e.get('location'),dict) and isinstance(e['location'].get('line'),int) and pathlib.PurePosixPath(str(e['location'].get('file',''))).name==name})
     found.append('%d:%d'%(files.index(name),spec['line'])+''.join('@%d'%l for l in lines[:3]))
   for child in suite.get('suites',[]):walk(child)
  for suite in report.get('suites',[]):walk(suite)
  text=','.join(sorted(set(found))[:20])
  return text if re.fullmatch('[0-9:,@]{0,400}',text) else ''
 except Exception:return ''
try:
 for command in (['npm','ci'],['npm','run','typecheck'],['npm','test'],['npm','run','test:schemas'],['npm','audit','--omit=dev','--audit-level=high'],['npm','run','build']):run(command)
 browser=next((shutil.which(name) for name in ('google-chrome','chromium','chromium-browser') if shutil.which(name)),None)
 if not browser:
  run(['npx','playwright','install','--with-deps','chromium'])
  # Capture resolution output instead of emitting source-controlled output.
  with log.open('ab') as output:
   browser=subprocess.run(['node','-e','process.stdout.write(require("@playwright/test").chromium.executablePath())'],cwd=source,env=env,stdout=subprocess.PIPE,stderr=output,check=True).stdout.decode()
 env['CHROMIUM_PATH']=browser
 env['PLAYWRIGHT_JSON_OUTPUT_NAME']=str(pathlib.Path(os.environ['RUNNER_TEMP'])/'htkk-e2e-report.json')
 run(['npm','run','test:e2e','--','--reporter=line,json'])
 if (source/'scripts/check-htkk-source-cases.mjs').is_file():run(['node','scripts/check-htkk-source-cases.mjs'])
 if os.environ['BUILD_MODE']=='release':
  # Adapter/case metadata is trusted builder data, not commands supplied by a private plan.
  spec=importlib.util.spec_from_file_location('trusted_producer_batch',pathlib.Path(__file__).with_name('produce_case_batch.py'));batch=importlib.util.module_from_spec(spec);spec.loader.exec_module(batch)
  stage='producers'
  batch.produce(source,os.environ['RUNNER_TEMP'],env,log)
  stage='provenance'
  # Public provenance only; no source files or diagnostics enter this manifest.
  sha=subprocess.run(['git','rev-parse','HEAD'],cwd=source,env=env,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,check=True).stdout.decode().strip()
  version=json.loads((source/'package.json').read_text())['version']
  if not re.fullmatch('[0-9a-f]{40}',sha) or not isinstance(version,str) or not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?',version):raise RuntimeError()
  (source/'out/build.json').write_text(json.dumps({'sourceSha':sha,'version':version,'builtAt':datetime.datetime.now(datetime.timezone.utc).isoformat()},separators=(',',':'))+'\n')
  # Portable distribution is retired. Never carry stale download output forward.
  shutil.rmtree(source/'out/downloads',ignore_errors=True)
except Exception as error:
 if stage=='e2e':
  locations=e2e_failure_locations()
  if locations:print('e2e failures (spec index:line): '+locations)
 raise SystemExit('Build or verification failed at stage=%s code=%s error=%s. Private diagnostics were not published.'%(stage if re.fullmatch('[a-z0-9-]{1,20}',stage) else 'other',code if re.fullmatch('[a-z0-9-]{1,12}',code) else 'other',type(error).__name__ if re.fullmatch('[A-Za-z]{1,40}',type(error).__name__) else 'other'))
print('Build and verification passed.')
