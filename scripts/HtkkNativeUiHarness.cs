// Shared original-control primitives. No adapter IDs, business rules or authored XML.
// CLR2 / C# 2.0; calls run on the original application's UI thread.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Windows.Forms;

internal static class HtkkNativeUiHarness {
 internal static object Get(object target,string name){PropertyInfo p=target.GetType().GetProperty(name,BindingFlags.Public|BindingFlags.Instance);if(p==null)throw new InvalidOperationException();return p.GetValue(target,null);}
 internal static object Cell(object sheet,int row,int column){object cells=Get(sheet,"Cells");PropertyInfo item=cells.GetType().GetProperty("Item",new Type[]{typeof(int),typeof(int)});if(item==null)throw new InvalidOperationException();return item.GetValue(cells,new object[]{row,column});}
 internal static string CellText(object sheet,int row,int column){object value=Get(Cell(sheet,row,column),"Text");return value==null?String.Empty:Convert.ToString(value,CultureInfo.InvariantCulture);}
 internal static void SetPublic(object target,string name,object value){PropertyInfo p=target.GetType().GetProperty(name,BindingFlags.Public|BindingFlags.Instance);if(p==null||!p.CanWrite)throw new InvalidOperationException();p.SetValue(target,value,null);}
 internal static Control FindVendorCombo(Control root,int depth){
  if(depth>6)return null;
  for(Type type=root.GetType();type!=null;type=type.BaseType)if(type.FullName=="FarPoint.Win.FpCombo")return root;
  Control found=null;foreach(Control child in root.Controls){Control candidate=FindVendorCombo(child,depth+1);if(candidate!=null){if(found!=null)throw new InvalidOperationException();found=candidate;}}return found;
 }
 internal static Control BeginCellEdit(Control spread,object sheet,int row,int column){
  spread.Focus();sheet.GetType().GetMethod("SetActiveCell",new Type[]{typeof(int),typeof(int)}).Invoke(sheet,new object[]{row,column});
  spread.GetType().GetMethod("StartCellEditing",new Type[]{typeof(EventArgs),typeof(bool)}).Invoke(spread,new object[]{EventArgs.Empty,false});
  Control editor=Get(spread,"EditingControl") as Control;if(editor==null)throw new InvalidOperationException();return editor;
 }
 internal static void CommitCellEdit(Control spread){spread.GetType().GetMethod("StopCellEditing",Type.EmptyTypes).Invoke(spread,null);}
 internal static bool SelectCombo(Control editor,string value){
  ComboBox combo=editor as ComboBox;if(combo==null){foreach(Control child in editor.Controls){if(child is ComboBox){if(combo!=null)throw new InvalidOperationException();combo=(ComboBox)child;}}}
  if(combo!=null){
   int selected=-1;for(int index=0;index<combo.Items.Count&&index<4096;index++){if(combo.GetItemText(combo.Items[index])==value){if(selected>=0)throw new InvalidOperationException();selected=index;}}
   if(selected<0)throw new InvalidOperationException();combo.DroppedDown=true;combo.SelectedIndex=selected;combo.DroppedDown=false;return true;
  }
  Control vendor=FindVendorCombo(editor,0);if(vendor==null)return false;
  SetPublic(vendor,"DroppedDown",true);object list=Get(vendor,"List");System.Collections.IList sequence=list as System.Collections.IList;int count=sequence!=null?sequence.Count:Convert.ToInt32(Get(list,"Count"));
  if(count<1||count>4096)throw new InvalidOperationException();PropertyInfo item=list.GetType().GetProperty("Item",new Type[]{typeof(int)});if(item==null&&sequence==null)throw new InvalidOperationException();
  int chosen=-1;for(int index=0;index<count;index++){object entry=sequence!=null?sequence[index]:item.GetValue(list,new object[]{index});if(entry!=null&&entry.ToString()==value){if(chosen>=0)throw new InvalidOperationException();chosen=index;}}
  if(chosen<0)throw new InvalidOperationException();SetPublic(vendor,"SelectedIndex",chosen);SetPublic(vendor,"DroppedDown",false);return true;
 }
 // Observe the original clean flag only; never clear dirty state or accept a warning.
 internal static bool IsOriginalWorksheetClean(Form owner){FieldInfo dirty=owner.GetType().GetField("isDataChanged",BindingFlags.Instance|BindingFlags.Public|BindingFlags.NonPublic);return dirty!=null&&dirty.FieldType==typeof(bool)&&!(bool)dirty.GetValue(owner);}
}

