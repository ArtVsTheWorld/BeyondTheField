# v72 account artwork, filters and recruiting continuity

The installed native DLL and MMC adapter are Dynasty Enhancer v72. Source and gameplay access remain read-only; only the mod's own JSON feed history changes.

## Requested presentation

- FanDuel Sports becomes **CanDuel Sports**, handle **@CanDuelSports**. The existing native C coin remains its image.
- Player-authored teammate references use the teammate's given name. Media retain full names, and athlete display names and persistent handles are unchanged.
- Players and Recruits are separate LB/RB account-type filters. Recruiting remains the subject filter covering offers/commitments from all account types. Replies inherit the parent's filter eligibility.
- Recruit StateRank and PositionRank are read directly from Recruit records. Reports vary between national, state and positional context. Zero/unavailable ranks do not become No. 1 claims; internal Player ratings are never used as recruiting ranks.
- Requested metadata changes also appear when viewing archived editions. This refresh preserves IDs, likes, publication dates and view membership. The only prose changes in that presentation pass are requested teammate given names and the renamed model's handle references.

## Exact native avatar bindings

| Account | Native asset | Library | Value |
| --- | --- | --- | --- |
| ESPNCFB | dynas_general_TeamNeed | 34 | 1096 |
| David Ellison | nilcp_Generic_0003_C_T0133_M_2_4 | 5 | 3 |
| Chris Maddox | ucp_narrative_malereporter3 | 62 | 235 |
| Tina Brooks | ucp_narrative_femalereporter4 | 62 | 228 |
| Marcus Bennett | ucp_narrative_HSmalereporter2 | 62 | 243 |
| Jake Whitmore | ucp_narrative_malereporter4 | 62 | 236 |
| Beat reporters | thf_<school> | 61 | Exact canonical-name mapping |
| After Dark fans | tma_<school> | 87 | Exact canonical-name mapping |
| Barstool fans | tlsec_Secondary_<school> | 89 | Exact canonical-name mapping |
| Official teams | tlow_<school> | 64 | Exact canonical-name mapping |

These IDs come from installed ImageLibraryRefTable metadata. They are not assumed to align: Akron primary/on-white ID 1 maps to flat helmet ID 2. Coverage is 149 helmet mappings and 138 mascot mappings; missing alternatives fall back to the primary logo.

East Point exposes primary ID 600 and secondary ID 632, with a nonempty native secondary-logo source. Its tertiary source is empty even though SMALL_ALT repeats 632. Fan and beat accounts therefore use the registered secondary. Other TeamBuilder teams require their own populated source and an allowed registered alternate; no replaced-school mascot/helmet is substituted.

## Week 4 recruiting gap

The Week 2 to Week 4 sim had no observed Week 3 recruiting snapshot. Previously, the immediate-prior-week comparison was unavailable, and Week 4 quietly seeded most commitments/offers. Only three commitments with useful native week values became visible.

The runtime now retains the last actual recruiting observation across a gap. Newly observed changes publish in the current edition as explicit catch-up reports (for example, 'since our Week 2 report'). Their exact event week remains unknown. The reconstructed Week 3 edition still contains only the supported completed-game stories approved by the user. It is not used as a recruiting/injury baseline.

For this Dynasty, a retained full native Week 4 capture exactly matches the stored Week 4 commitment/offer observations. The explicit archive repair adds **636** recruiting posts, retaining every original story and all later Week 5/6 observations. It does not use today's Week 6 commitments to invent Week 4 news. Covered original recruiting threads are left intact rather than attaching replies to a differently authored replacement parent. The first ever observation of a Dynasty still seeds recruiting quietly, and the scholarship-post chance remains 20%.

The stored recruiting observations include the repair version and catch-up provenance. Reloading or adding midweek news cannot duplicate or reroll those changes. Rewinds still prune future observations and withdrawn offers remain excluded.

## Verification

137 Node tests pass. Native checks include independent Player/Recruits selection, reply dependencies, category wrapping and existing menu/UI ownership guards. The preview native decoder validates eight editions and every dynamic scope. MMC registration, launch callback and protected-payload tamper checks pass; the installed adapter also validates. The live v72 worker published Week 6 directly from memory with 3,349 stories and 30 For You entries.

History was copied and checksum-verified before installation; the prior runtime/history and managed DLL remain in a versioned local backup. Native avatar rendering and the user-facing filter/Week 4 catch-up check are pending in-game confirmation. Fresh v72 MMC cold launch remains untested in this running session.

## Next validation

1. Verify v72 images, separate Players/Recruits filters, Week 4 catch-up stories and controller navigation.
2. Continue the existing season test through first native CFP publication, conference championships, bowls/playoffs and offseason/year rollover. Check archives, correct poll basis and recruiting continuity at each boundary.
3. Audit repeat frequency, team relevance and identity persistence from those real editions. Add further recruiting features after lifecycle issues are addressed.
4. Integrate player analytics grades and ratings fog, then validate all three components together before 1.0.
