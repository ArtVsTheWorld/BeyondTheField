import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {readRuntime} from './read_runtime.mjs';
import {advancedAnalytics,TEAM_SCENARIOS,PLAYER_SCENARIOS} from './advanced_analytics.mjs';
import {contentPack} from './story_templates.mjs';
const [rawPath,feedPath,output]=process.argv.slice(2);
if(!rawPath||!feedPath)throw Error('Usage: node audit_world_news.mjs runtime-raw.json runtime-feed.json [audit.json]');
const raw=JSON.parse(await fs.readFile(rawPath,'utf8')),s=await readRuntime(raw),feed=JSON.parse(await fs.readFile(feedPath,'utf8'));
assert.equal(feed.leagueId,s.leagueId);assert.equal(feed.userTeamIndex,s.userTeamIndex);assert.equal(feed.week,s.season.CurrentWeek);
const byId=new Map(feed.stories.map(p=>[p.id,p]));
for(const p of feed.stories){
 assert.ok([...p.body].length<=280&&Buffer.byteLength(p.body,'utf8')<=512&&!p.body.includes('\uFFFD'),'Invalid body '+p.id);
 assert.ok(!Object.hasOwn(p,'views'),'Views must not be generated');
 if(p.replyTo){const parent=byId.get(p.replyTo);assert.ok(parent,'Orphan reply '+p.id);assert.ok(p.likes>=Math.floor(parent.likes*.01)&&p.likes<=Math.floor(parent.likes*.2),'Reply engagement outside parent range '+p.id);}
 else assert.ok(p.likes<=10000,'Engagement exceeds maximum');
}
assert.ok(feed.posts.length<=30);
const tally=(rows,key)=>Object.fromEntries([...new Set(rows.map(key))].sort().map(k=>[k,rows.filter(r=>key(r)===k).length]));
const candidates=advancedAnalytics(s,{bounded:false}),selected=advancedAnalytics(s);
const audit={format:1,contentRevision:contentPack.revision,publicationWeek:feed.week,rawRecords:Object.keys(raw.records).length,teams:s.teams.filter(t=>t.id!==255).length,conferences:s.conferences.length,seasonStatPlayers:s.players.filter(p=>p.seasonStats?.length).length,publishedPlayerGameStatRows:s.performances.length,nativeWeeklyAwards:s.weeklyAwards.length,nativeRecords:s.records.length,teamAnalysisScenarios:TEAM_SCENARIOS.length,playerAnalysisScenarios:PLAYER_SCENARIOS.length,qualifyingScenarioTypes:new Set(candidates.map(c=>c.key)).size,selectedAdditionalAnalyses:selected.length,templateFamilies:Object.keys(contentPack.families).length,templateVariants:Object.values(contentPack.families).flat().length,stories:feed.stories.length,replies:feed.stories.filter(p=>p.replyTo).length,curatedPosts:feed.posts.length,scopeOptions:feed.scopeOptions.length,eventsByCategory:tally(feed.events,e=>e.category),storiesByVoice:tally(feed.stories,p=>p.voice),maximumBodyCharacters:Math.max(...feed.stories.map(p=>[...p.body].length)),maximumRootLikes:Math.max(...feed.stories.filter(p=>!p.replyTo).map(p=>p.likes)),maximumReplyLikes:Math.max(...feed.stories.filter(p=>p.replyTo).map(p=>p.likes)),viewsGenerated:false};
if(output)await fs.writeFile(output,JSON.stringify(audit,null,2)+'\n');
console.log(JSON.stringify(audit,null,2));
