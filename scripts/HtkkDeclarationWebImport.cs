// Generic declaration-family driver (mode declaration-web-import-inspect), C# 2.0 / CLR2.
// Cases whose compiled plan has an entry plan (native-case mode original-entry-export) replace the
// original import by typing into the original grid (HtkkDeclarationOriginalEntry.cs); the rest is shared.
// After the shared original profile save: original menu chain from Menu.xml (compiled plan),
// original period dialog (KieuKy month/quarter/year), original annex checkboxes, ORIGINAL
// "Nhập từ XML" of the synthetic web XML, original grid observation, ORIGINAL "Kết xuất",
// pinned .NET XSD, then whole-tree comparison with the web input. Only original buttons,
// editors and dialogs act; no business method, Cell.Value assignment or authored XML.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Net;
using System.Reflection;
using System.Text;
using System.Text.RegularExpressions;
using System.Windows.Forms;
using System.Xml;
using System.Xml.Schema;

public sealed partial class HtkkGuiReferenceAutomation {
 private HtkkDeclarationCasePlan declarationPlan=null;
 private string declarationPhase="not-started";
 private bool declarationSheetBusy=false,declarationFlowStarted=false;
 private Stopwatch declarationClock=null;
 private bool declarationMenuClicked=false,declarationPeriodObserved=false,declarationPeriodMatched=false,declarationAnnexMatched=false,declarationSheetObserved=false,declarationIdentityMatched=false,declarationSourcePinsMatched=false,declarationImportSheetMatched=false,declarationSchemaValid=false,declarationServiceIdentityMatched=false,declarationCreationDateValid=false,declarationTreeMatched=false;
 private int declarationPeriodRejectedMessageId=0,declarationAnnexSelectedCount=0,declarationSheetCount=0,declarationCellCheckCount=0,declarationCellMismatchMask=0,declarationCellLockedMask=0,declarationXmlCheckCount=0,declarationXmlMismatchMask=0,declarationTreeMismatchMask=0,declarationTreeLeafCount=0;
 private int declarationInvalidSheetMask=0,declarationInvalidCellCount=0,declarationInvalidCell1=0,declarationInvalidCell2=0,declarationInvalidCell3=0,declarationInvalidCell4=0;
 private bool DeclarationMode(){return modeEnum==HtkkAutomationMode.DeclarationWebImportInspect;}
 private string DeclarationJson(){
  string q=((char)34).ToString();StringBuilder json=new StringBuilder();
  string[] names=new string[]{"declarationMenuClicked","declarationPeriodObserved","declarationPeriodMatched","declarationAnnexMatched","declarationSheetObserved","declarationIdentityMatched","declarationSourcePinsMatched","declarationImportSheetMatched","declarationSchemaValid","declarationServiceIdentityMatched","declarationCreationDateValid","declarationTreeMatched"};
  bool[] values=new bool[]{declarationMenuClicked,declarationPeriodObserved,declarationPeriodMatched,declarationAnnexMatched,declarationSheetObserved,declarationIdentityMatched,declarationSourcePinsMatched,declarationImportSheetMatched,declarationSchemaValid,declarationServiceIdentityMatched,declarationCreationDateValid,declarationTreeMatched};
  for(int index=0;index<names.Length;index++)json.Append(","+q+names[index]+q+":"+Bool(values[index]));
  names=new string[]{"declarationPeriodRejectedMessageId","declarationAnnexSelectedCount","declarationSheetCount","declarationCellCheckCount","declarationCellMismatchMask","declarationCellLockedMask","declarationXmlCheckCount","declarationXmlMismatchMask","declarationTreeMismatchMask","declarationTreeLeafCount","declarationInvalidSheetMask","declarationInvalidCellCount","declarationInvalidCell1","declarationInvalidCell2","declarationInvalidCell3","declarationInvalidCell4"};
  int[] counts=new int[]{declarationPeriodRejectedMessageId,declarationAnnexSelectedCount,declarationSheetCount,declarationCellCheckCount,declarationCellMismatchMask,declarationCellLockedMask,declarationXmlCheckCount,declarationXmlMismatchMask,declarationTreeMismatchMask,declarationTreeLeafCount,declarationInvalidSheetMask,declarationInvalidCellCount,declarationInvalidCell1,declarationInvalidCell2,declarationInvalidCell3,declarationInvalidCell4};
  for(int index=0;index<names.Length;index++)json.Append(","+q+names[index]+q+":"+counts[index].ToString(CultureInfo.InvariantCulture));
  return json.ToString()+DeclarationEntryJson();
 }
 private void DeclarationTerminal(HtkkAutomationStage stage){SetStage(stage);finished=true;Record();if(exportWatcher!=null)exportWatcher.Stop();}

 // ---- Web input: own private staged sidecars only (never edits the XML) ----
 private void VerifyDeclarationWebInput(){
  string host=Assembly.GetExecutingAssembly().Location;if(!String.Equals(Path.GetDirectoryName(host),project,StringComparison.OrdinalIgnoreCase))throw new InvalidOperationException();
  FileInfo caseFile=new FileInfo(host+".web-case.id");if(!caseFile.Exists||(caseFile.Attributes&FileAttributes.ReparsePoint)!=0||caseFile.Length<1||caseFile.Length>64)throw new InvalidOperationException();
  string id=File.ReadAllText(caseFile.FullName,Encoding.ASCII);HtkkDeclarationCasePlan plan=HtkkDeclarationCasePlans.Find(id);
  if(plan==null||(declarationPlan!=null&&declarationPlan.CaseId!=id))throw new InvalidOperationException();
  declarationPlan=plan;webCaseId=id;
  webInputPath=host+".web-input.xml";webImportInputSha256=ReadOwnHexSidecar(host+".web-input.sha256",64);webSourceSha=ReadOwnHexSidecar(host+".web-source.sha",40);
  XmlDocument document=ReadBoundedOriginalXml(webInputPath);if(Hash(webInputPath)!=webImportInputSha256)throw new InvalidOperationException();
  if(FixedWebLeaf(document,"TTinChung/TTinTKhaiThue/NNT/mst")!=Mst||FixedWebLeaf(document,"TTinChung/TTinTKhaiThue/NNT/tenNNT")!=FakeName||FixedWebLeaf(document,"TTinChung/TTinTKhaiThue/TKhaiThue/nguoiKy")!=FakeSigner)throw new InvalidOperationException();
  if(FixedWebLeaf(document,"TTinChung/TTinDVu/maDVu")!="CCKK"||FixedWebLeaf(document,"TTinChung/TTinDVu/tenDVu")!=plan.WebServiceName||FixedWebLeaf(document,"TTinChung/TTinDVu/ttinNhaCCapDVu")!="hotrokekhai.net — Công cụ Kê khai, công cụ độc lập"||!Regex.IsMatch(FixedWebLeaf(document,"TTinChung/TTinDVu/pbanDVu"),"^[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}$"))throw new InvalidOperationException();
  if(FixedWebLeaf(document,"TTinChung/TTinTKhaiThue/TKhaiThue/maTKhai")!=plan.MaTKhai||FixedWebLeaf(document,"TTinChung/TTinTKhaiThue/TKhaiThue/pbanTKhaiXML")!=plan.VersionXml)throw new InvalidOperationException();
  webInputVerified=true;Record();
 }

