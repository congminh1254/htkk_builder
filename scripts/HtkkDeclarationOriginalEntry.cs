// Native-case mode original-entry-export of the declaration driver (C# 2.0 / CLR2).
// Used when the original "Nhập từ XML" cannot keep a form's data (Y8: AutoBindData_0 -> LockUnlock
// resets the three tables, release 238). After the shared menu/period/sheet steps the driver
// types the FIXED values of HtkkDeclarationCasePlans.Entry into HTKK's own grid: the part choice
// through the original checkbox (SPACE -> ButtonClicked -> ButtonClick_0), rows through the real
// F5 key (frmWinToKhai.ProcessCmdKey), every value through the original cell editor ("^a", value,
// "{TAB}"), the catalogue cell through the original drop-down by keyboard. Computed cells are only
// READ. Then the shared original export, pinned XSD and whole-tree comparison run unchanged.
// Never: Cell.Value/Text assignment, combo SelectedIndex assignment, business helper calls,
// authored totals, binary patches. Diagnostics are flags, counts, masks and codes, never values.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using System.Windows.Forms;

public sealed partial class HtkkGuiReferenceAutomation {
 private HtkkDeclarationEntryPlan declarationEntryPlan=null;
 private bool declarationEntryBusy=false;
 private Stopwatch declarationEntryClock=null;
 private bool declarationEntryMethodPinsMatched=false,declarationEntryCatalogueMatched=false,declarationEntryChoiceMatched=false,declarationEntryLocksMatched=false,declarationEntryRowsMatched=false,declarationEntryValuesMatched=false,declarationEntrySignerMatched=false,declarationEntrySigningDateLocked=false,declarationEntrySheetMatched=false;
 private int declarationEntryPlannedCount=0,declarationEntryActionCount=0,declarationEntryFailureCode=0,declarationEntryMethodPinMask=0,declarationEntryLockBeforeMask=0,declarationEntryLockAfterMask=0,declarationEntryLockFinalMask=0;
 private int declarationEntryRowsBefore=0,declarationEntryRowsAfter=0,declarationEntryRowInsertCount=0,declarationEntryMismatchMask=0,declarationEntryLockedMask=0,declarationEntryCellTypeMismatchMask=0,declarationEntryCombo1Mask=0,declarationEntryCombo2Mask=0,declarationEntryDateTextMask=0;
 private int declarationEntryComboCount=0;

 // Failure codes (declarationEntryFailureCode), value-free:
 //  1 method pin   2 catalogue pin   3 choice cell not an open unticked checkbox   4 choice not applied
 //  5 lock pattern after the choice   6 table metadata   7 rows/F5   8 entry cell locked
 //  9 entry cell type   10 foreground/focus guard   11 editor   12 typed text not in editor
 //  13 read-back   14 combo list   15 combo keyboard selection   16 combo code (CellChange)
 //  17 original message   18 active cell/editor lost during combo keys   20 computed cells / final locks
 private string DeclarationEntryJson(){
  string q=((char)34).ToString();StringBuilder json=new StringBuilder();
  string[] names=new string[]{"declarationEntryMethodPinsMatched","declarationEntryCatalogueMatched","declarationEntryChoiceMatched","declarationEntryLocksMatched","declarationEntryRowsMatched","declarationEntryValuesMatched","declarationEntrySignerMatched","declarationEntrySigningDateLocked","declarationEntrySheetMatched"};
  bool[] values=new bool[]{declarationEntryMethodPinsMatched,declarationEntryCatalogueMatched,declarationEntryChoiceMatched,declarationEntryLocksMatched,declarationEntryRowsMatched,declarationEntryValuesMatched,declarationEntrySignerMatched,declarationEntrySigningDateLocked,declarationEntrySheetMatched};
  for(int index=0;index<names.Length;index++)json.Append(","+q+names[index]+q+":"+Bool(values[index]));
  names=new string[]{"declarationEntryPlannedCount","declarationEntryActionCount","declarationEntryFailureCode","declarationEntryMethodPinMask","declarationEntryLockBeforeMask","declarationEntryLockAfterMask","declarationEntryLockFinalMask","declarationEntryRowsBefore","declarationEntryRowsAfter","declarationEntryRowInsertCount","declarationEntryMismatchMask","declarationEntryLockedMask","declarationEntryCellTypeMismatchMask","declarationEntryCombo1Mask","declarationEntryCombo2Mask","declarationEntryDateTextMask"};
  int[] counts=new int[]{declarationEntryPlannedCount,declarationEntryActionCount,declarationEntryFailureCode,declarationEntryMethodPinMask,declarationEntryLockBeforeMask,declarationEntryLockAfterMask,declarationEntryLockFinalMask,declarationEntryRowsBefore,declarationEntryRowsAfter,declarationEntryRowInsertCount,declarationEntryMismatchMask,declarationEntryLockedMask,declarationEntryCellTypeMismatchMask,declarationEntryCombo1Mask,declarationEntryCombo2Mask,declarationEntryDateTextMask};
  for(int index=0;index<names.Length;index++)json.Append(","+q+names[index]+q+":"+counts[index].ToString(CultureInfo.InvariantCulture));
  return json.ToString();
 }
 private bool DeclarationEntryCase(){return declarationPlan!=null&&HtkkDeclarationCasePlans.Entry(declarationPlan.CaseId)!=null;}
 private void DeclarationEntryFail(int code){if(declarationEntryFailureCode==0)declarationEntryFailureCode=code;DeclarationTerminal(HtkkAutomationStage.DeclarationEntryNotMatched);}

