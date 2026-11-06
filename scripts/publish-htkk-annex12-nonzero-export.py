"""Retain two ORIGINAL nonzero 01-2/GTGT exports privately after supplier shutdown.

Separate probe for comparing the web engine's predictions; it is not one of the
web/native cases and never claims import/roundtrip or filing compatibility.
Snapshot A is parent 1 at 50/50, snapshot B parent 7 at 33.33/66.67. Every
original XML byte is retained unchanged; amounts calculated by HTKK are only
bounded-shape checked (synthetic, at most the fixed parent), never normalized.
"""
import base64,copy,hashlib,importlib.util,json,os,pathlib,re,shutil,urllib.error
import xml.etree.ElementTree as ET

def module(name,file):
 spec=importlib.util.spec_from_file_location(name,pathlib.Path(__file__).with_name(file));value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
fixed=module('annex12_nonzero_fixed_contract','htkk_annex12_fixed_export.py')
cases=module('annex12_nonzero_case_contract','htkk_annex12_web_cases.py')
transport=module('annex12_nonzero_transport','publish-htkk-web-inputs.py')
privacy=fixed.privacy
REPO='htkk-net/htkk_web';BUILDER='congminh1254/htkk_builder'
PROBE_ID='01GTGT-annex12-nonzero-native-export-M10-2026'
DIRECTORY='htkk-annex12-nonzero-export-output';BRANCH='gtgt-annex12-nonzero-native-export'
# Retained name -> original export name in the fresh native directory.
SNAPSHOTS={'01GTGT-annex12-p1-50.xml':'01GTGT.xml','01GTGT-annex12-p7-3333.xml':'01GTGT-p7.xml'}
NAMES=tuple(SNAPSHOTS)+('provenance.json',)
ORIGINAL_DIRECTORY='DataFiles/9999999997/reference-annex12-nonzero-output'
SCHEMA_PINS={'InterfaceTemplates/Validate/01_GTGT_TT80_283.xsd':'8d4c0d88100e858ddfe221d080a6a338776d1364c7de04347bfb990d04833003','InterfaceTemplates/TKhaiThue.xsd':'8f451719355b5a6247f65a34a37584b4a0c7f7cc81a568e1033d08b8fe9b8c1d','InterfaceTemplates/xmldsig-core-schema.xsd':'c3b5160be1852606d10f6928e0b214d418f8dd418667cb2fb88fec31e4e6f56d'}
PINS={**privacy.PINS,**fixed.SOURCE_PINS,**SCHEMA_PINS,'Project/FarPoint.Win.Spread.dll':'2e7a0d4fc1ef6f219dd3a237ae6b26549ad03541d58da6f45d638309d2fa4c50'}
HELPERS=('HtkkGtgtPeriodAndSheet.cs','HtkkGtgtAnnex12NumericInspection.cs','HtkkGtgtAnnex12ExportInspection.cs','HtkkGtgtExportInspection.cs')
CODES=transport.CODES|frozenset(('PROVENANCE','FILES','XML_CONTRACT','HASH'))
class NonzeroPublicationError(ValueError):
 def __init__(self,code):
  if code not in CODES:raise ValueError('Invalid bounded nonzero annex publication code')
  self.code=code;super().__init__(code)
def fail(code):raise NonzeroPublicationError(code)
def safe_failure(error):
 if isinstance(error,NonzeroPublicationError):code=error.code if error.code in CODES else 'INTERNAL'
 elif isinstance(error,(cases.AnnexWebContractError,fixed.AnnexContractError)):code='XML_CONTRACT'
 else:code=transport.safe_failure(error)['code']
 return {'format':'htkk-annex12-nonzero-export-publication-status-v1','status':'rejected','code':code}
def contract_diagnostic(error):
 if isinstance(error,cases.AnnexWebContractError):return {'contractCode':error.code,'contractFieldId':error.fieldId}
 if isinstance(error,fixed.AnnexContractError):return {'contractCode':error.code,'contractFieldId':0}
 return {}

