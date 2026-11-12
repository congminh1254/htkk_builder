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
    if(labels[0].Text!="Nhập dữ liệu từ XML thành công."){importRejectedMessageId=OriginalMessageCatalogueId(labels[0].Text);SetStage(HtkkAutomationStage.GtgtImportOriginalMessageRejected);finished=true;Record();exportWatcher.Stop();return;}
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
   if(Annex12WebCase()&&!annex12WebHeadAuthorityRestored){RestoreImportedAnnex12HeadAuthorities();return;}
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
  InspectMoneyZero(sheet);InspectCaseMoney(sheet);gtgtCt42AfterImportObserved=true;gtgtCt42LockedAfterImport=gtgtCt42Locked;roundtripImportCheckedMoneyCount=27-gtgtEmptyMoney;bool ct21Matched=InspectCt21Case(sheet);if(NoActivityCase())gtgtCt21AfterImportMatched=ct21Matched;
  // Fixed web annex cases also require the imported original annex groups, rows, values and locks.
  bool annexMatched=!Annex12WebCase()||InspectOriginalImportedAnnex12(grids[0]);
  // 01-10: bounded observation of the imported original sheet only (the re-export comparison is the proof).
  if(Annex10WebCase())ObserveOriginalImportedAnnex10(grids[0]);
  return gtgtCaseMoneyMatched&&roundtripImportCheckedMoneyCount==27&&ct21Matched&&annexMatched;
 }
 // 01-10/GTGT (sheet 01_10, PL_NQ142_GTGT) after the original import: observation only, never an edit and never a
 // gate (the whole-tree re-export comparison decides). Bounded flags: the sheet is in the original grid and active in
 // ToKhaiInfo.SheetInfos, the row counts of its two dynamic tables (I purchases, II sales), and how the original shows the
 // negative row's G cell (II.2, G = ROUND(D*(E-F)/100,0) = -400002 with MinValue 0): mask bit 0 cell located, bit 1 Value
 // is -400002, bit 2 Value is 0 (clamped), bit 3 the displayed Text carries a minus sign. Never values or text.
 private bool annex10ImportSheetObserved=false,annex10ImportSheetActive=false;private int annex10ImportPurchaseRows=0,annex10ImportSaleRows=0,annex10NegativeDisplayMask=0;
 private string Annex10Json(){
  string q=((char)34).ToString();
  return ","+q+"annex10ImportSheetObserved"+q+":"+Bool(annex10ImportSheetObserved)+","+q+"annex10ImportSheetActive"+q+":"+Bool(annex10ImportSheetActive)
   +","+q+"annex10ImportPurchaseRows"+q+":"+annex10ImportPurchaseRows.ToString(CultureInfo.InvariantCulture)+","+q+"annex10ImportSaleRows"+q+":"+annex10ImportSaleRows.ToString(CultureInfo.InvariantCulture)
   +","+q+"annex10NegativeDisplayMask"+q+":"+annex10NegativeDisplayMask.ToString(CultureInfo.InvariantCulture);
 }
 private void ObserveOriginalImportedAnnex10(Control grid){
  if(!Annex10WebCase())throw new InvalidOperationException();
  annex10ImportSheetObserved=false;annex10ImportSheetActive=false;annex10ImportPurchaseRows=0;annex10ImportSaleRows=0;annex10NegativeDisplayMask=0;
  try{
   object sheets=Get(grid,"Sheets");int count=Convert.ToInt32(Get(sheets,"Count"));if(count<1||count>32)return;
   PropertyInfo item=sheets.GetType().GetProperty("Item",new Type[]{typeof(int)});if(item==null)return;object annex=null;
   for(int index=0;index<count;index++){object candidate=item.GetValue(sheets,new object[]{index});string name=Convert.ToString(Get(candidate,"SheetName"),CultureInfo.InvariantCulture);if(name=="01_10"||name=="PL 142/2024/QH15-174/2024/QH15-204/2025/QH15"){if(annex!=null)return;annex=candidate;}}
   annex10ImportSheetObserved=annex!=null;
   System.Collections.IList infos=Get(Global("ToKhaiInfo"),"SheetInfos") as System.Collections.IList;if(infos==null||infos.Count>32)return;object info=null;
   foreach(object candidate in infos)if(candidate!=null&&Convert.ToString(Get(candidate,"SheetID"),CultureInfo.InvariantCulture)=="01_10"){if(info!=null)return;info=candidate;}
   if(info==null)return;annex10ImportSheetActive=Selected(Get(info,"Active"));
   System.Collections.IList tables=Get(info,"Tables") as System.Collections.IList;if(tables==null||tables.Count<1||tables.Count>4)return;
   System.Collections.IList purchases=Get(tables[0],"RowsValues") as System.Collections.IList;if(purchases!=null)annex10ImportPurchaseRows=Math.Min(purchases.Count,10);
   if(tables.Count<2)return;System.Collections.IList sales=Get(tables[1],"RowsValues") as System.Collections.IList;if(sales==null)return;annex10ImportSaleRows=Math.Min(sales.Count,10);
   if(annex==null||sales.Count!=2)return;
   int row=Convert.ToInt32(Get(Get(tables[1],"Location"),"DataLocationTemplateRowStart"))-1+1;if(row<1||row>=Convert.ToInt32(Get(annex,"RowCount"))||Convert.ToInt32(Get(annex,"ColumnCount"))<7)return;
   annex10NegativeDisplayMask|=1;object raw=Get(Cell(annex,row,6),"Value");decimal number;
   if(raw!=null&&raw!=DBNull.Value&&Decimal.TryParse(Convert.ToString(raw,CultureInfo.InvariantCulture),NumberStyles.Number,CultureInfo.InvariantCulture,out number)){if(number==-400002m)annex10NegativeDisplayMask|=2;if(number==Decimal.Zero)annex10NegativeDisplayMask|=4;}
   if(CellText(annex,row,6).IndexOf('-')>=0)annex10NegativeDisplayMask|=8;
  }catch(Exception){}
  Record();
 }
 private static XmlDocument ReadBoundedOriginalXml(string path){
  FileInfo file=new FileInfo(path);if(!file.Exists||(file.Attributes&FileAttributes.ReparsePoint)!=0||file.Length<1||file.Length>262144)throw new InvalidOperationException();
  XmlReaderSettings settings=new XmlReaderSettings();settings.ProhibitDtd=true;settings.XmlResolver=null;XmlDocument document=new XmlDocument();document.XmlResolver=null;using(XmlReader reader=XmlReader.Create(path,settings))document.Load(reader);
  if(document.DocumentElement==null||document.DocumentElement.LocalName!="HSoThueDTu"||document.DocumentElement.NamespaceURI!="http://kekhaithue.gdt.gov.vn/TKhaiThue")throw new InvalidOperationException();return document;
 }
}
