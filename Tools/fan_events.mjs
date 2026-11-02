import {hash} from './story_authors.mjs';
const final=g=>g.published!==false&&['HomeWon','AwayWon','Tie'].includes(g.status)&&Number.isFinite(g.homeScore)&&Number.isFinite(g.awayScore);
// Barstool is a fan account with independent posts, not only a reply bot.
// After Dark retains the more personal/reactive role in existing reactions.
export function fanAccountEvents(s){
 if(s.reconstructed||s.season.CurrentStage!=='NFLSeason')return [];
 const teams=new Map(s.teams.filter(t=>t.id!==255).map(t=>[t.id,t])),events=[];
 for(const g of s.games.filter(g=>g.year===s.season.CurrentYear&&g.phase===s.season.CurrentWeekType&&[s.season.CurrentWeek-1,s.season.CurrentWeek].includes(g.week)&&final(g)))for(const [id,other] of [[g.home,g.away],[g.away,g.home]]){
  const t=teams.get(id),opponent=teams.get(other);if(!t||!opponent||s.seasonEndPublications?.[id])continue;
  if(hash(s.leagueId+'|'+g.id+'|'+id+'|barstool-root')%100>=65)continue;
  const own=id===g.home?g.homeScore:g.awayScore,against=id===g.home?g.awayScore:g.homeScore,win=own>against,rival=t.rivals?.includes(other)||opponent.rivals?.includes(id),mood=own===against?'tie':win?rival?'rivalry-win':'win':Math.abs(own-against)>=21?'bad-loss':'loss';
  events.push({id:`barstool:${g.id}:${id}`,category:'results',facts:{family:'fanclub.'+mood,voice:'fan',persona:1,school:t.name,opponent:opponent.name,score:own+'\u2013'+against,negative:!win},options:{team:id,relatedTeams:[other],national:false,eventWeek:g.week,priority:win&&rival?96:89,thread:'game:'+g.id}});
 }
 for(const g of s.games.filter(g=>g.year===s.season.CurrentYear&&g.phase===s.season.CurrentWeekType&&g.week===s.season.CurrentWeek&&g.status==='Unplayed')){
  const h=teams.get(g.home),a=teams.get(g.away);if(!h||!a||!(h.rivals?.includes(a.id)||a.rivals?.includes(h.id)))continue;
  for(const [t,opp] of [[h,a],[a,h]])events.push({id:`barstool-preview:${g.id}:${t.id}`,category:'schedule',facts:{family:'fanclub.rivalry-week',voice:'fan',persona:1,school:t.name,opponent:opp.name},options:{team:t.id,relatedTeams:[opp.id],national:false,priority:96,thread:'game:'+g.id,eventWeek:g.week}});
 }
 return events;
}
