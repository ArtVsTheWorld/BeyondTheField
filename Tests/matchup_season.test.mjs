import test from 'node:test';import assert from 'node:assert/strict';
import {cleanLanguage,cleanFeedLanguage} from '../Tools/clean_language.mjs';
import {seasonEndings,seasonEndingEvents,seedSeasonEndPublications,recruitingClassRanks} from '../Tools/season_ending_events.mjs';
import {matchupEvents} from '../Tools/matchup_events.mjs';import {fanAccountEvents} from '../Tools/fan_events.mjs';
import {lateSeasonEvents} from '../Tools/late_season_events.mjs';import {updateRuntime} from '../Tools/runtime_lifecycle.mjs';
import {buildFeed} from '../Tools/feed_engine.mjs';import {hash} from '../Tools/story_authors.mjs';
import {contentPack} from '../Tools/story_templates.mjs';import {filterConversations} from '../Tools/social_discovery.mjs';
const fixture=(wins=0)=>{
 const s={format:2,gameYear:27,sourceKind:'runtime',source:'runtime:7:1',sourceUnchanged:true,sha256:'a'.repeat(64),leagueId:7,userTeamIndex:1,season:{CurrentYear:0,CurrentSeasonYear:2026,CurrentWeek:15,CurrentWeekType:'RegularSeason',CurrentStage:'NFLSeason',RegularSeasonWeekConferenceChampionship:15},teams:[{id:1,name:'Harbor',nickname:'Hawks',logo:1,mediaRank:1,wins,losses:12-wins,ties:0,rivals:[2],conferenceId:'c',conferenceName:'Coastal',headCoach:{name:'Amir Cole',lastName:'Cole',jobSecurity:'Safe'},offensiveCoordinator:{name:'Ty West'},defensiveCoordinator:{name:'Mo Reed'}},{id:2,name:'Valley',nickname:'Bears',logo:2,mediaRank:2,wins:12-wins,losses:wins,ties:0,rivals:[1],conferenceId:'c',conferenceName:'Coastal'}],conferences:[{id:'c',name:'Coastal',teams:[1,2],championshipType:'TOPTEAMS'}],players:[{id:'senior',name:'Evan Moss',firstName:'Evan',lastName:'Moss',team:1,position:'QB',portrait:146,injury:'Uninjured',classYear:'Senior',redshirt:'Previous',seasonStats:[]}],games:[],performances:[],offers:[],commitments:[],heisman:[],records:[]};
 s.games=Array.from({length:12},(_,i)=>({id:'g'+i,year:0,week:i,phase:'RegularSeason',home:1,away:2,status:i<wins?'HomeWon':'AwayWon',published:true,homeScore:i<wins?30:7,awayScore:i<wins?7:30}));return s;
};
const bowl=(s,{playoff=false,title=false,win=true}={})=>{s.games.push({id:'bowl',year:0,week:17,phase:title?'NationalChampionship':'BowlSeason1',home:1,away:2,status:win?'HomeWon':'AwayWon',published:true,homeScore:win?31:10,awayScore:win?10:31,isPlayoff:playoff,bowlName:'Test Bowl'});s.season.CurrentWeekType=title?'NationalChampionship':'BowlSeason1';s.season.CurrentWeek=17;s.teams[win?0:1].wins++;s.teams[win?1:0].losses++;};

