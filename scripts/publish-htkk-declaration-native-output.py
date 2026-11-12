"""Privately retain the byte-exact ORIGINAL re-export of a declaration-family native case.

Runs only after the supplier stopped and the credential gate opened. Original bytes are never
rewritten; privacy checks and the whole-tree comparison work on in-memory parses. The raw export
is retained even when the comparison reports differences (the case status stays failure), so a
mismatch can be explained from private bytes. Nothing here grants compatibility or filing scope.
"""
import base64,hashlib,importlib.util,json,os,pathlib,re,shutil,urllib.error

def module(name,file):
 spec=importlib.util.spec_from_file_location(name,pathlib.Path(__file__).with_name(file));value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
transport=module('declaration_output_transport','publish-htkk-web-inputs.py')
reader=transport.reader
declaration=reader.declaration
oracle=module('htkk_oracle_declaration_output','htkk_oracle.py')
REPO=reader.REPO
BUILDER=reader.BUILDER
DIRECTORY='htkk-declaration-native-output'
NAMES=('declaration-native.xml','provenance.json')
BRANCHES={id:c['outputBranch'] for id,c in reader.case_registry.CASES.items() if declaration.is_case(id)}
CODES=transport.CODES|frozenset(('PROVENANCE','COMPARE','FILES','NATIVE_IDENTITY','NATIVE_DATE'))
NATIVE_ERRORS={'SERVICE':'NATIVE_IDENTITY','DATE':'NATIVE_DATE','SIZE':'XML_SIZE','ENCODING':'XML_ENCODING','DECLARATION':'XML_DECLARATION','PARSE':'XML_PARSE'}
HARNESS={'harnessSchemaValid':bool,'harnessTreeMatched':bool,'harnessTreeMismatchMask':(0,63),'harnessTreeLeafCount':(0,4096),'harnessXmlMismatchMask':(0,16777215),'harnessCellMismatchMask':(0,16777215)}

class OutputError(ValueError):
 def __init__(self,code,context=None):
  if code not in CODES:raise ValueError('Invalid safe output error')
  self.code=code;self.context=context or {};super().__init__(code)
def fail(code,context=None):raise OutputError(code,context)
def safe_context(context):
 """Only the bounded native-rule diagnostic: a fixed rule name, a leaf ordinal, a section bit,
 a coarse value shape and, for a concatenation, its value-free piece layout. Never a value, path or text."""
 result={}
 if not isinstance(context,dict):return result
 if context.get('nativeRule')in declaration.CODES:result['nativeRule']=context['nativeRule']
 if type(context.get('leafOrdinal'))is int and 0<=context['leafOrdinal']<=4096:result['leafOrdinal']=context['leafOrdinal']
 if type(context.get('section'))is int and context['section']in (1,2,4,8,16,32):result['section']=context['section']
 if context.get('valueShape')in declaration.VALUE_SHAPES:result['valueShape']=context['valueShape']
 # Value-free piece layout of a rejected concatenation (part letters, allowed-text indices, digit-run lengths and
 # encoding ids of the case's own synthetic inputs); anything outside the fixed grammar is dropped.
 if isinstance(context.get('concatLayout'),str) and len(context['concatLayout'])<=256 and declaration.LAYOUT.match(context['concatLayout']) and result.get('valueShape','').startswith('allowed-text-concat'):result['concatLayout']=context['concatLayout']
 return result
def safe_failure(error):
 context={}
 if isinstance(error,OutputError):code=error.code if error.code in CODES else 'INTERNAL';context=safe_context(error.context) if code=='XML_PRIVACY' else {}
 elif isinstance(error,declaration.DeclarationWebCaseError):code='XML_PRIVACY'
 else:code=transport.safe_failure(error)['code']
 return {'format':'htkk-declaration-native-output-publication-status-v1','status':'rejected','code':code,**context}
def exact_sha(value,count=40):
 if not isinstance(value,str) or not re.fullmatch('[0-9a-f]{'+str(count)+'}',value):fail('PROVENANCE')
 return value

def validate_native(body,case_id,today=None,version=oracle.DEFAULT):
 if case_id not in BRANCHES:fail('PROVENANCE')
 try:return declaration.validate_native_output(body,case_id,today,oracle.service_version(version))
 except declaration.DeclarationWebCaseError as error:
  code=NATIVE_ERRORS.get(error.code,'XML_PRIVACY')
  fail(code,dict(error.context,nativeRule=error.code) if code=='XML_PRIVACY' else None)

