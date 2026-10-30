"""Configuration, constants, unit IDs, balance dictionary, and lore descriptions for Gondolin Co-op (Etap A)."""

from __future__ import annotations

from typing import Any

from AoE2ScenarioParser.datasets.players import PlayerId

MAP_SIZE: int = 240

# Genie Engine Resource IDs
RES_FOOD: int = 0
RES_WOOD: int = 1
RES_STONE: int = 2
RES_GOLD: int = 3
RES_BONUS_POP_CAP: int = 32

# Genie Engine Technology IDs
TECH_CARTOGRAPHY: int = 19
TECH_FEUDAL_AGE: int = 101
TECH_CASTLE_AGE: int = 102
TECH_IMPERIAL_AGE: int = 103
TECH_LOOM: int = 22
TECH_SQUIRES: int = 215
TECH_ARSON: int = 602
TECH_FLETCHING: int = 199
TECH_BODKIN_ARROW: int = 200
TECH_BRACER: int = 201
TECH_PADDED_ARCHER_ARMOR: int = 211
TECH_LEATHER_ARCHER_ARMOR: int = 212
TECH_RING_ARCHER_ARMOR: int = 219
TECH_FORGING: int = 67
TECH_IRON_CASTING: int = 68
TECH_BLAST_FURNACE: int = 75
TECH_SCALE_MAIL_ARMOR: int = 74
TECH_CHAIN_MAIL_ARMOR: int = 76
TECH_PLATE_MAIL_ARMOR: int = 77
TECH_SCALE_BARDING_ARMOR: int = 81
TECH_CHAIN_BARDING_ARMOR: int = 82
TECH_PLATE_BARDING_ARMOR: int = 80
TECH_BALLISTICS: int = 93
TECH_CHEMISTRY: int = 47

# Genie Engine Object Attributes
ATTR_HIT_POINTS: int = 0
ATTR_LINE_OF_SIGHT: int = 1
ATTR_MOVEMENT_SPEED: int = 5
ATTR_ARMOR: int = 8
ATTR_ATTACK: int = 9
ATTR_ATTACK_RELOAD_TIME: int = 10
ATTR_MAXIMUM_RANGE: int = 12
ATTR_WORK_RATE: int = 13
ATTR_MINIMUM_RANGE: int = 20
ATTR_BLAST_WIDTH: int = 22
ATTR_SEARCH_RADIUS: int = 23
ATTR_HERO_STATUS: int = 40
ATTR_REGENERATION_RATE: int = 109

# Armor Classes for modify_attribute
ARMOR_CLASS_INFANTRY: int = 1
ARMOR_CLASS_PIERCE: int = 3
ARMOR_CLASS_MELEE: int = 4
ARMOR_CLASS_BUILDING: int = 11
ARMOR_CLASS_RAM: int = 17

# Special Utility & Environment Object IDs
MAP_REVEALER_ID: int = 837
FLARE_UNIT_ID: int = 112
ROCK_CLIFF_ID: int = 623
SEA_ROCKS_ID: int = 389
FIRE_TOWER_ID: int = 190
FLAME_EFFECT_ID: int = 303
TORCH_ID: int = 499
STATUE_ID: int = 817
FLAG_A_ID: int = 600
OAK_TREE_ID: int = 349
PINE_TREE_ID: int = 350
CYPRESS_TREE_ID: int = 1347
OLIVE_TREE_ID: int = 1349

# Flying Eye-Candy IDs (Thorondor's Eagles visual layer)
FALCON_ID: int = 96
MACAW_ID: int = 816
VULTURE_ID: int = 1305

# Safe Building IDs (Strictly no MONUMENT=596 or WONDER=276)
FEITORIA_ID: int = 1021
KREPOST_ID: int = 1251
CASTLE_ID: int = 82
KEEP_ID: int = 235
GUARD_TOWER_ID: int = 234
OUTPOST_ID: int = 598
BLACKSMITH_ID: int = 103
UNIVERSITY_ID: int = 209
MONASTERY_ID: int = 104
MARKET_ID: int = 84
TOWN_CENTER_ID: int = 109
BARRACKS_ID: int = 12
ARCHERY_RANGE_ID: int = 87
STABLE_ID: int = 101
SIEGE_WORKSHOP_ID: int = 49
HOUSE_ID: int = 70
MILL_ID: int = 68
LUMBER_CAMP_ID: int = 562
MINING_CAMP_ID: int = 584
PAVILION_ID: int = 626
FORTIFIED_WALL_ID: int = 155
CITY_GATE_SW_NE_ID: int = 64
CITY_GATE_NW_SE_ID: int = 88
FORTIFIED_PALISADE_ID: int = 119
PALISADE_GATE_X_ID: int = 789
PALISADE_GATE_Y_ID: int = 793

