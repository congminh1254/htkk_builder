"""Exact fixed synthetic KHBS (kê khai bổ sung lần 1) contract of the web->HTKK amendment case.

Privacy allowlist only, NOT native proof. Same shape as htkk_annex10_web_cases.py: callers validate the
PLuc subtree (PL01_KHBS, PL01_1_KHBS) exactly, then project an IN-MEMORY copy back to the first-declaration
shape (loaiTKhai B -> C, soLan 1 -> 0 after checking them, fragments removed) so the unchanged no-annex
allowlist (fake NNT, M10/2026) plus the case's main-sheet money vector is reused. Raw bytes are never
rewritten, staged or published here. Any other element, attribute, row, amount or string fails closed.
Values: htkk_web scripts/generate-htkk-web-khbs-reference.mjs (khbs-zero-to-sale10): previous version the
all-zero C0, amendment a 10 percent sale of 1.000.000, ngày lập 13/11/2026 (before the 20/11/2026 deadline).
"""
NS='http://kekhaithue.gdt.gov.vn/TKhaiThue'
XSI='http://www.w3.org/2001/XMLSchema-instance'
ZERO_TO_SALE10_CASE='01GTGT-khbs-zero-to-sale10-M10-2026'
# The producer pins ngayLapTKhai, ngayKy and ngày lập KHBS to this fixed day.
FIXED_DATE='2026-11-13'
CODES=frozenset(('NAMESPACE','STRUCTURE','ATTRIBUTES','CONTENT','VALUE','LEAF_COUNT','CASE','HEADER'))
FIELDS=('pluc','fragment','header')
SALE10={'ct32':'1000000','ct33':'100000','ct27':'1000000','ct28':'100000','ct34':'1000000','ct35':'100000','ct36':'100000','ct40a':'100000','ct40':'100000'}

class KhbsWebContractError(ValueError):
 def __init__(self,code,field='pluc'):
  if code not in CODES or field not in FIELDS:raise ValueError('Invalid bounded KHBS web diagnostic')
  self.code=code;self.field=field;self.fieldId=FIELDS.index(field);super().__init__(code)
def reject(code,field='pluc'):raise KhbsWebContractError(code,field)

