import test from 'node:test';
import assert from 'node:assert/strict';
import {capitalizeSentences} from '../Tools/prose_cleanup.mjs';
test('sentence starts and I contractions capitalize without changing handles, decimals and abbreviations',()=>{
 assert.equal(capitalizeSentences("ready for this. next week is huge! let's go\ni'm ready"),"Ready for this. Next week is huge! Let's go\nI'm ready");
 assert.equal(capitalizeSentences('No. 3 vs. Ohio State, 7.6 YPC. good work @i @julian_040.'),'No. 3 vs. Ohio State, 7.6 YPC. Good work @i @julian_040.');
 assert.equal(capitalizeSentences('i.e. this is an example'),'I.e. this is an example');
});
