"""Input contract data of the kê khai bổ sung (KHBS) cases of 01/GTGT TT89/2026 (menu Z5, maTKhai 2032, XML 3.0.9; HTKK 5.8.4).

The htkk_web producer scripts/generate-htkk-web-gtgt01-tt89-khbs-reference.mjs (lib/htkk-gtgt01-tt89-khbs.ts, docs/NGHIEP-VU-01-GTGT-TT89.md
"Kê khai bổ sung" there) stages per case the same files as the other KHBS cases: declaration-original.xml (the lần đầu C0) and
declaration-web.xml (the bổ sung), plus manifest.json; the two lần 2 cases also stage declaration-prior.xml (the bổ sung lần 1 of
the case they build on, byte for byte). Every file is synthetic and was reviewed byte for byte; this public
repository keeps only their sizes and SHA-256 (never the files). The checks, the native B validation and the whole-tree comparison
are those of htkk_ntnn_khbs_web_cases.py, which merges these cases (same driver mode declaration-amendment-khbs-inspect,
HtkkDeclarationKhbs.cs; non-gating observation cases on the HTKK 5.8.4 oracle, ``htkkVersion`` in the manifest).

Z5 has KieuKHBS 3 and VersionKHBS 3.0.9 in the HTKK 5.8.4 Menu.xml (sheets 01-KHBS, 01-1/KHBS), so a B file carries PL01_KHBS /
PL01_1_KHBS (no phụ lục in these cases) and the rounds run "Tổng hợp KHBS". The B schema is Validate/KHBS_01_GTGT_TT89_309.xsd,
the same bytes as Validate/01_GTGT_TT89_309.xsd (8481f7c9…). HTKK 5.8.4 takes the 01-KHBS template KHBS_01_DIA_BAN_THU_HOI_HOAN for
Z5 (Muc_B is the table DsThuHoiHoan). Every round is the original import, as the native-matched lần đầu case
01GTGT-TT89-sale10-M10-2026 (whose inputs are the lần đầu here). What the cases decide (htkk_web static reading of HTKK 5.8.4): the
MapMCT_TieuMuc Z5 tiểu mục path of [40] and [43] ("path_1") has no cell in 01_GTGT_TT89_309.xml, so the web files keep 01/KHBS
Muc_I.1 and Muc_II at their default row (ct10 0, no late days); and the MapMCT Z5 captions as written ("[23a]" on the path ct24,
"[24]" on ct23a). The public Z5 captions, sheet names, codes and tiểu mục names are accepted from the first run (catalogueTexts),
so a differing export is still retained."""