# Hero Unit IDs (Tracked strictly by object_list_unit_id + source_player, NEVER by reference_id!)
HERO_TUOR_ID: int = 426  # Harald Hardraada (Great Axe Dramborleg)
HERO_ROG_ID: int = 1066  # Edward Longshanks / Heavy Warlord
HERO_ECTHELION_ID: int = 168  # Belisarius / Silver Lord of the Fountain
HERO_EGALMOTH_ID: int = 682  # Henry V / Lord of the Heavenly Arch
HERO_GLORFINDEL_ID: int = 172  # La Hire / Golden-haired Lord with broadsword
HERO_DUILIN_ID: int = 428  # Hrolf the Ganger / Swallow Sniper Captain
HERO_IDRIL_ID: int = 1292  # Queen (Idril Celebrindal)
HERO_GALDOR_ID: int = 636  # Guy Josselyne / Tall Lord of the Tree
HERO_EARENDIL_ID: int = 430  # Joan the Maid (Foot noble ward - replaces invalid 831 Turtle Ship)
HERO_SALGANT_ID: int = 642  # William the Conqueror (Mounted Lord of the Harp)
SANCTUARY_KING_ID: int = 434  # King unit isolated inside the Balance Sanctuary

# Player Retinue Unit IDs
# P1: House of the Wing & House of the Hammer of Wrath
UNIT_HAMMER_SMITH_ID: int = 1703  # Elite Obuch (strips enemy armor with warhammers)
UNIT_WING_GUARD_ID: int = 693  # Elite Berserk (heavy axe infantry)
UNIT_WING_CHAMPION_ID: int = 567  # Champion

# P2: House of the Fountain & House of the Heavenly Arch
UNIT_FOUNTAIN_GUARD_ID: int = 1661  # Elite Serjeant (silver shield infantry)
UNIT_FOUNTAIN_HALB_ID: int = 359  # Halberdier
UNIT_ARCH_LONGBOW_ID: int = 530  # Elite Longbowman
UNIT_ARCH_RATTAN_ID: int = 1130  # Elite Rattan Archer

# P3: House of the Golden Flower & House of the Swallow
UNIT_FLOWER_BLADE_ID: int = 882  # Condottiero (fast shock infantry)
UNIT_FLOWER_CAV_ID: int = 569  # Paladin (mounted vanguard)
UNIT_SWALLOW_SNIPER_ID: int = 469  # Elite Genoese Crossbowman
UNIT_HARP_HEALER_ID: int = 125  # Monk (heals allies)

# P4: House of the Tree & Wardens of the Secret Way
UNIT_TREE_PIKE_ID: int = 1699  # Flemish Militia (heavy polearm infantry)
UNIT_TREE_SLINGER_ID: int = 185  # Slinger (anti-infantry ranged support)
UNIT_IDRIL_SAPPER_ID: int = 440  # Petard (demolition engineer)
UNIT_REFUGEE_CART_ID: int = 128  # Trade Cart Empty (Mithril / Relic convoy)
UNIT_REFUGEE_CIV_ID: int = 293  # Female Villager / Noldor Citizen (Gaia/P4)
UNIT_EAGLE_VANGUARD_ID: int = 752  # Elite Eagle Warrior (Thorondor's Ground Strike)

# Primary frontline unit per human player (used for clean object_list filtering in encounters & soft-cap)
PRIMARY_RETINUE_UNIT_BY_PLAYER: dict[PlayerId, int] = {
    PlayerId.ONE: UNIT_HAMMER_SMITH_ID,
    PlayerId.TWO: UNIT_FOUNTAIN_GUARD_ID,
    PlayerId.THREE: UNIT_FLOWER_BLADE_ID,
    PlayerId.FOUR: UNIT_TREE_PIKE_ID,
}

SECONDARY_RETINUE_UNIT_BY_PLAYER: dict[PlayerId, int] = {
    PlayerId.ONE: UNIT_WING_GUARD_ID,
    PlayerId.TWO: UNIT_ARCH_LONGBOW_ID,
    PlayerId.THREE: UNIT_SWALLOW_SNIPER_ID,
    PlayerId.FOUR: UNIT_TREE_SLINGER_ID,
}

