"""Modular sample adapter contract tests.

Verifies that HtkkSampleAdapter implements IHtkkNativeAutomationAdapter,
handles sample-roundtrip-inspect, isolates context and private artifact policy,
and preserves the privacy boundary (rejection of real taxpayer data).
"""
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent
REGISTRY_PATH = ROOT / "htkk-native-automation-registry.json"


class SampleAdapterContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            cls.registry = json.load(f)
        cls.modes = cls.registry["modes"]

    def test_sample_adapter_source_implements_interface(self):
        source = (ROOT / "HtkkSampleAdapter.cs").read_text(encoding="utf-8")
        self.assertIn("public sealed class HtkkSampleAdapter : IHtkkNativeAutomationAdapter", source)
        self.assertIn('public string AdapterId', source)
        self.assertIn('"sample-adapter"', source)
        self.assertIn('CanHandle(HtkkAutomationMode requestedMode)', source)
        self.assertIn('SampleRoundtripInspect', source)
        self.assertIn('OnProfileSaved', source)
        self.assertIn('ContinueNavigation', source)
        self.assertIn('BuildNavigationJson', source)

    def test_sample_adapter_does_not_modify_binaries_or_config(self):
        source = (ROOT / "HtkkSampleAdapter.cs").read_text(encoding="utf-8")
        for forbidden in ("SetValue", "SetPublic", "TAX.HTKK.Business", "HTKK.exe.config"):
            self.assertNotIn(forbidden, source)

    def test_sample_mode_metadata_isolated_in_registry(self):
        self.assertIn("sample-roundtrip-inspect", self.modes)
        meta = self.modes["sample-roundtrip-inspect"]
        self.assertEqual(meta["adapterId"], "sample-adapter")
        self.assertEqual(meta["runtime"], "clr2-x86-custom-reference")
        self.assertTrue(meta["login"])
        self.assertEqual(meta["permit"], "profile-save")
        self.assertEqual(meta["terminalStage"], "sample-roundtrip-inspected")
        self.assertEqual(meta["contextPolicy"], "htkk-native/sample")
        self.assertEqual(meta["privateArtifactPolicy"], "raw-sample-reexport")

    def test_sample_adapter_compilation_wiring_in_host(self):
        host = (ROOT / "New-HtkkX86ReferenceHost.ps1").read_text(encoding="utf-8")
        self.assertIn("$enumsSource=Join-Path $directory 'HtkkNativeAutomationEnums.cs'", host)
        self.assertIn("$sampleSource=Join-Path $directory 'HtkkSampleAdapter.cs'", host)
        self.assertIn("$source,$enumsSource,$sampleSource,$automationSource", host)

    def test_sample_roundtrip_evidence_publication_contract(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("pub_sample", ROOT / "publish-sample-roundtrip-evidence.py")
        pub = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pub)
        self.assertEqual(pub.BRANCH, "sample-roundtrip-reference-evidence")
        self.assertEqual(pub.NAMES, ("sample-declaration-roundtrip.xml", "provenance.json"))
        sample_xml = b'<?xml version="1.0" encoding="UTF-8"?><HSoThueDTu xmlns="http://kekhaithue.gdt.gov.vn/TKhaiThue"><HSoKhaiThue><TTinChung><mst>9999999997</mst></TTinChung></HSoKhaiThue></HSoThueDTu>'
        self.assertTrue(pub.validate_sample_xml(sample_xml))
        # Rejection of non-synthetic or malformed
        with self.assertRaises(ValueError):
            pub.validate_sample_xml(b'<invalid>')
        with self.assertRaises(ValueError):
            pub.validate_sample_xml(b'<?xml version="1.0"?><HSoThueDTu xmlns="http://kekhaithue.gdt.gov.vn/TKhaiThue"><mst>0100109106</mst></HSoThueDTu>')
        provenance = pub.create_provenance("a" * 40, "12345", sample_xml)
        self.assertEqual(provenance["format"], "htkk-sample-roundtrip-reference-evidence-v1")
        self.assertEqual(provenance["sourceVersion"], "5.8.1")
        self.assertTrue(provenance["fullRoundTrip"])



if __name__ == "__main__":
    unittest.main()
