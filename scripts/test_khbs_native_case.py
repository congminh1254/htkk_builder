"""Offline contracts of the KHBS (kê khai bổ sung lần 1) native case; synthetic, never Windows evidence."""
import copy,importlib.util,json,pathlib,re,unittest
import xml.etree.ElementTree as ET
ROOT=pathlib.Path(__file__).parent
def load(name,file):
 spec=importlib.util.spec_from_file_location(name,ROOT/file);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
cases=load('khbs_case_registry','htkk_native_cases.py')
w=load('khbs_web_input','fetch-htkk-web-input.py')
f=load('khbs_web_input_fixtures','test_htkk_web_input.py')
CASE='01GTGT-khbs-zero-to-sale10-M10-2026';MODE='gtgt-amendment-khbs-inspect'
def source(name):return (ROOT/name).read_text(encoding='utf-8')

class Registry(unittest.TestCase):
 def test_one_non_gating_582_case_with_its_own_driver_and_amendment_order(self):
  self.assertEqual(cases.KHBS_CASES,(CASE,));c=cases.CASES[CASE];a=cases.ADAPTERS[c['adapterId']]
  self.assertIs(c['releaseGate'],False);self.assertEqual(cases.htkk_version(CASE),'5.8.2');self.assertEqual(cases.driver(CASE),MODE)
  self.assertEqual((a['producer'],a['privacyValidator'],a['menuId'],a['xmlVersion']),('scripts/generate-htkk-web-khbs-reference.mjs','gtgt-khbs-v1','D1','2.8.3'))
  self.assertEqual(c['unit']['amendmentOrder'],1);self.assertEqual(c['unit']['annexes'],[])
  # amendmentOrder 1 is reserved to this adapter; every other case stays a first declaration.
  self.assertTrue(all(x['unit']['amendmentOrder']==0 for id,x in cases.CASES.items() if id!=CASE))
  self.assertEqual(cases.status_context(CASE),'htkk-native/khbs-zero-to-sale10@htkk582')
 def test_registry_mode_is_bounded_and_retains_no_raw_output(self):
  registry=json.loads(source('htkk-native-automation-registry.json'));meta=registry['modes'][MODE]
  self.assertEqual((meta['terminalStage'],meta['privateArtifactPolicy'],meta['contextPolicy']),('gtgt-amendment-khbs-inspected','none','htkk-native/case'))
  fields=registry['resultFields']
  for key,field in fields.items():
   if key.startswith('khbs'):self.assertEqual(field['activeModes'],[MODE])
  self.assertEqual(fields['amendmentLifecycleVerified']['activeModes'],[])
  output=load('khbs_native_output','publish-htkk-web-native-output.py');self.assertNotIn(CASE,output.BRANCHES)

class InputValidator(unittest.TestCase):
 def setUp(self):self.body=f.sale_fixture(CASE);self.manifest=f.case_manifest(self.body,CASE)
 def test_exact_fixed_input_and_manifest_accepted(self):
  self.assertEqual(w.validate_manifest((json.dumps(self.manifest)+'\n').encode())['caseId'],CASE)
  result=w.validate_web_xml(self.body,case_id=CASE,manifest=self.manifest);self.assertEqual(result['amendmentTaxLeafCount'],270);self.assertIs(result['nativeProvenance'],False)
 def test_any_fragment_header_or_money_change_rejected(self):
  for before,after in (('<ct3>100000</ct3>','<ct3>100001</ct3>'),('<loaiTKhai>B</loaiTKhai>','<loaiTKhai>C</loaiTKhai>'),('<soLan>1</soLan>','<soLan>2</soLan>'),
                       ('<ct04>0</ct04>','<ct04>1</ct04>'),('<ma_HSo>0026</ma_HSo>','<ma_HSo>0027</ma_HSo>'),('<ct3a_1>2026-11-13</ct3a_1>','<ct3a_1>2026-11-14</ct3a_1>'),
                       ('<ct32>1000000</ct32>','<ct32>1000001</ct32>'),('id="ID_9"','id="ID_10"'),('<ct8 />','<ct8>LY DO</ct8>')):
   text=self.body.decode()
   self.assertIn(before,text,before)
   with self.subTest(before=before),self.assertRaises(w.InputError):w.validate_web_xml(text.replace(before,after,1).encode(),case_id=CASE,manifest=self.manifest)
 def test_case_cannot_be_relabelled_and_manifest_is_pinned(self):
  with self.assertRaises(w.InputError):w.validate_web_xml(self.body,case_id='01GTGT-sale10-M10-2026')
  for key,value in (('soLan',2),('ngayLapKHBS','2026-11-14'),('htkkVersion','5.8.1'),('exporter','lib/htkk-xml.ts')):
   bad=copy.deepcopy(self.manifest);bad[key]=value
   with self.subTest(key=key),self.assertRaises(w.InputError):w.validate_manifest(json.dumps(bad).encode())

