"""Pytest binary .aoe2scenario Runtime CTD validator for Silmarillion: Fall of Gondolin."""

from __future__ import annotations

from collections import defaultdict, deque
import math
import os
from pathlib import Path
import sys
import types
from typing import Any

from AoE2ScenarioParser.datasets.buildings import BuildingInfo
from AoE2ScenarioParser.datasets.conditions import ConditionId
from AoE2ScenarioParser.datasets.effects import EffectId
from AoE2ScenarioParser.datasets.heroes import HeroInfo
from AoE2ScenarioParser.datasets.other import OtherInfo
from AoE2ScenarioParser.datasets.players import AiType, PlayerId
from AoE2ScenarioParser.datasets.projectiles import ProjectileInfo
from AoE2ScenarioParser.datasets.units import UnitInfo
from AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario
import pytest

SCENARIO_DIR: Path = Path(__file__).resolve().parent

ARMOR_ATTACK_ATTRS: frozenset[int] = frozenset({8, 9})  # 8 = Armor, 9 = Attack
MODIFY_ATTR_EFFECT_IDS: frozenset[int] = frozenset(
    {
        int(EffectId.MODIFY_ATTRIBUTE),
        int(EffectId.MODIFY_ATTRIBUTE_FOR_CLASS),
        int(EffectId.MODIFY_OBJECT_ATTRIBUTE),
    }
)
AREA_REQUIRED_COND_IDS: frozenset[int] = frozenset(
    {
        int(ConditionId.OBJECTS_IN_AREA),
        int(ConditionId.BRING_OBJECT_TO_AREA),
    }
)
STRICT_POINT_EFFECT_IDS: frozenset[int] = frozenset(
    {
        int(EffectId.CREATE_OBJECT),
        int(EffectId.PLACE_FOUNDATION),
        int(EffectId.BUILD_OBJECT),
        int(EffectId.CHANGE_VIEW),
    }
)
POINT_OR_REF_EFFECT_IDS: frozenset[int] = frozenset(
    {
        int(EffectId.TELEPORT_OBJECT),
        int(EffectId.ATTACK_MOVE),
        int(EffectId.PATROL),
        int(EffectId.SET_BUILDING_GATHER_POINT),
    }
)
KNOWN_DEAD_UNIT_FALLBACKS: dict[int, str] = {
    693: "DEAD_ID(UnitInfo.BERSERK=692)",
    756: "DEAD_ID(UnitInfo.TARKHAN=755)",
    867: "DEAD_ID(UnitInfo.GENOESE_CROSSBOWMAN=866)",
    1124: "DEAD_ID(UnitInfo.KARAMBIT_WARRIOR=1123)",
    1130: "DEAD_ID(UnitInfo.RATTAN_ARCHER=1129)",
}


def _ensure_local_import_path() -> None:
    dir_str = str(SCENARIO_DIR)
    if dir_str not in sys.path:
        sys.path.insert(0, dir_str)


def _effect_name(eff_type: int) -> str:
    try:
        return EffectId(eff_type).name
    except ValueError:
        return f"UNKNOWN_EFFECT({eff_type})"


def _condition_name(cond_type: int) -> str:
    try:
        return ConditionId(cond_type).name
    except ValueError:
        return f"UNKNOWN_CONDITION({cond_type})"


def _trigger_label(t_idx: int, trig: Any) -> str:
    tid = getattr(trig, "trigger_id", t_idx)
    return f"Trigger #{tid} '{trig.name}'"


def _ordered_effects(trig: Any) -> tuple[list[tuple[int, int, Any]], list[str]]:
    """Return effects in execution order (pos, raw_idx, eff) plus any corrupted effect_order errors."""
    order_errors: list[str] = []
    raw_order = list(getattr(trig, "effect_order", []) or [])
    if not raw_order:
        raw_order = list(range(len(trig.effects)))
    elif len(raw_order) != len(trig.effects):
        order_errors.append(
            f"Niezgodna dlugosc effect_order ({len(raw_order)}) wzgledem effects ({len(trig.effects)})"
        )

    ordered: list[tuple[int, int, Any]] = []
    for pos, eff_idx in enumerate(raw_order):
        if 0 <= eff_idx < len(trig.effects):
            ordered.append((pos, eff_idx, trig.effects[eff_idx]))
        else:
            order_errors.append(
                f"effect_order[{pos}]={eff_idx} wychodzi poza zakres effects (0..{len(trig.effects) - 1})"
            )
    return ordered, order_errors


def _has_positive_timer(trig: Any) -> bool:
    """Return True if trigger has at least one non-inverted TIMER condition with timer >= 1."""
    for cond in trig.conditions:
        if (
            int(cond.condition_type) == int(ConditionId.TIMER)
            and int(getattr(cond, "inverted", 0)) != 1
            and int(getattr(cond, "timer", -1)) >= 1
        ):
            return True
    return False


def build_dead_and_projectile_catalog() -> tuple[dict[int, str], dict[int, str]]:
    """Build lookup tables for Genie DEAD_ID corpse objects and ProjectileInfo objects."""
    dead_map: dict[int, str] = dict(KNOWN_DEAD_UNIT_FALLBACKS)
    for label, enum_cls in (
        ("UnitInfo", UnitInfo),
        ("HeroInfo", HeroInfo),
        ("BuildingInfo", BuildingInfo),
        ("OtherInfo", OtherInfo),
    ):
        for item in enum_cls:
            dead_id = getattr(item, "DEAD_ID", None)
            if dead_id is not None and int(dead_id) >= 0:
                dead_map.setdefault(
                    int(dead_id),
                    f"DEAD_ID({label}.{item.name}={int(item.ID)})",
                )

    proj_map: dict[int, str] = {
        int(proj.ID): f"ProjectileInfo.{proj.name}" for proj in ProjectileInfo
    }
    return dead_map, proj_map


def build_valid_live_object_catalog() -> set[int]:
    """Return all valid placeable/targetable Genie IDs across UnitInfo, HeroInfo, BuildingInfo, and OtherInfo."""
    valid_ids: set[int] = set()
    for enum_cls in (UnitInfo, HeroInfo, BuildingInfo, OtherInfo):
        for item in enum_cls:
            uid = getattr(item, "ID", None)
            if uid is not None and int(uid) >= 0:
                valid_ids.add(int(uid))
    return valid_ids


