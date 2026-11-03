param([string]$NativeName='DynastyEnhancerNative-v93',[string]$MmcRoot='C:/Apps/CFB 27/MMC/MMC_ModManager_v1.1.0.6',[string]$Node='C:/Program Files/nodejs/node.exe')
$ErrorActionPreference='Stop'
$packageRoot=Split-Path -Parent $PSScriptRoot
$packageBuild=Join-Path $packageRoot 'Build'
$packageStage=Join-Path $packageBuild ('Package-v93-'+[guid]::NewGuid().ToString('N'))
$packagePlugins=Join-Path $packageStage 'Plugins'
$packageRuntime=Join-Path $packagePlugins 'DynastyEnhancer/Runtime-v93'
if(-not (Test-Path -LiteralPath $Node -PathType Leaf)){throw 'Node.js executable is unavailable'}
New-Item -ItemType Directory -Path $packageRuntime,(Join-Path $packageRuntime 'Tools'),(Join-Path $packageRuntime 'Content/Runtime') -Force | Out-Null
Copy-Item -LiteralPath (Join-Path $packageBuild ($NativeName+'.dll')) -Destination (Join-Path $packageRuntime 'DynastyEnhancerNative-v93.dll')
Copy-Item -LiteralPath (Join-Path $packageBuild 'LoadDynastyEnhancer.exe') -Destination $packageRuntime
Get-ChildItem -LiteralPath (Join-Path $packageRoot 'Tools') -Filter '*.mjs' -File | Copy-Item -Destination (Join-Path $packageRuntime 'Tools')
Get-ChildItem -LiteralPath (Join-Path $packageRoot 'Content/Runtime') -Filter '*.json' -File | Copy-Item -Destination (Join-Path $packageRuntime 'Content/Runtime')
@{node=$Node;exporter='Tools/export_runtime.mjs'} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $packageRuntime 'dynasty-enhancer.json') -Encoding utf8NoBOM
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'PackageREADME.md') -Destination (Join-Path $packageStage 'README.md')
Copy-Item -LiteralPath (Join-Path $packageRoot 'THIRD_PARTY_NOTICES.md') -Destination $packageStage
New-Item -ItemType Directory -Path (Join-Path $packageStage 'LICENSES') -Force | Out-Null
Copy-Item -LiteralPath (Join-Path $packageRoot 'LICENSES/Aces-CFB-Toolkit-MIT.txt') -Destination (Join-Path $packageStage 'LICENSES')
Copy-Item -LiteralPath (Join-Path $packageRoot 'Vendor/json.LICENSE.txt') -Destination (Join-Path $packageStage 'LICENSES/nlohmann-json-MIT.txt')
$packageManifest=Join-Path $packageBuild 'mmc-payload-sha256.txt'
$packageHashes=Get-ChildItem -LiteralPath $packageRuntime -Recurse -File | Where-Object {$_.Name -ne 'dynasty-enhancer.json'} | Sort-Object FullName | ForEach-Object {
 (Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName).Hash.ToLowerInvariant()+'|'+$_.FullName.Substring($packageRuntime.Length+1).Replace('\','/')
}
[IO.File]::WriteAllLines($packageManifest,$packageHashes,[Text.UTF8Encoding]::new($false))
$packageCsc=Join-Path $env:WINDIR 'Microsoft.NET/Framework64/v4.0.30319/csc.exe'
& $packageCsc /nologo /target:library /platform:x64 /optimize+ ('/out:'+(Join-Path $packagePlugins 'DynastyEnhancer.dll')) ('/reference:'+(Join-Path $MmcRoot 'FrostyCore.dll')) ('/reference:'+(Join-Path $MmcRoot 'FrostySdk.dll')) /reference:System.Web.Extensions.dll ('/resource:'+$packageManifest+',DynastyEnhancer.payload-sha256.txt') (Join-Path $PSScriptRoot 'MmcPlugin.cs')
if($LASTEXITCODE -ne 0){throw 'MMC adapter compilation failed'}
Copy-Item -LiteralPath (Join-Path $packagePlugins 'DynastyEnhancer.dll') -Destination (Join-Path $packageBuild 'DynastyEnhancer.dll') -Force
& $packageCsc /nologo /target:exe /platform:x64 /optimize+ ('/out:'+(Join-Path $packageBuild 'AdapterSmoke.exe')) (Join-Path $packageRoot 'Tests/AdapterSmoke.cs')
if($LASTEXITCODE -ne 0){throw 'MMC adapter smoke-test compilation failed'}
$packageZip=Join-Path $packageBuild 'DynastyEnhancer-v93-MMC.zip'
Compress-Archive -Path (Join-Path $packageStage '*') -DestinationPath $packageZip -Force
@{stage=$packageStage;zip=$packageZip;runtime=$packageRuntime} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $packageBuild 'mmc-package.json') -Encoding utf8NoBOM
Write-Output "Staged package: $packageStage"
Write-Output "ZIP: $packageZip"
Write-Output 'No installed MMC files were changed.'
