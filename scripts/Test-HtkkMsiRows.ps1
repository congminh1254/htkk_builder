# Invoke the production read-only query adapter with a COM-shaped own fixture.
$ErrorActionPreference='Stop'
$tokens=$null;$errors=$null
$ast=[Management.Automation.Language.Parser]::ParseFile((Join-Path $PSScriptRoot 'Test-HtkkSourceCandidateTrust.ps1'),[ref]$tokens,[ref]$errors)
if($errors.Count){throw 'SOURCE_TRUST_PARSE_FAILED'}
foreach($name in @('Release-ComObject','Read-MsiRows')){
 $fn=$ast.Find({param($n) $n -is [Management.Automation.Language.FunctionDefinitionAst] -and $n.Name -ceq $name},$true)
 if($null -eq $fn){throw 'SOURCE_QUERY_FUNCTION_MISSING'}
 . ([scriptblock]::Create($fn.Extent.Text))
}
$row=[pscustomobject]@{disk=1;last=4526;cab='Data1.cab'}
$view=[pscustomobject]@{row=$row;read=$false;closed=$false}
$view|Add-Member ScriptMethod Execute {return 0}
$view|Add-Member ScriptMethod Close {$this.closed=$true;return 0}
$view|Add-Member ScriptMethod Fetch {if(-not $this.read){$this.read=$true;return $this.row};return $null}
$database=[pscustomobject]@{view=$view}
$database|Add-Member ScriptMethod OpenView {param($query) if($query -cne 'SELECT fixed fixture'){throw 'SQL_NOT_FIXED'};return $this.view}
$rows=Read-MsiRows $database 'SELECT fixed fixture' {param($r) return $r}
if($rows.Count -ne 1 -or $rows[0].disk -ne 1 -or $rows[0].last -ne 4526 -or $rows[0].cab -cne 'Data1.cab' -or -not $view.closed){throw 'COM_RETURN_CODES_CONTAMINATED_QUERY_ROWS'}
Write-Output 'Production MSI query adapter suppressed Execute/Close return codes: passed'
