// Pure whole-tree comparison of a synthetic web declaration with the ORIGINAL native re-export.
// Neither document is edited or serialized. Only the creation date and the four service-identity
// leaves follow the proven native rules (the same rule set as HtkkWebTaxComparison for D1).
// C# 2.0 / CLR2.
using System;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using System.Xml;

public static class HtkkDeclarationTreeComparison {
 private const string Ns="http://kekhaithue.gdt.gov.vn/TKhaiThue";
 private const string DatePath="HSoThueDTu/HSoKhaiThue/TTinChung/TTinTKhaiThue/TKhaiThue/ngayLapTKhai";
 private const string ServicePath="HSoThueDTu/HSoKhaiThue/TTinChung/TTinDVu/";
 // Bounded diagnostic sections (never values or paths): 1 TTinDVu, 2 TKhaiThue, 4 NNT,
 // 8 CTieuTKhaiChinh, 16 PLuc, 32 structure (element/attribute/child-count difference).
 public const int StructureBit=32;
 private static XmlElement Leaf(XmlDocument document,string path){string query="";foreach(string name in path.Split('/'))query+="/*[local-name()='"+name+"']";XmlNodeList nodes=document.SelectNodes(query);if(nodes.Count!=1||nodes[0].NamespaceURI!=Ns)return null;return (XmlElement)nodes[0];}
 private static string LeafText(XmlDocument document,string path){XmlElement leaf=Leaf(document,path);return leaf==null?null:leaf.InnerText;}
 // pbanDVu is the original's own release: the selected oracle (HtkkGuiReferenceAutomation.Start sets it
 // from HtkkOracleBaseline before any comparison; standalone use keeps the default 5.8.1).
 public static string NativeServiceVersion="5.8.1";
 public static bool NativeIdentity(XmlDocument output){
  string provider=LeafText(output,ServicePath+"ttinNhaCCapDVu");
  return LeafText(output,ServicePath+"maDVu")=="HTKK"&&LeafText(output,ServicePath+"tenDVu")=="HỖ TRỢ KÊ KHAI THUẾ"&&LeafText(output,ServicePath+"pbanDVu")==NativeServiceVersion&&provider!=null&&Regex.IsMatch(provider,"^[A-F0-9]{32}$");
 }
 public static bool CreationDateValid(XmlDocument output){string date=LeafText(output,DatePath);return date!=null&&Regex.IsMatch(date,"^[0-9]{4}-[0-9]{2}-[0-9]{2}$");}
 public static int Section(string path){
  string probe=path+"/";
  if(probe.IndexOf("/TTinDVu/",StringComparison.Ordinal)>=0)return 1;
  if(probe.IndexOf("/TKhaiThue/",StringComparison.Ordinal)>=0)return 2;
  if(probe.IndexOf("/NNT/",StringComparison.Ordinal)>=0)return 4;
  if(probe.IndexOf("/CTieuTKhaiChinh/",StringComparison.Ordinal)>=0)return 8;
  if(probe.IndexOf("/PLuc/",StringComparison.Ordinal)>=0)return 16;
  return StructureBit;
 }
 // Returns true only when every leaf matches; mask/leaves are always reported.
 public static bool Compare(XmlDocument input,XmlDocument output,int expectedLeaves,out int leaves,out int mask){return Compare(input,output,expectedLeaves,new string[0],out leaves,out mask);}
 // exportDatePaths: leaves the ORIGINAL export fills with the export day (form-specific, proven from
 // source). Each must equal its own document's creation date (web: draft date; native: export day);
 // a value that is not exactly that date is a mismatch, never ignored.
 public static bool Compare(XmlDocument input,XmlDocument output,int expectedLeaves,string[] exportDatePaths,out int leaves,out int mask){
  leaves=0;mask=0;
  if(input==null||output==null||input.DocumentElement==null||output.DocumentElement==null||exportDatePaths==null||exportDatePaths.Length>4){mask=StructureBit;return false;}
  string inputDate=LeafText(input,DatePath),outputDate=LeafText(output,DatePath);
  Walk(input.DocumentElement,output.DocumentElement,"HSoThueDTu",exportDatePaths,inputDate,outputDate,ref leaves,ref mask);
  if(!NativeIdentity(output))mask|=1;
  if(!CreationDateValid(output))mask|=2;
  return mask==0&&leaves==expectedLeaves;
 }
 private static List<XmlElement> Children(XmlElement element,ref bool mixed){List<XmlElement> values=new List<XmlElement>();foreach(XmlNode child in element.ChildNodes){if(child is XmlElement)values.Add((XmlElement)child);else if(child.NodeType==XmlNodeType.Text){if(child.Value.Trim().Length>0)mixed=true;}else if(child.NodeType!=XmlNodeType.Whitespace&&child.NodeType!=XmlNodeType.SignificantWhitespace)mixed=true;}return values;}
 private static Dictionary<string,string> Attributes(XmlElement element){Dictionary<string,string> values=new Dictionary<string,string>();foreach(XmlAttribute attribute in element.Attributes){if(attribute.NamespaceURI=="http://www.w3.org/2000/xmlns/")continue;values[attribute.NamespaceURI+"|"+attribute.LocalName]=attribute.Value;}return values;}
 private static void Walk(XmlElement a,XmlElement b,string path,string[] exportDatePaths,string inputDate,string outputDate,ref int leaves,ref int mask){
  if(a.NamespaceURI!=Ns||b.NamespaceURI!=Ns||a.LocalName!=b.LocalName){mask|=StructureBit|Section(path);return;}
  Dictionary<string,string> left=Attributes(a),right=Attributes(b);bool attributesEqual=left.Count==right.Count;
  if(attributesEqual)foreach(KeyValuePair<string,string> pair in left){string value;if(!right.TryGetValue(pair.Key,out value)||value!=pair.Value){attributesEqual=false;break;}}
  if(!attributesEqual)mask|=StructureBit|Section(path);
  bool mixedA=false,mixedB=false;List<XmlElement> x=Children(a,ref mixedA),y=Children(b,ref mixedB);
  if(x.Count!=y.Count){mask|=StructureBit|Section(path);return;}
  if(x.Count==0){
   if(path.StartsWith(ServicePath,StringComparison.Ordinal)){string name=path.Substring(ServicePath.Length);if(name!="maDVu"&&name!="tenDVu"&&name!="pbanDVu"&&name!="ttinNhaCCapDVu")mask|=StructureBit;return;}
   leaves++;
   if(Array.IndexOf(exportDatePaths,path)>=0){if(inputDate==null||outputDate==null||a.InnerText!=inputDate||b.InnerText!=outputDate)mask|=Section(path);return;}
   if(path!=DatePath&&a.InnerText!=b.InnerText)mask|=Section(path);return;
  }
  if(mixedA||mixedB){mask|=StructureBit|Section(path);return;}
  for(int index=0;index<x.Count;index++)Walk(x[index],y[index],path+"/"+x[index].LocalName,exportDatePaths,inputDate,outputDate,ref leaves,ref mask);
 }
}
