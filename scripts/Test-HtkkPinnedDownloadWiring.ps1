# Run the production wrapper without installation, network or credentials.
$ErrorActionPreference='Stop'
$tokens=$null;$errors=$null
$ast=[Management.Automation.Language.Parser]::ParseFile((Join-Path $PSScriptRoot 'probe-htkk-windows.ps1'),[ref]$tokens,[ref]$errors)
if(@($errors).Count){throw 'Probe syntax invalid'}
$definition=$ast.Find({param($node) $node -is [Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -ceq 'Get-PinnedFile'},$true)
if($null -eq $definition){throw 'Pinned wrapper missing'}
Invoke-Expression $definition.Extent.Text
function Invoke-HtkkPinnedDownload {
 param($Url,$Destination,$ExpectedSha256)
 return $script:downloadFixture
}
$cases=0
foreach($pair in @(@('none',''),@('dns','SOURCE_DOWNLOAD_DNS'),@('tls','SOURCE_DOWNLOAD_TLS'),@('http','SOURCE_DOWNLOAD_HTTP'),@('timeout','SOURCE_DOWNLOAD_TIMEOUT'),@('connect','SOURCE_DOWNLOAD_CONNECT'),@('tool','SOURCE_DOWNLOAD_TOOL'),@('hash','SOURCE_HASH_MISMATCH'),@('cleanup','SOURCE_DOWNLOAD_CLEANUP_NOT_VERIFIED'))){
 $script:downloadFixture=@{status='failed';failureCategory=$pair[0];partialFileRemoved=$true;attemptCount=1}
 if($pair[0] -ceq 'none'){$script:downloadFixture.status='verified'}
 if($pair[0] -ceq 'cleanup'){$script:downloadFixture.partialFileRemoved=$false}
 $report=@{sourceDownloads=@()};$reason=''
 try{Get-PinnedFile -Url 'https://example.invalid/not-fetched' -Path 'not-written' -Expected ('a'*64)}catch{$reason=$_.Exception.Message}
 if($reason -cne $pair[1]){throw 'Pinned download wrapper classification mismatch'}
 if($report.sourceDownloads.Count -ne 1 -or -not [object]::ReferenceEquals($report.sourceDownloads[0],$script:downloadFixture)){throw 'Actual download attempts not retained'}
 $cases++
}
Write-Host "Actual pinned download wrapper scenarios passed: $cases"
