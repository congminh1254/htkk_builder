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
 private string Annex12ExportJson(){string q=((char)34).ToString();return ","+q+"annex12ExportMainZeroMatched"+q+":"+Bool(annex12ExportMainZeroMatched)+","+q+"annex12ExportShapeMatched"+q+":"+Bool(annex12ExportShapeMatched)+","+q+"annex12ExportSchemaVerified"+q+":"+Bool(annex12ExportSchemaVerified);}
 private void StartOriginalAnnex12Export(Control grid,object annex){
  Annex12InputOwner(grid,annex);
  if(mode!="gtgt-annex12-export-inspect"||exportStarted||annex12InputActionCount!=14||!annex12InputReadOnlyIdentityMatched||!annex12InputIdentityMatched||!annex12InputTypesMatched||!annex12InputGeographyMatched||!annex12InputTaxAuthoritiesMatched||!annex12InputPercentagesMatched||!annex12InputZeroTaxMatched)throw new InvalidOperationException();
  object sheets=Get(grid,"Sheets");if(Convert.ToInt32(Get(sheets,"Count"))!=11)throw new InvalidOperationException();PropertyInfo item=sheets.GetType().GetProperty("Item",new Type[]{typeof(int)});if(item==null)throw new InvalidOperationException();object main=item.GetValue(sheets,new object[]{0});
  if(Convert.ToInt32(Get(main,"RowCount"))!=72||Convert.ToInt32(Get(main,"ColumnCount"))!=24||CellText(main,9,3)!=FakeName||CellText(main,10,3).Replace("-",String.Empty)!=Mst||CellText(main,63,10)!=FakeSigner||Selected(Get(Cell(main,35,8),"Value"))||!Convert.ToBoolean(Get(main,"AutoCalculation")))throw new InvalidOperationException();
  InspectMoneyZero(main);InspectCaseMoney(main);
  annex12ExportMainZeroMatched=gtgtZero&&gtgtEmptyMoney==0&&gtgtCaseMoneyMatched&&gtgtCaseMoneyCount==27&&gtgtCaseMismatchMask==0&&gtgtCaseNonzeroMask==0;
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
 private void ValidateOriginalAnnex12Export(){
  if(mode!="gtgt-annex12-export-inspect"||!annex12ExportMainZeroMatched||!exportSchemaPinnedVerified||!exportFileExists||!exportSyntheticIdentityMatched||exportBytes<1||exportBytes>262144||Hash(exportPath)!=exportSha256)throw new InvalidOperationException();
  SetStage(HtkkAutomationStage.GtgtAnnex12ExportValidating);Record();XmlDocument document=ReadBoundedOriginalXml(exportPath);XmlNamespaceManager ns=new XmlNamespaceManager(document.NameTable);ns.AddNamespace("t","http://kekhaithue.gdt.gov.vn/TKhaiThue");
  XmlNodeList plucs=document.SelectNodes("/t:HSoThueDTu/t:HSoKhaiThue/t:PLuc",ns),groups=document.SelectNodes("/t:HSoThueDTu/t:HSoKhaiThue/t:PLuc/t:PLuc_01_2_GTGT/t:TenNhaMay",ns),rows=document.SelectNodes("/t:HSoThueDTu/t:HSoKhaiThue/t:PLuc/t:PLuc_01_2_GTGT/t:TenNhaMay/t:DiaBanPhanBo",ns);
  int leaves=0;foreach(XmlNode node in document.SelectNodes("//*[not(*)]"))leaves++;
  annex12ExportShapeMatched=plucs.Count==1&&plucs[0].ChildNodes.Count==1&&groups.Count==1&&rows.Count==2&&leaves==112;
  if(!annex12ExportShapeMatched)throw new InvalidOperationException();
  string root=Path.Combine(Path.GetDirectoryName(project),"InterfaceTemplates"),schema=Path.Combine(root,"Validate/01_GTGT_TT80_283.xsd");Annex12PinnedSchemaResolver resolver=new Annex12PinnedSchemaResolver(root);
  XmlSchemaSet schemas=new XmlSchemaSet();schemas.XmlResolver=resolver;bool valid=true;schemas.ValidationEventHandler+=delegate(object sender,ValidationEventArgs args){valid=false;};
  XmlReaderSettings safe=new XmlReaderSettings();safe.ProhibitDtd=true;safe.XmlResolver=null;
  using(XmlReader reader=XmlReader.Create(schema,safe))schemas.Add(null,reader);schemas.Compile();if(!valid)throw new InvalidOperationException();
  XmlReaderSettings check=new XmlReaderSettings();check.ProhibitDtd=true;check.XmlResolver=null;check.ValidationType=ValidationType.Schema;check.Schemas=schemas;check.ValidationFlags=XmlSchemaValidationFlags.ProcessIdentityConstraints|XmlSchemaValidationFlags.AllowXmlAttributes;check.ValidationEventHandler+=delegate(object sender,ValidationEventArgs args){valid=false;};
  using(XmlReader reader=XmlReader.Create(exportPath,check)){while(reader.Read()){} }
  annex12ExportSchemaVerified=valid&&Hash(exportPath)==exportSha256;if(!annex12ExportSchemaVerified)throw new InvalidOperationException();Record();
 }
}
