import test from 'node:test';import assert from 'node:assert/strict';
import {historyMilestoneEvents,milestoneTotals,historicalEvent,lastHistoricalEvent,ordinal} from '../Tools/history_milestones.mjs';
import {lateSeasonEvents} from '../Tools/late_season_events.mjs';
import {verifiedPlayerStats,deepAnalyticsEvents} from '../Tools/deep_analytics.mjs';
import {updateRuntime} from '../Tools/runtime_lifecycle.mjs';
import {normalizeDynasty} from '../Tools/normalize_dynasty.mjs';
import {buildFeed} from '../Tools/feed_engine.mjs';
import {filterConversations} from '../Tools/social_discovery.mjs';
import {curate} from '../Tools/feed_selection.mjs';
const fixture=()=>({format:2,gameYear:27,sourceKind:'runtime',source:'runtime:7:1',sourceUnchanged:true,sha256:'a'.repeat(64),leagueId:7,userTeamIndex:1,season:{CurrentYear:0,CurrentSeasonYear:2026,CurrentWeek:14,CurrentWeekType:'RegularSeason',CurrentStage:'NFLSeason',RegularSeasonWeekConferenceChampionship:15},teams:[{id:1,name:'Harbor',nickname:'Hawks',logo:1,mediaRank:1,wins:10,losses:2,ties:0,conferenceId:'c',conferenceName:'Coastal',conferenceRank:1,conferenceWins:7,conferenceLosses:1,rivals:[2],historicalStats:{Wins:499,Losses:500,Ties:0,BowlsMade:5,NationalChampionshipsWon:1},headCoach:{id:'coach',name:'Amir Cole',lastName:'Cole',careerStats:{Wins:99,BowlWins:2}}},{id:2,name:'Valley',nickname:'Bears',logo:2,mediaRank:2,wins:9,losses:3,ties:0,conferenceId:'c',conferenceName:'Coastal',conferenceRank:2,conferenceWins:6,conferenceLosses:2}],conferences:[{id:'c',name:'Coastal',teams:[1,2],championshipType:'TOPTEAMS'}],players:[{id:'p',team:1,name:'Evan Moss',firstName:'Evan',lastName:'Moss',position:'QB',injury:'Uninjured',portrait:146,seasonStats:[],careerStats:{type:'CareerOffensiveStats',stats:{PASSYARDS:2990,PASSTDS:24}}}],games:[],performances:[],offers:[],commitments:[],heisman:[],records:[]});
const game=(id,week=15)=>({id,year:0,phase:'RegularSeason',week,status:'Unplayed',home:1,away:2});

