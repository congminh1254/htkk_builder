import copy,importlib.util,json,pathlib,unittest
ROOT=pathlib.Path(__file__).parent
def load(name,file):
 spec=importlib.util.spec_from_file_location(name,ROOT/file);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
design=load('descriptor_native_cases','htkk_descriptor_native_cases.py')
native=load('native_cases_for_descriptor_test','htkk_native_cases.py')
RAW=json.loads((ROOT/'htkk-descriptor-native-cases.json').read_text())
class DescriptorNativeCaseDesign(unittest.TestCase):
 def test_registry_has_zero_and_amount_cases_per_menu(self):
  self.assertEqual(design.CASE_IDS,('05KK-zero-Q3-2026','05KK-withheld-Q3-2026','05QTT-zero-Y2025','05QTT-two-employees-Y2025','02QTT-zero-Y2025','02QTT-dependants-Y2025','01NTNN-zero-M09-2026','01NTNN-two-contractors-M09-2026','01NTNN-NCCNN-zero-M10-2026','01NTNN-NCCNN-two-parts-M10-2026','03NTNN-zero-M10-2026','03NTNN-no-rate-M10-2026','01NTNN-NCCNN-entry-zero-M10-2026','01NTNN-NCCNN-entry-M10-2026','04NTNN-TT80-zero-2026','04NTNN-TT80-one-subcontractor-2026','04NTNN-TT89-one-subcontractor-2026','02NTNN-TT89-two-annexes-2026','02NTNN-TT80-zero-2026','02NTNN-TT80-two-annexes-2026','01NTNN-occurrence-D20-09-2026','01NTNN-NCCNN-occurrence-D20-10-2026','03NTNN-occurrence-D20-10-2026'))
  self.assertEqual({c['unit']['menuId'] for c in design.DESIGN['cases']},{'L7','B9','B8','I9','Y8','J1','D6','Y1','X9','C9'})
 def test_design_cannot_be_dispatched_or_gate_a_release(self):
  self.assertFalse(design.DESIGN['dispatchable'])
  # Only reviewed cases are promoted, through the declaration driver and never as a gate.
  promoted=set(design.CASE_IDS)&set(native.CASES)
  self.assertEqual(promoted,{'05KK-withheld-Q3-2026','05QTT-two-employees-Y2025','02QTT-dependants-Y2025','01NTNN-two-contractors-M09-2026','03NTNN-no-rate-M10-2026','01NTNN-NCCNN-entry-M10-2026','04NTNN-TT80-one-subcontractor-2026','04NTNN-TT89-one-subcontractor-2026','02NTNN-TT89-two-annexes-2026','02NTNN-TT80-two-annexes-2026','01NTNN-occurrence-D20-09-2026','01NTNN-NCCNN-occurrence-D20-10-2026','03NTNN-occurrence-D20-10-2026'})
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
  # 04/NTNN (XLS sheet 01 rows 32-39): [4] = [2] - [3] if positive; [5] = quyết toán - kê khai; [7] = [5] - [6].
  for case in ('04NTNN-TT80-one-subcontractor-2026','04NTNN-TT89-one-subcontractor-2026'):
   c=cases[case];row2,row4=('DThuChuaGomGTGT','DThuTinhThue') if case.startswith('04NTNN-TT80') else ('DThuTinhThue','DThuTinhThueNTNN')
   self.assertEqual(int(c[row4+'/quyetToan']),max(0,int(c[row2+'/quyetToan'])-int(c['DThuNTPhu/quyetToan'])))
   self.assertEqual(int(c['SoThueConPNop/quyetToan']),int(c['SoThueTNDNPNop/chenhLech'])+0)
 def test_04ntnn_range_period_and_no_zero_case_only_for_y1(self):
  bad=[lambda v:v['cases'][-1]['unit'].__setitem__('periodValue','07/2026'),
       lambda v:v['cases'][-1]['unit'].__setitem__('periodValue','01/07/2026-31/13/2026'),
       lambda v:v['cases'][-1]['unit'].__setitem__('periodType','month'),
       # D6 keeps its zero case; only Y1 (Header B42 blocks [5] = 0) is exempt.
       lambda v:v.__setitem__('cases',[c for c in v['cases'] if c['caseId']!='04NTNN-TT80-zero-2026'])]
  for mutate in bad:
   value=copy.deepcopy(RAW);mutate(value)
   with self.assertRaises(ValueError):design.validate(value)
  self.assertEqual(design.NO_ZERO_CASE,{'04-ntnn-tt89-3.0.9','02-ntnn-tt89-3.0.9'})
if __name__=='__main__':unittest.main()
