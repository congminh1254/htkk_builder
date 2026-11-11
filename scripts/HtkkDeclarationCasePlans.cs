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
  if(periodKind=="day"&&(kieuKy!="18"||fromDate.Length!=10||fromDate!=toDate||fromDate[2]!='/'||fromDate[5]!='/'||fromDate.Substring(6)!=year||periodNumber!=""))throw new InvalidOperationException();
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

internal static class HtkkDeclarationCasePlans {
 internal const string XmldsigSha256="c3b5160be1852606d10f6928e0b214d418f8dd418667cb2fb88fec31e4e6f56d";
 private const string TKhaiThue="TKhaiThue.xsd",TKhaiThueSha256="8f451719355b5a6247f65a34a37584b4a0c7f7cc81a568e1033d08b8fe9b8c1d";
 private const string TKhaiThueDbhc="TKhaiThue_DBHC.xsd",TKhaiThueDbhcSha256="aba7f2acbc9332caaf3eb2da9a081a3d876ddc7813d6230921da48c775460011";
 private const string WorkbookService="Công cụ Kê khai",CnkdService="Công cụ Kê khai";
 private const string Main="HSoThueDTu/HSoKhaiThue/CTieuTKhaiChinh/";
 // Fixed case IDs, in registry order. Kept identical to htkk-native-cases.json (tested offline).
 internal static readonly string[] CaseIds=new string[]{"03TNDN-profit20-Y2025","BCTC133-B01a-basic-Y2025","BCTC200-LT-basic-Y2025","05KK-withheld-Q3-2026","05QTT-two-employees-Y2025","01CNKD-TT50-revenue-two-groups-Q3-2026","02QTT-dependants-Y2025","01NTNN-two-contractors-M09-2026","03NTNN-no-rate-M10-2026","01NTNN-NCCNN-entry-M10-2026","04NTNN-TT80-one-subcontractor-2026","04NTNN-TT89-one-subcontractor-2026","02NTNN-TT89-two-annexes-2026","02NTNN-TT80-two-annexes-2026","01NTNN-occurrence-D20-09-2026","01NTNN-NCCNN-occurrence-D20-10-2026","03NTNN-occurrence-D20-10-2026"};
 // Original frmHTKKPeriod.SetLayoutToKhaiNamTuThangDenThang (KieuKy 12) calls
 // ShowDetailpnVT2_PhuLucKeKhai(false) for every menu except 97/H4/C8: the annex list is
 // bound (LoadPhuLucSpread) but hidden, so a user cannot tick it. The driver only observes
 // that hidden list's original defaults (run 42218301225: axfpsPhuLuc not visible for B9).
 internal static bool AnnexPanelHidden(HtkkDeclarationCasePlan plan){return plan!=null&&plan.KieuKy=="12"&&plan.MenuId!="97"&&plan.MenuId!="H4"&&plan.MenuId!="C8";}
 // Original frmWinToKhai.cmdImportXML_Click: MenuID in "~B8~37~33~B9~N7~W1" → AddFullPLImportXML,
 // which adds every sheet of the menu before the XML is read.
 // A2 BCTC TT133 (BctcB01aTt133Nckt232, no ExportXML override): no control of 133_B01A_01_THTC_232
 // is bound to TKhaiThue/ngayKy, so WinDoWorkEvent.UpdateObjectValue never sets TTinChung.ngayKy and
 // WinFnProcess.BindToKhaiInfoToTTinChung leaves it at DateTime.Now; xmlExportTTinChung writes it
 // as yyyy-MM-dd. 78 copies ngayLap (ExportXML_0) and the other cases bind it to a cell.
 internal static string[] ExportDatePaths(HtkkDeclarationCasePlan plan){return plan!=null&&plan.MenuId=="A2"?new string[]{"HSoThueDTu/HSoKhaiThue/TTinChung/TTinTKhaiThue/TKhaiThue/ngayKy"}:new string[0];}
 internal static bool ImportAddsAllAnnexes(HtkkDeclarationCasePlan plan){return plan!=null&&"~B8~37~33~B9~N7~W1~".IndexOf("~"+plan.MenuId+"~",StringComparison.Ordinal)>=0;}
 internal static HtkkDeclarationCasePlan Find(string caseId){
  switch(caseId){
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
   // U5 01/CNKD TT50: KieuKy 21 = SetLayoutToKhaiThangQuyLanPhatSinh (quarter), geography panel.
   case "01CNKD-TT50-revenue-two-groups-Q3-2026":return new HtkkDeclarationCasePlan(caseId,"U5","2.9.8","1266","CnkdHkd01TT50Nckt298",new string[]{"101","101_37","U5"},"quarter","21","2026","3","01/07/2026","30/09/2026",false,
    new string[0],new string[]{"01|Tờ khai"},
    "InterfaceTemplates/excel/01_CNKD_HKD_TT50_298.xls","b2afa8514b64ed1a4c9e63ab724a15c0b7fe4dcb5ff77d10277e982381c98ce0","InterfaceTemplates/xml/01_CNKD_HKD_TT50_298.xml","79873aaa4d9dcb31207e9083ffc0f1a72d3cb995d8ee688c198c6871f4e18578",
    "Validate/01_CNKD_HKD_TT50_298.xsd","016f97894b9a1472282ba342349b654b5bfd0f5e4ebba8ab5cbe176134adb31d",TKhaiThue,TKhaiThueSha256,CnkdService,261,
    new string[0],
    new string[]{Main+"KhaiThueGTGTTNCN/SoThueConPhaiNopCT20/soThueGTGT_ct14|10000000",Main+"KhaiThueGTGTTNCN/SoThueConPhaiNopCT20/soThueTNCN_ct17|4500000",Main+"HoTroThongTinNopThue/tongTienCT47|14500000"});
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
   case "04NTNN-TT89-one-subcontractor-2026":return new HtkkDeclarationCasePlan(caseId,"Y1","3.0.9","2015","Ntnn04TT89Nckt309",new string[]{"101","101_8","Y1"},"range","22","2026","","01/07/2026","30/09/2026",false,
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
 internal static HtkkDeclarationEntryPlan Entry(string caseId){
  // The lần phát sinh case types the same rows with (6) AE = the period day (checkTKChinh E_27).
  bool occurrence=caseId=="01NTNN-NCCNN-occurrence-D20-10-2026";
  if(caseId!="01NTNN-NCCNN-entry-M10-2026"&&!occurrence)return null;
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
  return entry;
 }
}