def exact(pattern):return lambda text:re.fullmatch(pattern,text) is not None
def snapshot_plant(parent,percentages):
 rows=[{'id':'ID_'+str(index+1),'values':{'sTT':'1.'+str(index+1),'loai':kind,**cases.FIXED_LOCATION,'ct10':cases.bounded_decimal(parent),'ct11':exact(percentage),'ct12':cases.bounded_decimal(parent)}} for index,(kind,percentage) in enumerate((('01',percentages[0]),('02',percentages[1])))]
 return [{'id':'ID_1','values':{'sTT':'1','ten_nhaMay':cases.PLANT_NAMES[0],'ma_nhaMay':cases.PLANT_CODES[0]},'totals':{'ct10_a':exact(str(parent)+r'(?:\.0{1,8})?'),'ct11_a':exact(r'100(?:\.0{1,8})?'),'ct12_a':cases.bounded_decimal(parent)},'rows':rows}]
# Inputs are exact; outputs HTKK calculates may be any bounded synthetic decimal.
VARIANTS={
 '01GTGT-annex12-p1-50.xml':{'parent':1,'plants':snapshot_plant(1,(r'50(?:\.0{1,8})?',r'50(?:\.0{1,8})?'))},
 '01GTGT-annex12-p7-3333.xml':{'parent':7,'plants':snapshot_plant(7,(r'33\.33(?:0{1,6})?',r'66\.67(?:0{1,6})?'))},
}
def validate_snapshot(body,name,today=None):
 if name not in VARIANTS:fail('PROVENANCE')
 spec=VARIANTS[name];root=fixed.parse(body)
 if not isinstance(root.tag,str) or root.tag!='{'+cases.NS+'}HSoThueDTu':raise cases.AnnexWebContractError('STRUCTURE','pluc')
 ns='{'+cases.NS+'}';plucs=root.findall('./'+ns+'HSoKhaiThue/'+ns+'PLuc')
 if len(plucs)!=1:raise cases.AnnexWebContractError('STRUCTURE','pluc')
 cases.container(plucs[0],('PLuc_01_2_GTGT',),{},'pluc')
 cases.validate_groups(plucs[0][0],spec['plants'],(cases.bounded_decimal(spec['parent']),cases.bounded_decimal(spec['parent'])))
 leaves=sum(1 for node in root.iter() if len(node)==0)
 if leaves!=112:raise cases.AnnexWebContractError('LEAF_COUNT','pluc')
 # Main declaration stays the fixed fake profile with 27 zeros; projection is in memory only.
 projected=cases.strip_annex(copy.deepcopy(root))
 ET.register_namespace('',privacy.NS);ET.register_namespace('xsi',privacy.XSI)
 try:base=privacy.validate_xml(ET.tostring(projected,encoding='utf-8'),today)
 except privacy.EvidenceError:raise cases.AnnexWebContractError('BASE_PRIVACY','base') from None
 if base['leafCount']!=74:raise cases.AnnexWebContractError('LEAF_COUNT','base')
 return {'snapshot':name,'sha256':hashlib.sha256(body).hexdigest(),'bytes':len(body),'fixedSyntheticInputsVerified':True,'calculatedAmountsBoundedOnly':True,'totalLeafCount':112,'originalAnnexExportVerified':False,'nativeAnnexRoundTripVerified':False,'fullCompatibilityVerified':False}

def identifier(value,length=40):
 if not isinstance(value,str) or not re.fullmatch('[0-9a-f]{'+str(length)+'}',value):fail('PROVENANCE')
 return value
def run_number(value):
 if not isinstance(value,str) or not re.fullmatch('[1-9][0-9]{0,19}',value):fail('PROVENANCE')
 return value
def helper_pins():
 return {name:hashlib.sha256(transport.safe_read(pathlib.Path(__file__).with_name(name),262144)).hexdigest() for name in HELPERS}
