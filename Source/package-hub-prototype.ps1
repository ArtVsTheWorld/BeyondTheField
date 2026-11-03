param([string]$NativeName='DynastyEnhancerHubPrototype-p02',[string]$BaselineRuntime='C:/Apps/CFB 27/MMC/MMC_ModManager_v1.1.0.6/Plugins/DynastyEnhancer/Runtime-v96')
$ErrorActionPreference='Stop'
if($NativeName -notmatch '^DynastyEnhancerHubPrototype-p[0-9]+$'){throw 'Experimental module name required'}
$hubProject=Split-Path -Parent $PSScriptRoot
$hubBuild=Join-Path $hubProject 'Build'
$hubStage=Join-Path $hubBuild ('DirectHub-'+$NativeName+'-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $hubStage,(Join-Path $hubStage 'Tools'),(Join-Path $hubStage 'Content/Runtime') -Force | Out-Null
Copy-Item -LiteralPath (Join-Path $hubBuild ($NativeName+'.dll')),(Join-Path $hubBuild 'LoadDynastyEnhancer.exe') -Destination $hubStage
Get-ChildItem -LiteralPath (Join-Path $hubProject 'Tools') -File -Filter '*.mjs' | Copy-Item -Destination (Join-Path $hubStage 'Tools')
Get-ChildItem -LiteralPath (Join-Path $hubProject 'Content/Runtime') -File -Filter '*.json' | Copy-Item -Destination (Join-Path $hubStage 'Content/Runtime')
Copy-Item -LiteralPath (Join-Path $BaselineRuntime 'dynasty-enhancer.json') -Destination $hubStage
Copy-Item -LiteralPath (Join-Path $hubProject 'THIRD_PARTY_NOTICES.md') -Destination $hubStage
Copy-Item -LiteralPath (Join-Path $hubProject 'LICENSES') -Destination (Join-Path $hubStage 'LICENSES') -Recurse
Copy-Item -LiteralPath (Join-Path $hubProject 'Vendor/json.LICENSE.txt') -Destination (Join-Path $hubStage 'LICENSES/nlohmann-json-MIT.txt')
$hubPayload=Get-ChildItem -LiteralPath $hubStage -Recurse -File | ForEach-Object {@{file=$_.FullName.Substring($hubStage.Length+1);sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash}}
@{experimental=$true;native=$NativeName;directHub=$true;installedMmcModified=$false;privateHistoryIncludedInZip=$false;files=@($hubPayload)} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $hubStage 'prototype-manifest.json') -Encoding utf8NoBOM
$hubZip=Join-Path $hubBuild ($NativeName+'.zip')
# Package code before copying any private history or runtime captures.
Compress-Archive -Path (Join-Path $hubStage '*') -DestinationPath $hubZip -Force
$hubHistory=Join-Path $BaselineRuntime 'RuntimeHistory'
Copy-Item -LiteralPath $hubHistory -Destination (Join-Path $hubStage 'RuntimeHistory') -Recurse
$hubHistoryFiles=0
foreach($hubFile in Get-ChildItem -LiteralPath $hubHistory -Recurse -File){
 $hubRelative=$hubFile.FullName.Substring($hubHistory.Length+1)
 if((Get-FileHash -LiteralPath $hubFile.FullName).Hash -ne (Get-FileHash -LiteralPath (Join-Path (Join-Path $hubStage 'RuntimeHistory') $hubRelative)).Hash){throw 'History copy changed during staging; no experimental load performed'}
 $hubHistoryFiles++
}
@{runtime=$hubStage;zip=$hubZip;native=(Join-Path $hubStage ($NativeName+'.dll'));baselineRuntime=$BaselineRuntime;historyFiles=$hubHistoryFiles;installedMmcModified=$false} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $hubBuild 'hub-prototype-package.json') -Encoding utf8NoBOM
Write-Output "Experimental runtime: $hubStage"
Write-Output "Code-only ZIP: $hubZip"
Write-Output "Verified private history copies: $hubHistoryFiles. No installation or injection performed."
