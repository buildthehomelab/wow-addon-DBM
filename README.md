# DBM for our AzerothCore realm

Deadly Boss Mods for the 3.3.5a client, based on [Zidras/DBM-Warmane](https://github.com/Zidras/DBM-Warmane)
10.1.13_alpha and adapted to our AzerothCore server: playerbot raids, Individual Progression 40-man raids,
and AzerothCore's boss scripts. The 36 stock folders are merged into 7.

## Install

1. Delete every old `DBM-*` folder from `Interface\AddOns`.
2. Copy these folders into `Interface\AddOns`:

   | Folder | What it holds | Loads |
   |---|---|---|
   | `DBM-Core` | Core, timer bars (was DBM-StatusBarTimers), spell timers (was DBM-SpellTimers) | at login |
   | `DBM-GUI` | Options window (`/dbm`) | when opened |
   | `DBM-Classic` | MC, BWL, ZG, AQ20, AQ40, Onyxia 40, Naxxramas 40, classic dungeons, world bosses | entering one of its zones |
   | `DBM-BC` | Burning Crusade raids, dungeons and world bosses | entering one of its zones |
   | `DBM-WotLK` | Wrath raids and dungeons | entering one of its zones |
   | `DBM-Extras` | Battlegrounds and holiday bosses | entering one of its zones |
   | `DBM-VPVEM` | VEM voice pack | at login |

If an old folder (for example `DBM-MC` or `DBM-StatusBarTimers`) is still installed, DBM disables it and
prints which folder to delete. Delete it and `/reload`.

The merge resets boss-mod options and timer-bar positions once. They lived in the old folders' saved variables.

## Changes from DBM-Warmane

This is a modified version of DBM-Warmane. The changes:

- **Folder layout.** The boss-mod folders live inside `DBM-Classic`, `DBM-BC`, `DBM-WotLK` and `DBM-Extras`
  (one subfolder per raid or dungeon pack). `DBM-StatusBarTimers` and `DBM-SpellTimers` are part of
  `DBM-Core`. DBM-Core reads the pack metadata from `DBM-Core/PackManifest.lua` and loads the expansion
  addon that holds a pack. `tools/merge_packs.py` builds this layout from a stock release.

## Updating to a new DBM-Warmane release

`tools/merge_packs.py` only builds the folder layout. It works on a stock tree and knows nothing about our fixes.

1. Unpack the new release over a clean checkout of the stock import (the 36 folders) and commit it.
2. Run `python3 tools/merge_packs.py` from the repo root and commit.
3. Re-apply the fixes from the "Fix DBM for AzerothCore and Individual Progression" commit at their new paths
   (`DBM-MC/` is now `DBM-Classic/MC/`). The script adds the `IP40` realm tags itself.
- **Difficulty.** Removed the Warmane Timewalking check. A 25-man raid-difficulty setting made every 40-man raid
  count as Timewalking. Unknown difficulties no longer break pull and kill statistics.
- **Individual Progression.** Naxxramas 40 and Onyxia 40 (the 10-man heroic slot on our realm) count as 40-man and
  load the vanilla mods instead of the WotLK ones (virtual realm `IP40` in the pack metadata).
- **Molten Core.** Golemagg's Quake uses AzerothCore's Earthquake. Majordomo counts as killed when his eight
  Flamewakers die (he submits instead of dying) and tracks his random-target teleport. The speed-clear
  listener stops once the clear can't be timed instead of filtering every damage event for the whole raid.
- **Bots.** Timer recovery only asks raid members known to run DBM; playerbots never answer.
- **Fixes.** Creature-ID lookups ignore non-string GUIDs. The backup raid-icon setter is chosen correctly.
  Toc file names match the files' case.

## Patch Notes: Deadly Boss Mods
Category: Addons

- **Deadly Boss Mods** now ships as 7 folders instead of 36, with one boss-mod addon per expansion.
- Molten Core warnings fit our server: **Majordomo Executus** counts as defeated when his Flamewakers fall, and **Golemagg's** Quake warning works.
- 40-man raids are no longer labelled Timewalking, and Naxxramas 40 and Onyxia 40 use the classic boss mods.
> Delete your old DBM folders before installing. Boss-mod options reset once.

## Requirements

- WoW 3.3.5a (12340) client.

## Troubleshooting

- **"The folder DBM-X is now part of DBM-Y"**: an old folder is still installed. Delete it and `/reload`.
- **Lua errors**: turn on `/console scriptErrors 1` and report the first error with its file and line.

## Credits

Deadly Boss Mods by the original DBM team (Tandanu, Nitram, MysticalOS, QartemisT and others). WotLK backport and
the Classic raid packs by Zidras, Barsoom, Bunny67 and the DBM-Frostmourne contributors. VEM voice pack by Iceoven.

## License

Creative Commons Attribution-NonCommercial-ShareAlike 3.0, the same license as DBM itself. See [LICENSE](LICENSE).
This repository is a modified version (see "Changes from DBM-Warmane") and is shared under the same terms.
