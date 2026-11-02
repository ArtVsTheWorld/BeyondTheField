import test from 'node:test';
import assert from 'node:assert/strict';
import {teamAnalytics} from '../Tools/team_analytics.mjs';
function fixture(){return {season:{CurrentYear:1,CurrentWeek:4,CurrentWeekType:'RegularSeason',CurrentStage:'NFLSeason'},teams:[{id:1,name:'A',wins:2,losses:1,ties:0},{id:2,name:'B',wins:1,losses:2,ties:0},{id:255,name:'Generic FCS'}],conferences:[{teams:[1,2]}],games:[
 {id:'a',year:1,week:1,phase:'RegularSeason',status:'HomeWon',home:1,away:2,homeScore:49,awayScore:7,homeStats:{OFFRUSHYARDS:100,THIRDDOWNCONV:1,THIRDDOWNS:2,GIVEAWAYS:1,TAKEAWAYS:3},awayStats:{OFFRUSHYARDS:50,THIRDDOWNCONV:1,THIRDDOWNS:4,GIVEAWAYS:3,TAKEAWAYS:1}},
 {id:'b',year:1,week:2,phase:'RegularSeason',status:'AwayWon',home:1,away:2,homeScore:10,awayScore:20,homeStats:{OFFRUSHYARDS:200,THIRDDOWNCONV:1,THIRDDOWNS:8,GIVEAWAYS:1,TAKEAWAYS:2},awayStats:{OFFRUSHYARDS:80,THIRDDOWNCONV:3,THIRDDOWNS:6,GIVEAWAYS:2,TAKEAWAYS:1}},
 {id:'c',year:1,week:3,phase:'RegularSeason',status:'HomeWon',home:1,away:2,homeScore:21,awayScore:14,homeStats:{OFFRUSHYARDS:300,THIRDDOWNCONV:0,THIRDDOWNS:0,GIVEAWAYS:0,TAKEAWAYS:2},awayStats:{OFFRUSHYARDS:110,THIRDDOWNCONV:2,THIRDDOWNS:4,GIVEAWAYS:2,TAKEAWAYS:0}}
]};}
test('season analytics sum real denominators, retain sample size, and identify the national field',()=>{
 const a=teamAnalytics(fixture()),r=a.teams.find(t=>t.teamId===1);assert.equal(r.gamesPlayed,3);assert.equal(r.rushingYardsPerGame,200);assert.equal(r.rushingRank,1);assert.equal(r.thirdDownConversions,2);assert.equal(r.thirdDownAttempts,10);assert.equal(r.thirdDownRate,.2);assert.notEqual(r.thirdDownRate,(.5+.125)/2);assert.equal(r.turnoverMargin,5);assert.equal(a.coverage.populationSize,2);assert.equal(a.coverage.rushingCoverageComplete,true);
});
test('missing stat caches suppress that measure rather than treating missing games as zero',()=>{
 const s=fixture();s.games[1].homeStats=null;const a=teamAnalytics(s),r=a.teams.find(t=>t.teamId===1);assert.equal(r.rushingYardsPerGame,null);assert.equal(r.thirdDownRate,null);assert.equal(r.rushingRank,null);assert.equal(a.coverage.rushingCoverageComplete,false);
});
test('zero attempts have no percentage, and inconsistent counts do not become rates',()=>{
 const s=fixture();for(const g of s.games){g.homeStats.THIRDDOWNCONV=0;g.homeStats.THIRDDOWNS=0;}assert.equal(teamAnalytics(s).teams.find(t=>t.teamId===1).thirdDownRate,null);
 s.games[0].homeStats.THIRDDOWNCONV=3;s.games[0].homeStats.THIRDDOWNS=2;assert.equal(teamAnalytics(s).teams.find(t=>t.teamId===1).thirdDownRate,null);
});
test('national ranking requires known membership and game coverage matching official records',()=>{
 const s=fixture();s.teams.push({id:3,name:'C',wins:1,losses:0});s.conferences[0].teams.push(3);assert.equal(teamAnalytics(s).coverage.recordCoverageComplete,false);assert.ok(teamAnalytics(s).teams.every(t=>t.rushingRank===null));
 s.conferences=[];assert.equal(teamAnalytics(s).coverage.nationalFieldKnown,false);
});
test('ties use competition ranks computed before display rounding',()=>{
 const s=fixture();for(const g of s.games)g.awayStats.OFFRUSHYARDS=g.homeStats.OFFRUSHYARDS;const a=teamAnalytics(s);assert.ok(a.teams.every(t=>t.rushingRank===1&&t.rushingRankTied));
 s.games[2].awayStats.OFFRUSHYARDS+=1;const b=teamAnalytics(s);assert.equal(b.teams.find(t=>t.teamId===2).rushingRank,1);assert.equal(b.teams.find(t=>t.teamId===1).rushingRank,2);
});
test('season margin superlative uses actual results rather than a fixed threshold',()=>{
 const s=fixture();s.games[0].homeScore=44;const a=teamAnalytics(s);assert.equal(a.milestones.length,1);assert.equal(a.milestones[0].gameId,'a');assert.equal(a.milestones[0].kind,'season_largest_winning_margin');assert.equal(a.milestones[0].margin,37);assert.equal(a.milestones[0].threshold,undefined);
 s.games[1].awayScore=47;s.games[1].homeScore=10;assert.equal(teamAnalytics(s).milestones.length,0);
});
test('future, other-year, unpublished, and unfinished games do not become season superlatives',()=>{
 const s=fixture();s.games.push({...s.games[0],id:'future',week:5,homeScore:99},{...s.games[0],id:'old',year:0,homeScore:99},{...s.games[0],id:'hidden',week:4,published:false,homeScore:99});
 const a=teamAnalytics(s);assert.equal(a.teams.find(t=>t.teamId===1).gamesPlayed,3);assert.equal(a.milestones[0].gameId,'a');
 s.games.push({...s.games[0],id:'unknown-past',week:0,status:'Unplayed'});assert.equal(teamAnalytics(s).milestones.length,0);
});
test('current-first official season counters can corroborate metrics independently of stale game rows',()=>{
 const s=fixture();s.games.push({...s.games[0],id:'stale',week:0});
 s.teams[0].seasonStats={season:2027,slot:0,stats:{WINS:2,LOSSES:1,TIES:0,OFFRUSHYARDS:600,THIRDDOWNCONV:2,THIRDDOWNS:10,GIVEAWAYS:2,TAKEAWAYS:7}};
 s.teams[1].seasonStats={season:2027,slot:0,stats:{WINS:1,LOSSES:2,TIES:0,OFFRUSHYARDS:240,THIRDDOWNCONV:6,THIRDDOWNS:14,GIVEAWAYS:7,TAKEAWAYS:2}};
 s.season.CurrentSeasonYear=2027;const a=teamAnalytics(s),r=a.teams.find(t=>t.teamId===1);assert.equal(r.source,'currentSeasonStats');assert.equal(r.gamesPlayed,3);assert.equal(r.thirdDownRate,.2);assert.equal(r.rushingRank,1);assert.equal(a.coverage.recordCoverageComplete,false);assert.equal(a.milestones.length,0);
});
test('uncorroborated per-game totals are suppressed rather than becoming season claims',()=>{
 const s=fixture();s.teams[0].wins=4;const a=teamAnalytics(s),r=a.teams.find(t=>t.teamId===1);assert.equal(r.metricRecordMatches,false);assert.equal(r.thirdDownRate,null);assert.equal(r.rushingYardsPerGame,null);assert.equal(r.turnoverMargin,null);
});

