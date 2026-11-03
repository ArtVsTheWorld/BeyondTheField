import {verifiedTeamRows,relativeVerdict,schemes,nilAllocation,money} from './football_context.mjs';
import {nationalCoverage} from './national_editorial.mjs';
import {hash} from './story_authors.mjs';
const one=n=>n.toFixed(1),two=n=>n.toFixed(2),pct=n=>one(n*100);
const known=(...values)=>values.every(Number.isFinite);
const comparisons={offense:'Yards per play',passing:'Yards per pass attempt',rushing:'Yards per carry',defense:'Yards allowed per play','pass-defense':'Yards allowed per pass attempt','run-defense':'Yards allowed per carry',disruption:'Takeaways per game',penalties:'Penalty yards per game','ball-security':'Giveaways per game'};
export function contextualAnalytics(s,{bounded=true}={}){
 if(s.reconstructed||s.season.CurrentStage!=='NFLSeason')return [];
 const rows=[...verifiedTeamRows(s).values()].filter(r=>r.n>=3),covered=nationalCoverage(s),events=[];
 const grade=(value,field,higher=true,poor=null,strong=null)=>relativeVerdict(value,rows.map(field),{higher,poor,strong});
 for(const r of rows){const t=r.team,candidates=[],off=schemes[t.offensiveScheme]??'offensive',def=schemes[t.defensiveScheme]??'defensive';
 const add=(key,values,g={verdict:'neutral',band:'unclassified',population:rows.length},priority=85)=>candidates.push({id:`context:${t.id}:${key}`,category:'analytics',facts:{family:'context.'+key,voice:'analyst',school:t.name,games:r.n,offense:off,defense:def,verdict:g.verdict,negative:g.verdict==='negative',comparison:g.band==='unclassified'?`A ${r.n}-game sample so far.`:`${comparisons[key]??'This measure'} puts them in the ${g.band} of ${g.population} comparable teams${g.verdict==='negative'?'; that needs to improve':g.verdict==='positive'?'; one of their strengths':''}.`,...values},options:{team:t.id,national:covered.has(t.id),priority,thread:'context:'+t.id+':'+key}});
  if(known(r.ypg,r.ypp))add('offense',{ppg:one(r.ppg),ypg:one(r.ypg),ypp:two(r.ypp)},grade(r.ypp,x=>x.ypp,true,4.8,6.2));
  const int=r.read('PASSINTS'),lost=r.read('FUMBLESLOST'),give=r.read('GIVEAWAYS'),pass=r.read('PASSATTEMPTS');
  if(known(r.passYPG,r.passYPA,r.passTDpg,int,r.passShare)&&pass>=80)add('passing',{ypg:one(r.passYPG),ypa:two(r.passYPA),tdpg:two(r.passTDpg),intpg:two(int/r.n),share:pct(r.passShare)},grade(r.passYPA,x=>x.passYPA,true,6,8));
  if(known(r.rushYPG,r.rushYPC,r.rushTDpg,r.passShare))add('rushing',{ypg:one(r.rushYPG),ypc:two(r.rushYPC),tdpg:two(r.rushTDpg),share:pct(1-r.passShare)},grade(r.rushYPC,x=>x.rushYPC,true,3.5,5));
  if(known(r.ypga,r.yppa))add('defense',{ppga:one(r.ppga),ypga:one(r.ypga),yppa:two(r.yppa)},grade(r.yppa,x=>x.yppa,false,6.2,5.2));
  const oppPass=r.read('PASSATTEMPTS',true),oppRush=r.read('RUSHATTEMPTS',true),dp=r.read('DEFPASSYARDS'),dr=r.read('DEFRUSHYARDS'),ints=r.read('DEFINTS'),fr=r.read('FUMBLEREC'),take=r.read('TAKEAWAYS'),sacks=r.read('SACKS');
  if(known(dp,oppPass,ints)&&oppPass>=80)add('pass-defense',{ypga:one(dp/r.n),ypa:two(dp/oppPass),intpg:two(ints/r.n)},grade(dp/oppPass,x=>{const a=x.read('PASSATTEMPTS',true),y=x.read('DEFPASSYARDS');return a>0&&y!==null?y/a:null;},false,8.5,6.5));
  if(known(dr,oppRush)&&oppRush>=80)add('run-defense',{ypga:one(dr/r.n),ypc:two(dr/oppRush)},grade(dr/oppRush,x=>{const a=x.read('RUSHATTEMPTS',true),y=x.read('DEFRUSHYARDS');return a>0&&y!==null?y/a:null;},false,5.5,4));
  if(known(ints,fr,take,sacks)&&take===ints+fr)add('disruption',{sackpg:two(sacks/r.n),intpg:two(ints/r.n),frpg:two(fr/r.n),takepg:two(take/r.n)},grade(take/r.n,x=>x.read('TAKEAWAYS')!==null?x.read('TAKEAWAYS')/x.n:null,true,.6,1.5));
  const flags=r.read('PENALTIES'),yards=r.read('PENALTYYARDS');if(known(flags,yards)&&flags>=0&&yards>=0)add('penalties',{penalties:two(flags/r.n),yards:one(yards/r.n)},grade(yards/r.n,x=>x.read('PENALTYYARDS')!==null?x.read('PENALTYYARDS')/x.n:null,false,70,45));
  if(known(int,lost,give,pass)&&pass>=80&&give===int+lost&&int<=pass)add('ball-security',{intpg:two(int/r.n),lostpg:two(lost/r.n),givepg:two(give/r.n),rate:pct(int/pass)},grade(give/r.n,x=>x.read('GIVEAWAYS')!==null?x.read('GIVEAWAYS')/x.n:null,false,2,1.2));
  const allocation=nilAllocation(s,t.id);
  if(allocation?.total>0&&allocation.groups.length>=2){const [a,b]=allocation.groups;add('nil',{total:money(allocation.total),first:a.group,firstMoney:money(a.dollars),firstShare:pct(a.share),second:b.group,secondMoney:money(b.dollars),secondShare:pct(b.share)},undefined,84);}
  if(!bounded)events.push(...candidates);else events.push(...candidates.sort((a,b)=>hash(a.id+'|'+s.season.CurrentWeek)-hash(b.id+'|'+s.season.CurrentWeek)||a.id.localeCompare(b.id)).slice(0,6));
 }
 for(const t of s.teams.filter(t=>t.id!==255)){
  const c=t.headCoach,st=c?.careerStats;if(!c||!st)continue;
  const n=st.Wins+st.Losses;if(known(st.Wins,st.Losses)&&n>=20){
   const rate=st.Wins/n,g=relativeVerdict(rate,s.teams.map(t=>{const a=t.headCoach?.careerStats;return a&&a.Wins+a.Losses>=20?a.Wins/(a.Wins+a.Losses):null;}),{poor:.35,strong:.65});
   events.push({id:'coach-context:'+c.id,category:'analytics',facts:{family:'context.coach-record',voice:'analyst',school:t.name,coachName:c.name,wins:st.Wins,losses:st.Losses,rate:pct(rate),schoolWins:st.WinsAtCurrentSchool,schoolLosses:st.LossesAtCurrentSchool,verdict:g.verdict,negative:g.verdict==='negative'},options:{team:t.id,national:covered.has(t.id),priority:84}});
  }
  const specs=[['ranked','Top25Wins','Top25Losses',6],['rivalries','RivalWins','RivalLosses',4],['bowls','BowlWins','BowlLosses',3],['playoffs','PlayoffWins','PlayoffLosses',3]];
  const options=specs.filter(([,w,l,min])=>known(st[w],st[l])&&st[w]+st[l]>=min);if(!options.length)continue;
  const [label,w,l]=options[hash(c.id+'|coach-context|'+s.season.CurrentWeek)%options.length],rate=st[w]/(st[w]+st[l]);
  events.push({id:'coach-split:'+c.id,category:'analytics',facts:{family:'context.coach-'+label,voice:'analyst',school:t.name,coachName:c.name,wins:st[w],losses:st[l],rate:pct(rate),verdict:rate>=.7?'positive':rate<=.3?'negative':'neutral',negative:rate<=.3},options:{team:t.id,national:covered.has(t.id),priority:85}});
 }
 return events;
}
