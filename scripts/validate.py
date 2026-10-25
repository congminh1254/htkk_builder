"""Authorize only current main or a verified internal PR head. Never print API data."""
import json,os,re,urllib.request
REPO='congminh1254/htkk_web'
def get(path):
 request=urllib.request.Request('https://api.github.com/repos/'+REPO+'/'+path,headers={'Authorization':'Bearer '+os.environ['SOURCE_READ_TOKEN'],'Accept':'application/vnd.github+json'})
 with urllib.request.urlopen(request,timeout=30) as response:return json.load(response)
def main():
 sha=os.environ['COMMIT_SHA'];mode=os.environ['BUILD_MODE'];pr=os.environ.get('PR_NUMBER','')
 if not re.fullmatch('[0-9a-f]{40}',sha) or mode not in ('ci','release'):raise ValueError()
 # Require current main, not merely an arbitrary SHA claimed to be a release.
 if get('branches/main')['commit']['sha']==sha:return
 if mode!='ci' or not re.fullmatch('[1-9][0-9]*',pr):raise ValueError()
 data=get('pulls/'+pr)
 if data['state']!='open' or data['base']['ref']!='main' or data['head']['repo']['full_name']!=REPO or data['head']['sha']!=sha:raise ValueError()
if __name__=='__main__':
 try:main()
 except Exception:raise SystemExit('Source request rejected or authorization unavailable.')
 print('Source request authorized.')
