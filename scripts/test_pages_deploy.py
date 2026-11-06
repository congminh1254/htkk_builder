"""Offline contracts: every Pages release deploys under its own marker commit and is proven live."""
import base64,contextlib,importlib.util,io,json,pathlib,re,shutil,subprocess,tempfile,unittest
spec=importlib.util.spec_from_file_location('pages_deploy',pathlib.Path(__file__).with_name('pages-deploy.py'));d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
WORKFLOW=(pathlib.Path(__file__).parent.parent/'.github/workflows/pages.yml').read_text()
P,S,B,M='8'*40,'f'*40,'5'*40,'a'*40
def job(name):
 return re.split(r'(?m)^  [a-z]+:$',re.split(r'(?m)^  '+name+':$',WORKFLOW.split('\njobs:\n')[1])[1])[0]
def steps(text):
 return [l.strip() for l in text.splitlines() if l.strip().startswith(('- name:','- uses:','uses:','run:'))]
def quiet(function,*args,**kwargs):
 with contextlib.redirect_stdout(io.StringIO()):return function(*args,**kwargs)
class Clock:
 def __init__(self):self.now=0.0
 def __call__(self):return self.now
 def sleep(self,seconds):self.now+=seconds
class WorkflowContract(unittest.TestCase):
 def test_three_jobs_in_order(self):
  self.assertEqual(re.findall(r'(?m)^  ([a-z]+):$',WORKFLOW.split('\njobs:\n')[1]),['prepare','marker','deploy'])
  self.assertIn('needs: prepare',job('marker'));self.assertIn('needs: [prepare, marker]',job('deploy'))
 def test_existing_trigger_gate_kept_on_first_job(self):
  for fragment in ("github.ref == 'refs/heads/main'","github.event.workflow_run.conclusion == 'success'","display_title == 'HTKK release'","repository.full_name == 'congminh1254/htkk_builder'"):
   self.assertIn(fragment,job('prepare'))
  self.assertIn('cancel-in-progress: false',WORKFLOW)
  self.assertEqual(WORKFLOW.split('permissions:')[1].split('concurrency:')[0].strip(),'contents: read')
 def permissions(self,name):
  block=job(name).split('permissions:\n')[1]
  return sorted(l.strip() for l in block.splitlines()[:6] if re.fullmatch(r'      [a-z-]+: (read|write)',l))
 def test_minimal_permissions_per_job(self):
  self.assertEqual(self.permissions('prepare'),['actions: read','contents: read'])
  self.assertEqual(self.permissions('marker'),['contents: write'])
  self.assertEqual(self.permissions('deploy'),['contents: read','id-token: write','pages: write'])
  self.assertNotIn('environment:',job('prepare'));self.assertNotIn('environment:',job('marker'))
  self.assertIn('name: github-pages',job('deploy'));self.assertIn('url: ${{ steps.deployment.outputs.page_url }}',job('deploy'))
 def test_private_source_only_in_prepare(self):
  self.assertIn('SOURCE_READ_TOKEN',job('prepare'))
  for name in ('marker','deploy'):
   with self.subTest(job=name):
    self.assertNotIn('secrets.',job(name));self.assertNotIn('htkk-net/htkk_web',job(name));self.assertNotIn('output/site',job(name))
 def test_prepare_gates_before_upload_and_cleanup(self):
  order=steps(job('prepare'));find=lambda f:next(i for i,l in enumerate(order) if f in l)
  sequence=[find('Resolve immutable private artifact'),find('Checkout generated static output only'),find('validate-pages.py'),find('pages-deploy.py expect'),find('upload-pages-artifact'),find('rm -rf output')]
  self.assertEqual(sequence,sorted(sequence))
  cleanup=job('prepare').split('Remove local private artifact')[1]
  self.assertIn('if: always()',cleanup)
  self.assertEqual(WORKFLOW.count('persist-credentials: false'),WORKFLOW.count('actions/checkout@'))
 def test_marker_job_runs_only_trusted_script(self):
  runs=[l for l in steps(job('marker')) if l.startswith('run:')]
  self.assertEqual(runs,['run: python3 builder/scripts/pages-deploy.py marker'])
  self.assertIn('GH_TOKEN: ${{ github.token }}',job('marker'))
 def test_deploy_uses_marker_and_no_builder_sha_action(self):
  self.assertNotIn('actions/deploy-pages',re.sub(r'#.*','',WORKFLOW))
  for fragment in ('MARKER_SHA: ${{ needs.marker.outputs.marker_sha }}','ARTIFACT_ID: ${{ needs.prepare.outputs.artifact_id }}','pages-deploy.py deploy','pages-deploy.py verify'):
   self.assertIn(fragment,job('deploy'))
  order=steps(job('deploy'));self.assertLess(next(i for i,l in enumerate(order) if 'deploy.py deploy' in l),next(i for i,l in enumerate(order) if 'deploy.py verify' in l))
 def test_job_outputs_wired(self):
  for fragment in ('pages_commit: ${{ steps.artifact_commit.outputs.pages_commit }}','source_sha: ${{ steps.expect.outputs.source_sha }}','artifact_id: ${{ steps.upload.outputs.artifact_id }}','id: artifact_commit','id: expect','id: upload','echo "pages_commit=$PAGES_COMMIT" >> "$GITHUB_OUTPUT"'):
   self.assertIn(fragment,job('prepare'))
  self.assertIn('marker_sha: ${{ steps.marker.outputs.marker_sha }}',job('marker'))
 def test_deploy_timeout_covers_waits(self):
  self.assertGreaterEqual(int(re.search(r'timeout-minutes: (\d+)',job('deploy'))[1])*60,d.DEPLOY_TIMEOUT+d.VERIFY_TIMEOUT)
