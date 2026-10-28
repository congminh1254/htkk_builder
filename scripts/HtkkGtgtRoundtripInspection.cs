// Own original-GUI import/reexport observation. Never authors a tax XML file.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Reflection;
using System.Text;
using System.Windows.Forms;
using System.Xml;
public sealed partial class HtkkGuiReferenceAutomation {
 private string roundtripPhase="not-started",firstExportPath="",firstExportSha256="",roundtripReexportSha256="";
 private Form roundtripOwner=null;private int firstExportBytes=0,roundtripReexportBytes=0,roundtripImportCheckedMoneyCount=0;
 private bool roundtripImportCommandInvoked=false,roundtripImportDialogMatched=false,roundtripImportKeyboardCommitted=false,roundtripImportDialogSubmitted=false,roundtripImportPathMatched=false,roundtripImportSheetMatched=false,roundtripImportSucceeded=false,roundtripReexportCommandInvoked=false,roundtripReexportSucceeded=false,roundtripXmlExactMatched=false;
 private string RoundtripJson(){
  string q=((char)34).ToString();StringBuilder json=new StringBuilder();
  string[] names=new string[]{"roundtripImportCommandInvoked","roundtripImportDialogMatched","roundtripImportKeyboardCommitted","roundtripImportDialogSubmitted","roundtripImportPathMatched","roundtripImportSheetMatched","roundtripImportSucceeded","roundtripReexportCommandInvoked","roundtripReexportSucceeded","roundtripXmlExactMatched"};
  bool[] values=new bool[]{roundtripImportCommandInvoked,roundtripImportDialogMatched,roundtripImportKeyboardCommitted,roundtripImportDialogSubmitted,roundtripImportPathMatched,roundtripImportSheetMatched,roundtripImportSucceeded,roundtripReexportCommandInvoked,roundtripReexportSucceeded,roundtripXmlExactMatched};
  for(int index=0;index<names.Length;index++)json.Append(","+q+names[index]+q+":"+Bool(values[index]));
  json.Append(","+q+"roundtripImportCheckedMoneyCount"+q+":"+roundtripImportCheckedMoneyCount+","+q+"roundtripReexportBytes"+q+":"+roundtripReexportBytes+","+q+"roundtripReexportSha256"+q+":"+q+roundtripReexportSha256+q);return json.ToString()+WebInputJson();
 }
 private bool OriginalMessageVisible(){foreach(Form form in Application.OpenForms)if(form.Visible&&form.GetType().FullName=="TAX.HTKK.Utilities.Control.frmMessage")return true;return false;}
 private bool OriginalRoundtripOwnerReady(){
  if(roundtripOwner==null||roundtripOwner.IsDisposed||roundtripOwner.GetType().FullName!="HTKK.frmWinToKhai")throw new InvalidOperationException();
  return roundtripOwner.Visible&&roundtripOwner.Enabled&&!OriginalMessageVisible();
 }
 private void ContinueOriginalRoundtrip(){
  if((mode!="gtgt-roundtrip-inspect"&&mode!="gtgt-web-import-inspect")||!exportSuccessAcknowledged||String.IsNullOrEmpty(firstExportPath)||Hash(firstExportPath)!=firstExportSha256)throw new InvalidOperationException();
  if(mode=="gtgt-web-import-inspect"&&(!webInputVerified||Hash(webInputPath)!=webImportInputSha256))throw new InvalidOperationException();
  if(roundtripPhase=="waiting-import-ready"){
   if(!OriginalRoundtripOwnerReady())return;
   Button import=Named(roundtripOwner,"cmdImportXML") as Button;if(import==null||import.FindForm()!=roundtripOwner||import.Text.Replace("&",String.Empty).Trim()!="Nhập từ XML"||roundtripImportCommandInvoked)throw new InvalidOperationException();
   roundtripImportCommandInvoked=true;roundtripPhase="waiting-import-result";SetStage(HtkkAutomationStage.GtgtImportFileDialogWaiting);Record();
   roundtripOwner.BeginInvoke(new MethodInvoker(delegate{try{import.PerformClick();}catch(Exception error){Failure(error);}}));return;
  }
  if(roundtripPhase=="waiting-import-result"){
   foreach(Form message in Application.OpenForms){if(!message.Visible||message.GetType().FullName!="TAX.HTKK.Utilities.Control.frmMessage")continue;
    Control[] labels=message.Controls.Find("lblThongBao",true);if(labels.Length!=1)throw new InvalidOperationException();
    if(labels[0].Text!="Nhập dữ liệu từ XML thành công."){SetStage(HtkkAutomationStage.GtgtImportOriginalMessageRejected);finished=true;Record();exportWatcher.Stop();return;}
    SetStage(HtkkAutomationStage.GtgtImportSuccessSheetChecking);
    FieldInfo loading=OriginalAssembly().GetType("HTKK.frmWinToKhai",true).GetField("FileNameLoading",BindingFlags.Static|BindingFlags.Public|BindingFlags.NonPublic);
    if(loading==null||loading.FieldType!=typeof(string))throw new InvalidOperationException();string actual=(string)loading.GetValue(null);
    roundtripImportPathMatched=!String.IsNullOrEmpty(actual)&&String.Equals(Path.GetFullPath(actual),Path.GetFullPath(RoundtripInputPath()),StringComparison.OrdinalIgnoreCase);Record();
    if(!roundtripImportCommandInvoked||!roundtripImportDialogMatched||!roundtripImportKeyboardCommitted||!roundtripImportDialogSubmitted||!roundtripImportPathMatched)throw new InvalidOperationException();
    roundtripImportSheetMatched=InspectOriginalImportedSheet();Record();if(!roundtripImportSheetMatched)throw new InvalidOperationException();
    Control[] controls=message.Controls.Find("btn_2",true);if(message.Text.Trim()!="Thông Báo"||controls.Length!=1||CountVisibleButtons(message)!=1)throw new InvalidOperationException();Button close=controls[0] as Button;if(close==null||!close.Visible||!close.Enabled||close.Text.Replace("&",String.Empty).Trim()!="Đóng")throw new InvalidOperationException();
    roundtripImportSucceeded=true;roundtripPhase="waiting-reexport-ready";SetStage(HtkkAutomationStage.GtgtReexportReadyWaiting);Record();close.PerformClick();return;
   }
   if(!roundtripImportDialogSubmitted)TrySubmitOriginalFileDialog("Chọn tờ khai để tải vào chương trình",RoundtripInputPath(),true);
   return;
  }
  if(roundtripPhase=="waiting-reexport-ready"){
   if(!OriginalRoundtripOwnerReady())return;
   if(!roundtripImportSucceeded||!InspectOriginalImportedSheet()||roundtripReexportCommandInvoked)throw new InvalidOperationException();
   string schema=Path.Combine(Path.GetDirectoryName(project),"InterfaceTemplates/Validate/01_GTGT_TT80_283.xsd");string actualSchema=Convert.ToString(Get(Global("ToKhaiInfo"),"XsdFileName"),CultureInfo.InvariantCulture);
   if(String.IsNullOrEmpty(actualSchema)||!String.Equals(Path.GetFullPath(actualSchema),Path.GetFullPath(schema),StringComparison.OrdinalIgnoreCase)||Hash(schema)!="8d4c0d88100e858ddfe221d080a6a338776d1364c7de04347bfb990d04833003")throw new InvalidOperationException();
   exportPath=Path.Combine(Path.GetDirectoryName(firstExportPath),"01GTGT-roundtrip.xml");if(File.Exists(exportPath))throw new InvalidOperationException();
   Button export=Named(roundtripOwner,"cmdExport") as Button;if(export==null||export.FindForm()!=roundtripOwner||export.Text.Replace("&",String.Empty).Trim()!="Kết xuất")throw new InvalidOperationException();
   exportButtonInvoked=false;exportDialogSubmitted=false;roundtripReexportCommandInvoked=true;roundtripPhase="reexporting";SetStage(HtkkAutomationStage.GtgtReexportCommandInvoking);Record();
   roundtripOwner.BeginInvoke(new MethodInvoker(delegate{try{export.PerformClick();}catch(Exception error){Failure(error);}}));return;
  }
  throw new InvalidOperationException();
 }
 private bool InspectOriginalImportedSheet(){
  List<Control> grids=new List<Control>();int count=0;GatherSpreads(roundtripOwner,grids,ref count);if(grids.Count!=1)return false;
  object sheets=Get(grids[0],"Sheets");PropertyInfo item=sheets.GetType().GetProperty("Item",new Type[]{typeof(int)});if(item==null)return false;object sheet=item.GetValue(sheets,new object[]{0});
  if(Convert.ToInt32(Get(sheet,"RowCount"))!=72||Convert.ToInt32(Get(sheet,"ColumnCount"))!=24||CellText(sheet,9,3)!=FakeName||CellText(sheet,10,3).Replace("-",String.Empty)!=Mst||CellText(sheet,63,10)!=FakeSigner)return false;
  if(Convert.ToString(Global("MenuID"),CultureInfo.InvariantCulture)!="D1"||Convert.ToString(Get(Global("ToKhaiInfo"),"VersionXML"),CultureInfo.InvariantCulture)!="2.8.3")return false;
  InspectMoneyZero(sheet);InspectCaseMoney(sheet);gtgtCt42AfterImportObserved=true;gtgtCt42LockedAfterImport=gtgtCt42Locked;roundtripImportCheckedMoneyCount=27-gtgtEmptyMoney;bool ct21Matched=InspectCt21Case(sheet);if(NoActivityCase())gtgtCt21AfterImportMatched=ct21Matched;return gtgtCaseMoneyMatched&&roundtripImportCheckedMoneyCount==27&&ct21Matched;
 }
 private static XmlDocument ReadBoundedOriginalXml(string path){
  FileInfo file=new FileInfo(path);if(!file.Exists||(file.Attributes&FileAttributes.ReparsePoint)!=0||file.Length<1||file.Length>262144)throw new InvalidOperationException();
  XmlReaderSettings settings=new XmlReaderSettings();settings.ProhibitDtd=true;settings.XmlResolver=null;XmlDocument document=new XmlDocument();document.XmlResolver=null;using(XmlReader reader=XmlReader.Create(path,settings))document.Load(reader);
  if(document.DocumentElement==null||document.DocumentElement.LocalName!="HSoThueDTu"||document.DocumentElement.NamespaceURI!="http://kekhaithue.gdt.gov.vn/TKhaiThue")throw new InvalidOperationException();return document;
 }
}
