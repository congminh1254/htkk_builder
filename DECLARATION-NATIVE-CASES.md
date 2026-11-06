# Ca native web→HTKK cho 03/TNDN, BCTC, TNCN, 01/CNKD (`declaration-web-import-inspect`)

Một mode chung cho mọi họ tờ khai sau `DeclarationEngine` của htkk_web. Đây là ca hồi quy
giả lập; **chưa là bằng chứng native** cho tới khi có lần chạy Windows thành công trọn
workflow. Mọi ca `releaseGate: false` (bị khóa bằng kiểm tra trong `htkk_native_cases.py`),
release/Pages/cohort/scoped evidence vẫn chỉ chờ 13 ca gate D1.

## Ca (một ca mỗi mẫu)

| caseId | Menu (chuỗi Menu.xml) | KieuKy | Kỳ | Phụ lục | Lá so sánh |
|---|---|---|---|---|---|
| `03TNDN-profit20-Y2025` | `101 → 101_2 → N8` (03/TNDN 2.9.4) | 11 | năm 2025, 01/01–31/12 | 03-1A | 143 |
| `BCTC133-B01a-basic-Y2025` | `101 → 101_6 → A2` (B01a-DNN 2.3.2) | 26 | năm 2025 | 01-1 (BCKQHĐKD) | 227 |
| `BCTC200-LT-basic-Y2025` | `101 → 101_6 → 78` (TT200 2.2.6) | 26 | năm 2025, hoạt động liên tục | 01-1 (KQHĐSXKD), 01-3 (LCTTGT; HTKK 0478 cần đúng một LCTT) | 566 |
| `05KK-withheld-Q3-2026` | `101 → 101_11 → L7` (05/KK 2.9.3) | 19 | quý 3/2026 (tháng bị HTKK từ chối từ 4/2026, 0682) | — | 53 |
| `05QTT-two-employees-Y2025` | `101 → 101_11 → B9` (05/QTT 2.9.3) | 12 | năm 2025 | 05-1, 05-3 | 145 |
| `01CNKD-TT50-revenue-two-groups-Q3-2026` | `101 → 101_37 → U5` (01/CNKD 2.9.8) | 21 | quý 3/2026 | — | 257 |

B8 (02/QTT) chưa có ca: web chưa kết xuất XML được (`exportBlockers`), cần kịch bản nhập tay riêng.

- Producer: `htkk_web/scripts/generate-htkk-declaration-reference.mjs --case <producerCase> <thư mục>`
  chạy code sản phẩm qua `declarationEngineFor(menuId)` (calculate → exportXml → XSD → importXml →
  kết xuất lại trùng byte), ghi `declaration-web.xml` + `manifest.json`. Định danh là hồ sơ NNT giả lập
  mà harness ghi (`9999999997`, `NNT KIEM THU GIA LAP - KHONG NOP`, `NGUOI KY GIA LAP`).
- `htkk_declaration_web_cases.py`: allowlist privacy (định danh, kỳ, dịch vụ, ngày, phụ lục, số lá, chỉ số
  /ngày/bool hoặc văn bản giả lập/mẫu đã duyệt) và oracle **độc lập** (workbook plan, descriptor design,
  phép tính Decimal của `htkk_hkd_web_cases.py`). Dùng cho input, cho bản xuất native và so toàn cây.
- `HtkkDeclarationCasePlans.cs`: kế hoạch biên dịch cố định (chuỗi menu, KieuKy, kỳ, nhãn phụ lục, pin
  SHA-256 xls/xml/xsd, ô kiểm, lá XML kiểm). Input private chỉ **chọn** một caseId, không cung cấp gì khác.

## Mode / adapter

`HtkkDeclarationAdapter` (adapter `declaration-web`) được `Start()` chọn cho mode này; D1 giữ
`HtkkGtgtAdapter`. Dùng chung với D1: lưu hồ sơ gốc, đóng hồ sơ, `RaiseOriginalMenuClick`, hộp thoại file
gốc (`TrySubmitOriginalFileDialog`), đọc thông báo từ chối bằng ID Message.xml đã pin.