// Shared profile ownership/lifecycle, independent of menu/period/adapter state.
internal sealed class HtkkNativeProfileLifecycle {
 private Form owner;
 private Button close;
 private bool requested;
 internal bool IsBound {get{return owner!=null;}}
 internal bool CloseRequested {get{return requested;}}
 internal bool Closed {get{return owner!=null&&(owner.IsDisposed||!owner.Visible);}}
 internal void Bind(Form profileOwner,Button closeButton,Control spread){
  if(owner!=null||profileOwner==null||profileOwner.GetType().FullName!="HTKK.frmWinToKhai"||closeButton==null||spread==null||closeButton.FindForm()!=profileOwner||spread.FindForm()!=profileOwner||closeButton.Name!="cmdExit")throw new InvalidOperationException();
  owner=profileOwner;close=closeButton;
 }
 internal bool IdentityMatched {get{return owner!=null&&!owner.IsDisposed&&owner.Visible&&close!=null&&!close.IsDisposed&&close.Name=="cmdExit"&&close.FindForm()==owner&&close.Text.Replace("&",String.Empty).Trim()=="Đóng";}}
 internal bool Ready {get{return IdentityMatched&&owner.Enabled&&close.Visible&&close.Enabled;}}
 internal bool Clean {get{return IdentityMatched&&HtkkNativeUiHarness.IsOriginalWorksheetClean(owner);}}
 internal void RequestClose(){if(requested||!Ready||!Clean)throw new InvalidOperationException();requested=true;close.PerformClick();}
}

// Resolves only this process's single visible original common dialog.
// Every call re-observes ownership and editor/button identity before any input.
internal sealed class HtkkNativeFileDialog {
 internal IntPtr Dialog,Editor,Submit,EditorParent;
 internal string EditorParentClass;
 private delegate bool WindowVisitor(IntPtr window,IntPtr parameter);
 [DllImport("user32.dll")]private static extern bool EnumWindows(WindowVisitor callback,IntPtr parameter);
 [DllImport("user32.dll")]private static extern bool EnumChildWindows(IntPtr parent,WindowVisitor callback,IntPtr parameter);
 [DllImport("user32.dll")]private static extern uint GetWindowThreadProcessId(IntPtr window,out uint process);
 [DllImport("user32.dll",CharSet=CharSet.Unicode)]private static extern int GetWindowText(IntPtr window,System.Text.StringBuilder text,int length);
 [DllImport("user32.dll",CharSet=CharSet.Unicode)]private static extern int GetClassName(IntPtr window,System.Text.StringBuilder text,int length);
 [DllImport("user32.dll")]private static extern bool IsWindowVisible(IntPtr window);
 [DllImport("user32.dll")]private static extern bool IsWindowEnabled(IntPtr window);
 [DllImport("user32.dll")]private static extern int GetDlgCtrlID(IntPtr window);
 [DllImport("user32.dll")]private static extern IntPtr GetWindow(IntPtr window,uint command);
 [DllImport("user32.dll")]private static extern IntPtr GetParent(IntPtr window);
 [DllImport("user32.dll")]private static extern IntPtr GetDlgItem(IntPtr window,int id);
 private static string Text(IntPtr window,bool className){System.Text.StringBuilder text=new System.Text.StringBuilder(2048);if(className)GetClassName(window,text,text.Capacity);else GetWindowText(window,text,text.Capacity);return text.ToString();}
 internal static HtkkNativeFileDialog Find(string expectedTitle){
  List<IntPtr> dialogs=new List<IntPtr>();uint own=(uint)Process.GetCurrentProcess().Id;
  EnumWindows(delegate(IntPtr window,IntPtr unused){uint pid;GetWindowThreadProcessId(window,out pid);if(pid==own&&IsWindowVisible(window)&&Text(window,true)=="#32770")dialogs.Add(window);return true;},IntPtr.Zero);
  if(dialogs.Count==0)return null;if(dialogs.Count!=1)throw new InvalidOperationException();IntPtr dialog=dialogs[0];if(Text(dialog,false)!=expectedTitle)throw new InvalidOperationException();
  IntPtr ownerWindow=GetWindow(dialog,4);uint ownerPid;if(ownerWindow==IntPtr.Zero||GetWindowThreadProcessId(ownerWindow,out ownerPid)==0||ownerPid!=own)throw new InvalidOperationException();
  List<IntPtr> edits=new List<IntPtr>();EnumChildWindows(dialog,delegate(IntPtr child,IntPtr unused){int id=GetDlgCtrlID(child);if(IsWindowVisible(child)&&IsWindowEnabled(child)&&Text(child,true)=="Edit"&&(id==1001||id==1148))edits.Add(child);return true;},IntPtr.Zero);
  IntPtr save=GetDlgItem(dialog,1);if(edits.Count!=1||save==IntPtr.Zero||!IsWindowVisible(save)||!IsWindowEnabled(save)||Text(save,true)!="Button")throw new InvalidOperationException();
  IntPtr parent=GetParent(edits[0]);string parentClass=Text(parent,true);
  if(parent==IntPtr.Zero||(parentClass!="ComboBox"&&parentClass!="ComboBoxEx32"))throw new InvalidOperationException();
  HtkkNativeFileDialog found=new HtkkNativeFileDialog();found.Dialog=dialog;found.Editor=edits[0];found.Submit=save;found.EditorParent=parent;found.EditorParentClass=parentClass;return found;
 }
}