@unittest.skipUnless(shutil.which('git'),'git required')
class MarkerCommit(unittest.TestCase):
 def setUp(self):
  self.dir=tempfile.TemporaryDirectory();root=pathlib.Path(self.dir.name)
  self.remote=str(root/'remote.git');self.repo=str(root/'work.git')
  for path in (self.remote,self.repo):d.git('.','init','--quiet','--bare',path)
 def tearDown(self):self.dir.cleanup()
 def record(self,run='7',attempt='1'):return d.provenance(P,S,B,run,attempt)
 def publish(self,record):
  old=d.remote_head(self.repo,self.remote)
  commit=d.make_marker(self.repo,record,old,self.remote)
  d.git(self.repo,*d.push_args(commit,old,self.remote));return commit,old
 def show(self,ref,*args):return d.git(self.remote,*args,ref)
 def test_orphan_marker_has_only_provenance(self):
  commit,old=self.publish(self.record())
  self.assertEqual(old,'');self.assertEqual(d.remote_head(self.repo,self.remote),commit)
  self.assertEqual(self.show(commit,'rev-list','--parents','-n1'),commit)
  self.assertEqual(self.show(commit,'ls-tree','--name-only','-r'),d.MARKER_FILE)
  self.assertEqual(self.show(commit,'log','-1','--format=%s%n%an'),d.MARKER_MESSAGE+'\n'+d.BOT[0])
  self.assertEqual(json.loads(d.git(self.remote,'show',commit+':'+d.MARKER_FILE)),self.record())
  self.assertEqual(d.git(self.remote,'for-each-ref','--format=%(refname)'),d.LOG_REF)
 def test_each_deployment_gets_a_new_fast_forward_commit(self):
  # Pages 108/109: same builder, new artifact. Also a re-run of the same artifact.
  first,_=self.publish(self.record('7','1'));second,old=self.publish(self.record('7','2'));third,_=self.publish(self.record('8','1'))
  self.assertEqual(old,first);self.assertEqual(len({first,second,third}),3)
  self.assertEqual(self.show(third,'rev-list','--count'),'3')
  self.assertNotIn(B,(first,second,third))
 def test_lease_rejects_moved_branch(self):
  first,_=self.publish(self.record('7','1'))
  stale=d.make_marker(self.repo,self.record('9','1'),'')
  with self.assertRaises(ValueError):d.git(self.repo,*d.push_args(stale,'',self.remote))
  self.publish(self.record('8','1'))
  late=d.make_marker(self.repo,self.record('10','1'),first,self.remote)
  with self.assertRaises(ValueError):d.git(self.repo,*d.push_args(late,first,self.remote))
 def test_push_only_targets_log_ref(self):
  args=d.push_args(M,'')
  self.assertEqual(args[-1],M+':refs/heads/pages-deploy-log');self.assertEqual(args[-2],'https://github.com/congminh1254/htkk_builder.git')
  self.assertIn('--force-with-lease=refs/heads/pages-deploy-log:',args);self.assertNotIn('main',' '.join(args))
 def test_auth_header_not_in_arguments(self):
  env=d.auth_env('ghs_secretvalue1234567890');self.assertNotIn('ghs_',' '.join(d.push_args(M,'')))
  self.assertEqual(env['GIT_CONFIG_KEY_0'],'http.https://github.com/.extraheader')
  with self.assertRaises(ValueError):d.auth_env('')
 def test_provenance_rejects_malformed(self):
  for args in [(P[:39],S,B,'7','1'),(P,'x',B,'7','1'),(P,S,B,'0','1'),(P,S,B,'7','')]:
   with self.subTest(args=args),self.assertRaises(ValueError):d.provenance(*args)
 def test_marker_provenance_must_match_run(self):
  d.check_marker(self.record(),self.record())
  with self.assertRaises(ValueError):d.check_marker(self.record('7','2'),self.record())
