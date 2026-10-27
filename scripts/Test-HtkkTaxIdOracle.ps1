# The caller must first authenticate the installed payload against the official-distribution CAB.
# This helper executes only fixed synthetic checksum vectors, never taxpayer input or a tax lookup.
function Invoke-HtkkTaxIdOracle {
  [CmdletBinding()]
  param([Parameter(Mandatory=$true)][string]$ProjectDirectory,[Parameter(Mandatory=$true)][string]$TemporaryDirectory)
  $ErrorActionPreference = 'Stop'
  . (Join-Path $PSScriptRoot 'Invoke-HtkkBoundedJobProcess.ps1')
  . (Join-Path $PSScriptRoot 'Invoke-HtkkBoundedCompiler.ps1')
  $expectedHash = '281689aaa7df4db33d0debcfc61d32c0c318bb871d4a19a0277d871a7c04bba7'
  $safe = [ordered]@{ status='not-run'; cases=0; matched=0; mismatches=0; runtime='unknown'; compilerExitCode=$null; compilerErrorCodes=@();compilerJobCleanupVerified=$true; oracleExitCode=$null; oracleJobCleanupVerified=$true; dllHashVerified=$false; originalMethodInvoked=$false; fullRoundTrip=$false; userDataUsed=$false }
  $directory = $null; $firewallName = $null
  try {
    $business = Join-Path $ProjectDirectory 'TAX.HTKK.Business.dll'
    if ((Get-FileHash -LiteralPath $business -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expectedHash) { $safe.status='dll-hash-mismatch'; return $safe }
    $safe.dllHashVerified = $true
    $compiler = Join-Path $env:WINDIR 'Microsoft.NET\Framework\v2.0.50727\csc.exe'
    if (-not (Test-Path -LiteralPath $compiler -PathType Leaf)) { $safe.status='clr2-compiler-unavailable'; return $safe }
    $directory = Join-Path $TemporaryDirectory ('tax-id-oracle-' + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $directory | Out-Null
    $source = Join-Path $directory 'ChecksumOracle.cs'; $program = Join-Path $directory 'ChecksumOracle.exe'; $outputFile = Join-Path $directory 'result.json'
    @'
using System;
using System.IO;
using System.Reflection;
using System.Text;
internal sealed class ChecksumCase {
  internal readonly string Value; internal readonly bool Expected;
  internal ChecksumCase(string value, bool expected) { Value=value; Expected=expected; }
}
internal static class ChecksumOracle {
  private static int cases=0, matched=0;
  private static string runtime="unknown";
  private static string project;
  private static Assembly ResolveAssembly(object sender, ResolveEventArgs args) {
    string name=new AssemblyName(args.Name).Name;
    if (String.IsNullOrEmpty(name) || name.IndexOfAny(new char[]{'/', (char)92, ':'})>=0) return null;
    string candidate=Path.Combine(project,name+".dll");
    return File.Exists(candidate) ? Assembly.LoadFrom(candidate) : null;
  }
  private static void WriteResult(string path,string status) {
    string q=((char)34).ToString();
    string json="{"+q+"format"+q+":"+q+"htkk-tax-id-oracle-v1"+q+","+q+"status"+q+":"+q+status+q+","+q+"cases"+q+":"+cases+","+q+"matched"+q+":"+matched+","+q+"mismatches"+q+":"+(cases-matched)+","+q+"runtime"+q+":"+q+runtime+q+"}";
    File.WriteAllText(path,json,Encoding.UTF8);
  }
  public static int Main(string[] args) {
    if(args.Length!=2) return 9;
    string output=args[1];
    try {
      runtime=Environment.Version.Major==2 ? "clr2" : "unsupported";
      if(runtime!="clr2") { WriteResult(output,"unsupported-runtime"); return 3; }
      project=Path.GetFullPath(args[0]);
      AppDomain.CurrentDomain.AssemblyResolve+=new ResolveEventHandler(ResolveAssembly);
      Assembly assembly=Assembly.LoadFrom(Path.Combine(project,"TAX.HTKK.Business.dll"));
      Type type=assembly.GetType("TAX.HTKK.Business.ValidateBase",true);
      MethodInfo method=type.GetMethod("CheckMaSoThue",BindingFlags.Public|BindingFlags.Static,null,new Type[]{typeof(string)},null);
      if(method==null || method.ReturnType!=typeof(bool) || !method.IsStatic) { WriteResult(output,"method-signature-mismatch"); return 4; }
      ChecksumCase[] vectors=new ChecksumCase[]{
        new ChecksumCase("9999999997",true),new ChecksumCase("9999999997001",true),new ChecksumCase("9999999997-001",true),
        new ChecksumCase("9999999997000",true),new ChecksumCase("9999999997-000",true),new ChecksumCase("0000000000",false),
        new ChecksumCase("9999999990-001",false),new ChecksumCase("9999999990001",false),new ChecksumCase("",false),
        new ChecksumCase("9999999997 ",false),new ChecksumCase(" 9999999997",false),new ChecksumCase("999999999",false),
        new ChecksumCase("999999999700",false),new ChecksumCase("99999999970001",false),new ChecksumCase("9999999997-01",false),
        new ChecksumCase("9999999997-0001",false),new ChecksumCase("9999999997-ABC",false),new ChecksumCase("99999999A7",false),
        new ChecksumCase(new string(new char[]{(char)0xFF19,(char)0xFF19,(char)0xFF19,(char)0xFF19,(char)0xFF19,(char)0xFF19,(char)0xFF19,(char)0xFF19,(char)0xFF19,(char)0xFF17}),false),new ChecksumCase("9999999997"+(char)10,false)
      };
      for(int i=0;i<vectors.Length;i++) {
        bool actual=(bool)method.Invoke(null,new object[]{vectors[i].Value});
        cases++; if(actual==vectors[i].Expected) matched++;
      }
      for(int digit=0;digit<=9;digit++) {
        bool actual=(bool)method.Invoke(null,new object[]{"999999999"+digit.ToString(System.Globalization.CultureInfo.InvariantCulture)});
        cases++; if(actual==(digit==7)) matched++;
      }
      WriteResult(output,cases==matched ? "matched" : "mismatch");
      return cases==matched ? 0 : 2;
    } catch { try { WriteResult(output,"reflection-or-invocation-failed"); } catch {} return 5; }
  }
}
'@ | Set-Content -LiteralPath $source -Encoding ASCII
    '<?xml version="1.0"?><configuration><startup><supportedRuntime version="v2.0.50727"/></startup></configuration>' | Set-Content -LiteralPath ($program+'.config') -Encoding ASCII
    $safe.compilerJobCleanupVerified=$false
    $compilerRun=Invoke-HtkkBoundedCompiler -Executable $compiler -WorkingDirectory $directory -Arguments @('/nologo','/target:exe','/platform:x86','/optimize+',('/out:'+$program),$source) -TimeoutMilliseconds 30000
    $safe.compilerJobCleanupVerified=$compilerRun.jobCleanupVerified;$safe.compilerExitCode=$compilerRun.exitCode;$safe.compilerErrorCodes=$compilerRun.compilerErrorCodes
    if(-not $compilerRun.jobCleanupVerified -or $compilerRun.status -notin @('exited','process-timeout')){$safe.status='host-or-tool-failure';return $safe}
    if($compilerRun.timedOut){$safe.status='compile-timeout';return $safe}
    if(-not $compilerRun.diagnosticsVerified){$safe.status='host-or-tool-failure';return $safe}
    if($safe.compilerExitCode -ne 0 -or -not(Test-Path -LiteralPath $program -PathType Leaf)){$safe.status='compile-failed';return $safe}
    $firewallName='HTKK checksum oracle '+[guid]::NewGuid().ToString('N')
    New-NetFirewallRule -DisplayName $firewallName -Direction Outbound -Program $program -Action Block | Out-Null
    $safe.oracleJobCleanupVerified=$false
    $oracleRun=Invoke-HtkkBoundedJobProcess -Executable $program -WorkingDirectory $ProjectDirectory -Arguments @($ProjectDirectory,$outputFile) -TimeoutMilliseconds 30000
    $safe.oracleJobCleanupVerified=$oracleRun.jobCleanupVerified;$safe.oracleExitCode=$oracleRun.exitCode
    if(-not $oracleRun.jobCleanupVerified -or $oracleRun.status -notin @('exited','process-timeout')){$safe.status='host-or-tool-failure';return $safe}
    if($oracleRun.timedOut){$safe.status='oracle-timeout';return $safe}
    if(-not (Test-Path -LiteralPath $outputFile -PathType Leaf) -or (Get-Item -LiteralPath $outputFile).Length -gt 4096) { $safe.status='oracle-result-unavailable'; return $safe }
    $result=Get-Content -LiteralPath $outputFile -Raw | ConvertFrom-Json -AsHashtable
    if($result.format -ne 'htkk-tax-id-oracle-v1' -or $result.status -notin @('matched','mismatch','unsupported-runtime','method-signature-mismatch','reflection-or-invocation-failed') -or $result.runtime -notin @('clr2','unsupported','unknown') -or $result.cases -notin 0..30 -or $result.matched -notin 0..30 -or $result.matched -gt $result.cases -or $result.mismatches -ne ($result.cases-$result.matched)) { $safe.status='oracle-result-invalid'; return $safe }
    $safe.runtime=$result.runtime; $safe.cases=$result.cases; $safe.matched=$result.matched; $safe.mismatches=$result.mismatches
    $safe.originalMethodInvoked=$result.cases -gt 0
    $safe.status=if($safe.oracleExitCode -eq 0 -and $result.status -eq 'matched' -and $result.cases -eq 30 -and $result.matched -eq 30) { 'matched' } elseif($result.status -eq 'mismatch') { 'mismatch' } else { 'oracle-runtime-blocked' }
    return $safe
  } catch { $safe.status='host-or-tool-failure'; return $safe }
  finally {
    if($firewallName) { Remove-NetFirewallRule -DisplayName $firewallName -ErrorAction SilentlyContinue }
    if($directory) { Remove-Item -LiteralPath $directory -Recurse -Force -ErrorAction SilentlyContinue }
  }
}
