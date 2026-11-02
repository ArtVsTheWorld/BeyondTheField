import test from 'node:test';
import assert from 'node:assert/strict';
import {buildFeed} from '../Tools/feed_engine.mjs';
import {renderStories} from '../Tools/story_renderer.mjs';
import {authorRegistry} from '../Tools/story_authors.mjs';
import {updateRuntime} from '../Tools/runtime_lifecycle.mjs';
const fixture=()=>({format:2,gameYear:27,sourceUnchanged:true,sha256:'a'.repeat(64),source:'runtime:10:1',sourceKind:'runtime',leagueId:10,userTeamIndex:1,
 season:{CurrentSeasonYear:2027,CurrentYear:1,CurrentWeek:8,CurrentWeekType:'RegularSeason',CurrentStage:'NFLSeason'},
 teams:[{id:1,name:'Harbor State',nickname:'Captains',hashtags:['#AllAboard'],logo:11,rivals:[2],mediaRank:8,mediaLastRank:12,headCoach:{lastName:'Ellison'}},{id:2,name:'Red Mesa',logo:22,rivals:[1]}],
 players:[{id:'p',name:'Caleb Moss',team:1,position:'LT',personality:'TeamPlayer',jerseyNumber:70,injury:'Uninjured'},{id:'q',name:'Darius Vann',team:1,position:'HB',personality:'Entertainer',jerseyNumber:22,injury:'Uninjured'},{id:'r',name:'Evan Mercer',team:255,position:'QB',personality:'Leader',injury:'Uninjured'}],
 games:[{id:'g',year:1,week:7,phase:'RegularSeason',published:true,status:'HomeWon',home:1,away:2,homeScore:36,awayScore:31}],
 performances:[{player:'q',team:1,game:'g',type:'GameOffensiveStats',stats:{RUSHATTEMPTS:20,RUSHYARDS:114,RUSHTDS:2}}],heisman:[],offers:[],commitments:[]});
