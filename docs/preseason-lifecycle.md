# Preseason and lifecycle candidate v67

## Story evidence

| Family | Required evidence |
| --- | --- |
| Preseason poll | Native MediaPoll_CurrentRank 1–25; AP label |
| AP/Coaches comparison | Both public ranks 1–25, differing by at least six places |
| National/conference honors | Current-year Season PlayerAward in AllAmAwards, supported ALL_AM_*_PRE type, actual player/team membership and conference reference |
| Honor-based outlook | Distinct current national preseason honorees per team |
| Team hype / fan mood | Actual program identity, native nickname/hashtag; mood is fictional authored flavor |
| Player camp / anticipation | Healthy roster player; native personality with secondary QB restraint |
| Opener | Earliest unplayed current-year regular-season game and actual opponent |
| Recruiting watch | Native Top10/Top5/Top3/Battle recruit stage, rank 1–100, no known commitment |
| Scholarship offer | Observed native scholarship change; preseason does not invent offers |
| Title futures | Supported actual rosters, same read-only roster aggregation as spread model; explicitly fictional estimate |
| Schedule gauntlet | At least two preseason AP-ranked opponents in one four-week schedule window |
| Poll/model debate | AP versus fictional title-model ordering differs by at least eight places, at least one in top 15; fan reply attaches to actual opinion |
| Conference talent map | Actual conference records and current native preseason All-Conference selections; distinct players and tied leading programs counted |

62 new variants in 24 families bring the executable pack to 339 variants. Templates still obey 280-code-point and 512-byte native budgets. Missing facts or oversized names suppress a variant; no values are cut off. CPU/user/TeamBuilder programs share eligibility. Model prices are not actual sportsbook markets or game probabilities. No actual rating/hidden Rank is presented as public knowledge.

## Public poll selection

AP is the default and always applies in preseason. During the active regular/postseason, a complete set of 25 distinct native CFP ranks (one each 1–25) selects CFP as the public primary poll. This is a conservative data-derived publication signal, not a hardcoded Week 10 boundary; live first-CFP release testing is still required. Partial or duplicate CFP data does not switch the feed. Coaches appears only in explicit comparisons. The first observed CFP edition does not compare its positions against the preceding AP edition. Pregame snapshots retain their original public poll basis for later upset stories.

## Blank Week 0 diagnosis and correction

v64's new BYU/TeamBuilder regular-season Week 0 capture normalized successfully, but entering News rejected the cached dropdown model at offset 0x24a58. The native CFM model allocation had changed across the phase transition. Navigation had already entered News, and returning false for the page-data request left only RT visible and unresponsive controls.

v67 validates every expected model byte at the current address and reacquires the supported APT model when the unowned cached allocation no longer matches. It requires exactly one fully matching allocation, has a bounded lookup, and refuses foreign/partially patched data. It performs model readiness checks before News navigation; failure completes through native no-action navigation. A late dropdown setup failure no longer suppresses native page data. News-screen checks still occur after the native navigation loads that asset; the screen is not assumed to exist in the hub.

Verified menu hooks now install before the worker waits for active Dynasty assets, catching initial CFB menu construction. UI-dependent hooks use atomic readiness gates. The managed adapter's fixed 20-second process-age delay is removed; exact executable/vtable/asset checks remain. The observer still waits for a stable active snapshot before publishing. No native UI methods run on the background observer.

## Verification and limits

109 Node tests pass, including new publication/poll/model/honor/recruiting coverage. Native tests cover early selection, stale model replacement, foreign ownership rejection, safe pre-navigation failure, restoration and existing UI/controller behavior. MMC package tests validate registration, payload tampering, path bounds and editable configuration without injecting a game.

The four BYU/TeamBuilder preseason/Week 0 saves were backed up and SHA-256 checked before recovery work. Legacy save parsing is not the production reader and could not reliably resolve optional TeamBuilder city references. Native runtime capture remains the only feed source. The v66 first-hub appearance passed but entry failed. v67 has published the live preseason edition successfully; the user confirmed preseason posts and normal Back navigation. Reload and Week 0 recovery checks are pending.

Publication history remains phase-isolated, so preseason and regular-season Week 0 cannot collide. The RT picker lists observed weeks only within the active phase; a combined phase-aware archive picker is later work.

## v66 entry failure and v67 recovery

The first-hub button appeared immediately in v66, but clicking it while uiReady was false silently returned from the native navigation callback. The native caller had already begun a transition, leaving pending state. The user could back out to the main menu but later navigation/loading stalled. Stop returned success; all four BYU preseason/Week-0 saves remained byte-identical to the verified backups. With Dynasty Enhancer disabled, the preseason save opened normally.

A read-only probe proved the old e1eac10 object is only 0xd0 bytes (native destructor allocation size), so its +0x290 read crossed into a neighboring allocation. Earlier successful sessions did not validate that ownership assumption. The current binding is native front-end ServiceGlobal fa519b8 / ServiceVtable baa8998, service+468 CareerManager bce9b08, service+470 UI context bd7a538, service+460 core owner matching CareerManager+20, and CareerManager+238 database. The supported shared database's unique child still requires exact vtable/parent gates. The service, manager and database ownership are checked again after capture.

The reader also encountered a native Award[] with one row and 8100 reserved words. Array-only reserved capacity now allows up to 16384 words; the actual populated array length remains capped at 4096 and total byte/record limits are unchanged. The unhooked live preseason capture contains 73770 records, 600 valid preseason honors, 25 AP ranks, 25 Coaches ranks and no CFP ranks. Both CPU and user preseason content are generated from this capture.

v67 resolves unready navigation info through native DO_NOTHING and completes failed entry requests through that same inert action. It no longer promises News and silently returns. UI readiness waits only for supported assets, independently of the data reader. Preseason analytic outlooks no longer inherit generic replies claiming current-season production. Native fixtures cover actual service ownership, inactive/foreign context rejection, array-only capacity bounds and navigation completion. The user confirmed the live v67 preseason page, Preseason 2026 choice and normal Back return. Native logs show the custom dropdowns, scrolling and layout restored on exit. Phase-transition and cold-launch/reload checks remain pending.
