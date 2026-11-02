import test from 'node:test';
import assert from 'node:assert/strict';
import {readRuntime} from '../Tools/read_runtime.mjs';
import {updateRuntime} from '../Tools/runtime_lifecycle.mjs';
function raw(status='None'){
 const records={};const add=(key,type,v,capacity=1)=>records[key]={key,type,v,capacity};
 add('season','SeasonInfo',{CurrentSeasonYear:2027,CurrentYear:1,CurrentWeek:8,CurrentWeekType:'RegularSeason',CurrentStage:'NFLSeason'});
 add('league','Franchise',{LeagueID:10});add('flow','FranchiseServer_CareerFlow',{IsStageActive:true,IsStageAdvancing:false});
 add('user','FranchiseUser',{Team:'team',AdminLevel:'Owner',IsRetired:false});
 add('team','Team',{TeamIndex:1,DisplayName:'Fixture University',TEAM_LOGO:11,RecruitingBoard:'board',HomeWin:0,RoadWin:0,HomeLoss:0,RoadLoss:0},143);
 add('player','Player',{FirstName:'Fixture',LastName:'Recruit',TeamIndex:255,Position:'QB',InjuryStatus:'Uninjured',Personality:'Leader',IsNIL:false});
 add('recruit','Recruit',{Player:'player',RecruitStage:'Top10',NationalRank:50});
 add('board','RecruitingBoard',{Recruits:'targets'});add('targets','UserRecruitTarget[]',{Member0:'target'});
 add('target','UserRecruitTarget',{Recruit:'recruit',ScholarshipStatus:status,CommittedWeekNumber:0});
 return {format:1,sourceKind:'runtime',records};
}
test('native New scholarship state becomes a midweek offer event, and Offered does not duplicate it',async()=>{
 const a=updateRuntime(await readRuntime(raw('None')));assert.equal(a.catalog.events.filter(p=>p.category==='offers').length,0);
 const snapshot=await readRuntime(raw('New'));assert.equal(snapshot.offers.length,1);
 const b=updateRuntime(snapshot,a.state),offer=b.catalog.events.find(p=>p.category==='offers');
 assert.equal(offer.facts.school,'Fixture University');assert.equal(offer.facts.playerName,'Fixture Recruit');assert.equal(offer.body,undefined);assert.ok(offer.scopes.includes('team'));assert.equal(offer.publication.week,8);
 const c=updateRuntime(await readRuntime(raw('Offered')),b.state);assert.equal(c.catalog.events.filter(p=>p.category==='offers').length,1);
 const next=raw('Offered');next.records.season.v.CurrentWeek=9;const d=updateRuntime(await readRuntime(next),c.state);assert.equal(d.catalog.events.filter(p=>p.category==='offers').length,0);
 assert.equal(d.catalog.weeks[0].events.filter(p=>p.category==='offers').length,1);
});
test('initial native New offers seed quietly, while non-offer board entries stay excluded',async()=>{
 const s=await readRuntime(raw('New'));const initial=updateRuntime(s);assert.equal(initial.catalog.events.filter(p=>p.category==='offers').length,0);
 for(const status of ['None','Declined'])assert.equal((await readRuntime(raw(status))).offers.length,0);
});

test('native personality reaches structured events and missing/sentinel values fall back neutrally',async()=>{
 const initial=updateRuntime(await readRuntime(raw('None')));const s=await readRuntime(raw('New'));assert.equal(s.players[0].personality,'Leader');
 assert.equal(updateRuntime(s,initial.state).catalog.events.find(e=>e.category==='offers').personality,'Leader');
 for(const value of [undefined,'Invalid_','NPCAvailableCount_']){const input=raw('New');input.records.player.v.Personality=value;assert.equal((await readRuntime(input)).players[0].personality,null);}
});