# Every element of the PLuc subtree in document order: (path below PLuc, sorted 'name=value' attributes,
# text of a leaf or None for a container). Both files must carry these exactly (the native comparison is exact).
ROWS=(
  ('PL01_KHBS', '', None),
  ('PL01_KHBS/Header', '', None),
  ('PL01_KHBS/Header/maTKhai', '', '842'),
  ('PL01_KHBS/Header/tenTKhai', '', 'TỜ KHAI THUẾ GIÁ TRỊ GIA TĂNG (Mẫu số 01/GTGT)'),
  ('PL01_KHBS/Header/maGiaoDich', '', ''),
  ('PL01_KHBS/Header/KyKKhaiThue', '', None),
  ('PL01_KHBS/Header/KyKKhaiThue/kieuKy', '', 'M'),
  ('PL01_KHBS/Header/KyKKhaiThue/kyKKhai', '', '10/2026'),
  ('PL01_KHBS/Header/KyKKhaiThue/kyKKhaiTuNgay', '', '01/10/2026'),
  ('PL01_KHBS/Header/KyKKhaiThue/kyKKhaiDenNgay', '', '31/10/2026'),
  ('PL01_KHBS/Header/KyKKhaiThue/kyKKhaiTuThang', '', ''),
  ('PL01_KHBS/Header/KyKKhaiThue/kyKKhaiDenThang', '', ''),
  ('PL01_KHBS/Header/soLan', '', '1'),
  ('PL01_KHBS/Header/mst', '', '9999999997'),
  ('PL01_KHBS/Header/tenNNT', '', 'NNT KIEM THU GIA LAP - KHONG NOP'),
  ('PL01_KHBS/Header/mstDLyThue', 'xsi:nil=true', ''),
  ('PL01_KHBS/Header/tenDLyThue', '', ''),
  ('PL01_KHBS/Header/soHDongDLyThue', '', ''),
  ('PL01_KHBS/Header/ngayKyHDDLyThue', 'xsi:nil=true', ''),
  ('PL01_KHBS/ma_DonViTien', '', 'VND'),
  ('PL01_KHBS/ten_DonViTien', '', 'Đồng Việt Nam'),
  ('PL01_KHBS/Muc_A', '', None),
  ('PL01_KHBS/Muc_A/Muc_I', '', None),
  ('PL01_KHBS/Muc_A/Muc_I/Muc_1', '', None),
  ('PL01_KHBS/Muc_A/Muc_I/Muc_1/ChiTiet', 'id=ID_1', None),
  ('PL01_KHBS/Muc_A/Muc_I/Muc_1/ChiTiet/ct2_ma', '', '1701'),
  ('PL01_KHBS/Muc_A/Muc_I/Muc_1/ChiTiet/ct2_ten', '', 'Thuế giá trị gia tăng hàng sản xuất, kinh doanh trong nước (gồm cả dịch vụ trong lĩnh vực dầu khí)'),
  ('PL01_KHBS/Muc_A/Muc_I/Muc_1/ChiTiet/ct3', '', '100000'),
  ('PL01_KHBS/Muc_A/Muc_I/Muc_1/tongCong_ct10', '', '100000'),
  ('PL01_KHBS/Muc_A/Muc_I/Muc_2', '', None),
  ('PL01_KHBS/Muc_A/Muc_I/Muc_2/DSachPLuc', '', None),
  ('PL01_KHBS/Muc_A/Muc_I/Muc_2/DSachPLuc/BKePLuc', 'id=ID_1', None),
  ('PL01_KHBS/Muc_A/Muc_I/Muc_2/DSachPLuc/BKePLuc/ma_PLuc', '', ''),
  ('PL01_KHBS/Muc_A/Muc_I/Muc_2/DSachPLuc/BKePLuc/ten_PLuc', '', ''),
  ('PL01_KHBS/Muc_A/Muc_I/Muc_2/DSachPLuc/BKePLuc/CTietPLuc', '', None),
  ('PL01_KHBS/Muc_A/Muc_I/Muc_2/DSachPLuc/BKePLuc/CTietPLuc/ChiTiet', 'id=ID_1', None),
  ('PL01_KHBS/Muc_A/Muc_I/Muc_2/DSachPLuc/BKePLuc/CTietPLuc/ChiTiet/ct2_ma', '', ''),
  ('PL01_KHBS/Muc_A/Muc_I/Muc_2/DSachPLuc/BKePLuc/CTietPLuc/ChiTiet/ct2_ten', '', ''),
  ('PL01_KHBS/Muc_A/Muc_I/Muc_2/DSachPLuc/BKePLuc/CTietPLuc/ChiTiet/ct3_ma', '', ''),
  ('PL01_KHBS/Muc_A/Muc_I/Muc_2/DSachPLuc/BKePLuc/CTietPLuc/ChiTiet/ct3_ten', '', ''),
  ('PL01_KHBS/Muc_A/Muc_I/Muc_2/DSachPLuc/BKePLuc/CTietPLuc/ChiTiet/ma_Xa', '', ''),
  ('PL01_KHBS/Muc_A/Muc_I/Muc_2/DSachPLuc/BKePLuc/CTietPLuc/ChiTiet/ten_Xa', '', ''),
  ('PL01_KHBS/Muc_A/Muc_I/Muc_2/DSachPLuc/BKePLuc/CTietPLuc/ChiTiet/ct04_ma', '', ''),
  ('PL01_KHBS/Muc_A/Muc_I/Muc_2/DSachPLuc/BKePLuc/CTietPLuc/ChiTiet/ct04_ten', '', ''),
  ('PL01_KHBS/Muc_A/Muc_I/Muc_2/DSachPLuc/BKePLuc/CTietPLuc/ChiTiet/ct05_ma', '', ''),
  ('PL01_KHBS/Muc_A/Muc_I/Muc_2/DSachPLuc/BKePLuc/CTietPLuc/ChiTiet/ct05_ten', '', ''),
  ('PL01_KHBS/Muc_A/Muc_I/Muc_2/DSachPLuc/BKePLuc/CTietPLuc/ChiTiet/ct06_ma', '', ''),
  ('PL01_KHBS/Muc_A/Muc_I/Muc_2/DSachPLuc/BKePLuc/CTietPLuc/ChiTiet/ct06_ten', '', ''),
  ('PL01_KHBS/Muc_A/Muc_I/Muc_2/DSachPLuc/BKePLuc/CTietPLuc/ChiTiet/ct7', '', '0'),
  ('PL01_KHBS/Muc_A/Muc_I/Muc_2/DSachPLuc/tongCong_ct11', '', '0'),
  ('PL01_KHBS/Muc_A/Muc_I/Muc_3', '', None),
  ('PL01_KHBS/Muc_A/Muc_I/Muc_3/ct3a_1', '', '2026-11-13'),
  ('PL01_KHBS/Muc_A/Muc_I/Muc_3/ct3a_2', '', '0'),
  ('PL01_KHBS/Muc_A/Muc_I/Muc_3/ct3b', '', '0'),
  ('PL01_KHBS/Muc_A/Muc_II', '', None),
  ('PL01_KHBS/Muc_A/Muc_II/ChiTiet', 'id=ID_1', None),
  ('PL01_KHBS/Muc_A/Muc_II/ChiTiet/ct2_ma', '', ''),
  ('PL01_KHBS/Muc_A/Muc_II/ChiTiet/ct2_ten', '', ''),
  ('PL01_KHBS/Muc_A/Muc_II/ChiTiet/ct3', '', '0'),
  ('PL01_KHBS/Muc_A/Muc_II/tongCong_ct12', '', '0'),
  ('PL01_KHBS/Muc_A/Muc_III', '', None),
  ('PL01_KHBS/Muc_A/Muc_III/ChiTiet', 'id=ID_1', None),
  ('PL01_KHBS/Muc_A/Muc_III/ChiTiet/ct2_ma', '', ''),
  ('PL01_KHBS/Muc_A/Muc_III/ChiTiet/ct2_ten', '', ''),
  ('PL01_KHBS/Muc_A/Muc_III/ChiTiet/ct3', '', '0'),
  ('PL01_KHBS/Muc_A/Muc_III/tongCong_ct13', '', '0'),
  ('PL01_KHBS/Muc_B', '', None),
  ('PL01_KHBS/Muc_B/Muc_I', '', None),
  ('PL01_KHBS/Muc_B/Muc_I/ct_1', '', '0'),
  ('PL01_KHBS/Muc_B/Muc_I/ct_2_so', '', ''),
  ('PL01_KHBS/Muc_B/Muc_I/ct_2_ngay', 'xsi:nil=true', ''),
  ('PL01_KHBS/Muc_B/Muc_I/ct_2_CQT_ma', '', ''),
  ('PL01_KHBS/Muc_B/Muc_I/ct_2_CQT_ten', '', ''),
  ('PL01_KHBS/Muc_B/Muc_I/ct_3_so', '', ''),
  ('PL01_KHBS/Muc_B/Muc_I/ct_3_ngay', 'xsi:nil=true', ''),
  ('PL01_KHBS/Muc_B/Muc_II', '', None),
  ('PL01_KHBS/Muc_B/Muc_II/ct_1', '', '0'),
  ('PL01_KHBS/Muc_B/Muc_II/ct_2', '', '0'),
  ('PL01_1_KHBS', '', None),
  ('PL01_1_KHBS/Header', '', None),
  ('PL01_1_KHBS/Header/maTKhai', '', '842'),
  ('PL01_1_KHBS/Header/tenTKhai', '', 'TỜ KHAI THUẾ GIÁ TRỊ GIA TĂNG (Mẫu số 01/GTGT)'),
  ('PL01_1_KHBS/Header/maGiaoDich', '', ''),
  ('PL01_1_KHBS/Header/KyKKhaiThue', '', None),
  ('PL01_1_KHBS/Header/KyKKhaiThue/kieuKy', '', 'M'),
  ('PL01_1_KHBS/Header/KyKKhaiThue/kyKKhai', '', '10/2026'),
  ('PL01_1_KHBS/Header/KyKKhaiThue/kyKKhaiTuNgay', '', '01/10/2026'),
  ('PL01_1_KHBS/Header/KyKKhaiThue/kyKKhaiDenNgay', '', '31/10/2026'),
  ('PL01_1_KHBS/Header/KyKKhaiThue/kyKKhaiTuThang', '', ''),
  ('PL01_1_KHBS/Header/KyKKhaiThue/kyKKhaiDenThang', '', ''),
  ('PL01_1_KHBS/Header/soLan', '', '1'),
  ('PL01_1_KHBS/Header/mst', '', '9999999997'),
  ('PL01_1_KHBS/Header/tenNNT', '', 'NNT KIEM THU GIA LAP - KHONG NOP'),
  ('PL01_1_KHBS/Header/mstDLyThue', 'xsi:nil=true', ''),
  ('PL01_1_KHBS/Header/tenDLyThue', '', ''),
  ('PL01_1_KHBS/Header/soHDongDLyThue', '', ''),
  ('PL01_1_KHBS/Header/ngayKyHDDLyThue', 'xsi:nil=true', ''),
  ('PL01_1_KHBS/ma_DonViTien', '', 'VND'),
  ('PL01_1_KHBS/ten_DonViTien', '', 'Đồng Việt Nam'),
  ('PL01_1_KHBS/Muc_A', '', None),
  ('PL01_1_KHBS/Muc_A/DSachHSo', '', None),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo', 'id=ID_1', None),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/ma_HSo', '', '0026'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/ten_HSo', '', '01/GTGT'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo', '', None),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet', 'id=ID_1', None),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct2_ma', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct2_ten', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_ma', '', '[27]'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_ten', '', 'Hàng hóa, dịch vụ bán ra chịu thuế giá trị gia tăng - Giá trị HHDV'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_1_ma', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_1_ten', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_2_ma', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_2_ten', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct04', '', '0'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct05', '', '1.000.000'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct06', '', '1000000'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct7', '', '0'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct8', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet', 'id=ID_2', None),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct2_ma', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct2_ten', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_ma', '', '[28]'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_ten', '', 'Hàng hóa, dịch vụ bán ra chịu thuế giá trị gia tăng - Thuế GTGT'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_1_ma', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_1_ten', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_2_ma', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_2_ten', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct04', '', '0'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct05', '', '100.000'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct06', '', '100000'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct7', '', '0'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct8', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet', 'id=ID_3', None),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct2_ma', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct2_ten', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_ma', '', '[32]'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_ten', '', 'Hàng hoá, dịch vụ bán ra chịu thuế suất 10% - Giá trị HHDV'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_1_ma', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_1_ten', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_2_ma', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_2_ten', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct04', '', '0'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct05', '', '1.000.000'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct06', '', '1000000'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct7', '', '0'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct8', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet', 'id=ID_4', None),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct2_ma', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct2_ten', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_ma', '', '[33]'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_ten', '', 'Hàng hoá, dịch vụ bán ra chịu thuế suất 10% - Thuế GTGT'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_1_ma', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_1_ten', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_2_ma', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_2_ten', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct04', '', '0'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct05', '', '100.000'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct06', '', '100000'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct7', '', '0'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct8', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet', 'id=ID_5', None),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct2_ma', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct2_ten', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_ma', '', '[34]'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_ten', '', 'Tổng doanh thu và thuế giá trị gia tăng của hàng hóa, dịch vụ bán ra - Giá trị HHDV'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_1_ma', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_1_ten', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_2_ma', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_2_ten', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct04', '', '0'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct05', '', '1.000.000'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct06', '', '1000000'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct7', '', '0'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct8', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet', 'id=ID_6', None),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct2_ma', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct2_ten', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_ma', '', '[35]'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_ten', '', 'Tổng doanh thu và thuế giá trị gia tăng của hàng hóa, dịch vụ bán ra - Thuế GTGT'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_1_ma', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_1_ten', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_2_ma', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_2_ten', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct04', '', '0'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct05', '', '100.000'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct06', '', '100000'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct7', '', '0'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct8', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet', 'id=ID_7', None),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct2_ma', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct2_ten', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_ma', '', '[36]'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_ten', '', 'Thuế giá trị gia tăng phát sinh trong kỳ'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_1_ma', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_1_ten', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_2_ma', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_2_ten', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct04', '', '0'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct05', '', '100.000'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct06', '', '100000'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct7', '', '0'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct8', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet', 'id=ID_8', None),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct2_ma', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct2_ten', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_ma', '', '[40a]'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_ten', '', 'Thuế giá trị gia tăng phải nộp của hoạt động sản xuất kinh doanh trong kỳ'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_1_ma', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_1_ten', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_2_ma', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_2_ten', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct04', '', '0'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct05', '', '100.000'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct06', '', '100000'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct7', '', '0'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct8', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet', 'id=ID_9', None),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct2_ma', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct2_ten', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_ma', '', '[40]'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_ten', '', 'Thuế giá trị gia tăng còn phải nộp trong kỳ ([40]=[40a]-[40b])'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_1_ma', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_1_ten', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_2_ma', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_2_ten', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct04', '', '0'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct05', '', '100.000'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct06', '', '100000'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct7', '', '100000'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct8', '', ''),
  ('PL01_1_KHBS/Muc_A/DSachHSo/TongCong', '', None),
  ('PL01_1_KHBS/Muc_A/DSachHSo/TongCong/tongCong_7', '', '100000'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/TongCong/tongCong_8', '', '0'),
  ('PL01_1_KHBS/Muc_A/DSachHSo/TongCong/tongCong_9', '', '0'),
  ('PL01_1_KHBS/Muc_B', '', None),
  ('PL01_1_KHBS/Muc_B/CTietTaiLieu', 'id=ID_1', None),
  ('PL01_1_KHBS/Muc_B/CTietTaiLieu/ma_TLieu', '', ''),
  ('PL01_1_KHBS/Muc_B/CTietTaiLieu/ten_TLieu', '', ''),
)
CASES={ZERO_TO_SALE10_CASE:{'rows':ROWS,'money':SALE10,'mainTaxLeaves':70,'fragmentLeaves':200,'taxLeaves':270}}
def is_case(case_id):return case_id in CASES
def tax_leaves(case_id):
 if case_id not in CASES:reject('CASE')
 return CASES[case_id]['taxLeaves']
