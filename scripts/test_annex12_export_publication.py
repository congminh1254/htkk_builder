"""Synthetic publisher/staging tests; no XML fixture is native runtime evidence."""
import base64,copy,hashlib,importlib.util,json,pathlib,tempfile,unittest,urllib.error
from unittest.mock import patch
ROOT=pathlib.Path(__file__).parent
spec=importlib.util.spec_from_file_location('annex_publication',ROOT/'publish-htkk-annex12-export.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
spec=importlib.util.spec_from_file_location('annex_publication_fixture',ROOT/'test_annex12_fixed_export.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
TODAY=f.TODAY
BUILDER_SHA='a'*40

def metadata(native):
 return {'format':'htkk-annex12-export-staging-v1','builderRepository':p.BUILDER,'builderCommit':BUILDER_SHA,'runId':'123','runAttempt':'1','sourceVersion':'5.8.1','runtimeHost':'clr2-x86-reference','caseId':p.contract.CASE_ID,'inputsSynthetic':True,'originalProcessStopped':True,'originalSourcesUnmodified':True,'originalExportSucceeded':True,'originalExporterValidatedSchema':True,'independentSchemaVerification':True,'independentSchemaEngine':'System.Xml.Schema/.NET2-x86','fixedInputCount':14,'groupCount':1,'childRowCount':2,'checkedMainMoneyCount':27,'observedTotalLeafCount':112,'inputHelperSha256':p.helper_pins(),'sourcePins':p.PINS,'originalOutputSha256':hashlib.sha256(native).hexdigest(),'originalOutputBytes':len(native),'nativeAnnexRoundTripVerified':False,'fullCompatibilityVerified':False}
def gui(native):
 keys=('sourcePinsVerified','periodAnnex12Matched','annex12SourcePinsMatched','annex12RowAfterMatched','annex12InputReadOnlyIdentityMatched','annex12InputIdentityMatched','annex12InputTypesMatched','annex12InputGeographyMatched','annex12InputTaxAuthoritiesMatched','annex12InputPercentagesMatched','annex12InputZeroTaxMatched','annex12ExportMainZeroMatched','annex12ExportShapeMatched','annex12ExportSchemaVerified','exportSchemaPinnedVerified','exportCommandInvoked','exportSelectorMatched','exportButtonInvoked','exportDialogMatched','exportDestinationFresh','exportFilenameKeyboardCommitted','exportDialogSubmitted','exportFileExists','exportXmlRootMatched','exportSyntheticIdentityMatched','exportSuccessAcknowledged','exportOriginalPathMatched')
 return {**dict.fromkeys(keys,True),'status':'matched','mode':'gtgt-annex12-export-inspect','stage':'gtgt-annex12-export-inspected','failureCategory':'none','webInputVerified':False,'realTaxpayerDataUsed':False,'runtimeRoundTrip':False,'annexSelectedCount':1,'annex12InputActionCount':14,'annex12GroupCount':1,'annex12RowAfterGroupRows':2,'annex12RowAfterRows':67,'gtgtCaseMoneyCount':27,'gtgtCaseMismatchMask':0,'gtgtCaseNonzeroMask':0,'exportSha256':hashlib.sha256(native).hexdigest(),'exportBytes':len(native)}
def api_fixture(private=True,existing=True,ref_error=None,patch_error=None):
 calls=[]
 def fetch(path,token,payload=None,method=None):
  calls.append((path,payload,method));
  if path=='':return {'private':private,'full_name':p.REPO}
  if path=='/git/blobs':
   body=base64.b64decode(payload['content']);return {'sha':hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest()}
  if path=='/git/trees':return {'sha':'b'*40}
  if path=='/git/commits':return {'sha':'c'*40}
  if path.startswith('/git/ref/heads/'):
   if ref_error or not existing:raise urllib.error.HTTPError('https://api.github.com',ref_error or 404,'PRIVATE ERROR',{},None)
   return {'ref':'refs/heads/'+p.BRANCH,'object':{'type':'commit','sha':'d'*40}}
  if path.startswith('/git/refs/heads/'):
   if patch_error:raise urllib.error.HTTPError('https://api.github.com',patch_error,'PRIVATE ERROR',{},None)
   return {'ref':'refs/heads/'+p.BRANCH,'object':{'type':'commit','sha':payload['sha']}}
  if path=='/git/refs':return {'ref':payload['ref'],'object':{'type':'commit','sha':payload['sha']}}
  raise AssertionError('Unknown fixed API path')
 return fetch,calls

class AnnexRetentionBoundaryTests(unittest.TestCase):
 def test_no_network_before_exact_case_provenance_and_privacy(self):
  native=f.fixture();base=metadata(native)
  for key,value in (('originalProcessStopped',False),('independentSchemaVerification',False),('inputsSynthetic',1),('fixedInputCount',16),('sourcePins',{}),('inputHelperSha256',{}),('fullCompatibilityVerified',True),('extra','PRIVATE')):
   bad={**base,key:value}
   with self.subTest(key=key),patch.object(p.transport,'api') as api,self.assertRaises(Exception):
    p.publish(native,bad,'synthetic-token',today=TODAY)
   api.assert_not_called()
  with patch.object(p.transport,'api') as api,self.assertRaises(Exception):p.publish(native.replace(b'9999999997-001',b'1234567890-001'),base,'synthetic-token',today=TODAY)
  api.assert_not_called()
 def test_run_and_attempt_are_bound_to_external_staging_context(self):
  native=f.fixture();body=json.dumps(metadata(native)).encode()
  for run_id,builder_sha,attempt in (('124',BUILDER_SHA,'1'),('123','b'*40,'1'),('123',BUILDER_SHA,'2')):
   with self.subTest(run_id=run_id,attempt=attempt),self.assertRaises(p.AnnexPublicationError):p.validate_provenance(body,native,run_id,builder_sha,attempt)
 def test_public_repo_is_rejected_before_any_git_object_write(self):
  native=f.fixture();fetch,calls=api_fixture(private=False)
  with self.assertRaises(p.AnnexPublicationError):p.publish(native,metadata(native),'synthetic-token',fetch,TODAY)
  self.assertEqual([x[0] for x in calls],[''])
 def test_raw_bytes_private_orphan_branch_and_false_roundtrip_flags(self):
  native=f.fixture();fetch,calls=api_fixture(existing=False)
  result=p.publish(native,metadata(native),'synthetic-token',fetch,TODAY)
  blobs=[base64.b64decode(payload['content']) for path,payload,_ in calls if path=='/git/blobs']
  self.assertEqual(blobs[0],native);manifest=json.loads(blobs[1]);self.assertTrue(manifest['originalAnnexExportVerified']);self.assertTrue(manifest['independentSchemaVerification']);self.assertFalse(manifest['nativeAnnexRoundTripVerified']);self.assertFalse(manifest['fullCompatibilityVerified'])
  self.assertEqual(next(payload['parents'] for path,payload,_ in calls if path=='/git/commits'),[])
  self.assertEqual(calls[-1][1],{'ref':'refs/heads/'+p.BRANCH,'sha':'c'*40});self.assertFalse(result['nativeAnnexRoundTripVerified'])
  self.assertFalse(any('main' in path or 'pages-output' in path or 'gtgt-web-native-' in path for path,_,_ in calls))
 def test_only_get_ref_404_creates_reference_and_patch_422_never_falls_back(self):
  native=f.fixture()
  for ref_error,patch_error in ((403,None),(None,422)):
   fetch,calls=api_fixture(ref_error=ref_error,patch_error=patch_error)
   with self.assertRaises(urllib.error.HTTPError):p.publish(native,metadata(native),'synthetic-token',fetch,TODAY)
   self.assertNotIn('/git/refs',[x[0] for x in calls])
 def test_bounded_failures_do_not_echo_raw_values_paths_or_remote_errors(self):
  for error in (p.AnnexPublicationError('HASH'),p.contract.AnnexContractError('VALUE'),urllib.error.HTTPError('https://PRIVATE.invalid',403,'PRIVATE ERROR',{},None),ValueError('PRIVATE XML')):
   result=p.safe_failure(error);self.assertNotIn('PRIVATE',json.dumps(result));self.assertEqual(set(result),{'format','status','code'})

class AnnexTokenFreeStagingTests(unittest.TestCase):
 def stage_layout(self,root,native):
  installed=root/'installed';temporary=root/'temp';temporary.mkdir();(installed/'Project').mkdir(parents=True)
  supplier=installed/'Project/HTKK.exe';supplier.write_bytes(b'fixed source parser fixture')
  original=installed/'DataFiles/9999999997/reference-annex12-output/01GTGT.xml';original.parent.mkdir(parents=True);original.write_bytes(native)
  return installed,temporary,original,{'Project/HTKK.exe':hashlib.sha256(supplier.read_bytes()).hexdigest()}
 def test_supplier_stop_and_each_observation_required_before_any_file_read(self):
  native=f.fixture();base=gui(native)
  for changes,stopped in (({},False),({'annex12ExportSchemaVerified':False},True),({'gtgtCaseMoneyCount':26},True),({'annex12InputActionCount':16},True),({'webInputVerified':True},True),({'annex12InputIdentityMatched':1},True)):
   with self.subTest(changes=changes),patch.object(p.transport,'safe_read') as read,self.assertRaises(Exception):p.stage_original('/unread','/unread' if changes is None else {**base,**changes},stopped,True,'/unread','123',BUILDER_SHA,'1',TODAY)
   read.assert_not_called()
 def test_stage_preserves_both_raw_bytes_and_original_source_while_binding_hashes(self):
  native=f.fixture()
  with tempfile.TemporaryDirectory() as tmp:
   installed,temporary,original,pins=self.stage_layout(pathlib.Path(tmp),native)
   with patch.object(p,'PINS',pins):
    result=p.stage_original(installed,gui(native),True,True,temporary,'123',BUILDER_SHA,'1',TODAY);staged,meta=p.read_evidence(temporary/p.DIRECTORY,'123',BUILDER_SHA,'1',TODAY)
   self.assertEqual(original.read_bytes(),native);self.assertEqual(staged,native);self.assertEqual(meta['inputHelperSha256'],p.helper_pins());self.assertTrue(result['rawBytesPreserved'])
 def test_source_hash_change_and_preexisting_destination_never_get_erased(self):
  native=f.fixture()
  with tempfile.TemporaryDirectory() as tmp:
   installed,temporary,original,pins=self.stage_layout(pathlib.Path(tmp),native)
   with patch.object(p,'PINS',{'Project/HTKK.exe':'f'*64}),self.assertRaises(Exception):p.stage_original(installed,gui(native),True,True,temporary,'123',BUILDER_SHA,'1',TODAY)
   self.assertFalse((temporary/p.DIRECTORY).exists())
   destination=temporary/p.DIRECTORY;destination.mkdir();(destination/'keep').write_bytes(b'owned before probe')
   with patch.object(p,'PINS',pins),self.assertRaises(Exception):p.stage_original(installed,gui(native),True,True,temporary,'123',BUILDER_SHA,'1',TODAY)
   self.assertEqual((destination/'keep').read_bytes(),b'owned before probe')
 def test_symlink_source_or_staged_file_and_extra_stage_files_rejected(self):
  native=f.fixture()
  with tempfile.TemporaryDirectory() as tmp:
   installed,temporary,original,pins=self.stage_layout(pathlib.Path(tmp),native)
   real=original.with_name('target.xml');original.rename(real)
   try:original.symlink_to(real)
   except OSError:self.skipTest('Symlink creation unavailable on this OS')
   with patch.object(p,'PINS',pins),self.assertRaises(Exception):p.stage_original(installed,gui(native),True,True,temporary,'123',BUILDER_SHA,'1',TODAY)
