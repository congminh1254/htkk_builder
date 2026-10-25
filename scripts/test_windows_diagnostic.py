"""Boundaries for private-only supplier startup diagnostics; no network or image capture."""
import hashlib,importlib.util,json,pathlib,struct,tempfile,unittest
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('diagnostic',pathlib.Path(__file__).with_name('publish-windows-diagnostic.py'))
diag=importlib.util.module_from_spec(spec);spec.loader.exec_module(diag)
class PrivateDiagnosticTests(unittest.TestCase):
 def files(self,root):
  png=b'\x89PNG\r\n\x1a\n'+struct.pack('>I',13)+b'IHDR'+struct.pack('>II',100,80)+b'\x08\x06\x00\x00\x00'+b'0000'
  metadata={'format':'htkk-registration-diagnostic-v1','runId':'123','runtimeHost':'original','scope':'verified-microsoft-regsvr32-window-only','width':100,'height':80,'pngSha256':hashlib.sha256(png).hexdigest(),'taxDataUsed':False,'publicScreenshot':False}
  (root/'regsvr32-window.png').write_bytes(png);(root/'diagnostic.json').write_text(json.dumps(metadata));return metadata
 def test_exact_pair_and_run_identity_only(self):
  with tempfile.TemporaryDirectory() as folder:
   root=pathlib.Path(folder);self.files(root)
   self.assertEqual(set(diag.read_diagnostic(root,'123')),{'diagnostic.json','regsvr32-window.png'})
   with self.assertRaises(ValueError):diag.read_diagnostic(root,'124')
   (root/'private.log').write_text('not-uploaded')
   with self.assertRaises(ValueError):diag.read_diagnostic(root,'123')
 def test_metadata_extension_hash_and_oversize_rejected(self):
  for field,value in [('scope','desktop'),('pngSha256','0'*64),('taxDataUsed',True),('extra','raw-window-text'),('width',4000)]:
   with self.subTest(field=field),tempfile.TemporaryDirectory() as folder:
    root=pathlib.Path(folder);metadata=self.files(root);metadata[field]=value;(root/'diagnostic.json').write_text(json.dumps(metadata))
    with self.assertRaises(ValueError):diag.read_diagnostic(root,'123')
 def test_symlink_rejected(self):
  with tempfile.TemporaryDirectory() as folder:
   root=pathlib.Path(folder);self.files(root);(root/'regsvr32-window.png').unlink();(root/'regsvr32-window.png').symlink_to(root/'diagnostic.json')
   with self.assertRaises(ValueError):diag.read_diagnostic(root,'123')
 def test_public_repository_stops_before_any_upload(self):
  with patch.object(diag,'api',return_value={'private':False}) as api:
   with self.assertRaises(ValueError):diag.publish({'regsvr32-window.png':b'not-sent'},'synthetic')
   self.assertEqual(api.call_count,1)
 def test_upload_only_fixed_diagnostic_branch(self):
  calls=[]
  def api(path,token,payload=None,method=None):
   calls.append((path,payload,method))
   if path=='':return {'private':True}
   return {'sha':'a'*40}
  with patch.object(diag,'api',side_effect=api):diag.publish({'regsvr32-window.png':b'PNG','diagnostic.json':b'{}'},'synthetic')
  self.assertEqual(calls[-1][0],'/git/refs/heads/windows-reference-diagnostics');self.assertEqual(calls[-1][2],'PATCH')
  self.assertFalse(any('main' in path or 'pages-output' in path for path,_,_ in calls))
if __name__=='__main__':unittest.main()
