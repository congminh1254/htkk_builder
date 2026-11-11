"""Offline contracts for the per-version HTKK oracle baselines (5.8.1 default, 5.8.2 selectable).

These tests never read vendor bytes. They pin the reviewed values, keep the generated
PowerShell/C# views in sync, and keep a 5.8.2 run apart from the default release cohort.
"""
import copy, importlib.util, json, os, pathlib, re, shutil, subprocess, tempfile, unittest

ROOT = pathlib.Path(__file__).resolve().parent


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / file); value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value); return value


generator = load('oracle_baseline_generator_test', 'generate-htkk-oracle-baselines.py')
oracle = load('oracle_selection_test', 'htkk_oracle.py')
DATA = json.loads((ROOT / 'htkk-oracle-baselines.json').read_text(encoding='utf-8'))
V1, V2 = DATA['versions']['5.8.1'], DATA['versions']['5.8.2']

# The exact 5.8.1 Y8 original-entry pins the driver was reviewed against (formerly inline in the plan).
REVIEWED_ENTRY = [
    'B|Ntnn01TT89Nckt309|AutoBindData_0|0x060018f9|352|86baaca777e636dd3d76918c3b779dbcdd557467f8704bba44d89838d52068c9',
    'B|Ntnn01TT89Nckt309|getCols|0x060018fb|70|4e1e803244481d03026f9ae6853bf8aab84e408231ad846733979dda6052969b',
    'B|Ntnn01TT89Nckt309|ButtonClick_0|0x060018fc|334|ffaa6fc9bbc450ef7f0477d89c0ddcff40d891c26e086249f32ae38f4b6dbf66',
    'B|Ntnn01TT89Nckt309|LockUnlock|0x060018fd|90|8d2a68d81882fda119adc9255b8f1b761d5f76764ec5283ea8db3391fa895dec',
    'B|Ntnn01TT89Nckt309|CellChange_0|0x060018ff|28|9f9a3e4f1b799483a1cc7ebba4429ca156e0d68538cf893b1a60b822934df6ac',
    'B|GeneralFunctions|LockUnLockColsInTable|0x06002676|451|782360e75e1659cd4fe4ae171daa6f431362c7623f5b03fa68afd206761aaab7',
    'H|frmWinToKhai|winFpSpread_ButtonClicked|0x060003b8|178|72d1aea7781d9d8352c8cee92819beda5ae5153d8672cb1963c32571db6289cb',
    'H|WinDoWorkEvent|ButtonClick|0x06000062|783|043ef431c6449bf1bcd8d0b469b7daf171fb523ce1437d33c47637064d72eca6',
    'H|frmWinToKhai|winFpSpread_CellChange|0x060003b2|24666|003007c0bb5ee2b26bd57e21d1604690b9662594ea2c1cbc067415c4bfa5d85b',
    'H|WinSpreadProcess|DMNnkdNtnn|0x060001f1|218|c21744b0248f384108da6140fcfe6218a084845ae9731c829249c69d5b7f16d1',
    'H|WinSpreadProcess|WinInsertCombox|0x060001be|827|e7bd7c1f2b90ad619b6017a99e9e200ada457b31a91a6f9acef877937d9c5604',
    'H|WinSpreadProcess|InsertDateCell|0x060001af|203|d58a8897e64e6dcb1a2e2384cecff2acf6d7430e653d92a95dab8661a1b343d0',
    'H|frmWinToKhai|ProcessCmdKey|0x0600039f|9783|32a0b79138f778aa1f4e9a4ea5f29b7faac4df0e046c001aed5f31d88ce31845',
    'H|frmWinToKhai|cmdExport_Click|0x060003a2|1941|37de581c58099f8c3243310c0b95eebd2d7dd9750fc48f3cdd842a4303312031']


