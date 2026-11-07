"""Offline synthetic fixtures for declaration-family cases (never native evidence).

The XML is assembled in memory from the reviewed contract in htkk_declaration_web_cases.py
(identity, period, oracle leaves, annex elements, leaf count). It is not a captured product
or original export; it only exercises the allowlist, transport and staging boundaries.
"""
import hashlib, importlib.util, pathlib
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).parent


def _load(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / file)
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value); return value


d = _load('declaration_fixture_contract', 'htkk_declaration_web_cases.py')
registry = _load('declaration_fixture_registry', 'htkk_native_cases.py')
NS = d.NS
PRODUCER = b'// Fixed synthetic declaration test producer, never executed.\n'


def _add(parent, name, text=None, attrib=None):
    node = ET.SubElement(parent, '{%s}%s' % (NS, name), attrib or {})
    if text is not None:
        node.text = text
    return node


def _path(root, path):
    node = root
    for name in path.split('/')[1:]:
        found = node.find('{%s}%s' % (NS, name))
        node = found if found is not None else _add(node, name)
    return node


def _tree(case_id, native=False, created=None):
    spec = d.case(case_id)
    ET.register_namespace('', NS); ET.register_namespace('xsi', d.XSI)
    root = ET.Element('{%s}HSoThueDTu' % NS)
    hs = _add(root, 'HSoKhaiThue', attrib={'id': 'ID_1'})
    common = _add(hs, 'TTinChung')
    service = _add(common, 'TTinDVu')
    values = (*d.NATIVE_SERVICE, 'A' * 32) if native else spec['webService']
    for name, value in zip(d.SERVICE_NAMES, values):
        _add(service, name, value)
    tt = _add(common, 'TTinTKhaiThue'); tk = _add(tt, 'TKhaiThue')
    for name, value in (('maTKhai', spec['maTKhai']), ('pbanTKhaiXML', spec['xmlVersion']), ('loaiTKhai', 'C'), ('soLan', '0')):
        _add(tk, name, value)
    period = _add(tk, 'KyKKhaiThue')
    for name, value in (('kieuKy', spec['kieuKy']), ('kyKKhai', spec['kyKKhai']), ('kyKKhaiTuNgay', spec['tuNgay']), ('kyKKhaiDenNgay', spec['denNgay'])):
        _add(period, name, value)
    _add(tk, 'ngayLapTKhai', created or spec['createdDate']); _add(tk, 'nguoiKy', d.SIGNER); _add(tk, 'ngayKy', spec['ngayKy'])
    nnt = _add(tt, 'NNT'); _add(nnt, 'mst', d.MST); _add(nnt, 'tenNNT', d.NAME)
    main = _add(hs, 'CTieuTKhaiChinh')
    family = spec['family']
    if family == 'workbook':
        for path, value in d._workbook_expected[case_id].items():
            _path(root, path).text = value
    elif family == 'descriptor':
        values, rows = d._descriptor_expected[case_id]
        # 01/NTNN table totals are written under their own parent below (mục II under ThueNCCNN_CNKCT).
        owned = {leaf for _, _, _, totals in (d.ntnn_tables(case_id) if case_id in d.NTNN_ROWS else ()) for leaf in totals}
        if case_id in d.NTNN04:  # 04/NTNN: every oracle row leaf (Group/leaf) under CTieuTKhaiChinh
            owned = set(values)
            for path, value in d.ntnn04_expected(case_id)[0].items():
                _path(main, 'CTieuTKhaiChinh/' + path).text = value
        for name, value in values.items():
            if name not in owned:
                _add(main, name, value)
        if case_id in d.NTNN_ROWS:  # 01/NTNN tables of the reviewed design (row id attribute as in the template)
            for row_path, parent_path, rows, totals in d.ntnn_tables(case_id):
                parent = _path(root, 'HSoThueDTu/' + parent_path)
                table = _path(root, 'HSoThueDTu/' + row_path.rsplit('/', 1)[0])
                name = row_path.rsplit('/', 1)[1]
                for index, row in enumerate(rows):
                    node = _add(table, name, attrib={('ID' if name == 'ThueNTNN' else 'id'): 'ID_%d' % (index + 1)})
                    for leaf, value in row.items():
                        _add(node, leaf, value)
                for leaf, value in totals.items():
                    _add(parent, leaf, value)
        pluc = _add(hs, 'PLuc')
        for annex in spec['annexElements']:
            node = _add(pluc, annex)
            if case_id in d.NTNN04:  # 02-2/NTNN subcontractor rows and totals of the oracle
                table = _add(node, 'BKCacNTPhu')
                for index, (ct9, ct10) in enumerate(d.NTNN04[case_id][3]):
                    row = _add(table, 'CTietBKCacNTPhu', attrib={'id': 'ID_%d' % (index + 1)}); _add(row, 'ct9', ct9); _add(row, 'ct10', ct10)
                for leaf, value in d.ntnn04_expected(case_id)[1].items():
                    _add(node, leaf, value)
                continue
            for key, count in rows.items():
                if key.split('/')[0] == annex:
                    for index in range(count):
                        _add(_add(node, key.split('/')[1], attrib={'id': 'ID_%d' % (index + 1)}), 'ct08', '0')
    else:
        exp = d.hkd_design.expected(case_id)
        _add(main, 'mst_cu', d.MST)
        for i in range(len(exp['ct14_soThue'])):
            r = _add(main, 'CTietDoanhThu')
            _add(r, 'ct10', exp['ct10'][i]); _add(r, 'ct14_soThue', exp['ct14_soThue'][i]); _add(r, 'ct17_soThue', exp['ct17_soThue'][i])
        _add(main, 'soThueGTGT_ct14', exp['soThueGTGT_ct14'][0]); _add(main, 'soThueTNCN_ct17', exp['soThueTNCN_ct17'][0])
        for i in range(len(exp['ct40'])):
            row = _add(main, 'ChiTietThongTinNopTHue')
            for name in ('ct38_ma', 'ct40', 'ct42_ma', 'ct46'):
                _add(row, name, exp[name][i])
        _add(main, 'tongTienCT47', exp['tongTienCT47'][0])
    if family == 'workbook':
        pluc = hs.find('{%s}PLuc' % NS)
        if pluc is not None:  # keep PLuc after the main body, in reviewed annex order
            hs.remove(pluc); hs.append(pluc)
            # Annexes without an oracle leaf (e.g. LCTTGT of the TT200 case) still appear in order.
            present = {child.tag: child for child in pluc}
            for child in list(pluc):
                pluc.remove(child)
            for annex in spec['annexElements']:
                tag = '{%s}%s' % (NS, annex)
                node = present.get(tag)
                if node is None:
                    node = ET.Element(tag); _add(node, 'ct01', '0')
                pluc.append(node)
    count = len(d.leaves(root))
    filler = _add(main, 'Filler')
    for index in range(spec['leafCount'] - count):
        _add(filler, 'pad%d' % index, '0')
    return root


