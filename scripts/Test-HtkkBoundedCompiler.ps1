$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'Invoke-HtkkBoundedCompiler.ps1')
$productionFactory=${function:New-HtkkBoundedCompilerOwner}
$productionReader=${function:Get-HtkkBoundedCompilerCodes}
$directory=Join-Path $env:RUNNER_TEMP ('htkk-compiler-boundary-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $directory|Out-Null
$script:fixture='normal';$script:disposed=$false;$script:disposeCalls=0;$script:readCalls=0
function New-HtkkBoundedCompilerOwner {
 param($Executable,$WorkingDirectory,$Arguments,$StdoutPath,$StderrPath)
 $script:disposed=$false
 if($script:fixture -eq 'unknown'){throw 'private unexpected fixture message'}
 if($script:fixture -eq 'missing'){throw [InvalidOperationException]::new('process-create-failed')}
 [IO.File]::WriteAllText($StdoutPath,'private source/path sentinel: CS2020 CS1002 CS2020',[Text.Encoding]::UTF8)
 [IO.File]::WriteAllText($StderrPath,'private source/path sentinel: CS2020',[Text.Encoding]::UTF8)
 if($script:fixture -eq 'utf16'){[IO.File]::WriteAllText($StderrPath,'private diagnostic CS0001',[Text.Encoding]::Unicode)}
 if($script:fixture -eq 'many'){[IO.File]::WriteAllText($StdoutPath,((0..14|ForEach-Object{'CS'+$_.ToString('D4')}) -join ' '))}
 if($script:fixture -eq 'tokens'){[IO.File]::WriteAllText($StdoutPath,'CS1002 CS12345 cs1002 ACS2000 XCS1001 CS0002')}
 if($script:fixture -eq 'limit'){
  $body=[byte[]]::new(1048576);[Text.Encoding]::ASCII.GetBytes('CS0002 ').CopyTo($body,0)
  [IO.File]::WriteAllBytes($StderrPath,$body)
 }
 if($script:fixture -eq 'oversize'){[IO.File]::WriteAllBytes($StderrPath,[byte[]]::new(1048577))}
 if($script:fixture -eq 'absent'){Remove-Item -LiteralPath $StderrPath}
 $owner=[pscustomobject]@{CleanupVerified=$false;RootExitCode=[uint32]1}
 if($script:fixture -eq 'signed'){$owner.RootExitCode=[uint32]::MaxValue}
 $owner|Add-Member ScriptMethod WaitForRootExit {
  param($milliseconds)
  if($milliseconds -ne 30000){throw 'Compiler deadline changed'}
  if($script:fixture -eq 'wait-error'){throw 'private wait failure'}
  return $script:fixture -ne 'timeout'
 }
 $owner|Add-Member ScriptMethod Dispose {
  $script:disposeCalls++
  if($script:fixture -eq 'cleanup'){throw 'private cleanup failure'}
  $this.CleanupVerified=$true;$script:disposed=$true
 }
 return $owner
}
function Get-HtkkBoundedCompilerCodes {
 param($Paths,$MaximumBytes=1048576)
 if(-not $script:disposed){throw 'Compiler output was read before verified cleanup'}
 $script:readCalls++
 return & $productionReader -Paths $Paths -MaximumBytes $MaximumBytes
}
try{
 $script:htkkHelperJobsStopped=$true
 foreach($case in @(
  @('normal','exited',1,@('CS1002','CS2020')),
  @('signed','exited',-1,@('CS1002','CS2020')),
  @('utf16','exited',1,@('CS0001','CS1002','CS2020')),
  @('many','exited',1,@('CS0000','CS0001','CS0002','CS0003','CS0004','CS0005','CS0006','CS0007','CS0008','CS0009')),
  @('tokens','exited',1,@('CS0002','CS1002','CS2020')),
  @('limit','exited',1,@('CS0002','CS1002','CS2020')),
  @('oversize','compiler-output-invalid',1,@()),
  @('absent','compiler-output-invalid',1,@()),
  @('timeout','process-timeout',$null,@()),
  @('wait-error','process-tool-failure',$null,@()),
  @('missing','process-tool-failure',$null,@()),
  @('cleanup','cleanup-not-verified',1,@()),
  @('unknown','cleanup-not-verified',$null,@())
 )){
  $script:fixture=$case[0]
  $value=Invoke-HtkkBoundedCompiler -Executable fixture -WorkingDirectory $directory
  if($value.status -cne $case[1] -or $value.exitCode -ne $case[2] -or ($value.compilerErrorCodes -join ',') -cne ($case[3] -join ',')){throw 'Compiler boundary policy outcome mismatch'}
  if($value.Count -ne 11 -or @($value.Keys|Where-Object{$_ -notin @('status','started','timedOut','processStopped','jobCleanupVerified','exitCode','timeoutMilliseconds','compilerErrorCodes','diagnosticsVerified','childEnvironmentPolicy','lifetimeBoundary')}).Count){throw 'Unbounded compiler result fields'}
  if(($value|ConvertTo-Json -Compress) -match 'private|sentinel|stdout|stderr|fixture|compiler-boundary'){throw 'Compiler result exposed private output/path'}
  if($case[0] -eq 'timeout' -and (-not $value.timedOut -or $value.diagnosticsVerified)){throw 'Timed out compiler diagnostics treated as complete'}
 }
 if($script:disposeCalls -ne 11 -or $script:readCalls -ne 8){throw 'Compiler cleanup or read order changed'}
 if($script:htkkHelperJobsStopped){throw 'Compiler cleanup failure permitted credentials'}
 $script:fixture='normal';$null=Invoke-HtkkBoundedCompiler -Executable fixture -WorkingDirectory $directory
 if($script:htkkHelperJobsStopped){throw 'Later compiler success erased unsafe cleanup'}
 Set-Item Function:New-HtkkBoundedCompilerOwner $productionFactory
 Set-Item Function:Get-HtkkBoundedCompilerCodes $productionReader
 Write-Host 'Bounded compiler policy checks passed: 14 scenarios; raw output excluded'
 if(-not $IsWindows){Write-Host 'Bounded compiler Win32 integration NOT RUN on this platform';return}

 # Mocked cleanup-failure cases intentionally leave their files untouched.
 # A fresh subdirectory keeps that safety-policy evidence separate from real capture.
 $nativeDirectory=Join-Path $directory 'native';New-Item -ItemType Directory -Path $nativeDirectory|Out-Null
 $source=Join-Path $nativeDirectory 'private invalid compiler fixture.cs'
 [IO.File]::WriteAllText($source,'internal class Fixture { static void Main() { int value = ; } }')
 $compiler=Join-Path $env:WINDIR 'Microsoft.NET/Framework/v4.0.30319/csc.exe'
 if(-not(Test-Path -LiteralPath $compiler -PathType Leaf)){throw 'Trusted Windows compiler fixture missing'}
 $script:htkkHelperJobsStopped=$true
 $actual=Invoke-HtkkBoundedCompiler -Executable $compiler -WorkingDirectory $nativeDirectory -Arguments @('/nologo','/target:exe',('/out:'+(Join-Path $nativeDirectory 'fixture.exe')),$source)
 if($actual.status -cne 'exited' -or $actual.exitCode -eq 0 -or -not $actual.diagnosticsVerified -or -not $actual.jobCleanupVerified -or $actual.compilerErrorCodes -cnotcontains 'CS1525'){throw 'Actual compiler diagnostic capture failed'}
 if(($actual|ConvertTo-Json -Compress) -match 'private|fixture|\.cs|stdout|stderr'){throw 'Actual compiler source/path escaped'}
 if(@(Get-ChildItem -LiteralPath $nativeDirectory -Filter 'compiler-*').Count){throw 'Private compiler output files were not removed'}

 # Exercise timeout through the output-file API without running an untrusted tool.
 $child=Join-Path $nativeDirectory 'hanging compiler fixture.ps1';$marker=Join-Path $nativeDirectory 'timeout marker.txt'
 @'
param([string]$Marker)
if([Environment]::GetEnvironmentVariable('HTKK_TEST_FAKE_CREDENTIAL')){exit 91}
[IO.File]::WriteAllText($Marker,[string]$PID)
[Console]::Out.WriteLine('private timeout CS1002')
Start-Sleep -Seconds 60
'@|Set-Content -LiteralPath $child -Encoding utf8BOM
 $previous=[Environment]::GetEnvironmentVariable('HTKK_TEST_FAKE_CREDENTIAL')
 try{
  [Environment]::SetEnvironmentVariable('HTKK_TEST_FAKE_CREDENTIAL','test-only-sentinel')
  $hostExecutable=[Diagnostics.Process]::GetCurrentProcess().MainModule.FileName
  $timeout=Invoke-HtkkBoundedCompiler -Executable $hostExecutable -WorkingDirectory $nativeDirectory -Arguments @('-NoLogo','-NoProfile','-NonInteractive','-File',$child,$marker) -TimeoutMilliseconds 2500
  if($timeout.status -cne 'process-timeout' -or -not $timeout.jobCleanupVerified -or $timeout.diagnosticsVerified -or $timeout.compilerErrorCodes.Count){throw 'Actual compiler timeout capture boundary failed'}
  if(-not(Test-Path -LiteralPath $marker)){throw 'Compiler timeout fixture did not start'}
  if(Get-Process -Id ([int][IO.File]::ReadAllText($marker)) -ErrorAction SilentlyContinue){throw 'Timed out compiler fixture remained alive'}
 }finally{[Environment]::SetEnvironmentVariable('HTKK_TEST_FAKE_CREDENTIAL',$previous)}
 Write-Host 'Bounded compiler Windows integration passed: actual CS1525 capture, private raw output, timeout cleanup and environment isolation'
}finally{
 Remove-Item -LiteralPath $directory -Recurse -Force -ErrorAction SilentlyContinue
}
