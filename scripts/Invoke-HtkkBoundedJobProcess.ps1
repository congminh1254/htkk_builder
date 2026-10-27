# Result-file tools only: native stdout/stderr go to NUL, never a pipe or log.
# Compiler callers that parse stdout must retain that behavior until a separate
# bounded diagnostic-capture path exists; do not silently replace those callers.
function New-HtkkBoundedJobOwner {
 [CmdletBinding()]
 param([string]$Executable,[string]$WorkingDirectory,[string[]]$Arguments)
 if(-not $IsWindows){throw [PlatformNotSupportedException]::new('windows-job-required')}
 if(-not ('HtkkWindowsJobProcess' -as [type])){Add-Type -Path (Join-Path $PSScriptRoot 'HtkkWindowsJobProcess.cs')}
 return [HtkkWindowsJobProcess]::Launch($Executable,$WorkingDirectory,$Arguments,$true,$false)
}

function Invoke-HtkkBoundedJobProcess {
 [CmdletBinding()]
 param(
  [Parameter(Mandatory=$true)][string]$Executable,
  [Parameter(Mandatory=$true)][string]$WorkingDirectory,
  [string[]]$Arguments=@(),
  [ValidateRange(100,30000)][int]$TimeoutMilliseconds=30000
 )
 $safe=[ordered]@{status='not-started';started=$false;timedOut=$false;processStopped=$true;jobCleanupVerified=$true;exitCode=$null;timeoutMilliseconds=$TimeoutMilliseconds;childEnvironmentPolicy='os-essentials-only';lifetimeBoundary='windows-job-before-resume'}
 $owner=$null
 if(-not (Get-Variable -Name htkkHelperJobsStopped -Scope Script -ErrorAction SilentlyContinue)){$script:htkkHelperJobsStopped=$true}
 $previousHelpersStopped=$script:htkkHelperJobsStopped -is [bool] -and $script:htkkHelperJobsStopped
 # Unknown launch/cleanup exceptions cannot leave the previous safe flag intact.
 $script:htkkHelperJobsStopped=$false
 try{
  $safe.processStopped=$false;$safe.jobCleanupVerified=$false
  $owner=New-HtkkBoundedJobOwner -Executable $Executable -WorkingDirectory $WorkingDirectory -Arguments $Arguments
  $safe.started=$true
  if($owner.WaitForRootExit($TimeoutMilliseconds)){
   # Preserve the signed Int32 exit-code convention of Diagnostics.Process.
   $safe.exitCode=[BitConverter]::ToInt32([BitConverter]::GetBytes([uint32]$owner.RootExitCode),0)
   $safe.status='exited'
  }else{$safe.timedOut=$true;$safe.status='process-timeout'}
 }catch{
  $safe.status='process-tool-failure'
  $errorObject=$_.Exception
  while($null -ne $errorObject.InnerException){$errorObject=$errorObject.InnerException}
  # LaunchCore emits these categories only AFTER verifying cleanup of a failed
  # launch. Anything else remains unverified; never publish arbitrary messages.
  $verifiedLaunchFailures=@('launch-arguments-invalid','job-create-failed','job-limit-failed','environment-invalid','stdio-create-failed','handle-list-failed','process-create-failed','job-assignment-failed','process-identity-failed','process-resume-failed','boundary-tool-failure')
  if($null -eq $owner -and $errorObject -is [InvalidOperationException] -and $errorObject.Message -in $verifiedLaunchFailures){$safe.processStopped=$true;$safe.jobCleanupVerified=$true}
 }finally{
  if($null -ne $owner){
   try{
    # Dispose performs exactly one Stop(5000), verifies root + job accounting
    # zero, then closes handles. Do not call Stop first and double this deadline.
    $owner.Dispose()
    $safe.jobCleanupVerified=$owner.CleanupVerified -is [bool] -and $owner.CleanupVerified
    $safe.processStopped=$safe.jobCleanupVerified
   }catch{$safe.processStopped=$false;$safe.jobCleanupVerified=$false}
  }
  if(-not $safe.jobCleanupVerified){$safe.status='cleanup-not-verified'}
  $script:htkkHelperJobsStopped=$previousHelpersStopped -and $safe.jobCleanupVerified
 }
 return $safe
}
