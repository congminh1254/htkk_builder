"""Compilation consumes the reviewed registry closure, not a parallel source list.

These are offline boundary tests; actual CLR2 compilation is proved by Windows.
"""
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).parent


class NativeCompilationContractTests(unittest.TestCase):
    def test_every_mode_compiles_identical_complete_partial_closure(self):
        registry = json.loads((ROOT / 'htkk-native-automation-registry.json').read_text())
        modes = registry['modes']
        closure = modes['gtgt-web-import-inspect']['orderedCompileInputs']
        self.assertEqual(len(closure), len(set(closure)))
        for name, metadata in modes.items():
            self.assertEqual(metadata['orderedCompileInputs'], closure, name)
        # This discovers real partial definitions and shared types, including future
        # partials: an omitted file must fail before reaching a Windows runner.
        required = {'HtkkNativeAutomationEnums.cs', 'HtkkNativeUiHarness.cs',
                    'HtkkWebTaxComparison.cs'}
        for path in ROOT.glob('Htkk*.cs'):
            if re.search(r'\bpartial\s+class\s+HtkkGuiReferenceAutomation\b', path.read_text()):
                required.add(path.name)
        self.assertEqual(set(closure), required)

    def test_host_consumes_generated_inputs_and_keeps_bounded_compiler(self):
        host = (ROOT / 'New-HtkkX86ReferenceHost.ps1').read_text()
        self.assertIn(". (Join-Path $PSScriptRoot 'HtkkNativeCompileInputs.ps1')", host)
        self.assertIn('foreach($name in @(Get-HtkkNativeCompileInputs -Mode $GuiAutomation))', host)
        self.assertIn("$name -cnotmatch '\\AHtkk[A-Za-z0-9]+\\.cs\\z'", host)
        self.assertIn('[IO.FileAttributes]::ReparsePoint', host)
        self.assertIn('$inputFile.Length -gt 524288', host)
        self.assertIn("'/reference:System.Windows.Forms.dll')+$compilerSources)", host)
        self.assertNotRegex(host, r'\$(?:automationSource|navigationSource|annexExportSource)=')
        self.assertIn('-TimeoutMilliseconds 30000', host)
        call = host.index('$compilerRun=Invoke-HtkkBoundedCompiler')
        self.assertLess(call, host.index('if(-not $compilerRun.jobCleanupVerified', call))
        self.assertLess(host.index('if(-not $compilerRun.jobCleanupVerified', call),
                        host.index("$safe.status='prepared'", call))

    def test_compilation_does_not_enable_automation_in_launch_only_mode(self):
        host = (ROOT / 'New-HtkkX86ReferenceHost.ps1').read_text()
        self.assertIn('if(automationMode!="none") {', host)
        start = host.index('if(automationMode!="none") {')
        end = host.index('int code=domain.ExecuteAssembly(original)', start)
        self.assertIn('agent.Start(automationMode);', host[start:end])
        self.assertIn('originalExecutableModified=$false; originalConfigurationModified=$false', host)
