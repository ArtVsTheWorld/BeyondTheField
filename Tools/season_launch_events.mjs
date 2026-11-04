// Season-launch stories use active native depth charts and explicit history only.
import {hash} from './story_authors.mjs';
import {titleFutures} from './preseason_events.mjs';
const ranked=n=>Number.isInteger(n)&&n>=1&&n<=25;
const done=g=>g.published!==false&&['HomeWon','AwayWon','Tie'].includes(g.status);
const primaryPositions=['QB','HB','TE','LT','LG','C','RG','RT','LE','RE','LOLB','ROLB','FS','SS'];
export function seasonLaunchEvents(s){
 const pre=s.season.CurrentStage==='PreSeason'&&s.season.CurrentWeekType==='PreSeason',opening=s.season.CurrentStage==='NFLSeason'&&s.season.CurrentWeekType==='RegularSeason'&&s.season.CurrentWeek===0;
 const aftermath=s.season.CurrentStage==='NFLSeason'&&s.season.CurrentWeekType==='RegularSeason'&&s.season.CurrentWeek<=1;
 if(!pre&&!opening&&!aftermath)return [];
 const teams=new Map(s.teams.filter(t=>t.id!==255).map(t=>[t.id,t])),players=new Map(s.players.map(p=>[p.id,p])),events=[];
 const emit=(key,family,voice,values,team,options={})=>events.push({id:'launch:'+key,category:options.category??(pre?'preseason':'schedule'),facts:{family:'launch.'+family,voice,...values},options:{team:team?.id,priority:options.priority??82,national:options.national??ranked(team?.mediaRank),...options}});
 const schedule=s.games.filter(g=>g.year===s.season.CurrentYear&&g.phase==='RegularSeason');
 const healthy=p=>p&&p.injury==='Uninjured';
 const classLabel=p=>(p.redshirt==='Previous'?'redshirt ':'')+String(p.classYear??'').toLowerCase();
 const top=roster=>[...roster].sort((a,b)=>(b.overall??0)-(a.overall??0)||a.id.localeCompare(b.id));
 const futures=pre?titleFutures(s):[],power=new Map(futures.map(f=>[f.team,f]));
 for(const t of teams.values()){
  const own=s.players.filter(p=>p.team===t.id),roster=top(own.filter(healthy)),games=schedule.filter(g=>g.home===t.id||g.away===t.id).sort((a,b)=>a.week-b.week||a.id.localeCompare(b.id)),opener=games[0],opponent=opener&&teams.get(opener.home===t.id?opener.away:opener.home);
  const v={school:t.name,nickname:t.nickname??t.name,hashtag:t.hashtags?.[0]??'',coach:t.headCoach?.name,stadium:t.stadium,opponent:opponent?.name,openerWeek:opener?.week};
  if(pre){
   const previous=t.previousSeason;
   if(previous){
    const vals={...v,wins:previous.wins,losses:previous.losses};
    emit('history:'+t.id,previous.wins<=3?'rebuild':'return', 'beat',vals,t,{priority:87});
    if(previous.playoffRound==='WonNationalChampionship')emit('defense:'+t.id,'champion','official',v,t,{national:true,priority:99});
    else if(['FirstRound','Quarterfinals','Semifinals','NationalChampionship'].includes(previous.playoffRound))emit('playoff:'+t.id,'playoff_return','analyst',{...vals,finish:({FirstRound:'first round',Quarterfinals:'quarterfinals',Semifinals:'semifinals',NationalChampionship:'national championship game'})[previous.playoffRound]},t,{category:'analytics',priority:91});
    const st=previous.stats;
    if(st?.CONFCHAMPSWON>0)emit('conf-defense:'+t.id,'conference_defense','official',v,t,{priority:90});
    if(st?.BOWLSMADE>0)emit('bowl:'+t.id,'bowl_return','beat',{...vals,bowlResult:st.BOWLSWON>0?'a bowl win':'a bowl appearance'},t);
   }
   const coach=t.headCoach;
   if(coach?.name&&Number.isInteger(coach.seasonsWithTeam)){
    if(coach.seasonsWithTeam===0)emit('coach:'+t.id,'new_coach','beat',{...v,coach:coach.name},t,{priority:89});
    else if(coach.seasonsWithTeam>=5)emit('coach:'+t.id,'veteran_coach','beat',{...v,coach:coach.name,seasonNumber:coach.seasonsWithTeam+1},t);
   }
   const style=coach?.style;
   if(['Recruiter','EliteRecruiter','Rainmaker'].includes(style))emit('coach-style:'+t.id,'recruiter','analyst',v,t,{category:'analytics'});
   else if(['TalentDeveloper','Architect'].includes(style))emit('coach-style:'+t.id,'developer','analyst',v,t,{category:'analytics'});
   for(const [side,c] of [['offense',t.offensiveCoordinator],['defense',t.defensiveCoordinator]])if(c?.name&&['Schemer','SchemeGuru','Strategist'].includes(c.style))emit('coordinator:'+t.id+':'+side,'coordinator','beat',{...v,coordinator:c.name,side},t);
   const battles=primaryPositions.map(position=>({position,list:(t.depthChart?.[position]??[]).slice(0,2).map(id=>players.get(id))})).filter(b=>b.list.length===2&&b.list.every(p=>healthy(p)&&p.team===t.id)&&b.list.every(p=>Number.isFinite(p.overall))&&Math.abs(b.list[0].overall-b.list[1].overall)<=3);
   const battle=battles[hash(s.leagueId+'|'+t.id+'|battle')%Math.max(1,battles.length)];
   if(battle)emit('battle:'+t.id,'battle','beat',{...v,position:battle.position,first:battle.list[0].name,second:battle.list[1].name},t,{priority:91});
   const freshmen=roster.filter(p=>p.classYear==='Freshman'&&p.redshirt==='Eligible'),freshman=freshmen[0];
   if(freshman&&freshman.overall>=78)emit('freshman:'+t.id,'freshman','beat',{...v,playerName:freshman.name,position:freshman.position},t,{player:freshman.id,priority:87});
   const young=roster.find(p=>['Freshman','Sophomore'].includes(p.classYear)&&p.overall>=80);
   if(young)emit('breakout:'+t.id,'breakout','analyst',{...v,playerName:young.name,position:young.position,classLabel:classLabel(young)},t,{player:young.id,category:'analytics',priority:87});
   const senior=roster.find(p=>p.classYear==='Senior'&&p.redshirt!=='Current');if(senior)emit('senior:'+t.id,'senior','player',{...v,classLabel:classLabel(senior)},t,{player:senior.id,national:false});
   const nil=roster.find(p=>p.nil>0);if(nil)emit('nil:'+t.id,'nil','player',v,t,{player:nil.id,national:false,priority:75});
   const honors=(s.preseasonHonors??[]).filter(a=>a.team===t.id&&a.year===s.season.CurrentYear&&!a.type.endsWith('_CONF'));
   const star=players.get(honors[0]?.player)??roster[0];if(star&&honors.length)emit('spotlight:'+t.id,'spotlight','official',{...v,playerName:star.name,position:star.position},t,{player:star.id,category:'awards',priority:88});
   const hopeful=roster.find(p=>['QB','HB','WR'].includes(p.position)&&p.overall>=90&&p.classYear!=='Freshman');if(hopeful)emit('hopeful:'+t.id,'heisman','analyst',{...v,playerName:hopeful.name,position:hopeful.position},t,{player:hopeful.id,category:'heisman',priority:89});
   const f=power.get(t.id);if(f&&f.modelRank<=25&&!ranked(t.mediaRank))emit('darkhorse:'+t.id,'darkhorse','analyst',v,t,{national:true,category:'analytics',priority:89});
   const rankedOpp=games.map(g=>teams.get(g.home===t.id?g.away:g.home)).filter(o=>ranked(o?.mediaRank));
   if(games.length>=10&&rankedOpp.length===0)emit('schedule-opportunity:'+t.id,'schedule_opportunity','analyst',v,t,{category:'analytics'});
   for(const p of roster){const prior=p.previousSeasonStats?.find(x=>x.stats.YEARBYYEARTEAMINDEX!==t.id&&(x.stats.PASSYARDS>=1500||x.stats.RUSHYARDS>=700||x.stats.RECEIVEYARDS>=700));if(!prior)continue;
    const former=teams.get(prior.stats.YEARBYYEARTEAMINDEX);if(former){emit('transfer:'+t.id,'transfer','beat',{...v,playerName:p.name,position:p.position,formerSchool:former.name},t,{player:p.id,relatedTeams:[former.id],priority:88});break;}}
  }
  if(opening){
   emit('kickoff:'+t.id,'kickoff','official',v,t,{national:false,priority:88});
   if(opener&&opponent&&!done(opener)){
    if(opener.week===0){emit('opener:'+t.id,'opening_preview','analyst',v,t,{relatedTeams:[opponent.id],priority:89});
     if(t.stadium&&opener.home===t.id&&opener.neutral===false)emit('venue:'+t.id,'venue','official',v,t,{national:false,priority:87});
     if(t.headCoach?.seasonsWithTeam===0)emit('debut:'+t.id,'coach_debut','beat',v,t,{priority:88});
    }else emit('countdown:'+t.id,'countdown','official',v,t,{national:false,priority:84});
    const starting=players.get(t.depthChart?.QB?.[0]);if(healthy(starting)&&starting.team===t.id)emit('qb:'+t.id,'depth','beat',{...v,playerName:starting.name,position:'QB',classLabel:classLabel(starting)},t,{player:starting.id,priority:86});
    const p=roster[hash(s.leagueId+'|'+t.id+'|opening-player')%Math.max(1,roster.length)];if(p)emit('player:'+t.id,'player_opening'+(p.position==='QB'?'_qb':''),'player',v,t,{player:p.id,national:false});
   }
  }
 }
 if(pre)for(const c of s.conferences??[]){if(c.independent)continue;const contenders=c.teams.map(id=>power.get(id)).filter(Boolean).sort((a,b)=>b.power-a.power||a.team-b.team),t=teams.get(contenders[0]?.team);
  if(t&&contenders.length>=4)emit('favorite:'+c.id,'favorite','analyst',{school:t.name,conference:c.name},t,{category:'analytics',national:false,relatedTeams:c.teams,priority:88});}
 if(opening){
  const watching=new Map();
  for(const r of [...(s.recruitStatuses??[])].sort((a,b)=>(a.nationalRank??9999)-(b.nationalRank??9999)||a.player.localeCompare(b.player))){
   const p=players.get(r.player);if(!p||p.team!==255||!['Top10','Top5','Top3','Battle'].includes(r.stage))continue;
   for(const id of (r.topSchools??[]).slice(0,3)){const t=teams.get(id),g=schedule.find(g=>g.week===0&&(g.home===id||g.away===id));if(!t||!g||(watching.get(id)??0)>=2)continue;
    watching.set(id,(watching.get(id)??0)+1);emit('recruit-watch:'+p.id+':'+id,'recruit_watch','recruit',{school:t.name,position:p.position},t,{player:p.id,category:'recruiting',national:r.nationalRank<=25,priority:79});
    const starter=players.get(t.depthChart?.[p.position]?.[0]);if(starter?.team===id)emit('recruit-tag:'+p.id+':'+id,'recruit_tag','recruit',{school:t.name,playerName:starter.name,tagPlayerId:starter.id},t,{player:p.id,category:'recruiting',national:false,priority:77});
   }
   if(r.nationalRank>=1&&r.nationalRank<=25)emit('hs:'+p.id,'high_school','recruit',{position:p.position},null,{player:p.id,category:'recruiting',national:true,priority:76});
  }
  for(const visit of s.recruitVisits??[]){const p=players.get(visit.player),t=teams.get(visit.team);if(p&&t&&visit.week===0&&visit.phase==='RegularSeason')emit('visit:'+p.id+':'+t.id,'visit','recruit',{school:t.name},t,{player:p.id,category:'recruiting',priority:85});}
 }
 if(aftermath)for(const g of schedule.filter(g=>g.week===0&&done(g)&&g.homeScore!==g.awayScore)){
  const winner=teams.get(g.homeScore>g.awayScore?g.home:g.away),loser=teams.get(g.homeScore>g.awayScore?g.away:g.home),margin=Math.abs(g.homeScore-g.awayScore);if(!winner||!loser)continue;
  const values={school:winner.name,opponent:loser.name,score:Math.max(g.homeScore,g.awayScore)+'\u2013'+Math.min(g.homeScore,g.awayScore),margin};
  emit('overreaction:'+g.id,margin>=28?'dominant_debut':margin<=3?'close_debut':'opening_takeaway','analyst',values,winner,{category:'analytics',relatedTeams:[loser.id],national:true,eventWeek:0,thread:'game:'+g.id,priority:86});
 }
 return events;
}