 // ---- Owner, grid and table observation (read only) ----
 private object DeclarationEntrySheet(out Control grid){
  List<Control> grids=new List<Control>();int visited=0;GatherSpreads(roundtripOwner,grids,ref visited);if(grids.Count!=1)throw new InvalidOperationException();
  grid=grids[0];object sheet=DeclarationSheet(grid,"01");if(sheet==null||Get(grid,"ActiveSheet")!=sheet||Convert.ToInt32(Get(grid,"ActiveSheetIndex"))!=0)throw new InvalidOperationException();
  object business=Global("InstanceClass");if(business==null||business.GetType().FullName!="TAX.HTKK.Business."+declarationPlan.BusinessClass||!Convert.ToBoolean(Get(sheet,"AutoCalculation")))throw new InvalidOperationException();
  return sheet;
 }
 private bool DeclarationEntryGuard(Control grid){
  Form owner=grid.FindForm();uint pid;GetWindowThreadProcessId(GetForegroundWindow(),out pid);
  return owner==roundtripOwner&&owner.GetType().FullName=="HTKK.frmWinToKhai"&&owner.Visible&&owner.Enabled&&grid.Visible&&grid.Enabled&&grid.ContainsFocus&&pid==(uint)Process.GetCurrentProcess().Id&&!OriginalMessageVisible();
 }
 private static int[] DeclarationEntryCell(string a1){int row,column;if(!ParseA1(a1,out row,out column))throw new InvalidOperationException();return new int[]{row,column};}
 private System.Collections.IList DeclarationEntryTables(){
  System.Collections.IList infos=Get(Global("ToKhaiInfo"),"SheetInfos") as System.Collections.IList;if(infos==null||infos.Count<1||infos.Count>32)throw new InvalidOperationException();
  System.Collections.IList tables=Get(infos[0],"Tables") as System.Collections.IList;if(tables==null||tables.Count!=declarationEntryPlan.Tables.Length)return null;
  for(int index=0;index<tables.Count;index++)if(Convert.ToString(Get(tables[index],"TableName"),CultureInfo.InvariantCulture)!=declarationEntryPlan.Tables[index].Split('|')[0])return null;
  return tables;
 }
 private static int DeclarationEntryRowCount(object table){System.Collections.IList rows=Get(table,"RowsValues") as System.Collections.IList;if(rows==null||rows.Count>64)throw new InvalidOperationException();return rows.Count;}
 private static int DeclarationEntryStart(object table){return Convert.ToInt32(Get(Get(table,"Location"),"DataLocationTemplateRowStart"));}
 // Per table t: bit t = every getCols cell of every row locked; bit 4+t = mixed.
 private int DeclarationEntryLockMask(object sheet){
  System.Collections.IList tables=DeclarationEntryTables();if(tables==null)return 0xFF00;int mask=0;
  for(int t=0;t<tables.Count;t++){
   int start=DeclarationEntryStart(tables[t])-1,rows=DeclarationEntryRowCount(tables[t]),locked=0,open=0;
   for(int r=0;r<rows;r++)foreach(string letters in declarationEntryPlan.LockColumns){int[] cell=DeclarationEntryCell(letters+(start+r+1).ToString(CultureInfo.InvariantCulture));if(Convert.ToBoolean(Get(Cell(sheet,cell[0],cell[1]),"Locked")))locked++;else open++;}
   if(open==0&&locked>0)mask|=1<<t;else if(locked>0)mask|=1<<(4+t);
  }
  return mask;
 }
 private int DeclarationEntryExpectedLocks(){int mask=0;for(int t=0;t<declarationEntryPlan.Tables.Length;t++)if(declarationEntryPlan.Tables[t].Split('|')[3]=="1")mask|=1<<t;return mask;}
 private static void DeclarationEntrySelect(Control grid,object sheet,int row,int column){
  grid.Focus();sheet.GetType().GetMethod("SetActiveCell",new Type[]{typeof(int),typeof(int)}).Invoke(sheet,new object[]{row,column});
  MethodInfo show=grid.GetType().GetMethod("ShowActiveCell",BindingFlags.Public|BindingFlags.Instance);if(show==null)throw new InvalidOperationException();ParameterInfo[] parameters=show.GetParameters();
  if(parameters.Length!=2||parameters[0].ParameterType.FullName!="FarPoint.Win.Spread.VerticalPosition"||parameters[1].ParameterType.FullName!="FarPoint.Win.Spread.HorizontalPosition")throw new InvalidOperationException();
  show.Invoke(grid,new object[]{Enum.Parse(parameters[0].ParameterType,"Center"),Enum.Parse(parameters[1].ParameterType,"Center")});Application.DoEvents();
 }
 private static bool DeclarationEntryActive(object sheet,int row,int column){return Convert.ToInt32(Get(sheet,"ActiveRowIndex"))==row&&Convert.ToInt32(Get(sheet,"ActiveColumnIndex"))==column;}
 private static string DeclarationEntryCellKind(object cell){object type=Get(cell,"CellType");return type==null?String.Empty:type.GetType().FullName;}

 // ---- Step 1: method-body and catalogue pins (read-only reflection over the loaded originals) ----
 private static string DeclarationEntrySha256(byte[] bytes){using(SHA256 hash=SHA256.Create()){StringBuilder value=new StringBuilder();foreach(byte b in hash.ComputeHash(bytes))value.Append(b.ToString("x2",CultureInfo.InvariantCulture));return value.ToString();}}
 // Bit i = pin i (asm|type|method|token|IL bytes|IL-code SHA-256) does not resolve to the reviewed loaded body.
 private static int DeclarationMethodPinMask(string[] pins){
  object business=Global("InstanceClass");if(business==null)throw new InvalidOperationException();
  Assembly businessAssembly=business.GetType().Assembly,exe=OriginalAssembly();int mask=0;
  for(int index=0;index<pins.Length;index++){
   string[] pin=pins[index].Split('|');bool matched=false;
   try{
    Module module=(pin[0]=="B"?businessAssembly:exe).ManifestModule;MethodBase method=module.ResolveMethod(Int32.Parse(pin[3].Substring(2),NumberStyles.HexNumber,CultureInfo.InvariantCulture));
    MethodBody body=method==null?null:method.GetMethodBody();byte[] il=body==null?null:body.GetILAsByteArray();
    matched=method!=null&&method.Name==pin[2]&&method.DeclaringType!=null&&method.DeclaringType.Name==pin[1]&&il!=null&&il.Length.ToString(CultureInfo.InvariantCulture)==pin[4]&&DeclarationEntrySha256(il)==pin[5];
   }catch(ArgumentException){matched=false;}
   if(!matched)mask|=1<<index;
  }
  return mask;
 }
 private void VerifyDeclarationEntryPins(){
  SetStage(HtkkAutomationStage.DeclarationEntryPinsChecking);declarationEntryPlannedCount=declarationEntryPlan.Entries.Length;Record();
  declarationEntryMethodPinMask=DeclarationMethodPinMask(declarationEntryPlan.MethodPins);
  declarationEntryMethodPinsMatched=declarationEntryMethodPinMask==0;
  declarationEntryCatalogueMatched=Hash(Path.Combine(Path.GetDirectoryName(project),declarationEntryPlan.CatalogueFile))==declarationEntryPlan.CatalogueSha256;Record();
  if(!declarationEntryMethodPinsMatched){DeclarationEntryFail(1);return;}
  if(!declarationEntryCatalogueMatched){DeclarationEntryFail(2);return;}
 }

