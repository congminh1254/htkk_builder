# Inspect only the reviewed 5.8.1 distribution as data; never install or run vendor code.
# The caller must run publication separately, after workerStopped/jobCleanupVerified.
[CmdletBinding()]
param(
 [Parameter(Mandatory=$true)][string]$CandidateDirectory,
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
$script:pins=[ordered]@{
 officialArchive='5d52c06595e933a3b246480785d5d4010fad669baed6fb38311f8a09b20e1e95'
 mirrorArchive='3f50ede214d802984549aa3841c3de6614fca90021ef5029a9c1ac1999776edb'
 msi='7c1da251ee2acd126a2363e4457502b8ad6fc0792d78dc0a92b153701dc29080'
 setup='19394e89351dc213306864168e16808d48401597f56d5fe4c977f9a5833d2936'
 cab='00669905937fb29e10cb53209ece5e8a9f8097970e4cb40bb28f89baa9fc3744'
 signerRoot='7b9d553e1c92cb6e8803e137f4f287d4363757f5d44b37d52f9fca22fb97df86'
}
$script:flagNames=@('archivePinsMatched','officialDistributionFilesMatched','extractorTrusted','signToolTrusted','msiAuthenticodeValid','setupAuthenticodeValid','msiPublisherMatched','setupPublisherMatched','msiTimestampValid','setupTimestampValid','signerRevocationVerified','timestampRevocationVerified','msiCabMediaMatched','payloadSizesMatched','payloadMsiHashesMatched','payloadVersionMatched','sourceFilesUnmodified')
function New-SafeTrustResult {
 $flags=[ordered]@{};foreach($name in $script:flagNames){$flags[$name]=$false}
 return [ordered]@{
  format='htkk-source-candidate-trust-v1';version='5.8.1';status='blocked';failureCode='NOT_STARTED';verificationStage='not-started'
  ready=$false;automaticActivation=$false;adapterActivated=$false
  vendorCodeExecuted=$false;installerExecuted=$false;msiCustomActionsExecuted=$false;mirrorUsed=$false;mirrorCompared=$false
  sourcePins=$script:pins;actualHashes=[ordered]@{officialArchive=$null;mirrorArchive=$null;msi=$null;setup=$null;cab=$null}
  checks=$flags
  payload=[ordered]@{files=0;sizeMatches=0;msiHashMatches=0;versionedWithoutMsiHash=0;sha256Entries=0;fullyCoveredBySignedMsiHashes=$false}
  payloadManifest=$null
  extractorPolicy='microsoft-signed-system32-tar-pinned-members';revocationPolicy='online-exclude-root-no-verification-exceptions';revocationUrlTimeoutSeconds=10
  timestampPolicy='authenticode-and-signtool-all-signatures-with-timestamp-certificate-chain'
  cabinetHelperSha256=(Get-PrivateFileHash ([IO.Path]::Combine($PSScriptRoot,'HtkkSourceCabinet.cs')));workerScriptSha256=$null;workerStopped=$false;jobCleanupVerified=$false;workerTimedOut=$false;workerExitCode=$null
  lifetimeBoundary='windows-job-before-resume';workerTimeoutMilliseconds=180000;childEnvironmentPolicy='os-essentials-only'
 }
}
function Get-BytesSha256([byte[]]$Bytes){$hash=[Security.Cryptography.SHA256]::Create();try{return [Convert]::ToHexString($hash.ComputeHash($Bytes)).ToLowerInvariant()}finally{$hash.Dispose()}}
function Get-PrivateFileHash([string]$Path){$stream=[IO.File]::OpenRead($Path);$hash=[Security.Cryptography.SHA256]::Create();try{return [Convert]::ToHexString($hash.ComputeHash($stream)).ToLowerInvariant()}finally{$stream.Dispose();$hash.Dispose()}}
function Assert-PlainPath([string]$Path,[bool]$MustExist){
 $full=[IO.Path]::GetFullPath($Path)
 if(-not [IO.Path]::IsPathFullyQualified($Path) -or ($IsWindows -and $full.StartsWith('\\'))){throw 'PATH_POLICY'}
 $current=$full
 while($current){
  if([IO.File]::Exists($current) -or [IO.Directory]::Exists($current)){
   if(([IO.File]::GetAttributes($current) -band [IO.FileAttributes]::ReparsePoint) -ne 0){throw 'PATH_POLICY'}
  }
  $parent=[IO.Path]::GetDirectoryName($current);if($parent -eq $current){break};$current=$parent
 }
 if($MustExist -and -not ([IO.File]::Exists($full) -or [IO.Directory]::Exists($full))){throw 'INPUT_MISSING'}
 return $full
}
function Write-NewPrivateJson([string]$Path,$Object){
 $null=Assert-PlainPath $Path $false
 $bytes=[Text.UTF8Encoding]::new($false).GetBytes((ConvertTo-Json -InputObject $Object -Depth 8 -Compress)+"`n")
 $stream=[IO.FileStream]::new($Path,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
 try{$stream.Write($bytes,0,$bytes.Length)}finally{$stream.Dispose()}
}
function Invoke-ReadOnlyTool([string]$Executable,[string[]]$Arguments,[string]$WorkingDirectory){
 # Worker already owns a before-resume Windows Job with NUL stdio and no credentials.
 # Descendant tools inherit that Job and NUL handles; no pipes/logs retain tool output.
 $info=[Diagnostics.ProcessStartInfo]::new();$info.FileName=$Executable;$info.WorkingDirectory=$WorkingDirectory
 $info.UseShellExecute=$false;$info.CreateNoWindow=$true
 foreach($argument in $Arguments){$info.ArgumentList.Add($argument)}
 $process=$null
 try{
  $process=[Diagnostics.Process]::Start($info)
  if(-not $process.WaitForExit(30000)){$process.Kill($true);$null=$process.WaitForExit(5000);throw 'TOOL_TIMEOUT'}
  if($process.ExitCode -ne 0){throw 'TOOL_REJECTED'}
 }finally{
  if($null -ne $process){try{if(-not $process.HasExited){$process.Kill($true);$null=$process.WaitForExit(5000)}}finally{$process.Dispose()}}
 }
}
function Assert-RunnerTool([string]$Path,[string]$PublisherPattern){
 $null=Assert-PlainPath $Path $true
 $signature=Get-AuthenticodeSignature -LiteralPath $Path -ErrorAction Stop
 if($signature.Status -ne 'Valid' -or $null -eq $signature.SignerCertificate -or $signature.SignerCertificate.Subject -notmatch $PublisherPattern){throw 'RUNNER_TOOL_TRUST'}
}
function Assert-OnlineChain($Certificate,[string]$Eku,[bool]$PinPublisherRoot){
 $chain=[Security.Cryptography.X509Certificates.X509Chain]::new()
 try{
  $chain.ChainPolicy.RevocationMode=[Security.Cryptography.X509Certificates.X509RevocationMode]::Online
  $chain.ChainPolicy.RevocationFlag=[Security.Cryptography.X509Certificates.X509RevocationFlag]::ExcludeRoot
  $chain.ChainPolicy.VerificationFlags=[Security.Cryptography.X509Certificates.X509VerificationFlags]::NoFlag
  $chain.ChainPolicy.UrlRetrievalTimeout=[TimeSpan]::FromSeconds(10)
  $null=$chain.ChainPolicy.ApplicationPolicy.Add([Security.Cryptography.Oid]::new($Eku))
  if(-not $chain.Build($Certificate) -or $chain.ChainStatus.Count -ne 0){throw 'REVOCATION_OR_CHAIN'}
  if($PinPublisherRoot){
   $last=$chain.ChainElements[$chain.ChainElements.Count-1].Certificate
   if((Get-BytesSha256 $last.RawData) -cne $script:pins.signerRoot){throw 'PUBLISHER_ROOT'}
  }
 }finally{$chain.Dispose()}
}
function Test-SignedDistributionFile([string]$Path,[string]$Kind,[string]$SignTool,[string]$Work,$Result){
 $signature=Get-AuthenticodeSignature -LiteralPath $Path -ErrorAction Stop
 if($signature.Status -ne 'Valid' -or $null -eq $signature.SignerCertificate -or $null -eq $signature.TimeStamperCertificate){throw 'AUTHENTICODE_OR_TIMESTAMP'}
 if($signature.SignerCertificate.SerialNumber -cne '6435F70483012A5DBC374003' -or $signature.SignerCertificate.Subject -notmatch 'Tổng Cục Thuế'){throw 'PUBLISHER_IDENTITY'}
 $Result.checks[($Kind+'PublisherMatched')]=$true
 Assert-OnlineChain $signature.SignerCertificate '1.3.6.1.5.5.7.3.3' $true
 Assert-OnlineChain $signature.TimeStamperCertificate '1.3.6.1.5.5.7.3.8' $false
 Invoke-ReadOnlyTool $SignTool @('verify','/pa','/all','/v',$Path) $Work
 $Result.checks[($Kind+'AuthenticodeValid')]=$true;$Result.checks[($Kind+'TimestampValid')]=$true
}
function Release-ComObject($Object){if($null -ne $Object -and [Runtime.InteropServices.Marshal]::IsComObject($Object)){$null=[Runtime.InteropServices.Marshal]::FinalReleaseComObject($Object)}}
function Read-MsiRows($Database,[string]$Sql,[scriptblock]$Read){
 $view=$null;$record=$null;$rows=[Collections.Generic.List[object]]::new()
 try{
  $view=$Database.OpenView($Sql);$null=$view.Execute()
  while($null -ne ($record=$view.Fetch())){try{$rows.Add((& $Read $record))}finally{Release-ComObject $record;$record=$null}}
 }finally{if($null -ne $view){$null=$view.Close()};Release-ComObject $view}
 return ,$rows
}
function Verify-CabPayload([string]$Msi,[string]$Cab,[string]$Seven,[string]$Work,[string]$ManifestPath,$Result){
 $installer=$null;$database=$null
 try{
  $installer=New-Object -ComObject WindowsInstaller.Installer
  # Mode0 is read-only. Never call InstallProduct, ConfigureProduct or msiexec.
  $database=$installer.OpenDatabase($Msi,0)
  $media=Read-MsiRows $database 'SELECT `DiskId`, `LastSequence`, `Cabinet` FROM `Media`' {param($r) [ordered]@{disk=[int]$r.IntegerData(1);last=[int]$r.IntegerData(2);cab=[string]$r.StringData(3)}}
  if($media.Count -ne 1 -or $media[0].disk -ne 1 -or $media[0].last -ne 4526 -or $media[0].cab -cne 'Data1.cab'){throw 'MSI_MEDIA'}
  $Result.checks.msiCabMediaMatched=$true
  $files=Read-MsiRows $database 'SELECT `File`, `FileSize`, `Version` FROM `File`' {param($r) [ordered]@{id=[string]$r.StringData(1);bytes=[int]$r.IntegerData(2);version=[string]$r.StringData(3)}}
  $hashes=Read-MsiRows $database 'SELECT `File_`, `Options`, `HashPart1`, `HashPart2`, `HashPart3`, `HashPart4` FROM `MsiFileHash`' {
   param($r)
   $bytes=[Collections.Generic.List[byte]]::new();foreach($index in 3..6){$bytes.AddRange([BitConverter]::GetBytes([int]$r.IntegerData($index)))}
   [ordered]@{id=[string]$r.StringData(1);options=[int]$r.IntegerData(2);md5=[Convert]::ToHexString($bytes.ToArray()).ToLowerInvariant()}
  }
  if($files.Count -ne 4526 -or $hashes.Count -ne 4493){throw 'MSI_FILE_COUNTS'}
  $fileMap=[Collections.Generic.Dictionary[string,object]]::new([StringComparer]::OrdinalIgnoreCase)
  foreach($file in $files){
   if(-not $file.id -or $file.id.Length -gt 72 -or [IO.Path]::GetFileName($file.id) -cne $file.id -or $file.id.Contains(':') -or $file.id -in @('.','..') -or $file.bytes -lt 0 -or $fileMap.ContainsKey($file.id)){throw 'MSI_FILE_IDENTITIES'}
   $fileMap.Add($file.id,$file)
  }
  $hashMap=[Collections.Generic.Dictionary[string,string]]::new([StringComparer]::OrdinalIgnoreCase)
  foreach($entry in $hashes){if($entry.options -ne 0 -or -not $fileMap.ContainsKey($entry.id) -or $hashMap.ContainsKey($entry.id)){throw 'MSI_HASH_IDENTITIES'};$hashMap.Add($entry.id,$entry.md5)}
  $payload=[IO.Path]::Combine($Work,'payload')
  Add-Type -Path ([IO.Path]::Combine($PSScriptRoot,'HtkkSourceCabinet.cs')) -ErrorAction Stop
  $ids=[string[]]@($files | ForEach-Object {$_.id});$sizes=[long[]]@($files | ForEach-Object {$_.bytes})
  $paths=[HtkkSourceCabinet]::Extract($Cab,$payload,$ids,$sizes)
  $all=@();for($i=0;$i -lt $ids.Length;$i++){$all+=@{Name=$ids[$i];FullName=$paths[$i];Length=([IO.FileInfo]::new($paths[$i])).Length}}
  $entries=[Collections.Generic.List[object]]::new();$sizeMatches=0;$hashMatches=0;$gaps=0
  foreach($leaf in $all){
   $null=Assert-PlainPath $leaf.FullName $true
   if(-not $fileMap.ContainsKey($leaf.Name) -or $leaf.Length -ne $fileMap[$leaf.Name].bytes){throw 'PAYLOAD_SIZE'}
   $sizeMatches++;$file=$fileMap[$leaf.Name];$matched=$false
   if($hashMap.ContainsKey($leaf.Name)){
    $stream=[IO.File]::OpenRead($leaf.FullName);$md5=[Security.Cryptography.MD5]::Create()
    try{$actual=[Convert]::ToHexString($md5.ComputeHash($stream)).ToLowerInvariant()}finally{$stream.Dispose();$md5.Dispose()}
    if($actual -cne $hashMap[$leaf.Name]){throw 'PAYLOAD_MSI_HASH'};$hashMatches++;$matched=$true
   }else{if([string]::IsNullOrWhiteSpace($file.version)){throw 'UNVERSIONED_HASH_GAP'};$gaps++}
   $entries.Add([ordered]@{fileId=$file.id;bytes=$leaf.Length;sha256=(Get-PrivateFileHash $leaf.FullName);msiHashVerified=$matched;versioned=(-not [string]::IsNullOrWhiteSpace($file.version))})
  }
  if($sizeMatches -ne 4526 -or $hashMatches -ne 4493 -or $gaps -ne 33){throw 'PAYLOAD_COVERAGE'}
  $settings=[Xml.XmlReaderSettings]::new();$settings.DtdProcessing=[Xml.DtdProcessing]::Prohibit;$settings.XmlResolver=$null
  $configIndex=[Array]::FindIndex($ids,[Predicate[string]]{param($id) $id -ceq 'htkk.exe.config'});if($configIndex -lt 0){throw 'PAYLOAD_VERSION'}
  $reader=[Xml.XmlReader]::Create($paths[$configIndex],$settings)
  try{$doc=[Xml.XmlDocument]::new();$doc.XmlResolver=$null;$doc.Load($reader)}finally{$reader.Dispose()}
  $versions=@($doc.SelectNodes('/configuration/appSettings/add[@key="VERSION"]'))
  if($versions.Count -ne 1 -or $versions[0].GetAttribute('value') -cne '5.8.1' -or -not $hashMap.ContainsKey('htkk.exe.config')){throw 'PAYLOAD_VERSION'}
  $Result.checks.payloadVersionMatched=$true;$Result.checks.payloadSizesMatched=$true;$Result.checks.payloadMsiHashesMatched=$true
  $manifest=[ordered]@{format='htkk-reviewed-source-payload-sha256-v1';version='5.8.1';sourcePins=$script:pins;files=@($entries | Sort-Object fileId);signedMsiHashAlgorithm='MD5-legacy';versionedWithoutMsiHash=33;fullyCoveredBySignedMsiHashes=$false;ready=$false;automaticActivation=$false}
  Write-NewPrivateJson $ManifestPath $manifest
  $Result.payload=[ordered]@{files=$files.Count;sizeMatches=$sizeMatches;msiHashMatches=$hashMatches;versionedWithoutMsiHash=$gaps;sha256Entries=$entries.Count;fullyCoveredBySignedMsiHashes=$false}
  $Result.payloadManifest=[ordered]@{path='payload-sha256.json';sha256=(Get-PrivateFileHash $ManifestPath);bytes=([IO.FileInfo]::new($ManifestPath)).Length;entries=$entries.Count}
 }finally{Release-ComObject $database;Release-ComObject $installer}
}
function Invoke-TrustWorker {
 $result=New-SafeTrustResult;$result.workerScriptSha256=Get-PrivateFileHash $PSCommandPath;$phase='INPUT_POLICY'
 try{
  if(-not $IsWindows){throw 'WINDOWS_REQUIRED'}
  $candidate=Assert-PlainPath $CandidateDirectory $true;$work=Assert-PlainPath $WorkerDirectory $true
  $official=Assert-PlainPath ([IO.Path]::Combine($candidate,'official.rar')) $true
  $mirror=[IO.Path]::Combine($candidate,'mirror.zip');$hasMirror=[IO.File]::Exists($mirror);$result.mirrorUsed=$hasMirror
  if($hasMirror){$mirror=Assert-PlainPath $mirror $true}
  $result.actualHashes.officialArchive=Get-PrivateFileHash $official;if($hasMirror){$result.actualHashes.mirrorArchive=Get-PrivateFileHash $mirror}
  if($result.actualHashes.officialArchive -cne $script:pins.officialArchive -or ($hasMirror -and $result.actualHashes.mirrorArchive -cne $script:pins.mirrorArchive)){throw 'ARCHIVE_PIN_MISMATCH'}
  $result.checks.archivePinsMatched=$true
  $phase='RUNNER_TOOLS'
  $seven=[IO.Path]::Combine($env:SystemRoot,'System32','tar.exe');Assert-RunnerTool $seven '(?i)(?:^|,\s*)O=Microsoft Corporation(?:,|$)';$result.checks.extractorTrusted=$true
  $sdk=[IO.Path]::Combine([Environment]::GetFolderPath([Environment+SpecialFolder]::ProgramFilesX86),'Windows Kits','10','bin','*','x64','signtool.exe')
  $signTool=Get-ChildItem $sdk -ErrorAction Stop | Sort-Object FullName -Descending | Select-Object -First 1
  if($null -eq $signTool){throw 'RUNNER_TOOLS'}
  Assert-RunnerTool $signTool.FullName '(?i)(?:^|,\s*)O=Microsoft Corporation(?:,|$)';$result.checks.signToolTrusted=$true
  $phase='ARCHIVE_EXTRACTION'
  $names=@('HTKK_5.8.1_DLL_signed/Data1.cab','HTKK_5.8.1_DLL_signed/HTKK.msi','HTKK_5.8.1_DLL_signed/setup.exe')
  $distributions=,@($official,'official');if($hasMirror){$distributions+=,@($mirror,'mirror')}
  foreach($pair in $distributions){
   $destination=[IO.Path]::Combine($work,$pair[1]);$null=[IO.Directory]::CreateDirectory($destination)
   Invoke-ReadOnlyTool $seven (@('-xf',$pair[0],'-C',$destination)+$names) $work
  }
  $source=[IO.Path]::Combine($work,'official','HTKK_5.8.1_DLL_signed');$mirrorSource=[IO.Path]::Combine($work,'mirror','HTKK_5.8.1_DLL_signed')
  foreach($item in @(@('msi','HTKK.msi'),@('setup','setup.exe'),@('cab','Data1.cab'))){
   $path=Assert-PlainPath ([IO.Path]::Combine($source,$item[1])) $true
   if($hasMirror){$other=Assert-PlainPath ([IO.Path]::Combine($mirrorSource,$item[1])) $true}
   $actual=Get-PrivateFileHash $path
   if($actual -cne $script:pins[$item[0]] -or ($hasMirror -and (Get-PrivateFileHash $other) -cne $actual)){throw 'DISTRIBUTION_HASH'}
   $result.actualHashes[$item[0]]=$actual
  }
  $result.checks.officialDistributionFilesMatched=$true;$result.mirrorCompared=$hasMirror
  $phase='SIGNATURE_CHAIN'
  Test-SignedDistributionFile ([IO.Path]::Combine($source,'HTKK.msi')) 'msi' $signTool.FullName $work $result
  Test-SignedDistributionFile ([IO.Path]::Combine($source,'setup.exe')) 'setup' $signTool.FullName $work $result
  $result.checks.signerRevocationVerified=$true;$result.checks.timestampRevocationVerified=$true
  $phase='MSI_CAB_PAYLOAD'
  Verify-CabPayload ([IO.Path]::Combine($source,'HTKK.msi')) ([IO.Path]::Combine($source,'Data1.cab')) $seven $work ([IO.Path]::Combine($work,'payload-sha256.json')) $result
  foreach($item in @(@('msi','HTKK.msi'),@('setup','setup.exe'),@('cab','Data1.cab'))){if((Get-PrivateFileHash ([IO.Path]::Combine($source,$item[1]))) -cne $script:pins[$item[0]]){throw 'SOURCE_CHANGED'}}
  if((Get-PrivateFileHash $official) -cne $script:pins.officialArchive -or ($hasMirror -and (Get-PrivateFileHash $mirror) -cne $script:pins.mirrorArchive)){throw 'SOURCE_CHANGED'}
  $result.checks.sourceFilesUnmodified=$true;$result.status='baseline-verified';$result.failureCode=$null
 }catch{
  $known=@('WINDOWS_REQUIRED','INPUT_MISSING','PATH_POLICY','ARCHIVE_PIN_MISMATCH','RUNNER_TOOL_TRUST','TOOL_TIMEOUT','TOOL_REJECTED','REVOCATION_OR_CHAIN','PUBLISHER_ROOT','AUTHENTICODE_OR_TIMESTAMP','PUBLISHER_IDENTITY','MSI_MEDIA','MSI_FILE_COUNTS','MSI_FILE_IDENTITIES','MSI_HASH_IDENTITIES','CAB_FILE_COUNTS','PAYLOAD_SIZE','PAYLOAD_MSI_HASH','UNVERSIONED_HASH_GAP','PAYLOAD_COVERAGE','PAYLOAD_VERSION','SOURCE_CHANGED')
  $result.failureCode=if($_.Exception.Message -cin $known){$_.Exception.Message}else{$phase}
 }
 $result.verificationStage=$phase
 Write-NewPrivateJson $ResultPath $result
}
if($Worker){Invoke-TrustWorker;exit 0}
$result=New-SafeTrustResult;$result.workerScriptSha256=Get-PrivateFileHash $PSCommandPath
$owner=$null;$work=$null;$safeCleanup=$true;$launchAttempted=$false
try{
 $candidate=Assert-PlainPath $CandidateDirectory $true;$target=Assert-PlainPath $ResultPath $false
 if([IO.File]::Exists($target) -or [IO.Directory]::Exists($target) -or [IO.File]::Exists([IO.Path]::Combine($candidate,'payload-sha256.json'))){throw 'OUTPUT_PREEXISTS'}
 if(-not $IsWindows){$result.failureCode='WINDOWS_REQUIRED'}else{
  $work=[IO.Path]::Combine($candidate,('trust-work-'+[Guid]::NewGuid().ToString('N')));$null=[IO.Directory]::CreateDirectory($work)
  $workerResult=[IO.Path]::Combine($work,'worker-result.json')
  . ([IO.Path]::Combine($PSScriptRoot,'Invoke-HtkkBoundedJobProcess.ps1'))
  $launchAttempted=$true;$safeCleanup=$false
  $owner=New-HtkkBoundedJobOwner -Executable ([Diagnostics.Process]::GetCurrentProcess().MainModule.FileName) -WorkingDirectory $work -Arguments @('-NoLogo','-NoProfile','-NonInteractive','-File',$PSCommandPath,'-Worker','-CandidateDirectory',$candidate,'-WorkerDirectory',$work,'-ResultPath',$workerResult)
  $safeCleanup=$false
  if($owner.WaitForRootExit(180000)){$result.workerExitCode=[BitConverter]::ToInt32([BitConverter]::GetBytes([uint32]$owner.RootExitCode),0)}else{$result.workerTimedOut=$true;$result.failureCode='WORKER_TIMEOUT'}
  $owner.Dispose();$safeCleanup=$owner.CleanupVerified -is [bool] -and $owner.CleanupVerified
  $result.workerStopped=$safeCleanup;$result.jobCleanupVerified=$safeCleanup
  if(-not $safeCleanup){$result.failureCode='WORKER_CLEANUP'}
  elseif($result.workerTimedOut){$result.failureCode='WORKER_TIMEOUT'}
  elseif($result.workerExitCode -ne 0){$result.failureCode='WORKER_EXIT'}
  elseif(-not [IO.File]::Exists($workerResult) -or ([IO.FileInfo]::new($workerResult)).Length -gt 16384){$result.failureCode='WORKER_RESULT'}
  else{
   $child=Get-Content -LiteralPath $workerResult -Raw -Encoding UTF8 | ConvertFrom-Json -AsHashtable
   if($child.format -cne $result.format -or $child.version -cne '5.8.1' -or $child.workerScriptSha256 -cne $result.workerScriptSha256 -or $child.cabinetHelperSha256 -cne $result.cabinetHelperSha256 -or $child.ready -isnot [bool] -or $child.ready -or $child.automaticActivation -isnot [bool] -or $child.automaticActivation -or $child.vendorCodeExecuted -isnot [bool] -or $child.vendorCodeExecuted -or $child.installerExecuted -isnot [bool] -or $child.installerExecuted -or $child.msiCustomActionsExecuted -isnot [bool] -or $child.msiCustomActionsExecuted){throw 'WORKER_RESULT'}
   if($child.status -cnotin @('blocked','baseline-verified') -or $child.checks.Count -ne $script:flagNames.Count){throw 'WORKER_RESULT'}
   foreach($name in $script:flagNames){if($child.checks[$name] -isnot [bool] -or ($child.status -ceq 'baseline-verified' -and -not $child.checks[$name])){throw 'WORKER_RESULT'}}
   if($child.status -ceq 'baseline-verified'){
    if($child.failureCode -ne $null -or $child.payload.files -ne 4526 -or $child.payload.msiHashMatches -ne 4493 -or $child.payload.versionedWithoutMsiHash -ne 33 -or $child.payload.fullyCoveredBySignedMsiHashes -isnot [bool] -or $child.payload.fullyCoveredBySignedMsiHashes){throw 'WORKER_RESULT'}
    $payloadFile=[IO.Path]::Combine($work,'payload-sha256.json');$null=Assert-PlainPath $payloadFile $true
    if($child.payloadManifest.path -cne 'payload-sha256.json' -or $child.payloadManifest.bytes -gt 2000000 -or ([IO.FileInfo]::new($payloadFile)).Length -ne $child.payloadManifest.bytes -or (Get-PrivateFileHash $payloadFile) -cne $child.payloadManifest.sha256){throw 'WORKER_RESULT'}
    [IO.File]::Move($payloadFile,[IO.Path]::Combine($candidate,'payload-sha256.json'))
   }
   $result=$child;$result.workerStopped=$true;$result.jobCleanupVerified=$true;$result.workerExitCode=0
  }
 }
}catch{
 if($launchAttempted -and $null -eq $owner){
  $errorItem=$_.Exception;while($null -ne $errorItem.InnerException){$errorItem=$errorItem.InnerException}
  $cleanFailures=@('launch-arguments-invalid','job-create-failed','job-limit-failed','environment-invalid','stdio-create-failed','handle-list-failed','process-create-failed','job-assignment-failed','process-identity-failed','process-resume-failed','boundary-tool-failure')
  $safeCleanup=$errorItem -is [InvalidOperationException] -and $errorItem.Message -cin $cleanFailures
 }
 if($result.failureCode -in @('NOT_STARTED',$null)){$result.failureCode='WORKER_POLICY'}
 $result.status='blocked'
}finally{
 if($null -ne $owner -and -not $safeCleanup){try{$owner.Dispose();$safeCleanup=$owner.CleanupVerified -is [bool] -and $owner.CleanupVerified}catch{$safeCleanup=$false}}
 $result.workerStopped=$safeCleanup;$result.jobCleanupVerified=$safeCleanup
 if(-not $safeCleanup){$result.status='blocked';$result.failureCode='WORKER_CLEANUP'}
 if($work -and $safeCleanup -and [IO.Directory]::Exists($work)){Remove-Item -LiteralPath $work -Recurse -Force -ErrorAction SilentlyContinue}
}
Write-NewPrivateJson $ResultPath $result
[Console]::WriteLine('Source candidate trust: '+$result.status+'; ready=false; worker stopped='+$result.workerStopped)
