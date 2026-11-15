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
   if(Annex16WebCase()&&!annex16HeadOfficeRestored){RestoreImportedAnnex16HeadOffices();return;}
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
 // 01-6/GTGT (CSSX, sheet 01_6) after the original "Nhập từ XML": the head tax office H (Controltype 8, path pathCucT,
 // SelectedValue T) has no XML leaf, so the import leaves it empty, and Header row 91 (TRIM(H22)="" -> 0, S = Y) makes the
 // original Kết xuất refuse with 0016, as R44 did for 01-2 (runs 42182681228/42182684607). Pick the fixed synthetic head
 // office of each row again through the original combo editor, as a user must; then, only if the original change handler
 // cleared it, the same managing office I (Controltype 9, code U). Codes are re-read, never written; the whole-tree XML
 // comparison stays exact. Bounded result: annex16HeadOfficeRepairCount (combo actions) and annex16HeadOfficeFailureMask
 // (0..4095): bits 0-4 H text, I text, U code, R province code, X ward code not as imported; bit 5 T code empty after the
 // pick (observed only, no leaf needs it); bits 6-8 row ordinal + 1; bit 9 H combo failed; bit 10 I combo failed; bit 11 I
 // had to be picked again; bits 12/13 the H/I list held the expected entry before the pick (0..16383).
 private bool annex16HeadOfficeRestored=false;private int annex16HeadOfficeRepairCount=0,annex16HeadOfficeFailureMask=0;
 private string Annex16Json(){string q=((char)34).ToString();return ","+q+"annex16HeadOfficeRepairCount"+q+":"+annex16HeadOfficeRepairCount.ToString(CultureInfo.InvariantCulture)+","+q+"annex16HeadOfficeFailureMask"+q+":"+annex16HeadOfficeFailureMask.ToString(CultureInfo.InvariantCulture);}
 // Rows of the fixed cases (htkk_web scripts/generate-htkk-web-annex16-cssx-reference.mjs): Hà Nội, Hải Phòng, Hà Nội.
 private static readonly string[][] Annex16ExpectedRows=new string[][]{
  new string[]{"Thuế Thành phố Hà Nội","Thuế cơ sở 16 Thành phố Hà Nội","10129","101","10129087"},
  new string[]{"Thuế Thành phố Hải Phòng","Thuế cơ sở 6 Thành phố Hải Phòng","10309","103","10309019"},
  new string[]{"Thuế Thành phố Hà Nội","Thuế cơ sở 16 Thành phố Hà Nội","10129","101","10129087"}};
 private const int Annex16ColumnH=7,Annex16ColumnI=8,Annex16ColumnK=10,Annex16ColumnR=17,Annex16ColumnT=19,Annex16ColumnU=20,Annex16ColumnX=23;
 private void RestoreImportedAnnex16HeadOffices(){
  if(!Annex16WebCase()||annex16HeadOfficeRestored||!roundtripImportSucceeded)throw new InvalidOperationException();
  List<Control> grids=new List<Control>();int visited=0;GatherSpreads(roundtripOwner,grids,ref visited);if(grids.Count!=1)throw new InvalidOperationException();Control grid=grids[0];
  object sheets=Get(grid,"Sheets");if(Convert.ToInt32(Get(sheets,"Count"))!=11)throw new InvalidOperationException();PropertyInfo item=sheets.GetType().GetProperty("Item",new Type[]{typeof(int)});if(item==null)throw new InvalidOperationException();
  object annex=null;int found=-1;
  for(int index=0;index<11;index++){object candidate=item.GetValue(sheets,new object[]{index});string name=Convert.ToString(Get(candidate,"SheetName"),CultureInfo.InvariantCulture);if(name=="01_6"||name=="01-6/GTGT (CSSX)"){if(annex!=null)throw new InvalidOperationException();annex=candidate;found=index;}}
  if(annex==null)throw new InvalidOperationException();
  annex12NonzeroBusy=true;exportWatcher.Stop();
  try{
   if(Get(grid,"ActiveSheet")!=annex){PropertyInfo active=grid.GetType().GetProperty("ActiveSheetIndex");if(active==null||!active.CanWrite)throw new InvalidOperationException();active.SetValue(grid,found,null);}
   if(Get(grid,"ActiveSheet")!=annex||OriginalMessageVisible())throw new InvalidOperationException();
   System.Collections.IList infos=Get(Global("ToKhaiInfo"),"SheetInfos") as System.Collections.IList;object info=null;if(infos==null||infos.Count>32)throw new InvalidOperationException();
   foreach(object candidate in infos)if(candidate!=null&&Convert.ToString(Get(candidate,"SheetID"),CultureInfo.InvariantCulture)=="01_6"){if(info!=null)throw new InvalidOperationException();info=candidate;}
   System.Collections.IList tables=info==null?null:Get(info,"Tables") as System.Collections.IList;if(tables==null||tables.Count!=2)throw new InvalidOperationException();
   System.Collections.IList rows=Get(tables[0],"RowsValues") as System.Collections.IList;if(rows==null||rows.Count!=Annex16ExpectedRows.Length)throw new InvalidOperationException();
   int start=Convert.ToInt32(Get(Get(tables[0],"Location"),"DataLocationTemplateRowStart"))-1;if(start!=21)throw new InvalidOperationException();
   for(int ordinal=0;ordinal<rows.Count;ordinal++){
    int row=start+ordinal;string[] expected=Annex16ExpectedRows[ordinal];
    annex16HeadOfficeFailureMask=(annex16HeadOfficeFailureMask&(2048|4096|8192))|((ordinal+1)<<6);Record();
    // Runs 43683942253/43683944987 (both cases, mask 2688 = 2048|512|row 2): row 1 passed, the H combo of row 2 failed. The
    // combo lists of H (Controltype 8, loadCqtCapCucTheoDiaBanXa by the row's ward) and I (Controltype 9, by T) are
    // installed by frmWinToKhai.winFpSpread_EnterCell, which the vendor raises for a user's move into the cell, not for
    // SetActiveCell (01-2 release 216): row 2 still had row 1's Hà Nội list. Enter H with one real Left key from I and
    // I with one real Right key from H, as a user does, before each pick. Bits 12/13: the H/I list held the expected
    // entry when the pick was attempted.
    if(CellText(annex,row,Annex16ColumnH)!=expected[0]){
     EnterImportedAnnex16CellByKey(grid,annex,row,Annex16ColumnH);
     if(Annex16ComboHasEntry(annex,row,Annex16ColumnH,expected[0]))annex16HeadOfficeFailureMask|=4096;
     try{SelectImportedAnnex16Combo(grid,annex,row,Annex16ColumnH,expected[0]);}catch{annex16HeadOfficeFailureMask|=512;Record();throw;}
     annex16HeadOfficeRepairCount++;Record();
    }
    // The original handlers may act when the user leaves a cell (01-2 runs 42206910531/42206915586): move to I first.
    EnterImportedAnnex16CellByKey(grid,annex,row,Annex16ColumnI);
    if(CellText(annex,row,Annex16ColumnI)!=expected[1]){
     if(Annex16ComboHasEntry(annex,row,Annex16ColumnI,expected[1]))annex16HeadOfficeFailureMask|=8192;
     annex16HeadOfficeFailureMask|=2048;
     try{SelectImportedAnnex16Combo(grid,annex,row,Annex16ColumnI,expected[1]);}catch{annex16HeadOfficeFailureMask|=1024;Record();throw;}
     annex16HeadOfficeRepairCount++;Record();
    }
    MoveImportedAnnex16Cell(grid,annex,row,Annex16ColumnK);
    int unmet=WaitImportedAnnex16HeadOffice(annex,row,expected,2.0);
    if(CellText(annex,row,Annex16ColumnT)==String.Empty)annex16HeadOfficeFailureMask|=32;
    if(unmet!=0){annex16HeadOfficeFailureMask|=unmet;Record();throw new InvalidOperationException();}
   }
   if(annex16HeadOfficeRepairCount<1||annex16HeadOfficeRepairCount>2*rows.Count)throw new InvalidOperationException();
   annex16HeadOfficeFailureMask&=2048|32|4096|8192;annex16HeadOfficeRestored=true;Record();
  }finally{annex12NonzeroBusy=false;if(!finished)exportWatcher.Start();}
 }
 private int ImportedAnnex16HeadOfficeUnmet(object annex,int row,string[] expected){
  int unmet=0;
  if(CellText(annex,row,Annex16ColumnH)!=expected[0])unmet|=1;
  if(CellText(annex,row,Annex16ColumnI)!=expected[1])unmet|=2;
  if(CellText(annex,row,Annex16ColumnU)!=expected[2])unmet|=4;
  if(CellText(annex,row,Annex16ColumnR)!=expected[3])unmet|=8;
  if(CellText(annex,row,Annex16ColumnX)!=expected[4])unmet|=16;
  return unmet;
 }
 private int WaitImportedAnnex16HeadOffice(object annex,int row,string[] expected,double seconds){
  System.Diagnostics.Stopwatch clock=System.Diagnostics.Stopwatch.StartNew();int unmet;
  do{unmet=ImportedAnnex16HeadOfficeUnmet(annex,row,expected);if(unmet==0||OriginalMessageVisible())return unmet;Application.DoEvents();System.Threading.Thread.Sleep(10);}while(clock.Elapsed.TotalSeconds<seconds);
  return ImportedAnnex16HeadOfficeUnmet(annex,row,expected);
 }
 // The same public vendor combo selection as the proven 01-2 restore (SelectImportedAnnex12Combo), for H and I of 01-6.
 private void SelectImportedAnnex16Combo(Control grid,object annex,int row,int column,string value){
  Form owner=grid.FindForm();uint pid;
  if((column!=Annex16ColumnH&&column!=Annex16ColumnI)||owner==null||owner!=roundtripOwner||!owner.Visible||!owner.Enabled||!grid.Visible||!grid.Enabled||Get(grid,"ActiveSheet")!=annex||OriginalMessageVisible()||Annex12CellLocked(annex,row,column))throw new InvalidOperationException();
  grid.Focus();GetWindowThreadProcessId(GetForegroundWindow(),out pid);if(pid!=(uint)System.Diagnostics.Process.GetCurrentProcess().Id||!grid.ContainsFocus)throw new InvalidOperationException();
  annex.GetType().GetMethod("SetActiveCell",new Type[]{typeof(int),typeof(int)}).Invoke(annex,new object[]{row,column});
  grid.GetType().GetMethod("StartCellEditing",new Type[]{typeof(EventArgs),typeof(bool)}).Invoke(grid,new object[]{EventArgs.Empty,false});
  Control editor=Get(grid,"EditingControl") as Control;if(editor==null||!editor.Visible||!editor.Enabled)throw new InvalidOperationException();
  Control vendor=FindVendorCombo(editor,0);if(vendor==null)throw new InvalidOperationException();editorKind="combo";SetPublic(vendor,"DroppedDown",true);
  object list=Get(vendor,"List");System.Collections.IList sequence=list as System.Collections.IList;int count=sequence!=null?sequence.Count:Convert.ToInt32(Get(list,"Count"));
  if(count<1||count>4096)throw new InvalidOperationException();PropertyInfo entryItem=list.GetType().GetProperty("Item",new Type[]{typeof(int)});if(entryItem==null&&sequence==null)throw new InvalidOperationException();int selected=-1;
  for(int offset=0;offset<count;offset++){object entry=sequence!=null?sequence[offset]:entryItem.GetValue(list,new object[]{offset});if(entry!=null&&entry.ToString()==value){if(selected>=0)throw new InvalidOperationException();selected=offset;}}
  if(selected<0)throw new InvalidOperationException();GetWindowThreadProcessId(GetForegroundWindow(),out pid);if(pid!=(uint)System.Diagnostics.Process.GetCurrentProcess().Id||OriginalMessageVisible())throw new InvalidOperationException();
  SetPublic(vendor,"SelectedIndex",selected);SetPublic(vendor,"DroppedDown",false);
  grid.GetType().GetMethod("StopCellEditing",Type.EmptyTypes).Invoke(grid,null);Application.DoEvents();grid.Focus();
  if(CellText(annex,row,column)!=value||OriginalMessageVisible()||Get(grid,"ActiveSheet")!=annex)throw new InvalidOperationException();
 }
 // One real arrow key between H and I (not editing): the vendor raises EnterCell and the original handler rebuilds the
 // entered cell's list; nothing is typed or written.
 private void EnterImportedAnnex16CellByKey(Control grid,object annex,int row,int column){
  int from=column==Annex16ColumnH?Annex16ColumnI:Annex16ColumnH;if(column!=Annex16ColumnH&&column!=Annex16ColumnI)throw new InvalidOperationException();
  if(from==Annex16ColumnI)MoveImportedAnnex16Cell(grid,annex,row,Annex16ColumnI);
  else if(Convert.ToInt32(Get(annex,"ActiveRowIndex"))!=row||Convert.ToInt32(Get(annex,"ActiveColumnIndex"))!=Annex16ColumnH)MoveImportedAnnex16Cell(grid,annex,row,Annex16ColumnH);
  Form owner=grid.FindForm();uint pid;
  if(owner==null||owner!=roundtripOwner||Get(grid,"EditingControl")!=null||Annex12CellLocked(annex,row,column))throw new InvalidOperationException();
  grid.Focus();GetWindowThreadProcessId(GetForegroundWindow(),out pid);if(pid!=(uint)System.Diagnostics.Process.GetCurrentProcess().Id||!grid.ContainsFocus||OriginalMessageVisible())throw new InvalidOperationException();
  string before=CellText(annex,row,column);SendKeys.SendWait(column==Annex16ColumnH?"{LEFT}":"{RIGHT}");Application.DoEvents();grid.Focus();
  if(Convert.ToInt32(Get(annex,"ActiveRowIndex"))!=row||Convert.ToInt32(Get(annex,"ActiveColumnIndex"))!=column||CellText(annex,row,column)!=before||OriginalMessageVisible()||Get(grid,"ActiveSheet")!=annex)throw new InvalidOperationException();
 }
 // Read-only: whether the cell's original combo type lists the entry once.
 private bool Annex16ComboHasEntry(object annex,int row,int column,string value){
  object type=Get(Cell(annex,row,column),"CellType");string[] items=type==null?null:Get(type,"Items") as string[];
  return items!=null&&items.Length<=4096&&Array.IndexOf(items,value)>=0&&Array.IndexOf(items,value)==Array.LastIndexOf(items,value);
 }
 // Navigation only: the original active cell moves as with the keyboard; nothing is written.
 private void MoveImportedAnnex16Cell(Control grid,object annex,int row,int column){
  Form owner=grid.FindForm();uint pid;
  if((column!=Annex16ColumnH&&column!=Annex16ColumnI&&column!=Annex16ColumnK)||owner==null||owner!=roundtripOwner||!owner.Visible||!owner.Enabled||!grid.Visible||!grid.Enabled||Get(grid,"ActiveSheet")!=annex||OriginalMessageVisible()||Annex12CellLocked(annex,row,column))throw new InvalidOperationException();
  grid.Focus();GetWindowThreadProcessId(GetForegroundWindow(),out pid);if(pid!=(uint)System.Diagnostics.Process.GetCurrentProcess().Id||!grid.ContainsFocus)throw new InvalidOperationException();
  annex.GetType().GetMethod("SetActiveCell",new Type[]{typeof(int),typeof(int)}).Invoke(annex,new object[]{row,column});Application.DoEvents();grid.Focus();
  if(Convert.ToInt32(Get(annex,"ActiveRowIndex"))!=row||Convert.ToInt32(Get(annex,"ActiveColumnIndex"))!=column||OriginalMessageVisible()||Get(grid,"ActiveSheet")!=annex)throw new InvalidOperationException();
 }
 private static XmlDocument ReadBoundedOriginalXml(string path){
  FileInfo file=new FileInfo(path);if(!file.Exists||(file.Attributes&FileAttributes.ReparsePoint)!=0||file.Length<1||file.Length>262144)throw new InvalidOperationException();
  XmlReaderSettings settings=new XmlReaderSettings();settings.ProhibitDtd=true;settings.XmlResolver=null;XmlDocument document=new XmlDocument();document.XmlResolver=null;using(XmlReader reader=XmlReader.Create(path,settings))document.Load(reader);
  if(document.DocumentElement==null||document.DocumentElement.LocalName!="HSoThueDTu"||document.DocumentElement.NamespaceURI!="http://kekhaithue.gdt.gov.vn/TKhaiThue")throw new InvalidOperationException();return document;
 }
}
