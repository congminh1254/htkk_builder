"""Input contract data of the kê khai bổ sung (KHBS) cases of 05/QTT-TNCN TT80 (menu B9, 2.9.3; quyết toán thuế TNCN của tổ chức trả
thu nhập, kèm 05-1, 05-3/BK-QTT-TNCN in these cases).

The htkk_web producer scripts/generate-htkk-web-qtt05-khbs-reference.mjs (docs/KE-KHAI-BO-SUNG-05-QTT-TNCN.md there) stages per
case the same files as the other KHBS cases: declaration-original.xml (the lần đầu C0), declaration-prior.xml (bổ sung lần N-1,
lần 2 only) and declaration-web.xml (the bổ sung), plus manifest.json. Every file is synthetic and was reviewed byte for byte;
this public repository keeps only their sizes and SHA-256 (never the files). The checks, the native B validation and the
whole-tree comparison are those of htkk_ntnn_khbs_web_cases.py, which merges these cases (same driver mode
declaration-amendment-khbs-inspect, HtkkDeclarationKhbs.cs; non-gating observation cases on HTKK 5.8.2).

B9 has KieuKHBS 3 in the HTKK 5.8.2 Menu.xml, so a B file carries PL01_KHBS / PL01_1_KHBS after the case's 05-1 and 05-3 annexes;
every round is the original import (cmdImportXML_Click adds every B9 annex first). Every MapMCT B9 item is static: the tờ khai and
the 05-1 / 05-2 totals each form one hồ sơ group of 01-1/KHBS. Learned from 02/QTT-TNCN (KHBS-NATIVE-CASE.md): HTKK may write
catalogue texts beyond the reviewed files, so the public B9 names, codes and captions are accepted from the first run
(CATALOGUE_TEXTS, with ' - '-joined row keys of input pieces), and the retained export can be ported if it differs."""

