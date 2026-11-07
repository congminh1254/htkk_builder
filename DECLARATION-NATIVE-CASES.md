# Ca native web→HTKK cho 03/TNDN, BCTC, TNCN, 01/CNKD (`declaration-web-import-inspect`)

Một mode chung cho mọi họ tờ khai sau `DeclarationEngine` của htkk_web. Đây là ca hồi quy
giả lập; **chưa là bằng chứng native** cho tới khi có lần chạy Windows thành công trọn
workflow. Mọi ca `releaseGate: false` (bị khóa bằng kiểm tra trong `htkk_native_cases.py`),
release/Pages/cohort/scoped evidence vẫn chỉ chờ 13 ca gate D1.

## Ca (một ca mỗi mẫu)

| caseId | Menu (chuỗi Menu.xml) | KieuKy | Kỳ | Phụ lục | Lá so sánh |
|---|---|---|---|---|---|
| `03TNDN-profit20-Y2025` | `101 → 101_2 → N8` (03/TNDN 2.9.4) | 11 | năm 2025, 01/01–31/12 | 03-1A | 143 |
| `BCTC133-B01a-basic-Y2025` | `101 → 101_6 → A2` (B01a-DNN 2.3.2) | 26 | năm 2025 | 01-1 (BCKQHĐKD), 01-4 (BCĐTK, `PL_CDTK`; HTKK 0485 cần cả hai) | 971 |
| `BCTC200-LT-basic-Y2025` | `101 → 101_6 → 78` (TT200 2.2.6) | 26 | năm 2025, hoạt động liên tục | 01-1 (KQHĐSXKD), 01-3 (LCTTGT; HTKK 0478 cần đúng một LCTT) | 566 |
| `05KK-withheld-Q3-2026` | `101 → 101_11 → L7` (05/KK 2.9.3) | 19 | quý 3/2026 (tháng bị HTKK từ chối từ 4/2026, 0682) | — | 52 |
| `05QTT-two-employees-Y2025` | `101 → 101_11 → B9` (05/QTT 2.9.3) | 12 | năm 2025 | 05-1, 05-3 | 145 |
| `01CNKD-TT50-revenue-two-groups-Q3-2026` | `101 → 101_37 → U5` (01/CNKD 2.9.8) | 21 | quý 3/2026 | — | 257 |
| `02QTT-dependants-Y2025` | `101 → 101_11 → B8` (02/QTT 2.7.3) | 12 | năm 2025 (NopTheoTinhCQT 3) | 02-1 (danh sách ẩn; nhập XML thêm mọi phụ lục) | 126 |
| `01NTNN-two-contractors-M10-2026` | `101 → 101_8 → I9` (01/NTNN TT80 2.5.1) | 18 | tháng 10/2026 | — (bảng nhà thầu `BKThueNTNN/ThueNTNN`, 2 dòng) | 70 |
| `03NTNN-no-rate-M10-2026` | `101 → 101_8 → J1` (03/NTNN 3.0.8) | 18 | tháng 10/2026 | — (bảng `BKThueNTNN/ThueNTNN`, 2 dòng, tỷ lệ [9] = 0) | 65 |
| `01NTNN-NCCNN-entry-M10-2026` | `101 → 101_8 → Y8` (01/NTNN, NCCNN TT89 3.0.9), **nhập tay** | 18 | tháng 10/2026 | — (ba bảng; phần II: `ThueNCCNN` 1 dòng, `ThueCNKCT` 1 dòng, `ThueNTNN` khóa; gõ vào lưới gốc) | 103 |
| `04NTNN-TT80-one-subcontractor-2026` | `101 → 101_8 → D6` (04/NTNN TT80 3.0.8) | 22 | từ 01/01/2026 đến 30/09/2026 (`D_D`) | 02-2/NTNN (sheet Menu `01-1` = sheet XLS `01-2`, 1 nhà thầu phụ) | 75 |
| `04NTNN-TT89-one-subcontractor-2026` | `101 → 101_8 → Y1` (04/NTNN TT89 3.0.9) | 22 | từ 01/07/2026 đến 30/09/2026 (`D_D`) | 02-2/NTNN (1 nhà thầu phụ) | 75 |

