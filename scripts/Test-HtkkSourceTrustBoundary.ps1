# Fault injection in a temporary copy of our own controller only; no vendor input/execution.
$ErrorActionPreference='Stop'
if(-not $IsWindows){Write-Output 'Source trust launch-failure runtime checks require Windows';return}
$work=Join-Path $env:RUNNER_TEMP ('htkk-trust-boundary-'+[Guid]::NewGuid().ToString('N'));$null=[IO.Directory]::CreateDirectory($work)
try{
 $original=[IO.File]::ReadAllText((Join-Path $PSScriptRoot 'Test-HtkkSourceCandidateTrust.ps1'))
 $launch='(?m)^  \$owner=New-HtkkBoundedJobOwner[^\r\n]*\r?$'
 if([regex]::Matches($original,$launch).Count -ne 1){throw 'TRUST_CONTROLLER_ANCHOR'}
 $count=0
 foreach($case in @(@('unclassified-fixture-launch',$false),@('job-assignment-failed',$true))){
  $source=Join-Path $work ('scripts'+$count);$candidate=Join-Path $work ('candidate'+$count);$null=[IO.Directory]::CreateDirectory($source);$null=[IO.Directory]::CreateDirectory($candidate)
  foreach($name in @('HtkkSourceCabinet.cs','Invoke-HtkkBoundedJobProcess.ps1')){[IO.File]::Copy((Join-Path $PSScriptRoot $name),(Join-Path $source $name))}
  $copy=Join-Path $source 'controller.ps1';$result=Join-Path $work ('result'+$count+'.json')
  $fault="  throw [InvalidOperationException]::new('"+$case[0]+"')"
  [IO.File]::WriteAllText($copy,[regex]::Replace($original,$launch,[Text.RegularExpressions.MatchEvaluator]{param($match) $fault}))
  & $copy -CandidateDirectory $candidate -ResultPath $result
  $r=Get-Content -LiteralPath $result -Raw | ConvertFrom-Json
  if($r.status -cne 'blocked' -or $r.ready -or $r.workerStopped -ne $case[1] -or $r.jobCleanupVerified -ne $case[1]){throw 'TRUST_LAUNCH_FAILURE_NOT_FAIL_CLOSED'}
  if(-not $case[1] -and $r.failureCode -cne 'WORKER_CLEANUP'){throw 'UNCLASSIFIED_LAUNCH_NOT_BLOCKED'}
  $count++
 }
 Write-Output 'Source trust actual controller launch-failure checks passed: 2'
}finally{Remove-Item -LiteralPath $work -Recurse -Force}
