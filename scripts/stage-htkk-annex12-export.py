"""Token-free bounded staging entry, used only after original supplier shutdown."""
import importlib.util,json,os,pathlib,sys
spec=importlib.util.spec_from_file_location('annex12_staging',pathlib.Path(__file__).with_name('publish-htkk-annex12-export.py'));p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
try:
 if os.environ.get('GITHUB_REPOSITORY')!=p.BUILDER:p.fail('BUILDER')
 raw=sys.stdin.buffer.read(32769)
 if len(raw)>32768:p.fail('PROVENANCE')
 request=p.transport.reader.json_object(raw,'MANIFEST')
 if set(request)!=set(('installedRoot','gui','supplierStopped','sourcesUnmodified')) or not isinstance(request['installedRoot'],str):p.fail('PROVENANCE')
 result=p.stage_original(request['installedRoot'],request['gui'],request['supplierStopped'],request['sourcesUnmodified'],os.environ.get('RUNNER_TEMP',''),os.environ.get('GITHUB_RUN_ID'),os.environ.get('GITHUB_SHA'),os.environ.get('GITHUB_RUN_ATTEMPT'))
 print(json.dumps(result,separators=(',',':')))
except Exception as error:
 result=p.safe_failure(error)
 if isinstance(error,p.contract.AnnexContractError):result.update(contractCode=error.code,contractFieldId=error.field)
 print(json.dumps(result,separators=(',',':')));raise SystemExit('Fixed annex staging rejected; no source XML, paths or raw errors logged.')
