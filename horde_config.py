from pathlib import Path

from AoE2ScenarioParser.datasets.units import UnitInfo


TREE_OAK_ID = 349


TREE_PINE_ID = 350


ROCK_CLIFF_ID = 623


RELIC_ID = 285


MAP_REVEALER_ID = 837


FLARE_UNIT_ID = 112


TORCH_ID = 499


FEITORIA_ID = 1021


KREPOST_ID = 1251


FORTIFIED_PALISADE_ID = 119


PALISADE_GATE_SW_NE_ID = 789


PALISADE_GATE_NW_SE_ID = 793


IMAM_UNIT_ID = 842


SIEGE_ONAGER_ID = 588


PETARD_ID = 440


FLAMING_CAMEL_ID = 1263


ELITE_BERSERK_ID = 694


ELITE_BATTLE_ELEPHANT_ID = 1134


HUSSAR_ID = 441


TERRAIN_WATER = 1


TERRAIN_SHALLOWS = 4


RES_FOOD = 0


RES_WOOD = 1


RES_STONE = 2


RES_GOLD = 3


RES_BONUS_POP_CAP = 32


ATTR_HIT_POINTS = 0


ATTR_LINE_OF_SIGHT = 1


ATTR_MOVEMENT_SPEED = 5


ATTR_ARMOR = 8


ATTR_ATTACK = 9


ATTR_ATTACK_RELOAD_TIME = 10


ATTR_MAXIMUM_RANGE = 12


ATTR_WORK_RATE = 13


ATTR_MINIMUM_RANGE = 20


ATTR_BLAST_WIDTH = 22


ATTR_SEARCH_RADIUS = 23


ATTR_HERO_STATUS = 40


ATTR_REGENERATION_RATE = 109


TECH_CARTOGRAPHY = 19


TECH_FAITH = 45


TECH_FEUDAL_AGE = 101


TECH_CASTLE_AGE = 102


TECH_IMPERIAL_AGE = 103


TECH_FORGING = 67


TECH_IRON_CASTING = 68


TECH_BLAST_FURNACE = 75


TECH_SCALE_MAIL = 74


TECH_CHAIN_MAIL = 76


TECH_PLATE_MAIL = 77


TECH_SQUIRES = 215


TECH_SCALE_BARDING = 81


TECH_CHAIN_BARDING = 82


TECH_PLATE_BARDING = 80


TECH_BLOODLINES = 435


TECH_HUSBANDRY = 39


TECH_FLETCHING = 199


TECH_BODKIN_ARROW = 200


TECH_BRACER = 201


TECH_BALLISTICS = 93


TECH_CHEMISTRY = 47


TECH_THUMB_RING = 437


TECH_SIEGE_ENGINEERS = 377


def populate_ingame_scenario_descriptions(scenario):
    mm_msg = getattr(scenario, "message_manager", None)
    if mm_msg is None:
        return

    instructions_text = (
        "KRONIKI RUBIEZY: HORDA I EKSPEDYCJE (v6.2 - 4P Co-op)\n\n"
        "SANKTUARIUM BALANSU (Wspolrzedne 6, 150 w zachodnim lesie):\n"
        "- Gracz 1 posiada odizolowanego Inzyniera Balansu (Krola) na (6, 150).\n"
        "- Wejscie Krolem na GORNA flage (6, 146) ZWIEKSZA trudnosc (+25% liczebnosci fal, +15 HP, +2 Ataku wroga).\n"
        "- Wejscie Krolem na DOLNA flage (6, 154) ZMNIEJSZA trudnosc (-20% liczebnosci fal, -15% HP wroga).\n"
        "- Po kazdej zmianie Krol wraca na srodek, a czat wypisuje numer korekty!\n\n"
        "SZLAK HANDLOWY I PLAC GRACZY (Lewy dolny rog mapy x=2..24, y=176..198):\n"
        "- W lewym dolnym rogu bazy znajduje sie duzy, czysty Plac pod Targowiska graczy.\n"
        "- Zburzenie Q1 (Karawanseraj) stawia pojedyncze Targowisko sojusznicze w prawym rogu (195, 194) oraz buduje Mur Obronny z Basztami wzdluz 10-kratkowego korytarza handlowego!\n\n"
        "ZASADY ROZGRYWKI (Horyzont 60-90 minut):\n"
        "- Fala 1 w 8:30 (bez taranow), Fala 2 w 13:00 (z taranem/mangonelem, bez mutantow), Fala 3 w 18:00, kolejne co 5,5 min.\n"
        "- Od 45. minuty (Fale 8-14) co druga fala wysyla szturm na SZLAK HANDLOWY, a w Falach 9 i 12 Onagery WYRABUJA PRZESIEKI W LESIE!\n"
    )

    hints_text = (
        "BESTIARIUSZ HORDY (WYSPECJALIZOWANE JEDNOSTKI Z POSWIATA BOHATERA):\n"
        "1. Taran-Zolw / Zelazny Slon (P8 - Tank): 1450 HP, +10/+12 pancerza, odporny na konwersje. Zadaje tylko 3 dmg jednostkom, ale +220 dmg budynkom!\n"
        "2. Szakale Dywersyjne (Huzarzy P7 - Eco-Raiders): Szybkosc 1.62, +6 pancerza na strzaly, tylko 2 ataku. Wjezdzaja pod TC atakowac chlopow!\n"
        "3. Arcymag Tarczy (Imam P7 - Globalny Support): W promieniu 25 kratek przed Brama Centralna daje +30/+30 Pancerza i leczy (+15 HP/3s) WSZYSTKIE frakcje Hordy (P5-P8)! Ma 240 HP i regeneracje 5 HP/s.\n"
        "4. Mozdzierz Oblezniczy (Onager P6): 350 HP, 21 zasiegu, wybuch co 10s, MARTWA STREFA 6 kratek.\n"
        "5. Snajperzy (Janczarzy P6): 90 HP, 19 zasiegu, ~107 dmg w 1 cel.\n"
        "6. Berserkerzy i Kamikaze (P5): Szybkie jednostki szturmowe o zerowym pancerzu na strzaly.\n"
    )

    scouts_text = (
        "RAPORT ZWIADOWCZY - 4 QUESTY I 6 SETTLEMENTOW:\n"
        "- Q1 Karawanseraj (154, 190): Buduje Kamienny Mur Handlowy i stawia sojuszniczy Market w prawym rogu (195, 194), daje +30 Popu i +20% szybszych Wiesniakow.\n"
        "- Q2 Klif Artylerii (28, 32): Balistyka, Chemia, +2 Zasiegu strzelcow, +12% szybkosci jazdy.\n"
        "- Q3 Skarbiec (142, 118): +20 Popu i duzy staly dochod co minute (+250F, +250W, +200G, +40S).\n"
        "- Q4 Krwawy Oltarz (105, 20): +30% HP armii, +2/+2 pancerza i +40% szybsza produkcja.\n"
    )

    if hasattr(mm_msg, "instructions"):
        mm_msg.instructions = instructions_text
    if hasattr(mm_msg, "hints"):
        mm_msg.hints = hints_text
    if hasattr(mm_msg, "scouts"):
        mm_msg.scouts = scouts_text
    if hasattr(mm_msg, "history"):
        mm_msg.history = f"{instructions_text}\n{hints_text}"


