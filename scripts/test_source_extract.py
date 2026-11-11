"""Offline contracts for the private HTKK 5.8.1 source extract (source-extract.yml)."""
import hashlib, importlib.util, io, json, os, pathlib, re, shutil, subprocess, tempfile, unittest, urllib.error
from unittest import mock
import sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from sandbox_test_support import Sandbox

ROOT = pathlib.Path(__file__).resolve().parent
WORKFLOW = ROOT.parent / '.github' / 'workflows' / 'source-extract.yml'
spec = importlib.util.spec_from_file_location('source_extract', ROOT / 'source-extract.py')
x = importlib.util.module_from_spec(spec)
spec.loader.exec_module(x)
TOKEN = 'ghp_' + 'A1b2' * 9


def sha(data):
    return hashlib.sha256(data).hexdigest()


def steps(text):
    """Split the single job into named step blocks without a YAML dependency."""
    blocks = re.split(r'\n      - ', text.split('\n    steps:\n', 1)[1])
    return [b for b in blocks if b.strip()]


class Fixture:
    """Synthetic 3-file MSI layout, trust manifest and payload; no vendor bytes."""

    def __init__(self, base):
        self.base = pathlib.Path(base)
        self.contents = [b'MZ fake exe', b'<Menu/>', b'<Cells/>']
        self.files = [
            {'id': 'htkk.exe', 'component': 'C_Project', 'fileName': 'HTKK~1.EXE|HTKK.exe', 'bytes': 0, 'version': '5.8.1.0', 'sequence': 1},
            {'id': 'menu.xml', 'component': 'C_Project', 'fileName': 'Menu.xml', 'bytes': 0, 'version': '', 'sequence': 2},
            {'id': 'a.xml', 'component': 'C_Xml', 'fileName': 'A_XML~1.XML|01_GTGT_TT80_283.xml', 'bytes': 0, 'version': '', 'sequence': 3},
        ]
        for f, c in zip(self.files, self.contents):
            f['bytes'] = len(c)
        self.layout = {
            'format': 'htkk-msi-layout-tables-v1', 'version': '5.8.1', 'sourcePins': {}, 'payloadNaming': 'x', 'ready': False, 'automaticActivation': False,
            'files': self.files,
            'components': [{'id': 'C_Project', 'directory': 'PROJECT'}, {'id': 'C_Xml', 'directory': 'XMLDIR'}],
            'directories': [
                {'id': 'TARGETDIR', 'parent': '', 'defaultDir': 'SourceDir'},
                {'id': 'ProgramFilesFolder', 'parent': 'TARGETDIR', 'defaultDir': 'PFiles'},
                {'id': 'INSTALLDIR', 'parent': 'ProgramFilesFolder', 'defaultDir': 'HTKK'},
                {'id': 'PROJECT', 'parent': 'INSTALLDIR', 'defaultDir': 'Project'},
                {'id': 'TEMPLATES', 'parent': 'INSTALLDIR', 'defaultDir': 'INTERF~1|InterfaceTemplates'},
                {'id': 'XMLDIR', 'parent': 'TEMPLATES', 'defaultDir': 'xml:srcxml'},
            ],
            'fileHashes': [{'id': 'menu.xml', 'options': 0, 'md5': hashlib.md5(self.contents[1]).hexdigest()},
                           {'id': 'a.xml', 'options': 0, 'md5': hashlib.md5(self.contents[2]).hexdigest()}],
        }
        self.policy = {
            'format': 'htkk-source-extract-policy-v1', 'version': '5.8.1', 'msiSha256': '7c1da251ee2acd126a2363e4457502b8ad6fc0792d78dc0a92b153701dc29080',
            'installRoot': {'markerMsiFileId': 'htkk.exe', 'markerPath': 'Project/HTKK.exe'}, 'scopes': ['priority', 'full'],
            'sharedDirectories': ['InterfaceIni'], 'sharedExcludes': ['InterfaceIni/GIA_TINH'], 'assemblyDirectories': ['Project'], 'assemblyExtensions': ['.dll', '.exe', '.config'],
            'forms': [{'id': '01-gtgt', 'title': '01/GTGT', 'menuIds': ['D1'], 'paths': ['InterfaceTemplates/xml/01_GTGT_TT80_283.xml']}],
            'pins': [{'path': 'InterfaceTemplates/xml/01_GTGT_TT80_283.xml', 'sha256': sha(self.contents[2]), 'msiFileId': 'a.xml'},
                     {'path': 'Project/HTKK.exe', 'sha256': sha(self.contents[0]), 'msiFileId': 'htkk.exe'}],
        }
        self.candidate = self.base / 'candidate'
        self.export = self.candidate / 'export'
        self.result = self.candidate / 'export-result.json'
        self.bundle = self.base / 'bundle'

    def write(self):
        (self.export / 'payload').mkdir(parents=True)
        for i, c in enumerate(self.contents):
            (self.export / 'payload' / ('%05d.bin' % i)).write_bytes(c)
        (self.export / 'layout.json').write_text(json.dumps(self.layout))
        (self.candidate / 'trust.json').write_text(json.dumps({'status': 'baseline-verified', 'sourcePins': {'msi': 'm'}, 'checks': {'a': True}, 'payload': {'files': 3}}))
        manifest = {'format': 'htkk-reviewed-source-payload-sha256-v1', 'version': '5.8.1', 'ready': False, 'automaticActivation': False,
                    'files': [{'fileId': f['id'], 'bytes': len(c), 'sha256': sha(c), 'msiHashVerified': f['id'] != 'htkk.exe', 'versioned': bool(f['version'])} for f, c in zip(self.files, self.contents)]}
        (self.candidate / 'payload-sha256.json').write_text(json.dumps(manifest))
        self.result.write_text(json.dumps(self.export_result()))
        policy_path = self.base / 'policy.json'
        policy_path.write_text(json.dumps(self.policy))
        return policy_path

    def export_result(self):
        return {'format': 'htkk-source-payload-export-v1', 'status': 'exported', 'failureCode': None, 'ready': False, 'automaticActivation': False,
                'vendorCodeExecuted': False, 'installerExecuted': False, 'msiCustomActionsExecuted': False, 'workerTimedOut': False,
                'workerStopped': True, 'jobCleanupVerified': True, 'workerExitCode': 0, 'files': 3, 'sizeMatches': 3, 'msiHashMatches': 2,
                'versionedWithoutMsiHash': 1, 'workerScriptSha256': sha((ROOT / 'Export-HtkkSourcePayload.ps1').read_bytes()),
                'cabinetHelperSha256': sha((ROOT / 'HtkkSourceCabinet.cs').read_bytes())}


