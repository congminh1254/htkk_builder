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
| `01NTNN-two-contractors-M09-2026` | `101 → 101_8 → I9` (01/NTNN TT80 2.5.1) | 18 | tháng 09/2026 | — (bảng nhà thầu `BKThueNTNN/ThueNTNN`, 2 dòng) | 70 |
| `03NTNN-no-rate-M10-2026` | `101 → 101_8 → J1` (03/NTNN 3.0.8) | 18 | tháng 10/2026 | — (bảng `BKThueNTNN/ThueNTNN`, 2 dòng, tỷ lệ [9] = 0) | 65 |
| `01NTNN-NCCNN-entry-M10-2026` | `101 → 101_8 → Y8` (01/NTNN, NCCNN TT89 3.0.9), **nhập tay** | 18 | tháng 10/2026 | — (ba bảng; phần II: `ThueNCCNN` 1 dòng, `ThueCNKCT` 1 dòng, `ThueNTNN` khóa; gõ vào lưới gốc) | 103 |
| `04NTNN-TT80-one-subcontractor-2026` | `101 → 101_8 → D6` (04/NTNN TT80 3.0.8) | 22 | từ 01/01/2026 đến 30/09/2026 (`D_D`) | 02-2/NTNN (sheet Menu `01-1` = sheet XLS `01-2`, 1 nhà thầu phụ) | 75 |
| `04NTNN-TT89-one-subcontractor-2026` | `101 → 101_8 → Y1` (04/NTNN TT89 3.0.9) | 22 | từ 01/07/2026 đến 30/09/2026 (`D_D`) | 02-2/NTNN (1 nhà thầu phụ) | 75 |
| `02NTNN-TT89-two-annexes-2026` | `101 → 101_8 → X9` (02/NTNN TT89 3.0.9) | 22 | từ 01/07/2026 đến 30/09/2026 (`D_D`) | 02-1/NTNN (1 nhà thầu nước ngoài, nước cư trú JP), 02-2/NTNN (1 nhà thầu phụ) | 108 |
| `02NTNN-TT80-two-annexes-2026` | `101 → 101_8 → C9` (02/NTNN TT80 2.5.1) | 22 | từ 01/01/2026 đến 30/09/2026 (`D_D`) | 02-1/NTNN (1 nhà thầu nước ngoài: JP, địa điểm 101), 02-2/NTNN (1 nhà thầu phụ, địa điểm 103) | 111 |
| `01CNKD-TT50-310-pl01-three-groups-Q3-2026` | `101 → 101_37 → U5` (01/CNKD **3.1.0**, chỉ oracle **HTKK 5.8.2**) | 21 | quý 3/2026 | 01-4 "PL 01 43/2026/QH16" (`PLuc_01_GiamTNCN_NQ43`, 2 dòng) | 295 |
| `05KK-TT89-withheld-Q4-2026` | `101 → 101_11 → Z8` (05/KK-TNCN TT89 **3.0.9**, chỉ oracle **HTKK 5.8.2**) | 14 | quý 4/2026 | — | 69 |

Z8 05/KK-TNCN TT89 (`05KK-TT89-withheld-Q4-2026`, non-gating, `htkkVersion` 5.8.2; adapter `05-kk-tncn-tt89-3.0.9` ghim vào
oracle 5.8.2 vì Z8 không có trong Menu.xml 5.8.1): KieuKy 14 = `SetLayoutToKhaiQuy` (chỉ kỳ quý). Driver chỉ tích `chkTKQuy` khi
ô hiện, bật và chưa tích; kết quả `GetPeriodInfo` (KieuKy Q, Quy 4, Nam 2026) là thẩm quyền. `CheckToKhaiBatDauCoHieuLuc` từ chối
quý trước 4/2026 bằng thông báo danh mục (driver chỉ báo ID). Kỳ vọng Decimal theo công thức XLS 5.8.2 (htkk_web
`docs/builder-patches/05KK-TT89-withheld-Q4-2026.md`): [35] = ROUND([23]×10/100,0) = 200001. Plan có 24 ô XML (giới hạn của plan):
mọi chỉ tiêu tính và các ô nhập chúng dùng; so sánh cả cây vẫn phủ đủ 69 lá. Manifest web mang `htkkVersion` 5.8.2
(`MANIFEST_HTKK_VERSION_CASES`), phải bằng `htkkVersion` của ca.

