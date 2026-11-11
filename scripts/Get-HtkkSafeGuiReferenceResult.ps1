# Strictly reconstructs a bounded allowlisted result; never exposes raw own/original output.
function Get-HtkkSafeGuiReferenceResult {
 [CmdletBinding()]
 param([Parameter(Mandatory=$true)][string]$ResultPath,[ValidateSet('inspect','profile-save','gtgt-inspect','gtgt-sheet-inspect','gtgt-amendment-inspect','gtgt-amendment-open-inspect','gtgt-annex12-inspect','gtgt-annex12-row-inspect','gtgt-annex12-input-inspect','gtgt-annex12-numeric-inspect','gtgt-annex12-export-inspect','gtgt-annex12-export-nonzero','gtgt-export-inspect','gtgt-roundtrip-inspect','gtgt-web-import-inspect','declaration-web-import-inspect')][string]$ExpectedMode)
 $invalid=[ordered]@{status='unavailable';mode=$ExpectedMode;stage='result-unavailable';runtimeRoundTrip=$false}
 try {
  if(-not(Test-Path -LiteralPath $ResultPath -PathType Leaf)){return $invalid}
  $file=Get-Item -LiteralPath $ResultPath
  if($file.Attributes -band [IO.FileAttributes]::ReparsePoint -or $file.Length -gt 16384 -or $file.Length -lt 2){$invalid.status='invalid';$invalid.stage='result-invalid';return $invalid}
  $value=Get-Content -LiteralPath $ResultPath -Raw -Encoding UTF8 | ConvertFrom-Json -AsHashtable
  $keys=@('annex12NumericTextSnapshots','annex12NumericTypeSnapshots','annex12NumericDoubleBits','annex12NumericActionCount','annex12NumericCaseCount','annex12NumericSnapshots','amendmentOpenLoadedSheets','amendmentOpenCloseInvoked','amendmentOpenPriorClosed','amendmentOpenDefaultsMatched','amendmentOpenConfirmInvoked','amendmentOpenPeriodMatched','amendmentOpenSourcesMatched','amendmentOpenKhbsSheetsObserved','amendmentOpenPriorUnchanged','amendmentOpenKhbsRows','amendmentOpenKhbsColumns','amendmentOpenExplanationRows','amendmentOpenExplanationColumns','annex12ExportMainZeroMatched','annex12ExportShapeMatched','annex12ExportSchemaVerified','annex12NonzeroEditsMatched','annex12NonzeroSecondShapeMatched','annex12NonzeroSecondSchemaVerified','annex12NonzeroExportCount','annex12NonzeroSecondExportBytes','annex12NonzeroSecondExportSha256','annex12WebImportSheetMatched','annex12WebBaselineSchemaVerified','annex12WebReexportSchemaVerified','annex12WebImportGroupCount','annex12WebImportRowCount','annex12WebImportDisplayEmptyMask','annex12WebHeadAuthorityRestored','annex12WebHeadAuthorityRepairCount','annex12WebHeadAuthorityFailureMask','annex12WebHeadAuthorityComboMask','annex12InputReadOnlyIdentityMatched','annex12InputIdentityMatched','annex12InputTypesMatched','annex12InputGeographyMatched','annex12InputTaxAuthoritiesMatched','annex12InputPercentagesMatched','annex12InputZeroTaxMatched','annex12InputActionCount','amendmentPriorSaveInvoked','amendmentPriorSaveSuccessAcknowledged','amendmentPriorDirtyCleared','amendmentPriorFileFresh','amendmentPriorFileScopeMatched','amendmentPriorXmlParsed','amendmentPriorMoneyZero','amendmentPriorSavedMoneyZero','amendmentLifecycleVerified','amendmentPriorFileBytes','amendmentPriorFileSha256','amendmentPriorSavedMoneyCount','format','mode','stage','failureCategory','editorKind','runtime','sourcePinsVerified','visibleForms','spreadCount','sheetRows','sheetColumns','mstBoxesMatched','initialRequiredTextBlank','editingApiAvailable','performedInputCount','originalSaveInvoked','savedHeaderExists','savedHeaderChecksMatched','savedHeaderCheckedFieldCount','saveDialogKind','savedHeaderMismatchMask','profileClosed','mainMenuObserved','d1MenuClicked','gtgtPeriodObserved','menuRowCount','menuClickCount','periodControlCount','periodControls','periodYearMonthMatched','periodFirstDeclarationMatched','periodActivityMatched','periodGeographyMatched','periodNoAnnexMatched','periodConfirmInvoked','gtgtWorkbookPinsVerified','gtgtMenuVersionMatched','gtgtPeriodModelMatched','gtgtSheetObserved','gtgtSheetNameMatched','gtgtDimensionsMatched','gtgtIdentityMatched','gtgtCt21Ready','gtgtCt21CaseMatched','gtgtCt21ConfirmationMatched','gtgtCt21LocksMatched','gtgtCt21BeforeExportMatched','gtgtCt21AfterImportMatched','gtgtCt21UncheckMatched','gtgtSignatureReady','gtgtMonetaryZero','periodAnnex12Matched','annex12SourcePinsMatched','annex12SheetObserved','annex12StructureMatched','annex12GroupMetadataMatched','annex12SttMatched','annex12LocksMatched','annex12SelectionActionCount','annex12SheetRows','annex12SheetColumns','annex12NumericCount','annex12NumericEmptyMask','annex12NumericNonzeroMask','annex12GroupCount','annex12FirstGroupId','annex12FirstGroupRows','annex12RowTabClickInvoked','annex12F5Visible','annex12F5Invoked','annex12RowBeforeMatched','annex12RowAfterMatched','annex12RowSttMatched','annex12RowLocksMatched','annex12RowBeforeRows','annex12RowAfterRows','annex12RowBeforeGroupRows','annex12RowAfterGroupRows','annex12RowAfterGroupId','annex12RowInsertActionCount','annexSelectedCount','gtgtSheetRows','gtgtSheetColumns','gtgtSheetCount','gtgtEmptyMonetaryCount','exportCommandInvoked','exportSelectorMatched','exportButtonInvoked','exportDialogMatched','exportDestinationFresh','exportDialogSubmitted','exportFileExists','exportXmlRootMatched','exportSyntheticIdentityMatched','exportSuccessAcknowledged','exportSchemaPinnedVerified','exportFilenameKeyboardCommitted','exportFilenameParentKind','exportOriginalPathMatched','exportOriginalPathKind','exportScopedFileCount','exportScopedXmlCount','exportBytes','exportSha256','exportRejectedMessageId','importRejectedMessageId','roundtripImportCommandInvoked','roundtripImportDialogMatched','roundtripImportKeyboardCommitted','roundtripImportDialogSubmitted','roundtripImportPathMatched','roundtripImportSheetMatched','roundtripImportSucceeded','roundtripReexportCommandInvoked','roundtripReexportSucceeded','roundtripXmlExactMatched','roundtripImportCheckedMoneyCount','roundtripReexportBytes','roundtripReexportSha256','gtgtCt42BeforeExportObserved','gtgtCt42LockedBeforeExport','gtgtCt42AfterImportObserved','gtgtCt42LockedAfterImport','gtgtAutoCalculationReady','gtgtBusinessInstanceMatched','gtgtCaseMoneyMatched','gtgtCt42Locked','webTaxValuesMatched','webCreationDateMatchedNativeBaseline','webServiceIdentityMatched','webInputVerified','webImportInputSha256','webSourceSha','webTaxLeafCount','webCaseId','webCaseEditCount','gtgtCaseMoneyCount','gtgtCaseMismatchMask','gtgtCaseNonzeroMask','declarationMenuClicked','declarationPeriodObserved','declarationPeriodMatched','declarationAnnexMatched','declarationSheetObserved','declarationIdentityMatched','declarationSourcePinsMatched','declarationImportSheetMatched','declarationSchemaValid','declarationServiceIdentityMatched','declarationCreationDateValid','declarationTreeMatched','declarationPeriodRejectedMessageId','declarationAnnexSelectedCount','declarationSheetCount','declarationCellCheckCount','declarationCellMismatchMask','declarationCellLockedMask','declarationXmlCheckCount','declarationXmlMismatchMask','declarationTreeMismatchMask','declarationTreeLeafCount','declarationInvalidSheetMask','declarationInvalidCellCount','declarationInvalidCell1','declarationInvalidCell2','declarationInvalidCell3','declarationInvalidCell4','declarationEntryMethodPinsMatched','declarationEntryCatalogueMatched','declarationEntryChoiceMatched','declarationEntryLocksMatched','declarationEntryRowsMatched','declarationEntryValuesMatched','declarationEntrySignerMatched','declarationEntrySigningDateLocked','declarationEntrySheetMatched','declarationEntryPlannedCount','declarationEntryActionCount','declarationEntryFailureCode','declarationEntryMethodPinMask','declarationEntryLockBeforeMask','declarationEntryLockAfterMask','declarationEntryLockFinalMask','declarationEntryRowsBefore','declarationEntryRowsAfter','declarationEntryRowInsertCount','declarationEntryMismatchMask','declarationEntryLockedMask','declarationEntryCellTypeMismatchMask','declarationEntryCombo1Mask','declarationEntryCombo2Mask','declarationEntryDateTextMask','controlKinds','realTaxpayerDataUsed','runtimeRoundTrip','webSigningDateEdited','webSigningDateReady','webSigningDateLocked','webSigningDateCellKind','annex12LifecycleMatched','annex12LifecycleActionCount','annex12LifecycleEditCount','annex12LifecycleObservedMask')
  if($value -isnot [Collections.IDictionary] -or $value.Count -ne $keys.Count){throw 'invalid'}
  foreach($key in $keys){if(@($value.Keys) -cnotcontains $key){throw 'invalid'}}
  $stages=@('gtgt-export-filename-focus-waiting','gtgt-export-filename-focus-timeout','gtgt-export-filename-keyboard-focused','gtgt-export-filename-keyboard-selected','gtgt-export-filename-keyboard-typed','gtgt-import-filename-focus-waiting','gtgt-import-filename-focus-timeout','gtgt-import-filename-keyboard-focused','gtgt-import-filename-keyboard-selected','gtgt-import-filename-keyboard-typed','gtgt-annex12-numeric-format-checking','gtgt-annex12-numeric-editor-ready','gtgt-annex12-numeric-committed','gtgt-annex12-numeric-value-mismatch','gtgt-annex12-numeric-editing','gtgt-annex12-numeric-observing','gtgt-annex12-numeric-inspected','gtgt-amendment-open-owner-waiting','gtgt-amendment-open-grid-waiting','gtgt-amendment-open-ready-waiting','gtgt-amendment-open-workbook-waiting','gtgt-amendment-open-main-waiting','gtgt-amendment-prior-close-waiting','gtgt-amendment-defaults-selecting','gtgt-amendment-open-confirm-invoking','gtgt-amendment-open-inspected','gtgt-amendment-open-khbs-observing','gtgt-amendment-open-sheet-waiting','gtgt-amendment-prior-close-invoking','gtgt-amendment-prior-closed','gtgt-annex12-export-main-checked','gtgt-annex12-export-validating','gtgt-annex12-export-inspected','gtgt-annex12-nonzero-editing','gtgt-annex12-nonzero-reexport-invoking','gtgt-annex12-export-nonzero-inspected','gtgt-annex12-web-import-checking','gtgt-annex12-web-schema-validating','gtgt-amendment-save-modal-observed','gtgt-amendment-save-modal-content-checking','gtgt-amendment-save-modal-button-checking','gtgt-amendment-save-modal-matched','gtgt-amendment-prior-file-enumerating','gtgt-amendment-prior-file-missing','gtgt-amendment-prior-file-not-unique','gtgt-amendment-prior-file-size-checking','gtgt-amendment-prior-file-parsing','gtgt-amendment-prior-money-checking','gtgt-annex12-input-editing','gtgt-annex12-input-inspected','gtgt-annex12-tab-clicking','gtgt-annex12-f5-invoking','gtgt-annex12-row-inspected','not-started','gtgt-annex12-inspected','gtgt-annex12-sheet-metadata','gtgt-annex12-table-metadata','gtgt-annex12-row-metadata','source-or-runtime-not-matched','fixture-preexists','waiting-for-profile','initialization-unavailable','profile-wait-timeout','profile-controls-not-yet-unique','profile-dimensions-unmatched','fresh-synthetic-profile-not-established','profile-inspected','editing-api-unavailable','profile-province-code-unmatched','profile-ward-code-unmatched','profile-taxhead-code-unmatched','profile-taxlocal-code-unmatched','waiting-for-profile-save-permit','edit-name','edit-province','edit-ward','edit-address','edit-signer','edit-tax-authority-head','edit-tax-authority-local','original-save-invoking','success-modal-acknowledged','original-profile-saved-verified','original-profile-save-not-verified','profile-close-invoking','waiting-profile-close-ready','waiting-profile-close','gtgt-profile-owner-not-matched','waiting-main-menu','gtgt-profile-preconditions-not-matched','gtgt-menu-spread-not-yet-unique','gtgt-menu-id-not-unique','gtgt-menu-target-hidden','gtgt-menu-click-101','gtgt-menu-click-101_1','gtgt-menu-click-D1','waiting-gtgt-period','gtgt-period-inspected','gtgt-period-configuring','gtgt-period-province-selecting','gtgt-period-ward-selecting','gtgt-period-taxhead-selecting','gtgt-period-taxlocal-selecting','gtgt-period-activity-selecting','gtgt-period-inputs-not-matched','gtgt-period-confirm-invoking','waiting-gtgt-sheet','gtgt-sheet-inspected','gtgt-original-declaration-save-invoking','gtgt-original-declaration-save-success','gtgt-original-declaration-saved-inspected','gtgt-sheet-contract-not-matched','gtgt-export-command-invoking','gtgt-export-original-message-rejected','gtgt-export-file-dialog-waiting','gtgt-export-original-writing','gtgt-export-filename-keyboard-editing','gtgt-export-success-file-checking','gtgt-export-inspected','gtgt-import-ready-waiting','gtgt-import-file-dialog-waiting','gtgt-import-filename-keyboard-editing','gtgt-import-original-reading','gtgt-import-original-message-rejected','gtgt-import-success-sheet-checking','gtgt-reexport-ready-waiting','gtgt-reexport-command-invoking','gtgt-roundtrip-inspected','gtgt-web-input-checking','gtgt-web-import-ready-waiting','gtgt-web-import-inspected','gtgt-case-editing','gtgt-noactivity-checkbox-activating','gtgt-noactivity-confirming','gtgt-noactivity-checkbox-unchecking','gtgt-annex12-lifecycle-inspecting','declaration-profile-preconditions-not-matched','declaration-menu-waiting','declaration-menu-click','declaration-menu-id-not-unique','declaration-menu-target-hidden','declaration-period-waiting','declaration-period-configuring','declaration-period-annex-selecting','declaration-period-inputs-not-matched','declaration-period-confirm-invoking','declaration-sheet-waiting','declaration-period-original-message-rejected','declaration-sheet-contract-not-matched','declaration-web-input-checking','declaration-import-ready-waiting','declaration-import-command-invoking','declaration-import-original-message-rejected','declaration-import-sheet-checking','declaration-import-sheet-not-matched','declaration-export-ready-waiting','declaration-export-command-invoking','declaration-export-file-dialog-waiting','declaration-export-original-message-rejected','declaration-export-validating','declaration-export-not-matched','declaration-web-import-inspected','declaration-entry-ready-waiting','declaration-entry-pins-checking','declaration-entry-choice-invoking','declaration-entry-rows-inserting','declaration-entry-editing','declaration-entry-sheet-checking','declaration-entry-not-matched','declaration-original-entry-exported')
  # BEGIN GENERATED RESULT CONTRACT - do not edit
  if($value['annex12NumericTextSnapshots'] -isnot [string] -or $value['annex12NumericTextSnapshots'].Length -gt 4096){throw 'invalid'}
  if($value['annex12NumericTypeSnapshots'] -isnot [string] -or $value['annex12NumericTypeSnapshots'].Length -gt 4096){throw 'invalid'}
  if($value['annex12NumericDoubleBits'] -isnot [string] -or $value['annex12NumericDoubleBits'].Length -gt 4096){throw 'invalid'}
  if(($value['annex12NumericActionCount'] -isnot [int] -and $value['annex12NumericActionCount'] -isnot [long]) -or $value['annex12NumericActionCount'] -lt 0 -or $value['annex12NumericActionCount'] -gt 5){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-annex12-numeric-inspect','gtgt-annex12-export-nonzero')) -and $value['annex12NumericActionCount'] -cne 0){throw 'invalid'}
  if(($value['annex12NumericCaseCount'] -isnot [int] -and $value['annex12NumericCaseCount'] -isnot [long]) -or $value['annex12NumericCaseCount'] -lt 0 -or $value['annex12NumericCaseCount'] -gt 3){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-annex12-numeric-inspect')) -and $value['annex12NumericCaseCount'] -cne 0){throw 'invalid'}
  if($value['annex12NumericSnapshots'] -isnot [string] -or $value['annex12NumericSnapshots'].Length -gt 4096){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-annex12-numeric-inspect')) -and $value['annex12NumericSnapshots'] -cne ''){throw 'invalid'}
  if(($value['amendmentOpenLoadedSheets'] -isnot [int] -and $value['amendmentOpenLoadedSheets'] -isnot [long]) -or $value['amendmentOpenLoadedSheets'] -lt 0 -or $value['amendmentOpenLoadedSheets'] -gt 32){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-amendment-open-inspect')) -and $value['amendmentOpenLoadedSheets'] -cne 0){throw 'invalid'}
  if($value['amendmentOpenCloseInvoked'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-amendment-open-inspect')) -and $value['amendmentOpenCloseInvoked'] -cne $false){throw 'invalid'}
  if($value['amendmentOpenPriorClosed'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-amendment-open-inspect')) -and $value['amendmentOpenPriorClosed'] -cne $false){throw 'invalid'}
  if($value['amendmentOpenDefaultsMatched'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-amendment-open-inspect')) -and $value['amendmentOpenDefaultsMatched'] -cne $false){throw 'invalid'}
  if($value['amendmentOpenConfirmInvoked'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-amendment-open-inspect')) -and $value['amendmentOpenConfirmInvoked'] -cne $false){throw 'invalid'}
  if($value['amendmentOpenPeriodMatched'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-amendment-open-inspect')) -and $value['amendmentOpenPeriodMatched'] -cne $false){throw 'invalid'}
  if($value['amendmentOpenSourcesMatched'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-amendment-open-inspect')) -and $value['amendmentOpenSourcesMatched'] -cne $false){throw 'invalid'}
  if($value['amendmentOpenKhbsSheetsObserved'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-amendment-open-inspect')) -and $value['amendmentOpenKhbsSheetsObserved'] -cne $false){throw 'invalid'}
  if($value['amendmentOpenPriorUnchanged'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-amendment-open-inspect')) -and $value['amendmentOpenPriorUnchanged'] -cne $false){throw 'invalid'}
  if(($value['amendmentOpenKhbsRows'] -isnot [int] -and $value['amendmentOpenKhbsRows'] -isnot [long]) -or $value['amendmentOpenKhbsRows'] -lt 0 -or $value['amendmentOpenKhbsRows'] -gt 10000){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-amendment-open-inspect')) -and $value['amendmentOpenKhbsRows'] -cne 0){throw 'invalid'}
  if(($value['amendmentOpenKhbsColumns'] -isnot [int] -and $value['amendmentOpenKhbsColumns'] -isnot [long]) -or $value['amendmentOpenKhbsColumns'] -lt 0 -or $value['amendmentOpenKhbsColumns'] -gt 512){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-amendment-open-inspect')) -and $value['amendmentOpenKhbsColumns'] -cne 0){throw 'invalid'}
  if(($value['amendmentOpenExplanationRows'] -isnot [int] -and $value['amendmentOpenExplanationRows'] -isnot [long]) -or $value['amendmentOpenExplanationRows'] -lt 0 -or $value['amendmentOpenExplanationRows'] -gt 10000){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-amendment-open-inspect')) -and $value['amendmentOpenExplanationRows'] -cne 0){throw 'invalid'}
  if(($value['amendmentOpenExplanationColumns'] -isnot [int] -and $value['amendmentOpenExplanationColumns'] -isnot [long]) -or $value['amendmentOpenExplanationColumns'] -lt 0 -or $value['amendmentOpenExplanationColumns'] -gt 512){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-amendment-open-inspect')) -and $value['amendmentOpenExplanationColumns'] -cne 0){throw 'invalid'}
  if($value['annex12ExportMainZeroMatched'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-annex12-export-inspect','gtgt-annex12-export-nonzero','gtgt-web-import-inspect')) -and $value['annex12ExportMainZeroMatched'] -cne $false){throw 'invalid'}
  if($value['annex12ExportShapeMatched'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-annex12-export-inspect','gtgt-annex12-export-nonzero')) -and $value['annex12ExportShapeMatched'] -cne $false){throw 'invalid'}
  if($value['annex12ExportSchemaVerified'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-annex12-export-inspect','gtgt-annex12-export-nonzero')) -and $value['annex12ExportSchemaVerified'] -cne $false){throw 'invalid'}
  if($value['annex12NonzeroEditsMatched'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-annex12-export-nonzero')) -and $value['annex12NonzeroEditsMatched'] -cne $false){throw 'invalid'}
  if($value['annex12NonzeroSecondShapeMatched'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-annex12-export-nonzero')) -and $value['annex12NonzeroSecondShapeMatched'] -cne $false){throw 'invalid'}
  if($value['annex12NonzeroSecondSchemaVerified'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-annex12-export-nonzero')) -and $value['annex12NonzeroSecondSchemaVerified'] -cne $false){throw 'invalid'}
  if(($value['annex12NonzeroExportCount'] -isnot [int] -and $value['annex12NonzeroExportCount'] -isnot [long]) -or $value['annex12NonzeroExportCount'] -lt 0 -or $value['annex12NonzeroExportCount'] -gt 2){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-annex12-export-nonzero')) -and $value['annex12NonzeroExportCount'] -cne 0){throw 'invalid'}
  if(($value['annex12NonzeroSecondExportBytes'] -isnot [int] -and $value['annex12NonzeroSecondExportBytes'] -isnot [long]) -or $value['annex12NonzeroSecondExportBytes'] -lt 0 -or $value['annex12NonzeroSecondExportBytes'] -gt 262144){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-annex12-export-nonzero')) -and $value['annex12NonzeroSecondExportBytes'] -cne 0){throw 'invalid'}
  if($value['annex12NonzeroSecondExportSha256'] -isnot [string] -or ($value['annex12NonzeroSecondExportSha256'] -cne '' -and $value['annex12NonzeroSecondExportSha256'] -cnotmatch '\A[0-9a-f]{64}\z')){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-annex12-export-nonzero')) -and $value['annex12NonzeroSecondExportSha256'] -cne ''){throw 'invalid'}
  if($value['annex12WebImportSheetMatched'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-web-import-inspect')) -and $value['annex12WebImportSheetMatched'] -cne $false){throw 'invalid'}
  if($value['annex12WebBaselineSchemaVerified'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-web-import-inspect')) -and $value['annex12WebBaselineSchemaVerified'] -cne $false){throw 'invalid'}
  if($value['annex12WebReexportSchemaVerified'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-web-import-inspect')) -and $value['annex12WebReexportSchemaVerified'] -cne $false){throw 'invalid'}
  if(($value['annex12WebImportGroupCount'] -isnot [int] -and $value['annex12WebImportGroupCount'] -isnot [long]) -or $value['annex12WebImportGroupCount'] -lt 0 -or $value['annex12WebImportGroupCount'] -gt 3){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-web-import-inspect')) -and $value['annex12WebImportGroupCount'] -cne 0){throw 'invalid'}
  if(($value['annex12WebImportRowCount'] -isnot [int] -and $value['annex12WebImportRowCount'] -isnot [long]) -or $value['annex12WebImportRowCount'] -lt 0 -or $value['annex12WebImportRowCount'] -gt 10){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-web-import-inspect')) -and $value['annex12WebImportRowCount'] -cne 0){throw 'invalid'}
  if(($value['annex12WebImportDisplayEmptyMask'] -isnot [int] -and $value['annex12WebImportDisplayEmptyMask'] -isnot [long]) -or $value['annex12WebImportDisplayEmptyMask'] -lt 0 -or $value['annex12WebImportDisplayEmptyMask'] -gt 33554431){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-web-import-inspect')) -and $value['annex12WebImportDisplayEmptyMask'] -cne 0){throw 'invalid'}
  if($value['annex12WebHeadAuthorityRestored'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-web-import-inspect')) -and $value['annex12WebHeadAuthorityRestored'] -cne $false){throw 'invalid'}
  if(($value['annex12WebHeadAuthorityRepairCount'] -isnot [int] -and $value['annex12WebHeadAuthorityRepairCount'] -isnot [long]) -or $value['annex12WebHeadAuthorityRepairCount'] -lt 0 -or $value['annex12WebHeadAuthorityRepairCount'] -gt 20){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-web-import-inspect')) -and $value['annex12WebHeadAuthorityRepairCount'] -cne 0){throw 'invalid'}
  if(($value['annex12WebHeadAuthorityFailureMask'] -isnot [int] -and $value['annex12WebHeadAuthorityFailureMask'] -isnot [long]) -or $value['annex12WebHeadAuthorityFailureMask'] -lt 0 -or $value['annex12WebHeadAuthorityFailureMask'] -gt 4095){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-web-import-inspect')) -and $value['annex12WebHeadAuthorityFailureMask'] -cne 0){throw 'invalid'}
  if(($value['annex12WebHeadAuthorityComboMask'] -isnot [int] -and $value['annex12WebHeadAuthorityComboMask'] -isnot [long]) -or $value['annex12WebHeadAuthorityComboMask'] -lt 0 -or $value['annex12WebHeadAuthorityComboMask'] -gt 2047){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-web-import-inspect')) -and $value['annex12WebHeadAuthorityComboMask'] -cne 0){throw 'invalid'}
  if($value['annex12InputReadOnlyIdentityMatched'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-annex12-input-inspect','gtgt-annex12-numeric-inspect','gtgt-annex12-export-inspect','gtgt-annex12-export-nonzero','gtgt-web-import-inspect')) -and $value['annex12InputReadOnlyIdentityMatched'] -cne $false){throw 'invalid'}
  if($value['annex12InputIdentityMatched'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-annex12-input-inspect','gtgt-annex12-numeric-inspect','gtgt-annex12-export-inspect','gtgt-annex12-export-nonzero','gtgt-web-import-inspect')) -and $value['annex12InputIdentityMatched'] -cne $false){throw 'invalid'}
  if($value['annex12InputTypesMatched'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-annex12-input-inspect','gtgt-annex12-numeric-inspect','gtgt-annex12-export-inspect','gtgt-annex12-export-nonzero','gtgt-web-import-inspect')) -and $value['annex12InputTypesMatched'] -cne $false){throw 'invalid'}
  if($value['annex12InputGeographyMatched'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-annex12-input-inspect','gtgt-annex12-numeric-inspect','gtgt-annex12-export-inspect','gtgt-annex12-export-nonzero','gtgt-web-import-inspect')) -and $value['annex12InputGeographyMatched'] -cne $false){throw 'invalid'}
  if($value['annex12InputTaxAuthoritiesMatched'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-annex12-input-inspect','gtgt-annex12-numeric-inspect','gtgt-annex12-export-inspect','gtgt-annex12-export-nonzero','gtgt-web-import-inspect')) -and $value['annex12InputTaxAuthoritiesMatched'] -cne $false){throw 'invalid'}
  if($value['annex12InputPercentagesMatched'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-annex12-input-inspect','gtgt-annex12-numeric-inspect','gtgt-annex12-export-inspect','gtgt-annex12-export-nonzero','gtgt-web-import-inspect')) -and $value['annex12InputPercentagesMatched'] -cne $false){throw 'invalid'}
  if($value['annex12InputZeroTaxMatched'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-annex12-input-inspect','gtgt-annex12-numeric-inspect','gtgt-annex12-export-inspect','gtgt-annex12-export-nonzero','gtgt-web-import-inspect')) -and $value['annex12InputZeroTaxMatched'] -cne $false){throw 'invalid'}
  if(($value['annex12InputActionCount'] -isnot [int] -and $value['annex12InputActionCount'] -isnot [long]) -or $value['annex12InputActionCount'] -lt 0 -or $value['annex12InputActionCount'] -gt 14){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-annex12-input-inspect','gtgt-annex12-numeric-inspect','gtgt-annex12-export-inspect','gtgt-annex12-export-nonzero','gtgt-web-import-inspect')) -and $value['annex12InputActionCount'] -cne 0){throw 'invalid'}
  if($value['amendmentPriorSaveInvoked'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-amendment-inspect','gtgt-amendment-open-inspect')) -and $value['amendmentPriorSaveInvoked'] -cne $false){throw 'invalid'}
  if($value['amendmentPriorSaveSuccessAcknowledged'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-amendment-inspect','gtgt-amendment-open-inspect')) -and $value['amendmentPriorSaveSuccessAcknowledged'] -cne $false){throw 'invalid'}
  if($value['amendmentPriorDirtyCleared'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-amendment-inspect','gtgt-amendment-open-inspect')) -and $value['amendmentPriorDirtyCleared'] -cne $false){throw 'invalid'}
  if($value['amendmentPriorFileFresh'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-amendment-inspect','gtgt-amendment-open-inspect')) -and $value['amendmentPriorFileFresh'] -cne $false){throw 'invalid'}
  if($value['amendmentPriorFileScopeMatched'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-amendment-inspect','gtgt-amendment-open-inspect')) -and $value['amendmentPriorFileScopeMatched'] -cne $false){throw 'invalid'}
  if($value['amendmentPriorXmlParsed'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-amendment-inspect','gtgt-amendment-open-inspect')) -and $value['amendmentPriorXmlParsed'] -cne $false){throw 'invalid'}
  if($value['amendmentPriorMoneyZero'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-amendment-inspect','gtgt-amendment-open-inspect')) -and $value['amendmentPriorMoneyZero'] -cne $false){throw 'invalid'}
  if($value['amendmentPriorSavedMoneyZero'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-amendment-inspect','gtgt-amendment-open-inspect')) -and $value['amendmentPriorSavedMoneyZero'] -cne $false){throw 'invalid'}
  if($value['amendmentLifecycleVerified'] -isnot [bool]){throw 'invalid'}
  if(($true) -and $value['amendmentLifecycleVerified'] -cne $false){throw 'invalid'}
  if(($value['amendmentPriorFileBytes'] -isnot [int] -and $value['amendmentPriorFileBytes'] -isnot [long]) -or $value['amendmentPriorFileBytes'] -lt 0 -or $value['amendmentPriorFileBytes'] -gt 262144){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-amendment-inspect','gtgt-amendment-open-inspect')) -and $value['amendmentPriorFileBytes'] -cne 0){throw 'invalid'}
  if($value['amendmentPriorFileSha256'] -isnot [string] -or ($value['amendmentPriorFileSha256'] -cne '' -and $value['amendmentPriorFileSha256'] -cnotmatch '\A[0-9a-f]{64}\z')){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-amendment-inspect','gtgt-amendment-open-inspect')) -and $value['amendmentPriorFileSha256'] -cne ''){throw 'invalid'}
  if(($value['amendmentPriorSavedMoneyCount'] -isnot [int] -and $value['amendmentPriorSavedMoneyCount'] -isnot [long]) -or $value['amendmentPriorSavedMoneyCount'] -lt 0 -or $value['amendmentPriorSavedMoneyCount'] -gt 27){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-amendment-inspect','gtgt-amendment-open-inspect')) -and $value['amendmentPriorSavedMoneyCount'] -cne 0){throw 'invalid'}
  if($value['format'] -isnot [string] -or $value['format'] -cnotin @('htkk-gui-reference-automation-v1')){throw 'invalid'}
  if($value['mode'] -isnot [string] -or $value['mode'] -cnotin @('inspect','profile-save','gtgt-inspect','gtgt-sheet-inspect','gtgt-amendment-inspect','gtgt-amendment-open-inspect','gtgt-annex12-inspect','gtgt-annex12-row-inspect','gtgt-annex12-input-inspect','gtgt-annex12-numeric-inspect','gtgt-annex12-export-inspect','gtgt-annex12-export-nonzero','gtgt-export-inspect','gtgt-roundtrip-inspect','gtgt-web-import-inspect','declaration-web-import-inspect')){throw 'invalid'}
  if($value['stage'] -isnot [string] -or $value['stage'] -cnotin @('gtgt-export-filename-focus-waiting','gtgt-export-filename-focus-timeout','gtgt-export-filename-keyboard-focused','gtgt-export-filename-keyboard-selected','gtgt-export-filename-keyboard-typed','gtgt-import-filename-focus-waiting','gtgt-import-filename-focus-timeout','gtgt-import-filename-keyboard-focused','gtgt-import-filename-keyboard-selected','gtgt-import-filename-keyboard-typed','gtgt-annex12-numeric-format-checking','gtgt-annex12-numeric-editor-ready','gtgt-annex12-numeric-committed','gtgt-annex12-numeric-value-mismatch','gtgt-annex12-numeric-editing','gtgt-annex12-numeric-observing','gtgt-annex12-numeric-inspected','gtgt-amendment-open-owner-waiting','gtgt-amendment-open-grid-waiting','gtgt-amendment-open-ready-waiting','gtgt-amendment-open-workbook-waiting','gtgt-amendment-open-main-waiting','gtgt-amendment-prior-close-waiting','gtgt-amendment-defaults-selecting','gtgt-amendment-open-confirm-invoking','gtgt-amendment-open-inspected','gtgt-amendment-open-khbs-observing','gtgt-amendment-open-sheet-waiting','gtgt-amendment-prior-close-invoking','gtgt-amendment-prior-closed','gtgt-annex12-export-main-checked','gtgt-annex12-export-validating','gtgt-annex12-export-inspected','gtgt-annex12-nonzero-editing','gtgt-annex12-nonzero-reexport-invoking','gtgt-annex12-export-nonzero-inspected','gtgt-annex12-web-import-checking','gtgt-annex12-web-schema-validating','gtgt-amendment-save-modal-observed','gtgt-amendment-save-modal-content-checking','gtgt-amendment-save-modal-button-checking','gtgt-amendment-save-modal-matched','gtgt-amendment-prior-file-enumerating','gtgt-amendment-prior-file-missing','gtgt-amendment-prior-file-not-unique','gtgt-amendment-prior-file-size-checking','gtgt-amendment-prior-file-parsing','gtgt-amendment-prior-money-checking','gtgt-annex12-input-editing','gtgt-annex12-input-inspected','gtgt-annex12-tab-clicking','gtgt-annex12-f5-invoking','gtgt-annex12-row-inspected','not-started','gtgt-annex12-inspected','gtgt-annex12-sheet-metadata','gtgt-annex12-table-metadata','gtgt-annex12-row-metadata','source-or-runtime-not-matched','fixture-preexists','waiting-for-profile','initialization-unavailable','profile-wait-timeout','profile-controls-not-yet-unique','profile-dimensions-unmatched','fresh-synthetic-profile-not-established','profile-inspected','editing-api-unavailable','profile-province-code-unmatched','profile-ward-code-unmatched','profile-taxhead-code-unmatched','profile-taxlocal-code-unmatched','waiting-for-profile-save-permit','edit-name','edit-province','edit-ward','edit-address','edit-signer','edit-tax-authority-head','edit-tax-authority-local','original-save-invoking','success-modal-acknowledged','original-profile-saved-verified','original-profile-save-not-verified','profile-close-invoking','waiting-profile-close-ready','waiting-profile-close','gtgt-profile-owner-not-matched','waiting-main-menu','gtgt-profile-preconditions-not-matched','gtgt-menu-spread-not-yet-unique','gtgt-menu-id-not-unique','gtgt-menu-target-hidden','gtgt-menu-click-101','gtgt-menu-click-101_1','gtgt-menu-click-D1','waiting-gtgt-period','gtgt-period-inspected','gtgt-period-configuring','gtgt-period-province-selecting','gtgt-period-ward-selecting','gtgt-period-taxhead-selecting','gtgt-period-taxlocal-selecting','gtgt-period-activity-selecting','gtgt-period-inputs-not-matched','gtgt-period-confirm-invoking','waiting-gtgt-sheet','gtgt-sheet-inspected','gtgt-original-declaration-save-invoking','gtgt-original-declaration-save-success','gtgt-original-declaration-saved-inspected','gtgt-sheet-contract-not-matched','gtgt-export-command-invoking','gtgt-export-original-message-rejected','gtgt-export-file-dialog-waiting','gtgt-export-original-writing','gtgt-export-filename-keyboard-editing','gtgt-export-success-file-checking','gtgt-export-inspected','gtgt-import-ready-waiting','gtgt-import-file-dialog-waiting','gtgt-import-filename-keyboard-editing','gtgt-import-original-reading','gtgt-import-original-message-rejected','gtgt-import-success-sheet-checking','gtgt-reexport-ready-waiting','gtgt-reexport-command-invoking','gtgt-roundtrip-inspected','gtgt-web-input-checking','gtgt-web-import-ready-waiting','gtgt-web-import-inspected','gtgt-case-editing','gtgt-noactivity-checkbox-activating','gtgt-noactivity-confirming','gtgt-noactivity-checkbox-unchecking','gtgt-annex12-lifecycle-inspecting','declaration-profile-preconditions-not-matched','declaration-menu-waiting','declaration-menu-click','declaration-menu-id-not-unique','declaration-menu-target-hidden','declaration-period-waiting','declaration-period-configuring','declaration-period-annex-selecting','declaration-period-inputs-not-matched','declaration-period-confirm-invoking','declaration-sheet-waiting','declaration-period-original-message-rejected','declaration-sheet-contract-not-matched','declaration-web-input-checking','declaration-import-ready-waiting','declaration-import-command-invoking','declaration-import-original-message-rejected','declaration-import-sheet-checking','declaration-import-sheet-not-matched','declaration-export-ready-waiting','declaration-export-command-invoking','declaration-export-file-dialog-waiting','declaration-export-original-message-rejected','declaration-export-validating','declaration-export-not-matched','declaration-web-import-inspected','declaration-entry-ready-waiting','declaration-entry-pins-checking','declaration-entry-choice-invoking','declaration-entry-rows-inserting','declaration-entry-editing','declaration-entry-sheet-checking','declaration-entry-not-matched','declaration-original-entry-exported')){throw 'invalid'}
  if($value['failureCategory'] -isnot [string] -or $value['failureCategory'] -cnotin @('none','reflection-invocation','operation-not-established','argument','com','io','other-standard')){throw 'invalid'}
  if($value['editorKind'] -isnot [string] -or $value['editorKind'] -cnotin @('not-started','combo','text-box','other-control')){throw 'invalid'}
  if($value['runtime'] -isnot [string] -or $value['runtime'] -cnotin @('clr2-x86-custom-reference')){throw 'invalid'}
  if($value['sourcePinsVerified'] -isnot [bool]){throw 'invalid'}
  if(($value['visibleForms'] -isnot [int] -and $value['visibleForms'] -isnot [long]) -or $value['visibleForms'] -lt 0 -or $value['visibleForms'] -gt 64){throw 'invalid'}
  if(($value['spreadCount'] -isnot [int] -and $value['spreadCount'] -isnot [long]) -or $value['spreadCount'] -lt 0 -or $value['spreadCount'] -gt 512){throw 'invalid'}
  if(($value['sheetRows'] -isnot [int] -and $value['sheetRows'] -isnot [long]) -or $value['sheetRows'] -lt 0 -or $value['sheetRows'] -gt 10000){throw 'invalid'}
  if(($value['sheetColumns'] -isnot [int] -and $value['sheetColumns'] -isnot [long]) -or $value['sheetColumns'] -lt 0 -or $value['sheetColumns'] -gt 10000){throw 'invalid'}
  if($value['mstBoxesMatched'] -isnot [bool]){throw 'invalid'}
  if($value['initialRequiredTextBlank'] -isnot [bool]){throw 'invalid'}
  if($value['editingApiAvailable'] -isnot [bool]){throw 'invalid'}
  if(($value['performedInputCount'] -isnot [int] -and $value['performedInputCount'] -isnot [long]) -or $value['performedInputCount'] -lt 0 -or $value['performedInputCount'] -gt 7){throw 'invalid'}
  if($value['originalSaveInvoked'] -isnot [bool]){throw 'invalid'}
  if($value['savedHeaderExists'] -isnot [bool]){throw 'invalid'}
  if($value['savedHeaderChecksMatched'] -isnot [bool]){throw 'invalid'}
  if(($value['savedHeaderCheckedFieldCount'] -isnot [int] -and $value['savedHeaderCheckedFieldCount'] -isnot [long]) -or $value['savedHeaderCheckedFieldCount'] -lt 0 -or $value['savedHeaderCheckedFieldCount'] -gt 8){throw 'invalid'}
  if($value['saveDialogKind'] -isnot [string] -or $value['saveDialogKind'] -cnotin @('not-observed','success-0002','invalid-0015','other-original-message')){throw 'invalid'}
  if(($value['savedHeaderMismatchMask'] -isnot [int] -and $value['savedHeaderMismatchMask'] -isnot [long]) -or $value['savedHeaderMismatchMask'] -lt 0 -or $value['savedHeaderMismatchMask'] -gt 255){throw 'invalid'}
  if($value['profileClosed'] -isnot [bool]){throw 'invalid'}
  if($value['mainMenuObserved'] -isnot [bool]){throw 'invalid'}
  if($value['d1MenuClicked'] -isnot [bool]){throw 'invalid'}
  if($value['gtgtPeriodObserved'] -isnot [bool]){throw 'invalid'}
  if(($value['menuRowCount'] -isnot [int] -and $value['menuRowCount'] -isnot [long]) -or $value['menuRowCount'] -lt 0 -or $value['menuRowCount'] -gt 2048){throw 'invalid'}
  if(($value['menuClickCount'] -isnot [int] -and $value['menuClickCount'] -isnot [long]) -or $value['menuClickCount'] -lt 0 -or $value['menuClickCount'] -gt $(if($ExpectedMode -ceq 'gtgt-amendment-open-inspect'){6}else{3})){throw 'invalid'}
  if(($value['periodControlCount'] -isnot [int] -and $value['periodControlCount'] -isnot [long]) -or $value['periodControlCount'] -lt 0 -or $value['periodControlCount'] -gt 512){throw 'invalid'}
  if($value['periodControls'] -isnot [Collections.IDictionary]){throw 'invalid'}
  if($value['periodYearMonthMatched'] -isnot [bool]){throw 'invalid'}
  if($value['periodFirstDeclarationMatched'] -isnot [bool]){throw 'invalid'}
  if($value['periodActivityMatched'] -isnot [bool]){throw 'invalid'}
  if($value['periodGeographyMatched'] -isnot [bool]){throw 'invalid'}
  if($value['periodNoAnnexMatched'] -isnot [bool]){throw 'invalid'}
  if($value['periodConfirmInvoked'] -isnot [bool]){throw 'invalid'}
  if($value['gtgtWorkbookPinsVerified'] -isnot [bool]){throw 'invalid'}
  if($value['gtgtMenuVersionMatched'] -isnot [bool]){throw 'invalid'}
  if($value['gtgtPeriodModelMatched'] -isnot [bool]){throw 'invalid'}
  if($value['gtgtSheetObserved'] -isnot [bool]){throw 'invalid'}
  if($value['gtgtSheetNameMatched'] -isnot [bool]){throw 'invalid'}
  if($value['gtgtDimensionsMatched'] -isnot [bool]){throw 'invalid'}
  if($value['gtgtIdentityMatched'] -isnot [bool]){throw 'invalid'}
  if($value['gtgtCt21Ready'] -isnot [bool]){throw 'invalid'}
  if($value['gtgtCt21CaseMatched'] -isnot [bool]){throw 'invalid'}
  if($value['gtgtCt21ConfirmationMatched'] -isnot [bool]){throw 'invalid'}
  if($value['gtgtCt21LocksMatched'] -isnot [bool]){throw 'invalid'}
  if($value['gtgtCt21BeforeExportMatched'] -isnot [bool]){throw 'invalid'}
  if($value['gtgtCt21AfterImportMatched'] -isnot [bool]){throw 'invalid'}
  if($value['gtgtCt21UncheckMatched'] -isnot [bool]){throw 'invalid'}
  if($value['gtgtSignatureReady'] -isnot [bool]){throw 'invalid'}
  if($value['gtgtMonetaryZero'] -isnot [bool]){throw 'invalid'}
  if($value['periodAnnex12Matched'] -isnot [bool]){throw 'invalid'}
  if($value['annex12SourcePinsMatched'] -isnot [bool]){throw 'invalid'}
  if($value['annex12SheetObserved'] -isnot [bool]){throw 'invalid'}
  if($value['annex12StructureMatched'] -isnot [bool]){throw 'invalid'}
  if($value['annex12GroupMetadataMatched'] -isnot [bool]){throw 'invalid'}
  if($value['annex12SttMatched'] -isnot [bool]){throw 'invalid'}
  if($value['annex12LocksMatched'] -isnot [bool]){throw 'invalid'}
  if(($value['annex12SelectionActionCount'] -isnot [int] -and $value['annex12SelectionActionCount'] -isnot [long]) -or $value['annex12SelectionActionCount'] -lt 0 -or $value['annex12SelectionActionCount'] -gt 1){throw 'invalid'}
  if(($value['annex12SheetRows'] -isnot [int] -and $value['annex12SheetRows'] -isnot [long]) -or $value['annex12SheetRows'] -lt 0 -or $value['annex12SheetRows'] -gt 10000){throw 'invalid'}
  if(($value['annex12SheetColumns'] -isnot [int] -and $value['annex12SheetColumns'] -isnot [long]) -or $value['annex12SheetColumns'] -lt 0 -or $value['annex12SheetColumns'] -gt 512){throw 'invalid'}
  if(($value['annex12NumericCount'] -isnot [int] -and $value['annex12NumericCount'] -isnot [long]) -or $value['annex12NumericCount'] -lt 0 -or $value['annex12NumericCount'] -gt 8){throw 'invalid'}
  if(($value['annex12NumericEmptyMask'] -isnot [int] -and $value['annex12NumericEmptyMask'] -isnot [long]) -or $value['annex12NumericEmptyMask'] -lt 0 -or $value['annex12NumericEmptyMask'] -gt 255){throw 'invalid'}
  if(($value['annex12NumericNonzeroMask'] -isnot [int] -and $value['annex12NumericNonzeroMask'] -isnot [long]) -or $value['annex12NumericNonzeroMask'] -lt 0 -or $value['annex12NumericNonzeroMask'] -gt 255){throw 'invalid'}
  if(($value['annex12GroupCount'] -isnot [int] -and $value['annex12GroupCount'] -isnot [long]) -or $value['annex12GroupCount'] -lt 0 -or $value['annex12GroupCount'] -gt 512){throw 'invalid'}
  if(($value['annex12FirstGroupId'] -isnot [int] -and $value['annex12FirstGroupId'] -isnot [long]) -or $value['annex12FirstGroupId'] -lt 0 -or $value['annex12FirstGroupId'] -gt 10000){throw 'invalid'}
  if(($value['annex12FirstGroupRows'] -isnot [int] -and $value['annex12FirstGroupRows'] -isnot [long]) -or $value['annex12FirstGroupRows'] -lt 0 -or $value['annex12FirstGroupRows'] -gt 10000){throw 'invalid'}
  if($value['annex12RowTabClickInvoked'] -isnot [bool]){throw 'invalid'}
  if($value['annex12F5Visible'] -isnot [bool]){throw 'invalid'}
  if($value['annex12F5Invoked'] -isnot [bool]){throw 'invalid'}
  if($value['annex12RowBeforeMatched'] -isnot [bool]){throw 'invalid'}
  if($value['annex12RowAfterMatched'] -isnot [bool]){throw 'invalid'}
  if($value['annex12RowSttMatched'] -isnot [bool]){throw 'invalid'}
  if($value['annex12RowLocksMatched'] -isnot [bool]){throw 'invalid'}
  if(($value['annex12RowBeforeRows'] -isnot [int] -and $value['annex12RowBeforeRows'] -isnot [long]) -or $value['annex12RowBeforeRows'] -lt 0 -or $value['annex12RowBeforeRows'] -gt 10000){throw 'invalid'}
  if(($value['annex12RowAfterRows'] -isnot [int] -and $value['annex12RowAfterRows'] -isnot [long]) -or $value['annex12RowAfterRows'] -lt 0 -or $value['annex12RowAfterRows'] -gt 10000){throw 'invalid'}
  if(($value['annex12RowBeforeGroupRows'] -isnot [int] -and $value['annex12RowBeforeGroupRows'] -isnot [long]) -or $value['annex12RowBeforeGroupRows'] -lt 0 -or $value['annex12RowBeforeGroupRows'] -gt 10000){throw 'invalid'}
  if(($value['annex12RowAfterGroupRows'] -isnot [int] -and $value['annex12RowAfterGroupRows'] -isnot [long]) -or $value['annex12RowAfterGroupRows'] -lt 0 -or $value['annex12RowAfterGroupRows'] -gt 10000){throw 'invalid'}
  if(($value['annex12RowAfterGroupId'] -isnot [int] -and $value['annex12RowAfterGroupId'] -isnot [long]) -or $value['annex12RowAfterGroupId'] -lt 0 -or $value['annex12RowAfterGroupId'] -gt 10000){throw 'invalid'}
  if(($value['annex12RowInsertActionCount'] -isnot [int] -and $value['annex12RowInsertActionCount'] -isnot [long]) -or $value['annex12RowInsertActionCount'] -lt 0 -or $value['annex12RowInsertActionCount'] -gt 1){throw 'invalid'}
  if(($value['annexSelectedCount'] -isnot [int] -and $value['annexSelectedCount'] -isnot [long]) -or $value['annexSelectedCount'] -lt 0 -or $value['annexSelectedCount'] -gt 512){throw 'invalid'}
  if(($value['gtgtSheetRows'] -isnot [int] -and $value['gtgtSheetRows'] -isnot [long]) -or $value['gtgtSheetRows'] -lt 0 -or $value['gtgtSheetRows'] -gt 10000){throw 'invalid'}
  if(($value['gtgtSheetColumns'] -isnot [int] -and $value['gtgtSheetColumns'] -isnot [long]) -or $value['gtgtSheetColumns'] -lt 0 -or $value['gtgtSheetColumns'] -gt 10000){throw 'invalid'}
  if(($value['gtgtSheetCount'] -isnot [int] -and $value['gtgtSheetCount'] -isnot [long]) -or $value['gtgtSheetCount'] -lt 0 -or $value['gtgtSheetCount'] -gt 32){throw 'invalid'}
  if(($value['gtgtEmptyMonetaryCount'] -isnot [int] -and $value['gtgtEmptyMonetaryCount'] -isnot [long]) -or $value['gtgtEmptyMonetaryCount'] -lt 0 -or $value['gtgtEmptyMonetaryCount'] -gt 27){throw 'invalid'}
  if($value['exportCommandInvoked'] -isnot [bool]){throw 'invalid'}
  if($value['exportSelectorMatched'] -isnot [bool]){throw 'invalid'}
  if($value['exportButtonInvoked'] -isnot [bool]){throw 'invalid'}
  if($value['exportDialogMatched'] -isnot [bool]){throw 'invalid'}
  if($value['exportDestinationFresh'] -isnot [bool]){throw 'invalid'}
  if($value['exportDialogSubmitted'] -isnot [bool]){throw 'invalid'}
  if($value['exportFileExists'] -isnot [bool]){throw 'invalid'}
  if($value['exportXmlRootMatched'] -isnot [bool]){throw 'invalid'}
  if($value['exportSyntheticIdentityMatched'] -isnot [bool]){throw 'invalid'}
  if($value['exportSuccessAcknowledged'] -isnot [bool]){throw 'invalid'}
  if($value['exportSchemaPinnedVerified'] -isnot [bool]){throw 'invalid'}
  if($value['exportFilenameKeyboardCommitted'] -isnot [bool]){throw 'invalid'}
  if($value['exportFilenameParentKind'] -isnot [string] -or $value['exportFilenameParentKind'] -cnotin @('not-observed','combobox','combobox-ex','other')){throw 'invalid'}
  if($value['exportOriginalPathMatched'] -isnot [bool]){throw 'invalid'}
  if($value['exportOriginalPathKind'] -isnot [string] -or $value['exportOriginalPathKind'] -cnotin @('not-observed','empty','expected-path','expected-double-extension','same-directory-other-name','other-directory')){throw 'invalid'}
  if(($value['exportScopedFileCount'] -isnot [int] -and $value['exportScopedFileCount'] -isnot [long]) -or $value['exportScopedFileCount'] -lt 0 -or $value['exportScopedFileCount'] -gt 32){throw 'invalid'}
  if(($value['exportScopedXmlCount'] -isnot [int] -and $value['exportScopedXmlCount'] -isnot [long]) -or $value['exportScopedXmlCount'] -lt 0 -or $value['exportScopedXmlCount'] -gt 32){throw 'invalid'}
  if(($value['exportBytes'] -isnot [int] -and $value['exportBytes'] -isnot [long]) -or $value['exportBytes'] -lt 0 -or $value['exportBytes'] -gt 262144){throw 'invalid'}
  if($value['exportSha256'] -isnot [string] -or ($value['exportSha256'] -cne '' -and $value['exportSha256'] -cnotmatch '\A[0-9a-f]{64}\z')){throw 'invalid'}
  if(($value['exportRejectedMessageId'] -isnot [int] -and $value['exportRejectedMessageId'] -isnot [long]) -or $value['exportRejectedMessageId'] -lt 0 -or $value['exportRejectedMessageId'] -gt 9999){throw 'invalid'}
  if(($value['importRejectedMessageId'] -isnot [int] -and $value['importRejectedMessageId'] -isnot [long]) -or $value['importRejectedMessageId'] -lt 0 -or $value['importRejectedMessageId'] -gt 9999){throw 'invalid'}
  if($value['roundtripImportCommandInvoked'] -isnot [bool]){throw 'invalid'}
  if($value['roundtripImportDialogMatched'] -isnot [bool]){throw 'invalid'}
  if($value['roundtripImportKeyboardCommitted'] -isnot [bool]){throw 'invalid'}
  if($value['roundtripImportDialogSubmitted'] -isnot [bool]){throw 'invalid'}
  if($value['roundtripImportPathMatched'] -isnot [bool]){throw 'invalid'}
  if($value['roundtripImportSheetMatched'] -isnot [bool]){throw 'invalid'}
  if($value['roundtripImportSucceeded'] -isnot [bool]){throw 'invalid'}
  if($value['roundtripReexportCommandInvoked'] -isnot [bool]){throw 'invalid'}
  if($value['roundtripReexportSucceeded'] -isnot [bool]){throw 'invalid'}
  if($value['roundtripXmlExactMatched'] -isnot [bool]){throw 'invalid'}
  if(($value['roundtripImportCheckedMoneyCount'] -isnot [int] -and $value['roundtripImportCheckedMoneyCount'] -isnot [long]) -or $value['roundtripImportCheckedMoneyCount'] -lt 0 -or $value['roundtripImportCheckedMoneyCount'] -gt 27){throw 'invalid'}
  if(($value['roundtripReexportBytes'] -isnot [int] -and $value['roundtripReexportBytes'] -isnot [long]) -or $value['roundtripReexportBytes'] -lt 0 -or $value['roundtripReexportBytes'] -gt 262144){throw 'invalid'}
  if($value['roundtripReexportSha256'] -isnot [string] -or ($value['roundtripReexportSha256'] -cne '' -and $value['roundtripReexportSha256'] -cnotmatch '\A[0-9a-f]{64}\z')){throw 'invalid'}
  if($value['gtgtCt42BeforeExportObserved'] -isnot [bool]){throw 'invalid'}
  if($value['gtgtCt42LockedBeforeExport'] -isnot [bool]){throw 'invalid'}
  if($value['gtgtCt42AfterImportObserved'] -isnot [bool]){throw 'invalid'}
  if($value['gtgtCt42LockedAfterImport'] -isnot [bool]){throw 'invalid'}
  if($value['gtgtAutoCalculationReady'] -isnot [bool]){throw 'invalid'}
  if($value['gtgtBusinessInstanceMatched'] -isnot [bool]){throw 'invalid'}
  if($value['gtgtCaseMoneyMatched'] -isnot [bool]){throw 'invalid'}
  if($value['gtgtCt42Locked'] -isnot [bool]){throw 'invalid'}
  if($value['webTaxValuesMatched'] -isnot [bool]){throw 'invalid'}
  if($value['webCreationDateMatchedNativeBaseline'] -isnot [bool]){throw 'invalid'}
  if($value['webServiceIdentityMatched'] -isnot [bool]){throw 'invalid'}
  if($value['webInputVerified'] -isnot [bool]){throw 'invalid'}
  if($value['webImportInputSha256'] -isnot [string] -or ($value['webImportInputSha256'] -cne '' -and $value['webImportInputSha256'] -cnotmatch '\A[0-9a-f]{64}\z')){throw 'invalid'}
  if($value['webSourceSha'] -isnot [string] -or ($value['webSourceSha'] -cne '' -and $value['webSourceSha'] -cnotmatch '\A[0-9a-f]{40}\z')){throw 'invalid'}
  if(($value['webTaxLeafCount'] -isnot [int] -and $value['webTaxLeafCount'] -isnot [long]) -or $value['webTaxLeafCount'] -lt 0 -or $value['webTaxLeafCount'] -gt 159){throw 'invalid'}
  if($value['webCaseId'] -isnot [string] -or $value['webCaseId'] -cnotin @('01GTGT-zero-M10-2026','01GTGT-sale10-M10-2026','01GTGT-sale10-half-M10-2026','01GTGT-sale10-manual-M10-2026','01GTGT-sale5-half-M10-2026','01GTGT-sale5-manual-M10-2026','01GTGT-noactivity-zero-M10-2026','01GTGT-noactivity-reset-sale10-M10-2026','01GTGT-noactivity-cancel-sale10-M10-2026','01GTGT-noactivity-uncheck-sale10-M10-2026','01GTGT-noactivity-keep-credit-M10-2026','01GTGT-zero-Q4-2026','01GTGT-native-import-sale10-M10-2026','01GTGT-annex12-zero-two-locations-M10-2026','01GTGT-annex12-two-plants-nonzero-M10-2026','03TNDN-profit20-Y2025','BCTC133-B01a-basic-Y2025','BCTC200-LT-basic-Y2025','05KK-withheld-Q3-2026','05QTT-two-employees-Y2025','01CNKD-TT50-revenue-two-groups-Q3-2026','01CNKD-TT50-310-pl01-three-groups-Q3-2026','02QTT-dependants-Y2025','01NTNN-two-contractors-M09-2026','03NTNN-no-rate-M10-2026','01NTNN-NCCNN-entry-M10-2026','04NTNN-TT80-one-subcontractor-2026','04NTNN-TT89-one-subcontractor-2026','02NTNN-TT89-two-annexes-2026','02NTNN-TT80-two-annexes-2026','01NTNN-occurrence-D20-09-2026','01NTNN-NCCNN-occurrence-D20-10-2026','03NTNN-occurrence-D20-10-2026')){throw 'invalid'}
  if(($value['webCaseEditCount'] -isnot [int] -and $value['webCaseEditCount'] -isnot [long]) -or $value['webCaseEditCount'] -lt 0 -or $value['webCaseEditCount'] -gt 3){throw 'invalid'}
  if(($value['gtgtCaseMoneyCount'] -isnot [int] -and $value['gtgtCaseMoneyCount'] -isnot [long]) -or $value['gtgtCaseMoneyCount'] -lt 0 -or $value['gtgtCaseMoneyCount'] -gt 27){throw 'invalid'}
  if(($value['gtgtCaseMismatchMask'] -isnot [int] -and $value['gtgtCaseMismatchMask'] -isnot [long]) -or $value['gtgtCaseMismatchMask'] -lt 0 -or $value['gtgtCaseMismatchMask'] -gt 134217727){throw 'invalid'}
  if(($value['gtgtCaseNonzeroMask'] -isnot [int] -and $value['gtgtCaseNonzeroMask'] -isnot [long]) -or $value['gtgtCaseNonzeroMask'] -lt 0 -or $value['gtgtCaseNonzeroMask'] -gt 134217727){throw 'invalid'}
  if($value['declarationMenuClicked'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationMenuClicked'] -cne $false){throw 'invalid'}
  if($value['declarationPeriodObserved'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationPeriodObserved'] -cne $false){throw 'invalid'}
  if($value['declarationPeriodMatched'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationPeriodMatched'] -cne $false){throw 'invalid'}
  if($value['declarationAnnexMatched'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationAnnexMatched'] -cne $false){throw 'invalid'}
  if($value['declarationSheetObserved'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationSheetObserved'] -cne $false){throw 'invalid'}
  if($value['declarationIdentityMatched'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationIdentityMatched'] -cne $false){throw 'invalid'}
  if($value['declarationSourcePinsMatched'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationSourcePinsMatched'] -cne $false){throw 'invalid'}
  if($value['declarationImportSheetMatched'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationImportSheetMatched'] -cne $false){throw 'invalid'}
  if($value['declarationSchemaValid'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationSchemaValid'] -cne $false){throw 'invalid'}
  if($value['declarationServiceIdentityMatched'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationServiceIdentityMatched'] -cne $false){throw 'invalid'}
  if($value['declarationCreationDateValid'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationCreationDateValid'] -cne $false){throw 'invalid'}
  if($value['declarationTreeMatched'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationTreeMatched'] -cne $false){throw 'invalid'}
  if(($value['declarationPeriodRejectedMessageId'] -isnot [int] -and $value['declarationPeriodRejectedMessageId'] -isnot [long]) -or $value['declarationPeriodRejectedMessageId'] -lt 0 -or $value['declarationPeriodRejectedMessageId'] -gt 9999){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationPeriodRejectedMessageId'] -cne 0){throw 'invalid'}
  if(($value['declarationAnnexSelectedCount'] -isnot [int] -and $value['declarationAnnexSelectedCount'] -isnot [long]) -or $value['declarationAnnexSelectedCount'] -lt 0 -or $value['declarationAnnexSelectedCount'] -gt 16){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationAnnexSelectedCount'] -cne 0){throw 'invalid'}
  if(($value['declarationSheetCount'] -isnot [int] -and $value['declarationSheetCount'] -isnot [long]) -or $value['declarationSheetCount'] -lt 0 -or $value['declarationSheetCount'] -gt 64){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationSheetCount'] -cne 0){throw 'invalid'}
  if(($value['declarationCellCheckCount'] -isnot [int] -and $value['declarationCellCheckCount'] -isnot [long]) -or $value['declarationCellCheckCount'] -lt 0 -or $value['declarationCellCheckCount'] -gt 24){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationCellCheckCount'] -cne 0){throw 'invalid'}
  if(($value['declarationCellMismatchMask'] -isnot [int] -and $value['declarationCellMismatchMask'] -isnot [long]) -or $value['declarationCellMismatchMask'] -lt 0 -or $value['declarationCellMismatchMask'] -gt 16777215){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationCellMismatchMask'] -cne 0){throw 'invalid'}
  if(($value['declarationCellLockedMask'] -isnot [int] -and $value['declarationCellLockedMask'] -isnot [long]) -or $value['declarationCellLockedMask'] -lt 0 -or $value['declarationCellLockedMask'] -gt 16777215){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationCellLockedMask'] -cne 0){throw 'invalid'}
  if(($value['declarationXmlCheckCount'] -isnot [int] -and $value['declarationXmlCheckCount'] -isnot [long]) -or $value['declarationXmlCheckCount'] -lt 0 -or $value['declarationXmlCheckCount'] -gt 24){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationXmlCheckCount'] -cne 0){throw 'invalid'}
  if(($value['declarationXmlMismatchMask'] -isnot [int] -and $value['declarationXmlMismatchMask'] -isnot [long]) -or $value['declarationXmlMismatchMask'] -lt 0 -or $value['declarationXmlMismatchMask'] -gt 16777215){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationXmlMismatchMask'] -cne 0){throw 'invalid'}
  if(($value['declarationTreeMismatchMask'] -isnot [int] -and $value['declarationTreeMismatchMask'] -isnot [long]) -or $value['declarationTreeMismatchMask'] -lt 0 -or $value['declarationTreeMismatchMask'] -gt 63){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationTreeMismatchMask'] -cne 0){throw 'invalid'}
  if(($value['declarationTreeLeafCount'] -isnot [int] -and $value['declarationTreeLeafCount'] -isnot [long]) -or $value['declarationTreeLeafCount'] -lt 0 -or $value['declarationTreeLeafCount'] -gt 4096){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationTreeLeafCount'] -cne 0){throw 'invalid'}
  if(($value['declarationInvalidSheetMask'] -isnot [int] -and $value['declarationInvalidSheetMask'] -isnot [long]) -or $value['declarationInvalidSheetMask'] -lt 0 -or $value['declarationInvalidSheetMask'] -gt 65535){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationInvalidSheetMask'] -cne 0){throw 'invalid'}
  if(($value['declarationInvalidCellCount'] -isnot [int] -and $value['declarationInvalidCellCount'] -isnot [long]) -or $value['declarationInvalidCellCount'] -lt 0 -or $value['declarationInvalidCellCount'] -gt 4096){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationInvalidCellCount'] -cne 0){throw 'invalid'}
  if(($value['declarationInvalidCell1'] -isnot [int] -and $value['declarationInvalidCell1'] -isnot [long]) -or $value['declarationInvalidCell1'] -lt 0 -or $value['declarationInvalidCell1'] -gt 16999999){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationInvalidCell1'] -cne 0){throw 'invalid'}
  if(($value['declarationInvalidCell2'] -isnot [int] -and $value['declarationInvalidCell2'] -isnot [long]) -or $value['declarationInvalidCell2'] -lt 0 -or $value['declarationInvalidCell2'] -gt 16999999){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationInvalidCell2'] -cne 0){throw 'invalid'}
  if(($value['declarationInvalidCell3'] -isnot [int] -and $value['declarationInvalidCell3'] -isnot [long]) -or $value['declarationInvalidCell3'] -lt 0 -or $value['declarationInvalidCell3'] -gt 16999999){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationInvalidCell3'] -cne 0){throw 'invalid'}
  if(($value['declarationInvalidCell4'] -isnot [int] -and $value['declarationInvalidCell4'] -isnot [long]) -or $value['declarationInvalidCell4'] -lt 0 -or $value['declarationInvalidCell4'] -gt 16999999){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationInvalidCell4'] -cne 0){throw 'invalid'}
  if($value['declarationEntryMethodPinsMatched'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationEntryMethodPinsMatched'] -cne $false){throw 'invalid'}
  if($value['declarationEntryCatalogueMatched'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationEntryCatalogueMatched'] -cne $false){throw 'invalid'}
  if($value['declarationEntryChoiceMatched'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationEntryChoiceMatched'] -cne $false){throw 'invalid'}
  if($value['declarationEntryLocksMatched'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationEntryLocksMatched'] -cne $false){throw 'invalid'}
  if($value['declarationEntryRowsMatched'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationEntryRowsMatched'] -cne $false){throw 'invalid'}
  if($value['declarationEntryValuesMatched'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationEntryValuesMatched'] -cne $false){throw 'invalid'}
  if($value['declarationEntrySignerMatched'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationEntrySignerMatched'] -cne $false){throw 'invalid'}
  if($value['declarationEntrySigningDateLocked'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationEntrySigningDateLocked'] -cne $false){throw 'invalid'}
  if($value['declarationEntrySheetMatched'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationEntrySheetMatched'] -cne $false){throw 'invalid'}
  if(($value['declarationEntryPlannedCount'] -isnot [int] -and $value['declarationEntryPlannedCount'] -isnot [long]) -or $value['declarationEntryPlannedCount'] -lt 0 -or $value['declarationEntryPlannedCount'] -gt 30){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationEntryPlannedCount'] -cne 0){throw 'invalid'}
  if(($value['declarationEntryActionCount'] -isnot [int] -and $value['declarationEntryActionCount'] -isnot [long]) -or $value['declarationEntryActionCount'] -lt 0 -or $value['declarationEntryActionCount'] -gt 30){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationEntryActionCount'] -cne 0){throw 'invalid'}
  if(($value['declarationEntryFailureCode'] -isnot [int] -and $value['declarationEntryFailureCode'] -isnot [long]) -or $value['declarationEntryFailureCode'] -lt 0 -or $value['declarationEntryFailureCode'] -gt 31){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationEntryFailureCode'] -cne 0){throw 'invalid'}
  if(($value['declarationEntryMethodPinMask'] -isnot [int] -and $value['declarationEntryMethodPinMask'] -isnot [long]) -or $value['declarationEntryMethodPinMask'] -lt 0 -or $value['declarationEntryMethodPinMask'] -gt 1073741823){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationEntryMethodPinMask'] -cne 0){throw 'invalid'}
  if(($value['declarationEntryLockBeforeMask'] -isnot [int] -and $value['declarationEntryLockBeforeMask'] -isnot [long]) -or $value['declarationEntryLockBeforeMask'] -lt 0 -or $value['declarationEntryLockBeforeMask'] -gt 65535){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationEntryLockBeforeMask'] -cne 0){throw 'invalid'}
  if(($value['declarationEntryLockAfterMask'] -isnot [int] -and $value['declarationEntryLockAfterMask'] -isnot [long]) -or $value['declarationEntryLockAfterMask'] -lt 0 -or $value['declarationEntryLockAfterMask'] -gt 65535){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationEntryLockAfterMask'] -cne 0){throw 'invalid'}
  if(($value['declarationEntryLockFinalMask'] -isnot [int] -and $value['declarationEntryLockFinalMask'] -isnot [long]) -or $value['declarationEntryLockFinalMask'] -lt 0 -or $value['declarationEntryLockFinalMask'] -gt 65535){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationEntryLockFinalMask'] -cne 0){throw 'invalid'}
  if(($value['declarationEntryRowsBefore'] -isnot [int] -and $value['declarationEntryRowsBefore'] -isnot [long]) -or $value['declarationEntryRowsBefore'] -lt 0 -or $value['declarationEntryRowsBefore'] -gt 65535){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationEntryRowsBefore'] -cne 0){throw 'invalid'}
  if(($value['declarationEntryRowsAfter'] -isnot [int] -and $value['declarationEntryRowsAfter'] -isnot [long]) -or $value['declarationEntryRowsAfter'] -lt 0 -or $value['declarationEntryRowsAfter'] -gt 65535){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationEntryRowsAfter'] -cne 0){throw 'invalid'}
  if(($value['declarationEntryRowInsertCount'] -isnot [int] -and $value['declarationEntryRowInsertCount'] -isnot [long]) -or $value['declarationEntryRowInsertCount'] -lt 0 -or $value['declarationEntryRowInsertCount'] -gt 4){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationEntryRowInsertCount'] -cne 0){throw 'invalid'}
  if(($value['declarationEntryMismatchMask'] -isnot [int] -and $value['declarationEntryMismatchMask'] -isnot [long]) -or $value['declarationEntryMismatchMask'] -lt 0 -or $value['declarationEntryMismatchMask'] -gt 1073741823){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationEntryMismatchMask'] -cne 0){throw 'invalid'}
  if(($value['declarationEntryLockedMask'] -isnot [int] -and $value['declarationEntryLockedMask'] -isnot [long]) -or $value['declarationEntryLockedMask'] -lt 0 -or $value['declarationEntryLockedMask'] -gt 1073741823){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationEntryLockedMask'] -cne 0){throw 'invalid'}
  if(($value['declarationEntryCellTypeMismatchMask'] -isnot [int] -and $value['declarationEntryCellTypeMismatchMask'] -isnot [long]) -or $value['declarationEntryCellTypeMismatchMask'] -lt 0 -or $value['declarationEntryCellTypeMismatchMask'] -gt 1073741823){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationEntryCellTypeMismatchMask'] -cne 0){throw 'invalid'}
  if(($value['declarationEntryCombo1Mask'] -isnot [int] -and $value['declarationEntryCombo1Mask'] -isnot [long]) -or $value['declarationEntryCombo1Mask'] -lt 0 -or $value['declarationEntryCombo1Mask'] -gt 2047){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationEntryCombo1Mask'] -cne 0){throw 'invalid'}
  if(($value['declarationEntryCombo2Mask'] -isnot [int] -and $value['declarationEntryCombo2Mask'] -isnot [long]) -or $value['declarationEntryCombo2Mask'] -lt 0 -or $value['declarationEntryCombo2Mask'] -gt 2047){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationEntryCombo2Mask'] -cne 0){throw 'invalid'}
  if(($value['declarationEntryDateTextMask'] -isnot [int] -and $value['declarationEntryDateTextMask'] -isnot [long]) -or $value['declarationEntryDateTextMask'] -lt 0 -or $value['declarationEntryDateTextMask'] -gt 1073741823){throw 'invalid'}
  if(($ExpectedMode -cnotin @('declaration-web-import-inspect')) -and $value['declarationEntryDateTextMask'] -cne 0){throw 'invalid'}
  if($value['controlKinds'] -isnot [Collections.IDictionary]){throw 'invalid'}
  if($value['realTaxpayerDataUsed'] -isnot [bool]){throw 'invalid'}
  if(($true) -and $value['realTaxpayerDataUsed'] -cne $false){throw 'invalid'}
  if($value['runtimeRoundTrip'] -isnot [bool]){throw 'invalid'}
  if(($true) -and $value['runtimeRoundTrip'] -cne $false){throw 'invalid'}
  if($value['webSigningDateEdited'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-web-import-inspect')) -and $value['webSigningDateEdited'] -cne $false){throw 'invalid'}
  if($value['webSigningDateReady'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-web-import-inspect')) -and $value['webSigningDateReady'] -cne $false){throw 'invalid'}
  if($value['webSigningDateLocked'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-web-import-inspect')) -and $value['webSigningDateLocked'] -cne $false){throw 'invalid'}
  if(($value['webSigningDateCellKind'] -isnot [int] -and $value['webSigningDateCellKind'] -isnot [long]) -or $value['webSigningDateCellKind'] -lt 0 -or $value['webSigningDateCellKind'] -gt 4){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-web-import-inspect')) -and $value['webSigningDateCellKind'] -cne 0){throw 'invalid'}
  if($value['annex12LifecycleMatched'] -isnot [bool]){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-annex12-row-inspect')) -and $value['annex12LifecycleMatched'] -cne $false){throw 'invalid'}
  if(($value['annex12LifecycleActionCount'] -isnot [int] -and $value['annex12LifecycleActionCount'] -isnot [long]) -or $value['annex12LifecycleActionCount'] -lt 0 -or $value['annex12LifecycleActionCount'] -gt 9){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-annex12-row-inspect')) -and $value['annex12LifecycleActionCount'] -cne 0){throw 'invalid'}
  if(($value['annex12LifecycleEditCount'] -isnot [int] -and $value['annex12LifecycleEditCount'] -isnot [long]) -or $value['annex12LifecycleEditCount'] -lt 0 -or $value['annex12LifecycleEditCount'] -gt 1){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-annex12-row-inspect')) -and $value['annex12LifecycleEditCount'] -cne 0){throw 'invalid'}
  if(($value['annex12LifecycleObservedMask'] -isnot [int] -and $value['annex12LifecycleObservedMask'] -isnot [long]) -or $value['annex12LifecycleObservedMask'] -lt 0 -or $value['annex12LifecycleObservedMask'] -gt 1023){throw 'invalid'}
  if(($ExpectedMode -cnotin @('gtgt-annex12-row-inspect')) -and $value['annex12LifecycleObservedMask'] -cne 0){throw 'invalid'}
  if($value.mode -cne $ExpectedMode){throw 'invalid'}
  # END GENERATED RESULT CONTRACT
  if($value.annex12NumericSnapshots -isnot [string] -or $value.annex12NumericSnapshots.Length -gt 4096){throw 'invalid'}
  if($value.annex12NumericSnapshots -cne ''){
   $parts=$value.annex12NumericSnapshots.Split(';')
   if($parts.Count -ne $value.annex12NumericCaseCount -or $parts.Count -gt 3){throw 'invalid'}
   foreach($part in $parts){$numbers=$part.Split(',');if($numbers.Count -ne 12){throw 'invalid'};foreach($number in $numbers){if($number -cnotmatch '^(?:0|[1-9][0-9]{0,14})(?:\.[0-9]{1,20})?$'){throw 'invalid'};if([decimal]$number -gt 999999999999999){throw 'invalid'}}}
  }elseif($value.annex12NumericCaseCount -ne 0){throw 'invalid'}
  foreach($field in @('annex12NumericTextSnapshots','annex12NumericTypeSnapshots','annex12NumericDoubleBits')){if($value[$field] -isnot [string] -or $value[$field].Length -gt 4096){throw 'invalid'};if($value.annex12NumericCaseCount -eq 0 -and $value[$field] -cne ''){throw 'invalid'}}
  if($value.annex12NumericCaseCount -gt 0){
   $displayCases=$value.annex12NumericTextSnapshots.Split(';');$typeCases=$value.annex12NumericTypeSnapshots.Split(';');$bitCases=$value.annex12NumericDoubleBits.Split(';')
   if($displayCases.Count -ne $value.annex12NumericCaseCount -or $typeCases.Count -ne $displayCases.Count -or $bitCases.Count -ne $displayCases.Count){throw 'invalid'}
   for($caseIndex=0;$caseIndex -lt $displayCases.Count;$caseIndex++){
    $displays=$displayCases[$caseIndex].Split('|');$types=$typeCases[$caseIndex].Split('|');$bits=$bitCases[$caseIndex].Split('|')
    if($displays.Count -ne 12 -or $types.Count -ne 12 -or $bits.Count -ne 12){throw 'invalid'}
    for($cellIndex=0;$cellIndex -lt 12;$cellIndex++){
     if($displays[$cellIndex] -cnotmatch '\A[0-9,.() -]{0,64}\z' -or $types[$cellIndex] -cnotin @('double','decimal','single','integer','other')){throw 'invalid'}
     if($types[$cellIndex] -ceq 'double'){if($bits[$cellIndex] -cnotmatch '\A[0-9A-F]{16}\z'){throw 'invalid'}}elseif($bits[$cellIndex] -cne ''){throw 'invalid'}
    }
   }
  }
  if($value.amendmentOpenKhbsSheetsObserved -and ($value.amendmentOpenLoadedSheets -lt 3 -or $value.amendmentOpenKhbsRows -lt 1 -or $value.amendmentOpenKhbsColumns -lt 1 -or $value.amendmentOpenExplanationRows -lt 1 -or $value.amendmentOpenExplanationColumns -lt 1 -or -not $value.amendmentOpenSourcesMatched -or -not $value.amendmentOpenPeriodMatched)){throw 'invalid'}
  if($value.amendmentPriorFileFresh -and ($value.amendmentPriorFileBytes -lt 2 -or $value.amendmentPriorFileSha256.Length -ne 64 -or -not $value.amendmentPriorFileScopeMatched -or -not $value.amendmentPriorXmlParsed)){throw 'invalid'}
  if($value.webInputVerified -and ($value.webImportInputSha256.Length -ne 64 -or $value.webSourceSha.Length -ne 40)){throw 'invalid'}
  $kindKeys=@('form','button','combo','text','spread','other')
  if($value.controlKinds -isnot [Collections.IDictionary] -or $value.controlKinds.Count -ne $kindKeys.Count){throw 'invalid'}
  $safeKinds=[ordered]@{}
  foreach($key in $kindKeys){if(@($value.controlKinds.Keys) -cnotcontains $key -or ($value.controlKinds[$key] -isnot [int] -and $value.controlKinds[$key] -isnot [long]) -or $value.controlKinds[$key] -lt 0 -or $value.controlKinds[$key] -gt 512){throw 'invalid'};$safeKinds[$key]=[int]$value.controlKinds[$key]}
  $allowedPeriodNames=@('chkTkhaiThang','chkTKQuy','OptTKThang','OptChinhthuc','OptBosung','mskYear','mskMonth','cbbQuy','btnDongY','cmdClose','axfpsPhuLuc','cboNganhKD','chkChonPhuLucKeKhaiAll','cboCQTCuc','cboCQTChiCuc','cboTinh','cboXa')
  if($value.periodControls -isnot [Collections.IDictionary] -or $value.periodControls.Count -gt $allowedPeriodNames.Count){throw 'invalid'}
  $safePeriod=[ordered]@{}
  foreach($name in $value.periodControls.Keys){
   if($name -isnot [string] -or $name -cnotin $allowedPeriodNames){throw 'invalid'}
   $description=$value.periodControls[$name];$descriptionKeys=@('kind','visible','enabled','checkedAvailable','checked')
   if($description -isnot [Collections.IDictionary] -or $description.Count -ne 5){throw 'invalid'}
   foreach($key in $descriptionKeys){if(@($description.Keys) -cnotcontains $key){throw 'invalid'}}
   if($description.kind -isnot [string] -or $description.kind -cnotin @('spread','radio','check','masked-text','text','combo','button','other')){throw 'invalid'}
   foreach($key in @('visible','enabled','checkedAvailable','checked')){if($description[$key] -isnot [bool]){throw 'invalid'}}
   if($description.checkedAvailable -ne ($description.kind -in @('radio','check')) -or (-not $description.checkedAvailable -and $description.checked)){throw 'invalid'}
   $safePeriod[$name]=[ordered]@{kind=$description.kind;visible=$description.visible;enabled=$description.enabled;checkedAvailable=$description.checkedAvailable;checked=$description.checked}
  }
  $safe=[ordered]@{status='valid'}
  foreach($key in $keys){if($key -eq 'controlKinds'){$safe[$key]=$safeKinds}elseif($key -eq 'periodControls'){$safe[$key]=$safePeriod}else{$safe[$key]=$value[$key]}}
  return $safe
 }catch{$invalid.status='invalid';$invalid.stage='result-invalid';return $invalid}
}
