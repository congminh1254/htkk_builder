"""Privately retain byte-exact native reexports of six fixed synthetic web cases.

Privacy adapters operate only on an in-memory copy. Original output bytes are
never rewritten. Neither this publisher nor its fixtures establish filing-wide
compatibility or independent XSD validation.
"""
import base64,datetime,hashlib,importlib.util,io,json,os,pathlib,re,shutil,urllib.error
import xml.etree.ElementTree as ET

def module(name,file):
 spec=importlib.util.spec_from_file_location(name,pathlib.Path(__file__).with_name(file));value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
transport=module('native_output_transport','publish-htkk-web-inputs.py')
reader=transport.reader
privacy=reader.privacy
REPO=reader.REPO
BUILDER=reader.BUILDER
DIRECTORY='htkk-web-native-output'
NAMES=('01GTGT-native.xml','provenance.json')
BRANCHES={'01GTGT-zero-M10-2026':'gtgt-web-native-zero-output','01GTGT-sale10-M10-2026':'gtgt-web-native-sale10-output','01GTGT-sale10-half-M10-2026':'gtgt-web-native-sale10-half-output','01GTGT-sale10-manual-M10-2026':'gtgt-web-native-sale10-manual-output','01GTGT-sale5-half-M10-2026':'gtgt-web-native-sale5-half-output','01GTGT-sale5-manual-M10-2026':'gtgt-web-native-sale5-manual-output'}
PINS={**privacy.PINS,'Project/FarPoint.Win.Spread.dll':'2e7a0d4fc1ef6f219dd3a237ae6b26549ad03541d58da6f45d638309d2fa4c50'}
MONEY=('ct22','ct23','ct24','ct23a','ct24a','ct25','ct26','ct27','ct28','ct29','ct30','ct31','ct32','ct33','ct32a','ct34','ct35','ct36','ct37','ct38','ct39a','ct40a','ct40b','ct40','ct41','ct42','ct43')
SERVICE={'maDVu':'HTKK','tenDVu':'HỖ TRỢ KÊ KHAI THUẾ','pbanDVu':'5.8.1'}
PREFIX='HSoKhaiThue/TTinChung/TTinTKhaiThue/TKhaiThue/'
SERVICE_PREFIX='HSoThueDTu/HSoKhaiThue/TTinChung/TTinDVu/'
CREATION='HSoThueDTu/'+PREFIX+'ngayLapTKhai'
CODES=transport.CODES|frozenset(('PROVENANCE','COMPARE','FILES','NATIVE_IDENTITY','NATIVE_DATE'))

class OutputError(ValueError):
 def __init__(self,code):
  if code not in CODES:raise ValueError('Invalid safe output error')
  self.code=code;super().__init__(code)
def fail(code):raise OutputError(code)
def safe_failure(error):
 if isinstance(error,OutputError):code=error.code if error.code in CODES else 'INTERNAL'
 elif isinstance(error,privacy.EvidenceError):code='XML_PRIVACY'
 else:code=transport.safe_failure(error)['code']
 return {'format':'htkk-web-native-output-publication-status-v1','status':'rejected','code':code}
def exact_sha(value,count=40):
 if not isinstance(value,str) or not re.fullmatch('[0-9a-f]{'+str(count)+'}',value):fail('PROVENANCE')
 return value
def exact_run(value):
 if not isinstance(value,str) or not re.fullmatch('[0-9]{1,20}',value):fail('PROVENANCE')
 return value
def leaf(root,path):
 query='./'+'/'.join('{'+privacy.NS+'}'+name for name in path.split('/'))
 values=root.findall(query)
 if len(values)!=1 or values[0].attrib or len(values[0]):fail('XML_PRIVACY')
 return values[0]

def native_document(body):
 if not isinstance(body,bytes) or not 0<len(body)<=reader.MAX_XML:fail('XML_SIZE')
 try:text=body.decode('utf-8-sig')
 except UnicodeError:fail('XML_ENCODING')
 if re.search(r'<!|<\?(?!xml\s)',text,re.I) or text.count('<?')>1:fail('XML_DECLARATION')
 try:
  for _,(prefix,uri) in ET.iterparse(io.BytesIO(body),events=('start-ns',)):
   if (prefix,uri) not in (('',privacy.NS),('xsi',privacy.XSI)):fail('XML_PRIVACY')
  return ET.fromstring(body)
 except ET.ParseError:fail('XML_PARSE')