U5 3.1.0 (`01CNKD-TT50-310-pl01-three-groups-Q3-2026`, non-gating, `htkkVersion` 5.8.2; adapter `01-cnkd-hkd-3.1.0-pl01`
ghim vào oracle 5.8.2 vì XML 3.1.0 chỉ có trong HTKK 5.8.2): ca doanh thu 2.9.8 thêm nhóm 04 (200tr); tích giảm thuế NQ 43/2026/QH16
(cột AJ `chonGiamThue`) ở nhóm 01 và 04. Oracle Decimal (`htkk_hkd_web_cases.py`): CE = ([15]−[16])×tỷ lệ TNCN (1,5tr / 3tr / 3tr),
PL 01 H = G×30% (H20 = `G20*30.0%`), [17] = CE − CD + CF (AE291 = `CE291-CD291+CF291`, CD = H, CF = 0): 1.050.000 / 3.000.000 /
2.100.000, [20] TNCN 6.150.000, [47] 22.150.000. Tổng PL 01 theo đúng ràng buộc của `01_43_1_CNKD_HKD_TT50_310.xml`: H_22 (Σ được
giảm) → `tongSoThueTNCN_phaiNop` = 1.350.000, G_22 (Σ phải nộp) → `tongsoThueTNCN_duocGiam` = 4.500.000. Câu hỏi mở: AJ và CD không
có trong XML; nếu "Nhập từ XML" để AE tính lại với CD = 0 thì ô kiểm AE291/AE293 thất bại và ca cần chế độ `original-entry-export`.
Đã xác nhận (run 43127371885, 43130173107): nhập XML thành công, `declarationCellMismatchMask` 40 = AE291/AE293; PL 01 nhập đúng.
Ca chuyển sang chế độ `web-xml-import-tick-reexport` (mục dưới).

### Chế độ ca native `web-xml-import-tick-reexport` (U5 3.1.0, `01CNKD-TT50-310-pl01-three-groups-Q3-2026`, non-gating)

Cùng driver/GUI mode `declaration-web-import-inspect`, cùng input web (không đổi: nhánh input, `web_artifact_commit`,
`web_source_sha` như run 43130173107), cùng "Nhập từ XML" gốc; sau thông báo nhập thành công, kế hoạch cố định
`HtkkDeclarationCasePlans.ImportTick(caseId)` (adapter `01-cnkd-hkd-3.1.0-pl01`, mode `IMPORT_TICK_MODE`) làm thêm các thao
tác gốc cho phần lưới mà XML không mang được, rồi mới tới ô kiểm, Kết xuất, XSD và so toàn cây như mọi ca import.
Nguồn (đọc tĩnh TAX.HTKK.Business.dll / HTKK.exe 5.8.2, ghim `u5-310-tick-*` trong `htkk-oracle-baselines.json`, trạng thái
`added-reviewed`: phương thức chỉ có từ 5.8.2, 5.8.1 không có lớp `CnkdHkd01TT50Nckt310` nên `TickMethodPins()` từ chối):

- XML không có `chonGiamThue` (AJ) / `ct17_soThueGiam` (CD); sau nhập AJ trống, CD = 0, AE = CE. `AutoBindData_0` →
  `lockUnLockA_TK` để AJ mở ở dòng có CE > 0.
- Cột khóa dòng con (BN/BK/CA/BS/BO/BP, không có đường dẫn XML) chỉ được `SetCacDongCon` ghi (cho mọi dòng của bảng, qua
  `GeneralFunctions.SetLaiDongConBangF5`), và `SetCacDongCon` chỉ chạy từ `CellChange_0`, tức một lần sửa ô gốc. Nếu không,
  `daySangPLGiamThue` chép BN/BK/CA rỗng sang PL 01 (C/D/N) và so cây lệch ở `ma_diaDiemKD`/`ten_diaDiemKD`/`mst_diaDiemKD`.
- `CopyTableToTable5(deleteDataOld = true, colCompare AJ, valueCompare "true")` xóa các dòng PL 01 đã nhập và dựng lại từ
  các dòng đã tích; CD dòng tích := H của dòng PL 01 khớp C/I/K (H = G × 30%, XLS H20), dòng không tích CD := 0; `capNhatToKhai`
  (CF = 0 khi không có PL 03). AE = CE − CD + CF là kết quả của chính HTKK.
- `ButtonClick_0` nhận `idxRow`/`idxCol` 0-based (WinDoWorkEvent.ButtonClick truyền `e.Row`/`e.Column`) nhưng đọc CE/ghi AJ ở
  `idxRow − 1`, tức dòng ngay trên ô bấm (dòng tiêu đề 290 trống hoặc dòng 292 chưa tích): chỉ đổi khóa/giá trị AJ của dòng
  đó, rồi `DetectIndexOfTable(idxRow + 1)` đúng dòng bấm → `daySangPLGiamThue`, `capNhatToKhai`. AJ292 vẫn trống (kiểm lại).

