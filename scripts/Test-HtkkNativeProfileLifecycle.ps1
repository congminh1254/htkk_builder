# Unit fixture for the exact production lifecycle policy. This is not native HTKK proof.
$ErrorActionPreference='Stop'
$source=[IO.File]::ReadAllText((Join-Path $PSScriptRoot 'HtkkNativeUiHarness.cs'))
# Compile the complete production helper with UI-shaped unit fixture types. Only
# the imported UI namespace changes; all helper methods and lifecycle logic stay intact.
$fixture=$source.Replace('using System.Windows.Forms;','using HtkkFixtureUi;')+@'
namespace HtkkFixtureUi {
 public class Control {public string Name="",Text="";public bool Visible=true,Enabled=true,IsDisposed=false;public Form Owner;public System.Collections.Generic.List<Control> Controls=new System.Collections.Generic.List<Control>();public Form FindForm(){return Owner;}public void Focus(){}}
 public class Form:Control {}
 public class ComboBox:Control {public System.Collections.Generic.List<object> Items=new System.Collections.Generic.List<object>();public bool DroppedDown;public int SelectedIndex=-1;public string GetItemText(object value){return value.ToString();}}
 public class Button:Control {public int Clicks;public void PerformClick(){Clicks++;}}
}
namespace HTKK {public sealed class frmWinToKhai:Form {private bool isDataChanged;public frmWinToKhai(bool dirty){isDataChanged=dirty;}public bool Dirty{get{return isDataChanged;}}}}
public sealed class HtkkFixtureSheet {public int Row=-1,Column=-1;public void SetActiveCell(int row,int column){Row=row;Column=column;}}
public sealed class HtkkFixtureSpread:Control {public int Started,Stopped;public Control EditingControl {get;set;}public void StartCellEditing(EventArgs args,bool mode){Started++;}public void StopCellEditing(){Stopped++;}}
namespace FarPoint.Win {public sealed class FpCombo:Control {public bool DroppedDown {get;set;}public int SelectedIndex {get;set;}public System.Collections.ArrayList List {get;set;}public FpCombo(){List=new System.Collections.ArrayList();SelectedIndex=-1;}}}
public static class HtkkNativeProfileLifecycleFixture {
 private static void Need(bool condition){if(!condition)throw new Exception("Lifecycle policy mismatch");}
 private static void Reject(Action action){bool rejected=false;try{action();}catch(InvalidOperationException){rejected=true;}Need(rejected);}
 private static Button Close(Form owner){Button b=new Button();b.Owner=owner;b.Name="cmdExit";b.Text="&Đóng";return b;}
 public static int Run(){
  HtkkNativeProfileLifecycle empty=new HtkkNativeProfileLifecycle();Need(!empty.IsBound&&!empty.Closed&&!empty.CloseRequested);Reject(delegate{empty.RequestClose();});
  HTKK.frmWinToKhai owner=new HTKK.frmWinToKhai(false);Button close=Close(owner);Control spread=new Control();spread.Owner=owner;
  HtkkNativeProfileLifecycle good=new HtkkNativeProfileLifecycle();good.Bind(owner,close,spread);Need(good.IsBound&&good.IdentityMatched&&good.Ready&&good.Clean);
  Reject(delegate{good.Bind(owner,close,spread);});
  close.Enabled=false;Need(!good.Ready);Reject(delegate{good.RequestClose();});Need(close.Clicks==0);close.Enabled=true;
  good.RequestClose();Need(good.CloseRequested&&close.Clicks==1&&!good.Closed);Reject(delegate{good.RequestClose();});Need(close.Clicks==1);
  owner.Visible=false;Need(good.Closed);owner.Visible=true;owner.IsDisposed=true;Need(good.Closed&&!good.IdentityMatched);
  HTKK.frmWinToKhai dirty=new HTKK.frmWinToKhai(true);Button dirtyClose=Close(dirty);Control dirtySpread=new Control();dirtySpread.Owner=dirty;
  HtkkNativeProfileLifecycle blocked=new HtkkNativeProfileLifecycle();blocked.Bind(dirty,dirtyClose,dirtySpread);Need(blocked.Ready&&!blocked.Clean);Reject(delegate{blocked.RequestClose();});Need(dirty.Dirty&&dirtyClose.Clicks==0&&!blocked.CloseRequested);
  HTKK.frmWinToKhai other=new HTKK.frmWinToKhai(false);Control foreignSpread=new Control();foreignSpread.Owner=other;
  Reject(delegate{new HtkkNativeProfileLifecycle().Bind(dirty,dirtyClose,foreignSpread);});
  Button wrong=Close(dirty);wrong.Name="other";Reject(delegate{new HtkkNativeProfileLifecycle().Bind(dirty,wrong,dirtySpread);});
  Form wrongOwner=new Form();Reject(delegate{new HtkkNativeProfileLifecycle().Bind(wrongOwner,Close(wrongOwner),new Control());});
  HtkkFixtureSheet sheet=new HtkkFixtureSheet();HtkkFixtureSpread grid=new HtkkFixtureSpread();Control editor=new Control();grid.EditingControl=editor;
  Need(HtkkNativeUiHarness.BeginCellEdit(grid,sheet,3,2)==editor&&sheet.Row==3&&sheet.Column==2&&grid.Started==1);HtkkNativeUiHarness.CommitCellEdit(grid);Need(grid.Stopped==1);
  ComboBox combo=new ComboBox();combo.Items.Add("a");combo.Items.Add("b");Need(HtkkNativeUiHarness.SelectCombo(combo,"b")&&combo.SelectedIndex==1&&!combo.DroppedDown);
  combo.Items.Add("b");Reject(delegate{HtkkNativeUiHarness.SelectCombo(combo,"b");});Reject(delegate{HtkkNativeUiHarness.SelectCombo(combo,"missing");});
  FarPoint.Win.FpCombo vendor=new FarPoint.Win.FpCombo();vendor.List.Add("a");vendor.List.Add("b");Need(HtkkNativeUiHarness.SelectCombo(vendor,"b")&&vendor.SelectedIndex==1&&!vendor.DroppedDown);
  vendor.List.Add("b");Reject(delegate{HtkkNativeUiHarness.SelectCombo(vendor,"b");});
  Control ambiguous=new Control();ambiguous.Controls.Add(new FarPoint.Win.FpCombo());ambiguous.Controls.Add(new FarPoint.Win.FpCombo());Reject(delegate{HtkkNativeUiHarness.FindVendorCombo(ambiguous,0);});
  Need(!HtkkNativeUiHarness.SelectCombo(new Control(),"a"));
  return 16;
 }
}
'@
Add-Type -TypeDefinition $fixture -ErrorAction Stop
if([HtkkNativeProfileLifecycleFixture]::Run() -ne 16){throw 'Lifecycle fixture incomplete.'}
'PASS: original profile lifecycle ownership, clean observation, single close, asynchronous completion and shared editor policy (unit fixture only).'
