import math

from AoE2ScenarioParser.datasets.buildings import BuildingInfo
from AoE2ScenarioParser.datasets.other import OtherInfo
from AoE2ScenarioParser.datasets.players import PlayerId
from AoE2ScenarioParser.datasets.terrains import TerrainId
from AoE2ScenarioParser.datasets.units import UnitInfo

from horde_config import (
    BALANCE,
    FEITORIA_ID,
    FORTIFIED_PALISADE_ID,
    KREPOST_ID,
    MAP_REVEALER_ID,
    MAP_SIZE,
    PALISADE_GATE_NW_SE_ID,
    PALISADE_GATE_SW_NE_ID,
    RELIC_ID,
    ROCK_CLIFF_ID,
    TERRAIN_SHALLOWS,
    TERRAIN_WATER,
    TORCH_ID,
    TREE_OAK_ID,
    TREE_PINE_ID,
    populate_ingame_scenario_descriptions,
)


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

    def mark_no_trees_box(self, x1: int, y1: int, x2: int, y2: int):
        for x in range(max(0, min(x1, x2)), min(self.size, max(x1, x2) + 1)):
            for y in range(max(0, min(y1, y2)), min(self.size, max(y1, y2) + 1)):
                self.no_tree_zones.add((x, y))

    def place_building(self, um, player: PlayerId, building_id: int, cx: int, cy: int, size_tiles: int, no_tree_margin: int = 3):
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

    def place_unit(self, um, player: PlayerId, unit_id: int, x: int, y: int, no_tree_margin: int = 2):
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
                        return um.add_unit(player=player, unit_const=unit_id, x=nx + 0.5, y=ny + 0.5)
        return None

    def place_wall_tile(self, um, player: PlayerId, wall_id: int, x: int, y: int, clear_trees_around: bool = True):
        if self.in_bounds(x, y, margin=0) and (x, y) not in self.occupied_tiles:
            self.occupied_tiles.add((x, y))
            if clear_trees_around:
                self.mark_no_trees(x, y, 1)
            return um.add_unit(player=player, unit_const=wall_id, x=x + 0.5, y=y + 0.5)
        return None

    def place_gate(self, um, player: PlayerId, gate_id: int, cx: int, cy: int, along_x: bool):
        if along_x:
            for x in range(cx - 2, cx + 2):
                self.occupied_tiles.add((x, cy))
            return um.add_unit(player=player, unit_const=gate_id, x=float(cx), y=cy + 0.5)

        for y in range(cy - 2, cy + 2):
            self.occupied_tiles.add((cx, y))
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


def reveal_building_center_permanent(um, cx: int, cy: int):
    um.add_unit(player=PlayerId.ONE, unit_const=MAP_REVEALER_ID, x=cx + 0.5, y=cy + 0.5)


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


def paint_organic_forest(mm, cx: int, cy: int, radius: float, terrain_id: int, seed: float = 0.0):
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
            elif dist <= eff_r + 1.5 and mm.get_tile(x, y).terrain_id == TerrainId.GRASS_1:
                mm.get_tile(x, y).terrain_id = TerrainId.GRASS_2


def build_rocky_cliff_ridge(mm, um, grid: SafeMapGrid, x1: int, y1: int, x2: int, y2: int, height: int = 3):
    steps = int(math.hypot(x2 - x1, y2 - y1))
    for i in range(steps + 1):
        t = i / max(1, steps)
        curve = math.sin(t * math.pi) * 3.0
        rx = round(x1 + (x2 - x1) * t + curve)
        ry = round(y1 + (y2 - y1) * t - curve)
        grid.add_hill_plateau(rx, ry, flat_radius=1, height=height)
        set_circle_terrain(mm, rx, ry, radius=2, terrain_id=TerrainId.DIRT_3)
        grid.mark_no_trees(rx, ry, radius=2)
        if i % 2 == 0 and grid.in_bounds(rx, ry) and (rx, ry) not in grid.occupied_tiles:
            grid.place_unit(um, PlayerId.GAIA, ROCK_CLIFF_ID, rx, ry, no_tree_margin=1)


def set_road(mm, grid: SafeMapGrid, x1: int, y1: int, x2: int, y2: int, width: int = 1):
    steps = int(math.hypot(x2 - x1, y2 - y1) * 2)
    for i in range(steps + 1):
        t = i / max(1, steps)
        rx = round(x1 + (x2 - x1) * t)
        ry = round(y1 + (y2 - y1) * t)
        set_circle_terrain(mm, rx, ry, width, TerrainId.ROAD)
        grid.mark_no_trees(rx, ry, width + 1)


