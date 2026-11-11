# HTKK 5.8.2 impact on the launched forms

Assessment date: 11/11/2026. This is an assessment only: no builder or web behaviour changes.
The oracle for the web app and the native harness is still **HTKK 5.8.1**. HTKK 5.8.2 was
released on 05/11/2026, and the GDT notice says that from that date, declarations touched by
the upgrade "sẽ sử dụng ... HTKK 5.8.2 thay cho các phiên bản trước đây".

No installer, MSI, CAB member, DLL or EXE was executed or patched. Everything was handled as
inert data in a session scratchpad. Nothing extracted from the installer is committed here,
only hashes, version strings, Menu.xml attribute values, XSD element names and short IL
string literals.

## 1. Source and trust

The download used the same route as 5.8.1. The release row on the official GDT software page
(`https://www.gdt.gov.vn/wps/portal/home/hotrokekhai?1dmy&current=true&urile=wcm:path:/gdt+content/sa_gdt/htkk/soft_sup_declare`)
was fetched through the vn-fetch relay because www.gdt.gov.vn resets direct TLS. In that row,
5.8.2 (dated 05/11/2026) has the `linkDown` href **`https://www.fshare.vn/file/WYSRASTITCWB`**.
The 5.8.1 row still points to the pinned `TPW3FMLVAJL1`. The archive was then downloaded
directly (no relay needed) with this repository's `scripts/source-candidate.py`
`fetch_resource` (URL policy, redirect checks, size bounds). The final host was
`download034.fshare.vn`.

| Item | 5.8.1 (baseline, re-downloaded) | 5.8.2 |
|---|---|---|
| Fshare file | `TPW3FMLVAJL1` | `WYSRASTITCWB` |
| Archive (RAR5) bytes | 86,398,816 | 89,262,341 |
| Archive SHA-256 | `5d52c06595e933a3b246480785d5d4010fad669baed6fb38311f8a09b20e1e95` (= pin) | `51baf5c8cea7f2d688476c611325e000bec2cbd3dff42f593b711cbe5863d424` |
| Archive Last-Modified | 2026-10-16T02:37:18Z | 2026-11-05T01:23:55Z |
| Folder in archive | `HTKK_5.8.1_DLL_signed/` | `HTKK_5.8.2_DLL_signed/` |
| `setup.exe` SHA-256 | `19394e89…2d936` (= pin) | `1c2612d37176b6e02401e2e8b43c247490a7e8a971ef14144c8b9a5e84eb0efb` |
| `HTKK.msi` SHA-256 | `7c1da251…29080` (= pin) | `17c21f3ccf8c0bc6618b1b049ad7ee0328cc1bf8e914c15dbbfe7946b7c0fd73` |
| `Data1.cab` SHA-256 | `00669905…c3744` (= pin) | `5427c6632d5b60b15440e504effd314f050a56e66d4b2178355ee34b261b530c` |
| MSI ProductVersion / ProductCode | 4.2.2 / `{53B9335C-0849-4958-9E88-84E55F97929D}` | same (not a business version) |
| `Project/HTKK.exe.config` VERSION | 5.8.1 | **5.8.2** |
| MSI File rows / size match / MsiFileHash MD5 match / no MsiFileHash | 4526 / 4526 / 4493 / 33 | **4781 / 4781 / 4748 / 33** |

**Authenticode** was checked with osslsigncode 2.8 and a private trust file: the Ubuntu CA
bundle plus GlobalSign Code Signing Root R45, downloaded over HTTPS from
`secure.globalsign.com`. Its SHA-256 is `7b9d553e…df86`, the same value as the 5.8.1
verification. The signer CRL was fetched over HTTPS from `crl.globalsign.com`
(lastUpdate 11/11/2026 12:20:38 UTC, nextUpdate 18/11/2026). Results:

- Both `setup.exe` and `HTKK.msi` pass with exit code 0: digest, chain and CRL are OK.
- Signer: **Tổng Cục Thuế**, OU IT Department, VN. Serial `6435F70483012A5DBC374003`, the
  same certificate as 5.8.1.
