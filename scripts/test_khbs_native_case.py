"""Offline contracts of the KHBS (kê khai bổ sung lần 1) native case; synthetic, never Windows evidence."""
import base64,copy,datetime,hashlib,importlib.util,json,pathlib,re,tempfile,unittest,urllib.error
import xml.etree.ElementTree as ET
ROOT=pathlib.Path(__file__).parent
def load(name,file):
 spec=importlib.util.spec_from_file_location(name,ROOT/file);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
cases=load('khbs_case_registry','htkk_native_cases.py')
w=load('khbs_web_input','fetch-htkk-web-input.py')
f=load('khbs_web_input_fixtures','test_htkk_web_input.py')
CASE='01GTGT-khbs-zero-to-sale10-M10-2026';CASE2='01GTGT-khbs-sale5-to-sale10-M09-2026';CASE3='01GTGT-khbs-lan2-sale10-M10-2026';MODE='gtgt-amendment-khbs-inspect'
out=load('khbs_native_output_publisher','publish-htkk-khbs-native-output.py')
TODAY=datetime.date(2026,11,20);SOURCE,ARTIFACT,BUILDER_SHA='a'*40,'b'*40,'c'*40
def source(name):return (ROOT/name).read_text(encoding='utf-8')

class Registry(unittest.TestCase):
 def test_one_non_gating_582_case_with_its_own_driver_and_amendment_order(self):
  self.assertEqual(cases.KHBS_CASES,(CASE,CASE2,CASE3));c=cases.CASES[CASE];a=cases.ADAPTERS[c['adapterId']]
  self.assertIs(c['releaseGate'],False);self.assertEqual(cases.htkk_version(CASE),'5.8.2');self.assertEqual(cases.driver(CASE),MODE)
  self.assertEqual((a['producer'],a['privacyValidator'],a['menuId'],a['xmlVersion']),('scripts/generate-htkk-web-khbs-reference.mjs','gtgt-khbs-v1','D1','2.8.3'))
  self.assertEqual(c['unit']['amendmentOrder'],1);self.assertEqual(c['unit']['annexes'],[])
  # amendmentOrder 1 is reserved to this adapter; every other case stays a first declaration.
  self.assertTrue(all(x['unit']['amendmentOrder']==0 for id,x in cases.CASES.items() if id not in (CASE,CASE2,CASE3)))
  # Case 3: bổ sung lần 2 (amendmentOrder 2, its own adapter), non-gating, on the same driver.
  c3=cases.CASES[CASE3];self.assertEqual((c3['adapterId'],c3['unit']['amendmentOrder'],c3['unit']['periodValue'],c3['releaseGate']),('01-gtgt-2.8.3-khbs-lan2',2,'10/2026',False));self.assertEqual(cases.driver(CASE3),MODE)
  self.assertEqual(cases.status_context(CASE),'htkk-native/khbs-zero-to-sale10@htkk582')
  # Case 2: non-gating too, M09/2026 (positive late days), same adapter and driver, its own branches and status.
  c2=cases.CASES[CASE2];self.assertIs(c2['releaseGate'],False);self.assertEqual(cases.htkk_version(CASE2),'5.8.2');self.assertEqual(cases.driver(CASE2),MODE)
  self.assertEqual((c2['adapterId'],c2['unit']['periodType'],c2['unit']['periodValue'],c2['unit']['amendmentOrder']),('01-gtgt-2.8.3-khbs','month','09/2026',1))
  self.assertEqual(cases.status_context(CASE2),'htkk-native/khbs-sale5-to-sale10@htkk582')
  self.assertEqual(cases.TRUSTED_ADAPTERS['01-gtgt-2.8.3']['periods']['month'],('10/2026',))
 def test_registry_mode_is_bounded_and_retains_no_raw_output(self):
  registry=json.loads(source('htkk-native-automation-registry.json'));meta=registry['modes'][MODE]
  self.assertEqual((meta['terminalStage'],meta['privateArtifactPolicy'],meta['contextPolicy']),('gtgt-amendment-khbs-inspected','raw-khbs-reexport','htkk-native/case'))
  fields=registry['resultFields']
  for key,field in fields.items():
   if key.startswith('khbs'):self.assertEqual(field['activeModes'],[MODE])
  self.assertEqual(fields['amendmentLifecycleVerified']['activeModes'],[])
  self.assertEqual(fields['khbsOpenMainState']['maximum'],3);self.assertIn(CASE2,fields['webCaseId']['values'])
  # The D1 publisher never takes a KHBS case; only the KHBS publisher retains them, on their own output branches.
  output=load('khbs_native_output','publish-htkk-web-native-output.py');self.assertNotIn(CASE,output.BRANCHES);self.assertNotIn(CASE2,output.BRANCHES)
  self.assertEqual(out.BRANCHES,{CASE:'gtgt-web-native-khbs-zero-to-sale10-output',CASE2:'gtgt-web-native-khbs-sale5-to-sale10-output',CASE3:'gtgt-web-native-khbs-lan2-sale10-output'})