 // ---- Step 2: part choice through the original checkbox, BEFORE any row value ----
 private void ChooseDeclarationEntryPart(){
  Control grid;object sheet=DeclarationEntrySheet(out grid);SetStage(HtkkAutomationStage.DeclarationEntryChoiceInvoking);Record();
  int[] choice=DeclarationEntryCell(declarationEntryPlan.ChoiceCell),exclusive=DeclarationEntryCell(declarationEntryPlan.ExclusiveCell);
  object cell=Cell(sheet,choice[0],choice[1]);
  if(DeclarationEntryCellKind(cell)!="FarPoint.Win.Spread.CellType.CheckBoxCellType"||DeclarationEntryCellKind(Cell(sheet,exclusive[0],exclusive[1]))!="FarPoint.Win.Spread.CellType.CheckBoxCellType"||Convert.ToBoolean(Get(cell,"Locked"))||Selected(Get(cell,"Value"))||!RowVisible(sheet,choice[0])){DeclarationEntryFail(3);return;}
  if(DeclarationEntryTables()==null){DeclarationEntryFail(6);return;}
  declarationEntryLockBeforeMask=DeclarationEntryLockMask(sheet);
  DeclarationEntrySelect(grid,sheet,choice[0],choice[1]);
  if(!DeclarationEntryActive(sheet,choice[0],choice[1])||!DeclarationEntryGuard(grid)){DeclarationEntryFail(10);return;}
  // SPACE on the active checkbox raises FpSpread.ButtonClicked -> frmWinToKhai.winFpSpread_ButtonClicked
  // -> WinDoWorkEvent.ButtonClick -> Ntnn01TT89Nckt309.ButtonClick_0(idxRow 7, idxCol 12).
  SendKeys.SendWait(" ");int expected=DeclarationEntryExpectedLocks();Stopwatch clock=Stopwatch.StartNew();
  do{
   if(OriginalMessageVisible()){DeclarationEntryFail(17);return;}
   declarationEntryChoiceMatched=Selected(Get(Cell(sheet,choice[0],choice[1]),"Value"))&&!Selected(Get(Cell(sheet,exclusive[0],exclusive[1]),"Value"));
   declarationEntryLockAfterMask=DeclarationEntryLockMask(sheet);declarationEntryLocksMatched=declarationEntryLockAfterMask==expected;
   if(declarationEntryChoiceMatched&&declarationEntryLocksMatched)break;
   Application.DoEvents();System.Threading.Thread.Sleep(10);
  }while(clock.Elapsed.TotalSeconds<3);
  Record();
  if(!declarationEntryChoiceMatched){DeclarationEntryFail(4);return;}
  if(!declarationEntryLocksMatched){DeclarationEntryFail(5);return;}
 }

 // ---- Step 3: rows through the real F5 key (ProcessCmdKey), at most four, one per UI turn ----
 private static int DeclarationEntryEncodeRows(System.Collections.IList tables){int value=0;for(int t=0;t<tables.Count&&t<4;t++)value|=Math.Min(DeclarationEntryRowCount(tables[t]),15)<<(4*t);return value;}
 private bool InsertDeclarationEntryRows(){
  Control grid;object sheet=DeclarationEntrySheet(out grid);SetStage(HtkkAutomationStage.DeclarationEntryRowsInserting);
  System.Collections.IList tables=DeclarationEntryTables();if(tables==null){DeclarationEntryFail(6);return false;}
  if(declarationEntryRowInsertCount==0)declarationEntryRowsBefore=DeclarationEntryEncodeRows(tables);Record();
  for(int t=0;t<tables.Count;t++){
   int required=Int32.Parse(declarationEntryPlan.Tables[t].Split('|')[2],CultureInfo.InvariantCulture),count=DeclarationEntryRowCount(tables[t]);
   if(count>required||count<1){DeclarationEntryFail(7);return false;}
   if(count==required)continue;
   if(declarationEntryRowInsertCount>=4){DeclarationEntryFail(7);return false;}
   int row=DeclarationEntryStart(tables[t])-1+count-1;int[] first=DeclarationEntryCell(declarationEntryPlan.LockColumns[0]+(row+1).ToString(CultureInfo.InvariantCulture));
   if(Convert.ToBoolean(Get(Cell(sheet,first[0],first[1]),"Locked"))){DeclarationEntryFail(7);return false;}
   DeclarationEntrySelect(grid,sheet,first[0],first[1]);Control[] panel=roundtripOwner.Controls.Find("pnF5",true);
   if(panel.Length!=1||!panel[0].Visible||!panel[0].Enabled||!DeclarationEntryActive(sheet,first[0],first[1])||!DeclarationEntryGuard(grid)){DeclarationEntryFail(10);return false;}
   // REAL F5 through frmWinToKhai.ProcessCmdKey; never a direct row insert or a row/DTO write.
   declarationEntryRowInsertCount++;Record();SendKeys.SendWait("{F5}");Stopwatch clock=Stopwatch.StartNew();
   while(DeclarationEntryRowCount(tables[t])!=count+1&&clock.Elapsed.TotalSeconds<2){if(OriginalMessageVisible()){DeclarationEntryFail(17);return false;}Application.DoEvents();System.Threading.Thread.Sleep(10);}
   if(DeclarationEntryRowCount(tables[t])!=count+1){DeclarationEntryFail(7);return false;}
   return false;
  }
  for(int t=0;t<tables.Count;t++)if(DeclarationEntryStart(tables[t])!=Int32.Parse(declarationEntryPlan.Tables[t].Split('|')[1],CultureInfo.InvariantCulture)){DeclarationEntryFail(6);return false;}
  declarationEntryRowsAfter=DeclarationEntryEncodeRows(tables);declarationEntryRowsMatched=true;Record();return true;
 }

