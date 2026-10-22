# DBM for AzerothCore with Individual Progression

Deadly Boss Mods for the 3.3.5a client, based on [Zidras/DBM-Warmane](https://github.com/Zidras/DBM-Warmane)
10.1.13_alpha and adapted to AzerothCore realms that run mod-playerbots and mod-individual-progression:
playerbot raids, Individual Progression 40-man raids, and AzerothCore's boss scripts. The 36 stock folders
are merged into 7.

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

- **Difficulty.** Removed the Warmane Timewalking check. A 25-man raid-difficulty setting made every 40-man raid
  count as Timewalking. Unknown difficulties no longer break pull and kill statistics.
- **Individual Progression.** Naxxramas 40 and Onyxia 40 (mod-individual-progression runs them in the 10-man heroic slot) count as 40-man and
  load the vanilla mods instead of the WotLK ones (virtual realm `IP40` in the pack metadata).
  The vanilla Onyxia mod looks for Individual Progression's own Onyxia (301000) and its Tail Sweep.
- **Molten Core.** Golemagg's Quake uses AzerothCore's Earthquake. Majordomo counts as killed when his eight
  Flamewakers die (he submits instead of dying) and tracks his random-target teleport. The speed-clear
  listener stops once the clear can't be timed instead of filtering every damage event for the whole raid.
  Boss timers follow AzerothCore's scripts: the Ragnaros pull countdown (72.6s from the summon cast, 7.5s
  from Majordomo's death), Garr's Anti-Magic Pulse, Shazzrah's Gate and curse, Majordomo's alternating
  teleports and shields, and the first casts and cooldowns of Lucifron, Gehennas and Baron Geddon.
- **MC/BWL timing follow-up.** Magmadar shows the first Fear at 9.5s and its 31s minimum repeat. BWL uses AzerothCore's Broodlord Knock Away spell (25778), first Blast Wave/Knock Away at 12s/30s, Vaelastrasz's 41s opening-yell countdown (29s from the Russian second-line trigger, synchronized across locales) and 15s Burning Adrenaline, drake Shadow Flame at 18s then a 15s minimum cooldown, and Nefarian's 25s minimum Fear cooldown. Random cooldown bars show the earliest scheduled cast, not an exact prediction; other casts can delay execution. Shadow Flame bars retain their existing disabled-by-default setting. In-game validation is still required.
- **Encounter timing.** Timers and warnings in the Classic, BC and Wrath packs follow the server's boss scripts. Cooldown bars show the earliest scheduled recurrence; random selection, event queues and phase changes can delay the actual cast. Not every encounter has been checked in a game client. The changes:
  - *Naxxramas 40.* Individual Progression's custom Naxxramas creature IDs map to the canonical vanilla IDs, only on the `IP40` difficulty. This covers engagement, kill counting, combat-log helpers and health scans. Gluth and Loatheb timers are corrected, including the direct spore summon spell 90006.
  - *Onyxia 40.* Flame and whelp intervals follow the Onyxia 40 script. Guard and breath predictions the script doesn't support are off on `IP40`.
  - *Zul'Gurub and AQ.* Kurinnaxx, Jeklik, Edge of Madness and Thekal event handling is repaired. Hakkar, Kurinnaxx, Huhuran, the Bug Trio, the Twin Emperors and Viscidus use the server's cooldowns. Huhuran's poison and sting timers survive berserk. Thekal keeps his first resurrection deadline and the mod watches for his actual Tiger Form.
  - *Hakkar.* No health-based guess for surviving priests. Aspect cooldowns start on their first observed cast. Insanity timing and the Corrupted Blood range frame cleanup are corrected.
  - *Classic dungeons.* Gnomeregan, Maraudon, Scarlet Monastery and the Stockade follow the server's schedules. Thermaplugg's misspelled event handler, Herod's Whirlwind condition and Landslide's Knock Away ID are fixed.
  - *Burning Crusade.* Teron Gorefiend's Shadow of Death and Illidan's Flame Crash subscriptions are restored. Teron, Anetheron, Void Reaver and Akil'zon timing and Malacrass's Flash Heal ID are corrected. Dungeon events for the Black Morass drake, Epoch Hunter, Kael'thas, Warp Splinter, Thorngrin and Zereketh are restored. Hellmaw, Blackheart, Vorpil, Tavarok and Kael'thas schedules are corrected.
  - *Wrath.* Raids: Vault of Archavon openings and repeats, Koralon (no hard berserk, triggered Meteor Fists), Gluth's difficulty-specific Decimate, Grobbulus spray and berserk, Sartharion's first breath and walls, selected Ulduar schedules and arm respawns, and the Jaraxxus and Twin Val'kyr timers. Dungeons: Dred's creature check (no health-triggered fear prediction), Consume and Gal'darah spells, form transitions and charge recovery, and the Eck, Moorabi, Loken, Maiden, Skadi, Moragg and Cyanigosa schedules.
  - *Other.* Lethon's breath stacks and Sulfuron's Inspire-removal handling are restored.
- **Bots.** Timer recovery only asks raid members known to run DBM; playerbots never answer.
- **Fixes.** Creature-ID lookups ignore non-string GUIDs. The backup raid-icon setter is chosen correctly.
  Toc file names match the files' case.

## Updating to a new DBM-Warmane release

`tools/merge_packs.py` only builds the folder layout. It works on a stock tree and knows nothing about this fork's fixes.

1. Unpack the new release over a clean checkout of the stock import (the 36 folders) and commit it.
2. Run `python3 tools/merge_packs.py` from the repo root and commit.
3. Re-apply this fork's fixes, the ones listed under "Changes from DBM-Warmane", at their new paths
   (`DBM-MC/` is now `DBM-Classic/MC/`). The script adds the `IP40` realm tags itself.

## Tests

`python -m unittest discover -s tests -v` runs the Molten Core and Blackwing Lair checks and the registered-event, timer, difficulty and IP40 identity checks against the boss mods under Lua 5.1. It needs `lupa` with Lua 5.1 support.

## Patch Notes: Deadly Boss Mods
Category: Addons

- **Deadly Boss Mods** now ships as 7 folders instead of 36, with one boss-mod addon per expansion.
- Molten Core warnings match AzerothCore's boss scripts: **Majordomo Executus** counts as defeated when his Flamewakers fall, and **Golemagg's** Quake warning works.
- Molten Core timers match our boss scripts. The **Ragnaros** pull countdown no longer runs past the moment he attacks, and **Garr**, **Shazzrah** and **Majordomo Executus** timers no longer run out seconds before the ability.
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
