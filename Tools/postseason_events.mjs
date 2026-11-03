import {postseasonTiming} from './postseason_timing.mjs';
import {hash} from './story_authors.mjs';
import {recruitingClassRanks} from './season_ending_events.mjs';
const roleLabel={HeadCoach:'head coach',OffensiveCoordinator:'offensive coordinator',DefensiveCoordinator:'defensive coordinator'};
const awards={HEISMAN:'Heisman Trophy',BEST_HC:'national head coach award',BEST_AC:'national assistant coach award',BEST_QB:'top quarterback award',BEST_SR_QB:'top senior quarterback award',BEST_RB:'top running back award',BEST_REC:'top receiver award',BEST_TE:'top tight end award',BEST_IL:'top offensive lineman award',BEST_C:'top center award',BEST_DE:'top defensive end award',BEST_DL:'top defensive lineman award',BEST_LB:'top linebacker award',BEST_DB:'top defensive back award',BEST_KICK:'top kicker award',BEST_PUNT:'top punter award',BEST_DEF_1:'national defensive player award',BEST_DEF_2:'national defensive player award',BEST_PLAYER:'national player award',BEST_POTY:'player of the year award',BEST_SR:'top senior player award',BEST_FRESHMAN_POTY:'freshman of the year award',MOST_VERSATILE:'most versatile player award',BEST_ACADEMIC:'national academic award'};
const complete=g=>g.published!==false&&Number.isFinite(g.homeScore)&&Number.isFinite(g.awayScore)&&(g.status==='HomeWon'&&g.homeScore>g.awayScore||g.status==='AwayWon'&&g.awayScore>g.homeScore);
export function quarterfinalPaths(s){
 const teams=new Set(s.teams.filter(t=>t.id!==255).map(t=>t.id)),rows=(s.playoffBracket??[]).filter(g=>g.year===s.season.CurrentYear&&Number.isInteger(g.slot)&&g.slot>=0&&g.slot<=10),map=new Map();
 for(const g of rows){if(map.has(g.slot))return [];map.set(g.slot,g);}
 const firstTeams=new Set(),paths=[];
 for(let i=0;i<4;i++){const g=map.get(i);if(!g||g.phase!=='BowlSeason1'||![g.home,g.away].every(id=>teams.has(id))||g.home===g.away)return [];firstTeams.add(g.home);firstTeams.add(g.away);}
 if(firstTeams.size!==8)return [];
 const byes=new Set();
 for(let i=0;i<4;i++){
  // Native slots 0-3 feed quarterfinal slots 4-7. The observed Miami
  // slot 7 / Boise State-USC slot 3 example corroborates the pairing.
  const first=map.get(i),quarter=map.get(i+4);if(!quarter||quarter.phase!=='BowlSeason2'||quarter.week<=first.week)return [];
  const known=[quarter.home,quarter.away].filter(id=>teams.has(id)),bye=known.filter(id=>!firstTeams.has(id));if(bye.length!==1||byes.has(bye[0]))return [];
  byes.add(bye[0]);const opponent=known.find(id=>id!==bye[0]);
  if(opponent!==undefined&&(!complete(first)||opponent!==(first.homeScore>first.awayScore?first.home:first.away)))return [];
  paths.push({bye:bye[0],first,quarter});
 }
 return paths;
}
export function postseasonCandidates(s){
 const timing=postseasonTiming(s);if(s.reconstructed||!timing.locked)return [];
 const teams=new Map(s.teams.filter(t=>t.id!==255).map(t=>[t.id,t])),players=new Map(s.players.map(p=>[p.id,p])),events=[];
 const add=(id,family,voice,team,values={},options={})=>events.push({id:'postseason:'+id,category:options.category??'postseason',facts:{family:'postseason.'+family,voice,school:teams.get(team)?.name,...values},options:{team,national:false,priority:98,...options}});
 const currentGames=s.games.filter(g=>g.year===s.season.CurrentYear&&g.phase==='BowlSeason1'&&teams.has(g.home)&&teams.has(g.away)&&g.home!==g.away);
 for(const g of currentGames.filter(g=>g.status==='Unplayed'&&(g.bowlName||g.isPlayoff)))for(const [id,opp] of [[g.home,g.away],[g.away,g.home]]){
  add('invitation:'+g.id+':'+id,g.isPlayoff?'playoff-invite':'bowl-invite','official',id,{opponent:teams.get(opp).name,venue:g.bowlName??'the College Football Playoff',importance:g.isPlayoff?'major':'normal'},{category:g.isPlayoff?'cfp':'bowls',national:g.isPlayoff,relatedTeams:[opp],priority:g.isPlayoff?112:102,thread:'game:'+g.id});
 }
 for(const path of quarterfinalPaths(s)){
  const a=teams.get(path.first.home),b=teams.get(path.first.away),winner=complete(path.first)?teams.get(path.first.homeScore>path.first.awayScore?path.first.home:path.first.away):null;
  const values={first:a.name,second:b.name,quarterWeek:path.quarter.week,importance:'major'};
  add('bye:'+path.quarter.id,winner?'bye-opponent':'bye-path','cfp',path.bye,{...values,opponent:winner?.name??null},{category:'cfp',national:true,priority:114,relatedTeams:[a.id,b.id],thread:'quarter:'+path.quarter.id});
  add('bye-team:'+path.quarter.id,winner?'bye-team-opponent':'bye-team','official',path.bye,{...values,opponent:winner?.name??null},{category:'cfp',priority:109,relatedTeams:[a.id,b.id],thread:'quarter:'+path.quarter.id});
  add('bye-fan:'+path.quarter.id,winner?'bye-fan-opponent':'bye-fan','fan',path.bye,{...values,persona:1},{category:'cfp',priority:91,relatedTeams:[a.id,b.id],thread:'quarter:'+path.quarter.id});
 }
 const coveredAwards=new Set();
 for(const a of s.annualAwards??[]){const t=teams.get(a.team),p=players.get(a.player),label=awards[a.type];if(!t||a.year!==s.season.CurrentYear||!label||(!p&&!a.coachName))continue;
  const key=t.id+':'+(a.player??a.coach)+':'+label;if(coveredAwards.has(key))continue;coveredAwards.add(key);
  const count=new Set((s.annualAwards??[]).filter(x=>x.year===a.year&&x.team===a.team&&(x.player??x.coach)===(a.player??a.coach)&&awards[x.type]===label).map(x=>x.type)).size;
  const values={award:count>1?'national defensive player honors':label,count,playerName:p?.name??a.coachName,coachName:a.coachName??null,finalAward:true,nationalAward:true,analystPersona:0,importance:a.type==='HEISMAN'?'major':'normal'};
  add('award:'+a.id,a.type==='HEISMAN'?'heisman':count>1?'award-multiple':'award','analyst',t.id,values,{category:'awards',player:p?.id,national:true,priority:a.type==='HEISMAN'?132:105});
  if(p){add('award-team:'+a.id,'award-team','official',t.id,values,{category:'awards',player:p.id,priority:104});if(a.type==='HEISMAN'||hash(a.id+'|award-thanks')%3===0)add('award-player:'+a.id,'award-player','player',t.id,values,{category:'awards',player:p.id,priority:102});}
 }
 const honors=(s.allAmericanHonors??[]).filter(a=>a.year===s.season.CurrentYear&&players.get(a.player)?.team===a.team&&teams.has(a.team));
 const best=new Map();for(const a of honors.filter(a=>['ALL_AM_1ST','ALL_AM_2ND','ALL_AM_FR'].includes(a.type))){const key=a.player,order=['ALL_AM_1ST','ALL_AM_2ND','ALL_AM_FR'];if(!best.has(key)||order.indexOf(a.type)<order.indexOf(best.get(key).type))best.set(key,a);}
 for(const a of best.values()){const p=players.get(a.player),honor=a.type==='ALL_AM_1ST'?'first-team All-American':a.type==='ALL_AM_2ND'?'second-team All-American':'Freshman All-American';
  add('all-american:'+a.player,'all-american','analyst',a.team,{playerName:p.name,honor,award:honor,finalAward:true,nationalAward:true,analystPersona:5},{category:'awards',player:p.id,national:true,priority:101});
 }
 for(const t of teams.values()){
  const rows=honors.filter(a=>a.team===t.id),national=new Set(rows.filter(a=>!a.type.endsWith('_CONF')).map(a=>a.player)),conference=new Set(rows.filter(a=>a.type.endsWith('_CONF')).map(a=>a.player));
  if(national.size||conference.size)add('honors:'+t.id,'honors-team','official',t.id,{nationalCount:national.size,conferenceCount:conference.size},{category:'awards',priority:100});
 }
 const ranks=recruitingClassRanks(s),signed=(s.signings??[]).filter(c=>players.has(c.player)&&teams.has(c.team)),seenSigners=new Set();
 for(const c of signed){if(seenSigners.has(c.player))continue;seenSigners.add(c.player);const p=players.get(c.player),t=teams.get(c.team),stars=p.starRating??null;
  const rate=stars===5?100:stars===4?60:20;if(hash(s.leagueId+'|'+s.season.CurrentSeasonYear+'|'+c.player+'|signing-post')%100>=rate)continue;
  const document=c.recruitClass==='HighSchool'||c.recruitClass?.startsWith('JuniorCollege_')?'my letter of intent':'my signing paperwork';
  add('signed:'+c.team+':'+c.player,'signed','recruit',c.team,{playerName:p.name,position:p.position,stars,nationalRecruitRank:c.rank>0?c.rank:null,signed:true,newlyObserved:true,commitment:'Signed',document,importance:stars===5?'major':'normal'},{category:'recruiting',player:p.id,national:stars===5||c.rank>0&&c.rank<=100,priority:stars===5?110:99,thread:'signed:'+p.id});
 }
 for(const t of teams.values()){
  const rows=[...new Map(signed.filter(c=>c.team===t.id).map(c=>[c.player,c])).values()];if(!rows.length)continue;
  const five=rows.filter(c=>players.get(c.player).starRating===5).length,four=rows.filter(c=>players.get(c.player).starRating===4).length,rank=ranks.get(t.id);
  add('class:'+t.id,'signed-class','beat',t.id,{count:rows.length,fiveStars:five,fourStars:four,rankDetail:rank?` The current class ranking is No. ${rank}.`:''},{category:'recruiting',priority:103,national:five>=2});
 }
 const offers=new Map((s.coachOffers??[]).map(o=>[o.id,o])),used=new Set();
 for(const j of s.coachingOpenings??[]){const label=roleLabel[j.role],t=teams.get(j.team),old=j.previous;if(!label||!t)continue;
  if(j.filled&&(!j.selected||!j.current||j.selected.id!==j.current.id))continue;
  const values={coachName:old?.name??null,role:label,negative:j.reason==='Fired'};
  if(j.filled&&j.selected?.id===j.current?.id){
   const extension=j.selected.id===old?.id,accepted=j.offerIds.some(id=>offers.get(id)?.status==='Accepted');
   if(!extension||accepted)add('hire:'+j.id,extension?'coach-retained':'coach-hired','analyst',t.id,{...values,coachName:j.selected.name,contractTerm:Number.isInteger(j.selected.contract?.length)&&j.selected.contract.length>0?' The contract term is '+j.selected.contract.length+(j.selected.contract.length===1?' year.':' years.'):'',analystPersona:1},{category:'coaching',national:j.role==='HeadCoach',priority:108});
  }else if(old?.name&&['Fired','Retired','Pro','NewJob','ContractEnding'].includes(j.reason)){
   const stillThere=j.current?.id===old.id,family=j.reason==='Fired'?stillThere?'coach-pending':'coach-fired':j.reason==='Retired'?'coach-retired':j.reason==='Pro'?'coach-pro':j.reason==='NewJob'?'coach-departed':stillThere?'coach-contract':'coach-open';
   add('opening:'+j.id,family,'analyst',t.id,{...values,analystPersona:1},{category:'coaching',national:j.role==='HeadCoach',priority:j.role==='HeadCoach'?111:101});
   add('opening-fan:'+j.id,'coach-fan','fan',t.id,{...values,persona:1},{category:'coaching',priority:90});
  }
  if(j.filled)continue;
  let count=0;
  for(const id of [...j.offerIds].sort((a,b)=>(offers.get(a)?.index??999)-(offers.get(b)?.index??999)||a.localeCompare(b))){const o=offers.get(id);if(!o||used.has(id)||o.status!=='Pending'||o.team!==j.team||o.role!==j.role||!o.coach?.name||count>=2)continue;used.add(id);count++;
   add('offer:'+id,j.current?.id===o.coach.id?'coach-renewal-offer':'coach-offer','beat',t.id,{coachName:o.coach.name,role:label,contractTerm:Number.isInteger(o.length)&&o.length>0?' The proposed term is '+o.length+(o.length===1?' year.':' years.'):''},{category:'coaching',national:j.role==='HeadCoach',priority:99});
  }
 }
 return events;
}
export function seedPostseasonPublications(s,prior={}){
 const key=`${s.season.CurrentWeekType}/${s.season.CurrentWeek}`,candidates=postseasonCandidates(s),ids=new Set(candidates.map(e=>e.id));
 s.postseasonPublications=Object.fromEntries(Object.entries(prior).filter(([id,pub])=>pub!==key||ids.has(id)));
 for(const id of ids)if(!s.postseasonPublications[id])s.postseasonPublications[id]=key;
 return s.postseasonPublications;
}
export function postseasonEvents(s){
 const key=`${s.season.CurrentWeekType}/${s.season.CurrentWeek}`,events=postseasonCandidates(s).filter(e=>!s.postseasonPublications?.[e.id]||s.postseasonPublications[e.id]===key);
 if(!postseasonTiming(s).waiting)return events;
 for(const t of s.teams.filter(t=>t.id!==255&&t.wins>=5)){
  const playoff=t.cfpRank>=1&&t.cfpRank<=16,record=t.wins+'\u2013'+t.losses;
  events.push({id:'waiting:'+t.id,category:playoff?'cfp':'bowls',facts:{family:'postseason.'+(playoff?'waiting-playoff':'waiting-bowl'),voice:'beat',school:t.name,record},options:{team:t.id,national:playoff,priority:96}});
  if(hash(t.id+'|waiting-fan')%2===0)events.push({id:'waiting-fan:'+t.id,category:playoff?'cfp':'bowls',facts:{family:'postseason.waiting-fan',voice:'fan',persona:1,school:t.name},options:{team:t.id,national:false,priority:87}});
 }
 return events;
}
