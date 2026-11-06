# Program-points icon string contract

The generic currency label adapter accepts two exact native strings for the
program-points icon. It does not infer money from substrings, a similar icon,
or an arbitrary library.

* `ImageUtil.BuildFbImageString(assetId, libraryId)` returns
  `FBImageDrawHelper.GetFormatToken() + ":" + assetId + ":" + libraryId`.
  The formatter constructs this through the same runtime helper, without
  assuming the format-token text.
* `PendingOfferListItem.Init` constructs its `mcOfferValue` WidgetData value
  directly as `Icons.ASSETID_ICON_CURRENCY_PROGRAMPOINTS + ":" +
  Icons.LIBRARY_ID`. The formatter also accepts this exact legacy expression.

Both forms must refer to the current `shared_enum.fblibraries.global.Icons`
program-points asset and its library. Other currencies, swapped argument order,
other libraries and extra segments remain unchanged.

Native source proof:

| Source | Native method | Frame | Evidence |
| --- | --- | --- | --- |
| `AbilityColors/Research/assets/common/ui/node_com/frameworkscriptpod.ast`, frame 0/control 290 | `art_utility.ImageUtil.BuildFbImageString`, body `0x751a8`, 21 bytes | 2 args, 3 registers, flags 42 | Calls `FBImageDrawHelper.GetFormatToken`, appends `:`, arg 1, `:`, arg 2, then returns. |
| `DynastyEnhancer/Evidence/PlayerFog/Gaps/current-cfm-currency.ast`, frame 0/control 282 | `art_control.list.PendingOfferListItem.Init`, body `0xbd738`, 1,076 bytes | 1 arg, 17 registers, flags 25 | Instructions `0xbda1b`–`0xbda2d` concatenate the program-points asset, `:`, and `Icons.LIBRARY_ID`, then assign WidgetData `value` to the `mcOfferValue` child. Native body FNV-1a is `e151c595349a4bc3`. |

`StaffModuleTile.Init` builds its `mcPgrPts`, `mcExpectedValue` and
`mcCurrentOffer` children with the canonical helper, so those paths already
use the first gate. `PendingOfferListItem.Draw` reads
`mData.ExtraInfo.ProgramPoints` into `mcOfferValue.SetLabel`; this budget amount
is distinct from coach XP/talent points.

The fix only broadens the existing display-label gate to the second verified
string. It changes no numeric values, widget style, layout, input, clamps,
sorting, or native frames. Dollars Off remains native. The currency tests
verify both exact forms, exclusion cases, source-body fingerprints, K/M
conversion and unchanged input data.
