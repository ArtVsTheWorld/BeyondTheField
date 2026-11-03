import {verifiedSeasonRecord} from './season_context.mjs';
import {gameStory} from './box_score_stories.mjs';
export function seasonStorylines(s){
 if(s.reconstructed||s.season.CurrentStage!=='NFLSeason')return [];
 const events=[],boxContext={teams:s.teams,players:[],performances:[]};
 for(const t of s.teams.filter(t=>t.id!==255)){
  const record=verifiedSeasonRecord(s,t);if(!record||record.played.length<4)continue;
  const recent=record.played.some(g=>g.phase===s.season.CurrentWeekType&&[s.season.CurrentWeek-1,s.season.CurrentWeek].includes(g.week));if(!recent)continue;
  const own=g=>g.home===t.id?g.homeScore:g.awayScore,other=g=>g.home===t.id?g.awayScore:g.homeScore,wins=record.played.filter(g=>own(g)>other(g)),narrowLosses=record.played.filter(g=>own(g)<other(g)&&other(g)-own(g)<=3);
  const add=(key,values)=>events.push({id:'season-story:'+t.id+':'+key,category:'analytics',facts:{family:'editorial.'+key,voice:'beat',school:t.name,record:record.record,...values},options:{team:t.id,national:false,priority:96,thread:'season-story:'+t.id+':'+key}});
  if(wins.length>=3&&wins.every(g=>own(g)-other(g)<=3))add('close-wins',{wins:wins.length,maxMargin:Math.max(...wins.map(g=>own(g)-other(g))),totalMargin:wins.reduce((n,g)=>n+own(g)-other(g),0)});
  if(narrowLosses.length>=3)add('close-losses',{count:narrowLosses.length,totalMargin:narrowLosses.reduce((n,g)=>n+other(g)-own(g),0)});
  const comebacks=wins.filter(g=>['fourth-comeback','half-comeback'].includes(gameStory(boxContext,g)?.kind));if(comebacks.length>=2)add('comebacks',{count:comebacks.length});
 }
 return events;
}
