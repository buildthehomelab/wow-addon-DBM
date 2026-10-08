#!/usr/bin/env python3
"""Fold the stock DBM-Warmane folders into a few addons.

The 3.3.5 client only finds addons one folder deep and loads boss mods with LoadAddOn on
whole folders, so the per-raid folders become subfolders of one load-on-demand addon per
expansion. DBM-Core still sees one entry per pack: their toc metadata moves into
DBM-Core/PackManifest.lua, and DBM-Core loads the expansion addon that holds the pack.

    DBM-Core     DBM-Core + DBM-StatusBarTimers + DBM-SpellTimers (all load at login)
    DBM-Classic  MC, BWL, ZG, AQ20, AQ40, vanilla Onyxia/Naxx, classic 5-mans, world bosses
    DBM-BC       TBC raids, 5-mans, Outland world bosses
    DBM-WotLK    WotLK raids and 5-mans
    DBM-Extras   PvP and holiday bosses
    DBM-GUI, DBM-VPVEM stay as they are (options load on demand; voice pack paths use the folder name)

Run from the repo root on a stock tree:  python3 tools/merge_packs.py
"""
import os
import re
import shutil
import sys

GROUPS = {
    "DBM-Classic": {
        "title": "Classic",
        "notes": "Boss mods for Classic raids and dungeons",
        "packs": ["DBM-MC", "DBM-BWL", "DBM-ZG", "DBM-AQ20", "DBM-AQ40", "DBM-VanillaOnyxia",
                  "DBM-VanillaNaxx", "DBM-Party-Classic", "DBM-Azeroth"],
    },
    "DBM-BC": {
        "title": "Burning Crusade",
        "notes": "Boss mods for Burning Crusade raids and dungeons",
        "packs": ["DBM-Karazhan", "DBM-Gruul", "DBM-Magtheridon", "DBM-Serpentshrine", "DBM-TheEye",
                  "DBM-Hyjal", "DBM-BlackTemple", "DBM-ZulAman", "DBM-Sunwell", "DBM-Party-BC",
                  "DBM-Outland"],
    },
    "DBM-WotLK": {
        "title": "Wrath of the Lich King",
        "notes": "Boss mods for Wrath of the Lich King raids and dungeons",
        "packs": ["DBM-Naxx", "DBM-Onyxia", "DBM-ChamberOfAspects", "DBM-EyeOfEternity", "DBM-VoA",
                  "DBM-Ulduar", "DBM-Coliseum", "DBM-Icecrown", "DBM-Party-WotLK"],
    },
    "DBM-Extras": {
        "title": "PvP & Events",
        "notes": "Battleground timers and holiday boss mods",
        "packs": ["DBM-PvP", "DBM-WorldEvents"],
    },
}
# Plain addons folded into DBM-Core: their files load right after the libraries / at the end.
CORE_EXTRAS = {
    "DBM-StatusBarTimers": "StatusBarTimers",
    "DBM-SpellTimers": "SpellTimers",
}
TITLE_PREFIX = "|cffffe00a<|r|cffff7d0aDBM|r|cffffe00a>|r |cff69ccf0"


def short(pack):
    return pack[len("DBM-"):]


def read_toc(folder):
    path = os.path.join(folder, os.path.basename(folder) + ".toc")
    text = open(path, encoding="utf-8-sig").read()
    meta, files = [], []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("##"):
            key, _, value = line[2:].partition(":")
            meta.append((key.strip(), value.strip()))
        elif line.startswith("#") or line.startswith("--"):
            continue  # comments (one stock toc uses "--")
        else:
            files.append(line)
    return meta, files


def meta_get(meta, key, default=None):
    for k, v in meta:
        if k == key:
            return v
    return default


