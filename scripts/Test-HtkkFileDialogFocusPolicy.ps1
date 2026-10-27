# Compile the exact production readiness policy, without GUI/HTKK dependencies.
$ErrorActionPreference='Stop'
$source=[IO.File]::ReadAllText((Join-Path $PSScriptRoot 'HtkkGtgtExportInspection.cs'))
$marker='public enum HtkkFileDialogFocusState'
$offset=$source.IndexOf($marker,[StringComparison]::Ordinal)
if($offset -lt 0){throw 'Production focus policy missing'}
Add-Type -TypeDefinition ('using System;'+$source.Substring($offset))
$script:focusCases=0
function Assert-FocusState($gate,$focus,$expected){
 $observed=$gate.Observe([IntPtr]11,[IntPtr]22,$focus).ToString()
 if($observed -cne $expected){throw "Focus policy transition mismatch: $observed"};$script:focusCases++
}
function Assert-FocusRejected([scriptblock]$operation){
 $rejected=$false;try{& $operation}catch{$rejected=$true}
 if(!$rejected){throw 'Unsafe focus transition accepted'};$script:focusCases++
}
$gate=New-Object HtkkFileDialogFocusGate
Assert-FocusRejected { $gate.Begin() }
Assert-FocusRejected { $gate.ResetAfterSubmission() }
Assert-FocusState $gate $true 'Waiting'
Assert-FocusState $gate $false 'Waiting'
Assert-FocusState $gate $true 'Waiting'
Assert-FocusState $gate $true 'Ready'
$gate.Begin()
Assert-FocusRejected { $gate.Begin() }
Assert-FocusRejected { $gate.Observe([IntPtr]11,[IntPtr]22,$true) }
$gate.ResetAfterSubmission()
Assert-FocusState $gate $true 'Waiting'
Assert-FocusState $gate $true 'Ready'
foreach($pair in @(@(0,22),@(11,0),@(12,22),@(11,23))){
 Assert-FocusRejected { $gate.Observe([IntPtr]$pair[0],[IntPtr]$pair[1],$true) }
}
$gate=New-Object HtkkFileDialogFocusGate
for($tick=1;$tick -le 40;$tick++){Assert-FocusState $gate $false 'Waiting'}
Assert-FocusState $gate $true 'Timeout'
Assert-FocusRejected { $gate.Begin() }
$gate=New-Object HtkkFileDialogFocusGate
for($tick=1;$tick -le 38;$tick++){Assert-FocusState $gate $false 'Waiting'}
Assert-FocusState $gate $true 'Waiting'
Assert-FocusState $gate $true 'Ready'
$gate.Begin()
Assert-FocusRejected { $gate.Observe([IntPtr]11,[IntPtr]22,$false) }
Write-Host "File dialog production focus policy checks passed: $script:focusCases"
