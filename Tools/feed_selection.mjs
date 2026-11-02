import {discoveryViews} from './social_discovery.mjs';
import {visibleEdition,comparePublication} from './publication_timeline.mjs';
export const SCOPES=['all','national','conference','team'];
const order=(a,b)=>b.priority-a.priority||a.id.localeCompare(b.id);
const byLikes=(a,b)=>Math.max(0,b.likes??0)-Math.max(0,a.likes??0)||(a.id<b.id?-1:a.id>b.id?1:0);
const bucketFor=p=>p.primaryScope&&p.scopes.includes(p.primaryScope)?p.primaryScope:(p.scopes.includes('team')||p.scopes.includes('relevant'))?'team':p.scopes.includes('conference')?'conference':'national';
// Order a real conversation with its parent immediately before the replies.
// Orphans and cycles never become visible, including in dedicated scope views.
export function conversationOrder(stories){
 const map=new Map(stories.map(p=>[p.id,p])),children=new Map(),roots=[],result=[],visited=new Set();
 for(const p of stories){if(!p.replyTo)roots.push(p);else if(map.has(p.replyTo)){const a=children.get(p.replyTo)??[];a.push(p);children.set(p.replyTo,a);}}
 function visit(p){if(visited.has(p.id))return;visited.add(p.id);result.push(p);for(const child of (children.get(p.id)??[]).sort(byLikes))visit(child);}
 for(const p of roots.sort(byLikes))visit(p);return result;
}
export function curate(stories,limit=30){
 const pool=stories.filter(p=>p.curated!==false&&p.scopes.length).sort(order),map=new Map(pool.map(p=>[p.id,p]));
 const target={national:Math.round(limit*.35),conference:Math.floor(limit*.25),team:0};target.team=limit-target.national-target.conference;
 const selected=[],used=new Set(),counts={national:0,conference:0,team:0},categories=new Map(),threads=new Map(),templates=new Map(),accounts=new Map(),voices=new Map();
 const categoryMax={'results':4,'team-stats':1,'player-stats':3,'polls':3,'injuries':2,'recruiting':2,'offers':1,'heisman':2,'cfp':1,'standings':1,'schedule':3,'watch':1,'lines':1,'holiday':1,'status':1,'replies':5,'preseason':5};
 const voiceMax={beat:8,analyst:4,official:4,player:4,fan:5,recruit:3,model:1};
 const scaled=n=>Math.ceil(n*limit/20);
 function accept(post,respectTargets=false){
  const bundle=[],seen=new Set();let p=post;
  while(p&&!used.has(p.id)){if(seen.has(p.id)||p.curated===false)return false;seen.add(p.id);bundle.unshift(p);if(!p.replyTo)break;p=map.get(p.replyTo);if(!p)return false;}
  if(!bundle.length||selected.length+bundle.length>limit)return false;
  const c=new Map(categories),t=new Map(threads),v=new Map(voices),a=new Map(accounts),forms=new Map(templates),byScope={...counts};
  for(const item of bundle){
   const category=item.replyTo?'replies':item.category,thread=item.thread??item.id,scope=bucketFor(item),account=item.handle?.toLowerCase();
   const accountMax=['player','fan'].includes(item.voice)?2:3;
   if((c.get(category)??0)>=(category==='offers'?1:scaled(categoryMax[category]??2))||(t.get(thread)??0)>=2||item.templateId&&(forms.get(item.templateId)??0)>=2||account&&(a.get(account)??0)>=accountMax||item.voice&&(v.get(item.voice)??0)>=scaled(voiceMax[item.voice]??20))return false;
   c.set(category,(c.get(category)??0)+1);t.set(thread,(t.get(thread)??0)+1);if(item.templateId)forms.set(item.templateId,(forms.get(item.templateId)??0)+1);if(account)a.set(account,(a.get(account)??0)+1);if(item.voice)v.set(item.voice,(v.get(item.voice)??0)+1);++byScope[scope];
  }
  if(respectTargets&&Object.keys(target).some(k=>byScope[k]>target[k]))return false;
  for(const item of bundle){const category=item.replyTo?'replies':item.category,thread=item.thread??item.id,scope=bucketFor(item),account=item.handle?.toLowerCase();used.add(item.id);selected.push(item);++counts[scope];categories.set(category,c.get(category));threads.set(thread,t.get(thread));if(item.templateId)templates.set(item.templateId,forms.get(item.templateId));if(account)accounts.set(account,a.get(account));if(item.voice)voices.set(item.voice,v.get(item.voice));}return true;
 }
 // Keep the actual user result before reserving room for personality/reactions.
 for(const p of pool.filter(p=>!p.replyTo&&p.category==='results'&&!pool.some(x=>x.category==='upsets'&&x.thread===p.thread)&&p.scopes.includes('team')&&!['fan','player'].includes(p.voice)))accept(p,true);
 for(const voice of ['player','fan','recruit'])for(const p of voice==='recruit'?[...pool].sort((a,b)=>Number(b.scopes.includes('team')||b.scopes.includes('relevant'))-Number(a.scopes.includes('team')||a.scopes.includes('relevant'))||order(a,b)):pool){if((voices.get(voice)??0)>=(voice==='recruit'?1:2))break;if(p.voice===voice)accept(p,true);}
 for(const scope of ['team','conference','national'])for(const p of pool){if(counts[scope]>=target[scope])break;if(bucketFor(p)===scope)accept(p,true);}
 for(const p of pool){if(selected.length>=limit)break;accept(p);}
 // Editorial selection retains relevance/variety; presentation ranks threads by likes.
 return conversationOrder(selected);
}
export function scopeViews(stories){
 const visible=conversationOrder(stories),all=curate(visible);
 return {all:all.map(p=>p.id),national:conversationOrder(visible.filter(p=>p.scopes.includes('national'))).map(p=>p.id),conference:conversationOrder(visible.filter(p=>p.scopes.includes('conference'))).map(p=>p.id),team:conversationOrder(visible.filter(p=>p.scopes.includes('team'))).map(p=>p.id)};
}

export function publishWeek(feed){
  const publication={key:feed.key,season:feed.season,phase:feed.phase,week:feed.week};
  const stories=feed.stories.map(p=>({...p,publication}));
  const views={...scopeViews(stories),...(feed.scopeOptions?discoveryViews(conversationOrder(stories),feed.scopeOptions):{})},map=new Map(stories.map(p=>[p.id,p]));
  return {...feed,stories,views,posts:views.all.map(id=>map.get(id)),publication};
}

export function buildCatalog(active,history=[]){
  const byWeek=new Map();
  for(const f of [...history,active]){
    if(!visibleEdition(active,f))continue;
    if(!f.publication||f.publication.key!==f.key||f.publication.week!==f.week)throw Error('Invalid publication-week archive');
    const old=byWeek.get(f.key);if(!old||f===active||(f.sourceModifiedMs??0)>(old.sourceModifiedMs??0))byWeek.set(f.key,f);
  }
  const displayKeys=['id','author','handle','body','stamp','category','voice','replyTo','imageLibrary','imageValue','uniformTeamLogo','likes','publication'];
  const weeks=[...byWeek.values()].sort(comparePublication).map(f=>({...Object.fromEntries(['format','engineVersion','key','leagueId','userTeamIndex','season','phase','week','conference','publication'].map(k=>[k,f[k]])),events:f.events??[],stories:f.stories.map(p=>Object.fromEntries(displayKeys.filter(k=>p[k]!==undefined).map(k=>[k,p[k]]))),views:f.views}));
  return {...active,catalogVersion:2,activeWeekKey:active.key,weeks};
}
