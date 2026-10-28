"""Test views for generated contracts; unknown enum references fail immediately."""
import json
import pathlib
import re
ROOT = pathlib.Path(__file__).parent

def registry():
    return json.loads((ROOT / 'htkk-native-automation-registry.json').read_text())

def field(name):
    return registry()['resultFields'][name]

def wire_source(name):
    source = (ROOT / name).read_text()
    if not name.endswith('.cs'):
        return source
    mapping = {stage['enumName']: stage['id'] for stage in registry()['stages']}
    # Only SetStage expressions are projected. This does not erase unresolved tokens.
    def project(match):
        expression = match[1]
        def token(value):
            return '"' + mapping[value[1]] + '"'
        expression = re.sub(r'HtkkAutomationStage\.([A-Za-z0-9_]+)', token, expression)
        return 'stage=' + expression + ';'
    return re.sub(r'SetStage\(([^;]+)\);', project, source)

def assert_compile_input(test, mode, name):
    test.assertIn(name, registry()['modes'][mode]['orderedCompileInputs'])
    host = (ROOT / 'New-HtkkX86ReferenceHost.ps1').read_text()
    test.assertIn('Get-HtkkNativeCompileInputs -Mode $GuiAutomation', host)
    test.assertIn('+$compilerSources)', host)