test('team identity and current coach references resolve from live records without inventing contact events',async()=>{
 const input=raw('New');Object.assign(input.records.team.v,{NickName:'Fixture Falcons',NickNameAlt:'Falcons',Hashtag1:' #FlyFixture ',Hashtag2:'FlyFixture',HeadCoach:'coach'});
 input.records.coach={key:'coach',type:'Coach',capacity:1,v:{FirstName:'Casey',LastName:'Dunn',TeamIndex:1}};
 input.records.player.v.TeamIndex=1;input.records.player.v.JerseyNum=0;
 const s=await readRuntime(input),t=s.teams[0];assert.equal(t.nickname,'Fixture Falcons');assert.deepEqual(t.hashtags,['#FlyFixture']);assert.equal(t.headCoach.name,'Casey Dunn');assert.equal(s.players[0].jerseyNumber,0);
 const baseline=updateRuntime(await readRuntime(raw('None'))),event=updateRuntime(s,baseline.state).catalog.events.find(e=>e.category==='offers');assert.equal(event.teamContext[0].headCoach.name,'Casey Dunn');assert.equal(event.facts.phoneCall,undefined);
 input.records.coach.v.TeamIndex=2;input.records.team.v.Hashtag1='bad tag';input.records.team.v.Hashtag2='';input.records.team.v.NickName='';const sparse=await readRuntime(input);assert.equal(sparse.teams[0].headCoach,null);assert.equal(sparse.teams[0].nickname,null);assert.deepEqual(sparse.teams[0].hashtags,[]);
});

test('current-first season arrays preserve null slots and do not use CurrentYear as a slot index',async()=>{
 const input=raw('New');input.records.season.v.CurrentYear=1;input.records.team.v.TeamSeasonStats='season-array';
 input.records['season-array']={key:'season-array',type:'TeamStats[]',capacity:1,v:{Member0:'current',Member1:'old'}};
 input.records.current={key:'current',type:'TeamStats',capacity:1,v:{WINS:3,LOSSES:0,TIES:0,OFFRUSHYARDS:500}};
 input.records.old={key:'old',type:'TeamStats',capacity:1,v:{WINS:12,LOSSES:1,TIES:0,OFFRUSHYARDS:3000}};
 assert.equal((await readRuntime(input)).teams[0].seasonStats.stats.WINS,3);
 input.records['season-array'].v.Member0=null;assert.equal((await readRuntime(input)).teams[0].seasonStats,null);
});

test('cached unpublished scores and quarter splits never enter the public snapshot',async()=>{
 const input=raw('None');input.records.team2={key:'team2',type:'Team',capacity:143,v:{TeamIndex:2,DisplayName:'Opponent',HomeWin:0,RoadWin:0,HomeLoss:0,RoadLoss:0}};
 input.records.match={key:'match',type:'SeasonGame',capacity:1000,v:{SeasonYear:1,SeasonWeek:8,SeasonWeekType:'RegularSeason',GameStatus:'HomeWon',HasBeenPublished:false,HomeTeam:'team',AwayTeam:'team2',HomeScore:99,AwayScore:3,HomeScoreQuarter1:40}};
 const s=await readRuntime(input),g=s.games[0];assert.equal(g.status,'Unplayed');assert.equal(g.homeScore,0);assert.equal(g.awayScore,0);assert.equal(g.homeQuarterScores,null);
 const e=updateRuntime(s).catalog.events;assert.ok(!e.some(e=>e.category==='results'));assert.ok(e.some(e=>e.category==='schedule'));
});

test('native zero-based Heisman ranks match the menu and preserve the leader and unknown prior rank',async()=>{
 const input=raw('None');input.records.player.v.TeamIndex=1;
 input.records.awards={key:'awards',type:'Awards',capacity:1,v:{HeismanRanking:'heisman-array'}};
 input.records['heisman-array']={key:'heisman-array',type:'HeismanAwardRanking[]',capacity:1,v:{}};
 for(const [i,[current,last]] of [[0,0],[1,2],[2,1],[3,-1],[-1,0],[undefined,0]].entries()){
  const key='h'+i;input.records[key]={key,type:'HeismanAwardRanking',capacity:1,v:{Player:'player',Team:'team',CurrentRank:current,LastWeekRank:last}};input.records['heisman-array'].v['Member'+i]=key;
 }
 const snapshot=await readRuntime(input);assert.deepEqual(snapshot.heisman.map(h=>[h.rank,h.lastRank]),[[1,1],[2,3],[3,2],[4,null]]);
});

test('native forced-silhouette preference survives portrait normalization',async()=>{
 const input=raw('None');input.records.player.v.PLYR_PORTRAIT=146;input.records.player.v.PortraitForceSilhouette=true;const s=await readRuntime(input);assert.equal(s.players[0].portrait,146);assert.equal(s.players[0].portraitForcedSilhouette,true);
});