# All 9 Noldor Heroes tracked by the 3 Seals of Turgon (player, hero_id, guard_unit_id, display_short_name)
TRACKED_NOLDOR_HEROES: list[tuple[PlayerId, int, int, str]] = [
    (PlayerId.ONE, HERO_TUOR_ID, UNIT_HAMMER_SMITH_ID, "Tuor"),
    (PlayerId.ONE, HERO_ROG_ID, UNIT_HAMMER_SMITH_ID, "Rog"),
    (PlayerId.TWO, HERO_ECTHELION_ID, UNIT_FOUNTAIN_GUARD_ID, "Ecthelion"),
    (PlayerId.TWO, HERO_EGALMOTH_ID, UNIT_ARCH_LONGBOW_ID, "Egalmoth"),
    (PlayerId.THREE, HERO_GLORFINDEL_ID, UNIT_FLOWER_BLADE_ID, "Glorfindel"),
    (PlayerId.THREE, HERO_DUILIN_ID, UNIT_SWALLOW_SNIPER_ID, "Duilin"),
    (PlayerId.FOUR, HERO_IDRIL_ID, UNIT_TREE_PIKE_ID, "Idril Celebrindal"),
    (PlayerId.FOUR, HERO_GALDOR_ID, UNIT_TREE_PIKE_ID, "Galdor"),
    (PlayerId.FOUR, HERO_EARENDIL_ID, UNIT_TREE_PIKE_ID, "Maly Earendil"),
]

# Enemy Unit IDs (P5: Angband Horde, P6: Iron Dragons, P7: Balrogs, P8: Maeglin's Traitors)
ENEMY_ORC_INFANTRY_ID: int = 1124  # Elite Karambit Warrior (swarming Orcs)
ENEMY_ORC_BRUTE_ID: int = 473  # Two-Handed Swordsman (Uruk heavy infantry)
ENEMY_ORC_ARCHER_ID: int = 4  # Bowman / Orc Crossbowman
ENEMY_ORC_CROSSBOW_ID: int = 24  # Crossbowman
ENEMY_DIRE_WOLF_ID: int = 89  # Dire Wolf
ENEMY_WARG_RIDER_ID: int = 756  # Elite Tarkhan (torch-wielding wolf/cavalry raider)

ENEMY_IRON_DRAGON_RAM_ID: int = 548  # Siege Ram (armored transport dragon)
ENEMY_FIRE_DRAKE_ID: int = 188  # Flamethrower (fire-breathing Uruloki machine)
ENEMY_HEAVY_SCORPION_ID: int = 542  # Heavy Scorpion

ENEMY_BALROG_BOSS_ID: int = 1737  # Elite Urumi Swordsman (whip of fire & splash damage)
ENEMY_GOTHMOG_ID: int = 1713  # Savar / High Lord of Balrogs

ENEMY_MOLE_TRAITOR_ID: int = 878  # Elite Boyar (heavy dark armor with pick/axe)
ENEMY_MOLE_PIKE_ID: int = 532  # Elite Teutonic Knight (Maeglin's Royal Guard)
ENEMY_MAEGLIN_ID: int = 640  # Mordred / Traitor Prince of the Mole

