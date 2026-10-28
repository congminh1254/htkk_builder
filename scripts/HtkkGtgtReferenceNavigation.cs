// Own staged reference navigation AFTER the original synthetic profile Save succeeded.
// Uses original close and original FarPoint CellClick event flow; no original output XML is authored.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Reflection;
using System.Text;
using System.Windows.Forms;

public sealed partial class HtkkGuiReferenceAutomation {
 private bool profileClosed=false,mainMenuObserved=false,d1MenuClicked=false,periodObserved=false;
 private int menuRowCount=0,menuClicks=0,menuStep=0,periodControlCount=0;
 private string navigationPhase="not-started";
 private Form closingProfileForm=null;
 private bool profileCloseRequested=false;
 private Button pendingProfileClose=null;
 private readonly Dictionary<string,string> periodDescriptions=new Dictionary<string,string>();
 private static readonly string[] PeriodNames=new string[]{"chkTkhaiThang","chkTKQuy","OptTKThang","OptChinhthuc","OptBosung","mskYear","mskMonth","cbbQuy","btnDongY","cmdClose","axfpsPhuLuc","cboNganhKD","chkChonPhuLucKeKhaiAll","cboCQTCuc","cboCQTChiCuc","cboTinh","cboXa"};
 internal string NavigationJson(){
  string q=((char)34).ToString();StringBuilder descriptions=new StringBuilder();
  foreach(string name in PeriodNames){if(!periodDescriptions.ContainsKey(name))continue;if(descriptions.Length>0)descriptions.Append(',');descriptions.Append(q+name+q+":"+periodDescriptions[name]);}
  return ","+q+"profileClosed"+q+":"+Bool(profileClosed)+","+q+"mainMenuObserved"+q+":"+Bool(mainMenuObserved)+","+q+"d1MenuClicked"+q+":"+Bool(d1MenuClicked)+","+q+"gtgtPeriodObserved"+q+":"+Bool(periodObserved)+","+q+"menuRowCount"+q+":"+menuRowCount.ToString(CultureInfo.InvariantCulture)+","+q+"menuClickCount"+q+":"+menuClicks.ToString(CultureInfo.InvariantCulture)+","+q+"periodControlCount"+q+":"+periodControlCount.ToString(CultureInfo.InvariantCulture)+","+q+"periodControls"+q+":{ "+descriptions.ToString()+"}"+SheetJson()+ExportJson();
 }
 private static void GatherSpreads(Control root,List<Control> found,ref int visited){
  if(++visited>512)return;if(root.Visible&&IsSpread(root))found.Add(root);
  foreach(Control child in root.Controls){if(visited>=512)break;GatherSpreads(child,found,ref visited);}
 }
 private static int FindMenuRow(object sheet,int idColumn,string id,int count){
  int found=-1;for(int row=0;row<count;row++){if(CellText(sheet,row,idColumn)==id){if(found>=0)return -1;found=row;}}return found;
 }
 private static bool RowVisible(object sheet,int row){object collection=Get(sheet,"Rows");PropertyInfo item=collection.GetType().GetProperty("Item",new Type[]{typeof(int)});if(item==null)throw new InvalidOperationException();return Convert.ToBoolean(Get(item.GetValue(collection,new object[]{row}),"Visible"));}
 private static void RaiseOriginalMenuClick(Control spread,int row,int column){
  // Public event args + vendor's protected OnCellClick retain the application's
  // original subscribed winSpMenu_CellClick handler, NNT checks and period routing.
  Type spreadType=spread.GetType();while(spreadType!=null&&spreadType.FullName!="FarPoint.Win.Spread.FpSpread")spreadType=spreadType.BaseType;if(spreadType==null)throw new InvalidOperationException();
  Assembly vendor=spreadType.Assembly;Type eventType=vendor.GetType("FarPoint.Win.Spread.CellClickEventArgs",true),viewType=vendor.GetType("FarPoint.Win.Spread.SpreadView",true);
  MethodInfo workbook=spread.GetType().GetMethod("GetRootWorkbook",Type.EmptyTypes);
  ConstructorInfo ctor=eventType.GetConstructor(new Type[]{viewType,typeof(int),typeof(int),typeof(int),typeof(int),typeof(MouseButtons),typeof(bool),typeof(bool)});
  MethodInfo raise=spreadType.GetMethod("OnCellClick",BindingFlags.Public|BindingFlags.NonPublic|BindingFlags.Instance,null,new Type[]{eventType},null);
  if(workbook==null||ctor==null||raise==null)throw new InvalidOperationException();
  object args=ctor.Invoke(new object[]{workbook.Invoke(spread,null),row,column,0,0,MouseButtons.Left,false,false});raise.Invoke(spread,new object[]{args});
 }
 private static void FindPeriods(Control root,List<Control> found,ref int visited){
  if(++visited>512)return;if(root.Visible&&root.GetType().FullName=="HTKK.frmHTKKPeriod")found.Add(root);
  foreach(Control child in root.Controls){if(visited>=512)break;FindPeriods(child,found,ref visited);}
 }
 private void DescribePeriod(Control root,ref int visited){
  if(++visited>512)return;periodControlCount++;
  foreach(string allowed in PeriodNames){
   if(root.Name!=allowed)continue;
   if(periodDescriptions.ContainsKey(allowed))throw new InvalidOperationException();
   string kind=IsSpread(root)?"spread":root is RadioButton?"radio":root is CheckBox?"check":root is MaskedTextBox?"masked-text":root is TextBoxBase?"text":root is ComboBox?"combo":root is Button?"button":"other";
   bool available=root is RadioButton||root is CheckBox;bool check=root is RadioButton?((RadioButton)root).Checked:root is CheckBox?((CheckBox)root).Checked:false;string q=((char)34).ToString();
   periodDescriptions[allowed]="{"+q+"kind"+q+":"+q+kind+q+","+q+"visible"+q+":"+Bool(root.Visible)+","+q+"enabled"+q+":"+Bool(root.Enabled)+","+q+"checkedAvailable"+q+":"+Bool(available)+","+q+"checked"+q+":"+Bool(check)+"}";
  }
  foreach(Control child in root.Controls){if(visited>=512)break;DescribePeriod(child,ref visited);}
 }
 private static void FindMainMenus(Control root,List<Form> found,List<Control> seen){
  if(seen.Count>=512||seen.Contains(root))return;seen.Add(root);
  Form form=root as Form;if(form!=null&&form.Visible&&!form.IsDisposed&&form.GetType().FullName=="HTKK.frmHTKKSystems")found.Add(form);
  foreach(Control child in root.Controls){if(seen.Count>=512)break;FindMainMenus(child,found,seen);}
 }
 internal void ContinueGtgtNavigation(){
  if(!headerMatched||headerChecks!=8||headerMismatchMask!=0||!successAcknowledged||closingProfileForm==null){stage="gtgt-profile-preconditions-not-matched";finished=true;Record();return;}
  if(navigationPhase=="waiting-profile-close-ready"){
   foreach(Form modal in Application.OpenForms){if(modal.Visible&&modal.GetType().FullName=="TAX.HTKK.Utilities.Control.frmMessage"){stage="waiting-profile-close-ready";Record();return;}}
   if(closingProfileForm.IsDisposed||!closingProfileForm.Visible||pendingProfileClose==null||pendingProfileClose.IsDisposed||pendingProfileClose.Name!="cmdExit"||pendingProfileClose.FindForm()!=closingProfileForm||pendingProfileClose.Text.Replace("&",String.Empty).Trim()!="Đóng"){stage="gtgt-profile-preconditions-not-matched";finished=true;Record();return;}
   if(!closingProfileForm.Enabled||!pendingProfileClose.Visible||!pendingProfileClose.Enabled){stage="waiting-profile-close-ready";Record();return;}
   // ORIGINAL cmdExit_Click (060003A5) and FormClosing consult this field.
   // Observe its clean state only; never clear it or acknowledge dirty warnings.
   FieldInfo dirty=closingProfileForm.GetType().GetField("isDataChanged",BindingFlags.Instance|BindingFlags.Public|BindingFlags.NonPublic);
   if(dirty==null||dirty.FieldType!=typeof(bool)||(bool)dirty.GetValue(closingProfileForm)){stage="gtgt-profile-preconditions-not-matched";finished=true;Record();return;}
   ReadSavedHeader();if(!headerMatched||headerChecks!=8||headerMismatchMask!=0||profileCloseRequested){stage="gtgt-profile-preconditions-not-matched";finished=true;Record();return;}
   profileCloseRequested=true;navigationPhase="waiting-main-menu";stage="profile-close-invoking";Record();pendingProfileClose.PerformClick();
   profileClosed=closingProfileForm.IsDisposed||!closingProfileForm.Visible;stage=profileClosed?"waiting-main-menu":"waiting-profile-close";Record();return;
  }
  if(!profileCloseRequested){stage="gtgt-profile-preconditions-not-matched";finished=true;Record();return;}
  // The worksheet can be a non-top-level Form inside the still-visible main frame.
  // Observe THAT original owner across UI turns rather than testing the outer frame.
  profileClosed=closingProfileForm.IsDisposed||!closingProfileForm.Visible;
  if(!profileClosed){stage="waiting-profile-close";Record();return;}
  if(navigationPhase=="waiting-amendment-prior-close"){ObserveOriginalAmendmentPriorClosed();return;}
  if(navigationPhase=="waiting-amendment-sheet"){InspectOriginalAmendmentOpen();return;}
  if(navigationPhase=="waiting-gtgt-sheet"){InspectOriginalGtgtSheet();return;}
  List<Form> menus=new List<Form>();List<Control> seen=new List<Control>();foreach(Form candidate in Application.OpenForms){if(candidate.Visible&&!candidate.IsDisposed)FindMainMenus(candidate,menus,seen);}
  if(menus.Count>1)throw new InvalidOperationException();Form main=menus.Count==1?menus[0]:null;
  if(main==null){stage="waiting-main-menu";Record();return;}mainMenuObserved=true;
  if(navigationPhase=="waiting-gtgt-period"){
   List<Control> periods=new List<Control>();int visited=0;FindPeriods(main,periods,ref visited);
   if(periods.Count!=1){stage="waiting-gtgt-period";Record();return;}
   periodDescriptions.Clear();periodControlCount=0;visited=0;DescribePeriod(periods[0],ref visited);
   periodObserved=true;
   if((mode=="gtgt-sheet-inspect"||AmendmentInspectionMode())||Annex12InspectionMode()||mode=="gtgt-export-inspect"||mode=="gtgt-roundtrip-inspect"||mode=="gtgt-web-import-inspect"){ConfigureOriginalGtgtPeriod(periods[0]);return;}
   stage="gtgt-period-inspected";finished=true;Record();return;
  }
  List<Control> grids=new List<Control>();int nodes=0;GatherSpreads(main,grids,ref nodes);
  if(grids.Count!=1){stage="gtgt-menu-spread-not-yet-unique";Record();return;}
  Control grid=grids[0];object sheet=Get(grid,"ActiveSheet");menuRowCount=Convert.ToInt32(Get(sheet,"RowCount"));int cols=Convert.ToInt32(Get(sheet,"ColumnCount"));
  FieldInfo idField=main.GetType().GetField("colE",BindingFlags.Static|BindingFlags.Public|BindingFlags.NonPublic),captionField=main.GetType().GetField("colC",BindingFlags.Static|BindingFlags.Public|BindingFlags.NonPublic);
  if(menuRowCount<1||menuRowCount>2048||cols<1||cols>64||idField==null||captionField==null)throw new InvalidOperationException();
  int idColumn=Convert.ToInt32(idField.GetValue(null))-1,captionColumn=Convert.ToInt32(captionField.GetValue(null))-1;
  if(idColumn<0||idColumn>=cols||captionColumn<0||captionColumn>=cols)throw new InvalidOperationException();
  string[] chain=new string[]{"101","101_1","D1"};
  while(menuStep<chain.Length){
   int row=FindMenuRow(sheet,idColumn,chain[menuStep],menuRowCount);
   if(row<0){stage="gtgt-menu-id-not-unique";finished=true;Record();return;}
   if(menuStep<chain.Length-1){int next=FindMenuRow(sheet,idColumn,chain[menuStep+1],menuRowCount);if(next<0){stage="gtgt-menu-id-not-unique";finished=true;Record();return;}if(RowVisible(sheet,next)){menuStep++;continue;}}
   if(!RowVisible(sheet,row)){SetStage(HtkkAutomationStage.GtgtMenuTargetHidden);finished=true;Record();return;}
   SetStage(HtkkNativeAutomationWireMap.GetMenuClickStage(chain[menuStep]));Record();RaiseOriginalMenuClick(grid,row,captionColumn);menuClicks++;
   if(chain[menuStep]=="D1"){d1MenuClicked=true;navigationPhase="waiting-gtgt-period";SetStage(HtkkAutomationStage.WaitingGtgtPeriod);}
   menuStep++;Record();return;
  }
 }
 internal void OnGtgtProfileSaved(Form profileOwner, Button closeButton, Control spread) {
  if(profileOwner==null||profileOwner.GetType().FullName!="HTKK.frmWinToKhai")throw new InvalidOperationException();
  closingProfileForm=profileOwner;
  pendingProfileClose=closeButton;
  SetStage(HtkkAutomationStage.WaitingProfileCloseReady);
  navigationPhase="waiting-profile-close-ready";
  Record();
 }
}