class SecondCase(unittest.TestCase):
 """Case 2: non-zero C0, a decrease at 5% (negative chênh lệch), M09/2026 with 24 late days."""
 def setUp(self):self.body=f.sale_fixture(CASE2);self.manifest=f.case_manifest(self.body,CASE2)
 def test_exact_fixed_input_with_late_interest_and_negative_rows(self):
  result=w.validate_web_xml(self.body,case_id=CASE2,manifest=self.manifest);self.assertEqual(result['amendmentTaxLeafCount'],296)
  text=self.body.decode()
  for fragment in ('<ct3a_2>24</ct3a_2>','<ct3b>1440</ct3b>','<ct06>-2000000</ct06>','<ct06>-100000</ct06>','<tongCong_ct10>200000</tongCong_ct10>','<kyKKhai>09/2026</kyKKhai>','<kyKKhaiDenNgay>30/09/2026</kyKKhaiDenNgay>'):self.assertIn(fragment,text)
  self.assertEqual(w.khbs.manifest_fields(CASE2)['expected']['ct3a_2'],'24');self.assertEqual(w.khbs.money(CASE2)['ct40'],'400000')
 def test_period_interest_rows_and_money_are_pinned(self):
  for before,after in (('<ct3a_2>24</ct3a_2>','<ct3a_2>23</ct3a_2>'),('<ct3b>1440</ct3b>','<ct3b>1441</ct3b>'),('<ct06>-2000000</ct06>','<ct06>2000000</ct06>'),
                       ('<kyKKhai>09/2026</kyKKhai>','<kyKKhai>10/2026</kyKKhai>'),('<kyKKhaiTuNgay>01/09/2026</kyKKhaiTuNgay>','<kyKKhaiTuNgay>01/10/2026</kyKKhaiTuNgay>'),('<ct32>4000000</ct32>','<ct32>1000000</ct32>')):
   text=self.body.decode();self.assertIn(before,text,before)
   for count in (1,text.count(before)):
    with self.subTest(before=before,count=count),self.assertRaises(w.InputError):w.validate_web_xml(text.replace(before,after,count).encode(),case_id=CASE2,manifest=self.manifest)
  # The M09 header only projects for this case; the cases cannot be swapped.
  with self.assertRaises(w.InputError):w.validate_web_xml(self.body,case_id=CASE)
  with self.assertRaises(w.InputError):w.validate_web_xml(f.sale_fixture(CASE),case_id=CASE2)
 def test_driver_types_the_fixed_c0_and_checks_it_on_the_sheet_and_in_the_saved_file(self):
  text=source('HtkkGtgtAmendmentKhbsInspection.cs')
  self.assertIn('private const string KhbsSale5WebCaseId="01GTGT-khbs-sale5-to-sale10-M09-2026";',text);self.assertIn('KhbsSale5LeafTarget=296',text)
  self.assertIn('new decimal[]{0,0,0,0,0,0,0,3000000,200000,0,2000000,100000,1000000,100000,0,3000000,200000,200000,0,0,0,200000,0,200000,0,0,0}',text)
  self.assertIn('EditOriginalGtgtCase(grid,sheet,46,9,"2000000",HtkkAutomationStage.GtgtCaseEditing)',text);self.assertIn('EditOriginalGtgtCase(grid,sheet,47,9,"1000000",HtkkAutomationStage.GtgtCaseEditing)',text)
  self.assertIn('private string PeriodMonth(){return KhbsNonzeroOriginal()?"09":"10";}',text)
  sheet=source('HtkkGtgtPeriodAndSheet.cs')
  self.assertIn('if(KhbsMode())fixedInput=KhbsNonzeroOriginal()&&column==9&&((webCaseEditCount==0&&row==46&&value=="2000000")||(webCaseEditCount==1&&row==47&&value=="1000000"));',sheet)
  self.assertIn('if(matched&&AmendmentInspectionMode()){if(amendmentPriorSaveInvoked)return;if(KhbsNonzeroOriginal()&&!PrepareKhbsOriginal(forms[0],grid,sheet))return;StartOriginalAmendmentPriorSave(forms[0],grid,sheet);return;}',sheet)
  self.assertIn('SetText(period,"mskMonth",PeriodMonth())',sheet);self.assertNotIn('SetText(period,"mskMonth","10")',sheet)
  prior=source('HtkkGtgtAmendmentInspection.cs')
  self.assertIn('!(KhbsNonzeroOriginal()?khbsOriginalMoneyMatched:gtgtZero)',prior);self.assertIn('if(!PriorSavedMoneyExpected()||amendmentPriorSavedMoneyCount!=27)throw new InvalidOperationException();',prior)
  opened=source('HtkkGtgtAmendmentOpenInspection.cs')
  self.assertIn('==PeriodMonth()&&',opened);self.assertIn('if(mainState==0||(!KhbsNonzeroOriginal()&&!(KhbsLan2Case()&&khbsRound==2)&&mainState!=1)',opened)
  # The month and the saved-file name change only for case 2; every other driver keeps M10/2026.
  self.assertNotIn('"Thang"),CultureInfo.InvariantCulture)=="10"',opened+sheet)

