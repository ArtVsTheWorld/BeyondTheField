param()
$ErrorActionPreference='Stop'
$resumeRoot=Split-Path -Parent $PSScriptRoot
$resumeOut=Join-Path $resumeRoot 'Build'
$resumeVs=& 'C:/Program Files (x86)/Microsoft Visual Studio/Installer/vswhere.exe' -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
if(-not $resumeVs){throw 'MSVC x64 tools are required'}
$resumeTool=Get-ChildItem -LiteralPath (Join-Path $resumeVs 'VC/Tools/MSVC') -Directory | Sort-Object Name -Descending | Select-Object -First 1
$resumeKits='C:/Program Files (x86)/Windows Kits/10'
$resumeSdk=Get-ChildItem -LiteralPath (Join-Path $resumeKits 'Include') -Directory | Sort-Object Name -Descending | Select-Object -First 1
$resumeFlags=@('/nologo','/O2','/MT','/W4','/WX','/EHsc','/std:c++17','/utf-8',('/I'+(Join-Path $resumeTool.FullName 'include')),('/I'+(Join-Path $resumeSdk.FullName 'ucrt')),('/I'+(Join-Path $resumeSdk.FullName 'shared')),('/I'+(Join-Path $resumeSdk.FullName 'um')))
$resumeLib=@(('/LIBPATH:'+(Join-Path $resumeTool.FullName 'lib/x64')),('/LIBPATH:'+(Join-Path $resumeKits ('Lib/'+$resumeSdk.Name+'/ucrt/x64'))),('/LIBPATH:'+(Join-Path $resumeKits ('Lib/'+$resumeSdk.Name+'/um/x64'))))
New-Item -ItemType Directory -Path $resumeOut -Force | Out-Null
& python (Join-Path $resumeRoot 'Tools/build_lower_division_schools.py')
if($LASTEXITCODE -ne 0){throw 'College school catalog validation failed'}
& python (Join-Path $resumeRoot 'Tools/build_recruit_notes_prose.py')
if($LASTEXITCODE -ne 0){throw 'Notes prose validation failed'}
Push-Location $resumeOut
try{
 foreach($resumeSource in @('RecruitResumeAudit','RecruitResumeMinimal','RecruitResumeTools')){
  & (Join-Path $resumeTool.FullName 'bin/Hostx64/x64/cl.exe') @resumeFlags (Join-Path $PSScriptRoot ($resumeSource+'.cpp')) ('/Fe:'+$resumeSource+'.exe') /link @resumeLib /INCREMENTAL:NO
  if($LASTEXITCODE -ne 0){throw ($resumeSource+' build failed')}
 }
 & .\RecruitResumeTools.exe --self-test
 if($LASTEXITCODE -ne 0){throw 'Resume generator checks failed'}
}finally{Pop-Location}
