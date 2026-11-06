"""Offline contracts: no silent duplicate Pages deployment, and every deploy is proven live."""
import contextlib,importlib.util,io,json,pathlib,re,unittest
spec=importlib.util.spec_from_file_location('pages_release_check',pathlib.Path(__file__).with_name('pages-release-check.py'));c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
WORKFLOW=(pathlib.Path(__file__).parent.parent/'.github/workflows/pages.yml').read_text()
class Clock:
 def __init__(self):self.now=0.0
 def __call__(self):return self.now
 def sleep(self,seconds):self.now+=seconds
def index(fragment):
 lines=[l.strip() for l in WORKFLOW.splitlines() if l.strip().startswith(('- name:','- uses:','uses:','run:'))]
 for position,line in enumerate(lines):
  if fragment in line:return position
 raise AssertionError(fragment)
def quiet(function,*args,**kwargs):
 with contextlib.redirect_stdout(io.StringIO()):return function(*args,**kwargs)
class WorkflowContract(unittest.TestCase):
 def test_deploy_pages_pinned_by_full_sha(self):
  uses=re.findall(r'uses: actions/deploy-pages@(\S+)',WORKFLOW)
  self.assertEqual(len(uses),1);self.assertRegex(uses[0],'^[0-9a-f]{40}$')
 def test_no_rest_deployment_with_invented_version(self):
  # Run 42183141113: a non-commit pages_build_version is rejected with HTTP 404.
  self.assertNotIn('pages/deployments',WORKFLOW);self.assertNotIn('pages_build_version',WORKFLOW)
  self.assertNotIn('pages/deployments',(pathlib.Path(__file__).with_name('pages-release-check.py')).read_text().split('"""',2)[2])
 def test_order_guard_validate_upload_deploy_verify(self):
  order=[index('pages-release-check.py guard'),index('Resolve immutable private artifact'),index('validate-pages.py'),index('pages-release-check.py expect'),index('upload-pages-artifact'),index('rm -rf output'),index('actions/deploy-pages@'),index('pages-release-check.py verify')]
  self.assertEqual(order,sorted(order))
 def test_guard_uses_workflow_token_only(self):
  block=WORKFLOW.split('Refuse builder SHA already used')[1].split('- name:')[0]
  self.assertIn('GH_TOKEN: ${{ github.token }}',block);self.assertNotIn('secrets.',block)
  verify=WORKFLOW.split('Verify public site serves this artifact')[1]
  self.assertNotIn('secrets.',verify);self.assertNotIn('TOKEN',verify)
 def test_existing_gates_and_minimal_permissions_kept(self):
  for fragment in ("github.ref == 'refs/heads/main'","github.event.workflow_run.conclusion == 'success'","display_title == 'HTKK release'","repository.full_name == 'congminh1254/htkk_builder'",'persist-credentials: false','EXPECTED_BUILD_RUN','name: github-pages','url: ${{ steps.deployment.outputs.page_url }}','cancel-in-progress: false','id: deployment'):
   self.assertIn(fragment,WORKFLOW)
  job=WORKFLOW.split('permissions:')[2].split('environment:')[0]
  self.assertEqual(sorted(l.strip() for l in job.splitlines() if l.strip()),['actions: read','contents: read','id-token: write','pages: write'])
  self.assertEqual(WORKFLOW.split('permissions:')[1].split('concurrency:')[0].strip(),'contents: read')
 def test_private_output_removed_even_on_failure(self):
  block=WORKFLOW.split('Remove local private artifact')[1].split('- name:')[0]
  self.assertIn('if: always()',block);self.assertIn('rm -rf output',block)
 def test_job_timeout_covers_verification(self):
  self.assertGreaterEqual(int(re.search(r'timeout-minutes: (\d+)',WORKFLOW)[1])*60,c.VERIFY_TIMEOUT+600)
