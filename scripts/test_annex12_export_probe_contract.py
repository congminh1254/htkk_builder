"""Harness route and credential/XSD boundary checks, never native proof."""
import pathlib,re,unittest
ROOT=pathlib.Path(__file__).parent
class AnnexExportProbeContract(unittest.TestCase):
 def test_after_proved_inputs_main_values_are_read_not_forged_before_original_export(self):
  text=(ROOT/'HtkkGtgtAnnex12ExportInspection.cs').read_text();block=text[text.index(' private void StartOriginalAnnex12Export('):text.index(' private sealed class Annex12PinnedSchemaResolver')]
  for value in ('annex12InputActionCount!=14','!annex12InputReadOnlyIdentityMatched','!annex12InputPercentagesMatched','!annex12InputZeroTaxMatched','Convert.ToInt32(Get(sheets,"Count"))!=11','new object[]{0}','!=72','!=24','Selected(Get(Cell(main,35,8),"Value"))','InspectMoneyZero(main);InspectCaseMoney(main);','gtgtCaseMoneyCount==27','gtgtCaseMismatchMask==0','gtgtCaseNonzeroMask==0','StartOriginalGtgtExport(grid.FindForm())'):
   self.assertIn(value,block)
  self.assertNotIn('gtgtCaseMoneyMatched=true',block);self.assertNotIn('SetValue',block);self.assertNotIn('SetPublic',block)
 def test_xsd_resolution_is_local_three_file_allowlist_with_source_hashes_and_no_remote_fallback(self):
  text=(ROOT/'HtkkGtgtAnnex12ExportInspection.cs').read_text()
  self.assertEqual(len(re.findall(r'files.Add\(',text)),3)
  for pin in ('8d4c0d88100e858ddfe221d080a6a338776d1364c7de04347bfb990d04833003','8f451719355b5a6247f65a34a37584b4a0c7f7cc81a568e1033d08b8fe9b8c1d','c3b5160be1852606d10f6928e0b214d418f8dd418667cb2fb88fec31e4e6f56d'):
   self.assertIn(pin,text)
  for term in ('!absoluteUri.IsFile','!files.ContainsKey(path)','Hash(path)!=files[path]','FileAttributes.ReparsePoint','schemas.XmlResolver=resolver','check.XmlResolver=null','check.ValidationType=ValidationType.Schema','schemas.Compile()','while(reader.Read())','Hash(exportPath)==exportSha256'):
   self.assertIn(term,text)
  self.assertNotIn('XmlUrlResolver',text);self.assertNotIn('WebRequest',text);self.assertNotIn('ProcessSchemaLocation',text);self.assertNotIn('ProcessInlineSchema',text)
 def test_raw_retention_is_separate_and_credentials_are_loaded_only_after_native_shutdown(self):
  workflow=(ROOT.parent/'.github/workflows/probe-htkk-windows.yml').read_text();start=workflow.index('      - name: Retain fixed original 01-2 GTGT export privately');end=workflow.index('      - name:',start+20);block=workflow[start:end]
  for term in ("steps.native_probe.outcome == 'success'","steps.native_probe.outputs.credentials_safe == 'true'","steps.native_probe.outputs.supplier_stopped == 'true'","inputs.gui_automation == 'gtgt-annex12-export-inspect'",'SOURCE_PUBLISH_TOKEN:','publish-htkk-annex12-export.py'):
   self.assertIn(term,block)
  probe=(ROOT/'probe-htkk-windows.ps1').read_text();self.assertLess(probe.index('$supplierStopped=$process.HasExited'),probe.index("'stage-htkk-annex12-export.py'"))
  stage=(ROOT/'stage-htkk-annex12-export.py').read_text();self.assertNotIn('SOURCE_PUBLISH_TOKEN',stage);self.assertNotIn('SOURCE_READ_TOKEN',stage)
  for name in ('publish-htkk-web-native-output.py','fetch-htkk-web-input.py','publish-htkk-web-inputs.py','report-native-case.py'):
   self.assertNotIn('gtgt-annex12-export-inspect',(ROOT/name).read_text())
 def test_new_partial_is_an_actual_compiler_input_and_report_flags_are_bounded(self):
  host=(ROOT/'New-HtkkX86ReferenceHost.ps1').read_text();reader=(ROOT/'Get-HtkkSafeGuiReferenceResult.ps1').read_text();fixture=(ROOT/'Test-HtkkSafeGuiReferenceResult.ps1').read_text()
  self.assertIn("$annexExportSource=Join-Path $directory 'HtkkGtgtAnnex12ExportInspection.cs'",host);self.assertIn('$amendmentSource,$amendmentOpenSource,$annexNumericSource,$annexExportSource)',host)
  for flag in ('annex12ExportMainZeroMatched','annex12ExportShapeMatched','annex12ExportSchemaVerified'):
   self.assertIn(flag+'=$false;',fixture);self.assertGreaterEqual(reader.count("'"+flag+"'"),2)
  self.assertIn("$ExpectedMode -cne 'gtgt-annex12-export-inspect'",reader)

 def test_every_new_native_stage_is_allowlisted_and_success_stage_is_terminal(self):
  source=(ROOT/'HtkkGtgtAnnex12ExportInspection.cs').read_text();reader=(ROOT/'Get-HtkkSafeGuiReferenceResult.ps1').read_text();probe=(ROOT/'probe-htkk-windows.ps1').read_text()
  allowed=set(re.findall(r"'([^']+)'",re.search(r'\$stages=@\(([^\n]+)\)',reader).group(1)))
  assigned=set(re.findall(r'stage="([^"]+)"',source))|{'gtgt-annex12-export-inspected'}
  self.assertTrue(assigned<=allowed,assigned-allowed)
  terminal=re.search(r'\$terminal=\$nextGui[^\n]+',probe).group(0);self.assertIn("'gtgt-annex12-export-inspected'",terminal)
  self.assertIn("$annexStageResult.code -cin @('PROVENANCE','STAGING','HASH','XML_CONTRACT','IO','INTERNAL','BUILDER','MANIFEST','SOURCE_COMMIT')",probe)