 // ---- Step 4: one fixed value per UI turn through the original editor ----
 [StructLayout(LayoutKind.Explicit,Size=28)]
 private struct DeclarationEntryKeyInput {
  [FieldOffset(0)] public uint Type;
  [FieldOffset(4)] public ushort Vk;
  [FieldOffset(6)] public ushort Scan;
  [FieldOffset(8)] public uint Flags;
  [FieldOffset(12)] public uint Time;
  [FieldOffset(16)] public IntPtr Extra;
 }
 [DllImport("user32.dll",EntryPoint="SendInput",SetLastError=true)] private static extern uint DeclarationEntrySendInput(uint count,[In] DeclarationEntryKeyInput[] inputs,int size);
 private static bool DeclarationEntryAscii(string value){foreach(char character in value)if(character<32||character>126)return false;return true;}
 // Non-ASCII text (e.g. "GIẢ LẬP") as real keyboard input: KEYEVENTF_UNICODE key down/up per character
 // to the focused original editor (x86 INPUT layout, 28 bytes). ASCII text keeps the proven SendKeys path.
 private bool TypeDeclarationEntryUnicode(Control grid,Control editor,string value){
  if(IntPtr.Size!=4||Marshal.SizeOf(typeof(DeclarationEntryKeyInput))!=28)throw new InvalidOperationException();
  foreach(char character in value){
   if(!DeclarationEntryGuard(grid)||!editor.ContainsFocus)return false;
   DeclarationEntryKeyInput[] inputs=new DeclarationEntryKeyInput[2];
   inputs[0].Type=1;inputs[0].Scan=character;inputs[0].Flags=0x0004;inputs[1].Type=1;inputs[1].Scan=character;inputs[1].Flags=0x0004|0x0002;
   if(DeclarationEntrySendInput(2,inputs,28)!=2)throw new InvalidOperationException();Application.DoEvents();
  }
  return true;
 }
 private static bool DeclarationEntryDate(object cell,string expected){
  DateTime wanted=DateTime.ParseExact(expected,"dd/MM/yyyy",CultureInfo.InvariantCulture);object value=Get(cell,"Value");DateTime date;
  if(value is DateTime)return ((DateTime)value).Date==wanted.Date;
  string text=Convert.ToString(value,CultureInfo.InvariantCulture);
  return DateTime.TryParseExact(text,new string[]{"dd/MM/yyyy","d/M/yyyy","yyyy-MM-dd","ddMMyyyy"},CultureInfo.InvariantCulture,DateTimeStyles.None,out date)&&date.Date==wanted.Date;
 }
 private static bool DeclarationEntryNumber(object cell,string expected){decimal actual,wanted;return Decimal.TryParse(Convert.ToString(Get(cell,"Value"),CultureInfo.InvariantCulture),NumberStyles.Float,CultureInfo.InvariantCulture,out actual)&&Decimal.TryParse(expected,NumberStyles.Number,CultureInfo.InvariantCulture,out wanted)&&actual==wanted;}
 private void EditDeclarationEntry(int index){
  if(index!=declarationEntryActionCount||index<0||index>=declarationEntryPlan.Entries.Length||index>29)throw new InvalidOperationException();
  Control grid;object sheet=DeclarationEntrySheet(out grid);SetStage(HtkkAutomationStage.DeclarationEntryEditing);Record();
  string[] parts=declarationEntryPlan.Entries[index].Split('|');string kind=parts[0];int[] at=DeclarationEntryCell(parts[1]);int row=at[0],column=at[1];
  if(row>=Convert.ToInt32(Get(sheet,"RowCount"))||column>=Convert.ToInt32(Get(sheet,"ColumnCount"))){DeclarationEntryFail(6);return;}
  object cell=Cell(sheet,row,column);bool locked=Convert.ToBoolean(Get(cell,"Locked"));string type=DeclarationEntryCellKind(cell);
  if(kind=="date-optional"&&locked){declarationEntrySigningDateLocked=true;declarationEntryActionCount++;Record();return;}
  if(locked){declarationEntryLockedMask|=1<<index;DeclarationEntryFail(8);return;}
  // Controltype 14 is WinSpreadProcess.InsertDateCell (MaskCellType "00/00/0000", typed ddMMyyyy like the
  // D1 signing date); a general/text date cell is typed dd/MM/yyyy and reported in declarationEntryDateTextMask.
  bool dateMask=type=="FarPoint.Win.Spread.CellType.MaskCellType"&&Convert.ToString(Get(Get(cell,"CellType"),"Mask"),CultureInfo.InvariantCulture)=="00/00/0000";
  bool dateText=type=="FarPoint.Win.Spread.CellType.GeneralCellType"||type=="FarPoint.Win.Spread.CellType.TextCellType";
  if((kind=="date"||kind=="date-optional")&&!dateMask&&dateText)declarationEntryDateTextMask|=1<<index;
  bool typeMatched=kind=="combo"?type=="FarPoint.Win.Spread.CellType.ComboBoxCellType":kind=="date"||kind=="date-optional"?dateMask||dateText:
   type!="FarPoint.Win.Spread.CellType.ComboBoxCellType"&&type!="FarPoint.Win.Spread.CellType.CheckBoxCellType"&&type!="FarPoint.Win.Spread.CellType.ButtonCellType"&&type!="FarPoint.Win.Spread.CellType.MaskCellType";
  if(!typeMatched){declarationEntryCellTypeMismatchMask|=1<<index;DeclarationEntryFail(9);return;}
  DeclarationEntrySelect(grid,sheet,row,column);
  if(!DeclarationEntryActive(sheet,row,column)||!DeclarationEntryGuard(grid)){DeclarationEntryFail(10);return;}
  Control editor=HtkkNativeUiHarness.BeginCellEdit(grid,sheet,row,column,true);
  if(editor==null||!editor.Visible||!editor.Enabled){DeclarationEntryFail(11);return;}
  editor.Focus();if(!editor.ContainsFocus||!DeclarationEntryGuard(grid)){DeclarationEntryFail(10);return;}
  if(kind=="combo"){EditDeclarationEntryCombo(grid,sheet,editor,index,parts,row,column);return;}
  editorKind=editor is TextBoxBase?"text-box":"other-control";
  SendKeys.SendWait("^a");
  string value=parts[2];
  if(kind=="text"){
   if(DeclarationEntryAscii(value))SendKeys.SendWait(EscapeSendKeys(value));else if(!TypeDeclarationEntryUnicode(grid,editor,value)){DeclarationEntryFail(10);return;}
   Stopwatch clock=Stopwatch.StartNew();while(editor.Text!=value&&clock.Elapsed.TotalSeconds<2){Application.DoEvents();System.Threading.Thread.Sleep(10);}
   if(editor.Text!=value){declarationEntryMismatchMask|=1<<index;DeclarationEntryFail(12);return;}
  }else if(kind=="number")SendKeys.SendWait(value);
  else if(dateMask)SendKeys.SendWait(DateTime.ParseExact(value,"dd/MM/yyyy",CultureInfo.InvariantCulture).ToString("ddMMyyyy",CultureInfo.InvariantCulture));
  else SendKeys.SendWait(value);
  if(!DeclarationEntryGuard(grid)||!editor.ContainsFocus){DeclarationEntryFail(10);return;}
  SendKeys.SendWait("{TAB}");HtkkNativeUiHarness.CommitCellEdit(grid);Application.DoEvents();
  if(OriginalMessageVisible()){DeclarationEntryFail(17);return;}
  cell=Cell(sheet,row,column);
  bool matched=kind=="text"?CellText(sheet,row,column)==value:kind=="number"?DeclarationEntryNumber(cell,value):DeclarationEntryDate(cell,value);
  if(!matched){declarationEntryMismatchMask|=1<<index;DeclarationEntryFail(13);return;}
  declarationEntryActionCount++;Record();
 }
 // Combo bits: 1 FpCombo editor, 2 list item at plan index is the plan name, 4 no earlier item starts
 // with the search key, 8 initial selection empty, 16 search key moved the selection, 32 selection =
 // plan index after the key, 64 fallback ENTER (list) used, 128 list dropped, 256 selection = plan
 // index after the fallback arrows, 512 committed name, 1024 CellChange wrote the plan code.
 private void EditDeclarationEntryCombo(Control grid,object sheet,Control editor,int index,string[] parts,int row,int column){
  int planned=Int32.Parse(parts[2],CultureInfo.InvariantCulture);string key=parts[3],name=parts[4],code=parts[6];int[] codeCell=DeclarationEntryCell(parts[5]);int mask=0;
  if(declarationEntryComboCount>1||key.Length!=1||!DeclarationEntryAscii(key))throw new InvalidOperationException();
  int ordinal=declarationEntryComboCount++;
  Control vendor=FindVendorCombo(editor,0);
  if(vendor!=null){
   mask|=1;editorKind="combo";object list=Get(vendor,"List");System.Collections.IList sequence=list as System.Collections.IList;int count=sequence!=null?sequence.Count:Convert.ToInt32(Get(list,"Count"));
   PropertyInfo item=list.GetType().GetProperty("Item",new Type[]{typeof(int)});if(count<1||count>4096||(item==null&&sequence==null))throw new InvalidOperationException();
   bool earlier=false;
   for(int offset=0;offset<count&&offset<=planned;offset++){
    object entry=sequence!=null?sequence[offset]:item.GetValue(list,new object[]{offset});string text=entry==null?String.Empty:entry.ToString();
    if(offset==planned&&text==name)mask|=2;
    if(offset<planned&&text.Length>0&&Char.ToUpperInvariant(text[0])==Char.ToUpperInvariant(key[0]))earlier=true;
   }
   if(!earlier)mask|=4;
  }
  if((mask&7)!=7){DeclarationEntryComboMask(ordinal,mask);DeclarationEntryFail(14);return;}
  int before=Convert.ToInt32(Get(vendor,"SelectedIndex"));if(before==-1)mask|=8;
  // Original FpCombo AutoSearch: the leading character of the item name, typed into the editor.
  SendKeys.SendWait(key);Stopwatch clock=Stopwatch.StartNew();
  while(Convert.ToInt32(Get(vendor,"SelectedIndex"))==before&&clock.Elapsed.TotalSeconds<1){Application.DoEvents();System.Threading.Thread.Sleep(10);}
  int after=Convert.ToInt32(Get(vendor,"SelectedIndex"));if(after!=before)mask|=16;if(after==planned)mask|=32;
  if(after!=planned){
   if(after!=before||OriginalMessageVisible()){DeclarationEntryComboMask(ordinal,mask);DeclarationEntryFail(15);return;}
   // Fallback, still keyboard only: ENTER shows the original list (FpCombo.OnKeyDown), DOWN moves
   // one item per key. Stops at the first key that does not advance or that leaves the cell.
   mask|=64;SendKeys.SendWait("{ENTER}");Application.DoEvents();
   if(!DeclarationEntryActive(sheet,row,column)||Get(grid,"EditingControl")==null||!DeclarationEntryGuard(grid)){DeclarationEntryComboMask(ordinal,mask);DeclarationEntryFail(18);return;}
   if(Convert.ToBoolean(Get(vendor,"DroppedDown")))mask|=128;
   for(int step=Convert.ToInt32(Get(vendor,"SelectedIndex"))+1;step<=planned;step++){
    SendKeys.SendWait("{DOWN}");clock=Stopwatch.StartNew();
    while(Convert.ToInt32(Get(vendor,"SelectedIndex"))!=step&&clock.Elapsed.TotalSeconds<1){Application.DoEvents();System.Threading.Thread.Sleep(10);}
    if(Convert.ToInt32(Get(vendor,"SelectedIndex"))!=step||!DeclarationEntryActive(sheet,row,column)||Get(grid,"EditingControl")==null){DeclarationEntryComboMask(ordinal,mask);DeclarationEntryFail(15);return;}
   }
   if(Convert.ToInt32(Get(vendor,"SelectedIndex"))!=planned){DeclarationEntryComboMask(ordinal,mask);DeclarationEntryFail(15);return;}
   mask|=256;
  }
  if(!DeclarationEntryGuard(grid)){DeclarationEntryComboMask(ordinal,mask);DeclarationEntryFail(10);return;}
  SendKeys.SendWait("{TAB}");HtkkNativeUiHarness.CommitCellEdit(grid);Application.DoEvents();
  if(OriginalMessageVisible()){DeclarationEntryComboMask(ordinal,mask);DeclarationEntryFail(17);return;}
  // frmWinToKhai.winFpSpread_CellChange (control 87) writes the catalogue key into the SelectedValue cell.
  clock=Stopwatch.StartNew();while(CellText(sheet,codeCell[0],codeCell[1])!=code&&clock.Elapsed.TotalSeconds<1){Application.DoEvents();System.Threading.Thread.Sleep(10);}
  if(CellText(sheet,row,column)==name)mask|=512;if(CellText(sheet,codeCell[0],codeCell[1])==code)mask|=1024;
  DeclarationEntryComboMask(ordinal,mask);
  if((mask&512)==0){declarationEntryMismatchMask|=1<<index;DeclarationEntryFail(13);return;}
  if((mask&1024)==0){declarationEntryMismatchMask|=1<<index;DeclarationEntryFail(16);return;}
  declarationEntryActionCount++;Record();
 }
 private void DeclarationEntryComboMask(int ordinal,int mask){if(ordinal==0)declarationEntryCombo1Mask=mask;else declarationEntryCombo2Mask=mask;Record();}

