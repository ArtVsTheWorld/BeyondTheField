import {publicPoll} from './public_polls.mjs';
import {brandAudience} from './story_engagement.mjs';
import {editorialRoots} from './feed_selection.mjs';
export function teamPostBudget(team){const {brand,poll}=brandAudience(team);return Math.max(5,Math.min(20,5+Math.round(15*(brand*.65+poll*.35))));}
// One shared allowance across all voices and all topics. A matchup consumes
// both involved teams' allowance; replies cannot outlive or exceed the parent.
export function applyWeeklyCoverage(stories,s){
 const ranks=publicPoll(s).ranks,budgets=new Map(s.teams.filter(t=>t.id!==255).map(t=>[t.id,teamPostBudget({...t,mediaRank:ranks[t.id]})])),counts=new Map(),children=new Map(),roots=[],chosen=new Set();
 for(const p of stories){if(p.replyTo){const list=children.get(p.replyTo)??[];list.push(p);children.set(p.replyTo,list);}else roots.push(p);}
 const slots=p=>[...new Set((p.teamIds??[]).filter(id=>budgets.has(id)))];
 function add(p){if(chosen.has(p.id))return false;const ids=slots(p);if(ids.some(id=>(counts.get(id)??0)>=budgets.get(id)))return false;chosen.add(p.id);for(const id of ids)counts.set(id,(counts.get(id)??0)+1);return true;}
 const focusGroups=new Map();for(const p of stories)if(p.eventFocus){const list=focusGroups.get(p.thread)??[];list.push(p);focusGroups.set(p.thread,list);for(const id of p.focusTeams??[])if(budgets.has(id))budgets.set(id,Math.max(budgets.get(id),p.eventFocus==='title'?20:p.eventFocus==='playoff'?16:budgets.get(id)));}
 // Keep one factual recap of the preceding game for each finalist. Hype
 // must not consume the whole allowance and erase how the team got here.
 for(const group of focusGroups.values())if(group[0].eventFocus==='title')for(const id of group[0].focusTeams??[]){const recap=editorialRoots(roots.filter(p=>!p.eventFocus&&p.id.endsWith(':box-story')&&slots(p).includes(id)))[0];if(recap)add(recap);}
 for(const group of focusGroups.values()){
  const focused=editorialRoots(group.filter(p=>!p.replyTo)),cap=group[0].eventFocus==='title'?20:group[0].eventFocus==='playoff'?16:12;let used=0;
  for(const p of focused){if(used>=cap)break;if(add(p)){used++;for(const child of children.get(p.id)??[])if(used<cap&&add(child))used++;}}
 }
 const ordered=editorialRoots(roots);
 // First reserve actual coverage for each program before shared national
// stories can consume the smaller school's whole allowance.
 const byTeam=new Map([...budgets.keys()].map(id=>[id,ordered.filter(p=>slots(p).includes(id))]));
 for(let round=0;round<5;round++)for(const [id,list] of byTeam){if((counts.get(id)??0)>round)continue;const p=list.find(p=>!chosen.has(p.id)&&slots(p).every(t=>(counts.get(t)??0)<budgets.get(t)));if(p)add(p);}
 // Replies get a bounded place in the same allowance, rather than an extra
 // hidden budget. Major news and the normal voice/category rotation follow.
 for(const p of ordered){if(!chosen.has(p.id)&&!add(p))continue;for(const child of children.get(p.id)??[])if(add(child))for(const sub of children.get(child.id)??[])add(sub);}
 return stories.filter(p=>chosen.has(p.id));
}
