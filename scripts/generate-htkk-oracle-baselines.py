"""Generate the PowerShell and C# views of scripts/htkk-oracle-baselines.json.

Offline and deterministic; never reads vendor bytes. The JSON is the only reviewed source of
the per-version HTKK pins (distribution, signer, MSI counts, file and method pins). Each
consumer gets a generated, closed table: an unknown version, a missing pin or a malformed
value is a generation error, never a fallback to another version.

  python3 scripts/generate-htkk-oracle-baselines.py          # write
  python3 scripts/generate-htkk-oracle-baselines.py --check  # verify (also run by the unit tests)
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent
SOURCE = ROOT / 'htkk-oracle-baselines.json'
PS_OUT = ROOT / 'HtkkOracleBaseline.ps1'
CS_OUT = ROOT / 'HtkkOracleBaseline.cs'
VERSIONS = ('5.8.1', '5.8.2')
DEFAULT = '5.8.1'
SHA = re.compile(r'[0-9a-f]{64}')
TOKEN = re.compile(r'0x06[0-9a-f]{6}')
FILES = ('Project/HTKK.exe', 'Project/HTKK.exe.config', 'Project/TAX.HTKK.Business.dll', 'Project/TAX.HTKK.Utilities.dll',
         'Project/Menu.xml', 'Project/Message.xml', 'InterfaceTemplates/excel/01_GTGT_TT80_283.xls',
         'InterfaceIni/Catalogue_DM_NNKD.xml', 'InterfaceIni/DM_DUNG_CHUNG.xml',
         'InterfaceTemplates/xml/04_GTGT_TT89_309.xml', 'InterfaceTemplates/excel/04_GTGT_TT89_309.xls')
STATUSES = ('reviewed', 'token-renumbered', 'changed', 'changed-reviewed', 'added-reviewed')
CHANGED = ('changed', 'changed-reviewed')
ENTRY_PREFIX = 'y8-entry-'
# U5 3.1.0 import-tick plan (CnkdHkd01TT50Nckt310 exists only from HTKK 5.8.2): methods of a later release only.
TICK_PREFIX = 'u5-310-tick-'
TICK_IDS = ('u5-310-tick-autobind', 'u5-310-tick-locks', 'u5-310-tick-cellchange', 'u5-310-tick-child-keys', 'u5-310-tick-buttonclick', 'u5-310-tick-pl01', 'u5-310-tick-capnhat',
            'u5-310-tick-copy-table', 'u5-310-tick-child-column', 'u5-310-tick-grid-cellchange', 'u5-310-tick-dowork-cellchange', 'u5-310-tick-grid-button', 'u5-310-tick-dowork-button')
ADDED = 'added-reviewed'


class BaselineError(ValueError):
    pass


def require(test, message):
    if not test:
        raise BaselineError(message)


def unique(pairs):
    value = {}
    for key, item in pairs:
        require(key not in value, 'duplicate key ' + key)
        value[key] = item
    return value


def load(path=SOURCE):
    data = json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique)
    validate(data)
    return data


def validate(data):
    require(type(data) is dict and set(data) == {'format', 'default', 'notes', 'versions'}, 'top-level keys')
    require(data['format'] == 'htkk-oracle-baselines-v1' and data['default'] == DEFAULT, 'format/default')
    require(type(data['versions']) is dict and tuple(data['versions']) == VERSIONS, 'versions')
    keys = {'releaseDate', 'distribution', 'signer', 'msi', 'configVersion', 'serviceVersion', 'mainWindowCaption', 'files', 'methods'}
    reviewed = None
    for version, value in data['versions'].items():
        require(type(value) is dict and set(value) == keys, version + ' keys')
        require(re.fullmatch(r'[0-3][0-9]/[01][0-9]/20[0-9]{2}', value['releaseDate']) is not None, version + ' date')
        d = value['distribution']
        require(set(d) == {'officialUrl', 'archiveSha256', 'archiveBytes', 'archiveFolder', 'setupSha256', 'msiSha256', 'cabSha256'}, version + ' distribution')
        require(re.fullmatch(r'https://www\.fshare\.vn/file/[A-Z0-9]{12}', d['officialUrl']) is not None, version + ' url')
        require(d['archiveFolder'] == 'HTKK_' + version + '_DLL_signed', version + ' folder')
        require(type(d['archiveBytes']) is int and 1 <= d['archiveBytes'] <= 200 * 1024 * 1024, version + ' bytes')
        for key in ('archiveSha256', 'setupSha256', 'msiSha256', 'cabSha256'):
            require(SHA.fullmatch(d[key]) is not None, version + ' ' + key)
        s = value['signer']
        require(s == {'serial': '6435F70483012A5DBC374003', 'subject': 'Tổng Cục Thuế', 'issuer': 'GlobalSign GCC R45 EV CodeSigning CA 2020', 'root': 'GlobalSign Code Signing Root R45'}, version + ' signer')
        m = value['msi']
        require(set(m) == {'productVersion', 'productCode', 'mediaLastSequence', 'files', 'sizeMatches', 'msiHashRows', 'msiHashMatches', 'versionedWithoutMsiHash', 'msiHashAlgorithm'}, version + ' msi')
        # The MSI ProductVersion is the installer's own version, not the business release.
        require(m['productVersion'] == '4.2.2' and m['productCode'] == '{53B9335C-0849-4958-9E88-84E55F97929D}' and m['msiHashAlgorithm'] == 'MD5-legacy', version + ' msi identity')
        require(m['files'] == m['sizeMatches'] == m['mediaLastSequence'] and m['msiHashRows'] == m['msiHashMatches'] and m['files'] - m['msiHashRows'] == m['versionedWithoutMsiHash'] == 33, version + ' msi counts')
        require(value['configVersion'] == value['serviceVersion'] == version and value['mainWindowCaption'] == 'Hỗ trợ kê khai thuế - Phiên bản ' + version, version + ' version strings')
        require(tuple(value['files']) == FILES and all(SHA.fullmatch(h) for h in value['files'].values()), version + ' files')
        methods = value['methods']
        require(type(methods) is list and 1 <= len(methods) <= 64, version + ' methods')
        ids = [x.get('id') for x in methods]
        require(len(set(ids)) == len(ids), version + ' method ids')
        for x in methods:
            base = {'id', 'assembly', 'type', 'method', 'token', 'ilBytes', 'ilSha256', 'status'}
            extra = set(x) - base
            require(base <= set(x) and extra <= {'reviewedToken581', 'change', 'review'}, version + ' method keys')
            require(re.fullmatch(r'[a-z0-9-]{1,40}', x['id']) and x['assembly'] in ('B', 'H') and re.fullmatch(r'[A-Za-z0-9_]{1,64}', x['type']) and re.fullmatch(r'[.A-Za-z0-9_]{1,64}', x['method']), version + ' method identity')
            require(TOKEN.fullmatch(x['token']) and type(x['ilBytes']) is int and 0 < x['ilBytes'] < 1 << 20 and SHA.fullmatch(x['ilSha256']) and x['status'] in STATUSES, version + ' method pin')
        if reviewed is None:
            require(all(x['status'] == 'reviewed' and set(x) == base for x in methods), 'default methods must all be reviewed')
            require(not any(x['id'].startswith(TICK_PREFIX) for x in methods), 'default methods must not carry later-release pins')
            reviewed = {x['id']: x for x in methods}
            continue
        # A method of a later release only: absent from the default oracle, pinned as itself with its review,
        # never a substitute for a default-version body (own id prefix, no reviewedToken581).
        added = [x for x in methods if x['status'] == ADDED]
        for x in added:
            require(x['id'].startswith(TICK_PREFIX) and x['id'] not in reviewed and set(x) == base | {'review'}, version + ' added method')
            require(type(x['review']) is str and 20 <= len(x['review']) <= 1000, version + ' added review')
        require(all(x['status'] == ADDED for x in methods if x['id'].startswith(TICK_PREFIX)), version + ' tick pins must be added-reviewed')
        # The plan pins every method it relies on, in this order, or none (a version without the class).
        require(tuple(x['id'] for x in methods if x['id'].startswith(TICK_PREFIX)) in ((), TICK_IDS), version + ' tick pin set')
        require(set(ids) - {x['id'] for x in added} == set(reviewed), version + ' method set')
        for x in methods:
            if x['status'] == ADDED:
                continue
            r = reviewed[x['id']]
            require((x['assembly'], x['type'], x['method']) == (r['assembly'], r['type'], r['method']), version + ' method identity drift')
            if x['status'] == 'reviewed':
                require(set(x) == base and x == r, version + ' reviewed must equal the default pin')
            else:
                require(x.get('reviewedToken581') == r['token'], version + ' reviewed token')
                require(('change' in x) == (x['status'] in CHANGED), version + ' change note')
                # An accepted changed body carries its review and is a different body from the default one.
                require(('review' in x) == (x['status'] == 'changed-reviewed'), version + ' review note')
                if x['status'] in CHANGED:
                    require((x['ilBytes'], x['ilSha256']) != (r['ilBytes'], r['ilSha256']), version + ' changed body')
                    require(all(type(x[k]) is str and 20 <= len(x[k]) <= 1000 for k in ('change', 'review') if k in x), version + ' notes')
                if x['status'] == 'token-renumbered':
                    # Raw bytes may differ only through renumbered operand tokens: same length.
                    require(x['ilBytes'] == r['ilBytes'], version + ' renumbered length')


def ps(value):
    return "'" + str(value).replace("'", "''") + "'"


def cs(value):
    text = str(value)
    require(all(c not in text for c in '"\\\n\r'), 'unsafe C# literal')
    return '"' + text + '"'


def entry_pins(value, reviewed):
    """Y8 original-entry pins as the C# plan expects them: asm|type|method|token|ilBytes|ilSha256.

    A changed body keeps the REVIEWED (default-version) length and hash at the new token: the
    harness then requires the reviewed body, finds another one and fails closed with that bit
    set in declarationEntryMethodPinMask. It is never accepted as the reviewed body. Only a
    changed-reviewed body (reviewed against the driver plan for that version) is pinned as itself.
    """
    out = []
    for x in value['methods']:
        if not x['id'].startswith(ENTRY_PREFIX):
            continue
        source = reviewed[x['id']] if x['status'] == 'changed' else x
        out.append('|'.join((x['assembly'], x['type'], x['method'], x['token'], str(source['ilBytes']), source['ilSha256'])))
    return out


def tick_pins(value):
    """U5 3.1.0 import-tick pins (asm|type|method|token|ilBytes|ilSha256) of one version; empty when the
    version has none (5.8.1: the class does not exist, the C# accessor then refuses to run the plan)."""
    return ['|'.join((x['assembly'], x['type'], x['method'], x['token'], str(x['ilBytes']), x['ilSha256'])) for x in value['methods'] if x['id'].startswith(TICK_PREFIX)]


def render(data):
    reviewed = {x['id']: x for x in data['versions'][DEFAULT]['methods']}
    lines = ['# Auto-generated by generate-htkk-oracle-baselines.py from htkk-oracle-baselines.json. Do not edit.',
             '# Closed per-version pins; an unknown version is refused by ValidateSet.',
             '$HtkkOracleDefaultVersion=' + ps(DEFAULT),
             'function Get-HtkkOracleBaseline {',
             ' [CmdletBinding()]',
             ' param([Parameter(Mandatory=$true)][ValidateSet(' + ','.join(ps(v) for v in VERSIONS) + ')][string]$Version)',
             ' switch -CaseSensitive ($Version) {']
    for version, v in data['versions'].items():
        d, s, m = v['distribution'], v['signer'], v['msi']
        fields = [('version', version), ('officialUrl', d['officialUrl']), ('archiveSha256', d['archiveSha256']), ('archiveFolder', d['archiveFolder']),
                  ('setupSha256', d['setupSha256']), ('msiSha256', d['msiSha256']), ('cabSha256', d['cabSha256']),
                  ('signerSerial', s['serial']), ('signerSubject', s['subject']), ('msiProductVersion', m['productVersion']),
                  ('configVersion', v['configVersion']), ('serviceVersion', v['serviceVersion']), ('mainWindowCaption', v['mainWindowCaption'])]
        numbers = [('mediaLastSequence', m['mediaLastSequence']), ('msiFiles', m['files']), ('msiHashMatches', m['msiHashMatches']), ('versionedWithoutMsiHash', m['versionedWithoutMsiHash'])]
        body = ';'.join(k + '=' + ps(x) for k, x in fields) + ';' + ';'.join(k + '=' + str(x) for k, x in numbers)
        files = ';'.join(ps(k) + '=' + ps(x) for k, x in v['files'].items())
        lines.append('  ' + ps(version) + ' { return [ordered]@{' + body + ';files=[ordered]@{' + files + '}} }')
    lines += ["  default { throw 'HTKK_ORACLE_VERSION_UNKNOWN' }", ' }', '}']
    ps_text = '\n'.join(lines) + '\n'

    c = ['// Auto-generated by generate-htkk-oracle-baselines.py from htkk-oracle-baselines.json. Do not edit.',
         '// C# 2.0 / CLR2. The reference host selects exactly one version before any pin is read;',
         '// an unknown version, a second different selection or an unpinned path throws.',
         'using System;',
         '',
         'internal static class HtkkOracleBaseline {',
         ' internal const string DefaultVersion=' + cs(DEFAULT) + ';',
         ' internal static readonly string[] Versions=new string[]{' + ','.join(cs(v) for v in VERSIONS) + '};',
         ' private static string selected;',
         ' internal static void Select(string version){',
         '  if(Index(version)<0)throw new ArgumentException("HTKK_ORACLE_VERSION_UNKNOWN");',
         '  if(selected!=null&&selected!=version)throw new InvalidOperationException("HTKK_ORACLE_VERSION_CONFLICT");',
         '  selected=version;',
         ' }',
         ' internal static string Version{get{if(selected==null)throw new InvalidOperationException("HTKK_ORACLE_VERSION_UNSELECTED");return selected;}}',
         ' private static int Index(string version){for(int i=0;i<Versions.Length;i++)if(Versions[i]==version)return i;return -1;}',
         ' private static int Current{get{return Index(Version);}}',
         ' private static readonly string[] FilePaths=new string[]{' + ','.join(cs(f) for f in FILES) + '};',
         ' private static readonly string[][] FileHashes=new string[][]{']
    c.append(',\n'.join('  new string[]{' + ','.join(cs(v['files'][f]) for f in FILES) + '}' for v in data['versions'].values()))
    c += [' };',
          ' internal static string File(string path){for(int i=0;i<FilePaths.Length;i++)if(FilePaths[i]==path)return FileHashes[Current][i];throw new ArgumentException("HTKK_ORACLE_FILE_UNPINNED");}',
          ' private static readonly string[] Services=new string[]{' + ','.join(cs(v['serviceVersion']) for v in data['versions'].values()) + '};',
          ' internal static string ServiceVersion{get{return Services[Current];}}',
          ' private static readonly string[] Captions=new string[]{' + ','.join(cs(v['mainWindowCaption']) for v in data['versions'].values()) + '};',
          ' internal static string MainWindowCaption{get{return Captions[Current];}}',
          ' private static readonly string[][] Entry=new string[][]{']
    c.append(',\n'.join('  new string[]{' + ','.join(cs(p) for p in entry_pins(v, reviewed)) + '}' for v in data['versions'].values()))
    c += [' };',
          ' // Y8 original-entry method pins: asm|type|method|token|IL bytes|IL-code SHA-256 (see entry_pins).',
          ' internal static string[] EntryMethodPins(){return (string[])Entry[Current].Clone();}',
          ' private static readonly string[][] Tick=new string[][]{']
    c.append(',\n'.join(('  new string[]{' + ','.join(cs(p) for p in tick_pins(v)) + '}') if tick_pins(v) else '  new string[0]' for v in data['versions'].values()))
    c += [' };',
          ' // U5 3.1.0 import-tick method pins (later-release methods, added-reviewed); none for 5.8.1, which refuses the plan.',
          ' internal static string[] TickMethodPins(){if(Tick[Current].Length==0)throw new InvalidOperationException("HTKK_ORACLE_TICK_UNPINNED");return (string[])Tick[Current].Clone();}',
          '}']
    return ps_text, '\n'.join(c) + '\n'


def main(argv):
    data = load()
    ps_text, cs_text = render(data)
    stale = [p.name for p, text in ((PS_OUT, ps_text), (CS_OUT, cs_text)) if not p.exists() or p.read_text(encoding='utf-8') != text]
    if '--check' in argv:
        if stale:
            raise SystemExit('HTKK oracle baselines stale: ' + ', '.join(stale))
        return
    for path, text in ((PS_OUT, ps_text), (CS_OUT, cs_text)):
        path.write_text(text, encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main(sys.argv[1:])
