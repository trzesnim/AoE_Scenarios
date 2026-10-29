"""Balance Sanctuary, 3 Seals of Turgon, Phase I-III Quests, Dilemmas, and Victory logic."""

from __future__ import annotations

from typing import Any

from AoE2ScenarioParser.datasets.players import PlayerId
from AoE2ScenarioParser.datasets.trigger_lists import Operation
from gondolin_config import (
    ARMOR_CLASS_MELEE,
    ARMOR_CLASS_PIERCE,
    ATTR_ARMOR,
    ATTR_ATTACK,
    ATTR_HIT_POINTS,
    ATTR_MAXIMUM_RANGE,
    ATTR_SEARCH_RADIUS,
    BALANCE,
    ENEMY_BALROG_BOSS_ID,
    ENEMY_DIRE_WOLF_ID,
    ENEMY_GOTHMOG_ID,
    ENEMY_MAEGLIN_ID,
    ENEMY_MOLE_PIKE_ID,
    ENEMY_MOLE_TRAITOR_ID,
    ENEMY_ORC_BRUTE_ID,
    ENEMY_ORC_CROSSBOW_ID,
    ENEMY_ORC_INFANTRY_ID,
    ENEMY_WARG_RIDER_ID,
    FALCON_ID,
    HERO_DUILIN_ID,
    HERO_EARENDIL_ID,
    HERO_ECTHELION_ID,
    HERO_GLORFINDEL_ID,
    HERO_IDRIL_ID,
    HERO_TUOR_ID,
    HUMAN_PLAYERS,
    ROCK_CLIFF_ID,
    SANCTUARY_KING_ID,
    UNIT_ARCH_LONGBOW_ID,
    UNIT_ARCH_RATTAN_ID,
    UNIT_EAGLE_VANGUARD_ID,
    UNIT_FLOWER_CAV_ID,
    UNIT_FOUNTAIN_GUARD_ID,
    UNIT_FOUNTAIN_HALB_ID,
    UNIT_HAMMER_SMITH_ID,
    UNIT_REFUGEE_CART_ID,
    UNIT_REFUGEE_CIV_ID,
    UNIT_SWALLOW_SNIPER_ID,
    UNIT_TREE_PIKE_ID,
    VULTURE_ID,
)
from gondolin_mechanics import (
    PLAYER_MELEE_RETINUE,
    PLAYER_RANGED_RETINUE,
    add_chat_and_flare,
    add_enemy_combat_buff,
    apply_unit_lore_name,
    award_glory_gold,
    create_escalating_encounter,
    grant_soft_cap_reinforcements,
    safe_call,
    spawn_progressive_revealer,
)


def _setup_balance_sanctuary(tm: Any, ctx: dict[str, Any]) -> None:
    """Configure the 5-level Balance Sanctuary (-2 to +2) with mutual lockouts and 2s Relays."""
    sanc = ctx["sanctuary"]
    x1, y1, x2, y2 = sanc["x1"], sanc["y1"], sanc["x2"], sanc["y2"]
    cx, cy = sanc["cx"], sanc["cy"]
    hx1, hy1, hx2, hy2 = sanc["harder_area"]
    ex1, ey1, ex2, ey2 = sanc["easier_area"]

    # Relays to respawn the Sanctuary King in the center after 2 seconds
    t_relay_h1 = tm.add_trigger(
        name="Sanctuary_Relay2s_Harder1",
        enabled=False,
        looping=False,
    )
    safe_call(t_relay_h1.new_condition.timer, timer=2)
    safe_call(
        t_relay_h1.new_effect.create_object,
        source_player=PlayerId.ONE,
        object_list_unit_id=SANCTUARY_KING_ID,
        location_x=cx,
        location_y=cy,
    )
    apply_unit_lore_name(t_relay_h1, PlayerId.ONE, SANCTUARY_KING_ID)

    t_relay_h2 = tm.add_trigger(
        name="Sanctuary_Relay2s_Harder2",
        enabled=False,
        looping=False,
    )
    safe_call(t_relay_h2.new_condition.timer, timer=2)
    safe_call(
        t_relay_h2.new_effect.create_object,
        source_player=PlayerId.ONE,
        object_list_unit_id=SANCTUARY_KING_ID,
        location_x=cx,
        location_y=cy,
    )
    apply_unit_lore_name(t_relay_h2, PlayerId.ONE, SANCTUARY_KING_ID)

    t_relay_e1 = tm.add_trigger(
        name="Sanctuary_Relay2s_Easier1",
        enabled=False,
        looping=False,
    )
    safe_call(t_relay_e1.new_condition.timer, timer=2)
    safe_call(
        t_relay_e1.new_effect.create_object,
        source_player=PlayerId.ONE,
        object_list_unit_id=SANCTUARY_KING_ID,
        location_x=cx,
        location_y=cy,
    )
    apply_unit_lore_name(t_relay_e1, PlayerId.ONE, SANCTUARY_KING_ID)

    t_relay_e2 = tm.add_trigger(
        name="Sanctuary_Relay2s_Easier2",
        enabled=False,
        looping=False,
    )
    safe_call(t_relay_e2.new_condition.timer, timer=2)
    safe_call(
        t_relay_e2.new_effect.create_object,
        source_player=PlayerId.ONE,
        object_list_unit_id=SANCTUARY_KING_ID,
        location_x=cx,
        location_y=cy,
    )
    apply_unit_lore_name(t_relay_e2, PlayerId.ONE, SANCTUARY_KING_ID)

    # Harder Step 1 (+1) and Step 2 (+2)
    t_hard_1 = tm.add_trigger(
        name="Sanctuary_Harder_Step1",
        enabled=True,
        looping=False,
    )
    t_hard_2 = tm.add_trigger(
        name="Sanctuary_Harder_Step2",
        enabled=False,
        looping=False,
    )

    # Easier Step 1 (-1) and Step 2 (-2)
    t_easy_1 = tm.add_trigger(
        name="Sanctuary_Easier_Step1",
        enabled=True,
        looping=False,
    )
    t_easy_2 = tm.add_trigger(
        name="Sanctuary_Easier_Step2",
        enabled=False,
        looping=False,
    )

    # Configure Harder Step 1 (+1: +1000 Glory)
    safe_call(
        t_hard_1.new_condition.objects_in_area,
        source_player=PlayerId.ONE,
        object_list=SANCTUARY_KING_ID,
        area_x1=hx1,
        area_y1=hy1,
        area_x2=hx2,
        area_y2=hy2,
        quantity=1,
    )
    safe_call(
        t_hard_1.new_effect.remove_object,
        source_player=PlayerId.ONE,
        object_list_unit_id=SANCTUARY_KING_ID,
        area_x1=x1,
        area_y1=y1,
        area_x2=x2,
        area_y2=y2,
    )
    safe_call(
        t_hard_1.new_effect.deactivate_trigger,
        trigger_id=t_easy_1.trigger_id,
    )
    add_enemy_combat_buff(
        t_hard_1,
        hp_delta=BALANCE["sanctuary_harder_hp_add"],
        atk_delta=BALANCE["sanctuary_harder_atk_add"],
    )
    award_glory_gold(
        t_hard_1,
        BALANCE["glory_scores"]["difficulty_plus_1"],
        "<RED>[Sanktuarium Balansu +1] Sily Morgotha wzmocnione (+20 HP, +2 Ataku)! Premia: +1000 Chwaly!",
    )
    safe_call(
        t_hard_1.new_effect.activate_trigger,
        trigger_id=t_relay_h1.trigger_id,
    )
    safe_call(
        t_relay_h1.new_effect.activate_trigger,
        trigger_id=t_hard_2.trigger_id,
    )

    # Configure Harder Step 2 (+2: total +2000 Glory from difficulty_plus_2)
    plus_2_delta = (
        BALANCE["glory_scores"]["difficulty_plus_2"]
        - BALANCE["glory_scores"]["difficulty_plus_1"]
    )
    safe_call(
        t_hard_2.new_condition.objects_in_area,
        source_player=PlayerId.ONE,
        object_list=SANCTUARY_KING_ID,
        area_x1=hx1,
        area_y1=hy1,
        area_x2=hx2,
        area_y2=hy2,
        quantity=1,
    )
    safe_call(
        t_hard_2.new_effect.remove_object,
        source_player=PlayerId.ONE,
        object_list_unit_id=SANCTUARY_KING_ID,
        area_x1=x1,
        area_y1=y1,
        area_x2=x2,
        area_y2=y2,
    )
    add_enemy_combat_buff(
        t_hard_2,
        hp_delta=BALANCE["sanctuary_harder_hp_add"],
        atk_delta=BALANCE["sanctuary_harder_atk_add"],
    )
    award_glory_gold(
        t_hard_2,
        plus_2_delta,
        "<RED>[Sanktuarium Balansu +2 (Maksimum)] Sily Morgotha ponownie wzmocnione (lacznie +40 HP, +4 Ataku, +2000 Chwaly)!",
    )
    safe_call(
        t_hard_2.new_effect.activate_trigger,
        trigger_id=t_relay_h2.trigger_id,
    )

    # Configure Easier Step 1 (-1: -500 Glory)
    safe_call(
        t_easy_1.new_condition.objects_in_area,
        source_player=PlayerId.ONE,
        object_list=SANCTUARY_KING_ID,
        area_x1=ex1,
        area_y1=ey1,
        area_x2=ex2,
        area_y2=ey2,
        quantity=1,
    )
    safe_call(
        t_easy_1.new_effect.remove_object,
        source_player=PlayerId.ONE,
        object_list_unit_id=SANCTUARY_KING_ID,
        area_x1=x1,
        area_y1=y1,
        area_x2=x2,
        area_y2=y2,
    )
    safe_call(
        t_easy_1.new_effect.deactivate_trigger,
        trigger_id=t_hard_1.trigger_id,
    )
    add_enemy_combat_buff(
        t_easy_1,
        hp_delta=0,
        atk_delta=0,
        use_multiply_hp=True,
        hp_mult=BALANCE["sanctuary_easier_hp_mult"],
    )
    award_glory_gold(
        t_easy_1,
        BALANCE["glory_scores"]["difficulty_minus_1"],
        "<GREEN>[Sanktuarium Balansu -1] Pancerze wroga oslabione (-15% HP)! Koszt: -500 Chwaly.",
    )
    safe_call(
        t_easy_1.new_effect.activate_trigger,
        trigger_id=t_relay_e1.trigger_id,
    )
    safe_call(
        t_relay_e1.new_effect.activate_trigger,
        trigger_id=t_easy_2.trigger_id,
    )

    # Configure Easier Step 2 (-2: total -1000 Glory from difficulty_minus_2)
    minus_2_delta = (
        BALANCE["glory_scores"]["difficulty_minus_2"]
        - BALANCE["glory_scores"]["difficulty_minus_1"]
    )
    safe_call(
        t_easy_2.new_condition.objects_in_area,
        source_player=PlayerId.ONE,
        object_list=SANCTUARY_KING_ID,
        area_x1=ex1,
        area_y1=ey1,
        area_x2=ex2,
        area_y2=ey2,
        quantity=1,
    )
    safe_call(
        t_easy_2.new_effect.remove_object,
        source_player=PlayerId.ONE,
        object_list_unit_id=SANCTUARY_KING_ID,
        area_x1=x1,
        area_y1=y1,
        area_x2=x2,
        area_y2=y2,
    )
    add_enemy_combat_buff(
        t_easy_2,
        hp_delta=0,
        atk_delta=0,
        use_multiply_hp=True,
        hp_mult=BALANCE["sanctuary_easier_hp_mult"],
    )
    award_glory_gold(
        t_easy_2,
        minus_2_delta,
        "<GREEN>[Sanktuarium Balansu -2 (Minimum)] Pancerze wroga ponownie oslabione (lacznie -1000 Chwaly).",
    )
    safe_call(
        t_easy_2.new_effect.activate_trigger,
        trigger_id=t_relay_e2.trigger_id,
    )


