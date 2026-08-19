import json
import collections
import re
from pathlib import Path

p = Path(r"C:\Users\codie\Projects\Blam-Title-Storage\reports\upgrade-20260819-203132\failures.jsonl")
rows = [json.loads(l) for l in p.read_bytes().decode("utf-8", "replace").splitlines() if l.strip()]


def names(cfg, step, vtype):
    out = []
    for r in rows:
        if r.get("Config") == cfg and r.get("Step") == step and r.get("VariantType") == vtype:
            out.append(Path(r.get("File") or "").name)
    return out


h3_games = names("Halo 3\\Release", "export-variant", "game_variants")
h3_maps = names("Halo 3\\Release", "export-variant", "map_variants")
print("H3 games failed export", len(h3_games))
print("H3 maps failed export", len(h3_maps))

root = Path(r"C:\Users\codie\Projects\Blam-Title-Storage\Halo 3\Release")

int_enum = 0
named = 0
other = []
for name in h3_games:
    hits = list(root.rglob(name))
    if not hits:
        other.append(("missing", name))
        continue
    text = hits[0].read_text(encoding="utf-8", errors="replace")
    if '"m_damage_resistance_percentage_setting": 0' in text:
        int_enum += 1
    elif "_damage_resistance_percentage_setting_" in text:
        named += 1
    else:
        other.append(("no trait field", name))
print("H3 games integer-enum", int_enum, "named", named, "other", other[:20], "other_count", len(other))

null_k = 0
ver_bad = 0
both = 0
neither = []
vers = collections.Counter()
for name in h3_maps:
    hits = list(root.rglob(name))
    if not hits:
        neither.append(("missing", name))
        continue
    text = hits[0].read_text(encoding="utf-8", errors="replace")
    nk = '"k": null' in text
    m = re.search(r'"m_map_variant_version"\s*:\s*(\d+)', text)
    v = int(m.group(1)) if m else -1
    vers[v] += 1
    v_ok = v in (12,)
    if nk and not v_ok:
        both += 1
    elif nk:
        null_k += 1
    elif not v_ok:
        ver_bad += 1
        neither.append(("badver", v, name))
    else:
        neither.append(("okver-nonull", v, name, str(hits[0].relative_to(root))))
print("H3 maps both-null-and-badver", both, "null-only", null_k, "badver-only", ver_bad)
print("failed map version hist", dict(vers))
print("neither/odd", neither[:25], "count", len(neither))

print("\nH3 failed maps:")
for n in sorted(h3_maps):
    print(" ", n)

print("\nH3 failed games (unique basenames):")
seen = set()
for n in h3_games:
    seen.add(n)
print(" count unique", len(seen))
# hopper split
from collections import Counter
hop = Counter()
for r in rows:
    if r.get("Config") == "Halo 3\\Release" and r.get("Step") == "export-variant" and r.get("VariantType") == "game_variants":
        hop[r.get("Hopper")] += 1
print(" games by hopper", dict(hop))
hopm = Counter()
for r in rows:
    if r.get("Config") == "Halo 3\\Release" and r.get("Step") == "export-variant" and r.get("VariantType") == "map_variants":
        hopm[r.get("Hopper")] += 1
print(" maps by hopper", dict(hopm))

for cfg in ["Halo Reach\\Alpha", "Halo Reach\\Beta", "Halo Reach\\Delta"]:
    exp = names(cfg, "export-variant", "game_variants")
    imp = [
        Path(r.get("File")).name
        for r in rows
        if r.get("Config") == cfg and r.get("Step") == "import-variant"
    ]
    exp_bin = {Path(n).stem + ".bin" for n in exp}
    extra = sorted(set(imp) - exp_bin)
    print(f"\n{cfg} export fail {len(exp)} import fail {len(imp)} import-only {len(extra)}")
    print("  export fails:", sorted(exp))
    print("  import-only:", extra)

# engine tags on reach failed vs ok
reach_root = Path(r"C:\Users\codie\Projects\Blam-Title-Storage\Halo Reach")
for folder, cfg in [("Alpha", "Halo Reach\\Alpha"), ("Beta", "Halo Reach\\Beta"), ("Delta", "Halo Reach\\Delta")]:
    engines = Counter()
    failed = set(names(cfg, "export-variant", "game_variants"))
    gdir = reach_root / folder / "default_hoppers" / "game_variants"
    if not gdir.exists():
        continue
    for f in gdir.glob("*.json"):
        head = f.read_text(encoding="utf-8", errors="replace")[:400]
        m = re.search(r'"m_game_engine"\s*:\s*"([^"]+)"', head)
        tag = m.group(1) if m else "?"
        status = "FAIL" if f.name in failed else "ok"
        engines[(status, tag)] += 1
    print(folder, "engine tags", dict(engines))
