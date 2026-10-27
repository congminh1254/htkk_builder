# Exercise the production installer control flow with deterministic native outcomes.
$ErrorActionPreference='Stop'
$source=[IO.File]::ReadAllText((Join-Path $PSScriptRoot 'probe-htkk-windows.ps1'))
$start=$source.IndexOf('  $installerCredentialsSafe=$false',[StringComparison]::Ordinal)
$end=$source.IndexOf('  $candidates =',$start,[StringComparison]::Ordinal)
if($start -lt 0 -or $end -le $start){throw 'Installer credential policy missing'}
$policy=[scriptblock]::Create($source.Substring($start,$end-$start))
function Invoke-HtkkBoundedNativeProcess {
 param($Executable,$WorkingDirectory,$Arguments,$TimeoutMilliseconds)
 if($script:installerFixture -ceq 'throw'){throw 'simulated internal boundary failure'}
 $result=@{processStopped=$true;status='exited';exitCode=0;timedOut=$false}
 switch($script:installerFixture){
  'timeout'{$result.timedOut=$true;$result.status='process-timeout';$result.exitCode=$null}
  'tool'{$result.status='process-tool-failure';$result.exitCode=$null}
  'cleanup'{$result.processStopped=$false;$result.status='cleanup-not-verified';$result.exitCode=$null}
  'nonzero'{$result.exitCode=1603}
  'reboot'{$result.exitCode=3010}
 }
 return $result
}
$work=$env:RUNNER_TEMP;$msi=Join-Path $work 'synthetic-not-executed.msi'
$cases=0
foreach($fixture in @('normal','timeout','tool','cleanup','nonzero','reboot','throw')){
 $script:installerFixture=$fixture;$report=@{};$installerCredentialsSafe=$true;$installerStopped=$true;$failed=$false
 try{. $policy}catch{$failed=$true}
 if($fixture -ceq 'normal'){
  if(-not $installerCredentialsSafe -or $failed){throw 'Normal installer completion rejected'}
 }else{
  if($installerCredentialsSafe -or -not $failed){throw 'Unverified installer completion permitted credentials'}
 }
 $cases++
}
Write-Host "Actual installer credential policy scenarios passed: $cases"
