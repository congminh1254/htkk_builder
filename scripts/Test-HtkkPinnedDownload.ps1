# Deterministic typed exceptions/downloaders only; no external network or source execution.
$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'Test-HtkkPinnedDownloadColdProcess.ps1')
. (Join-Path $PSScriptRoot 'Invoke-HtkkPinnedDownload.ps1')
$script:checks=0
$secret='test-only-private-message-never-emit'
function Assert-Classification([Exception]$errorItem,[string]$category,[bool]$retry,$httpStatus=$null){
 $observed=Get-HtkkDownloadFailure -Exception $errorItem
 if($observed.category -cne $category -or $observed.retryable -ne $retry -or $observed.httpStatus -ne $httpStatus){throw 'Typed download classification mismatch'}
 if(($observed|ConvertTo-Json -Compress).Contains($secret)){throw 'Exception content exposed'};$script:checks++
}
Assert-Classification ([TimeoutException]::new($secret)) 'timeout' $true
Assert-Classification ([Security.Authentication.AuthenticationException]::new($secret)) 'tls' $false
Assert-Classification ([Net.WebException]::new($secret,[Net.WebExceptionStatus]::TrustFailure)) 'tls' $false
Assert-Classification ([Net.WebException]::new($secret,[Net.WebExceptionStatus]::NameResolutionFailure)) 'dns' $false
Assert-Classification ([Net.WebException]::new($secret,[Net.WebExceptionStatus]::Timeout)) 'timeout' $true
Assert-Classification ([Net.WebException]::new($secret,[Net.WebExceptionStatus]::ConnectFailure)) 'connect' $false
Assert-Classification ([Net.WebException]::new($secret,[Net.WebExceptionStatus]::ReceiveFailure)) 'connect' $true
Assert-Classification ([OperationCanceledException]::new($secret)) 'tool' $false
Assert-Classification ([Exception]::new($secret)) 'tool' $false
foreach($case in @(@('TryAgain','dns',$true),@('HostNotFound','dns',$false),@('ConnectionReset','connect',$true),@('ConnectionRefused','connect',$false),@('TimedOut','timeout',$true))){
 $socketCode=[Net.Sockets.SocketError]::$($case[0])
 Assert-Classification ([Net.Sockets.SocketException]::new([int]$socketCode)) $case[1] $case[2]
}
foreach($status in @(401,403,404,408,429,500,501,502,503,504)){
 $errorItem=[Net.Http.HttpRequestException]::new($secret,$null,[Net.HttpStatusCode]$status)
 Assert-Classification $errorItem 'http' ($status -in @(408,429,500,502,503,504)) $status
}
$response=[Net.Http.HttpResponseMessage]::new([Net.HttpStatusCode]::Forbidden)
try{Assert-Classification ([Microsoft.PowerShell.Commands.HttpResponseException]::new($secret,$response)) 'http' $false 403}finally{$response.Dispose()}
Assert-Classification ([Net.Http.HttpRequestException]::new($secret,[Security.Authentication.AuthenticationException]::new($secret))) 'tls' $false
Assert-Classification ([Reflection.TargetInvocationException]::new([TimeoutException]::new($secret))) 'timeout' $true
Assert-Classification ([Net.Http.HttpRequestException]::new([Net.Http.HttpRequestError]::SecureConnectionError,$secret,$null,$null)) 'tls' $false
Assert-Classification ([Net.Http.HttpRequestException]::new([Net.Http.HttpRequestError]::NameResolutionError,$secret,$null,$null)) 'dns' $false
$directory=Join-Path $env:RUNNER_TEMP ('htkk-download-tests-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $directory|Out-Null
$target=Join-Path $directory 'download.bin'
$payload=[Text.Encoding]::UTF8.GetBytes('verified-public-test-source')
$expected=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($payload)).ToLowerInvariant()
$script:attempt=0
$downloader={param($source,$destination,$timeout)
 $script:attempt++
 if($timeout -ne 120){throw 'Unexpected download timeout'}
 [IO.File]::WriteAllBytes($destination,$payload)
 if($script:behavior -ceq 'recover' -and $script:attempt -eq 1){throw [TimeoutException]::new($secret)}
 if($script:behavior -ceq 'timeout'){throw [TimeoutException]::new($secret)}
 if($script:behavior -ceq 'tls'){throw [Security.Authentication.AuthenticationException]::new($secret)}
 if($script:behavior -ceq 'http-recover' -and $script:attempt -eq 1){throw [Net.Http.HttpRequestException]::new($secret,$null,[Net.HttpStatusCode]::ServiceUnavailable)}
 if($script:behavior -ceq 'auth'){throw [Net.Http.HttpRequestException]::new($secret,$null,[Net.HttpStatusCode]::Forbidden)}
 if($script:behavior -ceq 'hash'){[IO.File]::WriteAllText($destination,'incorrect')}
}
try{
 foreach($case in @(@('normal',1,'verified','none'),@('recover',2,'verified','none'),@('http-recover',2,'verified','none'),@('timeout',2,'failed','timeout'),@('tls',1,'failed','tls'),@('auth',1,'failed','http'),@('hash',1,'failed','hash'))){
  Remove-Item -LiteralPath $target -Force -ErrorAction SilentlyContinue
  $script:attempt=0;$script:behavior=$case[0]
  $actual=Invoke-HtkkPinnedDownload -Url 'https://example.com/public-test' -Destination $target -ExpectedSha256 $expected -Downloader $downloader
  if($script:attempt -ne $case[1] -or $actual.attemptCount -ne $case[1] -or $actual.status -cne $case[2] -or $actual.failureCategory -cne $case[3] -or $actual.attempts.Count -ne $case[1]){throw "Download attempt behavior mismatch: $($case[0])"}
  if($actual.status -ceq 'failed' -and ((Test-Path -LiteralPath $target) -or -not $actual.partialFileRemoved)){throw 'Partial download not removed'}
  if($actual.status -ceq 'verified' -and (-not $actual.hashVerified -or (Get-FileHash -LiteralPath $target).Hash.ToLowerInvariant() -cne $expected)){throw 'Verified hash not established'}
  $serialized=$actual|ConvertTo-Json -Depth 5 -Compress
  foreach($private in @($secret,'https://example.com',$directory,'incorrect')){if($serialized.Contains($private)){throw 'Private download context exposed'}}
  $script:checks++
 }
 # A caller-owned existing file must survive and must not trigger a request.
 [IO.File]::WriteAllText($target,'caller-owned');$script:attempt=0
 $actual=Invoke-HtkkPinnedDownload -Url 'https://example.com/public-test' -Destination $target -ExpectedSha256 $expected -Downloader $downloader
 if($actual.attemptCount -ne 0 -or $script:attempt -ne 0 -or [IO.File]::ReadAllText($target) -cne 'caller-owned'){throw 'Preexisting file overwritten'};$script:checks++
 Write-Host "Pinned download typed classification/attempt/cleanup checks passed: $script:checks"
}finally{Remove-Item -LiteralPath $directory -Recurse -Force -ErrorAction SilentlyContinue}

& (Join-Path $PSScriptRoot 'Test-HtkkPinnedDownloadWiring.ps1')
