import {createHash} from 'node:crypto';
import {normalizeDynasty} from './normalize_dynasty.mjs';

export async function readRuntime(raw){
  if(raw.format!==1||raw.sourceKind!=='runtime'||!raw.records)throw Error('Invalid runtime capture');
  const index=new Map(),all=new Map(Object.entries(raw.records));
  for(const row of all.values()){if(!row||row.key==null||!row.v)throw Error('Invalid live record');const list=index.get(row.type)??[];list.push(row);index.set(row.type,list);}
  const records=async name=>index.get(name)??[];
  const resolve=async ref=>{if(ref==null)return null;const row=all.get(ref);if(!row)throw Error('Unresolved live record');return row;};
  const array=async ref=>{const row=await resolve(ref);if(!row)return [];if(!row.type.endsWith('[]'))throw Error('Expected runtime array');return Promise.all(Object.entries(row.v).sort(([a],[b])=>Number(a.slice(6))-Number(b.slice(6))).map(([,v])=>v).filter(v=>v!=null).map(resolve));};
  const flow=(await records('FranchiseServer_CareerFlow'))[0]?.v;
  if(!flow?.IsStageActive||flow.IsStageAdvancing)throw Error('Dynasty stage is inactive or advancing');
  const snapshot=await normalizeDynasty({records,resolve,array},{source:'runtime',sha256:'0'.repeat(64),sourceKind:'runtime'});
  snapshot.source=`runtime:${snapshot.leagueId}:${snapshot.userTeamIndex}`;
  // Content hash excludes pointers, schema internals, and unconsumed game fields.
  snapshot.sha256=createHash('sha256').update(JSON.stringify({...snapshot,sha256:undefined})).digest('hex');
  return snapshot;
}
