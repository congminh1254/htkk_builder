"""The callback guard reads only the branch ref, never the full commit (whose files list can exceed the size cap)."""
import importlib.util,pathlib,unittest
spec=importlib.util.spec_from_file_location('callback_guard',pathlib.Path(__file__).with_name('callback_guard.py'));guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
SOURCE='a'*40
class GuardRefTests(unittest.TestCase):
 def test_reads_branch_ref_not_commit(self):
  paths=[]
  def get(repo,path,token):
   paths.append(path)
   if path=='git/ref/heads/main':return {'object':{'sha':SOURCE}}
   if path.startswith('actions/runs/'):return {'run_attempt':1}
   return []
  self.assertTrue(guard.allowed(SOURCE,'htkk-native/zero',5,1,'t','t',get=get))
  self.assertEqual(paths[0],'git/ref/heads/main')
  self.assertNotIn('commits/main',paths)
 def test_superseded_main_is_ignored(self):
  get=lambda repo,path,token:{'object':{'sha':'b'*40}} if path=='git/ref/heads/main' else {}
  self.assertFalse(guard.allowed(SOURCE,'htkk-native/zero',5,1,'t','t',get=get))
if __name__=='__main__':unittest.main()