def expected_provenance(bodies,run_id,builder_sha,run_attempt):
 return {'format':'htkk-annex12-nonzero-export-staging-v1','builderRepository':BUILDER,'builderCommit':builder_sha,'runId':run_id,'runAttempt':run_attempt,'sourceVersion':'5.8.1','runtimeHost':'clr2-x86-reference','probeId':PROBE_ID,'inputsSynthetic':True,'originalProcessStopped':True,'originalSourcesUnmodified':True,'originalExportSucceeded':True,'originalExporterValidatedSchema':True,'independentSchemaVerification':True,'independentSchemaEngine':'System.Xml.Schema/.NET2-x86','fixedInputCount':14,'numericEditCount':4,'exportCount':2,'groupCount':1,'childRowCount':2,'checkedMainMoneyCount':27,'observedTotalLeafCount':112,'snapshots':{'01GTGT-annex12-p1-50.xml':{'parentTax':'1','percentages':['50','50'],'sha256':hashlib.sha256(bodies['01GTGT-annex12-p1-50.xml']).hexdigest(),'bytes':len(bodies['01GTGT-annex12-p1-50.xml'])},'01GTGT-annex12-p7-3333.xml':{'parentTax':'7','percentages':['33.33','66.67'],'sha256':hashlib.sha256(bodies['01GTGT-annex12-p7-3333.xml']).hexdigest(),'bytes':len(bodies['01GTGT-annex12-p7-3333.xml'])}},'inputHelperSha256':helper_pins(),'sourcePins':PINS,'nativeAnnexRoundTripVerified':False,'fullCompatibilityVerified':False}
def validate_provenance(body,bodies,run_id,builder_sha,run_attempt):
 identifier(builder_sha);run_number(run_id);run_number(run_attempt)
 if not isinstance(body,bytes) or not 0<len(body)<=16384 or set(bodies)!=set(SNAPSHOTS):fail('PROVENANCE')
 metadata=transport.reader.json_object(body,'MANIFEST');expected=expected_provenance(bodies,run_id,builder_sha,run_attempt)
 if set(metadata)!=set(expected) or any(type(metadata[key]) is not type(value) or metadata[key]!=value for key,value in expected.items()):fail('PROVENANCE')
 if bodies['01GTGT-annex12-p1-50.xml']==bodies['01GTGT-annex12-p7-3333.xml']:fail('HASH')
 return metadata
def read_evidence(directory,run_id,builder_sha,run_attempt,today=None):
 directory=pathlib.Path(directory)
 if transport.unsafe_path(directory) or not directory.is_dir() or set(p.name for p in directory.iterdir())!=set(NAMES):fail('FILES')
 bodies={name:transport.safe_read(directory/name,262144) for name in SNAPSHOTS};provenance=transport.safe_read(directory/'provenance.json',16384)
 metadata=validate_provenance(provenance,bodies,run_id,builder_sha,run_attempt)
 checks={name:validate_snapshot(body,name,today) for name,body in bodies.items()}
 return bodies,metadata,checks

