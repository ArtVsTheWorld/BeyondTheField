import fs from 'node:fs';
import {comparePublication} from './publication_timeline.mjs';
export const contentPack=JSON.parse(fs.readFileSync(new URL('../Content/Runtime/first-pack.json',import.meta.url),'utf8'));
const expansion=JSON.parse(fs.readFileSync(new URL('../Content/Runtime/analysis-pack.json',import.meta.url),'utf8'));
Object.assign(contentPack.families,expansion.families);contentPack.revision=expansion.revision;
const preseason=JSON.parse(fs.readFileSync(new URL('../Content/Runtime/preseason-pack.json',import.meta.url),'utf8'));
Object.assign(contentPack.families,preseason.families);contentPack.revision=preseason.revision;
const launch=JSON.parse(fs.readFileSync(new URL('../Content/Runtime/season-launch-pack.json',import.meta.url),'utf8'));
Object.assign(contentPack.families,launch.families);contentPack.revision=launch.revision;
const accounts=JSON.parse(fs.readFileSync(new URL('../Content/Runtime/account-refresh-pack.json',import.meta.url),'utf8'));
Object.assign(contentPack.families,accounts.families);contentPack.revision=accounts.revision;
const playoff=JSON.parse(fs.readFileSync(new URL('../Content/Runtime/playoff-desk-pack.json',import.meta.url),'utf8'));
Object.assign(contentPack.families,playoff.families);contentPack.revision=playoff.revision;
const historyPack=JSON.parse(fs.readFileSync(new URL('../Content/Runtime/history-analysis-pack.json',import.meta.url),'utf8'));
Object.assign(contentPack.families,historyPack.families);contentPack.revision=historyPack.revision;
const matchupPack=JSON.parse(fs.readFileSync(new URL('../Content/Runtime/matchup-season-pack.json',import.meta.url),'utf8'));
Object.assign(contentPack.families,matchupPack.families);contentPack.revision=matchupPack.revision;
const postseasonPack=JSON.parse(fs.readFileSync(new URL('../Content/Runtime/postseason-pack.json',import.meta.url),'utf8'));
Object.assign(contentPack.families,postseasonPack.families);contentPack.revision=postseasonPack.revision;
const contextPack=JSON.parse(fs.readFileSync(new URL('../Content/Runtime/context-pack.json',import.meta.url),'utf8'));
Object.assign(contentPack.families,contextPack.families);contentPack.revision=contextPack.revision;
const transactionsPack=JSON.parse(fs.readFileSync(new URL('../Content/Runtime/transactions-pack.json',import.meta.url),'utf8'));
Object.assign(contentPack.families,transactionsPack.families);contentPack.revision=transactionsPack.revision;
const cyclePack=JSON.parse(fs.readFileSync(new URL('../Content/Runtime/cycle-pack.json',import.meta.url),'utf8'));
Object.assign(contentPack.families,cyclePack.families);contentPack.revision=cyclePack.revision;
const reviewPack=JSON.parse(fs.readFileSync(new URL('../Content/Runtime/season-review-pack.json',import.meta.url),'utf8'));
Object.assign(contentPack.families,reviewPack.families);contentPack.revision=reviewPack.revision;
const portalPack=JSON.parse(fs.readFileSync(new URL('../Content/Runtime/portal-draft-pack.json',import.meta.url),'utf8'));
Object.assign(contentPack.families,portalPack.families);contentPack.revision=portalPack.revision;
const discoursePack=JSON.parse(fs.readFileSync(new URL('../Content/Runtime/offseason-discourse-pack.json',import.meta.url),'utf8'));
Object.assign(contentPack.families,discoursePack.families);contentPack.revision=discoursePack.revision;
const carryPack=JSON.parse(fs.readFileSync(new URL('../Content/Runtime/offseason-carryover-pack.json',import.meta.url),'utf8'));
Object.assign(contentPack.families,carryPack.families);contentPack.revision=carryPack.revision;
const editorialPack=JSON.parse(fs.readFileSync(new URL('../Content/Runtime/editorial-variety-pack.json',import.meta.url),'utf8'));
Object.assign(contentPack.families,editorialPack.families);contentPack.revision=editorialPack.revision;
const correctionsPack=JSON.parse(fs.readFileSync(new URL('../Content/Runtime/review-corrections-pack.json',import.meta.url),'utf8'));
Object.assign(contentPack.families,correctionsPack.families);contentPack.revision=correctionsPack.revision;
const analyticsVarietyPack=JSON.parse(fs.readFileSync(new URL('../Content/Runtime/analytics-variety-pack.json',import.meta.url),'utf8'));
Object.assign(contentPack.families,analyticsVarietyPack.families);contentPack.revision=analyticsVarietyPack.revision;
const voiceVarietyPack=JSON.parse(fs.readFileSync(new URL('../Content/Runtime/voice-variety-pack.json',import.meta.url),'utf8'));
Object.assign(contentPack.families,voiceVarietyPack.families);contentPack.revision=voiceVarietyPack.revision;
const eventVarietyPack=JSON.parse(fs.readFileSync(new URL('../Content/Runtime/event-variety-pack.json',import.meta.url),'utf8'));
Object.assign(contentPack.families,eventVarietyPack.families);contentPack.revision=eventVarietyPack.revision;
const reactionVarietyPack=JSON.parse(fs.readFileSync(new URL('../Content/Runtime/reaction-variety-pack.json',import.meta.url),'utf8'));
Object.assign(contentPack.families,reactionVarietyPack.families);contentPack.revision=reactionVarietyPack.revision;
const cycleVarietyPack=JSON.parse(fs.readFileSync(new URL('../Content/Runtime/cycle-variety-pack.json',import.meta.url),'utf8'));
Object.assign(contentPack.families,cycleVarietyPack.families);contentPack.revision=cycleVarietyPack.revision;
const buzzVarietyPack=JSON.parse(fs.readFileSync(new URL('../Content/Runtime/buzz-variety-pack.json',import.meta.url),'utf8'));
Object.assign(contentPack.families,buzzVarietyPack.families);contentPack.revision=buzzVarietyPack.revision;
const retrospectiveVarietyPack=JSON.parse(fs.readFileSync(new URL('../Content/Runtime/retrospective-variety-pack.json',import.meta.url),'utf8'));
Object.assign(contentPack.families,retrospectiveVarietyPack.families);contentPack.revision=retrospectiveVarietyPack.revision;
const openingVarietyPack=JSON.parse(fs.readFileSync(new URL('../Content/Runtime/opening-variety-pack.json',import.meta.url),'utf8'));
Object.assign(contentPack.families,openingVarietyPack.families);contentPack.revision=openingVarietyPack.revision;
const raceVarietyPack=JSON.parse(fs.readFileSync(new URL('../Content/Runtime/race-variety-pack.json',import.meta.url),'utf8'));
Object.assign(contentPack.families,raceVarietyPack.families);contentPack.revision=raceVarietyPack.revision;
const recruitingVarietyPack=JSON.parse(fs.readFileSync(new URL('../Content/Runtime/recruiting-variety-pack.json',import.meta.url),'utf8'));
Object.assign(contentPack.families,recruitingVarietyPack.families);contentPack.revision=recruitingVarietyPack.revision;
const reporterVarietyPack=JSON.parse(fs.readFileSync(new URL('../Content/Runtime/reporter-variety-pack.json',import.meta.url),'utf8'));
Object.assign(contentPack.families,reporterVarietyPack.families);contentPack.revision=reporterVarietyPack.revision;
const matchupVarietyPack=JSON.parse(fs.readFileSync(new URL('../Content/Runtime/matchup-variety-pack.json',import.meta.url),'utf8'));
Object.assign(contentPack.families,matchupVarietyPack.families);contentPack.revision=matchupVarietyPack.revision;
const fanVarietyPack=JSON.parse(fs.readFileSync(new URL('../Content/Runtime/fan-variety-pack.json',import.meta.url),'utf8'));
Object.assign(contentPack.families,fanVarietyPack.families);contentPack.revision=fanVarietyPack.revision;
const finalCycleVarietyPack=JSON.parse(fs.readFileSync(new URL('../Content/Runtime/final-cycle-variety-pack.json',import.meta.url),'utf8'));
Object.assign(contentPack.families,finalCycleVarietyPack.families);contentPack.revision=finalCycleVarietyPack.revision;
const compactVarietyPack=JSON.parse(fs.readFileSync(new URL('../Content/Runtime/compact-variety-pack.json',import.meta.url),'utf8'));
for(const [family,lines] of Object.entries(compactVarietyPack.families))contentPack.families[family].push(...lines);
contentPack.revision=compactVarietyPack.revision;

