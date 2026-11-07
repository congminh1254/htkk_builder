"""Trusted adapter/case metadata. Private plans cannot select arbitrary commands/drivers."""
import copy,json,pathlib,re
ROOT=pathlib.Path(__file__).parent
REGISTRY=json.loads((ROOT/'htkk-native-cases.json').read_text())
def check(value):
 if not value:raise ValueError('CASE_POLICY')
check(REGISTRY.get('format')=='htkk-native-case-registry-v1')
# Reviewed adapter identities only. A private source cannot add a producer or driver.
D1_DRIVER='gtgt-web-import-inspect'
DECLARATION_DRIVER='declaration-web-import-inspect'
DECLARATION_PRODUCER='scripts/generate-htkk-declaration-reference.mjs'
_d1={'driver':D1_DRIVER,'menuId':'D1','xmlVersion':'2.8.3','periods':{'month':('10/2026',),'quarter':('4/2026',)}}
def _declaration(menu,version,periods,annexes):return {'producer':DECLARATION_PRODUCER,'privacyValidator':'declaration-v1','annexes':annexes,'driver':DECLARATION_DRIVER,'menuId':menu,'xmlVersion':version,'periods':periods}
TRUSTED_ADAPTERS={
 '01-gtgt-2.8.3':{'producer':'scripts/generate-htkk-web-reference.mjs','privacyValidator':'gtgt-v1','annexes':[],**_d1},
 '01-gtgt-2.8.3-annex12':{'producer':'scripts/generate-htkk-web-annex12-reference.mjs','privacyValidator':'gtgt-annex12-v1','annexes':['01-2/GTGT'],**_d1},
 # Declaration families behind htkk_web DeclarationEngine (03/TNDN, BCTC, TNCN, 01/CNKD).
 # One reviewed menu, XML version, period and annex set per adapter; Menu.xml 5.8.1 pins.
 '03-tndn-2.9.4':_declaration('N8','2.9.4',{'year':('2025',)},['03-1A']),
 # A2 requires BCKQHĐKD and BCĐTK (HTKK CheckChonPlBctc/Validate_0 0485): 01-1 + 01-4.
 '133-b01a-dnn-2.3.2':_declaration('A2','2.3.2',{'year':('2025',)},['01-1','01-4']),
 # 78 requires exactly one LCTT at export (HTKK cmdExport_Click 0478): KQHĐSXKD + LCTTGT.
 '200-bctc-2.2.6':_declaration('78','2.2.6',{'year':('2025',)},['01-1','01-3']),
 # L7 monthly first declarations are refused from 4/2026 (HTKK 0682): quarter only.
 '05-kk-tncn-2.9.3':_declaration('L7','2.9.3',{'quarter':('3/2026',)},[]),
 '05-qtt-tncn-2.9.3':_declaration('B9','2.9.3',{'year':('2025',)},['05-1','05-3']),
 '01-cnkd-hkd-2.9.8':_declaration('U5','2.9.8',{'quarter':('3/2026',)},[]),
 # B8 02/QTT-TNCN (non-gating): KieuKy 12 like B9; the import adds every annex (AddFullPLImportXML).
 '02-qtt-tncn-2.7.3':_declaration('B8','2.7.3',{'year':('2025',)},['02-1']),
 # I9 01/NTNN TT80 (non-gating): KieuKy 18 = SetLayoutToKhaiThangLanPhatSinh, month (Tháng is the default).
 '01-ntnn-tt80-2.5.1':_declaration('I9','2.5.1',{'month':('10/2026',)},[]),
 # Y8 01/NTNN, NCCNN TT89 (non-gating): KieuKy 18 like I9; Menu.xml validity from 01/10/2026.
 '01-ntnn-nccnn-tt89-3.0.9':_declaration('Y8','3.0.9',{'month':('10/2026',)},[]),
}
ADAPTERS={a['adapterId']:a for a in REGISTRY['adapters']}
check(len(ADAPTERS)==len(REGISTRY['adapters']) and set(ADAPTERS)<=set(TRUSTED_ADAPTERS))
for a in ADAPTERS.values():
 trusted=TRUSTED_ADAPTERS[a['adapterId']]
 check(set(a)=={'adapterId','htkkVersion','menuId','xmlVersion','producer','driver','privacyValidator','profilePolicy'})
 check(a['driver']==trusted['driver'] and a['privacyValidator']==trusted['privacyValidator'] and a['profilePolicy']=='synthetic-9999999997-v1')
 check(a['producer']==trusted['producer'] and a['menuId']==trusted['menuId'] and a['xmlVersion']==trusted['xmlVersion'] and a['htkkVersion']=='5.8.1')
CASES={c['caseId']:c for c in REGISTRY['cases']}
check(0<len(CASES)<=256 and len(CASES)==len(REGISTRY['cases']))
for c in CASES.values():
 check(set(c)=={'caseId','producerCase','adapterId','format','stagingDirectory','inputBranch','outputBranch','statusContext','releaseGate','unit'})
 check(re.fullmatch('[A-Za-z0-9-]{1,100}',c['caseId']) and re.fullmatch('[a-z0-9-]{1,80}',c['producerCase']))
 a=ADAPTERS[c['adapterId']];u=c['unit']
 check(u['menuId']==a['menuId'] and u['adapterVersion']==a['xmlVersion'] and u['activityCode']=='00' and u['annexes']==TRUSTED_ADAPTERS[a['adapterId']]['annexes'] and type(u['amendmentOrder'])is int and u['amendmentOrder']==0)
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
# Declaration-family cases use their own input/output file names, privacy allowlist and driver.
DECLARATION_CASES=tuple(id for id,c in CASES.items() if ADAPTERS[c['adapterId']]['driver']==DECLARATION_DRIVER)
check(all(not CASES[id]['releaseGate'] for id in DECLARATION_CASES))
DRIVERS=tuple(sorted({a['driver'] for a in ADAPTERS.values()}))
def driver(case):check(case in CASES);return ADAPTERS[CASES[case]['adapterId']]['driver']
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
