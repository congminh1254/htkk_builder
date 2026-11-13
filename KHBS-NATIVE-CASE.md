# Native case design: 01/GTGT kê khai bổ sung lần 1 (D1, KHBS)

Status: case 1 `01GTGT-khbs-zero-to-sale10-M10-2026` **passed** on Windows (release run 43358377013:
khbsTreeMatched, mask 0, 270 leaves, message ids 0). Case 2 `01GTGT-khbs-sale5-to-sale10-M09-2026` is
**wired, non-gating, not yet run**. Both use adapter `01-gtgt-2.8.3-khbs`, driver mode
`gtgt-amendment-khbs-inspect`, oracle HTKK 5.8.2 (per-case `htkkVersion`, `releaseGate=false`). The case
status comes from the in-harness whole-tree comparison; since case 2 the raw ORIGINAL B1 export is also
**retained privately** (registry `privateArtifactPolicy: raw-khbs-reexport`, see "Raw native output
retention"), so a mismatch can be diagnosed from the bytes. The web side has the KHBS engine, the XML
serializer, the producer `scripts/generate-htkk-web-khbs-reference.mjs --case khbs-zero-to-sale10 |
khbs-sale5-to-sale10` and keeps the feature hidden (`KHBS_01GTGT_RELEASED=false`) until case 2 passes.

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

## Bounded result fields

All active only in this mode (reader rejects them elsewhere): `khbsDateTyped`, `khbsPeriodMatched`,
`khbsImportInvoked/Succeeded/PathMatched`, `khbsSummaryInvoked/Acknowledged`, `khbsExportInvoked`,
`khbsExportSchemaPinnedVerified`, `khbsExportSucceeded`, `khbsIdentityMatched`, `khbsCreationDateValid`,
`khbsTreeMatched`, `khbsOriginalMoneyMatched`, `khbsSavedMoneyMatched` (case 2); message ids `khbsImportMessageId`, `khbsSummaryMessageId`, `khbsExportMessageId`
(pinned Message.xml id, 9999 = not catalogued); `khbsLeafCount` (expected 270 = 70 main + 200 KHBS
leaves; case 2: 296 = 70 + 226); `khbsOpenMainState` (0 not observed, 1 zero, 2 the C0 vector); `khbsMismatchMask` (1 structure, 2 attributes, 4 TTinChung, 8 CTieuTKhaiChinh, 16 PL01_KHBS,
32 PL01_1_KHBS, 64 other value, 128 output identity/date); `khbsFirstDifferenceOrdinal` (1-based leaf
ordinal in web order); `khbsExportBytes`, `khbsExportSha256`. Terminal failures:
`gtgt-amendment-khbs-import-rejected`, `-summary-rejected`, `-export-rejected`, `-not-matched`. No values,
paths or text are recorded. Input privacy: `htkk_khbs_web_cases.py` (exact PLuc subtree, B/1 header,
then the unchanged no-annex allowlist on an in-memory C/0 projection).

## Files the wiring touched

`scripts/htkk-native-cases.json` (adapter + case, `amendmentOrder` 1 allowed only for this adapter),
`scripts/htkk_native_cases.py` (trusted adapter, driver), a KHBS web-input validator next to
`htkk_annex10_web_cases.py` (case id, fixed values above, leaf allowlist of the two fragments),
`scripts/fetch-htkk-web-input.py`, a new partial `HtkkGtgtAmendmentKhbsInspection.cs`,
`htkk-native-automation-registry.json` + `generate-native-automation-registry.py` output
(`HtkkNativeAutomationEnums.cs`), the workflow mode lists in `probe-htkk-windows.yml`, the reader
allowlists in `Get-HtkkSafeGuiReferenceResult.ps1`, and contract tests like
`test_amendment_open_contract.py`. On the web side: `scripts/check-native-input-contract.mjs` (the producer). The web case plan
(`data/htkk-case-plan.json`) lists only release-gate cases, as `validate_plan` requires, so a candidate
case is not added there.

## Second case: non-zero C0, a decrease, positive late days

- `01GTGT-khbs-sale5-to-sale10-M09-2026`, month **09/2026** (GetHanNopToKhai D1: due 20/10/2026, a Tuesday),
  the same fixed ngày lập 13/11/2026: **24** late days, ct3b = 0,03% × 24 × 200.000 = **1.440**.
- C0, typed with two fixed original editor actions before Ghi (EditOriginalGtgtCase, the same keyboard path
  as the web-import cases): [30] (row 46, col 9) 2.000.000 → HTKK computes [31] 100.000; then [32] (row 47,
  col 9) 1.000.000 → [33] 100.000. The whole 27-cell vector ([27] 3.000.000, [28]/[35]/[36]/[40a]/[40]
  200.000, [34] 3.000.000) must be on the sheet (`khbsOriginalMoneyMatched`) and in the saved file
  `01_GTGT_TT80_CQTQL10129_00_092026_283.xml` (`khbsSavedMoneyMatched`; GetFileNameBySheet uses Thang,
  padded to two digits by GetPeriodInfo 0x0efc). The period dialog gets month `09` (mskMonth) and the
  TTPeriodInfo checks expect Thang `09` for this case only (`PeriodMonth()`); every other D1 driver keeps 10.
- B1 web XML: [30] 0, [31] 0, [32] 4.000.000, [33] 400.000, [40] 400.000. PL01_1_KHBS rows [27] [28]
  [30] [31] [32] [33] [34] [35] [36] [40a] [40], with **negative** chênh lệch on [30] (−2.000.000) and
  [31] (−100.000); tongCong_7 = tongCong_ct10 = 200.000. 296 compared leaves (70 main + 226 KHBS).
- B1 main sheet before the import: zero or the carried C0 vector, recorded as `khbsOpenMainState` 1/2
  (case 1 must be 1). Input privacy: the same exact PLuc allowlist, the M09 main header projected in
  memory onto the M10 baseline (`M09_PERIOD`), then the unchanged no-annex allowlist.

### Run 43367487266 (case 2): stopped after the non-zero Ghi

The C0 was typed and saved exactly (`khbsOriginalMoneyMatched`, `khbsSavedMoneyMatched`), then the run waited
at `gtgt-original-declaration-save-success` until the automation limit: `amendmentPriorDirtyCleared` false, so
the observer never reached the original Đóng. cmdSave_Click clears `isDataChanged` right after the 0002
message, and only Change/EditChange of the grid (or F5–F8 keys) set it again; the zero C0 of case 1 never hit
this. The driver now records `khbsPostSaveWaitMask` (1 owner hidden, 2 owner disabled, 4 grid hidden, 8 grid
disabled, 16 original message visible, 32 isDataChanged set) and stops after 30 s with
`gtgt-amendment-khbs-post-save-timeout`. For case 2 only, when the flag alone (mask 32) stays set for 2 s and
the sheet still holds the exact C0 vector, `khbsDirtyAfterSave` is recorded and the original Đóng is clicked:
cmdExit_Click shows 0013 "Có muốn ghi lại thông tin thay đổi không?" (style 6: btn_1 Có, btn_2 Không, btn_3 Hủy
bỏ) and the driver answers **Không** (cmd_No: close without saving again; `khbsDiscardPromptAnswered`). The
reopened B1 still re-hashes the C0 file and requires the same bytes as at the save.

### Run 43369672859 (case 2): the actual cause

Both case-2 runs ended within a minute with `failureCategory: operation-not-established` (an
InvalidOperationException from a guard), stage left at `gtgt-original-declaration-save-success`, so neither the
dirty flag nor the post-save wait was reached. The C0 sheet watcher (ConfigureOriginalGtgtPeriod) keeps ticking
while Ghi and its observer run; for case 2 its next tick re-entered `PrepareKhbsOriginal`, whose guard throws once
Ghi was invoked (case 1 went straight to `StartOriginalAmendmentPriorSave`, which just returns). The sheet watcher
now returns once `amendmentPriorSaveInvoked` is set, before any C0 step. The wait for the acknowledged 0002 message
is also bounded in KHBS mode (60 s, `khbsPostSaveWaitMask` bit 64, `gtgt-amendment-khbs-post-save-timeout`), and the
post-save wait above stays bounded (30 s). The 0013 path stays as a fallback.

## Raw native output retention

After the run reaches `gtgt-amendment-khbs-inspected` **or** `gtgt-amendment-khbs-not-matched`, the probe
stages `RUNNER_TEMP/htkk-khbs-native-output/` (`khbs-native.xml`, byte-identical to HTKK's
`DataFiles/9999999997/reference-khbs-output/01GTGT-khbs.xml`, plus `provenance.json`,
format `htkk-khbs-native-output-staging-v1` with the bounded harness fields). The workflow step "Retain raw
native KHBS export privately" runs `scripts/publish-htkk-khbs-native-output.py`: it downloads the case's own
immutable private web input, validates the native file against it (HTKK service identity, fresh
ngayLapTKhai, exact synthetic identity leaves, attributes `id`/`xsi:nil` only, and every other text either a
value of that synthetic input or a bounded number/date/code shape), recomputes the whole-tree comparison
(same region bits as CompareKhbs, up to 16 mismatching leaf ordinals, agreement with the harness), and
publishes an orphan commit with `khbs-native.xml` + `manifest.json` (format
`htkk-khbs-native-output-reference-v1`) to the case's private output branch (`…-output-htkk582`) and an
immutable tag. It retains mismatches too; it never grants qualification. The web repository pins such bytes
under `tests/fixtures/htkk-khbs-native-reexport/` (index-driven test `tests/htkk-khbs-web-native-reexport.test.ts`).
