param([string]$MmcRoot='C:/Apps/CFB 27/MMC/MMC_ModManager_v1.1.0.6',[string]$HistoryFrom='')
$ErrorActionPreference='Stop'
$installProject=Split-Path -Parent $PSScriptRoot
$installBuild=Join-Path $installProject 'Build'
$installInfo=Get-Content -LiteralPath (Join-Path $installBuild 'mmc-package.json') -Raw | ConvertFrom-Json
$installRoot=[IO.Path]::GetFullPath($MmcRoot)
if(-not (Test-Path -LiteralPath (Join-Path $installRoot 'MMCModManager.exe') -PathType Leaf)){throw 'MMC executable is unavailable at the selected root'}
if(Get-Process MMCModManager -ErrorAction SilentlyContinue){throw 'Close MMC before installing the package'}
$installPlugins=Join-Path $installRoot 'Plugins'
$installRuntime=[IO.Path]::GetFullPath((Join-Path $installPlugins 'DynastyEnhancer/Runtime-v103'))
if(-not $installRuntime.StartsWith($installRoot+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){throw 'Runtime target is outside MMC root'}
foreach($game in Get-Process CollegeFB27 -ErrorAction SilentlyContinue){foreach($module in $game.Modules){if($module.FileName.StartsWith($installRuntime+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){throw 'The target runtime is active in CFB; use a new version folder or close the game before replacing it'}}}
$installBackup=Join-Path $installProject ('Backups/MMC-v103-'+[DateTime]::UtcNow.ToString('yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Path $installBackup,$installRuntime -Force | Out-Null
$installAdapter=Join-Path $installPlugins 'DynastyEnhancer.dll'
if(Test-Path -LiteralPath $installAdapter){Copy-Item -LiteralPath $installAdapter -Destination (Join-Path $installBackup 'DynastyEnhancer.dll')}
$installConfig=Join-Path $installRuntime 'dynasty-enhancer.json'
$installExistingConfig=if(Test-Path -LiteralPath $installConfig){[IO.File]::ReadAllBytes($installConfig)}else{$null}
Get-ChildItem -LiteralPath $installInfo.runtime -Force | ForEach-Object {Copy-Item -LiteralPath $_.FullName -Destination $installRuntime -Recurse -Force}
if($null -ne $installExistingConfig){[IO.File]::WriteAllBytes($installConfig,$installExistingConfig)}
$installHistory=Join-Path $installRuntime 'RuntimeHistory'
if($HistoryFrom -and -not (Test-Path -LiteralPath $installHistory)){
 if(-not (Test-Path -LiteralPath $HistoryFrom -PathType Container)){throw 'Selected history folder is unavailable'}
 Copy-Item -LiteralPath $HistoryFrom -Destination $installHistory -Recurse
 foreach($file in Get-ChildItem -LiteralPath $HistoryFrom -Recurse -File){$relative=$file.FullName.Substring(([IO.Path]::GetFullPath($HistoryFrom).TrimEnd('\','/')).Length+1);if((Get-FileHash -LiteralPath $file.FullName).Hash -ne (Get-FileHash -LiteralPath (Join-Path $installHistory $relative)).Hash){throw 'History copy checksum differs'}}
}
# The adapter is copied last, after its complete runtime is present. History and
# user configuration are deliberately not overwritten on repeated installs.
Copy-Item -LiteralPath (Join-Path $installInfo.stage 'Plugins/DynastyEnhancer.dll') -Destination $installAdapter -Force
& (Join-Path $installBuild 'AdapterSmoke.exe') $installAdapter $installRoot --verify-only
if($LASTEXITCODE -ne 0){if(Test-Path -LiteralPath (Join-Path $installBackup 'DynastyEnhancer.dll')){Copy-Item -LiteralPath (Join-Path $installBackup 'DynastyEnhancer.dll') -Destination $installAdapter -Force};throw 'Installed package validation failed; previous adapter restored'}
@{adapter=$installAdapter;runtime=$installRuntime;backup=$installBackup;historyPreserved=(Test-Path -LiteralPath $installHistory)} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $installBuild 'mmc-installed.json') -Encoding utf8NoBOM
Write-Output "Installed Dynasty Enhancer MMC adapter: $installAdapter"
Write-Output "Preserved previous DLL: $installBackup"
