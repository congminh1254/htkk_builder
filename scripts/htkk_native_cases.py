"""Trusted adapter/case metadata. Private plans cannot select arbitrary commands/drivers."""
import copy,importlib.util,json,pathlib,re
ROOT=pathlib.Path(__file__).parent
REGISTRY=json.loads((ROOT/'htkk-native-cases.json').read_text())
def check(value):
 if not value:raise ValueError('CASE_POLICY')
check(REGISTRY.get('format')=='htkk-native-case-registry-v1')
# Reviewed adapter identities only. A private source cannot add a producer or driver.
D1_DRIVER='gtgt-web-import-inspect'
KHBS_DRIVER='gtgt-amendment-khbs-inspect'
DECLARATION_DRIVER='declaration-web-import-inspect'
DECLARATION_PRODUCER='scripts/generate-htkk-declaration-reference.mjs'
_d1={'driver':D1_DRIVER,'menuId':'D1','xmlVersion':'2.8.3','periods':{'month':('10/2026',),'quarter':('4/2026',)}}
# Native-case input modes of the declaration driver: the original "Nhập từ XML" of the web XML, or
# typing a compiled fixed plan into the original grid (HtkkDeclarationCasePlans.Entry) when the
# original import cannot keep the form's data. The web XML is the comparison reference in both.
IMPORT_MODE='web-xml-import-reexport'
ENTRY_MODE='original-entry-export'
# The original import, then fixed original edits and checkbox ticks for grid-only inputs the XML cannot carry
# (HtkkDeclarationCasePlans.ImportTick), then the original export. Used by U5 3.1.0 (NQ 43 reduction tick AJ).
IMPORT_TICK_MODE='web-xml-import-tick-reexport'
def _declaration(menu,version,periods,annexes,mode=IMPORT_MODE):return {'producer':DECLARATION_PRODUCER,'privacyValidator':'declaration-v1','annexes':annexes,'driver':DECLARATION_DRIVER,'menuId':menu,'xmlVersion':version,'periods':periods,'mode':mode}
TRUSTED_ADAPTERS={
 '01-gtgt-2.8.3':{'producer':'scripts/generate-htkk-web-reference.mjs','privacyValidator':'gtgt-v1','annexes':[],**_d1},
 '01-gtgt-2.8.3-annex12':{'producer':'scripts/generate-htkk-web-annex12-reference.mjs','privacyValidator':'gtgt-annex12-v1','annexes':['01-2/GTGT'],**_d1},
 # 01-10/GTGT (giảm thuế GTGT NQ 204/2025/QH15, sheet 01_10, PL_NQ142_GTGT). Its only case runs on the HTKK 5.8.2
 # oracle (per-case htkkVersion): 5.8.2 accepts negative goods values there (htkk_web docs/PHU-LUC-01-10-GTGT.md).
 '01-gtgt-2.8.3-annex10':{'producer':'scripts/generate-htkk-web-annex10-reference.mjs','privacyValidator':'gtgt-annex10-v1','annexes':['01-10/GTGT'],**_d1},
 # Kê khai bổ sung lần 1 (KHBS, loaiTKhai B, PL01_KHBS + PL01_1_KHBS) on the HTKK 5.8.2 oracle, own driver
 # (KHBS-NATIVE-CASE.md): C0 zero Ghi, B1 reopen with a fixed ngày lập, original import of the web B1 file,
 # Tổng hợp KHBS, original export, whole tree. The only adapter whose unit has amendmentOrder 1.
 '01-gtgt-2.8.3-khbs':{'producer':'scripts/generate-htkk-web-khbs-reference.mjs','privacyValidator':'gtgt-khbs-v1','annexes':[],**_d1,'driver':KHBS_DRIVER,'amendmentOrder':1,
  # Case 2 (non-zero C0, 24 late days) is M09/2026: due 20/10/2026, before the fixed ngày lập 13/11/2026.
  # Case 12 (quarterly capture, 14 late days) is quý 3/2026: due 30/10/2026 (GetHanNopToKhai D1 KieuKy Q).
  'periods':{'month':('10/2026','09/2026'),'quarter':('3/2026',)}},
 # Bổ sung LẦN 2 (amendmentOrder 2) on the same driver: the previous version (bổ sung lần 1 of the case-1 web file) is
 # imported, summarised and saved in HTKK first (htkk_khbs_web_cases.prior_case), then B2 is opened, imported and summarised.
 # KHBS ORACLE CAPTURE with phụ lục 01-2/GTGT (C0 without annex, B1 adds the proven two-plant annex): non-gating.
 '01-gtgt-2.8.3-khbs-annex12':{'producer':'scripts/generate-htkk-web-khbs-reference.mjs','privacyValidator':'gtgt-khbs-v1','annexes':['01-2/GTGT'],**_d1,'driver':KHBS_DRIVER,'amendmentOrder':1,'periods':{'month':('10/2026',)}},
 # KHBS ORACLE CAPTURE of a CHANGED allocation, bổ sung lần 2: round 1 is the annex capture B1 (saved), round 2 B2 moves [11].
 '01-gtgt-2.8.3-khbs-annex12-lan2':{'producer':'scripts/generate-htkk-web-khbs-reference.mjs','privacyValidator':'gtgt-khbs-v1','annexes':['01-2/GTGT'],**_d1,'driver':KHBS_DRIVER,'amendmentOrder':2,'periods':{'month':('10/2026',)}},
 '01-gtgt-2.8.3-khbs-lan2':{'producer':'scripts/generate-htkk-web-khbs-reference.mjs','privacyValidator':'gtgt-khbs-v1','annexes':[],**_d1,'driver':KHBS_DRIVER,'amendmentOrder':2,'periods':{'month':('10/2026',),'quarter':('3/2026',)}},
 # Declaration families behind htkk_web DeclarationEngine (03/TNDN, BCTC, TNCN, 01/CNKD).
 # One reviewed menu, XML version, period and annex set per adapter; Menu.xml 5.8.1 pins.
 '03-tndn-2.9.4':_declaration('N8','2.9.4',{'year':('2025',)},['03-1A']),
 # A2 requires BCKQHĐKD and BCĐTK (HTKK CheckChonPlBctc/Validate_0 0485): 01-1 + 01-4.
 '133-b01a-dnn-2.3.2':_declaration('A2','2.3.2',{'year':('2025',)},['01-1','01-4']),
 # 78 requires exactly one LCTT at export (HTKK cmdExport_Click 0478): KQHĐSXKD + LCTTGT.
 '200-bctc-2.2.6':_declaration('78','2.2.6',{'year':('2025',)},['01-1','01-3']),
 # L7 monthly first declarations are refused from 4/2026 (HTKK 0682): quarter only.
 '05-kk-tncn-2.9.3':_declaration('L7','2.9.3',{'quarter':('3/2026',)},[]),
 # Z8 05/KK-TNCN TT89 3.0.9 exists only in HTKK 5.8.2 (Menu.xml 5.8.2 Z8, TncnKk05TT89Nckt309, StartDate 01/10/2026):
 # the adapter is pinned to that oracle. KieuKy 14 = SetLayoutToKhaiQuy (quarter only); CheckToKhaiBatDauCoHieuLuc
 # refuses quarters before 4/2026.
 '05-kk-tncn-tt89-3.0.9':{**_declaration('Z8','3.0.9',{'quarter':('4/2026',)},[]),'htkkVersion':'5.8.2'},
 # 05/KK-TNCN with bảng 05-1/PBT-KK-TNCN (Menu sheet 01-1, period dialog label 05-1/PBT-KK-TNCN) on the HTKK 5.8.2 oracle.
 # Thuế tỉnh/CCT (control 8, Path path_15) has no XML leaf and the import leaves it empty (Header B37 would refuse the
 # export): mode IMPORT_TICK_MODE with combo edits (HtkkDeclarationCasePlans.ImportTick) chooses it and then CQT quản lý.
 '05-kk-tncn-2.9.3-pbt':{**_declaration('L7','2.9.3',{'quarter':('3/2026',)},['01-1'],IMPORT_TICK_MODE),'htkkVersion':'5.8.2'},
 '05-kk-tncn-tt89-3.0.9-pbt':{**_declaration('Z8','3.0.9',{'quarter':('4/2026',)},['01-1'],IMPORT_TICK_MODE),'htkkVersion':'5.8.2'},
 '05-qtt-tncn-2.9.3':_declaration('B9','2.9.3',{'year':('2025',)},['05-1','05-3']),
 '01-cnkd-hkd-2.9.8':_declaration('U5','2.9.8',{'quarter':('3/2026',)},[]),
 # U5 3.1.0 exists only in HTKK 5.8.2 (Menu.xml VersionXML 3.1.0, CnkdHkd01TT50Nckt310): the adapter is pinned to that
 # oracle; the period dialog ticks sheet 01-4 "PL 01 43/2026/QH16" (NQ 43/2026/QH16, kỳ quý only: LoadPhuLucSpread).
 # The XML carries no chonGiamThue (AJ) / ct17_soThueGiam (CD): after the import AJ is clear and [17] = CE (runs 43127371885,
 # 43130173107, cell mask 40). Mode IMPORT_TICK_MODE: the original import, one original edit of L291 (fills the child-row keys
 # through CellChange_0 -> SetCacDongCon) and SPACE on AJ291/AJ293 (ButtonClick_0 -> daySangPLGiamThue rebuilds PL 01 and CD).
 '01-cnkd-hkd-3.1.0-pl01':{**_declaration('U5','3.1.0',{'quarter':('3/2026',)},['01-4'],IMPORT_TICK_MODE),'htkkVersion':'5.8.2'},
 # U5 3.1.0 with PL 03 (Mẫu 03, thuế phải nộp bù; sheet 01-5 "PL 03 43/2026/QH16"): the PL 03 rows are in the XML, the
 # thuế bù CF of the industry rows is grid-only (capNhatToKhai, run only from CellChange_0/CellChange_4/ButtonClick_0).
 # Mode IMPORT_TICK_MODE with edits only: one original edit of L291 runs CellChange_0 -> SetCacDongCon and capNhatToKhai.
 '01-cnkd-hkd-3.1.0-pl03':{**_declaration('U5','3.1.0',{'quarter':('3/2026',)},['01-5'],IMPORT_TICK_MODE),'htkkVersion':'5.8.2'},
 # B8 02/QTT-TNCN (non-gating): KieuKy 12 like B9; the import adds every annex (AddFullPLImportXML).
 '02-qtt-tncn-2.7.3':_declaration('B8','2.7.3',{'year':('2025',)},['02-1']),
 # B8 năm 2025 with hoàn trả qua chuyển khoản (chuyenKhoan, tenChuTaiKhoan, soTaiKhoan, maNganHang/tenNganHang) on the HTKK
 # 5.8.2 oracle (non-gating). Every transfer leaf is in the XML (G151 tỉnh only filters the bank list), and the import binds
 # text into the locked tên chủ tài khoản H149 (fpSpBindDataCell), so plain XML import → re-export (htkk_web plugin
 # qtt02-refund-transfer, docs/NGHIEP-VU-TNCN.md).
 # Năm 2025, not 2026: the period dialog opens a year period on Now.Year - 1 (LoadDefaultInfor); typing another year runs
 # mskYear_Leave -> UpdatePeriodByVerSion, which shows the B8 annex list (run 43551336755: declaration-period-inputs-not-matched).
 '02-qtt-tncn-2.7.3-refund':{**_declaration('B8','2.7.3',{'year':('2025',)},['02-1']),'htkkVersion':'5.8.2'},
 # I9 01/NTNN TT80 (non-gating): KieuKy 18 = SetLayoutToKhaiThangLanPhatSinh, month (Tháng is the default).
 # Lần phát sinh (period 'day', KieuKy 18 chkTKLanPS: GetPeriodInfo KieuKy D, TuNgay = DenNgay = kyKKhai = the day).
 # HTKK 5.8.2 ends I9 (Menu.xml EndDate 30/09/2026, GeneralFunctions.CheckToKhaiHetHieuLuc: month after 09/2026 and
 # day after 30/09/2026 refused), so the I9 cases use M09/2026 and 20/09/2026, valid on 5.8.1 and 5.8.2 alike.
 '01-ntnn-tt80-2.5.1':_declaration('I9','2.5.1',{'month':('09/2026',),'day':('20/09/2026',)},[]),
 # Y8 01/NTNN, NCCNN TT89: KieuKy 18 like I9; Menu.xml validity from 01/10/2026. The import-based adapter
 # 01-ntnn-nccnn-tt89-3.0.9 (case 01NTNN-NCCNN-two-parts-M10-2026) was removed after release 242: HTKK resets
 # the Y8 tables on import, so it could never match; the original-entry case below superseded it.
 # Y8 original entry (non-gating): HTKK 5.8.1 resets the Y8 tables on "Nhập từ XML" (AutoBindData_0 ->
 # LockUnlock -> LockUnLockColsInTable deleteData=true, release 238), so the same synthetic rows are
 # typed into the original grid and exported with the original export instead.
 '01-ntnn-nccnn-tt89-3.0.9-entry':_declaration('Y8','3.0.9',{'month':('10/2026',),'day':('20/10/2026',)},[],ENTRY_MODE),
 # J1 03/NTNN 3.0.8 (non-gating): KieuKy 18 like I9; FinishImportXML clears rate [9], so the case uses rate 0.
 '03-ntnn-tt80-3.0.8':_declaration('J1','3.0.8',{'month':('10/2026',),'day':('20/10/2026',)},[]),
 # D6/Y1 04/NTNN quyết toán (non-gating): KieuKy 22 = SetLayoutToKhaiTuNgayDenNgay, period 'range' (from-to
 # dates, GetPeriodInfo KieuKy D_D); Menu.xml sheet 01-1 (SheetName 02-2/NTNN) ticked in the period dialog.
 # D6 validity ends 01/10/2026 (CheckToKhaiHetHieuLuc), Y1 starts 01/07/2026 (CheckHieuLuc 0441).
 '04-ntnn-tt80-3.0.8':_declaration('D6','3.0.8',{'range':('01/01/2026-30/09/2026',)},['01-1']),
 '04-ntnn-tt89-3.0.9':_declaration('Y1','3.0.9',{'range':('01/07/2026-30/09/2026',)},['01-1']),
 # X9 02/NTNN quyết toán TT89 (non-gating): KieuKy 22 like Y1; annexes 01-1 (02-1/NTNN) and 01-2 (02-2/NTNN).
 '02-ntnn-tt89-3.0.9':_declaration('X9','3.0.9',{'range':('01/07/2026-30/09/2026',)},['01-1','01-2']),
 # C9 02/NTNN quyết toán TT80 (non-gating): KieuKy 22 like D6 (Menu.xml EndDate 01/10/2026); annexes as X9.
 '02-ntnn-tt80-2.5.1':_declaration('C9','2.5.1',{'range':('01/01/2026-30/09/2026',)},['01-1','01-2']),
}
ADAPTERS={a['adapterId']:a for a in REGISTRY['adapters']}
check(len(ADAPTERS)==len(REGISTRY['adapters']) and set(ADAPTERS)<=set(TRUSTED_ADAPTERS))
for a in ADAPTERS.values():
 trusted=TRUSTED_ADAPTERS[a['adapterId']]
 check(set(a)=={'adapterId','htkkVersion','menuId','xmlVersion','producer','driver','privacyValidator','profilePolicy'})
 check(a['driver']==trusted['driver'] and a['privacyValidator']==trusted['privacyValidator'] and a['profilePolicy']=='synthetic-9999999997-v1')
 check(a['producer']==trusted['producer'] and a['menuId']==trusted['menuId'] and a['xmlVersion']==trusted['xmlVersion'] and a['htkkVersion']==trusted.get('htkkVersion','5.8.1'))
