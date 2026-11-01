param([int]$ExpectedWeek=7)
$ErrorActionPreference='Stop'
$socialRoot=Split-Path -Parent $PSScriptRoot
$socialConfig=Get-Content -LiteralPath (Join-Path $socialRoot 'Build/social-refresh.json') -Raw | ConvertFrom-Json
$socialFeed=Get-Content -LiteralPath (Join-Path $socialRoot 'Build/social-feed.json') -Raw | ConvertFrom-Json
if($socialFeed.week -ne $ExpectedWeek -or $socialFeed.leagueId -ne $socialConfig.leagueId -or $socialFeed.userTeamIndex -ne $socialConfig.userTeamIndex){throw 'Feed does not match the expected pre-rollover Dynasty/week'}
$socialSave=Get-Item -LiteralPath $socialConfig.save
$socialBefore=(Get-FileHash -LiteralPath $socialSave.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
if($socialBefore -ne $socialFeed.sha256){throw 'Autosave changed since the verified feed. Refresh the feed before taking this test backup.'}
$socialNow=[System.TimeZoneInfo]::ConvertTimeBySystemTimeZoneId([DateTimeOffset]::UtcNow,'Eastern Standard Time')
$socialBackup=Join-Path $socialRoot ('Backups/'+$socialNow.ToString('yyyyMMdd-HHmmss')+'-Dynasty-Week'+$ExpectedWeek+'-'+[Guid]::NewGuid().ToString('N').Substring(0,6))
New-Item -ItemType Directory -Path $socialBackup | Out-Null
$socialItems=@()
$socialCandidates=@($socialSave.FullName)
if($socialSave.Name.EndsWith('-AUTOSAVE')){
    $socialManual=Join-Path $socialSave.DirectoryName $socialSave.Name.Substring(0,$socialSave.Name.Length-9)
    if(Test-Path -LiteralPath $socialManual -PathType Leaf){$socialCandidates+=$socialManual}
}
$socialCandidates+=@(Join-Path $socialRoot 'Build/social-feed.json';Join-Path $socialRoot 'Build/social-refresh.json')
foreach($socialSource in $socialCandidates){
    $socialItem=Get-Item -LiteralPath $socialSource
    $socialHash=(Get-FileHash -LiteralPath $socialItem.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    $socialTarget=Join-Path $socialBackup $socialItem.Name
    Copy-Item -LiteralPath $socialItem.FullName -Destination $socialTarget
    $socialCopied=(Get-FileHash -LiteralPath $socialTarget -Algorithm SHA256).Hash.ToLowerInvariant()
    $socialAfter=(Get-FileHash -LiteralPath $socialItem.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    if($socialHash -ne $socialCopied -or $socialHash -ne $socialAfter){throw ('Backup verification failed or source changed: '+$socialItem.FullName)}
    $socialItems+=@{source=$socialItem.FullName;backup=$socialTarget;sha256=$socialCopied;bytes=$socialItem.Length}
}
$socialHistory=Join-Path $socialRoot ('Build/History/'+$socialFeed.leagueId+'/'+$socialFeed.season+'/'+$socialFeed.phase+'/'+$ExpectedWeek+'.snapshot.json')
if(Test-Path -LiteralPath $socialHistory -PathType Leaf){
    $socialHistoryTarget=Join-Path $socialBackup 'weekly-snapshot.json'
    Copy-Item -LiteralPath $socialHistory -Destination $socialHistoryTarget
    $socialHistoryHash=(Get-FileHash -LiteralPath $socialHistory -Algorithm SHA256).Hash
    if($socialHistoryHash -ne (Get-FileHash -LiteralPath $socialHistoryTarget -Algorithm SHA256).Hash){throw 'Weekly snapshot copy failed verification'}
    $socialItems+=@{source=$socialHistory;backup=$socialHistoryTarget;sha256=$socialHistoryHash.ToLowerInvariant();bytes=(Get-Item -LiteralPath $socialHistoryTarget).Length}
}
if((Get-FileHash -LiteralPath $socialSave.FullName -Algorithm SHA256).Hash.ToLowerInvariant() -ne $socialBefore){throw 'Autosave changed during the backup; do not use this backup for the test'}
$socialManifest=@{format=1;created=$socialNow.ToString('o');timezone='America/New_York';leagueId=$socialFeed.leagueId;teamIndex=$socialFeed.userTeamIndex;season=$socialFeed.season;week=$socialFeed.week;phase=$socialFeed.phase;sourceUnchanged=$true;verified=$true;files=$socialItems}
$socialManifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $socialBackup 'backup-manifest.json') -Encoding utf8
$socialManifest | ConvertTo-Json -Depth 8
