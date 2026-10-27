# Read-only oracle for the original property loader. This is not a GUI save/export round trip.
function Invoke-HtkkProfileAliasOracle {
  [CmdletBinding()]
  param([Parameter(Mandatory=$true)][string]$ProjectDirectory,[Parameter(Mandatory=$true)][string]$TemporaryDirectory)
  $ErrorActionPreference = 'Stop'
  . (Join-Path $PSScriptRoot 'Invoke-HtkkBoundedJobProcess.ps1')
  $safe = [ordered]@{ status='not-run'; cases=0; matched=0; mismatches=0; originalLoaderInvocations=0; runtime='unknown'; oracleStage='not-started'; oracleStatus='not-run'; compilerExitCode=$null; compilerErrorCodes=@(); oracleExitCode=$null; oracleJobCleanupVerified=$true; dllHashVerified=$false; templateHashVerified=$false; originalMethodInvoked=$false; aliasValuesRemainDistinct=$false; caseSensitiveBackingFieldUntouched=$false; loaderIgnoresCellId2=$false; legacyPhuongXaConstructorEmpty=$false; templateValuesBlanked=$false; projectSampleUsed=$false; guiOrExportRoundTrip=$false; userDataUsed=$false }
  $directory=$null; $compilerProcess=$null;  $firewallName=$null
  try {
    $dll=Join-Path $ProjectDirectory 'TAX.HTKK.Utilities.dll'
    if((Get-FileHash -LiteralPath $dll -Algorithm SHA256).Hash.ToLowerInvariant() -ne 'ccc35605a4d3bb235f896d6ab43cec4c6543a404159cf10897a57cba23d817ec') { $safe.status='dll-hash-mismatch'; return $safe }
    $safe.dllHashVerified=$true
    $template=Join-Path (Split-Path $ProjectDirectory) 'InterfaceTemplates/xml/HEADER.xml'
    if((Get-FileHash -LiteralPath $template -Algorithm SHA256).Hash.ToLowerInvariant() -ne 'ac34c57b29d4ff85f81be98ebf191630850e8b951f410ef3e4fa810a160d01a7') { $safe.status='template-hash-mismatch'; return $safe }
    $safe.templateHashVerified=$true
    $compiler=Join-Path $env:WINDIR 'Microsoft.NET/Framework/v2.0.50727/csc.exe'
    if (-not (Test-Path -LiteralPath $compiler -PathType Leaf)) { $safe.status='clr2-compiler-unavailable'; return $safe }
    $directory=Join-Path $TemporaryDirectory ('profile-alias-oracle-'+[guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $directory | Out-Null
    $dataRoot=Join-Path $directory 'DATAFILES'; New-Item -ItemType Directory -Path $dataRoot | Out-Null
    $source=Join-Path $directory 'ProfileAliasOracle.cs'; $program=Join-Path $directory 'ProfileAliasOracle.exe'; $resultFile=Join-Path $directory 'result.json'
    @'
using System;
using System.IO;
using System.Reflection;
using System.Text;
using System.Xml;
internal static class ProfileAliasOracle {
  private static int cases=0, matched=0, invocations=0;
  private static string runtime="unknown",project,stage="start";
  private static bool distinct=false, caseUntouched=false, ignoreAliases=false, legacyEmpty=false, blanked=false;
  private static readonly string[] keys=new string[]{"maHuyenNNT","maXaPhuongNNT","maXaPhuongDLyThue"};
  private static readonly string[] vectors=new string[]{"9100001","91000002","91000003"};
  private const string mst="9999999997";
  private static Assembly ResolveAssembly(object sender, ResolveEventArgs args) {
    string name=new AssemblyName(args.Name).Name;
    if(String.IsNullOrEmpty(name)||name.IndexOfAny(new char[]{'/',(char)92,':'})>=0)return null;
    string path=Path.Combine(project,name+".dll");return File.Exists(path)?Assembly.LoadFrom(path):null;
  }
  private static void Check(bool ok){cases++;if(ok)matched++;}
  private static string Bool(bool value){return value?"true":"false";}
  private static void WriteResult(string path,string status){
    string q=((char)34).ToString();
    string json="{"+q+"format"+q+":"+q+"htkk-profile-alias-oracle-v1"+q+","+q+"status"+q+":"+q+status+q+","+q+"runtime"+q+":"+q+runtime+q+","+q+"stage"+q+":"+q+stage+q+","+q+"cases"+q+":"+cases+","+q+"matched"+q+":"+matched+","+q+"mismatches"+q+":"+(cases-matched)+","+q+"originalLoaderInvocations"+q+":"+invocations+","+q+"aliasValuesRemainDistinct"+q+":"+Bool(distinct)+","+q+"caseSensitiveBackingFieldUntouched"+q+":"+Bool(caseUntouched)+","+q+"loaderIgnoresCellId2"+q+":"+Bool(ignoreAliases)+","+q+"legacyPhuongXaConstructorEmpty"+q+":"+Bool(legacyEmpty)+","+q+"templateValuesBlanked"+q+":"+Bool(blanked)+"}";
    File.WriteAllText(path,json,Encoding.UTF8);
  }
  private static XmlDocument LoadTemplate(string path){
    XmlReaderSettings settings=new XmlReaderSettings();settings.ProhibitDtd=true;settings.XmlResolver=null;
    XmlDocument document=new XmlDocument();document.XmlResolver=null;
    using(XmlReader reader=XmlReader.Create(path,settings)){document.Load(reader);}
    return document;
  }
  private static string Read(Type type,object instance,string name){
    PropertyInfo property=type.GetProperty(name,BindingFlags.Public|BindingFlags.Instance);
    if(property==null||property.PropertyType!=typeof(string))throw new InvalidOperationException();
    return (string)property.GetValue(instance,null);
  }
  private static object LoadOriginal(Type type,object loader,MethodInfo method){
    object instance=Activator.CreateInstance(type);object[] arguments=new object[]{instance,mst};
    method.Invoke(loader,arguments);invocations++;
    if(arguments[0]==null)throw new InvalidOperationException();return arguments[0];
  }
  public static int Main(string[] args){
    if(args.Length!=4)return 9;string output=args[3];
    try {
      runtime=Environment.Version.Major==2?"clr2":"unsupported";
      if(runtime!="clr2"){WriteResult(output,"unsupported-runtime");return 3;}
      project=Path.GetFullPath(args[0]);string dataRoot=Path.GetFullPath(args[2]);
      AppDomain.CurrentDomain.AssemblyResolve+=new ResolveEventHandler(ResolveAssembly);
      Assembly assembly=Assembly.LoadFrom(Path.Combine(project,"TAX.HTKK.Utilities.dll"));
      stage="configuration";Type config=assembly.GetType("TAX.HTKK.Utilities.Core.HTKKConfig",true);
      string actualRoot=(string)config.GetProperty("DATAFILES",BindingFlags.Public|BindingFlags.Static).GetValue(null,null);
      if(!String.Equals(Path.GetFullPath(actualRoot).TrimEnd(new char[]{'/',(char)92}),dataRoot.TrimEnd(new char[]{'/',(char)92}),StringComparison.OrdinalIgnoreCase)){WriteResult(output,"data-root-mismatch");return 4;}
      stage="header-types";Type header=assembly.GetType("TAX.HTKK.Utilities.Entity.HTKKHeaderInfo",true);
      Type implementation=assembly.GetType("TAX.HTKK.Utilities.Implement.HTKKHeaderImpl",true);
      MethodInfo method=implementation.GetMethod("SetPropertyHeader",BindingFlags.Public|BindingFlags.Instance,null,new Type[]{header.MakeByRefType(),typeof(string)},null);
      bool signature=method!=null&&method.ReturnType==typeof(void)&&!method.IsStatic;
      Check(signature);if(!signature){WriteResult(output,"method-signature-mismatch");return 5;}
      stage="loader-construction";object loader=Activator.CreateInstance(implementation),baseline=Activator.CreateInstance(header);
      string lowerBefore=Read(header,baseline,"maXaPhuongDlyThue");
      stage="blank-template";XmlDocument document=LoadTemplate(args[1]);XmlNodeList cells=document.GetElementsByTagName("Cell");
      foreach(XmlNode cell in cells){if(cell.Attributes["Value"]==null)throw new InvalidOperationException();cell.Attributes["Value"].Value=String.Empty;}
      blanked=true;XmlNode[] selected=new XmlNode[3];
      foreach(XmlNode cell in cells){
        XmlAttribute property=cell.Attributes["PropertyInfo"];if(property==null)continue;
        if(property.Value=="mst")cell.Attributes["Value"].Value=mst;
        for(int i=0;i<keys.Length;i++)if(property.Value==keys[i]){if(selected[i]!=null)throw new InvalidOperationException();selected[i]=cell;cell.Attributes["Value"].Value=vectors[i];}
      }
      bool collision=true;for(int i=0;i<selected.Length;i++)collision=collision&&selected[i]!=null&&selected[i].Attributes["CellID2"]!=null&&selected[i].Attributes["CellID2"].Value=="V_52";
      Check(collision);if(!collision){WriteResult(output,"source-alias-precondition-failed");return 6;}
      string targetDirectory=Path.Combine(dataRoot,mst);Directory.CreateDirectory(targetDirectory);string target=Path.Combine(targetDirectory,"HEADER.xml");document.Save(target);
      stage="first-load";object first=LoadOriginal(header,loader,method);
      Check(Read(header,first,"mst")==mst);
      bool firstValues=true;for(int i=0;i<keys.Length;i++){bool ok=Read(header,first,keys[i])==vectors[i];Check(ok);firstValues=firstValues&&ok;}
      bool firstCase=String.Equals(Read(header,first,"maXaPhuongDlyThue"),lowerBefore,StringComparison.Ordinal)&&Read(header,first,"maXaPhuongDlyThue")!=vectors[2];Check(firstCase);
      // Change only CellID2 metadata, not identity properties or synthetic data.
      for(int i=0;i<selected.Length;i++)selected[i].Attributes["CellID2"].Value="TEST_ALIAS_"+i;
      document.Save(target);stage="second-load";object second=LoadOriginal(header,loader,method);
      bool secondValues=true;for(int i=0;i<keys.Length;i++){bool ok=Read(header,second,keys[i])==vectors[i];Check(ok);secondValues=secondValues&&ok;}
      bool secondCase=String.Equals(Read(header,second,"maXaPhuongDlyThue"),lowerBefore,StringComparison.Ordinal)&&Read(header,second,"maXaPhuongDlyThue")!=vectors[2];Check(secondCase);
      stage="legacy-constructor";Type common=assembly.GetType("TAX.HTKK.Utilities.Entity.HTKKCMCTTinChungInfo",true);object commonInstance=Activator.CreateInstance(common);
      legacyEmpty=Read(common,commonInstance,"phuongXa")==String.Empty;Check(legacyEmpty);
      distinct=firstValues&&secondValues;caseUntouched=firstCase&&secondCase;ignoreAliases=firstValues&&secondValues;
      stage="complete";bool okAll=cases==12&&cases==matched&&invocations==2;WriteResult(output,okAll?"matched":"mismatch");return okAll?0:2;
    }catch{try{WriteResult(output,"reflection-or-loader-failed");}catch{}return 7;}
  }
}
'@ | Set-Content -LiteralPath $source -Encoding ASCII
    $configuration=[xml]'<?xml version="1.0"?><configuration><appSettings><add key="DataFiles" value=""/><add key="APP_PREFIX" value="HTKK-PROFILE-ORACLE"/><add key="ENABLE_LOGGING" value="0"/></appSettings><startup><supportedRuntime version="v2.0.50727"/></startup></configuration>'
    $configuration.configuration.appSettings.add | Where-Object {$_.key -eq 'DataFiles'} | ForEach-Object {$_.SetAttribute('value',$dataRoot)}
    $configuration.Save($program+'.config')
    $compilerInfo=[Diagnostics.ProcessStartInfo]::new();$compilerInfo.FileName=$compiler;$compilerInfo.WorkingDirectory=$directory;$compilerInfo.UseShellExecute=$false;$compilerInfo.CreateNoWindow=$true
    $compilerInfo.RedirectStandardOutput=$true;$compilerInfo.RedirectStandardError=$true;$compilerInfo.Environment.Clear()
    foreach($key in @('SystemRoot','WINDIR','TEMP','TMP','PATH')){$v=[Environment]::GetEnvironmentVariable($key);if($null -ne $v){$compilerInfo.Environment[$key]=$v}}
    foreach($argument in @('/nologo','/target:exe','/platform:x86','/optimize+',('/out:'+$program),$source)){$compilerInfo.ArgumentList.Add($argument)}
    $compilerProcess=[Diagnostics.Process]::Start($compilerInfo);$compilerOut=$compilerProcess.StandardOutput.ReadToEndAsync();$compilerErr=$compilerProcess.StandardError.ReadToEndAsync()
    if(-not $compilerProcess.WaitForExit(30000)){$compilerProcess.Kill($true);$safe.status='compile-timeout';return $safe}
    $safe.compilerExitCode=$compilerProcess.ExitCode;$compilerText=$compilerOut.GetAwaiter().GetResult()+$compilerErr.GetAwaiter().GetResult()
    $safe.compilerErrorCodes=@([regex]::Matches($compilerText,'\bCS[0-9]{4}\b')|ForEach-Object{$_.Value}|Sort-Object -Unique|Select-Object -First 10)
    if($compilerProcess.ExitCode -ne 0 -or -not(Test-Path -LiteralPath $program -PathType Leaf)){$safe.status='compile-failed';return $safe}
    $firewallName='HTKK profile oracle '+[guid]::NewGuid().ToString('N');New-NetFirewallRule -DisplayName $firewallName -Direction Outbound -Program $program -Action Block|Out-Null
    $safe.oracleJobCleanupVerified=$false
    $oracleRun=Invoke-HtkkBoundedJobProcess -Executable $program -WorkingDirectory $ProjectDirectory -Arguments @($ProjectDirectory,$template,$dataRoot,$resultFile) -TimeoutMilliseconds 30000
    $safe.oracleJobCleanupVerified=$oracleRun.jobCleanupVerified;$safe.oracleExitCode=$oracleRun.exitCode
    if(-not $oracleRun.jobCleanupVerified -or $oracleRun.status -notin @('exited','process-timeout')){$safe.status='host-or-tool-failure';return $safe}
    if($oracleRun.timedOut){$safe.status='oracle-timeout';return $safe}
    if (-not (Test-Path -LiteralPath $resultFile -PathType Leaf) -or (Get-Item -LiteralPath $resultFile).Length -gt 4096){$safe.status='oracle-result-unavailable';return $safe}
    $r=Get-Content -LiteralPath $resultFile -Raw|ConvertFrom-Json -AsHashtable
    $stages=@('start','configuration','header-types','loader-construction','blank-template','first-load','second-load','legacy-constructor','complete')
    $statuses=@('matched','mismatch','unsupported-runtime','data-root-mismatch','method-signature-mismatch','source-alias-precondition-failed','reflection-or-loader-failed')
    if ($r.format -ne 'htkk-profile-alias-oracle-v1' -or $r.status -notin $statuses -or $r.stage -notin $stages -or $r.runtime -notin @('clr2','unsupported','unknown') -or $r.cases -notin 0..12 -or $r.matched -notin 0..12 -or $r.matched -gt $r.cases -or $r.mismatches -ne ($r.cases-$r.matched) -or $r.originalLoaderInvocations -notin 0..2){$safe.status='oracle-result-invalid';return $safe}
    foreach($name in @('aliasValuesRemainDistinct','caseSensitiveBackingFieldUntouched','loaderIgnoresCellId2','legacyPhuongXaConstructorEmpty','templateValuesBlanked')){if($r[$name] -isnot [bool]){$safe.status='oracle-result-invalid';return $safe};$safe[$name]=$r[$name]}
    $safe.oracleStage=$r.stage;$safe.oracleStatus=$r.status;$safe.runtime=$r.runtime;$safe.cases=$r.cases;$safe.matched=$r.matched;$safe.mismatches=$r.mismatches;$safe.originalLoaderInvocations=$r.originalLoaderInvocations;$safe.originalMethodInvoked=$r.originalLoaderInvocations -gt 0
    $safe.status=if ($safe.oracleExitCode -eq 0 -and $r.status -eq 'matched' -and $r.cases -eq 12 -and $r.matched -eq 12 -and $r.originalLoaderInvocations -eq 2 -and $safe.aliasValuesRemainDistinct -and $safe.caseSensitiveBackingFieldUntouched -and $safe.loaderIgnoresCellId2 -and $safe.legacyPhuongXaConstructorEmpty -and $safe.templateValuesBlanked){'matched'}elseif($r.status -eq 'mismatch'){'mismatch'}else{'oracle-runtime-blocked'}
    return $safe
  }catch{$safe.status='host-or-tool-failure';return $safe}
  finally{
    if($null -ne $compilerProcess){if (-not $compilerProcess.HasExited){$compilerProcess.Kill($true)};$compilerProcess.Dispose()}
    if($firewallName){Remove-NetFirewallRule -DisplayName $firewallName -ErrorAction SilentlyContinue}
    if($directory){Remove-Item -LiteralPath $directory -Recurse -Force -ErrorAction SilentlyContinue}
  }
}
