# Classify only typed failures. Exception messages, URLs and response bodies are never output.
function Get-HtkkDownloadFailure {
 [CmdletBinding()]
 param([Parameter(Mandatory=$true)][Exception]$Exception)
 $chain=[Collections.Generic.List[Exception]]::new();$current=$Exception
 for($depth=0;$null -ne $current -and $depth -lt 8;$depth++){$chain.Add($current);$current=$current.InnerException}
 $safe=[ordered]@{category='tool';httpStatus=$null;retryable=$false}
 # A TLS failure is never made retryable by an outer HTTP/socket exception.
 foreach($errorItem in $chain){
  if(($errorItem -is [Net.Http.HttpRequestException] -and $errorItem.HttpRequestError -eq [Net.Http.HttpRequestError]::SecureConnectionError) -or $errorItem -is [Security.Authentication.AuthenticationException] -or ($errorItem -is [Net.WebException] -and $errorItem.Status -in @([Net.WebExceptionStatus]::TrustFailure,[Net.WebExceptionStatus]::SecureChannelFailure))){$safe.category='tls';return $safe}
 }
 foreach($errorItem in $chain){
  $status=$null
  if($errorItem -is [Microsoft.PowerShell.Commands.HttpResponseException] -and $null -ne $errorItem.Response){$status=[int]$errorItem.Response.StatusCode}
  elseif($errorItem -is [Net.Http.HttpRequestException] -and $null -ne $errorItem.StatusCode){$status=[int]$errorItem.StatusCode}
  elseif($errorItem -is [Net.WebException] -and $errorItem.Response -is [Net.HttpWebResponse]){$status=[int]$errorItem.Response.StatusCode}
  if($null -ne $status -and $status -ge 100 -and $status -le 599){$safe.category='http';$safe.httpStatus=$status;$safe.retryable=$status -in @(408,429,500,502,503,504);return $safe}
 }
 foreach($errorItem in $chain){
  if($errorItem -is [Net.Sockets.SocketException]){
   switch($errorItem.SocketErrorCode){
    'TryAgain' {$safe.category='dns';$safe.retryable=$true;return $safe}
    {$_ -in @('HostNotFound','NoData','NoRecovery')} {$safe.category='dns';return $safe}
    'TimedOut' {$safe.category='timeout';$safe.retryable=$true;return $safe}
    {$_ -in @('ConnectionReset','ConnectionAborted','NetworkReset')} {$safe.category='connect';$safe.retryable=$true;return $safe}
    {$_ -in @('ConnectionRefused','NetworkUnreachable','HostUnreachable','AddressNotAvailable','NotConnected')} {$safe.category='connect';return $safe}
   }
  }
  if($errorItem -is [Net.WebException]){
   switch($errorItem.Status){
    'Timeout' {$safe.category='timeout';$safe.retryable=$true;return $safe}
    {$_ -in @('NameResolutionFailure','ProxyNameResolutionFailure')} {$safe.category='dns';return $safe}
    'ConnectFailure' {$safe.category='connect';return $safe}
    {$_ -in @('ConnectionClosed','ReceiveFailure','SendFailure','KeepAliveFailure')} {$safe.category='connect';$safe.retryable=$true;return $safe}
   }
  }
  if($errorItem -is [Net.Http.HttpRequestException]){
   if($errorItem.HttpRequestError -eq [Net.Http.HttpRequestError]::NameResolutionError){$safe.category='dns';return $safe}
   if($errorItem.HttpRequestError -in @([Net.Http.HttpRequestError]::ConnectionError,[Net.Http.HttpRequestError]::ProxyTunnelError)){$safe.category='connect';return $safe}
  }
  if($errorItem -is [TimeoutException]){$safe.category='timeout';$safe.retryable=$true;return $safe}
 }
 # Cancellation without a typed timeout may be deliberate; do not retry it.
 return $safe
}

function Invoke-HtkkPinnedDownload {
 [CmdletBinding()]
 param(
  [Parameter(Mandatory=$true)][string]$Url,
  [Parameter(Mandatory=$true)][string]$Destination,
  [Parameter(Mandatory=$true)][string]$ExpectedSha256,
  [scriptblock]$Downloader={param($Source,$Target,$TimeoutSeconds)
   Invoke-WebRequest -Uri $Source -OutFile $Target -TimeoutSec $TimeoutSeconds -MaximumRedirection 8 -MaximumRetryCount 0 -UserAgent 'HotroKeKhai-ReadinessProbe/1.0'
  }
 )
 $ErrorActionPreference='Stop';$ProgressPreference='SilentlyContinue'
 $safe=[ordered]@{format='htkk-pinned-download-status-v1';status='failed';failureCategory='tool';httpStatus=$null;attemptCount=0;attempts=@();hashVerified=$false;partialFileRemoved=$true;timeoutSeconds=120;maximumAttempts=2}
 $uri=$null
 if(-not [Uri]::TryCreate($Url,[UriKind]::Absolute,[ref]$uri) -or $uri.Scheme -cne 'https' -or $uri.UserInfo -or $uri.Fragment -or $ExpectedSha256 -cnotmatch '^[0-9a-f]{64}$'){return $safe}
 # A destination is owned by this invocation only if it did not preexist.
 try{if(Test-Path -LiteralPath $Destination){return $safe}}catch{return $safe}
 for($attempt=1;$attempt -le 2;$attempt++){
  $failure=$null
  try{
   $null=& $Downloader $Url $Destination 120
   $file=Get-Item -LiteralPath $Destination
   if($file -isnot [IO.FileInfo] -or ($file.Attributes -band [IO.FileAttributes]::ReparsePoint)){throw [IO.IOException]::new('DOWNLOAD_OUTPUT_NOT_A_FILE')}
   if((Get-FileHash -LiteralPath $Destination -Algorithm SHA256).Hash.ToLowerInvariant() -cne $ExpectedSha256){$failure=[ordered]@{category='hash';httpStatus=$null;retryable=$false}}
  }catch{$failure=Get-HtkkDownloadFailure -Exception $_.Exception}
  $safe.attemptCount=$attempt
  if($null -eq $failure){
   $safe.attempts+=@([ordered]@{attempt=$attempt;category='none';httpStatus=$null;retryable=$false})
   $safe.status='verified';$safe.failureCategory='none';$safe.hashVerified=$true;return $safe
  }
  $safe.attempts+=@([ordered]@{attempt=$attempt;category=$failure.category;httpStatus=$failure.httpStatus;retryable=[bool]$failure.retryable})
  $safe.failureCategory=$failure.category;$safe.httpStatus=$failure.httpStatus
  try{if(Test-Path -LiteralPath $Destination){Remove-Item -LiteralPath $Destination -Force};$safe.partialFileRemoved=-not(Test-Path -LiteralPath $Destination)}catch{$safe.partialFileRemoved=$false}
  if(-not $safe.partialFileRemoved -or -not $failure.retryable -or $attempt -eq 2){return $safe}
 }
 return $safe
}
