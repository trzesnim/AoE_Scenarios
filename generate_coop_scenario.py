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

TREE_OAK_ID = 349
TREE_PINE_ID = 350
ROCK_CLIFF_ID = 623
RELIC_ID = 285

TERRAIN_WATER = 1
TERRAIN_SHALLOWS = 4

RES_FOOD = 0
RES_WOOD = 1
RES_STONE = 2
RES_GOLD = 3
RES_BONUS_POP_CAP = 32

ATTR_HIT_POINTS = 0
ATTR_WORK_RATE = 13

# Oficjalne ID Technologii w silniku AoE2: DE
TECH_FEUDAL_AGE = 101
TECH_CASTLE_AGE = 102
TECH_IMPERIAL_AGE = 103

# Kuźnia - Piechota i Kawaleria (Atak)
TECH_FORGING = 67
TECH_IRON_CASTING = 68
TECH_BLAST_FURNACE = 75

# Kuźnia - Pancerz Piechoty + Szybkość
TECH_SCALE_MAIL = 74
TECH_CHAIN_MAIL = 76
TECH_PLATE_MAIL = 77
TECH_SQUIRES = 215

# Kuźnia i Stajnia - Pancerz, HP i Szybkość Kawalerii
TECH_SCALE_BARDING = 81
TECH_CHAIN_BARDING = 82
TECH_PLATE_BARDING = 80
TECH_BLOODLINES = 435
TECH_HUSBANDRY = 39

# Strzelnica i Uniwersytet - Zasięg, Atak i Celność
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


def research_techs(trigger, players: list[PlayerId], tech_ids: list[int]):
    """Bada listę technologii dla wskazanych graczy."""
    for p in players:
        for t_id in tech_ids:
            safe_call(
                trigger.new_effect.research_technology,
                source_player=p,
                technology=t_id,
                force_research_technology=1,
            )


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
OUTPUT_SCENARIO = SCENARIO_FOLDER / "Operacja_Zelazny_Krag_Coop.aoe2scenario"

MAP_SIZE = 180

BALANCE = {
    "p1_bonus_pop": 50,

    # Ramy czasowe 3 Faz Rozgrywki (Feudal -> Castle -> Imperial)
    "phase1_feudal_start_sec": 660,    # 11:00 - Start fal Fazy I (Feudalnej) i technologii Feudalnych AI
    "phase2_castle_start_sec": 1200,   # 20:00 - Przejście fal w Fazę II (Castle Age) i technologie Zamkowe AI
    "phase3_imperial_start_sec": 1920, # 32:00 - Przejście fal w Fazę III (Imperial Age) i technologie Imperialne AI

    "siege_wave_interval_sec": 270,    # Co 4,5 minuty fala na przełęcze z P5
    "raider_wave_interval_sec": 270,   # Co 4,5 minuty rajd dywersyjny z P7
    "raider_warning_lead_sec": 35,     # Ostrzeżenie wywiadu 35s przed rajdem

    "mutator_interval_sec": 300,       # Co 5 minut (od 15. minuty) Kuźnia P6 wzmacnia pancerz/HP
    "mutator_hp_buff": 25,

    "bastion_bounty": {"gold": 600, "food": 600, "stone": 250},

    # UWAGA: Gracze AI (P5-P8) mają 0 zasobów na starcie, aby nie produkowali jednostek w 1. minucie!
    "starting_resources": {
        PlayerId.ONE:   {"food": 500, "wood": 500, "gold": 300, "stone": 150},
        PlayerId.TWO:   {"food": 400, "wood": 400, "gold": 250, "stone": 200},
        PlayerId.THREE: {"food": 400, "wood": 450, "gold": 300, "stone": 350},
        PlayerId.FOUR:  {"food": 450, "wood": 500, "gold": 350, "stone": 400},
        PlayerId.FIVE:  {"food": 0, "wood": 0, "gold": 0, "stone": 0},
        PlayerId.SIX:   {"food": 0, "wood": 0, "gold": 0, "stone": 0},
        PlayerId.SEVEN: {"food": 0, "wood": 0, "gold": 0, "stone": 0},
        PlayerId.EIGHT: {"food": 0, "wood": 0, "gold": 0, "stone": 0},
    },
}


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

    def add_hill_plateau(self, cx: int, cy: int, flat_radius: int, height: int):
        total_r = flat_radius + height
        for x in range(max(0, cx - total_r), min(self.size, cx + total_r + 1)):
            for y in range(max(0, cy - total_r), min(self.size, cy + total_r + 1)):
                dist = max(abs(x - cx), abs(y - cy))
                h = max(0, min(height, flat_radius + height - dist))
                if h > self.elev[x][y]:
                    self.elev[x][y] = h

    def apply_smooth_elevation(self, mm):
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


def add_player_resource(trigger, player: PlayerId, resource_id: int, amount: int):
    safe_call(
        trigger.new_effect.modify_resource,
        source_player=player,
        tribute_list=resource_id,
        operation=Operation.ADD,
        quantity=int(amount),
    )


def paint_natural_biome_background(mm, size: int):
    for x in range(size):
        for y in range(size):
            n = math.sin(x * 0.08) * math.cos(y * 0.08) + 0.5 * math.sin((x - y) * 0.05)
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


def paint_organic_forest(mm, cx: int, cy: int, radius: float, terrain_id: int, seed: float = 0.0):
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


