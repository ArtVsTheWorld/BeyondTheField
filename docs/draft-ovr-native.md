# Draft Results OVR

The custom Draft Results table and National/conference filters were cancelled. The active replacement is a minimal OVR display adapter with exactly two callbacks. It adds no columns, assignments, data reader, worker, native getter hook, filter, sidebar or input behavior.

`Tools/build_draft_ovr_ui.py` verifies the exact `PlayersLeavingStrategy._GetTeamModule` definition in the hub asset (descriptor0x49a98, original body207 bytes, hash0x9489b6fcc2ab8c9c). A prefix sets its existing provider's `mDEDraftOvr` marker to `this.mIsDraftClass === true`. This also clears an old marker if that provider is reused for ordinary Players Leaving. The full original body then executes unchanged. The shared CFM `UcmSpreadsheetProvider._GetColumnData` is deliberately untouched.

The second callback is shared `SpreadsheetProvider.GetRowData` (descriptor0x108a10, original72 bytes, hash0x692f2d8e6c46500d). Its first69 native bytes execute unchanged. A suffix replaces only canonical0–100 OVR display text in requested column4 when the provider's Draft marker is exactly true, then returns the same native array. It retains `value`, opaque keys, styles, selected/gray coloring, row order, results and all other fields. Unknown ratings and non-OVR cells remain unchanged.

The generated `Source/DraftOvrUiPrograms.h` exposes `draftovrui::strategyPrograms()` and `draftovrui::rowPrograms()`. Both retain exact native register frames (3 and6); extra scratch values use function-local variables. Root gates the two banks on Roster Fog so turning it off restores original native bodies. Grade labels use the shared selected scale. The adapter preserves native font colors rather than overriding selected or disabled rows.

Verification:

```
python Tools/build_draft_ovr_ui.py
python Tests/draft_ovr_ui_test.py
powershell -NoProfile -ExecutionPolicy Bypass -File Build/Run-DraftFrame.ps1
```

The UI test executes the original native strategy body and row-data prefix, verifies all101 ratings across four scales, and checks that the native calls, columns, scalar values, keys, styles and selected/gray states survive. The C++ fixture proves that both generated callbacks attach after native frame allocation. Live acceptance should check stock Draft Results OVR letters, team filters, sidebar, scrolling and Back, and numerical OVR after Roster Fog is disabled. No custom Draft filters should appear.
