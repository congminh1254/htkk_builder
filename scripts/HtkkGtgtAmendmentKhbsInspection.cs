// Own bounded ORIGINAL amendment (kê khai bổ sung lần 1, KHBS) observation of D1 01/GTGT 2.8.3 on HTKK 5.8.2.
// Flow (KHBS-NATIVE-CASE.md): C0 Ghi (HtkkGtgtAmendmentInspection.cs; zero, or for case 2 two fixed original edits)
// -> original Đóng -> reopen D1 10/2026 (case 2: 09/2026) with
// OptBosung and the fixed ngày lập 13/11/2026 (HtkkGtgtAmendmentOpenInspection.cs) -> original "Nhập từ XML" of the
// fixed web B1 file (cmdImportXML_Click 0x060003AC: LoaiToKhai B -> RevertFromXml, message 0291) -> original
// "Tổng hợp KHBS" (btnTongHopKHBS_Click 0x060003C1, message 0222) -> original "Kết xuất" XML -> whole-tree comparison
// with the web input. No XML is authored here. Only booleans, counts, message ids, a mismatch mask and the first
// differing leaf ordinal are recorded; never values, paths or text.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Reflection;
using System.Text;
using System.Windows.Forms;
using System.Xml;
public sealed partial class HtkkGuiReferenceAutomation {
 private const string KhbsWebCaseId="01GTGT-khbs-zero-to-sale10-M10-2026";
 // Case 2 (htkk_web producer khbs-sale5-to-sale10): M09/2026, due 20/10/2026, so the same fixed ngày lập gives 24 late
 // days. Its C0 is typed through the original grid before Ghi ([30] 2.000.000 at 5%, [32] 1.000.000 at 10%), and the web
 // B1 file moves [30] to 0 and [32] to 4.000.000 (negative chênh lệch rows [30]/[31]).
 private const string KhbsSale5WebCaseId="01GTGT-khbs-sale5-to-sale10-M09-2026";
 private const string KhbsFixedDate="13/11/2026";
 // 270 (case 1) / 296 (case 2) leaves of the fixed web B1 file without the four TTinDVu leaves.
 private const int KhbsLeafTarget=270,KhbsSale5LeafTarget=296;
 private static bool KhbsCaseId(string id){return id==KhbsWebCaseId||id==KhbsSale5WebCaseId;}
 private bool KhbsNonzeroOriginal(){return KhbsMode()&&webInputVerified&&webCaseId==KhbsSale5WebCaseId;}
 // The only period month of the D1 drivers: 10, or 09 for KHBS case 2 (GetPeriodInfo pads Thang to two digits, 0x0efc).
 private string PeriodMonth(){return KhbsNonzeroOriginal()?"09":"10";}
 // Exact C0 money of case 2 in the fixed 27-indicator order of InspectMoneyZero / InspectOriginalPriorFile
 // (ct22 ... ct43): [27] 3.000.000, [28] 200.000, [30] 2.000.000, [31] 100.000, [32] 1.000.000, [33] 100.000,
 // [34] 3.000.000, [35] 200.000, [36] 200.000, [40a] 200.000, [40] 200.000.
 private static readonly decimal[] KhbsSale5Original=new decimal[]{0,0,0,0,0,0,0,3000000,200000,0,2000000,100000,1000000,100000,0,3000000,200000,200000,0,0,0,200000,0,200000,0,0,0};
 private bool khbsOriginalMoneyMatched=false,khbsSavedMoneyMatched=false;private int khbsOpenMainState=0;
 private static bool KhbsAmount(object value,out decimal number){
  number=Decimal.Zero;if(value==null||value==DBNull.Value)return false;string text=Convert.ToString(value,CultureInfo.InvariantCulture);
  return Decimal.TryParse(text,NumberStyles.Number,CultureInfo.InvariantCulture,out number);
 }
 private bool KhbsOriginalVector(object sheet){
  int[,] coordinates=new int[,] {{36,11},{39,9},{39,11},{40,9},{40,11},{41,11},{43,9},{44,9},{44,11},{45,9},{46,9},{46,11},{47,9},{47,11},{48,9},{49,9},{49,11},{50,11},{52,11},{53,11},{54,11},{56,11},{57,11},{58,11},{59,11},{60,11},{61,11}};
  for(int index=0;index<coordinates.GetLength(0);index++){decimal number;if(!KhbsAmount(Get(Cell(sheet,coordinates[index,0],coordinates[index,1]),"Value"),out number)||number!=KhbsSale5Original[index])return false;}
  return true;
 }
 private bool PriorSavedMoneyExpected(){return KhbsNonzeroOriginal()?khbsSavedMoneyMatched:amendmentPriorSavedMoneyZero;}
 // Case 2 only, on the proven zero C0 sheet: two fixed original edits, each committed through the original editor and
 // waited for the original auto-calculation; true once the whole fixed C0 vector is on the sheet (then Ghi).
 private bool PrepareKhbsOriginal(Form owner,Control grid,object sheet){
  gtgtAutoCalculationReady=Convert.ToBoolean(Get(sheet,"AutoCalculation"));object business=Global("InstanceClass");gtgtBusinessInstanceMatched=business!=null&&business.GetType().FullName=="TAX.HTKK.Business.Gtgt01TT80Nckt283";
  if(!KhbsNonzeroOriginal()||amendmentPriorSaveInvoked)throw new InvalidOperationException();
  if(!gtgtAutoCalculationReady||!gtgtBusinessInstanceMatched||!owner.Enabled||!grid.Enabled||OriginalMessageVisible()){SetStage(HtkkAutomationStage.WaitingGtgtSheet);Record();return false;}
  if(webCaseEditCount==0){
   if(!gtgtZero||gtgtEmptyMoney!=0||Convert.ToBoolean(Get(Cell(sheet,46,9),"Locked")))throw new InvalidOperationException();
   webCaseEdited=true;webCaseEditClock=Stopwatch.StartNew();EditOriginalGtgtCase(grid,sheet,46,9,"2000000",HtkkAutomationStage.GtgtCaseEditing);return false;
  }
  if(webCaseEditCount==1){
   decimal tax;if(!KhbsAmount(Get(Cell(sheet,46,11),"Value"),out tax)||tax!=100000){if(webCaseEditClock.Elapsed.TotalSeconds<2){SetStage(HtkkAutomationStage.WaitingGtgtSheet);Record();return false;}throw new InvalidOperationException();}
   if(Convert.ToBoolean(Get(Cell(sheet,47,9),"Locked")))throw new InvalidOperationException();
   webCaseEditClock=Stopwatch.StartNew();EditOriginalGtgtCase(grid,sheet,47,9,"1000000",HtkkAutomationStage.GtgtCaseEditing);return false;
  }
  if(webCaseEditCount!=2)throw new InvalidOperationException();
  khbsOriginalMoneyMatched=gtgtEmptyMoney==0&&KhbsOriginalVector(sheet);
  if(!khbsOriginalMoneyMatched){if(webCaseEditClock.Elapsed.TotalSeconds<2){SetStage(HtkkAutomationStage.WaitingGtgtSheet);Record();return false;}throw new InvalidOperationException();}
  return true;
 }
 private bool khbsDateTyped=false,khbsPeriodMatched=false,khbsImportInvoked=false,khbsImportSucceeded=false,khbsImportPathMatched=false,khbsSummaryInvoked=false,khbsSummaryAcknowledged=false,khbsExportInvoked=false,khbsExportSchemaPinnedVerified=false,khbsExportSucceeded=false,khbsIdentityMatched=false,khbsCreationDateValid=false,khbsTreeMatched=false;
 private int khbsImportMessageId=0,khbsSummaryMessageId=0,khbsExportMessageId=0,khbsLeafCount=0,khbsMismatchMask=0,khbsFirstDifferenceOrdinal=0,khbsExportBytes=0;
 private string khbsExportSha256="",khbsPhase="not-started";private Form khbsOwner=null;private bool khbsBusy=false;
 private bool KhbsMode(){return mode=="gtgt-amendment-khbs-inspect";}
 private static bool KhbsDate(string text){DateTime parsed;return DateTime.TryParseExact(text,new string[]{"d/M/yyyy","dd/MM/yyyy"},CultureInfo.InvariantCulture,DateTimeStyles.None,out parsed)&&parsed.Date==new DateTime(2026,11,13);}
 private string KhbsJson(){
  string q=((char)34).ToString();StringBuilder json=new StringBuilder();
  string[] names=new string[]{"khbsDateTyped","khbsPeriodMatched","khbsImportInvoked","khbsImportSucceeded","khbsImportPathMatched","khbsSummaryInvoked","khbsSummaryAcknowledged","khbsExportInvoked","khbsExportSchemaPinnedVerified","khbsExportSucceeded","khbsIdentityMatched","khbsCreationDateValid","khbsTreeMatched","khbsOriginalMoneyMatched","khbsSavedMoneyMatched"};
  bool[] values=new bool[]{khbsDateTyped,khbsPeriodMatched,khbsImportInvoked,khbsImportSucceeded,khbsImportPathMatched,khbsSummaryInvoked,khbsSummaryAcknowledged,khbsExportInvoked,khbsExportSchemaPinnedVerified,khbsExportSucceeded,khbsIdentityMatched,khbsCreationDateValid,khbsTreeMatched,khbsOriginalMoneyMatched,khbsSavedMoneyMatched};
  for(int index=0;index<names.Length;index++)json.Append(","+q+names[index]+q+":"+Bool(values[index]));
  names=new string[]{"khbsImportMessageId","khbsSummaryMessageId","khbsExportMessageId","khbsLeafCount","khbsMismatchMask","khbsFirstDifferenceOrdinal","khbsExportBytes","khbsOpenMainState"};int[] counts=new int[]{khbsImportMessageId,khbsSummaryMessageId,khbsExportMessageId,khbsLeafCount,khbsMismatchMask,khbsFirstDifferenceOrdinal,khbsExportBytes,khbsOpenMainState};
  for(int index=0;index<names.Length;index++)json.Append(","+q+names[index]+q+":"+counts[index].ToString(CultureInfo.InvariantCulture));
  return json.ToString()+","+q+"khbsExportSha256"+q+":"+q+khbsExportSha256+q;
 }
 // KHBS case only, after the B1 defaults (Lần 1, today) were proven: the original ngày lập control gets the fixed date.
 private void TypeOriginalKhbsDate(Control period){
  if(!KhbsMode()||!amendmentOpenDefaultsMatched||khbsDateTyped)throw new InvalidOperationException();
  SetStage(HtkkAutomationStage.GtgtAmendmentKhbsDateTyping);Record();SetText(period,"mskNgayLapKHBS",KhbsFixedDate);
  khbsDateTyped=KhbsDate(ReadableNamed(period,"mskNgayLapKHBS").Text);if(!khbsDateTyped)throw new InvalidOperationException();
 }
 // Called once the B1 sheet, its two KHBS tabs, the unchanged C0 file and the fixed ngày lập are proven.
 private void StartOriginalKhbsImport(Form owner){
  if(!KhbsMode()||khbsPhase!="not-started"||!webInputVerified||!KhbsCaseId(webCaseId)||!khbsPeriodMatched||owner==null||owner.GetType().FullName!="HTKK.frmWinToKhai")throw new InvalidOperationException();
  if(Hash(webInputPath)!=webImportInputSha256)throw new InvalidOperationException();
  khbsOwner=owner;roundtripOwner=owner;khbsPhase="import-ready";SetStage(HtkkAutomationStage.GtgtAmendmentKhbsImportInvoking);Record();
  exportWatcher=new System.Windows.Forms.Timer();exportWatcher.Interval=100;exportWatcher.Tick+=delegate(object sender,EventArgs args){try{ContinueOriginalKhbs();}catch(Exception error){exportWatcher.Stop();Failure(error);}};exportWatcher.Start();
 }
 private Form KhbsMessage(out string text){
  text=null;Form found=null;
  foreach(Form form in Application.OpenForms){if(!form.Visible||form.GetType().FullName!="TAX.HTKK.Utilities.Control.frmMessage")continue;if(found!=null)throw new InvalidOperationException();found=form;}
  if(found==null)return null;Control[] labels=found.Controls.Find("lblThongBao",true);if(labels.Length!=1)throw new InvalidOperationException();text=labels[0].Text;return found;
 }
 private void CloseKhbsMessage(Form message){
  Control[] controls=message.Controls.Find("btn_2",true);if(controls.Length!=1||CountVisibleButtons(message)!=1)throw new InvalidOperationException();Button close=controls[0] as Button;
  if(close==null||!close.Visible||!close.Enabled||close.Text.Replace("&",String.Empty).Trim()!="Đóng")throw new InvalidOperationException();close.PerformClick();
 }
 private bool KhbsOwnerReady(){if(khbsOwner==null||khbsOwner.IsDisposed||khbsOwner.GetType().FullName!="HTKK.frmWinToKhai")throw new InvalidOperationException();return khbsOwner.Visible&&khbsOwner.Enabled&&!OriginalMessageVisible();}
 private void KhbsStop(HtkkAutomationStage stage){finished=true;SetStage(stage);Record();exportWatcher.Stop();}
 private void ContinueOriginalKhbs(){
  if(finished){exportWatcher.Stop();return;}if(khbsBusy||exportFilenameEditing)return;khbsBusy=true;
  try{
   string text;Form message;
   if(khbsPhase=="import-ready"){
    if(!KhbsOwnerReady())return;
    Button import=Named(khbsOwner,"cmdImportXML") as Button;if(import==null||import.FindForm()!=khbsOwner||import.Text.Replace("&",String.Empty).Trim()!="Nhập từ XML")throw new InvalidOperationException();
    khbsImportInvoked=true;roundtripImportCommandInvoked=true;khbsPhase="import-result";SetStage(HtkkAutomationStage.GtgtAmendmentKhbsImportWaiting);Record();
    khbsOwner.BeginInvoke(new MethodInvoker(delegate{try{import.PerformClick();}catch(Exception error){Failure(error);}}));return;
   }
   if(khbsPhase=="import-result"){
    message=KhbsMessage(out text);
    if(message==null){if(!roundtripImportDialogSubmitted)TrySubmitOriginalFileDialog("Chọn tờ khai để tải vào chương trình",webInputPath,true);return;}
    if(text!="Nhập dữ liệu từ XML thành công."){khbsImportMessageId=OriginalMessageCatalogueId(text);KhbsStop(HtkkAutomationStage.GtgtAmendmentKhbsImportRejected);return;}
    FieldInfo loading=OriginalAssembly().GetType("HTKK.frmWinToKhai",true).GetField("FileNameLoading",BindingFlags.Static|BindingFlags.Public|BindingFlags.NonPublic);
    if(loading==null||loading.FieldType!=typeof(string))throw new InvalidOperationException();string actual=(string)loading.GetValue(null);
    khbsImportPathMatched=!String.IsNullOrEmpty(actual)&&String.Equals(Path.GetFullPath(actual),Path.GetFullPath(webInputPath),StringComparison.OrdinalIgnoreCase);roundtripImportPathMatched=khbsImportPathMatched;
    if(!roundtripImportDialogMatched||!roundtripImportKeyboardCommitted||!roundtripImportDialogSubmitted||!khbsImportPathMatched){Record();throw new InvalidOperationException();}
    object period=Global("TTPeriodInfo");if(Convert.ToString(Get(period,"LoaiToKhai"),CultureInfo.InvariantCulture)!="B"||Convert.ToString(Get(period,"SoLan"),CultureInfo.InvariantCulture)!="1"||!KhbsDate(Convert.ToString(Get(period,"NgayLapKHBS"),CultureInfo.InvariantCulture)))throw new InvalidOperationException();
    khbsImportSucceeded=true;roundtripImportSucceeded=true;khbsPhase="summary-ready";SetStage(HtkkAutomationStage.GtgtAmendmentKhbsSummaryWaiting);Record();CloseKhbsMessage(message);return;
   }
   if(khbsPhase=="summary-ready"){
    if(!KhbsOwnerReady())return;
    Button summary=Named(khbsOwner,"btnTongHopKHBS") as Button;if(summary==null||summary.FindForm()!=khbsOwner||!summary.Visible||!summary.CanSelect)throw new InvalidOperationException();
    khbsSummaryInvoked=true;khbsPhase="summary-result";SetStage(HtkkAutomationStage.GtgtAmendmentKhbsSummaryInvoking);Record();
    khbsOwner.BeginInvoke(new MethodInvoker(delegate{try{summary.PerformClick();}catch(Exception error){Failure(error);}}));return;
   }
   if(khbsPhase=="summary-result"){
    message=KhbsMessage(out text);if(message==null){SetStage(HtkkAutomationStage.GtgtAmendmentKhbsSummaryResultWaiting);Record();return;}
    if(text!="Tổng hợp dữ liệu lên KHBS thành công"){khbsSummaryMessageId=OriginalMessageCatalogueId(text);KhbsStop(HtkkAutomationStage.GtgtAmendmentKhbsSummaryRejected);return;}
    khbsSummaryAcknowledged=true;khbsPhase="export-ready";SetStage(HtkkAutomationStage.GtgtAmendmentKhbsExportWaiting);Record();CloseKhbsMessage(message);return;
   }
   if(khbsPhase=="export-ready"){
    if(!KhbsOwnerReady())return;
    // LoaiToKhai B validates against the KHBS schema of the same declaration version (Menu.xml XsdSchema 01_GTGT_TT80).
    string schema=Path.Combine(Path.GetDirectoryName(project),"InterfaceTemplates/Validate/KHBS_01_GTGT_TT80_283.xsd");string actualSchema=Convert.ToString(Get(Global("ToKhaiInfo"),"XsdFileName"),CultureInfo.InvariantCulture);
    khbsExportSchemaPinnedVerified=!String.IsNullOrEmpty(actualSchema)&&String.Equals(Path.GetFullPath(actualSchema),Path.GetFullPath(schema),StringComparison.OrdinalIgnoreCase)&&Hash(schema)=="b0fcb96663749e897839db2c9c224c45b4f2ed779be508e1bf9f9a2f82daf76f";exportSchemaPinnedVerified=khbsExportSchemaPinnedVerified;
    if(!khbsExportSchemaPinnedVerified){Record();throw new InvalidOperationException();}
    string directory=Path.Combine(Path.Combine(Path.Combine(Path.GetDirectoryName(project),"DataFiles"),Mst),"reference-khbs-output");if(Directory.Exists(directory)||File.Exists(directory))throw new InvalidOperationException();Directory.CreateDirectory(directory);exportPath=Path.Combine(directory,"01GTGT-khbs.xml");exportDestinationFresh=true;
    Assembly utilities=null;foreach(Assembly loaded in AppDomain.CurrentDomain.GetAssemblies())if(loaded.GetName().Name=="TAX.HTKK.Utilities")utilities=loaded;if(utilities==null)throw new InvalidOperationException();
    Type configuration=utilities.GetType("TAX.HTKK.Utilities.Core.HTKKConfig",true);PropertyInfo temporary=configuration.GetProperty("PATH_TEMP",BindingFlags.Public|BindingFlags.Static);if(temporary==null)throw new InvalidOperationException();expectedSaveTitle="Tệp XML kết xuất tới thư mục "+Convert.ToString(temporary.GetValue(null,null),CultureInfo.InvariantCulture);
    Button command=Named(khbsOwner,"cmdExport") as Button;if(command==null||command.FindForm()!=khbsOwner||command.Text.Replace("&",String.Empty).Trim()!="Kết xuất")throw new InvalidOperationException();
    khbsExportInvoked=true;exportCommandInvoked=true;khbsPhase="exporting";SetStage(HtkkAutomationStage.GtgtAmendmentKhbsExportInvoking);Record();
    khbsOwner.BeginInvoke(new MethodInvoker(delegate{try{command.PerformClick();}catch(Exception error){Failure(error);}}));return;
   }
   if(khbsPhase=="exporting"){
    message=KhbsMessage(out text);
    if(message!=null){
     if(text!="Kết xuất tờ khai xml thành công."){khbsExportMessageId=OriginalMessageCatalogueId(text);exportRejectedMessageId=khbsExportMessageId;KhbsStop(HtkkAutomationStage.GtgtAmendmentKhbsExportRejected);return;}
     InspectOriginalExportDestination();ReadOriginalExport();if(!exportOriginalPathMatched||!exportDialogSubmitted||!exportXmlRootMatched||!exportSyntheticIdentityMatched)throw new InvalidOperationException();
     exportSuccessAcknowledged=true;khbsExportSucceeded=true;khbsExportBytes=exportBytes;khbsExportSha256=exportSha256;
     SetStage(HtkkAutomationStage.GtgtAmendmentKhbsComparing);Record();
     if(Hash(webInputPath)!=webImportInputSha256)throw new InvalidOperationException();
     XmlDocument input=ReadBoundedOriginalXml(webInputPath),output=ReadBoundedOriginalXml(exportPath);
     khbsTreeMatched=HtkkWebTaxComparison.CompareKhbs(input,output,webCaseId==KhbsSale5WebCaseId?KhbsSale5LeafTarget:KhbsLeafTarget,out khbsLeafCount,out khbsMismatchMask,out khbsFirstDifferenceOrdinal,out khbsIdentityMatched,out khbsCreationDateValid);
     if(Hash(exportPath)!=khbsExportSha256)throw new InvalidOperationException();
     finished=true;SetStage(khbsTreeMatched?HtkkAutomationStage.GtgtAmendmentKhbsInspected:HtkkAutomationStage.GtgtAmendmentKhbsNotMatched);Record();exportWatcher.Stop();CloseKhbsMessage(message);return;
    }
    if(!exportButtonInvoked){
     List<Form> selectors=new List<Form>();int count=0;foreach(Form top in Application.OpenForms)if(top.Visible)FindExportSelectors(top,selectors,ref count);if(selectors.Count==0)return;if(selectors.Count!=1)throw new InvalidOperationException();Form selector=selectors[0];
     RadioButton xml=Named(selector,"radKetXuatXML") as RadioButton,excel=Named(selector,"radKetXuatExcel") as RadioButton;Button button=Named(selector,"btnExport") as Button;
     if(xml==null||excel==null||!xml.Checked||excel.Checked||xml.Text!="Kết xuất XML"||button==null||button.FindForm()!=selector||button.Text.Replace("&",String.Empty).Trim()!="Kết xuất")throw new InvalidOperationException();
     exportSelectorMatched=true;exportButtonInvoked=true;SetStage(HtkkAutomationStage.GtgtExportFileDialogWaiting);Record();selector.BeginInvoke(new MethodInvoker(delegate{try{button.PerformClick();}catch(Exception error){Failure(error);}}));return;
    }
    if(!exportDialogSubmitted)TrySubmitOriginalFileDialog(expectedSaveTitle,exportPath,false);
    return;
   }
   throw new InvalidOperationException();
  }finally{khbsBusy=false;}
 }
}
