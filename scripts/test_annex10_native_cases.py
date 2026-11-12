"""Offline contract of the 01-10/GTGT web->HTKK case (oracle HTKK 5.8.2). Synthetic XML built
from the trusted contract; passing these tests is never native evidence."""
import copy,datetime,hashlib,importlib.util,json,pathlib,unittest
import xml.etree.ElementTree as ET
ROOT=pathlib.Path(__file__).parent
def load(name,file):
 spec=importlib.util.spec_from_file_location(name,ROOT/file);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
cases=load('annex10_cases_registry','htkk_native_cases.py')
contract=load('annex10_cases_contract','htkk_annex10_web_cases.py')
web=load('annex10_cases_web_fixture','test_htkk_web_input.py');w=web.w
out=load('annex10_cases_native_fixture','test_htkk_web_native_output.py');n=out.n
dispatch=load('annex10_cases_dispatch','dispatch-native-cases.py')
CASE=contract.NQ204_CASE;NS='{'+contract.NS+'}'
def edited(body,edit):
 root=ET.fromstring(body.decode('utf-8'));edit(root);ET.register_namespace('',contract.NS)
 return (w.PREAMBLE+ET.tostring(root,encoding='unicode')).encode('utf-8')

class Registry(unittest.TestCase):
 def test_single_non_gating_5_8_2_case_with_own_producer_and_context(self):
  self.assertEqual(cases.ANNEX10_CASES,(CASE,));c=cases.CASES[CASE];a=cases.ADAPTERS[c['adapterId']]
  self.assertIs(c['releaseGate'],False);self.assertEqual(cases.htkk_version(CASE),'5.8.2')
  self.assertEqual(cases.status_context(CASE),'htkk-native/annex10-nq204@htkk582')
  self.assertEqual((a['producer'],a['driver'],a['privacyValidator'],a['htkkVersion']),('scripts/generate-htkk-web-annex10-reference.mjs','gtgt-web-import-inspect','gtgt-annex10-v1','5.8.1'))
  self.assertEqual(c['unit'],{'menuId':'D1','adapterVersion':'2.8.3','periodType':'month','periodValue':'10/2026','activityCode':'00','annexes':['01-10/GTGT'],'amendmentOrder':0})
  self.assertNotIn(CASE,cases.GATE_CASES)

class InputContract(unittest.TestCase):
 def body(self):return web.annex10_fixture(CASE)
 def test_exact_fixture_and_manifest_pass(self):
  body=self.body();manifest=web.case_manifest(body,CASE)
  self.assertEqual(w.validate_manifest(json.dumps(manifest).encode()),manifest)
  result=w.validate_web_xml(body,case_id=CASE,manifest=manifest)
  self.assertEqual(result['annexTaxLeafCount'],88)
  self.assertEqual(manifest['expectedAnnexLeaves'][3],['PL_NQ142_GTGT/HH_DV_MuaVaoTrongKy/BangKeTenHHDV/thueGTGTHHDV','987654',''])
 def test_any_changed_amount_row_or_attribute_is_refused(self):
  body=self.body()
  def amount(root):root.find('.//'+NS+'thueGTGTDuocGiam').text='3000000'
  def extra(root):sales=root.find('.//'+NS+'HH_DV_BanRaTrongKy');sales.insert(0,copy.deepcopy(sales[0]))
  def ident(root):root.find('.//'+NS+'HH_DV_BanRaTrongKy')[1].set('ID','ID_3')
  def main(root):root.find('.//'+NS+'ct33').text='12999995'
  def name(root):root.find('.//'+NS+'tenHHDV').text='TEN THAT CUA KHACH HANG'
  for edit in (amount,extra,ident,main,name):
   with self.subTest(edit=edit.__name__),self.assertRaises(w.InputError):w.validate_web_xml(edited(body,edit),case_id=CASE)
 def test_manifest_keys_are_exact(self):
  body=self.body();manifest=web.case_manifest(body,CASE)
  for key,value in (('htkkVersion','5.8.1'),('nativeBaseSha256','0'*64),('expectedMainMoney',{}),('fullCompatibilityVerified',True)):
   with self.subTest(key=key),self.assertRaises(w.InputError):w.validate_manifest(json.dumps({**manifest,key:value}).encode())
  with self.assertRaises(w.InputError):w.validate_manifest(json.dumps({k:v for k,v in manifest.items() if k!='expectedMainMoney'}).encode())

class NativeOutput(unittest.TestCase):
 def test_reexport_exact_and_baseline_is_the_zero_main_declaration(self):
  web_body,native,_,_=out.fixture(CASE)
  self.assertEqual(n.validate_native(native,CASE,out.TODAY)['leafCount'],74)
  self.assertEqual(n.compare_tax(web_body,native,CASE)['checkedTaxLeafCount'],88)
  baseline=out.annex10_baseline(CASE)
  self.assertEqual(n.validate_native(baseline,CASE,out.TODAY,initial=True,aligned=True)['leafCount'],74)
  self.assertFalse(n.baseline_matches_input(CASE))
  with self.assertRaises((n.OutputError,n.privacy.EvidenceError)):n.validate_native(native,CASE,out.TODAY,initial=True,aligned=True)
  with self.assertRaises(n.OutputError):n.validate_native(baseline,CASE,out.TODAY)
