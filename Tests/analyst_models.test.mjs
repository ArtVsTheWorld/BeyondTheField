import test from 'node:test';import assert from 'node:assert/strict';
import {analystProjection,projectLine} from '../Tools/betting_model.mjs';
test('analysts emphasize different verified evidence instead of sharing a bookmaker line',()=>{
 const s={teams:[{id:1,rivals:[]},{id:2,rivals:[]}],players:[]},g={home:1,away:2,neutral:true};
 const strengths=new Map([[1,{off:88,def:79,st:77,units:{QB:94}}],[2,{off:75,def:86,st:80,units:{QB:79}}]]);
 const row=(id,ppg,ppga,ypp,yppa)=>({n:4,team:{id},ppg,ppga,ypp,yppa,games:Array.from({length:4},(_,week)=>({week,home:id,homeScore:ppg,awayScore:ppga}))});
 const stats=new Map([[1,row(1,30,24,5,6)],[2,row(2,38,17,7,4)]]),lines=[1,2,3,4,5].map(p=>analystProjection(s,g,p,{strengths,stats}));
 assert.equal(new Set(lines.map(l=>l.model)).size,5);assert.ok(new Set(lines.map(l=>l.homeSpread)).size>=4);assert.ok(lines.some(l=>l.favorite===1)&&lines.some(l=>l.favorite===2));
 assert.ok(lines.every(l=>Number.isFinite(l.spread)&&l.spread<=45));assert.ok(!lines.every(l=>l.homeSpread===projectLine(s,g,strengths).homeSpread));
});
test('missing verified statistics use roster evidence without inventing performance',()=>{
 const s={teams:[{id:1},{id:2}],players:[]},g={home:1,away:2},strengths=new Map([[1,{off:80,def:80,st:80,units:{QB:80}}],[2,{off:80,def:80,st:80,units:{QB:80}}]]);
 assert.equal(analystProjection(s,g,4,{strengths,stats:new Map()}).spread,2.5);
 assert.equal(analystProjection(s,g,4,{strengths:new Map(),stats:new Map()}),null);
});
