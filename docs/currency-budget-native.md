# Plain budget and recruiting offer currency

`Tools/build_currency_budget_ui.py` produces
`Source/CurrencyBudgetUiPrograms.h`. The runtime integration uses
`recruitingfog::currencybudgetui::corePrograms()` and
`recruitingfog::currencybudgetui::animationPrograms()`, plus
`recruitingfog::currencybudgetui::artPrograms()`. Enable all three only for the
Dollar Values option. These are separate native asset banks; no method duplicates
another currency bank.

The current MMC Presentation_Common collector maps
`common/ui/node_cfm/corenode.ast` to GUID
`38cfa64f-22dd-2e99-1dcf-4578b9828270`. The read-only extraction is in ignored
`Evidence/PlayerFog/Gaps/current-cfm-currency.ast`. Its exact callbacks are:

| Callback | Header | Arguments/registers/flags | Body bytes | FNV-1a |
|---|---:|---|---:|---|
| `ProgramBudgetMySchoolGradeRow._UpdateNumber` | `0x38A28` | 0/2/41 | 61 | `6E4DA88D33277C7E` |
| `ProgramBudgetMySchoolGradeRow.Draw` | `0x39048` | 0/5/25 | 3,377 | `82F8F4005CE31B3B` |
| `OfferScholarshipPopup._SetupStageObjects` | `0x7C470` | 0/20/41 | 3,922 | `95C711A6AA2835DB` |
| `OfferScholarshipPopup._OnOfferChanged` | `0x7E6D0` | 1/11/41 | 554 | `B7BAF5949354DCFF` |
| `coachcarousel.SchoolInfoModule.Draw` | `0x70228` | 0/12/25 | 1,024 | `12E088669C41063C` |
| `coachcarousel.ProgramPointsModule.Draw` | `0x710F0` | 0/9/25 | 526 | `527E120C5CA99BE4` |

The budget row's native sources are
`mData.ExtraInfo.ProgramPtsValue`, `PreviousProgramPtsValue`, and
`MaxProgramPtsValue`; its plain text children are `mcProgramPtsValue` and
`mcProgramPtsMax`. A prefix marks only the current-value child with the private
boolean `mDECurrencyPoints` before native code starts its numeric animation.
The Draw suffix formats the native-rendered current and maximum labels. Grade,
change, animation decisions, source numbers, colors, geometry and intervals
remain native.

Budget row maximums can arrive with a native leading slash. Only these verified
budget slots accept `/<amount>`, `<amount>/`, or a complete monetary ratio in
addition to plain numeric text. Each nonempty side still passes the canonical
number guard; formatted money, hidden values and malformed ratios are rejected.
This does not change the shared formatter for hours, statistics or other ratios.

`SchoolInfoModule.Draw` supplies the Select Your Team/school details amounts.
Its available amount comes from
`mData.ExtraInfo.SchoolInfo.DynastyPointsBudget` and goes to
`mcDynastyPointsValue`. Its header reads `mData.ExtraInfo.Budget.Remaining` and
`Budget` into separate `mcRemainingBudget` and `mcTotalBudget` children. The
remaining child includes the native trailing slash. The suffix formats only
these three monetary labels and repeats the native adjacent budget-grade x
position using the new text width. The budget grade, job difficulty, school
demeanor, stadium capacity, year founded, historical records and rivalry records
retain their values. This requires the active Dynasty's Dollar Values option;
no global/default option policy is changed.

`coachcarousel.ProgramPointsModule.Draw` uses the equivalent plain header
children with sources `mData.ExtraInfo.BudgetData.Remaining` and `Budget`.
The native wallet width is the sum of both children plus `BUDGET_BG_PADDING`,
centered under `mcBudgetTitle`; the suffix repeats that exact formula after
formatting. For example, remaining 915 and total 10,630 become `3.7M/` and
`42.5M`. Pie and allocation sources, their percentages, contracts, row sources,
sort keys and grades remain untouched.

The inner Program Overview allocation totals and center pie labels use the
distinct `common/ui/node_fe/scriptpodart.ast` pod, current GUID
`17184edd-bf84-7d14-c65d-16408b6a9240`. This is not `node_fe/scriptpod.ast` or
`art_control/scriptpod.ast`. Its read-only extraction is kept in ignored
`Evidence/PlayerFog/Gaps/current-scriptpodart.ast`. The `artPrograms()` bank
contains:

| Callback | Header | Arguments/registers/flags | Body bytes | FNV-1a |
|---|---:|---|---:|---|
| `programpoints.PointsAllocation.Draw` | `0x43F08` | 0/6/25 | 942 | `D328FBFD7790DB47` |
| `programpoints.ProgramPointsPieGraph._SetGraphLabelData` | `0x45750` | 0/10/41 | 310 | `A3F103B82B2B5F21` |

Allocation totals come from `mData.ExtraInfo.SpentTotal` and are displayed by
`mcSpentTotal`. The native class has a separate `SingleRow` variant that displays
this value as a percentage. That variant is excluded. The normal money variant
formats only `mcSpentTotal`, preserving suggested/current percentages, labels,
icons, colors and positions. The observed Staff/Facilities/Recruits/Roster/Unspent
values 445/250/620/115/200 become 1.8M/1.0M/2.5M/460K/800K.

Pie center amounts come from `mData.ExtraInfo.UpperData.Currency` and
`LowerData.Currency`, displayed by `mcBudgetCurrency` and `mcRemainingCurrency`.
The lower/remaining amount retains its native trailing slash. A total of 1,475
and remaining amount of 200 display as `800K/5.9M` across those two children.
Graph proportions, numeric currency sources, provider items, focused slices,
titles, transparency, graph dimensions and container positions remain native.
No inferred widget names or live probes are needed for these source-backed paths.

The native `fb_art_utility.TextUtil._SetLabel` helper lives in
`common/ui/art_control/scriptpod.ast`, at header `0x66DB0`, body 227 bytes,
arguments/registers/flags 7/10/42, FNV-1a `412593C510D7428E`. This is a static
callback: register 3 holds the target widget and register 2 the current numeric
value. Register 1 can be a formatted local string, so it is not used as an
implicit receiver. Its suffix only replaces a label when the target has the
exact private boolean marker. Every unmarked animation retains the native
formatter. `TextUtil.Increment` and `_Step` continue to update their own numeric
state and never consume the monetary display string. This adds no intervals,
delegate registrations or polling.

The scholarship popup's exact plain text slots are `mcProgramPoints` and
`mcNIL`. Setup reads `mPopupInfo.CustomData.NILValuation`; `_OnOfferChanged`
subtracts the current offer from the available budget before setting
`mcProgramPoints`. The suffix reads the final rendered plain numeric labels,
preserving that native calculation instead of using the initially cached
`mRemainingProgramPointsAfterCost`. Skill-point text, offer limits, discounts,
slider input and all stored values are unchanged.

All amounts use the shared 4K-per-point formatter, retaining the native currency
icon and adding no textual currency symbol. Zero stays `0`, 75 becomes `300K`
and 250 becomes `1.0M`. Invalid, hidden and previously formatted values are
ignored. The native function register frames are retained without expansion.

`Tests/currency_budget_ui_test.py` executes enabled/disabled suffixes, tests
private-marker-only animation behavior with static callback registers, preserves
native numeric state and nonmonetary text, checks whole native body hashes and
exact source/target opcode paths, bounds all scratch registers, and verifies
deterministic generation. Live spacing and attachment still require the normal
combined-build check.
