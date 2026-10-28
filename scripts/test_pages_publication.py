"""Adversarial provenance and static-output tests for public Pages hosting."""
import importlib.util,pathlib,tempfile,unittest
spec=importlib.util.spec_from_file_location('pages',pathlib.Path(__file__).with_name('validate-pages.py'));p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
class PagesTests(unittest.TestCase):
 def setUp(self):
  self.source='a'*40;self.artifact='b'*40;self.builder='c'*40
  self.metadata={'sourceSha':self.source,'checks':'passed','builderRepository':p.BUILDER,'builderRunId':'123'}
  self.run={'id':123,'repository':{'full_name':p.BUILDER},'path':'.github/workflows/build.yml','head_branch':'main','head_sha':self.builder,'event':'workflow_dispatch','display_title':'HTKK release','status':'completed','conclusion':'success'}
 def validate(self):return p.validate(self.metadata,{'sourceSha':self.source},self.source,self.artifact,self.artifact,self.run)
 def test_exact_verified_release(self):self.assertEqual(self.validate(),self.source)
 def test_stale_source_rejected(self):
  self.metadata['sourceSha']='d'*40
  with self.assertRaises(ValueError):self.validate()
 def test_artifact_substitution_rejected(self):
  with self.assertRaises(ValueError):p.validate(self.metadata,{'sourceSha':self.source},self.source,'d'*40,self.artifact,self.run)
 def test_untrusted_builder_rejected(self):
  self.metadata['builderRepository']='attacker/fork'
  with self.assertRaises(ValueError):self.validate()
 def test_failed_pending_ci_fork_wrong_workflow_rejected(self):
  for field,value in [('conclusion','failure'),('status','in_progress'),('display_title','HTKK ci'),('head_branch','other'),('path','.github/workflows/other.yml'),('event','pull_request'),('id',124)]:
   with self.subTest(field=field):
    original=self.run[field];self.run[field]=value
    with self.assertRaises(ValueError):self.validate()
    self.run[field]=original
 def statuses(self):return [{'context':c,'state':'success','target_url':'https://github.com/'+p.BUILDER+'/actions/runs/9'}for c in p.CONTEXTS]
 def native(self,repo,path):return {'path':'.github/workflows/probe-htkk-windows.yml','head_branch':'main','head_sha':self.builder,'status':'completed','conclusion':'success'}
 def test_all_thirteen_native_workflows_required(self):
  self.assertTrue(p.native_ready(self.statuses(),self.builder,self.native))
  self.assertFalse(p.native_ready(self.statuses()[:-1],self.builder,self.native))
 def test_latest_native_failure_overrides_previous_success(self):
  values=self.statuses();values.insert(0,{**values[0],'state':'failure'})
  with self.assertRaises(ValueError):p.native_ready(values,self.builder,self.native)
 def test_latest_pending_waits_for_retry(self):
  values=self.statuses();values.insert(0,{**values[0],'state':'pending'})
  self.assertFalse(p.native_ready(values,self.builder,self.native))
 def test_spoofed_callback_url_rejected(self):
  values=self.statuses();values[0]['target_url']='https://github.com/attacker/fork/actions/runs/9'
  with self.assertRaises(ValueError):p.native_ready(values,self.builder,self.native)
 def test_other_builder_revision_rejected(self):
  with self.assertRaises(ValueError):p.native_ready(self.statuses(),'d'*40,self.native)
 def test_success_callback_waits_for_native_post_steps(self):
  def active(repo,path):return {**self.native(repo,path),'status':'in_progress','conclusion':None}
  self.assertFalse(p.native_ready(self.statuses(),self.builder,active))
 def test_success_callback_does_not_hide_failed_whole_workflow(self):
  def failed(repo,path):return {**self.native(repo,path),'conclusion':'failure'}
  with self.assertRaises(ValueError):p.native_ready(self.statuses(),self.builder,failed)
 def test_active_foreign_builder_is_rejected_instead_of_waited(self):
  def foreign(repo,path):return {**self.native(repo,path),'status':'in_progress','conclusion':None,'head_sha':'d'*40}
  with self.assertRaises(ValueError):p.native_ready(self.statuses(),self.builder,foreign)
 def tree(self,root):
  (root/'dashboard').mkdir();(root/'dashboard/index.html').write_text('dashboard');(root/'index.html').write_text('home');(root/'CNAME').write_text('hotrokekhai.net\n')
 def test_static_only_site(self):
  with tempfile.TemporaryDirectory() as directory:
   root=pathlib.Path(directory);self.tree(root);p.static_tree(root)
 def test_source_maps_source_and_retired_downloads_rejected(self):
  for name in ('main.js.map','private.ts','worker.py','downloads'):
   with self.subTest(name=name),tempfile.TemporaryDirectory() as directory:
    root=pathlib.Path(directory);self.tree(root);(root/name).write_text('not public')
    with self.assertRaises(ValueError):p.static_tree(root)
 def test_symlink_rejected(self):
  with tempfile.TemporaryDirectory() as directory:
   root=pathlib.Path(directory);self.tree(root);(root/'leak').symlink_to('/etc/passwd')
   with self.assertRaises(ValueError):p.static_tree(root)
 def test_wrong_domain_rejected(self):
  with tempfile.TemporaryDirectory() as directory:
   root=pathlib.Path(directory);self.tree(root);(root/'CNAME').write_text('other.example')
   with self.assertRaises(ValueError):p.static_tree(root)
if __name__=='__main__':unittest.main()
