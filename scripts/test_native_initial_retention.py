"""Real-byte retention boundary tests; synthetic inputs do not prove native execution."""
import base64,hashlib,importlib.util,json,pathlib,tempfile,unittest
ROOT=pathlib.Path(__file__).parent
spec=importlib.util.spec_from_file_location('native_retention_tests',ROOT/'test_htkk_web_native_output.py');t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t);n=t.n
class InitialRetentionTests(unittest.TestCase):
 def setUp(self):
  self.web,self.native,self.input,self.metadata=t.fixture()
  # Distinct bytes, semantically equal: prove baseline is not synthesized from reexport.
  self.initial=t.changed(self.native,'ngayKy','2026-10-26').replace(b'?>',b'?>\n',1)
  self.metadata.update(format='htkk-web-native-output-staging-v2',runAttempt=2,initialOutputSha256=hashlib.sha256(self.initial).hexdigest(),initialOutputBytes=len(self.initial))
 def provenance(self,initial=None,attempt='2'):
  return n.validate_provenance(json.dumps(self.metadata).encode(),self.native,'123',t.BUILDER_SHA,t.SOURCE,'01GTGT-zero-M10-2026',t.ARTIFACT,self.initial if initial is None else initial,attempt)
 def test_binds_distinct_original_baseline_and_attempt(self):
  self.assertNotEqual(self.initial,self.native);self.assertEqual(self.provenance()['runAttempt'],2)
 def test_wrong_attempt_and_baseline_bytes_rejected(self):
  for initial,attempt in [(self.native,'2'),(self.initial,'1'),(self.initial,'0'),(self.initial,'02'),(self.initial,'true')]:
   with self.subTest(attempt=attempt),self.assertRaises(n.OutputError):self.provenance(initial,attempt)
 def test_boolean_attempt_rejected(self):
  self.metadata['runAttempt']=True
  with self.assertRaises(n.OutputError):self.provenance(attempt='1')
 def stage(self,directory):
  (directory/'01GTGT-native.xml').write_bytes(self.native);(directory/n.INITIAL).write_bytes(self.initial);(directory/'provenance.json').write_text(json.dumps(self.metadata))
 def read(self,directory):return n.read_evidence(directory,'123',t.BUILDER_SHA,t.SOURCE,'01GTGT-zero-M10-2026',t.ARTIFACT,t.TODAY,run_attempt='2')
 def test_reads_exact_three_file_envelope(self):
  with tempfile.TemporaryDirectory() as path:
   directory=pathlib.Path(path);self.stage(directory);native,metadata=self.read(directory);self.assertEqual(native,self.native);self.assertEqual(metadata,self.metadata)
 def test_no_legacy_fallback_for_live_v2_reader(self):
  with tempfile.TemporaryDirectory() as path:
   directory=pathlib.Path(path);self.stage(directory);(directory/n.INITIAL).unlink()
   with self.assertRaises(n.OutputError):self.read(directory)
 def test_symlink_and_additional_file_rejected(self):
  with tempfile.TemporaryDirectory() as path:
   directory=pathlib.Path(path);self.stage(directory);(directory/'unexpected.xml').write_bytes(self.initial)
   with self.assertRaises(n.OutputError):self.read(directory)
   (directory/'unexpected.xml').unlink();(directory/n.INITIAL).unlink();(directory/n.INITIAL).symlink_to(directory/'01GTGT-native.xml')
   with self.assertRaises((n.OutputError,n.transport.PublicationError)):self.read(directory)
 def test_publishes_both_original_byte_streams_to_private_commit(self):
  fetch,calls=t.fake_api(self.web,self.input);result=n.publish(self.native,self.metadata,'synthetic-token',fetch,t.TODAY,initial=self.initial)
  blobs=[base64.b64decode(payload['content'])for path,_,payload,_ in calls if path=='/git/blobs'];self.assertEqual(blobs[0],self.native);self.assertEqual(blobs[2],self.initial)
  manifest=json.loads(blobs[1]);self.assertEqual(manifest['format'],'htkk-web-native-output-reference-v2');self.assertEqual(manifest['files'][n.INITIAL]['sha256'],hashlib.sha256(self.initial).hexdigest());self.assertEqual(manifest['provenance']['runAttempt'],2);self.assertFalse(manifest['initialReexportComparison']['allLeafValuesMatched']);self.assertFalse(manifest['initialReexportComparison']['normalizationApplied']);self.assertFalse(manifest['fullRoundTrip']);self.assertFalse(manifest['independentSchemaVerification'])
 def test_bad_initial_never_reaches_authenticated_io(self):
  broken=t.changed(self.initial,'ct40','1');self.metadata.update(initialOutputSha256=hashlib.sha256(broken).hexdigest(),initialOutputBytes=len(broken));calls=[]
  def fetch(*args):calls.append(args);raise AssertionError('Unexpected authenticated call')
  with self.assertRaises((n.OutputError,n.privacy.EvidenceError)):n.publish(self.native,self.metadata,'synthetic-token',fetch,t.TODAY,initial=broken)
  self.assertEqual(calls,[])
 def test_native_pair_cannot_normalize_service_identity_or_creation_date(self):
  for name,value in [('ttinNhaCCapDVu','B'*32),('ngayLapTKhai','2026-10-25')]:
   with self.subTest(field=name):self.assertFalse(n.compare_native_roundtrip(self.initial,t.changed(self.native,name,value))['allLeafValuesMatched'])
 def test_missing_initial_cannot_publish_v2_claim(self):
  with self.assertRaises(n.OutputError):n.publish(self.native,self.metadata,'synthetic-token',lambda *args:self.fail('No API call allowed'),t.TODAY)
if __name__=='__main__':unittest.main()
