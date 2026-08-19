"""Remap old Reach megalo action/condition JSON to the current blf schema."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(r"C:\Users\codie\Projects\Blam-Title-Storage")

# Already-correct parameter wrappers keep their type; only rename m_type.
CONDITION_RENAME = {
    "compare": "if",
    "killer_type_is": "player_died",
    "is_zero": "timer_expired",
    "is_of_type": "object_is_type",
    "has_any_players": "team_is_active",
    "is_out_of_bounds": "object_out_of_bounds",
    "has_forge_label": "object_matches_filter",
    "shape_contains": "object_in_area",
    "is_not_respawning": "player_is_active",
}

ACTION_RENAME = {
    "modify_variable": "set",
    "run_nested_trigger": "for_each",
    "send_incident": "submit_incident",
    "set_timer_rate": "timer_set_rate",
    "reset_timer": "timer_reset",
    "set_waypoint_visibility": "navpoint_set_visible",
    "set_waypoint_priority": "navpoint_set_priority",
    "set_waypoint_icon": "navpoint_set_icon",
    "set_waypoint_timer": "navpoint_set_timer",
    "set_waypoint_text": "navpoint_set_text",
    "set_waypoint_distance": "navpoint_set_visible_range",
    "set_objective_text": "player_set_objective",
    "set_text": "hud_widget_set_text",
    "set_visibility": "hud_widget_set_visibility",
    "set_icon": "hud_widget_set_icon",
    "set_meter_parameters": "hud_widget_set_meter",
    "get_killer": "player_death_get_killing_player",
    "get_death_damage_modifier": "player_death_get_damage_type",
    "get_player_killstreak": "player_get_killing_spree_count",
    "get_player_scoreboard_position": "player_get_place",
    "get_team_scoreboard_pos": "team_get_place",
    "place_at_me": "create_object",
    "set_object_invincibility": "object_set_invincibility",
    "set_object_shape_visibility": "boundary_set_visible",
    "set_object_progress_bar": "set_progress_bar",
    "set_object_shape": "set_boundary",
    "get_carrier": "get_player_holding_object",
    "kill_object_instantly": "object_destroy",
    "set_spawn_location_permissions": "set_respawn_filter",
    "set_weapon_pickup_permissions": "set_pickup_filter",
    "set_spawn_location_permissions": "set_respawn_filter",
    "set_weapon_pickup_permissions": "set_pickup_filter",
    "set_weapon_pickup_priority": "weapon_set_pickup_priority",
    "animate_device_position": "device_animate_position",
    "set_device_position": "device_set_position",
    "set_device_power": "device_set_power",
    "set_device_position_track": "device_set_position_track",
    "set_device_actual_position": "device_set_position_immediate",
    "get_device_position": "device_get_position",
    "set_primary_respawn_object_for_player": "player_set_primary_respawn_object",
    "set_player_requisition_purchase_modes": "player_enable_purchases",
    "attach_objects": "object_attach",
    "detach": "object_detach",
    "enable_disable_spawn_zone": "respawn_zone_enable",
    "set_co_op_spawning": "team_set_coop_spawning",
    "modify_player_grenades": "adjust_grenades",
    "modify_object_shields": "object_adjust_shield",
    "get_object_health": "object_get_health",
    "get_distance": "object_get_distance",
    "get_vehicle": "player_get_vehicle",
    "get_speed": "object_get_velocity",
    "enable_disable_object_garbage_collection": "object_set_never_garbage",
    "get_player_weapon": "player_get_weapon",
    "show_message_to": "hud_post_message",
    "random_number": "random",
    "unknown_53": "object_get_shield",
    "unknown_68": "player_set_requisition_palette",
    "unknown_69": "player_set_fireteam_tier",
    "unknown_72": "give_weapon",
    "unknown_73": "give_weapon",
    "unknown_77": "set_loadout",
    "unknown_78": "set_loadout_palette",
    "unknown_91": "player_set_coop_spawning",
    "unknown_92": "player_set_coop_spawning",
}


def pop_fields(obj: dict, *names):
    out = {}
    for name in names:
        if name in obj:
            out[name] = obj.pop(name)
    return out


def wrap(obj: dict, param_key: str, mapping: dict[str, str]) -> None:
    if param_key in obj:
        return
    params = {}
    for old, new in mapping.items():
        if old in obj:
            params[new] = obj.pop(old)
    if params:
        obj[param_key] = params


def convert_condition(item: dict) -> None:
    old = item.get("m_type")
    item["m_type"] = CONDITION_RENAME.get(old, old)
    wrap(item, "m_timer_expired_parameters", {"m_timer": "m_timer"})
    wrap(item, "m_team_is_active_parameters", {"m_team_reference": "m_team"})
    wrap(item, "m_player_is_active_parameters", {"m_player_reference_1": "m_player"})
    wrap(
        item,
        "m_object_is_type_parameters",
        {"m_object_reference_1": "m_object", "m_object_type_reference": "m_object_type"},
    )
    wrap(item, "m_object_out_of_bounds_parameters", {"m_object_reference_1": "m_object"})
    wrap(
        item,
        "m_object_in_area_parameters",
        {"m_object_reference_1": "m_object_reference_1", "m_object_reference_2": "m_object_reference_2"},
    )


ACTION_WRAP = {
    "delete_object": ("m_delete_object_parameters", {"m_object_1": "m_object"}),
    "object_destroy": ("m_object_destroy_parameters", {"m_object_1": "m_object"}),
    "object_detach": ("m_object_detach_parameters", {"m_object_1": "m_object"}),
    "player_death_get_killing_player": (
        "m_player_death_get_killing_player_parameters",
        {"m_player_1": "m_player_1", "m_player_2": "m_player_2"},
    ),
    "player_death_get_damage_type": (
        "m_player_death_get_damage_type_parameters",
        {"m_player_1": "m_player", "m_variable_1": "m_variable"},
    ),
    "player_get_killing_spree_count": (
        "m_player_get_killing_spree_count_parameters",
        {"m_player_1": "m_player", "m_variable_1": "m_variable"},
    ),
    "player_get_place": (
        "m_player_get_place_parameters",
        {"m_player_1": "m_player", "m_variable_1": "m_variable"},
    ),
    "team_get_place": (
        "m_team_get_place_parameters",
        {"m_team": "m_team", "m_variable_1": "m_variable"},
    ),
    "player_set_objective": (
        "m_player_set_objective_parameters",
        {"m_player_1": "m_player", "m_string": "m_string"},
    ),
    "set_loadout_palette": (
        "m_set_loadout_palette_parameters",
        {"m_target": "m_target", "m_unknown_data": "m_palette_index"},
    ),
    "set_loadout": (
        "m_set_loadout_parameters",
        {"m_target": "m_target", "m_unknown_data": "m_palette_index"},
    ),
    "timer_reset": ("m_timer_reset_parameters", {"m_timer": "m_timer"}),
    "get_player_holding_object": (
        "m_get_player_holding_object_parameters",
        {"m_object_1": "m_object", "m_player_1": "m_player"},
    ),
    "object_set_invincibility": (
        "m_object_set_invincibility_parameters",
        {"m_object_1": "m_object", "m_variable_1": "m_variable"},
    ),
    "object_get_health": (
        "m_object_get_health_parameters",
        {"m_object_1": "m_object", "m_variable_1": "m_variable"},
    ),
    "object_get_velocity": (
        "m_object_get_velocity_parameters",
        {"m_object_1": "m_object", "m_variable_1": "m_variable"},
    ),
    "object_get_shield": (
        "m_object_get_shield_parameters",
        {"m_object_1": "m_object", "m_variable_1": "m_variable"},
    ),
    "object_set_never_garbage": (
        "m_object_set_never_garbage_parameters",
        {"m_object_1": "m_object", "m_variable_1": "m_variable"},
    ),
    "respawn_zone_enable": (
        "m_respawn_zone_enable_parameters",
        {"m_object_1": "m_object", "m_variable_1": "m_variable"},
    ),
    "device_set_power": (
        "m_device_set_power_parameters",
        {"m_object_1": "m_object", "m_variable_1": "m_variable"},
    ),
    "device_set_position": (
        "m_device_set_position_parameters",
        {"m_object_1": "m_object", "m_variable_1": "m_variable"},
    ),
    "device_get_position": (
        "m_device_get_position_parameters",
        {"m_object_1": "m_object", "m_variable_1": "m_variable"},
    ),
    "device_set_position_immediate": (
        "m_device_set_position_immediate_parameters",
        {"m_object_1": "m_object", "m_variable_1": "m_variable"},
    ),
    "player_set_primary_respawn_object": (
        "m_player_set_primary_respawn_object_parameters",
        {"m_object_1": "m_object", "m_player_1": "m_player"},
    ),
    "player_get_vehicle": (
        "m_player_get_vehicle_parameters",
        {"m_object_1": "m_object", "m_player_1": "m_player"},
    ),
    "navpoint_set_text": (
        "m_navpoint_set_text_parameters",
        {"m_object_1": "m_object", "m_string": "m_string"},
    ),
    "navpoint_set_visible": (
        "m_navpoint_set_visible_parameters",
        {"m_object_1": "m_object", "m_unknown_data": "m_value"},
    ),
    "navpoint_set_priority": (
        "m_navpoint_set_priority_parameters",
        {"m_object_1": "m_object", "m_unknown_data": "m_value"},
    ),
    "set_respawn_filter": (
        "m_set_respawn_filter_parameters",
        {"m_object_1": "m_object", "m_unknown_data": "m_value"},
    ),
    "set_pickup_filter": (
        "m_set_pickup_filter_parameters",
        {"m_object_1": "m_object", "m_unknown_data": "m_value"},
    ),
    "boundary_set_visible": (
        "m_boundary_set_visible_parameters",
        {"m_object_1": "m_object", "m_variable_1": "m_variable"},
    ),
    "random": (
        "m_random_parameters",
        {"m_variable_1": "m_variable_1", "m_variable_2": "m_variable_2"},
    ),
    "give_weapon": (
        "m_give_weapon_parameters",
        {"m_object_type": "m_object_type", "m_player_1": "m_player", "m_unknown_data": "m_flag"},
    ),
    "player_set_requisition_palette": (
        "m_player_set_requisition_palette_parameters",
        {"m_player_1": "m_player", "m_variable_1": "m_variable"},
    ),
    "player_set_fireteam_tier": (
        "m_player_set_fireteam_tier_parameters",
        {"m_player_1": "m_player", "m_variable_1": "m_variable"},
    ),
    "player_set_coop_spawning": (
        "m_player_set_coop_spawning_parameters",
        {"m_player_1": "m_player", "m_unknown_data": "m_enabled"},
    ),
}


def convert_action(item: dict) -> None:
    old = item.get("m_type")
    item["m_type"] = ACTION_RENAME.get(old, old)
    new = item["m_type"]

    if "m_hud_widget_text_base" in item and "m_hud_widget_set_text_parameters" not in item:
        item["m_hud_widget_set_text_parameters"] = item.pop("m_hud_widget_text_base")
    if "m_vitality_adjustment_parameters" in item and "m_object_adjust_shield_parameters" not in item:
        item["m_object_adjust_shield_parameters"] = item.pop("m_vitality_adjustment_parameters")

    spec = ACTION_WRAP.get(new)
    if spec:
        wrap(item, spec[0], spec[1])


def convert_engine(engine: dict) -> None:
    for item in engine.get("m_conditions") or []:
        if isinstance(item, dict):
            convert_condition(item)
    for item in engine.get("m_actions") or []:
        if isinstance(item, dict):
            convert_action(item)


def convert_document(data: dict) -> None:
    custom = data.get("m_custom_variant")
    if isinstance(custom, dict) and isinstance(custom.get("m_game_engine"), dict):
        convert_engine(custom["m_game_engine"])


def main():
    changed = 0
    scanned = 0
    for path in ROOT.rglob("*.json"):
        if path.parent.name != "game_variants" or "reports" in path.parts:
            continue
        if "Halo Reach" not in path.parts:
            continue
        scanned += 1
        original = path.read_text(encoding="utf-8")
        data = json.loads(original)
        convert_document(data)
        text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
        if text != original:
            path.write_text(text, encoding="utf-8")
            changed += 1
    print(f"scanned={scanned} rewritten={changed}")


if __name__ == "__main__":
    main()