class SmallCounts:
    def __enter__(self):
        self.patch = mock.patch.multiple(x, FILE_COUNT=3, HASHED_COUNT=2, UNHASHED_VERSIONED_COUNT=1)
        self.patch.start()
        return self

    def __exit__(self, *exc):
        self.patch.stop()


def trusted(trust, directory):
    return True


class PolicyTests(unittest.TestCase):
    def test_committed_policy_is_valid_and_covers_priority_forms(self):
        policy = x.load_policy()
        ids = {f['id'] for f in policy['forms']}
        self.assertEqual(ids, {'01-gtgt', '04-gtgt', '05-kk-tncn', '05-qtt-tncn', '02-qtt-tncn', '03-tndn', 'bctc-tt133', 'bctc-tt200', '01-cnkd', '01-tts', '01-lpmb', 'common-header'})
        menus = {m for f in policy['forms'] for m in f['menuIds']}
        self.assertTrue({'D1', 'D4', 'L7', 'B9', 'B8', 'N8', 'A2', 'A5', 'A6', 'A7', '78', 'G5', 'Q8', 'U5', 'G7', 'L1'} <= menus)
        pins = {p['path']: p for p in policy['pins']}
        for required in ('InterfaceTemplates/excel/01_GTGT_TT80_283.xls', 'InterfaceTemplates/xml/01_GTGT_TT80_283.xml', 'InterfaceTemplates/Validate/01_GTGT_TT80_283.xsd',
                         'InterfaceTemplates/Validate/KHBS_01_GTGT_TT80_283.xsd', 'Project/Menu.xml', 'Project/HTKK.exe'):
            self.assertIn(required, pins)
        self.assertEqual(policy['installRoot'], {'markerMsiFileId': 'htkk.exe', 'markerPath': 'Project/HTKK.exe'})
        self.assertEqual(policy['assemblyDirectories'], ['Project'])
        self.assertIn('InterfaceIni/GIA_TINH', policy['sharedExcludes'])
        # Every form's interactive workbook, sheet controls and schema: source of the web's
        # read-only XML viewer layouts, kept in the priority scope (not only the priority forms).
        for directory in ('InterfaceTemplates/excel', 'InterfaceTemplates/xml', 'InterfaceTemplates/Validate'):
            self.assertIn(directory, policy['sharedDirectories'])
        self.assertNotIn('InterfaceTemplates', policy['sharedDirectories'])

    def test_policy_rejects_unpinned_form_paths_duplicates_and_unsafe_paths(self):
        with tempfile.TemporaryDirectory() as d:
            f = Fixture(d)
            for mutate, code in ((lambda p: p['forms'][0]['paths'].append('InterfaceTemplates/xml/other.xml'), 'POLICY_FORM_UNPINNED'),
                                 (lambda p: p['pins'].append(dict(p['pins'][0], msiFileId='b.xml')), 'POLICY_DUPLICATE'),
                                 (lambda p: p['pins'].append({'path': '../escape.xml', 'sha256': '0' * 64, 'msiFileId': 'c.xml'}), 'POLICY_FORMAT'),
                                 (lambda p: p.update(msiSha256='0' * 64), 'POLICY_PIN'),
                                 (lambda p: p['installRoot'].update(markerPath='Project/Other.exe'), 'POLICY_ROOT')):
                policy = json.loads(json.dumps(f.policy))
                mutate(policy)
                path = pathlib.Path(d) / 'p.json'
                path.write_text(json.dumps(policy))
                with self.assertRaisesRegex(x.ExtractError, code):
                    x.load_policy(path)


