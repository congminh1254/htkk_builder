# Hai ca web→HTKK→xuất lại cho phụ lục 01-2/GTGT và probe xuất phụ lục có số phát sinh

Issue `htkk-net/htkk_web#23`. Đây là ca hồi quy cố định với dữ liệu giả lập. Chúng chưa
phải bằng chứng native cho tới khi có lần chạy Windows thành công trọn workflow. Mọi cờ
tương thích tổng thể vẫn là false.

## Hai ca mới (candidate, có status riêng)

| Ca | Producer (`--case`) | Status | Nhánh input / output private |
|---|---|---|---|
| `01GTGT-annex12-zero-two-locations-M10-2026` | `annex12-zero` | `htkk-native/annex12-zero` | `gtgt-web-reference-annex12-zero-input` / `gtgt-web-native-annex12-zero-output` |
| `01GTGT-annex12-two-plants-nonzero-M10-2026` | `annex12-two-plants` | `htkk-native/annex12-two-plants` | `gtgt-web-reference-annex12-two-plants-input` / `gtgt-web-native-annex12-two-plants-output` |

- Adapter tin cậy `01-gtgt-2.8.3-annex12`: producer là code sản phẩm thật
  `scripts/generate-htkk-web-annex12-reference.mjs`, chạy trong cùng môi trường không token
  (`produce_case_batch.ALLOWED_ENV`). Mỗi ca bị ràng buộc với hash producer của adapter mình.
- `releaseGate: false`: release vẫn sinh input, lưu nhánh private, tạo tag bất biến
  `htkk-case-input/...`, dispatch Windows bằng commit bất biến với status riêng. Cohort release
  (`native_batch.py`), Pages (`validate-pages.py`) và scoped evidence chỉ chờ 13 ca gate. Muốn
  biến một ca thành gate, đổi `releaseGate` thành `true` sau lần chạy native thành công đầu tiên
  (và cập nhật các hằng số 13 trong evidence/Pages).
- Case plan nguồn: builder chấp nhận plan chỉ có 13 ca gate (bản hiện tại trong htkk_web) hoặc
  plan đầy đủ mọi ca. Plan thiếu một phần hoặc lẫn producer bị từ chối.

## Allowlist privacy/số tiền

`htkk_annex12_web_cases.py` mô tả chính xác từng lá phụ lục: ID nhóm/dòng, STT, loại, mã/tên
địa bàn và CQT, tỷ lệ, số tiền, ct13/ct14. Ngày lập và ngày ký của input đúng `2026-10-27`.
Manifest của producer annex có tập khóa riêng; `expectedAnnexLeaves` được tính lại từ chính XML.
Sau khi kiểm chính xác cây PLuc, một bản sao trong bộ nhớ bỏ phụ lục để tái dùng allowlist tờ
khai chính (NNT giả lập, C0/M10/2026, 27 số 0). Byte gốc không bao giờ bị sửa.

## Driver Windows (`gtgt-web-import-inspect`, nhánh theo `webCaseId`)

1. Kỳ M10/2026, chọn đúng phụ lục 01-2 qua checkbox gốc; sửa ngày ký 27/10/2026 bằng editor gốc.
2. Dựng baseline bằng kịch bản đã chứng minh: F5 gốc và 14 ô nhập gốc (1 nhà máy, 2 dòng, 50/50,
   số tiền 0); kiểm 27 ô tiền tờ khai chính bằng 0; nút Kết xuất gốc; XSD .NET đã pin cho baseline.
3. Nhập XML web bằng nút gốc `Nhập từ XML`. Kiểm tờ khai chính (27 ô tiền), và trên phụ lục:
   số nhóm, TableID/STT, số dòng mỗi nhóm, tên/mã nhà máy, tiền nhà máy, tỷ lệ, mã loại/địa bàn/CQT
   ẩn, ô tên/MST con trống và bị khóa, khóa ô tỷ lệ/tiền theo nguồn.
4. Xuất lại bằng nút gốc; XSD .NET đã pin cho bản xuất lại (1 nhóm/2 dòng/112 lá hoặc 2 nhóm/5
   dòng/163 lá). So toàn bộ cây với input web: 108 hoặc 159 lá thuế. Chỉ ngày lập và 4 trường
   định danh dịch vụ theo luật native đã chứng minh.
