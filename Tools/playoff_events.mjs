import {publicPoll} from './public_polls.mjs';
import {phaseIndex} from './publication_timeline.mjs';
const ranked=n=>Number.isInteger(n)&&n>=1&&n<=25;
const complete=g=>g.published!==false&&Number.isFinite(g.homeScore)&&Number.isFinite(g.awayScore)&&g.homeScore>=0&&g.awayScore>=0&&(g.status==='HomeWon'&&g.homeScore>g.awayScore||g.status==='AwayWon'&&g.awayScore>g.homeScore);
const rounds=new Set(['FirstRound','Quarterfinals','Semifinals','NationalChampionship','WonNationalChampionship']);
export function playoffEvents(s,previous=null){
 const poll=publicPoll(s),phase=s.season.CurrentWeekType,week=s.season.CurrentWeek;
 if(s.season.CurrentStage!=='NFLSeason'||poll.key!=='cfp'&&!['BowlSeason1','BowlSeason2','BowlSeason3','NationalChampionship'].includes(phase))return [];
 const teams=new Map(s.teams.filter(t=>t.id!==255).map(t=>[t.id,t])),events=[];
 const emit=(id,family,voice,values,team,options={})=>events.push({id:'playoff:'+id,category:'cfp',facts:{family:'playoff.'+family,voice,...values},options:{team:team?.id,national:true,priority:options.priority??91,...options}});
 const actual=s.games.filter(g=>g.year===s.season.CurrentYear&&teams.has(g.home)&&teams.has(g.away)&&g.home!==g.away);
 const isPlayoff=g=>['BowlSeason1','BowlSeason2','BowlSeason3','NationalChampionship'].includes(g.phase)&&(g.isPlayoff===true||g.phase==='NationalChampionship'||g.phase==='BowlSeason1'&&!g.bowlName&&rounds.has(teams.get(g.home)?.playoffRound)&&rounds.has(teams.get(g.away)?.playoffRound));
 const notFuture=g=>phaseIndex(g.phase)<phaseIndex(phase)||g.phase===phase&&g.week<=week;
 const completed=actual.filter(g=>isPlayoff(g)&&complete(g)&&notFuture(g));
 const championship=completed.find(g=>g.phase==='NationalChampionship');
 const first=phase==='RegularSeason'&&week===10;
 if(!championship&&phase==='RegularSeason'){
  for(const t of [...teams.values()].filter(t=>ranked(t.cfpRank)).sort((a,b)=>a.cfpRank-b.cfpRank)){
   const old=!first&&poll.comparable&&ranked(t.cfpLastRank)?t.cfpLastRank:null;
   if(t.cfpRank<=3)emit('rank:'+t.id,first?'first_rank':old&&old!==t.cfpRank?'rank_move':'rank','cfp',{school:t.name,rank:t.cfpRank,previousRank:old,movement:old>t.cfpRank?'up':'down',places:old?Math.abs(old-t.cfpRank):0},t,{priority:98-t.cfpRank});
   else if(old&&old!==t.cfpRank&&(t.cfpRank<=16||old<=12||Math.abs(old-t.cfpRank)>=3))emit('rank:'+t.id,'rank_move','cfp',{school:t.name,rank:t.cfpRank,previousRank:old,movement:old>t.cfpRank?'up':'down',places:Math.abs(old-t.cfpRank)},t);
   if(phase==='RegularSeason'&&t.cfpRank<=16){
    emit('picture:'+t.id,t.cfpRank<=8?'position':'bubble','analyst',{school:t.name,rank:t.cfpRank,analystPersona:t.cfpRank<=3?1:t.cfpRank<=8?2:3},t,{priority:t.cfpRank<=8?92:89});
    emit('local:'+t.id,'local','beat',{school:t.name,rank:t.cfpRank},t,{national:false,priority:85});
    // Fans react to position, not a fabricated invitation or guaranteed berth.
    emit('fan:'+t.id,t.cfpRank<=8?'fan_position':'fan_bubble','fan',{school:t.name,rank:t.cfpRank},t,{national:false,priority:80});
   }
  }
 }
 for(const g of actual.filter(g=>isPlayoff(g)&&g.status==='Unplayed'&&g.phase===phase&&g.week===week)){
  const home=teams.get(g.home),away=teams.get(g.away);
  emit('preview:'+g.id,g.phase==='NationalChampionship'?'title_preview':'preview','cfp',{home:home.name,away:away.name,venue:g.bowlName??'the College Football Playoff',importance:'major'},home,{relatedTeams:[away.id],thread:'game:'+g.id,priority:110,eventWeek:g.week});
  emit('matchup:'+g.id,'matchup','analyst',{home:home.name,away:away.name,homeRank:ranked(home.cfpRank)?home.cfpRank:null,awayRank:ranked(away.cfpRank)?away.cfpRank:null,analystPersona:4},home,{relatedTeams:[away.id],thread:'game:'+g.id,priority:96});
 }
 // Carry the latest completed playoff round into the next edition. Earlier
 // round reports remain in their actual stored editions, not every later feed.
 const latest=completed.sort((a,b)=>phaseIndex(b.phase)-phaseIndex(a.phase)||b.week-a.week)[0];
 for(const g of completed.filter(g=>g.phase===latest?.phase&&g.week===latest.week)){
  const win=teams.get(g.homeScore>g.awayScore?g.home:g.away),lose=teams.get(g.homeScore>g.awayScore?g.away:g.home),score=Math.max(g.homeScore,g.awayScore)+'\u2013'+Math.min(g.homeScore,g.awayScore),title=g.phase==='NationalChampionship';
  emit('result:'+g.id,title?'champion':'result','cfp',{school:win.name,opponent:lose.name,score,importance:'major'},win,{relatedTeams:[lose.id],thread:'game:'+g.id,priority:title?135:115,eventWeek:g.week});
  emit('result-reaction:'+g.id,title?'champion_analysis':'result_analysis','analyst',{school:win.name,opponent:lose.name,score,analystPersona:title?1:2},win,{relatedTeams:[lose.id],thread:'game:'+g.id,priority:99});
  emit('result-fan:'+g.id,title?'champion_fan':'result_fan','fan',{school:win.name,opponent:lose.name,score},win,{relatedTeams:[lose.id],thread:'game:'+g.id,national:false,priority:90});
 }
 return events;
}