def lua_str(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


# Interface\AddOns\<old folder>\ -> Interface\AddOns\<new folder>\<sub>\ in Lua/XML sources.
def path_map():
    m = {}
    for group, g in GROUPS.items():
        for pack in g["packs"]:
            m[pack] = (group, short(pack))
    for addon, sub in CORE_EXTRAS.items():
        m[addon] = ("DBM-Core", sub)
    return m


PATH_RE = re.compile(r"(AddOns)(\\\\|\\|/)(DBM-[A-Za-z-]+)(\\\\|\\|/)")


def rewrite_paths(root, mapping):
    changed = 0
    for dirpath, _, names in os.walk(root):
        if "/.git" in dirpath or "/tools" in dirpath:
            continue
        for n in names:
            if not n.lower().endswith((".lua", ".xml")):
                continue
            p = os.path.join(dirpath, n)
            text = open(p, encoding="latin-1").read()

            def sub(mt):
                old = mt.group(3)
                if old not in mapping:
                    return mt.group(0)
                new, subdir = mapping[old]
                sep = mt.group(2)
                return f"{mt.group(1)}{sep}{new}{sep}{subdir}{mt.group(4)}"

            new_text = PATH_RE.sub(sub, text)
            if new_text != text:
                open(p, "w", encoding="latin-1").write(new_text)
                changed += 1
    return changed


def merge_group(group, g):
    os.makedirs(group)
    saved, saved_char, lines, manifest = [], [], [], []
    packs = []
    for pack in g["packs"]:
        meta, files = read_toc(pack)
        packs.append((float(meta_get(meta, "X-DBM-Mod-Sort", "1e9")), pack, meta, files))
    for _, pack, meta, files in sorted(packs):
        for key, dest in (("SavedVariables", saved), ("SavedVariablesPerCharacter", saved_char)):
            for name in (meta_get(meta, key) or "").split(","):
                if name.strip() and name.strip() not in dest:
                    dest.append(name.strip())
        lines.append("")
        lines.append(f"# {pack}")
        lines.extend(short(pack) + "\\" + f for f in files)
        manifest.append((pack, [(k, v) for k, v in meta if k.startswith("X-")]))
        shutil.move(pack, os.path.join(group, short(pack)))
        os.remove(os.path.join(group, short(pack), pack + ".toc"))
    toc = [
        "## Interface: 30300",
        f"## Title:{TITLE_PREFIX}{g['title']}|r",
        f"## Notes: {g['notes']}",
        "## LoadOnDemand: 1",
        "## RequiredDeps: DBM-Core",
        "## DefaultState: enabled",
        f"## SavedVariables: {', '.join(saved)}",
        f"## SavedVariablesPerCharacter: {', '.join(saved_char)}",
        "## X-DBM-Packs: 1",
    ] + lines
    with open(os.path.join(group, group + ".toc"), "w", encoding="utf-8", newline="\r\n") as f:
        f.write("\n".join(toc) + "\n")
    return manifest


def write_manifest(all_manifests):
    out = [
        "-- Generated by tools/merge_packs.py. Boss-mod packs that live inside a merged addon,",
        "-- with the toc metadata DBM-Core used to read from each pack's own .toc.",
        "local _, private = ...",
        "",
        "private.packManifest = {",
    ]
    for group, manifest in all_manifests:
        out.append(f"\t[{lua_str(group)}] = {{")
        for pack, meta in manifest:
            out.append(f"\t\t{{ modId = {lua_str(pack)}, meta = {{")
            for k, v in meta:
                out.append(f"\t\t\t[{lua_str(k)}] = {lua_str(v)},")
            out.append("\t\t} },")
        out.append("\t},")
    out.append("}")
    with open(os.path.join("DBM-Core", "PackManifest.lua"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")


def fold_core_extras():
    core_toc = os.path.join("DBM-Core", "DBM-Core.toc")
    text = open(core_toc, encoding="utf-8-sig").read().replace("\r\n", "\n")
    saved_line = re.search(r"^## SavedVariables: (.*)$", text, re.M)
    extra_saved = []
    file_lists = {}
    for addon, sub in CORE_EXTRAS.items():
        meta, files = read_toc(addon)
        extra_saved += [s.strip() for s in (meta_get(meta, "SavedVariables") or "").split(",") if s.strip()]
        file_lists[addon] = [sub + "\\" + f for f in files]
        shutil.move(addon, os.path.join("DBM-Core", sub))
        os.remove(os.path.join("DBM-Core", sub, addon + ".toc"))
    text = text.replace(saved_line.group(0), saved_line.group(0) + ", " + ", ".join(extra_saved))
    text = re.sub(r"^## Dependencies: DBM-StatusBarTimers\n", "", text, flags=re.M)
    # DBT has to exist before DBM-Core.lua runs (it used to be a dependency); the manifest
    # only needs the shared private table.
    text = text.replace("# Pre-core modules\n",
                        "# Status bar timers (was DBM-StatusBarTimers)\n"
                        + "\n".join(file_lists["DBM-StatusBarTimers"])
                        + "\n\n# Packs inside DBM-Classic/BC/WotLK/Extras\nPackManifest.lua\n\n# Pre-core modules\n")
    text = text.rstrip("\n") + "\n\n# Spell timers (was DBM-SpellTimers)\n" + "\n".join(file_lists["DBM-SpellTimers"]) + "\n"
    with open(core_toc, "w", encoding="utf-8", newline="\r\n") as f:
        f.write(text)


def main():
    if not os.path.isdir("DBM-MC"):
        sys.exit("Run this from the repo root on an unmerged (stock) tree.")
    mapping = path_map()
    print("paths rewritten in", rewrite_paths(".", mapping), "files")
    manifests = [(group, merge_group(group, g)) for group, g in GROUPS.items()]
    write_manifest(manifests)
    fold_core_extras()
    print("done:", ", ".join(sorted(d for d in os.listdir(".") if d.startswith("DBM-"))))


if __name__ == "__main__":
    main()