class BuilderShaGuard(unittest.TestCase):
 def setUp(self):self.builder='5'*40
 def run_(self,id,**fields):return {'id':id,'head_sha':self.builder,'path':'.github/workflows/pages.yml','head_branch':'main','status':'completed','conclusion':'success',**fields}
 def test_incident_second_release_on_same_builder_is_refused(self):
  # Pages 108 then 109 on builder 53b7a6b: the second must fail loudly, not "succeed".
  self.assertEqual(c.previous_deployments([self.run_(108),self.run_(109)],self.builder,'109'),[108])
 def test_first_deploy_and_retry_after_failure_allowed(self):
  self.assertEqual(c.previous_deployments([],self.builder,'7'),[])
  self.assertEqual(c.previous_deployments([self.run_(7)],self.builder,'7'),[])
  for field,value in [('conclusion','failure'),('conclusion','cancelled'),('status','in_progress'),('head_sha','6'*40),('head_branch','other'),('path','.github/workflows/build.yml')]:
   with self.subTest(field=field):self.assertEqual(c.previous_deployments([self.run_(6,**{field:value})],self.builder,'7'),[])
 def test_malformed_inputs_rejected(self):
  for args in [([],'5'*39,'7'),([],self.builder,'0'),([],self.builder,'x')]:
   with self.subTest(args=args),self.assertRaises(ValueError):c.previous_deployments(*args)
 def test_message_names_sha_runs_and_remedy_without_marker_commit(self):
  message=c.guard_message(self.builder,[108])
  self.assertIn(self.builder,message);self.assertIn('108',message);self.assertIn('real builder change',message)
  self.assertNotIn('empty',message.lower())
class PublicVerification(unittest.TestCase):
 def setUp(self):self.expected='f'*40;self.previous='5'*40
 def body(self,value):return json.dumps({'sourceSha':value,'checks':'passed'}).encode()
 def test_waits_through_stale_cdn_until_artifact_sha(self):
  clock=Clock();bodies=iter([self.body(self.previous),b'<html>',self.body(self.expected)])
  self.assertEqual(quiet(c.wait_public,lambda attempt:next(bodies),self.expected,sleep=clock.sleep,clock=clock),3)
 def test_stale_public_site_fails_after_deadline(self):
  clock=Clock();calls=[]
  def fetch(attempt):calls.append(attempt);return self.body(self.previous)
  with self.assertRaises(ValueError) as caught:quiet(c.wait_public,fetch,self.expected,sleep=clock.sleep,clock=clock)
  self.assertEqual(str(caught.exception),'PUBLIC_SITE_STALE');self.assertLessEqual(clock.now,c.VERIFY_TIMEOUT)
  self.assertEqual(len(calls),c.VERIFY_TIMEOUT//c.POLL+1)
 def test_fetch_errors_keep_polling_then_fail(self):
  clock=Clock()
  def fetch(attempt):raise OSError('reset')
  with self.assertRaises(ValueError):quiet(c.wait_public,fetch,self.expected,sleep=clock.sleep,clock=clock)
 def test_observed_only_accepts_full_sha(self):
  self.assertEqual(c.observed(self.body(self.expected)),self.expected)
  for body in (b'',b'[]',self.body('F'*40),self.body(self.expected[:7]),self.body(None),b'not json'):
   with self.subTest(body=body):self.assertIsNone(c.observed(body))
 def test_expected_must_be_sha(self):
  with self.assertRaises(ValueError):c.wait_public(lambda attempt:b'','abc',sleep=lambda s:None,clock=lambda:0)
 def test_cache_buster_unique_per_probe_on_production_host(self):
  first=c.probe_url(c.SITE,'x-1',1);second=c.probe_url(c.SITE,'x-1',2)
  self.assertTrue(first.startswith('https://hotrokekhai.net/build.json?'));self.assertNotEqual(first,second)
 def test_logs_only_shas(self):
  out=io.StringIO();clock=Clock();bodies=iter([json.dumps({'sourceSha':self.previous,'secret':'PRIVATE-VALUE'}).encode(),self.body(self.expected)])
  with contextlib.redirect_stdout(out):c.wait_public(lambda attempt:next(bodies),self.expected,sleep=clock.sleep,clock=clock)
  self.assertNotIn('PRIVATE-VALUE',out.getvalue())
  for line in out.getvalue().splitlines():self.assertRegex(line,r'^Public build\.json sourceSha: ([0-9a-f]{40}|unavailable) \(expected [0-9a-f]{40}\)$')
if __name__=='__main__':unittest.main()
