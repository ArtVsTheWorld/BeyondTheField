import {finalGame} from './football_context.mjs';
import {completeOffensiveLine} from './heisman_context.mjs';
const count=n=>Number.isInteger(n)&&n>=0;
export function gameStory(s,g){
 if(!finalGame(g)||g.homeScore===g.awayScore)return null;
 const names=new Map(s.teams.map(t=>[t.id,t.name])),winner=g.homeScore>g.awayScore?g.home:g.away,loser=winner===g.home?g.away:g.home,w=(winner===g.home?g.homeName:g.awayName)??names.get(winner),l=(loser===g.home?g.homeName:g.awayName)??names.get(loser);if(!w||!l)return null;
 const a=winner===g.home?g.homeQuarterScores:g.awayQuarterScores,b=winner===g.home?g.awayQuarterScores:g.homeQuarterScores,wo=winner===g.home?g.homeOvertimePoints:g.awayOvertimePoints,lo=winner===g.home?g.awayOvertimePoints:g.homeOvertimePoints,ws=Math.max(g.homeScore,g.awayScore),ls=Math.min(g.homeScore,g.awayScore),sum=v=>v.reduce((n,x)=>n+x,0);
 let turningPoint=null,kind='box',quarterVerified=false;
 if(Array.isArray(a)&&Array.isArray(b)&&a.length===4&&b.length===4&&a.every(count)&&b.every(count)){
  const oa=count(wo)?wo:ws-sum(a),ob=count(lo)?lo:ls-sum(b);
  if(oa>=0&&ob>=0&&sum(a)+oa===ws&&sum(b)+ob===ls&&(oa===0&&ob===0||sum(a)===sum(b))){
   quarterVerified=true;const halfA=a[0]+a[1],halfB=b[0]+b[1],thirdA=halfA+a[2],thirdB=halfB+b[2];
   if(oa+ob>0){kind='overtime';turningPoint=`Regulation ended ${sum(a)}\u2013${sum(b)}; ${w} outscored ${l} ${oa}\u2013${ob} in overtime.`;}
   else if(thirdA<thirdB){kind='fourth-comeback';turningPoint=`${w} trailed ${thirdB}\u2013${thirdA} entering the fourth, then won that quarter ${a[3]}\u2013${b[3]}.`;}
   else if(halfA<halfB){kind='half-comeback';turningPoint=`${w} trailed ${halfB}\u2013${halfA} at halftime and outscored ${l} ${a[2]+a[3]}\u2013${b[2]+b[3]} after the break.`;}
   else if(thirdA-thirdB>=14&&ws-ls<=7&&b[3]>a[3]){kind='survived';turningPoint=`${w} led ${thirdA}\u2013${thirdB} after three; ${l}'s ${b[3]}\u2013${a[3]} fourth quarter made it close.`;}
   else if(b[2]+b[3]<=3&&halfA>halfB){kind='second-half-defense';turningPoint=`${w} led ${halfA}\u2013${halfB} at halftime and allowed ${b[2]+b[3]} points in the second half.`;}
   else if(a[3]-b[3]>=14&&thirdA-thirdB<=7){kind='pulled-away';turningPoint=`It was ${thirdA}\u2013${thirdB} after three. ${w} pulled away with a ${a[3]}\u2013${b[3]} fourth quarter.`;}
   else{kind='quarter-path';turningPoint=`${w} led ${halfA}\u2013${halfB} at halftime${thirdA>=thirdB?` and ${thirdA}\u2013${thirdB} after three`:''}. The second-half split was ${a[2]+a[3]}\u2013${b[2]+b[3]}.`;if(halfA===halfB)turningPoint=`Tied ${halfA}\u2013${halfB} at halftime, ${w} won the second half ${a[2]+a[3]}\u2013${b[2]+b[3]}.`;}
  }
 }
 const own=winner===g.home?g.homeStats:g.awayStats,other=winner===g.home?g.awayStats:g.homeStats;
 if(!turningPoint&&Number.isFinite(own?.OFFPASSYARDS)&&Number.isFinite(own?.OFFRUSHYARDS)&&Number.isFinite(other?.OFFPASSYARDS)&&Number.isFinite(other?.OFFRUSHYARDS))turningPoint=`The offensive yardage split was ${own.OFFPASSYARDS+own.OFFRUSHYARDS} for ${w}, ${other.OFFPASSYARDS+other.OFFRUSHYARDS} for ${l}.`;
 if(!turningPoint)return null;
 const rows=(s.performances??[]).filter(r=>r.game===g.id&&r.team===winner&&/^GameOffensive(?:KPReturn)?Stats$/.test(r.type));
 const unique=new Map();for(const r of rows){if(unique.has(r.player))unique.set(r.player,null);else unique.set(r.player,r);}
 const candidates=[...unique.values()].filter(Boolean).map(r=>({r,p:s.players.find(p=>p.id===r.player),impact:(r.stats.PASSYARDS??0)/15+(r.stats.RUSHYARDS??0)/8+(r.stats.RECEIVEYARDS??0)/8+((r.stats.PASSTDS??0)+(r.stats.RUSHTDS??0)+(r.stats.RECEIVETDS??0))*5})).filter(x=>x.p).sort((a,b)=>b.impact-a.impact||a.p.id.localeCompare(b.p.id));
 const star=candidates[0],line=star&&completeOffensiveLine(star.p.position,star.r.stats),detail=line?`${star.p.name}: ${line}.`:Number.isFinite(own?.GIVEAWAYS)&&Number.isFinite(other?.GIVEAWAYS)?`Giveaways: ${w} ${own.GIVEAWAYS}, ${l} ${other.GIVEAWAYS}.`:'';
 return {winner:w,loser:l,winnerId:winner,loserId:loser,score:`${ws}\u2013${ls}`,turningPoint,detail,kind,quarterVerified,player:star?.p.id??null};
}
