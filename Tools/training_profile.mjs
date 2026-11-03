const groups={
 movement:['his burst and movement',['SpeedRating','AccelerationRating','AgilityRating']],
 accuracy:['his passing accuracy',['ThrowAccuracyShortRating','ThrowAccuracyMidRating','ThrowAccuracyDeepRating']],
 arm:['his arm strength',['ThrowPowerRating']],
 receiving:['his receiving technique',['CatchingRating','CatchInTrafficRating','ShortRouteRunningRating','MediumRouteRunningRating','DeepRouteRunningRating']],
 blocking:['his blocking',['RunBlockRating','PassBlockRating']],coverage:['his coverage',['ManCoverageRating','ZoneCoverageRating']],
 rush:['his pass-rush technique',['FinesseMovesRating','PowerMovesRating','BlockSheddingRating']],
 tackling:['his tackling and recognition',['TackleRating','PlayRecognitionRating']],strength:['his strength',['StrengthRating']],
 handling:['his ball security and contact balance',['CarryingRating','BreakTackleRating']],kicking:['his kicking',['KickPowerRating','KickAccuracyRating']]
};
const byPosition={QB:['accuracy','arm','movement','handling'],HB:['movement','handling','receiving','blocking','strength'],RB:['movement','handling','receiving','blocking','strength'],FB:['blocking','handling','strength'],WR:['receiving','movement','handling'],TE:['receiving','blocking','strength','movement'],K:['kicking'],P:['kicking']};
const names=position=>byPosition[position]??(/^(LT|LG|C|RG|RT|OL|OT|OG|LS)$/.test(position)?['blocking','strength']:/^(CB|FS|SS|S|DB)$/.test(position)?['coverage','movement','tackling']:['rush','tackling','coverage','movement','strength']);
export const trainingFields=position=>new Set(names(position).flatMap(n=>groups[n][1]));
export function trainingArea(position,gains){
 return names(position).map(n=>({text:groups[n][0],score:gains.filter(g=>groups[n][1].includes(g.field)&&g.gain>=3).reduce((n,g)=>n+g.gain,0)})).sort((a,b)=>b.score-a.score).find(a=>a.score>0)?.text??null;
}