def populate_forest_trees(
    mm,
    um,
    grid: SafeMapGrid,
    north_breach_box: tuple[int, int, int, int],
    east_breach_box: tuple[int, int, int, int],
) -> tuple[list, list]:
    north_trees = []
    east_trees = []
    nx1, ny1, nx2, ny2 = north_breach_box
    ex1, ey1, ex2, ey2 = east_breach_box

    for x in range(MAP_SIZE):
        for y in range(MAP_SIZE):
            if (x, y) in grid.occupied_tiles or (x, y) in grid.no_tree_zones:
                continue
            t_id = mm.get_tile(x, y).terrain_id
            tree_u = None
            if t_id == TerrainId.FOREST_OAK:
                grid.occupied_tiles.add((x, y))
                tree_u = um.add_unit(player=PlayerId.GAIA, unit_const=TREE_OAK_ID, x=x + 0.5, y=y + 0.5)
            elif t_id == TerrainId.FOREST_PINE:
                grid.occupied_tiles.add((x, y))
                tree_u = um.add_unit(player=PlayerId.GAIA, unit_const=TREE_PINE_ID, x=x + 0.5, y=y + 0.5)

            if tree_u is not None:
                if nx1 <= x <= nx2 and ny1 <= y <= ny2:
                    north_trees.append(tree_u)
                elif ex1 <= x <= ex2 and ey1 <= y <= ey2:
                    east_trees.append(tree_u)

    return north_trees, east_trees


def build_fortified_pass_defenses(um, grid: SafeMapGrid, owner: PlayerId, gx: int, gy: int, along_x: bool):
    if along_x:
        grid.place_gate(um, owner, PALISADE_GATE_SW_NE_ID, gx, gy, along_x=True)
        for x in range(gx - 7, gx + 8):
            if gx - 2 <= x < gx + 2:
                continue
            grid.place_wall_tile(um, owner, FORTIFIED_PALISADE_ID, x, gy, clear_trees_around=False)
        grid.place_building(um, owner, BuildingInfo.GUARD_TOWER.ID, gx - 4, gy + 4, size_tiles=2, no_tree_margin=1)
        grid.place_building(um, owner, BuildingInfo.GUARD_TOWER.ID, gx + 4, gy + 4, size_tiles=2, no_tree_margin=1)
    else:
        grid.place_gate(um, owner, PALISADE_GATE_NW_SE_ID, gx, gy, along_x=False)
        for y in range(gy - 7, gy + 8):
            if gy - 2 <= y < gy + 2:
                continue
            grid.place_wall_tile(um, owner, FORTIFIED_PALISADE_ID, gx, y, clear_trees_around=False)
        grid.place_building(um, owner, BuildingInfo.GUARD_TOWER.ID, gx - 4, gy - 4, size_tiles=2, no_tree_margin=1)
        grid.place_building(um, owner, BuildingInfo.GUARD_TOWER.ID, gx - 4, gy + 4, size_tiles=2, no_tree_margin=1)


def build_balance_sanctuary(mm, um, grid: SafeMapGrid, cx: int = 6, cy: int = 150):
    """
    Sanktuarium Balansu na poprzedniej pozycji w zachodnim lesie `(6, 150)`:
    - Środek `(6, 150)`: nieśmiertelny Inżynier Balansu (Król Gracza 1).
    - Góra `(6, 146)`: flaga ZWIĘKSZENIA trudności (+1 stopień).
    - Dół `(6, 154)`: flaga ZMNIEJSZENIA trudności (-1 stopień).
    """
    x_min, x_max = cx - 3, cx + 3
    y_min, y_max = cy - 5, cy + 5
    grid.mark_no_trees_box(x_min - 1, y_min - 1, x_max + 1, y_max + 1)

    for x in range(x_min, x_max + 1):
        for y in range(y_min, y_max + 1):
            grid.elev[x][y] = 0
            if x in (x_min, x_max) or y in (y_min, y_max):
                mm.get_tile(x, y).terrain_id = TerrainId.DIRT_3
                grid.place_wall_tile(um, PlayerId.GAIA, ROCK_CLIFF_ID, x, y, clear_trees_around=False)
            elif y <= cy - 3:
                mm.get_tile(x, y).terrain_id = TerrainId.DIRT_2
            elif y >= cy + 3:
                mm.get_tile(x, y).terrain_id = TerrainId.GRASS_2
            else:
                mm.get_tile(x, y).terrain_id = TerrainId.ROAD

    grid.place_unit(um, PlayerId.GAIA, TORCH_ID, cx - 1, cy - 4, no_tree_margin=0)
    grid.place_unit(um, PlayerId.GAIA, TORCH_ID, cx + 1, cy - 4, no_tree_margin=0)
    grid.place_unit(um, PlayerId.GAIA, TORCH_ID, cx - 1, cy + 4, no_tree_margin=0)
    grid.place_unit(um, PlayerId.GAIA, TORCH_ID, cx + 1, cy + 4, no_tree_margin=0)

    king_u = um.add_unit(player=PlayerId.ONE, unit_const=UnitInfo.KING.ID, x=cx + 0.5, y=cy + 0.5)
    grid.occupied_tiles.add((cx, cy))
    return king_u


