"""Offline contract tests: every Pages release gets a unique deployment and is proven live."""
import importlib.util,json,pathlib,re,unittest
spec=importlib.util.spec_from_file_location('deploy_pages',pathlib.Path(__file__).with_name('deploy-pages.py'));d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
WORKFLOW=(pathlib.Path(__file__).parent.parent/'.github/workflows/pages.yml').read_text()
class Clock:
 def __init__(self):self.now=0.0
 def __call__(self):return self.now
 def sleep(self,seconds):self.now+=seconds
def steps():
 return [line.strip() for line in WORKFLOW.splitlines() if line.strip().startswith(('- name:','- uses:','uses:','run:'))]
def index(fragment):
 for position,line in enumerate(steps()):
  if fragment in line:return position
 raise AssertionError(fragment)
class WorkflowContract(unittest.TestCase):
 def test_builder_sha_deploy_action_not_used(self):
  self.assertNotIn('actions/deploy-pages',re.sub(r'#.*','',WORKFLOW))
 def test_deploy_uses_uploaded_artifact_id_and_workflow_token(self):
  self.assertIn('id: artifact',WORKFLOW)
  self.assertIn('ARTIFACT_ID: ${{ steps.artifact.outputs.artifact_id }}',WORKFLOW)
  self.assertIn('python3 builder/scripts/deploy-pages.py deploy',WORKFLOW)
  block=WORKFLOW.split('Deploy with artifact-unique build version')[1].split('- name:')[0]
  self.assertIn('GH_TOKEN: ${{ github.token }}',block);self.assertNotIn('secrets.',block)
 def test_gates_run_before_upload_and_deploy_then_public_verification(self):
  order=[index('validate-pages.py'),index('deploy-pages.py expect'),index('upload-pages-artifact'),index('rm -rf output'),index('deploy-pages.py deploy'),index('deploy-pages.py verify')]
  self.assertEqual(order,sorted(order))
 def test_existing_security_gates_and_minimal_permissions_kept(self):
  for fragment in ("github.ref == 'refs/heads/main'","github.event.workflow_run.conclusion == 'success'","display_title == 'HTKK release'","repository.full_name == 'congminh1254/htkk_builder'",'persist-credentials: false','EXPECTED_BUILD_RUN','name: github-pages','url: ${{ steps.deployment.outputs.page_url }}','cancel-in-progress: false'):
   self.assertIn(fragment,WORKFLOW)
  job=WORKFLOW.split('permissions:')[2].split('environment:')[0]
  self.assertEqual(sorted(l.strip() for l in job.splitlines() if l.strip()),['actions: read','contents: read','id-token: write','pages: write'])
  self.assertEqual(WORKFLOW.split('permissions:')[1].split('concurrency:')[0].strip(),'contents: read')
 def test_private_output_removed_even_on_failure(self):
  block=WORKFLOW.split('Remove local private artifact')[1].split('- name:')[0]
  self.assertIn('if: always()',block);self.assertIn('rm -rf output',block)
 def test_job_timeout_covers_both_bounded_waits(self):
  self.assertGreaterEqual(int(re.search(r'timeout-minutes: (\d+)',WORKFLOW)[1])*60,d.DEPLOY_TIMEOUT+d.VERIFY_TIMEOUT)
class DeploymentVersion(unittest.TestCase):
 def setUp(self):self.artifact='8'*40;self.other='5'*40
 def test_version_bound_to_artifact_and_attempt(self):
  self.assertEqual(d.build_version(self.artifact,'42179175364','1'),self.artifact+'-42179175364-1')
 def test_new_artifact_on_same_builder_gets_new_version(self):
  self.assertNotEqual(d.build_version(self.artifact,'7','1'),d.build_version(self.other,'7','1'))
 def test_retry_of_same_artifact_gets_new_version(self):
  self.assertNotEqual(d.build_version(self.artifact,'7','1'),d.build_version(self.artifact,'7','2'))
  self.assertNotEqual(d.build_version(self.artifact,'7','1'),d.build_version(self.artifact,'8','1'))
 def test_malformed_inputs_rejected(self):
  for args in [('8'*39,'7','1'),('X'*40,'7','1'),(self.artifact,'0','1'),(self.artifact,'7',''),(self.artifact,'7;x','1'),(None,'7','1')]:
   with self.subTest(args=args),self.assertRaises(ValueError):d.build_version(*args)
 def test_payload_shape(self):
  version=d.build_version(self.artifact,'7','1')
  self.assertEqual(d.payload('123',version,'jwt'),{'artifact_id':123,'pages_build_version':version,'oidc_token':'jwt'})
  for artifact,token in [('','jwt'),('0','jwt'),('12a','jwt'),('123','')]:
   with self.subTest(artifact=artifact),self.assertRaises(ValueError):d.payload(artifact,version,token)
