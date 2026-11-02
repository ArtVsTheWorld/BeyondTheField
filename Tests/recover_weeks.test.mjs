import test from 'node:test';import assert from 'node:assert/strict';
import {updateRuntime} from '../Tools/runtime_lifecycle.mjs';import {recoverWeek} from '../Tools/recover_weeks.mjs';
const fixture=()=>({format:2,gameYear:27,sourceKind:'runtime',source:'runtime:7:1',sourceUnchanged:true,sha256:'a'.repeat(64),leagueId:7,userTeamIndex:1,season:{CurrentYear:0,CurrentSeasonYear:2026,CurrentWeek:2,CurrentWeekType:'RegularSeason',CurrentStage:'NFLSeason'},teams:[{id:1,name:'Home',logo:1,mediaRank:1,mediaLastRank:2},{id:2,name:'Away',logo:2,mediaRank:3}],players:[{id:'p',team:1,name:'A Player',position:'QB',overall:85,injury:'Injured'}],games:[{id:'two',year:0,week:2,phase:'RegularSeason',status:'HomeWon',published:true,home:1,away:2,homeScore:31,awayScore:7,homeStats:{OFFPASSYARDS:300,OFFRUSHYARDS:100,FIRSTDOWNS:20,GIVEAWAYS:0}},{id:'three',year:0,week:3,phase:'RegularSeason',status:'AwayWon',published:true,home:1,away:2,homeScore:7,awayScore:21}],performances:[{game:'two',player:'p',team:1,type:'GameOffensiveStats',stats:{PASSATTEMPTS:25,PASSCOMPLETED:20,PASSYARDS:300,PASSTDS:4,PASSINTS:0}}],offers:[],commitments:[],heisman:[{player:'p',team:1,rank:1}],weeklyAwards:[],records:[]});
test('sim 2 to 4 recovers publication Week 3 from completed Week 2 games and preserves observed archives byte for byte',()=>{
 const s=fixture(),a=updateRuntime(structuredClone(s)),old=JSON.stringify(a.state.editions[0].feed);s.season.CurrentWeek=4;const b=updateRuntime(structuredClone(s),a.state),recovered=b.state.editions.find(e=>e.week===3);
 assert.deepEqual(b.catalog.weeks.map(e=>e.week),[2,3,4]);assert.equal(recovered.reconstructed,true);assert.equal(recovered.snapshot,undefined);assert.equal(JSON.stringify(b.state.editions[0].feed),old);
 assert.ok(recovered.feed.stories.length);assert.ok(recovered.feed.events.every(e=>['results','team-stats','player-stats'].includes(e.category)&&e.eventWeek===2&&e.publication.week===3));
 assert.ok(recovered.feed.stories.every(p=>!p.replyTo&&!['official','player','recruit','fan','model'].includes(p.voice)));assert.ok(recovered.feed.stories.some(p=>p.body.includes('300')));assert.ok(!recovered.feed.stories.some(p=>/Heisman|injur|AP poll|scholarship/i.test(p.body)));
 assert.deepEqual(updateRuntime(structuredClone(s),b.state).catalog,b.catalog);
});
test('no first-observation invented editions; only same-phase known gaps; empty or unpublished game weeks stay absent',()=>{
 const s=fixture();s.season.CurrentWeek=4;assert.deepEqual(updateRuntime(structuredClone(s)).catalog.weeks.map(e=>e.week),[4]);
 assert.equal(recoverWeek(s,0),null);s.games[0].published=false;assert.equal(recoverWeek(s,3),null);s.season.CurrentWeekType='BowlSeason1';assert.equal(recoverWeek(s,3),null);
});
test('recovered editions cannot masquerade as observed recruiting or injury baselines after a rewind',()=>{
 const s=fixture(),a=updateRuntime(structuredClone(s));s.season.CurrentWeek=4;const b=updateRuntime(structuredClone(s),a.state);s.season.CurrentWeek=3;s.offers=[{team:1,player:'p'}];const c=updateRuntime(s,b.state);
 const current=c.state.editions.find(e=>e.week===3);assert.equal(current.reconstructed,undefined);assert.ok(current.snapshot);assert.ok(c.catalog.events.every(e=>e.category!=='offers'||e.publication.week===3));assert.deepEqual(c.catalog.weeks.map(e=>e.week),[2,3]);
});

test('runtime sources and packs use valid UTF-8; generated scores never contain replacement glyphs',async()=>{
 const fs=await import('node:fs/promises'),decoder=new TextDecoder('utf-8',{fatal:true});for(const folder of ['Tools','Content/Runtime'])for(const name of await fs.readdir(folder))if(/\.(mjs|json)$/.test(name))decoder.decode(await fs.readFile(folder+'/'+name));
 const s=fixture();s.season.CurrentWeek=4;const r=recoverWeek(s,3);assert.ok(r.feed.stories.every(p=>!p.body.includes('\uFFFD')));assert.ok(r.feed.stories.some(p=>p.body.includes('31\u20137')));
});
