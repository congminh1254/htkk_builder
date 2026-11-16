"""Offline CS0128/CS0136 lint of scripts/*.cs (csharp_local_scopes.py).

Run 43804931601: 623dfb8 declared `bool shown` at method scope of EditDeclarationTickCombo, which already had `string[] shown`
in a nested block. Windows csc refused it (CS0136), so the x86 reference host was not built and all 96 native cases stopped
at readiness; mono mcs, the only compiler offline, accepted it. Passing this lint is not a compilation.
"""
import importlib.util, pathlib, unittest

ROOT = pathlib.Path(__file__).parent
spec = importlib.util.spec_from_file_location('csharp_local_scopes_test', ROOT / 'csharp_local_scopes.py')
lint = importlib.util.module_from_spec(spec); spec.loader.exec_module(lint)

SAMPLE = '''class A {
 void M(int p){
  int a=0,b=1;
  if(a>0){int b2=2;string c="x";}
  for(int i=0;i<3;i++){int c=1;}
  foreach(string s in new string[0])if(s!=null){int a=3;}
  string c=null;
  object k=delegate(int p){return;};
  try{}catch(System.Exception e){int e2=0;}
  int i=5;
 }
 void N(string value){foreach(char x in value)if(x==' ')return;foreach(char x in value)if(x=='/')return;
  for(int j=0;j<2;j++){int t=0;}for(int j=0;j<2;j++){int t=1;}
  string text="//"; // int text=1;
 }
}
'''

# The method of run 43804931601 as 623dfb8 had it (shape only).
SHOWN = '''class B {
 private void EditDeclarationTickCombo(int index){
  object editor=null;
  if(editor!=null){
   object open=null;string[] shown=open==null?null:new string[0];
   if(shown==null){editor=null;}
  }
  int current=0;bool shown=false;
  if(current<0){shown=true;}
 }
}
'''


class LocalScopes(unittest.TestCase):
    def test_every_driver_source_is_clean(self):
        found = []
        for path in sorted(ROOT.glob('*.cs')):
            found += [(path.name,) + x for x in lint.conflicts(path.read_text(encoding='utf-8-sig'))]
        self.assertEqual(found, [])

    def test_reports_the_run_43804931601_shape(self):
        self.assertEqual(lint.conflicts(SHOWN), [('shown', 5, 8)])

    def test_nested_and_later_outer_declarations_conflict_siblings_do_not(self):
        self.assertEqual(sorted(lint.conflicts(SAMPLE)), sorted([('p', 2, 8), ('a', 3, 6), ('c', 4, 7), ('c', 5, 7), ('i', 5, 10)]))

    def test_comments_and_literals_are_ignored(self):
        self.assertEqual(lint.conflicts('class C { void M(){ string t="int t=1;"; /* int t=2; */ } }'), [])
