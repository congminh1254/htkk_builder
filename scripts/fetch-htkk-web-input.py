"""Read only a fixed PRIVATE synthetic web XML input; never fetch source code.

Original downloaded bytes are staged unchanged. In-memory service replacement is
only a privacy-allowlist adapter, never native provenance or filing validation.
"""
import base64,datetime,hashlib,importlib.util,io,json,os,pathlib,re,shutil,tempfile,urllib.error,urllib.parse,urllib.request
import xml.etree.ElementTree as ET
REPO='htkk-net/htkk_web'
BUILDER='congminh1254/htkk_builder'
BRANCH='gtgt-web-reference-input'
NAMES=('01GTGT-web.xml','manifest.json')
_case_spec=importlib.util.spec_from_file_location('trusted_case_input_metadata',pathlib.Path(__file__).with_name('htkk_native_cases.py'));case_registry=importlib.util.module_from_spec(_case_spec);_case_spec.loader.exec_module(case_registry)
CASES={id:c['format']for id,c in case_registry.CASES.items()}
SALE10={'ct32':'1000000','ct33':'100000','ct27':'1000000','ct28':'100000','ct34':'1000000','ct35':'100000','ct36':'100000','ct40a':'100000','ct40':'100000'}
SALE10_HALF={key:('5' if key in ('ct32','ct27','ct34') else '1') for key in SALE10}
SALE10_MANUAL={key:('1000000' if key in ('ct32','ct27','ct34') else '7') for key in SALE10}
SALE5_HALF={('ct30' if key=='ct32' else 'ct31' if key=='ct33' else key):('10' if key in ('ct32','ct27','ct34') else '1') for key in SALE10}
SALE5_MANUAL={('ct30' if key=='ct32' else 'ct31' if key=='ct33' else key):('1000000' if key in ('ct32','ct27','ct34') else '7') for key in SALE10}
CASE_MONEY={'01GTGT-zero-M10-2026':{},'01GTGT-sale10-M10-2026':SALE10,'01GTGT-sale10-half-M10-2026':SALE10_HALF,'01GTGT-sale10-manual-M10-2026':SALE10_MANUAL,'01GTGT-sale5-half-M10-2026':SALE5_HALF,'01GTGT-sale5-manual-M10-2026':SALE5_MANUAL,'01GTGT-noactivity-zero-M10-2026':{},'01GTGT-noactivity-reset-sale10-M10-2026':{},'01GTGT-noactivity-cancel-sale10-M10-2026':SALE10,'01GTGT-noactivity-uncheck-sale10-M10-2026':{},'01GTGT-noactivity-keep-credit-M10-2026':{'ct22':'7','ct41':'7','ct43':'7'},'01GTGT-zero-Q4-2026':{},'01GTGT-native-import-sale10-M10-2026':SALE10,'01GTGT-annex12-zero-two-locations-M10-2026':{},'01GTGT-annex12-two-plants-nonzero-M10-2026':SALE10}
PERIOD_FIELDS={'kieuKy':('M','Q'),'kyKKhai':('10/2026','4/2026'),'kyKKhaiTuNgay':('01/10/2026','01/10/2026'),'kyKKhaiDenNgay':('31/10/2026','31/12/2026')}
CASE_CHECKBOX={case:('1' if case in ('01GTGT-noactivity-zero-M10-2026', '01GTGT-noactivity-reset-sale10-M10-2026', '01GTGT-noactivity-keep-credit-M10-2026') else '0') for case in CASES}
MAX_XML=262144
MAX_MANIFEST=16384
MAX_API=600000
# 01/GTGT is verified against HTKK, so the web exporter (htkk_web lib/export-labelling.ts) writes no
# pre-root comment and the neutral tool identity. The earlier draft disclaimer (COMMENT) is now
# rejected like any other comment.
COMMENT='<!-- BẢN NHÁP; KHÔNG NỘP THUẾ; CHƯA KIỂM CHỨNG ĐẦY ĐỦ VỚI HTKK WINDOWS. -->'
PREAMBLE='<?xml version="1.0" encoding="UTF-8"?>\n'
SERVICE={'maDVu':'CCKK','tenDVu':'Công cụ Kê khai','pbanDVu':'0.9.2','ttinNhaCCapDVu':'hotrokekhai.net — Công cụ Kê khai, công cụ độc lập'}
CODES=frozenset(('AUTH','HTTP','NETWORK','API_SIZE','API_JSON','API_SHAPE','PRIVATE_REPO','SOURCE_COMMIT','MANIFEST','HASH','XML_SIZE','XML_ENCODING','XML_DECLARATION','XML_PARSE','XML_SERVICE','XML_PRIVACY','STAGING','BUILDER','IO','INTERNAL'))
_spec=importlib.util.spec_from_file_location('htkk_export_privacy',pathlib.Path(__file__).with_name('publish-gtgt-export-evidence.py'))
privacy=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(privacy)
_annex_spec=importlib.util.spec_from_file_location('htkk_annex12_web_input_contract',pathlib.Path(__file__).with_name('htkk_annex12_web_cases.py'))
annex12=importlib.util.module_from_spec(_annex_spec);_annex_spec.loader.exec_module(annex12)
if set(annex12.CASES)!=set(case_registry.ANNEX12_CASES):raise ValueError('CASE_POLICY')
# Annex manifests come from a separate application producer with its own fixed keys.
ANNEX_PRODUCER='scripts/generate-htkk-web-annex12-reference.mjs'
ANNEX_NATIVE_REFERENCE='6956eea0fa865e98da71ad3ce23ed6a527e7a17761c6fb11032a11fc0a97b8cb'
ANNEX_NATIVE_NODES={annex12.ZERO_CASE:(True,131),annex12.TWO_PLANTS_CASE:(False,0)}
# 01-10/GTGT (PL_NQ142_GTGT, oracle HTKK 5.8.2): own producer, manifest keys and exact allowlist.
_annex10_spec=importlib.util.spec_from_file_location('htkk_annex10_web_input_contract',pathlib.Path(__file__).with_name('htkk_annex10_web_cases.py'))
annex10=importlib.util.module_from_spec(_annex10_spec);_annex10_spec.loader.exec_module(annex10)
if set(annex10.CASES)!=set(case_registry.ANNEX10_CASES):raise ValueError('CASE_POLICY')
ANNEX10_PRODUCER='scripts/generate-htkk-web-annex10-reference.mjs'
ANNEX10_NATIVE_BASE='6956eea0fa865e98da71ad3ce23ed6a527e7a17761c6fb11032a11fc0a97b8cb'
CASE_MONEY.update({case:annex10.money(case) for case in annex10.CASES})
# Kê khai bổ sung lần 1 (KHBS, oracle HTKK 5.8.2): own producer, manifest keys and exact PLuc allowlist.
_khbs_spec=importlib.util.spec_from_file_location('htkk_khbs_web_input_contract',pathlib.Path(__file__).with_name('htkk_khbs_web_cases.py'))
khbs=importlib.util.module_from_spec(_khbs_spec);_khbs_spec.loader.exec_module(khbs)
if set(khbs.CASES)!=set(case_registry.KHBS_CASES):raise ValueError('CASE_POLICY')
CASE_MONEY.update({case:khbs.money(case) for case in khbs.CASES})
# Declaration-family cases (03/TNDN, BCTC, TNCN, 01/CNKD): own producer, file names and allowlist.
_declaration_spec=importlib.util.spec_from_file_location('htkk_declaration_web_input_contract',pathlib.Path(__file__).with_name('htkk_declaration_web_cases.py'))
declaration=importlib.util.module_from_spec(_declaration_spec);_declaration_spec.loader.exec_module(declaration)
if set(declaration.CASES)!=set(case_registry.DECLARATION_CASES):raise ValueError('CASE_POLICY')
DECLARATION_NAMES=('declaration-web.xml','manifest.json')
DECLARATION_PRODUCER='scripts/generate-htkk-declaration-reference.mjs'
DECLARATION_ERRORS={'SIZE':'XML_SIZE','ENCODING':'XML_ENCODING','DECLARATION':'XML_DECLARATION','PARSE':'XML_PARSE','SERVICE':'XML_SERVICE','MANIFEST':'MANIFEST'}
def names(case_id):
 if case_id not in CASES:raise InputError('MANIFEST')
 return DECLARATION_NAMES if declaration.is_case(case_id) else NAMES