// These stock endings add no information to an otherwise factual analysis.
const emptyEndings=['The whole stat line belongs in the conversation.','Worth keeping alongside the headline numbers.','A profile worth following as the evaluation develops.','A candidate, not a coronation.','A useful unit comparison before kickoff.'];
for(const variants of Object.values(contentPack.families))for(const t of variants)for(const ending of emptyEndings)t.body=t.body.replace(ending,'').trim();
const slots=/\{([A-Za-z][A-Za-z0-9]*)\}/g,ids=new Set(),slotCache=new WeakMap();
for(const variants of Object.values(contentPack.families))for(const t of variants){
 if(!t.id||ids.has(t.id)||typeof t.body!=='string'||/[\uFFFD\u{1F000}-\u{1FAFF}\u2600-\u27BF]/u.test(t.body))throw Error('Invalid runtime template '+t.id);ids.add(t.id);
}
const historyKey=(publication,week)=>publication?`${publication.leagueId}|${publication.userTeamIndex}|${publication.season}|${publication.phase}|${publication.week}`:`week:${week}`;
export function templateHistory(history=[],publication=null,week=null){
 const recent=publication?history.filter(f=>f.season===publication.season&&(f.leagueId==null||f.leagueId===publication.leagueId)&&(f.userTeamIndex==null||f.userTeamIndex===publication.userTeamIndex)&&comparePublication(f,publication)<0).sort(comparePublication).slice(-contentPack.publicationPolicy.templateCooldownWeeks):history.filter(f=>f.week<week&&week-f.week<=contentPack.publicationPolicy.templateCooldownWeeks);
 const byHandle=new Map();for(let i=0;i<recent.length;i++)for(const p of recent[i].stories??[]){const used=byHandle.get(p.handle)??new Map();used.set(p.templateId,i);if(p.voiceTemplateId)used.set(p.voiceTemplateId,i);byHandle.set(p.handle,used);}
 return {history,key:historyKey(publication,week),byHandle};
}
function requiredSlots(t){let cached=slotCache.get(t);if(!cached||cached.body!==t.body){cached={body:t.body,keys:[...new Set([...t.body.matchAll(slots)].map(m=>m[1]))]};slotCache.set(t,cached);}return cached.keys;}
export function chooseTemplate(family,values,seed,{handle,week,history=[],sameStory,renderKey,transformBody=body=>body,style=null,avoidBodies=new Set(),publication=null,onCandidates=null,usage=null}={}){
 const eligible=(contentPack.families[family]??[]).filter(t=>requiredSlots(t).every(k=>values[k]!==null&&values[k]!==undefined));
 if(sameStory?.contentRevision===contentPack.revision&&sameStory.renderKey===renderKey&&eligible.some(t=>t.id===sameStory.templateId))return {body:sameStory.body,templateId:sameStory.templateId,cooldownFallback:sameStory.cooldownFallback??false};
 const context=usage?.history===history&&usage.key===historyKey(publication,week)?usage:templateHistory(history,publication,week),lastUsed=context.byHandle.get(handle)??new Map();
 // Prefer a different phrase for this account across weeks. If all valid phrases
 // are cooling down, use the least recent one rather than inventing news/facts.
 const compare=(a,b)=>Number(lastUsed.has(a.id))-Number(lastUsed.has(b.id))||Number(!!a.fallback)-Number(!!b.fallback)||(style?Number(a.style!==style)-Number(b.style!==style):0)||(lastUsed.get(a.id)??-1)-(lastUsed.get(b.id)??-1)||score(seed,a.id)-score(seed,b.id)||a.id.localeCompare(b.id);
 eligible.sort(compare);
 const render=t=>{const body=transformBody(t.body.replace(slots,(_,k)=>values[k])).replace(/[ \t]+\n/g,'\n').replace(/[ \t]{2,}/g,' ').trim();return body&&!/[\uFFFD\x00-\x08\x0b\x0c\x0e-\x1f]/u.test(body)&&[...body].length<=280&&Buffer.byteLength(body,'utf8')<=512?body:null;};
 const choice=(t,body)=>({body,templateId:t.id,cooldownFallback:lastUsed.has(t.id)});
 // Audits deliberately render every candidate. The normal path transforms only
 // as many as needed to find the same best valid, non-repeated wording.
 if(onCandidates){const ranked=eligible.map(t=>({t,body:render(t)})).filter(x=>x.body).sort((a,b)=>Number(avoidBodies.has(a.body))-Number(avoidBodies.has(b.body))||compare(a.t,b.t));onCandidates({family,values,style,candidates:ranked.map(({t,body})=>({id:t.id,body,style:t.style??null}))});return ranked.length?choice(ranked[0].t,ranked[0].body):null;}
 let repeated=null;for(const t of eligible){const body=render(t);if(!body)continue;const result=choice(t,body);if(!avoidBodies.has(body))return result;repeated??=result;}
 return repeated;
}
function score(seed,id){let n=2166136261;for(const c of seed+'|'+id){n^=c.codePointAt(0);n=Math.imul(n,16777619);}return n>>>0;}
