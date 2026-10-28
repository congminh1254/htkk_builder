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

    This registry describes routing and wire names only. The registry owns field types/ranges/defaults. Reviewed custom validators
    and business success predicates remain code, never arbitrary expressions.
    """
    top = {"format", "version", "modes", "stages", "dynamicStageMappings", "keys", "controlKinds", "periodControls", "resultFields"}
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
            require(meta["runtime"] == "none" and not meta["login"] and bool(inputs) and meta["permit"] is None, "Invalid launch-only policy")
        else:
            require(meta["runtime"] == "clr2-x86-custom-reference" and meta["login"] and bool(inputs), "Invalid automation policy")
    require("none" in modes, "Missing launch-only mode")
    closure = modes["inspect"]["orderedCompileInputs"]
    require(all(m["orderedCompileInputs"] == closure for m in modes.values()), "All modes must compile the full shared partial closure")
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
    validate_result_fields(registry)
    return registry


def audit_result_producers(registry, sources=None):
    """Conservative source-shape audit for this reviewed CLR2 serializer.

    This is not a C# parser or native proof. Any new serializer shape needs a
    reviewed extractor, instead of silently bypassing the wire contract.
    """
    if sources is None:
        names = registry['modes']['inspect']['orderedCompileInputs']
        sources = [(ROOT/name).read_text(encoding='utf-8') for name in names
                   if name not in {'HtkkNativeAutomationEnums.cs', 'HtkkNativeUiHarness.cs'}]
    defaults = {}
    producers = {}
    def add(key, kind, member):
        require(key not in producers, 'Duplicate producer result field')
        producers[key] = (kind, member)
    for source in sources:
        for kind, declaration in re.findall(r'\bprivate\s+(bool|int)\s+([^;]+);', source):
            # Field declaration shape only: method bodies and computed expressions
            # do not count as declared initial defaults.
            if '(' in declaration or '{' in declaration:
                continue
            for item in declaration.split(','):
                match = re.fullmatch(r'\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(false|true|[0-9]+)\s*', item)
                if match:
                    name, value = match.groups()
                    require(name not in defaults, 'Ambiguous producer result member')
                    defaults[name] = (kind, value == 'true' if kind == 'bool' else int(value))
        for match in re.finditer(r'"([A-Za-z0-9_]+)"\+q\+":"\+Bool\(([A-Za-z0-9_]+)\)', source):
            if match[1] not in {'checked','checkedAvailable'}:  # reviewed periodControls nested schema
                add(match[1], 'boolean', match[2])
        for match in re.finditer(r'"([A-Za-z0-9_]+)"\+q\+":"\+([A-Za-z_][A-Za-z0-9_]*)(?=\+|\.ToString\(|[);])', source):
            key, member = match.groups()
            if member in defaults and defaults[member][0] == 'int':
                add(key, 'integer', member)
        for match in re.finditer(r'"([A-Za-z0-9_]+)"\+q\+":(false|true)', source):
            add(match[1], 'boolean', match[2] == 'true')
        # Array serializers pair names with a typed bool/int array. Match each
        # names declaration to the immediately following typed array, even when
        # q/StringBuilder declarations occur between the two.
        pattern = r'\bnames=new string\[\]\{([^}]+)\};(?:(?!\bnames=).)*?\b(bool|int)\[\]\s+(?:flags|values|counts)=new (?:bool|int)\[\]\{([^}]+)\};'
        for match in re.finditer(pattern, source, flags=re.S):
            names = re.findall(r'"([A-Za-z0-9_]+)"', match[1])
            members = [m.strip() for m in match[3].split(',')]
            require(len(names) == len(members), 'Result producer name/value arity mismatch')
            kind = 'boolean' if match[2] == 'bool' else 'integer'
            for key, member in zip(names, members):
                add(key, kind, member)
    expected = {k:v for k,v in registry['resultFields'].items() if v['kind'] in {'boolean','integer'}}
    require(set(producers) == set(expected), 'Typed result fields must exactly match actual serializer names: missing='+str(set(expected)-set(producers))+' extra='+str(set(producers)-set(expected)))
    for key, (kind, member) in producers.items():
        field = expected[key]
        require(kind == field['kind'], 'Result serializer type mismatch')
        if type(member) is bool:
            require(kind == 'boolean' and member is field['default'], 'Result literal default mismatch')
        else:
            require(member in defaults, 'Result member must have explicit reviewed initial default')
            declared, default = defaults[member]
            require(declared == ('bool' if kind == 'boolean' else 'int') and type(default) is type(field['default']) and default == field['default'], 'Result producer member type/default mismatch')
    return producers


def field_values(registry, field):
    if 'values' in field:
        return field['values']
    if field['valuesFrom'] == 'automation-modes':
        return [m for m in registry['modes'] if m != 'none']
    return [s['id'] for s in registry['stages']]


def validate_result_fields(registry):
    fields = registry['resultFields']
    require(type(fields) is dict and list(fields) == registry['keys'], 'Result field contract must exactly cover ordered keys')
    kinds = {'boolean', 'integer', 'enum', 'hex', 'string', 'object'}
    for key, field in fields.items():
        require(type(field) is dict and field.get('kind') in kinds, 'Invalid result field kind')
        kind = field['kind']
        base = {'kind', 'default'}
        optional = {'activeModes'}
        if kind == 'integer':
            base |= {'minimum', 'maximum'}
            optional |= {'modeMaximums'}
        elif kind == 'enum':
            require(('values' in field) != ('valuesFrom' in field), 'Enum requires one source')
            base |= {'values'} if 'values' in field else {'valuesFrom'}
        elif kind == 'hex':
            base |= {'length', 'allowEmpty'}
        elif kind == 'string':
            base |= {'validator', 'maximumLength'}
        elif kind == 'object':
            base |= {'validator'}
        require(base <= set(field) <= base | optional, 'Invalid result field properties')
        if 'activeModes' in field:
            active = field['activeModes']
            require(type(active) is list and all(type(m) is str and m in registry['modes'] and m != 'none' for m in active) and len(set(active)) == len(active), 'Invalid active mode restriction')
        default = field['default']
        if kind == 'boolean':
            require(type(default) is bool and default is False, 'Flag default must fail closed')
        elif kind == 'integer':
            low, high = field['minimum'], field['maximum']
            require(type(low) is int and type(high) is int and 0 <= low <= high <= 2147483647, 'Invalid counter range')
            require(type(default) is int and low <= default <= high and default == 0, 'Invalid counter default')
            overrides = field.get('modeMaximums', {})
            require(type(overrides) is dict and all(type(m) is str and m in registry['modes'] and m != 'none' and type(v) is int and low <= v <= 2147483647 for m,v in overrides.items()), 'Invalid mode counter range')
        elif kind == 'enum':
            if 'valuesFrom' in field:
                require(field['valuesFrom'] in {'automation-modes', 'stages'}, 'Unknown enum source')
            values = field_values(registry, field)
            require(type(values) is list and bool(values) and all(type(v) is str and re.fullmatch(r'[A-Za-z0-9_-]+',v) for v in values) and len(set(values)) == len(values), 'Invalid enum values')
            require(type(default) is str and default in values, 'Invalid enum default')
        elif kind == 'hex':
            require(type(field['length']) is int and field['length'] in {40,64} and field['allowEmpty'] is True and default == '', 'Invalid digest field')
        elif kind == 'string':
            require(field['validator'] == 'annex-numeric-snapshots-v1' and type(field['maximumLength']) is int and field['maximumLength'] == 4096 and default == '', 'Unknown string validator')
        else:
            require((key, field['validator']) in {('periodControls','period-controls-v1'),('controlKinds','control-kinds-v1')}, 'Unknown object validator')
            expected = {} if key == 'periodControls' else {k:0 for k in registry['controlKinds']}
            require(type(default) is dict and default == expected and all(type(v) is int for v in default.values()), 'Invalid object defaults')
    for key in ('realTaxpayerDataUsed', 'runtimeRoundTrip', 'amendmentLifecycleVerified'):
        require(fields[key].get('activeModes') == [] and fields[key]['kind'] == 'boolean', 'Privacy and capability flags must remain closed')


def ps_literal(value):
    if type(value) is bool:
        return '$true' if value else '$false'
    if type(value) is int:
        return str(value)
    if type(value) is str:
        return "'" + value.replace("'", "''") + "'"
    if type(value) is dict:
        return '[ordered]@{' + ';'.join(k+'='+ps_literal(v) for k,v in value.items()) + '}'
    raise ValueError('Unsupported PowerShell literal')


def generate_result_validation(registry):
    lines = ['  # BEGIN GENERATED RESULT CONTRACT - do not edit']
    for key, field in registry['resultFields'].items():
        value = "$value['"+key+"']"
        kind = field['kind']
        if kind == 'boolean':
            check = value + ' -isnot [bool]'
        elif kind == 'integer':
            maximum = str(field['maximum'])
            for mode, bound in reversed(list(field.get('modeMaximums', {}).items())):
                maximum = "$(if($ExpectedMode -ceq '"+mode+"'){"+str(bound)+'}else{'+maximum+'})'
            check = '('+value+' -isnot [int] -and '+value+' -isnot [long]) -or '+value+' -lt '+str(field['minimum'])+' -or '+value+' -gt '+maximum
        elif kind == 'enum':
            values = '@('+','.join(ps_literal(v) for v in field_values(registry,field))+')'
            check = value+' -isnot [string] -or '+value+' -cnotin '+values
        elif kind == 'hex':
            check = value+" -isnot [string] -or ("+value+" -cne '' -and "+value+" -cnotmatch '\\A[0-9a-f]{"+str(field['length'])+"}\\z')"
        elif kind == 'string':
            check = value+' -isnot [string] -or '+value+'.Length -gt '+str(field['maximumLength'])
        else:
            # Reviewed custom code below reconstructs object fields recursively.
            check = value+' -isnot [Collections.IDictionary]'
        lines.append("  if("+check+"){throw 'invalid'}")
        if 'activeModes' in field:
            modes = field['activeModes']
            condition = '$true' if not modes else '$ExpectedMode -cnotin @('+','.join(ps_literal(m) for m in modes)+')'
            lines.append("  if(("+condition+") -and "+value+' -cne '+ps_literal(field['default'])+"){throw 'invalid'}")
    lines.append("  if($value.mode -cne $ExpectedMode){throw 'invalid'}")
    lines.append('  # END GENERATED RESULT CONTRACT')
    return '\n'.join(lines)


def generate_result_defaults(registry):
    lines = ['# BEGIN GENERATED RESULT DEFAULTS - fixture initialization only; reader never fills missing keys',
             'function New-HtkkNativeResultDefaults {',
             ' param([Parameter(Mandatory=$true)][string]$Mode)',
             ' if($Mode -cnotin @('+','.join(ps_literal(m) for m in registry['modes'] if m != 'none')+")){throw 'Unknown mode'}",
             ' $result=[ordered]@{']
    for key, field in registry['resultFields'].items():
        lines.append('  '+key+'='+('$Mode' if key=='mode' else ps_literal(field['default'])))
    lines.extend([' }',' return $result','}','# END GENERATED RESULT DEFAULTS'])
    return '\n'.join(lines)


def generate_result_csharp(registry):
    flags = {k:v for k,v in registry['resultFields'].items() if v['kind']=='boolean'}
    counters = {k:v for k,v in registry['resultFields'].items() if v['kind']=='integer'}
    enum_name = lambda key: key[0].upper()+key[1:]
    lines = ['', '// Typed result metadata; values remain produced exclusively by original UI observations.',
             'public enum HtkkNativeResultFlag { '+', '.join(enum_name(k) for k in flags)+' }',
             'public enum HtkkNativeResultCounter { '+', '.join(enum_name(k) for k in counters)+' }',
             'public static class HtkkNativeResultContract {']
    for name, fields in [('Flag',flags),('Counter',counters)]:
        lines += [' public static string ToWireString(HtkkNativeResult'+name+' field) {','  switch(field) {']
        for key in fields:
            lines.append('   case HtkkNativeResult'+name+'.'+enum_name(key)+': return "'+key+'";')
        lines += ['   default: throw new ArgumentException("Unknown result field");','  }',' }']
    lines += [' public static bool FlagDefault(HtkkNativeResultFlag field) { ToWireString(field); return false; }',
              ' public static int CounterDefault(HtkkNativeResultCounter field) { ToWireString(field); return 0; }',
              ' public static int CounterMaximum(HtkkNativeResultCounter field, HtkkAutomationMode mode) {',
              '  HtkkNativeAutomationWireMap.ToWireString(mode);','  if(mode==HtkkAutomationMode.None)throw new ArgumentException("Launch-only mode");',
              '  switch(field) {']
    for key, field in counters.items():
        lines.append('   case HtkkNativeResultCounter.'+enum_name(key)+':')
        for mode, bound in field.get('modeMaximums',{}).items():
            lines.append('    if(mode==HtkkAutomationMode.'+''.join(p.capitalize() for p in mode.split('-'))+')return '+str(bound)+';')
        lines.append('    return '+str(field['maximum'])+';')
    lines += ['   default: throw new ArgumentException("Unknown result counter");','  }',' }','}']
    return '\n'.join(lines)+'\n'


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
    return "\n".join(code) + generate_result_csharp(registry)


def sync_powershell_and_workflow(registry, check_mode=False):
    audit_result_producers(registry)
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
    content = replace_exact(r"(?ms)^  # BEGIN GENERATED RESULT CONTRACT.*?^  # END GENERATED RESULT CONTRACT", generate_result_validation(registry), content)
    updates[ROOT / "HtkkNativeResultDefaults.ps1"] = generate_result_defaults(registry)+"\n"
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

    compile_lines = ['# Auto-generated by generate-native-automation-registry.py. Do not edit.',
                     'function Get-HtkkNativeCompileInputs {',
                     ' [CmdletBinding()]',
                     ' param([Parameter(Mandatory=$true)][string]$Mode)',
                     ' switch -CaseSensitive ($Mode) {']
    for mode, meta in modes.items():
        compile_lines.append("  '"+mode+"' { return @("+','.join(ps_literal(name) for name in meta['orderedCompileInputs'])+"); }")
    compile_lines += ["  default { throw 'Unknown automation mode' }", ' }', '}']
    updates[ROOT / 'HtkkNativeCompileInputs.ps1'] = '\n'.join(compile_lines)+'\n'

    # Check or write
    has_diff = False
    for path, new_text in updates.items():
        old_text = path.read_text(encoding="utf-8") if path.exists() else ""
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