class DeploymentStatus(unittest.TestCase):
 def test_success_failure_and_pending(self):
  self.assertTrue(d.classify('succeed'))
  for status in ('deployment_in_progress','syncing_files','updating_pages','purging_cdn','deployment_attempt_error',None):self.assertFalse(d.classify(status))
  for status in d.FAILED:
   with self.subTest(status=status),self.assertRaises(ValueError):d.classify(status)
 def test_wait_until_success(self):
  clock=Clock();seen=iter(['deployment_in_progress','syncing_files','succeed'])
  d.wait_deployment(lambda:next(seen),sleep=clock.sleep,clock=clock);self.assertEqual(clock.now,60)
 def test_transient_status_errors_retried_then_bounded(self):
  clock=Clock();seen=iter([OSError('reset'),'syncing_files','succeed'])
  def status():
   value=next(seen)
   if isinstance(value,Exception):raise value
   return value
  d.wait_deployment(status,sleep=clock.sleep,clock=clock)
  def broken():raise OSError('reset')
  with self.assertRaises(ValueError) as caught:d.wait_deployment(broken,sleep=Clock().sleep,clock=Clock())
  self.assertEqual(str(caught.exception),'DEPLOYMENT_STATUS_UNAVAILABLE')
 def test_bounded_wait_fails(self):
  clock=Clock()
  with self.assertRaises(ValueError) as caught:d.wait_deployment(lambda:'deployment_in_progress',sleep=clock.sleep,clock=clock)
  self.assertEqual(str(caught.exception),'DEPLOYMENT_TIMEOUT');self.assertLessEqual(clock.now,d.DEPLOY_TIMEOUT)
class PublicVerification(unittest.TestCase):
 def setUp(self):self.expected='f'*40;self.previous='5'*40
 def body(self,value):return json.dumps({'sourceSha':value,'checks':'passed'}).encode()
 def test_waits_through_stale_cdn_until_artifact_sha(self):
  clock=Clock();bodies=iter([self.body(self.previous),b'<html>',self.body(self.expected)])
  self.assertEqual(d.wait_public(lambda attempt:next(bodies),self.expected,sleep=clock.sleep,clock=clock),3)
 def test_stale_public_site_fails_after_deadline(self):
  # The incident: deployment reported success but the site kept the previous release.
  clock=Clock();calls=[]
  def fetch(attempt):calls.append(attempt);return self.body(self.previous)
  with self.assertRaises(ValueError) as caught:d.wait_public(fetch,self.expected,sleep=clock.sleep,clock=clock)
  self.assertEqual(str(caught.exception),'PUBLIC_SITE_STALE');self.assertLessEqual(clock.now,d.VERIFY_TIMEOUT)
  self.assertEqual(len(calls),d.VERIFY_TIMEOUT//d.POLL+1)
 def test_fetch_errors_keep_polling_then_fail(self):
  clock=Clock()
  def fetch(attempt):raise OSError('reset')
  with self.assertRaises(ValueError):d.wait_public(fetch,self.expected,sleep=clock.sleep,clock=clock)
 def test_observed_only_accepts_full_sha(self):
  self.assertEqual(d.observed(self.body(self.expected)),self.expected)
  for body in (b'',b'[]',b'{"sourceSha":"F'+b'F'*39+b'"}',self.body(self.expected[:7]),self.body(None),b'not json'):
   with self.subTest(body=body):self.assertIsNone(d.observed(body))
 def test_expected_must_be_sha(self):
  with self.assertRaises(ValueError):d.wait_public(lambda attempt:b'',"abc",sleep=lambda s:None,clock=lambda:0)
 def test_cache_buster_is_unique_per_probe_on_production_host(self):
  version=d.build_version(self.expected,'7','1')
  first=d.probe_url(d.SITE,version,1);second=d.probe_url(d.SITE,version,2)
  self.assertTrue(first.startswith('https://hotrokekhai.net/build.json?'));self.assertNotEqual(first,second);self.assertIn(version,first)
 def test_logs_only_shas(self):
  import contextlib,io
  out=io.StringIO();clock=Clock();bodies=iter([json.dumps({'sourceSha':self.previous,'secret':'PRIVATE-VALUE'}).encode(),self.body(self.expected)])
  with contextlib.redirect_stdout(out):d.wait_public(lambda attempt:next(bodies),self.expected,sleep=clock.sleep,clock=clock)
  self.assertNotIn('PRIVATE-VALUE',out.getvalue())
  for line in out.getvalue().splitlines():self.assertRegex(line,r'^Public build\.json sourceSha: ([0-9a-f]{40}|unavailable) \(expected [0-9a-f]{40}\)$')
if __name__=='__main__':unittest.main()
