import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {extractResumeInputs,resumeIdentity} from '../Tools/recruit_resume_data.mjs';
const config=JSON.parse(await readFile(new URL('../Config/high-school-state-strength.json',import.meta.url),'utf8'));
const player={PresentationId:2493,FirstName:'Luke',LastName:'Callen',PLYR_HOME_TOWN:'Buffalo',PLYR_HOME_STATE:'NewYork',PLYR_BIRTHDATE:20080101,Position:'QB',OverallRating:67,ThrowPowerRating:92,TraitDevelopment:'Normal',ProspectStarRating:'THREE_STAR'};
const snapshot=()=>({format:1,sourceKind:'runtime',status:{season:{CurrentSeasonYear:2026}},records:{f:{type:'Franchise',v:{LeagueID:-1649480587}},p:{type:'Player',v:{...player}},'4281:1748':{key:'4281:1748',type:'Recruit',capacity:7600,v:{Class:'HighSchool',Player:'p'}}}});
test('Persistent identity excludes file, scouting, week, position and mutable ability',()=>{
 const original=resumeIdentity(-1649480587,player);
 assert.equal(original,resumeIdentity(2645486709,{...player,Position:'HB',OverallRating:99,TraitDevelopment:'College_Elite',Age:19,PercentageScouted:100}));
 assert.notEqual(original,resumeIdentity(123,player));assert.notEqual(original,resumeIdentity(-1649480587,{...player,PresentationId:2500}));
 assert.equal(resumeIdentity(123,{...player,PLYR_BIRTHDATE:0}),resumeIdentity(123,{...player,PLYR_BIRTHDATE:undefined}));
});
test('Only native HS recruits enter the generated high-school pipeline',()=>{
 const raw=snapshot(),before=JSON.stringify(raw);const data=extractResumeInputs(raw,config);
 assert.equal(JSON.stringify(raw),before);assert.equal(data.prospects[0].nativeRecruitId,561120980);assert.equal(data.prospects[0].stateRank,30);
 for(const kind of ['JuniorCollege_Sophomore','Transfer_Senior']){raw.records['4281:1748'].v.Class=kind;assert.equal(extractResumeInputs(raw,config).prospects.length,0);}
});
test('Rank catalog and neutral origins preserve the requested baseline',()=>{
 assert.equal(new Set(config.rankedStates).size,50);assert.equal(config.rankedStates[0],'Florida');assert.equal(config.rankedStates[49],'Vermont');
 const raw=snapshot();raw.records.p.v.PLYR_HOME_STATE='NonUS';assert.equal(extractResumeInputs(raw,config).prospects[0].stateRank,null);
 raw.records.p.v.PLYR_HOME_STATE='DistrictOfColumbia';assert.equal(extractResumeInputs(raw,config).prospects[0].stateRank,21);
});
test('Ambiguous identities and incomplete hidden data fail before generation',()=>{
 const raw=snapshot();raw.records.duplicate={...raw.records['4281:1748'],key:'4281:1749'};assert.throws(()=>extractResumeInputs(raw,config),/Ambiguous/);
 delete raw.records.duplicate;delete raw.records.p.v.TraitDevelopment;assert.throws(()=>extractResumeInputs(raw,config),/Incomplete/);
 const ambiguous=snapshot();ambiguous.records.other={type:'Franchise',v:{LeagueID:123}};assert.throws(()=>extractResumeInputs(ambiguous,config),/identity/);
 ambiguous.status.league=-1649480587;assert.equal(extractResumeInputs(ambiguous,config).league,'2645486709');
});
