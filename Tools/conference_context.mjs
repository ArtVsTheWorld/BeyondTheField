import {finalGame,visibleGame} from './football_context.mjs';
import {publicPoll,completePoll} from './public_polls.mjs';
import {postseasonTiming} from './postseason_timing.mjs';
import {hash} from './story_authors.mjs';
const grades=['F','DMinus','D','DPlus','CMinus','C','CPlus','BMinus','B','BPlus','AMinus','A','APlus'];
const index=g=>grades.findIndex(x=>x.toLowerCase()===String(g??'').replaceAll('+','Plus').replaceAll('-','Minus').toLowerCase());
export function conferencePrestige(s){
 const teams=new Map(s.teams.filter(t=>t.id!==255).map(t=>[t.id,t]));
 return (s.conferences??[]).filter(c=>!c.independent&&c.teams.length>=4).flatMap(c=>{
  const values=c.teams.map(id=>index(teams.get(id)?.conferencePrestigeGrade));if(values.some(n=>n<0))return [];
  const counts=new Map();for(const n of values)counts.set(n,(counts.get(n)??0)+1);
  const [grade,n]=[...counts].sort((a,b)=>b[1]-a[1]||b[0]-a[0])[0];
  // This team attribute is normally shared by conference members. Don't turn
  // conflicting/partly stale member grades into an invented conference grade.
  if(n/values.length<.8)return [];
  return [{...c,grade,gradeLabel:grades[grade]}];
 }).sort((a,b)=>b.grade-a.grade||a.name.localeCompare(b.name));
}
export function conferenceDiscourse(s){
 if(s.reconstructed||s.season.CurrentStage!=='NFLSeason')return [];
 const all=conferencePrestige(s);if(all.length<2||all[0].grade<6)return [];
 const leading=all.filter(c=>c.grade>=Math.max(6,all[Math.min(2,all.length-1)].grade)).sort((a,b)=>b.grade-a.grade||hash(a.id+'|'+s.season.CurrentWeek)-hash(b.id+'|'+s.season.CurrentWeek)).slice(0,3);
 if(leading.length<2)return [];
 const teams=new Map(s.teams.filter(t=>t.id!==255).map(t=>[t.id,t])),poll=publicPoll(s),knownPoll=completePoll(s.teams,poll.field),timing=postseasonTiming(s),games=s.games.filter(g=>visibleGame(s,g)),events=[];
 const playoffTeams=new Set(timing.locked?(s.playoffBracket??[]).filter(g=>g.year===s.season.CurrentYear).flatMap(g=>[g.home,g.away]).filter(id=>teams.has(id)):[]);
 const representative=c=>c.teams.map(id=>teams.get(id)).filter(Boolean).sort((a,b)=>(poll.ranks[a.id]>=1&&poll.ranks[a.id]<=25?poll.ranks[a.id]:99)-(poll.ranks[b.id]>=1&&poll.ranks[b.id]<=25?poll.ranks[b.id]:99)||b.wins-a.wins||a.losses-b.losses||a.id-b.id)[0];
 for(let i=0;i<leading.length;i++){
  const c=leading[i],other=leading[(i+1)%leading.length],t=representative(c),rival=representative(other);if(!t||!rival)continue;
  const members=new Set(c.teams),inter=games.filter(g=>members.has(g.home)!==members.has(g.away)&&teams.get(g.home)?.conferenceId&&teams.get(g.away)?.conferenceId&&teams.get(g.home).conferenceId!==teams.get(g.away).conferenceId);
  const win=g=>members.has(g.home)?g.homeScore>g.awayScore:g.awayScore>g.homeScore,loss=g=>members.has(g.home)?g.homeScore<g.awayScore:g.awayScore<g.homeScore;
  const post=inter.filter(g=>g.phase!=='RegularSeason'),ranked=knownPoll?c.teams.filter(id=>poll.ranks[id]>=1&&poll.ranks[id]<=25).length:null,selected=c.teams.filter(id=>playoffTeams.has(id)).length;
  const facts={conference:c.name,otherConference:other.name,school:t.name,opponent:rival.name};
  const options={team:t.id,relatedTeams:[rival.id],national:true,priority:87,thread:'conference-talk:'+c.id};
  if(inter.length>=8){const w=inter.filter(win).length,l=inter.filter(loss).length;
   const details=[`${w}\u2013${l} against other conferences`,...(ranked!==null?[`${ranked} teams in the current ${poll.name} Top 25`]:[]),...(timing.locked?[`${selected} playoff selections`]:[]),...(post.length?[`${post.filter(win).length}\u2013${post.filter(loss).length} in interconference postseason games`]:[])].join('; ');
   events.push({id:'conference-context:'+c.id,category:'conference-talk',facts:{...facts,family:'context.conference',voice:'analyst',details,verdict:'neutral'},options});
  }
  events.push({id:'conference-fan:'+c.id,category:'conference-talk',facts:{...facts,family:'context.conference-fan',voice:'fan',persona:hash(c.id+'|fan-tone')%2,rivalReplyTeam:rival.id},options:{...options,national:false,priority:86}});
 }
 return events;
}
