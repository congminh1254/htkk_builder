# Private-only original HTKK window capture after the fixed synthetic login interaction.
# The original application can display bundled defaults: pixels are not claimed all synthetic.
function Save-HtkkSyntheticWindowDiagnostic {
 [CmdletBinding()]
 param([Parameter(Mandatory=$true)][int]$RootProcessId,[Parameter(Mandatory=$true)][datetime]$RootStartTime,[Parameter(Mandatory=$true)][string]$ExpectedHtkkExecutable,[Parameter(Mandatory=$true)]$LoginReport,[ValidatePattern('^[0-9]{1,20}$')][string]$RunId)
 $safe=[ordered]@{status='not-captured';captured=$false;sha256=$null;realTaxpayerDataUsed=$false;sourceDefaultsMayBeVisible=$true;publicScreenshot=$false}
 $owned=$null;$bitmap=$null;$graphics=$null;$stream=$null
 try {
  foreach($key in @('newIdClicked','inputVerified','loginClicked','loginHidden','fixtureDirectoryCreated')){if($LoginReport[$key] -isnot [bool] -or $LoginReport[$key] -ne $true){$safe.status='synthetic-transition-not-established';return $safe}}
  if($LoginReport.fixtureDirectoryPreexisting -isnot [bool] -or $LoginReport.fixtureDirectoryPreexisting){$safe.status='synthetic-directory-not-fresh';return $safe}
  $directory=Join-Path ([IO.Path]::GetFullPath($env:RUNNER_TEMP)) 'htkk-windows-diagnostic'
  if(Test-Path -LiteralPath $directory){$safe.status='diagnostic-directory-already-exists';return $safe}
  $owned=Get-Process -Id $RootProcessId -ErrorAction Stop;$null=$owned.Handle
  if($owned.HasExited -or $owned.StartTime.ToUniversalTime().Ticks -ne $RootStartTime.ToUniversalTime().Ticks){$safe.status='original-root-not-matched';return $safe}
  $image=[IO.Path]::GetFullPath($owned.MainModule.FileName)
  if(-not [string]::Equals($image,[IO.Path]::GetFullPath($ExpectedHtkkExecutable),[StringComparison]::OrdinalIgnoreCase) -or [IO.Path]::GetFileName($image) -ine 'HTKK.exe'){return $safe}
  if((Get-Item -LiteralPath $image).Attributes -band [IO.FileAttributes]::ReparsePoint){return $safe}
  if((Get-FileHash -LiteralPath $image -Algorithm SHA256).Hash.ToLowerInvariant() -ne '411141d2e728a45f4a35a876afb169d0ac2450de2499e8a1f43ac29ab6401938'){return $safe}
  if((Get-FileHash -LiteralPath ($image+'.config') -Algorithm SHA256).Hash.ToLowerInvariant() -ne 'b3547d6a6a61fd6e8e8b64c8976e8702aa94a2b5a44a1cf394c5486162297047'){return $safe}
  if(-not ('HtkkPrivateSyntheticImage' -as [type])) {
   Add-Type -AssemblyName System.Drawing
   Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
using System.Text;
public static class HtkkPrivateSyntheticImage {
 public struct Rect { public int Left,Top,Right,Bottom; }
 private delegate bool EnumProc(IntPtr window,IntPtr unused);
 [DllImport("user32.dll")] private static extern bool EnumWindows(EnumProc callback,IntPtr unused);
 [DllImport("user32.dll")] private static extern uint GetWindowThreadProcessId(IntPtr window,out uint owner);
 [DllImport("user32.dll")] private static extern bool IsWindowVisible(IntPtr window);
 [DllImport("user32.dll",CharSet=CharSet.Unicode)] private static extern int GetClassName(IntPtr window,StringBuilder value,int size);
 [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr window,out Rect rectangle);
 [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr window,IntPtr dc,uint flags);
 public static IntPtr Find(int root) {
  IntPtr found=IntPtr.Zero;int visited=0;
  // EnumWindows follows z-order: prefer the foremost owned visible modal/form.
  EnumProc callback=(window,unused)=>{
   if(++visited>4096)return false;uint owner;GetWindowThreadProcessId(window,out owner);
   if(owner!=(uint)root||!IsWindowVisible(window))return true;
   var name=new StringBuilder(256);GetClassName(window,name,name.Capacity);string cls=name.ToString();
   if(cls!="#32770"&&!cls.StartsWith("WindowsForms10.Window.",StringComparison.OrdinalIgnoreCase))return true;
   found=window;return false;
  };EnumWindows(callback,IntPtr.Zero);GC.KeepAlive(callback);return found;
 }
}
'@
  }
  $window=[HtkkPrivateSyntheticImage]::Find($RootProcessId)
  if($window -eq [IntPtr]::Zero){$safe.status='owned-original-window-unavailable';return $safe}
  $rectangle=[HtkkPrivateSyntheticImage+Rect]::new()
  if(-not [HtkkPrivateSyntheticImage]::GetWindowRect($window,[ref]$rectangle)){return $safe}
  $width=$rectangle.Right-$rectangle.Left;$height=$rectangle.Bottom-$rectangle.Top
  if($width -lt 16 -or $height -lt 16 -or $width -gt 2000 -or $height -gt 2000){$safe.status='window-size-limit';return $safe}
  $bitmap=[Drawing.Bitmap]::new($width,$height);$graphics=[Drawing.Graphics]::FromImage($bitmap);$dc=$graphics.GetHdc()
  try{$printed=[HtkkPrivateSyntheticImage]::PrintWindow($window,$dc,2)}finally{$graphics.ReleaseHdc($dc)}
  if(-not $printed){$safe.status='owned-window-print-unavailable';return $safe}
  $stream=[IO.MemoryStream]::new();$bitmap.Save($stream,[Drawing.Imaging.ImageFormat]::Png);$bytes=$stream.ToArray()
  if($bytes.Length -gt 2000000){$safe.status='image-size-limit';return $safe}
  New-Item -ItemType Directory -Path $directory | Out-Null
  [IO.File]::WriteAllBytes((Join-Path $directory 'synthetic-login-window.png'),$bytes)
  $hash=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($bytes)).ToLowerInvariant()
  $metadata=[ordered]@{format='htkk-synthetic-login-diagnostic-v1';runId=$RunId;runtimeHost='original';scope='verified-original-htkk-root-after-synthetic-login';width=$width;height=$height;pngSha256=$hash;originalExecutableSha256='411141d2e728a45f4a35a876afb169d0ac2450de2499e8a1f43ac29ab6401938';newIdClicked=$true;fixtureDirectoryPreexisting=$false;syntheticInputVerified=$true;loginClicked=$true;loginHidden=$true;freshFixtureDirectoryCreated=$true;realTaxpayerDataUsed=$false;sourceDefaultsMayBeVisible=$true;publicScreenshot=$false}
  $metadata | ConvertTo-Json -Compress | Set-Content -LiteralPath (Join-Path $directory 'diagnostic.json') -Encoding UTF8
  $safe.status='captured-for-private-upload';$safe.captured=$true;$safe.sha256=$hash;return $safe
 }catch{$safe.status='capture-unavailable';return $safe}
 finally{if($stream){$stream.Dispose()};if($graphics){$graphics.Dispose()};if($bitmap){$bitmap.Dispose()};if($owned){$owned.Dispose()}}
}
