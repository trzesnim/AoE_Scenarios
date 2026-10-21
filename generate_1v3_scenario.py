import inspect
import math
from pathlib import Path

from AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario
from AoE2ScenarioParser.datasets.players import PlayerId
from AoE2ScenarioParser.datasets.units import UnitInfo
from AoE2ScenarioParser.datasets.buildings import BuildingInfo
from AoE2ScenarioParser.datasets.other import OtherInfo
from AoE2ScenarioParser.datasets.terrains import TerrainId
from AoE2ScenarioParser.datasets.trigger_lists import DiplomacyState, Operation

# ID obiektów Gai (Drzewa, Skały/Klify, Relikty)
TREE_OAK_ID = 349
TREE_PINE_ID = 350
ROCK_CLIFF_ID = 623
RELIC_ID = 285

# ID terenów wodnych w AoE2: DE
TERRAIN_WATER = 1
TERRAIN_BEACH = 2
TERRAIN_SHALLOWS = 4

# ID zasobów gracza
RES_FOOD = 0
RES_WOOD = 1
RES_STONE = 2
RES_GOLD = 3
RES_BONUS_POP_CAP = 32


def safe_call(func, **kwargs):
    sig = inspect.signature(func)
    valid_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
    return func(**valid_kwargs)


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
OUTPUT_SCENARIO = SCENARIO_FOLDER / "Upadek_Imperium_1v3.aoe2scenario"

MAP_SIZE = 160

BALANCE = {
    "hold_time_seconds": 45 * 60,
    "p1_bonus_pop": 80,
    "tax_interval_sec": 60,
    "tax_per_outpost": {"gold": 90, "food": 90, "wood": 60},
    "bounty_per_outpost": {"gold": 400, "food": 400},
    "starting_resources": {
        PlayerId.ONE:   {"food": 600, "wood": 600, "gold": 400, "stone": 400},
        PlayerId.TWO:   {"food": 300, "wood": 300, "gold": 200, "stone": 200},
        PlayerId.THREE: {"food": 350, "wood": 350, "gold": 200, "stone": 250},
        PlayerId.FOUR:  {"food": 400, "wood": 400, "gold": 250, "stone": 250},
    },
}


