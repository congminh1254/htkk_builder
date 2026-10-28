"""Trusted source-update orchestration. Metadata and binaries remain inert/not-ready.

Fetch, Windows verification and authenticated private publication run in separate
processes. Prepared cloud observations are explicit immutable inputs, not a claim
that the GitHub runner reached the landing page itself.
"""
import argparse,base64,datetime,hashlib,importlib.util,json,os,pathlib,re,shutil,urllib.error
ROOT=pathlib.Path(__file__).resolve().parent
REPO='congminh1254/htkk_web';BUILDER='congminh1254/htkk_builder'
MAX_META=4*1024*1024;CHUNK=4*1024*1024
META=('official-sources.json','candidate.json','trust.json','proposal.json','payload-sha256.json')
ARCHIVES=('official.rar','mirror.zip')
def module(name,file):
 s=importlib.util.spec_from_file_location(name,ROOT/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
watch=module('source_update_watch','source-watch.py');candidate=module('source_update_candidate','source-candidate.py')
def require(test,code='SOURCE_UPDATE_POLICY'):
 if not test:raise ValueError(code)
def digest(b):return hashlib.sha256(b).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
def gitsha(s):require(isinstance(s,str)and re.fullmatch('[a-f0-9]{40}',s));return s
def exact(o,keys):require(type(o)is dict and set(o)==set(keys));return o
def plain(path,exists=True):
 p=pathlib.Path(path).absolute()
 for q in (p,*p.parents):
  require(not q.is_symlink() and not getattr(q,'is_junction',lambda:False)())
  if q.exists():require(not(getattr(q.stat(follow_symlinks=False),'st_file_attributes',0)&0x400))
 if exists:require(p.is_file())
 return p
def load(path,maximum=MAX_META):
 p=plain(path);require(p.stat().st_size<=maximum);return json.loads(p.read_text(encoding='utf-8-sig'))
def write(path,obj):
 p=plain(path,False);b=(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode();require(len(b)<=MAX_META)
 with p.open('xb')as f:f.write(b)
def file_info(p):
 p=plain(p);h=hashlib.sha256()
 with p.open('rb')as f:
  while b:=f.read(CHUNK):h.update(b)
 return {'path':p.name,'sha256':h.hexdigest(),'bytes':p.stat().st_size}
def getpaths():
 base=pathlib.Path(os.environ['RUNNER_TEMP']).absolute()
 return base/'htkk-source-candidate',base/'htkk-official-source-watch.json',base/'htkk-source-update-bundle'
def source_read(token,requested=''):
 info=watch.api('',token);require(info.get('private')is True and info.get('full_name')==REPO)
 sha=gitsha(watch.api('/branches/main',token)['commit']['sha']);require(not requested or gitsha(requested)==sha,'STALE_SOURCE')
 return sha
def output(name,value):
 require(re.fullmatch('[a-z_]+',name)and re.fullmatch('[a-z0-9]+',value))
 with open(os.environ['GITHUB_OUTPUT'],'a',encoding='utf8')as f:f.write(name+'='+value+'\n')
def resolve():
 work,report,bundle=getpaths();token=os.environ['SOURCE_READ_TOKEN'];source=source_read(token,os.environ.get('REQUESTED_SOURCE_SHA',''))
 prepared=os.environ.get('PREPARED_OBSERVATION_COMMIT','')
 if prepared:
  gitsha(prepared);entry=watch.api('/contents/prepared-source.json?ref='+prepared,token);raw=base64.b64decode(entry['content'],validate=True);require(len(raw)<=64000)
  p=json.loads(raw);exact(p,('format','sourceSha','origin','observerSha256','report'));require(p['format']=='htkk-prepared-source-observation-v1'and p['sourceSha']==source and p['origin']=='authorized-cloud-source-observation'and p['observerSha256']==digest((ROOT/'source-watch.py').read_text().replace('\r\n','\n').encode()))
  watch.validate_report(p['report']);age=datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(p['report']['checkedAt']);require(0<=age.total_seconds()<=86400,'STALE_OBSERVATION');write(report,p['report'])
 output('source_sha',source);print('Fixed private source identity resolved; no source checkout.')
def prepare_observation(filename,token):
 # Caller creates this report in a separate credential-free observer process.
 report=watch.validate_report(load(filename,64000));require(report['result']in('unchanged','review-required'))
 source=source_read(token);packet={'format':'htkk-prepared-source-observation-v1','sourceSha':source,'origin':'authorized-cloud-source-observation','observerSha256':digest((ROOT/'source-watch.py').read_text().replace('\r\n','\n').encode()),'report':report}
 body=(json.dumps(packet,ensure_ascii=False,separators=(',',':'))+'\n').encode();blob=gitsha(watch.api('/git/blobs',token,{'encoding':'base64','content':base64.b64encode(body).decode()})['sha']);tree=gitsha(watch.api('/git/trees',token,{'tree':[{'path':'prepared-source.json','mode':'100644','type':'blob','sha':blob}]})['sha']);commit=gitsha(watch.api('/git/commits',token,{'message':'Private prepared public-source observation; no activation','parents':[],'tree':tree})['sha']);require(source_read(token)==source,'STALE_SOURCE');return commit
STAGE_KEYS=('format','checkedAt','scope','observationSha256','preparedObservationCommit','verifyCurrent','observedVersion','reference','result','failureCode','transportFailures','official','mirror','baselineArchiveMatched','trustRequested','ready','automaticActivation')
def validate_stage(s):
 exact(s,STAGE_KEYS);require(s['format']=='htkk-source-update-stage-v1'and s['scope']=='inert-candidate-no-execution')
 require(s['result']in('metadata-only','staged','blocked','unreachable')and s['ready']is False and s['automaticActivation']is False)
 for k in('verifyCurrent','baselineArchiveMatched','trustRequested'):require(type(s[k])is bool)
 require(s['failureCode']is None or s['failureCode']in candidate.ERRORS|{'OBSERVATION_UNAVAILABLE','REFERENCE_UNSUPPORTED','BASELINE_BYTES_CHANGED','UNREVIEWED_VERSION'})
 require(re.fullmatch('[a-f0-9]{64}',s['observationSha256'])is not None)
 if s['preparedObservationCommit']:gitsha(s['preparedObservationCommit'])
 require(type(s['transportFailures'])is list and len(s['transportFailures'])<=2)
 for e in s['transportFailures']:
  exact(e,('code','status'));require(e['code']in candidate.ERRORS and(e['status']is None or type(e['status'])is int and 100<=e['status']<=599))
 for key in('official','mirror'):
  d=s[key]
  if d is None:continue
  keys={'format','checkedAt','transport','requestedUrlSha256','requestedHost','attempts','expectedHashMatched','signatureVerified','payloadVerified','ready','automaticActivation','bytes','sha256','kind','status','finalHost','finalUrlSha256','redirects','lastModified','rangeRequests'}
  if key=='mirror':keys.add('scope');require(d.get('scope')=='baseline-mirror-not-trusted-until-cab-and-signature-chain-match')
  exact(d,keys)
  require(d['transport']in('direct','relay')and type(d['expectedHashMatched'])is bool and type(d['rangeRequests'])is int and 0<=d['rangeRequests']<=64)
  for field in('requestedUrlSha256','finalUrlSha256'):require(re.fullmatch('[a-f0-9]{64}',d[field])is not None)
  require(type(d['attempts'])is list and 1<=len(d['attempts'])<=2 and type(d['redirects'])is list and len(d['redirects'])<=5)
  for event in d['attempts']:
   exact(event,('attempt','result','errorCode','httpStatus'));require(type(event['attempt'])is int and event['attempt']in(1,2)and event['result']in('downloaded','failed')and event['errorCode']in candidate.ERRORS|{None})
  for hop in d['redirects']:
   exact(hop,('status','fromHost','toHost','urlSha256'));require(type(hop['status'])is int and hop['status']in(301,302,303,307,308)and re.fullmatch('[a-f0-9]{64}',hop['urlSha256'])is not None)
  require(type(d)is dict and d.get('format')=='htkk-source-candidate-download-v1'and d.get('ready')is False and d.get('automaticActivation')is False and d.get('signatureVerified')is False and d.get('payloadVerified')is False)
  require(type(d.get('bytes'))is int and 1<=d['bytes']<=candidate.MAX_BYTES and re.fullmatch('[a-f0-9]{64}',d.get('sha256',''))is not None)
  require(d.get('kind')in('rar','zip','7z','cab','compound','pe'))
 require(not s['trustRequested']or(s['official']is not None and s['baselineArchiveMatched']))
 return s
def stage():
 work,report,bundle=getpaths();require(not work.exists());work.mkdir();r=watch.validate_report(load(report,64000))
 refs=r['releases'][0]['downloadReferences']if r['releases']else[]
 ref=refs[0]['url']if len(refs)==1 and refs[0]['recognition']=='recognized-fshare'else None
 s=dict(zip(STAGE_KEYS,('htkk-source-update-stage-v1',now(),'inert-candidate-no-execution',digest(report.read_bytes()),os.environ.get('PREPARED_OBSERVATION_COMMIT',''),os.environ.get('VERIFY_CURRENT')=='true',r['observation']['firstPublishedVersion'],ref,'metadata-only',None,[],None,None,False,False,False,False)))
 if r['result']in('unreachable','invalid'):s.update(result='unreachable',failureCode='OBSERVATION_UNAVAILABLE')
 elif r['result']=='review-required'or s['verifyCurrent']:
  if ref is None:s.update(result='blocked',failureCode='REFERENCE_UNSUPPORTED')
  else:
   try:
    try:s['official']=candidate.fetch_resource(ref,work/'official.rar',max_attempts=1)
    except candidate.CandidateError as e:
     s['transportFailures'].append({'code':e.code,'status':e.status})
     if not e.retryable or not os.environ.get('AGENT_AUTH_TOKEN'):raise
     s['official']=candidate.fetch_resource(ref,work/'official.rar',relay_token=os.environ['AGENT_AUTH_TOKEN'],transport='relay',max_attempts=1)
    s['baselineArchiveMatched']=s['observedVersion']==watch.PINNED_VERSION and s['official']['sha256']==candidate.BASELINE_OFFICIAL_SHA256
    if s['baselineArchiveMatched']:
     s.update(result='staged',trustRequested=True)
    else:s.update(result='blocked',failureCode='UNREVIEWED_VERSION'if s['observedVersion']!=watch.PINNED_VERSION else'BASELINE_BYTES_CHANGED')
   except candidate.CandidateError as e:s.update(result='blocked',failureCode=e.code)
 write(work/'candidate.json',validate_stage(s));output('trust_requested','true'if s['trustRequested']else'false');print(json.dumps({'result':s['result'],'failureCode':s['failureCode'],'trustRequested':s['trustRequested'],'ready':False}))
TRUST_FLAGS=('archivePinsMatched','officialDistributionFilesMatched','extractorTrusted','signToolTrusted','msiAuthenticodeValid','setupAuthenticodeValid','msiPublisherMatched','setupPublisherMatched','msiTimestampValid','setupTimestampValid','signerRevocationVerified','timestampRevocationVerified','msiCabMediaMatched','payloadSizesMatched','payloadMsiHashesMatched','payloadVersionMatched','sourceFilesUnmodified')
def validate_trust(t,directory):
 if t.get('format')=='htkk-source-candidate-trust-not-run-v1':
  exact(t,('format','reason','noProcessStarted','workerStopped','jobCleanupVerified','workerTimedOut','ready','automaticActivation'))
  require(t['reason']in('metadata-only','blocked','unreachable')and all(t[k]is True for k in('noProcessStarted','workerStopped','jobCleanupVerified'))and all(t[k]is False for k in('workerTimedOut','ready','automaticActivation')));return True
 require(t.get('format')=='htkk-source-candidate-trust-v1'and t.get('status')in('baseline-verified','blocked'))
 for k in('ready','automaticActivation','adapterActivated','vendorCodeExecuted','installerExecuted','msiCustomActionsExecuted'):require(t.get(k)is False)
 require(t.get('workerScriptSha256')==digest((ROOT/'Test-HtkkSourceCandidateTrust.ps1').read_bytes())and t.get('cabinetHelperSha256')==digest((ROOT/'HtkkSourceCabinet.cs').read_bytes()))
 require(t.get('revocationPolicy')=='online-exclude-root-no-verification-exceptions'and t.get('revocationUrlTimeoutSeconds')==10)
 require(type(t.get('checks'))is dict and set(t['checks'])==set(TRUST_FLAGS)and all(type(v)is bool for v in t['checks'].values()))
 for k in('workerStopped','jobCleanupVerified','workerTimedOut'):require(type(t.get(k))is bool)
 require(type(t.get('mirrorUsed'))is bool and type(t.get('mirrorCompared'))is bool)
 if t['status']=='baseline-verified':
  require(t['mirrorUsed']==t['mirrorCompared'])
  require(all(t['checks'].values())and t.get('failureCode')is None)
  p=t['payload'];require(p=={'files':4526,'sizeMatches':4526,'msiHashMatches':4493,'versionedWithoutMsiHash':33,'sha256Entries':4526,'fullyCoveredBySignedMsiHashes':False})
  f=t['payloadManifest'];require(f['path']=='payload-sha256.json'and f['entries']==4526)
  info=file_info(pathlib.Path(directory)/'payload-sha256.json');require(info['sha256']==f['sha256']and info['bytes']==f['bytes'])
 return t['workerStopped']and t['jobCleanupVerified']and not t['workerTimedOut']
def validate_bundle_metadata(directory,bundle):
 directory=pathlib.Path(directory);r=watch.validate_report(load(directory/'official-sources.json',64000));s=validate_stage(load(directory/'candidate.json'));t=load(directory/'trust.json')
 require(digest((directory/'official-sources.json').read_bytes())==s['observationSha256']);require(validate_trust(t,directory),'WORKER_UNSAFE')
 for name,key in(('official.rar','official'),('mirror.zip','mirror')):
  if s[key]is not None:
   f=file_info(directory/name);require(f['sha256']==s[key]['sha256']and f['bytes']==s[key]['bytes'])
 p=load(directory/'proposal.json');exact(p,('format','sourceSha','builderSha','runId','runAttempt','observedVersion','pinnedVersion','versionChanged','referenceChanged','archiveChanged','trustStatus','scope','result','ready','automaticActivation','adapterActivated'))
 require(p['format']=='htkk-source-update-proposal-v1'and p['scope']=='proposal-only-not-qualified-adapter'and all(p[k]is False for k in('ready','automaticActivation','adapterActivated')))
 for k in('sourceSha','builderSha','runId','runAttempt','result'):require(p[k]==bundle[k])
 require(p['observedVersion']==s['observedVersion']and p['pinnedVersion']==watch.PINNED_VERSION)
 require(p['versionChanged']is r['observation']['releaseChangedFromPinned']and p['referenceChanged']is r['observation']['downloadReferenceChangedFromPinned'])
 require(type(p['archiveChanged'])is bool and p['archiveChanged']==(s['official']is not None and s['official']['sha256']!=candidate.BASELINE_OFFICIAL_SHA256))
 expected=r['result']
 if s['result']=='blocked'or(s['trustRequested']and t.get('status')!='baseline-verified'):expected='review-required'
 require(p['result']==expected)
 require(p['trustStatus']==t.get('status','not-run'))
 return p

def seal():
 work,report,bundle=getpaths();s=validate_stage(load(work/'candidate.json'));trust=work/'trust.json'
 if not s['trustRequested']:
  write(trust,{'format':'htkk-source-candidate-trust-not-run-v1','reason':s['result'],'noProcessStarted':True,'workerStopped':True,'jobCleanupVerified':True,'workerTimedOut':False,'ready':False,'automaticActivation':False})
 t=load(trust);safe=validate_trust(t,work);output('credentials_safe','true'if safe else'false');require(safe,'WORKER_UNSAFE')
 r=watch.validate_report(load(report,64000));result=r['result']
 if s['result']=='blocked'or(s['trustRequested']and t.get('status')!='baseline-verified'):result='review-required'
 source=gitsha(os.environ['SOURCE_SHA']);builder=gitsha(os.environ['GITHUB_SHA']);run=os.environ['GITHUB_RUN_ID'];attempt=int(os.environ['GITHUB_RUN_ATTEMPT']);require(re.fullmatch('[1-9][0-9]{0,19}',run)and 1<=attempt<=100)
 p={'format':'htkk-source-update-proposal-v1','sourceSha':source,'builderSha':builder,'runId':run,'runAttempt':attempt,'observedVersion':s['observedVersion'],'pinnedVersion':watch.PINNED_VERSION,'versionChanged':r['observation']['releaseChangedFromPinned'],'referenceChanged':r['observation']['downloadReferenceChangedFromPinned'],'archiveChanged':s['official']is not None and s['official']['sha256']!=candidate.BASELINE_OFFICIAL_SHA256,'trustStatus':t.get('status','not-run'),'scope':'proposal-only-not-qualified-adapter','result':result,'ready':False,'automaticActivation':False,'adapterActivated':False}
 require(not bundle.exists());bundle.mkdir();shutil.copyfile(report,bundle/'official-sources.json')
 for name in META[1:]+ARCHIVES:
  path=work/name
  if path.exists():shutil.copyfile(plain(path),bundle/name)
 write(bundle/'proposal.json',p)
 b={'format':'htkk-source-update-bundle-v1','sourceSha':source,'builderSha':builder,'runId':run,'runAttempt':attempt,'credentialsSafe':True,'ready':False,'automaticActivation':False,'result':result,'files':[file_info(f)for f in sorted(bundle.iterdir())]}
 validate_bundle_metadata(bundle,b);write(bundle/'bundle.json',b);print(json.dumps({'result':result,'trustStatus':p['trustStatus'],'ready':False,'credentialsSafe':True}))
def main():
 a=argparse.ArgumentParser();a.add_argument('mode',choices=('resolve','stage','seal','publish','outcome','prepare'));a.add_argument('--report');args=a.parse_args()
 if args.mode=='prepare':print(prepare_observation(args.report,os.environ['SOURCE_READ_TOKEN']));return 0
 require(os.environ.get('GITHUB_REPOSITORY')==BUILDER and os.environ.get('GITHUB_REF')=='refs/heads/main')
 if args.mode=='resolve':resolve()
 elif args.mode=='stage':stage()
 elif args.mode=='seal':seal()
 elif args.mode=='publish':
  pub=module('source_update_publish','source-update-publish.py');_,_,bundle=getpaths();b=load(bundle/'bundle.json');commit=pub.publish_bundle(bundle,b['sourceSha'],b['builderSha'],b['runId'],b['runAttempt'],os.environ['SOURCE_PUBLISH_TOKEN'],os.environ['SOURCE_STATUS_TOKEN']);report=watch.validate_report(load(bundle/'official-sources.json',64000));require(source_read(os.environ['SOURCE_PUBLISH_TOKEN'])==b['sourceSha'],'STALE_SOURCE');state={'unchanged':'success','review-required':'failure','unreachable':'error','invalid':'error'}[report['result']];watch.api('/statuses/'+b['sourceSha'],os.environ['SOURCE_STATUS_TOKEN'],{'state':state,'context':'htkk-source-watch','description':'Metadata nguồn được lưu trong proposal private; không tự kích hoạt','target_url':'https://github.com/'+BUILDER+'/actions/runs/'+b['runId']});print('Private not-ready source proposal published: '+commit)
 else:
  _,_,bundle=getpaths();b=load(bundle/'bundle.json');print(json.dumps({'result':b['result'],'ready':False,'automaticActivation':False}));return 0 if b['result']=='unchanged'else 1
 return 0
if __name__=='__main__':
 try:raise SystemExit(main())
 except Exception:raise SystemExit('Source update failed; no raw data, headers or credentials published.')
