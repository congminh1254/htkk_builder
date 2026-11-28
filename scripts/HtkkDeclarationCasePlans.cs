// Reviewed, compiled-in plans for the declaration-family native cases (C# 2.0 / CLR2).
// A private input can only SELECT one of these fixed case IDs; it can never supply a
// menu chain, period, annex, cell, path or value. Sources: Menu.xml / InterfaceTemplates of
// HTKK 5.8.1 (hashes pinned below) and the builder's independent case oracles.
using System;

internal sealed class HtkkDeclarationCasePlan {
 internal readonly string CaseId,MenuId,VersionXml,MaTKhai,BusinessClass,PeriodKind,KieuKy,Year,PeriodNumber,FromDate,ToDate,WebServiceName;
 internal readonly string WorkbookFile,WorkbookSha256,LayoutFile,LayoutSha256,SchemaFile,SchemaSha256,BaseSchemaFile,BaseSchemaSha256;
 internal readonly string[] MenuChain,Annexes,SheetNames,CellChecks,XmlChecks;
 internal readonly bool ContinuousOperation;
 internal readonly int LeafCount;
 internal HtkkDeclarationCasePlan(string caseId,string menuId,string versionXml,string maTKhai,string businessClass,string[] menuChain,string periodKind,string kieuKy,string year,string periodNumber,string fromDate,string toDate,bool continuousOperation,string[] annexes,string[] sheetNames,string workbookFile,string workbookSha256,string layoutFile,string layoutSha256,string schemaFile,string schemaSha256,string baseSchemaFile,string baseSchemaSha256,string webServiceName,int leafCount,string[] cellChecks,string[] xmlChecks){
  CaseId=caseId;MenuId=menuId;VersionXml=versionXml;MaTKhai=maTKhai;BusinessClass=businessClass;MenuChain=menuChain;PeriodKind=periodKind;KieuKy=kieuKy;Year=year;PeriodNumber=periodNumber;FromDate=fromDate;ToDate=toDate;ContinuousOperation=continuousOperation;
  Annexes=annexes;SheetNames=sheetNames;WorkbookFile=workbookFile;WorkbookSha256=workbookSha256;LayoutFile=layoutFile;LayoutSha256=layoutSha256;SchemaFile=schemaFile;SchemaSha256=schemaSha256;BaseSchemaFile=baseSchemaFile;BaseSchemaSha256=baseSchemaSha256;
  WebServiceName=webServiceName;LeafCount=leafCount;CellChecks=cellChecks;XmlChecks=xmlChecks;
  if(menuChain.Length<2||menuChain.Length>3||menuChain[menuChain.Length-1]!=menuId||cellChecks.Length>24||xmlChecks.Length>24||annexes.Length>8||leafCount<1||leafCount>4096)throw new InvalidOperationException();
  if(periodKind!="month"&&periodKind!="quarter"&&periodKind!="year"&&periodKind!="range"&&periodKind!="day")throw new InvalidOperationException();
  // KieuKy 22 (frmHTKKPeriod.SetLayoutToKhaiTuNgayDenNgay 0x60004ae): only the from/to date boxes, no year box.
  if((periodKind=="range")!=(kieuKy=="22")||(periodKind=="range"&&(fromDate.Length!=10||toDate.Length!=10||toDate.Substring(6)!=year||periodNumber!="")))throw new InvalidOperationException();
  // KieuKy 18 "Lần phát sinh" (chkTKLanPS): one day typed into the ngày/tháng/năm boxes; GetPeriodInfo (0x60004e2,
  // KieuKy table index 16) gives KieuKy D, TuNgay = DenNgay = kyKKhai = dd/MM/yyyy, so FromDate = ToDate = that day.
  // KieuKy 21 (index 17, SetLayoutToKhaiThangQuyLanPhatSinh; 01/TCKT Y7) builds the same D period from the same boxes.
  if(periodKind=="day"&&((kieuKy!="18"&&kieuKy!="21")||fromDate.Length!=10||fromDate!=toDate||fromDate[2]!='/'||fromDate[5]!='/'||fromDate.Substring(6)!=year||periodNumber!=""))throw new InvalidOperationException();
 }
}

internal sealed class HtkkDeclarationEntryPlan {
 internal readonly string ChoiceCell,ExclusiveCell,SignerCell,CatalogueFile,CatalogueSha256;
 internal readonly string[] Tables,LockColumns,Entries,MethodPins;
 internal HtkkDeclarationEntryPlan(string choiceCell,string exclusiveCell,string signerCell,string catalogueFile,string catalogueSha256,string[] tables,string[] lockColumns,string[] entries,string[] methodPins){
  ChoiceCell=choiceCell;ExclusiveCell=exclusiveCell;SignerCell=signerCell;CatalogueFile=catalogueFile;CatalogueSha256=catalogueSha256;Tables=tables;LockColumns=lockColumns;Entries=entries;MethodPins=methodPins;
  if(tables.Length<1||tables.Length>4||lockColumns.Length<1||lockColumns.Length>16||entries.Length<1||entries.Length>30||methodPins.Length<1||methodPins.Length>30)throw new InvalidOperationException();
  foreach(string table in tables)if(table.Split('|').Length!=4)throw new InvalidOperationException();
  foreach(string entry in entries){string[] parts=entry.Split('|');if(!((parts.Length==3&&(parts[0]=="text"||parts[0]=="date"||parts[0]=="number"||parts[0]=="date-optional"))||(parts.Length==7&&parts[0]=="combo")))throw new InvalidOperationException();}
  foreach(string pin in methodPins){string[] parts=pin.Split('|');if(parts.Length!=6||(parts[0]!="B"&&parts[0]!="H")||parts[5].Length!=64)throw new InvalidOperationException();}
 }
}

// Native-case mode web-xml-import-tick-reexport: after the original "Nhập từ XML", fixed original keyboard actions on
// sheet 01 for inputs the XML cannot carry (grid-only cells). Edits: kind|cell|value through the original editor,
// one per UI turn. Ticks: checkbox cells ticked with SPACE (ButtonClicked), in order. Unticked: checkboxes that must
// stay clear. Readbacks: cell|text of HTKK-written cells, a value-free diagnostic mask only (the sheet checks and the
// whole-tree comparison decide). Method pins: HtkkOracleBaseline.TickMethodPins() of the selected oracle.
internal sealed class HtkkDeclarationTickPlan {
 internal readonly string[] Edits,Ticks,Unticked,Readbacks,MethodPins;
 internal HtkkDeclarationTickPlan(string[] edits,string[] ticks,string[] unticked,string[] readbacks,string[] methodPins){
  Edits=edits;Ticks=ticks;Unticked=unticked;Readbacks=readbacks;MethodPins=methodPins;
  // A plan may have no tick (PL 03: the edit alone runs capNhatToKhai); it always has an edit.
  if(edits.Length<1||edits.Length>5||ticks.Length>4||edits.Length+ticks.Length>8||unticked.Length>4||readbacks.Length>8||methodPins.Length<1||methodPins.Length>30)throw new InvalidOperationException();
  // number|cell|value on sheet 01; combo|sheet|cell|item name|code cell|item code: an original combobox of another
  // sheet (05-1/PBT Thuế tỉnh/CCT and CQT quản lý), the item chosen from the original list by keys, the code written by
  // frmWinToKhai.winFpSpread_CellChange (GetDMFromCombobox) read back.
  foreach(string edit in edits){string[] parts=edit.Split('|');if(!((parts.Length==3&&parts[0]=="number")||(parts.Length==6&&parts[0]=="combo"&&parts[1].Length>0&&parts[3].Length>0&&parts[5].Length>0)))throw new InvalidOperationException();}
  foreach(string readback in readbacks)if(readback.Split('|').Length!=2)throw new InvalidOperationException();
  foreach(string pin in methodPins){string[] parts=pin.Split('|');if(parts.Length!=6||(parts[0]!="B"&&parts[0]!="H")||parts[5].Length!=64)throw new InvalidOperationException();}
 }
}

// Taxpayer profile CQT and period-dialog place of a declaration case (registry fields taxpayerProfile / periodLocation,
// htkk_case_geography.py; test_case_geography.py keeps this table equal to it). Profile: Thuế tỉnh/CCT and CQT quản lý (code and
// the name its combo shows); the profile's tỉnh and xã stay 101 / 10129087. Period: tỉnh, xã, Thuế tỉnh/CCT, CQT quản lý.
internal sealed class HtkkCaseGeography {
 internal readonly string ProfileHeadCode,ProfileHeadName,ProfileOfficeCode,ProfileOfficeName,ProvinceCode,ProvinceName,WardCode,WardName,HeadCode,HeadName,OfficeCode,OfficeName;
 internal HtkkCaseGeography(string[] v){
  if(v==null||v.Length!=12)throw new InvalidOperationException();foreach(string item in v)if(String.IsNullOrEmpty(item))throw new InvalidOperationException();
  ProfileHeadCode=v[0];ProfileHeadName=v[1];ProfileOfficeCode=v[2];ProfileOfficeName=v[3];ProvinceCode=v[4];ProvinceName=v[5];WardCode=v[6];WardName=v[7];HeadCode=v[8];HeadName=v[9];OfficeCode=v[10];OfficeName=v[11];
  // 0611: the period's CQT quản lý is the profile's.
  if(OfficeCode!=ProfileOfficeCode||OfficeName!=ProfileOfficeName)throw new InvalidOperationException();
 }
}

