# Active-Dynasty feed candidate

## Runtime access

`LiveTables.h` follows the current career session pointer and its active runtime table context. It gates the supported session/context/table vtables, bounds every process-memory read, decodes packed integers/enums/strings/references and reference arrays, and checks captured table blocks again before accepting a snapshot. Free-list rows are excluded. Runtime references are translated through the context's serial remapping and table catalog. No game methods, field setters, record-retain functions, save APIs, or simulation effects are called.

The observer samples on a background thread using `ReadProcessMemory`. It copies native data rather than keeping game-owned records alive. The career flow must be active and not advancing. Two matching full captures are required before generation; the session/league/season/week/stage identity is checked again after generation. A context or edition change invalidates the prior pending UI feed. The page uses an immutable snapshot until reopened.

Bindings are specific to the inspected game executable. This is a development DLL loaded into an already-running Dynasty, not a packaged universal release.

## Publication and midweek news

The shared normalizer consumes either the native record adapter or the diagnostic save adapter. `runtime_lifecycle.mjs` stores history by league, controlled team, season, and phase. Its weekly editions use the publication week, include prior-week recaps and current-week developments, and retain deterministic story IDs. All Posts remains curated; dedicated scopes retain their full qualifying stories.

Offers and commitments use observed differences. Native scholarship status `New` means a current-week offer and is included alongside carried status `Offered`; moving from `New` to `Offered` does not create a second event. The first live offer test exposed that filtering only `Offered` omitted all three new user offers; the adapter and regression coverage now include both states. Initial offers seed a baseline quietly; midweek discoveries become current-week stories and survive repeated observations without duplicates. Existing commitment-week evidence is retained. Injury status updates and midweek recoveries use observed injury episodes and the game's injury metadata. Completed current-week games replace their upcoming previews and use current-week wording for player performances.

Loading an earlier week drops future editions from the active history branch. Replaying to a later week generates from its newly observed facts. Same-week rollback prunes offer and commitment events absent from the active state. Poll and Heisman posts reflect the latest authoritative state; this candidate does not keep an event-by-event timeline of every intermediate poll or injury transition. It observes only while loaded; it cannot reconstruct exact midweek events that happened before observation.

Generated JSON/history are mod-owned caches. Reading or writing them never requires saving the Dynasty. The external save parser and schema are only needed for diagnostic comparisons.

## Verification

- The native reader captured 119,646 records from the active Week 8 Dynasty with read-only process rights.
- Team facts, game/stat facts consumed by templates, Heisman entries, recruiting commitments, and offers were compared with the save reader. All 122 generated stories matched in body, category, and avatar selection. Runtime can contain additional unused/unaffiliated player rows; raw record dumps are not expected to match save serialization byte-for-byte.
- 29 Node tests cover content/curation and runtime lifecycle, including week rollover, an unsaved offer and commitment, current-week game completion, midweek recovery, deduplication, earlier-week rollback/replay, and cross-identity isolation.
- Native UI/build tests pass with the active reader included.
- The user verified the live Week 8 feed, USC recap, both dropdowns, and scrolling. An actual unsaved recruiting event and a real subsequent week advance remain pending.

## Remaining limits

The observer uses stable state rather than a native completion-event hook. Its nominal three-second sampling and second-capture requirement introduce a short update delay. A save restore with identical observable facts is indistinguishable from the same timeline; changes are reconciled from the facts that remain present. Broader voices, depth-chart/NIL/transfer stories, awards, postseason phase archives, and the 1.0 analytics/fog integrations remain future work.
