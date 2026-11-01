"""Boundaries of the fixed synthetic original common-info oracle."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parent
class CommonInfoOracleContract(unittest.TestCase):
 def test_original_binder_and_config_context_not_profile_or_main(self):
  source=(ROOT/'HtkkCommonInfoOracle.cs').read_text()
  self.assertIn('BindToKhaiInfoToTTinChung',source)
  self.assertIn('binder.MetadataToken!=0x060000f4',source)
  self.assertIn('binder.Invoke(null,new object[0])',source)
  self.assertIn('setup.ConfigurationFile=Path.Combine(project,"HTKK.exe.config")',source)
  self.assertIn('AppDomain.Unload(domain)',source)
  self.assertNotIn('ExecuteAssembly',source)
  self.assertNotIn('LoadFile',source)
  self.assertNotIn('StackTrace',source)
  self.assertNotIn('.Message',source)
  self.assertIn('string[] menus={"D1","D1","73","56","D1"}',source)
  self.assertIn('if(values.Count!=69)',source)
 def test_source_pins_bound_child_and_safe_diagnostic_shape(self):
  wrapper=(ROOT/'Invoke-HtkkCommonInfoOracle.ps1').read_text()
  for source in ['HTKK.exe.config','HTKK.exe','TAX.HTKK.Utilities.dll','TAX.HTKK.Business.dll','FarPoint.CalcEngine.dll','FarPoint.Win.Spread.dll','FarPoint.Win.dll']:
   self.assertIn("'"+source+"'=",wrapper)
  self.assertEqual(wrapper.count('-TimeoutMilliseconds 30000'),2)
  self.assertIn('jobCleanupVerified',wrapper)
  self.assertIn('New-NetFirewallRule',wrapper)
  self.assertIn('sourceHashesUnchanged=$true',wrapper)
  self.assertIn('DateKind String',wrapper)
  self.assertIn('COMMON_INFO_ORACLE_NATIVE_FAILURE',wrapper)
  self.assertIn("$v.cases.Count -ne 5",wrapper)