internal static class HtkkDeclarationCasePlans {
 internal const string XmldsigSha256="c3b5160be1852606d10f6928e0b214d418f8dd418667cb2fb88fec31e4e6f56d";
 private const string TKhaiThue="TKhaiThue.xsd",TKhaiThueSha256="8f451719355b5a6247f65a34a37584b4a0c7f7cc81a568e1033d08b8fe9b8c1d";
 private const string TKhaiThueDbhc="TKhaiThue_DBHC.xsd",TKhaiThueDbhcSha256="aba7f2acbc9332caaf3eb2da9a081a3d876ddc7813d6230921da48c775460011";
 private const string WorkbookService="Công cụ Kê khai",CnkdService="Công cụ Kê khai";
 private const string Main="HSoThueDTu/HSoKhaiThue/CTieuTKhaiChinh/";
 // Fixed case IDs, in registry order. Kept identical to htkk-native-cases.json (tested offline).
 internal static readonly string[] CaseIds=new string[]{"03TNDN-profit20-Y2025","BCTC133-B01a-basic-Y2025","BCTC200-LT-basic-Y2025","05KK-withheld-Q3-2026","05KK-TT89-withheld-Q4-2026","05QTT-two-employees-Y2025","01CNKD-TT50-revenue-two-groups-Q3-2026","02QTT-dependants-Y2025","01NTNN-two-contractors-M09-2026","03NTNN-no-rate-M10-2026","01NTNN-NCCNN-entry-M10-2026","04NTNN-TT80-one-subcontractor-2026","04NTNN-TT89-one-subcontractor-2026","02NTNN-TT89-two-annexes-2026","02NTNN-TT80-two-annexes-2026","01NTNN-occurrence-D20-09-2026","01NTNN-NCCNN-occurrence-D20-10-2026","03NTNN-occurrence-D20-10-2026","01CNKD-TT50-310-pl01-three-groups-Q3-2026","01CNKD-TT50-310-pl03-two-groups-Q3-2026","03TNDN-rate15-Y2025","03TNDN-rate17-Y2025","05KK-PBT-two-provinces-Q3-2026","05KK-TT89-PBT-two-provinces-Q4-2026","02QTT-refund-transfer-Y2025","02QTT-dependants-Y2026","02QTT-refund-transfer-Y2026","01TTS-individual-one-contract-Y2025","01TTS-individual-two-contracts-Y2025","01TTS-organization-two-individuals-Q3-2026","01TTS-organization-monthly-M10-2026","01TCKT-hop-tac-kd-two-individuals-Q4-2026","01TCKT-bds-three-lessors-M10-2026","01TCKT-bds-occurrence-D15-10-2026","01TCKT-310-hop-tac-kd-two-individuals-Q4-2026","01TCKT-310-bds-three-lessors-M10-2026","01TCKT-310-bds-occurrence-D15-10-2026","01TCKT-310-pl-nq43-hop-tac-kd-Q4-2026","04GTGT-TT80-one-group-M09-2026","04GTGT-TT80-quarter-Q3-2026","04GTGT-TT80-four-groups-rounding-M08-2026","04GTGT-TT80-reduction-annex-Q2-2026","04GTGT-TT89-one-group-M10-2026","04GTGT-TT89-quarter-Q4-2026","04GTGT-TT89-four-groups-rounding-M10-2026","04GTGT-TT89-reduction-annex-M10-2026","01GTGT-TT89-zero-M10-2026","01GTGT-TT89-sale10-M10-2026","01GTGT-TT89-quarter-Q4-2026","01GTGT-TT89-no-activity-M11-2026","01GTGT-TT89-full-M12-2026","01GTGT-TT89-full-M10-2026","01GTGT-TT89-nq204-M12-2026","01GTGT-TT89-nq204-M10-2026","02NTNN-TT89-two-annexes-to-07-10-2026","04NTNN-TT89-one-subcontractor-to-07-10-2026","01NTNN-NCCNN-entry-part-II1-M10-2026","01NTNN-NCCNN-entry-part-II2-M10-2026","02NTNN-TT80-two-annexes-to-06-10-2026","04NTNN-TT80-one-subcontractor-to-06-10-2026","02NTNN-TT89-two-annexes-from-01-06-2026","04NTNN-TT89-one-subcontractor-from-01-06-2026","01NTNN-NCCNN-entry-future-contract-M10-2026","01GTGT-TT89-pl016-cssx-M10-2026","01GTGT-TT89-pl016-cssx-ratio-M10-2026","01GTGT-TT89-pl016-dtvt-M10-2026","01GTGT-TT89-other-province-M10-2026","01GTGT-TT89-pl018-5pct-M10-2026","01GTGT-TT89-pl018-xk-M10-2026","01GTGT-TT89-pl018-gt-M10-2026","01GTGT-TT89-pl012-M10-2026"};
 // Original frmHTKKPeriod.SetLayoutToKhaiNamTuThangDenThang (KieuKy 12) calls
 // ShowDetailpnVT2_PhuLucKeKhai(false) for every menu except 97/H4/C8: the annex list is
 // bound (LoadPhuLucSpread) but hidden, so a user cannot tick it. The driver only observes
 // that hidden list's original defaults (run 42218301225: axfpsPhuLuc not visible for B9).
 // frmHTKKPeriod.btnDongY_Click (HTKK 5.8.1 0x60004dc, 5.8.2 0x60004de, 5.8.3 0x60004e0): for menu Y7 only, once every period
 // check passed, new frmMessage("0699","3","","Thông báo").ShowDialog() — style 3 = one "Đóng" button (cmd_OK), icon "" =
 // information.ico — then the result is discarded and OpenToKhai opens the tờ khai. Message.xml 0699 "Tờ khai này được tổng hợp từ
 // phụ lục. Đề nghị NNT kê khai phụ lục trước" is a notice, not a refusal (runs 44023258598, 44023261804 stopped at it). Every other
 // message after the dialog's OK stays a rejection.
 internal static bool PeriodInfoMessageAccepted(HtkkDeclarationCasePlan plan,int messageId){return plan!=null&&plan.MenuId=="Y7"&&messageId==699;}
 internal static bool AnnexPanelHidden(HtkkDeclarationCasePlan plan){return plan!=null&&plan.KieuKy=="12"&&plan.MenuId!="97"&&plan.MenuId!="H4"&&plan.MenuId!="C8";}
 // B8 (02/QTT, KieuKy 12) only: the list a typed year leaves visible (static reading of HTKK 5.8.2 HTKK.exe 331ed84a, run
 // 43551336755). frmHTKKPeriod.LoadDefaultInfor opens on Now.Year - 1; typing another year runs mskYear_Leave ->
 // UpdatePeriodByVerSion, whose KieuKHBS "3" branch (B8 has four Menu.xml sheets) sets pnVT2_PhuLucKeKhai visible, calls
 // LoadPhuLucSpread and only then hides the panel again for B9/B8/W1. WinSpreadProcess.BindDataToPhuLucSpread gives no row
 // to a sheet whose SheetName contains "KHBS" (01-KHBS, 01-1/KHBS), sets Rows.Count to the other annexes (B8: one row,
 // 02-1/BK-QTT-TNCN) and, for B8, ticks AND locks rows 0 and 1; once an earlier bind has cut the list to one row, Cells[1,0]
 // throws (FarPoint Cells.get_Item: row >= RowCount), UpdatePeriodByVerSion's catch only logs, and the panel stays visible
 // with row 0 ticked and locked (the run saw axfpsPhuLuc and chkChonPhuLucKeKhaiAll visible). On "Đồng ý" OpenToKhai adds
 // the ticked rows (GetPhuLucThemMoi); KHBS sheets are opened only for a bổ sung (LoaiToKhai B). The driver handles this
 // list by observation: SelectReviewedVisibleAnnexList ticks exactly the case annexes, never a KHBS row, never forces a
 // locked row, and verifies (terminal declaration-period-annex-list-not-matched otherwise).
 internal static bool VisibleAnnexListReviewed(HtkkDeclarationCasePlan plan){return plan!=null&&plan.MenuId=="B8"&&plan.KieuKy=="12";}
 internal static bool KhbsAnnexLabel(string label){return label!=null&&label.IndexOf("KHBS",StringComparison.Ordinal)>=0;}
 // The case annex a row label (CheckBoxCellType.TextTrue) names, -1 for none.
 internal static int ReviewedAnnexIndex(HtkkDeclarationCasePlan plan,string label){
  if(label==null)return -1;
  for(int index=0;index<plan.Annexes.Length;index++)foreach(string option in plan.Annexes[index].Split('|'))if(option==label)return index;
  return -1;
 }
 // Classifies the observed rows of a visible list (labels[r] null = not a checkbox row). owner[r]: case annex index, -1 a
 // KHBS row, -2 any other row. Returns declarationAnnexListMask bits: 4 a non-checkbox row or a label that is neither a case
 // annex nor KHBS; 8 a KHBS row ticked; 16 a KHBS row listed; 32 a case annex missing or listed twice; 64 a case annex
 // unticked and locked. Bits 4/8/32/64 stop the case before any action; a KHBS row is never ticked.
 internal static int ClassifyVisibleAnnexList(HtkkDeclarationCasePlan plan,string[] labels,bool[] ticked,bool[] locked,int[] owner){
  if(labels.Length!=ticked.Length||labels.Length!=locked.Length||labels.Length!=owner.Length||labels.Length>16)throw new InvalidOperationException();
  int mask=0;int[] seen=new int[plan.Annexes.Length];
  for(int row=0;row<labels.Length;row++){
   owner[row]=-2;
   if(labels[row]==null){mask|=4;continue;}
   if(KhbsAnnexLabel(labels[row])){owner[row]=-1;mask|=16;if(ticked[row])mask|=8;continue;}
   int wanted=ReviewedAnnexIndex(plan,labels[row]);if(wanted<0){mask|=4;continue;}
   owner[row]=wanted;seen[wanted]++;if(!ticked[row]&&locked[row])mask|=64;
  }
  foreach(int count in seen)if(count!=1)mask|=32;
  return mask;
 }
 // After the actions: same rows, every case annex ticked, every other row (KHBS) clear.
 internal static bool VisibleAnnexListExact(HtkkDeclarationCasePlan plan,string[] labels,bool[] ticked,int[] owner){
  if(labels.Length!=owner.Length||labels.Length!=ticked.Length)return false;
  int selected=0;
  for(int row=0;row<labels.Length;row++){
   if(labels[row]==null)return false;
   int expected=KhbsAnnexLabel(labels[row])?-1:ReviewedAnnexIndex(plan,labels[row]);
   if(expected==-1&&!KhbsAnnexLabel(labels[row]))return false;
   if(expected!=owner[row]||ticked[row]!=(expected>=0))return false;
   if(ticked[row])selected++;
  }
  return selected==plan.Annexes.Length;
 }
 // Original frmWinToKhai.cmdImportXML_Click: MenuID in "~B8~37~33~B9~N7~W1" → AddFullPLImportXML,
 // which adds every sheet of the menu before the XML is read.
 // A2 BCTC TT133 (BctcB01aTt133Nckt232, no ExportXML override): no control of 133_B01A_01_THTC_232
 // is bound to TKhaiThue/ngayKy, so WinDoWorkEvent.UpdateObjectValue never sets TTinChung.ngayKy and
 // WinFnProcess.BindToKhaiInfoToTTinChung leaves it at DateTime.Now; xmlExportTTinChung writes it
 // as yyyy-MM-dd. 78 copies ngayLap (ExportXML_0) and the other cases bind it to a cell.
 internal static string[] ExportDatePaths(HtkkDeclarationCasePlan plan){return plan!=null&&(plan.MenuId=="A2"||plan.MenuId=="Y7")?new string[]{"HSoThueDTu/HSoKhaiThue/TTinChung/TTinTKhaiThue/TKhaiThue/ngayKy"}:new string[0];}
 internal static bool ImportAddsAllAnnexes(HtkkDeclarationCasePlan plan){return plan!=null&&"~B8~37~33~B9~N7~W1~".IndexOf("~"+plan.MenuId+"~",StringComparison.Ordinal)>=0;}
 // Kê khai bổ sung (KHBS) of 01/NTNN I9 and 01/NTNN, NCCNN Y8 (mode declaration-amendment-khbs-inspect, non-gating; htkk_web
 // docs/KE-KHAI-BO-SUNG-01-NTNN.md, builder KHBS-NATIVE-CASE.md "01/NTNN"). Not lần-đầu declaration cases: CaseIds stays the
 // declaration-web-import-inspect list. The plans carry the KHBS schema (LoaiToKhai B exports against it; the Y8 one is the
 // same bytes as its main schema), no cell or XML checks (the whole-tree comparison of the B file decides) and the web leaf count.
 // The 05/KK-TNCN cases (L7 quý 3/2026, Z8 quý 4/2026; htkk_web docs/KE-KHAI-BO-SUNG-05-KK-TNCN.md, KHBS-NATIVE-CASE.md
 // "05/KK-TNCN") run on the same rounds: every round is the original import of the staged file, the 05-1/PBT case then chooses
 // Thuế tỉnh/CCT and CQT quản lý again (KhbsImportTick: path_15 has no XML leaf).
 internal static readonly string[] KhbsCaseIds=new string[]{"01NTNN-khbs-grossup-lan1-M09-2026","01NTNN-khbs-lan2-M09-2026","01NTNN-khbs-decrease-M09-2026","01NTNN-NCCNN-khbs-part1-M10-2026","01NTNN-NCCNN-khbs-part2-M10-2026","01NTNN-NCCNN-khbs-lan2-M10-2026",
  "01NTNN-NCCNN-khbs-part1-nodate-M10-2026","01NTNN-NCCNN-khbs-part2-nodate-M10-2026",
  "01NTNN-NCCNN-khbs-part2-585-M10-2026","01NTNN-NCCNN-khbs-part2-tncn-585-M10-2026","01NTNN-NCCNN-khbs-part1-future-contract-M10-2026",
  "05KK-khbs-increase-Q3-2026","05KK-khbs-lan2-Q3-2026","05KK-khbs-decrease-Q3-2026","05KK-TT89-khbs-increase-Q4-2026","05KK-PBT-khbs-Q3-2026","05KK-khbs-increase-M03-2026","05KK-PBT-nomst-khbs-Q3-2026",
  "01CNKD-khbs-increase-Q3-2026","01CNKD-khbs-decrease-Q3-2026","01CNKD-khbs-lan2-Q3-2026","01CNKD-PL01-khbs-Q3-2026",
  "02QTT-khbs-increase-Y2025","02QTT-khbs-lan2-Y2025","02QTT-khbs-decrease-Y2025","02QTT-khbs-refund-Y2025",
  "05QTT-khbs-increase-Y2025","05QTT-khbs-lan2-Y2025","05QTT-khbs-decrease-Y2025",
  "03TNDN-khbs-increase-Y2025","03TNDN-khbs-lan2-Y2025","03TNDN-khbs-decrease-Y2025","03TNDN-khbs-rate15-Y2025","03TNDN-khbs-negative-Y2025",
  "03NTNN-khbs-increase-M09-2026","03NTNN-khbs-lan2-M09-2026","03NTNN-khbs-decrease-M09-2026",
  "01TCKT-310-khbs-hop-tac-kd-Q4-2026","01TCKT-310-khbs-lan2-hop-tac-kd-Q4-2026","01TCKT-310-khbs-decrease-hop-tac-kd-Q4-2026","01TCKT-310-khbs-bds-M10-2026",
  "01GTGT-TT89-khbs-increase-M10-2026","01GTGT-TT89-khbs-decrease-M10-2026","01GTGT-TT89-khbs-lan2-increase-M10-2026","01GTGT-TT89-khbs-lan2-decrease-M10-2026"};
 internal static int KhbsSoLan(string caseId){return caseId=="01NTNN-khbs-lan2-M09-2026"||caseId=="01NTNN-NCCNN-khbs-lan2-M10-2026"||caseId=="05KK-khbs-lan2-Q3-2026"||caseId=="02QTT-khbs-lan2-Y2025"||caseId=="05QTT-khbs-lan2-Y2025"||caseId=="03TNDN-khbs-lan2-Y2025"||caseId=="03NTNN-khbs-lan2-M09-2026"||caseId=="01TCKT-310-khbs-lan2-hop-tac-kd-Q4-2026"||caseId=="01GTGT-TT89-khbs-lan2-increase-M10-2026"||caseId=="01GTGT-TT89-khbs-lan2-decrease-M10-2026"||caseId=="01CNKD-khbs-lan2-Q3-2026"?2:Array.IndexOf(KhbsCaseIds,caseId)>=0?1:0;}
 // Whether a bổ sung round runs the original "Tổng hợp KHBS": not for 01/CNKD (U5 KieuKHBS "" in the 5.8.2 Menu.xml;
 // frmWinToKhai.LoadButton shows btnTongHopKHBS only for LoaiToKhai B with a non-empty KieuKHBS).
 internal static bool KhbsSummary(string caseId){return Array.IndexOf(KhbsCaseIds,caseId)>=0&&!caseId.StartsWith("01CNKD-",StringComparison.Ordinal);}
 private static HtkkDeclarationCasePlan KhbsPlan(string caseId){
  if(caseId.StartsWith("05KK-",StringComparison.Ordinal))return Kk05KhbsPlan(caseId);
  if(caseId.StartsWith("01CNKD-",StringComparison.Ordinal))return CnkdKhbsPlan(caseId);
  if(caseId.StartsWith("02QTT-",StringComparison.Ordinal))return Qtt02KhbsPlan(caseId);
  if(caseId.StartsWith("05QTT-",StringComparison.Ordinal))return Qtt05KhbsPlan(caseId);
  if(caseId.StartsWith("03TNDN-khbs-",StringComparison.Ordinal))return Tndn03KhbsPlan(caseId);
  if(caseId.StartsWith("03NTNN-khbs-",StringComparison.Ordinal))return Ntnn03KhbsPlan(caseId);
  if(caseId.StartsWith("01TCKT-310-khbs-",StringComparison.Ordinal))return Tckt01KhbsPlan(caseId);
  if(caseId.StartsWith("01GTGT-TT89-khbs-",StringComparison.Ordinal))return Gtgt01Tt89KhbsPlan(caseId);
  bool i9=caseId.StartsWith("01NTNN-khbs-",StringComparison.Ordinal);
  int leaves=caseId=="01NTNN-khbs-grossup-lan1-M09-2026"?220:caseId=="01NTNN-NCCNN-khbs-part1-M10-2026"||caseId=="01NTNN-NCCNN-khbs-part1-nodate-M10-2026"?269:caseId=="01NTNN-NCCNN-khbs-part2-M10-2026"||caseId=="01NTNN-NCCNN-khbs-part2-nodate-M10-2026"?253:caseId=="01NTNN-NCCNN-khbs-lan2-M10-2026"?227:
   // HTKK 5.8.5 cases (htkkVersion 5.8.5): two Muc_I.1 rows (1749, 1099); four rows and ten 01-1/KHBS rows; phần I as part1.
   caseId=="01NTNN-NCCNN-khbs-part2-585-M10-2026"?256:caseId=="01NTNN-NCCNN-khbs-part2-tncn-585-M10-2026"?327:caseId=="01NTNN-NCCNN-khbs-part1-future-contract-M10-2026"?269:178;
  if(i9)return new HtkkDeclarationCasePlan(caseId,"I9","2.5.1","838","Ntnn01TT80Nckt251",new string[]{"101","101_8","I9"},"month","18","2026","09","01/09/2026","30/09/2026",false,
   new string[0],new string[]{"01|Tờ khai"},
   "InterfaceTemplates/excel/01_NTNN_TT80_251.xls","feebf2a918138aad860b52fb409232716027dc7ba59ec8aed861714d7e7de652","InterfaceTemplates/xml/01_NTNN_TT80_251.xml","cb8f1c83df2ebb590e314b2ca71fde4751760906e57df666e92086d6a1f9983c",
   "Validate/KHBS_01_NTNN_TT80_251.xsd","8d712f0611200c354704bf48dbea54c2d40a96777fe6dae1c4a213a0685938e6",TKhaiThue,TKhaiThueSha256,WorkbookService,leaves,new string[0],new string[0]);
  return new HtkkDeclarationCasePlan(caseId,"Y8","3.0.9","2012","Ntnn01TT89Nckt309",new string[]{"101","101_8","Y8"},"month","18","2026","10","01/10/2026","31/10/2026",false,
   new string[0],new string[]{"01|Tờ khai"},
   "InterfaceTemplates/excel/01_NTNN_NCCNN_TT89_309.xls","53630634bd02cc412ddde0682c2557226547737fceed792f595709a2fd0eafe1","InterfaceTemplates/xml/01_NTNN_NCCNN_TT89_309.xml","5c43131df4ecf265ddf9c780174416f95a249d82bd666339a97f0ea852f105d9",
   "Validate/KHBS_01_NTNN_NCCNN_TT89_309.xsd","7e417697b602867a819c80f59eaaae486ceb9148ab58867187206be5f75df1b8",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,leaves,new string[0],new string[0]);
 }
 // 05/KK-TNCN KHBS (L7 2.9.3 quý 3/2026, Z8 3.0.9 quý 4/2026): the plans of the lần đầu cases 05KK-withheld-Q3-2026 /
 // 05KK-TT89-withheld-Q4-2026 / 05KK-PBT-two-provinces-Q3-2026 with the KHBS schema of the form (KHBS_05_KK_TNCN_TT80_293.xsd,
 // KHBS_05_KK_TNCN_TT89_309.xsd), no cell or XML checks, and the web B file leaf count (contract leafTarget + 4 service leaves).
 private static HtkkDeclarationCasePlan Kk05KhbsPlan(string caseId){
  int leaves=caseId=="05KK-khbs-increase-Q3-2026"||caseId=="05KK-khbs-increase-M03-2026"?217:caseId=="05KK-TT89-khbs-increase-Q4-2026"?178:caseId=="05KK-PBT-khbs-Q3-2026"||caseId=="05KK-PBT-nomst-khbs-Q3-2026"?234:165;
  if(caseId=="05KK-TT89-khbs-increase-Q4-2026")return new HtkkDeclarationCasePlan(caseId,"Z8","3.0.9","2036","TncnKk05TT89Nckt309",new string[]{"101","101_11","Z8"},"quarter","14","2026","4","01/10/2026","31/12/2026",false,
   new string[0],new string[]{"01|Tờ khai"},
   "InterfaceTemplates/excel/05_KK_TNCN_TT89_309.xls","316a2c02e2d93ed254583775e5b8db2ab8909460b932a565f9a27c5d1a1b6c91","InterfaceTemplates/xml/05_KK_TNCN_TT89_309.xml","420921c52f38b929b432ca8fecc60fd6453b8b14702777612fd251cc2873fa2d",
   "Validate/KHBS_05_KK_TNCN_TT89_309.xsd","619a2ecf3228d80742e9dbea5c3939308f74fea55a94073e33bbc7efb23bdf97",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,leaves,new string[0],new string[0]);
  bool pbt=caseId=="05KK-PBT-khbs-Q3-2026"||caseId=="05KK-PBT-nomst-khbs-Q3-2026",month=caseId=="05KK-khbs-increase-M03-2026";
  // KieuKy 19 = SetLayoutToKhaiThangQuy: the monthly case picks tháng 03/2026 (monthly first declarations are refused only from
  // tháng 4/2026, 0682).
  return new HtkkDeclarationCasePlan(caseId,"L7","2.9.3","864","TncnKk05TT80Nckt293",new string[]{"101","101_11","L7"},month?"month":"quarter","19","2026",month?"03":"3",month?"01/03/2026":"01/07/2026",month?"31/03/2026":"30/09/2026",false,
   pbt?new string[]{"05-1/PBT-KK-TNCN"}:new string[0],pbt?new string[]{"01|Tờ khai","01-1|05-1/PBT-KK-TNCN"}:new string[]{"01|Tờ khai"},
   "InterfaceTemplates/excel/05_KK_TNCN_TT80_293.xls","3ce979a51388f872d4e881ffef944961f18c86cdd3ac6f5f8c61b7f4b5897f8f","InterfaceTemplates/xml/05_KK_TNCN_TT80_293.xml","ac49d746988fa0e18fa4f41c839b02b87d2d612988a20fae93004c5a99ed1d6e",
   "Validate/KHBS_05_KK_TNCN_TT80_293.xsd","91a2d625d1ddeaf5fe71fb5ca0413d25d063d3adb99e9b975e322d95a56d8ec4",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,leaves,new string[0],new string[0]);
 }
 // 01/CNKD KHBS (U5 3.1.0 quý 3/2026; htkk_web docs/KE-KHAI-BO-SUNG-01-CNKD.md, KHBS-NATIVE-CASE.md "01/CNKD"): the plan of
 // the lần đầu case 01CNKD-TT50-310-pl01-three-groups-Q3-2026 (with PL 01 for the PL 01 case, without it otherwise), no cell or
 // XML checks, and the web B file leaf count (contract leafTarget + 4 service leaves). Schema: the MAIN one, 01_CNKD_HKD_TT50_310.xsd.
 // WinFnProcess.GetToKhaiInfo sets ToKhaiInfo.XsdFileName to KHBS_<XsdSchema>_<VersionKBSXML>.xsd only for LoaiToKhai B with a
 // non-empty KieuKHBS (menus 31;30;39;33;28;M2 excepted), else <XsdSchema>_<VersionXML>.xsd; U5 has KieuKHBS "", so its B export
 // validates against the main schema (the KHBS one has the same bytes). Runs 43733536472/43733539063/43733541969 stopped at the
 // pinned-schema gate (exportSchemaPinnedVerified false) with the KHBS path.
 private static HtkkDeclarationCasePlan CnkdKhbsPlan(string caseId){
  bool pl01=caseId=="01CNKD-PL01-khbs-Q3-2026";
  return new HtkkDeclarationCasePlan(caseId,"U5","3.1.0","1266","CnkdHkd01TT50Nckt310",new string[]{"101","101_37","U5"},"quarter","21","2026","3","01/07/2026","30/09/2026",false,
   pl01?new string[]{"PL 01 43/2026/QH16"}:new string[0],pl01?new string[]{"01|Tờ khai","01-4|PL 01 43/2026/QH16"}:new string[]{"01|Tờ khai"},
   "InterfaceTemplates/excel/01_CNKD_HKD_TT50_310.xls","864ef2c1c28f4f0c807265fa2497264ec72283912dda1f3f6294b6b9aa8a3c56","InterfaceTemplates/xml/01_CNKD_HKD_TT50_310.xml","30f4d3162d6179ce8c233c977898b86f63756e741bda1a423c15e45babea0d86",
   "Validate/01_CNKD_HKD_TT50_310.xsd","c55ba118b03c859ed20f6bcf2cadfde89c2450a9869b00a36e075af917f75aff",TKhaiThue,TKhaiThueSha256,CnkdService,pl01?299:275,new string[0],new string[0]);
 }
 // 02/QTT-TNCN KHBS (B8 2.7.3 năm 2025; htkk_web docs/KE-KHAI-BO-SUNG-02-QTT-TNCN.md, KHBS-NATIVE-CASE.md "02/QTT-TNCN"): the
 // plan of the lần đầu case 02QTT-dependants-Y2025 (KieuKy 12, annex 02-1, every annex added by the import), the KHBS schema
 // KHBS_02_QTT_TNCN_TT80_273.xsd (B8 KieuKHBS 3: GetToKhaiInfo takes the KHBS schema for LoaiToKhai B), no cell or XML checks,
 // and the web B file leaf count (contract leafTarget + 4 service leaves).
 private static HtkkDeclarationCasePlan Qtt02KhbsPlan(string caseId){
  return new HtkkDeclarationCasePlan(caseId,"B8","2.7.3","952","TncnQtt02TT80Nckt273",new string[]{"101","101_11","B8"},"year","12","2025","","01/2025","12/2025",false,
   new string[]{"02-1/BK-QTT-TNCN"},new string[]{"02|Tờ khai","02-1|02-1/BK-QTT-TNCN"},
   "InterfaceTemplates/excel/02_QTT_TNCN_TT80_273.xls","e1eb77e740803215372e64e58d6c57bd71fc71ba64916ba1a8b4fddabbc95a26","InterfaceTemplates/xml/02_QTT_TNCN_TT80_273.xml","6b2a2c1d27c9298e1fe73b12138ab98e4f722f785e9c253ed91bde3570611f12",
   "Validate/KHBS_02_QTT_TNCN_TT80_273.xsd","b534fbed4424b694cb45dc9a37a65b8cfd9084daadeb810e7946c184303e7529",TKhaiThue,TKhaiThueSha256,WorkbookService,caseId=="02QTT-khbs-decrease-Y2025"?304:330,new string[0],new string[0]);
 }
 // 05/QTT-TNCN KHBS (B9 2.9.3 năm 2025; htkk_web docs/KE-KHAI-BO-SUNG-05-QTT-TNCN.md, KHBS-NATIVE-CASE.md "05/QTT-TNCN"): the
 // plan of the lần đầu case 05QTT-two-employees-Y2025 (KieuKy 12, annexes 05-1 and 05-3, every annex added by the import), the
 // KHBS schema KHBS_05_QTT_TNCN_TT80_293.xsd (KieuKHBS 3), no cell or XML checks, and the web B file leaf count (leafTarget + 4).
 private static HtkkDeclarationCasePlan Qtt05KhbsPlan(string caseId){
  return new HtkkDeclarationCasePlan(caseId,"B9","2.9.3","953","TncnQtt05TT80Nckt293",new string[]{"101","101_11","B9"},"year","12","2025","","01/2025","12/2025",false,
   new string[]{"05-1/BK-TNCN|05-1/BK-QTT-TNCN","05-3/BK-TNCN|05-3/BK-QTT-TNCN"},new string[]{"05|Tờ khai","05-1|05-1/BK-TNCN"},
   "InterfaceTemplates/excel/05_QTT_TNCN_TT80_293.xls","eb948994ab364965b6545cda88294e011605a643a88bb9c5cf5412bdd6008e11","InterfaceTemplates/xml/05_QTT_TNCN_TT80_293.xml","3f8791819f9fe088b939fec20c7d4deeb46931f3e20534dc434a86abd63bd250",
   "Validate/KHBS_05_QTT_TNCN_TT80_293.xsd","8f885a0f5c6abc500b1c6268891fdfcc78ffb7b96146ec088908c4c4f579931d",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,caseId=="05QTT-khbs-decrease-Y2025"?345:397,new string[0],new string[0]);
 }
 // 03/TNDN KHBS (N8 2.9.4 năm 2025; htkk_web docs/KE-KHAI-BO-SUNG-03-TNDN.md, KHBS-NATIVE-CASE.md "03/TNDN"): the plan of the
 // lần đầu cases 03TNDN-profit20-Y2025 / 03TNDN-rate15-Y2025 (KieuKy 11, annex 03-1A chosen in the period dialog, same workbook and
 // layout pins), the KHBS schema KHBS_03_TNDN_TT80_294.xsd (N8 KieuKHBS 3: GetToKhaiInfo takes the KHBS schema for LoaiToKhai B), no
 // cell or XML checks, and the web B file leaf count (contract leafTarget + 4 service leaves).
 private static HtkkDeclarationCasePlan Tndn03KhbsPlan(string caseId){
  // 03TNDN-khbs-negative-Y2025 changes fewer items (12 rows, no B1 / B2 / B13): its web B file has 386 compared leaves.
  int leaves=caseId=="03TNDN-khbs-negative-Y2025"?386:425;
  return new HtkkDeclarationCasePlan(caseId,"N8","2.9.4","892","Tndn03TT80Nckt294",new string[]{"101","101_2","N8"},"year","11","2025","","01/01/2025","31/12/2025",false,
   new string[]{"03-1A/TNDN"},new string[]{"03|Tờ khai","03-1A|03-1A/TNDN"},
   "InterfaceTemplates/excel/03_TNDN_TT80_294.xls","f7482448c4628bb56120eaa0cda5c245474c45f770b1d9f1c1b4caf31c319476","InterfaceTemplates/xml/03_TNDN_TT80_294.xml","cc05576d5356323c4f76e486814b72a3d48dd597523c1a0c11fba956e18be568",
   "Validate/KHBS_03_TNDN_TT80_294.xsd","42f72f6af7b53d74113c7005a1284ba1dacfd9267eae5ca50ad1d0b4f9558ba2",TKhaiThue,TKhaiThueSha256,WorkbookService,leaves,new string[0],new string[0]);
 }
 // 03/NTNN KHBS (J1 3.0.8 tháng 09/2026; htkk_web docs/KE-KHAI-BO-SUNG-03-NTNN.md, KHBS-NATIVE-CASE.md "03/NTNN"): the plan of
 // the lần đầu case 03NTNN-no-rate-M10-2026 (KieuKy 18, no annex, same workbook and layout pins) for kỳ 09/2026, the KHBS schema
 // KHBS_03_NTNN_TT80_308.xsd (J1 KieuKHBS 3: GetToKhaiInfo takes the KHBS schema for LoaiToKhai B), no cell or XML checks, and the
 // web B file leaf count (contract leafTarget + 4 service leaves). Every round is completed by KhbsImportTick (the rates again).
 private static HtkkDeclarationCasePlan Ntnn03KhbsPlan(string caseId){
  return new HtkkDeclarationCasePlan(caseId,"J1","3.0.8","840","Ntnn03TT80Nckt308",new string[]{"101","101_8","J1"},"month","18","2026","09","01/09/2026","30/09/2026",false,
   new string[0],new string[]{"01|Tờ khai"},
   "InterfaceTemplates/excel/03_NTNN_TT80_308.xls","ef4451f19a8a74ad667add7fd580ac83be149f7d35e65bbbe12aa42ccad11142","InterfaceTemplates/xml/03_NTNN_TT80_308.xml","41c8c6c92a684485aff87790739958948c94bf966cc5e56b6150a17f6beac550",
   "Validate/KHBS_03_NTNN_TT80_308.xsd","c99ad92ba68a08a8e319e52e6c617970d978882885bd746be01a67f8425d7272",TKhaiThue,TKhaiThueSha256,WorkbookService,172,new string[0],new string[0]);
 }
 // 01/TCKT 3.1.0 KHBS (Y7 on HTKK 5.8.2; htkk_web lib/htkk-tckt01-khbs.ts, KHBS-NATIVE-CASE.md "01/TCKT"): the plans of the lần đầu
 // cases 01TCKT-310-hop-tac-kd-two-individuals-Q4-2026 (quý 4/2026, 01/BK-KTHTKD) and 01TCKT-310-bds-three-lessors-M10-2026 (tháng
 // 10/2026, 02/BK-KTBĐS; the tỉnh/xã panel of the period dialog as there), same workbook and layout pins, the KHBS schema
 // KHBS_01_TCKT_TT89_310.xsd (Y7 KieuKHBS 3, VersionKHBS 3.1.0 in the 5.8.2 Menu.xml), no cell or XML checks, and the web B file
 // leaf count (contract leafTarget + 4 service leaves). ngayKy is the export day (ExportDatePaths, MenuId Y7).
 private static HtkkDeclarationCasePlan Tckt01KhbsPlan(string caseId){
  bool bds=caseId=="01TCKT-310-khbs-bds-M10-2026";
  int leaves=bds?246:caseId=="01TCKT-310-khbs-decrease-hop-tac-kd-Q4-2026"?202:228;
  return new HtkkDeclarationCasePlan(caseId,"Y7","3.1.0","2007","Tckt01TT89Nckt310",new string[]{"101","101_37","Y7"},bds?"month":"quarter","21","2026",bds?"10":"4","01/10/2026",bds?"31/10/2026":"31/12/2026",false,
   bds?new string[]{"02/BK-KTBĐS"}:new string[]{"01/BK-KTHTKD"},bds?new string[]{"01|Tờ khai","01-2|02/BK-KTBĐS"}:new string[]{"01|Tờ khai","01-1|01/BK-KTHTKD"},
   "InterfaceTemplates/excel/01_TCKT_TT89_310.xls","95ecbc2cd702100d49d946fd526ae71916a53229f25b335b358c4e35c3c48cd7","InterfaceTemplates/xml/01_TCKT_TT89_310.xml","2e99cdd5c7afc75ee539272ab2a8003ac0fb5d80387073d177a69f6723fdd69e",
   "Validate/KHBS_01_TCKT_TT89_310.xsd","4631d4c3d8b1a042158b53c36516a78be9f87db2c4e2f65c7a385675e5ef5020",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,leaves,new string[0],new string[0]);
 }
 // 01/GTGT TT89 KHBS (Z5 on HTKK 5.8.4; htkk_web lib/htkk-gtgt01-tt89-khbs.ts, KHBS-NATIVE-CASE.md "01/GTGT TT89"): the plan of
 // the lần đầu case 01GTGT-TT89-sale10-M10-2026 (tháng 10/2026, no phụ lục), same workbook and layout pins, the KHBS schema
 // KHBS_01_GTGT_TT89_309.xsd (Z5 KieuKHBS 3, VersionKHBS 3.0.9 in the 5.8.4 Menu.xml; the same bytes as 01_GTGT_TT89_309.xsd), no
 // cell or XML checks, and the web B file leaf count (contract leafTarget + 4 service leaves).
 private static HtkkDeclarationCasePlan Gtgt01Tt89KhbsPlan(string caseId){
  // Web B leaf count + 4 service leaves: decrease 291, lần 2 decrease 265 (six 01-1/KHBS rows), increase and lần 2 increase 304.
  int leaves=caseId=="01GTGT-TT89-khbs-decrease-M10-2026"?295:caseId=="01GTGT-TT89-khbs-lan2-decrease-M10-2026"?269:308;
  return new HtkkDeclarationCasePlan(caseId,"Z5","3.0.9","2032","Gtgt01TT89Nckt309",new string[]{"101","101_1","Z5"},"month","19","2026","10","01/10/2026","31/10/2026",false,
   new string[0],new string[]{"01|Tờ khai"},
   "InterfaceTemplates/excel/01_GTGT_TT89_309.xls","5370eb12c05cc2770e85ccc1bee7e6a7dc6138065f4c0fc4e0a418d3d9ee4585","InterfaceTemplates/xml/01_GTGT_TT89_309.xml","ba96834481a4b5b8a1c803572d10fafb669538402ed06f80a504c3212488638a",
   "Validate/KHBS_01_GTGT_TT89_309.xsd","8481f7c98ca9e008742552bda4f7ecc814cb91d453584b179fdf2d7767d9da19",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,leaves,new string[0],new string[0]);
 }
 // 05/KK-TNCN with 05-1/PBT: every imported round leaves Thuế tỉnh/CCT empty (no XML leaf), so the import is completed with the
 // reviewed combo edits of 05KK-PBT-two-provinces-Q3-2026 (the same two rows, offices unchanged between the versions).
 // 01/CNKD with PL 01: the giảm thuế ticks (AJ, no XML leaf) are made again after each import with the reviewed plan of the lần
 // đầu PL 01 case (rows 01 and 04 keep their 300tr / 200tr in every version of the case).
 // A tick cell left locked in a bổ sung round by a stale lockUnLockA_TK (01CNKD-PL01-khbs-Q3-2026, run 43742200645, lock shape
 // 151) gets one refresh through ButtonClick_0: the original SPACE on a giảm thuế checkbox of column AJ below the target found by
 // RefreshDeclarationTickLocks (unlocked, unticked, CE 0: the empty TMĐT row; HTKK clears it again, no daySangPLGiamThue for it).
 // Run 43758208221 showed the fixed AJ341 is not that cell once table_1 has three rows. Null: no refresh.
 internal static string KhbsTickRefresh(string caseId){return caseId=="01CNKD-PL01-khbs-Q3-2026"?"AJ":null;}
 // 03/NTNN (J1): Ntnn03TT80Nckt308.FinishImportXML (0x6001937) sets every imported rate [9] BU := getThuSuatByMa(CR, "DC_97") = ""
 // (CR has no XML leaf), so after each import the two rates of the case files (BU34 5, BU35 2: rows 34-35 of ThueNTNN) are typed
 // again through the original editor; TAB ends the edit (winFpSpread_CellChange -> WinDoWorkEvent.CellChange -> CellChange_0).
 // Method pins: the editor path of HTKK.exe only (HtkkOracleBaseline.Ntnn03KhbsRateMethodPins).
 internal static HtkkDeclarationTickPlan KhbsImportTick(string caseId){return caseId=="05KK-PBT-khbs-Q3-2026"||caseId=="05KK-PBT-nomst-khbs-Q3-2026"?ImportTick("05KK-PBT-two-provinces-Q3-2026"):caseId=="01CNKD-PL01-khbs-Q3-2026"?ImportTick("01CNKD-TT50-310-pl01-three-groups-Q3-2026"):Ntnn03KhbsRateTick(caseId);}
 private static HtkkDeclarationTickPlan Ntnn03KhbsRateTick(string caseId){
  if(caseId!="03NTNN-khbs-increase-M09-2026"&&caseId!="03NTNN-khbs-lan2-M09-2026"&&caseId!="03NTNN-khbs-decrease-M09-2026")return null;
  return new HtkkDeclarationTickPlan(new string[]{"number|BU34|5","number|BU35|2"},new string[0],new string[0],new string[0],HtkkOracleBaseline.Ntnn03KhbsRateMethodPins());
 }
 // Y8 KHBS rounds are TYPED (the original import resets the Y8 tables, release 238): round 0 the lần đầu rows, round 1 the bổ
 // sung rows, every planned cell typed again (the B sheet opens on the saved lần đầu, possibly reset). Values = the htkk_web
 // producer rows (generate-htkk-web-ntnn-khbs-reference.mjs); ngày ký 13/11/2026 as in the files. I9 rounds are imported: null.
 // The Y8 lần-2 case (01NTNN-NCCNN-khbs-lan2-M10-2026) is phần I with three typed rounds: round 0 the lần đầu, round 1 the
 // rows of bổ sung lần 1 (= 01NTNN-NCCNN-khbs-part1-M10-2026's bổ sung, saved and closed as an intermediate round; the staged
 // .web-prior.xml is that case's web file, verified but not imported), round 2 the lần 2 rows (TNDN revenue AZ 240.000.000).
 // The two "nodate" cases leave one date of the row key empty in every round, so the 01-1/KHBS key ends with an empty part (HTKK
 // exports the cell trimmed): phần I (01NTNN-NCCNN-khbs-part1-nodate-M10-2026) never types W60 (4) ngày hợp đồng, contract
 // HD-GL-202; phần II (01NTNN-NCCNN-khbs-part2-nodate-M10-2026) never types AE78 (6) ngày thanh toán of the supplier, HD-GL-005.
 // HTKK 5.8.5 cases (htkkVersion 5.8.5): 01NTNN-NCCNN-khbs-part2-585-M10-2026 types the rounds of the phần II case;
 // 01NTNN-NCCNN-khbs-part2-tncn-585-M10-2026 also types the individual's AJ86 / AZ86 150.000.000 in round 1 (thuế TNCN read by 5.8.5);
 // 01NTNN-NCCNN-khbs-part1-future-contract-M10-2026 types the phần I rounds with W60 31/12/2027 (after any run day), contract HD-GL-203.
 internal static HtkkDeclarationEntryPlan KhbsEntry(string caseId,int round){
  bool lan2=caseId=="01NTNN-NCCNN-khbs-lan2-M10-2026",noContractDate=caseId=="01NTNN-NCCNN-khbs-part1-nodate-M10-2026",noPaymentDate=caseId=="01NTNN-NCCNN-khbs-part2-nodate-M10-2026";
  bool futureContract=caseId=="01NTNN-NCCNN-khbs-part1-future-contract-M10-2026",tncn=caseId=="01NTNN-NCCNN-khbs-part2-tncn-585-M10-2026";
  bool part1=caseId=="01NTNN-NCCNN-khbs-part1-M10-2026"||lan2||noContractDate||futureContract,part2=caseId=="01NTNN-NCCNN-khbs-part2-M10-2026"||noPaymentDate||caseId=="01NTNN-NCCNN-khbs-part2-585-M10-2026"||tncn;
  if(!part1&&!part2||round<0||round>KhbsSoLan(caseId))return null;
  string[] entries;
  if(part1){
   string amount=round==0?"200000000":"220000000",tndn=round==2?"240000000":amount;
   entries=noContractDate?new string[]{"text|C60|NHA THAU NUOC NGOAI E - GIẢ LẬP","combo|L60|0|D|Dịch vụ, cho thuê máy móc thiết bị, bảo hiểm|BX60|01","text|S60|HD-GL-202","number|Y60|"+amount,
    "date|AE60|15/10/2026","number|AJ60|"+amount,"number|AN60|5","number|AZ60|"+tndn,"number|BD60|5","date-optional|AY98|13/11/2026"}:
    new string[]{"text|C60|NHA THAU NUOC NGOAI E - GIẢ LẬP","combo|L60|0|D|Dịch vụ, cho thuê máy móc thiết bị, bảo hiểm|BX60|01","text|S60|"+(futureContract?"HD-GL-203":"HD-GL-201"),"date|W60|"+(futureContract?"31/12/2027":"01/09/2026"),"number|Y60|"+amount,
    "date|AE60|15/10/2026","number|AJ60|"+amount,"number|AN60|5","number|AZ60|"+tndn,"number|BD60|5","date-optional|AY98|13/11/2026"};
   return new HtkkDeclarationEntryPlan("M6","M8","AY96","InterfaceIni/DM_NNKD_NTNN.xml","3aed1aea293f423271461892319217e33fc5dab32288dd708e6192a515802d17",
    new string[]{"ThueNTNN|60|1|0","ThueNCCNN|78|1|1","ThueCNKCT|86|1|1"},new string[]{"C","L","M","S","W","Y","AE","AJ","AN","AZ","BD","BH"},entries,HtkkOracleBaseline.EntryMethodPins());
  }
  string revenue=round==0?"200000000":"240000000",individualRevenue=tncn&&round==1?"150000000":"100000000";
  string[] supplier=noPaymentDate?new string[]{
   "text|C78|NHA CUNG CAP NUOC NGOAI C - GIẢ LẬP","combo|L78|0|D|Dịch vụ, cho thuê máy móc thiết bị, bảo hiểm|BX78|01","text|S78|HD-GL-005","date|W78|01/09/2026","number|Y78|200000000",
   "number|AJ78|"+revenue,"number|AN78|5","number|AZ78|"+revenue,"number|BD78|5"}:new string[]{
   "text|C78|NHA CUNG CAP NUOC NGOAI C - GIẢ LẬP","combo|L78|0|D|Dịch vụ, cho thuê máy móc thiết bị, bảo hiểm|BX78|01","text|S78|HD-GL-003","date|W78|01/09/2026","number|Y78|200000000",
   "date|AE78|15/10/2026","number|AJ78|"+revenue,"number|AN78|5","number|AZ78|"+revenue,"number|BD78|5"};
  string[] individual=new string[]{
   "text|C86|CA NHAN KHONG CU TRU D - GIẢ LẬP","combo|L86|4|H|Hoạt động kinh doanh khác|BX86|05","text|S86|HD-GL-004","date|W86|02/09/2026","number|Y86|100000000",
   "date|AE86|16/10/2026","number|AJ86|"+individualRevenue,"number|AN86|5","number|AZ86|"+individualRevenue,"number|BD86|2",
   "date-optional|AY98|13/11/2026"};
  entries=new string[supplier.Length+individual.Length];supplier.CopyTo(entries,0);individual.CopyTo(entries,supplier.Length);
  return new HtkkDeclarationEntryPlan("M8","M6","AY96","InterfaceIni/DM_NNKD_NTNN.xml","3aed1aea293f423271461892319217e33fc5dab32288dd708e6192a515802d17",
   new string[]{"ThueNTNN|60|1|1","ThueNCCNN|78|1|0","ThueCNKCT|86|1|0"},new string[]{"C","L","M","S","W","Y","AE","AJ","AN","AZ","BD","BH"},entries,HtkkOracleBaseline.EntryMethodPins());
 }
 // Every case not listed: the fixed synthetic profile and period place of all earlier cases.
 internal static HtkkCaseGeography Geography(string caseId){
  switch(caseId){
   // Hoạt động khác tỉnh: profile CQT 82500 (Thuế tỉnh/CCT 82500 too: loadCqtCapChiCucTheoDiaBanXa lists 82500 alone under it), period
   // Hải Phòng / Phường Đồ Sơn / 82500 / 82500 (loadCqtCapCucTheoDiaBanXa of 10309019 offers 10300, 82500, 82700).
   case "01GTGT-TT89-other-province-M10-2026":return new HtkkCaseGeography(new string[]{"82500","Chi cục Thuế doanh nghiệp lớn","82500","Chi cục Thuế doanh nghiệp lớn","103","Thành phố Hải Phòng","10309019","Phường Đồ Sơn","82500","Chi cục Thuế doanh nghiệp lớn","82500","Chi cục Thuế doanh nghiệp lớn"});
   default:return new HtkkCaseGeography(new string[]{"10100","Thuế Thành phố Hà Nội","10129","Thuế cơ sở 16 Thành phố Hà Nội","101","Thành phố Hà Nội","10129087","Phường Sơn Tây","10100","Thuế Thành phố Hà Nội","10129","Thuế cơ sở 16 Thành phố Hà Nội"});
  }
 }
 internal static HtkkDeclarationCasePlan Find(string caseId){
  switch(caseId){
   case "01NTNN-khbs-grossup-lan1-M09-2026":case "01NTNN-khbs-lan2-M09-2026":case "01NTNN-khbs-decrease-M09-2026":case "01NTNN-NCCNN-khbs-part1-M10-2026":case "01NTNN-NCCNN-khbs-part2-M10-2026":case "01NTNN-NCCNN-khbs-lan2-M10-2026":
   case "01NTNN-NCCNN-khbs-part1-nodate-M10-2026":case "01NTNN-NCCNN-khbs-part2-nodate-M10-2026":case "05KK-PBT-nomst-khbs-Q3-2026":
   case "01NTNN-NCCNN-khbs-part2-585-M10-2026":case "01NTNN-NCCNN-khbs-part2-tncn-585-M10-2026":case "01NTNN-NCCNN-khbs-part1-future-contract-M10-2026":
   case "05KK-khbs-increase-Q3-2026":case "05KK-khbs-lan2-Q3-2026":case "05KK-khbs-decrease-Q3-2026":case "05KK-TT89-khbs-increase-Q4-2026":case "05KK-PBT-khbs-Q3-2026":case "05KK-khbs-increase-M03-2026":
   case "01CNKD-khbs-increase-Q3-2026":case "01CNKD-khbs-decrease-Q3-2026":case "01CNKD-khbs-lan2-Q3-2026":case "01CNKD-PL01-khbs-Q3-2026":
   case "02QTT-khbs-increase-Y2025":case "02QTT-khbs-lan2-Y2025":case "02QTT-khbs-decrease-Y2025":case "02QTT-khbs-refund-Y2025":
   case "05QTT-khbs-increase-Y2025":case "05QTT-khbs-lan2-Y2025":case "05QTT-khbs-decrease-Y2025":
   case "03TNDN-khbs-increase-Y2025":case "03TNDN-khbs-lan2-Y2025":case "03TNDN-khbs-decrease-Y2025":case "03TNDN-khbs-rate15-Y2025":case "03TNDN-khbs-negative-Y2025":
   case "03NTNN-khbs-increase-M09-2026":case "03NTNN-khbs-lan2-M09-2026":case "03NTNN-khbs-decrease-M09-2026":
   case "01TCKT-310-khbs-hop-tac-kd-Q4-2026":case "01TCKT-310-khbs-lan2-hop-tac-kd-Q4-2026":case "01TCKT-310-khbs-decrease-hop-tac-kd-Q4-2026":case "01TCKT-310-khbs-bds-M10-2026":
   case "01GTGT-TT89-khbs-increase-M10-2026":case "01GTGT-TT89-khbs-decrease-M10-2026":case "01GTGT-TT89-khbs-lan2-increase-M10-2026":case "01GTGT-TT89-khbs-lan2-decrease-M10-2026":return KhbsPlan(caseId);
   // N8 03/TNDN TT80: KieuKy 11 = SetLayoutToKhaiNamTuNgayDenNgay (year + from/to date).
   case "03TNDN-profit20-Y2025":return new HtkkDeclarationCasePlan(caseId,"N8","2.9.4","892","Tndn03TT80Nckt294",new string[]{"101","101_2","N8"},"year","11","2025","","01/01/2025","31/12/2025",false,
    new string[]{"03-1A/TNDN"},new string[]{"03|Tờ khai","03-1A|03-1A/TNDN"},
    "InterfaceTemplates/excel/03_TNDN_TT80_294.xls","f7482448c4628bb56120eaa0cda5c245474c45f770b1d9f1c1b4caf31c319476","InterfaceTemplates/xml/03_TNDN_TT80_294.xml","cc05576d5356323c4f76e486814b72a3d48dd597523c1a0c11fba956e18be568",
    "Validate/03_TNDN_TT80_294.xsd","5961845ccec5ca08b681ecc7a5ab91e168974a738307293406bea58464af6981",TKhaiThue,TKhaiThueSha256,WorkbookService,147,
    new string[]{"03-1A|E23|5000000000","03-1A|E26|100000000","03-1A|E29|10000000","03-1A|E32|3000000000","03-1A|E33|400000000","03-1A|E34|300000000","03-1A|E35|50000000","03-1A|E38|20000000","03-1A|E39|5000000","03|O38|25000000","03|O50|1200000000","03|O66|1200000000","03|O98|200000000"},
    // Header ct04 (control 91, DM_NganhCoDoanhThuCao) and ct05 are required by Header!B25/B26 (release 213: 0016).
    // Release 214 (run 42243368664): AutoBindData_0 writes kyTaiChinh as profile "dd/MM" text, control
    // "0,00" exports ct05 as 100.00, and the DC_184 rate code (R66 = ctC7_thueSuat) must be 20: an empty
    // imported rate made HTKK compute ctC9 = ctC17 = 0.
    new string[]{Main+"Header/kyTaiChinh_Tu|01/01",Main+"Header/kyTaiChinh_Den|31/12",Main+"Header/ct04_ma|C10",Main+"Header/ct05|100.00","HSoThueDTu/HSoKhaiThue/PLuc/PLuc_03_1A_TNDN/ct22|1175000000",Main+"ctA1|1175000000",Main+"ctB13|1200000000",Main+"ctC1|1200000000",Main+"ctC7_thueSuat|20",Main+"ctC9|240000000",Main+"ctC17|240000000",Main+"ctE1|240000000",Main+"ctI1|40000000"});
   // N8 03/TNDN with the C7 rate chosen in the DC_184 combobox C66 (SelectedValue R66 = ctC7_thueSuat; HTKK 5.8.2 oracle,
   // non-gating). Same menu, template, XSD and class as 5.8.1 (identical pins below). Tndn03TT80Nckt294.AutoBindData_0
   // locks C66 only when PeriodInfo.Nam < 2025, so year 2025 keeps the imported item; ctC9 (O70) = ROUND(O66*R66/100).
   // The cell checks read back the imported rate (R66) and HTKK's own C9 before the export.
   case "03TNDN-rate15-Y2025":return new HtkkDeclarationCasePlan(caseId,"N8","2.9.4","892","Tndn03TT80Nckt294",new string[]{"101","101_2","N8"},"year","11","2025","","01/01/2025","31/12/2025",false,
    new string[]{"03-1A/TNDN"},new string[]{"03|Tờ khai","03-1A|03-1A/TNDN"},
    "InterfaceTemplates/excel/03_TNDN_TT80_294.xls","f7482448c4628bb56120eaa0cda5c245474c45f770b1d9f1c1b4caf31c319476","InterfaceTemplates/xml/03_TNDN_TT80_294.xml","cc05576d5356323c4f76e486814b72a3d48dd597523c1a0c11fba956e18be568",
    "Validate/03_TNDN_TT80_294.xsd","5961845ccec5ca08b681ecc7a5ab91e168974a738307293406bea58464af6981",TKhaiThue,TKhaiThueSha256,WorkbookService,147,
    new string[]{"03-1A|E23|2400000000","03-1A|E29|5000000","03-1A|E32|1800000000","03-1A|E33|200000000","03-1A|E34|150000000","03-1A|E35|5000000","03|O38|10000000","03|O50|260000000","03|O66|260000000","03|O98|20000000","03|R66|15","03|O70|39000000"},
    new string[]{Main+"Header/kyTaiChinh_Tu|01/01",Main+"Header/kyTaiChinh_Den|31/12",Main+"Header/ct04_ma|C10",Main+"Header/ct05|100.00","HSoThueDTu/HSoKhaiThue/PLuc/PLuc_03_1A_TNDN/ct22|250000000",Main+"ctA1|250000000",Main+"ctB13|260000000",Main+"ctC1|260000000",Main+"ctC7_thuNhap|260000000",Main+"ctC7_tenThueSuat|+ Thu nhập tính thuế áp dụng thuế suất 15%",Main+"ctC7_thueSuat|15",Main+"ctC9|39000000",Main+"ctC17|39000000",Main+"ctE1|39000000",Main+"ctI1|19000000"});
   case "03TNDN-rate17-Y2025":return new HtkkDeclarationCasePlan(caseId,"N8","2.9.4","892","Tndn03TT80Nckt294",new string[]{"101","101_2","N8"},"year","11","2025","","01/01/2025","31/12/2025",false,
    new string[]{"03-1A/TNDN"},new string[]{"03|Tờ khai","03-1A|03-1A/TNDN"},
    "InterfaceTemplates/excel/03_TNDN_TT80_294.xls","f7482448c4628bb56120eaa0cda5c245474c45f770b1d9f1c1b4caf31c319476","InterfaceTemplates/xml/03_TNDN_TT80_294.xml","cc05576d5356323c4f76e486814b72a3d48dd597523c1a0c11fba956e18be568",
    "Validate/03_TNDN_TT80_294.xsd","5961845ccec5ca08b681ecc7a5ab91e168974a738307293406bea58464af6981",TKhaiThue,TKhaiThueSha256,WorkbookService,147,
    new string[]{"03-1A|E23|20000000000","03-1A|E26|200000000","03-1A|E29|50000000","03-1A|E32|15000000000","03-1A|E33|1500000000","03-1A|E34|1200000000","03-1A|E35|100000000","03-1A|E38|30000000","03-1A|E39|10000000","03|O38|30000000","03|O50|2100000000","03|O66|2100000000","03|O98|300000000","03|R66|17","03|O70|357000000"},
    new string[]{Main+"Header/kyTaiChinh_Tu|01/01",Main+"Header/kyTaiChinh_Den|31/12",Main+"Header/ct04_ma|C10",Main+"Header/ct05|100.00","HSoThueDTu/HSoKhaiThue/PLuc/PLuc_03_1A_TNDN/ct22|2070000000",Main+"ctA1|2070000000",Main+"ctB13|2100000000",Main+"ctC1|2100000000",Main+"ctC7_thuNhap|2100000000",Main+"ctC7_tenThueSuat|+ Thu nhập tính thuế áp dụng thuế suất 17%",Main+"ctC7_thueSuat|17",Main+"ctC9|357000000",Main+"ctC17|357000000",Main+"ctE1|357000000",Main+"ctI1|57000000"});
   // A2 B01a-DNN TT133: KieuKy 26 = SetLayoutToKhaiNamTuNgayDenNgayBCTC. BCKQHĐKD and BCĐTK are both
   // required (CheckChonPlBctc / Validate_0 0485; release 213 refused the set without BCĐTK).
   case "BCTC133-B01a-basic-Y2025":return new HtkkDeclarationCasePlan(caseId,"A2","2.3.2","683","BctcB01aTt133Nckt232",new string[]{"101","101_6","A2"},"year","26","2025","","01/01/2025","31/12/2025",false,
    new string[]{"BCKQHĐKD","BCĐTK"},new string[]{"01|BCTHTC","01-1|BCKQHĐKD","01-4|BCĐTK"},
    "InterfaceTemplates/excel/133_B01A_DNN_BCTC_232.xls","6ebea484ce00adb397281e45eb65206bea6d15405d08fc974343c2ce47529783","InterfaceTemplates/xml/133_B01A_01_THTC_232.xml","7bfd648f4760c0d2cdce61c1bd1788f3143c01ce0294aa5b46fad80d7e6cc1fb",
    "Validate/133_B01A_DNN_BCTC_232.xsd","a1e92ba43fbc869bc6da2c1c987fafa5a3b8b0d9524fd137149e84099487327c",TKhaiThue,TKhaiThueSha256,WorkbookService,975,
    new string[]{"01|R40|500000000","01|R42|100000000","01|R47|200000000","01|R62|1000000000","01|R69|300000000","01|R80|1500000000","01-1|J22|2000000000","01-1|J23|50000000","01-1|J25|1200000000","01-4|P41|100000000","01-4|X41|50000000","01-4|T139|100000000","01-4|AB139|50000000"},
    new string[]{Main+"SoCuoiNam/ct200|1800000000",Main+"SoCuoiNam/ct500|1800000000","HSoThueDTu/HSoKhaiThue/PLuc/PL_KQHDSXKD/NamNay/ct10|1950000000","HSoThueDTu/HSoKhaiThue/PLuc/PL_KQHDSXKD/NamNay/ct20|750000000","HSoThueDTu/HSoKhaiThue/PLuc/PL_CDTK/SoDuCuoiKy/No/ct111|150000000","HSoThueDTu/HSoKhaiThue/PLuc/PL_CDTK/SoDuCuoiKy/Co/ct411|150000000","HSoThueDTu/HSoKhaiThue/PLuc/PL_CDTK/SoDuCuoiKy/No/tongCong|150000000","HSoThueDTu/HSoKhaiThue/PLuc/PL_CDTK/SoDuCuoiKy/Co/tongCong|150000000"});
   // 78 BCTC TT200: KieuKy 26; '78' shows pnQuyetToan_LienTuc (going-concern choice).
   // Exactly one LCTT is required (CheckChonPlBctc 0395, cmdExport_Click 0478; run 42218292765): LCTTGT.
   case "BCTC200-LT-basic-Y2025":return new HtkkDeclarationCasePlan(caseId,"78","2.2.6","402","BctcTt200Nckt226",new string[]{"101","101_6","78"},"year","26","2025","","01/01/2025","31/12/2025",true,
    new string[]{"KQHĐSXKD","LCTTGT"},new string[]{"01|CĐKT","01-1|KQHĐSXKD","01-3|LCTTGT"},
    "InterfaceTemplates/excel/200_BCTC_226.xls","c67bdb7a874e75c0c402144711abbf08f7e00c8705a47e2e2cf7dfbdf5d5d50b","InterfaceTemplates/xml/200_01_CDKT_226.xml","b6ac0bc4efaba4e90a32ed9bad6c7ccf51322c5b3e4f2f5872b940ea9bbe2c37",
    "Validate/200_01_CDKT_226.xsd","b2e6c14b68ffd30a09070bbf9377df3df544b23d2b3a585602714335c6b2a90f",TKhaiThue,TKhaiThueSha256,WorkbookService,570,
    // Header!B46 (release 213: 0016): the going-concern total capital [440] must be non-zero and equal [270].
    new string[]{"01-1|I22|3000000000","01-1|I25|2000000000","01|R58|500000000","01|R152|500000000"},
    new string[]{Main+"hoatDongLienTuc|true",Main+"CDKT_HoatDongLienTuc/SoCuoiNam/ct270|500000000",Main+"CDKT_HoatDongLienTuc/SoCuoiNam/ct440|500000000",Main+"CDKT_HoatDongLienTuc/nguoiLapBieu|Người lập giả lập","HSoThueDTu/HSoKhaiThue/PLuc/PL_KQHDSXKD/NamNay/ct20|1000000000"});
   // L7 05/KK-TNCN TT80: KieuKy 19 = SetLayoutToKhaiThangQuy, quarter (from 4/2026 a monthly first
   // declaration is refused: frmHTKKPeriod.btnDongY_Click 0682, run 42218296460); no activity list.
   case "05KK-withheld-Q3-2026":return new HtkkDeclarationCasePlan(caseId,"L7","2.9.3","864","TncnKk05TT80Nckt293",new string[]{"101","101_11","L7"},"quarter","19","2026","3","01/07/2026","30/09/2026",false,
    new string[0],new string[]{"01|Tờ khai"},
    "InterfaceTemplates/excel/05_KK_TNCN_TT80_293.xls","3ce979a51388f872d4e881ffef944961f18c86cdd3ac6f5f8c61b7f4b5897f8f","InterfaceTemplates/xml/05_KK_TNCN_TT80_293.xml","ac49d746988fa0e18fa4f41c839b02b87d2d612988a20fae93004c5a99ed1d6e",
    "Validate/05_KK_TNCN_TT80_293.xsd","9cd4d367123ee0ac1f94fb043975738ac142420d558bb24969e4c0afe64ac846",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,56,
    new string[]{"01|U40|9","01|U43|120000000","01|U49|100000000","01|U52|9000000","01|U55|100001"},
    new string[]{Main+"mst_cu|9999999997",Main+"ct16|10",Main+"ct17|8",Main+"ct18|9",Main+"ct19|7",Main+"ct20|2",Main+"ct21|120000000",Main+"ct22|100000000",Main+"ct23|20000000",Main+"ct24|1000005",Main+"ct25|3000000",Main+"ct26|100000000",Main+"ct27|80000000",Main+"ct28|20000000",Main+"ct29|9000000",Main+"ct30|5000000",Main+"ct31|4000000",Main+"ct32|100001"});
   // Z8 05/KK-TNCN TT89 (HTKK 5.8.2 only, case htkkVersion 5.8.2): KieuKy 14 = SetLayoutToKhaiQuy; StartDate 01/10/2026.
   // 24 XML checks (the plan bound): every computed indicator and the inputs they depend on; the whole-tree
   // comparison still covers all 69 leaves, including the omitted inputs [26] [28] [30] [31] [33] [34] [37] [38] [43].
   case "05KK-TT89-withheld-Q4-2026":return new HtkkDeclarationCasePlan(caseId,"Z8","3.0.9","2036","TncnKk05TT89Nckt309",new string[]{"101","101_11","Z8"},"quarter","14","2026","4","01/10/2026","31/12/2026",false,
    new string[0],new string[]{"01|Tờ khai"},
    "InterfaceTemplates/excel/05_KK_TNCN_TT89_309.xls","316a2c02e2d93ed254583775e5b8db2ab8909460b932a565f9a27c5d1a1b6c91","InterfaceTemplates/xml/05_KK_TNCN_TT89_309.xml","420921c52f38b929b432ca8fecc60fd6453b8b14702777612fd251cc2873fa2d",
    "Validate/05_KK_TNCN_TT89_309.xsd","f4ea48433b04be487587b38f10494ef4486656900faa01e595771110f43a2c9c",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,69,
    new string[]{"01|U63|10","01|U69|180000000","01|U76|8000000","01|U84|150000000","01|U90|90000000","01|U96|200001","01|U97|5000000","01|U106|12000000"},
    new string[]{Main+"mst_cu|9999999997",Main+"ct14|0",Main+"ct15|12",Main+"ct16|10",Main+"ct17|10",Main+"ct18|8",Main+"ct19|2",Main+"ct20|180000000",Main+"ct21|150000000",Main+"ct22|30000000",Main+"ct23|2000005",Main+"ct24|8000000",Main+"ct25|0",Main+"ct27|0",Main+"ct29|150000000",Main+"ct32|90000000",Main+"ct35|200001",Main+"ct36|5000000",Main+"ct39|0",Main+"ct40|0",Main+"ct41|1000000",Main+"ct42|12000000",Main+"ct44|6000000",Main+"ct45|200001"});
   // 05/KK-TNCN with bảng 05-1/PBT-KK-TNCN (non-gating, HTKK 5.8.2 oracle, mode web-xml-import-tick-reexport with combo
   // edits; htkk_web docs/NGHIEP-VU-TNCN.md "Bảng phân bổ 05-1/PBT-KK-TNCN"). [15] (L7) / [14] (Z8) ticked; two rows of the
   // tiền lương table: trụ sở chính in Hà Nội (ward 10129087, Thuế tỉnh/CCT 10100, CQT quản lý 10129) and a branch (mã địa
   // điểm 00001) in Hải Phòng (ward 10309019, 10300, 10309). Thuế tỉnh/CCT (control 8, Path path_15) has no XML leaf, so the
   // import leaves it empty (GetValueFromSelectedCell returns for control 8 in these menus) and Header B37 would refuse
   // the export: ImportTick chooses it again, then CQT quản lý (cleared by that choice). Rows 44-45; the total row is 47.
   case "05KK-PBT-two-provinces-Q3-2026":return new HtkkDeclarationCasePlan(caseId,"L7","2.9.3","864","TncnKk05TT80Nckt293",new string[]{"101","101_11","L7"},"quarter","19","2026","3","01/07/2026","30/09/2026",false,
    new string[]{"05-1/PBT-KK-TNCN"},new string[]{"01|Tờ khai","01-1|05-1/PBT-KK-TNCN"},
    "InterfaceTemplates/excel/05_KK_TNCN_TT80_293.xls","3ce979a51388f872d4e881ffef944961f18c86cdd3ac6f5f8c61b7f4b5897f8f","InterfaceTemplates/xml/05_KK_TNCN_TT80_293.xml","ac49d746988fa0e18fa4f41c839b02b87d2d612988a20fae93004c5a99ed1d6e",
    "Validate/05_KK_TNCN_TT80_293.xsd","9cd4d367123ee0ac1f94fb043975738ac142420d558bb24969e4c0afe64ac846",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,110,
    new string[]{"01|U40|9","01|U43|120000000","01|U49|100000000","01|U52|9000000","01|U55|100001","01-1|L47|120000000","01-1|M47|100000000","01-1|N47|10","01-1|O47|9","01-1|P47|9000000","01-1|R44|101","01-1|R45|103","01-1|Z44|10129087","01-1|Z45|10309019","01-1|T44|10100","01-1|T45|10300","01-1|U44|10129","01-1|U45|10309"},
    new string[]{Main+"mst_cu|9999999997",Main+"ct15|1",Main+"ct16|10",Main+"ct17|8",Main+"ct18|9",Main+"ct19|7",Main+"ct20|2",Main+"ct21|120000000",Main+"ct22|100000000",Main+"ct23|20000000",Main+"ct24|1000005",Main+"ct25|3000000",Main+"ct26|100000000",Main+"ct27|80000000",Main+"ct28|20000000",Main+"ct29|9000000",Main+"ct30|5000000",Main+"ct31|4000000",Main+"ct32|100001"});
   case "05KK-TT89-PBT-two-provinces-Q4-2026":return new HtkkDeclarationCasePlan(caseId,"Z8","3.0.9","2036","TncnKk05TT89Nckt309",new string[]{"101","101_11","Z8"},"quarter","14","2026","4","01/10/2026","31/12/2026",false,
    new string[]{"05-1/PBT-KK-TNCN"},new string[]{"01|Tờ khai","01-1|05-1/PBT-KK-TNCN"},
    "InterfaceTemplates/excel/05_KK_TNCN_TT89_309.xls","316a2c02e2d93ed254583775e5b8db2ab8909460b932a565f9a27c5d1a1b6c91","InterfaceTemplates/xml/05_KK_TNCN_TT89_309.xml","420921c52f38b929b432ca8fecc60fd6453b8b14702777612fd251cc2873fa2d",
    "Validate/05_KK_TNCN_TT89_309.xsd","f4ea48433b04be487587b38f10494ef4486656900faa01e595771110f43a2c9c",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,117,
    new string[]{"01|U63|10","01|U69|180000000","01|U84|150000000","01|U96|200001","01|U106|12000000","01-1|L47|180000000","01-1|M47|150000000","01-1|N47|12","01-1|O47|10","01-1|P47|12000000","01-1|R44|101","01-1|R45|103","01-1|Z44|10129087","01-1|Z45|10309019","01-1|T44|10100","01-1|T45|10300","01-1|U44|10129","01-1|U45|10309"},
    new string[]{Main+"mst_cu|9999999997",Main+"ct14|1",Main+"ct15|12",Main+"ct16|10",Main+"ct17|10",Main+"ct18|8",Main+"ct19|2",Main+"ct20|180000000",Main+"ct21|150000000",Main+"ct22|30000000",Main+"ct23|2000005",Main+"ct24|8000000",Main+"ct25|0",Main+"ct27|0",Main+"ct29|150000000",Main+"ct32|90000000",Main+"ct35|200001",Main+"ct36|5000000",Main+"ct39|0",Main+"ct40|0",Main+"ct41|1000000",Main+"ct42|12000000",Main+"ct44|6000000",Main+"ct45|200001"});
   // B9 05/QTT-TNCN TT80: KieuKy 12 = SetLayoutToKhaiNamTuThangDenThang; annexes 05-1, 05-3.
   case "05QTT-two-employees-Y2025":return new HtkkDeclarationCasePlan(caseId,"B9","2.9.3","953","TncnQtt05TT80Nckt293",new string[]{"101","101_11","B9"},"year","12","2025","","01/2025","12/2025",false,
    new string[]{"05-1/BK-TNCN|05-1/BK-QTT-TNCN","05-3/BK-TNCN|05-3/BK-QTT-TNCN"},new string[]{"05|Tờ khai","05-1|05-1/BK-TNCN"},
    "InterfaceTemplates/excel/05_QTT_TNCN_TT80_293.xls","eb948994ab364965b6545cda88294e011605a643a88bb9c5cf5412bdd6008e11","InterfaceTemplates/xml/05_QTT_TNCN_TT80_293.xml","3f8791819f9fe088b939fec20c7d4deeb46931f3e20534dc434a86abd63bd250",
    "Validate/05_QTT_TNCN_TT80_293.xsd","0556354bbe766d6ff75ab4fccb456ea7bd99c6915ad20628149f170bda389635",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,162,
    // Release 227 (run 42302313967): the import reached the sheet check and failed exactly on the four
    // checks 56f6393 left at the pre-d86e434 values (cell mask 1283 = AE24, AE25, U92, U95). They now
    // equal the input and the XML checks below: 05-1 [21] (AE) 95,200,000 / 68,000,000, [38] U92
    // 6,520,000, [41] U95 5,480,000.
    // Release 231 (run 42316192917): the export was refused with 0016 at 05-1!W24 (diagnostic cell
    // 2024023): TncnQtt05TT80Nckt293.FinishImportXML (0x600228a, IL 0x00ba-0x013a) recomputes 05-1
    // [16]/BF from 05-3 only for more than one 05-3 row, so BI stayed 11tr*12 below [17] W and
    // Validate_1 E_52 (0x0d36-0x0d5c) refused it. The case now has two dependants of employee A
    // (12 + 6 months): BI24 = W24 = 211,200,000, [21] 68,800,000, [38] 3,880,000, [41] 8,120,000.
    new string[]{"05-1|BI24|211200000","05-1|AE24|68800000","05-1|AE25|68000000","05|U49|2","05|U51|1","05|U61|500000000","05|U71|300000000","05|U74|12000000","05|U89|1","05|U92|3880000","05|U94|0","05|U95|8120000"},
    new string[]{Main+"mst_cu|9999999997",Main+"NVuKhauTruThue/ct16|2",Main+"NVuKhauTruThue/ct17|2",Main+"NVuKhauTruThue/ct18|1",Main+"NVuKhauTruThue/ct19|1",Main+"NVuKhauTruThue/ct23|500000000",Main+"NVuKhauTruThue/ct24|500000000",Main+"NVuKhauTruThue/ct28|300000000",Main+"NVuKhauTruThue/ct29|300000000",Main+"NVuKhauTruThue/ct31|12000000",Main+"NVuKhauTruThue/ct32|12000000",Main+"NVuQToanThay/ct35|1",Main+"NVuQToanThay/ct36|12000000",Main+"NVuQToanThay/ct38|3880000",Main+"NVuQToanThay/ct40|0",Main+"NVuQToanThay/ct41|8120000"});
   // B8 02/QTT-TNCN TT80 (non-gating): KieuKy 12 = SetLayoutToKhaiNamTuThangDenThang (hidden annex
   // list; cmdImportXML_Click adds every annex for B8); NopTheoTinhCQT 3 (geography panel); annex 02-1.
   // Inputs [21]/[34] and the dependant count [24] are checked on the imported sheet; the whole tree
   // decides the case. Mapping 02_QTT_TNCN_TT80_273.xml: ct21 M_86, ct24 M_94, ct34 M_109.
   case "02QTT-dependants-Y2025":return new HtkkDeclarationCasePlan(caseId,"B8","2.7.3","952","TncnQtt02TT80Nckt273",new string[]{"101","101_11","B8"},"year","12","2025","","01/2025","12/2025",false,
    new string[]{"02-1/BK-QTT-TNCN"},new string[]{"02|Tờ khai","02-1|02-1/BK-QTT-TNCN"},
    "InterfaceTemplates/excel/02_QTT_TNCN_TT80_273.xls","e1eb77e740803215372e64e58d6c57bd71fc71ba64916ba1a8b4fddabbc95a26","InterfaceTemplates/xml/02_QTT_TNCN_TT80_273.xml","6b2a2c1d27c9298e1fe73b12138ab98e4f722f785e9c253ed91bde3570611f12",
    "Validate/02_QTT_TNCN_TT80_273.xsd","9467d23b5deddd65739532ad470024df2f71af491b7cfc756e24bdd4225983cd",TKhaiThue,TKhaiThueSha256,WorkbookService,130,
    new string[]{"02|M86|300000000","02|M94|2","02|M109|10000000"},
    new string[]{Main+"ct20|300000000",Main+"ct21|300000000",Main+"ct24|2",Main+"ct27|79200000",Main+"ct34|10000000"});
   // B8 năm 2025 with hoàn trả qua chuyển khoản (non-gating, HTKK 5.8.2 oracle; same menu, XLS, XML template and XSD as 5.8.1).
   // Năm 2025: frmHTKKPeriod.LoadDefaultInfor opens a year period on Now.Year - 1, so mskYear is left as it is; typing 2026
   // ran mskYear_Leave -> UpdatePeriodByVerSion, which showed the B8 annex list (run 43551336755, period-inputs-not-matched).
   // Every transfer leaf is in the XML; the import binds text into the locked H149 (fpSpBindDataCell) and control 98 takes the
   // bank name back from maNganHang (GetValueFromSelectedCell). Cell checks read the imported [21]/[34]/[46], the computed [44]
   // and số tiền hoàn trả F145, and the account number in the unlocked O149; Header B37/B38/B55/B59 must pass for the export.
   // The XML checks are the design leaves; tên chủ tài khoản and the bank (texts) are covered by the whole-tree comparison.
   case "02QTT-refund-transfer-Y2025":return new HtkkDeclarationCasePlan(caseId,"B8","2.7.3","952","TncnQtt02TT80Nckt273",new string[]{"101","101_11","B8"},"year","12","2025","","01/2025","12/2025",false,
    new string[]{"02-1/BK-QTT-TNCN"},new string[]{"02|Tờ khai","02-1|02-1/BK-QTT-TNCN"},
    "InterfaceTemplates/excel/02_QTT_TNCN_TT80_273.xls","e1eb77e740803215372e64e58d6c57bd71fc71ba64916ba1a8b4fddabbc95a26","InterfaceTemplates/xml/02_QTT_TNCN_TT80_273.xml","6b2a2c1d27c9298e1fe73b12138ab98e4f722f785e9c253ed91bde3570611f12",
    "Validate/02_QTT_TNCN_TT80_273.xsd","9467d23b5deddd65739532ad470024df2f71af491b7cfc756e24bdd4225983cd",TKhaiThue,TKhaiThueSha256,WorkbookService,130,
    new string[]{"02|M86|300000000","02|M94|2","02|M109|20000000","02|M124|14120000","02|M126|14120000","02|F145|14120000","02|O149|9999000011112"},
    new string[]{Main+"ct21|300000000",Main+"ct24|2",Main+"ct27|79200000",Main+"ct31|88800000",Main+"ct32|5880000",Main+"ct33|20000000",Main+"ct44|14120000",Main+"ct45|14120000",Main+"ct46|14120000",Main+"ct47|0",Main+"ct48|0",
     Main+"TTinHoanThue/soTienHoanTra|14120000",Main+"TTinHoanThue/HinhThucHoanTra/chuyenKhoan|1",Main+"TTinHoanThue/HinhThucHoanTra/tienMat|0",Main+"TTinHoanThue/HinhThucHoanTra/soTaiKhoan|9999000011112"});
   // B8 năm 2026 (HTKK 5.8.2 oracle, non-gating): the two cases above, every month in 2026 (template 2.7.3 has no year
   // branch; same amounts, cell and XML checks). The dialog opens on Now.Year - 1, so mskYear is typed and the annex list that
   // leaves visible is handled by SelectReviewedVisibleAnnexList (VisibleAnnexListReviewed): 02-1 ticked, no KHBS row ticked.
   case "02QTT-dependants-Y2026":return new HtkkDeclarationCasePlan(caseId,"B8","2.7.3","952","TncnQtt02TT80Nckt273",new string[]{"101","101_11","B8"},"year","12","2026","","01/2026","12/2026",false,
    new string[]{"02-1/BK-QTT-TNCN"},new string[]{"02|Tờ khai","02-1|02-1/BK-QTT-TNCN"},
    "InterfaceTemplates/excel/02_QTT_TNCN_TT80_273.xls","e1eb77e740803215372e64e58d6c57bd71fc71ba64916ba1a8b4fddabbc95a26","InterfaceTemplates/xml/02_QTT_TNCN_TT80_273.xml","6b2a2c1d27c9298e1fe73b12138ab98e4f722f785e9c253ed91bde3570611f12",
    "Validate/02_QTT_TNCN_TT80_273.xsd","9467d23b5deddd65739532ad470024df2f71af491b7cfc756e24bdd4225983cd",TKhaiThue,TKhaiThueSha256,WorkbookService,130,
    new string[]{"02|M86|300000000","02|M94|2","02|M109|10000000"},
    new string[]{Main+"ct20|300000000",Main+"ct21|300000000",Main+"ct24|2",Main+"ct27|79200000",Main+"ct34|10000000"});
   case "02QTT-refund-transfer-Y2026":return new HtkkDeclarationCasePlan(caseId,"B8","2.7.3","952","TncnQtt02TT80Nckt273",new string[]{"101","101_11","B8"},"year","12","2026","","01/2026","12/2026",false,
    new string[]{"02-1/BK-QTT-TNCN"},new string[]{"02|Tờ khai","02-1|02-1/BK-QTT-TNCN"},
    "InterfaceTemplates/excel/02_QTT_TNCN_TT80_273.xls","e1eb77e740803215372e64e58d6c57bd71fc71ba64916ba1a8b4fddabbc95a26","InterfaceTemplates/xml/02_QTT_TNCN_TT80_273.xml","6b2a2c1d27c9298e1fe73b12138ab98e4f722f785e9c253ed91bde3570611f12",
    "Validate/02_QTT_TNCN_TT80_273.xsd","9467d23b5deddd65739532ad470024df2f71af491b7cfc756e24bdd4225983cd",TKhaiThue,TKhaiThueSha256,WorkbookService,130,
    new string[]{"02|M86|300000000","02|M94|2","02|M109|20000000","02|M124|14120000","02|M126|14120000","02|F145|14120000","02|O149|9999000011112"},
    new string[]{Main+"ct21|300000000",Main+"ct24|2",Main+"ct27|79200000",Main+"ct31|88800000",Main+"ct32|5880000",Main+"ct33|20000000",Main+"ct44|14120000",Main+"ct45|14120000",Main+"ct46|14120000",Main+"ct47|0",Main+"ct48|0",
     Main+"TTinHoanThue/soTienHoanTra|14120000",Main+"TTinHoanThue/HinhThucHoanTra/chuyenKhoan|1",Main+"TTinHoanThue/HinhThucHoanTra/tienMat|0",Main+"TTinHoanThue/HinhThucHoanTra/soTaiKhoan|9999000011112"});
   // U5 01/CNKD TT50: KieuKy 21 = SetLayoutToKhaiThangQuyLanPhatSinh (quarter), geography panel.
   case "01CNKD-TT50-revenue-two-groups-Q3-2026":return new HtkkDeclarationCasePlan(caseId,"U5","2.9.8","1266","CnkdHkd01TT50Nckt298",new string[]{"101","101_37","U5"},"quarter","21","2026","3","01/07/2026","30/09/2026",false,
    new string[0],new string[]{"01|Tờ khai"},
    "InterfaceTemplates/excel/01_CNKD_HKD_TT50_298.xls","b2afa8514b64ed1a4c9e63ab724a15c0b7fe4dcb5ff77d10277e982381c98ce0","InterfaceTemplates/xml/01_CNKD_HKD_TT50_298.xml","79873aaa4d9dcb31207e9083ffc0f1a72d3cb995d8ee688c198c6871f4e18578",
    "Validate/01_CNKD_HKD_TT50_298.xsd","016f97894b9a1472282ba342349b654b5bfd0f5e4ebba8ab5cbe176134adb31d",TKhaiThue,TKhaiThueSha256,CnkdService,261,
    new string[0],
    new string[]{Main+"KhaiThueGTGTTNCN/SoThueConPhaiNopCT20/soThueGTGT_ct14|10000000",Main+"KhaiThueGTGTTNCN/SoThueConPhaiNopCT20/soThueTNCN_ct17|4500000",Main+"HoTroThongTinNopThue/tongTienCT47|14500000"});
   // U5 01/CNKD TT50 3.1.0 (non-gating, HTKK 5.8.2 oracle only): Menu.xml 5.8.2 VersionXML 3.1.0, class
   // CnkdHkd01TT50Nckt310. The period dialog ticks "PL 01 43/2026/QH16" (sheet 01-4; frmHTKKPeriod.LoadPhuLucSpread locks
   // PL 01/PL 03 outside kỳ quý, btnDongY_Click refuses both with 0709). Three groups (rows 291-293: 01 and 04 ticked, 02 clear last), PL 01 rows 20-21.
   // chonGiamThue (AJ) and soThueGiam (CD) are not in the XML: after "Nhập từ XML" AJ is clear, CD = 0 and AE = CE
   // (runs 43127371885, 43130173107: cell mask 40 = AE291/AE293). The case therefore runs in mode
   // web-xml-import-tick-reexport (HtkkDeclarationCasePlans.ImportTick): the sheet checks below (AE, CD, PL 01 G/H)
   // are read AFTER the original ticks of AJ291/AJ292, when HTKK itself has rebuilt PL 01 and CD.
   // Run 43138236726 (rows 01, 02, 04): mask 4128 = AE293/CD293. HTKK 5.8.2 daySangPLGiamThue never advances its row
   // counter after an unticked row (0x0321 set CD := 0, 0x0327 br to 0x04a2 past the increment at 0x049b), so a ticked
   // row after an unticked one keeps CD = 0 while PL 01 lists it. The case now puts the ticked rows first (01, 04, 02).
   case "01CNKD-TT50-310-pl01-three-groups-Q3-2026":return new HtkkDeclarationCasePlan(caseId,"U5","3.1.0","1266","CnkdHkd01TT50Nckt310",new string[]{"101","101_37","U5"},"quarter","21","2026","3","01/07/2026","30/09/2026",false,
    new string[]{"PL 01 43/2026/QH16"},new string[]{"01|Tờ khai","01-4|PL 01 43/2026/QH16"},
    "InterfaceTemplates/excel/01_CNKD_HKD_TT50_310.xls","864ef2c1c28f4f0c807265fa2497264ec72283912dda1f3f6294b6b9aa8a3c56","InterfaceTemplates/xml/01_CNKD_HKD_TT50_310.xml","30f4d3162d6179ce8c233c977898b86f63756e741bda1a423c15e45babea0d86",
    "Validate/01_CNKD_HKD_TT50_310.xsd","c55ba118b03c859ed20f6bcf2cadfde89c2450a9869b00a36e075af917f75aff",TKhaiThue,TKhaiThueSha256,CnkdService,299,
    new string[]{"01|U291|300000000","01|U292|200000000","01|U293|150000000","01|AE291|1050000","01|AE292|2100000","01|AE293|3000000","01-4|G20|1500000","01-4|H20|450000","01-4|G21|3000000","01-4|H21|900000","01|CD291|450000","01|CD292|900000","01|CD293|0"},
    new string[]{Main+"KhaiThueGTGTTNCN/SoThueConPhaiNopCT20/soThueGTGT_ct14|16000000",Main+"KhaiThueGTGTTNCN/SoThueConPhaiNopCT20/soThueTNCN_ct17|6150000",Main+"HoTroThongTinNopThue/tongTienCT47|22150000",
     "HSoThueDTu/HSoKhaiThue/PLuc/PLuc_01_GiamTNCN_NQ43/TongCong/tongSoThueTNCN_phaiNop|1350000","HSoThueDTu/HSoKhaiThue/PLuc/PLuc_01_GiamTNCN_NQ43/TongCong/tongsoThueTNCN_duocGiam|4500000"});
   // U5 3.1.0 with PL 03 of NQ 43/2026/QH16 (Mẫu 03, thuế phải nộp bù; non-gating, HTKK 5.8.2 only). The period dialog ticks
   // "PL 03 43/2026/QH16" (sheet 01-5). Two industry rows (291 group 01, 292 group 04, location 00001, header (1)); PL 03 mục A
   // ONE row 22 (group 04, 300.000, H = G by XLS H22), mục B its default row 26. One row per section on purpose: HTKK 5.8.2
   // cannot export two (run 43162952097, 0279 = its own XSD check in WinDoWorkExportXML): the XLS mst_diaDiemKD formula
   // N22 = E8 is relative, InsertTableRow copies row 22 by SheetView.CopyRange, so row 23 gets N23 = E9 (empty), and
   // ExportDataTableToTableNode writes an empty TINType (not nillable). The PL 03 rows are in the XML; the thuế bù CF
   // (ct17_soThueBu) of the industry rows is grid-only: CnkdHkd01TT50Nckt310.capNhatToKhai (pinned u5-310-tick-capnhat)
   // writes it, called from CellChange_0 / CellChange_4 / ButtonClick_0 only, and reads the child-row key BN that only
   // SetCacDongCon fills. So the case runs in mode web-xml-import-tick-reexport with edits only (ImportTick): one original
   // edit of L291 (0, then the web value). capNhatToKhai with (1): CF = H of the FIRST mục A row with D = BN and K = BM
   // (row 291 group 01 finds none: CF 0; row 292 group 04: CF 300.000);
   // mục B only on the head office by group (default row: no group). Its string compares (op_Equality, 0x0400/0x040b) and
   // the skip of a row without BN/BM (0x02fd, no index advance) are not reached: every row has code and group.
   case "01CNKD-TT50-310-pl03-two-groups-Q3-2026":return new HtkkDeclarationCasePlan(caseId,"U5","3.1.0","1266","CnkdHkd01TT50Nckt310",new string[]{"101","101_37","U5"},"quarter","21","2026","3","01/07/2026","30/09/2026",false,
    new string[]{"PL 03 43/2026/QH16"},new string[]{"01|Tờ khai","01-5|PL 03 43/2026/QH16"},
    "InterfaceTemplates/excel/01_CNKD_HKD_TT50_310.xls","864ef2c1c28f4f0c807265fa2497264ec72283912dda1f3f6294b6b9aa8a3c56","InterfaceTemplates/xml/01_CNKD_HKD_TT50_310.xml","30f4d3162d6179ce8c233c977898b86f63756e741bda1a423c15e45babea0d86",
    "Validate/01_CNKD_HKD_TT50_310.xsd","c55ba118b03c859ed20f6bcf2cadfde89c2450a9869b00a36e075af917f75aff",TKhaiThue,TKhaiThueSha256,CnkdService,285,
    new string[]{"01|U291|300000000","01|U292|200000000","01|CF291|0","01|CF292|300000","01|CD291|0","01|CD292|0","01|AE291|1500000","01|AE292|3300000","01-5|G22|300000","01-5|H22|300000"},
    new string[]{Main+"KhaiThueGTGTTNCN/SoThueConPhaiNopCT20/soThueGTGT_ct14|9000000",Main+"KhaiThueGTGTTNCN/SoThueConPhaiNopCT20/soThueTNCN_ct17|4800000",Main+"HoTroThongTinNopThue/tongTienCT47|13800000",
     "HSoThueDTu/HSoKhaiThue/PLuc/PLuc_03_PhaiNop_NQ43/TongCong/tongSoThueTNCN_phaiNop|300000","HSoThueDTu/HSoKhaiThue/PLuc/PLuc_03_PhaiNop_NQ43/TongCong/tongsoThueTNCN_duocGiam|300000"});
   // I9 01/NTNN TT80 (non-gating): KieuKy 18 = SetLayoutToKhaiThangLanPhatSinh (frmHTKKPeriod_Load
   // 0x6000484 -> index 21; chkTkhaiThang checked by default), month 09/2026; no annex. CheckPeriod ->
   // CheckHLToKhaiTT80 only refuses months before 01/2022 (0577). HTKK 5.8.2 adds I9 to
   // GeneralFunctions.CheckToKhaiHetHieuLuc with Menu.xml EndDate 30/09/2026 (months after 09/2026 refused),
   // so the case moved from M10/2026 (release 238, run 42348087003) to M09/2026, valid on both oracles. Two contractor
   // rows of BKThueNTNN/ThueNTNN (template row 55): imported rows 55-56, totals row 58. Sheet checks are
   // the XLS row formulas AV=ROUND(AJ*AN/100), BN=MAX(0,ROUND(AZ*BD/100)-BH), BR=AV+BN; XML checks = the
   // design oracle's totals (mapping 01_NTNN_TT80_251.xml Y_57..BR_57).
   case "01NTNN-two-contractors-M09-2026":return new HtkkDeclarationCasePlan(caseId,"I9","2.5.1","838","Ntnn01TT80Nckt251",new string[]{"101","101_8","I9"},"month","18","2026","09","01/09/2026","30/09/2026",false,
    new string[0],new string[]{"01|Tờ khai"},
    "InterfaceTemplates/excel/01_NTNN_TT80_251.xls","feebf2a918138aad860b52fb409232716027dc7ba59ec8aed861714d7e7de652","InterfaceTemplates/xml/01_NTNN_TT80_251.xml","cb8f1c83df2ebb590e314b2ca71fde4751760906e57df666e92086d6a1f9983c",
    "Validate/01_NTNN_TT80_251.xsd","aa17404343424b1d3bf429d7279d7ea1c4a858f8509c087be9c4dc9db6b192da",TKhaiThue,TKhaiThueSha256,WorkbookService,74,
    new string[]{"01|AV55|50000000","01|BN55|50000000","01|BR55|100000000","01|AV56|15000000","01|BN56|8000000","01|BR56|23000000","01|AV58|65000000","01|BN58|58000000","01|BR58|123000000"},
    new string[]{Main+"tong_ct5|1500000000",Main+"tong_ct7|1500000000",Main+"tong_ct9|65000000",Main+"tong_ct10|1500000000",Main+"tong_ct12|2000000",Main+"tong_ct13|58000000",Main+"tong_ct14|123000000"});
   // J1 03/NTNN 3.0.8 (non-gating): KieuKy 18 like I9 (month 10/2026, no annex; J1 is in the
   // CheckHLToKhaiTT80 list, months from 01/2022). One ThueNTNN table (template row 34, BKThueNTNN):
   // imported rows 34-35, totals row 37. Ntnn03TT80Nckt308.FinishImportXML (0x6001937) then sets each
   // BU := getThuSuatByMa(CR, "DC_97") = "" (CR/pathTLTNDN never in the XML); the design rate is 0, so
   // the rewrite is a no-op. Sheet checks: CG = IF(BK*BU/100-BX<0,0,ROUND(..)) = 0 and the totals of
   // AU/BK/CG (mapping 03_NTNN_TT80_308.xml AU_36..CG_36); XML checks = the design oracle totals.
   case "03NTNN-no-rate-M10-2026":return new HtkkDeclarationCasePlan(caseId,"J1","3.0.8","840","Ntnn03TT80Nckt308",new string[]{"101","101_8","J1"},"month","18","2026","10","01/10/2026","31/10/2026",false,
    new string[0],new string[]{"01|Tờ khai"},
    "InterfaceTemplates/excel/03_NTNN_TT80_308.xls","ef4451f19a8a74ad667add7fd580ac83be149f7d35e65bbbe12aa42ccad11142","InterfaceTemplates/xml/03_NTNN_TT80_308.xml","41c8c6c92a684485aff87790739958948c94bf966cc5e56b6150a17f6beac550",
    "Validate/03_NTNN_TT80_308.xsd","97eaf67183cba1723fa00db46565598568288763185a503daf255b091eedb0b7",TKhaiThue,TKhaiThueSha256,WorkbookService,65,
    new string[]{"01|CG34|0","01|CG35|0","01|AU37|1100000000","01|BK37|1100000000","01|BX37|0","01|CG37|0"},
    new string[]{Main+"tongct6|1100000000",Main+"tongct8|1100000000",Main+"tongct10|0",Main+"tongct11|0"});
   // Y8 01/NTNN, NCCNN TT89 (non-gating, mode original-entry-export): KieuKy 18 like I9 (month 10/2026; Menu.xml
   // validity from 01/10/2026). Part II chosen (nopThayNCCNN M8; ButtonClick_0 keeps M6 false), ThueNTNN (row
   // 60) locked with its template row, ThueNCCNN row 78 (total 80), ThueCNKCT row 86 (total 88, TNCN). The rows are
   // TYPED into HTKK's own grid (HtkkDeclarationCasePlans.Entry): release 238 (run 42348089716) showed that the
   // original import resets the three tables (cmdImportXML_Click -> ... -> ProcessSheet -> AutoBindData_0 ->
   // LockUnlock -> GeneralFunctions.LockUnLockColsInTable deleteData=true), so the import-based case
   // 01NTNN-NCCNN-two-parts-M10-2026 was removed. Release 242 (run 42359742133): full match, 103 leaves.
   // XML checks: mapping 01_NTNN_NCCNN_TT89_309.xml M_6/M_8, Y_88..BR_88 mucII_tong_*.
   // Sheet checks after entry: the XLS row formulas (AV/BN/BR 78 and 86) and the table totals of rows
   // 80/88 (Y/AV/BN/BR = SUM over the table), recomputed independently by NTNN_ROWS; BR62 = 0 (part I locked).
   case "01NTNN-NCCNN-entry-M10-2026":return new HtkkDeclarationCasePlan(caseId,"Y8","3.0.9","2012","Ntnn01TT89Nckt309",new string[]{"101","101_8","Y8"},"month","18","2026","10","01/10/2026","31/10/2026",false,
    new string[0],new string[]{"01|Tờ khai"},
    "InterfaceTemplates/excel/01_NTNN_NCCNN_TT89_309.xls","53630634bd02cc412ddde0682c2557226547737fceed792f595709a2fd0eafe1","InterfaceTemplates/xml/01_NTNN_NCCNN_TT89_309.xml","5c43131df4ecf265ddf9c780174416f95a249d82bd666339a97f0ea852f105d9",
    "Validate/01_NTNN_NCCNN_TT89_309.xsd","7e417697b602867a819c80f59eaaae486ceb9148ab58867187206be5f75df1b8",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,107,
    new string[]{"01|AV78|10000000","01|BN78|10000000","01|BR78|20000000","01|Y80|200000000","01|AV80|10000000","01|BN80|10000000","01|BR80|20000000","01|AV86|5000000","01|BN86|2000000","01|BR86|7000000","01|Y88|100000000","01|AV88|5000000","01|BN88|2000000","01|BR88|7000000","01|BR62|0"},
    new string[]{Main+"nopThayNTNN|0",Main+"nopThayNCCNN|1",Main+"ThueNCCNN_CNKCT/mucII_tong_ct5|100000000",Main+"ThueNCCNN_CNKCT/mucII_tong_ct7|100000000",Main+"ThueNCCNN_CNKCT/mucII_tong_ct9|5000000",Main+"ThueNCCNN_CNKCT/mucII_tong_ct10|100000000",Main+"ThueNCCNN_CNKCT/mucII_tong_ct12|0",Main+"ThueNCCNN_CNKCT/mucII_tong_ct13|2000000",Main+"ThueNCCNN_CNKCT/mucII_tong_ct14|7000000"});
   // HTKK 5.8.5 (htkkVersion 5.8.5, original entry): the plan of the entry case; Entry() types both (4) ngày hợp đồng as 31/12/2027, after any run
   // day. Ntnn01TT89Nckt309.checkTKChinh 5.8.5 no longer tests a given W (5.8.4: E_33 format, E_36 "Ngày Hợp đồng phải nhỏ hơn ngày
   // hiện tại"); the sheet and XML checks are those of the entry case (W enters no formula).
   case "01NTNN-NCCNN-entry-future-contract-M10-2026":return new HtkkDeclarationCasePlan(caseId,"Y8","3.0.9","2012","Ntnn01TT89Nckt309",new string[]{"101","101_8","Y8"},"month","18","2026","10","01/10/2026","31/10/2026",false,
    new string[0],new string[]{"01|Tờ khai"},
    "InterfaceTemplates/excel/01_NTNN_NCCNN_TT89_309.xls","53630634bd02cc412ddde0682c2557226547737fceed792f595709a2fd0eafe1","InterfaceTemplates/xml/01_NTNN_NCCNN_TT89_309.xml","5c43131df4ecf265ddf9c780174416f95a249d82bd666339a97f0ea852f105d9",
    "Validate/01_NTNN_NCCNN_TT89_309.xsd","7e417697b602867a819c80f59eaaae486ceb9148ab58867187206be5f75df1b8",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,107,
    new string[]{"01|AV78|10000000","01|BN78|10000000","01|BR78|20000000","01|Y80|200000000","01|AV80|10000000","01|BN80|10000000","01|BR80|20000000","01|AV86|5000000","01|BN86|2000000","01|BR86|7000000","01|Y88|100000000","01|AV88|5000000","01|BN88|2000000","01|BR88|7000000","01|BR62|0"},
    new string[]{Main+"nopThayNTNN|0",Main+"nopThayNCCNN|1",Main+"ThueNCCNN_CNKCT/mucII_tong_ct5|100000000",Main+"ThueNCCNN_CNKCT/mucII_tong_ct7|100000000",Main+"ThueNCCNN_CNKCT/mucII_tong_ct9|5000000",Main+"ThueNCCNN_CNKCT/mucII_tong_ct10|100000000",Main+"ThueNCCNN_CNKCT/mucII_tong_ct12|0",Main+"ThueNCCNN_CNKCT/mucII_tong_ct13|2000000",Main+"ThueNCCNN_CNKCT/mucII_tong_ct14|7000000"});
   // HTKK 5.8.3 Y8 (htkkVersion 5.8.3, original entry): only II-I (ThueNCCNN) or only II-II (ThueCNKCT) is typed; checkTKChinh skips
   // the empty part II table when the other has data (5.8.2 required both). The empty table's sheet cells and XML totals are 0.
   case "01NTNN-NCCNN-entry-part-II1-M10-2026":return new HtkkDeclarationCasePlan(caseId,"Y8","3.0.9","2012","Ntnn01TT89Nckt309",new string[]{"101","101_8","Y8"},"month","18","2026","10","01/10/2026","31/10/2026",false,
    new string[0],new string[]{"01|Tờ khai"},
    "InterfaceTemplates/excel/01_NTNN_NCCNN_TT89_309.xls","53630634bd02cc412ddde0682c2557226547737fceed792f595709a2fd0eafe1","InterfaceTemplates/xml/01_NTNN_NCCNN_TT89_309.xml","5c43131df4ecf265ddf9c780174416f95a249d82bd666339a97f0ea852f105d9",
    "Validate/01_NTNN_NCCNN_TT89_309.xsd","7e417697b602867a819c80f59eaaae486ceb9148ab58867187206be5f75df1b8",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,107,
    new string[]{"01|AV78|10000000","01|BN78|10000000","01|BR78|20000000","01|Y80|200000000","01|AV80|10000000","01|BN80|10000000","01|BR80|20000000","01|AV86|0","01|BN86|0","01|BR86|0","01|Y88|0","01|AV88|0","01|BN88|0","01|BR88|0","01|BR62|0"},
    new string[]{Main+"nopThayNTNN|0",Main+"nopThayNCCNN|1",Main+"ThueNCCNN_CNKCT/mucII_tong_ct5|0",Main+"ThueNCCNN_CNKCT/mucII_tong_ct7|0",Main+"ThueNCCNN_CNKCT/mucII_tong_ct9|0",Main+"ThueNCCNN_CNKCT/mucII_tong_ct10|0",Main+"ThueNCCNN_CNKCT/mucII_tong_ct12|0",Main+"ThueNCCNN_CNKCT/mucII_tong_ct13|0",Main+"ThueNCCNN_CNKCT/mucII_tong_ct14|0"});
   case "01NTNN-NCCNN-entry-part-II2-M10-2026":return new HtkkDeclarationCasePlan(caseId,"Y8","3.0.9","2012","Ntnn01TT89Nckt309",new string[]{"101","101_8","Y8"},"month","18","2026","10","01/10/2026","31/10/2026",false,
    new string[0],new string[]{"01|Tờ khai"},
    "InterfaceTemplates/excel/01_NTNN_NCCNN_TT89_309.xls","53630634bd02cc412ddde0682c2557226547737fceed792f595709a2fd0eafe1","InterfaceTemplates/xml/01_NTNN_NCCNN_TT89_309.xml","5c43131df4ecf265ddf9c780174416f95a249d82bd666339a97f0ea852f105d9",
    "Validate/01_NTNN_NCCNN_TT89_309.xsd","7e417697b602867a819c80f59eaaae486ceb9148ab58867187206be5f75df1b8",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,107,
    new string[]{"01|AV78|0","01|BN78|0","01|BR78|0","01|Y80|0","01|AV80|0","01|BN80|0","01|BR80|0","01|AV86|5000000","01|BN86|2000000","01|BR86|7000000","01|Y88|100000000","01|AV88|5000000","01|BN88|2000000","01|BR88|7000000","01|BR62|0"},
    new string[]{Main+"nopThayNTNN|0",Main+"nopThayNCCNN|1",Main+"ThueNCCNN_CNKCT/mucII_tong_ct5|100000000",Main+"ThueNCCNN_CNKCT/mucII_tong_ct7|100000000",Main+"ThueNCCNN_CNKCT/mucII_tong_ct9|5000000",Main+"ThueNCCNN_CNKCT/mucII_tong_ct10|100000000",Main+"ThueNCCNN_CNKCT/mucII_tong_ct12|0",Main+"ThueNCCNN_CNKCT/mucII_tong_ct13|2000000",Main+"ThueNCCNN_CNKCT/mucII_tong_ct14|7000000"});
   // Kỳ lần phát sinh (KieuKy 18, non-gating). frmHTKKPeriod_Load -> SetLayoutToKhaiThangLanPhatSinh (0x60004a9): Tháng
   // ticked by default, Lần phát sinh offered; ticking chkTKLanPS (CheckedChanged 0x60004b2 -> ResetpnVT1_2NgayThangQuyNam
   // 0x60004b1 case 6) shows pnNgay/pnThang/pnNam with today's date (LoadDefaultInfor). The driver types the day into
   // mskDay/mskMonth/mskYear only (mskTuNgay/mskDenNgay stay hidden and untouched). After Đồng ý, GetPeriodInfo gives
   // KieuKy D, Ngay/Thang/Nam, TuNgay = DenNgay = kyKKhai = 20/10/2026 (DeclarationIdentity checks all of them).
   // CheckPeriod: CheckNgayThangNam, D after today -> 0223, CheckHLToKhaiTT80 D (I9/J1 in the TT80 list) before 01/01/2022
   // -> 0576, CheckHieuLuc before the Menu.xml StartDate (Y8 01/10/2026) -> 0441; 20/10/2026 (Y8, J1) and 20/09/2026 (I9) pass all of them.
   // I9/J1: AutoBindData_0 (0x60018ef / 0x6001931) writes kyKKhai into (6) AE / (7) BE of every row bound at load and
   // locks it; the web XML carries that day already (ct6 / ct7 = 2026-10-20), so the import changes nothing there.
   // Sheet and XML checks as the monthly cases (same rows; the period does not enter the row formulas).
   // I9 uses 20/09/2026: HTKK 5.8.2 CheckToKhaiHetHieuLuc refuses an I9 day period after 30/09/2026 (DenNgay > EndDate).
   case "01NTNN-occurrence-D20-09-2026":return new HtkkDeclarationCasePlan(caseId,"I9","2.5.1","838","Ntnn01TT80Nckt251",new string[]{"101","101_8","I9"},"day","18","2026","","20/09/2026","20/09/2026",false,
    new string[0],new string[]{"01|Tờ khai"},
    "InterfaceTemplates/excel/01_NTNN_TT80_251.xls","feebf2a918138aad860b52fb409232716027dc7ba59ec8aed861714d7e7de652","InterfaceTemplates/xml/01_NTNN_TT80_251.xml","cb8f1c83df2ebb590e314b2ca71fde4751760906e57df666e92086d6a1f9983c",
    "Validate/01_NTNN_TT80_251.xsd","aa17404343424b1d3bf429d7279d7ea1c4a858f8509c087be9c4dc9db6b192da",TKhaiThue,TKhaiThueSha256,WorkbookService,74,
    new string[]{"01|AV55|50000000","01|BN55|50000000","01|BR55|100000000","01|AV56|15000000","01|BN56|8000000","01|BR56|23000000","01|AV58|65000000","01|BN58|58000000","01|BR58|123000000"},
    new string[]{Main+"tong_ct5|1500000000",Main+"tong_ct7|1500000000",Main+"tong_ct9|65000000",Main+"tong_ct10|1500000000",Main+"tong_ct12|2000000",Main+"tong_ct13|58000000",Main+"tong_ct14|123000000"});
   // Y8 (original entry): Ntnn01TT89Nckt309.AutoBindData_0 (0x60018f9) writes the day into ThueNTNN AE and then runs
   // LockUnlock, whose LockUnLockColsInTable(deleteData=true) resets AE of every table, so AE is typed as in the monthly
   // entry case; checkTKChinh E_27 (TuNgay <= AE <= DenNgay) makes it the period day: the entry plan types 20/10/2026.
   case "01NTNN-NCCNN-occurrence-D20-10-2026":return new HtkkDeclarationCasePlan(caseId,"Y8","3.0.9","2012","Ntnn01TT89Nckt309",new string[]{"101","101_8","Y8"},"day","18","2026","","20/10/2026","20/10/2026",false,
    new string[0],new string[]{"01|Tờ khai"},
    "InterfaceTemplates/excel/01_NTNN_NCCNN_TT89_309.xls","53630634bd02cc412ddde0682c2557226547737fceed792f595709a2fd0eafe1","InterfaceTemplates/xml/01_NTNN_NCCNN_TT89_309.xml","5c43131df4ecf265ddf9c780174416f95a249d82bd666339a97f0ea852f105d9",
    "Validate/01_NTNN_NCCNN_TT89_309.xsd","7e417697b602867a819c80f59eaaae486ceb9148ab58867187206be5f75df1b8",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,107,
    new string[]{"01|AV78|10000000","01|BN78|10000000","01|BR78|20000000","01|Y80|200000000","01|AV80|10000000","01|BN80|10000000","01|BR80|20000000","01|AV86|5000000","01|BN86|2000000","01|BR86|7000000","01|Y88|100000000","01|AV88|5000000","01|BN88|2000000","01|BR88|7000000","01|BR62|0"},
    new string[]{Main+"nopThayNTNN|0",Main+"nopThayNCCNN|1",Main+"ThueNCCNN_CNKCT/mucII_tong_ct5|100000000",Main+"ThueNCCNN_CNKCT/mucII_tong_ct7|100000000",Main+"ThueNCCNN_CNKCT/mucII_tong_ct9|5000000",Main+"ThueNCCNN_CNKCT/mucII_tong_ct10|100000000",Main+"ThueNCCNN_CNKCT/mucII_tong_ct12|0",Main+"ThueNCCNN_CNKCT/mucII_tong_ct13|2000000",Main+"ThueNCCNN_CNKCT/mucII_tong_ct14|7000000"});
   // J1: rate [9] = 0 as in 03NTNN-no-rate-M10-2026 (FinishImportXML clears every imported rate). (7) BE is the day here,
   // so the run also observes checkTKChinh's ValidateFullDate(BE text, "ddMMyyyy") on a non-empty BE (E_18 open point).
   case "03NTNN-occurrence-D20-10-2026":return new HtkkDeclarationCasePlan(caseId,"J1","3.0.8","840","Ntnn03TT80Nckt308",new string[]{"101","101_8","J1"},"day","18","2026","","20/10/2026","20/10/2026",false,
    new string[0],new string[]{"01|Tờ khai"},
    "InterfaceTemplates/excel/03_NTNN_TT80_308.xls","ef4451f19a8a74ad667add7fd580ac83be149f7d35e65bbbe12aa42ccad11142","InterfaceTemplates/xml/03_NTNN_TT80_308.xml","41c8c6c92a684485aff87790739958948c94bf966cc5e56b6150a17f6beac550",
    "Validate/03_NTNN_TT80_308.xsd","97eaf67183cba1723fa00db46565598568288763185a503daf255b091eedb0b7",TKhaiThue,TKhaiThueSha256,WorkbookService,65,
    new string[]{"01|CG34|0","01|CG35|0","01|AU37|1100000000","01|BK37|1100000000","01|BX37|0","01|CG37|0"},
    new string[]{Main+"tongct6|1100000000",Main+"tongct8|1100000000",Main+"tongct10|0",Main+"tongct11|0"});
   // D6/Y1 04/NTNN quyết toán (non-gating, mode web-xml-import-reexport): Menu.xml KieuKy 22 -> frmHTKKPeriod
   // SetLayoutToKhaiTuNgayDenNgay (0x60004ae): no month/quarter/year box, only mskTuNgay/mskDenNgay and the visible
   // annex list. GetPeriodInfo (0x60004e2, branch 80/82/C9/D6/X9/Y1) sets KieuKy "D_D", Nam = year of mskDenNgay,
   // TuNgay/DenNgay = the two texts; xmlExportTTinChung (0x6000049) writes kieuKy "Y" for KieuKy 22. Menu.xml sheet
   // "01-1" (SheetName "02-2/NTNN") is the workbook's second sheet "01-2" (GetHTKKSheetInfo 0x60000f0, by position);
   // the menus are not in the AddFullPLImportXML list, so the period dialog ticks "02-2/NTNN". Neither class has
   // FinishImportXML; AutoBindData_0 writes only the settlement case (07) and Refresh_1 sets AB32/AB33 = the annex
   // totals BD32/BD33, which the case already carries. Sheet checks: XLS rows 32-39 and annex totals (one row, no
   // insertion: D6 01-2 BD26/BS26, Y1 01-2 BI51/BX51); XML checks = the Decimal oracle NTNN04 (htkk_declaration_web_cases).
   case "04NTNN-TT80-one-subcontractor-2026":return new HtkkDeclarationCasePlan(caseId,"D6","3.0.8","922","Ntnn04TT80Nckt308",new string[]{"101","101_8","D6"},"range","22","2026","","01/01/2026","30/09/2026",false,
    new string[]{"02-2/NTNN"},new string[]{"01|Tờ khai","01-2|02-2/NTNN"},
    "InterfaceTemplates/excel/04_NTNN_TT80_308.xls","38ce07db1cd2573d283ca9102edb7684e08c39aa718563016e42817cb6254415","InterfaceTemplates/xml/04_NTNN_TT80_308.xml","24a42a0529777cfdbf6946a220dee1c57ce18f817297c4ee1b77536fe3352d6b",
    "Validate/04_NTNN_TT80_308.xsd","f9a3d4b5355d16490adf8c014b62fb49260fc75a438d9bf1131ee5a4166cf25e",TKhaiThue,TKhaiThueSha256,WorkbookService,79,
    new string[]{"01|AB32|2500000000","01|AB33|2400000000","01|AJ32|0","01|T35|2400000000","01|AB35|2000000000","01|AJ35|-400000000","01|AJ36|4000000","01|AB38|4000000","01|AB39|0","01-2|BD26|2500000000","01-2|BS26|2400000000"},
    new string[]{Main+"GiaTriHDong/keKhai|2500000000",Main+"GiaTriHDong/quyetToan|2500000000",Main+"GiaTriHDong/chenhLech|0",Main+"DThuChuaGomGTGT/quyetToan|2400000000",Main+"DThuNTPhu/quyetToan|400000000",Main+"DThuTinhThue/keKhai|2400000000",Main+"DThuTinhThue/quyetToan|2000000000",Main+"SoThueTNDNPNop/chenhLech|4000000",Main+"SoThueDaNop/quyetToan|96000000",Main+"SoThueConPNop/quyetToan|4000000",Main+"SoThueNopThua/quyetToan|0","HSoThueDTu/HSoKhaiThue/PLuc/PL02_2_NTNN/tong_ct9|2500000000","HSoThueDTu/HSoKhaiThue/PLuc/PL02_2_NTNN/tong_ct10|2400000000"});
   // HTKK 5.8.3 (htkkVersion 5.8.3): D6 accepts đến ngày up to 06/10/2026 (0719).
   case "04NTNN-TT80-one-subcontractor-to-06-10-2026":return new HtkkDeclarationCasePlan(caseId,"D6","3.0.8","922","Ntnn04TT80Nckt308",new string[]{"101","101_8","D6"},"range","22","2026","","01/01/2026","06/10/2026",false,
    new string[]{"02-2/NTNN"},new string[]{"01|Tờ khai","01-2|02-2/NTNN"},
    "InterfaceTemplates/excel/04_NTNN_TT80_308.xls","38ce07db1cd2573d283ca9102edb7684e08c39aa718563016e42817cb6254415","InterfaceTemplates/xml/04_NTNN_TT80_308.xml","24a42a0529777cfdbf6946a220dee1c57ce18f817297c4ee1b77536fe3352d6b",
    "Validate/04_NTNN_TT80_308.xsd","f9a3d4b5355d16490adf8c014b62fb49260fc75a438d9bf1131ee5a4166cf25e",TKhaiThue,TKhaiThueSha256,WorkbookService,79,
    new string[]{"01|AB32|2500000000","01|AB33|2400000000","01|AJ32|0","01|T35|2400000000","01|AB35|2000000000","01|AJ35|-400000000","01|AJ36|4000000","01|AB38|4000000","01|AB39|0","01-2|BD26|2500000000","01-2|BS26|2400000000"},
    new string[]{Main+"GiaTriHDong/keKhai|2500000000",Main+"GiaTriHDong/quyetToan|2500000000",Main+"GiaTriHDong/chenhLech|0",Main+"DThuChuaGomGTGT/quyetToan|2400000000",Main+"DThuNTPhu/quyetToan|400000000",Main+"DThuTinhThue/keKhai|2400000000",Main+"DThuTinhThue/quyetToan|2000000000",Main+"SoThueTNDNPNop/chenhLech|4000000",Main+"SoThueDaNop/quyetToan|96000000",Main+"SoThueConPNop/quyetToan|4000000",Main+"SoThueNopThua/quyetToan|0","HSoThueDTu/HSoKhaiThue/PLuc/PL02_2_NTNN/tong_ct9|2500000000","HSoThueDTu/HSoKhaiThue/PLuc/PL02_2_NTNN/tong_ct10|2400000000"});
   case "04NTNN-TT89-one-subcontractor-2026":return new HtkkDeclarationCasePlan(caseId,"Y1","3.0.9","2015","Ntnn04TT89Nckt309",new string[]{"101","101_8","Y1"},"range","22","2026","","01/07/2026","30/09/2026",false,
    new string[]{"02-2/NTNN"},new string[]{"01|Tờ khai","01-2|02-2/NTNN"},
    "InterfaceTemplates/excel/04_NTNN_TT89_309.xls","3326d1ab92a20a1b5d52aa00cb32610584ef2fee4e2a86b73efa5bf4e093ca61","InterfaceTemplates/xml/04_NTNN_TT89_309.xml","c8555e3dbc3a2bbf0b5ac98a3d8f225c8fc2fc5dc0970475e8df06506802bee8",
    "Validate/04_NTNN_TT89_309.xsd","eaa0ab3ed35eed6ff0a2dd33cf2bd5dba8c179cd65169cc869ca46f1c03ea591",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,79,
    new string[]{"01|AB32|2000000000","01|AB33|1800000000","01|AJ32|0","01|T35|1800000000","01|AB35|1500000000","01|AJ35|-300000000","01|AJ36|3000000","01|AB38|3000000","01|AB39|0","01-2|BI51|2000000000","01-2|BX51|1800000000"},
    new string[]{Main+"GiaTriHDong/keKhai|2000000000",Main+"GiaTriHDong/quyetToan|2000000000",Main+"GiaTriHDong/chenhLech|0",Main+"DThuTinhThue/quyetToan|1800000000",Main+"DThuNTPhu/quyetToan|300000000",Main+"DThuTinhThueNTNN/keKhai|1800000000",Main+"DThuTinhThueNTNN/quyetToan|1500000000",Main+"SoThueTNDNPNop/chenhLech|3000000",Main+"SoThueDaNop/quyetToan|72000000",Main+"SoThueConPNop/quyetToan|3000000",Main+"SoThueNopThua/quyetToan|0","HSoThueDTu/HSoKhaiThue/PLuc/PL02_2_NTNN/tong_ct9|2000000000","HSoThueDTu/HSoKhaiThue/PLuc/PL02_2_NTNN/tong_ct10|1800000000"});
   // HTKK 5.8.3 (htkkVersion 5.8.3): CheckHLToKhaiTT80 refuses a TT89 quyết toán whose đến ngày is before 07/10/2026 (0718);
   // the same contract with đến ngày 07/10/2026, the first accepted day.
   case "04NTNN-TT89-one-subcontractor-to-07-10-2026":return new HtkkDeclarationCasePlan(caseId,"Y1","3.0.9","2015","Ntnn04TT89Nckt309",new string[]{"101","101_8","Y1"},"range","22","2026","","01/07/2026","07/10/2026",false,
    new string[]{"02-2/NTNN"},new string[]{"01|Tờ khai","01-2|02-2/NTNN"},
    "InterfaceTemplates/excel/04_NTNN_TT89_309.xls","3326d1ab92a20a1b5d52aa00cb32610584ef2fee4e2a86b73efa5bf4e093ca61","InterfaceTemplates/xml/04_NTNN_TT89_309.xml","c8555e3dbc3a2bbf0b5ac98a3d8f225c8fc2fc5dc0970475e8df06506802bee8",
    "Validate/04_NTNN_TT89_309.xsd","eaa0ab3ed35eed6ff0a2dd33cf2bd5dba8c179cd65169cc869ca46f1c03ea591",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,79,
    new string[]{"01|AB32|2000000000","01|AB33|1800000000","01|AJ32|0","01|T35|1800000000","01|AB35|1500000000","01|AJ35|-300000000","01|AJ36|3000000","01|AB38|3000000","01|AB39|0","01-2|BI51|2000000000","01-2|BX51|1800000000"},
    new string[]{Main+"GiaTriHDong/keKhai|2000000000",Main+"GiaTriHDong/quyetToan|2000000000",Main+"GiaTriHDong/chenhLech|0",Main+"DThuTinhThue/quyetToan|1800000000",Main+"DThuNTPhu/quyetToan|300000000",Main+"DThuTinhThueNTNN/keKhai|1800000000",Main+"DThuTinhThueNTNN/quyetToan|1500000000",Main+"SoThueTNDNPNop/chenhLech|3000000",Main+"SoThueDaNop/quyetToan|72000000",Main+"SoThueConPNop/quyetToan|3000000",Main+"SoThueNopThua/quyetToan|0","HSoThueDTu/HSoKhaiThue/PLuc/PL02_2_NTNN/tong_ct9|2000000000","HSoThueDTu/HSoKhaiThue/PLuc/PL02_2_NTNN/tong_ct10|1800000000"});
   // HTKK 5.8.3: Y1 no longer checks từ ngày (0441 gone); từ ngày 01/06/2026.
   case "04NTNN-TT89-one-subcontractor-from-01-06-2026":return new HtkkDeclarationCasePlan(caseId,"Y1","3.0.9","2015","Ntnn04TT89Nckt309",new string[]{"101","101_8","Y1"},"range","22","2026","","01/06/2026","07/10/2026",false,
    new string[]{"02-2/NTNN"},new string[]{"01|Tờ khai","01-2|02-2/NTNN"},
    "InterfaceTemplates/excel/04_NTNN_TT89_309.xls","3326d1ab92a20a1b5d52aa00cb32610584ef2fee4e2a86b73efa5bf4e093ca61","InterfaceTemplates/xml/04_NTNN_TT89_309.xml","c8555e3dbc3a2bbf0b5ac98a3d8f225c8fc2fc5dc0970475e8df06506802bee8",
    "Validate/04_NTNN_TT89_309.xsd","eaa0ab3ed35eed6ff0a2dd33cf2bd5dba8c179cd65169cc869ca46f1c03ea591",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,79,
    new string[]{"01|AB32|2000000000","01|AB33|1800000000","01|AJ32|0","01|T35|1800000000","01|AB35|1500000000","01|AJ35|-300000000","01|AJ36|3000000","01|AB38|3000000","01|AB39|0","01-2|BI51|2000000000","01-2|BX51|1800000000"},
    new string[]{Main+"GiaTriHDong/keKhai|2000000000",Main+"GiaTriHDong/quyetToan|2000000000",Main+"GiaTriHDong/chenhLech|0",Main+"DThuTinhThue/quyetToan|1800000000",Main+"DThuNTPhu/quyetToan|300000000",Main+"DThuTinhThueNTNN/keKhai|1800000000",Main+"DThuTinhThueNTNN/quyetToan|1500000000",Main+"SoThueTNDNPNop/chenhLech|3000000",Main+"SoThueDaNop/quyetToan|72000000",Main+"SoThueConPNop/quyetToan|3000000",Main+"SoThueNopThua/quyetToan|0","HSoThueDTu/HSoKhaiThue/PLuc/PL02_2_NTNN/tong_ct9|2000000000","HSoThueDTu/HSoKhaiThue/PLuc/PL02_2_NTNN/tong_ct10|1800000000"});
   // X9 02/NTNN quyết toán TT89 (non-gating, web-xml-import-reexport): KieuKy 22 like D6/Y1 (period kind 'range');
   // Menu.xml sheets 01-1 "02-1/NTNN" and 01-2 "02-2/NTNN" are the workbook sheets of the same names, both ticked in
   // the period dialog. Ntnn02TT89Nckt309 has no FinishImportXML; AutoBindData_0 writes the settlement case (BK8/BL8)
   // and Refresh_1/2 copy BO34/BO35 (02-1 totals + 02-2 totals) into AF34/AF35, equal to the web values. 02-1 J holds
   // nước cư trú (control 56, GetDMQuocGia) with its code JP in CW (ct3_ma). One row per annex, no insertion: totals
   // 02-1 BY42/CJ42, 02-2 BI56/BX56. XML checks = the Decimal oracle NTNN_QT (htkk_declaration_web_cases).
   case "02NTNN-TT89-two-annexes-2026":return new HtkkDeclarationCasePlan(caseId,"X9","3.0.9","2013","Ntnn02TT89Nckt309",new string[]{"101","101_8","X9"},"range","22","2026","","01/07/2026","30/09/2026",false,
    new string[]{"02-1/NTNN","02-2/NTNN"},new string[]{"01|Tờ khai","01-1|02-1/NTNN","01-2|02-2/NTNN"},
    "InterfaceTemplates/excel/02_NTNN_TT89_309.xls","28e9ebf3d3440988f21bc219c813a172f61ca696870c20a6ee79310156915b37","InterfaceTemplates/xml/02_NTNN_TT89_309.xml","485b44e9a7ce50e8bb40a1d01e5ef9f9f6e2bb16def14b4ebb6be711a7a93696",
    "Validate/02_NTNN_TT89_309.xsd","a63c0078197e64c317fca465b3a04287382e1e838b8cf261ae12865ea22d6b3f",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,112,
    new string[]{"01|AF34|3000000000","01|AF35|2800000000","01|AO34|0","01|AF37|1800000000","01|AF38|130000000","01|AO40|4000000","01|AF41|126000000","01|AF44|4000000","01|AF46|4000000","01|AF47|0","01-1|BY42|2000000000","01-1|CJ42|1800000000","01-2|BI56|1000000000","01-2|BX56|1000000000"},
    new string[]{Main+"GiaTriHDong/keKhai|3000000000",Main+"GiaTriHDong/quyetToan|3000000000",Main+"DThuTinhThue/quyetToan|2800000000",Main+"DThuTinhThueNTPhu/quyetToan|1000000000",Main+"DThuTinhThueNTNN/quyetToan|1800000000",Main+"SoThuePhaiNopNTNN/keKhai|126000000",Main+"SoThuePhaiNopNTNN/quyetToan|130000000",Main+"ThueTNDNPhaiNop/chenhLech|4000000",Main+"SoThueDaNop/quyetToan|126000000",Main+"SoThueConPhaiNop/quyetToan|4000000",Main+"ThueGTGTConPNop/quyetToan|0",Main+"ThueTNDNConPNop/quyetToan|4000000",Main+"SoThueNopThua/quyetToan|0","HSoThueDTu/HSoKhaiThue/PLuc/PL02_1_NTNN/tong_ct8|2000000000","HSoThueDTu/HSoKhaiThue/PLuc/PL02_1_NTNN/tong_ct9|1800000000","HSoThueDTu/HSoKhaiThue/PLuc/PL02_2_NTNN/tong_ct9|1000000000","HSoThueDTu/HSoKhaiThue/PLuc/PL02_2_NTNN/tong_ct10|1000000000"});
   // HTKK 5.8.3 (htkkVersion 5.8.3): as Y1, đến ngày 07/10/2026.
   case "02NTNN-TT89-two-annexes-to-07-10-2026":return new HtkkDeclarationCasePlan(caseId,"X9","3.0.9","2013","Ntnn02TT89Nckt309",new string[]{"101","101_8","X9"},"range","22","2026","","01/07/2026","07/10/2026",false,
    new string[]{"02-1/NTNN","02-2/NTNN"},new string[]{"01|Tờ khai","01-1|02-1/NTNN","01-2|02-2/NTNN"},
    "InterfaceTemplates/excel/02_NTNN_TT89_309.xls","28e9ebf3d3440988f21bc219c813a172f61ca696870c20a6ee79310156915b37","InterfaceTemplates/xml/02_NTNN_TT89_309.xml","485b44e9a7ce50e8bb40a1d01e5ef9f9f6e2bb16def14b4ebb6be711a7a93696",
    "Validate/02_NTNN_TT89_309.xsd","a63c0078197e64c317fca465b3a04287382e1e838b8cf261ae12865ea22d6b3f",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,112,
    new string[]{"01|AF34|3000000000","01|AF35|2800000000","01|AO34|0","01|AF37|1800000000","01|AF38|130000000","01|AO40|4000000","01|AF41|126000000","01|AF44|4000000","01|AF46|4000000","01|AF47|0","01-1|BY42|2000000000","01-1|CJ42|1800000000","01-2|BI56|1000000000","01-2|BX56|1000000000"},
    new string[]{Main+"GiaTriHDong/keKhai|3000000000",Main+"GiaTriHDong/quyetToan|3000000000",Main+"DThuTinhThue/quyetToan|2800000000",Main+"DThuTinhThueNTPhu/quyetToan|1000000000",Main+"DThuTinhThueNTNN/quyetToan|1800000000",Main+"SoThuePhaiNopNTNN/keKhai|126000000",Main+"SoThuePhaiNopNTNN/quyetToan|130000000",Main+"ThueTNDNPhaiNop/chenhLech|4000000",Main+"SoThueDaNop/quyetToan|126000000",Main+"SoThueConPhaiNop/quyetToan|4000000",Main+"ThueGTGTConPNop/quyetToan|0",Main+"ThueTNDNConPNop/quyetToan|4000000",Main+"SoThueNopThua/quyetToan|0","HSoThueDTu/HSoKhaiThue/PLuc/PL02_1_NTNN/tong_ct8|2000000000","HSoThueDTu/HSoKhaiThue/PLuc/PL02_1_NTNN/tong_ct9|1800000000","HSoThueDTu/HSoKhaiThue/PLuc/PL02_2_NTNN/tong_ct9|1000000000","HSoThueDTu/HSoKhaiThue/PLuc/PL02_2_NTNN/tong_ct10|1000000000"});
   // HTKK 5.8.3: X9 no longer checks từ ngày (Menu.xml StartDate 01/01/1900, 0441 gone); từ ngày 01/06/2026.
   case "02NTNN-TT89-two-annexes-from-01-06-2026":return new HtkkDeclarationCasePlan(caseId,"X9","3.0.9","2013","Ntnn02TT89Nckt309",new string[]{"101","101_8","X9"},"range","22","2026","","01/06/2026","07/10/2026",false,
    new string[]{"02-1/NTNN","02-2/NTNN"},new string[]{"01|Tờ khai","01-1|02-1/NTNN","01-2|02-2/NTNN"},
    "InterfaceTemplates/excel/02_NTNN_TT89_309.xls","28e9ebf3d3440988f21bc219c813a172f61ca696870c20a6ee79310156915b37","InterfaceTemplates/xml/02_NTNN_TT89_309.xml","485b44e9a7ce50e8bb40a1d01e5ef9f9f6e2bb16def14b4ebb6be711a7a93696",
    "Validate/02_NTNN_TT89_309.xsd","a63c0078197e64c317fca465b3a04287382e1e838b8cf261ae12865ea22d6b3f",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,112,
    new string[]{"01|AF34|3000000000","01|AF35|2800000000","01|AO34|0","01|AF37|1800000000","01|AF38|130000000","01|AO40|4000000","01|AF41|126000000","01|AF44|4000000","01|AF46|4000000","01|AF47|0","01-1|BY42|2000000000","01-1|CJ42|1800000000","01-2|BI56|1000000000","01-2|BX56|1000000000"},
    new string[]{Main+"GiaTriHDong/keKhai|3000000000",Main+"GiaTriHDong/quyetToan|3000000000",Main+"DThuTinhThue/quyetToan|2800000000",Main+"DThuTinhThueNTPhu/quyetToan|1000000000",Main+"DThuTinhThueNTNN/quyetToan|1800000000",Main+"SoThuePhaiNopNTNN/keKhai|126000000",Main+"SoThuePhaiNopNTNN/quyetToan|130000000",Main+"ThueTNDNPhaiNop/chenhLech|4000000",Main+"SoThueDaNop/quyetToan|126000000",Main+"SoThueConPhaiNop/quyetToan|4000000",Main+"ThueGTGTConPNop/quyetToan|0",Main+"ThueTNDNConPNop/quyetToan|4000000",Main+"SoThueNopThua/quyetToan|0","HSoThueDTu/HSoKhaiThue/PLuc/PL02_1_NTNN/tong_ct8|2000000000","HSoThueDTu/HSoKhaiThue/PLuc/PL02_1_NTNN/tong_ct9|1800000000","HSoThueDTu/HSoKhaiThue/PLuc/PL02_2_NTNN/tong_ct9|1000000000","HSoThueDTu/HSoKhaiThue/PLuc/PL02_2_NTNN/tong_ct10|1000000000"});
   // C9 02/NTNN quyết toán TT80 (non-gating, web-xml-import-reexport): KieuKy 22 like D6 (period kind 'range', Menu.xml
   // EndDate 01/10/2026); Menu.xml sheets 01-1 "02-1/NTNN" and 01-2 "02-2/NTNN" are the workbook sheets of the same names,
   // both ticked in the period dialog. Ntnn02TT80Nckt251 has no FinishImportXML; AutoBindData_0 writes the settlement case
   // (BK8/BL8); AF34/AF35 hold the XLS formulas =BK34/=BK35 (BK34 = 02-1 BG27 + 02-2 BD26, BK35 = 02-1 BY27 + 02-2 BS26),
   // which CellChange_1/2, UpdateFormula_1/2 and Refresh_1/2 set again. 02-1 J nước cư trú (control 56) → CM ct3_ma JP
   // (text, checked in the XML only); 02-1 AJ / 02-2 AM địa điểm (control 100, dicTinhTPMoi) → CO ct6_ma 101 / CB ct7_ma
   // 103. One row per annex, no insertion: 02-1 template row 25 (totals 27), 02-2 row 24 (totals 26). XML checks = the
   // Decimal oracle NTNN02 (htkk_declaration_web_cases).
   case "02NTNN-TT80-two-annexes-2026":return new HtkkDeclarationCasePlan(caseId,"C9","2.5.1","921","Ntnn02TT80Nckt251",new string[]{"101","101_8","C9"},"range","22","2026","","01/01/2026","30/09/2026",false,
    new string[]{"02-1/NTNN","02-2/NTNN"},new string[]{"01|Tờ khai","01-1|02-1/NTNN","01-2|02-2/NTNN"},
    "InterfaceTemplates/excel/02_NTNN_TT80_251.xls","c956b22758d8b4f6470765ecd09074689947702d8bc9a3e0d3f1b7f990f147c4","InterfaceTemplates/xml/02_NTNN_TT80_251.xml","c3cd8590d3fd6f0c7c4f76915f0fbe854dfba27a721dfb5be55fd136d6fbca5a",
    "Validate/02_NTNN_TT80_251.xsd","169eb977f1eed3c4e4ea269bb2d2cbc197e5dbcf0a8be26a92140b2475fe41b5",TKhaiThue,TKhaiThueSha256,WorkbookService,115,
    new string[]{"01|BK34|3000000000","01|BK35|2800000000","01|AF34|3000000000","01|AF35|2800000000","01|AO34|0","01|AF37|1800000000","01|AF38|130000000","01|AO40|4000000","01|AF41|126000000","01|AF44|4000000","01|AF46|4000000","01|AF47|0","01-1|BG27|2000000000","01-1|BY27|1800000000","01-1|CO25|101","01-2|BD26|1000000000","01-2|BS26|1000000000","01-2|CB24|103"},
    new string[]{Main+"GiaTriHDong/keKhai|3000000000",Main+"GiaTriHDong/quyetToan|3000000000",Main+"DThuChuaGomGTGT/quyetToan|2800000000",Main+"DThuTinhThueNTPhu/quyetToan|1000000000",Main+"DThuTinhThueNTNN/quyetToan|1800000000",Main+"SoThuePhaiNopNTNN/keKhai|126000000",Main+"SoThuePhaiNopNTNN/quyetToan|130000000",Main+"ThueTNDNPhaiNop/chenhLech|4000000",Main+"SoThueDaNop/quyetToan|126000000",Main+"SoThueConPhaiNop/quyetToan|4000000",Main+"ThueGTGTConPNop/quyetToan|0",Main+"ThueTNDNConPNop/quyetToan|4000000",Main+"SoThueNopThua/quyetToan|0","HSoThueDTu/HSoKhaiThue/PLuc/PL02_1_NTNN/tong_ct8|2000000000","HSoThueDTu/HSoKhaiThue/PLuc/PL02_1_NTNN/tong_ct9|1800000000","HSoThueDTu/HSoKhaiThue/PLuc/PL02_1_NTNN/tong_ct10|5","HSoThueDTu/HSoKhaiThue/PLuc/PL02_2_NTNN/tong_ct9|1000000000","HSoThueDTu/HSoKhaiThue/PLuc/PL02_2_NTNN/tong_ct10|1000000000"});
   // HTKK 5.8.3 (htkkVersion 5.8.3): C9 accepts đến ngày up to 06/10/2026 (0719; 5.8.2 stopped at 01/10/2026).
   case "02NTNN-TT80-two-annexes-to-06-10-2026":return new HtkkDeclarationCasePlan(caseId,"C9","2.5.1","921","Ntnn02TT80Nckt251",new string[]{"101","101_8","C9"},"range","22","2026","","01/01/2026","06/10/2026",false,
    new string[]{"02-1/NTNN","02-2/NTNN"},new string[]{"01|Tờ khai","01-1|02-1/NTNN","01-2|02-2/NTNN"},
    "InterfaceTemplates/excel/02_NTNN_TT80_251.xls","c956b22758d8b4f6470765ecd09074689947702d8bc9a3e0d3f1b7f990f147c4","InterfaceTemplates/xml/02_NTNN_TT80_251.xml","c3cd8590d3fd6f0c7c4f76915f0fbe854dfba27a721dfb5be55fd136d6fbca5a",
    "Validate/02_NTNN_TT80_251.xsd","169eb977f1eed3c4e4ea269bb2d2cbc197e5dbcf0a8be26a92140b2475fe41b5",TKhaiThue,TKhaiThueSha256,WorkbookService,115,
    new string[]{"01|BK34|3000000000","01|BK35|2800000000","01|AF34|3000000000","01|AF35|2800000000","01|AO34|0","01|AF37|1800000000","01|AF38|130000000","01|AO40|4000000","01|AF41|126000000","01|AF44|4000000","01|AF46|4000000","01|AF47|0","01-1|BG27|2000000000","01-1|BY27|1800000000","01-1|CO25|101","01-2|BD26|1000000000","01-2|BS26|1000000000","01-2|CB24|103"},
    new string[]{Main+"GiaTriHDong/keKhai|3000000000",Main+"GiaTriHDong/quyetToan|3000000000",Main+"DThuChuaGomGTGT/quyetToan|2800000000",Main+"DThuTinhThueNTPhu/quyetToan|1000000000",Main+"DThuTinhThueNTNN/quyetToan|1800000000",Main+"SoThuePhaiNopNTNN/keKhai|126000000",Main+"SoThuePhaiNopNTNN/quyetToan|130000000",Main+"ThueTNDNPhaiNop/chenhLech|4000000",Main+"SoThueDaNop/quyetToan|126000000",Main+"SoThueConPhaiNop/quyetToan|4000000",Main+"ThueGTGTConPNop/quyetToan|0",Main+"ThueTNDNConPNop/quyetToan|4000000",Main+"SoThueNopThua/quyetToan|0","HSoThueDTu/HSoKhaiThue/PLuc/PL02_1_NTNN/tong_ct8|2000000000","HSoThueDTu/HSoKhaiThue/PLuc/PL02_1_NTNN/tong_ct9|1800000000","HSoThueDTu/HSoKhaiThue/PLuc/PL02_1_NTNN/tong_ct10|5","HSoThueDTu/HSoKhaiThue/PLuc/PL02_2_NTNN/tong_ct9|1000000000","HSoThueDTu/HSoKhaiThue/PLuc/PL02_2_NTNN/tong_ct10|1000000000"});
   // G7 01/TTS TT40 2.8.3 (non-gating, HTKK 5.8.2 oracle): KieuKy 42 = SetLayoutToQDDSThueMSTToChucCaNhanNamThangQuy
   // (0x60004fb: Năm ticked by default, Tháng, Quý, Kỳ thanh toán; annex list shown). Menu 101 -> 101_15 -> G7. Menu.xml
   // sheets 01-1 "01-1/BK-TTS" and 01-2 "01-2/BK-TTS"; CheckChonLoaiNopThue pairs cá nhân trực tiếp khai with 01-1 and tổ
   // chức khai thay with 01-2 (tháng/quý: AutoBindData_0 forces the latter). FinishImportXML recomputes nothing but the
   // XLS formulas (GTGT/TNCN of a row, [28], [29]) and runs LockUnLockDongHopDongHoacKy, which deletes the contract fields
   // of the period rows (the web leaves them empty). Sheet checks are those formula cells; XML checks = CaNhanKeKhai.
   case "01TTS-individual-one-contract-Y2025":return new HtkkDeclarationCasePlan(caseId,"G7","2.8.3","470","Tts01TT40Nckt283",new string[]{"101","101_15","G7"},"year","42","2025","","01/01/2025","31/12/2025",false,
    new string[]{"01-1/BK-TTS"},new string[]{"01|Tờ khai","01-1|01-1/BK-TTS"},
    "InterfaceTemplates/excel/01_TTS_TT40_283.xls","2b7a1c4614ddeb155c751a8e7e2bc70f71071d3b8721ac05e84990068507b785","InterfaceTemplates/xml/01_TTS_TT40_283.xml","c3aa4916775e3db6d44a33144ebad5bf2e6701b745fbde72ae3fe30f11d7456e",
    "Validate/01_TTS_TT40_283.xsd","5fa930a828dcfcfa772ff668bcfdc9a333b7a6ba7433f97a5da1e690f9f01e3d",TKhaiThue,TKhaiThueSha256,WorkbookService,210,
    new string[]{"01|U210|120000000","01|U211|120000000","01|U212|6000000","01|U213|6000000","01|U214|10000010","01|U215|500001","01|U216|6500001","01-1|AJ66|120000000","01-1|AQ67|60000000","01-1|AR67|3000000","01-1|AS67|3000000","01-1|AR68|3000000"},
    new string[]{Main+"mst_cu|9999999997",Main+"CaNhanKeKhai/ct23|120000000",Main+"CaNhanKeKhai/ct24|120000000",Main+"CaNhanKeKhai/ct25|6000000",Main+"CaNhanKeKhai/ct26|6000000",Main+"CaNhanKeKhai/ct27|10000010",Main+"CaNhanKeKhai/ct28|500001",Main+"CaNhanKeKhai/ct29|6500001"});
   case "01TTS-individual-two-contracts-Y2025":return new HtkkDeclarationCasePlan(caseId,"G7","2.8.3","470","Tts01TT40Nckt283",new string[]{"101","101_15","G7"},"year","42","2025","","01/01/2025","31/12/2025",false,
    new string[]{"01-1/BK-TTS"},new string[]{"01|Tờ khai","01-1|01-1/BK-TTS"},
    "InterfaceTemplates/excel/01_TTS_TT40_283.xls","2b7a1c4614ddeb155c751a8e7e2bc70f71071d3b8721ac05e84990068507b785","InterfaceTemplates/xml/01_TTS_TT40_283.xml","c3aa4916775e3db6d44a33144ebad5bf2e6701b745fbde72ae3fe30f11d7456e",
    "Validate/01_TTS_TT40_283.xsd","5fa930a828dcfcfa772ff668bcfdc9a333b7a6ba7433f97a5da1e690f9f01e3d",TKhaiThue,TKhaiThueSha256,WorkbookService,274,
    new string[]{"01|U210|78000000","01|U211|0","01|U212|0","01|U213|0","01|U216|0","01-1|AJ66|48000000","01-1|AJ68|30000000","01-1|AQ67|0","01-1|AR67|0","01-1|AQ70|0"},
    new string[]{Main+"mst_cu|9999999997",Main+"CaNhanKeKhai/ct23|78000000",Main+"CaNhanKeKhai/ct24|0",Main+"CaNhanKeKhai/ct25|0",Main+"CaNhanKeKhai/ct26|0",Main+"CaNhanKeKhai/ct27|0",Main+"CaNhanKeKhai/ct28|0",Main+"CaNhanKeKhai/ct29|0"});
   case "01TTS-organization-two-individuals-Q3-2026":return new HtkkDeclarationCasePlan(caseId,"G7","2.8.3","470","Tts01TT40Nckt283",new string[]{"101","101_15","G7"},"quarter","42","2026","3","01/07/2026","30/09/2026",false,
    new string[]{"01-2/BK-TTS"},new string[]{"01|Tờ khai","01-2|01-2/BK-TTS"},
    "InterfaceTemplates/excel/01_TTS_TT40_283.xls","2b7a1c4614ddeb155c751a8e7e2bc70f71071d3b8721ac05e84990068507b785","InterfaceTemplates/xml/01_TTS_TT40_283.xml","c3aa4916775e3db6d44a33144ebad5bf2e6701b745fbde72ae3fe30f11d7456e",
    "Validate/01_TTS_TT40_283.xsd","5fa930a828dcfcfa772ff668bcfdc9a333b7a6ba7433f97a5da1e690f9f01e3d",TKhaiThue,TKhaiThueSha256,WorkbookService,386,
    new string[]{"01|U210|60000030","01|U211|45000030","01|U212|2250002","01|U213|2250002","01|U216|2250002","01-2|AM74|180000120","01-2|AQ77|45000030","01-2|AR77|2250002","01-2|AS77|2250002","01-2|AQ80|0"},
    new string[]{Main+"mst_cu|9999999997",Main+"CaNhanKeKhai/ct23|60000030",Main+"CaNhanKeKhai/ct24|45000030",Main+"CaNhanKeKhai/ct25|2250002",Main+"CaNhanKeKhai/ct26|2250002",Main+"CaNhanKeKhai/ct27|0",Main+"CaNhanKeKhai/ct28|0",Main+"CaNhanKeKhai/ct29|2250002"});
   case "01TTS-organization-monthly-M10-2026":return new HtkkDeclarationCasePlan(caseId,"G7","2.8.3","470","Tts01TT40Nckt283",new string[]{"101","101_15","G7"},"month","42","2026","10","01/10/2026","31/10/2026",false,
    new string[]{"01-2/BK-TTS"},new string[]{"01|Tờ khai","01-2|01-2/BK-TTS"},
    "InterfaceTemplates/excel/01_TTS_TT40_283.xls","2b7a1c4614ddeb155c751a8e7e2bc70f71071d3b8721ac05e84990068507b785","InterfaceTemplates/xml/01_TTS_TT40_283.xml","c3aa4916775e3db6d44a33144ebad5bf2e6701b745fbde72ae3fe30f11d7456e",
    "Validate/01_TTS_TT40_283.xsd","5fa930a828dcfcfa772ff668bcfdc9a333b7a6ba7433f97a5da1e690f9f01e3d",TKhaiThue,TKhaiThueSha256,WorkbookService,216,
    new string[]{"01|U210|50000001","01|U211|50000001","01|U212|2500000","01|U213|2500000","01-2|AN74|50000000","01-2|AQ75|50000001","01-2|AR75|2500000","01-2|AS75|2500000","01-2|AQ76|50000000","01-2|AR76|2500000"},
    new string[]{Main+"mst_cu|9999999997",Main+"CaNhanKeKhai/ct23|50000001",Main+"CaNhanKeKhai/ct24|50000001",Main+"CaNhanKeKhai/ct25|2500000",Main+"CaNhanKeKhai/ct26|2500000",Main+"CaNhanKeKhai/ct27|0",Main+"CaNhanKeKhai/ct28|0",Main+"CaNhanKeKhai/ct29|2500000"});
   // Y7 01/TCKT TT89 3.0.9 (non-gating, HTKK 5.8.1 oracle): KieuKy 21 = SetLayoutToKhaiThangQuyLanPhatSinh. Menu 101 ->
   // 101_37 -> Y7. One bảng kê ticked in the period dialog (axfpsPhuLuc_ButtonClicked unticks the other); 02/BK-KTBĐS opens the
   // tỉnh/xã/CQT panel (the synthetic profile ward). AutoBindData_0 sets hopTacKD/batDongSan from the attached bảng kê; the XLS
   // formulas recompute 01-1 I = H x K, 01-2 O/P and the totals after the import. Sheet checks are those cells.
   case "01TCKT-hop-tac-kd-two-individuals-Q4-2026":return new HtkkDeclarationCasePlan(caseId,"Y7","3.0.9","2007","Tckt01TT89Nckt309",new string[]{"101","101_37","Y7"},"quarter","21","2026","4","01/10/2026","31/12/2026",false,
    new string[]{"01/BK-KTHTKD"},new string[]{"01|Tờ khai","01-1|01/BK-KTHTKD"},
    "InterfaceTemplates/excel/01_TCKT_TT89_309.xls","83bae02e70b49955af05e725a1d317da190c05afc35483376f9ae82a6eab4ff0","InterfaceTemplates/xml/01_TCKT_TT89_309.xml","2e99cdd5c7afc75ee539272ab2a8003ac0fb5d80387073d177a69f6723fdd69e",
    "Validate/01_TCKT_TT89_309.xsd","aa29c008da1ae19d4d12eb263fa29fc0d21dbc8fafa079dd02fc388a18ad67b1",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,65,
    new string[]{"01|U59|420000000","01|U60|410000000","01|U61|7100000","01-1|I58|6000000","01-1|I59|1100000","01-1|G62|420000000","01-1|H62|410000000","01-1|I62|7100000"},
    new string[]{Main+"ThongTinKeKhai/DoiTuong/hopTacKD|1",Main+"ThongTinKeKhai/DoiTuong/batDongSan|0",Main+"ThongTinKeKhai/ct6|0",Main+"ThongTinKeKhai/ct7|420000000",Main+"ThongTinKeKhai/ct8|410000000",Main+"ThongTinKeKhai/ct9|7100000",Main+"ThongTinKeKhai/ct10|0",Main+"ThongTinKeKhai/ct11|0",Main+"ThongTinKeKhai/ct12|0",Main+"ThongTinKeKhai/ct13|0"});
   case "01TCKT-bds-three-lessors-M10-2026":return new HtkkDeclarationCasePlan(caseId,"Y7","3.0.9","2007","Tckt01TT89Nckt309",new string[]{"101","101_37","Y7"},"month","21","2026","10","01/10/2026","31/10/2026",false,
    new string[]{"02/BK-KTBĐS"},new string[]{"01|Tờ khai","01-2|02/BK-KTBĐS"},
    "InterfaceTemplates/excel/01_TCKT_TT89_309.xls","83bae02e70b49955af05e725a1d317da190c05afc35483376f9ae82a6eab4ff0","InterfaceTemplates/xml/01_TCKT_TT89_309.xml","2e99cdd5c7afc75ee539272ab2a8003ac0fb5d80387073d177a69f6723fdd69e",
    "Validate/01_TCKT_TT89_309.xsd","aa29c008da1ae19d4d12eb263fa29fc0d21dbc8fafa079dd02fc388a18ad67b1",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,79,
    new string[]{"01|U63|1560000011","01|U64|63000001","01|U65|53000000","01-2|O58|3000001","01-2|P58|3000000","01-2|O59|60000000","01-2|P59|50000000","01-2|O60|0","01-2|P60|0","01-2|O63|63000001","01-2|P63|53000000"},
    new string[]{Main+"ThongTinKeKhai/DoiTuong/hopTacKD|0",Main+"ThongTinKeKhai/DoiTuong/batDongSan|1",Main+"ThongTinKeKhai/ct6|0",Main+"ThongTinKeKhai/ct7|0",Main+"ThongTinKeKhai/ct8|0",Main+"ThongTinKeKhai/ct9|0",Main+"ThongTinKeKhai/ct10|0",Main+"ThongTinKeKhai/ct11|1560000011",Main+"ThongTinKeKhai/ct12|63000001",Main+"ThongTinKeKhai/ct13|53000000"});
   case "01TCKT-bds-occurrence-D15-10-2026":return new HtkkDeclarationCasePlan(caseId,"Y7","3.0.9","2007","Tckt01TT89Nckt309",new string[]{"101","101_37","Y7"},"day","21","2026","","15/10/2026","15/10/2026",false,
    new string[]{"02/BK-KTBĐS"},new string[]{"01|Tờ khai","01-2|02/BK-KTBĐS"},
    "InterfaceTemplates/excel/01_TCKT_TT89_309.xls","83bae02e70b49955af05e725a1d317da190c05afc35483376f9ae82a6eab4ff0","InterfaceTemplates/xml/01_TCKT_TT89_309.xml","2e99cdd5c7afc75ee539272ab2a8003ac0fb5d80387073d177a69f6723fdd69e",
    "Validate/01_TCKT_TT89_309.xsd","aa29c008da1ae19d4d12eb263fa29fc0d21dbc8fafa079dd02fc388a18ad67b1",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,63,
    new string[]{"01|U63|80000000","01|U64|4000000","01|U65|3000000","01-2|O58|4000000","01-2|P58|3000000","01-2|L61|80000000","01-2|O61|4000000","01-2|P61|3000000"},
    new string[]{Main+"ThongTinKeKhai/DoiTuong/hopTacKD|0",Main+"ThongTinKeKhai/DoiTuong/batDongSan|1",Main+"ThongTinKeKhai/ct6|0",Main+"ThongTinKeKhai/ct7|0",Main+"ThongTinKeKhai/ct8|0",Main+"ThongTinKeKhai/ct9|0",Main+"ThongTinKeKhai/ct10|0",Main+"ThongTinKeKhai/ct11|80000000",Main+"ThongTinKeKhai/ct12|4000000",Main+"ThongTinKeKhai/ct13|3000000"});
   // Y7 01/TCKT TT89 3.1.0 (non-gating, HTKK 5.8.2 oracle; Tckt01TT89Nckt310, 01_TCKT_TT89_310, byte-identical in 5.8.3). The
   // same dialog and sheets as 3.0.9; the bảng kê I / P read the NQ 43 tick (01-1 X, 01-2 S) and PL 01-3 "PL NQ 43/2026/QH16"
   // (workbook sheet giam_thue) holds the ticked rows. In the period dialog the third annex row (PL 01-3) unticks the second
   // (axfpsPhuLuc_ButtonClicked, unchanged from 5.8.1), so with 01/BK-KTHTKD any order leaves both ticked.
   case "01TCKT-310-hop-tac-kd-two-individuals-Q4-2026":return new HtkkDeclarationCasePlan(caseId,"Y7","3.1.0","2007","Tckt01TT89Nckt310",new string[]{"101","101_37","Y7"},"quarter","21","2026","4","01/10/2026","31/12/2026",false,
    new string[]{"01/BK-KTHTKD"},new string[]{"01|Tờ khai","01-1|01/BK-KTHTKD"},
    "InterfaceTemplates/excel/01_TCKT_TT89_310.xls","95ecbc2cd702100d49d946fd526ae71916a53229f25b335b358c4e35c3c48cd7","InterfaceTemplates/xml/01_TCKT_TT89_310.xml","2e99cdd5c7afc75ee539272ab2a8003ac0fb5d80387073d177a69f6723fdd69e",
    "Validate/01_TCKT_TT89_310.xsd","c408a41324cce9e7cfb7f1a8366088de800a589165c397a1fd7a5c7cab145182",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,67,
    new string[]{"01|U59|420000000","01|U60|410000000","01|U61|7100000","01-1|I58|6000000","01-1|I59|1100000","01-1|G62|420000000","01-1|H62|410000000","01-1|I62|7100000"},
    new string[]{Main+"ThongTinKeKhai/DoiTuong/hopTacKD|1",Main+"ThongTinKeKhai/DoiTuong/batDongSan|0",Main+"ThongTinKeKhai/ct6|0",Main+"ThongTinKeKhai/ct7|420000000",Main+"ThongTinKeKhai/ct8|410000000",Main+"ThongTinKeKhai/ct9|7100000",Main+"ThongTinKeKhai/ct10|0",Main+"ThongTinKeKhai/ct11|0",Main+"ThongTinKeKhai/ct12|0",Main+"ThongTinKeKhai/ct13|0"});
   case "01TCKT-310-bds-three-lessors-M10-2026":return new HtkkDeclarationCasePlan(caseId,"Y7","3.1.0","2007","Tckt01TT89Nckt310",new string[]{"101","101_37","Y7"},"month","21","2026","10","01/10/2026","31/10/2026",false,
    new string[]{"02/BK-KTBĐS"},new string[]{"01|Tờ khai","01-2|02/BK-KTBĐS"},
    "InterfaceTemplates/excel/01_TCKT_TT89_310.xls","95ecbc2cd702100d49d946fd526ae71916a53229f25b335b358c4e35c3c48cd7","InterfaceTemplates/xml/01_TCKT_TT89_310.xml","2e99cdd5c7afc75ee539272ab2a8003ac0fb5d80387073d177a69f6723fdd69e",
    "Validate/01_TCKT_TT89_310.xsd","c408a41324cce9e7cfb7f1a8366088de800a589165c397a1fd7a5c7cab145182",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,82,
    new string[]{"01|U63|1560000011","01|U64|63000001","01|U65|53000000","01-2|O58|3000001","01-2|P58|3000000","01-2|O59|60000000","01-2|P59|50000000","01-2|O60|0","01-2|P60|0","01-2|O63|63000001","01-2|P63|53000000"},
    new string[]{Main+"ThongTinKeKhai/DoiTuong/hopTacKD|0",Main+"ThongTinKeKhai/DoiTuong/batDongSan|1",Main+"ThongTinKeKhai/ct6|0",Main+"ThongTinKeKhai/ct7|0",Main+"ThongTinKeKhai/ct8|0",Main+"ThongTinKeKhai/ct9|0",Main+"ThongTinKeKhai/ct10|0",Main+"ThongTinKeKhai/ct11|1560000011",Main+"ThongTinKeKhai/ct12|63000001",Main+"ThongTinKeKhai/ct13|53000000"});
   case "01TCKT-310-bds-occurrence-D15-10-2026":return new HtkkDeclarationCasePlan(caseId,"Y7","3.1.0","2007","Tckt01TT89Nckt310",new string[]{"101","101_37","Y7"},"day","21","2026","","15/10/2026","15/10/2026",false,
    new string[]{"02/BK-KTBĐS"},new string[]{"01|Tờ khai","01-2|02/BK-KTBĐS"},
    "InterfaceTemplates/excel/01_TCKT_TT89_310.xls","95ecbc2cd702100d49d946fd526ae71916a53229f25b335b358c4e35c3c48cd7","InterfaceTemplates/xml/01_TCKT_TT89_310.xml","2e99cdd5c7afc75ee539272ab2a8003ac0fb5d80387073d177a69f6723fdd69e",
    "Validate/01_TCKT_TT89_310.xsd","c408a41324cce9e7cfb7f1a8366088de800a589165c397a1fd7a5c7cab145182",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,64,
    new string[]{"01|U63|80000000","01|U64|4000000","01|U65|3000000","01-2|O58|4000000","01-2|P58|3000000","01-2|L61|80000000","01-2|O61|4000000","01-2|P61|3000000"},
    new string[]{Main+"ThongTinKeKhai/DoiTuong/hopTacKD|0",Main+"ThongTinKeKhai/DoiTuong/batDongSan|1",Main+"ThongTinKeKhai/ct6|0",Main+"ThongTinKeKhai/ct7|0",Main+"ThongTinKeKhai/ct8|0",Main+"ThongTinKeKhai/ct9|0",Main+"ThongTinKeKhai/ct10|0",Main+"ThongTinKeKhai/ct11|80000000",Main+"ThongTinKeKhai/ct12|4000000",Main+"ThongTinKeKhai/ct13|3000000"});
   case "01TCKT-310-pl-nq43-hop-tac-kd-Q4-2026":return new HtkkDeclarationCasePlan(caseId,"Y7","3.1.0","2007","Tckt01TT89Nckt310",new string[]{"101","101_37","Y7"},"quarter","21","2026","4","01/10/2026","31/12/2026",false,
    new string[]{"01/BK-KTHTKD","PL NQ 43/2026/QH16"},new string[]{"01|Tờ khai","01-1|01/BK-KTHTKD","giam_thue|PL NQ 43/2026/QH16"},
    "InterfaceTemplates/excel/01_TCKT_TT89_310.xls","95ecbc2cd702100d49d946fd526ae71916a53229f25b335b358c4e35c3c48cd7","InterfaceTemplates/xml/01_TCKT_TT89_310.xml","2e99cdd5c7afc75ee539272ab2a8003ac0fb5d80387073d177a69f6723fdd69e",
    "Validate/01_TCKT_TT89_310.xsd","c408a41324cce9e7cfb7f1a8366088de800a589165c397a1fd7a5c7cab145182",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,90,
    new string[]{"01|U59|800000000","01|U60|780000000","01|U61|14500000","01-1|I58|3500000","01-1|I59|7000000","01-1|I60|4000000","01-1|I63|14500000","giam_thue|I45|5000000","giam_thue|J45|1500000","giam_thue|I46|10000000","giam_thue|J46|3000000","giam_thue|I48|15000000","giam_thue|J48|4500000"},
    new string[]{Main+"ThongTinKeKhai/DoiTuong/hopTacKD|1",Main+"ThongTinKeKhai/DoiTuong/batDongSan|0",Main+"ThongTinKeKhai/ct6|0",Main+"ThongTinKeKhai/ct7|800000000",Main+"ThongTinKeKhai/ct8|780000000",Main+"ThongTinKeKhai/ct9|14500000",Main+"ThongTinKeKhai/ct10|0",Main+"ThongTinKeKhai/ct11|0",Main+"ThongTinKeKhai/ct12|0",Main+"ThongTinKeKhai/ct13|0"});
   // D4 04/GTGT TT80 2.7.4 (non-gating, HTKK 5.8.2 oracle): KieuKy 21 = SetLayoutToKhaiThangQuyLanPhatSinh (month,
   // quarter). Menu 101 -> 101_1 -> D4. FinishImportXML recomputes [23]/[25]/[27]/[29] (TinhLaiChiTieu23_25_27_29Default:
   // ROUND([22]x1%), ROUND([24]x5%), ROUND([26]x3%), ROUND([28]x2%); with 01-3 TinhLaiChiTieu22_den_28_TK then TheoPL01_3)
   // and the XLS formulas [30]/[31]/[32]. Sheet checks are those cells; XML checks = KhaiThueTPPTTTDT.
   case "04GTGT-TT80-one-group-M09-2026":return new HtkkDeclarationCasePlan(caseId,"D4","2.7.4","847","Gtgt04TT80Nckt274",new string[]{"101","101_1","D4"},"month","21","2026","09","01/09/2026","30/09/2026",false,
    new string[0],new string[]{"01|Tờ khai"},
    "InterfaceTemplates/excel/04_GTGT_TT80_274.xls","ab789cba81340f3d6024f83fad3035f23294731eb30ce7ae340f960a68bfd7b2","InterfaceTemplates/xml/04_GTGT_TT80_274.xml","9dfbbcbf412ea4c3ac614d5414cb920c05ac52aaed1ea211d3a5503b1fad81b8",
    "Validate/04_GTGT_TT80_274.xsd","9d407f57da377ce2d201d8d1bee1b247624b52ae5c4889e88310741b9e6a9bad",TKhaiThue,TKhaiThueSha256,WorkbookService,63,
    new string[]{"01|Z47|2000000","01|Q51|200000000","01|Z51|2000000","01|S54|205000000"},
    new string[]{Main+"KhaiThueTPPTTTDT/ct21|5000000",Main+"KhaiThueTPPTTTDT/PPhoiCCapHHoa/ct22|200000000",Main+"KhaiThueTPPTTTDT/PPhoiCCapHHoa/ct23|2000000",Main+"KhaiThueTPPTTTDT/DVuXDungKoBaoThauNVL/ct24|0",Main+"KhaiThueTPPTTTDT/DVuXDungKoBaoThauNVL/ct25|0",Main+"KhaiThueTPPTTTDT/HHoaXDungCoBaoThauNVL/ct26|0",Main+"KhaiThueTPPTTTDT/HHoaXDungCoBaoThauNVL/ct27|0",Main+"KhaiThueTPPTTTDT/HDongKDoanhKhac/ct28|0",Main+"KhaiThueTPPTTTDT/HDongKDoanhKhac/ct29|0",Main+"KhaiThueTPPTTTDT/DoanhThuVaSoThuePNop/ct30|200000000",Main+"KhaiThueTPPTTTDT/DoanhThuVaSoThuePNop/ct31|2000000",Main+"KhaiThueTPPTTTDT/ct32|205000000"});
   case "04GTGT-TT80-quarter-Q3-2026":return new HtkkDeclarationCasePlan(caseId,"D4","2.7.4","847","Gtgt04TT80Nckt274",new string[]{"101","101_1","D4"},"quarter","21","2026","3","01/07/2026","30/09/2026",false,
    new string[0],new string[]{"01|Tờ khai"},
    "InterfaceTemplates/excel/04_GTGT_TT80_274.xls","ab789cba81340f3d6024f83fad3035f23294731eb30ce7ae340f960a68bfd7b2","InterfaceTemplates/xml/04_GTGT_TT80_274.xml","9dfbbcbf412ea4c3ac614d5414cb920c05ac52aaed1ea211d3a5503b1fad81b8",
    "Validate/04_GTGT_TT80_274.xsd","9d407f57da377ce2d201d8d1bee1b247624b52ae5c4889e88310741b9e6a9bad",TKhaiThue,TKhaiThueSha256,WorkbookService,63,
    new string[]{"01|Z48|7500000","01|Z50|600000","01|Q51|180000000","01|Z51|8100000","01|S54|180000000"},
    new string[]{Main+"KhaiThueTPPTTTDT/ct21|0",Main+"KhaiThueTPPTTTDT/PPhoiCCapHHoa/ct22|0",Main+"KhaiThueTPPTTTDT/PPhoiCCapHHoa/ct23|0",Main+"KhaiThueTPPTTTDT/DVuXDungKoBaoThauNVL/ct24|150000000",Main+"KhaiThueTPPTTTDT/DVuXDungKoBaoThauNVL/ct25|7500000",Main+"KhaiThueTPPTTTDT/HHoaXDungCoBaoThauNVL/ct26|0",Main+"KhaiThueTPPTTTDT/HHoaXDungCoBaoThauNVL/ct27|0",Main+"KhaiThueTPPTTTDT/HDongKDoanhKhac/ct28|30000000",Main+"KhaiThueTPPTTTDT/HDongKDoanhKhac/ct29|600000",Main+"KhaiThueTPPTTTDT/DoanhThuVaSoThuePNop/ct30|180000000",Main+"KhaiThueTPPTTTDT/DoanhThuVaSoThuePNop/ct31|8100000",Main+"KhaiThueTPPTTTDT/ct32|180000000"});
   // Every group at a half đồng: [23] 1.234.567,5 -> 1.234.568, [25] 2.500.000,5, [27] 1.000.000,5, [29] 1.555.555,5 (away from zero).
   case "04GTGT-TT80-four-groups-rounding-M08-2026":return new HtkkDeclarationCasePlan(caseId,"D4","2.7.4","847","Gtgt04TT80Nckt274",new string[]{"101","101_1","D4"},"month","21","2026","08","01/08/2026","31/08/2026",false,
    new string[0],new string[]{"01|Tờ khai"},
    "InterfaceTemplates/excel/04_GTGT_TT80_274.xls","ab789cba81340f3d6024f83fad3035f23294731eb30ce7ae340f960a68bfd7b2","InterfaceTemplates/xml/04_GTGT_TT80_274.xml","9dfbbcbf412ea4c3ac614d5414cb920c05ac52aaed1ea211d3a5503b1fad81b8",
    "Validate/04_GTGT_TT80_274.xsd","9d407f57da377ce2d201d8d1bee1b247624b52ae5c4889e88310741b9e6a9bad",TKhaiThue,TKhaiThueSha256,WorkbookService,63,
    new string[]{"01|Z47|1234568","01|Z48|2500001","01|Z49|1000001","01|Z50|1555556","01|Q51|284567885","01|Z51|6290126","01|S54|285567885"},
    new string[]{Main+"KhaiThueTPPTTTDT/ct21|1000000",Main+"KhaiThueTPPTTTDT/PPhoiCCapHHoa/ct22|123456750",Main+"KhaiThueTPPTTTDT/PPhoiCCapHHoa/ct23|1234568",Main+"KhaiThueTPPTTTDT/DVuXDungKoBaoThauNVL/ct24|50000010",Main+"KhaiThueTPPTTTDT/DVuXDungKoBaoThauNVL/ct25|2500001",Main+"KhaiThueTPPTTTDT/HHoaXDungCoBaoThauNVL/ct26|33333350",Main+"KhaiThueTPPTTTDT/HHoaXDungCoBaoThauNVL/ct27|1000001",Main+"KhaiThueTPPTTTDT/HDongKDoanhKhac/ct28|77777775",Main+"KhaiThueTPPTTTDT/HDongKDoanhKhac/ct29|1555556",Main+"KhaiThueTPPTTTDT/DoanhThuVaSoThuePNop/ct30|284567885",Main+"KhaiThueTPPTTTDT/DoanhThuVaSoThuePNop/ct31|6290126",Main+"KhaiThueTPPTTTDT/ct32|285567885"});
   // PL 01-3 (sheet 01-3, giảm thuế NQ 204/2025 in quý 2/2026): five sale rows at 1/5/3/2/1 %; G = ROUND(D x (rate -
   // ROUND(rate x 80%, 1))/100); TinhLaiChiTieu22_den_28_TK writes [22]..[28] from the SUMIF totals I9..L9 and TheoPL01_3
   // [23]..[29] = ROUND(total x rate - reduction) of I11..L11.
   case "04GTGT-TT80-reduction-annex-Q2-2026":return new HtkkDeclarationCasePlan(caseId,"D4","2.7.4","847","Gtgt04TT80Nckt274",new string[]{"101","101_1","D4"},"quarter","21","2026","2","01/04/2026","30/06/2026",false,
    new string[]{"PL 142/2024/QH15-174/2024/QH15-204/2025/QH15"},new string[]{"01|Tờ khai","01-3|PL 142/2024/QH15-174/2024/QH15-204/2025/QH15"},
    "InterfaceTemplates/excel/04_GTGT_TT80_274.xls","ab789cba81340f3d6024f83fad3035f23294731eb30ce7ae340f960a68bfd7b2","InterfaceTemplates/xml/04_GTGT_TT80_274.xml","9dfbbcbf412ea4c3ac614d5414cb920c05ac52aaed1ea211d3a5503b1fad81b8",
    "Validate/04_GTGT_TT80_274.xsd","9d407f57da377ce2d201d8d1bee1b247624b52ae5c4889e88310741b9e6a9bad",TKhaiThue,TKhaiThueSha256,WorkbookService,96,
    new string[]{"01|Q47|123458000","01|Z47|987663","01|Z48|2000001","01|Z49|800001","01|Z50|1244445","01|Z51|5032110","01|S54|285569135","01-3|G30|246914","01-3|G34|3","01-3|I11|246917","01-3|G36|1258028","01-3|D39|1258028"},
    new string[]{Main+"KhaiThueTPPTTTDT/ct21|1000000",Main+"KhaiThueTPPTTTDT/PPhoiCCapHHoa/ct22|123458000",Main+"KhaiThueTPPTTTDT/PPhoiCCapHHoa/ct23|987663",Main+"KhaiThueTPPTTTDT/DVuXDungKoBaoThauNVL/ct24|50000010",Main+"KhaiThueTPPTTTDT/DVuXDungKoBaoThauNVL/ct25|2000001",Main+"KhaiThueTPPTTTDT/HHoaXDungCoBaoThauNVL/ct26|33333350",Main+"KhaiThueTPPTTTDT/HHoaXDungCoBaoThauNVL/ct27|800001",Main+"KhaiThueTPPTTTDT/HDongKDoanhKhac/ct28|77777775",Main+"KhaiThueTPPTTTDT/HDongKDoanhKhac/ct29|1244445",Main+"KhaiThueTPPTTTDT/DoanhThuVaSoThuePNop/ct30|284569135",Main+"KhaiThueTPPTTTDT/DoanhThuVaSoThuePNop/ct31|5032110",Main+"KhaiThueTPPTTTDT/ct32|285569135","HSoThueDTu/HSoKhaiThue/PLuc/PL_NQ142_GTGT/HH_DV_BanRaTrongKy/tongCongThueGTGTDuocGiam|1258028","HSoThueDTu/HSoKhaiThue/PLuc/PL_NQ142_GTGT/ChenhLech/ct9|1258028"});
   // Z3 04/GTGT TT89 3.0.9 (non-gating, HTKK 5.8.2 only): KieuKy 21 = SetLayoutToKhaiThangQuyLanPhatSinh, Z3 branch (pnThuHo
   // "Hoạt động kê khai riêng" and pnChuyenNhuong shown, left unticked). Menu 101 -> 101_1 -> Z3. [23]/[25]/[27]/[29] are the XLS
   // formulas AW87:AW90 that TinhLaiChiTieu23_25_27_29TheoPL01_1 copies (on import only when PL 01-1 is attached:
   // FinishImportXML -> TinhLaiThueSuat_PL01_1); [30], [31], [30a], [32] are XLS formulas. The annex case ticks sheet 01-1
   // "PL 204/2025/QH15" (workbook sheet 01_2). XML checks = KhaiThueTPPTTTDT and the PL 01-1 totals.
   case "04GTGT-TT89-one-group-M10-2026":return new HtkkDeclarationCasePlan(caseId,"Z3","3.0.9","2035","Gtgt04TT89Nckt309",new string[]{"101","101_1","Z3"},"month","21","2026","10","01/10/2026","31/10/2026",false,
    new string[0],new string[]{"01|Tờ khai"},
    "InterfaceTemplates/excel/04_GTGT_TT89_309.xls","2fbacc83c574ba75dfd660fa10345a397fdead41a2506dddc21e0fd69908149c","InterfaceTemplates/xml/04_GTGT_TT89_309.xml","86b9f16266026657e092f2aef8817a8ad64ac9c0812a6198601e83e4645f3e54",
    "Validate/04_GTGT_TT89_309.xsd","18dee33cbdc2df39453c8baa48153709c09718a262e25f52bee4e78d9174fa97",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,74,
    new string[]{"01|Z87|2000000","01|Q91|200000000","01|Z91|2000000","01|K103|200000000","01|K105|205000000"},
    new string[]{Main+"KhaiThueTPPTTTDT/ct21a|5000000",Main+"KhaiThueTPPTTTDT/ct21b|0",Main+"KhaiThueTPPTTTDT/PPhoiCCapHHoa/ct22|200000000",Main+"KhaiThueTPPTTTDT/PPhoiCCapHHoa/ct23|2000000",Main+"KhaiThueTPPTTTDT/DVuXDungKoBaoThauNVL/ct24|0",Main+"KhaiThueTPPTTTDT/DVuXDungKoBaoThauNVL/ct25|0",Main+"KhaiThueTPPTTTDT/HHoaXDungCoBaoThauNVL/ct26|0",Main+"KhaiThueTPPTTTDT/HHoaXDungCoBaoThauNVL/ct27|0",Main+"KhaiThueTPPTTTDT/HDongKDoanhKhac/ct28|0",Main+"KhaiThueTPPTTTDT/HDongKDoanhKhac/ct29|0",Main+"KhaiThueTPPTTTDT/DoanhThuVaSoThuePNop/ct30|200000000",Main+"KhaiThueTPPTTTDT/DoanhThuVaSoThuePNop/ct31|2000000",Main+"KhaiThueTPPTTTDT/ct30a|200000000",Main+"KhaiThueTPPTTTDT/ct32|205000000"});
   case "04GTGT-TT89-quarter-Q4-2026":return new HtkkDeclarationCasePlan(caseId,"Z3","3.0.9","2035","Gtgt04TT89Nckt309",new string[]{"101","101_1","Z3"},"quarter","21","2026","4","01/10/2026","31/12/2026",false,
    new string[0],new string[]{"01|Tờ khai"},
    "InterfaceTemplates/excel/04_GTGT_TT89_309.xls","2fbacc83c574ba75dfd660fa10345a397fdead41a2506dddc21e0fd69908149c","InterfaceTemplates/xml/04_GTGT_TT89_309.xml","86b9f16266026657e092f2aef8817a8ad64ac9c0812a6198601e83e4645f3e54",
    "Validate/04_GTGT_TT89_309.xsd","18dee33cbdc2df39453c8baa48153709c09718a262e25f52bee4e78d9174fa97",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,74,
    new string[]{"01|Z88|7500000","01|Z90|600000","01|Q91|180000000","01|Z91|8100000","01|K103|190000000","01|K105|190000000"},
    new string[]{Main+"KhaiThueTPPTTTDT/ct21a|0",Main+"KhaiThueTPPTTTDT/ct21b|10000000",Main+"KhaiThueTPPTTTDT/PPhoiCCapHHoa/ct22|0",Main+"KhaiThueTPPTTTDT/PPhoiCCapHHoa/ct23|0",Main+"KhaiThueTPPTTTDT/DVuXDungKoBaoThauNVL/ct24|150000000",Main+"KhaiThueTPPTTTDT/DVuXDungKoBaoThauNVL/ct25|7500000",Main+"KhaiThueTPPTTTDT/HHoaXDungCoBaoThauNVL/ct26|0",Main+"KhaiThueTPPTTTDT/HHoaXDungCoBaoThauNVL/ct27|0",Main+"KhaiThueTPPTTTDT/HDongKDoanhKhac/ct28|30000000",Main+"KhaiThueTPPTTTDT/HDongKDoanhKhac/ct29|600000",Main+"KhaiThueTPPTTTDT/DoanhThuVaSoThuePNop/ct30|180000000",Main+"KhaiThueTPPTTTDT/DoanhThuVaSoThuePNop/ct31|8100000",Main+"KhaiThueTPPTTTDT/ct30a|190000000",Main+"KhaiThueTPPTTTDT/ct32|190000000"});
   case "04GTGT-TT89-four-groups-rounding-M10-2026":return new HtkkDeclarationCasePlan(caseId,"Z3","3.0.9","2035","Gtgt04TT89Nckt309",new string[]{"101","101_1","Z3"},"month","21","2026","10","01/10/2026","31/10/2026",false,
    new string[0],new string[]{"01|Tờ khai"},
    "InterfaceTemplates/excel/04_GTGT_TT89_309.xls","2fbacc83c574ba75dfd660fa10345a397fdead41a2506dddc21e0fd69908149c","InterfaceTemplates/xml/04_GTGT_TT89_309.xml","86b9f16266026657e092f2aef8817a8ad64ac9c0812a6198601e83e4645f3e54",
    "Validate/04_GTGT_TT89_309.xsd","18dee33cbdc2df39453c8baa48153709c09718a262e25f52bee4e78d9174fa97",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,74,
    new string[]{"01|Z87|1234568","01|Z88|2500001","01|Z89|1000001","01|Z90|1555556","01|Q91|284567885","01|Z91|6290126","01|K103|284567885","01|K105|285567885"},
    new string[]{Main+"KhaiThueTPPTTTDT/ct21a|1000000",Main+"KhaiThueTPPTTTDT/ct21b|0",Main+"KhaiThueTPPTTTDT/PPhoiCCapHHoa/ct22|123456750",Main+"KhaiThueTPPTTTDT/PPhoiCCapHHoa/ct23|1234568",Main+"KhaiThueTPPTTTDT/DVuXDungKoBaoThauNVL/ct24|50000010",Main+"KhaiThueTPPTTTDT/DVuXDungKoBaoThauNVL/ct25|2500001",Main+"KhaiThueTPPTTTDT/HHoaXDungCoBaoThauNVL/ct26|33333350",Main+"KhaiThueTPPTTTDT/HHoaXDungCoBaoThauNVL/ct27|1000001",Main+"KhaiThueTPPTTTDT/HDongKDoanhKhac/ct28|77777775",Main+"KhaiThueTPPTTTDT/HDongKDoanhKhac/ct29|1555556",Main+"KhaiThueTPPTTTDT/DoanhThuVaSoThuePNop/ct30|284567885",Main+"KhaiThueTPPTTTDT/DoanhThuVaSoThuePNop/ct31|6290126",Main+"KhaiThueTPPTTTDT/ct30a|284567885",Main+"KhaiThueTPPTTTDT/ct32|285567885"});
   case "04GTGT-TT89-reduction-annex-M10-2026":return new HtkkDeclarationCasePlan(caseId,"Z3","3.0.9","2035","Gtgt04TT89Nckt309",new string[]{"101","101_1","Z3"},"month","21","2026","10","01/10/2026","31/10/2026",false,
    new string[]{"PL 204/2025/QH15"},new string[]{"01|Tờ khai","01_2|PL 204/2025/QH15"},
    "InterfaceTemplates/excel/04_GTGT_TT89_309.xls","2fbacc83c574ba75dfd660fa10345a397fdead41a2506dddc21e0fd69908149c","InterfaceTemplates/xml/04_GTGT_TT89_309.xml","86b9f16266026657e092f2aef8817a8ad64ac9c0812a6198601e83e4645f3e54",
    "Validate/04_GTGT_TT89_309.xsd","18dee33cbdc2df39453c8baa48153709c09718a262e25f52bee4e78d9174fa97",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,107,
    new string[]{"01|Q87|123458000","01|Z87|987663","01|Z88|2000001","01|Z89|800001","01|Z90|1244445","01|Z91|5032110","01|K105|285569135","01_2|G30|246914","01_2|G34|3","01_2|I11|246917","01_2|G36|1258028","01_2|D39|1258028"},
    new string[]{Main+"KhaiThueTPPTTTDT/ct21a|1000000",Main+"KhaiThueTPPTTTDT/ct21b|0",Main+"KhaiThueTPPTTTDT/PPhoiCCapHHoa/ct22|123458000",Main+"KhaiThueTPPTTTDT/PPhoiCCapHHoa/ct23|987663",Main+"KhaiThueTPPTTTDT/DVuXDungKoBaoThauNVL/ct24|50000010",Main+"KhaiThueTPPTTTDT/DVuXDungKoBaoThauNVL/ct25|2000001",Main+"KhaiThueTPPTTTDT/HHoaXDungCoBaoThauNVL/ct26|33333350",Main+"KhaiThueTPPTTTDT/HHoaXDungCoBaoThauNVL/ct27|800001",Main+"KhaiThueTPPTTTDT/HDongKDoanhKhac/ct28|77777775",Main+"KhaiThueTPPTTTDT/HDongKDoanhKhac/ct29|1244445",Main+"KhaiThueTPPTTTDT/DoanhThuVaSoThuePNop/ct30|284569135",Main+"KhaiThueTPPTTTDT/DoanhThuVaSoThuePNop/ct31|5032110",Main+"KhaiThueTPPTTTDT/ct30a|284569135",Main+"KhaiThueTPPTTTDT/ct32|285569135","HSoThueDTu/HSoKhaiThue/PLuc/PL_NQ204_GTGT/HH_DV_BanRaTrongKy/tongCongThueGTGTDuocGiam|1258028","HSoThueDTu/HSoKhaiThue/PLuc/PL_NQ204_GTGT/ChenhLech/ct9|1258028"});
   // Z5 01/GTGT TT89 3.0.9 (non-gating, HTKK 5.8.4 only): KieuKy 19 = SetLayoutToKhaiThangQuy, menu 101 -> 101_1 -> Z5 (after D1),
   // "Hoạt động sản xuất kinh doanh thông thường" and the CQT quản lý left as the dialog opens (0611 refuses another CQT for 00).
   // Sheet checks: [27] J58, [28] L58, [34] J65, [35] L65, [36] L69, [40a] L78, [40] L80, [41] L81, [43] L83 (XLS formulas);
   // XML checks: the tax leaves of CTieuTKhaiChinh from the independent Decimal oracle (htkk_declaration_web_cases.py). The
   // pinned 5.8.4 01_GTGT_TT89_309 xls/xml/xsd (TKhaiThue_DBHC.xsd as 5.8.1), no phụ lục, 104 leaves.
   case "01GTGT-TT89-zero-M10-2026":return new HtkkDeclarationCasePlan(caseId,"Z5","3.0.9","2032","Gtgt01TT89Nckt309",new string[]{"101","101_1","Z5"},"month","19","2026","10","01/10/2026","31/10/2026",false,
    new string[0],new string[]{"01|Tờ khai"},
    "InterfaceTemplates/excel/01_GTGT_TT89_309.xls","5370eb12c05cc2770e85ccc1bee7e6a7dc6138065f4c0fc4e0a418d3d9ee4585","InterfaceTemplates/xml/01_GTGT_TT89_309.xml","ba96834481a4b5b8a1c803572d10fafb669538402ed06f80a504c3212488638a",
    "Validate/01_GTGT_TT89_309.xsd","8481f7c98ca9e008742552bda4f7ecc814cb91d453584b179fdf2d7767d9da19",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,104,
    new string[]{"01|J58|0","01|L58|0","01|J65|0","01|L65|0","01|L69|0","01|L78|0","01|L80|0","01|L81|0","01|L83|0"},
    new string[]{Main+"ct21|0",Main+"ct22|0",Main+"GiaTriVaThueGTGTHHDVMuaVao/ct23|0",Main+"GiaTriVaThueGTGTHHDVMuaVao/ct24|0",Main+"ct25|0",Main+"ct26|0",Main+"HHDVBRaChiuThueGTGT/ct27|0",Main+"HHDVBRaChiuThueGTGT/ct28|0",Main+"ct29|0",Main+"HHDVBRaChiuTSuat5/ct30|0",Main+"HHDVBRaChiuTSuat5/ct31|0",Main+"HHDVBRaChiuTSuat10/ct32|0",Main+"HHDVBRaChiuTSuat10/ct33|0",Main+"ct32a|0",Main+"ct32b|0",Main+"ct34a|0",Main+"TongDThuVaThueGTGTHHDVBRa/ct34|0",Main+"TongDThuVaThueGTGTHHDVBRa/ct35|0",Main+"ct37|0",Main+"ct38|0",Main+"ct40a|0",Main+"ct40|0",Main+"ct41|0",Main+"ct43|0"});
   case "01GTGT-TT89-sale10-M10-2026":return new HtkkDeclarationCasePlan(caseId,"Z5","3.0.9","2032","Gtgt01TT89Nckt309",new string[]{"101","101_1","Z5"},"month","19","2026","10","01/10/2026","31/10/2026",false,
    new string[0],new string[]{"01|Tờ khai"},
    "InterfaceTemplates/excel/01_GTGT_TT89_309.xls","5370eb12c05cc2770e85ccc1bee7e6a7dc6138065f4c0fc4e0a418d3d9ee4585","InterfaceTemplates/xml/01_GTGT_TT89_309.xml","ba96834481a4b5b8a1c803572d10fafb669538402ed06f80a504c3212488638a",
    "Validate/01_GTGT_TT89_309.xsd","8481f7c98ca9e008742552bda4f7ecc814cb91d453584b179fdf2d7767d9da19",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,104,
    new string[]{"01|J58|1000000","01|L58|100000","01|J65|1000000","01|L65|100000","01|L69|100000","01|L78|100000","01|L80|100000","01|L81|0","01|L83|0"},
    new string[]{Main+"ct21|0",Main+"ct22|0",Main+"GiaTriVaThueGTGTHHDVMuaVao/ct23|0",Main+"GiaTriVaThueGTGTHHDVMuaVao/ct24|0",Main+"ct25|0",Main+"ct26|0",Main+"HHDVBRaChiuThueGTGT/ct27|1000000",Main+"HHDVBRaChiuThueGTGT/ct28|100000",Main+"ct29|0",Main+"HHDVBRaChiuTSuat5/ct30|0",Main+"HHDVBRaChiuTSuat5/ct31|0",Main+"HHDVBRaChiuTSuat10/ct32|1000000",Main+"HHDVBRaChiuTSuat10/ct33|100000",Main+"ct32a|0",Main+"ct32b|0",Main+"ct34a|0",Main+"TongDThuVaThueGTGTHHDVBRa/ct34|1000000",Main+"TongDThuVaThueGTGTHHDVBRa/ct35|100000",Main+"ct37|0",Main+"ct38|0",Main+"ct40a|100000",Main+"ct40|100000",Main+"ct41|0",Main+"ct43|0"});
   case "01GTGT-TT89-quarter-Q4-2026":return new HtkkDeclarationCasePlan(caseId,"Z5","3.0.9","2032","Gtgt01TT89Nckt309",new string[]{"101","101_1","Z5"},"quarter","19","2026","4","01/10/2026","31/12/2026",false,
    new string[0],new string[]{"01|Tờ khai"},
    "InterfaceTemplates/excel/01_GTGT_TT89_309.xls","5370eb12c05cc2770e85ccc1bee7e6a7dc6138065f4c0fc4e0a418d3d9ee4585","InterfaceTemplates/xml/01_GTGT_TT89_309.xml","ba96834481a4b5b8a1c803572d10fafb669538402ed06f80a504c3212488638a",
    "Validate/01_GTGT_TT89_309.xsd","8481f7c98ca9e008742552bda4f7ecc814cb91d453584b179fdf2d7767d9da19",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,104,
    new string[]{"01|J58|150000000","01|L58|10000000","01|J65|160000000","01|L65|10000000","01|L69|-10000000","01|L78|0","01|L80|0","01|L81|10000000","01|L83|10000000"},
    new string[]{Main+"ct21|0",Main+"ct22|0",Main+"GiaTriVaThueGTGTHHDVMuaVao/ct23|200000000",Main+"GiaTriVaThueGTGTHHDVMuaVao/ct24|20000000",Main+"ct25|20000000",Main+"ct26|10000000",Main+"HHDVBRaChiuThueGTGT/ct27|150000000",Main+"HHDVBRaChiuThueGTGT/ct28|10000000",Main+"ct29|0",Main+"HHDVBRaChiuTSuat5/ct30|100000000",Main+"HHDVBRaChiuTSuat5/ct31|5000000",Main+"HHDVBRaChiuTSuat10/ct32|50000000",Main+"HHDVBRaChiuTSuat10/ct33|5000000",Main+"ct32a|0",Main+"ct32b|0",Main+"ct34a|0",Main+"TongDThuVaThueGTGTHHDVBRa/ct34|160000000",Main+"TongDThuVaThueGTGTHHDVBRa/ct35|10000000",Main+"ct37|0",Main+"ct38|0",Main+"ct40a|0",Main+"ct40|0",Main+"ct41|10000000",Main+"ct43|10000000"});
   case "01GTGT-TT89-no-activity-M11-2026":return new HtkkDeclarationCasePlan(caseId,"Z5","3.0.9","2032","Gtgt01TT89Nckt309",new string[]{"101","101_1","Z5"},"month","19","2026","11","01/11/2026","30/11/2026",false,
    new string[0],new string[]{"01|Tờ khai"},
    "InterfaceTemplates/excel/01_GTGT_TT89_309.xls","5370eb12c05cc2770e85ccc1bee7e6a7dc6138065f4c0fc4e0a418d3d9ee4585","InterfaceTemplates/xml/01_GTGT_TT89_309.xml","ba96834481a4b5b8a1c803572d10fafb669538402ed06f80a504c3212488638a",
    "Validate/01_GTGT_TT89_309.xsd","8481f7c98ca9e008742552bda4f7ecc814cb91d453584b179fdf2d7767d9da19",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,104,
    new string[]{"01|J58|0","01|L58|0","01|J65|0","01|L65|0","01|L69|0","01|L78|0","01|L80|0","01|L81|6000000","01|L83|6000000"},
    new string[]{Main+"ct21|1",Main+"ct22|5000000",Main+"GiaTriVaThueGTGTHHDVMuaVao/ct23|0",Main+"GiaTriVaThueGTGTHHDVMuaVao/ct24|0",Main+"ct25|0",Main+"ct26|0",Main+"HHDVBRaChiuThueGTGT/ct27|0",Main+"HHDVBRaChiuThueGTGT/ct28|0",Main+"ct29|0",Main+"HHDVBRaChiuTSuat5/ct30|0",Main+"HHDVBRaChiuTSuat5/ct31|0",Main+"HHDVBRaChiuTSuat10/ct32|0",Main+"HHDVBRaChiuTSuat10/ct33|0",Main+"ct32a|0",Main+"ct32b|0",Main+"ct34a|0",Main+"TongDThuVaThueGTGTHHDVBRa/ct34|0",Main+"TongDThuVaThueGTGTHHDVBRa/ct35|0",Main+"ct37|0",Main+"ct38|1000000",Main+"ct40a|0",Main+"ct40|0",Main+"ct41|6000000",Main+"ct43|6000000"});
   case "01GTGT-TT89-full-M12-2026":return new HtkkDeclarationCasePlan(caseId,"Z5","3.0.9","2032","Gtgt01TT89Nckt309",new string[]{"101","101_1","Z5"},"month","19","2026","12","01/12/2026","31/12/2026",false,
    new string[0],new string[]{"01|Tờ khai"},
    "InterfaceTemplates/excel/01_GTGT_TT89_309.xls","5370eb12c05cc2770e85ccc1bee7e6a7dc6138065f4c0fc4e0a418d3d9ee4585","InterfaceTemplates/xml/01_GTGT_TT89_309.xml","ba96834481a4b5b8a1c803572d10fafb669538402ed06f80a504c3212488638a",
    "Validate/01_GTGT_TT89_309.xsd","8481f7c98ca9e008742552bda4f7ecc814cb91d453584b179fdf2d7767d9da19",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,104,
    new string[]{"01|J58|306000015","01|L58|25000002","01|J65|308700015","01|L65|25000002","01|L69|21000002","01|L78|18050002","01|L80|18010002","01|L81|0","01|L83|0"},
    new string[]{Main+"ct21|0",Main+"ct22|3000000",Main+"GiaTriVaThueGTGTHHDVMuaVao/ct23|40000000",Main+"GiaTriVaThueGTGTHHDVMuaVao/ct24|4000000",Main+"ct25|4000000",Main+"ct26|2000000",Main+"HHDVBRaChiuThueGTGT/ct27|306000015",Main+"HHDVBRaChiuThueGTGT/ct28|25000002",Main+"ct29|5000000",Main+"HHDVBRaChiuTSuat5/ct30|100000010",Main+"HHDVBRaChiuTSuat5/ct31|5000001",Main+"HHDVBRaChiuTSuat10/ct32|200000005",Main+"HHDVBRaChiuTSuat10/ct33|20000001",Main+"ct32a|1000000",Main+"ct32b|0",Main+"ct34a|700000",Main+"TongDThuVaThueGTGTHHDVBRa/ct34|308700015",Main+"TongDThuVaThueGTGTHHDVBRa/ct35|25000002",Main+"ct37|200000",Main+"ct38|100000",Main+"ct40a|18050002",Main+"ct40|18010002",Main+"ct41|0",Main+"ct43|0"});
   // With PL 204/2025/QH15 (Menu sheet 01_11 = workbook sheet 01_10, ticked in the period dialog; XML PLuc/PL_NQ142_GTGT): one
   // purchase row, two sale rows, so the sale totals sit on row 33 and [09] on D36. V19 = 1 and R61 = ROUND([32] x 10% - I9);
   // the import keeps [32]/[33] of the file (FinishImportXML runs no CellChange_9). 104 + 18 annex leaves.
   case "01GTGT-TT89-nq204-M12-2026":return new HtkkDeclarationCasePlan(caseId,"Z5","3.0.9","2032","Gtgt01TT89Nckt309",new string[]{"101","101_1","Z5"},"month","19","2026","12","01/12/2026","31/12/2026",false,
    new string[]{"PL 204/2025/QH15"},new string[]{"01|Tờ khai","01_10|PL 204/2025/QH15"},
    "InterfaceTemplates/excel/01_GTGT_TT89_309.xls","5370eb12c05cc2770e85ccc1bee7e6a7dc6138065f4c0fc4e0a418d3d9ee4585","InterfaceTemplates/xml/01_GTGT_TT89_309.xml","ba96834481a4b5b8a1c803572d10fafb669538402ed06f80a504c3212488638a",
    "Validate/01_GTGT_TT89_309.xsd","8481f7c98ca9e008742552bda4f7ecc814cb91d453584b179fdf2d7767d9da19",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,122,
    new string[]{"01|V19|1","01|R61|24000002","01|J58|300000025","01|L58|24000002","01|J65|300000025","01|L65|24000002","01|L69|20000002","01|L78|20000002","01|L80|20000002","01|L83|0","01_10|F20|4000000","01_10|D22|50000000","01_10|F22|4000000","01_10|G31|2000001","01_10|D33|300000025","01_10|G33|6000001","01_10|D36|2000001"},
    new string[]{Main+"ct21|0",Main+"ct22|0",Main+"GiaTriVaThueGTGTHHDVMuaVao/ct23|50000000",Main+"GiaTriVaThueGTGTHHDVMuaVao/ct24|4000000",Main+"ct25|4000000",Main+"ct26|0",Main+"HHDVBRaChiuThueGTGT/ct27|300000025",Main+"HHDVBRaChiuThueGTGT/ct28|24000002",Main+"ct29|0",Main+"HHDVBRaChiuTSuat5/ct30|0",Main+"HHDVBRaChiuTSuat5/ct31|0",Main+"HHDVBRaChiuTSuat10/ct32|300000025",Main+"HHDVBRaChiuTSuat10/ct33|24000002",Main+"ct32a|0",Main+"ct32b|0",Main+"ct34a|0",Main+"TongDThuVaThueGTGTHHDVBRa/ct34|300000025",Main+"TongDThuVaThueGTGTHHDVBRa/ct35|24000002",Main+"ct37|0",Main+"ct38|0",Main+"ct40a|20000002",Main+"ct40|20000002",Main+"ct41|0",Main+"ct43|0"});
   // Tháng 10/2026 copies (frmHTKKPeriod.CheckPeriod 0044 refuses tháng 12/2026 before 2026-12-01).
   case "01GTGT-TT89-full-M10-2026":return new HtkkDeclarationCasePlan(caseId,"Z5","3.0.9","2032","Gtgt01TT89Nckt309",new string[]{"101","101_1","Z5"},"month","19","2026","10","01/10/2026","31/10/2026",false,
    new string[0],new string[]{"01|Tờ khai"},
    "InterfaceTemplates/excel/01_GTGT_TT89_309.xls","5370eb12c05cc2770e85ccc1bee7e6a7dc6138065f4c0fc4e0a418d3d9ee4585","InterfaceTemplates/xml/01_GTGT_TT89_309.xml","ba96834481a4b5b8a1c803572d10fafb669538402ed06f80a504c3212488638a",
    "Validate/01_GTGT_TT89_309.xsd","8481f7c98ca9e008742552bda4f7ecc814cb91d453584b179fdf2d7767d9da19",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,104,
    new string[]{"01|J58|306000015","01|L58|25000002","01|J65|308700015","01|L65|25000002","01|L69|21000002","01|L78|18050002","01|L80|18010002","01|L81|0","01|L83|0"},
    new string[]{Main+"ct21|0",Main+"ct22|3000000",Main+"GiaTriVaThueGTGTHHDVMuaVao/ct23|40000000",Main+"GiaTriVaThueGTGTHHDVMuaVao/ct24|4000000",Main+"ct25|4000000",Main+"ct26|2000000",Main+"HHDVBRaChiuThueGTGT/ct27|306000015",Main+"HHDVBRaChiuThueGTGT/ct28|25000002",Main+"ct29|5000000",Main+"HHDVBRaChiuTSuat5/ct30|100000010",Main+"HHDVBRaChiuTSuat5/ct31|5000001",Main+"HHDVBRaChiuTSuat10/ct32|200000005",Main+"HHDVBRaChiuTSuat10/ct33|20000001",Main+"ct32a|1000000",Main+"ct32b|0",Main+"ct34a|700000",Main+"TongDThuVaThueGTGTHHDVBRa/ct34|308700015",Main+"TongDThuVaThueGTGTHHDVBRa/ct35|25000002",Main+"ct37|200000",Main+"ct38|100000",Main+"ct40a|18050002",Main+"ct40|18010002",Main+"ct41|0",Main+"ct43|0"});
   case "01GTGT-TT89-nq204-M10-2026":return new HtkkDeclarationCasePlan(caseId,"Z5","3.0.9","2032","Gtgt01TT89Nckt309",new string[]{"101","101_1","Z5"},"month","19","2026","10","01/10/2026","31/10/2026",false,
    new string[]{"PL 204/2025/QH15"},new string[]{"01|Tờ khai","01_10|PL 204/2025/QH15"},
    "InterfaceTemplates/excel/01_GTGT_TT89_309.xls","5370eb12c05cc2770e85ccc1bee7e6a7dc6138065f4c0fc4e0a418d3d9ee4585","InterfaceTemplates/xml/01_GTGT_TT89_309.xml","ba96834481a4b5b8a1c803572d10fafb669538402ed06f80a504c3212488638a",
    "Validate/01_GTGT_TT89_309.xsd","8481f7c98ca9e008742552bda4f7ecc814cb91d453584b179fdf2d7767d9da19",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,122,
    new string[]{"01|V19|1","01|R61|24000002","01|J58|300000025","01|L58|24000002","01|J65|300000025","01|L65|24000002","01|L69|20000002","01|L78|20000002","01|L80|20000002","01|L83|0","01_10|F20|4000000","01_10|D22|50000000","01_10|F22|4000000","01_10|G31|2000001","01_10|D33|300000025","01_10|G33|6000001","01_10|D36|2000001"},
    new string[]{Main+"ct21|0",Main+"ct22|0",Main+"GiaTriVaThueGTGTHHDVMuaVao/ct23|50000000",Main+"GiaTriVaThueGTGTHHDVMuaVao/ct24|4000000",Main+"ct25|4000000",Main+"ct26|0",Main+"HHDVBRaChiuThueGTGT/ct27|300000025",Main+"HHDVBRaChiuThueGTGT/ct28|24000002",Main+"ct29|0",Main+"HHDVBRaChiuTSuat5/ct30|0",Main+"HHDVBRaChiuTSuat5/ct31|0",Main+"HHDVBRaChiuTSuat10/ct32|300000025",Main+"HHDVBRaChiuTSuat10/ct33|24000002",Main+"ct32a|0",Main+"ct32b|0",Main+"ct34a|0",Main+"TongDThuVaThueGTGTHHDVBRa/ct34|300000025",Main+"TongDThuVaThueGTGTHHDVBRa/ct35|24000002",Main+"ct37|0",Main+"ct38|0",Main+"ct40a|20000002",Main+"ct40|20000002",Main+"ct41|0",Main+"ct43|0"});
   // With PL 01-6/GTGT (Menu sheet 01_6 = workbook 01_6_GTGT_CSSX, 01_6_2 = 01_6_GTGT_DVVT; ticked in the period dialog; XML
   // PLuc/Pluc_01_6_GTGT_CSSX / _DVVT): three rows (Hải Phòng, Thái Nguyên, Hải Phòng), so table 1 holds rows 22:24, the
   // per-province table rows 29:30 and the totals [19]/[23] row 35, [20]/[24] row 36. R19/S19 = 1 (SetCoPhuLucHayKhong) and
   // R20 = [19]+[20]+[23]+[24], S20 = [19]+[20], U20 = P20+R20+S20 (Header B78). FinishImportXML recomputes both tables
   // (TinhTongTheoTinhPl01_3 + TinhCot_17_21_Pl_01_6CSSX, TinhTongTheoTinhPl01_4). Column H is hidden: nothing to choose again.
   // 104 + 61 annex leaves.
   case "01GTGT-TT89-pl016-cssx-M10-2026":return new HtkkDeclarationCasePlan(caseId,"Z5","3.0.9","2032","Gtgt01TT89Nckt309",new string[]{"101","101_1","Z5"},"month","19","2026","10","01/10/2026","31/10/2026",false,
    new string[]{"01-6/GTGT (CSSX)"},new string[]{"01|Tờ khai","01_6_GTGT_CSSX|01-6/GTGT (CSSX)"},
    "InterfaceTemplates/excel/01_GTGT_TT89_309.xls","5370eb12c05cc2770e85ccc1bee7e6a7dc6138065f4c0fc4e0a418d3d9ee4585","InterfaceTemplates/xml/01_GTGT_TT89_309.xml","ba96834481a4b5b8a1c803572d10fafb669538402ed06f80a504c3212488638a",
    "Validate/01_GTGT_TT89_309.xsd","8481f7c98ca9e008742552bda4f7ecc814cb91d453584b179fdf2d7767d9da19",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,165,
    new string[]{"01|R19|1","01|R20|50000000","01|U20|50000000","01|J58|1000000000","01|L58|80000000","01|L80|80000000","01_6_GTGT_CSSX|N22|5000002","01_6_GTGT_CSSX|N23|3000002","01_6_GTGT_CSSX|N24|1","01_6_GTGT_CSSX|P22|0","01_6_GTGT_CSSX|N29|5000003","01_6_GTGT_CSSX|N30|3000002","01_6_GTGT_CSSX|N35|8000005","01_6_GTGT_CSSX|N36|41999995","01_6_GTGT_CSSX|Q35|0","01_6_GTGT_CSSX|Q36|0"},
    new string[]{Main+"ct21|0",Main+"ct22|0",Main+"GiaTriVaThueGTGTHHDVMuaVao/ct23|0",Main+"GiaTriVaThueGTGTHHDVMuaVao/ct24|0",Main+"ct25|0",Main+"ct26|0",Main+"HHDVBRaChiuThueGTGT/ct27|1000000000",Main+"HHDVBRaChiuThueGTGT/ct28|80000000",Main+"ct29|0",Main+"HHDVBRaChiuTSuat5/ct30|400000000",Main+"HHDVBRaChiuTSuat5/ct31|20000000",Main+"HHDVBRaChiuTSuat10/ct32|600000000",Main+"HHDVBRaChiuTSuat10/ct33|60000000",Main+"ct32a|0",Main+"ct32b|0",Main+"ct34a|0",Main+"TongDThuVaThueGTGTHHDVBRa/ct34|1000000000",Main+"TongDThuVaThueGTGTHHDVBRa/ct35|80000000",Main+"ct37|0",Main+"ct38|0",Main+"ct40a|80000000",Main+"ct40|80000000",Main+"ct41|0",Main+"ct43|0"});
   // Ratio branch of TinhCot_17_21_Pl_01_6CSSX ([06] < sum of the [17] formula): [17] = 0, [21] = ROUND([06] x [16] / [07]).
   case "01GTGT-TT89-pl016-cssx-ratio-M10-2026":return new HtkkDeclarationCasePlan(caseId,"Z5","3.0.9","2032","Gtgt01TT89Nckt309",new string[]{"101","101_1","Z5"},"month","19","2026","10","01/10/2026","31/10/2026",false,
    new string[]{"01-6/GTGT (CSSX)"},new string[]{"01|Tờ khai","01_6_GTGT_CSSX|01-6/GTGT (CSSX)"},
    "InterfaceTemplates/excel/01_GTGT_TT89_309.xls","5370eb12c05cc2770e85ccc1bee7e6a7dc6138065f4c0fc4e0a418d3d9ee4585","InterfaceTemplates/xml/01_GTGT_TT89_309.xml","ba96834481a4b5b8a1c803572d10fafb669538402ed06f80a504c3212488638a",
    "Validate/01_GTGT_TT89_309.xsd","8481f7c98ca9e008742552bda4f7ecc814cb91d453584b179fdf2d7767d9da19",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,165,
    new string[]{"01|R19|1","01|R20|70000001","01|U20|70000001","01|J58|8000000000","01|L58|700000000","01|L80|700000000","01_6_GTGT_CSSX|N22|0","01_6_GTGT_CSSX|P22|30000000","01_6_GTGT_CSSX|P23|15000000","01_6_GTGT_CSSX|P24|3333333","01_6_GTGT_CSSX|P29|33333333","01_6_GTGT_CSSX|P30|15000000","01_6_GTGT_CSSX|N35|0","01_6_GTGT_CSSX|N36|0","01_6_GTGT_CSSX|Q35|48333333","01_6_GTGT_CSSX|Q36|21666668"},
    new string[]{Main+"ct21|0",Main+"ct22|0",Main+"GiaTriVaThueGTGTHHDVMuaVao/ct23|0",Main+"GiaTriVaThueGTGTHHDVMuaVao/ct24|0",Main+"ct25|0",Main+"ct26|0",Main+"HHDVBRaChiuThueGTGT/ct27|8000000000",Main+"HHDVBRaChiuThueGTGT/ct28|700000000",Main+"ct29|0",Main+"HHDVBRaChiuTSuat5/ct30|2000000000",Main+"HHDVBRaChiuTSuat5/ct31|100000000",Main+"HHDVBRaChiuTSuat10/ct32|6000000000",Main+"HHDVBRaChiuTSuat10/ct33|600000000",Main+"ct32a|0",Main+"ct32b|0",Main+"ct34a|0",Main+"TongDThuVaThueGTGTHHDVBRa/ct34|8000000000",Main+"TongDThuVaThueGTGTHHDVBRa/ct35|700000000",Main+"ct37|0",Main+"ct38|0",Main+"ct40a|700000000",Main+"ct40|700000000",Main+"ct41|0",Main+"ct43|0"});
   // 01-6/GTGT (ĐTVT): [07] and [14] locked, [20] = [06] - [19].
   case "01GTGT-TT89-pl016-dtvt-M10-2026":return new HtkkDeclarationCasePlan(caseId,"Z5","3.0.9","2032","Gtgt01TT89Nckt309",new string[]{"101","101_1","Z5"},"month","19","2026","10","01/10/2026","31/10/2026",false,
    new string[]{"01-6/GTGT (ĐTVT)"},new string[]{"01|Tờ khai","01_6_GTGT_DVVT|01-6/GTGT (ĐTVT)"},
    "InterfaceTemplates/excel/01_GTGT_TT89_309.xls","5370eb12c05cc2770e85ccc1bee7e6a7dc6138065f4c0fc4e0a418d3d9ee4585","InterfaceTemplates/xml/01_GTGT_TT89_309.xml","ba96834481a4b5b8a1c803572d10fafb669538402ed06f80a504c3212488638a",
    "Validate/01_GTGT_TT89_309.xsd","8481f7c98ca9e008742552bda4f7ecc814cb91d453584b179fdf2d7767d9da19",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,165,
    new string[]{"01|S19|1","01|S20|30000000","01|U20|30000000","01|J58|600000000","01|L58|60000000","01|L80|60000000","01_6_GTGT_DVVT|N22|4000001","01_6_GTGT_DVVT|N23|3000002","01_6_GTGT_DVVT|N24|1","01_6_GTGT_DVVT|N29|4000002","01_6_GTGT_DVVT|N30|3000002","01_6_GTGT_DVVT|N35|7000004","01_6_GTGT_DVVT|N36|22999996"},
    new string[]{Main+"ct21|0",Main+"ct22|0",Main+"GiaTriVaThueGTGTHHDVMuaVao/ct23|0",Main+"GiaTriVaThueGTGTHHDVMuaVao/ct24|0",Main+"ct25|0",Main+"ct26|0",Main+"HHDVBRaChiuThueGTGT/ct27|600000000",Main+"HHDVBRaChiuThueGTGT/ct28|60000000",Main+"ct29|0",Main+"HHDVBRaChiuTSuat5/ct30|0",Main+"HHDVBRaChiuTSuat5/ct31|0",Main+"HHDVBRaChiuTSuat10/ct32|600000000",Main+"HHDVBRaChiuTSuat10/ct33|60000000",Main+"ct32a|0",Main+"ct32b|0",Main+"ct34a|0",Main+"TongDThuVaThueGTGTHHDVBRa/ct34|600000000",Main+"TongDThuVaThueGTGTHHDVBRa/ct35|60000000",Main+"ct37|0",Main+"ct38|0",Main+"ct40a|60000000",Main+"ct40|60000000",Main+"ct41|0",Main+"ct43|0"});
   // Hoạt động khác tỉnh ([09]-[11]): ThayDoiTinhTheoCQT2Cap unlocks rows 26-36 only when the period dialog's tỉnh differs from the
   // profile's maTinhNNT, and fills [11c] D32 / P32 (TenTinh / MaTinh) and [11a] D36 / P36 (TenXa / MaXa). The cell checks read the
   // two code cells P32 103 and P36 10309019; the Header names, [09] and [10] are compared by the whole-tree check. Needs a profile
   // whose CQT is 82500 (0611) and the period geography 103 / 10309019 / 82500 / 82500: Geography() below (registry taxpayerProfile /
   // periodLocation).
   case "01GTGT-TT89-other-province-M10-2026":return new HtkkDeclarationCasePlan(caseId,"Z5","3.0.9","2032","Gtgt01TT89Nckt309",new string[]{"101","101_1","Z5"},"month","19","2026","10","01/10/2026","31/10/2026",false,
    new string[0],new string[]{"01|Tờ khai"},
    "InterfaceTemplates/excel/01_GTGT_TT89_309.xls","5370eb12c05cc2770e85ccc1bee7e6a7dc6138065f4c0fc4e0a418d3d9ee4585","InterfaceTemplates/xml/01_GTGT_TT89_309.xml","ba96834481a4b5b8a1c803572d10fafb669538402ed06f80a504c3212488638a",
    "Validate/01_GTGT_TT89_309.xsd","8481f7c98ca9e008742552bda4f7ecc814cb91d453584b179fdf2d7767d9da19",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,104,
    new string[]{"01|P32|103","01|P36|10309019","01|J58|200000000","01|L58|20000000","01|J65|200000000","01|L65|20000000","01|L69|20000000","01|L78|20000000","01|L80|20000000"},
    new string[]{Main+"ct21|0",Main+"ct22|0",Main+"GiaTriVaThueGTGTHHDVMuaVao/ct23|0",Main+"GiaTriVaThueGTGTHHDVMuaVao/ct24|0",Main+"ct25|0",Main+"ct26|0",Main+"HHDVBRaChiuThueGTGT/ct27|200000000",Main+"HHDVBRaChiuThueGTGT/ct28|20000000",Main+"ct29|0",Main+"HHDVBRaChiuTSuat5/ct30|0",Main+"HHDVBRaChiuTSuat5/ct31|0",Main+"HHDVBRaChiuTSuat10/ct32|200000000",Main+"HHDVBRaChiuTSuat10/ct33|20000000",Main+"ct32a|0",Main+"ct32b|0",Main+"ct34a|0",Main+"TongDThuVaThueGTGTHHDVBRa/ct34|200000000",Main+"TongDThuVaThueGTGTHHDVBRa/ct35|20000000",Main+"ct37|0",Main+"ct38|0",Main+"ct40a|20000000",Main+"ct40|20000000",Main+"ct41|0",Main+"ct43|0"});
   // PL 01-8/GTGT (5%) (Menu sheet 01_9 = workbook 01_8_2, ticked "01-8/GTGT (5%)" in the period dialog; Main+"ct21|0",Main+"ct22|0",Main+"GiaTriVaThueGTGTHHDVMuaVao/ct23|3050000000",Main+"GiaTriVaThueGTGTHHDVMuaVao/ct24|305000000",Main+"ct25|305000000",Main+"ct26|0",Main+"HHDVBRaChiuThueGTGT/ct27|100000000",Main+"HHDVBRaChiuThueGTGT/ct28|5000000",Main+"ct29|0",Main+"HHDVBRaChiuTSuat5/ct30|100000000",Main+"HHDVBRaChiuTSuat5/ct31|5000000",Main+"HHDVBRaChiuTSuat10/ct32|0",Main+"HHDVBRaChiuTSuat10/ct33|0",Main+"ct32a|0",Main+"ct32b|0",Main+"ct34a|0",Main+"TongDThuVaThueGTGTHHDVBRa/ct34|100000000",Main+"TongDThuVaThueGTGTHHDVBRa/ct35|5000000",Main+"ct37|0",Main+"ct38|0",Main+"ct40a|0",Main+"ct40|0",Main+"ct41|300000000",Main+"ct43|0" PLuc/Pluc_01_8_2_GTGT):
   // [42] 300.000.000 with W19 = 1 (Header B199), one bảng 1 row (AF47 [5]) and one invoice (AI128 tổng [11]); mục 3 W251, W271,
   // W277/W278 and N359 soTienHoan are XLS formulas. Run on HTKK 5.8.5 (Header B155/B158 constant, B235/B237). 104 + 233 annex leaves (the
   // template's file row id="String" stays, as HTKK left it in run 46060840803).
   case "01GTGT-TT89-pl018-5pct-M10-2026":return new HtkkDeclarationCasePlan(caseId,"Z5","3.0.9","2032","Gtgt01TT89Nckt309",new string[]{"101","101_1","Z5"},"month","19","2026","10","01/10/2026","31/10/2026",false,
    new string[]{"01-8/GTGT (5%)"},new string[]{"01|Tờ khai","01_8_2|01-8/GTGT (5%)"},
    "InterfaceTemplates/excel/01_GTGT_TT89_309.xls","5370eb12c05cc2770e85ccc1bee7e6a7dc6138065f4c0fc4e0a418d3d9ee4585","InterfaceTemplates/xml/01_GTGT_TT89_309.xml","ba96834481a4b5b8a1c803572d10fafb669538402ed06f80a504c3212488638a",
    "Validate/01_GTGT_TT89_309.xsd","8481f7c98ca9e008742552bda4f7ecc814cb91d453584b179fdf2d7767d9da19",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,337,
    new string[]{"01|W19|1","01|L81|300000000","01|L82|300000000","01|L83|0","01_8_2|AF47|300000000","01_8_2|AI128|305000000","01_8_2|W251|100","01_8_2|W271|305000000","01_8_2|W277|300000000","01_8_2|W278|300000000","01_8_2|N359|300000000"},
    new string[]{Main+"ct21|0",Main+"ct22|0",Main+"GiaTriVaThueGTGTHHDVMuaVao/ct23|3050000000",Main+"GiaTriVaThueGTGTHHDVMuaVao/ct24|305000000",Main+"ct25|305000000",Main+"ct26|0",Main+"HHDVBRaChiuThueGTGT/ct27|100000000",Main+"HHDVBRaChiuThueGTGT/ct28|5000000",Main+"ct29|0",Main+"HHDVBRaChiuTSuat5/ct30|100000000",Main+"HHDVBRaChiuTSuat5/ct31|5000000",Main+"HHDVBRaChiuTSuat10/ct32|0",Main+"HHDVBRaChiuTSuat10/ct33|0",Main+"ct32a|0",Main+"ct32b|0",Main+"ct34a|0",Main+"TongDThuVaThueGTGTHHDVBRa/ct34|100000000",Main+"TongDThuVaThueGTGTHHDVBRa/ct35|5000000",Main+"ct37|0",Main+"ct38|0",Main+"ct40a|0",Main+"ct40|0",Main+"ct41|300000000",Main+"ct43|0"});
   // PL 01-8/GTGT (Xuất khẩu) (Menu 01_8 = workbook 01_8_1, ticked "01-8/GTGT (Xuất khẩu)"; XML PLuc/Pluc_01_8_1_GTGT): [42] 300.000.000 with
   // U19 = 1, [5] AF47 <= [41] (B126); bảng 2.3 with D161 ticked; mục 3 W252, W280, W284, W288 are XLS formulas. HTKK 5.8.5. 104 + 293 leaves.
   case "01GTGT-TT89-pl018-xk-M10-2026":return new HtkkDeclarationCasePlan(caseId,"Z5","3.0.9","2032","Gtgt01TT89Nckt309",new string[]{"101","101_1","Z5"},"month","19","2026","10","01/10/2026","31/10/2026",false,
    new string[]{"01-8/GTGT (Xuất khẩu)"},new string[]{"01|Tờ khai","01_8_1|01-8/GTGT (Xuất khẩu)"},
    "InterfaceTemplates/excel/01_GTGT_TT89_309.xls","5370eb12c05cc2770e85ccc1bee7e6a7dc6138065f4c0fc4e0a418d3d9ee4585","InterfaceTemplates/xml/01_GTGT_TT89_309.xml","ba96834481a4b5b8a1c803572d10fafb669538402ed06f80a504c3212488638a",
    "Validate/01_GTGT_TT89_309.xsd","8481f7c98ca9e008742552bda4f7ecc814cb91d453584b179fdf2d7767d9da19",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,397,
    new string[]{"01|U19|1","01|L81|305000000","01|L82|300000000","01|L83|5000000","01_8_1|AF47|300000000","01_8_1|AI128|305000000","01_8_1|W252|100","01_8_1|W280|305000000","01_8_1|W284|300000000","01_8_1|W288|300000000","01_8_1|N359|300000000"},
    new string[]{Main+"ct21|0",Main+"ct22|0",Main+"GiaTriVaThueGTGTHHDVMuaVao/ct23|3050000000",Main+"GiaTriVaThueGTGTHHDVMuaVao/ct24|305000000",Main+"ct25|305000000",Main+"ct26|0",Main+"HHDVBRaChiuThueGTGT/ct27|3000000000",Main+"HHDVBRaChiuThueGTGT/ct28|0",Main+"ct29|3000000000",Main+"HHDVBRaChiuTSuat5/ct30|0",Main+"HHDVBRaChiuTSuat5/ct31|0",Main+"HHDVBRaChiuTSuat10/ct32|0",Main+"HHDVBRaChiuTSuat10/ct33|0",Main+"ct32a|0",Main+"ct32b|0",Main+"ct34a|0",Main+"TongDThuVaThueGTGTHHDVBRa/ct34|3000000000",Main+"TongDThuVaThueGTGTHHDVBRa/ct35|0",Main+"ct37|0",Main+"ct38|0",Main+"ct40a|0",Main+"ct40|0",Main+"ct41|305000000",Main+"ct43|5000000"});
   // PL 01-8/GTGT (Giải thể, phá sản) (Menu 01_10 = workbook 01_8_3; XML PLuc/Pluc_01_8_3_GTGT): [42] 300.000.000 with X19 = 1, [5] AF47 =
   // 01!L82 (formula); quyết định giải thể N41/Z41; bảng 2.3 with D161 ticked. HTKK 5.8.5. 104 + 144 leaves.
   case "01GTGT-TT89-pl018-gt-M10-2026":return new HtkkDeclarationCasePlan(caseId,"Z5","3.0.9","2032","Gtgt01TT89Nckt309",new string[]{"101","101_1","Z5"},"month","19","2026","10","01/10/2026","31/10/2026",false,
    new string[]{"01-8/GTGT (Giải thể, phá sản)"},new string[]{"01|Tờ khai","01_8_3|01-8/GTGT (Giải thể, phá sản)"},
    "InterfaceTemplates/excel/01_GTGT_TT89_309.xls","5370eb12c05cc2770e85ccc1bee7e6a7dc6138065f4c0fc4e0a418d3d9ee4585","InterfaceTemplates/xml/01_GTGT_TT89_309.xml","ba96834481a4b5b8a1c803572d10fafb669538402ed06f80a504c3212488638a",
    "Validate/01_GTGT_TT89_309.xsd","8481f7c98ca9e008742552bda4f7ecc814cb91d453584b179fdf2d7767d9da19",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,248,
    new string[]{"01|X19|1","01|L81|305000000","01|L82|300000000","01|L83|5000000","01_8_3|AF47|300000000","01_8_3|AI128|305000000","01_8_3|N359|300000000"},
    new string[]{Main+"ct21|0",Main+"ct22|0",Main+"GiaTriVaThueGTGTHHDVMuaVao/ct23|3050000000",Main+"GiaTriVaThueGTGTHHDVMuaVao/ct24|305000000",Main+"ct25|305000000",Main+"ct26|0",Main+"HHDVBRaChiuThueGTGT/ct27|0",Main+"HHDVBRaChiuThueGTGT/ct28|0",Main+"ct29|0",Main+"HHDVBRaChiuTSuat5/ct30|0",Main+"HHDVBRaChiuTSuat5/ct31|0",Main+"HHDVBRaChiuTSuat10/ct32|0",Main+"HHDVBRaChiuTSuat10/ct33|0",Main+"ct32a|0",Main+"ct32b|0",Main+"ct34a|0",Main+"TongDThuVaThueGTGTHHDVBRa/ct34|0",Main+"TongDThuVaThueGTGTHHDVBRa/ct35|0",Main+"ct37|0",Main+"ct38|0",Main+"ct40a|0",Main+"ct40|0",Main+"ct41|305000000",Main+"ct43|5000000"});
   // PL 01-2/GTGT (Menu sheet 01_2 = workbook 01_2, ticked "01-2/GTGT" in the period dialog; XML PLuc/PLuc_01_2_GTGT): two plants
   // (TenNhaMay) of two rows each (DiaBanPhanBo). P19 = 1 (SetCoPhuLucHayKhong), P20 = IF(P19=1, 01_2!X46) = [14], U20 = P20 (Header
   // B78 <= [40]); 01_2!AJ7 = T46 = [13] (row 7, above the table). FinishImportXML runs SetLaiDongCon (T -> AO, J -> AP) and
   // TinhLaiTongCot10_12_PL01_2; X44 = ROUND(U44 x AO44 / 100, 0) on every row. Columns P and R are hidden: nothing to choose again.
   // 104 + 70 annex leaves.
   case "01GTGT-TT89-pl012-M10-2026":return new HtkkDeclarationCasePlan(caseId,"Z5","3.0.9","2032","Gtgt01TT89Nckt309",new string[]{"101","101_1","Z5"},"month","19","2026","10","01/10/2026","31/10/2026",false,
    new string[]{"01-2/GTGT"},new string[]{"01|Tờ khai","01_2|01-2/GTGT"},
    "InterfaceTemplates/excel/01_GTGT_TT89_309.xls","5370eb12c05cc2770e85ccc1bee7e6a7dc6138065f4c0fc4e0a418d3d9ee4585","InterfaceTemplates/xml/01_GTGT_TT89_309.xml","ba96834481a4b5b8a1c803572d10fafb669538402ed06f80a504c3212488638a",
    "Validate/01_GTGT_TT89_309.xsd","8481f7c98ca9e008742552bda4f7ecc814cb91d453584b179fdf2d7767d9da19",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,174,
    new string[]{"01|P19|1","01|P20|130000002","01|U20|130000002","01|J58|2000000000","01|L58|200000000","01|L80|200000000","01_2|AJ7|130000001"},
    new string[]{Main+"ct21|0",Main+"ct22|0",Main+"GiaTriVaThueGTGTHHDVMuaVao/ct23|0",Main+"GiaTriVaThueGTGTHHDVMuaVao/ct24|0",Main+"ct25|0",Main+"ct26|0",Main+"HHDVBRaChiuThueGTGT/ct27|2000000000",Main+"HHDVBRaChiuThueGTGT/ct28|200000000",Main+"ct29|0",Main+"HHDVBRaChiuTSuat5/ct30|0",Main+"HHDVBRaChiuTSuat5/ct31|0",Main+"HHDVBRaChiuTSuat10/ct32|2000000000",Main+"HHDVBRaChiuTSuat10/ct33|200000000",Main+"ct32a|0",Main+"ct32b|0",Main+"ct34a|0",Main+"TongDThuVaThueGTGTHHDVBRa/ct34|2000000000",Main+"TongDThuVaThueGTGTHHDVBRa/ct35|200000000",Main+"ct37|0",Main+"ct38|0",Main+"ct40a|200000000",Main+"ct40|200000000",Main+"ct41|0",Main+"ct43|0"});
   default:return null;
  }
 }