def money(case_id):
 if case_id not in CASES:reject('CASE')
 return dict(CASES[case_id]['money'])

def _local(node):
 if not isinstance(node.tag,str) or not node.tag.startswith('{'+NS+'}'):reject('NAMESPACE','fragment')
 return node.tag[len(NS)+2:]
def _attributes(node):
 values=[]
 for key,value in node.attrib.items():
  if key=='{'+XSI+'}nil':values.append('xsi:nil='+value)
  elif key.startswith('{'):reject('ATTRIBUTES','fragment')
  else:values.append(key+'='+value)
 return ';'.join(sorted(values))
def _walk(node,path,out):
 here=path+'/'+_local(node) if path else _local(node);children=list(node)
 if (node.tail or '').strip():reject('CONTENT','fragment')
 if children and (node.text or '').strip():reject('CONTENT','fragment')
 out.append((here,_attributes(node),None if children else (node.text or '')))
 if len(out)>len(ROWS):reject('STRUCTURE','fragment')
 for child in children:_walk(child,here,out)

def validate_khbs(root,case_id):
 """Validate the exact PLuc subtree and the B/1 main header of the fixed case. Returns counts."""
 if case_id not in CASES:reject('CASE')
 spec=CASES[case_id];ns='{'+NS+'}'
 plucs=root.findall('./'+ns+'HSoKhaiThue/'+ns+'PLuc')
 if len(plucs)!=1 or plucs[0].attrib or (plucs[0].text or '').strip():reject('STRUCTURE','pluc')
 if tuple(_local(child) for child in plucs[0])!=('PL01_KHBS','PL01_1_KHBS'):reject('STRUCTURE','pluc')
 found=[]
 for child in plucs[0]:_walk(child,'',found)
 if len(found)!=len(spec['rows']):reject('STRUCTURE','fragment')
 for actual,expected in zip(found,spec['rows']):
  if actual[0]!=expected[0] or (actual[2] is None)!=(expected[2] is None):reject('STRUCTURE','fragment')
  if actual[1]!=expected[1]:reject('ATTRIBUTES','fragment')
  if actual[2]!=expected[2]:reject('VALUE','fragment')
 if sum(1 for row in found if row[2] is not None)!=spec['fragmentLeaves']:reject('LEAF_COUNT','fragment')
 head=ns+'HSoKhaiThue/'+ns+'TTinChung/'+ns+'TTinTKhaiThue/'+ns+'TKhaiThue/'
 for name,value in (('loaiTKhai','B'),('soLan','1')):
  nodes=root.findall('./'+head+ns+name)
  if len(nodes)!=1 or nodes[0].attrib or len(nodes[0]) or nodes[0].text!=value:reject('HEADER','header')
 return {'caseId':case_id,'fragmentLeafCount':spec['fragmentLeaves'],'taxLeafCount':spec['taxLeaves']}

