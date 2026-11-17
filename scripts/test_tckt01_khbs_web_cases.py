"""Input contract of the 01/TCKT TT89/2026 3.1.0 kê khai bổ sung cases (htkk_tckt01_khbs_web_cases.py, merged into
htkk_ntnn_khbs_web_cases.py). Y7 has KieuKHBS 3 and VersionKHBS 3.1.0 in HTKK 5.8.2: its B files carry the case's bảng kê, then
PL01_KHBS / PL01_1_KHBS, its rounds run "Tổng hợp KHBS", and ngayKy is compared as an export date. Synthetic checks only; the
reviewed producer files stay private (only their sizes and SHA-256 are pinned). Byte-level checks run on a second module instance
pinned to synthetic in-memory files (ntnn_khbs_test_support.py)."""
import hashlib
import importlib.util
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).parent


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


m = load('htkk_ntnn_khbs_web_cases_tckt01', 'htkk_ntnn_khbs_web_cases.py')
tckt01 = load('htkk_tckt01_khbs_web_cases_test', 'htkk_tckt01_khbs_web_cases.py')
support = load('ntnn_khbs_test_support_tckt01', 'ntnn_khbs_test_support.py')
sm = support.pin(load('htkk_ntnn_khbs_web_cases_tckt01_pinned', 'htkk_ntnn_khbs_web_cases.py'))
registry = load('htkk_native_cases_tckt01', 'htkk_native_cases.py')
INCREASE, LAN2, DECREASE, BDS = '01TCKT-310-khbs-hop-tac-kd-Q4-2026', '01TCKT-310-khbs-lan2-hop-tac-kd-Q4-2026', '01TCKT-310-khbs-decrease-hop-tac-kd-Q4-2026', '01TCKT-310-khbs-bds-M10-2026'
CASES = (INCREASE, LAN2, DECREASE, BDS)
HTKD, BDS_ANNEX = 'PLuc_HKD_CNKD', 'PLuc_CANHAN_TTS'
NGAY_KY = 'HSoThueDTu/HSoKhaiThue/TTinChung/TTinTKhaiThue/TKhaiThue/ngayKy'


def manifest(case_id, module):
    c = module.CASES[case_id]
    value = dict(module.manifest_fields(case_id), sourceCommit='0' * 40, producerSha256='1' * 64, bytes=c['web'][0], xmlSha256=c['web'][1],
                 originalBytes=c['original'][0], originalXmlSha256=c['original'][1])
    if c['prior']:
        value.update(priorBytes=c['prior'][0], priorXmlSha256=c['prior'][1])
    return value