# Canonical lore unit names for P1-P8 (applied to initial & dynamically spawned units)
UNIT_DISPLAY_NAMES: dict[int, str] = {
    HERO_TUOR_ID: "Tuor (Pan Domu Skrzydla)",
    HERO_ROG_ID: "Rog (Wodz Domu Mlota Gniewu)",
    HERO_ECTHELION_ID: "Ecthelion (Pan Domu Zrodla)",
    HERO_EGALMOTH_ID: "Egalmoth (Pan Niebianskiego Luku)",
    HERO_GLORFINDEL_ID: "Glorfindel (Pan Zlotego Kwiatu)",
    HERO_DUILIN_ID: "Duilin (Wodz Domu Jaskolki)",
    HERO_IDRIL_ID: "Idril Celebrindal (Krolewna Gondolinu)",
    HERO_GALDOR_ID: "Galdor (Pan Domu Drzewa)",
    HERO_EARENDIL_ID: "Earendil (Dziedzic Gondolinu)",
    SANCTUARY_KING_ID: "Powiernik Sanktuarium Balansu",
    UNIT_HAMMER_SMITH_ID: "Kowal Mlota Gniewu",
    UNIT_WING_GUARD_ID: "Topornik Domu Skrzydla",
    UNIT_WING_CHAMPION_ID: "Miecznik Domu Skrzydla",
    UNIT_FOUNTAIN_GUARD_ID: "Srebrny Gwardzista Zrodla",
    UNIT_FOUNTAIN_HALB_ID: "Halabardnik Wielkiego Targu",
    UNIT_ARCH_LONGBOW_ID: "Lucznik Niebianskiego Luku",
    UNIT_ARCH_RATTAN_ID: "Strzelec Klejnotow Egalmotha",
    UNIT_FLOWER_BLADE_ID: "Wojownik Zlotego Kwiatu",
    UNIT_FLOWER_CAV_ID: "Jezdziec Domu Harfy",
    UNIT_SWALLOW_SNIPER_ID: "Strzelec Wyborowy Jaskolki",
    UNIT_HARP_HEALER_ID: "Uzdrowiciel Domu Harfy",
    UNIT_TREE_PIKE_ID: "Wlocznik Domu Drzewa",
    UNIT_TREE_SLINGER_ID: "Procarz Domu Drzewa",
    UNIT_IDRIL_SAPPER_ID: "Saper Tajemnej Sciezki",
    UNIT_REFUGEE_CART_ID: "Woz z Mithrilem z Kuzni Roga",
    UNIT_REFUGEE_CIV_ID: "Uchodzca z Gondolinu",
    UNIT_EAGLE_VANGUARD_ID: "Szpon Thorondora (Straz Orlow)",
    ENEMY_ORC_INFANTRY_ID: "Ork z Angbandu",
    ENEMY_ORC_BRUTE_ID: "Ciezki Uruk Morgotha",
    ENEMY_ORC_ARCHER_ID: "Lucznik Orkow",
    ENEMY_ORC_CROSSBOW_ID: "Kusznik z Angbandu",
    ENEMY_DIRE_WOLF_ID: "Wilk z Thangorodrimu",
    ENEMY_WARG_RIDER_ID: "Jezdziec Wargow",
    ENEMY_IRON_DRAGON_RAM_ID: "Zelazny Smok Morgotha",
    ENEMY_FIRE_DRAKE_ID: "Uruloki (Smok Ognisty)",
    ENEMY_HEAVY_SCORPION_ID: "Balista Obleznicza Angbandu",
    ENEMY_BALROG_BOSS_ID: "Balrog z Angbandu",
    ENEMY_GOTHMOG_ID: "Gothmog (Wladca Balrogow)",
    ENEMY_MOLE_TRAITOR_ID: "Gwardzista Domu Kreta (Zdrajca)",
    ENEMY_MOLE_PIKE_ID: "Pikinier Maeglina (Dom Kreta)",
    ENEMY_MAEGLIN_ID: "Maeglin Zdrajca (Ksiaze Domu Kreta)",
}

# Lists for safe uint8 modify_attribute (Rule 6: strictly separate melee class 4 and ranged class 3)
ENEMY_MELEE_UNITS: list[int] = [
    ENEMY_ORC_INFANTRY_ID,
    ENEMY_ORC_BRUTE_ID,
    ENEMY_DIRE_WOLF_ID,
    ENEMY_WARG_RIDER_ID,
    ENEMY_BALROG_BOSS_ID,
    ENEMY_GOTHMOG_ID,
    ENEMY_MOLE_TRAITOR_ID,
    ENEMY_MOLE_PIKE_ID,
    ENEMY_MAEGLIN_ID,
]

ENEMY_RANGED_UNITS: list[int] = [
    ENEMY_ORC_ARCHER_ID,
    ENEMY_ORC_CROSSBOW_ID,
    ENEMY_FIRE_DRAKE_ID,
    ENEMY_HEAVY_SCORPION_ID,
]

