"""Trusted adapter/case metadata. Private plans cannot select arbitrary commands/drivers."""
import copy,json,pathlib,re
ROOT=pathlib.Path(__file__).parent
REGISTRY=json.loads((ROOT/'htkk-native-cases.json').read_text())
def check(value):
 if not value:raise ValueError('CASE_POLICY')
check(REGISTRY.get('format')=='htkk-native-case-registry-v1')
# Reviewed adapter identities only. A private source cannot add a producer or driver.
TRUSTED_ADAPTERS={
 '01-gtgt-2.8.3':{'producer':'scripts/generate-htkk-web-reference.mjs','privacyValidator':'gtgt-v1','annexes':[]},
 '01-gtgt-2.8.3-annex12':{'producer':'scripts/generate-htkk-web-annex12-reference.mjs','privacyValidator':'gtgt-annex12-v1','annexes':['01-2/GTGT']},
}
ADAPTERS={a['adapterId']:a for a in REGISTRY['adapters']}
check(len(ADAPTERS)==len(REGISTRY['adapters']) and set(ADAPTERS)<=set(TRUSTED_ADAPTERS))
for a in ADAPTERS.values():
 trusted=TRUSTED_ADAPTERS[a['adapterId']]
 check(set(a)=={'adapterId','htkkVersion','menuId','xmlVersion','producer','driver','privacyValidator','profilePolicy'})
 check(a['driver']=='gtgt-web-import-inspect' and a['privacyValidator']==trusted['privacyValidator'] and a['profilePolicy']=='synthetic-9999999997-v1')
 check(a['producer']==trusted['producer'] and a['menuId']=='D1' and a['xmlVersion']=='2.8.3' and a['htkkVersion']=='5.8.1')
CASES={c['caseId']:c for c in REGISTRY['cases']}
check(0<len(CASES)<=256 and len(CASES)==len(REGISTRY['cases']))
for c in CASES.values():
 check(set(c)=={'caseId','producerCase','adapterId','format','stagingDirectory','inputBranch','outputBranch','statusContext','releaseGate','unit'})
 check(re.fullmatch('[A-Za-z0-9-]{1,100}',c['caseId']) and re.fullmatch('[a-z0-9-]{1,80}',c['producerCase']))
 a=ADAPTERS[c['adapterId']];u=c['unit']
 check(u['menuId']==a['menuId'] and u['adapterVersion']==a['xmlVersion'] and u['activityCode']=='00' and u['annexes']==TRUSTED_ADAPTERS[a['adapterId']]['annexes'] and type(u['amendmentOrder'])is int and u['amendmentOrder']==0)
 check(u['periodType'] in ('month','quarter') and u['periodValue'] in ('10/2026','4/2026'))
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
