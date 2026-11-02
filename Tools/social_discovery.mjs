// Scope identity comes from native records; labels and memberships can change.
const alphabetical=(a,b)=>a.label.localeCompare(b.label,'en',{sensitivity:'base'})||a.key.localeCompare(b.key);
export function scopeCatalog(s){
 const teams=[...new Map(s.teams.filter(t=>t.id!==255&&t.name).map(t=>[t.id,t])).values()];
 const conferences=(s.conferences??[]).filter(c=>c.name&&c.teams.some(id=>teams.some(t=>t.id===id))).map(c=>({key:'conference:'+c.id,label:c.name,kind:'conference',teamIds:[...new Set(c.teams.filter(id=>id!==255))]})).sort(alphabetical);
 return [{key:'all',label:'For You',kind:'personalized'},{key:'national',label:'National',kind:'national'},...conferences,...teams.map(t=>({key:'team:'+t.id,label:t.name,kind:'team',teamIds:[t.id]})).sort(alphabetical)];
}
export function discoveryViews(stories,options){
 // stories already use parent-first conversation order; children inherit the root scope.
 return Object.fromEntries(options.filter(o=>o.teamIds).map(o=>[o.key,stories.filter(p=>p.teamIds?.some(id=>o.teamIds.includes(id))).map(p=>p.id)]));
}
export const CATEGORY_FILTERS=[
 {key:'all',label:'All Types'},
 {key:'recruiting',label:'Recruiting',categories:['recruiting','offers']},
 {key:'recaps',label:'Recaps',categories:['results','team-stats','player-stats']},
 {key:'upcoming',label:'Upcoming',categories:['schedule','watch','lines']},
 {key:'rankings',label:'Rankings & Awards',categories:['polls','heisman','cfp','awards']},
 {key:'analyst',label:'Analysts',voices:['analyst','model']},
 {key:'beat',label:'Beat Reporters',voices:['beat']},
 {key:'official',label:'Team Accounts',voices:['official']},
 {key:'player',label:'Players & Recruits',voices:['player','recruit']},
 {key:'fan',label:'Fans',voices:['fan']}
];
export function filterConversations(stories,key='all'){
 const f=CATEGORY_FILTERS.find(x=>x.key===key);if(!f)throw Error('Unknown category filter');
 const accepted=new Set(),result=[];
 for(const p of stories){if(p.replyTo?accepted.has(p.replyTo):key==='all'||f.categories?.includes(p.category)||f.voices?.includes(p.voice)){accepted.add(p.id);result.push(p);}}
 return result;
}