- Issuer: GlobalSign GCC R45 EV CodeSigning CA 2020. Root: GlobalSign Code Signing Root R45.
- Countersignature times: setup 05/11/2026 01:06:13 UTC; MSI 05/11/2026 01:06:28 UTC.
- osslsigncode prints "Timestamp is not available" for the RFC 3161 path. It prints exactly
  the same thing for the pinned 5.8.1 files (legacy Authenticode countersignature), so this
  is parity, not a regression.

The same caveats as 5.8.1 apply. The CAB has no signature of its own; it is trusted through
the signed MSI's File/MsiFileHash tables (legacy MD5). 33 versioned files have no
MsiFileHash: HTKK.exe and the DLLs have no Authenticode of their own and remain explicit
authentication gaps.

## 2. Payload diff (5.8.1 → 5.8.2)

255 files added, 0 removed, 67 changed. Changed binaries:

- `Project/HTKK.exe`, `TAX.HTKK.Business.dll`, `TAX.HTKK.Utilities.dll`,
  `Interop.TBARCODE5Lib.dll` and their `.pdb` files.
- `Menu.xml`, `Message.xml` (+0705–0715), `Map*.xml`, `Button.xml`.

Changed catalogues:

- `DM_DUNG_CHUNG`, `DM_MaTM`, `DM_TruongHopQuyetToan`, `Catalogue_DM_NNKD`, `ConvertVersion`,
  `DM_MAP_MAHH_MA_TM`, `Catalogue_012027_02`, `Catalogue_032027_02`.
- New: `Catalogue_112026_02`, `Catalogue_042027_02`, `DM_TIEU_MUC`.

New schemas (47 XSD). TT89 forms:

- 05/KK-TNCN (`05_KK_TNCN_TT89_309`) and 02/KK-TNCN.
- 05/GTGT and 01/GTGT (`01_GTGT_TT89_309`).
- 04/TKQT-TNCN and 05/QTT-TNCN (`05_QTT_TNCN_TT89_309`).
- Oil and gas: VSP and PSC forms, 01/TNS-DK, 03/TNDN-DK.

New 3.1.0 / 3.0.9 versions:

- 01/CNKD TT18 and **TT50 (`01_CNKD_HKD_TT50_310`)**.
- 01/TCKT, 01/XSBHDC, 01/XSBHDCMG and the 01/CNKD-TMĐT family.

**`01_GTGT_TT89_309` and `05_QTT_TNCN_TT89_309` are shipped (XSD, templates and the business
classes `Gtgt01TT89Nckt309` / `TncnQtt05TT89Nckt309`), but no Menu.xml entry references
them.** They are pre-staged for a later release and are not selectable in 5.8.2.

The GDT notice (fetched from the notice page; `NoiDungNangCap_HTKK_5.8.2.doc` has SHA-256
`da9e0965…fe6d8`) lists exactly the scope the diff shows:

1. TT89 forms: 03/04/05/GTGT, 02/KK-TNCN, 05/KK-TNCN, 04/NNG-TNCN, 04/TKQT-TNCN, 01/TNS-DK,
   03/TNDN-DK, 01/KD-VSP, 02/KD-VSP and 01/BKNT-KTNT.
2. NQ 43/2026/QH16 TNCN-reduction annexes:
   - Mẫu 02 for 01/TCKT (TT18 and TT89), 01/XSBHDC, 01/XSBHDCMG and 01/CNKD-TMĐT.
   - **Mẫu 01 and Mẫu 03 for 01/CNKD TT18 and TT50**.
3. NQ 45/2026/NĐ-CP: TTĐB 0% for xăng from 01/11/2026 to 31/03/2027.
4. Fixes to 02/TNDN and 04/TNDN (TT89), and **01/GTGT (TT80) PL 142/174/204: the goods/services
   value may be negative or positive**.

## 3. Method

The comparisons ran in the scratchpad (scripts not committed):

- **Menu.xml.** The `PopID=101` entries for each launched ID were compared attribute by
  attribute, including Validity and Sheet children.
- **XSD.** Compared by element tree (path, type, min/max occurrences, nillable, facets),
  walking the `xs:redefine` and `xs:extension` blocks.
- **XML/XLS templates.** XML templates were compared cell by cell (CellID / Path /
  Controltype / limits). XLS workbooks were compared on cell values with xlrd; formulas were
  not compared.
