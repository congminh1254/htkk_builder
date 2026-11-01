// Isolated reference host. No source program/config changes, private checkout or XML.
using System;using System.IO;using System.Reflection;using System.Threading;
internal static class HtkkGtgt04EventHost {
 static string startup;
 static void Stage(string value,string category){File.WriteAllText(startup,"{\"stage\":\""+value+"\",\"category\":\""+category+"\"}");}
 static string Category(Exception e){for(int i=0;i<8&&e.InnerException!=null;i++)e=e.InnerException;if(e is System.Runtime.Remoting.RemotingException)return "remoting";if(e is TypeInitializationException)return "type-init";if(e is TypeLoadException)return "type-load";if(e is FileNotFoundException)return "file-missing";if(e is FileLoadException)return "assembly-load";if(e is InvalidOperationException)return "invalid-operation";if(e is ArgumentException)return "argument";if(e is NullReferenceException)return "null-reference";return "other";}
 [STAThread]static int Main(string[] args){if(args.Length!=0)return 9;try{
  if(Environment.Version.Major!=2||IntPtr.Size!=4||Thread.CurrentThread.GetApartmentState()!=ApartmentState.STA)return 3;
  string host=Assembly.GetExecutingAssembly().Location,project=Path.GetDirectoryName(host),original=Path.Combine(project,"HTKK.exe");startup=host+".startup.json";Stage("source","none");
  if(HtkkGuiReferenceAutomation.Hash(original)!="411141d2e728a45f4a35a876afb169d0ac2450de2499e8a1f43ac29ab6401938"||HtkkGuiReferenceAutomation.Hash(original+".config")!="b3547d6a6a61fd6e8e8b64c8976e8702aa94a2b5a44a1cf394c5486162297047"||HtkkGuiReferenceAutomation.Hash(Path.Combine(project,"TAX.HTKK.Business.dll"))!="281689aaa7df4db33d0debcfc61d32c0c318bb871d4a19a0277d871a7c04bba7")return 4;
  Directory.SetCurrentDirectory(project);AppDomainSetup setup=new AppDomainSetup();setup.ApplicationBase=project;setup.ConfigurationFile=original+".config";setup.ApplicationName="HTKK.exe";setup.ShadowCopyFiles="false";
  AppDomain domain=AppDomain.CreateDomain("HTKK fixed04 event oracle",null,setup);
  Stage("profile-helper","none");HtkkGuiReferenceAutomation profile=(HtkkGuiReferenceAutomation)domain.CreateInstanceFromAndUnwrap(host,"HtkkGuiReferenceAutomation");profile.Start("profile-save");
  Stage("observer-helper","none");HtkkGtgt04EventObserver observer=(HtkkGtgt04EventObserver)domain.CreateInstanceFromAndUnwrap(host,"HtkkGtgt04EventObserver");observer.Start();
  Stage("original-entry","none");int code=domain.ExecuteAssembly(original);Stage("original-exited","none");return code;
 }catch(Exception e){try{Stage("exception",Category(e));}catch{}return 5;}}
}
