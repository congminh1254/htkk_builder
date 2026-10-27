# Actual child-process tests: no HTKK/MSI execution or network required.
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'Invoke-HtkkBoundedNativeProcess.ps1')
$directory=Join-Path $env:RUNNER_TEMP ('htkk-native-boundary-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $directory|Out-Null
$child=Join-Path $directory 'child.ps1'
$marker=Join-Path $directory 'marker.txt'
$hostExecutable=[Diagnostics.Process]::GetCurrentProcess().MainModule.FileName
$previous=[Environment]::GetEnvironmentVariable('HTKK_TEST_FAKE_CREDENTIAL')
try{
 [Environment]::SetEnvironmentVariable('HTKK_TEST_FAKE_CREDENTIAL','test-only-sentinel')
 @'
param([string]$Marker,[string]$Mode)
if([Environment]::GetEnvironmentVariable('HTKK_TEST_FAKE_CREDENTIAL')){exit 91}
[IO.File]::WriteAllText($Marker,[string]$PID)
[Console]::Out.WriteLine('native-output-must-not-escape')
[Console]::Error.WriteLine('native-error-must-not-escape')
if($Mode -eq 'hang'){Start-Sleep -Seconds 30}
exit 7
'@|Set-Content -LiteralPath $child -Encoding utf8NoBOM
 $normal=Invoke-HtkkBoundedNativeProcess -Executable $hostExecutable -WorkingDirectory $directory -Arguments @('-NoLogo','-NoProfile','-NonInteractive','-File',$child,$marker,'normal') -TimeoutMilliseconds 10000
 if($normal.status -cne 'exited' -or $normal.exitCode -ne 7 -or -not $normal.started -or $normal.timedOut -or -not $normal.processStopped -or -not(Test-Path -LiteralPath $marker)){throw 'Normal native process/isolation failed'}
 Remove-Item -LiteralPath $marker
 $clock=[Diagnostics.Stopwatch]::StartNew()
 $timeout=Invoke-HtkkBoundedNativeProcess -Executable $hostExecutable -WorkingDirectory $directory -Arguments @('-NoLogo','-NoProfile','-NonInteractive','-File',$child,$marker,'hang') -TimeoutMilliseconds 1500
 if($timeout.status -cne 'process-timeout' -or -not $timeout.timedOut -or -not $timeout.processStopped -or $null -ne $timeout.exitCode -or $clock.Elapsed.TotalSeconds -gt 10){throw 'Native timeout cleanup failed'}
 if(-not(Test-Path -LiteralPath $marker)){throw 'Timeout fixture did not reach child'}
 $childId=[int][IO.File]::ReadAllText($marker)
 if(Get-Process -Id $childId -ErrorAction SilentlyContinue){throw 'Timed out child remains alive'}
 $missing=Invoke-HtkkBoundedNativeProcess -Executable (Join-Path $directory 'missing.exe') -WorkingDirectory $directory -TimeoutMilliseconds 100
 if($missing.status -cne 'process-tool-failure' -or $missing.started -or -not $missing.processStopped){throw 'Missing tool boundary failed'}
 $keys=@('status','started','timedOut','processStopped','exitCode','timeoutMilliseconds','childEnvironmentPolicy')
 foreach($result in @($normal,$timeout,$missing)){if(@($result.Keys|Where-Object{$_ -notin $keys}).Count -or $result.Count -ne $keys.Count){throw 'Unbounded native result'}}
 Write-Host 'Bounded native process integration tests passed: exit/nonzero, environment isolation, timeout/termination, missing tool, fixed result schema'
}finally{
 [Environment]::SetEnvironmentVariable('HTKK_TEST_FAKE_CREDENTIAL',$previous)
 Remove-Item -LiteralPath $directory -Recurse -Force -ErrorAction SilentlyContinue
}
