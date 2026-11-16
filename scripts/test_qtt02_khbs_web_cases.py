"""Input contract of the 02/QTT-TNCN kê khai bổ sung cases (htkk_qtt02_khbs_web_cases.py, merged into htkk_ntnn_khbs_web_cases.py).
B8 has KieuKHBS 3 in HTKK 5.8.2: its B files carry the 02-1/BK-QTT-TNCN annex, then PL01_KHBS / PL01_1_KHBS, and its rounds run
"Tổng hợp KHBS". Synthetic checks only; the reviewed producer files stay private (only their sizes and SHA-256 are pinned).
Byte-level checks run on a second module instance pinned to synthetic in-memory files (ntnn_khbs_test_support.py)."""
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


m = load('htkk_ntnn_khbs_web_cases_qtt02', 'htkk_ntnn_khbs_web_cases.py')
qtt02 = load('htkk_qtt02_khbs_web_cases_test', 'htkk_qtt02_khbs_web_cases.py')
support = load('ntnn_khbs_test_support_qtt02', 'ntnn_khbs_test_support.py')
sm = support.pin(load('htkk_ntnn_khbs_web_cases_qtt02_pinned', 'htkk_ntnn_khbs_web_cases.py'))
registry = load('htkk_native_cases_qtt02', 'htkk_native_cases.py')
CASES = ('02QTT-khbs-increase-Y2025', '02QTT-khbs-lan2-Y2025', '02QTT-khbs-decrease-Y2025', '02QTT-khbs-refund-Y2025')
LAN2, DECREASE, REFUND = '02QTT-khbs-lan2-Y2025', '02QTT-khbs-decrease-Y2025', '02QTT-khbs-refund-Y2025'
ANNEX = 'PLuc_02_1_BK_QTT_TNCN'


def manifest(case_id, module):
    c = module.CASES[case_id]
    value = dict(module.manifest_fields(case_id), sourceCommit='0' * 40, producerSha256='1' * 64, bytes=c['web'][0], xmlSha256=c['web'][1],
                 originalBytes=c['original'][0], originalXmlSha256=c['original'][1])
    if c['prior']:
        value.update(priorBytes=c['prior'][0], priorXmlSha256=c['prior'][1])
    return value


