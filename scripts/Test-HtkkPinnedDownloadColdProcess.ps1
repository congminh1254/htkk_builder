# Own deterministic subprocess only: no requests, source execution or credentials.
[CmdletBinding()]
param([switch]$Child)
$ErrorActionPreference='Stop'
if($Child){
 # Core-only startup reproduces the production failure before Utility autoloads.
 $PSModuleAutoloadingPreference='None'
 $phase='initial-type'
 trap {[Console]::Error.WriteLine('COLD_DOWNLOAD_CLASSIFICATION_FAILED_'+$phase);exit 1}
 if($null -ne (Get-Module -Name Microsoft.PowerShell.Utility)){throw 'Utility module unexpectedly imported'}
 $initialHttpType='Microsoft.PowerShell.Commands.HttpResponseException' -as [type]
 $typeState=if($null -eq $initialHttpType){'ABSENT'}else{'PRELOADED'}
 $phase='load-production'
 . ([IO.Path]::Combine($PSScriptRoot,'Invoke-HtkkPinnedDownload.ps1'))
 $cases=@(
  @([TimeoutException]::new('private-fixture-message'),'timeout',$true),
  @([Security.Authentication.AuthenticationException]::new('private-fixture-message'),'tls',$false),
  @([Exception]::new('private-fixture-message'),'tool',$false),
  @([Net.Http.HttpRequestException]::new('private-fixture-message',$null,[Net.HttpStatusCode]::ServiceUnavailable),'http',$true)
 )
 $phase='core-classification'
 foreach($case in $cases){
  $result=Get-HtkkDownloadFailure -Exception $case[0]
  $expectedStatus=if($case[1] -ceq 'http'){503}else{$null}
  if($result.Count -ne 3 -or $result.category -cne $case[1] -or $result.retryable -ne $case[2] -or $result.httpStatus -ne $expectedStatus){throw 'Cold classification mismatch'}
 }
 $phase='core-type-still-absent'
 if($null -ne (Get-Module -Name Microsoft.PowerShell.Utility)){throw 'Classification imported Utility'}
 if($null -eq $initialHttpType -and $null -ne ('Microsoft.PowerShell.Commands.HttpResponseException' -as [type])){throw 'Classification loaded optional type'}
 # Load only the trusted PowerShell-distributed manifest, then test the actual
 # optional exception type as well as the generic .NET HTTP exception above.
 $phase='trusted-utility-load'
 Import-Module ([IO.Path]::Combine($PSHOME,'Modules','Microsoft.PowerShell.Utility','Microsoft.PowerShell.Utility.psd1')) -ErrorAction Stop
 $loadedHttpType='Microsoft.PowerShell.Commands.HttpResponseException' -as [type]
 if($null -eq $loadedHttpType){throw 'Trusted HTTP type unavailable'}
 $phase='loaded-http-classification'
 foreach($status in @(403,503)){
  $response=[Net.Http.HttpResponseMessage]::new([Net.HttpStatusCode]$status)
  try{
   $errorItem=[Activator]::CreateInstance($loadedHttpType,[object[]]@('private-fixture-message',$response))
   $result=Get-HtkkDownloadFailure -Exception $errorItem
   if($result.Count -ne 3 -or $result.category -cne 'http' -or $result.httpStatus -ne $status -or $result.retryable -ne ($status -eq 503)){throw 'Loaded HTTP type classification mismatch'}
  }finally{$response.Dispose()}
 }
 [Console]::Out.WriteLine('COLD_DOWNLOAD_CLASSIFICATION_OK_6_'+$typeState)
 exit 0
}
$start=[Diagnostics.ProcessStartInfo]::new()
$start.FileName=[Diagnostics.Process]::GetCurrentProcess().MainModule.FileName
$start.UseShellExecute=$false;$start.CreateNoWindow=$true
$start.RedirectStandardOutput=$true;$start.RedirectStandardError=$true
foreach($arg in @('-NoLogo','-NoProfile','-NonInteractive','-File',$PSCommandPath,'-Child')){$start.ArgumentList.Add($arg)}
# Whitelist OS/runtime paths only. Do not pass any Actions/relay/proxy credentials.
$start.Environment.Clear()
foreach($name in @('SystemRoot','WINDIR','SystemDrive','ComSpec','PATH','PATHEXT','TEMP','TMP','TMPDIR','HOME','USERPROFILE','LOCALAPPDATA','APPDATA','PROGRAMFILES','PROGRAMFILES(X86)','PROGRAMDATA','ALLUSERSPROFILE','LANG','LC_ALL')){
 $value=[Environment]::GetEnvironmentVariable($name)
 if($null -ne $value){$start.Environment[$name]=$value}
}
$start.Environment['POWERSHELL_TELEMETRY_OPTOUT']='1'
$start.Environment['POWERSHELL_UPDATECHECK']='Off'
$process=[Diagnostics.Process]::new();$process.StartInfo=$start;$started=$false
try{
 $started=$process.Start()
 if(-not $started){throw 'Cold classification subprocess not started'}
 if(-not $process.WaitForExit(20000)){$process.Kill($true);$null=$process.WaitForExit(5000);throw 'Cold classification subprocess timed out'}
 # The fixed child has no descendants and writes only one fixed marker. Read
 # after its observed exit; any unexpected blocked output hits the deadline.
 $stdout=$process.StandardOutput.ReadToEnd();$stderr=$process.StandardError.ReadToEnd()
 if($process.ExitCode -ne 0 -or $stdout.Trim() -cnotin @('COLD_DOWNLOAD_CLASSIFICATION_OK_6_ABSENT','COLD_DOWNLOAD_CLASSIFICATION_OK_6_PRELOADED') -or $stderr.Length -ne 0){throw 'Cold classification subprocess failed'}
 $typeState=if($stdout.Trim().EndsWith('_ABSENT')){'absent'}else{'preloaded'}
 Write-Host ('Pinned download cold/loaded Utility classification checks passed: 6; optional type initially '+$typeState)
}finally{
 try{
  if($started -and -not $process.HasExited){$process.Kill($true);if(-not $process.WaitForExit(5000)){throw 'Cold classification subprocess cleanup failed'}}
 }finally{$process.Dispose()}
}
