"""Publish eight fixed synthetic inputs privately after trusted release checks.

Never executes private code. XML and manifests remain byte-for-byte unchanged;
the public output contains only bounded commit identifiers and fixed case names.
"""
import base64,hashlib,importlib.util,json,os,pathlib,re,stat,urllib.error,urllib.request

_spec=importlib.util.spec_from_file_location('htkk_web_input_reader',pathlib.Path(__file__).with_name('fetch-htkk-web-input.py'))
reader=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(reader)
REPO=reader.REPO
BUILDER=reader.BUILDER
CASES=(('01GTGT-zero-M10-2026','htkk-web-reference-zero-input','gtgt-web-reference-zero-input'),('01GTGT-sale10-M10-2026','htkk-web-reference-sale10-input','gtgt-web-reference-sale10-input'),('01GTGT-sale10-half-M10-2026','htkk-web-reference-sale10-half-input','gtgt-web-reference-sale10-half-input'),('01GTGT-sale10-manual-M10-2026','htkk-web-reference-sale10-manual-input','gtgt-web-reference-sale10-manual-input'),('01GTGT-sale5-half-M10-2026','htkk-web-reference-sale5-half-input','gtgt-web-reference-sale5-half-input'),('01GTGT-sale5-manual-M10-2026','htkk-web-reference-sale5-manual-input','gtgt-web-reference-sale5-manual-input'),('01GTGT-noactivity-zero-M10-2026', 'htkk-web-reference-noactivity-zero-input', 'gtgt-web-reference-noactivity-zero-input'),('01GTGT-noactivity-reset-sale10-M10-2026', 'htkk-web-reference-noactivity-reset-sale10-input', 'gtgt-web-reference-noactivity-reset-sale10-input'))
OUTPUT='htkk-web-input-publication.json'
PRODUCER='scripts/generate-htkk-web-reference.mjs'
MAX_PRODUCER=262144
CODES=frozenset(('AUTH','HTTP','NETWORK','API_SIZE','API_JSON','API_SHAPE','PRIVATE_REPO','SOURCE_COMMIT','STALE_SOURCE','SOURCE_PRODUCER','SOURCE_VERSION','MANIFEST','HASH','XML_SIZE','XML_ENCODING','XML_DECLARATION','XML_PARSE','XML_SERVICE','XML_PRIVACY','STAGING','BUILDER','IO','INTERNAL'))

class PublicationError(ValueError):
 def __init__(self,code):
  if code not in CODES:raise ValueError('Invalid safe publication code')
  self.code=code;super().__init__(code)

def fail(code):raise PublicationError(code)
def sha(value):
 if not isinstance(value,str) or not re.fullmatch('[0-9a-f]{40}',value):fail('SOURCE_COMMIT')
 return value
def safe_failure(error):
 code='INTERNAL';extra={}
 if isinstance(error,PublicationError):code=error.code if error.code in CODES else 'INTERNAL'
 elif isinstance(error,reader.InputError):code=error.code if error.code in CODES else 'INTERNAL'
 elif isinstance(error,urllib.error.HTTPError):
  code='AUTH' if error.code in (401,403) else 'HTTP'
  if type(error.code) is int and 100<=error.code<=599:extra['httpStatus']=error.code
 elif isinstance(error,urllib.error.URLError):code='NETWORK'
 elif isinstance(error,OSError):code='IO'
 return {'format':'htkk-web-input-publication-status-v1','status':'rejected','code':code,**extra}

class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args):return None