class Qtt02KhbsWebCases(unittest.TestCase):
    def test_four_cases_merged_with_their_own_producer_menu_and_period(self):
        self.assertEqual(m.QTT02_CASES, CASES)
        self.assertEqual(set(qtt02.CASES), set(CASES))
        self.assertFalse((set(m.NTNN_CASES) | set(m.KK05_CASES) | set(m.CNKD_CASES)) & set(CASES))
        self.assertEqual(m.MENUS['B8'], ('952', '2.7.3'))
        self.assertEqual(m.PERIODS['B8'], ('Y', '2025', '', ''))
        for case_id in CASES:
            c = m.CASES[case_id]
            self.assertEqual(m.producer(case_id), 'scripts/generate-htkk-web-qtt02-khbs-reference.mjs')
            self.assertEqual(m.manifest_fields(case_id)['exporter'], 'lib/htkk-qtt02-khbs.ts')
            self.assertEqual(m.names(case_id), (m.ORIGINAL_NAME,) + ((m.PRIOR_NAME,) if case_id == LAN2 else ()) + (m.WEB_NAME, m.MANIFEST_NAME))
            self.assertEqual(m.input_mode(case_id), 'khbs-web-xml-import-reexport')
            self.assertEqual(c['annexParts'], (ANNEX,))
            # KieuKHBS 3: both KHBS fragments and the summary step.
            self.assertEqual(c['khbsParts'], ('PL01_KHBS', 'PL01_1_KHBS'))
            self.assertTrue(m.khbs_summary(case_id))
            self.assertEqual(m.validate_manifest(manifest(case_id, m))['caseId'], case_id)
            self.assertEqual(set(c['expected']), {'rows', 'subitems', 'refund', 'ct10', 'ct13', 'ct3a_1', 'ct3a_2', 'ct3b'})
            # Năm 2025 is due 31/03/2026 (GetHanNopToKhai KieuKy Y): 227 days to ngày lập 13/11/2026.
            self.assertEqual((c['expected']['ct3a_1'], c['expected']['ct3a_2']), ('2026-11-13', '227'))
        # Lần 2 starts from the lần-1 file of the increase case; the payable cases share one lần đầu, the refund case has its own.
        self.assertEqual(m.CASES[LAN2]['prior'], m.CASES['02QTT-khbs-increase-Y2025']['web'])
        self.assertEqual(len({m.CASES[c]['original'] for c in CASES if c != REFUND}), 1)
        self.assertNotEqual(m.CASES[REFUND]['original'], m.CASES[DECREASE]['original'])
        self.assertEqual(m.CASES[REFUND]['expected']['refund'], [['1001', '2000000']])
        self.assertEqual(m.tax_leaf_count(DECREASE), 246)
        self.assertEqual({m.tax_leaf_count(c) for c in CASES if c != DECREASE}, {272})

    def test_registered_as_observation_cases_with_summary(self):
        for case_id in CASES:
            row = registry.CASES[case_id]
            self.assertIs(row['releaseGate'], False)
            self.assertEqual(registry.htkk_version(case_id), '5.8.2')
            self.assertEqual(registry.driver(case_id), 'declaration-amendment-khbs-inspect')
            self.assertEqual(row['format'], m.manifest_fields(case_id)['format'])
            self.assertEqual(row['unit']['amendmentOrder'], m.CASES[case_id]['soLan'])
            self.assertEqual((row['unit']['menuId'], row['unit']['adapterVersion'], row['unit']['periodType'], row['unit']['periodValue']), ('B8', '2.7.3', 'year', '2025'))
            self.assertEqual(row['unit']['annexes'], ['02-1'])
            self.assertNotIn('notBefore', row)
        self.assertTrue(set(CASES) <= set(registry.NTNN_KHBS_CASES))
        self.assertFalse(set(CASES) & set(registry.NTNN_KHBS_NO_SUMMARY_CASES))
        self.assertFalse(set(CASES) & set(registry.NTNN_KHBS_TICK_CASES))

    def test_pinned_synthetic_files_validate_and_the_annex_order_is_enforced(self):
        for case_id in CASES:
            files = support.files(sm, case_id)
            self.assertEqual(sm.validate_files(files, manifest(case_id, sm))['amendmentLeafTarget'], sm.CASES[case_id]['leafTarget'])
            self.assertIn(b'<' + ANNEX.encode() + b'>', files[sm.ORIGINAL_NAME])
        # A B file without its 02-1 annex, or with the annex after the KHBS fragments, is refused (pins switched off for the check).
        body = support.files(sm, REFUND)[sm.WEB_NAME].decode('utf-8')
        annex = re.search('<%s>.*?</%s>' % (ANNEX, ANNEX), body).group(0)
        for changed in (body.replace(annex, ''), body.replace(annex, '').replace('</PLuc>', annex + '</PLuc>')):
            raw = changed.encode('utf-8')
            saved = sm.CASES[REFUND]['web']
            try:
                sm.CASES[REFUND]['web'] = (len(raw), hashlib.sha256(raw).hexdigest())
                with self.assertRaises(sm.NtnnKhbsWebCaseError) as error:
                    sm.validate_xml(raw, REFUND, 'web')
                self.assertEqual(error.exception.code, 'AMENDMENT')
            finally:
                sm.CASES[REFUND]['web'] = saved
        # The real pins refuse every synthetic file.
        with self.assertRaises(m.NtnnKhbsWebCaseError):
            m.validate_xml(support.files(sm, REFUND)[m.WEB_NAME], REFUND, 'web')


class Qtt02KhbsNativeRetention(unittest.TestCase):
    def test_catalogue_texts_and_row_keys_only_for_the_b8_cases(self):
        key = 'HSoThueDTu/HSoKhaiThue/PLuc/' + m.KEY_PATH_SUFFIX
        allowed = frozenset(('NGUOI PHU THUOC A', '001215000001'))
        items = [(key, 'NGUOI PHU THUOC A -  - 001215000001'), (key, 'NGUOI PHU THUOC A - 2015-02-01'), (key, 'NGUOI KHAC - 001215000001'),
                 ('HSoThueDTu/HSoKhaiThue/PLuc/PL01_1_KHBS/Muc_A/DSachHSo/BKeHSo/ten_HSo', 'NGUOI PHU THUOC A - 001215000001')]
        extra = m.catalogue_texts(REFUND, items, allowed)
        self.assertEqual(extra - qtt02.CATALOGUE_TEXTS, {'NGUOI PHU THUOC A -  - 001215000001', 'NGUOI PHU THUOC A - 2015-02-01'})
        for text in ('02-1/BK-QTT-TNCN', 'Tờ khai', 'Ngày sinh', '[15] - Quan hệ với NNT', 'Thời gian được tính giảm trừ trong năm\\ Đến tháng'):
            self.assertIn(text, extra)
        # Every other KHBS case keeps the exact input-text rule.
        for case_id in m.NTNN_CASES + m.KK05_CASES + m.CNKD_CASES:
            self.assertEqual(m.catalogue_texts(case_id, items, allowed), frozenset())
        source = (ROOT / 'htkk_ntnn_khbs_web_cases.py').read_text(encoding='utf-8')
        self.assertIn('d._texts(items, allowed | catalogue_texts(case_id, items, allowed))', source)


