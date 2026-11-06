"""Private HTKK 5.8.1 source snapshot for logic extraction (W1-D).

Separate processes per workflow step:
  preflight  SOURCE_READ_TOKEN only: fixed private target must be reachable/private.
  download   no source credential; optional AGENT_AUTH_TOKEN relay, same pinned archive.
  (Windows)  Test-HtkkSourceCandidateTrust.ps1 then Export-HtkkSourcePayload.ps1.
  stage      no credential: cross-check two independent CAB extractions, resolve MSI
             install paths, select the priority/full scope, write manifest.
  publish    SOURCE_PUBLISH_TOKEN only: push one snapshot commit to the fixed
             PRIVATE branch htkk-source-5.8.1 of htkk-net/htkk_web.
  outcome    no credential: fixed summary text.
Public output contains fixed codes and counts only: never file names, contents,
headers, URLs with tokens or raw exceptions. Vendor code is never executed.
"""
import argparse, base64, hashlib, importlib.util, json, os, pathlib, re, shutil, subprocess, time, urllib.error

ROOT = pathlib.Path(__file__).resolve().parent
REPO = 'htkk-net/htkk_web'
BUILDER = 'congminh1254/htkk_builder'
BRANCH = 'htkk-source-5.8.1'
TAG_PREFIX = 'htkk-source-5.8.1/run-'
PUSH_URL = 'https://github.com/' + REPO + '.git'
OFFICIAL_URL = 'https://www.fshare.vn/file/TPW3FMLVAJL1'
POLICY = ROOT / 'htkk-source-extract-policy.json'
FILE_COUNT = 4526
HASHED_COUNT = 4493
UNHASHED_VERSIONED_COUNT = 33
MAX_FILE = 95 * 1024 * 1024
MAX_TOTAL = 1536 * 1024 * 1024
CHUNK = 4 * 1024 * 1024
BUNDLE_TOP = frozenset(('.gitattributes', 'README.md', 'SHA256SUMS', 'catalog.json', 'manifest.json', 'msi', 'payload'))
# Fixed mapping of Windows Installer standard folders; never resolved from the host.
STANDARD_FOLDERS = {
    'TARGETDIR': '', 'ProgramFilesFolder': 'Program Files', 'ProgramFiles64Folder': 'Program Files',
    'CommonFilesFolder': 'Program Files/Common Files', 'CommonFiles64Folder': 'Program Files/Common Files',
    'WindowsFolder': 'Windows', 'SystemFolder': 'Windows/System32', 'System64Folder': 'Windows/System32',
    'System16Folder': 'Windows/System', 'FontsFolder': 'Windows/Fonts', 'DesktopFolder': '_shell/Desktop',
    'ProgramMenuFolder': '_shell/ProgramMenu', 'StartMenuFolder': '_shell/StartMenu', 'StartupFolder': '_shell/Startup',
    'AppDataFolder': '_shell/AppData', 'LocalAppDataFolder': '_shell/LocalAppData', 'CommonAppDataFolder': '_shell/CommonAppData',
    'PersonalFolder': '_shell/Personal', 'TempFolder': '_shell/Temp', 'SendToFolder': '_shell/SendTo',
    'TemplateFolder': '_shell/Templates', 'FavoritesFolder': '_shell/Favorites', 'NetHoodFolder': '_shell/NetHood',
    'PrintHoodFolder': '_shell/PrintHood', 'RecentFolder': '_shell/Recent', 'AdminToolsFolder': '_shell/AdminTools',
    'MyPicturesFolder': '_shell/MyPictures',
}
SAFE_COMPONENT = re.compile(r'[^\x00-\x1f<>:"/\\|?*]{1,200}')
WINDOWS_RESERVED = re.compile(r'(?i)(con|prn|aux|nul|com[0-9]|lpt[0-9])(\..*)?')


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / file)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


update = module('source_extract_update', 'source-update.py')
candidate = update.candidate
watch = update.watch
require = update.require


class ExtractError(ValueError):
    pass


def fail(code):
    raise ExtractError(code)


def check(test, code):
    if not test:
        fail(code)


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as stream:
        while block := stream.read(CHUNK):
            digest.update(block)
    return digest.hexdigest()


def plain_dir(path, exists=True):
    p = pathlib.Path(path).absolute()
    for q in (p, *p.parents):
        check(not q.is_symlink() and not getattr(q, 'is_junction', lambda: False)(), 'PATH_POLICY')
    if exists:
        check(p.is_dir(), 'PATH_POLICY')
    return p


def paths():
    base = pathlib.Path(os.environ['RUNNER_TEMP']).absolute()
    return {
        'candidate': base / 'htkk-source-candidate',
        'export': base / 'htkk-source-candidate' / 'export',
        'exportResult': base / 'htkk-source-candidate' / 'export-result.json',
        'bundle': base / 'htkk-source-extract-bundle',
        'git': base / 'htkk-source-extract-git',
        'publishResult': base / 'htkk-source-extract-publish.json',
    }


