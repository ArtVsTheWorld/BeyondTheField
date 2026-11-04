param([Parameter(Mandatory=$true)][ValidatePattern('^DynastyEnhancerRecruitFog-p[0-9]+$')][string]$Name,[switch]$RecruitNotesProbe,[switch]$RecruitNotesUi,[switch]$PlayerFogPreview,[switch]$PlayerFogColors)
$ErrorActionPreference='Stop'
$fogRoot=Split-Path -Parent $PSScriptRoot
$fogOut=Join-Path $fogRoot 'Build'
New-Item -ItemType Directory -Path $fogOut -Force | Out-Null
if(Test-Path -LiteralPath (Join-Path $fogOut ($Name+'.dll'))){throw 'Choose a fresh pNN name. Existing prototype DLLs may be pinned in the game and must not be overwritten.'}
$fogVs=& 'C:/Program Files (x86)/Microsoft Visual Studio/Installer/vswhere.exe' -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
if(-not $fogVs){throw 'MSVC x64 tools are required'}
$fogTool=Get-ChildItem -LiteralPath (Join-Path $fogVs 'VC/Tools/MSVC') -Directory | Sort-Object Name -Descending | Select-Object -First 1
$fogKits='C:/Program Files (x86)/Windows Kits/10'
$fogSdk=Get-ChildItem -LiteralPath (Join-Path $fogKits 'Include') -Directory | Sort-Object Name -Descending | Select-Object -First 1
$fogCl=Join-Path $fogTool.FullName 'bin/Hostx64/x64/cl.exe'
$fogInc=@(('/I'+(Join-Path $fogTool.FullName 'include')),('/I'+(Join-Path $fogSdk.FullName 'ucrt')),('/I'+(Join-Path $fogSdk.FullName 'shared')),('/I'+(Join-Path $fogSdk.FullName 'um')))
$fogLib=@(('/LIBPATH:'+(Join-Path $fogTool.FullName 'lib/x64')),('/LIBPATH:'+(Join-Path $fogKits ('Lib/'+$fogSdk.Name+'/ucrt/x64'))),('/LIBPATH:'+(Join-Path $fogKits ('Lib/'+$fogSdk.Name+'/um/x64'))))
$fogFlags=@('/nologo','/O2','/MT','/W4','/WX','/EHsc','/std:c++17','/utf-8')+$fogInc
if($RecruitNotesProbe -and $RecruitNotesUi){throw 'Choose either the pass-through probe or Notes UI candidate'}
if($RecruitNotesProbe){$fogFlags+='/DRECRUIT_NOTES_PROBE'}
if($RecruitNotesUi){$fogFlags+='/DRECRUIT_NOTES_UI'}
if($PlayerFogPreview){if(-not $RecruitNotesUi){throw 'Preview requires the shared UI implementation'};$fogFlags+='/DPLAYER_FOG_PREVIEW'}
if($PlayerFogColors){if(-not $RecruitNotesUi){throw 'Player colors require UI support'};$fogFlags+='/DPLAYER_FOG_COLORS'}
if($RecruitNotesUi){
 & python (Join-Path $fogRoot 'Tools/build_lower_division_schools.py')
 if($LASTEXITCODE -ne 0){throw 'College school catalog validation failed'}
 & python (Join-Path $fogRoot 'Tools/build_recruit_notes_prose.py')
 if($LASTEXITCODE -ne 0){throw 'Notes prose validation failed'}
 & python (Join-Path $fogRoot 'Tests/recruit_notes_ui_test.py')
 if($LASTEXITCODE -ne 0){throw 'Notes UI bytecode checks failed'}
 & python (Join-Path $fogRoot 'Tests/player_fog_ui_test.py')
 if($LASTEXITCODE -ne 0){throw 'Player UI bytecode checks failed'}
}
Push-Location $fogOut
try{
 & $fogCl @fogFlags (Join-Path $fogRoot 'Tests/RecruitingFogTests.cpp') /Fe:RecruitingFogTests.exe /link @fogLib /INCREMENTAL:NO
 if($LASTEXITCODE -ne 0){throw 'Recruiting Fog test build failed'}
 & .\RecruitingFogTests.exe
 if($LASTEXITCODE -ne 0){throw 'Recruiting Fog checks failed'}
 & $fogCl @fogFlags /LD (Join-Path $PSScriptRoot 'RecruitingFog.cpp') ('/Fe:'+$Name+'.dll') /link @fogLib /INCREMENTAL:NO
 if($LASTEXITCODE -ne 0){throw 'Recruiting Fog runtime build failed'}
 & $fogCl @fogFlags (Join-Path $PSScriptRoot 'LoadRuntime.cpp') /Fe:LoadDynastyEnhancer.exe /link @fogLib /INCREMENTAL:NO
 if($LASTEXITCODE -ne 0){throw 'Recruiting Fog loader build failed'}
}finally{Pop-Location}
