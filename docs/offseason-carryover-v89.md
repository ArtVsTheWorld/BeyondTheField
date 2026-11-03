# Offseason capture and preseason carryover — v89

The native reader now ticks before, and independently of, News UI readiness. A cold launch at Training Results or Encourage Transfers can observe the loaded Dynasty without a Team tab, Social Media page or native news layout. UI entry remains gated until its verified assets are ready. Native capture remains read-only and requires stable observations; the existing code/ownership guards and capture budgets remain intact. There are no new UI hooks, hub descriptors or save writes.

## Calendar

| Phase | Native offseason week | Coverage |
| --- | --- | --- |
| Season recap | 0 | Championship recap and season review |
| Players Leaving | 1 | Departures and portal entry |
| Offseason Recruiting 1–4 | 2–5 | Portal, unsigned prospects, draft results in week 2 |
| Second National Signing Day | 6 | Final recruiting and pre-training baseline |
| Training Results | 7 | Background development comparison and roster baseline |
| Conference realignment / Encourage Transfers | 8 | Background alignment and roster reconciliation |
| Next Preseason | New season, week 0 | Publish supported carryover alongside preseason coverage |

Native stage labels are read through their enum value codes. They supplement the verified week calendar; stale offseason labels during preseason are ignored. The live schema identifies Training Results as stage code 8, National Signing Day as 7 and final Offseason as 9. These are stage codes, not the zero-based offseason weeks above.

## What persists

`RuntimeHistory/<league>/<user-team>/offseason-ledger.json` sits outside the year/phase folders. Atomic replacement preserves it across year rollover, restarts and renamed manual saves. The installed runtime history, including this ledger, must be migrated during upgrades. Data is scoped by native league identity and user team; the most recent three year keys are retained. The sidecar changes no Dynasty table or save structure.

- **Training:** Capture private before/after attributes for actual roster records. Match native row, name, presentation identity when available, team and position. A jump of at least five points in one relevant skill, or three in two, qualifies. Stories describe football development without exposing ratings. Keep at most two development reports per program, with an occasional player reaction. If the final signing-day baseline and Training Results are observed, use training attribution; a broader observed interval gets offseason attribution. No baseline means no invented improvement.
- **Encouraged transfers:** Reconcile the roster during the actual final stage. Exclude known drafted players and ordinary graduating seniors. A same-player team change supports departure; a deletion observed within that stage supports a roster update. Missing or reused records only at rollover do not establish a departure. Publish from the roster-review perspective without asserting the coach forced a player out. Mention the portal or a destination only when supported by native data. A verified departure can survive later record deletion; returning to the original roster removes it.
- **Conferences:** Compare captured membership and native conference identity. Report individual moves, and group a same-conference rename once. A cold start can compare a unique prior-year conference history row with the current alignment, using cautious last-year/this-year wording. Team replacement and case-only name changes do not become realignment stories.

Loading an earlier phase/week prunes future observations. Reconstructed skipped-week editions cannot seed offseason facts. Refreshes in the same preseason retain stable event IDs and wording; training/departure events do not repeat during the hidden stages themselves. The new stories enter the normal scopes, category filters, editorial budgets and attached-reply policy.

## Verification

308 Node tests pass, including 25 carryover checks for lifecycle, persistence, rollback, identity reuse, graduates/draft exclusions, missing baselines, position relevance, conference renames and historical fallback. The native DLL builds with warnings as errors and passes the existing UI/catalog checks. The expanded reader captured 105,974 records from the loaded BYU preseason 2027 Dynasty read-only, including private attributes and native stage metadata. Its fresh ledger correctly produced zero unsupported carryover claims; the completed training period predates this feature and cannot be recovered from that capture alone.

A copied-history replay and native catalog decode validate the current actual data separately from the installed history. Full live progression through signing day → training → final roster review → next preseason remains a controller test for the next cycle; no live advance is performed by the build process.

The user subsequently confirmed that v89's preseason feed and controls work. The live hidden-stage/year transition remains the next validation checkpoint.
