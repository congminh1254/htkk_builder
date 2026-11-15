"""Input contract data of the kê khai bổ sung (KHBS) cases of 01/CNKD TT50/2026 (menu U5, 3.1.0).

The htkk_web producer scripts/generate-htkk-web-cnkd-khbs-reference.mjs (docs/KE-KHAI-BO-SUNG-01-CNKD.md there) stages per case
the same files as the 01/NTNN and 05/KK-TNCN KHBS cases: declaration-original.xml (the lần đầu C0), declaration-prior.xml (bổ
sung lần N-1, lần 2 only) and declaration-web.xml (the bổ sung), plus manifest.json. Every file is synthetic and was reviewed byte
for byte; this public repository keeps only their sizes and SHA-256 (never the files). The checks, the native B validation and
the whole-tree comparison are those of htkk_ntnn_khbs_web_cases.py, which merges these cases (same driver mode
declaration-amendment-khbs-inspect, HtkkDeclarationKhbs.cs; non-gating observation cases on HTKK 5.8.2).

U5 has KieuKHBS "" in the HTKK 5.8.2 Menu.xml: HTKK shows no "Tổng hợp KHBS" for it and its KHBS schema is the declaration
schema, so a B file is the whole declaration with loaiTKhai B and its lần, WITHOUT PL01_KHBS / PL01_1_KHBS (khbsParts empty)
and the driver skips the summary step (HtkkDeclarationCasePlans.KhbsSummary). Per case: the producer and exporter, the PLuc
parts (PL 01 of NQ 43/2026/QH16 for the PL 01 case, whose giảm thuế ticks have no XML leaf and are made again in HTKK's grid
after each import: inputMode khbs-web-xml-import-tick-reexport)."""

PRODUCER = 'scripts/generate-htkk-web-cnkd-khbs-reference.mjs'
EXPORTER = 'lib/htkk-cnkd01-khbs.ts'
MENUS = {'U5': ('1266', '3.1.0')}
# kieuKy, kyKKhai, kyKKhaiTuNgay, kyKKhaiDenNgay of every file of the cases.
PERIODS = {'U5': ('Q', '3/2026', '01/07/2026', '30/09/2026')}
PL01 = 'PLuc_01_GiamTNCN_NQ43'
IMPORT, IMPORT_TICK = 'khbs-web-xml-import-reexport', 'khbs-web-xml-import-tick-reexport'
_ORIGINAL = (9696, '7e270183c4ca14d3ef62f980771fa815cc466f33c69724e216bb9f736c3c8e69')
_INCREASE = (9696, 'b4c4aca370bfd4fcd3becc738f3109a222b8de5a4839c63f8076013d08dc4845')
_GTGT, _TNCN, _VAT, _PIT = 'Tổng doanh thu tính thuế GTGT', 'Tổng doanh thu tính thuế TNCN', 'Thuế GTGT còn phải nộp [20]', 'Thuế TNCN còn phải nộp [20]'
CASES = {
    '01CNKD-khbs-increase-Q3-2026': {'producerCase': 'cnkd01-khbs-increase-q3-2026', 'menuId': 'U5', 'soLan': 1, 'web': _INCREASE, 'original': _ORIGINAL, 'prior': None, 'leafTarget': 271,
        'expected': {'lines': [[_GTGT, '50000000'], [_TNCN, '50000000'], [_VAT, '500000'], [_PIT, '250000']], 'total': ['23500000', '24250000']}},
    '01CNKD-khbs-decrease-Q3-2026': {'producerCase': 'cnkd01-khbs-decrease-q3-2026', 'menuId': 'U5', 'soLan': 1, 'web': (9696, '8d1179d77cb9f9503b82c418a62b77047cf53686fbac726c9353678cbc913ed3'), 'original': _ORIGINAL, 'prior': None, 'leafTarget': 271,
        'expected': {'lines': [[_GTGT, '-50000000'], [_TNCN, '-50000000'], [_VAT, '-1500000'], [_PIT, '-750000']], 'total': ['23500000', '21250000']}},
    '01CNKD-khbs-lan2-Q3-2026': {'producerCase': 'cnkd01-khbs-lan2-q3-2026', 'menuId': 'U5', 'soLan': 2, 'web': (9696, '31d4306d5424839461e0d2779dd64119f9c65498ad598d43c9a88ae6ea99b6cb'), 'original': _ORIGINAL, 'prior': _INCREASE, 'leafTarget': 271,
        'expected': {'lines': [[_GTGT, '30000000'], [_TNCN, '30000000'], [_VAT, '300000'], [_PIT, '150000']], 'total': ['24250000', '24700000']}},
    # PL 01 of NQ 43/2026/QH16 on both versions (rows 01 and 04 ticked, unchanged): the giảm thuế ticks are made again after each
    # import with the reviewed tick plan of 01CNKD-TT50-310-pl01-three-groups-Q3-2026 (KhbsImportTick).
    '01CNKD-PL01-khbs-Q3-2026': {'producerCase': 'cnkd01-pl01-khbs-q3-2026', 'menuId': 'U5', 'soLan': 1, 'web': (11292, 'cab6505ff79e92309122b16efcef51f4c31172600cf95ee91ecf7d0baa6107bd'), 'original': (11292, 'f6ba21ce092b3622aab70ca0e65b5564e38eb32a81320175bd75723d9eeb647c'), 'prior': None, 'leafTarget': 295,
        'annexParts': (PL01,), 'inputMode': IMPORT_TICK,
        'expected': {'lines': [[_GTGT, '10000000'], [_TNCN, '10000000'], [_VAT, '500000'], [_PIT, '200000']], 'total': ['22150000', '22850000']}},
}
for _spec in CASES.values():
    _spec.setdefault('annexParts', ())
    _spec.setdefault('inputMode', IMPORT)
    # No KHBS fragments in a U5 B file, and no "Tổng hợp KHBS" round step.
    _spec['khbsParts'] = ()
    _spec['producer'], _spec['exporter'] = PRODUCER, EXPORTER
