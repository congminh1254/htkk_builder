# Offline schema-boundary tests for the actual public-result reader; no HTKK input.
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'Get-HtkkSafeGuiReferenceResult.ps1')
$directory=Join-Path $env:RUNNER_TEMP ('htkk-gui-result-test-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $directory | Out-Null
$file=Join-Path $directory 'result.json'
$base=[ordered]@{format='htkk-gui-reference-automation-v1';mode='inspect';stage='profile-inspected';failureCategory='none';editorKind='not-started';runtime='clr2-x86-custom-reference';sourcePinsVerified=$true;visibleForms=1;spreadCount=1;sheetRows=74;sheetColumns=22;mstBoxesMatched=$true;initialRequiredTextBlank=$true;editingApiAvailable=$true;performedInputCount=0;originalSaveInvoked=$false;savedHeaderExists=$false;savedHeaderChecksMatched=$false;savedHeaderCheckedFieldCount=0;saveDialogKind='not-observed';savedHeaderMismatchMask=0;profileClosed=$false;mainMenuObserved=$false;d1MenuClicked=$false;gtgtPeriodObserved=$false;menuRowCount=0;menuClickCount=0;periodControlCount=0;periodControls=@{};controlKinds=@{form=1;button=2;combo=0;text=0;spread=1;other=7};realTaxpayerDataUsed=$false;runtimeRoundTrip=$false}
$cases=0
try {
 $base | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath $file -Encoding UTF8
 if((Get-HtkkSafeGuiReferenceResult -ResultPath $file -ExpectedMode inspect).status -ne 'valid'){throw 'Safe GUI baseline rejected'};$cases++
 foreach($change in @(@{key='stage';value='RAW PRIVATE MESSAGE'},@{key='stage';value=@()},@{key='runtimeRoundTrip';value=$true},@{key='realTaxpayerDataUsed';value=$true},@{key='originalSaveInvoked';value=1},@{key='visibleForms';value=65},@{key='sheetRows';value=1.5},@{key='extra';value='PRIVATE'},@{key='mode';value='profile-save'},@{key='saveDialogKind';value='RAW'},@{key='savedHeaderMismatchMask';value=256},@{key='profileClosed';value=1},@{key='menuClickCount';value=4},@{key='periodControls';value=@{SECRET=@{kind='text';visible=$true;enabled=$true;checkedAvailable=$false;checked=$false}}})) {
  $copy=[ordered]@{};foreach($key in $base.Keys){$copy[$key]=$base[$key]};$copy[$change.key]=$change.value
  $copy | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath $file -Encoding UTF8
  $read=Get-HtkkSafeGuiReferenceResult -ResultPath $file -ExpectedMode inspect
  if($read.status -ne 'invalid' -or $read.Count -ne 4){throw 'Unsafe GUI schema accepted'};$cases++
 }
 $copy=[ordered]@{};foreach($key in $base.Keys){$copy[$key]=$base[$key]};$copy.controlKinds=@{form=1;button=2;combo=0;text=0;spread=1;other=7;PRIVATE=1}
 $copy | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath $file -Encoding UTF8
 if((Get-HtkkSafeGuiReferenceResult -ResultPath $file -ExpectedMode inspect).status -ne 'invalid'){throw 'Unknown kind accepted'};$cases++
 $copy=[ordered]@{};foreach($key in $base.Keys){$copy[$key]=$base[$key]};$copy.mode='gtgt-inspect';$copy.stage='gtgt-period-inspected';$copy.periodControls=@{mskYear=@{kind='masked-text';visible=$true;enabled=$true;checkedAvailable=$false;checked=$false};OptChinhthuc=@{kind='radio';visible=$true;enabled=$true;checkedAvailable=$true;checked=$true}}
 $copy | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $file -Encoding UTF8
 if((Get-HtkkSafeGuiReferenceResult -ResultPath $file -ExpectedMode gtgt-inspect).status -ne 'valid'){throw 'Safe period descriptor rejected'};$cases++
 foreach($description in @(@{kind='masked-text';visible=$true;enabled=$true;checkedAvailable=$false;checked=$true},@{kind='masked-text';visible=$true;enabled=$true;checkedAvailable=$false;checked=$false;Text='SECRET'},@{kind='PRIVATE';visible=$true;enabled=$true;checkedAvailable=$false;checked=$false})) {
  $copy.periodControls=@{mskYear=$description};$copy | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $file -Encoding UTF8
  if((Get-HtkkSafeGuiReferenceResult -ResultPath $file -ExpectedMode gtgt-inspect).status -ne 'invalid'){throw 'Unsafe period descriptor accepted'};$cases++
 }
 Remove-Item -LiteralPath $file
 if((Get-HtkkSafeGuiReferenceResult -ResultPath $file -ExpectedMode inspect).status -ne 'unavailable'){throw 'Missing result accepted'};$cases++
 Write-Output "Safe GUI result boundary tests passed: $cases"
}finally{Remove-Item -LiteralPath $directory -Recurse -Force -ErrorAction SilentlyContinue}
