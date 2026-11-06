# Dynasty topbar currency source

`Tools/build_currency_topbar_ui.py` generates the separate
`Source/CurrencyTopbarUiPrograms.h` bank. Integration uses
`recruitingfog::currencytopbarui::programs()` and enables the bank only for the
Dollar Values option.

The same header exposes `currencytopbarui::recruitingPrograms()` as a separate
bank for the recruitinghub AST. Keep that bank dispatched even when Dollar
Values is Off so the board-row adapter can restore an owned cached fit. Its
internal option literals still receive the actual Dollar Values setting; the
other two recruiting callbacks are no-ops while Off.

The current MMC cache's Presentation_Common collector maps
`common/ui/art_screen/infocenter/infocenterart.ast` to GUID
`4d05f3a1-2564-b8c4-486b-aa5e34d60ad4`. The private extraction is stored in ignored
`Evidence/PlayerFog/Gaps/current-infocenterart.ast`.

That asset embeds `art_screen.infocenter.CareerInfoModule`. Its SetExtraInfo
definition is at `0xBB90`, body size 5,040, one argument, 20 registers, flags 41,
FNV-1a `0x5F96F78C7A24561E`. The callback's native optimized member path reads
`this.mData.ExtraInfo.remainingProgramPoints` and passes the formatted result to
`mcProgramPoints.SetLabel`. This is a dedicated text widget, so the generic
SwappableAndTextItem currency-icon adapter does not cover it.

The suffix reads the merged native ExtraInfo only when `isCoach` is true. It
changes the displayed `mcProgramPoints` label using the common $4K-per-point
formatter. It leaves remainingProgramPoints, CoachPoints, StaffPoints, coach
level, job security and all native layout/style objects unchanged. No additional
registers, timers, polling, provider calls or native hooks are needed.

Money labels retain the game's currency icons and omit an extra textual currency
symbol: 75 points displays as `300K`, 250 as `1.0M`, and zero as `0`.

`Tests/currency_topbar_ui_test.py` executes the suffix with zero, float/string
zero, nonzero, large, negative and invalid values; tests default-Off and noncoach
no-ops; rejects already formatted dollar strings; preserves the source fields;
and verifies native member patterns, frame metadata, complete body fingerprint
and deterministic generation. Live attachment and visual spacing remain to be
checked.

Recruiting coverage uses the current recruitinghub asset GUID
`c1c94d9d-8708-a58e-7969-e68b31b6a610`, extracted read-only to ignored
`Evidence/PlayerFog/Gaps/current-recruitinghub.ast`:

| Callback | Numeric source | Display target | Native frame |
|---|---|---|---|
| `HubScreen._RefreshStats` (`0x4D58`) | `GetRecruitInfoData.programPoints`, cached unchanged as `mPreviousProgramPoints` | `mWalletProgramPoints` | argc 0, regs 7, flags 41, size 314 |
| `PlayerListItem.Draw` (`0x2C518`) | `mData.ExtraInfo.CurrentNILOffer` | `mcPoints` | argc 0, regs 18, flags 25, size 4,524 |
| `TotalHours.Draw` (`0x37668`) | `mData.ExtraInfo.OfferPoints` | `mcOfferPoints` | argc 0, regs 5, flags 25, size 419 |

The remaining-budget wallet is independent of Targets, Hours and Scholarships.
The small scouting/recruiting offer wallet is independent of MaxHours and
BonusHours. Their native numbers and ratios remain intact. After changing the
offer text, the suffix repeats only the existing offer-side width/position
formula so its background follows the new label. The hours wallet is untouched.

The board's `PlayerListItem.Draw` native formula is
`mcPointsIcon._x = mcPoints._x - mcPoints.GetWidth() - icon.GetWidth() - 4`.
It runs when the raw offer invalidates, before dollar text is substituted. A
longer `160K` label therefore previously expanded leftward into the old icon.
The native initialization uses a 430-pixel row, a name width limit of 260, a
right-column start (`mCoordFarLeftIcon`) of 332, a 26-pixel program-points icon,
and a right-aligned points font. The name and points container share the same
parent; the label and its icon are children of that points container.

The board suffix now keeps the native label's right anchor and restricts its
text with native `RESIZE_SCALEDOWN` to the remaining money column. The left
boundary is the greater of the native right-column start and the actual
rendered name's right edge plus eight pixels. The icon occupies that boundary,
then four pixels of padding precede the bounded right-aligned text. Pinning the
icon to the column avoids depending on a deferred formatted-text measurement.
Only resize/width/line-count style fields change; native focus colors, the
currency icon, hours, names, ranks, flags and all source values stay native.

The row caches its own source, layout and applied display. An unchanged-On draw
performs no label/style setter, style clone or layout invalidation. A changed
amount, layout or native override refreshes the fit; Off restores the numeric
label and owned style fields. For the same raw source it restores the captured
native icon baseline, adjusted only by exact text-anchor/icon-width deltas;
no just-restored text measurement is required. A changed raw source normally
arrives with the native offer invalidation's refreshed icon, which remains
authoritative. The original native formula remains a fallback for a changed
source without native dirty rendering. A fresh default-Off row receives no
style or position changes. There are no new callbacks, timers, polling loops or
register-frame expansion.

`Tests/currency_recruiting_ui_test.py` verifies all three sources/targets using
native method bytes, frame metadata and whole-body hashes. It executes zero,
nonzero, signed, invalid and already-formatted values, verifies symbol-free
labels, and checks unchanged counters, source amounts and offer-wallet geometry.
It also covers the native board column bound, long names, selected-row colors,
50 setter-free unchanged redraws, a renderer with unavailable formatted-text
and just-restored raw-text metrics, stale deferred raw metrics with exact anchor
and icon-size delta restoration, amount/geometry refreshes and same-instance
On/Off/On restoration.

Read-only inventories of the local Dollar Sign Dynasty Point Icon fbmods found
only the `icon_currency_programpoints` image resource and its texture chunk.
Those packages do not modify currency amounts or formatters. The duplicate
formatting defense is still necessary because the Dynasty Enhancer C++ grid
adapter can already supply dollar display strings to the generic UI cell.
