"""Private, bounded preservation of ORIGINAL GUI zero-case XML; not round-trip proof.

The privacy allowlist does not replace XSD validation or semantic comparison.
Every byte is preserved. Unit fixtures are parser fixtures, never runtime evidence.
"""
import base64,datetime,hashlib,io,json,os,pathlib,re,shutil,urllib.error,urllib.request
import xml.etree.ElementTree as ET
REPO='congminh1254/htkk_web'
BUILDER='congminh1254/htkk_builder'
BRANCH='gtgt-export-reference-evidence'
NS='http://kekhaithue.gdt.gov.vn/TKhaiThue'
XSI='http://www.w3.org/2001/XMLSchema-instance'
MAX_XML=262144
MAX_PROVENANCE=16384
NAMES=('01GTGT.xml','provenance.json')
HELPERS=('HtkkGuiReferenceAutomation.cs','HtkkGtgtReferenceNavigation.cs','HtkkGtgtPeriodAndSheet.cs','HtkkGtgtExportInspection.cs','HtkkGtgtRoundtripInspection.cs','New-HtkkX86ReferenceHost.ps1','Get-HtkkSafeGuiReferenceResult.ps1','probe-htkk-windows.ps1')
FAKE_NAME='NNT KIEM THU GIA LAP - KHONG NOP'
FAKE_SIGNER='NGUOI KY GIA LAP'
FAKE_ADDRESS='DU LIEU GIA LAP KIEM THU KHONG SU DUNG'
ACTIVITY='Hoạt động sản xuất kinh doanh thông thường'
PINS={'Project/HTKK.exe': '411141d2e728a45f4a35a876afb169d0ac2450de2499e8a1f43ac29ab6401938', 'Project/TAX.HTKK.Utilities.dll': 'ccc35605a4d3bb235f896d6ab43cec4c6543a404159cf10897a57cba23d817ec', 'Project/HTKK.exe.config': 'b3547d6a6a61fd6e8e8b64c8976e8702aa94a2b5a44a1cf394c5486162297047', 'Project/Menu.xml': '4ac42eae600f4c98ed3df8a17b6d18770904acff5267913fdc9f98be4a9f24b4', 'InterfaceTemplates/xml/01_GTGT_TT80_xml_283.xml': '7ba334067c52ea22cd744dcf2c0ff444190d6661f6b3e9b3ea08e5ead574830c', 'Project/TAX.HTKK.Business.dll': '281689aaa7df4db33d0debcfc61d32c0c318bb871d4a19a0277d871a7c04bba7', 'Project/TAX.HTKK.ComputeHash.dll': 'd9d63921565ea2039109ad63d71977dcf56889cd83851977a0c712873ab687f5', 'InterfaceTemplates/Validate/01_GTGT_TT80_283.xsd': '8d4c0d88100e858ddfe221d080a6a338776d1364c7de04347bfb990d04833003', 'InterfaceTemplates/excel/01_GTGT_TT80_283.xls': '8ad9ec9f0f3462da75ce4e873e4bb60003947e9edd5d738a5055e37d6c73b310', 'InterfaceTemplates/xml/01_GTGT_TT80_283.xml': '40f5d6f711f7acb69dcc4098e3e3bb0b1849224d1c185902a50b8cae6fc50aae', 'InterfaceIni/Catalogue_DM_NNKD.xml': '8e19468e899e1b6e35a9d584dddd5e278c0daf1127d4f14ac5c4e03b3164ea88'}
SHAPE={'': ('HSoKhaiThue',), 'HSoKhaiThue': ('TTinChung', 'CTieuTKhaiChinh', 'PLuc'), 'HSoKhaiThue/TTinChung': ('TTinDVu', 'TTinTKhaiThue'), 'HSoKhaiThue/TTinChung/TTinDVu': ('maDVu', 'tenDVu', 'pbanDVu', 'ttinNhaCCapDVu'), 'HSoKhaiThue/TTinChung/TTinTKhaiThue': ('TKhaiThue', 'NNT', 'DLyThue'), 'HSoKhaiThue/TTinChung/TTinTKhaiThue/TKhaiThue': ('maTKhai', 'tenTKhai', 'moTaBMau', 'pbanTKhaiXML', 'loaiTKhai', 'soLan', 'KyKKhaiThue', 'maCQTNoiNop', 'tenCQTNoiNop', 'ngayLapTKhai', 'GiaHan', 'nguoiKy', 'ngayKy', 'nganhNgheKD'), 'HSoKhaiThue/TTinChung/TTinTKhaiThue/TKhaiThue/KyKKhaiThue': ('kieuKy', 'kyKKhai', 'kyKKhaiTuNgay', 'kyKKhaiDenNgay', 'kyKKhaiTuThang', 'kyKKhaiDenThang'), 'HSoKhaiThue/TTinChung/TTinTKhaiThue/TKhaiThue/GiaHan': ('maLyDoGiaHan', 'lyDoGiaHan'), 'HSoKhaiThue/TTinChung/TTinTKhaiThue/NNT': ('mst', 'tenNNT', 'dchiNNT', 'phuongXa', 'maHuyenNNT', 'tenHuyenNNT', 'maTinhNNT', 'tenTinhNNT', 'dthoaiNNT', 'faxNNT', 'emailNNT'), 'HSoKhaiThue/TTinChung/TTinTKhaiThue/DLyThue': ('mstDLyThue', 'tenDLyThue', 'dchiDLyThue', 'maHuyenDLyThue', 'tenHuyenDLyThue', 'maTinhDLyThue', 'tenTinhDLyThue', 'dthoaiDLyThue', 'faxDLyThue', 'emailDLyThue', 'soHDongDLyThue', 'ngayKyHDDLyThue', 'NVienDLy'), 'HSoKhaiThue/TTinChung/TTinTKhaiThue/DLyThue/NVienDLy': ('tenNVienDLyThue', 'cchiHNghe'), 'HSoKhaiThue/CTieuTKhaiChinh': ('ma_NganhNghe', 'ten_NganhNghe', 'tieuMucHachToan', 'Header', 'ct21', 'ct22', 'GiaTriVaThueGTGTHHDVMuaVao', 'HangHoaDichVuNhapKhau', 'ct25', 'ct26', 'HHDVBRaChiuThueGTGT', 'ct29', 'HHDVBRaChiuTSuat5', 'HHDVBRaChiuTSuat10', 'ct32a', 'TongDThuVaThueGTGTHHDVBRa', 'ct36', 'ct37', 'ct38', 'ct39a', 'ct40a', 'ct40b', 'ct40', 'ct41', 'ct42', 'ct43'), 'HSoKhaiThue/CTieuTKhaiChinh/Header': ('ct09', 'ct10', 'DiaChiHDSXKDKhacTinhNDTSC'), 'HSoKhaiThue/CTieuTKhaiChinh/Header/DiaChiHDSXKDKhacTinhNDTSC': ('ct11a_phuongXa_ma', 'ct11a_phuongXa_ten', 'ct11b_quanHuyen_ma', 'ct11b_quanHuyen_ten', 'ct11c_tinhTP_ma', 'ct11c_tinhTP_ten'), 'HSoKhaiThue/CTieuTKhaiChinh/GiaTriVaThueGTGTHHDVMuaVao': ('ct23', 'ct24'), 'HSoKhaiThue/CTieuTKhaiChinh/HangHoaDichVuNhapKhau': ('ct23a', 'ct24a'), 'HSoKhaiThue/CTieuTKhaiChinh/HHDVBRaChiuThueGTGT': ('ct27', 'ct28'), 'HSoKhaiThue/CTieuTKhaiChinh/HHDVBRaChiuTSuat5': ('ct30', 'ct31'), 'HSoKhaiThue/CTieuTKhaiChinh/HHDVBRaChiuTSuat10': ('ct32', 'ct33'), 'HSoKhaiThue/CTieuTKhaiChinh/TongDThuVaThueGTGTHHDVBRa': ('ct34', 'ct35')}
LEAF_ORDER=['HSoKhaiThue/TTinChung/TTinDVu/maDVu', 'HSoKhaiThue/TTinChung/TTinDVu/tenDVu', 'HSoKhaiThue/TTinChung/TTinDVu/pbanDVu', 'HSoKhaiThue/TTinChung/TTinDVu/ttinNhaCCapDVu', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/TKhaiThue/maTKhai', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/TKhaiThue/tenTKhai', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/TKhaiThue/moTaBMau', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/TKhaiThue/pbanTKhaiXML', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/TKhaiThue/loaiTKhai', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/TKhaiThue/soLan', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/TKhaiThue/KyKKhaiThue/kieuKy', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/TKhaiThue/KyKKhaiThue/kyKKhai', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/TKhaiThue/KyKKhaiThue/kyKKhaiTuNgay', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/TKhaiThue/KyKKhaiThue/kyKKhaiDenNgay', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/TKhaiThue/KyKKhaiThue/kyKKhaiTuThang', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/TKhaiThue/KyKKhaiThue/kyKKhaiDenThang', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/TKhaiThue/maCQTNoiNop', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/TKhaiThue/tenCQTNoiNop', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/TKhaiThue/ngayLapTKhai', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/TKhaiThue/GiaHan/maLyDoGiaHan', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/TKhaiThue/GiaHan/lyDoGiaHan', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/TKhaiThue/nguoiKy', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/TKhaiThue/ngayKy', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/TKhaiThue/nganhNgheKD', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/NNT/mst', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/NNT/tenNNT', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/NNT/dchiNNT', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/NNT/phuongXa', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/NNT/maHuyenNNT', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/NNT/tenHuyenNNT', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/NNT/maTinhNNT', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/NNT/tenTinhNNT', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/NNT/dthoaiNNT', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/NNT/faxNNT', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/NNT/emailNNT', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/DLyThue/mstDLyThue', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/DLyThue/tenDLyThue', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/DLyThue/dchiDLyThue', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/DLyThue/maHuyenDLyThue', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/DLyThue/tenHuyenDLyThue', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/DLyThue/maTinhDLyThue', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/DLyThue/tenTinhDLyThue', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/DLyThue/dthoaiDLyThue', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/DLyThue/faxDLyThue', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/DLyThue/emailDLyThue', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/DLyThue/soHDongDLyThue', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/DLyThue/ngayKyHDDLyThue', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/DLyThue/NVienDLy/tenNVienDLyThue', 'HSoKhaiThue/TTinChung/TTinTKhaiThue/DLyThue/NVienDLy/cchiHNghe', 'HSoKhaiThue/CTieuTKhaiChinh/ma_NganhNghe', 'HSoKhaiThue/CTieuTKhaiChinh/ten_NganhNghe', 'HSoKhaiThue/CTieuTKhaiChinh/tieuMucHachToan', 'HSoKhaiThue/CTieuTKhaiChinh/Header/ct09', 'HSoKhaiThue/CTieuTKhaiChinh/Header/ct10', 'HSoKhaiThue/CTieuTKhaiChinh/Header/DiaChiHDSXKDKhacTinhNDTSC/ct11a_phuongXa_ma', 'HSoKhaiThue/CTieuTKhaiChinh/Header/DiaChiHDSXKDKhacTinhNDTSC/ct11a_phuongXa_ten', 'HSoKhaiThue/CTieuTKhaiChinh/Header/DiaChiHDSXKDKhacTinhNDTSC/ct11b_quanHuyen_ma', 'HSoKhaiThue/CTieuTKhaiChinh/Header/DiaChiHDSXKDKhacTinhNDTSC/ct11b_quanHuyen_ten', 'HSoKhaiThue/CTieuTKhaiChinh/Header/DiaChiHDSXKDKhacTinhNDTSC/ct11c_tinhTP_ma', 'HSoKhaiThue/CTieuTKhaiChinh/Header/DiaChiHDSXKDKhacTinhNDTSC/ct11c_tinhTP_ten', 'HSoKhaiThue/CTieuTKhaiChinh/ct21', 'HSoKhaiThue/CTieuTKhaiChinh/ct22', 'HSoKhaiThue/CTieuTKhaiChinh/GiaTriVaThueGTGTHHDVMuaVao/ct23', 'HSoKhaiThue/CTieuTKhaiChinh/GiaTriVaThueGTGTHHDVMuaVao/ct24', 'HSoKhaiThue/CTieuTKhaiChinh/HangHoaDichVuNhapKhau/ct23a', 'HSoKhaiThue/CTieuTKhaiChinh/HangHoaDichVuNhapKhau/ct24a', 'HSoKhaiThue/CTieuTKhaiChinh/ct25', 'HSoKhaiThue/CTieuTKhaiChinh/ct26', 'HSoKhaiThue/CTieuTKhaiChinh/HHDVBRaChiuThueGTGT/ct27', 'HSoKhaiThue/CTieuTKhaiChinh/HHDVBRaChiuThueGTGT/ct28', 'HSoKhaiThue/CTieuTKhaiChinh/ct29', 'HSoKhaiThue/CTieuTKhaiChinh/HHDVBRaChiuTSuat5/ct30', 'HSoKhaiThue/CTieuTKhaiChinh/HHDVBRaChiuTSuat5/ct31', 'HSoKhaiThue/CTieuTKhaiChinh/HHDVBRaChiuTSuat10/ct32', 'HSoKhaiThue/CTieuTKhaiChinh/HHDVBRaChiuTSuat10/ct33', 'HSoKhaiThue/CTieuTKhaiChinh/ct32a', 'HSoKhaiThue/CTieuTKhaiChinh/TongDThuVaThueGTGTHHDVBRa/ct34', 'HSoKhaiThue/CTieuTKhaiChinh/TongDThuVaThueGTGTHHDVBRa/ct35', 'HSoKhaiThue/CTieuTKhaiChinh/ct36', 'HSoKhaiThue/CTieuTKhaiChinh/ct37', 'HSoKhaiThue/CTieuTKhaiChinh/ct38', 'HSoKhaiThue/CTieuTKhaiChinh/ct39a', 'HSoKhaiThue/CTieuTKhaiChinh/ct40a', 'HSoKhaiThue/CTieuTKhaiChinh/ct40b', 'HSoKhaiThue/CTieuTKhaiChinh/ct40', 'HSoKhaiThue/CTieuTKhaiChinh/ct41', 'HSoKhaiThue/CTieuTKhaiChinh/ct42', 'HSoKhaiThue/CTieuTKhaiChinh/ct43']
BASE_HEADER={'TTinDVu/maDVu': 'HTKK', 'TTinDVu/tenDVu': 'HỖ TRỢ KÊ KHAI THUẾ', 'TTinDVu/pbanDVu': '5.8.1', 'TTinDVu/ttinNhaCCapDVu': 'TỔNG CỤC THUẾ HÀ NỘI', 'TTinTKhaiThue/TKhaiThue/maTKhai': '842', 'TTinTKhaiThue/TKhaiThue/tenTKhai': 'TỜ KHAI THUẾ GIÁ TRỊ GIA TĂNG (Mẫu số 01/GTGT)', 'TTinTKhaiThue/TKhaiThue/moTaBMau': '(Ban hành kèm theo Thông tư số 80/2021/TT-BTC ngày 29 tháng 9 năm 2021 của Bộ trưởng Bộ Tài chính)', 'TTinTKhaiThue/TKhaiThue/pbanTKhaiXML': '2.8.3', 'TTinTKhaiThue/TKhaiThue/loaiTKhai': None, 'TTinTKhaiThue/TKhaiThue/soLan': None, 'TTinTKhaiThue/TKhaiThue/KyKKhaiThue/kieuKy': 'M', 'TTinTKhaiThue/TKhaiThue/KyKKhaiThue/kyKKhai': '10/2026', 'TTinTKhaiThue/TKhaiThue/KyKKhaiThue/kyKKhaiTuNgay': '', 'TTinTKhaiThue/TKhaiThue/KyKKhaiThue/kyKKhaiDenNgay': '', 'TTinTKhaiThue/TKhaiThue/KyKKhaiThue/kyKKhaiTuThang': '', 'TTinTKhaiThue/TKhaiThue/KyKKhaiThue/kyKKhaiDenThang': '', 'TTinTKhaiThue/TKhaiThue/maCQTNoiNop': '', 'TTinTKhaiThue/TKhaiThue/tenCQTNoiNop': '', 'TTinTKhaiThue/TKhaiThue/ngayLapTKhai': '', 'TTinTKhaiThue/TKhaiThue/GiaHan/maLyDoGiaHan': '', 'TTinTKhaiThue/TKhaiThue/GiaHan/lyDoGiaHan': '', 'TTinTKhaiThue/TKhaiThue/nguoiKy': 'SYNTHETIC SIGNER', 'TTinTKhaiThue/TKhaiThue/ngayKy': None, 'TTinTKhaiThue/TKhaiThue/nganhNgheKD': '', 'TTinTKhaiThue/NNT/mst': '9999999997', 'TTinTKhaiThue/NNT/tenNNT': 'SYNTHETIC & <NNT> ĐỐI CHIẾU', 'TTinTKhaiThue/NNT/dchiNNT': 'SYNTHETIC ADDRESS', 'TTinTKhaiThue/NNT/phuongXa': '', 'TTinTKhaiThue/NNT/maHuyenNNT': '9100001', 'TTinTKhaiThue/NNT/tenHuyenNNT': '', 'TTinTKhaiThue/NNT/maTinhNNT': '', 'TTinTKhaiThue/NNT/tenTinhNNT': '', 'TTinTKhaiThue/NNT/dthoaiNNT': '', 'TTinTKhaiThue/NNT/faxNNT': '', 'TTinTKhaiThue/NNT/emailNNT': '', 'TTinTKhaiThue/DLyThue/mstDLyThue': '', 'TTinTKhaiThue/DLyThue/tenDLyThue': '', 'TTinTKhaiThue/DLyThue/dchiDLyThue': '', 'TTinTKhaiThue/DLyThue/maHuyenDLyThue': '', 'TTinTKhaiThue/DLyThue/tenHuyenDLyThue': '', 'TTinTKhaiThue/DLyThue/maTinhDLyThue': '', 'TTinTKhaiThue/DLyThue/tenTinhDLyThue': '', 'TTinTKhaiThue/DLyThue/dthoaiDLyThue': '', 'TTinTKhaiThue/DLyThue/faxDLyThue': '', 'TTinTKhaiThue/DLyThue/emailDLyThue': '', 'TTinTKhaiThue/DLyThue/soHDongDLyThue': '', 'TTinTKhaiThue/DLyThue/ngayKyHDDLyThue': '', 'TTinTKhaiThue/DLyThue/NVienDLy/tenNVienDLyThue': '', 'TTinTKhaiThue/DLyThue/NVienDLy/cchiHNghe': ''}
OPTIONAL=frozenset(('HSoKhaiThue/PLuc','HSoKhaiThue/TTinChung/TTinTKhaiThue/DLyThue'))
REASONS=frozenset(('SIZE','ENCODING','DECLARATION','XML_PARSE','ROOT','NAMESPACE','ATTRIBUTES','STRUCTURE','XML_CONTENT','VALUE_MISMATCH','DATE_VALUE','DATE_STALE','FILES','FILE_UNSAFE','PROVENANCE','HASH','HELPER_UNSAFE','GIT_OBJECT','PRIVATE_REPO','PUBLISH_FILES','BUILDER','API_AUTH','API_HTTP','NETWORK','IO','INTERNAL'))
SHAPES=frozenset(('empty','whitespace-only','zero','false','date','uppercase-md5','other'))
class EvidenceError(ValueError):
 def __init__(self,reason,**context):
  if reason not in REASONS:raise ValueError('Invalid safe reason')
  self.reason=reason;self.context=safe_context(context);super().__init__(reason)