 // ---- Profile close → original main menu chain ----
 internal void OnDeclarationProfileSaved(Form profileOwner,Button closeButton,Control spread){
  if(profileOwner==null||profileOwner.GetType().FullName!="HTKK.frmWinToKhai")throw new InvalidOperationException();
  profileLifecycle.Bind(profileOwner,closeButton,spread);navigationPhase="waiting-profile-close-ready";SetStage(HtkkAutomationStage.WaitingProfileCloseReady);Record();
 }
 internal void ContinueDeclarationNavigation(){
  if(finished||declarationFlowStarted)return;
  if(!headerMatched||headerChecks!=8||headerMismatchMask!=0||!successAcknowledged||!profileLifecycle.IsBound){DeclarationTerminal(HtkkAutomationStage.DeclarationProfilePreconditionsNotMatched);return;}
  if(declarationPlan==null){SetStage(HtkkAutomationStage.DeclarationWebInputChecking);Record();VerifyDeclarationWebInput();}
  if(navigationPhase=="waiting-profile-close-ready"){
   if(OriginalMessageVisible()||!profileLifecycle.Ready){if(!profileLifecycle.IdentityMatched){DeclarationTerminal(HtkkAutomationStage.DeclarationProfilePreconditionsNotMatched);return;}SetStage(HtkkAutomationStage.WaitingProfileCloseReady);Record();return;}
   ReadSavedHeader();if(!profileLifecycle.Clean||!headerMatched||headerChecks!=8||headerMismatchMask!=0||profileLifecycle.CloseRequested){DeclarationTerminal(HtkkAutomationStage.DeclarationProfilePreconditionsNotMatched);return;}
   navigationPhase="decl-main-menu";SetStage(HtkkAutomationStage.ProfileCloseInvoking);Record();profileLifecycle.RequestClose();
   profileClosed=profileLifecycle.Closed;SetStage(profileClosed?HtkkAutomationStage.DeclarationMenuWaiting:HtkkAutomationStage.WaitingProfileClose);Record();return;
  }
  if(!profileLifecycle.CloseRequested){DeclarationTerminal(HtkkAutomationStage.DeclarationProfilePreconditionsNotMatched);return;}
  profileClosed=profileLifecycle.Closed;if(!profileClosed){SetStage(HtkkAutomationStage.WaitingProfileClose);Record();return;}
  if(navigationPhase=="decl-sheet"){InspectDeclarationSheet();return;}
  List<Form> menus=new List<Form>();List<Control> seen=new List<Control>();foreach(Form candidate in Application.OpenForms){if(candidate.Visible&&!candidate.IsDisposed)FindMainMenus(candidate,menus,seen);}
  if(menus.Count>1)throw new InvalidOperationException();Form main=menus.Count==1?menus[0]:null;
  if(main==null){SetStage(HtkkAutomationStage.DeclarationMenuWaiting);Record();return;}mainMenuObserved=true;
  if(navigationPhase=="decl-period"){
   List<Control> periods=new List<Control>();int visited=0;FindPeriods(main,periods,ref visited);
   if(periods.Count!=1){SetStage(HtkkAutomationStage.DeclarationPeriodWaiting);Record();return;}
   periodDescriptions.Clear();periodControlCount=0;visited=0;DescribePeriod(periods[0],ref visited);declarationPeriodObserved=true;
   ConfigureDeclarationPeriod(periods[0]);return;
  }
  List<Control> grids=new List<Control>();int nodes=0;GatherSpreads(main,grids,ref nodes);
  if(grids.Count!=1){SetStage(HtkkAutomationStage.DeclarationMenuWaiting);Record();return;}
  Control grid=grids[0];object sheet=Get(grid,"ActiveSheet");menuRowCount=Convert.ToInt32(Get(sheet,"RowCount"));int cols=Convert.ToInt32(Get(sheet,"ColumnCount"));
  FieldInfo idField=main.GetType().GetField("colE",BindingFlags.Static|BindingFlags.Public|BindingFlags.NonPublic),captionField=main.GetType().GetField("colC",BindingFlags.Static|BindingFlags.Public|BindingFlags.NonPublic);
  if(menuRowCount<1||menuRowCount>2048||cols<1||cols>64||idField==null||captionField==null)throw new InvalidOperationException();
  int idColumn=Convert.ToInt32(idField.GetValue(null))-1,captionColumn=Convert.ToInt32(captionField.GetValue(null))-1;
  if(idColumn<0||idColumn>=cols||captionColumn<0||captionColumn>=cols)throw new InvalidOperationException();
  // Chain from Menu.xml (data/htkk-active-menu.json): group → category → declaration.
  string[] chain=declarationPlan.MenuChain;
  while(menuStep<chain.Length){
   int row=FindMenuRow(sheet,idColumn,chain[menuStep],menuRowCount);
   if(row<0){DeclarationTerminal(HtkkAutomationStage.DeclarationMenuIdNotUnique);return;}
   if(menuStep<chain.Length-1){int next=FindMenuRow(sheet,idColumn,chain[menuStep+1],menuRowCount);if(next<0){DeclarationTerminal(HtkkAutomationStage.DeclarationMenuIdNotUnique);return;}if(RowVisible(sheet,next)){menuStep++;continue;}}
   if(!RowVisible(sheet,row)){DeclarationTerminal(HtkkAutomationStage.DeclarationMenuTargetHidden);return;}
   SetStage(HtkkAutomationStage.DeclarationMenuClick);Record();RaiseOriginalMenuClick(grid,row,captionColumn);menuClicks++;
   if(menuStep==chain.Length-1){declarationMenuClicked=true;navigationPhase="decl-period";SetStage(HtkkAutomationStage.DeclarationPeriodWaiting);}
   menuStep++;Record();return;
  }
 }