 // ---- Fixed original-entry plans (native-case mode original-entry-export) ----
 // The ONLY values the entry driver may type, in this order, into HTKK's own editors. A value is
 // never assigned to a cell, row, DTO or total: the original CellChange/formulas compute the rest.
 // Source (HTKK 5.8.1, pinned by metadata token and IL-code SHA-256 in htkk-oracle-baselines.json; the
 // raw-body SHA-256 prefixes listed below are the ones htkk_web records in data/htkk-descriptor-declarations.json):
 //  * 01_NTNN_NCCNN_TT89_309.xml: M_6/M_8 checkboxes (Controltype 2, nopThayNTNN/nopThayNCCNN);
 //    ThueNTNN data row 60, ThueNCCNN 78, ThueCNKCT 86 (DataLocationTemplateRowStart); row cells C ct1a,
 //    L ct1b (Controltype 87, SelectedValue BX = ct1b_ma), S ct3, W ct4 / AE ct6 (Controltype 14), Y ct5,
 //    AJ ct7, AN ct8, AZ ct10, BD ct11, BH ct12 (Controltype 16); AY_96 nguoiKy, AY_98 ngayKy (14).
 //  * frmWinToKhai.winFpSpread_ButtonClicked -> WinDoWorkEvent.ButtonClick -> ButtonClick_<sheet>
 //    (reflection, idxRow/idxCol); Ntnn01TT89Nckt309.ButtonClick_0 at (7,12) = M8 sets M6 := !M8 and
 //    calls LockUnlock(!M8, M8); LockUnlock locks C..BH (getCols) of ThueNTNN unless M6 and of
 //    ThueNCCNN/ThueCNKCT unless M8 via GeneralFunctions.LockUnLockColsInTable(deleteData=true), so the
 //    choice is made BEFORE any row value. (9,2) opens Bang_Ke_01NTNN_TT89.xls and is never clicked.
 //  * Control 87: WinSpreadProcess.WinInsertCombox builds a ComboBoxCellType whose Items are the
 //    DM_NNKD_NTNN.xml names in file order (DMNnkdNtnn); frmWinToKhai.winFpSpread_CellChange writes the
 //    key of the chosen name into the SelectedValue column BX. Items 01 (index 0) and 05 (index 4).
 //  * Ntnn01TT89Nckt309.CellChange_0 is empty: AV/BN/BR and the row-80/88 totals are XLS formulas.
 // U5 01/CNKD TT50 3.1.0 (mode web-xml-import-tick-reexport, HTKK 5.8.2 only). Source: TAX.HTKK.Business.dll 5.8.2
 // CnkdHkd01TT50Nckt310 and HTKK.exe 5.8.2, read statically (pins: htkk-oracle-baselines.json u5-310-tick-*).
 //  * The XML has no chonGiamThue (AJ) / ct17_soThueGiam (CD): the import leaves AJ clear and CD = 0. AutoBindData_0 ->
 //    lockUnLockA_TK keeps AJ open on rows whose CE (XLS formula of U, Z and BM) is > 0.
 //  * The import fills no child-row key column (BN/BK/CA/BS/BO/BP: no XML path). They are written for every row of the
 //    table only by SetCacDongCon from CellChange_0, i.e. by an original cell edit. The plan therefore edits L291 (ct11)
 //    (and L292) through the original editor twice, 0 and then the web value (a real change each time, so FpSpread.Change
 //    -> winFpSpread_CellChange -> WinDoWorkEvent.CellChange -> CellChange_0 runs; column L also copies L into U).
 //  * Release run 43136692872 stopped at the first tick (then AJ293 of the old row order): failure code 3, the cell was
 //    not an open unticked checkbox. The import leaves AJ locked on rows no original edit has touched (only CellChange_0
 //    of an edited row re-derives AJ.Locked = !(CE > 0) for that row). So every reduced row is edited (L291 and L292, 0
 //    then the web value) and ticked in sheet order, AJ291 then AJ292. PL 01 rows follow the sheet row order.
 //  * Rows 01, 04 (ticked) come before 02 (clear): daySangPLGiamThue does not advance past an unticked row (run
 //    43138236726, see the case plan), so no ticked row may follow an unticked one.
 //  * SPACE on AJ291 and AJ292 (CE > 0, open): ButtonClicked -> WinDoWorkEvent.ButtonClick -> ButtonClick_0
 //    -> daySangPLGiamThue: CopyTableToTable5(deleteDataOld) rebuilds PL 01 from the ticked rows (the imported PL 01
 //    rows are discarded), CD of each ticked row := PL 01 H (= G x 30%, XLS H20), then capNhatToKhai (CF = 0 without
 //    PL 03), so AE = CE - CD is HTKK's own result. AJ293 (group 02, not reduced, last row) stays clear.
 //  * Readbacks (diagnostic): BN = ma_diaDiemKD 00001 and CA = the profile MST on the rows, written by SetCacDongCon.
 // Z3 04/GTGT TT89 PL 01-1 (mode web-xml-import-tick-reexport, HTKK 5.8.2 only). Source: TAX.HTKK.Business.dll and HTKK.exe 5.8.2,
 // read statically (pins: htkk-oracle-baselines.json gtgt04tt89-582-*).
 //  * Run 43762065235 / 43772871198 (import only): every checked cell differed; all but [32] (K105 = [21a] alone) were empty or 0
 //    (declarationCellZeroMask 4031). Gtgt04TT89Nckt309.FinishImportXML loops over the PL 01-1 rows and sets column E (thuế
 //    suất, Controltype DC_124, SelectedValue I) to getTenThueSuat(column I) BEFORE TinhLaiThueSuat_PL01_1 copies E into an
 //    empty I; I is still empty after the import, so E is cleared, I stays empty and the SUMIF totals I9:L11, G30 = ROUND(D30 x
 //    (I30 - F30) / 100) and [22]..[32] fall to 0. (Gtgt04TT80Nckt274 runs that loop on sheet 1, which the TT80 case does not
 //    attach, and its PL 01-3 kept the rates: run 43742176321.)
 //  * The plan chooses the thuế suất of each sale row again through the original combobox editor, as a user corrects the
 //    imported annex: winFpSpread_CellChange writes the DC_124 code into I (DM_DUNG_CHUNG.xml items 1, 2, 3, 5: name = code),
 //    WinDoWorkEvent.CellChange runs CellChange_1, whose E branch (I not empty, no thu hộ) runs TinhLaiChiTieu22_den_28_TK for
 //    every rate and TinhLaiChiTieu23_25_27_29TheoPL01_1. Rows in sheet order 30..34 (1%, 5%, 3%, 2%, 1%); the cell checks of
 //    the case plan then read the recomputed sheet, and the export is compared leaf by leaf with the web XML.
 internal static HtkkDeclarationTickPlan ImportTick(string caseId){
  // 05-1/PBT (L7, Z8): Thuế tỉnh/CCT then CQT quản lý of each row through the original combobox editor (see the case plans).
  if(caseId=="05KK-PBT-two-provinces-Q3-2026"||caseId=="05KK-TT89-PBT-two-provinces-Q4-2026")return new HtkkDeclarationTickPlan(
   new string[]{"combo|01-1|I44|Thuế Thành phố Hà Nội|T44|10100","combo|01-1|J44|Thuế cơ sở 16 Thành phố Hà Nội|U44|10129",
    "combo|01-1|I45|Thuế Thành phố Hải Phòng|T45|10300","combo|01-1|J45|Thuế cơ sở 6 Thành phố Hải Phòng|U45|10309"},
   new string[0],new string[0],new string[0],HtkkOracleBaseline.PbtMethodPins());
  // Z3 PL 01-1 (see the comment above ImportTick): the thuế suất of each imported sale row chosen again.
  if(caseId=="04GTGT-TT89-reduction-annex-M10-2026")return new HtkkDeclarationTickPlan(
   new string[]{"combo|01_2|E30|1|I30|1","combo|01_2|E31|5|I31|5","combo|01_2|E32|3|I32|3","combo|01_2|E33|2|I33|2","combo|01_2|E34|1|I34|1"},
   new string[0],new string[0],new string[0],HtkkOracleBaseline.Gtgt04Tt89AnnexMethodPins());
  // PL 03 (see its case plan): the original L291 edit fills BN/CA (SetCacDongCon) and runs capNhatToKhai (CF from PL 03);
  // no checkbox is ticked. Same pinned methods (u5-310-tick-*: CellChange_0, SetCacDongCon, capNhatToKhai, ...).
  if(caseId=="01CNKD-TT50-310-pl03-two-groups-Q3-2026")return new HtkkDeclarationTickPlan(
   new string[]{"number|L291|0","number|L291|300000000"},new string[0],new string[0],
   new string[]{"BN291|00001","BN292|00001","CA291|9999999997","CA292|9999999997"},
   HtkkOracleBaseline.TickMethodPins());
  if(caseId!="01CNKD-TT50-310-pl01-three-groups-Q3-2026")return null;
  return new HtkkDeclarationTickPlan(
   new string[]{"number|L291|0","number|L291|300000000","number|L292|0","number|L292|200000000"},
   new string[]{"AJ291","AJ292"},new string[]{"AJ293"},
   new string[]{"BN291|00001","BN292|00001","BN293|00001","CA291|9999999997","CA292|9999999997","CA293|9999999997"},
   HtkkOracleBaseline.TickMethodPins());
 }
 internal static HtkkDeclarationEntryPlan Entry(string caseId){
  // The lần phát sinh case types the same rows with (6) AE = the period day (checkTKChinh E_27).
  bool occurrence=caseId=="01NTNN-NCCNN-occurrence-D20-10-2026";
  // HTKK 5.8.3 one-part cases: only the rows of one part II table are typed (II-I row 78, II-II row 86); the other table keeps
  // its template row untouched. Ntnn01TT89Nckt309.checkTKChinh (5.8.3) skips an empty part II table when the other has data.
  string skippedRow=caseId=="01NTNN-NCCNN-entry-part-II1-M10-2026"?"86":caseId=="01NTNN-NCCNN-entry-part-II2-M10-2026"?"78":null;
  // HTKK 5.8.5 case: both (4) ngày hợp đồng (W78, W86) typed as 31/12/2027 (checkTKChinh 5.8.5 no longer tests the date), with
  // the contract numbers HD-GL-007 / HD-GL-008.
  bool futureContract=caseId=="01NTNN-NCCNN-entry-future-contract-M10-2026";
  if(caseId!="01NTNN-NCCNN-entry-M10-2026"&&!occurrence&&skippedRow==null&&!futureContract)return null;
  HtkkDeclarationEntryPlan entry=new HtkkDeclarationEntryPlan("M8","M6","AY96","InterfaceIni/DM_NNKD_NTNN.xml","3aed1aea293f423271461892319217e33fc5dab32288dd708e6192a515802d17",
   // Table name | 1-based first data row | rows required | locked after the choice (1) or open (0).
   new string[]{"ThueNTNN|60|1|1","ThueNCCNN|78|1|0","ThueCNKCT|86|1|0"},
   new string[]{"C","L","M","S","W","Y","AE","AJ","AN","AZ","BD","BH"},
   // kind|cell|value; combo: kind|cell|list index|search key|item name|code cell|item code. The values are
   // the web input rows (design case 01NTNN-NCCNN-two-parts-M10-2026: NTNN_ROWS and the reviewed text allowlist).
   // date-optional: typed only when the original cell is open (the observed lock is reported).
   new string[]{
    "text|C78|NHA CUNG CAP NUOC NGOAI C - GIẢ LẬP","combo|L78|0|D|Dịch vụ, cho thuê máy móc thiết bị, bảo hiểm|BX78|01","text|S78|HD-GL-003","date|W78|01/09/2026","number|Y78|200000000",
    "date|AE78|15/10/2026","number|AJ78|200000000","number|AN78|5","number|AZ78|200000000","number|BD78|5",
    "text|C86|CA NHAN KHONG CU TRU D - GIẢ LẬP","combo|L86|4|H|Hoạt động kinh doanh khác|BX86|05","text|S86|HD-GL-004","date|W86|02/09/2026","number|Y86|100000000",
    "date|AE86|16/10/2026","number|AJ86|100000000","number|AN86|5","number|AZ86|100000000","number|BD86|2",
    "date-optional|AY98|27/10/2026"},
   // assembly (B = TAX.HTKK.Business, H = HTKK.exe) | type | method | token | IL bytes | IL-code SHA-256, for the
   // selected oracle (htkk-oracle-baselines.json). The 5.8.1 list is the reviewed one; raw-body SHA-256 prefixes
   // (htkk_web) in order: 363197ad 6ec04bdb 1ea954f3 aa17c417 cd2fd820 52ebc630 8b1f6212 10bc7699 d46d5971 4b1e82f3
   // 3c4f6dae 92fe05f4 0ef81f1a 0dd56a23. 5.8.2 renumbers 12 of them (same instructions); winFpSpread_CellChange
   // and ProcessCmdKey really changed, and their 5.8.2 bodies were reviewed against this plan (Z8 list entries and
   // control 110; big-data, D4/Z3 0585 cap and F6 last-row branches): status changed-reviewed, pinned for 5.8.2 only.
   HtkkOracleBaseline.EntryMethodPins());
  // Lần phát sinh: every (6) AE is typed as the period day (checkTKChinh E_27: TuNgay <= AE <= DenNgay, both the day).
  if(occurrence)for(int i=0;i<entry.Entries.Length;i++)if(entry.Entries[i].StartsWith("date|AE",StringComparison.Ordinal))entry.Entries[i]=entry.Entries[i].Substring(0,entry.Entries[i].LastIndexOf('|')+1)+Find(caseId).FromDate;
  if(futureContract)for(int i=0;i<entry.Entries.Length;i++){
   if(entry.Entries[i].StartsWith("date|W",StringComparison.Ordinal))entry.Entries[i]=entry.Entries[i].Substring(0,entry.Entries[i].LastIndexOf('|')+1)+"31/12/2027";
   // Its own contract numbers (HD-GL-007, HD-GL-008), so its web file can never pass as the entry case's.
   else if(entry.Entries[i]=="text|S78|HD-GL-003")entry.Entries[i]="text|S78|HD-GL-007";
   else if(entry.Entries[i]=="text|S86|HD-GL-004")entry.Entries[i]="text|S86|HD-GL-008";
  }
  if(skippedRow!=null){
   System.Collections.Generic.List<string> kept=new System.Collections.Generic.List<string>();
   foreach(string value in entry.Entries){string cell=value.Split('|')[1];if(cell.Substring(cell.Length-skippedRow.Length)!=skippedRow||Char.IsDigit(cell[cell.Length-skippedRow.Length-1]))kept.Add(value);}
   entry=new HtkkDeclarationEntryPlan(entry.ChoiceCell,entry.ExclusiveCell,entry.SignerCell,entry.CatalogueFile,entry.CatalogueSha256,entry.Tables,entry.LockColumns,kept.ToArray(),entry.MethodPins);
  }
  return entry;
 }
}
