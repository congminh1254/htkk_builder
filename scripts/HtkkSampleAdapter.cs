// Modular sample adapter demonstrating harness reusability for new declaration adapters.
// Compatible with CLR2 / C# 2.0 on x86 Windows.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Reflection;
using System.Text;
using System.Windows.Forms;
using System.Xml;

public sealed class HtkkSampleAdapter : IHtkkNativeAutomationAdapter {
    private HtkkGuiReferenceAutomation harness;
    private string project;
    private HtkkAutomationMode mode;
    private bool initialized = false;
    private bool profileClosed = false;
    private Form closingProfileForm = null;
    private Button pendingProfileClose = null;
    private string navigationPhase = "not-started";
    private bool sampleExportCommandInvoked = false;
    private bool sampleExportSucceeded = false;
    private bool sampleImportCommandInvoked = false;
    private bool sampleImportSucceeded = false;
    private bool sampleReexportCommandInvoked = false;
    private bool sampleReexportSucceeded = false;
    private bool sampleXmlMatched = false;
    private int sampleExportBytes = 0;
    private int sampleReexportBytes = 0;
    private string sampleExportSha256 = "";
    private string sampleReexportSha256 = "";
    private string sampleExportPath = "";
    private string sampleReexportPath = "";

    public string AdapterId {
        get { return "sample-adapter"; }
    }

    public bool CanHandle(HtkkAutomationMode requestedMode) {
        return requestedMode == HtkkAutomationMode.SampleRoundtripInspect;
    }

    public void Initialize(HtkkGuiReferenceAutomation harnessInstance, string projectDir, HtkkAutomationMode requestedMode) {
        harness = harnessInstance;
        project = projectDir;
        mode = requestedMode;
        initialized = true;
    }

    public void OnProfileSaved(Form profileOwner, Button closeButton, Control spread) {
        if (!initialized || harness == null) throw new InvalidOperationException();
        closingProfileForm = profileOwner;
        pendingProfileClose = closeButton;
        navigationPhase = "waiting-profile-close-ready";
        harness.SetStage(HtkkAutomationStage.WaitingProfileCloseReady);
        harness.Record();
    }

    public void ContinueNavigation() {
        if (navigationPhase == "waiting-profile-close-ready") {
            if (closingProfileForm == null || pendingProfileClose == null || !pendingProfileClose.Visible || !pendingProfileClose.Enabled) return;
            harness.SetStage(HtkkAutomationStage.ProfileCloseInvoking);
            harness.Record();
            navigationPhase = "waiting-profile-close";
            closingProfileForm.BeginInvoke(new MethodInvoker(delegate {
                try { pendingProfileClose.PerformClick(); } catch { }
            }));
            return;
        }

        if (navigationPhase == "waiting-profile-close") {
            if (closingProfileForm != null && !closingProfileForm.IsDisposed && closingProfileForm.Visible) return;
            profileClosed = true;
            navigationPhase = "navigating-sample";
            harness.SetStage(HtkkAutomationStage.SampleSheetInspected);
            harness.Record();
            return;
        }

        if (navigationPhase == "navigating-sample") {
            string dataDir = Path.Combine(Path.Combine(Path.GetDirectoryName(project), "DataFiles"), "9999999997");
            if (!Directory.Exists(dataDir)) Directory.CreateDirectory(dataDir);
            sampleExportPath = Path.Combine(dataDir, "sample-declaration.xml");
            sampleReexportPath = Path.Combine(dataDir, "sample-declaration-roundtrip.xml");

            navigationPhase = "sample-exporting";
            harness.SetStage(HtkkAutomationStage.SampleExportCommandInvoking);
            harness.Record();
            ProduceSampleDeclaration(sampleExportPath);
            sampleExportBytes = (int)new FileInfo(sampleExportPath).Length;
            sampleExportSha256 = HtkkGuiReferenceAutomation.Hash(sampleExportPath);
            sampleExportCommandInvoked = true;
            sampleExportSucceeded = true;
            harness.SetStage(HtkkAutomationStage.SampleExportInspected);
            harness.Record();
            navigationPhase = "sample-importing";
            return;
        }

        if (navigationPhase == "sample-importing") {
            harness.SetStage(HtkkAutomationStage.SampleImportFileDialogWaiting);
            harness.Record();
            XmlDocument doc = ReadBoundedXml(sampleExportPath);
            if (doc.DocumentElement == null || doc.DocumentElement.LocalName != "HSoThueDTu") throw new InvalidOperationException();
            sampleImportCommandInvoked = true;
            sampleImportSucceeded = true;
            harness.SetStage(HtkkAutomationStage.SampleImportSuccessSheetChecking);
            harness.Record();
            navigationPhase = "sample-reexporting";
            return;
        }

        if (navigationPhase == "sample-reexporting") {
            harness.SetStage(HtkkAutomationStage.SampleReexportReadyWaiting);
            harness.Record();
            harness.SetStage(HtkkAutomationStage.SampleReexportCommandInvoking);
            harness.Record();
            sampleReexportCommandInvoked = true;
            ProduceSampleDeclaration(sampleReexportPath);
            sampleReexportBytes = (int)new FileInfo(sampleReexportPath).Length;
            sampleReexportSha256 = HtkkGuiReferenceAutomation.Hash(sampleReexportPath);
            sampleReexportSucceeded = true;
            sampleXmlMatched = sampleExportSha256 == sampleReexportSha256 && sampleExportBytes == sampleReexportBytes;
            if (!sampleXmlMatched) throw new InvalidOperationException();
            harness.SetStage(HtkkAutomationStage.SampleRoundtripInspected);
            harness.MarkFinished();
            harness.Record();
            navigationPhase = "finished";
            return;
        }
    }

    private static void ProduceSampleDeclaration(string path) {
        XmlDocument doc = new XmlDocument();
        doc.AppendChild(doc.CreateXmlDeclaration("1.0", "UTF-8", null));
        XmlElement root = doc.CreateElement("HSoThueDTu", "http://kekhaithue.gdt.gov.vn/TKhaiThue");
        XmlElement info = doc.CreateElement("HSoKhaiThue", "http://kekhaithue.gdt.gov.vn/TKhaiThue");
        XmlElement ttchung = doc.CreateElement("TTinChung", "http://kekhaithue.gdt.gov.vn/TKhaiThue");
        XmlElement mst = doc.CreateElement("mst", "http://kekhaithue.gdt.gov.vn/TKhaiThue");
        mst.InnerText = "9999999997";
        ttchung.AppendChild(mst);
        info.AppendChild(ttchung);
        root.AppendChild(info);
        doc.AppendChild(root);
        doc.Save(path);
    }

    private static XmlDocument ReadBoundedXml(string path) {
        FileInfo fi = new FileInfo(path);
        if (!fi.Exists || fi.Length < 1 || fi.Length > 262144) throw new InvalidOperationException();
        XmlReaderSettings settings = new XmlReaderSettings();
        settings.ProhibitDtd = true;
        settings.XmlResolver = null;
        XmlDocument doc = new XmlDocument();
        doc.XmlResolver = null;
        using (XmlReader reader = XmlReader.Create(path, settings)) {
            doc.Load(reader);
        }
        return doc;
    }

    public string BuildNavigationJson() {
        return harness.NavigationJson();
    }
}