 // ---- Original period dialog by KieuKy (compiled plan) ----
 private static bool VisibleNamed(Control root,string name){Control[] found=root.Controls.Find(name,true);return found.Length==1&&found[0].Visible;}
 private static bool MaskedTextMatches(Control root,string name,string expected){Control[] found=root.Controls.Find(name,true);if(found.Length!=1||!found[0].Visible)return true;return found[0].Text==expected;}
 private void SetDeclarationText(Control period,string name,string value){
  Control[] found=period.Controls.Find(name,true);if(found.Length!=1||!found[0].Visible)return;
  TextBoxBase input=found[0] as TextBoxBase;if(input==null)throw new InvalidOperationException();
  if(input.Text==value)return;if(!input.Enabled||input.ReadOnly)return;
  // Original Leave handlers (mskYear_Leave, mskTuNgay_Leave ...) run when focus moves on.
  input.Focus();input.Text=value;Control confirm=Named(period,"btnDongY");confirm.Focus();
 }
 private void SelectDeclarationAnnexes(Control period){
  HtkkDeclarationCasePlan plan=declarationPlan;bool[] found=new bool[plan.Annexes.Length];
  Control[] annexes=period.Controls.Find("axfpsPhuLuc",true);
  if(annexes.Length!=1||!IsSpread(annexes[0])){declarationAnnexMatched=plan.Annexes.Length==0;return;}
  Control grid=annexes[0];bool hidden=HtkkDeclarationCasePlans.AnnexPanelHidden(plan);
  if(hidden){
   // Observation only: no click on a list the original layout hides. Matched only if the
   // original defaults already include every reviewed annex of the case.
   if(grid.Visible){declarationAnnexMatched=false;return;}
   object hiddenSheet=Get(grid,"ActiveSheet");int hiddenRows=Convert.ToInt32(Get(hiddenSheet,"RowCount"));if(hiddenRows<0||hiddenRows>512)throw new InvalidOperationException();
   bool[] present=new bool[plan.Annexes.Length];declarationAnnexSelectedCount=0;
   for(int row=0;row<hiddenRows;row++){
    object selector=Get(Cell(hiddenSheet,row,0),"CellType");if(selector==null||selector.GetType().FullName!="FarPoint.Win.Spread.CellType.CheckBoxCellType")continue;
    if(!Selected(Get(Cell(hiddenSheet,row,0),"Value")))continue;declarationAnnexSelectedCount++;
    string label=Convert.ToString(Get(selector,"TextTrue"),CultureInfo.InvariantCulture);
    for(int index=0;index<plan.Annexes.Length;index++)foreach(string option in plan.Annexes[index].Split('|'))if(option==label)present[index]=true;
   }
   bool all=true;foreach(bool item in present)if(!item)all=false;
   // frmWinToKhai.cmdImportXML_Click calls AddFullPLImportXML for menus ~B8~37~33~B9~N7~W1: the
   // original import itself adds every Menu.xml sheet before reading the XML, so for these menus the
   // hidden list's defaults do not decide the annexes (run 42231692177: B9 stopped here). The imported
   // sheets are still checked after the import (declarationImportSheetMatched).
   if(HtkkDeclarationCasePlans.ImportAddsAllAnnexes(plan))all=true;
   declarationAnnexMatched=all;Record();return;
  }
  if(!grid.Visible){declarationAnnexMatched=plan.Annexes.Length==0;return;}
  object sheet=Get(grid,"ActiveSheet");int rowCount=Convert.ToInt32(Get(sheet,"RowCount"));if(rowCount<0||rowCount>512)throw new InvalidOperationException();
  SetStage(HtkkAutomationStage.DeclarationPeriodAnnexSelecting);Record();
  for(int row=0;row<rowCount;row++){
   object selector=Get(Cell(sheet,row,0),"CellType");if(selector==null||selector.GetType().FullName!="FarPoint.Win.Spread.CellType.CheckBoxCellType")continue;
   string label=Convert.ToString(Get(selector,"TextTrue"),CultureInfo.InvariantCulture);int wanted=-1;
   for(int index=0;index<plan.Annexes.Length;index++){foreach(string option in plan.Annexes[index].Split('|')){if(option==label){if(wanted>=0||found[index])throw new InvalidOperationException();wanted=index;}}}
   bool desired=wanted>=0;if(desired)found[wanted]=true;
   bool current=Selected(Get(Cell(sheet,row,0),"Value"));if(current==desired)continue;
   // A locked original default that disagrees with the reviewed case is a mismatch, never overridden.
   if(Convert.ToBoolean(Get(Cell(sheet,row,0),"Locked"))||!RowVisible(sheet,row)||!grid.Enabled||OriginalMessageVisible())continue;
   grid.Focus();sheet.GetType().GetMethod("SetActiveCell",new Type[]{typeof(int),typeof(int)}).Invoke(sheet,new object[]{row,0});
   uint pid;GetWindowThreadProcessId(GetForegroundWindow(),out pid);if(pid!=(uint)Process.GetCurrentProcess().Id||!grid.ContainsFocus)throw new InvalidOperationException();
   SendKeys.SendWait(" ");if(OriginalMessageVisible())throw new InvalidOperationException();
  }
  declarationAnnexSelectedCount=0;bool exact=true;
  for(int row=0;row<rowCount;row++){
   object selector=Get(Cell(sheet,row,0),"CellType");if(selector==null||selector.GetType().FullName!="FarPoint.Win.Spread.CellType.CheckBoxCellType")continue;
   bool current=Selected(Get(Cell(sheet,row,0),"Value"));if(current)declarationAnnexSelectedCount++;
   string label=Convert.ToString(Get(selector,"TextTrue"),CultureInfo.InvariantCulture);bool desired=false;
   foreach(string annex in plan.Annexes)foreach(string option in annex.Split('|'))if(option==label)desired=true;
   if(current!=desired)exact=false;
  }
  foreach(bool item in found)if(!item)exact=false;
  declarationAnnexMatched=exact&&declarationAnnexSelectedCount==plan.Annexes.Length;Record();
 }
 private void ConfigureDeclarationPeriod(Control period){
  HtkkDeclarationCasePlan plan=declarationPlan;SetStage(HtkkAutomationStage.DeclarationPeriodConfiguring);Record();
  if(Convert.ToString(Global("MenuID"),CultureInfo.InvariantCulture)!=plan.MenuId)throw new InvalidOperationException();
  if(plan.PeriodKind=="month"){SetCheck(Named(period,"chkTkhaiThang"),true);}
  else if(plan.PeriodKind=="quarter"){SetCheck(Named(period,"chkTKQuy"),true);}
  // KieuKy 18 Lần phát sinh: CheckedChanged (0x60004b2) unticks Tháng and shows the ngày/tháng/năm boxes.
  else if(plan.PeriodKind=="day"){SetCheck(Named(period,"chkTKLanPS"),true);}
  if(VisibleNamed(period,"OptChinhthuc")){SetCheck(Named(period,"OptChinhthuc"),true);periodFirstMatched=CheckValue(Named(period,"OptChinhthuc"))&&(!VisibleNamed(period,"OptBosung")||!CheckValue(ReadableNamed(period,"OptBosung")));}else periodFirstMatched=true;
  if(plan.PeriodKind!="range")SetDeclarationText(period,"mskYear",plan.Year);
  if(plan.PeriodKind=="month")SetDeclarationText(period,"mskMonth",plan.PeriodNumber);
  // The day goes into the VISIBLE original boxes only (mskDay_Leave/mskMonth_Leave pad to two digits).
  if(plan.PeriodKind=="day"){SetDeclarationText(period,"mskMonth",plan.FromDate.Substring(3,2));SetDeclarationText(period,"mskDay",plan.FromDate.Substring(0,2));}
  if(plan.PeriodKind=="quarter"){ComboBox quarter=Named(period,"cbbQuy") as ComboBox;if(quarter==null)throw new InvalidOperationException();int index=quarter.FindStringExact(plan.PeriodNumber);if(index<0)throw new InvalidOperationException();if(quarter.SelectedIndex!=index)quarter.SelectedIndex=index;}
  if(plan.KieuKy=="11"||plan.KieuKy=="26"||plan.KieuKy=="22"){SetDeclarationText(period,"mskTuNgay",plan.FromDate);SetDeclarationText(period,"mskDenNgay",plan.ToDate);}
  if(plan.KieuKy=="12"){SetDeclarationText(period,"mskTuThang",plan.FromDate);SetDeclarationText(period,"mskDenThang",plan.ToDate);}
  bool continuous=true;
  if(plan.ContinuousOperation){Control going=ReadableNamed(period,"chkQTTungNam_HoatDongLienTuc");if(going.Enabled&&!CheckValue(going))SetCheck(going,true);continuous=CheckValue(going)&&(!VisibleNamed(period,"chkQTNamDau_KhongHoatDongLienTuc")||!CheckValue(ReadableNamed(period,"chkQTNamDau_KhongHoatDongLienTuc")));}
  // KieuKy 22: the year box is hidden (GetPeriodInfo takes Nam from mskDenNgay), so only the two VISIBLE date boxes count.
  // Lần phát sinh: chkTKLanPS ticked (Tháng not), the three visible boxes hold the day, from/to boxes hidden.
  if(plan.PeriodKind=="day")periodDateMatched=CheckValue(ReadableNamed(period,"chkTKLanPS"))&&!CheckValue(ReadableNamed(period,"chkTkhaiThang"))
   &&VisibleNamed(period,"mskDay")&&VisibleNamed(period,"mskMonth")&&VisibleNamed(period,"mskYear")&&!VisibleNamed(period,"mskTuNgay")&&!VisibleNamed(period,"mskDenNgay")
   &&ReadableNamed(period,"mskDay").Text==plan.FromDate.Substring(0,2)&&ReadableNamed(period,"mskMonth").Text==plan.FromDate.Substring(3,2)&&ReadableNamed(period,"mskYear").Text==plan.Year&&continuous;
  else if(plan.PeriodKind=="range")periodDateMatched=VisibleNamed(period,"mskTuNgay")&&VisibleNamed(period,"mskDenNgay")&&ReadableNamed(period,"mskTuNgay").Text==plan.FromDate&&ReadableNamed(period,"mskDenNgay").Text==plan.ToDate&&continuous;
  else periodDateMatched=ReadableNamed(period,"mskYear").Text==plan.Year&&(plan.PeriodKind!="month"||(ReadableNamed(period,"mskMonth").Text==plan.PeriodNumber&&CheckValue(ReadableNamed(period,"chkTkhaiThang"))))&&(plan.PeriodKind!="quarter"||CheckValue(ReadableNamed(period,"chkTKQuy")))
   &&((plan.KieuKy!="11"&&plan.KieuKy!="26")||(MaskedTextMatches(period,"mskTuNgay",plan.FromDate)&&MaskedTextMatches(period,"mskDenNgay",plan.ToDate)))&&continuous;
  // Geography/tax-office panel only where the original layout shows it (e.g. NopTheoTinhCQT).
  bool geography=true;
  if(VisibleNamed(period,"cboTinh")){SetStage(HtkkAutomationStage.GtgtPeriodProvinceSelecting);Record();geography=SelectGeography(period,"cboTinh","101","Thành phố Hà Nội","MaTinh","TenTinh")&&geography;}
  if(VisibleNamed(period,"cboXa")){SetStage(HtkkAutomationStage.GtgtPeriodWardSelecting);Record();geography=SelectGeography(period,"cboXa","10129087","Phường Sơn Tây","MaXa","TenXa")&&geography;}
  if(VisibleNamed(period,"cboCQTCuc")){SetStage(HtkkAutomationStage.GtgtPeriodTaxheadSelecting);Record();geography=SelectGeography(period,"cboCQTCuc","10100","Thuế Thành phố Hà Nội","maCQTCapCuc","tenCQTCapCuc")&&geography;}
  if(VisibleNamed(period,"cboCQTChiCuc")){SetStage(HtkkAutomationStage.GtgtPeriodTaxlocalSelecting);Record();geography=SelectGeography(period,"cboCQTChiCuc","10129","Thuế cơ sở 16 Thành phố Hà Nội","maCQTQuanLy","tenCQTQuanLy")&&geography;}
  periodGeographyMatched=geography;
  SelectDeclarationAnnexes(period);
  periodDescriptions.Clear();periodControlCount=0;int visited=0;DescribePeriod(period,ref visited);
  declarationPeriodMatched=periodDateMatched&&periodFirstMatched&&periodGeographyMatched;
  if(!declarationPeriodMatched||!declarationAnnexMatched){DeclarationTerminal(HtkkAutomationStage.DeclarationPeriodInputsNotMatched);return;}
  Button confirm=Named(period,"btnDongY") as Button;if(confirm==null||confirm.Text.Replace("&",String.Empty).Trim()!="Đồng ý")throw new InvalidOperationException();
  navigationPhase="decl-sheet";SetStage(HtkkAutomationStage.DeclarationPeriodConfirmInvoking);periodConfirmInvoked=true;Record();
  // Original OpenToKhai is modal; observe its sheet from inside that ORIGINAL message loop.
  using(System.Windows.Forms.Timer watcher=new System.Windows.Forms.Timer()){
   watcher.Interval=100;watcher.Tick+=delegate(object sender,EventArgs args){try{if(!declarationFlowStarted)InspectDeclarationSheet();if(finished||declarationFlowStarted)watcher.Stop();}catch(Exception error){watcher.Stop();Failure(error);}};
   watcher.Start();try{confirm.PerformClick();}finally{watcher.Stop();}
  }
  if(!finished&&!declarationFlowStarted){SetStage(HtkkAutomationStage.DeclarationSheetWaiting);Record();}
 }

