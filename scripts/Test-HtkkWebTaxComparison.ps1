# Offline tests of the actual C# comparator, not supplier execution evidence.
$ErrorActionPreference='Stop'
Add-Type -Path (Join-Path $PSScriptRoot 'HtkkWebTaxComparison.cs')
function New-Fixture([bool]$Web) {
 $service=if($Web){'<maDVu>HTKK-WEB-DRAFT</maDVu><tenDVu>Hỗ trợ kê khai — bản nháp</tenDVu><pbanDVu>0.9.2</pbanDVu><ttinNhaCCapDVu>hotrokekhai.net — công cụ hỗ trợ độc lập</ttinNhaCCapDVu>'}else{'<maDVu>HTKK</maDVu><tenDVu>HỖ TRỢ KÊ KHAI THUẾ</tenDVu><pbanDVu>5.8.1</pbanDVu><ttinNhaCCapDVu>0123456789ABCDEF0123456789ABCDEF</ttinNhaCCapDVu>'}
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
Write-Output 'Synthetic C# web-tax comparison boundaries passed (12 cases).'
