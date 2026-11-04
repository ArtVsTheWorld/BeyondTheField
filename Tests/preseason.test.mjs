import {publishReply} from '../Tools/publication_policy.mjs';
import test from 'node:test';
import assert from 'node:assert/strict';
import {preseasonEvents,titleFutures} from '../Tools/preseason_events.mjs';
import {buildFeed} from '../Tools/feed_engine.mjs';
function fixture(){
 const s={format:2,gameYear:27,sourceKind:'runtime',source:'runtime:test',sourceUnchanged:true,sha256:'a'.repeat(64),leagueId:7,userTeamIndex:1,season:{CurrentYear:0,CurrentSeasonYear:2026,CurrentWeek:0,CurrentWeekType:'PreSeason',CurrentStage:'PreSeason'},teams:[{id:1,name:'BYU',nickname:'Cougars',logo:15,conferenceId:'custom',conferenceName:'Custom Conference',mediaRank:12,hashtags:['#GoCougs']},{id:230,name:'Harbor Tech',nickname:'Sharks',logo:230,conferenceId:'custom',conferenceName:'Custom Conference',mediaRank:99}],conferences:[{id:'custom',name:'Custom Conference',teams:[1,230]}],players:[],games:[{id:'opener',year:0,phase:'RegularSeason',week:1,status:'Unplayed',home:230,away:1}],performances:[],offers:[],commitments:[],heisman:[],weeklyAwards:[],records:[],recruitStatuses:[],preseasonHonors:[]};
 for(const team of s.teams)for(const position of ['QB','HB','FB','WR','TE','LT','LG','C','RG','RT','DT','LE','RE','MLB','LOLB','ROLB','CB','FS','SS','K','P'])s.players.push({id:team.id+'-'+position,name:'Evan '+position,team:team.id,position,injury:'Uninjured',overall:team.id===1?85:72,personality:'Leader'});
 s.preseasonHonors=[{id:'a',player:'1-QB',team:1,type:'ALL_AM_1ST_PRE',year:0},{id:'b',player:'230-WR',team:230,type:'ALL_AM_1ST_PRE_CONF',conferenceId:'custom',year:0}];s.players.push({id:'recruit',name:'Jay Moss',team:255,position:'WR',starRating:5,personality:'Entertainer'});s.recruitStatuses=[{player:'recruit',stage:'Top10',nationalRank:1}];return s;
}
test('preseason mixes native poll, honors, outlooks, openers, camp, fans, recruits and sportsbook futures',()=>{
 const s=fixture(),f=buildFeed(s);for(const voice of ['official','beat','analyst','player','fan','recruit','model'])assert.ok(f.stories.some(p=>p.voice===voice),voice+' missing');
 assert.ok(f.stories.some(p=>p.templateId.startsWith('preseason.poll')&&p.body.includes('12')));assert.ok(f.stories.some(p=>p.body.includes('All-Custom Conference')));assert.ok(f.stories.some(p=>p.templateId.startsWith('sportsbook.futures')&&/title|champion/i.test(p.body)&&!/(fictional|model)/i.test(p.body)));
 assert.ok(f.stories.some(p=>p.teamIds.includes(230)&&p.voice==='official'));assert.ok(!f.events.some(e=>e.category==='offers'));assert.ok(f.stories.every(p=>![...p.body].some(c=>c==='\uFFFD')&&[...p.body].length<=280&&Buffer.byteLength(p.body,'utf8')<=512));
});
test('missing poll evidence, wrong-year honors and committed recruits do not become preseason claims',()=>{
 const s=fixture();s.teams[0].mediaRank=null;s.preseasonHonors[0].year=1;s.commitments=[{player:'recruit',team:1,stage:'HardCommitted'}];const events=preseasonEvents(s);assert.ok(!events.some(e=>e.id==='preseason:poll:1'));assert.ok(!events.some(e=>e.id==='preseason:honor:a'));assert.ok(!events.some(e=>e.id.startsWith('preseason:recruit-')));
});
test('camp does not imply injured-player participation and QB voice stays restrained',()=>{
 const s=fixture();s.players.find(p=>p.id==='1-QB').injury='Injured';const events=preseasonEvents(s);assert.ok(!events.some(e=>e.id==='preseason:camp:1'&&e.options.player==='1-QB'));s.players.find(p=>p.id==='1-QB').injury='Uninjured';assert.equal(preseasonEvents(s).find(e=>e.id==='preseason:camp:1').facts.family,'preseason.player.QB');
});
test('preseason story families stop when regular-season play begins; model probabilities cover supported rosters',()=>{
 const s=fixture(),f=titleFutures(s);assert.equal(f.length,2);assert.ok(Math.abs(f.reduce((n,r)=>n+r.probability,0)-1)<1e-12);assert.equal(f[0].team,1);assert.ok(f.every(r=>r.simulated&&/^[+-]\d+$/.test(r.odds)));s.season.CurrentWeekType='RegularSeason';s.season.CurrentStage='NFLSeason';assert.deepEqual(preseasonEvents(s),[]);
});
test('unsaved preseason offers still use actual observation instead of fabricated commitments',()=>{
 const s=fixture();s.newOffers=[{player:'recruit',team:1,rank:1}];const f=buildFeed(s);assert.ok(f.stories.some(p=>p.category==='offers'&&p.body.includes('BYU')));assert.ok(!f.stories.some(p=>/committing to|welcome to the/i.test(p.body)));
});

