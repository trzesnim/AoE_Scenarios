"""Behavioral and discrete-time simulation test suite for Stage A (Audit Items 15, 16, 17, 18, 19)."""

from __future__ import annotations

import importlib
import shutil
import types
from typing import Any

import reproduce_audit_metrics

reproduce_audit_metrics._ensure_aoe2_parser_or_mock()

import gondolin_config
import gondolin_map
import gondolin_mechanics
import gondolin_quests

importlib.reload(gondolin_config)
importlib.reload(gondolin_mechanics)
importlib.reload(gondolin_quests)

from gondolin_config import (
    PlayerId,
    HERO_ECTHELION_ID,
    HERO_GLORFINDEL_ID,
    HERO_IDRIL_ID,
    HERO_ROG_ID,
    HERO_TUOR_ID,
    HUMAN_PLAYERS,
    MAP_REVEALER_ID,
    OBJECT_TYPE_MILITARY,
    PLAYER_ALL_COMBAT_UNITS,
    TORCH_ID,
    TRACKED_NOLDOR_HEROES,
    UNIT_ARCH_LONGBOW_ID,
    UNIT_FLOWER_BLADE_ID,
    UNIT_FOUNTAIN_GUARD_ID,
    UNIT_HAMMER_SMITH_ID,
    UNIT_HARP_HEALER_ID,
    UNIT_IDRIL_SAPPER_ID,
    UNIT_REFUGEE_CART_ID,
    UNIT_TREE_PIKE_ID,
    UNIT_WING_CHAMPION_ID,
    UNIT_WING_GUARD_ID,
)
from gondolin_quests import PHASE_MARKER_COORDS, PHASE_RALLY_AURA_BOXES

MILITARY_UNIT_IDS: set[int] = set(PLAYER_ALL_COMBAT_UNITS) | {
    UNIT_HARP_HEALER_ID,
    UNIT_IDRIL_SAPPER_ID,
}


class CondRec:
    def __init__(self, c_type: str, **kwargs: Any) -> None:
        self.condition_type = c_type
        self.kwargs = kwargs


class EffRec:
    def __init__(self, e_type: str, **kwargs: Any) -> None:
        self.effect_type = e_type
        self.kwargs = kwargs


class CondAPI:
    def __init__(self, trig: Any) -> None:
        self._t = trig

    def timer(self, timer: int = 0) -> None:
        self._t.conditions.append(CondRec("timer", timer=timer))

    def objects_in_area(
        self,
        source_player: PlayerId = PlayerId.ONE,
        object_list: int = -1,
        object_type: int = -1,
        area_x1: int = 0,
        area_y1: int = 0,
        area_x2: int = 0,
        area_y2: int = 0,
        quantity: int = 1,
        inverted: int = 0,
    ) -> None:
        self._t.conditions.append(
            CondRec(
                "objects_in_area",
                source_player=source_player,
                object_list=object_list,
                object_type=object_type,
                area_x1=area_x1,
                area_y1=area_y1,
                area_x2=area_x2,
                area_y2=area_y2,
                quantity=quantity,
                inverted=inverted,
            )
        )

    def own_fewer_objects(
        self,
        source_player: PlayerId = PlayerId.ONE,
        object_list: int = -1,
        object_type: int = -1,
        quantity: int = 0,
    ) -> None:
        self._t.conditions.append(
            CondRec(
                "own_fewer_objects",
                source_player=source_player,
                object_list=object_list,
                object_type=object_type,
                quantity=quantity,
            )
        )

    def own_objects(
        self,
        source_player: PlayerId = PlayerId.ONE,
        object_list: int = -1,
        object_type: int = -1,
        quantity: int = 1,
    ) -> None:
        self._t.conditions.append(
            CondRec(
                "own_objects",
                source_player=source_player,
                object_list=object_list,
                object_type=object_type,
                quantity=quantity,
            )
        )

    def destroy_object(self, unit_object: int = -1) -> None:
        self._t.conditions.append(CondRec("destroy_object", unit_object=unit_object))


