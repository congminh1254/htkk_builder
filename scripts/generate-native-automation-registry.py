#!/usr/bin/env python3
"""Validated wire-name registry generator for the HTKK native harness foundation.

Generates CLR2-compatible C# enums & wire mappings, and synchronizes PowerShell contracts,
workflow choice guards, and terminal stage matchers with scripts/htkk-native-automation-registry.json.
Supports --check to fail if any file is out of sync.
"""
import argparse
import difflib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent
REGISTRY_PATH = ROOT / "htkk-native-automation-registry.json"


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate registry property")
        result[key] = value
    return result


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_registry(registry):
    """Validate data before interpolating it into C#, PowerShell or YAML.

    This registry describes routing and wire names only. The reviewed PowerShell
    reader still owns field types/ranges/defaults and business success predicates.
    """
    top = {"format", "version", "modes", "stages", "dynamicStageMappings", "keys", "controlKinds", "periodControls"}
    require(type(registry) is dict and set(registry) == top, "Invalid registry properties")
    require(registry["format"] == "htkk-native-automation-registry-v1" and registry["version"] == "1.0.0", "Unsupported registry version")
    modes, stages = registry["modes"], registry["stages"]
    require(type(modes) is dict and 1 <= len(modes) <= 64, "Invalid mode collection")
    require(type(stages) is list and 1 <= len(stages) <= 512, "Invalid stage collection")
    safe_wire = lambda x: type(x) is str and re.fullmatch(r"[A-Za-z0-9_]+(?:-[A-Za-z0-9_]+)*", x) is not None
    safe_name = lambda x: type(x) is str and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", x) is not None
    stage_ids, enum_names = set(), set()
    categories = {"sheet", "menu", "annex12", "export-roundtrip", "lifecycle", "period", "amendment"}
    for stage in stages:
        require(type(stage) is dict and set(stage) == {"id", "enumName", "category"}, "Invalid stage properties")
        require(safe_wire(stage["id"]) and safe_name(stage["enumName"]) and stage["category"] in categories, "Invalid stage token")
        require(stage["id"] not in stage_ids and stage["enumName"] not in enum_names, "Duplicate stage identity")
        stage_ids.add(stage["id"])
        enum_names.add(stage["enumName"])
    mode_fields = {"adapterId", "runtime", "login", "permit", "terminalStage", "timeoutSeconds", "orderedCompileInputs", "successPolicyId", "privateArtifactPolicy", "contextPolicy"}
    seen_mode_enums = set()
    artifact_policies = {"none", "raw-annex12-export", "raw-gtgt-export", "raw-web-reexport", "synthetic-common-header", "synthetic-window-diagnostic"}
    success_policies = stage_ids | {"none", "gtgt-amendment-saved"}
    for mode, meta in modes.items():
        require(safe_wire(mode) and type(meta) is dict and set(meta) == mode_fields, "Invalid mode properties")
        mode_enum = "".join(part.capitalize() for part in mode.split("-"))
        require(safe_name(mode_enum) and mode_enum not in seen_mode_enums, "Duplicate mode enum")
        seen_mode_enums.add(mode_enum)
        require(meta["adapterId"] in {"none", "profile", "d1-gtgt"}, "Unknown adapter")
        require(meta["runtime"] in {"none", "clr2-x86-custom-reference"}, "Unknown runtime")
        require(type(meta["login"]) is bool and meta["permit"] in (None, "profile-save"), "Invalid login/permit")
        require(meta["terminalStage"] in stage_ids and meta["successPolicyId"] in success_policies, "Unknown success stage/policy")
        require(type(meta["timeoutSeconds"]) is int and 1 <= meta["timeoutSeconds"] <= 180, "Invalid timeout")
        require(meta["privateArtifactPolicy"] in artifact_policies and meta["contextPolicy"] in {"none", "htkk-native/case"}, "Unknown artifact/context policy")
        inputs = meta["orderedCompileInputs"]
        require(type(inputs) is list and len(inputs) <= 32 and len(set(inputs)) == len(inputs), "Invalid compile inputs")
        for name in inputs:
            require(type(name) is str and re.fullmatch(r"Htkk[A-Za-z0-9]+\.cs", name) is not None and (ROOT / name).is_file(), "Invalid compile input")
        if mode == "none":
            require(meta["runtime"] == "none" and not meta["login"] and not inputs and meta["permit"] is None, "Invalid launch-only policy")
        else:
            require(meta["runtime"] == "clr2-x86-custom-reference" and meta["login"] and bool(inputs), "Invalid automation policy")
    require("none" in modes, "Missing launch-only mode")
    for key in ("keys", "controlKinds", "periodControls"):
        values = registry[key]
        require(type(values) is list and bool(values) and all(safe_name(x) for x in values) and len(values) == len(set(values)), "Invalid or duplicate allowlist entries")
    require(set(registry["controlKinds"]) == {"form", "button", "combo", "text", "spread", "other"}, "Invalid control kinds")
    dynamic = registry["dynamicStageMappings"]
    require(type(dynamic) is dict and set(dynamic) == {"menuClicks", "filenameDialog"}, "Invalid dynamic maps")
    menus = dynamic["menuClicks"]
    require(type(menus) is dict and set(menus) == {"101", "101_1", "D1"}, "Invalid menu mapping")
    require(all(s in stage_ids for s in menus.values()), "Unknown menu stage")
    filenames = dynamic["filenameDialog"]
    require(type(filenames) is dict and set(filenames) == {"import", "export"}, "Invalid filename maps")
    actions = {"focus-waiting", "focus-timeout", "keyboard-editing", "keyboard-focused", "keyboard-selected", "keyboard-typed"}
    for mapping in filenames.values():
        require(type(mapping) is dict and set(mapping) == actions and all(s in stage_ids for s in mapping.values()), "Invalid filename mapping")
    return registry


