"""Exhaustive synchronization tests for the HTKK native automation registry.

Checks the generated mode/stage/key names and routing references across
C# source files, PowerShell controllers, and GitHub Actions workflows remain synchronized
with scripts/htkk-native-automation-registry.json.
"""
import ast
import json
import pathlib
import re
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent
REGISTRY_PATH = ROOT / "htkk-native-automation-registry.json"


class NativeAutomationRegistrySyncTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            cls.registry = json.load(f)
        cls.modes = cls.registry["modes"]
        cls.stages = cls.registry["stages"]
        cls.keys = cls.registry["keys"]
        cls.dynamic = cls.registry["dynamicStageMappings"]

    def test_generator_check_passes_with_zero_diff(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "generate-native-automation-registry.py"), "--check"],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0, f"Generator --check failed: {result.stderr}")
        self.assertIn("UP-TO-DATE", result.stdout)

    def test_all_registry_modes_in_csharp_enums_and_wiremaps(self):
        csharp = (ROOT / "HtkkNativeAutomationEnums.cs").read_text(encoding="utf-8")
        self.assertIn("public enum HtkkAutomationMode", csharp)
        for mode_id in self.modes.keys():
            if mode_id == "none":
                enum_name = "None"
            else:
                enum_name = "".join(part.capitalize() for part in mode_id.split("-"))
            self.assertIn(f"case HtkkAutomationMode.{enum_name}: return \"{mode_id}\";", csharp)
            self.assertIn(f'if (wire == "{mode_id}") return HtkkAutomationMode.{enum_name};', csharp)

    def test_all_registry_stages_in_csharp_enums_and_wiremaps(self):
        csharp = (ROOT / "HtkkNativeAutomationEnums.cs").read_text(encoding="utf-8")
        self.assertIn("public enum HtkkAutomationStage", csharp)
        for stage_rec in self.stages:
            s_id = stage_rec["id"]
            s_enum = stage_rec["enumName"]
            self.assertIn(f"case HtkkAutomationStage.{s_enum}: return \"{s_id}\";", csharp)
            self.assertIn(f'if (wire == "{s_id}") return HtkkAutomationStage.{s_enum};', csharp)

    def test_dynamic_mappings_sync(self):
        csharp = (ROOT / "HtkkNativeAutomationEnums.cs").read_text(encoding="utf-8")
        for menu_id, stage_id in self.dynamic["menuClicks"].items():
            self.assertIn(f'if (menuId == "{menu_id}") return HtkkAutomationStage.', csharp)
        for action in ("FocusWaiting", "FocusTimeout", "KeyboardEditing", "KeyboardFocused", "KeyboardSelected", "KeyboardTyped"):
            self.assertIn(f"case HtkkFilenameDialogAction.{action}:", csharp)

    def test_all_modes_in_powershell_controllers(self):
        all_modes = list(self.modes.keys())
        automation_modes = [m for m in all_modes if m != "none"]

        # 1. New-HtkkX86ReferenceHost.ps1
        host = (ROOT / "New-HtkkX86ReferenceHost.ps1").read_text(encoding="utf-8")
        host_modes = re.search(r"\[ValidateSet\(([^\)]+)\)\]\[string\]\$GuiAutomation='none'", host).group(1)
        host_set = {m.strip().strip("'") for m in host_modes.split(",")}
        self.assertEqual(host_set, set(all_modes))

        # 2. Get-HtkkSafeGuiReferenceResult.ps1
        reader = (ROOT / "Get-HtkkSafeGuiReferenceResult.ps1").read_text(encoding="utf-8")
        reader_modes = re.search(r"\[ValidateSet\(([^\)]+)\)\]\[string\]\$ExpectedMode", reader).group(1)
        reader_set = {m.strip().strip("'") for m in reader_modes.split(",")}
        self.assertEqual(reader_set, set(automation_modes))

        # 3. probe-htkk-windows.ps1
        probe = (ROOT / "probe-htkk-windows.ps1").read_text(encoding="utf-8")
        probe_modes = re.search(r"\[ValidateSet\(([^\)]+)\)\]\[string\]\$GuiAutomation='none'", probe).group(1)
        probe_set = {m.strip().strip("'") for m in probe_modes.split(",")}
        self.assertEqual(probe_set, set(all_modes))

    def test_all_stages_and_keys_in_safe_reader(self):
        reader = (ROOT / "Get-HtkkSafeGuiReferenceResult.ps1").read_text(encoding="utf-8")
        # Check keys
        reader_keys = re.search(r"\$keys=@\(([^\)]+)\)", reader).group(1)
        keys_set = [k.strip().strip("'") for k in reader_keys.split(",")]
        self.assertEqual(len(keys_set), len(self.keys))
        self.assertEqual(set(keys_set), set(self.keys))

        # Check stages
        reader_stages = re.search(r"\$stages=@\(([^\)]+)\)", reader).group(1)
        stages_set = [s.strip().strip("'") for s in reader_stages.split(",")]
        expected_stage_ids = [s["id"] for s in self.stages]
        self.assertEqual(len(stages_set), len(expected_stage_ids))
        self.assertEqual(set(stages_set), set(expected_stage_ids))

    def test_all_terminal_stages_in_probe_matcher(self):
        probe = (ROOT / "probe-htkk-windows.ps1").read_text(encoding="utf-8")
        term_match = re.search(r"\$terminal=\$nextGui\.failureCategory -ne 'none' -or \$nextGui\.stage -in @\(([^\)]+)\)", probe).group(1)
        terminal_in_probe = {s.strip().strip("'") for s in term_match.split(",")}
        for mode_meta in self.modes.values():
            term = mode_meta.get("terminalStage")
            if term and term != "not-started" and term != "profile-inspected":
                self.assertIn(term, terminal_in_probe)

    def test_workflow_options_and_guard_sync(self):
        workflow = (ROOT.parent / ".github/workflows/probe-htkk-windows.yml").read_text(encoding="utf-8")
        options = re.search(r"options: \[([^\n\]]+)\]", workflow).group(1)
        declared_options = {item.strip() for item in options.split(",")}
        self.assertEqual(declared_options, set(self.modes.keys()))

        guard = re.search(r"if \(\$guiAutomation -notin @\(([^\n\)]+)\)\)", workflow).group(1)
        verified_guard = {item.strip().strip("'") for item in guard.split(",")}
        self.assertEqual(verified_guard, set(self.modes.keys()))

    def test_compiler_inputs_for_all_modes_are_existing_files(self):
        for mode_id, meta in self.modes.items():
            inputs = meta.get("orderedCompileInputs", [])
            for filename in inputs:
                self.assertTrue((ROOT / filename).exists(), f"Compiler input {filename} for mode {mode_id} does not exist!")


