"""Trigger helpers, strict safe_call validator, unit stat/name mutations, auras, and Closed-Loop scaling."""

from __future__ import annotations

from collections.abc import Callable
import inspect
from typing import Any

from AoE2ScenarioParser.datasets.players import PlayerId
from AoE2ScenarioParser.datasets.trigger_lists import Operation
from gondolin_config import (
    AI_PLAYERS,
    ARMOR_CLASS_MELEE,
    ARMOR_CLASS_PIERCE,
    ATTR_ARMOR,
    ATTR_ATTACK,
    ATTR_BLAST_WIDTH,
    ATTR_HERO_STATUS,
    ATTR_HIT_POINTS,
    ATTR_MAXIMUM_RANGE,
    ATTR_MOVEMENT_SPEED,
    ATTR_REGENERATION_RATE,
    ATTR_SEARCH_RADIUS,
    BALANCE,
    ENEMY_BALROG_BOSS_ID,
    ENEMY_FIRE_DRAKE_ID,
    ENEMY_GOTHMOG_ID,
    ENEMY_IRON_DRAGON_RAM_ID,
    ENEMY_MAEGLIN_ID,
    ENEMY_MELEE_UNITS,
    ENEMY_MOLE_PIKE_ID,
    ENEMY_MOLE_TRAITOR_ID,
    ENEMY_ORC_BRUTE_ID,
    ENEMY_ORC_CROSSBOW_ID,
    ENEMY_ORC_INFANTRY_ID,
    ENEMY_RANGED_UNITS,
    FLARE_UNIT_ID,
    HERO_DUILIN_ID,
    HERO_ECTHELION_ID,
    HERO_EGALMOTH_ID,
    HERO_ROG_ID,
    HUMAN_PLAYERS,
    MAP_REVEALER_ID,
    OBJECT_TYPE_MILITARY,
    PRIMARY_RETINUE_UNIT_BY_PLAYER,
    RES_BONUS_POP_CAP,
    RES_FOOD,
    RES_GOLD,
    RES_STONE,
    RES_WOOD,
    SECONDARY_RETINUE_UNIT_BY_PLAYER,
    TECH_BALLISTICS,
    TECH_BLAST_FURNACE,
    TECH_BODKIN_ARROW,
    TECH_BRACER,
    TECH_CARTOGRAPHY,
    TECH_CASTLE_AGE,
    TECH_CHAIN_BARDING_ARMOR,
    TECH_CHAIN_MAIL_ARMOR,
    TECH_CHEMISTRY,
    TECH_FEUDAL_AGE,
    TECH_FLETCHING,
    TECH_FORGING,
    TECH_IMPERIAL_AGE,
    TECH_IRON_CASTING,
    TECH_LEATHER_ARCHER_ARMOR,
    TECH_LOOM,
    TECH_PADDED_ARCHER_ARMOR,
    TECH_PLATE_BARDING_ARMOR,
    TECH_PLATE_MAIL_ARMOR,
    TECH_RING_ARCHER_ARMOR,
    TECH_SCALE_BARDING_ARMOR,
    TECH_SCALE_MAIL_ARMOR,
    TECH_SQUIRES,
    UNIT_ARCH_LONGBOW_ID,
    UNIT_ARCH_RATTAN_ID,
    UNIT_DISPLAY_NAMES,
    UNIT_FLOWER_BLADE_ID,
    UNIT_FLOWER_CAV_ID,
    UNIT_FOUNTAIN_GUARD_ID,
    UNIT_FOUNTAIN_HALB_ID,
    UNIT_HAMMER_SMITH_ID,
    UNIT_IDRIL_SAPPER_ID,
    UNIT_SWALLOW_SNIPER_ID,
    UNIT_TREE_PIKE_ID,
    UNIT_TREE_SLINGER_ID,
    UNIT_WING_CHAMPION_ID,
    UNIT_WING_GUARD_ID,
)

PLAYER_MELEE_RETINUE: list[int] = [
    UNIT_HAMMER_SMITH_ID,
    UNIT_WING_GUARD_ID,
    UNIT_WING_CHAMPION_ID,
    UNIT_FOUNTAIN_GUARD_ID,
    UNIT_FOUNTAIN_HALB_ID,
    UNIT_FLOWER_BLADE_ID,
    UNIT_FLOWER_CAV_ID,
    UNIT_TREE_PIKE_ID,
]

PLAYER_RANGED_RETINUE: list[int] = [
    UNIT_ARCH_LONGBOW_ID,
    UNIT_ARCH_RATTAN_ID,
    UNIT_SWALLOW_SNIPER_ID,
    UNIT_TREE_SLINGER_ID,
]

HERO_RANGED_IDS: set[int] = {
    HERO_EGALMOTH_ID,
    HERO_DUILIN_ID,
}


def safe_call(func: Callable[..., Any], **kwargs: Any) -> Any:
    """Invoke AoE2ScenarioParser condition/effect methods and raise ValueError on any unsupported argument."""
    sig = inspect.signature(func)
    has_var_kw = any(
        p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()
    )
    if not has_var_kw:
        unsupported = sorted(set(kwargs.keys()) - set(sig.parameters.keys()))
        if unsupported:
            valid = sorted(sig.parameters.keys())
            func_name = getattr(func, "__qualname__", getattr(func, "__name__", str(func)))
            msg = (
                f"[BLAD KRYTYCZNY API] Funkcja '{func_name}' otrzymala nieobslugiwane argumenty: "
                f"{unsupported}. Dozwolone parametry w tej wersji AoE2ScenarioParser: {valid}"
            )
            raise ValueError(msg)
    return func(**kwargs)


def apply_unit_lore_name(
    trig: Any,
    player: PlayerId,
    unit_id: int,
    custom_name: str | None = None,
) -> None:
    """Apply canonical Silmarillion Polish name to all units of unit_id owned by player."""
    label = custom_name or UNIT_DISPLAY_NAMES.get(unit_id)
    if not label:
        return
    safe_call(
        trig.new_effect.change_object_name,
        source_player=player,
        object_list_unit_id=unit_id,
        message=label,
    )


