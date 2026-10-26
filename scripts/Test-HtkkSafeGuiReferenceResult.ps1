# Offline schema-boundary tests for the actual public-result reader; no HTKK input.
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'Get-HtkkSafeGuiReferenceResult.ps1')
$directory=Join-Path $env:RUNNER_TEMP ('htkk-gui-result-test-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $directory | Out-Null
$file=Join-Path $directory 'result.json'
$base=[ordered]@{format='htkk-gui-reference-automation-v1';mode='inspect';stage='profile-inspected';failureCategory='none';editorKind='not-started';runtime='clr2-x86-custom-reference';sourcePinsVerified=$true;visibleForms=1;spreadCount=1;sheetRows=74;sheetColumns=22;mstBoxesMatched=$true;initialRequiredTextBlank=$true;editingApiAvailable=$true;performedInputCount=0;originalSaveInvoked=$false;savedHeaderExists=$false;savedHeaderChecksMatched=$false;savedHeaderCheckedFieldCount=0;saveDialogKind='not-observed';savedHeaderMismatchMask=0;profileClosed=$false;mainMenuObserved=$false;d1MenuClicked=$false;gtgtPeriodObserved=$false;menuRowCount=0;menuClickCount=0;periodControlCount=0;periodControls=@{};periodYearMonthMatched=$false;periodFirstDeclarationMatched=$false;periodActivityMatched=$false;periodGeographyMatched=$false;periodNoAnnexMatched=$false;periodConfirmInvoked=$false;gtgtWorkbookPinsVerified=$false;gtgtMenuVersionMatched=$false;gtgtPeriodModelMatched=$false;gtgtSheetObserved=$false;gtgtSheetNameMatched=$false;gtgtDimensionsMatched=$false;gtgtIdentityMatched=$false;gtgtCt21Ready=$false;gtgtSignatureReady=$false;gtgtMonetaryZero=$false;annexSelectedCount=0;gtgtSheetRows=0;gtgtSheetColumns=0;gtgtSheetCount=0;gtgtEmptyMonetaryCount=0;exportCommandInvoked=$false;exportSelectorMatched=$false;exportButtonInvoked=$false;exportDialogMatched=$false;exportDestinationFresh=$false;exportDialogSubmitted=$false;exportFileExists=$false;exportXmlRootMatched=$false;exportSyntheticIdentityMatched=$false;exportSuccessAcknowledged=$false;exportSchemaPinnedVerified=$false;exportFilenameKeyboardCommitted=$false;exportFilenameParentKind='not-observed';exportOriginalPathMatched=$false;exportOriginalPathKind='not-observed';exportScopedFileCount=0;exportScopedXmlCount=0;exportBytes=0;exportSha256='';roundtripImportCommandInvoked=$false;roundtripImportDialogMatched=$false;roundtripImportKeyboardCommitted=$false;roundtripImportDialogSubmitted=$false;roundtripImportPathMatched=$false;roundtripImportSheetMatched=$false;roundtripImportSucceeded=$false;roundtripReexportCommandInvoked=$false;roundtripReexportSucceeded=$false;roundtripXmlExactMatched=$false;roundtripImportCheckedMoneyCount=0;roundtripReexportBytes=0;roundtripReexportSha256='';webInputVerified=$false;webImportInputSha256='';webSourceSha='';controlKinds=@{form=1;button=2;combo=0;text=0;spread=1;other=7};realTaxpayerDataUsed=$false;runtimeRoundTrip=$false}
$cases=0
try {
 $base | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath $file -Encoding UTF8
 if((Get-HtkkSafeGuiReferenceResult -ResultPath $file -ExpectedMode inspect).status -ne 'valid'){throw 'Safe GUI baseline rejected'};$cases++
 foreach($change in @(@{key='stage';value='RAW PRIVATE MESSAGE'},@{key='stage';value=@()},@{key='runtimeRoundTrip';value=$true},@{key='realTaxpayerDataUsed';value=$true},@{key='originalSaveInvoked';value=1},@{key='visibleForms';value=65},@{key='sheetRows';value=1.5},@{key='extra';value='PRIVATE'},@{key='mode';value='profile-save'},@{key='saveDialogKind';value='RAW'},@{key='savedHeaderMismatchMask';value=256},@{key='profileClosed';value=1},@{key='periodYearMonthMatched';value=1},@{key='exportFileExists';value=1},@{key='exportOriginalPathKind';value='RAW PRIVATE PATH'},@{key='exportScopedFileCount';value=33},@{key='exportOriginalPathMatched';value=1},@{key='exportFilenameKeyboardCommitted';value=1},@{key='exportSchemaPinnedVerified';value=1},@{key='roundtripImportSucceeded';value=1},@{key='webInputVerified';value=1},@{key='webInputVerified';value=$true},@{key='webImportInputSha256';value='PRIVATE INPUT XML'},@{key='webSourceSha';value=('a'*41)},@{key='roundtripImportCheckedMoneyCount';value=28},@{key='roundtripReexportBytes';value=262145},@{key='roundtripReexportSha256';value='RAW XML'},@{key='exportFilenameParentKind';value='RAW WINDOW TEXT'},@{key='exportBytes';value=262145},@{key='exportSha256';value='PRIVATE OUTPUT XML'},@{key='exportSha256';value=('a'*65)},@{key='gtgtSheetCount';value=33},@{key='menuClickCount';value=4},@{key='periodControls';value=@{SECRET=@{kind='text';visible=$true;enabled=$true;checkedAvailable=$false;checked=$false}}})) {
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
 foreach($selectionStage in @('gtgt-export-filename-keyboard-editing','gtgt-export-success-file-checking','waiting-profile-close-ready','gtgt-period-province-selecting','gtgt-period-ward-selecting','gtgt-period-taxhead-selecting','gtgt-period-taxlocal-selecting','gtgt-period-activity-selecting')){
  $stageCopy=[ordered]@{};foreach($key in $base.Keys){$stageCopy[$key]=$base[$key]};$stageCopy.mode='gtgt-sheet-inspect';$stageCopy.stage=$selectionStage
  $stageCopy | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $file -Encoding UTF8
  if((Get-HtkkSafeGuiReferenceResult -ResultPath $file -ExpectedMode gtgt-sheet-inspect).status -ne 'valid'){throw 'Safe period selection stage rejected'};$cases++
 }
 $copy=[ordered]@{};foreach($key in $base.Keys){$copy[$key]=$base[$key]};$copy.mode='gtgt-sheet-inspect';$copy.stage='gtgt-sheet-inspected';$copy.gtgtSheetRows=72;$copy.gtgtSheetColumns=24
 $copy | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $file -Encoding UTF8
 if((Get-HtkkSafeGuiReferenceResult -ResultPath $file -ExpectedMode gtgt-sheet-inspect).status -ne 'valid'){throw 'Safe D1 sheet descriptor rejected'};$cases++
 $copy=[ordered]@{};foreach($key in $base.Keys){$copy[$key]=$base[$key]};$copy.mode='gtgt-export-inspect';$copy.stage='gtgt-export-inspected';$copy.exportBytes=1234;$copy.exportSha256=('a'*64)
 $copy | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $file -Encoding UTF8
 if((Get-HtkkSafeGuiReferenceResult -ResultPath $file -ExpectedMode gtgt-export-inspect).status -ne 'valid'){throw 'Safe export metadata rejected'};$cases++
 foreach($roundtripStage in @('gtgt-import-ready-waiting','gtgt-import-file-dialog-waiting','gtgt-import-filename-keyboard-editing','gtgt-import-original-reading','gtgt-import-original-message-rejected','gtgt-import-success-sheet-checking','gtgt-reexport-ready-waiting','gtgt-reexport-command-invoking','gtgt-roundtrip-inspected')){
  $copy=[ordered]@{};foreach($key in $base.Keys){$copy[$key]=$base[$key]};$copy.mode='gtgt-roundtrip-inspect';$copy.stage=$roundtripStage;$copy.roundtripReexportSha256=('b'*64)
  $copy | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $file -Encoding UTF8
  if((Get-HtkkSafeGuiReferenceResult -ResultPath $file -ExpectedMode gtgt-roundtrip-inspect).status -ne 'valid'){throw 'Safe roundtrip observation rejected'};$cases++
 }
 foreach($webStage in @('gtgt-web-input-checking','gtgt-web-import-ready-waiting','gtgt-web-import-inspected')){
  $copy=[ordered]@{};foreach($key in $base.Keys){$copy[$key]=$base[$key]};$copy.mode='gtgt-web-import-inspect';$copy.stage=$webStage;$copy.webInputVerified=$true;$copy.webImportInputSha256=('c'*64);$copy.webSourceSha=('d'*40)
  $copy | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $file -Encoding UTF8
  if((Get-HtkkSafeGuiReferenceResult -ResultPath $file -ExpectedMode gtgt-web-import-inspect).status -ne 'valid'){throw 'Safe web input metadata rejected'};$cases++
 }
 Remove-Item -LiteralPath $file
 if((Get-HtkkSafeGuiReferenceResult -ResultPath $file -ExpectedMode inspect).status -ne 'unavailable'){throw 'Missing result accepted'};$cases++
 Write-Output "Safe GUI result boundary tests passed: $cases"
}finally{Remove-Item -LiteralPath $directory -Recurse -Force -ErrorAction SilentlyContinue}
