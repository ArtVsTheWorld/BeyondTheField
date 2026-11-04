// Read-only model estimates. Inspired by Ace's Smart Force Win roster/unit approach.
// Starter/depth blending and league-relative gain credit Balla's CFB27 Team Overall
// Calculation Tool, Option A (v0.1), via Ace's CFB Toolkit (MIT). See THIRD_PARTY_NOTICES.md.
import {verifiedTeamRows} from './football_context.mjs';
const counts={QB:1,HB:2,FB:1,WR:3,TE:1,LT:1,LG:1,C:1,RG:1,RT:1,DT:2,LE:1,RE:1,MLB:1,LOLB:1,ROLB:1,CB:2,FS:1,SS:1,K:1,P:1};
const weights={off:{QB:3,HB:1.5,FB:.5,WR:2,TE:1,LT:1.5,LG:1,C:1,RG:1,RT:1.5},def:{DT:1.5,LE:1.5,RE:1.5,MLB:1.5,LOLB:1,ROLB:1,CB:1.5,FS:1,SS:1},st:{K:1,P:1}};
const mean=a=>a.length?a.reduce((n,x)=>n+x,0)/a.length:null;
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
export function rosterStrengths(s){
 const rows=new Map();
 for(const t of s.teams.filter(t=>t.id!==255)){
  const positions={};for(const p of s.players)if(p.team===t.id&&p.injury==='Uninjured'&&Number.isFinite(p.overall)&&p.overall>0&&p.overall<=99&&counts[p.position])(positions[p.position]??=[]).push(p.overall);
  const blended={};for(const [pos,a] of Object.entries(positions)){a.sort((a,b)=>b-a);blended[pos]=.72*mean(a.slice(0,counts[pos]))+.28*mean(a);}
  const r={};for(const [unit,w] of Object.entries(weights)){const available=Object.entries(w).filter(([p])=>Number.isFinite(blended[p]));r[unit]=available.length?available.reduce((n,[p,w])=>n+blended[p]*w,0)/available.reduce((n,[,w])=>n+w,0):null;}
  // Thin/unknown rosters cannot silently become average opponents.
  if(r.off===null||r.def===null||!Number.isFinite(blended.QB)||Object.keys(blended).length<8)continue;
  r.st??=mean([r.off,r.def]);r.units=blended;rows.set(t.id,r);
 }
 const centers={off:mean([...rows.values()].map(r=>r.off)),def:mean([...rows.values()].map(r=>r.def)),st:mean([...rows.values()].map(r=>r.st))};
 for(const r of rows.values())for(const unit of ['off','def','st']){const delta=r[unit]-centers[unit];r[unit]=clamp(centers[unit]+delta*(delta>=0?2.25:2.75),0,99);}
 return rows;
}
export function projectLine(s,g,strengths=rosterStrengths(s)){
 const h=strengths.get(g.home),a=strengths.get(g.away);if(!h||!a)return null;
 const base=r=>.45*r.off+.45*r.def+.10*r.st;
 const matchup=((h.off-a.def)-(a.off-h.def))/2;
 const rivalry=s.teams.find(t=>t.id===g.home)?.rivals?.includes(g.away)||s.teams.find(t=>t.id===g.away)?.rivals?.includes(g.home);
 const venue=g.neutral===true?0:2.5;
 const edge=(.65*(base(h)-base(a))+.35*matchup)*1.25*(rivalry?.9:1)+venue;
 const homeSpread=-Math.round(clamp(edge,-45,45)*2)/2;
 return {homeSpread,spread:Math.abs(homeSpread),favorite:homeSpread===0?null:homeSpread<0?g.home:g.away,model:'starter-depth-units-v2'};
}
export function analystProjection(s,g,persona,{strengths=rosterStrengths(s),stats=verifiedTeamRows(s)}={}){
 const h=strengths.get(g.home),a=strengths.get(g.away);if(!h||!a)return null;
 const profiles={1:{off:.45,def:.45,st:.10,data:.40,basis:'roster depth and scoring balance'},2:{off:.55,def:.40,st:.05,data:.70,basis:'recent scoring form'},3:{off:.60,def:.35,st:.05,data:.55,basis:'offensive production and matchup pressure'},4:{off:.40,def:.55,st:.05,data:.65,basis:'efficiency on both sides of the ball'},5:{off:.50,def:.40,st:.10,data:.20,basis:'roster depth and quarterback play'}};
 const p=profiles[persona]??profiles[1],venue=g.neutral===true?0:2.5;
 let edge=((h.off-a.off)*p.off+(h.def-a.def)*p.def+(h.st-a.st)*p.st)*1.25+venue;
 const hr=stats.get(g.home),ar=stats.get(g.away);
 if(hr?.n>=3&&ar?.n>=3){
  let observed=(hr.ppg+ar.ppga-ar.ppg-hr.ppga)/2;
  if(persona===2){const recent=r=>r.games.slice().sort((x,y)=>y.week-x.week).slice(0,3).reduce((n,x)=>n+(x.home===r.team.id?x.homeScore-x.awayScore:x.awayScore-x.homeScore),0)/Math.min(3,r.games.length);observed=(recent(hr)-recent(ar))/2;}
  if(persona===4&&[hr.ypp,ar.ypp,hr.yppa,ar.yppa].every(Number.isFinite))observed=((hr.ypp+ar.yppa)-(ar.ypp+hr.yppa))*32;
  if(persona===3)observed=(hr.ppg-ar.ppg)*.7+(ar.ppga-hr.ppga)*.3;
  edge=edge*(1-p.data)+(observed+venue)*p.data;
 }
 if(persona===5&&Number.isFinite(h.units.QB)&&Number.isFinite(a.units.QB))edge+=Math.max(-5,Math.min(5,(h.units.QB-a.units.QB)*.2));
 const homeSpread=-Math.round(clamp(edge,-45,45)*2)/2;
 return {homeSpread,spread:Math.abs(homeSpread),favorite:homeSpread===0?null:homeSpread<0?g.home:g.away,model:'analyst-'+persona+'-v1',basis:p.basis};
}
