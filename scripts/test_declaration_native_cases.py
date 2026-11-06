"""Offline contracts for the declaration-family native driver (declaration-web-import-inspect).

XML here is synthetic, assembled in memory from the reviewed contract (declaration_test_support);
it is not a product or original export and passing these tests is never native evidence.
"""
import base64, copy, datetime, hashlib, importlib.util, json, pathlib, re, shutil, subprocess, tempfile, unittest, urllib.error

ROOT = pathlib.Path(__file__).parent


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / file); value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value); return value


registry = load('declaration_registry_test', 'htkk_native_cases.py')
dfx = load('declaration_fixture_test', 'declaration_test_support.py')
d = dfx.d
reader = load('declaration_reader_test', 'fetch-htkk-web-input.py')
out = load('declaration_output_test', 'publish-htkk-declaration-native-output.py')
d1_out = load('declaration_d1_output_test', 'publish-htkk-web-native-output.py')
failure = load('declaration_failure_callback_test', 'report-native-failure.py')
automation = json.loads((ROOT / 'htkk-native-automation-registry.json').read_text())
CASES = registry.DECLARATION_CASES
MODE = 'declaration-web-import-inspect'
TODAY = datetime.date(2026, 11, 6)
SOURCE, ARTIFACT, BUILDER_SHA = 'a' * 40, 'b' * 40, 'c' * 40
PLANS = (ROOT / 'HtkkDeclarationCasePlans.cs').read_text(encoding='utf-8')
DRIVER = (ROOT / 'HtkkDeclarationWebImport.cs').read_text(encoding='utf-8')


def plan_block(case_id):
    match = re.search(r'case "' + re.escape(case_id) + r'":return new HtkkDeclarationCasePlan\((.*?)\);\n', PLANS, re.S)
    return match.group(1)


def native_of(body, case_id, created='2026-11-06'):
    """In-memory native-shaped copy: original service identity and current creation date."""
    spec = d.case(case_id); text = body.decode('utf-8').replace(d.COMMENT + '\n', '')
    for web, native in zip(spec['webService'], (*d.NATIVE_SERVICE, 'A' * 32)):
        text = text.replace('>' + web + '<', '>' + native + '<', 1)
    text = text.replace('<ngayLapTKhai>' + spec['createdDate'] + '<', '<ngayLapTKhai>' + created + '<', 1)
    return text.encode('utf-8')


