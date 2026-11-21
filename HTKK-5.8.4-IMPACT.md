# HTKK 5.8.4 impact on the launched forms

Assessment date: 21/11/2026. The default oracle stays 5.8.1 (5.8.2 and 5.8.3 selectable per case); this change adds 5.8.4 as a
selectable, non-gating baseline (section 6). HTKK 5.8.4 was released on 18/11/2026. The GDT notice says it implements
Thông tư 89/2026/TT-BTC for 01/GTGT, 02/GTGT and five oil and gas forms, fixes 01/TTĐB, 01/NTNN, NCCNN and 03/TNDN, and that from
19/11/2026 declarations touched by the upgrade "sẽ sử dụng ... HTKK 5.8.4 thay cho các phiên bản trước đây". It does not say from
which period the new 01/GTGT applies. That answer comes from Menu.xml and the IL below, not from the notice.

No installer, MSI, CAB member, DLL or EXE was executed or patched. Everything was handled as inert data in a session scratchpad.
Nothing extracted from the installer is committed here, only hashes, version strings, Menu.xml attribute values, message texts and
short IL string literals.

## 0. The 01/GTGT question (period 11/2026, quý 4/2026)

**HTKK 5.8.4 routes both 01/GTGT forms for tháng 10, 11, 12/2026 and quý 4/2026.** It does not choose between them.

| Menu (5.8.4 Menu.xml) | Caption | VersionXML / MaToKhai | Validity | Period check in `frmHTKKPeriod.btnDongY_Click` |
|---|---|---|---|---|
| D1 | Tờ khai thuế GTGT (01/GTGT)(TT80/2021) | 2.8.3 / 842 | StartDate 01/06/2006, **EndDate 31/12/2026** (new; 5.8.3 had none) | `GeneralFunctions.CheckToKhaiHetHieuLuc`: D1 is new in its menu list; tháng after 12/2026 → "Tờ khai hiệu lực đến tháng 12/2026", quý after 4/2026 → "… đến quý 4/2026" |
| Z5 (new) | Tờ khai thuế GTGT (01/GTGT)(TT89/2026) | 3.0.9 / 2032, class `Gtgt01TT89` | **StartDate 01/10/2026**, no EndDate | new `GeneralFunctions.CheckToKhaiBatDauCoHieuLuc` (list `U9~X1~X2~Z7~Z8~Z2~Z3~Z4~S1~S6~S5~W3~S9~Z5~Z6~`): tháng before 10/2026 / quý before 4/2026 → "Tờ khai hiệu lực từ …" |

