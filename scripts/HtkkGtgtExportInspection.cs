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
 private bool exportFilenameEditing=false,exportFilenameKeyboardCommitted=false;private string exportFilenameParentKind="not-observed";private bool exportSchemaPinnedVerified=false;private bool exportOriginalPathMatched=false;private int exportScopedFileCount=0,exportScopedXmlCount=0;private string exportOriginalPathKind="not-observed";
 private int exportBytes=0;private string exportSha256="",exportPath="",expectedSaveTitle="";
 private readonly HtkkFileDialogFocusGate filenameFocusGate=new HtkkFileDialogFocusGate();
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
 [DllImport("user32.dll")]private static extern IntPtr GetParent(IntPtr window);
 [DllImport("user32.dll")]private static extern IntPtr SetFocus(IntPtr window);
 [DllImport("user32.dll")]private static extern IntPtr GetFocus();
 [DllImport("user32.dll")]private static extern IntPtr GetForegroundWindow();
 [DllImport("user32.dll")]private static extern bool SetForegroundWindow(IntPtr window);
 [DllImport("user32.dll")]private static extern IntPtr GetDlgItem(IntPtr window,int id);
 [DllImport("user32.dll",CharSet=CharSet.Unicode)]private static extern IntPtr SendMessage(IntPtr window,uint message,IntPtr wParam,string text);
 [DllImport("user32.dll")]private static extern bool PostMessage(IntPtr window,uint message,IntPtr wParam,IntPtr lParam);
 private static string NativeText(IntPtr window,bool className){StringBuilder text=new StringBuilder(2048);if(className)GetClassName(window,text,text.Capacity);else GetWindowText(window,text,text.Capacity);return text.ToString();}
 private string ExportJson(){
  string[] names=new string[]{"exportCommandInvoked","exportSelectorMatched","exportButtonInvoked","exportDialogMatched","exportDestinationFresh","exportDialogSubmitted","exportFileExists","exportXmlRootMatched","exportSyntheticIdentityMatched","exportSuccessAcknowledged"};
  bool[] values=new bool[]{exportCommandInvoked,exportSelectorMatched,exportButtonInvoked,exportDialogMatched,exportDestinationFresh,exportDialogSubmitted,exportFileExists,exportXmlRootMatched,exportSyntheticIdentityMatched,exportSuccessAcknowledged};StringBuilder json=new StringBuilder();string q=((char)34).ToString();
  for(int index=0;index<names.Length;index++)json.Append(","+q+names[index]+q+":"+Bool(values[index]));
  json.Append(","+q+"exportSchemaPinnedVerified"+q+":"+Bool(exportSchemaPinnedVerified));
  json.Append(","+q+"exportFilenameKeyboardCommitted"+q+":"+Bool(exportFilenameKeyboardCommitted)+","+q+"exportFilenameParentKind"+q+":"+q+exportFilenameParentKind+q);
  json.Append(","+q+"exportOriginalPathMatched"+q+":"+Bool(exportOriginalPathMatched)+","+q+"exportOriginalPathKind"+q+":"+q+exportOriginalPathKind+q+","+q+"exportScopedFileCount"+q+":"+exportScopedFileCount+","+q+"exportScopedXmlCount"+q+":"+exportScopedXmlCount);
  json.Append(","+q+"exportBytes"+q+":"+exportBytes+","+q+"exportSha256"+q+":"+q+exportSha256+q);return json.ToString()+RoundtripJson();
 }
 private static void FindExportSelectors(Control root,List<Form> found,ref int count){if(++count>512)return;Form form=root as Form;if(form!=null&&form.Visible&&form.GetType().FullName=="HTKK.frmWinSelectExport"&&!found.Contains(form))found.Add(form);foreach(Control child in root.Controls){if(count>=512)break;FindExportSelectors(child,found,ref count);}}
 private void StartOriginalGtgtExport(Form owner){
  if(exportStarted)return;gtgtCt42BeforeExportObserved=true;gtgtCt42LockedBeforeExport=gtgtCt42Locked;exportStarted=true;roundtripOwner=owner;
  if(mode=="gtgt-web-import-inspect"){stage="gtgt-web-input-checking";Record();VerifyOwnWebInput();}
  if(!pins||!headerMatched||!successAcknowledged||!gtgtPins||!gtgtIdentity||!gtgtSigner||!gtgtCaseMoneyMatched||owner.GetType().FullName!="HTKK.frmWinToKhai")throw new InvalidOperationException();
  string schema=Path.Combine(Path.GetDirectoryName(project),"InterfaceTemplates/Validate/01_GTGT_TT80_283.xsd");
  string originalSchema=Convert.ToString(Get(Global("ToKhaiInfo"),"XsdFileName"),CultureInfo.InvariantCulture);
  exportSchemaPinnedVerified=!String.IsNullOrEmpty(originalSchema)&&String.Equals(Path.GetFullPath(originalSchema),Path.GetFullPath(schema),StringComparison.OrdinalIgnoreCase)&&Hash(schema)=="8d4c0d88100e858ddfe221d080a6a338776d1364c7de04347bfb990d04833003"&&Hash(Path.Combine(project,"TAX.HTKK.ComputeHash.dll"))=="d9d63921565ea2039109ad63d71977dcf56889cd83851977a0c712873ab687f5";
  if(!exportSchemaPinnedVerified)throw new InvalidOperationException();
  string directory=Path.Combine(Path.Combine(Path.Combine(Path.GetDirectoryName(project),"DataFiles"),Mst),mode=="gtgt-annex12-export-inspect"?"reference-annex12-output":"reference-output");if(Directory.Exists(directory)||File.Exists(directory))throw new InvalidOperationException();Directory.CreateDirectory(directory);exportPath=Path.Combine(directory,"01GTGT.xml");exportDestinationFresh=!File.Exists(exportPath);
  Assembly utilities=null;foreach(Assembly loaded in AppDomain.CurrentDomain.GetAssemblies())if(loaded.GetName().Name=="TAX.HTKK.Utilities")utilities=loaded;if(utilities==null)throw new InvalidOperationException();
  Type configuration=utilities.GetType("TAX.HTKK.Utilities.Core.HTKKConfig",true);PropertyInfo temporary=configuration.GetProperty("PATH_TEMP",BindingFlags.Public|BindingFlags.Static);if(temporary==null)throw new InvalidOperationException();expectedSaveTitle="Tệp XML kết xuất tới thư mục "+Convert.ToString(temporary.GetValue(null,null),CultureInfo.InvariantCulture);
  Button command=Named(owner,"cmdExport") as Button;if(command==null||command.FindForm()!=owner||command.Text.Replace("&",String.Empty).Trim()!="Kết xuất")throw new InvalidOperationException();
  stage="gtgt-export-command-invoking";exportCommandInvoked=true;Record();
  exportWatcher=new System.Windows.Forms.Timer();exportWatcher.Interval=100;exportWatcher.Tick+=delegate(object sender,EventArgs args){try{ObserveOriginalExport();}catch(Exception error){exportWatcher.Stop();Failure(error);}};exportWatcher.Start();command.PerformClick();
 }
 private void ObserveOriginalExport(){
  if(finished){exportWatcher.Stop();return;}if(exportFilenameEditing)return;
  if(roundtripPhase!="not-started"&&roundtripPhase!="reexporting"){ContinueOriginalRoundtrip();return;}
  foreach(Form form in Application.OpenForms){if(!form.Visible||form.GetType().FullName!="TAX.HTKK.Utilities.Control.frmMessage")continue;
   Control[] labels=form.Controls.Find("lblThongBao",true);if(labels.Length!=1)throw new InvalidOperationException();
   if(labels[0].Text!="Kết xuất tờ khai xml thành công."){stage="gtgt-export-original-message-rejected";finished=true;Record();exportWatcher.Stop();return;}
   stage="gtgt-export-success-file-checking";InspectOriginalExportDestination();Record();if(!exportOriginalPathMatched)throw new InvalidOperationException();
   ReadOriginalExport();if(mode=="gtgt-annex12-export-inspect")ValidateOriginalAnnex12Export();if(!exportDialogSubmitted||!exportXmlRootMatched||!exportSyntheticIdentityMatched)throw new InvalidOperationException();
   Control[] closeControls=form.Controls.Find("btn_2",true);if(form.Text.Trim()!="Thông Báo"||closeControls.Length!=1||CountVisibleButtons(form)!=1)throw new InvalidOperationException();Button close=closeControls[0] as Button;if(close==null||!close.Visible||!close.Enabled||close.Text.Replace("&",String.Empty).Trim()!="Đóng")throw new InvalidOperationException();
   exportSuccessAcknowledged=true;
   if((mode=="gtgt-roundtrip-inspect"||mode=="gtgt-web-import-inspect")&&roundtripPhase=="not-started"){
    firstExportPath=exportPath;firstExportSha256=exportSha256;firstExportBytes=exportBytes;
    roundtripPhase="waiting-import-ready";SetStage(mode=="gtgt-web-import-inspect"?HtkkAutomationStage.GtgtWebImportReadyWaiting:HtkkAutomationStage.GtgtImportReadyWaiting);Record();close.PerformClick();return;
   }
   if(roundtripPhase=="reexporting"){
    roundtripReexportBytes=exportBytes;roundtripReexportSha256=exportSha256;roundtripReexportSucceeded=true;
    if(Hash(firstExportPath)!=firstExportSha256)throw new InvalidOperationException();
    roundtripXmlExactMatched=ReadBoundedOriginalXml(firstExportPath).DocumentElement.OuterXml==ReadBoundedOriginalXml(exportPath).DocumentElement.OuterXml;
    if(mode=="gtgt-web-import-inspect"){
     XmlDocument input=ReadBoundedOriginalXml(webInputPath),baseline=ReadBoundedOriginalXml(firstExportPath),output=ReadBoundedOriginalXml(exportPath);
     webCreationDateMatchedNativeBaseline=HtkkWebTaxComparison.CreationDateMatchesNativeBaseline(baseline,output);webServiceIdentityMatched=HtkkWebTaxComparison.NativeIdentity(baseline,output);webTaxValuesMatched=HtkkWebTaxComparison.Compare(input,baseline,output,out webTaxLeafCount);
    }
    exportBytes=firstExportBytes;exportSha256=firstExportSha256;if(mode=="gtgt-web-import-inspect"&&Hash(webInputPath)!=webImportInputSha256)throw new InvalidOperationException();SetStage(mode=="gtgt-web-import-inspect"?HtkkAutomationStage.GtgtWebImportInspected:HtkkAutomationStage.GtgtRoundtripInspected);
   }else SetStage(mode=="gtgt-annex12-export-inspect"?HtkkAutomationStage.GtgtAnnex12ExportInspected:HtkkAutomationStage.GtgtExportInspected);
   finished=true;Record();exportWatcher.Stop();close.PerformClick();return;
  }
  if(!exportButtonInvoked){List<Form> selectors=new List<Form>();int count=0;foreach(Form top in Application.OpenForms)if(top.Visible)FindExportSelectors(top,selectors,ref count);if(selectors.Count==0)return;if(selectors.Count!=1)throw new InvalidOperationException();Form selector=selectors[0];
   RadioButton xml=Named(selector,"radKetXuatXML") as RadioButton,excel=Named(selector,"radKetXuatExcel") as RadioButton;Button button=Named(selector,"btnExport") as Button;
   if(xml==null||excel==null||!xml.Checked||excel.Checked||xml.Text!="Kết xuất XML"||button==null||button.FindForm()!=selector||button.Text.Replace("&",String.Empty).Trim()!="Kết xuất")throw new InvalidOperationException();
   exportSelectorMatched=true;exportButtonInvoked=true;stage="gtgt-export-file-dialog-waiting";Record();selector.BeginInvoke(new MethodInvoker(delegate{try{button.PerformClick();}catch(Exception error){Failure(error);}}));return;
  }
  if(exportDialogSubmitted)return;
  TrySubmitOriginalFileDialog(expectedSaveTitle,exportPath,false);
 }
 private bool TrySubmitOriginalFileDialog(string expectedTitle,string desiredPath,bool opening){
  List<IntPtr> dialogs=new List<IntPtr>();uint own=(uint)Process.GetCurrentProcess().Id;
  EnumWindows(delegate(IntPtr window,IntPtr unused){uint pid;GetWindowThreadProcessId(window,out pid);if(pid==own&&IsWindowVisible(window)&&NativeText(window,true)=="#32770")dialogs.Add(window);return true;},IntPtr.Zero);
  if(dialogs.Count==0)return false;if(dialogs.Count!=1)throw new InvalidOperationException();IntPtr dialog=dialogs[0];if(NativeText(dialog,false)!=expectedTitle)throw new InvalidOperationException();
  IntPtr ownerWindow=GetWindow(dialog,4);uint ownerPid;if(ownerWindow==IntPtr.Zero||GetWindowThreadProcessId(ownerWindow,out ownerPid)==0||ownerPid!=own)throw new InvalidOperationException();
  List<IntPtr> edits=new List<IntPtr>();EnumChildWindows(dialog,delegate(IntPtr child,IntPtr unused){int id=GetDlgCtrlID(child);if(IsWindowVisible(child)&&IsWindowEnabled(child)&&NativeText(child,true)=="Edit"&&(id==1001||id==1148))edits.Add(child);return true;},IntPtr.Zero);
  IntPtr save=GetDlgItem(dialog,1);if(edits.Count!=1||save==IntPtr.Zero||!IsWindowVisible(save)||!IsWindowEnabled(save)||NativeText(save,true)!="Button")throw new InvalidOperationException();
  if(opening){if(!File.Exists(desiredPath)||Hash(desiredPath)!=RoundtripInputHash())throw new InvalidOperationException();}
  else{
   if(File.Exists(desiredPath))throw new InvalidOperationException();
   FileSystemInfo[] contents=new DirectoryInfo(Path.GetDirectoryName(desiredPath)).GetFileSystemInfos();
   if(roundtripPhase=="reexporting"){if(contents.Length!=1||!(contents[0] is FileInfo)||!String.Equals(contents[0].FullName,firstExportPath,StringComparison.OrdinalIgnoreCase)||Hash(firstExportPath)!=firstExportSha256)throw new InvalidOperationException();}
   else if(contents.Length!=0)throw new InvalidOperationException();
  }
  IntPtr edit=edits[0],parent=GetParent(edit);string parentClass=NativeText(parent,true);
  exportFilenameParentKind=parentClass=="ComboBox"?"combobox":parentClass=="ComboBoxEx32"?"combobox-ex":"other";Record();
  // Filename editors belong to the verified common-dialog combo. A search edit
  // or unrelated child must never receive keyboard input.
  if(parent==IntPtr.Zero||(parentClass!="ComboBox"&&parentClass!="ComboBoxEx32"))throw new InvalidOperationException();
  if(opening)roundtripImportDialogMatched=true;else exportDialogMatched=true;
  // Focus may settle on a later UI turn. Revalidate the same dialog and editor
  // above on every tick; never restart keyboard input after it has begun.
  // Generated explicit map for 10 filename prefix/suffix stages:
  // "gtgt-export-filename-" "gtgt-import-filename-"
  // "focus-waiting" "focus-timeout" "keyboard-focused" "keyboard-selected" "keyboard-typed"
  bool ownsFocus=GetForegroundWindow()==dialog&&GetFocus()==edit;
  HtkkFileDialogFocusState focusState=filenameFocusGate.Observe(dialog,edit,ownsFocus);
  if(focusState==HtkkFileDialogFocusState.Timeout){SetStage(HtkkNativeAutomationWireMap.GetFilenameStage(opening,HtkkFilenameDialogAction.FocusTimeout));Record();throw new InvalidOperationException();}
  if(focusState!=HtkkFileDialogFocusState.Ready){
   SetStage(HtkkNativeAutomationWireMap.GetFilenameStage(opening,HtkkFilenameDialogAction.FocusWaiting));Record();
   if(!ownsFocus){SetForegroundWindow(dialog);SetFocus(edit);}return false;
  }
  filenameFocusGate.Begin();exportFilenameEditing=true;exportWatcher.Stop();SetStage(HtkkNativeAutomationWireMap.GetFilenameStage(opening,HtkkFilenameDialogAction.KeyboardEditing));Record();
  try{
   if(GetForegroundWindow()!=dialog||GetFocus()!=edit)throw new InvalidOperationException();
   SetStage(HtkkNativeAutomationWireMap.GetFilenameStage(opening,HtkkFilenameDialogAction.KeyboardFocused));Record();
   SendKeys.SendWait("^a");SetStage(HtkkNativeAutomationWireMap.GetFilenameStage(opening,HtkkFilenameDialogAction.KeyboardSelected));Record();if(GetForegroundWindow()!=dialog||GetFocus()!=edit)throw new InvalidOperationException();
   SendKeys.SendWait(EscapeSendKeys(desiredPath));SetStage(HtkkNativeAutomationWireMap.GetFilenameStage(opening,HtkkFilenameDialogAction.KeyboardTyped));Record();if(GetForegroundWindow()!=dialog||GetFocus()!=edit||NativeText(edit,false)!=desiredPath)throw new InvalidOperationException();
   if(opening)roundtripImportKeyboardCommitted=true;else exportFilenameKeyboardCommitted=true;
   // Common-dialog change notifications may rebuild controls. Resolve the
   // original Save button again in the SAME verified dialog after real typing.
   save=GetDlgItem(dialog,1);if(NativeText(dialog,false)!=expectedTitle||save==IntPtr.Zero||!IsWindowVisible(save)||!IsWindowEnabled(save)||NativeText(save,true)!="Button")throw new InvalidOperationException();
   if(opening)roundtripImportDialogSubmitted=true;else exportDialogSubmitted=true;SetStage(opening?HtkkAutomationStage.GtgtImportOriginalReading:HtkkAutomationStage.GtgtExportOriginalWriting);Record();if(!PostMessage(save,245,IntPtr.Zero,IntPtr.Zero))throw new InvalidOperationException();filenameFocusGate.ResetAfterSubmission();
  }finally{exportFilenameEditing=false;if(!finished)exportWatcher.Start();}
  return true;
 }
 private static string EscapeSendKeys(string value){StringBuilder escaped=new StringBuilder();foreach(char character in value){if("+^%~(){}[]".IndexOf(character)>=0)escaped.Append("{"+character+"}");else escaped.Append(character);}return escaped.ToString();}
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

