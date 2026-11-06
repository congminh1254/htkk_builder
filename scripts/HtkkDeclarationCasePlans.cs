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
  if(periodKind!="month"&&periodKind!="quarter"&&periodKind!="year")throw new InvalidOperationException();
 }
}

internal static class HtkkDeclarationCasePlans {
 internal const string XmldsigSha256="c3b5160be1852606d10f6928e0b214d418f8dd418667cb2fb88fec31e4e6f56d";
 private const string TKhaiThue="TKhaiThue.xsd",TKhaiThueSha256="8f451719355b5a6247f65a34a37584b4a0c7f7cc81a568e1033d08b8fe9b8c1d";
 private const string TKhaiThueDbhc="TKhaiThue_DBHC.xsd",TKhaiThueDbhcSha256="aba7f2acbc9332caaf3eb2da9a081a3d876ddc7813d6230921da48c775460011";
 private const string WorkbookService="Công cụ Kê khai — bản nháp",CnkdService="Công cụ Kê khai — bản nháp";
 private const string Main="HSoThueDTu/HSoKhaiThue/CTieuTKhaiChinh/";
 // Fixed case IDs, in registry order. Kept identical to htkk-native-cases.json (tested offline).
 internal static readonly string[] CaseIds=new string[]{"03TNDN-profit20-Y2025","BCTC133-B01a-basic-Y2025","BCTC200-LT-basic-Y2025","05KK-withheld-Q3-2026","05QTT-two-employees-Y2025","01CNKD-TT50-revenue-two-groups-Q3-2026"};
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
    "Validate/05_QTT_TNCN_TT80_293.xsd","0556354bbe766d6ff75ab4fccb456ea7bd99c6915ad20628149f170bda389635",TKhaiThueDbhc,TKhaiThueDbhcSha256,WorkbookService,149,
    new string[]{"05-1|AE24|148000000","05-1|AE25|24000000","05|U49|2","05|U51|1","05|U61|500000000","05|U71|300000000","05|U74|12000000","05|U89|1","05|U92|10000000","05|U94|0","05|U95|2000000"},
    new string[]{Main+"mst_cu|9999999997",Main+"NVuKhauTruThue/ct16|2",Main+"NVuKhauTruThue/ct17|2",Main+"NVuKhauTruThue/ct18|1",Main+"NVuKhauTruThue/ct19|1",Main+"NVuKhauTruThue/ct23|500000000",Main+"NVuKhauTruThue/ct24|500000000",Main+"NVuKhauTruThue/ct28|300000000",Main+"NVuKhauTruThue/ct29|300000000",Main+"NVuKhauTruThue/ct31|12000000",Main+"NVuKhauTruThue/ct32|12000000",Main+"NVuQToanThay/ct35|1",Main+"NVuQToanThay/ct36|12000000",Main+"NVuQToanThay/ct38|6520000",Main+"NVuQToanThay/ct40|0",Main+"NVuQToanThay/ct41|5480000"});
   // U5 01/CNKD TT50: KieuKy 21 = SetLayoutToKhaiThangQuyLanPhatSinh (quarter), geography panel.
   case "01CNKD-TT50-revenue-two-groups-Q3-2026":return new HtkkDeclarationCasePlan(caseId,"U5","2.9.8","1266","CnkdHkd01TT50Nckt298",new string[]{"101","101_37","U5"},"quarter","21","2026","3","01/07/2026","30/09/2026",false,
    new string[0],new string[]{"01|Tờ khai"},
    "InterfaceTemplates/excel/01_CNKD_HKD_TT50_298.xls","b2afa8514b64ed1a4c9e63ab724a15c0b7fe4dcb5ff77d10277e982381c98ce0","InterfaceTemplates/xml/01_CNKD_HKD_TT50_298.xml","79873aaa4d9dcb31207e9083ffc0f1a72d3cb995d8ee688c198c6871f4e18578",
    "Validate/01_CNKD_HKD_TT50_298.xsd","016f97894b9a1472282ba342349b654b5bfd0f5e4ebba8ab5cbe176134adb31d",TKhaiThue,TKhaiThueSha256,CnkdService,261,
    new string[0],
    new string[]{Main+"KhaiThueGTGTTNCN/SoThueConPhaiNopCT20/soThueGTGT_ct14|10000000",Main+"KhaiThueGTGTTNCN/SoThueConPhaiNopCT20/soThueTNCN_ct17|4500000",Main+"HoTroThongTinNopThue/tongTienCT47|14500000"});
   default:return null;
  }
 }
}