B8 (02/QTT) dùng ca thiết kế `02QTT-dependants-Y2025` (hai người phụ thuộc, 6 và 12 tháng); web kết xuất XML qua descriptor engine.

I9 (01/NTNN TT80, non-gating) dùng ca thiết kế `01NTNN-two-contractors-M10-2026`: hai nhà thầu "GIẢ LẬP" không MST, ngành
01/02 của `DM_NNKD_NTNN.xml`, ngày thanh toán trong tháng 10/2026 (checkTKChinh E_27), ngày hợp đồng trước ngày chạy (E_36).
KieuKy 18 = `SetLayoutToKhaiThangLanPhatSinh` (tích sẵn `chkTkhaiThang`), driver đi nhánh tháng chung (`mskMonth` "10").
Oracle độc lập `NTNN_ROWS`/`ntnn_expected` trong `htkk_declaration_web_cases.py` tính lại bằng Decimal từng dòng theo công thức XLS
dòng 55 (ct9 = ROUND(ct7·ct8/100), ct13 = MAX(0, ROUND(ct10·ct11/100) − ct12), ct14 = ct9 + ct13; làm tròn nửa xa 0) và các
tổng `tong_ct5…ct14`: A 50tr/50tr/100tr, B 15tr/8tr/23tr, tổng [14] 123.000.000. Dòng `ThueNTNN` mang thuộc tính `ID` (chữ hoa,
theo `01_NTNN_TT80_xml_251.xml`/XSD), nên `leaves()` nhận cả `id` và `ID` với giá trị `ID_n`; so cây vẫn so thuộc tính chính xác.
Câu hỏi mở: tỷ lệ ct8/ct11 (control 16, DefaultValue `0,00`) web ghi `5.00` như 03/TNDN `ct05` của release 214.

Y8 (01/NTNN, NCCNN TT89, non-gating) dùng ca thiết kế `01NTNN-NCCNN-two-parts-M10-2026` (ca native import cùng tên đã bỏ sau release 242, xem dưới): tích M8 `nopThayNCCNN`
(`Ntnn01TT89Nckt309.ButtonClick_0` giữ M6 = false), bảng `ThueNTNN` khóa (`LockUnlock`) và chỉ có dòng mẫu mặc định;
một nhà cung cấp nước ngoài (200tr: GTGT 10tr, TNDN 10tr, [14] 20tr) và một cá nhân không cư trú (100tr: GTGT 5tr,
TNCN 2tr, [14] 7tr). Oracle `NTNN_ROWS` theo từng bảng (đường dẫn dòng, cha của dòng tổng, tiền tố `tong_`/`mucI_tong_`/
`mucII_tong_`). Mẫu `_xml_` của Y8 có `HSoKhaiThue id="ID1"` (không gạch dưới) nên `leaves()` nhận `ID_?n`.
Câu hỏi mở: HTKK kết xuất lại dòng mẫu của bảng bị khóa thế nào (web giữ một dòng mặc định).

Release 238 (web cdf10bbb, builder 66e98b8): I9 `01NTNN-two-contractors-M10-2026` **khớp toàn bộ** (run 42348087003,
70 lá). Y8 `01NTNN-NCCNN-two-parts-M10-2026` thất bại (run 42348089716): nhập XML thành công, `declarationCellMismatchMask`
255 (8/9 ô kiểm bằng 0, chỉ BR62 = 0 khớp), không kết xuất lại. Nguyên nhân trong nguồn HTKK 5.8.1: `cmdImportXML_Click`
(0x60003a9) → `frmToKhai_ReLoad` → `LoadToKhai` → `fpSpDisplayTemplate` → `ProcessSheet` (0x60001a2) nạp dữ liệu rồi gọi
`AutoBindData` → `Ntnn01TT89Nckt309.AutoBindData_0` → `LockUnlock`, và `LockUnlock` truyền `deleteData = true` cho
`GeneralFunctions.LockUnLockColsInTable` (0x6002676) ở cả ba bảng: mọi dòng, cột C…BH, bị đặt lại `DefaultValue`, bảng khóa
hay mở. Đường nhập XML vì vậy không giữ được bảng kê Y8; ô kiểm và so cây giữ nguyên (không nới). Muốn có bằng chứng
native cho Y8 cần chế độ nhập tay trên lưới gốc sau khi tích M6/M8 (`original-entry-export`): xem mục dưới.

