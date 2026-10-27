// Own staged controller of ORIGINAL period controls and inspection of the ORIGINAL D1 sheet.
// No HEADER or declaration XML is created by this helper.
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
 private bool periodDateMatched=false,periodFirstMatched=false,periodActivityMatched=false,periodGeographyMatched=false,periodNoAnnexMatched=false,periodConfirmInvoked=false;
 private bool gtgtPins=false,gtgtVersion=false,gtgtPeriod=false,gtgtSheet=false,gtgtName=false,gtgtDimensions=false,gtgtIdentity=false,gtgtCt21=false,gtgtSigner=false,gtgtZero=false;
 private int annexSelected=0,gtgtRows=0,gtgtColumns=0,gtgtSheets=0,gtgtEmptyMoney=0;
 private bool gtgtCt42BeforeExportObserved=false,gtgtCt42LockedBeforeExport=false,gtgtCt42AfterImportObserved=false,gtgtCt42LockedAfterImport=false;
 private bool gtgtSheetInspectionBusy=false,gtgtAutoCalculationReady=false,gtgtBusinessInstanceMatched=false;
 private bool gtgtCaseMoneyMatched=false,gtgtCt42Locked=false,webCaseEdited=false;private int gtgtCaseMoneyCount=0,gtgtCaseMismatchMask=0,gtgtCaseNonzeroMask=0;private Stopwatch webCaseEditClock=null;
 private Stopwatch gtgtObservationClock=null;
 private bool noActivityCheckboxActivated=false,gtgtCt21CaseMatched=false,gtgtCt21ConfirmationMatched=false,gtgtCt21LocksMatched=false,gtgtCt21BeforeExportMatched=false,gtgtCt21AfterImportMatched=false,gtgtCt21UncheckMatched=false;
 private bool periodAnnex12Matched=false,annex12SourcePinsMatched=false,annex12SheetObserved=false,annex12StructureMatched=false,annex12GroupMetadataMatched=false,annex12SttMatched=false,annex12LocksMatched=false;
 private int annex12SelectionActionCount=0,annex12SheetRows=0,annex12SheetColumns=0,annex12NumericCount=0,annex12NumericEmptyMask=0,annex12NumericNonzeroMask=0,annex12GroupCount=0,annex12FirstGroupId=0,annex12FirstGroupRows=0;
 private string Annex12Json(){
  string q=((char)34).ToString();StringBuilder value=new StringBuilder();
  string[] names=new string[]{"periodAnnex12Matched","annex12SourcePinsMatched","annex12SheetObserved","annex12StructureMatched","annex12GroupMetadataMatched","annex12SttMatched","annex12LocksMatched"};
  bool[] flags=new bool[]{periodAnnex12Matched,annex12SourcePinsMatched,annex12SheetObserved,annex12StructureMatched,annex12GroupMetadataMatched,annex12SttMatched,annex12LocksMatched};
  for(int index=0;index<names.Length;index++)value.Append(","+q+names[index]+q+":"+Bool(flags[index]));
  names=new string[]{"annex12SelectionActionCount","annex12SheetRows","annex12SheetColumns","annex12NumericCount","annex12NumericEmptyMask","annex12NumericNonzeroMask","annex12GroupCount","annex12FirstGroupId","annex12FirstGroupRows"};
  int[] counts=new int[]{annex12SelectionActionCount,annex12SheetRows,annex12SheetColumns,annex12NumericCount,annex12NumericEmptyMask,annex12NumericNonzeroMask,annex12GroupCount,annex12FirstGroupId,annex12FirstGroupRows};
  for(int index=0;index<names.Length;index++)value.Append(","+q+names[index]+q+":"+counts[index].ToString(CultureInfo.InvariantCulture));return value.ToString()+Annex12RowJson()+Annex12InputJson()+Annex12NumericJson()+Annex12ExportJson();
 }
 private bool Annex12InspectionMode(){return mode=="gtgt-annex12-inspect"||mode=="gtgt-annex12-row-inspect"||mode=="gtgt-annex12-input-inspect"||mode=="gtgt-annex12-numeric-inspect"||mode=="gtgt-annex12-export-inspect";}
 private bool annex12RowTabClickInvoked=false,annex12F5Visible=false,annex12F5Invoked=false,annex12RowBeforeMatched=false,annex12RowAfterMatched=false,annex12RowSttMatched=false,annex12RowLocksMatched=false;
 private int annex12RowBeforeRows=0,annex12RowAfterRows=0,annex12RowBeforeGroupRows=0,annex12RowAfterGroupRows=0,annex12RowAfterGroupId=0,annex12RowInsertActionCount=0;
 private string Annex12RowJson(){
  string q=((char)34).ToString();StringBuilder value=new StringBuilder();
  string[] names=new string[]{"annex12RowTabClickInvoked","annex12F5Visible","annex12F5Invoked","annex12RowBeforeMatched","annex12RowAfterMatched","annex12RowSttMatched","annex12RowLocksMatched"};
  bool[] flags=new bool[]{annex12RowTabClickInvoked,annex12F5Visible,annex12F5Invoked,annex12RowBeforeMatched,annex12RowAfterMatched,annex12RowSttMatched,annex12RowLocksMatched};
  for(int index=0;index<names.Length;index++)value.Append(","+q+names[index]+q+":"+Bool(flags[index]));
  names=new string[]{"annex12RowBeforeRows","annex12RowAfterRows","annex12RowBeforeGroupRows","annex12RowAfterGroupRows","annex12RowAfterGroupId","annex12RowInsertActionCount"};
  int[] counts=new int[]{annex12RowBeforeRows,annex12RowAfterRows,annex12RowBeforeGroupRows,annex12RowAfterGroupRows,annex12RowAfterGroupId,annex12RowInsertActionCount};
  for(int index=0;index<names.Length;index++)value.Append(","+q+names[index]+q+":"+counts[index].ToString(CultureInfo.InvariantCulture));return value.ToString();
 }
 private int ObserveAnnex12FirstGroupRowsAfterInsert(){
  System.Collections.IList infos=Get(Global("ToKhaiInfo"),"SheetInfos") as System.Collections.IList;if(infos==null||infos.Count>32)throw new InvalidOperationException();object info=null;
  foreach(object candidate in infos){if(candidate==null)continue;if(Convert.ToString(Get(candidate,"SheetID"),CultureInfo.InvariantCulture)=="01_2"){if(info!=null)throw new InvalidOperationException();info=candidate;}}
  if(info==null||!Selected(Get(info,"Active")))throw new InvalidOperationException();System.Collections.IList tables=Get(info,"Tables") as System.Collections.IList;if(tables==null||tables.Count!=1)throw new InvalidOperationException();
  object first=tables[0];if(Convert.ToString(Get(first,"TableID"),CultureInfo.InvariantCulture)!="1"||Convert.ToString(Get(first,"TableName"),CultureInfo.InvariantCulture)!="01_2_GTGT"||Convert.ToString(Get(first,"TablePath"),CultureInfo.InvariantCulture)!="PLuc_01_2_GTGT/TenNhaMay")throw new InvalidOperationException();annex12RowAfterGroupId=1;
  System.Collections.IList rows=Get(first,"RowsValues") as System.Collections.IList;if(rows==null||rows.Count>10000)throw new InvalidOperationException();return rows.Count;
 }
 private void ClickOriginalAnnex12Tab(Control grid,object annex,Form owner){
  if((mode!="gtgt-annex12-row-inspect"&&mode!="gtgt-annex12-input-inspect"&&mode!="gtgt-annex12-numeric-inspect"&&mode!="gtgt-annex12-export-inspect")||annex12RowTabClickInvoked||annex12F5Invoked||!periodAnnex12Matched||annexSelected!=1||!annex12SourcePinsMatched||!annex12StructureMatched||owner==null||owner.GetType().FullName!="HTKK.frmWinToKhai"||grid.FindForm()!=owner||!owner.Visible||!owner.Enabled||!grid.Visible||!grid.Enabled||Get(grid,"ActiveSheet")!=annex||Convert.ToInt32(Get(grid,"ActiveSheetIndex"))!=1||OriginalMessageVisible())throw new InvalidOperationException();
  string name=Convert.ToString(Get(annex,"SheetName"),CultureInfo.InvariantCulture);if(name!="01_2"&&name!="01-2/GTGT")throw new InvalidOperationException();
  grid.Focus();uint pid,controlPid;GetWindowThreadProcessId(GetForegroundWindow(),out pid);GetWindowThreadProcessId(grid.Handle,out controlPid);if(pid!=(uint)Process.GetCurrentProcess().Id||controlPid!=pid||!grid.ContainsFocus)throw new InvalidOperationException();
  stage="gtgt-annex12-tab-clicking";Record();
  MethodInfo geometry=grid.GetType().GetMethod("GetSheetTabRectangle",new Type[]{typeof(int)});if(geometry==null||!geometry.IsPublic)throw new InvalidOperationException();object tab=geometry.Invoke(grid,new object[]{1}),client=Get(grid,"ClientRectangle");if(tab==null||client==null||tab.GetType().FullName!="System.Drawing.Rectangle"||client.GetType().FullName!="System.Drawing.Rectangle")throw new InvalidOperationException();
  int left=Convert.ToInt32(Get(tab,"X")),top=Convert.ToInt32(Get(tab,"Y")),width=Convert.ToInt32(Get(tab,"Width")),height=Convert.ToInt32(Get(tab,"Height")),clientWidth=Convert.ToInt32(Get(client,"Width")),clientHeight=Convert.ToInt32(Get(client,"Height"));
  if(left<0||top<0||width<1||height<1||clientWidth<1||clientHeight<1||clientWidth>32767||clientHeight>32767||(long)left+width>clientWidth||(long)top+height>clientHeight)throw new InvalidOperationException();
  int x=left+width/2,y=top+height/2;IntPtr point=new IntPtr((y<<16)|(x&65535));
  GetWindowThreadProcessId(GetForegroundWindow(),out pid);if(pid!=(uint)Process.GetCurrentProcess().Id||!grid.ContainsFocus||OriginalMessageVisible())throw new InvalidOperationException();
  // Real mouse messages hit the vendor's public tab rectangle and preserve
  // ORIGINAL SheetTabClick/toolbar handlers. Do not invoke that private handler
  // or set pnF5.Visible directly. Geometry and coordinates are never reported.
  if(!PostMessage(grid.Handle,0x0201,new IntPtr(1),point)||!PostMessage(grid.Handle,0x0202,IntPtr.Zero,point))throw new InvalidOperationException();
  annex12RowTabClickInvoked=true;Application.DoEvents();
  if(Get(grid,"ActiveSheet")!=annex||!owner.Enabled||!grid.Enabled||OriginalMessageVisible())throw new InvalidOperationException();
 }

 private void InspectOriginalAnnex12Row(Control grid,object annex){
  if((mode!="gtgt-annex12-row-inspect"&&mode!="gtgt-annex12-input-inspect"&&mode!="gtgt-annex12-numeric-inspect"&&mode!="gtgt-annex12-export-inspect")||annex12F5Invoked||annex12RowInsertActionCount!=0||!periodAnnex12Matched||annexSelected!=1||!annex12SourcePinsMatched||!annex12StructureMatched||!annex12GroupMetadataMatched||!annex12LocksMatched||!annex12SttMatched||annex12NumericCount!=8||annex12NumericEmptyMask!=0||annex12NumericNonzeroMask!=0)throw new InvalidOperationException();
  annex12RowBeforeRows=annex12SheetRows;annex12RowBeforeGroupRows=annex12FirstGroupRows;
  annex12RowBeforeMatched=annex12RowBeforeRows==66&&annex12SheetColumns==45&&annex12GroupCount==1&&annex12FirstGroupId==1&&annex12RowBeforeGroupRows==1;
  Form owner=grid.FindForm();if(!annex12RowBeforeMatched||owner==null||owner.GetType().FullName!="HTKK.frmWinToKhai"||!owner.Visible||!owner.Enabled||!grid.Visible||!grid.Enabled||Get(grid,"ActiveSheet")!=annex||Convert.ToInt32(Get(grid,"ActiveSheetIndex"))!=1||OriginalMessageVisible())throw new InvalidOperationException();
  ClickOriginalAnnex12Tab(grid,annex,owner);
  if(Convert.ToBoolean(Get(Cell(annex,43,20),"Locked")))throw new InvalidOperationException();
  grid.Focus();annex.GetType().GetMethod("SetActiveCell",new Type[]{typeof(int),typeof(int)}).Invoke(annex,new object[]{43,20});Application.DoEvents();
  if(Convert.ToInt32(Get(annex,"ActiveRowIndex"))!=43||Convert.ToInt32(Get(annex,"ActiveColumnIndex"))!=20||Get(grid,"ActiveSheet")!=annex||!owner.Enabled||!grid.Enabled||OriginalMessageVisible())throw new InvalidOperationException();
  Control[] f5=owner.Controls.Find("pnF5",true);annex12F5Visible=f5.Length==1&&f5[0].Visible&&f5[0].Enabled;if(!annex12F5Visible)throw new InvalidOperationException();
  uint pid;GetWindowThreadProcessId(GetForegroundWindow(),out pid);if(pid!=(uint)Process.GetCurrentProcess().Id||!grid.ContainsFocus||Get(grid,"ActiveSheet")!=annex||OriginalMessageVisible())throw new InvalidOperationException();
  annex12F5Invoked=true;stage="gtgt-annex12-f5-invoking";Record();
  // REAL F5 is routed through original frmWinToKhai.ProcessCmdKey. Never call
  // InsertTableRowNoSView/InsertTable or directly write rows, values or totals.
  SendKeys.SendWait("{F5}");annex12RowInsertActionCount++;
  Stopwatch clock=Stopwatch.StartNew();
  do{
   if(OriginalMessageVisible()||Get(grid,"ActiveSheet")!=annex||!owner.Enabled||!grid.Enabled)throw new InvalidOperationException();
   annex12RowAfterRows=Convert.ToInt32(Get(annex,"RowCount"));annex12RowAfterGroupRows=ObserveAnnex12FirstGroupRowsAfterInsert();
   if(annex12RowAfterRows==annex12RowBeforeRows+1&&annex12RowAfterGroupRows==annex12RowBeforeGroupRows+1)break;
   Application.DoEvents();System.Threading.Thread.Sleep(10);
  }while(clock.Elapsed.TotalSeconds<2);
  if(annex12RowAfterRows<47||annex12RowAfterRows>10000||Convert.ToInt32(Get(annex,"ColumnCount"))!=45)throw new InvalidOperationException();
  annex12RowSttMatched=CellText(annex,42,1)=="1"&&CellText(annex,43,1)=="1.1"&&CellText(annex,44,1)=="1.2";annex12RowLocksMatched=true;
  int[,] cells=new int[,]{{42,4},{42,9},{42,19},{42,20},{42,23},{43,19},{43,20},{43,23},{44,19},{44,20},{44,23},{46,19},{46,23}};
  bool[] locks=new bool[]{false,false,false,true,true,true,false,true,true,false,true,true,true};
  for(int index=0;index<cells.GetLength(0);index++)if(Convert.ToBoolean(Get(Cell(annex,cells[index,0],cells[index,1]),"Locked"))!=locks[index])annex12RowLocksMatched=false;
  annex12RowAfterMatched=annex12RowAfterRows==67&&annex12RowAfterGroupRows==2&&annex12RowAfterGroupId==1&&annex12RowInsertActionCount==1&&annex12RowSttMatched&&annex12RowLocksMatched;
  if((mode=="gtgt-annex12-input-inspect"||mode=="gtgt-annex12-numeric-inspect"||mode=="gtgt-annex12-export-inspect")){if(!annex12RowAfterMatched)throw new InvalidOperationException();InspectOriginalAnnex12Inputs(grid,annex);return;}
  finished=true;stage="gtgt-annex12-row-inspected";Record();
 }

 // Fixed synthetic input scenario, separate from the already proved row-only mode.
 // These methods edit public ORIGINAL controls. Hidden codes and computed totals
 // are read afterwards; they are never assigned by the reference host.
 private bool annex12InputReadOnlyIdentityMatched=false,annex12InputIdentityMatched=false,annex12InputTypesMatched=false,annex12InputGeographyMatched=false,annex12InputTaxAuthoritiesMatched=false,annex12InputPercentagesMatched=false,annex12InputZeroTaxMatched=false;
 private int annex12InputActionCount=0;
 private string Annex12InputJson(){
  string q=((char)34).ToString();StringBuilder result=new StringBuilder();
  string[] names=new string[]{"annex12InputReadOnlyIdentityMatched","annex12InputIdentityMatched","annex12InputTypesMatched","annex12InputGeographyMatched","annex12InputTaxAuthoritiesMatched","annex12InputPercentagesMatched","annex12InputZeroTaxMatched"};
  bool[] flags=new bool[]{annex12InputReadOnlyIdentityMatched,annex12InputIdentityMatched,annex12InputTypesMatched,annex12InputGeographyMatched,annex12InputTaxAuthoritiesMatched,annex12InputPercentagesMatched,annex12InputZeroTaxMatched};
  for(int index=0;index<names.Length;index++)result.Append(","+q+names[index]+q+":"+Bool(flags[index]));
  return result.ToString()+","+q+"annex12InputActionCount"+q+":"+annex12InputActionCount.ToString(CultureInfo.InvariantCulture);
 }
 private void Annex12InputOwner(Control grid,object annex){
  Form owner=grid.FindForm();uint pid;GetWindowThreadProcessId(GetForegroundWindow(),out pid);
  if((mode!="gtgt-annex12-input-inspect"&&mode!="gtgt-annex12-numeric-inspect"&&mode!="gtgt-annex12-export-inspect")||Global("InstanceClass")==null||Global("InstanceClass").GetType().FullName!="TAX.HTKK.Business.Gtgt01TT80Nckt283"||!Convert.ToBoolean(Get(annex,"AutoCalculation"))||!annex12RowAfterMatched||annex12InputActionCount<0||annex12InputActionCount>14||owner==null||owner.GetType().FullName!="HTKK.frmWinToKhai"||!owner.Visible||!owner.Enabled||!grid.Visible||!grid.Enabled||!grid.ContainsFocus||Get(grid,"ActiveSheet")!=annex||pid!=(uint)Process.GetCurrentProcess().Id||OriginalMessageVisible()||Convert.ToInt32(Get(annex,"RowCount"))!=67||Convert.ToInt32(Get(annex,"ColumnCount"))!=45)throw new InvalidOperationException();
 }
 private void EditAnnex12FixedInput(Control grid,object annex,int index){
  // Source template locations, zero based. Parent tax remains its source default 0.
  int[,] locations=new int[,]{{42,4},{42,9},{43,2},{43,12},{43,16},{43,17},{43,18},{43,20},{44,2},{44,12},{44,16},{44,17},{44,18},{44,20}};
  string[] inputs=new string[]{"NHA MAY GIA LAP - KHONG NOP","9999999997-001","Nơi có văn phòng điều hành nhà máy","Thành phố Hà Nội","Phường Sơn Tây","Thuế Thành phố Hà Nội","Thuế cơ sở 16 Thành phố Hà Nội","50","Nơi có nhà máy thủy điện (khác nơi có văn phòng điều hành)","Thành phố Hà Nội","Phường Sơn Tây","Thuế Thành phố Hà Nội","Thuế cơ sở 16 Thành phố Hà Nội","50"};
  if(index<0||index>=inputs.Length||index!=annex12InputActionCount)throw new InvalidOperationException();
  int row=locations[index,0],column=locations[index,1];string value=inputs[index];bool combo=column==2||column==12||column==16||column==17||column==18;
  grid.Focus();Annex12InputOwner(grid,annex);if(Convert.ToBoolean(Get(Cell(annex,row,column),"Locked")))throw new InvalidOperationException();
  stage="gtgt-annex12-input-editing";Record();annex.GetType().GetMethod("SetActiveCell",new Type[]{typeof(int),typeof(int)}).Invoke(annex,new object[]{row,column});
  grid.GetType().GetMethod("StartCellEditing",new Type[]{typeof(EventArgs),typeof(bool)}).Invoke(grid,new object[]{EventArgs.Empty,false});
  Control editor=Get(grid,"EditingControl") as Control;if(editor==null||!editor.Visible||!editor.Enabled)throw new InvalidOperationException();
  if(combo){
   // Same public vendor combo selection mechanism used by the synthetic profile.
   Control vendor=FindVendorCombo(editor,0);if(vendor==null)throw new InvalidOperationException();editorKind="combo";SetPublic(vendor,"DroppedDown",true);
   object list=Get(vendor,"List");System.Collections.IList sequence=list as System.Collections.IList;int count=sequence!=null?sequence.Count:Convert.ToInt32(Get(list,"Count"));
   if(count<1||count>4096)throw new InvalidOperationException();PropertyInfo item=list.GetType().GetProperty("Item",new Type[]{typeof(int)});if(item==null&&sequence==null)throw new InvalidOperationException();int selected=-1;
   for(int offset=0;offset<count;offset++){object entry=sequence!=null?sequence[offset]:item.GetValue(list,new object[]{offset});if(entry!=null&&entry.ToString()==value){if(selected>=0)throw new InvalidOperationException();selected=offset;}}
   if(selected<0)throw new InvalidOperationException();uint foregroundPid;GetWindowThreadProcessId(GetForegroundWindow(),out foregroundPid);if(foregroundPid!=(uint)Process.GetCurrentProcess().Id||OriginalMessageVisible())throw new InvalidOperationException();SetPublic(vendor,"SelectedIndex",selected);SetPublic(vendor,"DroppedDown",false);
  }else{
   editorKind=editor is TextBoxBase?"text-box":"other-control";editor.Focus();
   foreach(string keys in new string[]{"^a",EscapeSendKeys(value),"{TAB}"}){Annex12InputOwner(grid,annex);if(!editor.ContainsFocus)throw new InvalidOperationException();SendKeys.SendWait(keys);}
  }
  grid.GetType().GetMethod("StopCellEditing",Type.EmptyTypes).Invoke(grid,null);Application.DoEvents();grid.Focus();Annex12InputOwner(grid,annex);
  if(combo||column!=20){if(CellText(annex,row,column)!=value)throw new InvalidOperationException();}
  else{decimal actual;if(!Decimal.TryParse(Convert.ToString(Get(Cell(annex,row,column),"Value"),CultureInfo.InvariantCulture),NumberStyles.Number,CultureInfo.InvariantCulture,out actual)||actual!=50)throw new InvalidOperationException();}
  annex12InputActionCount++;Record();
 }
 private static bool Annex12NumberMatched(object sheet,int row,int column,decimal expected){decimal actual;return Decimal.TryParse(Convert.ToString(Get(Cell(sheet,row,column),"Value"),CultureInfo.InvariantCulture),NumberStyles.Number,CultureInfo.InvariantCulture,out actual)&&actual==expected;}
 private void InspectOriginalAnnex12Inputs(Control grid,object annex){
  if(annex12InputActionCount!=0)throw new InvalidOperationException();
  for(int index=0;index<14;index++)EditAnnex12FixedInput(grid,annex,index);
  annex12InputIdentityMatched=CellText(annex,42,4)=="NHA MAY GIA LAP - KHONG NOP"&&CellText(annex,42,9)=="9999999997-001";
  annex12InputReadOnlyIdentityMatched=true;
  for(int row=43;row<=44;row++)foreach(int column in new int[]{4,9})if(!Convert.ToBoolean(Get(Cell(annex,row,column),"Locked"))||CellText(annex,row,column)!=String.Empty)annex12InputReadOnlyIdentityMatched=false;
  annex12InputTypesMatched=CellText(annex,43,32)=="01"&&CellText(annex,44,32)=="02";
  annex12InputGeographyMatched=true;annex12InputTaxAuthoritiesMatched=true;
  for(int row=43;row<=44;row++){
   if(CellText(annex,row,33)!="101"||CellText(annex,row,42)!="10129087"||CellText(annex,row,12)!="Thành phố Hà Nội"||CellText(annex,row,16)!="Phường Sơn Tây")annex12InputGeographyMatched=false;
   if(CellText(annex,row,35)!="10100"||CellText(annex,row,36)!="10129"||CellText(annex,row,17)!="Thuế Thành phố Hà Nội"||CellText(annex,row,18)!="Thuế cơ sở 16 Thành phố Hà Nội")annex12InputTaxAuthoritiesMatched=false;
  }
  annex12InputPercentagesMatched=Annex12NumberMatched(annex,43,20,50)&&Annex12NumberMatched(annex,44,20,50)&&Annex12NumberMatched(annex,42,20,100);
  annex12InputZeroTaxMatched=true;int[,] zeros=new int[,]{{42,19},{42,23},{43,19},{43,23},{44,19},{44,23},{46,19},{46,23}};
  for(int index=0;index<zeros.GetLength(0);index++)if(!Annex12NumberMatched(annex,zeros[index,0],zeros[index,1],0))annex12InputZeroTaxMatched=false;
  if(mode=="gtgt-annex12-export-inspect"){StartOriginalAnnex12Export(grid,annex);return;}
  if(mode=="gtgt-annex12-numeric-inspect"){InspectOriginalAnnex12Numeric(grid,annex);return;}
  finished=true;stage="gtgt-annex12-input-inspected";Record();
 }

 private static bool Annex12CaptionMatched(string typeName,string uncheckedText,string checkedText){return typeName=="FarPoint.Win.Spread.CellType.CheckBoxCellType"&&uncheckedText=="01-2/GTGT"&&checkedText=="01-2/GTGT";}
 private void SelectOriginalAnnex12(Control grid,object sheet){
  if(!Annex12InspectionMode()||annex12SelectionActionCount!=0||annexSelected!=0||!periodNoAnnexMatched||!grid.Visible||!grid.Enabled||grid.FindForm()==null||!grid.FindForm().Enabled||OriginalMessageVisible())throw new InvalidOperationException();
  string root=Path.GetDirectoryName(project);
  annex12SourcePinsMatched=Hash(Path.Combine(root,"InterfaceTemplates/excel/01_GTGT_TT80_283.xls"))=="8ad9ec9f0f3462da75ce4e873e4bb60003947e9edd5d738a5055e37d6c73b310"&&Hash(Path.Combine(root,"InterfaceTemplates/xml/01_2_GTGT_TT80_283.xml"))=="9512dcfef9551892d132fd905250427c580a1320f77318ab048d6d26fd3a32e5"&&Hash(Path.Combine(root,"InterfaceTemplates/xml/01_2_GTGT_TT80_xml_283.xml"))=="9dafb55263fa2729383cf57bc73f3b97cf48dc9a28632a596806ad0afe8f17d3"&&Hash(Path.Combine(root,"InterfaceTemplates/Validate/01_GTGT_TT80_283.xsd"))=="8d4c0d88100e858ddfe221d080a6a338776d1364c7de04347bfb990d04833003";
  if((mode=="gtgt-annex12-input-inspect"||mode=="gtgt-annex12-numeric-inspect"||mode=="gtgt-annex12-export-inspect"))annex12SourcePinsMatched=annex12SourcePinsMatched&&Hash(Path.Combine(root,"InterfaceIni/DM_DUNG_CHUNG.xml"))=="cff4311dff86113853b2a70ca43992d72f4f5dd7ac643041e3d4d9ac2b1ba0b0";
  if(!annex12SourcePinsMatched)throw new InvalidOperationException();
  int rowCount=Convert.ToInt32(Get(sheet,"RowCount")),columnCount=Convert.ToInt32(Get(sheet,"ColumnCount")),target=-1;
  if(rowCount<1||rowCount>512||columnCount<1||columnCount>16)throw new InvalidOperationException();
  for(int row=0;row<rowCount;row++){object selector=Get(Cell(sheet,row,0),"CellType");if(selector==null||selector.GetType().FullName!="FarPoint.Win.Spread.CellType.CheckBoxCellType")continue;bool rowMatched=Annex12CaptionMatched(selector.GetType().FullName,Convert.ToString(Get(selector,"TextFalse"),CultureInfo.InvariantCulture),Convert.ToString(Get(selector,"TextTrue"),CultureInfo.InvariantCulture));if(rowMatched){if(target>=0)throw new InvalidOperationException();target=row;}}
  if(target<0||!RowVisible(sheet,target)||Selected(Get(Cell(sheet,target,0),"Value"))||Convert.ToBoolean(Get(Cell(sheet,target,0),"Locked")))throw new InvalidOperationException();
  object type=Get(Cell(sheet,target,0),"CellType");if(type==null||type.GetType().FullName!="FarPoint.Win.Spread.CellType.CheckBoxCellType")throw new InvalidOperationException();
  grid.Focus();sheet.GetType().GetMethod("SetActiveCell",new Type[]{typeof(int),typeof(int)}).Invoke(sheet,new object[]{target,0});
  uint pid;GetWindowThreadProcessId(GetForegroundWindow(),out pid);if(pid!=(uint)Process.GetCurrentProcess().Id||!grid.ContainsFocus)throw new InvalidOperationException();
  SendKeys.SendWait(" ");if(OriginalMessageVisible())throw new InvalidOperationException();
  annexSelected=0;for(int row=0;row<rowCount;row++)if(Selected(Get(Cell(sheet,row,0),"Value")))annexSelected++;
  periodAnnex12Matched=annexSelected==1&&Selected(Get(Cell(sheet,target,0),"Value"));periodNoAnnexMatched=false;
  if(!periodAnnex12Matched)throw new InvalidOperationException();annex12SelectionActionCount++;Record();
 }
 private void InspectOriginalAnnex12(Control grid){
  if(!gtgtSigner||!gtgtZero||gtgtEmptyMoney!=0||!Annex12InspectionMode()||!periodAnnex12Matched||!annex12SourcePinsMatched||annexSelected!=1||!grid.Visible||!grid.Enabled||grid.FindForm()==null||!grid.FindForm().Enabled||OriginalMessageVisible())throw new InvalidOperationException();
  object business=Global("InstanceClass");if(business==null||business.GetType().FullName!="TAX.HTKK.Business.Gtgt01TT80Nckt283"||!Convert.ToBoolean(Get(Get(grid,"ActiveSheet"),"AutoCalculation"))){stage="waiting-gtgt-sheet";Record();return;}
  object sheets=Get(grid,"Sheets");int count=Convert.ToInt32(Get(sheets,"Count"));if(count!=11)throw new InvalidOperationException();
  PropertyInfo item=sheets.GetType().GetProperty("Item",new Type[]{typeof(int)});if(item==null)throw new InvalidOperationException();int found=-1;object annex=null;
  for(int index=0;index<count;index++){object candidate=item.GetValue(sheets,new object[]{index});string name=Convert.ToString(Get(candidate,"SheetName"),CultureInfo.InvariantCulture);if(name=="01_2"||name=="01-2/GTGT"){if(found>=0)throw new InvalidOperationException();found=index;annex=candidate;}}
  if(found<0)throw new InvalidOperationException();
  PropertyInfo active=grid.GetType().GetProperty("ActiveSheetIndex");if(active==null||!active.CanWrite)throw new InvalidOperationException();if(Convert.ToInt32(active.GetValue(grid,null))!=found)active.SetValue(grid,found,null);
  if(Get(grid,"ActiveSheet")!=annex||OriginalMessageVisible())throw new InvalidOperationException();
  annex12SheetRows=Convert.ToInt32(Get(annex,"RowCount"));annex12SheetColumns=Convert.ToInt32(Get(annex,"ColumnCount"));if(annex12SheetRows<46||annex12SheetRows>10000||annex12SheetColumns<43||annex12SheetColumns>512)throw new InvalidOperationException();annex12SheetObserved=true;
  annex12SttMatched=CellText(annex,42,1)=="1"&&CellText(annex,43,1)=="1.1";annex12LocksMatched=true;
  int[,] cells=new int[,]{{42,4},{42,9},{42,19},{42,20},{42,23},{43,19},{43,20},{43,23},{45,19},{45,23}};bool[] locks=new bool[]{false,false,false,true,true,true,false,true,true,true};
  for(int index=0;index<cells.GetLength(0);index++)if(Convert.ToBoolean(Get(Cell(annex,cells[index,0],cells[index,1]),"Locked"))!=locks[index])annex12LocksMatched=false;
  cells=new int[,]{{42,19},{42,20},{42,23},{43,19},{43,20},{43,23},{45,19},{45,23}};annex12NumericCount=0;annex12NumericEmptyMask=0;annex12NumericNonzeroMask=0;
  for(int index=0;index<cells.GetLength(0);index++){object raw=Get(Cell(annex,cells[index,0],cells[index,1]),"Value");decimal number;annex12NumericCount++;if(raw==null||raw==DBNull.Value||Convert.ToString(raw,CultureInfo.InvariantCulture)==String.Empty){annex12NumericEmptyMask|=1<<index;continue;}if(!Decimal.TryParse(Convert.ToString(raw,CultureInfo.InvariantCulture),NumberStyles.Number,CultureInfo.InvariantCulture,out number))throw new InvalidOperationException();if(number!=Decimal.Zero)annex12NumericNonzeroMask|=1<<index;}
  stage="gtgt-annex12-sheet-metadata";Record();System.Collections.IList infos=Get(Global("ToKhaiInfo"),"SheetInfos") as System.Collections.IList;if(infos==null||infos.Count>32)throw new InvalidOperationException();object info=null;
  foreach(object candidate in infos)if(candidate!=null&&Convert.ToString(Get(candidate,"SheetID"),CultureInfo.InvariantCulture)=="01_2"){if(info!=null)throw new InvalidOperationException();info=candidate;}
  if(info==null)throw new InvalidOperationException();stage="gtgt-annex12-table-metadata";Record();System.Collections.IList tables=Get(info,"Tables") as System.Collections.IList;if(tables==null||tables.Count<1||tables.Count>512)throw new InvalidOperationException();annex12GroupCount=tables.Count;
  object first=tables[0];string id=Convert.ToString(Get(first,"TableID"),CultureInfo.InvariantCulture);if(id.Length<1||id.Length>5)throw new InvalidOperationException();foreach(char character in id)if(character<'0'||character>'9')throw new InvalidOperationException();if(!Int32.TryParse(id,NumberStyles.None,CultureInfo.InvariantCulture,out annex12FirstGroupId)||annex12FirstGroupId<1||annex12FirstGroupId>10000||id!=annex12FirstGroupId.ToString(CultureInfo.InvariantCulture))throw new InvalidOperationException();
  stage="gtgt-annex12-row-metadata";Record();System.Collections.IList values=Get(first,"RowsValues") as System.Collections.IList;if(values==null||values.Count>10000)throw new InvalidOperationException();annex12FirstGroupRows=values.Count;
  annex12GroupMetadataMatched=Selected(Get(info,"Active"))&&Convert.ToString(Get(first,"TableName"),CultureInfo.InvariantCulture)=="01_2_GTGT"&&Convert.ToString(Get(first,"TablePath"),CultureInfo.InvariantCulture)=="PLuc_01_2_GTGT/TenNhaMay";
  annex12StructureMatched=annex12SttMatched&&annex12LocksMatched&&annex12NumericCount==8&&annex12NumericNonzeroMask==0&&annex12GroupMetadataMatched;
  if((mode=="gtgt-annex12-row-inspect"||mode=="gtgt-annex12-input-inspect"||mode=="gtgt-annex12-numeric-inspect"||mode=="gtgt-annex12-export-inspect")){InspectOriginalAnnex12Row(grid,annex);return;}
  finished=true;stage="gtgt-annex12-inspected";Record();
 }

 private bool QuarterCase(){return webCaseId=="01GTGT-zero-Q4-2026";}
 private bool NoActivityCase(){return webCaseId=="01GTGT-noactivity-zero-M10-2026"||webCaseId=="01GTGT-noactivity-reset-sale10-M10-2026"||webCaseId=="01GTGT-noactivity-cancel-sale10-M10-2026"||webCaseId=="01GTGT-noactivity-uncheck-sale10-M10-2026"||webCaseId=="01GTGT-noactivity-keep-credit-M10-2026";}
 private bool CancelCt21Case(){return webCaseId=="01GTGT-noactivity-cancel-sale10-M10-2026";}
 private bool UncheckCt21Case(){return webCaseId=="01GTGT-noactivity-uncheck-sale10-M10-2026";}
 private bool CreditCt21Case(){return webCaseId=="01GTGT-noactivity-keep-credit-M10-2026";}
 private bool SaleBeforeCt21Case(){return webCaseId=="01GTGT-noactivity-reset-sale10-M10-2026"||CancelCt21Case()||UncheckCt21Case();}
 private bool InspectCt21State(object sheet,bool selected,bool locked){
  gtgtCt21CaseMatched=Selected(Get(Cell(sheet,35,8),"Value"))==selected;gtgtCt21LocksMatched=true;
  int[,] cells=new int[,] {{39,9},{39,11},{40,9},{40,11},{41,11},{43,9},{45,9},{46,9},{46,11},{47,9},{47,11},{48,9}};
  for(int index=0;index<cells.GetLength(0);index++)if(Convert.ToBoolean(Get(Cell(sheet,cells[index,0],cells[index,1]),"Locked"))!=locked)gtgtCt21LocksMatched=false;
  return gtgtCt21CaseMatched&&gtgtCt21LocksMatched;
 }
 private bool InspectCt21Case(object sheet){
  if(!NoActivityCase())return true;
  bool selected=!CancelCt21Case()&&!UncheckCt21Case();
  return InspectCt21State(sheet,selected,selected)&&gtgtCt21ConfirmationMatched&&(!UncheckCt21Case()||gtgtCt21UncheckMatched);
 }
 private void ActivateOriginalCt21(Control grid,object sheet){
  if(!NoActivityCase()||noActivityCheckboxActivated||!webInputVerified||!gtgtCt21||Selected(Get(Cell(sheet,35,8),"Value"))||Convert.ToBoolean(Get(Cell(sheet,35,8),"Locked"))||!grid.Visible||!grid.Enabled||grid.FindForm()==null||grid.FindForm().GetType().FullName!="HTKK.frmWinToKhai"||!grid.FindForm().Enabled||OriginalMessageVisible())throw new InvalidOperationException();
  object type=Get(Cell(sheet,35,8),"CellType");if(type==null||type.GetType().FullName!="FarPoint.Win.Spread.CellType.CheckBoxCellType")throw new InvalidOperationException();
  noActivityCheckboxActivated=true;stage="gtgt-noactivity-checkbox-activating";Record();
  grid.Focus();sheet.GetType().GetMethod("SetActiveCell",new Type[]{typeof(int),typeof(int)}).Invoke(sheet,new object[]{35,8});
  uint foregroundPid;GetWindowThreadProcessId(GetForegroundWindow(),out foregroundPid);if(foregroundPid!=(uint)Process.GetCurrentProcess().Id||!grid.ContainsFocus)throw new InvalidOperationException();
  Exception modalFailure=null;Stopwatch clock=Stopwatch.StartNew();bool selected=!CancelCt21Case();
  using(System.Windows.Forms.Timer observer=new System.Windows.Forms.Timer()){
   observer.Interval=50;observer.Tick+=delegate(object sender,EventArgs args){try{if(clock.Elapsed.TotalSeconds>5)throw new InvalidOperationException();AcknowledgeOriginalCt21Choice();}catch(Exception error){modalFailure=error;observer.Stop();}};
   observer.Start();try{
    // SPACE runs the original checkbox event; only the exact owned Yes/No
    // dialog is acknowledged. The case fixes the choice before original input.
    SendKeys.SendWait(" ");
    while((!gtgtCt21ConfirmationMatched||!InspectCt21State(sheet,selected,selected))&&modalFailure==null&&clock.Elapsed.TotalSeconds<5){Application.DoEvents();System.Threading.Thread.Sleep(10);}
   }finally{observer.Stop();}
  }
  if(modalFailure!=null||!gtgtCt21ConfirmationMatched||!InspectCt21State(sheet,selected,selected))throw new InvalidOperationException();
  webCaseEditCount++;webCaseEditClock=Stopwatch.StartNew();Record();
 }
 private void UncheckOriginalCt21(Control grid,object sheet){
  if(!UncheckCt21Case()||gtgtCt21UncheckMatched||webCaseEditCount!=2||!gtgtCt21ConfirmationMatched||!InspectCt21State(sheet,true,true)||OriginalMessageVisible()||!grid.Enabled||!grid.Visible||grid.FindForm()==null||!grid.FindForm().Enabled||grid.FindForm().GetType().FullName!="HTKK.frmWinToKhai")throw new InvalidOperationException();
  object type=Get(Cell(sheet,35,8),"CellType");if(type==null||type.GetType().FullName!="FarPoint.Win.Spread.CellType.CheckBoxCellType"||Convert.ToBoolean(Get(Cell(sheet,35,8),"Locked")))throw new InvalidOperationException();
  grid.Focus();sheet.GetType().GetMethod("SetActiveCell",new Type[]{typeof(int),typeof(int)}).Invoke(sheet,new object[]{35,8});
  uint pid;GetWindowThreadProcessId(GetForegroundWindow(),out pid);if(pid!=(uint)Process.GetCurrentProcess().Id||!grid.ContainsFocus)throw new InvalidOperationException();
  stage="gtgt-noactivity-checkbox-unchecking";Record();SendKeys.SendWait(" ");
  Stopwatch clock=Stopwatch.StartNew();while(!InspectCt21State(sheet,false,false)&&clock.Elapsed.TotalSeconds<2){if(OriginalMessageVisible())throw new InvalidOperationException();Application.DoEvents();System.Threading.Thread.Sleep(10);}
  if(!InspectCt21State(sheet,false,false)||OriginalMessageVisible())throw new InvalidOperationException();
  gtgtCt21UncheckMatched=true;webCaseEditCount++;webCaseEditClock=Stopwatch.StartNew();Record();
 }
 private void AcknowledgeOriginalCt21Choice(){
  if(gtgtCt21ConfirmationMatched)return;
  const string expected="NNT chỉ được kê khai các chỉ tiêu: [22], [37], [38], [39a], [40b], [42]. Các chỉ tiêu còn lại khóa không cho kê khai. Bạn có tiếp tục thực hiện không?";
  List<IntPtr> dialogs=new List<IntPtr>();uint own=(uint)Process.GetCurrentProcess().Id;
  EnumWindows(delegate(IntPtr window,IntPtr unused){uint pid;GetWindowThreadProcessId(window,out pid);if(pid==own&&IsWindowVisible(window)&&NativeText(window,true)=="#32770")dialogs.Add(window);return true;},IntPtr.Zero);
  if(dialogs.Count==0)return;if(dialogs.Count!=1)throw new InvalidOperationException();IntPtr dialog=dialogs[0];uint ownerPid;IntPtr owner=GetWindow(dialog,4);
  if(NativeText(dialog,false)!="Thong bao"||owner==IntPtr.Zero||GetWindowThreadProcessId(owner,out ownerPid)==0||ownerPid!=own||GetForegroundWindow()!=dialog)throw new InvalidOperationException();
  int messages=0,buttons=0;EnumChildWindows(dialog,delegate(IntPtr child,IntPtr unused){if(IsWindowVisible(child)){if(NativeText(child,true)=="Static"&&NativeText(child,false)==expected)messages++;if(NativeText(child,true)=="Button")buttons++;}return true;},IntPtr.Zero);
  IntPtr yes=GetDlgItem(dialog,6),no=GetDlgItem(dialog,7);
  if(messages!=1||buttons!=2||yes==IntPtr.Zero||no==IntPtr.Zero||NativeText(yes,true)!="Button"||NativeText(no,true)!="Button"||!IsWindowVisible(yes)||!IsWindowEnabled(yes)||!IsWindowVisible(no)||!IsWindowEnabled(no))throw new InvalidOperationException();
  gtgtCt21ConfirmationMatched=true;stage="gtgt-noactivity-confirming";Record();if(!PostMessage(CancelCt21Case()?no:yes,245,IntPtr.Zero,IntPtr.Zero))throw new InvalidOperationException();
 }
 private string SheetJson(){
  string q=((char)34).ToString();string[] names=new string[]{"periodYearMonthMatched","periodFirstDeclarationMatched","periodActivityMatched","periodGeographyMatched","periodNoAnnexMatched","periodConfirmInvoked","gtgtWorkbookPinsVerified","gtgtMenuVersionMatched","gtgtPeriodModelMatched","gtgtSheetObserved","gtgtSheetNameMatched","gtgtDimensionsMatched","gtgtIdentityMatched","gtgtCt21Ready","gtgtSignatureReady","gtgtMonetaryZero"};
  bool[] values=new bool[]{periodDateMatched,periodFirstMatched,periodActivityMatched,periodGeographyMatched,periodNoAnnexMatched,periodConfirmInvoked,gtgtPins,gtgtVersion,gtgtPeriod,gtgtSheet,gtgtName,gtgtDimensions,gtgtIdentity,gtgtCt21,gtgtSigner,gtgtZero};StringBuilder json=new StringBuilder();
  for(int index=0;index<names.Length;index++)json.Append(","+q+names[index]+q+":"+Bool(values[index]));
  json.Append(","+q+"gtgtCt42BeforeExportObserved"+q+":"+Bool(gtgtCt42BeforeExportObserved)+","+q+"gtgtCt42LockedBeforeExport"+q+":"+Bool(gtgtCt42LockedBeforeExport)+","+q+"gtgtCt42AfterImportObserved"+q+":"+Bool(gtgtCt42AfterImportObserved)+","+q+"gtgtCt42LockedAfterImport"+q+":"+Bool(gtgtCt42LockedAfterImport));
  json.Append(","+q+"gtgtCt21CaseMatched"+q+":"+Bool(gtgtCt21CaseMatched)+","+q+"gtgtCt21ConfirmationMatched"+q+":"+Bool(gtgtCt21ConfirmationMatched)+","+q+"gtgtCt21LocksMatched"+q+":"+Bool(gtgtCt21LocksMatched)+","+q+"gtgtCt21BeforeExportMatched"+q+":"+Bool(gtgtCt21BeforeExportMatched)+","+q+"gtgtCt21AfterImportMatched"+q+":"+Bool(gtgtCt21AfterImportMatched)+","+q+"gtgtCt21UncheckMatched"+q+":"+Bool(gtgtCt21UncheckMatched));
  json.Append(","+q+"gtgtAutoCalculationReady"+q+":"+Bool(gtgtAutoCalculationReady)+","+q+"gtgtBusinessInstanceMatched"+q+":"+Bool(gtgtBusinessInstanceMatched));
  json.Append(","+q+"gtgtCaseMoneyMatched"+q+":"+Bool(gtgtCaseMoneyMatched)+","+q+"gtgtCt42Locked"+q+":"+Bool(gtgtCt42Locked)+","+q+"gtgtCaseMoneyCount"+q+":"+gtgtCaseMoneyCount+","+q+"gtgtCaseMismatchMask"+q+":"+gtgtCaseMismatchMask+","+q+"gtgtCaseNonzeroMask"+q+":"+gtgtCaseNonzeroMask);
  json.Append(","+q+"annexSelectedCount"+q+":"+annexSelected+","+q+"gtgtSheetRows"+q+":"+gtgtRows+","+q+"gtgtSheetColumns"+q+":"+gtgtColumns+","+q+"gtgtSheetCount"+q+":"+gtgtSheets+","+q+"gtgtEmptyMonetaryCount"+q+":"+gtgtEmptyMoney);return json.ToString()+Annex12Json()+AmendmentJson();
 }
 private static Control ReadableNamed(Control root,string name){Control[] controls=root.Controls.Find(name,true);if(controls.Length!=1||!controls[0].Visible)throw new InvalidOperationException();return controls[0];}
 private static Control Named(Control root,string name){Control control=ReadableNamed(root,name);if(!control.Enabled)throw new InvalidOperationException();return control;}
 private static bool CheckValue(Control control){RadioButton radio=control as RadioButton;if(radio!=null)return radio.Checked;CheckBox check=control as CheckBox;if(check!=null)return check.Checked;throw new InvalidOperationException();}
 private static void SetCheck(Control control,bool value){RadioButton radio=control as RadioButton;if(radio!=null){radio.Checked=value;return;}CheckBox check=control as CheckBox;if(check!=null){check.Checked=value;return;}throw new InvalidOperationException();}
 private static void SetText(Control root,string name,string value){TextBoxBase input=Named(root,name) as TextBoxBase;if(input==null)throw new InvalidOperationException();input.Focus();input.Text=value;if(input.Text!=value)throw new InvalidOperationException();}
 private static bool SelectGeography(Control root,string name,string code,string label,string codeProperty,string labelProperty){
  ComboBox combo=ReadableNamed(root,name) as ComboBox;if(combo==null)throw new InvalidOperationException();
  // ORIGINAL ShowDetailpnTinhCQT binds human-label string lists, not Key/Value
  // items. ORIGINAL SelectedIndexChanged resolves those labels to period codes.
  // Never write SelectedValue=code: that transiently deselects these source lists.
  // Focus commits the original mskMonth.Leave handler before resolving items.
  if(combo.Enabled){combo.Focus();if(!combo.Visible||combo.IsDisposed)return false;}
  int selected=-1;for(int index=0;index<combo.Items.Count&&index<4096;index++){if(combo.GetItemText(combo.Items[index])==label){if(selected>=0)throw new InvalidOperationException();selected=index;}}
  if(selected<0)return false;
  if(combo.Enabled){if(combo.SelectedIndex!=selected)combo.SelectedIndex=selected;}
  else if(combo.SelectedIndex!=selected)return false;
  object currentPeriod=Global("TTPeriodInfo");
  return combo.Text==label&&Convert.ToString(Get(currentPeriod,codeProperty),CultureInfo.InvariantCulture)==code&&Convert.ToString(Get(currentPeriod,labelProperty),CultureInfo.InvariantCulture)==label;
 }
 private bool SelectSourceActivity(Control period){
  const string label="Hoạt động sản xuất kinh doanh thông thường";
  string file=Path.Combine(Path.GetDirectoryName(project),"InterfaceIni/Catalogue_DM_NNKD.xml");
  if(new FileInfo(file).Length>2000000||Hash(file)!="8e19468e899e1b6e35a9d584dddd5e278c0daf1127d4f14ac5c4e03b3164ea88")return false;
  XmlReaderSettings settings=new XmlReaderSettings();settings.ProhibitDtd=true;settings.XmlResolver=null;XmlDocument document=new XmlDocument();document.XmlResolver=null;
  using(XmlReader reader=XmlReader.Create(file,settings)){document.Load(reader);}int sourceMatches=0;
  foreach(XmlNode item in document.SelectNodes("//Item[@Value]")){if(item.Attributes["Value"].Value=="01_GTGT_TT80###00###"+label)sourceMatches++;}
  if(sourceMatches!=1)return false;
  // ControlInit builds dictionary Key=source item[1], Value=source item[2].
  // TT80 internal catalogue ID is 00; 1701 belongs to the older 01_GTGT group/tax code.
  ComboBox combo=ReadableNamed(period,"cboNganhKD") as ComboBox;if(combo==null||combo.DisplayMember!="Value"||combo.ValueMember!="Key")return false;
  int selected=-1;for(int index=0;index<combo.Items.Count&&index<4096;index++){if(combo.GetItemText(combo.Items[index])==label){if(selected>=0)return false;selected=index;}}
  if(selected<0)return false;if(combo.SelectedIndex!=selected){if(!combo.Enabled)return false;combo.SelectedIndex=selected;}
  return Convert.ToString(combo.SelectedValue,CultureInfo.InvariantCulture)=="00";
 }
 private static bool Selected(object value){
  if(value==null||value==DBNull.Value)return false;if(value is bool)return (bool)value;
  string text=Convert.ToString(value,CultureInfo.InvariantCulture);if(text==String.Empty||text=="False"||text=="0")return false;if(text=="True"||text=="1")return true;throw new InvalidOperationException();
 }
 private static Assembly OriginalAssembly(){
  foreach(Assembly assembly in AppDomain.CurrentDomain.GetAssemblies()){if(assembly.GetName().Name=="HTKK")return assembly;}throw new InvalidOperationException();
 }
 private static object Global(string name){Type settings=OriginalAssembly().GetType("HTKK.WinSettings",true);FieldInfo field=settings.GetField(name,BindingFlags.Public|BindingFlags.NonPublic|BindingFlags.Static);if(field==null)throw new InvalidOperationException();return field.GetValue(null);}
 private void ConfigureOriginalGtgtPeriod(Control period){
  stage="gtgt-period-configuring";Record();
  if(Convert.ToString(Global("MenuID"),CultureInfo.InvariantCulture)!="D1")throw new InvalidOperationException();
  if(mode=="gtgt-web-import-inspect"&&!webInputVerified)VerifyOwnWebInput();
  SetCheck(Named(period,QuarterCase()?"chkTKQuy":"chkTkhaiThang"),true);SetCheck(Named(period,"OptChinhthuc"),true);
  periodFirstMatched=CheckValue(Named(period,"OptChinhthuc"))&&!CheckValue(ReadableNamed(period,"OptBosung"));
  SetText(period,"mskYear","2026");if(QuarterCase()){ComboBox quarter=Named(period,"cbbQuy") as ComboBox;if(quarter==null)throw new InvalidOperationException();int index=quarter.FindStringExact("4");if(index<0)throw new InvalidOperationException();quarter.SelectedIndex=index;if(Convert.ToString(quarter.SelectedItem,CultureInfo.InvariantCulture)!="4")throw new InvalidOperationException();}else SetText(period,"mskMonth","10");
  periodDateMatched=Named(period,"mskYear").Text=="2026"&&(QuarterCase()?CheckValue(Named(period,"chkTKQuy"))&&!CheckValue(ReadableNamed(period,"chkTkhaiThang")):Named(period,"mskMonth").Text=="10"&&CheckValue(Named(period,"chkTkhaiThang"))&&!CheckValue(ReadableNamed(period,"chkTKQuy")));
  periodDescriptions.Clear();periodControlCount=0;int currentControlCount=0;DescribePeriod(period,ref currentControlCount);
  stage="gtgt-period-province-selecting";Record();bool provinceMatched=SelectGeography(period,"cboTinh","101","Thành phố Hà Nội","MaTinh","TenTinh");
  stage="gtgt-period-ward-selecting";Record();bool wardMatched=SelectGeography(period,"cboXa","10129087","Phường Sơn Tây","MaXa","TenXa");
  stage="gtgt-period-taxhead-selecting";Record();bool taxHeadMatched=SelectGeography(period,"cboCQTCuc","10100","Thuế Thành phố Hà Nội","maCQTCapCuc","tenCQTCapCuc");
  stage="gtgt-period-taxlocal-selecting";Record();bool taxLocalMatched=SelectGeography(period,"cboCQTChiCuc","10129","Thuế cơ sở 16 Thành phố Hà Nội","maCQTQuanLy","tenCQTQuanLy");
  periodGeographyMatched=provinceMatched&&wardMatched&&taxHeadMatched&&taxLocalMatched;
  stage="gtgt-period-activity-selecting";Record();periodActivityMatched=SelectSourceActivity(period);
  // Exercise the ORIGINAL select-all/clear-all control, preserving its locked-row rules.
  Control all=ReadableNamed(period,"chkChonPhuLucKeKhaiAll");if(all.Enabled){SetCheck(all,true);SetCheck(all,false);}
  Control annex=ReadableNamed(period,"axfpsPhuLuc");if(!IsSpread(annex))throw new InvalidOperationException();object annexSheet=Get(annex,"ActiveSheet");int annexRows=Convert.ToInt32(Get(annexSheet,"RowCount"));if(annexRows<0||annexRows>512)throw new InvalidOperationException();annexSelected=0;
  for(int row=0;row<annexRows;row++)if(Selected(Get(Cell(annexSheet,row,0),"Value")))annexSelected++;
  periodNoAnnexMatched=annexSelected==0&&!CheckValue(all);
  if(Annex12InspectionMode())SelectOriginalAnnex12(annex,annexSheet);
  if(AmendmentReopening()){ConfigureOriginalAmendmentOpen(period);return;}
  if(!periodDateMatched||!periodFirstMatched||!periodGeographyMatched||!periodActivityMatched||!(Annex12InspectionMode()?periodAnnex12Matched:periodNoAnnexMatched)){stage="gtgt-period-inputs-not-matched";finished=true;Record();return;}
  Button confirm=Named(period,"btnDongY") as Button;if(confirm==null||confirm.Text.Replace("&",String.Empty).Trim()!="Đồng ý")throw new InvalidOperationException();
  navigationPhase="waiting-gtgt-sheet";stage="gtgt-period-confirm-invoking";periodConfirmInvoked=true;Record();
  // Original OpenToKhai uses ShowDialog. This timer observes its real sheet inside
  // that nested ORIGINAL message loop, without closing or bypassing any validator.
  using(System.Windows.Forms.Timer watcher=new System.Windows.Forms.Timer()){
   watcher.Interval=100;watcher.Tick+=delegate(object sender,EventArgs args){try{InspectOriginalGtgtSheet();if(finished)watcher.Stop();}catch(Exception error){watcher.Stop();Failure(error);}};
   watcher.Start();try{confirm.PerformClick();}finally{watcher.Stop();}
  }
  if(!finished){stage="waiting-gtgt-sheet";Record();}
 }
 private static void FindWorksheets(Control root,List<Form> forms,ref int visited){
  if(++visited>512)return;Form form=root as Form;if(form!=null&&form.Visible&&!form.IsDisposed&&form.GetType().FullName=="HTKK.frmWinToKhai"&&!forms.Contains(form))forms.Add(form);
  foreach(Control child in root.Controls){if(visited>=512)break;FindWorksheets(child,forms,ref visited);}
 }
 private void InspectOriginalGtgtSheet(){if(gtgtSheetInspectionBusy)return;gtgtSheetInspectionBusy=true;try{InspectOriginalGtgtSheetCore();}finally{gtgtSheetInspectionBusy=false;}}
 private void InspectOriginalGtgtSheetCore(){
  if(finished||exportStarted)return;
  List<Form> forms=new List<Form>();int visited=0;foreach(Form top in Application.OpenForms){if(visited>=512)break;if(top.Visible&&!top.IsDisposed)FindWorksheets(top,forms,ref visited);}
  if(forms.Count!=1){stage="waiting-gtgt-sheet";Record();return;}
  List<Control> grids=new List<Control>();visited=0;GatherSpreads(forms[0],grids,ref visited);if(grids.Count!=1){stage="waiting-gtgt-sheet";Record();return;}
  Control grid=grids[0];object sheet=Get(grid,"ActiveSheet");gtgtRows=Convert.ToInt32(Get(sheet,"RowCount"));gtgtColumns=Convert.ToInt32(Get(sheet,"ColumnCount"));gtgtSheets=Convert.ToInt32(Get(Get(grid,"Sheets"),"Count"));
  if(gtgtRows<67||gtgtColumns<15){stage="waiting-gtgt-sheet";Record();return;}
  gtgtSheet=true;gtgtDimensions=gtgtRows==72&&gtgtColumns==24;string sheetName=Convert.ToString(Get(sheet,"SheetName"),CultureInfo.InvariantCulture);gtgtName=sheetName=="01"||sheetName=="Tờ khai";
  string root=Path.GetDirectoryName(project);
  gtgtPins=Hash(Path.Combine(root,"InterfaceTemplates/excel/01_GTGT_TT80_283.xls"))=="8ad9ec9f0f3462da75ce4e873e4bb60003947e9edd5d738a5055e37d6c73b310"&&Hash(Path.Combine(root,"InterfaceTemplates/xml/01_GTGT_TT80_283.xml"))=="40f5d6f711f7acb69dcc4098e3e3bb0b1849224d1c185902a50b8cae6fc50aae"&&Hash(Path.Combine(root,"InterfaceTemplates/xml/01_GTGT_TT80_xml_283.xml"))=="7ba334067c52ea22cd744dcf2c0ff444190d6661f6b3e9b3ea08e5ead574830c";
  gtgtVersion=Convert.ToString(Global("MenuID"),CultureInfo.InvariantCulture)=="D1"&&Convert.ToString(Get(Global("ToKhaiInfo"),"VersionXML"),CultureInfo.InvariantCulture)=="2.8.3";
  object currentPeriod=Global("TTPeriodInfo");gtgtPeriod=Convert.ToString(Get(currentPeriod,"KieuKy"),CultureInfo.InvariantCulture)==(QuarterCase()?"Q":"M")&&Convert.ToString(Get(currentPeriod,"Nam"),CultureInfo.InvariantCulture)=="2026"&&Convert.ToString(Get(currentPeriod,QuarterCase()?"Quy":"Thang"),CultureInfo.InvariantCulture)==(QuarterCase()?"4":"10")&&Convert.ToString(Get(currentPeriod,"LoaiToKhai"),CultureInfo.InvariantCulture)=="C";
  gtgtIdentity=CellText(sheet,9,3)==FakeName&&CellText(sheet,10,3).Replace("-",String.Empty)==Mst;gtgtSigner=CellText(sheet,63,10)==FakeSigner;
  object checkbox=Cell(sheet,35,8),cellType=Get(checkbox,"CellType");if(!noActivityCheckboxActivated)gtgtCt21=cellType!=null&&cellType.GetType().FullName=="FarPoint.Win.Spread.CellType.CheckBoxCellType"&&!Convert.ToBoolean(Get(checkbox,"Locked"))&&!Selected(Get(checkbox,"Value"));
  InspectMoneyZero(sheet);
  bool matched=gtgtPins&&gtgtVersion&&gtgtPeriod&&gtgtName&&gtgtDimensions&&gtgtIdentity&&gtgtCt21;
  if(gtgtObservationClock==null)gtgtObservationClock=Stopwatch.StartNew();
  // Original load may pump a progress form while sheet binding is still in flight.
  if(!matched&&gtgtObservationClock.Elapsed.TotalSeconds<2){stage="waiting-gtgt-sheet";Record();return;}
  if(matched&&AmendmentInspectionMode()){StartOriginalAmendmentPriorSave(forms[0],grid,sheet);return;}
  if(matched&&Annex12InspectionMode()){InspectOriginalAnnex12(grid);return;}
  if(matched&&mode=="gtgt-web-import-inspect"){
   gtgtAutoCalculationReady=Convert.ToBoolean(Get(sheet,"AutoCalculation"));object business=Global("InstanceClass");gtgtBusinessInstanceMatched=business!=null&&business.GetType().FullName=="TAX.HTKK.Business.Gtgt01TT80Nckt283";
   if(!gtgtAutoCalculationReady||!gtgtBusinessInstanceMatched||!forms[0].Enabled||!grid.Enabled||OriginalMessageVisible()){stage="waiting-gtgt-sheet";Record();return;}
   if(!webInputVerified)VerifyOwnWebInput();
   gtgtCt42Locked=Convert.ToBoolean(Get(Cell(sheet,60,11),"Locked"));
   bool fivePercent=webCaseId=="01GTGT-sale5-half-M10-2026"||webCaseId=="01GTGT-sale5-manual-M10-2026";int caseRow=fivePercent?46:47;
   if(webCaseId!="01GTGT-zero-M10-2026"&&!QuarterCase()&&webCaseId!="01GTGT-noactivity-zero-M10-2026"&&!webCaseEdited){
    if(!gtgtZero||gtgtEmptyMoney!=0||gtgtCt42Locked||Convert.ToBoolean(Get(Cell(sheet,caseRow,9),"Locked")))throw new InvalidOperationException();
    webCaseEdited=true;webCaseEditClock=Stopwatch.StartNew();if(CreditCt21Case()){Edit(grid,sheet,36,11,"7",false,"gtgt-case-editing",false);return;}Edit(grid,sheet,caseRow,9,webCaseId=="01GTGT-sale5-half-M10-2026"?"10":webCaseId=="01GTGT-sale10-half-M10-2026"?"5":"1000000",false,"gtgt-case-editing",false);return;
   }
   if((webCaseId=="01GTGT-sale10-manual-M10-2026"||webCaseId=="01GTGT-sale5-manual-M10-2026")&&webCaseEditCount==1){
    decimal suggested;if(Convert.ToBoolean(Get(Cell(sheet,caseRow,11),"Locked"))||!Decimal.TryParse(Convert.ToString(Get(Cell(sheet,caseRow,11),"Value"),CultureInfo.InvariantCulture),NumberStyles.Number,CultureInfo.InvariantCulture,out suggested)||suggested!=(fivePercent?50000:100000)){if(webCaseEditClock.Elapsed.TotalSeconds<2){stage="waiting-gtgt-sheet";Record();return;}throw new InvalidOperationException();}
    webCaseEditClock=Stopwatch.StartNew();Edit(grid,sheet,caseRow,11,"7",false,"gtgt-case-editing",false);return;
   }
   if(NoActivityCase()&&!noActivityCheckboxActivated){
    if(SaleBeforeCt21Case()){
     decimal baseValue,taxValue;if(webCaseEditCount!=1||!Decimal.TryParse(Convert.ToString(Get(Cell(sheet,47,9),"Value"),CultureInfo.InvariantCulture),NumberStyles.Number,CultureInfo.InvariantCulture,out baseValue)||baseValue!=1000000||!Decimal.TryParse(Convert.ToString(Get(Cell(sheet,47,11),"Value"),CultureInfo.InvariantCulture),NumberStyles.Number,CultureInfo.InvariantCulture,out taxValue)||taxValue!=100000){if(webCaseEditClock!=null&&webCaseEditClock.Elapsed.TotalSeconds<2){stage="waiting-gtgt-sheet";Record();return;}throw new InvalidOperationException();}
    }else if(CreditCt21Case()){decimal credit;if(webCaseEditCount!=1||!Decimal.TryParse(Convert.ToString(Get(Cell(sheet,36,11),"Value"),CultureInfo.InvariantCulture),NumberStyles.Number,CultureInfo.InvariantCulture,out credit)||credit!=7)throw new InvalidOperationException();}
    else if(!gtgtZero||gtgtEmptyMoney!=0||webCaseEditCount!=0)throw new InvalidOperationException();
    ActivateOriginalCt21(grid,sheet);return;
   }
   if(UncheckCt21Case()&&!gtgtCt21UncheckMatched){UncheckOriginalCt21(grid,sheet);return;}
   if(!InspectCt21Case(sheet))throw new InvalidOperationException();if(NoActivityCase())gtgtCt21BeforeExportMatched=true;
   InspectCaseMoney(sheet);
   if(!gtgtCaseMoneyMatched){if(webCaseEditClock!=null&&webCaseEditClock.Elapsed.TotalSeconds<2){stage="waiting-gtgt-sheet";Record();return;}throw new InvalidOperationException();}
  }else InspectCaseMoney(sheet);
  if(matched&&(mode=="gtgt-export-inspect"||mode=="gtgt-roundtrip-inspect"||mode=="gtgt-web-import-inspect")){StartOriginalGtgtExport(forms[0]);return;}
  finished=true;stage=matched?"gtgt-sheet-inspected":"gtgt-sheet-contract-not-matched";Record();
 }
 private void InspectMoneyZero(object sheet){
  int[,] coordinates=new int[,] {{36,11},{39,9},{39,11},{40,9},{40,11},{41,11},{43,9},{44,9},{44,11},{45,9},{46,9},{46,11},{47,9},{47,11},{48,9},{49,9},{49,11},{50,11},{52,11},{53,11},{54,11},{56,11},{57,11},{58,11},{59,11},{60,11},{61,11}};gtgtZero=true;gtgtEmptyMoney=0;
  for(int index=0;index<coordinates.GetLength(0);index++){object value=Get(Cell(sheet,coordinates[index,0],coordinates[index,1]),"Value");if(value==null||value==DBNull.Value||Convert.ToString(value,CultureInfo.InvariantCulture)==String.Empty){gtgtEmptyMoney++;continue;}decimal number;if(!Decimal.TryParse(Convert.ToString(value,CultureInfo.InvariantCulture),NumberStyles.Number,CultureInfo.InvariantCulture,out number)||number!=Decimal.Zero)gtgtZero=false;}
 }
 private void InspectCaseMoney(object sheet){
  int[,] coordinates=new int[,] {{36,11},{39,9},{39,11},{40,9},{40,11},{41,11},{43,9},{44,9},{44,11},{45,9},{46,9},{46,11},{47,9},{47,11},{48,9},{49,9},{49,11},{50,11},{52,11},{53,11},{54,11},{56,11},{57,11},{58,11},{59,11},{60,11},{61,11}};
  gtgtCaseMoneyMatched=true;gtgtCaseMoneyCount=0;gtgtCaseMismatchMask=0;gtgtCaseNonzeroMask=0;gtgtCt42Locked=Convert.ToBoolean(Get(Cell(sheet,60,11),"Locked"));
  for(int index=0;index<coordinates.GetLength(0);index++){
   int row=coordinates[index,0],column=coordinates[index,1];decimal expected=Decimal.Zero;
   if(CreditCt21Case()&&column==11&&(row==36||row==59||row==61))expected=7;
   if(webCaseId!="01GTGT-zero-M10-2026"&&!QuarterCase()&&(!NoActivityCase()||CancelCt21Case())){
    bool fivePercent=webCaseId=="01GTGT-sale5-half-M10-2026"||webCaseId=="01GTGT-sale5-manual-M10-2026";int caseRow=fivePercent?46:47;
    if(column==9&&(row==44||row==caseRow||row==49))expected=webCaseId=="01GTGT-sale5-half-M10-2026"?10:webCaseId=="01GTGT-sale10-half-M10-2026"?5:1000000;
    if(column==11&&(row==44||row==caseRow||row==49||row==50||row==56||row==58))expected=(webCaseId=="01GTGT-sale10-half-M10-2026"||webCaseId=="01GTGT-sale5-half-M10-2026")?1:(webCaseId=="01GTGT-sale10-manual-M10-2026"||webCaseId=="01GTGT-sale5-manual-M10-2026")?7:100000;
   }
   object value=Get(Cell(sheet,row,column),"Value");decimal number;
   if(value==null||value==DBNull.Value||!Decimal.TryParse(Convert.ToString(value,CultureInfo.InvariantCulture),NumberStyles.Number,CultureInfo.InvariantCulture,out number)){gtgtCaseMoneyMatched=false;gtgtCaseMismatchMask|=1<<index;continue;}
   gtgtCaseMoneyCount++;if(number!=0)gtgtCaseNonzeroMask|=1<<index;if(number!=expected){gtgtCaseMoneyMatched=false;gtgtCaseMismatchMask|=1<<index;}
  }
  if(gtgtCaseMoneyCount!=27)gtgtCaseMoneyMatched=false;
 }
}
