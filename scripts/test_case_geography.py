"""Offline contracts of the per-case taxpayer profile CQT and period-dialog place (registry fields taxpayerProfile and
periodLocation, htkk_case_geography.py, HtkkDeclarationCasePlans.Geography). Every case without the fields keeps the fixed
synthetic values; a case with them names only places HTKK's pinned loaders offer. No network, no native evidence: whether HTKK
accepts the place is decided by a Windows run.
"""
import copy, importlib.util, json, pathlib, re, tempfile, unittest

ROOT = pathlib.Path(__file__).parent


def load(name, file, folder=ROOT):
    spec = importlib.util.spec_from_file_location(name, folder / file); module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module


g = load('case_geography_test', 'htkk_case_geography.py')
registry = load('case_geography_registry_test', 'htkk_native_cases.py')
RAW = json.loads((ROOT / 'htkk-native-cases.json').read_text())
PLANS = (ROOT / 'HtkkDeclarationCasePlans.cs').read_text(encoding='utf-8')
CASE = '01GTGT-TT89-other-province-M10-2026'
DEFAULT = ('10100', 'Thuế Thành phố Hà Nội', '10129', 'Thuế cơ sở 16 Thành phố Hà Nội', '101', 'Thành phố Hà Nội', '10129087', 'Phường Sơn Tây',
           '10100', 'Thuế Thành phố Hà Nội', '10129', 'Thuế cơ sở 16 Thành phố Hà Nội')
OTHER = ('82500', 'Chi cục Thuế doanh nghiệp lớn', '82500', 'Chi cục Thuế doanh nghiệp lớn', '103', 'Thành phố Hải Phòng', '10309019', 'Phường Đồ Sơn',
         '82500', 'Chi cục Thuế doanh nghiệp lớn', '82500', 'Chi cục Thuế doanh nghiệp lớn')


def compiled_table():
    """HtkkDeclarationCasePlans.Geography: case id (None = default) -> the twelve compiled strings."""
    body = re.search(r'internal static HtkkCaseGeography Geography\(string caseId\)\{(.*?)\n \}\n', PLANS, re.S).group(1)
    table = {}
    for label, values in re.findall(r'(case "[^"]+"|default):return new HtkkCaseGeography\(new string\[\]\{([^}]*)\}\);', body):
        table[None if label == 'default' else label[6:-1]] = tuple(re.findall(r'"([^"]*)"', values))
    return table


class Places(unittest.TestCase):
    def test_the_period_loaders_offer_what_the_pinned_il_review_says(self):
        # loadCqtCapCucTheoDiaBanXa: the cấp cục of the xã's office (MaCQT[0..3] + "00"), 82500, 82700.
        self.assertEqual(g.head_offices('10309019'), ['10300', '82500', '82700'])
        self.assertEqual(g.head_offices('10129087'), ['10100', '82500', '82700'])
        # loadCqtCapChiCucTheoDiaBanXa: 82500 / 82700 alone, otherwise the cấp cục and the xã's office.
        self.assertEqual(g.managing_offices('82500', '10309019'), ['82500'])
        self.assertEqual(g.managing_offices('10300', '10309019'), ['10300', '10309'])
        self.assertEqual(g.managing_offices('10100', '10129087'), ['10100', '10129'])
        # So CQT quản lý 82500 in Phường Đồ Sơn is reached only through Thuế tỉnh/CCT 82500.
        self.assertEqual([h for h in g.head_offices('10309019') if '82500' in g.managing_offices(h, '10309019')], ['82500'])

    def test_defaults_are_the_fixed_synthetic_values(self):
        self.assertEqual(g.compiled({}), DEFAULT)
        self.assertTrue(g.is_default({}))
        self.assertTrue(g.is_default({'taxpayerProfile': dict(g.DEFAULT_PROFILE), 'periodLocation': dict(g.DEFAULT_LOCATION)}))

    def test_refuses_any_place_htkk_would_not_offer(self):
        profile = {'taxOfficeHead': '82500', 'taxOffice': '82500'}
        location = {'province': '103', 'ward': '10309019', 'taxOfficeHead': '82500', 'taxOffice': '82500'}
        self.assertEqual(g.compiled({'taxpayerProfile': profile, 'periodLocation': location}), OTHER)
        bad = [
            ({**profile}, {**location, 'taxOfficeHead': '10300'}),            # 82500 is not under 10300
            ({**profile}, {**location, 'taxOfficeHead': '10100'}),            # not offered for a Hải Phòng xã
            (dict(g.DEFAULT_PROFILE), location),                              # 0611: period CQT is not the profile's
            ({**profile}, {**location, 'province': '101'}),                   # the xã is not in that tỉnh
            ({**profile}, {**location, 'ward': '10309018'}),                  # not a reviewed place
            ({**profile}, {**location, 'province': '999'}),
            ({'taxOfficeHead': '10300', 'taxOffice': '10309'}, {**location, 'taxOfficeHead': '10300', 'taxOffice': '10309'}),  # profile xã 10129087
            ({'taxOfficeHead': '82500', 'taxOffice': '10129'}, dict(g.DEFAULT_LOCATION)),  # 10129 is not under 82500
            ({**profile, 'extra': '1'}, location), ({'taxOffice': '82500'}, location), ({**profile}, {**location, 'ward': 10309019}),
            ([], location), (profile, None),
        ]
        for p, l in bad:
            with self.subTest(profile=p, location=l), self.assertRaises(ValueError):
                g.geography({'taxpayerProfile': p, 'periodLocation': l})


