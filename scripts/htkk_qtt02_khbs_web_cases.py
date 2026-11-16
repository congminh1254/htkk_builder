"""Input contract data of the kê khai bổ sung (KHBS) cases of 02/QTT-TNCN TT80 (menu B8, 2.7.3; cá nhân tự quyết toán, kèm
02-1/BK-QTT-TNCN).

The htkk_web producer scripts/generate-htkk-web-qtt02-khbs-reference.mjs (docs/KE-KHAI-BO-SUNG-02-QTT-TNCN.md there) stages per
case the same files as the other KHBS cases: declaration-original.xml (the lần đầu C0), declaration-prior.xml (bổ sung lần N-1,
lần 2 only) and declaration-web.xml (the bổ sung), plus manifest.json. Every file is synthetic and was reviewed byte for byte;
this public repository keeps only their sizes and SHA-256 (never the files). The checks, the native B validation and the
whole-tree comparison are those of htkk_ntnn_khbs_web_cases.py, which merges these cases (same driver mode
declaration-amendment-khbs-inspect, HtkkDeclarationKhbs.cs; non-gating observation cases on HTKK 5.8.2).

B8 has KieuKHBS 3 in the HTKK 5.8.2 Menu.xml (the D1 path of "Tổng hợp KHBS"), so a B file carries PL01_KHBS / PL01_1_KHBS
after the case's 02-1/BK-QTT-TNCN annex; every round is the original import (cmdImportXML_Click adds every B8 annex first).
Năm 2025 only: HTKK 5.8.2 refuses đến tháng 12/2026 before 01/12/2026 (CheckTuThangDenThang 0471)."""