Thứ tự, mỗi lượt timer một thao tác: `tick-pins` (13 thân phương thức, cùng cách ghim với Y8) → `tick-edits`: L291 qua editor
gốc (`^a`, giá trị, `{TAB}` như Y8) hai lần, `0` rồi `300000000` (giá trị web), để chắc chắn có thay đổi thật nên
FpSpread.Change → `winFpSpread_CellChange` → `WinDoWorkEvent.CellChange` → `CellChange_0` chạy (cột L cũng chép L → U) →
`tick-ticks`: SPACE trên AJ293 rồi AJ291 (ô `CheckBoxCellType` mở, chưa tích, hiện; AJ293 trước để `lockUnLockA_TK` đầu
`ButtonClick_0` tính lại khóa AJ mọi dòng theo CE sau khi sửa L291; dòng PL 01 theo thứ tự dòng tờ khai) → ButtonClicked → `ButtonClick_0` →
`tick-inspect`: AJ291/AJ293 còn tích, AJ292 trống (bắt buộc); đọc lại BN291..293 = `00001`, CA291..293 = MST hồ sơ (chỉ chẩn
đoán, mask) → ô kiểm chung (thêm CD291 = 450.000, CD292 = 0, CD293 = 900.000; AE291/AE293 giữ nguyên, không nới) → Kết xuất.
Stage thành công `declaration-import-tick-exported`; thất bại thao tác `declaration-import-tick-not-matched`. Trường chẩn đoán
(không giá trị): `declarationTickMethodPinsMatched`, `…EditsMatched`, `…TicksMatched`, `…ReadbackMatched`, `…PlannedCount`,
`…ActionCount`, `…FailureCode` (1 pin, 3 ô tích không phải checkbox mở chưa tích, 4 tích không ăn, 5 ô tích/ô trống đổi sau đó,
6 metadata, 8 ô sửa khóa, 9 kiểu ô, 10 foreground/focus, 11 editor, 13 đọc lại ô sửa, 17 thông báo gốc), `…MethodPinMask`,
`…MismatchMask` (bit = chỉ số thao tác), `…ReadbackMask` (bit 0–7 đọc lại, 8–11 ô tích, 12–15 ô phải trống). Provenance:
`inputMode` = `web-xml-import-tick-reexport`, `originalImportSucceeded` = true.

Vì sao không gõ lại cả tờ khai (`original-entry-export` như Y8): nhập XML giữ đúng mọi ô khác (ca 2.9.8 khớp toàn bộ; ca 3.1.0
chỉ lệch AE291/AE293), phần thiếu chỉ là ô tích AJ; nhập tay đầy đủ cần thêm ba loại danh mục thả xuống chưa từng chạy
(tỉnh control 100, xã control 101 phụ thuộc tỉnh, nhóm ngành DC_185), F5 trong bảng địa điểm lồng nhau và ô (1) B_26, mỗi thứ
một ẩn số Windows không liên quan tới NQ 43, trong khi phép tính giảm thuế (ButtonClick_0 → daySangPLGiamThue →
capNhatToKhai, công thức XLS) là cùng một đường trong cả hai chế độ.

B8 (02/QTT) dùng ca thiết kế `02QTT-dependants-Y2025` (hai người phụ thuộc, 6 và 12 tháng); web kết xuất XML qua descriptor engine.

I9 (01/NTNN TT80, non-gating) dùng ca thiết kế `01NTNN-two-contractors-M09-2026`: hai nhà thầu "GIẢ LẬP" không MST, ngành
01/02 của `DM_NNKD_NTNN.xml`, ngày thanh toán trong tháng 09/2026 (checkTKChinh E_27), ngày hợp đồng trước ngày chạy (E_36).
KieuKy 18 = `SetLayoutToKhaiThangLanPhatSinh` (tích sẵn `chkTkhaiThang`), driver đi nhánh tháng chung (`mskMonth` "09").

**Đổi kỳ I9 (HTKK 5.8.2).** HTKK 5.8.2 đặt Menu.xml `EndDate` 30/09/2026 cho I9 và đưa I9 vào
`GeneralFunctions.CheckToKhaiHetHieuLuc`: tháng sau 09/2026 và lần phát sinh sau 30/09/2026 bị từ chối ở hộp kỳ
(`HTKK-5.8.2-IMPACT.md`). Ba ca I9 chuyển sang kỳ còn hiệu lực trên cả 5.8.1 và 5.8.2, giữ nguyên nội dung (dòng, số tiền,
tổng): `01NTNN-two-contractors-M10-2026` → `01NTNN-two-contractors-M09-2026` (tháng 09/2026, 01/09–30/09/2026),
`01NTNN-occurrence-D20-10-2026` → `01NTNN-occurrence-D20-09-2026` (ngày 20/09/2026), ca thiết kế `01NTNN-zero-M10-2026` →
`01NTNN-zero-M09-2026`. Kết quả release 238/249 bên dưới là bằng chứng lịch sử của các tên cũ (kỳ 10/2026); ca mới cần chạy lại.
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

Release 244 (web ff456d23, builder 9c4260b): D6 `04NTNN-TT80-one-subcontractor-2026` (run 42373360682, 75 lá) và X9
`02NTNN-TT89-two-annexes-2026` (run 42373365304, 108 lá) **khớp toàn bộ**, bản xuất gốc lưu ở nhánh
`declaration-web-native-ntnn04-tt80-one-subcontractor-2026-output` 94c0b4dc / `declaration-web-native-ntnn02-tt89-two-annexes-2026-output`
b77fc69f; htkk_web ghim và bật D6, X9. Câu hỏi (1)–(3) đã có lời đáp: HTKK nhận kỳ, sheet và dòng phụ lục.

