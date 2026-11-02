import {phaseIndex} from './publication_timeline.mjs';
import {nationalCoverage} from './national_editorial.mjs';
// Advanced rates use the player's recorded games, never the team's games or
// invented targets/pass-block snaps. Every numerator/denominator is checked
// against the published game caches before a season story is eligible.
const final=g=>g.published!==false&&['HomeWon','AwayWon','Tie'].includes(g.status);
const family=type=>/^(?:Season|Game)(Offensive(?:KPReturn)?Stats)$/.test(type)?'offense':/^(?:Season|Game)(Defensive(?:KPReturn)?Stats)$/.test(type)?'defense':/^(?:Season|Game)OLineStats$/.test(type)?'line':/^(?:Season|Game)KickingStats$/.test(type)?'kicking':null;
const nonnegative=n=>Number.isFinite(n)&&n>=0;
const one=n=>n.toFixed(1),percent=n=>one(n*100);
const rotation=(a,w)=>[...a].sort((x,y)=>score(x.id,w)-score(y.id,w)||x.id.localeCompare(y.id));
function score(id,w){let h=w;for(const c of id)h=Math.imul(h^c.charCodeAt(0),16777619);return h>>>0;}
export function verifiedPlayerStats(s,p,kind,index=null){
 const seasons=(p.seasonStats??[]).filter(r=>family(r.type)===kind);
 // Two base/derived rows could be duplicate or conflicting; don't add them.
 if(seasons.length!==1)return null;
 const st=seasons[0].stats,n=st.GAMESPLAYED;
 if(!Number.isInteger(n)||n<1)return null;
 const games=index?.games??new Map(s.games.filter(g=>g.year===s.season.CurrentYear&&(phaseIndex(g.phase)>=0&&phaseIndex(g.phase)<phaseIndex(s.season.CurrentWeekType)||g.phase===s.season.CurrentWeekType&&g.week<=s.season.CurrentWeek)&&final(g)).map(g=>[g.id,g]));
 const rows=(index?(index.players.get(p.id)??[]):s.performances).filter(r=>r.player===p.id&&r.team===p.team&&games.has(r.game)&&[games.get(r.game).home,games.get(r.game).away].includes(p.team)&&family(r.type)===kind);
 if(rows.length!==n||new Set(rows.map(r=>r.game)).size!==n)return null;
 const memo=new Map();
 const read=key=>{if(!memo.has(key)){const values=rows.map(r=>r.stats[key]);memo.set(key,nonnegative(st[key])&&values.every(nonnegative)&&values.reduce((a,b)=>a+b,0)===st[key]?st[key]:null);}return memo.get(key);};
 return {n,read,rows};
}
export function deepAnalyticsEvents(s,{bounded=true}={}){
 if(s.reconstructed||s.season.CurrentStage!=='NFLSeason')return [];
 const teams=new Map(s.teams.filter(t=>t.id!==255).map(t=>[t.id,t])),events=[],covered=nationalCoverage(s);
 const index={players:new Map(),games:new Map(s.games.filter(g=>g.year===s.season.CurrentYear&&(phaseIndex(g.phase)>=0&&phaseIndex(g.phase)<phaseIndex(s.season.CurrentWeekType)||g.phase===s.season.CurrentWeekType&&g.week<=s.season.CurrentWeek)&&final(g)).map(g=>[g.id,g]))};
 for(const r of s.performances){const list=index.players.get(r.player)??[];list.push(r);index.players.set(r.player,list);}
 for(const p of s.players){const t=teams.get(p.team);if(!t)continue;
  const candidates=[];
  const add=(key,values,priority=83)=>candidates.push({id:`deep:${p.id}:${key}`,category:'analytics',facts:{family:'deep.'+key,voice:'analyst',playerName:p.name,school:t.name,...values},options:{team:p.team,player:p.id,national:covered.has(t.id),priority,thread:'deep:'+p.id}});
  const off=verifiedPlayerStats(s,p,'offense',index);
  if(off&&off.n>=3){const v=off.read,att=v('RUSHATTEMPTS'),broken=v('RUSHBROKENTACKLES'),contact=v('RUSHYARDSAFTER1STHIT'),ry=v('RUSHYARDS'),rec=v('RECEIVECATCHES'),yards=v('RECEIVEYARDS'),yac=v('RECEIVEYARDSAFTER'),drops=v('RECEIVEDROPS');
   if(att>=40&&broken>=10)add('broken-tackles',{broken,attempts:att,rate:one(broken/att*100)});
   if(att>=40&&contact>=100&&ry!==null)add('after-contact',{yards:contact,attempts:att,rate:one(contact/att)});
   if(rec>=15&&yards>=200&&yac!==null&&yac<=yards)add('yac-share',{yac,yards,rate:percent(yac/yards)});
   if(rec>=20&&drops>=3)add('drops',{catches:rec,drops,rate:percent(drops/(rec+drops)),negative:true});
   if(['HB','RB','FB'].includes(p.position)&&ry>=300&&yards>=150)add('receiving-back',{rushing:ry,receiving:yards,catches:rec},87);
  }
  const def=verifiedPlayerStats(s,p,'defense',index);
  if(def&&def.n>=3){const v=def.read,solo=v('DEFTACKLES'),assist=v('ASSDEFTACKLES'),sacks=v('DLINESACKS'),half=v('DLINEHALFSACK');
   if(solo!==null&&assist!==null&&solo+assist>=25)add('tackles-game',{total:solo+assist,games:def.n,rate:one((solo+assist)/def.n)});
   if(sacks!==null&&half!==null&&sacks+half*.5>=3)add('sacks-game',{total:sacks+half*.5,games:def.n,rate:( (sacks+half*.5)/def.n).toFixed(2)});
   for(const [key,field,min] of [['tfl-game','DEFTACKLESFORLOSS',6],['ints-game','DSECINTS',2],['pbu-game','DEFPASSDEFLECTIONS',5],['forced-game','DLINEFORCEDFUMBLES',2],['recoveries-game','DLINEFUMBLERECOVERIES',2]]){const total=v(field);if(total>=min)add(key,{total,games:def.n,rate:(total/def.n).toFixed(2)});}
  }
  const line=verifiedPlayerStats(s,p,'line',index);
  if(line&&line.n>=3){const snaps=line.read('DOWNSPLAYED'),sacks=line.read('OLINESACKSALLOWED'),pancakes=line.read('OLINEPANCAKES');
   if(snaps>=150&&sacks!==null)add('line-sacks',{snaps,sacks,rate:(sacks/snaps*100).toFixed(2),negative:sacks/snaps>.015});
   if(pancakes>=12)add('pancakes',{total:pancakes,games:line.n,rate:one(pancakes/line.n)});
  }
  const kicking=verifiedPlayerStats(s,p,'kicking',index);
  if(kicking&&kicking.n>=3){const v=kicking.read;
   for(const [key,a,m,min] of [['long-kicks','KICKFGATTEMPTS50ORMORE','KICKFGMADE50ORMORE',3],['mid-kicks','KICKFGATTEMPTS40TO49','KICKFGMADE40TO49',5]]){const attempts=v(a),made=v(m);if(attempts>=min&&made!==null&&made<=attempts)add(key,{attempts,made,rate:percent(made/attempts),negative:made/attempts<.65});}
   const kickoffs=v('KICKNUMKICKOFFS'),tb=v('KICKTOUCHBACKS');if(kickoffs>=20&&tb!==null&&tb<=kickoffs)add('touchbacks',{attempts:kickoffs,total:tb,rate:percent(tb/kickoffs)});
   const punts=v('PUNTATTEMPTS'),inside=v('PUNTIN20'),ptb=v('PUNTTOUCHBACKS');if(punts>=15&&inside!==null&&ptb!==null&&inside+ptb<=punts)add('punt-placement',{attempts:punts,total:inside,touchbacks:ptb,rate:percent(inside/punts)});
  }
  for(const stats of [off,def].filter(Boolean))if(stats.n>=3)for(const [key,att,yards,td,min] of [['kick-return','KRETATTEMPTS','KRETYARDS','KRETTDS',8],['punt-return','PRETATTEMPTS','PRETYARDS','PRETTDS',6]]){
   const a=stats.read(att),y=stats.read(yards),touchdowns=stats.read(td);if(a>=min&&y!==null&&touchdowns!==null)add(key,{attempts:a,yards:y,touchdowns,rate:one(y/a)});
  }
  // At most two season angles per player; rotate instead of burying the feed in
  // six slightly different stories about the same defender every week.
  events.push(...(bounded?rotation(candidates,s.season.CurrentWeek).slice(0,2):candidates));
 }
 const recent=new Map(s.games.filter(g=>g.year===s.season.CurrentYear&&g.phase===s.season.CurrentWeekType&&[s.season.CurrentWeek-1,s.season.CurrentWeek].includes(g.week)&&final(g)).map(g=>[g.id,g])),players=new Map(s.players.map(p=>[p.id,p]));
 for(const r of s.performances){const p=players.get(r.player),t=teams.get(r.team),g=recent.get(r.game);if(!p||!t||!g||family(r.type)!=='offense')continue;
  const st=r.stats,qb=p.position==='QB'&&st.PASSYARDS>=250&&st.RUSHYARDS>=50,back=['HB','RB','FB'].includes(p.position)&&st.RUSHYARDS>=100&&st.RECEIVEYARDS>=40;
  if(qb||back)events.push({id:`deep:two-way:${p.id}:${g.id}`,category:'player-stats',facts:{family:qb?'deep.dual-qb-game':'deep.dual-back-game',voice:'beat',playerName:p.name,school:t.name,passing:st.PASSYARDS,rushing:st.RUSHYARDS,receiving:st.RECEIVEYARDS,opponent:teams.get(g.home===r.team?g.away:g.home)?.name},options:{team:r.team,player:p.id,eventWeek:g.week,priority:94,thread:'game:'+g.id}});
 }
 if(!bounded)return events;
 const selected=[],counts=new Map(),types=new Map();
 for(const e of rotation(events,s.season.CurrentWeek)){
  if(e.category!=='analytics'){selected.push(e);continue;}
  const key=e.facts.family,kind=/tackles-game|sacks-game|tfl-game|ints-game|pbu-game|forced-game|recoveries-game/.test(key)?'defense':/line-sacks|pancakes/.test(key)?'line':/kicks|touchbacks|punt-|kick-return/.test(key)?'special':'offense',bucket=e.options.team+':'+kind;
  if((counts.get(e.options.team)??0)>=10||(types.get(bucket)??0)>=(kind==='offense'||kind==='defense'?3:2))continue;
  selected.push(e);counts.set(e.options.team,(counts.get(e.options.team)??0)+1);types.set(bucket,(types.get(bucket)??0)+1);
 }
 return selected;
}
