"""Offline contracts for the two 01-2/GTGT web->HTKK cases and the nonzero export probe.

Every XML here is synthetic and built from the trusted contracts; none is a
captured original export, and passing these tests is never native evidence.
"""
import base64,copy,datetime,hashlib,importlib.util,json,pathlib,re,tempfile,unittest,urllib.error
import xml.etree.ElementTree as ET
from unittest.mock import patch
ROOT=pathlib.Path(__file__).parent
def load(name,file):
 spec=importlib.util.spec_from_file_location(name,ROOT/file);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
cases=load('annex_cases_registry','htkk_native_cases.py')
contract=load('annex_cases_contract','htkk_annex12_web_cases.py')
web=load('annex_cases_web_fixture','test_htkk_web_input.py');w=web.w
native_fixture=load('annex_cases_native_fixture','test_htkk_web_native_output.py');n=native_fixture.n
publisher=load('annex_cases_input_publisher','publish-htkk-web-inputs.py')
dispatch=load('annex_cases_dispatch','dispatch-native-cases.py')
batch=load('annex_cases_batch','native_batch.py')
pages=load('annex_cases_pages','validate-pages.py')
nonzero=load('annex_cases_nonzero','publish-htkk-annex12-nonzero-export.py')
zero_export=load('annex_cases_zero_export_fixture','test_annex12_fixed_export.py')
ZERO=contract.ZERO_CASE;TWO=contract.TWO_PLANTS_CASE;ANNEX=(ZERO,TWO)
TODAY=datetime.date(2026,10,27);NS='{'+contract.NS+'}'
def edited(body,edit,preamble=True):
 text=body.decode('utf-8');root=ET.fromstring(text.replace(w.COMMENT,''));edit(root);ET.register_namespace('',contract.NS)
 return ((w.PREAMBLE if preamble else '')+ET.tostring(root,encoding='unicode')).encode('utf-8')

class RegistryContract(unittest.TestCase):
 def test_two_candidate_cases_use_the_annex_product_producer_and_own_status_contexts(self):
  self.assertEqual(cases.ANNEX12_CASES,ANNEX);self.assertEqual(tuple(c for c in cases.CANDIDATE_CASES if c not in cases.DECLARATION_CASES),ANNEX)
  self.assertEqual(len(cases.GATE_CASES),13);self.assertTrue(set(cases.GATE_CASES).isdisjoint(ANNEX))
  for case,producer_case in ((ZERO,'annex12-zero'),(TWO,'annex12-two-plants')):
   c=cases.CASES[case];a=cases.ADAPTERS[c['adapterId']]
   self.assertEqual(c['producerCase'],producer_case);self.assertIs(c['releaseGate'],False)
   self.assertEqual(a['producer'],'scripts/generate-htkk-web-annex12-reference.mjs');self.assertEqual(a['driver'],'gtgt-web-import-inspect');self.assertEqual(a['privacyValidator'],'gtgt-annex12-v1')
   self.assertEqual(c['statusContext'],'htkk-native/'+producer_case);self.assertEqual(dispatch.CONTEXTS[case],c['statusContext'])
   self.assertEqual(c['unit']['annexes'],['01-2/GTGT']);self.assertEqual(c['format'],'htkk-web-'+producer_case+'-input-v1')
  for key in ('stagingDirectory','inputBranch','outputBranch','statusContext'):self.assertEqual(len({c[key] for c in cases.CASES.values()}),len(cases.CASES))
 def test_registry_rejects_untrusted_adapter_producer_or_annex_scope(self):
  raw=json.loads((ROOT/'htkk-native-cases.json').read_text())
  for mutate in (lambda r:r['adapters'][1].update(producer='scripts/other.mjs'),lambda r:r['adapters'][1].update(privacyValidator='gtgt-v1'),lambda r:r['cases'][14]['unit'].update(annexes=[]),lambda r:r['cases'][0]['unit'].update(annexes=['01-2/GTGT']),lambda r:r['cases'][14].update(releaseGate='no'),lambda r:r['cases'][14].pop('releaseGate')):
   value=copy.deepcopy(raw);mutate(value)
   with self.subTest(),tempfile.TemporaryDirectory() as directory,self.assertRaises((ValueError,KeyError)):
    folder=pathlib.Path(directory);(folder/'htkk-native-cases.json').write_text(json.dumps(value));target=folder/'htkk_native_cases.py';target.write_text((ROOT/'htkk_native_cases.py').read_text())
    spec=importlib.util.spec_from_file_location('mutated_registry',target);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 def plan(self,ids):
  rows=[]
  for case in ids:
   c=cases.CASES[case];a=cases.ADAPTERS[c['adapterId']];rows.append({'caseId':case,'adapterId':c['adapterId'],'producerCase':c['producerCase'],'unit':c['unit'],'producer':a['producer'],'profilePolicy':a['profilePolicy'],'coverageGranted':False,'descriptorFingerprint':'a'*64})
  return {'format':'htkk-case-plan-v1','htkkVersion':'5.8.1','nativeQualified':False,'filingEnabled':False,'nativeCases':rows}
 def test_source_plan_is_the_legacy_gate_set_or_every_case_never_a_partial_set(self):
  self.assertTrue(cases.validate_plan(self.plan(cases.GATE_CASES)));self.assertTrue(cases.validate_plan(self.plan(cases.CASES)))
  for ids in ((*cases.GATE_CASES,ZERO),cases.GATE_CASES[1:],ANNEX):
   with self.subTest(ids=len(ids)),self.assertRaises(ValueError):cases.validate_plan(self.plan(ids))
  bad=self.plan(cases.CASES);bad['nativeCases'][-1]['producer']='scripts/generate-htkk-web-reference.mjs'
  with self.assertRaises(ValueError):cases.validate_plan(bad)
 def test_workflow_choices_powershell_formats_and_build_cleanup_cover_new_cases(self):
  workflow=(ROOT.parent/'.github/workflows/probe-htkk-windows.yml').read_text();formats=(ROOT/'HtkkNativeCaseFormats.ps1').read_text();build=(ROOT.parent/'.github/workflows/build.yml').read_text()
  options=re.search(r'web_case_id:\n.*?options: \[([^\]]+)\]',workflow,re.S).group(1)
  self.assertEqual([x.strip() for x in options.split(',')],list(cases.CASES))
  for case in ANNEX:
   self.assertIn("'"+case+"'='"+cases.CASES[case]['format']+"'",formats);self.assertIn('"$RUNNER_TEMP/'+cases.CASES[case]['stagingDirectory']+'"',build)

