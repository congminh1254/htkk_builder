# Original metadata binding + common-header serializer only. Never a GUI export/import oracle.
function Invoke-HtkkCommonHeaderOracle {
 [CmdletBinding()]
 param([Parameter(Mandatory=$true)][string]$ProjectDirectory,[Parameter(Mandatory=$true)][string]$TemporaryDirectory)
 $ErrorActionPreference='Stop'
 $safe=[ordered]@{status='not-run';runtime='unknown';stage='not-started';cases=0;matched=0;failedCaseIndices=@();getToKhaiInfoInvocations=0;bindInvocations=0;serializeInvocations=0;compilerExitCode=$null;compilerErrorCodes=@();oracleExitCode=$null;sourceHashesVerified=$false;sourceHashesUnchanged=$false;privateSyntheticXmlSaved=$false;fullRoundTrip=$false;guiExportInvoked=$false;userDataUsed=$false}
 $directory=$null;$compilerProcess=$null;$oracleProcess=$null;$firewallName=$null
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
  $compilerInfo=[Diagnostics.ProcessStartInfo]::new();$compilerInfo.FileName=$compiler;$compilerInfo.WorkingDirectory=$directory;$compilerInfo.UseShellExecute=$false;$compilerInfo.CreateNoWindow=$true;$compilerInfo.RedirectStandardOutput=$true;$compilerInfo.RedirectStandardError=$true;$compilerInfo.Environment.Clear()
  foreach($key in @('SystemRoot','WINDIR','TEMP','TMP','PATH')){$v=[Environment]::GetEnvironmentVariable($key);if($null -ne $v){$compilerInfo.Environment[$key]=$v}}
  foreach($argument in @('/nologo','/target:exe','/platform:x86','/optimize+',('/out:'+$program),$source)){$compilerInfo.ArgumentList.Add($argument)}
  $compilerProcess=[Diagnostics.Process]::Start($compilerInfo);$compilerOut=$compilerProcess.StandardOutput.ReadToEndAsync();$compilerErr=$compilerProcess.StandardError.ReadToEndAsync()
  if(-not $compilerProcess.WaitForExit(30000)){$compilerProcess.Kill($true);$safe.status='compile-timeout';return $safe}
  $safe.compilerExitCode=$compilerProcess.ExitCode;$compilerText=$compilerOut.GetAwaiter().GetResult()+$compilerErr.GetAwaiter().GetResult();$safe.compilerErrorCodes=@([regex]::Matches($compilerText,'\bCS[0-9]{4}\b')|ForEach-Object{$_.Value}|Sort-Object -Unique|Select-Object -First 10)
  if($compilerProcess.ExitCode -ne 0 -or -not(Test-Path -LiteralPath $program -PathType Leaf)){$safe.status='compile-failed';return $safe}
  $firewallName='HTKK common header oracle '+[guid]::NewGuid().ToString('N');New-NetFirewallRule -DisplayName $firewallName -Direction Outbound -Program $program -Action Block|Out-Null
  $info=[Diagnostics.ProcessStartInfo]::new();$info.FileName=$program;$info.WorkingDirectory=$directory;$info.UseShellExecute=$false;$info.CreateNoWindow=$true;$info.RedirectStandardOutput=$true;$info.RedirectStandardError=$true;$info.Environment.Clear()
  foreach($key in @('SystemRoot','WINDIR','TEMP','TMP','PATH')){$v=[Environment]::GetEnvironmentVariable($key);if($null -ne $v){$info.Environment[$key]=$v}}
  foreach($argument in @($ProjectDirectory,(Join-Path $ProjectDirectory 'Menu.xml'),(Join-Path $root 'InterfaceTemplates/xml/01_GTGT_TT80_xml_283.xml'),$directory,$resultFile)){$info.ArgumentList.Add($argument)}
  $oracleProcess=[Diagnostics.Process]::Start($info);$oracleOut=$oracleProcess.StandardOutput.ReadToEndAsync();$oracleErr=$oracleProcess.StandardError.ReadToEndAsync()
  if(-not $oracleProcess.WaitForExit(30000)){$oracleProcess.Kill($true);$safe.status='oracle-timeout';return $safe};$safe.oracleExitCode=$oracleProcess.ExitCode
  foreach($path in $pins.Keys){if((Get-FileHash -LiteralPath (Join-Path $root $path) -Algorithm SHA256).Hash.ToLowerInvariant() -ne $pins[$path]){$safe.status='source-changed';return $safe}};$safe.sourceHashesUnchanged=$true
  if(-not(Test-Path -LiteralPath $resultFile -PathType Leaf) -or (Get-Item -LiteralPath $resultFile).Length -gt 4096){$safe.status='oracle-result-unavailable';return $safe}
  $r=Get-Content -LiteralPath $resultFile -Raw|ConvertFrom-Json -AsHashtable
  $statuses=@('matched','mismatch','runtime-blocked','reflection-or-runtime-blocked');$stages=@('start','assembly-types','synthetic-profile','period','get-declaration','bind','serialize','save-synthetic','d1-overwrites-existing-metadata','version-fallback','complete')
  if($r.format -ne 'htkk-common-header-oracle-v1' -or $r.status -notin $statuses -or $r.stage -notin $stages -or $r.runtime -notin @('clr2','unsupported','unknown') -or $r.cases -notin 0..43 -or $r.matched -notin 0..43 -or $r.matched -gt $r.cases -or $r.getToKhaiInfoInvocations -notin 0..2 -or $r.bindInvocations -notin 0..2 -or $r.serializeInvocations -notin 0..5){$safe.status='oracle-result-invalid';return $safe}
  if($r.failedChecks -isnot [array] -or $r.failedChecks.Count -ne ($r.cases-$r.matched) -or @($r.failedChecks|Where-Object{($_ -isnot [long] -and $_ -isnot [int]) -or $_ -notin 1..43}).Count -or @($r.failedChecks|Select-Object -Unique).Count -ne $r.failedChecks.Count){$safe.status='oracle-result-invalid';return $safe}
  $safe.failedCaseIndices=$r.failedChecks
  foreach($key in @('runtime','stage','cases','matched','getToKhaiInfoInvocations','bindInvocations','serializeInvocations')){$safe[$key]=$r[$key]}
  $safe.status=if($oracleProcess.ExitCode -eq 0 -and $r.status -eq 'matched' -and $r.cases -eq 43 -and $r.matched -eq 43 -and $r.getToKhaiInfoInvocations -eq 2 -and $r.bindInvocations -eq 2 -and $r.serializeInvocations -eq 5){'matched'}elseif($r.status -eq 'mismatch'){'mismatch'}else{'oracle-runtime-blocked'}
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
  if($null -ne $oracleProcess){if(-not $oracleProcess.HasExited){$oracleProcess.Kill($true)};$oracleProcess.Dispose()}
  if($null -ne $compilerProcess){if(-not $compilerProcess.HasExited){$compilerProcess.Kill($true)};$compilerProcess.Dispose()}
  if($firewallName){Remove-NetFirewallRule -DisplayName $firewallName -ErrorAction SilentlyContinue}
  if($directory){Remove-Item -LiteralPath $directory -Recurse -Force -ErrorAction SilentlyContinue}
 }
}
