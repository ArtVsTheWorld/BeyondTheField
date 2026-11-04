import test from 'node:test';
import assert from 'node:assert/strict';
import {nilAllocation,NIL_DOLLARS_PER_POINT,verifiedTeamRows,relativeVerdict,schemes} from '../Tools/football_context.mjs';
import {contextualAnalytics} from '../Tools/context_analytics.mjs';
import {conferencePrestige,conferenceDiscourse} from '../Tools/conference_context.mjs';
import {completeOffensiveLine,heismanContext,correctHeismanArchive} from '../Tools/heisman_context.mjs';
import {renderStories} from '../Tools/story_renderer.mjs';

function fixture(){
 const s={leagueId:7,userTeamIndex:1,season:{CurrentYear:0,CurrentSeasonYear:2026,CurrentStage:'NFLSeason',CurrentWeekType:'RegularSeason',CurrentWeek:4},teams:[],players:[],games:[],performances:[],conferences:[]};
 const stats={PASSATTEMPTS:30,RUSHATTEMPTS:30,OFFPASSYARDS:240,OFFRUSHYARDS:150,DEFPASSYARDS:180,DEFRUSHYARDS:90,PASSTDS:2,RUSHTDS:2,PASSINTS:1,FUMBLESLOST:0,GIVEAWAYS:1,DEFINTS:2,FUMBLEREC:1,TAKEAWAYS:3,SACKS:3,PENALTIES:5,PENALTYYARDS:40};
 for(let i=1;i<=8;i++){
  s.teams.push({id:i,name:'School '+i,wins:3,losses:0,mediaRank:i,conferenceId:'custom-'+Math.ceil(i/4),offensiveScheme:'OFF_POWER_SPREAD',defensiveScheme:'DEF_4_3_MULTIPLE',conferencePrestigeGrade:i<=4?'APlus':'AMinus'});
  s.players.push({id:'p'+i,name:'Player '+i,team:i,position:'QB',nil:150});
  for(let w=0;w<3;w++)s.games.push({id:i+'-'+w,year:0,week:w,phase:'RegularSeason',home:i,away:100+i,awayName:'Opponent',homeScore:35,awayScore:14,status:'HomeWon',published:true,homeStats:{...stats},awayStats:{...stats,PASSATTEMPTS:20,RUSHATTEMPTS:25}});
 }
 s.conferences=[{id:'custom-1',name:'Northern League',teams:[1,2,3,4]},{id:'custom-2',name:'Mountain Association',teams:[5,6,7,8]}];return s;
}
test('NIL converts user-verified points to dollars and groups only the current roster',()=>{
 const s=fixture();s.players.push({id:'rb',team:1,position:'HB',nil:50},{id:'recruit',team:255,position:'QB',nil:900});
 const a=nilAllocation(s,1);assert.equal(NIL_DOLLARS_PER_POINT,4000);assert.equal(a.total,800000);assert.equal(a.groups[0].share,.75);assert.equal(a.groups[1].dollars,200000);
 s.players[0].nil=null;assert.equal(nilAllocation(s,1),null);
});
test('team rates use verified final games, actual opponent attempts and native schemes',()=>{
 const s=fixture(),r=verifiedTeamRows(s).get(1);assert.equal(r.ppg,35);assert.equal(r.ppga,14);assert.equal(r.ypg,390);assert.equal(r.ypp,6.5);assert.equal(r.yppa,6);assert.equal(r.read('PASSATTEMPTS',true),60);assert.equal(schemes[s.teams[0].offensiveScheme],'power spread');
 for(const g of s.games){g.homeStats.DEFPASSYARDS=270;g.awayStats.PASSATTEMPTS=30;}
 const e=contextualAnalytics(s,{bounded:false}).find(e=>e.id==='context:1:pass-defense');assert.equal(e.facts.ypa,'9.00');assert.equal(e.facts.verdict,'negative');
});
test('current full-season W/L/T corroborates neutral-site games omitted by home/road counters',()=>{
 const s=fixture();s.teams[0].wins=2;s.teams[0].seasonStats={season:2026,stats:{WINS:3,LOSSES:0,TIES:0}};assert.equal(verifiedTeamRows(s).get(1).n,3);
 s.teams[0].seasonStats.stats.WINS=4;assert.ok(!verifiedTeamRows(s).has(1));
});
test('unpublished games, missing caches and contradictory season totals cannot fabricate team rates',()=>{
 const s=fixture();s.games[0].published=false;assert.ok(!verifiedTeamRows(s).has(1));s.games[0].published=true;delete s.games[0].homeStats.OFFPASSYARDS;assert.equal(verifiedTeamRows(s).get(1).passYPG,null);
 assert.ok(!contextualAnalytics(s,{bounded:false}).some(e=>e.id==='context:1:passing'));
 s.teams[1].seasonStats={season:2026,stats:{OFFPASSYARDS:999}};assert.equal(verifiedTeamRows(s).get(2).passYPG,null);
});
test('team turnover sums and denominators must corroborate before publication',()=>{
 const s=fixture();s.games[0].homeStats.TAKEAWAYS=9;s.games[0].homeStats.GIVEAWAYS=9;
 const e=contextualAnalytics(s,{bounded:false});assert.ok(!e.some(e=>e.id==='context:1:disruption'));assert.ok(!e.some(e=>e.id==='context:1:ball-security'));
});
test('relative grading handles ties, small samples, reversed defensive measures and poor absolute efficiency',()=>{
 assert.equal(relativeVerdict(7,Array(8).fill(7)).verdict,'neutral');assert.equal(relativeVerdict(20,[1,2,3]).verdict,'neutral');assert.equal(relativeVerdict(1,[1,2,3,4,5,6,7,8],{higher:false}).verdict,'positive');assert.equal(relativeVerdict(4.5,[1,2,3,3.5,3.8,4,4.2,4.5],{poor:4.8,strong:6.2}).verdict,'negative');
});
test('new analytic families keep CPU and user eligibility identical and limit repeated angles',()=>{
 const s=fixture(),full=contextualAnalytics(s,{bounded:false});for(const id of [1,8])assert.ok(full.some(e=>e.id===`context:${id}:offense`));
 const limited=contextualAnalytics(s);for(const t of s.teams)assert.equal(limited.filter(e=>e.id.startsWith('context:'+t.id+':')).length,6);
});
test('coach context uses recorded career/school splits and proper win rates',()=>{
 const s=fixture();s.teams[0].headCoach={id:'c',name:'A Coach',careerStats:{Wins:80,Losses:20,WinsAtCurrentSchool:30,LossesAtCurrentSchool:10,Top25Wins:9,Top25Losses:3}};
 const a=contextualAnalytics(s).filter(e=>e.id.startsWith('coach'));assert.equal(a.length,2);assert.equal(a[0].facts.rate,'80.0');assert.equal(a[1].facts.rate,'75.0');assert.equal(a[0].facts.schoolWins,30);
});
test('neutral statistical facts do not receive celebration wrappers and negative efficiency stays negative',()=>{
 const s=fixture(),events=Array.from({length:40},(_,i)=>({id:'neutral:'+i,category:'analytics',teamIds:[1],scopes:['national'],priority:80,thread:'n'+i,facts:{family:'context.offense',school:'School 1',offense:'power spread',ppg:'24',ypg:'300',ypp:'4.5',games:3,comparison:'A limited sample.',verdict:i%2?'negative':'neutral'}}));
 const a=renderStories(s,events);assert.ok(a.stories.length);for(const p of a.stories)if(p.voiceTemplateId)assert.ok(p.voiceTemplateId.includes(events.find(e=>e.id===p.eventId).facts.verdict));
 assert.deepEqual(renderStories(s,events,{authors:a.authors,sameWeek:{stories:a.stories,dialogueEventOrder:a.dialogueEventOrder}}).stories,a.stories);
});
test('custom conference strength follows native member prestige and suppresses ambiguous or missing grades',()=>{
 const s=fixture(),c=conferencePrestige(s);assert.equal(c[0].name,'Northern League');assert.equal(c[0].gradeLabel,'APlus');assert.ok(conferenceDiscourse(s).some(e=>e.facts.conference==='Northern League'));
 s.teams[0].conferencePrestigeGrade='F';assert.ok(!conferencePrestige(s).some(c=>c.name==='Northern League'));s.teams[0].conferencePrestigeGrade=null;assert.equal(conferenceDiscourse(s).length,0);
});
test('conference discourse stops calling postseason results standings and never prints prestige grades',()=>{
 const s=fixture();s.season.CurrentWeekType='BowlSeason2';s.season.CurrentWeek=18;const e=conferenceDiscourse(s);assert.ok(e.length);assert.ok(e.every(e=>e.category==='conference-talk'));assert.ok(!JSON.stringify(e).includes('APlus'));
});
test('dual-threat Heisman lines include both yardage sources, total touchdowns and interceptions',()=>{
 assert.equal(completeOffensiveLine('QB',{PASSYARDS:200,RUSHYARDS:100,PASSTDS:1,RUSHTDS:2,PASSINTS:1}),'200 passing yards, 100 rushing yards, 3 passing/rushing TD, 1 INT');
 assert.equal(completeOffensiveLine('HB',{RUSHYARDS:90,RECEIVEYARDS:85,RUSHTDS:1,RECEIVETDS:1}),'90 rushing yards, 85 receiving yards, 2 scrimmage TD');
});
function heismanFixture(){const s=fixture();s.performances=s.games.filter(g=>g.home===1).map(g=>({player:'p1',team:1,game:g.id,type:'GameOffensiveStats',stats:{PASSYARDS:200,RUSHYARDS:100,PASSTDS:1,RUSHTDS:1,PASSINTS:0}}));s.players[0].seasonStats=[{type:'SeasonOffensiveStats',stats:{GAMESPLAYED:3,PASSYARDS:600,RUSHYARDS:300,PASSTDS:3,RUSHTDS:3,PASSINTS:0}}];return s;}
test('Heisman full-season production corroborates game rows and latest game rather than cherry-picked big games',()=>{
 const s=heismanFixture(),a=heismanContext(s,'p1');assert.match(a.seasonLine,/600 passing yards, 300 rushing yards/);assert.equal(a.verdict,'positive');
 Object.assign(s.performances[2].stats,{PASSYARDS:120,RUSHYARDS:0,PASSINTS:3});const b=heismanContext(s,'p1');assert.equal(b.verdict,'negative');assert.match(b.recentLine,/120 passing yards/);assert.equal(b.seasonLine,null);
});
test('Heisman archives cannot leak future production, change publication or alter likes',()=>{
 const s=heismanFixture(),p={id:'h',eventId:'h',category:'heisman',body:'Old text',likes:432,publication:{week:2}},feed={phase:'RegularSeason',week:2,season:2026,key:'old',stories:[p],events:[{id:'h',playerId:'p1',facts:{school:'School 1',rank:2}}]};
 s.performances[2].stats.PASSYARDS=9999;s.players[0].seasonStats[0].stats.PASSYARDS=10399;
 const historical=heismanContext({...s,season:{...s.season,CurrentWeek:2}},'p1',{historical:true,validationSnapshot:s});assert.match(historical.seasonLine,/400 passing yards, 200 rushing yards/);
 const n=correctHeismanArchive(feed,s).stories[0];assert.ok(!n.body.includes('9999'));assert.match(n.body,/200 passing yards, 100 rushing yards/);assert.equal(n.likes,432);assert.deepEqual(n.publication,{week:2});assert.equal(correctHeismanArchive({...feed,stories:[n]},s).stories[0],n);
});