def spawn_resource_cluster(um, grid: SafeMapGrid, cx: int, cy: int, res_const: int, count: int = 6):
    offsets = [
        (0, 0), (1, 0), (0, 1), (1, 1),
        (2, 0), (0, 2), (2, 1), (1, 2),
        (2, 2), (3, 0), (0, 3), (3, 1),
    ]
    for dx, dy in offsets[:count]:
        grid.place_unit(um, PlayerId.GAIA, res_const, cx + dx, cy + dy, no_tree_margin=2)


def spawn_symmetrical_player_base(um, mm, grid: SafeMapGrid, player: PlayerId, cx: int, cy: int):
    grid.mark_no_trees(cx, cy, radius=11)
    grid.place_building(um, player, BuildingInfo.TOWN_CENTER.ID, cx, cy, size_tiles=4, no_tree_margin=4)

    for dx, dy in [(-3, -2), (-3, -1), (-3, 0), (-3, 1), (-2, -3), (-1, -3)]:
        grid.place_unit(um, player, UnitInfo.VILLAGER_MALE.ID, cx + dx, cy + dy, no_tree_margin=1)
    grid.place_unit(um, player, UnitInfo.SCOUT_CAVALRY.ID, cx + 4, cy, no_tree_margin=1)

    for tx, ty in [(-5, -3), (4, -4), (-4, 4), (4, 3), (-5, 1), (3, -5)]:
        grid.place_unit(um, PlayerId.GAIA, TREE_OAK_ID, cx + tx, cy + ty, no_tree_margin=0)

    for sx, sy in [(-3, 2), (-2, 2), (-1, 2), (0, 2), (-3, 3), (-2, 3)]:
        grid.place_unit(um, PlayerId.GAIA, UnitInfo.SHEEP.ID, cx + sx, cy + sy, no_tree_margin=1)
    grid.place_unit(um, PlayerId.GAIA, UnitInfo.WILD_BOAR.ID, cx - 9, cy - 1, no_tree_margin=1)
    grid.place_unit(um, PlayerId.GAIA, UnitInfo.WILD_BOAR.ID, cx + 1, cy + 9, no_tree_margin=1)
    for dx, dy in [(-7, -7), (-8, -7), (-7, -8), (-8, -8)]:
        grid.place_unit(um, PlayerId.GAIA, UnitInfo.DEER.ID, cx + dx, cy + dy, no_tree_margin=1)

    spawn_resource_cluster(um, grid, cx - 8, cy - 4, OtherInfo.FORAGE_BUSH.ID, count=6)
    spawn_resource_cluster(um, grid, cx + 7, cy - 6, OtherInfo.GOLD_MINE.ID, count=8)
    spawn_resource_cluster(um, grid, cx + 7, cy + 5, OtherInfo.GOLD_MINE.ID, count=6)
    spawn_resource_cluster(um, grid, cx - 8, cy + 5, OtherInfo.STONE_MINE.ID, count=6)

    paint_organic_forest(mm, cx - 14, cy, radius=4.8, terrain_id=TerrainId.FOREST_OAK, seed=cx * 0.1)
    paint_organic_forest(mm, cx, cy + 14, radius=4.8, terrain_id=TerrainId.FOREST_PINE, seed=cy * 0.1)