class CohortContract(unittest.TestCase):
 def test_dispatch_includes_candidates_with_immutable_inputs_but_cohort_and_pages_do_not_wait_for_them(self):
  publication={'format':'htkk-web-input-publication-v1','sourceCommit':'a'*40,'cases':[{'caseId':case,'artifactCommit':hashlib.sha1(case.encode()).hexdigest()} for case in dispatch.CASES]}
  calls=[];dispatch.dispatch(dispatch.publication(json.dumps(publication).encode(),'a'*40),'actions','status',lambda *args:calls.append(args))
  sent=[args[2]['inputs'] for args in calls if args[0].endswith('/dispatches')]
  for case in ANNEX:
   inputs=next(item for item in sent if item['web_case_id']==case)
   self.assertEqual(inputs['gui_automation'],'gtgt-web-import-inspect');self.assertEqual(inputs['web_artifact_commit'],hashlib.sha1(case.encode()).hexdigest())
  self.assertEqual(pages.CONTEXTS,tuple(cases.CASES[c]['statusContext'] for c in cases.GATE_CASES))
  import test_caseflow_batch as cohort
  f=cohort.fixture();statuses=f['statuses']+[{'context':cases.CASES[c]['statusContext'],'state':'failure','description':'failed input:'+f['publication']['cases'][-1]['artifactCommit'],'target_url':'https://github.com/x'} for c in ANNEX]
  proof=cohort.batch.discover(f['publication'],cohort.BUILDER,statuses,f['get'],retry=lambda *args:self.fail('Candidate failures never retry or block the cohort'))
  self.assertEqual([item['caseId'] for item in proof['cases']],list(cases.GATE_CASES))

class InputPrivacyContract(unittest.TestCase):
 def test_exact_case_inputs_and_manifest_leaves_are_accepted_without_changing_bytes(self):
  for case in ANNEX:
   body=web.annex_fixture(case);raw=bytes(body);manifest=web.case_manifest(body,case)
   checked=w.validate_web_xml(body,case_id=case,manifest=w.validate_manifest(json.dumps(manifest,ensure_ascii=False).encode()))
   self.assertEqual(body,raw);self.assertEqual(checked['annexTaxLeafCount'],contract.tax_leaves(case))
   self.assertEqual(sum(1 for node in ET.fromstring(body.decode().replace(w.COMMENT,'')).iter() if len(node)==0),contract.total_leaves(case))
  self.assertEqual((contract.tax_leaves(ZERO),contract.tax_leaves(TWO)),(108,159))
 def test_relabelled_or_changed_annex_amounts_rows_ids_dates_and_strings_are_rejected(self):
  zero=web.annex_fixture(ZERO);two=web.annex_fixture(TWO)
  def first(tag):return lambda root:root.findall('.//'+NS+tag)[0]
  mutations=[
   (zero,TWO,None),(two,ZERO,None),(web.web_fixture(),ZERO,None),(zero,'01GTGT-zero-M10-2026',None),
   (two,TWO,lambda r:setattr(r.findall('.//'+NS+'ct12')[1],'text','6')),
   (two,TWO,lambda r:setattr(r.findall('.//'+NS+'ct10_a')[0],'text','8')),
   (two,TWO,lambda r:setattr(r.findall('.//'+NS+'ct11')[0],'text','33.34')),
   (two,TWO,lambda r:setattr(r.find('.//'+NS+'ct13'),'text','11')),
   (two,TWO,lambda r:r.findall('.//'+NS+'TenNhaMay')[1].set('id','ID_3')),
   (two,TWO,lambda r:r.findall('.//'+NS+'DiaBanPhanBo')[4].set('id','ID_9')),
   (two,TWO,lambda r:r.findall('.//'+NS+'TenNhaMay')[1].remove(r.findall('.//'+NS+'DiaBanPhanBo')[4])),
   (zero,ZERO,lambda r:setattr(r.find('.//'+NS+'ten_nhaMay'),'text','CONG TY THAT')),
   (zero,ZERO,lambda r:setattr(r.find('.//'+NS+'ma_nhaMay'),'text','0101234567')),
   (zero,ZERO,lambda r:setattr(r.find('.//'+NS+'ct05'),'text','NGUOI THAT')),
   (zero,ZERO,lambda r:setattr(r.find('.//'+NS+'ngayKy'),'text','2026-10-25')),
   (zero,ZERO,lambda r:setattr(r.find('.//'+NS+'ct40'),'text','1')),
   (zero,ZERO,lambda r:r.find('.//'+NS+'TenNhaMay').set('extra','x')),
  ]
  for body,case,mutate in mutations:
   candidate=edited(body,mutate) if mutate else body
   with self.subTest(case=case,mutated=mutate is not None),self.assertRaises(w.InputError):w.validate_web_xml(candidate,case_id=case)
 def test_manifest_shape_counters_and_recomputed_leaves_are_exact(self):
  body=web.annex_fixture(TWO);good=web.case_manifest(body,TWO)
  for key,value in (('nativeNodesCompared',131),('nativeLeafComparisonPassed',True),('exporter','lib/htkk-xml.ts'),('producer','scripts/x.mjs'),('fullCompatibilityVerified',True),('expectedAnnexLeaves','x'),('extra',1)):
   bad={**good,key:value}
   with self.subTest(key=key),self.assertRaises(w.InputError):
    manifest=w.validate_manifest(json.dumps(bad).encode());w.validate_web_xml(body,case_id=TWO,manifest=manifest)
  bad=copy.deepcopy(good);bad['expectedAnnexLeaves'][3][1]='OTHER'
  with self.assertRaises(w.InputError):w.validate_web_xml(body,case_id=TWO,manifest=w.validate_manifest(json.dumps(bad).encode()))
  zero=web.case_manifest(web.annex_fixture(ZERO),ZERO)
  with self.assertRaises(w.InputError):w.validate_manifest(json.dumps({**zero,'caseId':TWO,'format':cases.CASES[TWO]['format']}).encode())
 def test_each_producer_is_hash_bound_separately_before_writes(self):
  self.assertEqual(publisher.CASE_PRODUCERS[ZERO],'scripts/generate-htkk-web-annex12-reference.mjs');self.assertEqual(publisher.CASE_PRODUCERS['01GTGT-zero-M10-2026'],publisher.PRODUCER)
  import test_htkk_web_input_publisher as fixtures
  inputs=fixtures.fixtures();index=list(cases.CASES).index(ZERO);item=inputs[index];metadata=dict(item[3]);metadata['producerSha256']=hashlib.sha256(fixtures.PRODUCER).hexdigest()
  files=dict(item[2]);files['manifest.json']=(json.dumps(metadata,ensure_ascii=False)+'\n').encode();inputs[index]=(item[0],item[1],files,metadata)
  fetch,calls,_=fixtures.fake_api()
  with self.assertRaises(publisher.PublicationError):publisher.publish(inputs,fixtures.SHA,'synthetic-token',fetch)
  self.assertFalse(any(path in ('/git/blobs','/git/refs') for path,_,_,_ in calls))

