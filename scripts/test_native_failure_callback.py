"""Failure cannot authorize success, arbitrary endpoints or untrusted execution."""
import importlib.util,pathlib,unittest
ROOT=pathlib.Path(__file__).parent
spec=importlib.util.spec_from_file_location('native_failure',ROOT/'report-native-failure.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
class FailureCallbackTests(unittest.TestCase):
 def env(self):return {'GITHUB_REPOSITORY':f.callback.dispatch.BUILDER,'GITHUB_REF':'refs/heads/main','READINESS_RESULT':'failure','GUI_AUTOMATION':'gtgt-web-import-inspect','COMMIT_SHA':'a'*40,'GITHUB_RUN_ID':'123','GITHUB_SERVER_URL':'https://github.com','WEB_CASE_ID':'01GTGT-zero-M10-2026'}
 def test_all_fixed_cases_only_publish_failure(self):
  for case in f.callback.dispatch.CASES:
   with self.subTest(case=case):
    e=self.env();e.update(WEB_CASE_ID=case,PROBE_RESULT='success',SAMPLE_STATE='success');url,p=f.request(e);self.assertEqual(url,'https://api.github.com/repos/htkk-net/htkk_web/statuses/'+'a'*40);self.assertEqual(p['state'],'failure');self.assertEqual(p['context'],f.callback.dispatch.CONTEXTS[case]);self.assertTrue(p['target_url'].endswith('/actions/runs/123'))
 def test_no_success_downgrade_on_successful_or_pending_job(self):
  for result in ['success','pending','skipped','',None]:
   with self.subTest(result=result):
    e=self.env();e['READINESS_RESULT']=result
    with self.assertRaises(ValueError):f.request(e)
 def test_cancellation_can_only_report_failure(self):
  e=self.env();e['READINESS_RESULT']='cancelled';self.assertEqual(f.request(e)[1]['state'],'failure')
 def test_forks_other_branches_modes_cases_and_endpoints_rejected(self):
  for key,value in [('GITHUB_REPOSITORY','attacker/fork'),('GITHUB_REF','refs/heads/test'),('GUI_AUTOMATION','profile-save'),('WEB_CASE_ID','private-input'),('GITHUB_SERVER_URL','https://attacker.example'),('GITHUB_RUN_ID','123?token=secret'),('COMMIT_SHA','a'*39),('GITHUB_RUN_ID','0')]:
   with self.subTest(field=key):
    e=self.env();e[key]=value
    with self.assertRaises(ValueError):f.request(e)
if __name__=='__main__':unittest.main()
