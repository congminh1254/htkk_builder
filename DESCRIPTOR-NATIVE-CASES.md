# Ca native thiết kế cho họ descriptor: TNCN (05/KK, 05/QTT, 02/QTT) và NTNN (01/NTNN TT80)

> Cập nhật: `05KK-withheld-Q3-2026`, `05QTT-two-employees-Y2025`, `02QTT-dependants-Y2025`, `01NTNN-two-contractors-M09-2026`, `03NTNN-no-rate-M10-2026`, `01NTNN-NCCNN-entry-M10-2026`, `04NTNN-TT80-one-subcontractor-2026`, `04NTNN-TT89-one-subcontractor-2026`, `02NTNN-TT89-two-annexes-2026`, `02NTNN-TT80-two-annexes-2026` và ba ca kỳ lần phát sinh `01NTNN-occurrence-D20-09-2026`, `01NTNN-NCCNN-occurrence-D20-10-2026` (nhập tay), `03NTNN-occurrence-D20-10-2026` (`01NTNN-NCCNN-entry-M10-2026` nhập tay; thay ca import `01NTNN-NCCNN-two-parts-M10-2026`, nay chỉ còn là ca thiết kế, release 242) đã được đăng ký (releaseGate false) với driver
> chung `declaration-web-import-inspect` — xem `DECLARATION-NATIVE-CASES.md`. Các ca còn lại vẫn design-only.

Nguồn: `htkk-net/htkk_web` nhánh `work/forms-tncn` (`docs/NGHIEP-VU-TNCN.md`). Đây là
**thiết kế** sáu ca giả lập (MST 9999999997), không phải bằng chứng native.

| Ca | Menu | Kỳ | Phụ lục | Chế độ |
|---|---|---|---|---|
| `05KK-zero-Q3-2026` | L7 (05/KK-TNCN, XML 2.9.3) | quý 3/2026 | — | web XML → Nhập từ XML → Kết xuất |
| `05KK-withheld-Q3-2026` | L7 | quý 3/2026 | — | như trên, có số (kiểm ROUND [32]) |
| `05KK-TT89-zero-Q4-2026` | Z8 (05/KK-TNCN TT89, XML 3.0.9, chỉ HTKK 5.8.2: `htkkVersion` trên adapter và ca) | quý 4/2026 | — | web XML → Nhập từ XML → Kết xuất |
| `05KK-TT89-withheld-Q4-2026` | Z8 | quý 4/2026 | — | như trên, có số (kiểm [35] = ROUND([23]×10%)) |
| `05QTT-zero-Y2025` | B9 (05/QTT-TNCN, XML 2.9.3) | 2025 | — | như trên |
| `05QTT-two-employees-Y2025` | B9 | 2025 | 05-1 (2 dòng), 05-3 (1 dòng) | như trên |
| `02QTT-zero-Y2025` | B8 (02/QTT-TNCN, XML 2.7.3) | 2025 | — | nhập tay trong HTKK → Kết xuất XML gốc |
| `02QTT-dependants-Y2025` | B8 | 2025 | 02-1 (2 dòng) | như trên |
| `01NTNN-zero-M09-2026` | I9 (01/NTNN TT80, XML 2.5.1) | tháng 09/2026 | — (1 nhà thầu có tên, số 0; checkTKChinh E_13/E_37) | web XML → Nhập từ XML → Kết xuất |
| `01NTNN-two-contractors-M09-2026` | I9 | tháng 09/2026 | — (2 nhà thầu trong bảng chính) | như trên, có số (GTGT/TNDN theo tỷ lệ) |
| `01NTNN-NCCNN-zero-M10-2026` | Y8 (01/NTNN, NCCNN TT89, XML 3.0.9) | tháng 10/2026 | — (phần I, 1 nhà thầu có tên, số 0) | web XML → Nhập từ XML → Kết xuất |
| `01NTNN-NCCNN-two-parts-M10-2026` | Y8 | tháng 10/2026 | — (phần II: NCCNN + cá nhân không cư trú) | như trên, có số (GTGT, TNDN, TNCN) |
| `01NTNN-NCCNN-entry-zero-M10-2026` | Y8, adapter `-entry` | tháng 10/2026 | — (chỉ tích M8) | chỉ thiết kế: `original-entry-export` |
| `01NTNN-NCCNN-entry-M10-2026` | Y8, adapter `-entry` | tháng 10/2026 | — (như two-parts) | `original-entry-export`: gõ vào lưới gốc → Kết xuất (DECLARATION-NATIVE-CASES.md) |
| `03NTNN-zero-M10-2026` | J1 (03/NTNN, XML 3.0.8) | tháng 10/2026 | — (1 dòng có (1a)/(1b), số 0; checkTKChinh E_13/E_30) | web XML → Nhập từ XML → Kết xuất |
| `03NTNN-no-rate-M10-2026` | J1 | tháng 10/2026 | — (2 dòng, tỷ lệ [9] = 0: FinishImportXML xóa tỷ lệ khi nhập) | như trên, có số tiền (6)/(8) |
| `04NTNN-TT80-zero-2026` | D6 (04/NTNN TT80, XML 3.0.8, KieuKy 22) | 01/01/2026–30/09/2026 (`range`) | — (số/ngày hợp đồng, số 0) | chỉ thiết kế |
| `04NTNN-TT80-one-subcontractor-2026` | D6 | 01/01/2026–30/09/2026 | 02-2/NTNN (1 nhà thầu phụ, Hà Nội) | web XML → Nhập từ XML → Kết xuất |
| `04NTNN-TT89-one-subcontractor-2026` | Y1 (04/NTNN TT89, XML 3.0.9, KieuKy 22) | 01/07/2026–30/09/2026 | 02-2/NTNN (1 nhà thầu phụ) | như trên (không có ca 0: Header B42) |
| `02NTNN-TT89-two-annexes-2026` | X9 (02/NTNN TT89, XML 3.0.9, KieuKy 22) | 01/07/2026–30/09/2026 | 02-1/NTNN (1 nhà thầu, Nhật/JP), 02-2/NTNN (1 nhà thầu phụ) | web XML → Nhập từ XML → Kết xuất (không có ca 0: Header B55) |
| `02NTNN-TT80-zero-2026` | C9 (02/NTNN TT80, XML 2.5.1, KieuKy 22) | 01/01/2026–30/09/2026 | — (số/ngày hợp đồng, số 0) | chỉ thiết kế |
| `02NTNN-TT80-two-annexes-2026` | C9 | 01/01/2026–30/09/2026 | 02-1/NTNN (1 nhà thầu: JP, địa điểm 101), 02-2/NTNN (1 nhà thầu phụ, địa điểm 103) | web XML → Nhập từ XML → Kết xuất |
| `01NTNN-occurrence-D20-09-2026` | I9 (KieuKy 18 lần phát sinh, kiểu `day`) | ngày 20/09/2026 | — (hai nhà thầu như ca tháng; ct6 = ngày phát sinh) | web XML → Nhập từ XML → Kết xuất |
| `01NTNN-NCCNN-occurrence-D20-10-2026` | Y8 | ngày 20/10/2026 | — (phần II như ca nhập tay tháng; AE gõ 20/10/2026) | nhập tay → Kết xuất |
| `03NTNN-occurrence-D20-10-2026` | J1 | ngày 20/10/2026 | — (hai dòng tỷ lệ 0 như ca tháng; ct7 = ngày phát sinh) | web XML → Nhập từ XML → Kết xuất |

