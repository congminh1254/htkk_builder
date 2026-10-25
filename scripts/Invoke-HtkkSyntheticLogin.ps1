# Native original GUI interaction with a fixed synthetic identifier only.
# No arbitrary text, control IDs, handles, source sample data or screenshots are returned.
function Invoke-HtkkSyntheticLogin {
 [CmdletBinding()]
 param([Parameter(Mandatory=$true)][int]$RootProcessId,[Parameter(Mandatory=$true)][datetime]$RootStartTime,[Parameter(Mandatory=$true)][string]$ProjectDirectory)
 $safe=[ordered]@{status='not-started';fixtureDirectoryPreexisting=$null;fixtureDirectoryCreated=$false;syntheticIdentifierOnly=$true;realTaxpayerDataUsed=$false;newIdClicked=$false;inputVerified=$false;loginClicked=$false;loginHidden=$false;profileWindowObserved=$false;nextOwnedWindowObserved=$false;nativeControlKinds=@{};postLoginControlKinds=@{};allowedLabels=@();profileInChildWindow=$false;profileRecognition='not-verified';profileMainCaptionMatched=$false;profileSaveCloseMatched=$false;profileManagedContainerCount=0;runtimeRoundTrip=$false}
 $retained=$null
 try {
  # Never reuse an installed/bundled or previous-run profile. Do not open its content.
  $fixture=Join-Path (Join-Path (Split-Path ([IO.Path]::GetFullPath($ProjectDirectory))) 'DataFiles') '9999999997'
  $safe.fixtureDirectoryPreexisting=Test-Path -LiteralPath $fixture
  if($safe.fixtureDirectoryPreexisting){$safe.status='synthetic-profile-directory-preexists';return $safe}
  $retained=Get-Process -Id $RootProcessId -ErrorAction Stop
  $null=$retained.Handle
  if($retained.HasExited -or $retained.StartTime.ToUniversalTime().Ticks -ne $RootStartTime.ToUniversalTime().Ticks){$safe.status='root-identity-not-matched';return $safe}
  if(-not ('HtkkSyntheticLoginNative' -as [type])) {
   Add-Type -TypeDefinition @'
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Text;
public static class HtkkSyntheticLoginNative {
 private delegate bool EnumProc(IntPtr window,IntPtr unused);
 [DllImport("user32.dll")] private static extern bool EnumWindows(EnumProc callback,IntPtr unused);
 [DllImport("user32.dll")] private static extern bool EnumChildWindows(IntPtr parent,EnumProc callback,IntPtr unused);
 [DllImport("user32.dll")] private static extern bool IsWindowVisible(IntPtr window);
 [DllImport("user32.dll")] private static extern bool IsWindowEnabled(IntPtr window);
 [DllImport("user32.dll")] private static extern uint GetWindowThreadProcessId(IntPtr window,out uint process);
 [DllImport("user32.dll",CharSet=CharSet.Unicode)] private static extern int GetClassName(IntPtr window,StringBuilder value,int size);
 [DllImport("user32.dll",CharSet=CharSet.Unicode,SetLastError=true)] private static extern IntPtr SendMessageTimeout(IntPtr window,uint message,UIntPtr param,StringBuilder text,uint flags,uint timeout,out UIntPtr result);
 [DllImport("user32.dll",EntryPoint="SendMessageTimeoutW",CharSet=CharSet.Unicode,SetLastError=true)] private static extern IntPtr SendTextTimeout(IntPtr window,uint message,UIntPtr param,string text,uint flags,uint timeout,out UIntPtr result);
 [DllImport("user32.dll",SetLastError=true)] private static extern bool PostMessage(IntPtr window,uint message,IntPtr param,IntPtr value);
 private static IntPtr login=IntPtr.Zero,combo=IntPtr.Zero,newId=IntPtr.Zero,submit=IntPtr.Zero;
 private static bool Owned(IntPtr window,int root){uint owner;GetWindowThreadProcessId(window,out owner);return owner==(uint)root;}
 private static string Class(IntPtr window){var value=new StringBuilder(256);GetClassName(window,value,value.Capacity);return value.ToString();}
 private static string Text(IntPtr window){var value=new StringBuilder(256);UIntPtr result;return SendMessageTimeout(window,0x000D,new UIntPtr((uint)value.Capacity),value,2,200,out result)!=IntPtr.Zero?value.ToString().Replace("&","").Trim():String.Empty;}
 private static bool IsForm(IntPtr window){return Class(window).StartsWith("WindowsForms10.Window.",StringComparison.OrdinalIgnoreCase);}
 private static string Kind(IntPtr window){string name=Class(window).ToUpperInvariant();if(name.Contains("COMBOBOX"))return "combo";if(name.Contains("BUTTON"))return "button";if(name.Contains("EDIT"))return "edit";if(name.Contains("STATIC"))return "static";if(name.Contains("SPREAD"))return "spread";if(name.StartsWith("WINDOWSFORMS10.WINDOW.",StringComparison.Ordinal))return "managed-window";return "other";}
 public static Dictionary<string,int> Counts=new Dictionary<string,int>();
 public static string[] Labels=new string[0];
 public static bool ProfileInChildWindow=false;
 public static bool ProfileMainCaptionMatched=false,ProfileSaveCloseMatched=false;
 public static int ProfileManagedContainerCount=0;
 public static string ProfileRecognition="not-verified";
 public static Dictionary<string,int> PostCounts=new Dictionary<string,int>();
 public static bool Find(int root){
  login=combo=newId=submit=IntPtr.Zero;Counts.Clear();var labels=new HashSet<string>();
  var candidates=new List<IntPtr>();EnumProc top=(window,unused)=>{if(Owned(window,root)&&IsWindowVisible(window)&&IsForm(window))candidates.Add(window);return candidates.Count<64;};EnumWindows(top,IntPtr.Zero);GC.KeepAlive(top);
  var discoveryClock=Stopwatch.StartNew();
  foreach(IntPtr form in candidates){
   if(discoveryClock.ElapsedMilliseconds>5000)break;
   var combos=new List<IntPtr>();var newIds=new List<IntPtr>();var submits=new List<IntPtr>();bool mst=false;int total=0;
   EnumProc child=(window,unused)=>{
    if(++total>2048||discoveryClock.ElapsedMilliseconds>5000)return false;if(!Owned(window,root)||!IsWindowVisible(window))return true;
    string kind=Kind(window);Counts[kind]=Counts.ContainsKey(kind)?Counts[kind]+1:1;
    string text=Text(window);if(text=="Mã số mới"||text=="Đồng ý"||text=="Mã số thuế"||text=="Đóng"||text=="Ghi")labels.Add(text);
    if(kind=="combo"&&IsWindowEnabled(window))combos.Add(window);
    if(kind=="button"&&IsWindowEnabled(window)&&text=="Mã số mới")newIds.Add(window);
    if(kind=="button"&&IsWindowEnabled(window)&&text=="Đồng ý")submits.Add(window);
    if(text=="Mã số thuế")mst=true;return true;
   };EnumChildWindows(form,child,IntPtr.Zero);GC.KeepAlive(child);
   if(mst&&combos.Count==1&&newIds.Count==1&&submits.Count==1){if(login!=IntPtr.Zero){login=IntPtr.Zero;break;}login=form;combo=combos[0];newId=newIds[0];submit=submits[0];}
  }
  Labels=new List<string>(labels).ToArray();return login!=IntPtr.Zero;
 }
 public static bool NewId(int root){return login!=IntPtr.Zero&&Owned(login,root)&&Owned(newId,root)&&IsWindowVisible(login)&&IsWindowVisible(newId)&&IsWindowEnabled(newId)&&Text(newId)=="Mã số mới"&&PostMessage(newId,0x00F5,IntPtr.Zero,IntPtr.Zero);}
 public static bool Fill(int root){
  if(login==IntPtr.Zero||!Owned(login,root)||!Owned(combo,root)||!IsWindowVisible(login)||!IsWindowVisible(combo)||!IsWindowEnabled(combo)||Kind(combo)!="combo")return false;
  UIntPtr result;if(SendTextTimeout(combo,0x000C,UIntPtr.Zero,"9999999997",2,1000,out result)==IntPtr.Zero)return false;return Text(combo)=="9999999997";
 }
 public static bool Login(int root){return login!=IntPtr.Zero&&Owned(login,root)&&Owned(submit,root)&&IsWindowVisible(login)&&IsWindowVisible(submit)&&IsWindowEnabled(submit)&&Text(combo)=="9999999997"&&Text(submit)=="Đồng ý"&&PostMessage(submit,0x00F5,IntPtr.Zero,IntPtr.Zero);}
 public static bool LoginHidden(int root){return login!=IntPtr.Zero&&Owned(login,root)&&!IsWindowVisible(login);}
 public static bool NextWindow(int root,bool profileOnly){
  bool found=false;var clock=Stopwatch.StartNew();int count=0;
  EnumProc callback=(window,unused)=>{
   if(++count>2048||clock.ElapsedMilliseconds>2000)return false;
   if(window==login||!Owned(window,root)||!IsWindowVisible(window)||!IsForm(window))return true;
   if(!profileOnly){found=true;return false;}
   if(Text(window).Contains("Thông tin doanh nghiệp/Người nộp thuế")){found=true;ProfileRecognition="source-profile-caption";return false;}
   // Original ThemMSTMoi opens source Menu100_1 in a generic-title main form.
   // FarPoint.Win.Spread is managed and can expose only generic native WinForms HWNDs.
   // Never call a generic native class proof of the managed grid's identity.
   string caption=Text(window).Replace(" ",String.Empty);
   bool mainCaption=caption=="Hỗ trợ kê khai thuế - Phiên bản 5.8.1".Replace(" ",String.Empty);
   if(mainCaption){
    ProfileMainCaptionMatched=true;int save=0,close=0,containers=0;
    EnumProc profileChild=(nested,ignored)=>{
     if(++count>2048||clock.ElapsedMilliseconds>2000)return false;
     if(!Owned(nested,root)||!IsWindowVisible(nested))return true;
     string kind=Kind(nested);
     if(kind=="managed-window"||kind=="spread")containers++;
     if(kind=="button"&&IsWindowEnabled(nested)){string value=Text(nested);if(value=="Ghi")save++;if(value=="Đóng")close++;}
     return true;
    };EnumChildWindows(window,profileChild,IntPtr.Zero);GC.KeepAlive(profileChild);
    ProfileManagedContainerCount=containers;ProfileSaveCloseMatched=save==1&&close==1;
    if(ProfileSaveCloseMatched&&containers>0){found=true;ProfileRecognition="source-startup-flow-main-caption-save-close";return false;}
   }
   // The profile may be a native MDI child rather than a top-level window.
   EnumProc child=(nested,ignored)=>{
    if(++count>2048||clock.ElapsedMilliseconds>2000)return false;
    if(Owned(nested,root)&&IsWindowVisible(nested)&&Text(nested).Contains("Thông tin doanh nghiệp/Người nộp thuế")){found=true;ProfileInChildWindow=true;ProfileRecognition="source-profile-child-caption";return false;}return true;
   };EnumChildWindows(window,child,IntPtr.Zero);GC.KeepAlive(child);return !found;
  };EnumWindows(callback,IntPtr.Zero);GC.KeepAlive(callback);return found;
 }
 public static void CountAfter(int root){
  PostCounts.Clear();int count=0;var clock=Stopwatch.StartNew();
  EnumProc top=(window,unused)=>{
   if(++count>2048||clock.ElapsedMilliseconds>2000)return false;
   if(!Owned(window,root)||!IsWindowVisible(window)||window==login)return true;
   EnumProc child=(nested,ignored)=>{if(++count>2048||clock.ElapsedMilliseconds>2000)return false;if(Owned(nested,root)&&IsWindowVisible(nested)){string kind=Kind(nested);PostCounts[kind]=PostCounts.ContainsKey(kind)?PostCounts[kind]+1:1;}return true;};EnumChildWindows(window,child,IntPtr.Zero);GC.KeepAlive(child);return true;
  };EnumWindows(top,IntPtr.Zero);GC.KeepAlive(top);
 }
}
'@
  }
  $found=[HtkkSyntheticLoginNative]::Find($RootProcessId)
  $safe.nativeControlKinds=[HtkkSyntheticLoginNative]::Counts;$safe.allowedLabels=@([HtkkSyntheticLoginNative]::Labels)
  if(-not $found){$safe.status='exact-login-controls-not-found';return $safe}
  $safe.newIdClicked=[HtkkSyntheticLoginNative]::NewId($RootProcessId)
  if(-not $safe.newIdClicked){$safe.status='new-id-not-posted';return $safe}
  Start-Sleep -Milliseconds 300
  if($retained.HasExited){$safe.status='root-exited';return $safe}
  $safe.inputVerified=[HtkkSyntheticLoginNative]::Fill($RootProcessId)
  if(-not $safe.inputVerified){$safe.status='synthetic-input-not-verified';return $safe}
  $safe.loginClicked=[HtkkSyntheticLoginNative]::Login($RootProcessId)
  if(-not $safe.loginClicked){$safe.status='login-not-posted';return $safe}
  $clock=[Diagnostics.Stopwatch]::StartNew()
  do {
   if($retained.HasExited){$safe.status='root-exited';return $safe}
   $safe.loginHidden=[HtkkSyntheticLoginNative]::LoginHidden($RootProcessId)
   $safe.profileWindowObserved=[HtkkSyntheticLoginNative]::NextWindow($RootProcessId,$true)
   $safe.nextOwnedWindowObserved=[HtkkSyntheticLoginNative]::NextWindow($RootProcessId,$false)
   if($safe.loginHidden -and $safe.profileWindowObserved){break}
   Start-Sleep -Milliseconds 500
  }while($clock.Elapsed.TotalSeconds -lt 20)
  $safe.fixtureDirectoryCreated=Test-Path -LiteralPath $fixture -PathType Container
  [HtkkSyntheticLoginNative]::CountAfter($RootProcessId)
  $safe.postLoginControlKinds=[HtkkSyntheticLoginNative]::PostCounts
  $safe.profileInChildWindow=[HtkkSyntheticLoginNative]::ProfileInChildWindow
  $safe.profileRecognition=[HtkkSyntheticLoginNative]::ProfileRecognition
  $safe.profileMainCaptionMatched=[HtkkSyntheticLoginNative]::ProfileMainCaptionMatched
  $safe.profileSaveCloseMatched=[HtkkSyntheticLoginNative]::ProfileSaveCloseMatched
  $safe.profileManagedContainerCount=[HtkkSyntheticLoginNative]::ProfileManagedContainerCount
  $safe.status=if($safe.loginHidden -and $safe.profileWindowObserved){'synthetic-profile-window-observed'}elseif($safe.loginHidden -and $safe.nextOwnedWindowObserved){'next-window-not-yet-identified'}else{'login-transition-not-verified'}
  return $safe
 }catch{$safe.status='native-login-helper-unavailable';return $safe}
 finally{if($null -ne $retained){$retained.Dispose()}}
}