def output(name, value):
    check(re.fullmatch('[a-z_]+', name) and re.fullmatch('[a-z0-9-]+', value), 'OUTPUT_POLICY')
    with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf8') as stream:
        stream.write(name + '=' + value + '\n')


# ---------------------------------------------------------------- policy

def load_policy(path=POLICY):
    data = pathlib.Path(path).read_bytes()
    policy = json.loads(data)
    check(type(policy) is dict and policy.get('format') == 'htkk-source-extract-policy-v1' and policy.get('version') == '5.8.1', 'POLICY_FORMAT')
    check(policy['msiSha256'] == '7c1da251ee2acd126a2363e4457502b8ad6fc0792d78dc0a92b153701dc29080', 'POLICY_PIN')
    check(policy.get('scopes') == ['priority', 'full'], 'POLICY_FORMAT')
    pins = policy.get('pins')
    check(type(pins) is list and 1 <= len(pins) <= FILE_COUNT, 'POLICY_FORMAT')
    seen_path, seen_id = set(), set()
    for entry in pins:
        check(type(entry) is dict and set(entry) == {'path', 'sha256', 'msiFileId'}, 'POLICY_FORMAT')
        check(safe_relative(entry['path']) and re.fullmatch('[a-f0-9]{64}', entry['sha256']) and re.fullmatch(r'[A-Za-z0-9_.]{1,72}', entry['msiFileId']), 'POLICY_FORMAT')
        check(entry['path'].lower() not in seen_path and entry['msiFileId'].lower() not in seen_id, 'POLICY_DUPLICATE')
        seen_path.add(entry['path'].lower())
        seen_id.add(entry['msiFileId'].lower())
    pinned = {e['path'] for e in pins}
    forms = policy.get('forms')
    check(type(forms) is list and 1 <= len(forms) <= 64, 'POLICY_FORMAT')
    ids = set()
    for form in forms:
        check(type(form) is dict and re.fullmatch('[a-z0-9-]{2,40}', form.get('id', '')) and form['id'] not in ids, 'POLICY_FORMAT')
        ids.add(form['id'])
        check(type(form.get('menuIds')) is list and form['menuIds'] and all(re.fullmatch('[A-Z0-9_]{1,8}', m) for m in form['menuIds']), 'POLICY_FORMAT')
        check(type(form.get('paths')) is list and set(form['paths']) <= pinned, 'POLICY_FORM_UNPINNED')
    for key in ('sharedDirectories', 'sharedExcludes', 'assemblyDirectories'):
        check(type(policy.get(key)) is list and all(safe_relative(p) for p in policy[key]), 'POLICY_FORMAT')
    check(type(policy.get('assemblyExtensions')) is list and all(re.fullmatch(r'\.[a-z0-9]{1,8}', e) for e in policy['assemblyExtensions']), 'POLICY_FORMAT')
    root = policy.get('installRoot')
    check(type(root) is dict and root.get('markerPath') in pinned and any(e['msiFileId'] == root.get('markerMsiFileId') and e['path'] == root['markerPath'] for e in pins), 'POLICY_ROOT')
    policy['_sha256'] = hashlib.sha256(data).hexdigest()
    return policy


def safe_relative(path):
    if not isinstance(path, str) or not 1 <= len(path) <= 400 or path.startswith('/') or path.endswith('/'):
        return False
    return all(safe_component(part) for part in path.split('/'))


def safe_component(part):
    return bool(SAFE_COMPONENT.fullmatch(part)) and part not in ('.', '..') and not part.endswith((' ', '.')) and not WINDOWS_RESERVED.fullmatch(part)


# ---------------------------------------------------------------- MSI layout

def long_name(value):
    # MSI Filename/DefaultDir: "short|long"; the long name is installed when present.
    check(isinstance(value, str) and 1 <= len(value) <= 520, 'MSI_LAYOUT')
    parts = value.split('|')
    check(len(parts) in (1, 2) and all(parts), 'MSI_LAYOUT')
    return parts[-1]


def resolve_directories(rows):
    check(type(rows) is list and 1 <= len(rows) <= 10000, 'MSI_LAYOUT')
    table = {}
    for row in rows:
        check(type(row) is dict and set(row) == {'id', 'parent', 'defaultDir'}, 'MSI_LAYOUT')
        check(re.fullmatch(r'[A-Za-z_][A-Za-z0-9_.]{0,71}', row['id']) and row['id'] not in table, 'MSI_LAYOUT')
        table[row['id']] = row
    resolved = {}

    def walk(identity, depth=0):
        check(depth < 64 and identity in table, 'MSI_LAYOUT')
        if identity in resolved:
            return resolved[identity]
        row = table[identity]
        if identity in STANDARD_FOLDERS:
            value = STANDARD_FOLDERS[identity]
        elif not row['parent'] or row['parent'] == identity:
            value = '_root/' + identity
        else:
            target = row['defaultDir'].split(':')[0]
            name = long_name(target)
            parent = walk(row['parent'], depth + 1)
            if name == '.':
                value = parent
            else:
                check(safe_component(name), 'MSI_UNSAFE_NAME')
                value = parent + '/' + name if parent else name
        resolved[identity] = value
        return value

    for identity in table:
        walk(identity)
    return resolved