### Chế độ ca native `original-entry-export` (Y8, `01NTNN-NCCNN-entry-M10-2026`, non-gating)

Cùng driver/GUI mode `declaration-web-import-inspect`, cùng menu/kỳ/pin/kiểm XML/so cây, cùng input web (dữ liệu của ca thiết kế
`01NTNN-NCCNN-two-parts-M10-2026`; trước release 242 trùng byte với ca import cùng tên, `SAME_INPUT`, nay đã bỏ) nhưng **không** bấm "Nhập từ XML":
adapter `01-ntnn-nccnn-tt89-3.0.9-entry` (mode `original-entry-export` trong `TRUSTED_ADAPTERS` và
`htkk-descriptor-native-cases.json`) làm `HtkkDeclarationCasePlans.Entry(caseId)` khác null, và
`HtkkDeclarationOriginalEntry.cs` gõ kế hoạch cố định vào lưới gốc. Web XML vẫn là bản tham chiếu của so toàn cây.

1. `entry-ready`: pin 14 thân phương thức HTKK đã nạp (token metadata qua `Module.ResolveMethod`, số byte và SHA-256 của
   `GetILAsByteArray()`; hash raw-body tương ứng ghi trong comment để đối chiếu `htkk_web/data/htkk-descriptor-declarations.json`)
   và `InterfaceIni/DM_NNKD_NTNN.xml` (SHA-256). Lệch → `declaration-entry-not-matched`, mã 1/2, `declarationEntryMethodPinMask`.
2. `entry-choice`, **trước mọi giá trị**: ô M8 phải là `CheckBoxCellType` mở, chưa tích; `SetActiveCell(7,12)` + phím SPACE →
   `FpSpread.ButtonClicked` → `frmWinToKhai.winFpSpread_ButtonClicked` → `WinDoWorkEvent.ButtonClick` → `ButtonClick_0` (M6 := !M8,
   `LockUnlock`). Kiểm M8 = true, M6 = false và mask khóa theo bảng (bit t = mọi ô `getCols` của bảng t khóa, bit 4+t = lẫn):
   kỳ vọng 1 (chỉ `ThueNTNN` khóa). Ô (9,2) mở `Bang_Ke_01NTNN_TT89.xls` không bao giờ được chạm.
3. `entry-rows`: mỗi bảng đã có sẵn một dòng (`RowsValues`), kế hoạch cần đúng một dòng/bảng nên **không cần F5**; đường F5
   thật (`ProcessCmdKey`, `pnF5` hiện, tối đa 4 lần, mỗi lượt UI một lần) vẫn có cho kế hoạch cần thêm dòng. Kiểm dòng đầu
   60/78/86 sau bước này.
4. `entry-values`: 21 giá trị, mỗi lượt timer một giá trị, theo thứ tự kế hoạch (C, L, S, W, Y, AE, AJ, AN, AZ, BD của dòng 78
   rồi 86, rồi ngày ký AY98 nếu ô mở): `BeginCellEdit(..., showActiveCell)` → `^a` → giá trị → `{TAB}` qua `SendKeys` như
   `01GTGT-sale10-manual`; số và ngày (mask `00/00/0000`, gõ `ddMMyyyy`) như D1; văn bản ASCII qua `SendKeys`, văn bản có dấu
   ("GIẢ LẬP") qua `SendInput` `KEYEVENTF_UNICODE` (bàn phím thật tới editor đang focus, không `WM_SETTEXT`). Mỗi bước kiểm
   foreground/focus/ô active/không có `frmMessage`, đọc lại ô (văn bản, Decimal, ngày). Không bao giờ gán `Value`/`Text`.
