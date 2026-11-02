import test from 'node:test';
import assert from 'node:assert/strict';
import {buildFeed,detectEvents,weekKey,trackOffers} from '../Tools/feed_engine.mjs';
function fixture(){return {format:2,gameYear:27,sourceUnchanged:true,sha256:'a'.repeat(64),source:'C:/saves/DYNASTY-TEST',leagueId:10,userTeamIndex:1,
  season:{CurrentSeasonYear:2027,CurrentYear:1,CurrentWeek:7,CurrentWeekType:'RegularSeason',CurrentStage:'NFLSeason'},
  teams:[{id:1,name:'Home',logo:11,mediaRank:6,mediaLastRank:8},{id:2,name:'Away',logo:22,mediaRank:24,mediaLastRank:20}],
  players:[{id:'p',name:'Star Player',position:'QB',team:1,overall:90,injury:'Uninjured',isNil:false,portrait:123},{id:'q',name:'Other Player',position:'QB',team:2,overall:85,injury:'Uninjured'}],
  games:[{id:'last',year:1,week:6,phase:'RegularSeason',status:'HomeWon',home:1,away:2,homeScore:32,awayScore:24,homeStats:{OFFPASSYARDS:200,OFFRUSHYARDS:120,FIRSTDOWNS:16,GIVEAWAYS:0}},
    {id:'now',year:1,week:7,phase:'RegularSeason',status:'Unplayed',home:1,away:2,homeScore:0,awayScore:0,month:10,day:31,spotlight:10},
    {id:'future',year:1,week:8,phase:'RegularSeason',status:'HomeWon',home:1,away:2,homeScore:99,awayScore:3}],
  performances:[{player:'p',team:1,game:'last',type:'GameOffensiveStats',stats:{PASSATTEMPTS:20,PASSCOMPLETED:15,PASSYARDS:200,PASSTDS:3,PASSINTS:1}}],
  heisman:[{player:'p',team:1,rank:1,lastRank:2}],commitments:[]};}

