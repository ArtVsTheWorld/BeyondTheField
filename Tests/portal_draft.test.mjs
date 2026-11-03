import test from 'node:test';
import assert from 'node:assert/strict';
import {draftBoard,draftEvents} from '../Tools/draft_results.mjs';
import {offseasonRecruitingEvents,portalOrigin} from '../Tools/offseason_recruiting.mjs';
import {buildFeed} from '../Tools/feed_engine.mjs';
import {updateRuntime} from '../Tools/runtime_lifecycle.mjs';
import {filterConversations} from '../Tools/social_discovery.mjs';

function fixture(){
 const s={format:2,gameYear:27,sourceKind:'runtime',source:'runtime:19:1',sourceUnchanged:true,sha256:'a'.repeat(64),leagueId:19,userTeamIndex:1,season:{CurrentYear:0,CurrentSeasonYear:2026,CurrentStage:'OffSeason',CurrentWeekType:'OffSeason',CurrentWeek:2,RegularSeasonWeekConferenceChampionship:15},players:[],teams:[],games:[],performances:[],heisman:[],conferences:[],offers:[],commitments:[],signings:[],recruitStatuses:[],portalEntrants:[],draftResults:[]};
 for(let id=1;id<=8;id++)s.teams.push({id,name:'School '+id,nickname:'Club '+id,logo:id,mediaRank:id,brandExposure:'APlus',rivals:[],prestigeStars:3,depthChart:{},headCoach:{name:'Coach '+id}});
 for(let i=0;i<224;i++){const id='p'+String(i).padStart(3,'0');s.players.push({id,name:'Player Family'+i,firstName:'Player',team:1+i%8,position:['QB','WR','HB','LT','CB','LE','DT','TE'][i%8],overall:90,personality:'Leader',classYear:'Senior',nil:100,injury:'Uninjured',seasonStats:[],allSeasonStats:[]});s.draftResults.push({player:id,round:1+Math.floor(i/32)});}return s;
}
test('the complete native class produces seven rounds with all 32 NFL clubs in each',()=>{
 const s=fixture(),b=draftBoard(s);assert.equal(b.length,224);assert.equal(new Set(b.map(p=>p.player)).size,224);assert.deepEqual(b.map(p=>p.pick),Array.from({length:224},(_,i)=>i+1));
 for(let round=1;round<=7;round++){const r=b.filter(p=>p.round===round);assert.equal(r.length,32);assert.equal(new Set(r.map(p=>p.nflTeam)).size,32);assert.deepEqual(new Set(r.map(p=>p.player)),new Set(s.draftResults.filter(p=>p.round===round).map(p=>p.player)));}
 assert.equal(s.players.find(p=>p.id===b[0].player).position,'QB');
});
test('draft slots and destinations remain stable through reloads, unrelated updates and scouting changes',()=>{
 const s=fixture(),a=draftBoard(s);assert.deepEqual(draftBoard({...s,players:[...s.players].reverse()}),a);s.players[0].overall=1;s.players[1].overall=99;assert.deepEqual(draftBoard(s,a),a);s.userTeamIndex=4;assert.deepEqual(draftBoard(s,a),a);
});
test('duplicate, incomplete or future draft classes cannot invent extra drafted players',()=>{
 for(const mutate of [s=>s.draftResults.pop(),s=>s.draftResults[0]={...s.draftResults[1]},s=>s.draftResults[0].round=7,s=>s.season.CurrentWeek=1,s=>s.season.CurrentStage='NFLSeason']){const s=fixture();mutate(s);assert.deepEqual(draftBoard(s),[]);assert.deepEqual(draftEvents(s),[]);}
});
test('a corrupted stored draft board is rejected and deterministically reconstructed',()=>{
 const s=fixture(),a=draftBoard(s),bad=structuredClone(a);bad[1].nflTeam=bad[0].nflTeam;assert.deepEqual(draftBoard(s,bad),a);bad[1].pick=bad[0].pick;assert.deepEqual(draftBoard(s,bad),a);
});
test('every pick gets the NFL Draft account and native sticker, with special top-ten and final picks',()=>{
 const s=fixture(),f=buildFeed(s),draft=f.stories.filter(p=>p.category==='draft');assert.equal(draft.length,224);assert.ok(draft.every(p=>p.author==='NFL Draft'&&p.handle==='@NFLDraft'&&p.imageLibrary===34&&p.imageValue===21&&p.transaction));assert.equal(draft.filter(p=>p.templateId.startsWith('draft.top-ten')).length,10);assert.ok(draft.find(p=>p.draftPick===224).body.includes('MR. IRRELEVANT'));assert.ok(draft.every(p=>!p.body.includes('overall rating')&&[...p.body].length<=280&&Buffer.byteLength(p.body)<=512));
 assert.equal(filterConversations(draft,'official').length,224);assert.deepEqual(filterConversations([...draft].reverse(),'transactions').map(p=>p.draftPick),Array.from({length:224},(_,i)=>i+1));assert.ok(f.posts.length<=30);assert.equal(f.posts.filter(p=>p.voice==='nflDraft'&&p.teamIds.includes(s.userTeamIndex)).length,28);
});
test('same-week runtime refresh freezes draft allocations and preserves their native catalog metadata',()=>{
 const s=fixture(),a=updateRuntime(structuredClone(s));s.players[0].overall=1;const b=updateRuntime(structuredClone(s),a.state);assert.deepEqual(b.state.editions[0].snapshot.draftBoard,a.state.editions[0].snapshot.draftBoard);const w=b.catalog.weeks.find(w=>w.phase==='OffSeason');assert.equal(w.stories.filter(p=>p.draftPick>0).length,224);
});
function portalFixture(){const s=fixture();s.draftResults=[];const p={id:'transfer',name:'Avery Jones',firstName:'Avery',team:255,position:'QB',classYear:'Junior',overall:94,starRating:4,allSeasonStats:[{stats:{SEAS_YEAR:0,GAMESPLAYED:8,YEARBYYEARTEAMINDEX:2}}],seasonStats:[]};s.players.push(p);s.portalEntrants=['transfer'];s.recruitStatuses=[{player:p.id,recruitClass:'Transfer_Junior',stage:'Top3',nationalRank:4,positionRank:1,stateRank:1,topSchools:[1,3]}];return s;}
test('portal stories require actual entries, preserve the former school and only report recorded interest',()=>{
 const s=portalFixture(),p=s.players.at(-1);assert.equal(portalOrigin(s,p),2);const e=offseasonRecruitingEvents(s);assert.ok(e.some(e=>e.facts.originDetail===' after leaving School 2'));assert.ok(e.some(e=>e.facts.schools==='School 1, School 3'));assert.ok(e.every(e=>e.facts.family.startsWith('portal.')||e.facts.family==='roster.interest'));s.portalEntrants=[];assert.deepEqual(offseasonRecruitingEvents(s),[]);
});
test('transfer risk alone, a signed transfer and a committed high school prospect do not become opening targets',()=>{
 const s=portalFixture();s.recruitStatuses[0].stage='Signed';assert.deepEqual(offseasonRecruitingEvents(s),[]);s.recruitStatuses[0]={...s.recruitStatuses[0],recruitClass:'HighSchool',stage:'HardCommitted'};assert.deepEqual(offseasonRecruitingEvents(s),[]);s.recruitStatuses[0].stage='Top5';assert.ok(offseasonRecruitingEvents(s).some(e=>e.facts.family==='portal.unsigned'));
});
test('remaining unsigned high school targets use actual stars and national position/state ranks',()=>{
 const s=portalFixture();s.portalEntrants=[];s.recruitStatuses[0]={...s.recruitStatuses[0],recruitClass:'HighSchool',stage:'Top5',positionRank:2,stateRank:3};const f=buildFeed(s),p=f.stories.find(p=>p.id.startsWith('portal-opening:unsigned:'));assert.ok(p);assert.match(p.body,/4-star/);assert.match(p.body,/No. 4 nationally/);assert.match(p.body,/QB Avery Jones/);
});
test('ambiguous former-school stats fall back to an observed roster identity instead of a default team',()=>{
 const s=portalFixture(),p=s.players.at(-1);p.allSeasonStats.push({stats:{SEAS_YEAR:0,GAMESPLAYED:8,YEARBYYEARTEAMINDEX:4}});assert.equal(portalOrigin(s,p),null);s.portalOrigins={transfer:3};assert.equal(portalOrigin(s,p),3);
});