class Deployment(unittest.TestCase):
 def test_payload_uses_marker_commit(self):
  self.assertEqual(d.payload('13485529962',M,'jwt'),{'artifact_id':13485529962,'pages_build_version':M,'oidc_token':'jwt'})
  for artifact,version,token in [('',M,'jwt'),('0',M,'jwt'),('1',M+'-7-1','jwt'),('1',M,'')]:
   with self.subTest(artifact=artifact,version=version),self.assertRaises(ValueError):d.payload(artifact,version,token)
 def test_deployment_id_like_deploy_pages(self):
  self.assertEqual(d.deployment_id({'id':42},M),'42')
  self.assertEqual(d.deployment_id({'status_url':'https://api.github.com/x/pages/deployments/'+M},'b'*40),M)
  self.assertEqual(d.deployment_id({},M),M)
  with self.assertRaises(ValueError):d.deployment_id({'id':'../x y'},M)
 def test_fallback_only_for_rejected_version(self):
  for code in ('API_HTTP_400','API_HTTP_404','API_HTTP_422'):self.assertTrue(d.fallback_allowed(code))
  for code in ('API_HTTP_401','API_HTTP_403','API_HTTP_500','OIDC','ARTIFACT_ID'):self.assertFalse(d.fallback_allowed(code))
 def test_api_error_is_bounded_and_filtered(self):
  body=json.dumps({'message':'Not Found ghs_abcdefghijklmnopqrstuvwxyz eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJ4In0.sig <script>'+'x'*500,'documentation_url':'https://docs.github.com/rest/pages','token':'SECRET'}).encode()
  text=d.api_error(404,body)
  self.assertTrue(text.startswith('HTTP 404 message=Not Found [redacted] [redacted]'));self.assertIn('documentation_url=https://docs.github.com/rest/pages',text)
  for leak in ('ghs_','eyJ','SECRET','<'):self.assertNotIn(leak,text)
  self.assertLess(len(text),500)
  self.assertEqual(d.api_error(404,b'not json'),'HTTP 404');self.assertEqual(d.api_error(500,b'[1]'),'HTTP 500')
 def test_status_classification(self):
  self.assertTrue(d.classify('succeed'))
  for status in ('deployment_in_progress','syncing_files','updating_pages','purging_cdn','deployment_attempt_error',None):self.assertFalse(d.classify(status))
  for status in d.FAILED:
   with self.subTest(status=status),self.assertRaises(ValueError):d.classify(status)
 def test_wait_success_retry_and_timeout(self):
  clock=Clock();seen=iter([OSError('reset'),'syncing_files','succeed'])
  def status():
   value=next(seen)
   if isinstance(value,Exception):raise value
   return value
  quiet(d.wait_deployment,status,sleep=clock.sleep,clock=clock)
  def broken():raise OSError('reset')
  with self.assertRaises(ValueError) as caught:quiet(d.wait_deployment,broken,sleep=Clock().sleep,clock=Clock())
  self.assertEqual(str(caught.exception),'DEPLOYMENT_STATUS_UNAVAILABLE')
  clock=Clock()
  with self.assertRaises(ValueError) as caught:quiet(d.wait_deployment,lambda:'deployment_in_progress',sleep=clock.sleep,clock=clock)
  self.assertEqual(str(caught.exception),'DEPLOYMENT_TIMEOUT');self.assertLessEqual(clock.now,d.DEPLOY_TIMEOUT)
 def test_retry_bounded(self):
  calls=[]
  def flaky():
   calls.append(1)
   if len(calls)<3:raise OSError('not yet')
   return 'ok'
  self.assertEqual(d.retry(flaky,sleep=lambda s:None),'ok')
  with self.assertRaises(OSError):d.retry(lambda:(_ for _ in ()).throw(OSError('x')),sleep=lambda s:None)
