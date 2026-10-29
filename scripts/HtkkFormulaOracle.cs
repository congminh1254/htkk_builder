// Fixed synthetic primitive probes only. No taxpayer input, XML, application events or vendor modifications.
using System;
using System.IO;
using System.Reflection;
using System.Globalization;
using System.Text;
using System.Collections.Generic;
internal static class HtkkFormulaOracle {
 static string project;static Type sheetType;
 static Assembly Resolve(object sender,ResolveEventArgs e){string n=new AssemblyName(e.Name).Name;if(n.IndexOfAny(new char[]{'/','\\',':'})>=0)return null;string p=Path.Combine(project,n+".dll");return File.Exists(p)?Assembly.LoadFrom(p):null;}
 static string Escape(string x){return x.Replace("\\","\\\\").Replace("\"","\\\"").Replace("\r","\\r").Replace("\n","\\n").Replace("\t","\\t");}
 static object Call(object s,string method,Type[] types,object[] args){return sheetType.GetMethod(method,types).Invoke(s,args);}
 static object Sheet(){object s=Activator.CreateInstance(sheetType);sheetType.GetProperty("RowCount").SetValue(s,32,null);sheetType.GetProperty("ColumnCount").SetValue(s,8,null);return s;}
 static void Set(object s,int row,object v){Call(s,"SetValue",new Type[]{typeof(int),typeof(int),typeof(object)},new object[]{row,0,v});}
 static string Probe(string f,string mode){object s=Sheet();try{
  if(mode=="numeric"){Set(s,0,10.0);Set(s,1,-5.0);Set(s,2,0.0);Set(s,3,25.0);}
  if(mode=="mixed"){Set(s,0,1.0);Set(s,1,"01");Set(s,2,true);Set(s,3,null);Set(s,4,"");Set(s,5,"abc");}
  Call(s,"SetFormula",new Type[]{typeof(int),typeof(int),typeof(string)},new object[]{10,2,f});Call(s,"RecalculateAll",Type.EmptyTypes,new object[0]);object v=Call(s,"GetValue",new Type[]{typeof(int),typeof(int)},new object[]{10,2});string kind=v==null?"blank":v is bool?"boolean":v is string?"text":v is double||v is int||v is decimal?"number":"error";string val=v==null?"":Convert.ToString(v,CultureInfo.InvariantCulture);return "{\"kind\":\""+kind+"\",\"value\":\""+Escape(val)+"\",\"clrType\":\""+Escape(v==null?"null":v.GetType().FullName)+"\"}";
 }finally{IDisposable d=s as IDisposable;if(d!=null)d.Dispose();}}
 [STAThread]static int Main(string[] a){if(a.Length!=2)return 9;try{if(Environment.Version.Major!=2||IntPtr.Size!=4)return 3;project=Path.GetFullPath(a[0]);CultureInfo ci=CultureInfo.InvariantCulture;System.Threading.Thread.CurrentThread.CurrentCulture=ci;System.Threading.Thread.CurrentThread.CurrentUICulture=ci;AppDomain.CurrentDomain.AssemblyResolve+=Resolve;Assembly spread=Assembly.LoadFrom(Path.Combine(project,"FarPoint.Win.Spread.dll"));sheetType=spread.GetType("FarPoint.Win.Spread.SheetView",true);
 string[] formulas={"1+2","0.1+0.2","1/3*3","ROUND(1.005,2)","ROUND(-1.005,2)","ROUND(-150,-2)","ROUND(2.5,0)","ROUNDUP(-1.21,1)","ROUNDDOWN(-1.29,1)","INT(-3.2)","MOD(-10,3)","ABS(-2)","IF(TRUE,7,1/0)","IF(FALSE,1/0,8)","IFERROR(1/0,9)","ISERROR(1/0)","ISBLANK(A4)","AND(TRUE,1)","OR(FALSE,0)","NOT(0)","SUM(A1:A4)","MIN(A1:A4)","MAX(A1:A4)","TRIM(\"  Họ   tên  \")","LEFT(\"0123\",2)","RIGHT(\"0123\",0)","MID(\"012345\",3,2)","LEN(\"Hỗ trợ kê khai\")","DATE(1900,1,1)","DATE(1900,2,29)","DATE(1900,3,1)","DATE(2026,2,31)","DATE(2026,13,1)","DATE(26,1,1)","DAY(60)","MONTH(60)","YEAR(60)","YEAR(0)","DAY(0)","A1=TRUE","A4=0","A4=\"\"","SUM(1,TRUE,\"2\")","COUNTIF(A1:A6,\"01\")","COUNTIF(A1:A6,TRUE)","COUNTIF(A1:A6,0)","COUNTIF(A1:A6,\"<>0\")","COUNTIF(A1:A6,\"*\")","COUNTIF(A1:A6,\"?\")","COUNTIF(A1:A6,\"a*\")","LEFT(\"abc\",1.9)","MID(\"abc\",1.9,1.9)","ROUND(1.5,0.9)","1/0"};
 List<string> records=new List<string>();for(int i=0;i<formulas.Length;i++){string mode=i>=39?"mixed":"numeric";records.Add("{\"id\":"+(i+1)+",\"formula\":\""+Escape(formulas[i])+"\",\"fixture\":\""+mode+"\",\"result\":"+Probe(formulas[i],mode)+"}");}File.WriteAllText(a[1],"{\"format\":\"htkk-formula-oracle-v1\",\"runtime\":\"clr2-x86\",\"primitiveOnly\":true,\"cases\":["+String.Join(",",records.ToArray())+"]}",new UTF8Encoding(false));return 0;
 }catch{return 5;}}
}
