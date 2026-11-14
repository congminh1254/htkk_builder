// Own bounded ORIGINAL amendment (kê khai bổ sung lần 1, KHBS) observation of D1 01/GTGT 2.8.3 on HTKK 5.8.2.
// Flow (KHBS-NATIVE-CASE.md): C0 Ghi (HtkkGtgtAmendmentInspection.cs; zero, or for case 2 two fixed original edits)
// -> original Đóng -> reopen D1 10/2026 (case 2: 09/2026) with
// OptBosung and the fixed ngày lập 13/11/2026 (HtkkGtgtAmendmentOpenInspection.cs) -> original "Nhập từ XML" of the
// fixed web B1 file (cmdImportXML_Click 0x060003AC: LoaiToKhai B -> RevertFromXml, message 0291) -> original
// "Tổng hợp KHBS" (btnTongHopKHBS_Click 0x060003C1, message 0222) -> original "Kết xuất" XML -> whole-tree comparison
// with the web input. No XML is authored here. Only booleans, counts, message ids, a mismatch mask and the first
// differing leaf ordinal are recorded; never values, paths or text.
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
 private const string KhbsWebCaseId="01GTGT-khbs-zero-to-sale10-M10-2026";
 // Case 2 (htkk_web producer khbs-sale5-to-sale10): M09/2026, due 20/10/2026, so the same fixed ngày lập gives 24 late
 // days. Its C0 is typed through the original grid before Ghi ([30] 2.000.000 at 5%, [32] 1.000.000 at 10%), and the web
 // B1 file moves [30] to 0 and [32] to 4.000.000 (negative chênh lệch rows [30]/[31]).
 private const string KhbsSale5WebCaseId="01GTGT-khbs-sale5-to-sale10-M09-2026";
 private const string KhbsFixedDate="13/11/2026";
 // 270 (case 1) / 296 (case 2) leaves of the fixed web B1 file without the four TTinDVu leaves.
 private const int KhbsLeafTarget=270,KhbsSale5LeafTarget=296;
 // Case 3 (htkk_web producer khbs-lan2-sale10): bổ sung LẦN 2 of M10/2026. Round 1 is case 1 (C0 zero, Ghi, Đóng, B1 with
 // the fixed ngày lập) except that B1 imports the staged previous-version file (the exact case-1 web file, .web-prior.xml),
 // runs Tổng hợp KHBS and is SAVED with the original Ghi (HTKK writes bs1_<C0 file name>, the file CheckPeriodKhbs 0x060004F6
 // requires for lần 2, Message 0296) and closed with Đóng. Round 2 reopens D1 with Bổ sung lần 2, imports the web B2 file,
 // summarises and exports; the whole tree is compared with the B2 file (270 leaves). HTKK's lần trước of round 2 is the saved
 // B1 main sheet (ReadSheet_LanTruoc), so the B2 sheet opens with the B1 vector ([32] 1.000.000) or zero (khbsOpenMainState 3/1).
 private const string KhbsLan2WebCaseId="01GTGT-khbs-lan2-sale10-M10-2026";
 private const string KhbsPriorB1FileName="bs1_01_GTGT_TT80_CQTQL10129_00_102026_283.xml";
 private static readonly decimal[] KhbsSale10B1=new decimal[]{0,0,0,0,0,0,0,1000000,100000,0,0,0,1000000,100000,0,1000000,100000,100000,0,0,0,100000,0,100000,0,0,0};
 private int khbsRound=0,khbsPriorSaveMessageId=0;private string webPriorPath="",webPriorSha256="",khbsPriorFileSha256="";
 private bool khbsPriorImportSucceeded=false,khbsPriorSummaryAcknowledged=false,khbsPriorSaveAcknowledged=false,khbsPriorFileSaved=false,khbsRound2Opened=false;private Stopwatch khbsPriorCloseClock=null;
 // Case 4 (htkk_web producer khbs-annex12-capture): an ORACLE CAPTURE, not a port check. C0 is case 1's zero declaration
 // without annex; B1 is opened with phụ lục 01-2/GTGT selected in the period dialog and imports the web B1 file carrying the
 // proven two-plant 01-2 annex (annex12-two-plants) and only the main-sheet 01-1/KHBS group. After the original import the
 // head CQT display of every child row is restored through the original combos exactly as the proven annex web case does
 // (RestoreImportedAnnex12HeadAuthorities; HTKK 0016 otherwise), then Tổng hợp KHBS computes the annex hồ sơ group and the
 // Muc_I.2 phân bổ, the export is compared and retained raw. Run 43428877607 captured HTKK's output (then an expected
 // mismatch); the web producer now writes the annex group and Muc_I.2 as captured, so the whole tree (504 leaves) must match.
 private const string KhbsAnnex12CaptureCaseId="01GTGT-khbs-annex12-capture-M10-2026";
 private const int KhbsAnnex12CaptureLeafTarget=504;
 // Case 5 (htkk_web producer khbs-annex12-lan2-changed): ORACLE CAPTURE of a CHANGED allocation, bổ sung lần 2. C0 is case 1's
 // zero declaration without annex; round 1 is case 4's B1 (01-2 selected, the capture case's exact web file imported, head CQTs
 // restored, Tổng hợp) saved with Ghi as case 3 does; round 2 opens B2 with 01-2 selected (or already selected by HTKK from the
 // saved B1), imports the web B2 file whose annex moves plant 1's [11] to 40/60, restores, summarises, exports and compares.
 // Run 43454661870 captured HTKK's output (then a mismatch); the web now writes it as captured, so the tree must match.
 private const string KhbsAnnex12Lan2CaseId="01GTGT-khbs-annex12-lan2-changed-M10-2026";
 private const int KhbsAnnex12Lan2LeafTarget=465;
 // Cases 6-9 (htkk_web producers khbs-annex12-lan2-add-plant/-remove-plant/-two-places/-ct10): ORACLE CAPTURES of the WIDER
 // annex scope, exactly case 5's two rounds (round 1 = the capture case's exact B1, saved); round 2 imports a B2 annex variant
 // (htkk_annex12_web_cases VARIANTS): a third plant 99996 at 60/40 ([10] 5); plant 2 removed; plant 2's rows 2-3 at a second
 // place (Xã Phúc Lộc 10131091, Thuế cơ sở 25 Thành phố Hà Nội 10131); plant 2's [10] 4. The web file's annex hồ sơ group and
 // Muc_I.2 are htkk_web's static reading (computeKhbsAnnex12Wide): a mismatch is possible and the raw export is retained.
 private const string KhbsAnnex12AddPlantCaseId="01GTGT-khbs-annex12-lan2-add-plant-M10-2026";
 private const int KhbsAnnex12AddPlantLeafTarget=527;
 private const string KhbsAnnex12RemovePlantCaseId="01GTGT-khbs-annex12-lan2-remove-plant-M10-2026";
 private const int KhbsAnnex12RemovePlantLeafTarget=362;
 private const string KhbsAnnex12TwoPlacesCaseId="01GTGT-khbs-annex12-lan2-two-places-M10-2026";
 private const int KhbsAnnex12TwoPlacesLeafTarget=478;
 private const string KhbsAnnex12Ct10CaseId="01GTGT-khbs-annex12-lan2-ct10-M10-2026";
 private const int KhbsAnnex12Ct10LeafTarget=452;
 private static bool KhbsAnnexWideCaseId(string id){return id==KhbsAnnex12AddPlantCaseId||id==KhbsAnnex12RemovePlantCaseId||id==KhbsAnnex12TwoPlacesCaseId||id==KhbsAnnex12Ct10CaseId;}
 private static int KhbsAnnexWideLeafTarget(string id){return id==KhbsAnnex12AddPlantCaseId?KhbsAnnex12AddPlantLeafTarget:id==KhbsAnnex12RemovePlantCaseId?KhbsAnnex12RemovePlantLeafTarget:id==KhbsAnnex12TwoPlacesCaseId?KhbsAnnex12TwoPlacesLeafTarget:id==KhbsAnnex12Ct10CaseId?KhbsAnnex12Ct10LeafTarget:-1;}
 // Case 5 and cases 6-9 share the annex lần 2 flow.
 private bool KhbsAnnexLan2Case(){return KhbsMode()&&webInputVerified&&(webCaseId==KhbsAnnex12Lan2CaseId||KhbsAnnexWideCaseId(webCaseId));}
 private bool KhbsAnnexCase(){return KhbsMode()&&webInputVerified&&(webCaseId==KhbsAnnex12CaptureCaseId||webCaseId==KhbsAnnex12Lan2CaseId||KhbsAnnexWideCaseId(webCaseId));}
 private static bool KhbsCaseId(string id){return id==KhbsWebCaseId||id==KhbsSale5WebCaseId||id==KhbsLan2WebCaseId||id==KhbsAnnex12CaptureCaseId||id==KhbsAnnex12Lan2CaseId||KhbsAnnexWideCaseId(id);}
 // The lần 2 flow (round 1 imports, summarises and saves the previous-version B1, round 2 opens B2): cases 3, 5 and 6-9.
 private bool KhbsLan2Case(){return KhbsMode()&&webInputVerified&&(webCaseId==KhbsLan2WebCaseId||webCaseId==KhbsAnnex12Lan2CaseId||KhbsAnnexWideCaseId(webCaseId));}
 // The 01-2 percentages the imported annex must show: the proven two-plant annex, or in case 5's round 2 plant 1 at 40/60.
 private decimal[] KhbsAnnexFirstPlantPercentages(){return KhbsAnnexLan2Case()&&khbsRound==2?new decimal[]{40m,60m}:new decimal[]{33.33m,66.67m};}
 private string KhbsSoLan(){return KhbsLan2Case()?"2":"1";}
 private bool KhbsImportingPrior(){return KhbsLan2Case()&&khbsRound==1;}
 private string KhbsImportPath(){return KhbsImportingPrior()?webPriorPath:webInputPath;}
 private string KhbsImportHash(){return KhbsImportingPrior()?webPriorSha256:webImportInputSha256;}
 private bool KhbsB1Vector(object sheet){
  int[,] coordinates=new int[,] {{36,11},{39,9},{39,11},{40,9},{40,11},{41,11},{43,9},{44,9},{44,11},{45,9},{46,9},{46,11},{47,9},{47,11},{48,9},{49,9},{49,11},{50,11},{52,11},{53,11},{54,11},{56,11},{57,11},{58,11},{59,11},{60,11},{61,11}};
  for(int index=0;index<coordinates.GetLength(0);index++){decimal number;if(!KhbsAmount(Get(Cell(sheet,coordinates[index,0],coordinates[index,1]),"Value"),out number)||number!=KhbsSale10B1[index])return false;}
  return true;
 }
 private void InspectKhbsPriorSavedFile(){
  string directory=Path.GetFullPath(Path.Combine(Path.Combine(Path.GetDirectoryName(project),"DataFiles"),Mst));FileInfo file=new FileInfo(Path.Combine(directory,KhbsPriorB1FileName));
  if(!file.Exists||(file.Attributes&FileAttributes.ReparsePoint)!=0||file.Length<2||file.Length>262144||!String.Equals(Path.GetFullPath(file.DirectoryName),directory,StringComparison.OrdinalIgnoreCase))throw new InvalidOperationException();
  khbsPriorFileSha256=Hash(file.FullName);khbsPriorFileSaved=true;
 }
 private void TypeOriginalKhbsRound2(Control period){
  if(!KhbsLan2Case()||khbsRound!=2||!khbsRound2Opened||!amendmentOpenDefaultsMatched)throw new InvalidOperationException();
  SetText(period,"txtLan","2");if(ReadableNamed(period,"txtLan").Text.Trim()!="2")throw new InvalidOperationException();
 }
 // Round 2 begins once the saved B1 form is closed: the reopen goes through the same menu and period steps as round 1.
 private void BeginKhbsRound2(){
  if(!KhbsLan2Case()||khbsRound!=1||!khbsPriorSaveAcknowledged||!khbsPriorFileSaved)throw new InvalidOperationException();
  // The saved B1 must still be the bytes HTKK wrote at Ghi (the Đóng path never saves again).
  string saved=khbsPriorFileSha256;InspectKhbsPriorSavedFile();if(khbsPriorFileSha256!=saved)throw new InvalidOperationException();
  exportWatcher.Stop();khbsRound=2;khbsPhase="not-started";khbsDateTyped=false;khbsPeriodMatched=false;khbsImportPathMatched=false;khbsDirtyAfterSave=false;khbsDiscardPromptAnswered=false;
  roundtripImportDialogMatched=false;roundtripImportKeyboardCommitted=false;roundtripImportDialogSubmitted=false;roundtripImportPathMatched=false;roundtripImportSucceeded=false;
  amendmentOpenConfirmInvoked=false;amendmentOpenPeriodMatched=false;amendmentOpenKhbsSheetsObserved=false;amendmentOpenPriorUnchanged=false;
  // Case 5: round 2 selects (or finds selected) phụ lục 01-2 again and imports, checks and restores the changed B2 annex.
  if(KhbsAnnexLan2Case()){annex12SelectionActionCount=0;annexSelected=0;periodAnnex12Matched=false;annex12WebImportSheetMatched=false;annex12WebHeadAuthorityRestored=false;annex12WebHeadAuthorityRepairCount=0;annex12WebHeadAuthorityFailureMask=0;annex12WebHeadAuthorityComboMask=0;annex12WebImportDisplayEmptyMask=0;annex12WebImportGroupCount=0;annex12WebImportRowCount=0;}
  khbsRound2Opened=true;navigationPhase="waiting-main-menu";menuStep=0;SetStage(HtkkAutomationStage.GtgtAmendmentKhbsRound2Opening);Record();
 }
 private bool KhbsNonzeroOriginal(){return KhbsMode()&&webInputVerified&&webCaseId==KhbsSale5WebCaseId;}
 // The only period month of the D1 drivers: 10, or 09 for KHBS case 2 (GetPeriodInfo pads Thang to two digits, 0x0efc).
 private string PeriodMonth(){return KhbsNonzeroOriginal()?"09":"10";}
 // Exact C0 money of case 2 in the fixed 27-indicator order of InspectMoneyZero / InspectOriginalPriorFile
 // (ct22 ... ct43): [27] 3.000.000, [28] 200.000, [30] 2.000.000, [31] 100.000, [32] 1.000.000, [33] 100.000,
 // [34] 3.000.000, [35] 200.000, [36] 200.000, [40a] 200.000, [40] 200.000.
 private static readonly decimal[] KhbsSale5Original=new decimal[]{0,0,0,0,0,0,0,3000000,200000,0,2000000,100000,1000000,100000,0,3000000,200000,200000,0,0,0,200000,0,200000,0,0,0};
 private bool khbsOriginalMoneyMatched=false,khbsSavedMoneyMatched=false;private int khbsOpenMainState=0;
 private static bool KhbsAmount(object value,out decimal number){
  number=Decimal.Zero;if(value==null||value==DBNull.Value)return false;string text=Convert.ToString(value,CultureInfo.InvariantCulture);
  return Decimal.TryParse(text,NumberStyles.Number,CultureInfo.InvariantCulture,out number);
 }
 private bool KhbsOriginalVector(object sheet){
  int[,] coordinates=new int[,] {{36,11},{39,9},{39,11},{40,9},{40,11},{41,11},{43,9},{44,9},{44,11},{45,9},{46,9},{46,11},{47,9},{47,11},{48,9},{49,9},{49,11},{50,11},{52,11},{53,11},{54,11},{56,11},{57,11},{58,11},{59,11},{60,11},{61,11}};
  for(int index=0;index<coordinates.GetLength(0);index++){decimal number;if(!KhbsAmount(Get(Cell(sheet,coordinates[index,0],coordinates[index,1]),"Value"),out number)||number!=KhbsSale5Original[index])return false;}
  return true;
 }
 // After the original Ghi success message: the bounded wait mask of the readiness conditions (1 owner hidden, 2 owner
 // disabled, 4 grid hidden, 8 grid disabled, 16 original message visible, 32 isDataChanged still set; 64 = the success
 // message itself was never acknowledged, KhbsSaveWaitBounded). Run 43367487266
 // (case 2) stayed here after a correct non-zero save. Case 2 only: when the dirty flag alone stays set for 2 s while the
 // sheet still holds the exact C0 vector, the close continues through HTKK's own 0013 prompt (StartKhbsDiscardPromptWatcher).
 // Anything else ends after 30 s with gtgt-amendment-khbs-post-save-timeout instead of the whole automation limit.
 private bool khbsDirtyAfterSave=false,khbsDiscardPromptAnswered=false;private int khbsPostSaveWaitMask=0;private Stopwatch khbsPostSaveClock=null;
 private bool KhbsPostSaveReady(){
  if(!KhbsMode()||!amendmentPriorSaveSuccessAcknowledged||amendmentPriorOwner==null||amendmentPriorOwner.IsDisposed)throw new InvalidOperationException();
  if(khbsPostSaveClock==null)khbsPostSaveClock=Stopwatch.StartNew();
  FieldInfo dirty=amendmentPriorOwner.GetType().GetField("isDataChanged",BindingFlags.Instance|BindingFlags.Public|BindingFlags.NonPublic);if(dirty==null||dirty.FieldType!=typeof(bool))throw new InvalidOperationException();
  int mask=(amendmentPriorOwner.Visible?0:1)|(amendmentPriorOwner.Enabled?0:2)|(amendmentPriorGrid.Visible?0:4)|(amendmentPriorGrid.Enabled?0:8)|(OriginalMessageVisible()?16:0)|((bool)dirty.GetValue(amendmentPriorOwner)?32:0);
  if(mask!=khbsPostSaveWaitMask){khbsPostSaveWaitMask=mask;SetStage(HtkkAutomationStage.GtgtAmendmentKhbsPostSaveWaiting);Record();}
  if(mask==0)return true;
  if(mask==32&&KhbsNonzeroOriginal()&&khbsPostSaveClock.Elapsed.TotalSeconds>=2){
   InspectMoneyZero(amendmentPriorSheet);if(gtgtEmptyMoney!=0||!KhbsOriginalVector(amendmentPriorSheet))throw new InvalidOperationException();
   khbsDirtyAfterSave=true;Record();return true;
  }
  if(khbsPostSaveClock.Elapsed.TotalSeconds>=30){finished=true;SetStage(HtkkAutomationStage.GtgtAmendmentKhbsPostSaveTimeout);Record();amendmentPriorWatcher.Stop();}
  return false;
 }
 // KHBS mode: the wait for the original 0002 success message (Ghi -> message -> acknowledged) is bounded too: 60 s after
 // Ghi without the acknowledged message ends with gtgt-amendment-khbs-post-save-timeout and wait mask bit 64 (no ack).
 private Stopwatch khbsSaveClock=null;
 private bool KhbsSaveWaitBounded(){
  if(khbsSaveClock==null)khbsSaveClock=Stopwatch.StartNew();
  if(amendmentPriorSaveSuccessAcknowledged||khbsSaveClock.Elapsed.TotalSeconds<60)return true;
  khbsPostSaveWaitMask|=64;finished=true;SetStage(HtkkAutomationStage.GtgtAmendmentKhbsPostSaveTimeout);Record();amendmentPriorWatcher.Stop();return false;
 }
 private System.Windows.Forms.Timer StartKhbsDiscardPromptWatcher(){
  if(!KhbsNonzeroOriginal()||!khbsDirtyAfterSave)throw new InvalidOperationException();
  System.Windows.Forms.Timer watcher=new System.Windows.Forms.Timer();watcher.Interval=100;
  watcher.Tick+=delegate(object sender,EventArgs args){try{AnswerKhbsDiscardPrompt();}catch(Exception error){watcher.Stop();Failure(error);}};watcher.Start();return watcher;
 }
 // Pinned frmMessage style 6 (TAX.HTKK.Utilities Message): btn_1 Có (cmd_OK), btn_2 Không (cmd_No), btn_3 Hủy bỏ.
 private void AnswerKhbsDiscardPrompt(){
  if(khbsDiscardPromptAnswered)return;string text;Form message=KhbsMessage(out text);if(message==null)return;
  SetStage(HtkkAutomationStage.GtgtAmendmentKhbsDiscardPromptWaiting);Record();if(GetForegroundWindow()!=message.Handle)return;
  Control[] buttons=message.Controls.Find("btn_2",true);
  if(text!="Có muốn ghi lại thông tin thay đổi không?"||buttons.Length!=1||CountVisibleButtons(message)!=3)throw new InvalidOperationException();
  Button no=buttons[0] as Button;if(no==null||!no.Visible||!no.Enabled||no.Text.Replace("&",String.Empty).Trim()!="Không")throw new InvalidOperationException();
  khbsDiscardPromptAnswered=true;Record();no.PerformClick();
 }
 private bool PriorSavedMoneyExpected(){return KhbsNonzeroOriginal()?khbsSavedMoneyMatched:amendmentPriorSavedMoneyZero;}
 // Case 2 only, on the proven zero C0 sheet: two fixed original edits, each committed through the original editor and
 // waited for the original auto-calculation; true once the whole fixed C0 vector is on the sheet (then Ghi).
 private bool PrepareKhbsOriginal(Form owner,Control grid,object sheet){
  gtgtAutoCalculationReady=Convert.ToBoolean(Get(sheet,"AutoCalculation"));object business=Global("InstanceClass");gtgtBusinessInstanceMatched=business!=null&&business.GetType().FullName=="TAX.HTKK.Business.Gtgt01TT80Nckt283";
  if(!KhbsNonzeroOriginal()||amendmentPriorSaveInvoked)throw new InvalidOperationException();
  if(!gtgtAutoCalculationReady||!gtgtBusinessInstanceMatched||!owner.Enabled||!grid.Enabled||OriginalMessageVisible()){SetStage(HtkkAutomationStage.WaitingGtgtSheet);Record();return false;}
  if(webCaseEditCount==0){
   if(!gtgtZero||gtgtEmptyMoney!=0||Convert.ToBoolean(Get(Cell(sheet,46,9),"Locked")))throw new InvalidOperationException();
   webCaseEdited=true;webCaseEditClock=Stopwatch.StartNew();EditOriginalGtgtCase(grid,sheet,46,9,"2000000",HtkkAutomationStage.GtgtCaseEditing);return false;
  }
  if(webCaseEditCount==1){
   decimal tax;if(!KhbsAmount(Get(Cell(sheet,46,11),"Value"),out tax)||tax!=100000){if(webCaseEditClock.Elapsed.TotalSeconds<2){SetStage(HtkkAutomationStage.WaitingGtgtSheet);Record();return false;}throw new InvalidOperationException();}
   if(Convert.ToBoolean(Get(Cell(sheet,47,9),"Locked")))throw new InvalidOperationException();
   webCaseEditClock=Stopwatch.StartNew();EditOriginalGtgtCase(grid,sheet,47,9,"1000000",HtkkAutomationStage.GtgtCaseEditing);return false;
  }
  if(webCaseEditCount!=2)throw new InvalidOperationException();
  khbsOriginalMoneyMatched=gtgtEmptyMoney==0&&KhbsOriginalVector(sheet);
  if(!khbsOriginalMoneyMatched){if(webCaseEditClock.Elapsed.TotalSeconds<2){SetStage(HtkkAutomationStage.WaitingGtgtSheet);Record();return false;}throw new InvalidOperationException();}
  return true;
 }
 private bool khbsDateTyped=false,khbsPeriodMatched=false,khbsImportInvoked=false,khbsImportSucceeded=false,khbsImportPathMatched=false,khbsSummaryInvoked=false,khbsSummaryAcknowledged=false,khbsExportInvoked=false,khbsExportSchemaPinnedVerified=false,khbsExportSucceeded=false,khbsIdentityMatched=false,khbsCreationDateValid=false,khbsTreeMatched=false;
 private int khbsImportMessageId=0,khbsSummaryMessageId=0,khbsExportMessageId=0,khbsLeafCount=0,khbsMismatchMask=0,khbsFirstDifferenceOrdinal=0,khbsExportBytes=0;
 private string khbsExportSha256="",khbsPhase="not-started";private Form khbsOwner=null;private bool khbsBusy=false;
 private bool KhbsMode(){return mode=="gtgt-amendment-khbs-inspect";}
 private static bool KhbsDate(string text){DateTime parsed;return DateTime.TryParseExact(text,new string[]{"d/M/yyyy","dd/MM/yyyy"},CultureInfo.InvariantCulture,DateTimeStyles.None,out parsed)&&parsed.Date==new DateTime(2026,11,13);}
 private string KhbsJson(){
  string q=((char)34).ToString();StringBuilder json=new StringBuilder();
  string[] names=new string[]{"khbsDateTyped","khbsPeriodMatched","khbsImportInvoked","khbsImportSucceeded","khbsImportPathMatched","khbsSummaryInvoked","khbsSummaryAcknowledged","khbsExportInvoked","khbsExportSchemaPinnedVerified","khbsExportSucceeded","khbsIdentityMatched","khbsCreationDateValid","khbsTreeMatched","khbsOriginalMoneyMatched","khbsSavedMoneyMatched","khbsDirtyAfterSave","khbsDiscardPromptAnswered","khbsPriorImportSucceeded","khbsPriorSummaryAcknowledged","khbsPriorSaveAcknowledged","khbsPriorFileSaved","khbsRound2Opened"};
  bool[] values=new bool[]{khbsDateTyped,khbsPeriodMatched,khbsImportInvoked,khbsImportSucceeded,khbsImportPathMatched,khbsSummaryInvoked,khbsSummaryAcknowledged,khbsExportInvoked,khbsExportSchemaPinnedVerified,khbsExportSucceeded,khbsIdentityMatched,khbsCreationDateValid,khbsTreeMatched,khbsOriginalMoneyMatched,khbsSavedMoneyMatched,khbsDirtyAfterSave,khbsDiscardPromptAnswered,khbsPriorImportSucceeded,khbsPriorSummaryAcknowledged,khbsPriorSaveAcknowledged,khbsPriorFileSaved,khbsRound2Opened};
  for(int index=0;index<names.Length;index++)json.Append(","+q+names[index]+q+":"+Bool(values[index]));
  names=new string[]{"khbsImportMessageId","khbsSummaryMessageId","khbsExportMessageId","khbsLeafCount","khbsMismatchMask","khbsFirstDifferenceOrdinal","khbsExportBytes","khbsOpenMainState","khbsPostSaveWaitMask","khbsRound","khbsPriorSaveMessageId"};int[] counts=new int[]{khbsImportMessageId,khbsSummaryMessageId,khbsExportMessageId,khbsLeafCount,khbsMismatchMask,khbsFirstDifferenceOrdinal,khbsExportBytes,khbsOpenMainState,khbsPostSaveWaitMask,khbsRound,khbsPriorSaveMessageId};
  for(int index=0;index<names.Length;index++)json.Append(","+q+names[index]+q+":"+counts[index].ToString(CultureInfo.InvariantCulture));
  return json.ToString()+","+q+"khbsExportSha256"+q+":"+q+khbsExportSha256+q;
 }
 // KHBS case only, after the B1 defaults (Lần 1, today) were proven: the original ngày lập control gets the fixed date.
 private void TypeOriginalKhbsDate(Control period){
  if(!KhbsMode()||!amendmentOpenDefaultsMatched||khbsDateTyped)throw new InvalidOperationException();
  SetStage(HtkkAutomationStage.GtgtAmendmentKhbsDateTyping);Record();SetText(period,"mskNgayLapKHBS",KhbsFixedDate);
  khbsDateTyped=KhbsDate(ReadableNamed(period,"mskNgayLapKHBS").Text);if(!khbsDateTyped)throw new InvalidOperationException();
 }
 // Called once the B1 sheet, its two KHBS tabs, the unchanged C0 file and the fixed ngày lập are proven.
 private void StartOriginalKhbsImport(Form owner){
  if(!KhbsMode()||khbsPhase!="not-started"||!webInputVerified||!KhbsCaseId(webCaseId)||!khbsPeriodMatched||owner==null||owner.GetType().FullName!="HTKK.frmWinToKhai")throw new InvalidOperationException();
  if(Hash(KhbsImportPath())!=KhbsImportHash())throw new InvalidOperationException();
  khbsOwner=owner;roundtripOwner=owner;khbsPhase="import-ready";SetStage(HtkkAutomationStage.GtgtAmendmentKhbsImportInvoking);Record();
  exportWatcher=new System.Windows.Forms.Timer();exportWatcher.Interval=100;exportWatcher.Tick+=delegate(object sender,EventArgs args){try{ContinueOriginalKhbs();}catch(Exception error){exportWatcher.Stop();Failure(error);}};exportWatcher.Start();
 }
 private Form KhbsMessage(out string text){
  text=null;Form found=null;
  foreach(Form form in Application.OpenForms){if(!form.Visible||form.GetType().FullName!="TAX.HTKK.Utilities.Control.frmMessage")continue;if(found!=null)throw new InvalidOperationException();found=form;}
  if(found==null)return null;Control[] labels=found.Controls.Find("lblThongBao",true);if(labels.Length!=1)throw new InvalidOperationException();text=labels[0].Text;return found;
 }
 private void CloseKhbsMessage(Form message){
  Control[] controls=message.Controls.Find("btn_2",true);if(controls.Length!=1||CountVisibleButtons(message)!=1)throw new InvalidOperationException();Button close=controls[0] as Button;
  if(close==null||!close.Visible||!close.Enabled||close.Text.Replace("&",String.Empty).Trim()!="Đóng")throw new InvalidOperationException();close.PerformClick();
 }
 private bool KhbsOwnerReady(){if(khbsOwner==null||khbsOwner.IsDisposed||khbsOwner.GetType().FullName!="HTKK.frmWinToKhai")throw new InvalidOperationException();return khbsOwner.Visible&&khbsOwner.Enabled&&!OriginalMessageVisible();}
 private void KhbsStop(HtkkAutomationStage stage){finished=true;SetStage(stage);Record();exportWatcher.Stop();}
 private void ContinueOriginalKhbs(){
  if(finished){exportWatcher.Stop();return;}if(khbsBusy||exportFilenameEditing)return;khbsBusy=true;
  try{
   string text;Form message;
   if(khbsPhase=="import-ready"){
    if(!KhbsOwnerReady())return;
    Button import=Named(khbsOwner,"cmdImportXML") as Button;if(import==null||import.FindForm()!=khbsOwner||import.Text.Replace("&",String.Empty).Trim()!="Nhập từ XML")throw new InvalidOperationException();
    khbsImportInvoked=true;roundtripImportCommandInvoked=true;khbsPhase="import-result";SetStage(HtkkAutomationStage.GtgtAmendmentKhbsImportWaiting);Record();
    khbsOwner.BeginInvoke(new MethodInvoker(delegate{try{import.PerformClick();}catch(Exception error){Failure(error);}}));return;
   }
   if(khbsPhase=="import-result"){
    message=KhbsMessage(out text);
    if(message==null){if(!roundtripImportDialogSubmitted)TrySubmitOriginalFileDialog("Chọn tờ khai để tải vào chương trình",KhbsImportPath(),true);return;}
    if(text!="Nhập dữ liệu từ XML thành công."){khbsImportMessageId=OriginalMessageCatalogueId(text);KhbsStop(HtkkAutomationStage.GtgtAmendmentKhbsImportRejected);return;}
    FieldInfo loading=OriginalAssembly().GetType("HTKK.frmWinToKhai",true).GetField("FileNameLoading",BindingFlags.Static|BindingFlags.Public|BindingFlags.NonPublic);
    if(loading==null||loading.FieldType!=typeof(string))throw new InvalidOperationException();string actual=(string)loading.GetValue(null);
    khbsImportPathMatched=!String.IsNullOrEmpty(actual)&&String.Equals(Path.GetFullPath(actual),Path.GetFullPath(KhbsImportPath()),StringComparison.OrdinalIgnoreCase);roundtripImportPathMatched=khbsImportPathMatched;
    if(!roundtripImportDialogMatched||!roundtripImportKeyboardCommitted||!roundtripImportDialogSubmitted||!khbsImportPathMatched){Record();throw new InvalidOperationException();}
    object period=Global("TTPeriodInfo");if(Convert.ToString(Get(period,"LoaiToKhai"),CultureInfo.InvariantCulture)!="B"||Convert.ToString(Get(period,"SoLan"),CultureInfo.InvariantCulture)!=khbsRound.ToString(CultureInfo.InvariantCulture)||!KhbsDate(Convert.ToString(Get(period,"NgayLapKHBS"),CultureInfo.InvariantCulture)))throw new InvalidOperationException();
    if(KhbsImportingPrior())khbsPriorImportSucceeded=true;else khbsImportSucceeded=true;roundtripImportSucceeded=true;khbsPhase=KhbsAnnexCase()?"annex-restore":"summary-ready";SetStage(HtkkAutomationStage.GtgtAmendmentKhbsSummaryWaiting);Record();CloseKhbsMessage(message);return;
   }
   // Capture case only: the imported 01-2 annex is checked read-only, then its head CQT displays are restored (bounded).
   if(khbsPhase=="annex-restore"){
    if(!KhbsOwnerReady())return;
    List<Control> grids=new List<Control>();int visited=0;GatherSpreads(khbsOwner,grids,ref visited);if(grids.Count!=1)throw new InvalidOperationException();
    if(!InspectOriginalImportedAnnex12(grids[0])){if(khbsPriorCloseClock==null)khbsPriorCloseClock=Stopwatch.StartNew();if(khbsPriorCloseClock.Elapsed.TotalSeconds>=10)throw new InvalidOperationException();return;}
    khbsPhase="annex-restoring";RestoreImportedAnnex12HeadAuthorities();
    if(!annex12WebHeadAuthorityRestored)throw new InvalidOperationException();
    khbsPriorCloseClock=null;khbsPhase="summary-ready";SetStage(HtkkAutomationStage.GtgtAmendmentKhbsSummaryWaiting);Record();return;
   }
   if(khbsPhase=="summary-ready"){
    if(!KhbsOwnerReady())return;
    Button summary=Named(khbsOwner,"btnTongHopKHBS") as Button;if(summary==null||summary.FindForm()!=khbsOwner||!summary.Visible||!summary.CanSelect)throw new InvalidOperationException();
    khbsSummaryInvoked=true;khbsPhase="summary-result";SetStage(HtkkAutomationStage.GtgtAmendmentKhbsSummaryInvoking);Record();
    khbsOwner.BeginInvoke(new MethodInvoker(delegate{try{summary.PerformClick();}catch(Exception error){Failure(error);}}));return;
   }
   if(khbsPhase=="summary-result"){
    message=KhbsMessage(out text);if(message==null){SetStage(HtkkAutomationStage.GtgtAmendmentKhbsSummaryResultWaiting);Record();return;}
    if(text!="Tổng hợp dữ liệu lên KHBS thành công"){khbsSummaryMessageId=OriginalMessageCatalogueId(text);KhbsStop(HtkkAutomationStage.GtgtAmendmentKhbsSummaryRejected);return;}
    if(KhbsImportingPrior()){khbsPriorSummaryAcknowledged=true;khbsPhase="prior-save-ready";SetStage(HtkkAutomationStage.GtgtAmendmentKhbsPriorSaving);Record();CloseKhbsMessage(message);return;}
    khbsSummaryAcknowledged=true;khbsPhase="export-ready";SetStage(HtkkAutomationStage.GtgtAmendmentKhbsExportWaiting);Record();CloseKhbsMessage(message);return;
   }
   // Lần 2, round 1 only: save the summarised B1 with the original Ghi, verify the bs1_ file, close it with the original Đóng.
   if(khbsPhase=="prior-save-ready"){
    if(!KhbsOwnerReady())return;
    if(File.Exists(Path.Combine(Path.Combine(Path.Combine(Path.GetDirectoryName(project),"DataFiles"),Mst),KhbsPriorB1FileName)))throw new InvalidOperationException();
    Button save=Named(khbsOwner,"cmdSave") as Button;if(save==null||save.FindForm()!=khbsOwner||save.Text.Replace("&",String.Empty).Trim()!="Ghi")throw new InvalidOperationException();
    khbsPhase="prior-save-result";SetStage(HtkkAutomationStage.GtgtAmendmentKhbsPriorSaving);Record();
    khbsOwner.BeginInvoke(new MethodInvoker(delegate{try{save.PerformClick();}catch(Exception error){Failure(error);}}));return;
   }
   if(khbsPhase=="prior-save-result"){
    message=KhbsMessage(out text);if(message==null){if(khbsPriorCloseClock==null)khbsPriorCloseClock=Stopwatch.StartNew();if(khbsPriorCloseClock.Elapsed.TotalSeconds>=60){khbsPostSaveWaitMask|=64;KhbsStop(HtkkAutomationStage.GtgtAmendmentKhbsPostSaveTimeout);}return;}
    if(text!="Đã ghi dữ liệu thành công!"){khbsPriorSaveMessageId=OriginalMessageCatalogueId(text);KhbsStop(HtkkAutomationStage.GtgtAmendmentKhbsPriorSaveRejected);return;}
    InspectKhbsPriorSavedFile();khbsPriorSaveAcknowledged=true;khbsPriorCloseClock=Stopwatch.StartNew();khbsPhase="prior-close-ready";SetStage(HtkkAutomationStage.GtgtAmendmentKhbsPriorClosing);Record();CloseKhbsMessage(message);return;
   }
   if(khbsPhase=="prior-close-ready"){
    FieldInfo dirtyField=khbsOwner.GetType().GetField("isDataChanged",BindingFlags.Instance|BindingFlags.Public|BindingFlags.NonPublic);if(dirtyField==null||dirtyField.FieldType!=typeof(bool))throw new InvalidOperationException();
    bool ready=KhbsOwnerReady(),dirty=(bool)dirtyField.GetValue(khbsOwner);int mask=(ready?0:2)|(dirty?32:0);
    if(mask!=khbsPostSaveWaitMask){khbsPostSaveWaitMask=mask;Record();}
    if(!ready||dirty&&khbsPriorCloseClock.Elapsed.TotalSeconds<2){if(khbsPriorCloseClock.Elapsed.TotalSeconds>=30)KhbsStop(HtkkAutomationStage.GtgtAmendmentKhbsPostSaveTimeout);return;}
    if(dirty)khbsDirtyAfterSave=true;
    Button close=Named(khbsOwner,"cmdExit") as Button;if(close==null||close.FindForm()!=khbsOwner||!close.Visible||!close.Enabled||close.Text.Replace("&",String.Empty).Trim()!="Đóng")throw new InvalidOperationException();
    khbsPhase="prior-closing";SetStage(HtkkAutomationStage.GtgtAmendmentKhbsPriorClosing);Record();
    khbsOwner.BeginInvoke(new MethodInvoker(delegate{try{close.PerformClick();}catch(Exception error){Failure(error);}}));return;
   }
   if(khbsPhase=="prior-closing"){
    message=KhbsMessage(out text);
    if(message!=null){if(!khbsDirtyAfterSave||khbsDiscardPromptAnswered)throw new InvalidOperationException();AnswerKhbsDiscardPrompt();return;}
    if(khbsOwner.IsDisposed||!khbsOwner.Visible){BeginKhbsRound2();return;}
    if(khbsPriorCloseClock.Elapsed.TotalSeconds>=60)KhbsStop(HtkkAutomationStage.GtgtAmendmentKhbsPostSaveTimeout);return;
   }
   if(khbsPhase=="export-ready"){
    if(!KhbsOwnerReady())return;
    // LoaiToKhai B validates against the KHBS schema of the same declaration version (Menu.xml XsdSchema 01_GTGT_TT80).
    string schema=Path.Combine(Path.GetDirectoryName(project),"InterfaceTemplates/Validate/KHBS_01_GTGT_TT80_283.xsd");string actualSchema=Convert.ToString(Get(Global("ToKhaiInfo"),"XsdFileName"),CultureInfo.InvariantCulture);
    khbsExportSchemaPinnedVerified=!String.IsNullOrEmpty(actualSchema)&&String.Equals(Path.GetFullPath(actualSchema),Path.GetFullPath(schema),StringComparison.OrdinalIgnoreCase)&&Hash(schema)=="b0fcb96663749e897839db2c9c224c45b4f2ed779be508e1bf9f9a2f82daf76f";exportSchemaPinnedVerified=khbsExportSchemaPinnedVerified;
    if(!khbsExportSchemaPinnedVerified){Record();throw new InvalidOperationException();}
    string directory=Path.Combine(Path.Combine(Path.Combine(Path.GetDirectoryName(project),"DataFiles"),Mst),"reference-khbs-output");if(Directory.Exists(directory)||File.Exists(directory))throw new InvalidOperationException();Directory.CreateDirectory(directory);exportPath=Path.Combine(directory,"01GTGT-khbs.xml");exportDestinationFresh=true;
    Assembly utilities=null;foreach(Assembly loaded in AppDomain.CurrentDomain.GetAssemblies())if(loaded.GetName().Name=="TAX.HTKK.Utilities")utilities=loaded;if(utilities==null)throw new InvalidOperationException();
    Type configuration=utilities.GetType("TAX.HTKK.Utilities.Core.HTKKConfig",true);PropertyInfo temporary=configuration.GetProperty("PATH_TEMP",BindingFlags.Public|BindingFlags.Static);if(temporary==null)throw new InvalidOperationException();expectedSaveTitle="Tệp XML kết xuất tới thư mục "+Convert.ToString(temporary.GetValue(null,null),CultureInfo.InvariantCulture);
    Button command=Named(khbsOwner,"cmdExport") as Button;if(command==null||command.FindForm()!=khbsOwner||command.Text.Replace("&",String.Empty).Trim()!="Kết xuất")throw new InvalidOperationException();
    khbsExportInvoked=true;exportCommandInvoked=true;khbsPhase="exporting";SetStage(HtkkAutomationStage.GtgtAmendmentKhbsExportInvoking);Record();
    khbsOwner.BeginInvoke(new MethodInvoker(delegate{try{command.PerformClick();}catch(Exception error){Failure(error);}}));return;
   }
   if(khbsPhase=="exporting"){
    message=KhbsMessage(out text);
    if(message!=null){
     if(text!="Kết xuất tờ khai xml thành công."){khbsExportMessageId=OriginalMessageCatalogueId(text);exportRejectedMessageId=khbsExportMessageId;KhbsStop(HtkkAutomationStage.GtgtAmendmentKhbsExportRejected);return;}
     InspectOriginalExportDestination();ReadOriginalExport();if(!exportOriginalPathMatched||!exportDialogSubmitted||!exportXmlRootMatched||!exportSyntheticIdentityMatched)throw new InvalidOperationException();
     exportSuccessAcknowledged=true;khbsExportSucceeded=true;khbsExportBytes=exportBytes;khbsExportSha256=exportSha256;
     SetStage(HtkkAutomationStage.GtgtAmendmentKhbsComparing);Record();
     if(Hash(webInputPath)!=webImportInputSha256)throw new InvalidOperationException();
     XmlDocument input=ReadBoundedOriginalXml(webInputPath),output=ReadBoundedOriginalXml(exportPath);
     khbsTreeMatched=HtkkWebTaxComparison.CompareKhbs(input,output,webCaseId==KhbsSale5WebCaseId?KhbsSale5LeafTarget:webCaseId==KhbsAnnex12CaptureCaseId?KhbsAnnex12CaptureLeafTarget:webCaseId==KhbsAnnex12Lan2CaseId?KhbsAnnex12Lan2LeafTarget:KhbsAnnexWideCaseId(webCaseId)?KhbsAnnexWideLeafTarget(webCaseId):KhbsLeafTarget,out khbsLeafCount,out khbsMismatchMask,out khbsFirstDifferenceOrdinal,out khbsIdentityMatched,out khbsCreationDateValid);
     if(Hash(exportPath)!=khbsExportSha256)throw new InvalidOperationException();
     finished=true;SetStage(khbsTreeMatched?HtkkAutomationStage.GtgtAmendmentKhbsInspected:HtkkAutomationStage.GtgtAmendmentKhbsNotMatched);Record();exportWatcher.Stop();CloseKhbsMessage(message);return;
    }
    if(!exportButtonInvoked){
     List<Form> selectors=VisibleExportSelectors();if(selectors.Count==0)return;if(selectors.Count!=1)throw new InvalidOperationException();Form selector=selectors[0];
     RadioButton xml=Named(selector,"radKetXuatXML") as RadioButton,excel=Named(selector,"radKetXuatExcel") as RadioButton;Button button=Named(selector,"btnExport") as Button;
     if(xml==null||excel==null||!xml.Checked||excel.Checked||xml.Text!="Kết xuất XML"||button==null||button.FindForm()!=selector||button.Text.Replace("&",String.Empty).Trim()!="Kết xuất")throw new InvalidOperationException();
     exportSelectorMatched=true;exportButtonInvoked=true;SetStage(HtkkAutomationStage.GtgtExportFileDialogWaiting);Record();selector.BeginInvoke(new MethodInvoker(delegate{try{button.PerformClick();}catch(Exception error){Failure(error);}}));return;
    }
    if(!exportDialogSubmitted)TrySubmitOriginalFileDialog(expectedSaveTitle,exportPath,false);
    return;
   }
   throw new InvalidOperationException();
  }finally{khbsBusy=false;}
 }
}
