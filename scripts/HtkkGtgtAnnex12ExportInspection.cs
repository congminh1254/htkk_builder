// Own fixed synthetic ORIGINAL annex export observation. No tax XML is authored.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Net;
using System.Reflection;
using System.Text;
using System.Windows.Forms;
using System.Xml;
using System.Xml.Schema;
public sealed partial class HtkkGuiReferenceAutomation {
 private bool annex12ExportMainZeroMatched=false,annex12ExportShapeMatched=false,annex12ExportSchemaVerified=false;
 // Separate nonzero ORIGINAL export probe: parent 1 at 50/50, then parent 7 at 33.33/66.67.
 private bool annex12NonzeroEditsMatched=false,annex12NonzeroSecondShapeMatched=false,annex12NonzeroSecondSchemaVerified=false;
 private int annex12NonzeroExportCount=0,annex12NonzeroSecondExportBytes=0;private string annex12NonzeroSecondExportSha256="";
 // Fixed web annex cases: original import observations and pinned XSD checks of native files.
 private bool annex12WebImportSheetMatched=false,annex12WebBaselineSchemaVerified=false,annex12WebReexportSchemaVerified=false;
 private int annex12WebImportGroupCount=0,annex12WebImportRowCount=0,annex12WebImportDisplayEmptyMask=0;
 private bool annex12NonzeroBusy=false;private Control annex12ExportGrid=null;private object annex12ExportSheet=null;
 private string Annex12ExportJson(){
  string q=((char)34).ToString();StringBuilder json=new StringBuilder();
  string[] names=new string[]{"annex12ExportMainZeroMatched","annex12ExportShapeMatched","annex12ExportSchemaVerified","annex12NonzeroEditsMatched","annex12NonzeroSecondShapeMatched","annex12NonzeroSecondSchemaVerified","annex12WebImportSheetMatched","annex12WebBaselineSchemaVerified","annex12WebReexportSchemaVerified"};
  bool[] flags=new bool[]{annex12ExportMainZeroMatched,annex12ExportShapeMatched,annex12ExportSchemaVerified,annex12NonzeroEditsMatched,annex12NonzeroSecondShapeMatched,annex12NonzeroSecondSchemaVerified,annex12WebImportSheetMatched,annex12WebBaselineSchemaVerified,annex12WebReexportSchemaVerified};
  for(int index=0;index<names.Length;index++)json.Append(","+q+names[index]+q+":"+Bool(flags[index]));
  names=new string[]{"annex12NonzeroExportCount","annex12NonzeroSecondExportBytes","annex12WebImportGroupCount","annex12WebImportRowCount","annex12WebImportDisplayEmptyMask"};
  int[] counts=new int[]{annex12NonzeroExportCount,annex12NonzeroSecondExportBytes,annex12WebImportGroupCount,annex12WebImportRowCount,annex12WebImportDisplayEmptyMask};
  for(int index=0;index<names.Length;index++)json.Append(","+q+names[index]+q+":"+counts[index].ToString(CultureInfo.InvariantCulture));
  json.Append(","+q+"annex12NonzeroSecondExportSha256"+q+":"+q+annex12NonzeroSecondExportSha256+q);return json.ToString();
 }
 private void StartOriginalAnnex12Export(Control grid,object annex){
  Annex12InputOwner(grid,annex);bool nonzero=mode=="gtgt-annex12-export-nonzero",web=Annex12WebCase();
  if((mode!="gtgt-annex12-export-inspect"&&!nonzero&&!web)||exportStarted||annex12InputActionCount!=14||!annex12InputReadOnlyIdentityMatched||!annex12InputIdentityMatched||!annex12InputTypesMatched||!annex12InputGeographyMatched||!annex12InputTaxAuthoritiesMatched||!annex12InputPercentagesMatched||!annex12InputZeroTaxMatched)throw new InvalidOperationException();
  if(nonzero){
   // Snapshot A: fixed fake parent 1 with the source 50/50 split, original editor only.
   if(annex12NumericActionCount!=0)throw new InvalidOperationException();EditAnnex12Numeric(grid,annex,0);
   if(!Annex12NumberMatched(annex,42,19,1)||!Annex12NumberMatched(annex,43,20,50)||!Annex12NumberMatched(annex,44,20,50)||!Annex12NumberMatched(annex,42,20,100))throw new InvalidOperationException();
  }
  annex12ExportGrid=grid;annex12ExportSheet=annex;
  object sheets=Get(grid,"Sheets");if(Convert.ToInt32(Get(sheets,"Count"))!=11)throw new InvalidOperationException();PropertyInfo item=sheets.GetType().GetProperty("Item",new Type[]{typeof(int)});if(item==null)throw new InvalidOperationException();object main=item.GetValue(sheets,new object[]{0});
  if(Convert.ToInt32(Get(main,"RowCount"))!=72||Convert.ToInt32(Get(main,"ColumnCount"))!=24||CellText(main,9,3)!=FakeName||CellText(main,10,3).Replace("-",String.Empty)!=Mst||CellText(main,63,10)!=FakeSigner||Selected(Get(Cell(main,35,8),"Value"))||!Convert.ToBoolean(Get(main,"AutoCalculation")))throw new InvalidOperationException();
  InspectMoneyZero(main);InspectCaseMoney(main);
  // Main sheet equals the fixed case vector: 27 zeros, or the sale10 vector when plant tax is entered (Header!B66).
  annex12ExportMainZeroMatched=(Annex12SaleMain()?gtgtCaseNonzeroMask==10727808:gtgtZero&&gtgtCaseNonzeroMask==0)&&gtgtEmptyMoney==0&&gtgtCaseMoneyMatched&&gtgtCaseMoneyCount==27&&gtgtCaseMismatchMask==0;
  if(!annex12ExportMainZeroMatched)throw new InvalidOperationException();SetStage(HtkkAutomationStage.GtgtAnnex12ExportMainChecked);Record();StartOriginalGtgtExport(grid.FindForm());
 }
 private sealed class Annex12PinnedSchemaResolver : XmlResolver {
  private readonly Dictionary<string,string> files=new Dictionary<string,string>(StringComparer.OrdinalIgnoreCase);
  public Annex12PinnedSchemaResolver(string root){
   files.Add(Path.GetFullPath(Path.Combine(root,"Validate/01_GTGT_TT80_283.xsd")),"8d4c0d88100e858ddfe221d080a6a338776d1364c7de04347bfb990d04833003");
   files.Add(Path.GetFullPath(Path.Combine(root,"TKhaiThue.xsd")),"8f451719355b5a6247f65a34a37584b4a0c7f7cc81a568e1033d08b8fe9b8c1d");
   files.Add(Path.GetFullPath(Path.Combine(root,"xmldsig-core-schema.xsd")),"c3b5160be1852606d10f6928e0b214d418f8dd418667cb2fb88fec31e4e6f56d");
   foreach(string path in files.Keys)Check(path);
  }
  private void Check(string path){
   if(!files.ContainsKey(path))throw new InvalidOperationException();FileInfo file=new FileInfo(path);
   if(!file.Exists||file.Length<1||file.Length>2097152||(file.Attributes&FileAttributes.ReparsePoint)!=0||Hash(path)!=files[path])throw new InvalidOperationException();
   for(DirectoryInfo directory=file.Directory;directory!=null;directory=directory.Parent)if((directory.Attributes&FileAttributes.ReparsePoint)!=0)throw new InvalidOperationException();
  }
  public override ICredentials Credentials {set{if(value!=null)throw new InvalidOperationException();}}
  public override object GetEntity(Uri absoluteUri,string role,Type type){
   if(absoluteUri==null||!absoluteUri.IsAbsoluteUri||!absoluteUri.IsFile||absoluteUri.IsUnc||!String.IsNullOrEmpty(absoluteUri.Host)||!String.IsNullOrEmpty(absoluteUri.Query)||!String.IsNullOrEmpty(absoluteUri.Fragment)||(type!=null&&type!=typeof(Stream)))throw new InvalidOperationException();
   string path=Path.GetFullPath(absoluteUri.LocalPath);Check(path);return new FileStream(path,FileMode.Open,FileAccess.Read,FileShare.Read);
  }
 }
 private bool Annex12XmlShape(string path,int groups,int rows,int leaves){
  XmlDocument document=ReadBoundedOriginalXml(path);XmlNamespaceManager ns=new XmlNamespaceManager(document.NameTable);ns.AddNamespace("t","http://kekhaithue.gdt.gov.vn/TKhaiThue");
  XmlNodeList plucs=document.SelectNodes("/t:HSoThueDTu/t:HSoKhaiThue/t:PLuc",ns),found=document.SelectNodes("/t:HSoThueDTu/t:HSoKhaiThue/t:PLuc/t:PLuc_01_2_GTGT/t:TenNhaMay",ns),children=document.SelectNodes("/t:HSoThueDTu/t:HSoKhaiThue/t:PLuc/t:PLuc_01_2_GTGT/t:TenNhaMay/t:DiaBanPhanBo",ns);
  int count=0;foreach(XmlNode node in document.SelectNodes("//*[not(*)]"))count++;
  return plucs.Count==1&&plucs[0].ChildNodes.Count==1&&found.Count==groups&&children.Count==rows&&count==leaves;
 }
 private bool Annex12XmlSchemaValid(string path){
  // Pinned local schemas only: no network, UNC, instance schemaLocation or DTD.
  string root=Path.Combine(Path.GetDirectoryName(project),"InterfaceTemplates"),schema=Path.Combine(root,"Validate/01_GTGT_TT80_283.xsd");Annex12PinnedSchemaResolver resolver=new Annex12PinnedSchemaResolver(root);
  XmlSchemaSet schemas=new XmlSchemaSet();schemas.XmlResolver=resolver;bool valid=true;schemas.ValidationEventHandler+=delegate(object sender,ValidationEventArgs args){valid=false;};
  XmlReaderSettings safe=new XmlReaderSettings();safe.ProhibitDtd=true;safe.XmlResolver=null;
  using(XmlReader reader=XmlReader.Create(schema,safe))schemas.Add(null,reader);schemas.Compile();if(!valid)return false;
  XmlReaderSettings check=new XmlReaderSettings();check.ProhibitDtd=true;check.XmlResolver=null;check.ValidationType=ValidationType.Schema;check.Schemas=schemas;check.ValidationFlags=XmlSchemaValidationFlags.ProcessIdentityConstraints|XmlSchemaValidationFlags.AllowXmlAttributes;check.ValidationEventHandler+=delegate(object sender,ValidationEventArgs args){valid=false;};
  using(XmlReader reader=XmlReader.Create(path,check)){while(reader.Read()){} }
  return valid;
 }
 private void ValidateOriginalAnnex12Export(){
  if((mode!="gtgt-annex12-export-inspect"&&mode!="gtgt-annex12-export-nonzero")||!annex12ExportMainZeroMatched||!exportSchemaPinnedVerified||!exportFileExists||!exportSyntheticIdentityMatched||exportBytes<1||exportBytes>262144||Hash(exportPath)!=exportSha256)throw new InvalidOperationException();
  SetStage(HtkkAutomationStage.GtgtAnnex12ExportValidating);Record();
  annex12ExportShapeMatched=Annex12XmlShape(exportPath,1,2,112);
  if(!annex12ExportShapeMatched)throw new InvalidOperationException();
  annex12ExportSchemaVerified=Annex12XmlSchemaValid(exportPath)&&Hash(exportPath)==exportSha256;if(!annex12ExportSchemaVerified)throw new InvalidOperationException();Record();
 }
 private void ValidateOriginalAnnex12NonzeroSecondExport(){
  if(mode!="gtgt-annex12-export-nonzero"||roundtripPhase!="annex12-nonzero-reexporting"||!annex12NonzeroEditsMatched||!annex12ExportSchemaVerified||!exportFileExists||!exportSyntheticIdentityMatched||exportBytes<1||exportBytes>262144||Hash(exportPath)!=exportSha256||String.Equals(exportPath,firstExportPath,StringComparison.OrdinalIgnoreCase))throw new InvalidOperationException();
  SetStage(HtkkAutomationStage.GtgtAnnex12ExportValidating);Record();
  annex12NonzeroSecondShapeMatched=Annex12XmlShape(exportPath,1,2,112);if(!annex12NonzeroSecondShapeMatched)throw new InvalidOperationException();
  annex12NonzeroSecondSchemaVerified=Annex12XmlSchemaValid(exportPath)&&Hash(exportPath)==exportSha256;if(!annex12NonzeroSecondSchemaVerified)throw new InvalidOperationException();Record();
 }
 // Baseline is the proven one-plant zero annex. The reexport carries the
 // imported case: one plant/2 rows/112 leaves or two plants/5 rows/163 leaves.
 private void ValidateOriginalAnnex12WebExport(bool baseline){
  if(!Annex12WebCase()||!annex12ExportMainZeroMatched||!exportSchemaPinnedVerified||!exportFileExists||!exportSyntheticIdentityMatched||exportBytes<1||exportBytes>262144||Hash(exportPath)!=exportSha256)throw new InvalidOperationException();
  SetStage(HtkkAutomationStage.GtgtAnnex12WebSchemaValidating);Record();bool two=!baseline&&Annex12WebTwoPlantsCase();
  bool valid=Annex12XmlShape(exportPath,two?2:1,two?5:2,two?163:112)&&Annex12XmlSchemaValid(exportPath)&&Hash(exportPath)==exportSha256;
  if(baseline){annex12WebBaselineSchemaVerified=valid;Record();if(!valid)throw new InvalidOperationException();}
  else{annex12WebReexportSchemaVerified=valid;Record();}
 }
 private void ContinueOriginalAnnex12Nonzero(){
  if(mode!="gtgt-annex12-export-nonzero"||roundtripPhase!="annex12-nonzero-editing"||annex12NonzeroExportCount!=1||!exportSuccessAcknowledged||!annex12ExportSchemaVerified||String.IsNullOrEmpty(firstExportPath)||Hash(firstExportPath)!=firstExportSha256||annex12ExportGrid==null||annex12ExportSheet==null)throw new InvalidOperationException();
  if(!OriginalRoundtripOwnerReady())return;
  Control grid=annex12ExportGrid;object annex=annex12ExportSheet;if(grid.FindForm()!=roundtripOwner)throw new InvalidOperationException();
  annex12NonzeroBusy=true;exportWatcher.Stop();
  try{
   object sheets=Get(grid,"Sheets");if(Convert.ToInt32(Get(sheets,"Count"))!=11)throw new InvalidOperationException();PropertyInfo item=sheets.GetType().GetProperty("Item",new Type[]{typeof(int)});if(item==null)throw new InvalidOperationException();
   if(Get(grid,"ActiveSheet")!=annex){
    // Same public vendor sheet selection used by the proven annex inspection.
    int found=-1;for(int index=0;index<11;index++)if(item.GetValue(sheets,new object[]{index})==annex){if(found>=0)throw new InvalidOperationException();found=index;}
    PropertyInfo active=grid.GetType().GetProperty("ActiveSheetIndex");if(found<0||active==null||!active.CanWrite)throw new InvalidOperationException();active.SetValue(grid,found,null);
    if(Get(grid,"ActiveSheet")!=annex||OriginalMessageVisible())throw new InvalidOperationException();
   }
   SetStage(HtkkAutomationStage.GtgtAnnex12NonzeroEditing);Record();
   // Snapshot B: parent 7 with 33.33/66.67 through the original numeric editor.
   EditAnnex12Numeric(grid,annex,1);EditAnnex12Numeric(grid,annex,2);EditAnnex12Numeric(grid,annex,3);
   annex12NonzeroEditsMatched=annex12NumericActionCount==4&&Annex12NumberMatched(annex,42,19,7)&&Annex12NumberMatched(annex,43,20,33.33m)&&Annex12NumberMatched(annex,44,20,66.67m)&&Annex12NumberMatched(annex,42,20,100);Record();
   if(!annex12NonzeroEditsMatched)throw new InvalidOperationException();
   object main=item.GetValue(sheets,new object[]{0});
   if(Convert.ToInt32(Get(main,"RowCount"))!=72||Convert.ToInt32(Get(main,"ColumnCount"))!=24||CellText(main,9,3)!=FakeName||CellText(main,10,3).Replace("-",String.Empty)!=Mst||CellText(main,63,10)!=FakeSigner||Selected(Get(Cell(main,35,8),"Value")))throw new InvalidOperationException();
   InspectMoneyZero(main);InspectCaseMoney(main);if(gtgtEmptyMoney!=0||!gtgtCaseMoneyMatched||gtgtCaseMoneyCount!=27||gtgtCaseMismatchMask!=0||gtgtCaseNonzeroMask!=10727808)throw new InvalidOperationException();
   exportPath=Path.Combine(Path.GetDirectoryName(firstExportPath),"01GTGT-p7.xml");if(File.Exists(exportPath))throw new InvalidOperationException();
   Button export=Named(roundtripOwner,"cmdExport") as Button;if(export==null||export.FindForm()!=roundtripOwner||export.Text.Replace("&",String.Empty).Trim()!="Kết xuất")throw new InvalidOperationException();
   exportButtonInvoked=false;exportDialogSubmitted=false;exportSuccessAcknowledged=false;roundtripPhase="annex12-nonzero-reexporting";SetStage(HtkkAutomationStage.GtgtAnnex12NonzeroReexportInvoking);Record();
   roundtripOwner.BeginInvoke(new MethodInvoker(delegate{try{export.PerformClick();}catch(Exception error){Failure(error);}}));
  }finally{annex12NonzeroBusy=false;if(!finished)exportWatcher.Start();}
 }
 private static bool Annex12CellLocked(object sheet,int row,int column){return Convert.ToBoolean(Get(Cell(sheet,row,column),"Locked"));}
 // Read-only observation after the ORIGINAL import control loaded the web annex.
 // Values/locks are read from original cells and table metadata; nothing is written.
 private bool InspectOriginalImportedAnnex12(Control grid){
  if(!Annex12WebCase())throw new InvalidOperationException();
  SetStage(HtkkAutomationStage.GtgtAnnex12WebImportChecking);annex12WebImportSheetMatched=false;annex12WebImportGroupCount=0;annex12WebImportRowCount=0;annex12WebImportDisplayEmptyMask=0;
  object sheets=Get(grid,"Sheets");int count=Convert.ToInt32(Get(sheets,"Count"));if(count!=11)return false;
  PropertyInfo item=sheets.GetType().GetProperty("Item",new Type[]{typeof(int)});if(item==null)return false;object annex=null;
  for(int index=0;index<count;index++){object candidate=item.GetValue(sheets,new object[]{index});string name=Convert.ToString(Get(candidate,"SheetName"),CultureInfo.InvariantCulture);if(name=="01_2"||name=="01-2/GTGT"){if(annex!=null)return false;annex=candidate;}}
  if(annex==null||Convert.ToInt32(Get(annex,"ColumnCount"))!=45)return false;
  bool two=Annex12WebTwoPlantsCase();
  string[] names=two?new string[]{"NHA MAY GIA LAP - KHONG NOP","NHA MAY GIA LAP 2 - KHONG NOP"}:new string[]{"NHA MAY GIA LAP - KHONG NOP"};
  string[] codes=two?new string[]{"9999999997-001","99997"}:new string[]{"9999999997-001"};
  decimal[] parents=two?new decimal[]{7m,3m}:new decimal[]{0m};
  decimal[][] percentages=two?new decimal[][]{new decimal[]{33.33m,66.67m},new decimal[]{50m,25m,25m}}:new decimal[][]{new decimal[]{50m,50m}};
  string[][] types=two?new string[][]{new string[]{"01","02"},new string[]{"01","02","02"}}:new string[][]{new string[]{"01","02"}};
  System.Collections.IList infos=Get(Global("ToKhaiInfo"),"SheetInfos") as System.Collections.IList;if(infos==null||infos.Count>32)return false;object info=null;
  foreach(object candidate in infos)if(candidate!=null&&Convert.ToString(Get(candidate,"SheetID"),CultureInfo.InvariantCulture)=="01_2"){if(info!=null)return false;info=candidate;}
  if(info==null||!Selected(Get(info,"Active")))return false;
  System.Collections.IList tables=Get(info,"Tables") as System.Collections.IList;if(tables==null||tables.Count!=names.Length)return false;
  int total=Convert.ToInt32(Get(annex,"RowCount")),seen=0;if(total<46||total>10000)return false;
  for(int i=0;i<tables.Count;i++){
   object table=tables[i];string id=(i+1).ToString(CultureInfo.InvariantCulture);
   if(Convert.ToString(Get(table,"TableName"),CultureInfo.InvariantCulture)!="01_2_GTGT"||Convert.ToString(Get(table,"TablePath"),CultureInfo.InvariantCulture)!="PLuc_01_2_GTGT/TenNhaMay"||Convert.ToString(Get(table,"TableID"),CultureInfo.InvariantCulture)!=id||Convert.ToString(Get(Get(table,"CellTableSTT"),"Value"),CultureInfo.InvariantCulture)!=id)return false;
   System.Collections.IList rows=Get(table,"RowsValues") as System.Collections.IList;if(rows==null||rows.Count!=percentages[i].Length)return false;
   int start=Convert.ToInt32(Get(Get(table,"Location"),"DataLocationTemplateRowStart"))-1,parent=start-1;if(parent<42||start+rows.Count>=total)return false;
   // Parent: name, MST and parent tax editable; percentage total and allocated total locked.
   if(CellText(annex,parent,1)!=id||CellText(annex,parent,4)!=names[i]||CellText(annex,parent,9)!=codes[i]||!Annex12NumberMatched(annex,parent,19,parents[i])||!Annex12NumberMatched(annex,parent,20,100))return false;
   if(Annex12CellLocked(annex,parent,4)||Annex12CellLocked(annex,parent,9)||Annex12CellLocked(annex,parent,19)||!Annex12CellLocked(annex,parent,20)||!Annex12CellLocked(annex,parent,23))return false;
   for(int j=0;j<rows.Count;j++){
    int row=start+j;
    // Observation only: which original display cells (type, province, ward, tax head,
    // local CQT) the import left blank. Five bits per child in document order.
    int[] display=new int[]{2,12,16,17,18};int ordinal=seen+j;
    for(int k=0;k<display.Length;k++)if(ordinal<5&&CellText(annex,row,display[k])==String.Empty)annex12WebImportDisplayEmptyMask|=1<<(ordinal*5+k);
    if(CellText(annex,row,1)!=id+"."+(j+1).ToString(CultureInfo.InvariantCulture)||CellText(annex,row,32)!=types[i][j]||CellText(annex,row,33)!="101"||CellText(annex,row,42)!="10129087"||CellText(annex,row,35)!="10100"||CellText(annex,row,36)!="10129"||CellText(annex,row,4)!=String.Empty||CellText(annex,row,9)!=String.Empty||!Annex12NumberMatched(annex,row,20,percentages[i][j]))return false;
    // Child: source-locked name/MST/amount and allocated tax; only the percentage is editable.
    if(!Annex12CellLocked(annex,row,4)||!Annex12CellLocked(annex,row,9)||!Annex12CellLocked(annex,row,19)||Annex12CellLocked(annex,row,20)||!Annex12CellLocked(annex,row,23))return false;
   }
   seen+=rows.Count;
  }
  annex12WebImportGroupCount=tables.Count;annex12WebImportRowCount=seen;annex12WebImportSheetMatched=true;Record();return true;
 }
}
