import copy,importlib.util,json,pathlib,unittest
ROOT=pathlib.Path(__file__).parent
def load(name,file):
 spec=importlib.util.spec_from_file_location(name,ROOT/file);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
design=load('descriptor_native_cases','htkk_descriptor_native_cases.py')
native=load('native_cases_for_descriptor_test','htkk_native_cases.py')
RAW=json.loads((ROOT/'htkk-descriptor-native-cases.json').read_text())
class DescriptorNativeCaseDesign(unittest.TestCase):
 def test_registry_has_zero_and_amount_cases_per_menu(self):
  self.assertEqual(design.CASE_IDS,('05KK-zero-Q3-2026','05KK-withheld-Q3-2026','05QTT-zero-Y2025','05QTT-two-employees-Y2025','02QTT-zero-Y2025','02QTT-dependants-Y2025','01NTNN-zero-M10-2026','01NTNN-two-contractors-M10-2026'))
  self.assertEqual({c['unit']['menuId'] for c in design.DESIGN['cases']},{'L7','B9','B8','I9'})
 def test_design_cannot_be_dispatched_or_gate_a_release(self):
  self.assertFalse(design.DESIGN['dispatchable'])
  # Only reviewed cases are promoted, through the declaration driver and never as a gate.
  promoted=set(design.CASE_IDS)&set(native.CASES)
  self.assertEqual(promoted,{'05KK-withheld-Q3-2026','05QTT-two-employees-Y2025','02QTT-dependants-Y2025','01NTNN-two-contractors-M10-2026'})
  for case in promoted:self.assertEqual(native.driver(case),'declaration-web-import-inspect');self.assertIs(native.CASES[case]['releaseGate'],False)
  workflow=(ROOT.parent/'.github/workflows/probe-htkk-windows.yml').read_text()
  for case in set(design.CASE_IDS)-promoted:self.assertNotIn(case,workflow)
  for mutate in (lambda v:v.__setitem__('dispatchable',True),lambda v:v.__setitem__('status','ready'),lambda v:v['cases'][0].__setitem__('releaseGate',True)):
   value=copy.deepcopy(RAW);mutate(value)
   with self.assertRaises(ValueError):design.validate(value)
 def test_rejects_identity_period_annex_and_privacy_drift(self):
  mutations=[
   lambda v:v['adapters'][0].__setitem__('xmlVersion','2.8.3'),
   lambda v:v['adapters'][1].__setitem__('menuId','B8'),
   lambda v:v['cases'][0]['unit'].__setitem__('periodType','year'),
   lambda v:v['cases'][2]['unit'].__setitem__('periodValue','10/2025'),
   lambda v:v['cases'][3]['unit'].__setitem__('annexes',['01-KHBS']),
   lambda v:v['cases'][1]['expectedLeaves'].__setitem__('ct16','Nguyen Van A'),
   lambda v:v['cases'][1]['expectedLeaves'].__setitem__('mst_cu','0100109106'),
   lambda v:v['cases'][3].pop('expectedRows'),
   lambda v:v['cases'][1]['unit'].__setitem__('amendmentOrder',1),
   lambda v:v.__setitem__('producer','scripts/other.mjs'),
   lambda v:v['cases'].pop(0),
   lambda v:v['cases'][4].__setitem__('caseId',v['cases'][5]['caseId']),
  ]
  for mutate in mutations:
   value=copy.deepcopy(RAW);mutate(value)
   with self.assertRaises(ValueError):design.validate(value)
 def test_expectations_are_hand_computed_from_source_formulas(self):
  cases={c['caseId']:c['expectedLeaves'] for c in design.DESIGN['cases']}
  kk=cases['05KK-withheld-Q3-2026']
  self.assertEqual(int(kk['ct18']),int(kk['ct19'])+int(kk['ct20']))
  self.assertEqual(int(kk['ct21']),int(kk['ct22'])+int(kk['ct23']))
  self.assertEqual(int(kk['ct26']),int(kk['ct27'])+int(kk['ct28']))
  self.assertEqual(int(kk['ct29']),int(kk['ct30'])+int(kk['ct31']))
  self.assertEqual(int(kk['ct32']),int(int(kk['ct24'])*10/100+0.5))
  qtt=cases['05QTT-two-employees-Y2025']
  self.assertEqual(int(qtt['ct41']),max(0,int(qtt['ct36'])+0-int(qtt['ct38'])))
  self.assertEqual(int(cases['02QTT-dependants-Y2025']['ct27']),(6+12)*4400000)
if __name__=='__main__':unittest.main()
