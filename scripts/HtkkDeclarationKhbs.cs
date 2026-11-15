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
 private bool declarationKhbsPromptAnswered=false;
 private string webOriginalPath="",webOriginalSha256="",webPriorFilePath="",webPriorFileSha256="";
 private Stopwatch declarationKhbsClock=null;
 private bool DeclarationKhbsMode(){return modeEnum==HtkkAutomationMode.DeclarationAmendmentKhbsInspect;}
 private string DeclarationKhbsJson(){
  string q=((char)34).ToString();StringBuilder json=new StringBuilder();
  json.Append(","+q+"declarationKhbsPromptAnswered"+q+":"+Bool(declarationKhbsPromptAnswered));
  string[] names=new string[]{"declarationKhbsRound","declarationKhbsStepMask","declarationKhbsMessageId"};
  int[] counts=new int[]{declarationKhbsRound,declarationKhbsStepMask,declarationKhbsMessageId};
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
 // The saved round is closed: the original menu, period dialog (Bổ sung) and sheet steps run again for the next round.
 private void BeginDeclarationKhbsRound(){
  if(declarationKhbsRound>=declarationKhbsTarget)throw new InvalidOperationException();
  declarationKhbsStepMask|=declarationKhbsRound==0?4:128;exportWatcher.Stop();declarationKhbsRound++;declarationKhbsPromptAnswered=false;declarationKhbsClock=null;
  if(declarationKhbsRound==declarationKhbsTarget)declarationKhbsStepMask|=512;else declarationKhbsStepMask|=8;
  roundtripImportCommandInvoked=false;roundtripImportDialogMatched=false;roundtripImportKeyboardCommitted=false;roundtripImportDialogSubmitted=false;roundtripImportPathMatched=false;roundtripImportSucceeded=false;
  declarationImportClickReturned=false;declarationImportSheetMatched=false;declarationSheetObserved=false;declarationPeriodObserved=false;declarationPeriodMatched=false;declarationAnnexMatched=false;declarationClock=null;
  declarationEntryActionCount=0;declarationEntryMismatchMask=0;declarationEntryLockedMask=0;declarationEntryCellTypeMismatchMask=0;declarationEntryRowInsertCount=0;
  // A 05-1/PBT round (KhbsImportTick) chooses its Thuế tỉnh/CCT again after each import: the tick state starts afresh.
  declarationTickClock=null;declarationTickMethodPinsMatched=false;declarationTickEditsMatched=false;declarationTickTicksMatched=false;declarationTickReadbackMatched=false;
  declarationTickPlannedCount=0;declarationTickActionCount=0;declarationTickMethodPinMask=0;declarationTickReadbackMask=0;declarationTickComboMask=0;declarationTickComboListCount=0;declarationTickEntryMask=0;declarationTickEntryStartOffset=0;declarationTickEntryKeyOffset=0;
  declarationFlowStarted=false;declarationPhase="not-started";navigationPhase="decl-main-menu-again";menuStep=0;
  SetStage(HtkkAutomationStage.DeclarationKhbsReopening);Record();
 }
}
