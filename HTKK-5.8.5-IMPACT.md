# HTKK 5.8.5 impact on the launched forms

Assessment date: 21/11/2026. The default oracle stays 5.8.1 (5.8.2–5.8.4 selectable per case); this change adds 5.8.5 as a
selectable, non-gating baseline (section 5). HTKK 5.8.5 was released on 21/11/2026, three days after 5.8.4. The Cục Thuế notice says it
"cập nhật một số nội dung phát sinh trong quá trình triển khai HTKK 5.8.4" and that from 20/11/2026 declarations touched by it
"sẽ sử dụng ... HTKK 5.8.5 thay cho các phiên bản trước đây".

No installer, MSI, CAB member, DLL or EXE was executed or patched. Everything was handled as inert data in a session scratchpad.
Nothing extracted from the installer is committed here, only hashes, version strings, Menu.xml/MapMCT attribute values, message
texts and short IL string literals.

## 0. Answer first

- **Main declarations of every launched form: for the same input, the exported XML is the one 5.8.5 writes.** No XSD, output
  template, control template or Menu.xml entry of a launched form changed; Menu.xml and Message.xml are byte-identical to 5.8.4.
- **01/NTNN, NCCNN TT89 (Y8) changed in three ways** (section 3):
  1. `checkTKChinh` now requires (3) số hợp đồng and (4) ngày hợp đồng in ThueNTNN (mục I) and (5) số tiền thanh toán > 0 in every
     checked table; it no longer tests the ngày hợp đồng date (E_33, E_36). Files that 5.8.4 accepted with an empty số hợp đồng,
     ngày hợp đồng or a zero số tiền are refused by 5.8.5. The XML of a valid declaration is unchanged.
  2. `LockUnlock` clears the tables of the part not chosen (`RemoveDataOfTable`), also when a declaration is opened.
  3. **KHBS of mục II** (MapMCT_TieuMuc.xml, MapMCT.xml): ThueNCCNN [9]/[13] go to tiểu mục 1749/1099 and ThueCNKCT [9]/[13] to
     1701/1003 instead of 1052 for all four, and the ThueCNKCT items (10)–(13) now read `ThueTNCN/…`, the element the tờ khai
     writes, so a change of thuế TNCN of a cá nhân reaches 01-1/KHBS. **A Y8 bổ sung with mục II exported by the web (verified on
     5.8.2) differs from what 5.8.5 writes.** Mục I (ThueNTNN) KHBS is unchanged.
- The 01/GTGT answer of the 5.8.4 assessment stands (D1 and Z5 both open for tháng 10–12/2026 and quý 4/2026).

## 1. Source and trust

