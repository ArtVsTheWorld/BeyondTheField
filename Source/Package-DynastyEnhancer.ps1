param([string]$RecruitingName='DynastyEnhancerRecruitFog-p28',[string]$MmcRoot='C:/Apps/CFB 27/MMC/MMC_ModManager_v1.1.0.6',[ValidatePattern('^[a-zA-Z0-9][a-zA-Z0-9._-]*$')][string]$PackageTag='v105')
$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'Package-Recruiting.ps1') -RecruitingName $RecruitingName -MmcRoot $MmcRoot -PackageTag $PackageTag