class NativeOutputContract(unittest.TestCase):
 def test_reexports_require_exact_case_annex_and_fixed_signing_date(self):
  for case in ANNEX:
   web_body,native,_,_=native_fixture.fixture(case)
   self.assertTrue(n.validate_native(native,case,native_fixture.TODAY)['privacyValuesVerified'])
   self.assertEqual(n.compare_tax(web_body,native,case)['checkedTaxLeafCount'],contract.tax_leaves(case))
   with self.assertRaises(n.OutputError):n.compare_tax(web_body,native)
   with self.assertRaises(n.OutputError):n.validate_native(native_fixture.changed(native,'ngayKy','2026-10-25'),case,native_fixture.TODAY)
  zero=native_fixture.fixture(ZERO)[1];two=native_fixture.fixture(TWO)[1]
  with self.assertRaises(n.OutputError):n.validate_native(zero,TWO,native_fixture.TODAY)
  with self.assertRaises(n.OutputError):n.validate_native(two,ZERO,native_fixture.TODAY)
  # The UI baseline of both cases is the proven one-plant zero annex.
  # Two-plant baseline: proven zero annex with the sale10 main vector (Header!B66).
  self.assertTrue(n.validate_native(native_fixture.two_plant_baseline(),TWO,native_fixture.TODAY,initial=True,aligned=True)['privacyValuesVerified'])
  with self.assertRaises(n.OutputError):n.validate_native(zero,TWO,native_fixture.TODAY,initial=True,aligned=True)
  with self.assertRaises(n.OutputError):n.validate_native(two,TWO,native_fixture.TODAY,initial=True,aligned=True)
 def test_only_the_two_plant_case_may_differ_from_its_baseline(self):
  self.assertEqual([case for case in cases.CASES if not n.baseline_matches_input(case)],[TWO])
  probe=(ROOT/'probe-htkk-windows.ps1').read_text()
  self.assertIn("(-not $gui.roundtripXmlExactMatched -and $gui.webCaseId -cne '"+TWO+"')",probe)
  self.assertIn("webTaxCheckedLeafCount=[int]$gui.webTaxLeafCount;",probe)
  self.assertIn("$gui.webTaxLeafCount -ne $(if($gui.webCaseId -ceq '"+TWO+"'){159}elseif($gui.webCaseId -ceq '"+ZERO+"'){108}else{70})",probe)
  for line in probe.splitlines():
   if '$gui.webCaseId -cnotin @(' in line:
    for case in ANNEX:self.assertIn("'"+case+"'",line)
   # Edit counts: the zero annex makes no main edit; the two-plant case one J48 sale edit.
   marker="elseif($env:EXPECTED_WEB_CASE_ID -cnotin @('01GTGT-zero-M10-2026','01GTGT-zero-Q4-2026',"
   if marker in line:edits=line.split(marker)[1].split('){1}')[0];self.assertEqual(edits,"'"+ZERO+"')")

