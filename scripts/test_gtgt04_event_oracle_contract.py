"""Safety boundaries for the isolated fixed synthetic original UI observer."""
from pathlib import Path
import re
import unittest
ROOT=Path(__file__).resolve().parent
class Gtgt04OracleContract(unittest.TestCase):
 def test_original_editor_events_never_replace_business_computed_cells(self):
  observer=(ROOT/'HtkkGtgt04EventObserver.cs').read_text()
  self.assertIn('TAX.HTKK.Business.Gtgt04TT89Nckt309',observer)
  self.assertIn('BeginCellEdit(grid,sheet,86+r,16,true)',observer)
  self.assertIn('CommitCellEdit(grid)',observer)
  self.assertIn('new int[]{16,25,48}',observer)
  self.assertNotRegex(observer,r'\.SetValue\(|\.SetFormula\(')
  self.assertNotIn('TinhLaiChiTieu',observer)
  self.assertIn('IsOriginalWorksheetClean',observer)
  self.assertIn('computedCellsWritten\\\":false',observer)
 def test_bounded_source_and_process_cleanup_remain_fail_closed(self):
  wrapper=(ROOT/'Invoke-HtkkGtgt04EventOracle.ps1').read_text()
  host=(ROOT/'HtkkGtgt04EventHost.cs').read_text()
  self.assertIn('WaitForInputIdle(30000)',wrapper)
  self.assertIn('Invoke-HtkkBoundedCompiler',wrapper)
  self.assertIn('ActiveProcesses -eq 0',wrapper)
  self.assertIn('sourceHashesUnchanged=$sourceSafe',wrapper)
  self.assertIn('New-NetFirewallRule',wrapper)
  self.assertIn("'sourcePinsVerified','contextMatched'",wrapper)
  self.assertIn("$raw.editorActions -ne 12",wrapper)
  self.assertIn('setup.ConfigurationFile=original+".config"',host)
  self.assertIn('domain.ExecuteAssembly(original)',host)
  self.assertNotRegex(host,r'Exception\.Message|StackTrace|Console\.Write')