def build_rocky_cliff_ridge(mm, um, grid: SafeMapGrid, x1: int, y1: int, x2: int, y2: int, height: int = 3):
    steps = int(math.hypot(x2 - x1, y2 - y1))
    for i in range(steps + 1):
        t = i / max(1, steps)
        curve = math.sin(t * math.pi) * 2.5
        rx = int(round(x1 + (x2 - x1) * t + curve))
        ry = int(round(y1 + (y2 - y1) * t - curve))
        grid.add_hill_plateau(rx, ry, flat_radius=1, height=height)
        set_circle_terrain(mm, rx, ry, radius=2, terrain_id=TerrainId.DIRT_3)
        grid.mark_no_trees(rx, ry, radius=2)
        if i % 2 == 0 and grid.in_bounds(rx, ry) and (rx, ry) not in grid.occupied_tiles:
            grid.place_unit(um, PlayerId.GAIA, ROCK_CLIFF_ID, rx, ry, no_tree_margin=1)


def set_road(mm, grid: SafeMapGrid, x1: int, y1: int, x2: int, y2: int, width: int = 1):
    steps = int(math.hypot(x2 - x1, y2 - y1) * 2)
    for i in range(steps + 1):
        t = i / max(1, steps)
        rx = int(round(x1 + (x2 - x1) * t))
        ry = int(round(y1 + (y2 - y1) * t))
        set_circle_terrain(mm, rx, ry, width, TerrainId.ROAD)
        grid.mark_no_trees(rx, ry, width + 2)


def populate_forest_trees(mm, um, grid: SafeMapGrid):
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
    offsets = [
        (0, 0), (1, 0), (0, 1), (1, 1),
        (2, 0), (0, 2), (2, 1), (1, 2),
        (2, 2), (3, 0), (0, 3), (3, 1),
    ]
    for dx, dy in offsets[:count]:
        grid.place_unit(um, PlayerId.GAIA, res_const, cx + dx, cy + dy, no_tree_margin=3)


def spawn_player_base(um, grid: SafeMapGrid, player: PlayerId, cx: int, cy: int, role: str):
    grid.mark_no_trees(cx, cy, radius=15)
    grid.place_building(um, player, BuildingInfo.TOWN_CENTER.ID, cx, cy, size_tiles=4, no_tree_margin=4)

    for dx, dy in [(-3, -2), (-3, -1), (-3, 0), (-3, 1), (-2, -3), (-1, -3)]:
        grid.place_unit(um, player, UnitInfo.VILLAGER_MALE.ID, cx + dx, cy + dy, no_tree_margin=1)
    grid.place_unit(um, player, UnitInfo.SCOUT_CAVALRY.ID, cx + 4, cy, no_tree_margin=1)

    for tx, ty in [(-5, -3), (4, -4), (-4, 4), (4, 3)]:
        grid.place_unit(um, PlayerId.GAIA, TREE_OAK_ID, cx + tx, cy + ty, no_tree_margin=0)

    for sx, sy in [(-3, 2), (-2, 2), (-1, 2), (0, 2), (-3, 3), (-2, 3)]:
        grid.place_unit(um, PlayerId.GAIA, UnitInfo.SHEEP.ID, cx + sx, cy + sy, no_tree_margin=1)
    grid.place_unit(um, PlayerId.GAIA, UnitInfo.WILD_BOAR.ID, cx - 10, cy - 1, no_tree_margin=1)
    grid.place_unit(um, PlayerId.GAIA, UnitInfo.WILD_BOAR.ID, cx + 1, cy + 10, no_tree_margin=1)
    for dx, dy in [(-7, -9), (-8, -9), (-7, -10), (-8, -10)]:
        grid.place_unit(um, PlayerId.GAIA, UnitInfo.DEER.ID, cx + dx, cy + dy, no_tree_margin=1)

    spawn_resource_cluster(um, grid, cx - 9, cy - 5, OtherInfo.FORAGE_BUSH.ID, count=6)

    if role == "vanguard_p1":
        grid.place_building(um, player, BuildingInfo.BARRACKS.ID, cx + 8, cy - 5, size_tiles=3, no_tree_margin=2)
        grid.place_building(um, player, BuildingInfo.STABLE.ID, cx + 8, cy + 3, size_tiles=3, no_tree_margin=2)
        grid.place_building(um, player, BuildingInfo.BLACKSMITH.ID, cx + 2, cy - 8, size_tiles=3, no_tree_margin=2)
        grid.place_building(um, player, BuildingInfo.MARKET.ID, cx - 8, cy + 7, size_tiles=4, no_tree_margin=2)
        spawn_resource_cluster(um, grid, cx + 10, cy - 10, OtherInfo.GOLD_MINE.ID, count=4)
    elif role == "flank_p2":
        grid.place_building(um, player, BuildingInfo.BARRACKS.ID, cx + 7, cy - 5, size_tiles=3, no_tree_margin=2)
        spawn_resource_cluster(um, grid, cx + 8, cy - 9, OtherInfo.GOLD_MINE.ID, count=6)
        spawn_resource_cluster(um, grid, cx - 10, cy + 7, OtherInfo.STONE_MINE.ID, count=5)
    elif role == "valley_defender":
        grid.place_building(um, player, BuildingInfo.MARKET.ID, cx, cy + 9, size_tiles=4, no_tree_margin=2)
        spawn_resource_cluster(um, grid, cx + 9, cy - 7, OtherInfo.GOLD_MINE.ID, count=10)
        spawn_resource_cluster(um, grid, cx - 11, cy + 5, OtherInfo.GOLD_MINE.ID, count=10)
        spawn_resource_cluster(um, grid, cx + 9, cy + 6, OtherInfo.STONE_MINE.ID, count=8)


