"""Trusted batch launcher. Only credential-free children execute private product code."""
import importlib.util,json,os,pathlib,subprocess
_spec=importlib.util.spec_from_file_location('batch_case_policy',pathlib.Path(__file__).with_name('htkk_native_cases.py'));registry=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(registry)
ALLOWED_ENV=('PATH','HOME','TMPDIR','RUNNER_TEMP','RUNNER_TOOL_CACHE','LANG','CI','NEXT_TELEMETRY_DISABLED','NEXT_PUBLIC_ADSENSE_ENABLED','CHROMIUM_PATH')
def child_environment(environment):return {key:value for key,value in environment.items()if key in ALLOWED_ENV}
def produce(source,temporary,environment,log,execute=subprocess.run):
 source=pathlib.Path(source);temporary=pathlib.Path(temporary);env=child_environment(environment);env['TMPDIR']=str(temporary)
 plan_path=source/'data/htkk-case-plan.json'
 if plan_path.exists():
  if plan_path.is_symlink()or plan_path.stat().st_size>2_000_000:raise ValueError('CASE_PLAN')
  plan=registry.validate_plan(json.loads(plan_path.read_text()))
  # Staging is private and later authenticated against the immutable source blob.
  with (temporary/'htkk-source-case-plan.json').open('x')as stream:stream.write(json.dumps(plan,separators=(',',':')))
 for c in registry.CASES.values():
  a=registry.ADAPTERS[c['adapterId']];destination=temporary/c['stagingDirectory']
  if destination.exists()or destination.is_symlink():raise ValueError('STAGING_EXISTS')
  with pathlib.Path(log).open('ab')as output:
   result=execute(['node',a['producer'],'--case',c['producerCase'],str(destination)],cwd=source,env=env,stdout=output,stderr=subprocess.STDOUT)
  if result.returncode:raise ValueError('PRODUCER_FAILED')
 return len(registry.CASES)
