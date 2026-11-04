// Immutable edition blobs plus an atomic index. Original monolithic archives
// remain available; migration never overwrites them or rewrites past wording.
import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
const REFERENCE=Symbol('edition archive reference');
const hash=text=>createHash('sha256').update(text).digest('hex');
const indexFile=file=>file.replace(/\.json$/,'.index.json');
const blobPath=(dir,name)=>{if(!/^(feed|snapshot|carry)-[a-f0-9]{64}\.json$/.test(name))throw Error('Invalid archive blob reference');return path.join(dir,'.history-data',name);};
async function optionalJson(file){try{return JSON.parse(await fs.readFile(file,'utf8'));}catch(e){if(e.code==='ENOENT')return null;throw e;}}
async function blob(dir,name){const file=blobPath(dir,name),text=await fs.readFile(file,'utf8');if(hash(text)!==name.slice(name.indexOf('-')+1,-5))throw Error('Archive blob checksum mismatch');return JSON.parse(text);}
export async function atomicJsonFile(file,data){const tmp=`${file}.${process.pid}.tmp`;try{await fs.writeFile(tmp,JSON.stringify(data));await fs.rename(tmp,file);}finally{await fs.rm(tmp,{force:true}).catch(()=>{});}}
export async function readEditionHistory(file,{activeWeek=null,archiveOnly=false}={}){
 const index=await optionalJson(indexFile(file));
 if(!index){const old=await optionalJson(file);if(old&&(old.format!==1||!Array.isArray(old.editions)))throw Error('Invalid runtime history');return old;}
 if(index.format!==2||!Array.isArray(index.editions)||index.editions.length>48)throw Error('Invalid edition archive index');
 const dir=path.dirname(file),keys=new Set();
 const previous=Number.isInteger(activeWeek)?index.editions.filter(e=>!e.reconstructed&&e.snapshotFile&&e.week<activeWeek).sort((a,b)=>b.week-a.week)[0]?.key:null;
 const latest=index.editions.filter(e=>e.snapshotFile).sort((a,b)=>b.week-a.week)[0]?.key;
 const editions=[];
 for(const meta of index.editions){
  if(typeof meta.key!=='string'||keys.has(meta.key)||typeof meta.scope!=='string'||!Number.isInteger(meta.week))throw Error('Invalid edition archive identity');keys.add(meta.key);
  const feed=await blob(dir,meta.feedFile);if(feed.key!==meta.key||feed.week!==meta.week||meta.scope!==`${feed.leagueId}/${feed.userTeamIndex}/${feed.season}/${feed.phase}`)throw Error('Edition blob/index identity mismatch');
  const full=!archiveOnly&&(!Number.isInteger(activeWeek)||meta.week===activeWeek||meta.key===previous);
  const snapshot=meta.snapshotFile?(full?await blob(dir,meta.snapshotFile):{...meta.snapshotSummary,...(archiveOnly&&meta.key===latest&&meta.carryFile?await blob(dir,meta.carryFile):{})}):undefined;
  const entry={scope:meta.scope,week:meta.week,key:meta.key,...(meta.reconstructed?{reconstructed:true}:{}),...(snapshot?{snapshot}:{}),feed};
  entry[REFERENCE]={dir,meta,full};editions.push(entry);
 }
 return {format:1,editions,authors:index.authors??{}};
}
async function writeBlob(dir,kind,data){
 const text=JSON.stringify(data),name=`${kind}-${hash(text)}.json`,file=blobPath(dir,name);
 try{const old=await fs.readFile(file,'utf8');if(old!==text)throw Error('Existing archive blob differs from its checksum');}
 catch(e){if(e.code!=='ENOENT')throw e;const tmp=`${file}.${process.pid}.tmp`;try{await fs.writeFile(tmp,text);await fs.rename(tmp,file);}finally{await fs.rm(tmp,{force:true}).catch(()=>{});}}
 return name;
}
export async function writeEditionHistory(file,state){
 if(state.format!==1||!Array.isArray(state.editions)||state.editions.length>48)throw Error('Invalid runtime history for archive write');
 const dir=path.dirname(file);await fs.mkdir(path.join(dir,'.history-data'),{recursive:true});const editions=[];
 for(const entry of state.editions){
  const reference=entry[REFERENCE],prior=reference?.meta;
  if(reference&&!reference.full&&reference.dir!==dir)throw Error('A partial snapshot cannot migrate to another archive');
  const reuse=reference&&reference.dir===dir&&prior.key===entry.key;
  const snapshotFile=entry.snapshot?(reuse&&!reference.full?prior.snapshotFile:await writeBlob(dir,'snapshot',entry.snapshot)):null;
  const summary=entry.snapshot?Object.fromEntries(['sha256','recentDraftClass'].filter(k=>entry.snapshot[k]!==undefined).map(k=>[k,entry.snapshot[k]])):null;
  const carryFile=entry.snapshot?(reuse&&!reference.full?prior.carryFile:await writeBlob(dir,'carry',Object.fromEntries(['milestoneTotals','postseasonPublications','seasonEndPublications'].filter(k=>entry.snapshot[k]!==undefined).map(k=>[k,entry.snapshot[k]])))):null;
  editions.push({scope:entry.scope,week:entry.week,key:entry.key,reconstructed:entry.reconstructed===true,feedFile:await writeBlob(dir,'feed',entry.feed),snapshotFile,carryFile,snapshotSummary:summary});
 }
 await atomicJsonFile(indexFile(file),{format:2,authors:state.authors??{},editions});
}
