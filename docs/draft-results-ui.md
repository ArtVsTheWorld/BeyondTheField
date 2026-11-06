# Draft Results browsing

> Retired experiment: the custom draft table/scopes are disabled and are not
> included in the production dispatcher. User testing found hangs after filter
> changes. Current builds keep stock Draft Results and only adapt its OVR
> display; modeled picks/NFL teams remain Social Media content. The code and
> design below are retained as research history, not installation instructions.


**Retired experiment — 2026-11-06.** The user withdrew the custom table,
National/conference filters and added columns after the live navigation failures.
The current runtime restores stock Draft Results and keeps only its OVR display
conversion. The experimental worker, native getter hook and custom UI banks are
not compiled into the active DLL; the exporter is excluded from new packages.
The material below records the retired implementation and its evidence.

This adapter adds National, actual-conference and school filters to the native Draft Results screen and applies the shared OVR fog policy. It displays actual draft rounds only. Modeled pick numbers and NFL clubs remain solely in Social Media, as requested after the p88 test. It does not alter player records, draft outcomes or saves.

## Data and lifetime

`Tools/export_draft_results.mjs` accepts an existing read-only runtime capture and emits one bounded JSON view atomically. It reads the actual `Conference.TeamSlots` and `Conference.Divisions[].Teams` membership. National comes first, then actual conferences alphabetically, then schools alphabetically. It never assumes that a named school belongs to a real-world conference.

The actual-only view allows0–1024 drafted players and at most300 scopes. It reads actual drafted players/rounds independently of Social Media, archive history or simulated NFL assignments. Canonical order is actual round, school, name and player key; no modeled pick ordering is involved.

The format2 JSON view explicitly marks `actualRoundsOnly=true`. Its native identity uses unsigned LeagueID bits, including when the source Dynasty stores a negative signed LeagueID.

`Source/DraftResultsRuntime.h` validates identity, unique player keys, actual rounds, scope membership and bounds. It publishes an immutable view. The `DE_DRAFT_2` wire format is tab/newline-delimited, with ten fields per player row and control characters rejected; no `eval`, executable text or dynamic script compilation is involved.

The UI thread only checks active identity, acquires the ready shared pointer, and adds the string to the native `PlayersLeavingFlow.GetTeamInfo` response. Capturing, subprocess work, JSON parsing and disk access belong to the existing worker. The request runs even when Social Media is disabled. The worker rechecks active session, LeagueID, season and phase before publishing. Stale views must not be injected after a Dynasty load or year rollover.

## Native integration

The name-verified native binding is in `Source/DraftResultsBinding.h`: table RVA `0xc751ea0`, slot `0x60`, function RVA `0xa0db8e0`. Its ABI is exactly `void* __fastcall(void* self, void** out)`. The getter forwards first; only its returned object receives `DEDraftBoard`. Loader ownership and32-byte prefix validation remain mandatory. Offline proof is in the private `Evidence/PlayerFog/Draft/get-team-info-binding.json`; a read-only live check in `get-team-info-live.json` confirms that exact pointer and all32 prefix bytes in PID22004. No getter was invoked in that check.

Merge these generated custom program groups into the corresponding native script assets:

- `draftui::hubPrograms()` → `common/ui/node_cfm/hub/corenode.ast`
- `draftui::cfmPrograms()` → `common/ui/node_cfm/corenode.ast`
- `draftui::comPrograms()` → `common/ui/node_com/scriptpod.ast`

The generated programs contain only custom bytecode, original-body hashes and zeroed regions. Existing verified runtime copying supplies native fallback bodies. Each common provider prefix requires a board attached to that exact provider instance; it cannot affect other roster/stat tables. Each strategy change also requires `mIsDraftClass`, leaving ordinary Players Leaving intact. All22 callbacks preserve exact native register counts and flags. Extra scratch values use ordinary AS2 function-local variables, because provider callbacks can arrive after native frame allocation. Custom browsing activates only after the actual common-provider count callback and CFM column callback execute their adapters on that instance.

The LT dropdown retains the native control and navigation. It owns its National/conference/team scope keys, preventing synthetic scope IDs from reaching the engine's team-only filter. The six columns are Name, POS, Year, School, OVR and Result. Result retains the actual native round. OVR uses the shared fog/grade/color policy; other numeric facts remain numeric. Filtering preserves canonical actual-round order. General column sorting is disabled so custom column IDs cannot reach the native sorter.