PRODUCER = 'scripts/generate-htkk-web-gtgt01-tt89-khbs-reference.mjs'
EXPORTER = 'lib/htkk-gtgt01-tt89-khbs.ts'
HTKK_VERSION = '5.8.4'
MENUS = {'Z5': ('2032', '3.0.9')}
# kieuKy, kyKKhai, kyKKhaiTuNgay, kyKKhaiDenNgay of every file (tháng 10/2026: HTKK refuses tháng 12/2026 before 01/12/2026).
PERIODS = {'Z5': ('M', '10/2026', '01/10/2026', '31/10/2026')}
IMPORT = 'khbs-web-xml-import-reexport'
_ORIGINAL = (3244, '11f0796d54e28f69079de6aec2535fbb2457ab99f27963cd51e9b3607308cfed')
# The lần 1 web files, which are also the previous version (declaration-prior.xml) of the lần 2 cases.
_INCREASE = (8504, 'c8979d63cedfaf4803cce8bc35f0cb3ff983ab9d10ed46d688ceb3e6ec261ca9')
_DECREASE = (8204, 'e9cf8a4fcd07516504defa20143e7ca54a3adfc3c8f762a56eab27aea88dcab9')
# Tháng 10/2026 is due 20/11/2026: ngày lập 13/11/2026 is before it. ct10 is 0 in both cases (no tiểu mục on [40] / [43]), so
# ct3a_1 stays empty (nil) and ct3a_2 / ct3b are 0.
CASES = {
    # [32] 1.000.000 -> 3.000.000, [33] 100.000 -> 300.000: 01-1/KHBS [27] [28] [32] [33] [34] [35] [36] [40a] [40], ct7 +200.000 on [40].
    '01GTGT-TT89-khbs-increase-M10-2026': {'producerCase': 'gtgt01-tt89-khbs-increase-m10-2026', 'menuId': 'Z5', 'soLan': 1, 'web': _INCREASE, 'original': _ORIGINAL, 'prior': None, 'leafTarget': 304,
        'expected': {'rows': ['[27]', '[28]', '[32]', '[33]', '[34]', '[35]', '[36]', '[40a]', '[40]'], 'subitems': [], 'tongCong7': '200000', 'tongCong8': '0', 'ct10': '0', 'ct3a_1': '', 'ct3a_2': '0', 'ct3b': '0'}},
    # Purchases [23] 2.000.000, path ct24 200.000 (MapMCT "[23a]"), [25] 200.000: [40a]/[40] 100.000 -> 0, [41]/[43] 0 -> 100.000.
    '01GTGT-TT89-khbs-decrease-M10-2026': {'producerCase': 'gtgt01-tt89-khbs-decrease-m10-2026', 'menuId': 'Z5', 'soLan': 1, 'web': _DECREASE, 'original': _ORIGINAL, 'prior': None, 'leafTarget': 291,
        'expected': {'rows': ['[23]', '[23a]', '[25]', '[36]', '[40a]', '[40]', '[41]', '[43]'], 'subitems': [], 'tongCong7': '-100000', 'tongCong8': '100000', 'ct10': '0', 'ct3a_1': '', 'ct3a_2': '0', 'ct3b': '0'}},
    # Bổ sung LẦN 2 (adapter 01-gtgt-tt89-3.0.9-khbs-lan2, amendmentOrder 2): the prior is the lần 1 web file of the case above it,
    # imported, summarised and saved (bs1_) before round 2. htkk_web reading of HTKK 5.8.4 / 5.8.5 (same IL): GetFileNameLoadKhbs
    # loads "bs" + (SoLan - 1) for D1 and Z5 and ReadSheet_LanTruoc reads its main sheet, so lần 2 is compared with lần 1.
    # On increase: [32] 3.000.000 -> 5.000.000, [33] 300.000 -> 500.000: the nine rows again, ct04 of [40] 300.000, ct7 +200.000.
    '01GTGT-TT89-khbs-lan2-increase-M10-2026': {'producerCase': 'gtgt01-tt89-khbs-lan2-increase-m10-2026', 'menuId': 'Z5', 'soLan': 2, 'web': (8504, 'e467bcb510df1162df374f32bbf94157c09200f8ea2161d034c17eed1c611df2'), 'original': _ORIGINAL, 'prior': _INCREASE, 'leafTarget': 304,
        'expected': {'rows': ['[27]', '[28]', '[32]', '[33]', '[34]', '[35]', '[36]', '[40a]', '[40]'], 'subitems': [], 'tongCong7': '200000', 'tongCong8': '0', 'ct10': '0', 'ct3a_1': '', 'ct3a_2': '0', 'ct3b': '0'}},
    # On decrease: purchases halved ([23] 1.000.000, path ct24 100.000, [25] 100.000): [36] -100.000 -> 0 (ct04 "(100.000)"),
    # [41] / [43] 100.000 -> 0; [40a] / [40] stay 0, so no row for them (against the lần đầu they would change).
    '01GTGT-TT89-khbs-lan2-decrease-M10-2026': {'producerCase': 'gtgt01-tt89-khbs-lan2-decrease-m10-2026', 'menuId': 'Z5', 'soLan': 2, 'web': (7570, '5c5bb2315a143678f5dbfb24c4e1180e53a76cb3da98ef826f42479291be5ee2'), 'original': _ORIGINAL, 'prior': _DECREASE, 'leafTarget': 265,
        'expected': {'rows': ['[23]', '[23a]', '[25]', '[36]', '[41]', '[43]'], 'subitems': [], 'tongCong7': '0', 'tongCong8': '-100000', 'ct10': '0', 'ct3a_1': '', 'ct3a_2': '0', 'ct3b': '0'}},
}
# Public HTKK catalogue texts of Z5: Menu.xml sheet name and MaHoSo of the tờ khai, the MapMCT Z5 MauToKhai, the MCT codes and
# captions of its 30 main-sheet items (as written there), and the DM_MaTM names of tiểu mục 1701 and 7551.
_SHEETS = ('Tờ khai', '01/GTGT', '0026')
_ITEMS = (
    ('[21]', 'Không phát sinh hoạt động mua, bán trong kỳ'),
    ('[22]', 'Thuế giá trị gia tăng còn được khấu trừ kỳ trước chuyển sang'),
    ('[23]', 'Giá trị hàng hóa, dịch vụ của hàng hóa, dịch vụ mua vào'),
    ('[23a]', 'Trong đó: Giá trị hàng hóa, dịch vụ hàng hóa nhập khẩu'),
    ('[24]', 'Thuế giá trị gia tăng của hàng hóa, dịch vụ mua vào'),
    ('[24a]', 'Trong đó: Thuế giá trị gia tăng hàng hóa nhập khẩu'),
    ('[25]', 'Thuế giá trị gia tăng của hàng hóa, dịch vụ mua vào được khấu trừ kỳ này'),
    ('[26]', 'Giá trị Hàng hóa, dịch vụ bán ra không chịu thuế giá trị gia tăng'),
    ('[27]', 'Giá trị Hàng hóa, dịch vụ bán ra chịu thuế giá trị gia tăng ([27]=[29]+[30]+[32]+[32a]-[32b]'),
    ('[28]', 'Thuế GTGT của Hàng hóa, dịch vụ bán ra chịu thuế giá trị gia tăng [28]=[31]+[33]'),
    ('[29]', 'Giá trị Hàng hoá, dịch vụ bán ra chịu thuế suất 0%'),
    ('[30]', 'Giá trị Hàng hoá, dịch vụ bán ra chịu thuế suất 5%'),
    ('[31]', 'Thuế GTGT của Hàng hoá, dịch vụ bán ra chịu thuế suất 5%'),
    ('[32]', 'Giá trị Hàng hoá, dịch vụ bán ra chịu thuế suất 10%'),
    ('[33]', 'Thuế GTGT Hàng hoá, dịch vụ bán ra chịu thuế suất 10%'),
    ('[32a]', 'Giá trị Hàng hoá, dịch vụ bán ra không kê khai tính nộp thuế'),
    ('[32b]', 'Giá trị Hàng hoá, dịch vụ bán ra không tính vào giá tính thuế giá trị gia tăng'),
    ('[34a]', 'Giá trị Hàng hoá, dịch vụ bán ra không thuộc phạm vi điều chỉnh của pháp luật thuế giá trị gia tăng'),
    ('[34]', 'Tổng doanh thu của hàng hóa, dịch vụ bán ra ([34]=[26]+[27]+[34a];'),
    ('[35]', 'Tổng thuế giá trị gia tăng của hàng hóa, dịch vụ bán ra [35]=[28])'),
    ('[36]', 'Thuế giá trị gia tăng phát sinh trong kỳ ([36]=[35]-[25])'),
    ('[37]', 'Điều chỉnh giảm'),
    ('[38]', 'Điều chỉnh tăng'),
    ('[39a]', 'Thuế giá trị gia tăng nhận bàn giao được khấu trừ trong kỳ'),
    ('[40a]', 'Thuế giá trị gia tăng phải nộp của hoạt động sản xuất kinh doanh trong kỳ {[40a]=([36]-[22]+[37]-[38]-[39a]) ≥ 0}'),
    ('[40b]', 'Thuế giá trị gia tăng mua vào của dự án đầu tư được bù trừ với thuế GTGT còn phải nộp của hoạt động sản xuất kinh doanh cùng kỳ tính thuế ([40b]≤[40a])'),
    ('[40]', 'Thuế giá trị gia tăng còn phải nộp trong kỳ ([40]=[40a]-[40b])'),
    ('[41]', 'Thuế giá trị gia tăng chưa khấu trừ hết kỳ này {[41]=([36]-[22]+[37]-[38]-[39a]) ≤ 0}'),
    ('[42]', 'Thuế giá trị gia tăng đề nghị hoàn ([42] ≤ [41])'),
    ('[43]', 'Thuế giá trị gia tăng còn được khấu trừ chuyển kỳ sau ([43]=[41]-[42])'),
)
_SUBITEMS = ('Thuế giá trị gia tăng hàng sản xuất, kinh doanh trong nước (gồm cả dịch vụ trong lĩnh vực dầu khí)', 'Hoàn thuế giá trị gia tăng')
CATALOGUE_TEXTS = frozenset(_SHEETS + tuple(code for code, _ in _ITEMS) + tuple(caption for _, caption in _ITEMS) + _SUBITEMS)
for _spec in CASES.values():
    _spec['catalogueTexts'] = CATALOGUE_TEXTS
    _spec['inputMode'] = IMPORT
    _spec['annexParts'] = ()
    _spec['htkkVersion'] = HTKK_VERSION
    _spec['producer'], _spec['exporter'] = PRODUCER, EXPORTER
