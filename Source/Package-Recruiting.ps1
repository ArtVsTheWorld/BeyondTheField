param([ValidatePattern('^$|^DynastyEnhancerNative-[a-zA-Z0-9-]+$')][string]$SocialNativeName='DynastyEnhancerNative-options-p96',[string]$RecruitingName='DynastyEnhancerRecruitFog-p96',[string]$MmcRoot='C:/Apps/CFB 27/MMC/MMC_ModManager_v1.1.0.6',[ValidatePattern('^[a-zA-Z0-9][a-zA-Z0-9._-]*$')][string]$PackageTag='options-p96')
$ErrorActionPreference='Stop'
$recruitProject=Split-Path -Parent $PSScriptRoot
$recruitBuild=Join-Path $recruitProject 'Build'
$recruitBase=Join-Path $MmcRoot 'Plugins/DynastyEnhancer/Runtime-v103'
$recruitStage=Join-Path $recruitBuild ('Package-DynastyEnhancer-'+$PackageTag+'-'+[Guid]::NewGuid().ToString('N'))
$recruitPlugins=Join-Path $recruitStage 'Plugins'
$recruitRuntime=Join-Path $recruitPlugins 'DynastyEnhancer/Runtime-v103'
New-Item -ItemType Directory -Path $recruitRuntime,(Join-Path $recruitRuntime 'Tools'),(Join-Path $recruitRuntime 'Content/Runtime') -Force | Out-Null
# Preserve the user's working Social Media payload, including content updates
# made since the research branch was forked. No feeds/history enter the ZIP.
foreach($recruitFile in @('DynastyEnhancerNative-v103.dll','LoadDynastyEnhancer.exe','dynasty-enhancer.json')){
 Copy-Item -LiteralPath (Join-Path $recruitBase $recruitFile) -Destination $recruitRuntime
}
if($SocialNativeName){Copy-Item -LiteralPath (Join-Path $recruitBuild ($SocialNativeName+'.dll')) -Destination (Join-Path $recruitRuntime 'DynastyEnhancerNative-v103.dll')}
Get-ChildItem -LiteralPath (Join-Path $recruitBase 'Tools') -File -Filter '*.mjs' | Where-Object Name -NE 'export_draft_results.mjs' | Copy-Item -Destination (Join-Path $recruitRuntime 'Tools')
Get-ChildItem -LiteralPath (Join-Path $recruitBase 'Content/Runtime') -File -Filter '*.json' | Copy-Item -Destination (Join-Path $recruitRuntime 'Content/Runtime')
Copy-Item -LiteralPath (Join-Path $recruitBuild ($RecruitingName+'.dll')) -Destination (Join-Path $recruitRuntime 'DynastyEnhancerRecruitFog-v1.dll')
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'RecruitingPackageREADME.txt') -Destination (Join-Path $recruitStage 'README.txt')
New-Item -ItemType Directory -Path (Join-Path $recruitStage 'LICENSES') | Out-Null
Copy-Item -LiteralPath (Join-Path $recruitProject 'Vendor/json.LICENSE.txt') -Destination (Join-Path $recruitStage 'LICENSES/nlohmann-json-MIT.txt')
Copy-Item -LiteralPath (Join-Path $recruitProject 'THIRD_PARTY_NOTICES.md') -Destination $recruitStage
Copy-Item -LiteralPath (Join-Path $recruitProject 'LICENSES/Aces-CFB-Toolkit-MIT.txt') -Destination (Join-Path $recruitStage 'LICENSES')
$recruitManifest=Join-Path $recruitBuild ('mmc-recruiting-payload-'+$PackageTag+'-sha256.txt')
$recruitHashes=Get-ChildItem -LiteralPath $recruitRuntime -Recurse -File | Where-Object {$_.Name -ne 'dynasty-enhancer.json'} | Sort-Object FullName | ForEach-Object {(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()+'|'+$_.FullName.Substring($recruitRuntime.Length+1).Replace('\','/')}
[IO.File]::WriteAllLines($recruitManifest,$recruitHashes,[Text.UTF8Encoding]::new($false))
$recruitCsc=Join-Path $env:WINDIR 'Microsoft.NET/Framework64/v4.0.30319/csc.exe'
& $recruitCsc /nologo /target:library /platform:x64 /optimize+ ('/out:'+(Join-Path $recruitPlugins 'DynastyEnhancer.dll')) ('/reference:'+(Join-Path $MmcRoot 'FrostyCore.dll')) ('/reference:'+(Join-Path $MmcRoot 'FrostySdk.dll')) /reference:System.Web.Extensions.dll ('/resource:'+$recruitManifest+',DynastyEnhancer.payload-sha256.txt') (Join-Path $PSScriptRoot 'MmcRecruitingPlugin.cs')
if($LASTEXITCODE -ne 0){throw 'Recruiting MMC adapter build failed'}
& $recruitCsc /nologo /target:exe /platform:x64 /optimize+ ('/out:'+(Join-Path $recruitBuild 'AdapterSmoke.exe')) (Join-Path $recruitProject 'Tests/AdapterSmoke.cs')
if($LASTEXITCODE -ne 0){throw 'Adapter smoke-test build failed'}
& (Join-Path $recruitBuild 'AdapterSmoke.exe') (Join-Path $recruitPlugins 'DynastyEnhancer.dll') $MmcRoot
if($LASTEXITCODE -ne 0){throw 'Recruiting MMC package checks failed'}
$recruitZip=Join-Path $recruitBuild ('DynastyEnhancer-'+$PackageTag+'-MMC.zip')
Compress-Archive -Path (Join-Path $recruitStage '*') -DestinationPath $recruitZip -Force
$recruitMetadata=if($PackageTag -eq 'v105'){'mmc-package.json'}else{'mmc-package-'+$PackageTag+'.json'}
@{stage=$recruitStage;runtime=$recruitRuntime;zip=$recruitZip;recruitingSource=$RecruitingName;kind=('dynasty-enhancer-'+$PackageTag)} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $recruitBuild $recruitMetadata) -Encoding utf8NoBOM
Write-Output ('Staged and verified: '+$recruitZip)
Write-Output 'Installed MMC files and history remain unchanged.'
