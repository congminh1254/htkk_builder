"""Per-case taxpayer profile CQT and period-dialog place of a declaration native case (optional registry fields of
htkk-native-cases.json). Absent = the fixed synthetic values every case used before, so those cases run unchanged:

  taxpayerProfile  {"taxOfficeHead", "taxOffice"}: the profile's Thuế tỉnh/CCT (HEADER maCQTCapCuc) and CQT quản lý
                   (maCQTNoiNop). The profile's tỉnh and xã stay the fixed synthetic ones (101 / 10129087).
  periodLocation   {"province", "ward", "taxOfficeHead", "taxOffice"}: what the period dialog selects in cboTinh, cboXa,
                   cboCQTCuc and cboCQTChiCuc (TTPeriodInfo MaTinh, MaXa, maCQTCapCuc, maCQTQuanLy).

Places: the public HTKK catalogues InterfaceIni/Catalogue_Dia_Ban_Tinh_Moi.xml, Catalogue_Dia_Ban_Xa_Moi.xml and
Catalogue_CQT_Dia_Ban.xml (SHA-256 pinned in htkk-source-extract-policy.json), copied as htkk_web
data/htkk-taxpayer-profile.json lists them, as htkk_annex12_web_cases.py and HtkkGtgtAnnex12ExportInspection.cs do. Only these
reviewed places can be named; anything else fails closed. Offices offered for a ward follow the two pinned period-dialog
loaders (htkk-oracle-baselines.json pbt-582-cuc-items / pbt-582-office-items, same IL in 5.8.4 and 5.8.5):
  GeneralFunctions.loadCqtCapCucTheoDiaBanXa(xã): a blank item, the cấp cục of the xã's office (MaCQT[0..3] + "00"), 82500, 82700;
  GeneralFunctions.loadCqtCapChiCucTheoDiaBanXa(cấp cục, xã): 82500 / 82700 alone, otherwise the cấp cục and the xã's office.
frmHTKKPeriod.btnDongY_Click refuses (0611) a CQT quản lý other than the profile's for TieuMucHachToan "00", so the period's
taxOffice must equal the profile's. HtkkDeclarationCasePlans.cs Geography() compiles the same values (with the catalogue names
the original combos show); test_case_geography.py keeps the two equal.
"""

PROVINCES = {'101': 'Thành phố Hà Nội', '103': 'Thành phố Hải Phòng'}
# xã -> (tỉnh, name, CQT of the xã)
WARDS = {'10129087': ('101', 'Phường Sơn Tây', '10129'), '10309019': ('103', 'Phường Đồ Sơn', '10309')}
OFFICES = {'10100': 'Thuế Thành phố Hà Nội', '10129': 'Thuế cơ sở 16 Thành phố Hà Nội', '10300': 'Thuế Thành phố Hải Phòng',
           '10309': 'Thuế cơ sở 6 Thành phố Hải Phòng', '82500': 'Chi cục Thuế doanh nghiệp lớn', '82700': 'Chi cục Thuế Thương mại điện tử'}
NATIONWIDE = ('82500', '82700')
PROFILE_PROVINCE, PROFILE_WARD = '101', '10129087'
DEFAULT_PROFILE = {'taxOfficeHead': '10100', 'taxOffice': '10129'}
DEFAULT_LOCATION = {'province': '101', 'ward': '10129087', 'taxOfficeHead': '10100', 'taxOffice': '10129'}
FIELDS = ('taxpayerProfile', 'periodLocation')


def check(value):
    if not value:
        raise ValueError('CASE_POLICY')


def head_offices(ward):
    """loadCqtCapCucTheoDiaBanXa without its blank item."""
    check(ward in WARDS)
    return [WARDS[ward][2][:3] + '00', *NATIONWIDE]


def managing_offices(head, ward):
    """loadCqtCapChiCucTheoDiaBanXa."""
    check(ward in WARDS and head in head_offices(ward))
    return [head] if head in NATIONWIDE else [head, WARDS[ward][2]]


def _codes(value, keys):
    check(type(value) is dict and set(value) == set(keys) and all(type(value[k]) is str for k in keys))
    return value


def geography(case):
    """(profile, location) of one registry case, defaults filled in; refuses any place HTKK would not offer."""
    check(type(case) is dict)
    profile = dict(_codes(case.get('taxpayerProfile', DEFAULT_PROFILE), DEFAULT_PROFILE))
    location = dict(_codes(case.get('periodLocation', DEFAULT_LOCATION), DEFAULT_LOCATION))
    # The profile sheet offers the same two lists for its own (fixed) xã.
    check(profile['taxOfficeHead'] in head_offices(PROFILE_WARD) and profile['taxOffice'] in managing_offices(profile['taxOfficeHead'], PROFILE_WARD))
    ward = location['ward']
    check(location['province'] in PROVINCES and ward in WARDS and WARDS[ward][0] == location['province'])
    check(location['taxOfficeHead'] in head_offices(ward) and location['taxOffice'] in managing_offices(location['taxOfficeHead'], ward))
    check(location['taxOffice'] == profile['taxOffice'])  # 0611
    return profile, location


def is_default(case):
    return geography(case) == (DEFAULT_PROFILE, DEFAULT_LOCATION)


def compiled(case):
    """The twelve strings HtkkDeclarationCasePlans.Geography compiles: profile Thuế tỉnh/CCT code and name, CQT quản lý code and
    name; period tỉnh, xã, Thuế tỉnh/CCT, CQT quản lý, each code and name."""
    profile, location = geography(case)
    return (profile['taxOfficeHead'], OFFICES[profile['taxOfficeHead']], profile['taxOffice'], OFFICES[profile['taxOffice']],
            location['province'], PROVINCES[location['province']], location['ward'], WARDS[location['ward']][1],
            location['taxOfficeHead'], OFFICES[location['taxOfficeHead']], location['taxOffice'], OFFICES[location['taxOffice']])
