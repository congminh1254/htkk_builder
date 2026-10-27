# Standalone boundary validation; does not install, load or run HTKK.
$ErrorActionPreference='Stop'
$shim=@'
// Test-only typed invocation: PowerShell never constructs reflection object[].
public static class HtkkWindowsJobTestShim {
 public static string AssignmentRefusal(string executable, string directory, string[] arguments) {
  HtkkWindowsJobProcess unexpected = null;
  try {
   System.Reflection.MethodInfo method = typeof(HtkkWindowsJobProcess).GetMethod("LaunchCore", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Static);
   if (method == null) return "test-hook-missing";
   unexpected = (HtkkWindowsJobProcess)method.Invoke(null, new object[] { executable, directory, arguments, true, false, new System.IntPtr(-1) });
   return unexpected.Stop(5000) ? "unexpected-launch-success" : "job-cleanup-not-verified";
  } catch (System.Exception error) {
   while (error.InnerException != null) error = error.InnerException;
   if (error is System.InvalidOperationException) {
    string[] categories = new string[] { "job-assignment-failed", "job-cleanup-not-verified", "boundary-tool-failure", "process-create-failed", "job-create-failed", "job-limit-failed", "stdio-create-failed", "handle-list-failed", "launch-arguments-invalid", "environment-invalid", "process-resume-failed" };
    if (System.Array.IndexOf(categories, error.Message) >= 0) return error.Message;
    return "unexpected-invalid-operation";
   }
   if (error is System.ArgumentException) return "unexpected-argument-exception";
   if (error is System.Reflection.TargetParameterCountException) return "unexpected-parameter-count";
   if (error is System.Reflection.TargetException) return "unexpected-reflection-target";
   if (error is System.MethodAccessException) return "unexpected-method-access";
   if (error is System.Reflection.AmbiguousMatchException) return "unexpected-ambiguous-method";
   return "unexpected-other-exception-type";
  } finally {
   if (unexpected != null) unexpected.Dispose();
  }
 }
}
'@
Add-Type -TypeDefinition ([IO.File]::ReadAllText((Join-Path $PSScriptRoot 'HtkkWindowsJobProcess.cs'))+"`n"+$shim)
$quoteCases=@(
 @('', '""'),
 @('alpha beta','"alpha beta"'),
 @('a"b','"a\"b"'),
 @('C:\space path\','"C:\space path\\"')
)
foreach($case in $quoteCases){if([HtkkWindowsJobProcess]::QuoteArgument($case[0]) -cne $case[1]){throw 'Windows argument encoding failed'}}
# This reaches the actual production preflight through typed reflection on ANY
# platform, proving argument binding without starting a native process.
if([HtkkWindowsJobTestShim]::AssignmentRefusal('relative.exe','relative',@('quoted "argument"')) -cne 'launch-arguments-invalid'){throw 'Typed test invocation preflight failed'}
if(-not $IsWindows){Write-Host 'Windows Job boundary C# compiled; 4 quoting checks and typed invocation preflight passed; Win32 integration NOT RUN on this platform';return}

$directory=Join-Path $env:RUNNER_TEMP ('htkk-job-boundary-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $directory|Out-Null
$child=Join-Path $directory 'child fixture.ps1'
$marker=Join-Path $directory 'root marker.json'
$grandMarker=Join-Path $directory 'grandchild marker.txt'
$hostExecutable=[Diagnostics.Process]::GetCurrentProcess().MainModule.FileName
$previous=[Environment]::GetEnvironmentVariable('HTKK_TEST_FAKE_CREDENTIAL')
$owner=$null;$descendant=$null
function Wait-Marker([string]$Path){
 $clock=[Diagnostics.Stopwatch]::StartNew()
 while(-not(Test-Path -LiteralPath $Path)){if($clock.ElapsedMilliseconds -gt 10000){throw 'Native test fixture did not become ready'};Start-Sleep -Milliseconds 20}
}
function Get-FailureCategory($errorRecord){
 $errorObject=$errorRecord.Exception
 while($null -ne $errorObject.InnerException){$errorObject=$errorObject.InnerException}
 return $errorObject.Message
}
try{
 [Environment]::SetEnvironmentVariable('HTKK_TEST_FAKE_CREDENTIAL','test-only-sentinel')
 @'
param([string]$Mode,[string]$Marker,[string]$GrandMarker,[string]$HostExecutable,[string]$Payload)
if([Environment]::GetEnvironmentVariable('HTKK_TEST_FAKE_CREDENTIAL')){exit 91}
[Console]::Out.WriteLine('stdout-must-be-discarded')
[Console]::Error.WriteLine('stderr-must-be-discarded')
if($Mode -eq 'grandchild'){
 [IO.File]::WriteAllText($Marker,[string]$PID)
 Start-Sleep -Seconds 60
 exit 0
}
[IO.File]::WriteAllText($Marker,(@{pid=$PID;payload=$Payload}|ConvertTo-Json -Compress))
if($Mode -eq 'spawn'){
 $info=[Diagnostics.ProcessStartInfo]::new();$info.FileName=$HostExecutable;$info.UseShellExecute=$false;$info.CreateNoWindow=$true
 foreach($argument in @('-NoLogo','-NoProfile','-NonInteractive','-File',$PSCommandPath,'grandchild',$GrandMarker,'unused','unused','unused')){$info.ArgumentList.Add($argument)}
 $grandchild=[Diagnostics.Process]::Start($info)
 $clock=[Diagnostics.Stopwatch]::StartNew()
 while(-not(Test-Path -LiteralPath $GrandMarker)){if($clock.ElapsedMilliseconds -gt 10000){exit 92};Start-Sleep -Milliseconds 20}
 $grandchild.Dispose()
 exit 17
}
if($Mode -eq 'hang'){Start-Sleep -Seconds 60}
exit 17
'@|Set-Content -LiteralPath $child -Encoding utf8BOM
 $payload='a "quoted" value with trailing slash\'
 $arguments=@('-NoLogo','-NoProfile','-NonInteractive','-File',$child,'normal',$marker,$grandMarker,$hostExecutable,$payload)
 $owner=[HtkkWindowsJobProcess]::Launch($hostExecutable,$directory,$arguments,$true,$false)
 if(-not $owner.WaitForRootExit(15000) -or $owner.RootExitCode -ne 17){throw 'Normal job child exit failed'}
 $result=Get-Content -LiteralPath $marker -Raw|ConvertFrom-Json
 if($result.payload -cne $payload){throw 'Actual Windows argument roundtrip failed'}
 if(-not $owner.Stop(5000) -or -not $owner.CleanupVerified -or $owner.ActiveProcesses -ne 0){throw 'Normal job cleanup failed'}
 $owner.Dispose();$owner=$null
 Remove-Item -LiteralPath $marker

 # Parent exits first; its live grandchild must remain tracked by the job.
 $arguments[5]='spawn'
 $owner=[HtkkWindowsJobProcess]::Launch($hostExecutable,$directory,$arguments,$true,$false)
 if(-not $owner.WaitForRootExit(15000) -or $owner.RootExitCode -ne 17){throw 'Early-exit parent fixture failed'}
 Wait-Marker $grandMarker
 $descendant=[Diagnostics.Process]::GetProcessById([int][IO.File]::ReadAllText($grandMarker));$null=$descendant.Handle
 if($descendant.HasExited -or $owner.ActiveProcesses -lt 1){throw 'Orphaned descendant escaped accounting'}
 if(-not $owner.Stop(5000) -or $owner.ActiveProcesses -ne 0 -or -not $descendant.HasExited){throw 'Orphaned descendant was not terminated'}
 $descendant.Dispose();$descendant=$null;$owner.Dispose();$owner=$null
 Remove-Item -LiteralPath $marker,$grandMarker

 $arguments[5]='hang'
 $owner=[HtkkWindowsJobProcess]::Launch($hostExecutable,$directory,$arguments,$true,$false)
 Wait-Marker $marker
 if($owner.WaitForRootExit(100)){throw 'Hanging root unexpectedly exited'}
 if(-not $owner.Stop(5000) -or -not $owner.WaitForRootExit(0) -or $owner.ActiveProcesses -ne 0){throw 'Job timeout cleanup failed'}
 $owner.Dispose();$owner=$null
 Remove-Item -LiteralPath $marker

 # Force an actual native assignment error while the child is suspended.
 $arguments[5]='normal'
 $refusal=[HtkkWindowsJobTestShim]::AssignmentRefusal($hostExecutable,$directory,[string[]]$arguments)
 if($refusal -cne 'job-assignment-failed'){Write-Host ('Assignment failure diagnostic category: '+$refusal);throw 'Assignment failure cleanup was not verified'}
 if(Test-Path -LiteralPath $marker){throw 'Child executed before successful job assignment'}
 $rejected=$false
 try{$unexpected=[HtkkWindowsJobProcess]::Launch((Join-Path $directory 'missing.exe'),$directory,@(),$true,$false)}catch{
  if((Get-FailureCategory $_) -ceq 'process-create-failed'){$rejected=$true}else{throw 'Unexpected native launch failure category'}
 }
 if(-not $rejected){throw 'Missing native image accepted'}
 Write-Host 'Windows Job integration passed: normal exit/arguments/environment, orphaned grandchild, timeout, pre-resume assignment failure, missing image'
}finally{
 if($null -ne $owner){$null=$owner.Stop(5000);$owner.Dispose()}
 if($null -ne $descendant){$descendant.Dispose()}
 [Environment]::SetEnvironmentVariable('HTKK_TEST_FAKE_CREDENTIAL',$previous)
 Remove-Item -LiteralPath $directory -Recurse -Force -ErrorAction SilentlyContinue
}