# =============================================================================
# 1. MODIFY ATTRIBUTE: BRAKUJACE ARMOUR_ATTACK_CLASS
# =============================================================================
def check_modify_attribute_classes(scenario: Any) -> list[str]:
    """Check all Modify Attribute effects for missing or corrupted armour_attack_class / quantity."""
    errors: list[str] = []
    for t_idx, trig in enumerate(scenario.trigger_manager.triggers):
        t_lbl = _trigger_label(t_idx, trig)
        ordered, _ = _ordered_effects(trig)
        for pos, eff_idx, eff in ordered:
            eff_type = int(eff.effect_type)
            if eff_type not in MODIFY_ATTR_EFFECT_IDS:
                continue
            attr_id = int(getattr(eff, "object_attributes", -1))
            u_id = int(getattr(eff, "object_list_unit_id", -1))
            ctx = f"[{t_lbl}, Effect pos={pos} (idx={eff_idx}, {_effect_name(eff_type)}, unit={u_id}, attr={attr_id})]"

            if attr_id < 0:
                errors.append(f"{ctx}: Nieustawione object_attributes={attr_id}.")
            elif attr_id in ARMOR_ATTACK_ATTRS:
                aa_cls = getattr(eff, "armour_attack_class", None)
                aa_qty = getattr(eff, "armour_attack_quantity", None)
                raw_qty = getattr(eff, "quantity", -1)
                if aa_cls is None or int(aa_cls) < 0 or int(aa_cls) > 63 or raw_qty == -1:
                    errors.append(
                        f"{ctx}: Brakujace lub ujemne armour_attack_class={aa_cls} "
                        f"(raw_quantity={raw_qty}) dla atrybutu pancerza/ataku ({attr_id}) -> Runtime CTD!"
                    )
                elif int(aa_cls) == 0:
                    errors.append(
                        f"{ctx}: armour_attack_class=0 (nieuzywana klasa 0 - prawdopodobnie przekazano "
                        f"quantity zamiast armour_attack_class/armour_attack_quantity, raw_quantity={raw_qty})."
                    )
                if aa_qty is None or int(aa_qty) < 0 or int(aa_qty) >= 32768:
                    errors.append(
                        f"{ctx}: Nieprawidlowe armour_attack_quantity={aa_qty} (przepelnienie uint16/uint8)."
                    )
            else:
                qty = getattr(eff, "quantity", None)
                op_id = int(getattr(eff, "operation", -1))
                if qty is None or float(qty) == -1.0:
                    errors.append(
                        f"{ctx}: Brakujace quantity={qty} dla skalarnego atrybutu obiektu (attr={attr_id})."
                    )
                elif attr_id == 0 and op_id in (1, 3, 4) and float(qty) <= 0.0:
                    errors.append(
                        f"{ctx}: Niebezpieczna operacja na HIT_POINTS (operation={op_id}, quantity={qty}) "
                        f"-> obciecie float->int=0 lub ustawienie <=0 Max HP!"
                    )
    return errors


# =============================================================================
# 2. PETLE TRIGGEROW BEZ WARUNKU TIMER
# =============================================================================
def check_trigger_loops_have_timer(scenario: Any) -> list[str]:
    """Detect direct looping=True triggers without Timer>=1 and timerless activate_trigger cycles."""
    errors: list[str] = []
    triggers = scenario.trigger_manager.triggers
    num_trigs = len(triggers)

    has_timer: dict[int, bool] = {}
    for t_idx, trig in enumerate(triggers):
        has_t = _has_positive_timer(trig)
        has_timer[t_idx] = has_t
        if int(getattr(trig, "looping", 0)) == 1 and not has_t:
            timers_found = [
                (int(getattr(c, "timer", -1)), int(getattr(c, "inverted", 0)))
                for c in trig.conditions
                if int(c.condition_type) == int(ConditionId.TIMER)
            ]
            errors.append(
                f"[{_trigger_label(t_idx, trig)}]: Petla tickowa (looping=True) bez aktywnego warunku "
                f"Timer >= 1 (znalezione timery={timers_found}) -> ryzyko zawieszenia watku glownego C++!"
            )

    # Check directed cycles in the subgraph of triggers WITHOUT Timer >= 1
    adj: dict[int, list[int]] = defaultdict(list)
    for t_idx, trig in enumerate(triggers):
        if has_timer[t_idx]:
            continue
        for eff in trig.effects:
            if int(eff.effect_type) == int(EffectId.ACTIVATE_TRIGGER):
                target = int(getattr(eff, "trigger_id", -1))
                if 0 <= target < num_trigs and not has_timer[target]:
                    adj[t_idx].append(target)

    color: dict[int, int] = dict.fromkeys(range(num_trigs), 0)
    stack: list[int] = []
    reported_cycles: set[tuple[int, ...]] = set()

    def dfs(u: int) -> None:
        color[u] = 1
        stack.append(u)
        for v in adj.get(u, ()):
            if color[v] == 1:
                cycle_start = stack.index(v)
                cycle = stack[cycle_start:]
                min_pos = min(range(len(cycle)), key=lambda i: cycle[i])
                canonical = tuple(cycle[min_pos:] + cycle[:min_pos])
                if canonical not in reported_cycles:
                    reported_cycles.add(canonical)
                    chain_str = " -> ".join(
                        f"#{ idx } '{triggers[idx].name}'" for idx in [*canonical, canonical[0]]
                    )
                    errors.append(
                        f"[Cykl ACTIVATE_TRIGGER bez Timer >= 1]: {chain_str} -> ryzyko nieskonczonej petli klatkowej!"
                    )
            elif color[v] == 0:
                dfs(v)
        stack.pop()
        color[u] = 2

    for node in range(num_trigs):
        if not has_timer[node] and color[node] == 0:
            dfs(node)

    return errors


# =============================================================================
# 3. ODWROCONE I NIEKOMPLETNE PROSTOKATY OBSZAROW
# =============================================================================
def _check_single_area(
    ctx: str,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    require_area: bool = False,
) -> list[str]:
    coords = (x1, y1, x2, y2)
    if coords == (-1, -1, -1, -1):
        if require_area:
            return [f"{ctx}: Wymagany prostokat obszaru jest nieustawiony (-1, -1, -1, -1)!"]
        return []
    if any(c < 0 for c in coords):
        return [
            f"{ctx}: Czesciowo niezainicjalizowany lub ujemny obszar "
            f"(area_x1={x1}, area_y1={y1}, area_x2={x2}, area_y2={y2})!"
        ]
    errs: list[str] = []
    if x1 > x2:
        errs.append(
            f"{ctx}: Odwrocony prostokat w osi X: area_x1 ({x1}) > area_x2 ({x2}) "
            f"[pelny obszar: ({x1}, {y1})..({x2}, {y2})] -> Runtime CTD!"
        )
    if y1 > y2:
        errs.append(
            f"{ctx}: Odwrocony prostokat w osi Y: area_y1 ({y1}) > area_y2 ({y2}) "
            f"[pelny obszar: ({x1}, {y1})..({x2}, {y2})] -> Runtime CTD!"
        )
    return errs