def resolve_layout(layout):
    """Return File-table rows with their MSI target paths, in payload index order."""
    check(type(layout) is dict and layout.get('format') == 'htkk-msi-layout-tables-v1' and layout.get('version') == '5.8.1', 'MSI_LAYOUT')
    check(layout.get('ready') is False and layout.get('automaticActivation') is False, 'MSI_LAYOUT')
    directories = resolve_directories(layout.get('directories'))
    components = {}
    check(type(layout.get('components')) is list and 1 <= len(layout['components']) <= 10000, 'MSI_LAYOUT')
    for row in layout['components']:
        check(type(row) is dict and set(row) == {'id', 'directory'} and row['id'] not in components and row['directory'] in directories, 'MSI_LAYOUT')
        components[row['id']] = row['directory']
    hashes = {}
    check(type(layout.get('fileHashes')) is list, 'MSI_LAYOUT')
    for row in layout['fileHashes']:
        check(type(row) is dict and set(row) == {'id', 'options', 'md5'} and row['options'] == 0 and re.fullmatch('[a-f0-9]{32}', row['md5']) and row['id'].lower() not in hashes, 'MSI_LAYOUT')
        hashes[row['id'].lower()] = row['md5']
    files = layout.get('files')
    check(type(files) is list and len(files) == FILE_COUNT, 'MSI_FILE_COUNTS')
    result, ids = [], set()
    for index, row in enumerate(files):
        check(type(row) is dict and set(row) == {'id', 'component', 'fileName', 'bytes', 'version', 'sequence'}, 'MSI_LAYOUT')
        check(re.fullmatch(r'[A-Za-z0-9_.]{1,72}', row['id']) and row['id'].lower() not in ids, 'MSI_FILE_IDENTITIES')
        ids.add(row['id'].lower())
        check(row['component'] in components and type(row['bytes']) is int and 0 <= row['bytes'] <= 268435456, 'MSI_LAYOUT')
        name = long_name(row['fileName'])
        check(safe_component(name), 'MSI_UNSAFE_NAME')
        directory = directories[components[row['component']]]
        result.append({'index': index, 'fileId': row['id'], 'msiPath': (directory + '/' + name) if directory else name,
                       'bytes': row['bytes'], 'versioned': bool(row['version'] and row['version'].strip()),
                       'md5InSignedMsi': hashes.get(row['id'].lower())})
    check(set(hashes) <= ids, 'MSI_HASH_IDENTITIES')
    return result


def assign_install_paths(entries, policy):
    """Map MSI target paths to installation-root relative paths and resolve collisions."""
    marker = policy['installRoot']
    found = [e for e in entries if e['fileId'] == marker['markerMsiFileId']]
    check(len(found) == 1 and found[0]['msiPath'].endswith('/' + marker['markerPath']), 'INSTALL_ROOT')
    root = found[0]['msiPath'][:-len(marker['markerPath'])]
    for e in entries:
        e['path'] = e['msiPath'][len(root):] if e['msiPath'].startswith(root) else '_outside/' + e['msiPath']
        check(safe_relative(e['path']), 'MSI_UNSAFE_NAME')
    groups = {}
    for e in entries:
        groups.setdefault(e['path'].lower(), []).append(e)
    conflicts = []
    for key in sorted(groups):
        group = groups[key]
        if len(group) == 1:
            continue
        group.sort(key=lambda x: x['fileId'])
        if len({g['sha256'] for g in group}) == 1:
            for duplicate in group[1:]:
                duplicate['duplicateOf'] = group[0]['fileId']
            conflicts.append({'path': group[0]['path'], 'fileIds': [g['fileId'] for g in group], 'resolution': 'identical-bytes-first-file-id-kept'})
        else:
            for member in group:
                member['path'] = '_conflicts/' + member['fileId'] + '/' + member['path'].rsplit('/', 1)[-1]
            conflicts.append({'path': group[0]['msiPath'], 'fileIds': [g['fileId'] for g in group], 'resolution': 'different-bytes-moved-to-_conflicts'})
    # Directory and file names may not differ only by case (Windows staging).
    names = {}
    for e in entries:
        if 'duplicateOf' in e:
            continue
        parts = e['path'].split('/')
        for depth in range(1, len(parts) + 1):
            prefix = '/'.join(parts[:depth])
            check(names.setdefault(prefix.lower(), prefix) == prefix, 'PATH_CASE_COLLISION')
    return root, conflicts


