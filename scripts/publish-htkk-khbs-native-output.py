"""Privately retain the byte-exact ORIGINAL export of a KHBS (kê khai bổ sung lần 1) native case.

Runs only after the supplier stopped and the credential gate opened. Original bytes are never
rewritten. The export is retained whenever HTKK wrote and acknowledged it, including a reported
whole-tree mismatch (the case status stays failure), so a difference can be explained from the
private bytes. Before anything is uploaded the publisher downloads the case's own immutable private
web input, validates the native file against it (synthetic identity, HTKK service identity, a fresh
creation date, and every other text either a value of that synthetic input or a bounded numeric/date
shape), and recomputes the whole-tree comparison independently of the harness. Nothing here grants
compatibility, filing scope or a release gate.
"""
import base64,datetime,hashlib,importlib.util,io,json,os,pathlib,re,shutil,urllib.error
import xml.etree.ElementTree as ET

def module(name,file):
 spec=importlib.util.spec_from_file_location(name,pathlib.Path(__file__).with_name(file));value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
transport=module('khbs_output_transport','publish-htkk-web-inputs.py')
reader=transport.reader
khbs=reader.khbs
oracle=module('htkk_oracle_khbs_output','htkk_oracle.py')
REPO=reader.REPO
BUILDER=reader.BUILDER
DIRECTORY='htkk-khbs-native-output'
NAMES=('khbs-native.xml','provenance.json')
BRANCHES={id:c['outputBranch'] for id,c in reader.case_registry.CASES.items() if khbs.is_case(id)}
CODES=transport.CODES|frozenset(('PROVENANCE','COMPARE','FILES','NATIVE_IDENTITY','NATIVE_DATE'))
NS=khbs.NS;XSI=khbs.XSI
SERVICE={'maDVu':'HTKK','tenDVu':'HỖ TRỢ KÊ KHAI THUẾ'}
SERVICE_PATH='HSoThueDTu/HSoKhaiThue/TTinChung/TTinDVu/'
DATE_PATH='HSoThueDTu/HSoKhaiThue/TTinChung/TTinTKhaiThue/TKhaiThue/ngayLapTKhai'
HEAD='HSoThueDTu/HSoKhaiThue/TTinChung/TTinTKhaiThue/'
# Leaves whose native value must equal the synthetic input exactly (identity and the amendment header).
IDENTITY=(HEAD+'NNT/mst',HEAD+'NNT/tenNNT',HEAD+'TKhaiThue/loaiTKhai',HEAD+'TKhaiThue/soLan',HEAD+'TKhaiThue/nguoiKy')
# Value shapes HTKK may compute differently from the web input; any other text must be a value of the input itself.
SHAPES=tuple(re.compile(p) for p in (r'-?[0-9]{1,18}',r'-?[0-9]{1,3}(?:\.[0-9]{3})+',r'-?[0-9]{1,15}[.,][0-9]{1,6}',r'[0-9]{4}-[0-9]{2}-[0-9]{2}',r'[0-9]{2}/[0-9]{2}/[0-9]{4}',r'[0-9]{1,2}/[0-9]{4}',r'\[[0-9]{2}[a-z]?\]'))
# Whole-tree region bits, the same as HtkkWebTaxComparison.CompareKhbs.
REGIONS=((HEAD[:-len('TTinTKhaiThue/')],4),('HSoThueDTu/HSoKhaiThue/CTieuTKhaiChinh/',8),('HSoThueDTu/HSoKhaiThue/PLuc/PL01_KHBS/',16),('HSoThueDTu/HSoKhaiThue/PLuc/PL01_1_KHBS/',32))
MISMATCH_ORDINALS=16
HARNESS={'harnessTreeMatched':bool,'harnessMismatchMask':(0,255),'harnessLeafCount':(0,4096),'harnessFirstDifferenceOrdinal':(0,4096),'harnessOpenMainState':(0,2),'harnessIdentityMatched':bool,'harnessCreationDateValid':bool}

class OutputError(ValueError):
 def __init__(self,code,context=None):
  if code not in CODES:raise ValueError('Invalid safe output error')
  self.code=code;self.context=context or {};super().__init__(code)
def fail(code,context=None):raise OutputError(code,context)
def safe_context(context):
 """Only a fixed rule name and a leaf ordinal; never a value, path or text."""
 result={}
 if not isinstance(context,dict):return result
 if context.get('nativeRule') in ('STRUCTURE','ATTRIBUTES','IDENTITY','PRIVACY'):result['nativeRule']=context['nativeRule']
 if type(context.get('leafOrdinal')) is int and 0<=context['leafOrdinal']<=4096:result['leafOrdinal']=context['leafOrdinal']
 return result
