"""One native-first harness sample; parser fixtures never constitute native evidence.

Retains both byte-exact original files privately. No XML producer, vendor process,
normalization, compatibility upgrade or secret access occurs in token-free staging.
"""
import base64,datetime,hashlib,importlib.util,json,os,pathlib,re,shutil,urllib.error
import xml.etree.ElementTree as ET

def module(name,file):
 spec=importlib.util.spec_from_file_location(name,pathlib.Path(__file__).with_name(file));value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
transport=module('sample_transport','publish-htkk-web-inputs.py')
privacy=transport.reader.privacy
annex=module('sample_schema_pins','publish-htkk-annex12-export.py')
REPO=transport.REPO;BUILDER=transport.BUILDER
DIRECTORY='htkk-native-harness-sample';BRANCH='gtgt-native-harness-sample';CONTEXT='htkk-native/harness-sample';CASE='01GTGT-native-first-zero-M10-2026'
XMLS=('01GTGT.xml','01GTGT-roundtrip.xml');NAMES=(*XMLS,'provenance.json')
PINS={**privacy.PINS,**annex.SCHEMA_PINS,'Project/FarPoint.Win.Spread.dll':'2e7a0d4fc1ef6f219dd3a237ae6b26549ad03541d58da6f45d638309d2fa4c50'}
HELPERS=('HtkkGuiReferenceAutomation.cs','HtkkGtgtExportInspection.cs','HtkkGtgtRoundtripInspection.cs','Test-HtkkNativeSampleSchema.ps1','publish-htkk-native-sample.py')
CODES=frozenset(('PROVENANCE','COMPARE','SCHEMA','FILES','STAGING','HASH','AUTH','PRIVATE_REPO','STALE_SOURCE','API_SHAPE','BUILDER'))
class SampleError(ValueError):pass
def fail(code):
 if code not in CODES:raise ValueError('Invalid safe sample code')
 raise SampleError(code)
def safe_failure(error):
 code=str(error) if isinstance(error,SampleError) and str(error) in CODES else 'XML_PRIVACY' if isinstance(error,privacy.EvidenceError) else 'INTERNAL'
 return {'format':'htkk-native-harness-sample-status-v1','status':'rejected','code':code}
def sha(value,count=40):
 if not isinstance(value,str) or not re.fullmatch('[0-9a-f]{'+str(count)+'}',value):fail('PROVENANCE')
 return value
def number(value):
 if not isinstance(value,str) or not re.fullmatch('[1-9][0-9]{0,19}',value):fail('PROVENANCE')
 return value
def helpers():return {name:hashlib.sha256(transport.safe_read(pathlib.Path(__file__).with_name(name),262144)).hexdigest() for name in HELPERS}
def describe(files):return {name:{'sha256':hashlib.sha256(files[name]).hexdigest(),'bytes':len(files[name])} for name in XMLS}
def compare(files,today=None):
 checks=[privacy.validate_xml(files[name],today) for name in XMLS]
 if checks[0]!=checks[1]:fail('COMPARE')
 def tree(node):return (node.tag,tuple(sorted(node.attrib.items())),node.text or '' if not len(node) else (node.text or '').strip(),(node.tail or '').strip(),tuple(tree(child) for child in node))
 if tree(ET.fromstring(files[XMLS[0]]))!=tree(ET.fromstring(files[XMLS[1]])):fail('COMPARE')
 # Zero-case privacy independently checks all 27 monetary leaves. Exact semantic
 # equality includes service identity, dates, order and attributes: no exclusions.
 return {'allLeavesMatched':True,'leafCount':checks[0]['leafCount'],'moneyCount':27,'normalizations':[]}
def expected(files,source,builder,run,attempt,schema):
 sha(source);sha(builder);number(run);number(attempt)
 wanted={'format':'htkk-native-sample-schema-v1','valid':True,'engine':'System.Xml.Schema/PowerShell7','schemaPins':annex.SCHEMA_PINS,'files':describe(files)}
 if type(schema) is not dict or set(schema)!=set(wanted) or any(type(schema[k]) is not type(v) or schema[k]!=v for k,v in wanted.items()):fail('SCHEMA')
 return {'format':'htkk-native-harness-sample-staging-v1','caseId':CASE,'builderRepository':BUILDER,'builderCommit':builder,'sourceRepository':REPO,'sourceCommit':source,'runId':run,'runAttempt':attempt,'sourceVersion':'5.8.1','period':'M10/2026','runtimeHost':'clr2-x86-reference','producer':'original-HTKK-controls','inputsSynthetic':True,'supplierStopped':True,'sourcesUnmodified':True,'profileCreated':True,'originalExportSucceeded':True,'originalImportSucceeded':True,'originalReexportSucceeded':True,'schema':schema,'sourcePins':PINS,'helperSha256':helpers(),'files':describe(files),'fullCompatibilityVerified':False,'filingReady':False}
