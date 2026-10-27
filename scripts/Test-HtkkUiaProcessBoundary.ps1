# Exercise the actual UIA wrapper with deterministic native-tool outcomes.
# Parsing the production function avoids running installation/startup code.
$ErrorActionPreference='Stop'
$tokens=$null;$errors=$null
$ast=[Management.Automation.Language.Parser]::ParseFile((Join-Path $PSScriptRoot 'probe-htkk-windows.ps1'),[ref]$tokens,[ref]$errors)
if(@($errors).Count){throw 'Probe syntax invalid'}
foreach($functionName in @('Read-HtkkUiaHelperPhase','Get-HtkkSafeUiDiagnostics')){
 $definition=$ast.Find({param($node) $node -is [Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -ceq $functionName},$true)
 if($null -eq $definition){throw 'UIA wrapper missing'}
 Invoke-Expression $definition.Extent.Text
}
$directory=Join-Path $env:RUNNER_TEMP ('htkk-uia-boundary-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $directory|Out-Null
$previousWindir=$env:WINDIR
if(-not $env:WINDIR){$env:WINDIR=$directory}
$script:uiaHelpersStopped=$true
$script:fixture='valid';$script:calls=0
function Invoke-HtkkBoundedNativeProcess {
 param($Executable,$WorkingDirectory,$Arguments,$TimeoutMilliseconds)
 $script:calls++
 if($TimeoutMilliseconds -ne 15000 -or $Arguments[0] -cne '-STA' -or $Arguments -cnotcontains '-NonInteractive'){throw 'UIA invocation contract changed'}
 $outputIndex=[Array]::IndexOf($Arguments,'-OutputFile')
 if($outputIndex -lt 0 -or $Arguments[$outputIndex+1] -cne (Join-Path $directory 'uia-safe.json')){throw 'UIA output path mismatch'}
 $result=[ordered]@{status='exited';timedOut=$false;processStopped=$true;exitCode=0}
 $phaseIndex=[Array]::IndexOf($Arguments,'-PhaseFile')
 if($phaseIndex -lt 0){throw 'UIA progress path missing'}
 $phaseFile=$Arguments[$phaseIndex+1]
 [IO.File]::WriteAllText($phaseFile,($(if($script:fixture -ceq 'timeout'){'root-enumerating'}else{'complete'})))
 $resultFile=$Arguments[$outputIndex+1]
 Remove-Item -LiteralPath $resultFile -Force -ErrorAction SilentlyContinue
 switch($script:fixture){
  'valid' { @{status='scanned';windows=1;controls=2;loginReady=$true;types=@{};ids=@();labels=@()}|ConvertTo-Json|Set-Content -LiteralPath $resultFile -Encoding utf8BOM }
  'provider' { @{status='uia-unavailable';windows=0;controls=0;loginReady=$false;types=@{};ids=@();labels=@()}|ConvertTo-Json|Set-Content -LiteralPath $resultFile -Encoding utf8BOM }
  'invalid' { '{invalid'|Set-Content -LiteralPath $resultFile }
  'oversized' { (' '*32769)|Set-Content -LiteralPath $resultFile }
  'missing' { }
  'timeout' { $result.status='process-timeout';$result.timedOut=$true;$result.exitCode=$null }
  'nonzero' { $result.exitCode=1 }
  'tool' { $result.status='process-tool-failure';$result.exitCode=$null }
  'cleanup' { $result.status='cleanup-not-verified';$result.processStopped=$false;$result.exitCode=$null }
  'throw' { throw 'simulated internal boundary failure' }
 }
 return $result
}
try{
 foreach($case in @(
  @('valid','none'),@('provider','uia-provider-unavailable'),@('invalid','helper-result-invalid'),@('oversized','helper-result-invalid'),@('missing','helper-result-missing'),@('timeout','helper-timeout'),@('nonzero','helper-nonzero-exit'),@('tool','helper-tool-failure'),@('cleanup','helper-cleanup-not-verified')
 )){
  $script:fixture=$case[0]
  $actual=Get-HtkkSafeUiDiagnostics -AppProcessId 123 -Descendants @() -TemporaryDirectory $directory
  if($actual.helperFailureCategory -cne $case[1]){throw "UIA failure category mismatch: $($case[0])"}
  if($case[0] -ceq 'valid' -and (-not $actual.loginReady -or $actual.helperExitCode -ne 0)){throw 'Valid bounded UIA result lost'}
  if($case[0] -ceq 'timeout' -and ($actual.status -cne 'uia-timeout' -or -not $actual.helperProcessStopped -or $actual.helperPhase -cne 'root-enumerating')){throw 'Timeout cleanup not retained'}
 }
 if($script:uiaHelpersStopped){throw 'Cleanup failure permitted credentials'}
 $script:fixture='valid';$null=Get-HtkkSafeUiDiagnostics -AppProcessId 123 -Descendants @() -TemporaryDirectory $directory
 if($script:uiaHelpersStopped){throw 'Later success overwrote unsafe cleanup'}
 $script:uiaHelpersStopped=$true;$script:fixture='throw'
 try{$null=Get-HtkkSafeUiDiagnostics -AppProcessId 123 -Descendants @() -TemporaryDirectory $directory}catch{}
 if($script:uiaHelpersStopped){throw 'Unexpected helper exception permitted credentials'}
 $phaseFile=Join-Path $directory 'uia-phase.txt'
 foreach($phase in @('not-started','starting','modules-loading','assembly-loading','initializing','root-enumerating','root-scoping','traversing','result-building','provider-failed','result-writing','complete')){
  [IO.File]::WriteAllText($phaseFile,$phase)
  if((Read-HtkkUiaHelperPhase $phaseFile) -cne $phase){throw 'Safe phase rejected'}
 }
 foreach($unsafePhase in @('test-private-title-path-message',('x'*65))){
  [IO.File]::WriteAllText($phaseFile,$unsafePhase)
  if((Read-HtkkUiaHelperPhase $phaseFile) -cne 'invalid'){throw 'Unsafe phase accepted'}
 }
 Remove-Item -LiteralPath $phaseFile
 if((Read-HtkkUiaHelperPhase $phaseFile) -cne 'unavailable'){throw 'Missing phase accepted'}
 Write-Host "Actual UIA wrapper boundary scenarios passed: $script:calls; phase whitelist checks passed: 14"
}finally{
 $env:WINDIR=$previousWindir
 Remove-Item -LiteralPath $directory -Recurse -Force -ErrorAction SilentlyContinue
}
