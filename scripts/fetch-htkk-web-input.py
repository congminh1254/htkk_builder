"""Read only a fixed PRIVATE synthetic web XML input; never fetch source code.

Original downloaded bytes are staged unchanged. In-memory service replacement is
only a privacy-allowlist adapter, never native provenance or filing validation.
"""
import base64,hashlib,importlib.util,io,json,os,pathlib,re,shutil,tempfile,urllib.error,urllib.parse,urllib.request
import xml.etree.ElementTree as ET
REPO='congminh1254/htkk_web'
BUILDER='congminh1254/htkk_builder'
BRANCH='gtgt-web-reference-input'
NAMES=('01GTGT-web.xml','manifest.json')
MAX_XML=262144
MAX_MANIFEST=16384
MAX_API=600000
COMMENT='<!-- BẢN NHÁP; KHÔNG NỘP THUẾ; CHƯA KIỂM CHỨNG ĐẦY ĐỦ VỚI HTKK WINDOWS. -->'
PREAMBLE='<?xml version="1.0" encoding="UTF-8"?>\n'+COMMENT+'\n'
SERVICE={'maDVu':'HTKK-WEB-DRAFT','tenDVu':'Hỗ trợ kê khai — bản nháp','pbanDVu':'0.9.2','ttinNhaCCapDVu':'hotrokekhai.net — công cụ hỗ trợ độc lập'}
CODES=frozenset(('AUTH','HTTP','NETWORK','API_SIZE','API_JSON','API_SHAPE','PRIVATE_REPO','SOURCE_COMMIT','MANIFEST','HASH','XML_SIZE','XML_ENCODING','XML_DECLARATION','XML_PARSE','XML_SERVICE','XML_PRIVACY','STAGING','BUILDER','IO','INTERNAL'))
_spec=importlib.util.spec_from_file_location('htkk_export_privacy',pathlib.Path(__file__).with_name('publish-gtgt-export-evidence.py'))
privacy=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(privacy)
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
 fixed={'format':'htkk-web-zero-input-v1','sourceRepository':REPO,'sourceVersion':'0.9.2','caseId':'01GTGT-zero-M10-2026','inputsSynthetic':True,'exporter':'lib/htkk-xml.ts'}
 if set(manifest)!=set(fixed)|{'sourceCommit','producerSha256','xmlSha256','bytes'}:raise InputError('MANIFEST')
 if any(type(manifest[key]) is not type(value) or manifest[key]!=value for key,value in fixed.items()):raise InputError('MANIFEST')
 git_sha(manifest['sourceCommit'],'MANIFEST')
 for key in ('producerSha256','xmlSha256'):
  if not isinstance(manifest[key],str) or not re.fullmatch('[0-9a-f]{64}',manifest[key]):raise InputError('MANIFEST')
 if type(manifest['bytes']) is not int or not 0<manifest['bytes']<=MAX_XML:raise InputError('MANIFEST')
 return manifest
def validate_web_xml(body,today=None):
 if not isinstance(body,bytes) or not 0<len(body)<=MAX_XML:raise InputError('XML_SIZE')
 try:text=body.decode('utf-8')
 except UnicodeError:raise InputError('XML_ENCODING') from None
 # The actual exporter emits exactly this pre-root disclaimer. No other comment
 # is stripped, and no arbitrary declaration or entity can reach the parser.
 if not text.startswith(PREAMBLE) or text.count(COMMENT)!=1:raise InputError('XML_DECLARATION')
 no_comment=text.replace(COMMENT,'',1)
 if re.search(r'<!|<\?(?!xml\s)',no_comment,re.I) or no_comment.count('<?')!=1:raise InputError('XML_DECLARATION')
 try:
  for event,(prefix,uri) in ET.iterparse(io.BytesIO(no_comment.encode('utf-8')),events=('start-ns',)):
   if (prefix,uri) not in (('',privacy.NS),('xsi',privacy.XSI)):raise InputError('XML_PRIVACY')
  root=ET.fromstring(no_comment)
 except ET.ParseError:raise InputError('XML_PARSE') from None
 ns='{'+privacy.NS+'}'
 services=root.findall('./'+ns+'HSoKhaiThue/'+ns+'TTinChung/'+ns+'TTinDVu')
 if len(services)!=1:raise InputError('XML_SERVICE')
 service=services[0]
 if [child.tag for child in service]!=[ns+name for name in SERVICE]:raise InputError('XML_SERVICE')
 for child,(name,value) in zip(service,SERVICE.items()):
  if child.attrib or len(child) or child.text!=value:raise InputError('XML_SERVICE')
 # Only four already-verified service leaf values are changed IN MEMORY to
 # reuse the existing complete zero-case privacy allowlist. Original bytes stay
 # untouched and are the sole bytes consumed by the Windows import probe.
 for child in service:
  local=child.tag[len(ns):]
  child.text='0'*32 if local=='ttinNhaCCapDVu' else privacy.BASE_HEADER['TTinDVu/'+local]
 ET.register_namespace('',privacy.NS);ET.register_namespace('xsi',privacy.XSI)
 try:privacy.validate_xml(ET.tostring(root,encoding='utf-8'),today)
 except privacy.EvidenceError as error:raise InputError('XML_PRIVACY',**safe_context(error.context)) from None
 return {'privacyValuesVerified':True,'serviceIdentity':'web-draft','nativeProvenance':False}
