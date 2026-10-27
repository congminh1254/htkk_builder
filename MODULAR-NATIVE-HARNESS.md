# Modular Native Harness and Typed Registry Architecture (TASK-004)

## Overview and Goals

Previously, the custom CLR2/x86 Windows reference automation harness was tightly coupled with declaration 01/GTGT (menu coordinates `101 -> 101_1 -> D1`). Adding or modifying automation modes carried the risk of missing workflow guards, strict result allowlists, compiler arguments, or terminal stage matchers.

TASK-004 decouples the native harness into:
1. **Shared Common Harness**: Profile creation, lifecycle polling, STA dispatcher, WinForms/FarPoint control walking, active cell editors, vendor `FpCombo` selection, Save/Message modal dismissal, and bounded result persistence.
2. **Pluggable Adapter Contract (`IHtkkNativeAutomationAdapter`)**: Specialized declaration logic (e.g. `d1-gtgt` for 01/GTGT menu/period/sheets/annexes/cases, and `sample-adapter` for modular verification).
3. **Strict Typed Registry**: Single source of truth in `scripts/htkk-native-automation-registry.json` combined with a Python standard library generator `scripts/generate-native-automation-registry.py` (`--check`).
4. **Compile-Time Typed Stages and Enums**: CLR2/C# 2.0 compatible `HtkkAutomationMode` and `HtkkAutomationStage` enums with explicit wire mappings, replacing error-prone dynamic string concatenations and enabling compiler verification across ternaries.

## Architecture

```
+----------------------------------------------------------------------------------+
|                    htkk-native-automation-registry.json                          |
|             (16 modes, 138 stages, 182 keys, dynamic maps, bounds)              |
+----------------------------------------------------------------------------------+
                                         |
                                         v
                    scripts/generate-native-automation-registry.py (--check)
                                         |
         +-------------------------------+-------------------------------+
         |                               |                               |
         v                               v                               v
HtkkNativeAutomationEnums.cs   Get-HtkkSafeGuiReferenceResult.ps1  probe-htkk-windows.ps1
- HtkkAutomationMode           - ValidateSet([mode])               - ValidateSet([mode])
- HtkkAutomationStage          - $keys allowlist (182)             - Terminal stage matcher
- IHtkkNativeAutomationAdapter - $stages allowlist (138)
- WireMap: filename/menu maps
```

## Adapter Contract

```csharp
public interface IHtkkNativeAutomationAdapter {
  string AdapterId { get; }
  bool CanHandle(HtkkAutomationMode mode);
  void Initialize(HtkkGuiReferenceAutomation harness, string project, HtkkAutomationMode mode);
  void OnProfileSaved(Form profileOwner, Button closeButton, Control spread);
  void ContinueNavigation();
  string BuildNavigationJson();
}
```

### Adapters Implemented
- **`HtkkGtgtAdapter` (`d1-gtgt`)**: Handles all 12 GTGT modes (`gtgt-inspect`, `gtgt-sheet-inspect`, `gtgt-amendment-inspect`, `gtgt-amendment-open-inspect`, `gtgt-annex12-inspect`, `gtgt-annex12-row-inspect`, `gtgt-annex12-input-inspect`, `gtgt-annex12-numeric-inspect`, `gtgt-annex12-export-inspect`, `gtgt-export-inspect`, `gtgt-roundtrip-inspect`, `gtgt-web-import-inspect`).
- **`HtkkSampleAdapter` (`sample-adapter`)**: Proves harness reusability with independent roundtrip export/import verification, isolated artifact policy (`raw-sample-reexport`), and dedicated status context (`htkk-native/sample`).

## Verification & Commands

```sh
# 1. Verify that all generated files, PowerShell allowlists, and workflow guards are in sync:
python3 scripts/generate-native-automation-registry.py --check

# 2. Run full test suite (258 unit & contract tests):
TMPDIR=/private/tmp python3 -m unittest discover -s scripts -p 'test_*.py'
```

## Backward Compatibility & Privacy Guarantee
- All 13 fixed regression cases (`01GTGT-*`) remain 100% intact with zero breaking changes.
- Strict privacy boundary is preserved: no real taxpayer data, no log leakage, strictly synthetic test data.
- Unmodified source binaries and configuration: `HTKK.exe`, `TAX.HTKK.Business.dll`, and `HTKK.exe.config` hashes are verified and never patched.