def safe_context(context):
 result={}
 for key,maximum in (('leafIndex',len(LEAF_ORDER)),('observedLeafCount',1024),('httpStatus',599)):
  value=context.get(key)
  if type(value) is int and (100 if key=='httpStatus' else 0)<=value<=maximum:result[key]=value
 if isinstance(context.get('valueShape'),str) and context['valueShape'] in SHAPES:result['valueShape']=context['valueShape']
 return result
def safe_failure(error,stage):
 reason='INTERNAL';context={}
 if isinstance(error,EvidenceError):reason=error.reason if error.reason in REASONS else 'INTERNAL';context=safe_context(error.context if isinstance(error.context,dict) else {})
 elif isinstance(error,urllib.error.HTTPError):reason='API_AUTH' if error.code in (401,403) else 'API_HTTP';context={'httpStatus':error.code} if 100<=error.code<=599 else {}
 elif isinstance(error,urllib.error.URLError):reason='NETWORK'
 elif isinstance(error,OSError):reason='IO'
 return {'format':'htkk-gtgt-export-publication-status-v1','status':'rejected','stage':stage if stage in ('read','publish') else 'unknown','reason':reason,**context}
def value_shape(value):
 if value=='':return 'empty'
 if value.isspace():return 'whitespace-only'
 if re.fullmatch(r'0(?:\.0{1,8})?',value):return 'zero'
 if value in ('false','0'):return 'false'
 if re.fullmatch(r'\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}',value):return 'date'
 if re.fullmatch('[0-9A-F]{32}',value):return 'uppercase-md5'
 return 'other'
