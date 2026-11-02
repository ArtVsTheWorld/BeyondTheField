import fs from 'node:fs';
import {hash,authorRegistry} from './story_authors.mjs';
const pack=JSON.parse(fs.readFileSync(new URL('../Content/Runtime/first-pack.json',import.meta.url),'utf8'));
export const CONTENT_REVISION=pack.revision;
export const stampFor=category=>({'results':'Recap','team-stats':'Recap','player-stats':'Recap',recruiting:'Recruiting',offers:'Recruiting',schedule:'Upcoming',polls:'Rankings',heisman:'Heisman',cfp:'Playoff Watch',injuries:'Injury Report',standings:'Standings',watch:'Spotlight',lines:'Odds',holiday:'Calendar',analytics:'Analysis'}[category]??'News');
const personalities=new Set(['Leader','Intense','Entertainer','TeamPlayer','Unpredictable']);
const final=g=>g&&g.published!==false&&['HomeWon','AwayWon','Tie'].includes(g.status);
const ranked=n=>Number.isInteger(n)&&n>0&&n<=25;
const numeric=x=>Number.isFinite(x);
const limitOK=text=>[...text].length<=280&&Buffer.byteLength(text,'utf8')<=512;
const slots=/\{([A-Za-z][A-Za-z0-9]*)\}/g;
function selectTemplate(family,values,seed){
 const eligible=(pack.families[family]??[]).filter(t=>[...t.body.matchAll(slots)].every(m=>values[m[1]]!==null&&values[m[1]]!==undefined));
 if(!eligible.length)return null;const start=hash(seed+'|'+family)%eligible.length;
 for(let i=0;i<eligible.length;i++){const t=eligible[(start+i)%eligible.length];const body=t.body.replace(slots,(_,k)=>values[k]).replace(/[ \t]+\n/g,'\n').replace(/[ \t]{2,}/g,' ').trim();if(body&&limitOK(body))return {body,templateId:t.id};}
 return null; // Missing facts or overflow suppress the variant; never truncate a name/stat.
}
export function renderStories(s,events,{authors={}}={}){
 if(!pack.enabled)return {stories:[],authors};
 const registry=authorRegistry(authors),teams=new Map(s.teams.filter(t=>t.id!==255).map(t=>[t.id,t])),players=new Map(s.players.map(p=>[p.id,p])),games=new Map(s.games.map(g=>[g.id,g]));
 const stories=[],byId=new Map(),reactionGames=new Set();
 const edition=`${s.leagueId}/${s.season.CurrentSeasonYear}/${s.season.CurrentWeekType}/${s.season.CurrentWeek}`;
 const teamValues=t=>({school:t?.name,nickname:t?.nickname??t?.name,coachLastName:t?.headCoach?.lastName??null,hashtag:t?.hashtags?.[0]??''});
 function add(e,family,values,{role='beat',team=teams.get(e.teamIds[0]),player=null,suffix='main',priority=e.priority,curated=e.curated,replyTo=null}={}){
  if(!team&&['official','fan'].includes(role)||['player','recruit'].includes(role)&&!player)return null;
  const account=registry.get(s,role,team,player),chosen=selectTemplate(family,values,edition+'|'+e.id+'|'+suffix+'|'+account.handle);if(!chosen)return null;
  const individual=['player','recruit'].includes(role);const portrait=individual&&player?.isNil&&Number.isInteger(player.portrait)&&player.portrait>0;
  const logo=team&&Number.isInteger(team.logo)&&team.logo>=0&&['official','fan','beat','player','recruit'].includes(role);
  const p={id:e.id+':'+suffix,eventId:e.id,category:e.category,voice:role,author:account.author,handle:account.handle,...chosen,stamp:stampFor(e.category),imageLibrary:portrait?1:logo?0:79,imageValue:portrait?player.portrait:logo?team.logo:598,priority,scopes:e.scopes,teamIds:e.teamIds,playerId:individual?player.id:e.playerId,eventWeek:e.eventWeek,thread:e.thread,curated,primaryScope:e.primaryScope,contentRevision:CONTENT_REVISION};
  if(replyTo){p.replyTo=replyTo;p.curated=false;}
  stories.push(p);byId.set(p.id,p);return p;
 }
 function performanceLine(stats){
  const parts=[];
  if(numeric(stats.passingYards)&&numeric(stats.passingTouchdowns))parts.push(`${stats.passingYards} passing yards and ${stats.passingTouchdowns} TD`);
  if(numeric(stats.rushingYards)&&numeric(stats.rushingTouchdowns))parts.push(`${stats.rushingYards} rushing yards and ${stats.rushingTouchdowns} TD`);
  if(numeric(stats.receivingYards)&&numeric(stats.receivingTouchdowns))parts.push(`${stats.receivingYards} receiving yards and ${stats.receivingTouchdowns} TD`);
  if(numeric(stats.sacks)&&stats.sacks>0)parts.push(`${stats.sacks} sacks`);
  if(numeric(stats.interceptionsCaught)&&stats.interceptionsCaught>0)parts.push(`${stats.interceptionsCaught} interceptions`);
  if(numeric(stats.soloTackles)&&stats.soloTackles>=10)parts.push(`${stats.soloTackles} solo tackles`);
  // Keep the strongest two lines; a shorter factual form is tried if names are long.
  return parts.slice(0,2).join(', ');
 }
 function perfContext(e){const f=e.facts,g=games.get(f.gameId),p=players.get(e.playerId);if(!p||!final(g))return null;const t=teams.get(p.team);if(!t)return null;
  const win=g.homeScore===g.awayScore?null:g.homeScore>g.awayScore?g.home:g.away,opponent=p.team===g.home?g.awayName??teams.get(g.away)?.name:g.homeName??teams.get(g.home)?.name;
  return {...teamValues(t),...f,opponent,statLine:performanceLine(f.stats),win:win===p.team,resultLine:win===null?'The game finished tied.':win===p.team?'A team win to go with it.':'The individual numbers came in a team loss.'};}
 for(const e of events){const f=e.facts,t=teams.get(e.teamIds[0]),v={...teamValues(t),...f,giveawayLabel:e.facts.giveaways===1?'giveaway':'giveaways'};
  if(e.category==='results'){
   const g=games.get(f.gameId);if(!final(g))continue;
   if(f.tie){add(e,'beat.tie',v);continue;}
   const winningId=g.homeScore>g.awayScore?g.home:g.away,winningTeam=teams.get(winningId),ownGame=e.teamIds.includes(s.userTeamIndex),own=teams.get(s.userTeamIndex),userWon=winningId===s.userTeamIndex;
   Object.assign(v,teamValues(winningTeam),{score:Math.max(g.homeScore,g.awayScore)+'–'+Math.min(g.homeScore,g.awayScore),winnerScore:Math.max(g.homeScore,g.awayScore),loserScore:Math.min(g.homeScore,g.awayScore),opponent:f.loser});
   if(ownGame&&userWon){const family=v.loserScore===0?'team.shutout':f.rivalry?'team.rivalry_win':f.margin<=7?'team.narrow_win':'team.win';add(e,family,v,{role:'official',team:own});}
   else add(e,f.margin>=21?'beat.result_wide':f.margin<=7?'beat.result_close':'beat.result',v,{team:winningTeam??teams.get(e.teamIds.find(id=>teams.has(id)))});
   if(!ownGame||reactionGames.has(g.id))continue;reactionGames.add(g.id);
   const ownScore=s.userTeamIndex===g.home?g.homeScore:g.awayScore,opponentScore=s.userTeamIndex===g.home?g.awayScore:g.homeScore,opponent=s.userTeamIndex===g.home?f.away:f.home;
   const performances=events.filter(x=>x.category==='player-stats'&&x.facts.gameId===g.id&&players.get(x.playerId)?.team===s.userTeamIndex).sort((a,b)=>b.priority-a.priority||a.id.localeCompare(b.id));
   const best=performances[0],bestPlayer=best&&players.get(best.playerId);
   const values={...v,...teamValues(own),opponent,ownScore,opponentScore,playerName:bestPlayer?.name??null,score:ownScore+'–'+opponentScore};
   const seed=hash(edition+'|reaction|'+g.id);
   if(userWon&&seed%2===0){
    const roster=s.players.filter(p=>p.team===s.userTeamIndex&&p.injury==='Uninjured').sort((a,b)=>a.id.localeCompare(b.id));
    const author=roster.length?roster[seed%roster.length]:bestPlayer;
    if(author){const personality=personalities.has(author.personality)?author.personality:'Neutral';let family='player.win.'+personality;
     if(author.position==='QB'&&['Leader','Intense','Neutral'].includes(personality))family=f.rivalry&&personality==='Intense'?'player.rivalry':'player.win.QB';
     // Personal production is only available when the author actually owns that stat line.
     const self=performances.find(x=>x.playerId===author.id);const receivingYards=self?.facts.stats.receivingYards??null;
     add(e,family,{...values,playerName:bestPlayer?.id===author.id?null:values.playerName,receivingYards},{role:'player',team:own,player:author,suffix:'reaction',priority:e.priority-8});}
   }else{
    let family=userWon?f.rivalry?'fan.rivalry':f.margin<=7?'fan.narrow_win':'fan.win':'fan.loss';
    const twoPicks=performances.find(x=>x.facts.stats.interceptionsThrown===2);if(!userWon&&twoPicks&&own.headCoach?.lastName){family='fan.picks';values.playerName=twoPicks.facts.playerName;}
    add(e,family,values,{role:'fan',team:own,suffix:'reaction',priority:e.priority-8});
   }
  }else if(e.category==='team-stats'){
   const g=games.get(f.gameId);v.opponent=g&&(t?.id===g.home?g.awayName??teams.get(g.away)?.name:g.homeName??teams.get(g.home)?.name);add(e,'beat.team_stats',v,{curated:false});
  }else if(e.category==='player-stats'){
   const c=perfContext(e);if(!c||!c.statLine)continue;const p=players.get(e.playerId),team=teams.get(p.team);add(e,'beat.performance',c,{team});
   if(c.win&&p.team===s.userTeamIndex&&(f.stats.rushingTouchdowns>=2||f.stats.receivingTouchdowns>=2))add(e,'team.performance',c,{role:'official',team,suffix:'team',priority:e.priority-3,curated:false});
  }else if(e.category==='polls'){
   v.places=Math.abs(f.rank-f.previousRank);v.placeLabel=v.places===1?'place':'places';if(t?.id===s.userTeamIndex&&f.movement==='up')add(e,'team.poll_up',v,{role:'official'});
   else add(e,'beat.poll_'+({up:'up',down:'down',entry:'entry',unchanged:'same'}[f.movement]),v);
  }else if(e.category==='offers'||e.category==='recruiting'){
   const p=players.get(e.playerId),team=teams.get(e.teamIds.find(id=>teams.get(id)?.name===f.school));if(!p||!team)continue;
   const values={...teamValues(team),...f},personality=personalities.has(p.personality)?p.personality:'Neutral',account=registry.get(s,'recruit',team,p);
   if(e.category==='offers')add(e,'recruit.offer.'+(account.faithLanguage?'faith':personality),values,{role:'recruit',team,player:p});
   else if(f.newlyObserved&&f.commitment==='HardCommitted')add(e,'recruit.commit.'+personality,values,{role:'recruit',team,player:p});
   else if(f.newlyObserved){values.recruitRankDetail=numeric(f.nationalRecruitRank)?` He is No. ${f.nationalRecruitRank} nationally in this recruiting class.`:'';values.coachDetail=team.headCoach?.lastName?` A new addition for Coach ${team.headCoach.lastName}.`:'';add(e,'beat.commit',values,{team});}
  }else if(e.category==='injuries'){
   v.injuryDetail=f.injuryType?' Listed injury: '+f.injuryType.replace(/([a-z])([A-Z])/g,'$1 $2').toLowerCase()+'.':'';add(e,f.recovered?'beat.recovery':f.newlyInjured?'beat.new_injury':'beat.injury',v);
  }else if(e.category==='schedule'){
   const g=games.get(f.gameId);if(!g||final(g))continue;const own=teams.get(s.userTeamIndex),user=e.teamIds.includes(s.userTeamIndex);
   v.awayLabel=(ranked(f.awayRank)?'#'+f.awayRank+' ':'')+f.away;v.homeLabel=(ranked(f.homeRank)?'#'+f.homeRank+' ':'')+f.home;v.rivalryDetail=f.rivalry?' Rivalry week. That one carries a little extra weight.':'';
   if(user){Object.assign(v,teamValues(own),{opponent:s.userTeamIndex===g.home?f.away:f.home});add(e,'team.upcoming',v,{role:'official',team:own});}else add(e,'beat.preview',v);
  }else if(e.category==='watch'){
   v.watchDetail=f.basis==='heisman'?' He’s already part of the Heisman conversation.':' His recent production put him on this week’s watch list.';add(e,'beat.watch',v);
  }else if(e.category==='standings'){
   v.leaders=f.leaders.map(x=>`${x.school} (${x.wins}–${x.losses})`).join(', ');add(e,f.independent?'beat.independents':'beat.standings',v,{team:teams.get(s.userTeamIndex)});
  }else if(e.category==='cfp')add(e,'beat.cfp',v);
  else if(e.category==='heisman'){
   v.rankChange=numeric(f.previousRank)&&f.previousRank!==f.rank?`moves ${f.previousRank>f.rank?'up':'down'} from No. ${f.previousRank} to No. ${f.rank}`:`is No. ${f.rank}`;
   const perf=events.filter(x=>x.category==='player-stats'&&x.playerId===e.playerId).sort((a,b)=>(b.eventWeek??-1)-(a.eventWeek??-1)||b.priority-a.priority)[0],c=perf&&perfContext(perf);
   add(e,c?'analyst.heisman':'beat.heisman',{...v,statLine:c?.statLine,opponent:c?.opponent},{role:c?'analyst':'beat'});
  }else if(e.category==='lines'){
   const g=games.get(f.gameId);if(!g||final(g))continue;Object.assign(v,{home:g.homeName??teams.get(g.home)?.name,away:g.awayName??teams.get(g.away)?.name});add(e,f.pickem?'model.pickem':'model.line',v,{role:'model'});
  }else if(e.category==='holiday')add(e,'fan.holiday',v,{role:'fan',team:teams.get(s.userTeamIndex)});
  else if(e.category==='analytics'){
   let family;
   if(f.metric==='rushingYardsPerGame'){v.rushingYardsPerGame=f.rushingYardsPerGame.toFixed(1);v.rankPhrase=(f.nationalRankTied?'tied for No. ':'No. ')+f.nationalRank;family=ranked(f.pollRank)&&ranked(f.previousPollRank)&&f.pollRank<f.previousPollRank?'analyst.rushing_poll':'analyst.rushing';}
   else if(f.metric==='thirdDownConversionRate'){v.percent=(f.rate*100).toFixed(1);family=f.rate<=.3?'analyst.third_low':'analyst.third_high';}
   else if(f.metric==='redZoneTouchdownRate'){v.percent=(f.rate*100).toFixed(1);family=f.rate<=.45?'analyst.red_low':'analyst.red_high';}
   else if(f.metric==='turnoverMargin')family=f.margin>=0?'analyst.turnover_plus':'analyst.turnover_minus';
   else if(f.kind==='season_largest_winning_margin'){v.score=f.winnerScore+'–'+f.loserScore;family='analyst.margin';}
   if(family){const parent=add(e,family,v,{role:'analyst'});
    if(parent&&family==='analyst.rushing_poll'&&e.teamIds.includes(s.userTeamIndex)&&s.games.some(g=>final(g)&&g.week===s.season.CurrentWeek-1&&((g.home===s.userTeamIndex&&g.homeScore>g.awayScore)||(g.away===s.userTeamIndex&&g.awayScore>g.homeScore))))add(e,'fan.poll_reply',{...v,analystHandle:parent.handle},{role:'fan',team:teams.get(s.userTeamIndex),suffix:'reply',priority:e.priority-5,curated:false,replyTo:parent.id});
   }
  }
 }
 // Dependent replies only exist alongside the actual generated parent.
 return {stories:stories.filter(p=>!p.replyTo||byId.has(p.replyTo)),authors:registry.entries};
}
