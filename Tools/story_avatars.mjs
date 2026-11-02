import fs from 'node:fs';
const bank=JSON.parse(fs.readFileSync(new URL('../Content/Runtime/portrait-ranges.json',import.meta.url),'utf8'));
export function avatarFor(role,team,player){
 const personal=['player','recruit'].includes(role),id=player?.portrait;
 if(personal&&!player?.portraitForcedSilhouette&&Number.isInteger(id)&&id>0&&bank.ranges.some(([lo,hi])=>id>=lo&&id<=hi))return {imageLibrary:bank.libraryId,imageValue:id};
 if(Number.isInteger(team?.logo)&&team.logo>=0&&['player','recruit','beat','official','fan'].includes(role))return {imageLibrary:0,imageValue:team.logo};
 return {imageLibrary:79,imageValue:598};
}