5. `roundtripXmlExactMatched` phải true với ca zero; ca hai nhà máy có baseline là phụ lục zero nên
   được phép khác. Raw XML xuất lại được giữ nguyên byte trong nhánh output private của ca.

Không patch EXE/DLL, không gán Cell.Value, không gọi helper nghiệp vụ, không tự viết XML.

## Probe riêng `gtgt-annex12-export-nonzero`

Sau 14 ô nhập: cha 1 với 50/50 → Kết xuất gốc `01GTGT.xml`; rồi bằng editor số gốc nhập cha 7,
33,33/66,67 → Kết xuất gốc lần hai `01GTGT-p7.xml`. Cả hai đều qua XSD .NET đã pin. Sau khi
supplier dừng, `stage-htkk-annex12-nonzero-export.py` (không token) kiểm pin nguồn, hash và
allowlist: input cố định chính xác, số do HTKK tính chỉ được là số thập phân 0..tiền cha. Bước
publish riêng (chỉ khi `outcome == success`, `credentials_safe`, `supplier_stopped`) ghi
`01GTGT-annex12-p1-50.xml`, `01GTGT-annex12-p7-3333.xml`, `manifest.json` lên nhánh private mồ côi
`gtgt-annex12-nonzero-native-export`. Probe không có status và không so với engine web.

## Dispatch thủ công

```
gh workflow run probe-htkk-windows.yml --ref main \
  -f install_and_probe=true -f synthetic_login=true -f acknowledge_registration=true \
  -f runtime_host=clr2-x86-reference -f gui_automation=gtgt-annex12-export-nonzero
```

Ca web dùng `gui_automation=gtgt-web-import-inspect`, `web_case_id=<ca>`,
`web_source_sha=<commit main nguồn>`, `web_artifact_commit=<commit input bất biến>` (release tự
dispatch). Kiểm offline: `python3 -m unittest discover -s scripts -p 'test_*.py'`.

## Luật nguồn Header!B66 (run 42173347454)

Probe nonzero bị từ chối với `exportRejectedMessageId=16`. `frmWinToKhai.cmdExport_Click`
hiện 0016 khi có tab hồng. Trong `Header` của workbook đã pin, B66 là kiểm tra duy nhất phụ
thuộc tiền cha vừa nhập: `01_2!AJ7` (=T46, ct13) + tổng 01-6 không được lớn hơn `01!L59`
([40]). Vì vậy probe và ca hai nhà máy nhập trước bộ bán ra sale10 qua editor gốc (J48=1000000,
[40]=100000); ca zero giữ 27 số 0. Mặt nạ tiền chính phải là 10727808 (ct27/28/32/33/34/35/36/
40a/40). Ca zero web bị từ chối ở bước xuất lại trong run 42156474982 vẫn chưa rõ nguyên nhân;
cần `exportRejectedMessageId` và `annex12WebImportDisplayEmptyMask` của lần chạy kế tiếp.

## Nhập XML gốc để trống R (runs 42182681228 / 42182684607)

Cả hai ca đạt bước nhập và kiểm phụ lục, nhưng bản xuất lại bị 0016. Mặt nạ
`annex12WebImportDisplayEmptyMask` 264 (zero) và 8659208 (hai nhà máy) chỉ ra cột R
(`pathCucThue`, tên CQT cấp cục) của mọi dòng con trống sau khi nhập: R không phải lá XML.
Dòng 83 của sheet `Header` bắt buộc R44. Driver chọn lại đúng CQT cục giả lập qua combo gốc
(và CQT cơ sở nếu handler gốc xoá), đọc lại mã ẩn 10100/10129, rồi mới xuất lại. Giá trị XML
không đổi. Mặt nạ giữ trạng thái ngay sau nhập. Probe nonzero 42180279456 đạt; XML gốc
(cha 1 50/50: ct12 1/1, ct13/ct14 1; cha 7 33,33/66,67: ct12 2/5, ct13/ct14 7) khớp toàn bộ
131 nút với engine web.
