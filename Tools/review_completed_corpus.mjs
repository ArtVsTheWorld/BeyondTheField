// Read-only review of published editions. This does not claim to reconstruct
// every unobserved candidate or regenerate missing historical raw snapshots.
import fs from 'node:fs/promises';
import path from 'node:path';
import {readHistory} from './runtime_archive.mjs';
import {comparePublication} from './publication_timeline.mjs';
import {contentPack} from './story_templates.mjs';
const [root,yearArg,output]=process.argv.slice(2),year=Number(yearArg);
if(!root||!Number.isInteger(year)||!output)throw Error('Usage: review_completed_corpus.mjs frozen-runtime-folder YEAR output.json');
const folders=new Set();
async function walk(dir){for(const file of await fs.readdir(dir,{withFileTypes:true})){const p=path.join(dir,file.name);if(file.isDirectory()&&file.name!=='.history-data')await walk(p);else if(file.name==='history.json'||file.name==='history.index.json')folders.add(dir);}}
await walk(path.join(root,'RuntimeHistory'));
const editions=[];
for(const folder of folders){const history=await readHistory(path.join(folder,'history.json'),{archiveOnly:true});for(const e of history?.editions??[])if(e.feed?.leagueId===831346515&&e.feed.season===year)editions.push(e.feed);}
editions.sort(comparePublication);
const count=(list,key)=>Object.entries(Object.groupBy(list,key)).map(([key,items])=>({key,count:items.length})).sort((a,b)=>b.count-a.count||a.key.localeCompare(b.key));
const repeated=[],lowercase=[],redundant=[],leaks=[],draftIssues=[],nilZeros=[],rows=[],nationalEmpty=[],templateUse=new Map();
for(const feed of editions){
 const stories=feed.stories??[],lookup=new Map(stories.map(p=>[p.id,p])),byEvent=new Map((feed.events??[]).map(e=>[e.id,e]));
 const week={key:feed.key,stories:stories.length,forYou:feed.posts?.length??0,national:feed.views?.national?.length??0,team:feed.views?.['team:63']?.length??0,voices:count(stories,p=>p.voice),categories:count(stories,p=>p.category)};rows.push(week);
 if(!week.national)nationalEmpty.push(feed.key);
 for(const p of stories){
  const example={week:feed.key,id:p.id,template:p.templateId,body:p.body};
  if(p.templateId)templateUse.set(p.templateId,(templateUse.get(p.templateId)??0)+1);
  if(/^[\s"'“‘]*[a-z]/u.test(p.body))lowercase.push(example);
  if(/\b(QB|RB|HB|WR|TE|DE|DT|CB|S|LB|OL|OT|OG|C|K|P)\s+.{2,45},?\s+(?:a|an)\s+\1\b/u.test(p.body))redundant.push(example);
  if(p.category==='nil'&&/\$0(?![\d.])/u.test(p.body))nilZeros.push(example);
 }
 for(const group of Object.values(Object.groupBy(stories,p=>p.body.trim().toLowerCase()))){if(group.length>1)repeated.push({week:feed.key,count:group.length,body:group[0].body,templates:[...new Set(group.map(p=>p.templateId))]});}
 for(const id of feed.views?.['team:63']??[]){const p=lookup.get(id);if(!p)continue;const e=byEvent.get(p.eventId);if(p.primaryScope==='conference'||e?.primaryScope==='conference'||!p.teamIds?.includes(63))leaks.push({week:feed.key,id,category:p.category,body:p.body,teamIds:p.teamIds});}
 const early=(feed.events??[]).filter(e=>e.category==='draft'&&e.facts?.draftRound<=2&&['QB'].includes(e.facts.position));
 for(const [club,group] of Object.entries(Object.groupBy(early,e=>e.facts.nflTeam)))if(group.length>1)draftIssues.push({week:feed.key,nflTeam:club,picks:group.map(e=>({player:e.facts.playerName,round:e.facts.draftRound,pick:e.facts.draftPick}))});
}
const families=Object.entries(contentPack.families).map(([family,variants])=>({family,count:variants.length,uniqueBodies:new Set(variants.map(v=>v.body)).size}));
const report={mode:'Complete published-edition review; historical raw captures unavailable for some editions',year,editions:editions.length,stories:rows.reduce((n,r)=>n+r.stories,0),nationalEmpty,rows,templateCoverage:{families:families.length,variants:families.reduce((n,f)=>n+f.count,0),minimum:Math.min(...families.map(f=>f.count)),belowEight:families.filter(f=>f.uniqueBodies<8)},findings:{exactSameWeekDuplicateGroups:repeated.length,lowercaseStarts:lowercase.length,redundantPositions:redundant.length,nilToZeroPosts:nilZeros.length,broadConferenceInTeamView:leaks.length,earlyDuplicateQbDestinations:draftIssues.length},examples:{duplicates:repeated.slice(0,30),lowercase:lowercase.slice(0,30),redundant:redundant.slice(0,30),nilZeros:nilZeros.slice(0,20),leaks:leaks.slice(0,25),draftIssues},mostUsedTemplates:[...templateUse].sort((a,b)=>b[1]-a[1]).slice(0,30)};
await fs.writeFile(output,JSON.stringify(report,null,2));console.log(JSON.stringify({editions:report.editions,stories:report.stories,nationalEmpty,templateCoverage:{families:families.length,variants:report.templateCoverage.variants,belowEight:report.templateCoverage.belowEight.length},findings:report.findings}));