def fail_value(path,value):raise EvidenceError('VALUE_MISMATCH',leafIndex=LEAF_ORDER.index(path)+1 if path in LEAF_ORDER else 0,valueShape=value_shape(value))
def validate_date(value,today,path,allow_empty=False):
 if allow_empty and not value.strip():return
 try:
  if re.fullmatch(r'\d{4}-\d{2}-\d{2}',value):date=datetime.date.fromisoformat(value)
  elif re.fullmatch(r'\d{2}/\d{2}/\d{4}',value):date=datetime.datetime.strptime(value,'%d/%m/%Y').date()
  else:raise ValueError()
 except ValueError:raise EvidenceError('DATE_VALUE',leafIndex=LEAF_ORDER.index(path)+1,valueShape=value_shape(value)) from None
 if abs((today-date).days)>1:raise EvidenceError('DATE_STALE',leafIndex=LEAF_ORDER.index(path)+1,valueShape='date')
def expected_values():
 prefix='HSoKhaiThue/TTinChung/'
 expected={prefix+path:(value,) for path,value in BASE_HEADER.items()}
 def header(path,*values):expected[prefix+path]=values
 header('TTinDVu/ttinNhaCCapDVu','@SOURCE_MD5')
 header('TTinTKhaiThue/TKhaiThue/loaiTKhai','C');header('TTinTKhaiThue/TKhaiThue/soLan','0')
 # ORIGINAL frmHTKKPeriod.GetPeriodInfo initializes explicit bounds for M10/2026.
 # This is the selected period, not an arbitrary fresh/current date allowance.
 header('TTinTKhaiThue/TKhaiThue/KyKKhaiThue/kyKKhaiTuNgay','2026-10-01','01/10/2026')
 header('TTinTKhaiThue/TKhaiThue/KyKKhaiThue/kyKKhaiDenNgay','2026-10-31','31/10/2026')
 header('TTinTKhaiThue/TKhaiThue/nguoiKy',FAKE_SIGNER)
 header('TTinTKhaiThue/TKhaiThue/ngayKy','@DATE');header('TTinTKhaiThue/TKhaiThue/ngayLapTKhai','@OPTIONAL_DATE')
 header('TTinTKhaiThue/TKhaiThue/nganhNgheKD','',ACTIVITY)
 header('TTinTKhaiThue/TKhaiThue/maCQTNoiNop','10129');header('TTinTKhaiThue/TKhaiThue/tenCQTNoiNop','Thuế cơ sở 16 Thành phố Hà Nội')
 header('TTinTKhaiThue/NNT/tenNNT',FAKE_NAME);header('TTinTKhaiThue/NNT/dchiNNT',FAKE_ADDRESS)
 header('TTinTKhaiThue/NNT/maHuyenNNT','','10129','10129087');header('TTinTKhaiThue/NNT/tenHuyenNNT','','Phường Sơn Tây')
 header('TTinTKhaiThue/NNT/maTinhNNT','101');header('TTinTKhaiThue/NNT/tenTinhNNT','Thành phố Hà Nội')
 for path in LEAF_ORDER:
  if path.startswith('HSoKhaiThue/CTieuTKhaiChinh/'):
   leaf=path.rsplit('/',1)[1]
   if leaf=='ma_NganhNghe':expected[path]=('00',)
   elif leaf=='ten_NganhNghe':expected[path]=(ACTIVITY,)
   elif leaf=='tieuMucHachToan':expected[path]=('1701',)
   elif leaf=='ct21':expected[path]=('false','0')
   elif '/Header/' not in path:expected[path]=('@ZERO',)
   else:expected[path]=('',)
 return expected