def check_inverted_or_partial_areas(scenario: Any) -> list[str]:
    """Verify all condition and effect area rectangles satisfy x1 <= x2 and y1 <= y2."""
    errors: list[str] = []
    for t_idx, trig in enumerate(scenario.trigger_manager.triggers):
        t_lbl = _trigger_label(t_idx, trig)
        for c_idx, cond in enumerate(trig.conditions):
            c_type = int(cond.condition_type)
            ctx = f"[{t_lbl}, Condition #{c_idx} ({_condition_name(c_type)})]"
            errors.extend(
                _check_single_area(
                    ctx,
                    int(getattr(cond, "area_x1", -1)),
                    int(getattr(cond, "area_y1", -1)),
                    int(getattr(cond, "area_x2", -1)),
                    int(getattr(cond, "area_y2", -1)),
                    require_area=c_type in AREA_REQUIRED_COND_IDS,
                )
            )

        ordered, _ = _ordered_effects(trig)
        for pos, eff_idx, eff in ordered:
            e_type = int(eff.effect_type)
            ctx = f"[{t_lbl}, Effect pos={pos} (idx={eff_idx}, {_effect_name(e_type)})]"
            errors.extend(
                _check_single_area(
                    ctx,
                    int(getattr(eff, "area_x1", -1)),
                    int(getattr(eff, "area_y1", -1)),
                    int(getattr(eff, "area_x2", -1)),
                    int(getattr(eff, "area_y2", -1)),
                    require_area=False,
                )
            )
    return errors


# =============================================================================
# 4. WYJSCIE WSPOLRZEDNYCH POZA MAPE
# =============================================================================
def check_coordinates_within_map_bounds(scenario: Any) -> list[str]:
    """Verify all placed units, condition areas, effect areas, and effect locations lie inside [0, map_size)."""
    errors: list[str] = []
    map_size = int(scenario.map_manager.map_size)
    um = scenario.unit_manager

    for p_idx in range(9):
        p_enum = PlayerId(p_idx)
        for u in um.get_player_units(p_enum):
            ux = float(u.x)
            uy = float(u.y)
            if (
                not math.isfinite(ux)
                or not math.isfinite(uy)
                or ux < 0.0
                or ux >= map_size
                or uy < 0.0
                or uy >= map_size
            ):
                errors.append(
                    f"[Unit ref_id={u.reference_id} unit_const={u.unit_const} player={p_enum.name}]: "
                    f"Wspolrzedne ({ux}, {uy}) poza granicami mapy [0.0, {map_size}.0)!"
                )

    for t_idx, trig in enumerate(scenario.trigger_manager.triggers):
        t_lbl = _trigger_label(t_idx, trig)

        for c_idx, cond in enumerate(trig.conditions):
            c_type = int(cond.condition_type)
            coords = (
                int(getattr(cond, "area_x1", -1)),
                int(getattr(cond, "area_y1", -1)),
                int(getattr(cond, "area_x2", -1)),
                int(getattr(cond, "area_y2", -1)),
            )
            if coords != (-1, -1, -1, -1) and any(c < 0 or c >= map_size for c in coords):
                errors.append(
                    f"[{t_lbl}, Condition #{c_idx} ({_condition_name(c_type)})]: "
                    f"Obszar {coords} wykracza poza siatke mapy [0..{map_size - 1}]!"
                )

        ordered, _ = _ordered_effects(trig)
        for pos, eff_idx, eff in ordered:
            e_type = int(eff.effect_type)
            ctx = f"[{t_lbl}, Effect pos={pos} (idx={eff_idx}, {_effect_name(e_type)})]"

            area_coords = (
                int(getattr(eff, "area_x1", -1)),
                int(getattr(eff, "area_y1", -1)),
                int(getattr(eff, "area_x2", -1)),
                int(getattr(eff, "area_y2", -1)),
            )
            if area_coords != (-1, -1, -1, -1) and any(
                c < 0 or c >= map_size for c in area_coords
            ):
                errors.append(
                    f"{ctx}: Obszar {area_coords} wykracza poza siatke mapy [0..{map_size - 1}]!"
                )

            lx = int(getattr(eff, "location_x", -1))
            ly = int(getattr(eff, "location_y", -1))
            loc_ref = int(getattr(eff, "location_object_reference", -1))

            if (lx, ly) != (-1, -1):
                if lx < 0 or lx >= map_size or ly < 0 or ly >= map_size:
                    errors.append(
                        f"{ctx}: Punkt docelowy (location_x={lx}, location_y={ly}) "
                        f"wykracza poza granice mapy [0..{map_size - 1}] -> Runtime CTD!"
                    )
            elif e_type in STRICT_POINT_EFFECT_IDS or (
                e_type in POINT_OR_REF_EFFECT_IDS and loc_ref < 0
            ):
                errors.append(
                    f"{ctx}: Wymagane wspolrzedne docelowe pozostaly nieustawione (location_x=-1, location_y=-1)!"
                )

    return errors