class PostSave(unittest.TestCase):
 """Run 43367487266: case 2 saved the exact non-zero C0 and then waited at gtgt-original-declaration-save-success."""
 def test_post_save_wait_is_bounded_diagnosed_and_ends_with_its_own_terminal(self):
  text=source('HtkkGtgtAmendmentKhbsInspection.cs');registry=json.loads(source('htkk-native-automation-registry.json'))
  self.assertIn('int mask=(amendmentPriorOwner.Visible?0:1)|(amendmentPriorOwner.Enabled?0:2)|(amendmentPriorGrid.Visible?0:4)|(amendmentPriorGrid.Enabled?0:8)|(OriginalMessageVisible()?16:0)|((bool)dirty.GetValue(amendmentPriorOwner)?32:0);',text)
  self.assertIn('if(khbsPostSaveClock.Elapsed.TotalSeconds>=30){finished=true;SetStage(HtkkAutomationStage.GtgtAmendmentKhbsPostSaveTimeout);',text)
  self.assertEqual(registry['resultFields']['khbsPostSaveWaitMask']['maximum'],127)
  for key in ('khbsPostSaveWaitMask','khbsDirtyAfterSave','khbsDiscardPromptAnswered'):self.assertEqual(registry['resultFields'][key]['activeModes'],[MODE])
  self.assertIn('gtgt-amendment-khbs-post-save-timeout',{s['id'] for s in registry['stages']})
  self.assertIn("'gtgt-amendment-khbs-post-save-timeout'",source('generate-native-automation-registry.py'))
  self.assertIn('if(KhbsMode()&&!KhbsPostSaveReady())return;',source('HtkkGtgtAmendmentInspection.cs'))
 def test_only_case_two_may_close_through_the_original_discard_prompt(self):
  text=source('HtkkGtgtAmendmentKhbsInspection.cs')
  # Dirty alone (mask 32), stable for 2 s, the exact C0 vector still on the sheet, and only for the non-zero C0 case.
  self.assertIn('if(mask==32&&KhbsNonzeroOriginal()&&khbsPostSaveClock.Elapsed.TotalSeconds>=2){',text)
  self.assertIn('if(gtgtEmptyMoney!=0||!KhbsOriginalVector(amendmentPriorSheet))throw new InvalidOperationException();',text)
  # Pinned 0013 text and the style-6 "Không" button (cmd_No); no other answer is possible.
  self.assertIn('text!="Có muốn ghi lại thông tin thay đổi không?"||buttons.Length!=1||CountVisibleButtons(message)!=3',text)
  self.assertIn('no.Text.Replace("&",String.Empty).Trim()!="Không"',text);self.assertNotIn('"btn_1"',text);self.assertNotIn('"btn_3"',text)
  opened=source('HtkkGtgtAmendmentOpenInspection.cs')
  self.assertIn('System.Windows.Forms.Timer prompt=khbsDirtyAfterSave?StartKhbsDiscardPromptWatcher():null;',opened)
  self.assertIn('((bool)dirty.GetValue(amendmentPriorOwner)&&!khbsDirtyAfterSave)',opened)
  # The probe accepts the path for case 2 only; case 1 still needs the cleared flag and no dirty path.
  line=next(l for l in source('probe-htkk-windows.ps1').splitlines() if "if($GuiAutomation -eq 'gtgt-amendment-khbs-inspect'){$matched=" in l)
  self.assertIn("{$lastGui.amendmentPriorDirtyCleared -or ($lastGui.khbsDirtyAfterSave -and $lastGui.khbsPostSaveWaitMask -eq 32)}else{$lastGui.amendmentPriorDirtyCleared -and -not $lastGui.khbsDirtyAfterSave}",line)
  # The reopened B1 still requires the C0 file unchanged (same hash as at the save).
  self.assertIn('amendmentOpenPriorUnchanged=amendmentPriorFileFresh&&PriorSavedMoneyExpected()&&',opened)