def safe_failure(error):
 context={}
 if isinstance(error,OutputError):code=error.code if error.code in CODES else 'INTERNAL';context=safe_context(error.context) if code=='XML_PRIVACY' else {}
 else:code=transport.safe_failure(error)['code']
 return {'format':'htkk-khbs-native-output-publication-status-v1','status':'rejected','code':code,**context}
def exact_sha(value,count=40):
 if not isinstance(value,str) or not re.fullmatch('[0-9a-f]{'+str(count)+'}',value):fail('PROVENANCE')
 return value

def document(body):
 if not isinstance(body,bytes) or not 0<len(body)<=reader.MAX_XML:fail('XML_SIZE')
 try:text=body.decode('utf-8-sig')
 except UnicodeError:fail('XML_ENCODING')
 if re.search(r'<!|<\?(?!xml\s)',text,re.I) or text.count('<?')>1:fail('XML_DECLARATION')
 try:
  for _,(prefix,uri) in ET.iterparse(io.BytesIO(body),events=('start-ns',)):
   if (prefix,uri) not in (('',NS),('xsi',XSI)):fail('XML_PRIVACY',{'nativeRule':'STRUCTURE'})
  root=ET.fromstring(body)
 except ET.ParseError:fail('XML_PARSE')
 if root.tag!='{'+NS+'}HSoThueDTu':fail('XML_PRIVACY',{'nativeRule':'STRUCTURE'})
 return root

def leaves(root):
 """Every element in document order as (path, attributes, text or None for a container); bounded."""
 out=[]
 def walk(node,path):
  if not isinstance(node.tag,str) or not node.tag.startswith('{'+NS+'}'):fail('XML_PRIVACY',{'nativeRule':'STRUCTURE','leafOrdinal':len(out)})
  here=path+'/'+node.tag[len(NS)+2:] if path else node.tag[len(NS)+2:];children=list(node)
  if len(out)>=4096 or (node.tail or '').strip() or (children and (node.text or '').strip()):fail('XML_PRIVACY',{'nativeRule':'STRUCTURE','leafOrdinal':len(out)})
  attributes={}
  for key,value in node.attrib.items():
   if key=='{'+XSI+'}nil' and value=='true':attributes['xsi:nil']=value
   elif key=='id' and re.fullmatch('ID_[0-9]{1,4}',value):attributes['id']=value
   else:fail('XML_PRIVACY',{'nativeRule':'ATTRIBUTES','leafOrdinal':len(out)})
  out.append((here,attributes,None if children else (node.text or '')))
  for child in children:walk(child,here)
 walk(root,'');return out

def validate_native(body,web,case_id,today=None,version=oracle.DEFAULT):
 if case_id not in BRANCHES:fail('PROVENANCE')
 native=leaves(document(body));synthetic=leaves(document(web))
 known={text for _,_,text in synthetic if text}
 expected={path:text for path,_,text in synthetic if path in IDENTITY}
 service={**SERVICE,'pbanDVu':oracle.service_version(version)};seen=set();created=None;ordinal=0
 for path,_,text in native:
  if text is None:continue
  ordinal+=1
  if path.startswith(SERVICE_PATH):
   name=path[len(SERVICE_PATH):]
   if name in seen or not (text==service.get(name) or name=='ttinNhaCCapDVu' and re.fullmatch('[0-9A-F]{32}',text)):fail('NATIVE_IDENTITY')
   seen.add(name);continue
  if path==DATE_PATH:
   if created is not None or not re.fullmatch('[0-9]{4}-[0-9]{2}-[0-9]{2}',text):fail('NATIVE_DATE')
   try:created=datetime.date.fromisoformat(text)
   except ValueError:fail('NATIVE_DATE')
   continue
  if path in IDENTITY:
   if text!=expected.get(path):fail('XML_PRIVACY',{'nativeRule':'IDENTITY','leafOrdinal':ordinal})
   continue
  if text and text not in known and not any(shape.fullmatch(text) for shape in SHAPES):fail('XML_PRIVACY',{'nativeRule':'PRIVACY','leafOrdinal':ordinal})
 if seen!=set(service)|{'ttinNhaCCapDVu'}:fail('NATIVE_IDENTITY')
 today=today or datetime.datetime.now(datetime.timezone.utc).date()
 if created is None or abs((today-created).days)>1:fail('NATIVE_DATE')
 if set(expected)!=set(IDENTITY):fail('XML_PRIVACY',{'nativeRule':'IDENTITY'})
 return {'privacyValuesVerified':True,'fixedSyntheticCase':case_id,'leafCount':ordinal,'nativeServiceIdentityVerified':True,'creationDateRule':'native-export-current-date','textRule':'synthetic-input-value-or-bounded-shape'}

