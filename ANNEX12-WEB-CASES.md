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

## Ca 01-10/GTGT (NQ 204/2025/QH15, oracle HTKK 5.8.2)

`01GTGT-annex10-nq204-M10-2026` (producer `annex10-nq204`, status `htkk-native/annex10-nq204@htkk582`, nhánh
`gtgt-web-reference-annex10-nq204-input` / `gtgt-web-native-annex10-nq204-output`), non-gating, `htkkVersion` 5.8.2. Driver
`gtgt-web-import-inspect`: kỳ D1 tháng 10/2026 **không** tích phụ lục; baseline = tờ khai chính số 0 xuất bằng Kết xuất gốc
(HTKK từ chối 01-10 đính kèm mà trống: Header B104/B105, 0016), không sửa ô nào; ngày ký 27/10/2026 bằng editor gốc; rồi "Nhập từ
XML" gốc của tệp web; sau nhập tờ khai chính phải có J45/J48/J50 = 129.999.950 và L45/L48/L50/L51/L57/L59 = 10.399.996; Kết xuất
lại; so cả cây với tệp web: **88 lá thuế** (chỉ ngày lập và 4 lá dịch vụ theo luật native). Re-export được khác baseline
(`roundtripXmlExactMatched` false), như ca hai nhà máy. Cờ quan sát (không chặn): `annex10ImportSheetObserved`,
`annex10ImportSheetActive`, `annex10ImportPurchaseRows`, `annex10ImportSaleRows`, `annex10NegativeDisplayMask` (bit 0 tìm thấy ô G
dòng II.2, bit 1 Value = −400002, bit 2 Value = 0 (bị chặn MinValue), bit 3 Text có dấu trừ). Chưa có bước "Chọn phụ lục"
(`frmWinSelectPhuLuc`): nếu nhập XML không tự gắn sheet 01_10, lần chạy đầu cho `annex10ImportSheetObserved` false và so cây thất bại.

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
   `ttinNhaCCapDVu` là khóa HTKK tính từ HSoKhaiThue bỏ TTinDVu (`WinDoWorkExportXML`), nên
   khóa bản xuất lại bằng khóa baseline đúng khi và chỉ khi nội dung đó bằng nhau (run
   42310299991: ca hai nhà máy có khóa khác baseline); mọi lá thuế vẫn so chính xác.

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

## Khôi phục R dừng sau thao tác combo thứ hai (runs 42206910531 / 42206915586)

Cohort phát hành (builder dd60e2c, web e02721e): cả hai ca nhập XML gốc đạt, mặt nạ nhập vẫn
264 / 8659208, nhưng `annex12WebHeadAuthorityRestored=false` với `RepairCount=2` ở cả hai ca:
driver dừng ngay sau thao tác combo gốc thứ hai (khả năng cao: dòng con đầu, chọn R, handler gốc
xoá S, chọn lại S) ở bước đọc lại R/S/AJ/AK/AH/AQ khi chưa rời ô. Run đó không cho biết điều kiện
nào sai (giả thuyết: handler gốc chỉ cập nhật mã ẩn khi rời ô, như luồng 14 thao tác vẫn làm). Vì không có bước xuất lại nên
`roundtripReexportCommandInvoked=false`, `webTaxLeafCount=0` và publish trả `FILES`; đây là hệ
quả, không phải lỗi riêng. Danh tính dịch vụ không liên quan (input web đã `webInputVerified`).

Driver nay rời ô như người dùng: sang S trước khi đọc S, sang ô tỷ lệ của dòng con (trường kế
tiếp trong thứ tự 14 thao tác đã chứng minh) rồi chờ có giới hạn cho handler gốc; chỉ khi handler
chưa chạy mới mở/đóng editor tỷ lệ gốc không gõ phím, giá trị phải giữ nguyên. Không ghi ô/mã;
so sánh toàn cây XML không đổi. Trường mới `annex12WebHeadAuthorityFailureMask` (0..4095): bit 0-5
là kiểm R/S/AJ/AK/AH/AQ chưa đạt, bit 6-8 là thứ tự dòng con + 1, bit 9/10 combo R/S lỗi, bit 11 đã
cần mở editor tỷ lệ. Thành công yêu cầu `(mask & 2047) == 0`.

## Mã ẩn AJ vẫn trống ở dòng con đầu (release 213, mask 2116 cả hai ca)

IL `frmWinToKhai.cellChange` (gọi từ `ComboCloseUp`/`EditChange`) ghi mã CQT cục vào cột `SelectedValue`
(AJ) của dòng bảng **theo `ActiveCell.Row`** và chỉ khi ô R đã có chữ lúc danh sách đóng
(`winFpSpread_ComboCloseUp` bỏ qua `cellChange` khi ô còn trống — đúng trạng thái R sau nhập XML). Khi AJ
chưa đạt sau lượt đầu, driver mở lại đúng danh sách R gốc và xác nhận lại cùng mục (thao tác người dùng,
không ghi ô), rồi S như trước. Trường mới `annex12WebHeadAuthorityComboMask` (0..255): bit 0 kiểu combo,
1 có mục, 2 ItemData khớp số mục, 3 chữ R là một mục, 4 ItemData của mục là 10100, 5 ô hiện hành đúng
dòng, 6 đã xác nhận lại, 7 AJ đạt sau khi xác nhận lại. Chưa chạy Windows: hiệu quả chưa được chứng minh.