def find_scenario_folder() -> Path:
    aoe_base = Path.home() / "Games" / "Age of Empires 2 DE"
    if aoe_base.exists():
        for folder in aoe_base.glob("*/resources/_common/scenario"):
            if (folder / "template.aoe2scenario").exists():
                return folder
        for folder in aoe_base.glob("*/resources/_common/scenario"):
            if folder.parent.parent.parent.name != "0":
                return folder
    return Path(__file__).parent


SCENARIO_FOLDER = find_scenario_folder()


INPUT_TEMPLATE = SCENARIO_FOLDER / "template.aoe2scenario"


OUTPUT_SCENARIO = SCENARIO_FOLDER / "Kroniki_Rubiezy_Horda_Coop.aoe2scenario"


MAP_SIZE = 200


BALANCE = {
    "wave1_sec": 510,                     # 8:30
    "wave2_sec": 780,                     # 13:00
    "wave3_sec": 1080,                    # 18:00
    "wave_interval_sec": 330,             # Co 5,5 minuty (330s)

    "escalation_start_sec": 1200,         # Od 20:00 (Bieg 1): +5 HP i +1 Ataku co 5 minut
    "escalation_interval_sec": 300,
    "escalation_hp_add": 5,
    "escalation_atk_add": 1,
    "late_escalation_start_sec": 2700,    # Od 45:00 (Bieg 2): +9 HP i +1 Ataku co 5 minut
    "late_escalation_hp_add": 9,
    "endgame_escalation_start_sec": 3300, # Od 55:00 (Bieg 3): +10 HP i +2 Ataku co 5 minut
    "endgame_escalation_hp_add": 10,

    "diff_step_up_hp": 15,
    "diff_step_up_atk": 2,

    "tank_hp": 1450,
    "tank_unit_atk": 3,
    "tank_bldg_bonus": 220,
    "tank_melee_armor": 10,
    "tank_pierce_armor": 12,
    "tank_speed": 0.52,

    "raider_hp": 95,
    "raider_speed": 1.62,
    "raider_atk": 2,
    "raider_pierce_armor": 6,

    "mage_hp": 240,
    "mage_melee_armor": 3,
    "mage_pierce_armor": 4,
    "mage_regen_per_min": 300,
    "mage_local_radius": 25,
    "mage_shield_armor": 30,
    "mage_aoe_heal_3s": 15,
    "mage_speed": 0.78,

    "mortar_hp": 350,
    "mortar_range": 21,
    "mortar_min_range": 6,
    "mortar_reload": 10.0,
    "mortar_blast_width": 2.6,
    "mortar_bonus_atk": 75,
    "mortar_speed": 0.42,

    "sniper_hp": 90,
    "sniper_range": 19,
    "sniper_bonus_atk": 85,
    "sniper_reload": 6.5,

    "berserk_hp": 185,
    "berserk_speed": 1.40,
    "berserk_bonus_atk": 12,
    "kamikaze_hp": 115,
    "kamikaze_speed": 1.50,
    "kamikaze_blast_width": 2.4,
    "kamikaze_bonus_atk": 95,

    "q1_bonus_pop": 30,
    "q3_bonus_pop": 20,
    "quest3_trickle": {"food": 250, "wood": 250, "gold": 200, "stone": 40},
    "human_start_res": {"food": 500, "wood": 600, "gold": 400, "stone": 300},
}


def get_wave_definitions() -> list[tuple]:
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
    return wave_definitions