- `scripts/htkk-descriptor-native-cases.json` + `scripts/htkk_descriptor_native_cases.py`:
  registry riêng, `status=design-only`, `dispatchable=false`, `releaseGate=false`. Validator
  từ chối mọi thay đổi identity menu/class/XML/XSD, kỳ, phụ lục, giá trị ngoài số nguyên/MST
  giả lập, và mọi cờ khiến ca dispatch được. Không đụng `htkk-native-cases.json`,
  `HtkkNativeCaseFormats.ps1` hay `probe-htkk-windows.yml`.
- `scripts/test_descriptor_native_cases.py`: test offline, kể cả kiểm kỳ vọng tính tay
  theo công thức XLS ([18]=[19]+[20], [32]=ROUND([24]·10%), [41], [27]=Σtháng·4,4tr).
- Producer phía web: `node scripts/generate-htkk-descriptor-reference.mjs --case <id> --out <dir>`
  chạy code sản phẩm đã commit, kiểm XSD, ghi `draft.json`, `web.xml` (trừ B8), `manifest.json`.

## Việc còn thiếu trước khi dispatch

1. Driver Windows `descriptor-web-import-inspect` (C# `HtkkGuiReferenceAutomation`): mở menu
   L7/B9/B8 qua cây gốc, hộp chọn kỳ (tháng/quý cho L7; năm + "Trường hợp quyết toán" cho
   B9/B8), chọn phụ lục bằng checkbox gốc, `Nhập từ XML`, đọc ô lưới, `Kết xuất`, XSD .NET.
   Với B8 cần kịch bản nhập tay bằng editor gốc (web chưa xuất XML).
2. Adapter tin cậy mới trong `htkk_native_cases.py` (`TRUSTED_ADAPTERS`, menu/xmlVersion khác
   D1), privacy validator theo `expectedLeaves`, nhánh input/output private riêng.
3. Thêm case id vào workflow `web_case_id` qua `generate-native-cases.py`, chỉ sau khi 1–2 xong.

Khi đó PM mới dispatch `probe-htkk-windows.yml` (ref `main`) với `install_and_probe=true`,
`synthetic_login=true`, `gui_automation=descriptor-web-import-inspect`,
`web_case_id=<ca>`, `web_artifact_commit=<commit artifact input>`, `web_source_sha=<commit htkk_web>`.
Hiện tại **không có workflow nào cần dispatch** cho các ca này.