- **Catalogues.** Compared by `Map Controltype`.
- **Pins.** Every SHA-256 found in web `data/*.json` and `lib/*.ts` and in builder `scripts/`
  was checked against the changed files.
- **IL pins.** Every IL pin in web `data/*.json` (token plus methodBodySha256 or bodySha256,
  as written by `scripts/import-htkk-descriptor-declarations.py` using dnfile/dncil) was
  resolved in 5.8.1. Each of the 242 unique pinned methods matched. Each was then located in
  5.8.2 by type and method name. Raw body hashes change whenever metadata tokens are
  renumbered, and 5.8.2 adds about 1,150 methods to Business.dll. So the bodies were also
  compared **token-normalised**: operands resolved to names and literals; branch targets,
  local indices, `<PrivateImplementationDetails>` GUIDs and compiler lambda names masked.
- The four `TAX.HTKK.ComputeHash.dll` pins in `htkk-01-gtgt-signing-contract.json` did not
  resolve against the three changed assemblies. ComputeHash.dll itself is byte-identical in
  5.8.2, so those pins are unaffected.

Results for the 242 web-pinned methods:

- **212 are semantically identical.** Their raw hashes still drift because of tokens: every
  web pin into `HTKK.exe` and `TAX.HTKK.Business.dll` must be re-hashed.
- 1 differs only by lambda renaming.
- 29 really changed. Most of them only extend `~`-separated menu-ID lists for the new menus
  (S1–S9, W1, W3, W4, W7, Z1–Z8) or add the new table control 110. The changes that matter for
  launched forms are listed below.

In Business.dll, real IL changes are confined to `GeneralFunctions` (`CheckToKhaiHetHieuLuc`,
`CheckToKhaiBatDauCoHieuLuc`, large-data helpers) and to non-launched classes (04/GTGT TT89,
03/GTGT TT89, 04/NNG TT89, 01/BKNT-KTNT, Ds_tien_nop_TMDT). **The launched business classes
are unchanged**:

| Classes |
|---|
| `Gtgt01TT80Nckt283`, `Tndn03TT80Nckt294`, `TncnKk05TT80Nckt293` |
| `TncnQtt02TT80Nckt273`, `TncnQtt05TT80Nckt293` |
| `Ntnn01/02/03/04TT80`, `Ntnn01/02/04TT89` |
| BCTC, `CnkdHkd01TT50Nckt298` |

U5 is the exception: 5.8.2 points it to a **new** class, `CnkdHkd01TT50Nckt310`.

### Real changes in shared code that touch launched menus

1. **`GeneralFunctions.CheckToKhaiHetHieuLuc`**, called from
   `frmHTKKPeriod.btnDongY_Click`. This is the end-of-validity gate.
   - In 5.8.1 it applied only to `78~A1~A2~R4~C9~D6~`.
   - In 5.8.2 the list is `78~A1~A2~R4~C9~D6~Q9~M9~J5~L2~L7~D3~D4~D5~L8~I9~P1~M8~`, which adds
     **L7 and I9**.
   - For KieuKy `Q`, the period is refused when its quarter is after the quarter of Menu.xml
     `EndDate` → "Tờ khai hiệu lực đến quý 3/2026".
   - For `M`, the period is refused when its month is after the EndDate month → "Tờ khai hiệu
     lực đến tháng 09/2026".
   - Otherwise (D / D_D), the period is refused when `DenNgay` > EndDate → "Tờ khai hiệu lực
     đến 30/09/2026".
   - The check does not test LoaiToKhai, so amendments for such periods are refused too.
   - The new start-of-validity gate `CheckToKhaiBatDauCoHieuLuc` applies to
     `U9~X1~X2~Z7~Z8~Z2~Z3~Z4~`, which includes Z8 (the TT89 05/KK-TNCN).
2. **`WinDoWorkEvent.xmlExportTTinChung`** (common header).
   - For the menu list `L4~L7~…~B9~…~X9~Y1~…~Y8~…`, which in 5.8.1 already rewrote
     `NNT/tenXaNNT` and `maXaNNT`, it now also sets `NNT/tenHuyenNNT` and `NNT/maHuyenNNT` to
     `""` when those nodes exist (with new null checks). This concerns L7, B9, X9, Y1 and Y8.
   - In every 5.8.1 native fixture of these forms, both nodes are already empty (`<x />`). The
     only possible difference is `<x></x>` serialisation; the infoset is equal.