class NativeDriverContract(unittest.TestCase):
 def source(self,name):return (ROOT/name).read_text(encoding='utf-8')
 def test_comparison_counts_and_dates_are_fixed_per_case(self):
  compare=self.source('HtkkWebTaxComparison.cs');reference=self.source('HtkkWebInputReference.cs');export=self.source('HtkkGtgtExportInspection.cs')
  self.assertIn('if(expectedTaxLeaves!=70&&expectedTaxLeaves!=108&&expectedTaxLeaves!=159)return false;',compare)
  self.assertIn('public static bool Compare(XmlDocument input,XmlDocument baseline,XmlDocument output,out int taxLeaves){return Compare(input,baseline,output,70,out taxLeaves);}',compare)
  self.assertIn('private int WebTaxLeafTarget(){return !Annex12WebCaseId()?70:webCaseId==Annex12WebTwoPlantsCaseId?159:108;}',reference)
  self.assertIn('HtkkWebTaxComparison.Compare(input,baseline,output,WebTaxLeafTarget(),out webTaxLeafCount)',export)
  # Only creation date and the four service identity leaves keep native rules.
  self.assertIn('return path==DatePath||input.InnerText==output.InnerText;',compare)
 def test_driver_builds_the_proven_baseline_imports_with_original_control_and_never_writes_cells(self):
  sheet=self.source('HtkkGtgtPeriodAndSheet.cs');annex=self.source('HtkkGtgtAnnex12ExportInspection.cs');roundtrip=self.source('HtkkGtgtRoundtripInspection.cs')
  self.assertIn('||Annex12WebCase();}',sheet);self.assertIn('if(matched&&Annex12WebCase()){',sheet)
  branch=sheet[sheet.index('if(matched&&Annex12WebCase()){'):sheet.index('if(matched&&Annex12InspectionMode()){InspectOriginalAnnex12(grid);return;}')]
  self.assertLess(branch.index('EditOriginalSigningDate(grid,sheet)'),branch.index('InspectOriginalAnnex12(grid)'))
  self.assertIn('bool annexMatched=!Annex12WebCase()||InspectOriginalImportedAnnex12(grids[0]);',roundtrip)
  self.assertIn('Named(roundtripOwner,"cmdImportXML")',roundtrip)
  inspect=annex[annex.index(' private bool InspectOriginalImportedAnnex12('):annex.index(' private void RestoreImportedAnnex12HeadAuthorities(')]
  for forbidden in ('SetValue','set_Value','SetPublic','SendKeys','PerformClick','"Formula"','InsertTable'):self.assertNotIn(forbidden,inspect)
  for term in ('"TablePath"','"DataLocationTemplateRowStart"','Annex12CellLocked(annex,parent,20)','Annex12CellLocked(annex,row,20)','"9999999997-001","99997"','33.33m,66.67m','50m,25m,25m'):self.assertIn(term,inspect)
  self.assertIn('if(Annex12WebCase())ValidateOriginalAnnex12WebExport(roundtripPhase=="not-started");',self.source('HtkkGtgtExportInspection.cs'))
  self.assertIn('if(!Annex12SaleMain()&&(!gtgtZero||gtgtEmptyMoney!=0||webCaseEditCount!=0))throw new InvalidOperationException();',branch)
  self.assertLess(branch.index('PrepareAnnex12SaleMain(grid,sheet)'),branch.index('EditOriginalSigningDate(grid,sheet)'))
  # Main money vector: zero annex keeps 27 zeros; the two-plant case and the nonzero probe carry sale10.
  self.assertIn('webCaseId!=Annex12WebZeroCaseId&&(!NoActivityCase()||CancelCt21Case()))||mode=="gtgt-annex12-export-nonzero"',sheet)
 def test_success_predicate_requires_annex_baseline_import_and_both_schema_checks(self):
  probe=(ROOT/'probe-htkk-windows.ps1').read_text()
  line=next(x for x in probe.splitlines() if "if($GuiAutomation -eq 'gtgt-web-import-inspect' -and $env:EXPECTED_WEB_CASE_ID -cin @('"+ZERO+"','"+TWO+"')){$matched=" in x)
  for term in ('annex12InputActionCount -eq 14','annex12WebBaselineSchemaVerified','annex12WebReexportSchemaVerified','annex12WebImportSheetMatched','annex12WebImportGroupCount -eq $(if($env:EXPECTED_WEB_CASE_ID -ceq','annex12RowInsertActionCount -eq 1','annex12ExportMainZeroMatched'):self.assertIn(term,line)
  self.assertIn("-and $lastGui.webTaxLeafCount -eq $(if($env:EXPECTED_WEB_CASE_ID -ceq '"+TWO+"'){159}elseif($env:EXPECTED_WEB_CASE_ID -ceq '"+ZERO+"'){108}else{70})",probe)
  registry=json.loads((ROOT/'htkk-native-automation-registry.json').read_text())['resultFields']
  self.assertEqual(registry['webTaxLeafCount']['maximum'],159);values=registry['webCaseId']['values'];self.assertEqual(values[values.index(ANNEX[0]):values.index(ANNEX[0])+2],list(ANNEX))
  for key in ('annex12WebImportSheetMatched','annex12WebBaselineSchemaVerified','annex12WebReexportSchemaVerified','annex12WebImportGroupCount','annex12WebImportRowCount'):self.assertEqual(registry[key]['activeModes'],['gtgt-web-import-inspect'])
  csharp=(ROOT/'HtkkWebInputReference.cs').read_text(encoding='utf-8')
  for case in ANNEX:self.assertIn('"'+case+'"',csharp)

def snapshot(name):
 parent,first,second=(1,'50.00','50.00') if 'p1-50' in name else (7,'33.33','66.67')
 def edit(root):
  for name,value in nonzero.SALE10.items():root.find('.//'+NS+name).text=value
  root.find('.//'+NS+'ct10_a').text=str(parent);rows=root.findall('.//'+NS+'DiaBanPhanBo')
  rows[0].find(NS+'ct11').text=first;rows[1].find(NS+'ct11').text=second
  rows[0].find(NS+'ct12').text='0.5' if parent==1 else '2.3331';rows[1].find(NS+'ct12').text='0.5' if parent==1 else '4.6669'
  root.find('.//'+NS+'ct13').text=str(parent);root.find('.//'+NS+'ct14').text=str(parent)
 return zero_export.edited(zero_export.fixture(),edit)
NAMES=tuple(nonzero.SNAPSHOTS)

