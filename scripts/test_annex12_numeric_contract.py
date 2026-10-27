import pathlib,re,unittest
ROOT=pathlib.Path(__file__).parent
class NumericProbeContract(unittest.TestCase):
 def test_only_five_original_editable_inputs_are_changed(self):
  text=(ROOT/'HtkkGtgtAnnex12NumericInspection.cs').read_text()
  pairs=re.search(r'int\[,] cells=new int\[,]\{([^;]+)\};',text).group(1)
  self.assertEqual(re.findall(r'\{(\d+),(\d+)\}',pairs),[('42','19'),('42','19'),('43','20'),('44','20'),('42','19')])
  for term in ('"Locked"','SendKeys.SendWait(keys)','!editor.ContainsFocus','Annex12InputOwner(grid,annex)','annex12NumericCaseCount>=3','NumberStyles.Number','999999999999999m'):
   self.assertIn(term,text)
  for term in ('SetValue','SetPublic','"Formula"','StartOriginalGtgtExport','GetMethod("Calculate'):
   self.assertNotIn(term,text)
 def test_native_source_is_copied_and_compiled_and_result_is_terminal(self):
  host=(ROOT/'New-HtkkX86ReferenceHost.ps1').read_text()
  self.assertIn("ReadAllText((Join-Path $PSScriptRoot 'HtkkGtgtAnnex12NumericInspection.cs')",host)
  self.assertIn('$amendmentOpenSource,$annexNumericSource,$annexExportSource)',host)
  probe=(ROOT/'probe-htkk-windows.ps1').read_text();self.assertIn("'gtgt-annex12-input-inspected','gtgt-annex12-numeric-inspected','gtgt-annex12-export-inspected'",probe)
  for field in ('annex12NumericActionCount -eq 5','annex12NumericCaseCount -eq 3'):
   self.assertIn(field,probe)

 def test_fractional_ui_text_uses_original_separators_but_comparison_is_canonical(self):
  source=(ROOT/'HtkkGtgtAnnex12NumericInspection.cs').read_text()
  self.assertIn("editorValue=values[index].Replace('.',',')",source)
  self.assertIn('EscapeSendKeys(editorValue)',source)
  self.assertIn('Decimal.Parse(values[index],CultureInfo.InvariantCulture)',source)
  self.assertIn('Get(cellType,"DecimalSeparator")',source)
  self.assertIn('Get(cellType,"Separator")',source)
  reader=(ROOT/'Get-HtkkSafeGuiReferenceResult.ps1').read_text()
  for stage in ('format-checking','editor-ready','committed','value-mismatch'):
   self.assertIn('gtgt-annex12-numeric-'+stage,source)
   self.assertIn('gtgt-annex12-numeric-'+stage,reader)

 def test_display_and_bits_are_read_only_bounded_original_observations(self):
  source=(ROOT/'HtkkGtgtAnnex12NumericInspection.cs').read_text()
  for term in ('CellText(annex,cells[i,0],cells[i,1])','text.Length>64','"0123456789,.()- "','raw is Double?BitConverter.DoubleToInt64Bits((Double)raw)','ToString("X16",CultureInfo.InvariantCulture)'):
   self.assertIn(term,source)
  for field in ('annex12NumericTextSnapshots','annex12NumericTypeSnapshots','annex12NumericDoubleBits'):
   self.assertIn(field,source)
   self.assertIn(field,(ROOT/'Get-HtkkSafeGuiReferenceResult.ps1').read_text())
   self.assertIn(field+"='';",(ROOT/'Test-HtkkSafeGuiReferenceResult.ps1').read_text())