def load_registry():
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        return validate_registry(json.load(f, object_pairs_hook=unique_object))


def replace_exact(pattern, replacement, content):
    content, count = re.subn(pattern, lambda match: replacement, content)
    require(count == 1, "Generated integration anchor missing or ambiguous")
    return content


def generate_csharp_enums(registry):
    modes = registry["modes"]
    stages = registry["stages"]
    dynamic = registry["dynamicStageMappings"]

    # Enum HtkkAutomationMode
    mode_entries = []
    mode_to_wire = []
    wire_to_mode = []
    for mode_id, meta in modes.items():
        # CamelCase
        if mode_id == "none":
            enum_name = "None"
        else:
            enum_name = "".join(part.capitalize() for part in mode_id.split("-"))
        mode_entries.append(f"  {enum_name}")
        mode_to_wire.append(f'   case HtkkAutomationMode.{enum_name}: return "{mode_id}";')
        wire_to_mode.append(f'   if (wire == "{mode_id}") return HtkkAutomationMode.{enum_name};')

    # Enum HtkkAutomationStage
    stage_entries = []
    stage_to_wire = []
    wire_to_stage = []
    for stage_rec in stages:
        s_id = stage_rec["id"]
        s_enum = stage_rec["enumName"]
        stage_entries.append(f"  {s_enum}")
        stage_to_wire.append(f'   case HtkkAutomationStage.{s_enum}: return "{s_id}";')
        wire_to_stage.append(f'   if (wire == "{s_id}") return HtkkAutomationStage.{s_enum};')

    # Filename mappings
    fn_map = dynamic["filenameDialog"]
    fn_cases_import = []
    fn_cases_export = []
    action_enum_map = {
        "focus-waiting": "FocusWaiting",
        "focus-timeout": "FocusTimeout",
        "keyboard-editing": "KeyboardEditing",
        "keyboard-focused": "KeyboardFocused",
        "keyboard-selected": "KeyboardSelected",
        "keyboard-typed": "KeyboardTyped",
    }
    stage_id_to_enum = {s["id"]: s["enumName"] for s in stages}

    for action_key, stage_id in fn_map["import"].items():
        action_name = action_enum_map[action_key]
        stage_enum = stage_id_to_enum[stage_id]
        fn_cases_import.append(f"    case HtkkFilenameDialogAction.{action_name}: return HtkkAutomationStage.{stage_enum};")

    for action_key, stage_id in fn_map["export"].items():
        action_name = action_enum_map[action_key]
        stage_enum = stage_id_to_enum[stage_id]
        fn_cases_export.append(f"    case HtkkFilenameDialogAction.{action_name}: return HtkkAutomationStage.{stage_enum};")

    # Menu click mappings
    menu_cases = []
    for menu_id, stage_id in dynamic["menuClicks"].items():
        stage_enum = stage_id_to_enum[stage_id]
        menu_cases.append(f'   if (menuId == "{menu_id}") return HtkkAutomationStage.{stage_enum};')

    code = [
        "// Auto-generated by generate-native-automation-registry.py. Do not edit manually.",
        "// Strictly CLR2 / C# 2.0 compatible for x86 Windows automation host.",
        "using System;",
        "using System.Windows.Forms;",
        "",
        "public interface IHtkkNativeAutomationAdapter {",
        "  string AdapterId { get; }",
        "  bool CanHandle(HtkkAutomationMode mode);",
        "  void Initialize(HtkkGuiReferenceAutomation harness, string project, HtkkAutomationMode mode);",
        "  void OnProfileSaved(Form profileOwner, Button closeButton, Control spread);",
        "  void ContinueNavigation();",
        "  string BuildNavigationJson();",
        "}",
        "",
        "public enum HtkkAutomationMode {",
        ",\n".join(mode_entries),
        "}",
        "",
        "public enum HtkkAutomationStage {",
        ",\n".join(stage_entries),
        "}",
        "",
        "public enum HtkkFilenameDialogAction {",
        "  FocusWaiting,",
        "  FocusTimeout,",
        "  KeyboardEditing,",
        "  KeyboardFocused,",
        "  KeyboardSelected,",
        "  KeyboardTyped",
        "}",
        "",
        "public static class HtkkNativeAutomationWireMap {",
        " public static string ToWireString(HtkkAutomationMode mode) {",
        "  switch (mode) {",
        "\n".join(mode_to_wire),
        '   default: throw new ArgumentException("Unknown automation mode");',
        "  }",
        " }",
        " public static HtkkAutomationMode ParseMode(string wire) {",
        "\n".join(wire_to_mode),
        '  throw new ArgumentException("Unknown automation mode");',
        " }",
        " public static string ToWireString(HtkkAutomationStage stage) {",
        "  switch (stage) {",
        "\n".join(stage_to_wire),
        '   default: throw new ArgumentException("Unknown automation stage");',
        "  }",
        " }",
        " public static HtkkAutomationStage ParseStage(string wire) {",
        "\n".join(wire_to_stage),
        '  throw new ArgumentException("Unknown automation stage");',
        " }",
        " public static HtkkAutomationStage GetFilenameStage(bool opening, HtkkFilenameDialogAction action) {",
        "  if (opening) {",
        "   switch (action) {",
        "\n".join(fn_cases_import),
        '    default: throw new ArgumentException("Unknown filename action");',
        "   }",
        "  } else {",
        "   switch (action) {",
        "\n".join(fn_cases_export),
        '    default: throw new ArgumentException("Unknown filename action");',
        "   }",
        "  }",
        " }",
        " public static HtkkAutomationStage GetMenuClickStage(string menuId) {",
        "\n".join(menu_cases),
        '  throw new ArgumentException("Unknown menu ID for click stage");',
        " }",
        "}",
        ""
    ]
    return "\n".join(code)