5. Ngành nghề (control 87, `WinInsertCombox` từ `DMNnkdNtnn`, Items theo thứ tự tệp): đọc (chỉ đọc) danh sách của `FpCombo`,
   yêu cầu mục ở chỉ số kế hoạch (01 → 0, 05 → 4) đúng tên và không mục nào trước đó cùng chữ đầu; gõ chữ đầu ("D"/"H") để
   AutoSearch gốc chọn; nếu chọn không đổi thì dự phòng bàn phím ENTER (FpCombo.OnKeyDown mở danh sách) + DOWN từng mục,
   dừng ngay khi một phím không tiến/rời ô; `{TAB}` xác nhận; rồi đọc tên L và mã BX (do `winFpSpread_CellChange` ghi).
   Không gán `SelectedIndex`. Nếu cả hai đường bàn phím không chọn được, ca thất bại (mã 15, mask combo), không giả lập.
6. `entry-inspect`: đọc ô HTKK tính (AV/BN/BR 78 và 86, Y/AV/BN/BR 80 và 88, BR62 = 0) so oracle Decimal `NTNN_ROWS`,
   mask khóa cuối = 1, người ký AY96 = hồ sơ; rồi `Kết xuất` gốc chung → XSD pin → so cây → stage thành công
   `declaration-original-entry-exported` (ca import giữ `declaration-web-import-inspected`). Bản xuất gốc được lưu private như
   các ca khác (`inputMode` = `original-entry-export`, `originalImportSucceeded` = false trong provenance) để thành fixture.

Trường chẩn đoán (không giá trị ô): cờ `declarationEntryMethodPinsMatched`, `…CatalogueMatched`, `…ChoiceMatched`,
`…LocksMatched`, `…RowsMatched`, `…ValuesMatched`, `…SignerMatched`, `…SigningDateLocked`, `…SheetMatched`; số
`declarationEntryPlannedCount`/`ActionCount` (bước hỏng = ActionCount), `FailureCode` (1 pin phương thức, 2 pin danh mục, 3 ô
chọn, 4 chọn không ăn, 5 mẫu khóa, 6 metadata bảng, 7 dòng/F5, 8 ô khóa, 9 kiểu ô, 10 foreground/focus, 11 editor, 12 chữ
không tới editor, 13 đọc lại, 14 danh sách combo, 15 chọn combo, 16 mã combo, 17 thông báo gốc, 18 mất ô/editor khi chọn combo,
20 ô tính/khóa cuối), `MethodPinMask`, `LockBefore/After/FinalMask`, `RowsBefore/After` (4 bit/bảng), `RowInsertCount`,
`MismatchMask`/`LockedMask`/`CellTypeMismatchMask`/`DateTextMask` (bit = chỉ số bước), `Combo1Mask`/`Combo2Mask` (1 FpCombo, 2
tên ở chỉ số, 4 chữ đầu duy nhất, 8 rỗng ban đầu, 16 AutoSearch đổi, 32 đúng sau AutoSearch, 64 dùng ENTER, 128 danh sách mở,
256 đúng sau DOWN, 512 tên đã ghi, 1024 mã CellChange). Cùng `declarationCellMismatchMask`, mask cây và chẩn đoán 0016 sẵn có.

Câu hỏi lần chạy Windows đầu sẽ trả lời: ButtonClicked đọc M8 sau khi đổi (mask khóa sau); AutoSearch mặc định của
`ComboBoxCellType` (bit 16/32) hay phải dùng ENTER/DOWN; `SendInput` Unicode vào editor chung của FarPoint (mã 12); ô ngày của
dòng bảng là mask (`DateTextMask`); AY98 (công thức `TRIM(Header!V42)`) mở cho gõ hay khóa (`SigningDateLocked`, khi đó ngày ký
xuất ra có thể lệch → mask cây 2); HTKK kết xuất dòng mẫu của bảng khóa và `ct2` rỗng thế nào (mask cây 8). Ca import
`01NTNN-NCCNN-two-parts-M10-2026` ban đầu được giữ, non-gating.

