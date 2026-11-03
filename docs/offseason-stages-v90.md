# Native offseason identity correction — v90

The live ULM test found a real gap in v89's calendar fallback. The second-signing-day milestone has week 6/stage 7, Training Results has week 7/stage 8, and the final realignment/Encourage Transfers milestone has week 9/stage 9. v89 recognized training by its native label but did not recognize the generic final "Offseason" label. Its week-only fallback returned no stage at counter 9 and deleted the current cycle's ledger.

v90 uses the native stage ID to distinguish pre-training stages 1–7, training 8 and final roster/alignment 9. Legacy snapshots without those IDs retain their older calendar fallback. Unknown offseason stages preserve existing observations; only a genuine earlier non-offseason phase prunes future data. Rewind cleanup uses stage identity, and training attribution recognizes the actual signing-day stage baseline.

312 Node tests pass, including regressions for varying week counters, final counter 9, unknown-stage preservation and native-stage rollback. Native build/UI/catalog checks pass. The UI implementation and content wording are unchanged from v89.

## Actual ULM evidence

All 29 ULM milestone/manual/autosave files were copied and checksum-verified before inspection. A diagnostic read-only extraction of the signing-day, training and final-stage save copies recovered a 6,344-player roster baseline and 2,078 qualifying training changes league-wide, including 11 ULM players. All 16,257 extracted player row/name identities matched the active runtime. Conference membership extraction covered 138 teams. No Dynasty save was modified or loaded by the diagnostic.

The broad legacy save normalizer encountered an unsupported historical reference. Recovery therefore extracted only the required identity, roster, private attributes and conference membership records from the copies, with league and native player identity checks. This is a one-time diagnostic repair, not a new save-driven production feed. The live worker continues to read the active Dynasty only.

The recovered ledger records the final native stage as Encourage Transfers and retains the signing-day baseline and development facts. At the first inspection there were no observed roster-review departures or conference moves. A copied next-preseason projection selects WR Dalen Huston and WR Marcellus Jackson for ULM's two development reports. These are projected publication candidates, not a claimed live preseason result.

Remaining live check: make identifiable encouraged-transfer/conference changes, verify background capture, advance to next preseason, confirm factual carryover and reload persistence. The current cycle uses recovered milestone evidence; a future unassisted full-cycle capture remains a separate validation case.

A replay using the actual native snapshot, recovered ledger and copied history passed export and native decoding for all 31 ULM editions and every scope. The initial hot-loaded DLL reached the reader's existing child-context search bound in the long-running session; a clean MMC/game launch was requested without increasing those bounds. The user confirmed no encouraged transfers or realignment changes had been made yet, consistent with the zero-change observation.

The clean MMC launch succeeded. The user returned to the unchanged ULM final-stage hub; v90 captured the new native session and published 941 stories at native week 9/stage 9. The persisted signing-day baseline, 2,078 league-wide development facts and 11 ULM development facts remained intact. The observer and projected preseason comparison both reported zero roster-review departures/conference changes before user edits. Actual edits and their next-preseason publication remain the next checkpoint.
