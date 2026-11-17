"""Design-only registry of descriptor native cases (TNCN 05/KK, 05/QTT, 02/QTT; NTNN 01/NTNN TT80).

Kept separate from htkk-native-cases.json on purpose: no Windows driver exists for these
menus yet, so nothing here may be produced, dispatched or counted as a release gate.
The validator fails closed on any field that would make a case dispatchable.
"""
import copy,json,pathlib,re
ROOT=pathlib.Path(__file__).parent
def check(value):
 if not value:raise ValueError('DESCRIPTOR_CASE_POLICY')
TRUSTED={
 '05-kk-tncn-2.9.3':{'menuId':'L7','businessClass':'TncnKk05TT80','xmlVersion':'2.9.3','schemaId':'Validate/05_KK_TNCN_TT80_293.xsd','annexes':[],'mode':'web-xml-import-reexport','periodTypes':{'month','quarter'}},
 # 05/KK-TNCN TT89 (Z8 3.0.9): exists only in HTKK 5.8.2, so the adapter and its cases name that oracle (htkkVersion);
 # KieuKy 14 = SetLayoutToKhaiQuy, quarter only.
 '05-kk-tncn-tt89-3.0.9':{'menuId':'Z8','businessClass':'TncnKk05TT89','xmlVersion':'3.0.9','schemaId':'Validate/05_KK_TNCN_TT89_309.xsd','annexes':[],'mode':'web-xml-import-reexport','periodTypes':{'quarter'},'htkkVersion':'5.8.2'},
 '05-qtt-tncn-2.9.3':{'menuId':'B9','businessClass':'TncnQtt05TT80','xmlVersion':'2.9.3','schemaId':'Validate/05_QTT_TNCN_TT80_293.xsd','annexes':['05-1','05-2','05-3'],'mode':'web-xml-import-reexport','periodTypes':{'year'}},
 '02-qtt-tncn-2.7.3':{'menuId':'B8','businessClass':'TncnQtt02TT80','xmlVersion':'2.7.3','schemaId':'Validate/02_QTT_TNCN_TT80_273.xsd','annexes':['02-1'],'mode':'original-entry-export','periodTypes':{'year'}},
 # 01/NTNN TT80 (I9): main-sheet contractor table only, KieuKy 18 monthly or lần phát sinh ('day', dd/MM/yyyy).
 '01-ntnn-tt80-2.5.1':{'menuId':'I9','businessClass':'Ntnn01TT80','xmlVersion':'2.5.1','schemaId':'Validate/01_NTNN_TT80_251.xsd','annexes':[],'mode':'web-xml-import-reexport','periodTypes':{'month','day'}},
 # 01/NTNN, NCCNN TT89 (Y8): three main-sheet tables, part chosen by nopThayNTNN/nopThayNCCNN.
 '01-ntnn-nccnn-tt89-3.0.9':{'menuId':'Y8','businessClass':'Ntnn01TT89','xmlVersion':'3.0.9','schemaId':'Validate/01_NTNN_NCCNN_TT89_309.xsd','annexes':[],'mode':'web-xml-import-reexport','periodTypes':{'month'}},
 # 03/NTNN (J1, 3.0.8): one ThueNTNN table, TNDN only; the import clears rate [9] (FinishImportXML).
 # Y8 original entry: the same declaration typed into the original grid (the import resets the tables).
 '01-ntnn-nccnn-tt89-3.0.9-entry':{'menuId':'Y8','businessClass':'Ntnn01TT89','xmlVersion':'3.0.9','schemaId':'Validate/01_NTNN_NCCNN_TT89_309.xsd','annexes':[],'mode':'original-entry-export','periodTypes':{'month','day'}},
 '03-ntnn-tt80-3.0.8':{'menuId':'J1','businessClass':'Ntnn03TT80','xmlVersion':'3.0.8','schemaId':'Validate/03_NTNN_TT80_308.xsd','annexes':[],'mode':'web-xml-import-reexport','periodTypes':{'month','day'}},
 # 04/NTNN quyết toán (D6 TT80 3.0.8, Y1 TT89 3.0.9): KieuKy 22 from-to dates ('range'), annex 01-1 (sheet 01-2).
 '04-ntnn-tt80-3.0.8':{'menuId':'D6','businessClass':'Ntnn04TT80','xmlVersion':'3.0.8','schemaId':'Validate/04_NTNN_TT80_308.xsd','annexes':['01-1'],'mode':'web-xml-import-reexport','periodTypes':{'range'}},
 '04-ntnn-tt89-3.0.9':{'menuId':'Y1','businessClass':'Ntnn04TT89','xmlVersion':'3.0.9','schemaId':'Validate/04_NTNN_TT89_309.xsd','annexes':['01-1'],'mode':'web-xml-import-reexport','periodTypes':{'range'}},
 # 02/NTNN quyết toán TT89 (X9 3.0.9): KieuKy 22 ('range'), annexes 01-1 (02-1/NTNN) and 01-2 (02-2/NTNN).
 '02-ntnn-tt89-3.0.9':{'menuId':'X9','businessClass':'Ntnn02TT89','xmlVersion':'3.0.9','schemaId':'Validate/02_NTNN_TT89_309.xsd','annexes':['01-1','01-2'],'mode':'web-xml-import-reexport','periodTypes':{'range'}},
 # 02/NTNN quyết toán TT80 (C9 2.5.1): KieuKy 22 ('range', Menu.xml EndDate 01/10/2026), annexes as X9.
 # 05/KK-TNCN with bảng 05-1/PBT-KK-TNCN (L7 / Z8, HTKK 5.8.2 oracle): the import, then Thuế tỉnh/CCT and CQT quản lý
 # chosen in the original grid (Thuế tỉnh/CCT has no XML leaf).
 '05-kk-tncn-2.9.3-pbt':{'menuId':'L7','businessClass':'TncnKk05TT80','xmlVersion':'2.9.3','schemaId':'Validate/05_KK_TNCN_TT80_293.xsd','annexes':['01-1'],'mode':'web-xml-import-tick-reexport','periodTypes':{'quarter'},'htkkVersion':'5.8.2'},
 '05-kk-tncn-tt89-3.0.9-pbt':{'menuId':'Z8','businessClass':'TncnKk05TT89','xmlVersion':'3.0.9','schemaId':'Validate/05_KK_TNCN_TT89_309.xsd','annexes':['01-1'],'mode':'web-xml-import-tick-reexport','periodTypes':{'quarter'},'htkkVersion':'5.8.2'},
 # 02/QTT-TNCN năm 2025 with hoàn trả qua chuyển khoản (HTKK 5.8.2 oracle): plain import → re-export; a refund needs [44] > 0.
 '02-qtt-tncn-2.7.3-refund':{'menuId':'B8','businessClass':'TncnQtt02TT80','xmlVersion':'2.7.3','schemaId':'Validate/02_QTT_TNCN_TT80_273.xsd','annexes':['02-1'],'mode':'web-xml-import-reexport','periodTypes':{'year'},'htkkVersion':'5.8.2'},
 # 01/TTS TT40 (G7 2.8.3, HTKK 5.8.2 oracle): KieuKy 42; cá nhân trực tiếp khai năm with 01-1/BK-TTS, tổ chức khai thay
 # tháng/quý with 01-2/BK-TTS (CheckChonLoaiNopThue). No zero case: a table needs a contract row and a payment period.
 '01-tts-tt40-2.8.3-bk1':{'menuId':'G7','businessClass':'Tts01TT40','xmlVersion':'2.8.3','schemaId':'Validate/01_TTS_TT40_283.xsd','annexes':['01-1'],'mode':'web-xml-import-reexport','periodTypes':{'year'},'htkkVersion':'5.8.2'},
 '01-tts-tt40-2.8.3-bk2':{'menuId':'G7','businessClass':'Tts01TT40','xmlVersion':'2.8.3','schemaId':'Validate/01_TTS_TT40_283.xsd','annexes':['01-2'],'mode':'web-xml-import-reexport','periodTypes':{'month','quarter'},'htkkVersion':'5.8.2'},
 # 01/TCKT TT89 (Y7 3.0.9, HTKK 5.8.1 oracle): KieuKy 21; one bảng kê per tờ khai (frmHTKKPeriod axfpsPhuLuc_ButtonClicked):
 # 01/BK-KTHTKD (01-1, tháng/quý) or 02/BK-KTBĐS (01-2, tháng/lần phát sinh). No zero case: Header B18-B26/B30 require a row
 # with name, MST and amounts, and the period dialog refuses a tờ khai without bảng kê (0670).
 '01-tckt-tt89-3.0.9-bk1':{'menuId':'Y7','businessClass':'Tckt01TT89','xmlVersion':'3.0.9','schemaId':'Validate/01_TCKT_TT89_309.xsd','annexes':['01-1'],'mode':'web-xml-import-reexport','periodTypes':{'month','quarter'}},
 '01-tckt-tt89-3.0.9-bk2':{'menuId':'Y7','businessClass':'Tckt01TT89','xmlVersion':'3.0.9','schemaId':'Validate/01_TCKT_TT89_309.xsd','annexes':['01-2'],'mode':'web-xml-import-reexport','periodTypes':{'month','day'}},
 # 01/TCKT TT89 3.1.0 (Y7 of HTKK 5.8.2/5.8.3, Tckt01TT89Nckt310, HTKK 5.8.2 oracle): the same bảng kê adapters, and 01/BK-KTHTKD
 # with PL 01-3 "PL NQ 43/2026/QH16" (rows of the ticked bảng kê rows; it needs a ticked row with TNCN > 0, so no zero case).
 '01-tckt-tt89-3.1.0-bk1':{'menuId':'Y7','businessClass':'Tckt01TT89','xmlVersion':'3.1.0','schemaId':'Validate/01_TCKT_TT89_310.xsd','annexes':['01-1'],'mode':'web-xml-import-reexport','periodTypes':{'month','quarter'},'htkkVersion':'5.8.2'},
 '01-tckt-tt89-3.1.0-bk2':{'menuId':'Y7','businessClass':'Tckt01TT89','xmlVersion':'3.1.0','schemaId':'Validate/01_TCKT_TT89_310.xsd','annexes':['01-2'],'mode':'web-xml-import-reexport','periodTypes':{'month','day'},'htkkVersion':'5.8.2'},
 '01-tckt-tt89-3.1.0-bk1-pl013':{'menuId':'Y7','businessClass':'Tckt01TT89','xmlVersion':'3.1.0','schemaId':'Validate/01_TCKT_TT89_310.xsd','annexes':['01-1','01-3'],'mode':'web-xml-import-reexport','periodTypes':{'month','quarter'},'htkkVersion':'5.8.2'},
 # 04/GTGT TT80 (D4 2.7.4, HTKK 5.8.2 oracle): KieuKy 21, tháng/quý đến 09/2026; the annex adapter ticks PL 01-3 (giảm thuế
 # NQ 142/174/204), which needs at least one sale row with a rate, so it has no zero case.
 '04-gtgt-tt80-2.7.4':{'menuId':'D4','businessClass':'Gtgt04TT80','xmlVersion':'2.7.4','schemaId':'Validate/04_GTGT_TT80_274.xsd','annexes':[],'mode':'web-xml-import-reexport','periodTypes':{'month','quarter'},'htkkVersion':'5.8.2'},
 '04-gtgt-tt80-2.7.4-pl013':{'menuId':'D4','businessClass':'Gtgt04TT80','xmlVersion':'2.7.4','schemaId':'Validate/04_GTGT_TT80_274.xsd','annexes':['01-3'],'mode':'web-xml-import-reexport','periodTypes':{'quarter'},'htkkVersion':'5.8.2'},
 # 04/GTGT TT89 (Z3 3.0.9, HTKK 5.8.2 only): KieuKy 21, tháng/quý từ 10/2026; the annex adapter ticks PL 01-1 (NQ 204/2025),
 # which needs a sale row with a rate, so it has no zero case.
 '04-gtgt-tt89-3.0.9':{'menuId':'Z3','businessClass':'Gtgt04TT89','xmlVersion':'3.0.9','schemaId':'Validate/04_GTGT_TT89_309_htkk582.xsd','annexes':[],'mode':'web-xml-import-reexport','periodTypes':{'month','quarter'},'htkkVersion':'5.8.2'},
 '04-gtgt-tt89-3.0.9-pl011':{'menuId':'Z3','businessClass':'Gtgt04TT89','xmlVersion':'3.0.9','schemaId':'Validate/04_GTGT_TT89_309_htkk582.xsd','annexes':['01-1'],'mode':'web-xml-import-reexport','periodTypes':{'month'},'htkkVersion':'5.8.2'},
 '02-ntnn-tt80-2.5.1':{'menuId':'C9','businessClass':'Ntnn02TT80','xmlVersion':'2.5.1','schemaId':'Validate/02_NTNN_TT80_251.xsd','annexes':['01-1','01-2'],'mode':'web-xml-import-reexport','periodTypes':{'range'}},
}
# 05-1/PBT adapters: the annex needs at least one row with loại, tỉnh, xã, Thuế tỉnh/CCT and CQT quản lý (Header B35-B39),
# so there is no zero declaration with the annex.
# The 02/QTT refund adapter: a refund needs số thuế nộp thừa [44] > 0 and [46] > 0, so no zero declaration either.
NO_ZERO_CASE=frozenset({'04-ntnn-tt89-3.0.9','02-ntnn-tt89-3.0.9','05-kk-tncn-2.9.3-pbt','05-kk-tncn-tt89-3.0.9-pbt','02-qtt-tncn-2.7.3-refund','01-tts-tt40-2.8.3-bk1','01-tts-tt40-2.8.3-bk2','04-gtgt-tt80-2.7.4-pl013','04-gtgt-tt89-3.0.9-pl011','01-tckt-tt89-3.0.9-bk1','01-tckt-tt89-3.0.9-bk2','01-tckt-tt89-3.1.0-bk1','01-tckt-tt89-3.1.0-bk2','01-tckt-tt89-3.1.0-bk1-pl013'})
def validate(value):
 check(type(value) is dict and set(value)=={'format','htkkVersion','status','dispatchable','reason','producer','profilePolicy','adapters','cases'})
 check(value['format']=='htkk-descriptor-native-case-design-v1' and value['htkkVersion']=='5.8.1')
 # Promotion requires a reviewed Windows driver; until then the design cannot dispatch.
 check(value['status']=='design-only' and value['dispatchable'] is False and isinstance(value['reason'],str) and value['reason'])
 check(value['producer']=='scripts/generate-htkk-descriptor-reference.mjs' and value['profilePolicy']=='synthetic-9999999997-v1')
 adapters={}
 for a in value['adapters']:
  check(type(a) is dict and a.get('adapterId') in TRUSTED and a['adapterId'] not in adapters)
  trusted=TRUSTED[a['adapterId']]
  # 'htkkVersion' appears exactly on the adapters of a later HTKK release (an XML version absent from 5.8.1).
  check(set(a)=={'adapterId','menuId','businessClass','xmlVersion','schemaId','annexes','mode'}|({'htkkVersion'} if 'htkkVersion' in trusted else set()))
  check(a.get('htkkVersion')==trusted.get('htkkVersion'))
  for key in ('menuId','businessClass','xmlVersion','schemaId','annexes','mode'):check(a[key]==trusted[key])
  adapters[a['adapterId']]=a
 check(set(adapters)==set(TRUSTED))
 seen=set();per={}
 for c in value['cases']:
  check(type(c) is dict and set(c)<= {'caseId','adapterId','htkkVersion','releaseGate','unit','expectedLeaves','expectedRows','question'} and {'caseId','adapterId','releaseGate','unit','expectedLeaves'}<=set(c))
  check(re.fullmatch('[A-Za-z0-9-]{1,100}',c['caseId']) and c['caseId'] not in seen);seen.add(c['caseId'])
  check(c['adapterId'] in adapters and c['releaseGate'] is False)
  t=TRUSTED[c['adapterId']];u=c['unit']
  # A case of such an adapter names the same oracle; no other case names one.
  check(c.get('htkkVersion')==t.get('htkkVersion') and (('htkkVersion' in c)==('htkkVersion' in t)))
  check(type(u) is dict and set(u)=={'menuId','adapterVersion','periodType','periodValue','activityCode','annexes','amendmentOrder'})
  check(u['menuId']==t['menuId'] and u['adapterVersion']==t['xmlVersion'] and u['activityCode']=='00' and type(u['amendmentOrder']) is int and u['amendmentOrder']==0)
  check(u['periodType'] in t['periodTypes'])
  _day=r'(0[1-9]|[12]\d|3[01])/(0[1-9]|1[0-2])/20\d\d'
  check(re.fullmatch(r'(0[1-9]|1[0-2])/20\d\d',u['periodValue']) if u['periodType']=='month' else re.fullmatch(r'[1-4]/20\d\d',u['periodValue']) if u['periodType']=='quarter' else re.fullmatch(_day+'-'+_day,u['periodValue']) if u['periodType']=='range' else re.fullmatch(_day,u['periodValue']) if u['periodType']=='day' else re.fullmatch(r'20\d\d',u['periodValue']))
  check(type(u['annexes']) is list and len(set(u['annexes']))==len(u['annexes']) and set(u['annexes'])<=set(t['annexes']))
  leaves=c['expectedLeaves'];check(type(leaves) is dict and 0<len(leaves)<=64)
  for name,text in leaves.items():
   # A bare name must be unique under CTieuTKhaiChinh; 'Group/leaf' names one leaf of a repeated name (04/NTNN rows).
   check(re.fullmatch(r'[A-Za-z][A-Za-z0-9_.]{0,40}(/[A-Za-z][A-Za-z0-9_]{0,40})?',name) and isinstance(text,str))
   # Only the synthetic profile MST or plain non-negative integers: no names or free text.
   check(text=='9999999997' and name=='mst_cu' or re.fullmatch(r'0|[1-9][0-9]{0,15}',text))
  rows=c.get('expectedRows',{});check(type(rows) is dict and all(re.fullmatch(r'(PLuc_[A-Za-z0-9_]+/[A-Za-z]+(_[A-Za-z]+)?(/[A-Za-z]+)?|PL[0-9]{2}_[0-9]_NTNN/[A-Za-z]+/[A-Za-z]+|PL_NQ[0-9]{2,3}_GTGT/[A-Za-z_]+/[A-Za-z]+)',k) and type(v) is int and 1<=v<=50 for k,v in rows.items()))
  check(bool(rows)==bool(u['annexes']))
  per.setdefault(c['adapterId'],[]).append(c)
 # Each adapter needs a zero case and at least one case with amounts. The TT89 settlements have no zero
 # declaration: Y1 Header B42 (IF(01!AJ36=0,0,1), flag Y) blocks the export when [5] chênh lệch = 0, X9 Header
 # B55 (IF(AND(01!AO39=0,01!AO40=0),0,1), flag Y) when both tax differences are 0.
 for adapter,cases in per.items():
  check(adapter in NO_ZERO_CASE or any(all(v in ('0','9999999997') for v in c['expectedLeaves'].values()) for c in cases))
  check(any(any(v not in ('0','9999999997') for v in c['expectedLeaves'].values()) for c in cases))
 check(set(per)==set(TRUSTED))
 return copy.deepcopy(value)
DESIGN=validate(json.loads((ROOT/'htkk-descriptor-native-cases.json').read_text()))
CASE_IDS=tuple(c['caseId'] for c in DESIGN['cases'])
