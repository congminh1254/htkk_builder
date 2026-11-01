"""Security boundary contracts for a fixed synthetic original Header binder.
Actual binder behavior is verified on Windows, not inferred by these checks.
"""
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent

class HeaderBindingOracleContract(unittest.TestCase):
    def test_supplier_only_receives_source_and_output_paths_and_fixed_synthetic_data(self):
        source = (ROOT / 'HtkkHeaderBindingOracle.cs').read_text()
        self.assertIn('args.Length!=2', source)
        self.assertEqual(source.count('args[0]'), 1)
        self.assertEqual(source.count('args[1]'), 1)
        fixed = re.search(r'string\[\] ids=\{(.*?)\};', source).group(1)
        self.assertEqual(json.loads('[' + fixed + ']'), ['9999999997', '9999999997001', '999999999701', '9999999997-001', ''])
        self.assertNotRegex(source, r'(?i)GetEnvironmentVariable|GetCommandLineArgs|Process\.Start|HttpClient|WebClient|XmlDocument|LoadToKhai|frmWinToKhai|\.EntryPoint|Register|File\.Read|Directory\.GetFiles|SaveDeclaration')
        self.assertIn('"synthetic-"+p.Name', source)
        self.assertIn('bind.MetadataToken!=0x060000ed', source)
        self.assertIn('bind.Invoke(null,new object[]{"",spread})', source)
        self.assertIn('Environment.Version.Major!=2||IntPtr.Size!=4', source)

    def test_source_process_and_publication_boundaries(self):
        source = (ROOT / 'Invoke-HtkkHeaderBindingOracle.ps1').read_text()
        self.assertEqual(source.count('foreach($p in $pins.Keys)'), 2)
        self.assertIn("'HTKK.exe'='411141d2e728a45f4a35a876afb169d0ac2450de2499e8a1f43ac29ab6401938'", source)
        self.assertIn("'TAX.HTKK.Utilities.dll'='ccc35605a4d3bb235f896d6ab43cec4c6543a404159cf10897a57cba23d817ec'", source)
        self.assertEqual(source.count('-TimeoutMilliseconds 30000'), 2)
        self.assertIn('-Direction Outbound -Program $exe -Action Block', source)
        for condition in ['$c.jobCleanupVerified', '$c.diagnosticsVerified', '$r.jobCleanupVerified', '$r.processStopped']:
            self.assertIn(condition, source)
        self.assertIn('-DateKind String', source)
        self.assertIn('$v.cases.Count -ne 5', source)
        self.assertIn('$x.cells.Count -ne 67', source)
        self.assertIn('primitiveOnly=$true', source)
        self.assertIn('finally{', source)
        self.assertNotRegex(source, r'(?i)SOURCE_READ_TOKEN|SOURCE_PUBLISH_TOKEN|AGENT_AUTH_TOKEN|GH_TOKEN|GITHUB_TOKEN')

if __name__ == '__main__':
    unittest.main()
