# No tax data, credentials, public screenshots or installer logs are published.
[CmdletBinding()]
param([switch]$InstallAndProbe,[ValidateSet('original','clr2-x86-reference')][string]$RuntimeHost='original',[switch]$AcknowledgeRegistration,[switch]$SyntheticLogin,[ValidateSet('none','inspect','profile-save','gtgt-inspect','gtgt-sheet-inspect','gtgt-amendment-inspect','gtgt-amendment-open-inspect','gtgt-annex12-inspect','gtgt-annex12-row-inspect','gtgt-annex12-input-inspect','gtgt-annex12-numeric-inspect','gtgt-annex12-export-inspect','gtgt-export-inspect','gtgt-roundtrip-inspect','gtgt-web-import-inspect')][string]$GuiAutomation='none')
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
Set-StrictMode -Version Latest
$report = [ordered]@{
  version = '5.8.1'; stage = 'started'; sourceHashesVerified = $false; sourceDownloads = @()
  runtimeHost = $RuntimeHost; customReferenceHost = $RuntimeHost -eq 'clr2-x86-reference'
  referenceHostPreparation = $null; referenceHostResult = $null; originalSourcesUnmodified = $null
  childEnvironmentPolicy = 'not-launched'; hostOutboundBlocked = $false; originalOutboundBlocked = $false
  officialCabMatchesMirror = $false; msiAuthenticodeValid = $false
  netFx35Present = $false; installExitCode = $null; installerProcess = $null
  processStarted = $false; processAliveAfterWait = $false; windowObserved = $false
  runnerSessionId = $null; appSessionId = $null; userInteractive = [Environment]::UserInteractive
  registrationAcknowledgementEnabled = [bool]$AcknowledgeRegistration; registrationDialogPosts = 0; registrationProcessesTracked = 0
  registrationExitCodes = @(); registrationNonzeroExitCount = 0; registrationUnverifiedExitCount = 0; registrationPostFailureCount = 0; registrationCloseFallbackPosts = 0; registrationCloseFallbackFailures = 0; registrationAcknowledgementLimitReached = $false
  appArchitecture = 'unknown'; preexistingHtkkProcessCount = 0; preexistingHtkkSameSessionCount = 0
  descendantScope = 'created-at-or-after-root-start'; verifiedMicrosoftChildImages = @(); unknownChildImageInspectionFailures = 0
  threadDesktop = 'unavailable'; desktopWindowScope = 'current-thread-desktop'
  appVisibleWindowCount = 0; appHiddenWindowCount = 0; allVisibleWindowCount = 0
  childProcessCount = 0; childVisibleWindowCount = 0; childHiddenWindowCount = 0
  mainWindowHandlePresent = $false; startupWaitSeconds = 0; startupContext = 'not-probed'
  uiaStatus = 'not-probed'; uiaWindowCount = 0; uiaControlCount = 0; loginReady = $false
  uiaControlTypeCounts = @{}; uiaAllowedControlIds = @(); uiaStaticLabels = @()
  uiaHelperEncoding = 'utf8-bom'; uiaHelperExitCode = $null; uiaHelperParseErrorCount = 0; uiaHelperFailureCategory = 'not-probed'; uiaHelperPhase = 'not-probed'
  descendantProcessKinds = @{ HTKK = 0; msiexec = 0; WerFault = 0; rundll32 = 0; dllhost = 0; console = 0; shell = 0; browser = 0; updater = 0; debugger = 0; errorReporting = 0; other = 0 }
  ownedWindowKinds = @{}; nativeDialogCueCounts = @{}; rootAppWindowObserved = $false; uiaWindowCategories = @()
  uiaLegacyRoleCounts = @{}; uiaLegacyPatternAvailable = $false; uiaProviderProcessMismatchCount = 0; uiaViews = @()
  applicationEvents = $null
  privateSyntheticLoginDiagnostic = $null
  privateRegistrationDiagnostic = $null
  privateGtgtExportEvidence = $null
  privateWebNativeOutputEvidence = $null
  syntheticLoginRequested = [bool]$SyntheticLogin; syntheticLogin = $null
  guiReferenceAutomationMode = $GuiAutomation; guiReferenceAutomation = $null
  commonHeaderOracle = $null
  profileAliasOracle = $null
  taxIdOracle = $null
  runtimeRoundTrip = $false; taxDataUsed = $false; screenshotsPublished = $false
}
$work = Join-Path $env:RUNNER_TEMP ('htkk-probe-' + [guid]::NewGuid().ToString('N'))
$rootStartTime = $null
$installerStopped=$true
$installerCredentialsSafe=$true
$uiaHelpersStopped=$true
. (Join-Path $PSScriptRoot 'Invoke-HtkkBoundedNativeProcess.ps1')
. (Join-Path $PSScriptRoot 'Invoke-HtkkPinnedDownload.ps1')
$process = $null; $referencePreparation = $null; $referenceOwnedFiles = @(); $referenceHostName = ''
$firewallNames = [Collections.Generic.List[string]]::new()
$registrationProcesses = [Collections.Generic.List[Diagnostics.Process]]::new()
$registrationKeys = [Collections.Generic.HashSet[string]]::new()
function Assert-Hash([string]$Path, [string]$Expected) {
  if ((Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $Expected) { throw 'SOURCE_HASH_MISMATCH' }
}
function Get-PinnedFile([string]$Url, [string]$Path, [string]$Expected) {
  # Public HTTPS sources only; no relay token, auth header or TLS override.
  $download=Invoke-HtkkPinnedDownload -Url $Url -Destination $Path -ExpectedSha256 $Expected
  $report.sourceDownloads+=@($download)
  if($download.status -eq 'verified'){return}
  if(-not $download.partialFileRemoved){throw 'SOURCE_DOWNLOAD_CLEANUP_NOT_VERIFIED'}
  $code=switch($download.failureCategory){
    'hash' {'SOURCE_HASH_MISMATCH'}
    'dns' {'SOURCE_DOWNLOAD_DNS'}
    'tls' {'SOURCE_DOWNLOAD_TLS'}
    'http' {'SOURCE_DOWNLOAD_HTTP'}
    'timeout' {'SOURCE_DOWNLOAD_TIMEOUT'}
    'connect' {'SOURCE_DOWNLOAD_CONNECT'}
    default {'SOURCE_DOWNLOAD_TOOL'}
  }
  throw $code
}
# Never forward runner/service/GitHub credentials to either launch mode.
function Start-HtkkCleanProcess([string]$Executable,[string]$ProjectDirectory,[bool]$IsX86Reference) {
  $info=[Diagnostics.ProcessStartInfo]::new()
  $info.FileName=$Executable; $info.WorkingDirectory=$ProjectDirectory; $info.UseShellExecute=$false
  $info.CreateNoWindow=$false; $info.RedirectStandardOutput=$true; $info.RedirectStandardError=$true
  $info.Environment.Clear()
  foreach($key in @('SystemRoot','WINDIR','SystemDrive','TEMP','TMP','PATH','APPDATA','LOCALAPPDATA','USERPROFILE','ProgramData','COMSPEC','PROCESSOR_ARCHITECTURE','PROCESSOR_ARCHITEW6432','NUMBER_OF_PROCESSORS')) {
    $value=[Environment]::GetEnvironmentVariable($key)
    if($null -ne $value) { $info.Environment[$key]=$value }
  }
  # Match the standard architecture variables that a native 32-bit launch sees.
  if($IsX86Reference) {
    $info.Environment['PROCESSOR_ARCHITECTURE']='x86'
    if([Environment]::Is64BitOperatingSystem) { $nativeArchitecture=[Environment]::GetEnvironmentVariable('PROCESSOR_ARCHITECTURE'); if($nativeArchitecture) { $info.Environment['PROCESSOR_ARCHITEW6432']=$nativeArchitecture } }
  }
  return [Diagnostics.Process]::Start($info)
}
function Get-HtkkSafeReferenceResult([string]$ResultPath) {
  $invalid=[ordered]@{ status='result-unavailable'; mode='custom-x86-clr2-reference-host' }
  try {
    if(-not (Test-Path -LiteralPath $ResultPath -PathType Leaf)) { return $invalid }
    if((Get-Item -LiteralPath $ResultPath).Length -gt 4096) { $invalid.status='result-invalid'; return $invalid }
    $result=Get-Content -LiteralPath $ResultPath -Raw -Encoding UTF8 | ConvertFrom-Json -AsHashtable
    $statuses=@('unsupported-runtime','source-hash-mismatch','original-starting','original-exited','original-or-host-exception')
    $categories=@('none','bitness-load','native-library-missing','type-initialization','type-load','file-not-found','assembly-load','directory-not-found','com-exception','access-denied','format','null-reference','access-violation','invalid-operation','argument','security','remoting','other-standard-or-unclassified')
    if($result.format -ne 'htkk-x86-reference-host-v1' -or $result.mode -ne 'custom-x86-clr2-reference-host' -or $result.status -notin $statuses -or $result.runtime -notin @('clr2','unsupported') -or $result.bitness -notin @(32,64) -or $result.apartment -notin @('sta','unsupported') -or $result.launchMechanism -ne 'secondary-AppDomain.ExecuteAssembly' -or $result.exceptionCategory -notin $categories -or $result.outerExceptionCategory -notin $categories -or [string]$result.hresult -notmatch '^(?:none|unavailable|0x[0-9a-f]{8})$' -or $result.runtimeRoundTrip -ne $false) { $invalid.status='result-invalid'; return $invalid }
    foreach($key in @('originalExeHashVerified','businessDllHashVerified','originalConfigHashVerified')) { if($result[$key] -isnot [bool]) { $invalid.status='result-invalid'; return $invalid } }
    if(($result.originalExitCode -isnot [int] -and $result.originalExitCode -isnot [long]) -or $result.originalExitCode -lt [int]::MinValue -or $result.originalExitCode -gt [int]::MaxValue) { $invalid.status='result-invalid'; return $invalid }
    # Reconstruct an allowlisted object; never return arbitrary fields from disk.
    return [ordered]@{ status=$result.status; mode=$result.mode; runtime=$result.runtime; bitness=$result.bitness; apartment=$result.apartment; originalExeHashVerified=$result.originalExeHashVerified; businessDllHashVerified=$result.businessDllHashVerified; originalConfigHashVerified=$result.originalConfigHashVerified; launchMechanism=$result.launchMechanism; exceptionCategory=$result.exceptionCategory; outerExceptionCategory=$result.outerExceptionCategory; hresult=$result.hresult; originalExitCode=$result.originalExitCode; runtimeRoundTrip=$false }
  } catch { $invalid.status='result-invalid'; return $invalid }
}
# Only aggregate native GUI counts are exposed: no titles, class names, handles or identifiers.
function Initialize-WindowDiagnostics {
  Add-Type -TypeDefinition @'
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;
public static class HtkkWindowDiagnostics {
  private delegate bool EnumProc(IntPtr window, IntPtr unused);
  [DllImport("user32.dll")] private static extern bool EnumWindows(EnumProc callback, IntPtr unused);
  [DllImport("user32.dll")] private static extern bool IsWindowVisible(IntPtr window);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] private static extern int GetClassName(IntPtr window, StringBuilder value, int size);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] private static extern int GetWindowText(IntPtr window, StringBuilder text, int size);
  [DllImport("user32.dll", SetLastError=true)] private static extern bool PostMessage(IntPtr window, uint message, IntPtr wParam, IntPtr lParam);
  // Called only for a retained, verified Microsoft regsvr32 process created by this probe.
  // Keep the HWND privately so fallback can only close the SAME modal after IDOK.
  private static readonly Dictionary<int,IntPtr> PendingRegistrationWindows=new Dictionary<int,IntPtr>();
  // Return 0=no exact dialog, 1=exact dialog only, 2=IDOK posted, 3=same-modal WM_CLOSE posted.
  // No text or HWND is returned to PowerShell or public logs.
  public static int RegistrationDialog(int approvedProcess, bool acknowledge, bool closeFallback) {
    int outcome=0;
    EnumProc callback=(window,unused)=> {
      uint owner; GetWindowThreadProcessId(window,out owner);
      if (owner!=(uint)approvedProcess || !IsWindowVisible(window)) return true;
      var cls=new StringBuilder(64); GetClassName(window,cls,cls.Capacity);
      if (!String.Equals(cls.ToString(),"#32770",StringComparison.Ordinal)) return true;
      var caption=new StringBuilder(64); GetWindowText(window,caption,caption.Capacity);
      if (!String.Equals(caption.ToString(),"RegSvr32",StringComparison.OrdinalIgnoreCase)) return true;
      outcome=1;
      // Never IDYES or an arbitrary/default button. The fallback requires an earlier
      // IDOK on this exact HWND and is invoked only once by the retained-process caller.
      if (closeFallback) {
        IntPtr original;
        if (PendingRegistrationWindows.TryGetValue(approvedProcess,out original) && original==window) {
          PendingRegistrationWindows.Remove(approvedProcess);
          if (PostMessage(window,0x0010,IntPtr.Zero,IntPtr.Zero)) outcome=3;
        }
      } else if (acknowledge && PostMessage(window,0x0111,new IntPtr(1),IntPtr.Zero)) {
        PendingRegistrationWindows[approvedProcess]=window; outcome=2;
      }
      return false;
    };
    EnumWindows(callback,IntPtr.Zero); GC.KeepAlive(callback); return outcome;
  }
  [DllImport("user32.dll")] private static extern uint GetWindowThreadProcessId(IntPtr window, out uint process);
  [DllImport("user32.dll")] private static extern bool EnumChildWindows(IntPtr parent, EnumProc callback, IntPtr unused);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] private static extern IntPtr SendMessageTimeout(IntPtr window, uint message, UIntPtr count, StringBuilder text, uint flags, uint timeout, out UIntPtr result);
  [DllImport("kernel32.dll")] private static extern uint GetCurrentThreadId();
  [DllImport("kernel32.dll", SetLastError=true)] private static extern bool IsWow64Process(IntPtr process, out bool wow64);
  public static string Architecture(IntPtr process) {
    if (!Environment.Is64BitOperatingSystem) return "x86";
    bool wow64; return IsWow64Process(process, out wow64) ? (wow64 ? "x86" : "x64") : "unknown";
  }
  [DllImport("user32.dll")] private static extern IntPtr GetThreadDesktop(uint thread);
  [DllImport("user32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
  private static extern bool GetUserObjectInformation(IntPtr handle, int index, StringBuilder value, int size, out int needed);
  public static string DesktopKind() {
    var name = new StringBuilder(256); int needed;
    if (!GetUserObjectInformation(GetThreadDesktop(GetCurrentThreadId()), 2, name, name.Capacity * 2, out needed)) return "unavailable";
    // Do not publish an arbitrary desktop name: it may contain user-specific data.
    if (String.Equals(name.ToString(), "Default", StringComparison.OrdinalIgnoreCase)) return "default";
    if (String.Equals(name.ToString(), "Winlogon", StringComparison.OrdinalIgnoreCase)) return "winlogon";
    return "other";
  }
  // Class names are inspected only to return these fixed public categories.
  // Neither raw names, handles nor process identifiers leave this method.
  public static Dictionary<string,int> OwnedWindowKinds(int appProcess, int[] descendants) {
    var owners = new HashSet<int>(descendants); owners.Add(appProcess);
    var kinds = new Dictionary<string,int>();
    EnumProc callback = (window, unused) => {
      uint owner; GetWindowThreadProcessId(window, out owner);
      if (!owners.Contains((int)owner) || !IsWindowVisible(window)) return true;
      var text = new StringBuilder(256); GetClassName(window, text, text.Capacity);
      var name = text.ToString(); string kind = "other";
      if (name == "ConsoleWindowClass" || name == "CASCADIA_HOSTING_WINDOW_CLASS") kind = "console";
      else if (name.StartsWith("WindowsForms10.", StringComparison.Ordinal)) kind = "winforms";
      else if (name.StartsWith("Chrome_WidgetWin_", StringComparison.Ordinal) || name == "IEFrame") kind = "browser";
      else if (name == "#32770") kind = "win32-dialog";
      else if (name.StartsWith("HwndWrapper", StringComparison.Ordinal)) kind = "wpf";
      else if (name == "ApplicationFrameWindow") kind = "application-frame";
      if (!kinds.ContainsKey(kind)) kinds[kind] = 0; kinds[kind]++;
      return true;
    };
    if (!EnumWindows(callback, IntPtr.Zero)) throw new InvalidOperationException("WINDOW_ENUMERATION_FAILED");
    GC.KeepAlive(callback); return kinds;
  }
  // Native dialog labels are classified in memory only. Never read edit/combo
  // controls or return text, titles, handles, class names or identifiers.
  public static Dictionary<string,int> FixedDialogCues(int appProcess, int[] descendants) {
    var owners = new HashSet<int>(descendants); owners.Add(appProcess);
    var cues = new Dictionary<string,int>(); var clock = System.Diagnostics.Stopwatch.StartNew(); int inspected = 0;
    Action<IntPtr> inspect = window => {
      if (inspected++ >= 100 || clock.Elapsed.TotalSeconds >= 5) return;
      var className = new StringBuilder(256); GetClassName(window, className, className.Capacity);
      var cls = className.ToString();
      if (cls != "#32770" && cls != "Static" && cls != "Button" && cls != "SysLink") return;
      var text = new StringBuilder(2048); UIntPtr unused;
      if (SendMessageTimeout(window, 0x000D, new UIntPtr((uint)text.Capacity), text, 3, 100, out unused) == IntPtr.Zero) return;
      var name = text.ToString().ToLowerInvariant(); var matches = new List<string>();
      if (name.Contains("just-in-time") || name.Contains("jit debugger") || name.Contains("choose debugger")) matches.Add("jit-debugger");
      if (name.Contains("unhandled exception") || name.Contains("unhandled microsoft .net")) matches.Add("unhandled-exception");
      if (name.Contains("class not registered") || name.Contains("0x80040154") || name.Contains("comexception") || name.Contains("activex")) matches.Add("com-or-activex");
      if (name.Contains("badimageformatexception") || name.Contains("0x8007000b") || name.Contains("incorrect format")) matches.Add("bitness-load");
      if (name.Contains("could not load file or assembly") || name.Contains("filenotfoundexception") || name.Contains("fileloadexception") || name.Contains("typeloadexception")) matches.Add("assembly-load");
      if (name.Contains(".net framework") || name.Contains("clr error")) matches.Add("dotnet-runtime");
      if (name.Contains("program compatibility") || name.Contains("compatibility assistant")) matches.Add("compatibility");
      foreach (var cue in matches) { if (!cues.ContainsKey(cue)) cues[cue] = 0; cues[cue]++; }
    };
    EnumProc child = (window, unused) => { inspect(window); return inspected < 100 && clock.Elapsed.TotalSeconds < 5; };
    EnumProc top = (window, unused) => {
      uint owner; GetWindowThreadProcessId(window, out owner);
      if (owners.Contains((int)owner) && IsWindowVisible(window)) { inspect(window); EnumChildWindows(window, child, IntPtr.Zero); }
      return inspected < 100 && clock.Elapsed.TotalSeconds < 5;
    };
    EnumWindows(top, IntPtr.Zero); GC.KeepAlive(top); GC.KeepAlive(child); return cues;
  }
  // all-visible, app-visible, app-hidden, descendant-visible, descendant-hidden
  public static int[] Counts(int appProcess, int[] descendants) {
    var children = new HashSet<int>(descendants); var counts = new int[5];
    EnumProc callback = (window, unused) => {
      uint owner; GetWindowThreadProcessId(window, out owner);
      bool visible = IsWindowVisible(window);
      if (visible) counts[0]++;
      if (owner == (uint)appProcess) counts[visible ? 1 : 2]++;
      else if (children.Contains((int)owner)) counts[visible ? 3 : 4]++;
      return true;
    };
    if (!EnumWindows(callback, IntPtr.Zero)) throw new InvalidOperationException("WINDOW_ENUMERATION_FAILED");
    GC.KeepAlive(callback); return counts;
  }
}
'@
}
# Read a bounded local Application log window. Event text/XML stays in memory
# and is never returned, written to files or sent to the public console.
function Get-HtkkSafeApplicationEvents([datetime]$ApplicationStartTime,[string]$ReferenceHostName='') {
  $safe = [ordered]@{ status = 'not-queried'; queriedCount = 0; matchedEventCount = 0; providerQueryFailureCount = 0; bounded = $false; providers = @(); eventIds = @(); categories = @(); hresults = @() }
  $providerGroups = @{
    '.NET Runtime' = 'dotnet-runtime'
    '.NET Runtime 2.0 Error Reporting' = 'dotnet-runtime-v2'
    'Application Error' = 'application-error'
    'Windows Error Reporting' = 'windows-error-reporting'
  }
  $categoryPatterns = [ordered]@{
    'bitness-load' = '(?i)BadImageFormatException|0x8007000B|incorrect format'
    'com-class-not-registered' = '(?i)class not registered|0x80040154'
    'com-exception' = '(?i)COMException'
    'assembly-load' = '(?i)could not load file or assembly|FileLoadException'
    'file-not-found' = '(?i)FileNotFoundException|0x80070002'
    'native-library-missing' = '(?i)DllNotFoundException'
    'directory-not-found' = '(?i)DirectoryNotFoundException'
    'type-initialization' = '(?i)TypeInitializationException'
    'type-load' = '(?i)TypeLoadException'
    'format' = '(?i)(?<![A-Za-z])(?:System\.)?FormatException\b'
    'null-reference' = '(?i)NullReferenceException'
    'access-violation' = '(?i)AccessViolationException|0xc0000005'
    'access-denied' = '(?i)UnauthorizedAccessException|0x80070005'
    'invalid-operation' = '(?i)InvalidOperationException'
    'argument' = '(?i)ArgumentException|ArgumentOutOfRangeException'
    'index-range' = '(?i)IndexOutOfRangeException'
    'security' = '(?i)SecurityException'
    'native-exception' = '(?i)SEHException|Win32Exception'
    'stack-overflow' = '(?i)StackOverflowException'
    'out-of-memory' = '(?i)OutOfMemoryException'
    'clr-managed-exception' = '(?i)0xe0434352|0xe0434f4d'
  }
  try {
    $collected = [System.Collections.Generic.List[object]]::new()
    $endTime = Get-Date
    foreach ($providerName in $providerGroups.Keys) {
      try {
        # Query separately so an absent legacy provider cannot hide events from
        # the other providers. Four queries x25 events is the hard record bound.
        $filter = @{ LogName = 'Application'; ProviderName = $providerName; StartTime = $ApplicationStartTime.AddSeconds(-1); EndTime = $endTime }
        $batch = @(Get-WinEvent -FilterHashtable $filter -MaxEvents 25 -ErrorAction Stop)
        if ($batch.Count -ge 25) { $safe.bounded = $true }
        foreach ($record in $batch) { $collected.Add($record) }
      } catch {
        if ($_.FullyQualifiedErrorId -notlike 'NoMatchingEventsFound*') { $safe.providerQueryFailureCount++ }
      }
    }
    $items = @($collected.ToArray() | Sort-Object TimeCreated -Descending)
    $safe.queriedCount = $items.Count
    $matchedCount = 0
    $providers = [System.Collections.Generic.HashSet[string]]::new()
    $eventIds = [System.Collections.Generic.HashSet[int]]::new()
    $categories = [System.Collections.Generic.HashSet[string]]::new()
    $codes = [System.Collections.Generic.HashSet[string]]::new()
    foreach ($item in $items) {
      if (-not $providerGroups.ContainsKey([string]$item.ProviderName)) { continue }
      $message = ''; $xml = ''
      try { $message = [string]$item.Message } catch { }
      try { $xml = [string]$item.ToXml() } catch { }
      $privateText = $message + "`n" + $xml
      # Exclude unrelated events even from the allowlisted providers. Matching
      # only the executable name is intentional; no path or username is emitted.
      $matchesOriginal=$privateText -match '(?i)(?<![A-Za-z0-9_])HTKK\.exe(?![A-Za-z0-9_])'
      $matchesReference=$false
      if($ReferenceHostName -match '^HTKK\.X86ReferenceHost\.[a-f0-9]{32}\.exe$') { $matchesReference=$privateText -match ('(?i)(?<![A-Za-z0-9_])'+[regex]::Escape($ReferenceHostName)+'(?![A-Za-z0-9_])') }
      if(-not ($matchesOriginal -or $matchesReference)) { continue }
      if ($matchedCount -ge 10) { $safe.bounded = $true; break }
      foreach ($entry in $categoryPatterns.GetEnumerator()) {
        if ($privateText -match $entry.Value) { $categories.Add([string]$entry.Key) | Out-Null }
      }
      # HRESULT/NTSTATUS-shaped failure codes only: eight hex digits with the
      # high bit set. Exclude 64-bit addresses, arbitrary strings and success IDs.
      foreach ($code in [regex]::Matches($privateText, '(?i)(?<![A-Za-z0-9])0x[89a-f][0-9a-f]{7}(?![0-9a-f])')) {
        if ($codes.Count -ge 10) { break }
        $codes.Add($code.Value.ToLowerInvariant()) | Out-Null
      }
      $providers.Add($providerGroups[[string]$item.ProviderName]) | Out-Null
      $eventIds.Add([int]$item.Id) | Out-Null
      $matchedCount++
    }
    $safe.matchedEventCount = $matchedCount
    $safe.providers = @($providers | Sort-Object); $safe.eventIds = @($eventIds | Sort-Object)
    $safe.categories = @($categories | Sort-Object); $safe.hresults = @($codes | Sort-Object)
    $safe.status = if ($safe.providerQueryFailureCount -eq $providerGroups.Count) { 'unavailable' } elseif ($items.Count -eq 0) { 'no-events' } elseif ($safe.providerQueryFailureCount -gt 0) { 'partial' } else { 'scanned' }
  } catch {
    # A no-match result is distinct from permissions/provider/query failure.
    $safe.status = if ($_.FullyQualifiedErrorId -like 'NoMatchingEventsFound*') { 'no-events' } else { 'unavailable' }
  }
  return $safe
}
function Get-DescendantProcessIds([int]$AppProcessId, [datetime]$RootStartTime) {
  # Creation time prevents an older process whose parent PID was reused from
  # becoming a false descendant. No command lines or arbitrary process data leave this function.
  $snapshot = @(Get-CimInstance Win32_Process -Property ProcessId,ParentProcessId,CreationDate | Select-Object -First 4096)
  $births = @{}; $births[$AppProcessId] = $RootStartTime.ToUniversalTime()
  $found = [System.Collections.Generic.HashSet[int]]::new()
  $found.Add($AppProcessId) | Out-Null
  $round = 0
  do {
    $added = $false; $round++
    foreach ($entry in $snapshot) {
      if ($null -eq $entry.CreationDate) { continue }
      $parentId = [int]$entry.ParentProcessId; $childId = [int]$entry.ProcessId
      if (-not $found.Contains($parentId) -or $found.Contains($childId)) { continue }
      $created = ([datetime]$entry.CreationDate).ToUniversalTime()
      if ($created -lt $births[$parentId]) { continue }
      if ($found.Add($childId)) { $births[$childId] = $created; $added = $true }
    }
  } while ($added -and $round -lt 96)
  $found.Remove($AppProcessId) | Out-Null
  return $found | ForEach-Object { [int]$_ }
}
function Get-VerifiedMicrosoftImageBasename([int]$ProcessId) {
  # Only a signed Microsoft system-image basename may be returned. No path,
  # arbitrary process name, command line, certificate text or user information is published.
  $imagePath = (Get-Process -Id $ProcessId -ErrorAction Stop).Path
  if ([string]::IsNullOrWhiteSpace($imagePath)) { return $null }
  $fullPath = [IO.Path]::GetFullPath($imagePath)
  $basename = [IO.Path]::GetFileName($fullPath)
  if ($basename -notmatch '^[A-Za-z][A-Za-z0-9._-]{0,59}\.exe$' -or $basename -match '^(?i:gh[pousr]_|github_pat_|token|secret|password|authorization)') { return $null }
  $inside = $false
  $windowsRoot = [IO.Path]::GetFullPath($env:WINDIR).TrimEnd('\') + '\'
  if ($fullPath.StartsWith($windowsRoot,[StringComparison]::OrdinalIgnoreCase)) { $inside = $true }
  foreach ($variable in @('ProgramFiles','ProgramFiles(x86)','CommonProgramFiles','CommonProgramFiles(x86)')) {
    $base = [Environment]::GetEnvironmentVariable($variable)
    if ([string]::IsNullOrWhiteSpace($base)) { continue }
    $prefix = [IO.Path]::GetFullPath($base).TrimEnd('\') + '\'
    if ($fullPath.StartsWith($prefix,[StringComparison]::OrdinalIgnoreCase)) {
      $firstDirectory = $fullPath.Substring($prefix.Length).Split('\')[0]
      if ($firstDirectory -match '^Microsoft(?:[ .].*)?$') { $inside = $true }
    }
  }
  if (-not $inside) { return $null }
  $signature = Get-AuthenticodeSignature -LiteralPath $fullPath -ErrorAction Stop
  if ($signature.Status -ne 'Valid' -or $null -eq $signature.SignerCertificate -or $signature.SignerCertificate.Subject -notmatch '(?i)(?:^|,\s*)O=Microsoft Corporation(?:,|$)') { return $null }
  # Signed OriginalFilename prevents an arbitrary renamed image from becoming an output channel.
  $originalName = [IO.Path]::GetFileName([Diagnostics.FileVersionInfo]::GetVersionInfo($fullPath).OriginalFilename)
  if (-not [string]::Equals($basename,$originalName,[StringComparison]::OrdinalIgnoreCase)) { return $null }
  return $basename.ToLowerInvariant()
}
# Optional acknowledgement is confined to freshly scoped Microsoft regsvr32 descendants.
# A matching caption is not a success claim: every posted process must subsequently exit 0.
function Invoke-HtkkRegistrationAcknowledgement([int[]]$DescendantIds,[int]$AppProcessId,[datetime]$RootStartTime) {
  foreach ($candidateId in @($DescendantIds | Select-Object -First 64)) {
    $candidate = $null; $retained = $false
    try {
      $candidate = Get-Process -Id $candidateId -ErrorAction Stop
      $null = $candidate.Handle # Retain identity/exit information before touching a dialog.
      if ($candidate.HasExited -or $candidate.StartTime.ToUniversalTime() -lt $RootStartTime.ToUniversalTime()) { continue }
      $fresh = @(Get-DescendantProcessIds -AppProcessId $AppProcessId -RootStartTime $RootStartTime)
      if ($candidate.Id -notin $fresh) { continue }
      $key = [string]$candidate.Id + ':' + [string]$candidate.StartTime.ToUniversalTime().Ticks
      if ($registrationKeys.Contains($key)) { continue }
      $imagePath = [IO.Path]::GetFullPath($candidate.Path)
      $system32 = [IO.Path]::GetFullPath((Join-Path $env:WINDIR 'System32\regsvr32.exe'))
      $syswow64 = [IO.Path]::GetFullPath((Join-Path $env:WINDIR 'SysWOW64\regsvr32.exe'))
      if (-not ([string]::Equals($imagePath,$system32,[StringComparison]::OrdinalIgnoreCase) -or [string]::Equals($imagePath,$syswow64,[StringComparison]::OrdinalIgnoreCase))) { continue }
      if ((Get-VerifiedMicrosoftImageBasename -ProcessId $candidate.Id) -ne 'regsvr32.exe' -or $candidate.HasExited) { continue }
      if ($report.registrationDialogPosts -ge 16) {
        if ([HtkkWindowDiagnostics]::RegistrationDialog($candidate.Id,$false,$false) -eq 1) { $report.registrationAcknowledgementLimitReached = $true }
        continue
      }
      $outcome = [HtkkWindowDiagnostics]::RegistrationDialog($candidate.Id,$true,$false)
      if ($outcome -eq 2) {
        $registrationKeys.Add($key) | Out-Null
        $registrationProcesses.Add($candidate); $retained = $true
        $report.registrationDialogPosts++; $report.registrationProcessesTracked = $registrationProcesses.Count
        # Bounded wait only; a still-running process remains retained for later checks.
        $candidate.WaitForExit(1000) | Out-Null
        if (-not $candidate.HasExited) {
          # A prior private diagnostic showed the standard successful-registration
          # information popup. Revalidate scope, then close only that same pending HWND.
          $freshForClose = @(Get-DescendantProcessIds -AppProcessId $AppProcessId -RootStartTime $RootStartTime)
          if ($candidate.Id -in $freshForClose -and (Get-VerifiedMicrosoftImageBasename -ProcessId $candidate.Id) -eq 'regsvr32.exe') {
            $closeOutcome = [HtkkWindowDiagnostics]::RegistrationDialog($candidate.Id,$false,$true)
            if ($closeOutcome -eq 3) {
              $report.registrationCloseFallbackPosts++
              $candidate.WaitForExit(1000) | Out-Null
            } elseif ($closeOutcome -eq 1) { $report.registrationCloseFallbackFailures++ }
          }
        }
      } elseif ($outcome -eq 1) { $report.registrationPostFailureCount++ }
    } catch { } # No path, PID, caption, error text or command line is published.
    finally { if ($null -ne $candidate -and -not $retained) { $candidate.Dispose() } }
  }
}
function Update-HtkkRegistrationResults([int]$WaitMilliseconds=0) {
  $codes = [Collections.Generic.List[int]]::new()
  $nonzero = 0; $unverified = 0
  foreach ($registration in $registrationProcesses) {
    try {
      if (-not $registration.HasExited -and $WaitMilliseconds -gt 0) { $registration.WaitForExit([Math]::Min($WaitMilliseconds,1000)) | Out-Null }
      if (-not $registration.HasExited) { $unverified++; continue }
      $code = $registration.ExitCode
      if ($code -ge 0 -and $code -le 5) { $codes.Add([int]$code); if ($code -ne 0) { $nonzero++ } }
      else { $unverified++ }
    } catch { $unverified++ }
  }
  $report.registrationExitCodes = @($codes.ToArray())
  $report.registrationNonzeroExitCount = $nonzero; $report.registrationUnverifiedExitCount = $unverified
}
# Isolated Windows PowerShell helper: UIAutomation is a desktop .NET Framework assembly.
# Only process-scoped UIA controls are inspected, never ValuePattern or arbitrary names in output.
function Read-HtkkUiaHelperPhase([string]$PhasePath) {
  $phases=@('not-started','starting','assembly-loading','initializing','root-enumerating','root-scoping','traversing','result-building','provider-failed','result-writing','complete')
  try{
    if(-not(Test-Path -LiteralPath $PhasePath -PathType Leaf)){return 'unavailable'}
    $file=Get-Item -LiteralPath $PhasePath
    if($file.Length -gt 64 -or ($file.Attributes -band [IO.FileAttributes]::ReparsePoint)){return 'invalid'}
    $phase=[IO.File]::ReadAllText($PhasePath,[Text.Encoding]::UTF8).Trim()
    if($phase -cnotin $phases){return 'invalid'}
    return $phase
  }catch{return 'unavailable'}
}
function Get-HtkkSafeUiDiagnostics([int]$AppProcessId, [int[]]$Descendants, [string]$TemporaryDirectory) {
  $helper = Join-Path $TemporaryDirectory 'uia-helper.ps1'
  $resultPath = Join-Path $TemporaryDirectory 'uia-safe.json'
  $phasePath=Join-Path $TemporaryDirectory 'uia-phase.txt'
  [IO.File]::WriteAllText($phasePath,'not-started',[Text.UTF8Encoding]::new($false))
  @'
param([string]$ProcessIds, [string]$OutputFile, [string]$PhaseFile)
$ErrorActionPreference = 'Stop'
function Set-UiaPhase([string]$Phase){[IO.File]::WriteAllText($PhaseFile,$Phase,[Text.UTF8Encoding]::new($false))}
Set-UiaPhase 'starting'
Set-StrictMode -Version Latest
$result = [ordered]@{ status = 'unavailable'; windows = 0; controls = 0; loginReady = $false; types = @{}; ids = @(); labels = @(); categories = @(); legacyRoles = @{}; providerProcessMismatchCount = 0; legacyPatternAvailable = $false; views = @('children','raw-walker','control-walker','native-static-dialog') }
try {
  Set-UiaPhase 'assembly-loading'
  Add-Type -AssemblyName UIAutomationClient
  Add-Type -AssemblyName UIAutomationTypes
  Set-UiaPhase 'initializing'
  # Classic UIA assemblies may not expose LegacyIAccessiblePattern; never let
  # an unavailable optional pattern stop the raw/control child traversal.
  $legacyPatternType = [Type]::GetType('System.Windows.Automation.LegacyIAccessiblePattern, UIAutomationClient', $false)
  $legacyPatternField = if ($null -ne $legacyPatternType) { $legacyPatternType.GetField('Pattern') } else { $null }
  $legacyPattern = if ($null -ne $legacyPatternField) { $legacyPatternField.GetValue($null) } else { $null }
  $result.legacyPatternAvailable = $null -ne $legacyPattern
  $owners = [System.Collections.Generic.HashSet[int]]::new()
  foreach ($item in $ProcessIds.Split(',')) { $owners.Add([int]$item) | Out-Null }
  $ids = [System.Collections.Generic.HashSet[string]]::new()
  $labels = [System.Collections.Generic.HashSet[string]]::new()
  $categories = [System.Collections.Generic.HashSet[string]]::new()
  $allowedIds = @('cboMaSoThue','btnMaSoMoi','btnDongY','btnThoat','frmFormStart','txtMst','txtYear','chkTKQuy','OptTKThang','cboCQTCuc','cboCQTChiCuc','cmdImportXML','cmdExport','btnExport','radKetXuatXML','radKetXuatExcel')
  $allowedTypes = @('Button','Calendar','CheckBox','ComboBox','Edit','Hyperlink','Image','ListItem','List','Menu','MenuBar','MenuItem','ProgressBar','RadioButton','ScrollBar','Slider','Spinner','StatusBar','Tab','TabItem','Text','ToolBar','ToolTip','Tree','TreeItem','Custom','Group','Thumb','DataGrid','DataItem','Document','SplitButton','Window','Pane','Header','HeaderItem','Table','TitleBar','Separator')
  $staticNames = @{ 'Mã số thuế' = 'Mã số thuế'; 'Đăng nhập' = 'Đăng nhập'; 'Đăng nhập vào hệ thống' = 'Đăng nhập'; 'Mã số mới' = 'Mã số mới'; 'HTKK' = 'HTKK' }
  $queue = [System.Collections.Generic.Queue[System.Windows.Automation.AutomationElement]]::new()
  $visited = [System.Collections.Generic.HashSet[string]]::new()
  Set-UiaPhase 'root-enumerating'
  $top = [System.Windows.Automation.AutomationElement]::RootElement.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)
  Set-UiaPhase 'root-scoping'
  foreach ($window in $top) {
    try {
      if ($owners.Contains($window.Current.ProcessId)) { $queue.Enqueue($window); $result.windows++ }
    } catch { }
  }
  Set-UiaPhase 'traversing'
  $clock = [System.Diagnostics.Stopwatch]::StartNew()
  while ($queue.Count -gt 0 -and $result.controls -lt 2000 -and $clock.Elapsed.TotalSeconds -lt 10) {
    $element = $queue.Dequeue()
    try {
      # Top-level windows were scoped to known owners above. Proxy/MSAA child
      # providers can report process 0 or another host; do not discard their
      # descendants solely on that property. Never traverse another top-level.
      $runtimeId = ($element.GetRuntimeId() -join ',')
      if (-not $visited.Add($runtimeId)) { continue }
      if (-not $owners.Contains($element.Current.ProcessId)) { $result.providerProcessMismatchCount++ }
      $result.controls++
      $id = $element.Current.AutomationId
      if ($id -in $allowedIds) { $ids.Add($id) | Out-Null }
      # Names are read only for exact matching against a fixed public label allowlist.
      # Never output Name, Current.Value, title, HWND, PID, path, exception or a raw UIA node.
      $name = ([string]$element.Current.Name).Replace('&', '').Trim().TrimEnd(':').Trim()
      if ($staticNames.ContainsKey($name)) { $labels.Add($staticNames[$name]) | Out-Null }
      $legacy = $null
      try {
      if ($null -ne $legacyPattern -and $element.TryGetCurrentPattern($legacyPattern, [ref]$legacy)) {
        $legacyName = ([string]$legacy.Current.Name).Replace('&', '').Trim().TrimEnd(':').Trim()
        if ($staticNames.ContainsKey($legacyName)) { $labels.Add($staticNames[$legacyName]) | Out-Null }
        # Names are used only by the same fixed classifiers, never emitted.
        $name = $name + ' ' + $legacyName
        $role = switch ([int]$legacy.Current.Role) { 9 {'window'}; 10 {'client'}; 41 {'text'}; 42 {'edit'}; 43 {'button'}; 46 {'combo'}; default {'other'} }
        if (-not $result.legacyRoles.ContainsKey($role)) { $result.legacyRoles[$role] = 0 }; $result.legacyRoles[$role]++
      }
      } catch { }
      # Inspect fixed error/update cues without exposing the original text.
      if ($name -match '(?i)just-in-time|jit debugger|choose debugger') { $categories.Add('jit-debugger') | Out-Null }
      if ($name -match '(?i)unhandled exception|unhandled Microsoft \.NET') { $categories.Add('unhandled-exception') | Out-Null }
      if ($name -match '(?i)BadImageFormatException|0x8007000B|incorrect format') { $categories.Add('bitness-load') | Out-Null }
      if ($name -match '(?i)could not load file or assembly|FileNotFoundException|FileLoadException|TypeLoadException') { $categories.Add('assembly-load') | Out-Null }
      if ($name -match '(?i)run-time error|runtime error|application error|lỗi thời gian chạy') { $categories.Add('runtime-error') | Out-Null }
      if ($name -match '(?i)class not registered|0x80040154|COMException|ActiveX') { $categories.Add('com-or-activex') | Out-Null }
      if ($name -match '(?i)\.NET Framework|CLR error') { $categories.Add('dotnet-runtime') | Out-Null }
      if ($name -match '(?i)program compatibility|compatibility assistant') { $categories.Add('compatibility') | Out-Null }
      if ($name -match '(?i)check for updates|cập nhật|nâng cấp') { $categories.Add('updater') | Out-Null }
      if ($staticNames.ContainsKey($name)) { $labels.Add($staticNames[$name]) | Out-Null }
      $type = $element.Current.ControlType.ProgrammaticName.Replace('ControlType.', '')
      if ($type -notin $allowedTypes) { $type = 'Other' }
      if (-not $result.types.ContainsKey($type)) { $result.types[$type] = 0 }
      $result.types[$type]++
      $children = $element.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)
      foreach ($child in $children) { if ($queue.Count -lt 2000) { $queue.Enqueue($child) } }
      foreach ($walker in @([System.Windows.Automation.TreeWalker]::RawViewWalker, [System.Windows.Automation.TreeWalker]::ControlViewWalker)) {
        $walked = 0
        $child = $walker.GetFirstChild($element)
        while ($null -ne $child -and $walked -lt 200 -and $queue.Count -lt 2000 -and $clock.Elapsed.TotalSeconds -lt 10) {
          $queue.Enqueue($child); $walked++; $child = $walker.GetNextSibling($child)
        }
      }
    } catch { }
  }
  Set-UiaPhase 'result-building'
  $result.ids = @($ids | Sort-Object)
  $result.labels = @($labels | Sort-Object)
  $result.categories = @($categories | Sort-Object)
  $result.loginReady = ($ids.Contains('cboMaSoThue') -and ($ids.Contains('btnMaSoMoi') -or $labels.Contains('Mã số thuế'))) -or ($labels.Contains('Mã số thuế') -and $labels.Contains('Đăng nhập') -and $labels.Contains('Mã số mới'))
  $result.status = if ($queue.Count -gt 0) { 'bounded-partial' } else { 'scanned' }
} catch { Set-UiaPhase 'provider-failed';$result.status = 'uia-unavailable' }
Set-UiaPhase 'result-writing'
$result | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $OutputFile -Encoding UTF8
Set-UiaPhase 'complete'
'@ | Set-Content -LiteralPath $helper -Encoding utf8BOM
  $diagnostics = @{ status = 'uia-helper-failed'; windows = 0; controls = 0; loginReady = $false; types = @{}; ids = @(); labels = @(); helperEncoding = 'utf8-bom'; helperExitCode = $null; helperParseErrorCount = 0; helperFailureCategory = 'none'; helperProcessStopped = $true; helperPhase = 'not-started' }
  # Parse before execution; only the count is public, never source snippets or parser messages.
  $helperTokens = $null; $helperParseErrors = $null
  [System.Management.Automation.Language.Parser]::ParseFile($helper, [ref]$helperTokens, [ref]$helperParseErrors) | Out-Null
  $diagnostics.helperParseErrorCount = if ($null -eq $helperParseErrors) { 0 } else { @($helperParseErrors).Count }
  if ($diagnostics.helperParseErrorCount -gt 0) {
    $diagnostics.helperFailureCategory = 'preflight-parser-error'
    return $diagnostics
  }
  $legacy = Join-Path $env:WINDIR 'System32\WindowsPowerShell\v1.0\powershell.exe'
  $ownerList = (@($AppProcessId) + @($Descendants)) -join ','
  $arguments = @('-STA','-NoProfile','-NonInteractive','-ExecutionPolicy','RemoteSigned','-File',$helper,'-ProcessIds',$ownerList,'-OutputFile',$resultPath,'-PhaseFile',$phasePath)
  # Fail closed if a helper invocation itself unexpectedly throws; later calls
  # cannot overwrite a previously unverified cleanup with a safe value.
  $previousHelpersStopped=$script:uiaHelpersStopped;$script:uiaHelpersStopped=$false
  try{
    $helperRun=Invoke-HtkkBoundedNativeProcess -Executable $legacy -WorkingDirectory $TemporaryDirectory -Arguments $arguments -TimeoutMilliseconds 15000
  }finally{$diagnostics.helperPhase=Read-HtkkUiaHelperPhase -PhasePath $phasePath}
  $diagnostics.helperProcessStopped=$helperRun.processStopped -is [bool] -and $helperRun.processStopped
  $script:uiaHelpersStopped=$previousHelpersStopped -and $diagnostics.helperProcessStopped
  if(-not $diagnostics.helperProcessStopped){$diagnostics.helperFailureCategory='helper-cleanup-not-verified';return $diagnostics}
  if($helperRun.timedOut){
    $diagnostics.status='uia-timeout';$diagnostics.helperFailureCategory='helper-timeout';return $diagnostics
  }
  $diagnostics.helperExitCode=$helperRun.exitCode
  if($helperRun.status -ne 'exited'){$diagnostics.helperFailureCategory='helper-tool-failure';return $diagnostics}
  if($helperRun.exitCode -ne 0){$diagnostics.helperFailureCategory='helper-nonzero-exit';return $diagnostics}
  if (-not (Test-Path -LiteralPath $resultPath)) {
    $diagnostics.helperFailureCategory = 'helper-result-missing'
    return $diagnostics
  }
  try {
    if((Get-Item -LiteralPath $resultPath).Length -gt 32768){throw 'UIA_RESULT_OVERSIZED'}
    $safeUi = Get-Content -LiteralPath $resultPath -Raw -Encoding UTF8 | ConvertFrom-Json -AsHashtable
    foreach ($key in @('helperEncoding','helperExitCode','helperParseErrorCount','helperFailureCategory','helperProcessStopped','helperPhase')) { $safeUi[$key] = $diagnostics[$key] }
    if ($safeUi.status -eq 'uia-unavailable') { $safeUi.helperFailureCategory = 'uia-provider-unavailable' }
    return $safeUi
  } catch {
    $diagnostics.helperFailureCategory = 'helper-result-invalid'
    return $diagnostics
  }
}

try {
  if($GuiAutomation -ne 'none' -and ($RuntimeHost -ne 'clr2-x86-reference' -or -not $SyntheticLogin -or -not $InstallAndProbe)) { throw 'GUI_REFERENCE_AUTOMATION_MODE_INVALID' }
  New-Item -ItemType Directory -Path $work | Out-Null
  $report.stage = 'download'
  $rar = Join-Path $work 'official.rar'; $zip = Join-Path $work 'mirror.zip'
  Get-PinnedFile 'https://www.fshare.vn/file/TPW3FMLVAJL1' $rar '5d52c06595e933a3b246480785d5d4010fad669baed6fb38311f8a09b20e1e95'
  Get-PinnedFile 'https://fa.getpedia.net/data?q===QMzEDM2gjM3MDM0UzN4ITOzYDfxMTMxEDfwlmeuETL40SNts0SUh0L3EzLwEzL2IDMy8SZslmZvEGdhR2L' $zip '3f50ede214d802984549aa3841c3de6614fca90021ef5029a9c1ac1999776edb'
  $report.sourceHashesVerified = $true
  $report.stage = 'extract-data'
  $seven = Join-Path $env:ProgramFiles '7-Zip\7z.exe'
  if (-not (Test-Path -LiteralPath $seven)) { throw 'TRUSTED_RUNNER_7ZIP_MISSING' }
  # A pinned ZIP is expanded as data. The RAR's uncompressed cabinet is the only selected member.
  $mirror = Join-Path $work 'mirror'; $official = Join-Path $work 'official'
  Expand-Archive -LiteralPath $zip -DestinationPath $mirror
  & $seven x '-y' "-o$official" $rar 'HTKK_5.8.1_DLL_signed/Data1.cab' *> (Join-Path $work 'extract-private.log')
  if ($LASTEXITCODE -ne 0) { throw 'OFFICIAL_CAB_EXTRACTION_FAILED' }
  $source = Join-Path $mirror 'HTKK_5.8.1_DLL_signed'
  $cab = Join-Path $source 'Data1.cab'; $officialCab = Join-Path $official 'HTKK_5.8.1_DLL_signed\Data1.cab'
  Assert-Hash $cab '00669905937fb29e10cb53209ece5e8a9f8097970e4cb40bb28f89baa9fc3744'
  Assert-Hash $officialCab '00669905937fb29e10cb53209ece5e8a9f8097970e4cb40bb28f89baa9fc3744'
  $report.officialCabMatchesMirror = $true
  $msi = Join-Path $source 'HTKK.msi'
  Assert-Hash $msi '7c1da251ee2acd126a2363e4457502b8ad6fc0792d78dc0a92b153701dc29080'
  $report.stage = 'verify-msi'
  $signature = Get-AuthenticodeSignature -LiteralPath $msi
  if ($signature.Status -ne 'Valid' -or $null -eq $signature.SignerCertificate -or $null -eq $signature.TimeStamperCertificate) { throw 'MSI_AUTHENTICODE_NOT_VALID' }
  if ($signature.SignerCertificate.SerialNumber -ne '6435F70483012A5DBC374003') { throw 'MSI_PUBLISHER_SERIAL_MISMATCH' }
  if ($signature.SignerCertificate.Subject -notmatch 'Tổng Cục Thuế') { throw 'MSI_PUBLISHER_SUBJECT_MISMATCH' }
  $signTool = Get-ChildItem 'C:\Program Files (x86)\Windows Kits\10\bin\*\x64\signtool.exe' -ErrorAction SilentlyContinue | Sort-Object FullName -Descending | Select-Object -First 1
  if ($null -eq $signTool) { throw 'RUNNER_SIGNTOOL_MISSING' }
  & $signTool.FullName verify /pa /all /v $msi *> (Join-Path $work 'signature-private.log')
  if ($LASTEXITCODE -ne 0) { throw 'MSI_SIGNTOOL_VERIFICATION_FAILED' }
  $report.msiAuthenticodeValid = $true
  $report.stage = 'framework-check'
  $framework = Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\NET Framework Setup\NDP\v3.5' -ErrorAction SilentlyContinue
  $feature = Get-WindowsOptionalFeature -Online -FeatureName NetFx3
  if ($null -eq $framework -or $framework.Install -ne 1 -or $feature.State -ne 'Enabled') { throw 'NETFX35_MISSING_NO_BOOTSTRAPPER_EXECUTED' }
  $report.netFx35Present = $true
  if (-not $InstallAndProbe) { $report.stage = 'verified-install-not-requested'; return }
  # Execute only the pinned, publisher-verified MSI after official-distribution CAB equivalence.
  $report.stage = 'install'
  # An interrupted installer can leave service-mediated work; root exit alone is insufficient.
  $installerCredentialsSafe=$false
  $install=Invoke-HtkkBoundedNativeProcess -Executable "$env:WINDIR\System32\msiexec.exe" -WorkingDirectory $work -Arguments @('/i',$msi,'/qn','/norestart','ISCHECKFORPRODUCTUPDATES=0','/L*v',(Join-Path $work 'install-private.log')) -TimeoutMilliseconds 180000
  $report.installerProcess=$install;$installerStopped=$install.processStopped
  $installerCredentialsSafe=$installerStopped -and $install.status -eq 'exited' -and $install.exitCode -eq 0 -and -not $install.timedOut
  $report.installExitCode=$install.exitCode
  if(-not $installerStopped){throw 'MSI_PROCESS_NOT_STOPPED'}
  if($install.timedOut){throw 'MSI_INSTALL_TIMEOUT'}
  if($install.status -ne 'exited' -or $install.exitCode -notin @(0,3010)){throw 'MSI_INSTALL_FAILED'}
  if($install.exitCode -eq 3010){throw 'REBOOT_REQUIRED_PROBE_NOT_RUN'}
  $candidates = @("${env:ProgramFiles}\HTKK\Project\HTKK.exe", "${env:ProgramFiles(x86)}\HTKK\Project\HTKK.exe", 'C:\HTKK\Project\HTKK.exe')
  $exe = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
  if (-not $exe) { throw 'INSTALLED_HTKK_NOT_FOUND' }
  Assert-Hash $exe '411141d2e728a45f4a35a876afb169d0ac2450de2499e8a1f43ac29ab6401938'
  . (Join-Path $PSScriptRoot 'Test-HtkkTaxIdOracle.ps1')
  $report.taxIdOracle = Invoke-HtkkTaxIdOracle -ProjectDirectory (Split-Path $exe) -TemporaryDirectory $work
  . (Join-Path $PSScriptRoot 'Test-HtkkProfileAliasOracle.ps1')
  $report.profileAliasOracle = Invoke-HtkkProfileAliasOracle -ProjectDirectory (Split-Path $exe) -TemporaryDirectory $work
  . (Join-Path $PSScriptRoot 'Test-HtkkCommonHeaderOracle.ps1')
  $report.commonHeaderOracle = Invoke-HtkkCommonHeaderOracle -ProjectDirectory (Split-Path $exe) -TemporaryDirectory $work
  # Both modes block the original image; the reference mode additionally
  # blocks its own new host before any original code executes inside that host.
  $originalFirewall='HTKK readiness original '+[guid]::NewGuid().ToString('N')
  New-NetFirewallRule -DisplayName $originalFirewall -Direction Outbound -Program $exe -Action Block | Out-Null
  $firewallNames.Add($originalFirewall); $report.originalOutboundBlocked=$true
  $launchExecutable=$exe
  if($RuntimeHost -eq 'clr2-x86-reference') {
    $report.stage='prepare-x86-reference-host'
    . (Join-Path $PSScriptRoot 'New-HtkkX86ReferenceHost.ps1')
    $referencePreparation=New-HtkkX86ReferenceHost -ProjectDirectory (Split-Path $exe) -TemporaryDirectory $work -GuiAutomation $GuiAutomation
    $safeCompilerCodes=@($referencePreparation.compilerErrorCodes | Where-Object { $_ -match '^CS[0-9]{4}$' } | Select-Object -First 10)
    $report.referenceHostPreparation=[ordered]@{ status=$referencePreparation.status; mode='custom-x86-clr2-reference-host'; hostSha256=$null; originalExeHashVerified=$referencePreparation.originalExeHashVerified; businessDllHashVerified=$referencePreparation.businessDllHashVerified; originalConfigHashVerified=$referencePreparation.originalConfigHashVerified; compilerTrustVerified=$referencePreparation.compilerTrustVerified; compilerExitCode=$referencePreparation.compilerExitCode; compilerErrorCodes=$safeCompilerCodes; originalExecutableModified=$false; originalConfigurationModified=$false }
    if($referencePreparation.status -ne 'prepared') { throw 'X86_REFERENCE_HOST_PREPARATION_FAILED' }
    $projectFull=[IO.Path]::GetFullPath((Split-Path $exe)).TrimEnd('\')
    $hostFull=[IO.Path]::GetFullPath($referencePreparation.hostPath)
    $hostLeaf=[IO.Path]::GetFileName($hostFull)
    if([IO.Path]::GetDirectoryName($hostFull).TrimEnd('\') -ne $projectFull -or $hostLeaf -notmatch '^HTKK\.X86ReferenceHost\.[a-f0-9]{32}\.exe$' -or $referencePreparation.hostSha256 -notmatch '^[a-f0-9]{64}$' -or @($referencePreparation.arguments).Count -ne 0 -or $referencePreparation.hostConfigPath -ne ($hostFull+'.config') -or $referencePreparation.resultPath -ne ($hostFull+'.result.json') -or $referencePreparation.guiAutomationResultPath -ne ($hostFull+'.gui-automation.json') -or $referencePreparation.guiAutomationPermitPath -ne ($hostFull+'.gui-automation.allow') -or $referencePreparation.guiAutomationMode -cne $GuiAutomation) { throw 'X86_REFERENCE_HOST_LAYOUT_INVALID' }
    $referenceOwnedFiles=@($hostFull,($hostFull+'.config'),($hostFull+'.result.json'),($hostFull+'.gui-automation.json'),($hostFull+'.gui-automation.allow'))
    if($GuiAutomation -eq 'gtgt-web-import-inspect') {
      $casePath=$hostFull+'.web-case.id';$inputPath=$hostFull+'.web-input.xml';$hashPath=$hostFull+'.web-input.sha256';$shaPath=$hostFull+'.web-source.sha'
      if($env:EXPECTED_WEB_CASE_ID -cnotin @('01GTGT-zero-M10-2026','01GTGT-sale10-M10-2026','01GTGT-sale10-half-M10-2026','01GTGT-sale10-manual-M10-2026','01GTGT-sale5-half-M10-2026','01GTGT-sale5-manual-M10-2026','01GTGT-noactivity-zero-M10-2026','01GTGT-noactivity-reset-sale10-M10-2026','01GTGT-noactivity-cancel-sale10-M10-2026','01GTGT-noactivity-uncheck-sale10-M10-2026','01GTGT-noactivity-keep-credit-M10-2026','01GTGT-zero-Q4-2026','01GTGT-native-import-sale10-M10-2026') -or $referencePreparation.webImportCasePath -cne $casePath -or $referencePreparation.webImportInputPath -cne $inputPath -or $referencePreparation.webImportInputHashPath -cne $hashPath -or $referencePreparation.webImportSourceShaPath -cne $shaPath -or $env:EXPECTED_WEB_SOURCE_SHA -cnotmatch '^[a-f0-9]{40}$'){throw 'WEB_REFERENCE_INPUT_INVALID'}
      $referenceOwnedFiles+=@($inputPath,$hashPath,$shaPath,$casePath)
      foreach($path in @($inputPath,$hashPath,$shaPath,$casePath)){if(Test-Path -LiteralPath $path){throw 'WEB_REFERENCE_INPUT_INVALID'}}
      $stage=Join-Path $env:RUNNER_TEMP 'htkk-web-reference-input'
      $xml=Join-Path $stage '01GTGT-web.xml';$manifestPath=Join-Path $stage 'manifest.json'
      foreach($path in @($stage,$xml,$manifestPath)) {if(-not (Test-Path -LiteralPath $path) -or ((Get-Item -LiteralPath $path).Attributes -band [IO.FileAttributes]::ReparsePoint)){throw 'WEB_REFERENCE_INPUT_INVALID'}}
      if((Get-Item -LiteralPath $manifestPath).Length -gt 16384){throw 'WEB_REFERENCE_INPUT_INVALID'}
      $manifest=Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
      $expectedFormats=@{
        '01GTGT-zero-M10-2026'='htkk-web-zero-input-v1'
        '01GTGT-sale10-M10-2026'='htkk-web-sale10-input-v1'
        '01GTGT-sale10-half-M10-2026'='htkk-web-sale10-half-input-v1'
        '01GTGT-sale10-manual-M10-2026'='htkk-web-sale10-manual-input-v1'
        '01GTGT-sale5-half-M10-2026'='htkk-web-sale5-half-input-v1'
        '01GTGT-sale5-manual-M10-2026'='htkk-web-sale5-manual-input-v1'
        '01GTGT-noactivity-zero-M10-2026'='htkk-web-noactivity-zero-input-v1'
        '01GTGT-noactivity-reset-sale10-M10-2026'='htkk-web-noactivity-reset-sale10-input-v1'
        '01GTGT-noactivity-cancel-sale10-M10-2026'='htkk-web-noactivity-cancel-sale10-input-v1'
        '01GTGT-noactivity-uncheck-sale10-M10-2026'='htkk-web-noactivity-uncheck-sale10-input-v1'
        '01GTGT-noactivity-keep-credit-M10-2026'='htkk-web-noactivity-keep-credit-input-v1'
        '01GTGT-zero-Q4-2026'='htkk-web-quarter-zero-input-v1'
        '01GTGT-native-import-sale10-M10-2026'='htkk-web-native-import-sale10-input-v1'
      }
      $expectedFormat=$expectedFormats[$env:EXPECTED_WEB_CASE_ID]
      if($manifest.caseId -cne $env:EXPECTED_WEB_CASE_ID -or $manifest.format -cne $expectedFormat -or $manifest.sourceRepository -cne 'congminh1254/htkk_web' -or $manifest.inputsSynthetic -ne $true -or $manifest.sourceCommit -cne $env:EXPECTED_WEB_SOURCE_SHA -or $manifest.xmlSha256 -cnotmatch '^[a-f0-9]{64}$' -or $manifest.bytes -le 0 -or $manifest.bytes -gt 262144 -or (Get-Item -LiteralPath $xml).Length -ne $manifest.bytes){throw 'WEB_REFERENCE_INPUT_INVALID'}
      Assert-Hash $xml $manifest.xmlSha256
      [IO.File]::WriteAllBytes($inputPath,[IO.File]::ReadAllBytes($xml))
      Assert-Hash $inputPath $manifest.xmlSha256
      [IO.File]::WriteAllText($hashPath,$manifest.xmlSha256,[Text.Encoding]::ASCII)
      [IO.File]::WriteAllText($shaPath,$manifest.sourceCommit,[Text.Encoding]::ASCII)
      [IO.File]::WriteAllText($casePath,$manifest.caseId,[Text.Encoding]::ASCII)
    }
    Assert-Hash $hostFull $referencePreparation.hostSha256
    $expectedHostConfig='<?xml version="1.0"?><configuration><startup><supportedRuntime version="v2.0.50727"/></startup></configuration>'
    if((Get-Content -LiteralPath ($hostFull+'.config') -Raw -Encoding ASCII).Trim() -cne $expectedHostConfig) { throw 'X86_REFERENCE_HOST_LAYOUT_INVALID' }
    $report.referenceHostPreparation.hostSha256=$referencePreparation.hostSha256
    $referenceHostName=$hostLeaf
    $hostFirewall='HTKK readiness x86 reference '+[guid]::NewGuid().ToString('N')
    New-NetFirewallRule -DisplayName $hostFirewall -Direction Outbound -Program $hostFull -Action Block | Out-Null
    $firewallNames.Add($hostFirewall); $report.hostOutboundBlocked=$true
    $launchExecutable=$hostFull
  }
  $report.stage = 'startup'
  $preexistingHtkk = @(Get-Process -Name HTKK -ErrorAction SilentlyContinue)
  $report.preexistingHtkkProcessCount = $preexistingHtkk.Count
  $runnerSession = [Diagnostics.Process]::GetCurrentProcess().SessionId
  foreach ($existing in $preexistingHtkk) { try { if ($existing.SessionId -eq $runnerSession) { $report.preexistingHtkkSameSessionCount++ } } catch { } }
  $applicationStartTime = Get-Date
  $process = Start-HtkkCleanProcess -Executable $launchExecutable -ProjectDirectory (Split-Path $exe) -IsX86Reference ($RuntimeHost -eq 'clr2-x86-reference')
  $null=$process.Handle
  # Drain privately so no application output can reach the public log or block it.
  $applicationStdout=$process.StandardOutput.ReadToEndAsync(); $applicationStderr=$process.StandardError.ReadToEndAsync()
  $report.childEnvironmentPolicy='os-essentials-only'
  $report.processStarted = $true
  Initialize-WindowDiagnostics
  $report.runnerSessionId = [System.Diagnostics.Process]::GetCurrentProcess().SessionId
  try { $report.appSessionId = $process.SessionId } catch { $report.appSessionId=$null }
  $report.threadDesktop = [HtkkWindowDiagnostics]::DesktopKind()
  try { $report.appArchitecture = [HtkkWindowDiagnostics]::Architecture($process.Handle) } catch { $report.appArchitecture = 'unknown' }
  try { $rootStartTime = $process.StartTime } catch { $rootStartTime=$applicationStartTime }
  $startupClock = [System.Diagnostics.Stopwatch]::StartNew()
  do {
    $process.Refresh()
    $report.processAliveAfterWait = -not $process.HasExited
    $report.mainWindowHandlePresent = $report.processAliveAfterWait -and ($process.MainWindowHandle -ne [IntPtr]::Zero)
    $children = @(Get-DescendantProcessIds -AppProcessId $process.Id -RootStartTime $rootStartTime)
    if ($AcknowledgeRegistration) {
      Invoke-HtkkRegistrationAcknowledgement -DescendantIds ([int[]]$children) -AppProcessId $process.Id -RootStartTime $rootStartTime
      Update-HtkkRegistrationResults
      $children = @(Get-DescendantProcessIds -AppProcessId $process.Id -RootStartTime $rootStartTime)
    }
    $report.childProcessCount = $children.Count
    $counts = [HtkkWindowDiagnostics]::Counts($process.Id, [int[]]$children)
    $report.allVisibleWindowCount = $counts[0]
    $report.appVisibleWindowCount = $counts[1]; $report.appHiddenWindowCount = $counts[2]
    $report.childVisibleWindowCount = $counts[3]; $report.childHiddenWindowCount = $counts[4]
    $report.windowObserved = ($counts[1] + $counts[3]) -gt 0
    $report.startupWaitSeconds = [int][Math]::Floor($startupClock.Elapsed.TotalSeconds)
    $report.rootAppWindowObserved = $counts[1] -gt 0
    # A console/browser child is not evidence that the HTKK login is ready.
    if ($report.rootAppWindowObserved -or $startupClock.Elapsed.TotalSeconds -ge 45) { break }
    Start-Sleep -Seconds ([Math]::Min(5, [Math]::Max(1, [Math]::Ceiling(45 - $startupClock.Elapsed.TotalSeconds))))
  } while ($true)
  $startupClock.Stop()
  if ($AcknowledgeRegistration) { Update-HtkkRegistrationResults -WaitMilliseconds 1000 }
  if($RuntimeHost -eq 'clr2-x86-reference' -and $null -ne $referencePreparation) { $report.referenceHostResult=Get-HtkkSafeReferenceResult -ResultPath $referencePreparation.resultPath }
  $report.applicationEvents = Get-HtkkSafeApplicationEvents -ApplicationStartTime $applicationStartTime -ReferenceHostName $referenceHostName
  $report.ownedWindowKinds = [HtkkWindowDiagnostics]::OwnedWindowKinds($process.Id, [int[]]$children)
  $report.nativeDialogCueCounts = [HtkkWindowDiagnostics]::FixedDialogCues($process.Id, [int[]]$children)
  $report.startupContext = if ($report.windowObserved) { 'visible-app-or-child-window' }
    elseif ($report.appSessionId -ne $report.runnerSessionId) { 'different-process-session' }
    elseif ($report.runnerSessionId -eq 0) { 'session-zero' }
    elseif (-not $report.userInteractive) { 'noninteractive-environment' }
    elseif ($report.allVisibleWindowCount -eq 0) { 'no-visible-windows-on-current-desktop' }
    elseif (($report.appHiddenWindowCount + $report.childHiddenWindowCount) -gt 0) { 'only-hidden-app-windows' }
    else { 'no-app-windows-on-current-desktop' }
  if (-not $report.windowObserved) {
    if ($AcknowledgeRegistration -and $report.registrationNonzeroExitCount -gt 0) { throw 'REGISTRATION_PROCESS_FAILED' }
    if ($AcknowledgeRegistration -and $report.registrationUnverifiedExitCount -gt 0) { throw 'REGISTRATION_RESULT_NOT_VERIFIED' }
    throw 'STARTUP_WINDOW_NOT_OBSERVED'
  }
  # Read-only classification of descendant processes; arbitrary process names are never emitted.
  $verifiedChildImages = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
  $unknownInspections = 0
  foreach ($childId in $children) {
    try {
      $name = (Get-Process -Id $childId -ErrorAction Stop).ProcessName
      $kind = switch ($name.ToLowerInvariant()) {
        'htkk' { 'HTKK' }; 'msiexec' { 'msiexec' }; 'werfault' { 'WerFault' }
        'rundll32' { 'rundll32' }; 'dllhost' { 'dllhost' }
        'conhost' { 'console' }; 'openconsole' { 'console' }; 'windowsterminal' { 'console' }
        'cmd' { 'shell' }; 'powershell' { 'shell' }; 'pwsh' { 'shell' }
        'msedge' { 'browser' }; 'msedgewebview2' { 'browser' }; 'chrome' { 'browser' }; 'firefox' { 'browser' }; 'iexplore' { 'browser' }
        'updater' { 'updater' }; 'autoupdate' { 'updater' }; 'htkkupdate' { 'updater' }
        'vsjitdebugger' { 'debugger' }; 'vsdebugconsole' { 'debugger' }; 'devenv' { 'debugger' }; 'vsdebugeng' { 'debugger' }; 'dbghost' { 'debugger' }; 'dbgsvc' { 'debugger' }
        'dw20' { 'errorReporting' }; 'dwwin' { 'errorReporting' }; 'wermgr' { 'errorReporting' }; 'werfaultsecure' { 'errorReporting' }
        default { 'other' }
      }
      $report.descendantProcessKinds[$kind]++
      if ($kind -eq 'other' -and $unknownInspections -lt 16) {
        $unknownInspections++
        try { $image = Get-VerifiedMicrosoftImageBasename -ProcessId $childId; if ($image) { $verifiedChildImages.Add($image) | Out-Null } } catch { $report.unknownChildImageInspectionFailures++ }
      }
    } catch { $report.descendantProcessKinds.other++ }
  }
  $report.verifiedMicrosoftChildImages = @($verifiedChildImages | Sort-Object | Select-Object -First 16)
  try {
    $uia = Get-HtkkSafeUiDiagnostics -AppProcessId $process.Id -Descendants ([int[]]$children) -TemporaryDirectory $work
    $report.uiaStatus = $uia.status; $report.uiaWindowCount = $uia.windows; $report.uiaControlCount = $uia.controls
    $report.uiaControlTypeCounts = $uia.types; $report.uiaAllowedControlIds = @($uia.ids); $report.uiaStaticLabels = @($uia.labels)
    $report.loginReady = $uia.loginReady
    $report.uiaWindowCategories = if ($uia.ContainsKey('categories')) { @($uia.categories) } else { @() }
    $report.uiaLegacyRoleCounts = if ($uia.ContainsKey('legacyRoles')) { $uia.legacyRoles } else { @{} }
    $report.uiaLegacyPatternAvailable = if ($uia.ContainsKey('legacyPatternAvailable')) { $uia.legacyPatternAvailable } else { $false }
    $report.uiaProviderProcessMismatchCount = if ($uia.ContainsKey('providerProcessMismatchCount')) { $uia.providerProcessMismatchCount } else { 0 }
    $report.uiaViews = if ($uia.ContainsKey('views')) { @($uia.views) } else { @() }
    $report.uiaHelperEncoding = $uia.helperEncoding; $report.uiaHelperExitCode = $uia.helperExitCode
    $report.uiaHelperParseErrorCount = $uia.helperParseErrorCount; $report.uiaHelperFailureCategory = $uia.helperFailureCategory; $report.uiaHelperPhase=$uia.helperPhase
  } catch { $report.uiaStatus = 'uia-helper-failed'; $report.uiaHelperFailureCategory = 'helper-wrapper-failure' }
  if ($AcknowledgeRegistration) {
    Update-HtkkRegistrationResults
    if ($report.registrationNonzeroExitCount -gt 0) { throw 'REGISTRATION_PROCESS_FAILED' }
    if ($report.registrationUnverifiedExitCount -gt 0) { throw 'REGISTRATION_RESULT_NOT_VERIFIED' }
    if ($report.registrationAcknowledgementLimitReached) { throw 'REGISTRATION_ACKNOWLEDGEMENT_LIMIT' }
  }
  if ($report.taxIdOracle.status -ne 'matched') { throw 'TAX_ID_ORACLE_NOT_VERIFIED' }
  if ($report.profileAliasOracle.status -ne 'matched') { throw 'PROFILE_ALIAS_ORACLE_NOT_VERIFIED' }
  if ($SyntheticLogin) {
    if (-not $report.loginReady) { throw 'SYNTHETIC_LOGIN_NOT_READY' }
    . (Join-Path $PSScriptRoot 'Invoke-HtkkSyntheticLogin.ps1')
    $report.syntheticLogin = Invoke-HtkkSyntheticLogin -RootProcessId $process.Id -RootStartTime $rootStartTime -ProjectDirectory (Split-Path $exe)
    if ($report.syntheticLogin.status -ne 'synthetic-profile-window-observed') { throw 'SYNTHETIC_LOGIN_NOT_VERIFIED' }
  }
  if($GuiAutomation -ne 'none') {
    . (Join-Path $PSScriptRoot 'Get-HtkkSafeGuiReferenceResult.ps1')
    if($GuiAutomation -in @('profile-save','gtgt-inspect','gtgt-sheet-inspect','gtgt-amendment-inspect','gtgt-amendment-open-inspect','gtgt-annex12-inspect','gtgt-annex12-row-inspect','gtgt-annex12-input-inspect','gtgt-annex12-numeric-inspect','gtgt-annex12-export-inspect','gtgt-export-inspect','gtgt-roundtrip-inspect','gtgt-web-import-inspect')) {
      # Only now authorize mutation: the independent original GUI login/profile
      # transition and fresh synthetic directory have already been verified above.
      [IO.File]::WriteAllText($referencePreparation.guiAutomationPermitPath,'profile-save',[Text.Encoding]::ASCII)
    }
    $automationLimit=if($GuiAutomation -in @('gtgt-roundtrip-inspect','gtgt-web-import-inspect','gtgt-amendment-open-inspect')){60}else{30}
    $automationClock=[Diagnostics.Stopwatch]::StartNew();$lastGui=$null;$terminal=$false;$automationRootExited=$false
    do {
      $nextGui=Get-HtkkSafeGuiReferenceResult -ResultPath $referencePreparation.guiAutomationResultPath -ExpectedMode $GuiAutomation
      if($nextGui.status -eq 'valid') {
        $lastGui=$nextGui
        $terminal=$nextGui.failureCategory -ne 'none' -or $nextGui.stage -in @('source-or-runtime-not-matched','fixture-preexists','initialization-unavailable','profile-wait-timeout','profile-dimensions-unmatched','fresh-synthetic-profile-not-established','editing-api-unavailable','profile-province-code-unmatched','profile-ward-code-unmatched','profile-taxhead-code-unmatched','profile-taxlocal-code-unmatched','original-profile-saved-verified','original-profile-save-not-verified','gtgt-profile-preconditions-not-matched','gtgt-profile-owner-not-matched','gtgt-menu-id-not-unique','gtgt-menu-target-hidden','gtgt-period-inspected','gtgt-period-inputs-not-matched','gtgt-sheet-inspected','gtgt-original-declaration-saved-inspected','gtgt-amendment-open-inspected','gtgt-annex12-inspected','gtgt-annex12-row-inspected','gtgt-annex12-input-inspected','gtgt-annex12-numeric-inspected','gtgt-annex12-export-inspected','gtgt-sheet-contract-not-matched','gtgt-export-inspected','gtgt-export-original-message-rejected','gtgt-roundtrip-inspected','gtgt-web-import-inspected','gtgt-import-original-message-rejected') -or ($GuiAutomation -eq 'inspect' -and $nextGui.stage -eq 'profile-inspected')
        if($terminal){break}
      }
      if($process.HasExited){$automationRootExited=$true;break}
      Start-Sleep -Milliseconds 500
    }while($automationClock.Elapsed.TotalSeconds -lt $automationLimit)
    if($null -eq $lastGui){$report.guiReferenceAutomation=[ordered]@{status='no-valid-result';mode=$GuiAutomation;stage='result-unavailable-or-invalid';waitSeconds=[int]$automationClock.Elapsed.TotalSeconds;runtimeRoundTrip=$false};throw 'GUI_REFERENCE_AUTOMATION_NOT_VERIFIED'}
    $matched=$lastGui.sourcePinsVerified -and $lastGui.mstBoxesMatched -and $lastGui.initialRequiredTextBlank -and $lastGui.editingApiAvailable -and $lastGui.failureCategory -eq 'none' -and $lastGui.spreadCount -eq 1
    if($GuiAutomation -eq 'inspect'){$matched=$matched -and $lastGui.stage -eq 'profile-inspected' -and -not $lastGui.originalSaveInvoked -and $lastGui.performedInputCount -eq 0}
    else{
      $matched=$matched -and $lastGui.originalSaveInvoked -and $lastGui.savedHeaderExists -and $lastGui.savedHeaderChecksMatched -and $lastGui.savedHeaderCheckedFieldCount -eq 8 -and $lastGui.performedInputCount -eq 7 -and $lastGui.savedHeaderMismatchMask -eq 0 -and $lastGui.saveDialogKind -eq 'success-0002'
      if($GuiAutomation -in @('gtgt-inspect','gtgt-sheet-inspect','gtgt-amendment-inspect','gtgt-amendment-open-inspect','gtgt-annex12-inspect','gtgt-annex12-row-inspect','gtgt-annex12-input-inspect','gtgt-annex12-numeric-inspect','gtgt-annex12-export-inspect','gtgt-export-inspect','gtgt-roundtrip-inspect','gtgt-web-import-inspect')){
        $matched=$matched -and $lastGui.profileClosed -and $lastGui.mainMenuObserved -and $lastGui.d1MenuClicked -and $lastGui.gtgtPeriodObserved -and $lastGui.periodControlCount -gt 0
        if($GuiAutomation -in @('gtgt-sheet-inspect','gtgt-amendment-inspect','gtgt-amendment-open-inspect','gtgt-annex12-inspect','gtgt-annex12-row-inspect','gtgt-annex12-input-inspect','gtgt-annex12-numeric-inspect','gtgt-annex12-export-inspect','gtgt-export-inspect','gtgt-roundtrip-inspect','gtgt-web-import-inspect')){$matched=$matched -and $lastGui.stage -eq $(if($GuiAutomation -eq 'gtgt-web-import-inspect'){'gtgt-web-import-inspected'}elseif($GuiAutomation -eq 'gtgt-roundtrip-inspect'){'gtgt-roundtrip-inspected'}elseif($GuiAutomation -eq 'gtgt-export-inspect'){'gtgt-export-inspected'}elseif($GuiAutomation -eq 'gtgt-annex12-export-inspect'){'gtgt-annex12-export-inspected'}elseif($GuiAutomation -eq 'gtgt-annex12-numeric-inspect'){'gtgt-annex12-numeric-inspected'}elseif($GuiAutomation -eq 'gtgt-annex12-input-inspect'){'gtgt-annex12-input-inspected'}elseif($GuiAutomation -eq 'gtgt-annex12-row-inspect'){'gtgt-annex12-row-inspected'}elseif($GuiAutomation -eq 'gtgt-annex12-inspect'){'gtgt-annex12-inspected'}elseif($GuiAutomation -eq 'gtgt-amendment-open-inspect'){'gtgt-amendment-open-inspected'}elseif($GuiAutomation -eq 'gtgt-amendment-inspect'){'gtgt-original-declaration-saved-inspected'}else{'gtgt-sheet-inspected'}) -and $lastGui.periodYearMonthMatched -and $lastGui.periodFirstDeclarationMatched -and $lastGui.periodActivityMatched -and $lastGui.periodGeographyMatched -and $(if($GuiAutomation -in @('gtgt-annex12-inspect','gtgt-annex12-row-inspect','gtgt-annex12-input-inspect','gtgt-annex12-numeric-inspect','gtgt-annex12-export-inspect')){$lastGui.periodAnnex12Matched}else{$lastGui.periodNoAnnexMatched}) -and $lastGui.periodConfirmInvoked -and $lastGui.gtgtWorkbookPinsVerified -and $lastGui.gtgtMenuVersionMatched -and $lastGui.gtgtPeriodModelMatched -and $lastGui.gtgtSheetObserved -and $lastGui.gtgtSheetNameMatched -and $lastGui.gtgtDimensionsMatched -and $lastGui.gtgtIdentityMatched -and $lastGui.gtgtCt21Ready}
        else{$matched=$matched -and $lastGui.stage -eq 'gtgt-period-inspected'}
        if($GuiAutomation -in @('gtgt-export-inspect','gtgt-roundtrip-inspect','gtgt-web-import-inspect')){$matched=$matched -and $lastGui.exportSchemaPinnedVerified -and $lastGui.exportOriginalPathMatched -and $lastGui.exportCommandInvoked -and $lastGui.exportSelectorMatched -and $lastGui.exportButtonInvoked -and $lastGui.exportDialogMatched -and $lastGui.exportDestinationFresh -and $lastGui.exportDialogSubmitted -and $lastGui.exportFilenameKeyboardCommitted -and $lastGui.exportFileExists -and $lastGui.exportXmlRootMatched -and $lastGui.exportSyntheticIdentityMatched -and $lastGui.exportSuccessAcknowledged -and $lastGui.exportBytes -gt 0 -and $lastGui.exportSha256 -cmatch '^[0-9a-f]{64}$'}
        if($GuiAutomation -in @('gtgt-annex12-inspect','gtgt-annex12-row-inspect','gtgt-annex12-input-inspect','gtgt-annex12-numeric-inspect','gtgt-annex12-export-inspect')){$matched=$matched -and $lastGui.annexSelectedCount -eq 1 -and $lastGui.annex12SelectionActionCount -eq 1 -and $lastGui.annex12SourcePinsMatched -and $lastGui.annex12SheetObserved -and $lastGui.annex12StructureMatched -and $lastGui.annex12GroupMetadataMatched -and $lastGui.annex12GroupCount -ge 1 -and $lastGui.gtgtSignatureReady -and $lastGui.gtgtMonetaryZero -and $lastGui.gtgtEmptyMonetaryCount -eq 0 -and $(if($GuiAutomation -eq 'gtgt-annex12-export-inspect'){$lastGui.exportCommandInvoked}else{-not $lastGui.exportCommandInvoked}) -and -not $lastGui.webInputVerified}
        if($GuiAutomation -in @('gtgt-annex12-row-inspect','gtgt-annex12-input-inspect','gtgt-annex12-numeric-inspect','gtgt-annex12-export-inspect')){$matched=$matched -and $lastGui.annex12RowTabClickInvoked -and $lastGui.annex12F5Visible -and $lastGui.annex12F5Invoked -and $lastGui.annex12RowBeforeMatched -and $lastGui.annex12RowAfterMatched -and $lastGui.annex12RowSttMatched -and $lastGui.annex12RowLocksMatched -and $lastGui.annex12RowBeforeRows -eq 66 -and $lastGui.annex12RowAfterRows -eq 67 -and $lastGui.annex12RowBeforeGroupRows -eq 1 -and $lastGui.annex12RowAfterGroupRows -eq 2 -and $lastGui.annex12RowAfterGroupId -eq 1 -and $lastGui.annex12RowInsertActionCount -eq 1}
        if($GuiAutomation -in @('gtgt-annex12-input-inspect','gtgt-annex12-numeric-inspect','gtgt-annex12-export-inspect')){$matched=$matched -and $lastGui.annex12InputActionCount -eq 14 -and $lastGui.annex12InputReadOnlyIdentityMatched -and $lastGui.annex12InputIdentityMatched -and $lastGui.annex12InputTypesMatched -and $lastGui.annex12InputGeographyMatched -and $lastGui.annex12InputTaxAuthoritiesMatched -and $lastGui.annex12InputPercentagesMatched -and $lastGui.annex12InputZeroTaxMatched}
        if($GuiAutomation -eq 'gtgt-annex12-numeric-inspect'){$matched=$matched -and $lastGui.annex12NumericActionCount -eq 5 -and $lastGui.annex12NumericCaseCount -eq 3 -and $lastGui.annex12NumericSnapshots -cne ''}
        if($GuiAutomation -eq 'gtgt-annex12-export-inspect'){$matched=$matched -and $lastGui.annex12ExportMainZeroMatched -and $lastGui.annex12ExportShapeMatched -and $lastGui.annex12ExportSchemaVerified -and $lastGui.gtgtCaseMoneyCount -eq 27 -and $lastGui.gtgtCaseMismatchMask -eq 0 -and $lastGui.gtgtCaseNonzeroMask -eq 0 -and $lastGui.exportSchemaPinnedVerified -and $lastGui.exportSuccessAcknowledged -and $lastGui.exportOriginalPathMatched -and $lastGui.exportFilenameKeyboardCommitted -and $lastGui.exportDialogSubmitted -and $lastGui.exportXmlRootMatched -and $lastGui.exportSyntheticIdentityMatched -and $lastGui.exportFileExists -and $lastGui.exportBytes -gt 0 -and $lastGui.exportSha256 -cmatch '^[0-9a-f]{64}$'}
        if($GuiAutomation -eq 'gtgt-amendment-inspect'){$matched=$matched -and $lastGui.amendmentPriorSaveInvoked -and $lastGui.amendmentPriorSaveSuccessAcknowledged -and $lastGui.amendmentPriorDirtyCleared -and $lastGui.amendmentPriorFileFresh -and $lastGui.amendmentPriorFileScopeMatched -and $lastGui.amendmentPriorXmlParsed -and $lastGui.amendmentPriorMoneyZero -and $lastGui.amendmentPriorSavedMoneyZero -and $lastGui.amendmentPriorSavedMoneyCount -eq 27 -and $lastGui.amendmentPriorFileBytes -gt 1 -and $lastGui.amendmentPriorFileSha256 -cmatch '^[0-9a-f]{64}$' -and $lastGui.gtgtSignatureReady -and $lastGui.gtgtMonetaryZero -and $lastGui.gtgtEmptyMonetaryCount -eq 0 -and $lastGui.gtgtAutoCalculationReady -and $lastGui.gtgtBusinessInstanceMatched -and -not $lastGui.amendmentLifecycleVerified -and -not $lastGui.exportCommandInvoked -and -not $lastGui.webInputVerified}
        if($GuiAutomation -eq 'gtgt-amendment-open-inspect'){$matched=$matched -and $lastGui.amendmentPriorSaveInvoked -and $lastGui.amendmentPriorSaveSuccessAcknowledged -and $lastGui.amendmentPriorDirtyCleared -and $lastGui.amendmentPriorFileFresh -and $lastGui.amendmentPriorFileScopeMatched -and $lastGui.amendmentPriorXmlParsed -and $lastGui.amendmentPriorMoneyZero -and $lastGui.amendmentPriorSavedMoneyZero -and $lastGui.amendmentPriorSavedMoneyCount -eq 27 -and $lastGui.amendmentPriorFileBytes -gt 1 -and $lastGui.amendmentPriorFileSha256 -cmatch '^[0-9a-f]{64}$' -and $lastGui.gtgtSignatureReady -and $lastGui.gtgtMonetaryZero -and $lastGui.gtgtEmptyMonetaryCount -eq 0 -and $lastGui.gtgtAutoCalculationReady -and $lastGui.gtgtBusinessInstanceMatched -and -not $lastGui.amendmentLifecycleVerified -and -not $lastGui.exportCommandInvoked -and -not $lastGui.webInputVerified -and $lastGui.amendmentOpenCloseInvoked -and $lastGui.amendmentOpenPriorClosed -and $lastGui.amendmentOpenDefaultsMatched -and $lastGui.amendmentOpenConfirmInvoked -and $lastGui.amendmentOpenPeriodMatched -and $lastGui.amendmentOpenSourcesMatched -and $lastGui.amendmentOpenKhbsSheetsObserved -and $lastGui.amendmentOpenPriorUnchanged -and $lastGui.amendmentOpenLoadedSheets -ge 3 -and $lastGui.amendmentOpenLoadedSheets -le 32 -and $lastGui.amendmentOpenKhbsRows -gt 0 -and $lastGui.amendmentOpenKhbsColumns -gt 0 -and $lastGui.amendmentOpenExplanationRows -gt 0 -and $lastGui.amendmentOpenExplanationColumns -gt 0}
        if($GuiAutomation -eq 'gtgt-web-import-inspect'){$matched=$matched -and $lastGui.webInputVerified -and $lastGui.webCaseId -ceq $env:EXPECTED_WEB_CASE_ID -and $lastGui.webCaseEditCount -eq $(if($env:EXPECTED_WEB_CASE_ID -ceq '01GTGT-noactivity-uncheck-sale10-M10-2026'){3}elseif($env:EXPECTED_WEB_CASE_ID -cin @('01GTGT-sale10-manual-M10-2026','01GTGT-sale5-manual-M10-2026','01GTGT-noactivity-reset-sale10-M10-2026','01GTGT-noactivity-cancel-sale10-M10-2026','01GTGT-noactivity-uncheck-sale10-M10-2026','01GTGT-noactivity-keep-credit-M10-2026')){2}elseif($env:EXPECTED_WEB_CASE_ID -cnotin @('01GTGT-zero-M10-2026','01GTGT-zero-Q4-2026')){1}else{0}) -and $lastGui.gtgtCaseMoneyMatched -and $lastGui.gtgtCt42BeforeExportObserved -and $lastGui.gtgtCt42AfterImportObserved -and $lastGui.gtgtAutoCalculationReady -and $lastGui.gtgtBusinessInstanceMatched -and $lastGui.gtgtCaseMoneyCount -eq 27 -and $lastGui.webSourceSha -ceq $env:EXPECTED_WEB_SOURCE_SHA -and $lastGui.webImportInputSha256 -cmatch '^[a-f0-9]{64}$'}
        if($GuiAutomation -eq 'gtgt-web-import-inspect' -and $env:EXPECTED_WEB_CASE_ID -cin @('01GTGT-noactivity-zero-M10-2026','01GTGT-noactivity-reset-sale10-M10-2026','01GTGT-noactivity-cancel-sale10-M10-2026','01GTGT-noactivity-uncheck-sale10-M10-2026','01GTGT-noactivity-keep-credit-M10-2026')){$matched=$matched -and $lastGui.gtgtCt21CaseMatched -and $lastGui.gtgtCt21ConfirmationMatched -and $lastGui.gtgtCt21LocksMatched -and $lastGui.gtgtCt21BeforeExportMatched -and $lastGui.gtgtCt21AfterImportMatched}
        if($GuiAutomation -eq 'gtgt-web-import-inspect' -and $env:EXPECTED_WEB_CASE_ID -ceq '01GTGT-noactivity-uncheck-sale10-M10-2026'){$matched=$matched -and $lastGui.gtgtCt21UncheckMatched}
        if($GuiAutomation -in @('gtgt-roundtrip-inspect','gtgt-web-import-inspect')){$matched=$matched -and $lastGui.roundtripImportCommandInvoked -and $lastGui.roundtripImportDialogMatched -and $lastGui.roundtripImportKeyboardCommitted -and $lastGui.roundtripImportDialogSubmitted -and $lastGui.roundtripImportPathMatched -and $lastGui.roundtripImportSheetMatched -and $lastGui.roundtripImportSucceeded -and $lastGui.roundtripImportCheckedMoneyCount -eq 27 -and $lastGui.roundtripReexportCommandInvoked -and $lastGui.roundtripReexportSucceeded -and $lastGui.roundtripReexportBytes -gt 0 -and $lastGui.roundtripReexportSha256 -cmatch '^[0-9a-f]{64}$' -and $(if($GuiAutomation -eq 'gtgt-web-import-inspect'){$lastGui.webTaxValuesMatched -and $lastGui.webCreationDateMatchedNativeBaseline -and $lastGui.webServiceIdentityMatched -and $lastGui.webTaxLeafCount -eq 70}else{$lastGui.roundtripXmlExactMatched})}
      }else{$matched=$matched -and $lastGui.stage -eq 'original-profile-saved-verified'}
    }
    $lastGui.status=if($matched){'matched'}elseif($terminal){'failed'}elseif($automationRootExited){'root-exited'}else{'timed-out'}
    $lastGui['waitSeconds']=[int]$automationClock.Elapsed.TotalSeconds
    $report.guiReferenceAutomation=$lastGui
    if(-not $matched){throw 'GUI_REFERENCE_AUTOMATION_NOT_VERIFIED'}
  }
  $report.stage = if($GuiAutomation -eq 'gtgt-web-import-inspect'){'synthetic-original-gtgt-web-import-inspected'}elseif($GuiAutomation -eq 'gtgt-roundtrip-inspect'){'synthetic-original-gtgt-roundtrip-inspected'}elseif($GuiAutomation -eq 'gtgt-export-inspect'){'synthetic-original-gtgt-export-inspected'}elseif($GuiAutomation -eq 'gtgt-annex12-export-inspect'){'synthetic-original-gtgt-annex12-export-inspected'}elseif($GuiAutomation -eq 'gtgt-annex12-numeric-inspect'){'synthetic-original-gtgt-annex12-numeric-inspected'}elseif($GuiAutomation -eq 'gtgt-annex12-input-inspect'){'synthetic-original-gtgt-annex12-input-inspected'}elseif($GuiAutomation -eq 'gtgt-annex12-row-inspect'){'synthetic-original-gtgt-annex12-row-inspected'}elseif($GuiAutomation -eq 'gtgt-annex12-inspect'){'synthetic-original-gtgt-annex12-inspected'}elseif($GuiAutomation -eq 'gtgt-amendment-open-inspect'){'synthetic-original-amendment-open-inspected'}elseif($GuiAutomation -eq 'gtgt-amendment-inspect'){'synthetic-original-declaration-saved-for-amendment-inspected'}elseif($GuiAutomation -eq 'gtgt-sheet-inspect'){'synthetic-original-gtgt-sheet-inspected'}elseif($GuiAutomation -eq 'gtgt-inspect'){'synthetic-original-gtgt-period-inspected'}elseif($GuiAutomation -eq 'profile-save'){'synthetic-original-profile-saved-verified'}elseif($GuiAutomation -eq 'inspect'){'synthetic-profile-managed-controls-inspected'}elseif ($SyntheticLogin) { 'synthetic-profile-window-observed' } else { 'startup-window-observed' }
} catch {
  # Only allow fixed diagnostic enums into the public summary. Never dump remote/installer output.
  $known = @('SOURCE_DOWNLOAD_CLEANUP_NOT_VERIFIED','SOURCE_DOWNLOAD_DNS','SOURCE_DOWNLOAD_TLS','SOURCE_DOWNLOAD_HTTP','SOURCE_DOWNLOAD_TIMEOUT','SOURCE_DOWNLOAD_CONNECT','SOURCE_DOWNLOAD_TOOL','WEB_REFERENCE_INPUT_INVALID','GUI_REFERENCE_AUTOMATION_MODE_INVALID','GUI_REFERENCE_AUTOMATION_NOT_VERIFIED','SYNTHETIC_LOGIN_NOT_READY','SYNTHETIC_LOGIN_NOT_VERIFIED','PROFILE_ALIAS_ORACLE_NOT_VERIFIED','REGISTRATION_PROCESS_FAILED','REGISTRATION_RESULT_NOT_VERIFIED','REGISTRATION_ACKNOWLEDGEMENT_LIMIT','X86_REFERENCE_HOST_PREPARATION_FAILED','X86_REFERENCE_HOST_LAYOUT_INVALID','ORIGINAL_SOURCE_CHANGED','TAX_ID_ORACLE_NOT_VERIFIED','SOURCE_HASH_MISMATCH','TRUSTED_RUNNER_7ZIP_MISSING','OFFICIAL_CAB_EXTRACTION_FAILED','MSI_AUTHENTICODE_NOT_VALID','MSI_PUBLISHER_SERIAL_MISMATCH','MSI_PUBLISHER_SUBJECT_MISMATCH','RUNNER_SIGNTOOL_MISSING','MSI_SIGNTOOL_VERIFICATION_FAILED','NETFX35_MISSING_NO_BOOTSTRAPPER_EXECUTED','MSI_INSTALL_TIMEOUT','MSI_PROCESS_NOT_STOPPED','MSI_INSTALL_FAILED','REBOOT_REQUIRED_PROBE_NOT_RUN','INSTALLED_HTKK_NOT_FOUND','STARTUP_WINDOW_NOT_OBSERVED')
  $reason = $_.Exception.Message
  $report['blockedReason'] = if ($reason -in $known) { $reason } else { 'HOST_NETWORK_OR_TOOL_FAILURE' }
  $report.stage = 'blocked'
} finally {
  # Before cleanup, only a verified owned Microsoft RegSvr32 modal may be captured.
  # This diagnostic contains no taxpayer input and is uploaded privately in a separate step.
  if($null -ne $process -and $null -ne $rootStartTime -and -not $report.loginReady) {
    try {
      if(-not $process.HasExited) {
        . (Join-Path $PSScriptRoot 'Save-HtkkRegistrationDiagnostic.ps1')
        $owned=@(Get-DescendantProcessIds -AppProcessId $process.Id -RootStartTime $rootStartTime)
        $report.privateRegistrationDiagnostic=Save-HtkkRegistrationDiagnostic -RootProcessId $process.Id -OwnedProcessIds ([int[]]$owned) -RootStartTime $rootStartTime -RuntimeHost $RuntimeHost -RunId $env:GITHUB_RUN_ID
      }
    } catch { $report.privateRegistrationDiagnostic=@{status='capture-unavailable';captured=$false;taxDataUsed=$false;publicScreenshot=$false} }
  }
  if($RuntimeHost -eq 'original' -and $SyntheticLogin -and $report.stage -eq 'blocked' -and $null -ne $report.syntheticLogin -and $report.syntheticLogin.status -ne 'synthetic-profile-window-observed' -and $null -ne $process -and $null -ne $rootStartTime) {
    try {
      if(-not $process.HasExited) {
        . (Join-Path $PSScriptRoot 'Save-HtkkSyntheticWindowDiagnostic.ps1')
        $report.privateSyntheticLoginDiagnostic=Save-HtkkSyntheticWindowDiagnostic -RootProcessId $process.Id -RootStartTime $rootStartTime -ExpectedHtkkExecutable $exe -LoginReport $report.syntheticLogin -RunId $env:GITHUB_RUN_ID
      }
    } catch { $report.privateSyntheticLoginDiagnostic=@{status='capture-unavailable';captured=$false;realTaxpayerDataUsed=$false;sourceDefaultsMayBeVisible=$true;publicScreenshot=$false} }
  }
  if($RuntimeHost -eq 'clr2-x86-reference' -and $GuiAutomation -eq 'profile-save' -and $report.stage -eq 'blocked' -and $null -ne $report.guiReferenceAutomation -and $report.guiReferenceAutomation.originalSaveInvoked -eq $true -and $null -ne $referencePreparation -and $null -ne $process){
   try{if(-not $process.HasExited){
    . (Join-Path $PSScriptRoot 'Save-HtkkSyntheticWindowDiagnostic.ps1')
    $report.privateSyntheticLoginDiagnostic=Save-HtkkSyntheticWindowDiagnostic -RootProcessId $process.Id -RootStartTime $rootStartTime -ExpectedHtkkExecutable $exe -LoginReport $report.syntheticLogin -RunId $env:GITHUB_RUN_ID -ReferenceExecutable $referencePreparation.hostPath -ReferenceSha256 $referencePreparation.hostSha256 -GuiReport $report.guiReferenceAutomation
   }}catch{$report.privateSyntheticLoginDiagnostic=@{status='capture-unavailable';captured=$false;realTaxpayerDataUsed=$false;publicScreenshot=$false}}
  }
  $supplierStopped=$false
  if($null -ne $process) {
    try { if(-not $process.HasExited) { $process.Kill($true); $process.WaitForExit(5000) | Out-Null }; $supplierStopped=$process.HasExited } catch { }
    $process.Dispose()
  }
  if($null -ne $process -and -not $supplierStopped){$report.stage='blocked';$report['blockedReason']='ORIGINAL_PROCESS_NOT_STOPPED'}
  $report['uiaHelpersStopped']=$uiaHelpersStopped
  if($env:GITHUB_OUTPUT){
    $credentialsSafe=$installerCredentialsSafe -and $installerStopped -and $uiaHelpersStopped -and ($null -eq $process -or $supplierStopped)
    [IO.File]::AppendAllText($env:GITHUB_OUTPUT,('supplier_stopped='+$supplierStopped.ToString().ToLowerInvariant()+"`n"+'credentials_safe='+$credentialsSafe.ToString().ToLowerInvariant()+"`n"),[Text.UTF8Encoding]::new($false))
  }
  if($RuntimeHost -eq 'clr2-x86-reference' -and $null -ne $referencePreparation -and $referencePreparation.status -eq 'prepared') {
    try {
      $report.referenceHostResult=Get-HtkkSafeReferenceResult -ResultPath $referencePreparation.resultPath
      Assert-Hash $exe '411141d2e728a45f4a35a876afb169d0ac2450de2499e8a1f43ac29ab6401938'
      Assert-Hash (Join-Path (Split-Path $exe) 'TAX.HTKK.Business.dll') '281689aaa7df4db33d0debcfc61d32c0c318bb871d4a19a0277d871a7c04bba7'
      Assert-Hash ($exe+'.config') 'b3547d6a6a61fd6e8e8b64c8976e8702aa94a2b5a44a1cf394c5486162297047'
      if($GuiAutomation -in @('gtgt-export-inspect','gtgt-roundtrip-inspect','gtgt-web-import-inspect','gtgt-annex12-export-inspect')) {
        Assert-Hash (Join-Path (Split-Path $exe) 'TAX.HTKK.Utilities.dll') 'ccc35605a4d3bb235f896d6ab43cec4c6543a404159cf10897a57cba23d817ec'
        Assert-Hash (Join-Path (Split-Path $exe) 'FarPoint.Win.Spread.dll') '2e7a0d4fc1ef6f219dd3a237ae6b26549ad03541d58da6f45d638309d2fa4c50'
        Assert-Hash (Join-Path (Split-Path $exe) 'TAX.HTKK.ComputeHash.dll') 'd9d63921565ea2039109ad63d71977dcf56889cd83851977a0c712873ab687f5'
      }
      $report.originalSourcesUnmodified=$true
    } catch { $report.originalSourcesUnmodified=$false; $report.stage='blocked'; $report['blockedReason']='ORIGINAL_SOURCE_CHANGED' }
  }
  if($GuiAutomation -eq 'gtgt-export-inspect' -and $report.stage -eq 'synthetic-original-gtgt-export-inspected') {
    $evidenceCreated=$false
    $evidenceStage='preconditions'
    try {
      $gui=$report.guiReferenceAutomation
      if(-not $supplierStopped -or -not $report.originalSourcesUnmodified -or $gui.status -cne 'matched' -or $env:GITHUB_REPOSITORY -cne 'congminh1254/htkk_builder' -or $env:GITHUB_SHA -cnotmatch '^[0-9a-f]{40}$' -or $env:GITHUB_RUN_ID -notmatch '^[0-9]{1,20}$') { throw 'STAGING_NOT_VERIFIED' }
      foreach($flag in @('exportSchemaPinnedVerified','exportCommandInvoked','exportSelectorMatched','exportButtonInvoked','exportDialogMatched','exportDestinationFresh','exportFilenameKeyboardCommitted','exportDialogSubmitted','exportFileExists','exportXmlRootMatched','exportSyntheticIdentityMatched','exportSuccessAcknowledged','exportOriginalPathMatched')) { if($gui[$flag] -isnot [bool] -or -not $gui[$flag]) { throw 'STAGING_NOT_VERIFIED' } }
      $evidenceStage='source-file'
      # Original DATAFILES is beside Project, not inside Project.
      $original=Join-Path (Split-Path (Split-Path $exe)) 'DataFiles/9999999997/reference-output/01GTGT.xml'
      $originalFile=Get-Item -LiteralPath $original
      foreach($directory in @($originalFile.Directory,$originalFile.Directory.Parent,$originalFile.Directory.Parent.Parent)) { if($directory.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'STAGING_NOT_VERIFIED' } }
      if($originalFile.Attributes -band [IO.FileAttributes]::ReparsePoint -or $originalFile.Length -lt 1 -or $originalFile.Length -gt 262144 -or $originalFile.Length -ne $gui.exportBytes) { throw 'STAGING_NOT_VERIFIED' }
      Assert-Hash $original $gui.exportSha256
      $evidenceStage='fresh-destination'
      $evidence=Join-Path $env:RUNNER_TEMP 'htkk-gtgt-export-evidence'
      if(Test-Path -LiteralPath $evidence) { throw 'STAGING_NOT_VERIFIED' }
      New-Item -ItemType Directory -Path $evidence | Out-Null
      $evidenceCreated=$true
      $evidenceStage='copy-original'
      Copy-Item -LiteralPath $original -Destination (Join-Path $evidence '01GTGT.xml')
      Assert-Hash (Join-Path $evidence '01GTGT.xml') $gui.exportSha256
      $evidenceStage='provenance'
      [ordered]@{format='htkk-gtgt-export-staging-v1';builderRepository='congminh1254/htkk_builder';builderCommit=$env:GITHUB_SHA;runId=$env:GITHUB_RUN_ID;sourceVersion='5.8.1';runtimeHost='clr2-x86-reference';originalSourcesUnmodified=$true;inputsSynthetic=$true;guiExportInvoked=$true;originalExportSucceeded=$true;originalExporterValidatedSchema=$true;fullRoundTrip=$false;originalOutputSha256=$gui.exportSha256;originalOutputBytes=[int]$originalFile.Length} | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath (Join-Path $evidence 'provenance.json') -Encoding utf8NoBOM
      $report.privateGtgtExportEvidence=@{status='staged';stage='complete';supplierStopped=[bool]$supplierStopped;rawBytesPreserved=$true;fullRoundTrip=$false}
    } catch {
      if($evidenceCreated) { Remove-Item -LiteralPath $evidence -Recurse -Force -ErrorAction SilentlyContinue }
      $report.privateGtgtExportEvidence=@{status='not-staged';stage=$evidenceStage;supplierStopped=[bool]$supplierStopped;rawBytesPreserved=$false;fullRoundTrip=$false}
    }
  }
  if($GuiAutomation -eq 'gtgt-annex12-export-inspect' -and $report.stage -eq 'synthetic-original-gtgt-annex12-export-inspected') {
    $annexStageFailure='NOT_STAGED';$annexContractCode='none';$annexContractField=-1
    try {
      if(-not $supplierStopped -or -not $report.originalSourcesUnmodified){throw 'STAGING_NOT_VERIFIED'}
      $annexStageInput=[ordered]@{installedRoot=(Split-Path (Split-Path $exe));gui=$report.guiReferenceAutomation;supplierStopped=[bool]$supplierStopped;sourcesUnmodified=[bool]$report.originalSourcesUnmodified} | ConvertTo-Json -Depth 6 -Compress
      $annexStageOutput=$annexStageInput | & python (Join-Path $PSScriptRoot 'stage-htkk-annex12-export.py')
      $annexStageExit=$LASTEXITCODE
      $annexStageResult=$annexStageOutput | ConvertFrom-Json -AsHashtable
      if($annexStageExit -ne 0){if($annexStageResult.format -ceq 'htkk-annex12-export-publication-status-v1' -and $annexStageResult.status -ceq 'rejected' -and $annexStageResult.code -cin @('PROVENANCE','STAGING','HASH','XML_CONTRACT','IO','INTERNAL','BUILDER','MANIFEST','SOURCE_COMMIT')){$annexStageFailure=$annexStageResult.code;if($annexStageFailure -ceq 'XML_CONTRACT' -and $annexStageResult.contractCode -cin @('ATTRIBUTES','BASE_PRIVACY','CONTENT','DECLARATION','ENCODING','LEAF_COUNT','LIMIT','NAMESPACE','SIZE','STRUCTURE','VALUE','XML_PARSE') -and ($annexStageResult.contractFieldId -is [int] -or $annexStageResult.contractFieldId -is [long]) -and $annexStageResult.contractFieldId -ge 0 -and $annexStageResult.contractFieldId -lt 46){$annexContractCode=$annexStageResult.contractCode;$annexContractField=$annexStageResult.contractFieldId}};throw 'STAGING_NOT_VERIFIED'}
      if($annexStageResult.format -cne 'htkk-annex12-export-staging-status-v1' -or $annexStageResult.status -cne 'staged' -or $annexStageResult.rawBytesPreserved -isnot [bool] -or -not $annexStageResult.rawBytesPreserved -or $annexStageResult.independentSchemaVerification -isnot [bool] -or -not $annexStageResult.independentSchemaVerification){throw 'STAGING_NOT_VERIFIED'}
      $report.privateAnnex12ExportEvidence=@{status='staged';supplierStopped=$true;rawBytesPreserved=$true;independentSchemaVerification=$true;nativeAnnexRoundTripVerified=$false;fullCompatibilityVerified=$false}
    } catch { $report.privateAnnex12ExportEvidence=@{status='not-staged';failureCode=$annexStageFailure;contractCode=$annexContractCode;contractFieldId=$annexContractField;supplierStopped=[bool]$supplierStopped;rawBytesPreserved=$false;independentSchemaVerification=$false;nativeAnnexRoundTripVerified=$false;fullCompatibilityVerified=$false} }
  }
  if($GuiAutomation -eq 'gtgt-web-import-inspect' -and $report.stage -eq 'synthetic-original-gtgt-web-import-inspected') {
    $nativeEvidenceCreated=$false;$nativeEvidenceStage='preconditions'
    try {
      $gui=$report.guiReferenceAutomation
      if(-not $supplierStopped -or -not $report.originalSourcesUnmodified -or $gui.status -cne 'matched' -or $env:GITHUB_REPOSITORY -cne 'congminh1254/htkk_builder' -or $env:GITHUB_SHA -cnotmatch '^[0-9a-f]{40}$' -or $env:GITHUB_RUN_ID -cnotmatch '^[0-9]{1,20}$' -or $env:WEB_ARTIFACT_COMMIT -cnotmatch '^[0-9a-f]{40}$' -or $env:EXPECTED_WEB_SOURCE_SHA -cnotmatch '^[0-9a-f]{40}$' -or $gui.webSourceSha -cne $env:EXPECTED_WEB_SOURCE_SHA -or $gui.webCaseId -cne $env:EXPECTED_WEB_CASE_ID -or $gui.webCaseId -cnotin @('01GTGT-zero-M10-2026','01GTGT-sale10-M10-2026','01GTGT-sale10-half-M10-2026','01GTGT-sale10-manual-M10-2026','01GTGT-sale5-half-M10-2026','01GTGT-sale5-manual-M10-2026','01GTGT-noactivity-zero-M10-2026','01GTGT-noactivity-reset-sale10-M10-2026','01GTGT-noactivity-cancel-sale10-M10-2026','01GTGT-noactivity-uncheck-sale10-M10-2026','01GTGT-noactivity-keep-credit-M10-2026','01GTGT-zero-Q4-2026','01GTGT-native-import-sale10-M10-2026') -or $gui.webTaxLeafCount -ne 70 -or $gui.gtgtCaseMoneyCount -ne 27 -or $gui.gtgtCaseMismatchMask -ne 0 -or $gui.webImportInputSha256 -cnotmatch '^[0-9a-f]{64}$' -or $gui.roundtripReexportSha256 -cnotmatch '^[0-9a-f]{64}$') { throw 'STAGING_NOT_VERIFIED' }
      foreach($flag in @('sourcePinsVerified','webInputVerified','gtgtCaseMoneyMatched','webTaxValuesMatched','webCreationDateMatchedNativeBaseline','webServiceIdentityMatched','exportSchemaPinnedVerified','exportCommandInvoked','exportSelectorMatched','exportButtonInvoked','exportDialogMatched','exportDestinationFresh','exportFilenameKeyboardCommitted','exportDialogSubmitted','exportFileExists','exportXmlRootMatched','exportSyntheticIdentityMatched','exportSuccessAcknowledged','exportOriginalPathMatched','roundtripImportCommandInvoked','roundtripImportDialogMatched','roundtripImportKeyboardCommitted','roundtripImportDialogSubmitted','roundtripImportPathMatched','roundtripImportSheetMatched','roundtripImportSucceeded','roundtripReexportCommandInvoked','roundtripReexportSucceeded')) { if($gui[$flag] -isnot [bool] -or -not $gui[$flag]) { throw 'STAGING_NOT_VERIFIED' } }
       if($gui.webCaseId -cin @('01GTGT-noactivity-zero-M10-2026','01GTGT-noactivity-reset-sale10-M10-2026','01GTGT-noactivity-cancel-sale10-M10-2026','01GTGT-noactivity-uncheck-sale10-M10-2026','01GTGT-noactivity-keep-credit-M10-2026')){foreach($flag in @('gtgtCt21CaseMatched','gtgtCt21ConfirmationMatched','gtgtCt21LocksMatched','gtgtCt21BeforeExportMatched','gtgtCt21AfterImportMatched')){if($gui[$flag] -isnot [bool] -or -not $gui[$flag]){throw 'STAGING_NOT_VERIFIED'}}}
       if($gui.webCaseId -ceq '01GTGT-noactivity-uncheck-sale10-M10-2026' -and ($gui.gtgtCt21UncheckMatched -isnot [bool] -or -not $gui.gtgtCt21UncheckMatched)){throw 'STAGING_NOT_VERIFIED'}
      $nativeEvidenceStage='input-provenance'
      $inputDirectory=Join-Path $env:RUNNER_TEMP 'htkk-web-reference-input'
      $inputManifestPath=Join-Path $inputDirectory 'manifest.json'
      foreach($path in @($inputDirectory,$inputManifestPath)) {if(-not (Test-Path -LiteralPath $path) -or ((Get-Item -LiteralPath $path).Attributes -band [IO.FileAttributes]::ReparsePoint)){throw 'STAGING_NOT_VERIFIED'}}
      if((Get-Item -LiteralPath $inputManifestPath).Length -gt 16384){throw 'STAGING_NOT_VERIFIED'}
      $inputManifest=Get-Content -LiteralPath $inputManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
      if($inputManifest.sourceRepository -cne 'congminh1254/htkk_web' -or $inputManifest.sourceCommit -cne $gui.webSourceSha -or $inputManifest.caseId -cne $gui.webCaseId -or $inputManifest.xmlSha256 -cne $gui.webImportInputSha256 -or $inputManifest.inputsSynthetic -isnot [bool] -or -not $inputManifest.inputsSynthetic){throw 'STAGING_NOT_VERIFIED'}
      $nativeEvidenceStage='source-file'
      $nativeOriginal=Join-Path (Split-Path (Split-Path $exe)) 'DataFiles/9999999997/reference-output/01GTGT-roundtrip.xml'
      $nativeFile=Get-Item -LiteralPath $nativeOriginal
      foreach($directory in @($nativeFile.Directory,$nativeFile.Directory.Parent,$nativeFile.Directory.Parent.Parent)) {if($directory.Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'STAGING_NOT_VERIFIED'}}
      if($nativeFile.Attributes -band [IO.FileAttributes]::ReparsePoint -or $nativeFile.Length -lt 1 -or $nativeFile.Length -gt 262144 -or $nativeFile.Length -ne $gui.roundtripReexportBytes){throw 'STAGING_NOT_VERIFIED'}
      Assert-Hash $nativeOriginal $gui.roundtripReexportSha256
      $nativeEvidenceStage='fresh-destination'
      $nativeEvidence=Join-Path $env:RUNNER_TEMP 'htkk-web-native-output'
      if((Get-Item -LiteralPath $env:RUNNER_TEMP).Attributes -band [IO.FileAttributes]::ReparsePoint -or (Test-Path -LiteralPath $nativeEvidence)){throw 'STAGING_NOT_VERIFIED'}
      New-Item -ItemType Directory -Path $nativeEvidence | Out-Null;$nativeEvidenceCreated=$true
      $nativeEvidenceStage='copy-original'
      Copy-Item -LiteralPath $nativeOriginal -Destination (Join-Path $nativeEvidence '01GTGT-native.xml')
      Assert-Hash (Join-Path $nativeEvidence '01GTGT-native.xml') $gui.roundtripReexportSha256
      Assert-Hash $nativeOriginal $gui.roundtripReexportSha256
      if((Get-Item -LiteralPath (Join-Path $nativeEvidence '01GTGT-native.xml')).Length -ne $gui.roundtripReexportBytes){throw 'STAGING_NOT_VERIFIED'}
      $nativeEvidenceStage='provenance'
      [ordered]@{format='htkk-web-native-output-staging-v1';builderRepository='congminh1254/htkk_builder';builderCommit=$env:GITHUB_SHA;runId=$env:GITHUB_RUN_ID;sourceRepository='congminh1254/htkk_web';sourceCommit=$gui.webSourceSha;sourceVersion='5.8.1';runtimeHost='clr2-x86-reference';caseId=$gui.webCaseId;inputsSynthetic=$true;originalProcessStopped=$true;originalSourcesUnmodified=$true;originalExportSucceeded=$true;originalImportSucceeded=$true;originalReexportSucceeded=$true;originalExporterValidatedSchema=$true;webTaxComparisonPassed=$true;webTaxCheckedLeafCount=70;webImportInputSha256=$gui.webImportInputSha256;originalOutputSha256=$gui.roundtripReexportSha256;originalOutputBytes=[int]$nativeFile.Length;artifactCommit=$env:WEB_ARTIFACT_COMMIT;creationDateRule='native-export-current-date';fullRoundTrip=$false} | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath (Join-Path $nativeEvidence 'provenance.json') -Encoding utf8NoBOM
      $report.privateWebNativeOutputEvidence=@{status='staged';stage='complete';supplierStopped=[bool]$supplierStopped;rawBytesPreserved=$true;fullRoundTrip=$false}
    } catch {
      if($nativeEvidenceCreated){Remove-Item -LiteralPath $nativeEvidence -Recurse -Force -ErrorAction SilentlyContinue}
      $report.privateWebNativeOutputEvidence=@{status='not-staged';stage=$nativeEvidenceStage;supplierStopped=[bool]$supplierStopped;rawBytesPreserved=$false;fullRoundTrip=$false}
    }
  }
  foreach($registration in $registrationProcesses) { try { $registration.Dispose() } catch { } }
  foreach($rule in $firewallNames) { Remove-NetFirewallRule -DisplayName $rule -ErrorAction SilentlyContinue }
  foreach($owned in $referenceOwnedFiles) { Remove-Item -LiteralPath $owned -Force -ErrorAction SilentlyContinue }
  $safe = $report | ConvertTo-Json -Depth 5
  Write-Output $safe
  if ($env:GITHUB_STEP_SUMMARY) { Add-Content -LiteralPath $env:GITHUB_STEP_SUMMARY -Value ('```json' + "`n" + $safe + "`n" + '```') }
  Remove-Item -LiteralPath $work -Recurse -Force -ErrorAction SilentlyContinue
}
if ($report.stage -eq 'blocked') { exit 1 }
