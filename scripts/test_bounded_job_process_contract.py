import pathlib
import unittest

ROOT = pathlib.Path(__file__).parent


class BoundedJobProcessContract(unittest.TestCase):
    def test_wrapper_has_single_cleanup_deadline_and_no_output_pipe(self):
        source = (ROOT / 'Invoke-HtkkBoundedJobProcess.ps1').read_text()
        self.assertIn('[ValidateRange(100,30000)]', source)
        self.assertIn('$owner.WaitForRootExit($TimeoutMilliseconds)', source)
        self.assertEqual(source.count('$owner.Dispose()'), 1)
        self.assertNotIn('$owner.Stop(', source)
        self.assertNotIn('ReadToEnd', source)
        self.assertNotIn('GetAwaiter', source)
        self.assertIn('$script:htkkHelperJobsStopped=$false', source)
        self.assertIn('$previousHelpersStopped -and $safe.jobCleanupVerified', source)

    def test_test_exercises_actual_wrapper_with_orphan_timeout_and_sentinel(self):
        source = (ROOT / 'Test-HtkkBoundedJobProcess.ps1').read_text()
        self.assertIn("'Invoke-HtkkBoundedJobProcess.ps1'", source)
        self.assertIn('Set-Item Function:New-HtkkBoundedJobOwner $productionFactory', source)
        self.assertIn("$Mode -eq 'spawn'", source)
        self.assertIn("$Mode -eq 'hang'", source)
        self.assertIn('HTKK_TEST_FAKE_CREDENTIAL', source)
        self.assertIn('if(Get-Process -Id $childId', source)
        self.assertIn("Win32 process integration NOT RUN", source)

    def test_oracle_results_are_read_only_after_job_cleanup_and_compiler_diagnostics_remain(self):
        for name in ('Test-HtkkTaxIdOracle.ps1', 'Test-HtkkProfileAliasOracle.ps1',
                     'Test-HtkkCommonHeaderOracle.ps1'):
            with self.subTest(name=name):
                source = (ROOT / name).read_text()
                invocation = source.index('$oracleRun=Invoke-HtkkBoundedJobProcess')
                cleanup_gate = source.index('if(-not $oracleRun.jobCleanupVerified', invocation)
                result_read = source.index('ConvertFrom-Json', invocation)
                self.assertLess(invocation, cleanup_gate)
                self.assertLess(cleanup_gate, result_read)
                self.assertNotIn('$oracleProcess', source)
                self.assertNotIn('$oracleOut', source)
                self.assertNotIn('$oracleErr', source)
                self.assertIn('Invoke-HtkkBoundedCompiler -Executable $compiler', source)
                self.assertIn('$safe.compilerErrorCodes=$compilerRun.compilerErrorCodes', source)
                self.assertIn("$safe.status='oracle-timeout'", source)
