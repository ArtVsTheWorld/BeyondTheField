import {normalizeDynasty} from './normalize_dynasty.mjs';
// Read-only FTC adapter. Never calls Franchise.save() or any field setter.
import fs from 'node:fs/promises';
import {pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
import {gunzipSync} from 'node:zlib';

export async function readDynasty(input, schemaPath, parserPath) {
  const {default:Franchise}=await import(pathToFileURL(parserPath));
  const schema=JSON.parse(gunzipSync(await fs.readFile(schemaPath)));
  const hash=b=>createHash('sha256').update(b).digest('hex');
  const before=hash(await fs.readFile(input));
  const file=await Franchise.create(input,{autoParse:true,saveOnChange:false,gameYearOverride:27,
    gameTypeOverride:'college',schemaOverride:{major:schema.meta.major,minor:schema.meta.minor,gameYear:27,path:schemaPath}});
  const tables=new Map(file.tables.map(t=>[t.header.tableId,t])),loaded=new Set();
  const vals=r=>Object.fromEntries(Object.entries(r.fields).map(([k,v])=>[k,v.value]));
  async function load(t){if(!loaded.has(t)){await t.readRecords();loaded.add(t);}return t;}
  async function resolve(ref){
    if(ref==null||ref==='00000000000000000000000000000000')return null;
    if(typeof ref!=='string'||!/^[01]{32}$/.test(ref))throw Error('Malformed Dynasty reference');
    const t=tables.get(parseInt(ref.slice(0,15),2)),row=parseInt(ref.slice(15),2);
    if(!t)throw Error('Missing referenced table');await load(t);const r=t.records[row];
    if(!r||r.isEmpty)throw Error('Dangling Dynasty reference');
    return {key:`${t.header.tableId}:${row}`,type:t.name,v:vals(r)};
  }
  async function records(name){const result=[];for(const t of file.tables.filter(t=>t.name===name&&!t.header.isArray)){
    await load(t);for(const r of t.records)if(!r.isEmpty)result.push({key:`${t.header.tableId}:${r.index}`,v:vals(r),capacity:t.header.recordCapacity});
  }return result;}
  async function array(ref){const a=await resolve(ref);if(!a)return [];const result=[];
    if(!a.type.endsWith('[]'))throw Error('Expected Dynasty array');
    for(const v of Object.values(a.v))if(typeof v==='string'&&/^[01]{32}$/.test(v)&&v.includes('1'))result.push(await resolve(v));return result;}
  const snapshot=await normalizeDynasty({records,resolve,array},{source:input,sha256:before});
  if(hash(await fs.readFile(input))!==before)throw Error('Dynasty save changed during reading; retry');
  return snapshot;
}
