# Probe only public portable output. Never publish downloaded content or raw diagnostics.
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
Set-StrictMode -Version Latest
$expectedSource = [string]$env:EXPECTED_SOURCE_SHA
$cacheKey = if ($expectedSource) { '?commit=' + $expectedSource } else { '' }
$report = [ordered]@{ manifestParser = 'system-text-json-strings'; publishedManifestTypesValid = $false; publishedSourceMatchesExpected = $false; embeddedManifestTypesValid = $false; embeddedSourceMatchesExpected = $false; embeddedPublishedMetadataMatches = $false; packageSourceSha = $null; packageVersion = $null; sourceProvenanceValid = $false; stage = 'started'; packageSha256 = $null; packageChecksumValid = $false; archivePathsSafe = $false; nodeArchivePinned = $false; nodePayloadMatches = $false; licenseMatches = $false; nodeVersionValid = $false; launcherValid = $false; processStarted = $false; rootHttpOk = $false; dashboardHttpOk = $false; wasmMimeValid = $false; mjsMimeValid = $false; loopbackOnly = $false; browserInteractionTested = $false; userDataUsed = $false }
$work = Join-Path $env:RUNNER_TEMP ('portable-probe-' + [guid]::NewGuid().ToString('N'))
$server = $null
function Assert-Hash([string]$Path,[string]$Expected) {
  if ((Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $Expected) { throw 'CHECKSUM_MISMATCH' }
}
function Get-PublicFile([string]$Url,[string]$Destination) {
  # No redirect downgrade, credentials, cookies, proxy bypass or TLS override.
  Invoke-WebRequest -Uri $Url -OutFile $Destination -TimeoutSec 120 -MaximumRedirection 0 -UserAgent 'HotroKeKhai-PortableProbe/1.0'
}
# ConvertFrom-Json may coerce ISO timestamps to DateTime in newer PowerShell.
# Read only JSON string tokens directly so every supported pwsh preserves their types.
function Read-BuildManifest([string]$Path) {
  Add-Type -AssemblyName System.Text.Json
  $options = [System.Text.Json.JsonDocumentOptions]::new()
  $options.MaxDepth = 8
  $document = [System.Text.Json.JsonDocument]::Parse([IO.File]::ReadAllText($Path), $options)
  try {
    if ($document.RootElement.ValueKind -ne [System.Text.Json.JsonValueKind]::Object) { throw 'INVALID_BUILD_MANIFEST' }
    $result = @{}
    foreach ($property in $document.RootElement.EnumerateObject()) {
      if ($property.Name -notin @('sourceSha','version','builtAt')) { continue }
      if ($result.ContainsKey($property.Name) -or $property.Value.ValueKind -ne [System.Text.Json.JsonValueKind]::String) { throw 'INVALID_BUILD_MANIFEST' }
      $result[$property.Name] = $property.Value.GetString()
    }
    if ($result.Count -ne 3) { throw 'INVALID_BUILD_MANIFEST' }
    return $result
  } finally { $document.Dispose() }
}
function Expand-StrictZip([string]$Archive,[string]$Destination,[string]$Prefix) {
  New-Item -ItemType Directory -Path $Destination | Out-Null
  $base = [IO.Path]::GetFullPath($Destination) + [IO.Path]::DirectorySeparatorChar
  $zip = [IO.Compression.ZipFile]::OpenRead($Archive)
  try {
    if ($zip.Entries.Count -gt 20000) { throw 'ARCHIVE_LIMIT_EXCEEDED' }
    $names = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    [long]$total = 0
    foreach ($entry in $zip.Entries) {
      $name = $entry.FullName.Replace('\','/')
      $total += $entry.Length
      $unixType = ($entry.ExternalAttributes -shr 16) -band 0xf000
      if ($total -gt 600MB -or $name.Contains(':') -or $name.StartsWith('/') -or $name.Split('/') -contains '..' -or $name.Split('/') -contains '.' -or -not $name.StartsWith($Prefix + '/', [StringComparison]::Ordinal) -or $unixType -eq 0xa000 -or ($entry.ExternalAttributes -band 0x400) -ne 0 -or -not $names.Add($name)) { throw 'UNSAFE_ARCHIVE_ENTRY' }
      foreach ($segment in $name.TrimEnd('/').Split('/')) {
        if ($segment.Length -eq 0 -or $segment.EndsWith('.') -or $segment.EndsWith(' ') -or $segment.IndexOfAny([IO.Path]::GetInvalidFileNameChars()) -ge 0 -or $segment -match '^(?i:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)') { throw 'UNSAFE_ARCHIVE_ENTRY' }
      }
      $target = [IO.Path]::GetFullPath((Join-Path $Destination $name))
      if (-not $target.StartsWith($base,[StringComparison]::OrdinalIgnoreCase)) { throw 'UNSAFE_ARCHIVE_ENTRY' }
      if ($name.EndsWith('/')) { [IO.Directory]::CreateDirectory($target) | Out-Null; continue }
      [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($target)) | Out-Null
      $inputStream = $entry.Open(); $outputStream = [IO.File]::Open($target,[IO.FileMode]::CreateNew)
      try { $inputStream.CopyTo($outputStream) } finally { $inputStream.Dispose(); $outputStream.Dispose() }
    }
  } finally { $zip.Dispose() }
}
function Start-CleanNode([string]$Exe,[string[]]$Arguments,[string]$Directory) {
  $info = [Diagnostics.ProcessStartInfo]::new()
  $info.FileName = $Exe; $info.WorkingDirectory = $Directory; $info.UseShellExecute = $false; $info.CreateNoWindow = $true
  $info.RedirectStandardOutput = $true; $info.RedirectStandardError = $true
  $info.Environment.Clear()
  foreach ($key in @('SystemRoot','WINDIR','TEMP','TMP','PATH')) { $value = [Environment]::GetEnvironmentVariable($key); if ($null -ne $value) { $info.Environment[$key] = $value } }
  foreach ($argument in $Arguments) { $info.ArgumentList.Add($argument) }
  return [Diagnostics.Process]::Start($info)
}
try {
  New-Item -ItemType Directory -Path $work | Out-Null
  if ($expectedSource -and $expectedSource -cnotmatch '^[0-9a-f]{40}\z') { throw 'INVALID_EXPECTED_SOURCE' }
  $report.stage = 'download'
  $publishedBuild = $null
  if ($expectedSource) {
    $buildFile = Join-Path $work 'published-build.json'
    Get-PublicFile ('https://hotrokekhai.net/build.json' + $cacheKey) $buildFile
    if ((Get-Item -LiteralPath $buildFile).Length -gt 4096) { throw 'INVALID_BUILD_MANIFEST' }
    $publishedBuild = Read-BuildManifest $buildFile
    $report.publishedManifestTypesValid = $true
    $report.publishedSourceMatchesExpected = $publishedBuild.sourceSha -ceq $expectedSource
    if ($publishedBuild -isnot [Collections.IDictionary] -or $publishedBuild.sourceSha -isnot [string] -or $publishedBuild.version -isnot [string] -or $publishedBuild.builtAt -isnot [string] -or $publishedBuild.sourceSha -cne $expectedSource -or $publishedBuild.version -cnotmatch '^[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?\z') { throw 'PACKAGE_SOURCE_MISMATCH' }
  }
  $manifest = Join-Path $work 'SHA256SUMS'; $package = Join-Path $work 'portable.zip'
  Get-PublicFile ('https://hotrokekhai.net/downloads/SHA256SUMS' + $cacheKey) $manifest
  $checksumMatches = [regex]::Matches([IO.File]::ReadAllText($manifest),'(?im)^([a-f0-9]{64})[ \t]+\*?hotrokekhai-portable\.zip[ \t]*\r?$')
  if ($checksumMatches.Count -ne 1) { throw 'INVALID_PACKAGE_MANIFEST' }
  $expected = $checksumMatches[0].Groups[1].Value.ToLowerInvariant()
  Get-PublicFile ('https://hotrokekhai.net/downloads/hotrokekhai-portable.zip' + $cacheKey) $package
  Assert-Hash $package $expected; $report.packageChecksumValid = $true; $report.packageSha256 = $expected
  $report.stage = 'extract'
  $extracted = Join-Path $work 'package'
  Expand-StrictZip $package $extracted 'hotrokekhai-portable'
  $root = Join-Path $extracted 'hotrokekhai-portable'
  foreach ($entry in Get-ChildItem -LiteralPath $root) { if ($entry.Name -notin @('web','runtime','serve.mjs','start.bat','start.sh','HUONG-DAN.txt')) { throw 'UNEXPECTED_PACKAGE_LAYOUT' } }
  foreach ($path in @('runtime/node.exe','runtime/LICENSE','runtime/SOURCE.txt','serve.mjs','start.bat','web/index.html','web/dashboard/index.html')) { if (-not (Test-Path -LiteralPath (Join-Path $root $path) -PathType Leaf)) { throw 'UNEXPECTED_PACKAGE_LAYOUT' } }
  $report.archivePathsSafe = $true
  $embeddedBuild = Join-Path $root 'web/build.json'
  if (Test-Path -LiteralPath $embeddedBuild -PathType Leaf) {
    if ((Get-Item -LiteralPath $embeddedBuild).Length -gt 4096) { throw 'INVALID_BUILD_MANIFEST' }
    $build = Read-BuildManifest $embeddedBuild
    $report.embeddedManifestTypesValid = $true
    if ($expectedSource) {
      $report.embeddedSourceMatchesExpected = $build.sourceSha -ceq $expectedSource
      $report.embeddedPublishedMetadataMatches = $build.version -ceq $publishedBuild.version -and $build.builtAt -ceq $publishedBuild.builtAt
    }
    if ($build -isnot [Collections.IDictionary] -or $build.sourceSha -isnot [string] -or $build.version -isnot [string] -or $build.builtAt -isnot [string] -or $build.sourceSha -cnotmatch '^[0-9a-f]{40}\z' -or $build.version -cnotmatch '^[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?\z') { throw 'INVALID_BUILD_MANIFEST' }
    if ($expectedSource -and ($build.sourceSha -cne $expectedSource -or $build.version -cne $publishedBuild.version -or $build.builtAt -cne $publishedBuild.builtAt)) { throw 'PACKAGE_SOURCE_MISMATCH' }
    $report.packageSourceSha = $build.sourceSha; $report.packageVersion = $build.version
    $report.sourceProvenanceValid = [bool]$expectedSource
  } elseif ($expectedSource) { throw 'INVALID_BUILD_MANIFEST' }
  $report.stage = 'verify-node'
  $nodeZip = Join-Path $work 'official-node.zip'
  Get-PublicFile 'https://nodejs.org/dist/v24.22.1/node-v24.22.1-win-x64.zip' $nodeZip
  Assert-Hash $nodeZip 'd2046d28c2c3dcd211ac5145c0bf30e2047ef9dfb306693c8c6e2eccd8b95fa5'; $report.nodeArchivePinned = $true
  $official = Join-Path $work 'official-node'
  Expand-StrictZip $nodeZip $official 'node-v24.22.1-win-x64'
  $node = Join-Path $root 'runtime/node.exe'
  Assert-Hash $node (Get-FileHash -LiteralPath (Join-Path $official 'node-v24.22.1-win-x64/node.exe') -Algorithm SHA256).Hash.ToLowerInvariant()
  $report.nodePayloadMatches = $true
  Assert-Hash (Join-Path $root 'runtime/LICENSE') (Get-FileHash -LiteralPath (Join-Path $official 'node-v24.22.1-win-x64/LICENSE') -Algorithm SHA256).Hash.ToLowerInvariant()
  $report.licenseMatches = $true
  $launcher = [IO.File]::ReadAllText((Join-Path $root 'start.bat')).Replace("`r`n","`n")
  if ($launcher -cne "@echo off`ncd /d `"%~dp0`"`nruntime\node.exe serve.mjs web 4173`npause`n") { throw 'UNEXPECTED_LAUNCHER' }
  $report.launcherValid = $true
  $version = Start-CleanNode $node @('--version') $root
  try { if (-not $version.WaitForExit(10000)) { $version.Kill($true); throw 'NODE_VERSION_FAILED' }; if ($version.ExitCode -ne 0 -or $version.StandardOutput.ReadToEnd().Trim() -ne 'v24.22.1') { throw 'NODE_VERSION_FAILED' } } finally { $version.Dispose() }
  $report.nodeVersionValid = $true
  if (@(Get-NetTCPConnection -LocalPort 4173 -State Listen -ErrorAction SilentlyContinue).Count -gt 0) { throw 'PORT_ALREADY_IN_USE' }
  $report.stage = 'serve'
  $server = Start-CleanNode $node @('serve.mjs','web','4173') $root
  # Drain redirected streams asynchronously so no child output can reach public logs or block it.
  $stdoutTask = $server.StandardOutput.ReadToEndAsync(); $stderrTask = $server.StandardError.ReadToEndAsync()
  $report.processStarted = $true
  $ready = $false
  for ($attempt = 0; $attempt -lt 20; $attempt++) {
    if ($server.HasExited) { throw 'SERVER_EXITED' }
    try { $response = Invoke-WebRequest -Uri 'http://127.0.0.1:4173/' -TimeoutSec 2; if ($response.StatusCode -eq 200) { $ready = $true; break } } catch { }
    Start-Sleep -Milliseconds 500
  }
  if (-not $ready) { throw 'SERVER_NOT_READY' }
  $report.rootHttpOk = $response.StatusCode -eq 200 -and $response.Content -match 'Hỗ trợ kê khai|hỗ trợ kê khai'
  $dashboard = Invoke-WebRequest -Uri 'http://127.0.0.1:4173/dashboard/' -TimeoutSec 10
  $report.dashboardHttpOk = $dashboard.StatusCode -eq 200 -and $dashboard.Content -match 'HTKK'
  $listeners = @(Get-NetTCPConnection -LocalPort 4173 -State Listen)
  $report.loopbackOnly = $listeners.Count -eq 1 -and $listeners[0].LocalAddress -eq '127.0.0.1' -and $listeners[0].OwningProcess -eq $server.Id
  foreach ($extension in @('wasm','mjs')) {
    $asset = Get-ChildItem -LiteralPath (Join-Path $root 'web') -Filter ('*.' + $extension) -File -Recurse | Select-Object -First 1
    if ($null -eq $asset) { throw 'VALIDATOR_ASSET_MISSING' }
    $relative = [IO.Path]::GetRelativePath((Join-Path $root 'web'),$asset.FullName).Replace('\','/')
    $assetResponse = Invoke-WebRequest -Uri ('http://127.0.0.1:4173/' + $relative) -TimeoutSec 10
    $expectedMime = if ($extension -eq 'wasm') { 'application/wasm' } else { 'text/javascript' }
    $valid = $assetResponse.StatusCode -eq 200 -and ([string]$assetResponse.Headers['Content-Type']).StartsWith($expectedMime,[StringComparison]::OrdinalIgnoreCase)
    if ($extension -eq 'wasm') { $report.wasmMimeValid = $valid } else { $report.mjsMimeValid = $valid }
  }
  if (-not ($report.rootHttpOk -and $report.dashboardHttpOk -and $report.loopbackOnly -and $report.wasmMimeValid -and $report.mjsMimeValid)) { throw 'HTTP_VALIDATION_FAILED' }
  $report.stage = 'windows-runtime-and-http-verified'
} catch {
  $known = @('INVALID_EXPECTED_SOURCE','INVALID_BUILD_MANIFEST','PACKAGE_SOURCE_MISMATCH','CHECKSUM_MISMATCH','ARCHIVE_LIMIT_EXCEEDED','UNSAFE_ARCHIVE_ENTRY','INVALID_PACKAGE_MANIFEST','UNEXPECTED_PACKAGE_LAYOUT','UNEXPECTED_LAUNCHER','NODE_VERSION_FAILED','PORT_ALREADY_IN_USE','SERVER_EXITED','SERVER_NOT_READY','VALIDATOR_ASSET_MISSING','HTTP_VALIDATION_FAILED')
  $report.stage = 'blocked'; $report['blockedReason'] = if ($_.Exception.Message -in $known) { $_.Exception.Message } else { 'HOST_NETWORK_OR_TOOL_FAILURE' }
} finally {
  if ($null -ne $server) { if (-not $server.HasExited) { $server.Kill($true); $server.WaitForExit(5000) | Out-Null }; $server.Dispose() }
  Remove-Item -LiteralPath $work -Recurse -Force -ErrorAction SilentlyContinue
  $safe = $report | ConvertTo-Json -Depth 3
  Write-Output $safe
  if ($env:GITHUB_STEP_SUMMARY) { Add-Content -LiteralPath $env:GITHUB_STEP_SUMMARY -Value ('```json' + "`n" + $safe + "`n" + '```') }
}
if ($report.stage -eq 'blocked') { exit 1 }