def publish(bodies,metadata,token,fetch=None,today=None):
 metadata=validate_provenance(json.dumps(metadata).encode(),bodies,metadata.get('runId'),metadata.get('builderCommit'),metadata.get('runAttempt'))
 checks={name:validate_snapshot(body,name,today) for name,body in bodies.items()}
 if not isinstance(token,str) or not token:fail('AUTH')
 fetch=fetch or transport.api;info=fetch('',token)
 if not isinstance(info,dict) or info.get('private') is not True or info.get('full_name')!=REPO:fail('PRIVATE_REPO')
 manifest={'format':'htkk-annex12-nonzero-native-export-reference-v1','scope':'two-fixed-synthetic-original-nonzero-annex-exports','provenance':metadata,'sourcePins':PINS,'privacyCheck':checks,'files':{name:{'sha256':hashlib.sha256(body).hexdigest(),'bytes':len(body)} for name,body in bodies.items()},'originalAnnexExportVerified':True,'independentSchemaVerification':True,'independentSchemaEngine':'System.Xml.Schema/.NET2-x86','browserSchemaVerification':False,'webEnginePredictionCompared':False,'nativeAnnexRoundTripVerified':False,'fullCompatibilityVerified':False}
 manifest_bytes=(json.dumps(manifest,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode()
 if len(manifest_bytes)>16384:fail('MANIFEST')
 entries=[]
 for name,body in (*bodies.items(),('manifest.json',manifest_bytes)):
  expected=hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest();blob=fetch('/git/blobs',token,{'content':base64.b64encode(body).decode('ascii'),'encoding':'base64'})
  if not isinstance(blob,dict) or blob.get('sha')!=expected:fail('HASH')
  entries.append({'path':name,'mode':'100644','type':'blob','sha':expected})
 tree=fetch('/git/trees',token,{'tree':entries})
 if not isinstance(tree,dict):fail('API_SHAPE')
 tree_sha=identifier(tree.get('sha'));commit=fetch('/git/commits',token,{'message':'Private original nonzero 01-2 GTGT exports '+metadata['builderCommit'],'tree':tree_sha,'parents':[]})
 if not isinstance(commit,dict):fail('API_SHAPE')
 artifact=identifier(commit.get('sha'));missing=False
 # Only an explicit GET 404 permits creation; a failed PATCH never falls back.
 try:existing=fetch('/git/ref/heads/'+BRANCH,token)
 except urllib.error.HTTPError as error:
  if error.code!=404:raise
  missing=True
 if missing:updated=fetch('/git/refs',token,{'ref':'refs/heads/'+BRANCH,'sha':artifact})
 else:
  if not isinstance(existing,dict) or existing.get('ref')!='refs/heads/'+BRANCH or not isinstance(existing.get('object'),dict) or existing['object'].get('type')!='commit':fail('API_SHAPE')
  identifier(existing['object'].get('sha'));updated=fetch('/git/refs/heads/'+BRANCH,token,{'sha':artifact,'force':True},'PATCH')
 if not isinstance(updated,dict) or updated.get('ref')!='refs/heads/'+BRANCH or not isinstance(updated.get('object'),dict) or updated['object'].get('type')!='commit' or updated['object'].get('sha')!=artifact:fail('API_SHAPE')
 return {'format':'htkk-annex12-nonzero-export-publication-status-v1','status':'published','probeId':PROBE_ID,'artifactCommit':artifact,'snapshotCount':2,'nativeAnnexRoundTripVerified':False,'fullCompatibilityVerified':False}

GUI_FLAGS=('sourcePinsVerified','periodAnnex12Matched','annex12SourcePinsMatched','annex12RowAfterMatched','annex12InputReadOnlyIdentityMatched','annex12InputIdentityMatched','annex12InputTypesMatched','annex12InputGeographyMatched','annex12InputTaxAuthoritiesMatched','annex12InputPercentagesMatched','annex12InputZeroTaxMatched','annex12ExportMainZeroMatched','annex12ExportShapeMatched','annex12ExportSchemaVerified','annex12NonzeroEditsMatched','annex12NonzeroSecondShapeMatched','annex12NonzeroSecondSchemaVerified','exportSchemaPinnedVerified','exportCommandInvoked','exportSelectorMatched','exportButtonInvoked','exportDialogMatched','exportDestinationFresh','exportFilenameKeyboardCommitted','exportDialogSubmitted','exportFileExists','exportXmlRootMatched','exportSyntheticIdentityMatched','exportSuccessAcknowledged','exportOriginalPathMatched')
def stage_original(installed_root,gui,supplier_stopped,sources_unmodified,runner_temp,run_id,builder_sha,run_attempt,today=None):
 # Token-free native step, after confirmed shutdown and source re-hash.
 if supplier_stopped is not True or sources_unmodified is not True or not isinstance(gui,dict):fail('PROVENANCE')
 identifier(builder_sha);run_number(run_id);run_number(run_attempt)
 if any(gui.get(key) is not True for key in GUI_FLAGS):fail('PROVENANCE')
 if gui.get('status')!='matched' or gui.get('mode')!='gtgt-annex12-export-nonzero' or gui.get('stage')!='gtgt-annex12-export-nonzero-inspected' or gui.get('failureCategory')!='none' or gui.get('webInputVerified') is not False or gui.get('roundtripImportCommandInvoked') is not False or gui.get('realTaxpayerDataUsed') is not False or gui.get('runtimeRoundTrip') is not False:fail('PROVENANCE')
 for key,expected in (('annexSelectedCount',1),('annex12InputActionCount',14),('annex12NumericActionCount',4),('annex12NonzeroExportCount',2),('annex12GroupCount',1),('annex12RowAfterGroupRows',2),('annex12RowAfterRows',67),('gtgtCaseMoneyCount',27),('gtgtCaseMismatchMask',0),('gtgtCaseNonzeroMask',0)):
  if type(gui.get(key)) is not int or gui[key]!=expected:fail('PROVENANCE')
 observed={'01GTGT-annex12-p1-50.xml':(identifier(gui.get('exportSha256'),64),gui.get('exportBytes')),'01GTGT-annex12-p7-3333.xml':(identifier(gui.get('annex12NonzeroSecondExportSha256'),64),gui.get('annex12NonzeroSecondExportBytes'))}
 for _,size in observed.values():
  if type(size) is not int or not 0<size<=262144:fail('PROVENANCE')
 installed_root=pathlib.Path(installed_root);temporary=pathlib.Path(runner_temp)
 if not installed_root.is_absolute() or not temporary.is_absolute() or not installed_root.is_dir() or not temporary.is_dir() or transport.unsafe_path(installed_root) or transport.unsafe_path(temporary):fail('STAGING')
 for name,expected in PINS.items():
  if hashlib.sha256(transport.safe_read(installed_root/name,41943040)).hexdigest()!=expected:fail('HASH')
 folder=installed_root/ORIGINAL_DIRECTORY
 if transport.unsafe_path(folder) or not folder.is_dir():fail('STAGING')
 bodies={}
 for name,original in SNAPSHOTS.items():
  body=transport.safe_read(folder/original,262144);sha,size=observed[name]
  if len(body)!=size or hashlib.sha256(body).hexdigest()!=sha:fail('HASH')
  validate_snapshot(body,name,today);bodies[name]=body
 provenance=(json.dumps(expected_provenance(bodies,run_id,builder_sha,run_attempt),ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode();validate_provenance(provenance,bodies,run_id,builder_sha,run_attempt)
 destination=temporary/DIRECTORY
 if destination.exists() or transport.unsafe_path(destination):fail('STAGING')
 destination.mkdir()
 try:
  for name,body in bodies.items():
   with (destination/name).open('xb') as stream:stream.write(body)
  with (destination/'provenance.json').open('xb') as stream:stream.write(provenance)
  staged,_,_=read_evidence(destination,run_id,builder_sha,run_attempt,today)
  if staged!=bodies or any(transport.safe_read(folder/original,262144)!=bodies[name] for name,original in SNAPSHOTS.items()):fail('HASH')
 except Exception:
  if not transport.unsafe_path(destination):shutil.rmtree(destination,ignore_errors=True)
  raise
 return {'format':'htkk-annex12-nonzero-export-staging-status-v1','status':'staged','probeId':PROBE_ID,'snapshotCount':2,'rawBytesPreserved':True,'independentSchemaVerification':True,'nativeAnnexRoundTripVerified':False,'fullCompatibilityVerified':False}

def main():
 directory=pathlib.Path(os.environ.get('RUNNER_TEMP',''))/DIRECTORY
 try:
  if os.environ.get('GITHUB_REPOSITORY')!=BUILDER:fail('BUILDER')
  token=os.environ.get('SOURCE_PUBLISH_TOKEN') or os.environ.get('SOURCE_READ_TOKEN')
  if not token:fail('AUTH')
  bodies,metadata,_=read_evidence(directory,os.environ.get('GITHUB_RUN_ID'),os.environ.get('GITHUB_SHA'),os.environ.get('GITHUB_RUN_ATTEMPT'))
  print(json.dumps(publish(bodies,metadata,token),separators=(',',':')))
 except Exception as error:
  print(json.dumps(safe_failure(error),separators=(',',':')));raise SystemExit('Nonzero annex export retention rejected; no raw XML, paths, credentials or remote error published.')
 finally:
  if os.environ.get('RUNNER_TEMP') and directory.name==DIRECTORY and not transport.unsafe_path(directory):shutil.rmtree(directory,ignore_errors=True)
if __name__=='__main__':main()
