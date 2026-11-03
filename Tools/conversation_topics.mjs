export const bodyKey=text=>typeof text==='string'?text.normalize('NFKC').toLowerCase().replace(/[^\p{L}\p{N}@]+/gu,' ').trim():null;
export function canonicalTopic(e){
 if(!e)return null;const f=e.facts??{},player=e.playerId??f.playerName;
 if(player&&(f.recruitKind==='transfer'||e.id?.startsWith('portal-opening:')&&!e.id.includes('unsigned'))){const state=f.signed?'signed':f.newlyObserved?'commitment':f.flipped||f.decommitted?'changed':'open';return 'portal:'+player+':'+state+(state==='open'?'':':'+(f.school??f.destination??''));}
 return null;
}
export function deduplicateConversations(stories,events=[]){
 const eventMap=new Map(events.map(e=>[e.id,e])),kept=new Set(),seen=new Set();
 for(const p of stories){const topic=p.canonicalTopic??canonicalTopic(eventMap.get(p.eventId)),body=bodyKey(p.body),key=p.replyTo&&topic&&['fan','player','recruit'].includes(p.voice)?'reaction|'+p.handle+'|'+topic:body&&p.handle&&!p.coverageExempt&&p.voice!=='nflDraft'?'text|'+p.handle+'|'+body:null;
  if(key&&seen.has(key))continue;if(key)seen.add(key);kept.add(p.id);
 }
 // Remove descendants when an equivalent parent was rejected; never reparent a reply.
 let changed=true;while(changed){changed=false;for(const p of stories)if(kept.has(p.id)&&p.replyTo&&!kept.has(p.replyTo)){kept.delete(p.id);changed=true;}}
 return stories.filter(p=>kept.has(p.id));
}
