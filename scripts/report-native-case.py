"""Fixed status callback after the original process has stopped; no XML input."""
import importlib.util,os,pathlib
spec=importlib.util.spec_from_file_location('native_dispatch',pathlib.Path(__file__).with_name('dispatch-native-cases.py'));dispatch=importlib.util.module_from_spec(spec);spec.loader.exec_module(dispatch)
guard_spec=importlib.util.spec_from_file_location('native_callback_guard',pathlib.Path(__file__).with_name('callback_guard.py'));guard=importlib.util.module_from_spec(guard_spec);guard_spec.loader.exec_module(guard)
def publish_status(commit,value,environment):
 if not guard.allowed(commit,value['context'],environment.get('GITHUB_RUN_ID',''),environment.get('GITHUB_RUN_ATTEMPT',''),environment.get('SOURCE_READ_TOKEN')or environment.get('SOURCE_STATUS_TOKEN'),environment.get('GH_TOKEN'),input_commit=environment.get('WEB_ARTIFACT_COMMIT')):return False
 dispatch.post('https://api.github.com/repos/'+dispatch.REPO+'/statuses/'+commit,environment.get('SOURCE_STATUS_TOKEN'),value);return True

def payload(case,result,server,run,artifact=None):
 if case not in dispatch.CASES or result not in ('success','failure','cancelled','skipped') or server!='https://github.com' or not run.isdigit():raise ValueError('STATUS')
 if artifact is not None and not dispatch.sha(artifact):raise ValueError('ARTIFACT')
 value={'state':'success' if result=='success' else 'failure','context':dispatch.CONTEXTS[case],'description':'Fixed synthetic native case '+('passed' if result=='success' else 'did not pass'),'target_url':server+'/'+dispatch.BUILDER+'/actions/runs/'+run}
 if artifact:value['description']+=' input:'+artifact
 return value
def main():
 try:
  if os.environ.get('GITHUB_REPOSITORY')!=dispatch.BUILDER:raise ValueError('BUILDER')
  commit=dispatch.sha(os.environ.get('COMMIT_SHA'))
  value=payload(os.environ.get('WEB_CASE_ID'),os.environ.get('PROBE_RESULT'),os.environ.get('GITHUB_SERVER_URL'),os.environ.get('GITHUB_RUN_ID'),os.environ.get('WEB_ARTIFACT_COMMIT')or None)
  if not publish_status(commit,value,os.environ):print('Superseded native callback ignored.');return
  print('Fixed native-case status reported privately.')
 except Exception:raise SystemExit('Native-case callback failed; no raw response or credential published.')
if __name__=='__main__':main()
