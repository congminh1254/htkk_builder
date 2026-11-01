// Fixed synthetic table-metadata operations only. No Main, profiles, tax amounts,
// XML, original source changes, or calls to private business-total helpers.
using System;
using System.IO;
using System.Reflection;
using System.Globalization;
using System.Collections;
using System.Collections.Generic;
using System.Text;
internal static class HtkkTableLifecycleOracle {
 static string project,stage="load";static Type sheetType,tableType,sheetInfoType;
 static string Category(Exception e){for(int i=0;i<8&&e.InnerException!=null;i++)e=e.InnerException;if(e is NullReferenceException)return "null-reference";if(e is ArgumentException)return "argument";if(e is InvalidOperationException)return "invalid-operation";if(e is TypeLoadException)return "type-load";if(e is FileNotFoundException)return "file-missing";return "other";}
 static object Get(object target,string property){return target.GetType().GetProperty(property).GetValue(target,null);}
 static void Set(object target,string property,object value){target.GetType().GetProperty(property).SetValue(target,value,null);}
 static Assembly Resolve(object sender,ResolveEventArgs e){string name=new AssemblyName(e.Name).Name;if(name.IndexOfAny(new char[]{'/','\\',':'})>=0)return null;string path=Path.Combine(project,name+".dll");return File.Exists(path)?Assembly.LoadFrom(path):null;}
 static string DigitText(object value){string text=Convert.ToString(value,CultureInfo.InvariantCulture);if(text.Length<1||text.Length>3)throw new InvalidOperationException();for(int i=0;i<text.Length;i++)if(text[i]<'0'||text[i]>'9')throw new InvalidOperationException();return text;}
 static int BoundedInt(object value,int min,int max){int number=Convert.ToInt32(value,CultureInfo.InvariantCulture);if(number<min||number>max)throw new InvalidOperationException();return number;}
 static object InitialTable(){
  object table=Activator.CreateInstance(tableType);Set(table,"TableID","1");Set(table,"TableName","SYNTHETIC");Set(table,"TablePath","Synthetic/Group");Set(table,"TableLength",2);Set(table,"iColumnSTT",1);Set(table,"iColumnSTTReport",1);
  object location=Get(table,"Location");Set(location,"TableTemplateRowStart",1);Set(location,"DataLocationTemplateRowStart",2);Set(location,"TableReportRowStart",1);Set(location,"DataLocationReportRowStart",2);Set(location,"DataLocationTaiBangKeRowStart",-1);
  object stt=Get(table,"CellTableSTT"),report=Get(table,"CellTableReportSTT");Set(stt,"RowIndex",1);Set(stt,"ColIndex",1);Set(stt,"Value","1");Set(report,"RowIndex",1);Set(report,"ColIndex",1);Set(report,"Value","1");
  Set(Get(table,"RowsInfo"),"RowDefaultDisplay","1");Set(Get(table,"RowsInfo"),"RowPath","SyntheticRow");
  // Structural-only fixture: no input/derived cell definitions or data rows.
  // Original InsertTable/RemoveTable calculate subsequent identities themselves.
  if(((IList)Get(table,"RowsValues")).Count!=0||((IList)Get(Get(table,"RowsInfo"),"Cells")).Count!=0||((IList)Get(Get(table,"Header"),"StaticCells")).Count!=0||((IList)Get(Get(table,"Footer"),"StaticCells")).Count!=0)throw new InvalidOperationException();
  return table;
 }
 static string Snapshot(object sheet,IList tables,int id,string operation,int index,int expectedCount){
  if(tables.Count!=expectedCount||tables.Count<1||tables.Count>8)throw new InvalidOperationException();List<string> records=new List<string>();
  foreach(object table in tables){
   object location=Get(table,"Location");if((string)Get(table,"TableName")!="SYNTHETIC")throw new InvalidOperationException();
   int rows=((IList)Get(table,"RowsValues")).Count;if(rows!=0)throw new InvalidOperationException();
   string tableId=DigitText(Get(table,"TableID")),stt=DigitText(Get(Get(table,"CellTableSTT"),"Value")),report=DigitText(Get(Get(table,"CellTableReportSTT"),"Value"));
   int start=BoundedInt(Get(location,"TableTemplateRowStart"),1,256),data=BoundedInt(Get(location,"DataLocationTemplateRowStart"),1,256);
   records.Add("{\"tableId\":\""+tableId+"\",\"stt\":\""+stt+"\",\"reportStt\":\""+report+"\",\"tableRowStart\":"+start+",\"dataRowStart\":"+data+",\"dataRows\":0}");
  }
  int sheetRows=BoundedInt(Get(sheet,"RowCount"),1,256);
  return "{\"id\":"+id+",\"operation\":\""+operation+"\",\"index\":"+index+",\"sheetRows\":"+sheetRows+",\"tables\":["+String.Join(",",records.ToArray())+"]}";
 }
 [STAThread]static int Main(string[] args){if(args.Length!=2)return 9;object sheet=null;try{
  if(Environment.Version.Major!=2||IntPtr.Size!=4)return 3;project=Path.GetFullPath(args[0]);CultureInfo culture=CultureInfo.InvariantCulture;System.Threading.Thread.CurrentThread.CurrentCulture=culture;System.Threading.Thread.CurrentThread.CurrentUICulture=culture;AppDomain.CurrentDomain.AssemblyResolve+=Resolve;
  Assembly app=Assembly.LoadFrom(Path.Combine(project,"HTKK.exe")),utility=Assembly.LoadFrom(Path.Combine(project,"TAX.HTKK.Utilities.dll")),spread=Assembly.LoadFrom(Path.Combine(project,"FarPoint.Win.Spread.dll"));
  sheetType=spread.GetType("FarPoint.Win.Spread.SheetView",true);tableType=utility.GetType("TAX.HTKK.Utilities.Entity.HTKKCMCTableInfo",true);sheetInfoType=utility.GetType("TAX.HTKK.Utilities.Entity.HTKKCMCSheetInfo",true);
  Type process=app.GetType("HTKK.WinSpreadProcess",true);Type[] signature=new Type[]{sheetType,typeof(int),sheetInfoType};MethodInfo insert=process.GetMethod("InsertTable",BindingFlags.Public|BindingFlags.Static,null,signature,null),remove=process.GetMethod("RemoveTable",BindingFlags.Public|BindingFlags.Static,null,signature,null);
  if(insert==null||remove==null||insert.MetadataToken!=0x060001fd||remove.MetadataToken!=0x060001fa)return 4;
  // A fixed caller-context input, never a calculated result or supplier setting.
  app.GetType("HTKK.WinSettings",true).GetField("MenuID",BindingFlags.Public|BindingFlags.NonPublic|BindingFlags.Static).SetValue(null,"D1");
  stage="initial-table";sheet=Activator.CreateInstance(sheetType);Set(sheet,"RowCount",128);Set(sheet,"ColumnCount",8);object info=Activator.CreateInstance(sheetInfoType);IList tables=(IList)Get(info,"Tables");tables.Add(InitialTable());
  List<string> observations=new List<string>();observations.Add(Snapshot(sheet,tables,1,"initial",-1,1));
  string[] operations={"insert","insert","insert","remove","insert","remove","remove","insert"};int[] indices={0,0,1,1,0,0,2,1},counts={2,3,4,3,4,3,2,3};
  for(int i=0;i<operations.Length;i++){MethodInfo method=operations[i]=="insert"?insert:remove;stage="step"+(i+1);method.Invoke(null,new object[]{sheet,indices[i],info});tables=(IList)Get(info,"Tables");observations.Add(Snapshot(sheet,tables,i+2,operations[i],indices[i],counts[i]));}
  string json="{\"format\":\"htkk-table-lifecycle-oracle-v1\",\"runtime\":\"clr2-x86\",\"menu\":\"D1\",\"fixture\":\"synthetic-zero-data-rows-with-stt\",\"primitiveOnly\":true,\"originalMainInvoked\":false,\"realTaxpayerDataUsed\":false,\"computedTotalsWritten\":false,\"xmlAuthored\":false,\"nativeQualified\":false,\"filingEnabled\":false,\"cases\":["+String.Join(",",observations.ToArray())+"]}";
  File.WriteAllText(args[1],json,new UTF8Encoding(false));return 0;
 }catch(Exception e){try{File.WriteAllText(args[1],"{\"format\":\"htkk-table-lifecycle-oracle-failure-v1\",\"stage\":\""+stage+"\",\"category\":\""+Category(e)+"\"}",new UTF8Encoding(false));return 0;}catch{return 5;}}finally{IDisposable disposable=sheet as IDisposable;if(disposable!=null)disposable.Dispose();}}
}
