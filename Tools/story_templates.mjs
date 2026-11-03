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
// These stock endings add no information to an otherwise factual analysis.
const emptyEndings=['The whole stat line belongs in the conversation.','Worth keeping alongside the headline numbers.','A profile worth following as the evaluation develops.','A candidate, not a coronation.','A useful unit comparison before kickoff.'];
for(const variants of Object.values(contentPack.families))for(const t of variants)for(const ending of emptyEndings)t.body=t.body.replace(ending,'').trim();
const slots=/\{([A-Za-z][A-Za-z0-9]*)\}/g,ids=new Set();
for(const variants of Object.values(contentPack.families))for(const t of variants){
 if(!t.id||ids.has(t.id)||typeof t.body!=='string'||/[\uFFFD\u{1F000}-\u{1FAFF}\u2600-\u27BF]/u.test(t.body))throw Error('Invalid runtime template '+t.id);ids.add(t.id);
}
export function chooseTemplate(family,values,seed,{handle,week,history=[],sameStory,renderKey,transformBody=body=>body,style=null,avoidBodies=new Set(),publication=null}={}){
 const eligible=(contentPack.families[family]??[]).filter(t=>[...t.body.matchAll(slots)].every(m=>values[m[1]]!==null&&values[m[1]]!==undefined));
 if(sameStory?.contentRevision===contentPack.revision&&sameStory.renderKey===renderKey&&eligible.some(t=>t.id===sameStory.templateId))return {body:sameStory.body,templateId:sameStory.templateId,cooldownFallback:sameStory.cooldownFallback??false};
 const lastUsed=new Map();
 const recent=publication?history.filter(f=>f.season===publication.season&&(!f.leagueId||f.leagueId===publication.leagueId)&&(!f.userTeamIndex||f.userTeamIndex===publication.userTeamIndex)&&comparePublication(f,publication)<0).sort(comparePublication).slice(-contentPack.publicationPolicy.templateCooldownWeeks):history.filter(f=>f.week<week&&week-f.week<=contentPack.publicationPolicy.templateCooldownWeeks);
 for(let i=0;i<recent.length;i++)for(const p of recent[i].stories??[])if(p.handle===handle){lastUsed.set(p.templateId,i);if(p.voiceTemplateId)lastUsed.set(p.voiceTemplateId,i);}
 // Prefer a different phrase for this account across weeks. If all valid phrases
 // are cooling down, use the least recent one rather than inventing news/facts.
 const ranked=eligible.map(t=>({t,body:transformBody(t.body.replace(slots,(_,k)=>values[k])).replace(/[ \t]+\n/g,'\n').replace(/[ \t]{2,}/g,' ').trim()})).filter(({body})=>body&&!/[\uFFFD\x00-\x08\x0b\x0c\x0e-\x1f]/u.test(body)&&[...body].length<=280&&Buffer.byteLength(body,'utf8')<=512).sort((a,b)=>Number(avoidBodies.has(a.body))-Number(avoidBodies.has(b.body))||(style?Number(a.t.style!==style)-Number(b.t.style!==style):0)||(lastUsed.get(a.t.id)??-1)-(lastUsed.get(b.t.id)??-1)||score(seed,a.t.id)-score(seed,b.t.id)||a.t.id.localeCompare(b.t.id));
 if(ranked.length){const {t,body}=ranked[0];return {body,templateId:t.id,cooldownFallback:lastUsed.has(t.id)};}
 return null;
}
function score(seed,id){let n=2166136261;for(const c of seed+'|'+id){n^=c.codePointAt(0);n=Math.imul(n,16777619);}return n>>>0;}
