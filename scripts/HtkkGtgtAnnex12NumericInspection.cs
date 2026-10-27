// Fixed fake original-control numeric observation only. No calculation or XML authoring.
using System;
using System.Globalization;
using System.Text;
using System.Windows.Forms;
public sealed partial class HtkkGuiReferenceAutomation {
 private int annex12NumericActionCount=0,annex12NumericCaseCount=0;
 private string annex12NumericSnapshots=String.Empty;
 private string Annex12NumericJson(){string q=((char)34).ToString();return ","+q+"annex12NumericActionCount"+q+":"+annex12NumericActionCount.ToString(CultureInfo.InvariantCulture)+","+q+"annex12NumericCaseCount"+q+":"+annex12NumericCaseCount.ToString(CultureInfo.InvariantCulture)+","+q+"annex12NumericSnapshots"+q+":"+q+annex12NumericSnapshots+q;}
 private void EditAnnex12Numeric(Control grid,object annex,int index){
  int[,] cells=new int[,]{{42,19},{42,19},{43,20},{44,20},{42,19}};
  string[] values=new string[]{"1","7","33.33","66.67","99999999999999"};
  if(mode!="gtgt-annex12-numeric-inspect"||index!=annex12NumericActionCount||index<0||index>=values.Length)throw new InvalidOperationException();
  grid.Focus();Annex12InputOwner(grid,annex);int row=cells[index,0],column=cells[index,1];
  // Source FormatCelltypeFromSinfo06002702 configures the original number
  // editor with DecimalSeparator="," and thousands Separator=".". Keep the
  // canonical expected value independent from the text typed into that editor.
  string editorValue=values[index];
  if(index==2||index==3){
   stage="gtgt-annex12-numeric-format-checking";Record();
   object cellType=Get(Cell(annex,row,column),"CellType");
   if(cellType==null||Convert.ToString(Get(cellType,"DecimalSeparator"),CultureInfo.InvariantCulture)!=","||Convert.ToString(Get(cellType,"Separator"),CultureInfo.InvariantCulture)!=".")throw new InvalidOperationException();
   editorValue=values[index].Replace('.',',');
  }
  if(Convert.ToBoolean(Get(Cell(annex,row,column),"Locked")))throw new InvalidOperationException();
  stage="gtgt-annex12-numeric-editing";Record();annex.GetType().GetMethod("SetActiveCell",new Type[]{typeof(int),typeof(int)}).Invoke(annex,new object[]{row,column});
  grid.GetType().GetMethod("StartCellEditing",new Type[]{typeof(EventArgs),typeof(bool)}).Invoke(grid,new object[]{EventArgs.Empty,false});
  Control editor=Get(grid,"EditingControl") as Control;if(editor==null||!editor.Visible||!editor.Enabled)throw new InvalidOperationException();editor.Focus();stage="gtgt-annex12-numeric-editor-ready";Record();
  foreach(string keys in new string[]{"^a",EscapeSendKeys(editorValue),"{TAB}"}){Annex12InputOwner(grid,annex);if(!editor.ContainsFocus)throw new InvalidOperationException();SendKeys.SendWait(keys);}
  grid.GetType().GetMethod("StopCellEditing",Type.EmptyTypes).Invoke(grid,null);Application.DoEvents();grid.Focus();Annex12InputOwner(grid,annex);
  stage="gtgt-annex12-numeric-committed";Record();
  if(!Annex12NumberMatched(annex,row,column,Decimal.Parse(values[index],CultureInfo.InvariantCulture))){stage="gtgt-annex12-numeric-value-mismatch";Record();throw new InvalidOperationException();}
  annex12NumericActionCount++;Record();
 }
 private void SnapshotAnnex12Numeric(Control grid,object annex){
  Annex12InputOwner(grid,annex);if(annex12NumericCaseCount>=3)throw new InvalidOperationException();stage="gtgt-annex12-numeric-observing";Record();
  // Header T/U/X; child T/U/X/AO; footer T/X. Values come ONLY from original cells.
  int[,] cells=new int[,]{{42,19},{42,20},{42,23},{43,19},{43,20},{43,23},{43,40},{44,19},{44,20},{44,23},{46,19},{46,23}};
  StringBuilder snapshot=new StringBuilder();
  for(int i=0;i<cells.GetLength(0);i++){decimal value;if(!Decimal.TryParse(Convert.ToString(Get(Cell(annex,cells[i,0],cells[i,1]),"Value"),CultureInfo.InvariantCulture),NumberStyles.Number,CultureInfo.InvariantCulture,out value)||value<0||value>999999999999999m)throw new InvalidOperationException();if(i>0)snapshot.Append(',');snapshot.Append(value.ToString("0.####################",CultureInfo.InvariantCulture));}
  if(annex12NumericCaseCount>0)annex12NumericSnapshots+=";";annex12NumericSnapshots+=snapshot.ToString();annex12NumericCaseCount++;Record();
 }
 private void InspectOriginalAnnex12Numeric(Control grid,object annex){
  if(mode!="gtgt-annex12-numeric-inspect"||annex12InputActionCount!=14||!annex12InputIdentityMatched||!annex12InputReadOnlyIdentityMatched||!annex12InputPercentagesMatched||!annex12InputZeroTaxMatched||annex12NumericActionCount!=0)throw new InvalidOperationException();
  EditAnnex12Numeric(grid,annex,0);SnapshotAnnex12Numeric(grid,annex);
  EditAnnex12Numeric(grid,annex,1);EditAnnex12Numeric(grid,annex,2);EditAnnex12Numeric(grid,annex,3);SnapshotAnnex12Numeric(grid,annex);
  EditAnnex12Numeric(grid,annex,4);SnapshotAnnex12Numeric(grid,annex);
  finished=true;stage="gtgt-annex12-numeric-inspected";Record();
 }
}