3. **`frmWinToKhai.ProcessCmdKey`** (pinned as `f5-inserts-table-row`).
   - F5 row insertion now writes `GetRowValueDefault` into the new row.
   - A 2-row cap (message 0585) appears in a branch that was previously shared with Z3/D4.
   - This affects only original-entry (typed) native cases. Impact on our Y8 entry case is
     unverified.
4. **`xmlExportTTinChungProcessNode`**: a Q9-only 2026 special case was removed. Q9 is not
   launched.
5. The other changed pins are list extensions for new menus or the new control type 110:
   `GetValueFromSelectedCell`, `winFpSpread_CellChange`, `cellChange`, `GetHTKKSheetInfo`,
   `fpSpFormatTableCellTemplate`, `ExportDataTableToTableNode`,
   `ExportDataStaticTableToXMLNode`, `WinDoWorkImportFormXml`, `CheckHLToKhaiTT80`,
   `frmHTKKPeriod_Load`, `GetPeriodInfo`, `SetLayoutToKhaiThangQuyLanPhatSinh`,
   `ResetpnVT1_2NgayThangQuyNam`, `LoadToKhai` (sheet visibility and layout). The existing
   control types and menu IDs used by launched forms keep their branches.

Catalogues used by launched forms are unchanged in content:

- In `DM_DUNG_CHUNG`, only DC_197, DC_199 (removed), DC_200 and DC_201 (codes renumbered) and
  the new DC_207–220 changed. The web uses DC_01/97/103/124/128/129/185/192.
- `DM_MaTM` changed only the names of oil and gas tiểu mục.
- `DM_TruongHopQuyetToan` changed only W1, S2 and S4.
- `Catalogue_DM_NNKD` and `ConvertVersion` have additions only.

Their file hashes still change, and they are pinned by web and builder.

## 4. Classification per launched form

The four classes:

- **(a)** Unchanged.
- **(b)** Changed in 5.8.2, but our output is still what 5.8.2 produces for the same input.
- **(c)** Our output now differs from 5.8.2's, or 5.8.2 would refuse or alter it.
- **(d)** Superseded by a new menu for some periods.