Y1 `04NTNN-TT89-one-subcontractor-2026` (run 42373362877): nhập, kết xuất, 11 ô kiểm và 13 lá XML khớp; so cây
`declarationTreeMismatchMask` 16 (chỉ PLuc), 75 lá so (= 79 lá của web trừ 4 lá `TTinDVu`, không phải 4 lá lệch; không có bit 32
nên cấu trúc trùng, thứ tự lá trùng với input web). Lưu trữ bị từ chối `XML_PRIVACY` lá 71 = `PL02_2_NTNN/BKCacNTPhu/
CTietBKCacNTPhu/ct6_ma` (web ghi `01`), dạng `text-other`. Trả lời câu hỏi (4) từ nguồn (snapshot `afc42204`):

- `InterfaceTemplates/xml/04_1_NTNN_TT89_309.xml` (sha256 a585052e…fa48): `ct6_ten` = AG (control 87, `SelectedValue="CR"`),
  **`ct6_ma` = CR** (control 0), `pathCheckTrung` = CS; dòng dữ liệu 49.
- `InterfaceTemplates/excel/04_NTNN_TT89_309.xls` (sha256 3326d1ab…ca61) sheet `01-2`: CR49 khóa, có công thức khóa trùng
  `TRIM(E49)&TRIM(R49)&TRIM(AG49)&TRIM(AM49)&TRIM(AR49)&TRIM(AW49)` — chép từ 02-2 của X9 (`02_2_NTNN_TT89_309.xml`: ở đó
  CR là `pathCheckTrung`, `ct6_ma` là CQ; X9 khớp). Ở Y1 cột mã và cột khóa trùng lệch một cột, nên công thức nằm trong cột mã.
- `WinSpreadProcess.fpSpBindDataCell` (HTKK.exe 0x60001a8, IL sha256 f791ac662986fecf18a27a3c5ccc54a0a65bec1cf6a2ce1167d9e53fa35e5e49),
  nhánh control không đặc biệt: chỉ gọi `ResetFormula` khi ô **không khóa** và giá trị khác rỗng; ô khóa chỉ được `set_Text`. CR49
  khóa nên công thức còn nguyên sau nhập XML và được tính lại khi `ProcessSheet` (0x60001a2, IL sha256 dba83252…5035e) bật lại
  `AutoCalculation` của sheet. HTKK.exe sha256 411141d2e728a45f4a35a876afb169d0ac2450de2499e8a1f43ac29ab6401938.
- `WinDoWorkEvent.ExportDataTableToTableNode` (HTKK.exe 0x6000050, IL sha256 de6af1d32db04b6a542259b23ea70b4f4d2391a78e70fad3847472ccc24659e8)
  đọc lá bảng từ `Cells[DataLocationTemplateRowStart + i - 1, cột].Value` của lưới rồi `GeneralFunctions.GetValueExportXML`, nên
  `ct6_ma` = kết quả công thức CR49 (chuỗi ghép tên nhà thầu, ngành nghề, số và ngày hợp đồng), không phải mã `01`.

Đó là văn bản tự do theo thiết kế, quy tắc privacy từ chối đúng. Header B32/B34/B37/B38 bắt buộc E, R, AR, AW (B36 đọc CR49 nên
không bao giờ rỗng), vậy mọi input hợp lý đều cho chuỗi có chữ. Chỉ một input dị thường (tên E/R và số hợp đồng toàn chữ số,
ngành nghề trống) mới có thể cho chuỗi toàn số qua được quy tắc, và điều đó tùy cách FarPoint trả AW49 — không chứng minh được,
nên không dùng. Không nới quy tắc, không đổi kỳ vọng của ca, web không đổi (vẫn ghi mã ngành nghề).
Chưa chứng minh được từ nguồn: chuỗi chính xác FarPoint tính cho `TRIM(AG49)` (ô combo control 87, `EditorValue` mặc định) và
`TRIM(AW49)` (ô `MaskCellType` "00/00/0000", `InsertDateCell` 0x60001af đặt Text `dd/MM/yyyy`). Chẩn đoán mới, không chứa giá trị:
`value_shape` trả `allowed-text-concat-date` / `allowed-text-concat` khi giá trị bị từ chối ghép hoàn toàn từ văn bản cho phép của
ca và dãy số (có / không có mảnh ngày `dd/MM/yyyy` hoặc `yyyy-MM-dd`); vẫn từ chối, không lưu. Lần chạy Windows sau của Y1 (không
đổi input) phải cho cùng mask 16, cùng lá 71, dạng `allowed-text-concat-date` (ngày dạng `dd/MM/yyyy`) hoặc `allowed-text-concat`
(ngày thành dãy số hay combo trả chỉ số); dạng `text-other` nghĩa là giả thuyết sai.

