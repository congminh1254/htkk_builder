// Fixed synthetic shared Header binder probes. Never invokes Main/profile/file loading.
using System;
using System.IO;
using System.Reflection;
using System.Globalization;
using System.Collections;
using System.Collections.Generic;
using System.Text;
internal static class HtkkHeaderBindingOracle {
 static string project;
 static Assembly Resolve(object sender,ResolveEventArgs e){string n=new AssemblyName(e.Name).Name;if(n.IndexOfAny(new char[]{'/','\\',':'})>=0)return null;string p=Path.Combine(project,n+".dll");return File.Exists(p)?Assembly.LoadFrom(p):null;}
 static string Escape(string x){return x.Replace("\\","\\\\").Replace("\"","\\\"").Replace("\r","\\r").Replace("\n","\\n").Replace("\t","\\t");}
 static void Set(object target,string name,object value){target.GetType().GetProperty(name).SetValue(target,value,null);}
 static object Get(object target,string name){return target.GetType().GetProperty(name).GetValue(target,null);}
 static void Index(string cell,out int row,out int column){int i=0;column=0;while(i<cell.Length&&cell[i]>='A'&&cell[i]<='Z'){column=column*26+cell[i]-64;i++;}row=Int32.Parse(cell.Substring(i),CultureInfo.InvariantCulture)-1;column--;}
 static string Coordinate(string index){string[] parts=index.Split('_');int column=Int32.Parse(parts[0],CultureInfo.InvariantCulture),row=Int32.Parse(parts[1],CultureInfo.InvariantCulture);string letters="";while(column>0){int r=(column-1)%26;letters=(char)(65+r)+letters;column=(column-1)/26;}return letters+row.ToString(CultureInfo.InvariantCulture);}
 static string Probe(Assembly app,Type commonType,Type spreadType,Type sheetType,IDictionary dictionary,string taxId,int id){
  object common=Activator.CreateInstance(commonType),spread=Activator.CreateInstance(spreadType);try{
   foreach(PropertyInfo p in commonType.GetProperties()){if(p.CanWrite){if(p.PropertyType!=typeof(string))throw new InvalidOperationException("COMMON_INFO_TYPE");p.SetValue(common,"synthetic-"+p.Name,null);}}
   commonType.GetProperty("mst").SetValue(common,taxId,null);
   app.GetType("HTKK.WinSettings",true).GetField("TTinChung",BindingFlags.Public|BindingFlags.NonPublic|BindingFlags.Static).SetValue(null,common);
   object sheets=Get(spread,"Sheets");sheets.GetType().GetMethod("Clear",Type.EmptyTypes).Invoke(sheets,new object[0]);
   object first=Activator.CreateInstance(sheetType),header=Activator.CreateInstance(sheetType);Set(first,"SheetName","01");Set(first,"RowCount",100);Set(first,"ColumnCount",26);Set(header,"SheetName","Header");Set(header,"RowCount",100);Set(header,"ColumnCount",26);
   MethodInfo add=sheets.GetType().GetMethod("Add",new Type[]{sheetType});add.Invoke(sheets,new object[]{first});add.Invoke(sheets,new object[]{header});
   MethodInfo setValue=sheetType.GetMethod("SetValue",new Type[]{typeof(int),typeof(int),typeof(object)}),getValue=sheetType.GetMethod("GetValue",new Type[]{typeof(int),typeof(int)});
   List<string> cells=new List<string>();foreach(DictionaryEntry entry in dictionary){string index=(string)entry.Value;if(index.Length>0){string coordinate=Coordinate(index);if(!cells.Contains(coordinate))cells.Add(coordinate);}}
   for(int i=0;i<14;i++){string coordinate=((char)(67+i)).ToString()+"2";if(!cells.Contains(coordinate))cells.Add(coordinate);}
   cells.Sort(StringComparer.Ordinal);if(cells.Count!=67)throw new InvalidOperationException("HEADER_CELLS");
   foreach(string coordinate in cells){int row,column;Index(coordinate,out row,out column);setValue.Invoke(header,new object[]{row,column,"stale"});}
   // Original method's first string argument is unused in its pinned body. No
   // source profile path or form instance is supplied; only this synthetic spread.
   MethodInfo bind=app.GetType("HTKK.WinFnProcess",true).GetMethod("WinLoadTTinChungInfo",BindingFlags.Public|BindingFlags.Static);if(bind.MetadataToken!=0x060000ed)throw new InvalidOperationException("HEADER_METHOD");bind.Invoke(null,new object[]{"",spread});
   List<string> values=new List<string>();foreach(string coordinate in cells){int row,column;Index(coordinate,out row,out column);object v=getValue.Invoke(header,new object[]{row,column});string value=v==null?"":Convert.ToString(v,CultureInfo.InvariantCulture);values.Add("\""+coordinate+"\":{\"value\":\""+Escape(value)+"\",\"clrType\":\""+Escape(v==null?"null":v.GetType().FullName)+"\"}");}
   return "{\"id\":"+id+",\"taxId\":\""+taxId+"\",\"cells\":{"+String.Join(",",values.ToArray())+"}}";
  }finally{IDisposable d=spread as IDisposable;if(d!=null)d.Dispose();}
 }
 [STAThread]static int Main(string[] args){if(args.Length!=2)return 9;try{
  if(Environment.Version.Major!=2||IntPtr.Size!=4)return 3;project=Path.GetFullPath(args[0]);System.Threading.Thread.CurrentThread.CurrentCulture=CultureInfo.InvariantCulture;System.Threading.Thread.CurrentThread.CurrentUICulture=CultureInfo.InvariantCulture;AppDomain.CurrentDomain.AssemblyResolve+=Resolve;
  Assembly app=Assembly.LoadFrom(Path.Combine(project,"HTKK.exe")),utilities=Assembly.LoadFrom(Path.Combine(project,"TAX.HTKK.Utilities.dll")),farpoint=Assembly.LoadFrom(Path.Combine(project,"FarPoint.Win.Spread.dll"));
  Type commonType=utilities.GetType("TAX.HTKK.Utilities.Entity.HTKKCMCTTinChungInfo",true),spreadType=farpoint.GetType("FarPoint.Win.Spread.FpSpread",true),sheetType=farpoint.GetType("FarPoint.Win.Spread.SheetView",true);
  IDictionary dictionary=(IDictionary)app.GetType("HTKK.WinSettings",true).GetField("DictTTinChung",BindingFlags.Public|BindingFlags.NonPublic|BindingFlags.Static).GetValue(null);if(dictionary.Count!=60)return 6;
  string[] ids={"9999999997","9999999997001","999999999701","9999999997-001",""};List<string> records=new List<string>();for(int i=0;i<ids.Length;i++)records.Add(Probe(app,commonType,spreadType,sheetType,dictionary,ids[i],i+1));
  File.WriteAllText(args[1],"{\"format\":\"htkk-header-binding-oracle-v1\",\"runtime\":\"clr2-x86\",\"primitiveOnly\":true,\"cases\":["+String.Join(",",records.ToArray())+"]}",new UTF8Encoding(false));return 0;
 }catch{return 5;}}
}
