# Actual Windows/Framework readiness check under the same clean native-runner policy.
# No HTKK, taxpayer fixture, UI tree traversal, external network or Add-Type autoload.
$ErrorActionPreference='Stop'
if([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT){
 Write-Host 'SKIP: Framework UIA assembly-load integration requires Windows; no Windows readiness proven.'
 return
}
. (Join-Path $PSScriptRoot 'Invoke-HtkkBoundedNativeProcess.ps1')
$directory=Join-Path $env:RUNNER_TEMP ('htkk-framework-uia-load-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $directory|Out-Null
$child=Join-Path $directory 'framework-uia-load.ps1'
$resultPath=Join-Path $directory 'framework-uia-result.json'
$legacy=Join-Path $env:WINDIR 'System32\WindowsPowerShell\v1.0\powershell.exe'
try{
 @'
param([string]$OutputFile)
$ErrorActionPreference='Stop'
$clientIdentity='UIAutomationClient, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35'
$typesIdentity='UIAutomationTypes, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35'
$clientMatched=$false;$typesMatched=$false;$elementReady=$false;$controlReady=$false
$sortObjectMatched=$false;$jsonSerializationMatched=$false;$setContentMatched=$false
$apartmentMatched=[Threading.Thread]::CurrentThread.GetApartmentState() -eq [Threading.ApartmentState]::STA
$runtimeMatched=[Environment]::Version.Major -eq 4
try{
 # Direct CLR binding bypasses PowerShell cmdlet/module discovery in the clean child.
 $client=[Reflection.Assembly]::Load($clientIdentity)
 $types=[Reflection.Assembly]::Load($typesIdentity)
 $clientMatched=$client.FullName -ceq $clientIdentity
 $typesMatched=$types.FullName -ceq $typesIdentity
 $element=$client.GetType('System.Windows.Automation.AutomationElement',$false)
 $control=$types.GetType('System.Windows.Automation.ControlType',$false)
 $elementReady=$null -ne $element -and $element.Assembly -eq $client
 $controlReady=$null -ne $control -and $control.Assembly -eq $types
 # Exercise the remaining generated-UIA cmdlets on fixed public synthetic data.
 $sorted=@(@(3,1,2)|Sort-Object)
 $sortObjectMatched=$sorted.Count -eq 3 -and $sorted[0] -eq 1 -and $sorted[1] -eq 2 -and $sorted[2] -eq 3
 $fixture=[ordered]@{format='htkk-uia-framework-fixed-v1';values=$sorted;synthetic=$true}
 $fixtureJson=$fixture|ConvertTo-Json -Depth 4
 $jsonSerializationMatched=$fixtureJson.Length -gt 0 -and $fixtureJson.Length -le 1024 -and $fixtureJson.Contains('htkk-uia-framework-fixed-v1')
 $fixturePath=$OutputFile+'.cmdlets.json'
 $fixtureJson|Set-Content -LiteralPath $fixturePath -Encoding UTF8
 $setContentMatched=[IO.File]::Exists($fixturePath) -and [IO.File]::ReadAllText($fixturePath,[Text.Encoding]::UTF8).Trim() -ceq $fixtureJson.Trim()
}catch{}
$ready=$clientMatched -and $typesMatched -and $elementReady -and $controlReady -and $apartmentMatched -and $runtimeMatched -and $sortObjectMatched -and $jsonSerializationMatched -and $setContentMatched
$status=if($ready){'ready'}else{'not-ready'}
$json='{"format":"htkk-framework-uia-assembly-load-v1","status":"'+$status+'","clientIdentityMatched":'+$clientMatched.ToString().ToLowerInvariant()+',"typesIdentityMatched":'+$typesMatched.ToString().ToLowerInvariant()+',"elementTypeReady":'+$elementReady.ToString().ToLowerInvariant()+',"controlTypeReady":'+$controlReady.ToString().ToLowerInvariant()+',"apartmentMatched":'+$apartmentMatched.ToString().ToLowerInvariant()+',"runtimeMatched":'+$runtimeMatched.ToString().ToLowerInvariant()+',"sortObjectMatched":'+$sortObjectMatched.ToString().ToLowerInvariant()+',"jsonSerializationMatched":'+$jsonSerializationMatched.ToString().ToLowerInvariant()+',"setContentMatched":'+$setContentMatched.ToString().ToLowerInvariant()+'}'
[IO.File]::WriteAllText($OutputFile,$json,[Text.UTF8Encoding]::new($false))
if($ready){exit 0}else{exit 2}
'@|Set-Content -LiteralPath $child -Encoding utf8BOM
 $clock=[Diagnostics.Stopwatch]::StartNew()
 $run=Invoke-HtkkBoundedNativeProcess -Executable $legacy -WorkingDirectory $directory -Arguments @('-STA','-NoLogo','-NoProfile','-NonInteractive','-ExecutionPolicy','RemoteSigned','-File',$child,'-OutputFile',$resultPath) -TimeoutMilliseconds 15000
 if($run.status -cne 'exited' -or $run.exitCode -ne 0 -or -not $run.processStopped -or $run.timedOut){throw 'FRAMEWORK_UIA_ASSEMBLY_LOAD_PROCESS_NOT_VERIFIED'}
 if($clock.Elapsed.TotalMilliseconds -gt 15000){throw 'FRAMEWORK_UIA_ASSEMBLY_LOAD_EXCEEDED_DEADLINE'}
 if(-not(Test-Path -LiteralPath $resultPath -PathType Leaf) -or (Get-Item -LiteralPath $resultPath).Length -gt 2048){throw 'FRAMEWORK_UIA_ASSEMBLY_LOAD_RESULT_UNAVAILABLE'}
 $result=Get-Content -LiteralPath $resultPath -Raw -Encoding UTF8|ConvertFrom-Json -AsHashtable
 $flags=@('clientIdentityMatched','typesIdentityMatched','elementTypeReady','controlTypeReady','apartmentMatched','runtimeMatched','sortObjectMatched','jsonSerializationMatched','setContentMatched')
 $keys=@('format','status')+$flags
 if($result.Count -ne $keys.Count -or @($result.Keys|Where-Object{$_ -cnotin $keys}).Count -or $result.format -cne 'htkk-framework-uia-assembly-load-v1' -or $result.status -cne 'ready'){throw 'FRAMEWORK_UIA_ASSEMBLY_LOAD_RESULT_INVALID'}
 foreach($flag in $flags){if($result[$flag] -isnot [bool] -or -not $result[$flag]){throw 'FRAMEWORK_UIA_ASSEMBLY_LOAD_IDENTITY_OR_TYPE_NOT_VERIFIED'}}
 $fixturePath=$resultPath+'.cmdlets.json'
 if(-not(Test-Path -LiteralPath $fixturePath -PathType Leaf) -or (Get-Item -LiteralPath $fixturePath).Length -gt 1024){throw 'FRAMEWORK_UIA_CMDLET_FIXTURE_UNAVAILABLE'}
 $fixture=Get-Content -LiteralPath $fixturePath -Raw -Encoding UTF8|ConvertFrom-Json -AsHashtable
 if($fixture.Count -ne 3 -or @($fixture.Keys|Where-Object{$_ -cnotin @('format','values','synthetic')}).Count -or $fixture.format -cne 'htkk-uia-framework-fixed-v1' -or $fixture.synthetic -isnot [bool] -or -not $fixture.synthetic -or $fixture.values -isnot [Array] -or $fixture.values.Count -ne 3){throw 'FRAMEWORK_UIA_CMDLET_FIXTURE_INVALID'}
 for($index=0;$index -lt 3;$index++){if($fixture.values[$index] -isnot [long] -and $fixture.values[$index] -isnot [int]){throw 'FRAMEWORK_UIA_CMDLET_FIXTURE_INVALID'};if($fixture.values[$index] -ne ($index+1)){throw 'FRAMEWORK_UIA_CMDLET_SORT_NOT_VERIFIED'}}
 Write-Host 'Clean Windows PowerShell Framework UIA assembly identities/types/STA and fixed-data cmdlets verified within 15 seconds.'
}finally{Remove-Item -LiteralPath $directory -Recurse -Force -ErrorAction SilentlyContinue}