class Registry(unittest.TestCase):
    def test_only_the_other_province_case_carries_a_place_and_every_other_case_keeps_the_defaults(self):
        self.assertEqual(registry.GEOGRAPHY_CASES, (CASE,))
        self.assertEqual(g.compiled(registry.CASES[CASE]), OTHER)
        for case_id, case in registry.CASES.items():
            if case_id != CASE:
                self.assertNotIn('taxpayerProfile', case, case_id); self.assertNotIn('periodLocation', case, case_id)
                self.assertEqual(g.compiled(case), DEFAULT, case_id)

    def test_the_compiled_table_equals_the_registry(self):
        table = compiled_table()
        self.assertEqual(table, {None: DEFAULT, CASE: OTHER})
        self.assertEqual(set(table) - {None}, set(registry.GEOGRAPHY_CASES))
        for case_id in registry.GEOGRAPHY_CASES:
            self.assertEqual(table[case_id], g.compiled(registry.CASES[case_id]))
            self.assertIn('case "' + case_id + '":return new HtkkDeclarationCasePlan(', PLANS)

    def mutated(self, mutate):
        value = copy.deepcopy(RAW); mutate({c['caseId']: c for c in value['cases']})
        with tempfile.TemporaryDirectory() as directory:
            folder = pathlib.Path(directory); (folder / 'htkk-native-cases.json').write_text(json.dumps(value))
            for name in ('htkk_native_cases.py', 'htkk_oracle.py', 'htkk_case_geography.py', 'generate-htkk-oracle-baselines.py', 'htkk-oracle-baselines.json'):
                (folder / name).write_bytes((ROOT / name).read_bytes())
            return load('case_geography_registry_mutated', 'htkk_native_cases.py', folder)

    def test_the_registry_refuses_a_place_outside_declaration_import_cases_or_a_default_spelled_out(self):
        self.assertEqual(self.mutated(lambda c: None).GEOGRAPHY_CASES, (CASE,))  # the copied loader itself is sound
        place = {k: copy.deepcopy(registry.CASES[CASE][k]) for k in g.FIELDS}
        gate = registry.GATE_CASES[0]
        tick = registry.DECLARATION_TICK_CASES[0]
        for mutate in (lambda c: c[gate].update(place),                                   # a release gate
                       lambda c: c[tick].update(place),                                   # an import-tick case
                       lambda c: c['01GTGT-TT89-zero-M10-2026'].update(taxpayerProfile=dict(g.DEFAULT_PROFILE)),  # default spelled out
                       lambda c: c[CASE]['periodLocation'].update(taxOfficeHead='10300'),
                       lambda c: c[CASE].update(periodLocation={'province': '103', 'ward': '10309019', 'taxOfficeHead': '82500'})):
            with self.subTest(), self.assertRaises(ValueError):
                self.mutated(mutate)


class Harness(unittest.TestCase):
    def test_the_profile_and_period_dialog_take_the_case_place(self):
        core = (ROOT / 'HtkkGuiReferenceAutomation.cs').read_text(encoding='utf-8')
        driver = (ROOT / 'HtkkDeclarationWebImport.cs').read_text(encoding='utf-8')
        # Profile: the two CQT combos and their code read-back, and the saved HEADER check.
        self.assertIn('Edit(spread,sheet,33,2,place.ProfileHeadName,true,', core); self.assertIn('Edit(spread,sheet,35,2,place.ProfileOfficeName,true,', core)
        self.assertIn('new string[]{"101","10129087",place.ProfileHeadCode,place.ProfileOfficeCode}', core)
        self.assertIn('expected["maCQTCapCuc"]=place.ProfileHeadCode;expected["maCQTNoiNop"]=place.ProfileOfficeCode;', core)
        self.assertNotIn('"Thuế cơ sở 16 Thành phố Hà Nội"', core)
        # Period dialog of the declaration driver: no fixed place left.
        for combo, code, name in (('cboTinh', 'ProvinceCode', 'ProvinceName'), ('cboXa', 'WardCode', 'WardName'), ('cboCQTCuc', 'HeadCode', 'HeadName'), ('cboCQTChiCuc', 'OfficeCode', 'OfficeName')):
            self.assertIn('SelectGeography(period,"' + combo + '",place.' + code + ',place.' + name + ',', driver)
        self.assertNotIn('"10129087"', driver); self.assertNotIn('"Thuế cơ sở 16 Thành phố Hà Nội"', driver)
        # The case id is read from the staged sidecar once, and the later input check must see the same id.
        self.assertIn('(caseGeographyId!=null&&caseGeographyId!=id)', driver)


if __name__ == '__main__':
    unittest.main()