# =============================================================================
# 5. OPERACJE NA USUNIETYCH / ZABITYCH / NIEISTNIEJACYCH OBIEKTACH
# =============================================================================
def check_operations_on_removed_objects(scenario: Any) -> list[str]:
    """Detect dangling reference_ids, intra-trigger Use-After-Delete, looping deletes, and post-delete actions."""
    errors: list[str] = []
    um = scenario.unit_manager
    triggers = scenario.trigger_manager.triggers

    placed_by_ref: dict[int, tuple[PlayerId, Any]] = {}
    for p_idx in range(9):
        p_enum = PlayerId(p_idx)
        for u in um.get_player_units(p_enum):
            ref_id = int(u.reference_id)
            if ref_id in placed_by_ref:
                errors.append(
                    f"[UnitManager]: Zduplikowane reference_id={ref_id} (unit_const={u.unit_const}, player={p_enum.name})!"
                )
            placed_by_ref[ref_id] = (p_enum, u)

    all_referenced_ids: set[int] = set()
    removers: dict[int, set[int]] = defaultdict(set)
    killers: dict[int, set[int]] = defaultdict(set)
    destroy_watchers: dict[int, set[int]] = defaultdict(set)
    mutators: dict[int, set[int]] = defaultdict(set)
    activate_adj: dict[int, set[int]] = defaultdict(set)
    deactivate_map: dict[int, set[int]] = defaultdict(set)

    # Pass 1: Validate existence of all explicit reference_ids and intra-trigger / looping ordering
    for t_idx, trig in enumerate(triggers):
        t_lbl = _trigger_label(t_idx, trig)
        dead_in_trig: set[int] = set()

        for c_idx, cond in enumerate(trig.conditions):
            c_type = int(cond.condition_type)
            for attr_name in ("unit_object", "next_object"):
                ref_val = int(getattr(cond, attr_name, -1))
                if ref_val < -1:
                    errors.append(
                        f"[{t_lbl}, Condition #{c_idx} ({_condition_name(c_type)})]: "
                        f"Nieprawidlowe {attr_name}={ref_val}!"
                    )
                elif ref_val >= 0:
                    all_referenced_ids.add(ref_val)
                    if ref_val not in placed_by_ref:
                        errors.append(
                            f"[{t_lbl}, Condition #{c_idx} ({_condition_name(c_type)})]: "
                            f"Odwołanie do nieistniejacego na mapie obiektu {attr_name}={ref_val} -> Runtime CTD!"
                        )
                    elif c_type == int(ConditionId.DESTROY_OBJECT) and attr_name == "unit_object":
                        if int(getattr(cond, "inverted", 0)) != 1:
                            destroy_watchers[ref_val].add(t_idx)
                            dead_in_trig.add(ref_val)

        ordered, order_errs = _ordered_effects(trig)
        for oe in order_errs:
            errors.append(f"[{t_lbl}]: {oe}")

        self_deactivates = any(
            int(e.effect_type) == int(EffectId.DEACTIVATE_TRIGGER)
            and int(getattr(e, "trigger_id", -1)) == t_idx
            for _, _, e in ordered
        )
        is_looping = int(getattr(trig, "looping", 0)) == 1

        for pos, eff_idx, eff in ordered:
            e_type = int(eff.effect_type)
            ctx = f"[{t_lbl}, Effect pos={pos} (idx={eff_idx}, {_effect_name(e_type)})]"

            if e_type == int(EffectId.ACTIVATE_TRIGGER):
                tgt = int(getattr(eff, "trigger_id", -1))
                if 0 <= tgt < len(triggers):
                    activate_adj[t_idx].add(tgt)
            elif e_type == int(EffectId.DEACTIVATE_TRIGGER):
                tgt = int(getattr(eff, "trigger_id", -1))
                if 0 <= tgt < len(triggers):
                    deactivate_map[t_idx].add(tgt)

            raw_sel = list(getattr(eff, "selected_object_ids", []) or [])
            valid_sel: list[int] = []
            for oid in raw_sel:
                oid_int = int(oid)
                if oid_int < 0:
                    errors.append(f"{ctx}: Nieprawidlowe ID={oid_int} w selected_object_ids!")
                else:
                    all_referenced_ids.add(oid_int)
                    valid_sel.append(oid_int)
                    if oid_int not in placed_by_ref:
                        errors.append(
                            f"{ctx}: Operacja na nieistniejacym obiekcie selected_object_ids zawiera ref_id={oid_int} -> Runtime CTD!"
                        )

            loc_ref = int(getattr(eff, "location_object_reference", -1))
            if loc_ref < -1:
                errors.append(f"{ctx}: Nieprawidlowe location_object_reference={loc_ref}!")
            elif loc_ref >= 0:
                all_referenced_ids.add(loc_ref)
                if loc_ref not in placed_by_ref:
                    errors.append(
                        f"{ctx}: Cel location_object_reference={loc_ref} nie istnieje na mapie -> Runtime CTD!"
                    )

            touched_refs = set(valid_sel) | ({loc_ref} if loc_ref >= 0 else set())
            already_dead = sorted(touched_refs & dead_in_trig)
            if already_dead:
                errors.append(
                    f"{ctx}: Operacja na obiekcie juz usunietym/zniszczonym w tym samym triggerze "
                    f"(ref_ids={already_dead}) -> Runtime CTD!"
                )

            if e_type == int(EffectId.REMOVE_OBJECT):
                for oid_int in valid_sel:
                    removers[oid_int].add(t_idx)
                    dead_in_trig.add(oid_int)
                if is_looping and not self_deactivates and valid_sel:
                    errors.append(
                        f"{ctx}: Petla looping=True wykonuje REMOVE_OBJECT na statycznej liscie "
                        f"selected_object_ids={valid_sel[:5]} bez samodezaktywacji!"
                    )
            elif e_type == int(EffectId.KILL_OBJECT):
                for oid_int in valid_sel:
                    killers[oid_int].add(t_idx)
                    dead_in_trig.add(oid_int)
                if is_looping and not self_deactivates and valid_sel:
                    errors.append(
                        f"{ctx}: Petla looping=True wykonuje KILL_OBJECT na statycznej liscie "
                        f"selected_object_ids={valid_sel[:5]} bez samodezaktywacji!"
                    )
            else:
                for oid_int in touched_refs:
                    mutators[oid_int].add(t_idx)

    # Pass 2: Check area-based REMOVE_OBJECT / KILL_OBJECT covering any explicitly referenced static object
    for t_idx, trig in enumerate(triggers):
        for eff in trig.effects:
            e_type = int(eff.effect_type)
            if e_type not in (int(EffectId.REMOVE_OBJECT), int(EffectId.KILL_OBJECT)):
                continue
            if getattr(eff, "selected_object_ids", None):
                continue
            ax1 = int(getattr(eff, "area_x1", -1))
            ay1 = int(getattr(eff, "area_y1", -1))
            ax2 = int(getattr(eff, "area_x2", -1))
            ay2 = int(getattr(eff, "area_y2", -1))
            if (ax1, ay1, ax2, ay2) == (-1, -1, -1, -1) or ax1 > ax2 or ay1 > ay2:
                continue
            src_p = int(getattr(eff, "source_player", -1))
            u_filt = int(getattr(eff, "object_list_unit_id", -1))
            for ref_id in all_referenced_ids:
                if ref_id not in placed_by_ref:
                    continue
                p_enum, u_obj = placed_by_ref[ref_id]
                if src_p not in (-1, int(p_enum)):
                    continue
                if u_filt not in (-1, int(u_obj.unit_const)):
                    continue
                if ax1 <= int(u_obj.x) <= ax2 and ay1 <= int(u_obj.y) <= ay2:
                    if e_type == int(EffectId.REMOVE_OBJECT):
                        removers[ref_id].add(t_idx)
                    else:
                        killers[ref_id].add(t_idx)

    # Pass 3: Cross-trigger lifecycle & causal reachability checks
    def is_startup_init_trigger(t_idx: int) -> tuple[bool, int]:
        trig = triggers[t_idx]
        if int(getattr(trig, "enabled", 0)) != 1 or int(getattr(trig, "looping", 0)) != 0:
            return False, -1
        if len(trig.conditions) != 1:
            return False, -1
        cond = trig.conditions[0]
        if (
            int(cond.condition_type) == int(ConditionId.TIMER)
            and int(getattr(cond, "inverted", 0)) != 1
            and 0 <= int(getattr(cond, "timer", -1)) <= 5
        ):
            return True, int(cond.timer)
        return False, -1

    def can_fire_before_or_at(t_idx: int, max_time: int) -> bool:
        trig = triggers[t_idx]
        if int(getattr(trig, "enabled", 0)) != 1:
            return False
        for cond in trig.conditions:
            if (
                int(cond.condition_type) == int(ConditionId.TIMER)
                and int(getattr(cond, "inverted", 0)) != 1
                and int(getattr(cond, "timer", -1)) > max_time
            ):
                return False
            if int(cond.condition_type) == int(ConditionId.DESTROY_OBJECT):
                return False
        return True

    def reachable_from(start_idx: int) -> set[int]:
        visited: set[int] = set()
        queue: deque[int] = deque(activate_adj.get(start_idx, ()))
        while queue:
            curr = queue.popleft()
            if curr not in visited:
                visited.add(curr)
                queue.extend(activate_adj.get(curr, ()))
        return visited

    reach_cache: dict[int, set[int]] = {}

    for ref_id in sorted(all_referenced_ids):
        if ref_id not in placed_by_ref:
            continue
        del_trigs = sorted(removers[ref_id] | killers[ref_id])

        # 5D.1 Duplicate delete without mutual lockout
        if len(del_trigs) > 1:
            for i, t1 in enumerate(del_trigs):
                for t2 in del_trigs[i + 1 :]:
                    mutually_locked = (
                        t2 in deactivate_map[t1] and t1 in deactivate_map[t2]
                    )
                    if not mutually_locked:
                        errors.append(
                            f"[ref_id={ref_id}]: Wielokrotne usuwanie/zabijanie tego samego obiektu "
                            f"przez {_trigger_label(t1, triggers[t1])} oraz {_trigger_label(t2, triggers[t2])} "
                            "bez wzajemnej blokady DEACTIVATE_TRIGGER!"
                        )

        # 5D.2 REMOVE_OBJECT silently invalidates DESTROY_OBJECT watchers
        if removers[ref_id] and destroy_watchers[ref_id]:
            rem_names = [f"#{i} '{triggers[i].name}'" for i in sorted(removers[ref_id])]
            wat_names = [f"#{i} '{triggers[i].name}'" for i in sorted(destroy_watchers[ref_id])]
            errors.append(
                f"[ref_id={ref_id}]: Konflikt REMOVE_OBJECT ({rem_names}) z warunkiem DESTROY_OBJECT ({wat_names})!"
            )

        # 5D.3 Downstream triggers activated AFTER removal/destruction still operating on ref_id
        post_death_sources = removers[ref_id] | killers[ref_id] | destroy_watchers[ref_id]
        for src_t in sorted(post_death_sources):
            if src_t not in reach_cache:
                reach_cache[src_t] = reachable_from(src_t)
            downstream_users = sorted(
                (reach_cache[src_t] - {src_t})
                & (mutators[ref_id] | removers[ref_id] | killers[ref_id])
            )
            for dst_t in downstream_users:
                errors.append(
                    f"[ref_id={ref_id}]: {_trigger_label(dst_t, triggers[dst_t])} wykonuje operacje na obiekcie "
                    f"po jego usunieciu/zniszczeniu w {_trigger_label(src_t, triggers[src_t])} -> Runtime CTD!"
                )

        # 5D.4 Unprotected concurrent operations alongside REMOVE_OBJECT / KILL_OBJECT
        if del_trigs:
            for op_t in sorted(mutators[ref_id]):
                if op_t in del_trigs:
                    continue
                is_init, init_t = is_startup_init_trigger(op_t)
                for del_t in del_trigs:
                    if op_t in deactivate_map[del_t]:
                        continue
                    if is_init and not can_fire_before_or_at(del_t, init_t):
                        continue
                    errors.append(
                        f"[ref_id={ref_id}]: Niezabezpieczona operacja w {_trigger_label(op_t, triggers[op_t])} "
                        f"na obiekcie usuwanym/zabijanym przez {_trigger_label(del_t, triggers[del_t])}!"
                    )

    return errors