The native team header and player sidebar are hidden for custom browsing. The School column identifies each row. Native `GetEntryInfo` expects a transient `Blaze::DynastyMode::PlayersLeaving::PlayerLeaving` DTO key. Captured persistent Player keys cannot identify that DTO, even if encoded in the native serial format. Custom row/color/selection callbacks therefore bypass native lookup and persuasion. Input delegates only to native filters and verified grid movement codes, preserves Back directly, and consumes card/persuasion/sort commands. Custom hints bypass the Ucm command helper. Custom navigation backup returns an empty object instead of converting selected keys or persisting synthetic scopes into a native team-only filter. Ordinary Players Leaving and pending native Draft Results retain original callback bodies.

If the board or provider validation is pending, the stock screen remains usable. A scoped display-only suffix converts native OVR cells, preserving native `value`, unknown sentinels and every other column. At most40 half-second retries replace the table in place when ready; there is no steady-state polling afterward. Scope changes rebuild on a nonlocked next-tick callback so the native dropdown selection can unwind first. Initial synchronous `SetByItemArray` events are ignored during construction. The empty flag is published before `ResetData` dispatches synchronous RowChanged events. Shutdown cancels retry/deferred work even before activation and clears owned active/wire/pending/building/applying fields and provider row markers.

## Verification

Offline checks:

```
node Tests/draft_results.test.mjs
python Tests/draft_results_ui_test.py
python Tools/build_draft_results_ui.py
```

`Tests/draft_results_runtime_tests.cpp` separately exercises C++ identity/shape guards and immutable publication. The JS test verifies actual-only records and actual custom conference/division membership. The UI verifier exercises0-,1-,224- and1024-row classes, scope defaults, stable row order, key lookup, reordered columns, unknown/malformed/pending fallbacks and rating-only conversion.

Pending live checks on a backed-up Draft Results milestone:

1. Open Draft Results with Social Media both enabled and disabled; ready data should appear without reopening.
2. Verify default user team, National, at least one custom conference and another school; inspect that scope membership and draft order agree with the capture.
3. Verify actual draft-round results against the stock class and no Pick/NFL Team columns.
4. Test OVR with roster fog on/off, all scales and colors off; retain actual round/year/weight/stat numbers.
5. Verify the unsupported player sidebar is hidden; test scroll, LT D-pad/stick navigation, dropdown Back and screen Back. A/Y should not open persuasion or a player card for custom rows.
6. Reopen ordinary Players Leaving, Roster and Season Stats to verify native fallback and absence of the custom columns.
7. Load a different Dynasty and advance a year; no previous identity's board may appear.

The p87 live attempt failed: hub callbacks activated, but provider callbacks did not attach because generated register counts expanded existing native frames. It displayed NO DATA, invalid sidebar values and stranded navigation. p88 proved corrected provider frames attach, but the full hub bank rejected the native HandleInput fingerprint. Its nested zero-body cancellation callback had loader-relocated metadata. The next candidate explicitly describes that exact nested header at body+0x240, nameRVA0x7eb20 and paramsRVA0x7eb28 using the existing verified normalization path. The complete original body hash remains required; unexpected pointers, pools or instruction changes still fail closed. Live acceptance remains pending.

The connected regression executes empty user team → National → conference, with synchronous `SetByItemArray`, `ResetData`/RowChanged and navigation-backup events. DTO, card and command-helper routes are poisoned. It models GetHints' real ABI (`r1=super`, local `this`), checks blocked A/Y/sort inputs, both Back paths and shutdown cleanup. The native Runtime fixture proves all22 callbacks attach with preallocated frames and both lazy and relocated nested metadata, and rejects altered instructions, names and pools. The updated actual-data audit passes all450 scopes across ULM2026–2028 with zero forbidden native routes and Back succeeding: `Evidence/EnhancementOptions/draft-real-ui-audit-actual-only.json`. This is supplementary offline evidence, not live UI acceptance.

The correction work and offline audit performed no game UI actions, injected getter calls, DLL loads or save writes. Root handles the next packaged candidate and user-driven live check.
