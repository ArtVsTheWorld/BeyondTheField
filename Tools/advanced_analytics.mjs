import {teamAnalytics} from './team_analytics.mjs';
export const TEAM_SCENARIOS=['scoring-offense','scoring-defense','scoring-margin','yards-per-attempt','passing-efficiency','rushing-efficiency','offensive-balance','interception-rate','passing-td-rate','fourth-down','run-defense','pass-defense','takeaways','sack-pressure','red-zone-field-goals','penalty-discipline','second-half','halftime-comebacks','fourth-quarter-losses','home-road-split','close-games','opponent-records','offense-defense-contrast','red-zone-defense'];
export const PLAYER_SCENARIOS=['passing-yards-leader','passing-td-leader','rushing-yards-leader','receiving-yards-leader','sacks-leader','interceptions-leader','completion-rate','passing-yards-per-attempt','td-int-ratio','rushing-yards-per-carry','yards-per-catch','yards-after-catch','receiving-td-rate','scrimmage-yards','dual-threat','carry-share','catch-share','touchdown-share','tackles','tackles-for-loss','forced-fumbles','pass-breakups','field-goals','long-field-goals','net-punting','freshman-production'];
const final=g=>g.published!==false&&['HomeWon','AwayWon','Tie'].includes(g.status);
const finite=Number.isFinite,one=x=>x.toFixed(1),pct=x=>one(x*100),total=(a,f)=>a.reduce((n,x)=>n+(x[f]??0),0);
const teamRows=s=>new Map(teamAnalytics(s).teams.map(x=>[x.teamId,x]));
export function advancedAnalytics(s,{bounded=true}={}){
 if(s.season.CurrentStage!=='NFLSeason'||s.season.CurrentWeekType!=='RegularSeason')return [];
 const teams=new Map(s.teams.filter(t=>t.id!==255).map(t=>[t.id,t])),rows=teamRows(s),events=[],allGames=s.games.filter(g=>g.year===s.season.CurrentYear&&g.phase==='RegularSeason'&&g.week<=s.season.CurrentWeek&&final(g));
 function add(key,team,values,{player=null,negative=false,priority=82,national=false}={}){events.push({key,team:team.id,player:player?.id??null,values:{school:team.name,...(player?{playerName:player.name,position:player.position}:{}),...values},family:'analysis.'+(player?'player.':'team.')+key,negative,priority,national});}
 const verifiedTeams=new Map();
 for(const t of teams.values()){
  const a=rows.get(t.id);if(!a?.metricRecordMatches||a.gamesPlayed<3)continue;
  const games=allGames.filter(g=>g.home===t.id||g.away===t.id);if(games.length!==a.gamesPlayed)continue;
  const raw=t.seasonStats?.stats??{},caches=games.map(g=>g.home===t.id?g.homeStats:g.awayStats);
  const v=f=>finite(raw[f])&&caches.every(c=>finite(c?.[f]))&&total(caches,f)===raw[f]?raw[f]:null;
  verifiedTeams.set(t.id,{games,a,v});const n=games.length;
  const own=g=>g.home===t.id?g.homeScore:g.awayScore,against=g=>g.home===t.id?g.awayScore:g.homeScore;
  const pf=games.reduce((z,g)=>z+own(g),0),pa=games.reduce((z,g)=>z+against(g),0),margin=(pf-pa)/n;
  const emit=(key,values,o={})=>add(key,t,{games:n,...values},o);
  if(pf/n>=35)emit('scoring-offense',{value:one(pf/n)});
  if(pa/n<=18||pa/n>=35)emit('scoring-defense',{value:one(pa/n)},{negative:pa/n>=35});
  if(Math.abs(margin)>=17)emit('scoring-margin',{value:(margin>=0?'+':'')+one(margin)},{negative:margin<0});
  const pass=v('PASSATTEMPTS'),rush=v('RUSHATTEMPTS'),yards=v('OFFYARDS'),passY=v('OFFPASSYARDS'),rushY=v('OFFRUSHYARDS'),ints=v('PASSINTS'),td=v('PASSTDS');
  if(pass!==null&&rush!==null&&yards!==null&&pass+rush>=150&&(yards/(pass+rush)>=6.8||yards/(pass+rush)<=4.7))emit('yards-per-attempt',{value:one(yards/(pass+rush)),attempts:pass+rush},{negative:yards/(pass+rush)<=4.7});
  if(pass>=80&&passY!==null&&(passY/pass>=8.5||passY/pass<=5.8))emit('passing-efficiency',{value:one(passY/pass),attempts:pass},{negative:passY/pass<=5.8});
  if(rush>=80&&rushY!==null&&(rushY/rush>=5.8||rushY/rush<=3.2))emit('rushing-efficiency',{value:one(rushY/rush),attempts:rush},{negative:rushY/rush<=3.2});
  if(pass!==null&&rush!==null&&pass+rush>=150&&Math.max(pass,rush)/(pass+rush)>=.65)emit('offensive-balance',{value:pct(Math.max(pass,rush)/(pass+rush)),approach:pass>rush?'pass attempts':'carries'});
  if(pass>=100&&ints!==null&&(ints===0||ints/pass>=.04))emit('interception-rate',{value:pct(ints/pass),interceptions:ints,attempts:pass},{negative:ints/pass>=.04});
  if(pass>=100&&td!==null&&td/pass>=.08)emit('passing-td-rate',{value:pct(td/pass),touchdowns:td,attempts:pass});
  const fourth=v('FOURTHDOWNS'),conv=v('FOURTHDOWNCONV');if(fourth>=10&&conv!==null&&(conv/fourth>=.7||conv/fourth<=.3))emit('fourth-down',{value:pct(conv/fourth),conversions:conv,attempts:fourth},{negative:conv/fourth<=.3});
  for(const [key,field,low,high] of [['run-defense','DEFRUSHYARDS',100,220],['pass-defense','DEFPASSYARDS',180,300]]){const y=v(field);if(y!==null&&(y/n<=low||y/n>=high))emit(key,{value:one(y/n)},{negative:y/n>=high});}
  const take=v('TAKEAWAYS'),sacks=v('SACKS');if(take!==null&&take/n>=2)emit('takeaways',{value:one(take/n),takeaways:take});if(sacks!==null&&sacks/n>=3.5)emit('sack-pressure',{value:one(sacks/n),sacks});
  const fg=v('OFFREDZONEFGS'),rztd=v('OFFREDZONETDS');if(fg!==null&&rztd!==null&&fg+rztd>=10&&fg/(fg+rztd)>=.4)emit('red-zone-field-goals',{value:pct(fg/(fg+rztd)),fieldGoals:fg,scoringTrips:fg+rztd},{negative:true});
  const penalties=v('PENALTYYARDS');if(penalties>0&&(penalties/n>=70||penalties/n<=25))emit('penalty-discipline',{value:one(penalties/n)},{negative:penalties/n>=70});
  const quarters=games.filter(g=>[g.homeQuarterScores,g.awayQuarterScores].every(q=>Array.isArray(q)&&q.length===4&&q.every(finite))&&g.homeQuarterScores.reduce((a,b)=>a+b,0)+(g.homeOvertimePoints??0)===g.homeScore&&g.awayQuarterScores.reduce((a,b)=>a+b,0)+(g.awayOvertimePoints??0)===g.awayScore);
  if(quarters.length===n){const diff=(g,end)=>{const h=g.homeQuarterScores.slice(0,end).reduce((a,b)=>a+b,0)-g.awayQuarterScores.slice(0,end).reduce((a,b)=>a+b,0);return g.home===t.id?h:-h;};
   const second=quarters.reduce((z,g)=>z+(own(g)-against(g)-(g.home===t.id?(g.homeOvertimePoints??0)-(g.awayOvertimePoints??0):(g.awayOvertimePoints??0)-(g.homeOvertimePoints??0)))-diff(g,2),0)/n;
   if(finite(second)&&Math.abs(second)>=10)emit('second-half',{value:(second>=0?'+':'')+one(second)},{negative:second<0});
   const comeback=quarters.filter(g=>diff(g,2)<0&&own(g)>against(g)).length,collapse=quarters.filter(g=>diff(g,3)>0&&own(g)<against(g)).length;
   if(comeback>=2)emit('halftime-comebacks',{count:comeback});if(collapse>=2)emit('fourth-quarter-losses',{count:collapse},{negative:true});
  }
  const home=games.filter(g=>g.neutral===false&&g.home===t.id),away=games.filter(g=>g.neutral===false&&g.away===t.id);if(home.length>=2&&away.length>=2){const h=home.reduce((z,g)=>z+own(g)-against(g),0)/home.length,a=away.reduce((z,g)=>z+own(g)-against(g),0)/away.length;if(Math.abs(h-a)>=14)emit('home-road-split',{homeMargin:one(h),roadMargin:one(a),homeGames:home.length,roadGames:away.length},{negative:a<0});}
  const close=games.filter(g=>Math.abs(own(g)-against(g))<=7);if(close.length>=3)emit('close-games',{count:close.length,wins:close.filter(g=>own(g)>against(g)).length,losses:close.filter(g=>own(g)<against(g)).length});
  if(pf/n>=35&&pa/n>=30)emit('offense-defense-contrast',{pointsFor:one(pf/n),pointsAgainst:one(pa/n)},{negative:true});
  const trips=v('DEFREDZONES'),allowed=v('DEFREDZONETDS');if(trips>=10&&allowed!==null&&(allowed/trips<=.4||allowed/trips>=.8))emit('red-zone-defense',{value:pct(allowed/trips),trips,touchdowns:allowed},{negative:allowed/trips>=.8});
  // Opponent results exclude this matchup and require published, corroborated records.
  const opponents=[...new Set(games.map(g=>g.home===t.id?g.away:g.home))];if(opponents.every(id=>rows.get(id)?.resultCorroborated)){let w=0,l=0;for(const id of opponents){const r=rows.get(id),meetings=games.filter(g=>g.home===id||g.away===id);w+=r.resultWins-meetings.filter(g=>own(g)<against(g)).length;l+=r.resultLosses-meetings.filter(g=>own(g)>against(g)).length;}if(w+l>=6&&w/(w+l)>=.65)emit('opponent-records',{wins:w,losses:l});}
 }
 const gamesByPlayer=new Map();for(const perf of s.performances){if(!allGames.some(g=>g.id===perf.game))continue;const a=gamesByPlayer.get(perf.player)??[];a.push(perf);gamesByPlayer.set(perf.player,a);}
 const players=[];
 for(const p of s.players){const t=teams.get(p.team),team=verifiedTeams.get(p.team);if(!t||!team)continue;const records=p.seasonStats??[],gameRecords=gamesByPlayer.get(p.id)??[];
  const read=(type,field)=>{const st=records.find(x=>x.type==='Season'+type)?.stats;if(!st||st.GAMESPLAYED<1||st.GAMESPLAYED>team.games.length||!finite(st[field]))return null;const g=gameRecords.filter(x=>x.type==='Game'+type&&x.team===p.team);return g.length&&g.every(x=>finite(x.stats[field]))&&total(g.map(x=>x.stats),field)===st[field]?st[field]:null;};
  const o=f=>read('OffensiveStats',f),d=f=>read('DefensiveStats',f),k=f=>read('KickingStats',f);
  const def=records.find(x=>x.type==='SeasonDefensiveStats')?.stats,gd=gameRecords.filter(x=>x.type==='GameDefensiveStats'&&x.team===p.team);const sacks=def&&gd.length&&(def.DLINESACKS+.5*def.DLINEHALFSACK)===gd.reduce((z,x)=>z+x.stats.DLINESACKS+.5*x.stats.DLINEHALFSACK,0)?def.DLINESACKS+.5*def.DLINEHALFSACK:null;
  const n=Math.max(...records.map(x=>x.stats.GAMESPLAYED??0),0);players.push({p,t,team,n,o,d,k,sacks});
 }
 const leaderSpecs=[['passing-yards-leader',x=>x.o('PASSYARDS'),x=>x.o('PASSATTEMPTS')>=60,'passing yards'],['passing-td-leader',x=>x.o('PASSTDS'),x=>x.o('PASSATTEMPTS')>=60,'passing TD'],['rushing-yards-leader',x=>x.o('RUSHYARDS'),x=>x.o('RUSHATTEMPTS')>=40,'rushing yards'],['receiving-yards-leader',x=>x.o('RECEIVEYARDS'),x=>x.o('RECEIVECATCHES')>=15,'receiving yards'],['sacks-leader',x=>x.sacks,x=>x.sacks>=3,'sacks'],['interceptions-leader',x=>x.d('DSECINTS'),x=>x.d('DSECINTS')>=2,'interceptions']];
 const participantTeams=new Set(allGames.flatMap(g=>[g.home,g.away]).filter(id=>id!==255)),fullField=[...participantTeams].every(id=>verifiedTeams.has(id));
 for(const [key,value,eligible,label] of leaderSpecs){
  const field={'passing-yards-leader':'PASSYARDS','passing-td-leader':'PASSTDS','rushing-yards-leader':'RUSHYARDS','receiving-yards-leader':'RECEIVEYARDS','sacks-leader':'DLINESACKS','interceptions-leader':'DSECINTS'}[key],defensive=['sacks-leader','interceptions-leader'].includes(key),indexed=new Map(players.map(x=>[x.p.id,x])),unknown=new Set();
  for(const perf of s.performances)if(perf.type===(defensive?'GameDefensiveStats':'GameOffensiveStats')&&allGames.some(g=>g.id===perf.game)&&(perf.stats[field]>0||key==='sacks-leader'&&perf.stats.DLINEHALFSACK>0)){const x=indexed.get(perf.player);if(!x||value(x)===null)unknown.add(perf.team);}
  for(const p of s.players){const raw=p.seasonStats?.find(r=>r.type===(defensive?'SeasonDefensiveStats':'SeasonOffensiveStats'))?.stats;if(raw&&(raw[field]>0||key==='sacks-leader'&&raw.DLINEHALFSACK>0)){const x=indexed.get(p.id);if(!x||value(x)===null)unknown.add(p.team);}}

  const candidate=players.filter(x=>value(x)!==null&&value(x)>0);
  for(const x of candidate){const pools=[...(fullField&&!unknown.size?[{label:'FBS',rows:candidate,national:true}]:[]),...(x.t.conferenceId&&[...participantTeams].filter(id=>teams.get(id)?.conferenceId===x.t.conferenceId).every(id=>verifiedTeams.has(id)&&!unknown.has(id))?[{label:x.t.conferenceName,rows:candidate.filter(y=>y.t.conferenceId===x.t.conferenceId),national:false}]:[])];
   for(const pool of pools){if(pool.rows.some(y=>value(y)>value(x)))continue;const tied=pool.rows.filter(y=>value(y)===value(x)).length>1;add(key,x.t,{value:one(value(x)).replace(/\.0$/,''),metricLabel:label,field:pool.label,lead:tied?'shares the lead in':'leads',games:x.n},{player:x.p,national:pool.national,priority:pool.national?96:88});break;}
  }
 }
 for(const x of players){const {p,t,n,o,d,k,team}=x;if(n<3)continue;const emit=(key,values,negative=false)=>add(key,t,{games:n,...values},{player:p,negative});
  const att=o('PASSATTEMPTS'),comp=o('PASSCOMPLETED'),py=o('PASSYARDS'),ptd=o('PASSTDS'),pi=o('PASSINTS'),carries=o('RUSHATTEMPTS'),ry=o('RUSHYARDS'),rec=o('RECEIVECATCHES'),recy=o('RECEIVEYARDS'),rectd=o('RECEIVETDS'),rushtd=o('RUSHTDS'),yac=o('RECEIVEYARDSAFTER');
  if(att>=80&&comp!==null&&(comp/att>=.7||comp/att<=.52))emit('completion-rate',{value:pct(comp/att),attempts:att},comp/att<=.52);
  if(att>=80&&py!==null&&(py/att>=9||py/att<=5.5))emit('passing-yards-per-attempt',{value:one(py/att),attempts:att},py/att<=5.5);
  if(att>=80&&ptd!==null&&pi!==null&&(ptd>=10&&pi<=Math.floor(ptd/4)||pi>=8&&pi>=ptd))emit('td-int-ratio',{touchdowns:ptd,interceptions:pi},pi>=ptd);
  if(carries>=60&&ry!==null&&(ry/carries>=6.5||ry/carries<=3.5))emit('rushing-yards-per-carry',{value:one(ry/carries),carries,yards:ry},ry/carries<=3.5);
  if(rec>=20&&recy!==null&&recy/rec>=18)emit('yards-per-catch',{value:one(recy/rec),catches:rec});
  if(rec>=20&&yac!==null&&yac/rec>=7)emit('yards-after-catch',{value:one(yac/rec),catches:rec});
  if(rec>=20&&rectd!==null&&rectd/rec>=.15)emit('receiving-td-rate',{value:pct(rectd/rec),catches:rec,touchdowns:rectd});
  if(ry!==null&&recy!==null&&(ry+recy)/n>=125)emit('scrimmage-yards',{value:one((ry+recy)/n),yards:ry+recy});
  if(p.position==='QB'&&py!==null&&ry!==null&&py/n>=180&&ry/n>=40)emit('dual-threat',{passing:one(py/n),rushing:one(ry/n)});
  const teamCarries=team.v('RUSHATTEMPTS'),teamCatches=team.v('PASSCOMPLETIONS'),teamPTD=team.v('PASSTDS'),teamRTD=team.v('RUSHTDS');
  if(carries>=60&&teamCarries>0&&carries<=teamCarries&&carries/teamCarries>=.5)emit('carry-share',{value:pct(carries/teamCarries),carries});
  if(rec>=20&&teamCatches>0&&rec<=teamCatches&&rec/teamCatches>=.35)emit('catch-share',{value:pct(rec/teamCatches),catches:rec});
  if(rectd!==null&&rushtd!==null&&teamPTD!==null&&teamRTD!==null&&rectd+rushtd>=6&&rectd+rushtd<=teamPTD+teamRTD&&(rectd+rushtd)/(teamPTD+teamRTD)>=.4)emit('touchdown-share',{value:pct((rectd+rushtd)/(teamPTD+teamRTD)),touchdowns:rectd+rushtd});
  const solo=d('DEFTACKLES'),assist=d('ASSDEFTACKLES'),tfl=d('DEFTACKLESFORLOSS'),ff=d('DLINEFORCEDFUMBLES'),pbu=d('DEFPASSDEFLECTIONS');
  if(solo!==null&&assist!==null&&(solo+assist)/n>=8)emit('tackles',{value:one((solo+assist)/n),tackles:solo+assist});
  if(tfl>=10)emit('tackles-for-loss',{value:tfl});if(ff>=3)emit('forced-fumbles',{value:ff});if(pbu>=8)emit('pass-breakups',{value:pbu});
  const fga=k('KICKFGATTEMPTS'),fgm=k('KICKFGMADE'),longa=k('KICKFGATTEMPTS50ORMORE'),longm=k('KICKFGMADE50ORMORE'),punts=k('PUNTATTEMPTS'),net=k('PUNTNETYARDS');
  if(fga>=10&&fgm!==null&&fgm/fga>=.9)emit('field-goals',{value:pct(fgm/fga),made:fgm,attempts:fga});if(longa>=4&&longm>=3&&longm/longa>=.75)emit('long-field-goals',{made:longm,attempts:longa});
  if(punts>=15&&net!==null&&net/punts>=42)emit('net-punting',{value:one(net/punts),punts});
  if(p.classYear==='Freshman'&&(ry!==null&&recy!==null&&ry+recy>=500||solo!==null&&assist!==null&&solo+assist>=30))emit('freshman-production',{production:ry!==null&&recy!==null&&ry+recy>=500?`${ry+recy} yards from scrimmage`:`${solo+assist} tackles`});
 }
 if(!bounded)return events;
 // Same eligibility/caps for CPU and user programs; rotate equally ranked scenarios by week.
 const selected=[],counts=new Map(),used=new Set();events.sort((a,b)=>b.priority-a.priority||((TEAM_SCENARIOS.indexOf(a.key)+PLAYER_SCENARIOS.indexOf(a.key)+s.season.CurrentWeek)%31)-((TEAM_SCENARIOS.indexOf(b.key)+PLAYER_SCENARIOS.indexOf(b.key)+s.season.CurrentWeek)%31)||a.key.localeCompare(b.key)||String(a.player).localeCompare(String(b.player)));
 for(const e of events){const bucket=e.team+':'+(e.player?'player':'team'),identity=bucket+':'+e.key;if(used.has(identity)||(counts.get(bucket)??0)>=(e.player?4:3))continue;selected.push(e);used.add(identity);counts.set(bucket,(counts.get(bucket)??0)+1);}
 return selected;
}