# Per-case HTKK oracle (optional 'htkkVersion'). Absent = the default oracle (5.8.1), so a case without
# the field dispatches and reports exactly as before. When present it must name a reviewed NON-default
# baseline (one canonical spelling per version) and the case must not gate a release: release, Pages and
# scoped evidence stay on the default oracle (htkk_oracle.py keeps such runs on their own
# '@htkk582' status context, '-htkk582' output branch and immutable anchor).
_oracle_spec=importlib.util.spec_from_file_location('trusted_case_oracle',ROOT/'htkk_oracle.py');oracle=importlib.util.module_from_spec(_oracle_spec);_oracle_spec.loader.exec_module(oracle)
CASE_KEYS=frozenset({'caseId','producerCase','adapterId','format','stagingDirectory','inputBranch','outputBranch','statusContext','releaseGate','unit'})
def case_version(c):
 """The reviewed oracle version of one registry case; refuses anything else."""
 check(type(c)is dict and CASE_KEYS<=set(c)<=CASE_KEYS|{'htkkVersion'})
 if 'htkkVersion' not in c:return oracle.DEFAULT
 value=c['htkkVersion'];check(type(value)is str and value in oracle.VERSIONS and value!=oracle.DEFAULT and c['releaseGate']is False)
 return value
CASES={c['caseId']:c for c in REGISTRY['cases']}
check(0<len(CASES)<=256 and len(CASES)==len(REGISTRY['cases']))
for c in CASES.values():
 case_version(c)
 check(re.fullmatch('[A-Za-z0-9-]{1,100}',c['caseId']) and re.fullmatch('[a-z0-9-]{1,80}',c['producerCase']))
 a=ADAPTERS[c['adapterId']];u=c['unit']
 # An adapter of a later HTKK release (an XML version absent from 5.8.1) runs only on that oracle.
 check(a['htkkVersion']=='5.8.1' or case_version(c)==a['htkkVersion'])
 check(u['menuId']==a['menuId'] and u['adapterVersion']==a['xmlVersion'] and u['activityCode']=='00' and u['annexes']==TRUSTED_ADAPTERS[a['adapterId']]['annexes'] and type(u['amendmentOrder'])is int and u['amendmentOrder']==TRUSTED_ADAPTERS[a['adapterId']].get('amendmentOrder',0))
 periods=TRUSTED_ADAPTERS[a['adapterId']]['periods'];check(u['periodType'] in periods and u['periodValue'] in periods[u['periodType']])
 for key in ('stagingDirectory','inputBranch','outputBranch'):check(re.fullmatch('[a-zA-Z0-9-]{1,120}',c[key]))
 check(c['statusContext']=='htkk-native/'+c['producerCase'] and re.fullmatch('htkk-web-[a-z0-9-]+-input-v1',c['format']))
 # A candidate case is produced, retained and dispatched with its own status,
 # but cannot block or qualify a release until it is explicitly promoted.
 check(type(c['releaseGate'])is bool)