def validate(files,metadata,today=None):
 if type(files) is not dict or set(files)!=set(XMLS) or any(type(v) is not bytes for v in files.values()) or type(metadata) is not dict:fail('FILES')
 wanted=expected(files,metadata.get('sourceCommit'),metadata.get('builderCommit'),metadata.get('runId'),metadata.get('runAttempt'),metadata.get('schema'))
 if set(metadata)!=set(wanted) or any(type(metadata[k]) is not type(v) or metadata[k]!=v for k,v in wanted.items()):fail('PROVENANCE')
 return compare(files,today)
def stage(installed_root,gui,supplier_stopped,sources_unmodified,schema_path,runner_temp,source,builder,run,attempt,today=None):
 if supplier_stopped is not True or sources_unmodified is not True or type(gui) is not dict:fail('PROVENANCE')
 flags=('sourcePinsVerified','originalSaveInvoked','savedHeaderExists','savedHeaderChecksMatched','profileClosed','mainMenuObserved','periodYearMonthMatched','periodFirstDeclarationMatched','periodNoAnnexMatched','periodConfirmInvoked','gtgtWorkbookPinsVerified','gtgtIdentityMatched','gtgtMonetaryZero','exportSchemaPinnedVerified','exportOriginalPathMatched','exportCommandInvoked','exportSelectorMatched','exportButtonInvoked','exportDialogMatched','exportDestinationFresh','exportDialogSubmitted','exportFilenameKeyboardCommitted','exportFileExists','exportXmlRootMatched','exportSyntheticIdentityMatched','exportSuccessAcknowledged','roundtripImportCommandInvoked','roundtripImportDialogMatched','roundtripImportKeyboardCommitted','roundtripImportDialogSubmitted','roundtripImportPathMatched','roundtripImportSheetMatched','roundtripImportSucceeded','roundtripReexportCommandInvoked','roundtripReexportSucceeded','roundtripXmlExactMatched')
 if any(gui.get(key) is not True for key in flags):fail('PROVENANCE')
 if gui.get('status')!='matched' or gui.get('mode')!='gtgt-roundtrip-inspect' or gui.get('stage')!='gtgt-roundtrip-inspected' or gui.get('failureCategory')!='none' or gui.get('realTaxpayerDataUsed') is not False or gui.get('webInputVerified') is not False or type(gui.get('roundtripImportCheckedMoneyCount')) is not int or gui['roundtripImportCheckedMoneyCount']!=27:fail('PROVENANCE')
 root=pathlib.Path(installed_root);temporary=pathlib.Path(runner_temp)
 if not root.is_absolute() or not temporary.is_absolute() or not root.is_dir() or not temporary.is_dir() or transport.unsafe_path(root) or transport.unsafe_path(temporary):fail('STAGING')
 for name,pin in PINS.items():
  if hashlib.sha256(transport.safe_read(root/name,41943040)).hexdigest()!=pin:fail('HASH')
 files={name:transport.safe_read(root/'DataFiles/9999999997/reference-output'/name,262144) for name in XMLS}
 for name,sizekey,hashkey in ((XMLS[0],'exportBytes','exportSha256'),(XMLS[1],'roundtripReexportBytes','roundtripReexportSha256')):
  if type(gui.get(sizekey)) is not int or len(files[name])!=gui[sizekey] or hashlib.sha256(files[name]).hexdigest()!=gui.get(hashkey):fail('HASH')
 schema=transport.reader.json_object(transport.safe_read(pathlib.Path(schema_path),16384),'MANIFEST')
 metadata=expected(files,source,builder,run,attempt,schema);validate(files,metadata,today)
 destination=temporary/DIRECTORY
 if destination.exists() or transport.unsafe_path(destination):fail('STAGING')
 destination.mkdir()
 try:
  for name,body in {**files,'provenance.json':(json.dumps(metadata,sort_keys=True,separators=(',',':'))+'\n').encode()}.items():
   with (destination/name).open('xb') as stream:stream.write(body)
  read(destination,source,builder,run,attempt,today)
 except Exception:shutil.rmtree(destination,ignore_errors=True);raise
 return {'format':'htkk-native-harness-sample-status-v1','status':'staged','rawBytesPreserved':True,'independentSchemaVerification':True,'fullCompatibilityVerified':False}
def read(directory,source,builder,run,attempt,today=None):
 directory=pathlib.Path(directory)
 if transport.unsafe_path(directory) or not directory.is_dir() or set(p.name for p in directory.iterdir())!=set(NAMES):fail('FILES')
 files={name:transport.safe_read(directory/name,262144) for name in XMLS};metadata=transport.reader.json_object(transport.safe_read(directory/'provenance.json',16384),'MANIFEST')
 if any(metadata.get(k)!=v for k,v in (('sourceCommit',source),('builderCommit',builder),('runId',run),('runAttempt',attempt))):fail('PROVENANCE')
 validate(files,metadata,today);return files,metadata