class Tckt01KhbsWebCases(unittest.TestCase):
    def test_four_cases_merged_with_their_own_producer_menu_and_period(self):
        self.assertEqual(m.TCKT01_CASES, CASES)
        self.assertEqual(set(tckt01.CASES), set(CASES))
        self.assertFalse((set(m.NTNN_CASES) | set(m.KK05_CASES) | set(m.CNKD_CASES) | set(m.QTT02_CASES) | set(m.QTT05_CASES) | set(m.TNDN03_CASES)) & set(CASES))
        self.assertEqual(m.MENUS['Y7'], ('2007', '3.1.0'))
        self.assertEqual(m.PERIODS['Y7'], ('Q', '4/2026', '01/10/2026', '31/12/2026'))
        self.assertEqual(m.period_of(m.CASES[BDS]), ('M', '10/2026', '01/10/2026', '31/10/2026'))
        for case_id in CASES:
            c = m.CASES[case_id]
            self.assertEqual(m.producer(case_id), 'scripts/generate-htkk-web-tckt01-khbs-reference.mjs')
            self.assertEqual(m.manifest_fields(case_id)['exporter'], 'lib/htkk-tckt01-khbs.ts')
            self.assertEqual(m.names(case_id), (m.ORIGINAL_NAME,) + ((m.PRIOR_NAME,) if case_id == LAN2 else ()) + (m.WEB_NAME, m.MANIFEST_NAME))
            self.assertEqual(m.input_mode(case_id), 'khbs-web-xml-import-reexport')
            self.assertEqual(c['annexParts'], (BDS_ANNEX,) if case_id == BDS else (HTKD,))
            self.assertEqual(c['khbsParts'], ('PL01_KHBS', 'PL01_1_KHBS'))
            self.assertEqual(c['exportDates'], (NGAY_KY,))
            self.assertTrue(m.khbs_summary(case_id))
            self.assertEqual(m.validate_manifest(manifest(case_id, m))['caseId'], case_id)
            self.assertEqual(set(c['expected']), {'rows', 'subitems', 'ct10', 'ct3a_1', 'ct3a_2', 'ct3b'})
            # Quý 4/2026 is due 01/02/2027 and tháng 10/2026 on 20/11/2026: ngày lập 13/11/2026 is before both.
            self.assertEqual((c['expected']['ct3a_1'], c['expected']['ct3a_2'], c['expected']['ct3b']), ('2026-11-13', '0', '0'))
        self.assertEqual([s[0] for s in m.CASES[INCREASE]['expected']['subitems']], ['1003'])
        self.assertEqual([s[0] for s in m.CASES[BDS]['expected']['subitems']], ['1701', '1014'])
        self.assertEqual(m.CASES[LAN2]['prior'], m.CASES[INCREASE]['web'])
        self.assertEqual(len({m.CASES[c]['original'] for c in CASES if c != BDS}), 1)
        self.assertEqual([m.tax_leaf_count(c) for c in CASES], [224, 224, 198, 242])

    def test_registered_as_observation_cases_with_summary(self):
        for case_id in CASES:
            row = registry.CASES[case_id]
            self.assertIs(row['releaseGate'], False)
            self.assertEqual(registry.htkk_version(case_id), '5.8.2')
            self.assertEqual(registry.driver(case_id), 'declaration-amendment-khbs-inspect')
            self.assertEqual(row['format'], m.manifest_fields(case_id)['format'])
            self.assertEqual(row['unit']['amendmentOrder'], m.CASES[case_id]['soLan'])
            period = ('month', '10/2026') if case_id == BDS else ('quarter', '4/2026')
            self.assertEqual((row['unit']['menuId'], row['unit']['adapterVersion'], row['unit']['periodType'], row['unit']['periodValue']), ('Y7', '3.1.0') + period)
            self.assertEqual(row['unit']['annexes'], ['01-2'] if case_id == BDS else ['01-1'])
        self.assertTrue(set(CASES) <= set(registry.NTNN_KHBS_CASES))
        self.assertFalse(set(CASES) & set(registry.NTNN_KHBS_NO_SUMMARY_CASES))
        self.assertFalse(set(CASES) & set(registry.NTNN_KHBS_TICK_CASES))

    def test_pinned_synthetic_files_validate_and_the_annex_order_is_enforced(self):
        for case_id in CASES:
            files = support.files(sm, case_id)
            self.assertEqual(sm.validate_files(files, manifest(case_id, sm))['amendmentLeafTarget'], sm.CASES[case_id]['leafTarget'])
        body = support.files(sm, INCREASE)[sm.WEB_NAME].decode('utf-8')
        annex = re.search('<%s>.*?</%s>' % (HTKD, HTKD), body).group(0)
        for changed in (body.replace(annex, ''), body.replace(annex, '').replace('</PLuc>', annex + '</PLuc>'), body.replace(HTKD, BDS_ANNEX)):
            raw = changed.encode('utf-8')
            saved = sm.CASES[INCREASE]['web']
            try:
                sm.CASES[INCREASE]['web'] = (len(raw), hashlib.sha256(raw).hexdigest())
                with self.assertRaises(sm.NtnnKhbsWebCaseError) as error:
                    sm.validate_xml(raw, INCREASE, 'web')
                self.assertEqual(error.exception.code, 'AMENDMENT')
            finally:
                sm.CASES[INCREASE]['web'] = saved
        with self.assertRaises(m.NtnnKhbsWebCaseError):
            m.validate_xml(support.files(sm, INCREASE)[m.WEB_NAME], INCREASE, 'web')

    def test_ngay_ky_is_compared_as_an_export_date(self):
        web = support.files(sm, INCREASE)[sm.WEB_NAME]
        same = sm.compare_tree(web, web, INCREASE)
        self.assertTrue(same['allTaxValuesMatched'])
        # A native export of another day writes that day into ngayLapTKhai and ngayKy alike.
        other = web.replace(b'<ngayLapTKhai>2026-11-13</ngayLapTKhai>', b'<ngayLapTKhai>2026-11-20</ngayLapTKhai>').replace(b'<ngayKy>2026-11-13</ngayKy>', b'<ngayKy>2026-11-20</ngayKy>')
        self.assertTrue(sm.compare_tree(web, other, INCREASE)['allTaxValuesMatched'])
        # ngayKy that is not the export day still differs.
        stale = web.replace(b'<ngayLapTKhai>2026-11-13</ngayLapTKhai>', b'<ngayLapTKhai>2026-11-20</ngayLapTKhai>')
        self.assertFalse(sm.compare_tree(web, stale, INCREASE)['allTaxValuesMatched'])


