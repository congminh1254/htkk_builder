// Own bounded ORIGINAL B1 opening observation. No KHBS data or XML is authored.
using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Reflection;
using System.Text;
using System.Windows.Forms;
public sealed partial class HtkkGuiReferenceAutomation {
 private bool amendmentOpenCloseInvoked=false,amendmentOpenPriorClosed=false,amendmentOpenDefaultsMatched=false,amendmentOpenConfirmInvoked=false,amendmentOpenPeriodMatched=false,amendmentOpenSourcesMatched=false,amendmentOpenKhbsSheetsObserved=false,amendmentOpenPriorUnchanged=false;
 private int amendmentOpenLoadedSheets=0,amendmentOpenKhbsRows=0,amendmentOpenKhbsColumns=0,amendmentOpenExplanationRows=0,amendmentOpenExplanationColumns=0;
 private bool AmendmentInspectionMode(){return mode=="gtgt-amendment-inspect"||mode=="gtgt-amendment-open-inspect";}
 private bool AmendmentReopening(){return mode=="gtgt-amendment-open-inspect"&&amendmentOpenCloseInvoked;}
 private string AmendmentOpenJson(){
  string q=((char)34).ToString();StringBuilder json=new StringBuilder();
  string[] names=new string[]{"amendmentOpenCloseInvoked","amendmentOpenPriorClosed","amendmentOpenDefaultsMatched","amendmentOpenConfirmInvoked","amendmentOpenPeriodMatched","amendmentOpenSourcesMatched","amendmentOpenKhbsSheetsObserved","amendmentOpenPriorUnchanged"};
  bool[] values=new bool[]{amendmentOpenCloseInvoked,amendmentOpenPriorClosed,amendmentOpenDefaultsMatched,amendmentOpenConfirmInvoked,amendmentOpenPeriodMatched,amendmentOpenSourcesMatched,amendmentOpenKhbsSheetsObserved,amendmentOpenPriorUnchanged};
  for(int index=0;index<names.Length;index++)json.Append(","+q+names[index]+q+":"+Bool(values[index]));
  names=new string[]{"amendmentOpenKhbsRows","amendmentOpenKhbsColumns","amendmentOpenExplanationRows","amendmentOpenExplanationColumns"};int[] counts=new int[]{amendmentOpenKhbsRows,amendmentOpenKhbsColumns,amendmentOpenExplanationRows,amendmentOpenExplanationColumns};
  for(int index=0;index<names.Length;index++)json.Append(","+q+names[index]+q+":"+counts[index].ToString(CultureInfo.InvariantCulture));return json.ToString()+","+q+"amendmentOpenLoadedSheets"+q+":"+amendmentOpenLoadedSheets.ToString(CultureInfo.InvariantCulture);
 }
 private void CloseOriginalPriorForAmendment(){
  if(mode!="gtgt-amendment-open-inspect"||amendmentOpenCloseInvoked||!amendmentPriorDirtyCleared||!amendmentPriorSaveSuccessAcknowledged||!amendmentPriorFileFresh||!amendmentPriorSavedMoneyZero||amendmentPriorSavedMoneyCount!=27||amendmentPriorOwner==null||amendmentPriorOwner.IsDisposed||!amendmentPriorOwner.Visible||!amendmentPriorOwner.Enabled||OriginalMessageVisible())throw new InvalidOperationException();
  FieldInfo dirty=amendmentPriorOwner.GetType().GetField("isDataChanged",BindingFlags.Instance|BindingFlags.Public|BindingFlags.NonPublic);if(dirty==null||dirty.FieldType!=typeof(bool)||(bool)dirty.GetValue(amendmentPriorOwner))throw new InvalidOperationException();
  Button close=Named(amendmentPriorOwner,"cmdExit") as Button;if(close==null||close.FindForm()!=amendmentPriorOwner||!close.Visible||!close.Enabled||!close.CanSelect||close.Text.Replace("&",String.Empty).Trim()!="Đóng")throw new InvalidOperationException();
  amendmentPriorWatcher.Stop();amendmentOpenCloseInvoked=true;navigationPhase="waiting-amendment-prior-close";menuStep=0;SetStage(HtkkAutomationStage.GtgtAmendmentPriorCloseInvoking);Record();close.PerformClick();
  ObserveOriginalAmendmentPriorClosed();
 }
 private void ObserveOriginalAmendmentPriorClosed(){
  if(!AmendmentReopening()||amendmentPriorOwner==null||OriginalMessageVisible())throw new InvalidOperationException();
  amendmentOpenPriorClosed=amendmentPriorOwner.IsDisposed||!amendmentPriorOwner.Visible;
  if(!amendmentOpenPriorClosed){SetStage(HtkkAutomationStage.GtgtAmendmentPriorCloseWaiting);Record();return;}
  navigationPhase="waiting-main-menu";SetStage(HtkkAutomationStage.GtgtAmendmentPriorClosed);Record();
 }
 private static bool CurrentOriginalAmendmentDate(string text){DateTime parsed;return DateTime.TryParseExact(text,new string[]{"d/M/yyyy","dd/MM/yyyy"},CultureInfo.InvariantCulture,DateTimeStyles.None,out parsed)&&parsed.Date==DateTime.Now.Date;}
 private void ConfigureOriginalAmendmentOpen(Control period){
  if(!AmendmentReopening()||!amendmentOpenPriorClosed||amendmentOpenConfirmInvoked||!periodDateMatched||!periodGeographyMatched||!periodActivityMatched||!periodNoAnnexMatched||annexSelected!=0||OriginalMessageVisible())throw new InvalidOperationException();
  SetStage(HtkkAutomationStage.GtgtAmendmentDefaultsSelecting);Record();SetCheck(Named(period,"OptBosung"),true);
  Control number=ReadableNamed(period,"txtLan"),date=ReadableNamed(period,"mskNgayLapKHBS");
  amendmentOpenDefaultsMatched=CheckValue(Named(period,"OptBosung"))&&!CheckValue(ReadableNamed(period,"OptChinhthuc"))&&number.Visible&&date.Visible&&number.Text.Trim()=="1"&&CurrentOriginalAmendmentDate(date.Text);
  if(!amendmentOpenDefaultsMatched||OriginalMessageVisible())throw new InvalidOperationException();
  Button confirm=Named(period,"btnDongY") as Button;if(confirm==null||!confirm.Visible||!confirm.Enabled||!confirm.CanSelect||confirm.Text.Replace("&",String.Empty).Trim()!="Đồng ý")throw new InvalidOperationException();
  amendmentOpenConfirmInvoked=true;navigationPhase="waiting-amendment-sheet";SetStage(HtkkAutomationStage.GtgtAmendmentOpenConfirmInvoking);Record();
  using(System.Windows.Forms.Timer watcher=new System.Windows.Forms.Timer()){
   watcher.Interval=100;watcher.Tick+=delegate(object sender,EventArgs args){try{InspectOriginalAmendmentOpen();if(finished)watcher.Stop();}catch(Exception error){watcher.Stop();Failure(error);}};
   watcher.Start();try{confirm.PerformClick();}finally{watcher.Stop();}
  }
 }
 private bool amendmentOpenInspectionBusy=false;
 private void InspectOriginalAmendmentOpen(){
  if(finished||amendmentOpenInspectionBusy||!amendmentOpenConfirmInvoked)return;amendmentOpenInspectionBusy=true;
  try{
   SetStage(HtkkAutomationStage.GtgtAmendmentOpenSheetWaiting);Record();List<Form> forms=new List<Form>();int visited=0;foreach(Form top in Application.OpenForms){if(visited>=512)break;if(top.Visible&&!top.IsDisposed)FindWorksheets(top,forms,ref visited);}if(forms.Count!=1){SetStage(HtkkAutomationStage.GtgtAmendmentOpenOwnerWaiting);Record();return;}
   List<Control> grids=new List<Control>();visited=0;GatherSpreads(forms[0],grids,ref visited);if(grids.Count!=1){SetStage(HtkkAutomationStage.GtgtAmendmentOpenGridWaiting);Record();return;}if(!forms[0].Enabled||OriginalMessageVisible()){SetStage(HtkkAutomationStage.GtgtAmendmentOpenReadyWaiting);Record();return;}
   Control grid=grids[0];if(!grid.Enabled){SetStage(HtkkAutomationStage.GtgtAmendmentOpenReadyWaiting);Record();return;}object sheets=Get(grid,"Sheets");int count=Convert.ToInt32(Get(sheets,"Count"));if(count<1||count>32)throw new InvalidOperationException();amendmentOpenLoadedSheets=count;if(count<3){SetStage(HtkkAutomationStage.GtgtAmendmentOpenWorkbookWaiting);Record();return;}PropertyInfo item=sheets.GetType().GetProperty("Item",new Type[]{typeof(int)});if(item==null)throw new InvalidOperationException();object sheet=null;
   for(int index=0;index<count;index++){object candidate=item.GetValue(sheets,new object[]{index});string name=Convert.ToString(Get(candidate,"SheetName"),CultureInfo.InvariantCulture);if(name=="Tờ khai điều chỉnh"){if(sheet!=null)throw new InvalidOperationException();sheet=candidate;}}
   if(sheet==null||Convert.ToInt32(Get(sheet,"RowCount"))!=72||Convert.ToInt32(Get(sheet,"ColumnCount"))!=24){SetStage(HtkkAutomationStage.GtgtAmendmentOpenMainWaiting);Record();return;}
   object period=Global("TTPeriodInfo");amendmentOpenPeriodMatched=Convert.ToString(Get(period,"LoaiToKhai"),CultureInfo.InvariantCulture)=="B"&&Convert.ToString(Get(period,"SoLan"),CultureInfo.InvariantCulture)=="1"&&CurrentOriginalAmendmentDate(Convert.ToString(Get(period,"NgayLapKHBS"),CultureInfo.InvariantCulture))&&Convert.ToString(Get(period,"KieuKy"),CultureInfo.InvariantCulture)=="M"&&Convert.ToString(Get(period,"Thang"),CultureInfo.InvariantCulture)=="10"&&Convert.ToString(Get(period,"Nam"),CultureInfo.InvariantCulture)=="2026"&&Convert.ToString(Get(period,"TieuMucHachToanVal"),CultureInfo.InvariantCulture)=="00"&&Convert.ToString(Get(period,"maCQTQuanLy"),CultureInfo.InvariantCulture)=="10129";
   if(!amendmentOpenPeriodMatched)throw new InvalidOperationException();
   string root=Path.GetDirectoryName(project);amendmentOpenSourcesMatched=gtgtPins&&Hash(Path.Combine(root,"InterfaceTemplates/xml/KHBS_01_TT80_DIA_BAN_283.xml"))=="cdfab7d9968ea521e27424ca2520df6e5d9e2b18e272883bca0df5a411634c37"&&Hash(Path.Combine(root,"InterfaceTemplates/xml/KHBS_01_DIA_BAN_xml.xml"))=="990e69d80b573d8e9ed950a4dbb7c06fde39093d6178e6a1c4c6c9c42e3b2d90"&&Hash(Path.Combine(root,"InterfaceTemplates/xml/KHBS_01_1_TT80_283.xml"))=="a639d481c21749270ed30604cbe79aea3eb0f08e3a0896c463308c3cad2c3b71"&&Hash(Path.Combine(root,"InterfaceTemplates/xml/KHBS_01_1_TT80_xml.xml"))=="d3ad5ce44fdb242142efd35bad0cd981425b3b6f2f8179f92ce4df402b46ba38"&&Hash(Path.Combine(root,"InterfaceTemplates/Validate/KHBS_01_GTGT_TT80_283.xsd"))=="b0fcb96663749e897839db2c9c224c45b4f2ed779be508e1bf9f9a2f82daf76f";
   if(!amendmentOpenSourcesMatched)throw new InvalidOperationException();SetStage(HtkkAutomationStage.GtgtAmendmentOpenKhbsObserving);Record();
   IList infos=Get(Global("ToKhaiInfo"),"SheetInfos") as IList;if(infos==null||infos.Count>32)throw new InvalidOperationException();int observed=0;
   MethodInfo rectangle=grid.GetType().GetMethod("GetSheetTabRectangle",new Type[]{typeof(int)});if(rectangle==null)throw new InvalidOperationException();
   foreach(string id in new string[]{"01-KHBS","01-1-KHBS"}){
    object info=null;foreach(object candidate in infos){if(candidate!=null&&Convert.ToString(Get(candidate,"SheetID"),CultureInfo.InvariantCulture)==id){if(info!=null)throw new InvalidOperationException();info=candidate;}}if(info==null||!Selected(Get(info,"Active")))throw new InvalidOperationException();
    int matched=0;for(int index=0;index<count;index++){object candidate=item.GetValue(sheets,new object[]{index});if(Convert.ToString(Get(candidate,"SheetName"),CultureInfo.InvariantCulture)!=(id=="01-1-KHBS"?"01-1/KHBS":"01-KHBS"))continue;matched++;object bounds=rectangle.Invoke(grid,new object[]{index});int width=Convert.ToInt32(Get(bounds,"Width")),height=Convert.ToInt32(Get(bounds,"Height"));int rows=Convert.ToInt32(Get(candidate,"RowCount")),columns=Convert.ToInt32(Get(candidate,"ColumnCount"));if(width<=0||height<=0||rows<1||rows>10000||columns<1||columns>512)throw new InvalidOperationException();if(id=="01-KHBS"){amendmentOpenKhbsRows=rows;amendmentOpenKhbsColumns=columns;}else{amendmentOpenExplanationRows=rows;amendmentOpenExplanationColumns=columns;}}if(matched!=1)throw new InvalidOperationException();observed++;
   }
   amendmentOpenKhbsSheetsObserved=observed==2;InspectMoneyZero(sheet);if(!gtgtZero||gtgtEmptyMoney!=0||CellText(sheet,9,3)!=FakeName||CellText(sheet,10,3).Replace("-",String.Empty)!=Mst)throw new InvalidOperationException();
   InspectOriginalPriorFile();ReadSavedHeader();amendmentOpenPriorUnchanged=amendmentPriorFileFresh&&amendmentPriorSavedMoneyZero&&amendmentPriorSavedMoneyCount==27&&headerMatched&&headerChecks==8&&headerMismatchMask==0;
   if(!amendmentOpenPriorUnchanged)throw new InvalidOperationException();finished=true;SetStage(HtkkAutomationStage.GtgtAmendmentOpenInspected);Record();
  }finally{amendmentOpenInspectionBusy=false;}
 }
}
