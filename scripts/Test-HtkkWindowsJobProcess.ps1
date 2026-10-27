# Standalone boundary validation; does not install, load or run HTKK.
$ErrorActionPreference='Stop'
$shim=@'
// Test-only typed invocation: PowerShell never constructs reflection object[].
public static class HtkkWindowsJobTestShim {
 [System.Runtime.InteropServices.StructLayout(System.Runtime.InteropServices.LayoutKind.Sequential)]
 private struct SECURITY_ATTRIBUTES { public int length;public System.IntPtr descriptor;[System.Runtime.InteropServices.MarshalAs(System.Runtime.InteropServices.UnmanagedType.Bool)]public bool inherit; }
 [System.Runtime.InteropServices.DllImport("kernel32.dll",CharSet=System.Runtime.InteropServices.CharSet.Unicode,SetLastError=true)]
 private static extern System.IntPtr CreateFile(string name,uint access,uint share,ref SECURITY_ATTRIBUTES attributes,uint creation,uint flags,System.IntPtr template);
 [System.Runtime.InteropServices.DllImport("kernel32.dll")] private static extern bool CloseHandle(System.IntPtr handle);
 public static System.IntPtr OpenInheritableSentinel(string path){
  SECURITY_ATTRIBUTES attributes=new SECURITY_ATTRIBUTES();attributes.length=System.Runtime.InteropServices.Marshal.SizeOf(typeof(SECURITY_ATTRIBUTES));attributes.inherit=true;
  System.IntPtr handle=CreateFile(path,0x80000000,3,ref attributes,3,0x80,System.IntPtr.Zero);
  if(handle==new System.IntPtr(-1))throw new System.InvalidOperationException("test-sentinel-open-failed");return handle;
 }
 public static void CloseSentinel(System.IntPtr handle){if(handle!=System.IntPtr.Zero)CloseHandle(handle);}
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
    string[] categories = new string[] { "job-assignment-failed", "job-cleanup-not-verified", "boundary-tool-failure", "process-create-failed", "job-create-failed", "job-limit-failed", "stdio-create-failed", "output-path-invalid", "output-create-failed", "handle-list-failed", "launch-arguments-invalid", "environment-invalid", "process-identity-failed", "process-resume-failed" };
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
function Get-FailureCategory($errorRecord){
 $errorObject=$errorRecord.Exception
 while($null -ne $errorObject.InnerException){$errorObject=$errorObject.InnerException}
 return $errorObject.Message
}
$preflight=Join-Path $env:RUNNER_TEMP ('htkk-output-preflight-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $preflight|Out-Null
$freshOutput=Join-Path $preflight 'stdout.bin';$freshError=Join-Path $preflight 'stderr.bin';$existingOutput=Join-Path $preflight 'existing.bin'
[IO.File]::WriteAllText($existingOutput,'unchanged-test-sentinel')
$pathCases=0
try{
 foreach($pair in @(
  @('relative.bin',$freshError),
  @((Join-Path (Split-Path $preflight) 'outside.bin'),$freshError),
  @($freshOutput,$freshOutput),
  @((Join-Path $preflight 'file:stream'),$freshError),
  @((Join-Path $preflight 'NUL'),$freshError),
  @($existingOutput,$freshError)
 )){
  $refused=$false;$unexpected=$null
  try{$unexpected=[HtkkWindowsJobProcess]::LaunchWithOutputFiles([Diagnostics.Process]::GetCurrentProcess().MainModule.FileName,$preflight,@(),$true,$false,$pair[0],$pair[1])}catch{if((Get-FailureCategory $_) -ceq 'output-path-invalid'){$refused=$true}else{throw 'Unexpected private output path refusal'}}
  if($null -ne $unexpected){$unexpected.Dispose()}
  if(-not $refused -or (Test-Path -LiteralPath $freshOutput) -or (Test-Path -LiteralPath $freshError)){throw 'Invalid output path launched a child or created output'}
  $pathCases++
 }
 if([IO.File]::ReadAllText($existingOutput) -cne 'unchanged-test-sentinel'){throw 'Output preflight overwrote existing file'}
}finally{Remove-Item -LiteralPath $preflight -Recurse -Force -ErrorAction SilentlyContinue}
if(-not $IsWindows){Write-Host "Windows Job boundary C# compiled; 4 quoting, typed invocation and $pathCases output path preflight checks passed; Win32 integration NOT RUN on this platform";return}

$directory=Join-Path $env:RUNNER_TEMP ('htkk-job-boundary-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $directory|Out-Null
$child=Join-Path $directory 'child fixture.ps1'
$marker=Join-Path $directory 'root marker.json'
$grandMarker=Join-Path $directory 'grandchild marker.txt'
$hostExecutable=[Diagnostics.Process]::GetCurrentProcess().MainModule.FileName
$previous=[Environment]::GetEnvironmentVariable('HTKK_TEST_FAKE_CREDENTIAL')
$owner=$null;$descendant=$null;$sentinelHandle=[IntPtr]::Zero
function Wait-Marker([string]$Path){
 $clock=[Diagnostics.Stopwatch]::StartNew()
 while(-not(Test-Path -LiteralPath $Path)){if($clock.ElapsedMilliseconds -gt 10000){throw 'Native test fixture did not become ready'};Start-Sleep -Milliseconds 20}
}
try{
 [Environment]::SetEnvironmentVariable('HTKK_TEST_FAKE_CREDENTIAL','test-only-sentinel')
 @'
param([string]$Mode,[string]$Marker,[string]$GrandMarker,[string]$HostExecutable,[string]$Payload,[long]$ForbiddenHandle=0)
if([Environment]::GetEnvironmentVariable('HTKK_TEST_FAKE_CREDENTIAL')){exit 91}
if($ForbiddenHandle -ne 0){
 Add-Type -TypeDefinition @"
using System;using System.IO;using System.Text;using System.Runtime.InteropServices;
public static class ForbiddenHandleProbe {
 [DllImport("kernel32.dll",CharSet=CharSet.Unicode,SetLastError=true)]private static extern uint GetFinalPathNameByHandle(IntPtr handle,StringBuilder path,uint size,uint flags);
 public static bool Inherited(long handle,string expected){StringBuilder path=new StringBuilder(2048);uint length=GetFinalPathNameByHandle(new IntPtr(handle),path,(uint)path.Capacity,0);if(length==0||length>=path.Capacity)return false;string observed=path.ToString();if(observed.StartsWith(@"\\?\",StringComparison.Ordinal))observed=observed.Substring(4);return String.Equals(Path.GetFullPath(observed),Path.GetFullPath(expected),StringComparison.OrdinalIgnoreCase);}
}
"@
 if([ForbiddenHandleProbe]::Inherited($ForbiddenHandle,(Join-Path (Split-Path $PSCommandPath) 'sentinel.txt'))){exit 93}
}
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
 $retainedRoot=$owner.RootProcess;$retainedHandle=$retainedRoot.Handle
 if($retainedHandle -eq [IntPtr]::Zero -or $retainedRoot.Id -ne $owner.ProcessId){throw 'Pre-resume diagnostic identity missing'}
 if(-not $owner.WaitForRootExit(15000) -or $owner.RootExitCode -ne 17){throw 'Normal job child exit failed'}
 if(-not [Object]::ReferenceEquals($retainedRoot,$owner.RootProcess) -or $retainedRoot.Handle -ne $retainedHandle -or -not $retainedRoot.HasExited -or $retainedRoot.ExitCode -ne 17){throw 'Retained diagnostic identity changed after fast root exit'}
 $result=Get-Content -LiteralPath $marker -Raw|ConvertFrom-Json
 if($result.payload -cne $payload){throw 'Actual Windows argument roundtrip failed'}
 if(-not $owner.Stop(5000) -or -not $owner.CleanupVerified -or $owner.ActiveProcesses -ne 0){throw 'Normal job cleanup failed'}
 $owner.Dispose();$owner=$null
 Remove-Item -LiteralPath $marker

 # Capture only the explicit private output files, never arbitrary inherited handles.
 $stdout=Join-Path $directory 'capture-stdout.bin';$stderr=Join-Path $directory 'capture-stderr.bin'
 $sentinelPath=Join-Path $directory 'sentinel.txt'
 [IO.File]::WriteAllText($sentinelPath,'test-only-sentinel-not-a-real-credential')
 $sentinelHandle=[HtkkWindowsJobTestShim]::OpenInheritableSentinel($sentinelPath)
 $captureArguments=[string[]](@($arguments)+@([string]$sentinelHandle.ToInt64()))
 $owner=[HtkkWindowsJobProcess]::LaunchWithOutputFiles($hostExecutable,$directory,$captureArguments,$true,$false,$stdout,$stderr)
 if(-not $owner.WaitForRootExit(15000) -or $owner.RootExitCode -ne 17){throw 'Private output fixture or handle isolation failed'}
 $owner.Dispose()
 if(-not $owner.CleanupVerified){throw 'Private output job cleanup unverified'}
 $owner=$null
 $out=[IO.File]::ReadAllText($stdout);$err=[IO.File]::ReadAllText($stderr)
 if(-not $out.Contains('stdout-must-be-discarded') -or $out.Contains('stderr-must-be-discarded') -or -not $err.Contains('stderr-must-be-discarded') -or $err.Contains('stdout-must-be-discarded')){throw 'Private stdout/stderr capture changed bytes or crossed streams'}
 [HtkkWindowsJobTestShim]::CloseSentinel($sentinelHandle);$sentinelHandle=[IntPtr]::Zero
 Remove-Item -LiteralPath $marker
 # Existing files are refused without overwrite and before any child instruction.
 $before=[IO.File]::ReadAllBytes($stdout)
 $refused=$false
 try{$unexpected=[HtkkWindowsJobProcess]::LaunchWithOutputFiles($hostExecutable,$directory,$arguments,$true,$false,$stdout,(Join-Path $directory 'fresh-stderr.bin'))}catch{if((Get-FailureCategory $_) -ceq 'output-path-invalid'){$refused=$true}else{throw 'Unexpected output file refusal category'}}
 if(-not $refused -and $null -ne $unexpected){$unexpected.Dispose()}
 if(-not $refused -or (Test-Path -LiteralPath $marker) -or [Convert]::ToBase64String([IO.File]::ReadAllBytes($stdout)) -cne [Convert]::ToBase64String($before)){throw 'Existing private output file overwritten or child launched'}
 # A junction lexically inside cwd must not redirect diagnostics elsewhere.
 $target=Join-Path $directory 'junction-target';$junction=Join-Path $directory 'junction-output'
 New-Item -ItemType Directory -Path $target|Out-Null
 New-Item -ItemType Junction -Path $junction -Target $target|Out-Null
 $refused=$false;$unexpected=$null
 try{$unexpected=[HtkkWindowsJobProcess]::LaunchWithOutputFiles($hostExecutable,$directory,$arguments,$true,$false,(Join-Path $junction 'stdout.bin'),(Join-Path $directory 'fresh-stderr.bin'))}catch{if((Get-FailureCategory $_) -ceq 'output-path-invalid'){$refused=$true}else{throw 'Unexpected reparse output refusal category'}}
 if(-not $refused -and $null -ne $unexpected){$unexpected.Dispose()}
 if(-not $refused -or (Test-Path -LiteralPath $marker) -or (Test-Path -LiteralPath (Join-Path $target 'stdout.bin'))){throw 'Reparse output parent followed or child launched'}
 Remove-Item -LiteralPath $junction -Force

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
 Write-Host 'Windows Job integration passed: normal exit/arguments/environment, private output/handle isolation/no overwrite, orphaned grandchild, timeout, pre-resume assignment failure, missing image'
}finally{
 if($null -ne $owner){$null=$owner.Stop(5000);$owner.Dispose()}
 if($null -ne $descendant){$descendant.Dispose()}
 [HtkkWindowsJobTestShim]::CloseSentinel($sentinelHandle)
 [Environment]::SetEnvironmentVariable('HTKK_TEST_FAKE_CREDENTIAL',$previous)
 Remove-Item -LiteralPath $directory -Recurse -Force -ErrorAction SilentlyContinue
}
