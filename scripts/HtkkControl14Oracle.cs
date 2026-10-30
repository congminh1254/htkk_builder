// Fixed synthetic control-14 probes; no declaration, taxpayer data, XML or application initialization.
using System;
using System.IO;
using System.Reflection;
using System.Globalization;
using System.Text;
using System.Collections.Generic;
internal static class HtkkControl14Oracle {
 static string project;static Type sheetType,generalType;
 static Assembly Resolve(object sender,ResolveEventArgs e){string n=new AssemblyName(e.Name).Name;if(n.IndexOfAny(new char[]{'/','\\',':'})>=0)return null;string p=Path.Combine(project,n+".dll");return File.Exists(p)?Assembly.LoadFrom(p):null;}
 static string Escape(string x){return x.Replace("\\","\\\\").Replace("\"","\\\"").Replace("\r","\\r").Replace("\n","\\n").Replace("\t","\\t");}
 static object Call(object s,string method,Type[] types,object[] args){return sheetType.GetMethod(method,types).Invoke(s,args);}
 static string Q(string x){return x==null?"null":"\""+Escape(x)+"\"";}
 static string Probe(string input,string mode){object sheet=Activator.CreateInstance(sheetType);try{
  sheetType.GetProperty("RowCount").SetValue(sheet,4,null);sheetType.GetProperty("ColumnCount").SetValue(sheet,4,null);
  generalType.GetMethod("fpSpBindDataCell",new Type[]{sheetType,typeof(int),typeof(int),typeof(string),typeof(string)}).Invoke(null,new object[]{sheet,1,1,"14",mode=="bind"?input:""});
  string rejected=null;
  if(mode=="edit"){try{Call(sheet,"SetText",new Type[]{typeof(int),typeof(int),typeof(string)},new object[]{0,0,input});}catch(TargetInvocationException e){rejected=e.InnerException==null?"TargetInvocationException":e.InnerException.GetType().FullName;}}
  if(mode=="formula"){Call(sheet,"SetFormula",new Type[]{typeof(int),typeof(int),typeof(string)},new object[]{0,0,"\""+(input??"").Replace("\"","\"\"")+"\""});Call(sheet,"RecalculateAll",Type.EmptyTypes,new object[0]);}
  object value=Call(sheet,"GetValue",new Type[]{typeof(int),typeof(int)},new object[]{0,0});string text=(string)Call(sheet,"GetText",new Type[]{typeof(int),typeof(int)},new object[]{0,0});
  object celltype=Call(sheet,"GetCellType",new Type[]{typeof(int),typeof(int)},new object[]{0,0});string mask=(string)celltype.GetType().GetProperty("Mask").GetValue(celltype,null);char maskchar=(char)celltype.GetType().GetProperty("MaskChar").GetValue(celltype,null);
  string exported=(string)generalType.GetMethod("GetValueExport",new Type[]{sheetType,typeof(string),typeof(int),typeof(int),typeof(string)}).Invoke(null,new object[]{sheet,"14",1,1,null});
  return "{\"text\":"+Q(text)+",\"value\":"+Q(value==null?null:Convert.ToString(value,CultureInfo.InvariantCulture))+",\"valueClrType\":"+Q(value==null?"null":value.GetType().FullName)+",\"cellType\":"+Q(celltype.GetType().FullName)+",\"mask\":"+Q(mask)+",\"maskChar\":"+Q(maskchar.ToString())+",\"exported\":"+Q(exported)+",\"editRejected\":"+Q(rejected)+"}";
 }finally{IDisposable d=sheet as IDisposable;if(d!=null)d.Dispose();}}
 [STAThread]static int Main(string[] a){if(a.Length!=2)return 9;try{
  if(Environment.Version.Major!=2||IntPtr.Size!=4)return 3;project=Path.GetFullPath(a[0]);AppDomain.CurrentDomain.AssemblyResolve+=Resolve;
  Assembly spread=Assembly.LoadFrom(Path.Combine(project,"FarPoint.Win.Spread.dll"));sheetType=spread.GetType("FarPoint.Win.Spread.SheetView",true);Assembly business=Assembly.LoadFrom(Path.Combine(project,"TAX.HTKK.Business.dll"));generalType=business.GetType("TAX.HTKK.Business.GeneralFunctions",true);
  string[] inputs={null,""," ","null","30/10/2026","30102026","30-10-2026","30\\10\\2026","2026-10-30","1/2/2026","01/02/2026","29/02/2024","29/02/2026","31/04/2026","00/01/2026","01/13/2026","01/01/0001","31/12/9999","2026","102026","../../...."," 30/10/2026 ","30/10/26","30/10/2026abc","01.02.2026","01022026"};
  List<string> records=new List<string>();int id=0;string[] cultures={"invariant","vi-VN"};foreach(string culture in cultures){CultureInfo ci=culture=="invariant"?CultureInfo.InvariantCulture:new CultureInfo(culture);System.Threading.Thread.CurrentThread.CurrentCulture=ci;System.Threading.Thread.CurrentThread.CurrentUICulture=ci;
   foreach(string mode in new string[]{"bind","edit","formula"})foreach(string input in inputs){id++;records.Add("{\"id\":"+id+",\"culture\":"+Q(culture)+",\"mode\":"+Q(mode)+",\"input\":"+Q(input)+",\"result\":"+Probe(input,mode)+"}");}
  }
  File.WriteAllText(a[1],"{\"format\":\"htkk-control14-oracle-v1\",\"runtime\":\"clr2-x86\",\"primitiveOnly\":true,\"cases\":["+String.Join(",",records.ToArray())+"]}",new UTF8Encoding(false));return 0;
 }catch{return 5;}}
}