class LayoutTests(unittest.TestCase):
    def test_directory_resolution_uses_long_target_names_and_fixed_standard_folders(self):
        f = Fixture('.')
        resolved = x.resolve_directories(f.layout['directories'])
        self.assertEqual(resolved['XMLDIR'], 'Program Files/HTKK/InterfaceTemplates/xml')
        self.assertEqual(resolved['PROJECT'], 'Program Files/HTKK/Project')
        self.assertEqual(resolved['TARGETDIR'], '')
        with SmallCounts():
            rows = x.resolve_layout(f.layout)
        self.assertEqual([r['msiPath'] for r in rows], ['Program Files/HTKK/Project/HTKK.exe', 'Program Files/HTKK/Project/Menu.xml', 'Program Files/HTKK/InterfaceTemplates/xml/01_GTGT_TT80_283.xml'])
        self.assertEqual(rows[0]['md5InSignedMsi'], None)

    def test_dot_directory_inherits_parent(self):
        rows = [{'id': 'TARGETDIR', 'parent': '', 'defaultDir': 'SourceDir'}, {'id': 'A', 'parent': 'TARGETDIR', 'defaultDir': 'App'}, {'id': 'B', 'parent': 'A', 'defaultDir': '.'}]
        self.assertEqual(x.resolve_directories(rows)['B'], 'App')

    def test_unsafe_names_cycles_and_unknown_parents_fail_closed(self):
        base = [{'id': 'TARGETDIR', 'parent': '', 'defaultDir': 'SourceDir'}]
        for row, code in (({'id': 'A', 'parent': 'TARGETDIR', 'defaultDir': '..'}, 'MSI_UNSAFE_NAME'),
                          ({'id': 'A', 'parent': 'TARGETDIR', 'defaultDir': 'a\\b'}, 'MSI_UNSAFE_NAME'),
                          ({'id': 'A', 'parent': 'TARGETDIR', 'defaultDir': 'CON'}, 'MSI_UNSAFE_NAME'),
                          ({'id': 'A', 'parent': 'MISSING', 'defaultDir': 'x'}, 'MSI_LAYOUT')):
            with self.assertRaisesRegex(x.ExtractError, code):
                x.resolve_directories(base + [row])
        cycle = base + [{'id': 'A', 'parent': 'B', 'defaultDir': 'a'}, {'id': 'B', 'parent': 'A', 'defaultDir': 'b'}]
        with self.assertRaisesRegex(x.ExtractError, 'MSI_LAYOUT'):
            x.resolve_directories(cycle)

    def test_file_names_cannot_escape_and_file_count_is_exact(self):
        f = Fixture('.')
        with SmallCounts():
            bad = json.loads(json.dumps(f.layout))
            bad['files'][2]['fileName'] = 'x|../../evil.dll'
            with self.assertRaisesRegex(x.ExtractError, 'MSI_UNSAFE_NAME'):
                x.resolve_layout(bad)
            short = json.loads(json.dumps(f.layout))
            short['files'].pop()
            with self.assertRaisesRegex(x.ExtractError, 'MSI_FILE_COUNTS'):
                x.resolve_layout(short)
            dup = json.loads(json.dumps(f.layout))
            dup['files'][2]['id'] = 'MENU.xml'
            with self.assertRaisesRegex(x.ExtractError, 'MSI_FILE_IDENTITIES'):
                x.resolve_layout(dup)

    def test_install_root_collisions_and_outside_files(self):
        f = Fixture('.')
        with SmallCounts():
            rows = x.resolve_layout(f.layout)
        for r, c in zip(rows, f.contents):
            r['sha256'] = sha(c)
        root, conflicts = x.assign_install_paths(rows, f.policy)
        self.assertEqual(root, 'Program Files/HTKK/')
        self.assertEqual(rows[2]['path'], 'InterfaceTemplates/xml/01_GTGT_TT80_283.xml')
        self.assertEqual(conflicts, [])
        x.verify_pins(rows, f.policy)
        rows2 = [dict(r) for r in rows]
        rows2[1]['msiPath'] = 'Windows/System32/x.dll'
        rows2[2]['msiPath'] = 'Program Files/HTKK/Project/menu.XML'
        rows2[2]['sha256'] = rows2[1]['sha256'] = 'f' * 64
        x.assign_install_paths(rows2, f.policy)
        self.assertEqual(rows2[1]['path'], '_outside/Windows/System32/x.dll')
        rows3 = [dict(r) for r in rows]
        rows3[2]['msiPath'] = 'Program Files/HTKK/Project/MENU.xml'
        _, conflicts = x.assign_install_paths(rows3, f.policy)
        self.assertEqual(conflicts[0]['resolution'], 'different-bytes-moved-to-_conflicts')
        self.assertTrue(all(r['path'].startswith('_conflicts/') for r in rows3[1:]))
        rows4 = [dict(r) for r in rows]
        rows4[2]['msiPath'] = 'Program Files/HTKK/project/Other.xml'
        with self.assertRaisesRegex(x.ExtractError, 'PATH_CASE_COLLISION'):
            x.assign_install_paths(rows4, f.policy)

    def test_pins_require_same_path_hash_and_file_id(self):
        f = Fixture('.')
        with SmallCounts():
            rows = x.resolve_layout(f.layout)
        for r, c in zip(rows, f.contents):
            r['sha256'] = sha(c)
        x.assign_install_paths(rows, f.policy)
        for mutate, code in ((lambda p: p['pins'][0].update(sha256='0' * 64), 'PIN_HASH_MISMATCH'),
                             (lambda p: p['pins'][0].update(path='InterfaceTemplates/xml/Other.xml'), 'PIN_PATH_MISMATCH'),
                             (lambda p: p['pins'][0].update(msiFileId='missing.xml'), 'PIN_MISSING')):
            policy = json.loads(json.dumps(f.policy))
            mutate(policy)
            with self.assertRaisesRegex(x.ExtractError, code):
                x.verify_pins(rows, policy)

    def test_priority_scope_keeps_forms_pins_shared_and_assemblies_only(self):
        f = Fixture('.')
        entries = [{'fileId': 'a', 'path': 'InterfaceTemplates/xml/01_GTGT_TT80_283.xml'}, {'fileId': 'b', 'path': 'Project/HTKK.exe'},
                   {'fileId': 'c', 'path': 'Project/Menu.xml'}, {'fileId': 'd', 'path': 'InterfaceIni/Catalogue.xml'},
                   {'fileId': 'e', 'path': 'InterfaceIni/GIA_TINH/HN.xml'}, {'fileId': 'f', 'path': 'InterfaceTemplates/xml/other.xml'},
                   {'fileId': 'g', 'path': 'Lib/Other.DLL'}, {'fileId': 'h', 'path': '_outside/Windows/x.dll'}]
        chosen = {e['fileId']: e['categories'] for e in x.select([dict(e) for e in entries], f.policy, 'priority')}
        self.assertEqual(set(chosen), {'a', 'b', 'c', 'd', 'g'})
        self.assertEqual(chosen['a'], ['form', 'pinned'])
        self.assertIn('assembly', chosen['g'])
        full = {e['fileId'] for e in x.select([dict(e) for e in entries], f.policy, 'full')}
        self.assertEqual(full, set('abcdefgh'))
        with self.assertRaisesRegex(x.ExtractError, 'SCOPE_POLICY'):
            x.select(entries, f.policy, 'all')

    def test_priority_scope_keeps_every_form_template_with_the_committed_directories(self):
        f = Fixture('.')
        f.policy['sharedDirectories'] = x.load_policy()['sharedDirectories']
        entries = [{'fileId': 'a', 'path': 'InterfaceTemplates/excel/99_BCTC_305.xls'}, {'fileId': 'b', 'path': 'InterfaceTemplates/xml/01A_DNHT_283.xml'},
                   {'fileId': 'c', 'path': 'InterfaceTemplates/Validate/01A_DNHT_283.xsd'}, {'fileId': 'd', 'path': 'ReportTemplates/Excel/01A_DNHT_283.xls'},
                   {'fileId': 'e', 'path': 'InterfaceTemplates/Template.xls'}, {'fileId': 'f', 'path': 'InterfaceIni/GIA_TINH/HN.xml'}]
        chosen = {e['fileId']: e['categories'] for e in x.select([dict(e) for e in entries], f.policy, 'priority')}
        self.assertEqual(chosen, {'a': ['shared'], 'b': ['shared'], 'c': ['shared']})


