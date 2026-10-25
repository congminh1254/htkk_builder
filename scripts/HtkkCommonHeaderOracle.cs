// Our reflection harness. It invokes authenticated original methods without altering them.
using System;
using System.IO;
using System.Reflection;
using System.Text;
using System.Xml;
using System.Collections.Generic;
internal static class HtkkCommonHeaderOracle {
 private static string project,stage="start",runtime="unknown";
 private static readonly List<int> failed=new List<int>();
 private static int cases=0,matched=0,getInvocations=0,bindInvocations=0,serializeInvocations=0;
 private static Assembly Resolve(object sender,ResolveEventArgs args){string name=new AssemblyName(args.Name).Name;if(String.IsNullOrEmpty(name)||name.IndexOfAny(new char[]{'/',(char)92,':'})>=0)return null;string file=Path.Combine(project,name+".dll");return File.Exists(file)?Assembly.LoadFrom(file):null;}
 private static void Check(bool result){cases++;if(result)matched++;else failed.Add(cases);}
 private static void Set(object instance,string name,string value){PropertyInfo p=instance.GetType().GetProperty(name,BindingFlags.Public|BindingFlags.Instance);if(p==null||p.PropertyType!=typeof(string))throw new InvalidOperationException();p.SetValue(instance,value,null);}
 private static string Get(object instance,string name){return (string)instance.GetType().GetProperty(name,BindingFlags.Public|BindingFlags.Instance).GetValue(instance,null);}
 private static XmlDocument Load(string file){XmlReaderSettings settings=new XmlReaderSettings();settings.ProhibitDtd=true;settings.XmlResolver=null;XmlDocument d=new XmlDocument();d.XmlResolver=null;using(XmlReader r=XmlReader.Create(file,settings)){d.Load(r);}return d;}
 private static XmlDocument EmptyCommon(string template){XmlDocument original=Load(template),d=new XmlDocument();d.XmlResolver=null;XmlNode common=original.SelectSingleNode("//TTinChung");if(common==null)throw new InvalidOperationException();d.AppendChild(d.ImportNode(common,true));foreach(XmlNode node in d.SelectNodes("//*[not(*)]")){node.InnerText=String.Empty;}return d;}
 private static string Text(XmlDocument doc,string path){XmlNode n=doc.SelectSingleNode(path);if(n==null)throw new InvalidOperationException();return n.InnerText;}
 private static void Result(string output,string status){string failures=String.Join(",",failed.ConvertAll<string>(delegate(int value){return value.ToString();}).ToArray());string q=((char)34).ToString();string text="{"+q+"format"+q+":"+q+"htkk-common-header-oracle-v1"+q+","+q+"status"+q+":"+q+status+q+","+q+"stage"+q+":"+q+stage+q+","+q+"runtime"+q+":"+q+runtime+q+","+q+"cases"+q+":"+cases+","+q+"matched"+q+":"+matched+","+q+"failedChecks"+q+":["+failures+"],"+q+"getToKhaiInfoInvocations"+q+":"+getInvocations+","+q+"bindInvocations"+q+":"+bindInvocations+","+q+"serializeInvocations"+q+":"+serializeInvocations+"}";File.WriteAllText(output,text,Encoding.UTF8);}
 [STAThread] public static int Main(string[] args){if(args.Length!=5)return 9;string output=args[4];try{
  runtime=Environment.Version.Major==2?"clr2":"unsupported";if(runtime!="clr2"){Result(output,"runtime-blocked");return 3;}
  project=Path.GetFullPath(args[0]);AppDomain.CurrentDomain.AssemblyResolve+=new ResolveEventHandler(Resolve);
  stage="assembly-types";Assembly exe=Assembly.LoadFrom(Path.Combine(project,"HTKK.exe"));Type settings=exe.GetType("HTKK.WinSettings",true),fn=exe.GetType("HTKK.WinFnProcess",true),events=exe.GetType("HTKK.WinDoWorkEvent",true);
  BindingFlags flags=BindingFlags.Public|BindingFlags.NonPublic|BindingFlags.Static;
  FieldInfo periodField=settings.GetField("TTPeriodInfo",flags),headerField=settings.GetField("HTKKHeaderInfo",flags),commonField=settings.GetField("TTinChung",flags),declarationField=settings.GetField("ToKhaiInfo",flags);
  MethodInfo get=fn.GetMethod("GetToKhaiInfo",BindingFlags.Public|BindingFlags.Static),bind=fn.GetMethod("BindToKhaiInfoToTTinChung",BindingFlags.Public|BindingFlags.Static),serialize=events.GetMethod("xmlExportTTinChungProcessNode",BindingFlags.Public|BindingFlags.Static);
  stage="synthetic-profile";object header=Activator.CreateInstance(headerField.FieldType);Set(header,"mst","9999999997");Set(header,"tenNNT","SYNTHETIC & <NNT> \u0110\u1ed0I CHI\u1ebeU");Set(header,"dchiNNT","SYNTHETIC ADDRESS");Set(header,"tenXaPhuongNNT","SYNTHETIC NEW WARD");Set(header,"maXaPhuongNNT","91000002");Set(header,"maHuyenNNT","9100001");Set(header,"tenXaPhuongDLyThue","SYNTHETIC AGENT WARD");Set(header,"maXaPhuongDLyThue","91000003");Set(header,"maXaPhuongDlyThue","91000004");Set(header,"nguoiKy","SYNTHETIC SIGNER");headerField.SetValue(null,header);settings.GetField("MenuID",flags).SetValue(null,"D1");
  XmlDocument menu=Load(args[1]);XmlNode menuNode=menu.SelectSingleNode("//*[@ID='D1']");if(menuNode==null)throw new InvalidOperationException();
  string[] modes=new string[]{"C","B"};
  for(int index=0;index<modes.Length;index++){
   // Explicit range inputs prevent unrelated constructor defaults entering this synthetic oracle.
   stage="period";object period=Activator.CreateInstance(periodField.FieldType);Set(period,"LoaiToKhai",modes[index]);Set(period,"SoLan",index.ToString());Set(period,"KieuKy","M");Set(period,"TuNgay",String.Empty);Set(period,"DenNgay",String.Empty);Set(period,"TuThang",String.Empty);Set(period,"DenThang",String.Empty);Set(period,"Thang","10");Set(period,"Nam","2026");Set(period,"kyKKhai","10/2026");Set(period,"menuID","D1");periodField.SetValue(null,period);
   stage="get-declaration";object declaration=get.Invoke(null,new object[]{menuNode,period});getInvocations++;declarationField.SetValue(null,declaration);
   Check(Get(declaration,"MaToKhai")=="842");Check(Get(declaration,"VersionXML")=="2.8.3");Check(Get(declaration,"TenToKhai")==menuNode.Attributes["TenToKhai"].Value);Check(Get(declaration,"MoTaBieuMau")==menuNode.Attributes["MoTaBieuMau"].Value);
   stage="bind";object common=Activator.CreateInstance(commonField.FieldType);Set(common,"phuongXa","SYNTHETIC LEGACY SENTINEL");commonField.SetValue(null,common);bind.Invoke(null,new object[0]);bindInvocations++;
   Check(Get(common,"maTKhai")=="842");Check(Get(common,"pbanTKhaiXML")=="2.8.3");Check(Get(common,"loaiTKhai")==modes[index]);Check(Get(common,"soLan")==index.ToString());
   Check(Get(common,"phuongXa")==String.Empty);Check(Get(common,"tenXaPhuongNNT")=="SYNTHETIC NEW WARD");Check(Get(common,"maXaPhuongNNT")=="91000002");Check(Get(common,"tenXaPhuongDLyThue")=="SYNTHETIC AGENT WARD");Check(Get(common,"maXaPhuongDlyThue")=="91000004");
   stage="serialize";XmlDocument document=EmptyCommon(args[2]);serialize.Invoke(null,new object[]{document.DocumentElement});serializeInvocations++;
   string basePath="/TTinChung/TTinTKhaiThue/TKhaiThue/";
   Check(Text(document,basePath+"maTKhai")=="842");Check(Text(document,basePath+"pbanTKhaiXML")=="2.8.3");Check(Text(document,basePath+"loaiTKhai")==modes[index]);Check(Text(document,basePath+"soLan")==index.ToString());Check(Text(document,"/TTinChung/TTinTKhaiThue/NNT/phuongXa")==String.Empty);Check(Text(document,"/TTinChung/TTinTKhaiThue/NNT/tenNNT")==Get(header,"tenNNT"));Check(document.SelectSingleNode("//tenXaPhuongNNT")==null&&document.SelectSingleNode("//maXaPhuongNNT")==null);
   stage="save-synthetic";document.Save(Path.Combine(args[3],index==0?"common-header-first.xml":"common-header-supplement.xml"));
   // D1 exporter replaces existing template metadata with the bound source property.
   stage="d1-overwrites-existing-metadata";document.SelectSingleNode(basePath+"maTKhai").InnerText="SYNTHETIC KEEP";serialize.Invoke(null,new object[]{document.DocumentElement});serializeInvocations++;Check(Text(document,basePath+"maTKhai")=="842");
  }
  stage="version-fallback";object last=commonField.GetValue(null);Set(last,"pbanTKhaiXML",String.Empty);XmlDocument fallback=EmptyCommon(args[2]);serialize.Invoke(null,new object[]{fallback.DocumentElement});serializeInvocations++;Check(Text(fallback,"/TTinChung/TTinTKhaiThue/TKhaiThue/pbanTKhaiXML")=="2.8.3");
  stage="complete";bool ok=cases==43&&matched==cases&&getInvocations==2&&bindInvocations==2&&serializeInvocations==5;Result(output,ok?"matched":"mismatch");return ok?0:2;
 }catch{try{Result(output,"reflection-or-runtime-blocked");}catch{}return 7;}}
}