class EffAPI:
    def __init__(self, trig: Any) -> None:
        self._t = trig

    def send_chat(self, source_player: PlayerId = PlayerId.ONE, message: str = "") -> None:
        self._t.effects.append(EffRec("send_chat", source_player=source_player, message=message))

    def create_object(
        self,
        source_player: PlayerId = PlayerId.ONE,
        object_list_unit_id: int = -1,
        location_x: int = 0,
        location_y: int = 0,
    ) -> None:
        self._t.effects.append(
            EffRec(
                "create_object",
                source_player=source_player,
                object_list_unit_id=object_list_unit_id,
                location_x=location_x,
                location_y=location_y,
            )
        )

    def remove_object(
        self,
        source_player: PlayerId = PlayerId.ONE,
        object_list_unit_id: int = -1,
        selected_object_ids: list[int] | None = None,
        area_x1: int = 0,
        area_y1: int = 0,
        area_x2: int = 0,
        area_y2: int = 0,
    ) -> None:
        self._t.effects.append(
            EffRec(
                "remove_object",
                source_player=source_player,
                object_list_unit_id=object_list_unit_id,
                area_x1=area_x1,
                area_y1=area_y1,
                area_x2=area_x2,
                area_y2=area_y2,
            )
        )

    def kill_object(
        self,
        source_player: PlayerId = PlayerId.ONE,
        selected_object_ids: list[int] | None = None,
        area_x1: int = 0,
        area_y1: int = 0,
        area_x2: int = 0,
        area_y2: int = 0,
    ) -> None:
        self._t.effects.append(EffRec("kill_object", source_player=source_player))

    def damage_object(
        self,
        source_player: PlayerId = PlayerId.ONE,
        area_x1: int = 0,
        area_y1: int = 0,
        area_x2: int = 0,
        area_y2: int = 0,
        quantity: int = 0,
    ) -> None:
        self._t.effects.append(EffRec("damage_object", source_player=source_player, quantity=quantity))

    def heal_object(
        self,
        source_player: PlayerId = PlayerId.ONE,
        object_type: int = -1,
        area_x1: int = 0,
        area_y1: int = 0,
        area_x2: int = 0,
        area_y2: int = 0,
        quantity: int = 0,
    ) -> None:
        self._t.effects.append(
            EffRec(
                "heal_object",
                source_player=source_player,
                object_type=object_type,
                area_x1=area_x1,
                area_y1=area_y1,
                area_x2=area_x2,
                area_y2=area_y2,
                quantity=quantity,
            )
        )

    def modify_resource(
        self,
        source_player: PlayerId = PlayerId.ONE,
        tribute_list: int = 0,
        quantity: int = 0,
        operation: int = 1,
    ) -> None:
        self._t.effects.append(
            EffRec("modify_resource", source_player=source_player, tribute_list=tribute_list, quantity=quantity, operation=operation)
        )

    def modify_attribute(
        self,
        source_player: PlayerId = PlayerId.ONE,
        object_list_unit_id: int = -1,
        object_attributes: int = 0,
        operation: int = 1,
        quantity: float = 0,
        armour_attack_class: int = -1,
        armour_attack_quantity: int = 0,
    ) -> None:
        self._t.effects.append(
            EffRec("modify_attribute", source_player=source_player, object_list_unit_id=object_list_unit_id, object_attributes=object_attributes, operation=operation, quantity=quantity)
        )

    def attack_move(
        self,
        source_player: PlayerId = PlayerId.ONE,
        object_list_unit_id: int = -1,
        area_x1: int = 0,
        area_y1: int = 0,
        area_x2: int = 0,
        area_y2: int = 0,
        location_x: int = 0,
        location_y: int = 0,
    ) -> None:
        self._t.effects.append(EffRec("attack_move", source_player=source_player))

    def activate_trigger(self, trigger_id: int = -1) -> None:
        self._t.effects.append(EffRec("activate_trigger", trigger_id=trigger_id))

    def deactivate_trigger(self, trigger_id: int = -1) -> None:
        self._t.effects.append(EffRec("deactivate_trigger", trigger_id=trigger_id))

    def research_technology(self, source_player: PlayerId = PlayerId.ONE, technology: int = 0) -> None:
        self._t.effects.append(EffRec("research_technology", source_player=source_player))

    def change_object_name(
        self,
        source_player: PlayerId = PlayerId.ONE,
        object_list_unit_id: int = -1,
        selected_object_ids: list[int] | None = None,
        message: str = "",
    ) -> None:
        self._t.effects.append(EffRec("change_object_name", source_player=source_player, object_list_unit_id=object_list_unit_id, message=message))

    def declare_victory(self, source_player: PlayerId = PlayerId.ONE, enabled: bool = True) -> None:
        self._t.effects.append(EffRec("declare_victory", source_player=source_player, enabled=enabled))