def add_chat_and_flare(
    trig: Any,
    message: str,
    flare_x: int | None = None,
    flare_y: int | None = None,
) -> None:
    """Send a colored chat message to all human players and spawn a mini-map flare unit."""
    for p_id in HUMAN_PLAYERS:
        safe_call(
            trig.new_effect.send_chat,
            source_player=p_id,
            message=message,
        )
    if flare_x is not None and flare_y is not None:
        for p_id in HUMAN_PLAYERS:
            safe_call(
                trig.new_effect.create_object,
                source_player=p_id,
                object_list_unit_id=FLARE_UNIT_ID,
                location_x=flare_x,
                location_y=flare_y,
            )


def spawn_progressive_revealer(
    trig: Any,
    x: int,
    y: int,
    player: PlayerId = PlayerId.ONE,
) -> None:
    """Spawn a Map Revealer dynamically during gameplay for Player 1 (shared via Cartography with P1-P4)."""
    safe_call(
        trig.new_effect.create_object,
        source_player=player,
        object_list_unit_id=MAP_REVEALER_ID,
        location_x=x,
        location_y=y,
    )


def award_glory_gold(trig: Any, points: int, reason_msg: str | None = None) -> None:
    """Modify Player 1's Gold (Glory High Score counter) safely using Operation.ADD or SUBTRACT."""
    op = Operation.ADD if points >= 0 else Operation.SUBTRACT
    qty = abs(points)
    safe_call(
        trig.new_effect.modify_resource,
        source_player=PlayerId.ONE,
        tribute_list=RES_GOLD,
        quantity=qty,
        operation=op,
    )
    if reason_msg:
        add_chat_and_flare(trig, reason_msg)


def add_enemy_combat_buff(
    trig: Any,
    hp_delta: int,
    atk_delta: int,
    use_multiply_hp: bool = False,
    hp_mult: float = 1.0,
) -> None:
    """Safely scale enemy melee (class 4) and ranged (class 3) units without uint8 underflow."""
    for ai_p in AI_PLAYERS:
        for u_id in ENEMY_MELEE_UNITS + ENEMY_RANGED_UNITS:
            if use_multiply_hp:
                safe_call(
                    trig.new_effect.modify_attribute,
                    source_player=ai_p,
                    object_list_unit_id=u_id,
                    object_attributes=ATTR_HIT_POINTS,
                    operation=Operation.MULTIPLY,
                    quantity=hp_mult,
                )
            elif hp_delta > 0:
                safe_call(
                    trig.new_effect.modify_attribute,
                    source_player=ai_p,
                    object_list_unit_id=u_id,
                    object_attributes=ATTR_HIT_POINTS,
                    operation=Operation.ADD,
                    quantity=hp_delta,
                )

        if atk_delta > 0:
            for m_id in ENEMY_MELEE_UNITS:
                safe_call(
                    trig.new_effect.modify_attribute,
                    source_player=ai_p,
                    object_list_unit_id=m_id,
                    object_attributes=ATTR_ATTACK,
                    operation=Operation.ADD,
                    armour_attack_class=ARMOR_CLASS_MELEE,
                    armour_attack_quantity=atk_delta,
                )
            for r_id in ENEMY_RANGED_UNITS:
                safe_call(
                    trig.new_effect.modify_attribute,
                    source_player=ai_p,
                    object_list_unit_id=r_id,
                    object_attributes=ATTR_ATTACK,
                    operation=Operation.ADD,
                    armour_attack_class=ARMOR_CLASS_PIERCE,
                    armour_attack_quantity=atk_delta,
                )


