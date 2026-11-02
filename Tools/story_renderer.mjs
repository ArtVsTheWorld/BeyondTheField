import {createHash} from 'node:crypto';
import {hash,authorRegistry} from './story_authors.mjs';
import {likesFor,replyLikesFor,ENGAGEMENT_VERSION} from './story_engagement.mjs';
import {avatarFor} from './story_avatars.mjs';
import {chooseTemplate,contentPack as pack} from './story_templates.mjs';
import {addConversations} from './story_conversations.mjs';
export const CONTENT_REVISION=pack.revision;
export const stampFor=category=>({'results':'Recap','team-stats':'Recap','player-stats':'Recap',recruiting:'Recruiting',offers:'Recruiting',schedule:'Upcoming',polls:'Rankings',heisman:'Heisman',cfp:'Playoff Watch',injuries:'Injury Report',standings:'Standings',watch:'Spotlight',lines:'Odds',holiday:'Calendar',analytics:'Analysis',upsets:'Upset',records:'Record Book',streaks:'Streak',awards:'Award'}[category]??'News');
const personalities=new Set(['Leader','Intense','Entertainer','TeamPlayer','Unpredictable']);
const final=g=>g&&g.published!==false&&['HomeWon','AwayWon','Tie'].includes(g.status);
const ranked=n=>Number.isInteger(n)&&n>0&&n<=25;
const numeric=x=>Number.isFinite(x);
export function renderStories(s,events,{authors={},history=[],sameWeek=null}={}){
 if(!pack.enabled)return {stories:[],authors};
 const registry=authorRegistry(authors),teams=new Map(s.teams.filter(t=>t.id!==255).map(t=>[t.id,t])),players=new Map(s.players.map(p=>[p.id,p])),games=new Map(s.games.map(g=>[g.id,g]));
 const stories=[],byId=new Map(),reactionGames=new Set(),sameStories=new Map((sameWeek?.stories??[]).map(p=>[p.id,p])),reactionAccounts=new Map(),reactionTopics=new Map(),replyCounts=new Map();
 const edition=`${s.leagueId}/${s.season.CurrentSeasonYear}/${s.season.CurrentWeekType}/${s.season.CurrentWeek}`;
 const teamValues=t=>({school:t?.name,nickname:t?.nickname??t?.name,coachLastName:t?.headCoach?.lastName??null,hashtag:t?.hashtags?.[0]??''});
 function add(e,family,values,{role='beat',team=teams.get(e.teamIds[0]),player=null,suffix='main',priority=e.priority,curated=e.curated,replyTo=null,persona=0,important=false}={}){
  if(!team&&['official','fan'].includes(role)||['player','recruit'].includes(role)&&!player)return null;
  const parent=replyTo?byId.get(replyTo):null;if(replyTo&&!parent)return null;
  const account=registry.get(s,role,team,player,persona),id=e.id+':'+suffix;
  const filled={...values,...(parent?{parentHandle:parent.handle}:{})};
  const renderKey=createHash('sha256').update(JSON.stringify({family,values:filled,handle:account.handle})).digest('hex');
  const chosen=chooseTemplate(family,filled,edition+'|'+id+'|'+account.handle,{handle:account.handle,week:s.season.CurrentWeek,history,sameStory:sameStories.get(id),renderKey});if(!chosen)return null;
  const reaction=['player','fan'].includes(role),accountKey=account.handle.toLowerCase(),topic=e.facts.gameId?e.facts.gameId+':'+team?.id:null;
  if(reaction&&!important&&((reactionAccounts.get(accountKey)??0)>=pack.publicationPolicy.reactionPostsPerAccount||(topic&&(reactionTopics.get(topic)??0)>=pack.publicationPolicy.reactionsPerGameTeam)))return null;
  if(parent&&(replyCounts.get(parent.id)??0)>=pack.publicationPolicy.maximumRepliesPerParent)return null;
  const p={id,eventId:e.id,category:e.category,voice:role,author:account.author,handle:account.handle,...chosen,renderKey,stamp:parent?'Reply':stampFor(e.category),...avatarFor(role,team,player),likes:likesFor(s,id,role,team,e,sameStories.get(id)),priority,scopes:parent?parent.scopes:e.scopes,teamIds:e.teamIds,playerId:['player','recruit'].includes(role)?player.id:e.playerId,eventWeek:e.eventWeek,thread:e.thread,curated:curated!==false&&parent?.curated!==false,primaryScope:e.primaryScope,contentRevision:CONTENT_REVISION};
  if(parent)p.likes=replyLikesFor(s,id,parent.likes,sameStories.get(id));p.engagementVersion=ENGAGEMENT_VERSION;
  if(parent){p.replyTo=parent.id;replyCounts.set(parent.id,(replyCounts.get(parent.id)??0)+1);}
  if(reaction){reactionAccounts.set(accountKey,(reactionAccounts.get(accountKey)??0)+1);if(topic)reactionTopics.set(topic,(reactionTopics.get(topic)??0)+1);}
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
  if(f.family){const values={...v,...f};add(e,f.family,values,{role:e.category==='analytics'?'analyst':'beat',persona:e.category==='analytics'?1:0});continue;}
  if(e.category==='results'){
   const g=games.get(f.gameId);if(!final(g))continue;
   if(f.tie){add(e,'beat.tie',v);continue;}
   const winningId=g.homeScore>g.awayScore?g.home:g.away,winningTeam=teams.get(winningId);
   Object.assign(v,teamValues(winningTeam),{score:Math.max(g.homeScore,g.awayScore)+'–'+Math.min(g.homeScore,g.awayScore),winnerScore:Math.max(g.homeScore,g.awayScore),loserScore:Math.min(g.homeScore,g.awayScore),opponent:f.loser});
   if(winningTeam){const family=v.loserScore===0?'team.shutout':f.rivalry?'team.rivalry_win':f.margin<=7?'team.narrow_win':'team.win';add(e,family,v,{role:'official',team:winningTeam});}
   else add(e,f.margin>=21?'beat.result_wide':f.margin<=7?'beat.result_close':'beat.result',v,{team:winningTeam??teams.get(e.teamIds.find(id=>teams.has(id)))});
   if(reactionGames.has(g.id))continue;reactionGames.add(g.id);
   for(const own of [teams.get(g.home),teams.get(g.away)].filter(Boolean)){const userWon=winningId===own.id;
   const ownScore=own.id===g.home?g.homeScore:g.awayScore,opponentScore=own.id===g.home?g.awayScore:g.homeScore,opponent=own.id===g.home?f.away:f.home;
   const performances=events.filter(x=>x.category==='player-stats'&&x.facts.gameId===g.id&&players.get(x.playerId)?.team===own.id).sort((a,b)=>b.priority-a.priority||a.id.localeCompare(b.id));
   const best=performances[0],bestPlayer=best&&players.get(best.playerId);
   const values={...v,...teamValues(own),opponent,ownScore,opponentScore,playerName:bestPlayer?.name??null,score:ownScore+'–'+opponentScore};
   const seed=hash(edition+'|reaction|'+g.id);
   if(userWon&&seed%2===0){
    const roster=s.players.filter(p=>p.team===own.id&&p.injury==='Uninjured').sort((a,b)=>a.id.localeCompare(b.id));
    const author=roster.length?roster[seed%roster.length]:bestPlayer;
    if(author){const personality=personalities.has(author.personality)?author.personality:'Neutral';let family='player.win.'+personality;
     if(author.position==='QB'&&['Leader','Intense','Neutral'].includes(personality))family=f.rivalry&&personality==='Intense'?'player.rivalry':'player.win.QB';
     // Personal production is only available when the author actually owns that stat line.
     const self=performances.find(x=>x.playerId===author.id);const receivingYards=self?.facts.stats.receivingYards??null;
     add(e,family,{...values,playerName:bestPlayer?.id===author.id?null:values.playerName,receivingYards},{role:'player',team:own,player:author,suffix:'reaction:'+own.id,priority:e.priority-8});}
   }else{
    let family=userWon?f.rivalry?'fan.rivalry':f.margin<=7?'fan.narrow_win':'fan.win':'fan.loss';
    const twoPicks=performances.find(x=>x.facts.stats.interceptionsThrown===2);if(!userWon&&twoPicks&&own.headCoach?.lastName){family='fan.picks';values.playerName=twoPicks.facts.playerName;}
    add(e,family,values,{role:'fan',team:own,suffix:'reaction:'+own.id,priority:e.priority-8});
   }
   }
  }else if(e.category==='team-stats'){
   const g=games.get(f.gameId);v.opponent=g&&(t?.id===g.home?g.awayName??teams.get(g.away)?.name:g.homeName??teams.get(g.home)?.name);add(e,'beat.team_stats',v,{curated:false});
  }else if(e.category==='player-stats'){
   const c=perfContext(e);if(!c||!c.statLine)continue;const p=players.get(e.playerId),team=teams.get(p.team);add(e,'beat.performance',c,{team});
  }else if(e.category==='polls'){
   v.places=Math.abs(f.rank-f.previousRank);v.placeLabel=v.places===1?'place':'places';if(f.movement==='up')add(e,'team.poll_up',v,{role:'official'});
   else add(e,'beat.poll_'+({up:'up',down:'down',entry:'entry',unchanged:'same'}[f.movement]),v);
  }else if(e.category==='offers'||e.category==='recruiting'){
   const p=players.get(e.playerId),team=teams.get(e.teamIds.find(id=>teams.get(id)?.name===f.school));if(!p||!team)continue;
   const values={...teamValues(team),...f},personality=personalities.has(p.personality)?p.personality:'Neutral',account=registry.get(s,'recruit',team,p);
   if(e.category==='offers')add(e,'recruit.offer.'+(account.faithLanguage?'faith':personality),values,{role:'recruit',team,player:p});
   else if(f.newlyObserved&&f.commitment==='HardCommitted')add(e,'recruit.commit.'+personality,values,{role:'recruit',team,player:p});
   else if(f.newlyObserved){values.recruitRankDetail=numeric(f.nationalRecruitRank)?` He is No. ${f.nationalRecruitRank} nationally in this recruiting class.`:'';values.coachDetail=team.headCoach?.lastName?` A new addition for Coach ${team.headCoach.lastName}.`:'';add(e,'beat.commit',values,{team});}
   if(e.category==='recruiting'&&f.newlyObserved&&f.commitment==='HardCommitted'&&(f.recruitSignificance==='questioned'||f.stars>=4||hash(e.id+'|star-detail')%2===0)){
    const starDescription=f.stars?f.stars+'-star ':'';add(e,f.recruitSignificance==='questioned'?'beat.recruit_questioned':'beat.recruit_pickup',{...values,starDescription},{role:'beat',team,suffix:'pickup',priority:e.priority-1});
   }
  }else if(e.category==='injuries'){
   v.injuryDetail=f.injuryType?' Listed injury: '+f.injuryType.replace(/([a-z])([A-Z])/g,'$1 $2').toLowerCase()+'.':'';add(e,f.recovered?'beat.recovery':f.newlyInjured?'beat.new_injury':'beat.injury',v);
  }else if(e.category==='schedule'){
   const g=games.get(f.gameId);if(!g||final(g))continue;
   v.awayLabel=(ranked(f.awayRank)?'#'+f.awayRank+' ':'')+f.away;v.homeLabel=(ranked(f.homeRank)?'#'+f.homeRank+' ':'')+f.home;v.rivalryDetail=f.rivalry?' Rivalry week. That one carries a little extra weight.':'';
   if(t){Object.assign(v,teamValues(t),{opponent:t.id===g.home?f.away:f.home});add(e,'team.upcoming',v,{role:'official',team:t});}else add(e,'beat.preview',v);
  }else if(e.category==='watch'){
   v.watchDetail=f.basis==='heisman'?' He’s already part of the Heisman conversation.':' His recent production put him on this week’s watch list.';add(e,'beat.watch',v);
  }else if(e.category==='standings'){
   v.leaders=f.leaders.map(x=>`${x.school} (${x.wins}–${x.losses})`).join(', ');add(e,f.independent?'beat.independents':'beat.standings',v,{team:t});
  }else if(e.category==='cfp')add(e,'beat.cfp',v);
  else if(e.category==='heisman'){
   v.rankChange=numeric(f.previousRank)&&f.previousRank!==f.rank?`moves ${f.previousRank>f.rank?'up':'down'} from No. ${f.previousRank} to No. ${f.rank}`:`is No. ${f.rank}`;
   const perf=events.filter(x=>x.category==='player-stats'&&x.playerId===e.playerId).sort((a,b)=>(b.eventWeek??-1)-(a.eventWeek??-1)||b.priority-a.priority)[0],c=perf&&perfContext(perf);
   add(e,c?'analyst.heisman':'beat.heisman',{...v,statLine:c?.statLine,opponent:c?.opponent},{role:c?'analyst':'beat'});
  }else if(e.category==='lines'){
   const g=games.get(f.gameId);if(!g||final(g))continue;Object.assign(v,{home:g.homeName??teams.get(g.home)?.name,away:g.awayName??teams.get(g.away)?.name});add(e,f.pickem?'model.pickem':'model.line',v,{role:'model'});
  }else if(e.category==='holiday')add(e,'fan.holiday',v,{role:'fan',team:s.teams.filter(t=>t.id!==255)[hash(e.id+'|calendar')%s.teams.filter(t=>t.id!==255).length]});
  else if(e.category==='analytics'){
   let family;
   if(f.metric==='rushingYardsPerGame'){v.rushingYardsPerGame=f.rushingYardsPerGame.toFixed(1);v.rankPhrase=(f.nationalRankTied?'tied for No. ':'No. ')+f.nationalRank;family=ranked(f.pollRank)&&ranked(f.previousPollRank)&&f.pollRank<f.previousPollRank?'analyst.rushing_poll':'analyst.rushing';}
   else if(f.metric==='thirdDownConversionRate'){v.percent=(f.rate*100).toFixed(1);family=f.rate<=.3?'analyst.third_low':'analyst.third_high';}
   else if(f.metric==='redZoneTouchdownRate'){v.percent=(f.rate*100).toFixed(1);family=f.rate<=.45?'analyst.red_low':'analyst.red_high';}
   else if(f.metric==='turnoverMargin')family=f.margin>=0?'analyst.turnover_plus':'analyst.turnover_minus';
   else if(f.kind==='season_largest_winning_margin'){v.score=f.winnerScore+'–'+f.loserScore;family='analyst.margin';}
   if(family){const parent=add(e,family,v,{role:'analyst',persona:['thirdDownConversionRate','redZoneTouchdownRate'].includes(f.metric)?1:f.metric==='turnoverMargin'?2:0});
    if(parent&&family==='analyst.rushing_poll'&&t&&s.games.some(g=>final(g)&&g.week===s.season.CurrentWeek-1&&((g.home===t.id&&g.homeScore>g.awayScore)||(g.away===t.id&&g.awayScore>g.homeScore))))add(e,'fan.poll_reply',{...v,analystHandle:parent.handle},{role:'fan',team:t,suffix:'reply',priority:e.priority+1,replyTo:parent.id});
   }
  }
 }
 const dialogueEventOrder=addConversations({s,events,stories,byId,teams,players,games,registry,add,teamValues,perfContext,edition,schedule:sameWeek?.dialogueEventOrder??[]});
 // Dependent replies only exist alongside the actual generated parent.
 return {stories:stories.filter(p=>!p.replyTo||byId.has(p.replyTo)),authors:registry.entries,dialogueEventOrder};
}
