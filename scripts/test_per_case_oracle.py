"""Offline contracts of the per-case HTKK oracle (registry 'htkkVersion', default 5.8.1).

A case without the field dispatches, reports and is authenticated exactly as before; a 5.8.2
case gets the probe input htkk_version, the ' [HTKK 5.8.2]' run title and the '@htkk582' status
context, and never gates a release. No network, no native evidence.
"""
import copy, datetime, importlib.util, json, pathlib, tempfile, unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).parent


def load(name, file, folder=ROOT):
    spec = importlib.util.spec_from_file_location(name, folder / file); module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module


d = load('per_case_oracle_dispatch', 'dispatch-native-cases.py')
registry = d.case_registry
batch = load('per_case_oracle_batch', 'native_batch.py')
import native_preflight_retry as retry
import test_login_ready_retry as login
import test_native_preflight_retry as preflight

RAW = json.loads((ROOT / 'htkk-native-cases.json').read_text())
BUILDER_SHA = '9' * 40
START = datetime.datetime(2026, 11, 11, 10, 0, 0, tzinfo=datetime.timezone.utc)
GATE = registry.GATE_CASES[0]
CANDIDATE = '01NTNN-NCCNN-entry-M10-2026'
# U5 3.1.0 exists only in HTKK 5.8.2, so its adapter is pinned to that oracle; the 01-10/GTGT candidate also runs on 5.8.2.
U5_310 = '01CNKD-TT50-310-pl01-three-groups-Q3-2026'
ANNEX10 = '01GTGT-annex10-nq204-M10-2026'
# Z8 05/KK-TNCN TT89 3.0.9 exists only in HTKK 5.8.2 as well (adapter 05-kk-tncn-tt89-3.0.9 pinned to that oracle).
Z8_TT89 = '05KK-TT89-withheld-Q4-2026'
OTHER = '03TNDN-profit20-Y2025'


def on_582(*cases, module=registry):
    """The trusted registry with these candidate cases moved to the 5.8.2 oracle (in memory only)."""
    return patch.dict(module.CASES, {c: dict(module.CASES[c], htkkVersion='5.8.2') for c in cases})


def publication(*cases):
    return {'format': 'htkk-web-input-publication-v1', 'sourceCommit': 'a' * 40, 'cases': [{'caseId': c, 'artifactCommit': str(i + 1) * 40} for i, c in enumerate(cases)]}


def record(calls):
    def send(url, token, payload): calls.append((url, payload))
    return send


