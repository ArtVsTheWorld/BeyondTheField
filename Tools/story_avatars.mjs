import fs from 'node:fs';
const bank=JSON.parse(fs.readFileSync(new URL('../Content/Runtime/portrait-ranges.json',import.meta.url),'utf8'));
const logoBank=JSON.parse(fs.readFileSync(new URL('../Content/Runtime/team-logo-variants.json',import.meta.url),'utf8')),logos=logoBank.logos;
const national=JSON.parse(fs.readFileSync(new URL('../Content/Runtime/national-account-avatars.json',import.meta.url),'utf8')).portraits;
export function avatarFor(role,team,player,persona=0){
 const personal=['player','recruit'].includes(role),id=player?.portrait;
 if(personal&&!player?.portraitForcedSilhouette&&Number.isInteger(id)&&id>0&&bank.ranges.some(([lo,hi])=>id>=lo&&id<=hi))return {imageLibrary:bank.libraryId,imageValue:id,...(role==='player'&&Number.isInteger(player.team)&&player.team!==255&&player.team===team?.id&&Number.isInteger(team.logo)?{uniformTeamLogo:team.logo}:{})};
 if(role==='nflDraft')return {imageLibrary:34,imageValue:21};
 if(role==='cfp')return {imageLibrary:34,imageValue:41};
 if(role==='analyst'&&national[persona]){const {imageLibrary,imageValue}=national[persona];return {imageLibrary,imageValue};}
 if(team?.isTeamBuilder&&['beat','fan'].includes(role)&&Number.isInteger(team.logo))return {imageLibrary:0,imageValue:team.logo};
 if(Number.isInteger(team?.logo)&&team.logo>=0){
  if(role==='official')return !team.isTeamBuilder&&logos[team.logo]?.onwhite||{imageLibrary:0,imageValue:team.logo};
  if(role==='beat')return !team.isTeamBuilder&&logos[team.logo]?.helmet||{imageLibrary:0,imageValue:team.logo};
  if(role==='fan'&&persona===0)return !team.isTeamBuilder&&logos[team.logo]?.mascot||{imageLibrary:0,imageValue:team.logo};
  if(role==='fan'&&persona===1)return !team.isTeamBuilder&&logos[team.logo]?.secondary||{imageLibrary:0,imageValue:team.logo};
 }
 return {imageLibrary:79,imageValue:({beat:939,analyst:598,model:1053,fan:203,player:974,recruit:974})[role]??598};
}
