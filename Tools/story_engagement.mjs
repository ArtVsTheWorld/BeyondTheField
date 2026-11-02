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
export function likesFor(s,id,voice,team,event,previous){
 if(Number.isSafeInteger(previous?.likes)&&previous.likes>=0)return previous.likes;
 const {brand,poll}=brandAudience(team),seed=hash(`${s.leagueId}|${s.season.CurrentSeasonYear}|${s.season.CurrentWeekType}|${s.season.CurrentWeek}|${id}|likes`);
 const reach={official:1.5,analyst:1.25,beat:.7,model:.45,player:1,recruit:.4,fan:.12}[voice]??.5;
 const importance=event.scopes.includes('national')?1.6:1;
 return Math.max(1,Math.round((30+brand**2*18000+poll*9000)*reach*importance*(.35+(seed%10000)/10000*1.3)));
}
