# No tax data, credentials, screenshots or installer logs are published.
[CmdletBinding()]
param([switch]$InstallAndProbe)
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
Set-StrictMode -Version Latest
$report = [ordered]@{
  version = '5.8.1'; stage = 'started'; sourceHashesVerified = $false
  officialCabMatchesMirror = $false; msiAuthenticodeValid = $false
  netFx35Present = $false; installExitCode = $null
  processStarted = $false; processAliveAfterWait = $false; windowObserved = $false
  runtimeRoundTrip = $false; taxDataUsed = $false; screenshotsPublished = $false
}
$work = Join-Path $env:RUNNER_TEMP ('htkk-probe-' + [guid]::NewGuid().ToString('N'))
$process = $null
function Assert-Hash([string]$Path, [string]$Expected) {
  if ((Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $Expected) { throw 'SOURCE_HASH_MISMATCH' }
}
function Get-PinnedFile([string]$Url, [string]$Path, [string]$Expected) {
  # Public URLs only. No relay token, cookie, auth header or TLS override.
  Invoke-WebRequest -Uri $Url -OutFile $Path -TimeoutSec 120 -MaximumRedirection 8 -UserAgent 'HotroKeKhai-ReadinessProbe/1.0'
  Assert-Hash $Path $Expected
}
try {
  New-Item -ItemType Directory -Path $work | Out-Null
  $report.stage = 'download'
  $rar = Join-Path $work 'official.rar'; $zip = Join-Path $work 'mirror.zip'
  Get-PinnedFile 'https://www.fshare.vn/file/TPW3FMLVAJL1' $rar '5d52c06595e933a3b246480785d5d4010fad669baed6fb38311f8a09b20e1e95'
  Get-PinnedFile 'https://fa.getpedia.net/data?q===QMzEDM2gjM3MDM0UzN4ITOzYDfxMTMxEDfwlmeuETL40SNts0SUh0L3EzLwEzL2IDMy8SZslmZvEGdhR2L' $zip '3f50ede214d802984549aa3841c3de6614fca90021ef5029a9c1ac1999776edb'
  $report.sourceHashesVerified = $true
  $report.stage = 'extract-data'
  $seven = Join-Path $env:ProgramFiles '7-Zip\7z.exe'
  if (-not (Test-Path -LiteralPath $seven)) { throw 'TRUSTED_RUNNER_7ZIP_MISSING' }
  # A pinned ZIP is expanded as data. The RAR's uncompressed cabinet is the only selected member.
  $mirror = Join-Path $work 'mirror'; $official = Join-Path $work 'official'
  Expand-Archive -LiteralPath $zip -DestinationPath $mirror
  & $seven x '-y' "-o$official" $rar 'HTKK_5.8.1_DLL_signed/Data1.cab' *> (Join-Path $work 'extract-private.log')
  if ($LASTEXITCODE -ne 0) { throw 'OFFICIAL_CAB_EXTRACTION_FAILED' }
  $source = Join-Path $mirror 'HTKK_5.8.1_DLL_signed'
  $cab = Join-Path $source 'Data1.cab'; $officialCab = Join-Path $official 'HTKK_5.8.1_DLL_signed\Data1.cab'
  Assert-Hash $cab '00669905937fb29e10cb53209ece5e8a9f8097970e4cb40bb28f89baa9fc3744'
  Assert-Hash $officialCab '00669905937fb29e10cb53209ece5e8a9f8097970e4cb40bb28f89baa9fc3744'
  $report.officialCabMatchesMirror = $true
  $msi = Join-Path $source 'HTKK.msi'
  Assert-Hash $msi '7c1da251ee2acd126a2363e4457502b8ad6fc0792d78dc0a92b153701dc29080'
  $report.stage = 'verify-msi'
  $signature = Get-AuthenticodeSignature -LiteralPath $msi
  if ($signature.Status -ne 'Valid' -or $null -eq $signature.SignerCertificate -or $null -eq $signature.TimeStamperCertificate) { throw 'MSI_AUTHENTICODE_NOT_VALID' }
  if ($signature.SignerCertificate.SerialNumber -ne '6435F70483012A5DBC374003') { throw 'MSI_PUBLISHER_SERIAL_MISMATCH' }
  if ($signature.SignerCertificate.Subject -notmatch 'Tổng Cục Thuế') { throw 'MSI_PUBLISHER_SUBJECT_MISMATCH' }
  $signTool = Get-ChildItem 'C:\Program Files (x86)\Windows Kits\10\bin\*\x64\signtool.exe' -ErrorAction SilentlyContinue | Sort-Object FullName -Descending | Select-Object -First 1
  if ($null -eq $signTool) { throw 'RUNNER_SIGNTOOL_MISSING' }
  & $signTool.FullName verify /pa /all /v $msi *> (Join-Path $work 'signature-private.log')
  if ($LASTEXITCODE -ne 0) { throw 'MSI_SIGNTOOL_VERIFICATION_FAILED' }
  $report.msiAuthenticodeValid = $true
  $report.stage = 'framework-check'
  $framework = Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\NET Framework Setup\NDP\v3.5' -ErrorAction SilentlyContinue
  $feature = Get-WindowsOptionalFeature -Online -FeatureName NetFx3
  if ($null -eq $framework -or $framework.Install -ne 1 -or $feature.State -ne 'Enabled') { throw 'NETFX35_MISSING_NO_BOOTSTRAPPER_EXECUTED' }
  $report.netFx35Present = $true
  if (-not $InstallAndProbe) { $report.stage = 'verified-install-not-requested'; return }
  # Execute only the pinned, publisher-verified MSI after official-distribution CAB equivalence.
  $report.stage = 'install'
  $install = Start-Process -FilePath "$env:WINDIR\System32\msiexec.exe" -ArgumentList @('/i', "`"$msi`"", '/qn', '/norestart', 'ISCHECKFORPRODUCTUPDATES=0', '/L*v', "`"$(Join-Path $work 'install-private.log')`"") -Wait -PassThru
  $report.installExitCode = $install.ExitCode
  if ($install.ExitCode -notin @(0, 3010)) { throw 'MSI_INSTALL_FAILED' }
  if ($install.ExitCode -eq 3010) { throw 'REBOOT_REQUIRED_PROBE_NOT_RUN' }
  $candidates = @("${env:ProgramFiles}\HTKK\Project\HTKK.exe", "${env:ProgramFiles(x86)}\HTKK\Project\HTKK.exe", 'C:\HTKK\Project\HTKK.exe')
  $exe = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
  if (-not $exe) { throw 'INSTALLED_HTKK_NOT_FOUND' }
  Assert-Hash $exe '411141d2e728a45f4a35a876afb169d0ac2450de2499e8a1f43ac29ab6401938'
  # Prevent the application from contacting its legacy update endpoint during the startup probe.
  New-NetFirewallRule -DisplayName 'HTKK readiness probe outbound block' -Direction Outbound -Program $exe -Action Block | Out-Null
  $report.stage = 'startup'
  $process = Start-Process -FilePath $exe -WorkingDirectory (Split-Path $exe) -PassThru
  $report.processStarted = $true
  Start-Sleep -Seconds 15
  $process.Refresh()
  $report.processAliveAfterWait = -not $process.HasExited
  if (-not $process.HasExited) { $report.windowObserved = $process.MainWindowHandle -ne [IntPtr]::Zero }
  if (-not $report.windowObserved) { throw 'STARTUP_WINDOW_NOT_OBSERVED' }
  $report.stage = 'startup-window-observed'
} catch {
  # Only allow fixed diagnostic enums into the public summary. Never dump remote/installer output.
  $known = @('SOURCE_HASH_MISMATCH','TRUSTED_RUNNER_7ZIP_MISSING','OFFICIAL_CAB_EXTRACTION_FAILED','MSI_AUTHENTICODE_NOT_VALID','MSI_PUBLISHER_SERIAL_MISMATCH','MSI_PUBLISHER_SUBJECT_MISMATCH','RUNNER_SIGNTOOL_MISSING','MSI_SIGNTOOL_VERIFICATION_FAILED','NETFX35_MISSING_NO_BOOTSTRAPPER_EXECUTED','MSI_INSTALL_FAILED','REBOOT_REQUIRED_PROBE_NOT_RUN','INSTALLED_HTKK_NOT_FOUND','STARTUP_WINDOW_NOT_OBSERVED')
  $reason = $_.Exception.Message
  $report['blockedReason'] = if ($reason -in $known) { $reason } else { 'HOST_NETWORK_OR_TOOL_FAILURE' }
  $report.stage = 'blocked'
} finally {
  if ($null -ne $process -and -not $process.HasExited) { Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue }
  $safe = $report | ConvertTo-Json -Depth 3
  Write-Output $safe
  if ($env:GITHUB_STEP_SUMMARY) { Add-Content -LiteralPath $env:GITHUB_STEP_SUMMARY -Value ('```json' + "`n" + $safe + "`n" + '```') }
  Remove-Item -LiteralPath $work -Recurse -Force -ErrorAction SilentlyContinue
}
if ($report.stage -eq 'blocked') { exit 1 }