 // ---- Step 5: read the HTKK-computed cells (row taxes, table totals) and the final locks ----
 private bool InspectDeclarationEntrySheet(){
  Control grid;object sheet=DeclarationEntrySheet(out grid);SetStage(HtkkAutomationStage.DeclarationEntrySheetChecking);
  declarationEntrySheetMatched=InspectDeclarationGrid();declarationEntryLockFinalMask=DeclarationEntryLockMask(sheet);
  int[] signer=DeclarationEntryCell(declarationEntryPlan.SignerCell);declarationEntrySignerMatched=CellText(sheet,signer[0],signer[1])==FakeSigner;
  Record();return declarationEntrySheetMatched&&declarationEntryLockFinalMask==DeclarationEntryExpectedLocks();
 }

 // ---- Phase driver (one action per UI timer turn; nested pumping cannot re-enter) ----
 private void ContinueDeclarationEntry(){
  if(!OriginalRoundtripOwnerReady())return;
  if(declarationEntryPlan==null||!DeclarationEntryCase())throw new InvalidOperationException();
  declarationEntryBusy=true;
  try{
   if(declarationPhase=="entry-ready"){VerifyDeclarationEntryPins();if(!finished)declarationPhase="entry-choice";return;}
   if(declarationPhase=="entry-choice"){ChooseDeclarationEntryPart();if(!finished)declarationPhase="entry-rows";return;}
   if(declarationPhase=="entry-rows"){if(InsertDeclarationEntryRows()&&!finished)declarationPhase="entry-values";return;}
   if(declarationPhase=="entry-values"){
    EditDeclarationEntry(declarationEntryActionCount);if(finished)return;
    if(declarationEntryActionCount==declarationEntryPlannedCount){declarationEntryValuesMatched=declarationEntryMismatchMask==0&&declarationEntryLockedMask==0&&declarationEntryCellTypeMismatchMask==0;declarationPhase="entry-inspect";declarationEntryClock=Stopwatch.StartNew();Record();}
    return;
   }
   if(declarationPhase=="entry-inspect"){
    bool matched=InspectDeclarationEntrySheet();
    // Original recalculation may settle on a later UI turn; bounded wait.
    if(!matched&&declarationEntryClock.Elapsed.TotalSeconds<3)return;
    if(!matched){DeclarationEntryFail(20);return;}
    declarationPhase="export-start";SetStage(HtkkAutomationStage.DeclarationExportReadyWaiting);Record();return;
   }
   throw new InvalidOperationException();
  }finally{declarationEntryBusy=false;}
 }

