// Shared story facts from either a read-only save adapter or a native runtime snapshot.
export async function normalizeDynasty({records,resolve,array,arraySlots},identity) {
  const season=(await records('SeasonInfo'))[0]?.v,franchise=(await records('Franchise'))[0]?.v;
  if(!season||!franchise)throw Error('Missing Dynasty identity');
  let userTeamIndex=null;
  for(const {v:u} of await records('FranchiseUser')){if(u.IsRetired)continue;const team=await resolve(u.Team)??await resolve(u.UserEntity);
    if(team&&(userTeamIndex===null||u.AdminLevel==='Owner'))userTeamIndex=team.v.TeamIndex;}
  if(userTeamIndex===null)throw Error('No controlled Dynasty team');
  const finalStatuses=['HomeWon','AwayWon','Tie'];
  const publicStatus=g=>g.HasBeenPublished===false&&finalStatuses.includes(g.GameStatus)?'Unplayed':g.GameStatus;
  const cleanText=v=>typeof v==='string'&&v.trim()?v.trim():null;
  const tag=v=>{const s=cleanText(v)?.replace(/^#+/,'');return s&&/^[\p{L}\p{N}_]+$/u.test(s)?'#'+s:null;};
  const teamRefs=new Map(),teams=[],rawTeams=[];
  for(const {key,v,capacity} of await records('Team')){
    teamRefs.set(key,v.TeamIndex);if(capacity<=1)continue;
    const coachRecord=await resolve(v.HeadCoach),coach=coachRecord?.type==='Coach'&&coachRecord.v.TeamIndex===v.TeamIndex?coachRecord:null;
    const coachFirst=cleanText(coach?.v.FirstName),coachLast=cleanText(coach?.v.LastName),coachName=[coachFirst,coachLast].filter(Boolean).join(' ');
    const seasonSlots=arraySlots?await arraySlots(v.TeamSeasonStats):[];
    const currentStats=seasonSlots[0];
    const seasonStats=currentStats?.type==='TeamStats'?{season:season.CurrentSeasonYear,slot:0,stats:currentStats.v}:null;
    const coachFacts=c=>({seasonsWithTeam:Number.isInteger(c?.SeasonsWithTeam)?c.SeasonsWithTeam:null,yearsCoaching:Number.isInteger(c?.YearsCoaching)?c.YearsCoaching:null,style:c?.DominantArchetype??null});
    const headCoach=coachName?{id:coach.key,name:coachName,firstName:coachFirst,lastName:coachLast,...coachFacts(coach.v)}:null;
    const builder=await resolve(v.TeamBuilderData);
    const stadium=await resolve(v.Stadium),depth=await resolve(v.DepthChart),depthChart={};
    if(depth?.type==='DepthChart')for(const [position,ref] of Object.entries(depth.v))if(typeof ref==='string')depthChart[position]=(await array(ref)).filter(p=>p.type==='Player'&&p.v.TeamIndex===v.TeamIndex).map(p=>p.key);
    const prior=seasonSlots[1]?.type==='TeamStats'?seasonSlots[1].v:null;
    const priorWins=v.TEAM_PREVSEASWINS,priorLosses=v.TEAM_PREVSEASLOSSES;
    const previousSeason=Number.isInteger(priorWins)&&Number.isInteger(priorLosses)&&priorWins+priorLosses>=8?{wins:priorWins,losses:priorLosses,playoffRound:v.LastSeasonPlayoffRoundReached??null,
      stats:prior&&prior.WINS===priorWins&&prior.LOSSES===priorLosses&&season.CurrentYear>0?prior:null}:null;
    const city=await resolve(v.City);
    const pipelines=(await array(v.SchoolPipelineInfluenceList)).filter(x=>x.v.InfluenceLevel!=='None'&&x.v.InfluenceValue>0).map(x=>x.v.Pipeline).filter(Boolean);
    const staff=async ref=>{const c=await resolve(ref);return c?.type==='Coach'&&c.v.TeamIndex===v.TeamIndex?{id:c.key,name:[cleanText(c.v.FirstName),cleanText(c.v.LastName)].filter(Boolean).join(' '),lastName:cleanText(c.v.LastName),...coachFacts(c.v)}:null;};
    teams.push({id:v.TeamIndex,isTeamBuilder:v.IsTeamBuilder===true,logoVariants:{secondaryAvailable:builder?.type==='TeamBuilderData'&&Boolean(cleanText(builder.v.SecondaryLogoURL)),tertiaryAvailable:builder?.type==='TeamBuilderData'&&Boolean(cleanText(builder.v.TertiaryLogoURL)),secondary:v.TEAM_ALT_LOGO??null,tertiary:v.TEAM_LOGO_SMALL_ALT??null,secondaryAsset:cleanText(v.TEAM_ALT_LOGO_ASSETNAME),tertiaryAsset:cleanText(v.TEAM_LOGO_SMALL_ALT_ASSETNAME)},stadium:cleanText(stadium?.v.Name)||cleanText(stadium?.v.STADIUM_DISPLAYNAME),depthChart,previousSeason,prestigeStars:Number.isFinite(v.TeamPrestige)&&v.TeamPrestige>0?v.TeamPrestige/2:null,offensiveCoordinator:await staff(v.OffensiveCoordinator),defensiveCoordinator:await staff(v.DefensiveCoordinator),recordKey:key,brandExposure:v.ProgramPointsBrandExposureGrade??null,brandExposurePoints:v.BrandExposureProgramPoints??null,homeState:city?.v.State??null,pipelines,seasonStats,nickname:cleanText(v.NickName),nicknameAlt:cleanText(v.NickNameAlt),hashtags:[...new Set([tag(v.Hashtag1),tag(v.Hashtag2)].filter(Boolean))],headCoach,name:v.DisplayName||v.LongName||v.ShortName,logo:v.TEAM_LOGO,
      mediaRank:v.MediaPoll_CurrentRank,mediaLastRank:v.MediaPoll_LastWeeksRank,
      coachesRank:v.CoachesPoll_CurrentRank,coachesLastRank:v.CoachesPoll_LastWeeksRank,
      cfpRank:v.CFPPoll_CurrentRank,cfpLastRank:v.CFPPoll_LastWeeksRank,
      conferenceRank:v.CurSeasonConfStanding,conferenceLastRank:v.LastWeekConferenceStanding,
      conferenceWins:v.ConfWin,conferenceLosses:v.ConfLoss,conferenceTies:v.ConfTie,
      wins:v.HomeWin+v.RoadWin,losses:v.HomeLoss+v.RoadLoss,ties:(v.HomeTie??0)+(v.RoadTie??0)});rawTeams.push(v);
  }
  const teamIndex=async ref=>{const t=await resolve(ref);return t?teamRefs.get(t.key)??t.v.TeamIndex:null;};
  const teamName=async ref=>{const t=await resolve(ref);return t?.v.DisplayName||t?.v.LongName||t?.v.ShortName||null;};
  const conferences=[];
  for(const {key,v:c} of await records('Conference')){
    if(!c.Name&&!c.TeamSlots?.includes('1'))continue;
    const members=new Set();
    for(const t of await array(c.TeamSlots))if(t.type==='Team')members.add(t.v.TeamIndex);
    for(const d of await array(c.Divisions))for(const t of await array(d.v.Teams))if(t.type==='Team')members.add(t.v.TeamIndex);
    if(!members.size)continue;
    const conference={id:key,name:c.Name||c.ConferenceEnum,independent:c.ConferenceEnum==='Independents',teams:[...members]};
    conferences.push(conference);
    for(const team of teams)if(members.has(team.id)){
      if(team.conferenceId&&team.conferenceId!==key)throw Error('Team belongs to conflicting conference records');
      team.conferenceId=key;team.conferenceName=conference.name;team.independent=conference.independent;
    }
  }
  for(const t of rawTeams){const team=teams.find(p=>p.id===t.TeamIndex);team.rivals=[];
    for(const ref of [t.Rival1TeamRef,t.Rival2TeamRef,t.Rival3TeamRef]){const id=await teamIndex(ref);if(id!=null)team.rivals.push(id);}}
  const players=[],playerRefs=new Map(),rawPlayers=[];
  for(const {key,v:p} of await records('Player')){
    const player={id:key,firstName:cleanText(p.FirstName),lastName:cleanText(p.LastName),name:`${p.FirstName} ${p.LastName}`,position:p.Position,personality:['Leader','Intense','Entertainer','TeamPlayer','Unpredictable'].includes(p.Personality)?p.Personality:null,team:p.TeamIndex,
      homePipeline:p.HomePipeline??null,homeState:p.PLYR_HOME_STATE??null,jerseyNumber:p.TeamIndex!==255&&Number.isInteger(p.JerseyNum)&&p.JerseyNum>=0&&p.JerseyNum<=99?p.JerseyNum:null,portrait:p.PLYR_PORTRAIT,portraitForcedSilhouette:p.PortraitForceSilhouette===true,isNil:p.IsNIL,overall:p.OverallRating,age:p.Age,classYear:p.SchoolYear,redshirt:p.RedshirtStatus??null,yearsWithTeam:Number.isInteger(p.PLYR_CONSECYEARSWITHTEAM)?p.PLYR_CONSECYEARSWITHTEAM:null,
      injury:p.InjuryStatus,injuryType:p.InjuryType,injuryWeek:p.LatestInjuryWeek,injuryYear:p.LatestInjuryYear,
      injuryStage:p.LatestInjuryStage,minInjury:p.MinInjuryDuration,maxInjury:p.MaxInjuryDuration,
      transferRisk:p.AbsoluteTransferChance,nil:p.CurrentNILCompensation,stars:p.ProspectStarRating,starRating:({ONE_STAR:1,TWO_STAR:2,THREE_STAR:3,FOUR_STAR:4,FIVE_STAR:5})[p.ProspectStarRating]??null,seasonStats:[],previousSeasonStats:[]};
    for(const st of await array(p.SeasonStats)){if(st.v.SEAS_YEAR===season.CurrentYear&&st.v.YEARBYYEARTEAMINDEX===p.TeamIndex)player.seasonStats.push({type:st.type,stats:st.v});if(season.CurrentYear>0&&st.v.SEAS_YEAR===season.CurrentYear-1)player.previousSeasonStats.push({type:st.type,stats:st.v});}
    players.push(player);playerRefs.set(key,player);rawPlayers.push({key,v:p});
  }
  const games=[],gameRefs=new Map();
  for(const {key,v:g,capacity} of await records('SeasonGame')){
    if(capacity<=1||g.IsPractice||g.SeasonYear!==season.CurrentYear)continue;
    const home=await teamIndex(g.HomeTeam),away=await teamIndex(g.AwayTeam);if(home==null||away==null)continue;
    const homeVenue=rawTeams.find(t=>t.TeamIndex===home);
    const game={id:key,neutral:g.Stadium&&homeVenue?.Stadium?g.Stadium!==homeVenue.Stadium&&g.Stadium!==homeVenue.AltStadium:null,year:g.SeasonYear,week:g.SeasonWeek,phase:g.SeasonWeekType,status:publicStatus(g),published:typeof g.HasBeenPublished==='boolean'?g.HasBeenPublished:null,
      home,away,homeName:await teamName(g.HomeTeam),awayName:await teamName(g.AwayTeam),homeScore:publicStatus(g)==='Unplayed'?0:g.HomeScore,awayScore:publicStatus(g)==='Unplayed'?0:g.AwayScore,
      homeQuarterScores:g.HasBeenPublished===false?null:[g.HomeScoreQuarter1,g.HomeScoreQuarter2,g.HomeScoreQuarter3,g.HomeScoreQuarter4],awayQuarterScores:g.HasBeenPublished===false?null:[g.AwayScoreQuarter1,g.AwayScoreQuarter2,g.AwayScoreQuarter3,g.AwayScoreQuarter4],homeOvertimePoints:g.HasBeenPublished===false?null:g.HomeScoreOT,awayOvertimePoints:g.HasBeenPublished===false?null:g.AwayScoreOT,month:g.GameDateMonth,day:g.GameDateDay,
      weekday:g.DayOfWeek,time:g.TimeOfDay,spotlight:g.GameOfTheWeekScore,
      thanksgiving:g.ThanksgivingFlag,christmas:g.ChristmasFlag,newYears:g.NewYearsFlag};
    if(g.SeasonWeek<=season.CurrentWeek&&g.SeasonWeekType===season.CurrentWeekType&&g.HasBeenPublished!==false&&finalStatuses.includes(g.GameStatus)){
      game.homeStats=(await resolve(g.HomeTeamStatCache))?.v??null;game.awayStats=(await resolve(g.AwayTeamStatCache))?.v??null;
    }
    games.push(game);gameRefs.set(key,game);
  }
  const performances=[];
  if(season.CurrentStage==='NFLSeason')for(const {key,v:p} of rawPlayers){
    if(p.TeamIndex===255)continue;
    for(const st of await array(p.GameStats)){
      if(!/^Game.*Stats$/.test(st.type))throw Error('Unexpected game stat record');
      const ref=await resolve(st.v.SeasonGame),g=ref&&gameRefs.get(ref.key);
      if(!g||g.phase!==season.CurrentWeekType||!['HomeWon','AwayWon','Tie'].includes(g.status))continue;
      const opp=await teamIndex(st.v.OpposingTeam),team=opp===g.home?g.away:opp===g.away?g.home:null;
      if(team==null)throw Error('Game stats opponent mismatch');
      performances.push({player:key,game:g.id,team,type:st.type,stats:st.v});
    }
  }
  const heisman=[];
  const awards=(await records('Awards'))[0];
  if(awards)for(const h of await array(awards.v.HeismanRanking)){
    // Native Heisman ranks are zero-based; -1 means no prior place.
    // Verified against the native Heisman panel: internal places 0/1 display as No. 1/2.
    const p=await resolve(h.v.Player),current=h.v.CurrentRank,prior=h.v.LastWeekRank;
    if(!p||!Number.isInteger(current)||current<0||current>4)continue;
    heisman.push({player:p.key,team:await teamIndex(h.v.Team),rank:current+1,lastRank:Number.isInteger(prior)&&prior>=0&&prior<=4?prior+1:null});
  }
  const preseasonHonors=[];
  if(awards)for(const a of await array(awards.v.AllAmAwards)){
    if(a.type!=='PlayerAward'||!['ALL_AM_1ST_PRE','ALL_AM_2ND_PRE','ALL_AM_1ST_PRE_CONF','ALL_AM_2ND_PRE_CONF'].includes(a.v.AwardType)||a.v.Period!=='Season'||a.v.PeriodIndex!==season.CurrentYear)continue;
    const p=await resolve(a.v.Player),team=await teamIndex(a.v.Team),conference=await resolve(a.v.Conference);
    if(p&&team!==null&&p.v.TeamIndex===team)preseasonHonors.push({id:a.key,player:p.key,team,conferenceId:conference?.key??null,type:a.v.AwardType,position:a.v.Position,year:a.v.PeriodIndex});
  }
  const weeklyAwards=[];
  if(awards)for(const a of await array(awards.v.WeeklyAwards)){
    if(a.type!=='PlayerAward'||a.v.Period!=='Game')continue;
    const p=await resolve(a.v.Player),t=await teamIndex(a.v.Team),c=await resolve(a.v.Conference);
    if(p&&t!==null)weeklyAwards.push({id:a.key,type:a.v.AwardType,week:a.v.PeriodIndex,player:p.key,team:t,conferenceId:c?.key??null});
  }
  const recordsList=[];
  async function statRecords(ref,scope,scopeId,period){const group=await resolve(ref);if(!group)return;for(const [metric,child] of Object.entries(group.v)){
    const r=await resolve(child);if(!r||r.type!=='PlayerStatRecord'||!Number.isInteger(r.v.statValue)||r.v.statValue<=0)continue;
    recordsList.push({id:r.key,scope,scopeId,period,metric,value:r.v.statValue,year:r.v.calendarYear,playerName:[r.v.firstName,r.v.lastName].filter(Boolean).join(' '),team:await teamIndex(r.v.TeamRef),school:r.v.teamName});
  }}
  for(let i=0;i<rawTeams.length;++i){const t=rawTeams[i];if(t.TeamIndex===255)continue;await statRecords(t.GameStatRecords,'school',t.TeamIndex,'game');await statRecords(t.SeasonStatRecords,'school',t.TeamIndex,'season');}
  for(const {key,v:c} of await records('Conference')){await statRecords(c.GameStatRecords,'conference',key,'game');await statRecords(c.SeasonStatRecords,'conference',key,'season');}
  for(const {v:l} of await records('League')){await statRecords(l.PlayerGameStatRecords,'national','national','game');await statRecords(l.PlayerSeasonStatRecords,'national','national','season');}
  // CommittedPlayers is empty in this build, even after a hard commitment.
  // Verify the recruit stage and leading school against that school's board;
  // an offer or a nonzero target week on its own never establishes a commit.
  const recruitStatuses=[],recruitRefs=new Map();for(const r of await records('Recruit')){
    const recruitPlayer=await resolve(r.v.Player);if(recruitPlayer)recruitStatuses.push({player:recruitPlayer.key,stage:r.v.RecruitStage,nationalRank:r.v.NationalRank>0?r.v.NationalRank:null,positionRank:r.v.PositionRank>0?r.v.PositionRank:null,stateRank:r.v.StateRank>0?r.v.StateRank:null,topSchools:(await array(r.v.TopSchoolsList)).slice(0,3).map(x=>x.v.TeamId).filter(id=>teams.some(t=>t.id===id&&id!==255))});
    if(!['HardCommitted','SoftCommitted'].includes(r.v.RecruitStage))continue;
    const p=await resolve(r.v.Player),schools=await array(r.v.TopSchoolsList);
    if(!p||!schools.length)continue;
    const winner=schools[0].v;
    if(schools.slice(1).some(sc=>sc.v.TeamInfluence>=winner.TeamInfluence))continue;
    recruitRefs.set(r.key,{player:p.key,rank:r.v.NationalRank,stage:r.v.RecruitStage,team:winner.TeamId});
  }
  const commitments=[],offers=[],recruitInterests=[],recruitVisits=[];
  for(const t of rawTeams){
    const board=await resolve(t.RecruitingBoard);
    if(board)for(const target of await array(board.v.Recruits)){
      const r=await resolve(target.v.Recruit),commit=r&&recruitRefs.get(r.key);
      const visit=await resolve(target.v.ScheduledVisit);if(r&&visit?.type==='ActiveVisitInfo'&&visit.v.WeekType===season.CurrentWeekType&&visit.v.WeekNumber===season.CurrentWeek){const p=await resolve(r.v.Player);if(p)recruitVisits.push({player:p.key,team:t.TeamIndex,week:visit.v.WeekNumber,phase:visit.v.WeekType});}
      if(r&&t.TeamIndex===userTeamIndex){const p=await resolve(r.v.Player);if(p)recruitInterests.push(p.key);}
      // New is the native current-week offer state; Offered is the carried state.
      if(r&&['New','Offered'].includes(target.v.ScholarshipStatus)){
        const p=await resolve(r.v.Player);if(p)offers.push({player:p.key,team:t.TeamIndex,rank:r.v.NationalRank});
      }
      if(!commit||commit.team!==t.TeamIndex)continue;
      commitments.push({...commit,week:target.v.CommittedWeekNumber});
    }
  }
  return {format:2,sourceUnchanged:true,gameYear:27,...identity,leagueId:franchise.LeagueID,
    season,userTeamIndex,teams,conferences,players,games,performances,heisman,commitments,offers,recruitInterests,weeklyAwards,records:recordsList,recruitStatuses,recruitVisits,preseasonHonors};
}