# =============================================================================
# 6. OPERACJE NA OBIEKTACH ZWLOK (DEAD_UNIT) I POCISKOW (PROJECTILEINFO)
# =============================================================================
def check_dead_or_projectile_unit_operations(scenario: Any) -> list[str]:
    """Detect corpse (DEAD_ID), projectile (ProjectileInfo), and unexposed/invalid IDs on map or in triggers."""
    errors: list[str] = []
    dead_map, proj_map = build_dead_and_projectile_catalog()
    valid_live_ids = build_valid_live_object_catalog()
    um = scenario.unit_manager

    def classify_bad_id(uid: int) -> str | None:
        if uid in dead_map:
            return f"OBIEKT_ZWLOK [{dead_map[uid]}]"
        if uid in proj_map:
            return f"POCISK [{proj_map[uid]}]"
        if uid not in valid_live_ids:
            return "NIEZNANY_OBIEKT [brak w UnitInfo/HeroInfo/BuildingInfo/OtherInfo]"
        return None

    # 6A. Pre-placed map units
    map_bad_groups: dict[tuple[str, int, str], list[tuple[float, float]]] = defaultdict(list)
    for p_idx in range(9):
        p_enum = PlayerId(p_idx)
        for u in um.get_player_units(p_enum):
            uid = int(u.unit_const)
            bad_desc = classify_bad_id(uid)
            if bad_desc is not None:
                map_bad_groups[(p_enum.name, uid, bad_desc)].append((float(u.x), float(u.y)))

    for (p_name, uid, bad_desc), coords in sorted(map_bad_groups.items()):
        sample = ", ".join(f"({x:.1f}, {y:.1f})" for x, y in coords[:3])
        errors.append(
            f"[UnitManager player={p_name} unit_const={uid} ({bad_desc})]: "
            f"Postawiono {len(coords)} szt. na mapie w 0:00 (przyklady: {sample}) -> ryzyko Runtime CTD!"
        )

    # 6B. Trigger Conditions & Effects
    for t_idx, trig in enumerate(scenario.trigger_manager.triggers):
        t_lbl = _trigger_label(t_idx, trig)

        for c_idx, cond in enumerate(trig.conditions):
            uid = int(getattr(cond, "object_list", -1))
            if uid >= 0:
                bad_desc = classify_bad_id(uid)
                if bad_desc is not None:
                    c_type = int(cond.condition_type)
                    errors.append(
                        f"[{t_lbl}, Condition #{c_idx} ({_condition_name(c_type)})]: "
                        f"Warunek odwoluje sie do object_list={uid} ({bad_desc})!"
                    )

        ordered, _ = _ordered_effects(trig)
        eff_bad_groups: dict[tuple[str, int, str], list[tuple[int, int]]] = defaultdict(list)
        for pos, eff_idx, eff in ordered:
            uid = int(getattr(eff, "object_list_unit_id", -1))
            if uid >= 0:
                bad_desc = classify_bad_id(uid)
                if bad_desc is not None:
                    e_name = _effect_name(int(eff.effect_type))
                    eff_bad_groups[(e_name, uid, bad_desc)].append((pos, eff_idx))

        for (e_name, uid, bad_desc), hits in eff_bad_groups.items():
            if len(hits) == 1:
                pos, eff_idx = hits[0]
                errors.append(
                    f"[{t_lbl}, Effect pos={pos} (idx={eff_idx}, {e_name})]: "
                    f"Efekt wykonuje operacje na object_list_unit_id={uid} ({bad_desc}) -> ryzyko Runtime CTD!"
                )
            else:
                pos_preview = ", ".join(str(p) for p, _ in hits[:6])
                if len(hits) > 6:
                    pos_preview += ", ..."
                errors.append(
                    f"[{t_lbl}, Effect {e_name} x{len(hits)} (pos={pos_preview})]: "
                    f"Efekt wykonuje operacje na object_list_unit_id={uid} ({bad_desc}) -> ryzyko Runtime CTD!"
                )

    return errors


