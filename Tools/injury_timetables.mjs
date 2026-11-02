// Min/MaxInjuryDuration are remaining weeks, verified across real Week 4/6/10
// observations of the same injury episodes. Never subtract elapsed time twice.
export function injuryTimetable(p,season=null){
 if(!p.injury||p.injury==='Uninjured')return null;
 if(p.injurySeverity==='CareerEnding')return {kind:'career-ending',text:'Listed as a career-ending injury.'};
 if(p.injurySeverity==='SeasonEnding'&&(!season||!Number.isInteger(p.injuryYear)||p.injuryYear===season.CurrentYear))return {kind:'season-ending',text:'Expected to miss the rest of the season.'};
 if(p.injury==='Undiagnosed')return {kind:'pending',text:'Evaluation is still pending; no return estimate is available.'};
 const lo=p.minInjury,hi=p.maxInjury;
 if(!Number.isInteger(lo)||!Number.isInteger(hi)||lo < -32||hi<0||lo>=63||hi>=63||lo>hi)return {kind:'unknown',text:'A return timetable has not been established.'};
 const min=Math.max(0,lo),max=hi;
 if(p.injury==='EarlyReturn')return {kind:'early-return',minWeeks:min,maxWeeks:max,text:'Available for an early return, with recovery still ongoing.'};
 if(max===0)return {kind:'this-week',minWeeks:0,maxWeeks:0,text:'The listed return window is this week; availability still needs confirmation.'};
 if(min===0)return {kind:'window',minWeeks:0,maxWeeks:max,text:`Could return this week; the estimated window extends ${max===1?'up to 1 week':'up to '+max+' weeks'}.`};
 const range=min===max?String(min):min+'\u2013'+max;
 return {kind:'window',minWeeks:min,maxWeeks:max,text:`Estimated return: ${range} ${max===1?'week':'weeks'}.`};
}