def spawn_settlement_buildings(um, grid: SafeMapGrid, player: PlayerId, cx: int, cy: int, grade: int):
    reveal_building_center_permanent(um, cx, cy)
    if grade == 1:
        grid.mark_no_trees(cx, cy, radius=11)
        core = grid.place_building(um, player, BuildingInfo.GUARD_TOWER.ID, cx, cy, size_tiles=2, no_tree_margin=2)
        grid.place_building(um, player, BuildingInfo.GUARD_TOWER.ID, cx - 5, cy + 4, size_tiles=2, no_tree_margin=1)
        grid.place_building(um, player, BuildingInfo.GUARD_TOWER.ID, cx + 5, cy + 4, size_tiles=2, no_tree_margin=1)
        grid.place_building(um, player, BuildingInfo.BARRACKS.ID, cx - 6, cy - 4, size_tiles=3, no_tree_margin=2)
        grid.place_building(um, player, BuildingInfo.SIEGE_WORKSHOP.ID, cx + 6, cy - 4, size_tiles=3, no_tree_margin=2)
        return core

    if grade == 2:
        grid.mark_no_trees(cx, cy, radius=14)
        core = grid.place_building(um, player, BuildingInfo.CASTLE.ID, cx, cy, size_tiles=4, no_tree_margin=3)
        grid.place_building(um, player, BuildingInfo.ARCHERY_RANGE.ID, cx - 7, cy - 5, size_tiles=3, no_tree_margin=2)
        grid.place_building(um, player, BuildingInfo.MONASTERY.ID, cx + 7, cy - 5, size_tiles=3, no_tree_margin=2)
        for tx, ty in [(-9, -9), (9, -9), (-9, 9), (9, 9)]:
            grid.place_building(um, player, BuildingInfo.GUARD_TOWER.ID, cx + tx, cy + ty, size_tiles=2, no_tree_margin=2)
        return core

    grid.mark_no_trees(cx, cy, radius=18)
    core = grid.place_building(um, player, BuildingInfo.CASTLE.ID, cx, cy, size_tiles=4, no_tree_margin=3)
    grid.place_building(um, player, BuildingInfo.CASTLE.ID, cx - 9, cy + 8, size_tiles=4, no_tree_margin=2)
    grid.place_building(um, player, BuildingInfo.CASTLE.ID, cx + 9, cy - 8, size_tiles=4, no_tree_margin=2)
    grid.place_building(um, player, BuildingInfo.STABLE.ID, cx - 7, cy - 7, size_tiles=3, no_tree_margin=2)
    grid.place_building(um, player, BuildingInfo.SIEGE_WORKSHOP.ID, cx + 7, cy + 7, size_tiles=3, no_tree_margin=2)
    for tx, ty in [(-12, -12), (12, -12), (-12, 12), (12, 12)]:
        grid.place_building(um, player, BuildingInfo.KEEP.ID, cx + tx, cy + ty, size_tiles=2, no_tree_margin=2)
    return core