# =============================================================================
# 7. BLOKADA PROMIDE (STANDARD AI) PRZECIWKO APPHANGB1 NA ZAMKNIETYCH SEKTORACH
# =============================================================================
def check_ai_players_locked_immobile(scenario: Any) -> list[str]:
    """Ensure P1-P8 lock Immobile AI (AiType.CUSTOM + lock_personality) to prevent PromiDE AppHangB1."""
    errors: list[str] = []
    pm = getattr(scenario, "player_manager", None)
    players = getattr(pm, "players", []) if pm is not None else []
    for idx in range(1, min(9, len(players))):
        p_obj = players[idx]
        if p_obj is None:
            continue
        ai_type = int(getattr(p_obj, "ai_type", int(AiType.STANDARD)))
        locked = bool(getattr(p_obj, "lock_personality", False))
        script = getattr(p_obj, "ai_script", "") or ""
        if ai_type != int(AiType.CUSTOM) or not locked or len(script) == 0:
            errors.append(
                f"[Player P{idx}]: ai_type={ai_type} (wymagane AiType.CUSTOM=0), "
                f"lock_personality={locked}, len(ai_script)={len(script)} "
                f"-> aktywne PromiDE na zamknietych sektorach ROCK_CLIFF_ID powoduje AppHangB1 (Sig[3]=185d)!"
            )
    return errors


# =============================================================================
# 8. BEZPIECZENSTWO BANEROW UI ORAZ FILTROWANIA DAMAGE/KILL W OBSZARZE
# =============================================================================
def check_ui_and_area_damage_safety(scenario: Any) -> list[str]:
    """Ensure display_on_screen triggers have conditions and area damage/kill filters out Map Revealers/buildings."""
    errors: list[str] = []
    area_dmg_kill_ids = frozenset({int(EffectId.DAMAGE_OBJECT), int(EffectId.KILL_OBJECT)})
    for t_idx, trig in enumerate(scenario.trigger_manager.triggers):
        t_lbl = _trigger_label(t_idx, trig)
        if int(getattr(trig, "display_on_screen", 0)) == 1 and len(trig.conditions) == 0:
            errors.append(
                f"[{t_lbl}]: Baner UI (display_on_screen=1) ma 0 warunkow -> natychmiastowe wykonanie i skreslenie w 0:00!"
            )

        ordered, _ = _ordered_effects(trig)
        for pos, eff_idx, eff in ordered:
            eff_type = int(eff.effect_type)
            if eff_type not in area_dmg_kill_ids:
                continue
            sel_ids = [sid for sid in (getattr(eff, "selected_object_ids", None) or []) if int(sid) >= 0]
            if sel_ids:
                continue
            obj_type = int(getattr(eff, "object_type", -1))
            obj_list = int(getattr(eff, "object_list_unit_id", -1))
            if obj_type == -1 and obj_list == -1:
                errors.append(
                    f"[{t_lbl}, Effect pos={pos} (idx={eff_idx}, {_effect_name(eff_type)})]: "
                    f"Niefiltrowane obszarowe {_effect_name(eff_type)} (object_type=-1, object_list_unit_id=-1) "
                    f"uszkadza Map Revealery (837), Flary (112) i budynki!"
                )
    return errors


# =============================================================================
# PYTEST FIXTURES & TEST SUITE
# =============================================================================
def _resolve_scenario_path() -> Path:
    env_override = os.environ.get("GONDOLIN_SCENARIO_PATH")
    if env_override:
        return Path(env_override)
    _ensure_local_import_path()
    import generate_gondolin_scenario

    folder = generate_gondolin_scenario.find_scenario_folder()
    candidate = folder / generate_gondolin_scenario.OUTPUT_FILENAME
    if candidate.exists():
        return candidate
    return SCENARIO_DIR / generate_gondolin_scenario.OUTPUT_FILENAME


def _assert_no_ctd_errors(category_title: str, errors: list[str]) -> None:
    if errors:
        limit = 100
        preview = "\n  - ".join(errors[:limit])
        more = (
            f"\n  ... oraz {len(errors) - limit} kolejnych bledow."
            if len(errors) > limit
            else ""
        )
        pytest.fail(
            f"Wykryto {len(errors)} bledow klasy '{category_title}':\n  - {preview}{more}",
            pytrace=False,
        )


