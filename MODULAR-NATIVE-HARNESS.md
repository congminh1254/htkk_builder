# Native adapter routing and stage registry foundation (TASK-004, partial)

This change introduces a D1 adapter facade and generated wire-name contracts. It
is a foundation for issue `congminh1254/htkk_web#5`; it does **not** complete that
issue or qualify a new declaration, period, native sample, or status context.

## What is implemented

- `HtkkGtgtAdapter` delegates the existing D1 continuation and result collection
  through `IHtkkNativeAutomationAdapter`. Shared profile editing, STA dispatch,
  timers and the original control actions remain in the existing harness.
- `htkk-native-automation-registry.json` records the existing 14 automation modes
  plus launcher-only `none`, 130 wire stages, 182 result keys, and explicit menu
  and filename action maps. No sample mode or new context is exposed.
- The Python standard-library generator validates collection shapes, property
  allowlists, duplicate identities, safe generated tokens, cross-references,
  bounded timeouts and compile-input paths. Missing or ambiguous integration
  anchors fail instead of silently skipping synchronization.
- Generated CLR2/C# 2.0 enums and maps synchronize PowerShell mode/stage/key
  allowlists and workflow mode guards. Selected dynamic and ternary stages use
  enum values. Remaining string stage assignments are validated at runtime by
  the stage property; they are **not** claimed to have compile-time checking.

## Gates that remain handwritten

The registry currently describes routing metadata; timeout, permit, compile-set,
artifact/context and success-policy metadata do not replace the reviewed runtime
implementations. Field types, counter limits, defaults and mode-specific business
success predicates remain in the strict PowerShell reader/probe. Full generation
and validation of those contracts is pending in issue #5.

The D1 facade still depends on existing D1 partial state. Extraction of reusable
profile/editor/dialog state and an independently driven native sample remains
pending. A sample which authors XML itself and then parses/hashes its own output
would not establish original HTKK export/import compatibility and is excluded.

## Validation

```sh
python3 scripts/generate-native-automation-registry.py --check
python3 -m unittest discover -s scripts -p 'test_*.py'
```

These checks establish source synchronization and contract regression only.
A trusted Windows run must compile the complete CLR2/x86 host and replay the
existing 13 native cases before this revision can be described as native-qualified.
A future genuine sample requires original profile → declaration → export → import
→ re-export actions, independent XSD/semantic checks, immutable provenance and raw
bytes retained privately in its own case context. No new evidence claim is made
by this foundation.

Original binaries/configuration and source pins remain unchanged. Existing
process boundaries, credential gates, privacy rules and 13 case dispatch mappings
are preserved; this change supplies no evidence that broadens application scope.
