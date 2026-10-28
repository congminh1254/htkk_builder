"""Installer provenance must not depend on a mirror that returned HTTP410."""
import pathlib,unittest
ROOT=pathlib.Path(__file__).resolve().parent
class OfficialDistributionTests(unittest.TestCase):
 def test_original_setup_msi_and_cab_pins_precede_any_installer_execution(self):
  s=(ROOT/'probe-htkk-windows.ps1').read_text();start=s.index("$report.stage = 'download'");end=s.index("$report.stage = 'framework-check'");source=s[start:end]
  self.assertNotIn('getpedia',source);self.assertNotIn('Expand-Archive',source)
  self.assertIn("$source = Join-Path $official 'HTKK_5.8.1_DLL_signed'",source)
  for sha in ('5d52c06595e933a3b246480785d5d4010fad669baed6fb38311f8a09b20e1e95','00669905937fb29e10cb53209ece5e8a9f8097970e4cb40bb28f89baa9fc3744','7c1da251ee2acd126a2363e4457502b8ad6fc0792d78dc0a92b153701dc29080','19394e89351dc213306864168e16808d48401597f56d5fe4c977f9a5833d2936'):
   self.assertIn(sha,source)
  self.assertLess(s.index("$report.officialDistributionFilesVerified = $true"),s.index("$report.msiAuthenticodeValid = $true"))
  self.assertLess(s.index("$report.msiAuthenticodeValid = $true"),s.index("$report.stage = 'install'"))
  self.assertNotIn('$report.officialCabMatchesMirror = $true',s)
if __name__=='__main__':unittest.main()
