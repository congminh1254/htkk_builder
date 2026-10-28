"""Private, inert, chunked source proposals; no public artifact or adapter writes."""
import base64,hashlib,importlib.util,json,pathlib,re,urllib.error
spec=importlib.util.spec_from_file_location('source_update',pathlib.Path(__file__).with_name('source-update.py'));u=importlib.util.module_from_spec(spec);spec.loader.exec_module(u)
BRANCH='official-source-proposals';CHUNK=4*1024*1024
KEYS=('format','sourceSha','builderSha','runId','runAttempt','credentialsSafe','ready','automaticActivation','result','files')
def validate(directory,source,builder,run,attempt):
 directory=pathlib.Path(directory);u.plain(directory/'bundle.json');b=u.load(directory/'bundle.json',64000);u.exact(b,KEYS)
 u.require(b['format']=='htkk-source-update-bundle-v1'and b['sourceSha']==u.gitsha(source)and b['builderSha']==u.gitsha(builder)and b['runId']==run and b['runAttempt']==attempt)
 u.require(isinstance(run,str)and re.fullmatch('[1-9][0-9]{0,19}',run)and type(attempt)is int and 1<=attempt<=100)
 u.require(b['credentialsSafe']is True and b['ready']is False and b['automaticActivation']is False and b['result']in('unchanged','review-required','unreachable','invalid'))
 u.require(type(b['files'])is list and 4<=len(b['files'])<=7);names=set();metadata=0
 for f in b['files']:
  u.exact(f,('path','sha256','bytes'));name=f['path'];u.require(name in u.META+u.ARCHIVES and name not in names);names.add(name)
  u.require(type(f['bytes'])is int and 0<f['bytes']<=(u.candidate.MAX_BYTES if name in u.ARCHIVES else u.MAX_META))
  u.require(u.file_info(directory/name)==f)
  if name in u.META:metadata+=f['bytes']
 u.require(metadata<=u.MAX_META and set(u.META[:4])<=names and {p.name for p in directory.iterdir()}==names|{'bundle.json'})
 u.validate_bundle_metadata(directory,b);return b

def publish_bundle(directory,source_sha,builder_sha,run_id,run_attempt,token,status_token,fetch=None):
 b=validate(directory,source_sha,builder_sha,run_id,run_attempt);directory=pathlib.Path(directory);fetch=fetch or u.watch.api
 def current():
  info=fetch('',token);u.require(info.get('private')is True and info.get('full_name')==u.REPO)
  u.require(u.gitsha(fetch('/branches/main',token)['commit']['sha'])==source_sha,'STALE_SOURCE')
 def blob(data):
  expected=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
  actual=u.gitsha(fetch('/git/blobs',token,{'encoding':'base64','content':base64.b64encode(data).decode()})['sha']);u.require(actual==expected,'GIT_BLOB_MISMATCH');return actual
 def entry(path,data):return {'path':path,'mode':'100644','type':'blob','sha':blob(data)}
 current();entries=[];archives=[]
 for f in b['files']:
  path=directory/f['path']
  if f['path']in u.ARCHIVES:
   chunks=[];index=0;digest=hashlib.sha256();size=0
   with u.plain(path).open('rb')as stream:
    while data:=stream.read(CHUNK):
     name='archives/'+('official'if f['path']=='official.rar'else'mirror')+'/'+str(index).zfill(4)+'.part';entries.append(entry(name,data));chunks.append({'path':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()});digest.update(data);size+=len(data);index+=1
   u.require(digest.hexdigest()==f['sha256']and size==f['bytes'],'SOURCE_CHANGED');archives.append({'file':f['path'],'sha256':f['sha256'],'bytes':f['bytes'],'chunks':chunks})
  else:entries.append(entry(f['path'],u.plain(path).read_bytes()))
 u.require(validate(directory,source_sha,builder_sha,run_id,run_attempt)==b,'SOURCE_CHANGED')
 reassembly={'format':'htkk-private-inert-source-parts-v1','sourceSha':source_sha,'builderSha':builder_sha,'runId':run_id,'runAttempt':run_attempt,'archives':archives,'ready':False,'automaticActivation':False}
 entries.append(entry('archive-parts.json',(json.dumps(reassembly,separators=(',',':'))+'\n').encode()));entries.append(entry('bundle.json',(json.dumps(b,separators=(',',':'))+'\n').encode()))
 current();tree=u.gitsha(fetch('/git/trees',token,{'tree':entries})['sha']);commit=u.gitsha(fetch('/git/commits',token,{'tree':tree,'parents':[],'message':'Private inert HTKK source proposal; never activate'})['sha']);current()
 try:fetch('/git/ref/heads/'+BRANCH,token)
 except urllib.error.HTTPError as error:
  if error.code!=404:raise
  fetch('/git/refs',token,{'ref':'refs/heads/'+BRANCH,'sha':commit})
 else:fetch('/git/refs/heads/'+BRANCH,token,{'sha':commit,'force':True},'PATCH')
 current();state={'unchanged':'success','review-required':'failure','unreachable':'error','invalid':'error'}[b['result']]
 fetch('/statuses/'+source_sha,status_token,{'state':state,'context':'htkk-source-candidate','description':'Quan sát nguồn và đề xuất private; candidate luôn chưa sẵn sàng kích hoạt','target_url':'https://github.com/'+u.BUILDER+'/actions/runs/'+run_id})
 return commit
