"""Fixed status callback after the original process has stopped; no XML input."""
import importlib.util,os,pathlib
spec=importlib.util.spec_from_file_location('native_dispatch',pathlib.Path(__file__).with_name('dispatch-native-cases.py'));dispatch=importlib.util.module_from_spec(spec);spec.loader.exec_module(dispatch)
def payload(case,result,server,run):
 if case not in dispatch.CASES or result not in ('success','failure','cancelled','skipped') or server!='https://github.com' or not run.isdigit():raise ValueError('STATUS')
 return {'state':'success' if result=='success' else 'failure','context':dispatch.CONTEXTS[case],'description':'Fixed synthetic native case '+('passed' if result=='success' else 'did not pass'),'target_url':server+'/'+dispatch.BUILDER+'/actions/runs/'+run}
def main():
 try:
  if os.environ.get('GITHUB_REPOSITORY')!=dispatch.BUILDER:raise ValueError('BUILDER')
  commit=dispatch.sha(os.environ.get('COMMIT_SHA'))
  value=payload(os.environ.get('WEB_CASE_ID'),os.environ.get('PROBE_RESULT'),os.environ.get('GITHUB_SERVER_URL'),os.environ.get('GITHUB_RUN_ID'))
  dispatch.post('https://api.github.com/repos/'+dispatch.REPO+'/statuses/'+commit,os.environ.get('SOURCE_STATUS_TOKEN'),value)
  print('Fixed native-case status reported privately.')
 except Exception:raise SystemExit('Native-case callback failed; no raw response or credential published.')
if __name__=='__main__':main()
