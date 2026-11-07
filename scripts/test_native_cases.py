"""Offline trusted dispatch/callback contracts; no network or native evidence."""
import ast,importlib.util,pathlib,json,re,unittest,urllib.error
from unittest.mock import patch
ROOT=pathlib.Path(__file__).parent
def load(name,file):
 spec=importlib.util.spec_from_file_location(name,ROOT/file);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
d=load('native_dispatch_test','dispatch-native-cases.py');r=load('native_report_test','report-native-case.py')
def document():return {'format':'htkk-web-input-publication-v1','sourceCommit':'a'*40,'cases':[{'caseId':case,'artifactCommit':letter*40} for case,letter in zip(d.CASES,('b','c','d','e','f','1','2','3','4','5','6','7','8','9','0','a','b','c','d','e','f','1','2','3','4'))]}
class NativeCases(unittest.TestCase):
 def test_every_registered_case_and_separate_tokens_pending_before_dispatch(self):
  value=d.publication(json.dumps(document()).encode(),'a'*40);calls=[]
  d.dispatch(value,'builder-token','source-token',lambda *args:calls.append(args))
  self.assertEqual(len(calls),2*len(d.CASES))
  for index,case in enumerate(d.CASES):
   status,dispatch=calls[index*2:index*2+2]
   self.assertEqual(status[0],'https://api.github.com/repos/'+d.REPO+'/statuses/'+'a'*40);self.assertEqual(status[1],'source-token');self.assertEqual(status[2]['context'],d.CONTEXTS[case]);self.assertEqual(status[2]['state'],'pending')
   self.assertEqual(dispatch[1],'builder-token');self.assertEqual(dispatch[2]['inputs']['web_case_id'],case);self.assertEqual(dispatch[2]['inputs']['web_artifact_commit'],document()['cases'][index]['artifactCommit']);self.assertEqual(dispatch[2]['inputs']['web_source_sha'],'a'*40)
 def test_dispatch_failure_sets_failure_status_without_retrying_action(self):
  calls=[]
  def send(url,token,payload):
   calls.append((url,payload))
   if '/dispatches' in url:raise RuntimeError('unpublished remote error')
  with self.assertRaises(RuntimeError):d.dispatch(document(),'builder','source',send)
  self.assertEqual(len(calls),3);self.assertEqual(calls[-1][1]['state'],'failure');self.assertEqual(sum('/dispatches' in url for url,_ in calls),1)
 def test_publication_rejects_extra_duplicate_stale_mixed_cases_or_bad_sha(self):
  for mutate in (lambda x:x.update(extra='secret'),lambda x:x.update(sourceCommit='b'*40),lambda x:x['cases'].reverse(),lambda x:x['cases'][0].update(extra='private'),lambda x:x['cases'][0].update(artifactCommit='invalid')):
   value=document();mutate(value)
   with self.assertRaises(ValueError):d.publication(json.dumps(value).encode(),'a'*40)
  with self.assertRaises(ValueError):d.publication(b'{"format":"a","format":"b"}','a'*40)
  with self.assertRaises(ValueError):d.publication(b'x'*16385,'a'*40)
 def test_callback_success_is_only_actual_probe_success_other_outcomes_fail(self):
  for result in ('success','failure','cancelled','skipped'):
   payload=r.payload(d.CASES[0],result,'https://github.com','123')
   self.assertEqual(payload['state'],'success' if result=='success' else 'failure');self.assertEqual(payload['context'],'htkk-native/zero')
  for case,result,server,run in (('private','success','https://github.com','123'),(d.CASES[0],'pending','https://github.com','123'),(d.CASES[0],'success','https://evil.invalid','123'),(d.CASES[0],'success','https://github.com','private')):
   with self.assertRaises(ValueError):r.payload(case,result,server,run)
 def test_authenticated_post_has_no_redirects_or_error_body_logging(self):
  class Response:
   status=204
   def __enter__(self):return self
   def __exit__(self,*args):return False
  class Opener:
   def open(self,request,timeout):
    self_test.assertEqual(request.get_header('Authorization'),'Bearer fake-token');self_test.assertEqual(timeout,30);return Response()
  self_test=self
  with patch.object(d.urllib.request,'build_opener',return_value=Opener()) as build:d.post('https://api.github.com/repos/'+d.BUILDER+'/actions/workflows/probe-htkk-windows.yml/dispatches','fake-token',{})
  self.assertIsInstance(build.call_args.args[0],d.NoRedirect);self.assertIsNone(d.NoRedirect().redirect_request(None,None,None,None,None))
  with self.assertRaises(ValueError):d.post('https://api.github.com/','',{})