test('first milestone observation is quiet; real crossings persist without reroll and rewind removes them',()=>{
 const s=fixture(),seed=updateRuntime(structuredClone(s));assert.equal(seed.catalog.events.filter(e=>e.id.startsWith('history:')).length,0);
 s.teams[0].historicalStats.Wins=500;s.teams[0].headCoach.careerStats.Wins=100;s.players[0].careerStats.stats.PASSYARDS=3100;s.sha256='b'.repeat(64);
 const changed=updateRuntime(structuredClone(s),seed.state);for(const key of ['history:wins:','history:coach:','history:player:'])assert.ok(changed.catalog.events.some(e=>e.id.startsWith(key)),key);
 const repeat=updateRuntime(structuredClone(s),changed.state);assert.deepEqual(repeat.catalog.stories,changed.catalog.stories);
 const restored=fixture();restored.sha256='c'.repeat(64);assert.equal(updateRuntime(restored,changed.state).catalog.events.filter(e=>e.id.startsWith('history:')).length,0);
});
test('all-time percentages use native totals, half ties, exact boundaries and both crossing directions',()=>{
 const s=fixture();s.milestoneBaseline=milestoneTotals(s);s.teams[0].historicalStats.Wins=500;let e=historyMilestoneEvents(s).find(e=>e.id.startsWith('history:percentage:'));assert.equal(e.facts.boundary,'.500');assert.equal(e.facts.direction,'to or above');
 s.milestoneBaseline=milestoneTotals(s);s.teams[0].historicalStats.Losses=501;e=historyMilestoneEvents(s).find(e=>e.id.startsWith('history:percentage:'));assert.equal(e.facts.direction,'below');
 s.teams[0].historicalStats={Wins:1,Losses:1,Ties:2};assert.equal(milestoneTotals(s).teams[1].Wins,1);s.milestoneBaseline.year=2025;assert.deepEqual(historyMilestoneEvents(s),[]);
});
test('Nth team and coach achievements require observed increases, with distinct title wins and title-game appearances',()=>{
 const s=fixture();Object.assign(s.teams[0].historicalStats,{NationalChampionshipsMade:0,HeismanWinners:0});s.milestoneBaseline=milestoneTotals(s);Object.assign(s.teams[0].historicalStats,{NationalChampionshipsWon:2,NationalChampionshipsMade:1,HeismanWinners:1});s.teams[0].headCoach.careerStats.BowlWins=3;
 const e=historyMilestoneEvents(s);assert.ok(e.some(e=>e.facts.ordinal==='2nd'&&e.facts.achievement==='national championship'));assert.ok(e.some(e=>e.facts.ordinal==='1st'&&e.facts.achievement==='national championship game appearance'));assert.ok(e.some(e=>e.facts.achievement==='Heisman Trophy winner'));assert.ok(e.some(e=>e.facts.coachName==='Amir Cole'&&e.facts.ordinal==='3rd'));assert.deepEqual([1,2,3,11,12,13,21].map(ordinal),['1st','2nd','3rd','11th','12th','13th','21st']);
});
test('player career milestones use native career counters, including half sacks and former-school production',()=>{
 const s=fixture();s.players[0].careerStats={type:'CareerDefensiveStats',stats:{DLINESACKS:9,DLINEHALFSACK:1,DEFTACKLES:80,ASSDEFTACKLES:19,DLINEFORCEDFUMBLES:4}};s.milestoneBaseline=milestoneTotals(s);Object.assign(s.players[0].careerStats.stats,{DLINESACKS:10,DEFTACKLES:81,DLINEFORCEDFUMBLES:5});const e=historyMilestoneEvents(s);for(const metric of ['sacks','tackles','forced fumbles'])assert.ok(e.some(e=>e.facts.metric===metric));assert.equal(e.find(e=>e.facts.metric==='sacks').facts.total,'10.5');
 s.milestoneBaseline.players={};assert.ok(!historyMilestoneEvents(s).some(e=>e.options.player==='p'));
});
test('new publication editions use the last observed career baseline, including earlier-phase history',()=>{
 const s=fixture(),first=updateRuntime(structuredClone(s));s.season.CurrentWeek=15;s.players[0].careerStats.stats.PASSYARDS=3020;
 assert.ok(updateRuntime(structuredClone(s),first.state).catalog.events.some(e=>e.id.startsWith('history:player:')));
 s.season.CurrentWeekType='BowlSeason1';s.season.CurrentWeek=17;
 const archives=[{...first.catalog,milestoneObservation:first.state.editions[0].snapshot.milestoneTotals}];assert.ok(updateRuntime(structuredClone(s),undefined,{archives}).catalog.events.some(e=>e.id.startsWith('history:player:')));
});
test('old ordinary bowls are not playoff appearances; since-year claims require complete intervening history',()=>{
 assert.equal(historicalEvent({Year:2020,FirstRoundCFPBowlGameResult:'Win',FirstRoundCFPBowlPresentationId:'AlamoBowl'},'playoffAppearance'),false);
 assert.equal(historicalEvent({Year:2024,FirstRoundCFPBowlGameResult:'Loss',FirstRoundCFPBowlPresentationId:'CFPFirstRound'},'playoffAppearance'),true);
 assert.equal(historicalEvent({Year:2013,SemiFinalsBowlGameResult:'Win'},'playoffAppearance'),false);
 const t={seasonHistory:[{Year:2025},{Year:2023,NationalBowlGameResult:'Win'},{Year:2024}]};assert.equal(lastHistoricalEvent(t,2026,'nationalAppearance'),2023);t.seasonHistory=t.seasonHistory.filter(r=>r.Year!==2024);assert.equal(lastHistoricalEvent(t,2026,'nationalAppearance'),null);
});
test('Week 14 invitations need actual assigned fixtures in the configured championship week',()=>{
 const s=fixture();s.games=[game('title'),game('army-navy',14)];let e=lateSeasonEvents(s).filter(e=>e.facts.family==='late.title-invite');assert.equal(e.length,2);assert.ok(e.every(e=>e.facts.championshipWeek===15));
 s.season.CurrentWeek=13;assert.ok(!lateSeasonEvents(s).some(e=>e.facts.family==='late.title-invite'));s.season.CurrentWeek=14;s.conferences[0].championshipType='NONE';assert.ok(!lateSeasonEvents(s).some(e=>e.facts.family==='late.title-invite'));s.conferences[0].championshipType='TOPTEAMS';s.teams[1].conferenceId='other';assert.ok(!lateSeasonEvents(s).some(e=>e.facts.family==='late.title-invite'));
});
test('late standings are discussion, not clinches; bowl thresholds are not invitations',()=>{
 const s=fixture();s.season.CurrentWeek=11;s.teams[0].wins=5;s.games=[game('remaining',12)];const e=lateSeasonEvents(s);assert.ok(e.some(e=>e.facts.family==='late.conference-race'));assert.ok(e.some(e=>e.facts.family==='late.bowl-one-away'));assert.ok(!e.some(e=>/invite|berth/.test(e.facts.family)));
 s.season.CurrentWeek=15;s.games=[{...game('bowl',17),phase:'BowlSeason1',bowlName:'Harbor Bowl',isPlayoff:false},{...game('playoff',17),phase:'BowlSeason1',home:1,away:255,isPlayoff:true}];const invites=lateSeasonEvents(s).filter(e=>e.facts.family==='late.bowl-invite');assert.equal(invites.length,2);assert.ok(!lateSeasonEvents(s).some(e=>e.facts.family==='late.playoff-berth'));
});
test('rivalry hype belongs to the current scheduled week and fan replies retain a real parent',()=>{
 const s=fixture();s.games=[game('rival',14)];const f=buildFeed(s),rival=f.events.filter(e=>e.id.startsWith('late:rivalry'));assert.ok(rival.some(e=>e.facts.voice==='fan'));assert.ok(rival.some(e=>e.facts.voice==='official'));assert.ok(f.stories.filter(p=>p.replyTo).every(p=>f.stories.some(parent=>parent.id===p.replyTo)));s.games[0].week=13;assert.ok(!lateSeasonEvents(s).some(e=>e.id.startsWith('late:rivalry')));
});
test('year-over-year comparisons retain the actual prior conference and do not compare finish across realignment',()=>{
 const s=fixture();s.teams[0].seasonHistory=[{Year:2025,Wins:3,Losses:9,ConferenceName:'Old League',FinalConferenceStanding:9,ConferenceWins:1,ConferenceLosses:7}];const e=lateSeasonEvents(s);assert.equal(e.find(e=>e.facts.family==='late.turnaround').facts.previousConference,'Old League');assert.ok(!e.some(e=>e.facts.family==='late.conference-change'));
});
test('a late CFP stakes story names the actual current opponent and does not convert ranking into a berth',()=>{
 const s=fixture();s.teams=Array.from({length:25},(_,i)=>({...s.teams[i%2],id:i+1,name:'Team '+(i+1),cfpRank:i+1}));s.games=[game('current',14)];const e=lateSeasonEvents(s).filter(e=>e.facts.family==='late.cfp-stakes');assert.equal(e.length,2);assert.equal(e[0].facts.opponent,'Team 2');s.season.CurrentWeek=11;assert.ok(!lateSeasonEvents(s).some(e=>e.facts.family==='late.cfp-stakes'));
});
test('confirmed user-team title announcements retain room before fan reactions consume thread slots',()=>{
 const posts=[{id:'announcement',category:'championship',voice:'official',priority:112,scopes:['team'],thread:'title',handle:'@Harbor',likes:1000},...[1,2].map(i=>({id:'fan'+i,category:'championship',voice:'fan',priority:98,scopes:['team'],thread:'title',handle:'@fan'+i,likes:100}))];assert.ok(curate(posts).some(p=>p.id==='announcement'));
});
function playerStats(kind,stats){const s=fixture();s.season.CurrentWeek=4;s.players[0].seasonStats=[{type:'Season'+kind,stats:{GAMESPLAYED:3,...stats}}];s.games=[0,1,2].map(i=>({...game('g'+i,i),status:'HomeWon',published:true,homeScore:30,awayScore:7}));s.performances=s.games.map((g,i)=>({player:'p',team:1,game:g.id,type:'Game'+kind,stats:Object.fromEntries(Object.entries(stats).map(([k,v])=>[k,i===0?v:0]))}));return s;}
test('advanced rates corroborate published games and include derived offensive/defensive returner types',()=>{
 const s=playerStats('OffensiveKPReturnStats',{RUSHATTEMPTS:100,RUSHBROKENTACKLES:125,RUSHYARDSAFTER1STHIT:250,RUSHYARDS:600,RECEIVECATCHES:20,RECEIVEYARDS:300,RECEIVEYARDSAFTER:180,KRETATTEMPTS:10,KRETYARDS:250,KRETTDS:1});let e=deepAnalyticsEvents(s,{bounded:false});assert.equal(e.find(e=>e.facts.family==='deep.broken-tackles').facts.rate,'125.0');assert.equal(e.find(e=>e.facts.family==='deep.yac-share').facts.rate,'60.0');assert.ok(e.some(e=>e.facts.family==='deep.kick-return'));
 s.performances[0].stats.RUSHBROKENTACKLES=120;assert.ok(!deepAnalyticsEvents(s,{bounded:false}).some(e=>e.facts.family==='deep.broken-tackles'));s.games[0].published=false;assert.equal(verifiedPlayerStats(s,s.players[0],'offense'),null);
});
test('missing denominators, duplicate game rows and YAC exceeding total receiving yards suppress misleading analysis',()=>{
 const s=playerStats('OffensiveStats',{RECEIVECATCHES:25,RECEIVEYARDS:300,RECEIVEYARDSAFTER:350});assert.ok(!deepAnalyticsEvents(s,{bounded:false}).some(e=>e.facts.family==='deep.yac-share'));s.performances.push(s.performances[0]);assert.equal(verifiedPlayerStats(s,s.players[0],'offense'),null);
 const t=playerStats('DefensiveKPReturnStats',{DEFTACKLES:30,ASSDEFTACKLES:6,DLINESACKS:2,DLINEHALFSACK:2,DSECINTS:3});let e=deepAnalyticsEvents(t,{bounded:false});assert.equal(e.find(e=>e.facts.family==='deep.tackles-game').facts.rate,'12.0');assert.equal(e.find(e=>e.facts.family==='deep.sacks-game').facts.total,3);assert.equal(e.find(e=>e.facts.family==='deep.ints-game').facts.rate,'1.00');
});
test('OL rates use offensive snaps; kicker and returner rates respect samples and made/attempt bounds',()=>{
 let s=playerStats('OLineStats',{DOWNSPLAYED:200,OLINESACKSALLOWED:3,OLINEPANCAKES:15});assert.equal(deepAnalyticsEvents(s,{bounded:false}).find(e=>e.facts.family==='deep.line-sacks').facts.rate,'1.50');
 s=playerStats('KickingStats',{KICKFGATTEMPTS50ORMORE:4,KICKFGMADE50ORMORE:3,PUNTATTEMPTS:20,PUNTIN20:10,PUNTTOUCHBACKS:2});let e=deepAnalyticsEvents(s,{bounded:false});assert.equal(e.find(e=>e.facts.family==='deep.long-kicks').facts.rate,'75.0');assert.equal(e.find(e=>e.facts.family==='deep.punt-placement').facts.rate,'50.0');s.players[0].seasonStats[0].stats.KICKFGMADE50ORMORE=5;s.performances[0].stats.KICKFGMADE50ORMORE=5;assert.ok(!deepAnalyticsEvents(s,{bounded:false}).some(e=>e.facts.family==='deep.long-kicks'));
});
test('dual production stories require both stats from the same published recent game',()=>{
 const s=playerStats('OffensiveStats',{PASSYARDS:300,RUSHYARDS:70});s.games[0].week=3;let e=deepAnalyticsEvents(s);assert.ok(e.some(e=>e.facts.family==='deep.dual-qb-game'));s.performances[0].stats.PASSYARDS=200;s.performances[1].stats.PASSYARDS=100;assert.ok(!deepAnalyticsEvents(s).some(e=>e.facts.family==='deep.dual-qb-game'));
});
test('new category labels participate in native-compatible ranking filters while attached replies stay together',()=>{
 assert.deepEqual(filterConversations([{id:'a',category:'history'},{id:'b',category:'championship'},{id:'c',category:'bowls'},{id:'r',replyTo:'c',category:'schedule'}],'rankings').map(x=>x.id),['a','b','c','r']);
});
test('normalizer resolves history, calendar years, coach careers, polymorphic player careers and configured title week',async()=>{
 const rows=[{key:'s',type:'SeasonInfo',v:{CurrentYear:1,CurrentSeasonYear:2027,CurrentWeek:14,RegularSeasonWeekConferenceChampionship:15}},{key:'f',type:'Franchise',v:{LeagueID:7}},{key:'u',type:'FranchiseUser',v:{Team:'t'}},{key:'t',type:'Team',capacity:2,v:{TeamIndex:1,DisplayName:'Harbor',HomeWin:1,RoadWin:0,HomeLoss:0,RoadLoss:0,HeadCoach:'c',TeamHistoricalData:'h',TeamSeriesHistory:'series'}},{key:'h',type:'TeamHistoricalData',v:{Wins:500,NationalChampionshipsMade:1,NationalChampionshipsWon:3}},{key:'y',type:'TeamHistoricSeriesYear',v:{Year:2026,Wins:10,Losses:2,ConferenceName:'Old League'}},{key:'c',type:'Coach',v:{TeamIndex:1,FirstName:'Amir',LastName:'Cole',CareerStats:'cc',SeasonStats:'cs'}},{key:'cc',type:'CareerCoachStats',v:{Wins:100}},{key:'cs',type:'SeasonCoachStats',v:{Wins:1}},{key:'p',type:'Player',v:{TeamIndex:1,FirstName:'Evan',LastName:'Moss',CareerStats:'pc',SeasonStats:'seasons'}},{key:'pc',type:'CareerOffensiveStats',v:{PASSYARDS:3100}},{key:'ps',type:'SeasonOffensiveStats',v:{SEAS_YEAR:0,YEARBYYEARTEAMINDEX:2,PASSYARDS:3000}}];const map=new Map(rows.map(r=>[r.key,r]));const arrays={series:[map.get('y')],seasons:[map.get('ps')]};
 const s=await normalizeDynasty({records:async t=>rows.filter(r=>r.type===t),resolve:async k=>map.get(k)??null,array:async k=>arrays[k]??[],arraySlots:async()=>[]},{});assert.equal(s.teams[0].historicalStats.NationalChampionshipsWon,3);assert.equal(s.teams[0].seasonHistory[0].Year,2026);assert.equal(s.teams[0].headCoach.careerStats.Wins,100);assert.equal(s.players[0].careerStats.stats.PASSYARDS,3100);assert.equal(s.players[0].allSeasonStats.length,1);assert.equal(s.players[0].seasonStats.length,0);assert.equal(s.season.RegularSeasonWeekConferenceChampionship,15);
});