class Tckt01KhbsNativeRetention(unittest.TestCase):
    def test_catalogue_texts_of_y7_from_the_start(self):
        extra = m.catalogue_texts(INCREASE, [], frozenset())
        self.assertEqual(extra, tckt01.CATALOGUE_TEXTS)
        for text in ('Tờ khai', '01/TCKT', '01/BK-KTHTKD', '02/BK-KTBĐS', '0252', '025201', '[07]', '[13]',
                     '[07] - Tổng doanh thu phát sinh trong kỳ', 'Tổng doanh thu phát sinh trong kỳ', 'Doanh thu trả trong kỳ',
                     'Thuế thu nhập từ hoạt động sản xuất, kinh doanh của cá nhân', 'Thuế thu nhập từ hoạt động cho thuê tài sản'):
            self.assertIn(text, extra)
        self.assertNotIn('01/TCKT', m.catalogue_texts('05KK-khbs-increase-Q3-2026', [], frozenset()))


class Tckt01KhbsDriverWiring(unittest.TestCase):
    def test_case_plans_use_the_310_plans_with_the_khbs_schema_and_web_leaf_counts(self):
        plans = (ROOT / 'HtkkDeclarationCasePlans.cs').read_text(encoding='utf-8')
        ids = set(re.findall('"([^"]+)"', re.search(r'KhbsCaseIds=new string\[\]\{(.*?)\};', plans, re.S).group(1)))
        self.assertTrue(set(CASES) <= ids)
        self.assertRegex(plans, r'KhbsSoLan\(string caseId\)\{return [^;]*caseId=="01TCKT-310-khbs-lan2-hop-tac-kd-Q4-2026"[^;]*\?2:')
        self.assertIn('if(caseId.StartsWith("01TCKT-310-khbs-",StringComparison.Ordinal))return Tckt01KhbsPlan(caseId);', plans)
        body = plans[plans.index('private static HtkkDeclarationCasePlan Tckt01KhbsPlan('):]
        body = body[:body.index('\n }\n')]
        self.assertIn('"Validate/KHBS_01_TCKT_TT89_310.xsd","4631d4c3d8b1a042158b53c36516a78be9f87db2c4e2f65c7a385675e5ef5020"', body)
        self.assertIn('int leaves=bds?%d:caseId=="%s"?%d:%d;' % (m.tax_leaf_count(BDS) + 4, DECREASE, m.tax_leaf_count(DECREASE) + 4, m.tax_leaf_count(INCREASE) + 4), body)
        self.assertEqual(m.tax_leaf_count(INCREASE), m.tax_leaf_count(LAN2))
        self.assertIn('new HtkkDeclarationCasePlan(caseId,"Y7","3.1.0","2007","Tckt01TT89Nckt310",new string[]{"101","101_37","Y7"},bds?"month":"quarter","21","2026",bds?"10":"4","01/10/2026",bds?"31/10/2026":"31/12/2026",false,', body)
        for name in ('01TCKT-310-hop-tac-kd-two-individuals-Q4-2026', '01TCKT-310-bds-three-lessors-M10-2026'):
            first = plans[plans.index('case "%s":' % name):]
            first = first[:first.index(';\n')]
            for pin in ('"InterfaceTemplates/excel/01_TCKT_TT89_310.xls","95ecbc2cd702100d49d946fd526ae71916a53229f25b335b358c4e35c3c48cd7"', '"InterfaceTemplates/xml/01_TCKT_TT89_310.xml","2e99cdd5c7afc75ee539272ab2a8003ac0fb5d80387073d177a69f6723fdd69e"'):
                self.assertIn(pin, first)
                self.assertIn(pin, body)
        self.assertIn('new string[]{"01|Tờ khai","01-1|01/BK-KTHTKD"}', body)
        self.assertIn('new string[]{"01|Tờ khai","01-2|02/BK-KTBĐS"}', body)
        for case_id in CASES:
            self.assertIn('case "%s":' % case_id, plans)
        # Y7 plans write the export day into ngayKy and accept the 0699 notice of the period dialog.
        self.assertIn('plan.MenuId=="Y7"', plans[plans.index('internal static string[] ExportDatePaths('):])
        self.assertIn('plan.MenuId=="Y7"&&messageId==699', plans)

    def test_probe_lists(self):
        formats = (ROOT / 'HtkkNativeCaseFormats.ps1').read_text(encoding='utf-8')
        listed = re.search(r"\$HtkkNtnnKhbsCases=@\((.*?)\)\n", formats).group(1)
        self.assertTrue(set(CASES) <= set(re.findall("'([^']+)'", listed)))
        self.assertIn("'%s'" % LAN2, re.search(r"\$HtkkNtnnKhbsLan2Cases=@\((.*?)\)\n", formats).group(1))
        registry_text = (ROOT / 'htkk-native-automation-registry.json').read_text(encoding='utf-8')
        reader = (ROOT / 'Get-HtkkSafeGuiReferenceResult.ps1').read_text(encoding='utf-8')
        for case_id in CASES:
            self.assertIn('"%s"' % case_id, registry_text)
            self.assertIn("'%s'" % case_id, reader)


if __name__ == '__main__':
    unittest.main()