EXPECTED=expected_values()
def validate_xml(body,today=None):
 if not isinstance(body,bytes) or not 0<len(body)<=MAX_XML:raise EvidenceError('SIZE')
 try:text=body.decode('utf-8-sig')
 except UnicodeError:raise EvidenceError('ENCODING') from None
 if re.search(r'<!|<\?(?!xml\s)',text,re.I) or text.count('<?')>1:raise EvidenceError('DECLARATION')
 try:
  for event,(prefix,uri) in ET.iterparse(io.BytesIO(body),events=('start-ns',)):
   if (prefix,uri) not in (('',NS),('xsi',XSI)):raise EvidenceError('NAMESPACE')
  root=ET.fromstring(body,parser=ET.XMLParser(target=ET.TreeBuilder(insert_comments=True,insert_pis=True)))
 except ET.ParseError:raise EvidenceError('XML_PARSE') from None
 if root.tag!='{'+NS+'}HSoThueDTu':raise EvidenceError('ROOT')
 observed={};today=today or datetime.datetime.now(datetime.timezone.utc).date()
 def visit(node,path):
  if not isinstance(node.tag,str) or not node.tag.startswith('{'+NS+'}'):raise EvidenceError('NAMESPACE')
  attrs={'id':'ID_1'} if path=='HSoKhaiThue' else {}
  if node.attrib!=attrs:raise EvidenceError('ATTRIBUTES')
  if (node.tail or '').strip():raise EvidenceError('XML_CONTENT')
  if path in SHAPE:
   if (node.text or '').strip():raise EvidenceError('XML_CONTENT')
   children=[child.tag[len(NS)+2:] if isinstance(child.tag,str) and child.tag.startswith('{'+NS+'}') else None for child in node]
   required=list(SHAPE[path]);present=set(children)
   filtered=[name for name in required if (path+'/'+name if path else name) not in OPTIONAL or name in present]
   if children!=filtered:raise EvidenceError('STRUCTURE',observedLeafCount=len(observed))
   for child,name in zip(node,children):visit(child,path+'/'+name if path else name)
  elif path=='HSoKhaiThue/PLuc':
   if len(node) or (node.text or '').strip():raise EvidenceError('STRUCTURE')
  else:
   if len(node) or path not in EXPECTED or path in observed:raise EvidenceError('STRUCTURE',observedLeafCount=len(observed))
   value=node.text or '';observed[path]=value;allowed=EXPECTED[path]
   if '@SOURCE_MD5' in allowed:
    # GenerateKey -> EncryptText -> ObjectToByteArray -> MD5, X2 formatting.
    # Source ComputeHash.dll d9d639...; hash privacy check, not a signature claim.
    if not re.fullmatch('[0-9A-F]{32}',value):fail_value(path,value)
   elif '@DATE' in allowed:validate_date(value,today,path)
   elif '@OPTIONAL_DATE' in allowed:validate_date(value,today,path,True)
   elif '@ZERO' in allowed:
    if not re.fullmatch(r'0(?:\.0{1,8})?',value):fail_value(path,value)
   elif value not in allowed and not ('' in allowed and value.isspace()):fail_value(path,value)
 visit(root,'')
 return {'leafCount':len(observed),'privacyValuesVerified':True}
