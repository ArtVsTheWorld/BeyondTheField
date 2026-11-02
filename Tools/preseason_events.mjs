import {hash} from './story_authors.mjs';
import {rosterStrengths} from './betting_model.mjs';
const ranked=n=>Number.isInteger(n)&&n>=1&&n<=25;
export function titleFutures(s,strengths=rosterStrengths(s)){
 const rows=s.teams.filter(t=>t.id!==255&&strengths.has(t.id)).map(t=>{const r=strengths.get(t.id);return {team:t.id,school:t.name,power:.45*r.off+.45*r.def+.1*r.st};});
 if(rows.length<2)return [];
 const maximum=Math.max(...rows.map(r=>r.power));for(const r of rows)r.weight=Math.exp((r.power-maximum)/6);
 const total=rows.reduce((n,r)=>n+r.weight,0);for(const r of rows){r.probability=r.weight/total;r.odds=r.probability>=.5?'-'+Math.round(r.probability/(1-r.probability)*20)*5:'+'+Math.max(100,Math.min(250000,Math.round((1-r.probability)/r.probability*4)*25));}
 return rows.sort((a,b)=>b.probability-a.probability||a.team-b.team).map((r,i)=>({...r,modelRank:i+1,simulated:true}));
}
export function preseasonEvents(s,{strengths}={}){
 if(s.season.CurrentWeekType!=='PreSeason'||s.season.CurrentStage!=='PreSeason')return [];
 const teams=new Map(s.teams.filter(t=>t.id!==255).map(t=>[t.id,t])),players=new Map(s.players.map(p=>[p.id,p])),events=[];
 const emit=(id,category,facts,options={})=>events.push({id:'preseason:'+id,category,facts:{preseason:true,...facts},options});
 const honors=(s.preseasonHonors??[]).filter(a=>a.year===s.season.CurrentYear&&teams.has(a.team)&&players.get(a.player)?.team===a.team);
 const openingGames=s.games.filter(g=>g.year===s.season.CurrentYear&&g.phase==='RegularSeason'&&g.status==='Unplayed');
 const futures=titleFutures(s,strengths),futureMap=new Map(futures.map(x=>[x.team,x]));
 for(const t of teams.values()){
  const preseasonRank=t.mediaRank,teamHonors=honors.filter(a=>a.team===t.id),national=[...new Map(teamHonors.filter(a=>!a.type.endsWith('_CONF')).map(a=>[a.player,a])).values()];
  const opener=openingGames.filter(g=>g.home===t.id||g.away===t.id).sort((a,b)=>a.week-b.week||a.id.localeCompare(b.id))[0];
  const opponent=opener&&teams.get(opener.home===t.id?opener.away:opener.home);
  if(ranked(preseasonRank))emit('poll:'+t.id,'polls',{school:t.name,rank:preseasonRank,family:'preseason.poll.beat',voice:'beat'},{team:t.id,national:true,priority:preseasonRank<=5?96:88});
  emit('hype:'+t.id,'preseason',{school:t.name,family:'preseason.team.hype',voice:'official'},{team:t.id,national:ranked(preseasonRank)&&preseasonRank<=10,priority:80});
  emit('fan:'+t.id,'preseason',{school:t.name,family:hash(t.id+'|preseason-mood')%3===0?'preseason.fan.nervous':'preseason.fan.excited',voice:'fan'},{team:t.id,national:false,priority:77});
  const roster=s.players.filter(p=>p.team===t.id&&p.injury==='Uninjured').sort((a,b)=>a.id.localeCompare(b.id));
  const highlighted=teamHonors.map(a=>players.get(a.player)).find(p=>p?.injury==='Uninjured');
  const p=highlighted??roster[hash(s.leagueId+'|'+t.id+'|camp')%Math.max(1,roster.length)];
  if(p){const personality=['Leader','Intense','Entertainer','TeamPlayer','Unpredictable'].includes(p.personality)?p.personality:'Neutral',voice=p.position==='QB'&&['Leader','Intense','TeamPlayer','Neutral'].includes(personality)?'QB':personality;
   emit('camp:'+t.id,'preseason',{school:t.name,playerName:p.name,family:'preseason.player.'+voice,voice:'player'},{team:t.id,player:p.id,national:false,priority:79});}
  if(opener&&opponent)emit('opener:'+t.id,'schedule',{school:t.name,opponent:opponent.name,openerWeek:opener.week,family:'preseason.opener.beat',voice:'beat'},{team:t.id,relatedTeams:[opponent.id],national:ranked(preseasonRank)&&preseasonRank<=10,priority:85,thread:'preseason-opener:'+opener.id});
  if(national.length)emit('outlook:'+t.id,'analytics',{school:t.name,count:national.length,selectionLabel:national.length===1?'selection':'selections',playerName:players.get(national[0].player).name,family:'preseason.outlook.analyst',voice:'analyst'},{team:t.id,national:ranked(preseasonRank)||national.length>=3,priority:89});
  const f=futureMap.get(t.id);if(f)emit('futures:'+t.id,'lines',{school:t.name,odds:f.odds,modelRank:f.modelRank,simulated:true,family:'preseason.title.model',voice:'model'},{team:t.id,national:f.modelRank<=10,priority:83});
  if(f&&ranked(preseasonRank)&&Math.abs(preseasonRank-f.modelRank)>=8&&(preseasonRank<=15||f.modelRank<=15))emit('poll-debate:'+t.id,'analytics',{school:t.name,rank:preseasonRank,modelRank:f.modelRank,simulated:true,debate:true,family:preseasonRank>f.modelRank?'preseason.respect.analyst':'preseason.caution.analyst',voice:'analyst'},{team:t.id,national:true,priority:90});
  if(ranked(preseasonRank)&&ranked(t.coachesRank)&&Math.abs(preseasonRank-t.coachesRank)>=6)emit('poll-comparison:'+t.id,'polls',{school:t.name,rank:preseasonRank,coachesRank:t.coachesRank,family:'preseason.coaches.beat',voice:'beat'},{team:t.id,national:true,priority:88});
  const schedule=openingGames.filter(g=>g.home===t.id||g.away===t.id).sort((a,b)=>a.week-b.week||a.id.localeCompare(b.id));
  const windows=schedule.map(g=>({start:g.week,end:g.week+3,opponents:schedule.filter(x=>x.week>=g.week&&x.week<=g.week+3).map(x=>teams.get(x.home===t.id?x.away:x.home)).filter(o=>o&&ranked(o.mediaRank))})).filter(w=>w.opponents.length>=2).sort((a,b)=>b.opponents.length-a.opponents.length||a.start-b.start);
  const gauntlet=windows[0];if(gauntlet)emit('gauntlet:'+t.id,'schedule',{school:t.name,count:gauntlet.opponents.length,startWeek:gauntlet.start,endWeek:gauntlet.end,opponents:gauntlet.opponents.map(o=>'No. '+o.mediaRank+' '+o.name).join(', '),family:'preseason.gauntlet.analyst',voice:'analyst'},{team:t.id,relatedTeams:gauntlet.opponents.map(o=>o.id),national:true,priority:92});
 }
 for(const c of s.conferences??[]){
  if(c.independent)continue;
  const selections=honors.filter(a=>a.type.endsWith('_CONF')&&a.conferenceId===c.id),counts=new Map();
  for(const a of selections){const ids=counts.get(a.team)??new Set();ids.add(a.player);counts.set(a.team,ids);}
  const leaders=[...counts].map(([team,ids])=>({team,count:ids.size})).sort((a,b)=>b.count-a.count||a.team-b.team);if(!leaders.length)continue;
  const total=new Set(selections.map(a=>a.player)).size,top=leaders[0].count,leading=leaders.filter(x=>x.count===top),names=leading.map(x=>teams.get(x.team).name).join(', ');
  emit('talent-map:'+c.id,'analytics',{conference:c.name,count:total,leaders:names,leaderCount:top,leadVerb:leading.length===1?'leads':'share the lead',family:'preseason.talent.analyst',voice:'analyst'},{relatedTeams:[...counts.keys()],national:false,primaryScope:'conference',priority:91});
 }
 for(const a of honors){
  const t=teams.get(a.team),p=players.get(a.player),conference=s.conferences.find(c=>c.id===a.conferenceId),isConference=a.type.endsWith('_CONF');if(isConference&&!conference)continue;
  const first=a.type.includes('1ST'),award=(first?'first-team':'second-team')+' preseason '+(isConference?'All-'+conference.name:'All-American');
  emit('honor:'+a.id,'awards',{school:t.name,playerName:p.name,position:p.position,award,family:'preseason.honor.beat',voice:'beat'},{team:t.id,player:p.id,national:!isConference,priority:isConference?84:first?95:92});
 }
 const committed=new Set(s.commitments.map(c=>c.player));
 const recruits=(s.recruitStatuses??[]).filter(r=>!committed.has(r.player)&&['Top10','Top5','Top3','Battle'].includes(r.stage)&&r.nationalRank>=1&&r.nationalRank<=100).sort((a,b)=>a.nationalRank-b.nationalRank||a.player.localeCompare(b.player));
 for(const r of recruits){const p=players.get(r.player);if(!p||p.team!==255)continue;const values={playerName:p.name,position:p.position,nationalRank:r.nationalRank,recruitStars:p.starRating,starDetail:p.starRating?p.starRating+'-star ':''};
  emit('recruit-watch:'+p.id,'recruiting',{...values,family:'preseason.recruit.watch',voice:'beat'},{player:p.id,national:true,priority:r.nationalRank===1?93:81});
  if(r.nationalRank<=10)emit('recruit-self:'+p.id,'recruiting',{...values,family:'preseason.recruit.self',voice:'recruit'},{player:p.id,national:true,priority:78});
 }
 return events;
}
