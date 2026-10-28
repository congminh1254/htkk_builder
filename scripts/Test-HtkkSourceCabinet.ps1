# Own fixture data only, never supplier code or installer execution.
$ErrorActionPreference='Stop'
Add-Type -Path (Join-Path $PSScriptRoot 'HtkkSourceCabinet.cs')
$work=Join-Path $env:RUNNER_TEMP ('htkk-cabinet-test-'+[Guid]::NewGuid().ToString('N'));$null=[IO.Directory]::CreateDirectory($work)
try{
 $fake=Join-Path $work 'fake.cab';[IO.File]::WriteAllBytes($fake,[byte[]]@(1,2,3))
 foreach($bad in @('../outside','a/b','a:b','..','trailing space ')){
  try{$null=[HtkkSourceCabinet]::Extract($fake,(Join-Path $work 'reject'),[string[]]@($bad),[long[]]@(3));throw 'UNEXPECTED_ACCEPT'}catch{
   $errorItem=$_.Exception;while($null -ne $errorItem.InnerException){$errorItem=$errorItem.InnerException}
   if($errorItem.Message -cne 'CAB_MEMBER_POLICY'){throw 'CAB_MEMBER_POLICY_NOT_ENFORCED'}
  }
 }
 if(-not $IsWindows){Write-Output 'Cabinet member policy checks passed: 5; actual FDI requires Windows';return}
 . (Join-Path $PSScriptRoot 'Invoke-HtkkBoundedJobProcess.ps1')
 $inputFile=Join-Path $work 'input.bin';[IO.File]::WriteAllBytes($inputFile,[byte[]]@(7,8,9))
 $ddf=Join-Path $work 'fixture.ddf'
 [IO.File]::WriteAllText($ddf,('.OPTION EXPLICIT'+"`r`n"+'.Set CabinetNameTemplate=fixture.cab'+"`r`n"+'.Set DiskDirectoryTemplate="'+$work+'"'+"`r`n"+'.Set Cabinet=on'+"`r`n"+'.Set Compress=on'+"`r`n"+'"'+$inputFile+'" "barcodelib.barcode.winforms."'+"`r`n"+'"'+$inputFile+'" "htkk.exe.config"'+"`r`n"),[Text.Encoding]::ASCII)
 $tool=Join-Path $env:SystemRoot 'System32\makecab.exe'
 if((Get-AuthenticodeSignature -LiteralPath $tool).Status -ne 'Valid'){throw 'MAKECAB_NOT_TRUSTED'}
 $run=Invoke-HtkkBoundedJobProcess -Executable $tool -WorkingDirectory $work -Arguments @('/F',$ddf) -TimeoutMilliseconds 15000
 if($run.status -ne 'exited' -or $run.exitCode -ne 0 -or -not $run.jobCleanupVerified){throw 'FIXTURE_CREATION_FAILED'}
 $cab=Join-Path $work 'fixture.cab';$paths=[HtkkSourceCabinet]::Extract($cab,(Join-Path $work 'result'),[string[]]@('barcodelib.barcode.winforms.','htkk.exe.config'),[long[]]@(3,3))
 if($paths.Count -ne 2 -or [IO.Path]::GetFileName($paths[0]) -cne '00000.bin' -or [Convert]::ToHexString([IO.File]::ReadAllBytes($paths[0])) -cne '070809' -or [Convert]::ToHexString([IO.File]::ReadAllBytes($paths[1])) -cne '070809'){throw 'CAB_DATA_NOT_PRESERVED'}
 try{$null=[HtkkSourceCabinet]::Extract($cab,(Join-Path $work 'unknown'),[string[]]@('unknown'),[long[]]@(3));throw 'UNEXPECTED_ACCEPT'}catch{if($_.Exception.GetBaseException().Message -cne 'CAB_DATA_EXTRACTION_FAILED'){throw 'UNKNOWN_MEMBER_NOT_REJECTED'}}
 try{$null=[HtkkSourceCabinet]::Extract($cab,(Join-Path $work 'size'),[string[]]@('barcodelib.barcode.winforms.','htkk.exe.config'),[long[]]@(4,3));throw 'UNEXPECTED_ACCEPT'}catch{if($_.Exception.GetBaseException().Message -cne 'CAB_DATA_EXTRACTION_FAILED'){throw 'SIZE_NOT_REJECTED'}}
 Write-Output 'Cabinet data mapping checks passed: 8; original member IDs preserved, numeric owned paths only'
}finally{Remove-Item -LiteralPath $work -Recurse -Force}
