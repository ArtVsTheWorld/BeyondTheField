# Offseason filter redraw — v83

The user confirmed the permanent Dynasty Central entry, scrolled feed and Back in v82, then reported LB/RB did not work. Native logs show category, scope and week changes reaching social_selection_changed, followed by social_selection_refresh without the expected new Social Media panel-ready/card output. The selection model changed; the visible page did not.

One filterChangedHook path still requested CM_NEWSTAB after v82 moved the main entry, panel-ready translation and feed source to DynastyCentral. This is empty in Players Leaving. v83 uses requestSocialPanel for entry, selection refresh and diagnostic preflight; it forwards the exact native self/params and returns the native request result. Diagnostic ready publication also uses the persistent source. Callback scope accepts the active donor as well as synthetic/unset/legacy identifiers while the Social Media page is open. Unrelated menus still forward unchanged.

Native regression tests exercise the shared request with its panel identity, argument pointers and native failure result. Existing Node tests and actual catalog decoding remain required. Versioned native/runtime DLLs and payload-verified adapter are packaged together. Source does not modify save, calendar or simulation data. Controller confirmation is recorded separately in verified-v83.json.

Deployment: v83 is installed and payload-verified. Eight saves and ten history files were checksum-backed up and migrated history verified unchanged. The hot-loaded UI hooks activate, but the long-running game session hits the existing 12-second/6-GiB child-context discovery bound. No reader guard is relaxed. A clean launch through MMC is requested for live controller validation; it is not yet recorded as passed.
