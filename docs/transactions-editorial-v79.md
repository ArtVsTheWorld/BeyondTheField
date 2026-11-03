# v79 (v78 content): transactions, editorial coverage and UI performance

## Transactions

LB/RB now includes Transactions. Reported coaching departures, hires, retention offers, accepted renewals, current contract terms, new recruit signatures and observed NIL compensation changes qualify. Roots come from analysts/ESPN or beats; attached replies stay regardless of voice. Fan speculation is not a standalone transaction. Recruit signatures also qualify for Recruiting.

The reader adds RecruitTarget.CurrentNILOffer, coach contract length/remaining years/consecutive-contract count and offered coach term length. A signed recruit must still have the unique winning school and recruiting-board corroboration. Its listed winning-board offer uses the user-confirmed $2,500 per point; it is described as an offer, not invented cash already paid. Existing CurrentNILCompensation supplies observed player increases/decreases. No brand partner, guarantee, contract duration or signing date is fabricated.

Transaction observations persist across publication phases and same-week refreshes. Initial installation seeds existing compensation and old signatures quietly; changed values can then publish without a save. Rewinds remove a retracted compensation change. A different player team cannot become an apparent pay cut. A coach renewal requires a signed contract plus increased contract count or years remaining. A silent same-price player retention without a distinct native completion marker cannot currently be distinguished from no transaction.

Coach length/offer terms are supported. The actual captured ContractSalary field is zero for all current head coaches, so dollar salaries are not published. Contract program/expectation points are not treated as money.

## Coverage and order

The user confirmed 5–20 means total posts discussing each program across all voices. The budget is 5 + rounded 15 × (0.65 brand exposure + 0.35 current public poll prominence), bounded at 5–20. CFP replaces AP when the verified public poll is available. A shared matchup consumes both teams' allowances. Replies count, require a retained parent and never create an extra hidden allowance. Genuine sparse/recovered data is not padded with fabricated stories.

Selection reserves a base of coverage per school, then admits varied high-priority stories and attached replies. The real Week 19 preview covers all 138 programs with 5–19 posts each; BYU has 17. This budgets the generated edition rather than just hiding most stories in a team's dropdown. Earlier stored editions retain their observations and prose; their derived views adopt editorial ordering.

Likes no longer affect placement in any JS or native view. Root ordering uses news priority with topic/account rotation; replies remain attached and use editorial order. Native selection preserves serialized order, applies category filtering before existing display caps and never re-sorts by engagement. For You remains a curated 30-post mix, National 100, conferences 60 and each team selection at most 20 cards. Earlier stored candidates remain available to category filtering before that cap.

Engagement version 4 uses native brand/public-poll reach, voice, deterministic variation and event importance. Ordinary posts cap at 5K; major events can reach 20K. Actual playoffs/title games, awards, huge upsets and ranked rivalries receive more attention than routine analytics/beat/fan/player/recruit posts. Related teams contribute reach, so a small school's upset is not limited to its usual audience. Replies remain 1–20% of parent likes. Engagement never enters the editorial or team-budget scores.

## Player references

Known player names receive a natural position label using explicit player/team context where names collide. Existing QB/RB/etc. or spelled-out position references are preserved; handles and longer embedded names are untouched. Player-to-teammate references retain first-name style with position context. Qualification runs before 280-character/512-byte validation, so facts are never truncated to force a fit. Existing historical prose is not relabeled using a potentially changed current position.

## Blank screen and performance investigation

v77 successfully published Week 19 with 3,404 stories while the game showed only the blue BYU hub background. No Social Media entry navigation was logged after the advance. All prior UI restoration callbacks had completed; stopping v77 did not restore the already-blank menu. Thus the evidence establishes a UI/navigation failure, not another failed news-generation capture; it does not prove the complete cause.

One problematic production path was found: hovering Heisman Watch could run a synthetic native-panel preflight and publish a retained hub model. First Social Media activation could repeat that diagnostic request. v78 restricts synthetic preflight to the explicit diagnostic build; normal hover is forwarding only and entry uses one genuine navigation transaction with the existing exact ABI/layout/ownership gates. A clean relaunch is needed to clear the already-broken session; a forward Bowl Week 2 → Bowl Week 3 replay remains the regression check.

Catalog replacement now retires old shared catalogs to a worker queue, avoiding large map destruction on UI adoption or while holding the feed mutex. Historical events remain in observation history but are omitted from duplicated native display payloads. On the same 21-edition real archive, the v77 native catalog was 101.7 MB, removing duplicate archive events alone reduces it to 39.0 MB, and v78 with current team budgets is about 36.0 MB. Worker capture runs below normal priority and backs off unchanged observations to eight seconds. Transition/midweek changes still need verified stable captures. Native entry logs include preparation timing for further live profiling. Asset lookup still uses bounded exact-byte ownership checks; no worker invokes native UI functions.

## Validation and remaining checks

232 Node tests pass. New checks cover NIL units/change/rollback, phase continuity, genuine signatures, contract term safeguards, Transactions/reply filtering, shared school budgets/CPU parity/no filler, likes-independent order, major-event engagement, position labels and compact catalog data. Native checks validate 21 real publication editions in every dynamic scope, preserve editorial order and apply categories before caps. All current named-player references are already qualified on a second audit pass. Current bodies remain at most 279 characters.

Eight BYU saves were checksum-backed up before ending the stuck session. Live clean-start, first hub hover/entry, Transactions, both dropdowns, bumpers, scrolling/Back and another advance require verification. Same-price player retention and coach dollar salaries remain limited by the available verified facts, rather than being invented.

A clean subsequent launch automatically loaded v78 through MMC and opened Week 19 with working scope changes. Entry instrumentation exposed 3.5–3.9-second preparation. v79 adds a first pass over the previously verified News asset allocation before the existing process-wide fallback; it requires a unique exact header and every screen patch fingerprint. Foreign/ambiguous candidates remain rejected. It also limits old team selections to 20 cards. First-time lookup can still require the full bounded search; repeated-entry improvement requires live timing verification.

Final deployment: v79 is installed and payload-verified. Seven runtime history files were migrated byte for byte and backed up, along with eight BYU saves. The game is left closed at the user’s request for their own testing. The final real Week 19 replay passes native decoding in all 21 editions and every dynamic scope. The source verification record separates preceding v78 live observations from the remaining v79 performance/rollover checks.