def region(path):
 for prefix,bit in REGIONS:
  if path.startswith(prefix):return bit
 return 64
def compare_tree(web,body,case_id):
 """Independent whole-tree comparison, the same rule as the harness: TTinDVu skipped, ngayLapTKhai counted, not compared."""
 left=document(web);right=document(body);state={'leaves':0,'mask':0,'ordinals':[],'first':0}
 def differ(bit,ordinal):
  state['mask']|=bit;ordinal=max(1,ordinal)
  if not state['first']:state['first']=ordinal
  if bit in (4,8,16,32,64) and len(state['ordinals'])<MISMATCH_ORDINALS:state['ordinals'].append(ordinal)
 def attributes(node):return {key:value for key,value in node.attrib.items()}
 def equal(a,b,path):
  if a.tag!=b.tag:differ(1,state['leaves']+1);return
  if attributes(a)!=attributes(b):differ(2,state['leaves']+1)
  x,y=list(a),list(b)
  if not x and not y:
   if path.startswith(SERVICE_PATH):return
   state['leaves']+=1
   if path!=DATE_PATH and (a.text or '')!=(b.text or ''):differ(region(path),state['leaves'])
   return
  if len(x)!=len(y) or (a.text or '').strip() or (b.text or '').strip():differ(1,state['leaves']+1);return
  for c,d in zip(x,y):equal(c,d,path+'/'+c.tag[len(NS)+2:] if c.tag.startswith('{'+NS+'}') else path+'/?')
 equal(left,right,'HSoThueDTu')
 expected=khbs.tax_leaves(case_id)
 if state['leaves']!=expected:state['mask']|=1
 return {'allTaxValuesMatched':state['mask']==0,'checkedTaxLeafCount':state['leaves'],'expectedTaxLeafCount':expected,'mismatchSectionMask':state['mask'],'firstDifferenceOrdinal':state['first'],'mismatchLeafOrdinals':state['ordinals']}

def validate_provenance(body,native,run_id,builder_commit,source_commit,case_id,artifact_commit,run_attempt,version=oracle.DEFAULT):
 if case_id not in BRANCHES:fail('PROVENANCE')
 if not isinstance(run_id,str) or not re.fullmatch('[0-9]{1,20}',run_id) or not isinstance(run_attempt,str) or not re.fullmatch('[1-9][0-9]{0,5}',run_attempt):fail('PROVENANCE')
 exact_sha(builder_commit);exact_sha(source_commit);exact_sha(artifact_commit)
 if not isinstance(body,bytes) or not 0<len(body)<=reader.MAX_MANIFEST or not isinstance(native,bytes):fail('PROVENANCE')
 try:observed=reader.json_object(body,'MANIFEST')
 except reader.InputError:fail('PROVENANCE')
 expected={'format':'htkk-khbs-native-output-staging-v1','builderRepository':BUILDER,'builderCommit':builder_commit,'runId':run_id,'runAttempt':int(run_attempt),'sourceRepository':REPO,'sourceCommit':source_commit,'sourceVersion':oracle.baseline(version)['serviceVersion'],'runtimeHost':'clr2-x86-reference','caseId':case_id,'artifactCommit':artifact_commit,
  'inputsSynthetic':True,'originalProcessStopped':True,'originalSourcesUnmodified':True,'inputMode':'khbs-c0-save-b1-import-summary-reexport','originalImportSucceeded':True,'originalSummarySucceeded':True,'originalExportSucceeded':True,'originalExporterValidatedSchema':True,
  'webImportInputSha256':observed.get('webImportInputSha256'),'originalOutputSha256':hashlib.sha256(native).hexdigest(),'originalOutputBytes':len(native),'creationDateRule':'native-export-current-date','fullRoundTrip':False}
 exact_sha(expected['webImportInputSha256'],64)
 if set(observed)!=set(expected)|set(HARNESS) or any(type(observed[key]) is not type(value) or observed[key]!=value for key,value in expected.items()):fail('PROVENANCE')
 for key,rule in HARNESS.items():
  value=observed[key]
  if rule is bool:
   if type(value) is not bool:fail('PROVENANCE')
  elif type(value) is not int or not rule[0]<=value<=rule[1]:fail('PROVENANCE')
 return observed

def read_evidence(directory,run_id,builder_commit,source_commit,case_id,artifact_commit,run_attempt,version=oracle.DEFAULT):
 directory=pathlib.Path(directory)
 if transport.unsafe_path(directory) or not directory.is_dir() or set(p.name for p in directory.iterdir())!=set(NAMES):fail('FILES')
 native=transport.safe_read(directory/NAMES[0],reader.MAX_XML)
 provenance=transport.safe_read(directory/NAMES[1],reader.MAX_MANIFEST)
 metadata=validate_provenance(provenance,native,run_id,builder_commit,source_commit,case_id,artifact_commit,run_attempt,version)
 document(native)
 return native,metadata

