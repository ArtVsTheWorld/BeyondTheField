# v76: postseason selections, honors, signing and coaching

## Verified calendar

The tested league has conference championship games in Week 15, a regular-season waiting week in Week 16, then BowlSeason1/selection/early signing/annual awards in Week 17. The logic derives waiting/selection boundaries as configured championship week +1/+2 and requires the postseason phase for confirmed selections. The user verified this calendar.

Week 16 adds anticipation and keeps five-plus-win teams waiting. Allocated future bowl games, simulated unpublished scores, annual records or coaching queues cannot produce premature confirmations. Poll/Heisman race and conference standings updates stop after championship week. Actual championship-result recaps can still appear in the next publication.

The already-stored waiting-week edition receives a targeted correction: stale standings/race posts are removed and premature/old position announcements become waiting stories. Genuine recaps and unrelated recruiting/injury facts are preserved; no unavailable historical facts are reconstructed from Week 17. Original identities, likes and edition identity remain.

## Selections and bracket

Complete native bowl/first-round fixtures establish invitations. Partial fixtures are retained separately, so an assigned bye team does not need a known opponent to remain alive or receive a bracket-path story. A known partial ordinary-bowl assignment also prevents a false season-ending farewell.

Native first-round slots 0-3 connect to quarterfinal slots 4-7. The user's Miami example corroborates slot 3 -> slot 7; the actual fixture set has unique coherent slots and four distinct bye teams. The real paths are Ole Miss vs Ohio State/LSU winner, SMU vs Georgia/Nebraska winner, BYU vs Missouri/Iowa winner, and Miami vs USC/Boise State winner. No seed pairing is inferred from poll rank. Incomplete, duplicate or contradictory slot sets suppress inferred paths. Unpublished simulated winners never resolve an opponent. Semifinal/title matchups use actual assignments rather than an unverified future seed projection.

Nonselected five-plus-win programs can finish at selection week once all their results corroborate and no full/partial future assignment remains. Under-five-win teams can finish in championship week. Bowl completion, playoff elimination and national-final completion retain their existing safeguards.

## Actual final honors and signatures

Annual award records and postseason All-American records must have the current native season index. The Heisman trophy comes only from an explicit HEISMAN award, never the watch-list leader. Coach awards retain their recorded season school even if the coach subsequently changes jobs. Unknown award brands use verified category descriptions rather than guessed trophy names. Two distinct defensive awards with the same generic label/recipient combine into a multiple-honors report; duplicate records do not inflate the count.

National/first/second/freshman selections are separated from conference selections, with the highest national honor per player and school summaries counting unique recipients. All awards are final-season honors, not reused preseason projections. Official teams and selected athletes react; existing replies remain parent-dependent and use the 33% gate.

Signed recruits are read separately from soft/hard verbal commitments. The leading school must still be unique and corroborated on its recruiting board. Signed targets no longer create scholarship-offer stories. High-school/JUCO signers can mention letters of intent; unknown/transfer classes use generic signing paperwork. Every five-star gets an individual candidate, four-stars 60%, lower-star signers 20%, deterministically. School summaries report the whole verified signed group, star counts and a current native class rank when supported. CPU/user conditions are identical.

## Coaching carousel

Only the active hiring evaluator's opening/offer lists are consumed, with explicit college HC/OC/DC roles. The reader does not call hiring functions or modify offers.

- A pending offer is reported as an offer, not an acceptance or hire; at most two candidates per open role receive individual stories.
- A current coach's offer is identified as a retention offer.
- A filled opening requires selected coach == actual current role holder before a hire/retention announcement. Retention additionally requires an accepted offer.
- Resolved stale openings and pending offers on already-filled jobs are suppressed.
- A fired-reason opening whose old coach still occupies the role is a pending change. Removal from the role supports the completed departure wording. Retirement/pro/job-change/contract transitions remain distinct.
- Raw legacy “fire reported” flags alone are not evidence of a current firing.

Confirmed decisions use an edition ledger that carries through phases. Same-edition refreshes preserve the story; later weeks do not repeat the announcement. Retracted same-edition facts are pruned. New hires/awards/signers remain distinguishable from earlier pending stories.

## Validation

201 Node tests cover waiting/selection boundaries, partial assignments, slot conflicts and unpublished results, issued awards versus watch lists, final honors, signatures versus commitments, publication/rollback/phase continuity, firing/hire/retention/offer distinctions, stale queues, archive corrections and native normalization. Native unit tests plus the actual 19-edition catalog validate in every dynamic scope. MMC registration, payload-tamper checks and installed verification use the existing checks.

The read-only real-data capture has 24 annual award records, 899 postseason All-American/conference selection rows, 1,621 signed recruits, 195 hiring openings and 448 offer records. Not all queue entries are new public decisions: resolved/renewal/conflicting states are filtered. The preview contains conditional bye paths, final awards, individual signers/class summaries and pending staff changes/offers. The native roster still holds many PendingFire coaches, so these are deliberately not reported as completed firings.

Remaining live checks: in-page Week 17 honors/signing/bracket presentation, the corrected Week 16 archive, actual first-round completion/quarterfinal assignment and later accepted coaching offers. No simulation or save records are written.

Live deployment: v76 is installed and active in the existing game process. Four history files and four BYU saves were checksum-backed up; history migration also matches. The real Week 17 publication has 3,707 stories / 30 For You posts, 432 individual signing posts and 138 class summaries. The waiting-week correction affects 157 retained posts and removes standings. The user confirmed the BYU Missouri-Iowa winner path, signed posts, Week 16 waiting news, scrolling and Back. Actual later accepted coaching offers and round advancement remain progression checks.