class Baselines(unittest.TestCase):
    def test_generated_views_are_synchronized(self):
        generator.main(['--check'])

    def test_default_is_the_unchanged_5_8_1_baseline(self):
        self.assertEqual((DATA['default'], oracle.DEFAULT, generator.DEFAULT), ('5.8.1',) * 3)
        self.assertEqual(V1['files'], {
            'Project/HTKK.exe': '411141d2e728a45f4a35a876afb169d0ac2450de2499e8a1f43ac29ab6401938',
            'Project/HTKK.exe.config': 'b3547d6a6a61fd6e8e8b64c8976e8702aa94a2b5a44a1cf394c5486162297047',
            'Project/TAX.HTKK.Business.dll': '281689aaa7df4db33d0debcfc61d32c0c318bb871d4a19a0277d871a7c04bba7',
            'Project/TAX.HTKK.Utilities.dll': 'ccc35605a4d3bb235f896d6ab43cec4c6543a404159cf10897a57cba23d817ec',
            'Project/Menu.xml': '4ac42eae600f4c98ed3df8a17b6d18770904acff5267913fdc9f98be4a9f24b4',
            'Project/Message.xml': '586fa399b2996c84eadfa5fbad74dfdeb0d1e349e27cee355a22f92e14474606',
            'InterfaceTemplates/excel/01_GTGT_TT80_283.xls': '8ad9ec9f0f3462da75ce4e873e4bb60003947e9edd5d738a5055e37d6c73b310',
            'InterfaceIni/Catalogue_DM_NNKD.xml': '8e19468e899e1b6e35a9d584dddd5e278c0daf1127d4f14ac5c4e03b3164ea88',
            'InterfaceIni/DM_DUNG_CHUNG.xml': 'cff4311dff86113853b2a70ca43992d72f4f5dd7ac643041e3d4d9ac2b1ba0b0',
            'InterfaceTemplates/xml/04_GTGT_TT89_309.xml': 'ca36d3480cafae45d23829fa9acf56f27a4df5734a278f7723e245884720f160',
            'InterfaceTemplates/excel/04_GTGT_TT89_309.xls': 'd7c88f7d930c17b3913c621e6e7aa241cc4a8b6f5da0aba92f077b9ec68f9deb'})
        self.assertEqual(V1['msi'], {'productVersion': '4.2.2', 'productCode': '{53B9335C-0849-4958-9E88-84E55F97929D}', 'mediaLastSequence': 4526, 'files': 4526, 'sizeMatches': 4526, 'msiHashRows': 4493, 'msiHashMatches': 4493, 'versionedWithoutMsiHash': 33, 'msiHashAlgorithm': 'MD5-legacy'})
        self.assertEqual(generator.entry_pins(V1, {}), REVIEWED_ENTRY)
        self.assertTrue(all(m['status'] == 'reviewed' for m in V1['methods']))

    def test_5_8_2_baseline_is_the_verified_distribution(self):
        self.assertEqual(V2['distribution'], {
            'officialUrl': 'https://www.fshare.vn/file/WYSRASTITCWB',
            'archiveSha256': '51baf5c8cea7f2d688476c611325e000bec2cbd3dff42f593b711cbe5863d424', 'archiveBytes': 89262341,
            'archiveFolder': 'HTKK_5.8.2_DLL_signed',
            'setupSha256': '1c2612d37176b6e02401e2e8b43c247490a7e8a971ef14144c8b9a5e84eb0efb',
            'msiSha256': '17c21f3ccf8c0bc6618b1b049ad7ee0328cc1bf8e914c15dbbfe7946b7c0fd73',
            'cabSha256': '5427c6632d5b60b15440e504effd314f050a56e66d4b2178355ee34b261b530c'})
        # Same signer and chain; the MSI ProductVersion stays the installer's own 4.2.2.
        self.assertEqual(V2['signer'], V1['signer'])
        self.assertEqual(V2['msi'], dict(V1['msi'], mediaLastSequence=4781, files=4781, sizeMatches=4781, msiHashRows=4748, msiHashMatches=4748))
        self.assertEqual((V2['configVersion'], V2['serviceVersion'], V2['mainWindowCaption']), ('5.8.2', '5.8.2', 'Hỗ trợ kê khai thuế - Phiên bản 5.8.2'))
        # Every pinned file changed in 5.8.2 (that is why it is version-selected).
        self.assertTrue(all(V1['files'][k] != V2['files'][k] for k in V1['files']))

    def test_5_8_2_methods_record_renumbering_and_real_changes(self):
        status = {m['id']: m['status'] for m in V2['methods']}
        self.assertEqual(sorted(k for k, s in status.items() if s == 'changed'), ['y8-entry-f5-row', 'y8-entry-grid-cellchange'])
        self.assertNotIn('reviewed', status.values())
        tokens = {m['id']: m['token'] for m in V2['methods']}
        self.assertEqual((tokens['oracle-common-info-bind'], tokens['oracle-header-binding-load'], tokens['oracle-table-insert'], tokens['oracle-table-remove']), ('0x060000f6', '0x060000ef', '0x06000200', '0x060001fd'))
        pins = generator.entry_pins(V2, {m['id']: m for m in V1['methods']})
        for old, new, method in zip(REVIEWED_ENTRY, pins, [m for m in V2['methods'] if m['id'].startswith('y8-entry-')]):
            if method['status'] == 'changed':
                # Never accepted as the reviewed body: the reviewed size/hash is required at the new token.
                self.assertEqual(new.split('|')[4:], old.split('|')[4:])
                self.assertNotEqual((method['ilBytes'], method['ilSha256']), tuple(old.split('|')[4:6]))
                self.assertTrue(method['change'])
            else:
                self.assertEqual(new, '|'.join(old.split('|')[:3] + [method['token'], str(method['ilBytes']), method['ilSha256']]))

    def test_validation_refuses_loosened_or_inconsistent_data(self):
        def broken(mutate):
            data = copy.deepcopy(DATA); mutate(data)
            with self.assertRaises(generator.BaselineError): generator.validate(data)
        broken(lambda d: d.update(default='5.8.2'))
        broken(lambda d: d['versions']['5.8.2']['distribution'].update(archiveFolder='HTKK_5.8.1_DLL_signed'))
        broken(lambda d: d['versions']['5.8.2']['msi'].update(msiHashMatches=4747))
        broken(lambda d: d['versions']['5.8.2']['signer'].update(serial='00'))
        broken(lambda d: d['versions']['5.8.2'].update(serviceVersion='5.8.1'))
        broken(lambda d: d['versions']['5.8.2']['files'].pop('Project/Menu.xml'))
        broken(lambda d: d['versions']['5.8.1']['methods'][0].update(status='token-renumbered'))
        broken(lambda d: d['versions']['5.8.2']['methods'][12].pop('change'))
        broken(lambda d: d['versions']['5.8.2']['methods'][0].update(ilBytes=353))
        broken(lambda d: d['versions']['5.8.2']['methods'][0].update(reviewedToken581='0x06000001'))
        broken(lambda d: d['versions']['5.8.2']['methods'].pop())
        broken(lambda d: d['versions'].update({'5.8.3': d['versions']['5.8.2']}))

    def test_legacy_single_version_pins_agree_with_the_default_baseline(self):
        # Oracle workflows and manual reference modes stay 5.8.1-only: their literal pins must be the
        # default baseline, so a 5.8.2 install makes them fail closed instead of drifting silently.
        text = ''.join((ROOT / n).read_text(encoding='utf-8') for n in (
            'Invoke-HtkkCommonInfoOracle.ps1', 'Invoke-HtkkControl14Oracle.ps1', 'Invoke-HtkkGtgt04EventOracle.ps1', 'Invoke-HtkkHeaderBindingOracle.ps1',
            'Invoke-HtkkTableLifecycleOracle.ps1', 'Save-HtkkSyntheticWindowDiagnostic.ps1', 'publish-gtgt-export-evidence.py', 'publish-common-header-evidence.py', 'HtkkGtgt04EventHost.cs'))
        for sha in V2['files'].values():
            self.assertNotIn(sha, text)
        web = load('oracle_web_output_test', 'publish-htkk-web-native-output.py')
        self.assertEqual(oracle.pins(web.PINS, '5.8.1'), web.PINS)
        changed = oracle.pins(web.PINS, '5.8.2')
        self.assertEqual({k for k in web.PINS if changed[k] != web.PINS[k]}, {k for k in web.PINS if k in V2['files']})


