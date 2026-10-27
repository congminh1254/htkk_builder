import pathlib
import unittest

ROOT = pathlib.Path(__file__).parent


class FrameworkUiaLoadContract(unittest.TestCase):
    def test_actual_framework_child_bypasses_cmdlet_autoload_and_pins_identities(self):
        source = (ROOT / 'Test-HtkkFrameworkUiaAssemblyLoad.ps1').read_text()
        child = source.split(" @'\n", 1)[1].split("\n'@", 1)[0]
        self.assertNotIn('Add-Type', child)
        self.assertNotIn('Import-Module', child)
        for name in ('UIAutomationClient', 'UIAutomationTypes'):
            self.assertIn(f"{name}, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35", child)
        self.assertIn('$client=[Reflection.Assembly]::Load($clientIdentity)', child)
        self.assertIn('$types=[Reflection.Assembly]::Load($typesIdentity)', child)
        self.assertIn("$client.GetType('System.Windows.Automation.AutomationElement',$false)", child)
        self.assertIn("$types.GetType('System.Windows.Automation.ControlType',$false)", child)

    def test_real_clean_runner_enforces_deadline_and_termination(self):
        source = (ROOT / 'Test-HtkkFrameworkUiaAssemblyLoad.ps1').read_text()
        self.assertIn(". (Join-Path $PSScriptRoot 'Invoke-HtkkBoundedNativeProcess.ps1')", source)
        self.assertIn('Invoke-HtkkBoundedNativeProcess -Executable $legacy', source)
        self.assertIn('-TimeoutMilliseconds 15000', source)
        self.assertIn('-not $run.processStopped', source)
        self.assertIn('$clock.Elapsed.TotalMilliseconds -gt 15000', source)
        self.assertIn('no Windows readiness proven', source)
        for forbidden in ('RootElement', 'FindAll', 'HTKK.exe', 'SOURCE_READ_TOKEN'):
            self.assertNotIn(forbidden, source)

    def test_same_framework_child_exercises_remaining_uia_cmdlets_on_fixed_data(self):
        source = (ROOT / 'Test-HtkkFrameworkUiaAssemblyLoad.ps1').read_text()
        child = source.split(" @'\n", 1)[1].split("\n'@", 1)[0]
        self.assertIn('$sorted=@(@(3,1,2)|Sort-Object)', child)
        self.assertIn('$fixture|ConvertTo-Json -Depth 4', child)
        self.assertIn('$fixtureJson|Set-Content -LiteralPath $fixturePath -Encoding UTF8', child)
        for flag in ('sortObjectMatched', 'jsonSerializationMatched', 'setContentMatched'):
            self.assertIn(f"'{flag}'", source)
            self.assertIn(f'${flag}.ToString().ToLowerInvariant()', child)
        self.assertIn("'FRAMEWORK_UIA_CMDLET_FIXTURE_INVALID'", source)
        self.assertIn("'FRAMEWORK_UIA_CMDLET_SORT_NOT_VERIFIED'", source)
