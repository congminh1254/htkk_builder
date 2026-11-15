"""Offline contract of the 01-6/GTGT (ĐTVT) web->HTKK case (oracle HTKK 5.8.2). Synthetic XML built from the
trusted contract; passing these tests is never native evidence."""
import copy,importlib.util,json,pathlib,unittest
import xml.etree.ElementTree as ET
ROOT=pathlib.Path(__file__).parent
def load(name,file):
 spec=importlib.util.spec_from_file_location(name,ROOT/file);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
cases=load('annex16_cases_registry','htkk_native_cases.py')
contract=load('annex16_cases_contract','htkk_annex16_cssx_web_cases.py')
web=load('annex16_cases_web_fixture','test_htkk_web_input.py');w=web.w
out=load('annex16_cases_native_fixture','test_htkk_web_native_output.py');n=out.n
CASES=(contract.DVVT_CASE,);NS='{'+contract.NS+'}'
def edited(body,edit):
 root=ET.fromstring(body.decode('utf-8'));edit(root);ET.register_namespace('',contract.NS)
 return (w.PREAMBLE+ET.tostring(root,encoding='unicode')).encode('utf-8')

class Registry(unittest.TestCase):
 def test_two_non_gating_5_8_2_cases_with_own_producer_and_contexts(self):
  self.assertEqual(cases.ANNEX16_DVVT_CASES,CASES);self.assertEqual(cases.ANNEX16_CASES[-1:],CASES)
  for case,producer_case in zip(CASES,('annex16-dvvt',)):
   c=cases.CASES[case];a=cases.ADAPTERS[c['adapterId']]
   self.assertIs(c['releaseGate'],False);self.assertEqual(cases.htkk_version(case),'5.8.2');self.assertEqual(c['producerCase'],producer_case)
   self.assertEqual(cases.status_context(case),'htkk-native/'+producer_case+'@htkk582')
   self.assertEqual((a['producer'],a['driver'],a['privacyValidator'],a['htkkVersion']),('scripts/generate-htkk-web-annex16-dvvt-reference.mjs','gtgt-web-import-inspect','gtgt-annex16-dvvt-v1','5.8.1'))
   self.assertEqual(c['unit'],{'menuId':'D1','adapterVersion':'2.8.3','periodType':'month','periodValue':'10/2026','activityCode':'00','annexes':['01-6/GTGT (ĐTVT)'],'amendmentOrder':0})
   self.assertNotIn(case,cases.GATE_CASES)

class InputContract(unittest.TestCase):
 def test_exact_fixture_and_manifest_pass(self):
  for case in CASES:
   with self.subTest(case=case):
    body=web.annex16_fixture(case);manifest=web.case_manifest(body,case)
    self.assertEqual(w.validate_manifest(json.dumps(manifest).encode()),manifest)
    self.assertEqual(w.validate_web_xml(body,case_id=case,manifest=manifest)['annexTaxLeafCount'],131)
    self.assertEqual(manifest['expectedAnnexLeaves'][2],['Pluc_01_6_GTGT_DVVT/ct06',contract.CASES[case]['head'][2],''])
 def test_any_changed_amount_row_id_or_name_is_refused(self):
  body=web.annex16_fixture(contract.DVVT_CASE)
  def amount(root):root.find('.//'+NS+'ct17').text='4000002'
  def extra(root):annex=root.find('.//'+NS+'Pluc_01_6_GTGT_DVVT');annex.insert(5,copy.deepcopy(annex[4]))
  def ident(root):root.find('.//'+NS+'cong_ct18').set('id','ID_3')
  def main(root):root.find('.//'+NS+'ct33').text='60000001'
  def name(root):root.find('.//'+NS+'ct09').text='TEN THAT CUA DOANH NGHIEP'
  def total(root):root.find('.//'+NS+'ct24').text='1'
  for edit in (amount,extra,ident,main,name,total):
   with self.subTest(edit=edit.__name__),self.assertRaises(w.InputError):w.validate_web_xml(edited(body,edit),case_id=contract.DVVT_CASE)
 def test_cases_do_not_accept_each_other(self):
  with self.assertRaises(w.InputError):w.validate_web_xml(web.annex16_fixture(contract.RATIO_CASE),case_id=contract.DVVT_CASE)

class NativeOutput(unittest.TestCase):
 def test_reexport_exact_and_baseline_is_the_zero_main_declaration(self):
  for case in CASES:
   with self.subTest(case=case):
    web_body,native,_,_=out.fixture(case)
    self.assertEqual(n.validate_native(native,case,out.TODAY)['leafCount'],74)
    self.assertEqual(n.compare_tax(web_body,native,case)['checkedTaxLeafCount'],131)
    baseline=out.annex16_baseline(case)
    self.assertEqual(n.validate_native(baseline,case,out.TODAY,initial=True,aligned=True)['leafCount'],74)
    self.assertFalse(n.baseline_matches_input(case))
    with self.assertRaises((n.OutputError,n.privacy.EvidenceError)):n.validate_native(native,case,out.TODAY,initial=True,aligned=True)
    with self.assertRaises(n.OutputError):n.validate_native(baseline,case,out.TODAY)

class Driver(unittest.TestCase):
 def test_restore_switches_sheet_and_code_columns_for_the_dvvt_case(self):
  source=(ROOT/'HtkkGtgtRoundtripInspection.cs').read_text(encoding='utf-8')
  for text in ('private string Annex16SheetId{get{return Annex16DvvtWebCaseId()?"01_6_2":"01_6";}}','private int Annex16ColumnK{get{return Annex16DvvtWebCaseId()?11:10;}}',
               'private int Annex16ColumnU{get{return Annex16DvvtWebCaseId()?19:20;}}','if(name==Annex16SheetId||name==Annex16SheetName)'):self.assertIn(text,source)
  reference=(ROOT/'HtkkWebInputReference.cs').read_text(encoding='utf-8')
  self.assertIn('private const string Annex16DvvtCaseId="'+contract.DVVT_CASE+'";',reference)
  values=json.loads((ROOT/'htkk-native-automation-registry.json').read_text())['resultFields']['webCaseId']['values'];self.assertIn(contract.DVVT_CASE,values)

if __name__=='__main__':unittest.main()
