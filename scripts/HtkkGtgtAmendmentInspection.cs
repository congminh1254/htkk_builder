// Own staged inspection of the ORIGINAL declaration Ghi prerequisite for KHBS.
// No prior declaration XML is authored and no amendment is claimed verified.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Reflection;
using System.Text;
using System.Text.RegularExpressions;
using System.Windows.Forms;
using System.Xml;
public sealed partial class HtkkGuiReferenceAutomation {
 private bool amendmentPriorSaveInvoked=false,amendmentPriorSaveSuccessAcknowledged=false,amendmentPriorDirtyCleared=false,amendmentPriorFileFresh=false,amendmentPriorFileScopeMatched=false,amendmentPriorXmlParsed=false,amendmentPriorMoneyZero=false,amendmentPriorSavedMoneyZero=false;
 private int amendmentPriorFileBytes=0,amendmentPriorSavedMoneyCount=0;private string amendmentPriorFileSha256="",amendmentPriorDirectory="";private Form amendmentPriorOwner=null;private Control amendmentPriorGrid=null;private object amendmentPriorSheet=null;
 private System.Windows.Forms.Timer amendmentPriorWatcher=null;private bool amendmentPriorObservationBusy=false;
 private string AmendmentJson(){
  string q=((char)34).ToString();StringBuilder json=new StringBuilder();
  string[] names=new string[]{"amendmentPriorSaveInvoked","amendmentPriorSaveSuccessAcknowledged","amendmentPriorDirtyCleared","amendmentPriorFileFresh","amendmentPriorFileScopeMatched","amendmentPriorXmlParsed","amendmentPriorMoneyZero","amendmentPriorSavedMoneyZero"};
  bool[] flags=new bool[]{amendmentPriorSaveInvoked,amendmentPriorSaveSuccessAcknowledged,amendmentPriorDirtyCleared,amendmentPriorFileFresh,amendmentPriorFileScopeMatched,amendmentPriorXmlParsed,amendmentPriorMoneyZero,amendmentPriorSavedMoneyZero};
  for(int index=0;index<names.Length;index++)json.Append(","+q+names[index]+q+":"+Bool(flags[index]));
  json.Append(","+q+"amendmentPriorSavedMoneyCount"+q+":"+amendmentPriorSavedMoneyCount);
  json.Append(","+q+"amendmentPriorFileBytes"+q+":"+amendmentPriorFileBytes+","+q+"amendmentPriorFileSha256"+q+":"+q+amendmentPriorFileSha256+q+","+q+"amendmentLifecycleVerified"+q+":false");return json.ToString();
 }
 private FileInfo[] OriginalPriorCandidates(){
  DirectoryInfo directory=new DirectoryInfo(amendmentPriorDirectory);if(!directory.Exists||(directory.Attributes&FileAttributes.ReparsePoint)!=0)throw new InvalidOperationException();
  FileInfo[] all=directory.GetFiles("*.xml",SearchOption.TopDirectoryOnly);if(all.Length>64)throw new InvalidOperationException();List<FileInfo> found=new List<FileInfo>();
  foreach(FileInfo file in all){if((file.Attributes&FileAttributes.ReparsePoint)!=0)throw new InvalidOperationException();if(Regex.IsMatch(file.Name,"^01_GTGT_TT80_[0-9_]+\\.xml$")&&file.Name.Length<=96)found.Add(file);}
  return found.ToArray();
 }
 private void StartOriginalAmendmentPriorSave(Form owner,Control grid,object sheet){
  if(amendmentPriorSaveInvoked)return;
  if(mode!="gtgt-amendment-inspect"||!pins||!headerMatched||!successAcknowledged||!gtgtPins||!gtgtPeriod||!gtgtIdentity||!gtgtSigner||!gtgtZero||gtgtEmptyMoney!=0||gtgtSheets!=1||!periodNoAnnexMatched||annexSelected!=0||owner.GetType().FullName!="HTKK.frmWinToKhai"||!owner.Visible||!owner.Enabled||!grid.Visible||!grid.Enabled||OriginalMessageVisible())throw new InvalidOperationException();
  object business=Global("InstanceClass");gtgtBusinessInstanceMatched=business!=null&&business.GetType().FullName=="TAX.HTKK.Business.Gtgt01TT80Nckt283";gtgtAutoCalculationReady=Convert.ToBoolean(Get(sheet,"AutoCalculation"));if(!gtgtBusinessInstanceMatched||!gtgtAutoCalculationReady)throw new InvalidOperationException();
  amendmentPriorDirectory=Path.GetFullPath(Path.Combine(Path.Combine(Path.GetDirectoryName(project),"DataFiles"),Mst));
  if(OriginalPriorCandidates().Length!=0)throw new InvalidOperationException();
  ReadSavedHeader();if(!headerMatched||headerChecks!=8||headerMismatchMask!=0)throw new InvalidOperationException();
  Button save=Named(owner,"cmdSave") as Button;if(save==null||save.FindForm()!=owner||save.Text.Replace("&",String.Empty).Trim()!="Ghi")throw new InvalidOperationException();
  amendmentPriorOwner=owner;amendmentPriorGrid=grid;amendmentPriorSheet=sheet;amendmentPriorSaveInvoked=true;stage="gtgt-original-declaration-save-invoking";Record();
  amendmentPriorWatcher=new System.Windows.Forms.Timer();amendmentPriorWatcher.Interval=100;amendmentPriorWatcher.Tick+=delegate(object sender,EventArgs args){try{ObserveOriginalAmendmentPriorSave();}catch(Exception error){amendmentPriorWatcher.Stop();Failure(error);}};
  amendmentPriorWatcher.Start();save.PerformClick();
 }
 private void ObserveOriginalAmendmentPriorSave(){
  if(finished){amendmentPriorWatcher.Stop();return;}if(amendmentPriorObservationBusy)return;amendmentPriorObservationBusy=true;
  try{
   if(mode!="gtgt-amendment-inspect"||!amendmentPriorSaveInvoked||amendmentPriorOwner==null||amendmentPriorOwner.IsDisposed||amendmentPriorOwner.GetType().FullName!="HTKK.frmWinToKhai")throw new InvalidOperationException();
   foreach(Form form in Application.OpenForms){if(!form.Visible||form.GetType().FullName!="TAX.HTKK.Utilities.Control.frmMessage")continue;
    if(form.Text.Trim()!="Thông Báo"&&form.Text.Trim()!="Thông báo")throw new InvalidOperationException();
    if(GetForegroundWindow()!=form.Handle)return;
    Control[] labels=form.Controls.Find("lblThongBao",true),buttons=form.Controls.Find("btn_2",true);
    if(amendmentPriorSaveSuccessAcknowledged||labels.Length!=1||labels[0].Text!="Đã ghi dữ liệu thành công!"||buttons.Length!=1||CountVisibleButtons(form)!=1)throw new InvalidOperationException();
    Button close=buttons[0] as Button;if(close==null||!close.Visible||!close.Enabled||close.Text.Replace("&",String.Empty).Trim()!="Đóng")throw new InvalidOperationException();
    InspectOriginalPriorFile();amendmentPriorSaveSuccessAcknowledged=true;stage="gtgt-original-declaration-save-success";Record();close.PerformClick();return;
   }
   if(!amendmentPriorSaveSuccessAcknowledged)return;
   if(!amendmentPriorOwner.Visible||!amendmentPriorOwner.Enabled||!amendmentPriorGrid.Visible||!amendmentPriorGrid.Enabled||OriginalMessageVisible())return;
   FieldInfo dirty=amendmentPriorOwner.GetType().GetField("isDataChanged",BindingFlags.Instance|BindingFlags.Public|BindingFlags.NonPublic);if(dirty==null||dirty.FieldType!=typeof(bool))throw new InvalidOperationException();
   amendmentPriorDirtyCleared=!(bool)dirty.GetValue(amendmentPriorOwner);if(!amendmentPriorDirtyCleared)return;
   InspectMoneyZero(amendmentPriorSheet);amendmentPriorMoneyZero=gtgtZero&&gtgtEmptyMoney==0;if(!amendmentPriorMoneyZero)throw new InvalidOperationException();
   InspectOriginalPriorFile();ReadSavedHeader();if(!headerMatched||headerChecks!=8||headerMismatchMask!=0)throw new InvalidOperationException();
   finished=true;stage="gtgt-original-declaration-saved-inspected";Record();amendmentPriorWatcher.Stop();
  }finally{amendmentPriorObservationBusy=false;}
 }
 private void InspectOriginalPriorFile(){
  FileInfo[] files=OriginalPriorCandidates();if(files.Length!=1||files[0].Length<2||files[0].Length>262144)throw new InvalidOperationException();
  string hash=Hash(files[0].FullName);if(amendmentPriorFileSha256.Length>0&&amendmentPriorFileSha256!=hash)throw new InvalidOperationException();
  XmlReaderSettings settings=new XmlReaderSettings();settings.ProhibitDtd=true;settings.XmlResolver=null;XmlDocument document=new XmlDocument();document.XmlResolver=null;
  using(XmlReader reader=XmlReader.Create(files[0].FullName,settings)){document.Load(reader);}amendmentPriorXmlParsed=document.DocumentElement!=null&&document.DocumentElement.Name=="Sections";
  string[] money=new string[]{"ct22","ct23","ct24","ct23a","ct24a","ct25","ct26","ct27","ct28","ct29","ct30","ct31","ct32","ct33","ct32a","ct34","ct35","ct36","ct37","ct38","ct39a","ct40a","ct40b","ct40","ct41","ct42","ct43"};
  amendmentPriorSavedMoneyCount=0;amendmentPriorSavedMoneyZero=true;XmlNodeList cells=document.SelectNodes("/Sections/Section/Cells/Cell[@Path]");
  if(cells==null||cells.Count>512)throw new InvalidOperationException();
  foreach(string code in money){int matched=0;foreach(XmlNode cell in cells){XmlAttribute path=cell.Attributes["Path"];if(path!=null&&path.Value.EndsWith("/"+code,StringComparison.Ordinal)){matched++;if(cell.Attributes["Value"]==null||cell.Attributes["Value"].Value!="0")amendmentPriorSavedMoneyZero=false;}}if(matched!=1)amendmentPriorSavedMoneyZero=false;else amendmentPriorSavedMoneyCount++;}
  if(!amendmentPriorSavedMoneyZero||amendmentPriorSavedMoneyCount!=27)throw new InvalidOperationException();
  if(!amendmentPriorXmlParsed||Hash(files[0].FullName)!=hash)throw new InvalidOperationException();amendmentPriorFileFresh=true;amendmentPriorFileScopeMatched=String.Equals(Path.GetFullPath(files[0].DirectoryName),amendmentPriorDirectory,StringComparison.OrdinalIgnoreCase);amendmentPriorFileBytes=(int)files[0].Length;amendmentPriorFileSha256=hash;
  if(!amendmentPriorFileScopeMatched)throw new InvalidOperationException();
 }
}
