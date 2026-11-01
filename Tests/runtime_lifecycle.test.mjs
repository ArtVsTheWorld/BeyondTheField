import test from 'node:test';
import assert from 'node:assert/strict';
import {updateRuntime} from '../Tools/runtime_lifecycle.mjs';
function savedFixture(){return {format:2,gameYear:27,sourceUnchanged:true,sha256:'a'.repeat(64),source:'C:/saves/DYNASTY-TEST',leagueId:10,userTeamIndex:1,
  season:{CurrentSeasonYear:2027,CurrentYear:1,CurrentWeek:7,CurrentWeekType:'RegularSeason',CurrentStage:'NFLSeason'},
  teams:[{id:1,name:'Home',logo:11,mediaRank:6,mediaLastRank:8},{id:2,name:'Away',logo:22,mediaRank:24,mediaLastRank:20}],
  players:[{id:'p',name:'Star Player',position:'QB',team:1,overall:90,injury:'Uninjured',isNil:false,portrait:123},{id:'q',name:'Other Player',position:'QB',team:2,overall:85,injury:'Uninjured'}],
  games:[{id:'last',year:1,week:6,phase:'RegularSeason',status:'HomeWon',home:1,away:2,homeScore:32,awayScore:24,homeStats:{OFFPASSYARDS:200,OFFRUSHYARDS:120,FIRSTDOWNS:16,GIVEAWAYS:0}},
    {id:'now',year:1,week:7,phase:'RegularSeason',status:'Unplayed',home:1,away:2,homeScore:0,awayScore:0,month:10,day:31,spotlight:10},
    {id:'future',year:1,week:8,phase:'RegularSeason',status:'HomeWon',home:1,away:2,homeScore:99,awayScore:3}],
  performances:[{player:'p',team:1,game:'last',type:'GameOffensiveStats',stats:{PASSATTEMPTS:20,PASSCOMPLETED:15,PASSYARDS:200,PASSTDS:3,PASSINTS:1}}],
  heisman:[{player:'p',team:1,rank:1,lastRank:2}],commitments:[]};}

