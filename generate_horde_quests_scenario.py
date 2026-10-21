import inspect
import math
from pathlib import Path

from AoE2ScenarioParser.datasets.buildings import BuildingInfo
from AoE2ScenarioParser.datasets.other import OtherInfo
from AoE2ScenarioParser.datasets.players import PlayerId
from AoE2ScenarioParser.datasets.terrains import TerrainId
from AoE2ScenarioParser.datasets.trigger_lists import DiplomacyState, Operation
from AoE2ScenarioParser.datasets.units import UnitInfo
from AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario

# Stałe ID obiektów i jednostek specjalnych w silniku AoE2: DE
TREE_OAK_ID = 349
TREE_PINE_ID = 350
ROCK_CLIFF_ID = 623
RELIC_ID = 285
MAP_REVEALER_ID = 837

# Unikalne budynki zastępujące Cudy (brak licznika 350 lat!) i startowe umocnienia przełęczy
FEITORIA_ID = 1021  # Serce Twierdzy Sojuszu (zamiast Wonder P3)
KREPOST_ID = 1251  # Skarbiec w Queście 3 (zamiast Wonder P8)
FORTIFIED_PALISADE_ID = 155  # Wzmocniona palisada na 3 przełęczach
PALISADE_GATE_SW_NE_ID = 792  # Brama palisadowa wzdłuż osi X (Brama Północna)
PALISADE_GATE_NW_SE_ID = (
    796  # Brama palisadowa wzdłuż osi Y (Brama Centralna i Wschodnia)
)

# 6 klas zmodyfikowanych jednostek Hordy
IMAM_UNIT_ID = 842  # Arcymag Tarczy (P7)
SIEGE_ONAGER_ID = 588  # Kolos Oblężniczy / Moździerz 22 zasięgu (P6)
PETARD_ID = 440  # Fanatyk Kamikaze (P5)
FLAMING_CAMEL_ID = 1263  # Płonący Wielbłąd Kamikaze (P5)
ELITE_BERSERK_ID = 694  # Szybki Berserker Szturmowy (P5)
ELITE_BATTLE_ELEPHANT_ID = 1134  # Tytan Hordy 1400 HP (P8)

TERRAIN_WATER = 1
TERRAIN_SHALLOWS = 4

RES_FOOD = 0
RES_WOOD = 1
RES_STONE = 2
RES_GOLD = 3

# Oficjalne ID atrybutów obiektów silnika Genie (AoE2: DE)
ATTR_HIT_POINTS = 0
ATTR_LINE_OF_SIGHT = 1
ATTR_MOVEMENT_SPEED = 5
ATTR_ARMOR = 8
ATTR_ATTACK = 9
ATTR_ATTACK_RELOAD_TIME = 10
ATTR_MAXIMUM_RANGE = 12
ATTR_WORK_RATE = 13
ATTR_BLAST_WIDTH = 22
ATTR_SEARCH_RADIUS = 23

# Technologie
TECH_CARTOGRAPHY = 19  # Darmowa Kartografia od 0:00 dla graczy P1-P4
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


def safe_call(func, **kwargs):
    sig = inspect.signature(func)
    valid_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
    return func(**valid_kwargs)


def safe_modify_attribute(
    trigger, source_player, unit_id, attr_id, operation, val, armor_class=None
):
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


def set_as_objective(trigger, text: str, order: int, is_header: bool = False):
    """
    UWAGA: Silnik AoE2: DE sortuje listę Objectives MALEJĄCO po `description_order`
    (wyższa wartość `order` wyświetla się wyżej na ekranie!).
    """
    if hasattr(trigger, "short_description"):
        trigger.short_description = text
    if hasattr(trigger, "display_on_screen"):
        trigger.display_on_screen = 1
    if hasattr(trigger, "description_order"):
        trigger.description_order = order
    if is_header and hasattr(trigger, "header"):
        trigger.header = 1


def send_highlight_chat(
    trigger,
    color_tag: str,
    message: str,
    flare_x: int | None = None,
    flare_y: int | None = None,
):
    for h_p in [PlayerId.ONE, PlayerId.TWO, PlayerId.THREE, PlayerId.FOUR]:
        safe_call(
            trigger.new_effect.send_chat,
            source_player=h_p,
            message=f"{color_tag}{message}",
        )
        if (
            flare_x is not None
            and flare_y is not None
            and hasattr(trigger.new_effect, "flare")
        ):
            safe_call(
                trigger.new_effect.flare,
                source_player=h_p,
                location_x=flare_x,
                location_y=flare_y,
            )


def populate_ingame_scenario_descriptions(scenario):
    """Wpisuje opis scenariusza, bestiariusz i nagrody bezpośrednio do zakładek menu w grze."""
    mm_msg = getattr(scenario, "message_manager", None)
    if mm_msg is None:
        return

    instructions_text = (
        "KRONIKI RUBIEZY: HORDA I EKSPEDYCJE (4P Co-op)\n\n"
        "ZASADY ROZGRYWKI:\n"
        "- Broncie 3 Przeleczy Twierdzy Sojuszu oraz Cytadeli Sojuszu (Feitorii w centrum).\n"
        "- Pierwsza fala uderza w 10:00, a kolejne co 3 minuty (po kazdej fali macie ~2,5 minuty Okna Ekspedycyjnego).\n"
        "- Od 14:00 co 4 minuty jednostki Hordy otrzymuja bonus +25 HP i +2 Ataku.\n"
        "- Zburzenie wszystkich 6 Settlementow Hordy konczy gre zwyciestwem!\n\n"
        "4 QUESTY POBOCZNE (Zburz budynek wroga, aby odebrac nagrode dla calej druzyny):\n"
        "- Q1 Karawanseraj (Poludnie - Targowisko): +500 Zlota, 3 Wozy Handlowe i bezpieczne Targowiska.\n"
        "- Q2 Klif Artylerii (Polnocny-Zachod - Uniwersytet): Darmowa Balistyka, Chemia, Siege Engineers oraz +4 Ataku i +12% szybkosci jazdy/strzelcow.\n"
        "- Q3 Skarbiec Krasnoludow (Wschod - Krepost za murami): +400 surowcow od reki ORAZ staly dochod +120 Zywnosci, +120 Drewna i +100 Zlota co minute.\n"
        "- Q4 Krwawy Oltarz (Polnoc - Klasztor): +50 Max HP dla Waszych jednostek i oslabienie Magow o 80%.\n"
    )

    hints_text = (
        "BESTIARIUSZ HORDY (6 ZMODYFIKOWANYCH JEDNOSTEK):\n"
        "1. Kolosy Obleznicze (Onagery P6): 22 zasiegu, 850 HP, ogromny wybuch, ale strzelaja co 10s. Unikaj salw i dobijaj jazda!\n"
        "2. Kamikaze (Petardy i Plonace Wielblady P5): Bardzo szybkie (1.65x), 220 HP, wybuchaja w murach i oddzialach.\n"
        "3. Berserkerzy Szturmowi (P5): Szybka piechota (320 HP, duzy atak wrecz, 0 pancerza na strzaly).\n"
        "4. Snajperzy (Janczarzy P6): 20 zasiegu, +110 ataku, 140 HP.\n"
        "5. Arcymagowie Tarczy (Imamowie P7): W promieniu 25 kratek przed Brama Centralna daja wojskom P7 +60 Pancerza i regeneracje. Zabij Maga, aby zdjac tarcze!\n"
        "6. Tytani Hordy (Slonie Bojowe P8): 1400 HP i tratowanie obszarowe (kontruj halabardami i mnichami).\n"
    )

    scouts_text = (
        "RAPORT ZWIADOWCZY - 6 SETTLEMENTOW HORDY:\n"
        "- Grade 1 Polnoc (76, 72) i Wschod (132, 152): Bliskie obozy. Zburzenie Wiezy usuwa z fal Berserkerow i jednostki Kamikaze.\n"
        "- Grade 2 Akademia Artylerii P6 (68, 34): Zburzenie Zamku trwale usuwa z gry Snajperow i Kolosy Obleznicze!\n"
        "- Grade 2 Klasztor Arcymagow P7 (148, 72): Zburzenie Zamku trwale usuwa z gry Magow Niesmiertelnosci i Szamanow!\n"
        "- Grade 3 Cytadele Hordy P8 (142, 24) oraz (176, 56): Glowne bazy Tytanow Sloniowych.\n"
        "UWAGA: Zburzenie kazdego Settlementu daje +500 Zlota i Zywnosci, ale pozostale obozy wpadaja w Furie (+30 HP, +2 Ataku i fala odwetowa)!"
    )

    for attr_name, content in [
        ("instructions", instructions_text),
        ("hints", hints_text),
        ("scouts", scouts_text),
        ("history", instructions_text + "\n" + hints_text),
    ]:
        if hasattr(mm_msg, attr_name):
            try:
                setattr(mm_msg, attr_name, content)
            except Exception:
                pass


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
    "first_wave_sec": 600,  # 10:00 - Pierwsza fala
    "wave_interval_sec": 180,  # Co 3 minuty kolejna fala
    "escalation_interval_sec": 240,  # Co 4 minuty OD pierwszego ataku (14:00, 18:00...)
    "sniper_range": 20,
    "sniper_bonus_atk": 110,
    "sniper_reload": 6.0,
    "sniper_hp": 140,
    "colossus_hp": 850,
    "colossus_range": 22,
    "colossus_reload": 10.0,
    "colossus_blast_width": 2.8,
    "colossus_bonus_atk": 90,
    "colossus_speed": 0.40,
    "kamikaze_hp": 220,
    "kamikaze_speed_mult": 1.65,
    "kamikaze_blast_width": 2.5,
    "kamikaze_bonus_atk": 120,
    "berserk_hp": 320,
    "berserk_speed": 1.45,
    "berserk_bonus_atk": 18,
    "titan_hp": 1400,
    "titan_bonus_atk": 25,
    "titan_blast_width": 1.5,
    "mage_hp": 550,
    "mage_local_radius": 25,
    "mage_shield_armor": 60,
    "mage_local_heal_2s": 100,
    "quest3_trickle": {"food": 120, "wood": 120, "gold": 100},
    "human_start_res": {"food": 500, "wood": 600, "gold": 400, "stone": 300},
}


