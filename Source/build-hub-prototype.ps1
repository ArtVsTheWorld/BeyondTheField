param([string]$NativeName='DynastyEnhancerHubPrototype-p02')
$ErrorActionPreference='Stop'
if($NativeName -notmatch '^DynastyEnhancerHubPrototype-p[0-9]+$'){throw 'Use an isolated prototype module name'}
& (Join-Path $PSScriptRoot 'build.ps1') -NativeName $NativeName -HubFeed
if($LASTEXITCODE -ne 0){throw 'Hub prototype build failed'}
& (Join-Path $PSScriptRoot 'build-hub-foundation.ps1') -TestsOnly
if($LASTEXITCODE -ne 0){throw 'Hub prototype ABI/model tests failed'}
Write-Output 'Native prototype compiled and checked. No installation or injection performed.'
