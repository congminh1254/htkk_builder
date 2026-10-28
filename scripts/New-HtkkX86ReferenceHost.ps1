# Preparation only: this function never launches HTKK or the generated host.
# The caller must authenticate the complete installed payload against the official
# CAB first, firewall BOTH host and original executable before launching, and
# delete only the returned created paths when the differential probe finishes.
function New-HtkkX86ReferenceHost {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory=$true)][string]$ProjectDirectory,
    [Parameter(Mandatory=$true)][string]$TemporaryDirectory,
    [ValidateSet('none','inspect','profile-save','gtgt-inspect','gtgt-sheet-inspect','gtgt-amendment-inspect','gtgt-amendment-open-inspect','gtgt-annex12-inspect','gtgt-annex12-row-inspect','gtgt-annex12-input-inspect','gtgt-annex12-numeric-inspect','gtgt-annex12-export-inspect','gtgt-export-inspect','gtgt-roundtrip-inspect','gtgt-web-import-inspect')][string]$GuiAutomation='none'
  )
  $ErrorActionPreference = 'Stop'
  . (Join-Path $PSScriptRoot 'Invoke-HtkkBoundedCompiler.ps1')
  . (Join-Path $PSScriptRoot 'HtkkNativeCompileInputs.ps1')
  $safe = [ordered]@{
    status='not-prepared'; mode='custom-x86-clr2-reference-host'; launched=$false
    originalExeHashVerified=$false; businessDllHashVerified=$false; originalConfigHashVerified=$false
    compilerTrustVerified=$false; compilerExitCode=$null; compilerErrorCodes=@(); compilerJobCleanupVerified=$true
    hostPath=$null; hostSha256=$null; hostConfigPath=$null; resultPath=$null
    arguments=@(); createdPaths=@(); compilerDirectory=$null
    webImportInputPath=$null; webImportInputHashPath=$null; webImportCasePath=$null; webImportSourceShaPath=$null
    guiAutomationMode=$GuiAutomation; guiAutomationResultPath=$null; guiAutomationPermitPath=$null
    originalExecutableModified=$false; originalConfigurationModified=$false
    secondaryDomainUsesOriginalConfiguration=$true; runtimeRoundTrip=$false
  }
   $directory=$null; $owned=@(); $prepared=$false
  $expectedExe='411141d2e728a45f4a35a876afb169d0ac2450de2499e8a1f43ac29ab6401938'
  $expectedBusiness='281689aaa7df4db33d0debcfc61d32c0c318bb871d4a19a0277d871a7c04bba7'
  $expectedConfig='b3547d6a6a61fd6e8e8b64c8976e8702aa94a2b5a44a1cf394c5486162297047'
  try {
    foreach($candidate in @($ProjectDirectory,$TemporaryDirectory)) {
      if(-not [IO.Path]::IsPathRooted($candidate) -or $candidate.StartsWith('\\') -or $candidate.IndexOfAny([IO.Path]::GetInvalidPathChars()) -ge 0) { $safe.status='invalid-local-directory'; return $safe }
    }
    $project=[IO.Path]::GetFullPath($ProjectDirectory)
    $temporary=[IO.Path]::GetFullPath($TemporaryDirectory)
    if(-not (Test-Path -LiteralPath $project -PathType Container) -or -not (Test-Path -LiteralPath $temporary -PathType Container)) { $safe.status='directory-unavailable'; return $safe }
    $original=Join-Path $project 'HTKK.exe'; $business=Join-Path $project 'TAX.HTKK.Business.dll'; $originalConfig=$original+'.config'
    if((Get-FileHash -LiteralPath $original -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expectedExe) { $safe.status='original-exe-hash-mismatch'; return $safe }
    $safe.originalExeHashVerified=$true
    if((Get-FileHash -LiteralPath $business -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expectedBusiness) { $safe.status='business-dll-hash-mismatch'; return $safe }
    $safe.businessDllHashVerified=$true
    if((Get-FileHash -LiteralPath $originalConfig -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expectedConfig) { $safe.status='original-config-hash-mismatch'; return $safe }
    $safe.originalConfigHashVerified=$true
    $compiler=Join-Path $env:WINDIR 'Microsoft.NET\Framework\v2.0.50727\csc.exe'
    if(-not (Test-Path -LiteralPath $compiler -PathType Leaf)) { $safe.status='clr2-x86-compiler-unavailable'; return $safe }
    $signature=Get-AuthenticodeSignature -LiteralPath $compiler
    if($signature.Status -ne 'Valid' -or $null -eq $signature.SignerCertificate -or $signature.SignerCertificate.Subject -notmatch 'Microsoft') { $safe.status='os-compiler-trust-unavailable'; return $safe }
    $safe.compilerTrustVerified=$true
    $directory=Join-Path $temporary ('htkk-x86-host-build-'+[guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $directory | Out-Null
    # Keeping the NEW host beside the original preserves WinForms StartupPath.
    # No original executable, DLL, configuration, PE flag or native dependency is changed.
    $program=Join-Path $project ('HTKK.X86ReferenceHost.'+[guid]::NewGuid().ToString('N')+'.exe')
    $hostConfig=$program+'.config'; $resultFile=$program+'.result.json'
    $automationResultFile=$program+'.gui-automation.json'
    $automationPermitFile=$program+'.gui-automation.allow'
    $candidates=@($program,$hostConfig,$resultFile,$automationResultFile,$automationPermitFile)
    if($GuiAutomation -eq 'gtgt-web-import-inspect'){
      $safe.webImportCasePath=$program+'.web-case.id';$safe.webImportInputPath=$program+'.web-input.xml';$safe.webImportInputHashPath=$program+'.web-input.sha256';$safe.webImportSourceShaPath=$program+'.web-source.sha'
      $candidates+=@($safe.webImportInputPath,$safe.webImportInputHashPath,$safe.webImportSourceShaPath,$safe.webImportCasePath)
    }
    foreach($path in $candidates) { if(Test-Path -LiteralPath $path) { $safe.status='owned-path-already-exists'; return $safe } }
    # Claim only the previously absent unique names; a refusal above must never
    # delete an existing file in the installed project.
    $owned=$candidates
    $source=Join-Path $directory 'HtkkX86ReferenceHost.cs'
    $hostSource=@'
using System;
using System.Globalization;
using System.IO;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
internal static class HtkkX86ReferenceHost {
  private const string ExeHash="411141d2e728a45f4a35a876afb169d0ac2450de2499e8a1f43ac29ab6401938";
  private const string BusinessHash="281689aaa7df4db33d0debcfc61d32c0c318bb871d4a19a0277d871a7c04bba7";
  private const string ConfigHash="b3547d6a6a61fd6e8e8b64c8976e8702aa94a2b5a44a1cf394c5486162297047";
  private static string resultPath;
  private static bool exeVerified, businessVerified, configVerified;
  private static string category="none", outerCategory="none", hresult="none";
  private static string Hash(string path) {
    using(FileStream stream=File.OpenRead(path))
    using(SHA256 algorithm=SHA256.Create()) {
      byte[] bytes=algorithm.ComputeHash(stream); StringBuilder text=new StringBuilder(64);
      for(int i=0;i<bytes.Length;i++) text.Append(bytes[i].ToString("x2",CultureInfo.InvariantCulture));
      return text.ToString();
    }
  }
  private static string Category(Exception error) {
    if(error is BadImageFormatException) return "bitness-load";
    if(error is DllNotFoundException) return "native-library-missing";
    if(error is TypeInitializationException) return "type-initialization";
    if(error is TypeLoadException) return "type-load";
    if(error is FileNotFoundException) return "file-not-found";
    if(error is FileLoadException) return "assembly-load";
    if(error is DirectoryNotFoundException) return "directory-not-found";
    if(error is COMException) return "com-exception";
    if(error is UnauthorizedAccessException) return "access-denied";
    if(error is FormatException) return "format";
    if(error is NullReferenceException) return "null-reference";
    if(error is AccessViolationException) return "access-violation";
    if(error is InvalidOperationException) return "invalid-operation";
    if(error is ArgumentException) return "argument";
    if(error is System.Security.SecurityException) return "security";
    if(error is System.Runtime.Remoting.RemotingException) return "remoting";
    return "other-standard-or-unclassified";
  }
  private static void RecordException(Exception error) {
    // Unwrap only bounded, standard InnerException links. Never inspect Message,
    // StackTrace, Data, FusionLog, arbitrary exception properties or file paths.
    outerCategory=Category(error);
    for(int i=0;i<8 && error.InnerException!=null;i++) error=error.InnerException;
    category=Category(error);
    try { hresult="0x"+unchecked((uint)Marshal.GetHRForException(error)).ToString("x8",CultureInfo.InvariantCulture); } catch { hresult="unavailable"; }
  }
  private static string Bool(bool value) { return value ? "true" : "false"; }
  private static void WriteResult(string status,int exitCode) {
    string q=((char)34).ToString();
    string json="{"+q+"format"+q+":"+q+"htkk-x86-reference-host-v1"+q+","+
      q+"mode"+q+":"+q+"custom-x86-clr2-reference-host"+q+","+
      q+"status"+q+":"+q+status+q+","+
      q+"runtime"+q+":"+q+(Environment.Version.Major==2 ? "clr2" : "unsupported")+q+","+
      q+"bitness"+q+":"+(IntPtr.Size*8).ToString(CultureInfo.InvariantCulture)+","+
      q+"apartment"+q+":"+q+(System.Threading.Thread.CurrentThread.GetApartmentState()==System.Threading.ApartmentState.STA ? "sta" : "unsupported")+q+","+
      q+"originalExeHashVerified"+q+":"+Bool(exeVerified)+","+
      q+"businessDllHashVerified"+q+":"+Bool(businessVerified)+","+
      q+"originalConfigHashVerified"+q+":"+Bool(configVerified)+","+
      q+"launchMechanism"+q+":"+q+"secondary-AppDomain.ExecuteAssembly"+q+","+
      q+"exceptionCategory"+q+":"+q+category+q+","+
      q+"outerExceptionCategory"+q+":"+q+outerCategory+q+","+
      q+"hresult"+q+":"+q+hresult+q+","+
      q+"originalExitCode"+q+":"+exitCode.ToString(CultureInfo.InvariantCulture)+","+
      q+"runtimeRoundTrip"+q+":false}";
    File.WriteAllText(resultPath,json,new UTF8Encoding(false));
  }
  [STAThread]
  public static int Main(string[] args) {
    // No project/result arguments: only fixed names beside this unique host.
    // This prevents arbitrary file execution or output destinations via arguments.
    if(args.Length!=0) return 9;
    string host=Assembly.GetExecutingAssembly().Location;
    string project=Path.GetDirectoryName(Path.GetFullPath(host));
    resultPath=host+".result.json";
    try {
      if(Environment.Version.Major!=2 || IntPtr.Size!=4 || System.Threading.Thread.CurrentThread.GetApartmentState()!=System.Threading.ApartmentState.STA) { WriteResult("unsupported-runtime",-1); return 3; }
      string original=Path.Combine(project,"HTKK.exe");
      string business=Path.Combine(project,"TAX.HTKK.Business.dll");
      string configuration=original+".config";
      exeVerified=Hash(original)==ExeHash; businessVerified=Hash(business)==BusinessHash; configVerified=Hash(configuration)==ConfigHash;
      if(!exeVerified || !businessVerified || !configVerified) { WriteResult("source-hash-mismatch",-1); return 4; }
      Directory.SetCurrentDirectory(project);
      AppDomainSetup setup=new AppDomainSetup();
      setup.ApplicationBase=project;
      setup.ConfigurationFile=configuration;
      setup.ApplicationName="HTKK.exe";
      setup.ShadowCopyFiles="false";
      // The original, unmodified executable is the first executed entry assembly
      // in this secondary domain. No loader is injected into its source code.
      AppDomain domain=AppDomain.CreateDomain("HTKK verified x86 reference",null,setup);
      WriteResult("original-starting",-1);
      // Optional OWN reference helper in the same AppDomain. It uses BeginInvoke
      // to run public grid editors and the original Save handler on the original UI thread.
      const string automationMode="__GUI_AUTOMATION_MODE__";
      if(automationMode!="none") {
        HtkkGuiReferenceAutomation agent=(HtkkGuiReferenceAutomation)domain.CreateInstanceFromAndUnwrap(host,"HtkkGuiReferenceAutomation");
        agent.Start(automationMode);
      }
      int code=domain.ExecuteAssembly(original);
      WriteResult("original-exited",code);
      return code;
    } catch(Exception error) {
      RecordException(error);
      try { WriteResult("original-or-host-exception",-1); } catch { }
      return 5;
    }
  }
}
'@
    $hostSource.Replace('__GUI_AUTOMATION_MODE__',$GuiAutomation) | Set-Content -LiteralPath $source -Encoding ASCII
    # The generated contract is the exact compilation closure, including launch-only.
    # Copy only repository-owned, bounded leaf files into the private compiler directory.
    $compilerSources=@($source)
    foreach($name in @(Get-HtkkNativeCompileInputs -Mode $GuiAutomation)) {
      if($name -cnotmatch '\AHtkk[A-Za-z0-9]+\.cs\z') { throw 'Invalid compiler source contract.' }
      $inputPath=Join-Path $PSScriptRoot $name
      $inputFile=Get-Item -LiteralPath $inputPath
      if($inputFile.PSIsContainer -or ($inputFile.Attributes -band [IO.FileAttributes]::ReparsePoint) -or $inputFile.Length -gt 524288) { throw 'Invalid compiler source file.' }
      $copiedPath=Join-Path $directory $name
      [IO.File]::WriteAllText($copiedPath,[IO.File]::ReadAllText($inputPath,[Text.Encoding]::UTF8),[Text.UTF8Encoding]::new($true))
      $compilerSources+= $copiedPath
    }
    '<?xml version="1.0"?><configuration><startup><supportedRuntime version="v2.0.50727"/></startup></configuration>' | Set-Content -LiteralPath $hostConfig -Encoding ASCII
    $safe.compilerJobCleanupVerified=$false
    $compilerRun=Invoke-HtkkBoundedCompiler -Executable $compiler -WorkingDirectory $directory -Arguments (@('/nologo','/target:winexe','/platform:x86','/optimize+',('/out:'+$program),'/reference:System.Windows.Forms.dll')+$compilerSources) -TimeoutMilliseconds 30000
    $safe.compilerJobCleanupVerified=$compilerRun.jobCleanupVerified;$safe.compilerExitCode=$compilerRun.exitCode;$safe.compilerErrorCodes=$compilerRun.compilerErrorCodes
    if(-not $compilerRun.jobCleanupVerified -or $compilerRun.status -notin @('exited','process-timeout')){$safe.status='host-or-tool-failure';return $safe}
    if($compilerRun.timedOut){$safe.status='compile-timeout';return $safe}
    if(-not $compilerRun.diagnosticsVerified){$safe.status='host-or-tool-failure';return $safe}
    if($safe.compilerExitCode -ne 0 -or -not(Test-Path -LiteralPath $program -PathType Leaf)){$safe.status='compile-failed';return $safe}
    # Guard again after compilation, before returning anything launchable.
    if((Get-FileHash -LiteralPath $original -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expectedExe -or (Get-FileHash -LiteralPath $business -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expectedBusiness -or (Get-FileHash -LiteralPath $originalConfig -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expectedConfig) { $safe.status='source-changed-during-prepare'; return $safe }
    $safe.hostPath=$program; $safe.hostSha256=(Get-FileHash -LiteralPath $program -Algorithm SHA256).Hash.ToLowerInvariant()
    $safe.hostConfigPath=$hostConfig; $safe.resultPath=$resultFile; $safe.guiAutomationResultPath=$automationResultFile; $safe.guiAutomationPermitPath=$automationPermitFile
    $safe.createdPaths=$owned; $safe.compilerDirectory=$directory; $safe.status='prepared'; $prepared=$true
    return $safe
  } catch { $safe.status='host-or-tool-failure'; return $safe }
  finally {
    if(-not $prepared) {
      foreach($path in $owned) { if(Test-Path -LiteralPath $path) { Remove-Item -LiteralPath $path -Force -ErrorAction SilentlyContinue } }
      if($directory) { Remove-Item -LiteralPath $directory -Recurse -Force -ErrorAction SilentlyContinue }
    }
  }
}
