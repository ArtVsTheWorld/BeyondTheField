const valid=n=>Number.isFinite(n)&&n>=0;
const sum=(st,keys)=>keys.every(k=>valid(st?.[k]))?keys.reduce((n,k)=>n+st[k],0):null;
const playerMetrics={
 passingYards:{keys:['PASSYARDS'],step:1000,label:'passing yards'},rushingYards:{keys:['RUSHYARDS'],step:1000,label:'rushing yards'},receivingYards:{keys:['RECEIVEYARDS'],step:1000,label:'receiving yards'},
 passingTD:{keys:['PASSTDS'],step:25,label:'passing touchdowns'},rushingTD:{keys:['RUSHTDS'],step:10,label:'rushing touchdowns'},receivingTD:{keys:['RECEIVETDS'],step:10,label:'receiving touchdowns'},
 catches:{keys:['RECEIVECATCHES'],step:100,label:'receptions'},tackles:{keys:['DEFTACKLES','ASSDEFTACKLES'],step:100,label:'tackles'},tfl:{keys:['DEFTACKLESFORLOSS'],step:25,label:'tackles for loss'},
 sacks:{keys:['DLINESACKS','DLINEHALFSACK'],step:10,label:'sacks'},interceptions:{keys:['DSECINTS'],step:5,label:'interceptions'},forcedFumbles:{keys:['DLINEFORCEDFUMBLES'],step:5,label:'forced fumbles'},recoveries:{keys:['DLINEFUMBLERECOVERIES'],step:5,label:'fumble recoveries'},
 breakups:{keys:['DEFPASSDEFLECTIONS'],step:25,label:'passes defended'},fieldGoals:{keys:['KICKFGMADE'],step:25,label:'field goals'},kickReturnYards:{keys:['KRETYARDS'],step:1000,label:'kick-return yards'},puntReturnYards:{keys:['PRETYARDS'],step:500,label:'punt-return yards'}
};
const teamCounters={BowlsMade:'bowl appearance',BowlsWon:'bowl win',CFPSMade:'College Football Playoff appearance',CFPSWon:'College Football Playoff win',ConferenceChampionshipsMade:'conference championship game appearance',ConferenceChampionshipsWon:'conference championship',NationalChampionshipsMade:'national championship game appearance',NationalChampionshipsWon:'national championship',HeismanWinners:'Heisman Trophy winner'};
const coachCounters={BowlWins:'bowl win',ConfChampWins:'conference championship',NCWins:'national championship',PlayoffWins:'playoff win'};
export function ordinal(n){const m=n%100;return n+(m>=11&&m<=13?'th':({1:'st',2:'nd',3:'rd'})[n%10]??'th');}
export function milestoneTotals(s){
 const teams={},players={},coaches={};
 for(const t of s.teams.filter(t=>t.id!==255)){
  if(t.historicalStats)teams[t.id]={...t.historicalStats};
  const c=t.headCoach;if(c?.careerStats)coaches[c.id]={team:t.id,...c.careerStats};
 }
 for(const p of s.players){if(p.team===255||!p.careerStats)continue;const st=p.careerStats.stats,metrics={};
  for(const [key,{keys}] of Object.entries(playerMetrics)){const n=key==='sacks'?valid(st.DLINESACKS)&&valid(st.DLINEHALFSACK)?st.DLINESACKS+.5*st.DLINEHALFSACK:null:sum(st,keys);if(n!==null)metrics[key]=n;}
  players[p.id]=metrics;
 }
 return {version:1,year:s.season.CurrentSeasonYear,teams,players,coaches};
}
// Results in FirstRoundCFPBowlGameResult also contain ordinary historical bowls.
// The explicit CFPFirstRound identifier or a post-2013 quarter/semi/title result
// is required before calling a season a playoff appearance.
const result=x=>['Win','Loss','Tie'].includes(x);
export function historicalEvent(row,kind){
 if(kind==='nationalAppearance')return result(row.NationalBowlGameResult);
 if(kind==='nationalWin')return row.NationalBowlGameResult==='Win';
 if(kind==='conferenceWin')return typeof row.ConfChampionshipConferenceEnum==='string'&&!['None','Invalid_'].includes(row.ConfChampionshipConferenceEnum);
 const rounds=['FirstRoundCFPBowlGameResult','QuarterFinalsBowlGameResult','SemiFinalsBowlGameResult','NationalBowlGameResult'];
 if(kind==='bowlAppearance')return rounds.some(k=>result(row[k]));
 if(kind==='bowlWin')return rounds.some(k=>row[k]==='Win');
 if(kind==='playoffAppearance')return row.Year>=2014&&(row.FirstRoundCFPBowlPresentationId==='CFPFirstRound'&&result(row.FirstRoundCFPBowlGameResult)||rounds.slice(1).some(k=>result(row[k])));
 return false;
}
export function lastHistoricalEvent(team,calendarYear,kind){
 const rows=(team.seasonHistory??[]).filter(r=>Number.isInteger(r.Year)&&r.Year<calendarYear),byYear=new Map(rows.map(r=>[r.Year,r]));
 if(byYear.size!==rows.length)return null;
 const last=rows.filter(r=>historicalEvent(r,kind)).sort((a,b)=>b.Year-a.Year)[0];if(!last)return null;
 for(let y=last.Year;y<calendarYear;y++)if(!byYear.has(y))return null;
 return last.Year;
}
export function historyMilestoneEvents(s){
 if(s.reconstructed||s.season.CurrentStage!=='NFLSeason')return [];
 const now=milestoneTotals(s),old=s.milestoneBaseline;
 if(old?.version!==1||old.year!==now.year)return [];
 const events=[],teams=new Map(s.teams.map(t=>[t.id,t]));
 const emit=(id,team,facts,player=null,national=false)=>events.push({id:'history:'+id,category:'history',facts:{voice:'beat',school:team.name,...facts},options:{team:team.id,player,national,priority:99,thread:'history:'+id}});
 const counter=(id,team,current,prior,key,label,family='history.team-counter',extra={})=>{
  if(Number.isInteger(current?.[key])&&Number.isInteger(prior?.[key])&&prior[key]>=0&&current[key]>prior[key])emit(id+':'+key+':'+current[key],team,{family,count:current[key],ordinal:ordinal(current[key]),achievement:label,importance:'major',...extra},null,true);
 };
 for(const t of s.teams.filter(t=>t.id!==255)){const a=now.teams[t.id],b=old.teams?.[t.id];if(!a||!b)continue;
  for(const [key,label] of Object.entries(teamCounters))counter('team:'+t.id,t,a,b,key,label);
  if(valid(a.Wins)&&valid(b.Wins)&&a.Wins>=b.Wins&&Math.floor(a.Wins/100)>Math.floor(b.Wins/100))emit('wins:'+t.id+':'+Math.floor(a.Wins/100),t,{family:'history.team-wins',threshold:Math.floor(a.Wins/100)*100,total:a.Wins});
  if(['Wins','Losses','Ties'].every(k=>valid(a[k])&&valid(b[k])&&a[k]>=b[k])){
   const total=a.Wins+a.Losses+a.Ties,before=b.Wins+b.Losses+b.Ties;if(total<=before||before===0)continue;
   const pct=(a.Wins+.5*a.Ties)/total,prior=(b.Wins+.5*b.Ties)/before;
   for(const line of [.25,.5,.75])if(prior<line&&pct>=line||prior>=line&&pct<line)emit(`percentage:${t.id}:${line}`,t,{family:'history.win-percentage',boundary:line.toFixed(3).slice(1),percentage:pct.toFixed(4).slice(1),direction:pct>=line?'to or above':'below',wins:a.Wins,losses:a.Losses,ties:a.Ties});
  }
 }
 for(const p of s.players){const team=teams.get(p.team),a=now.players[p.id],b=old.players?.[p.id];if(!team||!a||!b)continue;
  for(const [key,config] of Object.entries(playerMetrics)){if(!valid(a[key])||!valid(b[key])||a[key]<=b[key])continue;const threshold=Math.floor(a[key]/config.step)*config.step;
   if(threshold<=0||b[key]>=threshold)continue;
   emit(`player:${p.id}:${key}:${threshold}`,team,{family:'history.player-career',playerName:p.name,threshold:threshold.toLocaleString('en-US'),total:a[key].toLocaleString('en-US'),metric:config.label},p.id,key==='passingYards'&&threshold>=10000);
  }
 }
 for(const t of s.teams){const c=t.headCoach,a=c&&now.coaches[c.id],b=c&&old.coaches?.[c.id];if(!a||!b||a.team!==t.id||b.team!==t.id)continue;
  if(valid(a.Wins)&&valid(b.Wins)&&a.Wins>b.Wins&&Math.floor(a.Wins/25)>Math.floor(b.Wins/25))emit('coach:'+c.id+':wins:'+Math.floor(a.Wins/25),t,{family:'history.coach-wins',coachName:c.name,threshold:Math.floor(a.Wins/25)*25,total:a.Wins});
  for(const [key,label] of Object.entries(coachCounters))counter('coach:'+c.id,t,a,b,key,label,'history.coach-counter',{coachName:c.name});
 }
 return events;
}