class Driver(unittest.TestCase):
 def test_driver_uses_only_original_controls_and_bounded_diagnostics(self):
  text=source('HtkkGtgtAmendmentKhbsInspection.cs')
  for original in ('"cmdImportXML"','"btnTongHopKHBS"','"cmdExport"','"radKetXuatXML"','"Nhập dữ liệu từ XML thành công."','"Tổng hợp dữ liệu lên KHBS thành công"','"Kết xuất tờ khai xml thành công."','TrySubmitOriginalFileDialog','OriginalMessageCatalogueId','HtkkWebTaxComparison.CompareKhbs','"mskNgayLapKHBS"','"13/11/2026"','KhbsLeafTarget=270'):
   self.assertIn(original,text)
  for forbidden in ('File.Write','.SetValue(','GetMethod(','InnerText=','InnerXml='):self.assertNotIn(forbidden,text)
  self.assertEqual(w.khbs.tax_leaves(CASE),270)
 def test_mode_is_routed_through_the_proven_b1_steps(self):
  self.assertIn('||KhbsMode();}',source('HtkkGtgtAmendmentOpenInspection.cs'));self.assertIn('if(KhbsMode()){khbsPeriodMatched=',source('HtkkGtgtAmendmentOpenInspection.cs'))
  self.assertIn('if(mode=="gtgt-amendment-open-inspect"||KhbsMode()){CloseOriginalPriorForAmendment();return;}',source('HtkkGtgtAmendmentInspection.cs'))
  self.assertIn('if((webCaseId==KhbsWebCaseId)!=KhbsMode())throw new InvalidOperationException();',source('HtkkWebInputReference.cs'))
  self.assertIn('|| mode == HtkkAutomationMode.GtgtAmendmentKhbsInspect',source('HtkkGtgtReferenceNavigation.cs'))
 def test_probe_and_workflow_require_the_whole_tree_and_report_status(self):
  probe=source('probe-htkk-windows.ps1');workflow=(ROOT.parent/'.github/workflows/probe-htkk-windows.yml').read_text(encoding='utf-8')
  line=next(l for l in probe.splitlines() if "if($GuiAutomation -eq 'gtgt-amendment-khbs-inspect'){$matched=" in l)
  for flag in ('khbsTreeMatched','khbsLeafCount -eq 270','khbsMismatchMask -eq 0','khbsFirstDifferenceOrdinal -eq 0','khbsSummaryAcknowledged','khbsImportPathMatched','khbsExportSchemaPinnedVerified','-not $lastGui.amendmentLifecycleVerified'):self.assertIn(flag,line)
  self.assertIn("if(($GuiAutomation -eq 'gtgt-amendment-khbs-inspect') -ne ($env:EXPECTED_WEB_CASE_ID -ceq '01GTGT-khbs-zero-to-sale10-M10-2026')){throw 'WEB_REFERENCE_INPUT_INVALID'}",probe)
  self.assertEqual(workflow.count("inputs.gui_automation == 'gtgt-amendment-khbs-inspect'"),3)
  self.assertIn("'01GTGT-khbs-zero-to-sale10-M10-2026'='htkk-web-khbs-zero-to-sale10-input-v1'",source('HtkkNativeCaseFormats.ps1'))

if __name__=='__main__':unittest.main()