// Pure bounded readiness policy, also compiled directly by the offline tests.
public enum HtkkFileDialogFocusState { Waiting, Ready, Timeout }
public sealed class HtkkFileDialogFocusGate {
 private IntPtr dialog=IntPtr.Zero,editor=IntPtr.Zero;
 private int ticks=0,stable=0;
 private bool inputStarted=false;
 public HtkkFileDialogFocusState Observe(IntPtr currentDialog,IntPtr currentEditor,bool ownsFocus){
  if(inputStarted||currentDialog==IntPtr.Zero||currentEditor==IntPtr.Zero)throw new InvalidOperationException();
  if(dialog==IntPtr.Zero){dialog=currentDialog;editor=currentEditor;}
  if(dialog!=currentDialog||editor!=currentEditor)throw new InvalidOperationException();
  if(++ticks>40)return HtkkFileDialogFocusState.Timeout;
  stable=ownsFocus?stable+1:0;
  return stable>=2?HtkkFileDialogFocusState.Ready:HtkkFileDialogFocusState.Waiting;
 }
 public void Begin(){if(inputStarted||stable<2||ticks>40)throw new InvalidOperationException();inputStarted=true;}
 public void ResetAfterSubmission(){if(!inputStarted)throw new InvalidOperationException();dialog=IntPtr.Zero;editor=IntPtr.Zero;ticks=0;stable=0;inputStarted=false;}
}