class PublicVerification(unittest.TestCase):
 def body(self,value):return json.dumps({'sourceSha':value,'checks':'passed'}).encode()
 def test_waits_through_stale_cdn_until_artifact_sha(self):
  clock=Clock();bodies=iter([self.body(B),b'<html>',self.body(S)])
  self.assertEqual(quiet(d.wait_public,lambda attempt:next(bodies),S,sleep=clock.sleep,clock=clock),3)
 def test_stale_public_site_fails_after_deadline(self):
  clock=Clock();calls=[]
  def fetch(attempt):calls.append(attempt);return self.body(B)
  with self.assertRaises(ValueError) as caught:quiet(d.wait_public,fetch,S,sleep=clock.sleep,clock=clock)
  self.assertEqual(str(caught.exception),'PUBLIC_SITE_STALE');self.assertEqual(len(calls),d.VERIFY_TIMEOUT//d.POLL+1)
 def test_observed_only_accepts_full_sha(self):
  self.assertEqual(d.observed(self.body(S)),S)
  for body in (b'',b'[]',self.body('F'*40),self.body(S[:7]),self.body(None),b'not json'):
   with self.subTest(body=body):self.assertIsNone(d.observed(body))
 def test_cache_buster_unique_per_probe_on_production_host(self):
  first=d.probe_url(d.SITE,M,1);second=d.probe_url(d.SITE,M,2)
  self.assertTrue(first.startswith('https://hotrokekhai.net/build.json?'));self.assertNotEqual(first,second)
 def test_logs_only_shas(self):
  out=io.StringIO();clock=Clock();bodies=iter([json.dumps({'sourceSha':B,'secret':'PRIVATE-VALUE'}).encode(),self.body(S)])
  with contextlib.redirect_stdout(out):d.wait_public(lambda attempt:next(bodies),S,sleep=clock.sleep,clock=clock)
  self.assertNotIn('PRIVATE-VALUE',out.getvalue())
  for line in out.getvalue().splitlines():self.assertRegex(line,r'^Public build\.json sourceSha: ([0-9a-f]{40}|unavailable) \(expected [0-9a-f]{40}\)$')
if __name__=='__main__':unittest.main()