Both checks compare (year, month) or (year, quarter) of the chosen period with the month/quarter of the Validity date; neither
tests LoaiToKhai, so amendments follow the same limits. Nothing else in `btnDongY_Click`, `CheckPeriod`, `CheckHieuLuc`,
`CheckHLToKhaiTT80`, `CheckPeriodKhbs` or `ExistTokhaiThangQuy` prefers one menu over the other for an overlapping period
(`ExistTokhaiThangQuy` treats D1 and Z5 alike when it looks for saved monthly/quarterly files). New messages 0721/0722 ("Cho phép kê
khai từ ngày/tháng 01/2027") belong to S5 (01/LNCN-VSP) only.

So: 11/2026 → D1 (TT80) and Z5 (TT89) both accepted; quý 4/2026 → both accepted; tháng 01/2027 or quý 1/2027 → Z5 only. The app's
current 01/GTGT is D1, and its XML for 11/2026 and quý 4/2026 is still what 5.8.4 produces with D1 (section 4). Which form a taxpayer
must file for those periods is a legal question this assessment does not answer: the notice is silent and no official text on
the transition of 01/GTGT was checked here.

Confidence: high for the routing (Menu.xml values and the two IL methods read in full), not run on Windows. HTKK 5.8.5
(21/11/2026, section 8) keeps Menu.xml byte-identical and the same two methods.

## 1. Source and trust

`source-watch.yml` run [44895284718](https://github.com/congminh1254/htkk_builder/actions/runs/44895284718) (21/11/2026, dispatched
for this intake) reported `review-required` and published a not-ready private proposal; `source-update.py stage` still blocks any
unpinned version (`UNREVIEWED_VERSION`). The review itself was done by hand on inert data, as for 5.8.2 and 5.8.3:

- The GDT software page (same URL as `source-watch.py` `PAGE`) was fetched through the vn-fetch relay (HTML SHA-256
  `45b2fc38…e497`). The 5.8.4 row (18/11/2026) links **`https://www.fshare.vn/file/JT65WVCUY1WA`**; a 5.8.5 row (21/11/2026) links
  `814AQNPCA7UF`; 5.8.3 still `59JNEQ8M6QW4`.
- Archive downloaded directly with this repository's `scripts/source-candidate.py` `fetch_resource`; final host
  `download041.fshare.vn`. The 5.8.3 archive was downloaded again the same way and still matches its pin (`0f950e23…2a98`).

| Item | 5.8.3 (reviewed baseline) | 5.8.4 |
|---|---|---|
| Fshare file | `59JNEQ8M6QW4` | `JT65WVCUY1WA` |
| Archive (RAR) bytes | 89,296,848 | 90,217,392 |
| Archive SHA-256 | `0f950e23…2a98` | `90cba39cbf0a648f8840e5ba41a1a1ccbae2c50016693087af14452849d2498f` |
| Archive Last-Modified | 2026-11-12T03:07:01Z | 2026-11-18T11:34:54Z |
| Folder in archive | `HTKK_5.8.3_DLL_signed/` | **`HTKK_v5.8.4_DLL_signed/`** (with a "v") |
| `setup.exe` SHA-256 | `9fcc416f…a06c` | `12f21a822f4a2bacce684cb487a9044b00ba7e3f5e591ca0924156e10f4b1de2` |
| `HTKK.msi` SHA-256 | `491c3fe7…2a60` | `d2709ada740ea3f57ccc01c7ef04527c4cbe9db86a72f2abf0380c834e3ecb2f` |
| `Data1.cab` SHA-256 | `277f6792…385e` | `f0efb2fc785533c500f80663a503ca4e302ba03fe4fd18216aeeab1b3aaf3479` |
| MSI ProductVersion / ProductCode | 4.2.2 / `{53B9335C-…-84E55F97929D}` | same |
| Media LastSequence | 4781 | 4835 |
| `Project/HTKK.exe.config` VERSION | 5.8.3 | **5.8.4** |
| MSI File rows / size match / MsiFileHash MD5 match / versioned without MsiFileHash | 4781 / 4781 / 4748 / 33 | **4835 / 4835 / 4802 / 33** |

**Authenticode** (osslsigncode 2.8). Trust file = Ubuntu CA bundle plus GlobalSign Code Signing Root R45 re-downloaded from
`secure.globalsign.com` (SHA-256 `7b9d553e…df86`, unchanged); the combined file hash is now `b8ed5039…92ca` because the Ubuntu
bundle was updated. CRLs fetched over HTTPS from `crl.globalsign.com`: signer CA lastUpdate 21/11/2026 09:19:10 UTC, nextUpdate
28/11/2026; root lastUpdate 07/10/2026, nextUpdate 15/01/2027.

- `setup.exe` and `HTKK.msi` both pass, exit code 0: "Signature verification: ok", "Signature CRL verification: ok".
- Signer **Tổng Cục Thuế**, OU IT Department, VN, serial `6435F70483012A5DBC374003` (same certificate as 5.8.1–5.8.3). Issuer
  GlobalSign GCC R45 EV CodeSigning CA 2020, root GlobalSign Code Signing Root R45.
- Countersignature times: setup 18/11/2026 11:12:44 UTC, MSI 18/11/2026 11:13:04 UTC. "Timestamp is not available" for the RFC 3161
  path, as for every earlier release (legacy countersignature).
- The 5.8.3 files verified the same way in the same session, as a control.

Same caveats as before: the CAB is trusted only through the signed MSI's File/MsiFileHash tables (legacy MD5), and 33 versioned
files (HTKK.exe and the DLLs among them) have no MsiFileHash.

The notice page (HTML SHA-256 `c2b93b01…3c55`) was read through the relay. Its attachments `ThongBaoNangCap_HTKK_5.8.4.doc` and
`NoiDungNangCap_HTKK_5.8.4.doc` returned a relay 504 twice; the notice text comes from the page body.

## 2. Payload diff (5.8.3 → 5.8.4)

54 files added, 0 removed, 81 changed.

- **Added**: XSD, input workbooks, control/output templates and print templates of 02/GTGT TT89 (Z6), 01-8/GTGT (three kinds, Z5),
  02-8/GTGT, 01/PH, 02/LNCN-PSC, 02/LNCN-VSP, 02/TNDN-PSC, KHBS_DIA_BAN_GTGT_309, KHBS_DIA_BAN_THU_HOI_HOAN (Z5/Z6 amendments),
  KHBS_TT80_GTGT_309.xls.
- **Changed templates**: everything of 01/GTGT TT89 (Z5: `01_GTGT_TT89_309.xsd` and KHBS twin, workbook, templates of 01-2, 01-3,
  01-6 ĐTVT/CSSX output, 01-7, 01-10 TT89, print) and of the oil and gas TT89 forms; `02_GTGT_TT80_251.xml` (D2, investment
  project code), `DK_Ma_du_an_DT_100.*`, `01_TTDB_ND373_293.xls`, `01_TCKT_TT89_310.xls`, `01_XSBHDC*_310.xls`, `Bang_Ke_01_1_HT.xls`.
- **Catalogues**: `Catalogue_CQThu_Dia_Ban.xml` (62 province-level tax offices get a 3-digit MaXa, one Hà Nội row added; the 3,321
  commune-level rows are identical and in the same order), `Catalogue_DM_NNKD.xml` (rows for the new PSC/VSP forms only),
  `DM_DUNG_CHUNG.xml` (DC_133 "Khác" → "KHAC" for 01-1/HT; DC_224, DC_227–DC_232, DC_238, DC_239 for 01-8/GTGT), `DM_TruongHopQuyetToan.xml`
  (W5, W6, S7 only), `ConvertVersion.xml` (DK_Ma_du_an_DT and 02_GTGT_TT80 rows).
- **Project**: `HTKK.exe`, `TAX.HTKK.Business.dll`, `TAX.HTKK.Utilities.dll` (+ `.pdb`), `Interop.TBARCODE5Lib.dll`,
  `HTKK.exe.config`, `Menu.xml`, `Message.xml`, `Button.xml`, `Map.xml`, `MapMCT.xml`, `MapMCT_TieuMuc.xml`.

No XSD, output template or control template of a launched form changed. The only input workbook of a launched form that changed is
`01_TCKT_TT89_310.xls` (Y7): every cell value is identical except `Header!B26` (0 → 1) and `Header!C26` (0 → empty) on a
"Dữ liệu bắt buộc nhập" rule row; what that row targets was not identified.

Menu.xml, menu by menu (every other entry identical):

| Menu | 5.8.3 | 5.8.4 |
|---|---|---|
| D1 01/GTGT TT80 | StartDate 01/06/2006, no EndDate | **EndDate 31/12/2026** |
| D2 02/GTGT TT80 | StartDate 01/01/2021, no EndDate | **EndDate 31/12/2026** |
| Z5 01/GTGT TT89 | — | **new**, 3.0.9, StartDate 01/10/2026; sheets tờ khai, 01-2, 01-3, 01-6 (CSSX, ĐTVT), 01-7, 01-8 (xuất khẩu, 5%, giải thể/phá sản; big-data), PL NQ 204, 01-KHBS, 01-1/KHBS |
| Z6 02/GTGT TT89 | — | **new**, 3.0.9, StartDate 01/10/2026 |
| S1, S5, S6, W3 | — | new oil and gas TT89 forms, StartDate 18/11/2026 |
| S9 01/PTHU-PSC TT89 | — | new, StartDate 01/10/2026 |
| E9 01/PTHU-DK | no EndDate | EndDate 30/09/2026 |
| R6, R9 (NĐ 373 dầu khí) | no EndDate | EndDate 31/10/2026 |

New messages: 0720 "Tờ khai hiệu lực đến ngày 17/11/2026" (R6/R9 lần xuất bán), 0721 "Cho phép kê khai từ ngày 01/01/2027", 0722
"Cho phép kê khai từ tháng 01/2027" (both S5 only).

The notice items, against the diff:

1. TT89 01/GTGT, 02/GTGT and five oil and gas forms: Z5, Z6, S1, S5, S6, S9, W3 above.
2.1 01/TTĐB ND 373: `01_TTDB_ND373_293.xls` changed. Not launched.
2.2 01/NTNN, NCCNN (Y8), data shown when opened from tra cứu: the LockUnlock change in section 3.
2.3 03/TNDN TT80, chỉ tiêu (5): no byte change found in N8's own files or class; DC_13 already gained the codes in 5.8.3.

## 3. IL diff

Method: the same token-normalised comparison as before (operands resolved to names and literals, branch targets masked, compiler
closure, cached-delegate, `$$method` and TypeSpec names masked; closures grouped by enclosing method), in the scratchpad with a small
CIL reader over `dnfile`. Scripts not committed. The reader reproduces all 55 method pins of the 5.8.3 baseline (token, IL size,
IL SHA-256) before it is used on 5.8.4.

| Assembly | Methods (non-closure, 5.8.3 → 5.8.4) | Really changed |
|---|---|---|
| HTKK.exe | 1,694 → 1,694 | 57, almost all gated on Z5/Z6 or the new oil and gas menus (below) |
| TAX.HTKK.Business.dll | 11,782 → 11,958 (+177 new: Gtgt01TT89, Gtgt02TT89, Ph01TT89, LnclVsp02/LnclPsc02/TndnPsc02 TT89, GeneralFunctions) | 49 |
| TAX.HTKK.Utilities.dll | 1,608 → 1,617 | 3 (`HTKKWinDictionaryDiaDanh` ctor/cctor, `HTKKTraCuuImpl.GetListDataSelect`) + new `CoQuanThuDiaBan` |

### Changes that reach launched forms

1. **D1 end of validity** (section 0): `CheckToKhaiHetHieuLuc` and the `btnDongY_Click` list gain `R9~R6~E9~D1~D2~`.
2. **`Ntnn01TT89Nckt309` (Y8)**: `LockUnlock` takes a fifth argument and now calls `LockUnLockColsInTable(…, lock, reset = arg,
   header = false)` instead of `(…, lock, true, true)`; `AutoBindData_0` (opening a declaration) passes false, `ButtonClick_0`
   (ticking part I/II) passes true. Opening a saved or imported Y8 no longer resets the unchosen part to template defaults, and the
   tables' header static cells are no longer locked or unlocked. For the same input the export is the same.
3. **`frmWinToKhai.winFpSpread_CellChange`** (table branch of the commune controls): after control 101 (mã xã) changes in a non-G2
   menu, the row's control 102 combobox is rebuilt from `Catalogue_CQThu_Dia_Ban`; control 102 writes `CoQuanThu.Ma` instead of
   reading ParentValue. No launched 5.8.4 template has a control 102 cell; only U5 3.1.0 has control 101, where the new call finds no
   102 cell and does nothing.
4. **`frmWinToKhai.ProcessCmdKey`** gains Z5 and Z6 branches; **`winFpSpread_EnterCell`** gains a Z5 branch; **`frmWinSelectPhuLuc`**
   checks 0716 (one 01-8/GTGT) for Z5. All gated on MenuID.
5. **KHBS code** (`*_01_KHBS`, `WinDoWorkEvent` export/import/save/barcode, `WinFnProcess`): the shared list
   `D1,N8,G9,…,Z8,Z5,Z8` loses Z5, which moves to a separate `Z5,Z6,` branch with the new `KHBS_01_DIA_BAN_THU_HOI_HOAN` templates.
   D1's KHBS path is unchanged; several methods gain null checks after `FirstOrDefault`. `RemoveTableF7IfNull` changes only for menus
   I7, I4, C7, I8, C8, S1, S5, S6, S9, W3.
6. `GetPrefix` writes 584; `xmlExportTTinChung` adds S6, S7 to its list; `CheckPeriod`, `CheckedChanged`, `LoadPhuLucSpread`,
   `SetLayout*` gain branches for the new oil and gas menus and Z6.

`Gtgt01TT80Nckt283` (D1), `Gtgt04TT80*` (D4), `Gtgt04TT89Nckt309` (Z3), `Tndn03TT80Nckt294` (N8), `TncnKk05TT80Nckt293`,
`TncnKk05TT89Nckt309`, `TncnQtt02TT80Nckt273`, `TncnQtt05TT80Nckt293`, the NTNN classes other than Y8, BCTC, `Tts01TT40*` (G7),
`Tckt01TT89Nckt310` (Y7) and `CnkdHkd01TT50Nckt310` (U5) have the same instructions as in 5.8.3.

## 4. Classification per launched form

Classes as in the earlier assessments: (a) unchanged; (b) changed in 5.8.4 but our output is still what 5.8.4 produces, or we are
stricter; (c) 5.8.4 would refuse or alter our output; (d) superseded for some periods.

| Menu | Form (open scope) | Class | Evidence |
|---|---|---|---|
| D1 | 01/GTGT TT80 + 01-2, 01-6 (CSSX, ĐTVT), 01-10, KHBS | **(d)** from tháng 01/2027 / quý 1/2027; (a) for current periods | Templates, XSD and `Gtgt01TT80Nckt283` identical; 5.8.4 still opens D1 for tháng 10–12/2026 and quý 4/2026, next to Z5. The web allowed D1 for 2027 periods, which 5.8.4 refuses; the web now refuses them too (htkk_web `lib/htkk-period-end-rules.ts`). |
| D4 | 04/GTGT TT80 | (a) | |
| Z3 | 04/GTGT TT89 | (a) | Template and workbook pins identical. |
| N8 | 03/TNDN + 03-1A/1B/1C/2/5 | (a) | See notice item 2.3. |
| L7, Z8 | 05/KK-TNCN TT80, TT89 + 05-1/PBT + KHBS | (a) | |
| B8 | 02/QTT-TNCN + 02-1 + KHBS | (a) | |
| B9 | 05/QTT-TNCN + 05-1/2/3 | (a) | |
| I9 | 01/NTNN TT80 + KHBS | (a) | |
| Y8 | 01/NTNN, NCCNN TT89 + KHBS lần 1 | (b) | Section 3.2: same export for the same input; opening a saved file keeps its data. Three entry pins changed. |
| C9, D6, X9, Y1 | 02/NTNN, 04/NTNN TT80/TT89 | (a) | `CheckHLToKhaiTT80` and `CheckPeriodKhbs` change only their menu list (S7, W5, W6 added); 0718/0719 unchanged. |
| J1 | 03/NTNN | (a) | |
| U5 | 01/CNKD TT50 3.1.0 + PL 01, PL 03 + KHBS | (a) | Section D reads `Catalogue_CQThu_Dia_Ban` by commune code; those rows are identical. |
| G7 | 01/TTS TT40 | (a) | |
| Y7 | 01/TCKT TT89 3.1.0 + KHBS | (b?) | Output template and XSD identical; one Header rule cell of the input workbook changed (section 2). Needs a 5.8.4 case. |
| A2, 78 | BCTC TT133 B01a, TT200 năm | (a) | |

## 5. Method pins (`scripts/htkk-oracle-baselines.json`, entry 5.8.4)

All 55 pins of the 5.8.3 entry resolve in 5.8.4. Raw IL hashes change for all but three (`y8-entry-cellchange`,
`u5-310-tick-capnhat`, `u5-310-tick-child-column` are raw-identical).

- **Really changed, reviewed against the plans and accepted for 5.8.4 only (changed-reviewed):** `y8-entry-autobind` (352 → 353),
  `y8-entry-buttonclick` (334 → 336), `y8-entry-lockunlock` (90 → 93), `y8-entry-grid-cellchange` (25029 → 24983),
  `y8-entry-f5-row` (9939 → 10113). The review notes are in the JSON. The LockUnlock review rests on the plan's own lock check
  reading row columns C..BH only; a 5.8.4 run of the Y8 entry cases is still the proof.
- **Same body as the reviewed 5.8.3 one:** `y8-entry-getcols`, `y8-entry-cellchange` (changed-reviewed kept); every
  token-renumbered pin; the later-release plan pins (u5-310-tick, pbt-582, gtgt04tt89-582, ntnn03-582). The grid CellChange and
  EnterCell bodies they share changed only in branches no launched template reaches (section 3.3, 3.4); their reviews say so.
- File pins: HTKK.exe `22d05763…f495`, config `33a528eb…2bd4`, Business `2250c8ad…62bb`, Utilities `a86213e0…4e80`, Menu.xml
  `bf3cfca4…87fd`, Message.xml `181a02a2…e964`, NNKD `d022f85c…6cd1`, DM_DUNG_CHUNG `ba10d728…5488`; `01_GTGT_TT80_283.xls`,
  `04_GTGT_TT89_309.xml`, `04_GTGT_TT89_309.xls` unchanged.
- The archive folder name changed to `HTKK_v5.8.4_DLL_signed`; `generate-htkk-oracle-baselines.py` now accepts that spelling (each
  version still pins its exact name, and the probe extracts from the pinned folder).

## 6. Selectable 5.8.4 oracle (this change)

`htkk_version` gains 5.8.4 with run title ` [HTKK 5.8.4]`, concurrency and output suffix `-htkk584`, status context `@htkk584`; the
PowerShell oracle parameters accept it. Default oracle unchanged (5.8.1), release dispatch unchanged (no committed case names
5.8.4). `probe-htkk-windows.yml` runs only on `refs/heads/main` (`readiness: if: github.ref == 'refs/heads/main'`), so no 5.8.4 run
is possible until this commit reaches main.

## 7. Plan

1. Merge the 5.8.4 baseline to main, then run the launched cases on 5.8.4 (`htkk_version=5.8.4`, non-gating), one per family as for
   5.8.3, plus the Y8 entry cases (three changed entry pins) and one Y7 case (changed Header rule).
2. Expected: every tree as on 5.8.3 (`pbanDVu` 5.8.4 is one of the four service fields compared apart). Negative case: D1 tháng
   01/2027 → "Tờ khai hiệu lực đến tháng 12/2026".
3. Retain the raw 5.8.4 exports privately and add them to htkk_web `tests/fixtures/htkk-584-original-import` to open 5.8.4 import
   per menu (`HTKK584_IMPORT_MENUS`).
4. 01/GTGT TT89 (Z5): plan in htkk_web `docs/HTKK-5.8.4-DANH-GIA.md`.

## 8. HTKK 5.8.5 (21/11/2026), seen during this intake

Fshare `814AQNPCA7UF`, archive SHA-256 `b8707ec635355ee72fc9f76f1873e56191183c15f03eb6f2e6f62c7d11e8ba1f` (90,224,953 bytes), folder
`HTKK_v5.8.5_DLL_signed`, setup `e4b79561…5ac8`, MSI `828bc698…1c5c`, CAB `a9887d6b…14ab`; Authenticode and CRL pass, same signer;
4835 / 4835 / 4802 / 33. **Menu.xml and Message.xml are byte-identical to 5.8.4**, and `CheckToKhaiHetHieuLuc` /
`CheckToKhaiBatDauCoHieuLuc` keep the same menu lists, so the 01/GTGT answer is the same. 23 files changed, among them
`01_NTNN_NCCNN_TT89_309.xls` (Y8, launched) and `Ntnn01TT89Nckt309.checkTKChinh` / `LockUnlock` (the notice: số hợp đồng and ngày hợp
đồng required in mục I, số tiền thanh toán > 0). Not pinned here; it needs its own intake.

## 9. Not verified

- Windows behaviour of 5.8.4: nothing was run; every rule above comes from Menu.xml and IL reading.
- Which 01/GTGT form eTax accepts or requires for tháng 10–12/2026 and quý 4/2026. HTKK offers both; the legal transition rule for
  01/GTGT was not looked up in an official text during this intake.
- The notice attachments (relay 504).
- What `Header!B26` of the Y7 workbook validates.
- XLS formulas (xlrd compares values only).
