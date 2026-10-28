"""Retain one fixed original 01-2/GTGT export privately after supplier shutdown.

Separate from the thirteen web/native cases. Original XML bytes are immutable;
this publisher never executes HTKK, validates XSD, or claims an import roundtrip.
"""
import base64,hashlib,importlib.util,json,os,pathlib,re,shutil,urllib.error

def module(name,file):
 spec=importlib.util.spec_from_file_location(name,pathlib.Path(__file__).with_name(file));value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
contract=module('annex12_export_contract','htkk_annex12_fixed_export.py')
transport=module('annex12_export_transport','publish-htkk-web-inputs.py')
REPO='htkk-net/htkk_web';BUILDER='congminh1254/htkk_builder'
DIRECTORY='htkk-annex12-export-output';BRANCH='gtgt-annex12-zero-two-locations-native-export'
NAMES=('01GTGT-annex12-native.xml','provenance.json')
SCHEMA_PINS={'InterfaceTemplates/Validate/01_GTGT_TT80_283.xsd':'8d4c0d88100e858ddfe221d080a6a338776d1364c7de04347bfb990d04833003','InterfaceTemplates/TKhaiThue.xsd':'8f451719355b5a6247f65a34a37584b4a0c7f7cc81a568e1033d08b8fe9b8c1d','InterfaceTemplates/xmldsig-core-schema.xsd':'c3b5160be1852606d10f6928e0b214d418f8dd418667cb2fb88fec31e4e6f56d'}
PINS={**contract.privacy.PINS,**contract.SOURCE_PINS,**SCHEMA_PINS,'Project/FarPoint.Win.Spread.dll':'2e7a0d4fc1ef6f219dd3a237ae6b26549ad03541d58da6f45d638309d2fa4c50'}
HELPERS=('HtkkGtgtPeriodAndSheet.cs','HtkkGtgtAnnex12ExportInspection.cs')
CODES=transport.CODES|frozenset(('PROVENANCE','FILES','XML_CONTRACT','HASH'))
class AnnexPublicationError(ValueError):
 def __init__(self,code):
  if code not in CODES:raise ValueError('Invalid bounded annex publication code')
  self.code=code;super().__init__(code)
def fail(code):raise AnnexPublicationError(code)
def safe_failure(error):
 if isinstance(error,AnnexPublicationError):code=error.code if error.code in CODES else 'INTERNAL'
 elif isinstance(error,contract.AnnexContractError):code='XML_CONTRACT'
 else:code=transport.safe_failure(error)['code']
 return {'format':'htkk-annex12-export-publication-status-v1','status':'rejected','code':code}
def identifier(value,length=40):
 if not isinstance(value,str) or not re.fullmatch('[0-9a-f]{'+str(length)+'}',value):fail('PROVENANCE')
 return value
def run_number(value):
 if not isinstance(value,str) or not re.fullmatch('[1-9][0-9]{0,19}',value):fail('PROVENANCE')
 return value
def helper_pins():
 return {name:hashlib.sha256(transport.safe_read(pathlib.Path(__file__).with_name(name),262144)).hexdigest() for name in HELPERS}
def validate_provenance(body,native,run_id,builder_sha,run_attempt):
 identifier(builder_sha);run_number(run_id);run_number(run_attempt)
 if not isinstance(body,bytes) or not 0<len(body)<=16384:fail('PROVENANCE')
 metadata=transport.reader.json_object(body,'MANIFEST')
 expected={'format':'htkk-annex12-export-staging-v1','builderRepository':BUILDER,'builderCommit':builder_sha,'runId':run_id,'runAttempt':run_attempt,'sourceVersion':'5.8.1','runtimeHost':'clr2-x86-reference','caseId':contract.CASE_ID,'inputsSynthetic':True,'originalProcessStopped':True,'originalSourcesUnmodified':True,'originalExportSucceeded':True,'originalExporterValidatedSchema':True,'independentSchemaVerification':True,'independentSchemaEngine':'System.Xml.Schema/.NET2-x86','fixedInputCount':14,'groupCount':1,'childRowCount':2,'checkedMainMoneyCount':27,'observedTotalLeafCount':112,'inputHelperSha256':helper_pins(),'sourcePins':PINS,'originalOutputSha256':hashlib.sha256(native).hexdigest(),'originalOutputBytes':len(native),'nativeAnnexRoundTripVerified':False,'fullCompatibilityVerified':False}
 if set(metadata)!=set(expected) or any(type(metadata[key]) is not type(value) or metadata[key]!=value for key,value in expected.items()):fail('PROVENANCE')
 return metadata
def read_evidence(directory,run_id,builder_sha,run_attempt,today=None):
 directory=pathlib.Path(directory)
 if transport.unsafe_path(directory) or not directory.is_dir() or set(p.name for p in directory.iterdir())!=set(NAMES):fail('FILES')
 native=transport.safe_read(directory/NAMES[0],262144);provenance=transport.safe_read(directory/NAMES[1],16384)
 metadata=validate_provenance(provenance,native,run_id,builder_sha,run_attempt);contract.validate_candidate(native,today)
 return native,metadata
