// Generic declaration-family driver (mode declaration-web-import-inspect), C# 2.0 / CLR2.
// Cases whose compiled plan has an entry plan (native-case mode original-entry-export) replace the
// original import by typing into the original grid (HtkkDeclarationOriginalEntry.cs); the rest is shared.
// Cases whose plan has an import-tick plan (mode web-xml-import-tick-reexport) keep the original import and then
// perform fixed original edits/ticks for grid-only inputs (HtkkDeclarationCasePlans.ImportTick) before the sheet checks.
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
 // The Y7 0699 notice of the current period confirmation was closed (once per period dialog; see InspectDeclarationSheetCore).
 private bool declarationPeriodInfoClosed=false;
 private int declarationPeriodRejectedMessageId=0,declarationPeriodInfoMessageId=0,declarationAnnexSelectedCount=0,declarationSheetCount=0,declarationCellCheckCount=0,declarationCellMismatchMask=0,declarationCellLockedMask=0,declarationCellZeroMask=0,declarationXmlCheckCount=0,declarationXmlMismatchMask=0,declarationTreeMismatchMask=0,declarationTreeLeafCount=0;
 // B8 visible period annex list (HtkkDeclarationCasePlans.VisibleAnnexListReviewed), value-free and text-free.
 // declarationAnnexListMask bits: 1 the list was visible on a plan whose layout hides it; 2 the reviewed handling matched;
 // 4 a row that is not a checkbox or whose label is neither a case annex nor KHBS; 8 a KHBS row ticked; 16 a KHBS row
 // listed; 32 a case annex missing or listed twice; 64 a case annex unticked and locked (never forced); 128 more than 16
 // rows; 256 the states after the actions differ from the case; 512 chkChonPhuLucKeKhaiAll checked; 1024 it was enabled;
 // 2048 an action could not be made (row hidden, list disabled, focus not on the list or an original message shown); 4096 a
 // Bổ sung round of a form without "Tổng hợp KHBS" (U5) found the list hidden and kept the annexes of the saved version.
 // Rows: row count; masks: bit r = row r (before any action: ticked, locked; after: ticked); actions: SPACE presses.
 private int declarationAnnexListMask=0,declarationAnnexListRows=0,declarationAnnexListTickedBefore=0,declarationAnnexListLockedBefore=0,declarationAnnexListTickedAfter=0,declarationAnnexListActions=0;
 // Period text shapes the opened declaration holds (run 43678756329: 01/TTS G7 quarter, import refused with 0437,
 // WinDoWorkImportFormXml compares kieuKy, kyKKhaiTuNgay/DenNgay/TuThang/DenThang and loaiTKhai with TTinChung).
 // Value-free classes of TTinChung, read once when the declaration sheet opens: bits 0-2 kyKKhaiTuNgay, 3-5
 // kyKKhaiDenNgay, 6-8 kyKKhaiTuThang, 9-11 kyKKhaiDenThang; class 0 not read, 1 empty, 2 the plan's own value
 // (dates: from/to date; months: MM/yyyy of them), 3 the plan year's bound (01/01/yyyy, 31/12/yyyy, 01/yyyy,
 // 12/yyyy), 4 only blanks, slashes or underscores, 5 other text. Bits 12/13: mskTuThang/mskDenThang visible
 // after the period dialog was configured; bit 14: the TTinChung read succeeded.
 private int declarationPeriodShapeMask=0;
 private static int PeriodTextShape(string text,string own,string yearBound){
  if(text==null||text.Length==0)return 1;if(text==own)return 2;if(text==yearBound)return 3;
  bool blank=true;foreach(char c in text)if(c!=' '&&c!='/'&&c!='_'){blank=false;break;}
  return blank?4:5;
 }
 private void ObserveDeclarationPeriodShape(){
  if((declarationPeriodShapeMask&16384)!=0)return;HtkkDeclarationCasePlan plan=declarationPlan;object common=Global("TTinChung");
  if(plan==null||common==null||plan.FromDate.Length!=10||plan.ToDate.Length!=10)return;
  string year=plan.Year;
  int mask=PeriodTextShape(Convert.ToString(Get(common,"kyKKhaiTuNgay"),CultureInfo.InvariantCulture),plan.FromDate,"01/01/"+year)
   |PeriodTextShape(Convert.ToString(Get(common,"kyKKhaiDenNgay"),CultureInfo.InvariantCulture),plan.ToDate,"31/12/"+year)<<3
   |PeriodTextShape(Convert.ToString(Get(common,"kyKKhaiTuThang"),CultureInfo.InvariantCulture),plan.FromDate.Substring(3),"01/"+year)<<6
   |PeriodTextShape(Convert.ToString(Get(common,"kyKKhaiDenThang"),CultureInfo.InvariantCulture),plan.ToDate.Substring(3),"12/"+year)<<9;
  declarationPeriodShapeMask|=mask|16384;
 }
 private bool declarationAnnexListFailed=false;
 private string DeclarationAnnexListJson(){
  string q=((char)34).ToString();StringBuilder json=new StringBuilder();
  string[] names=new string[]{"declarationAnnexListMask","declarationAnnexListRows","declarationAnnexListTickedBefore","declarationAnnexListLockedBefore","declarationAnnexListTickedAfter","declarationAnnexListActions","declarationPeriodShapeMask"};
  int[] counts=new int[]{declarationAnnexListMask,declarationAnnexListRows,declarationAnnexListTickedBefore,declarationAnnexListLockedBefore,declarationAnnexListTickedAfter,declarationAnnexListActions,declarationPeriodShapeMask};
  for(int index=0;index<names.Length;index++)json.Append(","+q+names[index]+q+":"+counts[index].ToString(CultureInfo.InvariantCulture));
  return json.ToString();
 }
 private int declarationInvalidSheetMask=0,declarationInvalidCellCount=0,declarationInvalidCell1=0,declarationInvalidCell2=0,declarationInvalidCell3=0,declarationInvalidCell4=0;
 // Whole-tree comparison detail (HtkkDeclarationTreeComparison.Diagnostics): value-free, path-free classes and counts;
 // the ordinal indexes the synthetic web input only.
 private int declarationTreeAttributeMask=0,declarationTreeTextMismatchCount=0,declarationTreeFirstMismatchOrdinal=0,declarationTreeFirstMismatchKind=0;
 private int declarationTreeMismatch1=0,declarationTreeMismatch2=0,declarationTreeMismatch3=0,declarationTreeMismatch4=0,declarationTreeFirstTextShape=0;
 // Bounded, value-free export wait diagnostics (runs 43498861393/43549091519: values matched, the original
 // "Kết xuất" was invoked and neither the selector nor any message appeared before the probe deadline).
 // declarationUiWaitMask bits: 1 the original import click handler has returned; 2 cmdExport.CanSelect at the
 // last gate check; 4 export click delegate entered; 8 export click delegate returned; 16 that click returned and
 // nothing (selector, message, new form, native dialog) appeared for the settle window; 32 the single bounded
 // second invocation was made; 64 the UI thread did not dispatch for >= 5 s during export (Poll watchdog);
 // 128 the owner (or its MDI parent) was the active form at invocation; 256 a visible native #32770 dialog of
 // this process during the selector wait; 512 owner ready (visible, enabled, no original message) at the last
 // gate check; 1024 the original cmdExport Click event was raised (observer only); 2048 the grid had an
 // active cell editor at invocation.
 // declarationUiForegroundKind: 0 not observed, 1 owner/MDI parent, 2 export selector, 3 original message,
 // 4 other own managed form, 5 own native #32770 dialog, 6 other own-process window, 7 other process, 8 none.
 private int declarationUiWaitMask=0,declarationUiWaitSeconds=0,declarationUiForegroundKind=0,declarationUiVisibleForms=0,declarationUiStallSeconds=0;
 private int declarationExportInvokeCount=0,declarationExportFormsAtInvoke=0,declarationStallRecordedSeconds=0;
 private bool declarationImportClickReturned=false,declarationExportClickReturned=false;
 private Stopwatch declarationExportClock=null,declarationExportQuietClock=null;
 private const double DeclarationExportSettleSeconds=10;
 private string DeclarationUiWaitJson(){
  string q=((char)34).ToString();StringBuilder json=new StringBuilder();
  string[] names=new string[]{"declarationUiWaitMask","declarationUiWaitSeconds","declarationUiForegroundKind","declarationUiVisibleForms","declarationUiStallSeconds"};
  int[] counts=new int[]{declarationUiWaitMask,declarationUiWaitSeconds,declarationUiForegroundKind,declarationUiVisibleForms,declarationUiStallSeconds};
  for(int index=0;index<names.Length;index++)json.Append(","+q+names[index]+q+":"+counts[index].ToString(CultureInfo.InvariantCulture));
  return json.ToString();
 }
 private string DeclarationTreeJson(){
  string q=((char)34).ToString();StringBuilder json=new StringBuilder();
  string[] names=new string[]{"declarationTreeAttributeMask","declarationTreeTextMismatchCount","declarationTreeFirstMismatchOrdinal","declarationTreeFirstMismatchKind","declarationTreeMismatch1","declarationTreeMismatch2","declarationTreeMismatch3","declarationTreeMismatch4","declarationTreeFirstTextShape"};
  int[] counts=new int[]{declarationTreeAttributeMask,declarationTreeTextMismatchCount,declarationTreeFirstMismatchOrdinal,declarationTreeFirstMismatchKind,declarationTreeMismatch1,declarationTreeMismatch2,declarationTreeMismatch3,declarationTreeMismatch4,declarationTreeFirstTextShape};
  for(int index=0;index<names.Length;index++)json.Append(","+q+names[index]+q+":"+counts[index].ToString(CultureInfo.InvariantCulture));
  return json.ToString();
 }
 private bool DeclarationMode(){return modeEnum==HtkkAutomationMode.DeclarationWebImportInspect||DeclarationKhbsMode();}
 private string DeclarationJson(){
  string q=((char)34).ToString();StringBuilder json=new StringBuilder();
  string[] names=new string[]{"declarationMenuClicked","declarationPeriodObserved","declarationPeriodMatched","declarationAnnexMatched","declarationSheetObserved","declarationIdentityMatched","declarationSourcePinsMatched","declarationImportSheetMatched","declarationSchemaValid","declarationServiceIdentityMatched","declarationCreationDateValid","declarationTreeMatched"};
  bool[] values=new bool[]{declarationMenuClicked,declarationPeriodObserved,declarationPeriodMatched,declarationAnnexMatched,declarationSheetObserved,declarationIdentityMatched,declarationSourcePinsMatched,declarationImportSheetMatched,declarationSchemaValid,declarationServiceIdentityMatched,declarationCreationDateValid,declarationTreeMatched};
  for(int index=0;index<names.Length;index++)json.Append(","+q+names[index]+q+":"+Bool(values[index]));
  names=new string[]{"declarationPeriodRejectedMessageId","declarationPeriodInfoMessageId","declarationAnnexSelectedCount","declarationSheetCount","declarationCellCheckCount","declarationCellMismatchMask","declarationCellLockedMask","declarationCellZeroMask","declarationXmlCheckCount","declarationXmlMismatchMask","declarationTreeMismatchMask","declarationTreeLeafCount","declarationInvalidSheetMask","declarationInvalidCellCount","declarationInvalidCell1","declarationInvalidCell2","declarationInvalidCell3","declarationInvalidCell4"};
  int[] counts=new int[]{declarationPeriodRejectedMessageId,declarationPeriodInfoMessageId,declarationAnnexSelectedCount,declarationSheetCount,declarationCellCheckCount,declarationCellMismatchMask,declarationCellLockedMask,declarationCellZeroMask,declarationXmlCheckCount,declarationXmlMismatchMask,declarationTreeMismatchMask,declarationTreeLeafCount,declarationInvalidSheetMask,declarationInvalidCellCount,declarationInvalidCell1,declarationInvalidCell2,declarationInvalidCell3,declarationInvalidCell4};
  for(int index=0;index<names.Length;index++)json.Append(","+q+names[index]+q+":"+counts[index].ToString(CultureInfo.InvariantCulture));
  return json.ToString()+DeclarationEntryJson()+DeclarationTickJson()+DeclarationTreeJson()+DeclarationUiWaitJson()+DeclarationAnnexListJson()+DeclarationKhbsJson()+DeclarationAnnex12Json();
 }
 private void DeclarationTerminal(HtkkAutomationStage stage){SetStage(stage);finished=true;Record();if(exportWatcher!=null)exportWatcher.Stop();}

 // ---- Web input: own private staged sidecars only (never edits the XML) ----
 private string ReadDeclarationCaseId(){
  string host=Assembly.GetExecutingAssembly().Location;if(!String.Equals(Path.GetDirectoryName(host),project,StringComparison.OrdinalIgnoreCase))throw new InvalidOperationException();
  FileInfo caseFile=new FileInfo(host+".web-case.id");if(!caseFile.Exists||(caseFile.Attributes&FileAttributes.ReparsePoint)!=0||caseFile.Length<1||caseFile.Length>64)throw new InvalidOperationException();
  return File.ReadAllText(caseFile.FullName,Encoding.ASCII);
 }
 // Profile CQT and period place of the staged case (HtkkDeclarationCasePlans.Geography), read once before the profile is
 // edited; outside the declaration modes (no staged case) the fixed defaults.
 private HtkkCaseGeography caseGeography=null;private string caseGeographyId=null;
 private HtkkCaseGeography CaseGeography(){
  if(caseGeography!=null)return caseGeography;
  if(DeclarationMode()){string id=ReadDeclarationCaseId();if(HtkkDeclarationCasePlans.Find(id)==null)throw new InvalidOperationException();caseGeographyId=id;}
  caseGeography=HtkkDeclarationCasePlans.Geography(caseGeographyId);return caseGeography;
 }
 private void VerifyDeclarationWebInput(){
  string host=Assembly.GetExecutingAssembly().Location;
  string id=ReadDeclarationCaseId();HtkkDeclarationCasePlan plan=HtkkDeclarationCasePlans.Find(id);
  if(plan==null||(declarationPlan!=null&&declarationPlan.CaseId!=id)||(caseGeographyId!=null&&caseGeographyId!=id))throw new InvalidOperationException();
  declarationPlan=plan;webCaseId=id;
  webInputPath=host+".web-input.xml";webImportInputSha256=ReadOwnHexSidecar(host+".web-input.sha256",64);webSourceSha=ReadOwnHexSidecar(host+".web-source.sha",40);
  XmlDocument document=ReadBoundedOriginalXml(webInputPath);if(Hash(webInputPath)!=webImportInputSha256)throw new InvalidOperationException();
  if(FixedWebLeaf(document,"TTinChung/TTinTKhaiThue/NNT/mst")!=Mst||FixedWebLeaf(document,"TTinChung/TTinTKhaiThue/NNT/tenNNT")!=FakeName||FixedWebLeaf(document,"TTinChung/TTinTKhaiThue/TKhaiThue/nguoiKy")!=FakeSigner)throw new InvalidOperationException();
  if(FixedWebLeaf(document,"TTinChung/TTinDVu/maDVu")!="CCKK"||FixedWebLeaf(document,"TTinChung/TTinDVu/tenDVu")!=plan.WebServiceName||FixedWebLeaf(document,"TTinChung/TTinDVu/ttinNhaCCapDVu")!="hotrokekhai.net — Công cụ Kê khai, công cụ độc lập"||!Regex.IsMatch(FixedWebLeaf(document,"TTinChung/TTinDVu/pbanDVu"),"^[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}$"))throw new InvalidOperationException();
  if(FixedWebLeaf(document,"TTinChung/TTinTKhaiThue/TKhaiThue/maTKhai")!=plan.MaTKhai||FixedWebLeaf(document,"TTinChung/TTinTKhaiThue/TKhaiThue/pbanTKhaiXML")!=plan.VersionXml)throw new InvalidOperationException();
  // Kê khai bổ sung mode: the KHBS case ids only (HtkkDeclarationKhbs.cs), never a lần-đầu declaration case, and back.
  if((HtkkDeclarationCasePlans.KhbsSoLan(id)>0)!=DeclarationKhbsMode())throw new InvalidOperationException();
  if(DeclarationKhbsMode())VerifyDeclarationKhbsInputs(host);
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
 private string[] ObservedAnnexLabels(object sheet,int rows,bool[] ticked,bool[] locked){
  string[] labels=new string[rows];
  for(int row=0;row<rows;row++){
   object selector=Get(Cell(sheet,row,0),"CellType");
   if(selector==null||selector.GetType().FullName!="FarPoint.Win.Spread.CellType.CheckBoxCellType")continue;
   labels[row]=Convert.ToString(Get(selector,"TextTrue"),CultureInfo.InvariantCulture);
   ticked[row]=Selected(Get(Cell(sheet,row,0),"Value"));locked[row]=Convert.ToBoolean(Get(Cell(sheet,row,0),"Locked"));
  }
  return labels;
 }
 // Observe every row (before), select exactly the case annexes with the original SPACE on unlocked unticked rows, never a KHBS
 // row (a lần đầu case), never a locked row, then read every row again. Any other state ends at
 // declaration-period-annex-list-not-matched with the value-free masks above; nothing is retried.
 private void SelectReviewedVisibleAnnexList(Control grid){
  HtkkDeclarationCasePlan plan=declarationPlan;SetStage(HtkkAutomationStage.DeclarationPeriodAnnexSelecting);
  object sheet=Get(grid,"ActiveSheet");int rows=Convert.ToInt32(Get(sheet,"RowCount"));if(rows<0||rows>512)throw new InvalidOperationException();
  declarationAnnexListRows=rows;declarationAnnexListFailed=true;declarationAnnexMatched=false;
  Control[] all=grid.Parent==null?new Control[0]:grid.Parent.Controls.Find("chkChonPhuLucKeKhaiAll",false);
  if(all.Length==1){if(CheckValue(all[0]))declarationAnnexListMask|=512;if(all[0].Enabled)declarationAnnexListMask|=1024;}
  if(rows>16){declarationAnnexListMask|=128;Record();return;}
  bool[] ticked=new bool[rows],locked=new bool[rows];int[] owner=new int[rows];
  string[] labels=ObservedAnnexLabels(sheet,rows,ticked,locked);
  for(int row=0;row<rows;row++){if(ticked[row])declarationAnnexListTickedBefore|=1<<row;if(locked[row])declarationAnnexListLockedBefore|=1<<row;}
  declarationAnnexListMask|=HtkkDeclarationCasePlans.ClassifyVisibleAnnexList(plan,labels,ticked,locked,owner);
  Record();if((declarationAnnexListMask&(4|8|32|64))!=0)return;
  for(int row=0;row<rows;row++){
   if(owner[row]<0||Selected(Get(Cell(sheet,row,0),"Value")))continue;
   if(Convert.ToBoolean(Get(Cell(sheet,row,0),"Locked"))){declarationAnnexListMask|=64;Record();return;}
   if(!RowVisible(sheet,row)||!grid.Visible||!grid.Enabled||OriginalMessageVisible()){declarationAnnexListMask|=2048;Record();return;}
   grid.Focus();sheet.GetType().GetMethod("SetActiveCell",new Type[]{typeof(int),typeof(int)}).Invoke(sheet,new object[]{row,0});
   uint pid;GetWindowThreadProcessId(GetForegroundWindow(),out pid);
   if(pid!=(uint)Process.GetCurrentProcess().Id||!grid.ContainsFocus){declarationAnnexListMask|=2048;Record();return;}
   SendKeys.SendWait(" ");declarationAnnexListActions++;
   if(OriginalMessageVisible()){declarationAnnexListMask|=2048;Record();return;}
  }
  // Read back every row: same row count, every case annex ticked, every KHBS row clear.
  bool[] after=new bool[rows],afterLocked=new bool[rows];
  string[] afterLabels=Convert.ToInt32(Get(sheet,"RowCount"))==rows?ObservedAnnexLabels(sheet,rows,after,afterLocked):null;
  declarationAnnexSelectedCount=0;
  for(int row=0;row<rows;row++)if(after[row]){declarationAnnexListTickedAfter|=1<<row;declarationAnnexSelectedCount++;}
  if(afterLabels==null||!HtkkDeclarationCasePlans.VisibleAnnexListExact(plan,afterLabels,after,owner)){declarationAnnexListMask|=256;Record();return;}
  declarationAnnexListMask|=2;declarationAnnexListFailed=false;declarationAnnexMatched=true;Record();
 }
 private void SelectDeclarationAnnexes(Control period){
  HtkkDeclarationCasePlan plan=declarationPlan;bool[] found=new bool[plan.Annexes.Length];
  Control[] annexes=period.Controls.Find("axfpsPhuLuc",true);
  if(annexes.Length!=1||!IsSpread(annexes[0])){declarationAnnexMatched=plan.Annexes.Length==0;return;}
  Control grid=annexes[0];bool hidden=HtkkDeclarationCasePlans.AnnexPanelHidden(plan);
  if(hidden){
   // Observation only: no click on a list the original layout hides. Matched only if the
   // original defaults already include every reviewed annex of the case.
   // A visible list fails here unless its menu has a reviewed visible-list handling (B8 after a typed year).
   if(grid.Visible){declarationAnnexListMask|=1;if(!HtkkDeclarationCasePlans.VisibleAnnexListReviewed(plan)){declarationAnnexMatched=false;return;}SelectReviewedVisibleAnnexList(grid);return;}
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
  // A Bổ sung round of a form without "Tổng hợp KHBS" (U5, KieuKHBS ""): UpdatePeriodByVerSion hides the list, the bổ sung opens
  // with the annexes of the saved previous version. Observation only (nothing is clicked); the imported sheets decide
  // (declarationImportSheetMatched).
  if(!grid.Visible&&DeclarationKhbsMode()&&declarationKhbsRound>0&&!HtkkDeclarationCasePlans.KhbsSummary(webCaseId)){declarationAnnexListMask|=4096;declarationAnnexMatched=true;Record();return;}
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
  // KieuKy 14 (Z8, frmHTKKPeriod.SetLayoutToKhaiQuy 0x60004a7): quarter is the only period, so the original layout may
  // show chkTKQuy already ticked and locked, or not at all. Tick it only when it is visible, enabled and unticked; the
  // original GetPeriodInfo result (DeclarationIdentity: KieuKy Q, Quy, Nam) is the authority either way.
  else if(plan.PeriodKind=="quarter"&&plan.KieuKy=="14"){Control[] quarterBox=period.Controls.Find("chkTKQuy",true);if(quarterBox.Length>1)throw new InvalidOperationException();if(quarterBox.Length==1&&quarterBox[0].Visible&&quarterBox[0].Enabled&&!CheckValue(quarterBox[0]))SetCheck(quarterBox[0],true);}
  else if(plan.PeriodKind=="quarter"){SetCheck(Named(period,"chkTKQuy"),true);}
  // KieuKy 18 Lần phát sinh: CheckedChanged (0x60004b2) unticks Tháng and shows the ngày/tháng/năm boxes.
  else if(plan.PeriodKind=="day"){SetCheck(Named(period,"chkTKLanPS"),true);}
  if(DeclarationKhbsMode()&&declarationKhbsRound>0)periodFirstMatched=false;
  else if(VisibleNamed(period,"OptChinhthuc")){SetCheck(Named(period,"OptChinhthuc"),true);periodFirstMatched=CheckValue(Named(period,"OptChinhthuc"))&&(!VisibleNamed(period,"OptBosung")||!CheckValue(ReadableNamed(period,"OptBosung")));}else periodFirstMatched=true;
  if(plan.PeriodKind!="range")SetDeclarationText(period,"mskYear",plan.Year);
  if(plan.PeriodKind=="month")SetDeclarationText(period,"mskMonth",plan.PeriodNumber);
  // The day goes into the VISIBLE original boxes only (mskDay_Leave/mskMonth_Leave pad to two digits).
  if(plan.PeriodKind=="day"){SetDeclarationText(period,"mskMonth",plan.FromDate.Substring(3,2));SetDeclarationText(period,"mskDay",plan.FromDate.Substring(0,2));}
  if(plan.PeriodKind=="quarter"){ComboBox quarter=Named(period,"cbbQuy") as ComboBox;if(quarter==null)throw new InvalidOperationException();int index=quarter.FindStringExact(plan.PeriodNumber);if(index<0)throw new InvalidOperationException();if(quarter.SelectedIndex!=index)quarter.SelectedIndex=index;}
  if(plan.KieuKy=="11"||plan.KieuKy=="26"||plan.KieuKy=="22"){SetDeclarationText(period,"mskTuNgay",plan.FromDate);SetDeclarationText(period,"mskDenNgay",plan.ToDate);}
  if(plan.KieuKy=="12"){SetDeclarationText(period,"mskTuThang",plan.FromDate);SetDeclarationText(period,"mskDenThang",plan.ToDate);}
  // Kê khai bổ sung rounds: Bổ sung, the lần and the fixed ngày lập, after the period boxes (their Leave handlers run first).
  if(DeclarationKhbsMode()&&declarationKhbsRound>0)periodFirstMatched=ConfigureDeclarationKhbsPeriod(period);
  if(VisibleNamed(period,"mskTuThang"))declarationPeriodShapeMask|=4096;if(VisibleNamed(period,"mskDenThang"))declarationPeriodShapeMask|=8192;
  bool continuous=true;
  if(plan.ContinuousOperation){Control going=ReadableNamed(period,"chkQTTungNam_HoatDongLienTuc");if(going.Enabled&&!CheckValue(going))SetCheck(going,true);continuous=CheckValue(going)&&(!VisibleNamed(period,"chkQTNamDau_KhongHoatDongLienTuc")||!CheckValue(ReadableNamed(period,"chkQTNamDau_KhongHoatDongLienTuc")));}
  // KieuKy 22: the year box is hidden (GetPeriodInfo takes Nam from mskDenNgay), so only the two VISIBLE date boxes count.
  // Lần phát sinh: chkTKLanPS ticked (Tháng not), the three visible boxes hold the day, from/to boxes hidden.
  if(plan.PeriodKind=="day")periodDateMatched=CheckValue(ReadableNamed(period,"chkTKLanPS"))&&!CheckValue(ReadableNamed(period,"chkTkhaiThang"))
   &&VisibleNamed(period,"mskDay")&&VisibleNamed(period,"mskMonth")&&VisibleNamed(period,"mskYear")&&!VisibleNamed(period,"mskTuNgay")&&!VisibleNamed(period,"mskDenNgay")
   &&ReadableNamed(period,"mskDay").Text==plan.FromDate.Substring(0,2)&&ReadableNamed(period,"mskMonth").Text==plan.FromDate.Substring(3,2)&&ReadableNamed(period,"mskYear").Text==plan.Year&&continuous;
  else if(plan.PeriodKind=="range")periodDateMatched=VisibleNamed(period,"mskTuNgay")&&VisibleNamed(period,"mskDenNgay")&&ReadableNamed(period,"mskTuNgay").Text==plan.FromDate&&ReadableNamed(period,"mskDenNgay").Text==plan.ToDate&&continuous;
  else periodDateMatched=ReadableNamed(period,"mskYear").Text==plan.Year&&(plan.PeriodKind!="month"||(ReadableNamed(period,"mskMonth").Text==plan.PeriodNumber&&CheckValue(ReadableNamed(period,"chkTkhaiThang"))))&&(plan.PeriodKind!="quarter"||(plan.KieuKy=="14"?(!VisibleNamed(period,"chkTKQuy")||CheckValue(ReadableNamed(period,"chkTKQuy")))&&(!VisibleNamed(period,"chkTkhaiThang")||!CheckValue(ReadableNamed(period,"chkTkhaiThang"))):CheckValue(ReadableNamed(period,"chkTKQuy"))))
   &&((plan.KieuKy!="11"&&plan.KieuKy!="26")||(MaskedTextMatches(period,"mskTuNgay",plan.FromDate)&&MaskedTextMatches(period,"mskDenNgay",plan.ToDate)))&&continuous;
  // Geography/tax-office panel only where the original layout shows it (e.g. NopTheoTinhCQT).
  bool geography=true;
  // The case's place (defaults 101 / 10129087 / 10100 / 10129); each combo is refilled by the original handler of the one before.
  HtkkCaseGeography place=CaseGeography();
  if(VisibleNamed(period,"cboTinh")){SetStage(HtkkAutomationStage.GtgtPeriodProvinceSelecting);Record();geography=SelectGeography(period,"cboTinh",place.ProvinceCode,place.ProvinceName,"MaTinh","TenTinh")&&geography;}
  if(VisibleNamed(period,"cboXa")){SetStage(HtkkAutomationStage.GtgtPeriodWardSelecting);Record();geography=SelectGeography(period,"cboXa",place.WardCode,place.WardName,"MaXa","TenXa")&&geography;}
  if(VisibleNamed(period,"cboCQTCuc")){SetStage(HtkkAutomationStage.GtgtPeriodTaxheadSelecting);Record();geography=SelectGeography(period,"cboCQTCuc",place.HeadCode,place.HeadName,"maCQTCapCuc","tenCQTCapCuc")&&geography;}
  if(VisibleNamed(period,"cboCQTChiCuc")){SetStage(HtkkAutomationStage.GtgtPeriodTaxlocalSelecting);Record();geography=SelectGeography(period,"cboCQTChiCuc",place.OfficeCode,place.OfficeName,"maCQTQuanLy","tenCQTQuanLy")&&geography;}
  periodGeographyMatched=geography;
  SelectDeclarationAnnexes(period);
  periodDescriptions.Clear();periodControlCount=0;int visited=0;DescribePeriod(period,ref visited);
  declarationPeriodMatched=periodDateMatched&&periodFirstMatched&&periodGeographyMatched;
  if(declarationPeriodMatched&&declarationAnnexListFailed){DeclarationTerminal(HtkkAutomationStage.DeclarationPeriodAnnexListNotMatched);return;}
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
  // A later release may re-pin the workbook (reviewed, per version): HtkkOracleBaseline.Workbook.
  return Hash(Path.Combine(root,plan.WorkbookFile))==HtkkOracleBaseline.Workbook(plan.WorkbookFile,plan.WorkbookSha256)&&Hash(Path.Combine(root,plan.LayoutFile))==plan.LayoutSha256&&Hash(Path.Combine(root,"InterfaceTemplates/"+plan.SchemaFile))==plan.SchemaSha256&&Hash(Path.Combine(root,"InterfaceTemplates/"+plan.BaseSchemaFile))==plan.BaseSchemaSha256&&Hash(Path.Combine(root,"InterfaceTemplates/xmldsig-core-schema.xsd"))==HtkkDeclarationCasePlans.XmldsigSha256;
 }
 private bool DeclarationIdentity(){
  HtkkDeclarationCasePlan plan=declarationPlan;object business=Global("InstanceClass"),info=Global("ToKhaiInfo"),period=Global("TTPeriodInfo");
  if(business==null||info==null||period==null)return false;
  bool menu=Convert.ToString(Global("MenuID"),CultureInfo.InvariantCulture)==plan.MenuId&&Convert.ToString(Get(info,"VersionXML"),CultureInfo.InvariantCulture)==plan.VersionXml&&business.GetType().FullName=="TAX.HTKK.Business."+plan.BusinessClass;
  string kind=plan.PeriodKind=="month"?"M":plan.PeriodKind=="quarter"?"Q":plan.PeriodKind=="range"?"D_D":plan.PeriodKind=="day"?"D":"Y";
  bool periodMatched=Convert.ToString(Get(period,"KieuKy"),CultureInfo.InvariantCulture)==kind&&Convert.ToString(Get(period,"Nam"),CultureInfo.InvariantCulture)==plan.Year&&Convert.ToString(Get(period,"LoaiToKhai"),CultureInfo.InvariantCulture)==(DeclarationKhbsMode()&&declarationKhbsRound>0?"B":"C")&&(!DeclarationKhbsMode()||declarationKhbsRound==0||Convert.ToString(Get(period,"SoLan"),CultureInfo.InvariantCulture)==declarationKhbsRound.ToString(CultureInfo.InvariantCulture))
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
  // Y7 (01/TCKT TT89) only: btnDongY_Click shows the information message 0699 after every period check passed and then
  // opens the tờ khai (HtkkDeclarationCasePlans.PeriodInfoMessageAccepted). It is recorded and closed once with its only
  // button ("Đóng"); any other message, or a second one in the same period confirmation, is still a refusal. A kê khai bổ
  // sung case opens the period dialog once per round (lần đầu C0, then each bổ sung) and btnDongY_Click shows 0699 each time
  // (runs 44102029926 / 44102047602: round 1 refused the second 0699), so the once-only flag is per round
  // (declarationPeriodInfoClosed, reset by BeginDeclarationKhbsRound); declarationPeriodInfoMessageId keeps the recorded id.
  if(forms.Count==0&&!declarationSheetObserved&&DeclarationMessage(out periodMessage,out periodText)){
   int periodMessageId=OriginalMessageCatalogueId(periodText);
   if(!declarationPeriodInfoClosed&&HtkkDeclarationCasePlans.PeriodInfoMessageAccepted(declarationPlan,periodMessageId)){declarationPeriodInfoClosed=true;declarationPeriodInfoMessageId=periodMessageId;Record();DeclarationMessageClose(periodMessage).PerformClick();return;}
   declarationPeriodRejectedMessageId=periodMessageId;DeclarationTerminal(HtkkAutomationStage.DeclarationPeriodOriginalMessageRejected);return;}
  if(forms.Count!=1){SetStage(HtkkAutomationStage.DeclarationSheetWaiting);Record();return;}
  List<Control> grids=new List<Control>();visited=0;GatherSpreads(forms[0],grids,ref visited);if(grids.Count!=1){SetStage(HtkkAutomationStage.DeclarationSheetWaiting);Record();return;}
  Control grid=grids[0];declarationSheetObserved=true;declarationSheetCount=Convert.ToInt32(Get(Get(grid,"Sheets"),"Count"));
  if(declarationClock==null)declarationClock=Stopwatch.StartNew();
  object sheet=Get(grid,"ActiveSheet");bool ready=Convert.ToBoolean(Get(sheet,"AutoCalculation"))&&forms[0].Enabled&&grid.Enabled&&!OriginalMessageVisible();
  declarationIdentityMatched=DeclarationIdentity();declarationSourcePinsMatched=DeclarationPinsMatched();ObserveDeclarationPeriodShape();
  bool matched=ready&&declarationIdentityMatched&&declarationSourcePinsMatched&&declarationSheetCount>=1+(HtkkDeclarationCasePlans.ImportAddsAllAnnexes(declarationPlan)?0:declarationPlan.Annexes.Length)&&declarationSheetCount<=64;
  // Original load may pump a progress form while sheet binding is still in flight.
  if(!matched&&declarationClock.Elapsed.TotalSeconds<3){SetStage(HtkkAutomationStage.DeclarationSheetWaiting);Record();return;}
  if(!matched){DeclarationTerminal(HtkkAutomationStage.DeclarationSheetContractNotMatched);return;}
  SetStage(HtkkAutomationStage.DeclarationWebInputChecking);Record();VerifyDeclarationWebInput();
  // Native-case mode original-entry-export: no original import, the fixed entry plan is typed instead.
  declarationEntryPlan=DeclarationKhbsMode()?HtkkDeclarationCasePlans.KhbsEntry(declarationPlan.CaseId,declarationKhbsRound):HtkkDeclarationCasePlans.Entry(declarationPlan.CaseId);
  // Native-case mode web-xml-import-tick-reexport: the original import, then the fixed original edits and ticks.
  declarationTickPlan=DeclarationKhbsMode()?HtkkDeclarationCasePlans.KhbsImportTick(declarationPlan.CaseId):HtkkDeclarationCasePlans.ImportTick(declarationPlan.CaseId);if(declarationEntryPlan!=null&&declarationTickPlan!=null)throw new InvalidOperationException();
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
  for(int index=0;index<count;index++){object sheet=item.GetValue(sheets,new object[]{index});string sheetName=Convert.ToString(Get(sheet,"SheetName"),CultureInfo.InvariantCulture);if(sheetName==key||(name!=null&&sheetName==name)||(DeclarationKhbsMode()&&declarationKhbsRound>0&&key=="01"&&sheetName=="Tờ khai điều chỉnh")){if(found!=null)throw new InvalidOperationException();found=sheet;}}
  return found;
 }
 private bool InspectDeclarationGrid(){
  List<Control> grids=new List<Control>();int count=0;GatherSpreads(roundtripOwner,grids,ref count);if(grids.Count!=1)return false;
  if(!DeclarationIdentity())return false;
  declarationCellCheckCount=0;declarationCellMismatchMask=0;declarationCellLockedMask=0;declarationCellZeroMask=0;
  string[] checks=declarationPlan.CellChecks;
  for(int index=0;index<checks.Length;index++){
   string[] parts=checks[index].Split('|');int row,column;if(parts.Length!=3||!ParseA1(parts[1],out row,out column))throw new InvalidOperationException();
   declarationCellCheckCount++;object sheet=DeclarationSheet(grids[0],parts[0]);
   if(sheet==null||row>=Convert.ToInt32(Get(sheet,"RowCount"))||column>=Convert.ToInt32(Get(sheet,"ColumnCount"))){declarationCellMismatchMask|=1<<index;continue;}
   object cell=Cell(sheet,row,column);decimal actual,expected;
   // Original numeric cells hold double/decimal; the invariant round-trip text may use an exponent.
   // declarationCellZeroMask: the checked cell holds no value or a numeric 0 (tells a cleared cell from a different amount).
   object observed=Get(cell,"Value");decimal zero;if(observed==null||Convert.ToString(observed,CultureInfo.InvariantCulture).Trim().Length==0||(Decimal.TryParse(Convert.ToString(observed,CultureInfo.InvariantCulture),NumberStyles.Float,CultureInfo.InvariantCulture,out zero)&&zero==0m))declarationCellZeroMask|=1<<index;
   if(!Decimal.TryParse(Convert.ToString(Get(cell,"Value"),CultureInfo.InvariantCulture),NumberStyles.Float,CultureInfo.InvariantCulture,out actual)||!Decimal.TryParse(parts[2],NumberStyles.Number,CultureInfo.InvariantCulture,out expected)||actual!=expected)declarationCellMismatchMask|=1<<index;
   if(Convert.ToBoolean(Get(cell,"Locked")))declarationCellLockedMask|=1<<index;
  }
  bool matched=declarationCellMismatchMask==0&&declarationCellCheckCount==checks.Length;
  if(DeclarationAnnex12Case())InspectDeclarationAnnex12(grids[0]);
  return matched;
 }

 // ---- Z5 PL 01-2/GTGT after the original import: value-free diagnostic (run 46107139838) ----
 // 01GTGT-TT89-pl012-M10-2026 imported (roundtripImportSucceeded) with 01!P20, 01!U20 and 01_2!AJ7 empty or 0
 // (declarationCellZeroMask 70): HTKK left [13] T46 and [14] X46 at 0. Gtgt01TT89Nckt309.TinhLaiTongCot10_12_PL01_2 (5.8.4 = 5.8.5)
 // is the only writer of both: FinishImportXML, CellChange_1 on column T or U, UpdateFormula_1. It finds the two cells as the
 // StaticCells of SheetInfos[1] whose Path is PLuc_01_2_GTGT/ct13 and /ct14 and sums each table through
 // Header.StaticCells[0].CellTemplate.RowIndex (CalculateSumHeaderByGroup / CalculateSumByGroup skip a table without it).
 // Recorded, all without a value: which branch of frmWinToKhai.cmdImportXML_Click ran (TaiDuLieuRatLon), the shape of the
 // tables, whether each table header is the row the sums read, which plant/row cells are 0 or empty, whether the two total cells
 // are found, their formula dependants point at them and they equal the sums of the sheet. None of it decides the case.
 // Run 46112620593 (masks 45, 290, 63, 26113, 3987): ToKhaiInfo.TaiDuLieuRatLon not "1" (the WinDoWorkImportFormXml / frmToKhai_ReLoad
 // branch), two plants of two rows whose headers are the rows the sums read, AG on every row, X = ROUND(U x AO / 100) on every row,
 // ct13 / ct14 found below the rows and equal to the sums of the sheet, while 01_2!AJ7 and 01!P20 do not name them and read 0.
 // (A post-failure edit probe of that run, without the declarationEntryBusy guard, re-entered this phase through SendKeys'
 // message pumping and set plant 1's [10] to 0 before these masks were taken again; it is removed.)
 private int declarationAnnex12ImportPathMask=0,declarationAnnex12TableShape=0,declarationAnnex12HeaderMask=0,declarationAnnex12CellZeroMask=0,declarationAnnex12TotalMask=0;
 private bool DeclarationAnnex12Case(){
  if(declarationPlan==null||declarationPlan.MenuId!="Z5")return false;
  foreach(string pair in declarationPlan.SheetNames)if(pair.Split('|')[0]=="01_2")return true;
  return false;
 }
 private string DeclarationAnnex12Json(){
  string q=((char)34).ToString();StringBuilder json=new StringBuilder();
  string[] names=new string[]{"declarationAnnex12ImportPathMask","declarationAnnex12TableShape","declarationAnnex12HeaderMask","declarationAnnex12CellZeroMask","declarationAnnex12TotalMask"};
  int[] counts=new int[]{declarationAnnex12ImportPathMask,declarationAnnex12TableShape,declarationAnnex12HeaderMask,declarationAnnex12CellZeroMask,declarationAnnex12TotalMask};
  for(int index=0;index<names.Length;index++)json.Append(","+q+names[index]+q+":"+counts[index].ToString(CultureInfo.InvariantCulture));
  return json.ToString();
 }
 private static object Annex12Property(object target,string name){
  if(target==null)return null;PropertyInfo property=target.GetType().GetProperty(name,BindingFlags.Public|BindingFlags.Instance);
  return property==null?null:property.GetValue(target,null);
 }
 // A numeric cell as Decimal; false when empty or not a number. Zero: empty or 0.
 private static bool Annex12Number(object sheet,int row,int column,out decimal value){
  object raw=Get(Cell(sheet,row,column),"Value");value=0m;
  return raw!=null&&Decimal.TryParse(Convert.ToString(raw,CultureInfo.InvariantCulture),NumberStyles.Float,CultureInfo.InvariantCulture,out value);
 }
 private static bool Annex12Zero(object sheet,int row,int column){decimal value;return !Annex12Number(sheet,row,column,out value)||value==0m;}
 private static string Annex12A1(int row,int column){string letters=column<26?((char)('A'+column)).ToString():((char)('A'+column/26-1)).ToString()+((char)('A'+column%26)).ToString();return letters+(row+1).ToString(CultureInfo.InvariantCulture);}
 // Whether a formula addresses exactly the cell (sheet prefix and $ ignored): "T49", "01_2!X49:X49".
 private static bool Annex12FormulaNames(object cell,string a1){
  string formula=Convert.ToString(Annex12Property(cell,"Formula"),CultureInfo.InvariantCulture);if(String.IsNullOrEmpty(formula))return false;
  formula=formula.Replace("$",String.Empty).Replace(" ",String.Empty).ToUpperInvariant();
  foreach(string part in formula.Split(new char[]{'(',')',',','+','-','*','/','=','<','>'}))
   foreach(string piece in part.Split(':')){string name=piece.IndexOf('!')>=0?piece.Substring(piece.LastIndexOf('!')+1):piece;if(name==a1)return true;}
  return false;
 }
 // The 01_2 sheet info, its plant tables (PLuc_01_2_GTGT/TenNhaMay) and the static cells of ct13 / ct14.
 private bool DeclarationAnnex12Infos(out object info,out List<object> tables,out object ct13,out object ct14){
  info=null;tables=new List<object>();ct13=null;ct14=null;
  System.Collections.IList infos=Annex12Property(Global("ToKhaiInfo"),"SheetInfos") as System.Collections.IList;if(infos==null||infos.Count>32)return false;
  foreach(object candidate in infos)if(candidate!=null&&Convert.ToString(Annex12Property(candidate,"SheetID"),CultureInfo.InvariantCulture)=="01_2"){if(info!=null)return false;info=candidate;}
  if(info==null)return false;
  System.Collections.IList all=Annex12Property(info,"Tables") as System.Collections.IList;
  if(all!=null)foreach(object table in all)if(table!=null&&Convert.ToString(Annex12Property(table,"TablePath"),CultureInfo.InvariantCulture)=="PLuc_01_2_GTGT/TenNhaMay")tables.Add(table);
  System.Collections.IList statics=Annex12Property(info,"StaticCells") as System.Collections.IList;
  if(statics!=null)foreach(object cell in statics){string path=Convert.ToString(Annex12Property(cell,"Path"),CultureInfo.InvariantCulture);if(path=="PLuc_01_2_GTGT/ct13"&&ct13==null)ct13=cell;else if(path=="PLuc_01_2_GTGT/ct14"&&ct14==null)ct14=cell;}
  return true;
 }
 // CellTemplate of a cell info as a 0-based sheet position (HTKK subtracts 1 from RowIndex / ColIndex), or false.
 private static bool Annex12Position(object cellInfo,out int row,out int column){
  row=-1;column=-1;object template=Annex12Property(cellInfo,"CellTemplate");if(template==null)return false;
  row=Convert.ToInt32(Annex12Property(template,"RowIndex"))-1;column=Convert.ToInt32(Annex12Property(template,"ColIndex"))-1;return row>=0&&column>=0&&row<100000&&column<256;
 }
 private const int Annex12ColumnB=1,Annex12ColumnC=2,Annex12ColumnT=19,Annex12ColumnU=20,Annex12ColumnX=23,Annex12ColumnAG=32,Annex12ColumnAO=40;
 // declarationAnnex12ImportPathMask: 1 ToKhaiInfo read; 2 its TaiDuLieuRatLon is "1" (the WinDoWorkImportXmlToSheetInfos branch:
 //   FinishImportXML on the spread without frmToKhai_ReLoad); 4 its TaiDuLieuLon is "1"; 8 the 01_2 sheet info found; 16 its
 //   TaiDuLieuRatLon is "1"; 32 it is Active.
 // declarationAnnex12TableShape: bits 0-3 plant tables (capped 15); bits 4+3i..6+3i rows of table i < 4 (capped 7).
 // declarationAnnex12HeaderMask, 3 bits per table i < 4: 1 Header.StaticCells not empty; 2 its first cell's row is the plant row
 //   (DataLocationTemplateRowStart - 2, as the D1 driver locates it); 4 column B of that row reads the TableID.
 // declarationAnnex12CellZeroMask: bits 2i / 2i+1 the plant row's T ([10]) / U ([11]) of table i < 4 is 0 or empty; then 4 bits per
 //   row in document order (rows 0..3) from bit 8: U ([11]), X ([12]), AO (SetLaiDongCon copy of T), C (tenLoai) text empty.
 // declarationAnnex12TotalMask: 1 / 2 the ct13 / ct14 static cell found; 4 / 8 that cell is 0 or empty; 16 both lie below the last
 //   row; 32 01_2!AJ7 has a formula naming the ct13 cell; 64 01!P20 has a formula naming the ct14 cell; 128 every row has AG
 //   (maLoai); 256 the ct13 cell equals the sum of the plant T; 512 the ct14 cell equals the sum of the rows' X; 1024 every row's X
 //   equals ROUND(U x AO / 100, 0) half away from zero; 2048 the 01 sheet was found; 4096 a read failed.
 private void InspectDeclarationAnnex12(Control grid){
  int path=0,shape=0,header=0,zero=0,total=0;
  try{
   object toKhai=Global("ToKhaiInfo");
   if(toKhai!=null){path|=1;if(Convert.ToString(Annex12Property(toKhai,"TaiDuLieuRatLon"),CultureInfo.InvariantCulture)=="1")path|=2;if(Convert.ToString(Annex12Property(toKhai,"TaiDuLieuLon"),CultureInfo.InvariantCulture)=="1")path|=4;}
   object info;List<object> tables;object ct13,ct14;
   if(DeclarationAnnex12Infos(out info,out tables,out ct13,out ct14)){
    path|=8;if(Convert.ToString(Annex12Property(info,"TaiDuLieuRatLon"),CultureInfo.InvariantCulture)=="1")path|=16;if(Selected(Annex12Property(info,"Active")))path|=32;
    object sheet=DeclarationSheet(grid,"01_2"),main=DeclarationSheet(grid,"01");if(main!=null)total|=2048;
    shape=Math.Min(tables.Count,15);
    decimal sumT=0m,sumX=0m;int child=0,lastRow=-1;bool allAg=true,allRound=true;
    for(int i=0;i<tables.Count;i++){
     object table=tables[i];System.Collections.IList rows=Annex12Property(table,"RowsValues") as System.Collections.IList;int count=rows==null?0:rows.Count;
     if(i<4)shape|=Math.Min(count,7)<<(4+3*i);
     int start=Convert.ToInt32(Annex12Property(Annex12Property(table,"Location"),"DataLocationTemplateRowStart"))-1,parent=start-1;
     object head=Annex12Property(table,"Header");System.Collections.IList statics=Annex12Property(head,"StaticCells") as System.Collections.IList;
     int headRow,headColumn;
     if(i<4&&statics!=null&&statics.Count>0){header|=1<<(3*i);if(Annex12Position(statics[0],out headRow,out headColumn)&&headRow==parent)header|=2<<(3*i);}
     if(sheet==null||parent<0||start+count>Convert.ToInt32(Get(sheet,"RowCount")))continue;
     if(i<4&&CellText(sheet,parent,Annex12ColumnB)==Convert.ToString(Annex12Property(table,"TableID"),CultureInfo.InvariantCulture))header|=4<<(3*i);
     decimal t;if(Annex12Number(sheet,parent,Annex12ColumnT,out t))sumT+=t;
     if(i<4){if(Annex12Zero(sheet,parent,Annex12ColumnT))zero|=1<<(2*i);if(Annex12Zero(sheet,parent,Annex12ColumnU))zero|=2<<(2*i);}
     for(int j=0;j<count;j++,child++){
      int row=start+j;lastRow=row;decimal u,x,ao;bool hasU=Annex12Number(sheet,row,Annex12ColumnU,out u),hasX=Annex12Number(sheet,row,Annex12ColumnX,out x),hasAo=Annex12Number(sheet,row,Annex12ColumnAO,out ao);
      if(hasX)sumX+=x;
      if(!hasU||!hasX||!hasAo||x!=Math.Round(u*ao/100m,0,MidpointRounding.AwayFromZero))allRound=false;
      if(CellText(sheet,row,Annex12ColumnAG).Trim().Length==0)allAg=false;
      if(child<4){int bit=8+4*child;if(!hasU||u==0m)zero|=1<<bit;if(!hasX||x==0m)zero|=2<<bit;if(!hasAo||ao==0m)zero|=4<<bit;if(CellText(sheet,row,Annex12ColumnC).Trim().Length==0)zero|=8<<bit;}
     }
    }
    if(allAg&&child>0)total|=128;if(allRound&&child>0)total|=1024;
    int r13,c13,r14,c14;bool p13=ct13!=null&&Annex12Position(ct13,out r13,out c13),p14=ct14!=null&&Annex12Position(ct14,out r14,out c14);
    if(ct13!=null)total|=1;if(ct14!=null)total|=2;
    if(sheet!=null&&p13&&p14){
     Annex12Position(ct13,out r13,out c13);Annex12Position(ct14,out r14,out c14);
     decimal v13,v14;bool n13=Annex12Number(sheet,r13,c13,out v13),n14=Annex12Number(sheet,r14,c14,out v14);
     if(!n13||v13==0m)total|=4;if(!n14||v14==0m)total|=8;
     if(r13>lastRow&&r14>lastRow)total|=16;
     if(Annex12FormulaNames(Cell(sheet,6,35),Annex12A1(r13,c13)))total|=32;
     if(main!=null&&Annex12FormulaNames(Cell(main,19,15),Annex12A1(r14,c14)))total|=64;
     if(n13&&v13==sumT)total|=256;if(n14&&v14==sumX)total|=512;
    }
   }
  }catch(Exception){total|=4096;}
  declarationAnnex12ImportPathMask=path;declarationAnnex12TableShape=shape;declarationAnnex12HeaderMask=header;declarationAnnex12CellZeroMask=zero;declarationAnnex12TotalMask=total;Record();
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
  int leaves,mask;HtkkDeclarationTreeComparison.Diagnostics detail;declarationTreeMatched=HtkkDeclarationTreeComparison.Compare(input,output,declarationPlan.LeafCount-4,HtkkDeclarationCasePlans.ExportDatePaths(declarationPlan),out leaves,out mask,out detail);declarationTreeLeafCount=leaves;declarationTreeMismatchMask=mask;
  declarationTreeAttributeMask=detail.AttributeMask;declarationTreeTextMismatchCount=detail.TextMismatches;declarationTreeFirstMismatchOrdinal=Math.Min(detail.FirstOrdinal,65535);declarationTreeFirstMismatchKind=detail.FirstKind;
  declarationTreeMismatch1=detail.Codes[0];declarationTreeMismatch2=detail.Codes[1];declarationTreeMismatch3=detail.Codes[2];declarationTreeMismatch4=detail.Codes[3];declarationTreeFirstTextShape=detail.FirstTextShape;
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
 // ---- Original export invocation: observable readiness gate, one click per invocation, bounded diagnostics ----
 private Button DeclarationExportCommand(){
  Button command=Named(roundtripOwner,"cmdExport") as Button;if(command==null||command.FindForm()!=roundtripOwner||command.Text.Replace("&",String.Empty).Trim()!="Kết xuất")throw new InvalidOperationException();return command;
 }
 private static int VisibleFormCount(){int count=0;foreach(Form form in Application.OpenForms)if(form.Visible&&!form.IsDisposed&&count<64)count++;return count;}
 private bool OwnerOrParent(Form form){return form!=null&&(form==roundtripOwner||form==roundtripOwner.MdiParent);}
 // Readiness for an original "Kết xuất": the owner is ready, the original import click handler (if any) has
 // fully returned (its success message is closed inside it, so a click queued earlier could run re-entrantly
 // in a still-running import), the button itself can take a click (PerformClick silently drops a click when
 // CanSelect is false) and no selector is already up.
 private bool DeclarationExportGate(){
  bool owner=OriginalRoundtripOwnerReady();Control[] found=roundtripOwner.Controls.Find("cmdExport",true);if(found.Length!=1||!(found[0] is Button))throw new InvalidOperationException();
  // A transiently disabled/hidden button is waited for here; the invocation itself still requires DeclarationExportCommand().
  bool selectable=owner&&found[0].Visible&&found[0].Enabled&&found[0].CanSelect;
  declarationUiWaitMask=(declarationUiWaitMask&~(2|512))|(selectable?2:0)|(owner?512:0);
  bool ready=owner&&selectable&&(!roundtripImportCommandInvoked||declarationImportClickReturned)&&VisibleExportSelectors().Count==0;
  if(!ready)ObserveDeclarationUiWait(false);
  return ready;
 }
 private void InvokeDeclarationExport(Button command){
  declarationExportInvokeCount++;declarationExportClickReturned=false;declarationExportQuietClock=null;declarationExportFormsAtInvoke=VisibleFormCount();
  if(OwnerOrParent(Form.ActiveForm))declarationUiWaitMask|=128;
  List<Control> grids=new List<Control>();int visited=0;GatherSpreads(roundtripOwner,grids,ref visited);if(grids.Count==1&&Get(grids[0],"EditingControl")!=null)declarationUiWaitMask|=2048;
  ObserveDeclarationUiWait(true);
  // Observer only: records that the original Click event was raised; HTKK's own handler runs first.
  EventHandler observed=delegate(object sender,EventArgs args){declarationUiWaitMask|=1024;};
  roundtripOwner.BeginInvoke(new MethodInvoker(delegate{
   try{declarationUiWaitMask|=4;command.Click+=observed;try{command.PerformClick();}finally{command.Click-=observed;}declarationExportClickReturned=true;declarationUiWaitMask|=8;}
   catch(Exception error){Failure(error);}
  }));
 }
 private void ObserveDeclarationExportWithoutSelector(){
  bool native=ObserveDeclarationUiWait(false);
  if(!declarationExportClickReturned)return;
  // The click handler returned: a modal selector or message would still be open inside it. Wait a bounded
  // settle window with nothing new on screen before treating the click as not taken.
  bool quiet=!native&&VisibleFormCount()<=declarationExportFormsAtInvoke&&!OriginalMessageVisible();
  if(!quiet){declarationExportQuietClock=null;return;}
  if(declarationExportQuietClock==null){declarationExportQuietClock=Stopwatch.StartNew();return;}
  if(declarationExportQuietClock.Elapsed.TotalSeconds<DeclarationExportSettleSeconds)return;
  if((declarationUiWaitMask&16)==0){declarationUiWaitMask|=16;Record();}
  if(declarationExportInvokeCount==1){declarationPhase="export-reinvoke";SetStage(HtkkAutomationStage.DeclarationExportReadyWaiting);Record();}
 }
 // Updates the bounded wait fields; records at most once per elapsed second (or when forced).
 private bool ObserveDeclarationUiWait(bool force){
  int seconds=declarationExportClock==null?0:Math.Min(255,(int)declarationExportClock.Elapsed.TotalSeconds);
  if(!force&&seconds==declarationUiWaitSeconds)return (declarationUiWaitMask&256)!=0&&OwnNativeDialogVisible();
  declarationUiWaitSeconds=seconds;declarationUiVisibleForms=VisibleFormCount();declarationUiForegroundKind=ManagedForegroundKind();
  bool native=declarationPhase=="export-selector"&&OwnNativeDialogVisible();if(native)declarationUiWaitMask|=256;
  Record();return native;
 }
 private int ManagedForegroundKind(){
  int kind=NativeForegroundKind();if(kind!=6)return kind;
  Form form=Control.FromHandle(GetForegroundWindow()) as Form;if(form==null)return 6;
  if(OwnerOrParent(form))return 1;string type=form.GetType().FullName;
  return type=="HTKK.frmWinSelectExport"?2:type=="TAX.HTKK.Utilities.Control.frmMessage"?3:4;
 }
 // Thread-agnostic (also used from the Poll thread): native handles and class names only, no text.
 private static int NativeForegroundKind(){
  IntPtr window=GetForegroundWindow();if(window==IntPtr.Zero)return 8;uint process;GetWindowThreadProcessId(window,out process);
  if(process!=(uint)Process.GetCurrentProcess().Id)return 7;return NativeText(window,true)=="#32770"?5:6;
 }
 private static bool OwnNativeDialogVisible(){
  uint own=(uint)Process.GetCurrentProcess().Id;bool found=false;int visited=0;
  EnumWindows(delegate(IntPtr window,IntPtr parameter){if(++visited>1024)return false;uint process;GetWindowThreadProcessId(window,out process);if(process==own&&IsWindowVisible(window)&&NativeText(window,true)=="#32770"){found=true;return false;}return true;},IntPtr.Zero);
  return found;
 }
 // Poll-thread watchdog: the UI thread has not run a queued dispatch for `seconds`. Records only while it is
 // stalled (so no UI-thread mutation races the snapshot), at most once per 5 s of stall.
 internal void ObserveDeclarationUiStall(double seconds){
  // Also after the original import (import-inspect): Z5 PL 01-6 runs 45257929186, 45257934535 stalled there with the UI timer silent.
  if(!DeclarationMode()||finished||!(declarationPhase.StartsWith("export-",StringComparison.Ordinal)||declarationPhase=="import-inspect"))return;
  if(seconds<5){declarationStallRecordedSeconds=0;return;}
  int value=Math.Min(255,(int)seconds);if(value>declarationUiStallSeconds)declarationUiStallSeconds=value;declarationUiWaitMask|=64;
  if(value-declarationStallRecordedSeconds<5)return;declarationStallRecordedSeconds=value;
  declarationUiForegroundKind=NativeForegroundKind();try{Record();}catch{}
 }
 private void ContinueDeclarationFlow(){
  if(finished){exportWatcher.Stop();return;}if(exportFilenameEditing||declarationEntryBusy)return;
  if(!DeclarationMode()||declarationPlan==null||!webInputVerified||Hash(webInputPath)!=webImportInputSha256)throw new InvalidOperationException();
  Form message;string text;
  if(declarationPhase.StartsWith("khbs-",StringComparison.Ordinal)){ContinueDeclarationKhbs();return;}
  if(declarationPhase.StartsWith("entry-",StringComparison.Ordinal)){ContinueDeclarationEntry();return;}
  if(declarationPhase.StartsWith("tick-",StringComparison.Ordinal)){ContinueDeclarationTick();return;}
  if(declarationPhase=="import-ready"){
   if(!OriginalRoundtripOwnerReady())return;
   Button import=Named(roundtripOwner,"cmdImportXML") as Button;if(import==null||import.FindForm()!=roundtripOwner||import.Text.Replace("&",String.Empty).Trim()!="Nhập từ XML"||roundtripImportCommandInvoked)throw new InvalidOperationException();
   roundtripImportCommandInvoked=true;declarationPhase="import-result";SetStage(HtkkAutomationStage.DeclarationImportCommandInvoking);Record();
   roundtripOwner.BeginInvoke(new MethodInvoker(delegate{try{import.PerformClick();declarationImportClickReturned=true;declarationUiWaitMask|=1;}catch(Exception error){Failure(error);}}));return;
  }
  if(declarationPhase=="import-result"){
   if(DeclarationMessage(out message,out text)){
    if(text!="Nhập dữ liệu từ XML thành công."){importRejectedMessageId=OriginalMessageCatalogueId(text);DeclarationTerminal(HtkkAutomationStage.DeclarationImportOriginalMessageRejected);return;}
    FieldInfo loading=OriginalAssembly().GetType("HTKK.frmWinToKhai",true).GetField("FileNameLoading",BindingFlags.Static|BindingFlags.Public|BindingFlags.NonPublic);
    if(loading==null||loading.FieldType!=typeof(string))throw new InvalidOperationException();string actual=(string)loading.GetValue(null);
    roundtripImportPathMatched=!String.IsNullOrEmpty(actual)&&String.Equals(Path.GetFullPath(actual),Path.GetFullPath(DeclarationImportPath()),StringComparison.OrdinalIgnoreCase);
    if(!roundtripImportDialogMatched||!roundtripImportKeyboardCommitted||!roundtripImportDialogSubmitted||!roundtripImportPathMatched)throw new InvalidOperationException();
    roundtripImportSucceeded=true;
    if(declarationTickPlan!=null){declarationPhase="tick-pins";SetStage(HtkkAutomationStage.DeclarationImportTickReadyWaiting);}
    else{declarationPhase="import-inspect";declarationClock=Stopwatch.StartNew();SetStage(HtkkAutomationStage.DeclarationImportSheetChecking);}
    Record();DeclarationMessageClose(message).PerformClick();return;
   }
   if(!roundtripImportDialogSubmitted){SetStage(HtkkAutomationStage.GtgtImportFileDialogWaiting);TrySubmitOriginalFileDialog("Chọn tờ khai để tải vào chương trình",DeclarationImportPath(),true);}
   return;
  }
  if(declarationPhase=="import-inspect"){
   // An original message after the import (other than the success message being closed) is recorded and ends the run, and an
   // owner that stays unavailable for 20 s records the visible forms and the foreground kind (runs 45253348604 .. 45254460397,
   // Z5 PL 01-6: the phase never settled and the probe ended without either).
   if(DeclarationMessage(out message,out text)&&text!="Nhập dữ liệu từ XML thành công."){importRejectedMessageId=OriginalMessageCatalogueId(text);DeclarationTerminal(HtkkAutomationStage.DeclarationImportOriginalMessageRejected);return;}
   if(!OriginalRoundtripOwnerReady()){if(declarationClock.Elapsed.TotalSeconds>=20){declarationUiVisibleForms=VisibleFormCount();declarationUiForegroundKind=ManagedForegroundKind();DeclarationTerminal(HtkkAutomationStage.DeclarationImportSheetNotMatched);}return;}
   declarationImportSheetMatched=InspectDeclarationGrid();roundtripImportSheetMatched=declarationImportSheetMatched;Record();
   // Original recalculation after import may settle on a later UI turn; bounded wait.
   if(!declarationImportSheetMatched&&declarationClock.Elapsed.TotalSeconds<3)return;
   if(!declarationImportSheetMatched){DeclarationTerminal(HtkkAutomationStage.DeclarationImportSheetNotMatched);return;}
   if(DeclarationKhbsMode()){DeclarationKhbsInputDone();return;}
   declarationPhase="export-start";SetStage(HtkkAutomationStage.DeclarationExportReadyWaiting);Record();return;
  }
  if(declarationPhase=="export-start"){
   // Bounded by the probe deadline; the stage stays declaration-export-ready-waiting with the gate bits recorded.
   if(declarationExportClock==null)declarationExportClock=Stopwatch.StartNew();
   if(!DeclarationExportGate())return;
   string schema=Path.Combine(Path.GetDirectoryName(project),"InterfaceTemplates/"+declarationPlan.SchemaFile);string originalSchema=Convert.ToString(Get(Global("ToKhaiInfo"),"XsdFileName"),CultureInfo.InvariantCulture);
   exportSchemaPinnedVerified=!String.IsNullOrEmpty(originalSchema)&&String.Equals(Path.GetFullPath(originalSchema),Path.GetFullPath(schema),StringComparison.OrdinalIgnoreCase)&&Hash(schema)==declarationPlan.SchemaSha256&&Hash(Path.Combine(project,"TAX.HTKK.ComputeHash.dll"))=="d9d63921565ea2039109ad63d71977dcf56889cd83851977a0c712873ab687f5";
   if(!exportSchemaPinnedVerified){DeclarationTerminal(HtkkAutomationStage.DeclarationExportNotMatched);return;}
   string directory=Path.Combine(Path.Combine(Path.Combine(Path.GetDirectoryName(project),"DataFiles"),Mst),"reference-declaration-output");if(Directory.Exists(directory)||File.Exists(directory))throw new InvalidOperationException();Directory.CreateDirectory(directory);
   exportPath=Path.Combine(directory,"declaration.xml");exportDestinationFresh=!File.Exists(exportPath);
   Assembly utilities=null;foreach(Assembly loaded in AppDomain.CurrentDomain.GetAssemblies())if(loaded.GetName().Name=="TAX.HTKK.Utilities")utilities=loaded;if(utilities==null)throw new InvalidOperationException();
   Type configuration=utilities.GetType("TAX.HTKK.Utilities.Core.HTKKConfig",true);PropertyInfo temporary=configuration.GetProperty("PATH_TEMP",BindingFlags.Public|BindingFlags.Static);if(temporary==null)throw new InvalidOperationException();expectedSaveTitle="Tệp XML kết xuất tới thư mục "+Convert.ToString(temporary.GetValue(null,null),CultureInfo.InvariantCulture);
   Button command=DeclarationExportCommand();
   exportCommandInvoked=true;declarationPhase="export-selector";SetStage(HtkkAutomationStage.DeclarationExportCommandInvoking);
   InvokeDeclarationExport(command);return;
  }
  if(declarationPhase=="export-selector"||declarationPhase=="export-dialog"||declarationPhase=="export-reinvoke"){
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
    // An import-tick case additionally needs its pinned methods, every edit and every tick.
    if(declarationTickPlan!=null)matched=matched&&declarationImportSheetMatched&&DeclarationTickSucceeded();
    if(DeclarationKhbsMode()){DeclarationKhbsExported(matched);close.PerformClick();return;}
    DeclarationTerminal(matched?(declarationEntryPlan!=null?HtkkAutomationStage.DeclarationOriginalEntryExported:declarationTickPlan!=null?HtkkAutomationStage.DeclarationImportTickExported:HtkkAutomationStage.DeclarationWebImportInspected):HtkkAutomationStage.DeclarationExportNotMatched);close.PerformClick();return;
   }
   if(declarationPhase=="export-reinvoke"){
    // At most one more original click, only after the first click's handler fully returned and nothing at all
    // appeared for the settle window: no selector, message, save dialog or file can exist from the first one.
    if(declarationExportInvokeCount!=1||exportSelectorMatched||exportButtonInvoked||exportDialogMatched||exportDialogSubmitted||File.Exists(exportPath))throw new InvalidOperationException();
    if(!DeclarationExportGate())return;
    Button again=DeclarationExportCommand();declarationUiWaitMask|=32;declarationPhase="export-selector";SetStage(HtkkAutomationStage.DeclarationExportCommandInvoking);
    InvokeDeclarationExport(again);return;
   }
   if(declarationPhase=="export-selector"){
    List<Form> selectors=VisibleExportSelectors();if(selectors.Count==0){ObserveDeclarationExportWithoutSelector();return;}if(selectors.Count!=1)throw new InvalidOperationException();Form selector=selectors[0];
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
 public bool CanHandle(HtkkAutomationMode mode) { return mode == HtkkAutomationMode.DeclarationWebImportInspect || mode == HtkkAutomationMode.DeclarationAmendmentKhbsInspect; }
 public void Initialize(HtkkGuiReferenceAutomation harnessInstance, string projectDir, HtkkAutomationMode mode) {
  if(harnessInstance==null||!CanHandle(mode))throw new ArgumentException();
  harness = harnessInstance;
 }
 public void OnProfileSaved(Form profileOwner, Button closeButton, Control spread) { harness.OnDeclarationProfileSaved(profileOwner, closeButton, spread); }
 public void ContinueNavigation() { harness.ContinueDeclarationNavigation(); }
 public string BuildNavigationJson() { return harness.NavigationJson(); }
}
