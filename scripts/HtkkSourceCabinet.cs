// Own read-only cabinet.dll bridge: member IDs never become output paths.
using System;using System.IO;using System.Collections.Generic;using System.Runtime.InteropServices;
public sealed class HtkkSourceCabinet {
 [StructLayout(LayoutKind.Sequential)] struct ERF{public int operation,type;public bool error;}
 [StructLayout(LayoutKind.Sequential)] struct Note{public int bytes;public IntPtr name,name2,name3,user,handle;public ushort date,time,attributes,set,cabinet,folder;public int error;}
 [UnmanagedFunctionPointer(CallingConvention.Cdecl)] delegate IntPtr Alloc(uint bytes);
 [UnmanagedFunctionPointer(CallingConvention.Cdecl)] delegate void Free(IntPtr pointer);
 [UnmanagedFunctionPointer(CallingConvention.Cdecl)] delegate IntPtr Open([MarshalAs(UnmanagedType.LPStr)]string path,int flags,int mode);
 [UnmanagedFunctionPointer(CallingConvention.Cdecl)] delegate uint Read(IntPtr handle,IntPtr bytes,uint count);
 [UnmanagedFunctionPointer(CallingConvention.Cdecl)] delegate uint Write(IntPtr handle,IntPtr bytes,uint count);
 [UnmanagedFunctionPointer(CallingConvention.Cdecl)] delegate int Close(IntPtr handle);
 [UnmanagedFunctionPointer(CallingConvention.Cdecl)] delegate int Seek(IntPtr handle,int distance,int origin);
 [UnmanagedFunctionPointer(CallingConvention.Cdecl)] delegate IntPtr Notify(int kind,IntPtr data);
 [DllImport("cabinet.dll",CallingConvention=CallingConvention.Cdecl),DefaultDllImportSearchPaths(DllImportSearchPath.System32)] static extern IntPtr FDICreate(Alloc a,Free f,Open o,Read r,Write w,Close c,Seek s,int cpu,ref ERF error);
 [DllImport("cabinet.dll",CallingConvention=CallingConvention.Cdecl,CharSet=CharSet.Ansi),DefaultDllImportSearchPaths(DllImportSearchPath.System32)] [return:MarshalAs(UnmanagedType.Bool)] static extern bool FDICopy(IntPtr context,string name,string directory,int flags,Notify notify,IntPtr decrypt,IntPtr user);
 [DllImport("cabinet.dll",CallingConvention=CallingConvention.Cdecl),DefaultDllImportSearchPaths(DllImportSearchPath.System32)] [return:MarshalAs(UnmanagedType.Bool)] static extern bool FDIDestroy(IntPtr context);
 sealed class State{public FileStream stream;public int index;public bool input;}
 readonly Dictionary<IntPtr,State> handles=new Dictionary<IntPtr,State>();readonly Dictionary<string,int> members=new Dictionary<string,int>(StringComparer.OrdinalIgnoreCase);readonly HashSet<int> seen=new HashSet<int>();
 readonly string cabinet,destination;readonly long[] sizes;readonly string[] paths;long next=1;bool failed;
 readonly Alloc alloc;readonly Free free;readonly Open open;readonly Read read;readonly Write write;readonly Close close;readonly Seek seek;readonly Notify notify;static readonly IntPtr Bad=new IntPtr(-1);
 HtkkSourceCabinet(string cab,string directory,string[] ids,long[] lengths){
  cabinet=Path.GetFullPath(cab);destination=Path.GetFullPath(directory);sizes=lengths;paths=new string[ids.Length];
  if(ids.Length!=lengths.Length||ids.Length==0||ids.Length>10000||!File.Exists(cabinet)||Directory.Exists(destination)||File.Exists(destination))throw new InvalidOperationException("CAB_INPUT_POLICY");long total=0;
  for(int i=0;i<ids.Length;i++){if(String.IsNullOrEmpty(ids[i])||ids[i].Length>72||!System.Text.RegularExpressions.Regex.IsMatch(ids[i],@"^[A-Za-z0-9_.]+$")||ids[i]=="."||ids[i]==".."||members.ContainsKey(ids[i])||lengths[i]<0||lengths[i]>268435456)throw new InvalidOperationException("CAB_MEMBER_POLICY");members.Add(ids[i],i);total=checked(total+lengths[i]);paths[i]=Path.Combine(destination,i.ToString("D5",System.Globalization.CultureInfo.InvariantCulture)+".bin");}
  if(total>1073741824)throw new InvalidOperationException("CAB_SIZE_POLICY");alloc=Allocate;free=Release;open=OpenCabinet;read=ReadFile;write=WriteFile;close=CloseFile;seek=SeekFile;notify=OnNote;
 }
 IntPtr Allocate(uint n){try{return n>4194304?IntPtr.Zero:Marshal.AllocHGlobal(checked((int)n));}catch{failed=true;return IntPtr.Zero;}}
 void Release(IntPtr p){if(p!=IntPtr.Zero)Marshal.FreeHGlobal(p);}
 IntPtr Add(State s){IntPtr id=new IntPtr(next++);handles.Add(id,s);return id;}
 IntPtr OpenCabinet(string path,int flags,int mode){try{if((flags & ~0x8000)!=0||!String.Equals(Path.GetFullPath(path),cabinet,StringComparison.OrdinalIgnoreCase))throw new InvalidOperationException();return Add(new State{input=true,index=-1,stream=new FileStream(cabinet,FileMode.Open,FileAccess.Read,FileShare.Read)});}catch{failed=true;return Bad;}}
 uint ReadFile(IntPtr h,IntPtr p,uint n){try{State f=handles[h];if(!f.input||n>4194304)throw new InvalidOperationException();byte[] b=new byte[(int)n];int count=f.stream.Read(b,0,b.Length);Marshal.Copy(b,0,p,count);return(uint)count;}catch{failed=true;return UInt32.MaxValue;}}
 uint WriteFile(IntPtr h,IntPtr p,uint n){try{State f=handles[h];if(f.input||n>4194304||f.stream.Position+n>sizes[f.index])throw new InvalidOperationException();byte[] b=new byte[(int)n];Marshal.Copy(p,b,0,b.Length);f.stream.Write(b,0,b.Length);return n;}catch{failed=true;return UInt32.MaxValue;}}
 int CloseFile(IntPtr h){try{State f=handles[h];handles.Remove(h);f.stream.Dispose();return 0;}catch{failed=true;return -1;}}
 int SeekFile(IntPtr h,int d,int origin){try{State f=handles[h];if(!f.input||origin<0||origin>2)throw new InvalidOperationException();long p=f.stream.Seek(d,(SeekOrigin)origin);if(p<0||p>f.stream.Length)throw new InvalidOperationException();return checked((int)p);}catch{failed=true;return -1;}}
 IntPtr OnNote(int kind,IntPtr pointer){try{Note n=(Note)Marshal.PtrToStructure(pointer,typeof(Note));if(kind==0||kind==5)return IntPtr.Zero;
  if(kind==2){string name=Marshal.PtrToStringAnsi(n.name);int i;if(name==null||!members.TryGetValue(name,out i)||seen.Contains(i)||n.bytes!=sizes[i])throw new InvalidOperationException();seen.Add(i);return Add(new State{input=false,index=i,stream=new FileStream(paths[i],FileMode.CreateNew,FileAccess.Write,FileShare.None)});}
  if(kind==3){State f=handles[n.handle];if(f.input||f.stream.Length!=sizes[f.index]||CloseFile(n.handle)!=0)throw new InvalidOperationException();return new IntPtr(1);}throw new InvalidOperationException();
 }catch{failed=true;return Bad;}}
 public static string[] Extract(string cabinet,string destination,string[] ids,long[] sizes){HtkkSourceCabinet x=new HtkkSourceCabinet(cabinet,destination,ids,sizes);IntPtr context=IntPtr.Zero;
  try{Directory.CreateDirectory(x.destination);ERF error=new ERF();context=FDICreate(x.alloc,x.free,x.open,x.read,x.write,x.close,x.seek,-1,ref error);if(context==IntPtr.Zero)throw new InvalidOperationException();bool ok=FDICopy(context,Path.GetFileName(x.cabinet),Path.GetDirectoryName(x.cabinet)+Path.DirectorySeparatorChar,0,x.notify,IntPtr.Zero,IntPtr.Zero);if(!ok||x.failed||x.seen.Count!=ids.Length)throw new InvalidOperationException();return x.paths;}catch{throw new InvalidOperationException("CAB_DATA_EXTRACTION_FAILED");}
  finally{if(context!=IntPtr.Zero)FDIDestroy(context);foreach(State f in x.handles.Values)f.stream.Dispose();x.handles.Clear();GC.KeepAlive(x);}
 }
}