BUILDER_SHA='9'*40
import datetime,http.client
START=datetime.datetime(2026,11,6,10,0,0,tzinfo=datetime.timezone.utc)
def http_error(code):return urllib.error.HTTPError('https://api.github.com/x',code,'unpublished',{},None)
def probe_run(case,created='2026-11-06T10:00:01Z',**extra):
 run={'id':4242,'path':d.PROBE,'event':'workflow_dispatch','head_branch':'main','head_sha':BUILDER_SHA,'repository':{'full_name':d.BUILDER},'created_at':created,'display_title':d.run_title(case)}
 run.update(extra);return run
class NativeDispatchRetry(unittest.TestCase):
 """Bounded, duplicate-safe retry of the non-idempotent workflow_dispatch POST."""
 def harness(self,failures,runs=lambda case:[],cases=1):
  value=document();value['cases']=value['cases'][:cases];calls=[];queries=[];sleeps=[];failures=list(failures)
  def send(url,token,payload):
   calls.append((url,payload))
   if '/dispatches' in url and failures:
    error=failures.pop(0)
    if error is not None:raise error
  def get(url,token):
   self.assertEqual(token,'builder');queries.append(url)
   listed=runs(value['cases'][0]['caseId'])
   if isinstance(listed,Exception):raise listed
   return {'total_count':len(listed),'workflow_runs':listed}
  return value,send,get,calls,queries,sleeps
 def run_dispatch(self,value,send,get,sleeps):
  with patch('builtins.print'):d.dispatch(value,'builder','source',send,builder=BUILDER_SHA,get=get,sleep=sleeps.append,now=lambda:START)
 def dispatches(self,calls):return sum('/dispatches' in url for url,_ in calls)
 def test_transient_failure_then_success_redispatches_only_after_absence_check(self):
  for error in (urllib.error.URLError('reset'),TimeoutError(),http.client.RemoteDisconnected('closed'),ConnectionResetError(),http_error(502),http_error(503)):
   value,send,get,calls,queries,sleeps=self.harness([error,None])
   self.run_dispatch(value,send,get,sleeps)
   self.assertEqual(self.dispatches(calls),2);self.assertEqual(len(queries),1);self.assertEqual(sleeps,[2])
   self.assertEqual([p['state'] for u,p in calls if '/statuses/' in u],['pending'])
   query=d.urllib.parse.parse_qs(d.urllib.parse.urlsplit(queries[0]).query)
   self.assertEqual(query,{'event':['workflow_dispatch'],'branch':['main'],'head_sha':[BUILDER_SHA],'created':['>=2026-11-06T09:59:30Z'],'per_page':['100']})
   self.assertTrue(queries[0].startswith('https://api.github.com/repos/'+d.BUILDER+'/actions/workflows/probe-htkk-windows.yml/runs?'))
 def test_two_retries_with_backoff_then_success(self):
  value,send,get,calls,queries,sleeps=self.harness([http_error(500),http_error(504),None])
  self.run_dispatch(value,send,get,sleeps)
  self.assertEqual(self.dispatches(calls),3);self.assertEqual(sleeps,[2,5]);self.assertEqual(len(queries),2)
 def test_existing_run_for_same_case_prevents_redispatch(self):
  value,send,get,calls,queries,sleeps=self.harness([http_error(502)],runs=lambda case:[probe_run(d.CASES[2]),probe_run(case)],cases=2)
  self.run_dispatch(value,send,get,sleeps)
  # First case is not re-sent; the second case still dispatches exactly once.
  self.assertEqual(self.dispatches(calls),2);self.assertEqual(len(queries),1)
  self.assertEqual([p['inputs']['web_case_id'] for u,p in calls if '/dispatches' in u],[d.CASES[0],d.CASES[1]])
  self.assertEqual([p['state'] for u,p in calls if '/statuses/' in u],['pending','pending'])
 def test_runs_of_other_cases_old_runs_or_foreign_identity_do_not_count(self):
  case=d.CASES[0]
  for run in (probe_run(d.CASES[1]),probe_run(case,created='2026-11-06T09:59:00Z'),probe_run(case,head_sha='8'*40),probe_run(case,path='.github/workflows/build.yml'),probe_run(case,event='push'),probe_run(case,head_branch='feature')):
   self.assertIs(d.created(case,BUILDER_SHA,START,'t',lambda url,token:{'total_count':1,'workflow_runs':[run]}),False)
  self.assertIs(d.created(case,BUILDER_SHA,START,'t',lambda url,token:{'total_count':1,'workflow_runs':[probe_run(case)]}),True)
 def test_ambiguous_or_unverifiable_listing_fails_closed_without_redispatch(self):
  case=d.CASES[0]
  for listing in ([probe_run(case,display_title='Kiểm tra điều kiện chạy HTKK Windows')],[probe_run(case,display_title=None)],[probe_run(case,created='bad')]):
   self.assertIsNone(d.created(case,BUILDER_SHA,START,'t',lambda url,token:{'total_count':1,'workflow_runs':listing}))
  self.assertIsNone(d.created(case,BUILDER_SHA,START,'t',lambda url,token:{'total_count':101,'workflow_runs':[]}))
  for runs in (lambda case:[probe_run(case,display_title='untitled')],lambda case:urllib.error.URLError('down')):
   value,send,get,calls,queries,sleeps=self.harness([http_error(503),None],runs=runs)
   with self.assertRaises(urllib.error.HTTPError):self.run_dispatch(value,send,get,sleeps)
   self.assertEqual(self.dispatches(calls),1);self.assertEqual(calls[-1][1]['state'],'failure')
 def test_client_errors_are_never_retried(self):
  for code in (400,401,403,404,409,422):
   value,send,get,calls,queries,sleeps=self.harness([http_error(code),None])
   with self.assertRaises(urllib.error.HTTPError):self.run_dispatch(value,send,get,sleeps)
   self.assertEqual(self.dispatches(calls),1);self.assertEqual(queries,[]);self.assertEqual(sleeps,[]);self.assertEqual(calls[-1][1]['state'],'failure')
  for error in (ValueError('HTTP'),RuntimeError('x'),http_error(501)):self.assertFalse(d.transient(error))
 def test_persistent_failure_is_bounded_and_keeps_safe_exit(self):
  value,send,get,calls,queries,sleeps=self.harness([http_error(502)]*10)
  with self.assertRaises(urllib.error.HTTPError):self.run_dispatch(value,send,get,sleeps)
  self.assertEqual(self.dispatches(calls),3);self.assertEqual(sleeps,[2,5]);self.assertEqual(len(queries),2);self.assertEqual(calls[-1][1]['state'],'failure')
  path=ROOT/'_absent_runner_temp'
  env={'GITHUB_REPOSITORY':d.BUILDER,'RUNNER_TEMP':str(path),'COMMIT_SHA':'a'*40,'GITHUB_SHA':BUILDER_SHA,'BUILDER_ACTIONS_TOKEN':'secret-actions','SOURCE_STATUS_TOKEN':'secret-status'}
  import io,contextlib,os,tempfile
  def fail_dispatch(url,token,payload):
   if '/dispatches' in url:raise http_error(503)
  with tempfile.TemporaryDirectory() as temp:
   (pathlib.Path(temp)/'htkk-web-input-publication.json').write_text(json.dumps(document()));env['RUNNER_TEMP']=temp;out=io.StringIO()
   with patch.dict(os.environ,env),patch.object(d,'post',side_effect=fail_dispatch) as posted,patch.object(d,'get_json',return_value={'total_count':0,'workflow_runs':[]}) as listed,patch.object(d.time,'sleep'),contextlib.redirect_stdout(out):
    with self.assertRaises(SystemExit) as raised:d.main()
   self.assertEqual(str(raised.exception),'Native-case dispatch failed; no raw response, input, path or credential published.')
   self.assertEqual(sum('/dispatches' in c.args[0] for c in posted.call_args_list),3);self.assertEqual(posted.call_args_list[-1].args[2]['state'],'failure');self.assertEqual(listed.call_count,2)
   self.assertNotIn('secret',out.getvalue());self.assertNotIn('a'*40,out.getvalue())
 def test_status_posts_retry_blindly_but_bounded(self):
  value=document();value['cases']=value['cases'][:1];calls=[];errors=[urllib.error.URLError('x'),http_error(500)];sleeps=[]
  def send(url,token,payload):
   calls.append(url)
   if '/statuses/' in url and errors:raise errors.pop(0)
  with patch('builtins.print'):d.dispatch(value,'builder','source',send,builder=BUILDER_SHA,get=lambda *a:self.fail('no run lookup'),sleep=sleeps.append,now=lambda:START)
  self.assertEqual(sleeps,[2,5]);self.assertEqual(sum('/statuses/' in u for u in calls),3);self.assertEqual(sum('/dispatches' in u for u in calls),1)
 def test_probe_run_name_matches_dispatcher_identity(self):
  text=(ROOT.parent/'.github/workflows/probe-htkk-windows.yml').read_text()
  self.assertIn('\nrun-name: HTKK native case ${{ inputs.web_case_id }} (${{ inputs.gui_automation }})\n',text)
  self.assertEqual(d.run_title(d.CASES[0]),'HTKK native case '+d.CASES[0]+' ('+d.case_registry.ADAPTERS[d.case_registry.CASES[d.CASES[0]]['adapterId']]['driver']+')')


