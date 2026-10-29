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
 public static bool NativeIdentity(XmlDocument baseline,XmlDocument output){
  foreach(string name in new string[]{"maDVu","tenDVu","pbanDVu","ttinNhaCCapDVu"})if(Leaf(output,ServicePath+name).InnerText!=Leaf(baseline,ServicePath+name).InnerText)return false;
  return Leaf(output,ServicePath+"maDVu").InnerText=="HTKK"&&Leaf(output,ServicePath+"tenDVu").InnerText=="HỖ TRỢ KÊ KHAI THUẾ"&&Leaf(output,ServicePath+"pbanDVu").InnerText=="5.8.1"&&Regex.IsMatch(Leaf(output,ServicePath+"ttinNhaCCapDVu").InnerText,"^[A-F0-9]{32}$");
 }
 public static bool CreationDateMatchesNativeBaseline(XmlDocument baseline,XmlDocument output){string date=Leaf(output,DatePath).InnerText;return Regex.IsMatch(date,"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")&&date==Leaf(baseline,DatePath).InnerText;}
 public static bool Compare(XmlDocument input,XmlDocument baseline,XmlDocument output,out int taxLeaves){taxLeaves=0;return NativeIdentity(baseline,output)&&CreationDateMatchesNativeBaseline(baseline,output)&&Equal(input.DocumentElement,output.DocumentElement,"HSoThueDTu",ref taxLeaves)&&taxLeaves==70;}
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
}
