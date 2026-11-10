# Beyond the Field

**By Ace.** Dynasty Social Media, scouting fog, clearer ratings/money labels and team Player Analytics.

**[Download 1.0.7 ZIP](https://github.com/ArtVsTheWorld/BeyondTheField/releases/download/v1.0.7/BeyondTheField-1.0.7.zip)** · [Full feature list](FEATURES.md) · [What's new](RELEASES.md)

Ace installed 1.0.6, restarted MMC/game and reported it working. 1.0.7 sets the initial interest choice to Default and renames its label; existing saved choices are preserved. Other setups still need their own checks.

## Install or update

1. Close the game and MMC Mod Manager.
2. Put **BeyondTheField.dll** directly in the versioned Mod Manager's **Plugins** folder. The ZIP contains that DLL, README.txt and FEATURES.md. Matching support files are embedded and prepared automatically.
3. Move older duplicate plugin DLLs outside Plugins, keeping settings/history folders. Restart MMC and launch normally. Use a writable MMC folder outside Program Files.

Read README.txt in the ZIP for this module's menu, old filenames, logs and removal steps. Use one provider of each feature. If keeping COT for other modules, disable this feature in COT before using the standalone. You can install any combination of matching current standalone modules.

**Want one feature? Download its standalone ZIP. Want the collection? [Download Dynasty COT](https://github.com/ArtVsTheWorld/DynastyCOT/releases).** See the [compatibility and saved-data guide](https://github.com/ArtVsTheWorld/DynastyCOT/blob/d2b98e9918930cf0bb3dd4070db072b5f06ed5d8/docs/standalones.md).

## Source and verification

This repository is the standalone download/help front door. Current releases are built from the [single maintained COT workspace](https://github.com/ArtVsTheWorld/DynastyCOT/tree/d2b98e9918930cf0bb3dd4070db072b5f06ed5d8), including [this module's source](https://github.com/ArtVsTheWorld/DynastyCOT/tree/d2b98e9918930cf0bb3dd4070db072b5f06ed5d8/Modules/DynastyEnhancer) and shared build/packaging code. `source-release.json` pins the exact source revision, baseline and artifact hashes.

The older source tree retained in this repository is historical; it is **not** the build input for this standalone release. Fixes are maintained in COT rather than separately editing four forks. Release assets include integrity metadata; successful offline checks do not certify every game/overhaul combination.
