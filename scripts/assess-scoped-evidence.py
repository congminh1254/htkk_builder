"""Run checked-out main's offline assessor without any credential variables."""
import os,pathlib,signal,subprocess
root=pathlib.Path(os.environ['RUNNER_TEMP']);log=root/'htkk-evidence-private.log';group=None
try:
 allowed=('PATH','HOME','LANG','TMPDIR','RUNNER_TEMP','RUNNER_TOOL_CACHE')
 env={key:os.environ[key] for key in allowed if key in os.environ};env['CI']='1'
 with log.open('wb') as output:
  for args in (['npm','ci'],['node','scripts/assemble-htkk-evidence.mjs',str(root/'htkk-scoped-evidence')]):
   process=subprocess.Popen(args,cwd='source',env=env,stdout=output,stderr=subprocess.STDOUT,start_new_session=True)
   group=process.pid
   try:result=process.wait(timeout=300)
   except subprocess.TimeoutExpired:raise RuntimeError()
   finally:
    # Supplier is never executed. Reap any assessor/npm descendants before later credentials load.
    try:os.killpg(group,signal.SIGKILL)
    except ProcessLookupError:pass
    group=None
   if result:raise RuntimeError()
 print('Offline evidence assessment completed privately; qualification unchanged.')
except Exception:raise SystemExit('Evidence assessment failed; private diagnostics suppressed.')
finally:
 if group:
  try:os.killpg(group,signal.SIGKILL)
  except ProcessLookupError:pass
