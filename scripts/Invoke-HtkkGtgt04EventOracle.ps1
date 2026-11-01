[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$ProjectDirectory)
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'Invoke-HtkkBoundedCompiler.ps1')
. (Join-Path $PSScriptRoot 'HtkkNativeCompileInputs.ps1')
. (Join-Path $PSScriptRoot 'Invoke-HtkkSyntheticLogin.ps1')
if(-not ('HtkkWindowsJobProcess' -as [type])){Add-Type -Path (Join-Path $PSScriptRoot 'HtkkWindowsJobProcess.cs')}
$project=[IO.Path]::GetFullPath($ProjectDirectory)
$fixture=Join-Path (Join-Path (Split-Path $project) 'DataFiles') '9999999997'
if(Test-Path -LiteralPath $fixture){throw 'GTGT04_FRESH_PROFILE_REQUIRED'}
$pins=@{'TAX.HTKK.Utilities.dll'='ccc35605a4d3bb235f896d6ab43cec4c6543a404159cf10897a57cba23d817ec';'FarPoint.CalcEngine.dll'='19183e5a0ad1d74bed1fc151178a8a118ae6544cddb7e3aabc64940f45900d5a';'FarPoint.Win.dll'='fae1320c67dbbfb97fafc0fb8716e4743a4728b4c0d7155e270d684568ef4d2a';'HTKK.exe'='411141d2e728a45f4a35a876afb169d0ac2450de2499e8a1f43ac29ab6401938';'HTKK.exe.config'='b3547d6a6a61fd6e8e8b64c8976e8702aa94a2b5a44a1cf394c5486162297047';'TAX.HTKK.Business.dll'='281689aaa7df4db33d0debcfc61d32c0c318bb871d4a19a0277d871a7c04bba7';'FarPoint.Win.Spread.dll'='2e7a0d4fc1ef6f219dd3a237ae6b26549ad03541d58da6f45d638309d2fa4c50'}
$work=Join-Path $env:RUNNER_TEMP ('htkk-gtgt04-event-'+[guid]::NewGuid().ToString('N'))
$hostPath=Join-Path $project ('HTKK.Gtgt04EventHost.'+[guid]::NewGuid().ToString('N')+'.exe')
$created=@($hostPath,($hostPath+'.config'),($hostPath+'.gui-automation.json'),($hostPath+'.gui-automation.allow'),($hostPath+'.event.json'),($hostPath+'.startup.json'))
foreach($path in $created){if(Test-Path -LiteralPath $path){throw 'GTGT04_OWNED_PATH_PREEXISTS'}}
$owner=$null;$rules=@();$login=$null;$raw=$null;$failure='none';$compilerSafe=$false;$clean=$false;$sourceSafe=$false;$startup=@{stage='not-observed';category='none'}
try{
 foreach($name in $pins.Keys){if((Get-FileHash -LiteralPath (Join-Path $project $name) -Algorithm SHA256).Hash.ToLowerInvariant() -cne $pins[$name]){throw 'GTGT04_SOURCE_PIN'}}
 New-Item -ItemType Directory -Path $work|Out-Null
 $compiler=Join-Path $env:WINDIR 'Microsoft.NET/Framework/v2.0.50727/csc.exe'
 $sig=Get-AuthenticodeSignature -LiteralPath $compiler;if($sig.Status -ne 'Valid' -or $null -eq $sig.SignerCertificate -or $sig.SignerCertificate.Subject -notmatch 'Microsoft'){throw 'GTGT04_COMPILER_TRUST'}
 $sources=@();foreach($name in (@('HtkkGtgt04EventHost.cs','HtkkGtgt04EventObserver.cs')+@(Get-HtkkNativeCompileInputs -Mode 'profile-save'))){
  if($name -cnotmatch '\AHtkk[A-Za-z0-9]+\.cs\z'){throw 'GTGT04_COMPILE_CONTRACT'}
  $inputPath=Join-Path $PSScriptRoot $name;$f=Get-Item -LiteralPath $inputPath;if($f.PSIsContainer -or ($f.Attributes -band [IO.FileAttributes]::ReparsePoint) -or $f.Length -gt 524288){throw 'GTGT04_COMPILE_SOURCE'}
  $copy=Join-Path $work $name;[IO.File]::WriteAllText($copy,[IO.File]::ReadAllText($inputPath,[Text.Encoding]::UTF8),[Text.UTF8Encoding]::new($true));$sources+=$copy
 }
 $c=Invoke-HtkkBoundedCompiler -Executable $compiler -WorkingDirectory $work -Arguments (@('/nologo','/target:winexe','/platform:x86','/optimize+',('/out:'+$hostPath),'/reference:System.Windows.Forms.dll')+$sources) -TimeoutMilliseconds 30000
 $compilerSafe=$c.jobCleanupVerified -and $c.processStopped
 if($c.status -cne 'exited' -or $c.exitCode -ne 0 -or $c.timedOut -or -not $compilerSafe -or -not $c.diagnosticsVerified){$codes=@($c.compilerErrorCodes);throw ('GTGT04_COMPILER_'+($codes -join '_'))}
 [IO.File]::WriteAllText(($hostPath+'.config'),'<?xml version="1.0"?><configuration><startup><supportedRuntime version="v2.0.50727"/></startup></configuration>',[Text.Encoding]::ASCII)
 foreach($exe in @($hostPath,(Join-Path $project 'HTKK.exe'))){$rule='HTKK04 event '+[guid]::NewGuid().ToString('N');New-NetFirewallRule -DisplayName $rule -Direction Outbound -Program $exe -Action Block|Out-Null;$rules+=$rule}
 $owner=[HtkkWindowsJobProcess]::Launch($hostPath,$project,[string[]]@(),$false,$true)
 $process=$owner.RootProcess;$started=$process.StartTime
 if(-not $process.WaitForInputIdle(30000)){throw 'GTGT04_STARTUP_BOUNDARY'}
 $startupClock=[Diagnostics.Stopwatch]::StartNew();do{$process.Refresh();if($process.HasExited){throw 'GTGT04_HOST_EXITED'};if($process.MainWindowHandle -ne [IntPtr]::Zero){break};Start-Sleep -Milliseconds 200}while($startupClock.Elapsed.TotalSeconds -lt 30)
 if($process.MainWindowHandle -eq [IntPtr]::Zero){throw 'GTGT04_STARTUP_BOUNDARY'}
 $login=Invoke-HtkkSyntheticLogin -RootProcessId $process.Id -RootStartTime $started -ProjectDirectory $project
 if($login.status -cne 'synthetic-profile-window-observed'){throw 'GTGT04_LOGIN_BOUNDARY'}
 [IO.File]::WriteAllText(($hostPath+'.gui-automation.allow'),'profile-save',[Text.Encoding]::ASCII)
 $clock=[Diagnostics.Stopwatch]::StartNew()
 do{
  $path=$hostPath+'.event.json'
  if(Test-Path -LiteralPath $path -PathType Leaf){$file=Get-Item -LiteralPath $path;if($file.Length -gt 65536){throw 'GTGT04_RESULT_SIZE'};try{$next=Get-Content -LiteralPath $path -Raw -Encoding UTF8|ConvertFrom-Json -AsHashtable -DateKind String}catch{$next=$null};if($null -ne $next -and $next.stage -in @('observed','blocked')){$raw=$next;break}}
  if($process.HasExited){throw 'GTGT04_HOST_EXITED'}
  Start-Sleep -Milliseconds 200
 }while($clock.Elapsed.TotalSeconds -lt 150)
 if($null -eq $raw){throw 'GTGT04_RESULT_TIMEOUT'}
}catch{
 # Only bounded categories, never exception text, native output or local paths.
 $message=$_.Exception.Message
 $failure=if($message -cmatch '\AGTGT04_[A-Z0-9_]{1,100}\z'){$message}else{'GTGT04_WRAPPER_FAILURE'}
}finally{
 $startupPath=$hostPath+'.startup.json';if((Test-Path -LiteralPath $startupPath -PathType Leaf) -and (Get-Item -LiteralPath $startupPath).Length -le 512){try{$v=Get-Content -LiteralPath $startupPath -Raw|ConvertFrom-Json -AsHashtable;if($v.stage -cin @('source','profile-helper','observer-helper','original-entry','original-exited','exception') -and $v.category -cin @('none','remoting','type-init','type-load','file-missing','assembly-load','invalid-operation','argument','null-reference','other')){$startup=$v}}catch{}}
 if($null -ne $owner){try{$stopped=$owner.Stop(5000);$clean=$stopped -and $owner.WaitForRootExit(0) -and $owner.ActiveProcesses -eq 0 -and $owner.CleanupVerified;$owner.Dispose();$clean=$clean -and $owner.CleanupVerified}catch{$clean=$false}}
 try{$sourceSafe=$true;foreach($name in $pins.Keys){if((Get-FileHash -LiteralPath (Join-Path $project $name) -Algorithm SHA256).Hash.ToLowerInvariant() -cne $pins[$name]){$sourceSafe=$false}}}catch{$sourceSafe=$false}
 foreach($rule in $rules){Remove-NetFirewallRule -DisplayName $rule -ErrorAction SilentlyContinue}
 foreach($path in $created){Remove-Item -LiteralPath $path -Force -ErrorAction SilentlyContinue}
 Remove-Item -LiteralPath $work -Recurse -Force -ErrorAction SilentlyContinue
 if($clean -and $null -ne $login -and $login.fixtureDirectoryCreated){Remove-Item -LiteralPath $fixture -Recurse -Force -ErrorAction SilentlyContinue}
}
if(-not $clean -or -not $compilerSafe -or -not $sourceSafe){throw 'GTGT04_CLEANUP_OR_SOURCE_BOUNDARY'}
$loginStatus=if($null -ne $login -and $login.status -in @('synthetic-profile-window-observed','exact-login-controls-not-found','new-id-not-posted','root-exited','synthetic-input-not-verified','login-not-posted','next-window-not-yet-identified','login-transition-not-verified','native-login-helper-unavailable')){$login.status}else{'not-verified'}
$report=[ordered]@{startup=$startup;loginStatus=$loginStatus;format='htkk-gtgt04-event-execution-v1';compilerJobCleanupVerified=$compilerSafe;supplierJobCleanupVerified=$clean;sourceHashesUnchanged=$sourceSafe;failure=$failure;observation=$null;primitiveOnly=$true;nativeQualified=$false;filingEnabled=$false}
if($null -ne $raw){
 if($raw.format -cne 'htkk-gtgt04-event-ui-v1' -or $raw.runtime -cne 'clr2-x86' -or $raw.stage -cnotin @('observed','blocked') -or $raw.failure -cnotin @('none','ui-contract','sheet-contract','timeout','source-version') -or $raw.observations.Count -gt 13){throw 'GTGT04_RESULT_SHAPE'}
 if($raw.stage -ceq 'observed'){foreach($flag in @('profileVerified','profileClosed','periodConfigured','annexSelected','sourcePinsVerified','contextMatched')){if($raw[$flag] -isnot [bool] -or -not $raw[$flag]){throw 'GTGT04_CONTEXT_BOUNDARY'}}}
 foreach($flag in @('realTaxpayerDataUsed','xmlAuthored','businessHelperInvoked','computedCellsWritten','nativeQualified','filingEnabled')){if($raw[$flag] -isnot [bool] -or $raw[$flag]){throw 'GTGT04_RESULT_PRIVACY'}}
 foreach($row in $raw.observations){if($row.label -cnotmatch '\A(initial|scenario[0-2]-row[0-3])\z' -or $row.cells.Count -ne 12){throw 'GTGT04_OBSERVATION_SHAPE'};foreach($entry in $row.cells.GetEnumerator()){if($entry.Key -cnotmatch '\A(Q|Z|AW)(87|88|89|90)\z' -or $entry.Value.value -isnot [string] -or $entry.Value.value.Length -gt 128 -or $entry.Value.value -cnotmatch '\A[+0-9.eE-]+\z' -or $entry.Value.text -isnot [string] -or $entry.Value.text.Length -gt 128 -or $entry.Value.text -cnotmatch '\A[+0-9., -]+\z' -or $entry.Value.locked -isnot [bool]){throw 'GTGT04_OBSERVATION_PRIVACY'}}}
 $report.observation=$raw
}
$report|ConvertTo-Json -Depth 12 -Compress|Write-Output
if($failure -cne 'none' -or $null -eq $raw -or $raw.stage -cne 'observed' -or $raw.editorActions -ne 12 -or $raw.observations.Count -ne 13){throw 'GTGT04_EVENT_NOT_OBSERVED'}
