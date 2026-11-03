param([string]$NativeName='DynastyEnhancerNative-v88',[switch]$Preflight,[switch]$ScrollTest,[switch]$ExperimentalFocus,[switch]$ListFeed,[switch]$ReadOnlyFeed=$true,[switch]$DualDropdown=$true)
$ErrorActionPreference='Stop'
$analyticsRoot=Split-Path -Parent $PSScriptRoot
$analyticsOut=Join-Path $analyticsRoot 'Build'
New-Item -ItemType Directory -Path $analyticsOut -Force | Out-Null
$analyticsVs=& 'C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe' -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
if(-not $analyticsVs){throw 'MSVC x64 tools required'}
$analyticsTool=Get-ChildItem -LiteralPath (Join-Path $analyticsVs 'VC\Tools\MSVC') -Directory | Sort-Object Name -Descending | Select-Object -First 1
$analyticsKits='C:\Program Files (x86)\Windows Kits\10'
$analyticsSdk=Get-ChildItem -LiteralPath (Join-Path $analyticsKits 'Include') -Directory | Sort-Object Name -Descending | Select-Object -First 1
$analyticsCl=Join-Path $analyticsTool.FullName 'bin\Hostx64\x64\cl.exe'
$analyticsInclude=@(('/I'+(Join-Path $analyticsTool.FullName 'include')),('/I'+(Join-Path $analyticsSdk.FullName 'ucrt')),('/I'+(Join-Path $analyticsSdk.FullName 'shared')),('/I'+(Join-Path $analyticsSdk.FullName 'um')))
$analyticsLib=@(('/LIBPATH:'+(Join-Path $analyticsTool.FullName 'lib\x64')),('/LIBPATH:'+(Join-Path $analyticsKits ('Lib\'+$analyticsSdk.Name+'\ucrt\x64'))),('/LIBPATH:'+(Join-Path $analyticsKits ('Lib\'+$analyticsSdk.Name+'\um\x64'))))
$analyticsCommon=@('/nologo','/O2','/MT','/W4','/WX','/EHsc','/std:c++17','/utf-8')+$analyticsInclude
$analyticsCommon+=('/I'+(Join-Path $analyticsSdk.FullName 'winrt'))
Push-Location $analyticsOut
try {
    $socialDefines=@();if($ScrollTest){$socialDefines+='/DSOCIAL_SCROLL_TEST'};if($Preflight){$socialDefines+='/DSOCIAL_PREFLIGHT_ONLY'};if($ExperimentalFocus){$socialDefines+='/DSOCIAL_EXPERIMENTAL_FOCUS'};if($ListFeed){$socialDefines+='/DSOCIAL_LIST_FEED'};if($ReadOnlyFeed){$socialDefines+='/DSOCIAL_READ_ONLY_FEED'};if($DualDropdown){$socialDefines+='/DSOCIAL_DUAL_DROPDOWN'}
    & $analyticsCl @analyticsCommon @socialDefines /LD (Join-Path $PSScriptRoot 'NativeSocialMedia.cpp') ('/Fe:'+$NativeName+'.dll') /link @analyticsLib /INCREMENTAL:NO
    if($LASTEXITCODE -ne 0){throw 'Native Social Media build failed'}
    & $analyticsCl @analyticsCommon @socialDefines (Join-Path $analyticsRoot 'Tests/NativeSocialMediaTests.cpp') /Fe:NativeSocialMediaTests.exe /link @analyticsLib /INCREMENTAL:NO
    if($LASTEXITCODE -ne 0){throw 'Native Social Media tests build failed'}
    & (Join-Path $analyticsOut 'NativeSocialMediaTests.exe')
    if($LASTEXITCODE -ne 0){throw 'Native Social Media checks failed'}
    & $analyticsCl @analyticsCommon (Join-Path $PSScriptRoot 'LiveCapture.cpp') /Fe:LiveCapture.exe /link @analyticsLib /INCREMENTAL:NO
    if($LASTEXITCODE -ne 0){throw 'Live reader build failed'}
    & $analyticsCl @analyticsCommon (Join-Path $PSScriptRoot 'LoadRuntime.cpp') /Fe:LoadDynastyEnhancer.exe /link @analyticsLib /INCREMENTAL:NO
    if($LASTEXITCODE -ne 0){throw 'Loader build failed'}
} finally {Pop-Location}
