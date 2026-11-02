import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
const guide=JSON.parse(await fs.readFile(new URL('../Content/Editorial/voice-guide.json',import.meta.url),'utf8'));
const batch=JSON.parse(await fs.readFile(new URL('../Content/Editorial/review-samples.json',import.meta.url),'utf8'));
test('editorial reset has six voices and thirty distinct, unapproved review drafts',()=>{
 assert.equal(guide.approvedForRuntime,false);assert.equal(batch.approvedForRuntime,false);assert.equal(guide.freshStart.approvedRuntimeTemplates,0);assert.equal(guide.voices.length,6);assert.equal(batch.posts.length,30);
 assert.equal(new Set(batch.posts.map(p=>p.id)).size,30);for(const v of guide.voices)assert.equal(batch.posts.filter(p=>p.voice===v.id).length,5);
 assert.ok(batch.posts.every(p=>p.approvedForRuntime===false&&p.trigger&&p.scope));
});
test('every review draft resolves its slots, fits the tweet limit, and avoids game-system language',()=>{
 const banned=/\b(?:ovr|overall|rating|skill points?|dev(?:elopment)? trait|ability tier|simulation engine)\b/i;
 for(const p of batch.posts){const slots=[...p.body.matchAll(/\{([A-Za-z][A-Za-z0-9]*)\}/g)].map(m=>m[1]);assert.deepEqual(new Set(slots),new Set(Object.keys(p.exampleValues)),p.id);
  const rendered=p.body.replace(/\{([A-Za-z][A-Za-z0-9]*)\}/g,(_,k)=>p.exampleValues[k]);assert.equal(rendered,p.previewText,p.id);assert.ok([...rendered].length<=280,p.id);assert.ok(!banned.test(rendered),p.id);
 }
});
test('player/recruit drafts carry verified enum names and secondary native positions',()=>{
 const personalities=new Set(Object.values(guide.personalityPolicy.nativeValueMap));assert.deepEqual([...personalities],['Leader','Intense','Entertainer','TeamPlayer','Unpredictable']);
 const positions=new Set(Object.values(guide.personalityPolicy.positionGroups).flat());
 for(const p of batch.posts.filter(p=>['recruit','player'].includes(p.voice))){assert.ok(personalities.has(p.nativePersonality),p.id);assert.ok(positions.has(p.position),p.id);}
 assert.equal(batch.posts.find(p=>p.id==='PLAYER-02').nativePersonality,'Intense');assert.equal(batch.posts.find(p=>p.id==='PLAYER-02').position,'QB');
});

test('revised voices preserve stable natural handles and remove routine public self-blame',()=>{
 const seen=new Map();for(const p of batch.posts.filter(p=>['player','recruit'].includes(p.voice))){assert.ok(!/(QB|WR|RB|OL|CB)$/i.test(p.handle),p.id);if(seen.has(p.author))assert.equal(p.handle,seen.get(p.author),p.id);seen.set(p.author,p.handle);}
 for(const p of batch.posts.filter(p=>p.voice==='player'))assert.ok(!/got to be better|for me to clean up|my fault|I let|I cost/i.test(p.previewText),p.id);
 assert.equal(batch.posts.find(p=>p.id==='RECRUIT-03').authoredFlavor[0],'recruiting phone call');
});
test('analyst examples include metric evidence and correct sample arithmetic',()=>{
 for(const p of batch.posts.filter(p=>p.voice==='analyst'))assert.ok(p.analyticEvidence?.metric,p.id);
 const a=batch.posts.find(p=>p.id==='ANALYST-01');assert.equal(Number((a.analyticEvidence.rushingYards/a.analyticEvidence.gamesPlayed).toFixed(1)),a.exampleValues.rushingYardsPerGame);
 const t=batch.posts.find(p=>p.id==='ANALYST-02');assert.equal(Number((100*t.analyticEvidence.conversions/t.analyticEvidence.attempts).toFixed(1)),t.exampleValues.thirdDownPercent);
 const m=batch.posts.find(p=>p.id==='ANALYST-03');assert.equal(m.analyticEvidence.winnerScore-m.analyticEvidence.loserScore,m.exampleValues.margin);
 const v=batch.posts.find(p=>p.id==='ANALYST-04');assert.equal(v.analyticEvidence.takeaways-v.analyticEvidence.giveaways,v.exampleValues.margin);
 for(const p of batch.posts.filter(p=>p.voice==='analyst'&&p.body.includes('{playerName}')))assert.ok(p.body.includes('{school}')||p.body.includes('{hashtag}')||p.body.includes('{nickname}'),p.id);
});
test('fan disagreement points to a genuine review opinion rather than an invented analyst quote',()=>{
 const reply=batch.posts.find(p=>p.replyToReviewId),parent=batch.posts.find(p=>p.id===reply.replyToReviewId);assert.ok(parent);assert.equal(reply.conversationId,parent.conversationId);
 const quote=reply.previewText.match(/“([^”]+)”/)[1];assert.ok(parent.previewText.includes(quote));assert.equal(reply.requiresVisibleParent,true);
});
