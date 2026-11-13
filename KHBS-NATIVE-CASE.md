# Native case design: 01/GTGT kê khai bổ sung lần 1 (D1, KHBS)

Status: **design only, not wired, not dispatched.** No mode, registry case, workflow option or
reader change is made here. The web side (htkk_web branch `work/khbs-01gtgt`) has the KHBS engine,
the XML serializer, the producer `scripts/generate-htkk-web-khbs-reference.mjs --case
khbs-zero-to-sale10` and keeps the feature hidden (`KHBS_01GTGT_RELEASED=false`) until this case
passes. The oracle is **HTKK 5.8.2** (per-case `htkkVersion`, non-gating, `releaseGate=false`).

Everything below was read statically from the pinned 5.8.2 payload (archive `51baf5c8…d424`,
`HTKK.msi` `17c21f3c…fd73`, `Data1.cab` `5427c663…530c`, HTKK.exe `331ed84a…f98a`,
TAX.HTKK.Business.dll `c446db6f…686c`). Nothing was executed. Method tokens are 5.8.2 MethodDef
tokens; the web file `data/htkk-01-gtgt-khbs-rules.json` pins their IL body SHA-256.

## Case

- `01GTGT-khbs-zero-to-sale10-M10-2026`, adapter `01-gtgt-2.8.3-khbs` (new), D1 2.8.3, month
  10/2026, activity 00, no annex, `amendmentOrder` 1.
- Previous version (C0): the all-zero first declaration that `gtgt-amendment-inspect` already types
  and saves with the original **Ghi** (run 40421871768; file
  `01_GTGT_TT80_CQTQL10129_00_102026_283.xml`, 27 money cells 0).
- Amendment (B1): web XML with loaiTKhai B, soLan 1, [32] 1.000.000, [33] 100.000, [40] 100.000 and
  the two fragments PL01_KHBS / PL01_1_KHBS. Ngày lập KHBS **13/11/2026** (before the 20/11/2026
  deadline): ct3a_1 = 2026-11-13, ct3a_2 = 0, ct3b = 0; tongCong_7 = tongCong_ct10 = 100000.

## Driver flow (new mode `gtgt-amendment-khbs-inspect`)

1. Reuse `gtgt-amendment-inspect` up to `GtgtOriginalDeclarationSavedInspected` (C0 Ghi, message
   0002, dirty false, file hash fixed).
2. Reuse `gtgt-amendment-open-inspect`: original **Đóng** (`cmdExit`), reopen D1 10/2026 by the
   original menu, tick **OptBosung**, then — the only new GUI input — type `13/11/2026` into
   `mskNgayLapKHBS` instead of keeping today. `frmHTKKPeriod.CheckPeriodKhbs` (0x060004F6) refuses a
   date after today (0224) and after hạn nộp + 10 years (0507), and needs the C0 file (0107). Require
   `TTPeriodInfo.NgayLapKHBS` = 13/11/2026, LoaiToKhai B, SoLan 1 after **Đồng ý**.
3. **Nhập từ XML** (`cmdImportXML_Click` 0x060003AC) with the fetched web B1 file, same file-dialog
   handling as `gtgt-web-import-inspect`. With LoaiToKhai B it calls `FinishImportXML` then
   `RevertFromXml` (rebuilds 01-KHBS / 01-1-KHBS from the XML) and shows 0291 "Nhập dữ liệu từ XML
   thành công."; 0278 means the structure was refused (record the id, stop).
4. Original **Tổng hợp KHBS** (`btnTongHopKHBS_Click` 0x060003C1, KieuKHBS 3 branch:
   `TongHopKhbsMoi`, `TinhSoThuePhaiNopKhauTruHoan_01_KHBS`, `TinhSoNgayNopCham`,
   `TinhSoTienPhatNopCham`, `AnHienSoNgayVaSoTienNopCham_01_KHBS`), acknowledge 0222 "Tổng hợp dữ
   liệu lên KHBS thành công". This recomputes both KHBS sheets from the saved C0 file
   (`WinFnProcess.ReadSheet_LanTruoc`) and the imported main sheet, so any web engine error shows in
   the export of step 5.
5. Original **Kết xuất** XML (existing export inspection; schema is
   `InterfaceTemplates/Validate/KHBS_01_GTGT_TT80_283.xsd` `b0fcb966…af76f` for LoaiToKhai B), message
   "Kết xuất tờ khai xml thành công.".
6. Compare the native export tree with the web input: every leaf of TTinChung (except
   `ngayLapTKhai` and the four TTinDVu leaves), CTieuTKhaiChinh, PL01_KHBS and PL01_1_KHBS, element
   order, `id` attributes and `xsi:nil`. Report counts and booleans only, as the other web-import
   modes do; never XML text.

## Points the case decides (web hypotheses from static reading)

- ct04/ct05 of 01-1/KHBS are controltype 0 in the binding, so `GetValueExport` writes Cell.Text:
  web writes `1.000.000` (main-sheet NumberCellType, ShowSeparator, `.`); depends on the runner
  culture as for the main sheet.
- Default rows kept: Muc_2 BKePLuc/ChiTiet, Muc_II/Muc_III ChiTiet with ct3 0, Muc_B leaves 0/empty,
  Muc_B CTietTaiLieu, and `xsi:nil` on empty dates and empty mstDLyThue / ngayKyHDDLyThue.
- Header of both fragments from TTinChung (`xmlExportTTinChungKHBS` 0x0600004A), ma_DonViTien VND.
- PLuc order PL01_KHBS then PL01_1_KHBS; BKeHSo ma_HSo 0026, ten_HSo 01/GTGT.

## Files a wiring change touches

`scripts/htkk-native-cases.json` (adapter + case, `amendmentOrder` 1 allowed only for this adapter),
`scripts/htkk_native_cases.py` (trusted adapter, driver), a KHBS web-input validator next to
`htkk_annex10_web_cases.py` (case id, fixed values above, leaf allowlist of the two fragments),
`scripts/fetch-htkk-web-input.py`, a new partial `HtkkGtgtAmendmentKhbsInspection.cs`,
`htkk-native-automation-registry.json` + `generate-native-automation-registry.py` output
(`HtkkNativeAutomationEnums.cs`), the workflow mode lists in `probe-htkk-windows.yml`, the reader
allowlists in `Get-HtkkSafeGuiReferenceResult.ps1`, and contract tests like
`test_amendment_open_contract.py`. On the web side: the case plan and
`scripts/check-native-input-contract.mjs` (add the producer).

## Second case (later)

A positive late-day count needs a period whose deadline is before the run date and a ngày lập
after it (e.g. M09/2026, deadline 20/10/2026, ngày lập 13/11/2026: 24 days, ct3b =
ROUND(0,0003 × 24 × amount)). The prior-save step is pinned to M10/2026 today.
