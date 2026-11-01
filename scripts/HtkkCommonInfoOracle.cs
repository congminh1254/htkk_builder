// Fixed synthetic common-info binding. Does not run Main, load profiles or modify original config.
using System;using System.IO;using System.Reflection;using System.Globalization;using System.Text;using System.Collections.Generic;
public sealed class HtkkCommonInfoProbe:MarshalByRefObject {
 string project;public override object InitializeLifetimeService(){return null;}
 Assembly Resolve(object sender,ResolveEventArgs e){string n=new AssemblyName(e.Name).Name;if(n.IndexOfAny(new char[]{'/','\\',':'})>=0)return null;string path=Path.Combine(project,n+".dll");return File.Exists(path)?Assembly.LoadFrom(path):null;}
 static string Q(string s){if(s==null)return "null";return "\""+s.Replace("\\","\\\\").Replace("\"","\\\"").Replace("\r","\\r").Replace("\n","\\n").Replace("\t","\\t")+"\"";}
 static void Fill(object target,bool empty){foreach(PropertyInfo p in target.GetType().GetProperties()){if(p.CanWrite&&p.PropertyType==typeof(string))p.SetValue(target,empty?"":"synthetic-"+p.Name,null);}}
 static void Set(object target,string name,string value){PropertyInfo p=target.GetType().GetProperty(name);if(p==null||p.PropertyType!=typeof(string))throw new InvalidOperationException();p.SetValue(target,value,null);}
 public string Run(string directory){project=directory;AppDomain.CurrentDomain.AssemblyResolve+=Resolve;System.Threading.Thread.CurrentThread.CurrentCulture=CultureInfo.InvariantCulture;System.Threading.Thread.CurrentThread.CurrentUICulture=CultureInfo.InvariantCulture;
  Assembly app=Assembly.LoadFrom(Path.Combine(project,"HTKK.exe"));Type settings=app.GetType("HTKK.WinSettings",true);BindingFlags flags=BindingFlags.Public|BindingFlags.NonPublic|BindingFlags.Static;
  MethodInfo binder=app.GetType("HTKK.WinFnProcess",true).GetMethod("BindToKhaiInfoToTTinChung",BindingFlags.Public|BindingFlags.Static,null,Type.EmptyTypes,null);if(binder==null||binder.MetadataToken!=0x060000f4)throw new InvalidOperationException();
  FieldInfo declarationField=settings.GetField("ToKhaiInfo",flags),periodField=settings.GetField("TTPeriodInfo",flags),profileField=settings.GetField("HTKKHeaderInfo",flags),commonField=settings.GetField("TTinChung",flags),menuField=settings.GetField("MenuID",flags);
  string[] menus={"D1","D1","73","56","D1"};List<string> cases=new List<string>();
  for(int i=0;i<menus.Length;i++){
   object declaration=Activator.CreateInstance(declarationField.FieldType),period=Activator.CreateInstance(periodField.FieldType),profile=Activator.CreateInstance(profileField.FieldType),common=Activator.CreateInstance(commonField.FieldType);
   Fill(declaration,false);Fill(period,false);Fill(profile,i==4);Set(declaration,"VersionXML","source-main");Set(declaration,"VersionKBSXML","source-supplemental");Set(period,"LoaiToKhai",i==1?"B":"C");
   declarationField.SetValue(null,declaration);periodField.SetValue(null,period);profileField.SetValue(null,profile);commonField.SetValue(null,common);menuField.SetValue(null,menus[i]);
   string before=DateTime.Now.ToString("dd/MM/yyyy",CultureInfo.InvariantCulture);binder.Invoke(null,new object[0]);string after=DateTime.Now.ToString("dd/MM/yyyy",CultureInfo.InvariantCulture);common=commonField.GetValue(null);
   List<string> values=new List<string>();foreach(PropertyInfo p in common.GetType().GetProperties()){if(!p.CanRead||p.PropertyType!=typeof(string))throw new InvalidOperationException();object value=p.GetValue(common,null);values.Add(Q(p.Name)+":"+Q((string)value));}values.Sort(StringComparer.Ordinal);if(values.Count!=69)throw new InvalidOperationException();
   cases.Add("{\"id\":"+(i+1)+",\"menu\":"+Q(menus[i])+",\"supplemental\":"+(i==1?"true":"false")+",\"emptyProfile\":"+(i==4?"true":"false")+",\"beforeDate\":"+Q(before)+",\"afterDate\":"+Q(after)+",\"values\":{"+String.Join(",",values.ToArray())+"}}");
  }
  return "{\"format\":\"htkk-common-info-oracle-v1\",\"runtime\":\"clr2-x86\",\"primitiveOnly\":true,\"cases\":["+String.Join(",",cases.ToArray())+"]}";
 }
}
internal static class HtkkCommonInfoOracle {
 [STAThread]static int Main(string[] args){if(args.Length!=2)return 9;try{if(Environment.Version.Major!=2||IntPtr.Size!=4)return 3;string project=Path.GetFullPath(args[0]);AppDomainSetup setup=new AppDomainSetup();setup.ApplicationBase=project;setup.ConfigurationFile=Path.Combine(project,"HTKK.exe.config");setup.ShadowCopyFiles="false";AppDomain domain=AppDomain.CreateDomain("HTKK fixed common-info oracle",null,setup);try{HtkkCommonInfoProbe probe=(HtkkCommonInfoProbe)domain.CreateInstanceFromAndUnwrap(Assembly.GetExecutingAssembly().Location,"HtkkCommonInfoProbe");string result=probe.Run(project);File.WriteAllText(args[1],result,new UTF8Encoding(false));}finally{AppDomain.Unload(domain);}return 0;}catch{return 5;}}
}