class BundleTests(unittest.TestCase):
    def build(self, d, scope='priority', mutate=None):
        f = Fixture(d)
        policy_path = f.write()
        if mutate:
            mutate(f)
        with SmallCounts():
            return f, x.build_bundle(f.candidate, f.export, f.result, f.bundle, scope, x.load_policy(policy_path), trust_validator=trusted)

    def test_bundle_layout_manifest_and_checksums(self):
        with tempfile.TemporaryDirectory() as d:
            f, manifest = self.build(d)
            self.assertEqual({p.name for p in f.bundle.iterdir()}, set(x.BUNDLE_TOP))
            self.assertEqual(manifest['counts']['included'], 3)
            self.assertEqual((f.bundle / 'payload/Project/Menu.xml').read_bytes(), b'<Menu/>')
            self.assertEqual(manifest['installRoot'], 'Program Files/HTKK')
            sums = (f.bundle / 'SHA256SUMS').read_text().splitlines()
            self.assertIn(sha(b'<Cells/>') + '  payload/InterfaceTemplates/xml/01_GTGT_TT80_283.xml', sums)
            self.assertFalse(manifest['ready'] or manifest['automaticActivation'] or manifest['vendorCodeExecuted'])
            catalog = json.loads((f.bundle / 'catalog.json').read_text())
            self.assertEqual(len(catalog['files']), 3)
            self.assertEqual(manifest['forms'][0]['paths'], ['InterfaceTemplates/xml/01_GTGT_TT80_283.xml'])
            self.assertEqual(x.validate_bundle(f.bundle)['counts'], manifest['counts'])

    def test_bundle_rejects_tampering_and_extra_files(self):
        with tempfile.TemporaryDirectory() as d:
            f, _ = self.build(d)
            (f.bundle / 'payload/Project/Menu.xml').write_bytes(b'<Changed/>')
            with self.assertRaisesRegex(x.ExtractError, 'BUNDLE_HASH'):
                x.validate_bundle(f.bundle)
        with tempfile.TemporaryDirectory() as d:
            f, _ = self.build(d)
            (f.bundle / 'payload/extra.txt').write_bytes(b'x')
            with self.assertRaisesRegex(x.ExtractError, 'BUNDLE_HASH'):
                x.validate_bundle(f.bundle)
        with tempfile.TemporaryDirectory() as d:
            f, _ = self.build(d)
            (f.bundle / 'leak.log').write_bytes(b'x')
            with self.assertRaisesRegex(x.ExtractError, 'BUNDLE_LAYOUT'):
                x.validate_bundle(f.bundle)

    def test_two_extractions_must_agree_and_export_must_be_clean(self):
        def different(f):
            (f.export / 'payload' / '00001.bin').write_bytes(b'<Menx/>')
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(x.ExtractError, 'TRUST_PAYLOAD_MISMATCH'):
                self.build(d, mutate=different)
        for key, value in (('vendorCodeExecuted', True), ('workerStopped', False), ('status', 'blocked'), ('workerScriptSha256', '0' * 64), ('msiHashMatches', 1)):
            def dirty(f, key=key, value=value):
                r = f.export_result()
                r[key] = value
                f.result.write_text(json.dumps(r))
            with tempfile.TemporaryDirectory() as d:
                with self.assertRaisesRegex(x.ExtractError, 'EXPORT_NOT_VERIFIED'):
                    self.build(d, mutate=dirty)

    def test_unverified_trust_and_extra_payload_members_block(self):
        def untrusted(f):
            (f.candidate / 'trust.json').write_text(json.dumps({'status': 'blocked'}))
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(x.ExtractError, 'TRUST_NOT_VERIFIED'):
                self.build(d, mutate=untrusted)
        def extra(f):
            (f.export / 'payload' / 'name.dll').write_bytes(b'x')
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(x.ExtractError, 'PAYLOAD_NAMES'):
                self.build(d, mutate=extra)

    def test_real_trust_validator_is_default(self):
        with tempfile.TemporaryDirectory() as d:
            f = Fixture(d)
            policy = x.load_policy(f.write())
            with SmallCounts(), self.assertRaises(ValueError):
                x.build_bundle(f.candidate, f.export, f.result, f.bundle, 'priority', policy)
            self.assertFalse(f.bundle.exists())


class FakeRemote:
    """GitHub API double backed by a local bare repository."""

    def __init__(self, bare, private=True, box=None):
        self.bare = bare
        self.box = box
        self.private = private
        self.calls = []

    def git(self, *args):
        command = ['git', '--git-dir', str(self.bare)] + list(args)
        if self.box is not None:
            self.box.check_git(command)
        return subprocess.run(command, capture_output=True, text=True)

    def __call__(self, path, token, payload=None, method=None):
        self.calls.append((path, token, payload is not None))
        if path == '':
            return {'private': self.private, 'full_name': x.REPO}
        if path == '/git/ref/heads/' + x.BRANCH:
            r = self.git('rev-parse', '--verify', '-q', 'refs/heads/' + x.BRANCH)
            if r.returncode:
                raise urllib.error.HTTPError('u', 404, 'Not Found', {}, io.BytesIO(b''))
            return {'ref': 'refs/heads/' + x.BRANCH, 'object': {'type': 'commit', 'sha': r.stdout.strip()}}
        if path.startswith('/git/commits/'):
            return {'tree': {'sha': self.git('rev-parse', path.rsplit('/', 1)[1] + '^{tree}').stdout.strip()}}
        raise AssertionError(path)