class Registry(unittest.TestCase):
    def test_committed_registry_keeps_every_case_on_the_default_oracle(self):
        # Only U5 3.1.0 and Z8 05/KK-TNCN TT89 (XML versions that exist only in HTKK 5.8.2) and the 01-10/GTGT candidate
        # (HTKK 5.8.2 accepts negative goods values there) name 5.8.2; every other case stays on the default oracle.
        NEWER = {U5_310, '01CNKD-TT50-310-pl03-two-groups-Q3-2026', ANNEX10, Z8_TT89}
        self.assertEqual(registry.oracle.DEFAULT, '5.8.1')
        self.assertEqual({c['caseId'] for c in RAW['cases'] if 'htkkVersion' in c}, NEWER)
        self.assertEqual({c for c in registry.CASES if registry.htkk_version(c) != '5.8.1'}, NEWER)
        self.assertTrue(all(registry.htkk_version(c) == '5.8.2' and not registry.CASES[c]['releaseGate'] for c in NEWER))
        self.assertEqual(registry.status_context(U5_310), 'htkk-native/cnkd01-310-pl01-three-groups-q3-2026@htkk582')
        self.assertEqual(registry.status_context(ANNEX10), 'htkk-native/annex10-nq204@htkk582')
        self.assertEqual(registry.status_context(Z8_TT89), 'htkk-native/tncn05kk-tt89-withheld-q4-2026@htkk582')
        self.assertEqual({c: registry.status_context(c) for c in registry.CASES if c not in NEWER}, {c: v['statusContext'] for c, v in registry.CASES.items() if c not in NEWER})

    def test_an_adapter_of_a_later_release_runs_only_on_that_oracle(self):
        index = {c['caseId']: i for i, c in enumerate(RAW['cases'])}
        adapters = {a['adapterId']: i for i, a in enumerate(RAW['adapters'])}
        for mutate in (lambda r: r['cases'][index[U5_310]].pop('htkkVersion'),
                       lambda r: r['adapters'][adapters['01-cnkd-hkd-3.1.0-pl01']].update(htkkVersion='5.8.1'),
                       lambda r: r['adapters'][adapters['01-cnkd-hkd-2.9.8']].update(htkkVersion='5.8.2'),
                       lambda r: r['cases'][index[Z8_TT89]].pop('htkkVersion'),
                       lambda r: r['adapters'][adapters['05-kk-tncn-tt89-3.0.9']].update(htkkVersion='5.8.1'),
                       lambda r: r['adapters'][adapters['05-kk-tncn-2.9.3']].update(htkkVersion='5.8.2')):
            with self.subTest(), self.assertRaises(ValueError):
                self.mutated(mutate)

    def test_case_version_accepts_only_a_reviewed_non_default_oracle_on_a_candidate(self):
        candidate = copy.deepcopy(registry.CASES[CANDIDATE]); gate = copy.deepcopy(registry.CASES[GATE])
        self.assertEqual(registry.case_version(candidate), '5.8.1')
        self.assertEqual(registry.case_version(dict(candidate, htkkVersion='5.8.2')), '5.8.2')
        # One spelling per version (absent = default), reviewed versions only, never on a release gate.
        for bad in (dict(candidate, htkkVersion='5.8.1'), dict(candidate, htkkVersion='5.8.3'), dict(candidate, htkkVersion=''), dict(candidate, htkkVersion=582),
                    dict(candidate, htkkVersion=None), dict(gate, htkkVersion='5.8.2'), dict(candidate, oracle='5.8.2')):
            with self.subTest(bad=bad.get('htkkVersion', bad.get('oracle'))), self.assertRaises(ValueError):
                registry.case_version(bad)

    def mutated(self, mutate):
        value = copy.deepcopy(RAW); mutate(value)
        with tempfile.TemporaryDirectory() as directory:
            folder = pathlib.Path(directory); (folder / 'htkk-native-cases.json').write_text(json.dumps(value))
            for name in ('htkk_native_cases.py', 'htkk_oracle.py', 'generate-htkk-oracle-baselines.py', 'htkk-oracle-baselines.json'):
                (folder / name).write_bytes((ROOT / name).read_bytes())
            return load('per_case_oracle_registry', 'htkk_native_cases.py', folder)

    def test_registry_file_loads_a_5_8_2_candidate_and_refuses_a_5_8_2_gate(self):
        index = {c['caseId']: i for i, c in enumerate(RAW['cases'])}
        self.assertEqual(self.mutated(lambda r: None).CASES, registry.CASES)  # the copied loader itself is sound
        module = self.mutated(lambda r: r['cases'][index[CANDIDATE]].update(htkkVersion='5.8.2'))
        self.assertEqual(module.htkk_version(CANDIDATE), '5.8.2'); self.assertEqual(module.htkk_version(OTHER), '5.8.1')
        self.assertEqual(module.status_context(CANDIDATE), 'htkk-native/ntnn01-nccnn-entry-m10-2026@htkk582')
        self.assertEqual(module.GATE_CASES, registry.GATE_CASES)
        for mutate in (lambda r: r['cases'][index[GATE]].update(htkkVersion='5.8.2'), lambda r: r['cases'][index[CANDIDATE]].update(htkkVersion='5.8.1'),
                       lambda r: r['cases'][index[CANDIDATE]].update(htkkVersion='5.8.3')):
            with self.subTest(), self.assertRaises(ValueError):
                self.mutated(mutate)


