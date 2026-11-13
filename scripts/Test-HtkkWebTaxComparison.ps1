# Offline tests of the actual C# comparator, not supplier execution evidence.
$ErrorActionPreference='Stop'
Add-Type -Path (Join-Path $PSScriptRoot 'HtkkWebTaxComparison.cs')
function New-Fixture([bool]$Web) {
 $service=if($Web){'<maDVu>CCKK</maDVu><tenDVu>Công cụ Kê khai</tenDVu><pbanDVu>0.9.2</pbanDVu><ttinNhaCCapDVu>hotrokekhai.net — Công cụ Kê khai, công cụ độc lập</ttinNhaCCapDVu>'}else{'<maDVu>HTKK</maDVu><tenDVu>HỖ TRỢ KÊ KHAI THUẾ</tenDVu><pbanDVu>5.8.1</pbanDVu><ttinNhaCCapDVu>0123456789ABCDEF0123456789ABCDEF</ttinNhaCCapDVu>'}
 $date=if($Web){'2026-10-25'}else{'2026-10-26'}
 $fields='';for($i=0;$i -lt 68;$i++){$fields+='<f'+$i+'>0</f'+$i+'>'}
 return [xml]('<HSoThueDTu xmlns="http://kekhaithue.gdt.gov.vn/TKhaiThue"><HSoKhaiThue id="ID_1"><TTinChung><TTinDVu>'+$service+'</TTinDVu><TTinTKhaiThue><TKhaiThue><ngayLapTKhai>'+$date+'</ngayLapTKhai><ngayKy>2026-10-25</ngayKy></TKhaiThue></TTinTKhaiThue></TTinChung><CTieuTKhaiChinh>'+$fields+'</CTieuTKhaiChinh></HSoKhaiThue></HSoThueDTu>')
}
$inputXml=New-Fixture $true;$baseline=New-Fixture $false;$output=New-Fixture $false
function Assert-Comparison([xml]$Output,[bool]$Expected) { $count=0;$actual=[HtkkWebTaxComparison]::Compare($inputXml,$baseline,$Output,[ref]$count);if($actual -ne $Expected -or ($Expected -and $count -ne 70)){throw 'Synthetic XML comparison boundary failed'} }
Assert-Comparison $output $true
foreach($change in @(
 @{before='<f0>0</f0>';after='<f0>1</f0>'},
 @{before='<ngayKy>2026-10-25</ngayKy>';after='<ngayKy>2026-10-26</ngayKy>'},
 @{before='<ngayLapTKhai>2026-10-26</ngayLapTKhai>';after='<ngayLapTKhai>2026-10-25</ngayLapTKhai>'},
 @{before='<f0>0</f0><f1>0</f1>';after='<f1>0</f1><f0>0</f0>'},
 @{before='<f0>0</f0>';after='<f0 extra="x">0</f0>'},
 @{before='<f0>0</f0>';after='<f0>0</f0><extra>0</extra>'},
 @{before='<CTieuTKhaiChinh>';after='<CTieuTKhaiChinh>extra'},
 @{before='<maDVu>HTKK</maDVu>';after='<maDVu>OTHER</maDVu>'},
 @{before='0123456789ABCDEF0123456789ABCDEF';after='INVALID'},
 @{before='0123456789ABCDEF0123456789ABCDEF';after='AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'}
)) {Assert-Comparison ([xml]$output.OuterXml.Replace($change.before,$change.after)) $false}
# The rule also works on the same day; no requirement that dates differ.
$inputXml=New-Fixture $true;$inputXml.HSoThueDTu.HSoKhaiThue.TTinChung.TTinTKhaiThue.TKhaiThue.ngayLapTKhai='2026-10-26'
Assert-Comparison $output $true
# The original key is a deterministic function of HSoKhaiThue without TTinDVu (WinDoWorkExportXML):
# a baseline with other content carries another key, and only then may the keys differ.
$inputXml=New-Fixture $true;$inputXml.HSoThueDTu.HSoKhaiThue.CTieuTKhaiChinh.f0='5'
$changed=[xml]$output.OuterXml.Replace('<f0>0</f0>','<f0>5</f0>')
Assert-Comparison ([xml]$changed.OuterXml.Replace('0123456789ABCDEF0123456789ABCDEF','FEDCBA9876543210FEDCBA9876543210')) $true
Assert-Comparison $changed $false
$savedBaseline=$baseline;$baseline=[xml]$baseline.OuterXml.Replace('0123456789ABCDEF0123456789ABCDEF','INVALID')
Assert-Comparison ([xml]$changed.OuterXml.Replace('0123456789ABCDEF0123456789ABCDEF','FEDCBA9876543210FEDCBA9876543210')) $false
$baseline=$savedBaseline
# KHBS: whole tree, output identity and any valid creation date; bounded mask and first differing leaf ordinal.
$khbsWeb=New-Fixture $true;$khbsOut=New-Fixture $false;$khbsCases=0
function Assert-Khbs([xml]$Output,[bool]$Expected,[int]$Mask,[int]$First) { $leaves=0;$mask=0;$first=0;$identity=$false;$date=$false;$actual=[HtkkWebTaxComparison]::CompareKhbs($khbsWeb,$Output,70,[ref]$leaves,[ref]$mask,[ref]$first,[ref]$identity,[ref]$date);if($actual -ne $Expected -or $mask -ne $Mask -or $first -ne $First){throw 'Synthetic KHBS comparison boundary failed'};$script:khbsCases++ }
Assert-Khbs $khbsOut $true 0 0
Assert-Khbs ([xml]$khbsOut.OuterXml.Replace('<f3>0</f3>','<f3>1</f3>')) $false 8 6
Assert-Khbs ([xml]$khbsOut.OuterXml.Replace('<ngayKy>2026-10-25</ngayKy>','<ngayKy>2026-10-26</ngayKy>')) $false 4 2
Assert-Khbs ([xml]$khbsOut.OuterXml.Replace('<ngayLapTKhai>2026-10-26</ngayLapTKhai>','<ngayLapTKhai>bad</ngayLapTKhai>')) $false 128 0
Assert-Khbs ([xml]$khbsOut.OuterXml.Replace('<f0>0</f0>','<f0 extra="x">0</f0>')) $false 2 3
Assert-Khbs ([xml]$khbsOut.OuterXml.Replace('<f0>0</f0>','<f0>0</f0><extra>0</extra>')) $false 1 3
Assert-Khbs ([xml]$khbsOut.OuterXml.Replace('<maDVu>HTKK</maDVu>','<maDVu>OTHER</maDVu>')) $false 128 0
Write-Output ('Synthetic C# web-tax comparison boundaries passed (15 cases, '+$khbsCases+' KHBS cases).')