def publish(files,metadata,token,fetch=None,today=None):
 comparison=validate(files,metadata,today)
 if not isinstance(token,str) or not token:fail('AUTH')
 fetch=fetch or transport.api
 info=fetch('',token)
 if type(info) is not dict or info.get('private') is not True or info.get('full_name')!=REPO:fail('PRIVATE_REPO')
 def current():
  head=fetch('/git/ref/heads/main',token)
  if type(head) is not dict or head.get('ref')!='refs/heads/main' or head.get('object',{}).get('type')!='commit' or head.get('object',{}).get('sha')!=metadata['sourceCommit']:fail('STALE_SOURCE')
 current()
 manifest={'format':'htkk-native-harness-sample-reference-v1','provenance':metadata,'comparison':comparison,'scope':'one-fixed-original-native-first-zero-roundtrip','fullCompatibilityVerified':False,'filingReady':False}
 published={**files,'manifest.json':(json.dumps(manifest,sort_keys=True,separators=(',',':'))+'\n').encode()};entries=[]
 for name,body in published.items():
  digest=hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest();blob=fetch('/git/blobs',token,{'content':base64.b64encode(body).decode(),'encoding':'base64'})
  if type(blob) is not dict or blob.get('sha')!=digest:fail('HASH')
  entries.append({'path':name,'mode':'100644','type':'blob','sha':digest})
 tree=fetch('/git/trees',token,{'tree':entries});tree_sha=sha(tree.get('sha'))
 artifact=sha(fetch('/git/commits',token,{'message':'Private native-first harness sample '+metadata['builderCommit'],'tree':tree_sha,'parents':[]}).get('sha'))
 current();missing=False
 try:old=fetch('/git/ref/heads/'+BRANCH,token)
 except urllib.error.HTTPError as error:
  if error.code!=404:raise
  missing=True
 if missing:updated=fetch('/git/refs',token,{'ref':'refs/heads/'+BRANCH,'sha':artifact})
 else:
  if type(old) is not dict or old.get('ref')!='refs/heads/'+BRANCH or old.get('object',{}).get('type')!='commit':fail('API_SHAPE')
  sha(old['object'].get('sha'));updated=fetch('/git/refs/heads/'+BRANCH,token,{'sha':artifact,'force':True},'PATCH')
 if type(updated) is not dict or updated.get('ref')!='refs/heads/'+BRANCH or updated.get('object',{}).get('sha')!=artifact or updated.get('object',{}).get('type')!='commit':fail('API_SHAPE')
 # Re-read the immutable commit and every blob before reporting success.
 commit=fetch('/git/commits/'+artifact,token)
 if type(commit) is not dict or commit.get('sha')!=artifact or commit.get('tree',{}).get('sha')!=tree_sha:fail('HASH')
 for entry in entries:
  blob=fetch('/git/blobs/'+entry['sha'],token)
  try:raw=base64.b64decode(re.sub(r'[\r\n]','',blob['content']),validate=True)
  except Exception:fail('HASH')
  if blob.get('encoding')!='base64' or raw!=published[entry['path']]:fail('HASH')
 current()
 fetch('/statuses/'+metadata['sourceCommit'],token,{'state':'success','context':CONTEXT,'description':'Fixed native-first sample retained; full compatibility remains false','target_url':'https://github.com/'+BUILDER+'/actions/runs/'+metadata['runId']+'/attempts/'+metadata['runAttempt']})
 return {'format':'htkk-native-harness-sample-status-v1','status':'published','caseId':CASE,'artifactCommit':artifact,'fullCompatibilityVerified':False}
def main():
 directory=pathlib.Path(os.environ.get('RUNNER_TEMP',''))/DIRECTORY
 try:
  if os.environ.get('GITHUB_REPOSITORY')!=BUILDER:fail('BUILDER')
  files,metadata=read(directory,os.environ.get('EXPECTED_WEB_SOURCE_SHA'),os.environ.get('GITHUB_SHA'),os.environ.get('GITHUB_RUN_ID'),os.environ.get('GITHUB_RUN_ATTEMPT'))
  result=publish(files,metadata,os.environ.get('SOURCE_PUBLISH_TOKEN'));print(json.dumps(result,separators=(',',':')))
 except Exception as error:
  print(json.dumps(safe_failure(error),separators=(',',':')));raise SystemExit('Native harness sample rejected; no source XML, paths or raw errors logged.')
 finally:
  if not transport.unsafe_path(directory):shutil.rmtree(directory,ignore_errors=True)
if __name__=='__main__':main()