def exact(value,keys):
 if not isinstance(value,dict) or set(value)!=set(keys):raise EvidenceError('PROVENANCE')
def safe_file(path,maximum):
 if path.is_symlink() or not path.is_file() or not 0<path.stat().st_size<=maximum:raise EvidenceError('FILE_UNSAFE')
 with path.open('rb') as stream:body=stream.read(maximum+1)
 if not 0<len(body)<=maximum:raise EvidenceError('FILE_UNSAFE')
 return body
def read_evidence(directory,run_id,builder_commit,today=None):
 if not isinstance(run_id,str) or not re.fullmatch('[0-9]{1,20}',run_id) or not isinstance(builder_commit,str) or not re.fullmatch('[0-9a-f]{40}',builder_commit):raise EvidenceError('PROVENANCE')
 if directory.is_symlink() or not directory.is_dir() or set(path.name for path in directory.iterdir())!=set(NAMES):raise EvidenceError('FILES')
 body=safe_file(directory/NAMES[0],MAX_XML)
 try:provenance=json.loads(safe_file(directory/NAMES[1],MAX_PROVENANCE).decode('utf-8-sig'))
 except (UnicodeError,json.JSONDecodeError):raise EvidenceError('PROVENANCE') from None
 expected={'format':'htkk-gtgt-export-staging-v1','builderRepository':BUILDER,'builderCommit':builder_commit,'runId':run_id,'sourceVersion':'5.8.1','runtimeHost':'clr2-x86-reference','originalSourcesUnmodified':True,'inputsSynthetic':True,'guiExportInvoked':True,'originalExportSucceeded':True,'originalExporterValidatedSchema':True,'fullRoundTrip':False,'originalOutputSha256':hashlib.sha256(body).hexdigest(),'originalOutputBytes':len(body)}
 exact(provenance,expected)
 if any(type(provenance[key]) is not type(value) or provenance[key]!=value for key,value in expected.items()):raise EvidenceError('PROVENANCE')
 privacy=validate_xml(body,today)
 helpers={}
 for name in HELPERS:
  helpers['scripts/'+name]=hashlib.sha256(safe_file(pathlib.Path(__file__).with_name(name),262144)).hexdigest()
 manifest={'format':'htkk-gtgt-export-reference-evidence-v1','sourceVersion':'5.8.1','sourcePins':PINS,'helperSha256':helpers,'builderRepository':BUILDER,'builderCommit':builder_commit,'runId':run_id,'runtimeHost':'clr2-x86-reference','scope':'original-gui-zero-export-only','inputsSynthetic':True,'guiExportInvoked':True,'schemaVerifiedByOriginalExporter':True,'independentSchemaVerification':False,'semanticComparisonPassed':False,'htkkImportPassed':False,'fullRoundTrip':False,'privacyCheck':privacy,'files':{'01GTGT.xml':{'sha256':hashlib.sha256(body).hexdigest(),'bytes':len(body)}}}
 return {'01GTGT.xml':body,'manifest.json':(json.dumps(manifest,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode()}
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args):return None
def api(path,token,payload=None,method=None):
 request=urllib.request.Request('https://api.github.com/repos/'+REPO+path,data=json.dumps(payload).encode() if payload is not None else None,headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','User-Agent':'HTKK-Private-GTGT-Export-Evidence/1.0'},method=method or ('POST' if payload is not None else 'GET'))
 with urllib.request.build_opener(NoRedirect()).open(request,timeout=30) as response:return json.load(response)
def sha(value):
 if not isinstance(value,str) or not re.fullmatch('[0-9a-f]{40}',value):raise EvidenceError('GIT_OBJECT')
 return value
def publish(files,token):
 if set(files)!=set(('01GTGT.xml','manifest.json')) or any(not isinstance(body,bytes) or not 0<len(body)<=MAX_XML for body in files.values()):raise EvidenceError('PUBLISH_FILES')
 # No API request occurs until XML and the complete generated manifest match.
 privacy=validate_xml(files['01GTGT.xml'])
 try:manifest=json.loads(files['manifest.json'])
 except (UnicodeError,json.JSONDecodeError):raise EvidenceError('PUBLISH_FILES') from None
 expected={'format':'htkk-gtgt-export-reference-evidence-v1','sourceVersion':'5.8.1','sourcePins':PINS,'helperSha256':{'scripts/'+name:hashlib.sha256(safe_file(pathlib.Path(__file__).with_name(name),262144)).hexdigest() for name in HELPERS},'builderRepository':BUILDER,'builderCommit':manifest.get('builderCommit') if isinstance(manifest,dict) else None,'runId':manifest.get('runId') if isinstance(manifest,dict) else None,'runtimeHost':'clr2-x86-reference','scope':'original-gui-zero-export-only','inputsSynthetic':True,'guiExportInvoked':True,'schemaVerifiedByOriginalExporter':True,'independentSchemaVerification':False,'semanticComparisonPassed':False,'htkkImportPassed':False,'fullRoundTrip':False,'privacyCheck':privacy,'files':{'01GTGT.xml':{'sha256':hashlib.sha256(files['01GTGT.xml']).hexdigest(),'bytes':len(files['01GTGT.xml'])}}}
 exact(manifest,expected)
 if not isinstance(expected['builderCommit'],str) or not re.fullmatch('[0-9a-f]{40}',expected['builderCommit']) or not isinstance(expected['runId'],str) or not re.fullmatch('[0-9]{1,20}',expected['runId']):raise EvidenceError('PUBLISH_FILES')
 if any(type(manifest[key]) is not type(value) or manifest[key]!=value for key,value in expected.items()):raise EvidenceError('PUBLISH_FILES')
 info=api('',token)
 if info.get('private') is not True or info.get('full_name')!=REPO:raise EvidenceError('PRIVATE_REPO')
 entries=[]
 for name,body in files.items():entries.append({'path':name,'mode':'100644','type':'blob','sha':sha(api('/git/blobs',token,{'content':base64.b64encode(body).decode(),'encoding':'base64'})['sha'])})
 tree=sha(api('/git/trees',token,{'tree':entries})['sha'])
 commit=sha(api('/git/commits',token,{'message':'Private synthetic original GUI zero export; no import or round-trip claim','tree':tree,'parents':[]})['sha'])
 try:api('/git/ref/heads/'+BRANCH,token)
 except urllib.error.HTTPError as error:
  if error.code!=404:raise
  api('/git/refs',token,{'ref':'refs/heads/'+BRANCH,'sha':commit})
 else:api('/git/refs/heads/'+BRANCH,token,{'sha':commit,'force':True},'PATCH')
 return commit
def main():
 directory=pathlib.Path(os.environ['RUNNER_TEMP'])/'htkk-gtgt-export-evidence'
 if not directory.exists():
  print(json.dumps({'format':'htkk-gtgt-export-publication-status-v1','status':'unavailable','stage':'read','reason':'FILES'},separators=(',',':')));raise SystemExit('Original GUI export evidence unavailable.')
 stage='read'
 try:
  if os.environ.get('GITHUB_REPOSITORY')!=BUILDER:raise EvidenceError('BUILDER')
  files=read_evidence(directory,os.environ['GITHUB_RUN_ID'],os.environ['GITHUB_SHA']);stage='publish';commit=publish(files,os.environ['SOURCE_PUBLISH_TOKEN']);print('Private original GUI zero export published: '+commit)
 except Exception as error:
  print(json.dumps(safe_failure(error,stage),separators=(',',':')));raise SystemExit('Private GUI export evidence publication failed; no XML, path or raw remote error published.')
 finally:
  if not directory.is_symlink():shutil.rmtree(directory,ignore_errors=True)
if __name__=='__main__':main()
