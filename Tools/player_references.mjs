const esc=s=>s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
const positionWords={HB:'RB',RB:'RB',FB:'FB',QB:'QB',WR:'WR',TE:'TE',LT:'LT',LG:'LG',C:'C',RG:'RG',RT:'RT',LE:'DE',RE:'DE',LEDG:'EDGE',REDG:'EDGE',DT:'DT',LOLB:'LB',ROLB:'LB',MLB:'LB',SAM:'LB',MIKE:'LB',WILL:'LB',CB:'CB',FS:'S',SS:'S',K:'K',P:'P',LS:'LS'};
export const publicPosition=p=>positionWords[p]??p;
export function playerReferenceQualifier(players,{staffNames=[]}={}){
 const staff=new Set(staffNames);
 const names=new Map();for(const p of players)if(p.name?.trim()&&p.position){const list=names.get(p.name)??[];list.push(p);names.set(p.name,list);}
 const pattern=names.size?new RegExp('(?<![\\p{L}\\p{N}_@])('+[...names.keys()].sort((a,b)=>b.length-a.length||a.localeCompare(b)).map(esc).join('|')+')(?![\\p{L}\\p{N}_])','gu'):null;
 return (body,{playerId=null,teamIds=[],includePosition=true}={})=>pattern&&includePosition?body.replace(pattern,(name,_,offset)=>{
  const all=names.get(name);if(staff.has(name)&&!all.some(p=>p.id===playerId))return name;
  const preferred=all.find(p=>p.id===playerId)??(all.filter(p=>teamIds.includes(p.team)).length===1?all.find(p=>teamIds.includes(p.team)):null),positions=new Set(all.map(p=>publicPosition(p.position))),position=publicPosition(preferred?.position)??(positions.size===1?[...positions][0]:null);
  if(!position)return name;
  const before=body.slice(0,offset),after=body.slice(offset+name.length);
  if(/^\s*,?\s*(?:(?:a|an)\s+)?(?:QB|RB|HB|FB|WR|TE|LT|LG|C|RG|RT|OT|OG|OL|DE|LE|RE|LEDG|REDG|DT|EDGE|LB|MLB|OLB|SAM|MIKE|WILL|CB|FS|SS|S|DB|K|P|LS)\b/u.test(after))return name;
  if(/(?:^|[^\p{L}\p{N}'’])(?:QB|RB|HB|FB|WR|TE|LT|LG|C|RG|RT|OT|OG|OL|DE|LE|RE|LEDG|REDG|DT|EDGE|LB|MLB|OLB|SAM|MIKE|WILL|CB|FS|SS|S|DB|K|P|LS)\s+$/u.test(before)||/\b(?:quarterback|running back|receiver|wide receiver|tight end|cornerback|safety|linebacker|lineman|kicker|punter)\s+$/i.test(before)||new RegExp('^\\s*\\('+esc(position)+'\\)').test(after))return name;
  return position+' '+name;
 }):body;
}