def build_map_and_entities(scenario) -> dict:
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
        p.food, p.wood, p.gold, p.stone = res["food"], res["wood"], res["gold"], res["stone"]

    for p_id in ai_players:
        p = pm.players[p_id]
        p.food, p.wood, p.gold, p.stone = 0, 0, 0, 0

    paint_natural_biome_background(mm, MAP_SIZE)

    # Pasmo górsko-leśne Twierdzy Sojuszu
    for x in range(0, 106, 8):
        if 72 <= x <= 84:
            continue
        grid.add_hill_plateau(x, 100, flat_radius=4, height=3)
    for y in range(100, 186, 8):
        if 134 <= y <= 146:
            continue
        grid.add_hill_plateau(104, y, flat_radius=4, height=3)

    set_box_terrain(mm, 0, 95, 108, 105, TerrainId.FOREST_PINE)
    set_box_terrain(mm, 99, 95, 109, 199, TerrainId.FOREST_PINE)

    gate_north = (48, 100)
    gate_center = (104, 114)
    gate_east = (104, 162)
    gate_trade = (104, 193)

    for gx, gy in [gate_north, gate_center, gate_east, gate_trade]:
        for x in range(gx - 6, gx + 7):
            for y in range(gy - 6, gy + 7):
                if 0 <= x < MAP_SIZE and 0 <= y < MAP_SIZE:
                    grid.elev[x][y] = 0
        set_box_terrain(mm, gx - 6, gy - 6, gx + 6, gy + 6, TerrainId.DIRT_1)
        grid.mark_no_trees_box(gx - 6, gy - 6, gx + 6, gy + 6)

    # 1) DUŻY PLAC HANDLOWY GRACZY W LEWYM DOLNYM ROGU (x: 2..24, y: 176..198 - czysty pod Markety graczy!)
    for x in range(2, 25):
        for y in range(176, MAP_SIZE - 1):
            grid.elev[x][y] = 0
    grid.mark_no_trees_box(2, 176, 24, MAP_SIZE - 2)
    set_box_terrain(mm, 3, 177, 23, MAP_SIZE - 2, TerrainId.DIRT_1)

    # 2) DOKŁADNE 10-KRATKOWE WYCIĘCIE WZDŁUŻ CAŁEGO SZLAKU HANDLOWEGO (y: 189..199, od x=2 do x=199)
    for x in range(2, MAP_SIZE):
        for y in range(189, MAP_SIZE):
            grid.elev[x][y] = 0
    grid.mark_no_trees_box(2, 189, MAP_SIZE - 1, MAP_SIZE - 1)
    set_road(mm, grid, 3, 194, 198, 194, width=1)

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
        "G1_East":  (132, 152),
        "G2_Snipers": (68, 34),
        "G2_Mages":   (148, 72),
        "G3_North":   (142, 24),
        "G3_East":    (176, 56),
    }
    grid.add_hill_plateau(*s_coords["G1_North"], flat_radius=9, height=1)
    grid.add_hill_plateau(*s_coords["G1_East"], flat_radius=9, height=1)
    grid.add_hill_plateau(*s_coords["G2_Snipers"], flat_radius=13, height=2)
    grid.add_hill_plateau(*s_coords["G2_Mages"], flat_radius=13, height=2)
    grid.add_hill_plateau(*s_coords["G3_North"], flat_radius=17, height=4)
    grid.add_hill_plateau(*s_coords["G3_East"], flat_radius=17, height=4)

    q1_pos = (154, 190)
    q2_pos = (28, 32)
    q3_pos = (142, 118)
    q4_pos = (105, 20)
    grid.add_hill_plateau(*q2_pos, flat_radius=9, height=4)
    grid.add_hill_plateau(*q3_pos, flat_radius=10, height=2)
    grid.add_hill_plateau(*q4_pos, flat_radius=9, height=3)

    build_rocky_cliff_ridge(mm, um, grid, 16, 48, 44, 48, height=3)
    build_rocky_cliff_ridge(mm, um, grid, 124, 134, 158, 134, height=2)

    # Sanktuarium Balansu na poprzedniej pozycji w zachodnim lesie na (6, 150)
    sanctuary_cx, sanctuary_cy = 6, 150
    balance_king = build_balance_sanctuary(mm, um, grid, cx=sanctuary_cx, cy=sanctuary_cy)

    grid.apply_smooth_elevation(mm)

    p_coords = {
        PlayerId.THREE: (32, 122),
        PlayerId.ONE:   (76, 124),
        PlayerId.TWO:   (32, 164),
        PlayerId.FOUR:  (76, 168),
    }

    set_road(mm, grid, *s_coords["G1_North"], *gate_north, width=1)
    set_road(mm, grid, *s_coords["G1_East"], *gate_east, width=1)
    set_road(mm, grid, *s_coords["G2_Mages"], *gate_center, width=1)
    set_road(mm, grid, *s_coords["G3_East"], *s_coords["G2_Mages"], width=1)

    for h_p in human_players:
        spawn_symmetrical_player_base(um, mm, grid, h_p, *p_coords[h_p])

    # Pełne Wzmocnione Palisady z Bramą na całej szerokości przełęczy (bez klifów)
    build_fortified_pass_defenses(um, grid, PlayerId.THREE, *gate_north, along_x=True)
    build_fortified_pass_defenses(um, grid, PlayerId.ONE, *gate_center, along_x=False)
    build_fortified_pass_defenses(um, grid, PlayerId.FOUR, *gate_east, along_x=False)
    build_fortified_pass_defenses(um, grid, PlayerId.FOUR, *gate_trade, along_x=False)

    for angle_deg in range(0, 360, 45):
        rad = math.radians(angle_deg)
        tx = round(116 + 10 * math.cos(rad))
        ty = round(114 + 10 * math.sin(rad))
        grid.place_unit(um, PlayerId.GAIA, TORCH_ID, tx, ty, no_tree_margin=1)

    fortress_heart_pos = (54, 146)
    allied_citadel = grid.place_building(
        um, PlayerId.TWO, FEITORIA_ID, fortress_heart_pos[0], fortress_heart_pos[1], size_tiles=5, no_tree_margin=3
    )

    s_g1_north = spawn_settlement_buildings(um, grid, PlayerId.FIVE, *s_coords["G1_North"], grade=1)
    s_g1_east  = spawn_settlement_buildings(um, grid, PlayerId.FIVE, *s_coords["G1_East"], grade=1)
    s_g2_snipers = spawn_settlement_buildings(um, grid, PlayerId.SIX, *s_coords["G2_Snipers"], grade=2)
    s_g2_mages   = spawn_settlement_buildings(um, grid, PlayerId.SEVEN, *s_coords["G2_Mages"], grade=2)
    s_g3_north = spawn_settlement_buildings(um, grid, PlayerId.EIGHT, *s_coords["G3_North"], grade=3)
    s_g3_east  = spawn_settlement_buildings(um, grid, PlayerId.EIGHT, *s_coords["G3_East"], grade=3)

    for sx, sy in [
        (48, 86), (118, 114), (120, 162), (76, 84), (120, 152),
        (68, 48), (134, 78), (128, 36), (160, 62), (162, 180), (78, 90), (114, 140),
    ]:
        grid.mark_no_trees(sx, sy, radius=6)

    reveal_building_center_permanent(um, *q1_pos)
    grid.mark_no_trees(*q1_pos, radius=9)
    set_circle_terrain(mm, *q1_pos, radius=7, terrain_id=TerrainId.DIRT_1)
    q1_bldg = grid.place_building(um, PlayerId.FIVE, BuildingInfo.MARKET.ID, q1_pos[0], q1_pos[1], size_tiles=4, no_tree_margin=2)
    grid.place_building(um, PlayerId.FIVE, BuildingInfo.GUARD_TOWER.ID, q1_pos[0] - 5, q1_pos[1] - 3, size_tiles=2, no_tree_margin=1)
    grid.place_building(um, PlayerId.FIVE, BuildingInfo.GUARD_TOWER.ID, q1_pos[0] + 5, q1_pos[1] - 3, size_tiles=2, no_tree_margin=1)

    reveal_building_center_permanent(um, *q2_pos)
    grid.mark_no_trees(*q2_pos, radius=11)
    set_circle_terrain(mm, *q2_pos, radius=10, terrain_id=TerrainId.DIRT_2)
    q2_bldg = grid.place_building(um, PlayerId.SIX, BuildingInfo.UNIVERSITY.ID, q2_pos[0], q2_pos[1], size_tiles=4, no_tree_margin=2)
    grid.place_building(um, PlayerId.SIX, BuildingInfo.KEEP.ID, q2_pos[0] - 5, q2_pos[1] + 5, size_tiles=2, no_tree_margin=1)
    grid.place_building(um, PlayerId.SIX, BuildingInfo.KEEP.ID, q2_pos[0] + 5, q2_pos[1] + 5, size_tiles=2, no_tree_margin=1)

    reveal_building_center_permanent(um, *q3_pos)
    grid.mark_no_trees(*q3_pos, radius=11)
    set_circle_terrain(mm, *q3_pos, radius=10, terrain_id=TerrainId.ROAD)
    q3_bldg = grid.place_building(um, PlayerId.EIGHT, KREPOST_ID, q3_pos[0], q3_pos[1], size_tiles=4, no_tree_margin=2)
    for tx, ty in [(-5, -5), (5, -5), (-5, 5), (5, 5)]:
        grid.place_building(um, PlayerId.EIGHT, BuildingInfo.KEEP.ID, q3_pos[0] + tx, q3_pos[1] + ty, size_tiles=2, no_tree_margin=1)
    for wx in range(-7, 8):
        grid.place_wall_tile(um, PlayerId.EIGHT, BuildingInfo.FORTIFIED_WALL.ID, q3_pos[0] + wx, q3_pos[1] - 8)
        grid.place_wall_tile(um, PlayerId.EIGHT, BuildingInfo.FORTIFIED_WALL.ID, q3_pos[0] + wx, q3_pos[1] + 8)

    reveal_building_center_permanent(um, *q4_pos)
    grid.mark_no_trees(*q4_pos, radius=10)
    set_circle_terrain(mm, *q4_pos, radius=9, terrain_id=TerrainId.DIRT_3)
    q4_bldg = grid.place_building(um, PlayerId.SEVEN, BuildingInfo.MONASTERY.ID, q4_pos[0], q4_pos[1], size_tiles=3, no_tree_margin=2)
    grid.place_building(um, PlayerId.SEVEN, BuildingInfo.KEEP.ID, q4_pos[0] - 5, q4_pos[1] + 4, size_tiles=2, no_tree_margin=1)
    grid.place_building(um, PlayerId.SEVEN, BuildingInfo.KEEP.ID, q4_pos[0] + 5, q4_pos[1] + 4, size_tiles=2, no_tree_margin=1)

    for rx, ry in [(54, 62), (116, 88), (168, 128), (92, 44)]:
        grid.place_unit(um, PlayerId.GAIA, RELIC_ID, rx, ry, no_tree_margin=2)
        spawn_resource_cluster(um, grid, rx + 3, ry + 3, OtherInfo.GOLD_MINE.ID, count=6)

    # Puszcza Zaplecza (omija Sanktuarium Balansu na 6, 150, Plac Targowy w lewym rogu oraz 10-kratkowy korytarz na y=189..199)
    set_box_terrain(mm, 0, 106, 12, 143, TerrainId.FOREST_OAK)
    set_box_terrain(mm, 0, 157, 12, 174, TerrainId.FOREST_OAK)
    set_box_terrain(mm, 26, 180, 98, 188, TerrainId.FOREST_PINE)

    for fx, fy, r, t_id, seed in [
        (54, 122, 5.5, TerrainId.FOREST_OAK, 0.5),
        (54, 172, 4.5, TerrainId.FOREST_PINE, 1.3),
        (20, 74, 7.0, TerrainId.FOREST_PINE, 1.7),
        (48, 74, 5.5, TerrainId.FOREST_OAK, 2.8),
        (16, 12, 7.5, TerrainId.FOREST_PINE, 3.9),
        (68, 12, 6.5, TerrainId.FOREST_OAK, 0.4),
        (108, 56, 6.0, TerrainId.FOREST_OAK, 1.6),
        (126, 94, 6.5, TerrainId.FOREST_PINE, 2.5),
        (172, 96, 7.0, TerrainId.FOREST_OAK, 3.2),
        (184, 136, 7.5, TerrainId.FOREST_PINE, 0.7),
        (184, 158, 5.0, TerrainId.FOREST_OAK, 1.9),
        (126, 172, 5.0, TerrainId.FOREST_OAK, 2.4),
        (184, 22, 7.0, TerrainId.FOREST_PINE, 3.7),
    ]:
        paint_organic_forest(mm, fx, fy, radius=r, terrain_id=t_id, seed=seed)

    north_breach_box = (75, 95, 80, 105)
    east_breach_box = (99, 137, 109, 142)
    north_breach_trees, east_breach_trees = populate_forest_trees(
        mm, um, grid, north_breach_box=north_breach_box, east_breach_box=east_breach_box
    )
    return {
        "ai_players": ai_players,
        "allied_citadel": allied_citadel,
        "balance_king": balance_king,
        "east_breach_trees": east_breach_trees,
        "gate_center": gate_center,
        "gate_east": gate_east,
        "gate_north": gate_north,
        "h_p": h_p,
        "human_players": human_players,
        "north_breach_trees": north_breach_trees,
        "p_coords": p_coords,
        "q1_bldg": q1_bldg,
        "q1_pos": q1_pos,
        "q2_bldg": q2_bldg,
        "q2_pos": q2_pos,
        "q3_bldg": q3_bldg,
        "q3_pos": q3_pos,
        "q4_bldg": q4_bldg,
        "q4_pos": q4_pos,
        "s_coords": s_coords,
        "s_g1_east": s_g1_east,
        "s_g1_north": s_g1_north,
        "s_g2_mages": s_g2_mages,
        "s_g2_snipers": s_g2_snipers,
        "s_g3_east": s_g3_east,
        "s_g3_north": s_g3_north,
        "sanctuary_cx": sanctuary_cx,
        "sanctuary_cy": sanctuary_cy,
        "sx": sx,
        "sy": sy,
        "tm": tm,
        "tx": tx,
        "ty": ty,
        "wx": wx,
    }