PRODUCER = 'scripts/generate-htkk-web-qtt05-khbs-reference.mjs'
EXPORTER = 'lib/htkk-qtt05-khbs.ts'
MENUS = {'B9': ('953', '2.9.3')}
# kieuKy, kyKKhai, kyKKhaiTuNgay, kyKKhaiDenNgay of every file of the cases.
PERIODS = {'B9': ('Y', '2025', '', '')}
# The lần đầu file carries 05-1 and 05-3; every B file carries all three bảng kê, 05-2 as HTKK's default sheet (cohort 5cf04ba: runs
# 43845164240, 43845168874, 43845173606 exported PLuc_05_2_BK_QTT with one empty row; htkk_web 2d7ead18 writes it, raw exports kept
# there and reproduced leaf for leaf).
ORIGINAL_ANNEXES = ('PLuc_05_1_BK_QTT', 'PLuc_05_3_BK_QTT')
ANNEXES = ('PLuc_05_1_BK_QTT', 'PLuc_05_2_BK_QTT', 'PLuc_05_3_BK_QTT')
IMPORT = 'khbs-web-xml-import-reexport'
_ORIGINAL = (4593, '3ee7bfff733a6954ca6bf8697ed9d38cc3b060482ab5160620d6b3722eb9a47a')
_INCREASE = (10485, '2ad42d11318db75cc9ac14f5d1e4734094cc26ef0df3410973f424c93646a0e1')
_ROWS = ['0[23]', '0[24]', '0[28]', '0[29]', '0[38]', '0[41]', '1[28]', '1[37]', '1[40]', '1[41]']
# Năm 2025 is due 31/03/2026 (GetHanNopToKhai KieuKy Y), ngày lập 13/11/2026: 227 late days. Rows: sheet index + MapMCT code.
CASES = {
    '05QTT-khbs-increase-Y2025': {'producerCase': 'qtt05-khbs-increase-y2025', 'menuId': 'B9', 'soLan': 1, 'web': _INCREASE, 'original': _ORIGINAL, 'prior': None, 'leafTarget': 393,
        'expected': {'rows': _ROWS, 'subitems': [['1001', '3000000']], 'ct10': '3000000', 'ct3a_1': '2026-11-13', 'ct3a_2': '227', 'ct3b': '204300'}},
    '05QTT-khbs-lan2-Y2025': {'producerCase': 'qtt05-khbs-lan2-y2025', 'menuId': 'B9', 'soLan': 2, 'web': (10486, '567c1cf8bddfcbae666a99e62ea9bebb9aac918ff5f01075f1882c107633a648'), 'original': _ORIGINAL, 'prior': _INCREASE, 'leafTarget': 393,
        'expected': {'rows': _ROWS, 'subitems': [['1001', '2000000']], 'ct10': '2000000', 'ct3a_1': '2026-11-13', 'ct3a_2': '227', 'ct3b': '136200'}},
    '05QTT-khbs-decrease-Y2025': {'producerCase': 'qtt05-khbs-decrease-y2025', 'menuId': 'B9', 'soLan': 1, 'web': (9386, '70ed280f721ea010d22d4acd013cf0ac0f68ef6dd66a0f28674b50bc641994a3'), 'original': _ORIGINAL, 'prior': None, 'leafTarget': 341,
        'expected': {'rows': ['0[31]', '0[32]', '0[36]', '0[41]', '1[38]', '1[41]'], 'subitems': [['1001', '-1000000']], 'ct10': '-1000000', 'ct3a_1': '2026-11-13', 'ct3a_2': '227', 'ct3b': '-68100'}},
}
# Public HTKK 5.8.2 catalogue texts of B9: Menu.xml sheet names and captions, the MapMCT B9 MauToKhai / SheetNames, the codes of
# the 05-1 / 05-2 total items and every MapMCT B9 caption.
CATALOGUE_TEXTS = frozenset((
    "Tờ khai",
    "05/QTT-TNCN",
    "05-1/BK-TNCN",
    "05-2/BK-TNCN",
    "05-3/BK-TNCN",
    "05-1/BK-QTT-TNCN",
    "05-2/BK-QTT-TNCN",
    "05-3/BK-QTT-TNCN",
    "05-QTT-TNCN",
    "[17]",
    "[18]",
    "[19]",
    "[20.1]",
    "[20]",
    "[21]",
    "[22]",
    "[28]",
    "[29]",
    "[30]",
    "[31.1]",
    "[31]",
    "[32]",
    "[33]",
    "[34]",
    "[35]",
    "[36]",
    "[37]",
    "[38]",
    "[39]",
    "[40]",
    "[41]",
    "[42]",
    "Cá nhân cư trú",
    "Cá nhân không cư trú",
    "Trong đó tổng thu nhập chịu thuế được miễn theo quy định của Hợp đồng dầu khí",
    "Trong đó: Cá nhân cư trú có hợp đồng lao động",
    "Trong đó: Số thuế thu nhập cá nhân đã khấu trừ tại tổ chức trước khi điều chuyển (trường hợp có đánh dấu vào chỉ tiêu [04])",
    "Trong đó: Tổng số thuế thu nhập cá nhân đã khấu trừ trên tiền phí mua bảo hiểm nhân thọ, bảo hiểm không bắt buộc khác của doanh nghiệp bảo hiểm không thành lập tại Việt Nam cho người lao động",
    "Trong đó: Tổng thu nhập chịu thuế từ tiền phí mua bảo hiểm nhân thọ, bảo hiểm không bắt buộc khác của doanh nghiệp bảo hiểm không thành lập tại Việt Nam cho người lao động",
    "Tổng Bảo hiểm được trừ",
    "Tổng Quĩ hưu trí tự nguyện được trừ",
    "Tổng Số lượng NPT tính giảm trừ",
    "Tổng TN chịu thuế được miễn theo quy định của Hợp đồng dầu khí",
    "Tổng TNCT tại tổ chức trước khi điều chuyển (trường hợp có đánh dấu vào chỉ tiêu [04] tại Tờ khai 05/QTT-TNCN)",
    "Tổng TNCT từ phí mua BH nhân thọ, BH không bắt buộc khác của DN BH không thành lập tại Việt Nam cho người lao động",
    "Tổng Thu nhập chịu thuế được miễn theo Hiệp định",
    "Tổng Thu nhập chịu thuế được miễn theo quy định của Hợp đồng dầu khí",
    "Tổng Thu nhập miễn thuế, thu nhập cá nhân theo nghị quyết",
    "Tổng Từ thiện, nhân đạo, khuyến học",
    "Tổng số cá nhân giảm trừ gia cảnh",
    "Tổng số cá nhân thuộc diện được miễn, giảm thuế theo Hiệp định tránh đánh thuế hai lần",
    "Tổng số cá nhân uỷ quyền cho tổ chức, cá nhân trả thu nhập quyết toán thay",
    "Tổng số cá nhân đã khấu trừ thuế [18]=[19]+[20]",
    "Tổng số người lao động:",
    "Tổng số thu nhập chịu thuế",
    "Tổng số thuế TNCN đã khấu trừ",
    "Tổng số thuế còn phải nộp",
    "Tổng số thuế phải nộp",
    "Tổng số thuế thu nhập cá nhân còn phải nộp [40] = ([38] – [36] – [39]) >0",
    "Tổng số thuế thu nhập cá nhân phải nộp",
    "Tổng số thuế thu nhập cá nhân đã khấu trừ",
    "Tổng số thuế thu nhập cá nhân đã khấu trừ [31]=[32]+[33]",
    "Tổng số thuế thu nhập cá nhân đã nộp thừa [41]",
    "Tổng số thuế thu nhập cá nhân được miễn do cá nhân có số thuế còn phải nộp sau ủy quyền quyết toán từ 50.000 đồng trở xuống",
    "Tổng số thuế từ phí mua BH nhân thọ, BH không bắt buộc khác của DN BH không thành lập tại Việt Nam cho người lao động",
    "Tổng số thuế đã khấu trừ tại tổ chức trước khi điều chuyển (trường hợp có đánh dấu vào chỉ tiêu [04] tại Tờ khai 05/QTT",
    "Tổng số thuế đã nộp thừa",
    "Tổng số tiền giảm trừ gia cảnh",
    "Tổng thu nhập chịu thuế",
    "Tổng thu nhập chịu thuế trả cho cá nhân [23]=[24]+[25]",
    "Tổng thu nhập chịu thuế trả cho cá nhân thuộc diện phải khấu trừ thuế [28]=[29]+[30]",
    "Tổng thu nhập chịu thuế được miễn theo Hiệp định",
    "Tổng thu nhập tính thuế ([21]=[12]-[14]-[15]-[15.1]-[17]-[18]-[19]-[20])",
))
for _spec in CASES.values():
    _spec['catalogueTexts'] = CATALOGUE_TEXTS
    _spec['annexParts'] = ANNEXES
    _spec['originalAnnexParts'] = ORIGINAL_ANNEXES
    _spec['inputMode'] = IMPORT
    _spec['producer'], _spec['exporter'] = PRODUCER, EXPORTER
