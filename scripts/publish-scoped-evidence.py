"""Publish candidate bundles only to the fixed PRIVATE source repository."""
import base64,hashlib,importlib.util,json,os,pathlib,re,urllib.error
_spec=importlib.util.spec_from_file_location('collector',pathlib.Path(__file__).with_name('collect-scoped-evidence.py'))
c=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(c)
t=c.retention.transport
BRANCH='gtgt-scoped-evidence-candidates'
FILES=('retained.json','input-manifest.json','initial.xml','native.xml','web.xml','producer.mjs','gui-report.json','run.json','roundtrip-v2.json','execution-v2.json')
def payload(directory,source,builder):
 source=c.sha(source);builder=c.sha(builder);directory=pathlib.Path(directory)
 paths=['bundle.json','assessment.json','evidence-v2.json']+[case+'/'+name for case in c.cases.CASES for name in FILES]
 c.check(not t.unsafe_path(directory) and directory.is_dir())
 actual=sorted(p.relative_to(directory).as_posix() for p in directory.rglob('*') if p.is_file() or p.is_symlink())
 c.check(actual==sorted(paths))
 files={name:t.safe_read(directory/name,2_000_000) for name in paths}
 bundle=json.loads(files['bundle.json']);report=json.loads(files['assessment.json']);manifest=json.loads(files['evidence-v2.json'])
 c.check(bundle.get('format')=='htkk-native-evidence-bundle-v1' and bundle.get('sourceCommit')==source and bundle.get('builderCommit')==builder and [x.get('caseId') for x in bundle.get('cases',[])]==list(c.cases.CASES))
 c.check(report.get('format')=='htkk-evidence-assessment-v1' and report.get('status')=='blocked' and report.get('caseCount')==13 and report.get('sourceCommit')==source and report.get('builderCommit')==builder and report.get('fullCompatibility') is False and report.get('nativeQualified') is False and report.get('filingEnabled') is False)
 c.check(manifest.get('format')=='htkk-windows-evidence-v2' and manifest.get('reviewer')=='' and len(manifest.get('cases',[]))==13)
 for case in bundle['cases']:
  for key in ('htkkOutput','webOutput','reexport','producer','retained','inputManifest'):
   entry=case[key];c.check(entry.get('path') in files and hashlib.sha256(files[entry['path']]).hexdigest()==entry.get('sha256'))
 return files
def publish(files,source,token,fetch=t.api):
 info=fetch('',token);c.check(info.get('private') is True and info.get('full_name')==c.SOURCE)
 entries=[]
 for name,body in sorted(files.items()):
  blob=fetch('/git/blobs',token,{'content':base64.b64encode(body).decode(),'encoding':'base64'})
  expected=hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest();c.check(blob.get('sha')==expected)
  entries.append({'path':name,'mode':'100644','type':'blob','sha':expected})
 tree=fetch('/git/trees',token,{'tree':entries});tree_sha=c.sha(tree.get('sha'))
 commit=fetch('/git/commits',token,{'message':'Private scoped evidence candidate '+c.sha(source),'tree':tree_sha,'parents':[]});commit_sha=c.sha(commit.get('sha'))
 try:ref=fetch('/git/ref/heads/'+BRANCH,token)
 except urllib.error.HTTPError as error:
  if error.code!=404:raise
  ref=None
 if ref is None:updated=fetch('/git/refs',token,{'ref':'refs/heads/'+BRANCH,'sha':commit_sha})
 else:
  c.check(ref.get('ref')=='refs/heads/'+BRANCH and ref.get('object',{}).get('type')=='commit');c.sha(ref['object']['sha'])
  updated=fetch('/git/refs/heads/'+BRANCH,token,{'sha':commit_sha,'force':True},'PATCH')
 c.check(updated.get('ref')=='refs/heads/'+BRANCH and updated.get('object',{}).get('sha')==commit_sha)
 return commit_sha
if __name__=='__main__':
 try:
  c.check(os.environ.get('GITHUB_REPOSITORY')==c.BUILDER and os.environ.get('GITHUB_REF')=='refs/heads/main')
  files=payload(pathlib.Path(os.environ['RUNNER_TEMP'])/'htkk-scoped-evidence',os.environ['EVIDENCE_SOURCE_SHA'],os.environ['NATIVE_BUILDER_SHA'])
  commit=publish(files,os.environ['EVIDENCE_SOURCE_SHA'],os.environ.get('SOURCE_PUBLISH_TOKEN') or os.environ['SOURCE_READ_TOKEN'])
  print(json.dumps({'format':'htkk-scoped-evidence-publication-v1','status':'candidate-retained','sourceCommit':os.environ['EVIDENCE_SOURCE_SHA'],'artifactCommit':commit,'qualificationGranted':False}))
 except Exception:raise SystemExit('Private evidence retention failed; raw data and diagnostics suppressed.')
