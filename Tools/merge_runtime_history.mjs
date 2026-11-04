// Installation-only migration. Sources are read-only; newest source per scope
// wins conflicts, while editions unique to either source remain available.
import fs from 'node:fs/promises';
import path from 'node:path';
import {isDeepStrictEqual} from 'node:util';
import {readHistory,writeHistory} from './runtime_archive.mjs';
const [target,...sources]=process.argv.slice(2).map(p=>path.resolve(p));
if(!target||!sources.length||sources.some(s=>s===target||target.startsWith(s+path.sep)||s.startsWith(target+path.sep)))throw Error('Use a separate history migration destination');
const scopes=new Map(),ledgers=new Map();
async function walk(root,dir=root){
 for(const f of await fs.readdir(dir,{withFileTypes:true})){
  const p=path.join(dir,f.name);if(f.isDirectory()){if(f.name!=='.history-data')await walk(root,p);continue;}
  if(f.name==='history.json'||f.name==='history.index.json'){
   const relative=path.relative(root,dir),key=root+'|'+relative,stat=await fs.stat(p),items=scopes.get(relative)??new Map();
   const old=items.get(key);if(!old||f.name==='history.index.json')items.set(key,{file:path.join(dir,'history.json'),mtime:stat.mtimeMs});scopes.set(relative,items);
  }else if(f.name==='offseason-ledger.json'){
   const relative=path.relative(root,p),stat=await fs.stat(p),old=ledgers.get(relative);if(!old||old.mtime<stat.mtimeMs)ledgers.set(relative,{file:p,mtime:stat.mtimeMs});
  }
 }
}
for(const s of sources)await walk(s);
let editions=0,stories=0;
for(const [relative,items] of scopes){
 const merged=new Map();let authors={};
 for(const source of [...items.values()].sort((a,b)=>a.mtime-b.mtime)){
  const h=await readHistory(source.file);if(!h)continue;authors={...authors,...h.authors};
  for(const e of h.editions)merged.set(e.key,e);
 }
 const expected=[...merged.values()].sort((a,b)=>a.week-b.week),file=path.join(target,relative,'history.json');
 await writeHistory(file,{format:1,authors,editions:expected});
 const actual=await readHistory(file,{archiveOnly:true});
 if(actual.editions.length!==expected.length||actual.editions.some((e,i)=>!isDeepStrictEqual(e.feed,expected[i].feed)))throw Error('Migrated edition changed');
 editions+=expected.length;stories+=expected.reduce((n,e)=>n+e.feed.stories.length,0);
}
for(const [relative,source] of ledgers){const p=path.join(target,relative);await fs.mkdir(path.dirname(p),{recursive:true});await fs.copyFile(source.file,p);if(!Buffer.from(await fs.readFile(source.file)).equals(await fs.readFile(p)))throw Error('Ledger migration changed');}
console.log(JSON.stringify({scopes:scopes.size,editions,stories,ledgers:ledgers.size,exactFeeds:true,sourceArchivesChanged:false}));
