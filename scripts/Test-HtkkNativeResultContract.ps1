# Own strict-reader fixtures only; no native HTKK/provenance claims.
param(
 [string]$Reader=(Join-Path $PSScriptRoot 'Get-HtkkSafeGuiReferenceResult.ps1'),
 [string]$Defaults=(Join-Path $PSScriptRoot 'HtkkNativeResultDefaults.ps1'),
 [string]$Registry=(Join-Path $PSScriptRoot 'htkk-native-automation-registry.json')
)
$ErrorActionPreference='Stop'
. $Reader
. $Defaults
$r=Get-Content -LiteralPath $Registry -Raw | ConvertFrom-Json -AsHashtable
$temporaryRoot=[IO.Path]::GetTempPath()
$Directory=Join-Path $temporaryRoot ('htkk-native-result-contract-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $Directory | Out-Null
$path=Join-Path $Directory 'result.json'
try {
$count=0
function Check($value,$mode,$expected){
 $value|ConvertTo-Json -Depth 12 -Compress|Set-Content -LiteralPath $path -Encoding utf8
 $actual=Get-HtkkSafeGuiReferenceResult -ResultPath $path -ExpectedMode $mode
 if($actual.status -cne $expected){throw "Boundary mismatch: $count ($expected/$($actual.status))"}
 $script:count++
}
foreach($mode in $r.modes.Keys){if($mode -ceq 'none'){continue};Check (New-HtkkNativeResultDefaults -Mode $mode) $mode 'valid'}
foreach($key in $r.resultFields.Keys){
 $field=$r.resultFields[$key]
 $v=New-HtkkNativeResultDefaults -Mode inspect;$v.Remove($key);Check $v inspect invalid
 $v=New-HtkkNativeResultDefaults -Mode inspect
 if($field.kind -ceq 'boolean'){$v[$key]='false'}else{$v[$key]=$true}
 Check $v inspect invalid
 if($field.kind -ceq 'integer'){
  foreach($bad in @(-1,([long]$field.maximum+1),'0',0.5)){
   $v=New-HtkkNativeResultDefaults -Mode inspect;$v[$key]=$bad;Check $v inspect invalid
  }
 }
 if($field.Contains('activeModes')){
  foreach($mode in $r.modes.Keys){
   if($mode -ceq 'none' -or $mode -cin $field.activeModes){continue}
   $v=New-HtkkNativeResultDefaults -Mode $mode
   switch($field.kind){boolean{$v[$key]=$true} integer{$v[$key]=1} hex{$v[$key]='a'*$field.length} string{$v[$key]='1'}}
   Check $v $mode invalid
  }
 }
}
$v=New-HtkkNativeResultDefaults -Mode inspect;$v.menuClickCount=4;Check $v inspect invalid
$v=New-HtkkNativeResultDefaults -Mode gtgt-amendment-open-inspect;$v.menuClickCount=6;Check $v gtgt-amendment-open-inspect valid
$v.menuClickCount=7;Check $v gtgt-amendment-open-inspect invalid
$v=New-HtkkNativeResultDefaults -Mode inspect;$v.controlKinds.form=513;Check $v inspect invalid
$v=New-HtkkNativeResultDefaults -Mode inspect;$v.unreviewed=$false;Check $v inspect invalid
$v=New-HtkkNativeResultDefaults -Mode inspect;$v.stage='unreviewed-stage';Check $v inspect invalid
$v=New-HtkkNativeResultDefaults -Mode inspect;$v.mode='profile-save';Check $v inspect invalid
Write-Output "BOUNDARIES=$count"
} finally {
 Remove-Item -LiteralPath $Directory -Recurse -Force
}
