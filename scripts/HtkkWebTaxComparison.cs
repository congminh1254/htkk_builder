// Pure comparison of synthetic web input with original-native reexport.
// Does not edit either document or serialize a replacement declaration.
using System;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using System.Xml;
public static class HtkkWebTaxComparison {
 private const string Ns="http://kekhaithue.gdt.gov.vn/TKhaiThue";
 private const string DatePath="HSoThueDTu/HSoKhaiThue/TTinChung/TTinTKhaiThue/TKhaiThue/ngayLapTKhai";
 private const string ServicePath="HSoThueDTu/HSoKhaiThue/TTinChung/TTinDVu/";
 private static XmlElement Leaf(XmlDocument document,string path){string query="";foreach(string name in path.Split('/'))query+="/*[local-name()='"+name+"']";XmlNodeList nodes=document.SelectNodes(query);if(nodes.Count!=1||nodes[0].NamespaceURI!=Ns)throw new InvalidOperationException();return (XmlElement)nodes[0];}
 // Original WinDoWorkEvent.WinDoWorkExportXML (HTKK.exe 0x6000045, IL 0x08cc-0x0989) sets
 // ttinNhaCCapDVu := HashGenerator.GenerateKey(InnerXml of HSoKhaiThue without TTinDVu,
 // "HTKK.CMCSoft") and saves the document right after. The key is a deterministic function of
 // the declaration content, so it equals the baseline key exactly when that content is equal:
 // equal content with another key, or different content with the same key, is not native.
 // A baseline built with other annex rows than the imported input (two-plant case) therefore
 // carries another key (run 42310299991: roundtripXmlExactMatched false, identity false).
 // pbanDVu is the original's own release: the selected oracle (HtkkGuiReferenceAutomation.Start sets it
 // from HtkkOracleBaseline before any comparison; standalone use keeps the default 5.8.1).
 public static string NativeServiceVersion="5.8.1";
 public static bool NativeIdentity(XmlDocument baseline,XmlDocument output){
  foreach(string name in new string[]{"maDVu","tenDVu","pbanDVu"})if(Leaf(output,ServicePath+name).InnerText!=Leaf(baseline,ServicePath+name).InnerText)return false;
  string provider=Leaf(output,ServicePath+"ttinNhaCCapDVu").InnerText,baselineProvider=Leaf(baseline,ServicePath+"ttinNhaCCapDVu").InnerText;
  if(!Regex.IsMatch(baselineProvider,"^[A-F0-9]{32}$")||(provider==baselineProvider)!=(HashedContent(baseline)==HashedContent(output)))return false;
  return Leaf(output,ServicePath+"maDVu").InnerText=="HTKK"&&Leaf(output,ServicePath+"tenDVu").InnerText=="HỖ TRỢ KÊ KHAI THUẾ"&&Leaf(output,ServicePath+"pbanDVu").InnerText==NativeServiceVersion&&Regex.IsMatch(provider,"^[A-F0-9]{32}$");
 }
 // The content the original key covers: HSoKhaiThue without TTinDVu (an in-memory copy only).
 private static string HashedContent(XmlDocument document){
  XmlElement declaration=Leaf(document,"HSoThueDTu/HSoKhaiThue");XmlDocument copy=new XmlDocument();copy.LoadXml(declaration.OuterXml);
  XmlNodeList services=copy.DocumentElement.SelectNodes("*[local-name()='TTinChung']/*[local-name()='TTinDVu']");if(services.Count!=1)throw new InvalidOperationException();
  services[0].ParentNode.RemoveChild(services[0]);return copy.DocumentElement.InnerXml;
 }
 public static bool CreationDateMatchesNativeBaseline(XmlDocument baseline,XmlDocument output){string date=Leaf(output,DatePath).InnerText;return Regex.IsMatch(date,"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")&&date==Leaf(baseline,DatePath).InnerText;}
 public static bool Compare(XmlDocument input,XmlDocument baseline,XmlDocument output,out int taxLeaves){return Compare(input,baseline,output,70,out taxLeaves);}
 // Whole tree, including every annex leaf. Only the creation date and four service
 // identity leaves follow the proven native rules; the expected count is fixed per case.
 public static bool Compare(XmlDocument input,XmlDocument baseline,XmlDocument output,int expectedTaxLeaves,out int taxLeaves){taxLeaves=0;if(expectedTaxLeaves!=70&&expectedTaxLeaves!=88&&expectedTaxLeaves!=108&&expectedTaxLeaves!=159)return false;return NativeIdentity(baseline,output)&&CreationDateMatchesNativeBaseline(baseline,output)&&Equal(input.DocumentElement,output.DocumentElement,"HSoThueDTu",ref taxLeaves)&&taxLeaves==expectedTaxLeaves;}
 private static List<XmlElement> Children(XmlElement element){List<XmlElement> values=new List<XmlElement>();foreach(XmlNode child in element.ChildNodes){if(child is XmlElement)values.Add((XmlElement)child);else if(child.NodeType!=XmlNodeType.Text&&child.NodeType!=XmlNodeType.Whitespace&&child.NodeType!=XmlNodeType.SignificantWhitespace)throw new InvalidOperationException();}return values;}
 private static Dictionary<string,string> Attributes(XmlElement element){Dictionary<string,string> values=new Dictionary<string,string>();foreach(XmlAttribute attribute in element.Attributes){if(attribute.NamespaceURI=="http://www.w3.org/2000/xmlns/")continue;values.Add(attribute.NamespaceURI+"|"+attribute.LocalName,attribute.Value);}return values;}
 private static bool Equal(XmlElement input,XmlElement output,string path,ref int taxLeaves){
  if(input.NamespaceURI!=Ns||output.NamespaceURI!=Ns||input.LocalName!=output.LocalName)return false;
  Dictionary<string,string> left=Attributes(input),right=Attributes(output);if(left.Count!=right.Count)return false;foreach(KeyValuePair<string,string> attribute in left){string value;if(!right.TryGetValue(attribute.Key,out value)||value!=attribute.Value)return false;}
  List<XmlElement> a=Children(input),b=Children(output);if(a.Count!=b.Count)return false;
  if(a.Count==0){if(path.StartsWith(ServicePath,StringComparison.Ordinal)){string name=path.Substring(ServicePath.Length);return name=="maDVu"||name=="tenDVu"||name=="pbanDVu"||name=="ttinNhaCCapDVu";}taxLeaves++;return path==DatePath||input.InnerText==output.InnerText;}
  // Non-whitespace mixed text is never discarded from structural comparison.
  foreach(XmlNode child in input.ChildNodes)if(child.NodeType==XmlNodeType.Text&&!String.IsNullOrEmpty(child.Value.Trim()))return false;
  foreach(XmlNode child in output.ChildNodes)if(child.NodeType==XmlNodeType.Text&&!String.IsNullOrEmpty(child.Value.Trim()))return false;
  for(int index=0;index<a.Count;index++)if(!Equal(a[index],b[index],path+"/"+a[index].LocalName,ref taxLeaves))return false;return true;
 }
 // Amendment (KHBS) case: whole web B1 tree against the ORIGINAL export after Nhập từ XML and Tổng hợp KHBS. There is no
 // native baseline export, so the service identity is checked on the output alone (HTKK, its release, a 32-hex key) and
 // ngayLapTKhai is the original's export date (any valid date). Every other leaf, element order and attribute must be
 // equal. Bounded diagnostics only: mask bits 1 structure (names/counts), 2 attributes, 4 TTinChung value, 8
 // CTieuTKhaiChinh value, 16 PL01_KHBS value, 32 PL01_1_KHBS value, 64 other value, 128 output identity or date;
 // firstDifference is the 1-based ordinal of the first differing leaf in input order (0 = none).
 public static bool CompareKhbs(XmlDocument input,XmlDocument output,int expectedLeaves,out int leaves,out int mask,out int firstDifference,out bool identity,out bool dateValid){
  leaves=0;mask=0;firstDifference=0;identity=false;dateValid=false;
  try{
   string provider=Leaf(output,ServicePath+"ttinNhaCCapDVu").InnerText;
   identity=Leaf(output,ServicePath+"maDVu").InnerText=="HTKK"&&Leaf(output,ServicePath+"tenDVu").InnerText=="HỖ TRỢ KÊ KHAI THUẾ"&&Leaf(output,ServicePath+"pbanDVu").InnerText==NativeServiceVersion&&Regex.IsMatch(provider,"^[A-F0-9]{32}$");
   DateTime parsed;dateValid=DateTime.TryParseExact(Leaf(output,DatePath).InnerText,"yyyy-MM-dd",System.Globalization.CultureInfo.InvariantCulture,System.Globalization.DateTimeStyles.None,out parsed);
  }catch(InvalidOperationException){mask|=1;}
  if(!identity||!dateValid)mask|=128;
  KhbsEqual(input.DocumentElement,output.DocumentElement,"HSoThueDTu",ref leaves,ref mask,ref firstDifference);
  if(leaves!=expectedLeaves)mask|=1;
  return mask==0;
 }
 private static int KhbsRegion(string path){
  if(path.StartsWith("HSoThueDTu/HSoKhaiThue/TTinChung/",StringComparison.Ordinal))return 4;
  if(path.StartsWith("HSoThueDTu/HSoKhaiThue/CTieuTKhaiChinh/",StringComparison.Ordinal))return 8;
  if(path.StartsWith("HSoThueDTu/HSoKhaiThue/PLuc/PL01_KHBS/",StringComparison.Ordinal))return 16;
  if(path.StartsWith("HSoThueDTu/HSoKhaiThue/PLuc/PL01_1_KHBS/",StringComparison.Ordinal))return 32;
  return 64;
 }
 private static void KhbsDiffer(int bit,int ordinal,ref int mask,ref int first){mask|=bit;if(first==0)first=Math.Max(1,ordinal);}
 private static void KhbsEqual(XmlElement input,XmlElement output,string path,ref int leaves,ref int mask,ref int first){
  if(input.NamespaceURI!=Ns||output.NamespaceURI!=Ns||input.LocalName!=output.LocalName){KhbsDiffer(1,leaves+1,ref mask,ref first);return;}
  Dictionary<string,string> left=Attributes(input),right=Attributes(output);bool same=left.Count==right.Count;
  if(same)foreach(KeyValuePair<string,string> attribute in left){string value;if(!right.TryGetValue(attribute.Key,out value)||value!=attribute.Value){same=false;break;}}
  if(!same)KhbsDiffer(2,leaves+1,ref mask,ref first);
  List<XmlElement> a,b;
  try{a=Children(input);b=Children(output);}catch(InvalidOperationException){KhbsDiffer(1,leaves+1,ref mask,ref first);return;}
  if(a.Count==0&&b.Count==0){
   if(path.StartsWith(ServicePath,StringComparison.Ordinal))return;
   leaves++;if(path!=DatePath&&input.InnerText!=output.InnerText)KhbsDiffer(KhbsRegion(path),leaves,ref mask,ref first);return;
  }
  if(a.Count!=b.Count){KhbsDiffer(1,leaves+1,ref mask,ref first);return;}
  foreach(XmlNode child in input.ChildNodes)if(child.NodeType==XmlNodeType.Text&&!String.IsNullOrEmpty(child.Value.Trim())){KhbsDiffer(1,leaves+1,ref mask,ref first);return;}
  foreach(XmlNode child in output.ChildNodes)if(child.NodeType==XmlNodeType.Text&&!String.IsNullOrEmpty(child.Value.Trim())){KhbsDiffer(1,leaves+1,ref mask,ref first);return;}
  for(int index=0;index<a.Count;index++)KhbsEqual(a[index],b[index],path+"/"+a[index].LocalName,ref leaves,ref mask,ref first);
 }
}
