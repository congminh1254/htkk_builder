# Compiler-only output capture. No raw text or private path leaves this helper.
function New-HtkkBoundedCompilerOwner {
 [CmdletBinding()]
 param([string]$Executable,[string]$WorkingDirectory,[string[]]$Arguments,[string]$StdoutPath,[string]$StderrPath)
 if(-not $IsWindows){throw [PlatformNotSupportedException]::new('windows-job-required')}
 if(-not ('HtkkWindowsJobProcess' -as [type])){Add-Type -Path (Join-Path $PSScriptRoot 'HtkkWindowsJobProcess.cs')}
 return [HtkkWindowsJobProcess]::LaunchWithOutputFiles($Executable,$WorkingDirectory,$Arguments,$true,$false,$StdoutPath,$StderrPath)
}

function Get-HtkkBoundedCompilerCodes {
 [CmdletBinding()]
 param([string[]]$Paths,[ValidateRange(1,1048576)][int]$MaximumBytes=1048576)
 $codes=[Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
 foreach($path in $Paths){
  $stream=$null
  try{
   if(([IO.File]::GetAttributes($path) -band [IO.FileAttributes]::ReparsePoint) -ne 0){throw 'compiler-output-invalid'}
   $stream=[IO.File]::Open($path,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::Read)
   if($stream.Length -gt $MaximumBytes){throw 'compiler-output-invalid'}
   $body=[byte[]]::new([int]$stream.Length);$offset=0
   while($offset -lt $body.Length){
    $read=$stream.Read($body,$offset,[Math]::Min(4096,$body.Length-$offset))
    if($read -le 0){throw 'compiler-output-invalid'}
    $offset+=$read
   }
   if($stream.ReadByte() -ne -1){throw 'compiler-output-invalid'}
   # CS#### tokens are ASCII in legacy code pages too. Recognize UTF-16 BOMs;
   # other diagnostics use UTF-8 replacement without exposing their raw text.
   $encoding=[Text.Encoding]::UTF8
   if($body.Length -ge 2 -and $body[0] -eq 255 -and $body[1] -eq 254){$encoding=[Text.Encoding]::Unicode}
   elseif($body.Length -ge 2 -and $body[0] -eq 254 -and $body[1] -eq 255){$encoding=[Text.Encoding]::BigEndianUnicode}
   foreach($match in [regex]::Matches($encoding.GetString($body),'\bCS[0-9]{4}\b')){$null=$codes.Add($match.Value)}
  }finally{if($null -ne $stream){$stream.Dispose()}}
 }
 return @($codes|Sort-Object -Unique|Select-Object -First 10)
}

function Invoke-HtkkBoundedCompiler {
 [CmdletBinding()]
 param(
  [Parameter(Mandatory=$true)][string]$Executable,
  [Parameter(Mandatory=$true)][string]$WorkingDirectory,
  [string[]]$Arguments=@(),
  [ValidateRange(100,30000)][int]$TimeoutMilliseconds=30000
 )
 $safe=[ordered]@{status='not-started';started=$false;timedOut=$false;processStopped=$true;jobCleanupVerified=$true;exitCode=$null;timeoutMilliseconds=$TimeoutMilliseconds;compilerErrorCodes=@();diagnosticsVerified=$false;childEnvironmentPolicy='os-essentials-only';lifetimeBoundary='windows-job-before-resume'}
 $owner=$null;$stdoutPath=$null;$stderrPath=$null
 if(-not(Get-Variable -Name htkkHelperJobsStopped -Scope Script -ErrorAction SilentlyContinue)){$script:htkkHelperJobsStopped=$true}
 $previousHelpersStopped=$script:htkkHelperJobsStopped -is [bool] -and $script:htkkHelperJobsStopped
 $script:htkkHelperJobsStopped=$false
 try{
  $suffix=[guid]::NewGuid().ToString('N')
  $stdoutPath=Join-Path $WorkingDirectory ('compiler-'+$suffix+'.stdout')
  $stderrPath=Join-Path $WorkingDirectory ('compiler-'+$suffix+'.stderr')
  $safe.processStopped=$false;$safe.jobCleanupVerified=$false
  $owner=New-HtkkBoundedCompilerOwner -Executable $Executable -WorkingDirectory $WorkingDirectory -Arguments $Arguments -StdoutPath $stdoutPath -StderrPath $stderrPath
  $safe.started=$true
  if($owner.WaitForRootExit($TimeoutMilliseconds)){
   $safe.exitCode=[BitConverter]::ToInt32([BitConverter]::GetBytes([uint32]$owner.RootExitCode),0)
   $safe.status='exited'
  }else{$safe.timedOut=$true;$safe.status='process-timeout'}
 }catch{
  $safe.status='process-tool-failure'
  $errorObject=$_.Exception
  while($null -ne $errorObject.InnerException){$errorObject=$errorObject.InnerException}
  $verifiedLaunchFailures=@('launch-arguments-invalid','job-create-failed','job-limit-failed','environment-invalid','stdio-create-failed','handle-list-failed','process-create-failed','job-assignment-failed','process-identity-failed','process-resume-failed','output-path-invalid','output-create-failed','boundary-tool-failure')
  if($null -eq $owner -and $errorObject -is [InvalidOperationException] -and $errorObject.Message -in $verifiedLaunchFailures){$safe.processStopped=$true;$safe.jobCleanupVerified=$true}
 }finally{
  if($null -ne $owner){
   try{
    # Exactly one native cleanup deadline, then handles close before file reads.
    $owner.Dispose()
    $safe.jobCleanupVerified=$owner.CleanupVerified -is [bool] -and $owner.CleanupVerified
    $safe.processStopped=$safe.jobCleanupVerified
   }catch{$safe.processStopped=$false;$safe.jobCleanupVerified=$false}
  }
  if(-not $safe.jobCleanupVerified){$safe.status='cleanup-not-verified'}
  $script:htkkHelperJobsStopped=$previousHelpersStopped -and $safe.jobCleanupVerified
 }
 # A timed-out or unverified job must never be mistaken for complete diagnostics.
 try{
  if($safe.status -eq 'exited' -and $safe.jobCleanupVerified){
   $safe.compilerErrorCodes=@(Get-HtkkBoundedCompilerCodes -Paths @($stdoutPath,$stderrPath))
   $safe.diagnosticsVerified=$true
  }
 }catch{$safe.status='compiler-output-invalid';$safe.compilerErrorCodes=@()}
 finally{
  # Do not touch potentially active output files after failed cleanup. The caller
  # owns the private working directory; no raw data/path enters this result.
  if($safe.jobCleanupVerified){
   foreach($path in @($stdoutPath,$stderrPath)){if($null -ne $path){Remove-Item -LiteralPath $path -Force -ErrorAction SilentlyContinue}}
  }
 }
 return $safe
}
