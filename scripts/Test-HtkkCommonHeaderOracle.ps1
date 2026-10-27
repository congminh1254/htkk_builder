# Original metadata binding + common-header serializer only. Never a GUI export/import oracle.
function Invoke-HtkkCommonHeaderOracle {
 [CmdletBinding()]
 param([Parameter(Mandatory=$true)][string]$ProjectDirectory,[Parameter(Mandatory=$true)][string]$TemporaryDirectory)
 $ErrorActionPreference='Stop'
  . (Join-Path $PSScriptRoot 'Invoke-HtkkBoundedJobProcess.ps1')
  . (Join-Path $PSScriptRoot 'Invoke-HtkkBoundedCompiler.ps1')
 $safe=[ordered]@{status='not-run';runtime='unknown';stage='not-started';cases=0;matched=0;failedCaseIndices=@();getToKhaiInfoInvocations=0;bindInvocations=0;serializeInvocations=0;compilerExitCode=$null;compilerErrorCodes=@();compilerJobCleanupVerified=$true;oracleExitCode=$null; oracleJobCleanupVerified=$true;sourceHashesVerified=$false;sourceHashesUnchanged=$false;privateSyntheticXmlSaved=$false;fullRoundTrip=$false;guiExportInvoked=$false;userDataUsed=$false}
 $directory=$null;$firewallName=$null
 try {
  $privateDirectory=Join-Path $env:RUNNER_TEMP 'htkk-common-header-diagnostic'
  foreach($name in @('common-header-first.xml','common-header-supplement.xml')){Remove-Item -LiteralPath (Join-Path $privateDirectory $name) -Force -ErrorAction SilentlyContinue}
  $root=Split-Path $ProjectDirectory
  $pins=[ordered]@{
   'Project/HTKK.exe'='411141d2e728a45f4a35a876afb169d0ac2450de2499e8a1f43ac29ab6401938'
   'Project/TAX.HTKK.Utilities.dll'='ccc35605a4d3bb235f896d6ab43cec4c6543a404159cf10897a57cba23d817ec'
   'Project/HTKK.exe.config'='b3547d6a6a61fd6e8e8b64c8976e8702aa94a2b5a44a1cf394c5486162297047'
   'Project/Menu.xml'='4ac42eae600f4c98ed3df8a17b6d18770904acff5267913fdc9f98be4a9f24b4'
   'InterfaceTemplates/xml/01_GTGT_TT80_xml_283.xml'='7ba334067c52ea22cd744dcf2c0ff444190d6661f6b3e9b3ea08e5ead574830c'
  }
  foreach($path in $pins.Keys){if((Get-FileHash -LiteralPath (Join-Path $root $path) -Algorithm SHA256).Hash.ToLowerInvariant() -ne $pins[$path]){$safe.status='source-hash-mismatch';return $safe}}
  $safe.sourceHashesVerified=$true
  $compiler=Join-Path $env:WINDIR 'Microsoft.NET/Framework/v2.0.50727/csc.exe'
  if(-not(Test-Path -LiteralPath $compiler -PathType Leaf)){$safe.status='clr2-compiler-unavailable';return $safe}
  $directory=Join-Path $TemporaryDirectory ('common-header-oracle-'+[guid]::NewGuid().ToString('N'));New-Item -ItemType Directory -Path $directory|Out-Null
  $program=Join-Path $directory 'CommonHeaderOracle.exe';$resultFile=Join-Path $directory 'result.json';$source=Join-Path $PSScriptRoot 'HtkkCommonHeaderOracle.cs'
  $configuration=[xml](Get-Content -LiteralPath (Join-Path $ProjectDirectory 'HTKK.exe.config') -Raw)
  foreach($setting in @{DataFiles=(Join-Path $directory 'DATAFILES');ENABLE_LOGGING='0';APP_PREFIX='HTKK-COMMON-HEADER-ORACLE'}.GetEnumerator()){
   $existing=@($configuration.configuration.appSettings.add|Where-Object{$_.key -eq $setting.Key})
   if($existing.Count){$existing|ForEach-Object{$_.SetAttribute('value',$setting.Value)}}else{$node=$configuration.CreateElement('add');$node.SetAttribute('key',$setting.Key);$node.SetAttribute('value',$setting.Value);$configuration.configuration.appSettings.AppendChild($node)|Out-Null}
  }
  New-Item -ItemType Directory -Path (Join-Path $directory 'DATAFILES')|Out-Null;$configuration.Save($program+'.config')
  $safe.compilerJobCleanupVerified=$false
  $compilerRun=Invoke-HtkkBoundedCompiler -Executable $compiler -WorkingDirectory $directory -Arguments @('/nologo','/target:exe','/platform:x86','/optimize+',('/out:'+$program),$source) -TimeoutMilliseconds 30000
  $safe.compilerJobCleanupVerified=$compilerRun.jobCleanupVerified;$safe.compilerExitCode=$compilerRun.exitCode;$safe.compilerErrorCodes=$compilerRun.compilerErrorCodes
  if(-not $compilerRun.jobCleanupVerified -or $compilerRun.status -notin @('exited','process-timeout')){$safe.status='host-or-tool-failure';return $safe}
  if($compilerRun.timedOut){$safe.status='compile-timeout';return $safe}
  if(-not $compilerRun.diagnosticsVerified){$safe.status='host-or-tool-failure';return $safe}
  if($safe.compilerExitCode -ne 0 -or -not(Test-Path -LiteralPath $program -PathType Leaf)){$safe.status='compile-failed';return $safe}
  $firewallName='HTKK common header oracle '+[guid]::NewGuid().ToString('N');New-NetFirewallRule -DisplayName $firewallName -Direction Outbound -Program $program -Action Block|Out-Null
  $safe.oracleJobCleanupVerified=$false
  $oracleRun=Invoke-HtkkBoundedJobProcess -Executable $program -WorkingDirectory $directory -Arguments @($ProjectDirectory,(Join-Path $ProjectDirectory 'Menu.xml'),(Join-Path $root 'InterfaceTemplates/xml/01_GTGT_TT80_xml_283.xml'),$directory,$resultFile) -TimeoutMilliseconds 30000
  $safe.oracleJobCleanupVerified=$oracleRun.jobCleanupVerified;$safe.oracleExitCode=$oracleRun.exitCode
  if(-not $oracleRun.jobCleanupVerified -or $oracleRun.status -notin @('exited','process-timeout')){$safe.status='host-or-tool-failure';return $safe}
  if($oracleRun.timedOut){$safe.status='oracle-timeout';return $safe}
  foreach($path in $pins.Keys){if((Get-FileHash -LiteralPath (Join-Path $root $path) -Algorithm SHA256).Hash.ToLowerInvariant() -ne $pins[$path]){$safe.status='source-changed';return $safe}};$safe.sourceHashesUnchanged=$true
  if(-not(Test-Path -LiteralPath $resultFile -PathType Leaf) -or (Get-Item -LiteralPath $resultFile).Length -gt 4096){$safe.status='oracle-result-unavailable';return $safe}
  $r=Get-Content -LiteralPath $resultFile -Raw|ConvertFrom-Json -AsHashtable
  $statuses=@('matched','mismatch','runtime-blocked','reflection-or-runtime-blocked');$stages=@('start','assembly-types','synthetic-profile','period','get-declaration','bind','serialize','save-synthetic','d1-overwrites-existing-metadata','version-fallback','complete')
  if($r.format -ne 'htkk-common-header-oracle-v1' -or $r.status -notin $statuses -or $r.stage -notin $stages -or $r.runtime -notin @('clr2','unsupported','unknown') -or $r.cases -notin 0..43 -or $r.matched -notin 0..43 -or $r.matched -gt $r.cases -or $r.getToKhaiInfoInvocations -notin 0..2 -or $r.bindInvocations -notin 0..2 -or $r.serializeInvocations -notin 0..5){$safe.status='oracle-result-invalid';return $safe}
  if($r.failedChecks -isnot [array] -or $r.failedChecks.Count -ne ($r.cases-$r.matched) -or @($r.failedChecks|Where-Object{($_ -isnot [long] -and $_ -isnot [int]) -or $_ -notin 1..43}).Count -or @($r.failedChecks|Select-Object -Unique).Count -ne $r.failedChecks.Count){$safe.status='oracle-result-invalid';return $safe}
  $safe.failedCaseIndices=$r.failedChecks
  foreach($key in @('runtime','stage','cases','matched','getToKhaiInfoInvocations','bindInvocations','serializeInvocations')){$safe[$key]=$r[$key]}
  $safe.status=if($safe.oracleExitCode -eq 0 -and $r.status -eq 'matched' -and $r.cases -eq 43 -and $r.matched -eq 43 -and $r.getToKhaiInfoInvocations -eq 2 -and $r.bindInvocations -eq 2 -and $r.serializeInvocations -eq 5){'matched'}elseif($r.status -eq 'mismatch'){'mismatch'}else{'oracle-runtime-blocked'}
  if($safe.status -eq 'matched'){
   New-Item -ItemType Directory -Path $privateDirectory -Force|Out-Null
   foreach($name in @('common-header-first.xml','common-header-supplement.xml')){
    $file=Join-Path $directory $name;if(-not(Test-Path -LiteralPath $file -PathType Leaf) -or (Get-Item -LiteralPath $file).Length -gt 65536){$safe.status='synthetic-output-unavailable';return $safe}
    Copy-Item -LiteralPath $file -Destination (Join-Path $privateDirectory $name)
   }
   $safe.privateSyntheticXmlSaved=$true
  }
  return $safe
 }catch{$safe.status='host-or-tool-failure';return $safe}
 finally{
  if($firewallName){Remove-NetFirewallRule -DisplayName $firewallName -ErrorAction SilentlyContinue}
  if($directory){Remove-Item -LiteralPath $directory -Recurse -Force -ErrorAction SilentlyContinue}
 }
}