class TrigObj:
    def __init__(self, trig_id: int, name: str, enabled: bool = True, looping: bool = False) -> None:
        self.trigger_id = trig_id
        self.name = name
        self.enabled = enabled
        self.looping = looping
        self.short_description = ""
        self.display_on_screen = 0
        self.description_order = 0
        self.conditions: list[CondRec] = []
        self.effects: list[EffRec] = []
        self.new_condition = CondAPI(self)
        self.new_effect = EffAPI(self)


class TMObj:
    def __init__(self) -> None:
        self.triggers: list[TrigObj] = []

    def add_trigger(self, name: str, enabled: bool = True, looping: bool = False) -> TrigObj:
        t = TrigObj(len(self.triggers), name, enabled=enabled, looping=looping)
        self.triggers.append(t)
        return t


class TriggerSimulator:
    """Discrete-time Genie Engine trigger simulator for behavioral testing of Seals, Auras, and Duels."""

    def __init__(self, triggers: list[TrigObj], initial_units: list[tuple[PlayerId, int, int, int]]) -> None:
        self.triggers = triggers
        self.enabled: dict[int, bool] = {t.trigger_id: t.enabled for t in triggers}
        self.timer_elapsed: dict[int, float] = {t.trigger_id: 0.0 for t in triggers}
        self.units: list[dict[str, Any]] = [
            {"player": p, "unit_id": u, "x": x, "y": y} for p, u, x, y in initial_units
        ]
        self.spawned_log: list[tuple[float, str, PlayerId, int, int, int]] = []
        self.fired_log: list[tuple[float, str]] = []
        self.defeated_players: set[PlayerId] = set()
        self.glory_gold: int = 0
        self.time: float = 0.0

    def _is_military(self, unit_id: int) -> bool:
        return unit_id in MILITARY_UNIT_IDS or unit_id >= 1100 or unit_id in (4, 24, 89, 473, 532, 542, 548, 640, 756, 878, 188)

    def _eval_cond(self, trig_id: int, cond: CondRec) -> bool:
        kw = cond.kwargs
        if cond.condition_type == "timer":
            return self.timer_elapsed[trig_id] + 1e-9 >= float(kw["timer"])
        if cond.condition_type == "destroy_object":
            return False

        p = kw["source_player"]
        u_list = kw.get("object_list", -1)
        u_type = kw.get("object_type", -1)

        def matches_unit(u: dict[str, Any]) -> bool:
            if u["player"] != p:
                return False
            if u_list != -1:
                return u["unit_id"] == u_list
            if u_type == OBJECT_TYPE_MILITARY:
                return self._is_military(u["unit_id"])
            return True

        if cond.condition_type == "own_fewer_objects":
            cnt = sum(1 for u in self.units if matches_unit(u))
            return cnt <= kw["quantity"]

        if cond.condition_type == "own_objects":
            cnt = sum(1 for u in self.units if matches_unit(u))
            return cnt >= kw["quantity"]

        if cond.condition_type == "objects_in_area":
            x1, y1, x2, y2 = kw["area_x1"], kw["area_y1"], kw["area_x2"], kw["area_y2"]
            cnt = sum(
                1
                for u in self.units
                if matches_unit(u) and x1 <= u["x"] <= x2 and y1 <= u["y"] <= y2
            )
            ok = cnt >= kw["quantity"]
            return (not ok) if kw.get("inverted", 0) == 1 else ok

        return False

    def step(self, dt: float = 0.5) -> None:
        """Advance simulation by dt seconds and evaluate all enabled triggers in ID order."""
        self.time = round(self.time + dt, 4)
        for tid, is_en in list(self.enabled.items()):
            if is_en:
                self.timer_elapsed[tid] += dt

        for trig in self.triggers:
            tid = trig.trigger_id
            if not self.enabled[tid] or not trig.conditions:
                continue
            if all(self._eval_cond(tid, c) for c in trig.conditions):
                self.fired_log.append((self.time, trig.name))
                if not trig.looping:
                    self.enabled[tid] = False
                self.timer_elapsed[tid] = 0.0

                for eff in trig.effects:
                    ekw = eff.kwargs
                    if eff.effect_type == "activate_trigger":
                        target_id = ekw["trigger_id"]
                        if target_id in self.enabled:
                            if not self.enabled[target_id]:
                                self.timer_elapsed[target_id] = 0.0
                            self.enabled[target_id] = True
                    elif eff.effect_type == "deactivate_trigger":
                        target_id = ekw["trigger_id"]
                        if target_id in self.enabled:
                            self.enabled[target_id] = False
                            self.timer_elapsed[target_id] = 0.0
                    elif eff.effect_type == "create_object":
                        self.units.append(
                            {
                                "player": ekw["source_player"],
                                "unit_id": ekw["object_list_unit_id"],
                                "x": ekw["location_x"],
                                "y": ekw["location_y"],
                            }
                        )
                        self.spawned_log.append(
                            (
                                self.time,
                                trig.name,
                                ekw["source_player"],
                                ekw["object_list_unit_id"],
                                ekw["location_x"],
                                ekw["location_y"],
                            )
                        )
                    elif eff.effect_type == "remove_object":
                        rp = ekw["source_player"]
                        ru = ekw.get("object_list_unit_id", -1)
                        ax1, ay1, ax2, ay2 = ekw["area_x1"], ekw["area_y1"], ekw["area_x2"], ekw["area_y2"]
                        self.units = [
                            u
                            for u in self.units
                            if not (
                                u["player"] == rp
                                and (ru == -1 or u["unit_id"] == ru)
                                and ax1 <= u["x"] <= ax2
                                and ay1 <= u["y"] <= ay2
                            )
                        ]
                    elif eff.effect_type == "modify_resource":
                        if ekw["source_player"] == PlayerId.ONE and ekw["tribute_list"] == 3:
                            if int(ekw["operation"]) == 1:
                                self.glory_gold += ekw["quantity"]
                            elif int(ekw["operation"]) == 3:
                                self.glory_gold -= ekw["quantity"]
                    elif eff.effect_type == "declare_victory":
                        if not ekw.get("enabled", True):
                            self.defeated_players.add(ekw["source_player"])


