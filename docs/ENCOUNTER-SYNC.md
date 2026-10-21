# Encounter synchronization audit — 2026-10-21

This audit compares the fork's Classic, TBC and Wrath packs with Evermore's server
implementation. It is not a claim that every mechanic has been validated in game.

## Reference versions

- DBM base: `9299b85` (includes reviewed MC/BWL PR #6).
- Live world database version record: core `d5e40f8b3b4f+`, ACDB 335.17-dev.
  The `+` suffix means the build included local changes; the version record alone
  does not prove byte-for-byte equality with a Git commit or the running process.
- Core scripts inspected at `d5e40f8b3b4f43bf3bbb4ad119493d0ee70f9e0a`.
  The current authenticated server pin `c89a4a401922f363faefbf596a4a465a1494c397`
  changes only two city scripts relative to those encounter references.
- Individual Progression server pin: `46ab14dce6be2b6c83435220a5f190573f516bf4`.
- Read-only world data: creature script/difficulty bindings, SmartAI schedules,
  spell difficulty mappings and custom Naxx40 entries/spells.

Source implementations:
[core](https://github.com/buildthehomelab/wow-azerothcore/tree/d5e40f8b3b4f43bf3bbb4ad119493d0ee70f9e0a/src/server/scripts),
[Individual Progression](https://github.com/buildthehomelab/wow-mod-individual-progression/tree/46ab14dce6be2b6c83435220a5f190573f516bf4/src).

## Corrected behavior

| Area | Changes |
| --- | --- |
| Core / Naxx40 | Recognize IP's custom Naxx creature IDs through the canonical vanilla IDs, restricted to the IP40 difficulty. This covers engagement, kill counting, combat-log helpers and health scans. Normal Naxx and custom Onyxia retain their existing IDs. |
| ZG / AQ | Repair Kurinnaxx, Jeklik, Edge of Madness and Thekal event handling; use server cooldowns for Hakkar, Kurinnaxx, Huhuran, Bug Trio, Twin Emperors and Viscidus. Preserve Huhuran poison/sting timers through berserk. Keep Thekal's first resurrection deadline and observe actual Tiger Form. |
| Hakkar | Remove the health-based guess for surviving priests. Aspect cooldowns start on their first observed cast. Correct Insanity timing and Corrupted Blood range-frame cleanup. |
| Classic dungeons | Correct live SmartAI schedules in Gnomeregan, Maraudon, Scarlet Monastery and Stockades; fix Thermaplugg's misspelled event handler, Herod's Whirlwind condition and Landslide's Knock Away ID. |
| Naxx40 / Onyxia40 | Correct Gluth and Loatheb timers, including IP's direct spore summon spell 90006. Use Onyxia40's flame and whelp intervals; suppress unsupported guard and speculative breath predictions on IP40. |
| TBC raids | Restore Teron Shadow of Death and Illidan Flame Crash event subscriptions; correct Teron, Anetheron, Void Reaver and Akil'zon timing and Malacrass's Flash Heal ID. |
| TBC dungeons | Restore Drake, Epoch Hunter, Kael'thas, Warp Splinter, Thorngrin and Zereketh events; correct Hellmaw, Blackheart, Vorpil, Tavarok and Kael'thas schedules. |
| Wrath raids | Correct VoA openings/repeats, remove Koralon's nonexistent hard berserk, and handle triggered Meteor Fists. Correct Gluth's difficulty-specific Decimate, Grobbulus spray and berserk, Sartharion's first breath/walls, selected Ulduar schedules and arm respawns, and Jaraxxus/Twin Valkyr timers. |
| Wrath dungeons | Correct Dred's creature check and remove its health-triggered fear prediction; restore normal Consume and Gal'darah spells, explicit form transitions and charge recovery; correct Eck, Moorabi, Loken, Maiden, Skadi, Moragg and Cyanigosa schedules. |
| Other events | Restore Lethon's breath stacks and Sulfuron's Inspire-removal handling. |

Cooldown bars show the earliest scheduled recurrence. Random selection, event
queues, casting and encounter transitions can delay the actual ability. Channel
start/success and triggered casts must be distinguished from cast-start events;
Scorch and Slime Spray retain success-event anchors.

## Coverage and remaining work

The inventory spans 488 encounter/trash definitions: 243 Classic, 116 TBC and 129
Wrath. Initial live bindings linked 324 definitions to C++ sources, 151 to SmartAI,
and left 13 without a direct script link. These are inventory counts, not counts
of fully verified encounters. Custom Naxx40 must use the separate IP source and
clone bindings rather than the normal Naxx rows.

All definitions were screened for event registration and spell-field errors.
104 definitions have no active spell handlers; many Classic dungeon definitions
are detection-only stubs. A passing syntax check cannot establish ability
coverage for those encounters. Detailed semantic review focused on the corrected
modules. Unchanged encounters have not all received equivalent semantic review.

Known follow-up areas include C'Thun/Ouro/Lurker phase observations, Viscidus
thaw/reformation recovery, and remaining timers in SSC, Ulduar and ICC. Some
schedules depend on add deaths, movement, interrupts or explicit event delays;
copying a raw interval into DBM is insufficient. Normal/heroic spell variants
and custom spell corrections also need encounter-specific validation.

Combat-log traces and in-game pulls remain necessary to validate actual event
visibility, target selection and phase recovery. No database writes, server
restart, addon installation or game-client validation were performed.

## Validation and distribution

`python -m unittest discover -s tests -v` runs the existing MC/BWL regressions and
new Lua 5.1 registered-event, timer, difficulty, repeated-phase and IP40 identity
checks. It requires `lupa` with Lua 5.1 support. Syntax checks handle the UTF-8 BOMs
accepted by the WoW file loader.

Distribute the matching **DBM-Core, DBM-Classic, DBM-BC and DBM-WotLK** folders
together after reviewed merge. Keep the other three existing folders installed.
This addon has no server manifest row; no SQL, MPQ, core/module pin or server
restart is required for these addon changes.