class Registry(unittest.TestCase):
    def test_one_case_per_form_all_candidates_with_own_driver_and_status(self):
        self.assertEqual([registry.CASES[c]['unit']['menuId'] for c in CASES], ['N8', 'A2', '78', 'L7', 'B9', 'U5'])
        self.assertEqual(set(CASES), set(d.CASES))
        self.assertEqual(len(registry.GATE_CASES), 13)
        for case in CASES:
            c = registry.CASES[case]; a = registry.ADAPTERS[c['adapterId']]
            self.assertIs(c['releaseGate'], False)
            self.assertEqual(a['driver'], MODE); self.assertEqual(a['producer'], 'scripts/generate-htkk-declaration-reference.mjs'); self.assertEqual(a['privacyValidator'], 'declaration-v1')
            self.assertEqual(c['statusContext'], 'htkk-native/' + c['producerCase']); self.assertEqual(c['producerCase'], d.CASES[case]['producerCase'])
            self.assertTrue(c['inputBranch'].startswith('declaration-web-reference-') and c['outputBranch'].startswith('declaration-web-native-'))
            self.assertEqual(c['unit']['adapterVersion'], d.CASES[case]['xmlVersion'])

    def test_registry_rejects_untrusted_menu_driver_period_annex_or_gate(self):
        raw = json.loads((ROOT / 'htkk-native-cases.json').read_text())
        index = next(i for i, c in enumerate(raw['cases']) if c['caseId'] == '03TNDN-profit20-Y2025')
        adapter = next(i for i, a in enumerate(raw['adapters']) if a['adapterId'] == '03-tndn-2.9.4')
        mutations = (lambda r: r['adapters'][adapter].update(menuId='N9'), lambda r: r['adapters'][adapter].update(driver='gtgt-web-import-inspect'),
                     lambda r: r['adapters'][adapter].update(producer='scripts/other.mjs'), lambda r: r['cases'][index]['unit'].update(periodValue='2024'),
                     lambda r: r['cases'][index]['unit'].update(periodType='month'), lambda r: r['cases'][index]['unit'].update(annexes=['03-1A', '03-2']),
                     lambda r: r['cases'][index].update(releaseGate=True), lambda r: r['cases'][index]['unit'].update(adapterVersion='2.9.2'))
        for mutate in mutations:
            value = copy.deepcopy(raw); mutate(value)
            with self.subTest(), tempfile.TemporaryDirectory() as directory, self.assertRaises((ValueError, KeyError)):
                folder = pathlib.Path(directory); (folder / 'htkk-native-cases.json').write_text(json.dumps(value)); target = folder / 'htkk_native_cases.py'
                target.write_text((ROOT / 'htkk_native_cases.py').read_text())
                spec = importlib.util.spec_from_file_location('mutated_declaration_registry', target); module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)

    def test_plan_accepts_gate_only_or_complete_source_plans(self):
        def row(case):
            c = registry.CASES[case]; a = registry.ADAPTERS[c['adapterId']]
            return {'caseId': case, 'adapterId': c['adapterId'], 'producerCase': c['producerCase'], 'unit': c['unit'], 'producer': a['producer'], 'profilePolicy': a['profilePolicy'], 'coverageGranted': False, 'descriptorFingerprint': 'f' * 64}
        base = {'format': 'htkk-case-plan-v1', 'htkkVersion': '5.8.1', 'nativeQualified': False, 'filingEnabled': False}
        registry.validate_plan({**base, 'nativeCases': [row(c) for c in registry.GATE_CASES]})
        registry.validate_plan({**base, 'nativeCases': [row(c) for c in registry.CASES]})
        with self.assertRaises(ValueError):
            registry.validate_plan({**base, 'nativeCases': [row(c) for c in (*registry.GATE_CASES, CASES[0])]})