class NonzeroExportProbeContract(unittest.TestCase):
 def test_mode_is_separate_registered_and_uses_only_original_numeric_edits(self):
  registry=json.loads((ROOT/'htkk-native-automation-registry.json').read_text())
  mode=registry['modes']['gtgt-annex12-export-nonzero']
  self.assertEqual((mode['terminalStage'],mode['privateArtifactPolicy'],mode['contextPolicy'],mode['permit']),('gtgt-annex12-export-nonzero-inspected','raw-annex12-nonzero-export','none','profile-save'))
  numeric=(ROOT/'HtkkGtgtAnnex12NumericInspection.cs').read_text(encoding='utf-8');annex=(ROOT/'HtkkGtgtAnnex12ExportInspection.cs').read_text(encoding='utf-8')
  self.assertIn('!(mode=="gtgt-annex12-export-nonzero"&&index<=3)',numeric)
  block=annex[annex.index(' private void ContinueOriginalAnnex12Nonzero('):annex.index(' private static bool Annex12CellLocked(')]
  self.assertIn('EditAnnex12Numeric(grid,annex,1);EditAnnex12Numeric(grid,annex,2);EditAnnex12Numeric(grid,annex,3);',block)
  self.assertIn('Named(roundtripOwner,"cmdExport")',block);self.assertIn('"01GTGT-p7.xml"',block)
  for forbidden in ('set_Value','SetPublic(','"Formula"','InsertTable','WriteAllText','XmlWriter'):self.assertNotIn(forbidden,block)
  # The only reflection write is the public vendor sheet selection, never a cell or model value.
  self.assertEqual(block.count('SetValue('),1);self.assertIn('active.SetValue(grid,found,null)',block)
  self.assertIn('EditAnnex12Numeric(grid,annex,0);',annex[annex.index(' private void StartOriginalAnnex12Export('):annex.index(' private sealed class Annex12PinnedSchemaResolver')])
  for key in ('annex12NonzeroEditsMatched','annex12NonzeroSecondShapeMatched','annex12NonzeroSecondSchemaVerified','annex12NonzeroExportCount','annex12NonzeroSecondExportBytes','annex12NonzeroSecondExportSha256'):
   self.assertEqual(registry['resultFields'][key]['activeModes'],['gtgt-annex12-export-nonzero'])
  self.assertEqual(registry['resultFields']['annex12NumericActionCount']['activeModes'],['gtgt-annex12-numeric-inspect','gtgt-annex12-export-nonzero'])
 def test_workflow_publishes_only_after_success_stop_and_credential_gate(self):
  workflow=(ROOT.parent/'.github/workflows/probe-htkk-windows.yml').read_text()
  step=workflow[workflow.index('      - name: Retain fixed original nonzero 01-2 GTGT exports privately'):]
  step=step[:step.index('      - name: Retain verified raw native web reexport privately')]
  for term in ("steps.native_probe.outcome == 'success'","steps.native_probe.outputs.credentials_safe == 'true'","steps.native_probe.outputs.supplier_stopped == 'true'","inputs.gui_automation == 'gtgt-annex12-export-nonzero'",'python ./scripts/publish-htkk-annex12-nonzero-export.py'):self.assertIn(term,step)
  self.assertNotIn('upload-artifact',workflow)
  stage=(ROOT/'stage-htkk-annex12-nonzero-export.py').read_text()
  for token in ('SOURCE_PUBLISH_TOKEN','SOURCE_READ_TOKEN','GH_TOKEN'):self.assertNotIn(token,stage)
  probe=(ROOT/'probe-htkk-windows.ps1').read_text();self.assertIn("& python (Join-Path $PSScriptRoot 'stage-htkk-annex12-nonzero-export.py')",probe)
 def test_inputs_are_exact_but_calculated_amounts_only_bounded_by_the_parent(self):
  for name in NAMES:
   body=snapshot(name);result=nonzero.validate_snapshot(body,name,zero_export.TODAY);self.assertEqual(result['sha256'],hashlib.sha256(body).hexdigest())
   self.assertIs(result['fullCompatibilityVerified'],False)
  bad=[(NAMES[0],'ct12','1.5'),(NAMES[1],'ct12','7.0001'),(NAMES[1],'ct11','33.34'),(NAMES[0],'ct10_a','7'),(NAMES[1],'ct13','8'),(NAMES[0],'ct40','1'),(NAMES[0],'ma_nhaMay','0101234567'),(NAMES[1],'ct12','-1'),(NAMES[1],'ct12','1e1')]
  for name,tag,value in bad:
   body=zero_export.edited(snapshot(name),lambda root,tag=tag,value=value:setattr(root.findall('.//'+NS+tag)[0],'text',value))
   with self.subTest(name=name,tag=tag,value=value),self.assertRaises((nonzero.cases.AnnexWebContractError,nonzero.fixed.AnnexContractError)):nonzero.validate_snapshot(body,name,zero_export.TODAY)
  with self.assertRaises(nonzero.cases.AnnexWebContractError):nonzero.validate_snapshot(snapshot(NAMES[0]),NAMES[1],zero_export.TODAY)
 def gui(self,bodies):
  return {**dict.fromkeys(nonzero.GUI_FLAGS,True),'status':'matched','mode':'gtgt-annex12-export-nonzero','stage':'gtgt-annex12-export-nonzero-inspected','failureCategory':'none','webInputVerified':False,'roundtripImportCommandInvoked':False,'realTaxpayerDataUsed':False,'runtimeRoundTrip':False,'annexSelectedCount':1,'annex12InputActionCount':14,'annex12NumericActionCount':4,'annex12NonzeroExportCount':2,'annex12GroupCount':1,'annex12RowAfterGroupRows':2,'annex12RowAfterRows':67,'gtgtCaseMoneyCount':27,'gtgtCaseMismatchMask':0,'gtgtCaseNonzeroMask':nonzero.SALE10_NONZERO_MASK,'webCaseEditCount':1,'exportSha256':hashlib.sha256(bodies[NAMES[0]]).hexdigest(),'exportBytes':len(bodies[NAMES[0]]),'annex12NonzeroSecondExportSha256':hashlib.sha256(bodies[NAMES[1]]).hexdigest(),'annex12NonzeroSecondExportBytes':len(bodies[NAMES[1]])}
 def layout(self,root,bodies):
  installed=root/'installed';temporary=root/'temp';temporary.mkdir();folder=installed/nonzero.ORIGINAL_DIRECTORY;folder.mkdir(parents=True)
  for name,original in nonzero.SNAPSHOTS.items():(folder/original).write_bytes(bodies[name])
  pin=installed/'pinned.bin';pin.write_bytes(b'pinned');return installed,temporary,{'pinned.bin':hashlib.sha256(b'pinned').hexdigest()}
 def test_stage_preserves_raw_bytes_then_publishes_privately_with_bounded_results(self):
  bodies={name:snapshot(name) for name in NAMES}
  with tempfile.TemporaryDirectory() as tmp:
   installed,temporary,pins=self.layout(pathlib.Path(tmp),bodies)
   with patch.object(nonzero,'PINS',pins):
    result=nonzero.stage_original(installed,self.gui(bodies),True,True,temporary,'123','a'*40,'1',zero_export.TODAY)
    staged,metadata,checks=nonzero.read_evidence(temporary/nonzero.DIRECTORY,'123','a'*40,'1',zero_export.TODAY)
    self.assertEqual(staged,bodies);self.assertTrue(result['rawBytesPreserved']);self.assertEqual(set(checks),set(NAMES))
    calls=[]
    def fetch(path,token,payload=None,method=None):
     calls.append((path,payload,method))
     if path=='':return {'private':True,'full_name':nonzero.REPO}
     if path=='/git/blobs':body=base64.b64decode(payload['content']);return {'sha':hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest()}
     if path=='/git/trees':return {'sha':'b'*40}
     if path=='/git/commits':return {'sha':'c'*40}
     if path=='/git/ref/heads/'+nonzero.BRANCH:raise urllib.error.HTTPError('https://api.github.com',404,'PRIVATE',{},None)
     if path=='/git/refs':return {'ref':payload['ref'],'object':{'type':'commit','sha':payload['sha']}}
     raise AssertionError('Unexpected fixed API path')
    published=nonzero.publish(staged,metadata,'synthetic-token',fetch,zero_export.TODAY)
   blobs=[base64.b64decode(payload['content']) for path,payload,_ in calls if path=='/git/blobs']
   self.assertEqual(blobs[:2],[bodies[NAMES[0]],bodies[NAMES[1]]]);self.assertFalse(any(method=='PATCH' for _,_,method in calls))
   text=json.dumps(published);self.assertNotIn('NHA MAY',text);self.assertNotIn('synthetic-token',text);self.assertEqual(published['snapshotCount'],2)
   manifest=json.loads(blobs[2]);self.assertLessEqual(len(blobs[2]),16384);self.assertIs(manifest['fullCompatibilityVerified'],False);self.assertIs(manifest['webEnginePredictionCompared'],False)
 def test_unverified_gui_public_repo_or_hash_change_stop_before_retention(self):
  bodies={name:snapshot(name) for name in NAMES}
  for change in ({'annex12NonzeroSecondSchemaVerified':False},{'annex12NonzeroExportCount':1},{'annex12NumericActionCount':5},{'roundtripImportCommandInvoked':True},{'mode':'gtgt-annex12-export-inspect'}):
   with self.subTest(change=change),patch.object(nonzero.transport,'safe_read') as read,self.assertRaises(nonzero.NonzeroPublicationError):nonzero.stage_original('/unread',{**self.gui(bodies),**change},True,True,'/unread','123','a'*40,'1')
   read.assert_not_called()
  with tempfile.TemporaryDirectory() as tmp:
   installed,temporary,pins=self.layout(pathlib.Path(tmp),bodies);gui=self.gui(bodies);gui['exportSha256']='0'*64
   with patch.object(nonzero,'PINS',pins),self.assertRaises(nonzero.NonzeroPublicationError):nonzero.stage_original(installed,gui,True,True,temporary,'123','a'*40,'1',zero_export.TODAY)
   self.assertFalse((temporary/nonzero.DIRECTORY).exists())
   with patch.object(nonzero,'PINS',pins):
    nonzero.stage_original(installed,self.gui(bodies),True,True,temporary,'123','a'*40,'1',zero_export.TODAY);staged,metadata,_=nonzero.read_evidence(temporary/nonzero.DIRECTORY,'123','a'*40,'1',zero_export.TODAY)
    with self.assertRaises(nonzero.NonzeroPublicationError):nonzero.publish(staged,metadata,'synthetic-token',lambda path,token,payload=None,method=None:{'private':False,'full_name':nonzero.REPO},zero_export.TODAY)
  failure=nonzero.safe_failure(nonzero.cases.AnnexWebContractError('VALUE','row/value'));self.assertEqual(failure['code'],'XML_CONTRACT')
  self.assertEqual(nonzero.contract_diagnostic(nonzero.cases.AnnexWebContractError('VALUE','row/value')),{'contractCode':'VALUE','contractFieldId':5})