if __name__ == "__main__":
    unittest.main()

class NativeAutomationRegistryRejectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import importlib.util
        spec = importlib.util.spec_from_file_location('native_registry_review', ROOT / 'generate-native-automation-registry.py')
        cls.generator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.generator)
        cls.registry = json.loads(REGISTRY_PATH.read_text())

    def mutated(self, mutate):
        import copy
        data = copy.deepcopy(self.registry)
        mutate(data)
        with self.assertRaises(ValueError):
            self.generator.validate_registry(data)

    def test_rejects_unknown_properties(self):
        self.mutated(lambda r: r.update(unreviewed=True))
        self.mutated(lambda r: r['modes']['inspect'].update(unreviewed=True))

    def test_rejects_unknown_references(self):
        self.mutated(lambda r: r['modes']['inspect'].update(terminalStage='unknown-stage'))
        self.mutated(lambda r: r['modes']['inspect'].update(successPolicyId='unknown-policy'))
        self.mutated(lambda r: r['modes']['inspect'].update(adapterId='sample-adapter'))
        self.mutated(lambda r: r['modes']['inspect'].update(contextPolicy='htkk-native/sample'))
        self.mutated(lambda r: r['dynamicStageMappings']['menuClicks'].update(D1='unknown-stage'))

    def test_rejects_unsafe_tokens_and_duplicate_ids(self):
        self.mutated(lambda r: r['stages'][0].update(id="'; injected"))
        self.mutated(lambda r: r['stages'].append(dict(r['stages'][0])))
        self.mutated(lambda r: r['keys'].append(r['keys'][0]))
        self.mutated(lambda r: r['modes']['inspect'].update(orderedCompileInputs=['../outside.cs']))

    def test_rejects_wrong_types_and_bounds(self):
        self.mutated(lambda r: r['modes']['inspect'].update(login='true'))
        for bad in (True, 0, -1, 181, '120'):
            self.mutated(lambda r: r['modes']['inspect'].update(timeoutSeconds=bad))

    def test_rejects_duplicate_json_properties(self):
        with self.assertRaises(ValueError):
            json.loads('{"mode":1,"mode":2}', object_pairs_hook=self.generator.unique_object)

    def test_missing_or_ambiguous_integration_anchor_fails(self):
        for content in ('missing', 'anchor anchor'):
            with self.assertRaises(ValueError):
                self.generator.replace_exact('anchor', 'replacement', content)

    def test_adapter_dispatch_facade_is_accessible_and_fail_closed(self):
        navigation = (ROOT / 'HtkkGtgtReferenceNavigation.cs').read_text()
        self.assertIn('internal void ContinueGtgtNavigation()', navigation)
        self.assertIn('internal string NavigationJson()', navigation)
        self.assertIn('if(harnessInstance==null||!CanHandle(mode))throw new ArgumentException();', navigation)
        self.assertNotIn('HtkkSampleAdapter', (ROOT / 'HtkkGuiReferenceAutomation.cs').read_text())
        self.assertFalse((ROOT / 'HtkkSampleAdapter.cs').exists())
        self.assertFalse((ROOT / 'publish-sample-roundtrip-evidence.py').exists())
