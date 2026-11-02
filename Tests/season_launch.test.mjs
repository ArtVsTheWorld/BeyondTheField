import test from 'node:test';import assert from 'node:assert/strict';
import {seasonLaunchEvents} from '../Tools/season_launch_events.mjs';import {buildFeed} from '../Tools/feed_engine.mjs';import {authorRegistry} from '../Tools/story_authors.mjs';import {avatarFor} from '../Tools/story_avatars.mjs';
const fixture=()=>({format:2,gameYear:27,sourceKind:'runtime',sourceUnchanged:true,sha256:'a'.repeat(64),leagueId:8,userTeamIndex:1,season:{CurrentSeasonYear:2026,CurrentYear:0,CurrentWeek:0,CurrentWeekType:'PreSeason',CurrentStage:'PreSeason'},teams:[{id:1,name:'Home',nickname:'Captains',logo:11,stadium:'Harbor Stadium',headCoach:{name:'Alex Jones',seasonsWithTeam:0,style:'Recruiter'},depthChart:{QB:['a','b']},mediaRank:8},{id:2,name:'Away',logo:22}],players:[{id:'a',name:'A Player',team:1,position:'QB',classYear:'Senior',redshirt:'Previous',overall:88,injury:'Uninjured',nil:30},{id:'b',name:'B Player',team:1,position:'QB',classYear:'Freshman',redshirt:'Eligible',overall:85,injury:'Uninjured'},{id:'r',name:'A Recruit',team:255,position:'QB',starRating:5}],games:[{id:'g',year:0,week:0,phase:'RegularSeason',home:1,away:2,status:'Unplayed',neutral:false}],performances:[],heisman:[],offers:[],commitments:[],preseasonHonors:[],recruitStatuses:[{player:'r',stage:'Top3',nationalRank:1,topSchools:[1,2]}]});
test('real top-two depth chart, class and staff facts drive launch stories without revealing ratings',()=>{
 const s=fixture(),e=seasonLaunchEvents(s);for(const key of ['battle','new_coach','recruiter','freshman','breakout','senior','nil'])assert.ok(e.some(x=>x.facts.family==='launch.'+key),key);
 const f=buildFeed(s);assert.ok(f.stories.some(p=>p.body.includes('Alex Jones')));assert.ok(f.stories.every(p=>! /\bOVR\b|\boverall\b|skill tree|undefined|NaN/i.test(p.body)));
 s.players[1].overall=84;assert.ok(!seasonLaunchEvents(s).some(e=>e.facts.family==='launch.battle'));s.players[1].overall=85;s.teams[0].depthChart.QB.reverse();assert.equal(seasonLaunchEvents(s).find(e=>e.facts.family==='launch.battle').facts.first,'B Player');
 s.players[1].redshirt='Previous';assert.ok(!seasonLaunchEvents(s).some(e=>e.facts.family==='launch.freshman'));
});
test('zero years with team cannot invent a transfer; missing prior-year records cannot invent a rebuild or championship',()=>{
 const s=fixture();s.players.forEach(p=>p.yearsWithTeam=0);assert.ok(!seasonLaunchEvents(s).some(e=>/transfer|rebuild|champion|return$/.test(e.facts.family)));
 s.teams[0].previousSeason={wins:2,losses:10};assert.ok(seasonLaunchEvents(s).some(e=>e.facts.family==='launch.rebuild'));
 s.teams[0].previousSeason={wins:15,losses:0,playoffRound:'WonNationalChampionship'};assert.ok(seasonLaunchEvents(s).some(e=>e.facts.family==='launch.champion'));
 s.players[0].previousSeasonStats=[{stats:{YEARBYYEARTEAMINDEX:2,PASSYARDS:2000}}];assert.ok(seasonLaunchEvents(s).some(e=>e.facts.family==='launch.transfer'&&e.facts.formerSchool==='Away'));
});
test('opening week uses genuine venues, current depth order, recruit top-three schools and existing player handles',()=>{
 const s=fixture();s.season.CurrentWeekType='RegularSeason';s.season.CurrentStage='NFLSeason';const f=buildFeed(s);
 for(const family of ['launch.venue','launch.depth','launch.recruit_watch','launch.recruit_tag','launch.high_school','launch.coach_debut'])assert.ok(f.stories.some(p=>p.templateId.startsWith(family)),family);
 const tagged=f.stories.find(p=>p.templateId.startsWith('launch.recruit_tag'));assert.ok(tagged.body.includes('@'));assert.ok(f.stories.filter(p=>p.voice==='recruit').every(p=>p.author.endsWith(' | QB')));
 assert.ok(f.stories.some(p=>p.body.includes('Harbor Stadium')));s.games[0].neutral=true;assert.ok(!seasonLaunchEvents(s).some(e=>e.facts.family==='launch.venue'));
});
test('opening overreactions require a published final and stop after Week 1',()=>{
 const s=fixture();Object.assign(s.season,{CurrentStage:'NFLSeason',CurrentWeekType:'RegularSeason',CurrentWeek:1});Object.assign(s.games[0],{status:'HomeWon',published:true,homeScore:42,awayScore:7});assert.ok(seasonLaunchEvents(s).some(e=>e.facts.family==='launch.dominant_debut'));
 s.games[0].published=false;assert.ok(!seasonLaunchEvents(s).some(e=>e.facts.family==='launch.dominant_debut'));s.games[0].published=true;s.season.CurrentWeek=2;assert.deepEqual(seasonLaunchEvents(s),[]);
});
test('brand migration keeps personal handles, adds recruit display position, and fixes static national identities',()=>{
 const s=fixture(),r=authorRegistry(),p=s.players[2],original=r.get(s,'recruit',s.teams[0],p),handle=original.handle,saved=structuredClone(r.entries);assert.ok(original.author.endsWith(' | QB'));
 const b=authorRegistry(saved);p.position='WR';assert.equal(b.get(s,'recruit',s.teams[0],p).handle,handle);assert.ok(b.get(s,'recruit',s.teams[0],p).author.endsWith(' | WR'));p.team=1;assert.equal(b.get(s,'player',s.teams[0],p).author,p.name);assert.equal(b.get(s,'player',s.teams[0],p).handle,handle);
 assert.deepEqual([0,1,2,3,4,5].map(i=>b.get(s,'analyst',null,null,i).handle),['@ESPNCFB','@JakeWhitmoreCFB','@MBennettSports','@TinaBrooksCFB','@DavidEllisonFB','@ChrisMaddoxCFB']);assert.equal(b.get(s,'model').author,'FanDuel Sports');assert.equal(b.get(s,'fan',s.teams[0],null,1).author,'Barstool Home');
});
test('exact on-white and secondary assets are used for ordinary schools; TeamBuilder retains its custom primary logo',()=>{
 const t={id:1,logo:1};assert.deepEqual(avatarFor('official',t),{imageLibrary:64,imageValue:1});assert.deepEqual(avatarFor('fan',t,null,1),{imageLibrary:89,imageValue:1});assert.deepEqual(avatarFor('official',{...t,isTeamBuilder:true,logo:600}),{imageLibrary:0,imageValue:600});assert.deepEqual(avatarFor('model'),{imageLibrary:79,imageValue:1053});
});
