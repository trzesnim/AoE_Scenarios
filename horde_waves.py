import inspect

from AoE2ScenarioParser.datasets.players import PlayerId
from AoE2ScenarioParser.datasets.trigger_lists import DiplomacyState, Operation
from AoE2ScenarioParser.datasets.units import UnitInfo

from horde_config import (
    ATTR_ARMOR,
    ATTR_ATTACK,
    ATTR_ATTACK_RELOAD_TIME,
    ATTR_BLAST_WIDTH,
    ATTR_HERO_STATUS,
    ATTR_HIT_POINTS,
    ATTR_LINE_OF_SIGHT,
    ATTR_MAXIMUM_RANGE,
    ATTR_MINIMUM_RANGE,
    ATTR_MOVEMENT_SPEED,
    ATTR_REGENERATION_RATE,
    ATTR_SEARCH_RADIUS,
    ATTR_WORK_RATE,
    BALANCE,
    ELITE_BATTLE_ELEPHANT_ID,
    ELITE_BERSERK_ID,
    FEITORIA_ID,
    FLAMING_CAMEL_ID,
    FLARE_UNIT_ID,
    FORTIFIED_PALISADE_ID,
    HUSSAR_ID,
    IMAM_UNIT_ID,
    MAP_REVEALER_ID,
    MAP_SIZE,
    PETARD_ID,
    RES_BONUS_POP_CAP,
    SIEGE_ONAGER_ID,
    TECH_BALLISTICS,
    TECH_BLAST_FURNACE,
    TECH_BLOODLINES,
    TECH_BODKIN_ARROW,
    TECH_BRACER,
    TECH_CARTOGRAPHY,
    TECH_CASTLE_AGE,
    TECH_CHAIN_BARDING,
    TECH_CHAIN_MAIL,
    TECH_CHEMISTRY,
    TECH_FAITH,
    TECH_FEUDAL_AGE,
    TECH_FLETCHING,
    TECH_FORGING,
    TECH_HUSBANDRY,
    TECH_IMPERIAL_AGE,
    TECH_IRON_CASTING,
    TECH_PLATE_BARDING,
    TECH_PLATE_MAIL,
    TECH_SCALE_BARDING,
    TECH_SCALE_MAIL,
    TECH_SIEGE_ENGINEERS,
    TECH_SQUIRES,
    get_wave_definitions,
)


def safe_call(func, **kwargs):
    sig = inspect.signature(func)
    valid_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
    return func(**valid_kwargs)


def safe_modify_attribute(trigger, source_player, unit_id, attr_id, operation, val, armor_class=None):
    fn = trigger.new_effect.modify_attribute
    base_kwargs = {
        "source_player": source_player,
        "object_list_unit_id": unit_id,
        "object_attributes": attr_id,
        "operation": operation,
    }
    if armor_class is not None:
        try:
            return safe_call(
                fn,
                **base_kwargs,
                armour_attack_class=armor_class,
                armour_attack_quantity=int(val),
            )
        except (ValueError, TypeError):
            return safe_call(
                fn,
                **base_kwargs,
                armour_attack_class=armor_class,
                quantity=val,
            )
    return safe_call(fn, **base_kwargs, quantity=val)


def add_enemy_combat_buff(
    trigger,
    ai_players: list[PlayerId],
    melee_units: list[int],
    ranged_units: list[int],
    hp_add: int,
    atk_add: int,
):
    """
    Dodaje HP oraz atak wyłącznie do właściwej klasy ataku danej jednostki:
    - melee_units -> tylko armor_class=4 (Base Melee),
    - ranged_units -> tylko armor_class=3 (Base Pierce).
    Chroni to w 100% przed błędem uint8 underflow (5+247 ataku)!
    """
    for ai_p in ai_players:
        for m_id in melee_units:
            if hp_add > 0:
                safe_modify_attribute(trigger, ai_p, m_id, ATTR_HIT_POINTS, Operation.ADD, hp_add)
            if atk_add > 0:
                safe_modify_attribute(trigger, ai_p, m_id, ATTR_ATTACK, Operation.ADD, atk_add, armor_class=4)
        for r_id in ranged_units:
            if hp_add > 0:
                safe_modify_attribute(trigger, ai_p, r_id, ATTR_HIT_POINTS, Operation.ADD, hp_add)
            if atk_add > 0:
                safe_modify_attribute(trigger, ai_p, r_id, ATTR_ATTACK, Operation.ADD, atk_add, armor_class=3)


def set_as_objective(trigger, text: str, order: int, is_header: bool = False):
    if hasattr(trigger, "short_description"):
        trigger.short_description = text
    if hasattr(trigger, "display_on_screen"):
        trigger.display_on_screen = 1
    if hasattr(trigger, "description_order"):
        trigger.description_order = order
    if is_header and hasattr(trigger, "header"):
        trigger.header = 1


def send_highlight_chat(trigger, color_tag: str, message: str, flare_x: int | None = None, flare_y: int | None = None):
    for h_p in [PlayerId.ONE, PlayerId.TWO, PlayerId.THREE, PlayerId.FOUR]:
        safe_call(
            trigger.new_effect.send_chat,
            source_player=h_p,
            message=f"{color_tag}{message}",
        )
        if flare_x is not None and flare_y is not None:
            if hasattr(trigger.new_effect, "flare"):
                safe_call(
                    trigger.new_effect.flare,
                    source_player=h_p,
                    location_x=flare_x,
                    location_y=flare_y,
                )
            safe_call(
                trigger.new_effect.create_object,
                object_list_unit_id=FLARE_UNIT_ID,
                source_player=h_p,
                location_x=flare_x,
                location_y=flare_y,
            )


def add_player_resource(trigger, player: PlayerId, resource_id: int, amount: int):
    safe_call(
        trigger.new_effect.modify_resource,
        source_player=player,
        tribute_list=resource_id,
        operation=Operation.ADD,
        quantity=amount,
    )


def research_techs(trigger, players: list[PlayerId], tech_ids: list[int]):
    for p in players:
        for t_id in tech_ids:
            safe_call(
                trigger.new_effect.research_technology,
                source_player=p,
                technology=t_id,
                force_research_technology=1,
            )


def add_guarded_camp_with_leash(tm, enable_parent_trigger, name: str, ai_player: PlayerId, cx: int, cy: int,
                                units_spec: list[tuple[int, int]]):
    detect_radius = 15
    x1, y1 = max(0, cx - detect_radius), max(0, cy - detect_radius)
    x2, y2 = min(MAP_SIZE - 1, cx + detect_radius), min(MAP_SIZE - 1, cy + detect_radius)

    t_spawn = tm.add_trigger(f"Garrison_Spawn_{name}", enabled=False, looping=False)
    add_spawn_and_attack_effect(t_spawn, ai_player, units_spec, spawn_x=cx, spawn_y=cy + 3, target_x=cx, target_y=cy)

    t_leash = tm.add_trigger(f"Garrison_Leash_{name}", enabled=False, looping=True)
    safe_call(t_leash.new_condition.timer, timer=3)
    ring_inner = 9
    ring_outer = 20
    leash_strips = [
        (cx - ring_outer, cy - ring_outer, cx + ring_outer, cy - ring_inner),
        (cx - ring_outer, cy + ring_inner, cx + ring_outer, cy + ring_outer),
        (cx - ring_outer, cy - ring_inner, cx - ring_inner, cy + ring_inner),
        (cx + ring_inner, cy - ring_inner, cx + ring_outer, cy + ring_inner),
    ]
    for sx1, sy1, sx2, sy2 in leash_strips:
        safe_call(
            t_leash.new_effect.attack_move,
            source_player=ai_player,
            area_x1=max(0, sx1),
            area_y1=max(0, sy1),
            area_x2=min(MAP_SIZE - 1, sx2),
            area_y2=min(MAP_SIZE - 1, sy2),
            location_x=cx,
            location_y=cy,
        )
    safe_call(t_spawn.new_effect.activate_trigger, trigger_id=t_leash.trigger_id)

    for h_p in [PlayerId.ONE, PlayerId.TWO, PlayerId.THREE, PlayerId.FOUR]:
        req_qty = 2 if h_p == PlayerId.ONE else 1
        t_detect = tm.add_trigger(f"Garrison_Detect_{name}_P{h_p.value}", enabled=False, looping=False)
        safe_call(
            t_detect.new_condition.objects_in_area,
            source_player=h_p,
            area_x1=x1, area_y1=y1, area_x2=x2, area_y2=y2,
            quantity=req_qty,
        )
        safe_call(t_detect.new_effect.activate_trigger, trigger_id=t_spawn.trigger_id)
        safe_call(enable_parent_trigger.new_effect.activate_trigger, trigger_id=t_detect.trigger_id)


