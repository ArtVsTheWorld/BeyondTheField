using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Security.Cryptography;
using System.Threading;
using System.Web.Script.Serialization;
using Frosty.Core;
using Frosty.Core.Attributes;
using FrostySdk.Interfaces;
[assembly: AssemblyTitle("Dynasty Enhancer")]
[assembly: AssemblyProduct("Dynasty Enhancer")]
[assembly: AssemblyDescription("Native Dynasty Social Media: weekly and midweek worldbuilding")]
[assembly: AssemblyVersion("0.1.69.0")]
[assembly: AssemblyFileVersion("0.1.69.0")]
[assembly: PluginVersion("0.1.69-prototype")]
[assembly: PluginAuthor("ArtVsTheWorld")]
[assembly: PluginDisplayName("Dynasty Enhancer (Prototype)")]
[assembly: RegisterExecutionAction(typeof(DynastyEnhancer.LaunchAction))]
namespace DynastyEnhancer {
 public sealed class LaunchAction : ExecutionAction {
  public const string NativeFile="DynastyEnhancerNative-v69.dll";
  private static int watching;
  private static Mutex watcherMutex;
  public static string PluginsFolder {get{return Path.GetDirectoryName(typeof(LaunchAction).Assembly.Location);}}
  public static string RuntimeFolder {get{return Path.Combine(PluginsFolder,"DynastyEnhancer","Runtime-v69");}}
  public LaunchAction(){using(var host=Process.GetCurrentProcess())if(String.Equals(host.ProcessName,"MMCModManager",StringComparison.OrdinalIgnoreCase))Start();}
  public override Action<ILogger,PluginManagerType,CancellationToken> PreLaunchAction {get{return (log,type,token)=>Start();}}
  public override Action<ILogger,PluginManagerType,CancellationToken> PostLaunchAction {get{return (log,type,token)=>Start();}}
  public static string PayloadPath(string relative){
   if(String.IsNullOrWhiteSpace(relative)||Path.IsPathRooted(relative)||relative.Contains(":"))throw new IOException("Invalid payload path");
   var root=Path.GetFullPath(RuntimeFolder)+Path.DirectorySeparatorChar;
   var path=Path.GetFullPath(Path.Combine(root,relative.Replace('/',Path.DirectorySeparatorChar)));
   if(!path.StartsWith(root,StringComparison.OrdinalIgnoreCase))throw new IOException("Payload path escapes runtime folder");
   return path;
  }
  public static void Prepare(){
   using(var stream=typeof(LaunchAction).Assembly.GetManifestResourceStream("DynastyEnhancer.payload-sha256.txt")){
    if(stream==null)throw new IOException("Missing payload manifest");
    using(var reader=new StreamReader(stream))for(string line;(line=reader.ReadLine())!=null;){
     if(line.Length==0)continue;var item=line.Split('|');if(item.Length!=2||item[0].Length!=64)throw new IOException("Invalid payload manifest");
     var path=PayloadPath(item[1]);if(!File.Exists(path))throw new IOException("Missing "+item[1]+"; install the complete Dynasty Enhancer package.");
     using(var hash=SHA256.Create())using(var input=File.OpenRead(path))if(BitConverter.ToString(hash.ComputeHash(input)).Replace("-","").ToLowerInvariant()!=item[0])throw new IOException("Payload differs: "+item[1]);
    }
   }
  }
  public static string ConfigurationIssue(){
   try{
    var config=new JavaScriptSerializer().Deserialize<Dictionary<string,object>>(File.ReadAllText(Path.Combine(RuntimeFolder,"dynasty-enhancer.json")));
    foreach(var key in new[]{"node","exporter"}){object value;if(!config.TryGetValue(key,out value)||!(value is string))return "Missing configuration field: "+key;
     var path=(string)value;if(!Path.IsPathRooted(path))path=Path.Combine(RuntimeFolder,path);if(!File.Exists(path))return "Configured "+key+" is unavailable: "+path;}
    return "";
   }catch(Exception error){return "Runtime configuration unavailable: "+error.Message;}
  }
  private static void Note(string message){
   var path=Path.Combine(PluginsFolder,"DynastyEnhancer-launcher.log");
   if(File.Exists(path)&&new FileInfo(path).Length>1024*1024){if(File.Exists(path+".1"))File.Delete(path+".1");File.Move(path,path+".1");}
   File.AppendAllText(path,DateTimeOffset.Now.ToString("O")+" | "+message+Environment.NewLine);
  }
  private static void Start(){
   if(Interlocked.CompareExchange(ref watching,1,0)!=0)return;
   bool first;watcherMutex=new Mutex(false,"Local\\DynastyEnhancer.MMC."+Process.GetCurrentProcess().Id,out first);if(!first)return;
   new Thread(()=>{
    try{
     Prepare();Note("v69 watcher ready; native activation waits for the active Dynasty and UI assets.");
     var loaded=new HashSet<string>();var retryAt=new Dictionary<string,DateTime>();var attempts=new Dictionary<string,int>();string previousIssue=null;
     while(true){
      var issue=ConfigurationIssue();if(issue.Length!=0){if(issue!=previousIssue)Note(issue);previousIssue=issue;Thread.Sleep(1000);continue;}previousIssue=null;
      foreach(var game in Process.GetProcessesByName("CollegeFB27"))using(game)try{
       if(game.HasExited||game.MainWindowHandle==IntPtr.Zero)continue;
       var key=game.Id+":"+game.StartTime.ToUniversalTime().Ticks;DateTime next;int count;attempts.TryGetValue(key,out count);
       if(loaded.Contains(key)||count>=3||retryAt.TryGetValue(key,out next)&&DateTime.UtcNow<next)continue;
       attempts[key]=count+1;retryAt[key]=DateTime.UtcNow.AddSeconds(10);
       var info=new ProcessStartInfo(Path.Combine(RuntimeFolder,"LoadDynastyEnhancer.exe"),game.Id+" \""+Path.Combine(RuntimeFolder,NativeFile)+"\""){
        WorkingDirectory=RuntimeFolder,UseShellExecute=false,CreateNoWindow=true,WindowStyle=ProcessWindowStyle.Hidden,RedirectStandardOutput=true,RedirectStandardError=true};
       using(var loader=Process.Start(info)){
        if(loader==null)throw new IOException("Loader did not start");
        var output=loader.StandardOutput.ReadToEnd();var errors=loader.StandardError.ReadToEnd();loader.WaitForExit();
        if(loader.ExitCode!=0)throw new IOException("Loader exit "+loader.ExitCode+": "+errors+output);
        loaded.Add(key);Note("Native runtime loaded for PID "+game.Id+"; see Runtime-v69/social-media.jsonl for startup_waiting / active / runtime_feed_published.");
       }
      }catch(Exception error){Note("Load attempt failed: "+error.Message);}
      Thread.Sleep(1000);
     }
    }catch(Exception error){try{Note("Watcher stopped: "+error.Message);}catch{}}
    finally{Interlocked.Exchange(ref watching,0);}
   }){IsBackground=true,Name="Dynasty Enhancer launch watcher"}.Start();
  }
 }
}
