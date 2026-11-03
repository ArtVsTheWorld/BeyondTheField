import {createHash} from 'node:crypto';
import {comparePublication} from './publication_timeline.mjs';
export const EDITORIAL_POLICY_VERSION=3;
const stable=v=>JSON.stringify(v,(_,x)=>x&&typeof x==='object'&&!Array.isArray(x)?Object.fromEntries(Object.entries(x).sort(([a],[b])=>a.localeCompare(b))):x);
const digest=v=>createHash('sha256').update(stable(v)).digest('hex');
export function validEditorialContext(e){
 const f=e.facts??{};
 if(e.category==='standings'&&Array.isArray(f.leaders))return f.leaders.length>0&&f.leaders.every(l=>Number.isInteger(l.wins)&&l.wins>=0&&Number.isInteger(l.losses)&&l.losses>=0&&(f.independent||Number.isInteger(l.conferencePlace)&&l.conferencePlace>=0))&&f.leaders.some(l=>l.wins+l.losses>0);
 if(f.family?.startsWith('matchup.protection')&&(Number(f.attack)===0||Number(f.defense)===0)&&f.protectionCorroborated!==true)return false;
 return true;
}
export function editorialTopic(e){
 const f=e.facts??{},family=f.family??'',team=e.teamIds?.[0]??f.school,person=e.playerId??f.playerName;
 let key,state;
 if(family==='cycle.team-reset'||family.startsWith('ending.team.')){key=['season-thanks',team];state=true;}
 else if(family==='cycle.player-reset'){key=['returner-thanks',team];state=true;}
 else if(['cycle.fan-future','cycle.fan-standards'].includes(family)){key=['fan-season-review',team];state=[f.record,f.verdict];}
 else if(['cycle.staff-plan','cycle.portal-plan'].includes(family)){key=[family,team];state=[f.coachName??null];}
 else if(['cycle.portal-needs','cycle.outlook','cycle.class-build'].includes(family)){key=[family,team];state=[f.position??null,f.count??null,f.record??null,f.classRank??null,f.verdict??null];}
 else if(family==='cycle.portal-target'){key=[family,team,person];state=[f.schools??null,f.formerSchool??null];}
 else if(family==='draft-talk.empty'){key=[family,team];state=true;}
 else if(e.id?.startsWith('portal-opening:')||family==='roster.interest'){
  key=['recruit-watch',person,team,family];state=[f.schools??null,f.stars??null,f.nationalRecruitRank??null,f.positionRecruitRank??null,f.stateRecruitRank??null,f.formerSchool??null];
 }else if(family==='roster.underdog'&&!f.newlyObserved&&!f.signed){key=[family,team,person];state=[f.stars,f.nationalRecruitRank??null];}
 else return null;
 return {key:stable(key),state:digest(state)};
}
// Remember actually published roots; crowded-out stories remain eligible.
export function freshEditorialEvents(events,publication,history=[]){
 const known=new Map();
 const previous=history.filter(f=>!f.reconstructed&&f.leagueId===publication.leagueId&&f.userTeamIndex===publication.userTeamIndex&&f.season===publication.season&&comparePublication(f,publication)<0).sort(comparePublication);
 for(const f of previous){const ids=new Set((f.stories??[]).filter(p=>!p.replyTo).map(p=>p.eventId));for(const e of f.events??[])if(ids.has(e.id)){const topic=editorialTopic(e);if(topic)known.set(topic.key,topic.state);}}
 const admitted=new Set(),seen=new Set();
 for(const e of [...events].sort((a,b)=>(b.priority??0)-(a.priority??0)||a.id.localeCompare(b.id))){if(!validEditorialContext(e))continue;const t=editorialTopic(e),key=t&&t.key+'|'+t.state;if(t&&(known.get(t.key)===t.state||seen.has(key)))continue;if(t)seen.add(key);admitted.add(e.id);}
 return events.filter(e=>admitted.has(e.id));
}