def download(token,fetch=None,today=None,expected_source=None):
 if expected_source is not None:git_sha(expected_source,'SOURCE_COMMIT')
 if not isinstance(token,str) or not token:raise InputError('AUTH')
 fetch=fetch or api
 info=fetch('',token)
 if not isinstance(info,dict) or info.get('private') is not True or info.get('full_name')!=REPO:raise InputError('PRIVATE_REPO')
 ref=fetch('/git/ref/heads/'+BRANCH,token)
 if not isinstance(ref,dict) or ref.get('ref')!='refs/heads/'+BRANCH or not isinstance(ref.get('object'),dict) or ref['object'].get('type')!='commit':raise InputError('API_SHAPE')
 artifact_commit=git_sha(ref['object'].get('sha'))
 query='?ref='+artifact_commit
 manifest_body=content_file(fetch('/contents/manifest.json'+query,token),'manifest.json',MAX_MANIFEST)
 manifest=validate_manifest(manifest_body)
 if expected_source is not None and manifest['sourceCommit']!=expected_source:raise InputError('SOURCE_COMMIT')
 source=fetch('/git/commits/'+manifest['sourceCommit'],token)
 if not isinstance(source,dict) or source.get('sha')!=manifest['sourceCommit']:raise InputError('SOURCE_COMMIT')
 body=content_file(fetch('/contents/01GTGT-web.xml'+query,token),'01GTGT-web.xml',MAX_XML)
 if manifest['bytes']!=len(body) or manifest['xmlSha256']!=hashlib.sha256(body).hexdigest():raise InputError('HASH')
 validate_web_xml(body,today)
 return {'01GTGT-web.xml':body,'manifest.json':manifest_body}
def stage(files,runner_temp,today=None):
 if set(files)!=set(NAMES) or any(not isinstance(body,bytes) for body in files.values()):raise InputError('STAGING')
 manifest=validate_manifest(files['manifest.json'])
 if manifest['bytes']!=len(files['01GTGT-web.xml']) or manifest['xmlSha256']!=hashlib.sha256(files['01GTGT-web.xml']).hexdigest():raise InputError('HASH')
 validate_web_xml(files['01GTGT-web.xml'],today)
 parent=pathlib.Path(runner_temp);destination=parent/'htkk-web-reference-input'
 if parent.is_symlink() or not parent.is_dir() or destination.exists() or destination.is_symlink():raise InputError('STAGING')
 temporary=pathlib.Path(tempfile.mkdtemp(prefix='.htkk-web-reference-input-',dir=parent))
 try:
  for name in NAMES:
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
  files=download(token,expected_source=expected);stage(files,os.environ['RUNNER_TEMP']);manifest=validate_manifest(files['manifest.json'])
  print(json.dumps({'format':'htkk-web-reference-input-fetch-status-v1','status':'staged','bytes':manifest['bytes'],'xmlSha256':manifest['xmlSha256'],'sourceCommit':manifest['sourceCommit']},separators=(',',':')))
 except Exception as error:
  print(json.dumps(safe_failure(error),separators=(',',':')));raise SystemExit('Private synthetic web input unavailable; no XML, path, token or raw remote error published.')
if __name__=='__main__':main()
