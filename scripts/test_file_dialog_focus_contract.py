import pathlib
import unittest

ROOT = pathlib.Path(__file__).parent


class FileDialogFocusContract(unittest.TestCase):
    def test_readiness_precedes_keyboard_and_submission_is_the_only_reset(self):
        source = (ROOT / 'HtkkGtgtExportInspection.cs').read_text()
        begin = source.index('filenameFocusGate.Begin()')
        first_input = source.index('SendKeys.SendWait("^a")')
        self.assertLess(source.index('filenameFocusGate.Observe(dialog,edit,ownsFocus)'), begin)
        self.assertLess(begin, first_input)
        self.assertEqual(source.count('filenameFocusGate.ResetAfterSubmission()'), 1)
        self.assertIn('if(!PostMessage(save,245,IntPtr.Zero,IntPtr.Zero))throw new InvalidOperationException();filenameFocusGate.ResetAfterSubmission();', source)
        self.assertIn('if(!ownsFocus){SetForegroundWindow(dialog);SetFocus(edit);}return false;', source)
        self.assertIn('if(inputStarted||currentDialog==IntPtr.Zero||currentEditor==IntPtr.Zero)', source)
        self.assertIn('if(dialog!=currentDialog||editor!=currentEditor)', source)

    def test_all_diagnostics_are_bounded_and_covered_by_actual_reader_tests(self):
        source = (ROOT / 'HtkkGtgtExportInspection.cs').read_text()
        reader = (ROOT / 'Get-HtkkSafeGuiReferenceResult.ps1').read_text()
        tests = (ROOT / 'Test-HtkkSafeGuiReferenceResult.ps1').read_text()
        for action in ('export', 'import'):
            self.assertIn(f'"gtgt-{action}-filename-"', source)
            for stage in ('focus-waiting', 'focus-timeout', 'keyboard-focused', 'keyboard-selected', 'keyboard-typed'):
                self.assertIn(f'"{stage}"', source)
                self.assertIn(f"'gtgt-{action}-filename-{stage}'", reader)
                self.assertIn(f"'gtgt-{action}-filename-{stage}'", tests)

    def test_behavioral_tests_compile_production_policy_and_run_in_boundary_suite(self):
        policy_test = (ROOT / 'Test-HtkkFileDialogFocusPolicy.ps1').read_text()
        boundary = (ROOT / 'Test-HtkkSafeGuiReferenceResult.ps1').read_text()
        self.assertIn("'HtkkGtgtExportInspection.cs'", policy_test)
        self.assertIn('Add-Type -TypeDefinition', policy_test)
        self.assertIn('$source.Substring($offset)', policy_test)
        self.assertIn("'Test-HtkkFileDialogFocusPolicy.ps1'", boundary)
        self.assertNotIn('public sealed class HtkkFileDialogFocusGate', policy_test)
