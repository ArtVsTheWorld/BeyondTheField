import {createHash} from 'node:crypto';
export const PUBLICATION_POLICY_VERSION=2;
export function publishOffer(s,event){
 const key=`${s.leagueId}|${s.season.CurrentSeasonYear}|${s.season.CurrentWeekType}|${s.season.CurrentWeek}|${event.id}|scholarship-post-v1`;
 return createHash('sha256').update(key).digest().readUInt32BE(0)<Math.floor(0x100000000*.20);
}
export function currentPublicationPolicy(feed){
 return feed.publicationPolicyVersion===PUBLICATION_POLICY_VERSION;
}

// One 33% gate per eligible parent thread: reloads and unrelated stories cannot reroll it.
export function publishReply(s,id,parentId){
 const key=`${s.leagueId}|${s.season.CurrentSeasonYear}|${s.season.CurrentWeekType}|${s.season.CurrentWeek}|${parentId}|reply-thread-v1`;
 return createHash('sha256').update(key).digest().readUInt32BE(0)<Math.floor(0x100000000*.33);
}
