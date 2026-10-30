[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$ProjectDirectory)
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'Invoke-HtkkBoundedCompiler.ps1')
. (Join-Path $PSScriptRoot 'Invoke-HtkkBoundedJobProcess.ps1')
$pins=@{'FarPoint.CalcEngine.dll'='19183e5a0ad1d74bed1fc151178a8a118ae6544cddb7e3aabc64940f45900d5a';'FarPoint.Win.Spread.dll'='2e7a0d4fc1ef6f219dd3a237ae6b26549ad03541d58da6f45d638309d2fa4c50';'FarPoint.Win.dll'='fae1320c67dbbfb97fafc0fb8716e4743a4728b4c0d7155e270d684568ef4d2a'}
$work=Join-Path $env:RUNNER_TEMP ('htkk-formula-oracle-'+[guid]::NewGuid().ToString('N'));$rule=$null
try{
 foreach($p in $pins.Keys){if((Get-FileHash -LiteralPath (Join-Path $ProjectDirectory $p) -Algorithm SHA256).Hash.ToLowerInvariant() -cne $pins[$p]){throw 'FORMULA_ORACLE_SOURCE_PIN'}}
 New-Item -ItemType Directory -Path $work|Out-Null
 $exe=Join-Path $work 'FormulaOracle.exe';$result=Join-Path $work 'result.json';$compiler=Join-Path $env:WINDIR 'Microsoft.NET/Framework/v2.0.50727/csc.exe'
 $c=Invoke-HtkkBoundedCompiler -Executable $compiler -WorkingDirectory $work -Arguments @('/nologo','/target:exe','/platform:x86','/optimize+',('/out:'+$exe),(Join-Path $PSScriptRoot 'HtkkFormulaOracle.cs')) -TimeoutMilliseconds 30000
 if($c.status -cne 'exited' -or $c.exitCode -ne 0 -or $c.timedOut -or -not $c.jobCleanupVerified -or -not $c.diagnosticsVerified){throw 'FORMULA_ORACLE_COMPILER_BOUNDARY'}
 $rule='HTKK fixed formula oracle '+[guid]::NewGuid().ToString('N');New-NetFirewallRule -DisplayName $rule -Direction Outbound -Program $exe -Action Block|Out-Null
 $r=Invoke-HtkkBoundedJobProcess -Executable $exe -WorkingDirectory $work -Arguments @($ProjectDirectory,$result) -TimeoutMilliseconds 30000
 if($r.status -cne 'exited' -or $r.exitCode -ne 0 -or $r.timedOut -or -not $r.jobCleanupVerified -or -not $r.processStopped){throw 'FORMULA_ORACLE_PROCESS_BOUNDARY'}
 foreach($p in $pins.Keys){if((Get-FileHash -LiteralPath (Join-Path $ProjectDirectory $p) -Algorithm SHA256).Hash.ToLowerInvariant() -cne $pins[$p]){throw 'FORMULA_ORACLE_SOURCE_CHANGED'}}
 if(-not(Test-Path -LiteralPath $result -PathType Leaf) -or (Get-Item -LiteralPath $result).Length -gt 65536){throw 'FORMULA_ORACLE_RESULT_SIZE'}
 $v=Get-Content -LiteralPath $result -Raw -Encoding UTF8|ConvertFrom-Json -AsHashtable -DateKind String
 if($v.format -cne 'htkk-formula-oracle-v1' -or $v.runtime -cne 'clr2-x86' -or $v.primitiveOnly -isnot [bool] -or -not $v.primitiveOnly -or $v.cases.Count -ne 168){throw 'FORMULA_ORACLE_RESULT_SHAPE'}
 for($i=0;$i -lt $v.cases.Count;$i++){$x=$v.cases[$i];if($x.id -ne $i+1 -or $x.formula -isnot [string] -or $x.formula.Length -gt 128 -or $x.fixture -cnotin @('numeric','mixed','errors') -or $x.result.kind -cnotin @('number','text','boolean','blank','error','date') -or $x.result.value -isnot [string] -or $x.result.value.Length -gt 256){throw 'FORMULA_ORACLE_CASE_SHAPE'}}
 $safe=[ordered]@{format='htkk-formula-oracle-execution-v1';sourceHashesVerified=$true;sourceHashesUnchanged=$true;compilerJobCleanupVerified=$true;oracleJobCleanupVerified=$true;runtime='clr2-x86';primitiveOnly=$true;cases=$v.cases}
 $safe|ConvertTo-Json -Depth 8 -Compress|Write-Output
}finally{
 if($rule){Remove-NetFirewallRule -DisplayName $rule -ErrorAction SilentlyContinue}
 Remove-Item -LiteralPath $work -Recurse -Force -ErrorAction SilentlyContinue
}
