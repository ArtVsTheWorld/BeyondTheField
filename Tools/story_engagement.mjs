import {publicPoll} from './public_polls.mjs';
import {hash} from './story_authors.mjs';
const grades=['F','DMinus','D','DPlus','CMinus','C','CPlus','BMinus','B','BPlus','AMinus','A','APlus'];
export function brandAudience(team){
 const grade=String(team?.brandExposure??'').replaceAll('+','Plus').replaceAll('-','Minus');
 const index=grades.findIndex(g=>g.toLowerCase()===grade.toLowerCase());
 // Missing native grades use a neutral audience, never a hidden player rating.
 const brand=index<0?.45:index/(grades.length-1),rank=team?.mediaRank;
 const poll=Number.isInteger(rank)&&rank>=1&&rank<=25?(26-rank)/25:0;
 return {brand,poll};
}
export const ENGAGEMENT_VERSION=4;
export function likesFor(s,id,voice,team,event,previous){
 if(previous?.engagementVersion===ENGAGEMENT_VERSION&&Number.isSafeInteger(previous?.likes)&&previous.likes>=0)return previous.likes;
 const rank=s.teams&&s.season?publicPoll(s).ranks[team?.id]:team?.mediaRank;
 const {brand,poll}=brandAudience({...team,mediaRank:rank}),seed=hash(`${s.leagueId}|${s.season.CurrentSeasonYear}|${s.season.CurrentWeekType}|${s.season.CurrentWeek}|${id}|likes-v4`);
 const f=event.facts??{},category=event.category??'',family=f.family??'';
 const championship=/champion|national-title|title-result/.test(family)&&!family.includes('watch'),playoff=category==='cfp'&&(/preview|result|champion|invite|bye/.test(family)||f.importance==='major'),award=category==='awards';
 const game=s.games?.find(g=>g.id===f.gameId),rivalry=Boolean(f.rivalry||game&&s.teams?.some(t=>[game.home,game.away].includes(t.id)&&(t.rivals??[]).includes(t.id===game.home?game.away:game.home)));
 const playoffGame=game?.isPlayoff===true||game?.phase==='NationalChampionship';
 const rankedRival=rivalry&&game&&[game.home,game.away].every(id=>{const r=s.teams?.find(t=>t.id===id);const n=r&&publicPoll(s).ranks[id];return n>=1&&n<=25;});
 const upset=category==='upsets',major=championship||playoff||playoffGame||award||rankedRival||upset||f.importance==='major'||f.huge||f.stars===5;
 const reach={official:.95,cfp:1,analyst:.62,beat:.4,model:.32,player:.45,recruit:.32,fan:.15}[voice]??.4;
 const attention=championship||game?.phase==='NationalChampionship'?3.4:playoff||playoffGame?2.8:upset?(f.huge?3:1.9):award?2.3:rankedRival?2.2:major?1.9:1;
 const related=major?(event.teamIds??[]).map(id=>s.teams?.find(t=>t.id===id)).filter(Boolean).map(t=>brandAudience({...t,mediaRank:publicPoll(s).ranks[t.id]})):[];
 const audience=70+Math.max(brand,...related.map(a=>a.brand))*2100+Math.max(poll,...related.map(a=>a.poll))*1400;
 const variation=.25+(seed%10000)/10000*1.1;
 return Math.max(1,Math.min(major?20000:5000,Math.round((audience*reach+(major?900:0))*variation*attention)));
}
export function replyLikesFor(s,id,parentLikes,previous){
 const low=Math.floor(parentLikes*.01),high=Math.floor(parentLikes*.2);
 if(previous?.engagementVersion===ENGAGEMENT_VERSION&&Number.isSafeInteger(previous.likes)&&previous.likes>=low&&previous.likes<=high)return previous.likes;
 const seed=hash(`${s.leagueId}|${s.season.CurrentSeasonYear}|${s.season.CurrentWeekType}|${s.season.CurrentWeek}|${id}|reply-likes`);
 return Math.floor(parentLikes*(1+seed%20)/100);
}