def build_full_scenario_triggers() -> tuple[list[TrigObj], dict[str, Any]]:
    placed_units: list[Any] = []

    def record_unit(player: PlayerId, unit_const: int, x: float, y: float) -> Any:
        u = types.SimpleNamespace(
            reference_id=len(placed_units) + 1,
            player=player,
            unit_const=unit_const,
            x=x,
            y=y,
        )
        placed_units.append(u)
        return u

    scen = types.SimpleNamespace(
        map_manager=types.SimpleNamespace(
            map_size=240,
            get_tile=lambda x, y: types.SimpleNamespace(terrain_id=0, elevation=0),
        ),
        unit_manager=types.SimpleNamespace(units=placed_units, add_unit=record_unit),
        player_manager=types.SimpleNamespace(
            active_players=8,
            players=[None] + [types.SimpleNamespace(diplomacy=[0] * 9) for _ in range(8)],
        ),
        trigger_manager=TMObj(),
    )
    ctx = gondolin_map.build_map_and_entities(scen)
    gondolin_mechanics.setup_init_auras_and_mechanics(scen, ctx)
    gondolin_quests.setup_sanctuary_quests_and_victory(scen, ctx)
    return scen.trigger_manager.triggers, ctx


def run_stage_a_verification() -> None:
    """Execute all structural AND discrete-time behavioral tests for Stage A (Audit Items 15-19)."""
    trigs, ctx = build_full_scenario_triggers()
    by_name = {t.name: t for t in trigs}

    print("=" * 80)
    print(f"RAPORT TESTOW LOGICZNYCH I SYMULACYJNYCH ETAPU A (Triggery: {len(trigs)})")
    print("=" * 80)

    # =========================================================================
    # ITEM 15A: SOFT-CAP MIXED-ARMY & BOUNDARY TESTS (0, 14, 15, 28, 29, 45)
    # =========================================================================
    for phase_label in ("Faza_II", "Faza_III"):
        for p_id in HUMAN_PLAYERS:
            p_trigs = [
                by_name[f"SoftCap_{phase_label}_P{p_id.value}_Critical"],
                by_name[f"SoftCap_{phase_label}_P{p_id.value}_Standard"],
                by_name[f"SoftCap_{phase_label}_P{p_id.value}_Dominance"],
            ]
            for count, expected_suffix in [
                (0, "Critical"),
                (14, "Critical"),
                (15, "Standard"),
                (28, "Standard"),
                (29, "Dominance"),
                (45, "Dominance"),
            ]:
                # Construct a mixed army of 4 different military unit types + 25 non-military buildings/carts/revealers
                mixed_units: list[tuple[PlayerId, int, int, int]] = []
                mil_cycle = [
                    HERO_TUOR_ID,
                    UNIT_HAMMER_SMITH_ID,
                    UNIT_WING_GUARD_ID,
                    UNIT_ARCH_LONGBOW_ID,
                    UNIT_FLOWER_BLADE_ID,
                    UNIT_TREE_PIKE_ID,
                ]
                for i in range(count):
                    mixed_units.append((p_id, mil_cycle[i % len(mil_cycle)], 50, 50))
                # Add non-military buildings (ID 70, 82), carts (128), and revealers (837) that must be ignored
                for non_mil in (70, 82, UNIT_REFUGEE_CART_ID, MAP_REVEALER_ID):
                    for _ in range(5):
                        mixed_units.append((p_id, non_mil, 40, 40))

                sim = TriggerSimulator(p_trigs, mixed_units)
                for t in p_trigs:
                    sim.enabled[t.trigger_id] = True
                    for c in t.conditions:
                        assert c.kwargs["object_type"] == OBJECT_TYPE_MILITARY
                        assert c.kwargs["object_list"] == -1
                sim.step(0.5)
                fired = [name.split("_")[-1] for _, name in sim.fired_log]
                assert fired == [expected_suffix], (
                    f"{phase_label} P{p_id.value} mixed army={count}: expected [{expected_suffix}], got {fired}"
                )
    print("[PASS 15A] Soft-Cap (0, 14 -> Critical | 15, 28 -> Standard | 29, 45 -> Dominance) na armiach mieszanych + ignorowanie budynkow/wozow/Revealerow dla P1-P4.")

    # =========================================================================
    # ITEM 15B & 19: ALL 8 ESCALATING ENCOUNTERS + ROG + WANDERING ELITE TEST
    # =========================================================================
    encounter_names = [
        "Aqueduct_Guard",
        "West_Forges",
        "East_Market",
        "Tumladen_Wolves_1",
        "Balrog_Altar_Tumladen",
        "Orfalch_orfalch_gate_3",
        "Orfalch_orfalch_gate_5",
        "Orfalch_orfalch_gate_7",
    ]
    elite_signatures: set[tuple[PlayerId, int]] = set()
    for enc in encounter_names:
        t_base = by_name[f"Enc_{enc}_Base"]
        t_elite = by_name[f"Enc_{enc}_EliteAmbush"]
        t_leash = by_name[f"Enc_{enc}_EliteLeash"]
        t_rew = by_name[f"Enc_{enc}_EliteDefeatedReward"]

        if enc in ("West_Forges", "Balrog_Altar_Tumladen"):
            assert t_base.conditions[0].kwargs["object_list"] == HERO_ROG_ID
            assert t_base.conditions[0].kwargs["quantity"] == 1
        else:
            assert t_base.conditions[0].kwargs["object_type"] == OBJECT_TYPE_MILITARY
            assert t_base.conditions[0].kwargs["quantity"] == 1

        # t_elite must check >= 8 military units (never 5 Rogs!)
        assert t_elite.conditions[1].kwargs["object_type"] == OBJECT_TYPE_MILITARY
        assert t_elite.conditions[1].kwargs["object_list"] == -1
        assert t_elite.conditions[1].kwargs["quantity"] == 8

        # t_rew must check >= 1 military unit holding sector + own_fewer_objects(qty=0) for elite unit
        assert t_rew.conditions[1].kwargs["object_type"] == OBJECT_TYPE_MILITARY
        assert t_rew.conditions[1].kwargs["object_list"] == -1
        assert t_rew.conditions[1].kwargs["quantity"] == 1
        own_fewer_conds = [c for c in t_rew.conditions if c.condition_type == "own_fewer_objects"]
        assert len(own_fewer_conds) >= 1
        for oc in own_fewer_conds:
            sig = (oc.kwargs["source_player"], oc.kwargs["object_list"])
            assert oc.kwargs["quantity"] == 0
            assert sig not in elite_signatures, f"Duplicate elite ambush signature {sig} in {enc}"
            elite_signatures.add(sig)
        assert len(t_leash.effects) >= 1

        # Behavioral Simulation for Item 19: Elite unit leaves combat box and stays alive at (5, 5)
        el_p, el_u = own_fewer_conds[0].kwargs["source_player"], own_fewer_conds[0].kwargs["object_list"]
        trig_p = t_rew.conditions[1].kwargs["source_player"]
        cx = (t_rew.conditions[1].kwargs["area_x1"] + t_rew.conditions[1].kwargs["area_x2"]) // 2
        cy = (t_rew.conditions[1].kwargs["area_y1"] + t_rew.conditions[1].kwargs["area_y2"]) // 2

        sim_enc = TriggerSimulator(
            [t_rew, t_leash],
            [
                (trig_p, UNIT_HAMMER_SMITH_ID, cx, cy),  # Player holds the combat sector
                (el_p, el_u, 5, 5),                      # Elite enemy wandered far outside the sector (alive!)
            ],
        )
        sim_enc.enabled[t_rew.trigger_id] = True
        sim_enc.enabled[t_leash.trigger_id] = True
        for _ in range(40):  # 20 seconds elapsed (> 15s timer)
            sim_enc.step(0.5)
        assert sim_enc.glory_gold == 0, f"{enc} granted reward while elite unit was still alive outside sector!"

        # Now kill the wandered elite unit -> reward must fire and deactivate leash!
        sim_enc.units = [u for u in sim_enc.units if not (u["player"] == el_p and u["unit_id"] == el_u)]
        sim_enc.step(0.5)
        assert sim_enc.glory_gold == 200, f"{enc} failed to grant +200 Glory after elite unit died!"
        assert not sim_enc.enabled[t_leash.trigger_id]

    print("[PASS 15B & 19] Wszystkie 8 spotkan (w tym Rog w West_Forges i Balrog_Altar) + blokada nagrody, gdy elitarny wrog wyjdzie poza sektor i zyje.")

    # =========================================================================
    # ITEM 16: GRACECORESPAWN 6 BOUNDARY TIMING TESTS + GUARD ESCORT RULE
    # =========================================================================
    seal_trigs = [t for t in trigs if t.name.startswith('Seal_') or t.name.startswith('UI_Seals_')]
    def make_all_9_heroes() -> list[tuple[PlayerId, int, int, int]]:
        px, py = PHASE_MARKER_COORDS["phase1"]
        units = [(PlayerId.ONE, TORCH_ID, px, py)]
        for p_id, h_id, _, _ in TRACKED_NOLDOR_HEROES:
            units.append((p_id, h_id, 50, 50))
        return units

    def kill_hero(sim: TriggerSimulator, h_id: int) -> None:
        sim.units = [u for u in sim.units if u["unit_id"] != h_id]

    # Case 16.1: Simultaneous death (dt = 0.0s) of Tuor and Idril -> 1 Seal (-500), Tuor gets 6 guards, Idril gets 0 guards
    sim1 = TriggerSimulator(seal_trigs, make_all_9_heroes())
    for _ in range(12):  # Advance to t = 6.0s (Seals armed at 5.0s)
        sim1.step(0.5)
    kill_hero(sim1, HERO_TUOR_ID)
    kill_hero(sim1, HERO_IDRIL_ID)
    sim1.step(0.5)  # t = 6.5s: Tuor triggers Stage 1 HeroLoss (-500, +6 guards) and arms GraceCoRespawn
    sim1.step(0.5)  # t = 7.0s: Idril revives via GraceCoRespawn (0 extra guards, 0 extra Seal cost)
    assert sim1.glory_gold == -500
    assert any(u["unit_id"] == HERO_TUOR_ID for u in sim1.units)
    assert any(u["unit_id"] == HERO_IDRIL_ID for u in sim1.units)
    assert sum(1 for u in sim1.units if u["unit_id"] == UNIT_HAMMER_SMITH_ID) == 6
    assert sum(1 for u in sim1.units if u["unit_id"] == UNIT_TREE_PIKE_ID) == 0

    # Case 16.2: Second hero dies after 1.5s (inside 3s window) -> 1 Seal (-500), 0 extra guards
    sim2 = TriggerSimulator(seal_trigs, make_all_9_heroes())
    for _ in range(12):
        sim2.step(0.5)
    kill_hero(sim2, HERO_TUOR_ID)
    sim2.step(0.5)  # t = 6.5s (Seal #1 consumed, relay timer = 0.0s)
    sim2.step(0.5)  # relay timer = 0.5s
    sim2.step(0.5)  # relay timer = 1.0s
    kill_hero(sim2, HERO_ECTHELION_ID)
    sim2.step(0.5)  # relay timer = 1.5s -> GraceCoRespawn revives Ecthelion!
    assert sim2.glory_gold == -500
    assert any(u["unit_id"] == HERO_ECTHELION_ID for u in sim2.units)
    assert sum(1 for u in sim2.units if u["unit_id"] == UNIT_FOUNTAIN_GUARD_ID) == 0

    # Case 16.3: Second hero dies just before end of window (at 2.5s elapsed on relay) -> 1 Seal (-500)
    sim3 = TriggerSimulator(seal_trigs, make_all_9_heroes())
    for _ in range(12):
        sim3.step(0.5)
    kill_hero(sim3, HERO_TUOR_ID)
    for _ in range(5):  # 2.5s elapsed since Tuor's death
        sim3.step(0.5)
    kill_hero(sim3, HERO_ROG_ID)
    sim3.step(0.5)  # At 2.5s -> 3.0s tick: GraceCoRespawn evaluates BEFORE relay (lower trigger_id) and revives Rog!
    assert sim3.glory_gold == -500
    assert any(u["unit_id"] == HERO_ROG_ID for u in sim3.units)

    # Case 16.4: Second hero dies right on the 3.0s boundary (after relay has armed Stage 2) -> 2 Seals (-1000) & +6 guards
    sim4 = TriggerSimulator(seal_trigs, make_all_9_heroes())
    for _ in range(12):
        sim4.step(0.5)
    kill_hero(sim4, HERO_TUOR_ID)
    for _ in range(7):  # 0.5s fire + 3.0s relay = window closed, Stage 2 now armed
        sim4.step(0.5)
    kill_hero(sim4, HERO_ECTHELION_ID)
    sim4.step(0.5)
    assert sim4.glory_gold == -1000
    assert sum(1 for u in sim4.units if u["unit_id"] == UNIT_FOUNTAIN_GUARD_ID) == 6

    # Case 16.5 & 16.6: Subsequent deaths after window (Stage 2 -> Stage 3 -> Stage 4 Defeat)
    for _ in range(8):  # Wait 4.0s (> 3s window) so Stage 3 arms
        sim4.step(0.5)
    kill_hero(sim4, HERO_GLORFINDEL_ID)
    sim4.step(0.5)  # Consumes Seal #3 (-1500)
    assert sim4.glory_gold == -1500
    assert not sim4.defeated_players
    for _ in range(8):  # Wait 4.0s (> 3s window) so Stage 4 arms
        sim4.step(0.5)
    kill_hero(sim4, HERO_IDRIL_ID)
    sim4.step(0.5)  # Stage 4 -> Defeat!
    assert sim4.defeated_players == set(HUMAN_PLAYERS)
    print("[PASS 16] Symulacja czasowa GraceCoRespawn (0s, 1.5s, 2.5s, granica 3.0s, >3s, Stage 4 Defeat + brak dodatkowej eskorty w oknie) zweryfikowana.")

    # =========================================================================
    # ITEM 17: NON-OVERLAPPING 20-SECOND HEALING LOOPS TEST (DEATHS 5s APART)
    # =========================================================================
    sim_heal = TriggerSimulator(seal_trigs, make_all_9_heroes())
    heal_loop_ids = [t.trigger_id for t in trigs if "LocalRallyHealLoop" in t.name]
    for _ in range(12):  # t = 6.0s
        sim_heal.step(0.5)
    kill_hero(sim_heal, HERO_TUOR_ID)
    sim_heal.step(0.5)  # t = 6.5s: Stage 1 heal loop starts
    assert sum(1 for tid in heal_loop_ids if sim_heal.enabled[tid]) == 1
    for _ in range(9):  # Advance 4.5s (t = 11.0s, Stage 2 is armed, Stage 1 heal loop still at 4.5s / 20s)
        sim_heal.step(0.5)
        assert sum(1 for tid in heal_loop_ids if sim_heal.enabled[tid]) == 1
    # Second hero dies 5 seconds after first hero (at t = 11.5s) -> Stage 2 fires!
    kill_hero(sim_heal, HERO_ECTHELION_ID)
    sim_heal.step(0.5)
    active_loops = [by_name[t.name].name for t in trigs if t.trigger_id in heal_loop_ids and sim_heal.enabled[t.trigger_id]]
    assert active_loops == ["Seal_Stage2_phase1_LocalRallyHealLoop"], f"Overlapping heal loops: {active_loops}"
    print("[PASS 17] Brak nakladania sie 20-sekundowych aur leczniczych przy zgonach w odstepie 5s (zawsze maks. 1 aktywna petla).")

    # =========================================================================
    # ITEM 18: CONTINUOUS 25s GLORFINDEL DUEL SPUR HOLD (LEAVE & RE-ENTER RESET)
    # =========================================================================
    duel_trigs = [
        by_name["P3_Finale_Cirith_Thoronath_Ambush"],
        by_name["P3_Finale_Glorfindel_Engages_Balrog"],
        by_name["P3_Finale_Thorondor_Hold25s"],
        by_name["P3_Finale_Glorfindel_LeftSpur"],
        by_name["P3_Finale_Glorfindel_ReenterSpur"],
        by_name["P3_Finale_Thorondor_HeroicSacrifice"],
        by_name["P3_Finale_Thorondor_Eagles_Arrive"],
    ]
    sim_duel = TriggerSimulator(duel_trigs, [(PlayerId.THREE, HERO_GLORFINDEL_ID, 198, 198)])
    sim_duel.step(0.5)  # Ambush fires, arms Engages_Balrog
    sim_duel.step(0.5)  # Engages_Balrog fires, arms Hold25s & LeftSpur
    for _ in range(20):  # Hold for 10s (less than 25s)
        sim_duel.step(0.5)
    # Glorfindel retreats off the Spur to (185, 180) while alive!
    sim_duel.units[0]["x"], sim_duel.units[0]["y"] = 185, 180
    for _ in range(40):  # Wait 20s outside the Spur (total 30s > 25s) -> Eagles must NOT arrive!
        sim_duel.step(0.5)
    assert not any(name == "P3_Finale_Thorondor_Eagles_Arrive" for _, name in sim_duel.fired_log)

    # Glorfindel returns to the Spur at (198, 198) and holds for 24s (not enough yet) then 25s (fires!)
    sim_duel.units[0]["x"], sim_duel.units[0]["y"] = 198, 198
    sim_duel.step(0.5)  # ReenterSpur fires and re-arms Hold25s from 0.0s
    for _ in range(48):  # 24.0s elapsed
        sim_duel.step(0.5)
    assert not any(name == "P3_Finale_Thorondor_Eagles_Arrive" for _, name in sim_duel.fired_log)
    sim_duel.step(0.5)  # 24.5s
    sim_duel.step(0.5)  # 25.0s continuous hold -> Hold25s fires!
    sim_duel.step(1.0)  # 1.0s relay -> P3_Finale_Thorondor_Eagles_Arrive fires!
    assert any(name == "P3_Finale_Thorondor_Eagles_Arrive" for _, name in sim_duel.fired_log)
    # Path B test: Glorfindel engages Balrog on Spur and falls in combat at t=8s -> HeroicSacrifice triggers Eagles without consuming a Seal!
    sim_sac = TriggerSimulator(duel_trigs, [(PlayerId.THREE, HERO_GLORFINDEL_ID, 198, 198)])
    sim_sac.step(0.5)  # Ambush
    sim_sac.step(0.5)  # Engages_Balrog
    for _ in range(14):  # 7s of combat on Spur
        sim_sac.step(0.5)
    kill_hero(sim_sac, HERO_GLORFINDEL_ID)
    sim_sac.step(0.5)  # HeroicSacrifice fires!
    sim_sac.step(1.0)  # Eagles arrive 1s later!
    assert any(name == "P3_Finale_Thorondor_HeroicSacrifice" for _, name in sim_sac.fired_log)
    assert any(name == "P3_Finale_Thorondor_Eagles_Arrive" for _, name in sim_sac.fired_log)
    assert not sim_sac.enabled[by_name["P3_Finale_Thorondor_Hold25s"].trigger_id]
    print("[PASS 18] Final Glorfindela: opuszczenie Wystepu resetuje 25s timer; dopiero 25s ciaglego utrzymania (Path A) lub poswiecenie (Path B) wzywa Orly.")
    print("=" * 80)


if __name__ == "__main__":
    run_stage_a_verification()
    shutil.rmtree("__pycache__", ignore_errors=True)