class SafeMapGrid:
    def __init__(self, size: int):
        self.size = size
        self.occupied_tiles: set[tuple[int, int]] = set()
        self.no_tree_zones: set[tuple[int, int]] = set()
        self.elev: list[list[int]] = [[0 for _ in range(size)] for _ in range(size)]

    def in_bounds(self, x: int, y: int, margin: int = 1) -> bool:
        return margin <= x < self.size - margin and margin <= y < self.size - margin

    def mark_no_trees(self, cx: int, cy: int, radius: int):
        for x in range(max(0, cx - radius), min(self.size, cx + radius + 1)):
            for y in range(max(0, cy - radius), min(self.size, cy + radius + 1)):
                self.no_tree_zones.add((x, y))

    def place_building(
        self,
        um,
        player: PlayerId,
        building_id: int,
        cx: int,
        cy: int,
        size_tiles: int,
        no_tree_margin: int = 3,
    ):
        half = size_tiles // 2
        if size_tiles % 2 == 0:
            x_range = range(cx - half, cx + half)
            y_range = range(cy - half, cy + half)
            bx, by = float(cx), float(cy)
        else:
            x_range = range(cx - half, cx + half + 1)
            y_range = range(cy - half, cy + half + 1)
            bx, by = cx + 0.5, cy + 0.5

        for x in x_range:
            for y in y_range:
                self.occupied_tiles.add((x, y))
        self.mark_no_trees(cx, cy, half + no_tree_margin)
        return um.add_unit(player=player, unit_const=building_id, x=bx, y=by)

    def place_unit(
        self,
        um,
        player: PlayerId,
        unit_id: int,
        x: int,
        y: int,
        no_tree_margin: int = 2,
    ):
        for r in range(6):
            for dx in range(-r, r + 1):
                for dy in range(-r, r + 1):
                    if abs(dx) != r and abs(dy) != r:
                        continue
                    nx, ny = x + dx, y + dy
                    if self.in_bounds(nx, ny) and (nx, ny) not in self.occupied_tiles:
                        self.occupied_tiles.add((nx, ny))
                        if no_tree_margin > 0:
                            self.mark_no_trees(nx, ny, no_tree_margin)
                        return um.add_unit(
                            player=player, unit_const=unit_id, x=nx + 0.5, y=ny + 0.5
                        )
        return None

    def place_wall_tile(self, um, player: PlayerId, wall_id: int, x: int, y: int):
        if self.in_bounds(x, y, margin=0) and (x, y) not in self.occupied_tiles:
            self.occupied_tiles.add((x, y))
            self.mark_no_trees(x, y, 1)
            return um.add_unit(player=player, unit_const=wall_id, x=x + 0.5, y=y + 0.5)
        return None

    def place_gate(
        self, um, player: PlayerId, gate_id: int, cx: int, cy: int, along_x: bool
    ):
        """Stawia 4-kratkową bramę palisadową na środku przełęczy i rezerwuje jej 4 pola."""
        if along_x:
            for x in range(cx - 2, cx + 2):
                self.occupied_tiles.add((x, cy))
            self.mark_no_trees(cx, cy, 3)
            return um.add_unit(
                player=player, unit_const=gate_id, x=float(cx), y=cy + 0.5
            )

        for y in range(cy - 2, cy + 2):
            self.occupied_tiles.add((cx, y))
        self.mark_no_trees(cx, cy, 3)
        return um.add_unit(player=player, unit_const=gate_id, x=cx + 0.5, y=float(cy))

    def add_hill_plateau(self, cx: int, cy: int, flat_radius: int, height: int):
        total_r = flat_radius + height
        for x in range(max(0, cx - total_r), min(self.size, cx + total_r + 1)):
            for y in range(max(0, cy - total_r), min(self.size, cy + total_r + 1)):
                dist = max(abs(x - cx), abs(y - cy))
                h = max(0, min(height, flat_radius + height - dist))
                self.elev[x][y] = max(self.elev[x][y], h)

    def apply_smooth_elevation(self, mm):
        for x in range(self.size):
            for y in range(self.size):
                for dx, dy in [(-1, 0), (0, -1), (-1, -1), (-1, 1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.size and 0 <= ny < self.size:
                        self.elev[x][y] = min(self.elev[x][y], self.elev[nx][ny] + 1)
        for x in range(self.size - 1, -1, -1):
            for y in range(self.size - 1, -1, -1):
                for dx, dy in [(1, 0), (0, 1), (1, 1), (1, -1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.size and 0 <= ny < self.size:
                        self.elev[x][y] = min(self.elev[x][y], self.elev[nx][ny] + 1)
        for x in range(self.size):
            for y in range(self.size):
                mm.get_tile(x, y).elevation = self.elev[x][y]


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


def reveal_building_pinpoint(um, cx: int, cy: int):
    """
    Stawia TYLKO 1 Map Revealer dla Gracza 1 (dzięki Kartografii widzą go wszyscy 4 gracze!)
    w odległości 9 kratek od środka celu (poza strefą detekcji garnizonu radius=7).
    Przy Line of Sight = 10 odkrywa wyłącznie sam budynek celu, zachowując pełną Mgłę Wojny na mapie!
    """
    rx = max(2, min(MAP_SIZE - 3, cx + 9))
    ry = max(2, min(MAP_SIZE - 3, cy))
    um.add_unit(player=PlayerId.ONE, unit_const=MAP_REVEALER_ID, x=rx + 0.5, y=ry + 0.5)


def paint_natural_biome_background(mm, size: int):
    for x in range(size):
        for y in range(size):
            n = math.sin(x * 0.08) * math.cos(y * 0.08) + 0.5 * math.sin((x + y) * 0.05)
            tile = mm.get_tile(x, y)
            if n > 0.65:
                tile.terrain_id = TerrainId.GRASS_2
            elif n < -0.75:
                tile.terrain_id = TerrainId.DIRT_2
            else:
                tile.terrain_id = TerrainId.GRASS_1


def set_circle_terrain(mm, cx: int, cy: int, radius: int, terrain_id: int):
    for x in range(max(0, cx - radius), min(MAP_SIZE, cx + radius + 1)):
        for y in range(max(0, cy - radius), min(MAP_SIZE, cy + radius + 1)):
            if math.hypot(x - cx, y - cy) <= radius:
                mm.get_tile(x, y).terrain_id = terrain_id


def set_box_terrain(mm, x1: int, y1: int, x2: int, y2: int, terrain_id: int):
    for x in range(max(0, min(x1, x2)), min(MAP_SIZE, max(x1, x2) + 1)):
        for y in range(max(0, min(y1, y2)), min(MAP_SIZE, max(y1, y2) + 1)):
            mm.get_tile(x, y).terrain_id = terrain_id


def paint_organic_forest(
    mm, cx: int, cy: int, radius: float, terrain_id: int, seed: float = 0.0
):
    max_r = int(radius * 1.6) + 2
    for x in range(max(0, cx - max_r), min(MAP_SIZE, cx + max_r + 1)):
        for y in range(max(0, cy - max_r), min(MAP_SIZE, cy + max_r + 1)):
            dx, dy = x - cx, y - cy
            dist = math.hypot(dx, dy)
            angle = math.atan2(dy, dx)
            wobble = (
                1.0
                + 0.28 * math.sin(3 * angle + seed)
                + 0.20 * math.cos(5 * angle - seed * 1.7)
                + 0.14 * math.sin(7 * angle + seed * 2.3)
            )
            eff_r = radius * wobble
            if dist <= eff_r:
                mm.get_tile(x, y).terrain_id = terrain_id
            elif (
                dist <= eff_r + 1.5
                and mm.get_tile(x, y).terrain_id == TerrainId.GRASS_1
            ):
                mm.get_tile(x, y).terrain_id = TerrainId.GRASS_2


def build_rocky_cliff_ridge(
    mm, um, grid: SafeMapGrid, x1: int, y1: int, x2: int, y2: int, height: int = 3
):
    steps = int(math.hypot(x2 - x1, y2 - y1))
    for i in range(steps + 1):
        t = i / max(1, steps)
        curve = math.sin(t * math.pi) * 3.0
        rx = round(x1 + (x2 - x1) * t + curve)
        ry = round(y1 + (y2 - y1) * t - curve)
        grid.add_hill_plateau(rx, ry, flat_radius=1, height=height)
        set_circle_terrain(mm, rx, ry, radius=2, terrain_id=TerrainId.DIRT_3)
        grid.mark_no_trees(rx, ry, radius=2)
        if (
            i % 2 == 0
            and grid.in_bounds(rx, ry)
            and (rx, ry) not in grid.occupied_tiles
        ):
            grid.place_unit(um, PlayerId.GAIA, ROCK_CLIFF_ID, rx, ry, no_tree_margin=1)


def set_road(mm, grid: SafeMapGrid, x1: int, y1: int, x2: int, y2: int, width: int = 1):
    steps = int(math.hypot(x2 - x1, y2 - y1) * 2)
    for i in range(steps + 1):
        t = i / max(1, steps)
        rx = round(x1 + (x2 - x1) * t)
        ry = round(y1 + (y2 - y1) * t)
        set_circle_terrain(mm, rx, ry, width, TerrainId.ROAD)
        grid.mark_no_trees(rx, ry, width + 2)


def populate_forest_trees(mm, um, grid: SafeMapGrid):
    """
    Sadzi drzewa na pełnym zakresie 0..MAP_SIZE-1 (bez marginesu na krawędziach!),
    dzięki czemu lasy graniczne szczelnie stykają się z krawędzią mapy.
    """
    for x in range(MAP_SIZE):
        for y in range(MAP_SIZE):
            if (x, y) in grid.occupied_tiles or (x, y) in grid.no_tree_zones:
                continue
            t_id = mm.get_tile(x, y).terrain_id
            if t_id == TerrainId.FOREST_OAK:
                grid.occupied_tiles.add((x, y))
                um.add_unit(
                    player=PlayerId.GAIA, unit_const=TREE_OAK_ID, x=x + 0.5, y=y + 0.5
                )
            elif t_id == TerrainId.FOREST_PINE:
                grid.occupied_tiles.add((x, y))
                um.add_unit(
                    player=PlayerId.GAIA, unit_const=TREE_PINE_ID, x=x + 0.5, y=y + 0.5
                )


def build_fortified_pass_defenses(
    um, grid: SafeMapGrid, owner: PlayerId, gx: int, gy: int, along_x: bool
):
    """
    Buduje na przełęczy wstępną Wzmocnioną Palisadę (ID 155) z Bramą Palisadową na środku
    oraz 2 Wieżami Strażniczymi po wewnętrznej stronie Twierdzy.
    """
    if along_x:
        # Przełęcz Północna (mur biegnie poziomo wzdłuż osi X: od gx-6 do gx+6 na wysokości gy)
        grid.place_gate(um, owner, PALISADE_GATE_SW_NE_ID, gx, gy, along_x=True)
        for x in range(gx - 6, gx + 7):
            if gx - 2 <= x < gx + 2:
                continue
            grid.place_wall_tile(um, owner, FORTIFIED_PALISADE_ID, x, gy)
        grid.place_building(
            um,
            owner,
            BuildingInfo.GUARD_TOWER.ID,
            gx - 4,
            gy + 4,
            size_tiles=2,
            no_tree_margin=2,
        )
        grid.place_building(
            um,
            owner,
            BuildingInfo.GUARD_TOWER.ID,
            gx + 4,
            gy + 4,
            size_tiles=2,
            no_tree_margin=2,
        )
    else:
        # Przełęcze Centralna i Wschodnia (mur biegnie pionowo wzdłuż osi Y: od gy-6 do gy+6 na szerokości gx)
        grid.place_gate(um, owner, PALISADE_GATE_NW_SE_ID, gx, gy, along_x=False)
        for y in range(gy - 6, gy + 7):
            if gy - 2 <= y < gy + 2:
                continue
            grid.place_wall_tile(um, owner, FORTIFIED_PALISADE_ID, gx, y)
        grid.place_building(
            um,
            owner,
            BuildingInfo.GUARD_TOWER.ID,
            gx - 4,
            gy - 4,
            size_tiles=2,
            no_tree_margin=2,
        )
        grid.place_building(
            um,
            owner,
            BuildingInfo.GUARD_TOWER.ID,
            gx - 4,
            gy + 4,
            size_tiles=2,
            no_tree_margin=2,
        )


def spawn_resource_cluster(
    um, grid: SafeMapGrid, cx: int, cy: int, res_const: int, count: int = 6
):
    offsets = [
        (0, 0),
        (1, 0),
        (0, 1),
        (1, 1),
        (2, 0),
        (0, 2),
        (2, 1),
        (1, 2),
        (2, 2),
        (3, 0),
        (0, 3),
        (3, 1),
    ]
    for dx, dy in offsets[:count]:
        grid.place_unit(
            um, PlayerId.GAIA, res_const, cx + dx, cy + dy, no_tree_margin=2
        )


def spawn_symmetrical_player_base(
    um, mm, grid: SafeMapGrid, player: PlayerId, cx: int, cy: int
):
    grid.mark_no_trees(cx, cy, radius=11)
    grid.place_building(
        um, player, BuildingInfo.TOWN_CENTER.ID, cx, cy, size_tiles=4, no_tree_margin=4
    )

    for dx, dy in [(-3, -2), (-3, -1), (-3, 0), (-3, 1), (-2, -3), (-1, -3)]:
        grid.place_unit(
            um, player, UnitInfo.VILLAGER_MALE.ID, cx + dx, cy + dy, no_tree_margin=1
        )
    grid.place_unit(um, player, UnitInfo.SCOUT_CAVALRY.ID, cx + 4, cy, no_tree_margin=1)

    for tx, ty in [(-5, -3), (4, -4), (-4, 4), (4, 3), (-5, 1), (3, -5)]:
        grid.place_unit(
            um, PlayerId.GAIA, TREE_OAK_ID, cx + tx, cy + ty, no_tree_margin=0
        )

    for sx, sy in [(-3, 2), (-2, 2), (-1, 2), (0, 2), (-3, 3), (-2, 3)]:
        grid.place_unit(
            um, PlayerId.GAIA, UnitInfo.SHEEP.ID, cx + sx, cy + sy, no_tree_margin=1
        )
    grid.place_unit(
        um, PlayerId.GAIA, UnitInfo.WILD_BOAR.ID, cx - 9, cy - 1, no_tree_margin=1
    )
    grid.place_unit(
        um, PlayerId.GAIA, UnitInfo.WILD_BOAR.ID, cx + 1, cy + 9, no_tree_margin=1
    )
    for dx, dy in [(-7, -7), (-8, -7), (-7, -8), (-8, -8)]:
        grid.place_unit(
            um, PlayerId.GAIA, UnitInfo.DEER.ID, cx + dx, cy + dy, no_tree_margin=1
        )

    spawn_resource_cluster(um, grid, cx - 8, cy - 4, OtherInfo.FORAGE_BUSH.ID, count=6)
    spawn_resource_cluster(um, grid, cx + 7, cy - 6, OtherInfo.GOLD_MINE.ID, count=8)
    spawn_resource_cluster(um, grid, cx + 7, cy + 5, OtherInfo.GOLD_MINE.ID, count=6)
    spawn_resource_cluster(um, grid, cx - 8, cy + 5, OtherInfo.STONE_MINE.ID, count=6)

    paint_organic_forest(
        mm, cx - 14, cy, radius=4.8, terrain_id=TerrainId.FOREST_OAK, seed=cx * 0.1
    )
    paint_organic_forest(
        mm, cx, cy + 14, radius=4.8, terrain_id=TerrainId.FOREST_PINE, seed=cy * 0.1
    )


def spawn_settlement_buildings(
    um, grid: SafeMapGrid, player: PlayerId, cx: int, cy: int, grade: int
):
    reveal_building_pinpoint(um, cx, cy)
    if grade == 1:
        grid.mark_no_trees(cx, cy, radius=11)
        core = grid.place_building(
            um,
            player,
            BuildingInfo.GUARD_TOWER.ID,
            cx,
            cy,
            size_tiles=2,
            no_tree_margin=2,
        )
        grid.place_building(
            um,
            player,
            BuildingInfo.BARRACKS.ID,
            cx - 6,
            cy - 4,
            size_tiles=3,
            no_tree_margin=2,
        )
        grid.place_building(
            um,
            player,
            BuildingInfo.SIEGE_WORKSHOP.ID,
            cx + 6,
            cy - 4,
            size_tiles=3,
            no_tree_margin=2,
        )
        return core

    if grade == 2:
        grid.mark_no_trees(cx, cy, radius=14)
        core = grid.place_building(
            um, player, BuildingInfo.CASTLE.ID, cx, cy, size_tiles=4, no_tree_margin=3
        )
        grid.place_building(
            um,
            player,
            BuildingInfo.ARCHERY_RANGE.ID,
            cx - 7,
            cy - 5,
            size_tiles=3,
            no_tree_margin=2,
        )
        grid.place_building(
            um,
            player,
            BuildingInfo.MONASTERY.ID,
            cx + 7,
            cy - 5,
            size_tiles=3,
            no_tree_margin=2,
        )
        for tx, ty in [(-9, -9), (9, -9), (-9, 9), (9, 9)]:
            grid.place_building(
                um,
                player,
                BuildingInfo.GUARD_TOWER.ID,
                cx + tx,
                cy + ty,
                size_tiles=2,
                no_tree_margin=2,
            )
        return core

    grid.mark_no_trees(cx, cy, radius=18)
    core = grid.place_building(
        um, player, BuildingInfo.CASTLE.ID, cx, cy, size_tiles=4, no_tree_margin=3
    )
    grid.place_building(
        um,
        player,
        BuildingInfo.CASTLE.ID,
        cx - 9,
        cy + 8,
        size_tiles=4,
        no_tree_margin=2,
    )
    grid.place_building(
        um,
        player,
        BuildingInfo.CASTLE.ID,
        cx + 9,
        cy - 8,
        size_tiles=4,
        no_tree_margin=2,
    )
    grid.place_building(
        um,
        player,
        BuildingInfo.STABLE.ID,
        cx - 7,
        cy - 7,
        size_tiles=3,
        no_tree_margin=2,
    )
    grid.place_building(
        um,
        player,
        BuildingInfo.SIEGE_WORKSHOP.ID,
        cx + 7,
        cy + 7,
        size_tiles=3,
        no_tree_margin=2,
    )
    for tx, ty in [(-12, -12), (12, -12), (-12, 12), (12, 12)]:
        grid.place_building(
            um,
            player,
            BuildingInfo.KEEP.ID,
            cx + tx,
            cy + ty,
            size_tiles=2,
            no_tree_margin=2,
        )
    return core


def add_proximity_garrison_trigger(
    tm,
    enable_parent_trigger,
    name: str,
    ai_player: PlayerId,
    cx: int,
    cy: int,
    units_spec: list[tuple[int, int]],
):
    detect_radius = 7
    x1, y1 = max(0, cx - detect_radius), max(0, cy - detect_radius)
    x2, y2 = (
        min(MAP_SIZE - 1, cx + detect_radius),
        min(MAP_SIZE - 1, cy + detect_radius),
    )

    t_spawn = tm.add_trigger(f"Garrison_Spawn_{name}", enabled=False, looping=False)
    add_spawn_and_attack_effect(
        t_spawn,
        ai_player,
        units_spec,
        spawn_x=cx,
        spawn_y=cy + 4,
        target_x=cx,
        target_y=cy,
    )

    for h_p in [PlayerId.ONE, PlayerId.TWO, PlayerId.THREE, PlayerId.FOUR]:
        t_detect = tm.add_trigger(
            f"Garrison_Detect_{name}_P{h_p.value}", enabled=False, looping=False
        )
        safe_call(
            t_detect.new_condition.objects_in_area,
            source_player=h_p,
            area_x1=x1,
            area_y1=y1,
            area_x2=x2,
            area_y2=y2,
            quantity=5,
        )
        safe_call(t_detect.new_effect.activate_trigger, trigger_id=t_spawn.trigger_id)
        safe_call(
            enable_parent_trigger.new_effect.activate_trigger,
            trigger_id=t_detect.trigger_id,
        )


def add_spawn_and_attack_effect(
    trigger,
    ai_player: PlayerId,
    units_spec: list[tuple[int, int]],
    spawn_x: int,
    spawn_y: int,
    target_x: int,
    target_y: int,
):
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

    safe_call(
        trigger.new_effect.attack_move,
        source_player=ai_player,
        area_x1=max(0, spawn_x - 8),
        area_y1=max(0, spawn_y - 8),
        area_x2=min(MAP_SIZE - 1, spawn_x + 8),
        area_y2=min(MAP_SIZE - 1, spawn_y + 8),
        location_x=target_x,
        location_y=target_y,
    )


def build_horde_scenario():
    if not INPUT_TEMPLATE.exists():
        raise FileNotFoundError(f"Nie znaleziono szablonu: {INPUT_TEMPLATE}")

    scenario = AoE2DEScenario.from_file(str(INPUT_TEMPLATE))
    tm = scenario.trigger_manager
    um = scenario.unit_manager
    mm = scenario.map_manager
    pm = scenario.player_manager

    tm.triggers = []
    um.units = [[] for _ in range(9)]
    mm.map_size = MAP_SIZE

    populate_ingame_scenario_descriptions(scenario)

    grid = SafeMapGrid(MAP_SIZE)

    human_players = [PlayerId.ONE, PlayerId.TWO, PlayerId.THREE, PlayerId.FOUR]
    ai_players = [PlayerId.FIVE, PlayerId.SIX, PlayerId.SEVEN, PlayerId.EIGHT]

    pm.active_players = 8
    for p_id in human_players:
        p = pm.players[p_id]
        res = BALANCE["human_start_res"]
        p.food, p.wood, p.gold, p.stone = (
            res["food"],
            res["wood"],
            res["gold"],
            res["stone"],
        )

    for p_id in ai_players:
        p = pm.players[p_id]
        p.food, p.wood, p.gold, p.stone = 0, 0, 0, 0

    paint_natural_biome_background(mm, MAP_SIZE)

    # Pasmo górsko-leśne Twierdzy Sojuszu dochodzące do samych krawędzi mapy (0 oraz 199!)
    for x in range(0, 106, 8):
        grid.add_hill_plateau(x, 100, flat_radius=4, height=3)
    for y in range(100, 200, 8):
        grid.add_hill_plateau(104, y, flat_radius=4, height=3)

    set_box_terrain(mm, 0, 95, 108, 105, TerrainId.FOREST_PINE)
    set_box_terrain(mm, 99, 95, 109, 199, TerrainId.FOREST_PINE)

    gate_north = (48, 100)
    gate_center = (104, 114)
    gate_east = (104, 162)

    for gx, gy in [gate_north, gate_center, gate_east]:
        for x in range(gx - 8, gx + 9):
            for y in range(gy - 8, gy + 9):
                if 0 <= x < MAP_SIZE and 0 <= y < MAP_SIZE:
                    grid.elev[x][y] = 0
        set_box_terrain(mm, gx - 6, gy - 6, gx + 6, gy + 6, TerrainId.DIRT_1)
        grid.mark_no_trees(gx, gy, radius=8)

    # Rzeka w otwartym polu z 3 szerokimi brodami
    for t_step in range(140):
        rx = round(62 + t_step * 0.9)
        ry = round(8 + t_step * 0.8 + 3 * math.sin(t_step * 0.08))
        if 2 <= rx < MAP_SIZE - 2 and 2 <= ry < MAP_SIZE - 2 and (rx > 112 or ry < 90):
            set_circle_terrain(mm, rx, ry, radius=2, terrain_id=TERRAIN_WATER)
            grid.mark_no_trees(rx, ry, radius=3)

    for fx, fy in [(84, 30), (122, 62), (154, 92)]:
        set_circle_terrain(mm, fx, fy, radius=5, terrain_id=TERRAIN_SHALLOWS)

    s_coords = {
        "G1_North": (76, 72),
        "G1_East": (132, 152),
        "G2_Snipers": (68, 34),
        "G2_Mages": (148, 72),
        "G3_North": (142, 24),
        "G3_East": (176, 56),
    }
    grid.add_hill_plateau(*s_coords["G1_North"], flat_radius=9, height=1)
    grid.add_hill_plateau(*s_coords["G1_East"], flat_radius=9, height=1)
    grid.add_hill_plateau(*s_coords["G2_Snipers"], flat_radius=13, height=2)
    grid.add_hill_plateau(*s_coords["G2_Mages"], flat_radius=13, height=2)
    grid.add_hill_plateau(*s_coords["G3_North"], flat_radius=17, height=4)
    grid.add_hill_plateau(*s_coords["G3_East"], flat_radius=17, height=4)

    q1_pos = (154, 182)
    q2_pos = (28, 32)
    q3_pos = (142, 118)
    q4_pos = (105, 20)
    grid.add_hill_plateau(*q2_pos, flat_radius=9, height=4)
    grid.add_hill_plateau(*q3_pos, flat_radius=10, height=2)
    grid.add_hill_plateau(*q4_pos, flat_radius=9, height=3)

    build_rocky_cliff_ridge(mm, um, grid, 16, 48, 44, 48, height=3)
    build_rocky_cliff_ridge(mm, um, grid, 124, 134, 158, 134, height=2)

    grid.apply_smooth_elevation(mm)

    p_coords = {
        PlayerId.THREE: (32, 122),
        PlayerId.ONE: (76, 124),
        PlayerId.TWO: (32, 164),
        PlayerId.FOUR: (76, 168),
    }

    set_road(mm, grid, *s_coords["G1_North"], *gate_north, width=1)
    set_road(mm, grid, *s_coords["G1_East"], *gate_east, width=1)
    set_road(mm, grid, *s_coords["G2_Mages"], *gate_center, width=1)
    set_road(mm, grid, *s_coords["G3_East"], *s_coords["G2_Mages"], width=1)

    for h_p in human_players:
        spawn_symmetrical_player_base(um, mm, grid, h_p, *p_coords[h_p])

    # Wstępne mury (Fortified Palisade Wall + Brama Palisadowa + 2 Wieże) na wszystkich 3 przełęczach
    build_fortified_pass_defenses(um, grid, PlayerId.THREE, *gate_north, along_x=True)
    build_fortified_pass_defenses(um, grid, PlayerId.ONE, *gate_center, along_x=False)
    build_fortified_pass_defenses(um, grid, PlayerId.FOUR, *gate_east, along_x=False)

    # Serce Twierdzy Sojuszu: Wielka Faktoria (FEITORIA_ID = 1021) zamiast Wonder (brak licznika 350 lat!)
    fortress_heart_pos = (54, 146)
    allied_citadel = grid.place_building(
        um,
        PlayerId.THREE,
        FEITORIA_ID,
        fortress_heart_pos[0],
        fortress_heart_pos[1],
        size_tiles=5,
        no_tree_margin=3,
    )

    # 3. Stawianie 6 Settlementów (punktowe odkrycie wyłącznie samego budynku!)
    s_g1_north = spawn_settlement_buildings(
        um, grid, PlayerId.FIVE, *s_coords["G1_North"], grade=1
    )
    s_g1_east = spawn_settlement_buildings(
        um, grid, PlayerId.FIVE, *s_coords["G1_East"], grade=1
    )
    s_g2_snipers = spawn_settlement_buildings(
        um, grid, PlayerId.SIX, *s_coords["G2_Snipers"], grade=2
    )
    s_g2_mages = spawn_settlement_buildings(
        um, grid, PlayerId.SEVEN, *s_coords["G2_Mages"], grade=2
    )
    s_g3_north = spawn_settlement_buildings(
        um, grid, PlayerId.EIGHT, *s_coords["G3_North"], grade=3
    )
    s_g3_east = spawn_settlement_buildings(
        um, grid, PlayerId.EIGHT, *s_coords["G3_East"], grade=3
    )

    for sx, sy in [
        (48, 86),
        (118, 114),
        (120, 162),
        (76, 84),
        (120, 152),
        (68, 48),
        (134, 78),
        (128, 36),
        (160, 62),
    ]:
        grid.mark_no_trees(sx, sy, radius=7)

    # 4. Stawianie 4 Questów (Bez użycia Wonder! Punktowe odkrycie tylko budynku Questu!)
    reveal_building_pinpoint(um, *q1_pos)
    grid.mark_no_trees(*q1_pos, radius=9)
    set_circle_terrain(mm, *q1_pos, radius=8, terrain_id=TerrainId.DIRT_1)
    q1_bldg = grid.place_building(
        um,
        PlayerId.FIVE,
        BuildingInfo.MARKET.ID,
        q1_pos[0],
        q1_pos[1],
        size_tiles=4,
        no_tree_margin=2,
    )

    reveal_building_pinpoint(um, *q2_pos)
    grid.mark_no_trees(*q2_pos, radius=11)
    set_circle_terrain(mm, *q2_pos, radius=10, terrain_id=TerrainId.DIRT_2)
    q2_bldg = grid.place_building(
        um,
        PlayerId.SIX,
        BuildingInfo.UNIVERSITY.ID,
        q2_pos[0],
        q2_pos[1],
        size_tiles=4,
        no_tree_margin=2,
    )

    # QUEST 3: Krepost (KREPOST_ID = 1251) zamiast Wonder P8 (brak licznika 350 lat!)
    reveal_building_pinpoint(um, *q3_pos)
    grid.mark_no_trees(*q3_pos, radius=11)
    set_circle_terrain(mm, *q3_pos, radius=10, terrain_id=TerrainId.ROAD)
    q3_bldg = grid.place_building(
        um,
        PlayerId.EIGHT,
        KREPOST_ID,
        q3_pos[0],
        q3_pos[1],
        size_tiles=4,
        no_tree_margin=2,
    )
    for tx, ty in [(-5, -5), (5, -5), (-5, 5), (5, 5)]:
        grid.place_building(
            um,
            PlayerId.EIGHT,
            BuildingInfo.KEEP.ID,
            q3_pos[0] + tx,
            q3_pos[1] + ty,
            size_tiles=2,
            no_tree_margin=1,
        )
    for wx in range(-7, 8):
        grid.place_wall_tile(
            um,
            PlayerId.EIGHT,
            BuildingInfo.FORTIFIED_WALL.ID,
            q3_pos[0] + wx,
            q3_pos[1] - 8,
        )
        grid.place_wall_tile(
            um,
            PlayerId.EIGHT,
            BuildingInfo.FORTIFIED_WALL.ID,
            q3_pos[0] + wx,
            q3_pos[1] + 8,
        )

    reveal_building_pinpoint(um, *q4_pos)
    grid.mark_no_trees(*q4_pos, radius=10)
    set_circle_terrain(mm, *q4_pos, radius=9, terrain_id=TerrainId.DIRT_3)
    q4_bldg = grid.place_building(
        um,
        PlayerId.SEVEN,
        BuildingInfo.MONASTERY.ID,
        q4_pos[0],
        q4_pos[1],
        size_tiles=3,
        no_tree_margin=2,
    )

    for rx, ry in [(54, 62), (116, 88), (168, 128), (92, 44)]:
        grid.place_unit(um, PlayerId.GAIA, RELIC_ID, rx, ry, no_tree_margin=2)
        spawn_resource_cluster(
            um, grid, rx + 3, ry + 3, OtherInfo.GOLD_MINE.ID, count=6
        )

    # Puszcza Zaplecza dochodząca do samych krawędzi mapy
    set_box_terrain(mm, 0, 106, 12, 199, TerrainId.FOREST_OAK)
    set_box_terrain(mm, 12, 188, 98, 199, TerrainId.FOREST_PINE)

    for fx, fy, r, t_id, seed in [
        (54, 122, 5.5, TerrainId.FOREST_OAK, 0.5),
        (54, 172, 6.0, TerrainId.FOREST_PINE, 1.3),
        (20, 74, 7.0, TerrainId.FOREST_PINE, 1.7),
        (48, 74, 5.5, TerrainId.FOREST_OAK, 2.8),
        (16, 12, 7.5, TerrainId.FOREST_PINE, 3.9),
        (68, 12, 6.5, TerrainId.FOREST_OAK, 0.4),
        (108, 56, 6.0, TerrainId.FOREST_OAK, 1.6),
        (126, 94, 6.5, TerrainId.FOREST_PINE, 2.5),
        (172, 96, 7.0, TerrainId.FOREST_OAK, 3.2),
        (184, 136, 7.5, TerrainId.FOREST_PINE, 0.7),
        (184, 168, 7.0, TerrainId.FOREST_OAK, 1.9),
        (126, 182, 6.5, TerrainId.FOREST_OAK, 2.4),
        (184, 22, 7.0, TerrainId.FOREST_PINE, 3.7),
    ]:
        paint_organic_forest(mm, fx, fy, radius=r, terrain_id=t_id, seed=seed)

    populate_forest_trees(mm, um, grid)

    # ==============================================================================
    # 5. TRIGGERY: INICJALIZACJA, KARTOGRAFIA, WĄSKI LOS REVEALERÓW I 6 MUTANTÓW
    # ==============================================================================
    t_init = tm.add_trigger(
        "01_Init_Diplomacy_And_Cartography", enabled=True, looping=False
    )

    # Zbadanie Kartografii dla wszystkich graczy od 0:00 + ustawienie małego LoS=10 dla Map Revealerów
    research_techs(t_init, human_players, [TECH_CARTOGRAPHY])
    safe_modify_attribute(
        t_init, PlayerId.ONE, MAP_REVEALER_ID, ATTR_LINE_OF_SIGHT, Operation.SET, 10
    )
    safe_modify_attribute(
        t_init, PlayerId.THREE, FEITORIA_ID, ATTR_HIT_POINTS, Operation.ADD, 5000
    )

    for h1 in human_players:
        safe_modify_attribute(
            t_init, h1, FORTIFIED_PALISADE_ID, ATTR_HIT_POINTS, Operation.ADD, 600
        )
        for h2 in human_players:
            if h1 != h2:
                safe_call(
                    t_init.new_effect.change_diplomacy,
                    source_player=h1,
                    target_player=h2,
                    diplomacy=DiplomacyState.ALLY,
                )
        for ai in ai_players:
            safe_call(
                t_init.new_effect.change_diplomacy,
                source_player=h1,
                target_player=ai,
                diplomacy=DiplomacyState.ENEMY,
            )
            safe_call(
                t_init.new_effect.change_diplomacy,
                source_player=ai,
                target_player=h1,
                diplomacy=DiplomacyState.ENEMY,
            )

    for ai1 in ai_players:
        for ai2 in ai_players:
            if ai1 != ai2:
                safe_call(
                    t_init.new_effect.change_diplomacy,
                    source_player=ai1,
                    target_player=ai2,
                    diplomacy=DiplomacyState.ALLY,
                )

    research_techs(
        t_init, ai_players, [TECH_FEUDAL_AGE, TECH_CASTLE_AGE, TECH_IMPERIAL_AGE]
    )
    research_techs(
        t_init, [PlayerId.FIVE], [TECH_SCALE_MAIL, TECH_CHAIN_MAIL, TECH_SQUIRES]
    )
    research_techs(
        t_init,
        [PlayerId.SIX],
        [
            TECH_FLETCHING,
            TECH_BODKIN_ARROW,
            TECH_BRACER,
            TECH_BALLISTICS,
            TECH_CHEMISTRY,
        ],
    )
    research_techs(
        t_init,
        [PlayerId.SEVEN],
        [TECH_FORGING, TECH_IRON_CASTING, TECH_BLOODLINES, TECH_HUSBANDRY],
    )
    research_techs(
        t_init,
        [PlayerId.EIGHT],
        [
            TECH_FORGING,
            TECH_IRON_CASTING,
            TECH_BLAST_FURNACE,
            TECH_SCALE_BARDING,
            TECH_CHAIN_BARDING,
            TECH_PLATE_BARDING,
            TECH_SIEGE_ENGINEERS,
        ],
    )

    building_labels = [
        (allied_citadel, "Cytadela Sojuszu (Serce Twierdzy - Broncie jej!)"),
        (q1_bldg, "Q1: Karawanseraj (+500 Zlota i 3 Wozy)"),
        (q2_bldg, "Q2: Klif Artylerii (Ulepszenia + Atak)"),
        (q3_bldg, "Q3: Skarbiec (Zasoby + Staly dochod)"),
        (q4_bldg, "Q4: Krwawy Oltarz (+50 HP i slabsi Magowie)"),
        (s_g1_north, "G1 Polnocny (Berserkerzy i Petardy)"),
        (s_g1_east, "G1 Wschodni (Huskarlowie i Wielblady)"),
        (s_g2_snipers, "G2 Akademia (Snajperzy i Kolosy)"),
        (s_g2_mages, "G2 Klasztor (Magowie i Szamani)"),
        (s_g3_north, "G3 Cytadela Pln. (Tytani Sloniowi)"),
        (s_g3_east, "G3 Cytadela Wsch. (Tytani i Artyleria)"),
    ]
    for b_unit, label_text in building_labels:
        safe_call(
            t_init.new_effect.change_object_name,
            selected_object_ids=[b_unit.reference_id],
            message=label_text,
        )

    send_highlight_chat(
        t_init,
        "<YELLOW>",
        "=== KRONIKI RUBIEZY === Pierwsza fala za 10 minut! Pelny opis jednostek i nagrod znajdziesz też w menu Wskazowek/Zwiadu (Hints/Scouts).",
    )

    # Trigger nakładający mutacje 6 specjalnych jednostek w 3. sekundzie gry
    t_mutate = tm.add_trigger(
        "01b_Apply_6_Custom_Unit_Mutations", enabled=True, looping=False
    )
    safe_call(t_mutate.new_condition.timer, timer=3)

    # 1. SNAJPERZY (Elitarny Janczar P6)
    safe_modify_attribute(
        t_mutate,
        PlayerId.SIX,
        UnitInfo.ELITE_JANISSARY.ID,
        ATTR_MAXIMUM_RANGE,
        Operation.SET,
        BALANCE["sniper_range"],
    )
    safe_modify_attribute(
        t_mutate,
        PlayerId.SIX,
        UnitInfo.ELITE_JANISSARY.ID,
        ATTR_SEARCH_RADIUS,
        Operation.SET,
        22,
    )
    safe_modify_attribute(
        t_mutate,
        PlayerId.SIX,
        UnitInfo.ELITE_JANISSARY.ID,
        ATTR_LINE_OF_SIGHT,
        Operation.SET,
        22,
    )
    safe_modify_attribute(
        t_mutate,
        PlayerId.SIX,
        UnitInfo.ELITE_JANISSARY.ID,
        ATTR_ATTACK_RELOAD_TIME,
        Operation.SET,
        BALANCE["sniper_reload"],
    )
    safe_modify_attribute(
        t_mutate,
        PlayerId.SIX,
        UnitInfo.ELITE_JANISSARY.ID,
        ATTR_HIT_POINTS,
        Operation.SET,
        BALANCE["sniper_hp"],
    )
    safe_modify_attribute(
        t_mutate,
        PlayerId.SIX,
        UnitInfo.ELITE_JANISSARY.ID,
        ATTR_ATTACK,
        Operation.ADD,
        BALANCE["sniper_bonus_atk"],
        armor_class=3,
    )
    safe_modify_attribute(
        t_mutate,
        PlayerId.SIX,
        UnitInfo.ELITE_JANISSARY.ID,
        ATTR_ATTACK,
        Operation.ADD,
        BALANCE["sniper_bonus_atk"],
        armor_class=4,
    )

    # 2. KOLOSY OBLĘŻNICZE (Siege Onager P6)
    safe_modify_attribute(
        t_mutate,
        PlayerId.SIX,
        SIEGE_ONAGER_ID,
        ATTR_HIT_POINTS,
        Operation.SET,
        BALANCE["colossus_hp"],
    )
    safe_modify_attribute(
        t_mutate,
        PlayerId.SIX,
        SIEGE_ONAGER_ID,
        ATTR_MAXIMUM_RANGE,
        Operation.SET,
        BALANCE["colossus_range"],
    )
    safe_modify_attribute(
        t_mutate, PlayerId.SIX, SIEGE_ONAGER_ID, ATTR_SEARCH_RADIUS, Operation.SET, 24
    )
    safe_modify_attribute(
        t_mutate, PlayerId.SIX, SIEGE_ONAGER_ID, ATTR_LINE_OF_SIGHT, Operation.SET, 24
    )
    safe_modify_attribute(
        t_mutate,
        PlayerId.SIX,
        SIEGE_ONAGER_ID,
        ATTR_ATTACK_RELOAD_TIME,
        Operation.SET,
        BALANCE["colossus_reload"],
    )
    safe_modify_attribute(
        t_mutate,
        PlayerId.SIX,
        SIEGE_ONAGER_ID,
        ATTR_BLAST_WIDTH,
        Operation.SET,
        BALANCE["colossus_blast_width"],
    )
    safe_modify_attribute(
        t_mutate,
        PlayerId.SIX,
        SIEGE_ONAGER_ID,
        ATTR_MOVEMENT_SPEED,
        Operation.SET,
        BALANCE["colossus_speed"],
    )
    safe_modify_attribute(
        t_mutate,
        PlayerId.SIX,
        SIEGE_ONAGER_ID,
        ATTR_ATTACK,
        Operation.ADD,
        BALANCE["colossus_bonus_atk"],
        armor_class=3,
    )
    safe_modify_attribute(
        t_mutate,
        PlayerId.SIX,
        SIEGE_ONAGER_ID,
        ATTR_ATTACK,
        Operation.ADD,
        BALANCE["colossus_bonus_atk"],
        armor_class=4,
    )

    # 3. FANATYCY KAMIKAZE I PŁONĄCE WIELBŁĄDY (Petard & Flaming Camel P5)
    for kamikaze_id in [PETARD_ID, FLAMING_CAMEL_ID]:
        safe_modify_attribute(
            t_mutate,
            PlayerId.FIVE,
            kamikaze_id,
            ATTR_HIT_POINTS,
            Operation.SET,
            BALANCE["kamikaze_hp"],
        )
        safe_modify_attribute(
            t_mutate,
            PlayerId.FIVE,
            kamikaze_id,
            ATTR_MOVEMENT_SPEED,
            Operation.MULTIPLY,
            BALANCE["kamikaze_speed_mult"],
        )
        safe_modify_attribute(
            t_mutate,
            PlayerId.FIVE,
            kamikaze_id,
            ATTR_BLAST_WIDTH,
            Operation.SET,
            BALANCE["kamikaze_blast_width"],
        )
        safe_modify_attribute(
            t_mutate,
            PlayerId.FIVE,
            kamikaze_id,
            ATTR_ATTACK,
            Operation.ADD,
            BALANCE["kamikaze_bonus_atk"],
            armor_class=4,
        )

    # 4. BERSERKERZY SZTURMOWI (Elite Berserk P5)
    safe_modify_attribute(
        t_mutate,
        PlayerId.FIVE,
        ELITE_BERSERK_ID,
        ATTR_HIT_POINTS,
        Operation.SET,
        BALANCE["berserk_hp"],
    )
    safe_modify_attribute(
        t_mutate,
        PlayerId.FIVE,
        ELITE_BERSERK_ID,
        ATTR_MOVEMENT_SPEED,
        Operation.SET,
        BALANCE["berserk_speed"],
    )
    safe_modify_attribute(
        t_mutate,
        PlayerId.FIVE,
        ELITE_BERSERK_ID,
        ATTR_ATTACK,
        Operation.ADD,
        BALANCE["berserk_bonus_atk"],
        armor_class=4,
    )

    # 5. TYTANI HORDY (Elite Battle Elephant P8)
    safe_modify_attribute(
        t_mutate,
        PlayerId.EIGHT,
        ELITE_BATTLE_ELEPHANT_ID,
        ATTR_HIT_POINTS,
        Operation.SET,
        BALANCE["titan_hp"],
    )
    safe_modify_attribute(
        t_mutate,
        PlayerId.EIGHT,
        ELITE_BATTLE_ELEPHANT_ID,
        ATTR_BLAST_WIDTH,
        Operation.SET,
        BALANCE["titan_blast_width"],
    )
    safe_modify_attribute(
        t_mutate,
        PlayerId.EIGHT,
        ELITE_BATTLE_ELEPHANT_ID,
        ATTR_ATTACK,
        Operation.ADD,
        BALANCE["titan_bonus_atk"],
        armor_class=4,
    )

    # 6. MAGOWIE NIEŚMIERTELNOŚCI (Imam P7) oraz SZAMANI KRWI (Misjonarz P7)
    safe_modify_attribute(
        t_mutate,
        PlayerId.SEVEN,
        IMAM_UNIT_ID,
        ATTR_HIT_POINTS,
        Operation.SET,
        BALANCE["mage_hp"],
    )
    safe_modify_attribute(
        t_mutate,
        PlayerId.SEVEN,
        IMAM_UNIT_ID,
        ATTR_ARMOR,
        Operation.ADD,
        8,
        armor_class=3,
    )
    safe_modify_attribute(
        t_mutate,
        PlayerId.SEVEN,
        IMAM_UNIT_ID,
        ATTR_ARMOR,
        Operation.ADD,
        8,
        armor_class=4,
    )
    safe_modify_attribute(
        t_mutate,
        PlayerId.SEVEN,
        UnitInfo.MISSIONARY.ID,
        ATTR_WORK_RATE,
        Operation.MULTIPLY,
        6.0,
    )
    safe_modify_attribute(
        t_mutate,
        PlayerId.SEVEN,
        UnitInfo.MISSIONARY.ID,
        ATTR_HIT_POINTS,
        Operation.SET,
        280,
    )

    # Detektory garnizonów uzbrajane w 6. minucie gry
    t_arm_garrisons = tm.add_trigger(
        "01c_Arm_Garrison_Detectors_At_6m", enabled=True, looping=False
    )
    safe_call(t_arm_garrisons.new_condition.timer, timer=360)

    add_proximity_garrison_trigger(
        tm,
        t_arm_garrisons,
        "Quest1_Caravan",
        PlayerId.FIVE,
        *q1_pos,
        units_spec=[(UnitInfo.STEPPE_LANCER.ID, 8), (FLAMING_CAMEL_ID, 3)],
    )
    add_proximity_garrison_trigger(
        tm,
        t_arm_garrisons,
        "Quest2_SniperCliff",
        PlayerId.SIX,
        *q2_pos,
        units_spec=[(UnitInfo.ELITE_JANISSARY.ID, 6), (SIEGE_ONAGER_ID, 2)],
    )
    add_proximity_garrison_trigger(
        tm,
        t_arm_garrisons,
        "Quest3_SiegeVault",
        PlayerId.EIGHT,
        *q3_pos,
        units_spec=[(UnitInfo.HALBERDIER.ID, 12), (ELITE_BATTLE_ELEPHANT_ID, 3)],
    )
    add_proximity_garrison_trigger(
        tm,
        t_arm_garrisons,
        "Quest4_BloodAltar",
        PlayerId.EIGHT,
        *q4_pos,
        units_spec=[(UnitInfo.PALADIN.ID, 10), (UnitInfo.MISSIONARY.ID, 4)],
    )

    add_proximity_garrison_trigger(
        tm,
        t_arm_garrisons,
        "Settle_G1_North",
        PlayerId.FIVE,
        *s_coords["G1_North"],
        units_spec=[(ELITE_BERSERK_ID, 8), (PETARD_ID, 3)],
    )
    add_proximity_garrison_trigger(
        tm,
        t_arm_garrisons,
        "Settle_G1_East",
        PlayerId.FIVE,
        *s_coords["G1_East"],
        units_spec=[(UnitInfo.HUSKARL.ID, 10), (FLAMING_CAMEL_ID, 3)],
    )
    add_proximity_garrison_trigger(
        tm,
        t_arm_garrisons,
        "Settle_G2_Snipers",
        PlayerId.SIX,
        *s_coords["G2_Snipers"],
        units_spec=[(UnitInfo.ELITE_JANISSARY.ID, 8), (SIEGE_ONAGER_ID, 2)],
    )
    add_proximity_garrison_trigger(
        tm,
        t_arm_garrisons,
        "Settle_G2_Mages",
        PlayerId.SEVEN,
        *s_coords["G2_Mages"],
        units_spec=[(UnitInfo.CAVALIER.ID, 12), (UnitInfo.MISSIONARY.ID, 4)],
    )
    add_proximity_garrison_trigger(
        tm,
        t_arm_garrisons,
        "Settle_G3_North",
        PlayerId.EIGHT,
        *s_coords["G3_North"],
        units_spec=[(ELITE_BATTLE_ELEPHANT_ID, 6), (UnitInfo.HALBERDIER.ID, 16)],
    )
    add_proximity_garrison_trigger(
        tm,
        t_arm_garrisons,
        "Settle_G3_East",
        PlayerId.EIGHT,
        *s_coords["G3_East"],
        units_spec=[
            (ELITE_BATTLE_ELEPHANT_ID, 6),
            (UnitInfo.ARBALESTER.ID, 16),
            (SIEGE_ONAGER_ID, 2),
        ],
    )

    # ==============================================================================
    # 6. LOKALNA AURA MAGÓW (PROMIEŃ 25 KRATEK WOKÓŁ BRAMY CENTRALNEJ)
    # ==============================================================================
    r_local = BALANCE["mage_local_radius"]
    mx1, my1 = max(0, gate_center[0] - r_local), max(0, gate_center[1] - r_local)
    mx2, my2 = (
        min(MAP_SIZE - 1, gate_center[0] + r_local),
        min(MAP_SIZE - 1, gate_center[1] + r_local),
    )

    p7_shielded_units = [
        UnitInfo.KNIGHT.ID,
        UnitInfo.CAVALIER.ID,
        UnitInfo.PALADIN.ID,
        UnitInfo.CAPPED_RAM.ID,
        UnitInfo.SIEGE_RAM.ID,
    ]

    t_shield_on = tm.add_trigger(
        "02a_Mage_Local_25Tile_Shield_On", enabled=False, looping=False
    )
    safe_call(
        t_shield_on.new_condition.objects_in_area,
        source_player=PlayerId.SEVEN,
        object_list=IMAM_UNIT_ID,
        object_list_unit_id=IMAM_UNIT_ID,
        area_x1=mx1,
        area_y1=my1,
        area_x2=mx2,
        area_y2=my2,
        quantity=1,
    )
    for u_id in p7_shielded_units:
        safe_modify_attribute(
            t_shield_on,
            PlayerId.SEVEN,
            u_id,
            ATTR_ARMOR,
            Operation.ADD,
            BALANCE["mage_shield_armor"],
            armor_class=3,
        )
        safe_modify_attribute(
            t_shield_on,
            PlayerId.SEVEN,
            u_id,
            ATTR_ARMOR,
            Operation.ADD,
            BALANCE["mage_shield_armor"],
            armor_class=4,
        )

    t_local_heal = tm.add_trigger(
        "02b_Mage_Local_25Tile_Heal_Pulse", enabled=False, looping=True
    )
    safe_call(t_local_heal.new_condition.timer, timer=2)
    safe_call(
        t_local_heal.new_condition.objects_in_area,
        source_player=PlayerId.SEVEN,
        object_list=IMAM_UNIT_ID,
        object_list_unit_id=IMAM_UNIT_ID,
        area_x1=mx1,
        area_y1=my1,
        area_x2=mx2,
        area_y2=my2,
        quantity=1,
    )
    for ai_p in [PlayerId.SEVEN, PlayerId.EIGHT]:
        safe_call(
            t_local_heal.new_effect.heal_object,
            source_player=ai_p,
            area_x1=mx1,
            area_y1=my1,
            area_x2=mx2,
            area_y2=my2,
            quantity=BALANCE["mage_local_heal_2s"],
        )

    t_shield_off = tm.add_trigger(
        "02c_Mage_Local_Shield_Off", enabled=False, looping=False
    )
    safe_call(
        t_shield_off.new_condition.own_fewer_objects,
        source_player=PlayerId.SEVEN,
        object_list=IMAM_UNIT_ID,
        quantity=0,
    )
    for u_id in p7_shielded_units:
        safe_modify_attribute(
            t_shield_off,
            PlayerId.SEVEN,
            u_id,
            ATTR_ARMOR,
            Operation.SUBTRACT,
            BALANCE["mage_shield_armor"],
            armor_class=3,
        )
        safe_modify_attribute(
            t_shield_off,
            PlayerId.SEVEN,
            u_id,
            ATTR_ARMOR,
            Operation.SUBTRACT,
            BALANCE["mage_shield_armor"],
            armor_class=4,
        )
    safe_call(
        t_shield_off.new_effect.deactivate_trigger, trigger_id=t_local_heal.trigger_id
    )
    send_highlight_chat(
        t_shield_off,
        "<GREEN>",
        "[BARIERA PRZELAMANA]: Arcymagowie przed brama zabici! Jednostki P7 traca niesmiertelnosc!",
    )

    safe_call(
        t_shield_on.new_effect.activate_trigger, trigger_id=t_local_heal.trigger_id
    )
    safe_call(
        t_shield_on.new_effect.activate_trigger, trigger_id=t_shield_off.trigger_id
    )
    send_highlight_chat(
        t_shield_on,
        "<PURPLE>",
        "[LOKALNA AURA MAGA - 25 KRATEK]: Arcymag (P7) wszedl w strefe 25 kratek przed Brama Centralna (+60 Pancerza i regeneracja)! Zabijcie go!",
        flare_x=114,
        flare_y=114,
    )

    # ==============================================================================
    # 7. ESKALACJA STATYSTYK (START DOPIERO PO 1. ATAKU - CZYLI OD 14. MINUTY!)
    # ==============================================================================
    all_enemy_combat_units = [
        UnitInfo.MAN_AT_ARMS.ID,
        UnitInfo.PIKEMAN.ID,
        UnitInfo.HALBERDIER.ID,
        UnitInfo.HUSKARL.ID,
        ELITE_BERSERK_ID,
        PETARD_ID,
        FLAMING_CAMEL_ID,
        UnitInfo.ARCHER.ID,
        UnitInfo.CROSSBOWMAN.ID,
        UnitInfo.ARBALESTER.ID,
        UnitInfo.ELITE_JANISSARY.ID,
        UnitInfo.SCOUT_CAVALRY.ID,
        UnitInfo.KNIGHT.ID,
        UnitInfo.CAVALIER.ID,
        UnitInfo.PALADIN.ID,
        ELITE_BATTLE_ELEPHANT_ID,
        SIEGE_ONAGER_ID,
        UnitInfo.BATTERING_RAM.ID,
        UnitInfo.CAPPED_RAM.ID,
        UnitInfo.SIEGE_RAM.ID,
    ]

    t_escalate = tm.add_trigger(
        "04_Global_Horde_Escalation", enabled=False, looping=True
    )
    safe_call(t_escalate.new_condition.timer, timer=BALANCE["escalation_interval_sec"])
    for ai_p in ai_players:
        for u_id in all_enemy_combat_units:
            safe_modify_attribute(
                t_escalate, ai_p, u_id, ATTR_HIT_POINTS, Operation.ADD, 25
            )
            safe_modify_attribute(
                t_escalate, ai_p, u_id, ATTR_ATTACK, Operation.ADD, 2, armor_class=4
            )
            safe_modify_attribute(
                t_escalate, ai_p, u_id, ATTR_ATTACK, Operation.ADD, 2, armor_class=3
            )
    send_highlight_chat(
        t_escalate,
        "<ORANGE>",
        "[ESKALACJA HORDY]: Wszystkie jednostki Hordy otrzymuja trwale +25 HP oraz +2 Ataku!",
    )

    # ==============================================================================
    # 8. HARMONOGRAM 12 ROSNĄCYCH FAL Z 6 KLASAMI MUTANTÓW (CO 3 MINUTY OD 10:00)
    # ==============================================================================
    all_settlement_wave_triggers = {
        "G1_North": [],
        "G1_East": [],
        "G2_Snipers": [],
        "G2_Mages": [],
        "G3_North": [],
        "G3_East": [],
    }

    for wave_num in range(1, 13):
        wave_time = (
            BALANCE["first_wave_sec"] + (wave_num - 1) * BALANCE["wave_interval_sec"]
        )
        is_endless_last = wave_num == 12
        loop_flag = is_endless_last
        cond_time = BALANCE["wave_interval_sec"] if is_endless_last else wave_time

        t_ann = tm.add_trigger(
            f"03_W{wave_num:02d}_Announce",
            enabled=not is_endless_last,
            looping=loop_flag,
        )
        safe_call(t_ann.new_condition.timer, timer=cond_time)

        if wave_num == 1:
            safe_call(
                t_ann.new_effect.activate_trigger, trigger_id=t_escalate.trigger_id
            )

        send_highlight_chat(
            t_ann,
            "<RED>",
            f"=== [FALA {wave_num}/12 UDERZA NA BRAMY!] === Po odparciu fali macie 2,5 min Okna Ekspedycyjnego na wypad w pole!",
            flare_x=gate_center[0],
            flare_y=gate_center[1],
        )

        if wave_num <= 2:
            g1_n_comp = [
                (ELITE_BERSERK_ID, 4 + wave_num * 2),
                (PETARD_ID, 2),
                (UnitInfo.BATTERING_RAM.ID, 1),
            ]
            g1_e_comp = [
                (UnitInfo.MAN_AT_ARMS.ID, 6 + wave_num * 2),
                (FLAMING_CAMEL_ID, 2),
                (UnitInfo.BATTERING_RAM.ID, 1),
            ]
            g2_s_comp = [
                (UnitInfo.ELITE_JANISSARY.ID, 2 + wave_num),
                (UnitInfo.SPEARMAN.ID, 6),
            ]
            g2_m_comp = []
            g3_n_comp = []
            g3_e_comp = []
        elif wave_num <= 5:
            mult = wave_num - 1
            g1_n_comp = [
                (ELITE_BERSERK_ID, 6 + mult * 2),
                (PETARD_ID, 3 + mult),
                (UnitInfo.CAPPED_RAM.ID, 2),
            ]
            g1_e_comp = [
                (UnitInfo.HUSKARL.ID, 6 + mult * 2),
                (FLAMING_CAMEL_ID, 3 + mult),
                (UnitInfo.CAPPED_RAM.ID, 2),
            ]
            g2_s_comp = [
                (UnitInfo.ELITE_JANISSARY.ID, 4 + mult),
                (SIEGE_ONAGER_ID, 1 + (mult // 2)),
                (UnitInfo.PIKEMAN.ID, 8),
            ]
            g2_m_comp = [
                (IMAM_UNIT_ID, 2),
                (UnitInfo.MISSIONARY.ID, 3),
                (UnitInfo.KNIGHT.ID, 6 + mult * 2),
                (UnitInfo.CAPPED_RAM.ID, 2),
            ]
            g3_n_comp = [(ELITE_BATTLE_ELEPHANT_ID, 2 + mult), (UnitInfo.KNIGHT.ID, 6)]
            g3_e_comp = [(UnitInfo.CROSSBOWMAN.ID, 8 + mult * 2), (SIEGE_ONAGER_ID, 1)]
        else:
            mult = wave_num - 4
            g1_n_comp = [
                (ELITE_BERSERK_ID, 10 + mult * 2),
                (PETARD_ID, 5 + mult),
                (UnitInfo.SIEGE_RAM.ID, 3),
            ]
            g1_e_comp = [
                (UnitInfo.HUSKARL.ID, 12 + mult * 2),
                (FLAMING_CAMEL_ID, 5 + mult),
                (UnitInfo.SIEGE_RAM.ID, 3),
            ]
            g2_s_comp = [
                (UnitInfo.ELITE_JANISSARY.ID, 7 + mult),
                (SIEGE_ONAGER_ID, 2 + (mult // 2)),
                (UnitInfo.HALBERDIER.ID, 12),
            ]
            g2_m_comp = [
                (IMAM_UNIT_ID, 2),
                (UnitInfo.MISSIONARY.ID, 4),
                (UnitInfo.CAVALIER.ID, 10 + mult * 2),
                (UnitInfo.SIEGE_RAM.ID, 3),
            ]
            g3_n_comp = [
                (ELITE_BATTLE_ELEPHANT_ID, 4 + mult),
                (UnitInfo.PALADIN.ID, 8 + mult * 2),
                (UnitInfo.SIEGE_RAM.ID, 3),
            ]
            g3_e_comp = [
                (ELITE_BATTLE_ELEPHANT_ID, 4 + mult),
                (UnitInfo.ARBALESTER.ID, 12 + mult * 2),
                (SIEGE_ONAGER_ID, 2),
            ]

        per_settlement_wave = [
            ("G1_North", PlayerId.FIVE, g1_n_comp, 48, 86, *gate_north),
            ("G1_East", PlayerId.FIVE, g1_e_comp, 120, 162, *gate_east),
            ("G2_Snipers", PlayerId.SIX, g2_s_comp, 68, 48, *gate_north),
            ("G2_Mages", PlayerId.SEVEN, g2_m_comp, 118, 114, *gate_center),
            ("G3_North", PlayerId.EIGHT, g3_n_comp, 128, 36, *gate_center),
            ("G3_East", PlayerId.EIGHT, g3_e_comp, 160, 62, *gate_east),
        ]

        for s_key, ai_p, comp, sx, sy, tx, ty in per_settlement_wave:
            if not comp:
                continue
            t_w = tm.add_trigger(
                f"03_W{wave_num:02d}_{s_key}",
                enabled=not is_endless_last,
                looping=loop_flag,
            )
            safe_call(t_w.new_condition.timer, timer=cond_time)
            add_spawn_and_attack_effect(
                t_w, ai_p, comp, spawn_x=sx, spawn_y=sy, target_x=tx, target_y=ty
            )

            if s_key == "G2_Mages":
                safe_call(
                    t_w.new_effect.activate_trigger, trigger_id=t_shield_on.trigger_id
                )

            all_settlement_wave_triggers[s_key].append(t_w)

            if is_endless_last:
                t_enable_endless = tm.add_trigger(
                    f"03_Enable_Endless_{s_key}", enabled=True, looping=False
                )
                safe_call(t_enable_endless.new_condition.timer, timer=wave_time)
                safe_call(
                    t_enable_endless.new_effect.activate_trigger,
                    trigger_id=t_w.trigger_id,
                )
                safe_call(
                    t_enable_endless.new_effect.activate_trigger,
                    trigger_id=t_ann.trigger_id,
                )
                all_settlement_wave_triggers[s_key].append(t_enable_endless)

    # ==============================================================================
    # 9. LOGIKA 4 QUESTÓW (POPRAWIONE MALEJĄCE DESCRIPTION_ORDER: 100 -> 96)
    # ==============================================================================
    t_obj_header_q = tm.add_trigger("00_Obj_Header_Quests", enabled=True, looping=False)
    safe_call(t_obj_header_q.new_condition.timer, timer=99999)
    set_as_objective(t_obj_header_q, "-- QUESTY POBOCZNE --", order=100, is_header=True)

    # QUEST 1: Karawanseraj Południowy (order=99)
    t_q1 = tm.add_trigger("06_Quest1_Unlock_Trade", enabled=True, looping=False)
    set_as_objective(t_q1, "Q1 - Karawanseraj (zasoby + handel)", order=99)
    safe_call(t_q1.new_condition.destroy_object, unit_object=q1_bldg.reference_id)
    safe_call(
        t_q1.new_effect.create_object,
        object_list_unit_id=BuildingInfo.MARKET.ID,
        source_player=PlayerId.TWO,
        location_x=152,
        location_y=190,
    )
    safe_call(
        t_q1.new_effect.create_object,
        object_list_unit_id=BuildingInfo.MARKET.ID,
        source_player=PlayerId.ONE,
        location_x=158,
        location_y=190,
    )
    for h_p in human_players:
        for i in range(3):
            px, py = p_coords[h_p]
            safe_call(
                t_q1.new_effect.create_object,
                object_list_unit_id=UnitInfo.TRADE_CART_EMPTY.ID,
                source_player=h_p,
                location_x=px + i,
                location_y=py + 5,
            )
        add_player_resource(t_q1, h_p, RES_GOLD, 500)
    send_highlight_chat(
        t_q1,
        "<GREEN>",
        "=== [Q1 UKONCZONY!] === Karawanseraj zburzony! Wszyscy otrzymuja +500 Zlota, 3 Wozy Handlowe i Targowiska na poludniu!",
        flare_x=154,
        flare_y=188,
    )

    # QUEST 2: Klif Artylerii (order=98)
    t_q2 = tm.add_trigger("06_Quest2_Sniper_Cliff_Buff", enabled=True, looping=False)
    set_as_objective(t_q2, "Q2 - Klif Artylerii (ulepszenia + atak)", order=98)
    safe_call(t_q2.new_condition.destroy_object, unit_object=q2_bldg.reference_id)
    research_techs(
        t_q2,
        human_players,
        [TECH_BALLISTICS, TECH_CHEMISTRY, TECH_SIEGE_ENGINEERS, TECH_THUMB_RING],
    )
    buffed_units = [
        UnitInfo.LIGHT_CAVALRY.ID,
        UnitInfo.KNIGHT.ID,
        UnitInfo.CAVALIER.ID,
        UnitInfo.PALADIN.ID,
        UnitInfo.CROSSBOWMAN.ID,
        UnitInfo.ARBALESTER.ID,
        UnitInfo.CAVALRY_ARCHER.ID,
    ]
    for h_p in human_players:
        for u_id in buffed_units:
            safe_modify_attribute(
                t_q2, h_p, u_id, ATTR_MOVEMENT_SPEED, Operation.MULTIPLY, 1.12
            )
            safe_modify_attribute(
                t_q2, h_p, u_id, ATTR_ATTACK, Operation.ADD, 4, armor_class=4
            )
            safe_modify_attribute(
                t_q2, h_p, u_id, ATTR_ATTACK, Operation.ADD, 4, armor_class=3
            )
    send_highlight_chat(
        t_q2,
        "<GREEN>",
        "=== [Q2 UKONCZONY!] === Klif Artylerii zdobyty! Wszyscy otrzymuja Balistyke, Chemie, Siege Engineers, +4 Ataku i +12% szybkosci!",
        flare_x=q2_pos[0],
        flare_y=q2_pos[1],
    )

    # QUEST 3: Skarbiec Krasnoludów (order=97)
    t_q3_unlock = tm.add_trigger(
        "06a_Quest3_Siege_Vault_Unlock", enabled=True, looping=False
    )
    set_as_objective(t_q3_unlock, "Q3 - Skarbiec (zasoby + staly dochod)", order=97)
    t_q3_trickle = tm.add_trigger(
        "06b_Quest3_Passive_Resource_Trickle", enabled=False, looping=True
    )
    safe_call(
        t_q3_unlock.new_condition.destroy_object, unit_object=q3_bldg.reference_id
    )
    safe_call(
        t_q3_unlock.new_effect.activate_trigger, trigger_id=t_q3_trickle.trigger_id
    )
    for h_p in human_players:
        add_player_resource(t_q3_unlock, h_p, RES_GOLD, 400)
        add_player_resource(t_q3_unlock, h_p, RES_FOOD, 400)
        add_player_resource(t_q3_unlock, h_p, RES_WOOD, 400)
    send_highlight_chat(
        t_q3_unlock,
        "<GREEN>",
        "=== [Q3 UKONCZONY!] === Skarbiec zdobyty! +400 surowcow od reki ORAZ staly dochod co minute dla kazdego gracza!",
        flare_x=q3_pos[0],
        flare_y=q3_pos[1],
    )

    safe_call(t_q3_trickle.new_condition.timer, timer=60)
    tr_res = BALANCE["quest3_trickle"]
    for h_p in human_players:
        add_player_resource(t_q3_trickle, h_p, RES_FOOD, tr_res["food"])
        add_player_resource(t_q3_trickle, h_p, RES_WOOD, tr_res["wood"])
        add_player_resource(t_q3_trickle, h_p, RES_GOLD, tr_res["gold"])

    # QUEST 4: Krwawy Ołtarz (order=96)
    t_q4 = tm.add_trigger(
        "06_Quest4_Blood_Altar_Weaken_Mages", enabled=True, looping=False
    )
    set_as_objective(t_q4, "Q4 - Krwawy Oltarz (+50 HP i slabsi Magowie)", order=96)
    safe_call(t_q4.new_condition.destroy_object, unit_object=q4_bldg.reference_id)
    safe_modify_attribute(
        t_q4, PlayerId.SEVEN, IMAM_UNIT_ID, ATTR_HIT_POINTS, Operation.SET, 120
    )
    for h_p in human_players:
        for u_id in buffed_units + [UnitInfo.PIKEMAN.ID, UnitInfo.HALBERDIER.ID]:
            safe_modify_attribute(t_q4, h_p, u_id, ATTR_HIT_POINTS, Operation.ADD, 50)
    send_highlight_chat(
        t_q4,
        "<GREEN>",
        "=== [Q4 UKONCZONY!] === Krwawy Oltarz zburzony! Magowie wroga traca 80% zycia, a Wasze wojska zyskuja na stale +50 Max HP!",
        flare_x=q4_pos[0],
        flare_y=q4_pos[1],
    )

    # ==============================================================================
    # 10. ZNISZCZENIE 6 SETTLEMENTÓW (MALEJĄCE DESCRIPTION_ORDER: 90 -> 84)
    # ==============================================================================
    t_obj_header_s = tm.add_trigger(
        "00_Obj_Header_Settlements", enabled=True, looping=False
    )
    safe_call(t_obj_header_s.new_condition.timer, timer=99999)
    set_as_objective(
        t_obj_header_s, "-- SETTLEMENTY HORDY --", order=90, is_header=True
    )

    settlement_defs = [
        (
            "G1_North",
            s_g1_north,
            "G1 - Polnocny (usuwa Berserkerow i Petardy)",
            89,
            *s_coords["G1_North"],
        ),
        (
            "G1_East",
            s_g1_east,
            "G1 - Wschodni (usuwa Huskarlow i Wielblady)",
            88,
            *s_coords["G1_East"],
        ),
        (
            "G2_Snipers",
            s_g2_snipers,
            "G2 - Akademia (usuwa Snajperow i Kolosy)",
            87,
            *s_coords["G2_Snipers"],
        ),
        (
            "G2_Mages",
            s_g2_mages,
            "G2 - Klasztor (usuwa Magow i Szamanow)",
            86,
            *s_coords["G2_Mages"],
        ),
        (
            "G3_North",
            s_g3_north,
            "G3 - Cytadela Pln. (usuwa Tytanow Pln.)",
            85,
            *s_coords["G3_North"],
        ),
        (
            "G3_East",
            s_g3_east,
            "G3 - Cytadela Wsch. (usuwa Tytanow Wsch.)",
            84,
            *s_coords["G3_East"],
        ),
    ]

    for s_key, core_unit, obj_label, obj_order, sx, sy in settlement_defs:
        t_destroy = tm.add_trigger(
            f"05_Settlement_Destroyed_{s_key}", enabled=True, looping=False
        )
        set_as_objective(t_destroy, obj_label, order=obj_order)
        safe_call(
            t_destroy.new_condition.destroy_object, unit_object=core_unit.reference_id
        )

        for tr_w in all_settlement_wave_triggers[s_key]:
            safe_call(
                t_destroy.new_effect.deactivate_trigger, trigger_id=tr_w.trigger_id
            )

        for h_p in human_players:
            add_player_resource(t_destroy, h_p, RES_GOLD, 500)
            add_player_resource(t_destroy, h_p, RES_FOOD, 500)

        for ai_p in ai_players:
            for u_id in all_enemy_combat_units:
                safe_modify_attribute(
                    t_destroy, ai_p, u_id, ATTR_HIT_POINTS, Operation.ADD, 30
                )
                safe_modify_attribute(
                    t_destroy, ai_p, u_id, ATTR_ATTACK, Operation.ADD, 2, armor_class=4
                )
                safe_modify_attribute(
                    t_destroy, ai_p, u_id, ATTR_ATTACK, Operation.ADD, 2, armor_class=3
                )

        add_spawn_and_attack_effect(
            t_destroy,
            PlayerId.EIGHT,
            [
                (ELITE_BATTLE_ELEPHANT_ID, 4),
                (UnitInfo.CAVALIER.ID, 10),
                (UnitInfo.HALBERDIER.ID, 12),
            ],
            spawn_x=118,
            spawn_y=114,
            target_x=gate_center[0],
            target_y=gate_center[1],
        )

        send_highlight_chat(
            t_destroy,
            "<AQUA>",
            f"=== [SETTLEMENT ZNISZCZONY: {s_key}] === Jego oddzialy znikaja z fal (+500 Zlota/Zywnosci), ALE pozostale obozy wpadaja w FURIE (+30 HP, +2 Ataku + Fala Odwetowa)!",
            flare_x=sx,
            flare_y=sy,
        )

    # 11. Warunki Zwycięstwa i Porażki
    t_win = tm.add_trigger(
        "07_Victory_All_6_Settlements_Destroyed", enabled=True, looping=False
    )
    for _, core_unit, _, _, _, _ in settlement_defs:
        safe_call(
            t_win.new_condition.destroy_object, unit_object=core_unit.reference_id
        )
    for h_p in human_players:
        safe_call(t_win.new_effect.declare_victory, source_player=h_p, enabled=1)

    t_lose = tm.add_trigger("08_Defeat_Citadel_Lost", enabled=True, looping=False)
    safe_call(
        t_lose.new_condition.destroy_object, unit_object=allied_citadel.reference_id
    )
    for ai_p in ai_players:
        safe_call(t_lose.new_effect.declare_victory, source_player=ai_p, enabled=1)

    scenario.write_to_file(str(OUTPUT_SCENARIO))
    print(f"Gotowe! Scenariusz Hordy (v3.2 Ruff-clean) zapisano w: {OUTPUT_SCENARIO}")


if __name__ == "__main__":
    build_horde_scenario()