PLAYER_ALL_COMBAT_UNITS: list[int] = [
    HERO_TUOR_ID,
    HERO_ROG_ID,
    HERO_ECTHELION_ID,
    HERO_EGALMOTH_ID,
    HERO_GLORFINDEL_ID,
    HERO_DUILIN_ID,
    HERO_IDRIL_ID,
    HERO_GALDOR_ID,
    HERO_EARENDIL_ID,
    UNIT_HAMMER_SMITH_ID,
    UNIT_WING_GUARD_ID,
    UNIT_WING_CHAMPION_ID,
    UNIT_FOUNTAIN_GUARD_ID,
    UNIT_FOUNTAIN_HALB_ID,
    UNIT_ARCH_LONGBOW_ID,
    UNIT_ARCH_RATTAN_ID,
    UNIT_FLOWER_BLADE_ID,
    UNIT_FLOWER_CAV_ID,
    UNIT_SWALLOW_SNIPER_ID,
    UNIT_TREE_PIKE_ID,
    UNIT_TREE_SLINGER_ID,
    UNIT_EAGLE_VANGUARD_ID,
]

HUMAN_PLAYERS: list[PlayerId] = [
    PlayerId.ONE,
    PlayerId.TWO,
    PlayerId.THREE,
    PlayerId.FOUR,
]

AI_PLAYERS: list[PlayerId] = [
    PlayerId.FIVE,
    PlayerId.SIX,
    PlayerId.SEVEN,
    PlayerId.EIGHT,
]

# Master Closed-Loop Balance Dictionary
BALANCE: dict[str, Any] = {
    "starting_seals": 3,
    "out_of_combat_regen_per_min": 30,  # 0.5 HP/s passive recovery for Noldor units
    "hero_regen_per_min": 120,  # 2.0 HP/s regeneration for Heroes
    "fountain_ally_regen_bonus": 90,  # +1.5 HP/s regeneration near Royal Fountain (no overheal!)
    "seal_shield_regen_bonus": 240,  # +4.0 HP/s regeneration for 20s after consuming a Seal
    "soft_cap_primary_critical_max": 7,  # <= 7 primary units (~14 total) -> Critical Rescue Pack
    "soft_cap_primary_standard_max": 14,  # 8..14 primary units (~15..28 total) -> Standard Pack
    "soft_cap_primary_dominance_min": 15,  # >= 15 primary units (> 28 total) -> Dominance Bonus
    "mid_encounter_escalation_delay": 20,  # Seconds before checking if players crushed base wave
    "sanctuary_harder_hp_add": 20,
    "sanctuary_harder_atk_add": 2,
    "sanctuary_easier_hp_mult": 0.85,
    "glory_scores": {
        "refugee_group_saved": 150,
        "side_quest_completed": 300,
        "elite_ambush_defeated": 200,
        "seal_preserved_bonus": 500,
        "difficulty_plus_1": 1000,
        "difficulty_plus_2": 2000,
        "difficulty_minus_1": -500,
        "difficulty_minus_2": -1000,
    },
    "heroes": {
        HERO_TUOR_ID: {
            "name": "Tuor (Pan Domu Skrzydla)",
            "player": PlayerId.ONE,
            "hp": 1350,
            "atk": 38,
            "melee_armor": 7,
            "pierce_armor": 7,
            "speed": 1.25,
            "blast": 0.5,
        },
        HERO_ROG_ID: {
            "name": "Rog (Wodz Domu Mlota Gniewu)",
            "player": PlayerId.ONE,
            "hp": 1450,
            "atk": 44,
            "melee_armor": 8,
            "pierce_armor": 6,
            "speed": 1.20,
            "blast": 0.6,
        },
        HERO_ECTHELION_ID: {
            "name": "Ecthelion (Pan Domu Zrodla)",
            "player": PlayerId.TWO,
            "hp": 1300,
            "atk": 36,
            "melee_armor": 8,
            "pierce_armor": 8,
            "speed": 1.25,
            "blast": 0.4,
        },
        HERO_EGALMOTH_ID: {
            "name": "Egalmoth (Pan Niebianskiego Luku)",
            "player": PlayerId.TWO,
            "hp": 1050,
            "atk": 30,
            "melee_armor": 5,
            "pierce_armor": 7,
            "speed": 1.20,
            "blast": 0.0,
        },
        HERO_GLORFINDEL_ID: {
            "name": "Glorfindel (Pan Zlotego Kwiatu)",
            "player": PlayerId.THREE,
            "hp": 1350,
            "atk": 42,
            "melee_armor": 7,
            "pierce_armor": 7,
            "speed": 1.38,
            "blast": 0.5,
        },
        HERO_DUILIN_ID: {
            "name": "Duilin (Wodz Domu Jaskolki)",
            "player": PlayerId.THREE,
            "hp": 980,
            "atk": 34,
            "melee_armor": 4,
            "pierce_armor": 6,
            "speed": 1.35,
            "blast": 0.0,
        },
        HERO_IDRIL_ID: {
            "name": "Idril Celebrindal (Krolewna Gondolinu)",
            "player": PlayerId.FOUR,
            "hp": 1150,
            "atk": 28,
            "melee_armor": 6,
            "pierce_armor": 8,
            "speed": 1.30,
            "blast": 0.0,
        },
        HERO_GALDOR_ID: {
            "name": "Galdor (Pan Domu Drzewa)",
            "player": PlayerId.FOUR,
            "hp": 1350,
            "atk": 35,
            "melee_armor": 8,
            "pierce_armor": 7,
            "speed": 1.22,
            "blast": 0.4,
        },
        HERO_EARENDIL_ID: {
            "name": "Earendil (Dziedzic Gondolinu)",
            "player": PlayerId.FOUR,
            "hp": 650,
            "atk": 5,
            "melee_armor": 5,
            "pierce_armor": 8,
            "speed": 1.28,
            "blast": 0.0,
        },
    },
    "bosses": {
        ENEMY_MAEGLIN_ID: {
            "name": "Maeglin Zdrajca (Ksiaze Domu Kreta)",
            "hp": 2200,
            "atk": 32,
            "melee_armor": 6,
            "pierce_armor": 6,
        },
        ENEMY_GOTHMOG_ID: {
            "name": "Gothmog (Wladca Balrogow)",
            "hp": 4800,
            "atk": 55,
            "melee_armor": 14,
            "pierce_armor": 14,
        },
        ENEMY_BALROG_BOSS_ID: {
            "name": "Balrog z Angbandu",
            "hp": 2800,
            "atk": 42,
            "melee_armor": 10,
            "pierce_armor": 10,
        },
        ENEMY_IRON_DRAGON_RAM_ID: {
            "name": "Zelazny Smok Morgotha",
            "hp": 2400,
            "atk": 35,
            "melee_armor": 6,
            "pierce_armor": 18,
        },
        ENEMY_FIRE_DRAKE_ID: {
            "name": "Uruloki (Smok Ognisty)",
            "hp": 1450,
            "atk": 24,
            "melee_armor": 5,
            "pierce_armor": 10,
        },
    },
}


