# HTKK 5.8.3 impact on the launched forms

Assessment date: 16/11/2026. Phase 1 only: no builder or web behaviour changes, and the default oracle
stays 5.8.1 (5.8.2 selectable per case). HTKK 5.8.3 was released on 12/11/2026. The GDT notice says that
from 11/11/2026, declarations touched by the upgrade "sẽ sử dụng ... HTKK 5.8.3 thay cho các phiên bản
trước đây".

No installer, MSI, CAB member, DLL or EXE was executed or patched. Everything was handled as inert data in
a session scratchpad. Nothing extracted from the installer is committed here, only hashes, version
strings, Menu.xml attribute values, message texts and short IL string literals.

## 1. Source and trust

`source-watch.yml` (run 43838373880, 16/11/2026 ~09:17 UTC) reported `review-required`
(pinned 5.8.1, published 5.8.3). `source-update.py stage` correctly blocks any version other than the
pinned one with `UNREVIEWED_VERSION`: the automated pipeline never extracts an unreviewed release. As for
5.8.2, the review itself was done by hand on inert data, which needs no owner action:

- The official GDT software page (same URL as `source-watch.py` `PAGE`) was fetched through the vn-fetch
  relay (direct TLS to www.gdt.gov.vn is reset). HTML SHA-256 `862fbaae…18c0`. The 5.8.3 row (dated
  12/11/2026) has the `linkDown` href **`https://www.fshare.vn/file/59JNEQ8M6QW4`**. The 5.8.2 row still
  points to `WYSRASTITCWB`, 5.8.1 to `TPW3FMLVAJL1`.
- The archive was downloaded directly with this repository's `scripts/source-candidate.py`
  `fetch_resource` (URL policy, redirect checks, size bounds). Final host `download048.fshare.vn`.

| Item | 5.8.2 (reviewed baseline) | 5.8.3 |
|---|---|---|
| Fshare file | `WYSRASTITCWB` | `59JNEQ8M6QW4` |
| Archive (RAR) bytes | 89,262,341 | 89,296,848 |
| Archive SHA-256 | `51baf5c8…d424` | `0f950e233aa3df7901a66eead224f8a10b94ddf7ee1fe844e9d1fb7bb73d2a98` |
| Archive Last-Modified | 2026-11-05T01:23:55Z | 2026-11-12T03:07:01Z |
| Folder in archive | `HTKK_5.8.2_DLL_signed/` | `HTKK_5.8.3_DLL_signed/` |
| `setup.exe` SHA-256 | `1c2612d3…0efb` | `9fcc416f7fe70cbb51a736cf5a29b2a203b64341e2a06902154f14d8e4cda06c` |
| `HTKK.msi` SHA-256 | `17c21f3c…fd73` | `491c3fe73ae557557e476c150e3d9ef6591e172ab94e69c51e99d084c5802a60` |
| `Data1.cab` SHA-256 | `5427c663…530c` | `277f6792f5860f3ddfb10f2ec1ac9d445c306973e24be5ca6dd189df86ae385e` |
| MSI ProductVersion / ProductCode | 4.2.2 / `{53B9335C-…-84E55F97929D}` | same |
| Media LastSequence | 4781 | 4781 |
| `Project/HTKK.exe.config` VERSION | 5.8.2 | **5.8.3** |
| MSI File rows / size match / MsiFileHash MD5 match / versioned without MsiFileHash | 4781 / 4781 / 4748 / 33 | **4781 / 4781 / 4748 / 33** |

**Authenticode** (osslsigncode 2.8; trust file = Ubuntu CA bundle plus GlobalSign Code Signing Root R45,
SHA-256 `ba80d6ea…d469`, the same file as for 5.8.2; R45 re-downloaded from `secure.globalsign.com`,
SHA-256 `7b9d553e…df86`, unchanged). Signer CRL fetched over HTTPS from `crl.globalsign.com`
(lastUpdate 16/11/2026 10:20:01 UTC, nextUpdate 23/11/2026).

- `setup.exe` and `HTKK.msi` both pass, exit code 0: digest, chain and CRL OK.
- Signer **Tổng Cục Thuế**, OU IT Department, VN, serial `6435F70483012A5DBC374003` (same certificate as
  5.8.1 and 5.8.2). Issuer GlobalSign GCC R45 EV CodeSigning CA 2020, root GlobalSign Code Signing Root R45.
- Countersignature times: setup 12/11/2026 02:57:06 UTC, MSI 12/11/2026 02:57:21 UTC.
- "Timestamp is not available" for the RFC 3161 path, exactly as for 5.8.1 and 5.8.2 (legacy
  countersignature): parity, not a regression.