@pytest.fixture(scope="session")
def reloaded_scenario() -> Any:
    """Load the generated .aoe2scenario binary once per pytest session."""
    scenario_path = _resolve_scenario_path()
    if not scenario_path.exists():
        pytest.fail(
            f"Nie znaleziono wygenerowanego pliku scenariusza: {scenario_path.resolve()}. "
            "Uruchom najpierw generate_gondolin_scenario.py!",
            pytrace=False,
        )
    return AoE2DEScenario.from_file(str(scenario_path))


def test_modify_attribute_armour_attack_class(reloaded_scenario: Any) -> None:
    """1. Brakujace lub uszkodzone armour_attack_class przy Modify Attribute."""
    _assert_no_ctd_errors(
        "Modify Attribute bez prawidlowego armour_attack_class",
        check_modify_attribute_classes(reloaded_scenario),
    )


def test_trigger_loops_have_timer(reloaded_scenario: Any) -> None:
    """2. Petle triggerow (looping=True oraz cykle activate_trigger) bez warunku Timer >= 1."""
    _assert_no_ctd_errors(
        "Petle triggerow bez warunku Timer >= 1",
        check_trigger_loops_have_timer(reloaded_scenario),
    )


def test_no_inverted_or_partial_areas(reloaded_scenario: Any) -> None:
    """3. Odwrocone lub czesciowo niezainicjalizowane prostokaty obszarow (area_x1 > area_x2 lub area_y1 > area_y2)."""
    _assert_no_ctd_errors(
        "Odwrocone lub niekompletne prostokaty obszarow",
        check_inverted_or_partial_areas(reloaded_scenario),
    )


def test_coordinates_within_map_bounds(reloaded_scenario: Any) -> None:
    """4. Wyjscie wspolrzednych jednostek, obszarow lub celow efektow poza granice mapy."""
    _assert_no_ctd_errors(
        "Wspolrzedne poza granicami mapy",
        check_coordinates_within_map_bounds(reloaded_scenario),
    )


def test_no_operations_on_removed_objects(reloaded_scenario: Any) -> None:
    """5. Operacje na usunietych, zabitych lub nieistniejacych obiektach (reference_id)."""
    _assert_no_ctd_errors(
        "Operacje na usunietych lub nieistniejacych obiektach",
        check_operations_on_removed_objects(reloaded_scenario),
    )


def test_no_dead_or_projectile_unit_operations(reloaded_scenario: Any) -> None:
    """6. Operacje na obiektach zwlok (DEAD_ID), pociskach (ProjectileInfo) i nieznanych ID."""
    _assert_no_ctd_errors(
        "Operacje na obiektach zwlok (dead_unit), pociskach (ProjectileInfo) i nieznanych ID",
        check_dead_or_projectile_unit_operations(reloaded_scenario),
    )


def test_ai_players_locked_immobile(reloaded_scenario: Any) -> None:
    """7. Blokada PromiDE (Immobile AI + lock_personality) przeciwko AppHangB1 na P1-P8."""
    _assert_no_ctd_errors(
        "Niezablokowane PromiDE (Standard AI) na graczach P1-P8",
        check_ai_players_locked_immobile(reloaded_scenario),
    )


def test_ui_and_area_damage_safety(reloaded_scenario: Any) -> None:
    """8. Banery UI z warunkiem Timer oraz filtrowanie obszarowych efektow DAMAGE_OBJECT / KILL_OBJECT."""
    _assert_no_ctd_errors(
        "Banery UI bez warunkow lub niefiltrowane obszarowe DAMAGE_OBJECT / KILL_OBJECT",
        check_ui_and_area_damage_safety(reloaded_scenario),
    )


def test_debug_chat_instrumentation(reloaded_scenario: Any) -> None:
    """Verify DEBUG_CHAT prepends exactly 1 Send Chat effect for P1 at index 0 of every trigger."""
    _ensure_local_import_path()
    import gondolin_config

    triggers = reloaded_scenario.trigger_manager.triggers
    assert len(triggers) > 0, "Scenariusz nie zawiera zadnych triggerow!"

    if not gondolin_config.DEBUG_CHAT:
        for idx, trig in enumerate(triggers):
            for eff in trig.effects:
                msg = getattr(eff, "message", "") or ""
                assert not msg.startswith("<AQUA>[DBG #"), (
                    f"DEBUG_CHAT=False, ale trigger #{idx} '{trig.name}' nadal zawiera log debugowy!"
                )
        return

    for idx, trig in enumerate(triggers):
        trig_id = getattr(trig, "trigger_id", idx)
        assert len(trig.effects) >= 1, f"Trigger #{trig_id} '{trig.name}' nie ma zadnych efektow!"
        assert trig.effect_order[0] == 0, (
            f"Trigger #{trig_id} '{trig.name}': effect_order[0]={trig.effect_order[0]} zamiast 0!"
        )
        first_eff = trig.effects[0]
        assert int(first_eff.effect_type) == int(EffectId.SEND_CHAT), (
            f"Trigger #{trig_id} '{trig.name}': pierwszy efekt to {first_eff.effect_type} zamiast SEND_CHAT!"
        )
        assert int(first_eff.source_player) == int(PlayerId.ONE), (
            f"Trigger #{trig_id} '{trig.name}': odbiorca Send Chat to {first_eff.source_player} zamiast P1!"
        )
        expected_msg = f"<AQUA>[DBG #{trig_id}] {trig.name}"
        assert first_eff.message == expected_msg, (
            f"Trigger #{trig_id} '{trig.name}': nieoczekiwany tekst '{first_eff.message}' != '{expected_msg}'"
        )
        dbg_count = sum(
            1
            for eff in trig.effects
            if int(eff.effect_type) == int(EffectId.SEND_CHAT)
            and (getattr(eff, "message", "") or "").startswith("<AQUA>[DBG #")
        )
        assert dbg_count == 1, (
            f"Trigger #{trig_id} '{trig.name}' zawiera {dbg_count} efektow [DBG #] zamiast dokladnie 1!"
        )


