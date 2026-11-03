# Year-round Social Media entry — v82

## Native menu change

In the inspected Players Leaving hub, native tabs are Actions, Members, Coach, Team, Stats & Records and Dynasty Central. CFB is absent. External read-only menu inspection confirms CM_NEWSTAB retains container records but every tile list is empty. The feed continues publishing Offseason Week 1; missing access is separate from generation.

DynastyCentral remains available and its native User Settings tile is at coordinate 5. v82 preserves that tile and every stock row, appending a separate coordinate-12 Social Media button. The existing CM_NEWSTAB/coordinate-7 Heisman-based shortcut remains during the season. Both route through the existing NEWS_MENU identity and native News page, with the same feed, filters, archives and controller behavior.

Feed panel requests, panel-ready translation, card tiles and container metadata now all use the persistent DynastyCentral source. They no longer depend on hidden CFB tiles. The native page title remains Social Media. Returning to either hub restores owned dropdown, layout, flow, scrolling and text changes. Synthetic preflight remains diagnostic-only and uses the same persistent source.

Only these two exact panel identities admit a shortcut. Missing donors leave original menus intact. An existing coordinate 12 causes insertion to be declined, and the tile hook only handles placements actually admitted for that panel; it cannot replace a foreign tile at the same coordinate. Typed bool/int/float/string collector forwarding and original coordinates are preserved. Game/save/simulation data and native tab visibility rules are unchanged.

## Verification

263 Node tests pass. Native tests cover the persistent source with CFB unavailable, sparse filtered row indices, preservation of original rows and typed fields, occupied coordinates, missing donors, custom feed container IDs and unrelated-menu forwarding. The exact existing binary/bytecode/ownership gates remain. Real catalog, package and in-game results are recorded in verified-v82.json. Offseason startup and return to preseason require actual progression or a separate existing save; no simulation is advanced automatically.

Deployment and live check: v82 is installed, payload-verified and active in Players Leaving (Offseason Week 1). Eight saves and ten history files were checksum-backed up and history was migrated unchanged. The permanent Dynasty Central shortcut opened a populated native Social Media feed, with scrolled posts visible. The following-week Keanu Tanuvasa NIL adjustment from $375K to $850K is visible. The user confirmed Back returns to Dynasty Central normally and Social Media remains available. No Dynasty reload or advance was needed. The current 24-edition catalog validates in every dynamic scope. Fresh-launch offseason entry and the next preseason CFB shortcut remain follow-up checks.