| Menu | Form | Class | Evidence |
|---|---|---|---|
| D1 | 01/GTGT TT80 (2.8.3) + 01-2 | **(b)** | The Menu entry, `01_GTGT_TT80_283` XSD, main/01-2 XML templates and `Gtgt01TT80Nckt283` IL are identical. Only `01_10_MGT_GTGT_TT80_283.xml` (MinValue 0 → −99,999,999,999,999 on `giaTriHHDVMuaVao`, `giaTriHHDV` and their totals) and the workbook's Header messages for that annex changed. We do not produce 01-10. Pinned file hashes for `01_GTGT_TT80_283.xls` and `01_10_*.xml` drift. Pre-staged `01_GTGT_TT89_309` has no menu yet (watch item). |
| N8 | 03/TNDN TT80 (2.9.4) | **(a)** for content | The Menu entry, templates and `Tndn03TT80Nckt294` are semantically identical. Only raw IL hashes in `htkk-workbook-rules.json` drift because of tokens. |
| L7 | 05/KK-TNCN TT80 (2.9.3) | **(d)** + **(c)** | `EndDate` changed from "" to **30/09/2026**. L7 is now in `CheckToKhaiHetHieuLuc`, so Q4/2026+ (and month amendments M10/2026+) are refused ("hiệu lực đến quý 3/2026"). Replacement: new **Z8** "05/KK-TNCN … (TT89/2026)", 3.0.9, MaToKhai 2036, KieuKy 14, StartDate 01/10/2026. Our web allows L7 with no end date, so it produces TT80 XML for periods 5.8.2 refuses. Header huyện blanking is (b). |
| B8 | 02/QTT-TNCN TT80 (2.7.3) | **(a)** | Nothing changed. |
| B9 | 05/QTT-TNCN TT80 (2.9.3) | **(b)** | The Menu entry, templates and class are identical. Header huyện blanking applies but the values are already empty. `TncnQtt05TT80Nckt293` raw IL pins drift (token renumbering only). Pre-staged `05_QTT_TNCN_TT89_309` has no menu yet (watch: quyết toán 2026). |
| I9 | 01/NTNN TT80 (2.5.1) | **(d)** + **(c)** | `EndDate` changed from none to **30/09/2026**, and I9 was added to `CheckToKhaiHetHieuLuc`. M10/2026+ is refused ("đến tháng 09/2026"), as is lần phát sinh after 30/09/2026 ("đến 30/09/2026"). The replacement **Y8** (TT89, from 01/10/2026) already exists and is launched. Our own launch evidence for I9 (`01NTNN-two-contractors-M10-2026`, `01NTNN-occurrence-D20-10-2026`) uses periods 5.8.2 refuses. |
| Y8 | 01/NTNN, NCCNN TT89 (3.0.9) | **(b)** | The Menu entry and class are identical. Header huyện blanking applies, already empty. The F5 row-insert change only touches typed entry. Rerun `01NTNN-NCCNN-entry-M10-2026`. |
| C9 | 02/NTNN TT80 (2.5.1) | **(a)** | EndDate 01/10/2026 was already enforced in 5.8.1. |
| X9 | 02/NTNN TT89 (3.0.9) | **(b)** | Header huyện blanking only. |
| J1 | 03/NTNN (3.0.8) | **(a)** | No EndDate. Not in the new end-validity list. |
| D6 | 04/NTNN TT80 (3.0.8) | **(a)** | EndDate 01/10/2026 unchanged. |
| Y1 | 04/NTNN TT89 (3.0.9) | **(b)** | Header huyện blanking only. |
| U5 | 01/CNKD TT50 | **(c)** | VersionXML/KHBS **2.9.8 → 3.1.0**. New class `CnkdHkd01TT50Nckt310`. New sheets 01-4 "PL 01 43/2026/QH16" (`PLuc_01_GiamTNCN_NQ43`) and 01-5 "PL 03" (`PLuc_03_PhaiNop_NQ43`). Message 0709 forbids both annexes together. The XSD `01_CNKD_HKD_TT50_310` = 2.9.8 plus the two optional annexes (`minOccurs=0`). Main and 01-1/01-3 XML export skeletons are identical. The main sheet adds UI-only cells (`chonGiamThue`, `soThueGiam`, `ct17_soThueGoc/Bu`). Validate_0 gains a new rule on the header checkboxes B_26/B_28 (exact condition not yet confirmed natively). `ConvertVersion` maps 298 → 310. HTKK writes pbanTKhaiXML from Menu.xml, so a 5.8.2 round trip of our file emits 3.1.0 where we emit 2.9.8. Our importer refuses 3.1.0 files (fails closed). |
| A2 | BCTC TT133 B01a-DNN | **(a)** | Nothing changed. |
| 78 | BCTC TT200 năm | **(a)** | EndDate 31/12/2026 unchanged. |

Cross-cutting **(c) for the tooling**: all builder pins on `HTKK.exe`, `.config`,
`Business.dll`, `Utilities.dll`, `Menu.xml`, `Message.xml` and the catalogues are invalid for
5.8.2. These pins sit in `htkk-source-extract-policy.json`, `Invoke-*Oracle.ps1`,
`HtkkGuiReferenceAutomation.cs`, `publish-*-evidence.py` and others. A native run against
5.8.2 will fail closed until they are re-pinned. The same holds for the web's IL token/body
pins and its file pins.

## 5. Specific questions

### (i) 05/KK-TNCN: from which kỳ the TT89 form is required, and what differs

**HTKK 5.8.2:**

- L7 (TT80) accepts periods up to **Q3/2026** (and months up to 09/2026 for amendments).
- **From Q4/2026** (kỳ starting on or after 01/10/2026), only **Z8** (TT89) is accepted.
- Z8 has StartDate 01/10/2026 and is gated by `CheckToKhaiBatDauCoHieuLuc`, so Q3/2026 and
  earlier must stay on L7.
