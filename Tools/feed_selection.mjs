export const SCOPES=['all','national','conference','team'];
const order=(a,b)=>b.priority-a.priority||a.id.localeCompare(b.id);

// Assign each selected story to one mix bucket, even when it qualifies for
// several dedicated views. No duplicates and no fabricated filler for quotas.
export function curate(stories,limit=20){
  const pool=stories.filter(p=>p.curated!==false).sort(order),buckets={national:[],conference:[],team:[]};
  const bucketFor=p=>p.primaryScope&&p.scopes.includes(p.primaryScope)?p.primaryScope:p.scopes.includes('team')?'team':p.scopes.includes('conference')?'conference':'national';
  for(const p of pool)buckets[bucketFor(p)].push(p);
  const target={national:Math.round(limit*.35),conference:Math.round(limit*.25),team:0};target.team=limit-target.national-target.conference;
  const selected=[],used=new Set(),categories=new Map(),threads=new Map();
  const categoryMax={'results':4,'team-stats':1,'player-stats':3,'polls':3,'injuries':2,'recruiting':2,'offers':1,'heisman':2,'cfp':1,'standings':1,'schedule':3,'watch':1,'lines':1,'holiday':1,'status':1};
  const accept=p=>{
    if(used.has(p.id)||(categories.get(p.category)??0)>=(categoryMax[p.category]??2))return false;
    // Keep an event from taking over the combined feed with many near-identical
    // player box scores or commitments. Dedicated scope lists keep them all.
    const thread=p.thread??p.id;
    if((threads.get(thread)??0)>=2)return false;
    used.add(p.id);categories.set(p.category,(categories.get(p.category)??0)+1);threads.set(thread,(threads.get(thread)??0)+1);selected.push(p);return true;
  };
  const counts={national:0,conference:0,team:0};
  for(const scope of ['team','conference','national'])for(const p of buckets[scope]){if(counts[scope]>=target[scope])break;if(accept(p))++counts[scope];}
  for(const p of pool){if(selected.length>=limit)break;accept(p);}
  // Interleave the buckets instead of placing every team story in one block.
  const remaining=[...selected].sort(order),result=[],pattern=['team','national','conference','team','national','conference','team','national','team','national'];
  while(remaining.length){const wanted=pattern[result.length%pattern.length];let i=remaining.findIndex(p=>bucketFor(p)===wanted);if(i<0)i=0;result.push(remaining.splice(i,1)[0]);}
  return result;
}

export function scopeViews(stories){
  const sorted=[...stories].sort(order),all=curate(sorted);
  return {all:all.map(p=>p.id),national:sorted.filter(p=>p.scopes.includes('national')).map(p=>p.id),
    conference:sorted.filter(p=>p.scopes.includes('conference')).map(p=>p.id),team:sorted.filter(p=>p.scopes.includes('team')).map(p=>p.id)};
}

export function publishWeek(feed){
  const publication={key:feed.key,season:feed.season,phase:feed.phase,week:feed.week};
  const stories=feed.stories.map(p=>({...p,publication}));
  const views=scopeViews(stories),map=new Map(stories.map(p=>[p.id,p]));
  return {...feed,stories,views,posts:views.all.map(id=>map.get(id)),publication};
}

export function buildCatalog(active,history=[]){
  const byWeek=new Map();
  for(const f of [...history,active]){
    if(f.engineVersion!==2||f.leagueId!==active.leagueId||f.userTeamIndex!==active.userTeamIndex||f.season!==active.season||f.phase!==active.phase||f.week>active.week)continue;
    if(!f.publication||f.publication.key!==f.key||f.publication.week!==f.week)throw Error('Invalid publication-week archive');
    const old=byWeek.get(f.key);if(!old||f===active||(f.sourceModifiedMs??0)>(old.sourceModifiedMs??0))byWeek.set(f.key,f);
  }
  const weeks=[...byWeek.values()].sort((a,b)=>a.week-b.week);
  return {...active,catalogVersion:1,activeWeekKey:active.key,weeks};
}