 // ---- Original declaration sheet: identity, pins, then original import ----
 private void InspectDeclarationSheet(){if(declarationSheetBusy)return;declarationSheetBusy=true;try{InspectDeclarationSheetCore();}finally{declarationSheetBusy=false;}}
 private bool DeclarationPinsMatched(){
  HtkkDeclarationCasePlan plan=declarationPlan;string root=Path.GetDirectoryName(project);
  return Hash(Path.Combine(root,plan.WorkbookFile))==plan.WorkbookSha256&&Hash(Path.Combine(root,plan.LayoutFile))==plan.LayoutSha256&&Hash(Path.Combine(root,"InterfaceTemplates/"+plan.SchemaFile))==plan.SchemaSha256&&Hash(Path.Combine(root,"InterfaceTemplates/"+plan.BaseSchemaFile))==plan.BaseSchemaSha256&&Hash(Path.Combine(root,"InterfaceTemplates/xmldsig-core-schema.xsd"))==HtkkDeclarationCasePlans.XmldsigSha256;
 }
 private bool DeclarationIdentity(){
  HtkkDeclarationCasePlan plan=declarationPlan;object business=Global("InstanceClass"),info=Global("ToKhaiInfo"),period=Global("TTPeriodInfo");
  if(business==null||info==null||period==null)return false;
  bool menu=Convert.ToString(Global("MenuID"),CultureInfo.InvariantCulture)==plan.MenuId&&Convert.ToString(Get(info,"VersionXML"),CultureInfo.InvariantCulture)==plan.VersionXml&&business.GetType().FullName=="TAX.HTKK.Business."+plan.BusinessClass;
  string kind=plan.PeriodKind=="month"?"M":plan.PeriodKind=="quarter"?"Q":plan.PeriodKind=="range"?"D_D":plan.PeriodKind=="day"?"D":"Y";
  bool periodMatched=Convert.ToString(Get(period,"KieuKy"),CultureInfo.InvariantCulture)==kind&&Convert.ToString(Get(period,"Nam"),CultureInfo.InvariantCulture)==plan.Year&&Convert.ToString(Get(period,"LoaiToKhai"),CultureInfo.InvariantCulture)=="C"
   &&(plan.PeriodKind!="month"||Convert.ToString(Get(period,"Thang"),CultureInfo.InvariantCulture)==plan.PeriodNumber)&&(plan.PeriodKind!="quarter"||Convert.ToString(Get(period,"Quy"),CultureInfo.InvariantCulture)==plan.PeriodNumber)
   &&(plan.PeriodKind!="range"||(Convert.ToString(Get(period,"TuNgay"),CultureInfo.InvariantCulture)==plan.FromDate&&Convert.ToString(Get(period,"DenNgay"),CultureInfo.InvariantCulture)==plan.ToDate))
   // KieuKy D (GetPeriodInfo chkTKLanPS branch): the same day in TuNgay, DenNgay and kyKKhai; Ngay/Thang padded.
   &&(plan.PeriodKind!="day"||(Convert.ToString(Get(period,"TuNgay"),CultureInfo.InvariantCulture)==plan.FromDate&&Convert.ToString(Get(period,"DenNgay"),CultureInfo.InvariantCulture)==plan.ToDate
    &&Convert.ToString(Get(period,"kyKKhai"),CultureInfo.InvariantCulture)==plan.FromDate&&Convert.ToString(Get(period,"Ngay"),CultureInfo.InvariantCulture)==plan.FromDate.Substring(0,2)&&Convert.ToString(Get(period,"Thang"),CultureInfo.InvariantCulture)==plan.FromDate.Substring(3,2)));
  return menu&&periodMatched;
 }
 private void InspectDeclarationSheetCore(){
  if(finished||declarationFlowStarted)return;
  List<Form> forms=new List<Form>();int visited=0;foreach(Form top in Application.OpenForms){if(visited>=512)break;if(top.Visible&&!top.IsDisposed)FindWorksheets(top,forms,ref visited);}
  // Runs 42218288529/42218296460 waited 120 s: the original period confirmation can refuse
  // the reviewed period/annex set with a modal catalogue message (e.g. 0485, 0682) before
  // any sheet opens. Report its catalogue ID only (never text) and stop; nothing is clicked.
  Form periodMessage;string periodText;
  if(forms.Count==0&&!declarationSheetObserved&&DeclarationMessage(out periodMessage,out periodText)){declarationPeriodRejectedMessageId=OriginalMessageCatalogueId(periodText);DeclarationTerminal(HtkkAutomationStage.DeclarationPeriodOriginalMessageRejected);return;}
  if(forms.Count!=1){SetStage(HtkkAutomationStage.DeclarationSheetWaiting);Record();return;}
  List<Control> grids=new List<Control>();visited=0;GatherSpreads(forms[0],grids,ref visited);if(grids.Count!=1){SetStage(HtkkAutomationStage.DeclarationSheetWaiting);Record();return;}
  Control grid=grids[0];declarationSheetObserved=true;declarationSheetCount=Convert.ToInt32(Get(Get(grid,"Sheets"),"Count"));
  if(declarationClock==null)declarationClock=Stopwatch.StartNew();
  object sheet=Get(grid,"ActiveSheet");bool ready=Convert.ToBoolean(Get(sheet,"AutoCalculation"))&&forms[0].Enabled&&grid.Enabled&&!OriginalMessageVisible();
  declarationIdentityMatched=DeclarationIdentity();declarationSourcePinsMatched=DeclarationPinsMatched();
  bool matched=ready&&declarationIdentityMatched&&declarationSourcePinsMatched&&declarationSheetCount>=1+(HtkkDeclarationCasePlans.ImportAddsAllAnnexes(declarationPlan)?0:declarationPlan.Annexes.Length)&&declarationSheetCount<=64;
  // Original load may pump a progress form while sheet binding is still in flight.
  if(!matched&&declarationClock.Elapsed.TotalSeconds<3){SetStage(HtkkAutomationStage.DeclarationSheetWaiting);Record();return;}
  if(!matched){DeclarationTerminal(HtkkAutomationStage.DeclarationSheetContractNotMatched);return;}
  SetStage(HtkkAutomationStage.DeclarationWebInputChecking);Record();VerifyDeclarationWebInput();
  // Native-case mode original-entry-export: no original import, the fixed entry plan is typed instead.
  declarationEntryPlan=HtkkDeclarationCasePlans.Entry(declarationPlan.CaseId);
  declarationFlowStarted=true;exportStarted=true;roundtripOwner=forms[0];declarationPhase=declarationEntryPlan!=null?"entry-ready":"import-ready";SetStage(declarationEntryPlan!=null?HtkkAutomationStage.DeclarationEntryReadyWaiting:HtkkAutomationStage.DeclarationImportReadyWaiting);Record();
  exportWatcher=new System.Windows.Forms.Timer();exportWatcher.Interval=100;exportWatcher.Tick+=delegate(object sender,EventArgs args){try{ContinueDeclarationFlow();}catch(Exception error){exportWatcher.Stop();Failure(error);}};exportWatcher.Start();
 }

