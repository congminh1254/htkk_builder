"""Generate trusted PowerShell/workflow case metadata; no application code execution."""
import importlib.util,pathlib,re,sys
ROOT=pathlib.Path(__file__).parent
spec=importlib.util.spec_from_file_location('case_generator_registry',ROOT/'htkk_native_cases.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
text='$HtkkNativeCaseFormats=@{\n'+''.join(" '"+id+"'='"+c['format']+"'\n"for id,c in r.CASES.items())+'}\n'
file=ROOT/'HtkkNativeCaseFormats.ps1';workflow=ROOT.parent/'.github/workflows/probe-htkk-windows.yml';body=workflow.read_text();updated=re.sub(r'(      web_case_id:\n.*?        options: )\[[^\n]*\]',lambda m:m[1]+'['+', '.join(r.CASES)+']',body,flags=re.S)
if '--check'in sys.argv:
 if file.read_text()!=text or body!=updated:raise SystemExit('Native case metadata stale.')
else:file.write_text(text);workflow.write_text(updated)
