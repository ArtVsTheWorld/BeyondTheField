import {visibleGame} from './football_context.mjs';
export function verifiedSeasonRecord(s,t){
 const played=s.games.filter(g=>visibleGame(s,g)&&(g.home===t.id||g.away===t.id));
 if(!played.length||new Set(played.map(g=>g.id)).size!==played.length)return null;
 const wins=played.filter(g=>(g.home===t.id?g.homeScore:g.awayScore)>(g.home===t.id?g.awayScore:g.homeScore)).length,losses=played.filter(g=>(g.home===t.id?g.homeScore:g.awayScore)<(g.home===t.id?g.awayScore:g.homeScore)).length,ties=played.length-wins-losses;
 const st=t.seasonStats?.season===s.season.CurrentSeasonYear?t.seasonStats.stats:null,expected=st&&Number.isInteger(st.WINS)&&Number.isInteger(st.LOSSES)?{wins:st.WINS,losses:st.LOSSES,ties:st.TIES??0}:t;
 if(wins!==expected.wins||losses!==expected.losses||ties!==(expected.ties??0))return null;
 return {wins,losses,ties,played,record:`${wins}\u2013${losses}`+(ties?'\u2013'+ties:'')};
}
// Editorial expectations come from native prestige, never school-name lore.
// Targets are expressed as win rates to support custom schedule lengths.
export function programExpectations(s,t,knownRecord=null){
 const record=knownRecord??verifiedSeasonRecord(s,t),stars=t.prestigeStars;
 if(!record||!Number.isFinite(stars)||stars<1||stars>5)return {verdict:'neutral',known:false,note:'',record:record?.record??null};
 const cc=s.season.RegularSeasonWeekConferenceChampionship??15,regular=record.played.filter(g=>g.phase==='RegularSeason'&&g.week<cc),n=regular.length;
 if(n<4)return {verdict:'neutral',known:false,note:'',record:record.record};
 const wins=regular.filter(g=>(g.home===t.id?g.homeScore:g.awayScore)>(g.home===t.id?g.awayScore:g.homeScore)).length,targets=[4,5,7,9,10],low=Math.floor(stars)-1,high=Math.ceil(stars)-1,target=(targets[low]+(targets[high]-targets[low])*(stars-Math.floor(stars)))/12,rate=wins/n;
 const champion=record.played.some(g=>g.phase==='NationalChampionship'&&(g.home===t.id?g.homeScore:g.awayScore)>(g.home===t.id?g.awayScore:g.homeScore));
 const verdict=champion?'positive':rate-target>=.125?'positive':rate-target<=-.125?'negative':'neutral';
 const note=champion?'A national championship is the standard-setting finish.':verdict==='negative'&&stars>=4?'That falls short of the standard at a program built to contend for titles.':verdict==='negative'?'The results fell below a reasonable expectation for this program.':verdict==='positive'&&stars<=2?'That is a meaningful step forward for a program still building its standing.':verdict==='positive'?'The results beat the usual expectations for this program.':stars>=4?'A winning record alone does not settle the conversation here; this program is judged on contention.':'The record broadly meets expectations; the next step matters.';
 return {known:true,verdict,note,record:record.record,regularWins:wins,regularLosses:n-wins,regularGames:n,targetRate:target,winRate:rate};
}
export function newsCycle(s){
 const {CurrentWeekType:phase,CurrentWeek:week,CurrentStage:stage}=s.season,cc=s.season.RegularSeasonWeekConferenceChampionship??15;
 if(phase==='PreSeason')return {key:'preseason',label:'Preseason',focusShare:0};
 if(phase==='OffSeason'||stage!=='NFLSeason')return {key:'offseason',label:'Offseason',focusShare:0};
 if(phase==='RegularSeason'&&week<cc)return {key:week<=3?'opening':week<10?'midseason':'late',label:week<=3?'Opening weeks':week<10?'Midseason':'Late-season races',focusShare:0};
 return {key:'postseason',label:phase==='NationalChampionship'?'National championship':phase==='RegularSeason'&&week===cc?'Conference championships':'Postseason',focusShare:phase==='NationalChampionship'?.65:.55};
}