class SheetWatcherAfterSave(unittest.TestCase):
 """Runs 43367487266 and 43369672859: after the case-2 Ghi the still-ticking sheet watcher re-entered PrepareKhbsOriginal,
 whose guard throws once Ghi was invoked (failureCategory operation-not-established, stage left at save-success)."""
 def test_sheet_watcher_returns_before_any_c0_step_once_ghi_was_invoked(self):
  sheet=source('HtkkGtgtPeriodAndSheet.cs');line=next(l for l in sheet.splitlines() if 'if(matched&&AmendmentInspectionMode()){' in l)
  self.assertLess(line.index('if(amendmentPriorSaveInvoked)return;'),line.index('PrepareKhbsOriginal('))
  self.assertLess(line.index('if(amendmentPriorSaveInvoked)return;'),line.index('StartOriginalAmendmentPriorSave('))
  # The guard itself stays fail-closed for any other caller.
  self.assertIn('if(!KhbsNonzeroOriginal()||amendmentPriorSaveInvoked)throw new InvalidOperationException();',source('HtkkGtgtAmendmentKhbsInspection.cs'))
 def test_success_message_wait_is_bounded_with_its_own_mask_bit(self):
  text=source('HtkkGtgtAmendmentKhbsInspection.cs');prior=source('HtkkGtgtAmendmentInspection.cs')
  self.assertIn('if(amendmentPriorSaveSuccessAcknowledged||khbsSaveClock.Elapsed.TotalSeconds<60)return true;',text)
  self.assertIn('khbsPostSaveWaitMask|=64;finished=true;SetStage(HtkkAutomationStage.GtgtAmendmentKhbsPostSaveTimeout);',text)
  observe=prior.split('private void ObserveOriginalAmendmentPriorSave(){',1)[1]
  self.assertLess(observe.index('if(KhbsMode()&&!KhbsSaveWaitBounded())return;'),observe.index('foreach(Form form in Application.OpenForms)'))