- First-time monthly declarations from 04/2026 remain refused for both L7 and Z8 (0682;
  Z8 was already in that list in 5.8.1).
- Use L7 for amendments (KHBS) of Q3/2026 and earlier, and Z8 for Q4/2026 onwards.

**Law:**

- TT89/2026/TT-BTC Điều 99 khoản 1: the circular takes effect on 01/07/2026.
- Điều 100 khoản 1: declarations whose kỳ tính thuế is before 01/07/2026 use the old forms.
  Both are verified by OCR of the signed PDF at
  `https://datafiles.chinhphu.vn/cpp/files/vbpq/2026/7/89-btc.signed.pdf`, 839 pages,
  SHA-256 `952c45ff…71dc`, pages 197 and 199.
- Strictly, Q3/2026 already falls under TT89. HTKK nevertheless keeps TT80 for Q3/2026
  because the TT89 form appeared only in 5.8.2. Follow HTKK: Q3/2026 on TT80, Q4/2026 on TT89.
  This gap is noted, not resolved.

**XML/XSD differences** (`05_KK_TNCN_TT80_293.xsd`, 62 elements → `05_KK_TNCN_TT89_309.xsd`,
71 elements):

| Item | TT80 (L7) | TT89 (Z8) |
|---|---|---|
| maTKhai | 864 | 2036 |
| pbanTKhaiXML | 2.9.3 | 3.0.9 |
| KieuKy | 19 | 14 |

The main indicators are fully renumbered:

- `ct14` is the allocation flag (the boolean that was `ct15`). `ct15` and `ct16` are the
  employee counts.
- `ct17`–`ct19`: the number of people withheld from.
- `ct20`–`ct23`: taxable income.
- **New `ct24`–`ct28`**: exempt income — dầu khí, KH&CN/ĐMST, startup experts, other.
- `ct29`–`ct31`: income subject to withholding.
- **New `ct32`–`ct34`**: thu nhập tính thuế.
- **New `ct35`**: tax to withhold.
- **New `ct36`–`ct41`**: exempt tax (digital-tech and high-tech personnel, other).
- `ct42`–`ct45`: tax withheld, including the insurance-premium part.
- `ct25_1` is removed.

In annex 05-1/PBT, `ma_xa`/`ten_xa` and the `ct08a/ct21a_huyen_*` fields are replaced by
`ct08a_xa_ma`/`ct08a_xa_ten`.

A TT80 05/KK file cannot simply be relabelled: it needs a new engine and layout.

### (ii) 01/CNKD NQ 43/2026 annex: what it adds, which periods, whether mandatory

**What it adds:**

- `PLuc_01_GiamTNCN_NQ43`: rows per business location, activity and ngành, with the TNCN
  payable, the TNCN reduced and tiểu mục, plus totals.
- `PLuc_03_PhaiNop_NQ43`: claw-back and adjustment when actual revenue exceeds the threshold,
  with self-declared and declared-on-behalf rows, plus totals.
- Both are attached to U5 as sheets 01-4 and 01-5.
- Selection is driven by a new checkbox (`chonGiamThue`).
- HTKK forbids both annexes in one declaration (0709).

**Periods.** NQ 43/2026/QH16 (24/08/2026; Điều 1 khoản 1, Điều 2 khoản 1; text from
xaydungchinhsach.chinhphu.vn, SHA-256 `cf8b36d0…8389`, listed at
vanban.chinhphu.vn docid 219330):

- 30% reduction of the TNCN payable on business income of resident individuals with annual
  revenue ≤ 10 tỷ.
- Effective 24/08/2026, for the **kỳ tính thuế năm 2026 and 2027**.

**Mandatory?** NĐ 398/2026/NĐ-CP (effective 29/10/2026; Điều 2 khoản 4 as published on
xaydungchinhsach.chinhphu.vn, SHA-256 `34efe39d…ce89`):

- An individual who expects revenue ≤ 10 tỷ "kê khai giảm thuế ... theo Mẫu số 01" with the
  quarterly / six-month / annual declaration.
- If revenue exceeds 10 tỷ, Mẫu số 03 is used to pay back.
- If the reduction was not declared, it may be claimed later by khai bổ sung or at quyết toán
  (point d).