def project_first_declaration(root):
 """IN-MEMORY copy only: drop the validated fragments, header B/1 -> C/0, for the unchanged no-annex allowlist."""
 ns='{'+NS+'}';pluc=root.find('./'+ns+'HSoKhaiThue/'+ns+'PLuc')
 if pluc is None or len(pluc)!=2:reject('STRUCTURE','pluc')
 for child in list(pluc):pluc.remove(child)
 pluc.text=None
 head=ns+'HSoKhaiThue/'+ns+'TTinChung/'+ns+'TTinTKhaiThue/'+ns+'TKhaiThue/'
 root.find('./'+head+ns+'loaiTKhai').text='C';root.find('./'+head+ns+'soLan').text='0'
 return root
# The producer manifest's fixed fields for this case (htkk_web generate-htkk-web-khbs-reference.mjs).
MANIFEST={ZERO_TO_SALE10_CASE:{'exporter':'lib/htkk-gtgt01-khbs-xml.ts','producer':'scripts/generate-htkk-web-khbs-reference.mjs','htkkVersion':'5.8.2','soLan':1,'ngayLapKHBS':FIXED_DATE,
 'expected':{'rows':['[27]','[28]','[32]','[33]','[34]','[35]','[36]','[40a]','[40]'],'tongCong_7':'100000','tongCong_ct10':'100000','ct3a_1':FIXED_DATE,'ct3a_2':'0','ct3b':'0','main':{'ct32':'1000000','ct33':'100000','ct40':'100000'}}}}
def manifest_fields(case_id):
 if case_id not in MANIFEST:reject('CASE')
 import copy;return copy.deepcopy(MANIFEST[case_id])