def publish(native,metadata,token,fetch=None,today=None):
 metadata=validate_provenance(json.dumps(metadata).encode(),native,metadata.get('runId'),metadata.get('builderCommit'),metadata.get('runAttempt'));checked=contract.validate_candidate(native,today)
 if not isinstance(token,str) or not token:fail('AUTH')
 fetch=fetch or transport.api;info=fetch('',token)
 if not isinstance(info,dict) or info.get('private') is not True or info.get('full_name')!=REPO:fail('PRIVATE_REPO')
 manifest={'format':'htkk-annex12-native-export-reference-v1','scope':'one-fixed-synthetic-original-annex-export','provenance':metadata,'sourcePins':PINS,'privacyCheck':checked,'files':{NAMES[0]:{'sha256':metadata['originalOutputSha256'],'bytes':len(native)}},'originalAnnexExportVerified':True,'independentSchemaVerification':True,'independentSchemaEngine':'System.Xml.Schema/.NET2-x86','browserSchemaVerification':False,'nativeAnnexRoundTripVerified':False,'fullCompatibilityVerified':False}
 manifest_bytes=(json.dumps(manifest,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode()
 if len(manifest_bytes)>16384:fail('MANIFEST')
 entries=[]
 for name,body in ((NAMES[0],native),('manifest.json',manifest_bytes)):
  expected=hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest();blob=fetch('/git/blobs',token,{'content':base64.b64encode(body).decode('ascii'),'encoding':'base64'})
  if not isinstance(blob,dict) or blob.get('sha')!=expected:fail('HASH')
  entries.append({'path':name,'mode':'100644','type':'blob','sha':expected})
 tree=fetch('/git/trees',token,{'tree':entries})
 if not isinstance(tree,dict):fail('API_SHAPE')
 tree_sha=identifier(tree.get('sha'));commit=fetch('/git/commits',token,{'message':'Private original fixed 01-2 GTGT export '+metadata['builderCommit'],'tree':tree_sha,'parents':[]})
 if not isinstance(commit,dict):fail('API_SHAPE')
 artifact=identifier(commit.get('sha'));missing=False
 try:existing=fetch('/git/ref/heads/'+BRANCH,token)
 except urllib.error.HTTPError as error:
  if error.code!=404:raise
  missing=True
 if missing:updated=fetch('/git/refs',token,{'ref':'refs/heads/'+BRANCH,'sha':artifact})
 else:
  if not isinstance(existing,dict) or existing.get('ref')!='refs/heads/'+BRANCH or not isinstance(existing.get('object'),dict) or existing['object'].get('type')!='commit':fail('API_SHAPE')
  identifier(existing['object'].get('sha'));updated=fetch('/git/refs/heads/'+BRANCH,token,{'sha':artifact,'force':True},'PATCH')
 if not isinstance(updated,dict) or updated.get('ref')!='refs/heads/'+BRANCH or not isinstance(updated.get('object'),dict) or updated['object'].get('type')!='commit' or updated['object'].get('sha')!=artifact:fail('API_SHAPE')
 return {'format':'htkk-annex12-export-publication-status-v1','status':'published','caseId':contract.CASE_ID,'artifactCommit':artifact,'nativeOutputSha256':metadata['originalOutputSha256'],'bytes':len(native),'nativeAnnexRoundTripVerified':False,'fullCompatibilityVerified':False}
def stage_original(installed_root,gui,supplier_stopped,sources_unmodified,runner_temp,run_id,builder_sha,run_attempt,today=None):
 # This function runs in the token-free native step, after confirmed shutdown.
 if supplier_stopped is not True or sources_unmodified is not True or not isinstance(gui,dict):fail('PROVENANCE')
 identifier(builder_sha);run_number(run_id);run_number(run_attempt)
 flags=('sourcePinsVerified','periodAnnex12Matched','annex12SourcePinsMatched','annex12RowAfterMatched','annex12InputReadOnlyIdentityMatched','annex12InputIdentityMatched','annex12InputTypesMatched','annex12InputGeographyMatched','annex12InputTaxAuthoritiesMatched','annex12InputPercentagesMatched','annex12InputZeroTaxMatched','annex12ExportMainZeroMatched','annex12ExportShapeMatched','annex12ExportSchemaVerified','exportSchemaPinnedVerified','exportCommandInvoked','exportSelectorMatched','exportButtonInvoked','exportDialogMatched','exportDestinationFresh','exportFilenameKeyboardCommitted','exportDialogSubmitted','exportFileExists','exportXmlRootMatched','exportSyntheticIdentityMatched','exportSuccessAcknowledged','exportOriginalPathMatched')
 if any(gui.get(key) is not True for key in flags):fail('PROVENANCE')
 if gui.get('status')!='matched' or gui.get('mode')!='gtgt-annex12-export-inspect' or gui.get('stage')!='gtgt-annex12-export-inspected' or gui.get('failureCategory')!='none' or gui.get('webInputVerified') is not False or gui.get('realTaxpayerDataUsed') is not False or gui.get('runtimeRoundTrip') is not False:fail('PROVENANCE')
 for key,expected in (('annexSelectedCount',1),('annex12InputActionCount',14),('annex12GroupCount',1),('annex12RowAfterGroupRows',2),('annex12RowAfterRows',67),('gtgtCaseMoneyCount',27),('gtgtCaseMismatchMask',0),('gtgtCaseNonzeroMask',0)):
  if type(gui.get(key)) is not int or gui[key]!=expected:fail('PROVENANCE')
 output_sha=identifier(gui.get('exportSha256'),64);output_bytes=gui.get('exportBytes')
 if type(output_bytes) is not int or not 0<output_bytes<=262144:fail('PROVENANCE')
 installed_root=pathlib.Path(installed_root);temporary=pathlib.Path(runner_temp)
 if not installed_root.is_absolute() or not temporary.is_absolute() or not installed_root.is_dir() or not temporary.is_dir() or transport.unsafe_path(installed_root) or transport.unsafe_path(temporary):fail('STAGING')
 for name,expected in PINS.items():
  if hashlib.sha256(transport.safe_read(installed_root/name,41943040)).hexdigest()!=expected:fail('HASH')
 original=installed_root/'DataFiles/9999999997/reference-annex12-output/01GTGT.xml';native=transport.safe_read(original,262144)
 if len(native)!=output_bytes or hashlib.sha256(native).hexdigest()!=output_sha:fail('HASH')
 contract.validate_candidate(native,today)
 metadata={'format':'htkk-annex12-export-staging-v1','builderRepository':BUILDER,'builderCommit':builder_sha,'runId':run_id,'runAttempt':run_attempt,'sourceVersion':'5.8.1','runtimeHost':'clr2-x86-reference','caseId':contract.CASE_ID,'inputsSynthetic':True,'originalProcessStopped':True,'originalSourcesUnmodified':True,'originalExportSucceeded':True,'originalExporterValidatedSchema':True,'independentSchemaVerification':True,'independentSchemaEngine':'System.Xml.Schema/.NET2-x86','fixedInputCount':14,'groupCount':1,'childRowCount':2,'checkedMainMoneyCount':27,'observedTotalLeafCount':112,'inputHelperSha256':helper_pins(),'sourcePins':PINS,'originalOutputSha256':output_sha,'originalOutputBytes':output_bytes,'nativeAnnexRoundTripVerified':False,'fullCompatibilityVerified':False}
 provenance=(json.dumps(metadata,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode();validate_provenance(provenance,native,run_id,builder_sha,run_attempt)
 destination=temporary/DIRECTORY
 if destination.exists() or transport.unsafe_path(destination):fail('STAGING')
 destination.mkdir()
 try:
  with (destination/NAMES[0]).open('xb') as stream:stream.write(native)
  with (destination/NAMES[1]).open('xb') as stream:stream.write(provenance)
  staged,checked=read_evidence(destination,run_id,builder_sha,run_attempt,today)
  if staged!=native or transport.safe_read(original,262144)!=native:fail('HASH')
 except Exception:
  if not transport.unsafe_path(destination):shutil.rmtree(destination,ignore_errors=True)
  raise
 return {'format':'htkk-annex12-export-staging-status-v1','status':'staged','caseId':contract.CASE_ID,'rawBytesPreserved':True,'independentSchemaVerification':True,'nativeAnnexRoundTripVerified':False,'fullCompatibilityVerified':False}

def main():
 directory=pathlib.Path(os.environ.get('RUNNER_TEMP',''))/DIRECTORY
 try:
  if os.environ.get('GITHUB_REPOSITORY')!=BUILDER:fail('BUILDER')
  token=os.environ.get('SOURCE_PUBLISH_TOKEN') or os.environ.get('SOURCE_READ_TOKEN')
  if not token:fail('AUTH')
  native,metadata=read_evidence(directory,os.environ.get('GITHUB_RUN_ID'),os.environ.get('GITHUB_SHA'),os.environ.get('GITHUB_RUN_ATTEMPT'))
  print(json.dumps(publish(native,metadata,token),separators=(',',':')))
 except Exception as error:
  print(json.dumps(safe_failure(error),separators=(',',':')));raise SystemExit('Fixed annex export retention rejected; no raw XML, paths, credentials or remote error published.')
 finally:
  if os.environ.get('RUNNER_TEMP') and directory.name==DIRECTORY and not transport.unsafe_path(directory):shutil.rmtree(directory,ignore_errors=True)
if __name__=='__main__':main()