def xml_name(case_id):return names(case_id)[0]
class InputError(ValueError):
 def __init__(self,code,**context):
  if code not in CODES:raise ValueError('Invalid safe input error')
  self.code=code;self.context=safe_context(context);super().__init__(code)
def safe_context(context):
 result={}
 for key,minimum,maximum in (('httpStatus',100,599),('leafIndex',0,len(privacy.LEAF_ORDER))):
  value=context.get(key)
  if type(value) is int and minimum<=value<=maximum:result[key]=value
 if isinstance(context.get('valueShape'),str) and context['valueShape'] in privacy.SHAPES:result['valueShape']=context['valueShape']
 return result
def safe_failure(error):
 code='INTERNAL';context={}
 if isinstance(error,InputError):code=error.code if isinstance(error.code,str) and error.code in CODES else 'INTERNAL';context=safe_context(error.context if isinstance(error.context,dict) else {})
 elif isinstance(error,urllib.error.HTTPError):code='AUTH' if error.code in (401,403) else 'HTTP';context=safe_context({'httpStatus':error.code})
 elif isinstance(error,urllib.error.URLError):code='NETWORK'
 elif isinstance(error,OSError):code='IO'
 return {'format':'htkk-web-reference-input-fetch-status-v1','status':'rejected','code':code,**context}
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args):return None
def json_object(body,code):
 def unique(pairs):
  value={}
  for key,item in pairs:
   if key in value:raise InputError(code)
   value[key]=item
  return value
 try:
  value=json.loads(body.decode('utf-8-sig'),object_pairs_hook=unique)
  if not isinstance(value,dict):raise InputError(code)
  return value
 except (UnicodeError,json.JSONDecodeError):raise InputError(code) from None