class Consumers(unittest.TestCase):
    def test_probe_selects_one_baseline_and_restricts_non_default_modes(self):
        probe = (ROOT / 'probe-htkk-windows.ps1').read_text(encoding='utf-8')
        self.assertIn("[ValidateSet('5.8.1','5.8.2')][string]$OracleVersion='5.8.1'", probe)
        self.assertIn("if($OracleVersion -cne $HtkkOracleDefaultVersion -and $InstallAndProbe -and $GuiAutomation -notin @('gtgt-web-import-inspect','declaration-web-import-inspect')) { throw 'ORACLE_VERSION_MODE_UNSUPPORTED' }", probe)
        for sha in list(V1['files'].values())[:4] + [V1['distribution'][k] for k in ('archiveSha256', 'setupSha256', 'msiSha256', 'cabSha256')]:
            self.assertNotIn(sha, probe)
        self.assertEqual(probe.count("$htkkOracle.files['Project/HTKK.exe']"), 2)
        self.assertEqual(probe.count('sourceVersion=$htkkOracle.version'), 3)
        self.assertNotIn("'5.8.1'", probe.replace("[ValidateSet('5.8.1','5.8.2')][string]$OracleVersion='5.8.1'", ''))
        for helper in ('Invoke-HtkkTaxIdOracle', 'Invoke-HtkkProfileAliasOracle', 'Invoke-HtkkCommonHeaderOracle', 'New-HtkkX86ReferenceHost', 'Invoke-HtkkSyntheticLogin'):
            call = next(line for line in probe.splitlines() if helper + ' -' in line)
            self.assertIn('-OracleVersion $OracleVersion', call, helper)
        for name in ('Test-HtkkTaxIdOracle.ps1', 'Test-HtkkProfileAliasOracle.ps1', 'Test-HtkkCommonHeaderOracle.ps1', 'New-HtkkX86ReferenceHost.ps1', 'Invoke-HtkkSyntheticLogin.ps1'):
            text = (ROOT / name).read_text(encoding='utf-8')
            self.assertIn("[ValidateSet('5.8.1','5.8.2')][string]$OracleVersion='5.8.1'", text, name)
            self.assertIn("Get-HtkkOracleBaseline -Version $OracleVersion", text, name)
            for sha in V1['files'].values():
                self.assertNotIn(sha, text, name)

    def test_workflow_passes_one_validated_version_to_every_versioned_step(self):
        workflow = (ROOT.parent / '.github/workflows/probe-htkk-windows.yml').read_text(encoding='utf-8')
        self.assertIn("      htkk_version:\n        description:", workflow)
        self.assertIn("        options: ['5.8.1', '5.8.2']\n        default: '5.8.1'\n", workflow)
        self.assertIn("if ($oracleVersion -cnotin @('5.8.1','5.8.2')) { throw 'Invalid HTKK oracle version.' }", workflow)
        self.assertIn('-GuiAutomation $guiAutomation -OracleVersion $oracleVersion\n', workflow)
        self.assertEqual(workflow.count('HTKK_ORACLE_VERSION: ${{ inputs.htkk_version }}'), 4)
        for script in ('publish-htkk-web-native-output.py', 'publish-htkk-declaration-native-output.py', 'report-native-case.py', 'report-native-failure.py'):
            step = workflow[:workflow.index(script)]
            self.assertIn('HTKK_ORACLE_VERSION: ${{ inputs.htkk_version }}\n        run: python', step[-200:], script)
        self.assertIn("${{ inputs.htkk_version == '5.8.2' && '-htkk582' || '' }}\n  cancel-in-progress: false", workflow)
        # Release dispatch never names a version: the default cohort is unchanged.
        self.assertNotIn('htkk_version', (ROOT / 'dispatch-native-cases.py').read_text(encoding='utf-8'))

    def test_csharp_reads_version_dependent_pins_from_the_selected_baseline(self):
        sources = {n: (ROOT / n).read_text(encoding='utf-8') for n in ('HtkkGuiReferenceAutomation.cs', 'HtkkGtgtPeriodAndSheet.cs', 'HtkkGtgtExportInspection.cs', 'HtkkDeclarationCasePlans.cs', 'HtkkWebTaxComparison.cs', 'HtkkDeclarationTreeComparison.cs')}
        for name, text in sources.items():
            for sha in V1['files'].values():
                self.assertNotIn(sha, text, name)
            self.assertNotIn('5.8.1"&&', text)
        start = sources['HtkkGuiReferenceAutomation.cs']
        self.assertIn(' public void Start(string requestedMode,string oracleVersion){\n  HtkkOracleBaseline.Select(oracleVersion);', start)
        self.assertNotIn('public void Start(string requestedMode){', start)
        self.assertIn('caption!=HtkkOracleBaseline.MainWindowCaption.Replace(" ",String.Empty)', start)
        self.assertIn('profile.Start("profile-save",HtkkOracleBaseline.DefaultVersion);', (ROOT / 'HtkkGtgt04EventHost.cs').read_text(encoding='utf-8'))

    @unittest.skipUnless(shutil.which('mcs') and shutil.which('mono'), 'local CLR baseline smoke test needs mono')
    def test_compiled_baseline_selects_exactly_once(self):
        program = ('using System;class P{static void Main(string[] a){'
                   'try{Console.WriteLine(HtkkOracleBaseline.Version);}catch(InvalidOperationException){Console.WriteLine("unselected");}'
                   'try{HtkkOracleBaseline.Select("5.8.3");}catch(ArgumentException){Console.WriteLine("unknown");}'
                   'HtkkOracleBaseline.Select(a[0]);HtkkOracleBaseline.Select(a[0]);'
                   'try{HtkkOracleBaseline.Select(a[0]=="5.8.1"?"5.8.2":"5.8.1");}catch(InvalidOperationException){Console.WriteLine("conflict");}'
                   'try{HtkkOracleBaseline.File("Project/Other.dll");}catch(ArgumentException){Console.WriteLine("unpinned");}'
                   'Console.WriteLine(HtkkOracleBaseline.File("Project/HTKK.exe")+" "+HtkkOracleBaseline.ServiceVersion);'
                   'Console.WriteLine(String.Join(";",HtkkOracleBaseline.EntryMethodPins()));'
                   'HtkkDeclarationEntryPlan e=HtkkDeclarationCasePlans.Entry("01NTNN-NCCNN-entry-M10-2026");Console.WriteLine(e.MethodPins.Length);}}')
        with tempfile.TemporaryDirectory() as directory:
            folder = pathlib.Path(directory); (folder / 'P.cs').write_text(program)
            subprocess.run(['mcs', '-langversion:ISO-2', '-warn:0', '-out:' + str(folder / 'p.exe'), str(folder / 'P.cs'), str(ROOT / 'HtkkOracleBaseline.cs'), str(ROOT / 'HtkkDeclarationCasePlans.cs')], check=True, capture_output=True)
            for version, value in DATA['versions'].items():
                out = subprocess.run(['mono', str(folder / 'p.exe'), version], check=True, capture_output=True, text=True).stdout.split('\n')
                self.assertEqual(out[:4], ['unselected', 'unknown', 'conflict', 'unpinned'])
                self.assertEqual(out[4], value['files']['Project/HTKK.exe'] + ' ' + version)
                self.assertEqual(out[5].split(';'), generator.entry_pins(value, {m['id']: m for m in V1['methods']}))
                self.assertEqual(out[6], '14')


