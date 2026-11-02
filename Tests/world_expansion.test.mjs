import test from 'node:test';
import assert from 'node:assert/strict';
import {advancedAnalytics,TEAM_SCENARIOS,PLAYER_SCENARIOS} from '../Tools/advanced_analytics.mjs';
import {worldEvents,recruitSignificance} from '../Tools/world_events.mjs';
import {projectLine,rosterStrengths} from '../Tools/betting_model.mjs';
import {updateRuntime} from '../Tools/runtime_lifecycle.mjs';
import {buildFeed} from '../Tools/feed_engine.mjs';
import {likesFor,replyLikesFor,ENGAGEMENT_VERSION} from '../Tools/story_engagement.mjs';
function fixture(){
 const stats={OFFPASSYARDS:350,OFFRUSHYARDS:190,OFFYARDS:540,PASSATTEMPTS:30,PASSCOMPLETIONS:24,RUSHATTEMPTS:30,PASSINTS:0,PASSTDS:4,RUSHTDS:5,FOURTHDOWNS:4,FOURTHDOWNCONV:3,DEFRUSHYARDS:70,DEFPASSYARDS:160,TAKEAWAYS:3,GIVEAWAYS:0,SACKS:4,OFFREDZONEFGS:2,OFFREDZONETDS:3,PENALTYYARDS:20,DEFREDZONES:4,DEFREDZONETDS:1};
 const s={format:2,gameYear:27,sourceUnchanged:true,source:'runtime:1:1',sourceKind:'runtime',sha256:'a'.repeat(64),leagueId:1,userTeamIndex:1,season:{CurrentYear:1,CurrentSeasonYear:2027,CurrentWeek:4,CurrentWeekType:'RegularSeason',CurrentStage:'NFLSeason'},teams:[{id:1,name:'Harbor',nickname:'Captains',logo:11,conferenceId:'c',conferenceName:'Coast',prestigeStars:1,mediaRank:8,mediaLastRank:24,wins:3,losses:0,ties:0,headCoach:{name:'Alex Stone',lastName:'Stone'},offensiveCoordinator:{name:'Casey Reed'},defensiveCoordinator:{name:'Sam West'}},{id:2,name:'Mesa',logo:22,conferenceId:'c',conferenceName:'Coast',mediaRank:20,mediaLastRank:3,wins:0,losses:3,ties:0}],conferences:[{id:'c',name:'Coast',teams:[1,2]}],players:[],games:[],performances:[],offers:[],commitments:[],heisman:[],records:[],weeklyAwards:[]};
 for(let i=1;i<=3;i++)s.games.push({id:'g'+i,year:1,week:i,phase:'RegularSeason',published:true,status:'HomeWon',home:1,away:2,homeScore:63,awayScore:38,homeQuarterScores:[14,21,14,14],awayQuarterScores:[7,7,10,14],homeOvertimePoints:0,awayOvertimePoints:0,homeStats:{...stats},awayStats:{...stats}});
 for(const t of s.teams)t.seasonStats={season:2027,slot:0,stats:{...Object.fromEntries(Object.entries(stats).map(([k,v])=>[k,v*3])),WINS:t.wins,LOSSES:t.losses,TIES:0}};
 const off={PASSATTEMPTS:30,PASSCOMPLETED:24,PASSYARDS:350,PASSTDS:4,PASSINTS:0,PASSSACKED:2,RUSHATTEMPTS:10,RUSHYARDS:60,RUSHTDS:1,RECEIVECATCHES:0,RECEIVEYARDS:0,RECEIVETDS:0,RECEIVEYARDSAFTER:0};
 const definitions=[['q','QB','OffensiveStats',off],['r','HB','OffensiveStats',{...off,PASSATTEMPTS:0,PASSCOMPLETED:0,PASSYARDS:0,PASSTDS:0,RUSHATTEMPTS:20,RUSHYARDS:130,RUSHTDS:4}],['w','WR','OffensiveStats',{...off,PASSATTEMPTS:0,PASSCOMPLETED:0,PASSYARDS:0,PASSTDS:0,RUSHATTEMPTS:0,RUSHYARDS:0,RUSHTDS:0,RECEIVECATCHES:10,RECEIVEYARDS:230,RECEIVETDS:2,RECEIVEYARDSAFTER:100}],['d','MLB','DefensiveStats',{DLINESACKS:1,DLINEHALFSACK:1,DSECINTS:1,DEFTACKLES:12,ASSDEFTACKLES:5,DEFTACKLESFORLOSS:4,DLINEFORCEDFUMBLES:1,DEFPASSDEFLECTIONS:3}],['k','K','KickingStats',{KICKFGATTEMPTS:4,KICKFGMADE:4,KICKFGATTEMPTS50ORMORE:2,KICKFGMADE50ORMORE:2,PUNTATTEMPTS:6,PUNTNETYARDS:270}]];
 for(const [id,position,type,st] of definitions){const totals=Object.fromEntries(Object.entries(st).map(([k,v])=>[k,v*3]));if(id==='d'){totals.DLINESACKS=4;totals.DLINEHALFSACK=1;}s.players.push({id,name:'Evan '+id.toUpperCase(),team:1,position,personality:'Leader',classYear:'Freshman',injury:'Uninjured',seasonStats:[{type:'Season'+type,stats:{...totals,GAMESPLAYED:3}}]});for(const g of s.games)s.performances.push({player:id,team:1,game:g.id,type:'Game'+type,stats:{...st}});}
 return s;
}
test('at least 15 distinct team and 15 player scenarios are executable against corroborated native-shaped stats',()=>{
 assert.ok(TEAM_SCENARIOS.length>=15&&PLAYER_SCENARIOS.length>=15);const s=fixture(),a=advancedAnalytics(s,{bounded:false});
 assert.ok(new Set(a.filter(x=>!x.player).map(x=>x.key)).size>=15);assert.ok(new Set(a.filter(x=>x.player).map(x=>x.key)).size>=15);
 assert.equal(a.find(x=>x.key==='rushing-yards-per-carry'&&x.player==='r').values.value,'6.5');assert.equal(a.find(x=>x.key==='catch-share').values.value,'41.7');
 assert.equal(a.find(x=>x.key==='sacks-leader').values.value,'4.5');assert.equal(a.find(x=>x.key==='field-goals').values.value,'100.0');
});
test('unknown or mismatching player totals cannot produce false national/conference leaders',()=>{
 const s=fixture();s.players[0].seasonStats[0].stats.PASSYARDS=9999;const a=advancedAnalytics(s,{bounded:false});assert.ok(!a.some(x=>x.key==='passing-yards-leader'));assert.ok(!a.some(x=>x.key==='passing-yards-per-attempt'&&x.player==='q'));
});
test('incomplete team denominators suppress the measure instead of treating missing stats as zero',()=>{
 const s=fixture();delete s.games[0].homeStats.OFFREDZONEFGS;const a=advancedAnalytics(s,{bounded:false});assert.ok(!a.some(x=>x.team===1&&x.key==='red-zone-field-goals'));assert.ok(a.some(x=>x.team===1&&x.key==='scoring-margin'));
});
test('players with positive native totals but missing all game caches cannot be omitted from leader comparisons',()=>{
 const s=fixture();s.performances=s.performances.filter(p=>p.player!=='q');assert.ok(!advancedAnalytics(s,{bounded:false}).some(x=>x.key==='passing-yards-leader'));
});
test('an observed broken record stays in its publication week across unrelated refreshes',()=>{
 const s=fixture(),record={id:'rec',scope:'school',scopeId:1,period:'game',metric:'PassYards',value:300,year:2026,team:1,playerName:'Evan Q'};s.records=[record];const a=updateRuntime(structuredClone(s));s.records=[{...record,value:350,year:2027}];const b=updateRuntime(structuredClone(s),a.state),c=updateRuntime(structuredClone(s),b.state);assert.ok(b.catalog.stories.some(p=>p.templateId.startsWith('world.record_broken')));assert.deepEqual(b.catalog,c.catalog);
});
test('CPU and user team choice have identical event eligibility and advanced selectors',()=>{
 const s=fixture(),a=buildFeed(s);s.userTeamIndex=2;const b=buildFeed(s);assert.deepEqual(a.events.map(e=>e.id).sort(),b.events.map(e=>e.id).sort());assert.deepEqual(advancedAnalytics({...s,userTeamIndex:1}),advancedAnalytics(s));
});
test('weekly awards require a published matching performance and do not leak future winners',()=>{
 const s=fixture();s.weeklyAwards=[{id:'award',type:'Offensive_Player_of_Week',week:3,player:'q',team:1}];assert.ok(worldEvents(s).some(x=>x.category==='awards'));s.games[2].published=false;assert.ok(!worldEvents(s).some(x=>x.category==='awards'));
});
test('upsets use the prior-week poll or captured pregame line rather than the updated poll',()=>{
 const s=fixture();s.teams[0].mediaLastRank=99;s.teams[1].mediaLastRank=3;const upset=worldEvents(s).find(x=>x.category==='upsets');assert.equal(upset.facts.winnerLabel,'Unranked Harbor');assert.equal(upset.facts.loserLabel,'#3 Mesa');assert.equal(upset.facts.huge,true);
 s.teams[0].mediaLastRank=1;s.teams[1].mediaLastRank=99;assert.ok(!worldEvents(s).some(x=>x.category==='upsets'));
});
test('school records need matching published production; broken versus existing-holder language is distinguished',()=>{
 const s=fixture(),record={id:'rec',scope:'school',scopeId:1,period:'game',metric:'PassYards',value:350,year:2027,team:1,playerName:'Evan Q'};s.records=[record];assert.equal(worldEvents(s).find(x=>x.category==='records').facts.family,'world.record_holder');s.recordBaseline=[{...record,value:300,year:2026}];assert.equal(worldEvents(s).find(x=>x.category==='records').facts.family,'world.record_broken');s.recordBaseline=[record];assert.ok(!worldEvents(s).some(x=>x.category==='records'));s.records[0].value=351;assert.ok(!worldEvents(s).some(x=>x.category==='records'));
});
test('recruit significance follows school prestige while every five-star and national No. 1 remains major',()=>{
 assert.equal(recruitSignificance(4,1,100),'program-changer');assert.equal(recruitSignificance(5,5,10),'five-star');assert.equal(recruitSignificance(3,5,500),'normal');assert.equal(recruitSignificance(4,5,100),'normal');assert.equal(recruitSignificance(2,5,1000),'questioned');assert.equal(recruitSignificance(5,5,1),'number-one');
 const s=fixture();s.userTeamIndex=2;s.players.push({id:'recruit',name:'Trey Moss',team:255,position:'QB',personality:'Leader',starRating:5});s.commitments=[{player:'recruit',team:1,rank:1,stage:'HardCommitted',week:3}];const f=buildFeed(s);assert.ok(f.stories.some(p=>p.voice==='fan'&&p.templateId.startsWith('reply.fan.recruit_number_one')));assert.ok(f.stories.some(p=>p.templateId.startsWith('beat.recruit_pickup')&&p.body.includes('5-star')));
});
test('elite-program low-star pickups get beat scrutiny and soft five-star commitments get a major fan response',()=>{
 const s=fixture();s.teams[0].prestigeStars=5;s.players.push({id:'recruit',name:'Trey Moss',team:255,position:'QB',personality:'Leader',starRating:2});s.commitments=[{player:'recruit',team:1,rank:1000,stage:'HardCommitted',week:3}];let f=buildFeed(s);assert.ok(f.stories.some(p=>p.templateId.startsWith('beat.recruit_questioned')));assert.ok(f.stories.some(p=>p.templateId.startsWith('reply.fan.recruit_questioned')));
 s.players.at(-1).starRating=5;s.commitments[0].stage='SoftCommitted';s.commitments[0].rank=1;f=buildFeed(s);assert.ok(f.stories.some(p=>p.templateId.startsWith('reply.fan.recruit_number_one')));assert.ok(!f.stories.some(p=>p.templateId.startsWith('reply.player.offer')));
});
test('midweek flips and reopened recruitments persist, while Signed is not mistaken for decommitting',()=>{
 const s=fixture();s.players.push({id:'recruit',name:'Trey Moss',team:255,position:'QB',personality:'Leader',starRating:5});s.commitments=[{player:'recruit',team:1,rank:10,stage:'HardCommitted',week:2}];s.recruitStatuses=[{player:'recruit',stage:'HardCommitted'}];const a=updateRuntime(structuredClone(s));s.commitments[0].team=2;const b=updateRuntime(structuredClone(s),a.state),c=updateRuntime(structuredClone(s),b.state);assert.ok(b.catalog.stories.some(p=>p.templateId.startsWith('world.flip')));assert.ok(b.catalog.stories.some(p=>p.templateId.startsWith('reply.fan.flip')));assert.deepEqual(b.catalog,c.catalog);
 s.commitments=[];s.recruitStatuses[0].stage='Signed';assert.ok(!updateRuntime(structuredClone(s),a.state).catalog.stories.some(p=>p.templateId.startsWith('world.decommit')));s.recruitStatuses[0].stage='Top5';assert.ok(updateRuntime(structuredClone(s),a.state).catalog.stories.some(p=>p.templateId.startsWith('world.decommit')));
});
test('approved rivalry steals, undefeated collisions and upset bounce-back previews use verified conditions',()=>{
 let s=fixture();s.players.push({id:'recruit',name:'Trey Moss',team:255,position:'QB',starRating:4});s.teams[0].rivals=[2];s.commitmentChanges=[{player:'recruit',from:1,to:2}];assert.ok(worldEvents(s).some(e=>e.facts.family==='world.rivalry_flip'));
 s.teams[0].mediaLastRank=99;s.games.push({id:'next',year:1,week:4,phase:'RegularSeason',status:'Unplayed',home:2,away:1});assert.ok(worldEvents(s).some(e=>e.facts.family==='world.bounceback'&&e.facts.school==='Mesa'));
 s=fixture();s.teams[1].wins=3;s.teams[1].losses=0;s.games=[];for(let i=1;i<=3;i++)for(const team of [1,2])s.games.push({id:`${team}-${i}`,year:1,week:i,phase:'RegularSeason',published:true,status:'HomeWon',home:team,away:team+2,homeScore:21,awayScore:7});s.games.push({id:'collision',year:1,week:4,phase:'RegularSeason',status:'Unplayed',home:1,away:2});assert.ok(worldEvents(s).some(e=>e.facts.family==='world.undefeated'));s.teams[1].wins=4;assert.ok(!worldEvents(s).some(e=>e.facts.family==='world.undefeated'));
});
test('the stronger spread model separates mismatches, handles neutral equals and never invents missing rosters',()=>{
 const s=fixture();s.players=[];for(const id of [1,2])for(const position of ['QB','HB','FB','WR','TE','LT','LG','C','RG','RT','DT','LE','RE','MLB','LOLB','ROLB','CB','FS','SS','K','P'])s.players.push({team:id,position,overall:id===1?92:60,injury:'Uninjured'});const game={home:1,away:2};const line=projectLine(s,game);assert.ok(line.spread>=30&&line.spread<=45);assert.equal(line.favorite,1);s.players.forEach(p=>p.overall=80);assert.equal(projectLine(s,{...game,neutral:true}).spread,0);assert.equal(projectLine({...s,players:s.players.filter(p=>p.team===1)},game),null);
});
test('engagement caps and 1–20 percent reply likes are stable; old large counts migrate once',()=>{
 const s=fixture(),t={brandExposure:'Aplus',mediaRank:1};for(let i=0;i<200;i++){const id='post'+i,normal=likesFor(s,id,'official',t,{facts:{},scopes:['national']}),major=likesFor(s,id,'official',t,{facts:{importance:'major'},scopes:['national']});assert.ok(normal<=5000&&major<=10000);const reply=replyLikesFor(s,id,normal);assert.ok(reply>=Math.floor(normal*.01)&&reply<=Math.floor(normal*.2));assert.equal(replyLikesFor(s,id,normal,{likes:99999,engagementVersion:2}),reply);assert.equal(likesFor(s,id,'official',t,{facts:{},scopes:[]},{likes:99999}),normal);assert.equal(likesFor(s,id,'fan',{}, {facts:{},scopes:[]},{likes:normal,engagementVersion:ENGAGEMENT_VERSION}),normal);}
});
