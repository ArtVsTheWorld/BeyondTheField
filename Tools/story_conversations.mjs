import {hash} from './story_authors.mjs';
const personalities=new Set(['Leader','Intense','Entertainer','TeamPlayer','Unpredictable']);
export function addConversations({s,events,stories,byId,teams,players,games,registry,add,teamValues,perfContext,edition,schedule=[]}){
 const roots=new Map(stories.filter(p=>p.id===p.eventId+':main').map(p=>[p.eventId,p]));
 const authorFor=(team,e,purpose,exclude=null,position=null)=>{
  let pool=s.players.filter(p=>p.team===team?.id&&p.id!==exclude&&p.injury==='Uninjured');const same=pool.filter(p=>p.position===position);if(same.length)pool=same;
  pool.sort((a,b)=>a.id.localeCompare(b.id));return pool.length?pool[hash(edition+'|'+e.id+'|'+purpose)%pool.length]:null;
 };
 const seenPerformances=new Set(),priorOrder=new Map(schedule.map((id,i)=>[id,i]));
 // Persist the admission order, so a later reopen cannot let a new high-priority
 // offer steal a reaction slot that was already published earlier in the week.
 const ordered=[...events].sort((a,b)=>(priorOrder.get(a.id)??Number.MAX_SAFE_INTEGER)-(priorOrder.get(b.id)??Number.MAX_SAFE_INTEGER)||b.priority-a.priority||a.id.localeCompare(b.id));
 for(const e of ordered){
  const root=roots.get(e.id),f=e.facts,t=teams.get(e.teamIds[0]);if(!root)continue;
  if(['recruiting','offers'].includes(e.category)&&root.voice==='recruit'){
   const recruit=players.get(e.playerId),team=teams.get(e.teamIds.find(id=>teams.get(id)?.name===f.school));if(!team||!recruit)continue;
   const hard=e.category==='recruiting'&&f.newlyObserved&&f.commitment==='HardCommitted',offer=e.category==='offers';if(!hard&&!offer)continue;
   const athlete=authorFor(team,e,'welcome',null,recruit.position),values={...teamValues(team),...f};
   if(athlete){const personality=personalities.has(athlete.personality)?athlete.personality:'Neutral';add(e,hard?'reply.player.commit.'+personality:'reply.player.offer',values,{role:'player',team,player:athlete,suffix:'welcome',priority:e.priority+1,replyTo:root.id});}
   // One recruit is not greeted by an automatic wall of accounts.
   if(team.id===s.userTeamIndex||hash(e.id+'|fan')%3===0)add(e,hard?'reply.fan.commit':'reply.fan.offer',values,{role:'fan',team,persona:1,suffix:'welcome-fan',priority:e.priority-2,replyTo:root.id});
  }else if(e.category==='results'){
   const g=games.get(f.gameId);if(!g||f.tie)continue;const user=e.teamIds.includes(s.userTeamIndex),winner=g.homeScore>g.awayScore?g.home:g.away,team=teams.get(user?s.userTeamIndex:winner);
   if(!team||!user&&(!e.scopes.includes('national')||hash(e.id+'|reaction')%3))continue;
   add(e,winner===team.id?'reply.fan.beat_win':'reply.fan.beat_loss',{...teamValues(team),...f},{role:'fan',team,suffix:'report-reply',priority:e.priority+1,replyTo:root.id});
  }else if(e.category==='player-stats'){
   const p=players.get(e.playerId),team=p&&teams.get(p.team),c=perfContext(e);if(!c?.win||!team)continue;
   const key=f.gameId+':'+team.id;if(seenPerformances.has(key))continue;seenPerformances.add(key);
   if(!e.scopes.includes('national')&&team.id!==s.userTeamIndex)continue;
   const profile=registry.get(s,'player',team,p),values={...c,playerHandle:profile.handle};
   // A program tags the actual athlete's persisted handle, not an unrelated subject.
   if(f.stats.rushingTouchdowns>=2||f.stats.receivingTouchdowns>=2||f.stats.sacks>=2)add(e,'official.performance.tag',values,{role:'official',team,suffix:'team',priority:e.priority+1});
   const personality=personalities.has(p.personality)?p.personality:'Neutral';const family=p.position==='QB'&&['Leader','Intense','Neutral'].includes(personality)?'player.performance.QB':'player.performance.'+personality;
   const self=add(e,family,values,{role:'player',team,player:p,suffix:'self',priority:e.priority+2});
   if(self){add(e,'reply.fan.player_win',values,{role:'fan',team,persona:1,suffix:'fan-player',priority:e.priority+3,replyTo:self.id});
    const teammate=authorFor(team,e,'teammate',p.id);if(teammate&&hash(e.id+'|teammate')%2===0)add(e,'reply.player.teammate',values,{role:'player',team,player:teammate,suffix:'teammate',priority:e.priority-1,replyTo:self.id});
   }
  }else if(e.category==='polls'&&f.movement==='up'&&(t?.id===s.userTeamIndex||f.rank<=10&&f.previousRank-f.rank>=3)){
   add(e,'fan.rank_up',{...teamValues(t),...f},{role:'fan',team:t,persona:1,suffix:'rank-reply',priority:e.priority,replyTo:root.id});
  }else if(e.category==='schedule'&&f.rivalry&&e.teamIds.includes(s.userTeamIndex)){
   const g=games.get(f.gameId),team=teams.get(s.userTeamIndex);if(g)add(e,'fan.preview.rivalry',{...teamValues(team),opponent:s.userTeamIndex===g.home?f.away:f.home},{role:'fan',team,persona:1,suffix:'rivalry-reply',priority:e.priority,replyTo:root.id});
  }else if(e.category==='analytics'&&e.teamIds.includes(s.userTeamIndex)&&!stories.some(p=>p.replyTo===root.id)){
   const low=f.metric==='thirdDownConversionRate'&&f.rate<=.3||f.metric==='redZoneTouchdownRate'&&f.rate<=.45||f.metric==='turnoverMargin'&&f.margin<0;
   add(e,low?'reply.fan.analyst_low':'reply.fan.analyst_high',{...teamValues(t),...f},{role:'fan',team:t,persona:1,suffix:'analysis-reply',priority:e.priority+1,replyTo:root.id});
  }
 }
 return ordered.map(e=>e.id);
}