 // ---- Grid observation after the original import ----
 private static bool ParseA1(string cell,out int row,out int column){
  row=-1;column=-1;Match match=Regex.Match(cell,"^([A-Z]{1,3})([1-9][0-9]{0,4})$");if(!match.Success)return false;
  column=0;foreach(char letter in match.Groups[1].Value)column=column*26+(letter-'A'+1);column--;row=Int32.Parse(match.Groups[2].Value,CultureInfo.InvariantCulture)-1;return true;
 }
 private object DeclarationSheet(Control grid,string key){
  string name=null;foreach(string pair in declarationPlan.SheetNames){string[] parts=pair.Split('|');if(parts[0]==key)name=parts[1];}
  object sheets=Get(grid,"Sheets");int count=Convert.ToInt32(Get(sheets,"Count"));PropertyInfo item=sheets.GetType().GetProperty("Item",new Type[]{typeof(int)});if(item==null||count<1||count>64)throw new InvalidOperationException();
  object found=null;
  for(int index=0;index<count;index++){object sheet=item.GetValue(sheets,new object[]{index});string sheetName=Convert.ToString(Get(sheet,"SheetName"),CultureInfo.InvariantCulture);if(sheetName==key||(name!=null&&sheetName==name)){if(found!=null)throw new InvalidOperationException();found=sheet;}}
  return found;
 }
 private bool InspectDeclarationGrid(){
  List<Control> grids=new List<Control>();int count=0;GatherSpreads(roundtripOwner,grids,ref count);if(grids.Count!=1)return false;
  if(!DeclarationIdentity())return false;
  declarationCellCheckCount=0;declarationCellMismatchMask=0;declarationCellLockedMask=0;
  string[] checks=declarationPlan.CellChecks;
  for(int index=0;index<checks.Length;index++){
   string[] parts=checks[index].Split('|');int row,column;if(parts.Length!=3||!ParseA1(parts[1],out row,out column))throw new InvalidOperationException();
   declarationCellCheckCount++;object sheet=DeclarationSheet(grids[0],parts[0]);
   if(sheet==null||row>=Convert.ToInt32(Get(sheet,"RowCount"))||column>=Convert.ToInt32(Get(sheet,"ColumnCount"))){declarationCellMismatchMask|=1<<index;continue;}
   object cell=Cell(sheet,row,column);decimal actual,expected;
   // Original numeric cells hold double/decimal; the invariant round-trip text may use an exponent.
   if(!Decimal.TryParse(Convert.ToString(Get(cell,"Value"),CultureInfo.InvariantCulture),NumberStyles.Float,CultureInfo.InvariantCulture,out actual)||!Decimal.TryParse(parts[2],NumberStyles.Number,CultureInfo.InvariantCulture,out expected)||actual!=expected)declarationCellMismatchMask|=1<<index;
   if(Convert.ToBoolean(Get(cell,"Locked")))declarationCellLockedMask|=1<<index;
  }
  return declarationCellMismatchMask==0&&declarationCellCheckCount==checks.Length;
 }