So the annex is the way to claim the reduction. It is not a validity requirement:

- In HTKK it is optional (`minOccurs=0`, the user ticks it).
- Without it the declaration stays valid, but the taxpayer pays 30% too much until amending.
- Mẫu 03 is required when the threshold is exceeded.

Our U5 cannot produce either annex.

### (iii) 01/GTGT tax-reduction annex (NQ 204/2025)

NQ 204/2025/QH15 (official full text on xaydungchinhsach.chinhphu.vn, SHA-256 `557d43ce…6daf0`):
the VAT rate is cut by 2% (to 8%) from 01/07/2025 to 31/12/2026. NĐ 174/2025/NĐ-CP
(congbao.chinhphu.vn metadata page; effective 01/07/2025) implements it.

In 5.8.2, annex 01-10 ("PL 142/2024-174/2024-204/2025", `PL_NQ142_GTGT`):

- Allows **negative** values (down to −99,999,999,999,999) for goods/services value
  (purchases `giaTriHHDVMuaVao`, sales `giaTriHHDV`) and both totals. The notice gives the
  purpose: "Cho phép nhập ... là số âm, dương".
- Changes the corresponding Header validation messages: "Chỉ nhập số >=0" becomes "Dữ liệu
  không được phép âm" on the tax columns.
- Leaves the XSD and the 01/GTGT main form unchanged.

Since our D1 does not produce 01-10, our output is unaffected (class b). Two side effects:

- U5's importer (`lib/htkk-hkd-cnkd-xml.ts`) also reads a `PL_NQ142_GTGT` part (its 01-3
  annex). U5 templates 01-3 2.9.8 and 3.1.0 are identical; whether 5.8.2 now accepts
  negative values there as well was not checked.
- A user cannot get 01-10 from us. Users with returned or adjusted goods must still use
  HTKK 5.8.2 for that annex.

The negative-value rule is supported only by the GDT notice and the template diff. The
NĐ 174/2025 body (PDF) was not read.

### (iv) Other launched forms

None of the others are affected in content: N8, B8, C9, J1, D6, A2 and 78 are (a); D1, B9,
Y8, X9 and Y1 are (b). Watch items:

- Pre-staged TT89 01/GTGT and 05/QTT-TNCN classes and XSDs point to future menus that will
  probably end D1 and B9.
- NQ 43/NĐ 398 also give a 30% **TNDN** reduction for kỳ 2026/2027. N8 (03/TNDN quyết toán
  2026) has no 5.8.2 change yet, but a later HTKK release will likely change it.

## 6. Upgrade plan (ranked by user risk)

1. **I9 periods from 10/2026 (now; filing deadline for M10/2026 is 20/11/2026).**
   - Refuse I9 for periods after 30/09/2026 (Menu.xml EndDate 30/09/2026, 5.8.2 semantics:
     month > 09/2026, day > 30/09/2026, including amendments). Point users to Y8.
   - Interim, without new verification: set the I9 descriptor `endDate` to "30/09/2026" and
     add a period check equivalent to 5.8.2 `CheckToKhaiHetHieuLuc`. If that cannot ship
     quickly, put `'I9': ['M','D']` in `HIDDEN_PERIOD_TYPES_UNTIL_VERIFIED`. That hides the
     form, though, so the end-date check is preferable.
   - Rewrite the I9 launch evidence comment: its M10 and D20/10 fixtures are no longer valid
     filings.
2. **L7 periods from Q4/2026.**
   - Same treatment: endDate 30/09/2026 with "Tờ khai hiệu lực đến quý 3/2026".
   - Q4/2026 cannot be filed until users can file it, from 01/01/2027 to 31/01/2027.
   - We have no TT89 05/KK, so tell users to use HTKK 5.8.2 (Z8) for Q4/2026.
   - Build Z8 as a new descriptor from `05_KK_TNCN_TT89_309` and verify it natively before
     January 2027.