class OriginalMessageDiagnosticContract(unittest.TestCase):
 """Run 42155339676 stopped at gtgt-export-original-message-rejected right after the
 original Kết xuất click (selector never shown) with parent 1 at 50/50. The text was
 deliberately not published; these fields report only its pinned catalogue ID."""
 def test_rejected_original_messages_report_only_a_bounded_catalogue_id(self):
  registry=json.loads((ROOT/'htkk-native-automation-registry.json').read_text())['resultFields']
  for key in ('exportRejectedMessageId','importRejectedMessageId'):
   self.assertEqual({k:registry[key][k] for k in ('kind','default','minimum','maximum')},{'kind':'integer','default':0,'minimum':0,'maximum':9999});self.assertNotIn('activeModes',registry[key])
  export=(ROOT/'HtkkGtgtExportInspection.cs').read_text(encoding='utf-8');roundtrip=(ROOT/'HtkkGtgtRoundtripInspection.cs').read_text(encoding='utf-8');start=(ROOT/'HtkkGuiReferenceAutomation.cs').read_text(encoding='utf-8')
  self.assertIn('{exportRejectedMessageId=OriginalMessageCatalogueId(labels[0].Text);SetStage(HtkkAutomationStage.GtgtExportOriginalMessageRejected);',export)
  self.assertIn('{importRejectedMessageId=OriginalMessageCatalogueId(labels[0].Text);SetStage(',roundtrip)
  block=export[export.index(' private int OriginalMessageCatalogueId('):export.index(' private static string EscapeSendKeys(')]
  pin='586fa399b2996c84eadfa5fbad74dfdeb0d1e349e27cee355a22f92e14474606'
  self.assertIn(pin,block);self.assertIn('Path.Combine(project,"Message.xml")',start+block);self.assertIn(pin,start)
  for term in ('settings.ProhibitDtd=true','settings.XmlResolver=null','/Message/Infor[@ID and @Msg]','node.Attributes["Msg"].Value.Trim()==wanted','return 9999;','value>9998'):self.assertIn(term,block)
  for forbidden in ('Record()','Contains(','StartsWith(','IndexOf('):self.assertNotIn(forbidden,block)
  # The message text never enters the public JSON; only the numeric ID does.
  json_block=export[export.index(' private string ExportJson('):export.index(' private static void FindExportSelectors(')]
  self.assertIn('"exportRejectedMessageId"+q+":"+exportRejectedMessageId',json_block);self.assertNotIn('labels',json_block)

 def test_import_display_mask_is_observation_only_and_bounded(self):
  """Runs 42156474982/42156478348: import and annex checks passed, then the
  original reexport was rejected. Blank display cells are recorded, never typed."""
  registry=json.loads((ROOT/'htkk-native-automation-registry.json').read_text())['resultFields']['annex12WebImportDisplayEmptyMask']
  self.assertEqual((registry['maximum'],registry['activeModes']),(33554431,['gtgt-web-import-inspect']))
  annex=(ROOT/'HtkkGtgtAnnex12ExportInspection.cs').read_text(encoding='utf-8')
  block=annex[annex.index(' private bool InspectOriginalImportedAnnex12('):]
  self.assertIn('int[] display=new int[]{2,12,16,17,18};',block);self.assertIn('annex12WebImportDisplayEmptyMask|=1<<(ordinal*5+k)',block);self.assertIn('ordinal<5',block)
  self.assertIn('annex12WebImportDisplayEmptyMask=0;',block)


