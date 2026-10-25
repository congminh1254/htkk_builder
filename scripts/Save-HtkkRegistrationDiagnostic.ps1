# Captures only the verified Microsoft registration information window before tax input.
# No desktop fallback, arbitrary HWND, process environment or raw text is accepted.
function Save-HtkkRegistrationDiagnostic {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory=$true)][int]$RootProcessId,
    [Parameter(Mandatory=$true)][int[]]$OwnedProcessIds,
    [Parameter(Mandatory=$true)][datetime]$RootStartTime,
    [ValidateSet('original','clr2-x86-reference')][string]$RuntimeHost='original',
    [ValidatePattern('^[0-9]{1,20}$')][string]$RunId='0'
  )
  $ErrorActionPreference='Stop'
  $safe=[ordered]@{status='not-captured';captured=$false;sha256=$null;taxDataUsed=$false;publicScreenshot=$false}
  $bitmap=$null; $graphics=$null; $stream=$null
  try {
    $temporary=[IO.Path]::GetFullPath($env:RUNNER_TEMP)
    $directory=Join-Path $temporary 'htkk-windows-diagnostic'
    if(Test-Path -LiteralPath $directory) { $safe.status='diagnostic-directory-already-exists'; return $safe }
    $snapshot=@(Get-CimInstance Win32_Process -Property ProcessId,ParentProcessId,CreationDate | Select-Object -First 4096)
    $byId=@{};foreach($entry in $snapshot){$byId[[int]$entry.ProcessId]=$entry}
    $start=$RootStartTime.ToUniversalTime()
    if(-not ('HtkkPrivateRegistrationImage' -as [type])) {
      Add-Type -AssemblyName System.Drawing
      Add-Type -TypeDefinition @'
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;
public static class HtkkPrivateRegistrationImage {
  public struct Rect { public int Left,Top,Right,Bottom; }
  private delegate bool EnumProc(IntPtr window,IntPtr unused);
  [DllImport("user32.dll")] private static extern bool EnumWindows(EnumProc callback,IntPtr unused);
  [DllImport("user32.dll")] private static extern uint GetWindowThreadProcessId(IntPtr window,out uint owner);
  [DllImport("user32.dll")] private static extern bool IsWindowVisible(IntPtr window);
  [DllImport("user32.dll",CharSet=CharSet.Unicode)] private static extern int GetClassName(IntPtr window,StringBuilder value,int size);
  [DllImport("user32.dll",CharSet=CharSet.Unicode)] private static extern int GetWindowText(IntPtr window,StringBuilder value,int size);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr window,out Rect rectangle);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr window,IntPtr dc,uint flags);
  public static IntPtr Find(int process) {
    IntPtr found=IntPtr.Zero;
    EnumProc callback=(window,unused)=>{
      uint owner;GetWindowThreadProcessId(window,out owner);
      if(owner!=(uint)process || !IsWindowVisible(window))return true;
      var name=new StringBuilder(64);var title=new StringBuilder(64);
      GetClassName(window,name,name.Capacity);GetWindowText(window,title,title.Capacity);
      if(name.ToString()=="#32770" && String.Equals(title.ToString(),"RegSvr32",StringComparison.OrdinalIgnoreCase)){found=window;return false;}
      return true;
    };
    EnumWindows(callback,IntPtr.Zero);GC.KeepAlive(callback);return found;
  }
}
'@
    }
    foreach($candidateId in $OwnedProcessIds) {
      if($candidateId -eq $RootProcessId -or -not $byId.ContainsKey($candidateId)){continue}
      $cursor=$candidateId;$descendant=$false
      for($depth=0;$depth -lt 96;$depth++) {
        if(-not $byId.ContainsKey($cursor)){break}
        $entry=$byId[$cursor]
        if($null -eq $entry.CreationDate -or $entry.CreationDate.ToUniversalTime() -lt $start){break}
        if([int]$entry.ParentProcessId -eq $RootProcessId){$descendant=$true;break}
        $cursor=[int]$entry.ParentProcessId
      }
      if(-not $descendant){continue}
      try {
        $registration=Get-Process -Id $candidateId -ErrorAction Stop
        if($registration.ProcessName -ine 'regsvr32' -or $registration.StartTime.ToUniversalTime() -lt $start){continue}
        $image=[IO.Path]::GetFullPath($registration.MainModule.FileName)
        $allowed=@((Join-Path $env:WINDIR 'System32\regsvr32.exe'),(Join-Path $env:WINDIR 'SysWOW64\regsvr32.exe'))
        if(-not ($allowed | Where-Object { [IO.Path]::GetFullPath($_) -ieq $image })){continue}
        if((Get-Item -LiteralPath $image).Attributes -band [IO.FileAttributes]::ReparsePoint){continue}
        $signature=Get-AuthenticodeSignature -LiteralPath $image
        if($signature.Status -ne 'Valid' -or $null -eq $signature.SignerCertificate -or $signature.SignerCertificate.Subject -notmatch 'Microsoft'){continue}
        if([IO.Path]::GetFileName([Diagnostics.FileVersionInfo]::GetVersionInfo($image).OriginalFilename) -ine 'regsvr32.exe'){continue}
        $window=[HtkkPrivateRegistrationImage]::Find($candidateId)
        if($window -eq [IntPtr]::Zero){continue}
        $rectangle=[HtkkPrivateRegistrationImage+Rect]::new()
        if(-not [HtkkPrivateRegistrationImage]::GetWindowRect($window,[ref]$rectangle)){continue}
        $width=$rectangle.Right-$rectangle.Left;$height=$rectangle.Bottom-$rectangle.Top
        if($width -lt 16 -or $height -lt 16 -or $width -gt 2000 -or $height -gt 2000){continue}
        $bitmap=[Drawing.Bitmap]::new($width,$height)
        $graphics=[Drawing.Graphics]::FromImage($bitmap);$dc=$graphics.GetHdc()
        try {$printed=[HtkkPrivateRegistrationImage]::PrintWindow($window,$dc,2)}finally{$graphics.ReleaseHdc($dc)}
        if(-not $printed){$safe.status='owned-window-print-unavailable';continue}
        $stream=[IO.MemoryStream]::new();$bitmap.Save($stream,[Drawing.Imaging.ImageFormat]::Png)
        $bytes=$stream.ToArray();if($bytes.Length -gt 2MB){$safe.status='image-size-limit';continue}
        # Fresh fixed directory and filenames. Never copy logs, source or the desktop.
        New-Item -ItemType Directory -Path $directory | Out-Null
        [IO.File]::WriteAllBytes((Join-Path $directory 'regsvr32-window.png'),$bytes)
        $digest=[Security.Cryptography.SHA256]::HashData($bytes)
        $hash=[Convert]::ToHexString($digest).ToLowerInvariant()
        $metadata=[ordered]@{format='htkk-registration-diagnostic-v1';runId=$RunId;runtimeHost=$RuntimeHost;scope='verified-microsoft-regsvr32-window-only';width=$width;height=$height;pngSha256=$hash;taxDataUsed=$false;publicScreenshot=$false}
        $metadata | ConvertTo-Json -Compress | Set-Content -LiteralPath (Join-Path $directory 'diagnostic.json') -Encoding UTF8
        $safe.status='captured-for-private-upload';$safe.captured=$true;$safe.sha256=$hash;return $safe
      } catch { $safe.status='capture-unavailable' }
      finally {if($stream){$stream.Dispose();$stream=$null};if($graphics){$graphics.Dispose();$graphics=$null};if($bitmap){$bitmap.Dispose();$bitmap=$null}}
    }
    return $safe
  } catch {$safe.status='capture-unavailable';return $safe}
  finally {if($stream){$stream.Dispose()};if($graphics){$graphics.Dispose()};if($bitmap){$bitmap.Dispose()}}
}
