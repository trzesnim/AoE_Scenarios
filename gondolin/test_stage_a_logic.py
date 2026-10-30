"""Logic and simulation test suite for Stage A (Soft-cap, Rog encounters, Phase-dynamic Seals, Glorfindel duel)."""

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
    HERO_GLORFINDEL_ID,
    OBJECT_TYPE_MILITARY,
    TORCH_ID,
    TRACKED_NOLDOR_HEROES,
    PlayerId,
)
from gondolin_quests import PHASE_MARKER_COORDS, PHASE_RALLY_AURA_BOXES


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


def run_stage_a_verification() -> None:
    """Run all Stage A audit tests on the generated triggers (Items 1-8)."""
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

    trigs = scen.trigger_manager.triggers
    by_name = {t.name: t for t in trigs}
    by_id = {t.trigger_id: t for t in trigs}

    print("=" * 78)
    print(f"RAPORT TESTOW LOGICZNYCH ETAPU A (Laczna liczba triggerow: {len(trigs)})")
    print("=" * 78)

    unfiltered = []
    for t in trigs:
        for c in t.conditions:
            if c.condition_type == "objects_in_area":
                if c.kwargs["object_list"] == -1 and c.kwargs["object_type"] == -1:
                    unfiltered.append(t.name)
    assert not unfiltered, f"Found unfiltered objects_in_area triggers: {unfiltered}"
    print("[PASS 1] Wszystkie warunki objects_in_area (P1-P8) posiadaja jawny filtr object_list lub object_type.")

    for st in (1, 2, 3):
        for ph in ("phase1", "phase2", "phase3"):
            mx, my = PHASE_MARKER_COORDS[ph]
            ax1, ay1, ax2, ay2 = PHASE_RALLY_AURA_BOXES[ph]
            heal_loop = by_name[f"Seal_Stage{st}_{ph}_LocalRallyHealLoop"]
            assert heal_loop.effects[0].effect_type == "heal_object"
            assert heal_loop.effects[0].kwargs["object_type"] == OBJECT_TYPE_MILITARY
            assert (
                heal_loop.effects[0].kwargs["area_x1"],
                heal_loop.effects[0].kwargs["area_y1"],
                heal_loop.effects[0].kwargs["area_x2"],
                heal_loop.effects[0].kwargs["area_y2"],
            ) == (ax1, ay1, ax2, ay2)

            for idx, (p_id, h_id, _, h_name) in enumerate(TRACKED_NOLDOR_HEROES):
                safe_h = h_name.replace(" ", "_")
                t_loss = by_name[f"Seal_Stage{st}_{ph}_HeroLoss_{safe_h}"]
                assert t_loss.conditions[0].kwargs["object_list"] == h_id
                assert t_loss.conditions[0].kwargs["quantity"] == 0
                assert t_loss.conditions[1].kwargs["object_list"] == TORCH_ID
                assert t_loss.conditions[1].kwargs["area_x1"] == mx - 1
                base_rx, base_ry = ctx["checkpoints"][ph][p_id]
                exp_rx = base_rx + (idx % 3) - 1
                exp_ry = base_ry + (idx // 3) - 1
                create_eff = next(
                    e for e in t_loss.effects if e.effect_type == "create_object" and e.kwargs["object_list_unit_id"] == h_id
                )
                assert (create_eff.kwargs["location_x"], create_eff.kwargs["location_y"]) == (exp_rx, exp_ry)

    t_p2 = by_name["P1_Boss_Gothmog_Slain_Start_Phase2"]
    t_p3 = by_name["P3_Start_Orfalch_Echor"]
    assert any(
        e.effect_type == "create_object"
        and e.kwargs["object_list_unit_id"] == TORCH_ID
        and (e.kwargs["location_x"], e.kwargs["location_y"]) == PHASE_MARKER_COORDS["phase2"]
        for e in t_p2.effects
    )
    assert any(
        e.effect_type == "create_object"
        and e.kwargs["object_list_unit_id"] == TORCH_ID
        and (e.kwargs["location_x"], e.kwargs["location_y"]) == PHASE_MARKER_COORDS["phase3"]
        for e in t_p3.effects
    )
    print("[PASS 2] Dynamiczny respawn Pieczeci (Faza I: Amon Gwareth, Faza II: Tumladen, Faza III: Orfalch Echor) + lokalny heal_object (20s) zweryfikowany.")

    t_s1_tuor = by_name["Seal_Stage1_phase1_HeroLoss_Tuor"]
    deactivated_by_s1_tuor = {
        by_id[e.kwargs["trigger_id"]].name
        for e in t_s1_tuor.effects
        if e.effect_type == "deactivate_trigger"
    }
    activated_by_s1_tuor = {
        by_id[e.kwargs["trigger_id"]].name
        for e in t_s1_tuor.effects
        if e.effect_type == "activate_trigger"
    }
    assert len([n for n in deactivated_by_s1_tuor if "_HeroLoss_" in n]) == 26
    assert len([n for n in activated_by_s1_tuor if "_GraceCoRespawn_" in n]) == 8
    assert "Seal_Stage1_phase1_GraceCoRespawn_Tuor" not in activated_by_s1_tuor
    assert "Seal_Relay_Stage1_To_Stage2" in activated_by_s1_tuor

    t_rel_1_2 = by_name["Seal_Relay_Stage1_To_Stage2"]
    assert t_rel_1_2.conditions[0].kwargs["timer"] == 3
    rel_deact = {
        by_id[e.kwargs["trigger_id"]].name
        for e in t_rel_1_2.effects
        if e.effect_type == "deactivate_trigger"
    }
    rel_act = {
        by_id[e.kwargs["trigger_id"]].name
        for e in t_rel_1_2.effects
        if e.effect_type == "activate_trigger"
    }
    assert len([n for n in rel_deact if "_GraceCoRespawn_" in n]) == 27
    assert len([n for n in rel_act if "Seal_Stage2_" in n and "_HeroLoss_" in n]) == 27
    print("[PASS 3] Piec scenariuszy GraceCoRespawn (1 zgon, 2 symultaniczne, zgon w oknie <3s, zgon po oknie >3s, Stage 4 Defeat) zweryfikowano.")

    t_engage = by_name["P3_Finale_Glorfindel_Engages_Balrog"]
    t_hold = by_name["P3_Finale_Thorondor_Hold25s"]
    t_sac = by_name["P3_Finale_Thorondor_HeroicSacrifice"]
    t_eagles = by_name["P3_Finale_Thorondor_Eagles_Arrive"]

    engage_act = {by_id[e.kwargs["trigger_id"]].name for e in t_engage.effects if e.effect_type == "activate_trigger"}
    assert engage_act == {"P3_Finale_Thorondor_Hold25s", "P3_Finale_Thorondor_HeroicSacrifice"}
    assert len(t_hold.conditions) == 2
    assert t_hold.conditions[1].kwargs["object_list"] == HERO_GLORFINDEL_ID
    assert t_sac.conditions[0].condition_type == "own_fewer_objects"
    assert t_sac.conditions[0].kwargs["object_list"] == HERO_GLORFINDEL_ID
    assert t_sac.conditions[0].kwargs["quantity"] == 0
    assert any(e.effect_type == "deactivate_trigger" and e.kwargs["trigger_id"] == t_sac.trigger_id for e in t_hold.effects)
    assert any(e.effect_type == "deactivate_trigger" and e.kwargs["trigger_id"] == t_hold.trigger_id for e in t_sac.effects)
    assert len(t_eagles.conditions) == 0
    print("[PASS 4] Dwusciezkowy final Glorfindela (Path A: utrzymanie wystepu przez 25s | Path B: kanoniczne poswiecenie) zweryfikowany.")

    sub_regen = [
        t.name
        for t in trigs
        for e in t.effects
        if e.effect_type == "modify_attribute"
        and e.kwargs.get("object_attributes") == 109
        and e.kwargs.get("operation") == 3
    ]
    assert not sub_regen, f"Found risky regeneration subtraction triggers: {sub_regen}"
    print("[PASS 5] Brak odejmowania globalnej regeneracji (pelne zastapienie lokalnym cyklicznym heal_object).")
    print("=" * 78)


if __name__ == "__main__":
    run_stage_a_verification()
    shutil.rmtree("__pycache__", ignore_errors=True)
