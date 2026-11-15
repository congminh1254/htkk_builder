"""Synthetic in-memory files for the 01/NTNN and 05/KK-TNCN kê khai bổ sung contract tests (htkk_ntnn_khbs_web_cases.py).

The reviewed producer files stay private: this public repository keeps only their pins. Tests therefore assemble small
synthetic files of the same shape here and pin THEIR sizes, SHA-256 and leaf counts into the module instance under test
(``pin``). They are not product output, not an HTKK export and never native evidence."""
import hashlib

ROLES = ('original', 'prior', 'web')


def _tk(m, case_id, role):
    spec = m.CASES[case_id]
    ma, version = m.MENUS[spec['menuId']]
    kind, period, start, end = m.period_of(spec)
    loai, lan = ('C', '0') if role == 'original' else ('B', str(spec['soLan'] - (1 if role == 'prior' else 0)))
    return ('<TKhaiThue><maTKhai>%s</maTKhai><tenTKhai>TO KHAI GIA LAP KIEM THU</tenTKhai><pbanTKhaiXML>%s</pbanTKhaiXML>'
            '<loaiTKhai>%s</loaiTKhai><soLan>%s</soLan><KyKKhaiThue><kieuKy>%s</kieuKy><kyKKhai>%s</kyKKhai>'
            '<kyKKhaiTuNgay>%s</kyKKhaiTuNgay><kyKKhaiDenNgay>%s</kyKKhaiDenNgay></KyKKhaiThue><ngayLapTKhai>%s</ngayLapTKhai>'
            '<nguoiKy>%s</nguoiKy><ngayKy>%s</ngayKy></TKhaiThue>') % (ma, version, loai, lan, kind, period, start, end, m.FIXED_DATE, m.SIGNER, m.FIXED_DATE), lan


def synthetic(m, case_id, role):
    """One synthetic staged file: web service identity, synthetic NNT, the case's identity/period/lần and, for a B file, the
    two KHBS annex parts. The web B file carries the case's expected ct10 so a comparison can change one amount."""
    spec = m.CASES[case_id]
    tk, lan = _tk(m, case_id, role)
    amount = {'original': '0', 'prior': '1000', 'web': spec['expected']['ct10']}[role]
    service = ''.join('<%s>%s</%s>' % (name, value, name) for name, value in zip(('maDVu', 'tenDVu', 'pbanDVu', 'ttinNhaCCapDVu'), m.SERVICE))
    # The case's own annexes (05/KK-TNCN 05-1/PBT) come first in PLuc, then the two KHBS fragments of a B file.
    annexes = ''.join('<%s><ct14>%s</ct14></%s>' % (part, amount, part) for part in spec['annexParts'])
    khbs = '' if role == 'original' else (
        '<PL01_KHBS><Header><soLan>%s</soLan><mst>%s</mst></Header><ct10>%s</ct10></PL01_KHBS>'
        '<PL01_1_KHBS><Header><soLan>%s</soLan><mst>%s</mst></Header><ct3_2_ten>CHI TIEU GIA LAP</ct3_2_ten></PL01_1_KHBS>') % (lan, m.MST, amount, lan, m.MST)
    pluc = '<PLuc>' + annexes + khbs + '</PLuc>' if annexes or khbs else ''
    body = ('<HSoThueDTu xmlns="%s" xmlns:xsi="%s"><HSoKhaiThue id="ID_1"><TTinChung><TTinDVu>%s</TTinDVu><TTinTKhaiThue>%s'
            '<NNT><mst>%s</mst><tenNNT>%s</tenNNT></NNT></TTinTKhaiThue></TTinChung><CTieuTKhaiChinh><ct1a>NHA THAU GIA LAP</ct1a>'
            '<ct3>HD-GL-101</ct3><ct10>%s</ct10></CTieuTKhaiChinh>%s</HSoKhaiThue></HSoThueDTu>') % (m.NS, m.XSI, service, tk, m.MST, m.NAME, amount, pluc)
    return (m.PREAMBLE[:m.PREAMBLE.index('<HSoThueDTu ')] + body).encode('utf-8')


def files(m, case_id):
    """The staged XML files of a case by staged name."""
    names = {'original': m.ORIGINAL_NAME, 'prior': m.PRIOR_NAME, 'web': m.WEB_NAME}
    return {names[role]: synthetic(m, case_id, role) for role in ROLES if m.CASES[case_id][role]}


def pin(m):
    """Pin the synthetic files into this module instance (sizes, SHA-256, web leaf target). Idempotent."""
    leaves = m.declaration().leaves
    parse = m.declaration()._parse
    for case_id, spec in m.CASES.items():
        for role in ROLES:
            if spec[role]:
                body = synthetic(m, case_id, role)
                spec[role] = (len(body), hashlib.sha256(body).hexdigest())
        spec['leafTarget'] = len(leaves(parse(synthetic(m, case_id, 'web'), True))) - 4
    return m