test('published results corroborate current-season stats when a separate record table lags',()=>{
 const s=fixture();s.season.CurrentSeasonYear=2027;for(const g of s.games)g.published=true;
 s.teams[0].wins=1;s.teams[0].seasonStats={season:2027,slot:0,stats:{WINS:2,LOSSES:1,TIES:0,OFFRUSHYARDS:600,THIRDDOWNCONV:2,THIRDDOWNS:10,GIVEAWAYS:2,TAKEAWAYS:7,OFFREDZONES:25,OFFREDZONETDS:9}};
 const a=teamAnalytics(s),r=a.teams.find(t=>t.teamId===1);assert.equal(r.resultCountMatchesRecord,false);assert.equal(r.resultCorroborated,true);assert.equal(r.redZoneTouchdownRate,.36);assert.equal(r.rushingRank,1);
});
test('red-zone rates require valid trips and exclude field goals from touchdown rate',()=>{
 const s=fixture();for(const g of s.games){g.homeStats.OFFREDZONES=5;g.homeStats.OFFREDZONETDS=2;g.homeStats.OFFREDZONEFGS=1;}
 assert.equal(teamAnalytics(s).teams.find(t=>t.teamId===1).redZoneTouchdownRate,.4);s.games[1].homeStats.OFFREDZONETDS=6;assert.equal(teamAnalytics(s).teams.find(t=>t.teamId===1).redZoneTouchdownRate,null);
});

test('matching game count alone does not corroborate a conflicting win-loss record',()=>{
 const s=fixture();s.teams[0].wins=1;s.teams[0].losses=2;
 const a=teamAnalytics(s),r=a.teams.find(t=>t.teamId===1);assert.equal(r.resultCountMatchesRecord,true);assert.equal(r.resultRecordMatches,false);assert.equal(r.resultCorroborated,false);assert.equal(r.rushingYardsPerGame,null);assert.equal(a.coverage.recordCoverageComplete,false);
});