def api(path,token,payload=None,method=None):
 if not isinstance(token,str) or not token:fail('AUTH')
 request=urllib.request.Request('https://api.github.com/repos/'+REPO+path,data=None if payload is None else json.dumps(payload,separators=(',',':')).encode('utf-8'),method=method or ('GET' if payload is None else 'POST'),headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','Content-Type':'application/json','Accept-Encoding':'identity','User-Agent':'HTKK-Private-Synthetic-Input-Publisher/1.0'})
 with urllib.request.build_opener(NoRedirect()).open(request,timeout=30) as response:
  expected=200 if payload is None or method=='PATCH' else 201
  if response.status!=expected:fail('HTTP')
  body=response.read(reader.MAX_API+1)
 if len(body)>reader.MAX_API:fail('API_SIZE')
 return reader.json_object(body,'API_JSON')

def unsafe_path(path):
 # Reject POSIX symlinks and Windows junction/reparse paths, including ancestors.
 for part in (path,*path.parents):
  try:info=part.lstat()
  except FileNotFoundError:continue
  if stat.S_ISLNK(info.st_mode) or getattr(info,'st_file_attributes',0)&getattr(stat,'FILE_ATTRIBUTE_REPARSE_POINT',1024):return True
 return False

def safe_read(path,maximum):
 if unsafe_path(path):fail('STAGING')
 before=path.stat()
 if not stat.S_ISREG(before.st_mode) or not 0<before.st_size<=maximum:fail('STAGING')
 flags=os.O_RDONLY|getattr(os,'O_NOFOLLOW',0)|getattr(os,'O_BINARY',0)
 with os.fdopen(os.open(path,flags),'rb') as stream:
  actual=os.fstat(stream.fileno())
  if (before.st_dev,before.st_ino,before.st_size)!=(actual.st_dev,actual.st_ino,actual.st_size):fail('STAGING')
  body=stream.read(maximum+1)
  after=os.fstat(stream.fileno())
 if len(body)!=before.st_size or len(body)>maximum or (actual.st_size,actual.st_mtime_ns)!=(after.st_size,after.st_mtime_ns) or unsafe_path(path):fail('STAGING')
 return body

def read_inputs(runner_temp,source_commit):
 sha(source_commit);parent=pathlib.Path(runner_temp)
 if unsafe_path(parent) or not parent.is_dir():fail('STAGING')
 result=[]
 for case,directory,branch in CASES:
  folder=parent/directory
  if unsafe_path(folder) or not folder.is_dir() or set(p.name for p in folder.iterdir())!=set(reader.NAMES):fail('STAGING')
  files={name:safe_read(folder/name,reader.MAX_XML if name.endswith('.xml') else reader.MAX_MANIFEST) for name in reader.NAMES}
  manifest=reader.validate_manifest(files['manifest.json'])
  if manifest['caseId']!=case:fail('MANIFEST')
  if manifest['sourceCommit']!=source_commit:fail('SOURCE_COMMIT')
  body=files['01GTGT-web.xml']
  if len(body)!=manifest['bytes'] or hashlib.sha256(body).hexdigest()!=manifest['xmlSha256']:fail('HASH')
  reader.validate_web_xml(body,case_id=case)
  result.append((case,branch,files,manifest))
 if len({item[3]['producerSha256'] for item in result})!=1:fail('SOURCE_PRODUCER')
 return result

def assert_current(fetch,token,source_commit):
 current=fetch('/git/ref/heads/main',token)
 if not isinstance(current,dict) or current.get('ref')!='refs/heads/main' or not isinstance(current.get('object'),dict) or current['object'].get('type')!='commit':fail('API_SHAPE')
 if sha(current['object'].get('sha'))!=source_commit:fail('STALE_SOURCE')

def publish(inputs,source_commit,token,fetch=None):
 sha(source_commit)
 if not isinstance(token,str) or not token:fail('AUTH')
 # Require callers to use the validated fixed-case order and unchanged bytes.
 if not isinstance(inputs,list) or len(inputs)!=len(CASES):fail('STAGING')
 for item,(case,_,branch) in zip(inputs,CASES):
  if not isinstance(item,tuple) or len(item)!=4 or item[0]!=case or item[1]!=branch or set(item[2])!=set(reader.NAMES):fail('STAGING')
  manifest=reader.validate_manifest(item[2]['manifest.json'])
  if manifest!=item[3] or manifest['sourceCommit']!=source_commit or manifest['caseId']!=case:fail('MANIFEST')
  body=item[2]['01GTGT-web.xml']
  if len(body)!=manifest['bytes'] or hashlib.sha256(body).hexdigest()!=manifest['xmlSha256']:fail('HASH')
  reader.validate_web_xml(body,case_id=case)
 fetch=fetch or api
 info=fetch('',token)
 if not isinstance(info,dict) or info.get('private') is not True or info.get('full_name')!=REPO:fail('PRIVATE_REPO')
 source=fetch('/git/commits/'+source_commit,token)
 if not isinstance(source,dict) or source.get('sha')!=source_commit:fail('SOURCE_COMMIT')
 assert_current(fetch,token,source_commit)
 query='?ref='+source_commit
 # ContentsAPI path is nested; reader deliberately accepts only root paths.
 envelope=fetch('/contents/'+PRODUCER+query,token)
 if not isinstance(envelope,dict) or envelope.get('path')!=PRODUCER:fail('SOURCE_PRODUCER')
 normalized=dict(envelope);normalized['path']='generate-htkk-web-reference.mjs'
 producer=reader.content_file(normalized,'generate-htkk-web-reference.mjs',MAX_PRODUCER)
 producer_hash=hashlib.sha256(producer).hexdigest()
 package=reader.content_file(fetch('/contents/package.json'+query,token),'package.json',reader.MAX_MANIFEST)
 metadata=reader.json_object(package,'API_JSON')
 if any(item[3]['producerSha256']!=producer_hash for item in inputs):fail('SOURCE_PRODUCER')
 if any(metadata.get('version')!=item[3]['sourceVersion'] for item in inputs):fail('SOURCE_VERSION')
 cases=[]
 for case,branch,files,manifest in inputs:
  entries=[]
  for name in reader.NAMES:
   body=files[name]
   blob=fetch('/git/blobs',token,{'content':base64.b64encode(body).decode('ascii'),'encoding':'base64'})
   if not isinstance(blob,dict) or sha(blob.get('sha'))!=hashlib.sha1(b'blob '+str(len(body)).encode('ascii')+b'\0'+body).hexdigest():fail('HASH')
   entries.append({'path':name,'mode':'100644','type':'blob','sha':blob['sha']})
  tree=fetch('/git/trees',token,{'tree':entries})
  if not isinstance(tree,dict):fail('API_SHAPE')
  tree_sha=sha(tree.get('sha'))
  commit=fetch('/git/commits',token,{'message':'Synthetic web reference input '+case+' '+source_commit,'tree':tree_sha,'parents':[]})
  if not isinstance(commit,dict):fail('API_SHAPE')
  artifact=sha(commit.get('sha'))
  assert_current(fetch,token,source_commit)
  # GitHub PATCH of a missing ref can return 422. Only an explicit GET 404
  # establishes absence; never reinterpret a failed mutation as permission to
  # create a ref or retry authorization/validation errors.
  missing=False
  try:existing=fetch('/git/ref/heads/'+branch,token)
  except urllib.error.HTTPError as error:
   if error.code!=404:raise
   missing=True
  if missing:
   updated=fetch('/git/refs',token,{'ref':'refs/heads/'+branch,'sha':artifact})
  else:
   if not isinstance(existing,dict) or existing.get('ref')!='refs/heads/'+branch or not isinstance(existing.get('object'),dict) or existing['object'].get('type')!='commit':fail('API_SHAPE')
   sha(existing['object'].get('sha'))
   updated=fetch('/git/refs/heads/'+branch,token,{'sha':artifact,'force':True},'PATCH')
  if not isinstance(updated,dict) or updated.get('ref')!='refs/heads/'+branch or not isinstance(updated.get('object'),dict) or updated['object'].get('type')!='commit' or updated['object'].get('sha')!=artifact:fail('API_SHAPE')
  cases.append({'caseId':case,'artifactCommit':artifact})
 assert_current(fetch,token,source_commit)
 return {'format':'htkk-web-input-publication-v1','sourceCommit':source_commit,'cases':cases}

def save_result(result,runner_temp):
 parent=pathlib.Path(runner_temp);path=parent/OUTPUT
 if unsafe_path(parent) or not parent.is_dir() or path.exists() or path.is_symlink():fail('STAGING')
 # Fresh exclusive fixed-path write; a failed run never leaves usable metadata.
 created=False
 try:
  with path.open('xb') as stream:
   created=True;stream.write((json.dumps(result,separators=(',',':'))+'\n').encode('ascii'))
 except Exception:
  if created:path.unlink(missing_ok=True)
  raise

def main():
 try:
  if os.environ.get('GITHUB_REPOSITORY')!=BUILDER:fail('BUILDER')
  source=sha(os.environ.get('COMMIT_SHA'));token=os.environ.get('SOURCE_PUBLISH_TOKEN') or os.environ.get('SOURCE_READ_TOKEN')
  if not token:fail('AUTH')
  runner_temp=os.environ['RUNNER_TEMP'];inputs=read_inputs(runner_temp,source)
  result=publish(inputs,source,token);save_result(result,runner_temp)
  print(json.dumps({'format':'htkk-web-input-publication-status-v1','status':'published','sourceCommit':source,'caseCount':len(result['cases'])},separators=(',',':')))
 except Exception as error:
  print(json.dumps(safe_failure(error),separators=(',',':')))
  raise SystemExit('Synthetic input publication failed; no XML, paths, credentials or raw remote error published.')

if __name__=='__main__':main()
