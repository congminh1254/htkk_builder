"""Offline contract of the two 01-6/GTGT (CSSX) web->HTKK cases (oracle HTKK 5.8.2). Synthetic XML built from the
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
CASES=(contract.FORMULA_CASE,contract.RATIO_CASE);NS='{'+contract.NS+'}'
def edited(body,edit):
 root=ET.fromstring(body.decode('utf-8'));edit(root);ET.register_namespace('',contract.NS)
 return (w.PREAMBLE+ET.tostring(root,encoding='unicode')).encode('utf-8')

class Registry(unittest.TestCase):
 def test_two_non_gating_5_8_2_cases_with_own_producer_and_contexts(self):
  self.assertEqual(cases.ANNEX16_CSSX_CASES,CASES)
  for case,producer_case in zip(CASES,('annex16-cssx-formula','annex16-cssx-ratio')):
   c=cases.CASES[case];a=cases.ADAPTERS[c['adapterId']]
   self.assertIs(c['releaseGate'],False);self.assertEqual(cases.htkk_version(case),'5.8.2');self.assertEqual(c['producerCase'],producer_case)
   self.assertEqual(cases.status_context(case),'htkk-native/'+producer_case+'@htkk582')
   self.assertEqual((a['producer'],a['driver'],a['privacyValidator'],a['htkkVersion']),('scripts/generate-htkk-web-annex16-cssx-reference.mjs','gtgt-web-import-inspect','gtgt-annex16-cssx-v1','5.8.1'))
   self.assertEqual(c['unit'],{'menuId':'D1','adapterVersion':'2.8.3','periodType':'month','periodValue':'10/2026','activityCode':'00','annexes':['01-6/GTGT (CSSX)'],'amendmentOrder':0})
   self.assertNotIn(case,cases.GATE_CASES)

class InputContract(unittest.TestCase):
 def test_exact_fixture_and_manifest_pass(self):
  for case in CASES:
   with self.subTest(case=case):
    body=web.annex16_fixture(case);manifest=web.case_manifest(body,case)
    self.assertEqual(w.validate_manifest(json.dumps(manifest).encode()),manifest)
    self.assertEqual(w.validate_web_xml(body,case_id=case,manifest=manifest)['annexTaxLeafCount'],131)
    self.assertEqual(manifest['expectedAnnexLeaves'][2],['Pluc_01_6_GTGT_CSSX/ct06',contract.CASES[case]['head'][2],''])
 def test_any_changed_amount_row_id_or_name_is_refused(self):
  body=web.annex16_fixture(contract.FORMULA_CASE)
  def amount(root):root.find('.//'+NS+'ct17').text='5000003'
  def extra(root):annex=root.find('.//'+NS+'Pluc_01_6_GTGT_CSSX');annex.insert(5,copy.deepcopy(annex[4]))
  def ident(root):root.find('.//'+NS+'cong_ct18').set('id','ID_3')
  def main(root):root.find('.//'+NS+'ct33').text='60000001'
  def name(root):root.find('.//'+NS+'ct09').text='TEN THAT CUA DOANH NGHIEP'
  def total(root):root.find('.//'+NS+'ct24').text='1'
  for edit in (amount,extra,ident,main,name,total):
   with self.subTest(edit=edit.__name__),self.assertRaises(w.InputError):w.validate_web_xml(edited(body,edit),case_id=contract.FORMULA_CASE)
 def test_cases_do_not_accept_each_other(self):
  with self.assertRaises(w.InputError):w.validate_web_xml(web.annex16_fixture(contract.RATIO_CASE),case_id=contract.FORMULA_CASE)

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
 def test_head_office_restore_is_bounded_and_never_writes_cells(self):
  source=(ROOT/'HtkkGtgtRoundtripInspection.cs').read_text(encoding='utf-8')
  self.assertIn('if(Annex16WebCase()&&!annex16HeadOfficeRestored){RestoreImportedAnnex16HeadOffices();return;}',source)
  body=source[source.index(' private static readonly string[][] Annex16ExpectedRows'):source.index(' private static XmlDocument ReadBoundedOriginalXml(')]
  for forbidden in ('set_Value','"Value",','PerformClick','"Formula"','InsertTable'):self.assertNotIn(forbidden,body)
  # Only one real arrow key between H and I (EnterCell rebuilds the list, runs 43683942253/43683944987); nothing is typed.
  self.assertEqual(body.count('SendKeys'),1);self.assertIn('SendKeys.SendWait(column==Annex16ColumnH?"{LEFT}":"{RIGHT}");',body)
  self.assertIn('TryEnterImportedAnnex16CellByKey(grid,annex,row,Annex16ColumnH);',body);self.assertIn('TryEnterImportedAnnex16CellByKey(grid,annex,row,Annex16ColumnI);',body)
  for row in contract.CASES[contract.FORMULA_CASE]['rows']:self.assertIn('"'+row[1][9]+'"',body)
  reference=(ROOT/'HtkkWebInputReference.cs').read_text(encoding='utf-8')
  for case in CASES:self.assertIn('"'+case+'"',reference)
  registry=json.loads((ROOT/'htkk-native-automation-registry.json').read_text())['resultFields']
  self.assertEqual([registry[k]['maximum'] for k in ('annex16HeadOfficeRepairCount','annex16HeadOfficeFailureMask')],[64,2097151])

if __name__=='__main__':unittest.main()
