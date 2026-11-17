"""Input contract data of the kê khai bổ sung (KHBS) cases of 01/TCKT TT89/2026 3.1.0 (menu Y7, maTKhai 2007; HTKK 5.8.2).

The htkk_web producer scripts/generate-htkk-web-tckt01-khbs-reference.mjs (lib/htkk-tckt01-khbs.ts, docs/NGHIEP-VU-HKD.md
"Kê khai bổ sung 01/TCKT 3.1.0" there) stages per case the same files as the other KHBS cases: declaration-original.xml (the
lần đầu C0), declaration-prior.xml (bổ sung lần N-1, lần 2 only) and declaration-web.xml (the bổ sung), plus manifest.json.
Every file is synthetic and was reviewed byte for byte; this public repository keeps only their sizes and SHA-256 (never the
files). The checks, the native B validation and the whole-tree comparison are those of htkk_ntnn_khbs_web_cases.py, which merges
these cases (same driver mode declaration-amendment-khbs-inspect, HtkkDeclarationKhbs.cs; non-gating observation cases on HTKK
5.8.2).

Y7 has KieuKHBS 3 and VersionKHBS 3.1.0 in the HTKK 5.8.2 Menu.xml (sheets 01-KHBS, 01-1/KHBS), so unlike U5 a B file carries
PL01_KHBS / PL01_1_KHBS after the case's bảng kê (01/BK-KTHTKD PLuc_HKD_CNKD or 02/BK-KTBĐS PLuc_CANHAN_TTS) and the rounds run
"Tổng hợp KHBS"; the B schema is Validate/KHBS_01_TCKT_TT89_310.xsd. Every round is the original import: the 3.1.0 lần đầu cases
01TCKT-310-* imported and re-exported both bảng kê with every leaf (runs 44044889464, 44044893474). Y7 writes the export day into
TKhaiThue/ngayKy (EXPORT_DATES of htkk_declaration_web_cases.py), so that leaf is compared as an export date here too
(exportDates). The web reading of MapMCT / MapMCT_TieuMuc is the HTKK 5.8.1 one (the 5.8.2 files were not available to it), so
the public Y7 captions, sheet names, codes and tiểu mục names are accepted from the first run (catalogueTexts) and a differing
export is still retained."""

