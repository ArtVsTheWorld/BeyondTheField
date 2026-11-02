// Persistent fictional account identities. Position and publication week never seed handles.
export function hash(text){let h=2166136261;for(const c of text){h^=c.codePointAt(0);h=Math.imul(h,16777619);}return h>>>0;}
const clean=x=>String(x??'').normalize('NFKD').replace(/[^A-Za-z0-9]/g,'');
const firstNames=['Maya','Jordan','Cameron','Alex','Riley','Morgan','Taylor','Casey'];
const surnames=['Wells','Bennett','Reed','Lawson','Brooks','Ellis','Grant','Hayes','Cole','Parker','Miles','West','Lane','Stone','Ford','Davis'];
export function authorRegistry(saved={}){
 const entries=structuredClone(saved),handles=new Map(Object.entries(entries).map(([k,v])=>[v.handle.toLowerCase(),k]));
 return {entries,get(s,role,team,player,persona=0){
  const person=['player','recruit'].includes(role),family=person?'person':role;
  const key=`${s.leagueId}:${family}:${person?player.id:['analyst','model'].includes(role)?'national':team?.id??'national'}${!person&&persona?':'+persona:''}`;
  if(entries[key]){if(person)entries[key].author=player.name;return entries[key];}
  const seed=hash(key),school=team?.name??'College Football',slug=clean(school).slice(0,13)||'College';let author,base;
  if(person){const pieces=player.name.trim().split(/\s+/),first=clean(pieces[0])||'Player',last=clean(pieces.slice(1).join(''))||first,num=player.team!==255&&Number.isInteger(player.jerseyNumber)?player.jerseyNumber:1+seed%99;
   base=[first+last,first+'_'+last,first+'.'+last,first[0].toLowerCase()+last.toLowerCase()+num,first+last+num,last.toLowerCase()+num+'_','the'+first.toLowerCase()+last.toLowerCase()][seed%7];author=player.name;
  }else if(role==='official'){author=school+' Football';base=slug+'Football';}
  else if(role==='beat'){const first=firstNames[seed%firstNames.length],last=surnames[Math.floor(seed/firstNames.length)%surnames.length];author=first+' '+last;base=first+last+'On'+slug.slice(0,9);}
  else if(role==='fan'){author=school+(persona?' Sideline':' After Dark');base=slug+(persona?'Sideline':'AfterDark');}
  else if(role==='model'){author='Saturday Model Lines';base='SaturdayModelCFB';}
  else if(persona===1){author='Situational Football';base='SituationalCFB';}
  else if(persona===2){author='Field Position';base='FieldPositionCFB';}
  else{author='Saturday Perspective';base='SaturdayViewCFB';}
  base=base.slice(0,28);let handle='@'+base;
  if(handles.has(handle.toLowerCase())&&handles.get(handle.toLowerCase())!==key){let n=0;do{handle='@'+base.slice(0,23)+(10+hash(key+':'+n++)%90);}while(handles.has(handle.toLowerCase()));}
  const profile={author,handle,styleSeed:seed,faithLanguage:person&&hash(key+':faith')%5===0};entries[key]=profile;handles.set(handle.toLowerCase(),key);return profile;
 }};
}
