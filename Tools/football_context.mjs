import {phaseIndex} from './publication_timeline.mjs';
export const NIL_DOLLARS_PER_POINT=2500; // User verified against the in-game display.
export const finalGame=g=>g.published!==false&&Number.isFinite(g.homeScore)&&Number.isFinite(g.awayScore)&&(g.status==='HomeWon'&&g.homeScore>g.awayScore||g.status==='AwayWon'&&g.awayScore>g.homeScore||g.status==='Tie'&&g.homeScore===g.awayScore);
export const visibleGame=(s,g)=>g.year===s.season.CurrentYear&&phaseIndex(g.phase)>=0&&(phaseIndex(g.phase)<phaseIndex(s.season.CurrentWeekType)||g.phase===s.season.CurrentWeekType&&g.week<=s.season.CurrentWeek)&&finalGame(g);
export const schemes={OFF_WEST_COAST_ZONE_RUN:'West Coast zone run',OFF_MULTIPLE_OFFENSE:'multiple offense',OFF_VEER_AND_SHOOT:'veer and shoot',OFF_POWER_SPREAD:'power spread',OFF_SPREAD_OPTION:'spread option',OFF_PRO_STYLE:'pro style',OFF_SPREAD:'spread',OFF_RUN_AND_SHOOT:'run and shoot',OFF_AIR_RAID:'air raid',OFF_PISTOL:'pistol',OFF_OPTION:'option',DEF_BASE4_3:'base 4-3',DEF_3_3_5:'3-3-5',DEF_BASE3_4:'base 3-4',DEF_4_2_5:'4-2-5',DEF_MULTIPLE_DEFENSE:'multiple defense',DEF_4_3_MULTIPLE:'4-3 multiple',DEF_3_4_MULTIPLE:'3-4 multiple',DEF_3_3_5_TITE:'3-3-5 tite',DEF_3_2_6:'3-2-6'};
export const money=n=>'$'+(n>=1e6?(n/1e6).toFixed(2).replace(/0+$/,'').replace(/\.$/,'')+'M':n>=1e3?(n/1e3).toFixed(1).replace(/\.0$/,'')+'K':Math.round(n));
export function positionGroup(position){return ({QB:'quarterbacks',HB:'running backs',RB:'running backs',FB:'running backs',WR:'receivers/tight ends',TE:'receivers/tight ends',LT:'offensive line',LG:'offensive line',C:'offensive line',RG:'offensive line',RT:'offensive line',LE:'defensive line',RE:'defensive line',DT:'defensive line',LEDG:'defensive line',REDG:'defensive line',LOLB:'linebackers',ROLB:'linebackers',MLB:'linebackers',SAM:'linebackers',MIKE:'linebackers',WILL:'linebackers',CB:'defensive backs',FS:'defensive backs',SS:'defensive backs',K:'specialists',P:'specialists',LS:'specialists'})[position]??'other positions';}
export function nilAllocation(s,team){
 const roster=s.players.filter(p=>p.team===team);if(!roster.length||roster.some(p=>!Number.isFinite(p.nil)||p.nil<0))return null;
 const groups=new Map();let total=0;for(const p of roster){const dollars=p.nil*NIL_DOLLARS_PER_POINT;total+=dollars;const group=positionGroup(p.position);groups.set(group,(groups.get(group)??0)+dollars);}
 return {total,players:roster.length,groups:[...groups].map(([group,dollars])=>({group,dollars,share:total?dollars/total:null})).sort((a,b)=>b.dollars-a.dollars||a.group.localeCompare(b.group))};
}
export function verifiedTeamRows(s){
 const map=new Map(),all=s.games.filter(g=>visibleGame(s,g));
 for(const t of s.teams.filter(t=>t.id!==255)){
  const games=all.filter(g=>g.home===t.id||g.away===t.id),n=games.length,own=g=>g.home===t.id?g.homeScore:g.awayScore,other=g=>g.home===t.id?g.awayScore:g.homeScore;
  // Home/road counters omit neutral-site championship and bowl decisions.
  // Current TeamStats includes them; require its full W/L/T when available.
  const current=t.seasonStats?.season===s.season.CurrentSeasonYear?t.seasonStats.stats:null;
  const record=current&&Number.isInteger(current.WINS)&&Number.isInteger(current.LOSSES)?{wins:current.WINS,losses:current.LOSSES,ties:current.TIES??0}:t;
  if(n<1||new Set(games.map(g=>g.id)).size!==n||n!==record.wins+record.losses+(record.ties??0)||games.filter(g=>own(g)>other(g)).length!==record.wins||games.filter(g=>own(g)<other(g)).length!==record.losses)continue;
  const cache=games.map(g=>({own:g.home===t.id?g.homeStats:g.awayStats,other:g.home===t.id?g.awayStats:g.homeStats})),memo=new Map();
  const read=(field,opponent=false)=>{const key=opponent+':'+field;if(!memo.has(key)){const values=cache.map(c=>(opponent?c.other:c.own)?.[field]);let value=values.every(Number.isFinite)?values.reduce((a,b)=>a+b,0):null;
   const raw=t.seasonStats?.season===s.season.CurrentSeasonYear?t.seasonStats.stats:null;if(!opponent&&value!==null&&Number.isFinite(raw?.[field])&&raw[field]!==value)value=null;memo.set(key,value);}return memo.get(key);};
  const ratio=(a,b)=>a!==null&&b>0?a/b:null;
  const pass=read('PASSATTEMPTS'),rush=read('RUSHATTEMPTS'),py=read('OFFPASSYARDS'),ry=read('OFFRUSHYARDS'),dp=read('DEFPASSYARDS'),dr=read('DEFRUSHYARDS'),op=read('PASSATTEMPTS',true),orr=read('RUSHATTEMPTS',true),plays=pass!==null&&rush!==null?pass+rush:null;
  const pf=games.reduce((x,g)=>x+own(g),0),pa=games.reduce((x,g)=>x+other(g),0);
  map.set(t.id,{team:t,games,n,read,pointsFor:pf,pointsAgainst:pa,plays,ppg:pf/n,ppga:pa/n,passYPG:py!==null?py/n:null,rushYPG:ry!==null?ry/n:null,ypg:py!==null&&ry!==null?(py+ry)/n:null,ypp:ratio(py!==null&&ry!==null?py+ry:null,plays),passYPA:ratio(py,pass),rushYPC:ratio(ry,rush),passShare:ratio(pass,plays),passTDpg:read('PASSTDS')!==null?read('PASSTDS')/n:null,rushTDpg:read('RUSHTDS')!==null?read('RUSHTDS')/n:null,passYPGAllowed:dp!==null?dp/n:null,rushYPGAllowed:dr!==null?dr/n:null,ypga:dp!==null&&dr!==null?(dp+dr)/n:null,yppa:ratio(dp!==null&&dr!==null?dp+dr:null,op!==null&&orr!==null?op+orr:null)});
 }
 return map;
}
export function relativeVerdict(value,field,{higher=true,minimum=8,poor=null,strong=null}={}){
 const sample=field.filter(Number.isFinite);if(!Number.isFinite(value)||sample.length<minimum)return {verdict:'neutral',band:'unclassified',population:sample.length};
 const cdf=(sample.filter(x=>x<value).length+.5*sample.filter(x=>x===value).length)/sample.length,quality=higher?cdf:1-cdf;
 let verdict=quality>=.75?'positive':quality<=.25?'negative':'neutral';
 if(poor!==null&&(higher?value<=poor:value>=poor))verdict='negative';
 if(strong!==null&&verdict==='positive'&&!(higher?value>=strong:value<=strong))verdict='neutral';
 return {verdict,band:quality>=.75?'upper quarter':quality<=.25?'lower quarter':'middle half',population:sample.length};
}