#### Y1, chuỗi CR49 (release 246 và quyết định ghi đúng chuỗi HTKK)

Release 246 (run 42380879950, builder 0545e50, web 2d83a6eb): như release 244 (nhập/kết xuất, 11 ô kiểm, 13 lá XML, mask 16,
lá 71 = `ct6_ma`), dạng `allowed-text-concat`: giá trị tách hết thành văn bản cho phép của ca và dãy số, **không** có mảnh
`dd/MM/yyyy`. PM quyết định: web ghi `ct6_ma` đúng chuỗi HTKK. Từng phần của `TRIM(E49)&TRIM(R49)&TRIM(AG49)&TRIM(AM49)&TRIM(AR49)&TRIM(AW49)`
theo nguồn (snapshot `afc42204`, đọc IL như dữ liệu; HTKK.exe 411141d2…1938, FarPoint.Win.dll fae1320c…ef4d2a,
FarPoint.Win.Spread.dll 2e7a0d4f…4c50, FarPoint.CalcEngine.dll 19183e5a…0d5a, TAX.HTKK.Utilities.dll ccc35605…17ec):

- **E, R, AR** (control 0, ô nhập không khóa): `fpSpBindDataCell` 0x60001a8 (IL f791ac66…5e49) nhánh mặc định: `Trim` giá trị XML
  rồi `set_Text`; văn bản giữ nguyên (D6/X9 xuất lại cùng các cột đó khớp). Độ tin cậy cao.
- **AG** (control 87): `fpSpFormatTableCell` 0x60001ab (IL 937b945f…6c20) → `WinInsertCombox` 0x60001be (IL 3c4f6dae…074f) tạo
  `ComboBoxCellType` (MaxLength 1000, Items/ItemData, Editable) và **không** gọi `set_EditorValue` (không assembly HTKK nào gọi;
  `ComboBoxCellType..ctor` 0x6007145 IL 13c050cb…70ad không gán trường `q`) → EditorValue 0 = Item; `ComboBoxCellType.Parse`
  0x6007151 (IL bd312555…b4b2) trả nguyên văn bản khi `IsValid` (0x6007150: độ dài ≤ MaxLength). `GetValueFromSelectedCell`
  bảng 0x6000085 (IL 977739e9…0695) không có nhánh '87', nên tên `ct6_ten` nhập vào AG giữ nguyên (X9 release 244: `ct6_ten`
  của 02-2 khớp). Phần AG = chữ mục danh mục ("Dịch vụ, cho thuê máy móc thiết bị, bảo hiểm"). Độ tin cậy cao.
- **AM**: control template không có ô AM; XLS AM49 trống (BIFF blank) → "". Độ tin cậy cao.
- **AW** (control 14): `ReChangeValue` 0x600008f (IL 2d977d98…e27e) đổi `yyyy-MM-dd` của XML thành `dd/MM/yyyy`;
  `HTKKFormater.toDateDDMMYYYY` (Utilities 0x600040e, IL 1a5fe17c…461e) giữ `15/03/2026`; `InsertDateCell` 0x60001af (IL
  92fe05f4…7bc7f55) đặt `MaskCellType` mặt nạ "00/00/0000", MaskChar '.', rồi `set_Text`. `Cell.set_Text` 0x600009c (IL
  40ab4966…f927) gọi `Formatter.Parse` rồi `SetValue`; `EditBaseCellType.Parse` 0x6006e77 (IL e2269139…dcf) →
  `MaskFormatter.FromFormattedString` 0x60000ff (IL 231379ad…0579; formatter kiểu 1 do `MaskCellType..ctor` 0x6006ffd IL
  d4ed3285…26ea tạo) → phần tử `h` (dựng bởi `r.a` 0x6000fbd IL 1d8212fa…2e04 với mã ký tự `r.b` 0x6000fc0 IL 86a6fa7a…4d78:
  '0' → 19, '/' → 0) → `h.a` 0x6000ec3 (IL 82f3aef2…e2ea) → `h.f` 0x6000edb (IL 42bdb017…f382): chỉ giữ ký tự ở vị trí có mã ≥ 6
  (chỗ giữ chỗ của mặt nạ), `TrimEnd(' ')`. Giá trị ô AW = **"15032026"** (ddMMyyyy, chuỗi). Khớp dạng release 246 (dãy số, không
  mảnh ngày). Độ tin cậy trung bình–cao (chuỗi IL đầy đủ; chưa có bản xuất gốc lưu được).
- **TRIM, &**: `TrimFunctionInfo.Evaluate` 0x60008da (IL ec9d65b6…f85f: `String.Trim`, mỗi dãy khoảng trắng giữ ký tự đầu),
  `ConcatenateOperatorInfo.Evaluate` 0x6000124 (IL fdd637e8…c30e: `ToString` hai vế).

