# Strictly reconstructs a bounded allowlisted result; never exposes raw own/original output.
function Get-HtkkSafeGuiReferenceResult {
 [CmdletBinding()]
 param([Parameter(Mandatory=$true)][string]$ResultPath,[ValidateSet('inspect','profile-save','gtgt-inspect')][string]$ExpectedMode)
 $invalid=[ordered]@{status='unavailable';mode=$ExpectedMode;stage='result-unavailable';runtimeRoundTrip=$false}
 try {
  if(-not(Test-Path -LiteralPath $ResultPath -PathType Leaf)){return $invalid}
  $file=Get-Item -LiteralPath $ResultPath
  if($file.Attributes -band [IO.FileAttributes]::ReparsePoint -or $file.Length -gt 16384 -or $file.Length -lt 2){$invalid.status='invalid';$invalid.stage='result-invalid';return $invalid}
  $value=Get-Content -LiteralPath $ResultPath -Raw -Encoding UTF8 | ConvertFrom-Json -AsHashtable
  $keys=@('format','mode','stage','failureCategory','editorKind','runtime','sourcePinsVerified','visibleForms','spreadCount','sheetRows','sheetColumns','mstBoxesMatched','initialRequiredTextBlank','editingApiAvailable','performedInputCount','originalSaveInvoked','savedHeaderExists','savedHeaderChecksMatched','savedHeaderCheckedFieldCount','saveDialogKind','savedHeaderMismatchMask','profileClosed','mainMenuObserved','d1MenuClicked','gtgtPeriodObserved','menuRowCount','menuClickCount','periodControlCount','periodControls','controlKinds','realTaxpayerDataUsed','runtimeRoundTrip')
  if($value -isnot [Collections.IDictionary] -or $value.Count -ne $keys.Count){throw 'invalid'}
  foreach($key in $keys){if(@($value.Keys) -cnotcontains $key){throw 'invalid'}}
  foreach($key in @('format','mode','stage','failureCategory','editorKind','runtime','saveDialogKind')){if($value[$key] -isnot [string]){throw 'invalid'}}
  $stages=@('not-started','source-or-runtime-not-matched','fixture-preexists','waiting-for-profile','initialization-unavailable','profile-wait-timeout','profile-controls-not-yet-unique','profile-dimensions-unmatched','fresh-synthetic-profile-not-established','profile-inspected','editing-api-unavailable','profile-province-code-unmatched','profile-ward-code-unmatched','profile-taxhead-code-unmatched','profile-taxlocal-code-unmatched','waiting-for-profile-save-permit','edit-name','edit-province','edit-ward','edit-address','edit-signer','edit-tax-authority-head','edit-tax-authority-local','original-save-invoking','success-modal-acknowledged','original-profile-saved-verified','original-profile-save-not-verified','profile-close-invoking','waiting-profile-close','gtgt-profile-owner-not-matched','waiting-main-menu','gtgt-profile-preconditions-not-matched','gtgt-menu-spread-not-yet-unique','gtgt-menu-id-not-unique','gtgt-menu-target-hidden','gtgt-menu-click-101','gtgt-menu-click-101_1','gtgt-menu-click-D1','waiting-gtgt-period','gtgt-period-inspected')
  if($value.format -cne 'htkk-gui-reference-automation-v1' -or $value.mode -cne $ExpectedMode -or $value.runtime -cne 'clr2-x86-custom-reference' -or $value.stage -cnotin $stages -or $value.failureCategory -cnotin @('none','reflection-invocation','operation-not-established','argument','com','io','other-standard') -or $value.saveDialogKind -cnotin @('not-observed','success-0002','invalid-0015','other-original-message') -or $value.editorKind -cnotin @('not-started','combo','text-box','other-control')){throw 'invalid'}
  foreach($key in @('sourcePinsVerified','mstBoxesMatched','initialRequiredTextBlank','editingApiAvailable','originalSaveInvoked','savedHeaderExists','savedHeaderChecksMatched','profileClosed','mainMenuObserved','d1MenuClicked','gtgtPeriodObserved','realTaxpayerDataUsed','runtimeRoundTrip')){if($value[$key] -isnot [bool]){throw 'invalid'}}
  if($value.realTaxpayerDataUsed -or $value.runtimeRoundTrip){throw 'invalid'}
  $maximum=@{visibleForms=64;spreadCount=512;sheetRows=10000;sheetColumns=10000;performedInputCount=7;savedHeaderCheckedFieldCount=8;savedHeaderMismatchMask=255;menuRowCount=2048;menuClickCount=3;periodControlCount=512}
  foreach($key in $maximum.Keys){if(($value[$key] -isnot [int] -and $value[$key] -isnot [long]) -or $value[$key] -lt 0 -or $value[$key] -gt $maximum[$key]){throw 'invalid'}}
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
