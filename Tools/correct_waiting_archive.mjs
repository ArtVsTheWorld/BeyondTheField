import {postseasonTiming} from './postseason_timing.mjs';
import {publishWeek} from './feed_selection.mjs';
// Targeted correction of the v75 waiting-week publication. Do not reconstruct
// unavailable old injuries/recruiting data from the current week's state.
export function correctWaitingArchive(feed,s){
 if(feed.phase!=='RegularSeason'||feed.week!==postseasonTiming(s).championshipWeek+1||feed.waitingWeekPolicy===1)return feed;
 const remove=p=>['standings','polls','heisman'].includes(p.category)||/^playoff:(rank|picture|local|fan):/.test(p.eventId??'')||/^late:conference-change:/.test(p.eventId??'');
 const premature=p=>/^late:berth:/.test(p.eventId??'')||/^playoff:(picture|local|fan):/.test(p.eventId??'')||/^late:bowl-position:/.test(p.eventId??'');
 if(!feed.stories.some(p=>remove(p)||premature(p)))return {...feed,waitingWeekPolicy:1};
 const eventMap=new Map((feed.events??[]).map(e=>[e.id,e]));
 let stories=feed.stories.filter(p=>!remove(p)||premature(p)).map(p=>{
  if(!premature(p))return p;
  const e=eventMap.get(p.eventId),school=e?.teamContext?.find(t=>t.teamId===p.teamIds?.[0])?.school;
  const body=school?(p.voice==='fan'?`${school} fans are waiting on next week's official selections. Yes, I have refreshed the projections again.`:`${school}'s postseason plans become official next week. This is the waiting week; there is no confirmed matchup to announce yet.`):'Postseason selections become official next week. This is the waiting week; matchups are still projections.';
  return {...p,body,rawBody:body,stamp:'Postseason',templateId:'P76-waiting-archive-correction',voiceTemplateId:null};
 });
 let changed=true;while(changed){const ids=new Set(stories.map(p=>p.id)),kept=stories.filter(p=>!p.replyTo||ids.has(p.replyTo));changed=kept.length!==stories.length;stories=kept;}
 const liveEvents=new Set(stories.map(p=>p.eventId)),events=(feed.events??[]).filter(e=>liveEvents.has(e.id)).map(e=>premature({eventId:e.id})?{...e,facts:{school:e.facts.school,waitingForSelection:true}}:e);
 return publishWeek({...feed,stories,events,waitingWeekPolicy:1});
}
