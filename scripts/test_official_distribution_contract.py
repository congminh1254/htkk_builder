"""Installer provenance must not depend on a mirror that returned HTTP410."""
import importlib.util,pathlib,unittest
ROOT=pathlib.Path(__file__).resolve().parent
_spec=importlib.util.spec_from_file_location('distribution_oracle',ROOT/'htkk_oracle.py');oracle=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(oracle)
class OfficialDistributionTests(unittest.TestCase):
 def test_original_setup_msi_and_cab_pins_precede_any_installer_execution(self):
  s=(ROOT/'probe-htkk-windows.ps1').read_text();start=s.index("$report.stage = 'download'");end=s.index("$report.stage = 'framework-check'");source=s[start:end]
  self.assertNotIn('getpedia',source);self.assertNotIn('Expand-Archive',source)
  # Every distribution pin comes from the ONE selected baseline, obtained before any download.
  self.assertLess(s.index(". (Join-Path $PSScriptRoot 'HtkkOracleBaseline.ps1'); $htkkOracle=Get-HtkkOracleBaseline -Version $OracleVersion"),start)
  self.assertIn("[ValidateSet('5.8.1','5.8.2')][string]$OracleVersion='5.8.1'",s)
  for line in ("Get-PinnedFile $htkkOracle.officialUrl $rar $htkkOracle.archiveSha256","$source = Join-Path $official $htkkOracle.archiveFolder","Assert-Hash $cab $htkkOracle.cabSha256","Assert-Hash $msi $htkkOracle.msiSha256","Assert-Hash (Join-Path $source 'setup.exe') $htkkOracle.setupSha256"):
   self.assertIn(line,source)
  self.assertNotRegex(source,r'[0-9a-f]{64}')
  # The default oracle keeps the exact historical 5.8.1 pins; 5.8.2 has its own verified pins.
  expected={'5.8.1':('https://www.fshare.vn/file/TPW3FMLVAJL1','HTKK_5.8.1_DLL_signed','5d52c06595e933a3b246480785d5d4010fad669baed6fb38311f8a09b20e1e95','00669905937fb29e10cb53209ece5e8a9f8097970e4cb40bb28f89baa9fc3744','7c1da251ee2acd126a2363e4457502b8ad6fc0792d78dc0a92b153701dc29080','19394e89351dc213306864168e16808d48401597f56d5fe4c977f9a5833d2936'),
            '5.8.2':('https://www.fshare.vn/file/WYSRASTITCWB','HTKK_5.8.2_DLL_signed','51baf5c8cea7f2d688476c611325e000bec2cbd3dff42f593b711cbe5863d424','5427c6632d5b60b15440e504effd314f050a56e66d4b2178355ee34b261b530c','17c21f3ccf8c0bc6618b1b049ad7ee0328cc1bf8e914c15dbbfe7946b7c0fd73','1c2612d37176b6e02401e2e8b43c247490a7e8a971ef14144c8b9a5e84eb0efb')}
  self.assertEqual(oracle.DEFAULT,'5.8.1')
  generated=(ROOT/'HtkkOracleBaseline.ps1').read_text(encoding='utf-8')
  for version,(url,folder,archive,cab,msi,setup) in expected.items():
   d=oracle.baseline(version)['distribution']
   self.assertEqual((d['officialUrl'],d['archiveFolder'],d['archiveSha256'],d['cabSha256'],d['msiSha256'],d['setupSha256']),(url,folder,archive,cab,msi,setup))
   line=next(l for l in generated.splitlines() if l.startswith("  '"+version+"' {"))
   for value in (url,folder,archive,cab,msi,setup):self.assertIn("'"+value+"'",line)
  self.assertLess(s.index("$report.officialDistributionFilesVerified = $true"),s.index("$report.msiAuthenticodeValid = $true"))
  self.assertLess(s.index("$report.msiAuthenticodeValid = $true"),s.index("$report.stage = 'install'"))
  self.assertNotIn('$report.officialCabMatchesMirror = $true',s)
if __name__=='__main__':unittest.main()

class TrustEnvironmentTests(unittest.TestCase):
 def test_worker_uses_os_known_folders_under_essential_only_environment(self):
  s=(ROOT/'Test-HtkkSourceCandidateTrust.ps1').read_text()
  self.assertNotIn('$env:ProgramFiles',s)
  self.assertIn("$env:SystemRoot,'System32','tar.exe'",s)
  self.assertIn('microsoft-signed-system32-tar-pinned-members',s)
  self.assertIn('[Environment+SpecialFolder]::ProgramFilesX86',s)
