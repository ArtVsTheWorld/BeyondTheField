import {verifiedPlayerStats} from './deep_analytics.mjs';
import {completeOffensiveLine} from './heisman_context.mjs';
import {postseasonTiming} from './postseason_timing.mjs';
import {conferencePrestige} from './conference_context.mjs';
import {seasonEndings} from './season_ending_events.mjs';
import {verifiedSeasonRecord} from './season_context.mjs';
import {verifiedTeamRows,finalGame} from './football_context.mjs';
import {rosterStrengths,projectLine} from './betting_model.mjs';
import {hash} from './story_authors.mjs';
export function focusFixtures(s){
 if(s.reconstructed||s.season.CurrentStage!=='NFLSeason')return [];
 const cc=postseasonTiming(s).championshipWeek,conferences=new Map((s.conferences??[]).map(c=>[c.id,c])),teams=new Map(s.teams.filter(t=>t.id!==255).map(t=>[t.id,t])),grades=new Map(conferencePrestige(s).map(c=>[c.id,c.grade]));
 return s.games.filter(g=>g.year===s.season.CurrentYear&&g.phase===s.season.CurrentWeekType&&g.week===s.season.CurrentWeek&&teams.has(g.home)&&teams.has(g.away)&&g.home!==g.away).flatMap(g=>{
  if(g.phase==='NationalChampionship')return [{game:g,kind:'title',label:'national championship',tier:3}];
  if(g.isPlayoff===true)return [{game:g,kind:'playoff',label:g.phase==='BowlSeason3'?'playoff semifinal':g.phase==='BowlSeason2'?'playoff quarterfinal':'playoff first round',tier:2}];
  const home=teams.get(g.home),away=teams.get(g.away),c=home.conferenceId&&home.conferenceId===away.conferenceId?conferences.get(home.conferenceId):null;
  if(g.phase==='RegularSeason'&&g.week===cc&&c?.championshipType&&!['NONE','None','Invalid_'].includes(c.championshipType))return [{game:g,kind:'conference',label:c.name+' championship',conference:c,grade:grades.get(c.id)??null,tier:1}];return [];
 });
}
const playerStyle=p=>p.position==='QB'&&['Leader','Intense',null,undefined].includes(p.personality)?'QB':p.personality??'Neutral';
export function postseasonBuzz(s){
 const fixtures=focusFixtures(s);if(!fixtures.length)return [];
 const teams=new Map(s.teams.filter(t=>t.id!==255).map(t=>[t.id,t])),stats=verifiedTeamRows(s),strengths=rosterStrengths(s),grades=new Map(conferencePrestige(s).map(c=>[c.id,c.grade])),ended=seasonEndings(s),events=[];
 const outside=[...ended.values()].map(x=>x.team).sort((a,b)=>Number(b.id===s.userTeamIndex)-Number(a.id===s.userTeamIndex)||hash(a.id+'|watching|'+s.season.CurrentWeek)-hash(b.id+'|watching|'+s.season.CurrentWeek));
 for(const f of fixtures){const g=f.game,home=teams.get(g.home),away=teams.get(g.away),grade=grades.get(f.conference?.id),major=f.kind!=='conference'||grade>=10,depth=f.kind==='title'?3:f.kind==='playoff'?2:grade>=10?2:grade>=7?1:0;
  const record=t=>verifiedSeasonRecord(s,t)?.record??null,base={gameId:g.id,home:home.name,away:away.name,homeRecord:record(home),awayRecord:record(away),eventLabel:f.label,eventFocus:f.kind,focusTier:f.tier,focusTeams:[home.id,away.id],importance:'major',majorGame:true,verdict:'neutral',venue:g.bowlName??f.label};
  function add(key,family,voice,team=home.id,values={},options={}){events.push({id:'buzz:'+g.id+':'+key,category:finalGame(g)?f.kind==='conference'?'championship':'cfp':f.kind==='conference'?'championship':'matchup-preview',facts:{...base,family:'buzz.'+family,voice,school:teams.get(team)?.name,...values},options:{team,relatedTeams:[home.id,away.id],national:major,priority:depth>=2?142:depth===1?111:96,thread:'game:'+g.id,eventWeek:g.week,...options}});}
  if(finalGame(g)){
   const win=g.homeScore>g.awayScore?home:away,lose=win===home?away:home,score=Math.max(g.homeScore,g.awayScore)+'\u2013'+Math.min(g.homeScore,g.awayScore),values={winner:win.name,loser:lose.name,score};
   add('final','final',f.kind==='conference'?'analyst':'cfp',win.id,{...values,analystPersona:0},{priority:155});
   for(const t of [win,lose]){
    const won=t.id===win.id,roster=s.players.filter(p=>p.team===t.id).sort((a,b)=>a.id.localeCompare(b.id)),p=roster[hash(g.id+'|reaction|'+t.id)%Math.max(1,roster.length)];
    add('official:'+t.id,won?'team-champion':'team-final-loss','official',t.id,values,{priority:150});
    add('fan:'+t.id,won?'fan-champion':'fan-final-loss','fan',t.id,{...values,persona:1},{priority:146});
    if(p)add('player:'+t.id,won?'player-champion':'player-final-loss','player',t.id,values,{player:p.id,priority:148});
   }
   for(const persona of [0,1,2,3,4,5].slice(0,depth>=2?6:2))add('analysis:'+persona,'final-analysis-'+persona,'analyst',win.id,{...values,analystPersona:persona},{priority:147});
   if(depth>=2)for(const t of outside.filter(t=>!t.rivals?.includes(win.id)&&!win.rivals?.includes(t.id)).slice(0,4))add('outside-final:'+t.id,'outside-final','fan',t.id,{...values,persona:hash(t.id+'|fan-tone')%2},{national:major,priority:143});
   continue;
  }
  const line=projectLine(s,g,strengths),fav=line?.favorite==null?null:teams.get(line.favorite),underdog=fav?(fav.id===home.id?away:home):null,shape=line?line.spread>=14?'lopsided':line.spread<=4?'close':'favored':'unknown';
  const lineContext=line?(fav?`Our matchup model favors ${fav.name} by ${line.spread} points.`:'Our matchup model has this one even.'):'There is no verified model line for this matchup.';
  add('stage',f.kind==='title'?'title-stage':'stage',f.kind==='conference'?'beat':'cfp',home.id,{lineContext},{priority:f.kind==='title'?156:135});
  const starFor=t=>s.players.filter(p=>p.team===t.id&&['QB','HB','RB','WR','TE'].includes(p.position)&&p.injury==='Uninjured').map(p=>{const checked=verifiedPlayerStats(s,p,'offense');if(!checked||checked.n<3)return null;const st={};for(const key of ['PASSYARDS','RUSHYARDS','RECEIVEYARDS','PASSTDS','RUSHTDS','RECEIVETDS','PASSINTS','RECEIVECATCHES']){const value=checked.read(key);if(value!==null)st[key]=value;}const yards=(st.PASSYARDS??0)+(st.RUSHYARDS??0)+(st.RECEIVEYARDS??0);return yards>300?{p,st,yards,line:completeOffensiveLine(p.position,st,{season:true})}:null;}).filter(x=>x?.line).sort((a,b)=>b.yards-a.yards||a.p.id.localeCompare(b.p.id))[0];
  const stars=depth>=2?[home,away].map(t=>({t,star:starFor(t)})).filter(x=>x.star):[];
  const fullMatchup=['ppg','ypg','ypp','ppga','ypga','yppa'].every(key=>Number.isFinite(stats.get(home.id)?.[key])&&Number.isFinite(stats.get(away.id)?.[key]));
  const personas=depth>=2?[1,2,3,4,5]:depth===1?[4,2]:[];
  for(const persona of personas){if(persona===4&&fullMatchup||persona===5&&stars.length)continue;const contrary=persona===2&&line&&line.spread>0&&line.spread<=14&&(line.spread<=7||hash(g.id+'|contrarian')%3===0),pick=contrary?underdog:fav??(hash(g.id+'|pick|'+persona)%2?home:away),opponent=pick.id===home.id?away:home;
   add('pick:'+persona,'pick-'+persona,'analyst',home.id,{pick:pick.name,opponent:opponent.name,lineContext,shape,shapeContext:shape==='lopsided'?'This projects as a mismatch, not a coin flip.':shape==='close'?'This projects as a close game.':shape==='favored'?'There is a clear lean, but the underdog has a path.':'The prediction is an opinion, not a claimed betting line.',analystPersona:persona,buzzReply:true,replyTeam:opponent.id},{priority:151-persona});
  }
  for(const {t,star} of stars)add('star:'+t.id,'star','analyst',t.id,{playerName:star.p.name,line:star.line,analystPersona:5},{player:star.p.id,priority:147});
  for(const t of [home,away]){const opponent=t===home?away:home,r=stats.get(t.id),d=stats.get(opponent.id),roster=s.players.filter(p=>p.team===t.id&&p.injury==='Uninjured').sort((a,b)=>a.id.localeCompare(b.id)),p=roster[hash(g.id+'|pregame|'+t.id)%Math.max(1,roster.length)];
   add('team:'+t.id,'team-pregame','official',t.id,{opponent:opponent.name},{priority:146});
   add('fan:'+t.id,'fan-pregame','fan',t.id,{opponent:opponent.name,persona:hash(t.id+'|buzz-fan')%2},{priority:143});
   if(p&&depth>=1)add('player:'+t.id,'player-pregame-'+playerStyle(p),'player',t.id,{opponent:opponent.name},{player:p.id,priority:149});
   if(depth>=1&&r&&d&&[r.ppg,r.ypg,r.ypp,d.ppga,d.ypga,d.yppa].every(Number.isFinite))add('breakdown:'+t.id,'matchup','analyst',t.id,{opponent:opponent.name,ppg:r.ppg.toFixed(1),ypg:r.ypg.toFixed(1),ypp:r.ypp.toFixed(2),ppga:d.ppga.toFixed(1),ypga:d.ypga.toFixed(1),yppa:d.yppa.toFixed(2),analystPersona:4},{priority:144});
   else if(depth>=1&&record(t))add('record:'+t.id,'record','beat',t.id,{opponent:opponent.name,record:record(t)},{priority:139});
  }
  if(depth>=2){
   const noRival=(t,c)=>t.id!==c.id&&!t.rivals?.includes(c.id)&&!c.rivals?.includes(t.id),picks=[];
   for(const t of outside){const allowed=[home,away].filter(c=>noRival(t,c));if(!allowed.length)continue;const same=allowed.filter(c=>c.conferenceId&&c.conferenceId===t.conferenceId),pool=same.length?same:allowed,choice=pool[hash(s.leagueId+'|rooting|'+t.id)%pool.length];picks.push({t,choice});if(picks.length>=4)break;}
   for(const {t,choice} of picks){add('watcher-fan:'+t.id,'watcher-fan','fan',t.id,{pick:choice.name,persona:hash(t.id+'|fan-tone')%2},{national:true,priority:t.id===s.userTeamIndex?149:138});}
   for(const {t} of picks.slice(0,2)){const pool=s.players.filter(p=>p.team===t.id).sort((a,b)=>a.id.localeCompare(b.id)),p=pool[hash(t.id+'|watching-player')%Math.max(1,pool.length)];if(p)add('watcher-player:'+t.id,'watcher-player-'+playerStyle(p),'player',t.id,{}, {player:p.id,national:true,priority:150});}
  }
 }
 return events;
}