 // ---- Bounded diagnostic of an original 0016 refusal ----
 // frmWinToKhai.cmdExport_Click shows 0016 after WinDoWorkKiemTra when a sheet is not valid;
 // the validators mark each refused cell with HTKKFile.SetNodeBackGroundPink (Cell.BackColor =
 // Color.Pink, ARGB FFFFC0CB) and RemoveValidate restores the others. Read only: sheet index
 // mask, a count, and the first four cells encoded (sheet+1)*1000000+(row+1)*1000+(column+1).
 // No value, text or note is read. Rows/columns beyond 999 and sheets beyond 16 are not scanned.
 private void InspectDeclarationRefusedCells(){
  List<Control> grids=new List<Control>();int visited=0;GatherSpreads(roundtripOwner,grids,ref visited);if(grids.Count!=1)return;
  object sheets=Get(grids[0],"Sheets");int sheetCount=Convert.ToInt32(Get(sheets,"Count"));PropertyInfo sheetItem=sheets.GetType().GetProperty("Item",new Type[]{typeof(int)});
  if(sheetItem==null||sheetCount<1||sheetCount>64)throw new InvalidOperationException();
  for(int index=0;index<sheetCount&&index<16;index++){
   object sheet=sheetItem.GetValue(sheets,new object[]{index});object cells=Get(sheet,"Cells");PropertyInfo cellItem=cells.GetType().GetProperty("Item",new Type[]{typeof(int),typeof(int)});if(cellItem==null)throw new InvalidOperationException();
   int rows=Math.Min(Convert.ToInt32(Get(sheet,"RowCount")),999),columns=Math.Min(Convert.ToInt32(Get(sheet,"ColumnCount")),999);
   for(int row=0;row<rows;row++)for(int column=0;column<columns;column++){
    object cell=cellItem.GetValue(cells,new object[]{row,column});object color=Get(cell,"BackColor");MethodInfo argb=color.GetType().GetMethod("ToArgb",Type.EmptyTypes);
    if(argb==null||Convert.ToInt32(argb.Invoke(color,null))!=unchecked((int)0xFFFFC0CB))continue;
    declarationInvalidSheetMask|=1<<index;int code=(index+1)*1000000+(row+1)*1000+(column+1);
    if(declarationInvalidCellCount==0)declarationInvalidCell1=code;else if(declarationInvalidCellCount==1)declarationInvalidCell2=code;else if(declarationInvalidCellCount==2)declarationInvalidCell3=code;else if(declarationInvalidCellCount==3)declarationInvalidCell4=code;
    if(declarationInvalidCellCount<4096)declarationInvalidCellCount++;
   }
  }
  Record();
 }

