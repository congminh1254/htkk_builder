import pathlib
import unittest

ROOT = pathlib.Path(__file__).parent


class PinnedDownloadContract(unittest.TestCase):
    def test_actual_download_owns_retry_count_and_preserves_tls_verification(self):
        helper = (ROOT / 'Invoke-HtkkPinnedDownload.ps1').read_text()
        self.assertIn('-TimeoutSec $TimeoutSeconds -MaximumRedirection 8 -MaximumRetryCount 0', helper)
        self.assertIn('for($attempt=1;$attempt -le 2;$attempt++)', helper)
        self.assertIn('-not $failure.retryable -or $attempt -eq 2', helper)
        for forbidden in ('SkipCertificateCheck', 'ServerCertificateValidationCallback', 'Exception.Message', '.ToString()', 'Write-Host', 'Write-Output'):
            self.assertNotIn(forbidden, helper)

    def test_hash_failure_is_nonretryable_and_partial_cleanup_precedes_retry(self):
        helper = (ROOT / 'Invoke-HtkkPinnedDownload.ps1').read_text()
        self.assertIn("category='hash';httpStatus=$null;retryable=$false", helper)
        self.assertIn('if(Test-Path -LiteralPath $Destination){return $safe}', helper)
        self.assertLess(helper.index('Remove-Item -LiteralPath $Destination -Force'), helper.index('-not $failure.retryable -or $attempt -eq 2'))

    def test_behavioral_suite_executes_production_helper_without_network(self):
        tests = (ROOT / 'Test-HtkkPinnedDownload.ps1').read_text()
        self.assertIn(". (Join-Path $PSScriptRoot 'Invoke-HtkkPinnedDownload.ps1')", tests)
        self.assertIn('-Downloader $downloader', tests)
        self.assertIn("@('http-recover',2,'verified','none')", tests)
        self.assertIn("@('auth',1,'failed','http')", tests)
        self.assertIn("@('tls',1,'failed','tls')", tests)
        self.assertIn("@('hash',1,'failed','hash')", tests)
        self.assertNotIn('Invoke-WebRequest', tests)

    def test_optional_http_exception_type_never_requires_utility_to_be_loaded(self):
        helper = (ROOT / 'Invoke-HtkkPinnedDownload.ps1').read_text()
        self.assertNotIn('[Microsoft.PowerShell.Commands.HttpResponseException]', helper)
        self.assertIn("'Microsoft.PowerShell.Commands.HttpResponseException' -as [type]", helper)
        self.assertIn('$null -ne $httpResponseExceptionType -and $httpResponseExceptionType.IsInstanceOfType($errorItem)', helper)

    def test_main_download_suite_runs_isolated_cold_process_regression(self):
        tests = (ROOT / 'Test-HtkkPinnedDownload.ps1').read_text()
        self.assertIn("& (Join-Path $PSScriptRoot 'Test-HtkkPinnedDownloadColdProcess.ps1')", tests)
        cold = (ROOT / 'Test-HtkkPinnedDownloadColdProcess.ps1').read_text()
        self.assertIn("$PSModuleAutoloadingPreference='None'", cold)
        self.assertIn("$start.Environment.Clear()", cold)
        self.assertIn("$process.WaitForExit(20000)", cold)
        self.assertIn("$process.Kill($true)", cold)
        self.assertIn("'Microsoft.PowerShell.Utility','Microsoft.PowerShell.Utility.psd1'", cold)
        self.assertIn("Get-HtkkDownloadFailure -Exception $case[0]", cold)
        self.assertIn("Get-HtkkDownloadFailure -Exception $errorItem", cold)
        self.assertNotIn('Invoke-WebRequest', cold)
        self.assertNotIn('Exception.Message', cold)
