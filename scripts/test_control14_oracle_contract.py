"""Safety contracts for the fixed synthetic original masked-date oracle."""
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent

class Control14OracleContract(unittest.TestCase):
    def test_fixed_inputs_and_original_control_path_have_no_application_or_xml_entry(self):
        source = (ROOT / 'HtkkControl14Oracle.cs').read_text()
        self.assertIn('Environment.Version.Major!=2||IntPtr.Size!=4', source)
        self.assertIn('TAX.HTKK.Business.GeneralFunctions', source)
        self.assertIn('"fpSpBindDataCell",new Type[]{sheetType,typeof(int),typeof(int),typeof(string),typeof(string)}', source)
        self.assertIn('new object[]{sheet,1,1,"14",mode=="bind"?input:""}', source)
        self.assertIn('"GetValueExport",new Type[]{sheetType,typeof(string),typeof(int),typeof(int),typeof(string)}', source)
        self.assertIn('new object[]{sheet,"14",1,1,null}', source)
        self.assertIn('"GetText",new Type[]{typeof(int),typeof(int)},new object[]{0,0}', source)
        self.assertIn('(char)celltype.GetType().GetProperty("MaskChar")', source)
        self.assertIn('foreach(string mode in new string[]{"bind","edit","formula"})', source)
        self.assertIn('Call(sheet,"SetFormula"', source)
        self.assertIn('Call(sheet,"RecalculateAll"', source)
        self.assertIn('string[] cultures={"invariant","vi-VN"}', source)
        self.assertNotRegex(source, r'(?i)GetEnvironmentVariable|GetCommandLineArgs|Process\.Start|HttpClient|WebClient|XmlDocument|frmWinToKhai|Register|SaveDeclaration')
        self.assertEqual(source.count('a[0]'), 1)
        self.assertEqual(source.count('a[1]'), 1)
        literals = re.search(r'string\[\] inputs=\{(.*?)\};', source).group(1)
        # JSON-compatible C# string literals, plus the explicit null input.
        self.assertEqual(len(re.findall(r'"(?:\\.|[^"\\])*"|\bnull\b', literals)), 26)

    def test_pins_bounded_processes_firewall_and_unambiguous_json_dates(self):
        source = (ROOT / 'Invoke-HtkkControl14Oracle.ps1').read_text()
        self.assertIn("'TAX.HTKK.Business.dll'='281689aaa7df4db33d0debcfc61d32c0c318bb871d4a19a0277d871a7c04bba7'", source)
        self.assertIn("'TAX.HTKK.Utilities.dll'='ccc35605a4d3bb235f896d6ab43cec4c6543a404159cf10897a57cba23d817ec'", source)
        self.assertEqual(source.count('foreach($p in $pins.Keys)'), 2)
        self.assertIn('Invoke-HtkkBoundedCompiler', source)
        self.assertIn('Invoke-HtkkBoundedJobProcess', source)
        self.assertIn('-TimeoutMilliseconds 30000', source)
        self.assertIn('-Direction Outbound -Program $exe -Action Block', source)
        self.assertIn('$c.jobCleanupVerified', source)
        self.assertIn('$r.jobCleanupVerified', source)
        self.assertIn('$r.processStopped', source)
        self.assertIn('ConvertFrom-Json -AsHashtable -DateKind String', source)
        self.assertIn('$v.cases.Count -ne 156', source)
        self.assertIn("format='htkk-control14-oracle-execution-v1'", source)
        self.assertIn('primitiveOnly=$true', source)
        self.assertIn('finally{', source)
        self.assertIn('Remove-NetFirewallRule -DisplayName $rule', source)
        self.assertIn('Remove-Item -LiteralPath $work -Recurse -Force', source)
        self.assertNotRegex(source, r'(?i)SOURCE_READ_TOKEN|SOURCE_PUBLISH_TOKEN|AGENT_AUTH_TOKEN|GH_TOKEN|GITHUB_TOKEN')

if __name__ == '__main__':
    unittest.main()