class Lan2(unittest.TestCase):
 """Case 3: bổ sung lần 2 on the saved bổ sung lần 1 (previous-version web file staged as 01GTGT-prior.xml)."""
 def setUp(self):self.body=f.sale_fixture(CASE3);self.manifest=f.case_manifest(self.body,CASE3);self.prior=f.sale_fixture(CASE)
 def test_input_prior_and_manifest_are_exact(self):
  self.assertEqual(w.names(CASE3),('01GTGT-web.xml','01GTGT-prior.xml','manifest.json'));self.assertEqual(w.names(CASE),('01GTGT-web.xml','manifest.json'))
  self.assertEqual(w.validate_web_xml(self.body,case_id=CASE3,manifest=self.manifest)['amendmentTaxLeafCount'],270)
  self.assertIn('<soLan>2</soLan>',self.body.decode());self.assertEqual(self.manifest['priorCaseId'],CASE)
  files={'01GTGT-web.xml':self.body,'01GTGT-prior.xml':self.prior,'manifest.json':(json.dumps(self.manifest)+'\n').encode()}
  self.assertIsNotNone(w.validate_prior(files,w.validate_manifest(files['manifest.json'])))
  for broken in (self.prior+b' ',f.sale_fixture(CASE2)):
   with self.subTest(size=len(broken)),self.assertRaises(w.InputError):w.validate_prior(dict(files,**{'01GTGT-prior.xml':broken}),self.manifest)
  bad=copy.deepcopy(self.manifest);bad['priorCaseId']=CASE2
  with self.assertRaises(w.InputError):w.validate_manifest(json.dumps(bad).encode())
  # lần 1 files cannot claim soLan 2, and the lần 2 file cannot be relabelled as lần 1.
  with self.assertRaises(w.InputError):w.validate_web_xml(self.body.replace(b'<soLan>2</soLan>',b'<soLan>1</soLan>'),case_id=CASE3,manifest=self.manifest)
  with self.assertRaises(w.InputError):w.validate_web_xml(self.body,case_id=CASE)
  with tempfile.TemporaryDirectory() as temp:
   staged=w.stage(files,temp);self.assertEqual(sorted(p.name for p in staged.iterdir()),['01GTGT-prior.xml','01GTGT-web.xml','manifest.json'])
  with tempfile.TemporaryDirectory() as temp,self.assertRaises(w.InputError):w.stage({k:v for k,v in files.items() if k!='01GTGT-prior.xml'},temp)
 def test_driver_saves_b1_and_reopens_b2_through_original_controls(self):
  text=source('HtkkGtgtAmendmentKhbsInspection.cs')
  for fragment in ('private const string KhbsPriorB1FileName="bs1_01_GTGT_TT80_CQTQL10129_00_102026_283.xml";','Button save=Named(khbsOwner,"cmdSave") as Button;','"Đã ghi dữ liệu thành công!"',
                   'Button close=Named(khbsOwner,"cmdExit") as Button;','SetText(period,"txtLan","2")','private string KhbsImportPath(){return KhbsImportingPrior()?webPriorPath:webInputPath;}',
                   'if(KhbsImportingPrior()){khbsPriorSummaryAcknowledged=true;khbsPhase="prior-save-ready";','navigationPhase="waiting-main-menu";menuStep=0;SetStage(HtkkAutomationStage.GtgtAmendmentKhbsRound2Opening);',
                   'string saved=khbsPriorFileSha256;InspectKhbsPriorSavedFile();if(khbsPriorFileSha256!=saved)throw new InvalidOperationException();'):self.assertIn(fragment,text)
  self.assertIn('new decimal[]{0,0,0,0,0,0,0,1000000,100000,0,0,0,1000000,100000,0,1000000,100000,100000,0,0,0,100000,0,100000,0,0,0}',text)
  opened=source('HtkkGtgtAmendmentOpenInspection.cs');self.assertNotIn('SetText(',opened)
  self.assertIn('==khbsRound.ToString(CultureInfo.InvariantCulture)&&(KhbsMode()',opened);self.assertIn('KhbsLan2Case()&&khbsRound==2&&KhbsB1Vector(sheet)?3:0',opened)
  web=source('HtkkWebInputReference.cs');self.assertIn('webPriorPath=host+".web-prior.xml";webPriorSha256=ReadOwnHexSidecar(host+".web-prior.sha256",64);',web)
  self.assertIn('private string RoundtripInputHash(){return KhbsMode()?KhbsImportHash():',web)
  registry=json.loads(source('htkk-native-automation-registry.json'));self.assertEqual(registry['resultFields']['menuClickCount']['modeMaximums'][MODE],9)
  probe=source('probe-htkk-windows.ps1');line=next(l for l in probe.splitlines() if "if($GuiAutomation -eq 'gtgt-amendment-khbs-inspect'){$matched=" in l)
  self.assertIn("{$lastGui.khbsRound -eq 2 -and $lastGui.khbsRound2Opened -and $lastGui.khbsPriorImportSucceeded -and $lastGui.khbsPriorSummaryAcknowledged -and $lastGui.khbsPriorSaveAcknowledged -and $lastGui.khbsPriorFileSaved",line)
  self.assertIn("$priorPath=$hostFull+'.web-prior.xml'",probe);self.assertIn("$manifest.priorCaseId -cne '01GTGT-khbs-zero-to-sale10-M10-2026'",probe)

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
  self.assertIn('if(KhbsCaseId(webCaseId)!=KhbsMode())throw new InvalidOperationException();',source('HtkkWebInputReference.cs'))
  self.assertIn('|| mode == HtkkAutomationMode.GtgtAmendmentKhbsInspect',source('HtkkGtgtReferenceNavigation.cs'))
 def test_probe_and_workflow_require_the_whole_tree_and_report_status(self):
  probe=source('probe-htkk-windows.ps1');workflow=(ROOT.parent/'.github/workflows/probe-htkk-windows.yml').read_text(encoding='utf-8')
  line=next(l for l in probe.splitlines() if "if($GuiAutomation -eq 'gtgt-amendment-khbs-inspect'){$matched=" in l)
  for flag in ('khbsTreeMatched',"khbsLeafCount -eq $(if($env:EXPECTED_WEB_CASE_ID -ceq '01GTGT-khbs-sale5-to-sale10-M09-2026'){296}else{270})",'khbsMismatchMask -eq 0','khbsFirstDifferenceOrdinal -eq 0','khbsSummaryAcknowledged','khbsImportPathMatched','khbsExportSchemaPinnedVerified','-not $lastGui.amendmentLifecycleVerified',
               '$lastGui.khbsOriginalMoneyMatched -and $lastGui.khbsSavedMoneyMatched -and -not $lastGui.amendmentPriorSavedMoneyZero -and $lastGui.khbsOpenMainState -in @(1,2) -and $lastGui.webCaseEditCount -eq 2',
               "$lastGui.amendmentPriorMoneyZero -and $lastGui.amendmentPriorSavedMoneyZero -and -not $lastGui.khbsOriginalMoneyMatched -and -not $lastGui.khbsSavedMoneyMatched -and $lastGui.khbsOpenMainState -eq $(if($env:EXPECTED_WEB_CASE_ID -ceq '01GTGT-khbs-lan2-sale10-M10-2026'){3}else{1}) -and $lastGui.webCaseEditCount -eq 0"):self.assertIn(flag,line)
  self.assertIn("if(($GuiAutomation -eq 'gtgt-amendment-khbs-inspect') -ne ($env:EXPECTED_WEB_CASE_ID -cin @('01GTGT-khbs-zero-to-sale10-M10-2026','01GTGT-khbs-sale5-to-sale10-M09-2026','01GTGT-khbs-lan2-sale10-M10-2026'))){throw 'WEB_REFERENCE_INPUT_INVALID'}",probe)
  self.assertEqual(workflow.count("inputs.gui_automation == 'gtgt-amendment-khbs-inspect'"),4)
  self.assertIn("'01GTGT-khbs-zero-to-sale10-M10-2026'='htkk-web-khbs-zero-to-sale10-input-v1'",source('HtkkNativeCaseFormats.ps1'))
  self.assertIn("'01GTGT-khbs-sale5-to-sale10-M09-2026'='htkk-web-khbs-sale5-to-sale10-input-v1'",source('HtkkNativeCaseFormats.ps1'))
  self.assertIn("'01GTGT-khbs-lan2-sale10-M10-2026'='htkk-web-khbs-lan2-sale10-input-v1'",source('HtkkNativeCaseFormats.ps1'))
 def test_raw_export_is_staged_on_match_and_mismatch_and_published_by_its_own_step(self):
  probe=source('probe-htkk-windows.ps1');workflow=(ROOT.parent/'.github/workflows/probe-htkk-windows.yml').read_text(encoding='utf-8')
  self.assertIn("if($GuiAutomation -eq 'gtgt-amendment-khbs-inspect' -and $null -ne $report.guiReferenceAutomation -and $report.guiReferenceAutomation.stage -cin @('gtgt-amendment-khbs-inspected','gtgt-amendment-khbs-not-matched')) {",probe)
  for text in ("format='htkk-khbs-native-output-staging-v1'","'DataFiles/9999999997/reference-khbs-output/01GTGT-khbs.xml'","(Join-Path $khbsEvidence 'khbs-native.xml')","Assert-Hash $khbsOriginal $gui.khbsExportSha256","$report.privateKhbsNativeOutputEvidence=@{status='staged'"):self.assertIn(text,probe)
  step=workflow.split('- name: Retain raw native KHBS export privately',1)[1].split('- name:',1)[0]
  self.assertIn("inputs.gui_automation == 'gtgt-amendment-khbs-inspect' && inputs.web_artifact_commit != ''",step);self.assertIn('run: python ./scripts/publish-htkk-khbs-native-output.py',step)
  self.assertNotIn("steps.native_probe.outcome == 'success'",step)