def sync_powershell_and_workflow(registry, check_mode=False):
    modes = registry["modes"]
    stages = [s["id"] for s in registry["stages"]]
    keys = registry["keys"]

    all_mode_ids = list(modes.keys())
    # PS expected modes (excluding 'none')
    automation_mode_ids = [m for m in all_mode_ids if m != "none"]

    # Files to update
    updates = {}

    # 1. scripts/Get-HtkkSafeGuiReferenceResult.ps1
    ps_safe_path = ROOT / "Get-HtkkSafeGuiReferenceResult.ps1"
    content = ps_safe_path.read_text(encoding="utf-8")

    # Replace ValidateSet for ExpectedMode
    new_validate = "[ValidateSet(" + ",".join(f"'{m}'" for m in automation_mode_ids) + ")][string]$ExpectedMode"
    content = replace_exact(r"\[ValidateSet\([^\)]+\)\]\[string\]\$ExpectedMode", new_validate, content)

    # Replace $keys=@(...)
    new_keys = "$keys=@(" + ",".join(f"'{k}'" for k in keys) + ")"
    content = replace_exact(r"\$keys=@\([^\)]+\)", new_keys, content)

    # Replace $stages=@(...)
    new_stages = "$stages=@(" + ",".join(f"'{s}'" for s in stages) + ")"
    content = replace_exact(r"\$stages=@\([^\)]+\)", new_stages, content)
    updates[ps_safe_path] = content

    # 2. scripts/New-HtkkX86ReferenceHost.ps1
    host_path = ROOT / "New-HtkkX86ReferenceHost.ps1"
    content = host_path.read_text(encoding="utf-8")
    new_host_validate = "[ValidateSet(" + ",".join(f"'{m}'" for m in all_mode_ids) + ")][string]$GuiAutomation='none'"
    content = replace_exact(r"\[ValidateSet\([^\)]+\)\]\[string\]\$GuiAutomation='none'", new_host_validate, content)
    updates[host_path] = content

    # 3. scripts/probe-htkk-windows.ps1
    probe_path = ROOT / "probe-htkk-windows.ps1"
    content = probe_path.read_text(encoding="utf-8")
    content = replace_exact(r"\[ValidateSet\([^\)]+\)\]\[string\]\$GuiAutomation='none'", new_host_validate, content)

    # Synchronize terminal matcher stages in probe-htkk-windows.ps1
    # Terminal stages include error stages and expected terminal stages for each mode
    base_order = [
        'source-or-runtime-not-matched', 'fixture-preexists', 'initialization-unavailable',
        'profile-wait-timeout', 'profile-dimensions-unmatched', 'fresh-synthetic-profile-not-established',
        'editing-api-unavailable', 'profile-province-code-unmatched', 'profile-ward-code-unmatched',
        'profile-taxhead-code-unmatched', 'profile-taxlocal-code-unmatched', 'original-profile-saved-verified',
        'original-profile-save-not-verified', 'gtgt-profile-preconditions-not-matched', 'gtgt-profile-owner-not-matched',
        'gtgt-menu-id-not-unique', 'gtgt-menu-target-hidden', 'gtgt-period-inspected', 'gtgt-period-inputs-not-matched',
        'gtgt-sheet-inspected', 'gtgt-original-declaration-saved-inspected', 'gtgt-amendment-open-inspected',
        'gtgt-annex12-inspected', 'gtgt-annex12-row-inspected', 'gtgt-annex12-input-inspected',
        'gtgt-annex12-numeric-inspected', 'gtgt-annex12-export-inspected', 'gtgt-sheet-contract-not-matched',
        'gtgt-export-inspected', 'gtgt-export-original-message-rejected', 'gtgt-roundtrip-inspected',
        'gtgt-web-import-inspected', 'gtgt-import-original-message-rejected'
    ]
    terminal_stages = list(base_order)
    for mode_meta in modes.values():
        term = mode_meta.get("terminalStage")
        if term and term != "not-started" and term != "profile-inspected" and term not in terminal_stages:
            terminal_stages.append(term)

    # Build terminal stage replacement pattern
    term_list_str = "@(" + ",".join(f"'{s}'" for s in terminal_stages) + ")"
    content = replace_exact(
        r"\$terminal=\$nextGui\.failureCategory -ne 'none' -or \$nextGui\.stage -in @\([^\)]+\) -or \(\$GuiAutomation -eq 'inspect' -and \$nextGui\.stage -eq 'profile-inspected'\)",
        f"$terminal=$nextGui.failureCategory -ne 'none' -or $nextGui.stage -in {term_list_str} -or ($GuiAutomation -eq 'inspect' -and $nextGui.stage -eq 'profile-inspected')",
        content
    )
    updates[probe_path] = content

    # 4. .github/workflows/probe-htkk-windows.yml
    workflow_path = ROOT.parent / ".github/workflows/probe-htkk-windows.yml"
    require(workflow_path.is_file(), "Workflow integration file missing")
    if workflow_path.exists():
        content = workflow_path.read_text(encoding="utf-8")
        # Update options
        options_str = "[" + ", ".join(all_mode_ids) + "]"
        content = replace_exact(r"(?m)^        options: \[none, [^\]\n]+\]$", f"        options: {options_str}", content)
        # Update powershell check in workflow
        notin_str = "@(" + ",".join(f"'{m}'" for m in all_mode_ids) + ")"
        content = replace_exact(r"if \(\$guiAutomation -notin @\([^\)]+\)\)", f"if ($guiAutomation -notin {notin_str})", content)
        updates[workflow_path] = content

    # Check or write
    has_diff = False
    for path, new_text in updates.items():
        old_text = path.read_text(encoding="utf-8")
        if old_text != new_text:
            has_diff = True
            if check_mode:
                print(f"Diff detected in {path.name}:", file=sys.stderr)
                diff = difflib.unified_diff(
                    old_text.splitlines(keepends=True),
                    new_text.splitlines(keepends=True),
                    fromfile=f"a/{path.name}",
                    tofile=f"b/{path.name}"
                )
                sys.stderr.writelines(diff)
            else:
                path.write_text(new_text, encoding="utf-8")
                print(f"Updated {path.name}")

    # Also C# enums file
    csharp_path = ROOT / "HtkkNativeAutomationEnums.cs"
    new_csharp = generate_csharp_enums(registry)
    old_csharp = csharp_path.read_text(encoding="utf-8") if csharp_path.exists() else ""
    if old_csharp != new_csharp:
        has_diff = True
        if check_mode:
            print(f"Diff detected in {csharp_path.name}:", file=sys.stderr)
            diff = difflib.unified_diff(
                old_csharp.splitlines(keepends=True),
                new_csharp.splitlines(keepends=True),
                fromfile=f"a/{csharp_path.name}",
                tofile=f"b/{csharp_path.name}"
            )
            sys.stderr.writelines(diff)
        else:
            csharp_path.write_text(new_csharp, encoding="utf-8")
            print(f"Updated {csharp_path.name}")

    if check_mode and has_diff:
        print("Registry check FAILED: files are out of sync with registry.", file=sys.stderr)
        return False
    return True


def main():
    parser = argparse.ArgumentParser(description="Generate and verify HTKK native automation registry.")
    parser.add_argument("--check", action="store_true", help="Verify files are up-to-date without writing.")
    args = parser.parse_args()

    registry = load_registry()
    success = sync_powershell_and_workflow(registry, check_mode=args.check)
    if not success:
        sys.exit(1)
    if args.check:
        print("All registry contracts, C# enums, PowerShell files, and workflow guards are UP-TO-DATE.")
    else:
        print("All files synchronized successfully with registry.")


if __name__ == "__main__":
    main()