Same caveats as before: the CAB is trusted only through the signed MSI's File/MsiFileHash tables (legacy
MD5), and 33 versioned files (HTKK.exe and the DLLs among them) have no MsiFileHash.

The GDT notice page (HTML SHA-256 `2730e404…b86e`) was read. Its attachment
`NoiDungNangCap_HTKK_5.8.3.doc` returned a relay 504, so the notice text comes from the page body.

## 2. Payload diff (5.8.2 → 5.8.3)

0 files added, 0 removed, 14 changed. **No XSD, no XML template and no input workbook of a launched form
changed.**

| File | 5.8.3 SHA-256 | What changed |
|---|---|---|
| `Project/HTKK.exe` (+ `.pdb`) | `2e69b74d…f382` | see §3 |
| `Project/TAX.HTKK.Business.dll` (+ `.pdb`) | `46a4dca1…aac3` | see §3 |
| `Project/TAX.HTKK.Utilities.dll` (+ `.pdb`) | `cd603a3e…15d9` | bytes only: all 1,617 method bodies identical |
| `Project/Interop.TBARCODE5Lib.dll` | `51f0bf31…d90a` | barcode interop, not pinned |
| `Project/HTKK.exe.config` | `92767481…b3f8` | VERSION 5.8.2 → 5.8.3 |
| `Project/Menu.xml` | `dec41973…5d06` | four Validity elements, below |
| `Project/Message.xml` | `09599f46…4274` | new 0716–0719 |
| `InterfaceIni/DM_DUNG_CHUNG.xml` | `691ccff6…cba5` | DC_13: 39 codes added (0101–0137, 0201, 0202) before the existing 0208… |
| `InterfaceIni/ConvertVersion.xml` | `1275bf11…de50` | XSBHDC, XSBHDCMG, TCKT and TMĐT rows extended; VersionApp 582 → 583 on the 310 rows (U5's row keeps 298 → 310) |
| `InterfaceTemplates/excel/01_BKNT_KTNT_TT89_309.xls` | `203481da…a99e` | Header rule of [08] (notice item 1); not launched |
| `ReportTemplates/Excel/04_GTGT_TT89_309.xls` | `b24536da…6716` | print template of Z3; cell values identical (xlrd), formatting only |

Menu.xml, attribute by attribute (every other entry identical):

| Menu | 5.8.2 Validity | 5.8.3 Validity |
|---|---|---|
| C9 02/NTNN TT80 | StartDate 01/01/1900, **EndDate 01/10/2026** | StartDate 01/01/1900, **EndDate ""** |
| X9 02/NTNN TT89 | **StartDate 01/07/2026** | **StartDate 01/01/1900** |
| D6 04/NTNN TT80 | StartDate 01/01/1900, **EndDate 01/10/2026** | StartDate 01/01/1900, **EndDate ""** |
| Y1 04/NTNN TT89 | **StartDate 01/07/2026** | **StartDate 01/01/1900** |

New messages: 0716 "Chỉ được chọn 1 PL 01-8/GTGT" (no caller in 5.8.3), 0717 "01/PL-PSC: Bắt buộc nhập …"
(oil and gas, `TkPsc01TT89Nckt309`), **0718 "Tờ khai hiệu lực từ ngày 07/10/2026"**, **0719 "Tờ khai hiệu
lực đến ngày 06/10/2026"**.

The GDT notice lists four items, all confirmed by the diff:

1. 01/BKNT-KTNT TT89: [08] may be 0 (was > 0). Not launched.
2. 02/NTNN: TT89 form when "Ngày đến" ≥ 07/10/2026, TT80 form when "Ngày đến" < 07/10/2026 (was: TT89
   valid from 01/07/2026).
3. 04/NTNN: the same rule.
4. 01/NTNN, NCCNN TT89 (Y8): with box (2) ticked, mục II is required but II-I and II-II are no longer both
   required.

## 3. IL diff

Method: the same token-normalised comparison as for 5.8.2 (operands resolved to names and literals,
branch targets, local indices and compiler closure names masked), in the scratchpad. Scripts not
committed.

| Assembly | Methods (5.8.2) | Raw-identical or token-renumbered | Real changes |
|---|---|---|---|
| HTKK.exe | 2,417 | all but the list below | `frmHTKKPeriod.CheckHLToKhaiTT80`, `btnDongY_Click`, `frmHTKKPeriod_Load`, `frmTraCuuToKhai..ctor`, `WinDoWorkEvent.xmlExportTTinChung`, `InsertExportTableNode`, `GetPrefix`, `WinFnProcess.InsertRowsValue`, `SpreadPrint2.SetupPageBreak`, `WinSpreadProcess` (`BindDataToPhuLucSpread`, `GetDataFromExcelLarge` and closure renumbering) |
| TAX.HTKK.Business.dll | 16,742 | all but the list below | `Ntnn01TT89Nckt309` (`getCols`, `CellChange_0`, `checkTKChinh`), `GeneralFunctions.GetPreperiodFileName_ThangQuy`, `GetDMThueBVMT`/`GetDMXangDau`/`GetDMThan` of the CNKD and TBVMT classes, and non-launched classes (`CnkdTmdt01Nckt309`, `DsTienNopTmdtNckt282`, `Gtgt01TT89Nckt309`, oil and gas `*Vsp01TT89`/`*Psc01TT89`) |
| TAX.HTKK.Utilities.dll | 1,617 | 1,617 | none |

### Changes that reach launched forms

1. **`frmHTKKPeriod.CheckHLToKhaiTT80`, KieuKy `D_D` (C9, D6, X9, Y1).** In 5.8.2 the four menus shared one
   branch: đến ngày before 01/01/2021 → 0619. In 5.8.3:
   - C9, D6: đến ngày before 01/01/2021 → 0619 (kept); **đến ngày after 06/10/2026 → 0719** ("Tờ khai hiệu
     lực đến ngày 06/10/2026"; literal `07/10/2026` minus one day, `op_GreaterThan`).
   - X9, Y1: **đến ngày before 07/10/2026 → 0718** ("Tờ khai hiệu lực từ ngày 07/10/2026",
     `op_LessThan`). The 0619 test no longer runs for them.
   - With Menu.xml EndDate "" for C9/D6, `GeneralFunctions.CheckToKhaiHetHieuLuc` (unchanged) returns ""
     for them, so the 5.8.2 "Tờ khai hiệu lực đến 01/10/2026" is gone. With StartDate 01/01/1900 for X9/Y1,
     `CheckHieuLuc` no longer refuses từ ngày before 01/07/2026 (0441).
   - Like the 5.8.2 end-of-validity gate, nothing tests LoaiToKhai, so amendments follow the same rule.
2. **`frmHTKKPeriod.btnDongY_Click`, D4/D5.** 5.8.2 never showed the `CheckToKhaiHetHieuLuc` refusal for
   D4/D5. 5.8.3 shows it unless "Tờ khai lần phát sinh" is ticked, so D4 tháng/quý after 30/09/2026 are now
   refused ("Tờ khai hiệu lực đến …"). The web already refuses them (`lib/htkk-period-end-rules.ts`
   `d4EndRule`).
3. **`Ntnn01TT89Nckt309` (Y8).**
   - `checkTKChinh`: before the row loop it computes `ValidateTableEmpty` for ThueNCCNN and ThueCNKCT
     (all columns but the last three). A ThueNCCNN or ThueCNKCT table that is empty is skipped when the
     other one has data, so its blank row no longer gets E_13. ThueNTNN and the M6/M8 choice are unchanged.
   - `getCols` (columns of LockUnlock): `C…BH` plus **BX** (`ct1b_ma`, the code cell of the ngành nghề
     combo L).
   - `CellChange_0`: when column L changes and its text is empty, BX is cleared. 5.8.2 left the old
     `ct1b_ma`.
4. **`WinDoWorkEvent`.** `xmlExportTTinChung` adds Z5~Z6 to the huyện/xã list and
   `InsertExportTableNode` adds Z6~Z5; neither menu exists in the 5.8.3 Menu.xml (pre-staged). `GetPrefix`
   (saved data file prefix `aa`/`bs` + version) now writes 583. Nothing in this repository depends on that
   prefix.
5. **`WinFnProcess.InsertRowsValue`** gains an index bound check (no change for valid rows).
6. `BindDataToPhuLucSpread`: the annex-list branch of Z5 changed (pre-staged menu). `SpreadPrint2`: Z5
   leaves the D1 page-break branch; D1 itself is unchanged. `GetPreperiodFileName_ThangQuy`: adds Z6 next to
   D2. `frmHTKKPeriod_Load`/`frmTraCuuToKhai`: data conversion for the TCKT annexes (not launched).
7. `GetDMThueBVMT` (U5 and the other CNKD classes) and `Tbvmt01TT80*`: the catalogue period list drops
   `102026` (no `Catalogue_102026_*` file exists in either release). U5 in the web does not support mục C
   (tài nguyên, BVMT).

The launched business classes are otherwise identical: `Gtgt01TT80Nckt283`, `Gtgt04TT80*`,
`Gtgt04TT89Nckt309`, `Tndn03TT80Nckt294`, `TncnKk05TT80Nckt293`, `TncnKk05TT89Nckt309`,
`TncnQtt02TT80Nckt273`, `TncnQtt05TT80Nckt293`, the NTNN classes other than Y8, BCTC, `Tts01TT40*`,
`CnkdHkd01TT50Nckt310` (apart from `GetDMThueBVMT`).

### Status of the 5.8.2 method pins in `scripts/htkk-oracle-baselines.json`

All 44 distinct (type, method) pins of the 5.8.2 entry resolve in 5.8.3. Raw IL hashes change for all of
them except `GeneralFunctions.SetLaiDongConBangF5` (raw-identical), because metadata tokens are renumbered.

- **Really changed:** `Ntnn01TT89Nckt309.getCols` (`y8-entry-getcols`) and `Ntnn01TT89Nckt309.CellChange_0`
  (`y8-entry-cellchange`). A 5.8.3 run of the Y8 entry cases fails closed at the method-pin step until both
  bodies are reviewed against the entry plan.
- `WinSpreadProcess.WinInsertCombox` (first overload, `y8-entry-combo`): only a compiler closure field is
  renamed (`CS$<>8__locals44` → `46`).
- Everything else: token-renumbered (same instructions).

## 4. Classification per launched form

Classes as in the 5.8.2 assessment: (a) unchanged; (b) changed in 5.8.3 but our output is still what 5.8.3
produces, or we are stricter; (c) 5.8.3 would refuse or alter our output; (d) superseded for some periods.

| Menu | Form (open scope) | Class | Evidence |
|---|---|---|---|
| D1 | 01/GTGT + 01-2, 01-6 (CSSX, ĐTVT), 01-10, KHBS | (a) | Menu, XSD, templates and `Gtgt01TT80Nckt283` identical. Print page break of D1 unchanged. |
| D4 | 04/GTGT TT80 | (b) | 5.8.3 now refuses tháng/quý after 30/09/2026, which the web already does. |
| Z3 | 04/GTGT TT89 | (a) | Only the print template's formatting changed (values identical). |
| N8 | 03/TNDN + 03-1A/1B/1C/2/5 | (a) | DC_13 additions concern 03-3A/3B, not open. |
| L7, Z8 | 05/KK-TNCN TT80/TT89 + 05-1/PBT + KHBS | (a) | Classes, templates, Menu identical. |
| B8 | 02/QTT-TNCN + 02-1 + KHBS | (a) | |
| B9 | 05/QTT-TNCN + 05-1/2/3 | (a) | `fpSpDisplayReportHoTroIn05QTT` token-renumbered only. |
| I9 | 01/NTNN TT80 + KHBS | (a) | |
| Y8 | 01/NTNN, NCCNN TT89 + KHBS lần 1 | (b) | Validation relaxed (§3.3); for the same input the export is the same, except a cleared ngành nghề now also clears `ct1b_ma`. The web still requires both II-I and II-II when M8 is ticked (5.8.2 rule): stricter, never a refused file. Two entry pins changed. |
| C9 | 02/NTNN TT80 | (b) | End moves from đến ngày 01/10/2026 to 06/10/2026. The web still refuses after 01/10/2026: stricter; contracts ending 02–06/10/2026 cannot be filed with us. |
| D6 | 04/NTNN TT80 | (b) | Same as C9. |
| X9 | 02/NTNN TT89 | **(c)** | 5.8.3 refuses đến ngày before 07/10/2026 (0718). The web refuses only từ ngày before 01/07/2026, so it builds TT89 files for periods 5.8.3 refuses, e.g. 01/07–30/09/2026. The launch case `02NTNN-TT89-two-annexes-2026` (01/07–30/09/2026) is now refused. |
| Y1 | 04/NTNN TT89 | **(c)** | Same as X9; launch case `04NTNN-TT89-one-subcontractor-2026` (01/07–30/09/2026) is now refused. |
| J1 | 03/NTNN | (a) | |
| U5 | 01/CNKD TT50 2.9.8/3.1.0 + PL 01/PL 03 + KHBS | (a) | `GetDMThueBVMT` list only (mục C not supported); ConvertVersion row of U5 changes only VersionApp. |
| G7 | 01/TTS TT40 | (a) | |
| A2, 78 | BCTC TT133 B01a, TT200 năm | (a) | |

No new form or menu. Pre-staged for a later release: code paths for menus Z5/Z6 (not in Menu.xml),
`Gtgt01TT89Nckt309` changes, message 0716 (PL 01-8/GTGT). Z5 sits next to D1 in the print code and in the
annex list, so it is probably the future 01/GTGT TT89 menu that will end D1 for some periods (watch item,
as in the 5.8.2 assessment).

Cross-cutting for the tooling: every pin of `HTKK.exe`, `HTKK.exe.config`, `TAX.HTKK.Business.dll`,
`TAX.HTKK.Utilities.dll`, `Menu.xml`, `Message.xml`, `DM_DUNG_CHUNG.xml` and `ConvertVersion.xml` drifts. A
5.8.3 run fails closed until the baseline exists. The XSD and template pins are unaffected.

## 5. Proposed interim block (for the owner to decide; not applied)

X9 and Y1 (class c), in the web: refuse a period whose đến ngày is before 07/10/2026 with the 5.8.3 text
"Tờ khai hiệu lực từ ngày 07/10/2026", in the period picker, when a JSON draft is opened and on XML import,
and point the user to C9/D6 (TT80). Keep the 5.8.2 limits of C9/D6 (đến ngày ≤ 01/10/2026) and X9/Y1
(từ ngày ≥ 01/07/2026) until 5.8.3 native cases confirm the wider ranges. Periods with đến ngày 02–06/10/2026,
and periods starting before 01/07/2026 and ending on or after 07/10/2026, then have no form in the web; the
message should tell the user to use HTKK 5.8.3 for them. Details in web `docs/HTKK-5.8.3-DANH-GIA.md`.

## 6. Phase 2 plan

1. **Baseline.** Add a 5.8.3 entry to `scripts/htkk-oracle-baselines.json` next to 5.8.1 and 5.8.2 (pins
   in §1–§2, Fshare `59JNEQ8M6QW4`), regenerate with `generate-htkk-oracle-baselines.py` (`--check` in
   tests). Method statuses as in §3; review the two changed Y8 bodies against the entry plan (the plan
   types L through the combo, so BX is set; LockUnlock now also resets BX of an unticked part). Workflow
   input `htkk_version` gains 5.8.3, with its own run title, concurrency group, status context
   (`@htkk583`), output branch and immutable anchor (`-htkk583`). Release dispatch unchanged.
2. **Cases.** Rerun every launched case on 5.8.3. Expected:
   - `02NTNN-TT89-two-annexes-2026` and `04NTNN-TT89-one-subcontractor-2026` fail at the period dialog
     (0718). Move them to a period with đến ngày ≥ 07/10/2026 and từ ngày not after the run date (for
     example 07/10/2026–31/10/2026), same rows.
   - New negative cases: X9/Y1 đến ngày 06/10/2026 → 0718; C9/D6 đến ngày 07/10/2026 → 0719. New positive
     cases: C9/D6 đến ngày 06/10/2026; X9/Y1 từ ngày before 01/07/2026 with đến ngày ≥ 07/10/2026.
   - Y8: a case with box (2) ticked and only II-I filled, and one with only II-II, to confirm the relaxed
     check; rerun the Y8 entry cases and the Y8 KHBS cases after the pin review.
   - All other cases should give the same trees as on 5.8.2 (`pbanDVu` 5.8.3 is one of the four service
     fields compared apart).
3. **Default.** When every launched case passes on 5.8.3, make 5.8.3 the default oracle (skipping a 5.8.2
   default). Then, if the private source branch is wanted, follow `SOURCE-EXTRACT.md` "HTKK 5.8.2" with the
   5.8.3 pins.
4. **Watch.** The next release for an active Z5/Z6 menu (01/GTGT TT89?) and for the DC_13 codes reaching an
   open 03/TNDN annex.

## 7. Not verified

- Windows behaviour of 5.8.3: nothing was run. The period and Y8 rules come from IL reading.
- Whether eTax refuses a TT89 02/NTNN or 04/NTNN with đến ngày before 07/10/2026, or a TT80 one after
  06/10/2026. Only the GDT notice and HTKK say so; the legal basis of the 07/10/2026 date was not looked up.
- The attachment `NoiDungNangCap_HTKK_5.8.3.doc` (relay 504); the notice page text was used.
- XLS formulas (xlrd compares values only); the only changed workbooks are not launched or are print
  templates.
