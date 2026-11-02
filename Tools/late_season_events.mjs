import {publicPoll} from './public_polls.mjs';
import {lastHistoricalEvent} from './history_milestones.mjs';
const final=g=>g.published!==false&&['HomeWon','AwayWon','Tie'].includes(g.status);
const integer=n=>Number.isInteger(n)&&n>=0;
export function lateSeasonEvents(s){
 if(s.reconstructed||s.season.CurrentStage!=='NFLSeason')return [];
 const week=s.season.CurrentWeek,phase=s.season.CurrentWeekType,year=s.season.CurrentSeasonYear,regular=phase==='RegularSeason',poll=publicPoll(s);
 const teams=new Map(s.teams.filter(t=>t.id!==255).map(t=>[t.id,t])),events=[];
 const add=(id,family,voice,t,values={},options={})=>events.push({id:'late:'+id,category:options.category??'standings',facts:{family:'late.'+family,voice,school:t.name,...values},options:{team:t.id,national:false,priority:92,...options}});
 const games=s.games.filter(g=>g.year===s.season.CurrentYear&&teams.has(g.home)&&teams.has(g.away)&&g.home!==g.away);
 const championshipWeek=s.season.RegularSeasonWeekConferenceChampionship;
 const conferences=new Map((s.conferences??[]).map(c=>[c.id,c]));
 const actualTitles=Number.isInteger(championshipWeek)?games.filter(g=>g.phase==='RegularSeason'&&g.week===championshipWeek&&teams.get(g.home).conferenceId&&teams.get(g.home).conferenceId===teams.get(g.away).conferenceId&&conferences.get(teams.get(g.home).conferenceId)?.championshipType&&!['NONE','None','Invalid_'].includes(conferences.get(teams.get(g.home).conferenceId).championshipType)):[];
 const invited=new Set(actualTitles.flatMap(g=>[g.home,g.away]));
 if(regular&&week>=9&&week<14)for(const c of conferences.values()){
  if(c.independent)continue;
  const members=s.teams.filter(t=>c.teams.includes(t.id)&&integer(t.conferenceWins)&&integer(t.conferenceLosses)&&Number.isInteger(t.conferenceRank)&&t.conferenceRank>0).sort((a,b)=>a.conferenceRank-b.conferenceRank||b.conferenceWins-a.conferenceWins||a.conferenceLosses-b.conferenceLosses);
  if(members.length<2)continue;
  const leaders=members.slice(0,3),leader=members[0];
  add('race:'+c.id,'conference-race','analyst',leader,{conference:c.name,leaders:leaders.map(t=>`${t.name} (${t.conferenceWins}\u2013${t.conferenceLosses})`).join(', ')},{relatedTeams:leaders.map(t=>t.id),primaryScope:'conference',national:leaders.some(t=>poll.ranks[t.id]>=1&&poll.ranks[t.id]<=15)});
  for(const t of members.filter(t=>t.conferenceRank<=4&&t.conferenceWins>=t.conferenceLosses&&t.conferenceWins>=leader.conferenceWins-1&&t.conferenceLosses<=leader.conferenceLosses+1))add('contender:'+t.id,'contender','beat',t,{conference:c.name,place:t.conferenceRank,wins:t.conferenceWins,losses:t.conferenceLosses});
 }
 // Week 14 invitations come from the assigned championship-week fixtures.
 // Neither a standings lead nor a projected tiebreaker establishes an invite.
 if(regular&&week>=14&&Number.isInteger(championshipWeek)&&week<=championshipWeek)for(const g of actualTitles){
  const h=teams.get(g.home),a=teams.get(g.away),c=conferences.get(h.conferenceId);
  if(g.status==='Unplayed')for(const [t,opponent] of [[h,a],[a,h]]){
   add('title-invite:'+g.id+':'+t.id,'title-invite','official',t,{conference:c.name,opponent:opponent.name,championshipWeek,importance:'major'},{relatedTeams:[opponent.id],national:true,priority:112,thread:'game:'+g.id,category:'championship'});
   add('title-fan:'+g.id+':'+t.id,'title-fan','fan',t,{conference:c.name,opponent:opponent.name,rivalReplyTeam:opponent.id},{relatedTeams:[opponent.id],priority:98,thread:'game:'+g.id,category:'championship'});
   const lastWin=lastHistoricalEvent(t,year,'conferenceWin');
   if(lastWin!==null&&lastWin<year-1)add('title-history:'+t.id,'title-history','beat',t,{conference:c.name,lastYear:lastWin,opponent:opponent.name},{priority:95,category:'history'});
  }
  else if(final(g)&&[week-1,week].includes(g.week)){
   const winner=teams.get(g.homeScore>g.awayScore?g.home:g.away),loser=winner.id===h.id?a:h;
   add('title-result:'+g.id,'title-result','analyst',winner,{conference:c.name,opponent:loser.name,score:Math.max(g.homeScore,g.awayScore)+'\u2013'+Math.min(g.homeScore,g.awayScore),importance:'major'},{relatedTeams:[loser.id],national:true,priority:115,category:'championship'});
  }
 }
 if(regular&&week>=9)for(const t of teams.values()){
  if(!integer(t.wins)||!integer(t.losses)||t.wins+t.losses<6)continue;
  const remaining=games.filter(g=>g.phase==='RegularSeason'&&g.status==='Unplayed'&&g.week>=week&&g.week!==championshipWeek&&(g.home===t.id||g.away===t.id)).length;
  if(t.wins===5&&remaining>0)add('bowl-watch:'+t.id,'bowl-one-away','beat',t,{wins:t.wins,losses:t.losses,remaining},{category:'bowls',priority:91});
  else if(t.wins>=6&&t.wins<=7&&!invited.has(t.id))add('bowl-position:'+t.id,'bowl-position','beat',t,{wins:t.wins,losses:t.losses},{category:'bowls',priority:86});
  else if(t.wins<6&&remaining>0&&6-t.wins===remaining)add('bowl-no-room:'+t.id,'bowl-no-room','beat',t,{wins:t.wins,losses:t.losses,remaining,needed:6-t.wins},{category:'bowls',priority:90});
 }
 if(regular&&week>=12&&poll.key==='cfp')for(const t of teams.values()){
  if(!Number.isInteger(t.cfpRank)||t.cfpRank<1||t.cfpRank>16)continue;
  const next=games.find(g=>g.phase==='RegularSeason'&&g.week===week&&g.status==='Unplayed'&&(g.home===t.id||g.away===t.id));if(!next)continue;
  const opponent=teams.get(next.home===t.id?next.away:next.home);
  add('cfp-stakes:'+t.id,'cfp-stakes','analyst',t,{rank:t.cfpRank,wins:t.wins,losses:t.losses,opponent:opponent.name},{category:'cfp',national:true,relatedTeams:[opponent.id],priority:102,thread:'game:'+next.id});
 }
 const postseason=phase.startsWith('BowlSeason')||phase==='NationalChampionship';
 if(postseason||regular&&Number.isInteger(championshipWeek)&&week>=championshipWeek){
  // Only the earliest assigned playoff round can establish the initial berth;
  // later-round placeholders are never presented as another invitation.
  const selected=new Set();
  const assigned=games.filter(g=>g.status==='Unplayed'&&(g.bowlName&&!g.isPlayoff&&g.phase.startsWith('BowlSeason')||g.isPlayoff&&g.phase==='BowlSeason1'));
  for(const g of assigned)for(const [id,opp] of [[g.home,g.away],[g.away,g.home]]){if(selected.has(id))continue;selected.add(id);const t=teams.get(id),opponent=teams.get(opp),last=lastHistoricalEvent(t,year,g.isPlayoff?'playoffAppearance':'bowlAppearance');
   add('berth:'+g.id+':'+id,g.isPlayoff?'playoff-berth':'bowl-invite',g.isPlayoff?'cfp':'official',t,{opponent:opponent.name,venue:g.bowlName??'the College Football Playoff',historyDetail:last!==null&&last<year-1?` The program last appeared in ${last}.`:'',importance:g.isPlayoff?'major':'normal'},{category:g.isPlayoff?'cfp':'bowls',national:g.isPlayoff,priority:g.isPlayoff?113:100,relatedTeams:[opp],thread:'game:'+g.id});
  }
 }
 for(const g of games.filter(g=>phase==='NationalChampionship'&&g.phase===phase&&g.week===week&&g.status==='Unplayed'))for(const [id,opp] of [[g.home,g.away],[g.away,g.home]]){const t=teams.get(id),last=lastHistoricalEvent(t,year,'nationalAppearance');if(last!==null&&last<year-1)add('national-title-history:'+id,'title-appearance-history','analyst',t,{lastYear:last,opponent:teams.get(opp).name},{category:'history',national:true,priority:110});}
 if(week>=8)for(const t of teams.values()){
  const rows=(t.seasonHistory??[]).filter(r=>r.Year===year-1);if(rows.length!==1)continue;const prior=rows[0];
  if(!integer(prior.Wins)||!integer(prior.Losses)||!integer(t.wins)||!integer(t.losses)||prior.Wins+prior.Losses<6)continue;
  if(t.wins>=prior.Wins+3)add('turnaround:'+t.id,'turnaround','beat',t,{wins:t.wins,losses:t.losses,priorWins:prior.Wins,priorLosses:prior.Losses,previousYear:year-1,previousConference:prior.ConferenceName??t.conferenceName},{category:'history',priority:94});
  else if(t.losses>=prior.Losses+3)add('regression:'+t.id,'regression','beat',t,{wins:t.wins,losses:t.losses,priorWins:prior.Wins,priorLosses:prior.Losses,previousYear:year-1,previousConference:prior.ConferenceName??t.conferenceName},{category:'history',priority:88});
  if(regular&&prior.ConferenceName===t.conferenceName&&Number.isInteger(prior.FinalConferenceStanding)&&prior.FinalConferenceStanding>0&&Number.isInteger(t.conferenceRank)&&t.conferenceRank>0&&Math.abs(prior.FinalConferenceStanding-t.conferenceRank)>=4&&integer(prior.ConferenceWins)&&integer(prior.ConferenceLosses))add('conference-change:'+t.id,'conference-change','beat',t,{conference:t.conferenceName,place:t.conferenceRank,wins:t.conferenceWins,losses:t.conferenceLosses,previousYear:year-1,priorPlace:prior.FinalConferenceStanding,priorWins:prior.ConferenceWins,priorLosses:prior.ConferenceLosses},{category:'history',priority:90});
 }
 // The rivalry must be on the current week's unplayed schedule. Both fanbases
 // get a voice; the optional cross-fan reply still goes through the 33% gate.
 for(const g of games.filter(g=>g.phase===phase&&g.week===week&&g.status==='Unplayed'&&(teams.get(g.home).rivals?.includes(g.away)||teams.get(g.away).rivals?.includes(g.home)))){
  for(const [id,opp] of [[g.home,g.away],[g.away,g.home]]){const t=teams.get(id),other=teams.get(opp),sameConference=Boolean(t.conferenceId&&t.conferenceId===other.conferenceId);
   add('rivalry-team:'+g.id+':'+id,'rivalry-team','official',t,{opponent:other.name},{category:'schedule',relatedTeams:[opp],eventWeek:g.week,priority:103,thread:'game:'+g.id});
   add('rivalry-fan:'+g.id+':'+id,'rivalry-fan','fan',t,{opponent:other.name,rivalReplyTeam:opp},{category:'schedule',relatedTeams:[opp],eventWeek:g.week,priority:97,thread:'game:'+g.id});
   if(sameConference)add('rivalry-stakes:'+g.id+':'+id,'rivalry-stakes','beat',t,{opponent:other.name,conference:t.conferenceName,wins:t.conferenceWins,losses:t.conferenceLosses},{category:'schedule',relatedTeams:[opp],eventWeek:g.week,priority:96,thread:'game:'+g.id});
  }
 }
 if(regular&&week>=9&&week<14)for(const c of conferences.values()){
  const leaders=s.teams.filter(t=>c.teams.includes(t.id)&&t.conferenceRank>=1&&t.conferenceRank<=2&&t.conferenceWins>=3).sort((a,b)=>a.conferenceRank-b.conferenceRank||a.id-b.id);
  if(c.independent||leaders.length!==2)continue;
  const [t,opponent]=leaders;
  add('conference-beef:'+c.id,'conference-beef','fan',t,{opponent:opponent.name,conference:c.name,wins:t.conferenceWins,losses:t.conferenceLosses,rivalReplyTeam:opponent.id},{relatedTeams:[opponent.id],priority:87});
 }
 return events;
}
