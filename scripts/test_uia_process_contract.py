import pathlib
import unittest

ROOT = pathlib.Path(__file__).parent


class UiaProcessContract(unittest.TestCase):
    def test_actual_uia_wrapper_uses_clean_bounded_runner_and_unquoted_arguments(self):
        source = (ROOT / 'probe-htkk-windows.ps1').read_text()
        wrapper = source[source.index('function Get-HtkkSafeUiDiagnostics('):source.index('\ntry {\n  if($GuiAutomation')]
        self.assertIn('$helperRun=Invoke-HtkkBoundedNativeProcess -Executable $legacy -WorkingDirectory $TemporaryDirectory -Arguments $arguments -TimeoutMilliseconds 15000', wrapper)
        self.assertNotIn('Start-Process', wrapper)
        self.assertNotIn('Stop-Process', wrapper)
        self.assertIn("'-File',$helper,'-ProcessIds',$ownerList,'-OutputFile',$resultPath", wrapper)
        self.assertIn('.Length -gt 32768', wrapper)

    def test_cleanup_failure_is_monotonic_and_gates_credentials(self):
        source = (ROOT / 'probe-htkk-windows.ps1').read_text()
        self.assertIn('$previousHelpersStopped=$script:uiaHelpersStopped;$script:uiaHelpersStopped=$false', source)
        self.assertIn('$script:uiaHelpersStopped=$previousHelpersStopped -and $diagnostics.helperProcessStopped', source)
        self.assertIn('$credentialsSafe=$installerStopped -and $uiaHelpersStopped -and ($null -eq $process -or $supplierStopped)', source)

    def test_windows_runs_actual_production_wrapper_scenarios(self):
        workflow = (ROOT.parent / '.github/workflows/probe-htkk-windows.yml').read_text()
        tests = (ROOT / 'Test-HtkkUiaProcessBoundary.ps1').read_text()
        self.assertIn('run: ./scripts/Test-HtkkUiaProcessBoundary.ps1', workflow)
        self.assertIn('Invoke-Expression $definition.Extent.Text', tests)
        self.assertIn("'Get-HtkkSafeUiDiagnostics'", tests)
        self.assertIn("'cleanup','helper-cleanup-not-verified'", tests)
        self.assertIn("'timeout','helper-timeout'", tests)
