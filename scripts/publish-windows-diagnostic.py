"""Publish only a bounded supplier-startup window image to the fixed PRIVATE repo.

No console image, artifact, raw window text, source checkout or diagnostic logs.
The GUI process never receives this step's credential.
"""
import base64,hashlib,json,os,pathlib,re,shutil,struct,urllib.request

REPO='congminh1254/htkk_web'
BRANCH='windows-reference-diagnostics'
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args):return None

def read_diagnostic(directory,run_id):
 if not re.fullmatch(r'[0-9]{1,20}',run_id):raise ValueError()
 if directory.is_symlink() or not directory.is_dir():raise ValueError()
 if {p.name for p in directory.iterdir()}!={'regsvr32-window.png','diagnostic.json'}:raise ValueError()
 files={}
 for name in ('regsvr32-window.png','diagnostic.json'):
  path=directory/name
  if path.is_symlink() or not path.is_file() or not 0<path.stat().st_size<=2_000_000:raise ValueError()
  files[name]=path.read_bytes()
 png=files['regsvr32-window.png']
 if len(png)<33 or png[:8]!=b'\x89PNG\r\n\x1a\n' or png[12:16]!=b'IHDR':raise ValueError()
 width,height=struct.unpack('>II',png[16:24])
 if not 16<=width<=2000 or not 16<=height<=2000:raise ValueError()
 metadata=json.loads(files['diagnostic.json'].decode('utf-8-sig'))
 expected={'format':'htkk-registration-diagnostic-v1','runId':run_id,'runtimeHost':metadata.get('runtimeHost'),'scope':'verified-microsoft-regsvr32-window-only','width':width,'height':height,'pngSha256':hashlib.sha256(png).hexdigest(),'taxDataUsed':False,'publicScreenshot':False}
 if metadata!=expected or metadata['runtimeHost'] not in ('original','clr2-x86-reference'):raise ValueError()
 # Canonical JSON removes any unexpected whitespace or untrusted representation.
 files['diagnostic.json']=(json.dumps(expected,separators=(',',':'))+'\n').encode()
 return files

def api(path,token,payload=None,method=None):
 request=urllib.request.Request('https://api.github.com/repos/'+REPO+path,data=json.dumps(payload).encode() if payload is not None else None,headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','User-Agent':'HTKK-Private-Startup-Diagnostic/1.0'},method=method or ('POST' if payload is not None else 'GET'))
 with urllib.request.build_opener(NoRedirect).open(request,timeout=30) as response:
  return json.load(response)

def publish(files,token):
 if api('',token).get('private') is not True:raise ValueError()
 entries=[]
 for name,body in files.items():
  sha=api('/git/blobs',token,{'content':base64.b64encode(body).decode(),'encoding':'base64'})['sha']
  if not re.fullmatch('[0-9a-f]{40}',sha):raise ValueError()
  entries.append({'path':name,'mode':'100644','type':'blob','sha':sha})
 tree=api('/git/trees',token,{'tree':entries})['sha']
 commit=api('/git/commits',token,{'message':'Private supplier startup diagnostic; no taxpayer data','tree':tree,'parents':[]})['sha']
 if not re.fullmatch('[0-9a-f]{40}',commit):raise ValueError()
 # No main/pages-output writes. Create once, then replace only this private branch.
 try:
  api('/git/ref/heads/'+BRANCH,token)
 except urllib.error.HTTPError as error:
  if error.code!=404:raise
  api('/git/refs',token,{'ref':'refs/heads/'+BRANCH,'sha':commit})
 else:
  api('/git/refs/heads/'+BRANCH,token,{'sha':commit,'force':True},'PATCH')
 return commit

def main():
 directory=pathlib.Path(os.environ['RUNNER_TEMP'])/'htkk-windows-diagnostic'
 if not directory.exists():
  print('No private startup image captured.');return
 try:
  files=read_diagnostic(directory,os.environ['GITHUB_RUN_ID'])
  commit=publish(files,os.environ['SOURCE_PUBLISH_TOKEN'])
  print('Private startup diagnostic published: '+commit)
 except Exception:
  raise SystemExit('Private startup diagnostic publication failed; no image or raw error published.')
 finally:
  if not directory.is_symlink():shutil.rmtree(directory,ignore_errors=True)

if __name__=='__main__':main()