def test_validator_catches_synthetic_ctd_cases(monkeypatch: pytest.MonkeyPatch) -> None:
    """Self-test ensuring every check_* function reliably catches synthetic Runtime CTD bugs."""

    def make_mock_scen(
        triggers: list[Any],
        units_by_p: dict[int, list[Any]] | None = None,
        map_size: int = 240,
    ) -> Any:
        ubp = units_by_p or {}
        return types.SimpleNamespace(
            map_manager=types.SimpleNamespace(map_size=map_size),
            unit_manager=types.SimpleNamespace(
                get_player_units=lambda p: ubp.get(int(p), []),
            ),
            trigger_manager=types.SimpleNamespace(triggers=triggers),
        )

    # 1. Missing armour_attack_class & class 0 misuse
    bad_attr_eff_1 = types.SimpleNamespace(
        effect_type=int(EffectId.MODIFY_ATTRIBUTE),
        object_attributes=9,
        object_list_unit_id=426,
        armour_attack_class=-1,
        armour_attack_quantity=65535,
        quantity=-1,
    )
    bad_attr_eff_2 = types.SimpleNamespace(
        effect_type=int(EffectId.MODIFY_ATTRIBUTE),
        object_attributes=8,
        object_list_unit_id=426,
        armour_attack_class=0,
        armour_attack_quantity=5,
        quantity=5,
    )
    trig_attr = types.SimpleNamespace(
        trigger_id=0,
        name="BadModifyAttr",
        looping=0,
        enabled=1,
        conditions=[],
        effects=[bad_attr_eff_1, bad_attr_eff_2],
        effect_order=[0, 1],
    )
    assert len(check_modify_attribute_classes(make_mock_scen([trig_attr]))) == 3

    # 2. Looping without timer & timerless cycle
    trig_loop = types.SimpleNamespace(
        trigger_id=0,
        name="NoTimerLoop",
        looping=1,
        enabled=1,
        conditions=[],
        effects=[],
        effect_order=[],
    )
    assert len(check_trigger_loops_have_timer(make_mock_scen([trig_loop]))) == 1

    # 3. Inverted area & 4. Out-of-bounds coordinates
    bad_cond = types.SimpleNamespace(
        condition_type=int(ConditionId.OBJECTS_IN_AREA),
        area_x1=120,
        area_y1=80,
        area_x2=100,
        area_y2=250,
    )
    bad_loc_eff = types.SimpleNamespace(
        effect_type=int(EffectId.CREATE_OBJECT),
        area_x1=-1,
        area_y1=-1,
        area_x2=-1,
        area_y2=-1,
        location_x=240,
        location_y=50,
        location_object_reference=-1,
    )
    trig_geo = types.SimpleNamespace(
        trigger_id=0,
        name="BadGeo",
        looping=0,
        enabled=1,
        conditions=[bad_cond],
        effects=[bad_loc_eff],
        effect_order=[0],
    )
    scen_geo = make_mock_scen([trig_geo], map_size=240)
    assert len(check_inverted_or_partial_areas(scen_geo)) == 1
    assert len(check_coordinates_within_map_bounds(scen_geo)) == 2

    # 5. Intra-trigger Use-After-Remove & dangling ref_id
    u_existing = types.SimpleNamespace(reference_id=10, unit_const=82, x=50.0, y=50.0)
    eff_rem = types.SimpleNamespace(
        effect_type=int(EffectId.REMOVE_OBJECT),
        selected_object_ids=[10],
        location_object_reference=-1,
    )
    eff_task = types.SimpleNamespace(
        effect_type=int(EffectId.TASK_OBJECT),
        selected_object_ids=[10, 999],
        location_object_reference=-1,
    )
    trig_uar = types.SimpleNamespace(
        trigger_id=0,
        name="BadUAR",
        looping=0,
        enabled=1,
        conditions=[],
        effects=[eff_rem, eff_task],
        effect_order=[0, 1],
    )
    scen_uar = make_mock_scen([trig_uar], units_by_p={1: [u_existing]})
    uar_errs = check_operations_on_removed_objects(scen_uar)
    assert any("999" in e for e in uar_errs)
    assert any("juz usunietym" in e for e in uar_errs)

    # 6. Dead unit, projectile, and unknown/unexposed IDs (e.g., 817)
    u_corpse = types.SimpleNamespace(reference_id=1, unit_const=693, x=20.0, y=20.0)
    u_unknown = types.SimpleNamespace(reference_id=2, unit_const=817, x=25.0, y=25.0)
    eff_proj = types.SimpleNamespace(
        effect_type=int(EffectId.CREATE_OBJECT),
        object_list_unit_id=469,
    )
    trig_dead = types.SimpleNamespace(
        trigger_id=0,
        name="BadDeadProj",
        looping=0,
        enabled=1,
        conditions=[],
        effects=[eff_proj],
        effect_order=[0],
    )
    scen_dead = make_mock_scen([trig_dead], units_by_p={1: [u_corpse, u_unknown]})
    dead_errs = check_dead_or_projectile_unit_operations(scen_dead)
    assert len(dead_errs) == 3

    # 6B. Zero-truncated HIT_POINTS MULTIPLY, unlocked PromiDE AI, conditionless UI & unfiltered DAMAGE_OBJECT
    zero_hp_eff = types.SimpleNamespace(
        effect_type=int(EffectId.MODIFY_ATTRIBUTE),
        object_attributes=0,
        operation=4,
        object_list_unit_id=1125,
        quantity=0,
    )
    unfiltered_dmg_eff = types.SimpleNamespace(
        effect_type=int(EffectId.DAMAGE_OBJECT),
        selected_object_ids=[],
        object_type=-1,
        object_list_unit_id=-1,
    )
    trig_ui_dmg = types.SimpleNamespace(
        trigger_id=0,
        name="UI_Bad_And_UnfilteredDmg",
        display_on_screen=1,
        looping=0,
        enabled=1,
        conditions=[],
        effects=[zero_hp_eff, unfiltered_dmg_eff],
        effect_order=[0, 1],
    )
    scen_ui_dmg = make_mock_scen([trig_ui_dmg])
    scen_ui_dmg.player_manager = types.SimpleNamespace(
        players=[None, types.SimpleNamespace(ai_type=int(AiType.STANDARD), lock_personality=False, ai_script="")]
    )
    assert len(check_modify_attribute_classes(scen_ui_dmg)) == 1
    assert len(check_ai_players_locked_immobile(scen_ui_dmg)) == 1
    assert len(check_ui_and_area_damage_safety(scen_ui_dmg)) == 2

    # 7. Pre-write guard in generate_gondolin_scenario rejects *_ID pointing to dead_unit or ProjectileInfo
    _ensure_local_import_path()
    import generate_gondolin_scenario
    import gondolin_config

    generate_gondolin_scenario.assert_no_dead_or_projectile_ids_before_write()
    monkeypatch.setattr(gondolin_config, "SYNTHETIC_CORPSE_TEST_ID", 693, raising=False)
    with pytest.raises(RuntimeError, match="SYNTHETIC_CORPSE_TEST_ID=693"):
        generate_gondolin_scenario.assert_no_dead_or_projectile_ids_before_write()


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))