def _setup_three_seals_of_turgon(tm: Any, ctx: dict[str, Any]) -> dict[str, Any]:
    """Implement the 3 Seals of Turgon reserve system with quantity=0, 5s stage relays, and 20s shield."""
    t_seals_ui = tm.add_trigger(
        name="UI_Seals_Of_Turgon_3",
        enabled=True,
        looping=False,
    )
    t_seals_ui.short_description = "[CHWALA] Pieczecie Rezerwy Turgona: 3/3 | Wynik Chwaly = Zloto P1"
    t_seals_ui.display_on_screen = 1
    t_seals_ui.description_order = 115

    t_seals_2_ui = tm.add_trigger(
        name="UI_Seals_Of_Turgon_2",
        enabled=False,
        looping=False,
    )
    t_seals_2_ui.short_description = "[CHWALA] Pieczecie Rezerwy Turgona: 2/3 (1 zuzyta!)"
    t_seals_2_ui.display_on_screen = 1
    t_seals_2_ui.description_order = 115

    t_seals_1_ui = tm.add_trigger(
        name="UI_Seals_Of_Turgon_1",
        enabled=False,
        looping=False,
    )
    t_seals_1_ui.short_description = "[CHWALA] Pieczecie Rezerwy Turgona: 1/3 (UWAGA: Ostatnia Pieczec!)"
    t_seals_1_ui.display_on_screen = 1
    t_seals_1_ui.description_order = 115

    t_seals_0_ui = tm.add_trigger(
        name="UI_Seals_Of_Turgon_0",
        enabled=False,
        looping=False,
    )
    t_seals_0_ui.short_description = "[ALARM] Pieczecie Rezerwy: 0/3 - Kolejna smierc Bohatera oznacza PORAZKE!"
    t_seals_0_ui.display_on_screen = 1
    t_seals_0_ui.description_order = 115

    tracked_heroes: list[tuple[PlayerId, int, int, str]] = [
        (PlayerId.ONE, HERO_TUOR_ID, UNIT_HAMMER_SMITH_ID, "Tuor"),
        (PlayerId.TWO, HERO_ECTHELION_ID, UNIT_FOUNTAIN_GUARD_ID, "Ecthelion"),
        (PlayerId.THREE, HERO_GLORFINDEL_ID, UNIT_SWALLOW_SNIPER_ID, "Glorfindel"),
        (PlayerId.FOUR, HERO_IDRIL_ID, UNIT_TREE_PIKE_ID, "Idril Celebrindal"),
        (PlayerId.FOUR, HERO_EARENDIL_ID, UNIT_TREE_PIKE_ID, "Maly Earendil"),
    ]

    cp_p1 = ctx["checkpoints"]["phase1"]
    seal_stage_triggers: dict[int, list[Any]] = {1: [], 2: [], 3: [], 4: []}

    # Arm Stage 1 only after 5 seconds so initialization at 0:00-0:03 is 100% complete
    t_arm_seals = tm.add_trigger(
        name="Seal_Arm_Stage1_At_05s",
        enabled=True,
        looping=False,
    )
    safe_call(t_arm_seals.new_condition.timer, timer=5)

    for stage in (1, 2, 3, 4):
        for p_id, h_id, guard_id, h_name in tracked_heroes:
            rx, ry = cp_p1[p_id]
            t_loss = tm.add_trigger(
                name=f"Seal_Stage{stage}_HeroLoss_{h_name}",
                enabled=False,
                looping=False,
            )
            # CRITICAL FIX P0: quantity=0 means 0 living heroes of type h_id (hero died!)
            safe_call(
                t_loss.new_condition.own_fewer_objects,
                source_player=p_id,
                object_list=h_id,
                quantity=0,
            )

            if stage <= 3:
                safe_call(
                    t_loss.new_effect.create_object,
                    source_player=p_id,
                    object_list_unit_id=h_id,
                    location_x=rx,
                    location_y=ry,
                )
                for i in range(6):
                    safe_call(
                        t_loss.new_effect.create_object,
                        source_player=p_id,
                        object_list_unit_id=guard_id,
                        location_x=rx + (i % 3) - 1,
                        location_y=ry + 1 + (i // 3),
                    )
                apply_unit_lore_name(t_loss, p_id, h_id)
                apply_unit_lore_name(t_loss, p_id, guard_id)
                award_glory_gold(
                    t_loss,
                    -BALANCE["glory_scores"]["seal_preserved_bonus"],
                    f"<RED>[Pieczec Turgona #{stage} Zuzyta!] {h_name} padl w boju! Gwardia Krolewska odradza bohatera na Punkcie Zbornym z 20s oslona (-500 Chwaly).",
                )
            else:
                add_chat_and_flare(
                    t_loss,
                    f"<RED>[UPADEK GONDOLINU] {h_name} polegl, a wszystkie 3 Pieczecie Rezerwy Turgona zostaly wyczerpane! Krolestwo upadlo.",
                    rx,
                    ry,
                )
                for hp_id in HUMAN_PLAYERS:
                    safe_call(
                        t_loss.new_effect.declare_victory,
                        source_player=hp_id,
                        enabled=False,
                    )

            seal_stage_triggers[stage].append(t_loss)

    for t_s1 in seal_stage_triggers[1]:
        safe_call(
            t_arm_seals.new_effect.activate_trigger,
            trigger_id=t_s1.trigger_id,
        )

    # Wire stage transitions via 5-second relay triggers + 20-second rally point protection shield
    ui_chain = [
        (1, t_seals_ui, t_seals_2_ui),
        (2, t_seals_2_ui, t_seals_1_ui),
        (3, t_seals_1_ui, t_seals_0_ui),
    ]
    for st_num, old_ui, new_ui in ui_chain:
        # 20s Protection Shield around Amon Gwareth rally point
        t_shield = tm.add_trigger(
            name=f"Seal_Stage{st_num}_ShieldAura",
            enabled=False,
            looping=True,
        )
        safe_call(t_shield.new_condition.timer, timer=2)
        for hp_id in HUMAN_PLAYERS:
            safe_call(
                t_shield.new_effect.damage_object,
                source_player=hp_id,
                area_x1=52,
                area_y1=50,
                area_x2=70,
                area_y2=70,
                quantity=-45,
            )
        t_shield_off = tm.add_trigger(
            name=f"Seal_Stage{st_num}_ShieldStop20s",
            enabled=False,
            looping=False,
        )
        safe_call(t_shield_off.new_condition.timer, timer=20)
        safe_call(
            t_shield_off.new_effect.deactivate_trigger,
            trigger_id=t_shield.trigger_id,
        )

        # 5-second relay before arming Stage N+1 (prevents single-tick cascade across stages!)
        t_stage_relay = tm.add_trigger(
            name=f"Seal_Relay_Stage{st_num}_To_Stage{st_num + 1}",
            enabled=False,
            looping=False,
        )
        safe_call(t_stage_relay.new_condition.timer, timer=5)
        for t_next in seal_stage_triggers[st_num + 1]:
            safe_call(
                t_stage_relay.new_effect.activate_trigger,
                trigger_id=t_next.trigger_id,
            )

        for t_curr in seal_stage_triggers[st_num]:
            safe_call(
                t_curr.new_effect.deactivate_trigger,
                trigger_id=old_ui.trigger_id,
            )
            safe_call(
                t_curr.new_effect.activate_trigger,
                trigger_id=new_ui.trigger_id,
            )
            safe_call(
                t_curr.new_effect.activate_trigger,
                trigger_id=t_shield.trigger_id,
            )
            safe_call(
                t_curr.new_effect.activate_trigger,
                trigger_id=t_shield_off.trigger_id,
            )
            for t_sibling in seal_stage_triggers[st_num]:
                if t_sibling.trigger_id != t_curr.trigger_id:
                    safe_call(
                        t_curr.new_effect.deactivate_trigger,
                        trigger_id=t_sibling.trigger_id,
                    )
            safe_call(
                t_curr.new_effect.activate_trigger,
                trigger_id=t_stage_relay.trigger_id,
            )

    return {
        "glorfindel_stage_triggers": [
            t for st in (1, 2, 3, 4) for t in seal_stage_triggers[st] if "Glorfindel" in t.name
        ]
    }


def _setup_refugee_rescues(tm: Any, ctx: dict[str, Any]) -> None:
    """Allow players to rescue the 6 stranded Noldor citizen/artisan groups for reinforcements & Glory."""
    for rg in ctx["refugee_groups"]:
        rx, ry = rg["x"], rg["y"]
        r_player = rg["reward_player"]
        r_unit = rg["reward_unit"]
        r_count = rg["reward_count"]
        r_name = rg["name"]

        t_rescue = tm.add_trigger(
            name=f"Rescue_{rg['id']}",
            enabled=True,
            looping=False,
        )
        # Require 2 objects if Player 1 is the rescuer so a lone Map Revealer cannot trigger rescue
        req_qty = 2 if r_player == PlayerId.ONE else 1
        safe_call(
            t_rescue.new_condition.objects_in_area,
            source_player=r_player,
            area_x1=rx - 6,
            area_y1=ry - 6,
            area_x2=rx + 6,
            area_y2=ry + 6,
            quantity=req_qty,
        )
        safe_call(
            t_rescue.new_effect.remove_object,
            source_player=PlayerId.GAIA,
            object_list_unit_id=UNIT_REFUGEE_CIV_ID,
            area_x1=rx - 4,
            area_y1=ry - 4,
            area_x2=rx + 4,
            area_y2=ry + 4,
        )
        for i in range(r_count):
            safe_call(
                t_rescue.new_effect.create_object,
                source_player=r_player,
                object_list_unit_id=r_unit,
                location_x=rx + (i % 3) - 1,
                location_y=ry + (i // 3) - 1,
            )
        apply_unit_lore_name(t_rescue, r_player, r_unit)
        award_glory_gold(
            t_rescue,
            BALANCE["glory_scores"]["refugee_group_saved"],
            f"<GREEN>[Ocaleni Noldorowie] Uratowano grupe '{r_name}'! Do szeregow P{r_player.value} dolacza {r_count} elitarnych wojownikow (+150 Chwaly)!",
        )


def _setup_phase1_city_and_dilemmas(tm: Any, ctx: dict[str, Any]) -> list[Any]:
    """Configure Phase I Objectives, Remote Co-op Quests, Individual Quests, and the 3-Enclave Dilemma."""
    sectors = ctx["sectors"]
    rocks = ctx["destructible_rocks"]
    q_bldgs = ctx["quest_buildings"]
    phase1_ui_triggers: list[Any] = []

    def add_p1_objective(name: str, text: str, order: int) -> Any:
        trig = tm.add_trigger(name=name, enabled=True, looping=False)
        trig.short_description = text
        trig.display_on_screen = 1
        trig.description_order = order
        phase1_ui_triggers.append(trig)
        return trig

    add_p1_objective(
        "UI_P1_Main",
        "[FAZA I - GLOWNE] Odbijcie Caragdur i Akwedukt, po czym zbierzcie sily na Amon Gwareth",
        110,
    )
    add_p1_objective(
        "UI_P1_Dilemma_Enclaves",
        "[DYLEMAT ENKLAW] Kuznie (Zach: +3 Atk/+2 Panc) | Targ (Wsch: +12 Gwardii) | Harfa (Pld: +Jazda/Mnisi)",
        108,
    )
    ui_q_caragdur = add_p1_objective(
        "UI_P1_Q_Caragdur",
        "[CO-OP P1+P4] Caragdur: P1 przebija brame od pld., P4 chroni Earendila przed Maeglinem (P8)",
        105,
    )
    ui_q_aqueduct = add_p1_objective(
        "UI_P1_Q_Aqueduct",
        "[CO-OP P2->P3] Akwedukt: P2 niszczy Sluzy (P8) na wschodzie, by ugasic pozary u P3 i zalac fose",
        104,
    )
    ui_q_snow = add_p1_objective(
        "UI_P1_Q_SnowTower",
        "[P3 - Duilin] Wieza ze Sniegu: Wejdz na baszte na polnocy, by odslonic mape i zyskac +1 Zasiegu",
        102,
    )
    ui_q_trees = add_p1_objective(
        "UI_P1_Q_SacredTrees",
        "[P4 - Idril] Drzewa Glingal i Belthil: Zabezpiecz pedy na Amon Gwareth (+60 HP Bohaterow)",
        101,
    )

    # Q1 [Co-op P1 + P4]: Betrayal of Maeglin at Caragdur
    t_spawn_maeglin = tm.add_trigger(
        name="P1_Spawn_Maeglin_Traitors",
        enabled=True,
        looping=False,
    )
    safe_call(t_spawn_maeglin.new_condition.timer, timer=10)
    safe_call(
        t_spawn_maeglin.new_effect.create_object,
        source_player=PlayerId.EIGHT,
        object_list_unit_id=ENEMY_MAEGLIN_ID,
        location_x=20,
        location_y=38,
    )
    for i in range(8):
        safe_call(
            t_spawn_maeglin.new_effect.create_object,
            source_player=PlayerId.EIGHT,
            object_list_unit_id=ENEMY_MOLE_TRAITOR_ID if i % 2 == 0 else ENEMY_MOLE_PIKE_ID,
            location_x=20 + (i % 4),
            location_y=34 + (i // 4),
        )
    for m_id in (ENEMY_MAEGLIN_ID, ENEMY_MOLE_TRAITOR_ID, ENEMY_MOLE_PIKE_ID):
        apply_unit_lore_name(t_spawn_maeglin, PlayerId.EIGHT, m_id)
    add_chat_and_flare(
        t_spawn_maeglin,
        "<PURPLE>[Zdrada Domu Kreta!] Maeglin (P8) zamknal bramy Caragdur i uderza na Dwor Tuora, by porwac Idril oraz Earendila! P1 musi uderzyc z odsieczą od poludnia!",
        24,
        32,
    )

    cg_x1, cg_y1, cg_x2, cg_y2 = sectors["caragdur_gate"]
    t_breach_caragdur = tm.add_trigger(
        name="P1_Tuor_Breaches_Caragdur_Gate",
        enabled=True,
        looping=False,
    )
    safe_call(
        t_breach_caragdur.new_condition.objects_in_area,
        source_player=PlayerId.ONE,
        area_x1=cg_x1,
        area_y1=cg_y1,
        area_x2=cg_x2,
        area_y2=cg_y2,
        quantity=2,
    )
    safe_call(
        t_breach_caragdur.new_effect.remove_object,
        selected_object_ids=rocks["caragdur_blockade"],
    )
    spawn_progressive_revealer(t_breach_caragdur, 18, 42)
    add_chat_and_flare(
        t_breach_caragdur,
        "<BLUE>[Tuor] Topor Dramborleg roztrzaskal barykade zdrajcow! Polaczcie sily z Idril (P4) i zepchnijcie Maeglina ze skaly Caragdur!",
        42,
        26,
    )

    t_kill_maeglin = tm.add_trigger(
        name="P1_Quest_Caragdur_Completed",
        enabled=True,
        looping=False,
    )
    safe_call(
        t_kill_maeglin.new_condition.destroy_object,
        unit_object=q_bldgs["caragdur_keep"]["ref_id"],
    )
    safe_call(
        t_kill_maeglin.new_effect.deactivate_trigger,
        trigger_id=ui_q_caragdur.trigger_id,
    )
    for p_id in (PlayerId.ONE, PlayerId.FOUR):
        for u_id in PLAYER_MELEE_RETINUE:
            safe_call(
                t_kill_maeglin.new_effect.modify_attribute,
                source_player=p_id,
                object_list_unit_id=u_id,
                object_attributes=ATTR_ATTACK,
                operation=Operation.ADD,
                armour_attack_class=ARMOR_CLASS_MELEE,
                armour_attack_quantity=2,
            )
    award_glory_gold(
        t_kill_maeglin,
        BALANCE["glory_scores"]["side_quest_completed"],
        "<GREEN>[Koniec Zdrajcy!] Tuor zrzucil Maeglina z urwiska Caragdur! Dom Kreta rozbity (+2 Ataku dla P1/P4, +300 Chwaly)!",
    )

    # Q2 [Remote Co-op P2 -> P3]: Great Aqueduct Sluices & Extinguishing North Fires
    aq_x1, aq_y1, aq_x2, aq_y2 = sectors["aqueduct_sluice"]
    create_escalating_encounter(
        tm,
        "Aqueduct_Guard",
        (aq_x1 - 4, aq_y1 - 4, aq_x2 + 4, aq_y2 + 4),
        (84, 70),
        [(PlayerId.EIGHT, ENEMY_MOLE_TRAITOR_ID, 6, 84, 76)],
        [(PlayerId.FIVE, ENEMY_ORC_BRUTE_ID, 5, 86, 78)],
    )

    t_aqueduct_done = tm.add_trigger(
        name="P1_Quest_Aqueduct_Completed",
        enabled=True,
        looping=False,
    )
    safe_call(
        t_aqueduct_done.new_condition.destroy_object,
        unit_object=q_bldgs["aqueduct_control"]["ref_id"],
    )
    safe_call(
        t_aqueduct_done.new_effect.deactivate_trigger,
        trigger_id=ui_q_aqueduct.trigger_id,
    )
    safe_call(
        t_aqueduct_done.new_effect.deactivate_trigger,
        trigger_id=ctx["north_fire_trigger_id"],
    )
    safe_call(
        t_aqueduct_done.new_effect.remove_object,
        selected_object_ids=rocks["north_fire_objects"],
    )
    safe_call(
        t_aqueduct_done.new_effect.remove_object,
        selected_object_ids=rocks["aqueduct_dry_rocks"],
    )
    mx1, _, mx2, my2 = sectors["north_moat"]
    safe_call(
        t_aqueduct_done.new_effect.damage_object,
        source_player=PlayerId.SIX,
        area_x1=mx1,
        area_y1=40,
        area_x2=mx2,
        area_y2=my2,
        quantity=600,
    )
    award_glory_gold(
        t_aqueduct_done,
        BALANCE["glory_scores"]["side_quest_completed"],
        "<AQUA>[Wody Ectheliona!] P2 otworzyl sluzy Akweduktu! Pozary w Dzielnicy Polnocnej ugaszone, a fala wodna zalala fose i oslabila Zelazne Smoki P6 (+300 Chwaly)!",
    )

    # Q3 [Individual P3 - Duilin]: Tower of Snow Vantage Point
    sx1, sy1, sx2, sy2 = sectors["tower_of_snow"]
    t_snow_tower = tm.add_trigger(
        name="P1_Quest_SnowTower_Completed",
        enabled=True,
        looping=False,
    )
    safe_call(
        t_snow_tower.new_condition.objects_in_area,
        source_player=PlayerId.THREE,
        area_x1=sx1,
        area_y1=sy1,
        area_x2=sx2,
        area_y2=sy2,
        quantity=1,
    )
    safe_call(
        t_snow_tower.new_effect.deactivate_trigger,
        trigger_id=ui_q_snow.trigger_id,
    )
    # Place revealers outside encounter detection boxes (or owned by P3) to avoid P1 false triggers
    for rx, ry in [(61, 108), (94, 63), (24, 63), (92, 26)]:
        spawn_progressive_revealer(t_snow_tower, rx, ry, player=PlayerId.THREE)
    for p_id in (PlayerId.TWO, PlayerId.THREE):
        for r_id in (UNIT_ARCH_LONGBOW_ID, UNIT_ARCH_RATTAN_ID, UNIT_SWALLOW_SNIPER_ID, HERO_DUILIN_ID):
            safe_call(
                t_snow_tower.new_effect.modify_attribute,
                source_player=p_id,
                object_list_unit_id=r_id,
                object_attributes=ATTR_MAXIMUM_RANGE,
                operation=Operation.ADD,
                quantity=1,
            )
            safe_call(
                t_snow_tower.new_effect.modify_attribute,
                source_player=p_id,
                object_list_unit_id=r_id,
                object_attributes=ATTR_SEARCH_RADIUS,
                operation=Operation.ADD,
                quantity=1,
            )
    award_glory_gold(
        t_snow_tower,
        BALANCE["glory_scores"]["side_quest_completed"],
        "<GREEN>[Wzrok Jaskolki - P3] Strzelcy Duilina obsadzili Wieze ze Sniegu! Odkryto pozycje enklaw w miescie, a lucznicy P2/P3 zyskali +1 Zasiegu (+300 Chwaly)!",
    )

    # Q4 [Individual P4 - Idril]: Saplings of Glingal and Belthil
    rf_x1, rf_y1, rf_x2, rf_y2 = sectors["royal_fountain"]
    t_sacred_trees = tm.add_trigger(
        name="P1_Quest_SacredTrees_Completed",
        enabled=True,
        looping=False,
    )
    safe_call(
        t_sacred_trees.new_condition.objects_in_area,
        source_player=PlayerId.FOUR,
        object_list=HERO_IDRIL_ID,
        area_x1=rf_x1,
        area_y1=rf_y1,
        area_x2=rf_x2,
        area_y2=rf_y2,
        quantity=1,
    )
    safe_call(
        t_sacred_trees.new_effect.deactivate_trigger,
        trigger_id=ui_q_trees.trigger_id,
    )
    for h_id, h_cfg in BALANCE["heroes"].items():
        safe_call(
            t_sacred_trees.new_effect.modify_attribute,
            source_player=h_cfg["player"],
            object_list_unit_id=h_id,
            object_attributes=ATTR_HIT_POINTS,
            operation=Operation.ADD,
            quantity=60,
        )
    award_glory_gold(
        t_sacred_trees,
        BALANCE["glory_scores"]["side_quest_completed"],
        "<YELLOW>[Dziedzictwo Gondolinu - P4] Idril zabezpieczyla pedy Zlotego i Srebrnego Drzewa (Glingal i Belthil)! Wszyscy Bohaterowie otrzymuja +60 HP (+300 Chwaly)!",
    )

    # Enclave A (West): Forges of Rog - bring Mithril Carts to Amon Gwareth
    fg_x1, fg_y1, fg_x2, fg_y2 = sectors["enclave_forges"]
    create_escalating_encounter(
        tm,
        "West_Forges",
        (fg_x1, fg_y1, fg_x2 + 6, fg_y2),
        (28, 63),
        [(PlayerId.FIVE, ENEMY_ORC_BRUTE_ID, 7, 26, 76), (PlayerId.EIGHT, ENEMY_MOLE_TRAITOR_ID, 4, 24, 54)],
        [(PlayerId.SEVEN, ENEMY_BALROG_BOSS_ID, 1, 24, 78)],
    )
    ag_x1, ag_y1, ag_x2, ag_y2 = sectors["amon_gwareth"]
    t_forges_saved = tm.add_trigger(
        name="P1_EnclaveA_Forges_Mithril_Delivered",
        enabled=True,
        looping=False,
    )
    safe_call(
        t_forges_saved.new_condition.objects_in_area,
        source_player=PlayerId.ONE,
        object_list=UNIT_REFUGEE_CART_ID,
        area_x1=ag_x1,
        area_y1=ag_y1,
        area_x2=ag_x2,
        area_y2=ag_y2,
        quantity=1,
    )
    for p_id in HUMAN_PLAYERS:
        for m_id in PLAYER_MELEE_RETINUE:
            safe_call(
                t_forges_saved.new_effect.modify_attribute,
                source_player=p_id,
                object_list_unit_id=m_id,
                object_attributes=ATTR_ATTACK,
                operation=Operation.ADD,
                armour_attack_class=ARMOR_CLASS_MELEE,
                armour_attack_quantity=3,
            )
        for r_id in PLAYER_RANGED_RETINUE:
            safe_call(
                t_forges_saved.new_effect.modify_attribute,
                source_player=p_id,
                object_list_unit_id=r_id,
                object_attributes=ATTR_ATTACK,
                operation=Operation.ADD,
                armour_attack_class=ARMOR_CLASS_PIERCE,
                armour_attack_quantity=3,
            )
        for u_id in PLAYER_MELEE_RETINUE + PLAYER_RANGED_RETINUE:
            safe_call(
                t_forges_saved.new_effect.modify_attribute,
                source_player=p_id,
                object_list_unit_id=u_id,
                object_attributes=ATTR_ARMOR,
                operation=Operation.ADD,
                armour_attack_class=ARMOR_CLASS_MELEE,
                armour_attack_quantity=2,
            )
            safe_call(
                t_forges_saved.new_effect.modify_attribute,
                source_player=p_id,
                object_list_unit_id=u_id,
                object_attributes=ATTR_ARMOR,
                operation=Operation.ADD,
                armour_attack_class=ARMOR_CLASS_PIERCE,
                armour_attack_quantity=2,
            )
    award_glory_gold(
        t_forges_saved,
        BALANCE["glory_scores"]["side_quest_completed"],
        "<BLUE>[Enklawa A - Kuznie Roga!] Wozy z Mithrilem dotarly na Amon Gwareth! Wszystkie oddzialy Noldorow zyskuja +3 Ataku i +2/+2 Pancerza (+300 Chwaly)!",
    )

    # Enclave B (East): Great Market of Penlod
    mk_x1, mk_y1, mk_x2, mk_y2 = sectors["enclave_market"]
    t_mkt_base, _ = create_escalating_encounter(
        tm,
        "East_Market",
        (mk_x1 - 4, mk_y1, mk_x2, mk_y2),
        (92, 63),
        [(PlayerId.FIVE, ENEMY_ORC_INFANTRY_ID, 10, 98, 66), (PlayerId.FIVE, ENEMY_ORC_CROSSBOW_ID, 6, 100, 60)],
        [(PlayerId.FIVE, ENEMY_WARG_RIDER_ID, 6, 102, 64)],
    )
    for i in range(6):
        safe_call(
            t_mkt_base.new_effect.create_object,
            source_player=PlayerId.TWO,
            object_list_unit_id=UNIT_FOUNTAIN_HALB_ID,
            location_x=90 + (i % 3),
            location_y=62 + (i // 3),
        )
        safe_call(
            t_mkt_base.new_effect.create_object,
            source_player=PlayerId.TWO,
            object_list_unit_id=UNIT_ARCH_LONGBOW_ID,
            location_x=90 + (i % 3),
            location_y=65 + (i // 3),
        )
    apply_unit_lore_name(t_mkt_base, PlayerId.TWO, UNIT_FOUNTAIN_HALB_ID)
    apply_unit_lore_name(t_mkt_base, PlayerId.TWO, UNIT_ARCH_LONGBOW_ID)
    award_glory_gold(
        t_mkt_base,
        BALANCE["glory_scores"]["side_quest_completed"],
        "<RED>[Enklawa B - Wielki Targ!] Odsiecz dotarla do garnizonu Penloda! +12 elitarnych halabardnikow i lucznikow dolacza do obrony (+300 Chwaly)!",
    )

    # Enclave C (South-East): Court of Salgant & House of the Harp
    hp_x1, hp_y1, hp_x2, hp_y2 = sectors["enclave_harp"]
    t_harp_saved = tm.add_trigger(
        name="P1_EnclaveC_Harp_Liberated",
        enabled=True,
        looping=False,
    )
    safe_call(
        t_harp_saved.new_condition.objects_in_area,
        source_player=PlayerId.THREE,
        area_x1=hp_x1,
        area_y1=hp_y1,
        area_x2=hp_x2,
        area_y2=hp_y2 + 6,
        quantity=1,
    )
    safe_call(
        t_harp_saved.new_effect.remove_object,
        selected_object_ids=rocks["salgant_gate_rocks"],
    )
    for i in range(6):
        safe_call(
            t_harp_saved.new_effect.create_object,
            source_player=PlayerId.THREE,
            object_list_unit_id=UNIT_FLOWER_CAV_ID,
            location_x=90 + (i % 3),
            location_y=28 + (i // 3),
        )
    apply_unit_lore_name(t_harp_saved, PlayerId.THREE, UNIT_FLOWER_CAV_ID)
    award_glory_gold(
        t_harp_saved,
        BALANCE["glory_scores"]["side_quest_completed"],
        "<GREEN>[Enklawa C - Dom Harfy!] Wojownicy Domu Harfy wypowiedzieli posluszenstwo tchorzliwemu Salgantowi! Jazda i Uzdrowiciele dolaczaja do P3 (+300 Chwaly)!",
    )

    return phase1_ui_triggers


def _setup_phase2_gothmog_and_tumladen(
    tm: Any,
    ctx: dict[str, Any],
    phase1_ui_triggers: list[Any],
) -> list[Any]:
    """Configure Gothmog boss fight on Amon Gwareth and the Phase II Dual Route across Tumladen."""
    sectors = ctx["sectors"]
    rocks = ctx["destructible_rocks"]
    q_bldgs = ctx["quest_buildings"]
    bldg_offsets = ctx.get("player_bldg_counts", {})

    t_spawn_gothmog = tm.add_trigger(
        name="P1_Boss_Spawn_Gothmog_AmonGwareth",
        enabled=True,
        looping=False,
    )
    safe_call(
        t_spawn_gothmog.new_condition.destroy_object,
        unit_object=q_bldgs["caragdur_keep"]["ref_id"],
    )
    safe_call(
        t_spawn_gothmog.new_condition.destroy_object,
        unit_object=q_bldgs["aqueduct_control"]["ref_id"],
    )
    safe_call(
        t_spawn_gothmog.new_effect.create_object,
        source_player=PlayerId.SEVEN,
        object_list_unit_id=ENEMY_GOTHMOG_ID,
        location_x=61,
        location_y=82,
    )
    safe_call(
        t_spawn_gothmog.new_effect.create_object,
        source_player=PlayerId.SEVEN,
        object_list_unit_id=ENEMY_BALROG_BOSS_ID,
        location_x=58,
        location_y=82,
    )
    for i in range(10):
        safe_call(
            t_spawn_gothmog.new_effect.create_object,
            source_player=PlayerId.FIVE,
            object_list_unit_id=ENEMY_ORC_BRUTE_ID,
            location_x=57 + (i % 5) * 2,
            location_y=84 + (i // 5),
        )
    apply_unit_lore_name(t_spawn_gothmog, PlayerId.SEVEN, ENEMY_GOTHMOG_ID)
    apply_unit_lore_name(t_spawn_gothmog, PlayerId.SEVEN, ENEMY_BALROG_BOSS_ID)
    apply_unit_lore_name(t_spawn_gothmog, PlayerId.FIVE, ENEMY_ORC_BRUTE_ID)
    safe_call(
        t_spawn_gothmog.new_effect.attack_move,
        source_player=PlayerId.SEVEN,
        area_x1=54,
        area_y1=78,
        area_x2=68,
        area_y2=88,
        location_x=61,
        location_y=60,
    )
    safe_call(
        t_spawn_gothmog.new_effect.attack_move,
        source_player=PlayerId.FIVE,
        area_x1=54,
        area_y1=78,
        area_x2=68,
        area_y2=88,
        location_x=61,
        location_y=60,
    )
    add_chat_and_flare(
        t_spawn_gothmog,
        "<RED>[BOSS: GOTHMOG, WLADCA BALROGOW!] Gothmog (P7) wkracza na wzgorze Amon Gwareth! Zwabcie go w wode Fontanny Krolewskiej (61, 60), gdzie traci pancerz i otrzymuje obrazenia!",
        61,
        80,
    )

    p2_softcap_trigs = grant_soft_cap_reinforcements(
        tm,
        "Faza_II",
        ctx["checkpoints"]["phase2"],
        bldg_offsets=bldg_offsets,
    )

    phase2_ui_triggers: list[Any] = []

    def add_p2_objective(name: str, text: str, order: int) -> Any:
        trig = tm.add_trigger(name=name, enabled=False, looping=False)
        trig.short_description = text
        trig.display_on_screen = 1
        trig.description_order = order
        phase2_ui_triggers.append(trig)
        return trig

    add_p2_objective(
        "UI_P2_Main",
        "[FAZA II - ODWROT] Przebijcie sie przez Rownine Tumladen do wejscia w wawoz Orfalch Echor (185, 85)",
        110,
    )
    ui_p2_dilemma = add_p2_objective(
        "UI_P2_Dilemma_Routes",
        "[WYBOR DROGI (Mozna isc razem lub 2+2)] DOL: Tunel Idril i Suche Koryto (Podkopy P4) | GORA: Rownina (Klify i Oltarz P7)",
        109,
    )
    ui_p2_lower = add_p2_objective(
        "UI_P2_Q_LowerMines",
        "[SZLAK DOLNY - P4] Podkopy w Korycie Rzeki: Wysadz komory pod obozami wilkow, by pomoc idacym gora",
        105,
    )
    ui_p2_upper = add_p2_objective(
        "UI_P2_Q_UpperCliffs",
        "[SZLAK GORNY - P2/P3] Skarpy nad Rzeka: Zniszcz 2 wieze lucznikow Orkow strzelajace w Koryto Rzeki",
        104,
    )
    ui_p2_rog = add_p2_objective(
        "UI_P2_Q_RogAltar",
        "[INDYWIDUALNY P1 - Rog] Ostatnia Szarza Domu Mlota: Zburz Polowy Oltarz Balrogow na polnocy Tumladen",
        102,
    )

    # Defeating Gothmog (quantity=0 alive) transitions from Phase I to Phase II
    t_gothmog_slain = tm.add_trigger(
        name="P1_Boss_Gothmog_Slain_Start_Phase2",
        enabled=False,
        looping=False,
    )
    safe_call(
        t_spawn_gothmog.new_effect.activate_trigger,
        trigger_id=t_gothmog_slain.trigger_id,
    )
    safe_call(
        t_gothmog_slain.new_condition.own_fewer_objects,
        source_player=PlayerId.SEVEN,
        object_list=ENEMY_GOTHMOG_ID,
        quantity=0,
    )
    for old_ui in phase1_ui_triggers:
        safe_call(
            t_gothmog_slain.new_effect.deactivate_trigger,
            trigger_id=old_ui.trigger_id,
        )
    for new_ui in phase2_ui_triggers:
        safe_call(
            t_gothmog_slain.new_effect.activate_trigger,
            trigger_id=new_ui.trigger_id,
        )
    for sc_trig in p2_softcap_trigs:
        safe_call(
            t_gothmog_slain.new_effect.activate_trigger,
            trigger_id=sc_trig.trigger_id,
        )

    safe_call(
        t_gothmog_slain.new_effect.remove_object,
        selected_object_ids=rocks["tumladen_exit_rocks"],
    )
    safe_call(
        t_gothmog_slain.new_effect.kill_object,
        selected_object_ids=[q_bldgs["tower_of_turgon"]["ref_id"]],
    )
    # Spawn revealers at safe coordinates outside trigger detection zones (owned by P2)
    for rx, ry in [(95, 42), (95, 86), (116, 40), (116, 88), (174, 85)]:
        spawn_progressive_revealer(t_gothmog_slain, rx, ry, player=PlayerId.TWO)

    award_glory_gold(
        t_gothmog_slain,
        500,
        "<AQUA>[Upadek Gothmoga i Ostatni Rozkaz Turgona!] Ecthelion powalil Wladce Balrogow w wodach Fontanny! Wieza Turgona runela, blokujac poscig. Tajemna Sciezka Idril (Dol) oraz Furta na Tumladen (Gora) sa otwarte (+500 Chwaly)!",
    )

    # Dismiss the persistent Phase II Dilemma banner only AFTER a squad (>= 3 units) commits to a route
    for route_name, r_sec in [("Lower", sectors["lower_mine_1"]), ("Upper", sectors["upper_cliff_1"])]:
        rx1, ry1, rx2, ry2 = r_sec
        t_hide_dilemma = tm.add_trigger(
            name=f"P2_Hide_Dilemma_On_{route_name}",
            enabled=True,
            looping=False,
        )
        safe_call(
            t_hide_dilemma.new_condition.objects_in_area,
            source_player=PlayerId.ONE,
            area_x1=rx1 - 10,
            area_y1=ry1 - 10,
            area_x2=rx2 + 10,
            area_y2=ry2 + 10,
            quantity=3,
        )
        safe_call(
            t_hide_dilemma.new_effect.deactivate_trigger,
            trigger_id=ui_p2_dilemma.trigger_id,
        )

    # Lower Route Co-op Mechanics: Collapsing Tunnel & Detonating Under-Mines
    tun_x1, tun_y1, tun_x2, tun_y2 = sectors["idril_tunnel_entrance"]
    t_collapse_tunnel = tm.add_trigger(
        name="P2_Idril_Collapses_Tunnel_Behind",
        enabled=True,
        looping=False,
    )
    safe_call(
        t_collapse_tunnel.new_condition.objects_in_area,
        source_player=PlayerId.FOUR,
        area_x1=tun_x1 + 12,
        area_y1=tun_y1 - 12,
        area_x2=tun_x2 + 25,
        area_y2=tun_y2,
        quantity=1,
    )
    for cy_rock in range(50, 55):
        safe_call(
            t_collapse_tunnel.new_effect.create_object,
            source_player=PlayerId.GAIA,
            object_list_unit_id=ROCK_CLIFF_ID,
            location_x=78,
            location_y=cy_rock,
        )
    add_chat_and_flare(
        t_collapse_tunnel,
        "<YELLOW>[Saperzy Idril - P4] Tunel za plecami kolumny zostal zawalony skalami! Poscig z plonacego miasta odciety!",
        78,
        52,
    )

    for idx, (m_sec_key, camp_key) in enumerate(
        [("lower_mine_1", "wolf_camp_1"), ("lower_mine_2", "wolf_camp_2")],
        start=1,
    ):
        mx1, my1, mx2, my2 = sectors[m_sec_key]
        t_mine = tm.add_trigger(
            name=f"P2_LowerRoute_Detonate_Mine_{idx}",
            enabled=True,
            looping=False,
        )
        safe_call(
            t_mine.new_condition.objects_in_area,
            source_player=PlayerId.FOUR,
            area_x1=mx1,
            area_y1=my1,
            area_x2=mx2,
            area_y2=my2,
            quantity=1,
        )
        safe_call(
            t_mine.new_effect.kill_object,
            selected_object_ids=[q_bldgs[camp_key]["ref_id"]],
        )
        safe_call(
            t_mine.new_effect.damage_object,
            source_player=PlayerId.FIVE,
            area_x1=q_bldgs[camp_key]["x"] - 8,
            area_y1=q_bldgs[camp_key]["y"] - 8,
            area_x2=q_bldgs[camp_key]["x"] + 8,
            area_y2=q_bldgs[camp_key]["y"] + 8,
            quantity=500,
        )
        if idx == 2:
            safe_call(
                t_mine.new_effect.deactivate_trigger,
                trigger_id=ui_p2_lower.trigger_id,
            )
        award_glory_gold(
            t_mine,
            200,
            f"<YELLOW>[Podkop Saperski #{idx} - P4!] Ladunki w Korycie Rzeki eksplodowaly pod Obozem Wilkow #{idx} na powierzchni Tumladen (+200 Chwaly)!",
        )

    # Upper Route Co-op Mechanics: Clearing Cliff Overlooks & Rog's Balrog Altar
    create_escalating_encounter(
        tm,
        "Tumladen_Wolves_1",
        (120, 78, 142, 98),
        (128, 88),
        [(PlayerId.FIVE, ENEMY_DIRE_WOLF_ID, 10, 134, 88), (PlayerId.FIVE, ENEMY_WARG_RIDER_ID, 6, 136, 90)],
        [(PlayerId.FIVE, ENEMY_WARG_RIDER_ID, 6, 140, 92)],
    )

    t_cliffs_cleared = tm.add_trigger(
        name="P2_UpperRoute_Cliffs_Cleared",
        enabled=True,
        looping=False,
    )
    safe_call(
        t_cliffs_cleared.new_condition.destroy_object,
        unit_object=q_bldgs["cliff_tower_1"]["ref_id"],
    )
    safe_call(
        t_cliffs_cleared.new_condition.destroy_object,
        unit_object=q_bldgs["cliff_tower_2"]["ref_id"],
    )
    safe_call(
        t_cliffs_cleared.new_effect.deactivate_trigger,
        trigger_id=ui_p2_upper.trigger_id,
    )
    award_glory_gold(
        t_cliffs_cleared,
        BALANCE["glory_scores"]["side_quest_completed"],
        "<GREEN>[Skarpy Oczyszczone!] Obie wieze strzeleckie Orkow nad Korytem Rzeki zniszczone! Dolny szlak jest bezpieczny (+300 Chwaly)!",
    )

    ra_x1, ra_y1, ra_x2, ra_y2 = sectors["rog_altar_zone"]
    create_escalating_encounter(
        tm,
        "Balrog_Altar_Tumladen",
        (ra_x1 - 6, ra_y1 - 6, ra_x2 + 6, ra_y2 + 6),
        (145, 110),
        [(PlayerId.SEVEN, ENEMY_BALROG_BOSS_ID, 1, 145, 114), (PlayerId.FIVE, ENEMY_ORC_BRUTE_ID, 8, 145, 108)],
        [(PlayerId.SEVEN, ENEMY_BALROG_BOSS_ID, 1, 148, 114)],
    )
    t_altar_destroyed = tm.add_trigger(
        name="P2_Quest_RogAltar_Completed",
        enabled=True,
        looping=False,
    )
    safe_call(
        t_altar_destroyed.new_condition.destroy_object,
        unit_object=q_bldgs["balrog_altar"]["ref_id"],
    )
    safe_call(
        t_altar_destroyed.new_effect.deactivate_trigger,
        trigger_id=ui_p2_rog.trigger_id,
    )
    safe_call(
        t_altar_destroyed.new_effect.modify_attribute,
        source_player=PlayerId.SEVEN,
        object_list_unit_id=ENEMY_BALROG_BOSS_ID,
        object_attributes=ATTR_HIT_POINTS,
        operation=Operation.MULTIPLY,
        quantity=0.80,
    )
    award_glory_gold(
        t_altar_destroyed,
        400,
        "<BLUE>[Ostatnia Szarza Roga - P1!] Kowale Domu Mlota rozbili Polowy Oltarz Balrogow na Tumladen! Demony P7 na przeleczy traca 20% HP (+400 Chwaly)!",
    )

    return phase2_ui_triggers


def _setup_phase3_orfalch_and_cirith_victory(
    tm: Any,
    ctx: dict[str, Any],
    phase2_ui_triggers: list[Any],
    seal_info: dict[str, Any],
) -> None:
    """Configure Phase III: Seven Gates of Orfalch Echor, Glorfindel's Duel, Thorondor's Eagles, and Victory."""
    sectors = ctx["sectors"]
    rocks = ctx["destructible_rocks"]
    q_bldgs = ctx["quest_buildings"]
    bldg_offsets = ctx.get("player_bldg_counts", {})

    p3_softcap_trigs = grant_soft_cap_reinforcements(
        tm,
        "Faza_III",
        ctx["checkpoints"]["phase3"],
        bldg_offsets=bldg_offsets,
    )

    phase3_ui_triggers: list[Any] = []

    def add_p3_objective(name: str, text: str, order: int) -> Any:
        trig = tm.add_trigger(name=name, enabled=False, looping=False)
        trig.short_description = text
        trig.display_on_screen = 1
        trig.description_order = order
        phase3_ui_triggers.append(trig)
        return trig

    add_p3_objective(
        "UI_P3_Main",
        "[FAZA III - CRISTHORN] Przebijcie sie przez Siedem Bram i ocalcie Tuora, Idril i Earendila w Dolinie Sirionu",
        110,
    )
    ui_p3_winches = add_p3_objective(
        "UI_P3_Q_Winches",
        "[CO-OP GORA/DOL] Gorna Gran (P3/P4): Zniszcz Kolowroty Bram (3, 5, 7), by zrzucic lawiny na Orkow w dole",
        106,
    )
    ui_p3_duel = add_p3_objective(
        "UI_P3_Q_GlorfindelDuel",
        "[FINAL - P3 Glorfindel] Cirith Thoronath (198, 198): Zwiaz Balroga walka na Skalnym Wystepie!",
        104,
    )

    og_x1, og_y1, og_x2, og_y2 = sectors["orfalch_gathering"]
    t_start_p3 = tm.add_trigger(
        name="P3_Start_Orfalch_Echor",
        enabled=True,
        looping=False,
    )
    # Require >= 4 P1 units in Orfalch Gathering so no stray Revealer can prematurely start Phase III
    safe_call(
        t_start_p3.new_condition.objects_in_area,
        source_player=PlayerId.ONE,
        area_x1=og_x1,
        area_y1=og_y1,
        area_x2=og_x2,
        area_y2=og_y2,
        quantity=4,
    )
    for old_ui in phase2_ui_triggers:
        safe_call(
            t_start_p3.new_effect.deactivate_trigger,
            trigger_id=old_ui.trigger_id,
        )
    for new_ui in phase3_ui_triggers:
        safe_call(
            t_start_p3.new_effect.activate_trigger,
            trigger_id=new_ui.trigger_id,
        )
    for sc_trig in p3_softcap_trigs:
        safe_call(
            t_start_p3.new_effect.activate_trigger,
            trigger_id=sc_trig.trigger_id,
        )

    for g_auto in ("orfalch_gate_1", "orfalch_gate_2", "orfalch_gate_4", "orfalch_gate_6"):
        safe_call(
            t_start_p3.new_effect.remove_object,
            selected_object_ids=rocks[g_auto],
        )
    # Place revealers owned by P3 outside the Sirion victory box (218..232, 216..230)
    for rx, ry in [(190, 114), (204, 144), (180, 172), (198, 198), (214, 214)]:
        spawn_progressive_revealer(t_start_p3, rx, ry, player=PlayerId.THREE)

    add_chat_and_flare(
        t_start_p3,
        "<AQUA>[Faza III: Wawoz Siedmiu Bram - Orfalch Echor!] Glowna kolumna wkracza w gory! P3 i P4 moga wejsc boczna sciezka na Gorna Gran (lewa strona wawozu), by otworzyc Bramy 3, 5 i 7 oraz zrzucic lawiny na Orkow!",
        190,
        96,
    )

    winch_configs: list[tuple[str, str, int, int, str]] = [
        ("winch_bronze", "orfalch_gate_3", 206, 122, "Trzecia Brama (Brazowa)"),
        ("winch_silver", "orfalch_gate_5", 202, 150, "Piata Brama (Srebrna)"),
        ("winch_steel", "orfalch_gate_7", 190, 174, "Siodma Brama (Stalowa)"),
    ]
    for w_key, g_key, gx, gy, g_label in winch_configs:
        create_escalating_encounter(
            tm,
            f"Orfalch_{g_key}",
            (gx - 8, gy - 8, gx + 8, gy + 8),
            (gx, gy),
            [(PlayerId.FIVE, ENEMY_ORC_BRUTE_ID, 7, gx, gy + 3), (PlayerId.FIVE, ENEMY_ORC_CROSSBOW_ID, 5, gx, gy + 5)],
            [(PlayerId.SEVEN, ENEMY_BALROG_BOSS_ID, 1, gx, gy + 6)],
        )
        t_winch = tm.add_trigger(
            name=f"P3_Winch_{w_key}_Destroyed",
            enabled=True,
            looping=False,
        )
        safe_call(
            t_winch.new_condition.destroy_object,
            unit_object=q_bldgs[w_key]["ref_id"],
        )
        safe_call(
            t_winch.new_effect.remove_object,
            selected_object_ids=rocks[g_key],
        )
        safe_call(
            t_winch.new_effect.damage_object,
            source_player=PlayerId.FIVE,
            area_x1=gx - 7,
            area_y1=gy - 7,
            area_x2=gx + 7,
            area_y2=gy + 7,
            quantity=600,
        )
        if w_key == "winch_steel":
            safe_call(
                t_winch.new_effect.deactivate_trigger,
                trigger_id=ui_p3_winches.trigger_id,
            )
        award_glory_gold(
            t_winch,
            200,
            f"<GREEN>[Lawina w Orfalch Echor!] Kolowrot na grani zniszczony! {g_label} otwarta, a kamienna lawina zmiazdzyla Orkow w dole wawozu (+200 Chwaly)!",
        )

    # FINALE AT CIRITH THORONATH: GLORFINDEL'S DUEL & THORONDOR'S EAGLES
    ct_x1, ct_y1, ct_x2, ct_y2 = sectors["cirith_thoronath"]
    dl_x1, dl_y1, dl_x2, dl_y2 = sectors["glorfindel_duel_ledge"]

    t_ambush_cirith = tm.add_trigger(
        name="P3_Finale_Cirith_Thoronath_Ambush",
        enabled=True,
        looping=False,
    )
    safe_call(
        t_ambush_cirith.new_condition.objects_in_area,
        source_player=PlayerId.THREE,
        area_x1=ct_x1 - 4,
        area_y1=ct_y1 - 4,
        area_x2=ct_x2,
        area_y2=ct_y2,
        quantity=1,
    )
    # Deactivate Glorfindel's Seal penalty triggers during his canonical duel on Cirith Thoronath
    for gl_seal_trig in seal_info["glorfindel_stage_triggers"]:
        safe_call(
            t_ambush_cirith.new_effect.deactivate_trigger,
            trigger_id=gl_seal_trig.trigger_id,
        )

    safe_call(
        t_ambush_cirith.new_effect.create_object,
        source_player=PlayerId.SEVEN,
        object_list_unit_id=ENEMY_BALROG_BOSS_ID,
        location_x=198,
        location_y=198,
    )
    for i in range(12):
        safe_call(
            t_ambush_cirith.new_effect.create_object,
            source_player=PlayerId.FIVE,
            object_list_unit_id=ENEMY_ORC_BRUTE_ID if i % 2 == 0 else ENEMY_ORC_INFANTRY_ID,
            location_x=190 + (i % 3),
            location_y=190 + (i // 3) * 3,
        )
    apply_unit_lore_name(t_ambush_cirith, PlayerId.SEVEN, ENEMY_BALROG_BOSS_ID)
    apply_unit_lore_name(t_ambush_cirith, PlayerId.FIVE, ENEMY_ORC_BRUTE_ID)
    apply_unit_lore_name(t_ambush_cirith, PlayerId.FIVE, ENEMY_ORC_INFANTRY_ID)
    add_chat_and_flare(
        t_ambush_cirith,
        "<RED>[CIRITH THORONATH - ZASADZKA NAD PRZEPASCIA!] Balrog zagrodzil waska polke skalna! Glorfindel (P3) musi wejsc na Skalny Wystep (198, 198) i zwiazac demona walka!",
        198,
        198,
    )

    # Require Glorfindel (or P3 force) to actually step onto the Duel Spur (192..204, 193..203) to engage the Balrog
    t_duel_engaged = tm.add_trigger(
        name="P3_Finale_Glorfindel_Engages_Balrog",
        enabled=False,
        looping=False,
    )
    safe_call(
        t_ambush_cirith.new_effect.activate_trigger,
        trigger_id=t_duel_engaged.trigger_id,
    )
    safe_call(
        t_duel_engaged.new_condition.objects_in_area,
        source_player=PlayerId.THREE,
        area_x1=dl_x1 - 2,
        area_y1=dl_y1 - 2,
        area_x2=dl_x2 + 2,
        area_y2=dl_y2 + 2,
        quantity=1,
    )
    add_chat_and_flare(
        t_duel_engaged,
        "<YELLOW>[Pojedynek na Cirith Thoronath!] Glorfindel starl sie z Balrogiem nad odchłania! Utrzymajcie przelecz przez 25 sekund do przylotu Orlow Thorondora!",
        198,
        198,
    )

    t_thorondor = tm.add_trigger(
        name="P3_Finale_Thorondor_Eagles_Arrive",
        enabled=False,
        looping=False,
    )
    safe_call(
        t_duel_engaged.new_effect.activate_trigger,
        trigger_id=t_thorondor.trigger_id,
    )
    safe_call(
        t_thorondor.new_condition.timer,
        timer=25,
    )

    for ey in range(182, 222, 5):
        safe_call(
            t_thorondor.new_effect.create_object,
            source_player=PlayerId.ONE,
            object_list_unit_id=VULTURE_ID,
            location_x=192,
            location_y=ey,
        )
        safe_call(
            t_thorondor.new_effect.create_object,
            source_player=PlayerId.THREE,
            object_list_unit_id=FALCON_ID,
            location_x=196,
            location_y=ey + 2,
        )

    safe_call(
        t_thorondor.new_effect.kill_object,
        source_player=PlayerId.SEVEN,
        area_x1=ct_x1 - 4,
        area_y1=ct_y1 - 4,
        area_x2=dl_x2 + 4,
        area_y2=ct_y2 + 4,
    )
    safe_call(
        t_thorondor.new_effect.kill_object,
        source_player=PlayerId.FIVE,
        area_x1=ct_x1 - 4,
        area_y1=ct_y1 - 4,
        area_x2=dl_x2 + 4,
        area_y2=ct_y2 + 4,
    )

    for p_id in HUMAN_PLAYERS:
        for i in range(4):
            safe_call(
                t_thorondor.new_effect.create_object,
                source_player=p_id,
                object_list_unit_id=UNIT_EAGLE_VANGUARD_ID,
                location_x=190 + i,
                location_y=214,
            )
        apply_unit_lore_name(t_thorondor, p_id, UNIT_EAGLE_VANGUARD_ID)

    safe_call(
        t_thorondor.new_effect.remove_object,
        selected_object_ids=rocks["cirith_exit_rocks"],
    )
    safe_call(
        t_thorondor.new_effect.deactivate_trigger,
        trigger_id=ui_p3_duel.trigger_id,
    )
    award_glory_gold(
        t_thorondor,
        600,
        "<AQUA>[ORLY THORONDORA!] Z szczytow Krisakael nadlecial Thorondor, Krol Orlow! Balrog stracony w przepasc Cirith Thoronath, a przelecz ku dolinie Sirionu stoi otworem (+600 Chwaly)!",
    )

    # FINAL VICTORY AT THE VALE OF SIRION EXIT (218, 216, 232, 230)
    # Requires Tuor (P1), Idril (P4), and Earendil (P4) to reach the Sirion exit alive!
    sx1, sy1, sx2, sy2 = sectors["sirion_exit"]
    t_victory = tm.add_trigger(
        name="Victory_Reached_Vale_Of_Sirion",
        enabled=False,
        looping=False,
    )
    safe_call(
        t_thorondor.new_effect.activate_trigger,
        trigger_id=t_victory.trigger_id,
    )
    safe_call(
        t_victory.new_condition.objects_in_area,
        source_player=PlayerId.ONE,
        object_list=HERO_TUOR_ID,
        area_x1=sx1,
        area_y1=sy1,
        area_x2=sx2,
        area_y2=sy2,
        quantity=1,
    )
    safe_call(
        t_victory.new_condition.objects_in_area,
        source_player=PlayerId.FOUR,
        object_list=HERO_IDRIL_ID,
        area_x1=sx1,
        area_y1=sy1,
        area_x2=sx2,
        area_y2=sy2,
        quantity=1,
    )
    safe_call(
        t_victory.new_condition.objects_in_area,
        source_player=PlayerId.FOUR,
        object_list=HERO_EARENDIL_ID,
        area_x1=sx1,
        area_y1=sy1,
        area_x2=sx2,
        area_y2=sy2,
        quantity=1,
    )
    award_glory_gold(
        t_victory,
        3 * BALANCE["glory_scores"]["seal_preserved_bonus"],
        "<GREEN>[ZWYCIESTWO - OCALENIE NOLDOROW!] Tuor, Idril i maly Earendil bezpiecznie dotarli do Doliny Sirionu! Sprawdzcie koncowa liczbe Zlota Gracza 1 jako Wasz Wynik Chwaly!",
    )
    for p_id in HUMAN_PLAYERS:
        safe_call(
            t_victory.new_effect.declare_victory,
            source_player=p_id,
            enabled=True,
        )


def setup_sanctuary_quests_and_victory(scenario: Any, ctx: dict[str, Any]) -> None:
    """Entry point to wire the Balance Sanctuary, 3 Seals of Turgon, Quests, Dilemmas, and Victory."""
    tm = scenario.trigger_manager
    _setup_balance_sanctuary(tm, ctx)
    seal_info = _setup_three_seals_of_turgon(tm, ctx)
    _setup_refugee_rescues(tm, ctx)
    p1_ui = _setup_phase1_city_and_dilemmas(tm, ctx)
    p2_ui = _setup_phase2_gothmog_and_tumladen(tm, ctx, p1_ui)
    _setup_phase3_orfalch_and_cirith_victory(tm, ctx, p2_ui, seal_info)
