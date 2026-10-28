"""Generated result metadata and actual PowerShell reader adversarial integration.

Fixtures here are reader inputs only, never native/vendor parity evidence.
"""
import copy
import importlib.util
import json
import os
import pathlib
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).parent
spec = importlib.util.spec_from_file_location('typed_result_generator', ROOT/'generate-native-automation-registry.py')
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)


class NativeResultContract(unittest.TestCase):
    def setUp(self):
        self.registry = generator.load_registry()

    def reject(self, mutation):
        value = copy.deepcopy(self.registry)
        mutation(value)
        with self.assertRaises(ValueError):
            generator.validate_registry(value)

    def test_every_field_exactly_typed_and_defaulted(self):
        self.assertEqual(list(self.registry['resultFields']), self.registry['keys'])
        flags = [f for f in self.registry['resultFields'].values() if f['kind']=='boolean']
        counters = [f for f in self.registry['resultFields'].values() if f['kind']=='integer']
        self.assertGreater(len(flags), 90)
        self.assertGreater(len(counters), 40)
        self.assertTrue(all(f['default'] is False for f in flags))
        self.assertTrue(all(type(f['default']) is int and f['default']==0 for f in counters))

    def test_rejects_missing_extra_mistyped_or_unsafe_field_contracts(self):
        for mutation in (
            lambda r:r['resultFields'].pop('sourcePinsVerified'),
            lambda r:r['resultFields'].update(unreviewed={'kind':'boolean','default':False}),
            lambda r:r['resultFields']['sourcePinsVerified'].update(default=0),
            lambda r:r['resultFields']['sourcePinsVerified'].update(default=True),
            lambda r:r['resultFields']['visibleForms'].update(maximum=True),
            lambda r:r['resultFields']['visibleForms'].update(default=False),
            lambda r:r['resultFields']['visibleForms'].update(minimum=-1),
            lambda r:r['resultFields']['visibleForms'].update(maximum=2**31),
            lambda r:r['resultFields']['menuClickCount'].update(modeMaximums={'unknown':6}),
            lambda r:r['resultFields']['menuClickCount'].update(modeMaximums={'inspect':True}),
            lambda r:r['resultFields']['format'].update(values=["'; injected"]),
            lambda r:r['resultFields']['stage'].update(valuesFrom='unknown'),
            lambda r:r['resultFields']['runtimeRoundTrip'].update(activeModes=['inspect']),
            lambda r:r['resultFields']['amendmentPriorMoneyZero'].update(activeModes=['unknown']),
            lambda r:r['resultFields']['periodControls'].update(validator='arbitrary-code'),
            lambda r:r['resultFields']['annex12NumericSnapshots'].update(maximumLength=1000000),
        ):
            with self.subTest(mutation=mutation): self.reject(mutation)

    def test_complete_compile_closure_is_shared_with_launch_only_mode(self):
        closure=self.registry['modes']['inspect']['orderedCompileInputs']
        self.assertIn('HtkkNativeUiHarness.cs',closure)
        for mode in self.registry['modes'].values():
            self.assertEqual(mode['orderedCompileInputs'],closure)
        generated=(ROOT/'HtkkNativeCompileInputs.ps1').read_text()
        for mode in self.registry['modes']:
            self.assertIn("'"+mode+"' { return @("+','.join(generator.ps_literal(n) for n in closure)+"); }",generated)

    def test_actual_serializer_names_types_and_initial_defaults_match_registry(self):
        producers=generator.audit_result_producers(self.registry)
        self.assertEqual(set(producers),{k for k,v in self.registry['resultFields'].items() if v['kind'] in {'boolean','integer'}})
        paths=[ROOT/n for n in self.registry['modes']['inspect']['orderedCompileInputs'] if n not in {'HtkkNativeAutomationEnums.cs','HtkkNativeUiHarness.cs'}]
        originals=[p.read_text() for p in paths]
        # Mutate the actual producers rather than merely testing generated enum text.
        changes=[('sourcePinsVerified','unreviewedFlag'),('pins=false','pins=true'),
                 ('private bool pins=false','private int pins=0'),
                 ('visibleForms','unreviewedCounter'),('forms=0','forms=1'),
                 ('"periodYearMonthMatched","periodFirstDeclarationMatched"','"periodYearMonthMatched"')]
        for before,after in changes:
            with self.subTest(before=before):
                sources=originals[:]
                index=next(i for i,v in enumerate(sources) if before in v)
                sources[index]=sources[index].replace(before,after,1)
                with self.assertRaises(ValueError):generator.audit_result_producers(self.registry,sources)

    def test_csharp_typed_names_and_maximums_are_exhaustive(self):
        code=(ROOT/'HtkkNativeAutomationEnums.cs').read_text()
        for key,field in self.registry['resultFields'].items():
            if field['kind'] not in ('boolean','integer'):continue
            enum='Flag' if field['kind']=='boolean' else 'Counter'
            self.assertIn('case HtkkNativeResult'+enum+'.'+key[0].upper()+key[1:]+':',code)
        self.assertIn('if(mode==HtkkAutomationMode.GtgtAmendmentOpenInspect)return 6;',code)
        self.assertNotIn('dynamic ',code)
        self.assertNotIn('System.Text.Json',code)


class ActualPowerShellReaderBoundary(unittest.TestCase):
    def test_generated_reader_rejects_every_field_type_missing_field_range_and_inactive_value(self):
        pwsh=shutil.which('pwsh')
        if pwsh is None:
            candidate=pathlib.Path('/tmp/htkk-pwsh/runtime/pwsh')
            pwsh=str(candidate) if candidate.is_file() else None
        if pwsh is None:self.skipTest('PowerShell unavailable; Windows workflow runs actual strict-reader fixtures')
        registry=generator.load_registry()
        # One PowerShell process: all cases run in memory with fixed fake defaults,
        # serializing to a temporary result path as the real reader receives it.
        with tempfile.TemporaryDirectory() as tmp:
            path=ROOT/'Test-HtkkNativeResultContract.ps1'
            env={k:os.environ[k] for k in ('PATH','HOME','LANG','TMPDIR','SystemRoot','WINDIR','TEMP','TMP') if k in os.environ}
            env.update(POWERSHELL_TELEMETRY_OPTOUT='1',POWERSHELL_UPDATECHECK='Off')
            result=subprocess.run([pwsh,'-NoLogo','-NoProfile','-NonInteractive','-File',str(path),str(ROOT/'Get-HtkkSafeGuiReferenceResult.ps1'),str(ROOT/'HtkkNativeResultDefaults.ps1'),str(ROOT/'htkk-native-automation-registry.json')],env=env,capture_output=True,text=True,timeout=90)
            self.assertEqual(result.returncode,0,result.stderr[-3000:])
            match=re.search(r'BOUNDARIES=(\d+)',result.stdout)
            self.assertIsNotNone(match,result.stdout[-2000:])
            self.assertGreater(int(match.group(1)),800)


if __name__=='__main__':unittest.main()