class Header66RuleContract(unittest.TestCase):
 """Run 42173347454: exportRejectedMessageId=16 (frmWinToKhai.cmdExport_Click shows 0016
 when a tab is pink). Pinned 01_GTGT_TT80_283.xls Header!B66 is the only workbook check
 that depends on the edited parent tax: 01_2!AJ7 (=T46, ct13) must not exceed 01!L59 ([40])."""
 def test_plant_tax_cases_enter_the_sale10_main_vector_through_the_original_editor(self):
  sheet=(ROOT/'HtkkGtgtPeriodAndSheet.cs').read_text(encoding='utf-8');annex=(ROOT/'HtkkGtgtAnnex12ExportInspection.cs').read_text(encoding='utf-8')
  self.assertIn('private bool Annex12SaleMain(){return mode=="gtgt-annex12-export-nonzero"||(mode=="gtgt-web-import-inspect"&&webInputVerified&&webCaseId==Annex12WebTwoPlantsCaseId);}',sheet)
  block=sheet[sheet.index(' private bool PrepareAnnex12SaleMain('):sheet.index(' private void InspectOriginalAnnex12(Control grid){')]
  self.assertIn('EditOriginalGtgtCase(grid,sheet,47,9,"1000000",HtkkAutomationStage.GtgtCaseEditing)',block)
  for forbidden in ('SetValue','set_Value','SetPublic','"Formula"'):self.assertNotIn(forbidden,block)
  self.assertIn('if(mode=="gtgt-annex12-export-nonzero")fixedInput=webCaseEditCount==0&&row==47&&column==9&&value=="1000000";',sheet)
  probe=sheet[sheet.index('if(matched&&mode=="gtgt-annex12-export-nonzero"){'):]
  self.assertLess(probe.index('PrepareAnnex12SaleMain(grid,sheet)'),probe.index('InspectOriginalAnnex12(grid)'))
  # Mask of the 27 main money cells carrying the sale10 vector (ct27/28/32/33/34/35/36/40a/40).
  order=('ct22','ct23','ct24','ct23a','ct24a','ct25','ct26','ct27','ct28','ct29','ct30','ct31','ct32','ct33','ct32a','ct34','ct35','ct36','ct37','ct38','ct39a','ct40a','ct40b','ct40','ct41','ct42','ct43')
  mask=sum(1<<order.index(name) for name in nonzero.SALE10);self.assertEqual(mask,10727808);self.assertEqual(nonzero.SALE10_NONZERO_MASK,mask)
  self.assertEqual(nonzero.SALE10,w.SALE10);self.assertEqual(w.CASE_MONEY[TWO],w.SALE10);self.assertEqual(w.CASE_MONEY[ZERO],{})
  self.assertIn('gtgtCaseNonzeroMask==10727808',annex)
  ps=(ROOT/'probe-htkk-windows.ps1').read_text()
  self.assertIn('$lastGui.gtgtCaseNonzeroMask -eq 10727808 -and $lastGui.webCaseEditCount -eq 1',ps)
  self.assertIn("($lastGui.gtgtMonetaryZero -or $GuiAutomation -eq 'gtgt-annex12-export-nonzero')",ps)
 def test_plant_tax_never_exceeds_main_ct40_in_any_fixed_contract(self):
  self.assertLessEqual(int(contract.CASES[TWO]['ct13']),int(w.CASE_MONEY[TWO]['ct40']))
  self.assertLessEqual(max(v['parent'] for v in nonzero.VARIANTS.values()),int(nonzero.SALE10['ct40']))
  self.assertEqual(int(contract.CASES[ZERO]['ct13']),0)
  # Snapshots whose main sheet lost the sale vector are refused before retention.
  bare=zero_export.edited(snapshot(NAMES[0]),lambda root:setattr(root.find('.//'+NS+'ct40'),'text','0'))
  with self.assertRaises(nonzero.cases.AnnexWebContractError):nonzero.validate_snapshot(bare,NAMES[0],zero_export.TODAY)


