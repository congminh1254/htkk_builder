"""Input contract data of the kê khai bổ sung (KHBS) cases of 05/KK-TNCN TT80 (menu L7) and 05/KK-TNCN TT89 (menu Z8).

The htkk_web producer scripts/generate-htkk-web-kk05-khbs-reference.mjs (docs/KE-KHAI-BO-SUNG-05-KK-TNCN.md there) stages per
case the same files as the 01/NTNN KHBS cases: declaration-original.xml (the lần đầu C0), declaration-prior.xml (bổ sung lần
N-1, lần 2 only) and declaration-web.xml (the bổ sung), plus manifest.json. Every file is synthetic and was reviewed byte for
byte; this public repository keeps only their sizes and SHA-256 (never the files). The checks, the native B validation and
the whole-tree comparison are those of htkk_ntnn_khbs_web_cases.py, which merges these cases (same driver mode
declaration-amendment-khbs-inspect, HtkkDeclarationKhbs.cs; non-gating observation cases on HTKK 5.8.2).

Per case: the producer and exporter, the PLuc parts before the two KHBS fragments (05-1/PBT-KK-TNCN for the PBT case, whose
Thuế tỉnh/CCT has no XML leaf and is chosen again in HTKK's grid after each import: inputMode khbs-web-xml-import-tick-reexport)."""

