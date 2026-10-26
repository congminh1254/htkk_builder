"""Trusted fixed-case dispatch only; never executes private source code."""
import json,os,pathlib,re,urllib.request,urllib.error
REPO='congminh1254/htkk_web'
BUILDER='congminh1254/htkk_builder'
CASES=('01GTGT-zero-M10-2026','01GTGT-sale10-M10-2026','01GTGT-sale10-half-M10-2026','01GTGT-sale10-manual-M10-2026','01GTGT-sale5-half-M10-2026','01GTGT-sale5-manual-M10-2026','01GTGT-noactivity-zero-M10-2026','01GTGT-noactivity-reset-sale10-M10-2026','01GTGT-noactivity-cancel-sale10-M10-2026','01GTGT-noactivity-uncheck-sale10-M10-2026','01GTGT-noactivity-keep-credit-M10-2026','01GTGT-zero-Q4-2026','01GTGT-native-import-sale10-M10-2026')
CONTEXTS=dict(zip(CASES,('htkk-native/zero','htkk-native/sale10','htkk-native/sale10-half','htkk-native/sale10-manual','htkk-native/sale5-half','htkk-native/sale5-manual','htkk-native/noactivity-zero','htkk-native/noactivity-reset-sale10','htkk-native/noactivity-cancel-sale10','htkk-native/noactivity-uncheck-sale10','htkk-native/noactivity-keep-credit','htkk-native/quarter-zero','htkk-native/native-import-sale10')))
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args):return None
def sha(value):
 if not isinstance(value,str) or not re.fullmatch('[0-9a-f]{40}',value):raise ValueError('SHA')
 return value
def publication(body,expected):
 sha(expected)
 if not isinstance(body,bytes) or len(body)>16384:raise ValueError('PUBLICATION')
 def unique(pairs):
  value={}
  for key,item in pairs:
   if key in value:raise ValueError('PUBLICATION')
   value[key]=item
  return value
 value=json.loads(body.decode('utf-8'),object_pairs_hook=unique)
 if type(value) is not dict or set(value)!= {'format','sourceCommit','cases'} or value['format']!='htkk-web-input-publication-v1' or value['sourceCommit']!=expected or type(value['cases']) is not list or len(value['cases'])!=len(CASES):raise ValueError('PUBLICATION')
 for item,case in zip(value['cases'],CASES):
  if type(item) is not dict or set(item)!={'caseId','artifactCommit'} or item['caseId']!=case:raise ValueError('PUBLICATION')
  sha(item['artifactCommit'])
 return value

def post(url,token,payload):
 if not isinstance(token,str) or not token:raise ValueError('AUTH')
 request=urllib.request.Request(url,data=json.dumps(payload,separators=(',',':')).encode(),headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','Content-Type':'application/json','User-Agent':'HTKK-Fixed-Native-Dispatch/1.0'},method='POST')
 with urllib.request.build_opener(NoRedirect()).open(request,timeout=30) as response:
  if response.status not in (201,204):raise ValueError('HTTP')

def dispatch(value,actions_token,status_token,send=post):
 for item in value['cases']:
  send('https://api.github.com/repos/'+REPO+'/statuses/'+value['sourceCommit'],status_token,{'state':'pending','context':CONTEXTS[item['caseId']],'description':'Fixed synthetic native case queued'})
  try:
   send('https://api.github.com/repos/'+BUILDER+'/actions/workflows/probe-htkk-windows.yml/dispatches',actions_token,{'ref':'main','inputs':{'install_and_probe':True,'synthetic_login':True,'acknowledge_registration':True,'runtime_host':'clr2-x86-reference','gui_automation':'gtgt-web-import-inspect','web_source_sha':value['sourceCommit'],'web_case_id':item['caseId'],'web_artifact_commit':item['artifactCommit']}})
  except Exception:
   send('https://api.github.com/repos/'+REPO+'/statuses/'+value['sourceCommit'],status_token,{'state':'failure','context':CONTEXTS[item['caseId']],'description':'Fixed synthetic native case dispatch failed'})
   raise

def main():
 try:
  if os.environ.get('GITHUB_REPOSITORY')!=BUILDER:raise ValueError('BUILDER')
  path=pathlib.Path(os.environ['RUNNER_TEMP'])/'htkk-web-input-publication.json'
  if path.is_symlink() or not path.is_file() or path.stat().st_size>16384:raise ValueError('PUBLICATION')
  value=publication(path.read_bytes(),os.environ['COMMIT_SHA'])
  dispatch(value,os.environ.get('BUILDER_ACTIONS_TOKEN'),os.environ.get('SOURCE_STATUS_TOKEN'))
  print('Four immutable synthetic native cases dispatched; results use separate commit statuses.')
 except Exception:raise SystemExit('Native-case dispatch failed; no raw response, input, path or credential published.')
if __name__=='__main__':main()
