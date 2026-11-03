import {publishWeek} from './feed_selection.mjs';
import {correctHeismanArchive} from './heisman_context.mjs';
import {correctWaitingArchive} from './correct_waiting_archive.mjs';
import {cleanFeedLanguage} from './clean_language.mjs';
// Requested account presentation changes do not regenerate archived event prose.
import {avatarFor} from './story_avatars.mjs';
const analysts=[['ESPNCFB','ESPNCFB'],['Jake Whitmore','JakeWhitmoreCFB'],['Marcus Bennett','MBennettSports'],['Tina Brooks','TinaBrooksCFB'],['David Ellison','DavidEllisonFB'],['Chris Maddox','ChrisMaddoxCFB']];
export function refreshAccountPresentation(feed,s){
 feed=correctHeismanArchive(correctWaitingArchive(cleanFeedLanguage(feed),s),s);
 if(feed.editorialVersion!==1&&feed.stories.every(p=>Array.isArray(p.scopes)))feed=publishWeek(feed);
 // Expand archived browsing/guaranteed draft visibility without regenerating
 // the wording, engagement or publication dates of existing stories.
 if(!feed.views?.['all:expanded']&&feed.stories.every(p=>Array.isArray(p.scopes)))feed=publishWeek(feed);
 if(feed.presentationVersion===3)return feed;
 const players=new Map(s.players.map(p=>[p.id,p])),teams=new Map(s.teams.map(t=>[t.id,t]));
 const stories=feed.stories.map(original=>{
  const p={...original,body:original.body.replaceAll('@FanDuelSports','@CanDuelSports')};let team=teams.get(p.teamIds?.[0]),person=players.get(p.playerId),persona=0;
  if(['player','recruit'].includes(p.voice)){
   if(!person)return p;
   if(p.voice==='player'&&!p.teamIds?.includes(person.team))return p;
   team=teams.get(person.team)??team;
   if(p.voice==='recruit')p.author=person.name+(person.position?' | '+person.position:'');
   if(p.voice==='player')for(const subject of s.players){if(subject.id===person.id||subject.team!==person.team||subject.name===subject.firstName)continue;const first=subject.firstName||subject.name.trim().split(/\s+/)[0];if(subject.name.includes(' '))p.body=p.body.replaceAll(subject.name,(match,offset,source)=>/[\p{L}\p{N}_]/u.test(source[offset-1]??'')||/[\p{L}\p{N}_]/u.test(source[offset+match.length]??'')?match:first);}
   return p;
  }else if(p.voice==='fan'){
   const match=s.teams.find(t=>[t.name+' After Dark',t.name+' Sideline','Barstool '+t.name].includes(p.author));if(!match)return p;team=match;persona=p.author===team.name+' After Dark'?0:1;
  }else if(p.voice==='analyst'){
   persona=analysts.findIndex(([name])=>name===p.author);if(persona<0)persona=({'Saturday Perspective':0,'Situational Football':1,'Field Position':2})[p.author]??-1;if(persona<0)return p;
  }else if(p.voice==='model'){p.author='CanDuel Sports';p.handle='@CanDuelSports';}
  else if(p.voice!=='beat'&&p.voice!=='official'&&p.voice!=='cfp')return p;
  Object.assign(p,avatarFor(p.voice,team,person,persona));return p;
 });
 const map=new Map(stories.map(p=>[p.id,p]));return {...feed,presentationVersion:3,stories,posts:(feed.views?.all??feed.posts?.map(p=>p.id)??[]).map(id=>map.get(id)).filter(Boolean)};
}
