# Production wrapper policy and actual Windows descendant lifecycle tests.
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'Invoke-HtkkBoundedJobProcess.ps1')
$productionFactory=${function:New-HtkkBoundedJobOwner}
$script:fixture='normal';$script:disposeCalls=0;$script:waitCalls=0
function New-HtkkBoundedJobOwner {
 param($Executable,$WorkingDirectory,$Arguments)
 if($script:fixture -eq 'throw'){throw 'unexpected private fixture failure'}
 if($script:fixture -eq 'missing'){throw [InvalidOperationException]::new('process-create-failed')}
 $owner=[pscustomobject]@{CleanupVerified=$false;RootExitCode=[uint32]7}
 if($script:fixture -eq 'signed'){$owner.RootExitCode=[uint32]::MaxValue}
 $owner|Add-Member ScriptMethod WaitForRootExit {
  param($milliseconds)
  $script:waitCalls++
  if($milliseconds -ne 30000){throw 'Wrapper changed native deadline'}
  if($script:fixture -eq 'wait-error'){throw 'private wait failure'}
  return $script:fixture -ne 'timeout'
 }
 $owner|Add-Member ScriptMethod Dispose {
  $script:disposeCalls++
  if($script:fixture -eq 'cleanup'){throw 'private cleanup failure'}
  $this.CleanupVerified=$true
 }
 return $owner
}
$script:htkkHelperJobsStopped=$true
foreach($case in @(@('normal','exited',7),@('signed','exited',-1),@('timeout','process-timeout',$null),@('wait-error','process-tool-failure',$null),@('missing','process-tool-failure',$null),@('cleanup','cleanup-not-verified',7),@('throw','cleanup-not-verified',$null))){
 $script:fixture=$case[0]
 $value=Invoke-HtkkBoundedJobProcess -Executable 'fixture' -WorkingDirectory 'fixture'
 if($value.status -cne $case[1] -or $value.exitCode -ne $case[2]){throw 'Bounded job policy outcome mismatch'}
 if($value.Count -ne 9 -or @($value.Keys|Where-Object{$_ -notin @('status','started','timedOut','processStopped','jobCleanupVerified','exitCode','timeoutMilliseconds','childEnvironmentPolicy','lifetimeBoundary')}).Count){throw 'Unbounded job result fields'}
 if($case[0] -eq 'timeout' -and (-not $value.timedOut -or -not $value.jobCleanupVerified)){throw 'Timeout cleanup result lost'}
}
if($script:disposeCalls -ne 5 -or $script:waitCalls -ne 5){throw 'Wrapper repeated or skipped cleanup/wait'}
if($script:htkkHelperJobsStopped){throw 'Unverified cleanup allowed credentials'}
$script:fixture='normal';$null=Invoke-HtkkBoundedJobProcess -Executable fixture -WorkingDirectory fixture
if($script:htkkHelperJobsStopped){throw 'Later helper success erased cleanup failure'}
Set-Item Function:New-HtkkBoundedJobOwner $productionFactory
Write-Host 'Bounded job wrapper policy checks passed: 8 scenarios'
if(-not $IsWindows){Write-Host 'Bounded job wrapper Win32 process integration NOT RUN on this platform';return}

$directory=Join-Path $env:RUNNER_TEMP ('htkk-bounded-job-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $directory|Out-Null
$child=Join-Path $directory 'job child fixture.ps1';$marker=Join-Path $directory 'descendant.txt'
$hostExecutable=[Diagnostics.Process]::GetCurrentProcess().MainModule.FileName
$previous=[Environment]::GetEnvironmentVariable('HTKK_TEST_FAKE_CREDENTIAL')
try{
 [Environment]::SetEnvironmentVariable('HTKK_TEST_FAKE_CREDENTIAL','test-only-sentinel')
 @'
param([string]$Mode,[string]$Marker,[string]$HostExecutable)
if([Environment]::GetEnvironmentVariable('HTKK_TEST_FAKE_CREDENTIAL')){exit 91}
[Console]::Out.WriteLine('private-native-output-must-not-escape')
[Console]::Error.WriteLine('private-native-error-must-not-escape')
if($Mode -eq 'descendant'){
 [IO.File]::WriteAllText($Marker,[string]$PID)
 Start-Sleep -Seconds 60
 exit 0
}
if($Mode -eq 'spawn'){
 $info=[Diagnostics.ProcessStartInfo]::new();$info.FileName=$HostExecutable;$info.UseShellExecute=$false;$info.CreateNoWindow=$true
 foreach($argument in @('-NoLogo','-NoProfile','-NonInteractive','-File',$PSCommandPath,'descendant',$Marker,$HostExecutable)){$info.ArgumentList.Add($argument)}
 $descendant=[Diagnostics.Process]::Start($info)
 $clock=[Diagnostics.Stopwatch]::StartNew()
 while(-not(Test-Path -LiteralPath $Marker)){if($clock.ElapsedMilliseconds -gt 10000){exit 92};Start-Sleep -Milliseconds 20}
 $descendant.Dispose()
 exit 7
}
if($Mode -eq 'hang'){
 [IO.File]::WriteAllText($Marker,[string]$PID)
 Start-Sleep -Seconds 60
}
exit 7
'@|Set-Content -LiteralPath $child -Encoding utf8BOM
 $script:htkkHelperJobsStopped=$true
 $fixtureArguments=@('-NoLogo','-NoProfile','-NonInteractive','-File',$child,'spawn',$marker,$hostExecutable)
 $normal=Invoke-HtkkBoundedJobProcess -Executable $hostExecutable -WorkingDirectory $directory -Arguments $fixtureArguments
 if($normal.status -cne 'exited' -or $normal.exitCode -ne 7 -or -not $normal.jobCleanupVerified -or -not $script:htkkHelperJobsStopped){throw 'Actual orphan job wrapper cleanup failed'}
 if(-not(Test-Path -LiteralPath $marker)){throw 'Orphan fixture did not run'}
 $childId=[int][IO.File]::ReadAllText($marker)
 if(Get-Process -Id $childId -ErrorAction SilentlyContinue){throw 'Orphan descendant remained alive'}
 Remove-Item -LiteralPath $marker
 $fixtureArguments[5]='hang';$clock=[Diagnostics.Stopwatch]::StartNew()
 $timeout=Invoke-HtkkBoundedJobProcess -Executable $hostExecutable -WorkingDirectory $directory -Arguments $fixtureArguments -TimeoutMilliseconds 2500
 if($timeout.status -cne 'process-timeout' -or -not $timeout.timedOut -or -not $timeout.jobCleanupVerified -or $clock.Elapsed.TotalSeconds -gt 9){throw 'Actual bounded job timeout failed'}
 if(-not(Test-Path -LiteralPath $marker)){throw 'Timeout fixture did not run'}
 if(Get-Process -Id ([int][IO.File]::ReadAllText($marker)) -ErrorAction SilentlyContinue){throw 'Timed out root remained alive'}
 $missing=Invoke-HtkkBoundedJobProcess -Executable (Join-Path $directory 'missing.exe') -WorkingDirectory $directory
 if($missing.status -cne 'process-tool-failure' -or $missing.started -or -not $missing.jobCleanupVerified){throw 'Native launch failure cleanup lost'}
 Write-Host 'Bounded job actual Windows integration passed: orphan cleanup, timeout, environment isolation, missing image'
}finally{
 [Environment]::SetEnvironmentVariable('HTKK_TEST_FAKE_CREDENTIAL',$previous)
 Remove-Item -LiteralPath $directory -Recurse -Force -ErrorAction SilentlyContinue
}