**Release 242** (web 192d4c03, builder d1d87637, run 42359742133): `01NTNN-NCCNN-entry-M10-2026` **khớp toàn bộ** ngay lần
chạy đầu: 103 lá, mask cây 0, 15/15 ô kiểm và 9/9 lá XML khớp; pin phương thức/danh mục khớp; khóa trước/sau/cuối 7/1/1;
`RowsBefore/After` 273 (một dòng/bảng, không F5); 21/21 giá trị; `Combo1Mask` = `Combo2Mask` = 1599 (AutoSearch bằng chữ đầu
chọn đúng ngay, không dùng ENTER/DOWN; mã BX do CellChange ghi); `SigningDateLocked` false (AY98 gõ được); `DateTextMask` 0.
Bản xuất gốc: nhánh `declaration-web-native-ntnn01-nccnn-entry-m10-2026-output` 7a01607c (htkk_web ghim làm fixture
`ntnn01-nccnn-entry-m10-2026-release242`; Y8 được bật). Ca import `01NTNN-NCCNN-two-parts-M10-2026` (thất bại như dự kiến ở
release 242) **bị bỏ** khỏi registry, kế hoạch biên dịch, allowlist privacy và producer web: HTKK 5.8.1 đặt lại bảng kê Y8
khi nhập XML nên ca đó không thể khớp, ca nhập tay thay thế. Ca thiết kế cùng tên vẫn là nguồn dữ liệu (design-only).

J1 (03/NTNN 3.0.8, non-gating) dùng `03NTNN-no-rate-M10-2026`: `Ntnn03TT80Nckt308.FinishImportXML` (0x6001937) ghi
`BU := GeneralFunctions.getThuSuatByMa(CR, "DC_97")` cho mọi dòng nhập; cột ẩn CR (`pathTLTNDN`) không có trong mẫu
`_xml_`/XSD và không có lệnh ghi (htkk_web quét IL `ntnn03-cr-no-writer`), nên tỷ lệ [9] luôn bị xóa khi nhập XML. Ca
dùng tỷ lệ 0 và miễn giảm 0 ở cả hai dòng để phép ghi lại là no-op: oracle Decimal `NTNN_ROWS` (công thức `03`: ct11 =
IF(ct8·ct9/100 − ct10 < 0, 0, ROUND(ct8·ct9/100 − ct10))) cho ct11 = 0, `tongct6`/`tongct8` = 1.100.000.000, `tongct10`/
`tongct11` = 0. Ngày thanh toán (7) để trống (IL đưa nguyên văn ô BE cho `ValidateFullDate(…, "ddMMyyyy")`).
Release 240 (web fbd22dad, builder 9d14366d, run 42353849411): nhập XML, 6 ô kiểm và 4 lá XML khớp; so cây khác đúng 2 lá
(thứ tự 46, 59): `ct9` HTKK ghi `0`, web khi đó ghi `0.00`. Nguồn: `GeneralFunctions.GetValueExportXML` (0x6002617) thay mọi
giá trị Controltype 16 có `Convert.ToDouble` = 0 bằng `"0"` trước khi định dạng (áp dụng cho cả số 0 nhập tay). Web
`work/j1-fix` ghi `0`; oracle (`_EMPTY_ROW` của Y8 và dòng J1) theo đó. Cần chạy lại ca ở release sau.
Release 241 (web 349cd65b, builder 8a1b4820, run 42356589757): **khớp toàn bộ** (61 lá, mismatch mask 0; bản
native trùng byte với release 240, chỉ input web đổi `ct9` thành `0`). htkk_web bật J1 (fixture `ntnn03-no-rate-m10-2026-release241`).

