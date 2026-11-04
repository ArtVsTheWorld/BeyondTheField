import {createHash} from 'node:crypto';
import {readFile,writeFile} from 'node:fs/promises';
import {pathToFileURL} from 'node:url';
export function resumeIdentity(league,p){
  if(!Number.isInteger(p.PresentationId)||p.PresentationId<=0)throw Error('No verified persistent prospect presentation identity');
  const birth=Number(p.PLYR_BIRTHDATE)>0?p.PLYR_BIRTHDATE:null;
  const parts=[String(Number(league)>>>0),p.PresentationId,p.FirstName,p.LastName,p.PLYR_HOME_TOWN,p.PLYR_HOME_STATE,birth];
  return createHash('sha256').update(JSON.stringify(parts)).digest('hex');
}
export function extractResumeInputs(raw,config){
  if(raw.sourceKind!=='runtime'||raw.format!==1||!raw.records)throw Error('Expected read-only native snapshot');
  const rows=Object.values(raw.records),franchises=rows.filter(r=>r.type==='Franchise'&&Number.isInteger(r.v.LeagueID));
  const franchise=Number.isInteger(raw.status?.league)?franchises.find(r=>(r.v.LeagueID>>>0)===(raw.status.league>>>0)):franchises.length===1?franchises[0]:null;
  const league=franchise?.v.LeagueID;
  if(!Number.isInteger(league)||!raw.status?.season)throw Error('Missing Dynasty identity');
  const ranks=new Map(config.rankedStates.map((s,i)=>[s,i+1]));
  const prospects=[];const seen=new Set();
  for(const r of rows){
    if(r.type!=='Recruit'||r.capacity<=1||r.v.Class!=='HighSchool')continue;
    const p=raw.records[r.v.Player]?.v;if(!p)throw Error('Missing recruit Player record');
    const id=resumeIdentity(league,p);if(seen.has(id))throw Error('Ambiguous persistent recruit identity');seen.add(id);
    const [table,row]=r.key.split(':').map(Number),state=config.aliases[p.PLYR_HOME_STATE]??p.PLYR_HOME_STATE;
    const ratings=Object.fromEntries(Object.entries(p).filter(([k,v])=>k.endsWith('Rating')&&Number.isInteger(v)&&v>=0&&v<=100));
    if(!ratings.OverallRating||!p.TraitDevelopment||!p.Position)throw Error('Incomplete underlying prospect data');
    prospects.push({identity:id,nativeRecruitId:table*131072+row,playerKey:r.v.Player,name:`${p.FirstName} ${p.LastName}`,position:p.Position,archetypeCode:p.PLYR_TENDENCY,state:p.PLYR_HOME_STATE,town:p.PLYR_HOME_TOWN,stateRank:ranks.get(state)??null,stars:({ONE_STAR:1,TWO_STAR:2,THREE_STAR:3,FOUR_STAR:4,FIVE_STAR:5})[p.ProspectStarRating]??null,development:p.TraitDevelopment,ratings,firstSeenSeason:raw.status.season.CurrentSeasonYear,previousSeasonYear:raw.status.season.CurrentSeasonYear-1,nativeProductionGrade:r.v.ProductionGrade,nativeQualityModifier:r.v.QualityModifier});
  }
  return {format:1,league:String(Number(league)>>>0),season:raw.status.season,prospects};
}
export function auditResumeInputs(data){
  const group=key=>Object.fromEntries([...new Set(data.prospects.map(p=>p[key]))].map(k=>[k,data.prospects.filter(p=>p[key]===k).length]));
  return {hsProspects:data.prospects.length,states:group('state'),development:group('development'),positions:group('position'),unmappedOrigins:data.prospects.filter(p=>p.stateRank===null).length,stars:Object.fromEntries([1,2,3,4,5].map(s=>{const p=data.prospects.filter(p=>p.stars===s);return [s,{count:p.length,overallRange:p.length?[Math.min(...p.map(p=>p.ratings.OverallRating)),Math.max(...p.map(p=>p.ratings.OverallRating))]:null}]})),identity:'Unsigned LeagueID + saved PresentationId + name + hometown/state + opaque birthdate when available; excludes save filename, week, ratings, stars, scouting, age and position'};
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href){
 const raw=JSON.parse(await readFile(process.argv[2],'utf8')),config=JSON.parse(await readFile(new URL('../Config/high-school-state-strength.json',import.meta.url),'utf8'));
 const data=extractResumeInputs(raw,config);await writeFile(process.argv[3],JSON.stringify(data));console.log(JSON.stringify(auditResumeInputs(data),null,2));
}
