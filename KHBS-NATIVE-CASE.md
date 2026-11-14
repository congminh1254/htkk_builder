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

## Case 3: bổ sung lần 2 (`01GTGT-khbs-lan2-sale10-M10-2026`, adapter `01-gtgt-2.8.3-khbs-lan2`, amendmentOrder 2)

Static reading of 5.8.2: Tổng hợp KHBS (TongHopKhbsMoi) compares the sheet with `WinFnProcess.ReadSheet_LanTruoc`, which
loads `GetFileNameLoadKhbs` of the previous version; CheckPeriodKhbs (0x060004F6) builds `bs<N-1>_<lần đầu file>` for
lần N and refuses lần N without it (Message 0296). So the lần trước of lần 2 is the SAVED bổ sung lần 1 main sheet.

- Inputs: the web B2 file (`01GTGT-web.xml`, soLan 2, [32] 1.500.000) and the previous version `01GTGT-prior.xml`
  (exactly the case-1 web file, soLan 1, [32] 1.000.000; manifest `priorCaseId`, `priorBytes`, `priorXmlSha256`). Both are
  validated, staged and published together (`fetch-htkk-web-input.py names()/validate_prior`); the host gets
  `.web-prior.xml` + `.web-prior.sha256`.
- Round 1 = case 1 up to Tổng hợp KHBS on B1, importing the prior file; then the original **Ghi** ("Đã ghi dữ liệu thành
  công!", `khbsPriorSaveAcknowledged`), the file `bs1_01_GTGT_TT80_CQTQL10129_00_102026_283.xml` (`khbsPriorFileSaved`, hash
  re-checked before round 2) and the original **Đóng** (0013 answered Không only if the dirty flag stays set).
- Round 2 (`khbsRound` 2, `khbsRound2Opened`): menu again, Bổ sung with `txtLan` 2 and the fixed ngày lập; TTPeriodInfo SoLan
  2; the B2 main sheet must be the B1 vector or zero (`khbsOpenMainState` 3/1); import of the B2 file, Tổng hợp, export,
  whole tree (270 leaves). Other failures: `gtgt-amendment-khbs-prior-save-rejected` (`khbsPriorSaveMessageId`) and the
  bounded post-save timeout. Up to 9 menu clicks.
- Web side: `KHBS_01GTGT_LATER_RELEASED=false` until this case passes (bổ sung XML refused as the base; soLan > 1 labelled
  as a draft).

Run 43402236959: the lần-2 HTKK part passed (round 2 opened, khbsOpenMainState 3, whole tree 270 leaves), but retention
was refused as PROVENANCE: the KHBS publisher accepted `harnessOpenMainState` 0..2 only. Each case now accepts exactly its
own states (`htkk_khbs_web_cases.OPEN_MAIN_STATES`: case 1 → 1, case 2 → 1/2, case 3 → 1/3); anything else stays refused.

## 01-2/GTGT and 01-10/GTGT annexes in KHBS (static reading, not yet a case)

TongHopKhbsMoi inserts one `BKeHSo` per sheet listed by `GetDMToKhaiPhuLucKHBS` (MapMCT D1 nodes with ToSheetIndex 01-1)
and fills it from MapMCT: 01-10 (SheetIndex 7) has five STATIC items ((3)/(4) mua vào, (3)/(6) bán ra, [09] ct9), the same
path as the main sheet (CollectionStatic01_1_KHBS); 01-2 (SheetIndex 1) has three DYNAMIC items [10] [11] [12] per row of
`PLuc_01_2_GTGT/TenNhaMay` (CollectionDynamicHeader01_1_KHBS + CollectionDynamic01_1_KHBS): rows are matched with the
lần trước table by the composite key of TCTPath `path_20###ten_xa###ct08_tinh_ten###ct09_cqt_ten` (internal grid cells,
not XML leaves), and UpdateCtForDoiTac (LoaiChiTieu 4) writes ct3_ma = MCT, ct3_ten = Caption without its "[nn] - "
prefix and ct3_2_ten = FormatKey2(prefix, key). The 01-2 node [12] with ToSheetIndex 01 (TenTinhPath ct08_tinh_ten) drives
Muc_I.2 phân bổ (CollectionDetailSoThuePhaiNopTungTinh_01_KHBS, ~1.000 IL lines with CheckTruongHopDacBietPhanBo). Porting
these from the decompiled IL alone is not reliable (the key cells and the phân bổ branches depend on the grid binding), so
the next step is an oracle-capture case: C0 with one 01-2 plant imported from the web and saved, B1 with a changed
allocation imported and summarised; the raw HTKK export (retained even on mismatch) then fixes the port.

## Case 4: ORACLE CAPTURE with phụ lục 01-2/GTGT (`01GTGT-khbs-annex12-capture-M10-2026`, adapter `01-gtgt-2.8.3-khbs-annex12`)