PRODUCER = 'scripts/generate-htkk-web-tckt01-khbs-reference.mjs'
EXPORTER = 'lib/htkk-tckt01-khbs.ts'
MENUS = {'Y7': ('2007', '3.1.0')}
# kieuKy, kyKKhai, kyKKhaiTuNgay, kyKKhaiDenNgay of the menu's cases (quý 4/2026); the 02/BK-KTBĐS case has its own (tháng 10/2026).
PERIODS = {'Y7': ('Q', '4/2026', '01/10/2026', '31/12/2026')}
HTKD, BDS = 'PLuc_HKD_CNKD', 'PLuc_CANHAN_TTS'
IMPORT = 'khbs-web-xml-import-reexport'
EXPORT_DATES = ('HSoThueDTu/HSoKhaiThue/TTinChung/TTinTKhaiThue/TKhaiThue/ngayKy',)
_ORIGINAL = (2544, '81ad4be39c11a73119f90c049e5a6b1122bbf1170de6206784648a8197b89338')
_INCREASE = (7068, 'b31cba8a8d36c5efba2e8a440ae38f44f3057a33c73e61f3ad11d2fbff769966')
# Rows: 'main' or the bảng kê sheet index (1 = 01/BK-KTHTKD, 2 = 02/BK-KTBĐS) + the MapMCT code. Quý 4/2026 is due 30/01/2027 (a
# Saturday, so 01/02/2027) and tháng 10/2026 on 20/11/2026: ngày lập 13/11/2026 is before both, ct3a_1 written, 0 days, ct3b 0.
_HTKD_ROWS = ['main [07]', 'main [08]', 'main [09]', '1 [07]', '1 [08]', '1 [09]']
CASES = {
    # 01/BK-KTHTKD, row A [07]/[08] 300tr -> 350tr (nhóm 02, 2%): [09] +1.000.000, tiểu mục 1003.
    '01TCKT-310-khbs-hop-tac-kd-Q4-2026': {'producerCase': 'tckt01-310-khbs-hop-tac-kd-q4-2026', 'menuId': 'Y7', 'soLan': 1, 'web': _INCREASE, 'original': _ORIGINAL, 'prior': None, 'leafTarget': 224,
        'annexParts': (HTKD,), 'expected': {'rows': _HTKD_ROWS, 'subitems': [['1003', '1000000']], 'ct10': '1000000', 'ct3a_1': '2026-11-13', 'ct3a_2': '0', 'ct3b': '0'}},
    # Bổ sung lần 2 on the case above: row A 350tr -> 380tr, 1003 +600.000.
    '01TCKT-310-khbs-lan2-hop-tac-kd-Q4-2026': {'producerCase': 'tckt01-310-khbs-lan2-hop-tac-kd-q4-2026', 'menuId': 'Y7', 'soLan': 2, 'web': (7062, '32864d8bfa6d181b7ee168c4b3da9e6332b56276162bfce36c8d90fc3b9b5199'), 'original': _ORIGINAL, 'prior': _INCREASE, 'leafTarget': 224,
        'annexParts': (HTKD,), 'expected': {'rows': _HTKD_ROWS, 'subitems': [['1003', '600000']], 'ct10': '600000', 'ct3a_1': '2026-11-13', 'ct3a_2': '0', 'ct3b': '0'}},
    # Row B [08] 110tr -> 100tr (nhóm 06, 1%): 1003 -100.000.
    '01TCKT-310-khbs-decrease-hop-tac-kd-Q4-2026': {'producerCase': 'tckt01-310-khbs-decrease-hop-tac-kd-q4-2026', 'menuId': 'Y7', 'soLan': 1, 'web': (6369, '0f36a2322230daaac8c96869cbb7e41dd818f3587b736ae4ec7d76d36b4a5913'), 'original': _ORIGINAL, 'prior': None, 'leafTarget': 198,
        'annexParts': (HTKD,), 'expected': {'rows': ['main [08]', 'main [09]', '1 [08]', '1 [09]'], 'subitems': [['1003', '-100000']], 'ct10': '-100000', 'ct3a_1': '2026-11-13', 'ct3a_2': '0', 'ct3b': '0'}},
    # 02/BK-KTBĐS tháng 10/2026, lessor A [08] 60.000.010 -> 80.000.010: [12] 1701 +1.000.000, [13] 1014 +1.000.000.
    '01TCKT-310-khbs-bds-M10-2026': {'producerCase': 'tckt01-310-khbs-bds-m10-2026', 'menuId': 'Y7', 'soLan': 1, 'web': (7548, '884328cbd31f0e8e1f7ab2bece11bfae9e6eb0a557170b626728c2868c038c31'), 'original': (3020, '0fe0ba33597ff8fd292348912e728ff992dee5b1d0de262e5c2faf451fe34052'), 'prior': None, 'leafTarget': 242,
        'annexParts': (BDS,), 'period': ('M', '10/2026', '01/10/2026', '31/10/2026'),
        'expected': {'rows': ['main [11]', 'main [12]', 'main [13]', '2 [08]', '2 [11]', '2 [12]'], 'subitems': [['1701', '1000000'], ['1014', '1000000']], 'ct10': '2000000', 'ct3a_1': '2026-11-13', 'ct3a_2': '0', 'ct3b': '0'}},
}
# Public HTKK catalogue texts of Y7: Menu.xml sheet names, the MapMCT Y7 MauToKhai / SheetNames / codes, every MapMCT Y7 caption with
# and without its "[nn] - " prefix, and the DM_MaTM names of its tiểu mục 1003 / 1701 / 1014.
_SHEETS = ('Tờ khai', '01/TCKT', '01/BK-KTHTKD', '02/BK-KTBĐS', 'PL NQ 43/2026/QH16', '0252', '025201', '025202', '025203')
_CAPTIONS = (
    '[07] - Tổng doanh thu phát sinh trong kỳ', '[08] - Tổng doanh thu tính thuế TNCN trong kỳ', '[09] - Tổng số thuế TNCN phải nộp',
    '[11] - Tổng doanh thu phát sinh trong kỳ', '[12] - Tổng số thuế GTGT phải nộp', '[13] - Tổng số thuế TNCN phải nộp',
    '[04] - Họ và tên hộ kinh doanh, cá nhân kinh doanh', '[05] - Mã số thuế hộ kinh doanh, cá nhân kinh doanh', '[06] - Nhóm ngành nghề',
    '[07] - Doanh thu trả trong kỳ', '[08] - Doanh thu tính thuế TNCN', '[09] - Số thuế TNCN phải nộp',
    '[05] - Họ tên bên cho thuê bất động sản', '[06] - Mã số thuế bên cho thuê bất động sản',
    '[07] - Địa chỉ bất động sản cho thuê (Số nhà, đường phố/xóm/ấp/ thôn)', '[08] - Tổng doanh thu phát sinh trong kỳ',
    '[09] - Doanh thu được trừ để xác định doanh thu tính thuế', '[10] - Cá nhân thuộc diện không phải nộp thuế',
    '[11] - Số thuế GTGT phải nộp', '[12] - Số thuế TNCN phải nộp',
)
_CODES = tuple(sorted({caption[:caption.index(' - ')] for caption in _CAPTIONS}))
_SUBITEMS = ('Thuế thu nhập từ hoạt động sản xuất, kinh doanh của cá nhân', 'Thuế thu nhập từ hoạt động cho thuê tài sản',
             'Thuế giá trị gia tăng hàng sản xuất, kinh doanh trong nước (gồm cả dịch vụ trong lĩnh vực dầu khí)')
CATALOGUE_TEXTS = frozenset(_SHEETS + _CODES + _CAPTIONS + tuple(caption[caption.index(' - ') + 3:] for caption in _CAPTIONS) + _SUBITEMS)
for _spec in CASES.values():
    _spec['catalogueTexts'] = CATALOGUE_TEXTS
    _spec['exportDates'] = EXPORT_DATES
    _spec['inputMode'] = IMPORT
    _spec['producer'], _spec['exporter'] = PRODUCER, EXPORTER