@unittest.skipUnless(shutil.which('git'), 'git unavailable')
class PublishTests(unittest.TestCase):
    def setUp(self):
        # Bundle, work directories and the fake remote all live in a sandbox this test created; every git command
        # of source-extract.py is checked against it.
        self.box = Sandbox.for_test(self)
        self.box.guard(x, self)
        self.base = self.box.root
        self.fixture, _ = BundleTests().build(str(self.base / 'f'))
        self.bare = self.base / 'remote.git'
        self.box.git('init', '--quiet', '--bare', self.bare)
        self.remote = FakeRemote(self.bare, box=self.box)
        self.push = mock.patch.object(x, 'PUSH_URL', str(self.bare))
        self.push.start()

    def tearDown(self):
        self.push.stop()

    def publish(self, name, **kw):
        return x.publish(self.fixture.bundle, self.base / name, TOKEN, '123', 1, 'a' * 40, fetch=self.remote, **kw)

    def test_creates_branch_tag_then_reports_unchanged(self):
        first = self.publish('g1')
        self.assertEqual(first['result'], 'published')
        self.assertEqual(self.remote.git('rev-parse', 'refs/heads/' + x.BRANCH).stdout.strip(), first['commit'])
        self.assertEqual(self.remote.git('rev-parse', 'refs/tags/' + x.TAG_PREFIX + '123-1').stdout.strip(), first['commit'])
        files = self.remote.git('ls-tree', '-r', '--name-only', first['commit']).stdout.split()
        self.assertIn('payload/Project/Menu.xml', files)
        self.assertIn('manifest.json', files)
        self.assertEqual(self.remote.git('cat-file', 'blob', first['commit'] + ':payload/Project/Menu.xml').stdout, '<Menu/>')
        second = x.publish(self.fixture.bundle, self.base / 'g2', TOKEN, '124', 1, 'a' * 40, fetch=self.remote)
        self.assertEqual(second['result'], 'unchanged')
        self.assertTrue(self.remote.git('rev-parse', '--verify', '-q', 'refs/tags/' + x.TAG_PREFIX + '124-1').returncode)
        self.assertTrue(all(call[2] is False for call in self.remote.calls))

    def test_replaces_only_observed_commit_and_keeps_old_snapshot_tag(self):
        first = self.publish('g1')
        (self.fixture.bundle / 'README.md').write_bytes(b'changed\n')
        second = x.publish(self.fixture.bundle, self.base / 'g2', TOKEN, '200', 2, 'b' * 40, fetch=self.remote)
        self.assertEqual(second['result'], 'published')
        self.assertEqual(second['previousCommit'], first['commit'])
        self.assertEqual(self.remote.git('rev-parse', 'refs/tags/' + x.TAG_PREFIX + '123-1').stdout.strip(), first['commit'])
        self.assertIn('run=200/2', self.remote.git('log', '-1', '--format=%B', second['commit']).stdout)

    def test_dry_run_and_public_target_never_push(self):
        result = self.publish('g1', dry_run=True)
        self.assertEqual(result['result'], 'dry-run')
        self.assertTrue(self.remote.git('rev-parse', '--verify', '-q', 'refs/heads/' + x.BRANCH).returncode)
        self.remote.private = False
        with self.assertRaisesRegex(x.ExtractError, 'TARGET_NOT_PRIVATE'):
            self.publish('g2')

    def test_tampered_bundle_is_never_pushed(self):
        (self.fixture.bundle / 'payload/Project/HTKK.exe').write_bytes(b'MZ changed')
        with self.assertRaisesRegex(x.ExtractError, 'BUNDLE_HASH'):
            self.publish('g1')
        self.assertEqual(self.remote.calls, [])