Chuỗi kỳ vọng của ca (oracle `check_key` trong `htkk_declaration_web_cases.py`, tính từ input tổng hợp của ca):
`NHA THAU PHU VIET NAM A - GIẢ LẬP` + `NHA THAU NUOC NGOAI B - GIẢ LẬP` + `Dịch vụ, cho thuê máy móc thiết bị, bảo hiểm` + "" +
`HD-GL-041` + `15032026`. Web (htkk_web `work/ntnn-y1`, plugin `check-key-code-cell`) ghi đúng chuỗi đó vào `ct6_ma`.

**Cho phép lưu theo lá, theo ca (không nới quy tắc chung)**: `_texts` chấp nhận ở đúng một đường dẫn
`HSoThueDTu/HSoKhaiThue/PLuc/PL02_2_NTNN/BKCacNTPhu/CTietBKCacNTPhu/ct6_ma` của đúng ca `04NTNN-TT89-one-subcontractor-2026` đúng
một giá trị: `check_key(case)` mà oracle tính lại từ input của ca (CHECK_KEYS). Mọi giá trị khác ở lá đó, và chuỗi đó ở lá khác
hay ca khác, vẫn qua quy tắc privacy như cũ. An toàn vì: mọi phần của chuỗi là dữ liệu tổng hợp đã có trong danh sách văn bản cho
phép của ca (tên nhà thầu giả lập, mục danh mục nguồn, số hợp đồng giả lập) cộng ngày hợp đồng giả lập; giá trị so khớp chính xác,
không phải mẫu. Oracle `_ntnn_qt` cũng kiểm `ct6_ma` của dòng phụ lục bằng `check_key` (VALUE) cho cả input web lẫn bản xuất gốc.
Ca vẫn non-gating.

**Chẩn đoán khi giá trị khác**: ngoài `valueShape`, trạng thái từ chối có `concatLayout` — bố cục mảnh không chứa giá trị: chữ cột
của phần có tên (E, R, AG, AR), `a<chỉ số>` cho văn bản cho phép khác (chỉ số trong danh sách văn bản đã sắp xếp), `dmy`/`iso`
(`=AW` nếu bằng ngày của ca), `n<độ dài>` cho dãy số, kèm `=ddMMyyyy|yyyyMMdd|MMddyyyy|ddMMyy|oadate|code|index` nếu bằng một
cách mã hóa ngày AW / mã AG của chính ca. Ngữ pháp cố định (regex `LAYOUT`), `publish-htkk-declaration-native-output.safe_context`
bỏ mọi thứ ngoài ngữ pháp.

Lần chạy Windows sau của Y1 (input web mới, `ct6_ma` = chuỗi trên): nếu giả thuyết đúng → nhập/kết xuất, 11 ô kiểm, 13 lá XML
khớp, so cây **mask 0**, lưu bản xuất gốc (published), `allTaxValuesMatched` true. Nếu sai → từ chối `XML_PRIVACY` lá 71
section 16 với `concatLayout`, ví dụ `E.R.AG.AR.n5=oadate` (AW là số serial), `E.R.AG.AR.dmy=AW` (giữ dấu "/"),
`E.R.AG.n1=index.AR.n8=ddMMyyyy` (combo trả chỉ số) — đủ để chọn ứng viên mà không lộ giá trị. Y1 vẫn ẩn trên web tới khi khớp
toàn bộ.

X9 (02/NTNN quyết toán TT89, non-gating, nhập XML) dùng `02NTNN-TT89-two-annexes-2026`: cùng kỳ KieuKy 22 (`range`); hộp kỳ
tích "02-1/NTNN" và "02-2/NTNN" (Sheet ID Menu.xml `01-1`/`01-2` = sheet workbook cùng tên). `Ntnn02TT89Nckt309` không có
`FinishImportXML`; `AutoBindData_0` (0x600191a) ghi trường hợp quyết toán vào BK8/BL8; `Refresh_1/2` gọi
`tinhGiaTriHDCt4_tk`/`tinhDoanhThuChuaThueCt4_tk` chép BO34/BO35 (= tổng [8]/[9] của 02-1 + tổng [9]/[10] của 02-2) vào AF34/AF35,
bằng giá trị web. Nước cư trú (control 56, 02-1 J → CW `ct3_ma`): `GetDMQuocGia` (`Catalogue_Quoc_Gia_full.xml`), nhập XML
ghi thẳng CW. Oracle Decimal `NTNN02`/`ntnn02_expected` (gộp với 04/NTNN trong `ntnn_qt_expected`/`_ntnn_qt`) tính lại sheet 01
dòng 34–49 (AF34/AF35 = tổng hai phụ lục, dòng 37 = IF(r35 − r36 > 0, …, 0), 38 = 39 + 40, AO = AF − W, 41 = 42 + 43, 44–46 =
IF(5 − 6 < 0, 0, 5 − 6), 47–49 = IF(5 − 6 ≥ 0, 0, |5 − 6|)): AF34 3.000.000.000, AF35 2.800.000.000, AF37 1.800.000.000, AF38
130.000.000, AO40 4.000.000, AF41 126.000.000, AF44 = AF46 4.000.000; dòng và tổng hai phụ lục. Không có ca 0: Header B55
(`IF(AND(01!AO39=0,01!AO40=0),0,1)`, cờ Y) chặn kết xuất khi cả hai chênh lệch thuế bằng 0. Câu hỏi mở: nhập XML giữ `ct3_ma`
và kết xuất lại `ct4` (MST nhà thầu nước ngoài, control 26 rỗng) là `xsi:nil` như web?

