import json
import os
from collections import Counter

def summarize_reach(path):
    print("====", path)
    for fn in sorted(os.listdir(path)):
        if not fn.endswith(".json"):
            continue
        with open(os.path.join(path, fn), encoding="utf-8") as f:
            data = json.load(f)
        engine = data.get("m_game_engine")
        keys = list(data.keys())
        extra = ""
        cv = data.get("m_custom_variant")
        if isinstance(cv, dict):
            extra = "enc=%s build=%s traits=%s opts=%s strings=%s" % (
                cv.get("m_encoding_version"),
                cv.get("m_build_number"),
                len(cv.get("m_player_traits") or []),
                len(cv.get("m_user_defined_options") or []),
                type(cv.get("m_script_strings")).__name__,
            )
        print(f"  {fn:40} engine={str(engine):16} keys={keys} {extra}")

def trait_style(path):
    print("==== trait styles", path)
    c = Counter()
    for fn in sorted(os.listdir(path)):
        if not fn.endswith(".json"):
            continue
        with open(os.path.join(path, fn), encoding="utf-8") as f:
            data = json.load(f)
        try:
            v = data["m_base_variant"]["m_respawn_options"]["m_respawn_player_traits"]["m_shield_vitality_traits"]["m_damage_resistance_percentage_setting"]
            c[(type(v).__name__, str(v)[:40])] += 1
            if isinstance(v, int):
                print("  INT", fn, v)
        except Exception as e:
            print("  ERR", fn, e)
    print(c)

summarize_reach(r"Halo Reach\Alpha\default_hoppers\game_variants")
print()
trait_style(r"Halo 3\Release\default_hoppers\game_variants")
