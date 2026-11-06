# Recruiting Scholarship detail currency

`Tools/build_currency_recruitdetail_ui.py` generates the separate
`Source/CurrencyRecruitDetailUiPrograms.h` bank. Integrate
`recruitingfog::currencyrecruitdetailui::programs()` and keep this bank
dispatched regardless of Dollar Values, passing the current Dollar Values
literal. Its internal checks keep a fresh default-Off widget unchanged and
restore only previously converted state when the option turns Off.

The current recruitinghub asset is
`common/ui/node_cfm/recruitinghub/corenode.ast`, GUID
`c1c94d9d-8708-a58e-7969-e68b31b6a610`, privately extracted at
`Evidence/PlayerFog/Gaps/current-recruitinghub.ast`. The adapter has one unique
native owner:

| Callback | Header | Arguments/registers/flags | Body bytes | FNV-1a |
|---|---:|---|---:|---|
| `art_control.recruitinghub.SummaryPanelListItem.Draw` | `0x16160` | 0/8/25 | 1,727 | `C06366D67CE77475` |

The source model `logic_cfm.model.recruitinghub.board.Recruiting._OnRecruitUpdated`
has body `0x111E8`, size 1,736, FNV-1a `61B616824D7E381A`. It populates two
independent summary rows:

| Row | Source | Renderer field | Native currency proof |
|---|---|---|---|
| Offer | Active recruit `CurrentNILOffer` | `ExtraInfo.Body` | Explicit program-points `Icon` and `IconLibrary` |
| Expected NIL | Active recruit `ExpectedNILValue` | `ExtraInfo.Body` | The same exact icon/library pair |

The suffix admits a row only when both `ExtraInfo.Icon` and `IconLibrary` match
`shared_enum.fblibraries.global.Icons.ASSETID_ICON_CURRENCY_PROGRAMPOINTS` and
`LIBRARY_ID`. It formats that row's own `Body` into `mcBody.SetLabel`. Text labels
are not used as a gate, so localization is preserved. No-offer messages, hours,
influence triangles, pitch grades, feedback and percentages remain native.
Amounts use the shared 4K-per-point K/M formatter without a textual dollar sign.

Native Draw positions `mcIcon` to the left of the right-aligned body using
`mcBody._x - mcBody.GetWidth() - mcIcon.GetWidth() - 10`, with y equal to
`mcBody._y - mcIcon.GetHeight()/2`. The suffix repeats those exact formulas after
formatting, preserving all fonts, colors, icon dimensions and visibility flags.

A small private state attached to the body records the original native display,
source value, applied label, style identity and primitive layout metrics, parent width, body position, icon
identity/dimensions and applied icon position. Unchanged On draws do no setter,
measurement, geometry or state-allocation work. When the source or layout changes,
or the option turns Off, cleanup restores a label only if it is still the
adapter's last applied label. It uses fresh source data for a reused row and
preserves native text/style/position replacements. Icon coordinates are restored
only while they still match the coordinates the adapter applied. The source
`Body` and the active recruit's offer, valuation, hours and eligibility are never
modified.

Layout metrics include font identity/size, resize mode/width, alignment, line
count and spacing. Comparing their saved primitive values catches native style
merges made in place; color-only focus changes leave the cache intact and do not
cause a setter, measurement or geometry update.

`Tests/currency_recruitdetail_ui_test.py` verifies independent Offer/Expected NIL
amounts, default-Off no-op, 100 unchanged On draws without setters/measurement or
geometry, same-widget On/Off restoration, changed source values without a dirty
native render, native dirty text/style changes, icon sizing and position changes,
exact icon/library exclusion, invalid/preformatted text rejection, source-field
preservation, original register-frame bounds, complete native fingerprints and
deterministic generation. It also checks that this offset/hash has exactly one
generated owner.
