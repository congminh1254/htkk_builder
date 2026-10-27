import pathlib
import unittest

ROOT = pathlib.Path(__file__).parent


class UiaProcessContract(unittest.TestCase):
    def test_actual_uia_wrapper_uses_clean_bounded_runner_and_unquoted_arguments(self):
        source = (ROOT / 'probe-htkk-windows.ps1').read_text()
        wrapper = source[source.index('function Get-HtkkSafeUiDiagnostics('):source.index('\ntry {\n  if($GuiAutomation')]
        self.assertIn('$helperRun=Invoke-HtkkBoundedJobProcess -Executable $legacy -WorkingDirectory $TemporaryDirectory -Arguments $arguments -TimeoutMilliseconds 15000', wrapper)
        self.assertNotIn('Start-Process', wrapper)
        self.assertNotIn('Stop-Process', wrapper)
        self.assertIn("'-File',$helper,'-ProcessIds',$ownerList,'-OutputFile',$resultPath", wrapper)
        self.assertIn('.Length -gt 32768', wrapper)

    def test_cleanup_failure_is_monotonic_and_gates_credentials(self):
        source = (ROOT / 'probe-htkk-windows.ps1').read_text()
        self.assertIn('$previousHelpersStopped=$script:uiaHelpersStopped;$script:uiaHelpersStopped=$false', source)
        self.assertIn('$script:uiaHelpersStopped=$previousHelpersStopped -and $diagnostics.helperProcessStopped', source)
        self.assertIn('$credentialsSafe=$installerCredentialsSafe -and $installerStopped -and $uiaHelpersStopped -and ($null -eq $process -or $supplierStopped)', source)

    def test_windows_runs_actual_production_wrapper_scenarios(self):
        workflow = (ROOT.parent / '.github/workflows/probe-htkk-windows.yml').read_text()
        tests = (ROOT / 'Test-HtkkUiaProcessBoundary.ps1').read_text()
        self.assertIn('run: ./scripts/Test-HtkkUiaProcessBoundary.ps1', workflow)
        self.assertIn('Invoke-Expression $definition.Extent.Text', tests)
        self.assertIn("'Get-HtkkSafeUiDiagnostics'", tests)
        self.assertIn("'cleanup','helper-cleanup-not-verified'", tests)
        self.assertIn("'timeout','helper-timeout'", tests)

    def test_phase_diagnostics_precede_blocking_com_calls_and_never_change_login_gate(self):
        source = (ROOT / 'probe-htkk-windows.ps1').read_text()
        self.assertLess(source.index("Set-UiaPhase 'root-enumerating'"), source.index('[System.Windows.Automation.AutomationElement]::RootElement.FindAll'))
        self.assertLess(source.index("Set-UiaPhase 'traversing'"), source.index('while ($queue.Count'))
        self.assertIn("if($phase -cnotin $phases){return 'invalid'}", source)
        self.assertIn('$file.Length -gt 64', source)
        self.assertIn("$diagnostics.status='uia-timeout';$diagnostics.helperFailureCategory='helper-timeout';return $diagnostics", source)