def declaration_fixture(case_id, native=False, created=None):
    root = _tree(case_id, native, created)
    text = ET.tostring(root, encoding='unicode')
    prefix = '<?xml version="1.0" encoding="UTF-8"?>\n'
    if not native and d.case(case_id)['family'] != 'descriptor':
        prefix = d.PREAMBLE
    return (prefix + text).encode('utf-8')


def declaration_manifest(body, case_id, producer_sha=None, source='a' * 40):
    spec = d.case(case_id); c = registry.CASES[case_id]
    return {'format': c['format'], 'sourceRepository': 'htkk-net/htkk_web', 'sourceCommit': source, 'sourceVersion': '0.9.2', 'caseId': case_id,
            'menuId': spec['menuId'], 'engine': spec['family'], 'xmlVersion': spec['xmlVersion'], 'schemaId': spec['schemaId'], 'annexes': c['unit']['annexes'],
            'inputsSynthetic': True, 'exporter': 'lib/htkk-declaration-engines.ts', 'producer': 'scripts/generate-htkk-declaration-reference.mjs',
            'producerSha256': producer_sha or hashlib.sha256(PRODUCER).hexdigest(), 'xmlSha256': hashlib.sha256(body).hexdigest(), 'bytes': len(body),
            'leafCount': spec['leafCount'], 'nativeQualified': False, 'filingEnabled': False}
