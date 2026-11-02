import fs from 'node:fs';
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
const slots=/\{([A-Za-z][A-Za-z0-9]*)\}/g,ids=new Set();
for(const variants of Object.values(contentPack.families))for(const t of variants){
 if(!t.id||ids.has(t.id)||typeof t.body!=='string'||/[\uFFFD\u{1F000}-\u{1FAFF}\u2600-\u27BF]/u.test(t.body))throw Error('Invalid runtime template '+t.id);ids.add(t.id);
}
export function chooseTemplate(family,values,seed,{handle,week,history=[],sameStory,renderKey}={}){
 const eligible=(contentPack.families[family]??[]).filter(t=>[...t.body.matchAll(slots)].every(m=>values[m[1]]!==null&&values[m[1]]!==undefined));
 if(sameStory?.contentRevision===contentPack.revision&&sameStory.renderKey===renderKey&&eligible.some(t=>t.id===sameStory.templateId))return {body:sameStory.body,templateId:sameStory.templateId,cooldownFallback:sameStory.cooldownFallback??false};
 const lastUsed=new Map();
 for(const f of history)if(f.week<week&&week-f.week<=contentPack.publicationPolicy.templateCooldownWeeks)for(const p of f.stories??[])if(p.handle===handle){lastUsed.set(p.templateId,Math.max(lastUsed.get(p.templateId)??-1,f.week));if(p.voiceTemplateId)lastUsed.set(p.voiceTemplateId,Math.max(lastUsed.get(p.voiceTemplateId)??-1,f.week));}
 // Prefer a different phrase for this account across weeks. If all valid phrases
 // are cooling down, use the least recent one rather than inventing news/facts.
 const ranked=[...eligible].sort((a,b)=>(lastUsed.get(a.id)??-1)-(lastUsed.get(b.id)??-1)||score(seed,a.id)-score(seed,b.id)||a.id.localeCompare(b.id));
 for(const t of ranked){const body=t.body.replace(slots,(_,k)=>values[k]).replace(/[ \t]+\n/g,'\n').replace(/[ \t]{2,}/g,' ').trim();if(body&&!/[\uFFFD\x00-\x08\x0b\x0c\x0e-\x1f]/u.test(body)&&[...body].length<=280&&Buffer.byteLength(body,'utf8')<=512)return {body,templateId:t.id,cooldownFallback:lastUsed.has(t.id)};}
 return null;
}
function score(seed,id){let n=2166136261;for(const c of seed+'|'+id){n^=c.codePointAt(0);n=Math.imul(n,16777619);}return n>>>0;}
