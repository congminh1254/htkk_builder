// Own fixed synthetic ORIGINAL annex export observation. No tax XML is authored.
using System;
using System.Collections.Generic;
using System.Diagnostics;
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
 // Original import leaves R (head CQT display, pathCucThue: not an XML leaf) blank; Header row 83
 // makes R44 mandatory (0016). Restored only through the original combo editor.
 private bool annex12WebHeadAuthorityRestored=false;private int annex12WebHeadAuthorityRepairCount=0;
 // Bounded diagnostic: bits 0-5 unmet R/S/AJ/AK/AH/AQ checks, bits 6-8 child ordinal+1, bit 9 R combo
 // failed, bit 10 S combo failed, bit 11 the percentage editor was opened to leave the row.
 private int annex12WebHeadAuthorityFailureMask=0;
 private int annex12WebHeadAuthorityComboMask=0;
 // Bounded diagnostic of the R list at the FIRST head-CQT pick of the latest row (run 44122393792, case 24: failure mask 2752 =
 // 2048|512|ordinal 3, the first Bắc Ninh row's first R pick threw; the public catalogue names 22100 AND 22300 "Thuế thành phố
 // Bắc Ninh", as every merged tỉnh's head CQT, while "Thuế Thành phố Hà Nội" is unique). Bits 0/1/2: the head text is 0, 1, 2+
 // times in R's Items; bit 3 R entered by a real key first (EnterCell installs the ward's list); after it bit 4 ItemData aligned,
 // bit 5/6 the text 1 / 2+ times, bit 7 exactly one entry has the text AND the head code; bit 8 the pick by that code was made.
 // Counts and flags only; no item text leaves the process.
 private int annex12WebHeadAuthorityListMask=0;
 private bool annex12NonzeroBusy=false;private Control annex12ExportGrid=null;private object annex12ExportSheet=null;
 private string Annex12ExportJson(){
  string q=((char)34).ToString();StringBuilder json=new StringBuilder();
  string[] names=new string[]{"annex12ExportMainZeroMatched","annex12ExportShapeMatched","annex12ExportSchemaVerified","annex12NonzeroEditsMatched","annex12NonzeroSecondShapeMatched","annex12NonzeroSecondSchemaVerified","annex12WebImportSheetMatched","annex12WebBaselineSchemaVerified","annex12WebReexportSchemaVerified","annex12WebHeadAuthorityRestored"};
  bool[] flags=new bool[]{annex12ExportMainZeroMatched,annex12ExportShapeMatched,annex12ExportSchemaVerified,annex12NonzeroEditsMatched,annex12NonzeroSecondShapeMatched,annex12NonzeroSecondSchemaVerified,annex12WebImportSheetMatched,annex12WebBaselineSchemaVerified,annex12WebReexportSchemaVerified,annex12WebHeadAuthorityRestored};
  for(int index=0;index<names.Length;index++)json.Append(","+q+names[index]+q+":"+Bool(flags[index]));
  names=new string[]{"annex12NonzeroExportCount","annex12NonzeroSecondExportBytes","annex12WebImportGroupCount","annex12WebImportRowCount","annex12WebImportDisplayEmptyMask","annex12WebHeadAuthorityRepairCount","annex12WebHeadAuthorityFailureMask","annex12WebHeadAuthorityComboMask","annex12WebHeadAuthorityListMask"};
  int[] counts=new int[]{annex12NonzeroExportCount,annex12NonzeroSecondExportBytes,annex12WebImportGroupCount,annex12WebImportRowCount,annex12WebImportDisplayEmptyMask,annex12WebHeadAuthorityRepairCount,annex12WebHeadAuthorityFailureMask,annex12WebHeadAuthorityComboMask,annex12WebHeadAuthorityListMask};
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
  if(!Annex12WebCase()&&!KhbsAnnexCase())throw new InvalidOperationException();
  SetStage(HtkkAutomationStage.GtgtAnnex12WebImportChecking);annex12WebImportSheetMatched=false;annex12WebImportGroupCount=0;annex12WebImportRowCount=0;if(!annex12WebHeadAuthorityRestored)annex12WebImportDisplayEmptyMask=0;
  object sheets=Get(grid,"Sheets");int count=Convert.ToInt32(Get(sheets,"Count"));if(count!=11)return false;
  PropertyInfo item=sheets.GetType().GetProperty("Item",new Type[]{typeof(int)});if(item==null)return false;object annex=null;
  for(int index=0;index<count;index++){object candidate=item.GetValue(sheets,new object[]{index});string name=Convert.ToString(Get(candidate,"SheetName"),CultureInfo.InvariantCulture);if(name=="01_2"||name=="01-2/GTGT"){if(annex!=null)return false;annex=candidate;}}
  if(annex==null||Convert.ToInt32(Get(annex,"ColumnCount"))!=45)return false;
  // The KHBS annex cases import exactly the two-plant web annex (case 5's B2: plant 1 at 40/60; cases 6-9's B2: their variant).
  bool two=Annex12WebTwoPlantsCase()||KhbsAnnexCase();
  string[] names=two?new string[]{"NHA MAY GIA LAP - KHONG NOP","NHA MAY GIA LAP 2 - KHONG NOP"}:new string[]{"NHA MAY GIA LAP - KHONG NOP"};
  string[] codes=two?new string[]{"9999999997-001","99997"}:new string[]{"9999999997-001"};
  decimal[] parents=two?new decimal[]{7m,3m}:new decimal[]{0m};
  decimal[][] percentages=two?new decimal[][]{KhbsAnnexCase()?KhbsAnnexFirstPlantPercentages():new decimal[]{33.33m,66.67m},new decimal[]{50m,25m,25m}}:new decimal[][]{new decimal[]{50m,50m}};
  string[][] types=two?new string[][]{new string[]{"01","02"},new string[]{"01","02","02"}}:new string[][]{new string[]{"01","02"}};
  string[][] wards=null;
  if(KhbsAnnexLan2Case()&&khbsRound==2&&KhbsAnnexWideCaseId(webCaseId)||webCaseId==KhbsAnnex12Lan1AddPlantCaseId&&!khbsC0Import)KhbsAnnexWideRound2(out names,out codes,out parents,out percentages,out types,out wards);
  if(KhbsAnnexRoundCase())KhbsAnnexRound(out names,out codes,out parents,out percentages,out types,out wards);
  // Case 24: the proven two-plant annex with plant 2's three rows in another tỉnh.
  if(webCaseId==KhbsAnnex12OtherProvinceCaseId){string w=Annex12FixedWard,b=Annex12OtherProvinceWard;wards=new string[][]{new string[]{w,w},new string[]{b,b,b}};}
  if(wards==null){wards=new string[types.Length][];for(int i=0;i<types.Length;i++){wards[i]=new string[types[i].Length];for(int j=0;j<wards[i].Length;j++)wards[i][j]=Annex12FixedWard;}}
  List<string> expectedWards=new List<string>();
  System.Collections.IList infos=Get(Global("ToKhaiInfo"),"SheetInfos") as System.Collections.IList;if(infos==null||infos.Count>32)return false;object info=null;
  foreach(object candidate in infos)if(candidate!=null&&Convert.ToString(Get(candidate,"SheetID"),CultureInfo.InvariantCulture)=="01_2"){if(info!=null)return false;info=candidate;}
  if(info==null||!Selected(Get(info,"Active")))return false;
  System.Collections.IList tables=Get(info,"Tables") as System.Collections.IList;if(tables==null||tables.Count!=names.Length)return false;
  int total=Convert.ToInt32(Get(annex,"RowCount")),seen=0;if(total<46||total>10000)return false;
  for(int i=0;i<wards.Length;i++)expectedWards.AddRange(wards[i]);if(expectedWards.Count>Annex12MaxRestoredRows)return false;
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
    // The mask keeps the state right after the original import, before any restoration.
    for(int k=0;k<display.Length;k++)if(!annex12WebHeadAuthorityRestored&&ordinal<5&&CellText(annex,row,display[k])==String.Empty)annex12WebImportDisplayEmptyMask|=1<<(ordinal*5+k);
    if(CellText(annex,row,1)!=id+"."+(j+1).ToString(CultureInfo.InvariantCulture)||CellText(annex,row,32)!=types[i][j]||CellText(annex,row,33)!=Annex12WardProvinceCode(wards[i][j])||CellText(annex,row,42)!=wards[i][j]||CellText(annex,row,35)!=Annex12WardHeadCode(wards[i][j])||CellText(annex,row,36)!=Annex12WardCqtCode(wards[i][j])||CellText(annex,row,4)!=String.Empty||CellText(annex,row,9)!=String.Empty||!Annex12NumberMatched(annex,row,20,percentages[i][j]))return false;
    // Child: source-locked name/MST/amount and allocated tax; only the percentage is editable.
    if(!Annex12CellLocked(annex,row,4)||!Annex12CellLocked(annex,row,9)||!Annex12CellLocked(annex,row,19)||Annex12CellLocked(annex,row,20)||!Annex12CellLocked(annex,row,23))return false;
   }
   seen+=rows.Count;
  }
  annex12ExpectedWards=expectedWards.ToArray();annex12WebImportGroupCount=tables.Count;annex12WebImportRowCount=seen;annex12WebImportSheetMatched=true;Record();return true;
 }
 // Fixed synthetic places of the annex cases (public HTKK 5.8.2 catalogues): the proven ward, and the second ward of the
 // KHBS two-places variant (same tỉnh and head CQT 10100, its own local CQT). Any other ward fails closed.
 private const string Annex12FixedWard="10129087",Annex12SecondWard="10131091";
 // Case 24's ward in ANOTHER tỉnh (Bắc Ninh): its head CQT is not the Hà Nội one, so the restore takes it from Annex12Places.
 private const string Annex12OtherProvinceWard="22117047";
 // What the case data of each fixed ward pins, as the public HTKK 5.8.2 catalogues name it (htkk_web data/htkk-taxpayer-profile.json:
 // Catalogue_Dia_Ban_Tinh_Moi.xml, Catalogue_Dia_Ban_Xa_Moi.xml, Catalogue_CQT_Dia_Ban.xml): ward, tỉnh code (AH), head CQT code (AJ,
 // which GetParentCodeFromChildCellInTable writes as the ward's first three digits + "00") and its display text (R: the cấp cục
 // entry loadCqtCapCucTheoDiaBanXa lists for the ward), local CQT code (AK) and display text (S). Display texts are copied exactly,
 // letter case included ("Thuế thành phố Bắc Ninh"); no code is written, every code is re-read from the original cells.
 private static readonly string[][] Annex12Places=new string[][]{
  new string[]{Annex12FixedWard,"101","10100","Thuế Thành phố Hà Nội","10129","Thuế cơ sở 16 Thành phố Hà Nội"},
  new string[]{Annex12SecondWard,"101","10100","Thuế Thành phố Hà Nội","10131","Thuế cơ sở 25 Thành phố Hà Nội"},
  new string[]{Annex12OtherProvinceWard,"221","22100","Thuế thành phố Bắc Ninh","22117","Thuế cơ sở 2 thành phố Bắc Ninh"}};
 private static string[] Annex12Place(string ward){foreach(string[] place in Annex12Places)if(place[0]==ward)return place;throw new InvalidOperationException();}
 private static string Annex12WardProvinceCode(string ward){return Annex12Place(ward)[1];}
 private static string Annex12WardHeadCode(string ward){return Annex12Place(ward)[2];}
 private static string Annex12WardHeadName(string ward){return Annex12Place(ward)[3];}
 // At most seven imported rows (case 6: 2+3+2); the failure mask keeps the 1-based ordinal in bits 6-8.
 private const int Annex12MaxRestoredRows=7;
 private string[] annex12ExpectedWards=new string[0];
 private static string Annex12WardCqtCode(string ward){return Annex12Place(ward)[4];}
 private static string Annex12WardCqtName(string ward){return Annex12Place(ward)[5];}
 private string Annex12ExpectedWard(int ordinal){if(ordinal<0||ordinal>=annex12ExpectedWards.Length)throw new InvalidOperationException();return annex12ExpectedWards[ordinal];}
 // Round 2 of the KHBS wider-scope cases 6-9: the B2 annex variant (htkk_annex12_web_cases VARIANTS), plants in document order.
 private void KhbsAnnexWideRound2(out string[] names,out string[] codes,out decimal[] parents,out decimal[][] percentages,out string[][] types,out string[][] wards){
  string n1="NHA MAY GIA LAP - KHONG NOP",n2="NHA MAY GIA LAP 2 - KHONG NOP",n3="NHA MAY GIA LAP 3 - KHONG NOP",w=Annex12FixedWard,v=Annex12SecondWard;
  decimal[] p1=new decimal[]{33.33m,66.67m},p2=new decimal[]{50m,25m,25m};string[] t1=new string[]{"01","02"},t2=new string[]{"01","02","02"};
  // Case 17's B1 carries the add-plant annex of case 6 (its C0 the proven two-plant annex).
  if(webCaseId==KhbsAnnex12AddPlantCaseId||webCaseId==KhbsAnnex12Lan1AddPlantCaseId){names=new string[]{n1,n2,n3};codes=new string[]{"9999999997-001","99997","99996"};parents=new decimal[]{7m,3m,5m};percentages=new decimal[][]{p1,p2,new decimal[]{60m,40m}};types=new string[][]{t1,t2,t1};wards=new string[][]{new string[]{w,w},new string[]{w,w,w},new string[]{w,w}};return;}
  if(webCaseId==KhbsAnnex12RemovePlantCaseId){names=new string[]{n1};codes=new string[]{"9999999997-001"};parents=new decimal[]{7m};percentages=new decimal[][]{p1};types=new string[][]{t1};wards=new string[][]{new string[]{w,w}};return;}
  if(webCaseId==KhbsAnnex12TwoPlacesCaseId){names=new string[]{n1,n2};codes=new string[]{"9999999997-001","99997"};parents=new decimal[]{7m,3m};percentages=new decimal[][]{p1,p2};types=new string[][]{t1,t2};wards=new string[][]{new string[]{w,w},new string[]{w,v,v}};return;}
  if(webCaseId==KhbsAnnex12EqualRowsCaseId){names=new string[]{n1,n2};codes=new string[]{"9999999997-001","99997"};parents=new decimal[]{7m,3m};percentages=new decimal[][]{new decimal[]{40m,60m},new decimal[]{50m,50m}};types=new string[][]{t1,t1};wards=new string[][]{new string[]{w,w},new string[]{w,w}};return;}
  if(webCaseId==KhbsAnnex12DisplaySameCaseId){names=new string[]{n1,n2};codes=new string[]{"9999999997-001","99997"};parents=new decimal[]{7m,3m};percentages=new decimal[][]{new decimal[]{35m,65m},p2};types=new string[][]{t1,t2};wards=new string[][]{new string[]{w,w},new string[]{w,w,w}};return;}
  // Cases 22-23 carry case 8's B2 annex.
  if(KhbsCt10AnnexCaseId(webCaseId)){names=new string[]{n1,n2};codes=new string[]{"9999999997-001","99997"};parents=new decimal[]{7m,4m};percentages=new decimal[][]{p1,p2};types=new string[][]{t1,t2};wards=new string[][]{new string[]{w,w},new string[]{w,w,w}};return;}
  throw new InvalidOperationException();
 }
 // Cases 14-15 (display-rounding captures): the B1 annex (case 14, and case 15's round 1) has plant 1 at [10] 3 and plant 2 at
 // [10] 5, each two rows 50/50 (types 01/02, the fixed ward); case 15's round 2 keeps plant 1 alone at [10] 8, rows 50/50.
 private void KhbsAnnexRound(out string[] names,out string[] codes,out decimal[] parents,out decimal[][] percentages,out string[][] types,out string[][] wards){
  string n1="NHA MAY GIA LAP - KHONG NOP",n2="NHA MAY GIA LAP 2 - KHONG NOP",w=Annex12FixedWard;decimal[] half=new decimal[]{50m,50m};string[] t1=new string[]{"01","02"};
  if(!KhbsAnnexRoundCase())throw new InvalidOperationException();
  if(webCaseId==KhbsAnnex12Lan2RoundCaseId&&khbsRound==2){names=new string[]{n1};codes=new string[]{"9999999997-001"};parents=new decimal[]{8m};percentages=new decimal[][]{half};types=new string[][]{t1};wards=new string[][]{new string[]{w,w}};return;}
  // Cases 19-20: three plants [10] 7/9/7 (the third is case 6's 99996), each two rows 50/50; case 20's round 2 keeps plant 1 at [10] 6.
  if(webCaseId==KhbsAnnex12Lan2NegRoundCaseId&&khbsRound==2){names=new string[]{n1};codes=new string[]{"9999999997-001"};parents=new decimal[]{6m};percentages=new decimal[][]{half};types=new string[][]{t1};wards=new string[][]{new string[]{w,w}};return;}
  if(khbsRound!=1)throw new InvalidOperationException();
  if(webCaseId==KhbsAnnex12Round3CaseId||webCaseId==KhbsAnnex12Lan2NegRoundCaseId){names=new string[]{n1,n2,"NHA MAY GIA LAP 3 - KHONG NOP"};codes=new string[]{"9999999997-001","99997","99996"};parents=new decimal[]{7m,9m,7m};percentages=new decimal[][]{half,half,half};types=new string[][]{t1,t1,t1};wards=new string[][]{new string[]{w,w},new string[]{w,w},new string[]{w,w}};return;}
  names=new string[]{n1,n2};codes=new string[]{"9999999997-001","99997"};parents=new decimal[]{3m,5m};percentages=new decimal[][]{half,half};types=new string[][]{t1,t1};wards=new string[][]{new string[]{w,w},new string[]{w,w}};
 }
 // Runs 42182681228/42182684607: after the ORIGINAL import every child R was blank (mask
 // 264 / 8659208) and the reexport was refused with 0016 (Header row 83: R44 required).
 // R is the parent-catalogue display of the imported child CQT; the XML carries only
 // ct09_cqt_ma/ten. Select the head CQT the case data pins for the row's ward (Annex12Places:
 // "Thuế Thành phố Hà Nội" for the Hà Nội wards, the Bắc Ninh one for case 24) through the original
 // combo editor, as a user must, then the same local CQT if the original change handler
 // cleared it. Codes are re-read, never written; the XML comparison stays exact.
 private void RestoreImportedAnnex12HeadAuthorities(){
  if((!Annex12WebCase()&&!KhbsAnnexCase())||annex12WebHeadAuthorityRestored||!roundtripImportSucceeded||!annex12WebImportSheetMatched)throw new InvalidOperationException();
  List<Control> grids=new List<Control>();int visited=0;GatherSpreads(roundtripOwner,grids,ref visited);if(grids.Count!=1)throw new InvalidOperationException();Control grid=grids[0];
  object sheets=Get(grid,"Sheets");if(Convert.ToInt32(Get(sheets,"Count"))!=11)throw new InvalidOperationException();PropertyInfo item=sheets.GetType().GetProperty("Item",new Type[]{typeof(int)});if(item==null)throw new InvalidOperationException();
  object annex=null;int found=-1;
  for(int index=0;index<11;index++){object candidate=item.GetValue(sheets,new object[]{index});string name=Convert.ToString(Get(candidate,"SheetName"),CultureInfo.InvariantCulture);if(name=="01_2"||name=="01-2/GTGT"){if(annex!=null)throw new InvalidOperationException();annex=candidate;found=index;}}
  if(annex==null)throw new InvalidOperationException();
  annex12NonzeroBusy=true;exportWatcher.Stop();
  try{
   if(Get(grid,"ActiveSheet")!=annex){PropertyInfo active=grid.GetType().GetProperty("ActiveSheetIndex");if(active==null||!active.CanWrite)throw new InvalidOperationException();active.SetValue(grid,found,null);}
   if(Get(grid,"ActiveSheet")!=annex||OriginalMessageVisible())throw new InvalidOperationException();
   SetStage(HtkkAutomationStage.GtgtAnnex12WebImportChecking);Record();
   System.Collections.IList infos=Get(Global("ToKhaiInfo"),"SheetInfos") as System.Collections.IList;object info=null;if(infos==null||infos.Count>32)throw new InvalidOperationException();
   foreach(object candidate in infos)if(candidate!=null&&Convert.ToString(Get(candidate,"SheetID"),CultureInfo.InvariantCulture)=="01_2"){if(info!=null)throw new InvalidOperationException();info=candidate;}
   System.Collections.IList tables=info==null?null:Get(info,"Tables") as System.Collections.IList;if(tables==null||tables.Count!=annex12WebImportGroupCount)throw new InvalidOperationException();
   int seen=0;
   for(int i=0;i<tables.Count;i++){
    System.Collections.IList rows=Get(tables[i],"RowsValues") as System.Collections.IList;if(rows==null||rows.Count<1||rows.Count>5)throw new InvalidOperationException();
    int start=Convert.ToInt32(Get(Get(tables[i],"Location"),"DataLocationTemplateRowStart"))-1;
    for(int j=0;j<rows.Count;j++){
     int row=start+j,ordinal=seen+j;if(ordinal>=Annex12MaxRestoredRows)throw new InvalidOperationException();string ward=Annex12ExpectedWard(ordinal),cqt=Annex12WardCqtName(ward),head=Annex12WardHeadName(ward),headCode=Annex12WardHeadCode(ward);
     annex12WebHeadAuthorityFailureMask=(annex12WebHeadAuthorityFailureMask&2048)|((ordinal+1)<<6);Record();
     if(CellText(annex,row,17)==String.Empty){
      try{SelectImportedAnnex12Head(grid,annex,row,head,headCode);}catch{annex12WebHeadAuthorityFailureMask|=512;Record();throw;}
      annex12WebHeadAuthorityRepairCount++;Record();
     }
     // Runs 42206910531/42206915586 stopped right after the second combo action: the original
     // handlers may act when the user leaves a cell, so move to S as a user does before reading it.
     MoveImportedAnnex12Cell(grid,annex,row,18);
     if(CellText(annex,row,18)!=cqt){
      try{SelectImportedAnnex12Combo(grid,annex,row,18,cqt);}catch{annex12WebHeadAuthorityFailureMask|=1024;Record();throw;}
      annex12WebHeadAuthorityRepairCount++;Record();
     }
     // Leave S for the child's percentage (the next field of the proven 14-input order), then wait
     // (bounded) for the original handlers. Only if they have not run, open and close the original
     // percentage editor without typing, exactly as a user tabbing through; its value must not change.
     MoveImportedAnnex12Cell(grid,annex,row,20);int unmet=WaitImportedAnnex12HeadAuthority(annex,row,ordinal,1.0);
     if(unmet!=0){annex12WebHeadAuthorityFailureMask|=2048;Record();PassImportedAnnex12Percentage(grid,annex,row);unmet=WaitImportedAnnex12HeadAuthority(annex,row,ordinal,2.0);}
     // frmWinToKhai.cellChange (ComboCloseUp/EditChange) writes the hidden code AJ of a table row only
     // from Cells[ActiveCell.Row, SelectedValue column] and only when the R cell text is non-empty when
     // the list closes; winFpSpread_ComboCloseUp skips cellChange while the cell is still empty. A
     // user whose first pick did not take re-opens the same list and confirms the same entry: do
     // exactly that once (R text unchanged), then S as before. Bounded shape of R's original combo
     // is recorded (annex12WebHeadAuthorityComboMask) so a remaining gap names its cause.
     // Release 216 (r1371) shape 107: combo type, items, text is an item and active row all held,
     // but ItemData was not aligned with Items, so GeneralFunctions.GetDMFromCombobox (the code
     // lookup cellChange uses for Controltype 8) found no code and AJ stayed empty. The ItemData
     // list (Keys = CQT codes) is installed only by frmWinToKhai.winFpSpread_EnterCell (Controltype
     // 8: loadCqtCapCucTheoDiaBanXa → GeneralFunctions.InsertCombobox(dictionary)), which the
     // vendor raises for a user's move into the cell, not for a programmatic SetActiveCell. Enter R
     // as a user does, with one real Left key from S, then re-confirm the same entry once.
     if((unmet&4)!=0&&CellText(annex,row,17)==head){
      annex12WebHeadAuthorityComboMask=ImportedAnnex12ComboShape(annex,row,17,head,headCode);Record();
      EnterImportedAnnex12HeadByKey(grid,annex,row);annex12WebHeadAuthorityComboMask|=256;
      int keyed=ImportedAnnex12ComboShape(annex,row,17,head,headCode);if((keyed&4)!=0)annex12WebHeadAuthorityComboMask|=512;if((keyed&16)!=0)annex12WebHeadAuthorityComboMask|=1024;Record();
      if(CellText(annex,row,17)!=head)throw new InvalidOperationException();
      // Release 222 (both cases, combo mask 1899 = 107|256|512|1024, still no 128): after the keyed
      // entry ItemData held code 10100, yet the same-entry re-confirm wrote nothing. Original
      // frmWinToKhai.cellChange (and winFpSpread_ComboSelChange) return early when the cell text
      // equals selectValueOld[row+col] (the last value they processed) for every menu except
      // 91/79/G1/G4/71/01; D1 is not exempt, so confirming the value already processed is a no-op.
      // A user then picks a neighbouring entry of the same original list and picks the head CQT
      // again: both are real changes, so the original handler runs and writes AJ from ItemData.
      try{SelectImportedAnnex12NeighbourEntry(grid,annex,row,17,head,headCode);SelectImportedAnnex12Combo(grid,annex,row,17,head,headCode);}catch{annex12WebHeadAuthorityFailureMask|=512;Record();throw;}
      annex12WebHeadAuthorityRepairCount++;annex12WebHeadAuthorityComboMask|=64;Record();
      MoveImportedAnnex12Cell(grid,annex,row,18);
      if(CellText(annex,row,18)!=cqt){
       try{SelectImportedAnnex12Combo(grid,annex,row,18,cqt);}catch{annex12WebHeadAuthorityFailureMask|=1024;Record();throw;}
       annex12WebHeadAuthorityRepairCount++;Record();
      }
      MoveImportedAnnex12Cell(grid,annex,row,20);unmet=WaitImportedAnnex12HeadAuthority(annex,row,ordinal,2.0);
      if((unmet&4)==0)annex12WebHeadAuthorityComboMask|=128;Record();
     }
     if(unmet!=0){annex12WebHeadAuthorityFailureMask|=unmet;Record();throw new InvalidOperationException();}
    }
    seen+=rows.Count;
   }
   if(seen!=annex12WebImportRowCount||annex12WebHeadAuthorityRepairCount<1||annex12WebHeadAuthorityRepairCount>4*seen)throw new InvalidOperationException();
   annex12WebHeadAuthorityFailureMask&=2048;annex12WebHeadAuthorityRestored=true;Record();
  }finally{annex12NonzeroBusy=false;if(!finished)exportWatcher.Start();}
 }
 // Picks the nearest other non-empty entry of the same original list (before ``value`` first, else
 // after it), through the same vendor combo selection; the caller then picks ``value`` again.
 // Releases 224/225 (both cases, failure mask 2624 = 2048|512|ordinal 1, combo mask 1835): the list
 // is GeneralFunctions.loadCqtCapCucTheoDiaBanXa's dictionary, whose first entry is the blank ''
 // (Add("","")), then the ward's head CQT, then the two nationwide CQTs 82500/82700. The entry before
 // the head CQT is that blank, which a user cannot use (winFpSpread_ComboCloseUp skips cellChange for
 // an empty cell), so the nearest non-empty entry after it is picked, as a user would.
 private void SelectImportedAnnex12NeighbourEntry(Control grid,object annex,int row,int column,string value,string code){
  if(column!=17)throw new InvalidOperationException();
  object type=Get(Cell(annex,row,column),"CellType");string[] items=type==null?null:Get(type,"Items") as string[];
  if(items==null||items.Length<2||items.Length>4096)throw new InvalidOperationException();
  int at=Array.IndexOf(items,value);if(at<0)throw new InvalidOperationException();
  // A text listed twice (merged tỉnh, case 24) is located by its ItemData code; a unique text as before.
  if(Array.LastIndexOf(items,value)!=at){at=Annex12CodedIndex(items,Get(type,"ItemData") as string[],value,code);if(at<0)throw new InvalidOperationException();}
  string neighbour=null;
  for(int step=1;step<items.Length&&neighbour==null;step++){
   foreach(int candidate in new int[]{at-step,at+step}){
    if(candidate<0||candidate>=items.Length)continue;string entry=items[candidate];
    if(!String.IsNullOrEmpty(entry)&&entry!=value&&Array.IndexOf(items,entry)==Array.LastIndexOf(items,entry)){neighbour=entry;break;}
   }
  }
  if(String.IsNullOrEmpty(neighbour)||neighbour==value)throw new InvalidOperationException();
  SelectImportedAnnex12Combo(grid,annex,row,column,neighbour);
 }
 private void SelectImportedAnnex12Combo(Control grid,object annex,int row,int column,string value){SelectImportedAnnex12Combo(grid,annex,row,column,value,null);}
 // The single index whose Items text is ``value`` and whose ItemData is ``code`` (ItemData aligned with Items), else -1.
 private static int Annex12CodedIndex(string[] items,string[] data,string value,string code){
  if(items==null||data==null||data.Length!=items.Length||String.IsNullOrEmpty(code))return -1;int found=-1;
  for(int index=0;index<items.Length;index++)if(items[index]==value&&data[index]==code){if(found>=0)return -1;found=index;}
  return found;
 }
 private static int Annex12ItemCount(string[] items,string value){int count=0;if(items!=null)foreach(string item in items)if(item==value)count++;return count;}
 // The FIRST pick of R (head CQT) of an imported row. A head text listed once in R's current Items (every Hà Nội row) is picked
 // exactly as before. Otherwise (absent, or a merged tỉnh's text listed twice) R is entered by one real Left key from S first
 // (EnterImportedAnnex12HeadByKey: winFpSpread_EnterCell installs the ward's list with ItemData), and a text still listed twice is
 // picked at the single entry whose ItemData is the head code the case data pins. Only original list entries are selected.
 private void SelectImportedAnnex12Head(Control grid,object annex,int row,string head,string headCode){
  object type=Get(Cell(annex,row,17),"CellType");int count=Annex12ItemCount(type==null?null:Get(type,"Items") as string[],head);
  annex12WebHeadAuthorityListMask=count==0?1:count==1?2:4;Record();
  if(count==1){SelectImportedAnnex12Combo(grid,annex,row,17,head);return;}
  EnterImportedAnnex12HeadByKey(grid,annex,row);annex12WebHeadAuthorityListMask|=8;
  type=Get(Cell(annex,row,17),"CellType");string[] items=type==null?null:Get(type,"Items") as string[];string[] data=type==null?null:Get(type,"ItemData") as string[];
  if(items!=null&&data!=null&&data.Length==items.Length)annex12WebHeadAuthorityListMask|=16;
  int keyed=Annex12ItemCount(items,head);if(keyed==1)annex12WebHeadAuthorityListMask|=32;else if(keyed>1)annex12WebHeadAuthorityListMask|=64;
  if(Annex12CodedIndex(items,data,head,headCode)>=0)annex12WebHeadAuthorityListMask|=128;Record();
  if(keyed==1){SelectImportedAnnex12Combo(grid,annex,row,17,head);return;}
  if(keyed<1||(annex12WebHeadAuthorityListMask&128)==0)throw new InvalidOperationException();
  annex12WebHeadAuthorityListMask|=256;Record();SelectImportedAnnex12Combo(grid,annex,row,17,head,headCode);
 }
 // ``code`` (head CQT only): when ``value`` is listed more than once, the entry whose ItemData is ``code``; null keeps the old rule
 // (exactly one entry with the text).
 private void SelectImportedAnnex12Combo(Control grid,object annex,int row,int column,string value,string code){
  Form owner=grid.FindForm();uint pid;
  if((column!=17&&column!=18)||owner==null||owner!=roundtripOwner||!owner.Visible||!owner.Enabled||!grid.Visible||!grid.Enabled||Get(grid,"ActiveSheet")!=annex||OriginalMessageVisible()||Annex12CellLocked(annex,row,column))throw new InvalidOperationException();
  grid.Focus();GetWindowThreadProcessId(GetForegroundWindow(),out pid);if(pid!=(uint)Process.GetCurrentProcess().Id||!grid.ContainsFocus)throw new InvalidOperationException();
  annex.GetType().GetMethod("SetActiveCell",new Type[]{typeof(int),typeof(int)}).Invoke(annex,new object[]{row,column});
  grid.GetType().GetMethod("StartCellEditing",new Type[]{typeof(EventArgs),typeof(bool)}).Invoke(grid,new object[]{EventArgs.Empty,false});
  Control editor=Get(grid,"EditingControl") as Control;if(editor==null||!editor.Visible||!editor.Enabled)throw new InvalidOperationException();
  // Same public vendor combo selection used by the proven 14-input scenario.
  Control vendor=FindVendorCombo(editor,0);if(vendor==null)throw new InvalidOperationException();editorKind="combo";SetPublic(vendor,"DroppedDown",true);
  object list=Get(vendor,"List");System.Collections.IList sequence=list as System.Collections.IList;int count=sequence!=null?sequence.Count:Convert.ToInt32(Get(list,"Count"));
  if(count<1||count>4096)throw new InvalidOperationException();PropertyInfo entryItem=list.GetType().GetProperty("Item",new Type[]{typeof(int)});if(entryItem==null&&sequence==null)throw new InvalidOperationException();int selected=-1;
  int matches=0;
  for(int offset=0;offset<count;offset++){object entry=sequence!=null?sequence[offset]:entryItem.GetValue(list,new object[]{offset});if(entry!=null&&entry.ToString()==value){if(selected<0)selected=offset;matches++;}}
  if(matches>1){
   // Only for a code-pinned head CQT: the vendor list must be the cell's Items (same count, same text at the index).
   object type=Get(Cell(annex,row,column),"CellType");string[] items=type==null?null:Get(type,"Items") as string[];
   if(code==null||column!=17||items==null||items.Length!=count)throw new InvalidOperationException();
   selected=Annex12CodedIndex(items,Get(type,"ItemData") as string[],value,code);
   if(selected<0)throw new InvalidOperationException();object chosen=sequence!=null?sequence[selected]:entryItem.GetValue(list,new object[]{selected});if(chosen==null||chosen.ToString()!=value)throw new InvalidOperationException();
  }
  if(selected<0)throw new InvalidOperationException();GetWindowThreadProcessId(GetForegroundWindow(),out pid);if(pid!=(uint)Process.GetCurrentProcess().Id||OriginalMessageVisible())throw new InvalidOperationException();
  SetPublic(vendor,"SelectedIndex",selected);SetPublic(vendor,"DroppedDown",false);
  grid.GetType().GetMethod("StopCellEditing",Type.EmptyTypes).Invoke(grid,null);Application.DoEvents();grid.Focus();
  if(CellText(annex,row,column)!=value||OriginalMessageVisible()||Get(grid,"ActiveSheet")!=annex)throw new InvalidOperationException();
 }

 // Read-only shape of the original combo cell: bit0 combobox cell type, bit1 items present, bit2
 // ItemData aligned with Items, bit3 the shown text is an item, bit4 its ItemData is the expected code,
 // bit5 the original active cell is this row. Counts and flags only; no item text leaves the process.
 // The caller adds bit6 re-confirm done, bit7 AJ written after it, bit8 R entered by a real key,
 // bit9/bit10 ItemData aligned / expected code present after that keyed entry.
 private int ImportedAnnex12ComboShape(object annex,int row,int column,string text,string code){
  int mask=0;object type=Get(Cell(annex,row,column),"CellType");
  if(type==null||type.GetType().FullName!="FarPoint.Win.Spread.CellType.ComboBoxCellType")return mask;mask|=1;
  string[] items=Get(type,"Items") as string[];string[] data=Get(type,"ItemData") as string[];
  if(items!=null&&items.Length>0&&items.Length<=4096)mask|=2;
  if(items!=null&&data!=null&&data.Length==items.Length)mask|=4;
  int at=items==null?-1:Array.IndexOf(items,text);if(at>=0)mask|=8;
  if(at>=0&&data!=null&&at<data.Length&&data[at]==code)mask|=16;
  if(Convert.ToInt32(Get(annex,"ActiveRowIndex"))==row)mask|=32;
  return mask;
 }
 private int ImportedAnnex12HeadAuthorityUnmet(object annex,int row,int ordinal){
  int unmet=0;string ward=Annex12ExpectedWard(ordinal);
  if(CellText(annex,row,17)!=Annex12WardHeadName(ward))unmet|=1;
  if(CellText(annex,row,18)!=Annex12WardCqtName(ward))unmet|=2;
  if(CellText(annex,row,35)!=Annex12WardHeadCode(ward))unmet|=4;
  if(CellText(annex,row,36)!=Annex12WardCqtCode(ward))unmet|=8;
  if(CellText(annex,row,33)!=Annex12WardProvinceCode(ward))unmet|=16;
  if(CellText(annex,row,42)!=ward)unmet|=32;
  return unmet;
 }
 private int WaitImportedAnnex12HeadAuthority(object annex,int row,int ordinal,double seconds){
  Stopwatch clock=Stopwatch.StartNew();int unmet;
  do{unmet=ImportedAnnex12HeadAuthorityUnmet(annex,row,ordinal);if(unmet==0||OriginalMessageVisible())return unmet;Application.DoEvents();System.Threading.Thread.Sleep(10);}while(clock.Elapsed.TotalSeconds<seconds);
  return ImportedAnnex12HeadAuthorityUnmet(annex,row,ordinal);
 }
 // Navigation only: the original active cell moves as with the keyboard; nothing is written.
 private void MoveImportedAnnex12Cell(Control grid,object annex,int row,int column){
  Form owner=grid.FindForm();uint pid;
  if((column!=18&&column!=20)||owner==null||owner!=roundtripOwner||!owner.Visible||!owner.Enabled||!grid.Visible||!grid.Enabled||Get(grid,"ActiveSheet")!=annex||OriginalMessageVisible()||Annex12CellLocked(annex,row,column))throw new InvalidOperationException();
  grid.Focus();GetWindowThreadProcessId(GetForegroundWindow(),out pid);if(pid!=(uint)Process.GetCurrentProcess().Id||!grid.ContainsFocus)throw new InvalidOperationException();
  annex.GetType().GetMethod("SetActiveCell",new Type[]{typeof(int),typeof(int)}).Invoke(annex,new object[]{row,column});Application.DoEvents();grid.Focus();
  if(Convert.ToInt32(Get(annex,"ActiveRowIndex"))!=row||Convert.ToInt32(Get(annex,"ActiveColumnIndex"))!=column||OriginalMessageVisible()||Get(grid,"ActiveSheet")!=annex)throw new InvalidOperationException();
 }
 // One real Left key from S (not editing) moves the original active cell to R, so the vendor raises
 // EnterCell and the original handler rebuilds R's list; nothing is typed or written.
 private void EnterImportedAnnex12HeadByKey(Control grid,object annex,int row){
  MoveImportedAnnex12Cell(grid,annex,row,18);
  Form owner=grid.FindForm();uint pid;
  if(owner==null||owner!=roundtripOwner||Get(grid,"EditingControl")!=null||Annex12CellLocked(annex,row,17))throw new InvalidOperationException();
  grid.Focus();GetWindowThreadProcessId(GetForegroundWindow(),out pid);if(pid!=(uint)Process.GetCurrentProcess().Id||!grid.ContainsFocus||OriginalMessageVisible())throw new InvalidOperationException();
  string before=CellText(annex,row,17);SendKeys.SendWait("{LEFT}");Application.DoEvents();grid.Focus();
  if(Convert.ToInt32(Get(annex,"ActiveRowIndex"))!=row||Convert.ToInt32(Get(annex,"ActiveColumnIndex"))!=17||CellText(annex,row,17)!=before||OriginalMessageVisible()||Get(grid,"ActiveSheet")!=annex)throw new InvalidOperationException();
 }
 // Opens and closes the original percentage editor without any key, as tabbing through it does.
 private void PassImportedAnnex12Percentage(Control grid,object annex,int row){
  string before=Convert.ToString(Get(Cell(annex,row,20),"Value"),CultureInfo.InvariantCulture);
  MoveImportedAnnex12Cell(grid,annex,row,20);
  grid.GetType().GetMethod("StartCellEditing",new Type[]{typeof(EventArgs),typeof(bool)}).Invoke(grid,new object[]{EventArgs.Empty,false});
  Control editor=Get(grid,"EditingControl") as Control;if(editor==null||!editor.Visible||!editor.Enabled)throw new InvalidOperationException();
  grid.GetType().GetMethod("StopCellEditing",Type.EmptyTypes).Invoke(grid,null);Application.DoEvents();grid.Focus();
  if(Convert.ToString(Get(Cell(annex,row,20),"Value"),CultureInfo.InvariantCulture)!=before||OriginalMessageVisible()||Get(grid,"ActiveSheet")!=annex)throw new InvalidOperationException();
 }
}
