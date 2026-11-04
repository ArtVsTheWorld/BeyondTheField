import {updateRuntime} from '../Tools/runtime_lifecycle.mjs';
import {refreshAccountPresentation} from '../Tools/account_presentation.mjs';
import test from 'node:test';
import assert from 'node:assert/strict';
import {buildFeed,detectEvents} from '../Tools/feed_engine.mjs';
import {playerReferenceQualifier} from '../Tools/player_references.mjs';
import {publishReply} from '../Tools/publication_policy.mjs';
import {recruitAttention} from '../Tools/recruit_context.mjs';
import {draftBoard} from '../Tools/draft_results.mjs';
import {draftDiscourse} from '../Tools/draft_discourse.mjs';
function fixture(){
 const s={format:2,gameYear:27,sourceKind:'runtime',source:'runtime:19:1',sourceUnchanged:true,sha256:'a'.repeat(64),leagueId:19,userTeamIndex:1,season:{CurrentYear:0,CurrentSeasonYear:2026,CurrentStage:'OffSeason',CurrentWeekType:'OffSeason',CurrentWeek:2,RegularSeasonWeekConferenceChampionship:15},players:[],teams:[],games:[],performances:[],heisman:[],conferences:[],offers:[],commitments:[],signings:[],recruitStatuses:[],portalEntrants:[],draftResults:[]};
 for(let id=1;id<=8;id++)s.teams.push({id,name:'School '+id,nickname:'Club '+id,logo:id,mediaRank:id,brandExposure:'APlus',rivals:[],prestigeStars:3,depthChart:{},headCoach:{name:'Coach '+id}});
 for(let i=0;i<224;i++){const id='p'+String(i).padStart(3,'0');s.players.push({id,name:'Player Family'+i,firstName:'Player',team:1+i%8,position:['QB','WR','HB','LT','CB','LE','DT','TE'][i%8],overall:90,personality:'Leader',classYear:'Senior',nil:100,injury:'Uninjured',seasonStats:[],allSeasonStats:[]});s.draftResults.push({player:id,round:1+Math.floor(i/32)});}return s;
}
function recruit(s,{id='r',stars=4,kind='Transfer_Junior',stage='HardCommitted',team=2,rank=5}={}){
 const p={id,name:'Jordan Player'+id,firstName:'Jordan',team:255,position:'QB',overall:94,starRating:stars,personality:'Leader',allSeasonStats:[{stats:{SEAS_YEAR:0,GAMESPLAYED:9,YEARBYYEARTEAMINDEX:1}}],seasonStats:[]};s.players.push(p);
 s.recruitStatuses.push({player:id,recruitClass:kind,stage,nationalRank:rank,positionRank:1,stateRank:3,topSchools:[team,3]});
 if(stage.includes('Committed')){const c={player:id,team,rank,stage,recruitClass:kind};s.commitments.push(c);s.newCommitments=[...(s.newCommitments??[]),c];}return p;
}
test('suffix positions do not get a duplicate prefix',()=>{
 const q=playerReferenceQualifier([{id:'a',name:'Colin Feil',position:'TE'}]);assert.equal(q('Colin Feil, a TE, has committed.'),'Colin Feil, a TE, has committed.');assert.equal(q('TE Colin Feil has committed.'),'TE Colin Feil has committed.');assert.equal(q('Colin Feil has committed.'),'TE Colin Feil has committed.');
});
test('one-stars get no recruiting coverage and occasional two-stars get only underdog stories',()=>{
 const s=fixture();s.draftResults=[];recruit(s,{stars:1,kind:'HighSchool'});assert.ok(!buildFeed(s).stories.some(p=>p.playerId==='r'));
 let admitted=0;for(let i=0;i<100;i++){const p={id:'under'+i,starRating:2};if(recruitAttention(s,p))admitted++;}assert.ok(admitted>=3&&admitted<=20);
 const p=s.players.at(-1);p.starRating=2;while(!recruitAttention(s,p))s.leagueId++;const posts=buildFeed(s).stories.filter(p=>p.playerId==='r');assert.ok(posts.length);assert.ok(posts.every(p=>p.templateId.startsWith('roster.underdog')));
});
test('transfer commitment names both schools and recognizes either side of a native rivalry',()=>{
 const s=fixture();s.draftResults=[];s.teams[0].name='Florida';s.teams[1].name='Florida State';s.teams[0].rivals=[2];recruit(s);const f=buildFeed(s),report=f.stories.find(p=>p.templateId.startsWith('roster.rival-transfer'));assert.ok(report);assert.match(report.body,/Florida State/);assert.match(report.body,/from (?:rival )?Florida/);assert.match(report.body,/4-star transfer QB/);assert.ok(detectEvents(s).find(e=>e.id==='commit:2:r').facts.rivalTransfer);
});
test('a returning portal player gets beat retention coverage and smug fans, never an official welcome',()=>{
 const s=fixture();s.draftResults=[];const p=recruit(s,{team:1});s.players.at(-1).overall=91;
 while(!publishReply(s,'x','commit:1:r:main'))s.leagueId++;
 const f=buildFeed(s),posts=f.stories.filter(x=>x.eventId==='commit:1:r');assert.ok(posts.some(x=>x.voice==='beat'&&x.templateId.startsWith('roster.returning')));assert.ok(posts.some(x=>x.voice==='fan'&&x.templateId.startsWith('roster.returning-star-fan')));assert.ok(!posts.some(x=>x.voice==='official'||/previously at|from School 1 to School 1/i.test(x.body)));
});
test('JUCO is explicit in reports and recruit profile; five-stars are announced by ESPNCFB',()=>{
 const s=fixture();s.draftResults=[];recruit(s,{stars:5,kind:'JuniorCollege_Sophomore'});const f=buildFeed(s);assert.ok(f.stories.some(p=>p.handle==='@ESPNCFB'&&/5-star JUCO QB/.test(p.body)));assert.ok(f.stories.some(p=>p.voice==='recruit'&&/JUCO QB/.test(p.author)));
});
test('every qualifying team commitment survives weekly flavor limits',()=>{
 const s=fixture();s.draftResults=[];for(let i=0;i<25;i++)recruit(s,{id:'r'+i,stars:3,kind:'HighSchool',team:1,rank:100+i});const f=buildFeed(s),reports=f.stories.filter(p=>p.coverageExempt&&p.eventId.startsWith('commit:1:'));assert.equal(reports.length,25);assert.ok(reports.every(p=>f.views['team:1:required'].includes(p.id)));assert.ok(reports.every(p=>f.views['team:1'].includes(p.id)));assert.ok(f.posts.length<=30);
});
test('Maddox and Brooks cover genuine portal interest throughout recruiting; committed transfers are excluded',()=>{
 const s=fixture();s.draftResults=[];s.season.CurrentWeek=3;for(let i=0;i<12;i++){const p=recruit(s,{id:'open'+i,kind:'Transfer_Junior',stage:'Top3'});s.portalEntrants.push(p.id);}const f=buildFeed(s),posts=f.stories.filter(p=>p.templateId.startsWith('roster.interest'));assert.ok(posts.some(p=>p.author==='Chris Maddox'));assert.ok(posts.some(p=>p.author==='Tina Brooks'));assert.ok(posts.every(p=>p.body.includes('School 1')&&p.body.includes('School 2')));
 s.recruitStatuses.forEach(r=>r.stage='Signed');assert.ok(!buildFeed(s).stories.some(p=>p.templateId.startsWith('roster.interest')));
});
test('former and destination fans reply to the actual recruit with persisted handles',()=>{
 const s=fixture();s.draftResults=[];s.teams[0].rivals=[2];recruit(s);while(!publishReply(s,'x','commit:2:r:main'))s.leagueId++;const f=buildFeed(s),parent=f.stories.find(p=>p.id==='commit:2:r:main'),replies=f.stories.filter(p=>p.replyTo===parent?.id);assert.ok(parent&&parent.voice==='recruit');assert.ok(replies.some(p=>p.templateId.startsWith('roster.rival-fan')));assert.ok(replies.some(p=>p.templateId.startsWith('roster.welcome')));assert.ok(replies.every(p=>p.body.includes(parent.handle)));
});
test('draft discourse counts actual first rounds, native conferences and all team picks',()=>{
 const s=fixture();s.teams.push({id:9,name:'No Picks',rivals:[]});s.conferences=[{id:1,name:'Custom League',teams:[1,2,3,4]},{id:2,name:'Other League',teams:[5,6,7,8,9]}];s.draftBoard=draftBoard(s);const e=draftDiscourse(s);assert.ok(e.some(e=>e.facts.family==='draft-talk.conference-leader'&&e.facts.count===16&&e.facts.conferences.includes('Custom League')));assert.equal(e.filter(e=>e.facts.family==='draft-talk.top-ten').length,10);assert.ok(e.some(e=>e.options.team===9&&e.facts.family==='draft-talk.empty'));const f=buildFeed(s);assert.equal(f.posts.filter(p=>p.voice==='nflDraft'&&p.teamIds.includes(1)).length,28);assert.ok(f.views['team:1'].filter(id=>f.stories.find(p=>p.id===id)?.voice==='nflDraft').length===28);
});

