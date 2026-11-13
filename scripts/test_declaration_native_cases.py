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


def export_day_of(native, case_id):
    """Native-shaped copy where every export-date leaf of the case carries the export day."""
    text = native.decode('utf-8'); created = re.search('<ngayLapTKhai>([^<]*)<', text)[1]
    for path in d.case(case_id)['exportDates']:
        name = path.rsplit('/', 1)[1]; text = re.sub('<' + name + '>[^<]*<', '<' + name + '>' + created + '<', text, count=1)
    return text.encode('utf-8')


class Registry(unittest.TestCase):
    def test_one_case_per_form_all_candidates_with_own_driver_and_status(self):
        self.assertEqual([registry.CASES[c]['unit']['menuId'] for c in CASES], ['N8', 'A2', '78', 'L7', 'Z8', 'B9', 'U5', 'B8', 'I9', 'J1', 'Y8', 'D6', 'Y1', 'X9', 'C9', 'I9', 'Y8', 'J1', 'U5', 'U5', 'N8', 'N8', 'L7', 'Z8'])
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
                for name in ('htkk_oracle.py', 'generate-htkk-oracle-baselines.py', 'htkk-oracle-baselines.json'): (folder / name).write_bytes((ROOT / name).read_bytes())
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
            self.assertIn('"' + spec['webService'][1] + '"', block.replace('WorkbookService', '"Công cụ Kê khai"').replace('CnkdService', '"Công cụ Kê khai"'))
            kind = {'month': 'month', 'quarter': 'quarter', 'year': 'year', 'range': 'range', 'day': 'day'}[unit['periodType']]
            self.assertIn('"' + kind + '"', block)

    def test_menu_chain_kieuky_and_annexes_follow_menu_xml_design_units(self):
        units = load('declaration_workbook_units', 'htkk_workbook_native_cases.py').UNITS
        chains = {'N8': units['N8']['menuChain'], 'A2': units['A2']['menuChain'], '78': units['78']['menuChain'], 'L7': ['101', '101_11', 'L7'], 'Z8': ['101', '101_11', 'Z8'], 'B9': ['101', '101_11', 'B9'], 'U5': ['101', '101_37', 'U5'], 'B8': ['101', '101_11', 'B8'], 'I9': ['101', '101_8', 'I9'], 'Y8': ['101', '101_8', 'Y8'], 'J1': ['101', '101_8', 'J1'], 'D6': ['101', '101_8', 'D6'], 'Y1': ['101', '101_8', 'Y1'], 'X9': ['101', '101_8', 'X9'], 'C9': ['101', '101_8', 'C9']}
        kieu = {'N8': '11', 'A2': '26', '78': '26', 'L7': '19', 'Z8': '14', 'B9': '12', 'U5': '21', 'B8': '12', 'I9': '18', 'Y8': '18', 'J1': '18', 'D6': '22', 'Y1': '22', 'X9': '22', 'C9': '22'}
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
            elif family == 'descriptor' and (case in d.NTNN04 or case in d.NTNN02):
                # 04/NTNN, 02/NTNN TT89: Group/leaf checks under CTieuTKhaiChinh are the design leaves, and the oracle
                # agrees with them; the annex checks are the oracle annex totals.
                main_prefix, annex_prefix = 'HSoThueDTu/HSoKhaiThue/CTieuTKhaiChinh/', 'HSoThueDTu/HSoKhaiThue/PLuc/'
                oracle, annexes = d.ntnn_qt_expected(case)
                self.assertEqual({p[len(main_prefix):]: v for p, v in checks if p.startswith(main_prefix)}, d._descriptor_expected[case][0])
                self.assertEqual({p[len(annex_prefix):]: v for p, v in checks if p.startswith(annex_prefix)}, {a[0] + '/' + k: v for a in annexes for k, v in a[5].items()})
                for name, value in d._descriptor_expected[case][0].items():
                    self.assertEqual(oracle[name], value)
                for path, value in checks:
                    self.assertEqual(leaves[path], value)
            elif family == 'descriptor':
                self.assertEqual({p.rsplit('/', 1)[1]: v for p, v in checks}, d._descriptor_expected[case][0])
            else:
                hkd = d.hkd_design.expected(case)
                self.assertEqual([v for _, v in checks], [hkd['soThueGTGT_ct14'][0], hkd['soThueTNCN_ct17'][0], hkd['tongTienCT47'][0]] +
                                 ([hkd['tongSoThueTNCN_phaiNop'][0], hkd['tongsoThueTNCN_duocGiam'][0]] if 'tongSoThueTNCN_phaiNop' in hkd else []))
            for path, value in checks:
                if family == 'workbook':
                    self.assertEqual(leaves[path], value)

    def test_05qtt_sheet_checks_agree_with_the_xml_checks(self):
        # Release 227 (run 42302313967) failed the imported-sheet check on stale values (mask 1283):
        # the totals cells on sheet 05 must carry the same expectations as their XML leaves
        # (mapping 05_QTT_TNCN_TT80_293.xml: U89 ct35, U92 ct38, U94 ct40, U95 ct41).
        block = plan_block('05QTT-two-employees-Y2025').replace('Main+"', '"HSoThueDTu/HSoKhaiThue/CTieuTKhaiChinh/')
        cells = dict((s_ + '|' + c, v) for s_, c, v in re.findall(r'"(05(?:-1)?)\|([A-Z]+[0-9]+)\|([0-9]+)"', block))
        xml = {p.rsplit('/', 1)[1]: v for p, v in re.findall(r'"(HSoThueDTu/[^"|]+)\|([^"]*)"', block)}
        for cell, leaf in (('05|U89', 'ct35'), ('05|U92', 'ct38'), ('05|U94', 'ct40'), ('05|U95', 'ct41')):
            self.assertEqual(cells[cell], xml[leaf], cell)
        # 05-1 [21] (AE) of the two rows: 300tr-211,2tr-20tr and 200tr-132tr.
        self.assertEqual((cells['05-1|AE24'], cells['05-1|AE25']), ('68800000', '68000000'))
        # Release 231 (run 42316192917, refused cell 2024023 = 05-1!W24, E_52): FinishImportXML recomputes
        # 05-1 BF only for more than one 05-3 row, so the case carries two dependants and the plan
        # checks BI24 = 11tr*12 + (12+6)*4,4tr on the imported sheet.
        self.assertEqual(cells['05-1|BI24'], str(11000000 * 12 + 18 * 4400000))
        web = dfx.declaration_fixture('05QTT-two-employees-Y2025')
        self.assertEqual(web.count(b'<BKeTTinNPT '), 2)

    def test_driver_only_acts_through_original_controls(self):
        for forbidden in ('SetPublic(', '"Value",', 'XmlWriter', '.Save(', 'InvokeMember', 'GetMethod("Tinh', 'Cell.Value='):
            self.assertNotIn(forbidden, DRIVER)
        for original in ('"cmdImportXML"', '"cmdExport"', '"radKetXuatXML"', '"btnDongY"', 'RaiseOriginalMenuClick', 'TrySubmitOriginalFileDialog', 'OriginalMessageCatalogueId', '"Nhập dữ liệu từ XML thành công."', '"Kết xuất tờ khai xml thành công."'):
            self.assertIn(original, DRIVER)
        core = (ROOT / 'HtkkGuiReferenceAutomation.cs').read_text(encoding='utf-8')
        self.assertIn('if(modeEnum==HtkkAutomationMode.DeclarationWebImportInspect)adapter=new HtkkDeclarationAdapter();else adapter=new HtkkGtgtAdapter();', core)
        self.assertIn('+SheetJson()+ExportJson()+DeclarationJson();', (ROOT / 'HtkkGtgtReferenceNavigation.cs').read_text(encoding='utf-8'))
        self.assertIn('KhbsMode()?KhbsImportHash():mode=="gtgt-web-import-inspect"||mode=="declaration-web-import-inspect"?webImportInputSha256', (ROOT / 'HtkkWebInputReference.cs').read_text(encoding='utf-8'))

    def test_0016_refusal_names_pink_cells_by_coordinate_only(self):
        # Release 228 run 42310319856 (05QTT): import and all 11 sheet checks matched, the original
        # export refused with 0016 and the result could not say which sheet/cell was refused.
        start = DRIVER.index(' private void InspectDeclarationRefusedCells(){')
        body = DRIVER[start:DRIVER.index('\n }\n', start)]
        self.assertIn('if(exportRejectedMessageId==16)InspectDeclarationRefusedCells();DeclarationTerminal(', DRIVER)
        self.assertIn('Get(cell,"BackColor")', body); self.assertIn('unchecked((int)0xFFFFC0CB)', body)
        for forbidden in ('"Value"', '"Text"', 'Note', 'set_', 'SetValue', 'PerformClick', 'Invoke(grid', 'SetNodeBackGround'):
            self.assertNotIn(forbidden, body)
        self.assertIn('(index+1)*1000000+(row+1)*1000+(column+1)', body)
        fields = automation['resultFields']
        self.assertEqual(fields['declarationInvalidSheetMask']['maximum'], 65535)
        self.assertEqual(fields['declarationInvalidCellCount']['maximum'], 4096)
        for k in range(1, 5):
            self.assertEqual(fields['declarationInvalidCell%d' % k], {'kind': 'integer', 'default': 0, 'minimum': 0, 'maximum': 16999999, 'activeModes': [MODE]})

    @unittest.skipUnless(shutil.which('mcs') and shutil.which('mono'), 'local CLR comparison smoke test needs mono')
    def test_compiled_tree_comparison_matches_python_oracle(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = pathlib.Path(directory)
            (folder / 'T.cs').write_text('using System;using System.Xml;class T{static XmlDocument L(string p){XmlReaderSettings s=new XmlReaderSettings();s.ProhibitDtd=true;s.XmlResolver=null;XmlDocument d=new XmlDocument();d.XmlResolver=null;using(XmlReader r=XmlReader.Create(p,s))d.Load(r);return d;}static void Main(string[] a){int l,m;string[] dates=a.Length>3?a[3].Split(new char[]{\'|\'},StringSplitOptions.RemoveEmptyEntries):new string[0];bool ok=HtkkDeclarationTreeComparison.Compare(L(a[0]),L(a[1]),int.Parse(a[2]),dates,out l,out m);Console.Write(ok+" "+l+" "+m);}}')
            subprocess.run(['mcs', '-langversion:ISO-2', '-warn:0', '-r:System.Xml.dll', '-out:' + str(folder / 't.exe'), str(folder / 'T.cs'), str(ROOT / 'HtkkDeclarationTreeComparison.cs')], check=True, capture_output=True)
            for case in CASES:
                web = dfx.declaration_fixture(case); native = native_of(web, case); dates = d.case(case)['exportDates']
                exported = export_day_of(native, case)
                for name, body in (('web.xml', web), ('native.xml', native), ('bad.xml', native.replace(b'<tenNNT>NNT', b'<tenNNT>XNT', 1)), ('exported.xml', exported)):
                    (folder / name).write_bytes(body)
                for target in ('native.xml', 'bad.xml', 'exported.xml'):
                    for rule in ((), dates):
                        expected = d.compare_tree(web, (folder / target).read_bytes(), rule)
                        got = subprocess.run(['mono', str(folder / 't.exe'), str(folder / 'web.xml'), str(folder / target), str(d.tax_leaf_count(case)), '|'.join(rule)], check=True, capture_output=True, text=True).stdout.split()
                        self.assertEqual(got, [str(expected['allTaxValuesMatched']), str(expected['checkedTaxLeafCount']), str(expected['mismatchSectionMask'])], (case, target, rule))
                # The case's own rule accepts exactly the export-day shape of the original.
                self.assertTrue(d.compare_tree(web, exported, dates)['allTaxValuesMatched'], case)

    @unittest.skipUnless(shutil.which('mcs') and shutil.which('mono'), 'local CLR comparison smoke test needs mono')
    def test_tree_diagnostics_classify_the_first_difference_without_values(self):
        # Run 43143244393 (U5 3.1.0) ended with mask 40 and the full leaf count: the detail names the attribute class,
        # the number of text differences and the first differing element as a pre-order ordinal of the WEB input.
        program = ('using System;using System.Xml;class T{static XmlDocument L(string p){XmlReaderSettings s=new XmlReaderSettings();s.ProhibitDtd=true;s.XmlResolver=null;XmlDocument d=new XmlDocument();d.XmlResolver=null;using(XmlReader r=XmlReader.Create(p,s))d.Load(r);return d;}'
                   'static void Main(string[] a){int l,m;HtkkDeclarationTreeComparison.Diagnostics x;bool ok=HtkkDeclarationTreeComparison.Compare(L(a[0]),L(a[1]),int.Parse(a[2]),new string[0],out l,out m,out x);'
                   'Console.Write(ok+" "+l+" "+m+" "+x.AttributeMask+" "+x.TextMismatches+" "+x.FirstOrdinal+" "+x.FirstKind+" "+x.Codes[0]+" "+x.Codes[1]+" "+x.Codes[2]+" "+x.Codes[3]);}}')
        case = '01CNKD-TT50-310-pl01-three-groups-Q3-2026'
        web = dfx.declaration_fixture(case); native = native_of(web, case)
        text = native.decode('utf-8')
        def ordinal(body, local):
            import xml.etree.ElementTree as ET
            for index, node in enumerate(ET.fromstring(body).iter(), 1):
                if node.tag.endswith('}' + local):
                    return index
        # The builder fixture is a reduced tree: mutate a native-shaped copy in the three ways the detail must tell apart.
        nil = text.replace('<ct38_ma>', '<ct38_ma xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true">', 1)
        moved = text.replace('<ct40>16000000</ct40>', '<ct40>16000001</ct40>', 1)
        ident = text.replace('<ChiTietThongTinNopTHue>', '<ChiTietThongTinNopTHue id="ID_1">', 1)
        for body in (nil, moved, ident):
            self.assertNotEqual(body, text)
        with tempfile.TemporaryDirectory() as directory:
            folder = pathlib.Path(directory); (folder / 'T.cs').write_text(program)
            subprocess.run(['mcs', '-langversion:ISO-2', '-warn:0', '-r:System.Xml.dll', '-out:' + str(folder / 't.exe'), str(folder / 'T.cs'), str(ROOT / 'HtkkDeclarationTreeComparison.cs')], check=True, capture_output=True)
            (folder / 'web.xml').write_bytes(web)
            def run(body):
                (folder / 'n.xml').write_text(body, encoding='utf-8')
                return subprocess.run(['mono', str(folder / 't.exe'), str(folder / 'web.xml'), str(folder / 'n.xml'), str(d.tax_leaf_count(case))], check=True, capture_output=True, text=True).stdout.split()
            leaves = str(d.tax_leaf_count(case))
            self.assertEqual(run(text), ['True', leaves, '0', '0', '0', '0', '0', '0', '0', '0', '0'])
            self.assertEqual(run(nil), ['False', leaves, '40', '1', '0', str(ordinal(web, 'ct38_ma')), '2', str(ordinal(web, 'ct38_ma') * 100 + 23), '0', '0', '0'])
            self.assertEqual(run(moved), ['False', leaves, '8', '0', '1', str(ordinal(web, 'ct40')), '5', str(ordinal(web, 'ct40') * 100 + 54), '0', '0', '0'])
            self.assertEqual(run(ident), ['False', leaves, '40', '2', '0', str(ordinal(web, 'ChiTietThongTinNopTHue')), '2', str(ordinal(web, 'ChiTietThongTinNopTHue') * 100 + 20), '0', '0', '0'])
            # The native text class names an empty leaf or the synthetic profile MST without any value; one code per element.
            both = text.replace('<ct38_ma>00001</ct38_ma>', '<ct38_ma>9999999997</ct38_ma>', 1).replace('<ct40>16000000</ct40>', '<ct40></ct40>', 1)
            self.assertEqual(run(both)[7:9], [str(ordinal(web, 'ct38_ma') * 100 + 52), str(ordinal(web, 'ct40') * 100 + 51)])
        fields = automation['resultFields']
        for name, maximum in (('declarationTreeAttributeMask', 7), ('declarationTreeTextMismatchCount', 4096), ('declarationTreeFirstMismatchOrdinal', 65535), ('declarationTreeFirstMismatchKind', 7),
                              ('declarationTreeMismatch1', 6553599), ('declarationTreeMismatch2', 6553599), ('declarationTreeMismatch3', 6553599), ('declarationTreeMismatch4', 6553599)):
            self.assertEqual(fields[name], {'kind': 'integer', 'default': 0, 'minimum': 0, 'maximum': maximum, 'activeModes': [MODE]})
        self.assertIn('return json.ToString()+DeclarationEntryJson()+DeclarationTickJson()+DeclarationTreeJson();', DRIVER)


class InputPrivacy(unittest.TestCase):
    def test_every_case_fixture_and_manifest_accepted(self):
        for case in CASES:
            body = dfx.declaration_fixture(case); manifest = dfx.declaration_manifest(body, case)
            self.assertEqual(reader.validate_web_xml(body, case_id=case, manifest=manifest)['leafCount'], d.CASES[case]['leafCount'])
            self.assertEqual(reader.validate_manifest(json.dumps(manifest, ensure_ascii=False).encode())['caseId'], case)
            self.assertEqual(reader.names(case), ('declaration-web.xml', 'manifest.json'))

    def test_manifest_names_the_case_oracle_exactly_where_the_web_writes_it(self):
        # Z8 05/KK-TNCN TT89: the web manifest carries htkkVersion 5.8.2 (the registry case version); no other
        # declaration manifest may carry the key, and the Z8 manifest must.
        # 03/TNDN C7 rate 15% / 17% (HTKK 5.8.2 oracle): the web writes htkkVersion for these producer cases too.
        self.assertEqual(d.MANIFEST_HTKK_VERSION_CASES, frozenset({'05KK-TT89-withheld-Q4-2026', '03TNDN-rate15-Y2025', '03TNDN-rate17-Y2025', '05KK-PBT-two-provinces-Q3-2026', '05KK-TT89-PBT-two-provinces-Q4-2026'}))
        for case in d.MANIFEST_HTKK_VERSION_CASES:
            self.assertEqual(registry.htkk_version(case), '5.8.2')
        case = '05KK-TT89-withheld-Q4-2026'; body = dfx.declaration_fixture(case); manifest = dfx.declaration_manifest(body, case)
        self.assertEqual(manifest['htkkVersion'], '5.8.2')
        self.assertEqual(reader.validate_manifest(json.dumps(manifest, ensure_ascii=False).encode())['htkkVersion'], '5.8.2')
        for bad in ({k: v for k, v in manifest.items() if k != 'htkkVersion'}, dict(manifest, htkkVersion='5.8.1'), dict(manifest, htkkVersion=582)):
            with self.subTest(bad=bad.get('htkkVersion')), self.assertRaises(reader.InputError):
                reader.validate_manifest(json.dumps(bad, ensure_ascii=False).encode())
        other = '05KK-withheld-Q3-2026'; body = dfx.declaration_fixture(other)
        with self.assertRaises(reader.InputError):
            reader.validate_manifest(json.dumps(dict(dfx.declaration_manifest(body, other), htkkVersion='5.8.2'), ensure_ascii=False).encode())

    def test_04ntnn_range_period_oracle_rows_and_totals_fail_closed(self):
        # KieuKy 22: kieuKy Y, kyKKhai = year of the to-date, from/to dates; Decimal oracle NTNN04 on every row.
        case = '04NTNN-TT89-one-subcontractor-2026'; body = dfx.declaration_fixture(case)
        self.assertIn(b'<kieuKy>Y</kieuKy><kyKKhai>2026</kyKKhai><kyKKhaiTuNgay>01/07/2026</kyKKhaiTuNgay><kyKKhaiDenNgay>30/09/2026</kyKKhaiDenNgay>', body)
        mutations = {
            'from date': (b'<kyKKhaiTuNgay>01/07/2026', b'<kyKKhaiTuNgay>01/06/2026'),
            'kieuKy D_D': (b'<kieuKy>Y', b'<kieuKy>D_D'),
            'negative difference': (b'<chenhLech>-300000000', b'<chenhLech>300000000'),
            'still to pay': (b'<SoThueConPNop><quyetToan>3000000', b'<SoThueConPNop><quyetToan>0'),
            'annex row': (b'<ct9>2000000000', b'<ct9>2000000001'),
            'annex total': (b'<tong_ct10>1800000000', b'<tong_ct10>1800000001'),
        }
        for name, (old, new) in mutations.items():
            self.assertIn(old, body, name)
            with self.subTest(name=name), self.assertRaises(reader.InputError):
                reader.validate_web_xml(body.replace(old, new, 1), case_id=case)
        self.assertEqual(d.ntnn04_expected('04NTNN-TT80-one-subcontractor-2026')[0]['DThuTinhThue/chenhLech'], '-400000000')
        # X9 02/NTNN TT89: AF34/AF35 = 02-1 + 02-2 totals; nước cư trú keeps its catalogue code.
        case = '02NTNN-TT89-two-annexes-2026'; body = dfx.declaration_fixture(case)
        for name, (old, new) in {'02-1 ct8': (b'<ct8>2000000000', b'<ct8>2000000001'), 'AF34': (b'<GiaTriHDong><keKhai>3000000000</keKhai><quyetToan>3000000000', b'<GiaTriHDong><keKhai>3000000000</keKhai><quyetToan>2000000000'),
                                 '02-2 total': (b'<tong_ct10>1000000000', b'<tong_ct10>1000000001')}.items():
            self.assertIn(old, body, name)
            with self.subTest(name=name), self.assertRaises(reader.InputError):
                reader.validate_web_xml(body.replace(old, new, 1), case_id=case)
        self.assertEqual(d.ntnn02_expected(case)[0]['SoThueConPhaiNop/quyetToan'], '4000000')
        # C9 02/NTNN TT80: row 2 is DThuChuaGomGTGT, 02-1 rows carry ct10 (số lượng lao động) and its total.
        case = '02NTNN-TT80-two-annexes-2026'; body = dfx.declaration_fixture(case)
        reader.validate_web_xml(body, case_id=case)
        for name, (old, new) in {'02-1 ct10': (b'<ct10>5</ct10>', b'<ct10>6</ct10>'), 'AF35': (b'<DThuChuaGomGTGT><keKhai>2800000000</keKhai><quyetToan>2800000000', b'<DThuChuaGomGTGT><keKhai>2800000000</keKhai><quyetToan>2700000000'),
                                 '02-1 total ct10': (b'<tong_ct10>5</tong_ct10>', b'<tong_ct10>4</tong_ct10>')}.items():
            self.assertIn(old, body, name)
            with self.subTest(name=name), self.assertRaises(reader.InputError):
                reader.validate_web_xml(body.replace(old, new, 1), case_id=case)
        main, annexes = d.ntnn02_expected(case)
        self.assertEqual((main['DThuChuaGomGTGT/quyetToan'], main['ThueTNDNConPNop/quyetToan'], annexes[0][5]), ('2800000000', '4000000', {'tong_ct8': '2000000000', 'tong_ct9': '1800000000', 'tong_ct10': '5'}))

    def test_identity_privacy_period_service_structure_and_values_fail_closed(self):
        case = '05KK-withheld-Q3-2026'; body = dfx.declaration_fixture(case)
        mutations = {
            'real name': (b'<tenNNT>NNT KIEM THU GIA LAP - KHONG NOP', b'<tenNNT>CONG TY THAT'),
            'other mst': (b'<mst>9999999997', b'<mst>0100109106'),
            'service': (d.WORKBOOK_SERVICE.encode(), b'HTKK'),
            'period': (b'<kyKKhai>3/2026', b'<kyKKhai>4/2026'),
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
                'runtimeHost': 'clr2-x86-reference', 'caseId': case, 'artifactCommit': ARTIFACT, 'inputsSynthetic': True, 'originalProcessStopped': True, 'originalSourcesUnmodified': True, 'inputMode': registry.input_mode(case), 'originalImportSucceeded': registry.input_mode(case) in (registry.IMPORT_MODE, registry.IMPORT_TICK_MODE), 'originalExportSucceeded': True,
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

    def test_rejected_native_export_names_rule_leaf_ordinal_and_shape_never_value(self):
        """Release 216: both BCTC native exports were rejected as XML_PRIVACY and never retained,
        so the cause could not be read. The status now carries a bounded rule/ordinal/shape."""
        case = 'BCTC133-B01a-basic-Y2025'; web = dfx.declaration_fixture(case); native = native_of(web, case)
        items = d.leaves(d._parse(native, False))
        ordinal = lambda name: next(i + 1 for i, (p, _) in enumerate(items) if p.endswith('/' + name))
        for old, new, rule, leaf, section, shape in (
                (b'<soLan>0<', b'<soLan>1<', 'IDENTITY', 'soLan', 2, 'numeric-other'),
                (b'<kyKKhai>2025<', b'<kyKKhai>2024<', 'PERIOD', 'kyKKhai', 2, 'numeric-other'),
                (b'<nguoiKy>NGUOI KY GIA LAP<', b'<nguoiKy>Nguoi Ky Gia Lap<', 'PRIVACY', 'nguoiKy', 2, 'case-variant'),
                (b'<nguoiKy>NGUOI KY GIA LAP<', b'<nguoiKy><', 'PRIVACY', 'nguoiKy', 2, 'empty'),
                (b'<pad1>0<', b'<pad1>False<', 'PRIVACY', 'pad1', 8, 'bool-titlecase'),
                (b'<ct200>1800000000<', b'<ct200>1,800,000,000<', 'PRIVACY', 'ct200', 8, 'grouped-number'),
                (b'<ct200>1800000000<', b'<ct200>PRIVATE CUSTOMER<', 'PRIVACY', 'ct200', 8, 'text-other')):
            body = native.replace(old, new, 1); self.assertNotEqual(body, native)
            with self.subTest(rule=rule, shape=shape), self.assertRaises(out.OutputError) as error:
                out.validate_native(body, case, TODAY)
            status = out.safe_failure(error.exception)
            self.assertEqual(status, {'format': 'htkk-declaration-native-output-publication-status-v1', 'status': 'rejected', 'code': 'XML_PRIVACY',
                                      'nativeRule': rule, 'leafOrdinal': ordinal(leaf), 'section': section, 'valueShape': shape})
            for secret in ('PRIVATE', 'Nguoi Ky', '1,800', 'False', '2024'):self.assertNotIn(secret, json.dumps(status, ensure_ascii=False))
        # Unbounded or unknown context never leaves the process.
        self.assertEqual(out.safe_context({'nativeRule': 'X', 'leafOrdinal': 99999, 'section': 3, 'valueShape': 'PRIVATE', 'raw': 'PRIVATE'}), {})
        self.assertEqual(out.safe_failure(out.OutputError('HASH', {'nativeRule': 'PRIVACY'}))['code'], 'HASH')
        self.assertNotIn('nativeRule', out.safe_failure(out.OutputError('HASH', {'nativeRule': 'PRIVACY'})))

    def test_y1_check_key_in_the_code_leaf_is_rejected_with_a_bounded_concat_shape(self):
        """Release 244 (run 42373362877): Y1 retention was refused at leaf 71 (PL02_2_NTNN/.../ct6_ma, section 16,
        text-other); release 246 (run 42380879950) at the same leaf with shape allowed-text-concat (no date piece).
        The 04_1_NTNN_TT89_309.xml control template binds ct6_ma to column CR, where the workbook keeps the locked
        check-key formula CR49 = TRIM(E49)&TRIM(R49)&TRIM(AG49)&TRIM(AM49)&TRIM(AR49)&TRIM(AW49); the import keeps
        formulas of locked cells (fpSpBindDataCell 0x60001a8) and the table export reads the cell value
        (ExportDataTableToTableNode 0x6000050). Only the exact value the oracle recomputes from the case's own
        synthetic inputs is accepted at that one leaf of that one case; any other value is rejected with a bounded
        shape and a value-free piece layout, never the value."""
        case = '04NTNN-TT89-one-subcontractor-2026'; web = dfx.declaration_fixture(case); native = native_of(web, case)
        key = d.check_key(case)
        self.assertEqual(key, 'NHA THAU PHU VIET NAM A - GIẢ LẬPNHA THAU NUOC NGOAI B - GIẢ LẬP'
                              'Dịch vụ, cho thuê máy móc thiết bị, bảo hiểmHD-GL-04115032026')
        tag = ('<ct6_ma>' + key + '<').encode()
        self.assertIn(tag, web); self.assertIn(tag, native)
        self.assertTrue(out.validate_native(native, case, TODAY)['privacyValuesVerified'])
        self.assertTrue(reader.validate_web_xml(web, case_id=case)['privacyValuesVerified'])
        self.assertTrue(d.compare_tree(web, native)['allTaxValuesMatched'])
        items = d.leaves(d._parse(native, False))
        ordinal = next(i + 1 for i, (p, _) in enumerate(items) if p.endswith('/ct6_ma'))
        self.assertEqual(items[ordinal - 1][0], d.CHECK_KEY_PATH)  # leaf 71 of the real export; the padded fixture differs
        stem = key[:-len('15032026')]
        for value, shape, layout in ((stem + '15/03/2026', 'allowed-text-concat-date', 'E.R.AG.AR.dmy=AW'),
                                     (stem + '46096', 'allowed-text-concat', 'E.R.AG.AR.n5=oadate'),
                                     (stem + '20260315', 'allowed-text-concat', 'E.R.AG.AR.n8=yyyyMMdd'),
                                     (stem.replace('HD-GL-041', '0HD-GL-041') + '15032026', 'allowed-text-concat', 'E.R.AG.n1=index.AR.n8=ddMMyyyy'),
                                     (stem.replace('HD-GL-041', '01HD-GL-041') + '15032026', 'allowed-text-concat', 'E.R.AG.n2=code.AR.n8=ddMMyyyy'),
                                     (stem + '15032027', 'allowed-text-concat', 'E.R.AG.AR.n8'),
                                     (stem + 'PRIVATE', 'text-other', None), ('01', None, None)):
            body = native.replace(tag, ('<ct6_ma>' + value + '<').encode(), 1); self.assertNotEqual(body, native)
            if shape is None:  # a plain code is a CODE leaf (allowed everywhere); the exact oracle still refuses it
                self.assertTrue(out.validate_native(body, case, TODAY)['privacyValuesVerified'])
                with self.assertRaises(reader.InputError):
                    reader.validate_web_xml(web.replace(tag, b'<ct6_ma>01<', 1), case_id=case)
                continue
            with self.subTest(shape=shape, layout=layout), self.assertRaises(out.OutputError) as error:
                out.validate_native(body, case, TODAY)
            status = out.safe_failure(error.exception)
            expected = {'format': 'htkk-declaration-native-output-publication-status-v1', 'status': 'rejected', 'code': 'XML_PRIVACY',
                        'nativeRule': 'PRIVACY', 'leafOrdinal': ordinal, 'section': 16, 'valueShape': shape}
            if layout:
                expected['concatLayout'] = layout
            self.assertEqual(status, expected)
            for secret in ('NHA THAU', '1503', '46096', '2026', 'PRIVATE', 'GIẢ'):
                self.assertNotIn(secret, json.dumps(status, ensure_ascii=False))
        # The allowance is keyed to the case and the leaf: another case or another leaf never accepts the key.
        other = '04NTNN-TT80-one-subcontractor-2026'; theirs = native_of(dfx.declaration_fixture(other), other)
        with self.assertRaises(out.OutputError):
            out.validate_native(theirs.replace(b'<ct9>', tag[:-1] + b'</ct6_ma><ct9>', 1), other, TODAY)
        with self.assertRaises(out.OutputError):
            out.validate_native(native.replace(b'<ct9>2000000000<', ('<ct9>' + key + '<').encode(), 1), case, TODAY)
        # Layout grammar: only fixed tokens leave the process.
        self.assertEqual(out.safe_context({'valueShape': 'allowed-text-concat', 'concatLayout': 'E.R.n8=ddMMyyyy'})['concatLayout'], 'E.R.n8=ddMMyyyy')
        for bad in ('E.R.15032026', 'E.R.n8=private', 'x' * 300, 'E', 'E.' * 40 + 'E'):
            self.assertNotIn('concatLayout', out.safe_context({'valueShape': 'allowed-text-concat', 'concatLayout': bad}))
        self.assertNotIn('concatLayout', out.safe_context({'valueShape': 'text-other', 'concatLayout': 'E.R'}))
        allowed = d.case(case)['texts']
        self.assertIsNone(d._concat_shape('HD-GL-041', allowed)); self.assertIsNone(d._concat_shape('PRIVATE CUSTOMER', allowed))
        self.assertIsNone(d._concat_shape('x' * 3000, allowed)); self.assertIsNone(d.concat_layout('x' * 3000, allowed))
        # FarPoint primitives of the oracle.
        self.assertEqual(d.mask_value('15/03/2026'), '15032026'); self.assertEqual(d.mask_value(''), '')
        self.assertEqual(d.farpoint_trim(' A  \tB \u00a0'), 'A B'); self.assertEqual(d.farpoint_trim('A\t  B'), 'A\tB')

    def test_whitespace_only_leaf_reads_empty_like_the_original_reader(self):
        """Release 222: both BCTC native exports (tree matched in the harness) were rejected as
        PRIVACY at leaf 20 (GiaHan/maLyDoGiaHan, section 2, text-other): the original writer emits an
        empty non-self-closed leaf as '<x>' CRLF indent '</x>'. XmlDocument (HTKK import, harness
        comparison) reads ''; only XML whitespace is folded, any other character still fails."""
        for case in ('BCTC133-B01a-basic-Y2025', 'BCTC200-LT-basic-Y2025'):
            # The synthetic contract has no GiaHan block: an empty filler leaf stands in for it.
            web = dfx.declaration_fixture(case).replace(b'<pad0>0</pad0>', b'<pad0></pad0>', 1); dates = d.case(case)['exportDates']
            native = export_day_of(native_of(web, case), case)
            spaced = native.replace(b'<pad0></pad0>', b'<pad0>\r\n          \t</pad0>', 1)
            self.assertNotEqual(spaced, native, case)
            self.assertTrue(out.validate_native(spaced, case, TODAY)['privacyValuesVerified'])
            result = d.compare_tree(web, spaced, dates)
            self.assertTrue(result['allTaxValuesMatched'], case); self.assertEqual(result['checkedTaxLeafCount'], d.tax_leaf_count(case))
            items = d.leaves(d._parse(spaced, False))
            self.assertEqual(next(v for p, v in items if p.endswith('/pad0')), '')
            for other in ('\u00a0', ' x ', '\u2003'):
                body = spaced.replace(b'<pad0>\r\n', ('<pad0>' + other).encode('utf-8'), 1)
                self.assertNotEqual(body, spaced)
                with self.subTest(case=case, other=other), self.assertRaises(out.OutputError) as error:
                    out.validate_native(body, case, TODAY)
                self.assertEqual(out.safe_failure(error.exception)['nativeRule'], 'PRIVACY')
                self.assertEqual(d.compare_tree(web, body, dates)['mismatchSectionMask'], 8)

    def test_bctc133_signing_date_is_the_export_day_on_both_sides_never_ignored(self):
        """A2 binds no control to TKhaiThue/ngayKy; the original export writes the day the form was
        opened (BindToKhaiInfoToTTinChung: DateTime.Now). Release 216 r1373: tree mask 2."""
        case = 'BCTC133-B01a-basic-Y2025'; dates = d.case(case)['exportDates']
        self.assertEqual(dates, ('HSoThueDTu/HSoKhaiThue/TTinChung/TTinTKhaiThue/TKhaiThue/ngayKy',))
        self.assertEqual([c for c in CASES if d.case(c)['exportDates']], [case])
        web = dfx.declaration_fixture(case); native = native_of(web, case); exported = export_day_of(native, case)
        self.assertEqual(d.compare_tree(web, exported)['mismatchSectionMask'], 2)  # exact comparison: the r1373 mask
        self.assertTrue(d.compare_tree(web, exported, dates)['allTaxValuesMatched'])
        self.assertEqual(d.compare_tree(web, exported, dates)['checkedTaxLeafCount'], d.tax_leaf_count(case))
        for other in (b'2026-11-05', b'', b'06/11/2026'):
            bad = exported.replace(b'<ngayKy>2026-11-06<', b'<ngayKy>' + other + b'<', 1); self.assertNotEqual(bad, exported)
            self.assertEqual(d.compare_tree(web, bad, dates)['mismatchSectionMask'], 2, other)
        # The web draft side must carry its own creation date too.
        self.assertEqual(d.compare_tree(web.replace(b'<ngayKy>2026-03-20<', b'<ngayKy>2026-03-21<', 1), exported, dates)['mismatchSectionMask'], 2)
        plans = (ROOT / 'HtkkDeclarationCasePlans.cs').read_text(encoding='utf-8')
        self.assertIn('plan.MenuId=="A2"?new string[]{"HSoThueDTu/HSoKhaiThue/TTinChung/TTinTKhaiThue/TKhaiThue/ngayKy"}:new string[0]', plans)
        self.assertIn('HtkkDeclarationCasePlans.ExportDatePaths(declarationPlan),out leaves,out mask', (ROOT / 'HtkkDeclarationWebImport.cs').read_text(encoding='utf-8'))
        self.assertIn("declaration.case(metadata['caseId'])['exportDates']", (ROOT / 'publish-htkk-declaration-native-output.py').read_text(encoding='utf-8'))

    def test_whole_tree_mask_reports_sections_without_values(self):
        case = '05QTT-two-employees-Y2025'; web = dfx.declaration_fixture(case); native = native_of(web, case)
        self.assertEqual(d.compare_tree(web, native.replace(b'<tenNNT>NNT', b'<tenNNT>XNT', 1))['mismatchSectionMask'], 4)
        self.assertEqual(d.compare_tree(web, native.replace(b'<ct16>2</ct16>', b'<ct16>3</ct16>', 1))['mismatchSectionMask'], 8)
        self.assertEqual(d.compare_tree(web, native.replace(b'<ct08>0</ct08>', b'<ct08>1</ct08>', 1))['mismatchSectionMask'], 16)
        self.assertEqual(d.compare_tree(web, native.replace(b'<pad0>0</pad0>', b'', 1))['mismatchSectionMask'], 32 | 8)
        many = native
        for n in range(12):
            many = many.replace(('<pad%d>0<' % n).encode(), ('<pad%d>1<' % n).encode(), 1)
        result = d.compare_tree(web, many)
        self.assertEqual(len(result['mismatchLeafOrdinals']), d.MISMATCH_ORDINALS); self.assertEqual(result['mismatchLeafOrdinals'], sorted(result['mismatchLeafOrdinals']))
        self.assertEqual(d.compare_tree(web, native)['mismatchLeafOrdinals'], [])
        changed = native.replace(b'<ngayLapTKhai>2026-11-06', b'<ngayLapTKhai>2026-11-07', 1)
        self.assertTrue(d.compare_tree(web, changed)['allTaxValuesMatched'])  # creation date: proven native rule only

    def test_byte_exact_retention_with_comparison_even_when_mismatched(self):
        for case in CASES:
            web = dfx.declaration_fixture(case); manifest = dfx.declaration_manifest(web, case, source=SOURCE)
            # The original's export-day leaves carry the export day (A2 ngayKy), as on Windows.
            for native, matched, mask in ((export_day_of(native_of(web, case), case), True, 0), (native_of(web, case).replace(b'<tenNNT>NNT', b'<tenNNT>XNT', 1), False, 4)):
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
            native = export_day_of(native_of(web, case), case)
            first = next(p for p, v in d.leaves(d._parse(native, False)) if v == '0' and '/pad' in p).rsplit('/', 1)[1]
            native = native.replace(('<' + first + '>0<').encode(), ('<' + first + '>7<').encode(), 1)
            fetch, calls = self.fake_api(web, manifest)
            result = out.publish(native, self.provenance(web, native, case, False, 8), 'synthetic-token', fetch, TODAY)
            self.assertFalse(result['allTaxValuesMatched']); self.assertEqual(result['mismatchSectionMask'], 8)
            # Value-free locator of the changed leaf (release 222: BCTC200 mask 8 had no position).
            ordinal = next(i + 1 for i, (p, _) in enumerate(d.leaves(d._parse(native, False))) if p.endswith('/' + first))
            self.assertEqual(result['mismatchLeafOrdinals'], [ordinal])
            self.assertEqual(d.compare_tree(web, native, d.case(case)['exportDates'])['mismatchLeafOrdinals'], [ordinal])

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
        # B9: the original import adds every sheet (cmdImportXML_Click → AddFullPLImportXML, run 42231692177).
        self.assertIn('if(HtkkDeclarationCasePlans.ImportAddsAllAnnexes(plan))all=true;', hidden)
        self.assertIn('"~B8~37~33~B9~N7~W1~".IndexOf("~"+plan.MenuId+"~",StringComparison.Ordinal)>=0', plans)
        self.assertIn('1+(HtkkDeclarationCasePlans.ImportAddsAllAnnexes(declarationPlan)?0:declarationPlan.Annexes.Length)', driver)
        # A modal original refusal of the period confirmation is reported by catalogue ID only.
        block = driver[driver.index('Form periodMessage;'):driver.index('if(forms.Count!=1){SetStage(HtkkAutomationStage.DeclarationSheetWaiting)')]
        self.assertIn('declarationPeriodRejectedMessageId=OriginalMessageCatalogueId(periodText)', block)
        self.assertNotIn('PerformClick', block)

    def test_root_exit_diagnostic_is_bounded_exit_code_and_category(self):
        # Run 42218283778: the root exited during the original import with no message.
        probe = (ROOT / 'probe-htkk-windows.ps1').read_text(encoding='utf-8')
        fn = probe[probe.index('function Get-HtkkRootExitDiagnostic($Job) {'):probe.index('function Get-HtkkSafeReferenceResult(')]
        for code, category in ((3762507597, 'clr-unhandled-exception'), (3221225725, 'stack-overflow'), (3221225477, 'access-violation'), (3221226505, 'fail-fast')):
            self.assertIn(str(code), fn); self.assertIn("'" + category + "'", fn)
        self.assertIn("('0x{0:x8}' -f $code)", fn)
        for forbidden in ('Message', 'StackTrace', 'Get-WinEvent', 'Get-EventLog', 'Path', 'Write-Host'):
            self.assertNotIn(forbidden, fn)
        loop = probe[probe.index('$automationClock=[Diagnostics.Stopwatch]::StartNew()'):probe.index("if($null -eq $lastGui){$report.guiReferenceAutomation=")]
        self.assertIn('if($automationRootExited){$report.referenceHostExit=Get-HtkkRootExitDiagnostic -Job $supplierJob}', loop)
        self.assertIn('referenceHostExit = $null', probe)

    def test_probe_success_staging_and_workflow_wiring(self):
        probe = (ROOT / 'probe-htkk-windows.ps1').read_text(encoding='utf-8')
        workflow = (ROOT.parent / '.github/workflows/probe-htkk-windows.yml').read_text(encoding='utf-8')
        for flag in ('declarationTreeMatched', 'declarationSchemaValid', 'declarationXmlMismatchMask -eq 0', 'declarationCellMismatchMask -eq 0', 'declarationAnnexMatched', 'declarationIdentityMatched', 'roundtripImportSucceeded', 'exportSuccessAcknowledged', 'importRejectedMessageId -eq 0', 'exportRejectedMessageId -eq 0'):
            self.assertIn(flag, probe)
        self.assertIn("Join-Path $stage $(if($declarationInput){'declaration-web.xml'}else{'01GTGT-web.xml'})", probe)
        self.assertIn("'DataFiles/9999999997/reference-declaration-output/declaration.xml'", probe)
        self.assertIn("format='htkk-declaration-native-output-staging-v1'", probe)
        self.assertIn("$HtkkDeclarationCases=@(" + ",".join("'" + c + "'" for c in CASES) + ")", (ROOT / 'HtkkNativeCaseFormats.ps1').read_text())
        self.assertIn("inputs.gui_automation == 'gtgt-web-import-inspect' || inputs.gui_automation == 'gtgt-amendment-khbs-inspect' || inputs.gui_automation == 'declaration-web-import-inspect'", workflow)
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


class OccurrencePeriod(unittest.TestCase):
    """Kỳ lần phát sinh (KieuKy 18, chkTKLanPS): period kind 'day' of I9/Y8/J1 (GetPeriodInfo KieuKy D)."""
    DAY_CASES = ('01NTNN-occurrence-D20-09-2026', '01NTNN-NCCNN-occurrence-D20-10-2026', '03NTNN-occurrence-D20-10-2026')
    # I9 moved to 20/09/2026: HTKK 5.8.2 refuses an I9 day period after its Menu.xml EndDate 30/09/2026.
    DAYS = {'01NTNN-occurrence-D20-09-2026': '20/09/2026', '01NTNN-NCCNN-occurrence-D20-10-2026': '20/10/2026', '03NTNN-occurrence-D20-10-2026': '20/10/2026'}

    def test_day_cases_are_non_gating_kieuky_18_plans_with_one_day(self):
        for case in self.DAY_CASES:
            unit = registry.CASES[case]['unit']; day = self.DAYS[case]
            self.assertEqual((unit['periodType'], unit['periodValue']), ('day', day))
            self.assertIs(registry.CASES[case]['releaseGate'], False)
            self.assertIn('"day","18","2026","","%s","%s",false' % (day, day), plan_block(case))
            spec = d.case(case)
            self.assertEqual((spec['kieuKy'], spec['kyKKhai'], spec['tuNgay'], spec['denNgay']), ('D', day, day, day))
        # The plan refuses a day period that is not KieuKy 18 or whose from/to differ.
        constructor = PLANS[PLANS.index('internal HtkkDeclarationCasePlan('):PLANS.index('internal sealed class HtkkDeclarationEntryPlan')]
        self.assertIn('periodKind=="day"&&(kieuKy!="18"||fromDate.Length!=10||fromDate!=toDate', constructor)

    def test_driver_types_only_the_visible_day_month_year_boxes_and_checks_kieuky_d(self):
        configure = DRIVER[DRIVER.index('private void ConfigureDeclarationPeriod('):DRIVER.index('// ---- Original declaration sheet')]
        self.assertIn('else if(plan.PeriodKind=="day"){SetCheck(Named(period,"chkTKLanPS"),true);}', configure)
        self.assertIn('if(plan.PeriodKind=="day"){SetDeclarationText(period,"mskMonth",plan.FromDate.Substring(3,2));SetDeclarationText(period,"mskDay",plan.FromDate.Substring(0,2));}', configure)
        # mskTuNgay/mskDenNgay are typed only for KieuKy 11/26/22, never for a day period; they must stay hidden.
        self.assertIn('if(plan.KieuKy=="11"||plan.KieuKy=="26"||plan.KieuKy=="22"){SetDeclarationText(period,"mskTuNgay"', configure)
        self.assertIn('!VisibleNamed(period,"mskTuNgay")&&!VisibleNamed(period,"mskDenNgay")', configure)
        identity = DRIVER[DRIVER.index('private bool DeclarationIdentity('):DRIVER.index('private void InspectDeclarationSheetCore(')]
        self.assertIn('plan.PeriodKind=="day"?"D"', identity)
        for name in ('"TuNgay"', '"DenNgay"', '"kyKKhai"', '"Ngay"', '"Thang"'):
            self.assertIn(name, identity)

    def test_web_inputs_carry_kieuky_d_and_the_day_and_fail_closed_on_any_other_period(self):
        for case in self.DAY_CASES:
            body = dfx.declaration_fixture(case); day = self.DAYS[case].encode(); month = day[3:]
            reader.validate_web_xml(body, case_id=case)
            iso = day[6:] + b'-' + day[3:5] + b'-' + day[:2]
            date = b'<ct7>' + iso + b'</ct7>' if case.startswith('03') else b'<ct6>' + iso + b'</ct6>'
            self.assertIn(date, body)
            for name, (old, new) in {'kieuKy': (b'<kieuKy>D</kieuKy>', b'<kieuKy>M</kieuKy>'), 'kyKKhai': (b'<kyKKhai>' + day + b'</kyKKhai>', b'<kyKKhai>' + month + b'</kyKKhai>'),
                                     'den': (b'<kyKKhaiDenNgay>' + day + b'</kyKKhaiDenNgay>', b'<kyKKhaiDenNgay>21/' + month + b'</kyKKhaiDenNgay>'), 'payment': (date, date.replace(b'20<', b'21<'))}.items():
                self.assertIn(old, body, (case, name))
                with self.subTest(case=case, name=name), self.assertRaises(reader.InputError):
                    reader.validate_web_xml(body.replace(old, new, 1), case_id=case)
