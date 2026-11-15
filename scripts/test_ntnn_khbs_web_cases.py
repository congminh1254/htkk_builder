"""Input contract of the 01/NTNN, 01/NTNN-NCCNN kê khai bổ sung cases (htkk_ntnn_khbs_web_cases.py). Synthetic checks only;
the reviewed producer files themselves stay private (the contract pins their sizes and SHA-256). Byte-level checks run on a
second module instance pinned to synthetic in-memory files (ntnn_khbs_test_support.py); the first keeps the real pins."""
import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).parent
spec = importlib.util.spec_from_file_location('htkk_ntnn_khbs_web_cases', ROOT / 'htkk_ntnn_khbs_web_cases.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
support_spec = importlib.util.spec_from_file_location('ntnn_khbs_test_support', ROOT / 'ntnn_khbs_test_support.py')
support = importlib.util.module_from_spec(support_spec)
support_spec.loader.exec_module(support)
pinned_spec = importlib.util.spec_from_file_location('htkk_ntnn_khbs_web_cases_pinned', ROOT / 'htkk_ntnn_khbs_web_cases.py')
sm = importlib.util.module_from_spec(pinned_spec)
pinned_spec.loader.exec_module(sm)
support.pin(sm)


def manifest(case_id, module=m):
    c = module.CASES[case_id]
    value = dict(module.manifest_fields(case_id), sourceCommit='0' * 40, producerSha256='1' * 64, bytes=c['web'][0], xmlSha256=c['web'][1],
                 originalBytes=c['original'][0], originalXmlSha256=c['original'][1])
    if c['prior']:
        value.update(priorBytes=c['prior'][0], priorXmlSha256=c['prior'][1])
    return value


class NtnnKhbsWebCases(unittest.TestCase):
    def test_five_cases_with_exact_staged_names(self):
        # The 05/KK-TNCN cases are merged from htkk_kk05_khbs_web_cases.py (test_kk05_khbs_web_cases.py).
        self.assertEqual(sorted(m.CASES), sorted(m.NTNN_CASES + m.KK05_CASES + m.CNKD_CASES))
        self.assertEqual(sorted(m.NTNN_CASES), sorted(['01NTNN-khbs-grossup-lan1-M09-2026', '01NTNN-khbs-lan2-M09-2026', '01NTNN-khbs-decrease-M09-2026',
                                                  '01NTNN-NCCNN-khbs-part1-M10-2026', '01NTNN-NCCNN-khbs-part2-M10-2026']))
        for case_id, c in m.CASES.items():
            self.assertEqual(m.names(case_id)[-2:], (m.WEB_NAME, m.MANIFEST_NAME))
            self.assertEqual(m.names(case_id)[0], m.ORIGINAL_NAME)
            self.assertEqual(m.PRIOR_NAME in m.names(case_id), c['soLan'] == 2)
            self.assertEqual(bool(c['prior']), c['soLan'] == 2)
            self.assertIn(c['menuId'], m.MENUS)
            self.assertTrue(0 < c['leafTarget'] <= 4096)
            for role in ('web', 'original') + (('prior',) if c['prior'] else ()):
                size, digest = c[role]
                self.assertTrue(0 < size <= m.MAX_XML)
                self.assertRegex(digest, '^[0-9a-f]{64}$')
            self.assertRegex(m.manifest_fields(case_id)['format'], '^htkk-web-[a-z0-9-]+-input-v1$')
        # The lần-2 previous version is the lần-1 case's own file, and every I9 case starts from the same lần đầu.
        lan1, lan2 = m.CASES['01NTNN-khbs-grossup-lan1-M09-2026'], m.CASES['01NTNN-khbs-lan2-M09-2026']
        self.assertEqual(lan2['prior'], lan1['web'])
        self.assertEqual(len({c['original'] for c in m.CASES.values() if c['menuId'] == 'I9'}), 1)

    def test_registered_as_non_gating_582_cases_of_the_khbs_declaration_mode(self):
        registry = json.loads((ROOT / 'htkk-native-cases.json').read_text(encoding='utf-8'))
        rows = {c['caseId']: c for c in registry['cases'] if c['caseId'] in m.CASES}
        adapters = {a['adapterId']: a for a in registry['adapters']}
        self.assertEqual(set(rows), set(m.CASES))
        for case_id, row in rows.items():
            self.assertIs(row['releaseGate'], False)
            self.assertEqual(row['htkkVersion'], '5.8.2')
            self.assertEqual(row['format'], m.manifest_fields(case_id)['format'])
            self.assertEqual(row['unit']['amendmentOrder'], m.CASES[case_id]['soLan'])
            self.assertEqual(adapters[row['adapterId']]['driver'], 'declaration-amendment-khbs-inspect')
            self.assertEqual(adapters[row['adapterId']]['producer'], m.producer(case_id))

    def test_pinned_files_validate_and_one_changed_byte_does_not(self):
        for case_id in sm.CASES:
            files = support.files(sm, case_id)
            self.assertEqual(sm.validate_files(files, manifest(case_id, sm))['amendmentLeafTarget'], sm.CASES[case_id]['leafTarget'])
            body = files[sm.WEB_NAME]
            changed = body.replace(b'<maDVu>CCKK</maDVu>', b'<maDVu>CCKX</maDVu>')
            self.assertNotEqual(changed, body)
            with self.assertRaises(sm.NtnnKhbsWebCaseError) as error:
                sm.validate_xml(changed, case_id, 'web')
            self.assertEqual(error.exception.code, 'HASH')
            # A file of the wrong role (lần đầu staged as the bổ sung) is refused by its pin.
            with self.assertRaises(sm.NtnnKhbsWebCaseError):
                sm.validate_xml(files[sm.ORIGINAL_NAME], case_id, 'web')
        # The real pins refuse every synthetic file.
        with self.assertRaises(m.NtnnKhbsWebCaseError):
            m.validate_xml(support.files(sm, '01NTNN-khbs-decrease-M09-2026')[m.WEB_NAME], '01NTNN-khbs-decrease-M09-2026', 'web')

    def test_manifest_is_exact(self):
        for case_id in m.CASES:
            self.assertIs(m.validate_manifest(manifest(case_id))['caseId'], case_id)
            for change in ({'extra': 1}, {'soLan': 9}, {'xmlSha256': '2' * 64}, {'htkkVersion': '5.8.1'}, {'sourceCommit': 'x'}):
                with self.assertRaises(m.NtnnKhbsWebCaseError):
                    m.validate_manifest(dict(manifest(case_id), **change))
        with self.assertRaises(m.NtnnKhbsWebCaseError) as error:
            m.validate_manifest(dict(manifest('01NTNN-khbs-lan2-M09-2026'), caseId='01NTNN-other'))
        self.assertEqual(error.exception.code, 'CASE')

    def test_files_are_the_pinned_bytes_only(self):
        case_id = '01NTNN-khbs-decrease-M09-2026'
        size = m.CASES[case_id]['web'][0]
        fake = (m.PREAMBLE + 'xmlns="%s"/>' % m.NS).encode('utf-8')
        for body, code in ((b'', 'SIZE'), (fake, 'SIZE'), (fake.ljust(size, b' '), 'HASH')):
            with self.assertRaises(m.NtnnKhbsWebCaseError) as error:
                m.validate_xml(body, case_id, 'web')
            self.assertEqual(error.exception.code, code)
        with self.assertRaises(m.NtnnKhbsWebCaseError) as error:
            m.validate_xml(fake, case_id, 'prior')
        self.assertEqual(error.exception.code, 'NAMES')
        with self.assertRaises(m.NtnnKhbsWebCaseError) as error:
            m.validate_files({m.WEB_NAME: fake}, manifest(case_id))
        self.assertEqual(error.exception.code, 'NAMES')

    def test_bounded_codes(self):
        with self.assertRaises(ValueError):
            m.NtnnKhbsWebCaseError('free text')




def native_of(case_id, created='2026-11-15'):
    """In-memory native-shaped copy of the synthetic web B file: original service identity and current creation date."""
    d = sm.declaration(); text = support.files(sm, case_id)[sm.WEB_NAME].decode('utf-8')
    for web, native in zip(sm.SERVICE, (*d.native_service('5.8.2'), 'A' * 32)):
        text = text.replace('>' + web + '<', '>' + native + '<', 1)
    return text.replace('<ngayLapTKhai>' + sm.FIXED_DATE + '<', '<ngayLapTKhai>' + created + '<', 1).encode('utf-8')


class NtnnKhbsNativeOutput(unittest.TestCase):
    TODAY = __import__('datetime').date(2026, 11, 15)

    def test_native_shaped_copy_validates_and_matches_the_whole_tree(self):
        for case_id in sm.CASES:
            with self.subTest(case=case_id):
                native = native_of(case_id); files = support.files(sm, case_id)
                self.assertIs(sm.validate_native_output(native, case_id, self.TODAY, '5.8.2')['privacyValuesVerified'], False)
                self.assertIs(sm.validate_native_output(native, case_id, self.TODAY, '5.8.2', files)['privacyValuesVerified'], True)
                comparison = sm.compare_tree(files[sm.WEB_NAME], native, case_id)
                self.assertTrue(comparison['allTaxValuesMatched'])
                self.assertEqual(comparison['checkedTaxLeafCount'], sm.tax_leaf_count(case_id))
                # Staged files are checked against their pins; a missing or extra file is refused.
                with self.assertRaises(sm.NtnnKhbsWebCaseError):
                    sm.validate_native_output(native, case_id, self.TODAY, '5.8.2', {sm.WEB_NAME: files[sm.WEB_NAME]})
                with self.assertRaises(sm.NtnnKhbsWebCaseError):
                    sm.compare_tree(native, native, case_id)

    def test_native_rules_fail_closed(self):
        d = sm.declaration(); case_id = '01NTNN-khbs-lan2-M09-2026'; native = native_of(case_id).decode('utf-8'); files = support.files(sm, case_id)
        bad = {'IDENTITY': native.replace('<soLan>2<', '<soLan>1<', 1), 'SERVICE': native.replace('>HTKK<', '>CCKK<', 1),
               'DATE': native.replace('<ngayLapTKhai>2026-11-15<', '<ngayLapTKhai>2026-11-01<', 1),
               'PERIOD': native.replace('<kyKKhai>09/2026<', '<kyKKhai>08/2026<', 1),
               'PRIVACY': native.replace('>' + sm.NAME + '<', '>NGUOI THAT<', 1)}
        for code, text in bad.items():
            self.assertNotEqual(text, native)
            with self.subTest(code=code), self.assertRaises(d.DeclarationWebCaseError) as caught:
                sm.validate_native_output(text.encode('utf-8'), case_id, self.TODAY, '5.8.2', files)
            self.assertEqual(caught.exception.code, code)
        # A text that is in no staged file of the case is refused with a value-free diagnostic only.
        self.assertIn('<ct3>HD-GL-101<', native)
        foreign = native.replace('<ct3>HD-GL-101<', '<ct3>HD-THAT-202<', 1).encode('utf-8')
        self.assertIs(sm.validate_native_output(foreign, case_id, self.TODAY, '5.8.2')['privacyValuesVerified'], False)
        with self.assertRaises(d.DeclarationWebCaseError) as caught:
            sm.validate_native_output(foreign, case_id, self.TODAY, '5.8.2', files)
        self.assertEqual(caught.exception.code, 'PRIVACY')
        self.assertEqual(set(caught.exception.context) - {'concatLayout'}, {'leafOrdinal', 'section', 'valueShape'})

    def test_comparison_reports_a_changed_amount(self):
        case_id = '01NTNN-khbs-grossup-lan1-M09-2026'; native = native_of(case_id).decode('utf-8')
        target = sm.CASES[case_id]['expected']['ct10']
        self.assertIn('<ct10>' + target + '<', native)
        changed = sm.compare_tree(support.files(sm, case_id)[sm.WEB_NAME], native.replace('<ct10>' + target + '<', '<ct10>' + target[:-1] + '9<', 1).encode('utf-8'), case_id)
        self.assertFalse(changed['allTaxValuesMatched'])
        self.assertEqual(changed['mismatchSectionMask'], 8)


class NtnnKhbsNativePublisher(unittest.TestCase):
    """publish-htkk-declaration-native-output.py retains the original B export of the KHBS observation cases."""
    SOURCE, ARTIFACT, BUILDER = 'a' * 40, 'b' * 40, 'c' * 40

    @classmethod
    def setUpClass(cls):
        out_spec = importlib.util.spec_from_file_location('ntnn_khbs_declaration_output', ROOT / 'publish-htkk-declaration-native-output.py')
        cls.out = importlib.util.module_from_spec(out_spec); out_spec.loader.exec_module(cls.out)
        support.pin(cls.out.ntnn)

    def provenance(self, case_id, native, matched=True):
        mode = sm.input_mode(case_id)
        return {'format': 'htkk-declaration-native-output-staging-v1', 'builderRepository': self.out.BUILDER, 'builderCommit': self.BUILDER, 'runId': '123', 'runAttempt': 1,
                'sourceRepository': self.out.REPO, 'sourceCommit': self.SOURCE, 'sourceVersion': '5.8.2', 'runtimeHost': 'clr2-x86-reference', 'caseId': case_id, 'artifactCommit': self.ARTIFACT,
                'inputsSynthetic': True, 'originalProcessStopped': True, 'originalSourcesUnmodified': True,
                'inputMode': mode, 'originalImportSucceeded': mode != 'khbs-original-entry-export', 'originalExportSucceeded': True, 'originalExporterValidatedSchema': True,
                'webImportInputSha256': sm.CASES[case_id]['web'][1], 'originalOutputSha256': __import__('hashlib').sha256(native).hexdigest(), 'originalOutputBytes': len(native),
                'harnessSchemaValid': True, 'harnessTreeMatched': matched, 'harnessTreeMismatchMask': 0 if matched else 8, 'harnessTreeLeafCount': sm.tax_leaf_count(case_id), 'harnessXmlMismatchMask': 0, 'harnessCellMismatchMask': 0,
                'creationDateRule': 'native-export-current-date', 'fullRoundTrip': False}

    def fake_api(self, case_id):
        import base64, hashlib, urllib.error
        files = support.files(sm, case_id)
        files['manifest.json'] = json.dumps(dict(manifest(case_id, sm), sourceCommit=self.SOURCE), ensure_ascii=False).encode('utf-8')
        calls = []
        def envelope(body, name):
            return {'type': 'file', 'name': name, 'path': name, 'encoding': 'base64', 'size': len(body), 'content': base64.encodebytes(body).decode(), 'sha': hashlib.sha1(b'blob ' + str(len(body)).encode() + b'\0' + body).hexdigest()}
        def fetch(path, token, payload=None, method=None):
            calls.append((path, payload))
            if path == '':return {'private': True, 'full_name': self.out.REPO}
            if path in ('/git/commits/' + self.SOURCE, '/git/commits/' + self.ARTIFACT):return {'sha': path.rsplit('/', 1)[1]}
            for name, body in files.items():
                if path == '/contents/' + name + '?ref=' + self.ARTIFACT:return envelope(body, name)
            if path == '/git/blobs':
                body = base64.b64decode(payload['content']); return {'sha': hashlib.sha1(b'blob ' + str(len(body)).encode() + b'\0' + body).hexdigest()}
            if path == '/git/trees':return {'sha': 'd' * 40}
            if path == '/git/commits':return {'sha': 'e' * 40}
            if path.startswith('/git/ref/heads/'):raise urllib.error.HTTPError('https://api.github.com/', 404, 'SECRET', {}, None)
            if path == '/git/refs':return {'ref': payload['ref'], 'object': {'type': 'commit', 'sha': payload['sha']}}
            raise AssertionError('Unexpected fixed API path')
        return fetch, calls

    def test_registered_branches_and_exact_provenance(self):
        self.assertTrue(set(sm.CASES) <= set(self.out.BRANCHES))
        for case_id in sm.CASES:
            native = native_of(case_id); value = self.provenance(case_id, native)
            self.out.validate_provenance(json.dumps(value).encode(), native, '123', self.BUILDER, self.SOURCE, case_id, self.ARTIFACT, '1', '5.8.2')
            for key, bad in (('inputMode', 'web-xml-import-reexport'), ('originalImportSucceeded', not value['originalImportSucceeded']), ('webImportInputSha256', 'f' * 64)):
                with self.subTest(case=case_id, key=key), self.assertRaises(self.out.OutputError):
                    changed = dict(value); changed[key] = bad
                    self.out.validate_provenance(json.dumps(changed).encode(), native, '123', self.BUILDER, self.SOURCE, case_id, self.ARTIFACT, '1', '5.8.2')

    def test_raw_export_retained_with_the_recomputed_comparison_even_when_it_differs(self):
        case_id = '01NTNN-khbs-lan2-M09-2026'; target = sm.CASES[case_id]['expected']['ct10']
        for native, matched in ((native_of(case_id), True), (native_of(case_id).replace(('<ct10>' + target + '<').encode(), ('<ct10>' + target[:-1] + '7<').encode(), 1), False)):
            with self.subTest(matched=matched):
                fetch, calls = self.fake_api(case_id)
                result = self.out.publish(native, self.provenance(case_id, native, matched), 'token', fetch, today=NtnnKhbsNativeOutput.TODAY, version='5.8.2')
                self.assertEqual((result['status'], result['allTaxValuesMatched']), ('published', matched))
                blobs = [__import__('base64').b64decode(p['content']) for path, p in calls if path == '/git/blobs']
                self.assertEqual(blobs[0], native)
                retained = json.loads(blobs[1])
                self.assertTrue(retained['comparison']['harnessAgreement'])
                self.assertIs(retained['privacyCheck']['privacyValuesVerified'], True)
                self.assertEqual(retained['comparison']['expectedTaxLeafCount'], sm.tax_leaf_count(case_id))
                self.assertIn(('/git/refs', {'ref': 'refs/heads/' + self.out.oracle.output_branch(self.out.BRANCHES[case_id], '5.8.2'), 'sha': 'e' * 40}), calls)

    def test_private_text_is_never_retained(self):
        case_id = '01NTNN-khbs-grossup-lan1-M09-2026'
        for old, new in (('>' + sm.NAME + '<', '>NGUOI THAT<'), ('<ct3>HD-GL-101<', '<ct3>HD-THAT-202<')):
            native = native_of(case_id).replace(old.encode(), new.encode(), 1)
            fetch, calls = self.fake_api(case_id)
            with self.subTest(new=new), self.assertRaises(self.out.OutputError) as error:
                self.out.publish(native, self.provenance(case_id, native), 'token', fetch, today=NtnnKhbsNativeOutput.TODAY, version='5.8.2')
            self.assertEqual(error.exception.code, 'XML_PRIVACY')
            self.assertNotIn('THAT', json.dumps(self.out.safe_failure(error.exception)))
            self.assertFalse(any(path == '/git/blobs' for path, _ in calls))


class NtnnKhbsProbeWiring(unittest.TestCase):
    def test_probe_stages_sidecars_requires_every_step_and_retains_the_raw_export(self):
        probe = (ROOT / 'probe-htkk-windows.ps1').read_text(encoding='utf-8')
        workflow = (ROOT.parent / '.github/workflows/probe-htkk-windows.yml').read_text(encoding='utf-8')
        host = (ROOT / 'New-HtkkX86ReferenceHost.ps1').read_text(encoding='utf-8')
        self.assertIn("if(($GuiAutomation -eq 'declaration-amendment-khbs-inspect') -ne ($env:EXPECTED_WEB_CASE_ID -cin $HtkkNtnnKhbsCases)){throw 'WEB_REFERENCE_INPUT_INVALID'}", probe)
        self.assertIn("if(($GuiAutomation -eq 'declaration-web-import-inspect') -ne ($env:EXPECTED_WEB_CASE_ID -cin $HtkkDeclarationCases)){throw 'WEB_REFERENCE_INPUT_INVALID'}", probe)
        for name, sidecar, key in ((m.ORIGINAL_NAME, '.web-original', 'originalXmlSha256'), (m.PRIOR_NAME, '.web-prior', 'priorXmlSha256')):
            self.assertIn("name='" + name + "';path=($hostFull+'" + sidecar + ".xml');hashPath=($hostFull+'" + sidecar + ".sha256');sha='" + key + "'", probe)
        self.assertIn('$referenceOwnedFiles+=@($staged.path,$staged.hashPath)', probe)
        self.assertIn("$matched=$matched -and $lastGui.stage -eq 'declaration-khbs-inspected'", probe)
        self.assertIn('($lastGui.declarationKhbsStepMask -band $khbsSteps) -eq $khbsSteps', probe)
        self.assertIn("$khbsSteps=if($khbsLan2){1791}else{1591}", probe)
        self.assertIn("$GuiAutomation -eq 'declaration-amendment-khbs-inspect' -and $null -ne $report.guiReferenceAutomation -and $report.guiReferenceAutomation.stage -cin @('declaration-khbs-inspected','declaration-export-not-matched')", probe)
        self.assertIn("'declaration-khbs-step-rejected','declaration-khbs-timeout'", probe)
        self.assertIn("(inputs.gui_automation == 'declaration-web-import-inspect' || inputs.gui_automation == 'declaration-amendment-khbs-inspect') && inputs.web_artifact_commit != ''", workflow)
        self.assertIn("'declaration-web-import-inspect','declaration-amendment-khbs-inspect')){", host)

    def test_lan2_menu_clicks_and_bo_sung_entry_rounds(self):
        # Cohort 1019e5f: the lần-2 runs (43686713666, and 05/KK 43686730343) had every result refused once round 2 clicked the
        # menu a fourth time (menuClickCount maximum 3); the Y8 runs (43686717364, 43686719047) failed at entry 0 of round 1
        # (code 12) because the B sheet already held the C0 text.
        registry = json.loads((ROOT / 'htkk-native-automation-registry.json').read_text(encoding='utf-8'))
        self.assertEqual(registry['resultFields']['menuClickCount']['modeMaximums']['declaration-amendment-khbs-inspect'], 9)
        reader = (ROOT / 'Get-HtkkSafeGuiReferenceResult.ps1').read_text(encoding='utf-8')
        self.assertIn("$(if($ExpectedMode -ceq 'declaration-amendment-khbs-inspect'){9}", reader)
        entry = (ROOT / 'HtkkDeclarationOriginalEntry.cs').read_text(encoding='utf-8')
        khbs = (ROOT / 'HtkkDeclarationKhbs.cs').read_text(encoding='utf-8')
        self.assertIn('if(DeclarationKhbsEntryHeld(sheet,cell,kind,parts,row,column)){declarationEntryActionCount++;Record();return;}\n  DeclarationEntrySelect(grid,sheet,row,column);', entry)
        held = khbs[khbs.index('private bool DeclarationKhbsEntryHeld('):]
        held = held[:held.index('\n }\n')]
        self.assertIn('if(!DeclarationKhbsMode()||declarationKhbsRound==0)return false;', held)
        for forbidden in ('PerformClick', 'SendKeys', 'Value=', '.Text='):
            self.assertNotIn(forbidden, held)
        self.assertIn('declarationEntryActionCount=0;declarationEntryComboCount=0;', khbs)
        # Cohort c22c37f (runs 43698793633, 43698796274): the Y8 round-1 text entry still failed (code 12); the next run reports
        # the value-free shape of that cell and editor once (lengths and booleans only, never the text).
        self.assertIn('ObserveDeclarationKhbsEntry(khbsBefore,khbsOpened,editor,value);declarationEntryMismatchMask|=1<<index;DeclarationEntryFail(12);', entry)
        observe = khbs[khbs.index('private void ObserveDeclarationKhbsEntry('):]
        observe = observe[:observe.index('\n }\n')]
        for forbidden in ('PerformClick', 'SendKeys', 'Record()', '.Text='):
            self.assertNotIn(forbidden, observe)
        self.assertEqual(registry['resultFields']['declarationKhbsEntryShape']['maximum'], 4095)
        self.assertEqual(registry['resultFields']['declarationKhbsEntryLengths']['maximum'], 65535)

    def test_profile_save_wait_is_observed_and_stale_results_are_counted(self):
        # Cohort 1a6f600: the KHBS runs stopped at original-save-invoking / waiting-profile-close-ready with no later valid result.
        automation = (ROOT / 'HtkkGuiReferenceAutomation.cs').read_text(encoding='utf-8')
        khbs = (ROOT / 'HtkkDeclarationKhbs.cs').read_text(encoding='utf-8')
        probe = (ROOT / 'probe-htkk-windows.ps1').read_text(encoding='utf-8')
        self.assertIn('  if(successAcknowledged||!saveInvoked)return;\n  ObserveDeclarationKhbsProfileSave();\n  ReadSavedHeader();', automation)
        body = khbs[khbs.index('private void ObserveDeclarationKhbsProfileSave(){'):]
        body = body[:body.index('\n }\n')]
        self.assertIn('if(!DeclarationKhbsMode())return;', body)
        self.assertNotIn('PerformClick', body)
        self.assertIn('$report.guiReferenceResultReads=[ordered]@{invalidAfterValid=[int]$guiInvalidAfterValid;missingAfterValid=[int]$guiMissingAfterValid;lastWriteAgeSeconds=$guiResultAge}', probe)


if __name__ == '__main__':
    unittest.main()
