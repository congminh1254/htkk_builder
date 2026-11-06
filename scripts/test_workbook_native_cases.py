"""Offline contract for the 03/TNDN and BCTC candidate cases; no network or native run."""
import hashlib, importlib.util, json, pathlib, unittest
ROOT = pathlib.Path(__file__).parent
def load(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / file); module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module
w = load('workbook_native_cases_test', 'htkk_workbook_native_cases.py')
registry = load('native_cases_registry_test', 'htkk_native_cases.py')
# Pinned to htkk_web data/htkk-workbook-native-cases.json (work/forms-tndn).
WEB_SHA256 = 'bd0d80ad45ef5d49efc33e095555fa5c03e21fc0b2355175cc49d2ae7a8efc5b'

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
        self.assertTrue(set(c['caseId'] for c in w.PLAN['cases']).isdisjoint(registry.CASES))
        workflow = (ROOT.parent / '.github/workflows/probe-htkk-windows.yml').read_text(encoding='utf-8')
        for case in w.PLAN['cases']: self.assertNotIn(case['caseId'], workflow)
        self.assertTrue(all(a['menuId'] == 'D1' for a in registry.ADAPTERS.values()))
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
        self.rejects(lambda v: v['cases'][2].update(selected=['01-4']))
        self.rejects(lambda v: v['cases'][0]['expected'].update({'HSoThueDTu/HSoKhaiThue/TTinChung/x': '1'}))
        self.rejects(lambda v: v.update(cases=[c for c in v['cases'] if c['caseId'] != '03TNDN-loss-c3b-Y2025']), 'WORKBOOK_CASE_COVERAGE')
        self.rejects(lambda v: v.update(extra=1))
        with self.assertRaises(ValueError): w.validate(b'{"format":"a","format":"b"}')
    def test_units_follow_menu_xml(self):
        self.assertEqual({k: (u['maTKhai'], u['xmlVersion'], u['kieuKy']) for k, u in w.UNITS.items()}, {'N8': ('892', '2.9.4', '11'), 'A2': ('683', '2.3.2', '26'), '78': ('402', '2.2.6', '26')})
        self.assertEqual(w.UNITS['N8']['menuChain'], ['101', '101_2', 'N8'])

if __name__ == '__main__': unittest.main()
