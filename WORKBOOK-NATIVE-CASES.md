# Ca native ứng viên cho 03/TNDN và BCTC

> Cập nhật: `03TNDN-profit20-Y2025`, `BCTC133-B01a-basic-Y2025`, `BCTC200-LT-basic-Y2025` đã được đăng ký
> (releaseGate false) với driver chung `declaration-web-import-inspect` — xem `DECLARATION-NATIVE-CASES.md`.
> `03TNDN-loss-c3b-Y2025` vẫn chỉ là ứng viên. Bản sao plan này giữ nguyên (driverImplemented=false là cờ của plan thiết kế).

`scripts/htkk-workbook-native-cases.json` là bản sao ghim SHA-256 của
`htkk_web/data/htkk-workbook-native-cases.json` (nhánh `work/forms-tndn`). Bốn ca tổng hợp,
chỉ dùng MST giả lập `9999999997`:

| caseId | Menu | Phụ lục | Mục đích |
|---|---|---|---|
| `03TNDN-profit20-Y2025` | N8 (03/TNDN TT80, XML 2.9.4) | 03-1A | lãi, thuế suất 20%, tạm nộp G1 |
| `03TNDN-loss-c3b-Y2025` | N8 | 03-2 | C3a/C3b, điều kiện mở khóa `LockUnLockC3bTK` |
| `BCTC133-B01a-basic-Y2025` | A2 (B01a-DNN TT133, XML 2.3.2) | 01-1 | tổng tài sản/nguồn vốn, B02 |
| `BCTC200-LT-basic-Y2025` | 78 (BCTC TT200, XML 2.2.6) | 01-1 | nhánh hoạt động liên tục |

`htkk_workbook_native_cases.py` chỉ kiểm tra offline (định danh giả lập, đơn vị Menu.xml,
kỳ, phụ lục, đường dẫn kỳ vọng). Các ca **không** nằm trong `htkk-native-cases.json`,
không có trong `web_case_id` của `probe-htkk-windows.yml`, và `driverImplemented=false`.

## Việc còn thiếu trước khi dispatch

Driver hiện có (`gtgt-web-import-inspect`) chỉ đi chuỗi menu `101 → 101_1 → D1` và hộp kỳ
tháng/quý. Cần một driver mới (đề xuất `workbook-web-import-inspect`) với:

1. Chuỗi menu `101 → 101_2 → N8` hoặc `101 → 101_6 → A2/78`.
2. Hộp chọn kỳ năm 2025 (KieuKy 11/26), từ 01/01/2025 đến 31/12/2025, và danh sách phụ lục
   đúng `selected` của ca; với 78 chọn "doanh nghiệp hoạt động liên tục" (LT).
3. Nhập XML bản nháp do web sinh ra, ghi, kết xuất XML gốc và so sánh các lá trong `expected`.
4. Các stage/flag mới trong `generate-native-automation-registry.py` và test hợp đồng tương ứng.

Chỉ sau khi driver được review và ca được thêm vào `htkk-native-cases.json` (releaseGate
`false` trước) thì PM mới dispatch `probe-htkk-windows.yml` với `web_case_id` tương ứng.