C9 (02/NTNN quyết toán TT80, non-gating, nhập XML) dùng `02NTNN-TT80-two-annexes-2026`: kỳ KieuKy 22 (`range`) 01/01/2026–30/09/2026
(Menu.xml `EndDate` 01/10/2026, `CheckToKhaiHetHieuLuc` như D6); hộp kỳ tích "02-1/NTNN" và "02-2/NTNN". `Ntnn02TT80Nckt251` không có
`FinishImportXML`; `AutoBindData_0` (0x600190b) ghi trường hợp quyết toán vào BK8/BL8. Khác X9: AF34/AF35 là **công thức XLS**
`=BK34`/`=BK35` (BK34 = 02-1 BG27 + 02-2 BD26, BK35 = 02-1 BY27 + 02-2 BS26); `CellChange_1/2`, `UpdateFormula_1/2`, `ClearData_1/2`,
`Refresh_1/2` chỉ đặt lại đúng công thức đó (như D6). Dòng 2 của tờ khai là `DThuChuaGomGTGT`; dòng 02-1 có `ct10` = số lượng lao
động (5), tổng `tong_ct10` 5. Control 100 (địa điểm, `dicTinhTPMoi` từ `Catalogue_Dia_Ban_Tinh_Moi.xml`): 02-1 AJ → CO `ct6_ma` 101
"Thành phố Hà Nội", 02-2 AM → CB `ct7_ma` 103 "Thành phố Hải Phòng" (kiểm ô CO25/CB24 sau nhập). `isValidDuLieuTK` (0x6001915) chạy
`checkPL2_1`/`checkPL2_2` trên phụ lục đang hiện, mọi lỗi tô hồng (chặn, 0016): dữ liệu ca đủ mọi ô bắt buộc, ngày trước hôm nay,
[8]/[9] (02-1) và [9]/[10] (02-2) khác 0, không trùng. Oracle `NTNN02` mở rộng (`_NTNN02_TT80`): cùng công thức dòng 34–49 như X9,
tên `DThuChuaGomGTGT`, 02-1 ba lá `ct8/ct9/ct10`: AF34 3.000.000.000, AF35 2.800.000.000, AF37 1.800.000.000, AF38 130.000.000, AO40
4.000.000, AF41 126.000.000, AF44 = AF46 4.000.000, AF47 0; 02-1 `tong_ct8` 2.000.000.000, `tong_ct9` 1.800.000.000, `tong_ct10` 5; 02-2
`tong_ct9` = `tong_ct10` 1.000.000.000. XML web 115 lá (111 lá thuế). Ca 0 chỉ thiết kế (`02NTNN-TT80-zero-2026`, không phụ lục; C9 không
có quy tắc Header chặn quyết toán 0). Câu hỏi mở cho lần chạy Windows: (1) nhập XML giữ `ct6_ma`/`ct7_ma` (control 100) và
`ct3_ma`; (2) sau nhập AF34/AF35 vẫn là công thức `=BK34`/`=BK35` (không có Refresh chế độ 2 nào chạy); (3) `checkPL2_1`/`checkPL2_2`
không chặn kết xuất với ngày 05/01/2026–30/09/2026; (4) `ct4` (MST nhà thầu nước ngoài) và `ct3`/`ct5` của 02-2 rỗng kết xuất lại
`xsi:nil` như web; (5) `ct10` của 02-1 (số lượng lao động, control 16) kết xuất là `5`.

**Kỳ lần phát sinh (KieuKy 18, kiểu kỳ plan `day`; non-gating)** — I9 `01NTNN-occurrence-D20-09-2026` (nhập XML; ngày 20/09/2026, trước đây `01NTNN-occurrence-D20-10-2026`),
Y8 `01NTNN-NCCNN-occurrence-D20-10-2026` (nhập tay, cùng chế độ `original-entry-export` như ca tháng) và J1
`03NTNN-occurrence-D20-10-2026` (nhập XML), ngày phát sinh 20/10/2026 (I9: 20/09/2026). Dò từ HTKK 5.8.1 (snapshot `afc42204`, htkk_web
`docs/NGHIEP-VU-NTNN.md` mục "Kỳ lần phát sinh"):

