# Native Class & NIL label bounds

The active-player sidebar uses `art_control.module.spreadsheet.InfoSlotsItemWidget`.
Its native `Draw` (definition `0x34730`, body `0x34760`, 702 bytes) positions
`mcCurrencyValue` after the class label and `CURRENCY_PADDING`, but gives its text
no remaining-width constraint. Dollar labels such as `600K` and `1.2M` can
therefore overlap the neighboring Height & Weight slot when the class includes
a redshirt suffix.

The existing currency-only `Draw` suffix now gives this native child a fixed
container width and a native `RESIZE_SCALEDOWN` text style. The available width
comes from the parent slot's logical `mData.Width`, minus the currency child's
native `_x`, 10 pixels of native-style right padding, the icon size and text
padding. It never depends on a previously shrunken label's width. The native
`LabelTextStyle.CloneAndModify` preserves the existing font, color, alignment
and icon styling, including the child's deferred redraw. Missing or invalid
geometry/style leaves layout unchanged.

An unchanged-On fast path checks the exact currency semantics, source amount,
parent width, currency origin, icon/text padding, owned child width/fixed mode,
style identity/resize fields and display. When these still match, the suffix
does not format a label, clone a style, call a setter or invalidate a widget.

When one of those inputs changes or dollars is turned Off, the per-child fit
state is removed. The suffix restores the numeric label, native width,
fixed-width mode and the three resize fields only while those fields still
contain the values it applied. It then fits again if dollars is enabled. A
native style replacement is preserved as the fresh baseline; native font/color
edits to the fitted style also survive because restoration changes only the
three resize properties. This supports On → Off → On on one cached widget
without requiring a screen rebuild or accumulating shrinkage. The slot bank
therefore remains dispatched while dollars is Off, while its internal option
gate prevents new formatting/fitting.

The suffix is gated by the dollars option and exact native program-points icon
ID/library. It does not change the parent class/year text, NIL compensation,
grid keys, numeric sort fields, neighboring slots, or non-money widgets. The
same verified native method and register frame remain in use; no extra UI
callbacks or per-frame traversal were added.

Validation:

- `python Tests/currency_slot_layout_test.py`: all class years with and without
  redshirts, K/M amounts, repeated/deferred draws, same-instance On/Off/On,
  non-money reuse, native width/style replacement and in-place font/color
  refreshes, zero setters/clones over 50 unchanged-On draws, source/geometry
  invalidation and return to the fast path, style/icon/year/data preservation,
  and invalid geometry/style.
- `python Tests/currency_ui_test.py`: existing money formatting, source-data
  preservation, exact currency icon guards, native fingerprints and register
  bounds.

Live follow-up: inspect a redshirt player's Class & NIL line containing a long
K/M label on the roster sidebar and player card. This checks readability at the
game's actual slot dimensions; the offline checks establish containment and
unchanged data, not the final apparent font size.
