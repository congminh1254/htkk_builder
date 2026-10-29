"""Strict aligned-input native retention; no simulated test is native proof."""
import base64,hashlib,importlib.util,json,pathlib,tempfile,unittest
ROOT=pathlib.Path(__file__).parent
spec=importlib.util.spec_from_file_location('aligned_retention_fixture',ROOT/'test_htkk_web_native_output.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f);n=f.n
class AlignedSigningTests(unittest.TestCase):
 def make(self,case='01GTGT-zero-M10-2026'):
  web,native,im,m=f.fixture(case);initial=native.replace(b'?>',b'?>\n',1)
  m.update(format='htkk-web-native-output-staging-v3',runAttempt=1,initialOutputSha256=hashlib.sha256(initial).hexdigest(),initialOutputBytes=len(initial),initialSigningDateRule='fixed-web-synthetic-date')
  return web,native,im,m,initial
 def test_all_thirteen_aligned_pairs_publish_without_normalization(self):
  for case in n.BRANCHES:
   with self.subTest(case=case):
    web,native,im,m,initial=self.make(case);fetch,calls=f.fake_api(web,im);n.publish(native,m,'synthetic-token',fetch,f.TODAY,initial=initial)
    blobs=[base64.b64decode(payload['content'])for path,_,payload,_ in calls if path=='/git/blobs'];manifest=json.loads(blobs[1]);self.assertEqual(manifest['format'],'htkk-web-native-output-reference-v3');self.assertEqual(blobs[0],native);self.assertEqual(blobs[2],initial);self.assertTrue(manifest['initialReexportComparison']['allLeafValuesMatched']);self.assertFalse(manifest['initialReexportComparison']['normalizationApplied']);self.assertFalse(manifest['fullRoundTrip'])
 def test_provider_date_money_and_attribute_changes_reject_before_api(self):
  for field,value in [('ttinNhaCCapDVu','B'*32),('ngayKy','2026-10-26'),('ngayLapTKhai','2026-10-25'),('ct40','1')]:
   with self.subTest(field=field):
    web,native,im,m,initial=self.make();initial=f.changed(initial,field,value);m.update(initialOutputSha256=hashlib.sha256(initial).hexdigest(),initialOutputBytes=len(initial));calls=[]
    def forbidden(*args):calls.append(args);raise AssertionError('Unexpected API call')
    with self.assertRaises((n.OutputError,n.privacy.EvidenceError)):n.publish(native,m,'synthetic-token',forbidden,f.TODAY,initial=initial)
    self.assertEqual(calls,[])
 def test_live_aligned_reader_rejects_legacy_v2_policy(self):
  web,native,im,m,initial=self.make();m.pop('initialSigningDateRule');m['format']='htkk-web-native-output-staging-v2'
  with tempfile.TemporaryDirectory() as directory:
   root=pathlib.Path(directory);(root/'01GTGT-native.xml').write_bytes(native);(root/n.INITIAL).write_bytes(initial);(root/'provenance.json').write_text(json.dumps(m))
   with self.assertRaises(n.OutputError):n.read_evidence(root,'123',f.BUILDER_SHA,f.SOURCE,'01GTGT-zero-M10-2026',f.ARTIFACT,f.TODAY,run_attempt='1',aligned=True)
 def test_claimed_alignment_requires_explicit_fixed_date_policy(self):
  web,native,im,m,initial=self.make();m['initialSigningDateRule']='normalize-signing-date'
  with self.assertRaises(n.OutputError):n.publish(native,m,'synthetic-token',lambda *args:self.fail('No IO allowed'),f.TODAY,initial=initial)

class OriginalSigningControlTests(unittest.TestCase):
 def test_original_editor_requires_source_mask_and_preserves_type_and_protection(self):
  source=(ROOT/'HtkkGtgtPeriodAndSheet.cs').read_text()
  block=source.split('private void EditOriginalSigningDate')[1].split('private bool periodDateMatched')[0]
  self.assertIn('FarPoint.Win.Spread.CellType.GeneralCellType',block)
  self.assertIn('Get(type,"FormatString")',block);self.assertIn('=="@"',block)
  self.assertIn('FarPoint.Win.Spread.CellType.MaskCellType',block);self.assertIn('Get(type,"Mask")',block);self.assertIn('=="00/00/0000"',block);self.assertIn('webSigningDateCellKind!=4',block);self.assertIn('"25102026"',block)
  for forbidden in ('SetValue','set_Value','set_CellType','set_Locked'):
   self.assertNotIn(forbidden,block)
  self.assertIn('BeginCellEdit(grid,sheet,65,10,true)',block)
 def test_staging_requires_date_editor_and_unchanged_full_document(self):
  source=(ROOT/'probe-htkk-windows.ps1').read_text()
  self.assertIn("@('webSigningDateEdited','webSigningDateReady')",source)
  self.assertIn('$gui.webSigningDateLocked -or',source);self.assertIn('$gui.roundtripXmlExactMatched -isnot [bool]',source)

if __name__=='__main__':unittest.main()