def create_escalating_encounter(
    tm: Any,
    name_prefix: str,
    sector: tuple[int, int, int, int],
    target_xy: tuple[int, int],
    base_spawns: list[tuple[PlayerId, int, int, int, int]],
    elite_spawns: list[tuple[PlayerId, int, int, int, int]],
    arm_at_start: bool = True,
    trigger_player: PlayerId = PlayerId.ONE,
    trigger_unit_id: int | None = None,
) -> tuple[Any, Any]:
    """Create a 2-stage Closed-Loop encounter separating t_base initiation from t_elite/reward military checks."""
    x1, y1, x2, y2 = sector
    tx, ty = target_xy

    t_base = tm.add_trigger(
        name=f"Enc_{name_prefix}_Base",
        enabled=arm_at_start,
        looping=False,
    )
    # 1. t_base initiation: can require a specific Hero/Unit (e.g. Rog) OR any Military unit of trigger_player
    if trigger_unit_id is not None:
        safe_call(
            t_base.new_condition.objects_in_area,
            source_player=trigger_player,
            object_list=trigger_unit_id,
            area_x1=x1,
            area_y1=y1,
            area_x2=x2,
            area_y2=y2,
            quantity=1,
        )
    else:
        safe_call(
            t_base.new_condition.objects_in_area,
            source_player=trigger_player,
            object_type=OBJECT_TYPE_MILITARY,
            area_x1=x1,
            area_y1=y1,
            area_x2=x2,
            area_y2=y2,
            quantity=1,
        )

    spawned_types_base: set[tuple[PlayerId, int]] = set()
    for ai_p, unit_id, count, sx, sy in base_spawns:
        spawned_types_base.add((ai_p, unit_id))
        for i in range(count):
            ox = sx + (i % 4) - 1
            oy = sy + (i // 4) - 1
            safe_call(
                t_base.new_effect.create_object,
                source_player=ai_p,
                object_list_unit_id=unit_id,
                location_x=ox,
                location_y=oy,
            )
        safe_call(
            t_base.new_effect.attack_move,
            source_player=ai_p,
            object_list_unit_id=unit_id,
            area_x1=sx - 5,
            area_y1=sy - 5,
            area_x2=sx + 5,
            area_y2=sy + 5,
            location_x=tx,
            location_y=ty,
        )
    for ai_p, unit_id in spawned_types_base:
        apply_unit_lore_name(t_base, ai_p, unit_id)

    t_elite = tm.add_trigger(
        name=f"Enc_{name_prefix}_EliteAmbush",
        enabled=False,
        looping=False,
    )
    safe_call(
        t_base.new_effect.activate_trigger,
        trigger_id=t_elite.trigger_id,
    )

    # 2. Mid-Encounter Escalation check after 20 seconds:
    # Always checks total Military squad strength (object_type=OBJECT_TYPE_MILITARY, quantity=8),
    # NEVER 5 copies of a unique hero like Rog!
    safe_call(
        t_elite.new_condition.timer,
        timer=BALANCE["mid_encounter_escalation_delay"],
    )
    safe_call(
        t_elite.new_condition.objects_in_area,
        source_player=trigger_player,
        object_type=OBJECT_TYPE_MILITARY,
        area_x1=max(0, x1 - 8),
        area_y1=max(0, y1 - 8),
        area_x2=min(239, x2 + 8),
        area_y2=min(239, y2 + 8),
        quantity=BALANCE["mid_encounter_military_min"],
    )

    spawned_types_elite: set[tuple[PlayerId, int]] = set()
    for ai_p, unit_id, count, sx, sy in elite_spawns:
        spawned_types_elite.add((ai_p, unit_id))
        for i in range(count):
            ox = sx + (i % 4) - 1
            oy = sy + (i // 4) - 1
            safe_call(
                t_elite.new_effect.create_object,
                source_player=ai_p,
                object_list_unit_id=unit_id,
                location_x=ox,
                location_y=oy,
            )
        safe_call(
            t_elite.new_effect.attack_move,
            source_player=ai_p,
            object_list_unit_id=unit_id,
            area_x1=sx - 5,
            area_y1=sy - 5,
            area_x2=sx + 5,
            area_y2=sy + 5,
            location_x=tx,
            location_y=ty,
        )
    for ai_p, unit_id in spawned_types_elite:
        apply_unit_lore_name(t_elite, ai_p, unit_id)

    add_chat_and_flare(
        t_elite,
        f"<ORANGE>[Zasadzka Elitarna] Odwod Angbandu uderza w sektorze {name_prefix}! Pokonajcie ich, aby zdobyc +200 Chwaly!",
        tx,
        ty,
    )

    # 3. Camp Leash trigger keeping Elite Ambush units engaged around target_xy
    rx1 = max(0, min(x1, tx) - 24)
    ry1 = max(0, min(y1, ty) - 24)
    rx2 = min(239, max(x2, tx) + 24)
    ry2 = min(239, max(y2, ty) + 24)

    t_elite_leash = tm.add_trigger(
        name=f"Enc_{name_prefix}_EliteLeash",
        enabled=False,
        looping=True,
    )
    safe_call(t_elite_leash.new_condition.timer, timer=6)
    for ai_p, unit_id in sorted(spawned_types_elite, key=lambda item: (item[0].value, item[1])):
        safe_call(
            t_elite_leash.new_effect.attack_move,
            source_player=ai_p,
            object_list_unit_id=unit_id,
            area_x1=max(0, rx1 - 15),
            area_y1=max(0, ry1 - 15),
            area_x2=min(239, rx2 + 15),
            area_y2=min(239, ry2 + 15),
            location_x=tx,
            location_y=ty,
        )
    safe_call(
        t_elite.new_effect.activate_trigger,
        trigger_id=t_elite_leash.trigger_id,
    )

    # 4. Separate reward trigger: requires that trigger_player still holds the sector with >= 1 Military unit
    # AND all spawned elite ambush units are genuinely dead (own_fewer_objects quantity=0 + local inverted check).
    # Simply kiting an elite unit outside the combat box will NEVER grant the reward while the unit lives!
    t_elite_reward = tm.add_trigger(
        name=f"Enc_{name_prefix}_EliteDefeatedReward",
        enabled=False,
        looping=False,
    )
    safe_call(
        t_elite.new_effect.activate_trigger,
        trigger_id=t_elite_reward.trigger_id,
    )
    safe_call(t_elite_reward.new_condition.timer, timer=15)
    safe_call(
        t_elite_reward.new_condition.objects_in_area,
        source_player=trigger_player,
        object_type=OBJECT_TYPE_MILITARY,
        area_x1=rx1,
        area_y1=ry1,
        area_x2=rx2,
        area_y2=ry2,
        quantity=1,
    )
    for ai_p, unit_id in sorted(spawned_types_elite, key=lambda item: (item[0].value, item[1])):
        safe_call(
            t_elite_reward.new_condition.own_fewer_objects,
            source_player=ai_p,
            object_list=unit_id,
            quantity=0,
        )
        safe_call(
            t_elite_reward.new_condition.objects_in_area,
            source_player=ai_p,
            object_list=unit_id,
            area_x1=rx1,
            area_y1=ry1,
            area_x2=rx2,
            area_y2=ry2,
            quantity=1,
            inverted=1,
        )
    safe_call(
        t_elite_reward.new_effect.deactivate_trigger,
        trigger_id=t_elite_leash.trigger_id,
    )
    award_glory_gold(
        t_elite_reward,
        BALANCE["glory_scores"]["elite_ambush_defeated"],
        f"<GREEN>[Zasadzka Elitarna Rozbita!] Odwod wroga w sektorze {name_prefix} zostal calkowicie wybity (+200 Chwaly)!",
    )

    return t_base, t_elite


def grant_soft_cap_reinforcements(
    tm: Any,
    phase_name: str,
    checkpoint_map: dict[PlayerId, tuple[int, int]],
    bldg_offsets: dict[PlayerId, int] | None = None,
) -> list[Any]:
    """Evaluate each player's total military army (0..14, 15..28, 29+) using object_type=OBJECT_TYPE_MILITARY."""
    _ = bldg_offsets  # Unused: object_type=OBJECT_TYPE_MILITARY naturally excludes buildings, walls, and revealers
    created_triggers: list[Any] = []

    crit_thresh = BALANCE["soft_cap_critical_threshold"]  # 15 -> Critical is <= 14 (0..14)
    dom_thresh = BALANCE["soft_cap_dominance_threshold"]  # 28 -> Standard is 15..28; Dominance is >= 29

    for p_id in HUMAN_PLAYERS:
        cx, cy = checkpoint_map[p_id]
        u_main = PRIMARY_RETINUE_UNIT_BY_PLAYER[p_id]
        u_sec = SECONDARY_RETINUE_UNIT_BY_PLAYER[p_id]

        # 1. Critical Rescue Pack: 0..14 total military units (own_fewer_objects <= 14, no object_list!)
        t_crit = tm.add_trigger(
            name=f"SoftCap_{phase_name}_P{p_id.value}_Critical",
            enabled=False,
            looping=False,
        )
        safe_call(
            t_crit.new_condition.own_fewer_objects,
            source_player=p_id,
            object_type=OBJECT_TYPE_MILITARY,
            quantity=crit_thresh - 1,
        )
        for i in range(8):
            safe_call(
                t_crit.new_effect.create_object,
                source_player=p_id,
                object_list_unit_id=u_main,
                location_x=cx + (i % 4) - 1,
                location_y=cy + (i // 4),
            )
        for i in range(6):
            safe_call(
                t_crit.new_effect.create_object,
                source_player=p_id,
                object_list_unit_id=u_sec,
                location_x=cx + (i % 3) - 1,
                location_y=cy + 2 + (i // 3),
            )
        apply_unit_lore_name(t_crit, p_id, u_main)
        apply_unit_lore_name(t_crit, p_id, u_sec)
        safe_call(
            t_crit.new_effect.send_chat,
            source_player=p_id,
            message=f"<YELLOW>[Przegrupowanie {phase_name}] Twoja armia liczyla ponizej 15 wojownikow - Gwardia Krolewska uzupelnia szeregi (+14 jednostek)!",
        )
        created_triggers.append(t_crit)

        # 2. Standard Reserve Pack: 15..28 total military units (>= 15 AND <= 28, no object_list!)
        t_std = tm.add_trigger(
            name=f"SoftCap_{phase_name}_P{p_id.value}_Standard",
            enabled=False,
            looping=False,
        )
        safe_call(
            t_std.new_condition.own_objects,
            source_player=p_id,
            object_type=OBJECT_TYPE_MILITARY,
            quantity=crit_thresh,
        )
        safe_call(
            t_std.new_condition.own_fewer_objects,
            source_player=p_id,
            object_type=OBJECT_TYPE_MILITARY,
            quantity=dom_thresh,
        )
        for i in range(4):
            safe_call(
                t_std.new_effect.create_object,
                source_player=p_id,
                object_list_unit_id=u_main,
                location_x=cx + (i % 2),
                location_y=cy + (i // 2),
            )
        for i in range(3):
            safe_call(
                t_std.new_effect.create_object,
                source_player=p_id,
                object_list_unit_id=u_sec,
                location_x=cx + i - 1,
                location_y=cy + 2,
            )
        apply_unit_lore_name(t_std, p_id, u_main)
        apply_unit_lore_name(t_std, p_id, u_sec)
        created_triggers.append(t_std)

        # 3. Dominance Bonus: >= 29 total military units (own_objects >= 29, no object_list!)
        t_dom = tm.add_trigger(
            name=f"SoftCap_{phase_name}_P{p_id.value}_Dominance",
            enabled=False,
            looping=False,
        )
        safe_call(
            t_dom.new_condition.own_objects,
            source_player=p_id,
            object_type=OBJECT_TYPE_MILITARY,
            quantity=dom_thresh + 1,
        )
        award_glory_gold(
            t_dom,
            150,
            f"<AQUA>[Wzorowe Dowodzenie - P{p_id.value}] Ponad 28 jednostek wojskowych w {phase_name}: +150 Punktow Chwaly i +15 HP dla oddzialow!",
        )
        for u_id in (u_main, u_sec):
            safe_call(
                t_dom.new_effect.modify_attribute,
                source_player=p_id,
                object_list_unit_id=u_id,
                object_attributes=ATTR_HIT_POINTS,
                operation=Operation.ADD,
                quantity=15,
            )

        # Mutual lockouts: prevent units spawned by Critical/Standard from cascading into higher branches in the same tick!
        for t_branch in (t_crit, t_std, t_dom):
            for t_other in (t_crit, t_std, t_dom):
                if t_other.trigger_id != t_branch.trigger_id:
                    safe_call(
                        t_branch.new_effect.deactivate_trigger,
                        trigger_id=t_other.trigger_id,
                    )

        created_triggers.append(t_dom)

    return created_triggers


def _setup_t_init_and_unit_scaling(tm: Any, ctx: dict[str, Any]) -> None:
    """Rule 5.2: Research ages/techs and apply lore names at 0:01, then apply RPG stat mutations at 0:03."""
    t_init_techs = tm.add_trigger(
        name="Init_01s_Techs_And_Names",
        enabled=True,
        looping=False,
    )
    safe_call(t_init_techs.new_condition.timer, timer=1)

    all_combat_techs: list[int] = [
        TECH_FEUDAL_AGE,
        TECH_CASTLE_AGE,
        TECH_IMPERIAL_AGE,
        TECH_LOOM,
        TECH_SQUIRES,
        TECH_FLETCHING,
        TECH_BODKIN_ARROW,
        TECH_BRACER,
        TECH_PADDED_ARCHER_ARMOR,
        TECH_LEATHER_ARCHER_ARMOR,
        TECH_RING_ARCHER_ARMOR,
        TECH_FORGING,
        TECH_IRON_CASTING,
        TECH_BLAST_FURNACE,
        TECH_SCALE_MAIL_ARMOR,
        TECH_CHAIN_MAIL_ARMOR,
        TECH_PLATE_MAIL_ARMOR,
        TECH_SCALE_BARDING_ARMOR,
        TECH_CHAIN_BARDING_ARMOR,
        TECH_PLATE_BARDING_ARMOR,
        TECH_BALLISTICS,
        TECH_CHEMISTRY,
    ]

    for p_id in HUMAN_PLAYERS:
        safe_call(
            t_init_techs.new_effect.research_technology,
            source_player=p_id,
            technology=TECH_CARTOGRAPHY,
        )
        for tech_id in all_combat_techs:
            safe_call(
                t_init_techs.new_effect.research_technology,
                source_player=p_id,
                technology=tech_id,
            )
        safe_call(
            t_init_techs.new_effect.modify_resource,
            source_player=p_id,
            tribute_list=RES_BONUS_POP_CAP,
            quantity=150,
            operation=Operation.ADD,
        )

    for ai_p in AI_PLAYERS:
        for tech_id in all_combat_techs:
            safe_call(
                t_init_techs.new_effect.research_technology,
                source_player=ai_p,
                technology=tech_id,
            )
        for res_id in (RES_FOOD, RES_WOOD, RES_STONE, RES_GOLD):
            safe_call(
                t_init_techs.new_effect.modify_resource,
                source_player=ai_p,
                tribute_list=res_id,
                quantity=0,
                operation=Operation.SET,
            )

    # Rename key Gondolin landmarks
    bldg_names: dict[str, str] = {
        "tower_of_turgon": "Wieza Krola Turgona (Amon Gwareth)",
        "royal_fountain_bldg": "Fontanna Krolewska Ectheliona",
        "glingal_tree": "Glingal (Zlote Drzewo Gondolinu)",
        "belthil_tree": "Belthil (Srebrne Drzewo Gondolinu)",
        "great_forge": "Wielka Kuznia Roga (Dom Mlota)",
        "forge_workshop": "Zbrojownia Mithrilu",
        "great_market": "Wielki Targ Penloda",
        "aqueduct_control": "Sluzy Wielkiego Akweduktu (Zajete przez P8)",
        "snow_watchtower": "Wieza ze Sniegu (Punkt Obserwacyjny P3)",
        "salgant_manor": "Dwor Salganta (Dom Harfy)",
        "house_of_tuor": "Dwor Tuora i Idril (Oblezony przez Maeglina)",
        "caragdur_keep": "Twierdza Zdrajcow na Skale Caragdur (P8)",
        "idril_waygate": "Wejscie do Tajemnej Sciezki Idril",
        "balrog_altar": "Polowy Oltarz Balrogow na Tumladen",
        "winch_bronze": "Kolowrot Trzeciej Bramy (Brazowej)",
        "winch_silver": "Kolowrot Piatej Bramy (Srebrnej)",
        "winch_steel": "Kolowrot Siodmej Bramy (Stalowej)",
    }
    q_bldgs = ctx["quest_buildings"]
    for key, label in bldg_names.items():
        if key in q_bldgs:
            b_info = q_bldgs[key]
            safe_call(
                t_init_techs.new_effect.change_object_name,
                source_player=b_info["player"],
                selected_object_ids=[b_info["ref_id"]],
                message=label,
            )

    # Apply Silmarillion lore names to all initial Heroes, Noldor Retinues, Refugees, and Enemy Forces
    for u_id in UNIT_DISPLAY_NAMES:
        for p_id in HUMAN_PLAYERS + AI_PLAYERS + [PlayerId.GAIA]:
            apply_unit_lore_name(t_init_techs, p_id, u_id)

    # Trigger at 0:03: Apply Noldor Elite Retinue, Hero, and Boss stat mutations
    t_init_stats = tm.add_trigger(
        name="Init_03s_RPG_Unit_And_Hero_Stats",
        enabled=True,
        looping=False,
    )
    safe_call(t_init_stats.new_condition.timer, timer=3)

    for p_id in HUMAN_PLAYERS:
        for u_id in PLAYER_MELEE_RETINUE + PLAYER_RANGED_RETINUE:
            safe_call(
                t_init_stats.new_effect.modify_attribute,
                source_player=p_id,
                object_list_unit_id=u_id,
                object_attributes=ATTR_HIT_POINTS,
                operation=Operation.ADD,
                quantity=85,
            )
            safe_call(
                t_init_stats.new_effect.modify_attribute,
                source_player=p_id,
                object_list_unit_id=u_id,
                object_attributes=ATTR_REGENERATION_RATE,
                operation=Operation.SET,
                quantity=BALANCE["out_of_combat_regen_per_min"],
            )
            safe_call(
                t_init_stats.new_effect.modify_attribute,
                source_player=p_id,
                object_list_unit_id=u_id,
                object_attributes=ATTR_ARMOR,
                operation=Operation.ADD,
                armour_attack_class=ARMOR_CLASS_MELEE,
                armour_attack_quantity=2,
            )
            safe_call(
                t_init_stats.new_effect.modify_attribute,
                source_player=p_id,
                object_list_unit_id=u_id,
                object_attributes=ATTR_ARMOR,
                operation=Operation.ADD,
                armour_attack_class=ARMOR_CLASS_PIERCE,
                armour_attack_quantity=2,
            )

        for m_id in PLAYER_MELEE_RETINUE:
            safe_call(
                t_init_stats.new_effect.modify_attribute,
                source_player=p_id,
                object_list_unit_id=m_id,
                object_attributes=ATTR_ATTACK,
                operation=Operation.ADD,
                armour_attack_class=ARMOR_CLASS_MELEE,
                armour_attack_quantity=6,
            )

        for r_id in PLAYER_RANGED_RETINUE:
            safe_call(
                t_init_stats.new_effect.modify_attribute,
                source_player=p_id,
                object_list_unit_id=r_id,
                object_attributes=ATTR_ATTACK,
                operation=Operation.ADD,
                armour_attack_class=ARMOR_CLASS_PIERCE,
                armour_attack_quantity=6,
            )
            safe_call(
                t_init_stats.new_effect.modify_attribute,
                source_player=p_id,
                object_list_unit_id=r_id,
                object_attributes=ATTR_MAXIMUM_RANGE,
                operation=Operation.ADD,
                quantity=2,
            )
            safe_call(
                t_init_stats.new_effect.modify_attribute,
                source_player=p_id,
                object_list_unit_id=r_id,
                object_attributes=ATTR_SEARCH_RADIUS,
                operation=Operation.ADD,
                quantity=2,
            )

        safe_call(
            t_init_stats.new_effect.modify_attribute,
            source_player=p_id,
            object_list_unit_id=UNIT_IDRIL_SAPPER_ID,
            object_attributes=ATTR_HIT_POINTS,
            operation=Operation.SET,
            quantity=240,
        )

    for h_id, h_cfg in BALANCE["heroes"].items():
        p_id = h_cfg["player"]
        atk_class = ARMOR_CLASS_PIERCE if h_id in HERO_RANGED_IDS else ARMOR_CLASS_MELEE

        safe_call(
            t_init_stats.new_effect.modify_attribute,
            source_player=p_id,
            object_list_unit_id=h_id,
            object_attributes=ATTR_HERO_STATUS,
            operation=Operation.SET,
            quantity=1,
        )
        safe_call(
            t_init_stats.new_effect.modify_attribute,
            source_player=p_id,
            object_list_unit_id=h_id,
            object_attributes=ATTR_HIT_POINTS,
            operation=Operation.SET,
            quantity=h_cfg["hp"],
        )
        safe_call(
            t_init_stats.new_effect.modify_attribute,
            source_player=p_id,
            object_list_unit_id=h_id,
            object_attributes=ATTR_REGENERATION_RATE,
            operation=Operation.SET,
            quantity=BALANCE["hero_regen_per_min"],
        )
        safe_call(
            t_init_stats.new_effect.modify_attribute,
            source_player=p_id,
            object_list_unit_id=h_id,
            object_attributes=ATTR_ATTACK,
            operation=Operation.SET,
            armour_attack_class=atk_class,
            armour_attack_quantity=h_cfg["atk"],
        )
        safe_call(
            t_init_stats.new_effect.modify_attribute,
            source_player=p_id,
            object_list_unit_id=h_id,
            object_attributes=ATTR_ARMOR,
            operation=Operation.SET,
            armour_attack_class=ARMOR_CLASS_MELEE,
            armour_attack_quantity=h_cfg["melee_armor"],
        )
        safe_call(
            t_init_stats.new_effect.modify_attribute,
            source_player=p_id,
            object_list_unit_id=h_id,
            object_attributes=ATTR_ARMOR,
            operation=Operation.SET,
            armour_attack_class=ARMOR_CLASS_PIERCE,
            armour_attack_quantity=h_cfg["pierce_armor"],
        )
        safe_call(
            t_init_stats.new_effect.modify_attribute,
            source_player=p_id,
            object_list_unit_id=h_id,
            object_attributes=ATTR_MOVEMENT_SPEED,
            operation=Operation.SET,
            quantity=h_cfg["speed"],
        )
        if h_cfg["blast"] > 0:
            safe_call(
                t_init_stats.new_effect.modify_attribute,
                source_player=p_id,
                object_list_unit_id=h_id,
                object_attributes=ATTR_BLAST_WIDTH,
                operation=Operation.SET,
                quantity=h_cfg["blast"],
            )

    for ai_p in AI_PLAYERS:
        safe_call(
            t_init_stats.new_effect.modify_attribute,
            source_player=ai_p,
            object_list_unit_id=ENEMY_ORC_INFANTRY_ID,
            object_attributes=ATTR_HIT_POINTS,
            operation=Operation.SET,
            quantity=95,
        )
        safe_call(
            t_init_stats.new_effect.modify_attribute,
            source_player=ai_p,
            object_list_unit_id=ENEMY_ORC_INFANTRY_ID,
            object_attributes=ATTR_ATTACK,
            operation=Operation.SET,
            armour_attack_class=ARMOR_CLASS_MELEE,
            armour_attack_quantity=15,
        )
        safe_call(
            t_init_stats.new_effect.modify_attribute,
            source_player=ai_p,
            object_list_unit_id=ENEMY_ORC_BRUTE_ID,
            object_attributes=ATTR_HIT_POINTS,
            operation=Operation.SET,
            quantity=185,
        )
        safe_call(
            t_init_stats.new_effect.modify_attribute,
            source_player=ai_p,
            object_list_unit_id=ENEMY_ORC_BRUTE_ID,
            object_attributes=ATTR_ATTACK,
            operation=Operation.SET,
            armour_attack_class=ARMOR_CLASS_MELEE,
            armour_attack_quantity=22,
        )
        for mole_id in (ENEMY_MOLE_TRAITOR_ID, ENEMY_MOLE_PIKE_ID):
            safe_call(
                t_init_stats.new_effect.modify_attribute,
                source_player=ai_p,
                object_list_unit_id=mole_id,
                object_attributes=ATTR_HIT_POINTS,
                operation=Operation.SET,
                quantity=240,
            )
            safe_call(
                t_init_stats.new_effect.modify_attribute,
                source_player=ai_p,
                object_list_unit_id=mole_id,
                object_attributes=ATTR_ATTACK,
                operation=Operation.SET,
                armour_attack_class=ARMOR_CLASS_MELEE,
                armour_attack_quantity=26,
            )

    for b_id, b_cfg in BALANCE["bosses"].items():
        atk_cls = (
            ARMOR_CLASS_PIERCE if b_id == ENEMY_FIRE_DRAKE_ID else ARMOR_CLASS_MELEE
        )
        for ai_p in AI_PLAYERS:
            safe_call(
                t_init_stats.new_effect.modify_attribute,
                source_player=ai_p,
                object_list_unit_id=b_id,
                object_attributes=ATTR_HIT_POINTS,
                operation=Operation.SET,
                quantity=b_cfg["hp"],
            )
            safe_call(
                t_init_stats.new_effect.modify_attribute,
                source_player=ai_p,
                object_list_unit_id=b_id,
                object_attributes=ATTR_ATTACK,
                operation=Operation.SET,
                armour_attack_class=atk_cls,
                armour_attack_quantity=b_cfg["atk"],
            )
            safe_call(
                t_init_stats.new_effect.modify_attribute,
                source_player=ai_p,
                object_list_unit_id=b_id,
                object_attributes=ATTR_ARMOR,
                operation=Operation.SET,
                armour_attack_class=ARMOR_CLASS_MELEE,
                armour_attack_quantity=b_cfg["melee_armor"],
            )
            safe_call(
                t_init_stats.new_effect.modify_attribute,
                source_player=ai_p,
                object_list_unit_id=b_id,
                object_attributes=ATTR_ARMOR,
                operation=Operation.SET,
                armour_attack_class=ARMOR_CLASS_PIERCE,
                armour_attack_quantity=b_cfg["pierce_armor"],
            )
            if b_id in (ENEMY_GOTHMOG_ID, ENEMY_BALROG_BOSS_ID, ENEMY_MAEGLIN_ID):
                safe_call(
                    t_init_stats.new_effect.modify_attribute,
                    source_player=ai_p,
                    object_list_unit_id=b_id,
                    object_attributes=ATTR_HERO_STATUS,
                    operation=Operation.SET,
                    quantity=1,
                )
                safe_call(
                    t_init_stats.new_effect.modify_attribute,
                    source_player=ai_p,
                    object_list_unit_id=b_id,
                    object_attributes=ATTR_BLAST_WIDTH,
                    operation=Operation.SET,
                    quantity=1.4 if b_id == ENEMY_GOTHMOG_ID else 1.0,
                )


def _setup_special_auras_and_hazards(tm: Any, ctx: dict[str, Any]) -> None:
    """Set up Ecthelion's local Fountain Aura (heal_object), Rog's Wrath on Balrog entry, and North Fires."""
    sectors = ctx["sectors"]

    # 1A. Ecthelion's Royal Fountain Water Damage against Balrogs/Gothmog (P7 military units only)
    fx1, fy1, fx2, fy2 = sectors["royal_fountain"]
    t_fountain_weaken = tm.add_trigger(
        name="Aura_Fountain_Weaken_Balrogs",
        enabled=True,
        looping=True,
    )
    safe_call(t_fountain_weaken.new_condition.timer, timer=5)
    safe_call(
        t_fountain_weaken.new_condition.objects_in_area,
        source_player=PlayerId.SEVEN,
        object_type=OBJECT_TYPE_MILITARY,
        area_x1=fx1,
        area_y1=fy1,
        area_x2=fx2,
        area_y2=fy2,
        quantity=1,
    )
    safe_call(
        t_fountain_weaken.new_effect.damage_object,
        source_player=PlayerId.SEVEN,
        area_x1=fx1,
        area_y1=fy1,
        area_x2=fx2,
        area_y2=fy2,
        quantity=140,
    )

    # 1B. Local Royal Fountain Healing Aura: uses native heal_object every 4s for military units in the basin
    # (Works for both initial and future spawned units, strictly local to the fountain, never overheals!)
    t_fountain_heal = tm.add_trigger(
        name="Aura_Fountain_Local_Heal_Allies",
        enabled=True,
        looping=True,
    )
    safe_call(t_fountain_heal.new_condition.timer, timer=4)
    for p_id in HUMAN_PLAYERS:
        safe_call(
            t_fountain_heal.new_effect.heal_object,
            source_player=p_id,
            object_type=OBJECT_TYPE_MILITARY,
            area_x1=fx1,
            area_y1=fy1,
            area_x2=fx2,
            area_y2=fy2,
            quantity=BALANCE["fountain_local_heal_hp"],
        )

    # When Ecthelion personally stands at the Royal Fountain, he empowers its local waters (+35 extra heal & +80 P7 dmg)
    t_fountain_blessing = tm.add_trigger(
        name="Aura_Fountain_Ecthelion_Blessing",
        enabled=True,
        looping=False,
    )
    safe_call(
        t_fountain_blessing.new_condition.objects_in_area,
        source_player=PlayerId.TWO,
        object_list=HERO_ECTHELION_ID,
        area_x1=fx1,
        area_y1=fy1,
        area_x2=fx2,
        area_y2=fy2,
        quantity=1,
    )
    t_fountain_empowered = tm.add_trigger(
        name="Aura_Fountain_Empowered_Loop",
        enabled=False,
        looping=True,
    )
    safe_call(t_fountain_empowered.new_condition.timer, timer=4)
    for p_id in HUMAN_PLAYERS:
        safe_call(
            t_fountain_empowered.new_effect.heal_object,
            source_player=p_id,
            object_type=OBJECT_TYPE_MILITARY,
            area_x1=fx1,
            area_y1=fy1,
            area_x2=fx2,
            area_y2=fy2,
            quantity=35,
        )
    safe_call(
        t_fountain_blessing.new_effect.activate_trigger,
        trigger_id=t_fountain_empowered.trigger_id,
    )
    add_chat_and_flare(
        t_fountain_blessing,
        "<AQUA>[Muzyka Wody - P2] Ecthelion wzmocnil lokalna aure Fontanny Krolewskiej (+65 HP leczenia co 4s w basenie fontanny)!",
        61,
        61,
    )

    # 2. North Quarter Fire Hazard (Damages units in north_fire_zone until P2 opens the Aqueduct)
    nx1, ny1, nx2, ny2 = sectors["north_fire_zone"]
    t_north_fire = tm.add_trigger(
        name="Hazard_North_Avenue_Fires",
        enabled=True,
        looping=True,
    )
    safe_call(t_north_fire.new_condition.timer, timer=4)
    for p_id in HUMAN_PLAYERS:
        safe_call(
            t_north_fire.new_effect.damage_object,
            source_player=p_id,
            area_x1=nx1,
            area_y1=ny1,
            area_x2=nx2,
            area_y2=ny2,
            quantity=18,
        )
    ctx["north_fire_trigger_id"] = t_north_fire.trigger_id

    # 3. P1 House of the Hammer: Wrath of Rog activates ONLY when a Balrog (P7 military unit) enters Gondolin!
    t_rog_wrath = tm.add_trigger(
        name="Aura_Rog_Wrath_Against_Balrogs",
        enabled=True,
        looping=False,
    )
    safe_call(
        t_rog_wrath.new_condition.objects_in_area,
        source_player=PlayerId.SEVEN,
        object_type=OBJECT_TYPE_MILITARY,
        area_x1=16,
        area_y1=16,
        area_x2=104,
        area_y2=114,
        quantity=1,
    )
    for u_id in (HERO_ROG_ID, UNIT_HAMMER_SMITH_ID):
        safe_call(
            t_rog_wrath.new_effect.modify_attribute,
            source_player=PlayerId.ONE,
            object_list_unit_id=u_id,
            object_attributes=ATTR_ATTACK,
            operation=Operation.ADD,
            armour_attack_class=ARMOR_CLASS_MELEE,
            armour_attack_quantity=6,
        )
    add_chat_and_flare(
        t_rog_wrath,
        "<BLUE>[Gniew Domu Mlota] Balrog przekroczyl mury Gondolinu! Widok demona budzi furie kowali Roga (+6 Ataku)!",
    )


def _setup_iron_dragon_corridor_spawners(tm: Any, ctx: dict[str, Any]) -> None:
    """Spawn P6 Iron Dragons in North & East Avenues and loop Orc drops filtered strictly by ENEMY_IRON_DRAGON_RAM_ID."""
    t_spawn_dragons = tm.add_trigger(
        name="P6_Spawn_Iron_Dragons_Phase1",
        enabled=True,
        looping=False,
    )
    safe_call(t_spawn_dragons.new_condition.timer, timer=15)

    dragon_spawns: list[tuple[int, int, int, int, int]] = [
        (ENEMY_IRON_DRAGON_RAM_ID, 61, 108, 61, 78),
        (ENEMY_FIRE_DRAKE_ID, 59, 108, 61, 78),
        (ENEMY_FIRE_DRAKE_ID, 63, 108, 61, 78),
        (ENEMY_IRON_DRAGON_RAM_ID, 98, 63, 76, 63),
        (ENEMY_FIRE_DRAKE_ID, 98, 61, 76, 63),
    ]
    for u_id, sx, sy, tx, ty in dragon_spawns:
        safe_call(
            t_spawn_dragons.new_effect.create_object,
            source_player=PlayerId.SIX,
            object_list_unit_id=u_id,
            location_x=sx,
            location_y=sy,
        )
        safe_call(
            t_spawn_dragons.new_effect.attack_move,
            source_player=PlayerId.SIX,
            object_list_unit_id=u_id,
            area_x1=sx - 3,
            area_y1=sy - 3,
            area_x2=sx + 3,
            area_y2=sy + 3,
            location_x=tx,
            location_y=ty,
        )
    apply_unit_lore_name(t_spawn_dragons, PlayerId.SIX, ENEMY_IRON_DRAGON_RAM_ID)
    apply_unit_lore_name(t_spawn_dragons, PlayerId.SIX, ENEMY_FIRE_DRAKE_ID)

    add_chat_and_flare(
        t_spawn_dragons,
        "<ORANGE>[Zelazne Smoki Morgotha] Pancerne machiny P6 wtoczyly sie w Aleje Polnocna i Wschodnia! Zniszczcie je, aby zatrzymac zrzuty Orkow!",
        61,
        106,
    )

    corridors = ctx["dragon_corridors"]
    for ave_name, zones in corridors.items():
        for idx, (zx1, zy1, zx2, zy2) in enumerate(zones):
            cx = (zx1 + zx2) // 2
            cy = (zy1 + zy2) // 2
            t_drop = tm.add_trigger(
                name=f"P6_Dragon_Drop_{ave_name}_Z{idx}",
                enabled=True,
                looping=True,
            )
            safe_call(t_drop.new_condition.timer, timer=32)
            # Filter strictly by ENEMY_IRON_DRAGON_RAM_ID so P6 buildings or minor units never trigger Orc drops!
            safe_call(
                t_drop.new_condition.objects_in_area,
                source_player=PlayerId.SIX,
                object_list=ENEMY_IRON_DRAGON_RAM_ID,
                area_x1=zx1,
                area_y1=zy1,
                area_x2=zx2,
                area_y2=zy2,
                quantity=1,
            )
            for i in range(5):
                safe_call(
                    t_drop.new_effect.create_object,
                    source_player=PlayerId.FIVE,
                    object_list_unit_id=ENEMY_ORC_INFANTRY_ID,
                    location_x=cx + (i % 3) - 1,
                    location_y=cy + (i // 3) - 1,
                )
            for i in range(2):
                safe_call(
                    t_drop.new_effect.create_object,
                    source_player=PlayerId.FIVE,
                    object_list_unit_id=ENEMY_ORC_BRUTE_ID,
                    location_x=cx + i,
                    location_y=cy + 1,
                )
                safe_call(
                    t_drop.new_effect.create_object,
                    source_player=PlayerId.FIVE,
                    object_list_unit_id=ENEMY_ORC_CROSSBOW_ID,
                    location_x=cx - i,
                    location_y=cy - 1,
                )
            for u_id in (ENEMY_ORC_INFANTRY_ID, ENEMY_ORC_BRUTE_ID, ENEMY_ORC_CROSSBOW_ID):
                apply_unit_lore_name(t_drop, PlayerId.FIVE, u_id)
            safe_call(
                t_drop.new_effect.attack_move,
                source_player=PlayerId.FIVE,
                area_x1=zx1,
                area_y1=zy1,
                area_x2=zx2,
                area_y2=zy2,
                location_x=61,
                location_y=63,
            )


def setup_init_auras_and_mechanics(scenario: Any, ctx: dict[str, Any]) -> None:
    """Entry point to configure 0:01/0:03 initialization, hero/retinue scaling, auras, and Iron Dragons."""
    tm = scenario.trigger_manager
    _setup_t_init_and_unit_scaling(tm, ctx)
    _setup_special_auras_and_hazards(tm, ctx)
    _setup_iron_dragon_corridor_spawners(tm, ctx)
