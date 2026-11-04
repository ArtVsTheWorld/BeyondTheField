param([string]$Name='DynastyEnhancerRecruitListProbe-p2',[ValidateSet('RecruitListProbe','RosterViewProbe','PlayerUiTrace','PlayerUiPreview')][string]$Source='RecruitListProbe')
$ErrorActionPreference='Stop'
if(Test-Path -LiteralPath ('Build/'+$Name+'.dll')){throw 'Choose a fresh probe name'}
$listProbeVs=& 'C:/Program Files (x86)/Microsoft Visual Studio/Installer/vswhere.exe' -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
if(-not $listProbeVs){throw 'MSVC x64 tools are required'}
$listProbeTool=Get-ChildItem -LiteralPath (Join-Path $listProbeVs 'VC/Tools/MSVC') -Directory | Sort-Object Name -Descending | Select-Object -First 1
$listProbeKits='C:/Program Files (x86)/Windows Kits/10'
$listProbeSdk=Get-ChildItem -LiteralPath (Join-Path $listProbeKits 'Include') -Directory | Sort-Object Name -Descending | Select-Object -First 1
$listProbeFlags=@('/nologo','/O2','/MT','/W4','/WX','/EHsc','/std:c++17','/utf-8',('/I'+(Join-Path $listProbeTool.FullName 'include')),('/I'+(Join-Path $listProbeSdk.FullName 'ucrt')),('/I'+(Join-Path $listProbeSdk.FullName 'shared')),('/I'+(Join-Path $listProbeSdk.FullName 'um')))
$listProbeLib=@(('/LIBPATH:'+(Join-Path $listProbeTool.FullName 'lib/x64')),('/LIBPATH:'+(Join-Path $listProbeKits ('Lib/'+$listProbeSdk.Name+'/ucrt/x64'))),('/LIBPATH:'+(Join-Path $listProbeKits ('Lib/'+$listProbeSdk.Name+'/um/x64'))))

& (Join-Path $listProbeTool.FullName 'bin/Hostx64/x64/cl.exe') @listProbeFlags /LD (Join-Path $PSScriptRoot ($Source+'.cpp')) ('/Fe:Build/'+$Name+'.dll') ('/Fo:Build/'+$Name+'.obj') /link @listProbeLib /INCREMENTAL:NO
if($LASTEXITCODE -ne 0){throw 'List probe build failed'}