 // ---- Pinned schema and exported XML checks ----
 private sealed class DeclarationPinnedSchemaResolver : XmlResolver {
  private readonly Dictionary<string,string> files=new Dictionary<string,string>(StringComparer.OrdinalIgnoreCase);
  public DeclarationPinnedSchemaResolver(string root,HtkkDeclarationCasePlan plan){
   files.Add(Path.GetFullPath(Path.Combine(root,plan.SchemaFile)),plan.SchemaSha256);
   files.Add(Path.GetFullPath(Path.Combine(root,plan.BaseSchemaFile)),plan.BaseSchemaSha256);
   files.Add(Path.GetFullPath(Path.Combine(root,"xmldsig-core-schema.xsd")),HtkkDeclarationCasePlans.XmldsigSha256);
   foreach(string path in files.Keys)Check(path);
  }
  private void Check(string path){
   if(!files.ContainsKey(path))throw new InvalidOperationException();FileInfo file=new FileInfo(path);
   if(!file.Exists||file.Length<1||file.Length>2097152||(file.Attributes&FileAttributes.ReparsePoint)!=0||Hash(path)!=files[path])throw new InvalidOperationException();
   for(DirectoryInfo directory=file.Directory;directory!=null;directory=directory.Parent)if((directory.Attributes&FileAttributes.ReparsePoint)!=0)throw new InvalidOperationException();
  }
  public override ICredentials Credentials {set{if(value!=null)throw new InvalidOperationException();}}
  public override object GetEntity(Uri absoluteUri,string role,Type type){
   if(absoluteUri==null||!absoluteUri.IsAbsoluteUri||!absoluteUri.IsFile||absoluteUri.IsUnc||!String.IsNullOrEmpty(absoluteUri.Host)||!String.IsNullOrEmpty(absoluteUri.Query)||!String.IsNullOrEmpty(absoluteUri.Fragment)||(type!=null&&type!=typeof(Stream)))throw new InvalidOperationException();
   string path=Path.GetFullPath(absoluteUri.LocalPath);Check(path);return new FileStream(path,FileMode.Open,FileAccess.Read,FileShare.Read);
  }
 }
 private bool DeclarationSchemaValid(string path){
  // Pinned local schemas only: no network, UNC, instance schemaLocation or DTD.
  string root=Path.Combine(Path.GetDirectoryName(project),"InterfaceTemplates"),schema=Path.Combine(root,declarationPlan.SchemaFile);DeclarationPinnedSchemaResolver resolver=new DeclarationPinnedSchemaResolver(root,declarationPlan);
  XmlSchemaSet schemas=new XmlSchemaSet();schemas.XmlResolver=resolver;bool valid=true;schemas.ValidationEventHandler+=delegate(object sender,ValidationEventArgs args){valid=false;};
  XmlReaderSettings safe=new XmlReaderSettings();safe.ProhibitDtd=true;safe.XmlResolver=null;
  using(XmlReader reader=XmlReader.Create(schema,safe))schemas.Add(null,reader);schemas.Compile();if(!valid)return false;
  XmlReaderSettings check=new XmlReaderSettings();check.ProhibitDtd=true;check.XmlResolver=null;check.ValidationType=ValidationType.Schema;check.Schemas=schemas;check.ValidationFlags=XmlSchemaValidationFlags.ProcessIdentityConstraints|XmlSchemaValidationFlags.AllowXmlAttributes;check.ValidationEventHandler+=delegate(object sender,ValidationEventArgs args){valid=false;};
  using(XmlReader reader=XmlReader.Create(path,check)){while(reader.Read()){}}
  return valid;
 }
 private static string DeclarationLeaf(XmlDocument document,string path){string query="";foreach(string name in path.Split('/'))query+="/*[local-name()='"+name+"']";XmlNodeList nodes=document.SelectNodes(query);if(nodes.Count!=1||nodes[0].ChildNodes.Count>1)return null;foreach(XmlNode child in nodes[0].ChildNodes)if(child.NodeType!=XmlNodeType.Text)return null;return nodes[0].InnerText;}
 private void ValidateDeclarationExport(){
  SetStage(HtkkAutomationStage.DeclarationExportValidating);Record();
  if(Hash(webInputPath)!=webImportInputSha256)throw new InvalidOperationException();
  declarationSchemaValid=DeclarationSchemaValid(exportPath);
  XmlDocument input=ReadBoundedOriginalXml(webInputPath),output=ReadBoundedOriginalXml(exportPath);
  declarationXmlCheckCount=0;declarationXmlMismatchMask=0;
  for(int index=0;index<declarationPlan.XmlChecks.Length;index++){
   string[] parts=declarationPlan.XmlChecks[index].Split('|');if(parts.Length!=2)throw new InvalidOperationException();
   declarationXmlCheckCount++;if(DeclarationLeaf(output,parts[0])!=parts[1])declarationXmlMismatchMask|=1<<index;
  }
  declarationServiceIdentityMatched=HtkkDeclarationTreeComparison.NativeIdentity(output);declarationCreationDateValid=HtkkDeclarationTreeComparison.CreationDateValid(output);
  int leaves,mask;declarationTreeMatched=HtkkDeclarationTreeComparison.Compare(input,output,declarationPlan.LeafCount-4,HtkkDeclarationCasePlans.ExportDatePaths(declarationPlan),out leaves,out mask);declarationTreeLeafCount=leaves;declarationTreeMismatchMask=mask;
  webServiceIdentityMatched=declarationServiceIdentityMatched;webTaxValuesMatched=declarationTreeMatched;
 }

