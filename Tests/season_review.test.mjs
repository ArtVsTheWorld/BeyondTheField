import test from 'node:test';
import assert from 'node:assert/strict';
import {buildFeed} from '../Tools/feed_engine.mjs';
import {updateRuntime} from '../Tools/runtime_lifecycle.mjs';
import {transactionObservation,transactionEvents,blueprintNILChanges} from '../Tools/transaction_events.mjs';
import {observedStaffMoves,seasonReviewEvents,portalRiskEvents} from '../Tools/season_review_events.mjs';
import {focusFixtures} from '../Tools/postseason_buzz.mjs';
import {filterConversations} from '../Tools/social_discovery.mjs';

function fixture(){
 const s={format:2,gameYear:27,sourceKind:'runtime',source:'runtime:9:2',sourceUnchanged:true,sha256:'a'.repeat(64),leagueId:9,userTeamIndex:2,season:{CurrentYear:0,CurrentSeasonYear:2026,CurrentWeek:0,CurrentWeekType:'OffSeason',CurrentStage:'OffSeason',RegularSeasonWeekConferenceChampionship:15},teams:[],players:[],games:[],performances:[],signings:[],commitments:[],offers:[],heisman:[],conferences:[],recruitStatuses:[]};
 for(let id=1;id<=8;id++){
  const w=id<=2?12:5,t={id,name:'School '+id,nickname:'Club '+id,logo:id,rivals:[],brandExposure:'APlus',mediaRank:id,prestigeStars:id<=2?5:1,wins:w,losses:12-w,seasonStats:{season:2026,stats:{WINS:w+(id===1?1:0),LOSSES:12-w+(id===2?1:0),TIES:0}},depthChart:{},headCoach:{id:'c'+id,name:'Coach '+id,contract:{status:'Signed',length:3,count:1,remaining:2}}};s.teams.push(t);
  s.players.push({id:'p'+id,name:'Milo Taylor'+id,firstName:'Milo',team:id,position:'QB',classYear:'Junior',nil:100,transferRisk:-1,injury:'Uninjured',personality:'Leader',overall:80,seasonStats:[]});
  for(let week=1;week<=12;week++)s.games.push({id:id+'-g'+week,year:0,phase:'RegularSeason',week,home:id,away:255,status:week<=w?'HomeWon':'AwayWon',published:true,homeScore:week<=w?35:14,awayScore:week<=w?14:35});
 }
 s.games.push({id:'title',year:0,week:20,phase:'NationalChampionship',isPlayoff:true,bowlName:'National Championship',home:1,away:2,homeName:'School 1',awayName:'School 2',status:'HomeWon',published:true,homeScore:31,awayScore:22,homeQuarterScores:[3,6,8,14],awayQuarterScores:[8,6,0,8],homeStats:{GIVEAWAYS:0},awayStats:{GIVEAWAYS:2}});
 return s;
}
test('offseason week zero has a national title recap and both finalist perspectives',()=>{
 const s=fixture(),f=buildFeed(s),national=f.views.national.map(id=>f.stories.find(p=>p.id===id));
 assert.ok(national.length>0);assert.ok(national.some(p=>p.author==='CFP'&&p.body.includes('31–22')));
 assert.ok(national.some(p=>p.body.includes('trailed 14–9 at halftime')));
 assert.ok(national.some(p=>p.body.includes('one win short')||p.body.includes('runner-up')));
 assert.ok(national.some(p=>p.author==='Tina Brooks'&&/season|offseason/i.test(p.body)));
 for(const author of ['Jake Whitmore','Marcus Bennett','Tina Brooks','David Ellison','Chris Maddox'])assert.ok(national.some(p=>p.author===author),author);
 for(const id of [1,2])assert.ok(f.stories.filter(p=>p.teamIds.includes(id)).length<=25);
 assert.ok(f.stories.every(p=>[...p.body].length<=280&&Buffer.byteLength(p.body)<=512));
});
test('the recap edition never predicts the completed title or carries it into later offseason weeks',()=>{
 const s=fixture();assert.equal(focusFixtures(s).length,1);assert.ok(!buildFeed(s).stories.some(p=>/my pick|one game left|take on.*national championship/i.test(p.body)));
 s.season.CurrentWeek=1;assert.deepEqual(focusFixtures(s),[]);assert.deepEqual(seasonReviewEvents(s),[]);
});
test('Players Leaving has national coverage without premature portal entries or draft results',()=>{
 const s=fixture();s.season.CurrentWeek=1;const f=buildFeed(s),national=f.views.national.map(id=>f.stories.find(p=>p.id===id));
 assert.ok(national.length>=3);assert.ok(national.some(p=>p.author==='Chris Maddox'));assert.ok(national.some(p=>p.author==='Tina Brooks'));assert.ok(national.some(p=>p.author==='Jake Whitmore'));
 assert.ok(!national.some(p=>p.draftPick||p.templateId.startsWith('portal.entrant')));
});
test('missing, unpublished, ambiguous or different-year finals cannot create championship claims',()=>{
 for(const mutate of [s=>s.games.pop(),s=>s.games.at(-1).published=false,s=>s.games.at(-1).year=-1,s=>s.games.push({...s.games.at(-1),id:'duplicate'})]){
  const s=fixture();mutate(s);assert.deepEqual(focusFixtures(s),[]);const e=seasonReviewEvents(s);assert.ok(e.some(e=>e.id==='review:national-calendar'));assert.ok(!e.some(e=>e.facts.gameId));
 }
});
test('retention watch rejects uninitialized risks and distinguishes risk from an entry or destination',()=>{
 const s=fixture();assert.deepEqual(portalRiskEvents(s),[]);s.players[0].transferRisk=85;
 const e=portalRiskEvents(s);assert.equal(e.length,1);assert.equal(e[0].facts.playerName,'Milo Taylor1');
 const p=buildFeed(s).stories.find(p=>p.category==='transfer');assert.ok(p);assert.match(p.body,/not a report|no confirmed/i);assert.match(p.body,/QB Milo/);
 assert.ok(filterConversations([p],'transactions').includes(p));
});
test('seniors, zero risk, invalid values and non-offseason phases do not become portal rumors',()=>{
 for(const risk of [-1,0,49,101,NaN]){const s=fixture();s.players[0].transferRisk=risk;assert.deepEqual(portalRiskEvents(s),[]);}
 const s=fixture();s.players[0].transferRisk=90;s.players[0].classYear='Senior';assert.deepEqual(portalRiskEvents(s),[]);s.players[0].classYear='Junior';s.season.CurrentStage='NFLSeason';assert.deepEqual(portalRiskEvents(s),[]);
});
test('unchanged retention concerns stay quiet in later offseason editions, while material risk changes reopen coverage',()=>{
 const s=fixture();s.players[0].transferRisk=75;const a=updateRuntime(structuredClone(s));assert.ok(a.catalog.stories.some(p=>p.eventId==='retention-watch:p1'));
 s.season.CurrentWeek=1;const b=updateRuntime(structuredClone(s),a.state);assert.ok(!b.catalog.stories.some(p=>p.eventId==='retention-watch:p1'));
 s.players[0].transferRisk=95;const c=updateRuntime(structuredClone(s),b.state);assert.ok(c.catalog.stories.some(p=>p.eventId==='retention-watch:p1'));
});
test('staff retrospective admits confirmed same-season moves, never pending offers or firings',()=>{
 const row=(id,family,coachName='Actual Coach')=>({id,teamIds:[3],facts:{family,coachName,role:'head coach'}});
 const feed={season:2026,events:[row('hire','postseason.coach-hired'),row('offer','postseason.coach-offer'),row('pending','postseason.coach-pending')]};
 const moves=observedStaffMoves([feed,feed,{season:2025,events:[row('old','postseason.coach-fired','Old Coach')]}],2026);assert.equal(moves.length,1);
 const s=fixture();s.seasonStaffMoves=moves;const e=seasonReviewEvents(s).find(e=>e.category==='coaching');assert.ok(e);assert.equal(e.facts.coachName,'Actual Coach');assert.ok(!e.facts.contractSalary);
});
test('phase archives supply staff retrospectives even when current carousel tables have emptied',()=>{
 const s=fixture(),past=structuredClone(s);Object.assign(past.season,{CurrentStage:'NFLSeason',CurrentWeekType:'BowlSeason1',CurrentWeek:17});const archive=buildFeed(past);archive.events.push({id:'hire',category:'coaching',teamIds:[3],facts:{family:'postseason.coach-hired',coachName:'Actual Coach',role:'head coach'}});
 const r=updateRuntime(s,undefined,{archives:[archive]});assert.ok(r.catalog.stories.some(p=>p.category==='coaching'&&p.body.includes('Actual Coach')));
});
test('blueprint NIL adjustments publish the next week, stay stable, and do not repeat a week later',()=>{
 let s=fixture(),a=updateRuntime(structuredClone(s));s.players[0].nil=140;s.players[1].nil=75;
 const b=updateRuntime(structuredClone(s),a.state);assert.ok(!b.catalog.stories.some(p=>p.category==='nil'));
 s.season.CurrentWeek=1;const c=updateRuntime(structuredClone(s),b.state),deals=c.catalog.stories.filter(p=>p.category==='nil');assert.equal(deals.length,2);assert.ok(deals.some(p=>p.body.includes('$560K')&&p.body.includes('$400K')));assert.ok(deals.some(p=>p.body.includes('$300K')));assert.ok(deals.every(p=>/last week|review/i.test(p.body)));
 assert.deepEqual(updateRuntime(structuredClone(s),c.state).catalog.stories,c.catalog.stories);
 s.season.CurrentWeek=2;assert.ok(!updateRuntime(s,c.state).catalog.stories.some(p=>p.category==='nil'));
});
test('net blueprint changes exclude reverted edits, team moves, missing amounts and another season',()=>{
 const s=fixture(),a=transactionObservation(s);s.players[0].nil=150;s.players[0].nil=100;s.players[1].nil=null;s.players[2].team=4;s.players[2].nil=200;
 assert.deepEqual(blueprintNILChanges(a,transactionObservation(s)),[]);s.players[0].nil=200;assert.equal(blueprintNILChanges(a,transactionObservation(s)).length,1);assert.deepEqual(blueprintNILChanges({...a,year:2025},transactionObservation(s)),[]);
});
test('a newly installed week-one observer cannot invent unobserved blueprint adjustments',()=>{const s=fixture();s.season.CurrentWeek=1;assert.ok(!updateRuntime(s).catalog.stories.some(p=>p.category==='nil'));});
test('later offseason midweek NIL changes and confirmed coach renewals remain observable',()=>{
 const s=fixture();s.season.CurrentWeek=2;s.transactionBaseline=transactionObservation(s);s.players[0].nil=125;s.teams[0].headCoach.contract.count=2;
 const e=transactionEvents(s);assert.ok(e.some(e=>e.category==='nil'));assert.ok(e.some(e=>e.facts.family==='transactions.coach-deal'));
});
test('same-week title recap refresh preserves prose and archived title-week news remains intact',()=>{
 const s=fixture(),a=updateRuntime(structuredClone(s)),b=updateRuntime(structuredClone(s),a.state);assert.deepEqual(a.catalog.stories,b.catalog.stories);
 const past=structuredClone(s);Object.assign(past.season,{CurrentStage:'NFLSeason',CurrentWeekType:'NationalChampionship',CurrentWeek:20});const title=buildFeed(past);const signature=stories=>JSON.stringify(stories.map(p=>({id:p.id,body:p.body,author:p.author,handle:p.handle,likes:p.likes,publication:p.publication})));const before=signature(title.stories),c=updateRuntime(structuredClone(s),b.state,{archives:[title]});assert.equal(signature(c.catalog.weeks.find(w=>w.phase==='NationalChampionship').stories),before);
});
