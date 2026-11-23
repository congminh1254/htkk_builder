"""Offline authorization boundary tests; no API calls or private checkout."""
import importlib.util,os,unittest,tempfile,pathlib,subprocess,sys
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('validate',os.path.join(os.path.dirname(__file__),'validate.py'))
validate=importlib.util.module_from_spec(spec);spec.loader.exec_module(validate)
MAIN='a'*40
PR='b'*40
class AuthorizationTests(unittest.TestCase):
 def request(self,mode='ci',sha=PR,number='8',fork=False,state='open',head=PR):
  def get(path):
   if path=='branches/main':return {'commit':{'sha':MAIN}}
   return {'state':state,'base':{'ref':'main'},'head':{'sha':head,'repo':{'full_name':'attacker/fork' if fork else validate.REPO}}}
  with patch.dict(os.environ,{'COMMIT_SHA':sha,'BUILD_MODE':mode,'PR_NUMBER':number}),patch.object(validate,'get',get):validate.main()
 def test_release_current_main_allowed(self):self.request(mode='release',sha=MAIN)
 def test_ci_internal_open_pr_allowed(self):self.request()
 def test_release_pr_head_rejected(self):
  with self.assertRaises(ValueError):self.request(mode='release')
 def test_fork_rejected(self):
  with self.assertRaises(ValueError):self.request(fork=True)
 def test_closed_pr_rejected(self):
  with self.assertRaises(ValueError):self.request(state='closed')
 def test_stale_pr_head_rejected(self):
  with self.assertRaises(ValueError):self.request(head='c'*40)
 def test_invalid_inputs_rejected(self):
  for args in ({'sha':'$(bad)'},{'mode':'publish'},{'number':'1; bad'}):
   with self.subTest(args=args),self.assertRaises(ValueError):self.request(**args)
class PrivateLogTests(unittest.TestCase):
 @unittest.skipIf(os.name == 'nt', 'POSIX build subprocess fixture; exercised by Linux build workflow')
 def test_failed_build_hides_diagnostics_and_strips_tokens(self):
  with tempfile.TemporaryDirectory() as temporary:
   root=pathlib.Path(temporary);(root/'source').mkdir();(root/'bin').mkdir()
   npm=root/'bin/npm'
   npm.write_text('#!/bin/sh\n/usr/bin/env > "$HOME/child-env"\necho "PRIVATE SOURCE DIAGNOSTIC" >&2\nexit 1\n');npm.chmod(0o700)
   env={'PATH':str(root/'bin')+':/usr/bin','HOME':temporary,'RUNNER_TEMP':temporary,'BUILD_MODE':'release','SOURCE_PUBLISH_TOKEN':'synthetic-do-not-leak','GITHUB_TOKEN':'synthetic-other-secret'}
   result=subprocess.run([sys.executable,str(pathlib.Path(__file__).with_name('build.py').resolve())],cwd=root,env=env,text=True,capture_output=True)
   self.assertNotEqual(result.returncode,0)
   self.assertNotIn('PRIVATE SOURCE DIAGNOSTIC',result.stdout+result.stderr)
   self.assertIn('PRIVATE SOURCE DIAGNOSTIC',(root/'htkk-builder-log.txt').read_text())
   child=(root/'child-env').read_text()
   self.assertNotIn('TOKEN',child);self.assertNotIn('synthetic-do-not-leak',child)
 @unittest.skipIf(os.name == 'nt', 'POSIX build subprocess fixture; exercised by Linux build workflow')
 def test_e2e_timings_are_numbers_only(self):
  import json
  report={'stats':{'duration':123456},'suites':[{'title':'PRIVATE SUITE','specs':[
   {'title':'PRIVATE TITLE a','file':'b.spec.ts','line':7,'ok':True,'tests':[{'results':[{'status':'passed','duration':4200}]}]},
   {'title':'PRIVATE TITLE b','file':'a.spec.ts','line':44,'ok':False,'tests':[{'results':[{'status':'timedOut','duration':61000,'errors':[{'message':'PRIVATE ERROR','location':{'file':'/src/tests/e2e/a.spec.ts','line':71}}]}]}]},
   {'title':'PRIVATE TITLE c','file':'b.spec.ts','line':9,'ok':True,'tests':[{'results':[{'status':'skipped','duration':0}]}]}]}]}
  for failing in (False,True):
   with self.subTest(failing=failing),tempfile.TemporaryDirectory() as temporary:
    root=pathlib.Path(temporary);(root/'source/tests/e2e').mkdir(parents=True);(root/'bin').mkdir()
    for name in ('a.spec.ts','b.spec.ts'):(root/'source/tests/e2e'/name).write_text('')
    (root/'report.json').write_text(json.dumps(report))
    npm=root/'bin/npm'
    npm.write_text('#!/bin/sh\necho "PRIVATE SOURCE DIAGNOSTIC"\nif [ "$2" = "test:e2e" ]; then cp "%s" "$PLAYWRIGHT_JSON_OUTPUT_NAME"; exit %d; fi\nexit 0\n'%(root/'report.json',1 if failing else 0));npm.chmod(0o700)
    chrome=root/'bin/google-chrome';chrome.write_text('#!/bin/sh\nexit 0\n');chrome.chmod(0o700)
    env={'PATH':str(root/'bin')+':/usr/bin:/bin','HOME':temporary,'RUNNER_TEMP':temporary,'BUILD_MODE':'ci'}
    result=subprocess.run([sys.executable,str(pathlib.Path(__file__).with_name('build.py').resolve())],cwd=root,env=env,text=True,capture_output=True)
    out=result.stdout+result.stderr
    self.assertEqual(result.returncode!=0,failing)
    self.assertRegex(out,r'stage seconds: install=\d+,typecheck=\d+,unit=\d+,schemas=\d+,audit=\d+,build=\d+,e2e=\d+')
    self.assertIn('e2e seconds=123 tests=2 slowest=0:44=61,1:7=4 timedout=0:44',out)
    if failing:self.assertIn('e2e failures (spec index:line): 0:44@71',out)
    self.assertNotIn('PRIVATE',out)
if __name__=='__main__':unittest.main()
