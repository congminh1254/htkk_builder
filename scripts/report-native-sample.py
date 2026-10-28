"""Trusted metadata-only pending/failure callback; never runs supplier/private code."""
import importlib.util,os,pathlib
spec=importlib.util.spec_from_file_location('sample_status',pathlib.Path(__file__).with_name('publish-htkk-native-sample.py'));p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
def report(state,source,builder,run,attempt,token,fetch=None):
 if state not in ('pending','failure'):p.fail('PROVENANCE')
 p.sha(source);p.sha(builder);p.number(run);p.number(attempt)
 if not isinstance(token,str) or not token:p.fail('AUTH')
 fetch=fetch or p.transport.api
 info=fetch('',token)
 if type(info) is not dict or info.get('private') is not True or info.get('full_name')!=p.REPO:p.fail('PRIVATE_REPO')
 head=fetch('/git/ref/heads/main',token)
 if type(head) is not dict or head.get('ref')!='refs/heads/main' or head.get('object',{}).get('type')!='commit' or head.get('object',{}).get('sha')!=source:p.fail('STALE_SOURCE')
 description=('Native harness sample queued' if state=='pending' else 'Native harness sample failed; no new success evidence')+'; builder '+builder[:12]+'; attempt '+attempt
 fetch('/statuses/'+source,token,{'state':state,'context':p.CONTEXT,'description':description,'target_url':'https://github.com/'+p.BUILDER+'/actions/runs/'+run+'/attempts/'+attempt})
def main():
 try:
  if os.environ.get('GITHUB_REPOSITORY')!=p.BUILDER:p.fail('BUILDER')
  report(os.environ.get('SAMPLE_STATE'),os.environ.get('EXPECTED_WEB_SOURCE_SHA'),os.environ.get('GITHUB_SHA'),os.environ.get('GITHUB_RUN_ID'),os.environ.get('GITHUB_RUN_ATTEMPT'),os.environ.get('SOURCE_STATUS_TOKEN'))
  print('Fixed native harness sample metadata status reported.')
 except Exception:raise SystemExit('Native harness sample callback rejected; no private source, response or credential logged.')
if __name__=='__main__':main()
