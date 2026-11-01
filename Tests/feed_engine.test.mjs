import test from 'node:test';
import assert from 'node:assert/strict';
import {buildFeed,weekKey,trackOffers} from '../Tools/feed_engine.mjs';

function fixture(){return {format:2,gameYear:27,sourceUnchanged:true,sha256:'a'.repeat(64),source:'C:/saves/DYNASTY-TEST',leagueId:10,userTeamIndex:1,
  season:{CurrentSeasonYear:2027,CurrentYear:1,CurrentWeek:7,CurrentWeekType:'RegularSeason',CurrentStage:'NFLSeason'},
  teams:[{id:1,name:'Home',logo:11,mediaRank:6,mediaLastRank:8},{id:2,name:'Away',logo:22,mediaRank:24,mediaLastRank:20}],
  players:[{id:'p',name:'Star Player',position:'QB',team:1,overall:90,injury:'Uninjured',isNil:false,portrait:123},{id:'q',name:'Other Player',position:'QB',team:2,overall:85,injury:'Uninjured'}],
  games:[{id:'last',year:1,week:6,phase:'RegularSeason',status:'HomeWon',home:1,away:2,homeScore:32,awayScore:24,homeStats:{OFFPASSYARDS:200,OFFRUSHYARDS:120,FIRSTDOWNS:16,GIVEAWAYS:0}},
    {id:'now',year:1,week:7,phase:'RegularSeason',status:'Unplayed',home:1,away:2,homeScore:0,awayScore:0,month:10,day:31,spotlight:10},
    {id:'future',year:1,week:8,phase:'RegularSeason',status:'HomeWon',home:1,away:2,homeScore:99,awayScore:3}],
  performances:[{player:'p',team:1,game:'last',type:'GameOffensiveStats',stats:{PASSATTEMPTS:20,PASSCOMPLETED:15,PASSYARDS:200,PASSTDS:3,PASSINTS:1}}],
  heisman:[{player:'p',team:1,rank:1,lastRank:2}],commitments:[]};}