The GDT software page (relay vn-fetch, HTML SHA-256 `45b2fc38…e497`) lists 5.8.5 on 21/11/2026 with
**`https://www.fshare.vn/file/814AQNPCA7UF`**. Downloaded with `scripts/source-candidate.py` `fetch_resource`. The source-watch run
of this morning, [44895284718](https://github.com/congminh1254/htkk_builder/actions/runs/44895284718), already saw a not-pinned
release and stopped at `review-required`; no workflow was run for this pass.

| Item | 5.8.4 (reviewed) | 5.8.5 |
|---|---|---|
| Fshare file | `JT65WVCUY1WA` | `814AQNPCA7UF` |
| Archive (RAR) bytes | 90,217,392 | 90,224,953 |
| Archive SHA-256 | `90cba39c…498f` | `b8707ec635355ee72fc9f76f1873e56191183c15f03eb6f2e6f62c7d11e8ba1f` |
| Folder in archive | `HTKK_v5.8.4_DLL_signed/` | `HTKK_v5.8.5_DLL_signed/` |
| `setup.exe` SHA-256 | `12f21a82…1de2` | `e4b795616eec5880df9939a35e4bbd5b04b873d79ddf1e13eb0700fcce845ac8` |
| `HTKK.msi` SHA-256 | `d2709ada…cb2f` | `828bc698206842c1073731c1c81ca8c8c0e8b91bc4822ddbfe05852b5b6e1c5c` |
| `Data1.cab` SHA-256 | `f0efb2fc…3479` | `a9887d6b1956e623c6797f785a10862b523f283fead144df690924bd825114ab` |
| MSI ProductVersion / ProductCode / LastSequence | 4.2.2 / `{53B9335C-…}` / 4835 | same |
| `HTKK.exe.config` VERSION | 5.8.4 | **5.8.5** |
| MSI File rows / size match / MD5 match / versioned without MsiFileHash | 4835 / 4835 / 4802 / 33 | **4835 / 4835 / 4802 / 33** |

**Authenticode** (osslsigncode 2.8, same trust file and CRLs as the 5.8.4 review of the same day: signer CA CRL lastUpdate
21/11/2026 09:19:10 UTC): `setup.exe` and `HTKK.msi` pass with exit code 0, "Signature verification: ok", "Signature CRL
verification: ok". Signer Tổng Cục Thuế, serial `6435F70483012A5DBC374003`. Countersignature times 21/11/2026 05:13:02 UTC (setup)
and 05:13:16 UTC (MSI). Same caveats as before (CAB trusted through legacy MD5, 33 versioned files without MsiFileHash).

The notice page (HTML SHA-256 `fab459af…0426`) was read through the relay; its attachments returned a relay 504.

## 2. Payload diff (5.8.4 → 5.8.5)

0 files added, 0 removed, 23 changed.

| File | What changed |
|---|---|
| `Project/HTKK.exe` (+ `.pdb`), `TAX.HTKK.Business.dll` (+ `.pdb`), `TAX.HTKK.Utilities.dll` (+ `.pdb`) | section 3 |
| `Project/HTKK.exe.config` | VERSION 5.8.5 |
| `Project/Interop.TBARCODE5Lib.dll` | barcode interop, not pinned |
| `Project/Button.xml` | G2: Xoa 0 → 1 |
| **`Project/MapMCT.xml`** | Y8 ThueCNKCT items (10)–(13): MCTPath `ThueTNDN/ct10…ct13` → `ThueTNCN/ct10…ct13` |
| **`Project/MapMCT_TieuMuc.xml`** | Y8 ThueNCCNN `ThueGTGT/ct9` 1052 → 1749, `ThueTNDN/ct13` 1052 → 1099; ThueCNKCT `ThueGTGT/ct9` 1052 → 1701, `ThueTNDN/ct13` (1052) → `ThueTNCN/ct13` 1003. ThueNTNN rows unchanged (1701, 1052). |
| **`InterfaceTemplates/excel/01_NTNN_NCCNN_TT89_309.xls`** | `Header!E25` "Dữ liệu bắt buộc nhập" → "Nhập số >0" (the E_25 message); nothing else |
| `InterfaceTemplates/excel/01_GTGT_TT89_309.xls`, `02_GTGT_TT89_309.xls`, `InterfaceTemplates/xml/01_8_{1,2,3}_GTGT_TT89_309.xml`, `02_8_GTGT_TT89_309.xml` | Z5/Z6 01-8 rules (notice item 2). Not launched. |
| `01_BKNT_KTNT_TT89_309.xls` | "Thuế tỉnh" → "Tỉnh/TP", a note (notice item 4). Not launched. |
| `Bang_Ke_01_1_HT.xls` | cell values identical (formatting). Not launched. |
| `InterfaceIni/Catalogue_CQT_Dia_Ban.xml` | 63 rows: province-level offices get a 3-digit MaXa (`###10100###…` → `101###10100###…`), and one commune row `20115124###20118` becomes `20118124###20118` (Xã Khuôn Lùng, Tuyên Quang; the commune catalogue still lists the xã as 20115124) |
| `InterfaceIni/DM_DUNG_CHUNG.xml` | DC_229 (cửa khẩu, 108 → 358 items) and DC_231 (+1), both 01-8/GTGT. Not launched. |
| `InterfaceIni/ConvertVersion.xml` | DK_Ma_du_an_DT row VersionApp 583 → 585 |

Notice items, against the diff: 1 (01/NTNN TT89: số và ngày hợp đồng required in mục I, số tiền thanh toán > 0) = section 3.1; 2
(01/GTGT TT89 01-8 mục 4a no longer required) = the Z5 workbooks/templates; 3 (02/GTGT dự án đầu tư) = `Gtgt02TT89Nckt309`,
`WinFnProcess.convertDuLieuDuAnDauTu_Stt*`; 4 (01/BKNT-KTNT) = its workbook; 5 (01-1/HT "KHAC") = `Dnht01Nckt286.Validate_1`. The
notice does not mention the Y8 KHBS tables or the LockUnlock change.

## 3. IL diff

Same token-normalised method as for 5.8.4.

| Assembly | Really changed (non-closure) |
|---|---|
| HTKK.exe | menu lists gain S8 (`GetFileName*`, `GetDataFileNameExtend`, `SpreadPrint2.printDoc_PrintPage`); `GetPrefix` 585; `frmHTKKPeriod_Load`, `frmTraCuuToKhai..ctor` (dự án đầu tư conversion); **`frmHTKKPeriod.loadDefaultTinhCqtTheoDiaBan` / `axfpsPhuLuc_ButtonClicked` (Y7, 3.3)**; `CheckHLToKhaiTT80`, `CheckPeriodKhbs` (list literal only, same menu set) |
| TAX.HTKK.Business.dll | **`Ntnn01TT89Nckt309.checkTKChinh`, `.LockUnlock` (Y8)**; `Dnht01Nckt286.Validate_1`; `Gtgt02TT89Nckt309` (`.ctor`, `AutoBindData_0`, new `ClearData_1`, `Refresh_1`); `TncnXsbhdcmgCnkd01Nckt310.dayTuPLGiamThueSangTk` (01/XSBHDCMG, not launched) |
| TAX.HTKK.Utilities.dll | `HTKKTraCuuImpl.GetListDataSelect` (menu list gains S8) |

### 3.1 `Ntnn01TT89Nckt309.checkTKChinh` (Y8)

Columns: C ct1a, L ct1b, M ct2, S ct3 số hợp đồng, W ct4 ngày hợp đồng, Y ct5 số tiền thanh toán, AE ct6 ngày thanh toán.

- New: ThueNTNN only, S empty → E_13 at S; W empty → E_13 at W.
- New: every checked table, `Convert.ToDouble(Y) == 0` → E_25 at Y; Header!E25 now reads "Nhập số >0".
- Removed: for a given W, the parse test (E_33) and the "not before today" test (E_36).
- Unchanged: C, L/BX, M (E_19), AE within the period (E_27), duplicate key (E_35), the 5.8.3 rule that skips an empty mục II table.

### 3.2 `Ntnn01TT89Nckt309.LockUnlock` (Y8)

Before the 5.8.4 `LockUnLockColsInTable` calls, `RemoveDataOfTable` runs for ThueNTNN when M6 is unticked and for ThueNCCNN,
ThueCNKCT when M8 is unticked: rows after the first are removed and the first gets its template defaults. It runs from
`AutoBindData_0` too, so a saved or imported file is opened with the unchosen part empty. The export of a declaration whose unchosen
part already holds one default row (the web always exports it that way) is unchanged.

### 3.3 Y7 period dialog (01/TCKT)

5.8.4 `loadDefaultTinhCqtTheoDiaBan` set, for Y7 only, the CQT cấp cục / chi cục combos from the taxpayer's own xã. 5.8.5 removes
that and adds it to `axfpsPhuLuc_ButtonClicked`: when the second annex row (02/BK-KTBĐS) is ticked, `pnTinhCQT` is enabled and the
CQT follows the tỉnh/xã chosen in the dialog; when unticked, the defaults of the other menus are reloaded and row 0 is ticked. This
changes the CQT the dialog proposes, not the XML of the same chosen CQT. The web takes CQT nơi nộp from the taxpayer profile; a 5.8.5
Y7 native case is needed to see the dialog defaults the driver now meets.

## 4. Classification per launched form

Classes as before: (a) unchanged; (b) changed in 5.8.5 but our output is still what 5.8.5 produces, or we are stricter; (c) 5.8.5
would refuse or alter our output.

| Menu | Form (open scope) | Class | Evidence |
|---|---|---|---|
| D1, D4, Z3, N8, L7, Z8, B8, B9, I9, J1, C9, X9, D6, Y1, U5, G7, A2, 78 | as in the 5.8.4 table | (a) | No file or method of theirs changed. `Catalogue_CQT_Dia_Ban` affects the CQT list of Xã Khuôn Lùng only (section 2). |
| Y8 | 01/NTNN, NCCNN TT89, main declaration | **(c)** before the web change, (b) after | 3.1: the web exported files with empty S/W in mục I or Y = 0, which 5.8.5 refuses. The web now refuses them; for valid input the XML is unchanged. The web keeps E_36 (stricter). |
| Y8 | KHBS lần 1, 2 with mục II | **(c)** | Section 2 MapMCT/MapMCT_TieuMuc. The web now refuses it until a 5.8.5 KHBS case matches. |
| Y8 | KHBS with mục I only | (a) | ThueNTNN rows of both map files unchanged. |
| Y7 | 01/TCKT TT89 3.1.0 + KHBS | (b?) | 3.3: dialog defaults only. Needs a 5.8.5 case. |

## 5. Method pins (`scripts/htkk-oracle-baselines.json`, entry 5.8.5)

All 55 pins resolve. Only `y8-entry-lockunlock` really changed (93 → 133 IL bytes, RemoveDataOfTable); reviewed against the Y8
entry plan (fresh declaration, M8 ticked before any row is typed, so the cleared ThueNTNN already holds its defaults) and accepted
for 5.8.5 only (changed-reviewed). Every other pin keeps the instructions of its reviewed 5.8.4 body; `y8-entry-cellchange`,
`y8-entry-grid-button`, `u5-310-tick-capnhat`, `-child-column`, `-grid-button`, `pbt-582-combo-items` are raw-identical. The checkTKChinh
change is not pinned (the plan does not depend on it), but the entry cases type every S, W and Y, so they pass the new checks.

File pins: HTKK.exe `21ca70f5…2728`, config `b1ab2fcc…ca91`, Business `43d8a997…ff4a`, Utilities `da9b75bc…a755`, DM_DUNG_CHUNG
`e0bbc67f…8bfc`; Menu.xml, Message.xml, NNKD, `01_GTGT_TT80_283.xls`, `04_GTGT_TT89_309.*` unchanged from 5.8.4.

Selectable like 5.8.4: `htkk_version` gains 5.8.5, run title ` [HTKK 5.8.5]`, suffix `-htkk585`, context `@htkk585`. Default oracle
and release dispatch unchanged. `probe-htkk-windows.yml` runs only on main.

## 6. Native cases to run on 5.8.5 (once the pin is on main)

Non-gating, `htkk_version=5.8.5`, after a release of the web commit that carries the Y8 changes:

1. Y8 entry: `01NTNN-NCCNN-entry-M10-2026`, `01NTNN-NCCNN-entry-part-II1-M10-2026`, `01NTNN-NCCNN-entry-part-II2-M10-2026` (LockUnlock
   pin changed; every row has S, W, Y).
2. Y8 lần phát sinh: `01NTNN-NCCNN-occurrence-D20-10-2026`.
3. Y8 KHBS: `01NTNN-NCCNN-khbs-part1-M10-2026`, `01NTNN-NCCNN-khbs-lan2-M10-2026` (mục I, expected unchanged) and
   `01NTNN-NCCNN-khbs-part2-M10-2026` (mục II: expected new tiểu mục 1749/1099/1701/1003; the case's pinned web file is the 5.8.3-rule
   one, so a mismatch at exactly the tiểu mục leaves is the expected result until a 5.8.5-rule producer case is added).
   `01NTNN-NCCNN-khbs-part1-nodate-M10-2026` (W empty) is now refused by 5.8.5 by design; run it once to confirm the E_13.
4. Y7: `01TCKT-310-hop-tac-kd-two-individuals-Q4-2026`, `01TCKT-310-bds-three-lessors-M10-2026` (dialog defaults, 3.3).
5. One case per other family as in the 5.8.4 plan, for the import evidence (`HTKK585_IMPORT_MENUS`).

## 7. Not verified

- Windows behaviour of 5.8.5: nothing was run.
- Whether the Catalogue_CQT_Dia_Ban row 20118124 is a data error (the commune catalogue keeps 20115124).
- What HTKK does with an empty Y (Convert.ToDouble("") throws); the web treats empty as 0.
- The notice attachments (relay 504).