# ==============================================================================
# DWUWARSTWOWY SYSTEM SIATKI (ZERO BRAKUJĄCYCH JEDNOSTEK + ZERO KOLIZJI)
# ==============================================================================
class SafeMapGrid:
    def __init__(self, size: int):
        self.size = size
        self.occupied_tiles: set[tuple[int, int]] = set()
        self.no_tree_zones: set[tuple[int, int]] = set()
        self.elev: list[list[int]] = [[0 for _ in range(size)] for _ in range(size)]

    def in_bounds(self, x: int, y: int, margin: int = 2) -> bool:
        return margin <= x < self.size - margin and margin <= y < self.size - margin

    def mark_no_trees(self, cx: int, cy: int, radius: int):
        for x in range(max(0, cx - radius), min(self.size, cx + radius + 1)):
            for y in range(max(0, cy - radius), min(self.size, cy + radius + 1)):
                self.no_tree_zones.add((x, y))

    def place_building(self, um, player: PlayerId, building_id: int, cx: int, cy: int, size_tiles: int, no_tree_margin: int = 3):
        """Stawia budynek i blokuje wyłącznie jego dokładny obrys w occupied_tiles."""
        if size_tiles % 2 == 0:
            half = size_tiles // 2
            x_range = range(cx - half, cx + half)
            y_range = range(cy - half, cy + half)
            bx, by = float(cx), float(cy)
        else:
            half = size_tiles // 2
            x_range = range(cx - half, cx + half + 1)
            y_range = range(cy - half, cy + half + 1)
            bx, by = cx + 0.5, cy + 0.5

        for x in x_range:
            for y in y_range:
                self.occupied_tiles.add((x, y))
        self.mark_no_trees(cx, cy, size_tiles // 2 + no_tree_margin)
        return um.add_unit(player=player, unit_const=building_id, x=bx, y=by)

    def place_unit(self, um, player: PlayerId, unit_id: int, x: int, y: int, no_tree_margin: int = 2):
        """Stawia jednostkę lub złoże 1x1. Jeśli kafelek jest zajęty, znajduje najbliższy wolny obok."""
        for r in range(0, 6):
            for dx in range(-r, r + 1):
                for dy in range(-r, r + 1):
                    if abs(dx) != r and abs(dy) != r:
                        continue
                    nx, ny = x + dx, y + dy
                    if self.in_bounds(nx, ny) and (nx, ny) not in self.occupied_tiles:
                        self.occupied_tiles.add((nx, ny))
                        if no_tree_margin > 0:
                            self.mark_no_trees(nx, ny, no_tree_margin)
                        return um.add_unit(player=player, unit_const=unit_id, x=nx + 0.5, y=ny + 0.5)
        return None

    def place_wall_tile(self, um, player: PlayerId, wall_id: int, x: int, y: int):
        """Stawia pojedynczy segment muru na dokładnym kafelku (x, y)."""
        if self.in_bounds(x, y) and (x, y) not in self.occupied_tiles:
            self.occupied_tiles.add((x, y))
            self.mark_no_trees(x, y, 1)
            return um.add_unit(player=player, unit_const=wall_id, x=x + 0.5, y=y + 0.5)
        return None

    def add_hill_plateau(self, cx: int, cy: int, flat_radius: int, height: int):
        """Tworzy płaskowyż o wysokości `height` z łagodnym zejściem."""
        total_r = flat_radius + height
        for x in range(max(0, cx - total_r), min(self.size, cx + total_r + 1)):
            for y in range(max(0, cy - total_r), min(self.size, cy + total_r + 1)):
                dist = max(abs(x - cx), abs(y - cy))
                h = max(0, min(height, flat_radius + height - dist))
                if h > self.elev[x][y]:
                    self.elev[x][y] = h

    def apply_smooth_elevation(self, mm):
        """Wymusza warunek silnika Genie (|dh| <= 1 między sąsiadami) i zapisuje wysokość do mapy."""
        for x in range(self.size):
            for y in range(self.size):
                for dx, dy in [(-1, 0), (0, -1), (-1, -1), (-1, 1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.size and 0 <= ny < self.size:
                        if self.elev[x][y] > self.elev[nx][ny] + 1:
                            self.elev[x][y] = self.elev[nx][ny] + 1
        for x in range(self.size - 1, -1, -1):
            for y in range(self.size - 1, -1, -1):
                for dx, dy in [(1, 0), (0, 1), (1, 1), (1, -1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.size and 0 <= ny < self.size:
                        if self.elev[x][y] > self.elev[nx][ny] + 1:
                            self.elev[x][y] = self.elev[nx][ny] + 1
        for x in range(self.size):
            for y in range(self.size):
                mm.get_tile(x, y).elevation = self.elev[x][y]


# ==============================================================================
# FUNKCJE RZEŹBY TERENU, ORGANICZNYCH LASÓW, KLIFÓW I BAZ
# ==============================================================================
def add_player_resource(trigger, player: PlayerId, resource_id: int, amount: int):
    safe_call(
        trigger.new_effect.modify_resource,
        source_player=player,
        tribute_list=resource_id,
        operation=Operation.ADD,
        quantity=int(amount),
    )


def paint_natural_biome_background(mm, size: int):
    """Tworzy urozmaicone podłoże (mieszanka traw i ziemi zamiast jednolitej planszy)."""
    for x in range(size):
        for y in range(size):
            n = math.sin(x * 0.09) * math.cos(y * 0.09) + 0.5 * math.sin((x + y) * 0.05)
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


def paint_organic_forest(mm, cx: int, cy: int, radius: float, terrain_id: int, seed: float = 0.0):
    """Maluje nieregularny, organiczny kształt lasu za pomocą fal harmonicznych."""
    max_r = int(radius * 1.6) + 2
    for x in range(max(2, cx - max_r), min(MAP_SIZE - 2, cx + max_r + 1)):
        for y in range(max(2, cy - max_r), min(MAP_SIZE - 2, cy + max_r + 1)):
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
            elif dist <= eff_r + 1.5 and mm.get_tile(x, y).terrain_id == TerrainId.GRASS_1:
                mm.get_tile(x, y).terrain_id = TerrainId.GRASS_2


def build_rocky_cliff_ridge(mm, um, grid: SafeMapGrid, x1: int, y1: int, x2: int, y2: int, height: int = 2):
    """Tworzy funkcjonalną skalistą grań (klif) z głazami i podwyższeniem terenu."""
    steps = int(math.hypot(x2 - x1, y2 - y1))
    for i in range(steps + 1):
        t = i / max(1, steps)
        # Lekkie wygięcie łuku grani
        curve = math.sin(t * math.pi) * 3.0
        rx = int(round(x1 + (x2 - x1) * t + curve))
        ry = int(round(y1 + (y2 - y1) * t - curve))
        grid.add_hill_plateau(rx, ry, flat_radius=1, height=height)
        set_circle_terrain(mm, rx, ry, radius=2, terrain_id=TerrainId.DIRT_3)
        grid.mark_no_trees(rx, ry, radius=3)
        if i % 2 == 0 and grid.in_bounds(rx, ry) and (rx, ry) not in grid.occupied_tiles:
            grid.place_unit(um, PlayerId.GAIA, ROCK_CLIFF_ID, rx, ry, no_tree_margin=2)


def set_road(mm, grid: SafeMapGrid, x1: int, y1: int, x2: int, y2: int, width: int = 1):
    steps = int(math.hypot(x2 - x1, y2 - y1) * 2)
    for i in range(steps + 1):
        t = i / max(1, steps)
        rx = int(round(x1 + (x2 - x1) * t))
        ry = int(round(y1 + (y2 - y1) * t))
        set_circle_terrain(mm, rx, ry, width, TerrainId.ROAD)
        grid.mark_no_trees(rx, ry, width + 2)


def populate_forest_trees(mm, um, grid: SafeMapGrid):
    """Sadzi drzewa na kafelkach leśnych poza strefami baz i dróg."""
    for x in range(2, MAP_SIZE - 2):
        for y in range(2, MAP_SIZE - 2):
            if (x, y) in grid.occupied_tiles or (x, y) in grid.no_tree_zones:
                continue
            t_id = mm.get_tile(x, y).terrain_id
            if t_id == TerrainId.FOREST_OAK:
                grid.place_unit(um, PlayerId.GAIA, TREE_OAK_ID, x, y, no_tree_margin=0)
            elif t_id == TerrainId.FOREST_PINE:
                grid.place_unit(um, PlayerId.GAIA, TREE_PINE_ID, x, y, no_tree_margin=0)


def spawn_resource_cluster(um, grid: SafeMapGrid, cx: int, cy: int, res_const: int, count: int = 6):
    offsets = [(0, 0), (1, 0), (0, 1), (1, 1), (2, 0), (0, 2), (2, 1), (1, 2), (2, 2), (3, 0)]
    for dx, dy in offsets[:count]:
        grid.place_unit(um, PlayerId.GAIA, res_const, cx + dx, cy + dy, no_tree_margin=3)


def spawn_starting_base(um, grid: SafeMapGrid, player: PlayerId, cx: int, cy: int, extra_tc: bool = False):
    # Chroni bazę wyłącznie przed zarastaniem lasem (NIE blokuje stawiania jednostek i kopalń!)
    grid.mark_no_trees(cx, cy, radius=15)

    # Główne Town Center (4x4)
    grid.place_building(um, player, BuildingInfo.TOWN_CENTER.ID, cx, cy, size_tiles=4, no_tree_margin=4)

    # 6 wieśniaków + zwiadowca
    for dx, dy in [(-3, -2), (-3, -1), (-3, 0), (-3, 1), (-2, -3), (-1, -3)]:
        grid.place_unit(um, player, UnitInfo.VILLAGER_MALE.ID, cx + dx, cy + dy, no_tree_margin=1)
    grid.place_unit(um, player, UnitInfo.SCOUT_CAVALRY.ID, cx + 4, cy, no_tree_margin=1)

    # Pojedyncze drzewa startowe (Straggler Trees) wokół TC
    for tx, ty in [(-5, -3), (4, -4), (-4, 4), (4, 3)]:
        grid.place_unit(um, PlayerId.GAIA, TREE_OAK_ID, cx + tx, cy + ty, no_tree_margin=0)

    if extra_tc:
        tc2_x, tc2_y = cx + 10, cy - 8
        grid.place_building(um, player, BuildingInfo.TOWN_CENTER.ID, tc2_x, tc2_y, size_tiles=4, no_tree_margin=3)
        for i in range(4):
            grid.place_unit(um, player, UnitInfo.VILLAGER_MALE.ID, tc2_x - 2 + i, tc2_y + 3, no_tree_margin=1)

    # Jagody, 2x złoto, 1x kamień
    spawn_resource_cluster(um, grid, cx - 9, cy - 7, OtherInfo.FORAGE_BUSH.ID, count=6)
    spawn_resource_cluster(um, grid, cx + 8, cy + 6, OtherInfo.GOLD_MINE.ID, count=7)
    spawn_resource_cluster(um, grid, cx - 10, cy + 6, OtherInfo.GOLD_MINE.ID, count=5)
    spawn_resource_cluster(um, grid, cx - 1, cy + 9, OtherInfo.STONE_MINE.ID, count=5)

    # 6 owiec, 2 dziki i 4 jelenie
    for sx, sy in [(-3, 2), (-2, 2), (-1, 2), (0, 2), (-3, 3), (-2, 3)]:
        grid.place_unit(um, PlayerId.GAIA, UnitInfo.SHEEP.ID, cx + sx, cy + sy, no_tree_margin=1)

    grid.place_unit(um, PlayerId.GAIA, UnitInfo.WILD_BOAR.ID, cx - 11, cy - 1, no_tree_margin=1)
    grid.place_unit(um, PlayerId.GAIA, UnitInfo.WILD_BOAR.ID, cx + 1, cy - 11, no_tree_margin=1)

    for dx, dy in [(7, -11), (8, -11), (7, -12), (8, -12)]:
        grid.place_unit(um, PlayerId.GAIA, UnitInfo.DEER.ID, cx + dx, cy + dy, no_tree_margin=1)


def build_rectangular_wall_with_gates(um, grid: SafeMapGrid, player: PlayerId, cx: int, cy: int, half_size: int):
    x_min, x_max = cx - half_size, cx + half_size
    y_min, y_max = cy - half_size, cy + half_size

    # Ciągły mur kamienny z czystymi, 4-kratkowymi przerwami na 4 bramy
    for x in range(x_min, x_max + 1):
        if abs(x - cx) <= 2:
            continue
        grid.place_wall_tile(um, player, BuildingInfo.STONE_WALL.ID, x, y_min)
        grid.place_wall_tile(um, player, BuildingInfo.STONE_WALL.ID, x, y_max)

    for y in range(y_min + 1, y_max):
        if abs(y - cy) <= 2:
            continue
        grid.place_wall_tile(um, player, BuildingInfo.STONE_WALL.ID, x_min, y)
        grid.place_wall_tile(um, player, BuildingInfo.STONE_WALL.ID, x_max, y)

    # Wieże strażnicze stoją 2 kratki WEWNĄTRZ muru (zero kolizji z linią muru!)
    tower_spots = [
        (x_min + 2, y_min + 2), (x_min + 2, y_max - 2),
        (x_max - 2, y_min + 2), (x_max - 2, y_max - 2),
        (cx - 5, y_min + 2), (cx + 5, y_min + 2),
        (cx - 5, y_max - 2), (cx + 5, y_max - 2),
        (x_min + 2, cy - 5), (x_min + 2, cy + 5),
    ]
    for tx, ty in tower_spots:
        grid.place_building(um, player, BuildingInfo.GUARD_TOWER.ID, tx, ty, size_tiles=2, no_tree_margin=2)


# ==============================================================================
# GŁÓWNY GENERATOR SCENARIUSZA
# ==============================================================================
def build_scenario():
    if not INPUT_TEMPLATE.exists():
        raise FileNotFoundError(f"Nie znaleziono pliku szablonu: {INPUT_TEMPLATE}")

    scenario = AoE2DEScenario.from_file(str(INPUT_TEMPLATE))
    tm = scenario.trigger_manager
    um = scenario.unit_manager
    mm = scenario.map_manager
    pm = scenario.player_manager

    tm.triggers = []
    um.units = [[] for _ in range(9)]
    mm.map_size = MAP_SIZE

    grid = SafeMapGrid(MAP_SIZE)

    pm.active_players = 4
    for p_id in [PlayerId.ONE, PlayerId.TWO, PlayerId.THREE, PlayerId.FOUR]:
        p = pm.players[p_id]
        res = BALANCE["starting_resources"][p_id]
        p.food = res["food"]
        p.wood = res["wood"]
        p.gold = res["gold"]
        p.stone = res["stone"]

    # 1. Urozmaicone podłoże i elewacja terenu
    paint_natural_biome_background(mm, MAP_SIZE)

    center = MAP_SIZE // 2
    # Szerokie, płaskie Wzgórze Imperialne w centrum (wysokość 3)
    grid.add_hill_plateau(center, center, flat_radius=24, height=3)
    set_circle_terrain(mm, center, center, radius=24, terrain_id=TerrainId.GRASS_2)

    bases = {
        PlayerId.ONE:   (center - 4, center - 2),
        PlayerId.TWO:   (24, center),
        PlayerId.THREE: (132, 28),
        PlayerId.FOUR:  (132, 132),
    }

    # Płaskie wzniesienia pod bazy koalicji (wysokość 1)
    for p_id in [PlayerId.TWO, PlayerId.THREE, PlayerId.FOUR]:
        bx, by = bases[p_id]
        grid.add_hill_plateau(bx, by, flat_radius=14, height=1)

    outpost_coords = [
        ("Zachodnia Faktoria (Front P2)", 50, center),
        ("Polnocna Faktoria (Szlak P3)", 84, 42),
        ("Poludniowa Faktoria (Szlak P4)", 84, 118),
        ("Wschodnia Faktoria (Styk P3/P4)", 114, center),
    ]
    for _, ox, oy in outpost_coords:
        grid.add_hill_plateau(ox, oy, flat_radius=5, height=2)
        set_circle_terrain(mm, ox, oy, radius=6, terrain_id=TerrainId.DIRT_1)

    # 2. Fosa wokół wzgórza centralnego z 4 brodami (Shallows) na drogach
    for angle_deg in range(0, 360, 2):
        rad = math.radians(angle_deg)
        mx = int(round(center + 31 * math.cos(rad)))
        my = int(round(center + 31 * math.sin(rad)))
        set_circle_terrain(mm, mx, my, radius=1, terrain_id=TERRAIN_WATER)
        grid.mark_no_trees(mx, my, radius=2)

    # Drogi i brody (Shallows) przecinające fosę
    for p_id in [PlayerId.TWO, PlayerId.THREE, PlayerId.FOUR]:
        bx, by = bases[p_id]
        set_road(mm, grid, bx, by, center, center, width=1)
    for fx, fy in [(center - 31, center), (center + 31, center), (center, center - 31), (center, center + 31)]:
        set_circle_terrain(mm, fx, fy, radius=3, terrain_id=TERRAIN_SHALLOWS)

    # Skaliste granie (klify) osłaniające flanki
    build_rocky_cliff_ridge(mm, um, grid, 36, 36, 62, 22, height=3)
    build_rocky_cliff_ridge(mm, um, grid, 36, 124, 62, 138, height=3)
    build_rocky_cliff_ridge(mm, um, grid, 126, 62, 138, 98, height=2)

    # Wyliczenie i nałożenie gładkiej, w 100% bezpiecznej siatki wysokości
    grid.apply_smooth_elevation(mm)

    # 3. Stawianie baz, murów, Faktorii i Reliktów
    spawn_starting_base(um, grid, PlayerId.ONE, *bases[PlayerId.ONE], extra_tc=True)
    spawn_starting_base(um, grid, PlayerId.TWO, *bases[PlayerId.TWO], extra_tc=False)
    spawn_starting_base(um, grid, PlayerId.THREE, *bases[PlayerId.THREE], extra_tc=False)
    spawn_starting_base(um, grid, PlayerId.FOUR, *bases[PlayerId.FOUR], extra_tc=False)

    # Dodatkowe złoża na przedpolu dla P2, P3, P4
    spawn_resource_cluster(um, grid, 40, center - 16, OtherInfo.GOLD_MINE.ID, count=6)
    spawn_resource_cluster(um, grid, 40, center + 16, OtherInfo.STONE_MINE.ID, count=5)
    spawn_resource_cluster(um, grid, 118, 52, OtherInfo.GOLD_MINE.ID, count=6)
    spawn_resource_cluster(um, grid, 118, 108, OtherInfo.GOLD_MINE.ID, count=6)

    # 4 Relikty w strategicznych punktach mapy
    for rx, ry in [(44, 48), (44, 112), (112, 48), (112, 112)]:
        grid.place_unit(um, PlayerId.GAIA, RELIC_ID, rx, ry, no_tree_margin=2)

    build_rectangular_wall_with_gates(um, grid, PlayerId.ONE, center, center, half_size=22)

    imperial_monument = grid.place_building(
        um, PlayerId.ONE, BuildingInfo.MONUMENT.ID, cx=center + 4, cy=center + 4, size_tiles=2, no_tree_margin=2
    )
    grid.place_building(
        um, PlayerId.ONE, BuildingInfo.CASTLE.ID, cx=center - 8, cy=center + 12, size_tiles=4, no_tree_margin=3
    )

    outpost_buildings = []
    for name, ox, oy in outpost_coords:
        main_tower = grid.place_building(
            um, PlayerId.ONE, BuildingInfo.KEEP.ID, cx=ox, cy=oy, size_tiles=2, no_tree_margin=3
        )
        spawn_resource_cluster(um, grid, ox + 4, oy - 4, OtherInfo.GOLD_MINE.ID, count=5)
        for gx, gy in [(-3, -2), (-3, 2), (3, -2), (3, 2)]:
            grid.place_unit(um, PlayerId.ONE, UnitInfo.PIKEMAN.ID, ox + gx, oy + gy, no_tree_margin=1)
        outpost_buildings.append((name, main_tower))

    # 4. Generowanie 26 organicznych, nieregularnych kompleksów leśnych
    forest_spots = [
        # Lasy w stolicy P1
        (center - 16, center - 15, 4.5, TerrainId.FOREST_OAK, 1.1),
        (center + 16, center - 15, 4.5, TerrainId.FOREST_OAK, 2.3),
        (center + 15, center + 15, 4.0, TerrainId.FOREST_PINE, 0.7),
        # Lasy wokół P2 (Zachód)
        (10, center - 18, 6.5, TerrainId.FOREST_OAK, 0.5),
        (10, center + 18, 6.5, TerrainId.FOREST_OAK, 1.9),
        (26, center - 24, 5.5, TerrainId.FOREST_PINE, 3.1),
        (26, center + 24, 5.5, TerrainId.FOREST_PINE, 4.2),
        # Lasy wokół P3 (NE)
        (112, 10, 6.5, TerrainId.FOREST_PINE, 1.4),
        (148, 26, 6.5, TerrainId.FOREST_OAK, 2.8),
        (146, 10, 6.0, TerrainId.FOREST_PINE, 0.3),
        (100, 22, 5.5, TerrainId.FOREST_OAK, 3.7),
        # Lasy wokół P4 (SE)
        (112, 150, 6.5, TerrainId.FOREST_PINE, 2.1),
        (148, 134, 6.5, TerrainId.FOREST_OAK, 1.2),
        (146, 150, 6.0, TerrainId.FOREST_PINE, 4.0),
        (100, 138, 5.5, TerrainId.FOREST_OAK, 0.9),
        # Lasy taktyczne w polu i na krawędziach mapy
        (64, 18, 6.5, TerrainId.FOREST_OAK, 1.7),
        (64, 142, 6.5, TerrainId.FOREST_OAK, 2.5),
        (18, 22, 7.5, TerrainId.FOREST_PINE, 3.3),
        (18, 138, 7.5, TerrainId.FOREST_PINE, 0.4),
        (62, 60, 4.5, TerrainId.FOREST_OAK, 2.9),
        (62, 100, 4.5, TerrainId.FOREST_OAK, 1.6),
        (102, 62, 5.0, TerrainId.FOREST_PINE, 3.8),
        (102, 98, 5.0, TerrainId.FOREST_PINE, 0.6),
        (146, 68, 6.0, TerrainId.FOREST_OAK, 2.2),
        (146, 92, 6.0, TerrainId.FOREST_OAK, 4.5),
    ]
    for fx, fy, r, t_id, seed in forest_spots:
        paint_organic_forest(mm, fx, fy, radius=r, terrain_id=t_id, seed=seed)

    populate_forest_trees(mm, um, grid)

    # ==============================================================================
    # 5. SYSTEM TRIGGERÓW
    # ==============================================================================
    t_init = tm.add_trigger("01_Init_Setup_And_Balance", enabled=True, looping=False)

    rebel_players = [PlayerId.TWO, PlayerId.THREE, PlayerId.FOUR]
    for r_p in rebel_players:
        safe_call(t_init.new_effect.change_diplomacy, source_player=PlayerId.ONE, target_player=r_p, diplomacy=DiplomacyState.ENEMY)
        safe_call(t_init.new_effect.change_diplomacy, source_player=r_p, target_player=PlayerId.ONE, diplomacy=DiplomacyState.ENEMY)
        for other_r in rebel_players:
            if r_p != other_r:
                safe_call(t_init.new_effect.change_diplomacy, source_player=r_p, target_player=other_r, diplomacy=DiplomacyState.ALLY)

    add_player_resource(t_init, PlayerId.ONE, RES_BONUS_POP_CAP, BALANCE["p1_bonus_pop"])

    safe_call(
        t_init.new_effect.send_chat,
        source_player=PlayerId.ONE,
        message="[UPADEK IMPERIUM 1v3]: P1 broni Monumentu w stolicy przez 45 min. P2, P3 i P4 musza go zburzyc (4 Faktorie daja podatki P1)!",
    )

    tax = BALANCE["tax_per_outpost"]
    bounty = BALANCE["bounty_per_outpost"]

    for idx, (f_name, tower_unit) in enumerate(outpost_buildings, start=1):
        t_tax = tm.add_trigger(f"02_Tax_Loop_Outpost_{idx}", enabled=True, looping=True)
        safe_call(t_tax.new_condition.timer, timer=BALANCE["tax_interval_sec"])

        add_player_resource(t_tax, PlayerId.ONE, RES_GOLD, tax["gold"])
        add_player_resource(t_tax, PlayerId.ONE, RES_FOOD, tax["food"])
        add_player_resource(t_tax, PlayerId.ONE, RES_WOOD, tax["wood"])

        t_destroy = tm.add_trigger(f"03_Destroy_Outpost_{idx}", enabled=True, looping=False)
        safe_call(t_destroy.new_condition.destroy_object, unit_object=tower_unit.reference_id)
        safe_call(t_destroy.new_effect.deactivate_trigger, trigger_id=t_tax.trigger_id)

        for r_p in rebel_players:
            add_player_resource(t_destroy, r_p, RES_GOLD, bounty["gold"])
            add_player_resource(t_destroy, r_p, RES_FOOD, bounty["food"])

        safe_call(
            t_destroy.new_effect.send_chat,
            source_player=PlayerId.ONE,
            message=f"[!] {f_name} zdobyta! Imperator traci 25% podatkow, a Koalicja otrzymuje po +400 Zlota i Zywnosci!",
        )

    t_p1_win = tm.add_trigger("04_Imperator_Timer_Victory", enabled=True, looping=False)
    safe_call(t_p1_win.new_condition.timer, timer=BALANCE["hold_time_seconds"])
    safe_call(t_p1_win.new_effect.declare_victory, source_player=PlayerId.ONE, enabled=1)

    total_minutes = BALANCE["hold_time_seconds"] // 60
    for rem_min in [40, 35, 30, 25, 20, 15, 10, 5, 3, 2, 1]:
        if rem_min >= total_minutes:
            continue
        elapsed_sec = (total_minutes - rem_min) * 60
        t_tick = tm.add_trigger(f"04b_Chat_Timer_{rem_min}m", enabled=True, looping=False)
        safe_call(t_tick.new_condition.timer, timer=elapsed_sec)
        safe_call(
            t_tick.new_effect.send_chat,
            source_player=PlayerId.ONE,
            message=f"[ZEGAR]: Do przybycia Legionow Imperatora pozostalo {rem_min} min!",
        )

    t_rebels_win = tm.add_trigger("05_Coalition_Monument_Destroyed", enabled=True, looping=False)
    safe_call(t_rebels_win.new_condition.destroy_object, unit_object=imperial_monument.reference_id)
    for r_p in rebel_players:
        safe_call(t_rebels_win.new_effect.declare_victory, source_player=r_p, enabled=1)

    scenario.write_to_file(str(OUTPUT_SCENARIO))
    print(f"Gotowe! Scenariusz 1v3 zapisano w: {OUTPUT_SCENARIO}")


if __name__ == "__main__":
    build_scenario()