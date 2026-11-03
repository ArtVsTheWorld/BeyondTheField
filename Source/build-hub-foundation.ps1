$ErrorActionPreference='Stop'
# Isolated native-only foundation. No MMC adapter, installation or injection.
& (Join-Path $PSScriptRoot 'build.ps1') -NativeName 'DynastyEnhancerHubFoundation-p01'
if($LASTEXITCODE -ne 0){throw 'Foundation native build failed'}
$hubProject=Split-Path -Parent $PSScriptRoot
$hubVs=& 'C:/Program Files (x86)/Microsoft Visual Studio/Installer/vswhere.exe' -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
$hubTool=Get-ChildItem -LiteralPath (Join-Path $hubVs 'VC/Tools/MSVC') -Directory | Sort-Object Name -Descending | Select-Object -First 1
$hubKits='C:/Program Files (x86)/Windows Kits/10'
$hubSdk=Get-ChildItem -LiteralPath (Join-Path $hubKits 'Include') -Directory | Sort-Object Name -Descending | Select-Object -First 1
$hubIncludes=@(('/I'+(Join-Path $hubTool.FullName 'include')),('/I'+(Join-Path $hubSdk.FullName 'ucrt')),('/I'+(Join-Path $hubSdk.FullName 'shared')),('/I'+(Join-Path $hubSdk.FullName 'um')))
$hubLibraries=@(('/LIBPATH:'+(Join-Path $hubTool.FullName 'lib/x64')),('/LIBPATH:'+(Join-Path $hubKits ('Lib/'+$hubSdk.Name+'/ucrt/x64'))),('/LIBPATH:'+(Join-Path $hubKits ('Lib/'+$hubSdk.Name+'/um/x64'))))
Push-Location (Join-Path $hubProject 'Build')
try {
 & (Join-Path $hubTool.FullName 'bin/Hostx64/x64/cl.exe') /nologo /O2 /MT /W4 /WX /EHsc /std:c++17 @hubIncludes (Join-Path $hubProject 'Tests/NativeMapValueTests.cpp') /Fe:NativeMapValueTests.exe /link @hubLibraries
 if($LASTEXITCODE -ne 0){throw 'Native map ABI test compilation failed'}
 & ./NativeMapValueTests.exe
 if($LASTEXITCODE -ne 0){throw 'Native map ABI checks failed'}
} finally {Pop-Location}