- Hộp kỳ: `frmHTKKPeriod_Load` (0x6000484) → `SetLayoutToKhaiThangLanPhatSinh` (0x60004a9; SHA-256 thân phương thức như htkk_web: `5fabdefc…`): Tháng tích sẵn, có
  "Lần phát sinh" (`chkTKLanPS`). Tích `chkTKLanPS` → `CheckedChanged` (0x60004b2, `bea14e68…`) → `ResetpnVT1_2NgayThangQuyNam`
  (0x60004b1, `d758413b…`, nhánh 6) hiện `pnNgay`/`pnThang`/`pnNam` và điền ngày hôm nay (`LoadDefaultInfor` 0x60004e0);
  `pnTuNgay`/`pnDenNgay` vẫn ẩn. Driver: `SetCheck(chkTKLanPS)`, gõ `mskYear`, `mskMonth`, `mskDay` qua `SetDeclarationText`
  (Leave gốc `mskDay_Leave` 0x60004d0 / `mskMonth_Leave` 0x60004d1 đệm 2 chữ số), **không** đụng `mskTuNgay`/`mskDenNgay`;
  `periodDateMatched` đòi `chkTKLanPS` tích, `chkTkhaiThang` không, ba ô đang hiện đúng ngày của plan và hai ô từ/đến ngày ẩn.
- Sau Đồng ý: `GetPeriodInfo` (0x60004e2, `7e938338…`; bảng KieuKy chỉ số 16 = "18", nhánh `chkTKLanPS` tại 0x2667) cho
  `KieuKy` `D`, `Ngay`/`Thang` (đệm 2), `Nam`, `TuNgay` = `DenNgay` = `kyKKhai` = `dd/MM/yyyy`; `DeclarationIdentity` kiểm cả bảy.
  `CheckPeriod` (0x60004ef): `CheckNgayThangNam` (0x60004db: năm < 2000 → 0067, tháng/năm sai → 0062, ngày sai → 0071), `D` sau
  hôm nay → 0223, `CheckHLToKhaiTT80` (0x60004f2) `D` trước 01/01/2022 → 0576 (I9/J1; Y8 không thuộc danh sách TT80),
  `CheckHieuLuc` (0x6000504) trước `StartDate` (Y8 01/10/2026) → 0441. 20/10/2026 qua hết.
- XML: `BindToKhaiInfoToTTinChung` (0x60000f4) chép kỳ; `xmlExportTTinChung` (0x6000049) không đổi `kieuKy` `D` cho ba menu này:
  `kieuKy` D, `kyKKhai`/`kyKKhaiTuNgay`/`kyKKhaiDenNgay` 20/10/2026, tháng trống (manifest kỳ `('D', '20/10/2026', '20/10/2026',
  '20/10/2026')`). `WinDoWorkImportFormXml` (0x600007d) báo 0437 nếu `kieuKy`, từ/đến ngày, từ/đến tháng hoặc `loaiTKhai` khác kỳ đang mở.
- Dòng: `AutoBindData_0` I9 (0x60018ef) / J1 (0x6001931) ghi `kyKKhai` vào AE / BE mọi dòng đang có lúc nạp sheet và khóa; Y8
  (0x60018f9) ghi rồi `LockUnlock` (deleteData) đặt lại AE về mặc định, nên ca Y8 gõ AE = 20/10/2026 (`Entry`: cùng 21 lệnh như ca
  tháng, chỉ AE78/AE86 đổi; E_27 của `checkTKChinh` bắt AE nằm trong TuNgay–DenNgay = đúng ngày đó). Web XML I9/J1 đã mang ngày
  đó ở `ct6`/`ct7` (`2026-10-20`).
- Oracle: `NTNN_ROWS` của ba ca = dòng của ca tháng tương ứng + `ct6`/`ct7` = `2026-10-20` (Decimal giữ nguyên: I9 tổng `tong_ct5`
  1.500.000.000, `tong_ct9` 65.000.000, `tong_ct13` 58.000.000, `tong_ct14` 123.000.000; Y8 `mucII_tong_ct14` 7.000.000, mục I.II
  `mucI_tong_ct14` 20.000.000; J1 `tongct6` = `tongct8` 1.100.000.000, `tongct10` = `tongct11` 0). Ô kiểm và lá XML như ca tháng.
- Câu hỏi mở cho lần chạy Windows: (1) nhập XML I9/J1 với `kieuKy` D không bị 0437; (2) sau nhập AE/BE bị khóa và giữ 20/10/2026
  (kết xuất `ct6`/`ct7` = `2026-10-20`); (3) J1: `checkTKChinh` đưa văn bản BE nguyên dạng cho `ValidateFullDate(…, "ddMMyyyy")`
  — nếu giá trị ô có dấu `/` thì E_18 chặn kết xuất (điểm mở từ ca tháng, nay BE luôn khác rỗng); (4) Y8: AE gõ được sau khi tích
  M8 (LockUnlock mở lại) và E_27 nhận; (5) hộp kỳ hiện đúng ba ô ngày/tháng/năm, từ/đến ngày ẩn, và `KieuKy` D sau Đồng ý.

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