def native_of(web,created='2026-11-20',provider='A'*32):
 """In-memory native-shaped copy of the web input: HTKK service identity, BOM, current creation date."""
 text=web.decode('utf-8')
 for name,value in (('maDVu','HTKK'),('tenDVu','HỖ TRỢ KÊ KHAI THUẾ'),('pbanDVu','5.8.2'),('ttinNhaCCapDVu',provider)):text=re.sub('<'+name+'>[^<]*</'+name+'>','<'+name+'>'+value+'</'+name+'>',text,count=1)
 text=re.sub('<ngayLapTKhai>[^<]*<','<ngayLapTKhai>'+created+'<',text,count=1)
 return ('\ufeff'+text).encode('utf-8')

class NativeOutput(unittest.TestCase):
 def provenance(self,web,native,case,matched=True,mask=0,leaves=270,first=0,state=1):
  return {'format':'htkk-khbs-native-output-staging-v1','builderRepository':out.BUILDER,'builderCommit':BUILDER_SHA,'runId':'123','runAttempt':1,'sourceRepository':out.REPO,'sourceCommit':SOURCE,'sourceVersion':'5.8.2','runtimeHost':'clr2-x86-reference','caseId':case,'artifactCommit':ARTIFACT,
          'inputsSynthetic':True,'originalProcessStopped':True,'originalSourcesUnmodified':True,'inputMode':'khbs-c0-save-b1-import-summary-reexport','originalImportSucceeded':True,'originalSummarySucceeded':True,'originalExportSucceeded':True,'originalExporterValidatedSchema':True,
          'webImportInputSha256':hashlib.sha256(web).hexdigest(),'originalOutputSha256':hashlib.sha256(native).hexdigest(),'originalOutputBytes':len(native),'harnessTreeMatched':matched,'harnessMismatchMask':mask,'harnessLeafCount':leaves,'harnessFirstDifferenceOrdinal':first,'harnessOpenMainState':state,'harnessIdentityMatched':True,'harnessCreationDateValid':True,
          'creationDateRule':'native-export-current-date','fullRoundTrip':False}
 def fake_api(self,web,manifest,prior=None):
  calls=[]
  def envelope(body,name):return {'type':'file','name':name,'path':name,'encoding':'base64','size':len(body),'content':base64.encodebytes(body).decode(),'sha':hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest()}
  def fetch(path,token,payload=None,method=None):
   calls.append((path,token,payload,method))
   if path=='':return {'private':True,'full_name':out.REPO}
   if path in ('/git/commits/'+SOURCE,'/git/commits/'+ARTIFACT):return {'sha':path.rsplit('/',1)[1]}
   if path=='/contents/manifest.json?ref='+ARTIFACT:return envelope(json.dumps(manifest,ensure_ascii=False).encode(),'manifest.json')
   if path=='/contents/01GTGT-web.xml?ref='+ARTIFACT:return envelope(web,'01GTGT-web.xml')
   if prior is not None and path=='/contents/01GTGT-prior.xml?ref='+ARTIFACT:return envelope(prior,'01GTGT-prior.xml')
   if path=='/git/blobs':
    body=base64.b64decode(payload['content']);return {'sha':hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest()}
   if path=='/git/trees':return {'sha':'d'*40}
   if path=='/git/commits':return {'sha':'e'*40}
   if path.startswith('/git/ref/heads/'):raise urllib.error.HTTPError('https://api.github.com/',404,'SECRET',{},None)
   if path=='/git/refs':return {'ref':payload['ref'],'object':{'type':'commit','sha':payload['sha']}}
   raise AssertionError('Unexpected fixed API path')
  return fetch,calls
 def test_matching_native_export_is_retained_byte_exact_with_an_independent_comparison(self):
  for case,leaves in ((CASE,270),(CASE2,296)):
   web=f.sale_fixture(case);manifest=f.case_manifest(web,case);native=native_of(web);fetch,calls=self.fake_api(web,manifest)
   status=out.publish(native,self.provenance(web,native,case,leaves=leaves),'token',fetch,TODAY,version='5.8.2')
   self.assertEqual((status['status'],status['allTaxValuesMatched'],status['mismatchSectionMask'],status['firstDifferenceOrdinal'],status['harnessAgreement']),('published',True,0,0,True))
   blobs=[base64.b64decode(c[2]['content']) for c in calls if c[0]=='/git/blobs'];self.assertEqual(blobs[0],native)
   stored=json.loads(blobs[1]);self.assertEqual(stored['comparison']['checkedTaxLeafCount'],leaves);self.assertEqual(stored['files'],{'khbs-native.xml':{'sha256':hashlib.sha256(native).hexdigest(),'bytes':len(native)}})
   self.assertIs(stored['qualificationGranted'],False)
   ref=next(c for c in calls if c[0]=='/git/refs');self.assertEqual(ref[2]['ref'],'refs/heads/'+out.oracle.output_branch(out.BRANCHES[case],'5.8.2'))
   self.assertEqual(calls[0][0],'')  # the private input is downloaded before any upload
 def test_lan2_provenance_carries_its_round_2_main_state_and_publishes_with_the_prior_file(self):
  """Run 43402236959: the lần-2 export matched (270 leaves) but retention was refused as PROVENANCE, because the B2 sheet
  opens on the saved B1 (khbsOpenMainState 3) and the publisher only accepted 0..2. Each case accepts exactly its own states."""
  self.assertEqual({case:w.khbs.open_main_states(case) for case in w.khbs.CASES},{CASE:(1,),CASE2:(1,2),CASE3:(1,3)})
  web=f.sale_fixture(CASE3);manifest=f.case_manifest(web,CASE3);prior=f.sale_fixture(CASE);native=native_of(web);fetch,calls=self.fake_api(web,manifest,prior)
  status=out.publish(native,self.provenance(web,native,CASE3,state=3),'token',fetch,TODAY,version='5.8.2')
  self.assertEqual((status['status'],status['allTaxValuesMatched'],status['harnessAgreement']),('published',True,True))
  self.assertIn('/contents/01GTGT-prior.xml?ref='+ARTIFACT,[c[0] for c in calls])
  ref=next(c for c in calls if c[0]=='/git/refs');self.assertEqual(ref[2]['ref'],'refs/heads/gtgt-web-native-khbs-lan2-sale10-output-htkk582')
  for case,state in ((CASE,3),(CASE,2),(CASE2,3),(CASE3,2),(CASE3,0),(CASE3,4)):
   body=f.sale_fixture(case);n=native_of(body)
   with self.subTest(case=case,state=state),self.assertRaises(out.OutputError) as error:
    out.validate_provenance(json.dumps(self.provenance(body,n,case,state=state)).encode(),n,'123',BUILDER_SHA,SOURCE,case,ARTIFACT,'1','5.8.2')
   self.assertEqual(error.exception.code,'PROVENANCE')
  for case,state in ((CASE,1),(CASE2,2),(CASE3,3),(CASE3,1)):
   body=f.sale_fixture(case);n=native_of(body)
   self.assertEqual(out.validate_provenance(json.dumps(self.provenance(body,n,case,state=state)).encode(),n,'123',BUILDER_SHA,SOURCE,case,ARTIFACT,'1','5.8.2')['harnessOpenMainState'],state)
 def test_mismatching_native_export_is_still_retained_and_the_disagreement_is_bounded(self):
  web=f.sale_fixture(CASE2);manifest=f.case_manifest(web,CASE2);native=native_of(web).replace(b'<ct3a_2>24</ct3a_2>',b'<ct3a_2>23</ct3a_2>',1).replace(b'<ct3b>1440</ct3b>',b'<ct3b>1380</ct3b>',1)
  fetch,calls=self.fake_api(web,manifest);comparison=out.compare_tree(web,native,CASE2)
  self.assertEqual((comparison['allTaxValuesMatched'],comparison['mismatchSectionMask'],len(comparison['mismatchLeafOrdinals'])),(False,16,2))
  status=out.publish(native,self.provenance(web,native,CASE2,False,16,296,comparison['firstDifferenceOrdinal']),'token',fetch,TODAY,version='5.8.2')
  self.assertEqual((status['status'],status['allTaxValuesMatched'],status['mismatchSectionMask'],status['harnessAgreement']),('published',False,16,True))
  self.assertNotIn('1380',json.dumps(status));self.assertNotIn('23<',json.dumps(status))
 def test_native_privacy_identity_date_and_texts_are_checked_against_the_case_input(self):
  web=f.sale_fixture(CASE2);native=native_of(web)
  self.assertTrue(out.validate_native(native,web,CASE2,TODAY,'5.8.2')['privacyValuesVerified'])
  for body,code,rule in ((native.replace(b'<maDVu>HTKK<',b'<maDVu>CCKK<',1),'NATIVE_IDENTITY',None),(native_of(web,provider='a'*32),'NATIVE_IDENTITY',None),(native_of(web,'2026-11-01'),'NATIVE_DATE',None),
                         (native.replace(b'<ct2_ten>Thu',b'<ct2_ten>PRIVATE CUSTOMER Thu',1),'XML_PRIVACY','PRIVACY'),(native.replace(b'<mst>9999999997<',b'<mst>0101234567<',1),'XML_PRIVACY','IDENTITY'),
                         (native.replace(b'id="ID_1"',b'id="SECRET"',1),'XML_PRIVACY','ATTRIBUTES'),(native.replace(b'<ct3b>1440</ct3b>',b'<ct3b>1440<!-- x --></ct3b>',1),'XML_DECLARATION',None)):
   self.assertNotEqual(body,native)
   with self.subTest(code=code,rule=rule),self.assertRaises(out.OutputError) as error:out.validate_native(body,web,CASE2,TODAY,'5.8.2')
   status=out.safe_failure(error.exception);self.assertEqual(status['code'],code)
   if rule:self.assertEqual(status['nativeRule'],rule)
   for secret in ('PRIVATE','0101234567','SECRET'):self.assertNotIn(secret,json.dumps(status))
  # Numbers HTKK computes differently stay retainable (bounded shapes); unknown text never does.
  self.assertTrue(out.validate_native(native.replace(b'<ct3b>1440</ct3b>',b'<ct3b>-1.440</ct3b>',1),web,CASE2,TODAY,'5.8.2')['privacyValuesVerified'])
 def test_provenance_is_exact_and_the_staging_reader_takes_only_the_two_names(self):
  web=f.sale_fixture(CASE);native=native_of(web);value=self.provenance(web,native,CASE)
  for key,bad in (('caseId','01GTGT-sale10-M10-2026'),('harnessMismatchMask',256),('inputMode','web-xml-import-reexport'),('originalOutputBytes',1),('fullRoundTrip',True)):
   broken=dict(value);broken[key]=bad
   with self.subTest(key=key),self.assertRaises(out.OutputError):out.validate_provenance(json.dumps(broken).encode(),native,'123',BUILDER_SHA,SOURCE,CASE if key!='caseId' else bad,ARTIFACT,'1','5.8.2')
  with tempfile.TemporaryDirectory() as temp:
   directory=pathlib.Path(temp)/out.DIRECTORY;directory.mkdir();(directory/'khbs-native.xml').write_bytes(native);(directory/'provenance.json').write_text(json.dumps(value))
   got,metadata=out.read_evidence(directory,'123',BUILDER_SHA,SOURCE,CASE,ARTIFACT,'1','5.8.2');self.assertEqual(got,native);self.assertEqual(metadata['caseId'],CASE)
   (directory/'extra.txt').write_text('x')
   with self.assertRaises(out.OutputError):out.read_evidence(directory,'123',BUILDER_SHA,SOURCE,CASE,ARTIFACT,'1','5.8.2')

if __name__=='__main__':unittest.main()
