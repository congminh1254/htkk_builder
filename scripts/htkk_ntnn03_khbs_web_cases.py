"""Input contract data of the kê khai bổ sung (KHBS) cases of 03/NTNN (menu J1, 3.0.8, maTKhai 840; kỳ tháng).

The htkk_web producer scripts/generate-htkk-web-ntnn03-khbs-reference.mjs (docs/KE-KHAI-BO-SUNG-03-NTNN.md there) stages per case
the same files as the other KHBS cases: declaration-original.xml (the lần đầu C0), declaration-prior.xml (bổ sung lần N-1, lần 2
only) and declaration-web.xml (the bổ sung), plus manifest.json. Every file is synthetic and was reviewed byte for byte; this public
repository keeps only their sizes and SHA-256 (never the files). The checks, the native B validation and the whole-tree comparison
are those of htkk_ntnn_khbs_web_cases.py, which merges these cases (same driver mode declaration-amendment-khbs-inspect,
HtkkDeclarationKhbs.cs; non-gating observation cases on HTKK 5.8.2).

J1 has KieuKHBS 3 like I9 (dynamic MapMCT items of ThueNTNN, PL01_KHBS / PL01_1_KHBS after no annex). Its original "Nhập từ XML"
clears every rate [9] (Ntnn03TT80Nckt308.FinishImportXML: BU := getThuSuatByMa(CR, "DC_97") = ""), so every round is the original
import completed by the original editor typing the two rates again (HtkkDeclarationCasePlans.KhbsImportTick: BU34 5, BU35 2, the
rates of every file of every case): inputMode khbs-web-xml-import-tick-reexport. Kỳ 09/2026: GetHanNopToKhai (kỳ tháng) gives
20/10/2026, 24 late days to the fixed ngày lập 13/11/2026."""

PRODUCER = 'scripts/generate-htkk-web-ntnn03-khbs-reference.mjs'
EXPORTER = 'lib/htkk-ntnn01-khbs.ts'
MENUS = {'J1': ('840', '3.0.8')}
# kieuKy, kyKKhai, kyKKhaiTuNgay, kyKKhaiDenNgay of every file of the cases.
PERIODS = {'J1': ('M', '09/2026', '01/09/2026', '30/09/2026')}
IMPORT_TICK = 'khbs-web-xml-import-tick-reexport'
# Web files of htkk_web (lib/htkk-ntnn01-khbs.ts with data/htkk-03-ntnn-khbs-rules.json, static reading): the lần đầu holds the two
# rows of 03NTNN-no-rate-M10-2026 with rates 5% / 2% (ngày lập 13/11/2026); each bổ sung moves one row by one amount.
# The 01-1/KHBS key ct3_2_ten ends with the empty ct7, so it is written trimmed as HTKK exports it ("… - 15/08/2026 -", run 44101960535).
_ORIGINAL = (2485, '54ac4624a7f5465681eff4f3ae45f0776669f4c2c0a2ad32824bbe78def5829e')
_INCREASE = (5933, 'a057a99bfa6d55ca0e2ae4b5960f011f90539b27223bad8e164a3dafcf6baedd')
_LATE = {'ct3a_1': '2026-11-13', 'ct3a_2': '24'}
CASES = {
    # Row A (6), (8) 800.000.000 → 900.000.000 at 5%: (8) +100.000.000, (11) +5.000.000.
    '03NTNN-khbs-increase-M09-2026': {'producerCase': 'ntnn03-khbs-increase-m09-2026', 'menuId': 'J1', 'soLan': 1, 'web': _INCREASE, 'original': _ORIGINAL, 'prior': None, 'leafTarget': 168,
        'expected': {'rows': ['(8)', '(11)'], 'subitems': [['1052', '5000000']], 'ct10': '5000000', **_LATE, 'ct3b': '36000'}},
    # Lần 2 on the increase: row A (8) → 1.000.000.000 ((6) stays 900.000.000): (11) +5.000.000.
    '03NTNN-khbs-lan2-M09-2026': {'producerCase': 'ntnn03-khbs-lan2-m09-2026', 'menuId': 'J1', 'soLan': 2, 'web': (5936, '4c62f15525b79afea3b572ff44ffe73a64335e431a472907d1b1b9f216143259'), 'original': _ORIGINAL, 'prior': _INCREASE, 'leafTarget': 168,
        'expected': {'rows': ['(8)', '(11)'], 'subitems': [['1052', '5000000']], 'ct10': '5000000', **_LATE, 'ct3b': '36000'}},
    # Row B gets 1.000.000 miễn giảm theo hiệp định (10): (11) 6.000.000 → 5.000.000.
    '03NTNN-khbs-decrease-M09-2026': {'producerCase': 'ntnn03-khbs-decrease-m09-2026', 'menuId': 'J1', 'soLan': 1, 'web': (5968, '94a7427f5e14d32161969221a8d9cbf7ebe70f80a239d0e64ff4bc36ab245a0a'), 'original': _ORIGINAL, 'prior': None, 'leafTarget': 168,
        'expected': {'rows': ['(10)', '(11)'], 'subitems': [['1052', '-1000000']], 'ct10': '-1000000', **_LATE, 'ct3b': '-7200'}},
}
# Public HTKK catalogue texts of J1 that the native 01/KHBS / 01-1/KHBS may carry beyond the reviewed files, so that a differing export
# is still retained (as for N8): Project/Menu.xml sheet names of J1, Project/MapMCT.xml Map J1 (MauToKhai / SheetName, every MCT code,
# every caption with and without its "(n) - " prefix) and the InterfaceIni/DM_MaTM.xml name of tiểu mục 1052.
_SHEETS = ('Tờ khai', '01-KHBS', '01-1/KHBS', '03/NTNN')
_CODES = ('(8)', '(9)', '(10)', '(11)')
_CAPTIONS = ('Doanh thu tính thuế TNDN', 'Tỷ lệ % thuế TNDN', 'Số thuế được miễn giảm theo Hiệp định', 'Thuế TNDN phải nộp')
_SUBITEMS = ('Thuế thu nhập doanh nghiệp từ hoạt động sản xuất kinh doanh (gồm cả dịch vụ trong lĩnh vực dầu khí)',)
CATALOGUE_TEXTS = frozenset(_SHEETS + _CODES + _CAPTIONS + tuple(code + ' - ' + text for code, text in zip(_CODES, _CAPTIONS)) + _SUBITEMS)
for _spec in CASES.values():
    _spec['catalogueTexts'] = CATALOGUE_TEXTS
    _spec['annexParts'] = ()
    _spec['inputMode'] = IMPORT_TICK
    _spec['producer'], _spec['exporter'] = PRODUCER, EXPORTER