function fixture(){const s=savedFixture();s.source='runtime:10:1';s.sourceKind='runtime';s.offers=[];return s;}
const ids=f=>f.catalog.events.map(p=>p.id);
test('runtime first observation seeds recruiting quietly and reloads deterministically',()=>{
  const s=fixture();s.offers=[{player:'q',team:1,rank:10}];
  const a=updateRuntime(structuredClone(s)),b=updateRuntime(structuredClone(s),a.state);
  assert.ok(!ids(a).some(id=>id.startsWith('offer:')));assert.deepEqual(a.catalog,b.catalog);
});
test('an unsaved midweek offer and commitment appear once in the current publication week',()=>{
  const s=fixture(),a=updateRuntime(structuredClone(s));s.offers.push({player:'q',team:1,rank:10});s.commitments.push({player:'q',team:1,rank:10,stage:'HardCommitted',week:0});
  const b=updateRuntime(structuredClone(s),a.state),c=updateRuntime(structuredClone(s),b.state);
  assert.equal(b.catalog.week,7);assert.equal(b.catalog.weeks.length,1);assert.equal(ids(b).filter(id=>id==='offer:1:q').length,1);
  assert.equal(b.catalog.events.find(p=>p.id==='commit:1:q').facts.newlyObserved,true);assert.deepEqual(b.catalog,c.catalog);
});
test('midweek game completion replaces its preview and publishes current-week performance accurately',()=>{
  const s=fixture(),a=updateRuntime(structuredClone(s));Object.assign(s.games[1],{status:'HomeWon',homeScore:21,awayScore:6});
  s.performances.push({player:'p',team:1,game:'now',type:'GameOffensiveStats',stats:{PASSATTEMPTS:30,PASSCOMPLETED:20,PASSYARDS:310,PASSTDS:3,PASSINTS:0}});
  const b=updateRuntime(s,a.state);assert.ok(!ids(b).includes('preview:now'));const recap=b.catalog.events.find(p=>p.id==='result:now');
  assert.equal(recap.facts.homeScore,21);assert.equal(recap.facts.awayScore,6);assert.equal(recap.publication.week,7);assert.equal(recap.eventWeek,7);
  assert.equal(b.catalog.events.find(p=>p.id==='performance:now:p:GameOffensiveStats').facts.stats.passingYards,310);
});
test('native week advance creates the next edition and preserves the prior edition',()=>{
  const s=fixture(),a=updateRuntime(structuredClone(s));s.season.CurrentWeek=8;
  const b=updateRuntime(s,a.state);assert.equal(b.catalog.week,8);assert.deepEqual(b.catalog.weeks.map(e=>e.week),[7,8]);assert.deepEqual(b.catalog.weeks[0],a.catalog.weeks[0]);
});
test('loading an earlier week removes future editions and replaying can publish different facts',()=>{
  const s=fixture(),a=updateRuntime(structuredClone(s));s.season.CurrentWeek=8;const b=updateRuntime(structuredClone(s),a.state);
  s.season.CurrentWeek=7;const c=updateRuntime(structuredClone(s),b.state);assert.deepEqual(c.catalog.weeks.map(e=>e.week),[7]);
  s.season.CurrentWeek=8;s.games[1].status='HomeWon';s.games[1].homeScore=42;s.games[1].awayScore=3;const d=updateRuntime(s,c.state);
  assert.equal(d.catalog.events.find(p=>p.id==='result:now').facts.homeScore,42);assert.notDeepEqual(d.catalog.events.find(p=>p.id==='result:now').facts,b.catalog.events.find(p=>p.id==='result:now')?.facts);
});
test('same-week rollback cannot retain an absent offer or commitment event',()=>{
  const s=fixture(),a=updateRuntime(structuredClone(s)),changed=structuredClone(s);changed.offers=[{player:'q',team:1}];changed.commitments=[{player:'q',team:1,stage:'HardCommitted',rank:10,week:0}];
  const b=updateRuntime(changed,a.state),c=updateRuntime(s,b.state);assert.ok(!ids(c).includes('offer:1:q'));assert.ok(!ids(c).includes('commit:1:q'));
});
test('midweek injury recovery is detected without a week advance',()=>{
  const s=fixture();s.players[0].injury='Injured';const a=updateRuntime(structuredClone(s));s.players[0].injury='Uninjured';
  const b=updateRuntime(s,a.state);assert.ok(ids(b).includes('healthy:p'));assert.equal(b.catalog.week,7);
});
test('league, team, phase, and year changes isolate publication history',()=>{
  const a=updateRuntime(fixture());for(const change of [s=>s.leagueId=20,s=>s.userTeamIndex=2,s=>s.season.CurrentWeekType='PreSeason',s=>s.season.CurrentSeasonYear=2028]){
    const s=fixture();change(s);const b=updateRuntime(s,a.state);assert.equal(b.catalog.weeks.length,1);assert.equal(b.state.editions.length,1);
  }
});

test('an injury sustained and recovered midweek retains its recovery event, but a pre-injury restore does not',()=>{
  const clean=fixture(),a=updateRuntime(structuredClone(clean)),hurt=structuredClone(clean);
  Object.assign(hurt.players[0],{injury:'Injured',injuryType:'BrokenHand',injuryWeek:7,injuryYear:1});
  const b=updateRuntime(structuredClone(hurt),a.state);hurt.players[0].injury='Uninjured';
  const c=updateRuntime(structuredClone(hurt),b.state),d=updateRuntime(structuredClone(hurt),c.state);assert.ok(ids(c).includes('healthy:p'));assert.ok(ids(d).includes('healthy:p'));
  const restored=updateRuntime(clean,d.state);assert.ok(!ids(restored).includes('healthy:p'));
});
