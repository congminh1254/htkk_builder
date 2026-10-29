"""Failure-only callback from a fresh job with no supplier/private-source execution."""
import importlib.util,os,pathlib,re
spec=importlib.util.spec_from_file_location('native_case_callback',pathlib.Path(__file__).with_name('report-native-case.py'));callback=importlib.util.module_from_spec(spec);spec.loader.exec_module(callback)
def request(env):
 if env.get('GITHUB_REPOSITORY')!=callback.dispatch.BUILDER or env.get('GITHUB_REF')!='refs/heads/main':raise ValueError('BUILDER')
 if env.get('READINESS_RESULT')not in ('failure','cancelled') or env.get('GUI_AUTOMATION')!='gtgt-web-import-inspect':raise ValueError('RESULT')
 commit=callback.dispatch.sha(env.get('COMMIT_SHA'));run=env.get('GITHUB_RUN_ID','')
 if not re.fullmatch('[1-9][0-9]{0,19}',run):raise ValueError('RUN')
 payload=callback.payload(env.get('WEB_CASE_ID'),'failure',env.get('GITHUB_SERVER_URL'),run)
 return 'https://api.github.com/repos/'+callback.dispatch.REPO+'/statuses/'+commit,payload
def main():
 try:
  url,payload=request(os.environ)
  token=os.environ.get('SOURCE_STATUS_TOKEN')
  if not token:raise ValueError('AUTH')
  callback.dispatch.post(url,token,payload)
 except Exception:raise SystemExit('Native failure callback rejected or unavailable; no raw response or credential published.')
 print('Whole native job failure reported privately from isolated job.')
if __name__=='__main__':main()
