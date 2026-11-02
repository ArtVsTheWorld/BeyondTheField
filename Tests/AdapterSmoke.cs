using System;using System.IO;using System.Reflection;
class AdapterSmoke {
 static void Require(bool ok,string why){if(!ok)throw new Exception(why);}
 static int Main(string[] args){
  var sdk=args[1];AppDomain.CurrentDomain.AssemblyResolve+=(s,e)=>{var path=Path.Combine(sdk,new AssemblyName(e.Name).Name+".dll");return File.Exists(path)?Assembly.LoadFrom(path):null;};
  var a=Assembly.LoadFrom(args[0]);var type=a.GetType("DynastyEnhancer.LaunchAction",true);var prepare=type.GetMethod("Prepare");
  prepare.Invoke(null,null);Require((string)type.GetMethod("ConfigurationIssue").Invoke(null,null)=="","Package configuration unavailable");
  bool registered=false;foreach(var attr in a.GetCustomAttributesData())if(attr.AttributeType.Name=="RegisterExecutionActionAttribute"||attr.AttributeType.Name=="RegisterExecutionAction")registered=true;
  Require(registered,"Missing MMC execution action registration");
  var action=Activator.CreateInstance(type);Require(type.GetProperty("PreLaunchAction").GetValue(action,null)!=null&&type.GetProperty("PostLaunchAction").GetValue(action,null)!=null,"Missing launch callbacks");
  if(args.Length>2&&args[2]=="--verify-only"){Console.WriteLine("Installed MMC adapter, protected payload, configuration and launch callbacks validated; no game injection.");return 0;}
  var folder=(string)type.GetProperty("RuntimeFolder").GetValue(null,null);
  foreach(var relative in new[]{"LoadDynastyEnhancer.exe","Content/Runtime/analysis-pack.json"}){
   var path=Path.Combine(folder,relative);var original=File.ReadAllBytes(path);bool rejected=false;
   try{File.WriteAllText(path,"tampered smoke fixture");try{prepare.Invoke(null,null);}catch(TargetInvocationException error){rejected=error.InnerException is IOException;}}
   finally{File.WriteAllBytes(path,original);}Require(rejected,"Tampered runtime/content accepted");
  }
  var config=Path.Combine(folder,"dynasty-enhancer.json");var before=File.ReadAllText(config);
  try{File.AppendAllText(config,"\n ");prepare.Invoke(null,null);Require(File.ReadAllText(config)==before+"\n ","User configuration was overwritten");}finally{File.WriteAllText(config,before);}
  bool escape=false;try{type.GetMethod("PayloadPath").Invoke(null,new object[]{"../outside.dll"});}catch(TargetInvocationException error){escape=error.InnerException is IOException;}Require(escape,"Payload path escaped package root");
  prepare.Invoke(null,null);Console.WriteLine("MMC registration, launch callbacks, native/content tamper rejection, path bounds and editable configuration passed; no game injection.");return 0;
 }
}
