import pathlib
import unittest

ROOT = pathlib.Path(__file__).parent


class BoundedCompilerContract(unittest.TestCase):
    def test_all_compilers_use_same_bounded_capture_without_pipe_waits(self):
        for name in ('Test-HtkkTaxIdOracle.ps1', 'Test-HtkkProfileAliasOracle.ps1',
                     'Test-HtkkCommonHeaderOracle.ps1', 'New-HtkkX86ReferenceHost.ps1'):
            with self.subTest(name=name):
                source = (ROOT / name).read_text()
                invocation = source.index('$compilerRun=Invoke-HtkkBoundedCompiler')
                cleanup_gate = source.index('if(-not $compilerRun.jobCleanupVerified', invocation)
                prepared_check = source.index('if($safe.compilerExitCode -ne 0', invocation)
                self.assertLess(invocation, cleanup_gate)
                self.assertLess(cleanup_gate, prepared_check)
                self.assertIn('-TimeoutMilliseconds 30000', source[invocation:cleanup_gate])
                self.assertIn('$safe.compilerErrorCodes=$compilerRun.compilerErrorCodes', source)
                self.assertNotIn('GetAwaiter', source)
                self.assertNotIn('ReadToEndAsync', source)
                self.assertNotIn('$compilerProcess', source)
                self.assertIn("$safe.status='compile-timeout'", source)

    def test_capture_has_size_limit_cleanup_gate_and_actual_behavioral_tests(self):
        source = (ROOT / 'Invoke-HtkkBoundedCompiler.ps1').read_text()
        tests = (ROOT / 'Test-HtkkBoundedCompiler.ps1').read_text()
        self.assertIn('[ValidateRange(1,1048576)]', source)
        self.assertIn('if($stream.Length -gt $MaximumBytes)', source)
        self.assertIn("$safe.status -eq 'exited' -and $safe.jobCleanupVerified", source)
        self.assertEqual(source.count('$owner.Dispose()'), 1)
        self.assertNotIn('$owner.Stop(', source)
        self.assertNotIn('GetAwaiter', source)
        self.assertIn("'\\bCS[0-9]{4}\\b'", source)
        self.assertIn('Select-Object -First 10', source)
        self.assertIn('$previousHelpersStopped -and $safe.jobCleanupVerified', source)
        for marker in ('Actual compiler diagnostic capture failed', 'Compiler output was read before verified cleanup',
                       "$script:fixture -eq 'oversize'", "$script:fixture -eq 'limit'",
                       'Later compiler success erased unsafe cleanup'):
            self.assertIn(marker, tests)
        self.assertIn('CS1525', tests)
        self.assertIn('Win32 integration NOT RUN', tests)