def publish(native,metadata,token,fetch=None,today=None,retain_immutable=False,version=oracle.DEFAULT):
 # Revalidate even when called independently of the fixed-path staging reader.
 metadata=validate_provenance(json.dumps(metadata).encode('utf-8'),native,metadata.get('runId'),metadata.get('builderCommit'),metadata.get('sourceCommit'),metadata.get('caseId'),metadata.get('artifactCommit'),str(metadata.get('runAttempt','')),version)
 if not isinstance(token,str) or not token:fail('AUTH')
 fetch=fetch or transport.api
 if retain_immutable:transport.assert_current(fetch,token,metadata['sourceCommit'])
 # Only the fixed PRIVATE immutable input artifact of this case may justify retention.
 inputs=reader.download(token,fetch=lambda path,read_token:fetch(path,read_token),expected_source=metadata['sourceCommit'],expected_case=metadata['caseId'],artifact_commit=metadata['artifactCommit'])
 name=reader.xml_name(metadata['caseId']);input_manifest=reader.validate_manifest(inputs['manifest.json'])
 if hashlib.sha256(inputs[name]).hexdigest()!=metadata['webImportInputSha256']:fail('HASH')
 checked=validate_native(native,inputs[name],metadata['caseId'],today,version)
 comparison=compare_tree(inputs[name],native,metadata['caseId'])
 # Independent recomputation vs the harness; a disagreement is recorded, never hidden.
 comparison['harnessAgreement']=comparison['allTaxValuesMatched']==metadata['harnessTreeMatched'] and comparison['mismatchSectionMask']==metadata['harnessMismatchMask'] and comparison['checkedTaxLeafCount']==metadata['harnessLeafCount'] and comparison['firstDifferenceOrdinal']==metadata['harnessFirstDifferenceOrdinal']
 manifest={'format':'htkk-khbs-native-output-reference-v1','scope':'single-fixed-synthetic-khbs-native-reexport','provenance':metadata,'privacyCheck':checked,'comparison':comparison,
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
 commit=fetch('/git/commits',token,{'message':'Private original native KHBS reexport '+metadata['caseId']+' '+metadata['sourceCommit'],'tree':tree_sha,'parents':[]})
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
 return {'format':'htkk-khbs-native-output-publication-status-v1','status':'published','caseId':metadata['caseId'],'sourceCommit':metadata['sourceCommit'],'artifactCommit':artifact,'nativeOutputSha256':metadata['originalOutputSha256'],'bytes':len(native),'allTaxValuesMatched':comparison['allTaxValuesMatched'],'mismatchSectionMask':comparison['mismatchSectionMask'],'firstDifferenceOrdinal':comparison['firstDifferenceOrdinal'],'mismatchLeafOrdinals':[n for n in comparison['mismatchLeafOrdinals'] if type(n) is int and 0<n<=4096][:MISMATCH_ORDINALS],'harnessAgreement':comparison['harnessAgreement']}

def main():
 directory=pathlib.Path(os.environ.get('RUNNER_TEMP',''))/DIRECTORY
 try:
  if os.environ.get('GITHUB_REPOSITORY')!=BUILDER:fail('BUILDER')
  token=os.environ.get('SOURCE_PUBLISH_TOKEN') or os.environ.get('SOURCE_READ_TOKEN')
  if not token:fail('AUTH')
  if not directory.exists():print(json.dumps({'format':'htkk-khbs-native-output-publication-status-v1','status':'not-staged'},separators=(',',':')));return
  version=oracle.version(os.environ)
  native,metadata=read_evidence(directory,os.environ.get('GITHUB_RUN_ID'),os.environ.get('GITHUB_SHA'),os.environ.get('EXPECTED_WEB_SOURCE_SHA'),os.environ.get('EXPECTED_WEB_CASE_ID'),os.environ.get('WEB_ARTIFACT_COMMIT'),os.environ.get('GITHUB_RUN_ATTEMPT',''),version=version)
  print(json.dumps(publish(native,metadata,token,retain_immutable=True,version=version),separators=(',',':')))
 except Exception as error:
  print(json.dumps(safe_failure(error),separators=(',',':')))
  raise SystemExit('Native KHBS output retention failed; no XML, paths, credentials or raw remote error published.')
 finally:
  # Never follow an unsafe directory or erase another task's runner files.
  if os.environ.get('RUNNER_TEMP') and directory.name==DIRECTORY and not transport.unsafe_path(directory):shutil.rmtree(directory,ignore_errors=True)

if __name__=='__main__':main()
