"""Offline release provenance tests; no network, executable runtime or private source."""
import contextlib,datetime,io,json,os,pathlib,runpy,tempfile,unittest
from unittest.mock import patch

BUILDER=pathlib.Path(__file__).with_name('build.py')
class ReleaseProvenanceTests(unittest.TestCase):
 def build(self,sha='a'*40,version='0.7.0'):
  with tempfile.TemporaryDirectory() as folder:
   root=pathlib.Path(folder);source=root/'source';source.mkdir();(source/'out').mkdir();(source/'out/downloads').mkdir()
   (source/'package.json').write_text(json.dumps({'version':version}))
   for name in ('hotrokekhai-portable.zip','SHA256SUMS'):(source/'out/downloads'/name).write_text('synthetic-public-output')
   calls=[]
   def command(args,**kwargs):
    self.assertFalse(any('TOKEN' in key or 'SECRET' in key for key in kwargs['env']))
    calls.append(args)
    if args==['git','rev-parse','HEAD']:
     return type('Result',(),{'returncode':0,'stdout':sha.encode()})()
    return type('Result',(),{'returncode':0})()
   previous=pathlib.Path.cwd()
   try:
    os.chdir(root)
    with patch.dict(os.environ,{'RUNNER_TEMP':folder,'BUILD_MODE':'release','SOURCE_READ_TOKEN':'not-forwarded','UNRELATED_SECRET':'not-forwarded'}),patch('subprocess.run',side_effect=command),patch('shutil.which',return_value='/trusted/browser'),contextlib.redirect_stdout(io.StringIO()):
     try:runpy.run_path(str(BUILDER))
     except SystemExit as error:return None,calls,str(error)
    metadata=json.loads((source/'out/build.json').read_text())
    self.assertFalse((source/'out/downloads').exists())
    return metadata,calls,None
   finally:os.chdir(previous)
 def test_web_manifest_without_downloads_or_credential_environment(self):
  metadata,calls,error=self.build()
  self.assertIsNone(error);self.assertEqual(metadata['sourceSha'],'a'*40);self.assertEqual(metadata['version'],'0.7.0')
  self.assertIsNotNone(datetime.datetime.fromisoformat(metadata['builtAt']).tzinfo)
  self.assertNotIn(['node','scripts/package-portable.mjs'],calls)
  self.assertNotIn(['python3','scripts/fetch-node-runtime.py'],calls)
 def test_invalid_commit_prevents_runtime_fetch_and_package(self):
  metadata,calls,error=self.build(sha='bad; input')
  self.assertIsNone(metadata);self.assertEqual(error,'Build or verification failed. Private diagnostics were not published.')
  self.assertNotIn(['node','scripts/package-portable.mjs'],calls)
  self.assertNotIn(['python3','scripts/fetch-node-runtime.py'],calls)
 def test_invalid_version_does_not_enter_public_manifest(self):
  for value in ('secret-value',{'unexpected':'object'},'0.7.0\nprivate-data'):
   with self.subTest(value=value):
    metadata,calls,error=self.build(version=value)
    self.assertIsNone(metadata);self.assertIsNotNone(error);self.assertNotIn(['node','scripts/package-portable.mjs'],calls)
if __name__=='__main__':unittest.main()