1. Đóng hồ sơ NNT như D1; đi chuỗi menu từ plan (Menu.xml đã pin, `data/htkk-active-menu.json`).
2. `frmHTKKPeriod` theo KieuKy: 19 → `chkTkhaiThang` + `mskMonth`; 21 → `chkTKQuy` + `cbbQuy`; 11/26 →
   `mskYear` + `mskTuNgay/mskDenNgay`; 12 → `mskYear` (+ `mskTuThang/mskDenThang` nếu sửa được); 78 →
   `chkQTTungNam_HoatDongLienTuc`. `OptChinhthuc`, combo địa bàn/CQT chỉ khi layout gốc hiện. Phụ lục bằng
   checkbox gốc của `axfpsPhuLuc` (khớp `TextTrue` với SheetName/Caption Menu.xml); ô mặc định bị khóa mà
   khác ca thì **không** ép, ca thất bại `declaration-period-inputs-not-matched`.
3. Tờ khai mở: `MenuID`, `VersionXML`, `InstanceClass` (`TAX.HTKK.Business.<Class>Nckt<ver>`),
   `TTPeriodInfo`, pin nguồn. Rồi nút gốc `Nhập từ XML` với web XML đã staging.
4. Sau thông báo `Nhập dữ liệu từ XML thành công.`: kiểm ô tiền theo plan (giá trị; trạng thái khóa chỉ
   ghi mask chẩn đoán).
5. Nút gốc `Kết xuất` → `frmWinSelectExport` (XML) → hộp thoại lưu gốc → `reference-declaration-output/declaration.xml`.
   XSD .NET qua resolver chỉ cho 3 tệp đã pin (xsd mẫu, `TKhaiThue*.xsd`, xmldsig). Kiểm lá XML theo plan.
6. `HtkkDeclarationTreeComparison`: so toàn cây với web XML; chuẩn hóa trong bộ nhớ **chỉ** `ngayLapTKhai`
   và 4 trường `TTinDVu` (định danh native bắt buộc `HTKK`/`HỖ TRỢ KÊ KHAI THUẾ`/`5.8.1`/hex32). Kết quả là
   cờ + số lá + mask vùng (1 TTinDVu, 2 TKhaiThue, 4 NNT, 8 CTieuTKhaiChinh, 16 PLuc, 32 cấu trúc), không giá trị.
7. Mã lỗi giới hạn: stage terminal `declaration-*-not-matched`, `declaration-import/export-original-message-rejected`
   kèm `importRejectedMessageId`/`exportRejectedMessageId` (ID 4 chữ số trong Message.xml đã pin, 9999 = không có).

Raw: probe staging `htkk-declaration-native-output/` (bản xuất gốc nguyên byte + provenance) khi bản xuất đã được
HTKK xác nhận, **kể cả khi so cây lệch** (status vẫn failure). `publish-htkk-declaration-native-output.py` (sau cổng
credential) kiểm lại privacy, tải input bất biến, so cây độc lập, ghi nhánh private `declaration-web-native-*-output`
và tag `htkk-case-output/...`. Không public log XML/đường dẫn/tiêu đề cửa sổ.

## Dispatch (chỉ sau khi merge main, theo thứ tự trong báo cáo)

Release htkk_web tự sinh input, lưu nhánh `declaration-web-reference-*-input`, dispatch từng ca với status
`htkk-native/<producerCase>`. Thủ công:

```
gh workflow run probe-htkk-windows.yml --ref main \
  -f install_and_probe=true -f synthetic_login=true -f acknowledge_registration=true \
  -f runtime_host=clr2-x86-reference -f gui_automation=declaration-web-import-inspect \
  -f web_case_id=<caseId> -f web_source_sha=<commit htkk_web main> -f web_artifact_commit=<commit input bất biến>
```

## Chưa chắc chắn (chưa chạy Windows)

`TTPeriodInfo.KieuKy` của kỳ năm (giả định `Y`); định dạng text `mskTuNgay`/`mskTuThang`; nhãn `TextTrue` của
phụ lục (SheetName hay Caption); phụ lục BCTC mặc định/khóa; `cboNganhKD` (N8) và `cboTruongHopQT` (N8/B9) để mặc
định nên `ct04_*`/`ma_THQuyetToan` có thể lệch; HTKK có thể điền NNT (địa chỉ, tỉnh, CQT) từ hồ sơ trong khi web để
trống (mask 4); `xsi:nil` của web (U5, B9) so với cách HTKK ghi ô rỗng (mask 32); hộp thoại phụ khi nhập XML;
`InstanceClass` của 78 (`BctcTt200Nckt226` hay biến thể `Hn`).

Kiểm offline: `python3 -m unittest discover -s scripts -p 'test_*.py'`,
`python3 scripts/generate-native-automation-registry.py --check`, `python3 scripts/generate-native-cases.py --check`.
