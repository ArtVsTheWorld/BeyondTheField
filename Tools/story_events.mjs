import {teamAnalytics} from './team_analytics.mjs';
// Read-only Dynasty facts. This module contains no tweet prose or account identities.
export const weekKey=s=>`${s.leagueId}/${s.season.CurrentSeasonYear}/${s.season.CurrentWeekType}/${s.season.CurrentWeek}`;
const complete=g=>['HomeWon','AwayWon','Tie'].includes(g.status);
const ranked=n=>Number.isInteger(n)&&n>=1&&n<=25;
export function detectEvents(s,previous=null){
  if(s.format!==2||s.gameYear!==27||!s.sourceUnchanged||!/^[a-f0-9]{64}$/.test(s.sha256))throw Error('Invalid Dynasty snapshot');
  const year=s.season.CurrentYear,week=s.season.CurrentWeek,phase=s.season.CurrentWeekType;
  if(!Number.isInteger(week)||week<0||week>40)throw Error('Invalid Dynasty week');
  const inSeason=s.season.CurrentStage==='NFLSeason',teams=new Map(s.teams.map(t=>[t.id,t])),players=new Map(s.players.map(p=>[p.id,p]));
  if(!teams.has(s.userTeamIndex))throw Error('Controlled team missing from snapshot');
  const own=teams.get(s.userTeamIndex),conferenceTeams=new Set(s.teams.filter(t=>own.conferenceId&&t.conferenceId===own.conferenceId).map(t=>t.id));
  const rank=id=>ranked(teams.get(id)?.mediaRank)?teams.get(id).mediaRank:99;
  const events=[],ids=new Set();
  const emit=(id,category,facts,{team=null,player=null,relatedTeams=[],national=null,eventWeek=null,priority=50,thread=null,curated=true,primaryScope=null}={})=>{
    if(ids.has(id))return;const p=players.get(player);const teamIds=[...new Set([team,p?.team,...relatedTeams].filter(t=>Number.isInteger(t)&&t!==255))],scopes=[];
    if(teamIds.includes(s.userTeamIndex))scopes.push('team');if(teamIds.some(t=>conferenceTeams.has(t)))scopes.push('conference');
    if(national??['polls','heisman','cfp','holiday'].includes(category))scopes.push('national');if(!scopes.length)return;
    ids.add(id);const teamContext=teamIds.map(id=>teams.get(id)).filter(Boolean).map(t=>({teamId:t.id,school:t.name,nickname:t.nickname??null,nicknameAlt:t.nicknameAlt??null,hashtags:t.hashtags??[],headCoach:t.headCoach??null}));
    events.push({id,category,facts,teamIds,teamContext,playerId:player,personality:p?.personality??null,position:p?.position??null,scopes,eventWeek,priority,thread:thread??id,curated,primaryScope});
  };
  const eligible=s.games.filter(g=>g.year===year&&g.phase===phase);
  const recent=inSeason?eligible.filter(g=>[week-1,week].includes(g.week)&&complete(g)):[];
  const upcoming=inSeason?eligible.filter(g=>g.week===week&&!complete(g)):[];
  for(const g of recent){
    const user=[g.home,g.away].includes(s.userTeamIndex),margin=Math.abs(g.homeScore-g.awayScore),tie=g.homeScore===g.awayScore;
    const winner=tie?null:g.homeScore>g.awayScore?g.home:g.away,loser=tie?null:winner===g.home?g.away:g.home;
    emit(`result:${g.id}`,'results',{gameId:g.id,home:g.homeName??teams.get(g.home)?.name,away:g.awayName??teams.get(g.away)?.name,homeScore:g.homeScore,awayScore:g.awayScore,winner:tie?null:winner===g.home?g.homeName??teams.get(g.home)?.name:g.awayName??teams.get(g.away)?.name,loser:tie?null:loser===g.home?g.homeName??teams.get(g.home)?.name:g.awayName??teams.get(g.away)?.name,margin,tie,rivalry:Boolean(teams.get(g.home)?.rivals?.includes(g.away)||teams.get(g.away)?.rivals?.includes(g.home)),timing:g.week===week?'current':'previous'},
      {team:winner,relatedTeams:[g.home,g.away],national:rank(g.home)<=25||rank(g.away)<=25,eventWeek:g.week,priority:user?100:60,thread:`game:${g.id}`});
    if(user)for(const [id,st] of [[g.home,g.homeStats],[g.away,g.awayStats]])if(id===s.userTeamIndex&&st&&['OFFPASSYARDS','OFFRUSHYARDS','FIRSTDOWNS','GIVEAWAYS'].every(k=>Number.isFinite(st[k])))
      emit(`teamstats:${g.id}:${id}`,'team-stats',{gameId:g.id,school:teams.get(id).name,passingYards:st.OFFPASSYARDS,rushingYards:st.OFFRUSHYARDS,firstDowns:st.FIRSTDOWNS,giveaways:st.GIVEAWAYS},{team:id,eventWeek:g.week,priority:94,thread:`game:${g.id}`});
  }
  const games=new Map(recent.map(g=>[g.id,g])),form=new Map();
  for(const r of s.performances){
    const g=games.get(r.game),p=players.get(r.player);if(!g||!p)continue;const st=r.stats,stats={};let impact=0;
    if(st.PASSATTEMPTS>0){Object.assign(stats,{passAttempts:st.PASSATTEMPTS,passCompletions:st.PASSCOMPLETED,passingYards:st.PASSYARDS,passingTouchdowns:st.PASSTDS,interceptionsThrown:st.PASSINTS});impact+=st.PASSYARDS/10+st.PASSTDS*8;}
    if(st.RUSHATTEMPTS>0&&(st.RUSHYARDS>=50||st.RUSHTDS>0)){Object.assign(stats,{rushingYards:st.RUSHYARDS,rushingTouchdowns:st.RUSHTDS});impact+=st.RUSHYARDS/5+st.RUSHTDS*8;}
    if(st.RECEIVECATCHES>0&&(st.RECEIVEYARDS>=60||st.RECEIVETDS>0)){Object.assign(stats,{catches:st.RECEIVECATCHES,receivingYards:st.RECEIVEYARDS,receivingTouchdowns:st.RECEIVETDS});impact+=st.RECEIVEYARDS/5+st.RECEIVETDS*8;}
    const sacks=(st.DLINESACKS??0)+(st.DLINEHALFSACK??0)*0.5;if(sacks>0){stats.sacks=sacks;impact+=sacks*12;}
    if(st.DSECINTS>0){stats.interceptionsCaught=st.DSECINTS;impact+=st.DSECINTS*15;}if(st.DEFTACKLES>=10){stats.soloTackles=st.DEFTACKLES;impact+=st.DEFTACKLES*2;}
    form.set(p.id,(form.get(p.id)??0)+impact);
    if(Object.keys(stats).length&&impact>=25)emit(`performance:${r.game}:${r.player}:${r.type}`,'player-stats',{gameId:g.id,playerName:p.name,school:teams.get(r.team)?.name,position:p.position,stats,timing:g.week===week?'current':'previous'},
      {player:p.id,team:r.team,national:impact>=75||(rank(r.team)<=25&&impact>=40),eventWeek:g.week,priority:(r.team===s.userTeamIndex?91:65)+Math.min(impact,100)/100,thread:`game:${g.id}`});
  }
  if(inSeason)for(const t of s.teams){if(!ranked(t.mediaRank)||t.mediaLastRank===t.mediaRank&&t.id!==s.userTeamIndex&&t.mediaRank!==1)continue;
    emit(`poll:${t.id}`,'polls',{school:t.name,rank:t.mediaRank,previousRank:ranked(t.mediaLastRank)?t.mediaLastRank:null,movement:!ranked(t.mediaLastRank)?'entry':t.mediaLastRank>t.mediaRank?'up':t.mediaLastRank<t.mediaRank?'down':'unchanged'},
      {team:t.id,priority:t.id===s.userTeamIndex?98:t.mediaRank<=5?83:55});
  }
  const prior=previous&&previous.leagueId===s.leagueId&&previous.season.CurrentSeasonYear===s.season.CurrentSeasonYear&&previous.season.CurrentWeekType===phase&&previous.season.CurrentWeek===week-1?previous:null;
  const previousPlayers=new Map((s.midweekBaseline?.players??prior?.players??[]).map(p=>[p.id,p]));
  for(const p of s.players){if(p.team!==s.userTeamIndex||!p.injury||p.injury==='Uninjured')continue;
    const fresh=inSeason&&p.injuryYear===year&&p.injuryWeek===week-1&&p.injuryStage===s.season.CurrentStage;
    emit(`injury:${p.id}`,'injuries',{playerName:p.name,school:own.name,status:p.injury,injuryType:p.injuryType&&p.injuryType!=='Invalid_'&&p.injuryType!=='None'?p.injuryType:null,newlyInjured:fresh},
      {player:p.id,priority:96,eventWeek:fresh?p.injuryWeek:null});
  }
  if(prior||s.midweekBaseline)for(const p of s.players){const old=previousPlayers.get(p.id);if(p.team===s.userTeamIndex&&p.injury==='Uninjured'&&old?.injury&&old.injury!=='Uninjured')
    emit(`healthy:${p.id}`,'injuries',{playerName:p.name,school:own.name,status:'Uninjured',recovered:true},{player:p.id,priority:95});}
  const oldCommits=new Set((prior?.commitments??[]).map(c=>`${c.team}:${c.player}`));
  for(const c of s.commitments){const p=players.get(c.player);if(!p)continue;
    const fresh=(s.newCommitments??[]).some(n=>n.team===c.team&&n.player===c.player)||(prior&&!oldCommits.has(`${c.team}:${c.player}`))||(inSeason&&c.week>0&&c.week===week-1);
    if(!fresh&&c.team!==s.userTeamIndex)continue;
    emit(`commit:${c.team}:${c.player}`,'recruiting',{playerName:p.name,school:teams.get(c.team)?.name,position:p.position,nationalRecruitRank:c.rank>0?c.rank:null,commitment:c.stage,newlyObserved:Boolean(fresh)},
      {team:c.team,player:p.id,national:fresh&&c.rank>0&&c.rank<=100,curated:Boolean(fresh),thread:`commitments:${c.team}`,priority:c.team===s.userTeamIndex&&fresh?97:fresh?79+1/(c.rank||9999):64});
  }
  for(const o of s.newOffers??[]){const p=players.get(o.player);if(!p||!teams.has(o.team))continue;
    emit(`offer:${o.team}:${p.id}`,'offers',{playerName:p.name,school:teams.get(o.team).name,position:p.position,nationalRecruitRank:o.rank>0?o.rank:null},
      {team:o.team,player:p.id,national:o.rank>0&&o.rank<=100,thread:`offers:${o.team}`,priority:o.team===s.userTeamIndex?95:72+1/(o.rank||9999)});
  }
  for(const h of s.heisman){const p=players.get(h.player);if(inSeason&&p)emit(`heisman:${p.id}`,'heisman',{playerName:p.name,school:teams.get(h.team)?.name,rank:h.rank,previousRank:h.lastRank>0?h.lastRank:null},{team:h.team,player:p.id,priority:h.rank===1?88:74-h.rank});}
  for(const g of upcoming){const user=[g.home,g.away].includes(s.userTeamIndex),national=rank(g.home)<=25||rank(g.away)<=25;
    emit(`preview:${g.id}`,'schedule',{gameId:g.id,home:g.homeName??teams.get(g.home)?.name,away:g.awayName??teams.get(g.away)?.name,homeRank:ranked(rank(g.home))?rank(g.home):null,awayRank:ranked(rank(g.away))?rank(g.away):null,month:g.month,day:g.day,rivalry:Boolean(teams.get(g.home)?.rivals?.includes(g.away)||teams.get(g.away)?.rivals?.includes(g.home))},
      {team:user?s.userTeamIndex:g.home,relatedTeams:[g.home,g.away],national,eventWeek:g.week,priority:user?93:national?85:78,thread:`game:${g.id}`});
    // Candidate selection uses observed performance or Heisman contention, not hidden ability values.
    const candidates=s.players.filter(p=>[g.home,g.away].includes(p.team)&&p.injury==='Uninjured'&&((form.get(p.id)??0)>0||s.heisman.some(h=>h.player===p.id)));
    candidates.sort((a,b)=>(form.get(b.id)??0)-(form.get(a.id)??0)||a.id.localeCompare(b.id));const p=candidates[0];
    if(p&&user)emit(`watch:${g.id}:${p.id}`,'watch',{gameId:g.id,playerName:p.name,school:teams.get(p.team)?.name,position:p.position,opponent:teams.get(p.team===g.home?g.away:g.home)?.name,basis:(form.get(p.id)??0)>0?'recentPerformance':'heisman'},
      {team:p.team,player:p.id,priority:86,thread:`game:${g.id}`});
    if(user){const strength=id=>{const ps=s.players.filter(p=>p.team===id&&p.injury==='Uninjured'&&Number.isFinite(p.overall)).sort((a,b)=>b.overall-a.overall).slice(0,22);return ps.length?ps.reduce((n,p)=>n+p.overall,0)/ps.length:null;};
      const hs=strength(g.home),as=strength(g.away);if(hs!==null&&as!==null){const spread=Math.round(((hs-as)*0.6+2.5)*2)/2;
        emit(`line:${g.id}`,'lines',{gameId:g.id,favorite:spread===0?null:teams.get(spread>0?g.home:g.away)?.name,opponent:teams.get(spread>0?g.away:g.home)?.name,spread:Math.abs(spread),pickem:spread===0,simulated:true},{team:s.userTeamIndex,relatedTeams:[g.home,g.away],priority:70,thread:`game:${g.id}`});}
    }
  }
  if(inSeason){for(const [flag,name] of [['thanksgiving','Thanksgiving'],['christmas','Christmas'],['newYears','New Year']])if(upcoming.some(g=>g[flag]))emit(`holiday:${flag}`,'holiday',{holiday:name},{priority:82});
    if(upcoming.some(g=>g.month===10&&g.day===31))emit('holiday:halloween','holiday',{holiday:'Halloween'},{priority:82});
  }
  if(inSeason&&conferenceTeams.size){const independent=own.independent;
    const leaders=s.teams.filter(t=>conferenceTeams.has(t.id)&&Number.isFinite(independent?t.wins:t.conferenceRank)).sort((a,b)=>independent?b.wins-a.wins||a.losses-b.losses:a.conferenceRank-b.conferenceRank).slice(0,3);
    if(leaders.length)emit(`standings:${own.conferenceId}`,'standings',{conference:own.conferenceName,independent:Boolean(independent),leaders:leaders.map(t=>({school:t.name,wins:independent?t.wins:t.conferenceWins,losses:independent?t.losses:t.conferenceLosses,conferencePlace:independent?null:t.conferenceRank}))},
      {relatedTeams:[...conferenceTeams],national:false,priority:84,primaryScope:'conference'});
  }
  if(inSeason)for(const t of s.teams.filter(t=>ranked(t.cfpRank)).sort((a,b)=>a.cfpRank-b.cfpRank).slice(0,5))emit(`cfp:${t.id}`,'cfp',{school:t.name,rank:t.cfpRank,previousRank:ranked(t.cfpLastRank)?t.cfpLastRank:null},{team:t.id,national:true,priority:t.id===s.userTeamIndex?96:87});
  const analytics=teamAnalytics(s);
  for(const a of analytics.teams){const t=teams.get(a.teamId),national=rank(a.teamId)<=25;
    if(a.rushingRank!==null&&(a.rushingRank<=10||a.teamId===s.userTeamIndex))emit(`analysis:rushing:${a.teamId}`,'analytics',{metric:'rushingYardsPerGame',school:a.school,sampleGames:a.gamesPlayed,rushingYards:a.rushingYards,rushingYardsPerGame:a.rushingYardsPerGame,nationalRank:a.rushingRank,nationalRankTied:a.rushingRankTied,nationalPopulation:analytics.coverage.populationSize,pollRank:ranked(t.mediaRank)?t.mediaRank:null,previousPollRank:ranked(t.mediaLastRank)?t.mediaLastRank:null},{team:a.teamId,national:national||a.rushingRank<=10,priority:85});
    if(a.gamesPlayed>=3&&a.thirdDownRate!==null&&(a.thirdDownRate<=.30||a.thirdDownRate>=.55))emit(`analysis:third-down:${a.teamId}`,'analytics',{metric:'thirdDownConversionRate',school:a.school,sampleGames:a.gamesPlayed,conversions:a.thirdDownConversions,attempts:a.thirdDownAttempts,rate:a.thirdDownRate},{team:a.teamId,national:national||a.thirdDownRate<=.25||a.thirdDownRate>=.60,priority:82});
    if(a.gamesPlayed>=3&&a.redZoneTouchdownRate!==null&&a.redZoneTrips>=10&&(a.redZoneTouchdownRate<=.45||a.redZoneTouchdownRate>=.8))emit(`analysis:red-zone:${a.teamId}`,'analytics',{metric:'redZoneTouchdownRate',school:a.school,sampleGames:a.gamesPlayed,trips:a.redZoneTrips,touchdowns:a.redZoneTouchdowns,rate:a.redZoneTouchdownRate},{team:a.teamId,national:national||a.redZoneTouchdownRate<=.35,priority:83});
    if(a.gamesPlayed>=3&&a.turnoverMargin!==null&&Math.abs(a.turnoverMargin)>=5)emit(`analysis:turnovers:${a.teamId}`,'analytics',{metric:'turnoverMargin',school:a.school,sampleGames:a.gamesPlayed,giveaways:a.giveaways,takeaways:a.takeaways,margin:a.turnoverMargin},{team:a.teamId,national,priority:81});
  }
  for(const m of analytics.milestones)if(m.eventWeek>=week-1)emit(`analysis:margin-superlative:${m.gameId}`,'analytics',m,{team:m.teamId,national:true,eventWeek:m.eventWeek,priority:87});
  return events;
}
