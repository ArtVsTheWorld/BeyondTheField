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
 add('player','Player',{FirstName:'Fixture',LastName:'Recruit',TeamIndex:255,Position:'QB',InjuryStatus:'Uninjured',IsNIL:false});
 add('recruit','Recruit',{Player:'player',RecruitStage:'Top10',NationalRank:50});
 add('board','RecruitingBoard',{Recruits:'targets'});add('targets','UserRecruitTarget[]',{Member0:'target'});
 add('target','UserRecruitTarget',{Recruit:'recruit',ScholarshipStatus:status,CommittedWeekNumber:0});
 return {format:1,sourceKind:'runtime',records};
}
test('native New scholarship state becomes a midweek offer post, and Offered does not duplicate it',async()=>{
 const a=updateRuntime(await readRuntime(raw('None')));assert.equal(a.catalog.stories.filter(p=>p.category==='offers').length,0);
 const snapshot=await readRuntime(raw('New'));assert.equal(snapshot.offers.length,1);
 const b=updateRuntime(snapshot,a.state),offer=b.catalog.stories.find(p=>p.category==='offers');
 assert.equal(offer.body,'AGTG! Blessed to receive an offer from Fixture University');assert.equal(offer.author,'Fixture Recruit');assert.ok(offer.scopes.includes('team'));assert.equal(offer.publication.week,8);
 const c=updateRuntime(await readRuntime(raw('Offered')),b.state);assert.equal(c.catalog.stories.filter(p=>p.category==='offers').length,1);
 const next=raw('Offered');next.records.season.v.CurrentWeek=9;const d=updateRuntime(await readRuntime(next),c.state);assert.equal(d.catalog.stories.filter(p=>p.category==='offers').length,0);
 assert.equal(d.catalog.weeks[0].stories.filter(p=>p.category==='offers').length,1);
});
test('initial native New offers seed quietly, while non-offer board entries stay excluded',async()=>{
 const s=await readRuntime(raw('New'));const initial=updateRuntime(s);assert.equal(initial.catalog.stories.filter(p=>p.category==='offers').length,0);
 for(const status of ['None','Declined'])assert.equal((await readRuntime(raw(status))).offers.length,0);
});