 // ==== Native-case mode web-xml-import-tick-reexport (U5 3.1.0): original actions AFTER the original import ====
 // The web XML is imported as in every import case; then HtkkDeclarationCasePlans.ImportTick types its fixed edits
 // through the original editor and ticks its checkbox cells with SPACE (FpSpread.ButtonClicked -> ButtonClick_0),
 // one action per UI turn, so HTKK itself rebuilds what the XML cannot carry (PL 01 and CD of the NQ 43 reduction).
 // Then the shared sheet checks, original export, pinned XSD and whole-tree comparison run unchanged.
 // Never: Cell.Value/Text assignment, business helper calls, authored totals. Diagnostics are flags, counts, masks.
 private HtkkDeclarationTickPlan declarationTickPlan=null;
 private Stopwatch declarationTickClock=null;
 private bool declarationTickMethodPinsMatched=false,declarationTickEditsMatched=false,declarationTickTicksMatched=false,declarationTickReadbackMatched=false;
 private int declarationTickPlannedCount=0,declarationTickActionCount=0,declarationTickFailureCode=0,declarationTickMethodPinMask=0,declarationTickMismatchMask=0,declarationTickReadbackMask=0;
 // Failure codes (declarationTickFailureCode), value-free:
 //  1 method pin   3 tick cell not a CheckBoxCellType   7 tick cell locked   12 tick cell already ticked   14 tick row hidden
 //  4 tick not applied   5 ticks/clear cells changed afterwards
 //  6 sheet metadata   8 edit cell locked   9 edit cell type   10 foreground/focus guard   11 editor   13 edit read-back
 //  17 original message
 // declarationTickMismatchMask: bit = action index (edits first, then ticks). declarationTickReadbackMask: bits 0-7
 // readback cell i differs (diagnostic only), bits 8-11 tick i no longer ticked, bits 12-15 clear cell i ticked.
 private string DeclarationTickJson(){
  string q=((char)34).ToString();StringBuilder json=new StringBuilder();
  string[] names=new string[]{"declarationTickMethodPinsMatched","declarationTickEditsMatched","declarationTickTicksMatched","declarationTickReadbackMatched"};
  bool[] values=new bool[]{declarationTickMethodPinsMatched,declarationTickEditsMatched,declarationTickTicksMatched,declarationTickReadbackMatched};
  for(int index=0;index<names.Length;index++)json.Append(","+q+names[index]+q+":"+Bool(values[index]));
  names=new string[]{"declarationTickPlannedCount","declarationTickActionCount","declarationTickFailureCode","declarationTickMethodPinMask","declarationTickMismatchMask","declarationTickReadbackMask"};
  int[] counts=new int[]{declarationTickPlannedCount,declarationTickActionCount,declarationTickFailureCode,declarationTickMethodPinMask,declarationTickMismatchMask,declarationTickReadbackMask};
  for(int index=0;index<names.Length;index++)json.Append(","+q+names[index]+q+":"+counts[index].ToString(CultureInfo.InvariantCulture));
  return json.ToString();
 }
 private void DeclarationTickFail(int code){if(declarationTickFailureCode==0)declarationTickFailureCode=code;DeclarationTerminal(HtkkAutomationStage.DeclarationImportTickNotMatched);}
 private bool DeclarationTickSucceeded(){return declarationTickMethodPinsMatched&&declarationTickEditsMatched&&declarationTickTicksMatched&&declarationTickFailureCode==0&&declarationTickMismatchMask==0&&declarationTickPlannedCount>0&&declarationTickActionCount==declarationTickPlannedCount;}
 private void VerifyDeclarationTickPins(){
  SetStage(HtkkAutomationStage.DeclarationImportTickPinsChecking);declarationTickPlannedCount=declarationTickPlan.Edits.Length+declarationTickPlan.Ticks.Length;Record();
  declarationTickMethodPinMask=DeclarationMethodPinMask(declarationTickPlan.MethodPins);declarationTickMethodPinsMatched=declarationTickMethodPinMask==0;Record();
  if(!declarationTickMethodPinsMatched)DeclarationTickFail(1);
 }
 // One fixed number through the original editor ("^a", value, "{TAB}"), read back as Decimal.
 private void EditDeclarationTick(int index){
  if(index!=declarationTickActionCount||index<0||index>=declarationTickPlan.Edits.Length)throw new InvalidOperationException();
  Control grid;object sheet=DeclarationEntrySheet(out grid);SetStage(HtkkAutomationStage.DeclarationImportTickEditing);Record();
  string[] parts=declarationTickPlan.Edits[index].Split('|');int[] at=DeclarationEntryCell(parts[1]);int row=at[0],column=at[1];
  if(row>=Convert.ToInt32(Get(sheet,"RowCount"))||column>=Convert.ToInt32(Get(sheet,"ColumnCount"))){DeclarationTickFail(6);return;}
  object cell=Cell(sheet,row,column);string type=DeclarationEntryCellKind(cell);
  if(Convert.ToBoolean(Get(cell,"Locked"))){declarationTickMismatchMask|=1<<index;DeclarationTickFail(8);return;}
  if(type=="FarPoint.Win.Spread.CellType.ComboBoxCellType"||type=="FarPoint.Win.Spread.CellType.CheckBoxCellType"||type=="FarPoint.Win.Spread.CellType.ButtonCellType"||type=="FarPoint.Win.Spread.CellType.MaskCellType"){declarationTickMismatchMask|=1<<index;DeclarationTickFail(9);return;}
  DeclarationEntrySelect(grid,sheet,row,column);
  if(!DeclarationEntryActive(sheet,row,column)||!DeclarationEntryGuard(grid)){DeclarationTickFail(10);return;}
  Control editor=HtkkNativeUiHarness.BeginCellEdit(grid,sheet,row,column,true);
  if(editor==null||!editor.Visible||!editor.Enabled){DeclarationTickFail(11);return;}
  editor.Focus();if(!editor.ContainsFocus||!DeclarationEntryGuard(grid)){DeclarationTickFail(10);return;}
  editorKind=editor is TextBoxBase?"text-box":"other-control";
  SendKeys.SendWait("^a");SendKeys.SendWait(parts[2]);
  if(!DeclarationEntryGuard(grid)||!editor.ContainsFocus){DeclarationTickFail(10);return;}
  // TAB ends the edit: FpSpread.Change -> winFpSpread_CellChange -> WinDoWorkEvent.CellChange -> CellChange_0.
  SendKeys.SendWait("{TAB}");HtkkNativeUiHarness.CommitCellEdit(grid);Application.DoEvents();
  if(OriginalMessageVisible()){DeclarationTickFail(17);return;}
  if(!DeclarationEntryNumber(Cell(sheet,row,column),parts[2])){declarationTickMismatchMask|=1<<index;DeclarationTickFail(13);return;}
  declarationTickActionCount++;Record();
 }
 // SPACE on an open, unticked original checkbox: FpSpread.ButtonClicked -> frmWinToKhai.winFpSpread_ButtonClicked
 // -> WinDoWorkEvent.ButtonClick -> ButtonClick_0 (daySangPLGiamThue, capNhatToKhai).
 private void TickDeclarationImport(int index){
  int action=declarationTickPlan.Edits.Length+index;
  if(action!=declarationTickActionCount||index<0||index>=declarationTickPlan.Ticks.Length)throw new InvalidOperationException();
  Control grid;object sheet=DeclarationEntrySheet(out grid);SetStage(HtkkAutomationStage.DeclarationImportTickInvoking);Record();
  int[] at=DeclarationEntryCell(declarationTickPlan.Ticks[index]);
  if(at[0]>=Convert.ToInt32(Get(sheet,"RowCount"))||at[1]>=Convert.ToInt32(Get(sheet,"ColumnCount"))){DeclarationTickFail(6);return;}
  object cell=Cell(sheet,at[0],at[1]);
  // Distinct value-free codes for the four preconditions (release run 43136692872 could only report code 3).
  int precondition=DeclarationEntryCellKind(cell)!="FarPoint.Win.Spread.CellType.CheckBoxCellType"?3:Convert.ToBoolean(Get(cell,"Locked"))?7:Selected(Get(cell,"Value"))?12:!RowVisible(sheet,at[0])?14:0;
  if(precondition!=0){declarationTickMismatchMask|=1<<action;DeclarationTickFail(precondition);return;}
  DeclarationEntrySelect(grid,sheet,at[0],at[1]);
  if(!DeclarationEntryActive(sheet,at[0],at[1])||!DeclarationEntryGuard(grid)){DeclarationTickFail(10);return;}
  SendKeys.SendWait(" ");Stopwatch clock=Stopwatch.StartNew();bool ticked=false;
  do{
   if(OriginalMessageVisible()){DeclarationTickFail(17);return;}
   ticked=Selected(Get(Cell(sheet,at[0],at[1]),"Value"));if(ticked)break;
   Application.DoEvents();System.Threading.Thread.Sleep(10);
  }while(clock.Elapsed.TotalSeconds<3);
  if(!ticked){declarationTickMismatchMask|=1<<action;DeclarationTickFail(4);return;}
  declarationTickActionCount++;Record();
 }
 // Ticks still ticked, clear cells still clear (gating); readbacks of HTKK-written cells (diagnostic mask only).
 private bool InspectDeclarationTick(){
  Control grid;object sheet=DeclarationEntrySheet(out grid);SetStage(HtkkAutomationStage.DeclarationImportTickReadbackChecking);int mask=0;
  for(int index=0;index<declarationTickPlan.Readbacks.Length;index++){string[] parts=declarationTickPlan.Readbacks[index].Split('|');int[] at=DeclarationEntryCell(parts[0]);if(CellText(sheet,at[0],at[1])!=parts[1])mask|=1<<index;}
  for(int index=0;index<declarationTickPlan.Ticks.Length;index++){int[] at=DeclarationEntryCell(declarationTickPlan.Ticks[index]);if(!Selected(Get(Cell(sheet,at[0],at[1]),"Value")))mask|=1<<(8+index);}
  for(int index=0;index<declarationTickPlan.Unticked.Length;index++){int[] at=DeclarationEntryCell(declarationTickPlan.Unticked[index]);object cell=Cell(sheet,at[0],at[1]);if(DeclarationEntryCellKind(cell)!="FarPoint.Win.Spread.CellType.CheckBoxCellType"||Selected(Get(cell,"Value")))mask|=1<<(12+index);}
  declarationTickReadbackMask=mask;declarationTickReadbackMatched=(mask&0xFF)==0;declarationTickTicksMatched=(mask&0xFF00)==0;Record();
  return mask==0;
 }
 private void ContinueDeclarationTick(){
  if(!OriginalRoundtripOwnerReady())return;
  if(declarationTickPlan==null||declarationEntryPlan!=null||!roundtripImportSucceeded)throw new InvalidOperationException();
  declarationEntryBusy=true;
  try{
   if(declarationPhase=="tick-pins"){VerifyDeclarationTickPins();if(!finished)declarationPhase="tick-edits";return;}
   if(declarationPhase=="tick-edits"){
    EditDeclarationTick(declarationTickActionCount);if(finished)return;
    // A plan without ticks (PL 03: the edit alone runs capNhatToKhai) goes straight to the read-back.
    if(declarationTickActionCount==declarationTickPlan.Edits.Length){declarationTickEditsMatched=declarationTickMismatchMask==0;if(declarationTickPlan.Ticks.Length==0){declarationPhase="tick-inspect";declarationTickClock=Stopwatch.StartNew();}else declarationPhase="tick-ticks";Record();}
    return;
   }
   if(declarationPhase=="tick-ticks"){
    TickDeclarationImport(declarationTickActionCount-declarationTickPlan.Edits.Length);if(finished)return;
    if(declarationTickActionCount==declarationTickPlannedCount){declarationPhase="tick-inspect";declarationTickClock=Stopwatch.StartNew();Record();}
    return;
   }
   if(declarationPhase=="tick-inspect"){
    bool settled=InspectDeclarationTick();
    // Original recalculation may settle on a later UI turn; bounded wait. Readbacks never stop the case.
    if(!settled&&declarationTickClock.Elapsed.TotalSeconds<3)return;
    if(!declarationTickTicksMatched){DeclarationTickFail(5);return;}
    declarationPhase="import-inspect";declarationClock=Stopwatch.StartNew();SetStage(HtkkAutomationStage.DeclarationImportSheetChecking);Record();return;
   }
   throw new InvalidOperationException();
  }finally{declarationEntryBusy=false;}
 }
}
