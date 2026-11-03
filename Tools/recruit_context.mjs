import {hash} from './story_authors.mjs';
import {portalOrigin} from './offseason_recruiting.mjs';
export const recruitingCategory=c=>['recruiting','offers','signings'].includes(c);
export function recruitContext(s,p){
 const r=s.recruitStatuses?.find(r=>r.player===p.id),raw=r?.recruitClass??s.commitments?.find(c=>c.player===p.id)?.recruitClass??s.signings?.find(c=>c.player===p.id)?.recruitClass;
 const kind=raw?.startsWith('Transfer_')?'transfer':raw?.startsWith('JuniorCollege_')?'JUCO':raw==='HighSchool'?'high school':null;
 const from=kind==='transfer'?portalOrigin(s,p):null,old=s.teams.find(t=>t.id===from&&t.id!==255);
 return {recruitKind:kind,prospectType:kind?kind+' ':'',stars:p.starRating??null,formerTeam:old?.id??null,formerSchool:old?.name??null,originDetail:old?' from '+old.name:'',starDescription:p.starRating?p.starRating+'-star ':''};
}
export function recruitAttention(s,p){
 if(p.starRating===1)return false;
 if(p.starRating!==2)return true;
 return hash(`${s.leagueId}|${s.season.CurrentSeasonYear}|${s.season.CurrentWeekType}|${s.season.CurrentWeek}|${p.id}|underdog`) % 10===0;
}