for key in ('producerCase','stagingDirectory','inputBranch','outputBranch','statusContext'):check(len({c[key]for c in CASES.values()})==len(CASES))
GATE_CASES=tuple(id for id,c in CASES.items() if c['releaseGate'])
CANDIDATE_CASES=tuple(id for id,c in CASES.items() if not c['releaseGate'])
check(GATE_CASES and list(CASES)[:len(GATE_CASES)]==list(GATE_CASES))
ANNEX12_CASES=tuple(id for id,c in CASES.items() if c['adapterId']=='01-gtgt-2.8.3-annex12')
ANNEX10_CASES=tuple(id for id,c in CASES.items() if c['adapterId']=='01-gtgt-2.8.3-annex10')
KHBS_CASES=tuple(id for id,c in CASES.items() if c['adapterId'] in ('01-gtgt-2.8.3-khbs','01-gtgt-2.8.3-khbs-lan2','01-gtgt-2.8.3-khbs-annex12','01-gtgt-2.8.3-khbs-annex12-lan2'))
check(all(not CASES[id]['releaseGate'] and case_version(CASES[id])=='5.8.2' for id in KHBS_CASES))
# Declaration-family cases use their own input/output file names, privacy allowlist and driver.
DECLARATION_CASES=tuple(id for id,c in CASES.items() if ADAPTERS[c['adapterId']]['driver']==DECLARATION_DRIVER)
check(all(not CASES[id]['releaseGate'] for id in DECLARATION_CASES))
# Declaration cases typed into the original grid; never a release gate.
DECLARATION_ENTRY_CASES=tuple(id for id in DECLARATION_CASES if TRUSTED_ADAPTERS[CASES[id]['adapterId']]['mode']==ENTRY_MODE)
# Declaration cases imported and then completed by fixed original edits/ticks; never a release gate.
DECLARATION_TICK_CASES=tuple(id for id in DECLARATION_CASES if TRUSTED_ADAPTERS[CASES[id]['adapterId']]['mode']==IMPORT_TICK_MODE)
check(set(t['mode'] for t in TRUSTED_ADAPTERS.values() if 'mode' in t)<={IMPORT_MODE,ENTRY_MODE,IMPORT_TICK_MODE})
def input_mode(case):check(case in DECLARATION_CASES);return TRUSTED_ADAPTERS[CASES[case]['adapterId']]['mode']
DRIVERS=tuple(sorted({a['driver'] for a in ADAPTERS.values()}))
def driver(case):check(case in CASES);return ADAPTERS[CASES[case]['adapterId']]['driver']
def htkk_version(case):check(case in CASES);return case_version(CASES[case])
# Status context of a dispatched case: the registry context, suffixed '@htkk582' for a 5.8.2 case.
def status_context(case):return oracle.status_context(CASES[case]['statusContext'],htkk_version(case))
def is_declaration(case):return case in DECLARATION_CASES
def policy(case):
 check(case in CASES);return copy.deepcopy(CASES[case])
def validate_plan(value):
 check(type(value)is dict and value.get('format')=='htkk-case-plan-v1' and value.get('htkkVersion')=='5.8.1' and value.get('nativeQualified')is False and value.get('filingEnabled')is False)
 rows=value.get('nativeCases');check(type(rows)is list);seen=set()
 for item in rows:
  check(type(item)is dict and item.get('caseId')in CASES and item['caseId']not in seen);seen.add(item['caseId']);c=CASES[item['caseId']];a=ADAPTERS[c['adapterId']]
  for key in ('adapterId','producerCase','unit'):check(item.get(key)==c[key])
  check(item.get('producer')==a['producer'] and item.get('profilePolicy')==a['profilePolicy'] and item.get('coverageGranted')is False and re.fullmatch('[a-f0-9]{64}',item.get('descriptorFingerprint','')))
 # A source plan registers either every trusted case or, before the source
 # registers candidates, exactly the release-gate cases. Nothing else.
 check(seen==set(CASES) or seen==set(GATE_CASES))
 return value