const bodies=f=>f.posts.map(p=>p.body).join('\n');
test('uses exact prior-week games and stats; excludes future, other-year and unfinished results',()=>{
  const s=fixture();s.games.push({...s.games[0],id:'old-year',year:0,homeScore:88},{...s.games[0],id:'unfinished',status:'Unplayed',homeScore:77});
  const f=buildFeed(s);assert.match(bodies(f),/Home 32, Away 24/);assert.match(bodies(f),/200 yards, 3 TD, 1 INT/);
  assert.doesNotMatch(bodies(f),/99|88|77/);assert.ok(!f.posts.some(p=>p.id.includes('future')));
  assert.match(f.posts.find(p=>p.category==='results').stamp,/Week 6/);assert.match(f.posts.find(p=>p.category==='schedule').stamp,/Week 7/);
});
test('deterministic reload, stable IDs, quotas and visible simulated-line attribution',()=>{
  const s=fixture(),a=buildFeed(s),b=buildFeed(structuredClone(s));assert.deepEqual(a,b);assert.equal(new Set(a.posts.map(p=>p.id)).size,a.posts.length);
  assert.ok(a.posts.length<=24);assert.match(a.posts.find(p=>p.category==='lines').body,/SIMULATED LINE.*Fictional estimate; not a sportsbook/);
  assert.equal(a.posts.find(p=>p.category==='player-stats').imageLibrary,0); // generated player falls back to actual team logo
});
test('week and season rollover cannot leak previous results or future stats',()=>{
  const s=fixture();s.season.CurrentWeek=0;assert.ok(!buildFeed(s).posts.some(p=>['results','player-stats'].includes(p.category)));
  s.season.CurrentWeek=7;s.season.CurrentYear=2;s.season.CurrentSeasonYear=2028;
  assert.ok(!buildFeed(s).posts.some(p=>['results','player-stats','schedule'].includes(p.category)));assert.match(weekKey(s),/2028/);
  s.season.CurrentStage='OffSeason';assert.ok(!buildFeed(s).posts.some(p=>['results','player-stats','schedule','heisman','lines'].includes(p.category)));
});
test('poll history comes from the game; no invented previous rank for new entries',()=>{
  const s=fixture();s.teams[0].mediaLastRank=0;const p=buildFeed(s).posts.find(p=>p.id==='poll:1');assert.match(p.body,/enters the Top 25/);assert.doesNotMatch(p.body,/#0/);
});
test('commitments need an observed event or verified week; old board entries are not new',()=>{
  const s=fixture();s.commitments=[{player:'q',team:1,rank:33,stage:'HardCommitted',week:2}];
  assert.match(buildFeed(s).stories.find(p=>p.category==='recruiting').body,/Commitment board check/);
  s.commitments[0].week=6;assert.match(buildFeed(s).stories.find(p=>p.category==='recruiting').body,/Commitment update/);
  s.commitments[0].week=0;const prior=fixture();prior.season.CurrentWeek=6;
  assert.match(buildFeed(s,prior).stories.find(p=>p.category==='recruiting').body,/Commitment update/);
  prior.leagueId=99;assert.match(buildFeed(s,prior).stories.find(p=>p.category==='recruiting').body,/Commitment board check/);
});
test('injury reports distinguish current status, newly sustained injury and recovery',()=>{
  const s=fixture();s.players[0].injury='Injured';s.players[0].injuryType='BrokenHand';
  assert.match(buildFeed(s).posts.find(p=>p.category==='injuries').body,/Current injury report/);
  Object.assign(s.players[0],{injuryYear:1,injuryWeek:6,injuryStage:'NFLSeason'});
  assert.match(buildFeed(s).posts.find(p=>p.category==='injuries').body,/Injury update from last week/);
  const prior=structuredClone(s);prior.season.CurrentWeek=6;s.players[0].injury='Uninjured';
  assert.match(buildFeed(s,prior).posts.find(p=>p.category==='injuries').body,/listed as uninjured/);
  prior.season.CurrentWeek=5;assert.ok(!buildFeed(s,prior).posts.some(p=>p.id.startsWith('healthy:')));
});
test('holidays follow the in-game calendar and explicit flags',()=>{
  const s=fixture();assert.match(bodies(buildFeed(s)),/Halloween/);s.games[1].day=15;
  assert.doesNotMatch(bodies(buildFeed(s)),/Halloween/);s.games[1].thanksgiving=true;
  assert.match(bodies(buildFeed(s)),/Thanksgiving/);
});
test('defensive stat lines include whole and half sacks from actual game fields',()=>{
  const s=fixture();s.performances=[{player:'p',team:1,game:'last',type:'GameDefensiveStats',stats:{DLINESACKS:2,DLINEHALFSACK:1,DSECINTS:1}}];
  assert.match(bodies(buildFeed(s)),/2.5 sacks; 1 interceptions/);
});
test('wrong game, malformed identity and missing controlled team fail closed',()=>{
  for(const mutate of [s=>s.gameYear=26,s=>s.sourceUnchanged=false,s=>s.sha256='bad',s=>s.userTeamIndex=999]){const s=fixture();mutate(s);assert.throws(()=>buildFeed(s));}
});
test('new offer uses the requested player wording and stays separate from commitments',()=>{
  const s=fixture();s.newOffers=[{player:'q',team:1}];const f=buildFeed(s),p=f.posts.find(p=>p.category==='offers');
  assert.equal(p.body,'AGTG! Blessed to receive an offer from Home');assert.equal(p.author,'Other Player');assert.equal(p.handle,'@OtherPlayer');
  assert.ok(!f.posts.some(p=>p.category==='recruiting'));delete s.newOffers;assert.ok(!buildFeed(s).posts.some(p=>p.category==='offers'));
});
test('offer observation seeds quietly, preserves same-week news, and handles reloads and rollbacks',()=>{
  const s=fixture();s.offers=[{player:'p',team:1}];assert.deepEqual(trackOffers(s),[]);
  const old=structuredClone(s);s.offers.push({player:'q',team:1});
  const events=trackOffers(s,old);assert.deepEqual(events,[{player:'q',team:1}]);
  const current={...structuredClone(s),offerEvents:events};assert.deepEqual(trackOffers(s,current),events);
  const next=structuredClone(s);next.season.CurrentWeek=8;assert.deepEqual(trackOffers(next,null,current),[]);
  assert.deepEqual(trackOffers(old,current),[]); // later observed offer is absent after rewind
  const unrelated=structuredClone(old);unrelated.leagueId=20;assert.deepEqual(trackOffers(s,unrelated),[]);
});
