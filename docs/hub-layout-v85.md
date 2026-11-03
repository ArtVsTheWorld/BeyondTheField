# Hub descriptor recovery — v85

The first v84 hub refresh logged social_tab_added, then the user reported a completely blank hub and unresponsive controls. v84's unit tests covered the JSON plan and decoder but did not exercise the native numeric setter. The new tileFloat binding at RVA 0x2bf67d0 was incorrect: disassembly shows it calls the unsigned-number factory at 0x8aec7e0, which consumes R8D. Passing a float in XMM2 left the numeric argument invalid. This affects sizes, row counts and priorities in the new descriptor and explains why an otherwise valid JSON plan did not establish native presentation safety.

v85 removes that binding. It calls the verified number factory at 0x8aec870 through its exact (manager, output pointer, double) signature, then attaches/releases the resulting ASP number through the existing map-value helper. The factory reads XMM2 and stores a double. A 32-byte gate verifies its code before activation.

Before publishing, v85 decodes the constructed native map again and requires exact scalar equality with the planned descriptor. It builds the replacement array with the tab immediately after Team, then reads back its span and every pointer, requiring the expected count and order. Failure releases only the newly owned objects and forwards the original hub array. Original descriptors remain unchanged. This adds no save/calendar/simulation writes.

Native regressions exercise double argument forwarding for 4.5, -1 and 13, physical insertion, matching readback and rejection of missing/corrupt native values. All previous layout, feed, scope, input and ownership tests remain. In-game placement, entry, controls and Back must still be verified separately.

Recovery: v84 hooks were stopped successfully and its automatic adapter renamed to DynastyEnhancer.dll.v84-disabled. The user then closed CFB. Saves and history from the v84 installation are preserved; v85 migrates the latest history rather than regenerating prior editions. Package, installation and controller outcomes are recorded in verified-v85.json.
