import {hash} from './story_authors.mjs';
const valid=n=>Number.isInteger(n)&&n>=1&&n<=4500;
export function recruitRankDetail(f,key,{excludeNational=false}={}){
 const candidates=[];
 if(valid(f.stateRecruitRank)&&f.recruitState&&f.recruitState!=='Invalid_')candidates.push(` Ranked No. ${f.stateRecruitRank} in ${String(f.recruitState).replace(/([a-z])([A-Z])/g,'$1 $2')}.`);
 if(valid(f.positionRecruitRank)&&f.position)candidates.push(` Ranked No. ${f.positionRecruitRank} nationally at ${f.position}.`);
 if(!excludeNational&&valid(f.nationalRecruitRank))candidates.push(` No. ${f.nationalRecruitRank} nationally in this recruiting class.`);
 return candidates.length?candidates[hash(key+'|recruit-ranking')%candidates.length]:'';
}