def spawn_ai_bastion_buildings_only(um, grid: SafeMapGrid, player: PlayerId, cx: int, cy: int, is_boss: bool = False):
    """
    Stawia w 0:00 WYŁĄCZNIE budynki Bastionu (Zamek, Wieże, Koszary).
    Brak mobilnych jednostek w 0:00 gwarantuje, że AI nie wyśle ich w 1. minucie na bazy graczy w Dark Age!
    Garnizon obronny pojawia się dopiero, gdy gracze podejdą pod Bastion (Proximity Trigger).
    """
    grid.mark_no_trees(cx, cy, radius=18 if is_boss else 14)
    command_castle = grid.place_building(um, player, BuildingInfo.CASTLE.ID, cx, cy, size_tiles=4, no_tree_margin=3)

    grid.place_building(um, player, BuildingInfo.BARRACKS.ID, cx - 7, cy - 5, size_tiles=3, no_tree_margin=2)
    grid.place_building(um, player, BuildingInfo.ARCHERY_RANGE.ID, cx + 7, cy - 5, size_tiles=3, no_tree_margin=2)
    grid.place_building(um, player, BuildingInfo.STABLE.ID, cx - 7, cy + 6, size_tiles=3, no_tree_margin=2)
    grid.place_building(um, player, BuildingInfo.SIEGE_WORKSHOP.ID, cx + 7, cy + 6, size_tiles=3, no_tree_margin=2)

    tower_type = BuildingInfo.KEEP.ID if is_boss else BuildingInfo.GUARD_TOWER.ID
    for tx, ty in [(-10, -10), (-10, 10), (10, -10), (10, 10)]:
        grid.place_building(um, player, tower_type, cx + tx, cy + ty, size_tiles=2, no_tree_margin=2)

    if is_boss:
        grid.place_building(um, player, BuildingInfo.CASTLE.ID, cx - 10, cy + 4, size_tiles=4, no_tree_margin=2)
        grid.place_building(um, player, BuildingInfo.CASTLE.ID, cx + 10, cy - 4, size_tiles=4, no_tree_margin=2)

    return command_castle


def add_proximity_garrison_trigger(tm, name: str, ai_player: PlayerId, cx: int, cy: int, radius: int,
                                   units_spec: list[tuple[int, int]]):
    """Spawnuje garnizon obronny obozu dopiero wtedy, gdy dowolny gracz P1-P4 podejdzie pod obóz."""
    x1, y1 = max(0, cx - radius), max(0, cy - radius)
    x2, y2 = min(MAP_SIZE - 1, cx + radius), min(MAP_SIZE - 1, cy + radius)

    t_spawn = tm.add_trigger(f"Garrison_Spawn_{name}", enabled=False, looping=False)
    add_spawn_and_attack_effect(t_spawn, ai_player, units_spec, spawn_x=cx, spawn_y=cy + 6, target_x=cx, target_y=cy)

    for h_p in [PlayerId.ONE, PlayerId.TWO, PlayerId.THREE, PlayerId.FOUR]:
        t_detect = tm.add_trigger(f"Garrison_Detect_{name}_P{h_p.value}", enabled=True, looping=False)
        safe_call(
            t_detect.new_condition.objects_in_area,
            source_player=h_p,
            area_x1=x1, area_y1=y1, area_x2=x2, area_y2=y2,
            quantity=1,
        )
        safe_call(t_detect.new_effect.activate_trigger, trigger_id=t_spawn.trigger_id)


def add_spawn_and_attack_effect(trigger, ai_player: PlayerId, units_spec: list[tuple[int, int]],
                                spawn_x: int, spawn_y: int, target_x: int, target_y: int):
    idx = 0
    for unit_id, count in units_spec:
        for _ in range(count):
            dx = (idx % 5) - 2
            dy = (idx // 5) - 2
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
        area_x1=max(0, spawn_x - 6),
        area_y1=max(0, spawn_y - 6),
        area_x2=min(MAP_SIZE - 1, spawn_x + 6),
        area_y2=min(MAP_SIZE - 1, spawn_y + 6),
        location_x=target_x,
        location_y=target_y,
    )


