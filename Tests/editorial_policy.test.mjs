import test from 'node:test';
import assert from 'node:assert/strict';
import {freshEditorialEvents,validEditorialContext} from '../Tools/editorial_policy.mjs';
import {corroboratedSackGames} from '../Tools/matchup_events.mjs';
const pub=(phase='OffSeason',week=3)=>({leagueId:1,userTeamIndex:1,season:2027,phase,week});
const event=(family='cycle.staff-plan',facts={})=>({id:family,category:'offseason',teamIds:[1],facts:{family,coachName:'Coach One',...facts}});
const old=(e,phase='RegularSeason',week=16,published=true)=>({...pub(phase,week),events:[e],stories:published?[{id:e.id+':main',eventId:e.id}]:[]});
test('unavailable standings and entirely empty tables do not become leader stories',()=>{
 const e={category:'standings',facts:{leaders:[{wins:0,losses:0,conferencePlace:-1}]}};assert.equal(validEditorialContext(e),false);e.facts.leaders[0].conferencePlace=0;assert.equal(validEditorialContext(e),false);e.facts.leaders[0].wins=1;assert.equal(validEditorialContext(e),true);e.facts.leaders[0].conferencePlace=-1;assert.equal(validEditorialContext(e),false);
});
test('uncorroborated zero-sacks claims are withheld without treating a confirmed zero as missing',()=>{
 const e=event('matchup.protection-preview',{attack:'0.0',defense:'1.2'});assert.equal(validEditorialContext(e),false);e.facts.protectionCorroborated=true;assert.equal(validEditorialContext(e),true);
});
test('protection needs complete matching offensive/defensive sacks, including a legitimate zero',()=>{
 const g={homeStats:{SACKSALLOWED:0,SACKS:2},awayStats:{SACKSALLOWED:2,SACKS:0}};assert.ok(corroboratedSackGames([g]));const bad=structuredClone(g);bad.awayStats.SACKS=1;assert.ok(!corroboratedSackGames([bad]));delete bad.awayStats.SACKS;assert.ok(!corroboratedSackGames([bad]));assert.ok(!corroboratedSackGames([]));
});
test('unchanged topic stays quiet across publication phases and reopens for a real staff change',()=>{
 const e=event();assert.equal(freshEditorialEvents([e],pub(),[old(e)]).length,0);const changed=event('cycle.staff-plan',{coachName:'New Coach'});assert.equal(freshEditorialEvents([changed],pub(),[old(e)]).length,1);
});
test('same-week reopens retain stories while future, foreign, reconstructed and older-season observations cannot suppress them',()=>{
 const e=event();for(const h of [{...old(e),...pub()},{...old(e),...pub('OffSeason',5)},{...old(e),leagueId:2},{...old(e),userTeamIndex:2},{...old(e),season:2026},{...old(e),reconstructed:true}])assert.equal(freshEditorialEvents([e],pub(),[h]).length,1);
});
test('crowded-out roots and replies alone never count as published news',()=>{
 const e=event();assert.equal(freshEditorialEvents([e],pub(),[old(e,'OffSeason',2,false)]).length,1);const h=old(e);h.stories[0].replyTo='missing';assert.equal(freshEditorialEvents([e],pub(),[h]).length,1);
});
test('thanks published at the actual season ending suppresses a later generic team reset',()=>{
 assert.equal(freshEditorialEvents([event('cycle.team-reset')],pub(),[old(event('ending.team.rough'))]).length,0);
});
test('actual season-ending thanks wins over same-edition generic reset',()=>{
 const ending={...event('ending.team.rough'),priority:100},reset={...event('cycle.team-reset'),priority:85};assert.deepEqual(freshEditorialEvents([reset,ending],pub()).map(e=>e.id),[ending.id]);
});
test('new recruit interest survives freshness filtering and unchanged interest does not',()=>{
 const e={...event('roster.interest',{schools:'Alpha, Beta'}),playerId:'p',category:'recruiting'};assert.equal(freshEditorialEvents([e],pub(),[old(e)]).length,0);assert.equal(freshEditorialEvents([{...e,facts:{...e.facts,schools:'Gamma, Beta'}}],pub(),[old(e)]).length,1);
});
test('freshness never suppresses actual offers, commitments, injuries, signatures or new game results',()=>{
 for(const category of ['offers','recruiting','injuries','signings','results']){const e={id:category,category,teamIds:[1],facts:{}};assert.equal(freshEditorialEvents([e],pub(),[old(e)]).length,1);}
});
test('latest published state allows a real change back and pruning future history restores eligibility',()=>{
 const a=event(),b=event('cycle.staff-plan',{coachName:'Second Coach'});assert.equal(freshEditorialEvents([a],pub(),[old(a,'OffSeason',0),old(b,'OffSeason',1)]).length,1);assert.equal(freshEditorialEvents([b],pub('OffSeason',0),[old(b,'OffSeason',1)]).length,1);
});