D6/Y1 (04/NTNN quyết toán, non-gating, nhập XML) dùng `04NTNN-TT80-one-subcontractor-2026` / `04NTNN-TT89-one-subcontractor-2026`.
Kỳ **KieuKy 22**: `frmHTKKPeriod.SetLayoutToKhaiTuNgayDenNgay` (0x60004ae) chỉ hiện `mskTuNgay`/`mskDenNgay` (không ô năm,
không ô tích tháng/quý) và danh sách phụ lục. Plan `periodKind` = `range`: driver gõ hai ngày qua `SetDeclarationText`
(Leave gốc chuẩn hóa), **không** đụng `mskYear` (ẩn), kiểm hai ô đang hiện bằng đúng ngày của plan, rồi tích "02-2/NTNN"
(menu không thuộc `AddFullPLImportXML`). Định danh sau Đồng ý: `GetPeriodInfo` (0x60004e2, nhánh 80/82/C9/D6/X9/Y1) cho
`KieuKy` `D_D`, `Nam` = năm của đến ngày, `TuNgay`/`DenNgay` = nguyên văn hai ô — `DeclarationIdentity` kiểm cả bốn.
`xmlExportTTinChung` (0x6000049) ghi `kieuKy` `Y`, `kyKKhai` 2026 và hai ngày (manifest kỳ `('Y', '2026', từ, đến)`).
Hai class không có `FinishImportXML`; `AutoBindData_0` chỉ ghi trường hợp quyết toán 07; `Refresh_1` đặt AB32/AB33 =
BD32/BD33 (tổng phụ lục, bằng giá trị web). Oracle Decimal độc lập `NTNN04`/`ntnn04_expected` (`htkk_declaration_web_cases.py`)
tính lại từ đầu vào (kê khai [3] dòng 1/2/3/5, quyết toán [4] dòng 3/5/6, dòng phụ lục ct9/ct10) theo công thức XLS sheet 01
dòng 32–39: [4] dòng 1/2 = tổng phụ lục, dòng 4 = IF(dòng 2 − dòng 3 > 0, …, 0), [5] = [4] − [3] (có thể âm), dòng 7 =
IF(r5 − r6 < 0, 0, r5 − r6), dòng 8 = IF(r6 − r5 > 0, r6 − r5, 0); kiểm mọi lá `Nhóm/lá` dưới `CTieuTKhaiChinh`, dòng phụ lục
và `tong_ct9`/`tong_ct10`.

| Ca | [1] GT HĐ QT | [2] DT QT | [3] DT NTP | [4] DT tính thuế QT / chênh lệch | [5] chênh lệch thuế | [7] còn phải nộp |
|---|---|---|---|---|---|---|
| D6 | 2.500.000.000 | 2.400.000.000 | 400.000.000 | 2.000.000.000 / −400.000.000 | 4.000.000 | 4.000.000 |
| Y1 | 2.000.000.000 | 1.800.000.000 | 300.000.000 | 1.500.000.000 / −300.000.000 | 3.000.000 | 3.000.000 |

Kiểm sheet sau nhập: AB32/AB33/AJ32/T35/AB35/AJ35/AJ36/AB38/AB39 và tổng phụ lục (một dòng, không chèn: D6 `01-2!BD26/BS26`,
Y1 `01-2!BI51/BX51`). Y1 không có ca 0: Header B42 (`IF(01!AJ36=0,0,1)`, cờ Y) chặn kết xuất khi [5] = 0
(`NO_ZERO_CASE`). Câu hỏi mở cho lần chạy Windows đầu: (1) nhập XML có nhận `kieuKy` `Y` + hai ngày cho kỳ `D_D` (0437)?
(2) sheet phụ lục trong lưới gốc tên `01-2` hay "02-2/NTNN" (driver nhận cả hai)? (3) D6 `checkPL4_1` từ chối gì khi kết xuất
(ngày trước hôm nay, mã tỉnh 101)? (4) Y1: mã CR của 02-2 có là SelectedValue của AG khi nhập XML (CR49 trong XLS là công
thức khóa trùng)?

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
   Khi bản xuất bị `0016`, driver chỉ đọc màu nền ô (HTKKFile.SetNodeBackGroundPink tô `Color.Pink`): mask sheet
   `declarationInvalidSheetMask`, số ô `declarationInvalidCellCount` và tối đa 4 ô `declarationInvalidCell1..4`
   mã hóa `(sheet+1)*1000000+(dòng+1)*1000+(cột+1)` (0-based); không đọc giá trị, chữ hay ghi chú.

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

