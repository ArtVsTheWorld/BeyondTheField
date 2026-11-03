import {publicPoll} from './public_polls.mjs';
import {hash} from './story_authors.mjs';
// Coverage selection may use the poll's full native ordering; ranks beyond 25
// remain private selection inputs and are never printed as public Top-25 places.
export function nationalCoverage(s){
 const poll=publicPoll(s),valid=n=>Number.isInteger(n)&&n>=1&&n<=60;
 const teams=s.teams.filter(t=>t.id!==255&&valid(t[poll.field])).sort((a,b)=>a[poll.field]-b[poll.field]||a.id-b.id).slice(0,60);
 return new Set(teams.map(t=>t.id));
}
export function editorialAssignment(s,e,family,role,team,requestedPersona=0,coverage=null){
 // National prospect watches have no school beat. Use the established desks
 // instead of creating an unassigned "OnCollegeFootball" beat identity.
 if(role==='beat'&&!team&&family==='preseason.recruit.watch')return {role:'analyst',persona:hash(e.id+'|prospect-desk')%3===0?3:5};
 if(role!=='analyst')return {role,persona:requestedPersona};
 const covered=coverage??nationalCoverage(s),teamIds=e.teamIds??[];
 const draftTalk=e.category==='draft-discourse';
 const majorRecruit=['offers','recruiting','signings'].includes(e.category)&&(e.facts.stars===5||e.facts.recruitKind==='transfer'&&e.facts.stars>=4||e.facts.nationalRecruitRank<=100&&e.facts.nationalRecruitRank>=1);
 if(team&&teamIds.length&&!teamIds.some(id=>covered.has(id))&&!majorRecruit&&!draftTalk&&!e.facts.eventFocus&&!(e.facts.finalAward&&e.facts.nationalAward))return {role:'beat',persona:0};
 if(Number.isInteger(e.facts.analystPersona))return {role:'analyst',persona:e.facts.analystPersona};
 if(/recruit|freshman|breakout|heisman/.test(family))return {role:'analyst',persona:5};
 if(/poll|cfp/.test(family)&&e.category!=='analytics')return {role:'analyst',persona:1};
 // All five writers have regular-season opportunities, using stable topic IDs.
 const slot=hash(e.id+'|national-desk')%10;
 let persona=slot<2?1:slot<4?2:slot<6?3:slot<8?4:(e.playerId||e.facts.playerName?5:4);
 return {role:'analyst',persona};
}