def add_spawn_and_attack_effect(trigger, ai_player: PlayerId, units_spec: list[tuple[int, int]],
                                spawn_x: int, spawn_y: int, target_x: int, target_y: int,
                                ignore_frontline_move_only: bool = False):
    idx = 0
    for unit_id, count in units_spec:
        for _ in range(count):
            dx = (idx % 6) - 3
            dy = (idx // 6) - 3
            safe_call(
                trigger.new_effect.create_object,
                object_list_unit_id=unit_id,
                source_player=ai_player,
                location_x=spawn_x + dx,
                location_y=spawn_y + dy,
            )
            idx += 1

    order_fn = trigger.new_effect.attack_move
    if ignore_frontline_move_only and hasattr(trigger.new_effect, "move"):
        order_fn = trigger.new_effect.move

    safe_call(
        order_fn,
        source_player=ai_player,
        area_x1=max(0, spawn_x - 8),
        area_y1=max(0, spawn_y - 8),
        area_x2=min(MAP_SIZE - 1, spawn_x + 8),
        area_y2=min(MAP_SIZE - 1, spawn_y + 8),
        location_x=target_x,
        location_y=target_y,
    )


def scale_comp(comp: list[tuple[int, int]], factor: float) -> list[tuple[int, int]]:
    scaled = []
    for u_id, cnt in comp:
        new_cnt = round(cnt * factor)
        if new_cnt > 0:
            scaled.append((u_id, new_cnt))
    return scaled


def setup_init_aura_and_waves(scenario, ctx: dict) -> None:
    ai_players = ctx["ai_players"]
    allied_citadel = ctx["allied_citadel"]
    balance_king = ctx["balance_king"]
    east_breach_trees = ctx["east_breach_trees"]
    gate_center = ctx["gate_center"]
    gate_east = ctx["gate_east"]
    gate_north = ctx["gate_north"]
    human_players = ctx["human_players"]
    north_breach_trees = ctx["north_breach_trees"]
    q1_bldg = ctx["q1_bldg"]
    q1_pos = ctx["q1_pos"]
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
    sx = ctx["sx"]
    sy = ctx["sy"]
    tm = ctx["tm"]
    tx = ctx["tx"]
    ty = ctx["ty"]

    t_init = tm.add_trigger("01_Init_Diplomacy_And_Cartography", enabled=True, looping=False)

    research_techs(t_init, human_players, [TECH_CARTOGRAPHY])
    safe_modify_attribute(t_init, PlayerId.ONE, MAP_REVEALER_ID, ATTR_LINE_OF_SIGHT, Operation.SET, 4)

    safe_modify_attribute(t_init, PlayerId.ONE, UnitInfo.KING.ID, ATTR_HIT_POINTS, Operation.SET, 9999)
    safe_modify_attribute(t_init, PlayerId.ONE, UnitInfo.KING.ID, ATTR_REGENERATION_RATE, Operation.SET, 5000)

    safe_modify_attribute(t_init, PlayerId.TWO, FEITORIA_ID, ATTR_HIT_POINTS, Operation.ADD, 3000)
    add_player_resource(t_init, PlayerId.TWO, RES_BONUS_POP_CAP, 20)

    for h1 in human_players:
        safe_modify_attribute(t_init, h1, FORTIFIED_PALISADE_ID, ATTR_HIT_POINTS, Operation.ADD, 400)
        for h2 in human_players:
            if h1 != h2:
                safe_call(t_init.new_effect.change_diplomacy, source_player=h1, target_player=h2, diplomacy=DiplomacyState.ALLY)
        for ai in ai_players:
            safe_call(t_init.new_effect.change_diplomacy, source_player=h1, target_player=ai, diplomacy=DiplomacyState.ENEMY)
            safe_call(t_init.new_effect.change_diplomacy, source_player=ai, target_player=h1, diplomacy=DiplomacyState.ENEMY)

    for ai1 in ai_players:
        for ai2 in ai_players:
            if ai1 != ai2:
                safe_call(t_init.new_effect.change_diplomacy, source_player=ai1, target_player=ai2, diplomacy=DiplomacyState.ALLY)

    research_techs(t_init, ai_players, [TECH_FEUDAL_AGE, TECH_CASTLE_AGE, TECH_IMPERIAL_AGE])
    research_techs(t_init, [PlayerId.EIGHT], [TECH_FAITH])

    t_ai_smith_feudal = tm.add_trigger("01d_AI_Techs_Feudal_8m30s", enabled=True, looping=False)
    safe_call(t_ai_smith_feudal.new_condition.timer, timer=510)
    research_techs(t_ai_smith_feudal, [PlayerId.FIVE], [TECH_SCALE_MAIL])
    research_techs(t_ai_smith_feudal, [PlayerId.SIX], [TECH_FLETCHING])
    research_techs(t_ai_smith_feudal, [PlayerId.SEVEN], [TECH_FORGING, TECH_BLOODLINES])
    research_techs(t_ai_smith_feudal, [PlayerId.EIGHT], [TECH_FORGING, TECH_SCALE_BARDING])

    t_ai_smith_castle = tm.add_trigger("01e_AI_Techs_Castle_18m", enabled=True, looping=False)
    safe_call(t_ai_smith_castle.new_condition.timer, timer=1080)
    research_techs(t_ai_smith_castle, [PlayerId.FIVE], [TECH_CHAIN_MAIL, TECH_SQUIRES])
    research_techs(t_ai_smith_castle, [PlayerId.SIX], [TECH_BODKIN_ARROW, TECH_BALLISTICS])
    research_techs(t_ai_smith_castle, [PlayerId.SEVEN], [TECH_IRON_CASTING, TECH_HUSBANDRY])
    research_techs(t_ai_smith_castle, [PlayerId.EIGHT], [TECH_IRON_CASTING, TECH_CHAIN_BARDING])

    t_ai_smith_imp = tm.add_trigger("01f_AI_Techs_Imperial_34m30s", enabled=True, looping=False)
    safe_call(t_ai_smith_imp.new_condition.timer, timer=2070)
    research_techs(t_ai_smith_imp, [PlayerId.FIVE], [TECH_PLATE_MAIL])
    research_techs(t_ai_smith_imp, [PlayerId.SIX], [TECH_BRACER, TECH_CHEMISTRY, TECH_SIEGE_ENGINEERS])
    research_techs(t_ai_smith_imp, [PlayerId.SEVEN], [TECH_BLAST_FURNACE])
    research_techs(t_ai_smith_imp, [PlayerId.EIGHT], [TECH_BLAST_FURNACE, TECH_PLATE_BARDING, TECH_SIEGE_ENGINEERS])

    building_labels = [
        (balance_king, "Inzynier Balansu (Gora = Trudniej, Dol = Latwiej)"),
        (allied_citadel, "Cytadela Sojuszu P2 (Serce Twierdzy - Broncie jej!)"),
        (q1_bldg, "Q1: Karawanseraj (Buduje Mur Handlowy, +30 Pop, +20% Eko)"),
        (q2_bldg, "Q2: Klif Artylerii (+2 Zasiegu, +4 Ataku, Szybkosc)"),
        (q3_bldg, "Q3: Skarbiec (+20 Pop i Duzy Staly Dochod)"),
        (q4_bldg, "Q4: Krwawy Oltarz (+30% HP Armii i +40% Produkcji)"),
        (s_g1_north, "G1 Polnocny (Berserkerzy i Petardy)"),
        (s_g1_east,  "G1 Wschodni (Huskarlowie i Wielblady)"),
        (s_g2_snipers, "G2 Akademia (Snajperzy i Mozdzierze)"),
        (s_g2_mages,   "G2 Klasztor (Arcymagowie i Szakale)"),
        (s_g3_north, "G3 Cytadela Pln. (Zelazne Slonie-Tanki)"),
        (s_g3_east,  "G3 Cytadela Wsch. (Slonie-Tanki i Artyleria)"),
    ]
    for b_unit, label_text in building_labels:
        safe_call(
            t_init.new_effect.change_object_name,
            selected_object_ids=[b_unit.reference_id],
            message=label_text,
        )

    send_highlight_chat(
        t_init, "<YELLOW>",
        "=== KRONIKI RUBIEZY v6.2 === Inzynier Balansu P1 powrocil na (6, 150) w zachodnim lesie! Lewy dolny rog mapy (x=3..23, y=177..198) jest czysty pod Targowiska graczy!",
    )

    t_mutate = tm.add_trigger("01b_Apply_Specialized_Unit_Archetypes", enabled=True, looping=False)
    safe_call(t_mutate.new_condition.timer, timer=3)

    for ai_p in ai_players:
        for monk_id in [IMAM_UNIT_ID, UnitInfo.MISSIONARY.ID, UnitInfo.MONK.ID]:
            safe_modify_attribute(t_mutate, ai_p, monk_id, ATTR_MAXIMUM_RANGE, Operation.SET, 0)
            safe_modify_attribute(t_mutate, ai_p, monk_id, ATTR_WORK_RATE, Operation.SET, 0)

    # 1. TARAN-ŻÓŁW / ŻELAZNY SŁOŃ (Tank P8)
    safe_modify_attribute(t_mutate, PlayerId.EIGHT, ELITE_BATTLE_ELEPHANT_ID, ATTR_HIT_POINTS, Operation.SET, BALANCE["tank_hp"])
    safe_modify_attribute(t_mutate, PlayerId.EIGHT, ELITE_BATTLE_ELEPHANT_ID, ATTR_HERO_STATUS, Operation.SET, 1)
    safe_modify_attribute(t_mutate, PlayerId.EIGHT, ELITE_BATTLE_ELEPHANT_ID, ATTR_MOVEMENT_SPEED, Operation.SET, BALANCE["tank_speed"])
    safe_modify_attribute(t_mutate, PlayerId.EIGHT, ELITE_BATTLE_ELEPHANT_ID, ATTR_ATTACK, Operation.SET, BALANCE["tank_unit_atk"], armor_class=4)
    safe_modify_attribute(t_mutate, PlayerId.EIGHT, ELITE_BATTLE_ELEPHANT_ID, ATTR_ATTACK, Operation.ADD, BALANCE["tank_bldg_bonus"], armor_class=11)
    safe_modify_attribute(t_mutate, PlayerId.EIGHT, ELITE_BATTLE_ELEPHANT_ID, ATTR_ATTACK, Operation.ADD, BALANCE["tank_bldg_bonus"], armor_class=21)
    safe_modify_attribute(t_mutate, PlayerId.EIGHT, ELITE_BATTLE_ELEPHANT_ID, ATTR_ARMOR, Operation.SET, BALANCE["tank_melee_armor"], armor_class=4)
    safe_modify_attribute(t_mutate, PlayerId.EIGHT, ELITE_BATTLE_ELEPHANT_ID, ATTR_ARMOR, Operation.SET, BALANCE["tank_pierce_armor"], armor_class=3)

    # 2. SZAKAL DYWERSYJNY (Eco-Raider Huzar P7)
    safe_modify_attribute(t_mutate, PlayerId.SEVEN, HUSSAR_ID, ATTR_HIT_POINTS, Operation.SET, BALANCE["raider_hp"])
    safe_modify_attribute(t_mutate, PlayerId.SEVEN, HUSSAR_ID, ATTR_MOVEMENT_SPEED, Operation.SET, BALANCE["raider_speed"])
    safe_modify_attribute(t_mutate, PlayerId.SEVEN, HUSSAR_ID, ATTR_ATTACK, Operation.SET, BALANCE["raider_atk"], armor_class=4)
    safe_modify_attribute(t_mutate, PlayerId.SEVEN, HUSSAR_ID, ATTR_ARMOR, Operation.SET, BALANCE["raider_pierce_armor"], armor_class=3)
    safe_modify_attribute(t_mutate, PlayerId.SEVEN, HUSSAR_ID, ATTR_ARMOR, Operation.SET, 0, armor_class=4)

    # 3. ARCYMAG TARCZY (Imam P7)
    safe_modify_attribute(t_mutate, PlayerId.SEVEN, IMAM_UNIT_ID, ATTR_HIT_POINTS, Operation.SET, BALANCE["mage_hp"])
    safe_modify_attribute(t_mutate, PlayerId.SEVEN, IMAM_UNIT_ID, ATTR_HERO_STATUS, Operation.SET, 1)
    safe_modify_attribute(t_mutate, PlayerId.SEVEN, IMAM_UNIT_ID, ATTR_REGENERATION_RATE, Operation.SET, BALANCE["mage_regen_per_min"])
    safe_modify_attribute(t_mutate, PlayerId.SEVEN, IMAM_UNIT_ID, ATTR_MOVEMENT_SPEED, Operation.SET, BALANCE["mage_speed"])
    safe_modify_attribute(t_mutate, PlayerId.SEVEN, IMAM_UNIT_ID, ATTR_ARMOR, Operation.SET, BALANCE["mage_pierce_armor"], armor_class=3)
    safe_modify_attribute(t_mutate, PlayerId.SEVEN, IMAM_UNIT_ID, ATTR_ARMOR, Operation.SET, BALANCE["mage_melee_armor"], armor_class=4)

    # 4. MOŹDZIERZ OBLĘŻNICZY (Siege Onager P6)
    safe_modify_attribute(t_mutate, PlayerId.SIX, SIEGE_ONAGER_ID, ATTR_HIT_POINTS, Operation.SET, BALANCE["mortar_hp"])
    safe_modify_attribute(t_mutate, PlayerId.SIX, SIEGE_ONAGER_ID, ATTR_HERO_STATUS, Operation.SET, 1)
    safe_modify_attribute(t_mutate, PlayerId.SIX, SIEGE_ONAGER_ID, ATTR_MAXIMUM_RANGE, Operation.SET, BALANCE["mortar_range"])
    safe_modify_attribute(t_mutate, PlayerId.SIX, SIEGE_ONAGER_ID, ATTR_MINIMUM_RANGE, Operation.SET, BALANCE["mortar_min_range"])
    safe_modify_attribute(t_mutate, PlayerId.SIX, SIEGE_ONAGER_ID, ATTR_SEARCH_RADIUS, Operation.SET, 23)
    safe_modify_attribute(t_mutate, PlayerId.SIX, SIEGE_ONAGER_ID, ATTR_LINE_OF_SIGHT, Operation.SET, 23)
    safe_modify_attribute(t_mutate, PlayerId.SIX, SIEGE_ONAGER_ID, ATTR_ATTACK_RELOAD_TIME, Operation.SET, BALANCE["mortar_reload"])
    safe_modify_attribute(t_mutate, PlayerId.SIX, SIEGE_ONAGER_ID, ATTR_BLAST_WIDTH, Operation.SET, BALANCE["mortar_blast_width"])
    safe_modify_attribute(t_mutate, PlayerId.SIX, SIEGE_ONAGER_ID, ATTR_MOVEMENT_SPEED, Operation.SET, BALANCE["mortar_speed"])
    safe_modify_attribute(t_mutate, PlayerId.SIX, SIEGE_ONAGER_ID, ATTR_ATTACK, Operation.ADD, BALANCE["mortar_bonus_atk"], armor_class=4)

    # 5. SNAJPER IMPERIALNY (Elitarny Janczar P6)
    safe_modify_attribute(t_mutate, PlayerId.SIX, UnitInfo.ELITE_JANISSARY.ID, ATTR_HIT_POINTS, Operation.SET, BALANCE["sniper_hp"])
    safe_modify_attribute(t_mutate, PlayerId.SIX, UnitInfo.ELITE_JANISSARY.ID, ATTR_HERO_STATUS, Operation.SET, 1)
    safe_modify_attribute(t_mutate, PlayerId.SIX, UnitInfo.ELITE_JANISSARY.ID, ATTR_MAXIMUM_RANGE, Operation.SET, BALANCE["sniper_range"])
    safe_modify_attribute(t_mutate, PlayerId.SIX, UnitInfo.ELITE_JANISSARY.ID, ATTR_SEARCH_RADIUS, Operation.SET, 21)
    safe_modify_attribute(t_mutate, PlayerId.SIX, UnitInfo.ELITE_JANISSARY.ID, ATTR_LINE_OF_SIGHT, Operation.SET, 21)
    safe_modify_attribute(t_mutate, PlayerId.SIX, UnitInfo.ELITE_JANISSARY.ID, ATTR_ATTACK_RELOAD_TIME, Operation.SET, BALANCE["sniper_reload"])
    safe_modify_attribute(t_mutate, PlayerId.SIX, UnitInfo.ELITE_JANISSARY.ID, ATTR_ATTACK, Operation.ADD, BALANCE["sniper_bonus_atk"], armor_class=3)

    # 6. BERSERKERZY I KAMIKAZE (P5)
    for kamikaze_id in [PETARD_ID, FLAMING_CAMEL_ID]:
        safe_modify_attribute(t_mutate, PlayerId.FIVE, kamikaze_id, ATTR_HIT_POINTS, Operation.SET, BALANCE["kamikaze_hp"])
        safe_modify_attribute(t_mutate, PlayerId.FIVE, kamikaze_id, ATTR_MOVEMENT_SPEED, Operation.SET, BALANCE["kamikaze_speed"])
        safe_modify_attribute(t_mutate, PlayerId.FIVE, kamikaze_id, ATTR_BLAST_WIDTH, Operation.SET, BALANCE["kamikaze_blast_width"])
        safe_modify_attribute(t_mutate, PlayerId.FIVE, kamikaze_id, ATTR_ATTACK, Operation.ADD, BALANCE["kamikaze_bonus_atk"], armor_class=4)
        safe_modify_attribute(t_mutate, PlayerId.FIVE, kamikaze_id, ATTR_ARMOR, Operation.SET, 0, armor_class=3)

    safe_modify_attribute(t_mutate, PlayerId.FIVE, ELITE_BERSERK_ID, ATTR_HIT_POINTS, Operation.SET, BALANCE["berserk_hp"])
    safe_modify_attribute(t_mutate, PlayerId.FIVE, ELITE_BERSERK_ID, ATTR_MOVEMENT_SPEED, Operation.SET, BALANCE["berserk_speed"])
    safe_modify_attribute(t_mutate, PlayerId.FIVE, ELITE_BERSERK_ID, ATTR_ATTACK, Operation.ADD, BALANCE["berserk_bonus_atk"], armor_class=4)
    safe_modify_attribute(t_mutate, PlayerId.FIVE, ELITE_BERSERK_ID, ATTR_ARMOR, Operation.SET, 0, armor_class=3)

    t_arm_garrisons = tm.add_trigger("01c_Arm_Garrison_Detectors_At_4s", enabled=True, looping=False)
    safe_call(t_arm_garrisons.new_condition.timer, timer=4)

    add_guarded_camp_with_leash(tm, t_arm_garrisons, "Quest1_Caravan", PlayerId.FIVE, *q1_pos,
                                units_spec=[(UnitInfo.STEPPE_LANCER.ID, 12), (UnitInfo.CROSSBOWMAN.ID, 10), (ELITE_BERSERK_ID, 4)])
    add_guarded_camp_with_leash(tm, t_arm_garrisons, "Quest2_SniperCliff", PlayerId.SIX, *q2_pos,
                                units_spec=[(UnitInfo.ELITE_JANISSARY.ID, 6), (SIEGE_ONAGER_ID, 2), (UnitInfo.HALBERDIER.ID, 14)])
    add_guarded_camp_with_leash(tm, t_arm_garrisons, "Quest3_SiegeVault", PlayerId.EIGHT, *q3_pos,
                                units_spec=[(UnitInfo.HALBERDIER.ID, 18), (ELITE_BATTLE_ELEPHANT_ID, 2), (UnitInfo.ARBALESTER.ID, 14)])
    add_guarded_camp_with_leash(tm, t_arm_garrisons, "Quest4_BloodAltar", PlayerId.EIGHT, *q4_pos,
                                units_spec=[(UnitInfo.PALADIN.ID, 14), (ELITE_BATTLE_ELEPHANT_ID, 2), (UnitInfo.HALBERDIER.ID, 12)])

    add_guarded_camp_with_leash(tm, t_arm_garrisons, "Settle_G1_North", PlayerId.FIVE, *s_coords["G1_North"],
                                units_spec=[(UnitInfo.PIKEMAN.ID, 14), (ELITE_BERSERK_ID, 6), (UnitInfo.CROSSBOWMAN.ID, 8)])
    add_guarded_camp_with_leash(tm, t_arm_garrisons, "Settle_G1_East", PlayerId.FIVE, *s_coords["G1_East"],
                                units_spec=[(UnitInfo.HUSKARL.ID, 12), (UnitInfo.PIKEMAN.ID, 10), (FLAMING_CAMEL_ID, 3)])
    add_guarded_camp_with_leash(tm, t_arm_garrisons, "Settle_G2_Snipers", PlayerId.SIX, *s_coords["G2_Snipers"],
                                units_spec=[(UnitInfo.ELITE_JANISSARY.ID, 7), (SIEGE_ONAGER_ID, 2), (UnitInfo.HALBERDIER.ID, 16)])
    add_guarded_camp_with_leash(tm, t_arm_garrisons, "Settle_G2_Mages", PlayerId.SEVEN, *s_coords["G2_Mages"],
                                units_spec=[(UnitInfo.CAVALIER.ID, 14), (HUSSAR_ID, 8), (IMAM_UNIT_ID, 1)])
    add_guarded_camp_with_leash(tm, t_arm_garrisons, "Settle_G3_North", PlayerId.EIGHT, *s_coords["G3_North"],
                                units_spec=[(ELITE_BATTLE_ELEPHANT_ID, 3), (UnitInfo.HALBERDIER.ID, 20), (UnitInfo.PALADIN.ID, 12)])
    add_guarded_camp_with_leash(tm, t_arm_garrisons, "Settle_G3_East", PlayerId.EIGHT, *s_coords["G3_East"],
                                units_spec=[(ELITE_BATTLE_ELEPHANT_ID, 3), (UnitInfo.ARBALESTER.ID, 20), (SIEGE_ONAGER_ID, 2)])

    # ==============================================================================
    # 6. GLOBALNA AURA MAGÓW (USZCZELNIONY CYKL ON <-> OFF)
    # ==============================================================================
    r_local = BALANCE["mage_local_radius"]
    mx1, my1 = max(0, gate_center[0] - r_local), max(0, gate_center[1] - r_local)
    mx2, my2 = min(MAP_SIZE - 1, gate_center[0] + r_local), min(MAP_SIZE - 1, gate_center[1] + r_local)

    global_shielded_units = [
        UnitInfo.MAN_AT_ARMS.ID, UnitInfo.PIKEMAN.ID, UnitInfo.HALBERDIER.ID, UnitInfo.HUSKARL.ID,
        UnitInfo.ARCHER.ID, UnitInfo.CROSSBOWMAN.ID, UnitInfo.ARBALESTER.ID,
        UnitInfo.KNIGHT.ID, UnitInfo.CAVALIER.ID, UnitInfo.PALADIN.ID,
        UnitInfo.CAPPED_RAM.ID, UnitInfo.SIEGE_RAM.ID,
    ]

    t_shield_on = tm.add_trigger("02a_Mage_Global_Horde_Shield_On", enabled=False, looping=False)
    t_mage_heal_pulse = tm.add_trigger("02b_Mage_AoE_Heal_Pulse_3s", enabled=False, looping=True)
    t_mage_beacon = tm.add_trigger("02c_Mage_Visual_Flare_Beacon_8s", enabled=False, looping=True)
    t_shield_off = tm.add_trigger("02d_Mage_Global_Horde_Shield_Off", enabled=False, looping=False)

    safe_call(
        t_shield_on.new_condition.objects_in_area,
        source_player=PlayerId.SEVEN,
        object_list=IMAM_UNIT_ID,
        object_list_unit_id=IMAM_UNIT_ID,
        area_x1=mx1, area_y1=my1, area_x2=mx2, area_y2=my2,
        quantity=1,
    )
    for ai_p in ai_players:
        for u_id in global_shielded_units:
            safe_modify_attribute(t_shield_on, ai_p, u_id, ATTR_ARMOR, Operation.ADD, BALANCE["mage_shield_armor"], armor_class=3)
            safe_modify_attribute(t_shield_on, ai_p, u_id, ATTR_ARMOR, Operation.ADD, BALANCE["mage_shield_armor"], armor_class=4)
    safe_call(t_shield_on.new_effect.deactivate_trigger, trigger_id=t_shield_on.trigger_id)
    safe_call(t_shield_on.new_effect.activate_trigger, trigger_id=t_mage_heal_pulse.trigger_id)
    safe_call(t_shield_on.new_effect.activate_trigger, trigger_id=t_mage_beacon.trigger_id)
    safe_call(t_shield_on.new_effect.activate_trigger, trigger_id=t_shield_off.trigger_id)
    send_highlight_chat(
        t_shield_on, "<PURPLE>",
        "[GLOBALNA AURA MAGA - 25 KRATEK]: Arcymag (240 HP, regen 5 HP/s, flara!) dal +30/+30 Pancerza i leczenie WSZYSTKIM frakcjom Hordy (P5-P8)! Skupcie na nim ogien!",
        flare_x=114, flare_y=114,
    )

    safe_call(t_mage_heal_pulse.new_condition.timer, timer=3)
    safe_call(
        t_mage_heal_pulse.new_condition.objects_in_area,
        source_player=PlayerId.SEVEN,
        object_list=IMAM_UNIT_ID,
        object_list_unit_id=IMAM_UNIT_ID,
        area_x1=mx1, area_y1=my1, area_x2=mx2, area_y2=my2,
        quantity=1,
    )
    for ai_p in ai_players:
        safe_call(
            t_mage_heal_pulse.new_effect.heal_object,
            source_player=ai_p,
            area_x1=mx1, area_y1=my1, area_x2=mx2, area_y2=my2,
            quantity=BALANCE["mage_aoe_heal_3s"],
        )

    safe_call(t_mage_beacon.new_condition.timer, timer=8)
    safe_call(
        t_mage_beacon.new_condition.objects_in_area,
        source_player=PlayerId.SEVEN,
        object_list=IMAM_UNIT_ID,
        object_list_unit_id=IMAM_UNIT_ID,
        area_x1=mx1, area_y1=my1, area_x2=mx2, area_y2=my2,
        quantity=1,
    )
    send_highlight_chat(
        t_mage_beacon, "<PURPLE>",
        "[FLARA - ARCYMAG TARCZY]: Arcymag (P7 - 240 HP, regen 5 HP/s) w kregu pochodni przed Brama Centralna leczy i utrzymuje +30 Pancerza na Hordzie!",
        flare_x=114, flare_y=114,
    )

    safe_call(
        t_shield_off.new_condition.own_fewer_objects,
        source_player=PlayerId.SEVEN,
        object_list=IMAM_UNIT_ID,
        quantity=0,
    )
    for ai_p in ai_players:
        for u_id in global_shielded_units:
            safe_modify_attribute(t_shield_off, ai_p, u_id, ATTR_ARMOR, Operation.SUBTRACT, BALANCE["mage_shield_armor"], armor_class=3)
            safe_modify_attribute(t_shield_off, ai_p, u_id, ATTR_ARMOR, Operation.SUBTRACT, BALANCE["mage_shield_armor"], armor_class=4)
    safe_call(t_shield_off.new_effect.deactivate_trigger, trigger_id=t_mage_heal_pulse.trigger_id)
    safe_call(t_shield_off.new_effect.deactivate_trigger, trigger_id=t_mage_beacon.trigger_id)
    safe_call(t_shield_off.new_effect.deactivate_trigger, trigger_id=t_shield_off.trigger_id)
    send_highlight_chat(
        t_shield_off, "<GREEN>",
        "[BARIERA PRZELAMANA]: Arcymag zabity! Wszystkie armie Hordy (P5, P6, P7, P8) traca +30 Pancerza i leczenie!",
    )

    t_push_inside = tm.add_trigger("02e_Push_Gate_Units_Deep_Into_Base", enabled=True, looping=True)
    safe_call(t_push_inside.new_condition.timer, timer=15)
    gate_push_zones = [
        (gate_north[0] - 8, gate_north[1] - 4, gate_north[0] + 8, gate_north[1] + 8, 48, 138),
        (gate_center[0] - 8, gate_center[1] - 8, gate_center[0] + 4, gate_center[1] + 8, 54, 146),
        (gate_east[0] - 8, gate_east[1] - 8, gate_east[0] + 4, gate_east[1] + 8, 68, 162),
        (74, 94, 82, 108, 68, 130),
        (98, 135, 112, 144, 68, 146),
    ]
    for ai_p in [PlayerId.FIVE, PlayerId.SIX, PlayerId.EIGHT]:
        for gx1, gy1, gx2, gy2, p_tx, p_ty in gate_push_zones:
            safe_call(
                t_push_inside.new_effect.attack_move,
                source_player=ai_p,
                area_x1=gx1, area_y1=gy1, area_x2=gx2, area_y2=gy2,
                location_x=p_tx, location_y=p_ty,
            )

    # ==============================================================================
    # 7. ROZDZIELONE LISTY WRĘCZ / STRZELECKIE I 3-STOPNIOWA ESKALACJA
    # ==============================================================================
    enemy_melee_units = [
        UnitInfo.MAN_AT_ARMS.ID, UnitInfo.PIKEMAN.ID, UnitInfo.HALBERDIER.ID, UnitInfo.HUSKARL.ID,
        ELITE_BERSERK_ID,
        UnitInfo.SCOUT_CAVALRY.ID, UnitInfo.KNIGHT.ID, UnitInfo.CAVALIER.ID, UnitInfo.PALADIN.ID,
        ELITE_BATTLE_ELEPHANT_ID, SIEGE_ONAGER_ID,
    ]
    enemy_ranged_units = [
        UnitInfo.ARCHER.ID, UnitInfo.CROSSBOWMAN.ID, UnitInfo.ARBALESTER.ID, UnitInfo.ELITE_JANISSARY.ID,
    ]

    t_enable_esc1 = tm.add_trigger("04a_Enable_Escalation_At_20m", enabled=True, looping=False)
    safe_call(t_enable_esc1.new_condition.timer, timer=BALANCE["escalation_start_sec"])

    t_escalate1 = tm.add_trigger("04b_Global_Horde_Escalation_Every_5m", enabled=False, looping=True)
    safe_call(t_enable_esc1.new_effect.activate_trigger, trigger_id=t_escalate1.trigger_id)
    safe_call(t_escalate1.new_condition.timer, timer=BALANCE["escalation_interval_sec"])
    add_enemy_combat_buff(
        t_escalate1, ai_players, enemy_melee_units, enemy_ranged_units,
        hp_add=BALANCE["escalation_hp_add"], atk_add=BALANCE["escalation_atk_add"],
    )
    send_highlight_chat(
        t_escalate1, "<ORANGE>",
        f"[WZROST SILY HORDY]: Jednostki Hordy otrzymuja +{BALANCE['escalation_hp_add']} HP oraz +{BALANCE['escalation_atk_add']} Ataku!",
    )

    t_enable_esc2 = tm.add_trigger("04c_Enable_LateGame_Escalation_At_45m", enabled=True, looping=False)
    safe_call(t_enable_esc2.new_condition.timer, timer=BALANCE["late_escalation_start_sec"])

    t_escalate2 = tm.add_trigger("04d_LateGame_Horde_Overdrive_Every_5m", enabled=False, looping=True)
    safe_call(t_enable_esc2.new_effect.activate_trigger, trigger_id=t_escalate2.trigger_id)
    safe_call(t_escalate2.new_condition.timer, timer=BALANCE["escalation_interval_sec"])
    add_enemy_combat_buff(
        t_escalate2, ai_players, enemy_melee_units, enemy_ranged_units,
        hp_add=BALANCE["late_escalation_hp_add"], atk_add=1,
    )
    send_highlight_chat(
        t_escalate2, "<RED>",
        f"[FURIA LATE-GAME]: Horda wchodzi w faze pelnej mobilizacji (+{BALANCE['late_escalation_hp_add']} HP i +1 Ataku)!",
    )

    t_enable_esc3 = tm.add_trigger("04e_Enable_Endgame_Escalation_At_55m", enabled=True, looping=False)
    safe_call(t_enable_esc3.new_condition.timer, timer=BALANCE["endgame_escalation_start_sec"])

    t_escalate3 = tm.add_trigger("04f_Endgame_Horde_Escalation_Every_5m", enabled=False, looping=True)
    safe_call(t_enable_esc3.new_effect.activate_trigger, trigger_id=t_escalate3.trigger_id)
    safe_call(t_escalate3.new_condition.timer, timer=BALANCE["escalation_interval_sec"])
    add_enemy_combat_buff(
        t_escalate3, ai_players, enemy_melee_units, enemy_ranged_units,
        hp_add=BALANCE["endgame_escalation_hp_add"], atk_add=2,
    )
    send_highlight_chat(
        t_escalate3, "<RED>",
        f"[ESKALACJA ENDGAME]: Elitarne dywizje Hordy zyskuja kolejne +{BALANCE['endgame_escalation_hp_add']} HP i +2 Ataku!",
    )

    # ==============================================================================
    # 8. HARMONOGRAM 14 FAL Z PODZIAŁEM NA WARSTWY TRUDNOŚCI ORAZ ATAKAMI NA TRADE I LAS
    # ==============================================================================
    all_settlement_wave_triggers = {
        "G1_North": [], "G1_East": [], "G2_Snipers": [], "G2_Mages": [], "G3_North": [], "G3_East": [],
    }

    tier_m1_wave_triggers = []
    tier_0_wave_triggers = []
    tier_p1_wave_triggers = []
    tier_p2_wave_triggers = []

    wave_definitions = [
        (
            1, 510, "Fala 1/14 (8:30 - Szturm Feudalny bez taranow)",
            [(UnitInfo.MAN_AT_ARMS.ID, 6), (UnitInfo.ARCHER.ID, 5)],
            [(UnitInfo.MAN_AT_ARMS.ID, 6), (UnitInfo.SCOUT_CAVALRY.ID, 5)],
            [], [], [], [], 0,
        ),
        (
            2, 780, "Fala 2/14 (13:00 - Feudalna z Taranem i Mangonelem, bez jednostek specjalnych)",
            [(UnitInfo.MAN_AT_ARMS.ID, 8), (UnitInfo.ARCHER.ID, 6), (UnitInfo.BATTERING_RAM.ID, 1)],
            [(UnitInfo.SPEARMAN.ID, 8), (UnitInfo.SCOUT_CAVALRY.ID, 6), (UnitInfo.MANGONEL.ID, 1)],
            [], [], [], [], 0,
        ),
        (
            3, 1080, "Fala 3/14 (18:00 - Castle Age + pierwsi Berserkerzy, Snajperzy i Szakale!)",
            [(UnitInfo.PIKEMAN.ID, 11), (ELITE_BERSERK_ID, 3), (PETARD_ID, 1), (UnitInfo.BATTERING_RAM.ID, 1)],
            [(UnitInfo.HUSKARL.ID, 8), (UnitInfo.KNIGHT.ID, 5), (FLAMING_CAMEL_ID, 1)],
            [(UnitInfo.CROSSBOWMAN.ID, 10), (UnitInfo.ELITE_JANISSARY.ID, 2)],
            [], [], [], 5,
        ),
        (
            4, 1410, "Fala 4/14 (23:30 - Castle Age + Arcymag Tarczy dajacy +30 Pancerza calej Hordzie!)",
            [(UnitInfo.PIKEMAN.ID, 14), (ELITE_BERSERK_ID, 4), (UnitInfo.BATTERING_RAM.ID, 2)],
            [(UnitInfo.HUSKARL.ID, 10), (UnitInfo.KNIGHT.ID, 6), (FLAMING_CAMEL_ID, 2)],
            [(UnitInfo.CROSSBOWMAN.ID, 12), (UnitInfo.ELITE_JANISSARY.ID, 3)],
            [(IMAM_UNIT_ID, 1), (UnitInfo.KNIGHT.ID, 10), (UnitInfo.BATTERING_RAM.ID, 2)],
            [], [], 6,
        ),
        (
            5, 1740, "Fala 5/14 (29:00 - Pozny Castle Age + Mozdzierz Oblezniczy!)",
            [(UnitInfo.PIKEMAN.ID, 16), (ELITE_BERSERK_ID, 4), (PETARD_ID, 2), (UnitInfo.CAPPED_RAM.ID, 2)],
            [(UnitInfo.HUSKARL.ID, 12), (FLAMING_CAMEL_ID, 2), (UnitInfo.CAPPED_RAM.ID, 2)],
            [(UnitInfo.CROSSBOWMAN.ID, 14), (UnitInfo.ELITE_JANISSARY.ID, 3), (SIEGE_ONAGER_ID, 1)],
            [(IMAM_UNIT_ID, 1), (UnitInfo.KNIGHT.ID, 12)],
            [(UnitInfo.KNIGHT.ID, 8), (UnitInfo.PIKEMAN.ID, 10)],
            [], 7,
        ),
        (
            6, 2070, "Fala 6/14 (34:30 - Debiut Zelaznego Slonia-Tanka 1450 HP!)",
            [(UnitInfo.PIKEMAN.ID, 18), (ELITE_BERSERK_ID, 5), (UnitInfo.CAPPED_RAM.ID, 2)],
            [(UnitInfo.HUSKARL.ID, 14), (FLAMING_CAMEL_ID, 3), (UnitInfo.CAPPED_RAM.ID, 2)],
            [(UnitInfo.CROSSBOWMAN.ID, 16), (UnitInfo.ELITE_JANISSARY.ID, 3), (SIEGE_ONAGER_ID, 1)],
            [(IMAM_UNIT_ID, 1), (UnitInfo.CAVALIER.ID, 12), (UnitInfo.CAPPED_RAM.ID, 2)],
            [(ELITE_BATTLE_ELEPHANT_ID, 1), (UnitInfo.KNIGHT.ID, 10), (UnitInfo.PIKEMAN.ID, 12)],
            [(UnitInfo.CROSSBOWMAN.ID, 14), (UnitInfo.KNIGHT.ID, 8)],
            8,
        ),
        (
            7, 2400, "Fala 7/14 (40:00 - Wczesny Imperial Age)",
            [(UnitInfo.HALBERDIER.ID, 20), (ELITE_BERSERK_ID, 5), (PETARD_ID, 3), (UnitInfo.CAPPED_RAM.ID, 3)],
            [(UnitInfo.HUSKARL.ID, 16), (FLAMING_CAMEL_ID, 3), (UnitInfo.CAPPED_RAM.ID, 2)],
            [(UnitInfo.ARBALESTER.ID, 18), (UnitInfo.ELITE_JANISSARY.ID, 4), (SIEGE_ONAGER_ID, 1)],
            [(IMAM_UNIT_ID, 1), (UnitInfo.CAVALIER.ID, 14)],
            [(ELITE_BATTLE_ELEPHANT_ID, 2), (UnitInfo.CAVALIER.ID, 12), (UnitInfo.HALBERDIER.ID, 12)],
            [(ELITE_BATTLE_ELEPHANT_ID, 1), (UnitInfo.ARBALESTER.ID, 16)],
            9,
        ),
        (
            8, 2730, "Fala 8/14 (45:30 - Imperial Age + UDERZENIE NA SZLAK HANDLOWY!)",
            [(UnitInfo.HALBERDIER.ID, 22), (ELITE_BERSERK_ID, 6), (UnitInfo.SIEGE_RAM.ID, 3)],
            [(UnitInfo.HUSKARL.ID, 18), (FLAMING_CAMEL_ID, 3), (UnitInfo.SIEGE_RAM.ID, 3)],
            [(UnitInfo.ARBALESTER.ID, 20), (UnitInfo.ELITE_JANISSARY.ID, 4), (SIEGE_ONAGER_ID, 2)],
            [(IMAM_UNIT_ID, 2), (UnitInfo.CAVALIER.ID, 16), (UnitInfo.SIEGE_RAM.ID, 3)],
            [(ELITE_BATTLE_ELEPHANT_ID, 2), (UnitInfo.CAVALIER.ID, 14), (UnitInfo.HALBERDIER.ID, 14)],
            [(ELITE_BATTLE_ELEPHANT_ID, 2), (UnitInfo.ARBALESTER.ID, 18), (SIEGE_ONAGER_ID, 1)],
            10,
        ),
        (
            9, 3060, "Fala 9/14 (51:00 - Imperial Age + PRZEBICIE PRZEZ POLNOCNY LAS!)",
            [(UnitInfo.HALBERDIER.ID, 25), (ELITE_BERSERK_ID, 7), (PETARD_ID, 3), (UnitInfo.SIEGE_RAM.ID, 3)],
            [(UnitInfo.HUSKARL.ID, 20), (FLAMING_CAMEL_ID, 4), (UnitInfo.SIEGE_RAM.ID, 3)],
            [(UnitInfo.ARBALESTER.ID, 22), (UnitInfo.ELITE_JANISSARY.ID, 4), (SIEGE_ONAGER_ID, 2)],
            [(IMAM_UNIT_ID, 2), (UnitInfo.PALADIN.ID, 16), (UnitInfo.SIEGE_RAM.ID, 3)],
            [(ELITE_BATTLE_ELEPHANT_ID, 3), (UnitInfo.PALADIN.ID, 15), (UnitInfo.HALBERDIER.ID, 16)],
            [(ELITE_BATTLE_ELEPHANT_ID, 2), (UnitInfo.ARBALESTER.ID, 20), (SIEGE_ONAGER_ID, 2)],
            12,
        ),
    ]

    for w_late in range(10, 15):
        m = w_late - 9
        wave_sec = 3060 + m * 330
        minute_mark = wave_sec // 60
        extra_tag = ""
        if w_late in (10, 12, 14):
            extra_tag += " + ATAK NA TRADE LINE"
        if w_late in (12, 14):
            extra_tag += " + PRZEBICIE PRZEZ LAS"
        wave_definitions.append((
            w_late, wave_sec,
            f"Fala {w_late}/14 ({minute_mark}m - Late Imperial{extra_tag}!)",
            [(UnitInfo.HALBERDIER.ID, 25 + m * 3), (ELITE_BERSERK_ID, 7 + m), (PETARD_ID, 3 + (m // 2)), (UnitInfo.SIEGE_RAM.ID, 4)],
            [(UnitInfo.HUSKARL.ID, 20 + m * 3), (FLAMING_CAMEL_ID, 3 + (m // 2)), (UnitInfo.SIEGE_RAM.ID, 4)],
            [(UnitInfo.ARBALESTER.ID, 22 + m * 3), (UnitInfo.ELITE_JANISSARY.ID, 4 + (m // 2)), (SIEGE_ONAGER_ID, 2 + (m // 3))],
            [(IMAM_UNIT_ID, 2 + (m // 3)), (UnitInfo.PALADIN.ID, 16 + m * 3), (UnitInfo.SIEGE_RAM.ID, 4)],
            [(ELITE_BATTLE_ELEPHANT_ID, 3 + (m // 2)), (UnitInfo.PALADIN.ID, 16 + m * 3), (UnitInfo.HALBERDIER.ID, 16 + m * 2)],
            [(ELITE_BATTLE_ELEPHANT_ID, 3 + (m // 2)), (UnitInfo.ARBALESTER.ID, 20 + m * 3), (SIEGE_ONAGER_ID, 2 + (m // 3))],
            12 + m,
        ))

    eco_raid_targets = [(32, 118), (76, 120), (32, 168), (76, 172)]
    deep_target_north = (48, 138)
    deep_target_center = (54, 146)
    deep_target_east = (68, 162)

    wave_definitions = get_wave_definitions()
    total_waves = len(wave_definitions)
    for (
        wave_num, wave_time, wave_title,
        g1_n_comp, g1_e_comp, g2_s_comp, g2_m_comp, g3_n_comp, g3_e_comp, raider_count,
    ) in wave_definitions:
        is_endless_last = wave_num == total_waves
        loop_flag = is_endless_last
        cond_time = BALANCE["wave_interval_sec"] if is_endless_last else wave_time

        t_ann = tm.add_trigger(f"03_W{wave_num:02d}_Announce", enabled=not is_endless_last, looping=loop_flag)
        safe_call(t_ann.new_condition.timer, timer=cond_time)

        send_highlight_chat(
            t_ann, "<RED>",
            f"=== [{wave_title}] === Po odparciu fali wyjdzcie w pole po Questy i Settlementy!",
            flare_x=gate_center[0], flare_y=gate_center[1],
        )

        per_settlement_wave = [
            ("G1_North", PlayerId.FIVE, g1_n_comp, 48, 86, *deep_target_north),
            ("G1_East",  PlayerId.FIVE, g1_e_comp, 120, 162, *deep_target_east),
            ("G2_Snipers", PlayerId.SIX, g2_s_comp, 68, 48, *deep_target_north),
            ("G2_Mages",   PlayerId.SEVEN, g2_m_comp, 116, 114, *deep_target_center),
            ("G3_North", PlayerId.EIGHT, g3_n_comp, 128, 36, *deep_target_center),
            ("G3_East",  PlayerId.EIGHT, g3_e_comp, 160, 62, *deep_target_east),
        ]

        for s_key, ai_p, comp, sx, sy, tx, ty in per_settlement_wave:
            if not comp:
                continue

            base_comp = scale_comp(comp, 0.60)
            m1_comp = scale_comp(comp, 0.20)
            t0_comp = scale_comp(comp, 0.20)
            p1_comp = scale_comp(comp, 0.25)
            p2_comp = scale_comp(comp, 0.25)

            layer_specs = [
                ("Base", base_comp, not is_endless_last, None),
                ("TierM1", m1_comp, not is_endless_last, tier_m1_wave_triggers),
                ("Tier0", t0_comp, not is_endless_last, tier_0_wave_triggers),
                ("TierP1", p1_comp, False, tier_p1_wave_triggers),
                ("TierP2", p2_comp, False, tier_p2_wave_triggers),
            ]

            for layer_name, l_comp, start_enabled, layer_list in layer_specs:
                if not l_comp:
                    continue
                t_w = tm.add_trigger(f"03_W{wave_num:02d}_{s_key}_{layer_name}", enabled=start_enabled, looping=loop_flag)
                safe_call(t_w.new_condition.timer, timer=cond_time)
                add_spawn_and_attack_effect(t_w, ai_p, l_comp, spawn_x=sx, spawn_y=sy, target_x=tx, target_y=ty)

                if layer_name == "Base" and s_key == "G2_Mages" and any(u == IMAM_UNIT_ID for u, _ in comp):
                    safe_call(t_w.new_effect.activate_trigger, trigger_id=t_shield_on.trigger_id)

                all_settlement_wave_triggers[s_key].append(t_w)
                if layer_list is not None:
                    layer_list.append(t_w)

                if is_endless_last and start_enabled:
                    t_enable_endless = tm.add_trigger(f"03_Enable_Endless_{s_key}_{layer_name}", enabled=True, looping=False)
                    safe_call(t_enable_endless.new_condition.timer, timer=wave_time)
                    safe_call(t_enable_endless.new_effect.activate_trigger, trigger_id=t_w.trigger_id)
                    if layer_name == "Base":
                        safe_call(t_enable_endless.new_effect.activate_trigger, trigger_id=t_ann.trigger_id)
                    all_settlement_wave_triggers[s_key].append(t_enable_endless)

        if raider_count > 0:
            eco_tx, eco_ty = eco_raid_targets[wave_num % len(eco_raid_targets)]
            t_raid = tm.add_trigger(f"03_W{wave_num:02d}_Szakale_EcoRaid", enabled=not is_endless_last, looping=loop_flag)
            safe_call(t_raid.new_condition.timer, timer=cond_time)
            add_spawn_and_attack_effect(
                t_raid, PlayerId.SEVEN, [(HUSSAR_ID, raider_count)],
                spawn_x=116, spawn_y=162 if wave_num % 2 == 0 else 114,
                target_x=eco_tx, target_y=eco_ty,
                ignore_frontline_move_only=True,
            )
            all_settlement_wave_triggers["G2_Mages"].append(t_raid)
            if is_endless_last:
                t_en_raid = tm.add_trigger("03_Enable_Endless_Szakale", enabled=True, looping=False)
                safe_call(t_en_raid.new_condition.timer, timer=wave_time)
                safe_call(t_en_raid.new_effect.activate_trigger, trigger_id=t_raid.trigger_id)
                all_settlement_wave_triggers["G2_Mages"].append(t_en_raid)

        if wave_num in (8, 10, 12, 14):
            t_trade_raid = tm.add_trigger(f"03_W{wave_num:02d}_Trade_Line_Attack", enabled=not is_endless_last, looping=loop_flag)
            safe_call(t_trade_raid.new_condition.timer, timer=cond_time)
            trade_raid_comp = [
                (UnitInfo.SIEGE_RAM.ID, 3),
                (UnitInfo.PALADIN.ID, 10 + (wave_num - 8) * 2),
                (UnitInfo.HEAVY_CAVALRY_ARCHER.ID, 10 + (wave_num - 8) * 2),
            ]
            add_spawn_and_attack_effect(
                t_trade_raid, PlayerId.EIGHT, trade_raid_comp,
                spawn_x=162, spawn_y=180, target_x=190, target_y=194,
            )
            send_highlight_chat(
                t_trade_raid, "<ORANGE>",
                "[ATAK NA SZLAK HANDLOWY!]: Wydzielony korpus Hordy z taranami uderza na Mur Handlowy na poludniu (162, 184)!",
                flare_x=162, flare_y=184,
            )
            all_settlement_wave_triggers["G3_East"].append(t_trade_raid)
            if is_endless_last:
                t_en_tr = tm.add_trigger("03_Enable_Endless_Trade_Attack", enabled=True, looping=False)
                safe_call(t_en_tr.new_condition.timer, timer=wave_time)
                safe_call(t_en_tr.new_effect.activate_trigger, trigger_id=t_trade_raid.trigger_id)
                all_settlement_wave_triggers["G3_East"].append(t_en_tr)

        if wave_num == 9:
            t_warn_forest_n = tm.add_trigger("03_W09_Forest_Breach_North_Warn", enabled=True, looping=False)
            safe_call(t_warn_forest_n.new_condition.timer, timer=wave_time - 15)
            add_spawn_and_attack_effect(
                t_warn_forest_n, PlayerId.SIX, [(SIEGE_ONAGER_ID, 2), (UnitInfo.HALBERDIER.ID, 8)],
                spawn_x=78, spawn_y=90, target_x=78, target_y=95,
            )
            send_highlight_chat(
                t_warn_forest_n, "<ORANGE>",
                "[ALARM SAPERSKI - POLNOCNY LAS]: Wrogie Onagery zaczynaja wyrabywac przesieke w lesie na (78, 100)! Za 15 sekund przebija sie do bazy!",
                flare_x=78, flare_y=98,
            )
            all_settlement_wave_triggers["G2_Snipers"].append(t_warn_forest_n)

            t_breach_n = tm.add_trigger("03_W09_Forest_Breach_North_Execute", enabled=True, looping=False)
            safe_call(t_breach_n.new_condition.timer, timer=wave_time)
            for tr_u in north_breach_trees:
                safe_call(t_breach_n.new_effect.remove_object, selected_object_ids=[tr_u.reference_id])
            add_spawn_and_attack_effect(
                t_breach_n, PlayerId.SIX,
                [(SIEGE_ONAGER_ID, 2), (UnitInfo.HALBERDIER.ID, 14), (ELITE_BERSERK_ID, 8)],
                spawn_x=78, spawn_y=94, target_x=68, target_y=130,
            )
            send_highlight_chat(
                t_breach_n, "<RED>",
                "[PRZESIEKA WYRABANA!]: Onagery Hordy przebily przejscie przez polnocny las na (78, 100) i wlewaja sie na tyly bazy!",
                flare_x=78, flare_y=102,
            )
            all_settlement_wave_triggers["G2_Snipers"].append(t_breach_n)

        if wave_num == 12:
            t_warn_forest_e = tm.add_trigger("03_W12_Forest_Breach_East_Warn", enabled=True, looping=False)
            safe_call(t_warn_forest_e.new_condition.timer, timer=wave_time - 15)
            add_spawn_and_attack_effect(
                t_warn_forest_e, PlayerId.SIX, [(SIEGE_ONAGER_ID, 2), (UnitInfo.HALBERDIER.ID, 10)],
                spawn_x=114, spawn_y=140, target_x=109, target_y=140,
            )
            send_highlight_chat(
                t_warn_forest_e, "<ORANGE>",
                "[ALARM SAPERSKI - WSCHODNI LAS]: Wrogie Onagery wyrabuja druga przesieke we wschodnim lesie na (104, 140)! Za 15s przebija sie do bazy!",
                flare_x=106, flare_y=140,
            )
            all_settlement_wave_triggers["G2_Snipers"].append(t_warn_forest_e)

            t_breach_e = tm.add_trigger("03_W12_Forest_Breach_East_Execute", enabled=True, looping=False)
            safe_call(t_breach_e.new_condition.timer, timer=wave_time)
            for tr_u in east_breach_trees:
                safe_call(t_breach_e.new_effect.remove_object, selected_object_ids=[tr_u.reference_id])
            add_spawn_and_attack_effect(
                t_breach_e, PlayerId.SIX,
                [(SIEGE_ONAGER_ID, 2), (UnitInfo.HALBERDIER.ID, 16), (UnitInfo.HUSKARL.ID, 12)],
                spawn_x=110, spawn_y=140, target_x=68, target_y=146,
            )
            send_highlight_chat(
                t_breach_e, "<RED>",
                "[DRUGA PRZESIEKA WYRABANA!]: Onagery Hordy przebily wschodni las na (104, 140)!",
                flare_x=104, flare_y=140,
            )
            all_settlement_wave_triggers["G2_Snipers"].append(t_breach_e)

        if wave_num == 14:
            t_endless_sapper = tm.add_trigger("03_W14_Endless_Forest_Breach_Assault", enabled=False, looping=True)
            safe_call(t_endless_sapper.new_condition.timer, timer=cond_time)
            add_spawn_and_attack_effect(
                t_endless_sapper, PlayerId.SIX,
                [(SIEGE_ONAGER_ID, 2), (UnitInfo.HALBERDIER.ID, 14), (ELITE_BERSERK_ID, 8)],
                spawn_x=78, spawn_y=94, target_x=68, target_y=130,
            )
            add_spawn_and_attack_effect(
                t_endless_sapper, PlayerId.SIX,
                [(SIEGE_ONAGER_ID, 2), (UnitInfo.HALBERDIER.ID, 14), (UnitInfo.HUSKARL.ID, 10)],
                spawn_x=110, spawn_y=140, target_x=68, target_y=146,
            )
            all_settlement_wave_triggers["G2_Snipers"].append(t_endless_sapper)

            t_en_sap = tm.add_trigger("03_Enable_Endless_Sapper", enabled=True, looping=False)
            safe_call(t_en_sap.new_condition.timer, timer=wave_time)
            safe_call(t_en_sap.new_effect.activate_trigger, trigger_id=t_endless_sapper.trigger_id)
            all_settlement_wave_triggers["G2_Snipers"].append(t_en_sap)

    ctx["ai_p"] = ai_p
    ctx["all_settlement_wave_triggers"] = all_settlement_wave_triggers
    ctx["deep_target_center"] = deep_target_center
    ctx["enemy_melee_units"] = enemy_melee_units
    ctx["enemy_ranged_units"] = enemy_ranged_units
    ctx["s_key"] = s_key
    ctx["sx"] = sx
    ctx["sy"] = sy
    ctx["tier_0_wave_triggers"] = tier_0_wave_triggers
    ctx["tier_m1_wave_triggers"] = tier_m1_wave_triggers
    ctx["tier_p1_wave_triggers"] = tier_p1_wave_triggers
    ctx["tier_p2_wave_triggers"] = tier_p2_wave_triggers
    ctx["u_id"] = u_id
