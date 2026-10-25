// Own controller: only ORIGINAL GUI actions create the declaration XML.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Text;
using System.Windows.Forms;
using System.Xml;
public sealed partial class HtkkGuiReferenceAutomation {
 private bool exportStarted=false,exportCommandInvoked=false,exportSelectorMatched=false,exportButtonInvoked=false,exportDialogMatched=false,exportDestinationFresh=false,exportDialogSubmitted=false,exportFileExists=false,exportXmlRootMatched=false,exportSyntheticIdentityMatched=false,exportSuccessAcknowledged=false;
 private bool exportOriginalPathMatched=false;private int exportScopedFileCount=0,exportScopedXmlCount=0;private string exportOriginalPathKind="not-observed";
 private int exportBytes=0;private string exportSha256="",exportPath="",expectedSaveTitle="";
 private System.Windows.Forms.Timer exportWatcher=null;
 private delegate bool WindowVisitor(IntPtr window,IntPtr parameter);
 [DllImport("user32.dll")]private static extern bool EnumWindows(WindowVisitor callback,IntPtr parameter);
 [DllImport("user32.dll")]private static extern bool EnumChildWindows(IntPtr parent,WindowVisitor callback,IntPtr parameter);
 [DllImport("user32.dll")]private static extern uint GetWindowThreadProcessId(IntPtr window,out uint process);
 [DllImport("user32.dll",CharSet=CharSet.Unicode)]private static extern int GetWindowText(IntPtr window,StringBuilder text,int length);
 [DllImport("user32.dll",CharSet=CharSet.Unicode)]private static extern int GetClassName(IntPtr window,StringBuilder text,int length);
 [DllImport("user32.dll")]private static extern bool IsWindowVisible(IntPtr window);
 [DllImport("user32.dll")]private static extern bool IsWindowEnabled(IntPtr window);
 [DllImport("user32.dll")]private static extern int GetDlgCtrlID(IntPtr window);
 [DllImport("user32.dll")]private static extern IntPtr GetWindow(IntPtr window,uint command);
 [DllImport("user32.dll")]private static extern IntPtr GetDlgItem(IntPtr window,int id);
 [DllImport("user32.dll",CharSet=CharSet.Unicode)]private static extern IntPtr SendMessage(IntPtr window,uint message,IntPtr wParam,string text);
 [DllImport("user32.dll")]private static extern bool PostMessage(IntPtr window,uint message,IntPtr wParam,IntPtr lParam);
 private static string NativeText(IntPtr window,bool className){StringBuilder text=new StringBuilder(2048);if(className)GetClassName(window,text,text.Capacity);else GetWindowText(window,text,text.Capacity);return text.ToString();}
 private string ExportJson(){
  string[] names=new string[]{"exportCommandInvoked","exportSelectorMatched","exportButtonInvoked","exportDialogMatched","exportDestinationFresh","exportDialogSubmitted","exportFileExists","exportXmlRootMatched","exportSyntheticIdentityMatched","exportSuccessAcknowledged"};
  bool[] values=new bool[]{exportCommandInvoked,exportSelectorMatched,exportButtonInvoked,exportDialogMatched,exportDestinationFresh,exportDialogSubmitted,exportFileExists,exportXmlRootMatched,exportSyntheticIdentityMatched,exportSuccessAcknowledged};StringBuilder json=new StringBuilder();string q=((char)34).ToString();
  for(int index=0;index<names.Length;index++)json.Append(","+q+names[index]+q+":"+Bool(values[index]));
  json.Append(","+q+"exportOriginalPathMatched"+q+":"+Bool(exportOriginalPathMatched)+","+q+"exportOriginalPathKind"+q+":"+q+exportOriginalPathKind+q+","+q+"exportScopedFileCount"+q+":"+exportScopedFileCount+","+q+"exportScopedXmlCount"+q+":"+exportScopedXmlCount);
  json.Append(","+q+"exportBytes"+q+":"+exportBytes+","+q+"exportSha256"+q+":"+q+exportSha256+q);return json.ToString();
 }
 private static void FindExportSelectors(Control root,List<Form> found,ref int count){if(++count>512)return;Form form=root as Form;if(form!=null&&form.Visible&&form.GetType().FullName=="HTKK.frmWinSelectExport"&&!found.Contains(form))found.Add(form);foreach(Control child in root.Controls){if(count>=512)break;FindExportSelectors(child,found,ref count);}}
 private void StartOriginalGtgtExport(Form owner){
  if(exportStarted)return;exportStarted=true;
  if(!pins||!headerMatched||!successAcknowledged||!gtgtPins||!gtgtIdentity||!gtgtSigner||!gtgtZero||owner.GetType().FullName!="HTKK.frmWinToKhai")throw new InvalidOperationException();
  string directory=Path.Combine(Path.Combine(Path.Combine(Path.GetDirectoryName(project),"DataFiles"),Mst),"reference-output");if(Directory.Exists(directory)||File.Exists(directory))throw new InvalidOperationException();Directory.CreateDirectory(directory);exportPath=Path.Combine(directory,"01GTGT.xml");exportDestinationFresh=!File.Exists(exportPath);
  Assembly utilities=null;foreach(Assembly loaded in AppDomain.CurrentDomain.GetAssemblies())if(loaded.GetName().Name=="TAX.HTKK.Utilities")utilities=loaded;if(utilities==null)throw new InvalidOperationException();
  Type configuration=utilities.GetType("TAX.HTKK.Utilities.Core.HTKKConfig",true);PropertyInfo temporary=configuration.GetProperty("PATH_TEMP",BindingFlags.Public|BindingFlags.Static);if(temporary==null)throw new InvalidOperationException();expectedSaveTitle="Tệp XML kết xuất tới thư mục "+Convert.ToString(temporary.GetValue(null,null),CultureInfo.InvariantCulture);
  Button command=Named(owner,"cmdExport") as Button;if(command==null||command.FindForm()!=owner||command.Text.Replace("&",String.Empty).Trim()!="Kết xuất")throw new InvalidOperationException();
  stage="gtgt-export-command-invoking";exportCommandInvoked=true;Record();
  exportWatcher=new System.Windows.Forms.Timer();exportWatcher.Interval=100;exportWatcher.Tick+=delegate(object sender,EventArgs args){try{ObserveOriginalExport();}catch(Exception error){exportWatcher.Stop();Failure(error);}};exportWatcher.Start();command.PerformClick();
 }
 private void ObserveOriginalExport(){
  if(finished){exportWatcher.Stop();return;}
  foreach(Form form in Application.OpenForms){if(!form.Visible||form.GetType().FullName!="TAX.HTKK.Utilities.Control.frmMessage")continue;
   Control[] labels=form.Controls.Find("lblThongBao",true);if(labels.Length!=1)throw new InvalidOperationException();
   if(labels[0].Text!="Kết xuất tờ khai xml thành công."){stage="gtgt-export-original-message-rejected";finished=true;Record();exportWatcher.Stop();return;}
   stage="gtgt-export-success-file-checking";InspectOriginalExportDestination();Record();if(!exportOriginalPathMatched)throw new InvalidOperationException();
   ReadOriginalExport();if(!exportDialogSubmitted||!exportXmlRootMatched||!exportSyntheticIdentityMatched)throw new InvalidOperationException();
   Control[] closeControls=form.Controls.Find("btn_2",true);if(form.Text.Trim()!="Thông Báo"||closeControls.Length!=1||CountVisibleButtons(form)!=1)throw new InvalidOperationException();Button close=closeControls[0] as Button;if(close==null||!close.Visible||!close.Enabled||close.Text.Replace("&",String.Empty).Trim()!="Đóng")throw new InvalidOperationException();
   exportSuccessAcknowledged=true;stage="gtgt-export-inspected";finished=true;Record();exportWatcher.Stop();close.PerformClick();return;
  }
  if(!exportButtonInvoked){List<Form> selectors=new List<Form>();int count=0;foreach(Form top in Application.OpenForms)if(top.Visible)FindExportSelectors(top,selectors,ref count);if(selectors.Count==0)return;if(selectors.Count!=1)throw new InvalidOperationException();Form selector=selectors[0];
   RadioButton xml=Named(selector,"radKetXuatXML") as RadioButton,excel=Named(selector,"radKetXuatExcel") as RadioButton;Button button=Named(selector,"btnExport") as Button;
   if(xml==null||excel==null||!xml.Checked||excel.Checked||xml.Text!="Kết xuất XML"||button==null||button.FindForm()!=selector||button.Text.Replace("&",String.Empty).Trim()!="Kết xuất")throw new InvalidOperationException();
   exportSelectorMatched=true;exportButtonInvoked=true;stage="gtgt-export-file-dialog-waiting";Record();selector.BeginInvoke(new MethodInvoker(delegate{try{button.PerformClick();}catch(Exception error){Failure(error);}}));return;
  }
  if(exportDialogSubmitted)return;
  List<IntPtr> dialogs=new List<IntPtr>();uint own=(uint)Process.GetCurrentProcess().Id;
  EnumWindows(delegate(IntPtr window,IntPtr unused){uint pid;GetWindowThreadProcessId(window,out pid);if(pid==own&&IsWindowVisible(window)&&NativeText(window,true)=="#32770")dialogs.Add(window);return true;},IntPtr.Zero);
  if(dialogs.Count==0)return;if(dialogs.Count!=1)throw new InvalidOperationException();IntPtr dialog=dialogs[0];if(NativeText(dialog,false)!=expectedSaveTitle)throw new InvalidOperationException();
  IntPtr ownerWindow=GetWindow(dialog,4);uint ownerPid;if(ownerWindow==IntPtr.Zero||GetWindowThreadProcessId(ownerWindow,out ownerPid)==0||ownerPid!=own)throw new InvalidOperationException();
  List<IntPtr> edits=new List<IntPtr>();EnumChildWindows(dialog,delegate(IntPtr child,IntPtr unused){int id=GetDlgCtrlID(child);if(IsWindowVisible(child)&&IsWindowEnabled(child)&&NativeText(child,true)=="Edit"&&(id==1001||id==1148))edits.Add(child);return true;},IntPtr.Zero);
  IntPtr save=GetDlgItem(dialog,1);if(edits.Count!=1||save==IntPtr.Zero||!IsWindowVisible(save)||!IsWindowEnabled(save)||NativeText(save,true)!="Button")throw new InvalidOperationException();
  if(File.Exists(exportPath)||new DirectoryInfo(Path.GetDirectoryName(exportPath)).GetFileSystemInfos().Length!=0)throw new InvalidOperationException();
  exportDialogMatched=true;SendMessage(edits[0],12,IntPtr.Zero,exportPath);if(NativeText(edits[0],false)!=exportPath)throw new InvalidOperationException();
  exportDialogSubmitted=true;stage="gtgt-export-original-writing";Record();if(!PostMessage(save,245,IntPtr.Zero,IntPtr.Zero))throw new InvalidOperationException();
 }
 private void InspectOriginalExportDestination(){
  Type selector=OriginalAssembly().GetType("HTKK.frmWinSelectExport",true);FieldInfo path=selector.GetField("PathSave",BindingFlags.Static|BindingFlags.Public|BindingFlags.NonPublic);if(path==null||path.FieldType!=typeof(string))throw new InvalidOperationException();string actual=(string)path.GetValue(null);
  exportOriginalPathMatched=!String.IsNullOrEmpty(actual)&&String.Equals(Path.GetFullPath(actual),Path.GetFullPath(exportPath),StringComparison.OrdinalIgnoreCase);
  exportOriginalPathKind=String.IsNullOrEmpty(actual)?"empty":exportOriginalPathMatched?"expected-path":String.Equals(Path.GetFullPath(actual),Path.GetFullPath(exportPath+".xml"),StringComparison.OrdinalIgnoreCase)?"expected-double-extension":String.Equals(Path.GetDirectoryName(Path.GetFullPath(actual)),Path.GetDirectoryName(Path.GetFullPath(exportPath)),StringComparison.OrdinalIgnoreCase)?"same-directory-other-name":"other-directory";
  DirectoryInfo directory=new DirectoryInfo(Path.GetDirectoryName(exportPath));if((directory.Attributes&FileAttributes.ReparsePoint)!=0)throw new InvalidOperationException();FileInfo[] files=directory.GetFiles();if(files.Length>32)throw new InvalidOperationException();exportScopedFileCount=files.Length;exportScopedXmlCount=0;foreach(FileInfo file in files)if(String.Equals(file.Extension,".xml",StringComparison.OrdinalIgnoreCase))exportScopedXmlCount++;
 }
 private void ReadOriginalExport(){
  exportFileExists=File.Exists(exportPath);if(!exportFileExists)throw new InvalidOperationException();FileInfo file=new FileInfo(exportPath);if((file.Attributes&FileAttributes.ReparsePoint)!=0||file.Length<1||file.Length>262144)throw new InvalidOperationException();exportBytes=(int)file.Length;
  XmlReaderSettings settings=new XmlReaderSettings();settings.ProhibitDtd=true;settings.XmlResolver=null;XmlDocument document=new XmlDocument();document.XmlResolver=null;using(XmlReader reader=XmlReader.Create(exportPath,settings))document.Load(reader);
  exportXmlRootMatched=document.DocumentElement!=null&&document.DocumentElement.LocalName=="HSoThueDTu"&&document.DocumentElement.NamespaceURI=="http://kekhaithue.gdt.gov.vn/TKhaiThue";
  XmlNode mst=document.SelectSingleNode("/*[local-name()='HSoThueDTu']/*[local-name()='HSoKhaiThue']/*[local-name()='TTinChung']/*[local-name()='TTinTKhaiThue']/*[local-name()='NNT']/*[local-name()='mst']");
  XmlNode name=document.SelectSingleNode("/*[local-name()='HSoThueDTu']/*[local-name()='HSoKhaiThue']/*[local-name()='TTinChung']/*[local-name()='TTinTKhaiThue']/*[local-name()='NNT']/*[local-name()='tenNNT']");
  exportSyntheticIdentityMatched=mst!=null&&mst.InnerText==Mst&&name!=null&&name.InnerText==FakeName;if(!exportXmlRootMatched||!exportSyntheticIdentityMatched)throw new InvalidOperationException();exportSha256=Hash(exportPath);
 }
}