def validate_native(body,case_id,today=None):
 if case_id not in BRANCHES:fail('PROVENANCE')
 root=native_document(body)
 if root.tag!='{'+privacy.NS+'}HSoThueDTu':fail('XML_PRIVACY')
 for name,value in SERVICE.items():
  if leaf(root,'HSoKhaiThue/TTinChung/TTinDVu/'+name).text!=value:fail('NATIVE_IDENTITY')
 provider=leaf(root,'HSoKhaiThue/TTinChung/TTinDVu/ttinNhaCCapDVu').text
 if not isinstance(provider,str) or not re.fullmatch('[0-9A-F]{32}',provider):fail('NATIVE_IDENTITY')
 created=leaf(root,PREFIX+'ngayLapTKhai');signed=leaf(root,PREFIX+'ngayKy')
 if signed.text!='2026-10-25' or not isinstance(created.text,str) or not re.fullmatch('[0-9]{4}-[0-9]{2}-[0-9]{2}',created.text):fail('NATIVE_DATE')
 try:created_date=datetime.date.fromisoformat(created.text)
 except ValueError:fail('NATIVE_DATE')
 today=today or datetime.datetime.now(datetime.timezone.utc).date()
 if abs((today-created_date).days)>1:fail('NATIVE_DATE')
 # Only the known historical sign date is adapted for the existing privacy
 # validator's freshness policy, after independently checking its exact value.
 # This is NOT a comparison normalization and never changes published bytes.
 signed.text=created.text
 if leaf(root,'HSoKhaiThue/CTieuTKhaiChinh/ct21').text!='0':fail('XML_PRIVACY')
 expected=reader.CASE_MONEY[case_id]
 for name in MONEY:
  values=root.findall('.//{'+privacy.NS+'}'+name)
  if len(values)!=1 or values[0].attrib or len(values[0]) or values[0].text!=expected.get(name,'0'):fail('XML_PRIVACY')
  values[0].text='0'
 ET.register_namespace('',privacy.NS);ET.register_namespace('xsi',privacy.XSI)
 checked=privacy.validate_xml(ET.tostring(root,encoding='utf-8'),today)
 if checked['leafCount']!=74:fail('XML_PRIVACY')
 return {'privacyValuesVerified':True,'leafCount':74,'fixedSyntheticCase':case_id,'historicalSigningDate':'2026-10-25','creationDateRule':'native-export-current-date','nativeServiceIdentityVerified':True}

def validate_provenance(body,native,run_id,builder_commit,source_commit,case_id,artifact_commit):
 if case_id not in BRANCHES:fail('PROVENANCE')
 exact_run(run_id);exact_sha(builder_commit);exact_sha(source_commit);exact_sha(artifact_commit)
 if not isinstance(body,bytes) or not 0<len(body)<=reader.MAX_MANIFEST:fail('PROVENANCE')
 observed=reader.json_object(body,'MANIFEST')
 expected={'format':'htkk-web-native-output-staging-v1','builderRepository':BUILDER,'builderCommit':builder_commit,'runId':run_id,'sourceRepository':REPO,'sourceCommit':source_commit,'sourceVersion':'5.8.1','runtimeHost':'clr2-x86-reference','caseId':case_id,'inputsSynthetic':True,'originalProcessStopped':True,'originalSourcesUnmodified':True,'originalExportSucceeded':True,'originalImportSucceeded':True,'originalReexportSucceeded':True,'originalExporterValidatedSchema':True,'webTaxComparisonPassed':True,'webTaxCheckedLeafCount':70,'webImportInputSha256':observed.get('webImportInputSha256'),'originalOutputSha256':hashlib.sha256(native).hexdigest(),'originalOutputBytes':len(native),'artifactCommit':artifact_commit,'creationDateRule':'native-export-current-date','fullRoundTrip':False}
 exact_sha(expected['webImportInputSha256'],64)
 if set(observed)!=set(expected) or any(type(observed[key]) is not type(value) or observed[key]!=value for key,value in expected.items()):fail('PROVENANCE')
 return observed

def read_evidence(directory,run_id,builder_commit,source_commit,case_id,artifact_commit,today=None):
 directory=pathlib.Path(directory)
 if transport.unsafe_path(directory) or not directory.is_dir() or set(p.name for p in directory.iterdir())!=set(NAMES):fail('FILES')
 native=transport.safe_read(directory/NAMES[0],reader.MAX_XML)
 provenance=transport.safe_read(directory/NAMES[1],reader.MAX_MANIFEST)
 metadata=validate_provenance(provenance,native,run_id,builder_commit,source_commit,case_id,artifact_commit)
 validate_native(native,case_id,today)
 return native,metadata

def compare_tax(input_body,native_body):
 # Reader already validates the sole known web disclaimer before ET parsing.
 left=ET.fromstring(input_body);right=native_document(native_body);count=0
 def equal(a,b,path):
  nonlocal count
  if a.tag!=b.tag or a.attrib!=b.attrib or len(a)!=len(b):return False
  if len(a):
   if (a.text or '').strip() or (b.text or '').strip():return False
   for x,y in zip(a,b):
    if (x.tail or '').strip() or (y.tail or '').strip() or not equal(x,y,path+'/'+x.tag.rsplit('}',1)[-1]):return False
   return True
  if path.startswith(SERVICE_PREFIX):return path[len(SERVICE_PREFIX):] in (*SERVICE,'ttinNhaCCapDVu')
  count+=1
  return path==CREATION or (a.text or '')==(b.text or '')
 if not equal(left,right,'HSoThueDTu') or count!=70:fail('COMPARE')
 return {'allTaxValuesMatched':True,'checkedTaxLeafCount':70,'creationDateRule':'native-export-current-date','independentSchemaVerification':False}