PRODUCER = 'scripts/generate-htkk-web-qtt02-khbs-reference.mjs'
EXPORTER = 'lib/htkk-qtt02-khbs.ts'
MENUS = {'B8': ('952', '2.7.3')}
# kieuKy, kyKKhai, kyKKhaiTuNgay, kyKKhaiDenNgay of every file of the cases.
PERIODS = {'B8': ('Y', '2025', '', '')}
ANNEX = 'PLuc_02_1_BK_QTT_TNCN'
IMPORT = 'khbs-web-xml-import-reexport'
_ORIGINAL = (3599, '1b0bfba345e5ab2122bad362fd06d6cb73237674cb98f2d56dc4fea7d5f04843')
_INCREASE = (7635, '536c0615160e91ea9eed59a37ea4fc0d4d65387098a6d95d8fc27fa2296880c2')
# Năm 2025 is due 31/03/2026 as GetHanNopToKhai reads it (KieuKy Y), ngày lập 13/11/2026: 227 late days in every case.
CASES = {
    '02QTT-khbs-increase-Y2025': {'producerCase': 'qtt02-khbs-increase-y2025', 'menuId': 'B8', 'soLan': 1, 'web': _INCREASE, 'original': _ORIGINAL, 'prior': None, 'leafTarget': 272,
        'expected': {'rows': ['[20]', '[21]', '[31]', '[32]', '[42]'], 'subitems': [['1001', '3000000']], 'refund': [], 'ct10': '3000000', 'ct13': '0', 'ct3a_1': '2026-11-13', 'ct3a_2': '227', 'ct3b': '204300'}},
    '02QTT-khbs-lan2-Y2025': {'producerCase': 'qtt02-khbs-lan2-y2025', 'menuId': 'B8', 'soLan': 2, 'web': (7637, 'd21ed222b7c25f52637092a65f36426e03d588553a6ee609e610e262e2b082b3'), 'original': _ORIGINAL, 'prior': _INCREASE, 'leafTarget': 272,
        'expected': {'rows': ['[20]', '[21]', '[31]', '[32]', '[42]'], 'subitems': [['1001', '1440000']], 'refund': [], 'ct10': '1440000', 'ct13': '0', 'ct3a_1': '2026-11-13', 'ct3a_2': '227', 'ct3b': '98064'}},
    '02QTT-khbs-decrease-Y2025': {'producerCase': 'qtt02-khbs-decrease-y2025', 'menuId': 'B8', 'soLan': 1, 'web': (7104, '5df997694c4aea2a0994105ef77301401fab73d026ce8b72ed022517d91ad667'), 'original': _ORIGINAL, 'prior': None, 'leafTarget': 246,
        'expected': {'rows': ['[33]', '[34]', '[42]'], 'subitems': [['1001', '-1000000']], 'refund': [], 'ct10': '-1000000', 'ct13': '0', 'ct3a_1': '2026-11-13', 'ct3a_2': '227', 'ct3b': '-68100'}},
    # Hoàn qua chuyển khoản on both versions (the reviewed transfer of 02QTT-refund-transfer-Y2025): [34] 20tr → 22tr, [46] 14,12tr
    # → 16,12tr; [45] (LoaiThue 2) goes to Muc_III.
    '02QTT-khbs-refund-Y2025': {'producerCase': 'qtt02-khbs-refund-y2025', 'menuId': 'B8', 'soLan': 1, 'web': (7945, 'f9c305efa68e4d8259f44e3e2842d33d88f9d89a5f31af3fe438120105f2eb9a'), 'original': (3819, '12924fb7cfcec03807839fe4f9cea3e3254b9c467ed59a8007fc63b045d18b06'), 'prior': None, 'leafTarget': 272,
        'expected': {'rows': ['[33]', '[34]', '[44]', '[45]', '[46]'], 'subitems': [['1001', '-2000000']], 'refund': [['1001', '2000000']], 'ct10': '-2000000', 'ct13': '2000000', 'ct3a_1': '2026-11-13', 'ct3a_2': '227', 'ct3b': '-136200'}},
}
# Public HTKK 5.8.2 catalogue texts of B8 (Project/Menu.xml sheet names and caption, Project/MapMCT.xml Map B8 SheetName and the
# captions of the 02-1/BK-QTT-TNCN items with and without their "[nn] - " prefix) that the native 01-1/KHBS may carry beyond the
# reviewed files. Cohort e0ad917 (runs 43776168729, 43776171044, 43776173361, 43776176073): every export differed in
# PL01_1_KHBS/Muc_A/DSachHSo (child count) and its retention was refused at a text outside the inputs (leaf 206, ten_HSo). With
# these texts and ' - '-joined row keys of input pieces (CATALOGUE_KEY_PATH) the next export can be retained and the web ported.
_CAPTIONS = ('[14] - Ngày sinh', '[15] - Quan hệ với NNT', '[16] - Thời gian được tính giảm trừ trong năm\\ Từ tháng',
             '[17] - Thời gian được tính giảm trừ trong năm\\ Đến tháng')
# Cohort fc800a2 (runs 43790973810, 43790976608, 43790979591, 43790982675): the Header dates matched; DSachHSo still differs in child
# count and retention stopped at native leaf 209 = ct3_ma of the FIRST row of the first hồ sơ group, whose ten_HSo passed: the 02-1
# group comes first and its rows carry the MapMCT codes of the 02-1 items ([14]…[17]), outside the inputs.
_CODES = ('[14]', '[15]', '[16]', '[17]')
CATALOGUE_TEXTS = frozenset(('Tờ khai', '02/QTT-TNCN', '02-1/BK-QTT-TNCN') + _CODES + _CAPTIONS + tuple(c.split(' - ', 1)[1] for c in _CAPTIONS))
CATALOGUE_KEY_PATH = 'PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/CTietHSo/ChiTiet/ct3_2_ten'
for _spec in CASES.values():
    _spec['catalogueTexts'] = CATALOGUE_TEXTS
    _spec['annexParts'] = (ANNEX,)
    _spec['inputMode'] = IMPORT
    _spec['producer'], _spec['exporter'] = PRODUCER, EXPORTER
