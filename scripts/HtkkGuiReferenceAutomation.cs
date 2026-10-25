// Own reference automation, loaded only in the custom CLR2/x86 AppDomain.
// Original DLLs, EXE and configuration are never patched. No output XML is authored here.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using System.Threading;
using System.Windows.Forms;
using System.Xml;

public sealed class HtkkGuiReferenceAutomation : MarshalByRefObject {
 private const string Mst="9999999997";
 private const string FakeName="NNT KIEM THU GIA LAP - KHONG NOP";
 private const string FakeAddress="DU LIEU GIA LAP KIEM THU KHONG SU DUNG";
 private const string FakeSigner="NGUOI KY GIA LAP";
 private string result,project,mode="inspect",stage="not-started",failure="none",editorKind="not-started";
 private volatile bool finished=false,queued=false;
 private bool pins=false,mstMatched=false,initialBlank=false,editingAvailable=false,saveInvoked=false,headerExists=false,headerMatched=false;
 private int forms=0,spreads=0,rows=0,columns=0,inputCount=0,headerChecks=0;
 private readonly Dictionary<string,int> kinds=new Dictionary<string,int>();
 public override object InitializeLifetimeService(){return null;}
 private static string Hash(string path){using(FileStream stream=File.OpenRead(path))using(SHA256 hash=SHA256.Create()){StringBuilder value=new StringBuilder();foreach(byte b in hash.ComputeHash(stream))value.Append(b.ToString("x2",CultureInfo.InvariantCulture));return value.ToString();}}
 private static string Bool(bool value){return value?"true":"false";}
 private void Record(){
  string q=((char)34).ToString();StringBuilder counts=new StringBuilder();
  foreach(string key in new string[]{"form","button","combo","text","spread","other"}){if(counts.Length>0)counts.Append(',');counts.Append(q+key+q+":"+(kinds.ContainsKey(key)?kinds[key]:0).ToString(CultureInfo.InvariantCulture));}
  string json="{"+q+"format"+q+":"+q+"htkk-gui-reference-automation-v1"+q+","+q+"mode"+q+":"+q+mode+q+","+q+"stage"+q+":"+q+stage+q+","+q+"failureCategory"+q+":"+q+failure+q+","+q+"editorKind"+q+":"+q+editorKind+q+","+q+"runtime"+q+":"+q+"clr2-x86-custom-reference"+q+","+q+"sourcePinsVerified"+q+":"+Bool(pins)+","+q+"visibleForms"+q+":"+forms+","+q+"spreadCount"+q+":"+spreads+","+q+"sheetRows"+q+":"+rows+","+q+"sheetColumns"+q+":"+columns+","+q+"mstBoxesMatched"+q+":"+Bool(mstMatched)+","+q+"initialRequiredTextBlank"+q+":"+Bool(initialBlank)+","+q+"editingApiAvailable"+q+":"+Bool(editingAvailable)+","+q+"performedInputCount"+q+":"+inputCount+","+q+"originalSaveInvoked"+q+":"+Bool(saveInvoked)+","+q+"savedHeaderExists"+q+":"+Bool(headerExists)+","+q+"savedHeaderChecksMatched"+q+":"+Bool(headerMatched)+","+q+"savedHeaderCheckedFieldCount"+q+":"+headerChecks+","+q+"controlKinds"+q+":{ "+counts.ToString()+"},"+q+"realTaxpayerDataUsed"+q+":false,"+q+"runtimeRoundTrip"+q+":false}";
  File.WriteAllText(result,json,new UTF8Encoding(false));
 }
 public void Start(string requestedMode){
  if(requestedMode!="inspect"&&requestedMode!="profile-save")throw new ArgumentException();
  mode=requestedMode;string host=Assembly.GetExecutingAssembly().Location;project=Path.GetDirectoryName(host);result=host+".gui-automation.json";
  try{
   pins=Hash(Path.Combine(project,"HTKK.exe"))=="411141d2e728a45f4a35a876afb169d0ac2450de2499e8a1f43ac29ab6401938"&&Hash(Path.Combine(project,"TAX.HTKK.Business.dll"))=="281689aaa7df4db33d0debcfc61d32c0c318bb871d4a19a0277d871a7c04bba7"&&Hash(Path.Combine(project,"HTKK.exe.config"))=="b3547d6a6a61fd6e8e8b64c8976e8702aa94a2b5a44a1cf394c5486162297047"&&Hash(Path.Combine(project,"FarPoint.Win.Spread.dll"))=="2e7a0d4fc1ef6f219dd3a237ae6b26549ad03541d58da6f45d638309d2fa4c50";
   if(!pins||Environment.Version.Major!=2||IntPtr.Size!=4){stage="source-or-runtime-not-matched";finished=true;Record();return;}
   // Never reuse a source/sample/previous-run fixture directory.
   if(Directory.Exists(Path.Combine(Path.Combine(Path.GetDirectoryName(project),"DataFiles"),Mst))){stage="fixture-preexists";finished=true;Record();return;}
   stage="waiting-for-profile";Record();Thread thread=new Thread(new ThreadStart(Poll));thread.IsBackground=true;thread.SetApartmentState(ApartmentState.STA);thread.Start();
  }catch{stage="initialization-unavailable";finished=true;try{Record();}catch{}}
 }
 private void Poll(){
  Stopwatch clock=Stopwatch.StartNew();
  while(!finished&&clock.Elapsed.TotalSeconds<120){
   try{
    if(!queued&&Application.OpenForms.Count>0){
     Form dispatcher=null;
     foreach(Form form in Application.OpenForms){if(form.IsHandleCreated&&!form.IsDisposed){dispatcher=form;break;}}
     if(dispatcher!=null){queued=true;dispatcher.BeginInvoke(new MethodInvoker(delegate{try{InspectAndMaybeSave();}catch(Exception error){Failure(error);}finally{queued=false;}}));}
    }
   }catch{}
   Thread.Sleep(200);
  }
  if(!finished){stage="profile-wait-timeout";finished=true;try{Record();}catch{}}
 }
 private static bool IsSpread(Control control){for(Type type=control.GetType();type!=null;type=type.BaseType)if(type.FullName=="FarPoint.Win.Spread.FpSpread")return true;return false;}
 private void Walk(Control parent,List<Control> found,List<Button> saves,List<Button> closes,ref int visited){
  if(++visited>512)return;
  string kind=IsSpread(parent)?"spread":parent is Form?"form":parent is Button?"button":parent is ComboBox?"combo":parent is TextBoxBase?"text":"other";
  kinds[kind]=kinds.ContainsKey(kind)?kinds[kind]+1:1;
  if(IsSpread(parent)&&parent.Visible)found.Add(parent);
  Button button=parent as Button;if(button!=null&&button.Visible&&button.Enabled){string label=button.Text.Replace("&",String.Empty).Trim();if(label=="Ghi")saves.Add(button);if(label=="Đóng")closes.Add(button);}
  foreach(Control child in parent.Controls){if(visited>=512)break;Walk(child,found,saves,closes,ref visited);}
 }
 private static object Get(object target,string name){PropertyInfo property=target.GetType().GetProperty(name,BindingFlags.Public|BindingFlags.Instance);if(property==null)throw new InvalidOperationException();return property.GetValue(target,null);}
 private static object Cell(object sheet,int row,int column){object cells=Get(sheet,"Cells");PropertyInfo item=cells.GetType().GetProperty("Item",new Type[]{typeof(int),typeof(int)});if(item==null)throw new InvalidOperationException();return item.GetValue(cells,new object[]{row,column});}
 private static string CellText(object sheet,int row,int column){object value=Get(Cell(sheet,row,column),"Text");return value==null?String.Empty:Convert.ToString(value,CultureInfo.InvariantCulture);}
 private void InspectAndMaybeSave(){
  forms=0;
  foreach(Form form in Application.OpenForms){
   if(!form.Visible||form.IsDisposed)continue;forms++;
   string caption=form.Text.Replace(" ",String.Empty);
   if(caption!="Hỗ trợ kê khai thuế - Phiên bản 5.8.1".Replace(" ",String.Empty))continue;
   kinds.Clear();List<Control> found=new List<Control>();List<Button> saves=new List<Button>();List<Button> closes=new List<Button>();int visited=0;Walk(form,found,saves,closes,ref visited);spreads=found.Count;
   if(found.Count!=1||saves.Count!=1||closes.Count!=1){stage="profile-controls-not-yet-unique";Record();continue;}
   Control spread=found[0];object sheet=Get(spread,"ActiveSheet");rows=Convert.ToInt32(Get(sheet,"RowCount"));columns=Convert.ToInt32(Get(sheet,"ColumnCount"));
   if(rows<74||columns<20||rows>10000||columns>10000){stage="profile-dimensions-unmatched";finished=true;Record();return;}
   StringBuilder boxes=new StringBuilder();for(int column=2;column<12;column++)boxes.Append(CellText(sheet,1,column));mstMatched=boxes.ToString()==Mst;
   initialBlank=CellText(sheet,3,2)==String.Empty&&CellText(sheet,15,2)==String.Empty&&CellText(sheet,31,2)==String.Empty;
   editingAvailable=spread.GetType().GetMethod("StartCellEditing",new Type[]{typeof(EventArgs),typeof(bool)})!=null&&spread.GetType().GetMethod("StopCellEditing",Type.EmptyTypes)!=null&&spread.GetType().GetProperty("EditingControl")!=null&&sheet.GetType().GetMethod("SetActiveCell",new Type[]{typeof(int),typeof(int)})!=null;
   if(!mstMatched||!initialBlank){stage="fresh-synthetic-profile-not-established";finished=true;Record();return;}
   stage="profile-inspected";Record();
   if(mode=="inspect"){finished=true;return;}
   if(!editingAvailable){stage="editing-api-unavailable";finished=true;Record();return;}
   string permit=Assembly.GetExecutingAssembly().Location+".gui-automation.allow";
   if(!File.Exists(permit)||new FileInfo(permit).Length!=12||File.ReadAllText(permit,Encoding.ASCII)!="profile-save"){stage="waiting-for-profile-save-permit";Record();return;}
   Edit(spread,sheet,3,2,FakeName,false,"edit-name");
   Edit(spread,sheet,5,2,"Thành phố Hà Nội",true,"edit-province");
   Edit(spread,sheet,9,2,"Phường Sơn Tây",true,"edit-ward");
   Edit(spread,sheet,15,2,FakeAddress,false,"edit-address");
   Edit(spread,sheet,31,2,FakeSigner,false,"edit-signer");
   Edit(spread,sheet,33,2,"Thuế Thành phố Hà Nội",true,"edit-tax-authority-head");
   Edit(spread,sheet,35,2,"Thuế cơ sở 16 Thành phố Hà Nội",true,"edit-tax-authority-local");
   if(CellText(sheet,29,2)!="01/01")throw new InvalidOperationException();
   stage="original-save-invoking";saveInvoked=true;Record();
   // This is the ORIGINAL application button and its original validators/save handler.
   // A validation dialog is not dismissed automatically; the outer probe remains bounded.
   saves[0].PerformClick();
   ReadSavedHeader();finished=true;stage=headerMatched?"original-profile-saved-verified":"original-profile-save-not-verified";Record();return;
  }
 }
 private void Edit(Control spread,object sheet,int row,int column,string value,bool isCombo,string nextStage){
  stage=nextStage;Record();spread.Focus();sheet.GetType().GetMethod("SetActiveCell",new Type[]{typeof(int),typeof(int)}).Invoke(sheet,new object[]{row,column});
  spread.GetType().GetMethod("StartCellEditing",new Type[]{typeof(EventArgs),typeof(bool)}).Invoke(spread,new object[]{EventArgs.Empty,false});
  Control editor=Get(spread,"EditingControl") as Control;if(editor==null)throw new InvalidOperationException();
  if(isCombo){
   ComboBox combo=editor as ComboBox;if(combo==null){foreach(Control child in editor.Controls){if(child is ComboBox){if(combo!=null)throw new InvalidOperationException();combo=(ComboBox)child;}}}
   if(combo==null){editorKind="other-control";Record();throw new InvalidOperationException();}
   editorKind="combo";int selected=-1;
   for(int index=0;index<combo.Items.Count&&index<4096;index++){if(combo.GetItemText(combo.Items[index])==value){if(selected>=0)throw new InvalidOperationException();selected=index;}}
   if(selected<0)throw new InvalidOperationException();combo.DroppedDown=true;combo.SelectedIndex=selected;combo.DroppedDown=false;
  }else{editorKind=editor is TextBoxBase?"text-box":"other-control";editor.Text=value;}
  spread.GetType().GetMethod("StopCellEditing",Type.EmptyTypes).Invoke(spread,null);
  if(CellText(sheet,row,column)!=value)throw new InvalidOperationException();inputCount++;Record();
 }
 private void ReadSavedHeader(){
  string file=Path.Combine(Path.Combine(Path.Combine(Path.GetDirectoryName(project),"DataFiles"),Mst),"HEADER.xml");headerExists=File.Exists(file);if(!headerExists)return;
  if(new FileInfo(file).Length>2000000)throw new InvalidOperationException();XmlReaderSettings settings=new XmlReaderSettings();settings.ProhibitDtd=true;settings.XmlResolver=null;XmlDocument document=new XmlDocument();document.XmlResolver=null;
  using(XmlReader reader=XmlReader.Create(file,settings)){document.Load(reader);}Dictionary<string,string> values=new Dictionary<string,string>();foreach(XmlNode node in document.SelectNodes("//*[@PropertyInfo]")){string key=node.Attributes["PropertyInfo"].Value;if(key.Length>0){if(values.ContainsKey(key))throw new InvalidOperationException();values[key]=node.Attributes["Value"]==null?String.Empty:node.Attributes["Value"].Value;}}
  Dictionary<string,string> expected=new Dictionary<string,string>();expected["mst"]=Mst;expected["tenNNT"]=FakeName;expected["dchiNNT"]=FakeAddress;expected["nguoiKy"]=FakeSigner;expected["maTinhNNT"]="101";expected["maXaPhuongNNT"]="10129087";expected["maCQTCapCuc"]="10100";expected["maCQTNoiNop"]="10129";
  headerMatched=true;foreach(KeyValuePair<string,string> entry in expected){headerChecks++;if(!values.ContainsKey(entry.Key)||values[entry.Key]!=entry.Value)headerMatched=false;}
 }
 private void Failure(Exception error){
  for(int depth=0;depth<8&&error.InnerException!=null;depth++)error=error.InnerException;
  failure=error is TargetInvocationException?"reflection-invocation":error is InvalidOperationException?"operation-not-established":error is ArgumentException?"argument":error is System.Runtime.InteropServices.COMException?"com":error is IOException?"io":"other-standard";finished=true;try{Record();}catch{}
 }
}
