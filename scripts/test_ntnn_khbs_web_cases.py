"""Input contract of the 01/NTNN, 01/NTNN-NCCNN kê khai bổ sung cases (htkk_ntnn_khbs_web_cases.py). Synthetic checks only;
the reviewed producer files themselves stay private (the contract pins their sizes and SHA-256)."""
import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).parent
spec = importlib.util.spec_from_file_location('htkk_ntnn_khbs_web_cases', ROOT / 'htkk_ntnn_khbs_web_cases.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def manifest(case_id):
    c = m.CASES[case_id]
    value = dict(m.manifest_fields(case_id), sourceCommit='0' * 40, producerSha256='1' * 64, bytes=c['web'][0], xmlSha256=c['web'][1],
                 originalBytes=c['original'][0], originalXmlSha256=c['original'][1])
    if c['prior']:
        value.update(priorBytes=c['prior'][0], priorXmlSha256=c['prior'][1])
    return value


class NtnnKhbsWebCases(unittest.TestCase):
    def test_five_cases_with_exact_staged_names(self):
        self.assertEqual(sorted(m.CASES), sorted(['01NTNN-khbs-grossup-lan1-M09-2026', '01NTNN-khbs-lan2-M09-2026', '01NTNN-khbs-decrease-M09-2026',
                                                  '01NTNN-NCCNN-khbs-part1-M10-2026', '01NTNN-NCCNN-khbs-part2-M10-2026']))
        for case_id, c in m.CASES.items():
            self.assertEqual(m.names(case_id)[-2:], (m.WEB_NAME, m.MANIFEST_NAME))
            self.assertEqual(m.names(case_id)[0], m.ORIGINAL_NAME)
            self.assertEqual(m.PRIOR_NAME in m.names(case_id), c['soLan'] == 2)
            self.assertEqual(bool(c['prior']), c['soLan'] == 2)
            self.assertIn(c['menuId'], m.MENUS)
            self.assertTrue(0 < c['leafTarget'] <= 4096)
            for role in ('web', 'original') + (('prior',) if c['prior'] else ()):
                size, digest = c[role]
                self.assertTrue(0 < size <= m.MAX_XML)
                self.assertRegex(digest, '^[0-9a-f]{64}$')
            self.assertRegex(m.manifest_fields(case_id)['format'], '^htkk-web-[a-z0-9-]+-input-v1$')
        # The lần-2 previous version is the lần-1 case's own file, and every I9 case starts from the same lần đầu.
        lan1, lan2 = m.CASES['01NTNN-khbs-grossup-lan1-M09-2026'], m.CASES['01NTNN-khbs-lan2-M09-2026']
        self.assertEqual(lan2['prior'], lan1['web'])
        self.assertEqual(len({c['original'] for c in m.CASES.values() if c['menuId'] == 'I9'}), 1)

    def test_not_registered_until_the_driver_exists(self):
        registry = json.loads((ROOT / 'htkk-native-cases.json').read_text(encoding='utf-8'))
        self.assertFalse(set(m.CASES) & {c['caseId'] for c in registry['cases']})

    def test_manifest_is_exact(self):
        for case_id in m.CASES:
            self.assertIs(m.validate_manifest(manifest(case_id))['caseId'], case_id)
            for change in ({'extra': 1}, {'soLan': 9}, {'xmlSha256': '2' * 64}, {'htkkVersion': '5.8.1'}, {'sourceCommit': 'x'}):
                with self.assertRaises(m.NtnnKhbsWebCaseError):
                    m.validate_manifest(dict(manifest(case_id), **change))
        with self.assertRaises(m.NtnnKhbsWebCaseError) as error:
            m.validate_manifest(dict(manifest('01NTNN-khbs-lan2-M09-2026'), caseId='01NTNN-other'))
        self.assertEqual(error.exception.code, 'CASE')

    def test_files_are_the_pinned_bytes_only(self):
        case_id = '01NTNN-khbs-decrease-M09-2026'
        size = m.CASES[case_id]['web'][0]
        fake = (m.PREAMBLE + 'xmlns="%s"/>' % m.NS).encode('utf-8')
        for body, code in ((b'', 'SIZE'), (fake, 'SIZE'), (fake.ljust(size, b' '), 'HASH')):
            with self.assertRaises(m.NtnnKhbsWebCaseError) as error:
                m.validate_xml(body, case_id, 'web')
            self.assertEqual(error.exception.code, code)
        with self.assertRaises(m.NtnnKhbsWebCaseError) as error:
            m.validate_xml(fake, case_id, 'prior')
        self.assertEqual(error.exception.code, 'NAMES')
        with self.assertRaises(m.NtnnKhbsWebCaseError) as error:
            m.validate_files({m.WEB_NAME: fake}, manifest(case_id))
        self.assertEqual(error.exception.code, 'NAMES')

    def test_bounded_codes(self):
        with self.assertRaises(ValueError):
            m.NtnnKhbsWebCaseError('free text')


if __name__ == '__main__':
    unittest.main()