class GitEnvironmentTests(unittest.TestCase):
    def test_only_allowlisted_variables_and_header_scoped_token(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.dict(os.environ, {'GITHUB_TOKEN': 'leak1', 'SOURCE_READ_TOKEN': 'leak2', 'AGENT_AUTH_TOKEN': 'leak3', 'ACTIONS_RUNTIME_TOKEN': 'leak4'}):
            plain = x.git_environment(d)
            self.assertFalse(any('leak' in v for v in plain.values()))
            self.assertNotIn(TOKEN, json.dumps(plain))
            withtoken = x.git_environment(d, TOKEN)
            self.assertFalse(any('leak' in v for v in withtoken.values()))
            keys = {withtoken['GIT_CONFIG_KEY_%d' % i]: withtoken['GIT_CONFIG_VALUE_%d' % i] for i in range(int(withtoken['GIT_CONFIG_COUNT']))}
            self.assertEqual(keys['core.autocrlf'], 'false')
            self.assertEqual(keys['credential.helper'], '')
            self.assertTrue(keys['http.https://github.com/.extraheader'].startswith('AUTHORIZATION: basic '))
            self.assertEqual(withtoken['GIT_CONFIG_NOSYSTEM'], '1')
            self.assertEqual(withtoken['GIT_TERMINAL_PROMPT'], '0')
            with self.assertRaisesRegex(x.ExtractError, 'PUBLISH_TOKEN'):
                x.git_environment(d, 'bad token\nX: y')


class DownloadTests(unittest.TestCase):
    def fake(self, failures):
        calls = []

        def fetch(url, destination, expected, relay_token=None, transport='direct', max_attempts=2):
            calls.append((url, transport, relay_token, expected))
            if failures:
                raise failures.pop(0)
            pathlib.Path(destination).write_bytes(b'x')
            return {'sha256': expected, 'expectedHashMatched': True, 'transport': transport}
        return fetch, calls

    def test_pinned_url_and_hash_only(self):
        with tempfile.TemporaryDirectory() as d:
            fetch, calls = self.fake([])
            result = x.download(pathlib.Path(d) / 'c', 'auto', None, fetch)
            self.assertEqual(result['status'], 'downloaded-pinned-baseline')
            self.assertEqual(calls, [(x.OFFICIAL_URL, 'direct', None, x.candidate.BASELINE_OFFICIAL_SHA256)])
            self.assertTrue((pathlib.Path(d) / 'c' / 'downloads.json').exists())

    def test_relay_only_after_retryable_failure_with_token(self):
        transient = x.candidate.CandidateError('TIMEOUT', retryable=True)
        with tempfile.TemporaryDirectory() as d:
            fetch, calls = self.fake([transient])
            self.assertEqual(x.download(pathlib.Path(d) / 'c', 'auto', 'relay-secret', fetch)['status'], 'downloaded-pinned-baseline')
            self.assertEqual([c[1] for c in calls], ['direct', 'relay'])
        with tempfile.TemporaryDirectory() as d:
            fetch, calls = self.fake([x.candidate.CandidateError('TLS')])
            result = x.download(pathlib.Path(d) / 'c', 'auto', 'relay-secret', fetch)
            self.assertEqual((result['status'], result['failureCode']), ('blocked', 'TLS'))
            self.assertEqual(len(calls), 1)
        with tempfile.TemporaryDirectory() as d:
            fetch, calls = self.fake([transient])
            self.assertEqual(x.download(pathlib.Path(d) / 'c', 'direct', 'relay-secret', fetch)['status'], 'blocked')
            self.assertEqual([c[1] for c in calls], ['direct'])
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(x.ExtractError, 'RELAY_TOKEN_MISSING'):
                x.download(pathlib.Path(d) / 'c', 'relay', None, self.fake([])[0])

    def test_entry_point_requires_trusted_main(self):
        with mock.patch.dict(os.environ, {'GITHUB_REPOSITORY': x.BUILDER, 'GITHUB_REF': 'refs/heads/work/source-extract'}), mock.patch('sys.argv', ['x', 'stage']):
            with self.assertRaisesRegex(x.ExtractError, 'TRUSTED_REF'):
                x.main()


class WorkflowContractTests(unittest.TestCase):
    def setUp(self):
        self.text = WORKFLOW.read_text(encoding='utf-8')
        self.steps = steps(self.text)

    def step(self, needle):
        found = [s for s in self.steps if needle in s]
        self.assertEqual(len(found), 1, needle)
        return found[0]

    def test_dispatch_only_on_main_with_read_only_permissions(self):
        head = self.text.split('\njobs:', 1)[0]
        self.assertIn('workflow_dispatch:', head)
        for trigger in ('push:', 'pull_request', 'schedule:', 'workflow_run', 'repository_dispatch'):
            self.assertNotIn(trigger, head)
        self.assertIn("if: github.ref == 'refs/heads/main'", self.text)
        self.assertIn('permissions:\n  contents: read\n', self.text)
        self.assertEqual(self.text.count('permissions:'), 1)
        self.assertIn('persist-credentials: false', self.text)
        self.assertEqual(self.text.count('uses: '), 1)

    def test_no_public_artifacts_caches_or_payload_logging(self):
        lowered = '\n'.join(l for l in self.text.lower().splitlines() if not l.lstrip().startswith('#'))
        for banned in ('upload-artifact', 'actions/cache', 'download-artifact', 'set -x', 'get-childitem', 'type ', 'cat ', 'tree ', 'write-host', 'actions_step_debug', 'echo '):
            self.assertFalse(banned in lowered, banned)
        self.assertNotIn('ConvertTo-Json', self.text)

    def test_each_secret_appears_only_in_its_own_step(self):
        secrets = {'SOURCE_READ_TOKEN': ('preflight', 'publish'), 'SOURCE_PUBLISH_TOKEN': ('publish',), 'AGENT_AUTH_TOKEN': ('download',)}
        for secret, allowed in secrets.items():
            holders = [s for s in self.steps if 'secrets.' + secret in s]
            self.assertEqual(len(holders), len(allowed), secret)
            for s in holders:
                self.assertTrue(any('source-extract.py ' + mode in s for mode in allowed), secret)
        self.assertNotIn('github.token', self.text)
        self.assertNotIn('GITHUB_TOKEN', self.text)
        self.assertIn('${{ secrets.SOURCE_PUBLISH_TOKEN || secrets.SOURCE_READ_TOKEN }}', self.step('source-extract.py publish'))
        for needle in ('Test-HtkkSourceCandidateTrust.ps1 -CandidateDirectory', 'Export-HtkkSourcePayload.ps1', 'source-extract.py stage', 'source-extract.py outcome'):
            self.assertNotIn('secrets.', self.step(needle))

    def test_order_trust_before_export_before_stage_before_publish(self):
        order = [self.text.index(n) for n in ('Test-HtkkSourceTrustBoundary.ps1', 'source-extract.py preflight', 'source-extract.py download',
                                               'Test-HtkkSourceCandidateTrust.ps1 -CandidateDirectory', 'Export-HtkkSourcePayload.ps1 -CandidateDirectory',
                                               'source-extract.py stage', 'source-extract.py publish', 'source-extract.py outcome', 'SOURCE_WORKER_CLEANUP_UNCONFIRMED')]
        self.assertEqual(order, sorted(order))
        self.assertIn("if: steps.stage.outputs.bundle_ready == 'true'", self.step('source-extract.py publish'))
        self.assertIn("SOURCE_TRUST_NOT_VERIFIED", self.text)
        self.assertIn("SOURCE_EXPORT_NOT_VERIFIED", self.text)
        cleanup = self.step('SOURCE_WORKER_CLEANUP_UNCONFIRMED')
        self.assertIn('if: always()', cleanup)

    def test_tests_in_workflow_include_this_suite(self):
        self.assertIn('-p test_source*.py', self.text)


class ExporterContractTests(unittest.TestCase):
    def setUp(self):
        self.text = (ROOT / 'Export-HtkkSourcePayload.ps1').read_text(encoding='utf-8')
        self.code = '\n'.join(line for line in self.text.splitlines() if not line.lstrip().startswith('#'))

    def test_no_vendor_execution_paths(self):
        lowered = self.code.lower()
        for banned in ('msiexec', 'start-process', 'installproduct', 'configureproduct', 'doaction', 'invoke-expression', 'iex ', 'shell.application', 'rundll32', 'regsvr32', 'process]::start', '& $'):
            self.assertFalse(banned in lowered, banned)
        # The only external tool is the Microsoft-signed System32 tar.exe (data extraction).
        calls = [line for line in self.code.splitlines() if 'Invoke-ReadOnlyTool ' in line]
        self.assertEqual(len(calls), 1)
        self.assertIn('Invoke-ReadOnlyTool $tar @(', calls[0])
        self.assertIn('$installer.OpenDatabase($msi,0)', self.code)
        self.assertIn("[IO.Path]::Combine($env:SystemRoot,'System32','tar.exe')", self.code)
        self.assertIn('[HtkkSourceCabinet]::Extract($cab,$payload,$ids,$sizes)', self.code)

    def test_reuses_reviewed_helpers_and_pins(self):
        trust = (ROOT / 'Test-HtkkSourceCandidateTrust.ps1').read_text(encoding='utf-8')
        for name in ('Get-PrivateFileHash', 'Assert-PlainPath', 'Write-NewPrivateJson', 'Invoke-ReadOnlyTool', 'Assert-RunnerTool', 'Release-ComObject', 'Read-MsiRows'):
            self.assertIn("'" + name + "'", self.text)
            self.assertIn('function ' + name, trust)
        for pin in ('5d52c06595e933a3b246480785d5d4010fad669baed6fb38311f8a09b20e1e95', '7c1da251ee2acd126a2363e4457502b8ad6fc0792d78dc0a92b153701dc29080',
                    '19394e89351dc213306864168e16808d48401597f56d5fe4c977f9a5833d2936', '00669905937fb29e10cb53209ece5e8a9f8097970e4cb40bb28f89baa9fc3744'):
            self.assertIn(pin, self.text)
            self.assertIn(pin, trust)

    def test_requires_verified_trust_and_bounded_job_cleanup(self):
        self.assertIn("$trusted['status'] -cne 'baseline-verified'", self.code)
        self.assertIn('New-HtkkBoundedJobOwner', self.code)
        self.assertIn('$exited=$owner.WaitForRootExit($script:workerTimeoutMilliseconds)', self.code)
        self.assertEqual(self.code.count('WaitForRootExit('), 1)
        self.assertLess(self.code.index("throw 'TRUST_NOT_VERIFIED'"), self.code.index('New-HtkkBoundedJobOwner'))
        self.assertIn("childEnvironmentPolicy='os-essentials-only'", self.code)
        self.assertNotIn('Write-Output', self.code)
        self.assertNotIn('Write-Host', self.code)

    def parts(self):
        worker = self.code[self.code.index('function Invoke-ExportWorker'):self.code.index('\nif($Worker){')]
        controller = self.code[self.code.index('function Write-SafeExportLine'):]
        return worker, controller

    def array(self, name):
        m = re.search(r'\$script:' + name + r'=@\(([^)]*)\)', self.code)
        self.assertIsNotNone(m, name)
        return set(re.findall(r"'([^']+)'", m.group(1)))

    def test_every_failure_code_is_from_a_fixed_enum(self):
        worker, controller = self.parts()
        known, controller_known = self.array('known'), self.array('controllerKnown')
        for code in known | controller_known:
            self.assertRegex(code, r'^[A-Z0-9_]{1,48}$')
        self.assertLessEqual(set(re.findall(r"throw '([A-Z0-9_]+)'", worker)), known)
        self.assertLessEqual(set(re.findall(r"throw '([A-Z0-9_]+)'", controller)), controller_known)
        self.assertLessEqual(set(re.findall(r"\$step='([A-Z0-9_]+)'", controller)), controller_known)
        # Worker phases double as failure codes; the controller accepts exactly these.
        phases = set(re.findall(r"\$phase='([A-Z0-9_]+)'", worker))
        accepted = re.search(r"\$script:known\+@\(([^)]*)\)", controller)
        self.assertIsNotNone(accepted)
        self.assertLessEqual(phases, known | set(re.findall(r"'([^']+)'", accepted.group(1))))
        for name in ('ARCHIVE_EXTRACTION', 'MSI_OPEN', 'MSI_QUERY_FILE', 'CABINET_HELPER', 'CAB_EXTRACTION', 'LAYOUT_WRITE'):
            self.assertIn(name, phases)
        # Distinct pre-launch codes instead of one opaque WORKER_POLICY.
        for name in ('OUTPUT_PREEXISTS', 'TRUST_RESULT_MISSING', 'TRUST_NOT_VERIFIED', 'JOB_LAUNCH', 'WORKER_EXIT', 'WORKER_RESULT_MISSING', 'EXPORT_MOVE'):
            self.assertIn(name, controller_known)

    def test_exception_messages_never_reach_results_or_console(self):
        # Messages are only compared against enums; only type names (allowlisted) and HRESULT numbers are kept.
        for line in self.code.splitlines():
            if '.Message' in line:
                self.assertRegex(line, r'\.Message -cin \$|\.Message -cin \$script:|\.Message -cin \$cleanFailures')
        self.assertIn("errorType=$(if($name -cin $script:errorTypes){$name}else{'other'})", self.code)
        self.assertIn("errorHResult=('0x{0:X8}' -f $item.HResult)", self.code)
        lines = [l for l in self.code.splitlines() if '[Console]::WriteLine(' in l]
        self.assertEqual(len(lines), 2)
        self.assertIn("'Source payload export: blocked; code=HELPER_LOAD; stage=BOOTSTRAP; ready=false'", lines[0])
        self.assertIn("'Source payload export: '+$status+'; code='+$code+'; stage='+$stage", lines[1])
        start = self.code.index('function Write-SafeExportLine')
        line_writer = self.code[start:self.code.index('$result=New-SafeExportResult;$result.workerScriptSha256', start)]
        for check in ("-cmatch '^[A-Z0-9_]{1,48}$'", "-cmatch '^0x[0-9A-F]{8}$'", "-cin (@('other')+$script:errorTypes)", "-cin @('exported','blocked')"):
            self.assertIn(check, line_writer)
        # Blocked workers contribute only the four bounded diagnostic fields.
        self.assertIn("foreach($key in @('failureCode','stage','errorType','errorHResult')){$result[$key]=$child[$key]}", self.code)
        self.assertNotIn('$result=$child', self.code)

    def test_worker_bootstrap_failures_still_produce_a_coded_result(self):
        self.assertIn("Write-HtkkBootstrapFailure $ResultPath 'HELPER_LOAD'", self.code)
        self.assertIn("try{Invoke-ExportWorker}catch{Write-HtkkBootstrapFailure $ResultPath 'WORKER_UNHANDLED' 'WORKER';exit 4}", self.code)
        self.assertLess(self.code.index('function Write-HtkkBootstrapFailure'), self.code.index('ParseFile('))
        self.assertIn("if(-not [IO.File]::Exists($workerResult)){if($result.workerExitCode -ne 0)", self.code)

    def test_workflow_reports_bounded_codes(self):
        text = WORKFLOW.read_text(encoding='utf-8')
        self.assertIn("throw ('SOURCE_EXPORT_NOT_VERIFIED:'+$code+':'+$stage)", text)
        self.assertIn("throw ('SOURCE_TRUST_NOT_VERIFIED:'+$code)", text)
        self.assertEqual(text.count("-cmatch '^[A-Z0-9_]{1,48}$'"), 3)


class JobDeadlineTests(unittest.TestCase):
    """Run 42146199473: WaitForRootExit(420000) threw deadline-invalid and was misreported as a timeout."""

    def setUp(self):
        self.cs = (ROOT / 'HtkkWindowsJobProcess.cs').read_text(encoding='utf-8')
        text = (ROOT / 'Export-HtkkSourcePayload.ps1').read_text(encoding='utf-8')
        self.code = '\n'.join(l for l in text.splitlines() if not l.lstrip().startswith('#'))

    def test_worker_deadline_is_inside_the_job_api_range(self):
        limit = int(re.search(r'CheckDeadline\(int value\) \{ if \(value < 0 \|\| value > ([0-9]+)\)', self.cs).group(1))
        timeout = int(re.search(r'\$script:workerTimeoutMilliseconds=([0-9]+)', self.code).group(1))
        self.assertTrue(0 < timeout <= limit, (timeout, limit))
        for literal in re.findall(r'\.(?:WaitForRootExit|Stop)\(([0-9]+)\)', self.code):
            self.assertLessEqual(int(literal), limit)
        trust = (ROOT / 'Test-HtkkSourceCandidateTrust.ps1').read_text(encoding='utf-8')
        trust_wait = int(re.search(r'\$owner\.WaitForRootExit\(([0-9]+)\)', trust).group(1))
        self.assertLessEqual(trust_wait, limit)
        self.assertIn('workerTimeoutMilliseconds=$script:workerTimeoutMilliseconds', self.code)

    def test_wait_exceptions_are_not_timeouts(self):
        wait = self.code[self.code.index("$step='WORKER_WAIT_FAILED'"):self.code.index("if($result.workerTimedOut)")]
        self.assertIn("try{$exited=$owner.WaitForRootExit($script:workerTimeoutMilliseconds)}catch{", wait)
        self.assertIn("throw 'WORKER_WAIT_FAILED'", wait)
        self.assertIn("throw 'WORKER_EXIT_CODE_FAILED'", wait)
        self.assertIn('}else{$result.workerTimedOut=$true}', wait)
        # Timeout is only the false return of a successful wait.
        self.assertNotIn("WORKER_TIMEOUT", wait)
        self.assertIn("if($result.workerTimedOut){$step='WORKER_TIMEOUT';throw 'WORKER_TIMEOUT'}", self.code)
        # Original API exception details survive the rethrow.
        self.assertIn('if($null -eq $result.errorType){$info=Get-SafeErrorInfo $_.Exception', self.code)

    def test_job_categories_match_the_csharp_failures(self):
        categories = set(re.findall(r'Failure\("([a-z-]+)"\)', self.cs)) | {'boundary-tool-failure'}
        listed = set(re.findall(r"'([a-z-]+)'", re.search(r'\$script:jobCategories=@\(([^)]*)\)', self.code).group(1)))
        self.assertEqual(listed, categories)
        self.assertIn("[string]$item.Message -cin $script:jobCategories", self.code)
        self.assertIn("'; job='+$job+'", self.code)


class SafeFailureTests(unittest.TestCase):
    def test_only_enum_shaped_values_are_reported(self):
        with tempfile.TemporaryDirectory() as d:
            path = pathlib.Path(d) / 'export-result.json'
            self.assertEqual(x.safe_failure(path, 'export'), {'exportCode': 'ABSENT'})
            path.write_text(json.dumps({'status': 'blocked', 'failureCode': 'TRUST_NOT_VERIFIED', 'stage': 'NOT_STARTED', 'controllerStage': 'TRUST_NOT_VERIFIED', 'errorHResult': '0x80131500', 'path': 'C:/secret/file.xls'}))
            out = x.safe_failure(path, 'export')
            self.assertEqual(out, {'exportStatus': 'blocked', 'exportCode': 'TRUST_NOT_VERIFIED', 'exportStage': 'NOT_STARTED', 'exportControllerStage': 'TRUST_NOT_VERIFIED', 'exportErrorHResult': '0x80131500'})
            path.write_text(json.dumps({'status': 'blocked', 'failureCode': 'WORKER_WAIT_FAILED', 'jobErrorCategory': 'deadline-invalid'}))
            self.assertEqual(x.safe_failure(path, 'export')['exportJobErrorCategory'], 'deadline-invalid')
            path.write_text(json.dumps({'status': 'blocked', 'failureCode': 'WORKER_WAIT_FAILED', 'jobErrorCategory': 'C:/x y'}))
            self.assertEqual(x.safe_failure(path, 'export')['exportJobErrorCategory'], 'none')
            path.write_text(json.dumps({'status': 'oops', 'failureCode': 'C:\\payload\\x.dll', 'stage': 'Program Files/HTKK', 'errorHResult': 'message text'}))
            out = x.safe_failure(path, 'export')
            self.assertEqual(out, {'exportStatus': 'INVALID', 'exportCode': 'INVALID', 'exportStage': 'INVALID', 'exportErrorHResult': 'none'})
            path.write_text('not json')
            self.assertEqual(x.safe_failure(path, 'export'), {'exportCode': 'UNREADABLE'})

    def test_outcome_prints_codes_when_nothing_was_published(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.dict(os.environ, {'GITHUB_REPOSITORY': x.BUILDER, 'GITHUB_REF': 'refs/heads/main', 'RUNNER_TEMP': d}), mock.patch('sys.argv', ['x', 'outcome']):
            candidate = pathlib.Path(d) / 'htkk-source-candidate'
            candidate.mkdir()
            (candidate / 'trust.json').write_text(json.dumps({'status': 'baseline-verified', 'failureCode': None, 'verificationStage': 'MSI_CAB_PAYLOAD'}))
            (candidate / 'export-result.json').write_text(json.dumps({'status': 'blocked', 'failureCode': 'ARCHIVE_EXTRACTION', 'stage': 'ARCHIVE_EXTRACTION'}))
            with mock.patch('builtins.print') as printed:
                self.assertEqual(x.main(), 1)
            out = json.loads(printed.call_args[0][0])
            self.assertEqual((out['result'], out['trustCode'], out['exportCode'], out['exportStage']), ('not-published', 'NONE', 'ARCHIVE_EXTRACTION', 'ARCHIVE_EXTRACTION'))


if __name__ == '__main__':
    unittest.main()
