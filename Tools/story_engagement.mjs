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
export const ENGAGEMENT_VERSION=3;
export function likesFor(s,id,voice,team,event,previous){
 if(previous?.engagementVersion===ENGAGEMENT_VERSION&&Number.isSafeInteger(previous?.likes)&&previous.likes>=0)return previous.likes;
 const {brand,poll}=brandAudience(team),seed=hash(`${s.leagueId}|${s.season.CurrentSeasonYear}|${s.season.CurrentWeekType}|${s.season.CurrentWeek}|${id}|likes-v2`);
 const reach={official:1,cfp:1,analyst:.9,beat:.65,model:.5,player:.8,recruit:.65,fan:.24}[voice]??.5;
 const major=event.facts?.importance==='major'||event.facts?.huge||event.category==='records'&&event.scopes.includes('national')||event.facts?.stars===5;
 const audience=Math.max(major?3600:0,80+brand*2700+poll*1800);
 return Math.max(1,Math.min(major?10000:5000,Math.round(audience*reach*(.45+(seed%10000)/10000*.7)*(major?2.8:1))));
}
export function replyLikesFor(s,id,parentLikes,previous){
 const low=Math.floor(parentLikes*.01),high=Math.floor(parentLikes*.2);
 if(previous?.engagementVersion===ENGAGEMENT_VERSION&&Number.isSafeInteger(previous.likes)&&previous.likes>=low&&previous.likes<=high)return previous.likes;
 const seed=hash(`${s.leagueId}|${s.season.CurrentSeasonYear}|${s.season.CurrentWeekType}|${s.season.CurrentWeek}|${id}|reply-likes`);
 return Math.floor(parentLikes*(1+seed%20)/100);
}