def api(path,token):
 if not isinstance(token,str) or not token:raise InputError('AUTH')
 request=urllib.request.Request('https://api.github.com/repos/'+REPO+path,headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','User-Agent':'HTKK-Private-Web-Input-Read/1.0','Accept-Encoding':'identity'})
 with urllib.request.build_opener(NoRedirect()).open(request,timeout=30) as response:
  if response.status!=200:raise InputError('HTTP',httpStatus=response.status)
  raw=response.read(MAX_API+1)
 if len(raw)>MAX_API:raise InputError('API_SIZE')
 return json_object(raw,'API_JSON')
def git_sha(value,code='API_SHAPE'):
 if not isinstance(value,str) or not re.fullmatch('[0-9a-f]{40}',value):raise InputError(code)
 return value
def content_file(envelope,name,maximum):
 if not isinstance(envelope,dict) or envelope.get('type')!='file' or envelope.get('name')!=name or envelope.get('path')!=name or envelope.get('encoding')!='base64' or type(envelope.get('size')) is not int or not 0<envelope['size']<=maximum:raise InputError('API_SHAPE')
 encoded=envelope.get('content')
 if not isinstance(encoded,str) or len(encoded)>maximum*2 or not re.fullmatch('[A-Za-z0-9+/=\r\n]*',encoded):raise InputError('API_SHAPE')
 try:body=base64.b64decode(encoded.replace('\r','').replace('\n',''),validate=True)
 except (ValueError,base64.binascii.Error):raise InputError('API_SHAPE') from None
 if len(body)!=envelope['size'] or not 0<len(body)<=maximum:raise InputError('API_SIZE')
 # Verify GitHub's Git blob identity, not only its declared decoded size.
 actual=hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest()
 if git_sha(envelope.get('sha'))!=actual:raise InputError('HASH')
 return body
def validate_manifest(body):
 if not isinstance(body,bytes) or not 0<len(body)<=MAX_MANIFEST:raise InputError('MANIFEST')
 manifest=json_object(body,'MANIFEST')
 case=manifest.get('caseId')
 if not isinstance(case,str) or case not in CASES:raise InputError('MANIFEST')
 fixed={'format':CASES[case],'sourceRepository':REPO,'sourceVersion':'0.9.2','caseId':case,'inputsSynthetic':True,'exporter':'lib/htkk-xml.ts'}
 variable={'sourceCommit','producerSha256','xmlSha256','bytes'}
 if declaration.is_case(case):
  spec=declaration.case(case);c=case_registry.CASES[case]
  fixed.update(exporter='lib/htkk-declaration-engines.ts',producer=DECLARATION_PRODUCER,menuId=spec['menuId'],engine=spec['family'],xmlVersion=spec['xmlVersion'],schemaId=spec['schemaId'],annexes=c['unit']['annexes'],leafCount=spec['leafCount'],nativeQualified=False,filingEnabled=False)
  # A per-case oracle the web manifest names must be the registry case version (never the default spelling).
  if case in declaration.MANIFEST_HTKK_VERSION_CASES:fixed['htkkVersion']=case_registry.htkk_version(case)
 if annex12.is_case(case):
  compared,nodes=ANNEX_NATIVE_NODES[case]
  fixed.update(exporter='lib/htkk-gtgt-annex12-xml.ts',producer=ANNEX_PRODUCER,nativeAnnexReferenceSha256=ANNEX_NATIVE_REFERENCE,fullCompatibilityVerified=False,independentXsdPassed=True,nativeLeafComparisonPassed=compared,nativeNodesCompared=nodes,nativeAnnexRoundTripVerified=False)
  variable=variable|{'expectedAnnexLeaves'}
 if annex10.is_case(case):
  fixed.update(exporter='lib/htkk-gtgt-annex10-xml.ts',producer=ANNEX10_PRODUCER,htkkVersion=case_registry.htkk_version(case),nativeBaseSha256=ANNEX10_NATIVE_BASE,fullCompatibilityVerified=False,independentXsdPassed=True,nativeAnnexRoundTripVerified=False,expectedMainMoney=annex10.money(case))
  variable=variable|{'expectedAnnexLeaves'}
 if khbs.is_case(case):
  fixed.update(khbs.manifest_fields(case));fixed['htkkVersion']=case_registry.htkk_version(case)
 if set(manifest)!=set(fixed)|variable:raise InputError('MANIFEST')
 if any(type(manifest[key]) is not type(value) or manifest[key]!=value for key,value in fixed.items()):raise InputError('MANIFEST')
 git_sha(manifest['sourceCommit'],'MANIFEST')
 for key in ('producerSha256','xmlSha256'):
  if not isinstance(manifest[key],str) or not re.fullmatch('[0-9a-f]{64}',manifest[key]):raise InputError('MANIFEST')
 if type(manifest['bytes']) is not int or not 0<manifest['bytes']<=MAX_XML:raise InputError('MANIFEST')
 if annex12.is_case(case) or annex10.is_case(case):
  rows=manifest['expectedAnnexLeaves']
  if type(rows) is not list or not 0<len(rows)<=256 or any(type(row) is not list or len(row)!=3 or any(type(item) is not str or len(item)>160 for item in row) for row in rows):raise InputError('MANIFEST')
 return manifest
def annex_manifest_leaves(root):
 # Recompute the producer's canonical annex rows from the validated XML itself:
 # every leaf and every attributed element below PLuc, in document order.
 rows=[];prefix='{'+privacy.NS+'}'
 def visit(node,path):
  name=node.tag[len(prefix):];current=path+'/'+name if path else name
  attrs=';'.join(key+'='+value for key,value in node.attrib.items())
  if len(node)==0 or node.attrib:rows.append([current,(node.text or '') if len(node)==0 else '',attrs])
  for child in node:visit(child,current)
 pluc=root.find('./'+prefix+'HSoKhaiThue/'+prefix+'PLuc')
 for child in pluc:visit(child,'')
 return rows
def validate_web_xml(body,today=None,case_id='01GTGT-zero-M10-2026',manifest=None):
 if case_id not in CASES:raise InputError('MANIFEST')
 if declaration.is_case(case_id):
  try:return declaration.validate_web_input(body,case_id,manifest)
  except declaration.DeclarationWebCaseError as error:raise InputError(DECLARATION_ERRORS.get(error.code,'XML_PRIVACY')) from None
 annex=annex12 if annex12.is_case(case_id) else annex10 if annex10.is_case(case_id) else None;amendment=khbs.is_case(case_id)
 fixed_day=datetime.date.fromisoformat(annex.FIXED_DATE if annex else khbs.FIXED_DATE if amendment else '2026-10-25')
 if not isinstance(body,bytes) or not 0<len(body)<=MAX_XML:raise InputError('XML_SIZE')
 try:text=body.decode('utf-8')
 except UnicodeError:raise InputError('XML_ENCODING') from None
 # The actual exporter emits the XML declaration and then the root, nothing else. No
 # comment (the old draft disclaimer included), declaration or entity reaches the parser.
 if not text.startswith(PREAMBLE+'<HSoThueDTu '):raise InputError('XML_DECLARATION')
 no_comment=text
 if re.search(r'<!|<\?(?!xml\s)',no_comment,re.I) or no_comment.count('<?')!=1:raise InputError('XML_DECLARATION')
 try:
  for event,(prefix,uri) in ET.iterparse(io.BytesIO(no_comment.encode('utf-8')),events=('start-ns',)):
   if (prefix,uri) not in (('',privacy.NS),('xsi',privacy.XSI)):raise InputError('XML_PRIVACY')
  root=ET.fromstring(no_comment)
 except ET.ParseError:raise InputError('XML_PARSE') from None
 ns='{'+privacy.NS+'}'
 # This producer is a fixed historical fixture, not a daily native export.
 # Validate both business dates exactly before reusing the zero-case allowlist.
 for name in ('ngayLapTKhai','ngayKy'):
  nodes=root.findall('./'+ns+'HSoKhaiThue/'+ns+'TTinChung/'+ns+'TTinTKhaiThue/'+ns+'TKhaiThue/'+ns+name)
  if len(nodes)!=1 or nodes[0].text!=fixed_day.isoformat():raise InputError('XML_PRIVACY')
 services=root.findall('./'+ns+'HSoKhaiThue/'+ns+'TTinChung/'+ns+'TTinDVu')
 if len(services)!=1:raise InputError('XML_SERVICE')
 service=services[0]
 if [child.tag for child in service]!=[ns+name for name in SERVICE]:raise InputError('XML_SERVICE')
 for child,(name,value) in zip(service,SERVICE.items()):
  if child.attrib or len(child) or child.text!=value:raise InputError('XML_SERVICE')
 if case_id=='01GTGT-zero-Q4-2026':
  for name,(baseline,expected) in PERIOD_FIELDS.items():
   nodes=root.findall('./'+ns+'HSoKhaiThue/'+ns+'TTinChung/'+ns+'TTinTKhaiThue/'+ns+'TKhaiThue/'+ns+'KyKKhaiThue/'+ns+name)
   if len(nodes)!=1 or nodes[0].attrib or len(nodes[0]) or nodes[0].text!=expected:raise InputError('XML_PRIVACY')
   nodes[0].text=baseline
 if annex:
  # Exact fixed annex subtree first; then an IN-MEMORY projection without it
  # reuses the unchanged no-annex allowlist. Staged bytes are never changed.
  try:
   annex.validate_annex(root,case_id)
   if manifest is not None and manifest.get('expectedAnnexLeaves')!=annex_manifest_leaves(root):raise InputError('MANIFEST')
   annex.strip_annex(root)
  except annex.AnnexWebContractError:raise InputError('XML_PRIVACY') from None
 if amendment:
  # Exact fixed PL01_KHBS/PL01_1_KHBS subtree and B/1 header first; then an IN-MEMORY first-declaration
  # projection reuses the unchanged no-annex allowlist. Staged bytes are never changed.
  try:
   khbs.validate_khbs(root,case_id)
   khbs.project_first_declaration(root)
  except khbs.KhbsWebContractError:raise InputError('XML_PRIVACY') from None
 # Verify the fixed checkbox before adapting only the in-memory privacy copy.
 nodes=root.findall('./'+ns+'HSoKhaiThue/'+ns+'CTieuTKhaiChinh/'+ns+'ct21')
 if len(nodes)!=1 or nodes[0].attrib or len(nodes[0]) or nodes[0].text!=CASE_CHECKBOX[case_id]:raise InputError('XML_PRIVACY')
 nodes[0].text='0'
 # Exact fixed monetary case adapter; no arbitrary taxpayer amounts accepted.
 # Replacements occur ONLY in the in-memory privacy copy, never staged bytes.
 if CASE_MONEY[case_id]:
  for name,value in CASE_MONEY[case_id].items():
   nodes=root.findall('.//'+ns+name)
   if len(nodes)!=1 or nodes[0].attrib or len(nodes[0]) or nodes[0].text!=value:raise InputError('XML_PRIVACY')
   nodes[0].text='0'
 # Only four already-verified service leaf values are changed IN MEMORY to
 # reuse the existing complete zero-case privacy allowlist. Original bytes stay
 # untouched and are the sole bytes consumed by the Windows import probe.
 for child in service:
  local=child.tag[len(ns):]
  child.text='0'*32 if local=='ttinNhaCCapDVu' else privacy.BASE_HEADER['TTinDVu/'+local]
 ET.register_namespace('',privacy.NS);ET.register_namespace('xsi',privacy.XSI)
 try:privacy.validate_xml(ET.tostring(root,encoding='utf-8'),fixed_day)
 except privacy.EvidenceError as error:raise InputError('XML_PRIVACY',**safe_context(error.context)) from None
 result={'privacyValuesVerified':True,'serviceIdentity':'web-tool','nativeProvenance':False}
 if annex:result['annexTaxLeafCount']=annex.tax_leaves(case_id)
 if amendment:result['amendmentTaxLeafCount']=khbs.tax_leaves(case_id)
 return result
def download(token,fetch=None,today=None,expected_source=None,expected_case=None,artifact_commit=None):
 if artifact_commit is not None:git_sha(artifact_commit,'SOURCE_COMMIT')
 if expected_case is not None and expected_case not in CASES:raise InputError('MANIFEST')
 if expected_source is not None:git_sha(expected_source,'SOURCE_COMMIT')
 if not isinstance(token,str) or not token:raise InputError('AUTH')
 fetch=fetch or api
 info=fetch('',token)
 if not isinstance(info,dict) or info.get('private') is not True or info.get('full_name')!=REPO:raise InputError('PRIVATE_REPO')
 if artifact_commit is None:
  ref=fetch('/git/ref/heads/'+BRANCH,token)
  if not isinstance(ref,dict) or ref.get('ref')!='refs/heads/'+BRANCH or not isinstance(ref.get('object'),dict) or ref['object'].get('type')!='commit':raise InputError('API_SHAPE')
  artifact_commit=git_sha(ref['object'].get('sha'))
 else:
  pinned=fetch('/git/commits/'+artifact_commit,token)
  if not isinstance(pinned,dict) or pinned.get('sha')!=artifact_commit:raise InputError('SOURCE_COMMIT')
 query='?ref='+artifact_commit
 manifest_body=content_file(fetch('/contents/manifest.json'+query,token),'manifest.json',MAX_MANIFEST)
 manifest=validate_manifest(manifest_body)
 if expected_case is not None and manifest['caseId']!=expected_case:raise InputError('MANIFEST')
 if expected_source is not None and manifest['sourceCommit']!=expected_source:raise InputError('SOURCE_COMMIT')
 source=fetch('/git/commits/'+manifest['sourceCommit'],token)
 if not isinstance(source,dict) or source.get('sha')!=manifest['sourceCommit']:raise InputError('SOURCE_COMMIT')
 name=xml_name(manifest['caseId'])
 body=content_file(fetch('/contents/'+name+query,token),name,MAX_XML)
 if manifest['bytes']!=len(body) or manifest['xmlSha256']!=hashlib.sha256(body).hexdigest():raise InputError('HASH')
 validate_web_xml(body,today,manifest['caseId'],manifest)
 return {name:body,'manifest.json':manifest_body}
def stage(files,runner_temp,today=None):
 if not isinstance(files,dict) or 'manifest.json' not in files or any(not isinstance(body,bytes) for body in files.values()):raise InputError('STAGING')
 manifest=validate_manifest(files['manifest.json']);xml=xml_name(manifest['caseId'])
 if set(files)!=set(names(manifest['caseId'])):raise InputError('STAGING')
 if manifest['bytes']!=len(files[xml]) or manifest['xmlSha256']!=hashlib.sha256(files[xml]).hexdigest():raise InputError('HASH')
 validate_web_xml(files[xml],today,manifest['caseId'],manifest)
 parent=pathlib.Path(runner_temp);destination=parent/'htkk-web-reference-input'
 if parent.is_symlink() or not parent.is_dir() or destination.exists() or destination.is_symlink():raise InputError('STAGING')
 temporary=pathlib.Path(tempfile.mkdtemp(prefix='.htkk-web-reference-input-',dir=parent))
 try:
  for name in names(manifest['caseId']):
   with (temporary/name).open('xb') as stream:stream.write(files[name])
  # rename never overwrites an existing destination directory on Windows.
  if destination.exists() or destination.is_symlink():raise InputError('STAGING')
  temporary.rename(destination)
 except Exception:
  shutil.rmtree(temporary,ignore_errors=True);raise
 return destination
def main():
 try:
  if os.environ.get('GITHUB_REPOSITORY')!=BUILDER:raise InputError('BUILDER')
  token=os.environ.get('SOURCE_READ_TOKEN')
  if not token:raise InputError('AUTH')
  expected=git_sha(os.environ.get('EXPECTED_WEB_SOURCE_SHA'),'SOURCE_COMMIT')
  case=os.environ.get('EXPECTED_WEB_CASE_ID')
  if case not in CASES:raise InputError('MANIFEST')
  artifact=os.environ.get('WEB_ARTIFACT_COMMIT') or None
  files=download(token,expected_source=expected,expected_case=case,artifact_commit=artifact);stage(files,os.environ['RUNNER_TEMP']);manifest=validate_manifest(files['manifest.json'])
  print(json.dumps({'format':'htkk-web-reference-input-fetch-status-v1','status':'staged','bytes':manifest['bytes'],'xmlSha256':manifest['xmlSha256'],'sourceCommit':manifest['sourceCommit']},separators=(',',':')))
 except Exception as error:
  print(json.dumps(safe_failure(error),separators=(',',':')));raise SystemExit('Private synthetic web input unavailable; no XML, path, token or raw remote error published.')
if __name__=='__main__':main()
