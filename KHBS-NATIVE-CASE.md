# Native case design: 01/GTGT kê khai bổ sung lần 1 (D1, KHBS)

Status (cases 12-13, quarterly, matched; cases 14-15, display rounding, differed and are ported; cases 16, 19, 20 matched, 18 ported, 17 to rerun; see below): case 1 `01GTGT-khbs-zero-to-sale10-M10-2026` **passed** on Windows (release run 43358377013:
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
| `01GTGT-khbs-annex12-lan2-display-same-M10-2026` | plant 1 at 35/65 (first [12] 2,3331 -> 2,45, shown "2" both) | since run 43555407694: HTKK's output (the [12] row "2" -> "2", ct06/ct7 0 included) | 465 (89 + 70 + 306) |

Either outcome is retained raw; the released verified scope changes only after HTKK has decided.

**Results (builder 8dd4a53, web 1585a559).** ct10 matched (run 43555403183, 452 leaves) after the displayRound port;
equal-rows matched (run 43555405226, 424 leaves), confirming pass 2 for equal duplicate rows. display-same differed
structurally (run 43555407694, mismatch mask 1, first difference 357): HTKK writes the [12] row whose value changes but
whose display does not (`[12] 2 -> 2`, ct06 0, ct7 0), which the released web computation omitted. htkk_web now uses the
same rules for every 01-2 amendment, so `ROWS_ANNEX12_DISPLAY_SAME` is HTKK's fragment (355 rows, 306 fragment leaves) and the
case is expected to match on its next run.

## Cases 12-13: QUARTERLY captures (non-gating; adapters `01-gtgt-2.8.3-khbs` / `-khbs-lan2`, period `quarter` `3/2026`)

htkk_web releases bổ sung for monthly AND quarterly 01/GTGT, but cases 1-11 are all monthly. Cases 12-13 are case 1 and case 3
on **quý 3/2026** (most small taxpayers file 01/GTGT quarterly). Static reading of the pinned 5.8.2 payload (nothing executed):

- `GeneralFunctions.GetHanNopToKhai` (TAX.HTKK.Business, KieuKy Q): quý 4 -> 30/01 of the next year, 3 -> 30/10, 2 -> 30/07,
  1 -> 01/05; then the DMNgayLe rows of the period's own KieuKy (only Q rows 30/04/2021 and 01/05/2021 exist) and Saturday +2 /
  Sunday +1. 30/10/2026 is a Friday, so the due date is 30/10/2026 (the law's 31/10 would move to 02/11; htkk_web follows HTKK).
- `GeneralFunctions.SoNgayNopCham` = ngày lập KHBS − hạn nộp in days (min 0): the fixed ngày lập 13/11/2026 gives **14** days.
  `CheckPeriodKhbs` (KieuKy not D) refuses only a date after today (0224) or after hạn nộp + 10 years (0507).
- `WinDoWorkEvent.GetFileNameBySheet`, D1, KieuKy Q, `TuThang` empty (GetPeriodInfo sets it only while mskTuThang is visible; the proven quý-4 web case exports an empty kyKKhaiTuThang): C0 file
  `01_GTGT_TT80_CQTQL10129_00_Q032026_283.xml` ("_Q" + String.Format("{0}{1}",Quy,Nam).PadLeft(6,'0')) and, for LoaiToKhai B,
  `bs1_01_GTGT_TT80_CQTQL10129_00_Q032026_283.xml` ("_Q0" + Quy + Nam). If HTKK names them otherwise, the run stops at
  `gtgt-amendment-prior-file-missing` (bounded), which is itself the finding.

| Case | Flow | Web file | Leaves |
| --- | --- | --- | --- |
| `01GTGT-khbs-zero-to-sale10-Q3-2026` (producer `khbs-q3-zero-to-sale10`) | case 1 on Q3/2026: zero C0 Ghi, B1 imports sale10 | ct10 100.000, ct3a_2 **14**, ct3b **420** (0,03% x 14 x 100.000) | 270 |
| `01GTGT-khbs-lan2-sale10-Q3-2026` (producer `khbs-q3-lan2-sale10`) | case 3 on Q3/2026: round 1 imports case 12's exact file, Ghi; round 2 [32] 1.500.000 | ct10 50.000, ct3a_2 14, ct3b **210** | 270 |

Driver: `KhbsQuarterCase()` selects `chkTKQuy` and `cbbQuy` "3" in the period dialog for C0, B1 and B2 (`QuarterPeriod()`,
`PeriodQuarter()`; the zero quý-4 web case keeps "4"), and TTPeriodInfo must read KieuKy Q, Quy 3 at the C0 sheet and at every
reopening (`amendmentOpenPeriodMatched`). Input privacy: the exact PLuc rows (the KHBS headers carry Q, 3/2026, 01/07/2026,
30/09/2026), then the main header projected in memory onto the M10 baseline (`Q3_PERIOD`) and the unchanged no-annex allowlist.
The case-13 prior must be case 12's file (kyKKhai 3/2026). Automation limit 150 s / 175 s (as cases 1 / 3).

## Cases 14-15: captures of the ct06/ct7 display rounding (non-gating; adapters `-khbs-annex12` / `-khbs-annex12-lan2`)

htkk_web's `displayRound` is fitted to three observed points only (+0,5 -> "1", −0,5 -> "0", −1,5 -> "−2"). These cases add
+1,5, +2,5 and −2,5 (and a .5 annex-group total), all exact in binary64:

| Case | Flow | Annex | Web writes ([12] ct04 -> ct05, ct06) | Leaves |
| --- | --- | --- | --- | --- |
| `01GTGT-khbs-annex12-round-M10-2026` (producer `khbs-annex12-round`) | case 4's (C0 without annex, B1 adds 01-2) | `htkk_annex12_web_cases.ROUND_B1_VARIANT`: plant 1 [10] 3, plant 2 [10] 5, each two rows 50,00/50,00 | 0 -> 2, "2" (+1,5) twice; 0 -> 2, "3" (+2,5) twice; tongCong_7 100008 | 463 (74 + 70 + 319) |
| `01GTGT-khbs-annex12-lan2-round-M10-2026` (producer `khbs-annex12-lan2-round`) | case 5's two rounds, round 1 imports case 14's exact file | `ROUND_B2_VARIANT`: plant 1 [10] 8 (rows 4/4), plant 2 removed | 2 -> 4, "3" (+2,5) twice; 2 -> 0, "-2" (−2,5, pass 2); tongCong_7 50002 | 388 (38 + 70 + 280) |

They also pin two other .5 displays the web reads statically: the 01-2 XML `ct12` of 2,5 (web "3") and the 01-1/KHBS ct04/ct05
of 2,5 (web roundEven "2"). Driver: `KhbsAnnexRound` gives the expected imported annex per round (names, codes, [10],
percentages, types, the fixed ward); everything else is case 4's / case 5's flow. Automation limit 175 s / 240 s.

**Results (builder a960f8c, web 3c6ea8e3).** Case 12 (run 43591669543) and case 13 (run 43591672052) matched the whole tree
(270 leaves each): the quarterly period dialog, the static file names `…_Q032026_283.xml` / `bs1_…`, the 30/10/2026 due date
and 14 late days (ct3b 420 / 210) are as read. Case 14 (run 43591674509) differed only at leaves 442/455 and case 15 (run
43591676788) at 379/384, all in PL01_1_KHBS: ct06/ct7 were exactly as `displayRound` predicted (+1,5 "2", +2,5 "3", −2,5
"−2"), but HTKK shows the [12] ct04/ct05 of 2,5 as "3" (web wrote "2", round half to even) and the annex group tongCong_7
50.002,5 as "50003" (web "50002"). htkk_web now uses the same display rule for ct04/ct05, tongCong_7, Muc_I.2 ct7 and
tongCong_ct11; the raw exports are pinned there byte-identical and re-export equal, so `ROWS_ANNEX12_ROUND` /
`ROWS_ANNEX12_LAN2_ROUND` carry "3" / "3" / "50003" and both cases are expected to match on their next run.

## Cases 16-20: lần 1 on a lần đầu with 01-2, quý 3 with 01-2, negative display rounding (non-gating)

**Static reading (HTKK.exe `331ed84a…f98a`, dnfile only, nothing executed).** `TongHopKhbsMoi` reads the previous version of
EACH annex sheet listed by `GetDMToKhaiPhuLucKHBS`, 01-2 included, through `WinFnProcess.ReadSheet_LanTruoc(sheet)`, which for
D1 calls `WinDoWorkEvent.GetFileNameLoadKhbs(TTPeriodInfo, DataFile, DataFiles\<MST>\, 0)`: SoLan "1" gives the lần đầu name
(`01_GTGT_TT80_CQTQL10129_00_102026_283.xml`), SoLan N the `bs<N-1>_` name; the current lần's own `bs<N>_` file is used only when
the last argument is non-zero (IL 0xd38-0xd56 and 0x12ff-0x131d), never here. `GetDetailSheetInfo` then reads the sheet from that
file the same way. No method of `TongHopKhbsMoi`, `CollectionDynamicHeader01_1_KHBS`, `CollectionDynamic01_1_KHBS`,
`CollectionDetailSoThuePhaiNopTungTinh_01_KHBS`, `DanhDauNeuCoPhanBo` or the `GeneralFunctions` / `WinSpreadProcess` /
`WinFnProcess` helpers they call reads `SoLan` or `LoaiToKhai`. So the 01-2 hồ sơ group and Muc_I.2 of lần 1 against a lần đầu
with 01-2 are computed exactly as lần N against lần N-1; htkk_web's producer files for cases 16-17 equal those of cases 5-6
except `soLan` (`ROWS_ANNEX12_LAN1_*`), and htkk_web keeps the scope behind `KHBS_01GTGT_ANNEX_LAN1_EXISTING_RELEASED=false`.

| Case | Flow | Annex (B1 / B2) | Web writes | Leaves |
| --- | --- | --- | --- | --- |
| `01GTGT-khbs-annex12-lan1-ct11-M10-2026` (`khbs-annex12-lan1-ct11`) | C0 imports the staged lần đầu (the proven annex web case `01GTGT-annex12-two-plants-nonzero-M10-2026`'s own file, `priorCaseId`), 01-2 selected, head CQTs restored, Ghi; B1 as case 4 | `TWO_PLANTS_CHANGED_VARIANT` (plant 1 at 40/60), main [32] 1.500.000 | case 5's fragments, soLan 1 | 465 |
| `01GTGT-khbs-annex12-lan1-add-plant-M10-2026` (`khbs-annex12-lan1-add-plant`) | as case 16 | `ADD_PLANT_VARIANT` (third plant 99996) | case 6's fragments, soLan 1 | 527 |
| `01GTGT-khbs-annex12-capture-Q3-2026` (`khbs-q3-annex12-capture`) | case 4 on quý 3/2026 (zero C0, `…_Q032026_283.xml`) | the proven two-plant annex | 14 late days, ct3b 0 (HTKK, run 43642289420; see results) | 504 |
| `01GTGT-khbs-annex12-round3-M10-2026` (`khbs-annex12-round3`) | case 14's | `ROUND3_B1_VARIANT`: [10] 7 / 9 / 7, rows 50/50 | [12] 0 -> 4 "4", 0 -> 5 "5" (+3,5 / +4,5) | 564 |
| `01GTGT-khbs-annex12-lan2-neg-round-M10-2026` (`khbs-annex12-lan2-neg-round`) | case 15's, round 1 imports case 19's exact file | `NEG_ROUND_B2_VARIANT`: plant 1 [10] 6 (rows 3/3), plants 2-3 removed | ct06/ct7 "0" (−0,5) twice, "-4" (−4,5), "-4" (−3,5); tongCong_7 49991 | 427 |

Driver for cases 16-17 (`KhbsLan1ExistingCase`): the C0 period dialog selects 01-2 (`SelectOriginalAnnex12`); once the C0 sheet
is matched, `PrepareKhbsOriginalImport` hands C0 to the phases `c0-import-ready` -> `c0-import-result` (original "Nhập từ XML" of
`.web-prior.xml`, "Nhập dữ liệu từ XML thành công.", FileNameLoading = the prior, LoaiToKhai still C; `khbsPriorImportSucceeded`)
-> `c0-annex-restore` (`InspectOriginalImportedAnnex12` with the proven two-plant annex, `RestoreImportedAnnex12HeadAuthorities`)
-> `c0-main-ready` (main sheet = `KhbsSale10B1`, import state reset) -> the original Ghi (`StartOriginalAmendmentPriorSave`, which
then requires 01-2 selected and the vector; the saved file must carry the vector, `khbsSavedMoneyMatched`). The C0 sheet watcher
stands aside once the import began. B1 reopens with 01-2 selected again (or observed if HTKK keeps it), opens on the C0 vector (3)
or zero (1), and runs case 4's B1 (import, annex check: plant 1 at 40/60 or case 6's annex, restore, Tổng hợp, export, compare).
A dirty flag left after the C0 Ghi takes case 2's bounded discard path. Automation limit 240 s (cases 16-17, 20), 175 s (18-19).
The previous version of cases 16-17 is staged like a lần-2 prior (`01GTGT-prior.xml` -> `.web-prior.xml`) and validated by the
annex web case's own contract.

What each run decides: cases 16-17 match -> htkk_web may open `KHBS_01GTGT_ANNEX_LAN1_EXISTING_RELEASED`; case 18 matches ->
`KHBS_01GTGT_ANNEX_QUARTER_RELEASED` (late interest with 01-2 for a quarter); case 20's "-4" for −4,5 confirms the web's
round-half-to-even negative branch (away from zero would give "-5"), "-4" for −3,5 rules out truncation toward zero.

**Results (builder 23b7abf, web 18e72dc9).** Case 16 (run 43642284685) matched the whole tree (465 leaves): the C0 import flow works
and lần 1 against the annexed lần đầu is exactly case 5's computation. Cases 19 (run 43642291803, 564 leaves) and 20 (run
43642294376, 427 leaves) matched: −4,5 -> "-4", −3,5 -> "-4", −0,5 -> "0" confirm htkk_web's negative `displayRound` branch. Case
17 failed before any tax step (profile-wait-timeout) and reruns with the next release. Case 18 (run 43642289420) differed only at
leaf 213, PL01_KHBS Muc_3 ct3b: HTKK wrote 0 where the web wrote 420 (ct3a_1 and 14 days as the web).
`TinhSoTienPhatNopCham` copies the FIXED cell AA38 of 01-KHBS, whose formula `0.03/100*P71*O49` names fixed cells (P71 the days
cell, O49 Σ Muc_I.1 of `KHBS_01_TT80_DIA_BAN_283.xls`); the second Muc_I.2 row is inserted above row 71, so P71 is then an empty
template cell. htkk_web ports it (`khbsAnnex12LateInterest`: 2-11 Muc_I.2 rows give 0) and `ROWS_ANNEX12_CAPTURE_Q3` now carries
ct3b 0; the raw exports are pinned in htkk_web byte-identical and the producer reproduces every leaf of all four.

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

## 01/NTNN (I9) and 01/NTNN, NCCNN (Y8): mode `declaration-amendment-khbs-inspect` (observation cases)

htkk_web (docs/KE-KHAI-BO-SUNG-01-NTNN.md, `lib/htkk-ntnn01-khbs.ts`, hidden behind `KHBS_01NTNN_*_RELEASED=false`) ports the
KHBS of both menus statically from HTKK 5.8.2: KieuKHBS 3 like D1, but every MapMCT item is DYNAMIC (LoaiChiTieu 4), so the
01-1/KHBS rows come from `CollectionDynamic01_1_KHBS` per table row (row key = the TCTPath columns joined with " - "), tiểu mục
= `MapMCT_TieuMuc` MaTieuMuc (I9 1701/1052; Y8 part II 1052 for both GTGT and TNDN/TNCN), templates `KHBS_TT80_251.xls` /
`KHBS_TT80_309.xls` (same formulas as D1, AA38 included), output `KHBS_01_TT80_xml.xml` / `KHBS_01_1_TT80_xml.xml`, schemas
`KHBS_01_NTNN_TT80_251.xsd` / `KHBS_01_NTNN_NCCNN_TT89_309.xsd`.

`scripts/htkk_ntnn_khbs_web_cases.py` is the reviewed INPUT half of six cases (sizes and SHA-256 of every staged file pinned,
bounded structural checks; the reviewed bytes themselves in `htkk_ntnn_khbs_web_inputs.json`; `test_ntnn_khbs_web_cases.py`).
The six cases are registered in `htkk-native-cases.json` (adapters `01-ntnn-tt80-2.5.1-khbs`, `01-ntnn-tt80-2.5.1-khbs-lan2`,
`01-ntnn-nccnn-tt89-3.0.9-khbs`, `01-ntnn-nccnn-tt89-3.0.9-khbs-lan2`; driver `declaration-amendment-khbs-inspect`, HTKK 5.8.2) with `releaseGate: false`: they are
observation cases, dispatched by the cohort but never in `GATE_CASES`, so a mismatch neither blocks a release nor turns Assess red.

| Case | Menu | Files | Web leaf target (no TTinDVu) |
| --- | --- | --- | --- |
| `01NTNN-khbs-grossup-lan1-M09-2026` | I9 | original, web | 216 |
| `01NTNN-khbs-lan2-M09-2026` | I9 | original, prior (= the case above's web file), web | 174 |
| `01NTNN-khbs-decrease-M09-2026` | I9 | original, web | 174 |
| `01NTNN-NCCNN-khbs-part1-M10-2026` | Y8 | original, web | 265 |
| `01NTNN-NCCNN-khbs-part2-M10-2026` | Y8 | original, web | 249 |
| `01NTNN-NCCNN-khbs-lan2-M10-2026` | Y8 | original, prior (= `01NTNN-NCCNN-khbs-part1-M10-2026`'s web file), web | 223 |

Driver (`scripts/HtkkDeclarationKhbs.cs` on the declaration driver; step mask bits listed there):

1. Declaration flow up to the C0 sheet (menu chain 101 → 101_8 → I9/Y8, period month 09/2026 or 10/2026 with Chính thức).
   I9: original "Nhập từ XML" of `.web-original.xml` (I9 keeps its table on import, release 238). Y8: the tables are reset on
   import (`LockUnlock` deleteData, release 238), so C0 is TYPED with an entry plan as `01NTNN-NCCNN-entry-M10-2026` does
   (part I: M6; part II: M8, rows of NCCNN and CNKCT).
2. Original Ghi ("Đã ghi dữ liệu thành công!"), check the saved C0 file in `DataFiles\9999999997`, original Đóng (0013 → Không
   if the dirty flag stays set), as the D1 KHBS driver does.
3. Menu again; period dialog: OptBosung, txtLan (2 in round 2 of lần 2), `mskNgayLapKHBS` 13/11/2026, Đồng ý; TTPeriodInfo
   LoaiToKhai B, SoLan, NgayLapKHBS; sheets 01-KHBS and 01-1/KHBS present.
4. I9: original import of the bổ sung file (lần 2 round 1: `.web-prior.xml`, then Tổng hợp KHBS, Ghi `bs1_…`, Đóng, round 2).
   Y8: the changed cells typed (the B sheet may open reset; type every planned cell). Y8 lần 2 (phần I): round 1 types the
   lần 1 rows of `01NTNN-NCCNN-khbs-part1-M10-2026` (Tổng hợp KHBS, Ghi, Đóng), round 2 the lần 2 rows (AZ 240.000.000); the
   staged `.web-prior.xml` is verified against its pin but never imported.
5. Original "Tổng hợp KHBS" (0222), original export (schema pinned: the two KHBS XSDs above), whole-tree comparison
   with the web B file (C# leaf counts = targets above + 4 service leaves); the shared export readiness gate applies.

Probe (`probe-htkk-windows.ps1`): writes the profile-save permit for this mode like every mode whose registry `permit` is
`profile-save` (test_native_automation_registry pins the probe list to the registry); stages `declaration-original.xml` as `<host>.web-original.xml/.sha256` and, for the lần-2 case,
`declaration-prior.xml` as `<host>.web-prior.xml/.sha256` (manifest `originalXmlSha256`/`priorXmlSha256`); limit 420 s (above the
driver's own 400 s; release b352279 waited 300 s for a permit the probe never wrote, runs 43671647120-43671657019); success = stage `declaration-khbs-inspected`, the last round (1, or 2), step mask 1591 (lần 2: 1791), entry (Y8) or
import (I9) flags, export flags, KHBS XSD and whole tree matched. On `declaration-khbs-inspected` or
`declaration-export-not-matched` the original export is staged and `publish-htkk-declaration-native-output.py` retains it
(inputMode `khbs-web-xml-import-reexport` / `khbs-original-entry-export`) after `htkk_ntnn_khbs_web_cases.validate_native_output`:
HTKK service identity, fresh ngayLapTKhai, maTKhai/version, loaiTKhai B and soLan of the case, the synthetic NNT, and every text a
leaf text of the case's own reviewed files or the synthetic profile. The comparison is recomputed against the reviewed web file.

Cohort c741595 (Y8 runs 43742154547, 43742157400): `declarationKhbsEntryLengths` high byte 0x33: attempt A ({HOME} + first
character) and C (select all, first character doubled) both left another text, B was skipped. Read: {HOME} does not put the
caret at the start of this editor, and a second typing keeps every key, so only the very first key typed into the freshly
opened editor of a bổ sung round is lost. HTKK 5.8.2 itself does not drop it (static read: frmWinToKhai.winFpSpread_EditModeOn
adds winFpSpread_KeyPress, which only turns Enter into Tab and checks date-type keys; WinDoWorkEvent.KeyPress finds no KeyPress
on Ntnn01TT89Nckt309). Each bổ sung entry (text, number, date text) now first types one space by the value's own keyboard path
and erases it with BACKSPACE; the editor must be empty again; the fallback is one select-all retype. High byte bits: 4 space
lost, 8 space landed and erased, 16 not empty after, 1/2/3 the fallback outcome.

Cohort 9d45beb (Y8 runs 43733503058, 43733506098): shape 23305 again, no 32768: {HOME} and the first character (SendKeys) did
not take. The repair now makes up to three bounded keyboard attempts and records each outcome in the high byte of
`declarationKhbsEntryLengths` (2 bits each: 1 took, 2 still without the first character, 3 other): A {HOME} + SendKeys,
B {HOME} + KEYEVENTF_UNICODE, C select all and type the first character twice then the rest.

Cohort 455ecc7 (Y8 runs 43727202330, 43727204841): shape 23305: the FIRST character was missing and a select-all retype lost
it again. A bổ sung round now repairs only that: with the editor holding the typed text minus its first character, {HOME} and
the first character are typed (same keyboard path), for text, number and date-text entries; 16384/32768 record it. (Importing
the B file instead is not available for Y8: its original import resets the tables, release 238.)

Cohort f3b64d4 (Y8 runs 43705699385, 43705701482): round-1 entry 0 still code 12 with `declarationKhbsEntryShape` 2825 (cell
empty, editor = cell when opened, focus kept, own foreground) and lengths 30 / 34 for 31- / 35-character texts: one character of
the planned text did not land. A bổ sung round now selects with {END}+{HOME} only over a non-empty cell, lets the editor settle
(5 UI turns) before the first key and retypes once over a short result (shape bits 4096/8192 first/last character missing,
16384 retyped, 32768 retype took).

Cohort 1019e5f: `01NTNN-khbs-decrease-M09-2026` matched the whole tree (run 43686715380, retained). The other four:
- Gross-up (run 43686711369): exported and retained; one leaf differed, `PL01_KHBS/.../Muc_3/ct3b` (HTKK 7.778, web 0). HTKK
  computes AA38 over ct10 with two Muc_I.1 rows too; the web was fixed to HTKK and the pins of the gross-up web file and of the
  lần-2 prior (the same file) changed with it.
- Lần 2 (run 43686713666, and the 05/KK lần 2): every result was refused once round 2 clicked the menu a fourth time;
  `menuClickCount` allowed 3 for this mode. It now allows 9 (three menu traversals), as for `gtgt-amendment-khbs-inspect`.
- Y8 part1/part2 (runs 43686717364, 43686719047): round 1 failed at entry 0 (code 12): the B sheet opens with the saved C0
  values and the planned text was typed over a cell that already held it. A bổ sung round now leaves a planned cell that
  already holds its planned value as HTKK loaded it (read only), selects with {END}+{HOME} before typing over any other, and
  resets the combo counter per round.

Cohort 1a6f600 (runs 43676048794, 43676050610, 43676052218, 43676054472, 43676056452): permit written, the seven profile
inputs typed and the original profile Ghi clicked; four cases then never showed a valid result past `original-save-invoking`
(no success message, no HEADER.xml), part1 stopped after `waiting-profile-close-ready`, and none showed the driver's own 400 s
timeout before the probe's 420 s. The logs cannot tell a stalled save from results the reader refused, so the next run reports
`guiReferenceResultReads` (refused reads after a valid one, age of the last write) and, in this mode only, the profile-save
wait every 2 s in `declarationUiWaitSeconds` / `declarationUiVisibleForms` / `declarationUiForegroundKind`.

Cohort cbff9e0 (runs 43681376802-43681386953, and the five 05/KK KHBS cases): about 816 refused reads after the last valid
result in every run. Cause: the reader's `webCaseId` allowlist (registry `resultFields.webCaseId.values`) had none of the ten
KHBS case ids, so every result written after `VerifyDeclarationWebInput` set the case id was refused; the probe kept the
last result from before it (`original-save-invoking` / `success-modal-acknowledged` / `waiting-profile-close-ready`,
whichever read came last). Offline, a result built by the helper itself (mono) right after that step fails exactly on that
line and passes once the ids are listed. The ids are now listed, a test pins the allowlist to every registered case, and
`guiReferenceResultReads` counts refused (`invalidAfterValid`) and absent (`missingAfterValid`) results apart.

What only these runs decide (web predictions in its golden): the text of the row key `ct3_2_ten` (dates dd/MM/yyyy, rates "5"),
`ct04`/`ct05` of amounts ("1.000.000"), ct3b 0 when Muc_I.1 has two rows (gross-up case: 24 late days), negative ct3b −7.200
(decrease case) and 3.311 (lần 2), and the Y8 part II tiểu mục 1052.

## 05/KK-TNCN (L7) and 05/KK-TNCN TT89 (Z8): mode `declaration-amendment-khbs-inspect` (observation cases)

htkk_web (docs/KE-KHAI-BO-SUNG-05-KK-TNCN.md, `lib/htkk-kk05-khbs.ts`, hidden behind `KHBS_05KK_*_RELEASED=false`) ports the
KHBS of both menus statically from HTKK 5.8.2: KieuKHBS 3, and both menus are in the menu list of `WinFnProcess.WinLoadFromFile`
and `WinDoWorkEvent.WinDoWorkGetExportSheetXML` that D1 is in, so the KHBS workbook is `KHBS_DIA_BAN_293.xls` / `_309.xls` (same
formulas as D1, AA38 included) and 01/KHBS is written with `KHBS_01_DIA_BAN_xml.xml` (Muc_I.2 with ma_Xa/ten_Xa). The main-sheet
items are static (`CollectionStatic01_1_KHBS`), tiểu mục 1001 for [29] (L7) / [42] (Z8); the 05-1/PBT-KK-TNCN items [10]…[14] are
dynamic (key MST - xã - tỉnh - CQT) and [14] feeds Muc_I.2 (`CollectionDetailSoThuePhaiNopTungTinh_01_KHBS`). Schemas
`KHBS_05_KK_TNCN_TT80_293.xsd` / `KHBS_05_KK_TNCN_TT89_309.xsd`.

`scripts/htkk_kk05_khbs_web_cases.py` holds the pins (sizes and SHA-256 of every staged file, never the files) and per-case
settings of five cases; `htkk_ntnn_khbs_web_cases.py` merges them, so fetch, publishers and the probe lists check them exactly like
the 01/NTNN cases (`test_kk05_khbs_web_cases.py`). Registered in `htkk-native-cases.json` (adapters `05-kk-tncn-2.9.3-khbs`,
`-khbs-lan2`, `-khbs-pbt`, `05-kk-tncn-tt89-3.0.9-khbs`; HTKK 5.8.2) with `releaseGate: false`.

| Case | Menu | Files | Web leaf target (no TTinDVu) |
| --- | --- | --- | --- |
| `05KK-khbs-increase-Q3-2026` | L7 | original, web | 213 |
| `05KK-khbs-lan2-Q3-2026` | L7 | original, prior (= the case above's web file), web | 161 |
| `05KK-khbs-decrease-Q3-2026` | L7 | original, web | 161 |
| `05KK-TT89-khbs-increase-Q4-2026` | Z8 | original, web | 174 |
| `05KK-PBT-khbs-Q3-2026` | L7 + 05-1/PBT | original, web | 230 |

Driver: the rounds of the 01/NTNN cases with the plans of `05KK-withheld-Q3-2026` / `05KK-TT89-withheld-Q4-2026` (menu 101 →
101_11 → L7/Z8, quý 3/2026 or quý 4/2026), every round imported. The PBT case ticks 05-1/PBT-KK-TNCN in the period dialog and, after
EACH import (C0 and bổ sung), chooses Thuế tỉnh/CCT and CQT quản lý again with the reviewed combo edits of
`05KK-PBT-two-provinces-Q3-2026` (`HtkkDeclarationCasePlans.KhbsImportTick`; path_15 has no XML leaf, Header B37 would refuse Ghi
and Kết xuất); the tick state is reset in `BeginDeclarationKhbsRound`. Probe: the success
predicate of the 01/NTNN cases (limit 420 s, as for them), with the tick flags for `$HtkkNtnnKhbsTickCases`; raw export retained with inputMode
`khbs-web-xml-import-reexport` or `khbs-web-xml-import-tick-reexport`.

What only these runs decide (web predictions in its golden): hạn nộp quý 30/10/2026 (14 late days, ct3b 4.200 / −4.200 / 2.100)
and Z8 quý 4/2026 30/01/2027 moved to 01/02/2027 (0 days, ct3a_1 still written); the 05-1/PBT hồ sơ group 000101 and its key text;
Muc_I.2 with ct04 = Thuế tỉnh/CCT of the row (path_24, saved by HTKK in its Sections file) and ct3 = the unit's MST; tongCong_7
adding the [14] row; ct3b kept with one Muc_I.2 row.

Cohort 1019e5f (HTKK 5.8.2): `05KK-khbs-increase-Q3-2026` (run 43686728548, 213 leaves), `05KK-khbs-decrease-Q3-2026` (run 43686732231,
161) and `05KK-TT89-khbs-increase-Q4-2026` (run 43686734447, 174) matched the whole tree. `05KK-PBT-khbs-Q3-2026` (run 43686736338)
got through every round, KhbsImportTick included, and differed only in leaves 141/142: HTKK writes Muc_I.2 `ct04_ma`/`ct04_ten`
EMPTY (the web had put the row's Thuế tỉnh/CCT there). htkk_web now writes them empty (its raw export reproduces every leaf);
the pinned web file of the PBT case changed accordingly (7460 bytes, f27e9cf3…b806; leaf target unchanged). `05KK-khbs-lan2-Q3-2026`
(run 43686730343) stopped in round 2 at `declaration-menu-click` (step mask 767, menuClickCount 3, every later result refused, none
missing): the reader caps `menuClickCount` at 3 for this mode while a third round clicks again, the shared lần-2 path of the
01/NTNN lần-2 case.


`05KK-khbs-increase-M03-2026` (observation, adapter `05-kk-tncn-2.9.3-khbs` now also takes month 03/2026): the increase case on L7
kỳ tháng 3/2026 (HTKK takes monthly 05/KK-TNCN until tháng 3/2026), its own period in the contract (`period_of`), plan month
03/2026 (`chkTkhaiThang`, KieuKy 19). Web prediction: hạn 20/04/2026, 207 late days, ct3b 62.100; 213 leaves. htkk_web released
KHBS 05/KK lần 1 without 05-1/PBT for L7 kỳ quý and Z8 only (runs 43686728548, 43686732231, 43686734447); kỳ tháng waits for this case.

## 01/CNKD TT50/2026 (U5 3.1.0): mode `declaration-amendment-khbs-inspect` (observation cases)

htkk_web (docs/KE-KHAI-BO-SUNG-01-CNKD.md, `lib/htkk-cnkd01-khbs.ts`, hidden behind `KHBS_01CNKD_*_RELEASED=false`) read the
KHBS of U5 statically from HTKK 5.8.2: Menu.xml has `KieuKHBS=""` (VersionKHBS 3.1.0, sheet KHBS `Active="0"`), MapMCT.xml and
MapMCT_TieuMuc.xml have no U5 map, and `Validate/KHBS_01_CNKD_HKD_TT50_310.xsd` is the same bytes as `01_CNKD_HKD_TT50_310.xsd`
(no `PL01_KHBS`). `frmWinToKhai.LoadButton` shows `btnTongHopKHBS` only for LoaiToKhai B with a non-empty KieuKHBS, and
`frmHTKKPeriod.UpdatePeriodByVerSion` hides `pnVT2_PhuLucKeKhai` for a Bổ sung with an empty KieuKHBS. So the web bổ sung is the
whole declaration with loaiTKhai B and its lần: no 01/KHBS, no 01-1/KHBS, no tiền chậm nộp.

`scripts/htkk_cnkd_khbs_web_cases.py` holds the pins (sizes and SHA-256, never the files) and per-case settings of four cases, with
`khbsParts` empty (the merged contract `htkk_ntnn_khbs_web_cases.py` refuses a KHBS fragment in their B files and expects one in every
other KHBS case; `test_cnkd_khbs_web_cases.py`). Registered in `htkk-native-cases.json` (adapters `01-cnkd-hkd-3.1.0-khbs`,
`-khbs-lan2`, `-khbs-pl01`; HTKK 5.8.2, `summary: false`) with `releaseGate: false`.

| Case | Files | Web leaf target (no TTinDVu) |
| --- | --- | --- |
| `01CNKD-khbs-increase-Q3-2026` (group 01 300tr → 350tr) | original, web | 271 |
| `01CNKD-khbs-decrease-Q3-2026` (group 04 200tr → 150tr) | original, web | 271 |
| `01CNKD-khbs-lan2-Q3-2026` (lần 2 on the increase case, 350tr → 380tr) | original, prior (= the increase web file), web | 271 |
| `01CNKD-PL01-khbs-Q3-2026` (PL 01 NQ 43 on both, unticked group 02 150tr → 160tr) | original, web | 295 |

Driver: the rounds of the other KHBS cases with the plan of `01CNKD-TT50-310-pl01-three-groups-Q3-2026` (menu 101 → 101_37 → U5,
quý 3/2026; with PL 01 for the PL 01 case, without otherwise), schema `Validate/KHBS_01_CNKD_HKD_TT50_310.xsd`, every round imported.
`HtkkDeclarationCasePlans.KhbsSummary` is false for these cases: after the bổ sung input the round goes straight to Ghi (intermediate)
or Kết xuất (last) without clicking anything, and step bit 2048 records that `btnTongHopKHBS` was not shown (the probe expects 2048
instead of 32, `$HtkkNtnnKhbsNoSummaryCases`). In a Bổ sung period dialog the phụ lục list is hidden for U5: `SelectDeclarationAnnexes`
clicks nothing there, sets `declarationAnnexListMask` bit 4096 and leaves the annexes to the saved previous version (the imported
sheets are still checked). The PL 01 case makes the giảm thuế ticks again after EACH import with the reviewed tick plan of the lần
đầu PL 01 case (`KhbsImportTick`; rows 01 and 04 keep 300tr / 200tr in every version).

What only these runs decide: whether HTKK accepts the import of a loaiTKhai B file into the Bổ sung form; whether it writes anything
the web file does not (mục D `soTienChenhLech`, `ct46`); whether the PL 01 bổ sung reopens with the saved PL 01 sheet.

Cohort 9d45beb (HTKK 5.8.2), the four U5 cases: `01CNKD-khbs-increase-Q3-2026` (run 43733536472), `-decrease-` (43733539063) and
`-lan2-` (43733541969) got through every round: HTKK imported the loaiTKhai B files into the Bổ sung form, showed no "Tổng hợp KHBS"
(step bit 2048 set; masks 2583, lần 2 2783), saved the intermediate bổ sung, then stopped at the pinned-schema gate before Kết xuất
(`exportSchemaPinnedVerified` false, `declaration-export-not-matched`): `WinFnProcess.GetToKhaiInfo` sets `ToKhaiInfo.XsdFileName` to
`KHBS_<XsdSchema>_<VersionKBSXML>.xsd` only for LoaiToKhai B with a non-empty KieuKHBS, so for U5 it is the MAIN schema
`01_CNKD_HKD_TT50_310.xsd`. `CnkdKhbsPlan` now pins that path (same SHA-256 as before). `01CNKD-PL01-khbs-Q3-2026` (run 43733544586)
stopped in its bổ sung round at the first giảm thuế tick (`declaration-import-tick-not-matched`, code 7 = tick cell locked, mismatch
16 = AJ291) after the four edits matched: `CnkdHkd01TT50Nckt310.lockUnLockA_TK` sets `AJ.Locked = !(CE > 0)` for every row, and runs
only from `AutoBindData_0` and `ButtonClick_0`. The tick now records `declarationTickLockShape` (1 CE > 0, 2 U > 0, 4 L > 0, 8 ticked,
16 bổ sung round, 128 recorded) so the next run says whether the lock follows a zero CE or a refresh that did not run after the import.

PL 01 refresh (work/cnkd-khbs-4): the "Thêm phụ lục" route cannot re-run `lockUnLockA_TK`: `frmWinSelectPhuLuc.btnDongY_Click` calls
`ProcessSheet` (hence `AutoBindData_<index>`) only for annex sheets newly ticked there, never `AutoBindData_0`. The other caller is
`ButtonClick_0`, reached through `frmWinToKhai.winFpSpread_ButtonClicked` for a click on any button or checkbox cell of sheet 0; it
runs `lockUnLockA_TK` first. So when a tick cell is locked in a bổ sung round with CE > 0 (lock shape bits 1 and 16), the driver
makes ONE original SPACE on `AJ341`, the giảm thuế checkbox of the empty TMĐT row (`HtkkDeclarationCasePlans.KhbsTickRefresh`), only if
it is an unlocked, unticked checkbox; `ButtonClick_0` then clears and locks it again (its CE is 0; not table_1, so no
`daySangPLGiamThue`). The tick is retried once; `declarationTickRefreshMask` records each step (1 attempted, 2 checkbox, 4 unlocked,
8 unticked, 16 SPACE sent, 32 refresh cell unticked afterwards, 64 target unlocked afterwards, 128 original message, 256 recorded).
Cohort c741595 (HTKK 5.8.2): with the main-schema pin, `01CNKD-khbs-increase-Q3-2026` (run 43742193235),
`01CNKD-khbs-decrease-Q3-2026` (43742195682) and `01CNKD-khbs-lan2-Q3-2026` (43742197893) matched the whole tree (271 leaves); htkk_web
keeps the raw exports byte-identical (tests/fixtures/htkk-cnkd-khbs-native-reexport) and released U5 KHBS lần 1 and lần 2+. In those
runs the Bổ sung period dialog showed its phụ lục list (annex list mask 0, the case's annex ticked like round 0), so the static
reading of `UpdatePeriodByVerSion` (list hidden) did not hold; the 4096 branch never ran.
`01CNKD-PL01-khbs-Q3-2026` (run 43742200645) stopped again at AJ291 with `declarationTickLockShape` 151 (CE, U, L > 0, unticked,
bổ sung round): the lock is stale, set by `lockUnLockA_TK` when the sheet was bound before the import, and nothing re-runs it after
the import. In HTKK it runs only from `AutoBindData_0` (`WinSpreadProcess.ProcessSheet`: sheet load, the "Đồng ý" of
`frmWinSelectPhuLuc` behind btnThemPhuLuc, `frmWinToKhai.AddFullPLImportXML`) and `ButtonClick_0`. A candidate original route is the
"Thêm phụ lục" dialog after the import (not tried; the case stays an observation case and the web keeps PL 01 bổ sung hidden).

Run 43758208221 (PL 01 with the refresh): `declarationTickRefreshMask` 265 = attempted, AJ341 unticked, but AJ341 was neither a
checkbox nor unlocked: the TMĐT table moves down with the rows of table_1 (three rows here), so a fixed address misses it. The refresh
cell is now found by scanning column AJ below the target for the first visible, unlocked, unticked CheckBoxCellType whose row has
CE <= 0 and is not a planned cell (bit 512; `declarationTickRefreshRowOffset` = its row minus the target row). If none is found, or the
target stays locked (bit 64 clear), PL 01 bổ sung stays with HTKK (web flag false, the app already refuses it).

Run 43765180283 (PL 01 with the scan, builder 876871a): `declarationTickRefreshMask` 257 = attempted and recorded only, row offset 0:
no visible, unlocked, unticked giảm thuế checkbox with CE <= 0 below the target, so nothing was pressed; the target stayed locked
(lock shape 151, code 7). Every AJ of table_1 carries the stale lock and the other tables' rows are locked by `lockUnLockA_TK` too (no
TMĐT / LPS activity in the case header). The remaining checkboxes of sheet 0 are declaration data (header B_26…B_35, locked in a bổ sung
by `AutoBindData_0`; trụ sở chính G_260), and pressing one would change the declaration. Conclusion: with the original import followed by
original ticks, HTKK 5.8.2 gives no original action that re-runs `lockUnLockA_TK` for sheet 0 in a U5 bổ sung round, so this case
cannot reach Kết xuất. `01CNKD-PL01-khbs-Q3-2026` stays registered as a non-gating observation case; htkk_web keeps
`KHBS_01CNKD_PL01_RELEASED` false and refuses a 01/CNKD bổ sung with a phụ lục giảm thuế ("Trường hợp này lập bằng HTKK.").
## 02/QTT-TNCN TT80 (B8 2.7.3): mode `declaration-amendment-khbs-inspect` (observation cases)

htkk_web (docs/KE-KHAI-BO-SUNG-02-QTT-TNCN.md, `lib/htkk-qtt02-khbs.ts`, hidden behind `KHBS_02QTT_RELEASED=false`) read the KHBS of
B8 statically from HTKK 5.8.2: Menu.xml has `KieuKHBS="3"` (VersionKHBS 2.7.3, sheets 02, 02-1, 01-KHBS, 01-1-KHBS), so
`btnTongHopKHBS` is shown for a bổ sung; B8 is in neither menu list of `WinFnProcess.WinLoadFromFile` /
`WinDoWorkEvent.WinDoWorkGetExportSheetXML`, so the workbook is `KHBS_TT80_273.xls` (D1 formulas) and the fragments use
`KHBS_01_TT80_xml.xml` / `KHBS_01_1_TT80_xml.xml`; schema `Validate/KHBS_02_QTT_TNCN_TT80_273.xsd` (b534fbed…7529). MapMCT: 29 static
items [20]…[48]; `CollectionStatic01_1_KHBS` writes NopThua into CE, so ct7 is −ct06 for [34], [36], [40], [41], [43]; [45] has
LoaiThue 2 (Muc_III); tiểu mục 1001. `GetHanNopToKhai` KieuKy Y over a whole year: the last day of the third month after the year
(năm 2025 → 31/03/2026), so 227 late days to the fixed ngày lập 13/11/2026.

`scripts/htkk_qtt02_khbs_web_cases.py` holds the pins (sizes and SHA-256, never the files) and per-case settings of four cases, merged
into `htkk_ntnn_khbs_web_cases.py` (annexParts `PLuc_02_1_BK_QTT_TNCN` before the two fragments; `test_qtt02_khbs_web_cases.py`).
Registered in `htkk-native-cases.json` (adapters `02-qtt-tncn-2.7.3-khbs`, `-khbs-lan2`; HTKK 5.8.2) with `releaseGate: false`.

| Case | Files | Web leaf target (no TTinDVu) |
| --- | --- | --- |
| `02QTT-khbs-increase-Y2025` ([21] 300tr → 330tr; [32] +3tr) | original, web | 326 |
| `02QTT-khbs-lan2-Y2025` (lần 2 on the increase case, [21] 340tr) | original, prior (= the increase web file), web | 326 |
| `02QTT-khbs-decrease-Y2025` ([34] 4tr → 5tr; ct7 −1tr) | original, web | 300 |
| `02QTT-khbs-refund-Y2025` (hoàn qua chuyển khoản on both: [34] 20tr → 22tr, [46] 16,12tr; Muc_III +2tr) | original, web | 326 |

Driver: the rounds of the other KHBS cases with the plan of `02QTT-dependants-Y2025` (menu 101 → 101_11 → B8, năm 2025, KieuKy 12,
annex 02-1; `cmdImportXML_Click` adds every B8 annex), KHBS schema above, every round imported, "Tổng hợp KHBS" in each bổ sung
round (no driver change). Năm 2025 only: the period dialog opens on Now.Year − 1, and HTKK refuses đến tháng 12/2026 before
01/12/2026. What only these runs decide (web predictions in its golden): hạn nộp 31/03/2026 and 227 days; the sign of ct7 for the
NopThua items; [45] in Muc_III with tongCong_9; negative ct3b; the [33] caption with its double space; whether the Bổ sung period
dialog shows the B8 annex list (handled by `SelectReviewedVisibleAnnexList` as in the năm 2026 cases).

Cohort e0ad917 (web 54ebb413; runs 43776168729 increase, 43776171044 lần 2, 43776173361 decrease, 43776176073 refund): every
round ran (step masks 1591 / 1791, round 1 / 2, import and summary acknowledged, export written and the KHBS schema pin held),
then `declaration-export-not-matched` with the same shape in all four: tree mask 48 (PLuc + structure), 202 compared leaves, four
text differences at web element ordinals 159, 160, 235, 236 = `kyKKhaiTuNgay` / `kyKKhaiDenNgay` of the two fragment Headers
(native text 10 characters, web empty). `WinDoWorkEvent.xmlExportTTinChungKHBS` writes `GetNgayDauKyKeKhai` /
`GetNgayCuoiKyKeKhai` as dd/MM/yyyy when TTinChung leaves them empty (KieuKy Y: 01/01/2025, 31/12/2025); htkk_web now writes them
(pins re-made, leaf targets unchanged). 202 leaves = the web count minus `DSachHSo` (BKeHSo + TongCong, 70 / 44 leaves): its child
count differs, i.e. HTKK writes another hồ sơ group (presumably 02-1/BK-QTT-TNCN). Retention was refused (`XML_PRIVACY`, native
leaf 206 = the first `ten_HSo`, a text outside the inputs), so no raw export exists yet. These cases now also accept the public B8
catalogue texts (`CATALOGUE_TEXTS`: sheet names, the 02-1 captions with and without "[nn] - ") and, on the 01-1/KHBS row key
leaf only, ' - '-joined keys of input pieces (`catalogue_texts`), so the next run retains the export and the web port follows HTKK.

Cohort fc800a2 (web b13c8cd9; runs 43790973810, 43790976608, 43790979591, 43790982675): the four fragment Header dates now match
(no text difference left); the only difference is the child count of `PL01_1_KHBS/Muc_A/DSachHSo` (web element 249, kind 3, 202
leaves). Retention stopped again (`XML_PRIVACY`), now at native leaf 209: the catalogue `ten_HSo` of leaf 206 passed, and leaf 209
is `ct3_ma` of the first row of the FIRST hồ sơ group. A main-sheet row would carry an input text ("[20]"…), so the first group is
the 02-1/BK-QTT-TNCN one and its rows name the 02-1 items. `CATALOGUE_TEXTS` now also holds the MapMCT codes [14]…[17].

Cohort aaf853d (web b0371ca1; runs 43818257270, 43818260608, 43818263782, 43818267354): retention passed for all four (output branches
`declaration-web-native-qtt02-khbs-*-y2025-output-htkk582`, `allTaxValuesMatched` false, mask 48, 202 leaves as before). The raw
exports show the second `DSachHSo` group: `001201` "02-1/BK-QTT-TNCN", one row per 02-1 row for [16] then for [17] although the table
is unchanged (key "họ tên -  - số giấy tờ", ct04 = ct05 = the month, ct06/ct7 0), none for [14]/[15]. htkk_web 94d441ce writes it and
reproduces every leaf of the four exports (kept byte-identical there); every other prediction (hạn 31/03/2026, 227 days, NopThua
signs, Muc_III, negative ct3b) held. New pins; leaf targets 326 / 300 (plans 330 / 304).

## 05/QTT-TNCN TT80 (B9 2.9.3): mode `declaration-amendment-khbs-inspect` (observation cases)

htkk_web (docs/KE-KHAI-BO-SUNG-05-QTT-TNCN.md, `lib/htkk-qtt05-khbs.ts`, hidden behind `KHBS_05QTT_RELEASED=false`) read the KHBS of
B9 statically from HTKK 5.8.2: Menu.xml `KieuKHBS="3"` (VersionKHBS 2.9.3; sheets 05 0004, 05-1 000401, 05-2 000402, 05-3 000403), B9
in neither KHBS menu list, so `KHBS_TT80_293.xls` (D1 formulas) and the generic TT80 templates; schema
`Validate/KHBS_05_QTT_TNCN_TT80_293.xsd` (8f885a0f…931d, on TKhaiThue_DBHC.xsd). Every MapMCT B9 item is static: 26 of the tờ khai, the
totals of 05-1 (SheetIndex 1) and of 05-2 (SheetIndex 2), each sheet one hồ sơ group when it has rows; only [40] (LoaiThue 0) and [41]
(LoaiThue 0, NopThua 1) carry ct7; tiểu mục 1001; hạn 31/03/2026, 227 days to 13/11/2026.

`scripts/htkk_qtt05_khbs_web_cases.py` holds the pins and per-case settings of three cases (annexParts 05-1, 05-3 before the fragments),
merged into `htkk_ntnn_khbs_web_cases.py` (`test_qtt05_khbs_web_cases.py`). Learning from B8, the public B9 catalogue texts (sheet names
and captions of Menu.xml, MapMCT SheetNames, the codes of the annex totals, every MapMCT B9 caption) are in `CATALOGUE_TEXTS` from the
first run, so a differing export is retained. Registered in `htkk-native-cases.json` (adapters `05-qtt-tncn-2.9.3-khbs`, `-khbs-lan2`;
HTKK 5.8.2) with `releaseGate: false`.

| Case | Files | Web leaf target (no TTinDVu) |
| --- | --- | --- |
| `05QTT-khbs-increase-Y2025` (05-1 row A income 300tr → 330tr; [41] −3tr, ct7 +3tr) | original, web | 393 |
| `05QTT-khbs-lan2-Y2025` (lần 2 on the increase case, 350tr) | original, prior (= the increase web file), web | 393 |
| `05QTT-khbs-decrease-Y2025` (05-1 row A tax withheld 12tr → 13tr; ct7 −1tr) | original, web | 341 |

Driver: the rounds of the other KHBS cases with the plan of `05QTT-two-employees-Y2025` (menu 101 → 101_11 → B9, năm 2025, KieuKy 12,
annexes 05-1, 05-3; `cmdImportXML_Click` adds every B9 annex), KHBS schema above, every round imported, "Tổng hợp KHBS" in each bổ sung
round; no driver change. What only these runs decide: whether HTKK writes only the changed rows of the 05-1 totals (B8 wrote unchanged
dynamic rows of its annex), the ten_HSo of the 05-1 group ("05-1/BK-TNCN"), the 0016 checks of a B9 bổ sung after the import, and the
annex list of the Bổ sung period dialog.

Cohort 5cf04ba (web cccb59f8; runs 43845164240, 43845168874, 43845173606): every round ran (step masks 1591 / 1791, the Bổ sung period
dialog showed no annex list: `declarationAnnexListMask` 0), and the three exports were retained (`allTaxValuesMatched` false, mask 48,
63 leaves: the walk stopped at the child count of `HSoKhaiThue/PLuc`). The only difference: HTKK wrote `PLuc_05_2_BK_QTT` as its default
sheet (one empty row, totals 0) into every bổ sung although neither version had 05-2 (the lần đầu export of the same C0 had none).
htkk_web 2d7ead18 writes every bảng kê into a B9 bổ sung and reproduces every leaf of the three exports. The contract now separates the
lần đầu annexes (`originalAnnexParts`: 05-1, 05-3) from those of a B file (05-1, 05-2, 05-3); new pins, leaf targets 393 / 341
(plans 397 / 345). The KHBS groups (0004, 000401 "05-1/BK-TNCN", changed totals only), ct7 of [41], 227 days and ct3b held.

## 03/TNDN TT80 (N8 2.9.4): mode `declaration-amendment-khbs-inspect` (observation cases)

htkk_web (docs/KE-KHAI-BO-SUNG-03-TNDN.md, `lib/htkk-tndn03-khbs.ts`, hidden behind `KHBS_03TNDN_RELEASED` / `_LATER_RELEASED` = false)
read the KHBS of N8 statically from HTKK 5.8.2: Menu.xml `KieuKHBS="3"`, VersionKHBS 2.9.4, tờ khai MaHoSo 0066; N8 is in the DIA_BAN
menu list of `WinFnProcess.WinLoadFromFile` / `WinDoWorkEvent.WinDoWorkGetExportSheetXML` (as D1, L7), so the workbook is
`KHBS_DIA_BAN_294.xls` (D1 formulas) and 01/KHBS uses `KHBS_01_DIA_BAN_xml.xml`; schema `Validate/KHBS_03_TNDN_TT80_294.xsd` (42f72f6a…8ba2).
MapMCT: 71 static tờ khai items, only the nine `E1_PN`/`E2_PN`/`E5_PN` items (NghiaVuThue/CtE*/tieuMuc*) have LoaiThue 0 (tiểu mục
1052/1056/1057/1099/1053), no NopThua, no item on 03-1A/1B/1C/03-2/03-5. `GetHanNopToKhai` has an N8 branch (T5,Y4,C6,C7,N8,H4; MaQuyetToan
01/04): the quarter after the one holding DenNgay, its last day: năm 2025 → 31/03/2026, 227 late days to 13/11/2026.

`scripts/htkk_tndn03_khbs_web_cases.py` holds the pins (sizes and SHA-256, never the files), per-case settings (annexParts
`PLuc_03_1A_TNDN`, import) and, from the start, the public N8 catalogue texts (`CATALOGUE_TEXTS`: Menu sheet names, every MapMCT N8 code
and caption with and without its "[nn] - " prefix, DM_MaTM names of the tờ khai tiểu mục), merged into `htkk_ntnn_khbs_web_cases.py`
(`test_tndn03_khbs_web_cases.py`). Registered with adapters `03-tndn-2.9.4-khbs`, `-khbs-lan2` (HTKK 5.8.2), `releaseGate: false`.

| Case | Files | Web leaf target (no TTinDVu) |
| --- | --- | --- |
| `03TNDN-khbs-increase-Y2025` ([B2] 25tr → 35tr, [B14] = [C7] 1,2 tỷ → 1,21 tỷ; 1052 +2tr) | original, web | 421 |
| `03TNDN-khbs-lan2-Y2025` (lần 2 on the increase case, 1052 +1tr) | original, prior (= the increase web file), web | 421 |
| `03TNDN-khbs-decrease-Y2025` (1052 −2tr, ct3b −136.200) | original, web | 421 |
| `03TNDN-khbs-rate15-Y2025` (C7 15% on both, 1052 +1,5tr) | original, web | 421 |

Driver: the rounds of the other KHBS cases with the plan of `03TNDN-profit20-Y2025` (menu 101 → 101_2 → N8, năm 2025, KieuKy 11, 03-1A
chosen in the period dialog), KHBS schema above, every round imported, "Tổng hợp KHBS" in each bổ sung round (no driver change). What only
these runs decide (web predictions in its golden): the row set of 01-1/KHBS (computed items B1, B13, C4, C6, H1, I included), ct3_ma
"E1_PN" with the "1052 - " caption, ct7 0 for items without LoaiThue, no 03-1A hồ sơ group in `DSachHSo`, hạn 31/03/2026.

Cohort for web 6c7096f01 / builder c8f0bfe: `03TNDN-khbs-increase-Y2025`, `-decrease-` and `-lan2-` matched the whole tree.
`03TNDN-khbs-rate15-Y2025` (run 43871378439) stopped at `declaration-export-not-matched`, tree mask 16 (PLuc text only), one text
mismatch at element ordinal 374 = `ct3_ten` of the C9 row (text shape 360: native 90 characters, neither a prefix of the other);
retention was refused (`XML_PRIVACY`, first ct3_ten path, text-other). MapMCT has "(C9 =(C7 x 20%) + (C8 x C8a))" while the tờ khai
cell C70 is ="…(C9 =(C7 x "&R66&"%) + (C8 x C8a))": htkk_web now writes the C9 caption with the case's rate (15%), the rate15 web pin
changed (11201 bytes, 918e23b7…1036), and `CATALOGUE_TEXTS` takes the C9 caption for 15/17/20% (space or line break) so the next
export is retained even if that reading is wrong.

## 03/NTNN (J1 3.0.8): mode `declaration-amendment-khbs-inspect` (observation cases)

htkk_web (docs/KE-KHAI-BO-SUNG-03-NTNN.md, `lib/htkk-ntnn01-khbs.ts` with `data/htkk-03-ntnn-khbs-rules.json`, hidden behind
`KHBS_03NTNN_RELEASED` / `KHBS_03NTNN_LATER_RELEASED` = false) reads the KHBS of J1 statically: Menu.xml `KieuKHBS="3"`, VersionKHBS 3.0.8,
tờ khai MaHoSo 0046, the generic workbook `KHBS_TT80_308.xls` (the formulas of the I9 `KHBS_TT80_251.xls`), the I9/Y8 output templates
and schema `Validate/KHBS_03_NTNN_TT80_308.xsd` (c99ad92b…7272). MapMCT J1: four DYNAMIC items of ThueNTNN, (8) ThueTNDN/ct8, (9) the
rate ThueTNDN/ct9, (10) ThueTNDN/ct10, (11) ThueTNDN/ct11 (LoaiThue 0), key TCTPath ct1a…ct5, ct7; MapMCT_TieuMuc gives (11) tiểu mục
1052. The J1 entries were read from the 5.8.1 payload (J1 is class (a) in HTKK-5.8.2-IMPACT.md and HTKK-5.8.3-IMPACT.md); these runs
also check that they hold on 5.8.2. Kỳ 09/2026: hạn 20/10/2026, 24 late days to 13/11/2026.

`scripts/htkk_ntnn03_khbs_web_cases.py` holds the pins (sizes and SHA-256, never the files), per-case settings (no annex,
`khbs-web-xml-import-tick-reexport`) and the public J1 catalogue texts (`CATALOGUE_TEXTS`), merged into `htkk_ntnn_khbs_web_cases.py`
(`test_ntnn03_khbs_web_cases.py`). Registered with adapters `03-ntnn-tt80-3.0.8-khbs`, `-khbs-lan2` (HTKK 5.8.2, `tick`), `releaseGate: false`.

| Case | Files | Web leaf target (no TTinDVu) |
| --- | --- | --- |
| `03NTNN-khbs-increase-M09-2026` (row A (6), (8) 800tr → 900tr at 5%: (8), (11); 1052 +5tr, ct3b 36.000) | original, web | 168 |
| `03NTNN-khbs-lan2-M09-2026` (lần 2 on the increase case: row A (8) → 1 tỷ; 1052 +5tr, ct3b 36.000) | original, prior (= the increase web file), web | 168 |
| `03NTNN-khbs-decrease-M09-2026` (row B (10) 1tr miễn giảm: (10), (11); 1052 −1tr, ct3b −7.200) | original, web | 168 |

Driver: the rounds of the I9 cases with the plan of `03NTNN-no-rate-M10-2026` for tháng 09/2026 (menu 101 → 101_8 → J1, KieuKy 18, no
annex), KHBS schema above, "Tổng hợp KHBS" in each bổ sung round. Ntnn03TT80Nckt308.FinishImportXML (0x6001937) clears every imported rate
[9] (BU := getThuSuatByMa(CR, "DC_97") = ""), so after EVERY import (C0, the intermediate lần 1 of the lần-2 case, the last round)
`HtkkDeclarationCasePlans.KhbsImportTick` types the rates of the files again through the original editor: `number|BU34|5`,
`number|BU35|2` (`$HtkkNtnnKhbsTickCases`; method pins `HtkkOracleBaseline.Ntnn03KhbsRateMethodPins`, the HTKK.exe editor path only:
the same bodies as the gtgt04tt89 pins; the J1 business methods are not pinned, no payload of 5.8.2 was on the review machine). No other
driver change. What only these runs decide (web predictions in its golden): the J1 MapMCT/MapMCT_TieuMuc of 5.8.2, the text of
`ct3_2_ten` with the empty ct3 / ct7 parts, `ct9` of a typed rate ("5.00" in the web file), no (9) row when the rate is typed again
equal, and the J1 tiền chậm nộp.

## 01/TCKT TT89/2026 3.1.0 (Y7 on HTKK 5.8.2): mode `declaration-amendment-khbs-inspect` (observation cases)

htkk_web (`lib/htkk-tckt01-khbs.ts`, docs/NGHIEP-VU-HKD.md "Kê khai bổ sung 01/TCKT 3.1.0", hidden behind `KHBS_01TCKT_TT89_RELEASED` /
`_LATER_RELEASED` = false) reads Y7 from the HTKK 5.8.2 Menu.xml (f26c2ea2…): `KieuKHBS="3"`, VersionXML and VersionKHBS 3.1.0, sheets
01-KHBS and 01-1/KHBS. So unlike U5 (KieuKHBS "") the bổ sung carries 01/KHBS and 01-1/KHBS, the rounds run "Tổng hợp KHBS" and the B file
is checked against `Validate/KHBS_01_TCKT_TT89_310.xsd` (52067 bytes, 4631d4c3…5020: the 3.1.0 tree plus PL01_KHBS / PL01_1_KHBS; the web
rebuilt it from the 5.8.2 main schema and the 5.8.1 KHBS block and checked it against the SHA-256 of the 5.8.2 payload and the MsiFileHash
entry). KHBS workbook `KHBS_TT80_310.xls` (same bytes as the 5.8.1 `KHBS_TT80_309.xls`, formulas of the 5.8.2 `KHBS_TT80_309.xls`), templates
`KHBS_01_TT80_xml.xml` / `KHBS_01_1_TT80_xml.xml`. The MapMCT / MapMCT_TieuMuc / DM_MaTM the web read are the 5.8.1 files (the 5.8.2 ones
were not available to it): main items [07] [08] [09] [11] [12] [13] static (tiểu mục [09] 1003, [12] 1701, [13] 1014), 01/BK-KTHTKD items
[04]…[09] dynamic keyed ct04 - ct05 - ct06_ten, 02/BK-KTBĐS items [05]…[12] keyed ct05 - ct06.

`scripts/htkk_tckt01_khbs_web_cases.py` holds the pins (sizes and SHA-256, never the files), per-case settings (annexParts
`PLuc_HKD_CNKD` / `PLuc_CANHAN_TTS`, import), the public Y7 catalogue texts (`CATALOGUE_TEXTS`: sheet names and MaHoSo, every MapMCT Y7 code
and caption with and without its "[nn] - " prefix, the DM_MaTM names of 1003 / 1701 / 1014) and `exportDates` (TKhaiThue/ngayKy is the
export day for Y7, as in the lần đầu cases), merged into `htkk_ntnn_khbs_web_cases.py` (`compare_tree` now passes a case's exportDates;
`test_tckt01_khbs_web_cases.py`). Registered with adapters `01-tckt-tt89-3.1.0-khbs-bk1`, `-khbs-bk1-lan2`, `-khbs-bk2` (HTKK 5.8.2),
`releaseGate: false`.

| Case | Files | Web leaf target (no TTinDVu) |
| --- | --- | --- |
| `01TCKT-310-khbs-hop-tac-kd-Q4-2026` (01/BK-KTHTKD quý 4/2026, row A 300tr → 350tr; 1003 +1tr) | original, web | 224 |
| `01TCKT-310-khbs-lan2-hop-tac-kd-Q4-2026` (lần 2 on the case above, 350tr → 380tr; 1003 +600.000) | original, prior (= the case above's web file), web | 224 |
| `01TCKT-310-khbs-decrease-hop-tac-kd-Q4-2026` (row B [08] 110tr → 100tr; 1003 −100.000) | original, web | 198 |
| `01TCKT-310-khbs-bds-M10-2026` (02/BK-KTBĐS tháng 10/2026, lessor A [08] +20tr; 1701 +1tr, 1014 +1tr) | original, web | 242 |

Driver: the rounds of the other KHBS cases with the plans of `01TCKT-310-hop-tac-kd-two-individuals-Q4-2026` (menu 101 → 101_37 → Y7, quý
4/2026, 01/BK-KTHTKD) and `01TCKT-310-bds-three-lessors-M10-2026` (tháng 10/2026, 02/BK-KTBĐS; tỉnh/xã panel of the period dialog), KHBS
schema above, every round imported (both bảng kê import with every leaf, runs 44044889464, 44044893474), 0699 closed as for the lần đầu
cases, "Tổng hợp KHBS" in each bổ sung round (no driver change; `Tckt01KhbsPlan`). Ngày lập 13/11/2026 is before both hạn nộp (quý 4/2026
01/02/2027, tháng 10/2026 20/11/2026): ct3a_1 written, 0 days, ct3b 0. What only these runs decide (web predictions in its golden): whether
the 5.8.2 MapMCT adds Y7 3.1.0 items (ct09a / ct12a, PL 01-3) to 01-1/KHBS; the static ct3_ten with its "[07] - " prefix (CollectionStatic
adds " - Tiểu mục" only with a TCTPath); the row key texts (the nhóm ngành name with its double space); the hồ sơ groups 0252 "01/TCKT",
025201 "01/BK-KTHTKD", 025202 "02/BK-KTBĐS"; tiểu mục 1003 / 1701 / 1014 and their names.
