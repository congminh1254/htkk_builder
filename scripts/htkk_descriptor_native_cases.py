"""Design-only registry of TNCN descriptor native cases (05/KK, 05/QTT, 02/QTT).

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
}
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
  check(re.fullmatch(r'(0[1-9]|1[0-2])/20\d\d',u['periodValue']) if u['periodType']=='month' else re.fullmatch(r'[1-4]/20\d\d',u['periodValue']) if u['periodType']=='quarter' else re.fullmatch(r'20\d\d',u['periodValue']))
  check(type(u['annexes']) is list and len(set(u['annexes']))==len(u['annexes']) and set(u['annexes'])<=set(t['annexes']))
  leaves=c['expectedLeaves'];check(type(leaves) is dict and 0<len(leaves)<=64)
  for name,text in leaves.items():
   check(re.fullmatch(r'[A-Za-z][A-Za-z0-9_.]{0,40}',name) and isinstance(text,str))
   # Only the synthetic profile MST or plain non-negative integers: no names or free text.
   check(text=='9999999997' and name=='mst_cu' or re.fullmatch(r'0|[1-9][0-9]{0,15}',text))
  rows=c.get('expectedRows',{});check(type(rows) is dict and all(re.fullmatch(r'PLuc_[A-Za-z0-9_]+/[A-Za-z]+',k) and type(v) is int and 1<=v<=50 for k,v in rows.items()))
  check(bool(rows)==bool(u['annexes']))
  per.setdefault(c['adapterId'],[]).append(c)
 # Each adapter needs a zero case and at least one case with amounts.
 for adapter,cases in per.items():
  check(any(all(v in ('0','9999999997') for v in c['expectedLeaves'].values()) for c in cases))
  check(any(any(v not in ('0','9999999997') for v in c['expectedLeaves'].values()) for c in cases))
 check(set(per)==set(TRUSTED))
 return copy.deepcopy(value)
DESIGN=validate(json.loads((ROOT/'htkk-descriptor-native-cases.json').read_text()))
CASE_IDS=tuple(c['caseId'] for c in DESIGN['cases'])