def validate_provenance(body,native,run_id,builder_commit,source_commit,case_id,artifact_commit,run_attempt,version=oracle.DEFAULT):
 if case_id not in BRANCHES:fail('PROVENANCE')
 if not isinstance(run_id,str) or not re.fullmatch('[0-9]{1,20}',run_id) or not isinstance(run_attempt,str) or not re.fullmatch('[1-9][0-9]{0,5}',run_attempt):fail('PROVENANCE')
 exact_sha(builder_commit);exact_sha(source_commit);exact_sha(artifact_commit)
 if not isinstance(body,bytes) or not 0<len(body)<=reader.MAX_MANIFEST or not isinstance(native,bytes):fail('PROVENANCE')
 try:observed=reader.json_object(body,'MANIFEST')
 except reader.InputError:fail('PROVENANCE')
 expected={'format':'htkk-declaration-native-output-staging-v1','builderRepository':BUILDER,'builderCommit':builder_commit,'runId':run_id,'runAttempt':int(run_attempt),'sourceRepository':REPO,'sourceCommit':source_commit,'sourceVersion':oracle.baseline(version)['serviceVersion'],'runtimeHost':'clr2-x86-reference','caseId':case_id,'artifactCommit':artifact_commit,
  'inputsSynthetic':True,'originalProcessStopped':True,'originalSourcesUnmodified':True,
  # Native-case input mode: the original import of the web XML, the import completed by fixed original edits/ticks,
  # or the fixed plan typed into the original grid (no import).
  'inputMode':reader.case_registry.input_mode(case_id),'originalImportSucceeded':reader.case_registry.input_mode(case_id) in (reader.case_registry.IMPORT_MODE,reader.case_registry.IMPORT_TICK_MODE),'originalExportSucceeded':True,'originalExporterValidatedSchema':True,
  'webImportInputSha256':observed.get('webImportInputSha256'),'originalOutputSha256':hashlib.sha256(native).hexdigest(),'originalOutputBytes':len(native),'creationDateRule':'native-export-current-date','fullRoundTrip':False}
 exact_sha(expected['webImportInputSha256'],64)
 if set(observed)!=set(expected)|set(HARNESS) or any(type(observed[key]) is not type(value) or observed[key]!=value for key,value in expected.items()):fail('PROVENANCE')
 for key,rule in HARNESS.items():
  value=observed[key]
  if rule is bool:
   if type(value) is not bool:fail('PROVENANCE')
  elif type(value) is not int or not rule[0]<=value<=rule[1]:fail('PROVENANCE')
 return observed

def read_evidence(directory,run_id,builder_commit,source_commit,case_id,artifact_commit,run_attempt,today=None,version=oracle.DEFAULT):
 directory=pathlib.Path(directory)
 if transport.unsafe_path(directory) or not directory.is_dir() or set(p.name for p in directory.iterdir())!=set(NAMES):fail('FILES')
 native=transport.safe_read(directory/NAMES[0],reader.MAX_XML)
 provenance=transport.safe_read(directory/NAMES[1],reader.MAX_MANIFEST)
 metadata=validate_provenance(provenance,native,run_id,builder_commit,source_commit,case_id,artifact_commit,run_attempt,version)
 validate_native(native,case_id,today,version)
 return native,metadata

