param(
 [Parameter(Mandatory=$true)][string]$Tag,
 [string]$Saves='C:/Users/Art/Documents/EA SPORTS College Football 27/saves',
 [string]$History='C:/Apps/CFB 27/MMC/MMC_ModManager_v1.1.0.6/Plugins/DynastyEnhancer/Runtime-v96/RuntimeHistory'
)
$ErrorActionPreference='Stop'
if($Tag -notmatch '^[a-z0-9-]+$'){throw 'Use a plain trial identifier'}
$hubProject=Split-Path -Parent $PSScriptRoot
$hubBackup=Join-Path $hubProject ('Backups/DirectHub-'+$Tag+'-'+(Get-Date -Format 'yyyyMMdd-HHmmss')+'-'+[guid]::NewGuid().ToString('N').Substring(0,8))
if(Test-Path -LiteralPath $hubBackup){throw 'Backup destination already exists'}
New-Item -ItemType Directory -Path $hubBackup | Out-Null
$hubManifest=@()
foreach($hubKind in @('save','history')){
 $hubOrigin=if($hubKind -eq 'save'){$Saves}else{$History}
 $hubFiles=if($hubKind -eq 'save'){@(Get-ChildItem -LiteralPath $hubOrigin -File | Where-Object Name -Match 'ULM')}else{@(Get-ChildItem -LiteralPath $hubOrigin -Recurse -File)}
 if(-not $hubFiles.Count){throw "No $hubKind files found"}
 foreach($hubFile in $hubFiles){
  $hubRelative=if($hubKind -eq 'save'){$hubFile.Name}else{$hubFile.FullName.Substring($hubOrigin.TrimEnd('/','\').Length+1)}
  $hubDestination=Join-Path (Join-Path $hubBackup $hubKind) $hubRelative
  New-Item -ItemType Directory -Path (Split-Path -Parent $hubDestination) -Force | Out-Null
  Copy-Item -LiteralPath $hubFile.FullName -Destination $hubDestination
  $hubSourceHash=(Get-FileHash -LiteralPath $hubFile.FullName -Algorithm SHA256).Hash
  if($hubSourceHash -ne (Get-FileHash -LiteralPath $hubDestination -Algorithm SHA256).Hash){throw "Checksum mismatch for $($hubFile.Name)"}
  $hubManifest+=@{kind=$hubKind;source=$hubFile.FullName;copy=$hubDestination;sha256=$hubSourceHash}
 }
}
$hubManifest | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $hubBackup 'checksums.json') -Encoding utf8NoBOM
[pscustomobject]@{backup=$hubBackup;saves=@($hubManifest|Where-Object kind -eq 'save').Count;historyFiles=@($hubManifest|Where-Object kind -eq 'history').Count}
