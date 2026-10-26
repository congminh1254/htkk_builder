// Own staged controller of ORIGINAL period controls and inspection of the ORIGINAL D1 sheet.
// No HEADER or declaration XML is created by this helper.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Reflection;
using System.Text;
using System.Windows.Forms;
using System.Xml;

public sealed partial class HtkkGuiReferenceAutomation {
 private bool periodDateMatched=false,periodFirstMatched=false,periodActivityMatched=false,periodGeographyMatched=false,periodNoAnnexMatched=false,periodConfirmInvoked=false;
 private bool gtgtPins=false,gtgtVersion=false,gtgtPeriod=false,gtgtSheet=false,gtgtName=false,gtgtDimensions=false,gtgtIdentity=false,gtgtCt21=false,gtgtSigner=false,gtgtZero=false;
 private int annexSelected=0,gtgtRows=0,gtgtColumns=0,gtgtSheets=0,gtgtEmptyMoney=0;
 private bool gtgtCt42BeforeExportObserved=false,gtgtCt42LockedBeforeExport=false,gtgtCt42AfterImportObserved=false,gtgtCt42LockedAfterImport=false;
 private bool gtgtSheetInspectionBusy=false,gtgtAutoCalculationReady=false,gtgtBusinessInstanceMatched=false;
 private bool gtgtCaseMoneyMatched=false,gtgtCt42Locked=false,webCaseEdited=false;private int gtgtCaseMoneyCount=0,gtgtCaseMismatchMask=0,gtgtCaseNonzeroMask=0;private Stopwatch webCaseEditClock=null;
 private Stopwatch gtgtObservationClock=null;
 private string SheetJson(){
  string q=((char)34).ToString();string[] names=new string[]{"periodYearMonthMatched","periodFirstDeclarationMatched","periodActivityMatched","periodGeographyMatched","periodNoAnnexMatched","periodConfirmInvoked","gtgtWorkbookPinsVerified","gtgtMenuVersionMatched","gtgtPeriodModelMatched","gtgtSheetObserved","gtgtSheetNameMatched","gtgtDimensionsMatched","gtgtIdentityMatched","gtgtCt21Ready","gtgtSignatureReady","gtgtMonetaryZero"};
  bool[] values=new bool[]{periodDateMatched,periodFirstMatched,periodActivityMatched,periodGeographyMatched,periodNoAnnexMatched,periodConfirmInvoked,gtgtPins,gtgtVersion,gtgtPeriod,gtgtSheet,gtgtName,gtgtDimensions,gtgtIdentity,gtgtCt21,gtgtSigner,gtgtZero};StringBuilder json=new StringBuilder();
  for(int index=0;index<names.Length;index++)json.Append(","+q+names[index]+q+":"+Bool(values[index]));
  json.Append(","+q+"gtgtCt42BeforeExportObserved"+q+":"+Bool(gtgtCt42BeforeExportObserved)+","+q+"gtgtCt42LockedBeforeExport"+q+":"+Bool(gtgtCt42LockedBeforeExport)+","+q+"gtgtCt42AfterImportObserved"+q+":"+Bool(gtgtCt42AfterImportObserved)+","+q+"gtgtCt42LockedAfterImport"+q+":"+Bool(gtgtCt42LockedAfterImport));
  json.Append(","+q+"gtgtAutoCalculationReady"+q+":"+Bool(gtgtAutoCalculationReady)+","+q+"gtgtBusinessInstanceMatched"+q+":"+Bool(gtgtBusinessInstanceMatched));
  json.Append(","+q+"gtgtCaseMoneyMatched"+q+":"+Bool(gtgtCaseMoneyMatched)+","+q+"gtgtCt42Locked"+q+":"+Bool(gtgtCt42Locked)+","+q+"gtgtCaseMoneyCount"+q+":"+gtgtCaseMoneyCount+","+q+"gtgtCaseMismatchMask"+q+":"+gtgtCaseMismatchMask+","+q+"gtgtCaseNonzeroMask"+q+":"+gtgtCaseNonzeroMask);
  json.Append(","+q+"annexSelectedCount"+q+":"+annexSelected+","+q+"gtgtSheetRows"+q+":"+gtgtRows+","+q+"gtgtSheetColumns"+q+":"+gtgtColumns+","+q+"gtgtSheetCount"+q+":"+gtgtSheets+","+q+"gtgtEmptyMonetaryCount"+q+":"+gtgtEmptyMoney);return json.ToString();
 }
 private static Control ReadableNamed(Control root,string name){Control[] controls=root.Controls.Find(name,true);if(controls.Length!=1||!controls[0].Visible)throw new InvalidOperationException();return controls[0];}
 private static Control Named(Control root,string name){Control control=ReadableNamed(root,name);if(!control.Enabled)throw new InvalidOperationException();return control;}
 private static bool CheckValue(Control control){RadioButton radio=control as RadioButton;if(radio!=null)return radio.Checked;CheckBox check=control as CheckBox;if(check!=null)return check.Checked;throw new InvalidOperationException();}
 private static void SetCheck(Control control,bool value){RadioButton radio=control as RadioButton;if(radio!=null){radio.Checked=value;return;}CheckBox check=control as CheckBox;if(check!=null){check.Checked=value;return;}throw new InvalidOperationException();}
 private static void SetText(Control root,string name,string value){TextBoxBase input=Named(root,name) as TextBoxBase;if(input==null)throw new InvalidOperationException();input.Focus();input.Text=value;if(input.Text!=value)throw new InvalidOperationException();}
 private static bool SelectGeography(Control root,string name,string code,string label,string codeProperty,string labelProperty){
  ComboBox combo=ReadableNamed(root,name) as ComboBox;if(combo==null)throw new InvalidOperationException();
  // ORIGINAL ShowDetailpnTinhCQT binds human-label string lists, not Key/Value
  // items. ORIGINAL SelectedIndexChanged resolves those labels to period codes.
  // Never write SelectedValue=code: that transiently deselects these source lists.
  // Focus commits the original mskMonth.Leave handler before resolving items.
  if(combo.Enabled){combo.Focus();if(!combo.Visible||combo.IsDisposed)return false;}
  int selected=-1;for(int index=0;index<combo.Items.Count&&index<4096;index++){if(combo.GetItemText(combo.Items[index])==label){if(selected>=0)throw new InvalidOperationException();selected=index;}}
  if(selected<0)return false;
  if(combo.Enabled){if(combo.SelectedIndex!=selected)combo.SelectedIndex=selected;}
  else if(combo.SelectedIndex!=selected)return false;
  object currentPeriod=Global("TTPeriodInfo");
  return combo.Text==label&&Convert.ToString(Get(currentPeriod,codeProperty),CultureInfo.InvariantCulture)==code&&Convert.ToString(Get(currentPeriod,labelProperty),CultureInfo.InvariantCulture)==label;
 }
 private bool SelectSourceActivity(Control period){
  const string label="Hoạt động sản xuất kinh doanh thông thường";
  string file=Path.Combine(Path.GetDirectoryName(project),"InterfaceIni/Catalogue_DM_NNKD.xml");
  if(new FileInfo(file).Length>2000000||Hash(file)!="8e19468e899e1b6e35a9d584dddd5e278c0daf1127d4f14ac5c4e03b3164ea88")return false;
  XmlReaderSettings settings=new XmlReaderSettings();settings.ProhibitDtd=true;settings.XmlResolver=null;XmlDocument document=new XmlDocument();document.XmlResolver=null;
  using(XmlReader reader=XmlReader.Create(file,settings)){document.Load(reader);}int sourceMatches=0;
  foreach(XmlNode item in document.SelectNodes("//Item[@Value]")){if(item.Attributes["Value"].Value=="01_GTGT_TT80###00###"+label)sourceMatches++;}
  if(sourceMatches!=1)return false;
  // ControlInit builds dictionary Key=source item[1], Value=source item[2].
  // TT80 internal catalogue ID is 00; 1701 belongs to the older 01_GTGT group/tax code.
  ComboBox combo=ReadableNamed(period,"cboNganhKD") as ComboBox;if(combo==null||combo.DisplayMember!="Value"||combo.ValueMember!="Key")return false;
  int selected=-1;for(int index=0;index<combo.Items.Count&&index<4096;index++){if(combo.GetItemText(combo.Items[index])==label){if(selected>=0)return false;selected=index;}}
  if(selected<0)return false;if(combo.SelectedIndex!=selected){if(!combo.Enabled)return false;combo.SelectedIndex=selected;}
  return Convert.ToString(combo.SelectedValue,CultureInfo.InvariantCulture)=="00";
 }
 private static bool Selected(object value){
  if(value==null||value==DBNull.Value)return false;if(value is bool)return (bool)value;
  string text=Convert.ToString(value,CultureInfo.InvariantCulture);if(text==String.Empty||text=="False"||text=="0")return false;if(text=="True"||text=="1")return true;throw new InvalidOperationException();
 }
 private static Assembly OriginalAssembly(){
  foreach(Assembly assembly in AppDomain.CurrentDomain.GetAssemblies()){if(assembly.GetName().Name=="HTKK")return assembly;}throw new InvalidOperationException();
 }
 private static object Global(string name){Type settings=OriginalAssembly().GetType("HTKK.WinSettings",true);FieldInfo field=settings.GetField(name,BindingFlags.Public|BindingFlags.NonPublic|BindingFlags.Static);if(field==null)throw new InvalidOperationException();return field.GetValue(null);}
 private void ConfigureOriginalGtgtPeriod(Control period){
  stage="gtgt-period-configuring";Record();
  if(Convert.ToString(Global("MenuID"),CultureInfo.InvariantCulture)!="D1")throw new InvalidOperationException();
  SetCheck(Named(period,"chkTkhaiThang"),true);SetCheck(Named(period,"OptChinhthuc"),true);
  periodFirstMatched=CheckValue(Named(period,"OptChinhthuc"))&&!CheckValue(ReadableNamed(period,"OptBosung"));
  SetText(period,"mskYear","2026");SetText(period,"mskMonth","10");
  periodDateMatched=Named(period,"mskYear").Text=="2026"&&Named(period,"mskMonth").Text=="10"&&CheckValue(Named(period,"chkTkhaiThang"))&&!CheckValue(ReadableNamed(period,"chkTKQuy"));
  periodDescriptions.Clear();periodControlCount=0;int currentControlCount=0;DescribePeriod(period,ref currentControlCount);
  stage="gtgt-period-province-selecting";Record();bool provinceMatched=SelectGeography(period,"cboTinh","101","Thành phố Hà Nội","MaTinh","TenTinh");
  stage="gtgt-period-ward-selecting";Record();bool wardMatched=SelectGeography(period,"cboXa","10129087","Phường Sơn Tây","MaXa","TenXa");
  stage="gtgt-period-taxhead-selecting";Record();bool taxHeadMatched=SelectGeography(period,"cboCQTCuc","10100","Thuế Thành phố Hà Nội","maCQTCapCuc","tenCQTCapCuc");
  stage="gtgt-period-taxlocal-selecting";Record();bool taxLocalMatched=SelectGeography(period,"cboCQTChiCuc","10129","Thuế cơ sở 16 Thành phố Hà Nội","maCQTQuanLy","tenCQTQuanLy");
  periodGeographyMatched=provinceMatched&&wardMatched&&taxHeadMatched&&taxLocalMatched;
  stage="gtgt-period-activity-selecting";Record();periodActivityMatched=SelectSourceActivity(period);
  // Exercise the ORIGINAL select-all/clear-all control, preserving its locked-row rules.
  Control all=ReadableNamed(period,"chkChonPhuLucKeKhaiAll");if(all.Enabled){SetCheck(all,true);SetCheck(all,false);}
  Control annex=ReadableNamed(period,"axfpsPhuLuc");if(!IsSpread(annex))throw new InvalidOperationException();object annexSheet=Get(annex,"ActiveSheet");int annexRows=Convert.ToInt32(Get(annexSheet,"RowCount"));if(annexRows<0||annexRows>512)throw new InvalidOperationException();annexSelected=0;
  for(int row=0;row<annexRows;row++)if(Selected(Get(Cell(annexSheet,row,0),"Value")))annexSelected++;
  periodNoAnnexMatched=annexSelected==0&&!CheckValue(all);
  if(!periodDateMatched||!periodFirstMatched||!periodGeographyMatched||!periodActivityMatched||!periodNoAnnexMatched){stage="gtgt-period-inputs-not-matched";finished=true;Record();return;}
  Button confirm=Named(period,"btnDongY") as Button;if(confirm==null||confirm.Text.Replace("&",String.Empty).Trim()!="Đồng ý")throw new InvalidOperationException();
  navigationPhase="waiting-gtgt-sheet";stage="gtgt-period-confirm-invoking";periodConfirmInvoked=true;Record();
  // Original OpenToKhai uses ShowDialog. This timer observes its real sheet inside
  // that nested ORIGINAL message loop, without closing or bypassing any validator.
  using(System.Windows.Forms.Timer watcher=new System.Windows.Forms.Timer()){
   watcher.Interval=100;watcher.Tick+=delegate(object sender,EventArgs args){try{InspectOriginalGtgtSheet();if(finished)watcher.Stop();}catch(Exception error){watcher.Stop();Failure(error);}};
   watcher.Start();try{confirm.PerformClick();}finally{watcher.Stop();}
  }
  if(!finished){stage="waiting-gtgt-sheet";Record();}
 }
 private static void FindWorksheets(Control root,List<Form> forms,ref int visited){
  if(++visited>512)return;Form form=root as Form;if(form!=null&&form.Visible&&!form.IsDisposed&&form.GetType().FullName=="HTKK.frmWinToKhai"&&!forms.Contains(form))forms.Add(form);
  foreach(Control child in root.Controls){if(visited>=512)break;FindWorksheets(child,forms,ref visited);}
 }
 private void InspectOriginalGtgtSheet(){if(gtgtSheetInspectionBusy)return;gtgtSheetInspectionBusy=true;try{InspectOriginalGtgtSheetCore();}finally{gtgtSheetInspectionBusy=false;}}
 private void InspectOriginalGtgtSheetCore(){
  if(finished||exportStarted)return;
  List<Form> forms=new List<Form>();int visited=0;foreach(Form top in Application.OpenForms){if(visited>=512)break;if(top.Visible&&!top.IsDisposed)FindWorksheets(top,forms,ref visited);}
  if(forms.Count!=1){stage="waiting-gtgt-sheet";Record();return;}
  List<Control> grids=new List<Control>();visited=0;GatherSpreads(forms[0],grids,ref visited);if(grids.Count!=1){stage="waiting-gtgt-sheet";Record();return;}
  Control grid=grids[0];object sheet=Get(grid,"ActiveSheet");gtgtRows=Convert.ToInt32(Get(sheet,"RowCount"));gtgtColumns=Convert.ToInt32(Get(sheet,"ColumnCount"));gtgtSheets=Convert.ToInt32(Get(Get(grid,"Sheets"),"Count"));
  if(gtgtRows<67||gtgtColumns<15){stage="waiting-gtgt-sheet";Record();return;}
  gtgtSheet=true;gtgtDimensions=gtgtRows==72&&gtgtColumns==24;string sheetName=Convert.ToString(Get(sheet,"SheetName"),CultureInfo.InvariantCulture);gtgtName=sheetName=="01"||sheetName=="Tờ khai";
  string root=Path.GetDirectoryName(project);
  gtgtPins=Hash(Path.Combine(root,"InterfaceTemplates/excel/01_GTGT_TT80_283.xls"))=="8ad9ec9f0f3462da75ce4e873e4bb60003947e9edd5d738a5055e37d6c73b310"&&Hash(Path.Combine(root,"InterfaceTemplates/xml/01_GTGT_TT80_283.xml"))=="40f5d6f711f7acb69dcc4098e3e3bb0b1849224d1c185902a50b8cae6fc50aae"&&Hash(Path.Combine(root,"InterfaceTemplates/xml/01_GTGT_TT80_xml_283.xml"))=="7ba334067c52ea22cd744dcf2c0ff444190d6661f6b3e9b3ea08e5ead574830c";
  gtgtVersion=Convert.ToString(Global("MenuID"),CultureInfo.InvariantCulture)=="D1"&&Convert.ToString(Get(Global("ToKhaiInfo"),"VersionXML"),CultureInfo.InvariantCulture)=="2.8.3";
  object currentPeriod=Global("TTPeriodInfo");gtgtPeriod=Convert.ToString(Get(currentPeriod,"KieuKy"),CultureInfo.InvariantCulture)=="M"&&Convert.ToString(Get(currentPeriod,"Nam"),CultureInfo.InvariantCulture)=="2026"&&Convert.ToString(Get(currentPeriod,"Thang"),CultureInfo.InvariantCulture)=="10"&&Convert.ToString(Get(currentPeriod,"LoaiToKhai"),CultureInfo.InvariantCulture)=="C";
  gtgtIdentity=CellText(sheet,9,3)==FakeName&&CellText(sheet,10,3).Replace("-",String.Empty)==Mst;gtgtSigner=CellText(sheet,63,10)==FakeSigner;
  object checkbox=Cell(sheet,35,8),cellType=Get(checkbox,"CellType");gtgtCt21=cellType!=null&&cellType.GetType().FullName=="FarPoint.Win.Spread.CellType.CheckBoxCellType"&&!Convert.ToBoolean(Get(checkbox,"Locked"))&&!Selected(Get(checkbox,"Value"));
  InspectMoneyZero(sheet);
  bool matched=gtgtPins&&gtgtVersion&&gtgtPeriod&&gtgtName&&gtgtDimensions&&gtgtIdentity&&gtgtCt21;
  if(gtgtObservationClock==null)gtgtObservationClock=Stopwatch.StartNew();
  // Original load may pump a progress form while sheet binding is still in flight.
  if(!matched&&gtgtObservationClock.Elapsed.TotalSeconds<2){stage="waiting-gtgt-sheet";Record();return;}
  if(matched&&mode=="gtgt-web-import-inspect"){
   gtgtAutoCalculationReady=Convert.ToBoolean(Get(sheet,"AutoCalculation"));object business=Global("InstanceClass");gtgtBusinessInstanceMatched=business!=null&&business.GetType().FullName=="TAX.HTKK.Business.Gtgt01TT80Nckt283";
   if(!gtgtAutoCalculationReady||!gtgtBusinessInstanceMatched||!forms[0].Enabled||!grid.Enabled||OriginalMessageVisible()){stage="waiting-gtgt-sheet";Record();return;}
   if(!webInputVerified)VerifyOwnWebInput();
   gtgtCt42Locked=Convert.ToBoolean(Get(Cell(sheet,60,11),"Locked"));
   if(webCaseId=="01GTGT-sale10-M10-2026"&&!webCaseEdited){
    if(!gtgtZero||gtgtEmptyMoney!=0||gtgtCt42Locked||Convert.ToBoolean(Get(Cell(sheet,47,9),"Locked")))throw new InvalidOperationException();
    webCaseEdited=true;webCaseEditClock=Stopwatch.StartNew();Edit(grid,sheet,47,9,"1000000",false,"gtgt-case-editing",false);return;
   }
   InspectCaseMoney(sheet);
   if(!gtgtCaseMoneyMatched){if(webCaseEditClock!=null&&webCaseEditClock.Elapsed.TotalSeconds<2){stage="waiting-gtgt-sheet";Record();return;}throw new InvalidOperationException();}
  }else InspectCaseMoney(sheet);
  if(matched&&(mode=="gtgt-export-inspect"||mode=="gtgt-roundtrip-inspect"||mode=="gtgt-web-import-inspect")){StartOriginalGtgtExport(forms[0]);return;}
  finished=true;stage=matched?"gtgt-sheet-inspected":"gtgt-sheet-contract-not-matched";Record();
 }
 private void InspectMoneyZero(object sheet){
  int[,] coordinates=new int[,] {{36,11},{39,9},{39,11},{40,9},{40,11},{41,11},{43,9},{44,9},{44,11},{45,9},{46,9},{46,11},{47,9},{47,11},{48,9},{49,9},{49,11},{50,11},{52,11},{53,11},{54,11},{56,11},{57,11},{58,11},{59,11},{60,11},{61,11}};gtgtZero=true;gtgtEmptyMoney=0;
  for(int index=0;index<coordinates.GetLength(0);index++){object value=Get(Cell(sheet,coordinates[index,0],coordinates[index,1]),"Value");if(value==null||value==DBNull.Value||Convert.ToString(value,CultureInfo.InvariantCulture)==String.Empty){gtgtEmptyMoney++;continue;}decimal number;if(!Decimal.TryParse(Convert.ToString(value,CultureInfo.InvariantCulture),NumberStyles.Number,CultureInfo.InvariantCulture,out number)||number!=Decimal.Zero)gtgtZero=false;}
 }
 private void InspectCaseMoney(object sheet){
  int[,] coordinates=new int[,] {{36,11},{39,9},{39,11},{40,9},{40,11},{41,11},{43,9},{44,9},{44,11},{45,9},{46,9},{46,11},{47,9},{47,11},{48,9},{49,9},{49,11},{50,11},{52,11},{53,11},{54,11},{56,11},{57,11},{58,11},{59,11},{60,11},{61,11}};
  gtgtCaseMoneyMatched=true;gtgtCaseMoneyCount=0;gtgtCaseMismatchMask=0;gtgtCaseNonzeroMask=0;gtgtCt42Locked=Convert.ToBoolean(Get(Cell(sheet,60,11),"Locked"));
  for(int index=0;index<coordinates.GetLength(0);index++){
   int row=coordinates[index,0],column=coordinates[index,1];decimal expected=Decimal.Zero;
   if(webCaseId=="01GTGT-sale10-M10-2026"){
    if(column==9&&(row==44||row==47||row==49))expected=1000000;
    if(column==11&&(row==44||row==47||row==49||row==50||row==56||row==58))expected=100000;
   }
   object value=Get(Cell(sheet,row,column),"Value");decimal number;
   if(value==null||value==DBNull.Value||!Decimal.TryParse(Convert.ToString(value,CultureInfo.InvariantCulture),NumberStyles.Number,CultureInfo.InvariantCulture,out number)){gtgtCaseMoneyMatched=false;gtgtCaseMismatchMask|=1<<index;continue;}
   gtgtCaseMoneyCount++;if(number!=0)gtgtCaseNonzeroMask|=1<<index;if(number!=expected){gtgtCaseMoneyMatched=false;gtgtCaseMismatchMask|=1<<index;}
  }
  if(gtgtCaseMoneyCount!=27)gtgtCaseMoneyMatched=false;
 }
}
