import {createHash} from 'node:crypto';
export const PUBLICATION_POLICY_VERSION=1;
export function publishOffer(s,event){
 const key=`${s.leagueId}|${s.season.CurrentSeasonYear}|${s.season.CurrentWeekType}|${s.season.CurrentWeek}|${event.id}|scholarship-post-v1`;
 return createHash('sha256').update(key).digest().readUInt32BE(0)<Math.floor(0x100000000*.20);
}
export function currentPublicationPolicy(feed){
 return feed.publicationPolicyVersion===PUBLICATION_POLICY_VERSION||feed.publicationPolicyVersion==null&&Array.isArray(feed.events)&&!feed.events.some(e=>e.category==='offers');
}
