"""Convert title-storage variant JSON to the current blf schema."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(r"C:\Users\codie\Projects\Blam-Title-Storage")

H3_DAMAGE_RESISTANCE = [
    "_damage_resistance_percentage_setting_unchanged",
    "_damage_resistance_percentage_setting_10_percent",
    "_damage_resistance_percentage_setting_50_percent",
    "_damage_resistance_percentage_setting_90_percent",
    "_damage_resistance_percentage_setting_100_percent",
    "_damage_resistance_percentage_setting_110_percent",
    "_damage_resistance_percentage_setting_150_percent",
    "_damage_resistance_percentage_setting_200_percent",
    "_damage_resistance_percentage_setting_300_percent",
    "_damage_resistance_percentage_setting_500_percent",
    "_damage_resistance_percentage_setting_1000_percent",
    "_damage_resistance_percentage_setting_2000_percent",
    "_damage_resistance_percentage_setting_invulnerable",
]
H3_SHIELD_RECHARGE = [
    "_shield_recharge_rate_percentage_setting_unchanged",
    "_shield_recharge_rate_percentage_setting_negative_25_percent",
    "_shield_recharge_rate_percentage_setting_negative_10_percent",
    "_shield_recharge_rate_percentage_setting_negative_5_percent",
    "_shield_recharge_rate_percentage_setting_0_percent",
    "_shield_recharge_rate_percentage_setting_50_percent",
    "_shield_recharge_rate_percentage_setting_90_percent",
    "_shield_recharge_rate_percentage_setting_100_percent",
    "_shield_recharge_rate_percentage_setting_110_percent",
    "_shield_recharge_rate_percentage_setting_200_percent",
]
H3_VAMPIRISM = {
    -1: "_vampirism_percentage_setting_default",
    0: "_vampirism_percentage_setting_unchanged",
    1: "_vampirism_percentage_setting_0_percent",
    2: "_vampirism_percentage_setting_10_percent",
    3: "_vampirism_percentage_setting_25_percent",
    4: "_vampirism_percentage_setting_50_percent",
    5: "_vampirism_percentage_setting_100_percent",
}
H3_SHIELD_MULTIPLIER = [
    "_shield_multiplier_setting_unchanged",
    "_shield_multiplier_setting_0x",
    "_shield_multiplier_setting_1x",
    "_shield_multiplier_setting_2x",
    "_shield_multiplier_setting_3x",
    "_shield_multiplier_setting_4x",
]
H3_HEADSHOT = [
    "_headshot_immunity_setting_unchanged",
    "_headshot_immunity_setting_immune_to_headshots",
    "_headshot_immunity_setting_not_immune_to_headshots",
]

REACH_ACTIVITY = {
    -1: "none",
    0: "activities",
    1: "campaign",
    2: "matchmaking",
    3: "multiplayer",
    4: "mapeditor",
    5: "theater",
    6: "survival",
}
REACH_CONTENT_GAME_MODE = {
    0: "none",
    1: "campaign",
    2: "survival",
    3: "multiplayer",
}

BN1_ALIASES = {
    "paralysis_v1.0.json": "bn1_paralysis_v10.json",
    "plurality_snipe.json": "bn1_sniper_plurality.json",
}

H3_RELEASE = ROOT / "Halo 3" / "Release"


def replace_nulls(value):
    if value is None:
        return 0.0
    if isinstance(value, dict):
        return {k: replace_nulls(v) for k, v in value.items()}
    if isinstance(value, list):
        return [replace_nulls(v) for v in value]
    return value


def convert_h3_traits(obj):
    if isinstance(obj, list):
        for item in obj:
            convert_h3_traits(item)
        return
    if not isinstance(obj, dict):
        return
    if isinstance(obj.get("m_damage_resistance_percentage_setting"), int):
        idx = obj["m_damage_resistance_percentage_setting"]
        if 0 <= idx < len(H3_DAMAGE_RESISTANCE):
            obj["m_damage_resistance_percentage_setting"] = H3_DAMAGE_RESISTANCE[idx]
    if isinstance(obj.get("m_shield_recharge_rate_percentage_setting"), int):
        idx = obj["m_shield_recharge_rate_percentage_setting"]
        if 0 <= idx < len(H3_SHIELD_RECHARGE):
            obj["m_shield_recharge_rate_percentage_setting"] = H3_SHIELD_RECHARGE[idx]
    if isinstance(obj.get("m_vampirism_percentage_setting"), int):
        idx = obj["m_vampirism_percentage_setting"]
        if idx in H3_VAMPIRISM:
            obj["m_vampirism_percentage_setting"] = H3_VAMPIRISM[idx]
    if isinstance(obj.get("m_shield_multiplier_setting"), int):
        idx = obj["m_shield_multiplier_setting"]
        if 0 <= idx < len(H3_SHIELD_MULTIPLIER):
            obj["m_shield_multiplier_setting"] = H3_SHIELD_MULTIPLIER[idx]
    if isinstance(obj.get("m_headshot_immunity_setting"), int):
        idx = obj["m_headshot_immunity_setting"]
        if 0 <= idx < len(H3_HEADSHOT):
            obj["m_headshot_immunity_setting"] = H3_HEADSHOT[idx]
    for v in obj.values():
        convert_h3_traits(v)


def convert_map_fields(obj):
    if isinstance(obj, list):
        for item in obj:
            convert_map_fields(item)
        return
    if not isinstance(obj, dict):
        return
    if "m_map_variant_checksum" in obj and "m_original_map_rsa_signature_hash" not in obj:
        obj["m_original_map_rsa_signature_hash"] = obj.pop("m_map_variant_checksum")
    elif "m_map_variant_checksum" in obj:
        obj.pop("m_map_variant_checksum")
    for v in obj.values():
        convert_map_fields(v)


def add_reuse_timeout(obj):
    if isinstance(obj, list):
        for item in obj:
            add_reuse_timeout(item)
        return
    if not isinstance(obj, dict):
        return
    if "flags" in obj and "object_datum_index" in obj and "reuse_timeout" not in obj:
        items = list(obj.items())
        obj.clear()
        inserted = False
        for key, value in items:
            obj[key] = value
            if key == "flags" and not inserted:
                obj["reuse_timeout"] = 0
                inserted = True
        if not inserted:
            obj["reuse_timeout"] = 0
    for v in obj.values():
        add_reuse_timeout(v)


def convert_flat_reach_metadata(meta: dict) -> dict:
    if "general" in meta:
        general = meta["general"]
        if isinstance(general.get("activity"), int) and general["activity"] in REACH_ACTIVITY:
            general["activity"] = REACH_ACTIVITY[general["activity"]]
        if isinstance(general.get("game_mode"), int) and general["game_mode"] in REACH_CONTENT_GAME_MODE:
            general["game_mode"] = REACH_CONTENT_GAME_MODE[general["game_mode"]]
        return meta

    activity = meta.get("activity", "mapeditor")
    if isinstance(activity, int):
        activity = REACH_ACTIVITY.get(activity, activity)
    game_mode = meta.get("game_mode", "multiplayer")
    if isinstance(game_mode, int):
        game_mode = REACH_CONTENT_GAME_MODE.get(game_mode, game_mode)

    return {
        "general": {
            "file_type": meta.get("file_type", 5),
            "size_in_bytes": meta.get("size_in_bytes", 0),
            "unique_id": meta.get("unique_id", 0),
            "parent_unique_id": meta.get("parent_unique_id", 0),
            "root_unique_id": meta.get("root_unique_id", 0),
            "game_id": meta.get("game_id", 0),
            "activity": activity,
            "game_mode": game_mode,
            "game_engine_type": meta.get("game_engine_type", 0),
            "map_id": meta.get("map_id", 0),
        },
        "display": {
            "megalo_category_index": meta.get("megalo_category_index", -1),
        },
        "creation_history": {
            "timestamp": meta.get("creation_time") or meta.get("creation_timestamp") or "2000-01-01 00:00:00",
            "xuid": meta.get("creator_xuid", "0000000000000000"),
            "name": meta.get("creator_name", ""),
            "is_online": meta.get("creator_xuid_is_online", False),
        },
        "modification_history": {
            "timestamp": meta.get("modification_time") or meta.get("modification_timestamp") or "2000-01-01 00:00:00",
            "xuid": meta.get("modifier_xuid", "0000000000000000"),
            "name": meta.get("modifier_name", ""),
            "is_online": meta.get("modifier_xuid_is_online", False),
        },
        "name": meta.get("name", ""),
        "description": meta.get("description", ""),
    }


def convert_document(data: dict, kind: str, is_h3_release: bool) -> dict:
    data = replace_nulls(data)
    if is_h3_release and kind == "game_variants":
        convert_h3_traits(data)
    if kind == "map_variants":
        convert_map_fields(data)
        add_reuse_timeout(data)
    if data.get("m_game_engine") == "custom":
        data["m_game_engine"] = "megalogamengine"
    if isinstance(data.get("m_metadata"), dict) and (
        "creator_xuid" in data["m_metadata"] or "general" in data["m_metadata"]
    ):
        data["m_metadata"] = convert_flat_reach_metadata(data["m_metadata"])
    return data


def write_json(path: Path, data: dict):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def is_garbage_h3_map(data: dict) -> bool:
    version = data.get("m_map_variant_version")
    if version not in (12, 13, 14):
        return True
    map_id = data.get("m_map_id")
    if isinstance(map_id, int) and map_id > 10_000:
        return True
    return False


def bn1_source_for(path: Path) -> Path | None:
    name = path.name
    alias = BN1_ALIASES.get(name)
    if alias:
        candidate = path.with_name(alias)
        if candidate.exists():
            return candidate
    if not name.startswith("bn1_"):
        candidate = path.with_name("bn1_" + name)
        if candidate.exists():
            return candidate
    return None


def main():
    changed = 0
    recovered = 0
    scanned = 0
    files = [
        p
        for p in ROOT.rglob("*.json")
        if p.parent.name in ("game_variants", "map_variants")
        and "reports" not in p.parts
    ]
    for path in files:
        scanned += 1
        kind = path.parent.name
        is_h3_release = H3_RELEASE in path.parents
        original = path.read_text(encoding="utf-8")
        data = json.loads(original)
        converted = convert_document(data, kind, is_h3_release)
        text = json.dumps(converted, indent=2, ensure_ascii=False) + "\n"
        if text != original:
            path.write_text(text, encoding="utf-8")
            changed += 1

    # Recover Halo 3 maps that were decoded with the wrong struct from a bn1_ twin.
    for path in (H3_RELEASE).rglob("*.json"):
        if path.parent.name != "map_variants":
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if not is_garbage_h3_map(data):
            continue
        source = bn1_source_for(path)
        if source is None or source == path:
            continue
        recovered_data = json.loads(source.read_text(encoding="utf-8"))
        write_json(path, recovered_data)
        recovered += 1
        print(f"recovered {path.relative_to(ROOT)} from {source.name}")

    print(f"scanned={scanned} rewritten={changed} recovered_from_bn1={recovered}")


if __name__ == "__main__":
    main()