PRODUCER = 'scripts/generate-htkk-web-kk05-khbs-reference.mjs'
EXPORTER = 'lib/htkk-kk05-khbs.ts'
MENUS = {'L7': ('864', '2.9.3'), 'Z8': ('2036', '3.0.9')}
# kieuKy, kyKKhai, kyKKhaiTuNgay, kyKKhaiDenNgay of every file of a menu's cases.
PERIODS = {'L7': ('Q', '3/2026', '01/07/2026', '30/09/2026'), 'Z8': ('Q', '4/2026', '01/10/2026', '31/12/2026')}
PBT = 'PLuc_05_1_PBT_KK_TNCN'
IMPORT, IMPORT_TICK = 'khbs-web-xml-import-reexport', 'khbs-web-xml-import-tick-reexport'
_L7_ORIGINAL = (2003, '077189398fbc32706962038d3c135ac16cdb83c5a9b356cbf20442a14919ed65')
_L7_INCREASE = (6355, 'df8340c414ba3298f1abf84e059c22a42f6b32f339a0c4549018ca42da5514aa')
CASES = {
    '05KK-khbs-increase-Q3-2026': {'producerCase': 'kk05-khbs-increase-q3-2026', 'menuId': 'L7', 'soLan': 1, 'web': _L7_INCREASE, 'original': _L7_ORIGINAL, 'prior': None, 'leafTarget': 213,
        'expected': {'rows': ['[21]', '[22]', '[26]', '[27]', '[29]', '[30]'], 'subitems': [['1001', '1000000']], 'allocation': [], 'ct10': '1000000', 'ct11': '0', 'ct3a_1': '2026-11-13', 'ct3a_2': '14', 'ct3b': '4200'}},
    '05KK-khbs-lan2-Q3-2026': {'producerCase': 'kk05-khbs-lan2-q3-2026', 'menuId': 'L7', 'soLan': 2, 'web': (5145, '03ae8ada9a018fdb827b0d214766b91e788c4ba000e7ddbb4e20ca165636c5fe'), 'original': _L7_ORIGINAL, 'prior': _L7_INCREASE, 'leafTarget': 161,
        'expected': {'rows': ['[29]', '[30]'], 'subitems': [['1001', '500000']], 'allocation': [], 'ct10': '500000', 'ct11': '0', 'ct3a_1': '2026-11-13', 'ct3a_2': '14', 'ct3b': '2100'}},
    '05KK-khbs-decrease-Q3-2026': {'producerCase': 'kk05-khbs-decrease-q3-2026', 'menuId': 'L7', 'soLan': 1, 'web': (5162, '6ddc7013fecad91c03f5da21164f903b21dd2e28bb2485cd705ebbed4ba9f1db'), 'original': _L7_ORIGINAL, 'prior': None, 'leafTarget': 161,
        'expected': {'rows': ['[29]', '[31]'], 'subitems': [['1001', '-1000000']], 'allocation': [], 'ct10': '-1000000', 'ct11': '0', 'ct3a_1': '2026-11-13', 'ct3a_2': '14', 'ct3b': '-4200'}},
    '05KK-TT89-khbs-increase-Q4-2026': {'producerCase': 'kk05-tt89-khbs-increase-q4-2026', 'menuId': 'Z8', 'soLan': 1, 'web': (5381, '8b14b2eeaa4b764e09de4f9481936df4bb7d592ff74ebaf7174e1c877eb5bfdc'), 'original': (2239, 'd0e5fbff3b66a826e2200908477affd238dc8f320ade3c922c73d25837f4b906'), 'prior': None, 'leafTarget': 174,
        'expected': {'rows': ['[42]', '[43]'], 'subitems': [['1001', '1000000']], 'allocation': [], 'ct10': '1000000', 'ct11': '0', 'ct3a_1': '2026-11-13', 'ct3a_2': '0', 'ct3b': '0'}},
    # L7 KỲ THÁNG 3/2026 (HTKK takes monthly 05/KK-TNCN until tháng 3/2026): the increase case on a month, its own period.
    '05KK-khbs-increase-M03-2026': {'producerCase': 'kk05-khbs-increase-m03-2026', 'menuId': 'L7', 'soLan': 1, 'web': (6360, '363acc5436766fd2da5e3d64d93113f7ceb3ebf3b13ce21d261f90269bc9d78d'), 'original': (2004, '6dceb1348089e9ccd1d3fb4e7dcc8b25a7c8ca488bcb9716e84fdef430d78be1'), 'prior': None, 'leafTarget': 213,
        'period': ('M', '03/2026', '01/03/2026', '31/03/2026'),
        'expected': {'rows': ['[21]', '[22]', '[26]', '[27]', '[29]', '[30]'], 'subitems': [['1001', '1000000']], 'allocation': [], 'ct10': '1000000', 'ct11': '0', 'ct3a_1': '2026-11-13', 'ct3a_2': '207', 'ct3b': '62100'}},
    '05KK-PBT-khbs-Q3-2026': {'producerCase': 'kk05-pbt-khbs-q3-2026', 'menuId': 'L7', 'soLan': 1, 'web': (7460, 'f27e9cf3168a94295e6a80344d7e983ef45554fc3260bd1b5aaa7e9252bcb806'), 'original': (3541, '7f42c909ac6ba799691bf3f560211ce3fb20b4fa94a52ad7b4cc5c5fda70c69e'), 'prior': None, 'leafTarget': 230,
        'annexParts': (PBT,), 'inputMode': IMPORT_TICK,
        'expected': {'rows': ['[29]', '[30]', '[14]'], 'subitems': [['1001', '1000000']], 'allocation': [['00001', '10300', '1000000']], 'ct10': '1000000', 'ct11': '1000000', 'ct3a_1': '2026-11-13', 'ct3a_2': '14', 'ct3b': '4200'}},
    # The 05-1/PBT case with the branch's MST (ct08) empty (TT80 does not require it): its 01-1/KHBS key starts with an empty part,
    # written trimmed by the web file (htkk_web lib/htkk-khbs-fragments.ts dotNetTrim) as HTKK exports cells; Muc_I.2 MST empty.
    '05KK-PBT-nomst-khbs-Q3-2026': {'producerCase': 'kk05-pbt-nomst-khbs-q3-2026', 'menuId': 'L7', 'soLan': 1, 'web': (7431, 'b04f39670dc346f449478eb09c0c3b63473ed847e941e8448c7aab4f5f50c68e'), 'original': (3545, 'af7979790358175e67f9e7751902827db28e2376ffe04d29cea97c984b0b97b3'), 'prior': None, 'leafTarget': 230,
        'annexParts': (PBT,), 'inputMode': IMPORT_TICK,
        'expected': {'rows': ['[29]', '[30]', '[14]'], 'subitems': [['1001', '1000000']], 'allocation': [['', '10300', '1000000']], 'ct10': '1000000', 'ct11': '1000000', 'ct3a_1': '2026-11-13', 'ct3a_2': '14', 'ct3b': '4200'}},
}
for _spec in CASES.values():
    _spec.setdefault('annexParts', ())
    _spec.setdefault('inputMode', IMPORT)
    _spec['producer'], _spec['exporter'] = PRODUCER, EXPORTER
