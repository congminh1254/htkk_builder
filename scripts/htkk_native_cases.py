"""Trusted adapter/case metadata. Private plans cannot select arbitrary commands/drivers."""
import copy,json,pathlib,re
ROOT=pathlib.Path(__file__).parent
REGISTRY=json.loads((ROOT/'htkk-native-cases.json').read_text())
def check(value):
 if not value:raise ValueError('CASE_POLICY')
check(REGISTRY.get('format')=='htkk-native-case-registry-v1')
ADAPTERS={a['adapterId']:a for a in REGISTRY['adapters']}
check(len(ADAPTERS)==len(REGISTRY['adapters']))
for a in ADAPTERS.values():
 check(a['driver']=='gtgt-web-import-inspect' and a['privacyValidator']=='gtgt-v1' and a['profilePolicy']=='synthetic-9999999997-v1')
 check(a['producer']=='scripts/generate-htkk-web-reference.mjs' and a['menuId']=='D1' and a['xmlVersion']=='2.8.3' and a['htkkVersion']=='5.8.1')
CASES={c['caseId']:c for c in REGISTRY['cases']}
check(0<len(CASES)<=256 and len(CASES)==len(REGISTRY['cases']))
for c in CASES.values():
 check(re.fullmatch('[A-Za-z0-9-]{1,100}',c['caseId']) and re.fullmatch('[a-z0-9-]{1,80}',c['producerCase']))
 a=ADAPTERS[c['adapterId']];u=c['unit']
 check(u['menuId']==a['menuId'] and u['adapterVersion']==a['xmlVersion'] and u['activityCode']=='00' and u['annexes']==[] and type(u['amendmentOrder'])is int and u['amendmentOrder']==0)
 check(u['periodType'] in ('month','quarter') and u['periodValue'] in ('10/2026','4/2026'))
 for key in ('stagingDirectory','inputBranch','outputBranch'):check(re.fullmatch('[a-zA-Z0-9-]{1,120}',c[key]))
 check(c['statusContext']=='htkk-native/'+c['producerCase'] and re.fullmatch('htkk-web-[a-z0-9-]+-input-v1',c['format']))
for key in ('producerCase','stagingDirectory','inputBranch','outputBranch','statusContext'):check(len({c[key]for c in CASES.values()})==len(CASES))
def policy(case):
 check(case in CASES);return copy.deepcopy(CASES[case])
def validate_plan(value):
 check(type(value)is dict and value.get('format')=='htkk-case-plan-v1' and value.get('htkkVersion')=='5.8.1' and value.get('nativeQualified')is False and value.get('filingEnabled')is False)
 rows=value.get('nativeCases');check(type(rows)is list and len(rows)==len(CASES));seen=set()
 for item in rows:
  check(type(item)is dict and item.get('caseId')in CASES and item['caseId']not in seen);seen.add(item['caseId']);c=CASES[item['caseId']];a=ADAPTERS[c['adapterId']]
  for key in ('adapterId','producerCase','unit'):check(item.get(key)==c[key])
  check(item.get('producer')==a['producer'] and item.get('profilePolicy')==a['profilePolicy'] and item.get('coverageGranted')is False and re.fullmatch('[a-f0-9]{64}',item.get('descriptorFingerprint','')))
 return value