class NativeWorkflowCredentials(unittest.TestCase):
 def test_parallel_web_cases_skip_shared_references_but_keep_scoped_raw_and_status(self):
  # Exercise the workflow conditions, including their process/credential gates.
  # This verifies the real publication routing rather than a duplicated helper.
  text=(ROOT.parent/'.github/workflows/probe-htkk-windows.yml').read_text()
  conditions=dict(re.findall(r"      - name: ([^\n]+)\n        if: ([^\n]+)",text))
  def enabled(name,mode,install=True,safe='true',stopped='true',artifact='a'*40):
   expression=conditions[name].replace('always()','True').replace('&&',' and ').replace('||',' or ')
   values={'inputs.install_and_probe':install,'inputs.gui_automation':mode,'steps.native_probe.outputs.credentials_safe':safe,'steps.native_probe.outputs.supplier_stopped':stopped,'inputs.web_artifact_commit':artifact}
   for key,value in values.items():expression=expression.replace(key,repr(value))
   parsed=ast.parse(expression,mode='eval')
   for node in ast.walk(parsed):
    self.assertIsInstance(node,(ast.Expression,ast.BoolOp,ast.And,ast.Or,ast.Compare,ast.Eq,ast.NotEq,ast.Constant))
   return eval(compile(parsed,'<fixed workflow condition>','eval'),{'__builtins__':{}},{})
  shared=('Publish supplier startup window privately','Retain synthetic common-header reference privately')
  raw='Retain verified raw native web reexport privately';status='Report fixed native-case status privately'
  declaration_raw='Retain raw native declaration export privately'
  for mode in ('none','profile-save','gtgt-export-inspect','gtgt-web-import-inspect','declaration-web-import-inspect'):
   web=mode=='gtgt-web-import-inspect';declaration=mode=='declaration-web-import-inspect'
   for name in shared:self.assertEqual(enabled(name,mode),not web and not declaration)
   self.assertEqual(enabled(raw,mode),web);self.assertEqual(enabled(status,mode),web or declaration);self.assertEqual(enabled(declaration_raw,mode),declaration)
   for name in (*shared,raw,status,declaration_raw):
    self.assertFalse(enabled(name,mode,install=False));self.assertFalse(enabled(name,mode,safe='false'))
  self.assertFalse(enabled(raw,'gtgt-web-import-inspect',stopped='false'))
  self.assertFalse(enabled(raw,'gtgt-web-import-inspect',artifact=''))

