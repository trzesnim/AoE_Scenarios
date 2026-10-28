from AoE2ScenarioParser.datasets.buildings import BuildingInfo
from AoE2ScenarioParser.datasets.players import PlayerId
from AoE2ScenarioParser.datasets.trigger_lists import Operation
from AoE2ScenarioParser.datasets.units import UnitInfo

from horde_config import (
    ATTR_ARMOR,
    ATTR_ATTACK,
    ATTR_HIT_POINTS,
    ATTR_MAXIMUM_RANGE,
    ATTR_MOVEMENT_SPEED,
    ATTR_SEARCH_RADIUS,
    ATTR_WORK_RATE,
    BALANCE,
    ELITE_BATTLE_ELEPHANT_ID,
    HUSSAR_ID,
    IMAM_UNIT_ID,
    MAP_SIZE,
    RES_BONUS_POP_CAP,
    RES_FOOD,
    RES_GOLD,
    RES_STONE,
    RES_WOOD,
    TECH_BALLISTICS,
    TECH_CHEMISTRY,
    TECH_SIEGE_ENGINEERS,
    TECH_THUMB_RING,
)
from horde_waves import (
    add_enemy_combat_buff,
    add_player_resource,
    add_spawn_and_attack_effect,
    research_techs,
    safe_call,
    safe_modify_attribute,
    send_highlight_chat,
    set_as_objective,
)


