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
_INCREASE = (7533, '2838c556d0744c35c04f95fe6fe6689dc14ed579f0613be659374c9fde54bb27')
# Năm 2025 is due 31/03/2026 as GetHanNopToKhai reads it (KieuKy Y), ngày lập 13/11/2026: 227 late days in every case.
CASES = {
    '02QTT-khbs-increase-Y2025': {'producerCase': 'qtt02-khbs-increase-y2025', 'menuId': 'B8', 'soLan': 1, 'web': _INCREASE, 'original': _ORIGINAL, 'prior': None, 'leafTarget': 272,
        'expected': {'rows': ['[20]', '[21]', '[31]', '[32]', '[42]'], 'subitems': [['1001', '3000000']], 'refund': [], 'ct10': '3000000', 'ct13': '0', 'ct3a_1': '2026-11-13', 'ct3a_2': '227', 'ct3b': '204300'}},
    '02QTT-khbs-lan2-Y2025': {'producerCase': 'qtt02-khbs-lan2-y2025', 'menuId': 'B8', 'soLan': 2, 'web': (7535, '0cb27777150ae8ac67850397cdc2cc73565dcf87e6a30859384a6d8c76728642'), 'original': _ORIGINAL, 'prior': _INCREASE, 'leafTarget': 272,
        'expected': {'rows': ['[20]', '[21]', '[31]', '[32]', '[42]'], 'subitems': [['1001', '1440000']], 'refund': [], 'ct10': '1440000', 'ct13': '0', 'ct3a_1': '2026-11-13', 'ct3a_2': '227', 'ct3b': '98064'}},
    '02QTT-khbs-decrease-Y2025': {'producerCase': 'qtt02-khbs-decrease-y2025', 'menuId': 'B8', 'soLan': 1, 'web': (7002, 'ba77ad7590f97b7f8b9c9ed2e6e3741631d7c40011d8b7521568d69a539e5f88'), 'original': _ORIGINAL, 'prior': None, 'leafTarget': 246,
        'expected': {'rows': ['[33]', '[34]', '[42]'], 'subitems': [['1001', '-1000000']], 'refund': [], 'ct10': '-1000000', 'ct13': '0', 'ct3a_1': '2026-11-13', 'ct3a_2': '227', 'ct3b': '-68100'}},
    # Hoàn qua chuyển khoản on both versions (the reviewed transfer of 02QTT-refund-transfer-Y2025): [34] 20tr → 22tr, [46] 14,12tr
    # → 16,12tr; [45] (LoaiThue 2) goes to Muc_III.
    '02QTT-khbs-refund-Y2025': {'producerCase': 'qtt02-khbs-refund-y2025', 'menuId': 'B8', 'soLan': 1, 'web': (7843, 'b87263b9c99eaea3c4ce772ac4d498ec037fd2a12c1523b062fee0f793f3e306'), 'original': (3819, '12924fb7cfcec03807839fe4f9cea3e3254b9c467ed59a8007fc63b045d18b06'), 'prior': None, 'leafTarget': 272,
        'expected': {'rows': ['[33]', '[34]', '[44]', '[45]', '[46]'], 'subitems': [['1001', '-2000000']], 'refund': [['1001', '2000000']], 'ct10': '-2000000', 'ct13': '2000000', 'ct3a_1': '2026-11-13', 'ct3a_2': '227', 'ct3b': '-136200'}},
}
for _spec in CASES.values():
    _spec['annexParts'] = (ANNEX,)
    _spec['inputMode'] = IMPORT
    _spec['producer'], _spec['exporter'] = PRODUCER, EXPORTER