class Qtt02KhbsDriverWiring(unittest.TestCase):
    def test_case_plans_use_the_b8_plan_with_the_khbs_schema_and_web_leaf_counts(self):
        plans = (ROOT / 'HtkkDeclarationCasePlans.cs').read_text(encoding='utf-8')
        ids = set(re.findall('"([^"]+)"', re.search(r'KhbsCaseIds=new string\[\]\{(.*?)\};', plans, re.S).group(1)))
        self.assertTrue(set(CASES) <= ids)
        self.assertRegex(plans, r'KhbsSoLan\(string caseId\)\{return [^;]*caseId=="02QTT-khbs-lan2-Y2025"[^;]*\?2:')
        self.assertIn('if(caseId.StartsWith("02QTT-",StringComparison.Ordinal))return Qtt02KhbsPlan(caseId);', plans)
        body = plans[plans.index('private static HtkkDeclarationCasePlan Qtt02KhbsPlan('):]
        body = body[:body.index('\n }\n')]
        self.assertIn('"Validate/KHBS_02_QTT_TNCN_TT80_273.xsd","b534fbed4424b694cb45dc9a37a65b8cfd9084daadeb810e7946c184303e7529"', body)
        self.assertIn('WorkbookService,caseId=="02QTT-khbs-decrease-Y2025"?%d:%d,new string[0],new string[0]' % (m.tax_leaf_count(DECREASE) + 4, m.tax_leaf_count(CASES[0]) + 4), body)
        # The lần đầu B8 plan (02QTT-dependants-Y2025): year 2025, KieuKy 12, annex 02-1, the same workbook and layout pins.
        self.assertIn('new HtkkDeclarationCasePlan(caseId,"B8","2.7.3","952","TncnQtt02TT80Nckt273",new string[]{"101","101_11","B8"},"year","12","2025","","01/2025","12/2025",false,', body)
        self.assertIn('new string[]{"02-1/BK-QTT-TNCN"},new string[]{"02|Tờ khai","02-1|02-1/BK-QTT-TNCN"},', body)
        first = plans[plans.index('case "02QTT-dependants-Y2025":'):]
        first = first[:first.index(';\n')]
        for pin in ('"InterfaceTemplates/excel/02_QTT_TNCN_TT80_273.xls","e1eb77e740803215372e64e58d6c57bd71fc71ba64916ba1a8b4fddabbc95a26"', '"InterfaceTemplates/xml/02_QTT_TNCN_TT80_273.xml","6b2a2c1d27c9298e1fe73b12138ab98e4f722f785e9c253ed91bde3570611f12"'):
            self.assertIn(pin, first)
            self.assertIn(pin, body)
        self.assertNotIn('02QTT-', plans[plans.index('internal static HtkkDeclarationTickPlan KhbsImportTick('):].split('\n')[0])
        for case_id in CASES:
            self.assertIn('case "%s":' % case_id, plans)

    def test_probe_lists(self):
        formats = (ROOT / 'HtkkNativeCaseFormats.ps1').read_text(encoding='utf-8')
        listed = re.search(r"\$HtkkNtnnKhbsCases=@\((.*?)\)\n", formats).group(1)
        self.assertTrue(set(CASES) <= set(re.findall("'([^']+)'", listed)))
        self.assertIn("'02QTT-khbs-lan2-Y2025'", re.search(r"\$HtkkNtnnKhbsLan2Cases=@\((.*?)\)\n", formats).group(1))
        registry_text = (ROOT / 'htkk-native-automation-registry.json').read_text(encoding='utf-8')
        reader = (ROOT / 'Get-HtkkSafeGuiReferenceResult.ps1').read_text(encoding='utf-8')
        for case_id in CASES:
            self.assertIn('"%s"' % case_id, registry_text)
            self.assertIn("'%s'" % case_id, reader)


if __name__ == '__main__':
    unittest.main()
