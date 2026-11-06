# Read-only data export of the reviewed 5.8.1 payload for PRIVATE source analysis.
# Precondition: Test-HtkkSourceCandidateTrust.ps1 has returned baseline-verified for
# the same candidate directory. Never install, run setup.exe, msiexec or any
# vendor code; the MSI is opened read-only only to read layout tables.
# Outputs (inside -OutputDirectory, which must not exist):
#   layout.json  - File/Component/Directory/MsiFileHash rows, member order = payload index
#   payload/NNNNN.bin - CAB members named by numeric index, never by MSI identifiers
# The public console receives only fixed status text, allowlisted codes and counts:
# failureCode/stage/controllerStage come from fixed enums, errorType from a .NET
# type allowlist and errorHResult is a numeric HRESULT. Never names, paths or messages.
[CmdletBinding()]
param(
 [Parameter(Mandatory=$true)][string]$CandidateDirectory,
 [Parameter(Mandatory=$true)][string]$OutputDirectory,
 [Parameter(Mandatory=$true)][string]$ResultPath,
 [switch]$Worker,
 [string]$WorkerDirectory
)
$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
Import-Module ([IO.Path]::Combine($PSHOME,'Modules','Microsoft.PowerShell.Utility','Microsoft.PowerShell.Utility.psd1')) -ErrorAction Stop
Import-Module ([IO.Path]::Combine($PSHOME,'Modules','Microsoft.PowerShell.Management','Microsoft.PowerShell.Management.psd1')) -ErrorAction Stop
Import-Module ([IO.Path]::Combine($PSHOME,'Modules','Microsoft.PowerShell.Security','Microsoft.PowerShell.Security.psd1')) -ErrorAction Stop
$PSModuleAutoloadingPreference='None'
# Minimal fallback writer for bootstrap failures (before reviewed helpers exist).
function Write-HtkkBootstrapFailure([string]$Path,[string]$Code,[string]$Mode){
 $json='{"format":"htkk-source-payload-export-v1","version":"5.8.1","status":"blocked","failureCode":"'+$Code+'","stage":"BOOTSTRAP","controllerStage":"'+$Mode+'","errorType":"other","errorHResult":null,"ready":false,"automaticActivation":false,"vendorCodeExecuted":false,"installerExecuted":false,"msiCustomActionsExecuted":false,"workerStopped":true,"jobCleanupVerified":true,"workerTimedOut":false,"workerExitCode":null}'
 try{if(-not [IO.File]::Exists($Path)){[IO.File]::WriteAllText($Path,$json+"`n",[Text.UTF8Encoding]::new($false))}}catch{}
}
# Reuse the reviewed production helpers of the trust verifier instead of copies.
try{
 $tokens=$null;$errors=$null
 $trustAst=[Management.Automation.Language.Parser]::ParseFile(([IO.Path]::Combine($PSScriptRoot,'Test-HtkkSourceCandidateTrust.ps1')),[ref]$tokens,[ref]$errors)
 if($errors.Count){throw 'SOURCE_TRUST_PARSE_FAILED'}
 foreach($helper in @('Get-PrivateFileHash','Assert-PlainPath','Write-NewPrivateJson','Invoke-ReadOnlyTool','Assert-RunnerTool','Release-ComObject','Read-MsiRows')){
  $fn=$trustAst.Find({param($n) $n -is [Management.Automation.Language.FunctionDefinitionAst] -and $n.Name -ceq $helper},$true)
  if($null -eq $fn){throw 'SOURCE_HELPER_MISSING'}
  . ([scriptblock]::Create($fn.Extent.Text))
 }
}catch{
 Write-HtkkBootstrapFailure $ResultPath 'HELPER_LOAD' $(if($Worker){'WORKER'}else{'CONTROLLER'})
 [Console]::WriteLine('Source payload export: blocked; code=HELPER_LOAD; stage=BOOTSTRAP; ready=false')
 exit 3
}
$script:pins=[ordered]@{
 officialArchive='5d52c06595e933a3b246480785d5d4010fad669baed6fb38311f8a09b20e1e95'
 msi='7c1da251ee2acd126a2363e4457502b8ad6fc0792d78dc0a92b153701dc29080'
 setup='19394e89351dc213306864168e16808d48401597f56d5fe4c977f9a5833d2936'
 cab='00669905937fb29e10cb53209ece5e8a9f8097970e4cb40bb28f89baa9fc3744'
}
$script:known=@('WINDOWS_REQUIRED','INPUT_MISSING','PATH_POLICY','ARCHIVE_PIN_MISMATCH','RUNNER_TOOL_TRUST','TOOL_TIMEOUT','TOOL_REJECTED','DISTRIBUTION_HASH','MSI_MEDIA','MSI_FILE_COUNTS','MSI_FILE_IDENTITIES','MSI_HASH_IDENTITIES','PAYLOAD_SIZE','PAYLOAD_MSI_HASH','PAYLOAD_COVERAGE','SOURCE_CHANGED','CAB_DATA_EXTRACTION_FAILED','LAYOUT_TOO_LARGE')
# Controller-only codes (pre-launch, launch and post-worker validation).
$script:controllerKnown=@('CANDIDATE_PATH','OUTPUT_PATH','OUTPUT_PREEXISTS','TRUST_RESULT_MISSING','TRUST_RESULT_UNREADABLE','TRUST_NOT_VERIFIED','WORK_DIRECTORY','JOB_HELPER_LOAD','JOB_LAUNCH','WORKER_TIMEOUT','WORKER_CLEANUP','WORKER_EXIT','WORKER_RESULT_MISSING','WORKER_RESULT_UNREADABLE','WORKER_RESULT_INVALID','WORKER_RESULT_COUNTS','EXPORT_LAYOUT_INVALID','EXPORT_PAYLOAD_INVALID','EXPORT_MOVE','WINDOWS_REQUIRED','WORKER_POLICY')
$script:errorTypes=@('COMException','IOException','UnauthorizedAccessException','PathTooLongException','DirectoryNotFoundException','FileNotFoundException','InvalidOperationException','ArgumentException','ArgumentNullException','NotSupportedException','OutOfMemoryException','Win32Exception','MethodInvocationException','RuntimeException','ParameterBindingException','CommandNotFoundException','PSInvalidCastException','InvalidCastException','NullReferenceException','IndexOutOfRangeException','KeyNotFoundException','SecurityException','CryptographicException','TypeInitializationException','PlatformNotSupportedException')
# Innermost exception type name (allowlisted) and numeric HRESULT only; never messages.
function Get-SafeErrorInfo($Exception){
 $item=$Exception;$depth=0
 while($null -ne $item.InnerException -and $depth -lt 8){$item=$item.InnerException;$depth++}
 $name=$item.GetType().Name
 return [ordered]@{errorType=$(if($name -cin $script:errorTypes){$name}else{'other'});errorHResult=('0x{0:X8}' -f $item.HResult)}
}
function New-SafeExportResult {
 return [ordered]@{
  format='htkk-source-payload-export-v1';version='5.8.1';status='blocked';failureCode='NOT_STARTED';stage='NOT_STARTED';controllerStage='NOT_STARTED';errorType=$null;errorHResult=$null
  ready=$false;automaticActivation=$false;vendorCodeExecuted=$false;installerExecuted=$false;msiCustomActionsExecuted=$false
  sourcePins=$script:pins;files=0;sizeMatches=0;msiHashMatches=0;versionedWithoutMsiHash=0
  layout=$null;workerScriptSha256=$null;cabinetHelperSha256=(Get-PrivateFileHash ([IO.Path]::Combine($PSScriptRoot,'HtkkSourceCabinet.cs')))
  workerStopped=$false;jobCleanupVerified=$false;workerTimedOut=$false;workerExitCode=$null
  lifetimeBoundary='windows-job-before-resume';workerTimeoutMilliseconds=420000;childEnvironmentPolicy='os-essentials-only'
 }
}
function Invoke-ExportWorker {
 $result=New-SafeExportResult;$result.workerScriptSha256=Get-PrivateFileHash $PSCommandPath;$phase='INPUT_POLICY';$installer=$null;$database=$null
 try{
  if(-not $IsWindows){throw 'WINDOWS_REQUIRED'}
  $candidate=Assert-PlainPath $CandidateDirectory $true;$work=Assert-PlainPath $WorkerDirectory $true
  $official=Assert-PlainPath ([IO.Path]::Combine($candidate,'official.rar')) $true
  $phase='ARCHIVE_PIN'
  if((Get-PrivateFileHash $official) -cne $script:pins.officialArchive){throw 'ARCHIVE_PIN_MISMATCH'}
  $phase='RUNNER_TOOLS'
  $tar=[IO.Path]::Combine($env:SystemRoot,'System32','tar.exe');Assert-RunnerTool $tar '(?i)(?:^|,\s*)O=Microsoft Corporation(?:,|$)'
  $phase='ARCHIVE_EXTRACTION'
  $distribution=[IO.Path]::Combine($work,'official');$null=[IO.Directory]::CreateDirectory($distribution)
  Invoke-ReadOnlyTool $tar @('-xf',$official,'-C',$distribution,'HTKK_5.8.1_DLL_signed/Data1.cab','HTKK_5.8.1_DLL_signed/HTKK.msi','HTKK_5.8.1_DLL_signed/setup.exe') $work
  $source=[IO.Path]::Combine($distribution,'HTKK_5.8.1_DLL_signed')
  $phase='DISTRIBUTION_HASH'
  foreach($item in @(@('msi','HTKK.msi'),@('setup','setup.exe'),@('cab','Data1.cab'))){
   if((Get-PrivateFileHash (Assert-PlainPath ([IO.Path]::Combine($source,$item[1])) $true)) -cne $script:pins[$item[0]]){throw 'DISTRIBUTION_HASH'}
  }
  $phase='MSI_OPEN'
  $msi=[IO.Path]::Combine($source,'HTKK.msi');$cab=[IO.Path]::Combine($source,'Data1.cab')
  $installer=New-Object -ComObject WindowsInstaller.Installer
  # Mode0 is read-only. Never call InstallProduct, ConfigureProduct, DoAction or msiexec.
  $database=$installer.OpenDatabase($msi,0)
  $phase='MSI_QUERY_MEDIA'
  $media=Read-MsiRows $database 'SELECT `DiskId`, `LastSequence`, `Cabinet` FROM `Media`' {param($r) [ordered]@{disk=[int]$r.IntegerData(1);last=[int]$r.IntegerData(2);cab=[string]$r.StringData(3)}}
  if($media.Count -ne 1 -or $media[0].disk -ne 1 -or $media[0].last -ne 4526 -or $media[0].cab -cne 'Data1.cab'){throw 'MSI_MEDIA'}
  $phase='MSI_QUERY_FILE'
  $files=Read-MsiRows $database 'SELECT `File`, `Component_`, `FileName`, `FileSize`, `Version`, `Sequence` FROM `File`' {param($r) [ordered]@{id=[string]$r.StringData(1);component=[string]$r.StringData(2);fileName=[string]$r.StringData(3);bytes=[int]$r.IntegerData(4);version=[string]$r.StringData(5);sequence=[int]$r.IntegerData(6)}}
  $phase='MSI_QUERY_COMPONENT'
  $components=Read-MsiRows $database 'SELECT `Component`, `Directory_` FROM `Component`' {param($r) [ordered]@{id=[string]$r.StringData(1);directory=[string]$r.StringData(2)}}
  $phase='MSI_QUERY_DIRECTORY'
  $directories=Read-MsiRows $database 'SELECT `Directory`, `Directory_Parent`, `DefaultDir` FROM `Directory`' {param($r) [ordered]@{id=[string]$r.StringData(1);parent=[string]$r.StringData(2);defaultDir=[string]$r.StringData(3)}}
  $phase='MSI_QUERY_HASH'
  $hashes=Read-MsiRows $database 'SELECT `File_`, `Options`, `HashPart1`, `HashPart2`, `HashPart3`, `HashPart4` FROM `MsiFileHash`' {
   param($r)
   $bytes=[Collections.Generic.List[byte]]::new();foreach($index in 3..6){$bytes.AddRange([BitConverter]::GetBytes([int]$r.IntegerData($index)))}
   [ordered]@{id=[string]$r.StringData(1);options=[int]$r.IntegerData(2);md5=[Convert]::ToHexString($bytes.ToArray()).ToLowerInvariant()}
  }
  $phase='MSI_IDENTITIES'
  if($files.Count -ne 4526 -or $hashes.Count -ne 4493 -or $components.Count -lt 1 -or $components.Count -gt 10000 -or $directories.Count -lt 1 -or $directories.Count -gt 10000){throw 'MSI_FILE_COUNTS'}
  $fileMap=[Collections.Generic.Dictionary[string,object]]::new([StringComparer]::OrdinalIgnoreCase)
  foreach($file in $files){
   if(-not $file.id -or $file.id.Length -gt 72 -or [IO.Path]::GetFileName($file.id) -cne $file.id -or $file.id.Contains(':') -or $file.id -in @('.','..') -or $file.bytes -lt 0 -or $fileMap.ContainsKey($file.id)){throw 'MSI_FILE_IDENTITIES'}
   $fileMap.Add($file.id,$file)
  }
  $hashMap=[Collections.Generic.Dictionary[string,string]]::new([StringComparer]::OrdinalIgnoreCase)
  foreach($entry in $hashes){if($entry.options -ne 0 -or -not $fileMap.ContainsKey($entry.id) -or $hashMap.ContainsKey($entry.id)){throw 'MSI_HASH_IDENTITIES'};$hashMap.Add($entry.id,$entry.md5)}
  $phase='CABINET_HELPER'
  Add-Type -Path ([IO.Path]::Combine($PSScriptRoot,'HtkkSourceCabinet.cs')) -ErrorAction Stop
  $ids=[string[]]@($files | ForEach-Object {$_.id});$sizes=[long[]]@($files | ForEach-Object {$_.bytes})
  $payload=[IO.Path]::Combine($work,'payload')
  $phase='CAB_EXTRACTION'
  $paths=[HtkkSourceCabinet]::Extract($cab,$payload,$ids,$sizes)
  $phase='PAYLOAD_VERIFY'
  $sizeMatches=0;$hashMatches=0;$gaps=0
  for($i=0;$i -lt $ids.Length;$i++){
   $leaf=Assert-PlainPath $paths[$i] $true;$file=$fileMap[$ids[$i]]
   if(([IO.FileInfo]::new($leaf)).Length -ne $file.bytes){throw 'PAYLOAD_SIZE'};$sizeMatches++
   if($hashMap.ContainsKey($file.id)){
    $stream=[IO.File]::OpenRead($leaf);$md5=[Security.Cryptography.MD5]::Create()
    try{$actual=[Convert]::ToHexString($md5.ComputeHash($stream)).ToLowerInvariant()}finally{$stream.Dispose();$md5.Dispose()}
    if($actual -cne $hashMap[$file.id]){throw 'PAYLOAD_MSI_HASH'};$hashMatches++
   }elseif([string]::IsNullOrWhiteSpace($file.version)){throw 'PAYLOAD_MSI_HASH'}else{$gaps++}
  }
  if($sizeMatches -ne 4526 -or $hashMatches -ne 4493 -or $gaps -ne 33){throw 'PAYLOAD_COVERAGE'}
  $phase='LAYOUT_WRITE'
  $layoutPath=[IO.Path]::Combine($work,'layout.json')
  $layout=[ordered]@{format='htkk-msi-layout-tables-v1';version='5.8.1';sourcePins=$script:pins;payloadNaming='payload/{index:D5}.bin in File-table order';files=@($files);components=@($components);directories=@($directories);fileHashes=@($hashes);ready=$false;automaticActivation=$false}
  Write-NewPrivateJson $layoutPath $layout
  if(([IO.FileInfo]::new($layoutPath)).Length -gt 16000000){throw 'LAYOUT_TOO_LARGE'}
  $phase='SOURCE_RECHECK'
  foreach($item in @(@('msi','HTKK.msi'),@('setup','setup.exe'),@('cab','Data1.cab'))){if((Get-PrivateFileHash ([IO.Path]::Combine($source,$item[1]))) -cne $script:pins[$item[0]]){throw 'SOURCE_CHANGED'}}
  if((Get-PrivateFileHash $official) -cne $script:pins.officialArchive){throw 'SOURCE_CHANGED'}
  $result.files=$files.Count;$result.sizeMatches=$sizeMatches;$result.msiHashMatches=$hashMatches;$result.versionedWithoutMsiHash=$gaps
  $result.layout=[ordered]@{path='layout.json';sha256=(Get-PrivateFileHash $layoutPath);bytes=([IO.FileInfo]::new($layoutPath)).Length}
  $result.status='exported';$result.failureCode=$null
 }catch{
  $result.failureCode=if($_.Exception.Message -cin $script:known){$_.Exception.Message}else{$phase}
  $info=Get-SafeErrorInfo $_.Exception;$result.errorType=$info.errorType;$result.errorHResult=$info.errorHResult
 }finally{Release-ComObject $database;Release-ComObject $installer}
 $result.stage=$phase
 Write-NewPrivateJson $ResultPath $result
}
if($Worker){
 try{Invoke-ExportWorker}catch{Write-HtkkBootstrapFailure $ResultPath 'WORKER_UNHANDLED' 'WORKER';exit 4}
 exit 0
}
# Fixed public line: every interpolated value is re-validated against a fixed shape.
function Write-SafeExportLine($Result){
 $code=if($null -eq $Result.failureCode){'NONE'}elseif([string]$Result.failureCode -cmatch '^[A-Z0-9_]{1,48}$'){[string]$Result.failureCode}else{'INVALID_CODE'}
 $stage=if([string]$Result.stage -cmatch '^[A-Z0-9_]{1,48}$'){[string]$Result.stage}else{'INVALID_STAGE'}
 $controller=if([string]$Result.controllerStage -cmatch '^[A-Z0-9_]{1,48}$'){[string]$Result.controllerStage}else{'INVALID_STAGE'}
 $type=if([string]$Result.errorType -cin (@('other')+$script:errorTypes)){[string]$Result.errorType}else{'none'}
 $hresult=if([string]$Result.errorHResult -cmatch '^0x[0-9A-F]{8}$'){[string]$Result.errorHResult}else{'none'}
 $exit=if($Result.workerExitCode -is [int] -or $Result.workerExitCode -is [long]){[string][long]$Result.workerExitCode}else{'none'}
 $status=if([string]$Result.status -cin @('exported','blocked')){[string]$Result.status}else{'blocked'}
 [Console]::WriteLine('Source payload export: '+$status+'; code='+$code+'; stage='+$stage+'; controller='+$controller+'; error='+$type+'; hresult='+$hresult+'; workerExit='+$exit+'; ready=false; worker stopped='+[bool]$Result.workerStopped)
}
$result=New-SafeExportResult;$result.workerScriptSha256=Get-PrivateFileHash $PSCommandPath
$owner=$null;$work=$null;$safeCleanup=$true;$launchAttempted=$false;$step='CANDIDATE_PATH'
try{
 $result.controllerStage=$step
 $candidate=Assert-PlainPath $CandidateDirectory $true
 $step='OUTPUT_PATH';$result.controllerStage=$step
 $target=Assert-PlainPath $ResultPath $false;$output=Assert-PlainPath $OutputDirectory $false
 $step='OUTPUT_PREEXISTS';$result.controllerStage=$step
 if([IO.File]::Exists($target) -or [IO.Directory]::Exists($target) -or [IO.File]::Exists($output) -or [IO.Directory]::Exists($output)){throw 'OUTPUT_PREEXISTS'}
 $step='TRUST_RESULT_MISSING';$result.controllerStage=$step
 $trust=Assert-PlainPath ([IO.Path]::Combine($candidate,'trust.json')) $true
 $step='TRUST_RESULT_UNREADABLE';$result.controllerStage=$step
 if(([IO.FileInfo]::new($trust)).Length -gt 65536){throw 'TRUST_RESULT_UNREADABLE'}
 $trusted=[IO.File]::ReadAllText($trust,[Text.UTF8Encoding]::new($false)) | ConvertFrom-Json -AsHashtable
 # Export only after the separate signature/revocation verifier succeeded and stopped.
 $step='TRUST_NOT_VERIFIED';$result.controllerStage=$step
 if($trusted -isnot [Collections.IDictionary] -or $trusted['status'] -cne 'baseline-verified' -or $trusted['workerStopped'] -ne $true -or $trusted['jobCleanupVerified'] -ne $true -or $trusted['ready'] -ne $false -or $trusted['vendorCodeExecuted'] -ne $false){throw 'TRUST_NOT_VERIFIED'}
 $step='WINDOWS_REQUIRED';$result.controllerStage=$step
 if(-not $IsWindows){throw 'WINDOWS_REQUIRED'}
 $step='WORK_DIRECTORY';$result.controllerStage=$step
 $work=[IO.Path]::Combine($candidate,('export-work-'+[Guid]::NewGuid().ToString('N')));$null=[IO.Directory]::CreateDirectory($work)
 $workerResult=[IO.Path]::Combine($work,'worker-result.json')
 $step='JOB_HELPER_LOAD';$result.controllerStage=$step
 . ([IO.Path]::Combine($PSScriptRoot,'Invoke-HtkkBoundedJobProcess.ps1'))
 $step='JOB_LAUNCH';$result.controllerStage=$step
 $launchAttempted=$true;$safeCleanup=$false
 $owner=New-HtkkBoundedJobOwner -Executable ([Diagnostics.Process]::GetCurrentProcess().MainModule.FileName) -WorkingDirectory $work -Arguments @('-NoLogo','-NoProfile','-NonInteractive','-File',$PSCommandPath,'-Worker','-CandidateDirectory',$candidate,'-WorkerDirectory',$work,'-OutputDirectory',$output,'-ResultPath',$workerResult)
 $safeCleanup=$false
 $step='WORKER_TIMEOUT';$result.controllerStage=$step
 if($owner.WaitForRootExit(420000)){$result.workerExitCode=[BitConverter]::ToInt32([BitConverter]::GetBytes([uint32]$owner.RootExitCode),0)}else{$result.workerTimedOut=$true}
 $step='WORKER_CLEANUP';$result.controllerStage=$step
 $owner.Dispose();$safeCleanup=$owner.CleanupVerified -is [bool] -and $owner.CleanupVerified
 $result.workerStopped=$safeCleanup;$result.jobCleanupVerified=$safeCleanup
 if(-not $safeCleanup){$step='WORKER_CLEANUP';throw 'WORKER_CLEANUP'}
 if($result.workerTimedOut){throw 'WORKER_TIMEOUT'}
 $step='WORKER_RESULT_MISSING';$result.controllerStage=$step
 # A worker that wrote a bounded blocked result is reported by ITS code, even on a nonzero exit.
 if(-not [IO.File]::Exists($workerResult)){if($result.workerExitCode -ne 0){$step='WORKER_EXIT';throw 'WORKER_EXIT'};throw 'WORKER_RESULT_MISSING'}
 $step='WORKER_RESULT_UNREADABLE';$result.controllerStage=$step
 if(([IO.FileInfo]::new($workerResult)).Length -gt 16384){throw 'WORKER_RESULT_UNREADABLE'}
 $child=[IO.File]::ReadAllText($workerResult,[Text.UTF8Encoding]::new($false)) | ConvertFrom-Json -AsHashtable
 $step='WORKER_RESULT_INVALID';$result.controllerStage=$step
 if($child -isnot [Collections.IDictionary] -or $child['format'] -cne $result.format -or $child['version'] -cne '5.8.1' -or $child['ready'] -ne $false -or $child['automaticActivation'] -ne $false -or $child['vendorCodeExecuted'] -ne $false -or $child['installerExecuted'] -ne $false -or $child['msiCustomActionsExecuted'] -ne $false -or $child['status'] -cnotin @('blocked','exported')){throw 'WORKER_RESULT_INVALID'}
 if($child['status'] -ceq 'blocked'){
  # Copy only bounded diagnostic fields; the line writer re-validates their shape.
  foreach($key in @('failureCode','stage','errorType','errorHResult')){$result[$key]=$child[$key]}
  if([string]$result.failureCode -cnotin ($script:known+@('HELPER_LOAD','WORKER_UNHANDLED','INPUT_POLICY','ARCHIVE_PIN','RUNNER_TOOLS','ARCHIVE_EXTRACTION','MSI_OPEN','MSI_QUERY_MEDIA','MSI_QUERY_FILE','MSI_QUERY_COMPONENT','MSI_QUERY_DIRECTORY','MSI_QUERY_HASH','MSI_IDENTITIES','CABINET_HELPER','CAB_EXTRACTION','PAYLOAD_VERIFY','LAYOUT_WRITE','SOURCE_RECHECK'))){$result.failureCode='WORKER_RESULT_INVALID'}
  $result.controllerStage='WORKER_BLOCKED'
 }else{
  if($child['workerScriptSha256'] -cne $result.workerScriptSha256 -or $child['cabinetHelperSha256'] -cne $result.cabinetHelperSha256){throw 'WORKER_RESULT_INVALID'}
  $step='WORKER_RESULT_COUNTS';$result.controllerStage=$step
  if($null -ne $child['failureCode'] -or $child['files'] -ne 4526 -or $child['sizeMatches'] -ne 4526 -or $child['msiHashMatches'] -ne 4493 -or $child['versionedWithoutMsiHash'] -ne 33){throw 'WORKER_RESULT_COUNTS'}
  $step='EXPORT_LAYOUT_INVALID';$result.controllerStage=$step
  $layoutFile=Assert-PlainPath ([IO.Path]::Combine($work,'layout.json')) $true
  if($child['layout'] -isnot [Collections.IDictionary] -or $child['layout']['path'] -cne 'layout.json' -or $child['layout']['bytes'] -gt 16000000 -or ([IO.FileInfo]::new($layoutFile)).Length -ne $child['layout']['bytes'] -or (Get-PrivateFileHash $layoutFile) -cne $child['layout']['sha256']){throw 'EXPORT_LAYOUT_INVALID'}
  $step='EXPORT_PAYLOAD_INVALID';$result.controllerStage=$step
  $payloadDirectory=Assert-PlainPath ([IO.Path]::Combine($work,'payload')) $true
  if(@([IO.Directory]::GetFileSystemEntries($payloadDirectory)).Count -ne 4526){throw 'EXPORT_PAYLOAD_INVALID'}
  $step='EXPORT_MOVE';$result.controllerStage=$step
  $null=[IO.Directory]::CreateDirectory($output)
  [IO.File]::Move($layoutFile,[IO.Path]::Combine($output,'layout.json'))
  [IO.Directory]::Move($payloadDirectory,[IO.Path]::Combine($output,'payload'))
  foreach($key in @('status','failureCode','stage','files','sizeMatches','msiHashMatches','versionedWithoutMsiHash','layout')){$result[$key]=$child[$key]}
  $result.controllerStage='DONE'
 }
}catch{
 if($launchAttempted -and $null -eq $owner){
  $errorItem=$_.Exception;while($null -ne $errorItem.InnerException){$errorItem=$errorItem.InnerException}
  $cleanFailures=@('launch-arguments-invalid','job-create-failed','job-limit-failed','environment-invalid','stdio-create-failed','handle-list-failed','process-create-failed','job-assignment-failed','process-identity-failed','process-resume-failed','boundary-tool-failure')
  $safeCleanup=$errorItem -is [InvalidOperationException] -and $errorItem.Message -cin $cleanFailures
 }
 if(-not $launchAttempted){$safeCleanup=$true}
 $result.failureCode=if([string]$_.Exception.Message -cin $script:controllerKnown){[string]$_.Exception.Message}elseif($step -cin $script:controllerKnown){$step}else{'WORKER_POLICY'}
 $result.controllerStage=$step
 $info=Get-SafeErrorInfo $_.Exception;$result.errorType=$info.errorType;$result.errorHResult=$info.errorHResult
 $result.status='blocked'
}finally{
 if($null -ne $owner -and -not $safeCleanup){try{$owner.Dispose();$safeCleanup=$owner.CleanupVerified -is [bool] -and $owner.CleanupVerified}catch{$safeCleanup=$false}}
 $result.workerStopped=$safeCleanup;$result.jobCleanupVerified=$safeCleanup
 if(-not $safeCleanup){$result.status='blocked';$result.failureCode='WORKER_CLEANUP'}
 if($work -and $safeCleanup -and [IO.Directory]::Exists($work)){Remove-Item -LiteralPath $work -Recurse -Force -ErrorAction SilentlyContinue}
}
if($result.status -cne 'exported' -and $null -eq $result.failureCode){$result.failureCode='WORKER_POLICY'}
Write-NewPrivateJson $ResultPath $result
Write-SafeExportLine $result