class Dispatch(unittest.TestCase):
    def test_default_case_dispatch_is_byte_for_byte_unchanged(self):
        calls = []
        d.dispatch(publication(GATE, OTHER), 'builder', 'source', record(calls))
        # The exact pre-field body: same keys, order and values, no htkk_version.
        for (status, probe), case, artifact in zip(zip(calls[::2], calls[1::2]), (GATE, OTHER), ('1' * 40, '2' * 40)):
            self.assertEqual(json.dumps(status[1], separators=(',', ':')), json.dumps({'state': 'pending', 'context': registry.CASES[case]['statusContext'], 'description': 'Fixed synthetic native case queued input:' + artifact}, separators=(',', ':')))
            expected = {'ref': 'main', 'inputs': {'install_and_probe': True, 'synthetic_login': True, 'acknowledge_registration': True, 'runtime_host': 'clr2-x86-reference', 'gui_automation': registry.driver(case),
                                                  'web_source_sha': 'a' * 40, 'web_case_id': case, 'web_artifact_commit': artifact}}
            self.assertEqual(json.dumps(probe[1], separators=(',', ':')), json.dumps(expected, separators=(',', ':')))
            self.assertEqual(d.run_title(case), 'HTKK native case ' + case + ' (' + registry.driver(case) + ')')
        # The whole default-oracle cohort never names a version; only the 5.8.2 cases are dispatched on 5.8.2.
        calls = []
        d.dispatch({'format': 'htkk-web-input-publication-v1', 'sourceCommit': 'a' * 40, 'cases': [{'caseId': c, 'artifactCommit': 'b' * 40} for c in d.CASES if registry.htkk_version(c) == '5.8.1']}, 'builder', 'source', record(calls))
        self.assertFalse(any('htkk_version' in p.get('inputs', {}) or '@' in p.get('context', '') for _, p in calls))
        calls = []
        d.dispatch(publication(U5_310), 'builder', 'source', record(calls))
        self.assertEqual([p['inputs'].get('htkk_version') for _, p in calls if 'inputs' in p], ['5.8.2'])
        self.assertTrue(all(p['context'].endswith('@htkk582') for _, p in calls if 'context' in p))

    def test_5_8_2_case_dispatches_with_its_version_title_and_context(self):
        calls = []
        with on_582(CANDIDATE):
            d.dispatch(publication(OTHER, CANDIDATE), 'builder', 'source', record(calls))
            self.assertEqual(d.run_title(CANDIDATE), 'HTKK native case ' + CANDIDATE + ' (declaration-web-import-inspect) [HTKK 5.8.2]')
            self.assertEqual(d.run_title(OTHER), 'HTKK native case ' + OTHER + ' (declaration-web-import-inspect)')
        (s1, p1), (s2, p2) = (calls[0][1], calls[1][1]), (calls[2][1], calls[3][1])
        self.assertEqual(s1['context'], 'htkk-native/tndn03-profit20-y2025'); self.assertNotIn('htkk_version', p1['inputs'])
        self.assertEqual(s2['context'], 'htkk-native/ntnn01-nccnn-entry-m10-2026@htkk582')
        self.assertEqual(list(p2['inputs'])[-1], 'htkk_version'); self.assertEqual(p2['inputs']['htkk_version'], '5.8.2')
        self.assertEqual({k: v for k, v in p2['inputs'].items() if k != 'htkk_version'}, d.inputs('a' * 40, {'caseId': CANDIDATE, 'artifactCommit': '2' * 40}))
        # The probe workflow accepts exactly this input value and renders exactly this title suffix.
        workflow = (ROOT.parent / '.github/workflows/probe-htkk-windows.yml').read_text()
        self.assertIn("options: ['5.8.1', '5.8.2']", workflow); self.assertIn("inputs.htkk_version == '5.8.2' && ' [HTKK 5.8.2]' || ''", workflow)

    def test_5_8_2_dispatch_failure_reports_on_its_own_context(self):
        calls = []
        def send(url, token, payload):
            calls.append((url, payload))
            if '/dispatches' in url: raise RuntimeError('unpublished')
        with on_582(CANDIDATE), self.assertRaises(RuntimeError):
            d.dispatch(publication(CANDIDATE), 'builder', 'source', send)
        self.assertEqual([(p['state'], p['context']) for u, p in calls if '/statuses/' in u], [('pending', 'htkk-native/ntnn01-nccnn-entry-m10-2026@htkk582'), ('failure', 'htkk-native/ntnn01-nccnn-entry-m10-2026@htkk582')])

    def test_run_lookup_tells_the_two_oracles_of_one_case_apart(self):
        def run(title): return {'id': 1, 'path': d.PROBE, 'event': 'workflow_dispatch', 'head_branch': 'main', 'head_sha': BUILDER_SHA, 'repository': {'full_name': d.BUILDER}, 'created_at': '2026-11-11T10:00:01Z', 'display_title': title}
        default_title = 'HTKK native case ' + CANDIDATE + ' (declaration-web-import-inspect)'
        def listing(*titles): return lambda url, token: {'total_count': len(titles), 'workflow_runs': [run(t) for t in titles]}
        self.assertIs(d.created(CANDIDATE, BUILDER_SHA, START, 't', listing(default_title)), True)
        self.assertIs(d.created(CANDIDATE, BUILDER_SHA, START, 't', listing(default_title + ' [HTKK 5.8.2]')), False)
        with on_582(CANDIDATE):
            self.assertIs(d.created(CANDIDATE, BUILDER_SHA, START, 't', listing(default_title)), False)
            self.assertIs(d.created(CANDIDATE, BUILDER_SHA, START, 't', listing(default_title + ' [HTKK 5.8.2]')), True)
            self.assertIsNone(d.created(CANDIDATE, BUILDER_SHA, START, 't', listing('Kiểm tra điều kiện chạy HTKK Windows')))