Not a port check: its purpose is HTKK's own output for the annex. C0 is case 1's zero declaration without annex (proven);
the B1 period dialog selects phụ lục 01-2/GTGT (the original selector, `SelectOriginalAnnex12`) next to Bổ sung; the
original import loads the web B1 file, whose PLuc is exactly the two-plant 01-2 annex of the proven web case
`01GTGT-annex12-two-plants-nonzero-M10-2026` (validated by its own contract) followed by case 1's two KHBS fragments
(at capture time: main-sheet group only). The imported annex is checked read-only
(`InspectOriginalImportedAnnex12`) and its child head CQT displays are restored through the original combos exactly as the
proven annex web case does (`RestoreImportedAnnex12HeadAuthorities`, export 0016 otherwise). Then Tổng hợp KHBS, export and
the whole-tree comparison; the raw export is retained either way. The
output publisher accepts, for this case only, the public MapMCT 01-2 catalogue texts (sheet name, captions with and without
their "[nn] - " prefix) and ' - '-joined row keys whose every piece is a value of the input or a bounded shape; anything
else is still refused with a bounded leaf ordinal.

**Captured and ported.** Run 43428877607 retained HTKK's export (private branch
`gtgt-web-native-khbs-annex12-capture-output-htkk582`, then a mismatch as expected: the web file had no annex group).
HTKK wrote a second 01-1/KHBS hồ sơ group (`002601` "01-2/GTGT": one row per changed DiaBanPhanBo cell, items [11] then
[12], keyed "plant - ward - province - CQT", [12] unrounded so `tongCong_7` adds the binary64 values) and Muc_I.2
(`BKePLuc` `002601`, one row per plant/location with its Σ[12]). The web producer now writes exactly that (htkk_web
`lib/htkk-gtgt01-khbs-annex12.ts`; the raw bytes are pinned byte-identical there and re-exported equal), so the contract
`ROWS_ANNEX12_CAPTURE` is the full ported fragment (397 rows, 345 fragment leaves) and the whole tree must now MATCH:
504 compared leaves (89 annex + 70 main + 345 KHBS), `gtgt-amendment-khbs-inspected`. Still non-gating: the web keeps
every bổ sung with an annex refused (`KHBS_01GTGT_ANNEX_RELEASED=false`) until a changed-allocation case exists.

Run 43437157891 confirmed the port (stage `gtgt-amendment-khbs-inspected`, `khbsTreeMatched`, mask 0, 504 leaves, published
with `allTaxValuesMatched` true, same native bytes) but the probe still refused it: its common period predicate required
`periodNoAnnexMatched` for every KHBS case, while this case's B1 dialog selects 01-2 (`periodAnnex12Matched`). The predicate
now takes `periodAnnex12Matched -and -not periodNoAnnexMatched` for this case only; the other KHBS cases are unchanged.
Replaying that run's own result through the predicate region gives not-matched before and matched after the change.

## Case 5: ORACLE CAPTURE of a changed allocation, bổ sung lần 2 (`01GTGT-khbs-annex12-lan2-changed-M10-2026`, adapter `01-gtgt-2.8.3-khbs-annex12-lan2`)

Not a port check. It combines the two proven flows: C0 is case 1's zero declaration without annex; round 1 is case 4's B1
(01-2 selected in the period dialog, the capture case's exact web file imported as the staged previous version, the annex
checked read-only, head CQTs restored, Tổng hợp KHBS) saved with Ghi and closed exactly as case 3 does
(`bs1_…_283.xml`); round 2 opens B2 with 01-2 selected again (if HTKK already keeps 01-2 selected from the saved B1 it is only
observed, never clicked: `annex12SelectionActionCount` 0), imports the web B2 file, checks its annex (plant 1 at
40,00/60,00, plant 2 unchanged), restores the head CQTs, summarises, exports and compares the whole tree (465 leaves:
89 annex + 70 main + 306 KHBS). The B2 main sheet opens on the saved B1 vector (`khbsOpenMainState` 3) and raises [32] to
1.500.000 as case 3. The changed annex is a contract **variant** (`htkk_annex12_web_cases.VARIANTS`), not a native annex
case. Automation limit 210 s.

**Captured and ported.** Run 43454661870 (round 2 opened, 01-2 selected with one click: HTKK does not keep it selected for
B2; head CQTs restored; export 23077 bytes) retained HTKK's output; it differed from the web's first static reading
(k-th row of a key against the k-th previous row). HTKK compares every changed DiaBanPhanBo row with the FIRST previous row
of the same key; all rows of a plant share the key here, so plant 1's 60,00 is against 33,33 and plant 2's two unchanged
25,00 rows against its 50,00 row (four [11] and four [12] rows), `tongCong_7` 50.001 and Muc_I.2 stays the empty template
because no plant's Σ[12] changes. The web producer now writes exactly that (htkk_web pins the raw bytes byte-identical and
re-exports them equal), so `ROWS_ANNEX12_LAN2` is the ported fragment (355 rows, 306 fragment leaves) and the tree must
match. `annex12InputPercentagesMatched` belongs to `gtgt-annex12-input-inspect` (typed 50/50/100 inputs) and is never set
in this mode; the KHBS annex check is `annex12WebImportSheetMatched` (40/60 in round 2), which held.

