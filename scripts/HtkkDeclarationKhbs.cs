// Kê khai bổ sung (KHBS) of 01/NTNN TT80 (I9), 01/NTNN, NCCNN TT89 (Y8) and 05/KK-TNCN (L7, Z8) on the declaration driver, mode
// declaration-amendment-khbs-inspect (HTKK 5.8.2, non-gating; KHBS-NATIVE-CASE.md "01/NTNN"). C# 2.0 / CLR2.
// Rounds: 0 = the lần đầu C0 (I9: original "Nhập từ XML" of .web-original.xml; Y8: typed, the original import resets the
// Y8 tables), saved with the original Ghi and closed with the original Đóng; 1..n = the bổ sung, reopened from the original
// menu with Bổ sung, its lần (txtLan) and the fixed ngày lập 13/11/2026 (mskNgayLapKHBS), then imported (I9: .web-prior.xml
// for lần 1 of a lần-2 case, else .web-input.xml) or typed (Y8), summarised with the original "Tổng hợp KHBS"; the last
// round is exported with the original "Kết xuất" (shared declaration export path: readiness gate, selector, pinned KHBS
// schema, whole-tree comparison with the web B file). An intermediate bổ sung is saved and closed like C0. Only original
// buttons, editors and dialogs act; no business method, Cell.Value assignment or authored XML. Bounded fields only.
using System;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Reflection;
using System.Text;
using System.Windows.Forms;

