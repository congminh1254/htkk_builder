[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$ProjectDirectory)
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'Invoke-HtkkBoundedCompiler.ps1')
. (Join-Path $PSScriptRoot 'Invoke-HtkkBoundedJobProcess.ps1')
$pins=@{'HTKK.exe.config'='b3547d6a6a61fd6e8e8b64c8976e8702aa94a2b5a44a1cf394c5486162297047';'HTKK.exe'='411141d2e728a45f4a35a876afb169d0ac2450de2499e8a1f43ac29ab6401938';'TAX.HTKK.Utilities.dll'='ccc35605a4d3bb235f896d6ab43cec4c6543a404159cf10897a57cba23d817ec';'TAX.HTKK.Business.dll'='281689aaa7df4db33d0debcfc61d32c0c318bb871d4a19a0277d871a7c04bba7';'FarPoint.CalcEngine.dll'='19183e5a0ad1d74bed1fc151178a8a118ae6544cddb7e3aabc64940f45900d5a';'FarPoint.Win.Spread.dll'='2e7a0d4fc1ef6f219dd3a237ae6b26549ad03541d58da6f45d638309d2fa4c50';'FarPoint.Win.dll'='fae1320c67dbbfb97fafc0fb8716e4743a4728b4c0d7155e270d684568ef4d2a'}
$work=Join-Path $env:RUNNER_TEMP ('htkk-table-lifecycle-oracle-'+[guid]::NewGuid().ToString('N'));$rule=$null
try{
 foreach($p in $pins.Keys){if((Get-FileHash -LiteralPath (Join-Path $ProjectDirectory $p) -Algorithm SHA256).Hash.ToLowerInvariant() -cne $pins[$p]){throw 'TABLE_LIFECYCLE_ORACLE_SOURCE_PIN'}}
 New-Item -ItemType Directory -Path $work|Out-Null
 $exe=Join-Path $work 'TableLifecycleOracle.exe';$result=Join-Path $work 'result.json';$compiler=Join-Path $env:WINDIR 'Microsoft.NET/Framework/v2.0.50727/csc.exe'
 $c=Invoke-HtkkBoundedCompiler -Executable $compiler -WorkingDirectory $work -Arguments @('/nologo','/target:exe','/platform:x86','/optimize+',('/out:'+$exe),(Join-Path $PSScriptRoot 'HtkkTableLifecycleOracle.cs')) -TimeoutMilliseconds 30000
 if($c.status -cne 'exited' -or $c.exitCode -ne 0 -or $c.timedOut -or -not $c.jobCleanupVerified -or -not $c.diagnosticsVerified){throw 'TABLE_LIFECYCLE_ORACLE_COMPILER_BOUNDARY'}
 $rule='HTKK fixed table lifecycle oracle '+[guid]::NewGuid().ToString('N');New-NetFirewallRule -DisplayName $rule -Direction Outbound -Program $exe -Action Block|Out-Null
 $r=Invoke-HtkkBoundedJobProcess -Executable $exe -WorkingDirectory $work -Arguments @($ProjectDirectory,$result) -TimeoutMilliseconds 30000
 if($r.status -cne 'exited' -or $r.exitCode -ne 0 -or $r.timedOut -or -not $r.jobCleanupVerified -or -not $r.processStopped){throw 'TABLE_LIFECYCLE_ORACLE_PROCESS_BOUNDARY'}
 foreach($p in $pins.Keys){if((Get-FileHash -LiteralPath (Join-Path $ProjectDirectory $p) -Algorithm SHA256).Hash.ToLowerInvariant() -cne $pins[$p]){throw 'TABLE_LIFECYCLE_ORACLE_SOURCE_CHANGED'}}
 if(-not(Test-Path -LiteralPath $result -PathType Leaf) -or (Get-Item -LiteralPath $result).Length -gt 65536){throw 'TABLE_LIFECYCLE_ORACLE_RESULT_SIZE'}
 $v=Get-Content -LiteralPath $result -Raw -Encoding UTF8|ConvertFrom-Json -AsHashtable -DateKind String
 if($v.format -ceq 'htkk-table-lifecycle-oracle-failure-v1'){if($v.stage -cnotmatch '^(load|initial-table|step[1-8])$' -or $v.category -cnotin @('null-reference','argument','invalid-operation','type-load','file-missing','other')){throw 'TABLE_LIFECYCLE_ORACLE_FAILURE_SHAPE'};$v|ConvertTo-Json -Compress|Write-Output;throw 'TABLE_LIFECYCLE_ORACLE_NATIVE_FAILURE'}
 if($v.format -cne 'htkk-table-lifecycle-oracle-v1' -or $v.runtime -cne 'clr2-x86' -or $v.menu -cne 'D1' -or $v.fixture -cne 'synthetic-zero-data-rows-with-stt' -or $v.primitiveOnly -isnot [bool] -or -not $v.primitiveOnly -or $v.cases.Count -ne 9){throw 'TABLE_LIFECYCLE_ORACLE_RESULT_SHAPE'}
 foreach($name in @('originalMainInvoked','realTaxpayerDataUsed','computedTotalsWritten','xmlAuthored','nativeQualified','filingEnabled')){if($v[$name] -isnot [bool] -or $v[$name]){throw 'TABLE_LIFECYCLE_ORACLE_SUPPLIER_SCOPE'}}
 $operations=@('initial','insert','insert','insert','remove','insert','remove','remove','insert');$indices=@(-1,0,0,1,1,0,0,2,1);$counts=@(1,2,3,4,3,4,3,2,3)
 for($i=0;$i -lt $v.cases.Count;$i++){
  $x=$v.cases[$i];if($x.id -ne $i+1 -or $x.operation -cne $operations[$i] -or $x.index -ne $indices[$i] -or ($x.sheetRows -isnot [int] -and $x.sheetRows -isnot [long]) -or $x.sheetRows -lt 1 -or $x.sheetRows -gt 256 -or $x.tables -isnot [System.Collections.IList] -or $x.tables.Count -ne $counts[$i]){throw 'TABLE_LIFECYCLE_ORACLE_CASE_SHAPE'}
  foreach($table in $x.tables){
   if($table -isnot [System.Collections.IDictionary] -or $table.Count -ne 6){throw 'TABLE_LIFECYCLE_ORACLE_TABLE_SHAPE'}
   foreach($key in @('tableId','stt','reportStt')){if($table[$key] -isnot [string] -or $table[$key] -cnotmatch '^[0-9]{1,3}$'){throw 'TABLE_LIFECYCLE_ORACLE_ID_SHAPE'}}
   foreach($key in @('tableRowStart','dataRowStart')){if(($table[$key] -isnot [int] -and $table[$key] -isnot [long]) -or $table[$key] -lt 1 -or $table[$key] -gt 256){throw 'TABLE_LIFECYCLE_ORACLE_LOCATION_SHAPE'}}
   if(($table.dataRows -isnot [int] -and $table.dataRows -isnot [long]) -or $table.dataRows -ne 0){throw 'TABLE_LIFECYCLE_ORACLE_DATA_ROWS'}
  }
 }
 $safe=[ordered]@{format='htkk-table-lifecycle-oracle-execution-v1';sourceHashesVerified=$true;sourceHashesUnchanged=$true;compilerJobCleanupVerified=$true;oracleJobCleanupVerified=$true;runtime='clr2-x86';primitiveOnly=$true;menu=$v.menu;fixture=$v.fixture;originalMainInvoked=$false;realTaxpayerDataUsed=$false;computedTotalsWritten=$false;xmlAuthored=$false;nativeQualified=$false;filingEnabled=$false;cases=$v.cases}
 $safe|ConvertTo-Json -Depth 8 -Compress|Write-Output
}finally{
 if($rule){Remove-NetFirewallRule -DisplayName $rule -ErrorAction SilentlyContinue}
 Remove-Item -LiteralPath $work -Recurse -Force -ErrorAction SilentlyContinue
}