class ImportedHeadAuthorityContract(unittest.TestCase):
 """Runs 42182681228 (zero) and 42182684607 (two plants): import matched, then reexport refused
 with 0016. annex12WebImportDisplayEmptyMask 264 / 8659208 = bit 3 of every child, i.e. R
 (pathCucThue, head-CQT display) blank after the ORIGINAL import. Header row 83 of the pinned
 workbook requires R44 ("Chỉ tiêu bắt buộc nhập"); R is not an XML leaf."""
 def test_masks_decode_to_the_head_authority_column_of_every_child(self):
  display=(2,12,16,17,18)
  for mask,rows in ((264,2),(8659208,5)):
   bits=[i for i in range(25) if mask>>i&1]
   self.assertEqual(bits,[r*5+display.index(17) for r in range(rows)])
  workbook_rule="A83={01_2!R44:R44}'cbo' | B83={IF(TRIM(01_2!R44:R44)=\"\",0.0,1.0)}"
  self.assertIn('R44',workbook_rule)
 def test_restoration_uses_original_combo_editor_only_and_precedes_the_reexport(self):
  annex=(ROOT/'HtkkGtgtAnnex12ExportInspection.cs').read_text(encoding='utf-8');roundtrip=(ROOT/'HtkkGtgtRoundtripInspection.cs').read_text(encoding='utf-8')
  block=annex[annex.index(' private void RestoreImportedAnnex12HeadAuthorities('):]
  self.assertIn('SelectImportedAnnex12Combo(grid,annex,row,17,"Thuế Thành phố Hà Nội")',block)
  self.assertIn('SelectImportedAnnex12Combo(grid,annex,row,18,"Thuế cơ sở 16 Thành phố Hà Nội")',block)
  self.assertIn('SetPublic(vendor,"SelectedIndex",selected)',block);self.assertIn('FindVendorCombo(editor,0)',block)
  # Only the vendor combo index and the public sheet selection are set; never a cell value or code.
  for forbidden in ('set_Value','"Value",','"Text",','"Formula"','InsertTable','SendKeys'):self.assertNotIn(forbidden,block)
  self.assertEqual(block.count('SetValue('),1);self.assertIn('active.SetValue(grid,found,null)',block)
  self.assertIn('if((column!=17&&column!=18)',block)
  for code in ('CellText(annex,row,35)!="10100"','CellText(annex,row,36)!="10129"','CellText(annex,row,33)!="101"','CellText(annex,row,42)!="10129087"'):self.assertIn(code,block)
  phase=roundtrip[roundtrip.index('if(roundtripPhase=="waiting-reexport-ready"){'):]
  self.assertLess(phase.index('RestoreImportedAnnex12HeadAuthorities()'),phase.index('Named(roundtripOwner,"cmdExport")'))
  self.assertIn('if(!annex12WebHeadAuthorityRestored&&ordinal<5',annex)
  registry=json.loads((ROOT/'htkk-native-automation-registry.json').read_text())['resultFields']
  self.assertEqual((registry['annex12WebHeadAuthorityRepairCount']['maximum'],registry['annex12WebHeadAuthorityRepairCount']['activeModes']),(10,['gtgt-web-import-inspect']))
  probe=(ROOT/'probe-htkk-windows.ps1').read_text()
  self.assertIn('-and $lastGui.annex12WebHeadAuthorityRestored -and $lastGui.annex12WebHeadAuthorityRepairCount -ge $lastGui.annex12WebImportRowCount -and $lastGui.annex12WebHeadAuthorityRepairCount -le (2*$lastGui.annex12WebImportRowCount)',probe)
  self.assertIn("'annex12WebImportSheetMatched','annex12WebHeadAuthorityRestored')",probe)
  self.assertIn("-and ($lastGui.annex12WebHeadAuthorityFailureMask -band 2047) -eq 0",probe)
 def test_restoration_leaves_each_cell_before_reading_original_codes(self):
  """Runs 42206910531 (zero) and 42206915586 (two plants): RepairCount 2, Restored false in both,
  i.e. the run stopped right after the second original combo action of the first child. The
  restoration now moves to S before reading it and to the child's percentage before reading the
  hidden codes, waits (bounded), and reports which check was unmet."""
  annex=(ROOT/'HtkkGtgtAnnex12ExportInspection.cs').read_text(encoding='utf-8')
  block=annex[annex.index(' private void RestoreImportedAnnex12HeadAuthorities('):]
  loop=block[:block.index(' private void SelectImportedAnnex12Combo(')]
  order=[loop.index(x) for x in ('SelectImportedAnnex12Combo(grid,annex,row,17,','MoveImportedAnnex12Cell(grid,annex,row,18);','SelectImportedAnnex12Combo(grid,annex,row,18,','MoveImportedAnnex12Cell(grid,annex,row,20);','WaitImportedAnnex12HeadAuthority(annex,row,1.0)','PassImportedAnnex12Percentage(grid,annex,row)')]
  self.assertEqual(order,sorted(order))
  self.assertIn('annex12WebHeadAuthorityFailureMask&=2048;annex12WebHeadAuthorityRestored=true;',loop)
  move=block[block.index(' private void MoveImportedAnnex12Cell('):block.index(' private void PassImportedAnnex12Percentage(')]
  self.assertIn('if((column!=18&&column!=20)',move);self.assertIn('Annex12CellLocked(annex,row,column)',move)
  passing=block[block.index(' private void PassImportedAnnex12Percentage('):]
  # The percentage editor is opened and closed with no key; its original value must be unchanged.
  for forbidden in ('SendKeys','SetPublic','set_Value','"Text",'):self.assertNotIn(forbidden,passing)
  self.assertIn('!=before',passing)
  registry=json.loads((ROOT/'htkk-native-automation-registry.json').read_text())['resultFields']
  self.assertEqual((registry['annex12WebHeadAuthorityFailureMask']['maximum'],registry['annex12WebHeadAuthorityFailureMask']['activeModes']),(4095,['gtgt-web-import-inspect']))

if __name__=='__main__':unittest.main()
