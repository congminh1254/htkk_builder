// Own bounded ORIGINAL amendment (kê khai bổ sung lần 1, KHBS) observation of D1 01/GTGT 2.8.3 on HTKK 5.8.2.
// Flow (KHBS-NATIVE-CASE.md): C0 zero Ghi (HtkkGtgtAmendmentInspection.cs) -> original Đóng -> reopen D1 10/2026 with
// OptBosung and the fixed ngày lập 13/11/2026 (HtkkGtgtAmendmentOpenInspection.cs) -> original "Nhập từ XML" of the
// fixed web B1 file (cmdImportXML_Click 0x060003AC: LoaiToKhai B -> RevertFromXml, message 0291) -> original
// "Tổng hợp KHBS" (btnTongHopKHBS_Click 0x060003C1, message 0222) -> original "Kết xuất" XML -> whole-tree comparison
// with the web input. No XML is authored here. Only booleans, counts, message ids, a mismatch mask and the first
// differing leaf ordinal are recorded; never values, paths or text.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Reflection;
using System.Text;
using System.Windows.Forms;
using System.Xml;
public sealed partial class HtkkGuiReferenceAutomation {
 private const string KhbsWebCaseId="01GTGT-khbs-zero-to-sale10-M10-2026";
 private const string KhbsFixedDate="13/11/2026";
 // 270 leaves of the fixed web B1 file without the four TTinDVu leaves (htkk_web producer khbs-zero-to-sale10).
 private const int KhbsLeafTarget=270;
 private bool khbsDateTyped=false,khbsPeriodMatched=false,khbsImportInvoked=false,khbsImportSucceeded=false,khbsImportPathMatched=false,khbsSummaryInvoked=false,khbsSummaryAcknowledged=false,khbsExportInvoked=false,khbsExportSchemaPinnedVerified=false,khbsExportSucceeded=false,khbsIdentityMatched=false,khbsCreationDateValid=false,khbsTreeMatched=false;
 private int khbsImportMessageId=0,khbsSummaryMessageId=0,khbsExportMessageId=0,khbsLeafCount=0,khbsMismatchMask=0,khbsFirstDifferenceOrdinal=0,khbsExportBytes=0;
 private string khbsExportSha256="",khbsPhase="not-started";private Form khbsOwner=null;private bool khbsBusy=false;
 private bool KhbsMode(){return mode=="gtgt-amendment-khbs-inspect";}
 private static bool KhbsDate(string text){DateTime parsed;return DateTime.TryParseExact(text,new string[]{"d/M/yyyy","dd/MM/yyyy"},CultureInfo.InvariantCulture,DateTimeStyles.None,out parsed)&&parsed.Date==new DateTime(2026,11,13);}
 private string KhbsJson(){
  string q=((char)34).ToString();StringBuilder json=new StringBuilder();
  string[] names=new string[]{"khbsDateTyped","khbsPeriodMatched","khbsImportInvoked","khbsImportSucceeded","khbsImportPathMatched","khbsSummaryInvoked","khbsSummaryAcknowledged","khbsExportInvoked","khbsExportSchemaPinnedVerified","khbsExportSucceeded","khbsIdentityMatched","khbsCreationDateValid","khbsTreeMatched"};
  bool[] values=new bool[]{khbsDateTyped,khbsPeriodMatched,khbsImportInvoked,khbsImportSucceeded,khbsImportPathMatched,khbsSummaryInvoked,khbsSummaryAcknowledged,khbsExportInvoked,khbsExportSchemaPinnedVerified,khbsExportSucceeded,khbsIdentityMatched,khbsCreationDateValid,khbsTreeMatched};
  for(int index=0;index<names.Length;index++)json.Append(","+q+names[index]+q+":"+Bool(values[index]));
  names=new string[]{"khbsImportMessageId","khbsSummaryMessageId","khbsExportMessageId","khbsLeafCount","khbsMismatchMask","khbsFirstDifferenceOrdinal","khbsExportBytes"};int[] counts=new int[]{khbsImportMessageId,khbsSummaryMessageId,khbsExportMessageId,khbsLeafCount,khbsMismatchMask,khbsFirstDifferenceOrdinal,khbsExportBytes};
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
  if(!KhbsMode()||khbsPhase!="not-started"||!webInputVerified||webCaseId!=KhbsWebCaseId||!khbsPeriodMatched||owner==null||owner.GetType().FullName!="HTKK.frmWinToKhai")throw new InvalidOperationException();
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
     khbsTreeMatched=HtkkWebTaxComparison.CompareKhbs(input,output,KhbsLeafTarget,out khbsLeafCount,out khbsMismatchMask,out khbsFirstDifferenceOrdinal,out khbsIdentityMatched,out khbsCreationDateValid);
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