def verify_pins(entries, policy):
    by_id = {e['fileId'].lower(): e for e in entries}
    for pin in policy['pins']:
        e = by_id.get(pin['msiFileId'].lower())
        check(e is not None, 'PIN_MISSING')
        check(e['path'] == pin['path'], 'PIN_PATH_MISMATCH')
        check(e['sha256'] == pin['sha256'], 'PIN_HASH_MISMATCH')
        check('duplicateOf' not in e, 'PIN_PATH_MISMATCH')


def select(entries, policy, scope):
    check(scope in ('priority', 'full'), 'SCOPE_POLICY')
    pinned = {p['path'] for p in policy['pins']}
    forms = {}
    for form in policy['forms']:
        for path in form['paths']:
            forms.setdefault(path, []).append(form['id'])
    shared = tuple(d + '/' for d in policy['sharedDirectories'])
    excluded = tuple(d + '/' for d in policy['sharedExcludes'])
    assemblies = tuple(d + '/' for d in policy['assemblyDirectories'])
    extensions = tuple(policy['assemblyExtensions'])
    chosen = []
    for e in entries:
        if 'duplicateOf' in e:
            continue
        path = e['path']
        inside = not path.startswith(('_outside/', '_conflicts/'))
        categories = []
        if path in forms:
            categories.append('form')
        if path in pinned:
            categories.append('pinned')
        if inside and path.startswith(shared) and not path.startswith(excluded):
            categories.append('shared')
        if inside and (path.startswith(assemblies) or path.lower().endswith(extensions)):
            categories.append('assembly')
        if scope == 'full' and not categories:
            categories.append('full-scope')
        if categories:
            e['categories'] = categories
            e['forms'] = sorted(forms.get(path, []))
            chosen.append(e)
    chosen.sort(key=lambda x: x['path'])
    return chosen


# ---------------------------------------------------------------- stage

def load_trust_manifest(directory):
    manifest = update.load(pathlib.Path(directory) / 'payload-sha256.json', 4 * 1024 * 1024)
    check(manifest.get('format') == 'htkk-reviewed-source-payload-sha256-v1' and manifest.get('version') == '5.8.1', 'TRUST_MANIFEST')
    check(manifest.get('ready') is False and manifest.get('automaticActivation') is False, 'TRUST_MANIFEST')
    files = manifest.get('files')
    check(type(files) is list and len(files) == FILE_COUNT, 'TRUST_MANIFEST')
    result = {}
    for row in files:
        check(type(row) is dict and re.fullmatch('[a-f0-9]{64}', row.get('sha256', '')) and type(row.get('bytes')) is int and row.get('fileId', '').lower() not in result, 'TRUST_MANIFEST')
        result[row['fileId'].lower()] = row
    return result


def validate_export_result(result):
    check(type(result) is dict and result.get('format') == 'htkk-source-payload-export-v1' and result.get('status') == 'exported' and result.get('failureCode') is None, 'EXPORT_NOT_VERIFIED')
    for key in ('ready', 'automaticActivation', 'vendorCodeExecuted', 'installerExecuted', 'msiCustomActionsExecuted', 'workerTimedOut'):
        check(result.get(key) is False, 'EXPORT_NOT_VERIFIED')
    check(result.get('workerStopped') is True and result.get('jobCleanupVerified') is True and result.get('workerExitCode') == 0, 'EXPORT_NOT_VERIFIED')
    check((result.get('files'), result.get('sizeMatches'), result.get('msiHashMatches'), result.get('versionedWithoutMsiHash')) == (FILE_COUNT, FILE_COUNT, HASHED_COUNT, UNHASHED_VERSIONED_COUNT), 'EXPORT_NOT_VERIFIED')
    check(result.get('workerScriptSha256') == hashlib.sha256((ROOT / 'Export-HtkkSourcePayload.ps1').read_bytes()).hexdigest(), 'EXPORT_NOT_VERIFIED')
    check(result.get('cabinetHelperSha256') == hashlib.sha256((ROOT / 'HtkkSourceCabinet.cs').read_bytes()).hexdigest(), 'EXPORT_NOT_VERIFIED')


