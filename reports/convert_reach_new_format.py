"""Convert Reach variant JSON integer enums/bitfields to the current blf schema."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(r"C:\Users\codie\Projects\Blam-Title-Storage")

ACTIVE_CAMO = ["off", "on", "poor", "good", "excellent", "invisible"]
BOOLEAN_TRAIT = ["unchanged", "off", "on"]
DAMAGE_RESISTANCE = [
    "unchanged",
    "percent_10",
    "percent_50",
    "percent_90",
    "percent_100",
    "percent_110",
    "percent_150",
    "percent_200",
    "percent_300",
    "percent_500",
    "percent_1000",
    "percent_2000",
    "invulnerable",
]
DAMAGE_MODIFIER = [
    "unchanged",
    "percent_0",
    "percent_25",
    "percent_50",
    "percent_75",
    "percent_90",
    "percent_100",
    "percent_110",
    "percent_125",
    "percent_150",
    "percent_200",
    "percent_300",
    "fatality",
]
BODY_MULTIPLIER = ["unchanged", "percent_0", "percent_100", "percent_150", "percent_200", "percent_300", "percent_400"]
SHIELD_MULTIPLIER = BODY_MULTIPLIER
RECHARGE_RATE = [
    "unchanged",
    "percent_negative_25",
    "percent_negative_10",
    "percent_negative_5",
    "percent_0",
    "percent_10",
    "percent_25",
    "percent_50",
    "percent_75",
    "percent_90",
    "percent_100",
    "percent_110",
    "percent_125",
    "percent_150",
    "percent_200",
]
VAMPIRISM = ["unchanged", "percent_0", "percent_10", "percent_25", "percent_50", "percent_100"]
GRENADE_COUNT = [
    "unchanged",
    "map_default",
    "none",
    "frag_1",
    "frag_2",
    "frag_3",
    "frag_4",
    "plasma_1",
    "plasma_2",
    "plasma_3",
    "plasma_4",
    "each_1",
    "each_2",
    "each_3",
    "each_4",
]
INFINITE_AMMO = ["unchanged", "disabled", "enabled", "bottomless_clip"]
EQUIPMENT_USAGE = ["unchanged", "off", "not_with_objectives", "on"]
VEHICLE_USAGE = [
    "unchanged",
    "none",
    "passenger",
    "driver",
    "gunner",
    "not_passenger",
    "not_driver",
    "not_gunner",
    "full",
]
WAYPOINT = ["unchanged", "off", "allies", "all"]
DOUBLE_JUMP = ["unchanged", "off", "on", "triple"]
AURA = ["unchanged", "off", "team_color", "black", "white"]
FORCED_COLOR = [
    "unchanged",
    "off",
    "red",
    "blue",
    "green",
    "yellow",
    "purple",
    "orange",
    "brown",
    "pink",
    "white",
    "black",
    "zombie",
    "extra4",
]
MOTION_TRACKER = ["unchanged", "off", "allies", "normal", "enhanced"]
MOTION_TRACKER_RANGE = [
    "unchanged",
    "meters_10",
    "meters_15",
    "meters_25",
    "meters_50",
    "meters_75",
    "meters_100",
    "meters_150",
]
PLAYER_SPEED = [
    "unchanged",
    "percent_0",
    "percent_25",
    "percent_50",
    "percent_75",
    "percent_90",
    "percent_100",
    "percent_110",
    "percent_120",
    "percent_130",
    "percent_140",
    "percent_150",
    "percent_160",
    "percent_170",
    "percent_180",
    "percent_190",
    "percent_200",
    "percent_300",
]
PLAYER_GRAVITY = [
    "unchanged",
    "percent_50",
    "percent_75",
    "percent_100",
    "percent_110",
    "percent_120",
    "percent_130",
    "percent_140",
    "percent_150",
    "percent_160",
    "percent_170",
    "percent_180",
    "percent_190",
    "percent_200",
]
TEAM_CHANGING = ["disabled", "enabled", "balancing_only"]
TEAM_SCORING = ["sum", "minimum", "maximum"]
TEAM_MODEL_OVERRIDE = ["none", "spartan", "elite", "set_by_team", "by_designator"]
DESIGNATOR_SWITCH = ["none", "random", "rotate"]
PLAYER_MODEL = ["spartan", "elite"]
TEAM_DESIGNATOR = {
    -1: "none",
    0: "defenders",
    1: "attackers",
    2: "third_party",
    3: "fourth_party",
    4: "fifth_party",
    5: "sixth_party",
    6: "seventh_party",
    7: "eighth_party",
    8: "neutral",
}
SOCIAL_FLAGS = [
    "friendly_fire_enabled",
    "betrayal_booting_enabled",
    "enemy_voice_enabled",
    "open_channel_voice_enabled",
    "dead_player_voice_enabled",
]
MAP_OVERRIDE_FLAGS = [
    "grenades_on_map",
    "shortcuts_on_map",
    "equipment_on_map",
    "powerups_on_map",
    "turrets_on_map",
    "indestructible_vehicles",
]
LOADOUT_FLAGS = ["spartan_loadouts_enabled", "elite_loadouts_enabled"]


def schema_for(path: Path) -> str | None:
    parts = path.parts
    try:
        idx = next(i for i, part in enumerate(parts) if part.lower() == "halo reach")
    except StopIteration:
        return None
    if idx + 1 >= len(parts):
        return None
    build = parts[idx + 1].lower()
    if build == "alpha":
        return "alpha"
    if build in ("beta", "delta", "demo"):
        return "delta"
    if build == "release":
        return "release"
    return None


def map_list(value, names):
    if isinstance(value, int) and 0 <= value < len(names):
        return names[value]
    return value


def map_dict(value, names):
    if isinstance(value, int) and value in names:
        return names[value]
    return value


def int_to_bitfield(value, names):
    if not isinstance(value, int):
        return value
    return {name: bool((value >> i) & 1) for i, name in enumerate(names)}


def convert_shield(obj: dict, schema: str) -> None:
    if schema == "alpha":
        return
    mapping = {
        "m_damage_resistance_percentage_setting": DAMAGE_RESISTANCE,
        "m_body_multiplier": BODY_MULTIPLIER,
        "m_body_recharge_rate": RECHARGE_RATE,
        "m_shield_multiplier": SHIELD_MULTIPLIER,
        "m_shield_recharge_rate": RECHARGE_RATE,
        "m_overshield_recharge_rate": RECHARGE_RATE,
        "m_headshot_immunity_setting": BOOLEAN_TRAIT,
        "m_vampirism_percentage_setting": VAMPIRISM,
        "m_assasination_immunity": BOOLEAN_TRAIT,
        "m_cannot_die_from_damage": BOOLEAN_TRAIT,
    }
    for key, names in mapping.items():
        if key in obj:
            obj[key] = map_list(obj[key], names)


def convert_weapons(obj: dict, schema: str) -> None:
    if schema != "release":
        return
    mapping = {
        "m_damage_modifier_percentage_setting": DAMAGE_MODIFIER,
        "m_melee_damage_modifier_percentage_setting": DAMAGE_MODIFIER,
        "m_initial_grenade_count_setting": GRENADE_COUNT,
        "m_infinite_ammo_setting": INFINITE_AMMO,
        "m_recharging_grenades_setting": BOOLEAN_TRAIT,
        "m_weapon_pickup_setting": BOOLEAN_TRAIT,
        "m_equipment_usage_setting": EQUIPMENT_USAGE,
        "m_equipment_drop_on_death_setting": BOOLEAN_TRAIT,
        "m_infinite_equipment_setting": BOOLEAN_TRAIT,
    }
    for key, names in mapping.items():
        if key in obj:
            obj[key] = map_list(obj[key], names)


def convert_movement(obj: dict, schema: str) -> None:
    if schema != "release":
        return
    mapping = {
        "m_speed_setting": PLAYER_SPEED,
        "m_gravity_setting": PLAYER_GRAVITY,
        "m_vehicle_usage_setting": VEHICLE_USAGE,
        "m_double_jump_setting": DOUBLE_JUMP,
    }
    for key, names in mapping.items():
        if key in obj:
            obj[key] = map_list(obj[key], names)
    jump = obj.get("m_jump_modifier")
    if isinstance(jump, float):
        obj["m_jump_modifier"] = int(jump)


def convert_appearance(obj: dict, schema: str) -> None:
    if "m_active_camo_setting" in obj:
        obj["m_active_camo_setting"] = map_list(obj["m_active_camo_setting"], ACTIVE_CAMO)
    if schema != "release":
        return
    mapping = {
        "m_waypoint_setting": WAYPOINT,
        "m_gamertag_setting": WAYPOINT,
        "m_aura_setting": AURA,
        "m_forced_change_color_setting": FORCED_COLOR,
    }
    for key, names in mapping.items():
        if key in obj:
            obj[key] = map_list(obj[key], names)


def convert_sensors(obj: dict, schema: str) -> None:
    if schema != "release":
        return
    mapping = {
        "m_motion_tracker_setting": MOTION_TRACKER,
        "m_motion_tracker_range_setting": MOTION_TRACKER_RANGE,
        "m_directional_damage_setting": BOOLEAN_TRAIT,
    }
    for key, names in mapping.items():
        if key in obj:
            obj[key] = map_list(obj[key], names)


def convert_social(obj: dict) -> None:
    obj["m_flags"] = int_to_bitfield(obj.get("m_flags"), SOCIAL_FLAGS)
    if "m_team_changing" in obj:
        obj["m_team_changing"] = map_list(obj["m_team_changing"], TEAM_CHANGING)


def convert_team_entry(obj: dict) -> None:
    if "m_team_initial_designator" in obj:
        obj["m_team_initial_designator"] = map_dict(obj["m_team_initial_designator"], TEAM_DESIGNATOR)
    if "m_model_override" in obj:
        obj["m_model_override"] = map_list(obj["m_model_override"], PLAYER_MODEL)


def convert_team_options(obj: dict, schema: str) -> None:
    if "m_designator_switch_type" in obj:
        obj["m_designator_switch_type"] = map_list(obj["m_designator_switch_type"], DESIGNATOR_SWITCH)
    if schema != "release" and "m_model_override" in obj:
        obj["m_model_override"] = map_list(obj["m_model_override"], TEAM_MODEL_OVERRIDE)
    teams = obj.get("m_teams")
    if schema != "release" and isinstance(teams, list):
        for team in teams:
            if isinstance(team, dict):
                convert_team_entry(team)


def walk(obj, schema: str, parent: str | None = None) -> None:
    if isinstance(obj, list):
        for item in obj:
            walk(item, schema, parent)
        return
    if not isinstance(obj, dict):
        return

    if parent == "m_shield_vitality_traits":
        convert_shield(obj, schema)
    elif parent == "m_weapon_traits":
        convert_weapons(obj, schema)
    elif parent == "m_movement_traits":
        convert_movement(obj, schema)
    elif parent == "m_appearance_traits":
        convert_appearance(obj, schema)
    elif parent == "m_sensor_traits":
        convert_sensors(obj, schema)
    elif parent == "m_social_options":
        convert_social(obj)
    elif parent == "m_map_override_options" and schema == "release":
        obj["m_flags"] = int_to_bitfield(obj.get("m_flags"), MAP_OVERRIDE_FLAGS)
    elif parent == "m_team_options":
        convert_team_options(obj, schema)
    elif parent is None or parent not in ("m_teams",):
        pass

    if "m_team_scoring_method" in obj:
        obj["m_team_scoring_method"] = map_list(obj["m_team_scoring_method"], TEAM_SCORING)

    if schema == "release" and "m_loadout_palettes" in obj:
        obj["m_flags"] = int_to_bitfield(obj.get("m_flags"), LOADOUT_FLAGS)
    if schema == "release" and "m_visible" in obj and "m_initial_grenade_count_setting" in obj:
        obj["m_initial_grenade_count_setting"] = map_list(
            obj["m_initial_grenade_count_setting"], GRENADE_COUNT
        )

    for key, value in obj.items():
        walk(value, schema, key)


def main():
    changed = 0
    scanned = 0
    for path in ROOT.rglob("*.json"):
        if path.parent.name != "game_variants" or "reports" in path.parts:
            continue
        schema = schema_for(path)
        if schema is None:
            continue
        scanned += 1
        original = path.read_text(encoding="utf-8")
        data = json.loads(original)
        walk(data, schema)
        text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
        if text != original:
            path.write_text(text, encoding="utf-8")
            changed += 1
    print(f"scanned={scanned} rewritten={changed}")


if __name__ == "__main__":
    main()
