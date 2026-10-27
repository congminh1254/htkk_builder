# A native-tool boundary: no credentials or native stdout/stderr escape this function.
function Invoke-HtkkBoundedNativeProcess {
 [CmdletBinding()]
 param(
  [Parameter(Mandatory=$true)][string]$Executable,
  [Parameter(Mandatory=$true)][string]$WorkingDirectory,
  [string[]]$Arguments=@(),
  [ValidateRange(100,300000)][int]$TimeoutMilliseconds=180000
 )
 $safe=[ordered]@{status='not-started';started=$false;timedOut=$false;processStopped=$true;exitCode=$null;timeoutMilliseconds=$TimeoutMilliseconds;childEnvironmentPolicy='os-essentials-only'}
 $nativeProcess=$null
 try {
  $info=[Diagnostics.ProcessStartInfo]::new()
  $info.FileName=$Executable;$info.WorkingDirectory=$WorkingDirectory;$info.UseShellExecute=$false;$info.CreateNoWindow=$true
  $info.RedirectStandardOutput=$true;$info.RedirectStandardError=$true;$info.Environment.Clear()
  foreach($key in @('SystemRoot','WINDIR','SystemDrive','TEMP','TMP','PATH','APPDATA','LOCALAPPDATA','USERPROFILE','ProgramData','COMSPEC','PROCESSOR_ARCHITECTURE','PROCESSOR_ARCHITEW6432','NUMBER_OF_PROCESSORS')){
   $value=[Environment]::GetEnvironmentVariable($key);if($null -ne $value){$info.Environment[$key]=$value}
  }
  foreach($argument in $Arguments){$info.ArgumentList.Add($argument)}
  $nativeProcess=[Diagnostics.Process]::Start($info)
  $safe.started=$true;$safe.processStopped=$false;$null=$nativeProcess.Handle
  # Drain without retaining arbitrary native output in memory or exposing it.
  $nativeStdout=$nativeProcess.StandardOutput.BaseStream.CopyToAsync([IO.Stream]::Null)
  $nativeStderr=$nativeProcess.StandardError.BaseStream.CopyToAsync([IO.Stream]::Null)
  if($nativeProcess.WaitForExit($TimeoutMilliseconds)){$safe.exitCode=$nativeProcess.ExitCode;$safe.status='exited'}
  else{$safe.timedOut=$true;$safe.status='process-timeout'}
 }catch{$safe.status='process-tool-failure'}
 finally{
  if($null -ne $nativeProcess){
   try{
    if(-not $nativeProcess.HasExited){$nativeProcess.Kill($true);$null=$nativeProcess.WaitForExit(5000)}
    $safe.processStopped=$nativeProcess.HasExited
   }catch{$safe.processStopped=$false}
   if(-not $safe.processStopped){$safe.status='cleanup-not-verified'}
   try{$nativeProcess.Dispose()}catch{if(-not $safe.processStopped){$safe.status='cleanup-not-verified'}}
  }
 }
 return $safe
}