def get_retinue_configs() -> dict[PlayerId, list[tuple[int, int]]]:
    """Return initial squad composition (unit_id, count) for each of the 4 Noldor players."""
    return {
        PlayerId.ONE: [
            (UNIT_HAMMER_SMITH_ID, 14),
            (UNIT_WING_GUARD_ID, 12),
            (UNIT_WING_CHAMPION_ID, 6),
        ],
        PlayerId.TWO: [
            (UNIT_FOUNTAIN_GUARD_ID, 12),
            (UNIT_FOUNTAIN_HALB_ID, 6),
            (UNIT_ARCH_LONGBOW_ID, 10),
            (UNIT_ARCH_RATTAN_ID, 6),
        ],
        PlayerId.THREE: [
            (UNIT_FLOWER_BLADE_ID, 12),
            (UNIT_FLOWER_CAV_ID, 6),
            (UNIT_SWALLOW_SNIPER_ID, 10),
            (UNIT_HARP_HEALER_ID, 3),
        ],
        PlayerId.FOUR: [
            (UNIT_TREE_PIKE_ID, 16),
            (UNIT_TREE_SLINGER_ID, 10),
            (UNIT_IDRIL_SAPPER_ID, 4),
        ],
    }


def populate_ingame_scenario_descriptions(scenario: Any) -> None:
    """Populate Instructions, Hints, Scouts, and History tabs in the AoE2: DE briefing menu."""
    mm = scenario.message_manager

    mm.instructions = (
        "SILMARILLION: UPADEK GONDOLINU I ODWROT PRZEZ CRISTHORN (4P Co-op RPG)\n\n"
        "1. BRAK EKONOMII I ASYMETRIA 4 DOMOW:\n"
        "- P1 (Niebieski - Tuor i Rog): Ciezka piechota i kowale z mlotami zdzierajacymi pancerz. "
        "Niszczyciel Zelaznych Smokow. Tylko P1 uruchamia Krolewskie Kuznie (+statystyki dla wszystkich).\n"
        "- P2 (Czerwony - Ecthelion i Egalmoth): Wlocznicy i dalekosiezni lucznicy. "
        "Ecthelion otwiera sluzy akweduktu (gasi pozary u P3 i oslabia pancerz Balrogow).\n"
        "- P3 (Zielony - Glorfindel i Duilin): Szybka gwardia, uzdrowiciele i strzelcy wyborowi. "
        "Zajmowanie baszt i grani odslania mape i zasadzki wroga.\n"
        "- P4 (Zolty - Idril, Galdor i maly Earendil): Pikinierzy i saperzy. "
        "Otwiera tajne przejscia, wysadza podkopy i prowadzi uchodzcow.\n\n"
        "2. 9 BOHATEROW I 3 PIECZECIE REZERWY TURGONA:\n"
        "- Wszystkich 9 Bohaterow (Tuor, Rog, Ecthelion, Egalmoth, Glorfindel, Duilin, Idril, Galdor, Earendil) "
        "posiada regeneracje 2 HP/s, ale nie sa niesmiertelni.\n"
        "- Jesli ktorykolwiek z 9 Bohaterow zginie, druzyna zuzywa 1 Pieczec Rezerwy Turgona, a polegly bohater "
        "odradza sie z oddzialem ratunkowym i 20s premia regeneracji na Punkcie Zbornym aktualnej Fazy. "
        "Utrata wszystkich 3 Pieczeci i smierc kolejnego bohatera = Porazka.\n\n"
        "3. PUNKTY CHWALY (ZLOTO):\n"
        "- Zloto Gracza 1 mierzy Wasz wynik (High Score) za uratowanych mieszkancow, zadania i zachowane Pieczecie."
    )

    mm.hints = (
        "WSKAZOWKI TAKTYCZNE:\n"
        "1. ZELAZNE SMOKI (P6): Dopoki Zelazny Smok zyje w danej alei, co 30 sekund zrzuca nowe oddzialy Orkow. "
        "Uzyjcie topornikow Tuora i mlotow Roga (P1), aby szybko zniszczyc kadlub Smoka!\n"
        "2. WSPOLPRACA ZDALNA W FAZIE I: P4 jest odciety w dzielnicy Caragdur przez zdrajcow Maeglina (P8). "
        "P1 musi uderzyc na brame od poludnia. Jednoczesnie P2 powinien odbic Akwedukt, aby ugasic ogien przed P3.\n"
        "3. GOTHMOG I BALROGOWIE (P7): Na suchym ladzie maja ogromny pancerz. Zwabcie ich w wode Fontanny Krolewskiej "
        "lub zalanej fosy, albo uzyjcie mlotow Roga (Obuchow P1), ktore zdzieraja pancerz z kazdym uderzeniem.\n"
        "4. DWA SZLAKI PRZEZ TUMLADEN (FAZA II): Mozecie isc razem lub rozdzielic druzyne na Szlak Dolny (Koryto Rzeki - "
        "wysadzanie podkopow przez P4) oraz Szlak Gorny (Rownina - czyszczenie klifow nad glowami uchodzcow)."
    )

    mm.scouts = (
        "RAPORT ZWIADOWCOW:\n"
        "- Polnocne i Wschodnie mury Gondolinu pekaja pod naporem Zelaznych Smokow (P6 - Pomaranczowy) "
        "oraz hord Orkow i Wilkow z Angbandu (P5 - Turkusowy).\n"
        "- W centrum i na przeleczy czaja sie Balrogowie pod wodza Gothmoga (P7 - Szary).\n"
        "- Wewnatrz miasta wybuchl bunt! Ksiazeta Domu Kreta pod wodza Maeglina (P8 - Fioletowy) "
        "zamkneli bramy poludniowo-zachodnie i probuja porwac Idril oraz Earendila na skale Caragdur."
    )

    mm.history = (
        "KRONIKA PIERWSZEJ ERY - UPADEK GONDOLINU:\n"
        "Przez blisko piecset lat Ukryte Krolestwo krola Turgona trwalo bezpieczne za pierscieniem Gor Okreznych "
        "(Echoriath). Jednak zdrada Maeglina, siostrzenca krola, wydala tajemnice miasta Wladcy Ciemnosci. "
        "W noc swieta Tarnin Austa (Bramy Lata), gdy mieszkancy wypatrywali wschodu slonca na wschodnich murach, "
        "z polnocnych szczytow splynely ognie Morgotha..."
    )