class CompiledPlans(unittest.TestCase):
    def test_compiled_case_ids_and_identity_match_the_trusted_registry(self):
        ids = re.search(r'CaseIds=new string\[\]\{([^}]*)\}', PLANS).group(1)
        self.assertEqual(re.findall(r'"([^"]+)"', ids), list(CASES))
        for case in CASES:
            block = plan_block(case); spec = d.CASES[case]; unit = registry.CASES[case]['unit']
            head = re.findall(r'"([^"]*)"', block)
            self.assertTrue(block.startswith('caseId,"' + spec['menuId'] + '"'))
            self.assertEqual(head[:4], [spec['menuId'], spec['xmlVersion'], spec['maTKhai'], 'TAX.HTKK.Business.'[:0] + head[3]])
            self.assertIn('"' + spec['schemaId'] + '"', block)
            self.assertIn(',' + str(spec['leafCount']) + ',', block)
            self.assertIn('"' + spec['webService'][1] + '"', block.replace('WorkbookService', '"Công cụ Kê khai — bản nháp"').replace('CnkdService', '"Công cụ Kê khai — bản nháp"'))
            kind = {'month': 'month', 'quarter': 'quarter', 'year': 'year'}[unit['periodType']]
            self.assertIn('"' + kind + '"', block)

    def test_menu_chain_kieuky_and_annexes_follow_menu_xml_design_units(self):
        units = load('declaration_workbook_units', 'htkk_workbook_native_cases.py').UNITS
        chains = {'N8': units['N8']['menuChain'], 'A2': units['A2']['menuChain'], '78': units['78']['menuChain'], 'L7': ['101', '101_11', 'L7'], 'B9': ['101', '101_11', 'B9'], 'U5': ['101', '101_37', 'U5']}
        kieu = {'N8': '11', 'A2': '26', '78': '26', 'L7': '19', 'B9': '12', 'U5': '21'}
        for case in CASES:
            menu = d.CASES[case]['menuId']; block = plan_block(case)
            self.assertIn('new string[]{' + ','.join('"' + x + '"' for x in chains[menu]) + '}', block)
            self.assertIn('"' + kieu[menu] + '"', block)
            annexes = re.search(r'false,\s*new string\[(?:0)?\]\{?([^}]*)\}?,new string\[\]\{"|true,\s*new string\[\]\{([^}]*)\}', block, re.S)
            annex_text = (annexes.group(1) or annexes.group(2) or '') if annexes else ''
            self.assertEqual(len(re.findall(r'"([^"]+)"', annex_text)), len(registry.CASES[case]['unit']['annexes']), case)

    def test_compiled_xml_checks_are_the_independent_oracle_expectations(self):
        for case in CASES:
            block = plan_block(case).replace('Main+"', '"HSoThueDTu/HSoKhaiThue/CTieuTKhaiChinh/')
            checks = re.findall(r'"(HSoThueDTu/[^"|]+)\|([^"]*)"', block)
            self.assertTrue(0 < len(checks) <= 24)
            fixture = dfx.declaration_fixture(case); leaves = dict(d.leaves(d._parse(fixture, True)))
            family = d.CASES[case]['family']
            if family == 'workbook':
                self.assertEqual(dict(checks), d._workbook_expected[case])
            elif family == 'descriptor':
                self.assertEqual({p.rsplit('/', 1)[1]: v for p, v in checks}, d._descriptor_expected[case][0])
            else:
                hkd = d.hkd_design.expected(case)
                self.assertEqual([v for _, v in checks], [hkd['soThueGTGT_ct14'][0], hkd['soThueTNCN_ct17'][0], hkd['tongTienCT47'][0]])
            for path, value in checks:
                if family == 'workbook':
                    self.assertEqual(leaves[path], value)

    def test_driver_only_acts_through_original_controls(self):
        for forbidden in ('SetPublic(', '"Value",', 'XmlWriter', '.Save(', 'InvokeMember', 'GetMethod("Tinh', 'Cell.Value='):
            self.assertNotIn(forbidden, DRIVER)
        for original in ('"cmdImportXML"', '"cmdExport"', '"radKetXuatXML"', '"btnDongY"', 'RaiseOriginalMenuClick', 'TrySubmitOriginalFileDialog', 'OriginalMessageCatalogueId', '"Nhập dữ liệu từ XML thành công."', '"Kết xuất tờ khai xml thành công."'):
            self.assertIn(original, DRIVER)
        core = (ROOT / 'HtkkGuiReferenceAutomation.cs').read_text(encoding='utf-8')
        self.assertIn('if(modeEnum==HtkkAutomationMode.DeclarationWebImportInspect)adapter=new HtkkDeclarationAdapter();else adapter=new HtkkGtgtAdapter();', core)
        self.assertIn('+SheetJson()+ExportJson()+DeclarationJson();', (ROOT / 'HtkkGtgtReferenceNavigation.cs').read_text(encoding='utf-8'))
        self.assertIn('mode=="gtgt-web-import-inspect"||mode=="declaration-web-import-inspect"?webImportInputSha256', (ROOT / 'HtkkWebInputReference.cs').read_text(encoding='utf-8'))

    @unittest.skipUnless(shutil.which('mcs') and shutil.which('mono'), 'local CLR comparison smoke test needs mono')
    def test_compiled_tree_comparison_matches_python_oracle(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = pathlib.Path(directory)
            (folder / 'T.cs').write_text('using System;using System.Xml;class T{static XmlDocument L(string p){XmlReaderSettings s=new XmlReaderSettings();s.ProhibitDtd=true;s.XmlResolver=null;XmlDocument d=new XmlDocument();d.XmlResolver=null;using(XmlReader r=XmlReader.Create(p,s))d.Load(r);return d;}static void Main(string[] a){int l,m;bool ok=HtkkDeclarationTreeComparison.Compare(L(a[0]),L(a[1]),int.Parse(a[2]),out l,out m);Console.Write(ok+" "+l+" "+m);}}')
            subprocess.run(['mcs', '-langversion:ISO-2', '-warn:0', '-r:System.Xml.dll', '-out:' + str(folder / 't.exe'), str(folder / 'T.cs'), str(ROOT / 'HtkkDeclarationTreeComparison.cs')], check=True, capture_output=True)
            for case in CASES:
                web = dfx.declaration_fixture(case); native = native_of(web, case)
                for name, body in (('web.xml', web), ('native.xml', native), ('bad.xml', native.replace(b'<tenNNT>NNT', b'<tenNNT>XNT', 1))):
                    (folder / name).write_bytes(body)
                for target in ('native.xml', 'bad.xml'):
                    expected = d.compare_tree(web, (folder / target).read_bytes())
                    got = subprocess.run(['mono', str(folder / 't.exe'), str(folder / 'web.xml'), str(folder / target), str(d.tax_leaf_count(case))], check=True, capture_output=True, text=True).stdout.split()
                    self.assertEqual(got, [str(expected['allTaxValuesMatched']), str(expected['checkedTaxLeafCount']), str(expected['mismatchSectionMask'])], case)


class InputPrivacy(unittest.TestCase):
    def test_every_case_fixture_and_manifest_accepted(self):
        for case in CASES:
            body = dfx.declaration_fixture(case); manifest = dfx.declaration_manifest(body, case)
            self.assertEqual(reader.validate_web_xml(body, case_id=case, manifest=manifest)['leafCount'], d.CASES[case]['leafCount'])
            self.assertEqual(reader.validate_manifest(json.dumps(manifest, ensure_ascii=False).encode())['caseId'], case)
            self.assertEqual(reader.names(case), ('declaration-web.xml', 'manifest.json'))

    def test_identity_privacy_period_service_structure_and_values_fail_closed(self):
        case = '05KK-withheld-M10-2026'; body = dfx.declaration_fixture(case)
        mutations = {
            'real name': (b'<tenNNT>NNT KIEM THU GIA LAP - KHONG NOP', b'<tenNNT>CONG TY THAT'),
            'other mst': (b'<mst>9999999997', b'<mst>0100109106'),
            'service': (d.WORKBOOK_SERVICE.encode(), b'HTKK'),
            'period': (b'<kyKKhai>10/2026', b'<kyKKhai>11/2026'),
            'value': (b'<ct32>100001', b'<ct32>100000'),
            'free text': (b'<pad0>0', b'<pad0>Nguyen Van A'),
            'version': (b'<pbanTKhaiXML>2.9.3', b'<pbanTKhaiXML>2.9.2'),
            'signing date': (b'<ngayKy>2026-10-27', b'<ngayKy>2026-10-28'),
        }
        for name, (old, new) in mutations.items():
            self.assertIn(old, body, name)
            with self.subTest(name=name), self.assertRaises(reader.InputError):
                reader.validate_web_xml(body.replace(old, new, 1), case_id=case)
        for extra in (b'<!-- secret -->', b'<?private x?>', b'<!DOCTYPE x>'):
            with self.subTest(extra=extra), self.assertRaises(reader.InputError):
                reader.validate_web_xml(body + extra, case_id=case)
        with self.assertRaises(reader.InputError):
            reader.validate_web_xml(body.replace(b'<pad0>0</pad0>', b'', 1), case_id=case)  # leaf count
        with self.assertRaises(reader.InputError):
            reader.validate_web_xml(body.replace(b'xmlns="http://kekhaithue.gdt.gov.vn/TKhaiThue"', b'xmlns="http://kekhaithue.gdt.gov.vn/TKhaiThue" xmlns:x="urn:x"', 1), case_id=case)

    def test_cases_cannot_be_relabelled_or_routed_through_the_d1_validator(self):
        for case in CASES:
            body = dfx.declaration_fixture(case)
            for other in (c for c in CASES if c != case):
                with self.subTest(case=case, other=other), self.assertRaises(reader.InputError):
                    reader.validate_web_xml(body, case_id=other)
            with self.assertRaises(reader.InputError):
                reader.validate_web_xml(body, case_id='01GTGT-zero-M10-2026')

    def test_staging_writes_only_the_case_names(self):
        case = CASES[0]; body = dfx.declaration_fixture(case)
        files = {'declaration-web.xml': body, 'manifest.json': json.dumps(dfx.declaration_manifest(body, case), ensure_ascii=False).encode()}
        with tempfile.TemporaryDirectory() as directory:
            target = reader.stage(files, directory)
            self.assertEqual(sorted(p.name for p in target.iterdir()), ['declaration-web.xml', 'manifest.json']); self.assertEqual((target / 'declaration-web.xml').read_bytes(), body)
        with tempfile.TemporaryDirectory() as directory, self.assertRaises(reader.InputError):
            reader.stage({'01GTGT-web.xml': body, 'manifest.json': files['manifest.json']}, directory)


class NativeOutput(unittest.TestCase):
    def provenance(self, web, native, case, matched=True, mask=0):
        return {'format': 'htkk-declaration-native-output-staging-v1', 'builderRepository': out.BUILDER, 'builderCommit': BUILDER_SHA, 'runId': '123', 'runAttempt': 1, 'sourceRepository': out.REPO, 'sourceCommit': SOURCE, 'sourceVersion': '5.8.1',
                'runtimeHost': 'clr2-x86-reference', 'caseId': case, 'artifactCommit': ARTIFACT, 'inputsSynthetic': True, 'originalProcessStopped': True, 'originalSourcesUnmodified': True, 'originalImportSucceeded': True, 'originalExportSucceeded': True,
                'originalExporterValidatedSchema': True, 'webImportInputSha256': hashlib.sha256(web).hexdigest(), 'originalOutputSha256': hashlib.sha256(native).hexdigest(), 'originalOutputBytes': len(native),
                'harnessSchemaValid': True, 'harnessTreeMatched': matched, 'harnessTreeMismatchMask': mask, 'harnessTreeLeafCount': d.tax_leaf_count(case), 'harnessXmlMismatchMask': 0, 'harnessCellMismatchMask': 0,
                'creationDateRule': 'native-export-current-date', 'fullRoundTrip': False}

    def fake_api(self, web, manifest):
        calls = []
        def envelope(body, name):
            return {'type': 'file', 'name': name, 'path': name, 'encoding': 'base64', 'size': len(body), 'content': base64.encodebytes(body).decode(), 'sha': hashlib.sha1(b'blob ' + str(len(body)).encode() + b'\0' + body).hexdigest()}
        def fetch(path, token, payload=None, method=None):
            calls.append((path, token, payload, method))
            if path == '':return {'private': True, 'full_name': out.REPO}
            if path in ('/git/commits/' + SOURCE, '/git/commits/' + ARTIFACT):return {'sha': path.rsplit('/', 1)[1]}
            if path == '/contents/manifest.json?ref=' + ARTIFACT:return envelope(json.dumps(manifest, ensure_ascii=False).encode(), 'manifest.json')
            if path == '/contents/declaration-web.xml?ref=' + ARTIFACT:return envelope(web, 'declaration-web.xml')
            if path == '/git/blobs':
                body = base64.b64decode(payload['content']); return {'sha': hashlib.sha1(b'blob ' + str(len(body)).encode() + b'\0' + body).hexdigest()}
            if path == '/git/trees':return {'sha': 'd' * 40}
            if path == '/git/commits':return {'sha': 'e' * 40}
            if path.startswith('/git/ref/heads/'):raise urllib.error.HTTPError('https://api.github.com/', 404, 'SECRET', {}, None)
            if path == '/git/refs':return {'ref': payload['ref'], 'object': {'type': 'commit', 'sha': payload['sha']}}
            raise AssertionError('Unexpected fixed API path')
        return fetch, calls

    def test_native_identity_fresh_date_and_synthetic_texts_required(self):
        for case in CASES:
            web = dfx.declaration_fixture(case); native = native_of(web, case)
            self.assertTrue(out.validate_native(native, case, TODAY)['nativeServiceIdentityVerified'])
            self.assertTrue(d.compare_tree(web, native)['allTaxValuesMatched'])
            for body, code in ((web.replace((d.COMMENT + '\n').encode(), b''), 'NATIVE_IDENTITY'), (web if d.COMMENT.encode() in web else web + b'<!-- x -->', 'XML_DECLARATION'), (native_of(web, case, '2026-10-01'), 'NATIVE_DATE'), (native.replace(b'<pad0>0', b'<pad0>PRIVATE CUSTOMER', 1), 'XML_PRIVACY')):
                with self.subTest(case=case, code=code), self.assertRaises(out.OutputError) as error:
                    out.validate_native(body, case, TODAY)
                self.assertEqual(error.exception.code, code)

    def test_whole_tree_mask_reports_sections_without_values(self):
        case = '05QTT-two-employees-Y2025'; web = dfx.declaration_fixture(case); native = native_of(web, case)
        self.assertEqual(d.compare_tree(web, native.replace(b'<tenNNT>NNT', b'<tenNNT>XNT', 1))['mismatchSectionMask'], 4)
        self.assertEqual(d.compare_tree(web, native.replace(b'<ct16>2</ct16>', b'<ct16>3</ct16>', 1))['mismatchSectionMask'], 8)
        self.assertEqual(d.compare_tree(web, native.replace(b'<ct08>0</ct08>', b'<ct08>1</ct08>', 1))['mismatchSectionMask'], 16)
        self.assertEqual(d.compare_tree(web, native.replace(b'<pad0>0</pad0>', b'', 1))['mismatchSectionMask'], 32 | 8)
        changed = native.replace(b'<ngayLapTKhai>2026-11-06', b'<ngayLapTKhai>2026-11-07', 1)
        self.assertTrue(d.compare_tree(web, changed)['allTaxValuesMatched'])  # creation date: proven native rule only

    def test_byte_exact_retention_with_comparison_even_when_mismatched(self):
        for case in CASES:
            web = dfx.declaration_fixture(case); manifest = dfx.declaration_manifest(web, case, source=SOURCE)
            for native, matched, mask in ((native_of(web, case), True, 0), (native_of(web, case).replace(b'<tenNNT>NNT', b'<tenNNT>XNT', 1), False, 4)):
                if not matched:
                    with self.assertRaises(out.OutputError):  # privacy still blocks a non-synthetic name
                        out.publish(native, self.provenance(web, native, case, matched, mask), 'synthetic-token', self.fake_api(web, manifest)[0], TODAY)
                    continue
                fetch, calls = self.fake_api(web, manifest)
                result = out.publish(native, self.provenance(web, native, case, matched, mask), 'synthetic-token', fetch, TODAY)
                blobs = [base64.b64decode(p['content']) for path, _, p, _ in calls if path == '/git/blobs']
                self.assertEqual(blobs[0], native); stored = json.loads(blobs[1])
                self.assertTrue(stored['comparison']['allTaxValuesMatched']); self.assertTrue(stored['comparison']['harnessAgreement']); self.assertFalse(stored['qualificationGranted'])
                self.assertEqual(result['artifactCommit'], 'e' * 40); self.assertEqual(stored['comparison']['checkedTaxLeafCount'], d.tax_leaf_count(case))
            # A value mismatch keeps synthetic privacy, is retained, and is recorded as such.
            native = native_of(web, case)
            first = next(p for p, v in d.leaves(d._parse(native, False)) if v == '0' and '/pad' in p).rsplit('/', 1)[1]
            native = native.replace(('<' + first + '>0<').encode(), ('<' + first + '>7<').encode(), 1)
            fetch, calls = self.fake_api(web, manifest)
            result = out.publish(native, self.provenance(web, native, case, False, 8), 'synthetic-token', fetch, TODAY)
            self.assertFalse(result['allTaxValuesMatched']); self.assertEqual(result['mismatchSectionMask'], 8)

    def test_provenance_is_exact_and_publishers_are_separated(self):
        case = CASES[3]; web = dfx.declaration_fixture(case); native = native_of(web, case); value = self.provenance(web, native, case)
        out.validate_provenance(json.dumps(value).encode(), native, '123', BUILDER_SHA, SOURCE, case, ARTIFACT, '1')
        for key, bad in (('harnessTreeMismatchMask', 64), ('harnessSchemaValid', 1), ('fullRoundTrip', True), ('originalOutputBytes', 1), ('runtimeHost', 'original')):
            changed = dict(value); changed[key] = bad
            with self.subTest(key=key), self.assertRaises(out.OutputError):
                out.validate_provenance(json.dumps(changed).encode(), native, '123', BUILDER_SHA, SOURCE, case, ARTIFACT, '1')
        with self.assertRaises(out.OutputError):
            out.validate_provenance(json.dumps(value).encode(), native, '123', BUILDER_SHA, SOURCE, '01GTGT-zero-M10-2026', ARTIFACT, '1')
        self.assertTrue(set(CASES).isdisjoint(d1_out.BRANCHES)); self.assertEqual(set(out.BRANCHES), set(CASES))


class WorkflowAndProbe(unittest.TestCase):
    def test_mode_registered_with_fixed_policies_and_typed_fields(self):
        mode = automation['modes'][MODE]
        self.assertEqual((mode['adapterId'], mode['permit'], mode['terminalStage'], mode['privateArtifactPolicy'], mode['contextPolicy']), ('declaration-web', 'profile-save', 'declaration-web-import-inspected', 'raw-declaration-reexport', 'htkk-native/case'))
        self.assertEqual(mode['orderedCompileInputs'], automation['modes']['inspect']['orderedCompileInputs'])
        for name in ('HtkkDeclarationCasePlans.cs', 'HtkkDeclarationTreeComparison.cs', 'HtkkDeclarationWebImport.cs'):
            self.assertIn(name, mode['orderedCompileInputs'])
        fields = automation['resultFields']
        for key, field in fields.items():
            if key.startswith('declaration'):
                self.assertEqual(field.get('activeModes'), [MODE], key)
        self.assertTrue(set(CASES) <= set(fields['webCaseId']['values']))
        stages = {s['id'] for s in automation['stages'] if s['category'] == 'declaration'}
        probe = (ROOT / 'probe-htkk-windows.ps1').read_text(encoding='utf-8')
        terminal = re.search(r"\$terminal=.*?-in @\(([^)]*)\)", probe).group(1)
        for stage in ('declaration-web-import-inspected', 'declaration-export-not-matched', 'declaration-import-original-message-rejected', 'declaration-export-original-message-rejected', 'declaration-period-inputs-not-matched', 'declaration-period-original-message-rejected'):
            self.assertIn(stage, stages); self.assertIn("'" + stage + "'", terminal)
        self.assertEqual(fields['declarationPeriodRejectedMessageId'], {'kind': 'integer', 'default': 0, 'minimum': 0, 'maximum': 9999, 'activeModes': [MODE]})

    def test_hidden_period_annex_list_is_observed_never_clicked(self):
        plans = (ROOT / 'HtkkDeclarationCasePlans.cs').read_text(encoding='utf-8')
        driver = (ROOT / 'HtkkDeclarationWebImport.cs').read_text(encoding='utf-8')
        # KieuKy 12 layout hides pnVT2_PhuLucKeKhai except for menus 97/H4/C8 (frmHTKKPeriod IL).
        self.assertIn('plan.KieuKy=="12"&&plan.MenuId!="97"&&plan.MenuId!="H4"&&plan.MenuId!="C8"', plans)
        hidden = driver[driver.index('if(hidden){'):driver.index('if(!grid.Visible){declarationAnnexMatched=plan.Annexes.Length==0;return;}')]
        self.assertNotIn('SendKeys', hidden); self.assertNotIn('SetActiveCell', hidden); self.assertNotIn('set_Value', hidden)
        self.assertIn('if(grid.Visible){declarationAnnexMatched=false;return;}', hidden)
        # A modal original refusal of the period confirmation is reported by catalogue ID only.
        block = driver[driver.index('Form periodMessage;'):driver.index('if(forms.Count!=1){SetStage(HtkkAutomationStage.DeclarationSheetWaiting)')]
        self.assertIn('declarationPeriodRejectedMessageId=OriginalMessageCatalogueId(periodText)', block)
        self.assertNotIn('PerformClick', block)

    def test_probe_success_staging_and_workflow_wiring(self):
        probe = (ROOT / 'probe-htkk-windows.ps1').read_text(encoding='utf-8')
        workflow = (ROOT.parent / '.github/workflows/probe-htkk-windows.yml').read_text(encoding='utf-8')
        for flag in ('declarationTreeMatched', 'declarationSchemaValid', 'declarationXmlMismatchMask -eq 0', 'declarationCellMismatchMask -eq 0', 'declarationAnnexMatched', 'declarationIdentityMatched', 'roundtripImportSucceeded', 'exportSuccessAcknowledged', 'importRejectedMessageId -eq 0', 'exportRejectedMessageId -eq 0'):
            self.assertIn(flag, probe)
        self.assertIn("Join-Path $stage $(if($declarationInput){'declaration-web.xml'}else{'01GTGT-web.xml'})", probe)
        self.assertIn("'DataFiles/9999999997/reference-declaration-output/declaration.xml'", probe)
        self.assertIn("format='htkk-declaration-native-output-staging-v1'", probe)
        self.assertIn("$HtkkDeclarationCases=@(" + ",".join("'" + c + "'" for c in CASES) + ")", (ROOT / 'HtkkNativeCaseFormats.ps1').read_text())
        self.assertIn("inputs.gui_automation == 'gtgt-web-import-inspect' || inputs.gui_automation == 'declaration-web-import-inspect'", workflow)
        self.assertIn('run: python ./scripts/publish-htkk-declaration-native-output.py', workflow)
        self.assertIn(MODE, re.search(r'gui_automation:\n.*?options: \[([^\]]+)\]', workflow, re.S).group(1))
        for case in CASES:
            self.assertIn(case, re.search(r'web_case_id:\n.*?options: \[([^\]]+)\]', workflow, re.S).group(1))
        build = (ROOT.parent / '.github/workflows/build.yml').read_text()
        for case in CASES:
            self.assertIn('"$RUNNER_TEMP/' + registry.CASES[case]['stagingDirectory'] + '"', build)

    def test_failure_callback_requires_the_case_driver(self):
        base = {'GITHUB_REPOSITORY': failure.callback.dispatch.BUILDER, 'GITHUB_REF': 'refs/heads/main', 'READINESS_RESULT': 'failure', 'COMMIT_SHA': SOURCE, 'GITHUB_RUN_ID': '42', 'GITHUB_SERVER_URL': 'https://github.com', 'WEB_ARTIFACT_COMMIT': ARTIFACT}
        url, payload = failure.request({**base, 'GUI_AUTOMATION': MODE, 'WEB_CASE_ID': CASES[0]})
        self.assertEqual(payload['context'], registry.CASES[CASES[0]]['statusContext']); self.assertEqual(payload['state'], 'failure')
        for automation_mode, case in ((MODE, '01GTGT-zero-M10-2026'), ('gtgt-web-import-inspect', CASES[0]), ('gtgt-export-inspect', CASES[0])):
            with self.subTest(mode=automation_mode, case=case), self.assertRaises(ValueError):
                failure.request({**base, 'GUI_AUTOMATION': automation_mode, 'WEB_CASE_ID': case})


if __name__ == '__main__':
    unittest.main()
