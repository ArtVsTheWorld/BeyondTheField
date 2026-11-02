import test from 'node:test';
import assert from 'node:assert/strict';
import {publicPoll} from '../Tools/public_polls.mjs';
import {updateRuntime} from '../Tools/runtime_lifecycle.mjs';
import {worldEvents} from '../Tools/world_events.mjs';
const fixture=()=>({format:2,gameYear:27,sourceKind:'runtime',source:'runtime:polls',sourceUnchanged:true,sha256:'a'.repeat(64),leagueId:8,userTeamIndex:0,
 season:{CurrentYear:0,CurrentSeasonYear:2026,CurrentWeek:9,CurrentWeekType:'RegularSeason',CurrentStage:'NFLSeason'},
 teams:Array.from({length:26},(_,id)=>({id,name:'School '+id,mediaRank:id<25?25-id:99,mediaLastRank:id<25?25-id:99,cfpRank:id<25?id+1:99,cfpLastRank:99,rank:26-id,coachesRank:1})),players:[],games:[],performances:[],offers:[],commitments:[],heisman:[],conferences:[]});
test('AP remains public before Week 10 and until a complete native CFP Top 25 exists',()=>{
 const s=fixture();s.season.CurrentStage='PreSeason';s.season.CurrentWeekType='PreSeason';assert.equal(publicPoll(s).key,'ap');
 s.season.CurrentStage='NFLSeason';s.season.CurrentWeekType='RegularSeason';s.teams[24].cfpRank=null;s.season.CurrentWeek=15;assert.equal(publicPoll(s).key,'ap');
 s.teams[24].cfpRank=24;assert.equal(publicPoll(s).key,'ap');s.teams[24].cfpRank=25;s.season.CurrentWeek=8;assert.equal(publicPoll(s).key,'ap');s.season.CurrentWeek=10;assert.equal(publicPoll(s).key,'cfp');
});
test('the first CFP publication never reports AP-to-CFP differences as weekly movement',()=>{
 const s=fixture();s.teams[24].cfpRank=null;const ap=updateRuntime(structuredClone(s));s.teams[24].cfpRank=25;s.season.CurrentWeek++;
 // Even seeded last-CFP fields cannot override an observed AP edition.
 for(const t of s.teams)t.cfpLastRank=t.cfpRank;
 const cfp=updateRuntime(structuredClone(s),ap.state),story=cfp.catalog.events.find(e=>e.id==='poll:0');
 assert.equal(story.facts.rank,1);assert.equal(story.facts.previousRank,null);assert.equal(story.facts.family,'poll.initial.beat');assert.ok(cfp.catalog.stories.some(p=>p.eventId==='poll:0'&&p.body.includes('CFP')));
 s.season.CurrentWeek++;const next=updateRuntime(s,cfp.state);assert.equal(next.catalog.events.find(e=>e.id==='poll:0').facts.previousRank,1);
});
test('pregame ranks retain their actual public-poll basis after the primary poll changes',()=>{
 const s=fixture();s.teams[24].cfpRank=null;s.games=[{id:'g',year:0,phase:'RegularSeason',week:9,status:'Unplayed',home:0,away:25}];const a=updateRuntime(structuredClone(s));assert.equal(a.state.editions[0].snapshot.pregameGames.g.poll,'ap');
 s.teams[24].cfpRank=25;s.season.CurrentWeek=10;Object.assign(s.games[0],{status:'AwayWon',homeScore:10,awayScore:20});const b=updateRuntime(s,a.state);
 const upset=b.catalog.events.find(e=>e.category==='upsets');assert.equal(upset.facts.loserRank,25);assert.equal(upset.facts.huge,false); // CFP No.1 must not leak backward into the pregame AP basis.
});
test('unpublished CFP and hidden Rank cannot create playoff news or change public ranks',()=>{
 const s=fixture();s.teams[24].cfpRank=null;const f=updateRuntime(s);assert.ok(!f.catalog.events.some(e=>e.category==='cfp'));assert.equal(f.catalog.events.find(e=>e.id==='poll:0').facts.rank,25);assert.equal(f.catalog.events.find(e=>e.id==='poll:0').facts.pollName,'AP poll');
 const w=fixture();w.season.CurrentWeek=10;w.games=[{id:'x',year:0,phase:'RegularSeason',week:9,status:'AwayWon',home:0,away:25,homeScore:3,awayScore:20}];assert.ok(!worldEvents(w).some(e=>e.category==='upsets'));
});
