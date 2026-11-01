// Deterministic prewritten templates. Every factual slot comes from this save.
import {publishWeek} from './feed_selection.mjs';
export const ENGINE_VERSION=2;
const complete=g=>['HomeWon','AwayWon','Tie'].includes(g.status);
const ranked=n=>Number.isInteger(n)&&n>=1&&n<=25;
export const weekKey=s=>`${s.leagueId}/${s.season.CurrentSeasonYear}/${s.season.CurrentWeekType}/${s.season.CurrentWeek}`;
export function trackOffers(s,sameWeek=null,previous=null){
  const valid=(x,w)=>x&&x.leagueId===s.leagueId&&x.season.CurrentSeasonYear===s.season.CurrentSeasonYear&&x.season.CurrentWeekType===s.season.CurrentWeekType&&x.season.CurrentWeek===w;
  const same=valid(sameWeek,s.season.CurrentWeek)?sameWeek:null;
  const prior=valid(previous,s.season.CurrentWeek-1)?previous:null;
  const baseline=Array.isArray(same?.offers)?same:Array.isArray(prior?.offers)?prior:null;
  const key=o=>`${o.team}:${o.player}`,current=new Set(s.offers.map(key));
  // A rewind or withdrawn offer cannot leave a fact in this week's feed that
  // is absent from the currently loaded snapshot.
  const events=new Map((same?.offerEvents??[]).filter(o=>current.has(key(o))).map(o=>[key(o),o]));
  if(baseline){const known=new Set(baseline.offers.map(key));for(const o of s.offers)if(!known.has(key(o)))events.set(key(o),o);}
  return [...events.values()];
}
export function buildFeed(s,previous=null){
  if(s.format!==2||s.gameYear!==27||!s.sourceUnchanged||!/^[a-f0-9]{64}$/.test(s.sha256))throw Error('Invalid Dynasty snapshot');
  const year=s.season.CurrentYear,week=s.season.CurrentWeek,phase=s.season.CurrentWeekType;
  if(!Number.isInteger(week)||week<0||week>40)throw Error('Invalid Dynasty week');
  const inSeason=s.season.CurrentStage==='NFLSeason';
  const teams=new Map(s.teams.map(t=>[t.id,t])),players=new Map(s.players.map(p=>[p.id,p]));
  if(!teams.has(s.userTeamIndex))throw Error('Controlled team missing from snapshot');
  const name=id=>teams.get(id)?.name??'Unknown team';
  const rank=id=>ranked(teams.get(id)?.mediaRank)?teams.get(id).mediaRank:99;
  const teamLabel=id=>`${rank(id)<=25?'#'+rank(id)+' ':''}${name(id)}`;
  const own=teams.get(s.userTeamIndex),conferenceTeams=new Set(s.teams.filter(t=>own.conferenceId&&t.conferenceId===own.conferenceId).map(t=>t.id));
  const posts=[],ids=new Set();
  const currentLabel=`${phase==='RegularSeason'?'Week':phase+' week'} ${week}`;
  const add=(id,category,body,{team=null,player=null,priority=50,stamp=currentLabel,relatedTeams=[],national=null,eventWeek=null,thread=null,curated=true,primaryScope=null}={})=>{
    if(ids.has(id)||!body||body.length>380)return;ids.add(id);
    const p=player&&players.get(player),t=teams.get(team??p?.team);
    let author='Campus Football Wire',handle='@CampusFBWire',imageLibrary=79,imageValue=598;
    if(t&&Number.isInteger(t.logo)){imageLibrary=0;imageValue=t.logo;author=`${t.name} Beat`;handle='@CampusBeat';}
    // Real-player portrait IDs and generated-player head IDs use different
    // libraries. Until generated head mapping is verified use the team logo.
    if(p?.isNil&&p.portrait>0){imageLibrary=1;imageValue=p.portrait;}
    if(category==='lines'){author='Saturday Model Lines';handle='@SimulatedLines';imageLibrary=79;imageValue=598;}
    const involved=[...new Set([team,p?.team,...relatedTeams].filter(t=>Number.isInteger(t)&&t!==255))];
    const scopes=[];
    if(involved.includes(s.userTeamIndex))scopes.push('team');
    if(involved.some(t=>conferenceTeams.has(t)))scopes.push('conference');
    if(national??['polls','heisman','cfp','holiday'].includes(category))scopes.push('national');
    if(!scopes.length)return;
    posts.push({id,category,author,handle,body,imageLibrary,imageValue,stamp,priority,scopes,teamIds:involved,eventWeek,thread,curated,primaryScope});
  };
  const eligible=s.games.filter(g=>g.year===year&&g.phase===phase);
  const last=inSeason&&week>0?eligible.filter(g=>g.week===week-1&&complete(g)):[];
  const upcoming=inSeason?eligible.filter(g=>g.week===week&&!complete(g)):[];
  for(const g of last){
    const user=[g.home,g.away].includes(s.userTeamIndex),margin=Math.abs(g.homeScore-g.awayScore);
    const national=rank(g.home)<=25||rank(g.away)<=25;
    if(!user&&!national&&![g.home,g.away].some(t=>conferenceTeams.has(t)))continue;
    const win=g.homeScore>=g.awayScore?g.home:g.away,lose=win===g.home?g.away:g.home;
    const ws=Math.max(g.homeScore,g.awayScore),ls=Math.min(g.homeScore,g.awayScore);
    const body=g.homeScore===g.awayScore?`Final: ${name(g.away)} ${g.awayScore}, ${name(g.home)} ${g.homeScore}. A tie on the Week ${week-1} scoreboard.`:
      `Final: ${name(win)} ${ws}, ${name(lose)} ${ls}. ${margin<=7?'One possession made the difference.':margin>=21?'A statement on the scoreboard.':'That one goes in the win column.'}`;
    add(`result:${g.id}`,'results',body,{team:win,relatedTeams:[g.home,g.away],national,eventWeek:week-1,thread:`result:${g.id}`,priority:user?100:rank(lose)<rank(win)?84:60,stamp:`Last week · Week ${week-1}`});
    if(user)for(const [id,st] of [[g.home,g.homeStats],[g.away,g.awayStats]])if(id===s.userTeamIndex&&st){
      const keys=['OFFPASSYARDS','OFFRUSHYARDS','FIRSTDOWNS','GIVEAWAYS'];
      if(keys.every(k=>Number.isFinite(st[k])))add(`teamstats:${g.id}:${id}`,'team-stats',`${name(id)} last week: ${st.OFFPASSYARDS} passing yards, ${st.OFFRUSHYARDS} rushing yards, ${st.FIRSTDOWNS} first downs and ${st.GIVEAWAYS} giveaways. The box score tells the story.`,{team:id,priority:94,eventWeek:week-1,stamp:`Last week · Week ${week-1}`});
    }
  }
  const gameIds=new Set(last.map(g=>g.id));
  for(const r of s.performances){
    if(!gameIds.has(r.game))continue;const p=players.get(r.player);if(!p)continue;
    const st=r.stats,parts=[];let impact=0;
    if(st.PASSATTEMPTS>0){parts.push(`${st.PASSCOMPLETED}/${st.PASSATTEMPTS} passing, ${st.PASSYARDS} yards, ${st.PASSTDS} TD, ${st.PASSINTS} INT`);impact+=st.PASSYARDS/10+st.PASSTDS*8;}
    if(st.RUSHATTEMPTS>0&&(st.RUSHYARDS>=50||st.RUSHTDS>0)){parts.push(`${st.RUSHYARDS} rushing yards and ${st.RUSHTDS} rushing TD`);impact+=st.RUSHYARDS/5+st.RUSHTDS*8;}
    if(st.RECEIVECATCHES>0&&(st.RECEIVEYARDS>=60||st.RECEIVETDS>0)){parts.push(`${st.RECEIVECATCHES} catches, ${st.RECEIVEYARDS} yards and ${st.RECEIVETDS} receiving TD`);impact+=st.RECEIVEYARDS/5+st.RECEIVETDS*8;}
    const sacks=(st.DLINESACKS??0)+(st.DLINEHALFSACK??0)*0.5;
    if(sacks>0){parts.push(`${sacks} sacks`);impact+=sacks*12;}
    if(st.DSECINTS>0){parts.push(`${st.DSECINTS} interceptions`);impact+=st.DSECINTS*15;}
    if(st.DEFTACKLES>=10){parts.push(`${st.DEFTACKLES} solo tackles`);impact+=st.DEFTACKLES*2;}
    if(parts.length&&impact>=25)add(`performance:${r.game}:${r.player}:${r.type}`,'player-stats',`${p.name} (${name(r.team)}) last week: ${parts.join('; ')}. Put that performance on the weekly reel.`,{player:p.id,team:r.team,national:impact>=75||(rank(r.team)<=25&&impact>=40),eventWeek:week-1,thread:`performances:${r.game}:${r.team}`,priority:(r.team===s.userTeamIndex?91:65)+Math.min(impact,100)/100,stamp:`Last week · Week ${week-1}`});
  }
  if(inSeason)for(const t of s.teams){
    if(!ranked(t.mediaRank))continue;
    const old=t.mediaLastRank,changed=old!==t.mediaRank;
    if(!changed&&t.id!==s.userTeamIndex&&t.mediaRank!==1)continue;
    const movement=!ranked(old)?`enters the Top 25 at #${t.mediaRank}`:old>t.mediaRank?`climbs from #${old} to #${t.mediaRank}`:old<t.mediaRank?`slides from #${old} to #${t.mediaRank}`:`holds steady at #${t.mediaRank}`;
    add(`poll:${t.id}`,'polls',`${t.name} ${movement} in this week's Media Poll. ${ranked(old)&&old>t.mediaRank?'The voters noticed.':ranked(old)&&old<t.mediaRank?'A chance to answer back this week.':'Every spot matters.'}`,{team:t.id,priority:t.id===s.userTeamIndex?98:t.mediaRank<=5?83:55});
  }
  const prior=previous&&previous.leagueId===s.leagueId&&previous.season.CurrentSeasonYear===s.season.CurrentSeasonYear&&previous.season.CurrentWeekType===phase&&previous.season.CurrentWeek===week-1?previous:null;
  const previousPlayers=new Map((prior?.players??[]).map(p=>[p.id,p]));
  for(const p of s.players){
    if(p.team!==s.userTeamIndex||!p.injury||p.injury==='Uninjured')continue;
    const fresh=inSeason&&p.injuryYear===year&&p.injuryWeek===week-1&&p.injuryStage===s.season.CurrentStage;
    add(`injury:${p.id}`,'injuries',`${fresh?'Injury update from last week':'Current injury report'}: ${p.name} (${p.position}, ${name(p.team)}) — ${p.injury.replace(/([a-z])([A-Z])/g,'$1 $2')}${p.injuryType&&p.injuryType!=='None'?`, ${p.injuryType.replace(/([a-z])([A-Z])/g,'$1 $2')}`:''}. ${fresh?'The depth chart may need an answer.':'Keep an eye on availability.'}`,{player:p.id,priority:96,stamp:fresh?`Last week · Week ${week-1}`:currentLabel});
  }
  if(prior)for(const p of s.players){const old=previousPlayers.get(p.id);
    if(p.team===s.userTeamIndex&&p.injury==='Uninjured'&&old?.injury&&old.injury!=='Uninjured')add(`healthy:${p.id}`,'injuries',`${p.name} is listed as uninjured in the latest ${name(p.team)} roster. A welcome update heading into this week.`,{player:p.id,priority:95});
  }
  const oldCommits=new Set((prior?.commitments??[]).map(c=>`${c.team}:${c.player}`));
  for(const c of s.commitments){
    const p=players.get(c.player);if(!p)continue;
    // On first observation, avoid assigning an unverified event week. The
    // game's committed-week numbering is retained for research, not asserted.
    const fresh=(prior&&!oldCommits.has(`${c.team}:${c.player}`))||(inSeason&&c.week>0&&c.week===week-1);
    if(!fresh&&c.team!==s.userTeamIndex)continue;
    add(`commit:${c.team}:${c.player}`,'recruiting',`${fresh?'Commitment update':'Commitment board check'}: ${p.name} (${p.position}${c.rank>0?`, national #${c.rank}`:''}) is ${c.stage==='SoftCommitted'?'verbally ':''}committed to ${name(c.team)}. ${fresh?'The next class is taking shape.':'One of the names in the next class.'}`,{team:c.team,national:fresh&&c.rank>0&&c.rank<=100,curated:fresh,thread:`commitments:${c.team}`,priority:c.team===s.userTeamIndex&&fresh?97:fresh?79+1/(c.rank||9999):64,stamp:fresh?currentLabel:'Current commitment board'});
  }
  for(const offer of s.newOffers??[]){
    const p=players.get(offer.player);if(!p||!teams.has(offer.team))continue;
    const id=`offer:${offer.team}:${p.id}`;
    add(id,'offers',`AGTG! Blessed to receive an offer from ${name(offer.team)}`,{team:offer.team,player:p.id,national:offer.rank>0&&offer.rank<=100,thread:`offers:${offer.team}`,priority:offer.team===s.userTeamIndex?95:72+1/(offer.rank||9999),stamp:`New offer · ${currentLabel}`});
    const post=posts.find(post=>post.id===id);if(post){post.author=p.name;post.handle='@'+p.name.replace(/[^a-zA-Z0-9]/g,'').slice(0,24);}
  }
  for(const h of s.heisman){const p=players.get(h.player);if(!inSeason||!p)continue;
    const change=h.lastRank>0&&h.lastRank!==h.rank?` (last week: #${h.lastRank})`:'';
    add(`heisman:${p.id}`,'heisman',`Heisman watch: ${p.name}, ${name(h.team)}, is #${h.rank} in the game's current race${change}. ${h.rank===1?'The one everyone is chasing.':'Still in the conversation.'}`,{player:p.id,team:h.team,priority:h.rank===1?88:74-h.rank});
  }
  const sortedUpcoming=[...upcoming].sort((a,b)=>Number([b.home,b.away].includes(s.userTeamIndex))-Number([a.home,a.away].includes(s.userTeamIndex))||(rank(a.home)+rank(a.away))-(rank(b.home)+rank(b.away))||b.spotlight-a.spotlight||a.id.localeCompare(b.id));
  for(const g of sortedUpcoming){
    const user=[g.home,g.away].includes(s.userTeamIndex);
    const national=rank(g.home)<=25||rank(g.away)<=25;
    if(!user&&!national&&![g.home,g.away].some(t=>conferenceTeams.has(t)))continue;
    add(`preview:${g.id}`,'schedule',`This week: ${teamLabel(g.away)} at ${teamLabel(g.home)} — ${g.month}/${g.day} on the game calendar. ${rank(g.home)<=25&&rank(g.away)<=25?'Ranked matchup. Circle this one.':'A fresh chance to change the conversation.'}`,{team:user?s.userTeamIndex:g.home,relatedTeams:[g.home,g.away],national,priority:user?93:rank(g.home)<=25&&rank(g.away)<=25?85:78});
    const watch=s.players.filter(p=>[g.home,g.away].includes(p.team)&&p.injury==='Uninjured'&&['QB','HB','RB','WR','TE'].includes(p.position)).sort((a,b)=>b.overall-a.overall||a.id.localeCompare(b.id))[0];
    if(watch&&user)add(`watch:${g.id}:${watch.id}`,'watch',`Player to watch: ${watch.name}, ${watch.position}, ${name(watch.team)}. ${watch.overall} OVR and a matchup with ${name(watch.team===g.home?g.away:g.home)} this week. Watch the touches.`,{player:watch.id,priority:86});
    if(user){
      // Transparent entertainment model, never an actual sportsbook price.
      const strength=id=>{const ps=s.players.filter(p=>p.team===id&&p.injury==='Uninjured').sort((a,b)=>b.overall-a.overall).slice(0,22);return ps.length?ps.reduce((n,p)=>n+p.overall,0)/ps.length:null;};
      const hs=strength(g.home),as=strength(g.away);
      if(hs!==null&&as!==null){const spread=Math.round(((hs-as)*0.6+2.5)*2)/2,abs=Math.abs(spread);
        add(`line:${g.id}`,'lines',`SIMULATED LINE: ${spread===0?'Pick\'em':name(spread>0?g.home:g.away)+' -'+abs} vs ${name(spread>0?g.away:g.home)}. Simple active-roster strength model + home field. Fictional estimate; not a sportsbook line.`,{team:s.userTeamIndex,relatedTeams:[g.home,g.away],priority:70});}
    }
  }
  if(inSeason){
    const flags=[['thanksgiving','Thanksgiving','Thanksgiving week brings football and plenty to be thankful for.'],['christmas','Christmas','Christmas week on the college football calendar. Enjoy the holiday and the games.'],['newYears',"New Year","A new year and more football ahead. Happy New Year, college football fans."]];
    for(const [flag,title,body] of flags)if(upcoming.some(g=>g[flag]))add(`holiday:${flag}`,'holiday',body,{priority:82,stamp:`${title} · ${currentLabel}`});
    // Date-based holidays use only scheduled in-game dates.
    const dates=upcoming.filter(g=>g.month>=1&&g.month<=12&&g.day>=1&&g.day<=31);
    if(dates.some(g=>g.month===10&&g.day===31))add('holiday:halloween','holiday','Halloween on the football calendar. Which defense is bringing the scares this week?',{priority:82});
  }
  if(inSeason&&conferenceTeams.size){
    const members=s.teams.filter(t=>conferenceTeams.has(t.id));
    const independent=own.independent;
    const leaders=members.filter(t=>Number.isFinite(independent?t.wins:t.conferenceRank)).sort((a,b)=>independent?b.wins-a.wins||a.losses-b.losses:a.conferenceRank-b.conferenceRank).slice(0,3);
    if(leaders.length)add(`standings:${own.conferenceId}`,'standings',`${own.conferenceName} ${independent?'check-in':'standings watch'}: ${leaders.map(t=>`${t.name} ${independent?t.wins:t.conferenceWins}-${independent?t.losses:t.conferenceLosses}${!independent&&t.conferenceRank>0?' (conference #'+t.conferenceRank+')':''}`).join('; ')}. ${independent?'Records among the independent programs.':'The conference picture heading into this week.'}`,{relatedTeams:members.map(t=>t.id),priority:84,national:false,primaryScope:'conference'});
  }
  if(inSeason)for(const t of s.teams.filter(t=>ranked(t.cfpRank)).sort((a,b)=>a.cfpRank-b.cfpRank).slice(0,5))add(`cfp:${t.id}`,'cfp',`CFP rankings: ${t.name} is #${t.cfpRank}${ranked(t.cfpLastRank)?` (previously #${t.cfpLastRank})`:''} in the game's current playoff poll. The postseason picture is taking shape.`,{team:t.id,national:true,priority:t.id===s.userTeamIndex?96:87});
  if(!posts.length)add('quiet-week','status',`${name(s.userTeamIndex)} — ${currentLabel}. No verified weekly headlines are available in this saved snapshot. Save after advancing and reopen the feed for the latest news.`,{team:s.userTeamIndex});
  return publishWeek({format:1,engineVersion:ENGINE_VERSION,key:weekKey(s),leagueId:s.leagueId,userTeamIndex:s.userTeamIndex,
    season:s.season.CurrentSeasonYear,week,phase,source:s.source,sha256:s.sha256,sourceUnchanged:true,
    conference:own.conferenceName??null,sourceLabel:`${s.source.split(/[\\/]/).pop()} · ${s.season.CurrentSeasonYear} · ${currentLabel} · Saved data`,stories:posts});
}
