# Offline schema-boundary tests for the actual public-result reader; no HTKK input.
$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'Test-HtkkFileDialogFocusPolicy.ps1')
. (Join-Path $PSScriptRoot 'Get-HtkkSafeGuiReferenceResult.ps1')
$directory=Join-Path $env:RUNNER_TEMP ('htkk-gui-result-test-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $directory | Out-Null
$file=Join-Path $directory 'result.json'
$base=[ordered]@{annex12NumericTextSnapshots='';annex12NumericTypeSnapshots='';annex12NumericDoubleBits='';annex12NumericActionCount=0;annex12NumericCaseCount=0;annex12NumericSnapshots='';amendmentOpenLoadedSheets=0;amendmentOpenCloseInvoked=$false;amendmentOpenPriorClosed=$false;amendmentOpenDefaultsMatched=$false;amendmentOpenConfirmInvoked=$false;amendmentOpenPeriodMatched=$false;amendmentOpenSourcesMatched=$false;amendmentOpenKhbsSheetsObserved=$false;amendmentOpenPriorUnchanged=$false;amendmentOpenKhbsRows=0;amendmentOpenKhbsColumns=0;amendmentOpenExplanationRows=0;amendmentOpenExplanationColumns=0;annex12ExportMainZeroMatched=$false;annex12ExportShapeMatched=$false;annex12ExportSchemaVerified=$false;annex12InputReadOnlyIdentityMatched=$false;annex12InputIdentityMatched=$false;annex12InputTypesMatched=$false;annex12InputGeographyMatched=$false;annex12InputTaxAuthoritiesMatched=$false;annex12InputPercentagesMatched=$false;annex12InputZeroTaxMatched=$false;annex12InputActionCount=0;amendmentPriorSaveInvoked=$false;amendmentPriorSaveSuccessAcknowledged=$false;amendmentPriorDirtyCleared=$false;amendmentPriorFileFresh=$false;amendmentPriorFileScopeMatched=$false;amendmentPriorXmlParsed=$false;amendmentPriorMoneyZero=$false;amendmentPriorSavedMoneyZero=$false;amendmentLifecycleVerified=$false;amendmentPriorFileBytes=0;amendmentPriorFileSha256='';amendmentPriorSavedMoneyCount=0;format='htkk-gui-reference-automation-v1';mode='inspect';stage='profile-inspected';failureCategory='none';editorKind='not-started';runtime='clr2-x86-custom-reference';sourcePinsVerified=$true;visibleForms=1;spreadCount=1;sheetRows=74;sheetColumns=22;mstBoxesMatched=$true;initialRequiredTextBlank=$true;editingApiAvailable=$true;performedInputCount=0;originalSaveInvoked=$false;savedHeaderExists=$false;savedHeaderChecksMatched=$false;savedHeaderCheckedFieldCount=0;saveDialogKind='not-observed';savedHeaderMismatchMask=0;profileClosed=$false;mainMenuObserved=$false;d1MenuClicked=$false;gtgtPeriodObserved=$false;menuRowCount=0;menuClickCount=0;periodControlCount=0;periodControls=@{};periodYearMonthMatched=$false;periodFirstDeclarationMatched=$false;periodActivityMatched=$false;periodGeographyMatched=$false;periodNoAnnexMatched=$false;periodConfirmInvoked=$false;gtgtWorkbookPinsVerified=$false;gtgtMenuVersionMatched=$false;gtgtPeriodModelMatched=$false;gtgtSheetObserved=$false;gtgtSheetNameMatched=$false;gtgtDimensionsMatched=$false;gtgtIdentityMatched=$false;gtgtCt21Ready=$false;gtgtCt21CaseMatched=$false;gtgtCt21ConfirmationMatched=$false;gtgtCt21LocksMatched=$false;gtgtCt21BeforeExportMatched=$false;gtgtCt21AfterImportMatched=$false;gtgtCt21UncheckMatched=$false;gtgtSignatureReady=$false;gtgtMonetaryZero=$false;periodAnnex12Matched=$false;annex12SourcePinsMatched=$false;annex12SheetObserved=$false;annex12StructureMatched=$false;annex12GroupMetadataMatched=$false;annex12SttMatched=$false;annex12LocksMatched=$false;annex12SelectionActionCount=0;annex12SheetRows=0;annex12SheetColumns=0;annex12NumericCount=0;annex12NumericEmptyMask=0;annex12NumericNonzeroMask=0;annex12GroupCount=0;annex12FirstGroupId=0;annex12FirstGroupRows=0;annex12RowTabClickInvoked=$false;annex12F5Visible=$false;annex12F5Invoked=$false;annex12RowBeforeMatched=$false;annex12RowAfterMatched=$false;annex12RowSttMatched=$false;annex12RowLocksMatched=$false;annex12RowBeforeRows=0;annex12RowAfterRows=0;annex12RowBeforeGroupRows=0;annex12RowAfterGroupRows=0;annex12RowAfterGroupId=0;annex12RowInsertActionCount=0;annexSelectedCount=0;gtgtSheetRows=0;gtgtSheetColumns=0;gtgtSheetCount=0;gtgtEmptyMonetaryCount=0;exportCommandInvoked=$false;exportSelectorMatched=$false;exportButtonInvoked=$false;exportDialogMatched=$false;exportDestinationFresh=$false;exportDialogSubmitted=$false;exportFileExists=$false;exportXmlRootMatched=$false;exportSyntheticIdentityMatched=$false;exportSuccessAcknowledged=$false;exportSchemaPinnedVerified=$false;exportFilenameKeyboardCommitted=$false;exportFilenameParentKind='not-observed';exportOriginalPathMatched=$false;exportOriginalPathKind='not-observed';exportScopedFileCount=0;exportScopedXmlCount=0;exportBytes=0;exportSha256='';roundtripImportCommandInvoked=$false;roundtripImportDialogMatched=$false;roundtripImportKeyboardCommitted=$false;roundtripImportDialogSubmitted=$false;roundtripImportPathMatched=$false;roundtripImportSheetMatched=$false;roundtripImportSucceeded=$false;roundtripReexportCommandInvoked=$false;roundtripReexportSucceeded=$false;roundtripXmlExactMatched=$false;roundtripImportCheckedMoneyCount=0;roundtripReexportBytes=0;roundtripReexportSha256='';gtgtCt42BeforeExportObserved=$false;gtgtCt42LockedBeforeExport=$false;gtgtCt42AfterImportObserved=$false;gtgtCt42LockedAfterImport=$false;gtgtAutoCalculationReady=$false;gtgtBusinessInstanceMatched=$false;gtgtCaseMoneyMatched=$false;gtgtCt42Locked=$false;webCaseId='01GTGT-zero-M10-2026';webCaseEditCount=0;gtgtCaseMoneyCount=0;gtgtCaseMismatchMask=0;gtgtCaseNonzeroMask=0;webTaxValuesMatched=$false;webCreationDateMatchedNativeBaseline=$false;webServiceIdentityMatched=$false;webTaxLeafCount=0;webInputVerified=$false;webImportInputSha256='';webSourceSha='';controlKinds=@{form=1;button=2;combo=0;text=0;spread=1;other=7};realTaxpayerDataUsed=$false;runtimeRoundTrip=$false}
$cases=0
try {
 $base | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath $file -Encoding UTF8
 if((Get-HtkkSafeGuiReferenceResult -ResultPath $file -ExpectedMode inspect).status -ne 'valid'){throw 'Safe GUI baseline rejected'};$cases++
 foreach($change in @(@{key='amendmentLifecycleVerified';value=$true},@{key='amendmentPriorFileBytes';value=262145},@{key='amendmentPriorFileSha256';value='RAW PRIVATE PATH'},@{key='amendmentPriorSaveInvoked';value=$true},@{key='amendmentPriorDirtyCleared';value=1},@{key='stage';value='RAW PRIVATE MESSAGE'},@{key='stage';value=@()},@{key='runtimeRoundTrip';value=$true},@{key='realTaxpayerDataUsed';value=$true},@{key='originalSaveInvoked';value=1},@{key='visibleForms';value=65},@{key='sheetRows';value=1.5},@{key='extra';value='PRIVATE'},@{key='mode';value='profile-save'},@{key='saveDialogKind';value='RAW'},@{key='savedHeaderMismatchMask';value=256},@{key='gtgtCt21CaseMatched';value=1},@{key='gtgtCt21ConfirmationMatched';value=1},@{key='gtgtCt21LocksMatched';value=1},@{key='gtgtCt21BeforeExportMatched';value=1},@{key='gtgtCt21AfterImportMatched';value=1},@{key='profileClosed';value=1},@{key='periodYearMonthMatched';value=1},@{key='exportFileExists';value=1},@{key='exportOriginalPathKind';value='RAW PRIVATE PATH'},@{key='exportScopedFileCount';value=33},@{key='exportOriginalPathMatched';value=1},@{key='exportFilenameKeyboardCommitted';value=1},@{key='exportSchemaPinnedVerified';value=1},@{key='roundtripImportSucceeded';value=1},@{key='webCaseId';value='PRIVATE'},@{key='webCaseEditCount';value=4},@{key='gtgtCaseMismatchMask';value=134217728},@{key='gtgtCaseMoneyCount';value=28},@{key='webTaxValuesMatched';value=1},@{key='webTaxLeafCount';value=71},@{key='webInputVerified';value=1},@{key='webInputVerified';value=$true},@{key='webImportInputSha256';value='PRIVATE INPUT XML'},@{key='webSourceSha';value=('a'*41)},@{key='roundtripImportCheckedMoneyCount';value=28},@{key='roundtripReexportBytes';value=262145},@{key='roundtripReexportSha256';value='RAW XML'},@{key='exportFilenameParentKind';value='RAW WINDOW TEXT'},@{key='exportBytes';value=262145},@{key='exportSha256';value='PRIVATE OUTPUT XML'},@{key='exportSha256';value=('a'*65)},@{key='gtgtSheetCount';value=33},@{key='menuClickCount';value=4},@{key='periodControls';value=@{SECRET=@{kind='text';visible=$true;enabled=$true;checkedAvailable=$false;checked=$false}}})) {
  $copy=[ordered]@{};foreach($key in $base.Keys){$copy[$key]=$base[$key]};$copy[$change.key]=$change.value
  $copy | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath $file -Encoding UTF8
  $read=Get-HtkkSafeGuiReferenceResult -ResultPath $file -ExpectedMode inspect
  if($read.status -ne 'invalid' -or $read.Count -ne 4){throw 'Unsafe GUI schema accepted'};$cases++
 }
 $amendment=[ordered]@{};foreach($key in $base.Keys){$amendment[$key]=$base[$key]};$amendment.mode='gtgt-amendment-inspect';$amendment.stage='gtgt-original-declaration-saved-inspected'
 foreach($key in @('amendmentPriorSaveInvoked','amendmentPriorSaveSuccessAcknowledged','amendmentPriorDirtyCleared','amendmentPriorFileFresh','amendmentPriorFileScopeMatched','amendmentPriorXmlParsed','amendmentPriorMoneyZero','amendmentPriorSavedMoneyZero')){$amendment[$key]=$true}
 $amendment.amendmentPriorSavedMoneyCount=27;$amendment.amendmentPriorFileBytes=2;$amendment.amendmentPriorFileSha256='a'*64
 $amendment | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath $file -Encoding UTF8
 if((Get-HtkkSafeGuiReferenceResult -ResultPath $file -ExpectedMode 'gtgt-amendment-inspect').status -ne 'valid'){throw 'Typed prerequisite metadata rejected'};$cases++
 foreach($change in @(@{key='amendmentLifecycleVerified';value=$true},@{key='amendmentPriorFileBytes';value=0},@{key='amendmentPriorFileSha256';value=''},@{key='amendmentPriorXmlParsed';value=$false},@{key='amendmentPriorFileScopeMatched';value=$false})){
  $copy=[ordered]@{};foreach($key in $amendment.Keys){$copy[$key]=$amendment[$key]};$copy[$change.key]=$change.value
  $copy | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath $file -Encoding UTF8
  if((Get-HtkkSafeGuiReferenceResult -ResultPath $file -ExpectedMode 'gtgt-amendment-inspect').status -ne 'invalid'){throw 'Unsafe prerequisite metadata accepted'};$cases++
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
 foreach($selectionStage in @('gtgt-export-filename-focus-waiting','gtgt-export-filename-focus-timeout','gtgt-export-filename-keyboard-focused','gtgt-export-filename-keyboard-selected','gtgt-export-filename-keyboard-typed','gtgt-export-filename-keyboard-editing','gtgt-export-success-file-checking','waiting-profile-close-ready','gtgt-period-province-selecting','gtgt-period-ward-selecting','gtgt-period-taxhead-selecting','gtgt-period-taxlocal-selecting','gtgt-period-activity-selecting')){
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
 foreach($roundtripStage in @('gtgt-import-filename-focus-waiting','gtgt-import-filename-focus-timeout','gtgt-import-filename-keyboard-focused','gtgt-import-filename-keyboard-selected','gtgt-import-filename-keyboard-typed','gtgt-import-ready-waiting','gtgt-import-file-dialog-waiting','gtgt-import-filename-keyboard-editing','gtgt-import-original-reading','gtgt-import-original-message-rejected','gtgt-import-success-sheet-checking','gtgt-reexport-ready-waiting','gtgt-reexport-command-invoking','gtgt-roundtrip-inspected')){
  $copy=[ordered]@{};foreach($key in $base.Keys){$copy[$key]=$base[$key]};$copy.mode='gtgt-roundtrip-inspect';$copy.stage=$roundtripStage;$copy.roundtripReexportSha256=('b'*64)
  $copy | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $file -Encoding UTF8
  if((Get-HtkkSafeGuiReferenceResult -ResultPath $file -ExpectedMode gtgt-roundtrip-inspect).status -ne 'valid'){throw 'Safe roundtrip observation rejected'};$cases++
 }
 foreach($webStage in @('gtgt-web-input-checking','gtgt-web-import-ready-waiting','gtgt-web-import-inspected')){
  $copy=[ordered]@{};foreach($key in $base.Keys){$copy[$key]=$base[$key]};$copy.mode='gtgt-web-import-inspect';$copy.stage=$webStage;$copy.webInputVerified=$true;$copy.webImportInputSha256=('c'*64);$copy.webSourceSha=('d'*40)
  $copy | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $file -Encoding UTF8
  if((Get-HtkkSafeGuiReferenceResult -ResultPath $file -ExpectedMode gtgt-web-import-inspect).status -ne 'valid'){throw 'Safe web input metadata rejected'};$cases++
 }
 foreach($newCase in @('01GTGT-sale10-half-M10-2026','01GTGT-sale10-manual-M10-2026','01GTGT-sale5-half-M10-2026','01GTGT-sale5-manual-M10-2026','01GTGT-noactivity-zero-M10-2026','01GTGT-noactivity-reset-sale10-M10-2026','01GTGT-noactivity-cancel-sale10-M10-2026','01GTGT-noactivity-uncheck-sale10-M10-2026','01GTGT-noactivity-keep-credit-M10-2026')){
  $copy.webCaseId=$newCase;$copy.webCaseEditCount=if($newCase -ceq '01GTGT-noactivity-uncheck-sale10-M10-2026'){3}elseif($newCase -cin @('01GTGT-sale10-manual-M10-2026','01GTGT-sale5-manual-M10-2026','01GTGT-noactivity-reset-sale10-M10-2026','01GTGT-noactivity-cancel-sale10-M10-2026','01GTGT-noactivity-uncheck-sale10-M10-2026','01GTGT-noactivity-keep-credit-M10-2026')){2}else{1}
  $copy | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $file -Encoding UTF8
  if((Get-HtkkSafeGuiReferenceResult -ResultPath $file -ExpectedMode gtgt-web-import-inspect).status -ne 'valid'){throw 'Safe bounded new-case edit count rejected'};$cases++
 }
 $copy.webCaseEditCount=4;$copy | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $file -Encoding UTF8
 if((Get-HtkkSafeGuiReferenceResult -ResultPath $file -ExpectedMode gtgt-web-import-inspect).status -eq 'valid'){throw 'Unbounded native edit count accepted'};$cases++
 Remove-Item -LiteralPath $file
 if((Get-HtkkSafeGuiReferenceResult -ResultPath $file -ExpectedMode inspect).status -ne 'unavailable'){throw 'Missing result accepted'};$cases++

 $open=[ordered]@{};foreach($key in $amendment.Keys){$open[$key]=$amendment[$key]};$open.mode='gtgt-amendment-open-inspect';$open.stage='gtgt-amendment-open-inspected'
 $open.amendmentOpenCloseInvoked=$true;
 $open.amendmentOpenPriorClosed=$true;
 $open.amendmentOpenDefaultsMatched=$true;
 $open.amendmentOpenConfirmInvoked=$true;
 $open.amendmentOpenPeriodMatched=$true;
 $open.amendmentOpenSourcesMatched=$true;
 $open.amendmentOpenKhbsSheetsObserved=$true;
 $open.amendmentOpenPriorUnchanged=$true;
 $open.amendmentOpenKhbsRows=10;
 $open.amendmentOpenKhbsColumns=10;
 $open.amendmentOpenExplanationRows=10;
 $open.amendmentOpenExplanationColumns=10;$open.menuClickCount=4;$open.amendmentOpenLoadedSheets=11;
 $open | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $file -Encoding UTF8
 if((Get-HtkkSafeGuiReferenceResult -ResultPath $file -ExpectedMode 'gtgt-amendment-open-inspect').status -ne 'valid'){throw 'Typed B1 opening rejected'};$cases++
 foreach($change in @(@{key='amendmentLifecycleVerified';value=$true},@{key='amendmentOpenKhbsRows';value=0},@{key='amendmentOpenKhbsColumns';value=513},@{key='amendmentOpenSourcesMatched';value=$false},@{key='amendmentOpenPeriodMatched';value=$false},@{key='menuClickCount';value=7},@{key='amendmentOpenCloseInvoked';value=1},@{key='amendmentOpenPriorClosed';value=1},@{key='amendmentOpenDefaultsMatched';value=1},@{key='amendmentOpenConfirmInvoked';value=1},@{key='amendmentOpenPeriodMatched';value=1},@{key='amendmentOpenSourcesMatched';value=1},@{key='amendmentOpenKhbsSheetsObserved';value=1},@{key='amendmentOpenPriorUnchanged';value=1})){
  $copy=[ordered]@{};foreach($key in $open.Keys){$copy[$key]=$open[$key]};$copy[$change.key]=$change.value
  $copy | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $file -Encoding UTF8
  if((Get-HtkkSafeGuiReferenceResult -ResultPath $file -ExpectedMode 'gtgt-amendment-open-inspect').status -ne 'invalid'){throw 'Unsafe B1 opening accepted'};$cases++
 }
 $annex=[ordered]@{};foreach($key in $base.Keys){$annex[$key]=$base[$key]};$annex.mode='gtgt-annex12-inspect';$annex.stage='gtgt-annex12-inspected';$annex.periodAnnex12Matched=$true;$annex.annex12SourcePinsMatched=$true;$annex.annex12SheetObserved=$true;$annex.annex12StructureMatched=$true;$annex.annex12GroupMetadataMatched=$true;$annex.annex12SttMatched=$true;$annex.annex12LocksMatched=$true;$annex.annex12GroupCount=1;$annex.annex12FirstGroupId=1;$annex.annex12FirstGroupRows=1;$annex.annex12SelectionActionCount=1;$annex.annex12SheetRows=64;$annex.annex12SheetColumns=43;$annex.annex12NumericCount=8
 $annex | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $file -Encoding UTF8
 if((Get-HtkkSafeGuiReferenceResult -ResultPath $file -ExpectedMode gtgt-annex12-inspect).status -ne 'valid'){throw 'Bounded annex metadata rejected'};$cases++
 foreach($pair in @(@('annex12FirstGroupId',10001),@('annex12SelectionActionCount',2),@('annex12NumericNonzeroMask',256),@('annex12StructureMatched','SECRET'))){$unsafe=[ordered]@{};foreach($key in $annex.Keys){$unsafe[$key]=$annex[$key]};$unsafe[$pair[0]]=$pair[1];$unsafe | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $file -Encoding UTF8;if((Get-HtkkSafeGuiReferenceResult -ResultPath $file -ExpectedMode gtgt-annex12-inspect).status -ne 'invalid'){throw 'Unsafe annex metadata accepted'};$cases++}
 $row=[ordered]@{};foreach($key in $annex.Keys){$row[$key]=$annex[$key]};$row.mode='gtgt-annex12-row-inspect';$row.annexSelectedCount=1;$row.annex12SheetRows=66;$row.annex12SheetColumns=45;$row.stage='gtgt-annex12-row-inspected';$row.annex12RowTabClickInvoked=$true;$row.annex12F5Visible=$true;$row.annex12F5Invoked=$true;$row.annex12RowBeforeMatched=$true;$row.annex12RowAfterMatched=$true;$row.annex12RowSttMatched=$true;$row.annex12RowLocksMatched=$true;$row.annex12RowBeforeRows=66;$row.annex12RowAfterRows=67;$row.annex12RowBeforeGroupRows=1;$row.annex12RowAfterGroupRows=2;$row.annex12RowAfterGroupId=1;$row.annex12RowInsertActionCount=1
 $row | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $file -Encoding UTF8
 if((Get-HtkkSafeGuiReferenceResult -ResultPath $file -ExpectedMode gtgt-annex12-row-inspect).status -ne 'valid'){throw 'Bounded original row-insertion metadata rejected'};$cases++
 foreach($pair in @(@('annex12RowInsertActionCount',2),@('annex12RowAfterGroupRows',10001),@('annex12F5Invoked','SECRET'),@('annex12RowTabClickInvoked','SECRET'))){$unsafe=[ordered]@{};foreach($key in $row.Keys){$unsafe[$key]=$row[$key]};$unsafe[$pair[0]]=$pair[1];$unsafe | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $file -Encoding UTF8;if((Get-HtkkSafeGuiReferenceResult -ResultPath $file -ExpectedMode gtgt-annex12-row-inspect).status -ne 'invalid'){throw 'Unsafe row-insertion metadata accepted'};$cases++}

 $inputCase=[ordered]@{};foreach($key in $row.Keys){$inputCase[$key]=$row[$key]};$inputCase.mode='gtgt-annex12-input-inspect';$inputCase.stage='gtgt-annex12-input-inspected';$inputCase.annex12InputActionCount=14
 $inputCase.annex12InputReadOnlyIdentityMatched=$true
 $inputCase.annex12InputIdentityMatched=$true
 $inputCase.annex12InputTypesMatched=$true
 $inputCase.annex12InputGeographyMatched=$true
 $inputCase.annex12InputTaxAuthoritiesMatched=$true
 $inputCase.annex12InputPercentagesMatched=$true
 $inputCase.annex12InputZeroTaxMatched=$true
 $inputCase | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $file -Encoding UTF8
 if((Get-HtkkSafeGuiReferenceResult -ResultPath $file -ExpectedMode gtgt-annex12-input-inspect).status -ne 'valid'){throw 'Bounded annex input result rejected'};$cases++
 $inputCase.mode='gtgt-annex12-row-inspect';$inputCase | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $file -Encoding UTF8
 if((Get-HtkkSafeGuiReferenceResult -ResultPath $file -ExpectedMode gtgt-annex12-row-inspect).status -ne 'invalid'){throw 'Annex inputs leaked into row-only mode'};$cases++
 $inputCase.mode='gtgt-annex12-input-inspect'
 foreach($pair in @(@('annex12InputActionCount',15),@('annex12InputIdentityMatched','PRIVATE'))){$unsafe=[ordered]@{};foreach($key in $inputCase.Keys){$unsafe[$key]=$inputCase[$key]};$unsafe[$pair[0]]=$pair[1];$unsafe | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $file -Encoding UTF8;if((Get-HtkkSafeGuiReferenceResult -ResultPath $file -ExpectedMode gtgt-annex12-input-inspect).status -ne 'invalid'){throw 'Unsafe annex input result accepted'};$cases++}

 $annexExport=[ordered]@{};foreach($key in $inputCase.Keys){$annexExport[$key]=$inputCase[$key]};$annexExport.mode='gtgt-annex12-export-inspect';$annexExport.stage='gtgt-annex12-export-inspected'
 $annexExport.annex12ExportMainZeroMatched=$true
 $annexExport.annex12ExportShapeMatched=$true
 $annexExport.annex12ExportSchemaVerified=$true
 $annexExport | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $file -Encoding UTF8
 if((Get-HtkkSafeGuiReferenceResult -ResultPath $file -ExpectedMode gtgt-annex12-export-inspect).status -ne 'valid'){throw 'Bounded annex export rejected'};$cases++
 foreach($key in @('annex12ExportMainZeroMatched','annex12ExportShapeMatched','annex12ExportSchemaVerified')){$bad=[ordered]@{};foreach($name in $annexExport.Keys){$bad[$name]=$annexExport[$name]};$bad[$key]='PRIVATE';$bad | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $file -Encoding UTF8;if((Get-HtkkSafeGuiReferenceResult -ResultPath $file -ExpectedMode gtgt-annex12-export-inspect).status -ne 'invalid'){throw 'Unsafe annex export accepted'};$cases++}
 $numeric=[ordered]@{};foreach($key in $inputCase.Keys){$numeric[$key]=$inputCase[$key]};$numeric.mode='gtgt-annex12-numeric-inspect';$numeric.stage='gtgt-annex12-numeric-inspected';$numeric.annex12NumericActionCount=5;$numeric.annex12NumericCaseCount=3
 $numeric.annex12NumericSnapshots='1,100,0,0,50,0.5,1,0,50,0.5,1,1;7,100,0,0,33.33,2.3331,7,0,66.67,4.6669,7,7;99999999999999,100,0,0,33.33,33329999999999.6667,99999999999999,0,66.67,66669999999999.3333,99999999999999,99999999999999'
 $numeric.annex12NumericTextSnapshots=(1..3 | ForEach-Object { '1|100,00|0|0|50,00|1|1|0|50,00|1|1|1' }) -join ';'
 $numeric.annex12NumericTypeSnapshots=(1..3 | ForEach-Object { ((1..12 | ForEach-Object { 'double' }) -join '|') }) -join ';'
 $numeric.annex12NumericDoubleBits=(1..3 | ForEach-Object { ((1..12 | ForEach-Object { '3FF0000000000000' }) -join '|') }) -join ';'

 $numeric | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $file -Encoding UTF8
 if((Get-HtkkSafeGuiReferenceResult -ResultPath $file -ExpectedMode gtgt-annex12-numeric-inspect).status -ne 'valid'){throw 'Bounded numeric observations rejected'};$cases++
 foreach($stage in @('gtgt-annex12-numeric-format-checking','gtgt-annex12-numeric-editor-ready','gtgt-annex12-numeric-committed','gtgt-annex12-numeric-value-mismatch')){$numeric.stage=$stage;$numeric | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $file -Encoding UTF8;if((Get-HtkkSafeGuiReferenceResult -ResultPath $file -ExpectedMode gtgt-annex12-numeric-inspect).status -ne 'valid'){throw 'Bounded numeric diagnostic rejected'};$cases++}
 $numeric.stage='gtgt-annex12-numeric-inspected'
 foreach($pair in @(@('annex12NumericActionCount',6),@('annex12NumericCaseCount',4),@('annex12NumericCaseCount',2),@('annex12NumericSnapshots','PRIVATE'),@('annex12NumericSnapshots','1,NaN'),@('annex12NumericSnapshots','1,Infinity'),@('annex12NumericSnapshots','-1'),@('annex12NumericActionCount','5'))){$bad=[ordered]@{};foreach($key in $numeric.Keys){$bad[$key]=$numeric[$key]};$bad[$pair[0]]=$pair[1];$bad | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $file -Encoding UTF8;if((Get-HtkkSafeGuiReferenceResult -ResultPath $file -ExpectedMode gtgt-annex12-numeric-inspect).status -ne 'invalid'){throw 'Unsafe numeric observations accepted'};$cases++}
 $typed=[ordered]@{};foreach($key in $numeric.Keys){$typed[$key]=$numeric[$key]}
 $typed.annex12NumericTypeSnapshots=(1..3 | ForEach-Object { ((1..12 | ForEach-Object { 'integer' }) -join '|') }) -join ';'
 $typed.annex12NumericDoubleBits=(1..3 | ForEach-Object { '|||||||||||' }) -join ';'
 $typed.annex12NumericTextSnapshots=(1..3 | ForEach-Object { '|||||||||||' }) -join ';'
 $typed | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $file -Encoding UTF8
 if((Get-HtkkSafeGuiReferenceResult -ResultPath $file -ExpectedMode gtgt-annex12-numeric-inspect).status -ne 'valid'){throw 'Non-double or blank numeric display observation rejected'};$cases++
 $typed.annex12NumericDoubleBits=$numeric.annex12NumericDoubleBits;$typed | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $file -Encoding UTF8
 if((Get-HtkkSafeGuiReferenceResult -ResultPath $file -ExpectedMode gtgt-annex12-numeric-inspect).status -ne 'invalid'){throw 'Double bits accepted for non-double original Value'};$cases++
 foreach($pair in @(@('annex12NumericTextSnapshots','PRIVATE'),@('annex12NumericTextSnapshots',("1`n")),@('annex12NumericTypeSnapshots','System.Double'),@('annex12NumericDoubleBits','secret'),@('annex12NumericDoubleBits',''),@('annex12NumericTextSnapshots',1))){$bad=[ordered]@{};foreach($key in $numeric.Keys){$bad[$key]=$numeric[$key]};$bad[$pair[0]]=$pair[1];$bad | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $file -Encoding UTF8;if((Get-HtkkSafeGuiReferenceResult -ResultPath $file -ExpectedMode gtgt-annex12-numeric-inspect).status -ne 'invalid'){throw 'Unsafe numeric display/type/bits accepted'};$cases++}
 $numeric.mode='gtgt-annex12-input-inspect';$numeric.stage='gtgt-annex12-input-inspected';$numeric | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $file -Encoding UTF8
 if((Get-HtkkSafeGuiReferenceResult -ResultPath $file -ExpectedMode gtgt-annex12-input-inspect).status -ne 'invalid'){throw 'Numeric observations accepted outside own mode'};$cases++
 Write-Output "Safe GUI result boundary tests passed: $cases"
}finally{Remove-Item -LiteralPath $directory -Recurse -Force -ErrorAction SilentlyContinue}
