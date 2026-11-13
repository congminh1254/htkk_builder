"""Offline contract for the 03/TNDN and BCTC candidate cases; no network or native run."""
import hashlib, importlib.util, json, pathlib, unittest
ROOT = pathlib.Path(__file__).parent
def load(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / file); module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module
w = load('workbook_native_cases_test', 'htkk_workbook_native_cases.py')
registry = load('native_cases_registry_test', 'htkk_native_cases.py')
# Pinned to htkk_web data/htkk-workbook-native-cases.json (work/tndn03-native-diff).
WEB_SHA256 = 'b1244004ea9c9f3ce323c41630ebaea819b2f60cee29530f0c9f9cd55593a417'

class WorkbookNativeCases(unittest.TestCase):
    def plan(self): return json.loads(w.PLAN_FILE.read_text(encoding='utf-8'))
    def rejects(self, mutate, reason=None):
        value = self.plan(); mutate(value)
        with self.assertRaises(ValueError) as caught: w.validate(json.dumps(value, ensure_ascii=False).encode())
        if reason: self.assertEqual(str(caught.exception), reason)
    def test_copy_is_the_reviewed_web_plan(self):
        self.assertEqual(hashlib.sha256(w.PLAN_FILE.read_bytes()).hexdigest(), WEB_SHA256)
        self.assertEqual([c['caseId'] for c in w.PLAN['cases']], ['03TNDN-profit20-Y2025', '03TNDN-loss-c3b-Y2025', 'BCTC133-B01a-basic-Y2025', 'BCTC200-LT-basic-Y2025'])
    def test_not_dispatchable_until_a_driver_exists(self):
        self.assertFalse(w.PLAN['driverImplemented'])
        # The design plan stays design-only; three of its cases are promoted separately through
        # the reviewed declaration driver (releaseGate false), the C3b loss case is not.
        promoted = set(c['caseId'] for c in w.PLAN['cases']) & set(registry.CASES)
        self.assertEqual(promoted, {'03TNDN-profit20-Y2025', 'BCTC133-B01a-basic-Y2025', 'BCTC200-LT-basic-Y2025'})
        for case in promoted: self.assertEqual(registry.driver(case), 'declaration-web-import-inspect'); self.assertIs(registry.CASES[case]['releaseGate'], False)
        workflow = (ROOT.parent / '.github/workflows/probe-htkk-windows.yml').read_text(encoding='utf-8')
        self.assertNotIn('03TNDN-loss-c3b-Y2025', workflow)
        self.assertTrue(all((a['menuId'] == 'D1') == (a['driver'] == 'gtgt-web-import-inspect') for a in registry.ADAPTERS.values()))
    def test_gates_and_synthetic_identity(self):
        self.rejects(lambda v: v.update(driverImplemented=True), 'WORKBOOK_CASE_GATE')
        self.rejects(lambda v: v.update(nativeQualified=True), 'WORKBOOK_CASE_GATE')
        self.rejects(lambda v: v['header'].update(taxId='0100109106'), 'WORKBOOK_CASE_PRIVACY')
        self.rejects(lambda v: v['cases'][3]['overrides']['01'].update(F251='Nguyễn Văn Thật'), 'WORKBOOK_CASE_PRIVACY')
        self.rejects(lambda v: v['cases'][0]['overrides']['03'].update(O38='1.5'), 'WORKBOOK_CASE_PRIVACY')
    def test_menu_unit_period_and_appendices(self):
        self.rejects(lambda v: v['cases'][0].update(menuId='D1'), 'WORKBOOK_CASE_MENU')
        self.rejects(lambda v: v['cases'][0].update(xmlVersion='2.9.2'))
        self.rejects(lambda v: v['cases'][0]['period'].update(year=2027), 'WORKBOOK_CASE_PERIOD')
        self.rejects(lambda v: v['cases'][0].update(selected=['03-6']))
        self.rejects(lambda v: v['cases'][2].update(selected=['01-4']), 'WORKBOOK_CASE_0485')
        self.rejects(lambda v: v['cases'][2].update(selected=['01-1']), 'WORKBOOK_CASE_0485')
        self.rejects(lambda v: v['cases'][0]['overrides']['03'].update(G14='C11'), 'WORKBOOK_CASE_PRIVACY')
        self.rejects(lambda v: v['cases'][0]['expected'].update({'HSoThueDTu/HSoKhaiThue/TTinChung/x': '1'}))
        self.rejects(lambda v: v.update(cases=[c for c in v['cases'] if c['caseId'] != '03TNDN-loss-c3b-Y2025']), 'WORKBOOK_CASE_COVERAGE')
        self.rejects(lambda v: v.update(extra=1))
        with self.assertRaises(ValueError): w.validate(b'{"format":"a","format":"b"}')
    def test_rate_plan_copy_is_the_reviewed_web_plan_on_the_582_oracle(self):
        # Pinned to htkk_web data/htkk-workbook-native-cases-582.json (work/tndn-rates): 03/TNDN C7 rate 15 and 17 percent.
        self.assertEqual(hashlib.sha256(w.PLAN_582_FILE.read_bytes()).hexdigest(), '08601c0aa4e639e30600aa85b429db46445673f6b2ca30e87b680e1a16650ab1')
        self.assertEqual([(c['caseId'], c['overrides']['03']['C66']) for c in w.PLAN_582['cases']], [('03TNDN-rate15-Y2025', '15'), ('03TNDN-rate17-Y2025', '17')])
        for case in ('03TNDN-rate15-Y2025', '03TNDN-rate17-Y2025'):
            self.assertEqual(registry.htkk_version(case), '5.8.2'); self.assertEqual(registry.driver(case), 'declaration-web-import-inspect')
            self.assertIs(registry.CASES[case]['releaseGate'], False); self.assertEqual(registry.CASES[case]['adapterId'], '03-tndn-2.9.4')
        raw = w.PLAN_582_FILE.read_bytes()
        def rejects(mutate, reason=None):
            value = json.loads(raw); mutate(value)
            with self.assertRaises(ValueError) as caught: w.validate(json.dumps(value, ensure_ascii=False).encode(), '5.8.2')
            if reason: self.assertEqual(str(caught.exception), reason)
        rejects(lambda v: v['cases'][0]['overrides']['03'].update(C66='20'), 'WORKBOOK_CASE_RATE')
        rejects(lambda v: v['cases'][0]['overrides']['03'].update(C66='25'), 'WORKBOOK_CASE_RATE')
        rejects(lambda v: v['cases'][0]['overrides']['03'].pop('C66'), 'WORKBOOK_CASE_RATE')
        rejects(lambda v: v['cases'][0]['expected'].update({w.RATE_PATH + 'thueSuat': '17'}), 'WORKBOOK_CASE_RATE')
        rejects(lambda v: v['cases'][1]['expected'].update({w.RATE_PATH + 'tenThueSuat': w.RATE_NAMES['15']}), 'WORKBOOK_CASE_RATE')
        rejects(lambda v: v['cases'][1]['overrides']['03'].update(C66='15'), 'WORKBOOK_CASE_RATE')
        rejects(lambda v: v.update(cases=v['cases'][:1]), 'WORKBOOK_CASE_COVERAGE')
        rejects(lambda v: v['cases'][0]['period'].update(year=2024), 'WORKBOOK_CASE_PERIOD')
        rejects(lambda v: v['header'].update(taxId='0100109106'), 'WORKBOOK_CASE_PRIVACY')
        rejects(lambda v: v.update(htkkVersion='5.8.1'))
        # The 5.8.1 design plan may not choose a rate at all.
        value = json.loads(w.PLAN_FILE.read_bytes()); value['cases'][0]['overrides']['03']['C66'] = '15'
        with self.assertRaises(ValueError) as caught: w.validate(json.dumps(value, ensure_ascii=False).encode())
        self.assertEqual(str(caught.exception), 'WORKBOOK_CASE_RATE')

    def test_units_follow_menu_xml(self):
        self.assertEqual({k: (u['maTKhai'], u['xmlVersion'], u['kieuKy']) for k, u in w.UNITS.items()}, {'N8': ('892', '2.9.4', '11'), 'A2': ('683', '2.3.2', '26'), '78': ('402', '2.2.6', '26')})
        self.assertEqual(w.UNITS['N8']['menuChain'], ['101', '101_2', 'N8'])

if __name__ == '__main__': unittest.main()