def publish(native,metadata,token,fetch=None,today=None):
 # Revalidate even when called independently of the fixed-path staging reader.
 metadata=validate_provenance(json.dumps(metadata).encode('utf-8'),native,metadata.get('runId'),metadata.get('builderCommit'),metadata.get('sourceCommit'),metadata.get('caseId'),metadata.get('artifactCommit'))
 checked=validate_native(native,metadata['caseId'],today)
 if not isinstance(token,str) or not token:fail('AUTH')
 fetch=fetch or transport.api
 # Only a fixed PRIVATE immutable input artifact may justify retention.
 def read_api(path,read_token):return fetch(path,read_token)
 inputs=reader.download(token,fetch=read_api,expected_source=metadata['sourceCommit'],expected_case=metadata['caseId'],artifact_commit=metadata['artifactCommit'])
 input_manifest=reader.validate_manifest(inputs['manifest.json'])
 if hashlib.sha256(inputs['01GTGT-web.xml']).hexdigest()!=metadata['webImportInputSha256']:fail('HASH')
 comparison=compare_tax(inputs['01GTGT-web.xml'],native)
 manifest={'format':'htkk-web-native-output-reference-v1','scope':'single-fixed-synthetic-web-native-reexport','provenance':metadata,'sourcePins':PINS,'privacyCheck':checked,'comparison':comparison,'input':{'artifactCommit':metadata['artifactCommit'],'sourceCommit':metadata['sourceCommit'],'caseId':metadata['caseId'],'sha256':metadata['webImportInputSha256'],'bytes':input_manifest['bytes'],'producerSha256':input_manifest['producerSha256']},'files':{'01GTGT-native.xml':{'sha256':metadata['originalOutputSha256'],'bytes':len(native)}},'fullRoundTrip':False,'independentSchemaVerification':False}
 files={'01GTGT-native.xml':native,'manifest.json':(json.dumps(manifest,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode('utf-8')}
 if len(files['manifest.json'])>reader.MAX_MANIFEST:fail('MANIFEST')
 entries=[]
 for name,body in files.items():
  blob=fetch('/git/blobs',token,{'content':base64.b64encode(body).decode('ascii'),'encoding':'base64'})
  expected=hashlib.sha1(b'blob '+str(len(body)).encode('ascii')+b'\0'+body).hexdigest()
  if not isinstance(blob,dict) or blob.get('sha')!=expected:fail('HASH')
  entries.append({'path':name,'mode':'100644','type':'blob','sha':expected})
 tree=fetch('/git/trees',token,{'tree':entries})
 if not isinstance(tree,dict):fail('API_SHAPE')
 tree_sha=exact_sha(tree.get('sha'))
 commit=fetch('/git/commits',token,{'message':'Private original native reexport '+metadata['caseId']+' '+metadata['sourceCommit'],'tree':tree_sha,'parents':[]})
 if not isinstance(commit,dict):fail('API_SHAPE')
 artifact=exact_sha(commit.get('sha'));branch=BRANCHES[metadata['caseId']];missing=False
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
 return {'format':'htkk-web-native-output-publication-status-v1','status':'published','caseId':metadata['caseId'],'sourceCommit':metadata['sourceCommit'],'artifactCommit':artifact,'nativeOutputSha256':metadata['originalOutputSha256'],'bytes':len(native)}

def main():
 directory=pathlib.Path(os.environ.get('RUNNER_TEMP',''))/DIRECTORY
 try:
  if os.environ.get('GITHUB_REPOSITORY')!=BUILDER:fail('BUILDER')
  token=os.environ.get('SOURCE_PUBLISH_TOKEN') or os.environ.get('SOURCE_READ_TOKEN')
  if not token:fail('AUTH')
  native,metadata=read_evidence(directory,os.environ.get('GITHUB_RUN_ID'),os.environ.get('GITHUB_SHA'),os.environ.get('EXPECTED_WEB_SOURCE_SHA'),os.environ.get('EXPECTED_WEB_CASE_ID'),os.environ.get('WEB_ARTIFACT_COMMIT'))
  print(json.dumps(publish(native,metadata,token),separators=(',',':')))
 except Exception as error:
  print(json.dumps(safe_failure(error),separators=(',',':')))
  raise SystemExit('Native synthetic output retention failed; no XML, paths, credentials or raw remote error published.')
 finally:
  # Never follow an unsafe directory or erase another task's runner files.
  if os.environ.get('RUNNER_TEMP') and directory.name==DIRECTORY and not transport.unsafe_path(directory):shutil.rmtree(directory,ignore_errors=True)

if __name__=='__main__':main()
