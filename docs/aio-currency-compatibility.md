# AIO Dynasty 1.4.1 currency compatibility

AIO's updated UI assets append recompiled class scripts and redirect their
control pointers. Several old method bodies remain in the file but are no
longer the active callbacks. The previous exact-version adapters therefore
could not reliably reach the displayed amounts.

The compatibility candidate adds four separately fingerprinted asset banks
and 18 callbacks. It retains the original adapters for installations without
this AIO version. Each new definition requires the exact header, register
frame, whole-body hash and readable current constant pool. The AIO native
body is copied at runtime before our presentation suffix; source budgets,
NIL points, sliders, negotiation commands, discounts and sorting stay intact.
No AIO/native AST or extracted game data is shipped in the DLL/package.

The suffixes read original points where available. Known currency text slots
can also contain explicit AIO dollars, such as `$4,720,000` or `$2.1M`.
Those are normalized to `4.7M` and `2.1M`, without multiplying the amount
by 4,000 again. Plain numbers continue to mean Dynasty points. Generic
numbers, ratings, percentages and other currencies are excluded.

Dollar Values Off leaves AIO's own monetary display intact. This option
controls Dynasty Enhancer's formatting; it does not disable AIO features.
Known native/team grade settings remain independently gated. No additional
background polling or asset scan is installed for this compatibility path.

The new candidate also includes the previously built independent Player/Team
Grade Scale, Blind mode and recruiting currency-fit improvements. Both native
components must be installed together because they share options protocol 4.

Checks cover raw points, explicit dollars, K/M, negatives, zero, invalid input,
Blueprint/topbar output, Off no-op, source-data preservation and the existing
native/UI suites. MMC registration/integrity/tamper tests run on the combined
package. Live acceptance requires a clean launch with AIO 1.4.1; offline tests
alone do not prove that another mod or a cached deployment selects these assets.

## Mapped callbacks

| Family | Callback | New definition | Registers | Body bytes |
|---|---|---:|---:|---:|
| cellPrograms | SetData | 0x3075E0 | 4 | 583 |
| corePrograms | _UpdateNumber | 0x2E9278 | 2 | 645 |
| corePrograms | Draw | 0x2E9AE0 | 5 | 6521 |
| corePrograms | _SetupStageObjects | 0x2FB3F0 | 20 | 4690 |
| corePrograms | _OnOfferChanged | 0x2FD950 | 11 | 1055 |
| corePrograms | Draw | 0x2F50D8 | 12 | 1083 |
| corePrograms | Draw | 0x2F6870 | 9 | 574 |
| artPrograms | Draw | 0xA8060 | 6 | 958 |
| artPrograms | _SetGraphLabelData | 0xAB268 | 10 | 1486 |
| topbar | SetExtraInfo | 0x165D8 | 20 | 5064 |
| recruiting | _RefreshStats | 0x6F7C0 | 7 | 338 |
| recruiting | Draw | 0x5D760 | 18 | 5068 |
| editor | Draw | 0x2FF0D0 | 4 | 478 |
| editor | _AddCurrentValue | 0x2FF898 | 3 | 177 |
| editor | _SetCurrentValueToMax | 0x2FFA10 | 2 | 121 |
| editor | _SetCurrentValueToMin | 0x2FFAC0 | 2 | 121 |
| editor | _SetCurrentValueToDefault | 0x2FFB70 | 2 | 121 |
| team | Draw | 0x2F8C90 | 5 | 4514 |
