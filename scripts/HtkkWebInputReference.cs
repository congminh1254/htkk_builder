// Own private staged WEB XML input. Verification only: never creates or edits XML.
using System;
using System.IO;
using System.Reflection;
using System.Text;
using System.Text.RegularExpressions;
using System.Xml;
public sealed partial class HtkkGuiReferenceAutomation {
 private bool webTaxValuesMatched=false,webCreationDateMatchedNativeBaseline=false,webServiceIdentityMatched=false;private int webTaxLeafCount=0;
 private bool webInputVerified=false;private string webInputPath="",webImportInputSha256="",webSourceSha="";
 private string WebInputJson(){string q=((char)34).ToString();return ","+q+"webTaxValuesMatched"+q+":"+Bool(webTaxValuesMatched)+","+q+"webCreationDateMatchedNativeBaseline"+q+":"+Bool(webCreationDateMatchedNativeBaseline)+","+q+"webServiceIdentityMatched"+q+":"+Bool(webServiceIdentityMatched)+","+q+"webTaxLeafCount"+q+":"+webTaxLeafCount+","+q+"webInputVerified"+q+":"+Bool(webInputVerified)+","+q+"webImportInputSha256"+q+":"+q+webImportInputSha256+q+","+q+"webSourceSha"+q+":"+q+webSourceSha+q;}
 private string RoundtripInputPath(){return mode=="gtgt-web-import-inspect"?webInputPath:firstExportPath;}
 private string RoundtripInputHash(){return mode=="gtgt-web-import-inspect"?webImportInputSha256:firstExportSha256;}
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
  webInputPath=host+".web-input.xml";webImportInputSha256=ReadOwnHexSidecar(host+".web-input.sha256",64);webSourceSha=ReadOwnHexSidecar(host+".web-source.sha",40);
  XmlDocument document=ReadBoundedOriginalXml(webInputPath);if(Hash(webInputPath)!=webImportInputSha256)throw new InvalidOperationException();
  if(FixedWebLeaf(document,"TTinChung/TTinTKhaiThue/NNT/mst")!=Mst||FixedWebLeaf(document,"TTinChung/TTinTKhaiThue/NNT/tenNNT")!=FakeName||FixedWebLeaf(document,"TTinChung/TTinTKhaiThue/TKhaiThue/nguoiKy")!=FakeSigner)throw new InvalidOperationException();
  if(FixedWebLeaf(document,"TTinChung/TTinDVu/maDVu")!="HTKK-WEB-DRAFT"||FixedWebLeaf(document,"TTinChung/TTinDVu/tenDVu")!="Hỗ trợ kê khai — bản nháp"||FixedWebLeaf(document,"TTinChung/TTinDVu/ttinNhaCCapDVu")!="hotrokekhai.net — công cụ hỗ trợ độc lập"||!Regex.IsMatch(FixedWebLeaf(document,"TTinChung/TTinDVu/pbanDVu"),"^[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}$"))throw new InvalidOperationException();
  if(FixedWebLeaf(document,"TTinChung/TTinTKhaiThue/TKhaiThue/maTKhai")!="842"||FixedWebLeaf(document,"TTinChung/TTinTKhaiThue/TKhaiThue/pbanTKhaiXML")!="2.8.3")throw new InvalidOperationException();
  webInputVerified=true;Record();
 }
}