def build_bundle(candidate_dir, export_dir, export_result, bundle, scope, policy, trust_validator=None):
    candidate_dir = plain_dir(candidate_dir)
    export_dir = plain_dir(export_dir)
    bundle = pathlib.Path(bundle).absolute()
    check(not bundle.exists() and not bundle.is_symlink(), 'OUTPUT_PREEXISTS')
    trust = update.load(candidate_dir / 'trust.json', 64000)
    if trust_validator is None:
        trust_validator = update.validate_trust
    check(trust.get('status') == 'baseline-verified' and trust_validator(trust, candidate_dir) is True, 'TRUST_NOT_VERIFIED')
    validate_export_result(update.load(export_result, 16384))
    layout_path = export_dir / 'layout.json'
    layout = update.load(layout_path, 16 * 1024 * 1024)
    entries = resolve_layout(layout)
    payload = plain_dir(export_dir / 'payload')
    names = sorted(p.name for p in payload.iterdir())
    check(names == ['%05d.bin' % i for i in range(FILE_COUNT)], 'PAYLOAD_NAMES')
    trusted = load_trust_manifest(candidate_dir)
    for e in entries:
        source = payload / ('%05d.bin' % e['index'])
        check(source.is_file() and not source.is_symlink() and source.stat().st_size == e['bytes'], 'PAYLOAD_SIZE')
        e['sha256'] = sha256_file(source)
        reference = trusted.get(e['fileId'].lower())
        # Two independent CAB extractions (trust verifier and exporter) must agree.
        check(reference is not None and reference['sha256'] == e['sha256'] and reference['bytes'] == e['bytes'], 'TRUST_PAYLOAD_MISMATCH')
        e['msiMd5Verified'] = reference.get('msiHashVerified') is True
    root, conflicts = assign_install_paths(entries, policy)
    verify_pins(entries, policy)
    chosen = select(entries, policy, scope)
    total = 0
    for e in chosen:
        check(e['bytes'] <= MAX_FILE, 'FILE_TOO_LARGE')
        total += e['bytes']
    check(total <= MAX_TOTAL, 'BUNDLE_TOO_LARGE')
    bundle.mkdir()
    (bundle / 'msi').mkdir()
    (bundle / 'payload').mkdir()
    for e in chosen:
        target = bundle / 'payload' / pathlib.PurePosixPath(e['path'])
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(payload / ('%05d.bin' % e['index']), 'rb') as src, open(target, 'xb') as dst:
            shutil.copyfileobj(src, dst, CHUNK)
        check(sha256_file(target) == e['sha256'], 'SOURCE_CHANGED')
    shutil.copyfile(layout_path, bundle / 'msi' / 'layout.json')
    files = [{'path': e['path'], 'bytes': e['bytes'], 'sha256': e['sha256'], 'msiFileId': e['fileId'],
              'md5InSignedMsi': e['md5InSignedMsi'], 'msiMd5Verified': e['msiMd5Verified'], 'versioned': e['versioned'],
              'categories': e['categories'], 'forms': e['forms']} for e in chosen]
    included = {e['fileId'] for e in chosen}
    catalog = {'format': 'htkk-source-catalog-v1', 'version': '5.8.1', 'installRoot': root.rstrip('/'),
               'files': [{'path': e['path'], 'msiPath': e['msiPath'], 'msiFileId': e['fileId'], 'bytes': e['bytes'], 'sha256': e['sha256'],
                          'msiMd5Verified': e['msiMd5Verified'], 'versioned': e['versioned'], 'included': e['fileId'] in included,
                          **({'duplicateOf': e['duplicateOf']} if 'duplicateOf' in e else {})} for e in sorted(entries, key=lambda x: x['path'])]}
    forms = []
    present = {e['path'] for e in chosen}
    for form in policy['forms']:
        forms.append({'id': form['id'], 'title': form.get('title', ''), 'menuIds': form['menuIds'], 'paths': [p for p in form['paths'] if p in present]})
    manifest = {
        'format': 'htkk-source-extract-manifest-v1', 'version': '5.8.1', 'scope': scope,
        'branch': BRANCH, 'repository': REPO, 'policySha256': policy['_sha256'],
        'sourcePins': trust['sourcePins'], 'trust': {'status': trust['status'], 'checks': trust['checks'], 'payload': trust['payload']},
        'installRoot': root.rstrip('/'), 'payloadRoot': 'payload', 'referenceLayout': 'payload/<path> == <installRoot>/<path>',
        'counts': {'msiFiles': FILE_COUNT, 'included': len(files), 'includedBytes': total, 'pins': len(policy['pins']),
                   'forms': len(forms), 'conflicts': len(conflicts)},
        'conflicts': conflicts, 'forms': forms, 'files': files,
        'catalogSha256': None, 'layoutSha256': sha256_file(bundle / 'msi' / 'layout.json'),
        'vendorCodeExecuted': False, 'installerExecuted': False, 'msiCustomActionsExecuted': False,
        'ready': False, 'automaticActivation': False,
    }
    catalog_bytes = (json.dumps(catalog, ensure_ascii=False, indent=1) + '\n').encode('utf-8')
    (bundle / 'catalog.json').write_bytes(catalog_bytes)
    manifest['catalogSha256'] = hashlib.sha256(catalog_bytes).hexdigest()
    (bundle / 'manifest.json').write_bytes((json.dumps(manifest, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    (bundle / 'SHA256SUMS').write_bytes(''.join(f"{f['sha256']}  payload/{f['path']}\n" for f in files).encode('utf-8'))
    (bundle / '.gitattributes').write_bytes(b'* -text -diff -merge\n')
    (bundle / 'README.md').write_bytes(README.encode('utf-8'))
    validate_bundle(bundle)
    return manifest


README = """# HTKK 5.8.1 source snapshot (PRIVATE)

Nhánh này do workflow `source-extract.yml` của builder công khai tạo ra từ bộ cài
HTKK 5.8.1 đã ghim hash và xác minh chữ ký. Không chạy installer, setup.exe,
msiexec hay custom action nào. Không phải mã nguồn ứng dụng, không kích hoạt adapter.

- `payload/<path>`: tệp gốc, đường dẫn tương đối gốc cài đặt (Program Files/HTKK).
- `manifest.json`: SHA-256, MSI file ID, biểu mẫu ưu tiên, danh mục từng tệp.
- `SHA256SUMS`: kiểm bằng `sha256sum -c SHA256SUMS`.
- `catalog.json`: toàn bộ 4526 tệp của MSI (kể cả tệp không đưa vào snapshot).
- `msi/layout.json`: bảng File/Component/Directory/MsiFileHash đọc read-only.

Hướng dẫn dùng: docs/TRICH-XUAT-NGUON.md trên main. Không công khai các tệp này.
"""


def validate_bundle(bundle):
    bundle = plain_dir(bundle)
    check({p.name for p in bundle.iterdir()} == BUNDLE_TOP, 'BUNDLE_LAYOUT')
    manifest = update.load(bundle / 'manifest.json', 64 * 1024 * 1024)
    check(manifest.get('format') == 'htkk-source-extract-manifest-v1' and manifest.get('ready') is False and manifest.get('automaticActivation') is False, 'BUNDLE_MANIFEST')
    check(manifest.get('branch') == BRANCH and manifest.get('repository') == REPO and manifest.get('scope') in ('priority', 'full'), 'BUNDLE_MANIFEST')
    check(sha256_file(bundle / 'catalog.json') == manifest['catalogSha256'] and sha256_file(bundle / 'msi' / 'layout.json') == manifest['layoutSha256'], 'BUNDLE_MANIFEST')
    check({p.name for p in (bundle / 'msi').iterdir()} == {'layout.json'}, 'BUNDLE_LAYOUT')
    expected = {}
    for f in manifest['files']:
        check(safe_relative(f['path']) and f['path'].lower() not in expected, 'BUNDLE_MANIFEST')
        expected[f['path'].lower()] = f
    actual = set()
    total = 0
    for item in sorted((bundle / 'payload').rglob('*')):
        check(not item.is_symlink(), 'BUNDLE_LAYOUT')
        if item.is_dir():
            continue
        rel = item.relative_to(bundle / 'payload').as_posix()
        f = expected.get(rel.lower())
        check(f is not None and f['path'] == rel and item.stat().st_size == f['bytes'] and sha256_file(item) == f['sha256'], 'BUNDLE_HASH')
        actual.add(rel.lower())
        total += f['bytes']
    check(actual == set(expected) and total == manifest['counts']['includedBytes'] and len(actual) == manifest['counts']['included'], 'BUNDLE_HASH')
    sums = ''.join(f"{f['sha256']}  payload/{f['path']}\n" for f in manifest['files'])
    check((bundle / 'SHA256SUMS').read_bytes() == sums.encode('utf-8'), 'BUNDLE_HASH')
    return manifest


# ---------------------------------------------------------------- publish

def git_environment(base, token=None):
    """Small explicit allowlist; credentials only as an env-scoped HTTP header."""
    home = pathlib.Path(base) / 'home'
    home.mkdir(parents=True, exist_ok=True)
    empty = home / 'empty.gitconfig'
    if not empty.exists():
        empty.write_bytes(b'')
    env = {k: os.environ[k] for k in ('PATH', 'SystemRoot', 'WINDIR', 'SystemDrive', 'TEMP', 'TMP', 'COMSPEC', 'PATHEXT') if k in os.environ}
    env.update({'HOME': str(home), 'USERPROFILE': str(home), 'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': str(empty),
                'GIT_TERMINAL_PROMPT': '0', 'GCM_INTERACTIVE': 'never', 'GIT_ASKPASS': '', 'SSH_ASKPASS': '',
                'GIT_AUTHOR_NAME': 'htkk-source-extract', 'GIT_AUTHOR_EMAIL': 'htkk-source-extract@users.noreply.github.com',
                'GIT_COMMITTER_NAME': 'htkk-source-extract', 'GIT_COMMITTER_EMAIL': 'htkk-source-extract@users.noreply.github.com'})
    config = [('core.autocrlf', 'false'), ('core.safecrlf', 'false'), ('core.longpaths', 'true'), ('core.quotepath', 'false'),
              ('credential.helper', ''), ('http.postBuffer', '524288000'), ('gc.auto', '0')]
    if token is not None:
        check(isinstance(token, str) and re.fullmatch(r'[A-Za-z0-9_\-]{20,255}', token), 'PUBLISH_TOKEN')
        header = base64.b64encode(('x-access-token:' + token).encode()).decode()
        config.append(('http.https://github.com/.extraheader', 'AUTHORIZATION: basic ' + header))
    env['GIT_CONFIG_COUNT'] = str(len(config))
    for i, (key, value) in enumerate(config):
        env['GIT_CONFIG_KEY_%d' % i] = key
        env['GIT_CONFIG_VALUE_%d' % i] = value
    return env


def run_git(git, args, env, cwd, code, capture=False, timeout=600):
    # Output is never forwarded to the public log; only the exit status is used.
    completed = subprocess.run([git] + args, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                               stdout=subprocess.PIPE if capture else subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL, timeout=timeout, check=False)
    check(completed.returncode == 0, code)
    return completed.stdout.decode('ascii', 'replace').strip() if capture else None


def remote_state(token, fetch=None):
    fetch = fetch or watch.api
    info = fetch('', token)
    check(info.get('private') is True and info.get('full_name') == REPO, 'TARGET_NOT_PRIVATE')
    try:
        ref = fetch('/git/ref/heads/' + BRANCH, token)
    except urllib.error.HTTPError as error:
        if error.code != 404:
            raise
        return None, None
    check(ref.get('ref') == 'refs/heads/' + BRANCH and ref.get('object', {}).get('type') == 'commit', 'TARGET_REF')
    commit = update.gitsha(ref['object']['sha'])
    tree = update.gitsha(fetch('/git/commits/' + commit, token)['tree']['sha'])
    return commit, tree


def publish(bundle, workdir, token, run_id, attempt, builder_sha, fetch=None, git=None, dry_run=False):
    manifest = validate_bundle(bundle)
    check(re.fullmatch('[1-9][0-9]{0,19}', run_id) and type(attempt) is int and 1 <= attempt <= 100, 'RUN_IDENTITY')
    update.gitsha(builder_sha)
    git = git or shutil.which('git')
    check(git is not None, 'GIT_MISSING')
    workdir = pathlib.Path(workdir).absolute()
    check(not workdir.exists(), 'OUTPUT_PREEXISTS')
    workdir.mkdir()
    gitdir = workdir / 'repo.git'
    env = git_environment(workdir)
    base = ['--git-dir', str(gitdir), '--work-tree', str(pathlib.Path(bundle).absolute())]
    run_git(git, base + ['init', '--quiet'], env, workdir, 'GIT_INIT')
    run_git(git, base + ['add', '--all', '--force', '.'], env, bundle, 'GIT_ADD')
    tree = update.gitsha(run_git(git, base + ['write-tree'], env, bundle, 'GIT_WRITE_TREE', capture=True))
    old_commit, old_tree = remote_state(token, fetch)
    summary = {'format': 'htkk-source-extract-publish-v1', 'branch': BRANCH, 'scope': manifest['scope'], 'included': manifest['counts']['included'],
               'includedBytes': manifest['counts']['includedBytes'], 'tree': tree, 'previousCommit': old_commit, 'ready': False}
    if old_tree == tree:
        summary.update(result='unchanged', commit=old_commit)
        return summary
    message = ('Private HTKK 5.8.1 source snapshot (scope=%s); never activate\n\nbuilder=%s run=%s/%d manifest=%s\n'
               % (manifest['scope'], builder_sha, run_id, attempt, sha256_file(pathlib.Path(bundle) / 'manifest.json')))
    message_file = workdir / 'message.txt'
    message_file.write_bytes(message.encode('utf-8'))
    commit = update.gitsha(run_git(git, base + ['commit-tree', tree, '-F', str(message_file)], env, bundle, 'GIT_COMMIT', capture=True))
    summary.update(commit=commit)
    if dry_run:
        summary.update(result='dry-run')
        return summary
    check(remote_state(token, fetch) == (old_commit, old_tree), 'TARGET_MOVED')
    # New branch: plain (non-force) creation. Existing branch: replace only the
    # exact commit observed above; older snapshots stay reachable through tags.
    lease = ['--force-with-lease=refs/heads/%s:%s' % (BRANCH, old_commit)] if old_commit else []
    push_env = git_environment(workdir, token)
    run_git(git, ['--git-dir', str(gitdir), 'push', '--quiet', '--no-verify'] + lease + [PUSH_URL,
                  commit + ':refs/heads/' + BRANCH, commit + ':refs/tags/' + TAG_PREFIX + run_id + '-' + str(attempt)],
            push_env, workdir, 'GIT_PUSH', timeout=1800)
    for delay in (0, 2, 5, 10):
        time.sleep(delay)  # the REST ref view can trail a successful push briefly
        new_commit, new_tree = remote_state(token, fetch)
        if (new_commit, new_tree) == (commit, tree):
            break
    check(new_commit == commit and new_tree == tree, 'PUSH_NOT_OBSERVED')
    summary.update(result='published')
    return summary


# ---------------------------------------------------------------- entry points

def download(target_dir, transport, relay_token=None, fetcher=None):
    fetcher = fetcher or candidate.fetch_resource
    target_dir = pathlib.Path(target_dir).absolute()
    check(not target_dir.exists() and not target_dir.is_symlink(), 'OUTPUT_PREEXISTS')
    check(transport in ('auto', 'direct', 'relay'), 'TRANSPORT_POLICY')
    check(transport != 'relay' or relay_token, 'RELAY_TOKEN_MISSING')
    target_dir.mkdir()
    failures = []
    official = None
    try:
        if transport == 'relay':
            official = fetcher(OFFICIAL_URL, target_dir / 'official.rar', candidate.BASELINE_OFFICIAL_SHA256, relay_token=relay_token, transport='relay')
        else:
            try:
                official = fetcher(OFFICIAL_URL, target_dir / 'official.rar', candidate.BASELINE_OFFICIAL_SHA256, max_attempts=2 if transport == 'direct' else 1)
            except candidate.CandidateError as error:
                failures.append({'code': error.code, 'status': error.status})
                if transport == 'direct' or not error.retryable or not relay_token:
                    raise
                official = fetcher(OFFICIAL_URL, target_dir / 'official.rar', candidate.BASELINE_OFFICIAL_SHA256, relay_token=relay_token, transport='relay', max_attempts=1)
    except candidate.CandidateError as error:
        return {'status': 'blocked', 'failureCode': error.code, 'httpStatus': error.status, 'transportFailures': failures, 'ready': False}
    check(official['sha256'] == candidate.BASELINE_OFFICIAL_SHA256 and official['expectedHashMatched'] is True, 'ARCHIVE_PIN_MISMATCH')
    report = {'format': 'htkk-pinned-source-reverification-v1', 'scope': 'pinned-baseline-for-private-source-extract', 'official': official,
              'mirror': None, 'transportFailures': failures, 'ready': False, 'automaticActivation': False}
    (target_dir / 'downloads.json').write_text(json.dumps(report) + '\n')
    return {'status': 'downloaded-pinned-baseline', 'officialSha256': official['sha256'], 'transport': official['transport'], 'ready': False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=('preflight', 'download', 'stage', 'publish', 'outcome'))
    args = parser.parse_args()
    check(os.environ.get('GITHUB_REPOSITORY') == BUILDER and os.environ.get('GITHUB_REF') == 'refs/heads/main', 'TRUSTED_REF')
    p = paths()
    if args.mode == 'preflight':
        commit, _ = remote_state(os.environ['SOURCE_READ_TOKEN'])
        print(json.dumps({'status': 'private-target-reachable', 'branchExists': commit is not None, 'ready': False}))
    elif args.mode == 'download':
        result = download(p['candidate'], os.environ.get('SOURCE_TRANSPORT', 'auto'), os.environ.get('AGENT_AUTH_TOKEN') or None)
        print(json.dumps(result))
        return 0 if result['status'] == 'downloaded-pinned-baseline' else 1
    elif args.mode == 'stage':
        manifest = build_bundle(p['candidate'], p['export'], p['exportResult'], p['bundle'], os.environ.get('EXTRACT_SCOPE', 'priority'), load_policy())
        output('bundle_ready', 'true')
        print(json.dumps({'status': 'staged', 'scope': manifest['scope'], 'counts': manifest['counts'], 'ready': False}))
    elif args.mode == 'publish':
        summary = publish(p['bundle'], p['git'], os.environ['SOURCE_PUBLISH_TOKEN'], os.environ['GITHUB_RUN_ID'],
                          int(os.environ['GITHUB_RUN_ATTEMPT']), os.environ['GITHUB_SHA'], dry_run=os.environ.get('EXTRACT_PUBLISH') != 'true')
        p['publishResult'].write_text(json.dumps(summary) + '\n')
        print(json.dumps({k: summary[k] for k in ('result', 'scope', 'included', 'includedBytes', 'ready')}))
    else:
        result = p['publishResult']
        if not result.exists():
            print(json.dumps({'result': 'not-published', 'ready': False}))
            return 1
        summary = json.loads(result.read_text())
        print(json.dumps({k: summary.get(k) for k in ('result', 'branch', 'scope', 'included', 'includedBytes', 'ready')}))
        return 0 if summary.get('result') in ('published', 'unchanged', 'dry-run') else 1
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except ExtractError as error:
        print(json.dumps({'result': 'failed', 'failureCode': str(error), 'ready': False}))
        raise SystemExit(1)
    except urllib.error.HTTPError as error:
        print(json.dumps({'result': 'failed', 'failureCode': 'PRIVATE_API_AUTH' if error.code in (401, 403) else 'PRIVATE_API_HTTP', 'httpStatus': error.code, 'ready': False}))
        raise SystemExit(1)
    except subprocess.TimeoutExpired:
        print(json.dumps({'result': 'failed', 'failureCode': 'GIT_TIMEOUT', 'ready': False}))
        raise SystemExit(1)
    except Exception:
        raise SystemExit('Source extract failed; no file names, contents, headers or credentials published.')
