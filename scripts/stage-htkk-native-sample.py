"""Token-free bounded staging entry, never executes vendor code."""
import importlib.util,json,os,pathlib,sys
spec=importlib.util.spec_from_file_location('native_sample_stage',pathlib.Path(__file__).with_name('publish-htkk-native-sample.py'));p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
try:
 if os.environ.get('GITHUB_REPOSITORY')!=p.BUILDER:p.fail('BUILDER')
 raw=sys.stdin.buffer.read(32769)
 if len(raw)>32768:p.fail('PROVENANCE')
 request=p.transport.reader.json_object(raw,'MANIFEST')
 if set(request)!=set(('installedRoot','gui','supplierStopped','sourcesUnmodified','schemaPath')):p.fail('PROVENANCE')
 result=p.stage(request['installedRoot'],request['gui'],request['supplierStopped'],request['sourcesUnmodified'],request['schemaPath'],os.environ.get('RUNNER_TEMP'),os.environ.get('EXPECTED_WEB_SOURCE_SHA'),os.environ.get('GITHUB_SHA'),os.environ.get('GITHUB_RUN_ID'),os.environ.get('GITHUB_RUN_ATTEMPT'))
 print(json.dumps(result,separators=(',',':')))
except Exception as error:
 print(json.dumps(p.safe_failure(error),separators=(',',':')));raise SystemExit('Native sample staging rejected; no source XML, paths or raw errors logged.')
