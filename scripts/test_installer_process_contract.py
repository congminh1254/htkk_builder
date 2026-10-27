import pathlib
import unittest

ROOT = pathlib.Path(__file__).parent


class InstallerProcessContract(unittest.TestCase):
    def test_original_installer_arguments_and_verification_precede_bounded_execution(self):
        source = (ROOT / 'probe-htkk-windows.ps1').read_text()
        invocation = source.index('$install=Invoke-HtkkBoundedNativeProcess')
        self.assertLess(source.index("$report.msiAuthenticodeValid = $true"), invocation)
        self.assertIn("@('/i',$msi,'/qn','/norestart','ISCHECKFORPRODUCTUPDATES=0','/L*v',(Join-Path $work 'install-private.log')) -TimeoutMilliseconds 180000", source)
        self.assertNotIn('$install = Start-Process', source)
        self.assertIn("if($install.exitCode -eq 3010){throw 'REBOOT_REQUIRED_PROBE_NOT_RUN'}", source)

    def test_unverified_installer_stop_blocks_publication_credentials(self):
        source = (ROOT / 'probe-htkk-windows.ps1').read_text()
        self.assertIn('$installerStopped=$install.processStopped', source)
        self.assertIn("if(-not $installerStopped){throw 'MSI_PROCESS_NOT_STOPPED'}", source)
        self.assertIn('$credentialsSafe=$installerStopped -and $uiaHelpersStopped -and ($null -eq $process -or $supplierStopped)', source)
        for code in ('MSI_INSTALL_TIMEOUT', 'MSI_PROCESS_NOT_STOPPED'):
            self.assertGreaterEqual(source.count("'" + code + "'"), 2)

    def test_actual_process_boundary_tests_run_in_windows_workflow(self):
        workflow = (ROOT.parent / '.github/workflows/probe-htkk-windows.yml').read_text()
        test = (ROOT / 'Test-HtkkBoundedNativeProcess.ps1').read_text()
        self.assertIn('run: ./scripts/Test-HtkkBoundedNativeProcess.ps1', workflow)
        self.assertIn(". (Join-Path $PSScriptRoot 'Invoke-HtkkBoundedNativeProcess.ps1')", test)
        self.assertIn("$Mode -eq 'hang'", test)
        self.assertIn("if(Get-Process -Id $childId", test)
