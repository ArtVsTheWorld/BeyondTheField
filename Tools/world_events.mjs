const final=g=>g.published!==false&&['HomeWon','AwayWon','Tie'].includes(g.status);
const ranked=n=>Number.isInteger(n)&&n>=1&&n<=25;
export function recruitSignificance(stars,prestige,rank){return rank===1?'number-one':stars>=4&&Number.isFinite(prestige)&&prestige<=2?'program-changer':stars===5?'five-star':Number.isFinite(prestige)&&prestige>=4.5&&stars>0&&stars<=2?'questioned':'normal';}
export function worldEvents(s){
 const week=s.season.CurrentWeek,teams=new Map(s.teams.filter(t=>t.id!==255).map(t=>[t.id,t])),players=new Map(s.players.map(p=>[p.id,p])),events=[];
 const games=s.games.filter(g=>g.year===s.season.CurrentYear&&g.phase===s.season.CurrentWeekType&&g.week<=week&&final(g));
 const recent=games.filter(g=>g.week>=week-1),emit=(id,category,facts,options={})=>events.push({id,category,facts,options});
 for(const g of recent){if(g.homeScore===g.awayScore)continue;const winner=g.homeScore>g.awayScore?g.home:g.away,loser=winner===g.home?g.away:g.home,w=teams.get(winner),l=teams.get(loser);if(!w||!l)continue;
  const observed=s.pregameGames?.[g.id],rank=t=>observed?.ranks?.[t.id]??(g.week===week-1?t.mediaLastRank:t.mediaRank),wr=rank(w),lr=rank(l);
  const lineUpset=observed?.favorite===loser&&observed.spread>=10,pollUpset=Number.isInteger(wr)&&Number.isInteger(lr)&&ranked(lr)&&(!ranked(wr)||wr-lr>=8);
  if(lineUpset||pollUpset){const huge=lineUpset&&observed.spread>=20||ranked(lr)&&lr<=5&&!ranked(wr);emit('upset:'+g.id,'upsets',{gameId:g.id,winner:w.name,loser:l.name,winnerRank:ranked(wr)?wr:null,loserRank:ranked(lr)?lr:null,winnerLabel:(Number.isInteger(wr)?(ranked(wr)?'#'+wr:'Unranked')+' ':'')+w.name,loserLabel:(ranked(lr)?'#'+lr+' ':'')+l.name,score:Math.max(g.homeScore,g.awayScore)+'–'+Math.min(g.homeScore,g.awayScore),huge,importance:huge?'major':'notable',family:'world.upset'},{team:winner,relatedTeams:[winner,loser],national:true,priority:huge?112:103,thread:'game:'+g.id,eventWeek:g.week});}
 }
 for(const t of teams.values()){
  const played=games.filter(g=>g.home===t.id||g.away===t.id).sort((a,b)=>b.week-a.week||b.id.localeCompare(a.id));if(!played.length||played[0].week<week-1)continue;
  if(played.length!==t.wins+t.losses+(t.ties??0))continue;
  let wins=0;for(const g of played){if((g.home===t.id?g.homeScore:g.awayScore)>(g.home===t.id?g.awayScore:g.homeScore))wins++;else break;}
  if(wins>=4)emit('streak:'+t.id,'streaks',{school:t.name,count:wins,family:'world.streak'},{team:t.id,national:wins>=7,priority:88});
 }
 const awardNames={Offensive_Player_of_Week:'national offensive player of the week',Defensive_Player_of_Week:'national defensive player of the week',Offensive_Player_of_Week_Conf:'conference offensive player of the week',Defensive_Player_of_Week_Conf:'conference defensive player of the week'};
 for(const a of s.weeklyAwards??[]){const p=players.get(a.player),t=teams.get(a.team);if(!p||!t||!awardNames[a.type]||![week-1,week].includes(a.week))continue;
  if(!s.performances.some(x=>x.player===p.id&&x.team===a.team&&recent.some(g=>g.id===x.game&&g.week===a.week)))continue;
  const national=!a.type.endsWith('_Conf');emit('award:'+a.id,'awards',{school:t.name,playerName:p.name,award:awardNames[a.type],awardWeek:a.week,family:'world.award'},{team:t.id,player:p.id,national,priority:national?101:91,eventWeek:a.week});
 }
 const statFields={PassYards:'PASSYARDS',PassTDS:'PASSTDS',RushYards:'RUSHYARDS',RushTDS:'RUSHTDS',ReceivingYards:'RECEIVEYARDS',ReceivingTDS:'RECEIVETDS',ReceivingCatches:'RECEIVECATCHES',DefensiveInts:'DSECINTS',DefensiveSacks:'DLINESACKS'};
 const statNames={PassYards:'passing yards',PassTDS:'passing touchdowns',RushYards:'rushing yards',RushTDS:'rushing touchdowns',ReceivingYards:'receiving yards',ReceivingTDS:'receiving touchdowns',ReceivingCatches:'receptions',DefensiveInts:'interceptions',DefensiveSacks:'sacks'};
 for(const r of s.records??[]){if(r.year!==s.season.CurrentSeasonYear||!statFields[r.metric])continue;const p=s.players.find(p=>p.team===r.team&&p.name===r.playerName),t=teams.get(r.team);if(!p||!t)continue;
  const field=statFields[r.metric],old=(s.recordBaseline??[]).find(x=>x.scope===r.scope&&x.scopeId===r.scopeId&&x.period===r.period&&x.metric===r.metric);
  const matching=s.performances.filter(x=>x.player===p.id&&recent.some(g=>g.id===x.game));
  const actual=r.period==='game'?matching.find(x=>(r.metric==='DefensiveSacks'?x.stats.DLINESACKS+.5*x.stats.DLINEHALFSACK:x.stats[field])===r.value):p.seasonStats?.find(x=>(r.metric==='DefensiveSacks'?x.stats.DLINESACKS+.5*x.stats.DLINEHALFSACK:x.stats[field])===r.value);
  if(!actual)continue;
  // A season mark needs an observed increase; otherwise it may have been set weeks ago.
  if(old&&r.value<=old.value)continue;
  const broken=old&&r.value>old.value;if(r.period==='season'&&!broken)continue;
  const scope=r.scope==='school'?t.name:r.scope==='conference'?s.conferences.find(c=>c.id===r.scopeId)?.name:'FBS';if(!scope)continue;
  emit('record:'+r.scope+':'+r.scopeId+':'+r.period+':'+r.metric+':'+r.value,'records',{playerName:p.name,school:t.name,value:r.value,metric:statNames[r.metric],recordScope:scope,period:r.period==='game'?'single-game':'single-season',recordVerb:broken?'broke':'now holds',family:broken?'world.record_broken':'world.record_holder'},{team:t.id,player:p.id,national:r.scope==='national',priority:broken?108:92});
 }
 for(const c of s.commitmentChanges??[]){const p=players.get(c.player),old=teams.get(c.from),next=teams.get(c.to);if(!p||!old)continue;
  emit('recruit-change:'+p.id+':'+old.id+':'+(next?.id??'open'),'recruiting',{playerName:p.name,school:old.name,oldSchool:old.name,newSchool:next?.name??null,stars:p.starRating??null,family:next?(old.rivals?.includes(next.id)?'world.rivalry_flip':'world.flip'):'world.decommit',flipped:Boolean(next),decommitted:!next,importance:p.starRating===5?'major':'notable'},{team:old.id,player:p.id,relatedTeams:next?[next.id]:[],national:p.starRating>=4,priority:p.starRating===5?108:94});
 }
 const upcoming=s.games.filter(g=>g.year===s.season.CurrentYear&&g.phase===s.season.CurrentWeekType&&g.week===week&&!final(g));
 for(const g of upcoming){const h=teams.get(g.home),a=teams.get(g.away);if(!h||!a)continue;
  const recordVerified=t=>{const played=games.filter(g=>g.home===t.id||g.away===t.id);return played.length===t.wins+t.losses+(t.ties??0)&&played.filter(g=>(g.home===t.id?g.homeScore:g.awayScore)>(g.home===t.id?g.awayScore:g.homeScore)).length===t.wins;};
  if(recordVerified(h)&&recordVerified(a)&&h.wins>=3&&a.wins>=3&&h.losses===0&&a.losses===0&&!(h.ties>0)&&!(a.ties>0))emit('collision:'+g.id,'schedule',{home:h.name,away:a.name,homeWins:h.wins,awayWins:a.wins,family:'world.undefeated'},{team:h.id,relatedTeams:[a.id],national:true,priority:98});
  for(const e of [...events].filter(e=>e.category==='upsets'&&e.options.eventWeek===week-1)){
   const loser=e.options.relatedTeams.find(id=>teams.get(id)?.name===e.facts.loser);if(![g.home,g.away].includes(loser))continue;
   emit('bounceback:'+g.id+':'+loser,'schedule',{school:teams.get(loser).name,opponent:loser===g.home?a.name:h.name,family:'world.bounceback'},{team:loser,relatedTeams:[g.home,g.away],national:e.facts.huge,priority:89});
  }
 }
 return events;
}