class Separation(unittest.TestCase):
    def test_non_default_oracle_never_shares_context_branch_or_anchor(self):
        self.assertEqual(oracle.version({}), '5.8.1'); self.assertEqual(oracle.version({'HTKK_ORACLE_VERSION': ''}), '5.8.1')
        self.assertEqual(oracle.version({'HTKK_ORACLE_VERSION': '5.8.2'}), '5.8.2')
        for bad in ('5.8.3', '5.8.2 ', 'latest', '5.8'):
            with self.assertRaises(ValueError): oracle.version({'HTKK_ORACLE_VERSION': bad})
        self.assertEqual((oracle.status_context('htkk-native/zero', '5.8.1'), oracle.output_branch('gtgt-web-native-zero-output', '5.8.1'), oracle.suffix('5.8.1')), ('htkk-native/zero', 'gtgt-web-native-zero-output', ''))
        self.assertEqual((oracle.status_context('htkk-native/zero', '5.8.2'), oracle.output_branch('gtgt-web-native-zero-output', '5.8.2'), oracle.suffix('5.8.2')), ('htkk-native/zero@htkk582', 'gtgt-web-native-zero-output-htkk582', '-htkk582'))
        with self.assertRaises(ValueError): oracle.status_context('htkk-native/zero', '9')

    def test_status_callbacks_use_the_versioned_context(self):
        callback = load('oracle_callback_test', 'report-native-case.py')
        case = callback.dispatch.CASES[0]
        default = callback.payload(case, 'success', 'https://github.com', '123')
        self.assertEqual(default['context'], callback.dispatch.CONTEXTS[case]); self.assertEqual(default['description'], 'Fixed synthetic native case passed')
        other = callback.payload(case, 'failure', 'https://github.com', '123', 'a' * 40, '5.8.2')
        self.assertEqual(other['context'], callback.dispatch.CONTEXTS[case] + '@htkk582'); self.assertIn(' on HTKK 5.8.2 input:' + 'a' * 40, other['description'])
        failure = load('oracle_failure_test', 'report-native-failure.py')
        env = {'GITHUB_REPOSITORY': callback.dispatch.BUILDER, 'GITHUB_REF': 'refs/heads/main', 'READINESS_RESULT': 'failure', 'GUI_AUTOMATION': callback.dispatch.case_registry.driver(case),
               'COMMIT_SHA': 'b' * 40, 'GITHUB_RUN_ID': '42', 'WEB_CASE_ID': case, 'GITHUB_SERVER_URL': 'https://github.com'}
        self.assertEqual(failure.request(env)[1]['context'], callback.dispatch.CONTEXTS[case])
        self.assertEqual(failure.request(dict(env, HTKK_ORACLE_VERSION='5.8.2'))[1]['context'], callback.dispatch.CONTEXTS[case] + '@htkk582')
        with self.assertRaises(ValueError): failure.request(dict(env, HTKK_ORACLE_VERSION='5.9.0'))

    def test_publishers_bind_the_service_version_to_the_selected_oracle(self):
        web = load('oracle_web_publisher_test', 'publish-htkk-web-native-output.py')
        self.assertEqual(web.service('5.8.1')['pbanDVu'], '5.8.1'); self.assertEqual(web.service('5.8.2')['pbanDVu'], '5.8.2')
        declaration = load('oracle_declaration_publisher_test', 'publish-htkk-declaration-native-output.py')
        cases = declaration.declaration
        self.assertEqual(cases.native_service(), ('HTKK', 'HỖ TRỢ KÊ KHAI THUẾ', '5.8.1')); self.assertEqual(cases.native_service('5.8.2'), ('HTKK', 'HỖ TRỢ KÊ KHAI THUẾ', '5.8.2'))
        for text in ((ROOT / 'publish-htkk-web-native-output.py').read_text(encoding='utf-8'), (ROOT / 'publish-htkk-declaration-native-output.py').read_text(encoding='utf-8')):
            self.assertIn("metadata['caseId']+oracle.suffix(version),artifact)", text)
            self.assertIn("branch=oracle.output_branch(BRANCHES[metadata['caseId']],version)", text)
            self.assertIn('version=oracle.version(os.environ)', text)
            self.assertNotIn("'sourceVersion':'5.8.1'", text)


if __name__ == '__main__':
    unittest.main()
