"""Resolve only immutable identifiers; no private source execution."""
import importlib.util,json,os,pathlib
_spec=importlib.util.spec_from_file_location('collect_scoped',pathlib.Path(__file__).with_name('collect-scoped-evidence.py'))
c=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(c)
def prepare(event,inputs,get=c.api):
 code=c.sha(get(c.SOURCE,'commits/main')['sha'])
 if event.get('workflow_run'):
  run=event['workflow_run'];actual=get(c.BUILDER,'actions/runs/'+str(run['id']))
  c.check(actual.get('repository',{}).get('full_name')==c.BUILDER and actual.get('head_branch')=='main' and actual.get('path')=='.github/workflows/pages.yml' and actual.get('status')=='completed' and actual.get('conclusion')=='success')
  artifact=c.sha(get(c.SOURCE,'git/ref/heads/pages-output')['object']['sha'])
  metadata=json.loads(c.raw(get,'.htkk-build.json',artifact))
  source=c.sha(metadata.get('sourceSha'));c.check(source==code and metadata.get('builderRepository')==c.BUILDER and metadata.get('checks')=='passed')
  release=get(c.BUILDER,'actions/runs/'+str(metadata['builderRunId']))
  c.check(release.get('path')=='.github/workflows/build.yml' and release.get('event')=='workflow_dispatch' and release.get('head_branch')=='main' and release.get('status')=='completed' and release.get('conclusion')=='success' and release.get('display_title')=='HTKK release')
  builder=c.sha(release.get('head_sha'))
 else:source=c.sha(inputs.get('source'));builder=c.sha(inputs.get('builder'))
 return {'CODE_SOURCE_SHA':code,'EVIDENCE_SOURCE_SHA':source,'NATIVE_BUILDER_SHA':builder}
if __name__=='__main__':
 try:
  c.check(os.environ.get('GITHUB_REPOSITORY')==c.BUILDER and os.environ.get('GITHUB_REF')=='refs/heads/main')
  event=json.loads(pathlib.Path(os.environ['GITHUB_EVENT_PATH']).read_text())
  values=prepare(event,{'source':os.environ.get('EVIDENCE_SOURCE_SHA'),'builder':os.environ.get('NATIVE_BUILDER_SHA')})
  with open(os.environ['GITHUB_ENV'],'a') as stream:
   for key,value in values.items():stream.write(key+'='+value+'\n')
  print('Immutable evidence/code source coordinates resolved.')
 except Exception:raise SystemExit('Evidence request rejected; private metadata suppressed.')