public sealed class HtkkGtgtAdapter : IHtkkNativeAutomationAdapter {
 private HtkkGuiReferenceAutomation harness;
 public string AdapterId { get { return "d1-gtgt"; } }
 public bool CanHandle(HtkkAutomationMode mode) {
  return mode == HtkkAutomationMode.GtgtInspect
   || mode == HtkkAutomationMode.GtgtSheetInspect
   || mode == HtkkAutomationMode.GtgtAmendmentInspect
   || mode == HtkkAutomationMode.GtgtAmendmentOpenInspect
   || mode == HtkkAutomationMode.GtgtAnnex12Inspect
   || mode == HtkkAutomationMode.GtgtAnnex12RowInspect
   || mode == HtkkAutomationMode.GtgtAnnex12InputInspect
   || mode == HtkkAutomationMode.GtgtAnnex12NumericInspect
   || mode == HtkkAutomationMode.GtgtAnnex12ExportInspect
   || mode == HtkkAutomationMode.GtgtExportInspect
   || mode == HtkkAutomationMode.GtgtRoundtripInspect
   || mode == HtkkAutomationMode.GtgtWebImportInspect;
 }
 public void Initialize(HtkkGuiReferenceAutomation harnessInstance, string projectDir, HtkkAutomationMode mode) {
  if(harnessInstance==null||!CanHandle(mode))throw new ArgumentException();
  harness = harnessInstance;
 }
 public void OnProfileSaved(Form profileOwner, Button closeButton, Control spread) {
  harness.OnGtgtProfileSaved(profileOwner, closeButton, spread);
 }
 public void ContinueNavigation() {
  harness.ContinueGtgtNavigation();
 }
 public string BuildNavigationJson() {
  return harness.NavigationJson();
 }
}