## Cases 6-9: ORACLE CAPTURES of the wider 01-2 scope, bổ sung lần 2 (adapter `01-gtgt-2.8.3-khbs-annex12-lan2`)

Not port checks (non-gating, `releaseGate` false). Exactly case 5's two rounds: round 1 imports, summarises and saves case 4's
exact B1 file (two plants, one place each); round 2 opens B2, selects 01-2, imports the web B2 file, checks its annex,
restores the head CQTs, summarises, exports and compares the whole tree. Main sheet as case 5 ([32] 1.500.000). Each B2
annex is a contract **variant** (`htkk_annex12_web_cases.VARIANTS`), never a native annex case:

| Case | B2 annex (vs the capture B1) | Leaves (annex + main + KHBS) |
| --- | --- | --- |
| `01GTGT-khbs-annex12-lan2-add-plant-M10-2026` | third plant `99996` ([10] 5, two rows 60,00/40,00 at the plants' place); 7 rows | 527 (125 + 70 + 332) |
| `01GTGT-khbs-annex12-lan2-remove-plant-M10-2026` | plant 2 removed; plant 1 unchanged | 362 (38 + 70 + 254) |
| `01GTGT-khbs-annex12-lan2-two-places-M10-2026` | plant 2's rows 2-3 at a second place: Xã Phúc Lộc `10131091`, Thuế cơ sở 25 Thành phố Hà Nội `10131` (same tỉnh, head CQT `10100`) | 478 (89 + 70 + 319) |
| `01GTGT-khbs-annex12-lan2-ct10-M10-2026` | plant 2's [10] 3 -> 4 (its [12] 1,5/0,75/0,75 -> 2/1/1) | 452 (89 + 70 + 293) |

The web file's 01-2 hồ sơ group and Muc_I.2 are htkk_web's STATIC reading of HTKK 5.8.2 (`computeKhbsAnnex12Wide`, read
from frmWinToKhai.CollectionDynamic01_1_KHBS and CollectionDetailSoThuePhaiNopTungTinh_01_KHBS): pass 1 over the current rows
(each against the first previous row of its key, written when the two values differ as numbers), pass 2 over the previous
rows (skipped when the key already has a row for that item; else compared with the only current row of the key, or 0), and a
Muc_I.2 row for every place whose Σ[12] changed, removed places included. A mismatch (`gtgt-amendment-khbs-not-matched`) is
therefore possible; the raw export is retained to port HTKK's output. The driver checks the B2 annex in round 2 per case
(`KhbsAnnexWideRound2`: names, codes, [10], percentages, types and each row's ward); the head-CQT restoration selects each
row's own local CQT (`Annex12WardCqtName`; only the two fixed wards are accepted) and handles up to seven rows
(`Annex12MaxRestoredRows`; `annex12WebHeadAuthorityRepairCount` at most 4 × 7 = 28). Automation limit 240 s (case 5 keeps
210 s). Cases 6-9 are the evidence the htkk_web gate `KHBS_01GTGT_ANNEX_WIDE_RELEASED` waits for.

**Results (builder 44daec1, web 6312552).** add-plant (run 43549118061), remove-plant (run 43549120429) and two-places (run
43549123678) matched the whole tree; htkk_web releases them (`KHBS_01GTGT_ANNEX_WIDE_RELEASED`). ct10 (run 43549126253)
differed only at leaves 419/420: ct06/ct7 of plant 2's first [12] row (1,5 -> 2, shown "2" -> "2") are "1" in HTKK, the web
wrote "0" (round half to even). HTKK wrote that row, confirming the numeric (not displayed) difference rule; its two −0,5 rows
are "0" and the remove-plant −1,5 row is "−2". htkk_web now writes the displayed text as observed (`displayRound`), so
`ROWS_ANNEX12_CT10` carries "1"/"1" there and the case is expected to match on its next run; the [10] change stays behind
`KHBS_01GTGT_ANNEX_CT10_RELEASED` until it does.

## Cases 10-11: captures of the released verified scope's two possible deviations (non-gating)

Same two rounds and B1 as cases 5-9.

| Case | B2 annex (vs the capture B1) | Web file | Leaves |
| --- | --- | --- | --- |
| `01GTGT-khbs-annex12-lan2-equal-rows-M10-2026` | plant 1 at 40/60; plant 2 at two EQUAL rows 50,00/50,00 (row 3 dropped) | wide reading: pass 2 writes plant 2 "50,00 -> 0,00" and [12] "2" -> "0" (no single current row of the key) | 424 (74 + 70 + 280) |
| `01GTGT-khbs-annex12-lan2-display-same-M10-2026` | plant 1 at 35/65 (first [12] 2,3331 -> 2,45, shown "2" both) | the RELEASED verified computation, which omits that row; the static reading and run 43549126253 say HTKK writes it | 452 (89 + 70 + 293) |

Either outcome is retained raw; the released verified scope changes only after HTKK has decided.

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