test('clean language replaces profanity without damaging names, handles or punctuation',()=>{
 assert.equal(cleanLanguage('That shit was fucking wild. DAMN!'),'That trash was fricking wild. DANG!');assert.equal(cleanLanguage('hell, bullshit and pissed'),'heck, nonsense and ticked off');assert.equal(cleanLanguage('Massachusetts, Dickerson, Shittu and @shit'),'Massachusetts, Dickerson, Shittu and @shit');
 const feed={stories:[{id:'a',body:'talk shit',likes:22,handle:'@h'}],views:{all:['a']}};const result=cleanFeedLanguage(feed);assert.equal(result.stories[0].body,'talk trash');assert.equal(result.posts[0].likes,22);assert.equal(feed.stories[0].body,'talk shit');
});
test('every runtime template is clean, including the retired wording in the original pack',()=>{
 for(const variants of Object.values(contentPack.families))for(const t of variants)assert.equal(cleanLanguage(t.body),t.body,t.id);
});
test('a winless regular season receives appropriate team, fan, player and media wrapups',()=>{
 const s=fixture(),ended=seasonEndings(s);assert.equal(ended.get(1).winless,true);assert.ok(!ended.has(2));const e=seasonEndingEvents(s).filter(e=>e.options.team===1);for(const role of ['official','fan','player','analyst'])assert.ok(e.some(e=>e.facts.voice===role),role);assert.ok(!e.some(e=>e.facts.family.includes('perfect')));const f=buildFeed(s);assert.ok(f.stories.some(p=>p.author==='Barstool Harbor'&&p.category==='season-end'));assert.ok(f.stories.some(p=>p.author==='Harbor After Dark'&&p.category==='season-end'));assert.ok(f.stories.some(p=>p.voice==='player'&&p.body.includes('senior')));
});
test('bowl-eligible teams with no assigned games wait for selection; regular unbeaten teams do not declare a perfect full season',()=>{
 const s=fixture(6);assert.equal(seasonEndings(s).size,0);s.season.CurrentWeek=14;assert.equal(seasonEndings(s).size,0);const unbeaten=fixture(12);assert.ok(!seasonEndings(unbeaten).has(1));assert.ok(!seasonEndingEvents(unbeaten).some(e=>e.options.team===1&&e.facts.family.includes('perfect')));
});
test('five-win teams remain pending during championship week and nonselected teams close by the title phase',()=>{
 const s=fixture(5);assert.ok(!seasonEndings(s).has(1));s.season.CurrentWeekType='BowlSeason1';s.season.CurrentWeek=17;assert.ok(seasonEndings(s).has(1));const other=fixture(6);other.season.CurrentWeekType='NationalChampionship';other.season.CurrentWeek=20;assert.ok(seasonEndings(other).has(1));
});
test('ordinary bowl completion and playoff elimination finish a season; playoff advancement does not',()=>{
 let s=fixture(6);bowl(s);assert.ok(seasonEndings(s).has(1)&&seasonEndings(s).has(2));s=fixture(12);bowl(s,{playoff:true});assert.ok(!seasonEndings(s).has(1));assert.ok(seasonEndings(s).has(2));s=fixture(12);bowl(s,{playoff:true,title:true});assert.equal(seasonEndings(s).get(1).undefeated,true);assert.ok(seasonEndingEvents(s).some(e=>e.options.team===1&&e.facts.family==='ending.team.perfect'));
});
test('unpublished results, missing games and future assigned fixtures prevent premature season endings',()=>{
 let s=fixture();s.games[0].published=false;assert.equal(seasonEndings(s).size,0);s=fixture();s.games.pop();assert.equal(seasonEndings(s).size,0);s=fixture();s.games.push({id:'future',year:0,week:17,phase:'BowlSeason1',home:1,away:2,status:'Unplayed',bowlName:'Bowl'});assert.equal(seasonEndings(s).size,0);
});
test('end-of-season editions persist on refresh but do not republish each subsequent week or phase',()=>{
 const s=fixture(),first=updateRuntime(structuredClone(s));assert.ok(first.catalog.stories.some(p=>p.category==='season-end'));const repeat=updateRuntime(structuredClone(s),first.state);assert.deepEqual(repeat.catalog.stories,first.catalog.stories);s.season.CurrentWeek=16;const next=updateRuntime(structuredClone(s),first.state);assert.ok(!next.catalog.stories.some(p=>p.category==='season-end'));s.season.CurrentWeekType='BowlSeason1';s.season.CurrentWeek=17;seedSeasonEndPublications(s,first.state.editions[0].snapshot.seasonEndPublications);assert.ok(!seasonEndingEvents(s).some(e=>e.options.team===1));
});
test('restoring unfinished play clears a stale end ledger, and a later real finish can publish',()=>{
 const s=fixture(),ledger=seedSeasonEndPublications(s);s.games[11].status='Unplayed';s.teams[0].losses--;s.teams[1].wins--;assert.deepEqual(seedSeasonEndPublications(s,ledger),{});s.games[11].status='AwayWon';s.teams[0].losses++;s.teams[1].wins++;s.season.CurrentWeek++;assert.equal(seedSeasonEndPublications(s,{} )[1],'RegularSeason/16');
});
test('coach pressure uses native status; poor-season accountability names the appropriate coordinator',()=>{
 const s=fixture();let e=seasonEndingEvents(s);assert.ok(!e.some(e=>e.facts.family==='ending.coach-pressure'));assert.equal(e.find(e=>e.options.team===1&&e.facts.family==='ending.fan-accountability').facts.coachName,'Ty West');s.teams[0].headCoach.jobSecurity='HotSeat';assert.ok(seasonEndingEvents(s).some(e=>e.facts.family==='ending.coach-pressure'&&e.facts.coachName==='Amir Cole'));
});
test('native recruiting-class rankings need distinct populated rows and never rank from stars',()=>{
 const s=fixture();s.commitments=[{team:1,player:'a'},{team:2,player:'b'}];s.teams[0].nativeRecruitingRank=0;s.teams[1].nativeRecruitingRank=1;assert.equal(recruitingClassRanks(s).get(1),1);s.teams[1].nativeRecruitingRank=0;assert.equal(recruitingClassRanks(s).size,0);
});
test('Week 15 uses fresh championship-week hype, with no repeated Week 14 invitation family',()=>{
 const s=fixture(6);s.games.push({id:'title',year:0,week:15,phase:'RegularSeason',home:1,away:2,status:'Unplayed'});s.season.CurrentWeek=14;assert.ok(lateSeasonEvents(s).some(e=>e.facts.family==='late.title-invite'));s.season.CurrentWeek=15;const e=lateSeasonEvents(s);assert.ok(!e.some(e=>e.facts.family==='late.title-invite'||e.facts.family==='late.title-history'));assert.ok(e.some(e=>e.facts.family==='late.title-week'));
});
test('Barstool independently posts as Fans, stays clean and does not celebrate a loss',()=>{
 const s=fixture();s.season.CurrentWeek=12;const events=fanAccountEvents(s);assert.ok(events.length);assert.ok(events.every(e=>e.facts.persona===1&&e.facts.voice==='fan'));assert.ok(events.filter(e=>e.options.team===1).every(e=>/loss/.test(e.facts.family)));const posts=buildFeed(s).stories.filter(p=>p.eventId.startsWith('barstool:'));assert.ok(posts.some(p=>p.author==='Barstool Harbor'));assert.ok(posts.every(p=>p.voice==='fan'&&cleanLanguage(p.body)===p.body));
});
function matchupFixture(recap=false){
 const s=fixture(6);s.games=s.games.slice(0,4);s.season.CurrentWeek=4;s.teams[0].wins=4;s.teams[0].losses=0;s.teams[1].wins=0;s.teams[1].losses=4;
 const cache=(yards=100)=>({OFFPASSYARDS:yards,DEFPASSYARDS:100,OFFRUSHYARDS:100,DEFRUSHYARDS:100,SACKSALLOWED:1,SACKS:1});
 for(const g of s.games){g.status='HomeWon';g.homeScore=30;g.awayScore=7;g.homeStats=cache();g.awayStats=cache();}
 let id='target';for(let i=0;;i++){id='target'+i;if(hash(id+'|matchup-angle')%3===0&&hash(id+'|matchup-side')%2===0)break;}
 const g={id,year:0,week:4,phase:'RegularSeason',home:1,away:2,status:recap?'HomeWon':'Unplayed',published:recap,homeScore:recap?35:0,awayScore:recap?7:0,homeStats:cache(250),awayStats:cache()};s.games.push(g);
 if(recap){s.teams[0].wins++;s.teams[1].losses++;}
 s.players=[{id:'wr',name:'Trey Miles',team:1,position:'WR',portrait:146,injury:'Uninjured',seasonStats:[]},{id:'db',name:'Noah Reed',team:2,position:'CB',portrait:147,injury:'Uninjured',seasonStats:[]}];
 for(const p of s.players){const games=s.games.filter(g=>g.status==='HomeWon'),off=p.id==='wr',stats=off?{RECEIVECATCHES:games.length*5,RECEIVEYARDS:games.length*100}:{DEFPASSDEFLECTIONS:games.length*2,DSECINTS:0};p.seasonStats=[{type:off?'SeasonOffensiveStats':'SeasonDefensiveStats',stats:{GAMESPLAYED:games.length,...stats}}];for(const x of games)s.performances.push({player:p.id,team:p.team,game:x.id,type:off?'GameOffensiveStats':'GameDefensiveStats',stats:off?{RECEIVECATCHES:5,RECEIVEYARDS:100}:{DEFPASSDEFLECTIONS:2,DSECINTS:0}});}
 return s;
}
test('opponent previews compare verified entering units and receiver/secondary production',()=>{
 const s=matchupFixture(),e=matchupEvents(s,{force:true});const a=e.find(e=>e.facts.family==='matchup.passing-preview');assert.equal(a.facts.attack,'100.0');assert.equal(a.facts.defense,'100.0');assert.ok(e.some(e=>e.facts.receiver==='Trey Miles'&&e.facts.defender==='Noah Reed'));s.games[0].homeStats.OFFPASSYARDS=undefined;assert.ok(!matchupEvents(s,{force:true}).some(e=>e.facts.family==='matchup.passing-preview'));
});
test('recaps exclude their own game from entering averages and report independent opposing player lines',()=>{
 const s=matchupFixture(true),e=matchupEvents(s,{force:true}),a=e.find(e=>e.facts.family==='matchup.passing-recap');assert.equal(a.facts.attack,'100.0');assert.equal(a.facts.actual,250);assert.ok(e.some(e=>e.facts.family==='matchup.receiver-secondary-recap'&&e.facts.actualYards===100&&e.facts.actualBreakups===2));s.performances.push(s.performances[0]);assert.ok(!matchupEvents(s,{force:true}).some(e=>e.facts.receiver==='Trey Miles'));
});
test('per-attempt matchups use the opposing offense attempts as the defense denominator',()=>{
 const s=matchupFixture(true);for(const g of s.games){g.homeStats.PASSATTEMPTS=25;g.awayStats.PASSATTEMPTS=50;}const e=matchupEvents(s,{force:true}).find(e=>e.facts.family==='matchup.passing-recap-rates');assert.equal(e.facts.attackRate,'4.0');assert.equal(e.facts.defenseRate,'4.0');assert.equal(e.facts.actualRate,'10.0');
});
test('cleaning archives preserves publication, order, likes and account identity',()=>{
 const feed={key:'week-old',stories:[{id:'a',body:'what the hell',handle:'@a',likes:21,publication:{week:3}},{id:'b',replyTo:'a',body:'damn right',likes:2}],views:{all:['a','b']}};const f=cleanFeedLanguage(feed);assert.equal(f.key,feed.key);assert.deepEqual(f.views,feed.views);assert.deepEqual(f.stories[0].publication,feed.stories[0].publication);assert.equal(f.stories[0].likes,21);assert.equal(f.stories[1].likes,2);assert.equal(f.stories[1].replyTo,'a');
});
test('matchup/season reviews participate in the right category filters, retaining replies',()=>{
 assert.equal(filterConversations([{id:'a',category:'matchup-preview'}],'upcoming').length,1);assert.equal(filterConversations([{id:'a',category:'matchup-recap'},{id:'b',category:'season-end'},{id:'r',replyTo:'b',voice:'fan'}],'recaps').length,3);
});