3. **U5 01/CNKD TT50.**
   - Our 2.9.8 output differs from 5.8.2's 3.1.0, and eTax acceptance of 2.9.8 after
     05/11/2026 cannot be verified.
   - Users eligible for the NQ 43 reduction cannot claim it with us, and would overpay 30%.
   - Interim: show a notice on U5 that the NQ 43 reduction annex is not supported and that
     users should use HTKK 5.8.2 if they claim it. Consider `HIDDEN_UNTIL_VERIFIED: ['U5']`
     until a 3.1.0 native case passes.
   - Then move the contract to 3.1.0: XSD/templates `_310`, the new Validate rule on
     B_26/B_28, and the importer accepting 3.1.0. Optionally add PL 01/PL 03.
4. **Builder oracle.**
   - Add a 5.8.2 baseline alongside 5.8.1 rather than replacing it. Use the new
     archive/MSI/setup/CAB pins and counts above, the Fshare `WYSRASTITCWB` URL, and a policy
     regenerated in the private repo by `prepare-htkk-source-extract-policy.py`.
   - Re-pin every HTKK.exe/DLL/Menu/Message/catalogue hash consumer.
   - Run both versions until all launched cases pass on 5.8.2, then make 5.8.2 the default.
     GDT requires 5.8.2 from 05/11/2026, so 5.8.1 evidence no longer proves acceptance.
   - Then publish `htkk-source-5.8.2` through `source-extract.yml`.
5. **Web re-import and pins.**
   - Regenerate the web data importers against 5.8.2: Menu navigation, descriptor
     declarations, workbook rules, the taxpayer-profile IL pins (token renumbering) and the
     file pins.
   - Set `htkkVersion` to 5.8.2 only after the native reruns.
   - The 01-2/GTGT and descriptor catalogue contents are unchanged, so expect pure pin
     updates.
6. **Native cases to rerun on 5.8.2.** Run all 32 in `htkk-native-cases.json`, the 23
   descriptor cases and the 4 workbook cases. Expected outcomes:
   - `01NTNN-two-contractors-M10-2026`, `01NTNN-zero-M10-2026` and
     `01NTNN-occurrence-D20-10-2026` must now **fail at the period dialog**. Replace them with
     M09/2026 and D≤30/09/2026 variants (for example `01NTNN-two-contractors-M09-2026`,
     `01NTNN-occurrence-D20-09-2026`).
   - Add negative cases asserting the 5.8.2 refusal message for I9 M10/2026 and L7 Q4/2026.
   - `05KK-*-Q3-2026` should still pass on L7.
   - `01CNKD-TT50-revenue-two-groups-Q3-2026` should re-export with pbanTKhaiXML 3.1.0.
     Compare the leaves and add the version to the allowed differences, or move the web to
     3.1.0.
   - Add U5 cases with the PL 01 annex ticked and with the B_26/B_28 combinations.
   - Rerun `01NTNN-NCCNN-entry-*`, because of the F5 row-insert change.
   - Check L7, B9, X9, Y1 and Y8 for `<maHuyenNNT></maHuyenNNT>` and confirm the comparator
     treats it as equal to the empty element.
   - New, after a Z8 engine exists: `05KK-TT89-withheld-Q4-2026`, as XML import then
     re-export.
7. **Watch the next HTKK release** for active menus that use the pre-staged
   `01_GTGT_TT89_309` and `05_QTT_TNCN_TT89_309`, and for a 03/TNDN change under NQ 43. Each
   would supersede D1, B9 or N8 for some periods.

## 7. Not verified

- Windows behaviour of 5.8.2. Nothing was run. The refusal semantics come from IL reading;
  they need native confirmation (item 6).
- The exact condition of the new U5 Validate_0 rule on B_26/B_28 (message E_36 in a
  template we did not decode).
- Whether eTax still accepts 01/CNKD TT50 2.9.8 or TT80 05/KK and 01/NTNN files for the
  periods above.
- XLS formulas (xlrd compares values only). Templates of launched forms other than D1's
  workbook did not change byte-wise.
- Full bodies of NĐ 398/2026 and NĐ 174/2025. Government-portal summaries and metadata were
  used.
- The `ThongBaoNangCap_HTKK_5.8.2.doc` attachment on the notice page. The `NoiDungNangCap`
  file and the notice HTML were used instead.
- The 33 versioned files without MsiFileHash remain unauthenticated, as in 5.8.1.
