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
 '05-qtt-tncn-2.9.3':{'menuId':'B9','businessClass':'TncnQtt05TT80','xmlVersion':'2.9.3','schemaId':'Validate/05_QTT_TNCN_TT80_293.xsd','annexes':['05-1','05-2','05-3'],'mode':'web-xml-import-reexport','periodTypes':{'year'}},
 '02-qtt-tncn-2.7.3':{'menuId':'B8','businessClass':'TncnQtt02TT80','xmlVersion':'2.7.3','schemaId':'Validate/02_QTT_TNCN_TT80_273.xsd','annexes':['02-1'],'mode':'original-entry-export','periodTypes':{'year'}},
 # 01/NTNN TT80 (I9): main-sheet contractor table only, KieuKy 18 monthly.
 '01-ntnn-tt80-2.5.1':{'menuId':'I9','businessClass':'Ntnn01TT80','xmlVersion':'2.5.1','schemaId':'Validate/01_NTNN_TT80_251.xsd','annexes':[],'mode':'web-xml-import-reexport','periodTypes':{'month'}},
 # 01/NTNN, NCCNN TT89 (Y8): three main-sheet tables, part chosen by nopThayNTNN/nopThayNCCNN.
 '01-ntnn-nccnn-tt89-3.0.9':{'menuId':'Y8','businessClass':'Ntnn01TT89','xmlVersion':'3.0.9','schemaId':'Validate/01_NTNN_NCCNN_TT89_309.xsd','annexes':[],'mode':'web-xml-import-reexport','periodTypes':{'month'}},
 # 03/NTNN (J1, 3.0.8): one ThueNTNN table, TNDN only; the import clears rate [9] (FinishImportXML).
 # Y8 original entry: the same declaration typed into the original grid (the import resets the tables).
 '01-ntnn-nccnn-tt89-3.0.9-entry':{'menuId':'Y8','businessClass':'Ntnn01TT89','xmlVersion':'3.0.9','schemaId':'Validate/01_NTNN_NCCNN_TT89_309.xsd','annexes':[],'mode':'original-entry-export','periodTypes':{'month'}},
 '03-ntnn-tt80-3.0.8':{'menuId':'J1','businessClass':'Ntnn03TT80','xmlVersion':'3.0.8','schemaId':'Validate/03_NTNN_TT80_308.xsd','annexes':[],'mode':'web-xml-import-reexport','periodTypes':{'month'}},
 # 04/NTNN quyết toán (D6 TT80 3.0.8, Y1 TT89 3.0.9): KieuKy 22 from-to dates ('range'), annex 01-1 (sheet 01-2).
 '04-ntnn-tt80-3.0.8':{'menuId':'D6','businessClass':'Ntnn04TT80','xmlVersion':'3.0.8','schemaId':'Validate/04_NTNN_TT80_308.xsd','annexes':['01-1'],'mode':'web-xml-import-reexport','periodTypes':{'range'}},
 '04-ntnn-tt89-3.0.9':{'menuId':'Y1','businessClass':'Ntnn04TT89','xmlVersion':'3.0.9','schemaId':'Validate/04_NTNN_TT89_309.xsd','annexes':['01-1'],'mode':'web-xml-import-reexport','periodTypes':{'range'}},
 # 02/NTNN quyết toán TT89 (X9 3.0.9): KieuKy 22 ('range'), annexes 01-1 (02-1/NTNN) and 01-2 (02-2/NTNN).
 '02-ntnn-tt89-3.0.9':{'menuId':'X9','businessClass':'Ntnn02TT89','xmlVersion':'3.0.9','schemaId':'Validate/02_NTNN_TT89_309.xsd','annexes':['01-1','01-2'],'mode':'web-xml-import-reexport','periodTypes':{'range'}},
}
NO_ZERO_CASE=frozenset({'04-ntnn-tt89-3.0.9','02-ntnn-tt89-3.0.9'})
def validate(value):
 check(type(value) is dict and set(value)=={'format','htkkVersion','status','dispatchable','reason','producer','profilePolicy','adapters','cases'})
 check(value['format']=='htkk-descriptor-native-case-design-v1' and value['htkkVersion']=='5.8.1')
 # Promotion requires a reviewed Windows driver; until then the design cannot dispatch.
 check(value['status']=='design-only' and value['dispatchable'] is False and isinstance(value['reason'],str) and value['reason'])
 check(value['producer']=='scripts/generate-htkk-descriptor-reference.mjs' and value['profilePolicy']=='synthetic-9999999997-v1')
 adapters={}
 for a in value['adapters']:
  check(type(a) is dict and set(a)=={'adapterId','menuId','businessClass','xmlVersion','schemaId','annexes','mode'} and a['adapterId'] in TRUSTED and a['adapterId'] not in adapters)
  trusted=TRUSTED[a['adapterId']]
  for key in ('menuId','businessClass','xmlVersion','schemaId','annexes','mode'):check(a[key]==trusted[key])
  adapters[a['adapterId']]=a
 check(set(adapters)==set(TRUSTED))
 seen=set();per={}
 for c in value['cases']:
  check(type(c) is dict and set(c)<= {'caseId','adapterId','releaseGate','unit','expectedLeaves','expectedRows','question'} and {'caseId','adapterId','releaseGate','unit','expectedLeaves'}<=set(c))
  check(re.fullmatch('[A-Za-z0-9-]{1,100}',c['caseId']) and c['caseId'] not in seen);seen.add(c['caseId'])
  check(c['adapterId'] in adapters and c['releaseGate'] is False)
  t=TRUSTED[c['adapterId']];u=c['unit']
  check(type(u) is dict and set(u)=={'menuId','adapterVersion','periodType','periodValue','activityCode','annexes','amendmentOrder'})
  check(u['menuId']==t['menuId'] and u['adapterVersion']==t['xmlVersion'] and u['activityCode']=='00' and type(u['amendmentOrder']) is int and u['amendmentOrder']==0)
  check(u['periodType'] in t['periodTypes'])
  _day=r'(0[1-9]|[12]\d|3[01])/(0[1-9]|1[0-2])/20\d\d'
  check(re.fullmatch(r'(0[1-9]|1[0-2])/20\d\d',u['periodValue']) if u['periodType']=='month' else re.fullmatch(r'[1-4]/20\d\d',u['periodValue']) if u['periodType']=='quarter' else re.fullmatch(_day+'-'+_day,u['periodValue']) if u['periodType']=='range' else re.fullmatch(r'20\d\d',u['periodValue']))
  check(type(u['annexes']) is list and len(set(u['annexes']))==len(u['annexes']) and set(u['annexes'])<=set(t['annexes']))
  leaves=c['expectedLeaves'];check(type(leaves) is dict and 0<len(leaves)<=64)
  for name,text in leaves.items():
   # A bare name must be unique under CTieuTKhaiChinh; 'Group/leaf' names one leaf of a repeated name (04/NTNN rows).
   check(re.fullmatch(r'[A-Za-z][A-Za-z0-9_.]{0,40}(/[A-Za-z][A-Za-z0-9_]{0,40})?',name) and isinstance(text,str))
   # Only the synthetic profile MST or plain non-negative integers: no names or free text.
   check(text=='9999999997' and name=='mst_cu' or re.fullmatch(r'0|[1-9][0-9]{0,15}',text))
  rows=c.get('expectedRows',{});check(type(rows) is dict and all(re.fullmatch(r'(PLuc_[A-Za-z0-9_]+/[A-Za-z]+|PL[0-9]{2}_[0-9]_NTNN/[A-Za-z]+/[A-Za-z]+)',k) and type(v) is int and 1<=v<=50 for k,v in rows.items()))
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