def publish(native,metadata,token,fetch=None,today=None,retain_immutable=False,version=oracle.DEFAULT):
 # Revalidate even when called independently of the fixed-path staging reader.
 metadata=validate_provenance(json.dumps(metadata).encode('utf-8'),native,metadata.get('runId'),metadata.get('builderCommit'),metadata.get('sourceCommit'),metadata.get('caseId'),metadata.get('artifactCommit'),str(metadata.get('runAttempt','')),version)
 checked=validate_native(native,metadata['caseId'],today,version)
 if not isinstance(token,str) or not token:fail('AUTH')
 fetch=fetch or transport.api
 if retain_immutable:transport.assert_current(fetch,token,metadata['sourceCommit'])
 # Only the fixed PRIVATE immutable input artifact of this case may justify retention.
 inputs=reader.download(token,fetch=lambda path,read_token:fetch(path,read_token),expected_source=metadata['sourceCommit'],expected_case=metadata['caseId'],artifact_commit=metadata['artifactCommit'])
 name=reader.xml_name(metadata['caseId']);input_manifest=reader.validate_manifest(inputs['manifest.json'])
 if hashlib.sha256(inputs[name]).hexdigest()!=metadata['webImportInputSha256']:fail('HASH')
 try:comparison=declaration.compare_tree(inputs[name],native,declaration.case(metadata['caseId'])['exportDates'])
 except declaration.DeclarationWebCaseError:fail('COMPARE')
 comparison['expectedTaxLeafCount']=declaration.tax_leaf_count(metadata['caseId'])
 comparison['allTaxValuesMatched']=comparison['allTaxValuesMatched'] and comparison['checkedTaxLeafCount']==comparison['expectedTaxLeafCount']
 # Independent recomputation vs the harness flag; a disagreement is recorded, never hidden.
 comparison['harnessAgreement']=comparison['allTaxValuesMatched']==metadata['harnessTreeMatched'] and comparison['mismatchSectionMask']==metadata['harnessTreeMismatchMask']
 manifest={'format':'htkk-declaration-native-output-reference-v1','scope':'single-fixed-synthetic-declaration-native-reexport','provenance':metadata,'privacyCheck':checked,'comparison':comparison,
  'input':{'artifactCommit':metadata['artifactCommit'],'sourceCommit':metadata['sourceCommit'],'caseId':metadata['caseId'],'sha256':metadata['webImportInputSha256'],'bytes':input_manifest['bytes'],'producerSha256':input_manifest['producerSha256']},
  'files':{NAMES[0]:{'sha256':metadata['originalOutputSha256'],'bytes':len(native)}},'fullRoundTrip':False,'qualificationGranted':False}
 files={NAMES[0]:native,'manifest.json':(json.dumps(manifest,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode('utf-8')}
 if len(files['manifest.json'])>reader.MAX_MANIFEST:fail('MANIFEST')
 entries=[]
 for file_name,body in files.items():
  blob=fetch('/git/blobs',token,{'content':base64.b64encode(body).decode('ascii'),'encoding':'base64'})
  expected=hashlib.sha1(b'blob '+str(len(body)).encode('ascii')+b'\0'+body).hexdigest()
  if not isinstance(blob,dict) or blob.get('sha')!=expected:fail('HASH')
  entries.append({'path':file_name,'mode':'100644','type':'blob','sha':expected})
 tree=fetch('/git/trees',token,{'tree':entries})
 if not isinstance(tree,dict):fail('API_SHAPE')
 tree_sha=exact_sha(tree.get('sha'))
 commit=fetch('/git/commits',token,{'message':'Private original native declaration reexport '+metadata['caseId']+' '+metadata['sourceCommit'],'tree':tree_sha,'parents':[]})
 if not isinstance(commit,dict):fail('API_SHAPE')
 artifact=exact_sha(commit.get('sha'))
 if retain_immutable:
  transport.assert_current(fetch,token,metadata['sourceCommit']);transport.immutable_refs.retain(fetch,token,'output',metadata['sourceCommit'],metadata['caseId']+oracle.suffix(version),artifact)
 # A non-default oracle keeps its own branch: it never replaces the default cohort's retained output.
 branch=oracle.output_branch(BRANCHES[metadata['caseId']],version);missing=False
 # Only an explicit GET 404 establishes absence; failed mutations are never retried as creation.
 try:existing=fetch('/git/ref/heads/'+branch,token)
 except urllib.error.HTTPError as error:
  if error.code!=404:raise
  missing=True
 if missing:updated=fetch('/git/refs',token,{'ref':'refs/heads/'+branch,'sha':artifact})
 else:
  if not isinstance(existing,dict) or existing.get('ref')!='refs/heads/'+branch or not isinstance(existing.get('object'),dict) or existing['object'].get('type')!='commit':fail('API_SHAPE')
  exact_sha(existing['object'].get('sha'))
  updated=fetch('/git/refs/heads/'+branch,token,{'sha':artifact,'force':True},'PATCH')
 if not isinstance(updated,dict) or updated.get('ref')!='refs/heads/'+branch or not isinstance(updated.get('object'),dict) or updated['object'].get('type')!='commit' or updated['object'].get('sha')!=artifact:fail('API_SHAPE')
 return {'format':'htkk-declaration-native-output-publication-status-v1','status':'published','caseId':metadata['caseId'],'sourceCommit':metadata['sourceCommit'],'artifactCommit':artifact,'nativeOutputSha256':metadata['originalOutputSha256'],'bytes':len(native),'allTaxValuesMatched':comparison['allTaxValuesMatched'],'mismatchSectionMask':comparison['mismatchSectionMask'],'mismatchLeafOrdinals':[n for n in comparison['mismatchLeafOrdinals'] if type(n) is int and 0<n<=4096][:declaration.MISMATCH_ORDINALS]}

def main():
 directory=pathlib.Path(os.environ.get('RUNNER_TEMP',''))/DIRECTORY
 try:
  if os.environ.get('GITHUB_REPOSITORY')!=BUILDER:fail('BUILDER')
  token=os.environ.get('SOURCE_PUBLISH_TOKEN') or os.environ.get('SOURCE_READ_TOKEN')
  if not token:fail('AUTH')
  if not directory.exists():print(json.dumps({'format':'htkk-declaration-native-output-publication-status-v1','status':'not-staged'},separators=(',',':')));return
  version=oracle.version(os.environ)
  native,metadata=read_evidence(directory,os.environ.get('GITHUB_RUN_ID'),os.environ.get('GITHUB_SHA'),os.environ.get('EXPECTED_WEB_SOURCE_SHA'),os.environ.get('EXPECTED_WEB_CASE_ID'),os.environ.get('WEB_ARTIFACT_COMMIT'),os.environ.get('GITHUB_RUN_ATTEMPT',''),version=version)
  print(json.dumps(publish(native,metadata,token,retain_immutable=True,version=version),separators=(',',':')))
 except Exception as error:
  print(json.dumps(safe_failure(error),separators=(',',':')))
  raise SystemExit('Native declaration output retention failed; no XML, paths, credentials or raw remote error published.')
 finally:
  # Never follow an unsafe directory or erase another task's runner files.
  if os.environ.get('RUNNER_TEMP') and directory.name==DIRECTORY and not transport.unsafe_path(directory):shutil.rmtree(directory,ignore_errors=True)

if __name__=='__main__':main()