 // ---- Original import → observe → original export, driven by one UI timer ----
 private bool DeclarationMessage(out Form message,out string text){
  message=null;text=null;
  foreach(Form form in Application.OpenForms){if(!form.Visible||form.GetType().FullName!="TAX.HTKK.Utilities.Control.frmMessage")continue;if(message!=null)throw new InvalidOperationException();message=form;}
  if(message==null)return false;Control[] labels=message.Controls.Find("lblThongBao",true);if(labels.Length!=1)throw new InvalidOperationException();text=labels[0].Text;return true;
 }
 private Button DeclarationMessageClose(Form message){
  Control[] controls=message.Controls.Find("btn_2",true);if(message.Text.Trim()!="Thông Báo"||controls.Length!=1||CountVisibleButtons(message)!=1)throw new InvalidOperationException();
  Button close=controls[0] as Button;if(close==null||!close.Visible||!close.Enabled||close.Text.Replace("&",String.Empty).Trim()!="Đóng")throw new InvalidOperationException();return close;
 }
 private void ContinueDeclarationFlow(){
  if(finished){exportWatcher.Stop();return;}if(exportFilenameEditing||declarationEntryBusy)return;
  if(!DeclarationMode()||declarationPlan==null||!webInputVerified||Hash(webInputPath)!=webImportInputSha256)throw new InvalidOperationException();
  Form message;string text;
  if(declarationPhase.StartsWith("entry-",StringComparison.Ordinal)){ContinueDeclarationEntry();return;}
  if(declarationPhase=="import-ready"){
   if(!OriginalRoundtripOwnerReady())return;
   Button import=Named(roundtripOwner,"cmdImportXML") as Button;if(import==null||import.FindForm()!=roundtripOwner||import.Text.Replace("&",String.Empty).Trim()!="Nhập từ XML"||roundtripImportCommandInvoked)throw new InvalidOperationException();
   roundtripImportCommandInvoked=true;declarationPhase="import-result";SetStage(HtkkAutomationStage.DeclarationImportCommandInvoking);Record();
   roundtripOwner.BeginInvoke(new MethodInvoker(delegate{try{import.PerformClick();}catch(Exception error){Failure(error);}}));return;
  }
  if(declarationPhase=="import-result"){
   if(DeclarationMessage(out message,out text)){
    if(text!="Nhập dữ liệu từ XML thành công."){importRejectedMessageId=OriginalMessageCatalogueId(text);DeclarationTerminal(HtkkAutomationStage.DeclarationImportOriginalMessageRejected);return;}
    FieldInfo loading=OriginalAssembly().GetType("HTKK.frmWinToKhai",true).GetField("FileNameLoading",BindingFlags.Static|BindingFlags.Public|BindingFlags.NonPublic);
    if(loading==null||loading.FieldType!=typeof(string))throw new InvalidOperationException();string actual=(string)loading.GetValue(null);
    roundtripImportPathMatched=!String.IsNullOrEmpty(actual)&&String.Equals(Path.GetFullPath(actual),Path.GetFullPath(webInputPath),StringComparison.OrdinalIgnoreCase);
    if(!roundtripImportDialogMatched||!roundtripImportKeyboardCommitted||!roundtripImportDialogSubmitted||!roundtripImportPathMatched)throw new InvalidOperationException();
    roundtripImportSucceeded=true;declarationPhase="import-inspect";declarationClock=Stopwatch.StartNew();SetStage(HtkkAutomationStage.DeclarationImportSheetChecking);Record();DeclarationMessageClose(message).PerformClick();return;
   }
   if(!roundtripImportDialogSubmitted){SetStage(HtkkAutomationStage.GtgtImportFileDialogWaiting);TrySubmitOriginalFileDialog("Chọn tờ khai để tải vào chương trình",webInputPath,true);}
   return;
  }
  if(declarationPhase=="import-inspect"){
   if(!OriginalRoundtripOwnerReady())return;
   declarationImportSheetMatched=InspectDeclarationGrid();roundtripImportSheetMatched=declarationImportSheetMatched;Record();
   // Original recalculation after import may settle on a later UI turn; bounded wait.
   if(!declarationImportSheetMatched&&declarationClock.Elapsed.TotalSeconds<3)return;
   if(!declarationImportSheetMatched){DeclarationTerminal(HtkkAutomationStage.DeclarationImportSheetNotMatched);return;}
   declarationPhase="export-start";SetStage(HtkkAutomationStage.DeclarationExportReadyWaiting);Record();return;
  }
  if(declarationPhase=="export-start"){
   if(!OriginalRoundtripOwnerReady())return;
   string schema=Path.Combine(Path.GetDirectoryName(project),"InterfaceTemplates/"+declarationPlan.SchemaFile);string originalSchema=Convert.ToString(Get(Global("ToKhaiInfo"),"XsdFileName"),CultureInfo.InvariantCulture);
   exportSchemaPinnedVerified=!String.IsNullOrEmpty(originalSchema)&&String.Equals(Path.GetFullPath(originalSchema),Path.GetFullPath(schema),StringComparison.OrdinalIgnoreCase)&&Hash(schema)==declarationPlan.SchemaSha256&&Hash(Path.Combine(project,"TAX.HTKK.ComputeHash.dll"))=="d9d63921565ea2039109ad63d71977dcf56889cd83851977a0c712873ab687f5";
   if(!exportSchemaPinnedVerified){DeclarationTerminal(HtkkAutomationStage.DeclarationExportNotMatched);return;}
   string directory=Path.Combine(Path.Combine(Path.Combine(Path.GetDirectoryName(project),"DataFiles"),Mst),"reference-declaration-output");if(Directory.Exists(directory)||File.Exists(directory))throw new InvalidOperationException();Directory.CreateDirectory(directory);
   exportPath=Path.Combine(directory,"declaration.xml");exportDestinationFresh=!File.Exists(exportPath);
   Assembly utilities=null;foreach(Assembly loaded in AppDomain.CurrentDomain.GetAssemblies())if(loaded.GetName().Name=="TAX.HTKK.Utilities")utilities=loaded;if(utilities==null)throw new InvalidOperationException();
   Type configuration=utilities.GetType("TAX.HTKK.Utilities.Core.HTKKConfig",true);PropertyInfo temporary=configuration.GetProperty("PATH_TEMP",BindingFlags.Public|BindingFlags.Static);if(temporary==null)throw new InvalidOperationException();expectedSaveTitle="Tệp XML kết xuất tới thư mục "+Convert.ToString(temporary.GetValue(null,null),CultureInfo.InvariantCulture);
   Button command=Named(roundtripOwner,"cmdExport") as Button;if(command==null||command.FindForm()!=roundtripOwner||command.Text.Replace("&",String.Empty).Trim()!="Kết xuất")throw new InvalidOperationException();
   exportCommandInvoked=true;declarationPhase="export-selector";SetStage(HtkkAutomationStage.DeclarationExportCommandInvoking);Record();
   roundtripOwner.BeginInvoke(new MethodInvoker(delegate{try{command.PerformClick();}catch(Exception error){Failure(error);}}));return;
  }
  if(declarationPhase=="export-selector"||declarationPhase=="export-dialog"){
   if(DeclarationMessage(out message,out text)){
    if(text!="Kết xuất tờ khai xml thành công."){exportRejectedMessageId=OriginalMessageCatalogueId(text);if(exportRejectedMessageId==16)InspectDeclarationRefusedCells();DeclarationTerminal(HtkkAutomationStage.DeclarationExportOriginalMessageRejected);return;}
    if(declarationPhase!="export-dialog"||!exportDialogSubmitted)throw new InvalidOperationException();
    InspectOriginalExportDestination();Record();if(!exportOriginalPathMatched)throw new InvalidOperationException();
    ReadOriginalExport();if(!exportXmlRootMatched||!exportSyntheticIdentityMatched)throw new InvalidOperationException();
    Button close=DeclarationMessageClose(message);exportSuccessAcknowledged=true;
    ValidateDeclarationExport();
    bool matched=declarationSchemaValid&&declarationXmlMismatchMask==0&&declarationXmlCheckCount==declarationPlan.XmlChecks.Length&&declarationTreeMatched&&declarationServiceIdentityMatched&&declarationCreationDateValid;
    // An entry case additionally needs every entry step; its success stage names the mode.
    if(declarationEntryPlan!=null)matched=matched&&declarationEntryMethodPinsMatched&&declarationEntryCatalogueMatched&&declarationEntryChoiceMatched&&declarationEntryLocksMatched&&declarationEntryRowsMatched&&declarationEntryValuesMatched&&declarationEntrySheetMatched&&declarationEntryActionCount==declarationEntryPlannedCount;
    DeclarationTerminal(matched?(declarationEntryPlan!=null?HtkkAutomationStage.DeclarationOriginalEntryExported:HtkkAutomationStage.DeclarationWebImportInspected):HtkkAutomationStage.DeclarationExportNotMatched);close.PerformClick();return;
   }
   if(declarationPhase=="export-selector"){
    List<Form> selectors=new List<Form>();int count=0;foreach(Form top in Application.OpenForms)if(top.Visible)FindExportSelectors(top,selectors,ref count);if(selectors.Count==0)return;if(selectors.Count!=1)throw new InvalidOperationException();Form selector=selectors[0];
    RadioButton xml=Named(selector,"radKetXuatXML") as RadioButton,excel=Named(selector,"radKetXuatExcel") as RadioButton;Button button=Named(selector,"btnExport") as Button;
    if(xml==null||excel==null||!xml.Checked||excel.Checked||xml.Text!="Kết xuất XML"||button==null||button.FindForm()!=selector||button.Text.Replace("&",String.Empty).Trim()!="Kết xuất")throw new InvalidOperationException();
    exportSelectorMatched=true;exportButtonInvoked=true;declarationPhase="export-dialog";SetStage(HtkkAutomationStage.DeclarationExportFileDialogWaiting);Record();
    selector.BeginInvoke(new MethodInvoker(delegate{try{button.PerformClick();}catch(Exception error){Failure(error);}}));return;
   }
   if(!exportDialogSubmitted)TrySubmitOriginalFileDialog(expectedSaveTitle,exportPath,false);
   return;
  }
  throw new InvalidOperationException();
 }
}

public sealed class HtkkDeclarationAdapter : IHtkkNativeAutomationAdapter {
 private HtkkGuiReferenceAutomation harness;
 public string AdapterId { get { return "declaration-web"; } }
 public bool CanHandle(HtkkAutomationMode mode) { return mode == HtkkAutomationMode.DeclarationWebImportInspect; }
 public void Initialize(HtkkGuiReferenceAutomation harnessInstance, string projectDir, HtkkAutomationMode mode) {
  if(harnessInstance==null||!CanHandle(mode))throw new ArgumentException();
  harness = harnessInstance;
 }
 public void OnProfileSaved(Form profileOwner, Button closeButton, Control spread) { harness.OnDeclarationProfileSaved(profileOwner, closeButton, spread); }
 public void ContinueNavigation() { harness.ContinueDeclarationNavigation(); }
 public string BuildNavigationJson() { return harness.NavigationJson(); }
}