class NativeManifestFormatRouting(unittest.TestCase):
 def test_powershell_staging_routes_every_fixed_case_to_its_exact_manifest(self):
  reader=load('native_manifest_reader_test','fetch-htkk-web-input.py')
  script=(ROOT/'probe-htkk-windows.ps1').read_text()
  table=re.search(r'\$HtkkNativeCaseFormats=@\{(.*?)\n\}',(ROOT/'HtkkNativeCaseFormats.ps1').read_text(),re.S)
  self.assertIn("HtkkNativeCaseFormats.ps1",script)
  self.assertIsNotNone(table)
  pairs=re.findall(r"'([^']+)'='([^']+)'",table.group(1))
  self.assertEqual(len(pairs),len(reader.CASES))
  self.assertEqual(dict(pairs),reader.CASES)
  self.assertIn('$expectedFormat=$expectedFormats[$env:EXPECTED_WEB_CASE_ID]',script)

class NativeEditorCountBoundary(unittest.TestCase):
 def test_powershell_negative_fixture_exceeds_accepted_editor_count(self):
  boundary=(ROOT/'Get-HtkkSafeGuiReferenceResult.ps1').read_text()
  fixtures=(ROOT/'Test-HtkkSafeGuiReferenceResult.ps1').read_text()
  maximum=json.loads((ROOT/'htkk-native-automation-registry.json').read_text())['resultFields']['webCaseEditCount']['maximum']
  self.assertIn("$value['webCaseEditCount'] -gt "+str(maximum),boundary)
  rejected=int(re.search(r"@\{key='webCaseEditCount';value=(\d+)\}",fixtures).group(1))
  self.assertEqual(rejected,maximum+1)

