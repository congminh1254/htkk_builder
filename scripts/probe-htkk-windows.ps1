# No tax data, credentials, screenshots or installer logs are published.
[CmdletBinding()]
param([switch]$InstallAndProbe)
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
Set-StrictMode -Version Latest
$report = [ordered]@{
  version = '5.8.1'; stage = 'started'; sourceHashesVerified = $false
  officialCabMatchesMirror = $false; msiAuthenticodeValid = $false
  netFx35Present = $false; installExitCode = $null
  processStarted = $false; processAliveAfterWait = $false; windowObserved = $false
  runnerSessionId = $null; appSessionId = $null; userInteractive = [Environment]::UserInteractive
  appArchitecture = 'unknown'; preexistingHtkkProcessCount = 0; preexistingHtkkSameSessionCount = 0
  descendantScope = 'created-at-or-after-root-start'; verifiedMicrosoftChildImages = @(); unknownChildImageInspectionFailures = 0
  threadDesktop = 'unavailable'; desktopWindowScope = 'current-thread-desktop'
  appVisibleWindowCount = 0; appHiddenWindowCount = 0; allVisibleWindowCount = 0
  childProcessCount = 0; childVisibleWindowCount = 0; childHiddenWindowCount = 0
  mainWindowHandlePresent = $false; startupWaitSeconds = 0; startupContext = 'not-probed'
  uiaStatus = 'not-probed'; uiaWindowCount = 0; uiaControlCount = 0; loginReady = $false
  uiaControlTypeCounts = @{}; uiaAllowedControlIds = @(); uiaStaticLabels = @()
  uiaHelperEncoding = 'utf8-bom'; uiaHelperExitCode = $null; uiaHelperParseErrorCount = 0; uiaHelperFailureCategory = 'not-probed'
  descendantProcessKinds = @{ HTKK = 0; msiexec = 0; WerFault = 0; rundll32 = 0; dllhost = 0; console = 0; shell = 0; browser = 0; updater = 0; debugger = 0; errorReporting = 0; other = 0 }
  ownedWindowKinds = @{}; nativeDialogCueCounts = @{}; rootAppWindowObserved = $false; uiaWindowCategories = @()
  uiaLegacyRoleCounts = @{}; uiaLegacyPatternAvailable = $false; uiaProviderProcessMismatchCount = 0; uiaViews = @()
  applicationEvents = $null
  taxIdOracle = $null
  runtimeRoundTrip = $false; taxDataUsed = $false; screenshotsPublished = $false
}
$work = Join-Path $env:RUNNER_TEMP ('htkk-probe-' + [guid]::NewGuid().ToString('N'))
$process = $null
function Assert-Hash([string]$Path, [string]$Expected) {
  if ((Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $Expected) { throw 'SOURCE_HASH_MISMATCH' }
}
function Get-PinnedFile([string]$Url, [string]$Path, [string]$Expected) {
  # Public URLs only. No relay token, cookie, auth header or TLS override.
  Invoke-WebRequest -Uri $Url -OutFile $Path -TimeoutSec 120 -MaximumRedirection 8 -UserAgent 'HotroKeKhai-ReadinessProbe/1.0'
  Assert-Hash $Path $Expected
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
function Get-HtkkSafeApplicationEvents([datetime]$ApplicationStartTime) {
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
      if ($privateText -notmatch '(?i)(?<![A-Za-z0-9_])HTKK\.exe(?![A-Za-z0-9_])') { continue }
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
# Isolated Windows PowerShell helper: UIAutomation is a desktop .NET Framework assembly.
# Only process-scoped UIA controls are inspected, never ValuePattern or arbitrary names in output.
function Get-HtkkSafeUiDiagnostics([int]$AppProcessId, [int[]]$Descendants, [string]$TemporaryDirectory) {
  $helper = Join-Path $TemporaryDirectory 'uia-helper.ps1'
  $resultPath = Join-Path $TemporaryDirectory 'uia-safe.json'
  @'
param([string]$ProcessIds, [string]$OutputFile)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$result = [ordered]@{ status = 'unavailable'; windows = 0; controls = 0; loginReady = $false; types = @{}; ids = @(); labels = @(); categories = @(); legacyRoles = @{}; providerProcessMismatchCount = 0; legacyPatternAvailable = $false; views = @('children','raw-walker','control-walker','native-static-dialog') }
try {
  Add-Type -AssemblyName UIAutomationClient
  Add-Type -AssemblyName UIAutomationTypes
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
  $top = [System.Windows.Automation.AutomationElement]::RootElement.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)
  foreach ($window in $top) {
    try {
      if ($owners.Contains($window.Current.ProcessId)) { $queue.Enqueue($window); $result.windows++ }
    } catch { }
  }
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
  $result.ids = @($ids | Sort-Object)
  $result.labels = @($labels | Sort-Object)
  $result.categories = @($categories | Sort-Object)
  $result.loginReady = ($ids.Contains('cboMaSoThue') -and ($ids.Contains('btnMaSoMoi') -or $labels.Contains('Mã số thuế'))) -or ($labels.Contains('Mã số thuế') -and $labels.Contains('Đăng nhập') -and $labels.Contains('Mã số mới'))
  $result.status = if ($queue.Count -gt 0) { 'bounded-partial' } else { 'scanned' }
} catch { $result.status = 'uia-unavailable' }
$result | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $OutputFile -Encoding UTF8
'@ | Set-Content -LiteralPath $helper -Encoding utf8BOM
  $diagnostics = @{ status = 'uia-helper-failed'; windows = 0; controls = 0; loginReady = $false; types = @{}; ids = @(); labels = @(); helperEncoding = 'utf8-bom'; helperExitCode = $null; helperParseErrorCount = 0; helperFailureCategory = 'none' }
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
  $arguments = @('-STA','-NoProfile','-NonInteractive','-ExecutionPolicy','RemoteSigned','-File',"`"$helper`"",'-ProcessIds',$ownerList,'-OutputFile',"`"$resultPath`"")
  $helperProcess = Start-Process -FilePath $legacy -ArgumentList $arguments -PassThru -RedirectStandardOutput (Join-Path $TemporaryDirectory 'uia-private.stdout') -RedirectStandardError (Join-Path $TemporaryDirectory 'uia-private.stderr')
  # Retain the process handle before waiting so ExitCode remains available after a fast exit.
  $null = $helperProcess.Handle
  if (-not $helperProcess.WaitForExit(15000)) {
    Stop-Process -Id $helperProcess.Id -Force -ErrorAction SilentlyContinue
    $diagnostics.status = 'uia-timeout'; $diagnostics.helperFailureCategory = 'helper-timeout'
    return $diagnostics
  }
  $diagnostics.helperExitCode = $helperProcess.ExitCode
  if ($helperProcess.ExitCode -ne 0) {
    # Inspect stderr privately only to choose a fixed enum. Never emit its content.
    $privateError = Get-Content -LiteralPath (Join-Path $TemporaryDirectory 'uia-private.stderr') -Raw -ErrorAction SilentlyContinue
    $diagnostics.helperFailureCategory = if ($privateError -match 'ParserError') { 'legacy-parser-error' } else { 'helper-nonzero-exit' }
    return $diagnostics
  }
  if (-not (Test-Path -LiteralPath $resultPath)) {
    $diagnostics.helperFailureCategory = 'helper-result-missing'
    return $diagnostics
  }
  try {
    $safeUi = Get-Content -LiteralPath $resultPath -Raw -Encoding UTF8 | ConvertFrom-Json -AsHashtable
    foreach ($key in @('helperEncoding','helperExitCode','helperParseErrorCount','helperFailureCategory')) { $safeUi[$key] = $diagnostics[$key] }
    if ($safeUi.status -eq 'uia-unavailable') { $safeUi.helperFailureCategory = 'uia-provider-unavailable' }
    return $safeUi
  } catch {
    $diagnostics.helperFailureCategory = 'helper-result-invalid'
    return $diagnostics
  }
}

try {
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
  $install = Start-Process -FilePath "$env:WINDIR\System32\msiexec.exe" -ArgumentList @('/i', "`"$msi`"", '/qn', '/norestart', 'ISCHECKFORPRODUCTUPDATES=0', '/L*v', "`"$(Join-Path $work 'install-private.log')`"") -Wait -PassThru
  $report.installExitCode = $install.ExitCode
  if ($install.ExitCode -notin @(0, 3010)) { throw 'MSI_INSTALL_FAILED' }
  if ($install.ExitCode -eq 3010) { throw 'REBOOT_REQUIRED_PROBE_NOT_RUN' }
  $candidates = @("${env:ProgramFiles}\HTKK\Project\HTKK.exe", "${env:ProgramFiles(x86)}\HTKK\Project\HTKK.exe", 'C:\HTKK\Project\HTKK.exe')
  $exe = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
  if (-not $exe) { throw 'INSTALLED_HTKK_NOT_FOUND' }
  Assert-Hash $exe '411141d2e728a45f4a35a876afb169d0ac2450de2499e8a1f43ac29ab6401938'
  . (Join-Path $PSScriptRoot 'Test-HtkkTaxIdOracle.ps1')
  $report.taxIdOracle = Invoke-HtkkTaxIdOracle -ProjectDirectory (Split-Path $exe) -TemporaryDirectory $work
  # Prevent the application from contacting its legacy update endpoint during the startup probe.
  New-NetFirewallRule -DisplayName 'HTKK readiness probe outbound block' -Direction Outbound -Program $exe -Action Block | Out-Null
  $report.stage = 'startup'
  $preexistingHtkk = @(Get-Process -Name HTKK -ErrorAction SilentlyContinue)
  $report.preexistingHtkkProcessCount = $preexistingHtkk.Count
  $runnerSession = [Diagnostics.Process]::GetCurrentProcess().SessionId
  foreach ($existing in $preexistingHtkk) { try { if ($existing.SessionId -eq $runnerSession) { $report.preexistingHtkkSameSessionCount++ } } catch { } }
  $applicationStartTime = Get-Date
  $process = Start-Process -FilePath $exe -WorkingDirectory (Split-Path $exe) -PassThru
  $report.processStarted = $true
  Initialize-WindowDiagnostics
  $report.runnerSessionId = [System.Diagnostics.Process]::GetCurrentProcess().SessionId
  $report.appSessionId = $process.SessionId
  $report.threadDesktop = [HtkkWindowDiagnostics]::DesktopKind()
  try { $report.appArchitecture = [HtkkWindowDiagnostics]::Architecture($process.Handle) } catch { $report.appArchitecture = 'unknown' }
  $rootStartTime = $process.StartTime
  $startupClock = [System.Diagnostics.Stopwatch]::StartNew()
  do {
    $process.Refresh()
    $report.processAliveAfterWait = -not $process.HasExited
    $report.mainWindowHandlePresent = $report.processAliveAfterWait -and ($process.MainWindowHandle -ne [IntPtr]::Zero)
    $children = @(Get-DescendantProcessIds -AppProcessId $process.Id -RootStartTime $rootStartTime)
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
  $report.applicationEvents = Get-HtkkSafeApplicationEvents -ApplicationStartTime $applicationStartTime
  $report.ownedWindowKinds = [HtkkWindowDiagnostics]::OwnedWindowKinds($process.Id, [int[]]$children)
  $report.nativeDialogCueCounts = [HtkkWindowDiagnostics]::FixedDialogCues($process.Id, [int[]]$children)
  $report.startupContext = if ($report.windowObserved) { 'visible-app-or-child-window' }
    elseif ($report.appSessionId -ne $report.runnerSessionId) { 'different-process-session' }
    elseif ($report.runnerSessionId -eq 0) { 'session-zero' }
    elseif (-not $report.userInteractive) { 'noninteractive-environment' }
    elseif ($report.allVisibleWindowCount -eq 0) { 'no-visible-windows-on-current-desktop' }
    elseif (($report.appHiddenWindowCount + $report.childHiddenWindowCount) -gt 0) { 'only-hidden-app-windows' }
    else { 'no-app-windows-on-current-desktop' }
  if (-not $report.windowObserved) { throw 'STARTUP_WINDOW_NOT_OBSERVED' }
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
    $report.uiaHelperParseErrorCount = $uia.helperParseErrorCount; $report.uiaHelperFailureCategory = $uia.helperFailureCategory
  } catch { $report.uiaStatus = 'uia-helper-failed'; $report.uiaHelperFailureCategory = 'helper-wrapper-failure' }
  if ($report.taxIdOracle.status -ne 'matched') { throw 'TAX_ID_ORACLE_NOT_VERIFIED' }
  $report.stage = 'startup-window-observed'
} catch {
  # Only allow fixed diagnostic enums into the public summary. Never dump remote/installer output.
  $known = @('TAX_ID_ORACLE_NOT_VERIFIED','SOURCE_HASH_MISMATCH','TRUSTED_RUNNER_7ZIP_MISSING','OFFICIAL_CAB_EXTRACTION_FAILED','MSI_AUTHENTICODE_NOT_VALID','MSI_PUBLISHER_SERIAL_MISMATCH','MSI_PUBLISHER_SUBJECT_MISMATCH','RUNNER_SIGNTOOL_MISSING','MSI_SIGNTOOL_VERIFICATION_FAILED','NETFX35_MISSING_NO_BOOTSTRAPPER_EXECUTED','MSI_INSTALL_FAILED','REBOOT_REQUIRED_PROBE_NOT_RUN','INSTALLED_HTKK_NOT_FOUND','STARTUP_WINDOW_NOT_OBSERVED')
  $reason = $_.Exception.Message
  $report['blockedReason'] = if ($reason -in $known) { $reason } else { 'HOST_NETWORK_OR_TOOL_FAILURE' }
  $report.stage = 'blocked'
} finally {
  if ($null -ne $process -and -not $process.HasExited) { Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue }
  $safe = $report | ConvertTo-Json -Depth 3
  Write-Output $safe
  if ($env:GITHUB_STEP_SUMMARY) { Add-Content -LiteralPath $env:GITHUB_STEP_SUMMARY -Value ('```json' + "`n" + $safe + "`n" + '```') }
  Remove-Item -LiteralPath $work -Recurse -Force -ErrorAction SilentlyContinue
}
if ($report.stage -eq 'blocked') { exit 1 }