const find=(s,id,previous)=>detectEvents(s,previous).find(e=>e.id===id);
test('event detection retains verified prior-week results and performances without authored prose',()=>{
 const s=fixture();s.games.push({...s.games[0],id:'old-year',year:0,homeScore:88},{...s.games[0],id:'unfinished',status:'Unplayed',homeScore:77});
 const e=detectEvents(s);assert.equal(find(s,'result:last').facts.homeScore,32);assert.equal(find(s,'performance:last:p:GameOffensiveStats').facts.stats.passingYards,200);
 assert.ok(!e.some(e=>e.id.includes('future')||e.id.includes('old-year')||e.id.includes('unfinished')));assert.ok(e.every(e=>!('body' in e)&&!('author' in e)));
});
test('approved pack generates deterministic stories from retained event facts',()=>{
 const s=fixture(),a=buildFeed(s),b=buildFeed(structuredClone(s));assert.deepEqual(a,b);assert.equal(a.contentStatus,'generated');assert.ok(a.events.length>0);assert.ok(a.stories.length>0);
 assert.ok(a.stories.every(p=>p.templateId&&p.contentRevision===a.contentRevision));assert.ok(a.posts.length<=30);assert.ok(a.stories.every(p=>p.publication.week===7));
 assert.ok(a.events.every(e=>e.publication.week===7));assert.equal(new Set(a.events.map(e=>e.id)).size,a.events.length);
});
test('week, phase, and season boundaries reject unrelated results',()=>{
 const s=fixture();s.season.CurrentWeek=0;assert.ok(!detectEvents(s).some(e=>['results','player-stats'].includes(e.category)));
 s.season.CurrentSeasonYear=2028;s.season.CurrentYear=2;s.season.CurrentWeek=7;assert.ok(!detectEvents(s).some(e=>['results','player-stats','schedule'].includes(e.category)));assert.match(weekKey(s),/2028/);
 s.season.CurrentStage='OffSeason';assert.ok(!detectEvents(s).some(e=>['results','player-stats','schedule','heisman','lines'].includes(e.category)));
});
test('poll facts distinguish entry from a verified previous rank',()=>{
 const s=fixture();s.teams[0].mediaLastRank=0;const p=find(s,'poll:1');assert.equal(p.facts.movement,'entry');assert.equal(p.facts.previousRank,null);
});
test('commitment detection retains board checks separately from newly observed events',()=>{
 const s=fixture();s.commitments=[{player:'q',team:1,rank:33,stage:'HardCommitted',week:2}];assert.equal(find(s,'commit:1:q').facts.newlyObserved,false);
 s.commitments[0].week=6;assert.equal(find(s,'commit:1:q').facts.newlyObserved,true);
 s.commitments[0].week=0;const prior=fixture();prior.season.CurrentWeek=6;assert.equal(find(s,'commit:1:q',prior).facts.newlyObserved,true);
 prior.leagueId=99;assert.equal(find(s,'commit:1:q',prior).facts.newlyObserved,false);
});
test('injury facts distinguish new status and recovery without inventing unavailable details',()=>{
 const s=fixture();Object.assign(s.players[0],{injury:'Injured',injuryType:'Invalid_'});assert.equal(find(s,'injury:p').facts.newlyInjured,false);assert.equal(find(s,'injury:p').facts.injuryType,null);
 Object.assign(s.players[0],{injuryYear:1,injuryWeek:6,injuryStage:'NFLSeason'});assert.equal(find(s,'injury:p').facts.newlyInjured,true);
 const prior=structuredClone(s);prior.season.CurrentWeek=6;s.players[0].injury='Uninjured';assert.equal(find(s,'healthy:p',prior).facts.recovered,true);prior.season.CurrentWeek=5;assert.equal(find(s,'healthy:p',prior),undefined);
});
test('calendar events use game dates and flags',()=>{
 const s=fixture();assert.equal(find(s,'holiday:halloween').facts.holiday,'Halloween');s.games[1].day=15;assert.equal(find(s,'holiday:halloween'),undefined);
 s.games[1].thanksgiving=true;assert.equal(find(s,'holiday:thanksgiving').facts.holiday,'Thanksgiving');
});
test('defensive performance facts include half sacks',()=>{
 const s=fixture();s.performances=[{player:'p',team:1,game:'last',type:'GameDefensiveStats',stats:{DLINESACKS:2,DLINEHALFSACK:1,DSECINTS:1}}];
 assert.equal(find(s,'performance:last:p:GameDefensiveStats').facts.stats.sacks,2.5);
});
test('invalid Dynasty snapshots fail closed',()=>{
 for(const mutate of [s=>s.gameYear=26,s=>s.sourceUnchanged=false,s=>s.sha256='bad',s=>s.userTeamIndex=999]){const s=fixture();mutate(s);assert.throws(()=>buildFeed(s));}
});
test('new offers retain identity and native personality without an old tweet template',()=>{
 const s=fixture();s.players[1].personality='Intense';s.newOffers=[{player:'q',team:1}];const e=find(s,'offer:1:q');
 assert.equal(e.facts.school,'Home');assert.equal(e.facts.playerName,'Other Player');assert.equal(e.personality,'Intense');assert.equal(e.position,'QB');assert.equal(e.body,undefined);
 assert.ok(!detectEvents(s).some(e=>e.category==='recruiting'));delete s.newOffers;assert.equal(find(s,'offer:1:q'),undefined);
});
test('offer observation seeds quietly and retains same-week news without duplicates',()=>{
 const s=fixture();s.offers=[{player:'q',team:1}];assert.deepEqual(trackOffers(s),[]);
 const same=structuredClone(s);same.offers=[];const news=trackOffers(s,same);assert.equal(news.length,1);same.offers=s.offers;same.offerEvents=news;assert.equal(trackOffers(s,same).length,1);
 s.offers=[];assert.deepEqual(trackOffers(s,same),[]);
 const prior=fixture();prior.season.CurrentWeek=6;prior.offers=[];s.offers=[{player:'q',team:1}];assert.equal(trackOffers(s,null,prior).length,1);prior.leagueId=99;assert.deepEqual(trackOffers(s,null,prior),[]);
});
test('current-week team and player facts retain their actual event week',()=>{
 const s=fixture();Object.assign(s.games[1],{status:'HomeWon',homeScore:21,awayScore:6,homeStats:s.games[0].homeStats});
 s.performances.push({...s.performances[0],game:'now'});for(const id of ['result:now','teamstats:now:1','performance:now:p:GameOffensiveStats'])assert.equal(find(s,id).eventWeek,7);
});
test('spotlight facts use demonstrated performance rather than ability labels',()=>{
 const s=fixture();const p=find(s,'watch:now:p');assert.equal(p.facts.basis,'recentPerformance');assert.ok(!('overall' in p.facts));assert.ok(!('rating' in p.facts));
 s.performances=[];s.heisman=[];assert.ok(!detectEvents(s).some(e=>e.category==='watch'));
});
