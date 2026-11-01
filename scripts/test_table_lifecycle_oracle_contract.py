from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parent
class TableLifecycleOracleContract(unittest.TestCase):
 def test_fixed_metadata_fixture_never_loads_profiles_or_forces_business_totals(self):
  source=(ROOT/'HtkkTableLifecycleOracle.cs').read_text()
  self.assertIn('0x060001fd',source);self.assertIn('0x060001fa',source)
  self.assertIn('method.Invoke(null,new object[]{sheet,indices[i],info})',source)
  self.assertNotIn('ExecuteAssembly',source);self.assertNotIn('1/0',source)
  self.assertNotIn('Exception.Message',source);self.assertNotIn('StackTrace',source)
  self.assertIn('computedTotalsWritten\\\":false',source)
 def test_source_and_process_boundaries_remain_required(self):
  source=(ROOT/'Invoke-HtkkTableLifecycleOracle.ps1').read_text()
  for required in ['Invoke-HtkkBoundedCompiler','Invoke-HtkkBoundedJobProcess','jobCleanupVerified','New-NetFirewallRule','SOURCE_CHANGED','DateKind String','NATIVE_FAILURE']:
   self.assertIn(required,source)
  self.assertIn('$v.cases.Count -ne 9',source)