class NativeImportDispatchIdentity(unittest.TestCase):
 def test_import_case_never_reuses_direct_sale_context_or_artifact_branch(self):
  reader=load('native_import_identity_reader','fetch-htkk-web-input.py')
  publisher=load('native_import_identity_publisher','publish-htkk-web-inputs.py')
  output=load('native_import_identity_output','publish-htkk-web-native-output.py')
  case='01GTGT-native-import-sale10-M10-2026';sale='01GTGT-sale10-M10-2026'
  self.assertIn(case,d.CASES);self.assertEqual(d.CONTEXTS[case],'htkk-native/native-import-sale10');self.assertNotEqual(d.CONTEXTS[case],d.CONTEXTS[sale])
  self.assertEqual(reader.CASES[case],'htkk-web-native-import-sale10-input-v1')
  cases={entry[0]:entry[1:] for entry in publisher.CASES}
  self.assertEqual(cases[case],('htkk-web-reference-native-import-sale10-input','gtgt-web-reference-native-import-sale10-input'))
  self.assertNotEqual(cases[case],cases[sale]);self.assertNotEqual(output.BRANCHES[case],output.BRANCHES[sale])
  self.assertEqual(len(d.CASES),len(set(d.CASES)));self.assertEqual(set(cases),set(d.CASES));self.assertEqual(set(output.BRANCHES),set(d.CASES)-set(reader.case_registry.DECLARATION_CASES))