## Release 213 (web edcfea5, builder 4fc497d) → thay đổi

- 03/TNDN (run 42231670259) và TT200 (run 42231681905): bản xuất lại bị `0016` (tab hồng do các dòng
  bắt buộc của sheet `Header`). 03: `B25` (ngành nghề `ct04`, control 91 danh mục
  `DM_NganhCoDoanhThuCao`) và `B26` (`ct05` ≠ 0 khi mã ≠ 000) → ca chọn `C10`, `ct05` 100. TT200: `B46`
  (tổng nguồn vốn [440] ≠ 0, nhánh LT) và `B27/B28` (cân đối) → ca nhập tiền 500.000.000 / vốn góp
  500.000.000. Web kiểm cùng các dòng trước khi xuất. 03 còn ghi `ma/ten_THQuyetToan` mặc định của hộp kỳ
  (`01`/`QT định kỳ`, AutoBindData_0).
- 05/KK (run 42231687321): toàn cây khác (mask 32) vì web thiếu `HSoKhaiThue id="ID_1"` của mẫu, thiếu các
  lá hồ sơ (`maCQTNoiNop/tenCQTNoiNop`, `maTinhNNT/tenTinhNNT`, `maXaNNT/tenXaNNT`) và còn `PLuc` rỗng. Web
  đã sửa; so cây offline với bản xuất gốc private: khớp 52 lá. Mọi ca web nay mang lá hồ sơ giả lập
  (`PROFILE_TEXTS` được nhận trong input).
- 05/QTT (run 42231692177): `declaration-period-inputs-not-matched` vì danh sách phụ lục ẩn (KieuKy 12).
  `cmdImportXML_Click` gọi `AddFullPLImportXML` cho `~B8~37~33~B9~N7~W1`: chính lệnh nhập gốc thêm mọi
  sheet, nên driver chỉ quan sát và kiểm sheet sau khi nhập.
- BCTC133 (run 42231675585): 0485 như dự kiến → thêm 01-4. HTKK ghi phần tử `PL_CDTK` của mẫu `_xml_`; tên
  XSD `"PL_CDTK "` là `xs:NCName` được .NET XmlSchema thu gọn khoảng trắng.
- Root thoát khi nhập (run 42218283778): `referenceHostExit` = mã thoát Win32 (hex) + nhóm cố định
  (`clr-unhandled-exception`, `stack-overflow`, `access-violation`, `fail-fast`, `zero`, `reference-host-code`,
  `other`), không đọc thông điệp/đường dẫn.

## Chưa chắc chắn (chưa chạy Windows)

`TTPeriodInfo.KieuKy` của kỳ năm (giả định `Y`); định dạng text `mskTuNgay`/`mskTuThang`; nhãn `TextTrue` của
phụ lục (SheetName hay Caption); phụ lục BCTC mặc định/khóa; `cboNganhKD` (N8) và `cboTruongHopQT` (N8/B9) để mặc
định nên `ct04_*`/`ma_THQuyetToan` có thể lệch; HTKK có thể điền NNT (địa chỉ, tỉnh, CQT) từ hồ sơ trong khi web để
trống (mask 4); `xsi:nil` của web (U5, B9) so với cách HTKK ghi ô rỗng (mask 32); hộp thoại phụ khi nhập XML;
`InstanceClass` của 78 (`BctcTt200Nckt226` hay biến thể `Hn`).

Kiểm offline: `python3 -m unittest discover -s scripts -p 'test_*.py'`,
`python3 scripts/generate-native-automation-registry.py --check`, `python3 scripts/generate-native-cases.py --check`.