test('draft discussion survives native draft cleanup using the recorded class, without republishing official picks',()=>{
 const s=fixture(),a=updateRuntime(structuredClone(s));s.season.CurrentWeek=4;s.draftResults=[];s.players.forEach(p=>p.team=255);const b=updateRuntime(s,a.state);assert.ok(b.catalog.stories.some(p=>p.category==='draft-discourse'));assert.ok(!b.catalog.stories.some(p=>p.voice==='nflDraft'));assert.ok(b.catalog.stories.some(p=>p.body.includes('School 1')&&p.category==='draft-discourse'));
});
test('archived draft browsing gains every own pick without rewriting its stories',()=>{
 const s=fixture(),f=buildFeed(s),before=f.stories.map(p=>[p.id,p.body,p.likes]);delete f.views['all:expanded'];delete f.views['all:default'];const fixed=refreshAccountPresentation(f,s);assert.deepEqual(fixed.stories.map(p=>[p.id,p.body,p.likes]),before);assert.equal(fixed.views['all:default'].filter(id=>fixed.stories.find(p=>p.id===id)?.voice==='nflDraft'&&fixed.stories.find(p=>p.id===id)?.teamIds.includes(1)).length,28);
});

test('undrafted signings do not prevent draft recovery after native cleanup',()=>{
 const s=fixture(),a=updateRuntime(structuredClone(s)),entry=a.state.editions.at(-1);
 entry.snapshot.recentDraftClass=[];entry.feed.events.push({id:'udfa:test',category:'draft',teamIds:[1],facts:{family:'draft.udfa',playerName:'Undrafted Senior'}});
 s.season.CurrentWeek=4;s.draftResults=[];s.players.forEach(p=>p.team=255);
 const b=updateRuntime(s,a.state);assert.equal(s.recentDraftClass.length,224);assert.ok(b.catalog.stories.some(p=>p.category==='draft-discourse'));
});