class Authenticator(unittest.TestCase):
    def statuses(self, context, state='failure', artifact='1' * 40):
        return [{'context': context, 'state': state, 'description': 'Fixed synthetic native case did not pass input:' + artifact, 'target_url': 'https://github.com/congminh1254/htkk_builder/actions/runs/77'}]

    def discover(self, statuses):
        seen = []
        def retry_hint(status, context, source, builder, artifact): seen.append(context); return False
        result = batch.discover(publication(CANDIDATE), BUILDER_SHA, statuses, get=lambda *a: self.fail('no evidence read for a candidate'), retry=retry_hint)
        return result, seen

    def test_candidate_is_tracked_on_its_own_oracle_context_and_never_gates(self):
        plain, versioned = 'htkk-native/ntnn01-nccnn-entry-m10-2026', 'htkk-native/ntnn01-nccnn-entry-m10-2026@htkk582'
        self.assertEqual(self.discover(self.statuses(plain))[1], [plain])
        self.assertEqual(self.discover(self.statuses(versioned))[1], [])  # another oracle's status is not this case's
        with on_582(CANDIDATE, module=batch.registry):
            result, seen = self.discover(self.statuses(versioned))
            self.assertEqual(seen, [versioned]); self.assertEqual(result['cases'], [])
            self.assertEqual(self.discover(self.statuses(plain))[1], [])

    def test_gate_rules_are_unchanged(self):
        # A failed gate on its default context still rejects the cohort; a 5.8.2 status never satisfies it.
        with self.assertRaises(ValueError):
            batch.discover(publication(GATE), BUILDER_SHA, self.statuses(registry.CASES[GATE]['statusContext']), get=lambda *a: self.fail())
        self.assertIsNone(batch.discover(publication(GATE), BUILDER_SHA, self.statuses(registry.CASES[GATE]['statusContext'] + '@htkk582', 'success'), get=lambda *a: self.fail()))


class PreflightRetry(unittest.TestCase):
    def fixture(self, version):
        jobs, records = login.gtgt(); records[0]['version'] = version
        f = preflight.NativePreflightRetry.fixture(preflight.NativePreflightRetry(), 'startup'); f['steps'][:] = jobs['jobs'][0]['steps']; f['records'][:] = records
        return f

    def recover(self, f, context):
        return retry.recover(f['status'], context, preflight.SOURCE, preflight.BUILDER, preflight.INPUT, f['get'], lambda x: x, f['send'], 'actions-placeholder', 'status-placeholder', f['state'])

    def test_contexts_admit_only_reviewed_oracle_suffixes(self):
        for context in ('htkk-native/zero', 'htkk-native/zero@htkk582'):
            self.assertTrue(retry.CONTEXT.fullmatch(context))
        for context in ('htkk-native/zero@htkk581', 'htkk-native/zero@htkk583', 'htkk-native/zero@evil', 'htkk-native/zero@htkk582@htkk582', 'other/zero@htkk582'):
            self.assertFalse(retry.CONTEXT.fullmatch(context), context)
            self.assertFalse(self.recover(self.fixture('5.8.1'), context))

    def test_classification_requires_the_report_of_the_runs_own_oracle(self):
        jobs, records = login.gtgt()
        self.assertEqual(retry.classify(jobs, records), 'synthetic-login-not-ready')
        self.assertIsNone(retry.classify(jobs, records, '5.8.2'))
        records[0]['version'] = '5.8.2'
        self.assertIsNone(retry.classify(jobs, records)); self.assertEqual(retry.classify(jobs, records, '5.8.2'), 'synthetic-login-not-ready')

    def test_a_5_8_2_run_is_retried_once_on_its_own_context(self):
        f = self.fixture('5.8.2')
        self.assertFalse(self.recover(f, 'htkk-native/zero')); self.assertEqual(f['calls'], [])
        f = self.fixture('5.8.2')
        self.assertTrue(self.recover(f, 'htkk-native/zero@htkk582'))
        self.assertIn('/rerun-failed-jobs', f['calls'][0][0]); self.assertEqual(f['calls'][1][2]['context'], 'htkk-native/zero@htkk582')
        f = self.fixture('5.8.1')
        self.assertFalse(self.recover(f, 'htkk-native/zero@htkk582'))
        f = self.fixture('5.8.1')
        self.assertTrue(self.recover(f, 'htkk-native/zero')); self.assertEqual(f['calls'][1][2]['context'], 'htkk-native/zero')


if __name__ == '__main__':
    unittest.main()