def setup_sanctuary_quests_and_victory(scenario, ctx: dict) -> None:
    ai_p = ctx["ai_p"]
    ai_players = ctx["ai_players"]
    all_settlement_wave_triggers = ctx["all_settlement_wave_triggers"]
    allied_citadel = ctx["allied_citadel"]
    deep_target_center = ctx["deep_target_center"]
    enemy_melee_units = ctx["enemy_melee_units"]
    enemy_ranged_units = ctx["enemy_ranged_units"]
    h_p = ctx["h_p"]
    human_players = ctx["human_players"]
    p_coords = ctx["p_coords"]
    q1_bldg = ctx["q1_bldg"]
    q2_bldg = ctx["q2_bldg"]
    q2_pos = ctx["q2_pos"]
    q3_bldg = ctx["q3_bldg"]
    q3_pos = ctx["q3_pos"]
    q4_bldg = ctx["q4_bldg"]
    q4_pos = ctx["q4_pos"]
    s_coords = ctx["s_coords"]
    s_g1_east = ctx["s_g1_east"]
    s_g1_north = ctx["s_g1_north"]
    s_g2_mages = ctx["s_g2_mages"]
    s_g2_snipers = ctx["s_g2_snipers"]
    s_g3_east = ctx["s_g3_east"]
    s_g3_north = ctx["s_g3_north"]
    s_key = ctx["s_key"]
    sanctuary_cx = ctx["sanctuary_cx"]
    sanctuary_cy = ctx["sanctuary_cy"]
    sx = ctx["sx"]
    sy = ctx["sy"]
    tier_0_wave_triggers = ctx["tier_0_wave_triggers"]
    tier_m1_wave_triggers = ctx["tier_m1_wave_triggers"]
    tier_p1_wave_triggers = ctx["tier_p1_wave_triggers"]
    tier_p2_wave_triggers = ctx["tier_p2_wave_triggers"]
    tm = ctx["tm"]
    u_id = ctx["u_id"]
    wx = ctx["wx"]

    pad_up_box = (sanctuary_cx - 2, sanctuary_cy - 4, sanctuary_cx + 2, sanctuary_cy - 3)
    pad_down_box = (sanctuary_cx - 2, sanctuary_cy + 3, sanctuary_cx + 2, sanctuary_cy + 4)
    full_chamber_box = (sanctuary_cx - 2, sanctuary_cy - 4, sanctuary_cx + 2, sanctuary_cy + 4)

    def apply_king_reset_and_safe_stat_shift(trig, mode: str):
        cx1, cy1, cx2, cy2 = full_chamber_box
        safe_call(
            trig.new_effect.remove_object,
            source_player=PlayerId.ONE,
            object_list_unit_id=UnitInfo.KING.ID,
            area_x1=cx1, area_y1=cy1, area_x2=cx2, area_y2=cy2,
        )
        safe_call(
            trig.new_effect.create_object,
            object_list_unit_id=UnitInfo.KING.ID,
            source_player=PlayerId.ONE,
            location_x=sanctuary_cx,
            location_y=sanctuary_cy,
        )

        if mode in ("pos_up", "pos_down"):
            op = Operation.ADD if mode == "pos_up" else Operation.SUBTRACT
            hp_val = BALANCE["diff_step_up_hp"]
            atk_val = BALANCE["diff_step_up_atk"]
            for ai_p in ai_players:
                for m_id in enemy_melee_units:
                    safe_modify_attribute(trig, ai_p, m_id, ATTR_HIT_POINTS, op, hp_val)
                    safe_modify_attribute(trig, ai_p, m_id, ATTR_ATTACK, op, atk_val, armor_class=4)
                for r_id in enemy_ranged_units:
                    safe_modify_attribute(trig, ai_p, r_id, ATTR_HIT_POINTS, op, hp_val)
                    safe_modify_attribute(trig, ai_p, r_id, ATTR_ATTACK, op, atk_val, armor_class=3)
        else:
            mult_val = 0.85 if mode == "neg_down" else 1.18
            for ai_p in ai_players:
                for u_id in enemy_melee_units + enemy_ranged_units:
                    safe_modify_attribute(trig, ai_p, u_id, ATTR_HIT_POINTS, Operation.MULTIPLY, mult_val)

    t_up_0_to_p1 = tm.add_trigger("09_Diff_Up_0_to_P1", enabled=True, looping=False)
    t_down_0_to_m1 = tm.add_trigger("09_Diff_Down_0_to_M1", enabled=True, looping=False)

    t_up_p1_to_p2 = tm.add_trigger("09_Diff_Up_P1_to_P2", enabled=False, looping=False)
    t_down_p1_to_0 = tm.add_trigger("09_Diff_Down_P1_to_0", enabled=False, looping=False)
    t_down_p2_to_p1 = tm.add_trigger("09_Diff_Down_P2_to_P1", enabled=False, looping=False)

    t_up_m1_to_0 = tm.add_trigger("09_Diff_Up_M1_to_0", enabled=False, looping=False)
    t_down_m1_to_m2 = tm.add_trigger("09_Diff_Down_M1_to_M2", enabled=False, looping=False)
    t_up_m2_to_m1 = tm.add_trigger("09_Diff_Up_M2_to_M1", enabled=False, looping=False)

    def wire_difficulty_transition(
        trig,
        is_up: bool,
        stat_mode: str,
        to_disable: list,
        to_enable_after_2s: list,
        waves_to_enable: list,
        waves_to_disable: list,
        log_msg: str,
    ):
        bx1, by1, bx2, by2 = pad_up_box if is_up else pad_down_box
        safe_call(
            trig.new_condition.objects_in_area,
            source_player=PlayerId.ONE,
            object_list=UnitInfo.KING.ID,
            object_list_unit_id=UnitInfo.KING.ID,
            area_x1=bx1, area_y1=by1, area_x2=bx2, area_y2=by2,
            quantity=1,
        )
        for d_tr in to_disable:
            safe_call(trig.new_effect.deactivate_trigger, trigger_id=d_tr.trigger_id)
        for w_en in waves_to_enable:
            safe_call(trig.new_effect.activate_trigger, trigger_id=w_en.trigger_id)
        for w_dis in waves_to_disable:
            safe_call(trig.new_effect.deactivate_trigger, trigger_id=w_dis.trigger_id)

        apply_king_reset_and_safe_stat_shift(trig, mode=stat_mode)
        send_highlight_chat(trig, "<RED>" if is_up else "<AQUA>", log_msg, flare_x=sanctuary_cx, flare_y=sanctuary_cy)

        t_relay = tm.add_trigger(f"{trig.name}_Relay2s", enabled=False, looping=False)
        safe_call(t_relay.new_condition.timer, timer=2)
        for e_tr in to_enable_after_2s:
            safe_call(t_relay.new_effect.activate_trigger, trigger_id=e_tr.trigger_id)
        safe_call(t_relay.new_effect.deactivate_trigger, trigger_id=t_relay.trigger_id)
        safe_call(trig.new_effect.activate_trigger, trigger_id=t_relay.trigger_id)

    wire_difficulty_transition(
        t_up_0_to_p1, is_up=True, stat_mode="pos_up",
        to_disable=[t_up_0_to_p1, t_down_0_to_m1],
        to_enable_after_2s=[t_up_p1_to_p2, t_down_p1_to_0],
        waves_to_enable=tier_p1_wave_triggers, waves_to_disable=[],
        log_msg="[LOG BALANSU]: Trudnosc ZWIEKSZONA do POZIOMU +1 (TRUDNY: +25% wielkosci fal, +15 HP, +2 Ataku)!",
    )
    wire_difficulty_transition(
        t_up_p1_to_p2, is_up=True, stat_mode="pos_up",
        to_disable=[t_up_p1_to_p2, t_down_p1_to_0],
        to_enable_after_2s=[t_down_p2_to_p1],
        waves_to_enable=tier_p2_wave_triggers, waves_to_disable=[],
        log_msg="[LOG BALANSU]: Trudnosc ZWIEKSZONA do POZIOMU +2 (EKSTREMALNY: +50% wielkosci fal, +30 HP, +4 Ataku)!",
    )
    wire_difficulty_transition(
        t_down_p2_to_p1, is_up=False, stat_mode="pos_down",
        to_disable=[t_down_p2_to_p1],
        to_enable_after_2s=[t_up_p1_to_p2, t_down_p1_to_0],
        waves_to_enable=[], waves_to_disable=tier_p2_wave_triggers,
        log_msg="[LOG BALANSU]: Trudnosc ZMNIEJSZONA z +2 do POZIOMU +1 (TRUDNY: +25% wielkosci fal)!",
    )
    wire_difficulty_transition(
        t_down_p1_to_0, is_up=False, stat_mode="pos_down",
        to_disable=[t_up_p1_to_p2, t_down_p1_to_0],
        to_enable_after_2s=[t_up_0_to_p1, t_down_0_to_m1],
        waves_to_enable=[], waves_to_disable=tier_p1_wave_triggers,
        log_msg="[LOG BALANSU]: Trudnosc ZMNIEJSZONA z +1 do POZIOMU 0 (DOMYSLNY: 100% wielkosci fal)!",
    )
    wire_difficulty_transition(
        t_down_0_to_m1, is_up=False, stat_mode="neg_down",
        to_disable=[t_up_0_to_p1, t_down_0_to_m1],
        to_enable_after_2s=[t_up_m1_to_0, t_down_m1_to_m2],
        waves_to_enable=[], waves_to_disable=tier_0_wave_triggers,
        log_msg="[LOG BALANSU]: Trudnosc ZMNIEJSZONA do POZIOMU -1 (LATWY: -20% wielkosci fal, -15% HP wroga)!",
    )
    wire_difficulty_transition(
        t_down_m1_to_m2, is_up=False, stat_mode="neg_down",
        to_disable=[t_up_m1_to_0, t_down_m1_to_m2],
        to_enable_after_2s=[t_up_m2_to_m1],
        waves_to_enable=[], waves_to_disable=tier_m1_wave_triggers,
        log_msg="[LOG BALANSU]: Trudnosc ZMNIEJSZONA do POZIOMU -2 (BARDZO LATWY: -40% wielkosci fal, -28% HP wroga)!",
    )
    wire_difficulty_transition(
        t_up_m2_to_m1, is_up=True, stat_mode="neg_up",
        to_disable=[t_up_m2_to_m1],
        to_enable_after_2s=[t_up_m1_to_0, t_down_m1_to_m2],
        waves_to_enable=tier_m1_wave_triggers, waves_to_disable=[],
        log_msg="[LOG BALANSU]: Trudnosc ZWIEKSZONA z -2 do POZIOMU -1 (LATWY: -20% wielkosci fal)!",
    )
    wire_difficulty_transition(
        t_up_m1_to_0, is_up=True, stat_mode="neg_up",
        to_disable=[t_up_m1_to_0, t_down_m1_to_m2],
        to_enable_after_2s=[t_up_0_to_p1, t_down_0_to_m1],
        waves_to_enable=tier_0_wave_triggers, waves_to_disable=[],
        log_msg="[LOG BALANSU]: Trudnosc ZWIEKSZONA z -1 do POZIOMU 0 (DOMYSLNY: 100% wielkosci fal)!",
    )

    t_obj_balance = tm.add_trigger("00_Obj_Balance_Info", enabled=True, looping=False)
    safe_call(t_obj_balance.new_condition.timer, timer=99999)
    set_as_objective(t_obj_balance, "Balans (6,150): Krol P1 Gora=Trudniej / Dol=Latwiej", order=75, is_header=True)

    # ==============================================================================
    # 10. LOGIKA 4 QUESTÓW (POJEDYNCZE TARGOWISKO W PRAWYM ROGU + 10-KRATKOWY SZLAK)
    # ==============================================================================
    t_obj_header_q = tm.add_trigger("00_Obj_Header_Quests", enabled=True, looping=False)
    safe_call(t_obj_header_q.new_condition.timer, timer=99999)
    set_as_objective(t_obj_header_q, "-- QUESTY POBOCZNE (STALE PERKI) --", order=100, is_header=True)

    t_q1 = tm.add_trigger("06_Quest1_Build_Trade_Wall_And_Pop", enabled=True, looping=False)
    set_as_objective(t_q1, "Q1 - Karawanseraj (Mur Handlowy, +30 Pop, +20% Eko)", order=99)
    safe_call(t_q1.new_condition.destroy_object, unit_object=q1_bldg.reference_id)

    # Ciągły Kamienny Mur Obronny z Basztami wzdłuż 10-kratkowego korytarza handlowego (y = 188)
    keep_x_positions = {115, 130, 145, 160, 175, 190}
    for wx in range(105, MAP_SIZE):
        if wx in keep_x_positions:
            safe_call(
                t_q1.new_effect.create_object,
                object_list_unit_id=BuildingInfo.KEEP.ID,
                source_player=PlayerId.FOUR,
                location_x=wx,
                location_y=190,
            )
        safe_call(
            t_q1.new_effect.create_object,
            object_list_unit_id=BuildingInfo.FORTIFIED_WALL.ID,
            source_player=PlayerId.FOUR,
            location_x=wx,
            location_y=188,
        )

    # POJEDYNCZE sojusznicze Targowisko w prawym rogu mapy na (195, 194)
    safe_call(
        t_q1.new_effect.create_object,
        object_list_unit_id=BuildingInfo.MARKET.ID,
        source_player=PlayerId.TWO,
        location_x=195,
        location_y=194,
    )

    for h_p in human_players:
        add_player_resource(t_q1, h_p, RES_BONUS_POP_CAP, BALANCE["q1_bonus_pop"])
        add_player_resource(t_q1, h_p, RES_GOLD, 500)
        for vil_id in [UnitInfo.VILLAGER_MALE.ID, UnitInfo.VILLAGER_FEMALE.ID]:
            safe_modify_attribute(t_q1, h_p, vil_id, ATTR_WORK_RATE, Operation.MULTIPLY, 1.20)
        safe_modify_attribute(t_q1, h_p, UnitInfo.TRADE_CART_EMPTY.ID, ATTR_MOVEMENT_SPEED, Operation.MULTIPLY, 1.25)
        for i in range(4):
            px, py = p_coords[h_p]
            safe_call(
                t_q1.new_effect.create_object,
                object_list_unit_id=UnitInfo.TRADE_CART_EMPTY.ID,
                source_player=h_p,
                location_x=px + i,
                location_y=py + 5,
            )

    add_enemy_combat_buff(t_q1, ai_players, enemy_melee_units, enemy_ranged_units, hp_add=8, atk_add=1)

    send_highlight_chat(
        t_q1, "<GREEN>",
        "=== [Q1 UKONCZONY!] === Wybudowano KAMIENNY MUR HANDLOWY i postawiono sojuszniczy Market w prawym rogu (195, 194)! Wszyscy zyskuja +30 POPU, +20% Eko i 4 Wozy!",
        flare_x=195, flare_y=194,
    )

    # QUEST 2: Klif Artylerii
    t_q2 = tm.add_trigger("06_Quest2_Sniper_Cliff_Buff", enabled=True, looping=False)
    set_as_objective(t_q2, "Q2 - Klif Artylerii (+2 Zasiegu, +4 Ataku, Szybkosc)", order=98)
    safe_call(t_q2.new_condition.destroy_object, unit_object=q2_bldg.reference_id)
    research_techs(t_q2, human_players, [TECH_BALLISTICS, TECH_CHEMISTRY, TECH_SIEGE_ENGINEERS, TECH_THUMB_RING])

    ranged_units = [
        UnitInfo.ARCHER.ID, UnitInfo.CROSSBOWMAN.ID, UnitInfo.ARBALESTER.ID,
        UnitInfo.SKIRMISHER.ID, UnitInfo.ELITE_SKIRMISHER.ID,
        UnitInfo.CAVALRY_ARCHER.ID, UnitInfo.HEAVY_CAVALRY_ARCHER.ID, UnitInfo.HAND_CANNONEER.ID,
    ]
    cavalry_units = [
        UnitInfo.SCOUT_CAVALRY.ID, UnitInfo.LIGHT_CAVALRY.ID, HUSSAR_ID,
        UnitInfo.KNIGHT.ID, UnitInfo.CAVALIER.ID, UnitInfo.PALADIN.ID,
        UnitInfo.STEPPE_LANCER.ID, UnitInfo.CAMEL_RIDER.ID,
    ]
    for h_p in human_players:
        for r_id in ranged_units:
            safe_modify_attribute(t_q2, h_p, r_id, ATTR_MAXIMUM_RANGE, Operation.ADD, 2)
            safe_modify_attribute(t_q2, h_p, r_id, ATTR_SEARCH_RADIUS, Operation.ADD, 2)
            safe_modify_attribute(t_q2, h_p, r_id, ATTR_ATTACK, Operation.ADD, 4, armor_class=3)
        for c_id in cavalry_units:
            safe_modify_attribute(t_q2, h_p, c_id, ATTR_MOVEMENT_SPEED, Operation.MULTIPLY, 1.12)
            safe_modify_attribute(t_q2, h_p, c_id, ATTR_ATTACK, Operation.ADD, 4, armor_class=4)

    add_enemy_combat_buff(t_q2, ai_players, enemy_melee_units, enemy_ranged_units, hp_add=8, atk_add=1)

    send_highlight_chat(
        t_q2, "<GREEN>",
        "=== [Q2 UKONCZONY!] === Wszyscy otrzymuja Balistyke, Chemie, Siege Engineers, +2 Zasiegu i +4 Ataku dla strzelcow oraz +12% szybkosci i +4 Ataku dla jazdy!",
        flare_x=q2_pos[0], flare_y=q2_pos[1],
    )

    # QUEST 3: Skarbiec Krasnoludów
    t_q3_unlock = tm.add_trigger("06a_Quest3_Siege_Vault_Unlock", enabled=True, looping=False)
    set_as_objective(t_q3_unlock, "Q3 - Skarbiec (+20 Pop i Duzy Staly Dochod)", order=97)
    t_q3_trickle = tm.add_trigger("06b_Quest3_Passive_Resource_Trickle", enabled=False, looping=True)
    safe_call(t_q3_unlock.new_condition.destroy_object, unit_object=q3_bldg.reference_id)
    safe_call(t_q3_unlock.new_effect.activate_trigger, trigger_id=t_q3_trickle.trigger_id)
    for h_p in human_players:
        add_player_resource(t_q3_unlock, h_p, RES_BONUS_POP_CAP, BALANCE["q3_bonus_pop"])
        add_player_resource(t_q3_unlock, h_p, RES_GOLD, 600)
        add_player_resource(t_q3_unlock, h_p, RES_STONE, 300)

    add_enemy_combat_buff(t_q3_unlock, ai_players, enemy_melee_units, enemy_ranged_units, hp_add=10, atk_add=1)

    send_highlight_chat(
        t_q3_unlock, "<GREEN>",
        "=== [Q3 UKONCZONY!] === Wszyscy zyskuja na stale +20 LIMITU POPULACJI oraz duzy dochod (+250 Zywn/Drewna, +200 Zlota i +40 Kamienia co minute)!",
        flare_x=q3_pos[0], flare_y=q3_pos[1],
    )

    safe_call(t_q3_trickle.new_condition.timer, timer=60)
    tr_res = BALANCE["quest3_trickle"]
    for h_p in human_players:
        add_player_resource(t_q3_trickle, h_p, RES_FOOD, tr_res["food"])
        add_player_resource(t_q3_trickle, h_p, RES_WOOD, tr_res["wood"])
        add_player_resource(t_q3_trickle, h_p, RES_GOLD, tr_res["gold"])
        add_player_resource(t_q3_trickle, h_p, RES_STONE, tr_res["stone"])

    # QUEST 4: Krwawy Ołtarz
    t_q4 = tm.add_trigger("06_Quest4_Blood_Altar_Super_Army", enabled=True, looping=False)
    set_as_objective(t_q4, "Q4 - Krwawy Oltarz (+30% HP Armii i +40% Produkcji)", order=96)
    safe_call(t_q4.new_condition.destroy_object, unit_object=q4_bldg.reference_id)
    safe_modify_attribute(t_q4, PlayerId.SEVEN, IMAM_UNIT_ID, ATTR_HIT_POINTS, Operation.SET, 140)

    infantry_units = [
        UnitInfo.MAN_AT_ARMS.ID, UnitInfo.LONG_SWORDSMAN.ID, UnitInfo.TWO_HANDED_SWORDSMAN.ID, UnitInfo.CHAMPION.ID,
        UnitInfo.SPEARMAN.ID, UnitInfo.PIKEMAN.ID, UnitInfo.HALBERDIER.ID,
    ]
    prod_buildings = [BuildingInfo.BARRACKS.ID, BuildingInfo.STABLE.ID, BuildingInfo.ARCHERY_RANGE.ID, BuildingInfo.CASTLE.ID]
    for h_p in human_players:
        for u_id in ranged_units + cavalry_units + infantry_units:
            safe_modify_attribute(t_q4, h_p, u_id, ATTR_HIT_POINTS, Operation.MULTIPLY, 1.30)
            safe_modify_attribute(t_q4, h_p, u_id, ATTR_ARMOR, Operation.ADD, 2, armor_class=4)
            safe_modify_attribute(t_q4, h_p, u_id, ATTR_ARMOR, Operation.ADD, 2, armor_class=3)
        for b_id in prod_buildings:
            safe_modify_attribute(t_q4, h_p, b_id, ATTR_WORK_RATE, Operation.MULTIPLY, 1.40)

    add_enemy_combat_buff(t_q4, ai_players, enemy_melee_units, enemy_ranged_units, hp_add=10, atk_add=1)

    send_highlight_chat(
        t_q4, "<GREEN>",
        "=== [Q4 UKONCZONY!] === Wasze armie otrzymuja na stale +30% Max HP, +2/+2 Pancerza oraz +40% szybsza produkcje w budynkach wojskowych!",
        flare_x=q4_pos[0], flare_y=q4_pos[1],
    )

    # ==============================================================================
    # 11. ZNISZCZENIE 6 SETTLEMENTÓW (+15 HP i +2 ATAKU ZA ZBURZONY OBÓZ)
    # ==============================================================================
    t_obj_header_s = tm.add_trigger("00_Obj_Header_Settlements", enabled=True, looping=False)
    safe_call(t_obj_header_s.new_condition.timer, timer=99999)
    set_as_objective(t_obj_header_s, "-- SETTLEMENTY HORDY --", order=90, is_header=True)

    settlement_defs = [
        ("G1_North", s_g1_north, "G1 - Polnocny (usuwa Berserkerow i Petardy)", 89, *s_coords["G1_North"]),
        ("G1_East",  s_g1_east,  "G1 - Wschodni (usuwa Huskarlow i Wielblady)", 88, *s_coords["G1_East"]),
        ("G2_Snipers", s_g2_snipers, "G2 - Akademia (usuwa Snajperow i Mozdzierze)", 87, *s_coords["G2_Snipers"]),
        ("G2_Mages",   s_g2_mages,   "G2 - Klasztor (usuwa Magow i Szakale)", 86, *s_coords["G2_Mages"]),
        ("G3_North", s_g3_north, "G3 - Cytadela Pln. (usuwa Slonie-Tanki Pln.)", 85, *s_coords["G3_North"]),
        ("G3_East",  s_g3_east,  "G3 - Cytadela Wsch. (usuwa Slonie-Tanki Wsch.)", 84, *s_coords["G3_East"]),
    ]

    for s_key, core_unit, obj_label, obj_order, sx, sy in settlement_defs:
        t_destroy = tm.add_trigger(f"05_Settlement_Destroyed_{s_key}", enabled=True, looping=False)
        set_as_objective(t_destroy, obj_label, order=obj_order)
        safe_call(t_destroy.new_condition.destroy_object, unit_object=core_unit.reference_id)

        for tr_w in all_settlement_wave_triggers[s_key]:
            safe_call(t_destroy.new_effect.deactivate_trigger, trigger_id=tr_w.trigger_id)

        for h_p in human_players:
            add_player_resource(t_destroy, h_p, RES_GOLD, 600)
            add_player_resource(t_destroy, h_p, RES_FOOD, 600)

        add_enemy_combat_buff(t_destroy, ai_players, enemy_melee_units, enemy_ranged_units, hp_add=15, atk_add=2)

        add_spawn_and_attack_effect(
            t_destroy, PlayerId.EIGHT,
            [(ELITE_BATTLE_ELEPHANT_ID, 1), (UnitInfo.CAVALIER.ID, 12), (UnitInfo.HALBERDIER.ID, 16)],
            spawn_x=118, spawn_y=114, target_x=deep_target_center[0], target_y=deep_target_center[1],
        )

        send_highlight_chat(
            t_destroy, "<AQUA>",
            f"=== [SETTLEMENT ZNISZCZONY: {s_key}] === Jego oddzialy znikaja z fal (+600 Zlota/Zywnosci), a pozostale obozy zyskuja +15 HP i +2 Ataku!",
            flare_x=sx, flare_y=sy,
        )

    # 12. Warunki Zwycięstwa i Porażki
    t_win = tm.add_trigger("07_Victory_All_6_Settlements_Destroyed", enabled=True, looping=False)
    for _, core_unit, _, _, _, _ in settlement_defs:
        safe_call(t_win.new_condition.destroy_object, unit_object=core_unit.reference_id)
    for h_p in human_players:
        safe_call(t_win.new_effect.declare_victory, source_player=h_p, enabled=1)

    t_lose = tm.add_trigger("08_Defeat_Citadel_Lost", enabled=True, looping=False)
    safe_call(t_lose.new_condition.destroy_object, unit_object=allied_citadel.reference_id)
    for ai_p in ai_players:
        safe_call(t_lose.new_effect.declare_victory, source_player=ai_p, enabled=1)
