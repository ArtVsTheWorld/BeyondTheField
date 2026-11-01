// Acceptance check against an actual backed-up Dynasty and the newly saved week.
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readDynasty} from './read_dynasty.mjs';
const [backup,configPath]=process.argv.slice(2);
if(!backup||!configPath)throw Error('Usage: node verify_rollover.mjs backup-directory social-refresh.json');
const read=async p=>JSON.parse((await fs.readFile(p,'utf8')).replace(/^\uFEFF/,''));
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const manifest=await read(path.join(backup,'backup-manifest.json'));
assert.equal(manifest.verified,true);
for(const file of manifest.files)assert.equal(hash(await fs.readFile(file.backup)),file.sha256,'Backup checksum changed');
const before=await read(path.join(backup,'social-feed.json')),c=await read(configPath);
const s=await readDynasty(c.save,c.schema,c.parser);
const feed=await read(path.join(path.dirname(configPath),'social-feed.json'));
assert.equal(s.leagueId,manifest.leagueId,'Different Dynasty');assert.equal(s.userTeamIndex,manifest.teamIndex,'Different controlled team');
assert.equal(s.season.CurrentSeasonYear,manifest.season,'Unexpected season change');assert.equal(s.season.CurrentWeekType,manifest.phase,'Unexpected phase change');
assert.equal(s.season.CurrentWeek,manifest.week+1,'Dynasty has not advanced exactly one week');
assert.notEqual(s.sha256,before.sha256,'Save fingerprint did not change');assert.equal(feed.sha256,s.sha256,'Feed has not refreshed to this save yet');
assert.equal(feed.week,s.season.CurrentWeek);assert.equal(feed.leagueId,s.leagueId);assert.equal(new Set(feed.posts.map(p=>p.id)).size,feed.posts.length,'Duplicate posts');
const done=g=>['HomeWon','AwayWon','Tie'].includes(g.status);
const last=s.games.filter(g=>g.year===s.season.CurrentYear&&g.phase===s.season.CurrentWeekType&&g.week===manifest.week&&done(g));
const games=new Map(last.map(g=>[g.id,g]));
for(const p of feed.posts.filter(p=>p.category==='results')){
  const g=games.get(p.id.slice('result:'.length));assert.ok(g,'Result refers to the wrong week/game');
  assert.match(p.stamp,new RegExp(`Week ${manifest.week}$`));assert.ok(p.body.includes(String(g.homeScore))&&p.body.includes(String(g.awayScore)),'Result score mismatch');
}
const performanceIds=new Set(s.performances.filter(p=>games.has(p.game)).map(p=>`performance:${p.game}:${p.player}:${p.type}`));
for(const p of feed.posts.filter(p=>p.category==='player-stats'))assert.ok(performanceIds.has(p.id),'Player stat line not linked to the previous week');
const upcoming=new Set(s.games.filter(g=>g.week===s.season.CurrentWeek&&g.phase===s.season.CurrentWeekType&&!done(g)).map(g=>`preview:${g.id}`));
for(const p of feed.posts.filter(p=>p.category==='schedule'))assert.ok(upcoming.has(p.id),'Preview is not a current-week unplayed game');
const userGame=last.find(g=>[g.home,g.away].includes(s.userTeamIndex));
if(userGame)assert.ok(feed.posts.some(p=>p.id===`result:${userGame.id}`),'Controlled team recap missing');
const afterHash=hash(await fs.readFile(c.save));assert.equal(afterHash,s.sha256,'Source changed during verification');
const report={passed:true,leagueId:s.leagueId,season:s.season.CurrentSeasonYear,fromWeek:manifest.week,toWeek:s.season.CurrentWeek,
  posts:feed.posts.length,sourceUnchanged:true,sourceSha256:s.sha256,backupVerified:true,userGameRecap:userGame?.id??null,
  categories:[...new Set(feed.posts.map(p=>p.category))],resultPosts:feed.posts.filter(p=>p.category==='results').map(p=>p.body)};
await fs.writeFile(path.join(backup,'rollover-verification.json'),JSON.stringify(report,null,2));
console.log(JSON.stringify(report,null,2));
