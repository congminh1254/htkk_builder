# Actual supplier wrapper control flow, without starting HTKK or installer.
$ErrorActionPreference='Stop'
$tokens=$null;$errors=$null
$sourcePath=Join-Path $PSScriptRoot 'probe-htkk-windows.ps1'
$ast=[Management.Automation.Language.Parser]::ParseFile($sourcePath,[ref]$tokens,[ref]$errors)
if(@($errors).Count){throw 'Probe syntax invalid'}
foreach($name in @('Start-HtkkCleanProcess','Stop-HtkkSupplierJob')){
 $definition=$ast.Find({param($node) $node -is [Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -ceq $name},$true)
 if($null -eq $definition){throw 'Supplier wrapper missing'}
 Invoke-Expression $definition.Extent.Text
}
function New-JobFixture([string]$Scenario){
 $job=[pscustomobject]@{Scenario=$Scenario;CleanupVerified=($Scenario -cne 'unverified');ActiveProcesses=0;DisposeCount=0}
 if($Scenario -ceq 'active'){$job.ActiveProcesses=1}
 if($Scenario -ceq 'invalid-count'){$job.ActiveProcesses='0'}
 $job|Add-Member -MemberType ScriptMethod -Name Stop -Value {
  param($Milliseconds)
  if($Milliseconds -ne 5000){throw 'Unexpected stop deadline'}
  if($this.Scenario -ceq 'stop-throw'){throw 'synthetic stop failure'}
  if($this.Scenario -ceq 'stop-nonboolean'){return 1}
  return $this.Scenario -cne 'stop-false'
 }
 $job|Add-Member -MemberType ScriptMethod -Name WaitForRootExit -Value {
  param($Milliseconds)
  if($Milliseconds -ne 0){throw 'Unexpected root proof deadline'}
  if($this.Scenario -ceq 'wait-throw'){throw 'synthetic root wait failure'}
  if($this.Scenario -ceq 'root-nonboolean'){return 1}
  return $this.Scenario -cne 'root-live'
 }
 $job|Add-Member -MemberType ScriptMethod -Name Dispose -Value {
  $this.DisposeCount++
  if($this.Scenario -ceq 'dispose-throw'){throw 'synthetic disposal failure'}
 }
 return $job
}
$cases=0
foreach($scenario in @('normal','stop-false','stop-nonboolean','unverified','active','invalid-count','root-live','root-nonboolean','stop-throw','wait-throw','dispose-throw')){
 $job=New-JobFixture $scenario
 $result=Stop-HtkkSupplierJob -Job $job -LaunchAttempted $true
 if($job.DisposeCount -ne 1){throw 'Supplier job owner not disposed exactly once'}
 $expected=$scenario -ceq 'normal'
 if($result.cleanupVerified -ne $expected -or $result.supplierStopped -ne $expected){throw 'Unverified supplier job permitted credentials'}
 if($expected -and ($result.status -cne 'stopped-empty-job' -or -not $result.rootStopped -or -not $result.jobEmpty)){throw 'Supplier proof fields incomplete'}
 if($result.Count -ne 5 -or @($result.Keys|Where-Object{$_ -notin @('status','cleanupVerified','supplierStopped','rootStopped','jobEmpty')}).Count){throw 'Unbounded supplier result'}
 $cases++
}
$notLaunched=Stop-HtkkSupplierJob -Job $null -LaunchAttempted $false
if(-not $notLaunched.cleanupVerified -or $notLaunched.supplierStopped -or $notLaunched.status -cne 'not-launched'){throw 'No-launch boundary changed'};$cases++
$failedLaunch=Stop-HtkkSupplierJob -Job $null -LaunchAttempted $true
if($failedLaunch.cleanupVerified -or $failedLaunch.supplierStopped -or $failedLaunch.status -cne 'launch-cleanup-not-verified'){throw 'Missing launch owner permitted credentials'};$cases++
Write-Host "Actual supplier job cleanup wrapper scenarios passed: $cases"

if(-not $IsWindows){Write-Host 'Actual supplier launch wrapper Win32 integration NOT RUN on this platform';return}

# Compile a tiny OWN fixed-argument fixture; production launcher accepts no args.
. (Join-Path $PSScriptRoot 'Invoke-HtkkBoundedNativeProcess.ps1')
$directory=Join-Path $env:RUNNER_TEMP ('htkk-supplier-job-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $directory|Out-Null
$fixtureSource=Join-Path $directory 'Fixture.cs';$fixtureExe=Join-Path $directory 'Fixture.exe'
$rootMarker=Join-Path $directory 'root.txt';$grandMarker=Join-Path $directory 'grandchild.txt'
$previous=[Environment]::GetEnvironmentVariable('HTKK_TEST_FAKE_CREDENTIAL')
$job=$null;$descendant=$null
try{
 @'
using System;using System.Diagnostics;using System.IO;using System.Reflection;using System.Threading;
public static class Fixture {
 public static int Main(string[] args){
  if(Environment.GetEnvironmentVariable("HTKK_TEST_FAKE_CREDENTIAL")!=null)return 91;
  Console.Out.WriteLine("fixture-output-must-not-escape");Console.Error.WriteLine("fixture-error-must-not-escape");
  string directory=Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location);
  string grand=Path.Combine(directory,"grandchild.txt");
  if(args.Length==1&&args[0]=="--grandchild"){File.WriteAllText(grand,Process.GetCurrentProcess().Id.ToString());Thread.Sleep(60000);return 0;}
  File.WriteAllText(Path.Combine(directory,"root.txt"),Environment.GetEnvironmentVariable("PROCESSOR_ARCHITECTURE"));
  ProcessStartInfo info=new ProcessStartInfo(Assembly.GetExecutingAssembly().Location,"--grandchild");info.UseShellExecute=false;info.CreateNoWindow=true;
  using(Process child=Process.Start(info)){
   Stopwatch clock=Stopwatch.StartNew();
   while(true){try{if(File.Exists(grand)&&File.ReadAllText(grand)==child.Id.ToString())break;}catch(IOException){}if(clock.ElapsedMilliseconds>10000)return 92;Thread.Sleep(20);}
  }
  return 17;
 }
}
'@|Set-Content -LiteralPath $fixtureSource -Encoding utf8BOM
 $compiler=Join-Path $env:WINDIR 'Microsoft.NET\Framework\v4.0.30319\csc.exe'
 $compiled=Invoke-HtkkBoundedNativeProcess -Executable $compiler -WorkingDirectory $directory -Arguments @('/nologo','/target:exe','/platform:x86',('/out:'+$fixtureExe),$fixtureSource) -TimeoutMilliseconds 30000
 if($compiled.status -cne 'exited' -or $compiled.exitCode -ne 0 -or -not $compiled.processStopped -or -not(Test-Path -LiteralPath $fixtureExe)){throw 'Own supplier fixture compilation failed'}
 [Environment]::SetEnvironmentVariable('HTKK_TEST_FAKE_CREDENTIAL','test-only-sentinel')
 $job=Start-HtkkCleanProcess -Executable $fixtureExe -ProjectDirectory $directory -IsX86Reference $true
 $retained=$job.RootProcess;$handle=$retained.Handle
 if($handle -eq [IntPtr]::Zero -or $retained.Id -ne $job.ProcessId){throw 'Supplier diagnostic identity missing'}
 if(-not $job.WaitForRootExit(15000) -or $job.RootExitCode -ne 17 -or -not $retained.HasExited -or $retained.ExitCode -ne 17){throw 'Own supplier root fixture failed'}
 if([IO.File]::ReadAllText($rootMarker) -cne 'x86'){throw 'Supplier x86 environment policy lost'}
 $descendant=[Diagnostics.Process]::GetProcessById([int][IO.File]::ReadAllText($grandMarker));$null=$descendant.Handle
 if($descendant.HasExited -or $job.ActiveProcesses -lt 1){throw 'Own supplier descendant fixture not active'}
 $proof=Stop-HtkkSupplierJob -Job $job -LaunchAttempted $true;$job=$null
 if(-not $proof.cleanupVerified -or -not $proof.supplierStopped -or -not $proof.jobEmpty -or -not $descendant.HasExited){throw 'Actual supplier wrapper did not stop orphan descendant'}
 Write-Host 'Actual supplier launch/cleanup wrapper integration passed: retained identity, clean x86 environment, orphan descendant, no native output'
}finally{
 if($null -ne $job){$null=Stop-HtkkSupplierJob -Job $job -LaunchAttempted $true}
 if($null -ne $descendant){$descendant.Dispose()}
 [Environment]::SetEnvironmentVariable('HTKK_TEST_FAKE_CREDENTIAL',$previous)
 Remove-Item -LiteralPath $directory -Recurse -Force -ErrorAction SilentlyContinue
}