def build_coop_scenario():
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

    human_players = [PlayerId.ONE, PlayerId.TWO, PlayerId.THREE, PlayerId.FOUR]
    ai_players = [PlayerId.FIVE, PlayerId.SIX, PlayerId.SEVEN, PlayerId.EIGHT]

    pm.active_players = 8
    for p_id in human_players + ai_players:
        p = pm.players[p_id]
        res = BALANCE["starting_resources"][p_id]
        p.food = res["food"]
        p.wood = res["wood"]
        p.gold = res["gold"]
        p.stone = res["stone"]

    paint_natural_biome_background(mm, MAP_SIZE)

    for x in range(10, MAP_SIZE - 10, 8):
        grid.add_hill_plateau(x, 126, flat_radius=4, height=3)
    set_box_terrain(mm, 0, 121, MAP_SIZE - 1, 131, TerrainId.FOREST_PINE)

    west_pass = (62, 126)
    east_pass = (118, 126)
    for px in range(west_pass[0] - 8, west_pass[0] + 9):
        for py in range(116, 136):
            grid.elev[px][py] = 0
    for px in range(east_pass[0] - 8, east_pass[0] + 9):
        for py in range(116, 136):
            grid.elev[px][py] = 0

    set_box_terrain(mm, west_pass[0] - 6, 118, west_pass[0] + 6, 134, TerrainId.DIRT_1)
    set_box_terrain(mm, east_pass[0] - 6, 118, east_pass[0] + 6, 134, TerrainId.DIRT_1)
    grid.mark_no_trees(west_pass[0], west_pass[1], radius=9)
    grid.mark_no_trees(east_pass[0], east_pass[1], radius=9)

    for x in range(0, MAP_SIZE):
        ry = int(round(66 + 4 * math.sin(x * 0.06)))
        set_circle_terrain(mm, x, ry, radius=2, terrain_id=TERRAIN_WATER)
        grid.mark_no_trees(x, ry, radius=3)
    for ford_x in [34, 86, 142]:
        ry = int(round(66 + 4 * math.sin(ford_x * 0.06)))
        set_circle_terrain(mm, ford_x, ry, radius=4, terrain_id=TERRAIN_SHALLOWS)

    for sx, sy in [(west_pass[0], 98), (east_pass[0], 98), (48, 112), (136, 138)]:
        grid.mark_no_trees(sx, sy, radius=8)

    p_coords = {
        PlayerId.ONE:   (30, 48),
        PlayerId.TWO:   (28, 98),
        PlayerId.THREE: (62, 152),
        PlayerId.FOUR:  (118, 152),
    }

    ai_coords = {
        PlayerId.FIVE:  (82, 30),
        PlayerId.SIX:   (150, 92),
        PlayerId.SEVEN: (88, 86),
        PlayerId.EIGHT: (146, 28),
    }

    for ai_p, (ax, ay) in ai_coords.items():
        is_boss = ai_p == PlayerId.EIGHT
        grid.add_hill_plateau(ax, ay, flat_radius=15 if is_boss else 12, height=3 if is_boss else 2)
        set_circle_terrain(mm, ax, ay, radius=16 if is_boss else 12, terrain_id=TerrainId.DIRT_1)

    build_rocky_cliff_ridge(mm, um, grid, 54, 48, 66, 82, height=2)
    build_rocky_cliff_ridge(mm, um, grid, 116, 48, 126, 78, height=3)

    grid.apply_smooth_elevation(mm)

    set_road(mm, grid, *p_coords[PlayerId.THREE], *p_coords[PlayerId.FOUR], width=1)
    set_road(mm, grid, *p_coords[PlayerId.THREE], *west_pass, width=1)
    set_road(mm, grid, *p_coords[PlayerId.FOUR], *east_pass, width=1)
    set_road(mm, grid, *west_pass, *ai_coords[PlayerId.SEVEN], width=1)
    set_road(mm, grid, *east_pass, *ai_coords[PlayerId.SIX], width=1)
    set_road(mm, grid, *p_coords[PlayerId.ONE], *ai_coords[PlayerId.FIVE], width=1)

    spawn_player_base(um, grid, PlayerId.ONE, *p_coords[PlayerId.ONE], role="vanguard_p1")
    spawn_player_base(um, grid, PlayerId.TWO, *p_coords[PlayerId.TWO], role="flank_p2")
    spawn_player_base(um, grid, PlayerId.THREE, *p_coords[PlayerId.THREE], role="valley_defender")
    spawn_player_base(um, grid, PlayerId.FOUR, *p_coords[PlayerId.FOUR], role="valley_defender")

    for rx, ry in [(52, 26), (115, 26), (62, 108), (122, 108)]:
        grid.place_unit(um, PlayerId.GAIA, RELIC_ID, rx, ry, no_tree_margin=2)

    forge_pos = (90, 148)
    imperial_forge = grid.place_building(um, PlayerId.THREE, BuildingInfo.WONDER.ID, forge_pos[0], forge_pos[1], size_tiles=5, no_tree_margin=3)

    # Wzmocnione przełęcze na starcie (po 2 Wieże Strażnicze na przełęcz)
    grid.place_building(um, PlayerId.THREE, BuildingInfo.GUARD_TOWER.ID, west_pass[0] - 4, west_pass[1] + 5, size_tiles=2, no_tree_margin=2)
    grid.place_building(um, PlayerId.THREE, BuildingInfo.GUARD_TOWER.ID, west_pass[0] + 4, west_pass[1] + 5, size_tiles=2, no_tree_margin=2)
    grid.place_building(um, PlayerId.FOUR, BuildingInfo.GUARD_TOWER.ID, east_pass[0] - 4, east_pass[1] + 5, size_tiles=2, no_tree_margin=2)
    grid.place_building(um, PlayerId.FOUR, BuildingInfo.GUARD_TOWER.ID, east_pass[0] + 4, east_pass[1] + 5, size_tiles=2, no_tree_margin=2)

    castle_p5 = spawn_ai_bastion_buildings_only(um, grid, PlayerId.FIVE, *ai_coords[PlayerId.FIVE], is_boss=False)
    castle_p6 = spawn_ai_bastion_buildings_only(um, grid, PlayerId.SIX, *ai_coords[PlayerId.SIX], is_boss=False)
    castle_p7 = spawn_ai_bastion_buildings_only(um, grid, PlayerId.SEVEN, *ai_coords[PlayerId.SEVEN], is_boss=False)
    castle_p8_boss = spawn_ai_bastion_buildings_only(um, grid, PlayerId.EIGHT, *ai_coords[PlayerId.EIGHT], is_boss=True)

    forests = [
        (12, 34, 6.5, TerrainId.FOREST_OAK, 0.4),
        (48, 30, 5.5, TerrainId.FOREST_PINE, 1.8),
        (12, 82, 6.5, TerrainId.FOREST_OAK, 2.3),
        (12, 112, 6.5, TerrainId.FOREST_PINE, 3.1),
        (48, 84, 5.0, TerrainId.FOREST_OAK, 0.9),
        (28, 162, 7.5, TerrainId.FOREST_OAK, 1.2),
        (90, 168, 7.0, TerrainId.FOREST_OAK, 2.7),
        (152, 162, 7.5, TerrainId.FOREST_OAK, 3.5),
        (42, 140, 5.5, TerrainId.FOREST_PINE, 4.1),
        (140, 140, 5.5, TerrainId.FOREST_PINE, 0.6),
        (62, 12, 6.5, TerrainId.FOREST_PINE, 1.5),
        (112, 14, 6.5, TerrainId.FOREST_PINE, 2.9),
        (114, 58, 6.0, TerrainId.FOREST_OAK, 3.3),
        (168, 60, 6.5, TerrainId.FOREST_PINE, 0.8),
        (168, 112, 6.5, TerrainId.FOREST_OAK, 2.1),
    ]
    for fx, fy, r, t_id, seed in forests:
        paint_organic_forest(mm, fx, fy, radius=r, terrain_id=t_id, seed=seed)

    populate_forest_trees(mm, um, grid)

    # ==============================================================================
    # TRIGGERY: INICJALIZACJA, GARNIZONY PROXIMITY, DOKTRYNY TECHNOLOGICZNE I 3 FAZY FAL
    # ==============================================================================
    t_init = tm.add_trigger("01_Init_Coop_And_Boss_Shield", enabled=True, looping=False)

    for h1 in human_players:
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

    add_player_resource(t_init, PlayerId.ONE, RES_BONUS_POP_CAP, BALANCE["p1_bonus_pop"])

    for b_id in [BuildingInfo.BARRACKS.ID, BuildingInfo.STABLE.ID, BuildingInfo.ARCHERY_RANGE.ID]:
        safe_call(
            t_init.new_effect.modify_attribute,
            source_player=PlayerId.ONE,
            object_list_unit_id=b_id,
            object_attributes=ATTR_WORK_RATE,
            operation=Operation.MULTIPLY,
            quantity=1.35,
        )

    safe_call(
        t_init.new_effect.modify_attribute,
        source_player=PlayerId.EIGHT,
        object_list_unit_id=BuildingInfo.CASTLE.ID,
        object_attributes=ATTR_HIT_POINTS,
        operation=Operation.ADD,
        quantity=4500,
    )

    safe_call(
        t_init.new_effect.send_chat,
        source_player=PlayerId.ONE,
        message="[OPERACJA ZELAZNY KRAG]: Macie 11 minut spokoju na rozbudowe gospodarki! Pierwsza fala (Feudalna) uderzy w 11. minucie.",
    )

    # Garnizony Bastionów spawnowane dopiero, gdy gracze podejdą pod dany Bastion (brak ataków w 1. minucie!)
    add_proximity_garrison_trigger(tm, "Bastion_P5", PlayerId.FIVE, *ai_coords[PlayerId.FIVE], radius=18,
                                   units_spec=[(UnitInfo.PIKEMAN.ID, 10), (UnitInfo.LONG_SWORDSMAN.ID, 8)])
    add_proximity_garrison_trigger(tm, "Bastion_P6", PlayerId.SIX, *ai_coords[PlayerId.SIX], radius=18,
                                   units_spec=[(UnitInfo.CROSSBOWMAN.ID, 12), (UnitInfo.MANGONEL.ID, 2)])
    add_proximity_garrison_trigger(tm, "Bastion_P7", PlayerId.SEVEN, *ai_coords[PlayerId.SEVEN], radius=18,
                                   units_spec=[(UnitInfo.KNIGHT.ID, 10), (UnitInfo.LIGHT_CAVALRY.ID, 8)])
    add_proximity_garrison_trigger(tm, "Boss_P8", PlayerId.EIGHT, *ai_coords[PlayerId.EIGHT], radius=22,
                                   units_spec=[(UnitInfo.PALADIN.ID, 12), (UnitInfo.ARBALESTER.ID, 12), (UnitInfo.ONAGER.ID, 3)])

    # ==============================================================================
    # DOKTRYNY TECHNOLOGICZNE WROGA (KUŹNIA I UNIWERSYTET W 3 FAZACH)
    # ==============================================================================
    # FAZA I (11:00 - Feudal Age): Podstawowe technologie Feudalne z podziałem na specjalizacje
    t_tech_p1 = tm.add_trigger("02a_Tech_Phase1_Feudal", enabled=True, looping=False)
    safe_call(t_tech_p1.new_condition.timer, timer=BALANCE["phase1_feudal_start_sec"])
    research_techs(t_tech_p1, ai_players, [TECH_FEUDAL_AGE])
    research_techs(t_tech_p1, [PlayerId.FIVE], [TECH_SCALE_MAIL])                         # P5: Pancerz piechoty (+0 ataku)
    research_techs(t_tech_p1, [PlayerId.SIX], [TECH_FLETCHING])                           # P6: Zasięg i atak łuków (+0 pancerza)
    research_techs(t_tech_p1, [PlayerId.SEVEN], [TECH_FORGING, TECH_BLOODLINES])          # P7: Atak i HP jazdy (+0 pancerza)
    research_techs(t_tech_p1, [PlayerId.EIGHT], [TECH_FORGING, TECH_SCALE_BARDING, TECH_FLETCHING])

    # FAZA II (20:00 - Castle Age): Specjalizacje Zamkowe (Balistyka dla P6, Squires dla P5, Husbandry dla P7)
    t_tech_p2 = tm.add_trigger("02b_Tech_Phase2_Castle", enabled=True, looping=False)
    safe_call(t_tech_p2.new_condition.timer, timer=BALANCE["phase2_castle_start_sec"])
    research_techs(t_tech_p2, ai_players, [TECH_CASTLE_AGE])
    research_techs(t_tech_p2, [PlayerId.FIVE], [TECH_CHAIN_MAIL, TECH_SQUIRES])
    research_techs(t_tech_p2, [PlayerId.SIX], [TECH_BODKIN_ARROW, TECH_BALLISTICS, TECH_THUMB_RING])
    research_techs(t_tech_p2, [PlayerId.SEVEN], [TECH_IRON_CASTING, TECH_HUSBANDRY])
    research_techs(t_tech_p2, [PlayerId.EIGHT], [TECH_IRON_CASTING, TECH_CHAIN_BARDING, TECH_BODKIN_ARROW, TECH_BALLISTICS])
    safe_call(
        t_tech_p2.new_effect.send_chat,
        source_player=PlayerId.ONE,
        message="[FAZA II - ERA ZAMKOWA]: Wrog wszedl w Castle Age! P5 ma twardy pancerz piechoty, P6 zbadal Balistyke, a P7 szybka jazde (Bloodlines + Husbandry)!",
    )

    # FAZA III (32:00 - Imperial Age): Pełna Kuźnia Imperialna (możliwa do zablokowania przez zniszczenie Kuźni P6!)
    t_tech_p3 = tm.add_trigger("02c_Tech_Phase3_Imperial", enabled=True, looping=False)
    safe_call(t_tech_p3.new_condition.timer, timer=BALANCE["phase3_imperial_start_sec"])
    research_techs(t_tech_p3, ai_players, [TECH_IMPERIAL_AGE])
    research_techs(t_tech_p3, [PlayerId.FIVE], [TECH_PLATE_MAIL])
    research_techs(t_tech_p3, [PlayerId.SIX], [TECH_BRACER, TECH_CHEMISTRY, TECH_SIEGE_ENGINEERS])
    research_techs(t_tech_p3, [PlayerId.SEVEN], [TECH_BLAST_FURNACE])
    research_techs(t_tech_p3, [PlayerId.EIGHT], [TECH_BLAST_FURNACE, TECH_PLATE_BARDING, TECH_PLATE_MAIL, TECH_BRACER, TECH_CHEMISTRY, TECH_SIEGE_ENGINEERS])
    safe_call(
        t_tech_p3.new_effect.send_chat,
        source_player=PlayerId.ONE,
        message="[FAZA III - ERA IMPERIALNA]: Kuznia P6 odblokowala ulepszenia Imperialne (Blast Furnace, Bracer, Chemistry, Siege Engineers) dla armii wroga!",
    )

    # Mutator Kuźni P6 (uruchamia się dopiero po wejściu w Castle Age)
    t_mutator = tm.add_trigger("02d_Bastion_P6_HP_Mutator", enabled=False, looping=True)
    safe_call(t_tech_p2.new_effect.activate_trigger, trigger_id=t_mutator.trigger_id)
    safe_call(t_mutator.new_condition.timer, timer=BALANCE["mutator_interval_sec"])

    mutated_units = [
        UnitInfo.PIKEMAN.ID, UnitInfo.HALBERDIER.ID,
        UnitInfo.CROSSBOWMAN.ID, UnitInfo.ARBALESTER.ID,
        UnitInfo.KNIGHT.ID, UnitInfo.CAVALIER.ID, UnitInfo.PALADIN.ID,
        UnitInfo.HUSKARL.ID, UnitInfo.CAPPED_RAM.ID, UnitInfo.LIGHT_CAVALRY.ID,
    ]
    for ai_p in ai_players:
        for u_id in mutated_units:
            safe_call(
                t_mutator.new_effect.modify_attribute,
                source_player=ai_p,
                object_list_unit_id=u_id,
                object_attributes=ATTR_HIT_POINTS,
                operation=Operation.ADD,
                quantity=BALANCE["mutator_hp_buff"],
            )
    safe_call(
        t_mutator.new_effect.send_chat,
        source_player=PlayerId.ONE,
        message=f"[KUZNIA WSCHODNIA P6]: Wrog przekul pancerze (+{BALANCE['mutator_hp_buff']} HP)! Zburzcie Zamek P6 przed 32. minuta, by zablokowac mu technologie Imperialne!",
    )

    # ==============================================================================
    # TRÓJFAZOWE FALE Z BASTIONU P5 (FEUDAL -> CASTLE -> IMPERIAL)
    # ==============================================================================
    # Fala Fazy I (Feudalna: 11:00 - 20:00)
    t_wave_p1 = tm.add_trigger("03a_P5_Wave_Phase1_Feudal", enabled=False, looping=True)
    safe_call(t_wave_p1.new_condition.timer, timer=BALANCE["siege_wave_interval_sec"])
    add_spawn_and_attack_effect(
        t_wave_p1, PlayerId.FIVE, [(UnitInfo.MAN_AT_ARMS.ID, 8), (UnitInfo.BATTERING_RAM.ID, 1)],
        spawn_x=west_pass[0], spawn_y=98, target_x=forge_pos[0] - 10, target_y=forge_pos[1],
    )
    add_spawn_and_attack_effect(
        t_wave_p1, PlayerId.SIX, [(UnitInfo.ARCHER.ID, 8), (UnitInfo.SCOUT_CAVALRY.ID, 4)],
        spawn_x=east_pass[0], spawn_y=98, target_x=forge_pos[0] + 10, target_y=forge_pos[1],
    )
    safe_call(t_wave_p1.new_effect.send_chat, source_player=PlayerId.ONE,
              message="[FALA FEUDALNA P5]: Kolumny Zbrojnych i Lucznikow maszeruja na obie przelecze Doliny!")

    # Fala Fazy II (Zamkowa: 20:00 - 32:00)
    t_wave_p2 = tm.add_trigger("03b_P5_Wave_Phase2_Castle", enabled=False, looping=True)
    safe_call(t_wave_p2.new_condition.timer, timer=BALANCE["siege_wave_interval_sec"])
    add_spawn_and_attack_effect(
        t_wave_p2, PlayerId.FIVE, [(UnitInfo.PIKEMAN.ID, 10), (UnitInfo.HUSKARL.ID, 6), (UnitInfo.BATTERING_RAM.ID, 2)],
        spawn_x=west_pass[0], spawn_y=98, target_x=forge_pos[0] - 10, target_y=forge_pos[1],
    )
    add_spawn_and_attack_effect(
        t_wave_p2, PlayerId.SIX, [(UnitInfo.CROSSBOWMAN.ID, 12), (UnitInfo.KNIGHT.ID, 6), (UnitInfo.MANGONEL.ID, 1)],
        spawn_x=east_pass[0], spawn_y=98, target_x=forge_pos[0] + 10, target_y=forge_pos[1],
    )
    safe_call(t_wave_p2.new_effect.send_chat, source_player=PlayerId.ONE,
              message="[FALA ZAMKOWA P5]: Taran, Huskarlowie (pancerz P5) i Kusznicy z Balistyka (P6) uderzaja na przelecze!")

    # Fala Fazy III (Imperialna: od 32:00)
    t_wave_p3 = tm.add_trigger("03c_P5_Wave_Phase3_Imperial", enabled=False, looping=True)
    safe_call(t_wave_p3.new_condition.timer, timer=BALANCE["siege_wave_interval_sec"])
    add_spawn_and_attack_effect(
        t_wave_p3, PlayerId.FIVE, [(UnitInfo.HALBERDIER.ID, 14), (UnitInfo.HUSKARL.ID, 10), (UnitInfo.CAPPED_RAM.ID, 3)],
        spawn_x=west_pass[0], spawn_y=98, target_x=forge_pos[0] - 10, target_y=forge_pos[1],
    )
    add_spawn_and_attack_effect(
        t_wave_p3, PlayerId.SIX, [(UnitInfo.ARBALESTER.ID, 14), (UnitInfo.CAVALIER.ID, 8), (UnitInfo.ONAGER.ID, 2)],
        spawn_x=east_pass[0], spawn_y=98, target_x=forge_pos[0] + 10, target_y=forge_pos[1],
    )
    safe_call(t_wave_p3.new_effect.send_chat, source_player=PlayerId.ONE,
              message="[FALA IMPERIALNA P5]: Ciężkie kolumny oblężnicze uderzaja na obie przelecze!")

    # Przełączanie faz fal P5 (tylko jeśli Bastion P5 nadal stoi!)
    safe_call(t_tech_p1.new_effect.activate_trigger, trigger_id=t_wave_p1.trigger_id)

    t_switch_p2 = tm.add_trigger("03d_Switch_P5_Waves_To_Castle", enabled=True, looping=False)
    safe_call(t_switch_p2.new_condition.timer, timer=BALANCE["phase2_castle_start_sec"])
    safe_call(t_switch_p2.new_effect.deactivate_trigger, trigger_id=t_wave_p1.trigger_id)
    safe_call(t_switch_p2.new_effect.activate_trigger, trigger_id=t_wave_p2.trigger_id)

    t_switch_p3 = tm.add_trigger("03e_Switch_P5_Waves_To_Imperial", enabled=True, looping=False)
    safe_call(t_switch_p3.new_condition.timer, timer=BALANCE["phase3_imperial_start_sec"])
    safe_call(t_switch_p3.new_effect.deactivate_trigger, trigger_id=t_wave_p2.trigger_id)
    safe_call(t_switch_p3.new_effect.activate_trigger, trigger_id=t_wave_p3.trigger_id)

    # ==============================================================================
    # RAJDY DYWERSYJNE P7 (START DOPIERO OD 20. MINUTY - W CASTLE AGE)
    # ==============================================================================
    t_raid_warn = tm.add_trigger("04a_Bastion_P7_Raid_Intel_Warning", enabled=False, looping=True)
    t_raid_exec = tm.add_trigger("04b_Bastion_P7_Raid_Spawn_Execution", enabled=False, looping=False)

    safe_call(t_tech_p2.new_effect.activate_trigger, trigger_id=t_raid_warn.trigger_id)

    safe_call(t_raid_warn.new_condition.timer, timer=BALANCE["raider_wave_interval_sec"])
    safe_call(
        t_raid_warn.new_effect.send_chat,
        source_player=PlayerId.ONE,
        message=f"[WYWIAD - DYWERSJA P7]: Za {BALANCE['raider_warning_lead_sec']}s szybka jazda P7 (Bloodlines + Husbandry) uderzy na zaplecze P2 oraz wschodnia Doline!",
    )
    safe_call(t_raid_warn.new_effect.activate_trigger, trigger_id=t_raid_exec.trigger_id)

    safe_call(t_raid_exec.new_condition.timer, timer=BALANCE["raider_warning_lead_sec"])
    raid_comp = [(UnitInfo.LIGHT_CAVALRY.ID, 8), (UnitInfo.KNIGHT.ID, 4), (UnitInfo.PETARD.ID, 2)]

    add_spawn_and_attack_effect(
        t_raid_exec, PlayerId.SEVEN, raid_comp,
        spawn_x=48, spawn_y=112,
        target_x=p_coords[PlayerId.TWO][0], target_y=p_coords[PlayerId.TWO][1],
    )
    add_spawn_and_attack_effect(
        t_raid_exec, PlayerId.SEVEN, raid_comp,
        spawn_x=136, spawn_y=138,
        target_x=p_coords[PlayerId.FOUR][0], target_y=p_coords[PlayerId.FOUR][1],
    )
    safe_call(t_raid_exec.new_effect.deactivate_trigger, trigger_id=t_raid_exec.trigger_id)

    # ==============================================================================
    # ZNISZCZENIE BASTIONÓW (WYŁĄCZENIE FAL + SABOTAŻ TECHNOLOGII + KONTRATAK)
    # ==============================================================================
    bastion_specs = [
        ("Bastion Polnocny (Oblezniczy P5)", castle_p5, [t_wave_p1, t_wave_p2, t_wave_p3, t_switch_p2, t_switch_p3]),
        ("Bastion Wschodni (Kuznia Imperialna P6)", castle_p6, [t_mutator, t_tech_p3]),
        ("Bastion Centralny (Dywersyjny P7)", castle_p7, [t_raid_warn, t_raid_exec]),
    ]

    bounty = BALANCE["bastion_bounty"]
    revenge_comp = [(UnitInfo.CAVALIER.ID, 8), (UnitInfo.MANGONEL.ID, 3), (UnitInfo.PIKEMAN.ID, 12)]

    for idx, (b_name, b_castle, triggers_to_disable) in enumerate(bastion_specs, start=1):
        t_kill = tm.add_trigger(f"05_Bastion_Destroyed_{idx}", enabled=True, looping=False)
        safe_call(t_kill.new_condition.destroy_object, unit_object=b_castle.reference_id)

        for tr in triggers_to_disable:
            safe_call(t_kill.new_effect.deactivate_trigger, trigger_id=tr.trigger_id)

        safe_call(
            t_kill.new_effect.modify_attribute,
            source_player=PlayerId.EIGHT,
            object_list_unit_id=BuildingInfo.CASTLE.ID,
            object_attributes=ATTR_HIT_POINTS,
            operation=Operation.SUBTRACT,
            quantity=1500,
        )

        # Bonus: Zburzenie Kuźni P6 daje graczom natychmiastowe darmowe technologie Kuźni!
        if idx == 2:
            research_techs(t_kill, human_players, [TECH_IRON_CASTING, TECH_CHAIN_BARDING, TECH_CHAIN_MAIL, TECH_BODKIN_ARROW])

        for h_p in human_players:
            add_player_resource(t_kill, h_p, RES_GOLD, bounty["gold"])
            add_player_resource(t_kill, h_p, RES_FOOD, bounty["food"])
            add_player_resource(t_kill, h_p, RES_STONE, bounty["stone"])

        add_spawn_and_attack_effect(
            t_kill, PlayerId.EIGHT, revenge_comp,
            spawn_x=west_pass[0], spawn_y=98,
            target_x=forge_pos[0], target_y=forge_pos[1],
        )
        add_spawn_and_attack_effect(
            t_kill, PlayerId.EIGHT, revenge_comp,
            spawn_x=east_pass[0], spawn_y=98,
            target_x=forge_pos[0], target_y=forge_pos[1],
        )

        safe_call(
            t_kill.new_effect.send_chat,
            source_player=PlayerId.ONE,
            message=f"[ZWYCIESTWO TAKTYCZNE]: {b_name} zburzony! Tarcza P8 slabnie (-1500 HP), wrog traci jego bonusy, ale rusza KONTRATAK na przelecze!",
        )

    t_win = tm.add_trigger("06_Coop_Victory_Boss_Destroyed", enabled=True, looping=False)
    safe_call(t_win.new_condition.destroy_object, unit_object=castle_p8_boss.reference_id)
    for h_p in human_players:
        safe_call(t_win.new_effect.declare_victory, source_player=h_p, enabled=1)

    t_lose = tm.add_trigger("07_Coop_Defeat_Forge_Lost", enabled=True, looping=False)
    safe_call(t_lose.new_condition.destroy_object, unit_object=imperial_forge.reference_id)
    for ai_p in ai_players:
        safe_call(t_lose.new_effect.declare_victory, source_player=ai_p, enabled=1)

    scenario.write_to_file(str(OUTPUT_SCENARIO))
    print(f"Gotowe! Scenariusz Co-op zapisano w: {OUTPUT_SCENARIO}")


if __name__ == "__main__":
    build_coop_scenario()