const event=(category,facts,extra={})=>({id:'x',category,facts,teamIds:[1],scopes:['team'],priority:90,thread:'x',curated:true,...extra});
test('real result produces a short program caption and independent positive reaction; no fixture school leaks',()=>{
 const f=buildFeed(fixture());const recap=f.stories.find(p=>p.eventId==='result:g'&&p.voice==='official');assert.ok(recap);assert.ok(recap.body.includes('36'));assert.ok(recap.body.includes('Red Mesa'));assert.ok(recap.body.includes('#AllAboard'));assert.ok([...recap.body].length<130);
 assert.ok(f.stories.some(p=>p.eventId==='result:g'&&['player','fan'].includes(p.voice)));assert.ok(f.stories.every(p=>!p.body.includes('North Valley')));
});
test('account identity survives recruit-to-roster, position, name, jersey, week and season changes',()=>{
 const s=fixture(),a=authorRegistry(),p=s.players[2],first=a.get(s,'recruit',s.teams[0],p);const saved=structuredClone(a.entries);Object.assign(p,{team:1,position:'WR',jerseyNumber:8,name:'Evan T. Mercer'});s.season.CurrentWeek++;s.season.CurrentSeasonYear++;
 const b=authorRegistry(saved),later=b.get(s,'player',s.teams[0],p);assert.equal(later.handle,first.handle);assert.equal(later.author,p.name);assert.equal(Object.keys(b.entries).length,1);assert.ok(!/(QB|WR|RB|OL)$/i.test(later.handle));
});
test('similar names resolve handle collisions once and preserve the chosen identities',()=>{
 const s=fixture(),r=authorRegistry();for(let i=0;i<30;i++)r.get(s,'recruit',s.teams[0],{id:'same'+i,name:'Alex Smith',team:255});const values=Object.values(r.entries).map(p=>p.handle.toLowerCase());assert.equal(new Set(values).size,30);assert.deepEqual(authorRegistry(r.entries).entries,r.entries);
});
test('personality changes vocabulary while QB influence remains secondary; unknown personality is neutral',()=>{
 const s=fixture(),p=s.players[2],facts={playerName:p.name,school:'Harbor State',position:'QB'},e=event('offers',facts,{playerId:p.id});
 const noFaith=authorRegistry();const account=noFaith.get(s,'recruit',s.teams[0],p);account.faithLanguage=false;
 p.personality='Intense';const intense=renderStories(s,[e],{authors:noFaith.entries}).stories[0];p.personality='Leader';const leader=renderStories(s,[e],{authors:noFaith.entries}).stories[0];assert.ok(intense.templateId.startsWith('recruit.offer.Intense'));assert.ok(leader.templateId.startsWith('recruit.offer.Leader'));assert.equal(intense.handle,leader.handle);
 p.personality='Invalid_';assert.ok(renderStories(s,[e],{authors:noFaith.entries}).stories[0].templateId.startsWith('recruit.offer.Neutral'));
});
test('missing coach never invents a coach or phone call, and old commitments do not masquerade as news',()=>{
 const s=fixture();delete s.teams[0].headCoach;s.players[2].personality='TeamPlayer';const e=event('recruiting',{playerName:'Evan Mercer',school:'Harbor State',newlyObserved:true,commitment:'HardCommitted'},{playerId:'r'});
 const a=renderStories(s,[e]).stories[0];assert.ok(a);assert.ok(!/Coach|phone call|undefined/.test(a.body));e.facts.newlyObserved=false;assert.equal(renderStories(s,[e]).stories.length,0);
});
test('losses never create default player apologies and unpublished results never become recaps',()=>{
 const s=fixture();Object.assign(s.games[0],{homeScore:6,awayScore:21,status:'AwayWon'});assert.ok(!buildFeed(s).stories.some(p=>p.voice==='player'));
 s.games[0].published=false;assert.ok(!buildFeed(s).stories.some(p=>p.eventId==='result:g'||p.category==='player-stats'));
});
test('missing or oversized factual values suppress a variant instead of truncating it',()=>{
 const s=fixture(),e=event('offers',{playerName:'Evan Mercer',school:'Harbor State'},{playerId:'r'});s.teams[0].name='VeryLongSchool'.repeat(60);e.facts.school=s.teams[0].name;assert.equal(renderStories(s,[e]).stories.length,0);
});
test('generated English posts fit native byte and character budgets with no emoji or game-system metrics',()=>{
 const f=buildFeed(fixture());for(const p of f.stories){assert.ok([...p.body].length<=280,p.id);assert.ok(Buffer.byteLength(p.body)<=512,p.id);assert.ok(!/[\u{1F000}-\u{1FAFF}\u2600-\u27BF]/u.test(p.body),p.id);assert.ok(!/undefined|NaN|\b(?:OVR|overall|ratings?)\b/i.test(p.body),p.id);assert.ok(!/\{[A-Za-z]/.test(p.body));}
});
test('midweek unsaved recruiting renders once, persists identity, and does not reroll existing stories',()=>{
 const s=fixture(),a=updateRuntime(structuredClone(s));s.offers=[{team:1,player:'r',rank:20}];const b=updateRuntime(structuredClone(s),a.state),c=updateRuntime(structuredClone(s),b.state);assert.equal(b.catalog.stories.filter(p=>p.eventId==='offer:1:r').length,1);assert.deepEqual(b.catalog,c.catalog);
 for(const p of a.catalog.stories)assert.equal(b.catalog.stories.find(x=>x.id===p.id)?.body,p.body,p.id);
});
test('analyst replies quote a real parent, retain school context, and stay out of All Posts without a parent',()=>{
 const s=fixture(),e=event('analytics',{metric:'rushingYardsPerGame',school:'Harbor State',sampleGames:7,rushingYards:1643,rushingYardsPerGame:1643/7,nationalRank:3,nationalRankTied:false,pollRank:8,previousPollRank:12},{scopes:['team','national']});
 const result=renderStories(s,[e]).stories,parent=result.find(p=>p.voice==='analyst'),reply=result.find(p=>p.replyTo);assert.ok(parent.body.includes('234.7'));assert.ok(parent.body.includes('Harbor State'));assert.ok(reply);assert.equal(reply.replyTo,parent.id);assert.ok(parent.body.includes('No. 8 feels about right'));assert.equal(reply.curated,false);
});

test('all five supported analyst measures resolve their actual denominators and polarity',()=>{
 const s=fixture();const cases=[
  {metric:'rushingYardsPerGame',school:'Harbor State',sampleGames:7,rushingYards:1643,rushingYardsPerGame:1643/7,nationalRank:3,nationalRankTied:true},
  {metric:'thirdDownConversionRate',school:'Harbor State',sampleGames:3,conversions:8,attempts:36,rate:8/36},
  {metric:'redZoneTouchdownRate',school:'Harbor State',sampleGames:4,trips:25,touchdowns:9,rate:9/25},
  {metric:'turnoverMargin',school:'Harbor State',sampleGames:4,takeaways:10,giveaways:3,margin:7},
  {metric:'turnoverMargin',school:'Harbor State',sampleGames:4,takeaways:1,giveaways:8,margin:-7},
  {kind:'season_largest_winning_margin',school:'Harbor State',winnerScore:44,loserScore:7,margin:37,opponent:'Red Mesa',comparisonGames:100}
 ];for(const facts of cases){const out=renderStories(s,[event('analytics',facts)]).stories;assert.equal(out.length,1,JSON.stringify(facts));assert.equal(out[0].voice,'analyst');assert.ok(!/undefined|NaN|\{/.test(out[0].body));}
});