test('unaffiliated preseason prospect watches use Maddox and Brooks rather than a generic school beat',()=>{
 const s=fixture();for(let i=0;i<20;i++){s.players.push({id:'watch'+i,name:'Prospect '+i,team:255,position:'WR',starRating:5});s.recruitStatuses.push({player:'watch'+i,stage:'Top10',nationalRank:i+2});}
 const f=buildFeed(s),posts=f.stories.filter(p=>p.eventId.startsWith('preseason:recruit-watch:'));assert.ok(posts.length>5);assert.ok(posts.every(p=>p.voice==='analyst'&&['Chris Maddox','Tina Brooks'].includes(p.author)));assert.ok(posts.some(p=>p.author==='Chris Maddox')&&posts.some(p=>p.author==='Tina Brooks'));assert.ok(!posts.some(p=>p.handle.includes('OnCollege')));assert.ok(f.stories.some(p=>p.voice==='beat'&&p.teamIds.length));
});
test('approved schedule gauntlets count actual AP-ranked opponents inside a four-week window',()=>{
 const s=fixture();s.teams[1].mediaRank=20;s.teams.push({id:3,name:'Mountain',mediaRank:3});s.games.push({id:'g2',year:0,phase:'RegularSeason',week:4,status:'Unplayed',home:1,away:3});
 const e=preseasonEvents(s).find(e=>e.id==='preseason:gauntlet:1');assert.equal(e.facts.count,2);assert.equal(e.facts.startWeek,1);assert.ok(e.facts.opponents.includes('No. 20 Harbor Tech'));s.games[1].week=5;assert.ok(!preseasonEvents(s).some(e=>e.id==='preseason:gauntlet:1'));
});
test('native conference selections drive talent maps, deduplicating player appearances',()=>{
 const s=fixture();s.preseasonHonors.push({...s.preseasonHonors[1],id:'duplicate'});const f=buildFeed(s),e=f.events.find(e=>e.id==='preseason:talent-map:custom');assert.equal(e.facts.count,1);assert.equal(e.facts.leaderCount,1);assert.equal(e.facts.leaders,'Harbor Tech');assert.ok(f.stories.some(p=>p.eventId===e.id&&p.body.includes('Custom Conference')));
});
test('preseason outlooks do not inherit in-season production or coach-performance replies',()=>{
 const s=fixture();s.teams[0].headCoach={name:'Casey Dunn',lastName:'Dunn'};const f=buildFeed(s),previews=new Set(f.stories.filter(p=>p.category==='analytics'&&p.eventId.startsWith('preseason:')&&!p.eventId.includes('poll-debate')).map(p=>p.id));assert.ok(!f.stories.some(p=>p.replyTo&&previews.has(p.replyTo)));
});
test('poll-model disagreements are labeled model opinions with attached fan replies; Coaches comparisons are labeled',()=>{
 const s=fixture();s.teams[0].mediaRank=20;s.teams[0].coachesRank=4;const f=buildFeed(s),p=f.stories.find(p=>p.eventId==='preseason:poll-debate:1');assert.ok(p&&p.body.includes('model')&&!p.body.includes('fictional'));assert.equal(f.stories.some(r=>r.replyTo===p.id),publishReply(s,'reply',p.id));assert.ok(f.stories.some(p=>p.eventId==='preseason:poll-comparison:1'&&p.body.includes('Coaches poll')&&p.body.includes('AP')));
});
