import {hash} from './story_authors.mjs';
import {phaseIndex} from './publication_timeline.mjs';
import {nationalCoverage} from './national_editorial.mjs';
import {verifiedPlayerStats} from './deep_analytics.mjs';
const final=g=>g.published!==false&&Number.isFinite(g.homeScore)&&Number.isFinite(g.awayScore)&&(g.status==='HomeWon'&&g.homeScore>g.awayScore||g.status==='AwayWon'&&g.awayScore>g.homeScore||g.status==='Tie'&&g.homeScore===g.awayScore);
const before=(a,b)=>phaseIndex(a.phase)<phaseIndex(b.phase)||a.phase===b.phase&&a.week<b.week;
const finite=Number.isFinite,one=n=>n.toFixed(1);
export function matchupEvents(s,{force=false}={}){
 if(s.reconstructed||s.season.CurrentStage!=='NFLSeason')return [];
 const teams=new Map(s.teams.filter(t=>t.id!==255).map(t=>[t.id,t])),covered=nationalCoverage(s),events=[];
 const played=s.games.filter(g=>g.year===s.season.CurrentYear&&phaseIndex(g.phase)>=0&&final(g)),byPlayer=new Map();
 for(const r of s.performances){const list=byPlayer.get(r.player)??[];list.push(r);byPlayer.set(r.player,list);}
 const current=s.games.filter(g=>g.year===s.season.CurrentYear&&g.phase===s.season.CurrentWeekType&&teams.has(g.home)&&teams.has(g.away)&&(g.status==='Unplayed'&&g.week===s.season.CurrentWeek||final(g)&&[s.season.CurrentWeek-1,s.season.CurrentWeek].includes(g.week)));
 for(const g of current){
  if(!force&&hash(s.leagueId+'|'+g.id+'|matchup-v1')%100>=40)continue;
  const recap=final(g),sides=[teams.get(g.home),teams.get(g.away)];
  // Use games strictly before this fixture for the entering baseline. The game
  // being recapped must never inflate its own pregame average.
  const baseline=t=>{
   const all=played.filter(x=>x.home===t.id||x.away===t.id),prior=all.filter(x=>before(x,g));
   if(prior.length<3||all.length!==t.wins+t.losses+(t.ties??0)||all.filter(x=>(x.home===t.id?x.homeScore:x.awayScore)>(x.home===t.id?x.awayScore:x.homeScore)).length!==t.wins)return null;
   const caches=prior.map(x=>({own:x.home===t.id?x.homeStats:x.awayStats,other:x.home===t.id?x.awayStats:x.homeStats}));
   const read=(field,opponent=false)=>caches.every(c=>finite((opponent?c.other:c.own)?.[field]))?caches.reduce((n,c)=>n+(opponent?c.other:c.own)[field],0):null;
   return {n:prior.length,read,prior};
  };
  const a=baseline(sides[0]),b=baseline(sides[1]);if(!a||!b)continue;
  const first=hash(g.id+'|matchup-side')%2,off=sides[first],def=sides[1-first],o=first===0?a:b,d=first===0?b:a;
  const angle=hash(g.id+'|matchup-angle')%3,field=angle===0?'OFFPASSYARDS':angle===1?'OFFRUSHYARDS':'SACKSALLOWED',allowed=angle===0?'DEFPASSYARDS':angle===1?'DEFRUSHYARDS':'SACKS';
  const own=o.read(field),other=d.read(allowed);if(own===null||other===null)continue;
  const values={school:off.name,opponent:def.name,games:o.n,opponentGames:d.n,attack:one(own/o.n),defense:one(other/d.n)};
  const attemptField=angle===0?'PASSATTEMPTS':'RUSHATTEMPTS',attempts=angle<2?o.read(attemptField):null,defAttempts=angle<2?d.read(attemptField,true):null;
  const rates=attempts>=80&&defAttempts>=80;if(rates)Object.assign(values,{attackRate:one(own/attempts),defenseRate:one(other/defAttempts)});
  const options={team:off.id,relatedTeams:[def.id],national:covered.has(off.id)||covered.has(def.id),eventWeek:g.week,priority:recap?91:90,thread:'game:'+g.id};
  const emit=(key,family,facts,extra={})=>events.push({id:`matchup:${g.id}:${key}`,category:recap?'matchup-recap':'matchup-preview',facts:{family:'matchup.'+family,voice:'analyst',...values,...facts},options:{...options,...extra}});
  const base=angle===0?'passing':angle===1?'rushing':'protection';
  if(recap){const actual=off.id===g.home?g.homeStats:g.awayStats;if(finite(actual?.[field])){const actualRate=rates&&actual[attemptField]>0?one(actual[field]/actual[attemptField]):null;emit('team',base+'-recap'+(actualRate!==null?'-rates':''),{actual:actual[field],actualRate});}}
  else emit('team',base+'-preview'+(rates?'-rates':''),{});
  const checked=new Map(),index={players:byPlayer,games:new Map(played.map(g=>[g.id,g]))};
  const rowsFor=(p,pattern,ids)=>{const kind=pattern.source.includes('Offensive')?'offense':'defense',key=p.id+':'+kind;if(!checked.has(key))checked.set(key,verifiedPlayerStats(s,p,kind,index));const full=checked.get(key);if(!full)return null;const rows=full.rows.filter(r=>pattern.test(r.type)&&ids.has(r.game));return rows.length?{rows,full}:null;};
  const offGames=new Set(o.prior.map(x=>x.id)),defGames=new Set(d.prior.map(x=>x.id));
  const total=(sample,key)=>sample&&sample.full.read(key)!==null&&sample.rows.every(r=>finite(r.stats[key]))?sample.rows.reduce((n,r)=>n+r.stats[key],0):null;
  const receivers=s.players.filter(p=>p.team===off.id&&['WR','TE'].includes(p.position)).map(p=>{const rows=rowsFor(p,/^GameOffensive(?:KPReturn)?Stats$/,offGames);return {p,catches:total(rows,'RECEIVECATCHES'),yards:total(rows,'RECEIVEYARDS')};}).filter(x=>x.catches>=15&&x.yards>=200).sort((a,b)=>b.yards-a.yards||a.p.id.localeCompare(b.p.id));
  const dbs=s.players.filter(p=>p.team===def.id&&['CB','FS','SS'].includes(p.position)).map(p=>{const rows=rowsFor(p,/^GameDefensive(?:KPReturn)?Stats$/,defGames);return {p,pbu:total(rows,'DEFPASSDEFLECTIONS'),ints:total(rows,'DSECINTS')};}).filter(x=>x.pbu>=3&&x.ints!==null).sort((a,b)=>b.pbu-a.pbu||b.ints-a.ints||a.p.id.localeCompare(b.p.id));
  const wr=receivers[0],db=dbs[0];if(!wr||!db)continue;
  const named={receiver:wr.p.name,defender:db.p.name,catches:wr.catches,yards:wr.yards,breakups:db.pbu,interceptions:db.ints};
  if(!recap)emit('players','receiver-secondary-preview',named,{player:wr.p.id});
  else {const wrRows=rowsFor(wr.p,/^GameOffensive(?:KPReturn)?Stats$/,new Set([g.id])),dbRows=rowsFor(db.p,/^GameDefensive(?:KPReturn)?Stats$/,new Set([g.id])),yards=total(wrRows,'RECEIVEYARDS'),catches=total(wrRows,'RECEIVECATCHES'),pbu=total(dbRows,'DEFPASSDEFLECTIONS'),ints=total(dbRows,'DSECINTS');if([yards,catches,pbu,ints].every(finite))emit('players','receiver-secondary-recap',{...named,actualYards:yards,actualCatches:catches,actualBreakups:pbu,actualInts:ints},{player:wr.p.id});}
 }
 return events;
}