public sealed partial class HtkkGuiReferenceAutomation {
 private const string DeclarationKhbsDate="13/11/2026";
 // declarationKhbsStepMask bits: 1 C0 input done, 2 C0 saved, 4 C0 closed, 8 a bổ sung round opened, 16 its input done,
 // 32 Tổng hợp KHBS acknowledged, 64 intermediate bổ sung saved, 128 it was closed, 256 the 0013 prompt answered Không,
 // 512 the last round opened, 1024 the export written.
 private int declarationKhbsRound=0,declarationKhbsTarget=0,declarationKhbsStepMask=0,declarationKhbsMessageId=0;
 // First text entry of a bổ sung round that did not take (runs 43698793633, 43698796274: Y8 round 1 entry 0, code 12). Value-free:
 // declarationKhbsEntryShape bits 1 cell empty before, 2 cell = planned before, 4 trimmed cell = planned before, 8 editor text =
 // cell text when the editor opened, 16 editor = planned after typing, 32 editor ends with planned, 64 editor starts with the
 // cell's previous text, 128 editor empty after, 256 editor kept focus, 512 the foreground window is this process, 1024 the
 // editor is a TextBoxBase, 2048 recorded, 4096 the editor holds the planned text without its first character, 8192 without
 // its last, 16384 one bounded retype was made, 32768 the retype took; declarationKhbsEntryLengths = 256 × length before
 // (≤ 255) + length after (≤ 255). Run 43705699385 (part1): 2825, lengths 30 for a 31-character text (part2: 34 of 35).
 private int declarationKhbsEntryShape=0,declarationKhbsEntryLengths=0;
 private bool declarationKhbsPromptAnswered=false;
 private string webOriginalPath="",webOriginalSha256="",webPriorFilePath="",webPriorFileSha256="";
 private Stopwatch declarationKhbsClock=null;
 // Profile Ghi of a KHBS run (cohort 1a6f600: four of five cases never saw the original success message, the fifth stopped
 // after it): every 2 s while the original save has not been acknowledged, the shared bounded wait fields record the seconds
 // since the click, the visible own forms and the foreground kind (declarationUiForegroundKind codes; 3 = an original
 // message, 4 = another own managed form, 5 = an own native #32770 dialog). Observation only; nothing is clicked here.
 private Stopwatch declarationKhbsSaveClock=null;private int declarationKhbsSaveRecorded=-1;
 private void ObserveDeclarationKhbsProfileSave(){
  if(!DeclarationKhbsMode())return;
  if(declarationKhbsSaveClock==null)declarationKhbsSaveClock=Stopwatch.StartNew();
  int seconds=Math.Min(255,(int)declarationKhbsSaveClock.Elapsed.TotalSeconds);
  if(seconds<2||seconds/2==declarationKhbsSaveRecorded)return;declarationKhbsSaveRecorded=seconds/2;
  int kind=NativeForegroundKind();
  if(kind==6){Form form=Control.FromHandle(GetForegroundWindow()) as Form;if(form!=null)kind=form.GetType().FullName=="TAX.HTKK.Utilities.Control.frmMessage"?3:4;}
  declarationUiWaitSeconds=seconds;declarationUiVisibleForms=VisibleFormCount();declarationUiForegroundKind=kind;Record();
 }
 private bool DeclarationKhbsMode(){return modeEnum==HtkkAutomationMode.DeclarationAmendmentKhbsInspect;}
 private string DeclarationKhbsJson(){
  string q=((char)34).ToString();StringBuilder json=new StringBuilder();
  json.Append(","+q+"declarationKhbsPromptAnswered"+q+":"+Bool(declarationKhbsPromptAnswered));
  string[] names=new string[]{"declarationKhbsRound","declarationKhbsStepMask","declarationKhbsMessageId","declarationKhbsEntryShape","declarationKhbsEntryLengths"};
  int[] counts=new int[]{declarationKhbsRound,declarationKhbsStepMask,declarationKhbsMessageId,declarationKhbsEntryShape,declarationKhbsEntryLengths};
  for(int index=0;index<names.Length;index++)json.Append(","+q+names[index]+q+":"+counts[index].ToString(CultureInfo.InvariantCulture));
  return json.ToString();
 }
 // Own private staged sidecars: the lần đầu file always, the previous bổ sung for a lần-2 case (fetch-htkk-web-input.py).
 private void VerifyDeclarationKhbsInputs(string host){
  declarationKhbsTarget=HtkkDeclarationCasePlans.KhbsSoLan(webCaseId);if(declarationKhbsTarget<1||declarationKhbsTarget>2)throw new InvalidOperationException();
  webOriginalPath=host+".web-original.xml";webOriginalSha256=ReadOwnHexSidecar(host+".web-original.sha256",64);ReadBoundedOriginalXml(webOriginalPath);if(Hash(webOriginalPath)!=webOriginalSha256)throw new InvalidOperationException();
  if(declarationKhbsTarget==2){webPriorFilePath=host+".web-prior.xml";webPriorFileSha256=ReadOwnHexSidecar(host+".web-prior.sha256",64);ReadBoundedOriginalXml(webPriorFilePath);if(Hash(webPriorFilePath)!=webPriorFileSha256)throw new InvalidOperationException();}
 }
 private string DeclarationImportPath(){if(!DeclarationKhbsMode())return webInputPath;return declarationKhbsRound==0?webOriginalPath:declarationKhbsRound<declarationKhbsTarget?webPriorFilePath:webInputPath;}
 private string DeclarationImportHash(){if(!DeclarationKhbsMode())return webImportInputSha256;return declarationKhbsRound==0?webOriginalSha256:declarationKhbsRound<declarationKhbsTarget?webPriorFileSha256:webImportInputSha256;}
 // Bổ sung rounds of the original period dialog (frmHTKKPeriod.CheckPeriodKhbs needs the saved previous file, 0107/0296).
 private bool ConfigureDeclarationKhbsPeriod(Control period){
  SetCheck(Named(period,"OptBosung"),true);
  string lan=declarationKhbsRound.ToString(CultureInfo.InvariantCulture);
  if(ReadableNamed(period,"txtLan").Text.Trim()!=lan)SetText(period,"txtLan",lan);
  SetText(period,"mskNgayLapKHBS",DeclarationKhbsDate);
  return CheckValue(Named(period,"OptBosung"))&&!CheckValue(ReadableNamed(period,"OptChinhthuc"))&&ReadableNamed(period,"txtLan").Text.Trim()==lan&&KhbsDate(ReadableNamed(period,"mskNgayLapKHBS").Text);
 }
 private void DeclarationKhbsStop(HtkkAutomationStage stage){DeclarationTerminal(stage);}
 private bool DeclarationKhbsTimedOut(double seconds){
  if(declarationKhbsClock==null)declarationKhbsClock=Stopwatch.StartNew();
  if(declarationKhbsClock.Elapsed.TotalSeconds<seconds)return false;
  DeclarationKhbsStop(HtkkAutomationStage.DeclarationKhbsTimeout);return true;
 }
 // The round's input (import or entry) and the sheet checks passed.
 private void DeclarationKhbsInputDone(){
  declarationKhbsStepMask|=declarationKhbsRound==0?1:16;declarationKhbsClock=null;
  declarationPhase=declarationKhbsRound==0?"khbs-save-ready":"khbs-summary-ready";SetStage(declarationKhbsRound==0?HtkkAutomationStage.DeclarationKhbsSaving:HtkkAutomationStage.DeclarationKhbsSummaryWaiting);Record();
 }
 private void DeclarationKhbsExported(bool matched){
  declarationKhbsStepMask|=1024;
  DeclarationTerminal(matched?HtkkAutomationStage.DeclarationKhbsInspected:HtkkAutomationStage.DeclarationExportNotMatched);
 }
 private void DeclarationKhbsClick(string name,string text,string next,HtkkAutomationStage stage){
  Button button=Named(roundtripOwner,name) as Button;
  if(button==null||button.FindForm()!=roundtripOwner||!button.Visible||!button.Enabled||button.Text.Replace("&",String.Empty).Trim()!=text)throw new InvalidOperationException();
  declarationPhase=next;declarationKhbsClock=null;SetStage(stage);Record();
  roundtripOwner.BeginInvoke(new MethodInvoker(delegate{try{button.PerformClick();}catch(Exception error){Failure(error);}}));
 }
 private void ContinueDeclarationKhbs(){
  if(!DeclarationKhbsMode())throw new InvalidOperationException();
  string text;Form message;
  if(declarationPhase=="khbs-save-ready"){if(!OriginalRoundtripOwnerReady())return;DeclarationKhbsClick("cmdSave","Ghi","khbs-save-result",HtkkAutomationStage.DeclarationKhbsSaving);return;}
  if(declarationPhase=="khbs-save-result"){
   message=KhbsMessage(out text);if(message==null){DeclarationKhbsTimedOut(60);return;}
   if(text!="Đã ghi dữ liệu thành công!"){declarationKhbsMessageId=OriginalMessageCatalogueId(text);DeclarationKhbsStop(HtkkAutomationStage.DeclarationKhbsStepRejected);return;}
   declarationKhbsStepMask|=declarationKhbsRound==0?2:64;declarationPhase="khbs-close-ready";declarationKhbsClock=Stopwatch.StartNew();SetStage(HtkkAutomationStage.DeclarationKhbsClosing);Record();CloseKhbsMessage(message);return;
  }
  if(declarationPhase=="khbs-close-ready"){
   // cmdSave_Click clears isDataChanged after the message; a grid event may set it again (D1 run 43367487266): 2 s settle,
   // then the original Đóng, whose 0013 prompt is answered Không (the file was just saved).
   if(!OriginalRoundtripOwnerReady()||declarationKhbsClock.Elapsed.TotalSeconds<2){if(declarationKhbsClock.Elapsed.TotalSeconds>=30)DeclarationKhbsStop(HtkkAutomationStage.DeclarationKhbsTimeout);return;}
   DeclarationKhbsClick("cmdExit","Đóng","khbs-closing",HtkkAutomationStage.DeclarationKhbsClosing);return;
  }
  if(declarationPhase=="khbs-closing"){
   message=KhbsMessage(out text);
   if(message!=null){
    if(declarationKhbsPromptAnswered||text!="Có muốn ghi lại thông tin thay đổi không?"){declarationKhbsMessageId=OriginalMessageCatalogueId(text);DeclarationKhbsStop(HtkkAutomationStage.DeclarationKhbsStepRejected);return;}
    Control[] buttons=message.Controls.Find("btn_2",true);Button no=buttons.Length==1?buttons[0] as Button:null;
    if(no==null||CountVisibleButtons(message)!=3||!no.Visible||!no.Enabled||no.Text.Replace("&",String.Empty).Trim()!="Không")throw new InvalidOperationException();
    declarationKhbsPromptAnswered=true;declarationKhbsStepMask|=256;Record();no.PerformClick();return;
   }
   if(roundtripOwner.IsDisposed||!roundtripOwner.Visible){BeginDeclarationKhbsRound();return;}
   DeclarationKhbsTimedOut(60);return;
  }
  if(declarationPhase=="khbs-summary-ready"){if(!OriginalRoundtripOwnerReady())return;DeclarationKhbsClick("btnTongHopKHBS","Tổng hợp KHBS","khbs-summary-result",HtkkAutomationStage.DeclarationKhbsSummaryWaiting);return;}
  if(declarationPhase=="khbs-summary-result"){
   message=KhbsMessage(out text);if(message==null){DeclarationKhbsTimedOut(60);return;}
   if(text!="Tổng hợp dữ liệu lên KHBS thành công"){declarationKhbsMessageId=OriginalMessageCatalogueId(text);DeclarationKhbsStop(HtkkAutomationStage.DeclarationKhbsStepRejected);return;}
   declarationKhbsStepMask|=32;
   if(declarationKhbsRound<declarationKhbsTarget){declarationPhase="khbs-save-ready";SetStage(HtkkAutomationStage.DeclarationKhbsSaving);}
   else{declarationPhase="export-start";SetStage(HtkkAutomationStage.DeclarationExportReadyWaiting);}
   Record();CloseKhbsMessage(message);return;
  }
  throw new InvalidOperationException();
 }
 // A bổ sung round's sheet opens with the values HTKK loaded from the saved previous version (runs 43686717364 and
 // 43686719047: Y8 round 1 failed at entry 0, code 12, because the planned text was typed into a cell that already held it).
 // A planned cell that already holds exactly its planned value is left as HTKK loaded it and counted; any other cell is typed
 // as in C0. Read only: nothing is clicked, typed or assigned here.
 private bool DeclarationKhbsEntryHeld(object sheet,object cell,string kind,string[] parts,int row,int column){
  if(!DeclarationKhbsMode()||declarationKhbsRound==0)return false;
  if(kind=="text")return CellText(sheet,row,column)==parts[2];
  if(kind=="number")return DeclarationEntryNumber(cell,parts[2]);
  if(kind=="date"||kind=="date-optional")return DeclarationEntryDate(cell,parts[2]);
  if(kind=="combo"){int[] code=DeclarationEntryCell(parts[5]);return CellText(sheet,row,column)==parts[4]&&CellText(sheet,code[0],code[1])==parts[6];}
  return false;
 }
 private static void DeclarationKhbsSettle(){for(int turn=0;turn<5;turn++){Application.DoEvents();System.Threading.Thread.Sleep(20);}}
 private void ObserveDeclarationKhbsEntry(string before,string opened,Control editor,string value){
  if(!DeclarationKhbsMode()||declarationKhbsRound==0||(declarationKhbsEntryShape&2048)!=0)return;
  string after=editor.Text??String.Empty;before=before??String.Empty;opened=opened??String.Empty;int shape=2048;
  if(before.Length==0)shape|=1;if(before==value)shape|=2;if(before.Trim()==value)shape|=4;if(opened==before)shape|=8;
  if(after==value)shape|=16;if(after.EndsWith(value,StringComparison.Ordinal))shape|=32;if(before.Length>0&&after.StartsWith(before,StringComparison.Ordinal))shape|=64;
  if(after.Length==0)shape|=128;if(editor.ContainsFocus)shape|=256;int kind=NativeForegroundKind();if(kind!=7&&kind!=8)shape|=512;if(editor is TextBoxBase)shape|=1024;
  if(value.Length>1&&after==value.Substring(1))shape|=4096;if(value.Length>1&&after==value.Substring(0,value.Length-1))shape|=8192;
  declarationKhbsEntryShape=shape;declarationKhbsEntryLengths=Math.Min(255,before.Length)*256+Math.Min(255,after.Length);
 }
 // The saved round is closed: the original menu, period dialog (Bổ sung) and sheet steps run again for the next round.
 private void BeginDeclarationKhbsRound(){
  if(declarationKhbsRound>=declarationKhbsTarget)throw new InvalidOperationException();
  declarationKhbsStepMask|=declarationKhbsRound==0?4:128;exportWatcher.Stop();declarationKhbsRound++;declarationKhbsPromptAnswered=false;declarationKhbsClock=null;
  if(declarationKhbsRound==declarationKhbsTarget)declarationKhbsStepMask|=512;else declarationKhbsStepMask|=8;
  roundtripImportCommandInvoked=false;roundtripImportDialogMatched=false;roundtripImportKeyboardCommitted=false;roundtripImportDialogSubmitted=false;roundtripImportPathMatched=false;roundtripImportSucceeded=false;
  declarationImportClickReturned=false;declarationImportSheetMatched=false;declarationSheetObserved=false;declarationPeriodObserved=false;declarationPeriodMatched=false;declarationAnnexMatched=false;declarationClock=null;
  declarationEntryActionCount=0;declarationEntryComboCount=0;declarationEntryMismatchMask=0;declarationEntryLockedMask=0;declarationEntryCellTypeMismatchMask=0;declarationEntryRowInsertCount=0;
  // A 05-1/PBT round (KhbsImportTick) chooses its Thuế tỉnh/CCT again after each import: the tick state starts afresh.
  declarationTickClock=null;declarationTickMethodPinsMatched=false;declarationTickEditsMatched=false;declarationTickTicksMatched=false;declarationTickReadbackMatched=false;
  declarationTickPlannedCount=0;declarationTickActionCount=0;declarationTickMethodPinMask=0;declarationTickReadbackMask=0;declarationTickComboMask=0;declarationTickComboListCount=0;declarationTickEntryMask=0;declarationTickEntryStartOffset=0;declarationTickEntryKeyOffset=0;
  declarationFlowStarted=false;declarationPhase="not-started";navigationPhase="decl-main-menu-again";menuStep=0;
  SetStage(HtkkAutomationStage.DeclarationKhbsReopening);Record();
 }
}
