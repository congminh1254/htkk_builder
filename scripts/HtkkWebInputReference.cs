// Own private staged WEB XML input. Verification only: never creates or edits XML.
using System;
using System.IO;
using System.Reflection;
using System.Text;
using System.Text.RegularExpressions;
using System.Xml;
public sealed partial class HtkkGuiReferenceAutomation {
 private string webCaseId="01GTGT-zero-M10-2026";private int webCaseEditCount=0;
 private bool webTaxValuesMatched=false,webCreationDateMatchedNativeBaseline=false,webServiceIdentityMatched=false;private int webTaxLeafCount=0;
 private bool webInputVerified=false;private string webInputPath="",webImportInputSha256="",webSourceSha="";
 private string SigningDateJson(){string q=((char)34).ToString();return ","+q+"webSigningDateEdited"+q+":"+Bool(webSigningDateEdited)+","+q+"webSigningDateReady"+q+":"+Bool(webSigningDateReady)+","+q+"webSigningDateLocked"+q+":"+Bool(webSigningDateLocked)+","+q+"webSigningDateCellKind"+q+":"+webSigningDateCellKind;}
 private string WebInputJson(){string q=((char)34).ToString();return ","+q+"webCaseId"+q+":"+q+webCaseId+q+","+q+"webCaseEditCount"+q+":"+webCaseEditCount+","+q+"webTaxValuesMatched"+q+":"+Bool(webTaxValuesMatched)+","+q+"webCreationDateMatchedNativeBaseline"+q+":"+Bool(webCreationDateMatchedNativeBaseline)+","+q+"webServiceIdentityMatched"+q+":"+Bool(webServiceIdentityMatched)+","+q+"webTaxLeafCount"+q+":"+webTaxLeafCount+","+q+"webInputVerified"+q+":"+Bool(webInputVerified)+","+q+"webImportInputSha256"+q+":"+q+webImportInputSha256+q+","+q+"webSourceSha"+q+":"+q+webSourceSha+q+SigningDateJson()+Annex10Json();}
 // Fixed 01-2/GTGT web cases. Their UI baseline is the proven 14-input zero
 // annex; only the original import control loads the case's web annex.
 private const string Annex12WebZeroCaseId="01GTGT-annex12-zero-two-locations-M10-2026";
 private const string Annex12WebTwoPlantsCaseId="01GTGT-annex12-two-plants-nonzero-M10-2026";
 private bool Annex12WebCaseId(){return webCaseId==Annex12WebZeroCaseId||webCaseId==Annex12WebTwoPlantsCaseId;}
 private bool Annex12WebCase(){return mode=="gtgt-web-import-inspect"&&webInputVerified&&Annex12WebCaseId();}
 private bool Annex12WebTwoPlantsCase(){return Annex12WebCase()&&webCaseId==Annex12WebTwoPlantsCaseId;}
 // Fixed 01-10/GTGT web case (PL_NQ142_GTGT, HTKK 5.8.2 oracle only). Its baseline is the proven zero main
 // declaration WITHOUT the annex: HTKK refuses to export an attached but empty 01-10 (Header B104/B105, 0016).
 // The original "Nhập từ XML" then loads the web file; the whole re-export is compared with it (88 tax leaves).
 private const string Annex10WebNq204CaseId="01GTGT-annex10-nq204-M10-2026";
 private bool Annex10WebCaseId(){return webCaseId==Annex10WebNq204CaseId;}
 private bool Annex10WebCase(){return mode=="gtgt-web-import-inspect"&&webInputVerified&&Annex10WebCaseId();}
 // Exact compared tax leaves: 70 main leaves, plus 38 (one plant, two rows) or
 // 89 (two plants, 2+3 rows) annex leaves; service identity leaves excluded.
 // 01-10: 74 main leaves of the no-annex declaration + 18 annex leaves, minus the 4 service leaves = 88.
 private int WebTaxLeafTarget(){return Annex10WebCaseId()?88:!Annex12WebCaseId()?70:webCaseId==Annex12WebTwoPlantsCaseId?159:108;}
 // The annex producers (01-2 and 01-10) pin both declaration dates to 2026-10-27.
 private DateTime WebFixedSigningDate(){return Annex12WebCaseId()||Annex10WebCaseId()?new DateTime(2026,10,27):new DateTime(2026,10,25);}
 private string RoundtripInputPath(){return KhbsMode()?KhbsImportPath():mode=="gtgt-web-import-inspect"||mode=="declaration-web-import-inspect"?webInputPath:firstExportPath;}
 private string RoundtripInputHash(){return KhbsMode()?KhbsImportHash():mode=="gtgt-web-import-inspect"||mode=="declaration-web-import-inspect"?webImportInputSha256:firstExportSha256;}
 private static string ReadOwnHexSidecar(string path,int count){
  FileInfo file=new FileInfo(path);if(!file.Exists||(file.Attributes&FileAttributes.ReparsePoint)!=0||file.Length!=count)throw new InvalidOperationException();byte[] bytes=File.ReadAllBytes(path);foreach(byte value in bytes)if(!((value>=48&&value<=57)||(value>=97&&value<=102)))throw new InvalidOperationException();return Encoding.ASCII.GetString(bytes);
 }
 private static string FixedWebLeaf(XmlDocument document,string suffix){
  string query="/*[local-name()='HSoThueDTu']/*[local-name()='HSoKhaiThue']";foreach(string name in suffix.Split('/'))query+="/*[local-name()='"+name+"']";
  XmlNodeList matches=document.SelectNodes(query);if(matches.Count!=1||matches[0].NamespaceURI!=document.DocumentElement.NamespaceURI||matches[0].ChildNodes.Count>1||matches[0].Attributes.Count!=0)throw new InvalidOperationException();
  foreach(XmlNode child in matches[0].ChildNodes)if(child.NodeType!=XmlNodeType.Text)throw new InvalidOperationException();return matches[0].InnerText;
 }
 private void VerifyOwnWebInput(){
  string host=Assembly.GetExecutingAssembly().Location;if(!String.Equals(Path.GetDirectoryName(host),project,StringComparison.OrdinalIgnoreCase))throw new InvalidOperationException();
  FileInfo caseFile=new FileInfo(host+".web-case.id");if(!caseFile.Exists||(caseFile.Attributes&FileAttributes.ReparsePoint)!=0||caseFile.Length<1||caseFile.Length>64)throw new InvalidOperationException();webCaseId=File.ReadAllText(caseFile.FullName,Encoding.ASCII);if(webCaseId!="01GTGT-zero-M10-2026"&&webCaseId!="01GTGT-sale10-M10-2026"&&webCaseId!="01GTGT-sale10-half-M10-2026"&&webCaseId!="01GTGT-sale10-manual-M10-2026"&&webCaseId!="01GTGT-sale5-half-M10-2026"&&webCaseId!="01GTGT-sale5-manual-M10-2026"&&webCaseId!="01GTGT-noactivity-zero-M10-2026"&&webCaseId!="01GTGT-noactivity-reset-sale10-M10-2026"&&webCaseId!="01GTGT-noactivity-cancel-sale10-M10-2026"&&webCaseId!="01GTGT-noactivity-uncheck-sale10-M10-2026"&&webCaseId!="01GTGT-noactivity-keep-credit-M10-2026"&&webCaseId!="01GTGT-zero-Q4-2026"&&webCaseId!="01GTGT-native-import-sale10-M10-2026"&&webCaseId!=Annex12WebZeroCaseId&&webCaseId!=Annex12WebTwoPlantsCaseId&&webCaseId!=Annex10WebNq204CaseId&&!KhbsCaseId(webCaseId))throw new InvalidOperationException();
  // The amendment cases run only in their own mode, and no other case runs there.
  if(KhbsCaseId(webCaseId)!=KhbsMode())throw new InvalidOperationException();
  webInputPath=host+".web-input.xml";webImportInputSha256=ReadOwnHexSidecar(host+".web-input.sha256",64);webSourceSha=ReadOwnHexSidecar(host+".web-source.sha",40);
  XmlDocument document=ReadBoundedOriginalXml(webInputPath);if(Hash(webInputPath)!=webImportInputSha256)throw new InvalidOperationException();
  if(FixedWebLeaf(document,"TTinChung/TTinTKhaiThue/NNT/mst")!=Mst||FixedWebLeaf(document,"TTinChung/TTinTKhaiThue/NNT/tenNNT")!=FakeName||FixedWebLeaf(document,"TTinChung/TTinTKhaiThue/TKhaiThue/nguoiKy")!=FakeSigner)throw new InvalidOperationException();
  if(FixedWebLeaf(document,"TTinChung/TTinDVu/maDVu")!="CCKK"||FixedWebLeaf(document,"TTinChung/TTinDVu/tenDVu")!="Công cụ Kê khai"||FixedWebLeaf(document,"TTinChung/TTinDVu/ttinNhaCCapDVu")!="hotrokekhai.net — Công cụ Kê khai, công cụ độc lập"||!Regex.IsMatch(FixedWebLeaf(document,"TTinChung/TTinDVu/pbanDVu"),"^[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}$"))throw new InvalidOperationException();
  if(FixedWebLeaf(document,"TTinChung/TTinTKhaiThue/TKhaiThue/maTKhai")!="842"||FixedWebLeaf(document,"TTinChung/TTinTKhaiThue/TKhaiThue/pbanTKhaiXML")!="2.8.3")throw new InvalidOperationException();
  if(KhbsMode()&&(FixedWebLeaf(document,"TTinChung/TTinTKhaiThue/TKhaiThue/loaiTKhai")!="B"||FixedWebLeaf(document,"TTinChung/TTinTKhaiThue/TKhaiThue/soLan")!=(webCaseId==KhbsLan2WebCaseId||webCaseId==KhbsAnnex12Lan2CaseId?"2":"1")))throw new InvalidOperationException();
  if(KhbsMode())khbsRound=1;
  // Lần 2 only: the staged previous-version file (bổ sung lần 1: the exact case-1 web file, or for case 5 the exact capture
  // case web file), never another case's.
  if(KhbsMode()&&(webCaseId==KhbsLan2WebCaseId||webCaseId==KhbsAnnex12Lan2CaseId)){
   webPriorPath=host+".web-prior.xml";webPriorSha256=ReadOwnHexSidecar(host+".web-prior.sha256",64);
   XmlDocument prior=ReadBoundedOriginalXml(webPriorPath);if(Hash(webPriorPath)!=webPriorSha256||webPriorSha256==webImportInputSha256)throw new InvalidOperationException();
   if(FixedWebLeaf(prior,"TTinChung/TTinTKhaiThue/NNT/mst")!=Mst||FixedWebLeaf(prior,"TTinChung/TTinTKhaiThue/TKhaiThue/loaiTKhai")!="B"||FixedWebLeaf(prior,"TTinChung/TTinTKhaiThue/TKhaiThue/soLan")!="1"||FixedWebLeaf(prior,"TTinChung/TTinTKhaiThue/TKhaiThue/KyKKhaiThue/kyKKhai")!="10/2026")throw new InvalidOperationException();
  }else if(File.Exists(host+".web-prior.xml")||File.Exists(host+".web-prior.sha256"))throw new InvalidOperationException();
  webInputVerified=true;Record();
 }
}
