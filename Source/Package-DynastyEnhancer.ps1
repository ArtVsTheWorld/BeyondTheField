param([ValidatePattern('^$|^DynastyEnhancerNative-[a-zA-Z0-9-]+$')][string]$SocialNativeName='DynastyEnhancerNative-options-p96',[string]$RecruitingName='DynastyEnhancerRecruitFog-p96',[string]$MmcRoot='C:/Apps/CFB 27/MMC/MMC_ModManager_v1.1.0.6',[ValidatePattern('^[a-zA-Z0-9][a-zA-Z0-9._-]*$')][string]$PackageTag='options-p96')
$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'Package-Recruiting.ps1') -SocialNativeName $SocialNativeName -RecruitingName $RecruitingName -MmcRoot $MmcRoot -PackageTag $PackageTag
