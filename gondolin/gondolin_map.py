"""Map generation, SafeMapGrid, elevation smoothing, Gondolin city architecture, and entity placement."""

from __future__ import annotations

from typing import Any

from AoE2ScenarioParser.datasets.players import PlayerId
from AoE2ScenarioParser.datasets.terrains import TerrainId
from gondolin_config import (
    AI_PLAYERS,
    ARCHERY_RANGE_ID,
    BARRACKS_ID,
    BLACKSMITH_ID,
    CASTLE_ID,
    CYPRESS_TREE_ID,
    ENEMY_BALROG_BOSS_ID,
    ENEMY_DIRE_WOLF_ID,
    ENEMY_FIRE_DRAKE_ID,
    ENEMY_HEAVY_SCORPION_ID,
    ENEMY_IRON_DRAGON_RAM_ID,
    ENEMY_MOLE_PIKE_ID,
    ENEMY_MOLE_TRAITOR_ID,
    ENEMY_ORC_ARCHER_ID,
    ENEMY_ORC_BRUTE_ID,
    ENEMY_ORC_CROSSBOW_ID,
    ENEMY_ORC_INFANTRY_ID,
    FEITORIA_ID,
    FLAG_A_ID,
    FLAME_EFFECT_ID,
    FORTIFIED_WALL_ID,
    GUARD_TOWER_ID,
    HERO_DUILIN_ID,
    HERO_EARENDIL_ID,
    HERO_ECTHELION_ID,
    HERO_EGALMOTH_ID,
    HERO_GALDOR_ID,
    HERO_GLORFINDEL_ID,
    HERO_IDRIL_ID,
    HERO_ROG_ID,
    HERO_TUOR_ID,
    HOUSE_ID,
    HUMAN_PLAYERS,
    KEEP_ID,
    KREPOST_ID,
    LUMBER_CAMP_ID,
    MAP_REVEALER_ID,
    MAP_SIZE,
    MARKET_ID,
    MILL_ID,
    MINING_CAMP_ID,
    MONASTERY_ID,
    OAK_TREE_ID,
    OLIVE_TREE_ID,
    OUTPOST_ID,
    PAVILION_ID,
    PINE_TREE_ID,
    ROCK_CLIFF_ID,
    SANCTUARY_KING_ID,
    SIEGE_WORKSHOP_ID,
    STABLE_ID,
    STATUE_ID,
    TORCH_ID,
    UNIT_ARCH_LONGBOW_ID,
    UNIT_FOUNTAIN_GUARD_ID,
    UNIT_HAMMER_SMITH_ID,
    UNIT_HARP_HEALER_ID,
    UNIT_REFUGEE_CART_ID,
    UNIT_REFUGEE_CIV_ID,
    UNIT_SWALLOW_SNIPER_ID,
    UNIT_TREE_PIKE_ID,
    UNIVERSITY_ID,
    get_retinue_configs,
)


class SafeMapGrid:
    """Anti-collision grid tracking occupied tiles, road corridors, no-tree zones, and Lipschitz elevations."""

    def __init__(self, size: int = MAP_SIZE) -> None:
        self.size: int = size
        self.occupied_tiles: set[tuple[int, int]] = set()
        self.road_corridors: set[tuple[int, int]] = set()
        self.no_tree_zones: set[tuple[int, int]] = set()
        self.terrain: list[list[int]] = [
            [TerrainId.GRASS_1 for _ in range(size)] for _ in range(size)
        ]
        self.elevation: list[list[int]] = [
            [2 for _ in range(size)] for _ in range(size)
        ]

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if tile coordinates lie inside the map grid."""
        return 0 <= x < self.size and 0 <= y < self.size

    def mark_no_trees_box(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """Protect a rectangular area from forest tree placement."""
        xmin, xmax = max(0, min(x1, x2)), min(self.size - 1, max(x1, x2))
        ymin, ymax = max(0, min(y1, y2)), min(self.size - 1, max(y1, y2))
        for y in range(ymin, ymax + 1):
            for x in range(xmin, xmax + 1):
                self.no_tree_zones.add((x, y))

    def mark_road_box(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """Reserve a passable street/avenue box where decorative city buildings must not be placed."""
        xmin, xmax = max(0, min(x1, x2)), min(self.size - 1, max(x1, x2))
        ymin, ymax = max(0, min(y1, y2)), min(self.size - 1, max(y1, y2))
        for y in range(ymin, ymax + 1):
            for x in range(xmin, xmax + 1):
                self.road_corridors.add((x, y))
                self.no_tree_zones.add((x, y))

    def can_place_footprint(
        self,
        x: int,
        y: int,
        footprint: int = 1,
        respect_roads: bool = True,
    ) -> bool:
        """Return True if the footprint around (x, y) is free of occupied tiles (and road corridors)."""
        half = footprint // 2
        for ty in range(y - half, y + half + 1):
            for tx in range(x - half, x + half + 1):
                if not self.in_bounds(tx, ty):
                    return False
                if (tx, ty) in self.occupied_tiles:
                    return False
                if respect_roads and (tx, ty) in self.road_corridors:
                    return False
        return True

    def mark_occupied_box(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        clear_trees_around: bool = True,
    ) -> None:
        """Mark tiles as occupied by a structure or unit footprint."""
        xmin, xmax = max(0, min(x1, x2)), min(self.size - 1, max(x1, x2))
        ymin, ymax = max(0, min(y1, y2)), min(self.size - 1, max(y1, y2))
        for y in range(ymin, ymax + 1):
            for x in range(xmin, xmax + 1):
                self.occupied_tiles.add((x, y))
        if clear_trees_around:
            self.mark_no_trees_box(xmin - 2, ymin - 2, xmax + 2, ymax + 2)

    def paint_box(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        terrain_id: int,
        elev: int | None = None,
        protect_trees: bool = False,
        is_road: bool = False,
    ) -> None:
        """Paint terrain texture and optional elevation inside a rectangle."""
        xmin, xmax = max(0, min(x1, x2)), min(self.size - 1, max(x1, x2))
        ymin, ymax = max(0, min(y1, y2)), min(self.size - 1, max(y1, y2))
        for y in range(ymin, ymax + 1):
            for x in range(xmin, xmax + 1):
                self.terrain[y][x] = terrain_id
                if elev is not None:
                    self.elevation[y][x] = max(0, min(7, elev))
                if protect_trees or is_road:
                    self.no_tree_zones.add((x, y))
                if is_road:
                    self.road_corridors.add((x, y))

    def paint_circle(
        self,
        cx: int,
        cy: int,
        radius: int,
        terrain_id: int,
        elev: int | None = None,
        protect_trees: bool = False,
    ) -> None:
        """Paint terrain texture and optional elevation inside a disk."""
        r2 = radius * radius
        for y in range(max(0, cy - radius), min(self.size, cy + radius + 1)):
            for x in range(max(0, cx - radius), min(self.size, cx + radius + 1)):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r2:
                    self.terrain[y][x] = terrain_id
                    if elev is not None:
                        self.elevation[y][x] = max(0, min(7, elev))
                    if protect_trees:
                        self.no_tree_zones.add((x, y))

    def paint_corridor(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        half_width: int,
        terrain_id: int,
        elev: int | None = None,
        protect_trees: bool = True,
        is_road: bool = False,
    ) -> None:
        """Carve a wide corridor between two points (minimum 4+ tiles wide for convoys)."""
        steps = max(abs(x2 - x1), abs(y2 - y1), 1)
        for i in range(steps + 1):
            px = round(x1 + (x2 - x1) * i / steps)
            py = round(y1 + (y2 - y1) * i / steps)
            self.paint_box(
                px - half_width,
                py - half_width,
                px + half_width,
                py + half_width,
                terrain_id,
                elev=elev,
                protect_trees=protect_trees,
                is_road=is_road,
            )

    def smooth_elevations_lipschitz(self) -> None:
        """Enforce two-pass Lipschitz smoothing (|dh| <= 1 between adjacent tiles) to prevent graphic tears."""
        for _ in range(2):
            for y in range(self.size):
                for x in range(self.size):
                    if x > 0:
                        self.elevation[y][x] = min(
                            self.elevation[y][x], self.elevation[y][x - 1] + 1
                        )
                    if y > 0:
                        self.elevation[y][x] = min(
                            self.elevation[y][x], self.elevation[y - 1][x] + 1
                        )
            for y in range(self.size - 1, -1, -1):
                for x in range(self.size - 1, -1, -1):
                    if x < self.size - 1:
                        self.elevation[y][x] = min(
                            self.elevation[y][x], self.elevation[y][x + 1] + 1
                        )
                    if y < self.size - 1:
                        self.elevation[y][x] = min(
                            self.elevation[y][x], self.elevation[y + 1][x] + 1
                        )

    def place_unit_safe(
        self,
        um: Any,
        player: PlayerId,
        unit_id: int,
        x: int,
        y: int,
        footprint: int = 1,
        clear_trees_around: bool = True,
    ) -> Any:
        """Place a unit or building on the grid and register its footprint."""
        cx = max(1, min(self.size - 2, x))
        cy = max(1, min(self.size - 2, y))
        half = footprint // 2
        self.mark_occupied_box(
            cx - half,
            cy - half,
            cx + half,
            cy + half,
            clear_trees_around=clear_trees_around,
        )
        return um.add_unit(
            player=player,
            unit_const=unit_id,
            x=float(cx) + 0.5,
            y=float(cy) + 0.5,
        )


def _configure_players_and_diplomacy(pm: Any) -> None:
    """Configure P1-P4 as allied human Noldor Houses and P5-P8 as allied AI Morgoth forces."""
    pm.active_players = 8

    # Suggested Civilizations / Architecture sets (if exposed as writable attributes on Player)
    civ_map: dict[int, int] = {
        1: 36,  # Poles / Vikings (Tuor & Rog)
        2: 1,   # Britons (Ecthelion & Egalmoth)
        3: 2,   # Franks (Glorfindel & Duilin)
        4: 33,  # Burgundians (Idril & Galdor)
        5: 3,   # Goths (Angband Orc Horde)
        6: 35,  # Bohemians (Iron Dragons)
        7: 37,  # Dravidians / Persians (Balrogs)
        8: 4,   # Teutons (Maeglin's Traitors)
    }

    players = getattr(pm, "players", [])
    for idx in range(1, min(9, len(players))):
        p_obj = players[idx]
        if p_obj is None:
            continue
        is_human = idx <= 4
        for attr_name, val in [
            ("human", is_human),
            ("civilization", civ_map.get(idx, 1)),
            ("architecture_set", civ_map.get(idx, 1)),
            ("food", 0),
            ("wood", 0),
            ("stone", 0),
            ("gold", 0),
        ]:
            if hasattr(p_obj, attr_name):
                try:
                    setattr(p_obj, attr_name, val)
                except AttributeError:
                    pass

        # Set diplomacy matrix if diplomacy list is exposed on player object (0=Ally, 3=Enemy)
        dip = getattr(p_obj, "diplomacy", None)
        if isinstance(dip, list) and len(dip) >= 9:
            for other_idx in range(1, 9):
                if other_idx == idx:
                    continue
                same_team = (idx <= 4 and other_idx <= 4) or (idx >= 5 and other_idx >= 5)
                dip[other_idx] = 0 if same_team else 3


def _sculpt_world_terrain(grid: SafeMapGrid) -> None:
    """Sculpt the 240x240 landscape: Gondolin, Tumladen, Underground Way, Orfalch Echor, and Cirith Thoronath."""
    # 1. Base highland forest & Encircling Mountains (Echoriath)
    grid.paint_box(0, 0, MAP_SIZE - 1, MAP_SIZE - 1, TerrainId.FOREST_PINE, elev=5)

    # 2. Plains of Tumladen (Central basin, misty grassland, elev=2..3)
    grid.paint_box(95, 70, 175, 165, TerrainId.GRASS_2, elev=3, protect_trees=False)
    grid.paint_box(105, 85, 165, 150, TerrainId.DIRT_3, elev=3, protect_trees=True)

    # 3. Gondolin City Basin & Terraces (SW quadrant: X=10..112, Y=10..122)
    grid.paint_box(10, 10, 112, 122, TerrainId.GRASS_1, elev=2, protect_trees=True)

    # Outer Ring Wall foundation & Northern Moat
    grid.paint_box(16, 16, 104, 114, TerrainId.ROAD, elev=2, protect_trees=True)
    # Northern Moat (Shallows = 4, initially blocked by rocks until P2 opens the Aqueduct!)
    grid.paint_box(22, 112, 98, 116, TerrainId.SHALLOWS, elev=1, protect_trees=True)

    # Middle City Terrace (elev=4)
    grid.paint_box(28, 28, 92, 98, TerrainId.ROAD_BROKEN, elev=4, protect_trees=True)

    # Amon Gwareth - Royal Hill at the heart of Gondolin (X=46..76, Y=48..78, elev=6)
    grid.paint_box(46, 48, 76, 78, TerrainId.ROAD, elev=6, protect_trees=True)
    # Royal Fountain water basin in the center of Amon Gwareth
    grid.paint_circle(61, 61, 5, TerrainId.SHALLOWS, elev=6, protect_trees=True)

    # Water Reservoir & Aqueduct Channel in P2's Fountain District (X=76..96, Y=58..76)
    grid.paint_box(80, 66, 92, 72, TerrainId.WATER_AZURE, elev=4, protect_trees=True)
    grid.paint_corridor(
        76, 65, 65, 63, 2, TerrainId.SHALLOWS, elev=5, protect_trees=True, is_road=True
    )

    # Grand Avenues of Gondolin (marked as road_corridors so city blocks never obstruct movement!)
    # North Avenue (Great Gate -> Great Market -> Amon Gwareth)
    grid.paint_corridor(
        61, 118, 61, 76, 4, TerrainId.ROAD, elev=3, protect_trees=True, is_road=True
    )
    # South Avenue (South Gate -> Tuor's Quarter -> Amon Gwareth)
    grid.paint_corridor(
        61, 16, 61, 48, 4, TerrainId.ROAD, elev=3, protect_trees=True, is_road=True
    )
    # West Avenue (Forges of Rog -> Amon Gwareth)
    grid.paint_corridor(
        20, 63, 46, 63, 4, TerrainId.ROAD, elev=3, protect_trees=True, is_road=True
    )
    # East Avenue (East Gate -> Great Market -> Amon Gwareth)
    grid.paint_corridor(
        104, 63, 76, 63, 4, TerrainId.ROAD, elev=3, protect_trees=True, is_road=True
    )
    # SW Avenue (Caragdur & House of Tuor/Idril -> South Gate & Forges)
    grid.paint_corridor(
        24, 26, 61, 26, 3, TerrainId.ROAD, elev=2, protect_trees=True, is_road=True
    )
    grid.paint_corridor(
        26, 26, 26, 63, 3, TerrainId.ROAD, elev=2, protect_trees=True, is_road=True
    )
    # SE Avenue (Court of Salgant / House of the Harp)
    grid.paint_corridor(
        61, 26, 90, 26, 3, TerrainId.ROAD, elev=2, protect_trees=True, is_road=True
    )
    grid.paint_corridor(
        90, 26, 90, 63, 3, TerrainId.ROAD, elev=3, protect_trees=True, is_road=True
    )
    # Inner Ring Boulevards connecting northern districts to East & West Avenues
    grid.paint_corridor(
        34, 63, 34, 98, 2, TerrainId.ROAD, elev=3, protect_trees=True, is_road=True
    )
    grid.paint_corridor(
        34, 96, 86, 96, 2, TerrainId.ROAD, elev=3, protect_trees=True, is_road=True
    )
    grid.paint_corridor(
        82, 63, 82, 98, 2, TerrainId.ROAD, elev=3, protect_trees=True, is_road=True
    )

    # 4. Phase II Dual Routes across Tumladen:
    # Route A (Lower): Secret Way of Idril (Underground Tunnel & Dry Riverbed, Y=35..55, X=105..175, elev=1)
    grid.paint_box(102, 22, 182, 58, TerrainId.FOREST_PINE, elev=5, protect_trees=False)
    grid.paint_corridor(
        72, 52, 112, 38, 3, TerrainId.ROAD_FUNGUS, elev=1, protect_trees=True, is_road=True
    )
    grid.paint_corridor(
        112, 38, 175, 42, 4, TerrainId.ROAD_BROKEN, elev=1, protect_trees=True, is_road=True
    )
    grid.paint_corridor(
        175, 42, 185, 85, 4, TerrainId.DIRT_1, elev=2, protect_trees=True, is_road=True
    )

    # Route B (Upper): Misty Plains of Tumladen & Cliff Overlook (X=105..175, Y=65..125, elev=3)
    grid.paint_corridor(
        76, 72, 115, 88, 4, TerrainId.DIRT_2, elev=3, protect_trees=True, is_road=True
    )
    grid.paint_corridor(
        115, 88, 172, 88, 5, TerrainId.DIRT_2, elev=3, protect_trees=True, is_road=True
    )
    grid.paint_box(122, 58, 165, 68, TerrainId.ROAD_BROKEN, elev=4, protect_trees=True)
    grid.paint_corridor(
        172, 88, 185, 85, 4, TerrainId.ROAD, elev=3, protect_trees=True, is_road=True
    )

    # 5. Phase III: Orfalch Echor (Gorge of Seven Gates) & Cirith Thoronath (NE Quadrant)
    grid.paint_corridor(
        185, 85, 212, 130, 4, TerrainId.ROAD, elev=4, protect_trees=True, is_road=True
    )
    grid.paint_corridor(
        212, 130, 190, 175, 4, TerrainId.ROAD, elev=5, protect_trees=True, is_road=True
    )
    # High goat-paths flanking Orfalch Echor for P3/P4 vertical cooperation
    grid.paint_corridor(
        176, 92, 198, 132, 2, TerrainId.DIRT_3, elev=6, protect_trees=True, is_road=True
    )
    grid.paint_corridor(
        198, 132, 178, 175, 2, TerrainId.DIRT_3, elev=7, protect_trees=True, is_road=True
    )
    grid.paint_corridor(
        198, 132, 212, 130, 2, TerrainId.DIRT_3, elev=5, protect_trees=True, is_road=True
    )
    grid.paint_corridor(
        178, 175, 190, 175, 2, TerrainId.DIRT_3, elev=6, protect_trees=True, is_road=True
    )

    # Cirith Thoronath (Eagle's Cleft) - narrow precipice above a deep chasm (X=190..225, Y=175..225)
    grid.paint_box(196, 178, 232, 215, TerrainId.WATER_AZURE, elev=0, protect_trees=True)
    grid.paint_corridor(
        190, 175, 190, 218, 3, TerrainId.ROAD, elev=7, protect_trees=True, is_road=True
    )
    grid.paint_corridor(
        190, 218, 224, 224, 4, TerrainId.ROAD, elev=6, protect_trees=True, is_road=True
    )
    grid.paint_box(
        193, 194, 203, 202, TerrainId.ROAD_BROKEN, elev=7, protect_trees=True, is_road=True
    )

    # 6. Balance Sanctuary chamber isolated in NW corner (X=6..18, Y=222..234)
    grid.paint_box(4, 220, 20, 236, TerrainId.ROAD, elev=4, protect_trees=True, is_road=True)

    # Apply two-pass Lipschitz smoothing so all elevation transitions are valid
    grid.smooth_elevations_lipschitz()


def _build_gondolin_walls_and_districts(
    grid: SafeMapGrid,
    um: Any,
    bldg_counter: dict[PlayerId, int],
) -> int:
    """Construct Gondolin's outer/inner fortifications, gatehouses, and 7 House districts (~110 buildings)."""
    placed_buildings = 0

    def add_city_bldg(
        player: PlayerId,
        unit_id: int,
        x: int,
        y: int,
        footprint: int = 3,
        respect_roads: bool = True,
    ) -> bool:
        nonlocal placed_buildings
        if not grid.can_place_footprint(x, y, footprint=footprint, respect_roads=respect_roads):
            return False
        grid.place_unit_safe(um, player, unit_id, x, y, footprint=footprint)
        bldg_counter[player] = bldg_counter.get(player, 0) + 1
        placed_buildings += 1
        return True

    # =========================================================================
    # A. CONTINUOUS OUTER STONE WALLS OF GONDOLIN (X=16..104, Y=16..111)
    # =========================================================================
    # Leave wide passable openings at the 4 Grand Gates and Northern/Eastern Siege Breaches
    for wx in range(16, 105):
        # South Wall (Y=16): South Grand Gate opening at X=57..65
        if not (57 <= wx <= 65):
            if wx % 8 == 0:
                add_city_bldg(PlayerId.ONE, GUARD_TOWER_ID, wx, 16, footprint=2, respect_roads=False)
            else:
                add_city_bldg(PlayerId.ONE, FORTIFIED_WALL_ID, wx, 16, footprint=1, respect_roads=False)

        # North Wall (Y=111): Breached at X=55..67 (North Avenue) & X=80..86 (NE Breach)
        if not (55 <= wx <= 67 or 80 <= wx <= 86):
            if wx % 8 == 0:
                add_city_bldg(PlayerId.THREE, GUARD_TOWER_ID, wx, 111, footprint=2, respect_roads=False)
            else:
                add_city_bldg(PlayerId.THREE, FORTIFIED_WALL_ID, wx, 111, footprint=1, respect_roads=False)

    for wy in range(17, 111):
        # West Wall (X=16): West Forge Gate opening at Y=59..67
        if not (59 <= wy <= 67):
            if wy % 8 == 0:
                add_city_bldg(PlayerId.FOUR, GUARD_TOWER_ID, 16, wy, footprint=2, respect_roads=False)
            else:
                add_city_bldg(PlayerId.FOUR, FORTIFIED_WALL_ID, 16, wy, footprint=1, respect_roads=False)

        # East Wall (X=104): East Breach opening at Y=57..69
        if not (57 <= wy <= 69):
            if wy % 8 == 0:
                add_city_bldg(PlayerId.TWO, GUARD_TOWER_ID, 104, wy, footprint=2, respect_roads=False)
            else:
                add_city_bldg(PlayerId.TWO, FORTIFIED_WALL_ID, 104, wy, footprint=1, respect_roads=False)

    # Grand Gatehouse Bastions (KEEP_ID = 235) flanking the 4 main avenues
    gate_bastions: list[tuple[PlayerId, int, int]] = [
        (PlayerId.ONE, 56, 16),
        (PlayerId.ONE, 66, 16),
        (PlayerId.THREE, 54, 111),
        (PlayerId.THREE, 68, 111),
        (PlayerId.ONE, 16, 58),
        (PlayerId.ONE, 16, 68),
        (PlayerId.TWO, 104, 56),
        (PlayerId.TWO, 104, 70),
    ]
    for p_id, gx, gy in gate_bastions:
        add_city_bldg(p_id, KEEP_ID, gx, gy, footprint=2, respect_roads=False)

    # =========================================================================
    # B. INNER CITADEL RING WALL AROUND AMON GWARETH (X=46..76, Y=48..78)
    # =========================================================================
    for cx in range(46, 77):
        if not (57 <= cx <= 65):
            add_city_bldg(PlayerId.ONE, FORTIFIED_WALL_ID, cx, 48, footprint=1, respect_roads=False)
            add_city_bldg(PlayerId.ONE, FORTIFIED_WALL_ID, cx, 78, footprint=1, respect_roads=False)
    for cy in range(49, 78):
        # Leave West (59..67), East (59..67), Secret Tunnel (49..56), and Postern (69..76) open
        if not (59 <= cy <= 67):
            add_city_bldg(PlayerId.ONE, FORTIFIED_WALL_ID, 46, cy, footprint=1, respect_roads=False)
        if not (49 <= cy <= 56 or 59 <= cy <= 67 or 69 <= cy <= 76):
            add_city_bldg(PlayerId.TWO, FORTIFIED_WALL_ID, 76, cy, footprint=1, respect_roads=False)

    # Corner Citadel Keeps on Amon Gwareth
    for kx, ky in [(46, 48), (76, 48), (46, 78), (76, 78)]:
        add_city_bldg(PlayerId.ONE, KEEP_ID, kx, ky, footprint=2, respect_roads=False)

    # =========================================================================
    # C. PLANNED URBAN DISTRICTS OF THE SEVEN HOUSES (~105 BUILDINGS)
    # =========================================================================
    # 1. West Quarter: House of the Hammer of Wrath (Rog's Smithies, Armories & Guilds)
    west_hammer_layout: list[tuple[int, int, int, int]] = [
        (BLACKSMITH_ID, 20, 54, 3),
        (BLACKSMITH_ID, 29, 54, 3),
        (MINING_CAMP_ID, 20, 48, 2),
        (BARRACKS_ID, 38, 54, 3),
        (BARRACKS_ID, 38, 72, 3),
        (BLACKSMITH_ID, 20, 76, 3),
        (MINING_CAMP_ID, 28, 78, 2),
        (HOUSE_ID, 20, 43, 2),
        (HOUSE_ID, 24, 43, 2),
        (HOUSE_ID, 38, 46, 2),
        (HOUSE_ID, 41, 46, 2),
        (HOUSE_ID, 38, 78, 2),
        (HOUSE_ID, 41, 78, 2),
        (PAVILION_ID, 31, 48, 2),
    ]
    for u_id, bx, by, fp in west_hammer_layout:
        add_city_bldg(PlayerId.ONE, u_id, bx, by, footprint=fp)

    # 2. South Quarter: House of the Wing (Tuor's Royal Guard Barracks & Noble Mansions)
    south_wing_layout: list[tuple[int, int, int, int]] = [
        (BARRACKS_ID, 48, 34, 3),
        (BARRACKS_ID, 72, 34, 3),
        (ARCHERY_RANGE_ID, 48, 41, 3),
        (ARCHERY_RANGE_ID, 72, 41, 3),
        (BLACKSMITH_ID, 53, 20, 3),
        (BLACKSMITH_ID, 69, 20, 3),
        (PAVILION_ID, 54, 35, 2),
        (PAVILION_ID, 68, 35, 2),
        (HOUSE_ID, 46, 20, 2),
        (HOUSE_ID, 49, 20, 2),
        (HOUSE_ID, 73, 20, 2),
        (HOUSE_ID, 76, 20, 2),
        (HOUSE_ID, 42, 34, 2),
        (HOUSE_ID, 42, 38, 2),
        (HOUSE_ID, 78, 34, 2),
        (HOUSE_ID, 78, 38, 2),
    ]
    for u_id, bx, by, fp in south_wing_layout:
        add_city_bldg(PlayerId.ONE, u_id, bx, by, footprint=fp)

    # 3. SW Quarter: House of the Tree & Wardens of the Secret Way (Idril & Galdor)
    sw_tree_layout: list[tuple[int, int, int, int]] = [
        (BARRACKS_ID, 33, 20, 3),
        (ARCHERY_RANGE_ID, 33, 35, 3),
        (LUMBER_CAMP_ID, 20, 32, 2),
        (PAVILION_ID, 31, 31, 2),
        (PAVILION_ID, 20, 19, 2),
        (HOUSE_ID, 20, 29, 2),
        (HOUSE_ID, 37, 20, 2),
        (HOUSE_ID, 37, 34, 2),
        (HOUSE_ID, 37, 38, 2),
        (HOUSE_ID, 30, 42, 2),
        (HOUSE_ID, 38, 42, 2),
    ]
    for u_id, bx, by, fp in sw_tree_layout:
        add_city_bldg(PlayerId.FOUR, u_id, bx, by, footprint=fp)

    # 4. East Quarter: House of the Fountain & Heavenly Arch (Ecthelion & Egalmoth)
    east_fountain_layout: list[tuple[int, int, int, int]] = [
        (ARCHERY_RANGE_ID, 86, 52, 3),
        (ARCHERY_RANGE_ID, 98, 52, 3),
        (BARRACKS_ID, 96, 74, 3),
        (MONASTERY_ID, 80, 48, 3),
        (MARKET_ID, 96, 44, 4),
        (MILL_ID, 86, 44, 2),
        (PAVILION_ID, 79, 55, 2),
        (PAVILION_ID, 98, 70, 2),
        (HOUSE_ID, 80, 42, 2),
        (HOUSE_ID, 83, 42, 2),
        (HOUSE_ID, 98, 38, 2),
        (HOUSE_ID, 100, 48, 2),
        (HOUSE_ID, 100, 76, 2),
        (HOUSE_ID, 94, 82, 2),
        (HOUSE_ID, 98, 82, 2),
    ]
    for u_id, bx, by, fp in east_fountain_layout:
        add_city_bldg(PlayerId.TWO, u_id, bx, by, footprint=fp)

    # 5. SE Quarter: Court of Salgant & House of the Harp
    se_harp_layout: list[tuple[int, int, int, int]] = [
        (STABLE_ID, 82, 20, 3),
        (STABLE_ID, 98, 20, 3),
        (MONASTERY_ID, 82, 36, 3),
        (PAVILION_ID, 98, 32, 2),
        (HOUSE_ID, 86, 19, 2),
        (HOUSE_ID, 94, 19, 2),
        (HOUSE_ID, 98, 26, 2),
        (HOUSE_ID, 84, 38, 2),
        (HOUSE_ID, 95, 38, 2),
    ]
    for u_id, bx, by, fp in se_harp_layout:
        add_city_bldg(PlayerId.THREE, u_id, bx, by, footprint=fp)

    # 6. NE & North Quarter: House of the Golden Flower & House of the Swallow (Glorfindel & Duilin)
    ne_flower_swallow_layout: list[tuple[int, int, int, int]] = [
        (STABLE_ID, 74, 84, 3),
        (ARCHERY_RANGE_ID, 88, 86, 3),
        (ARCHERY_RANGE_ID, 88, 102, 3),
        (BARRACKS_ID, 68, 102, 3),
        (UNIVERSITY_ID, 96, 92, 4),
        (PAVILION_ID, 74, 90, 2),
        (PAVILION_ID, 80, 104, 2),
        (HOUSE_ID, 72, 80, 2),
        (HOUSE_ID, 76, 80, 2),
        (HOUSE_ID, 88, 80, 2),
        (HOUSE_ID, 92, 80, 2),
        (HOUSE_ID, 96, 100, 2),
        (HOUSE_ID, 96, 104, 2),
        (HOUSE_ID, 84, 106, 2),
    ]
    for u_id, bx, by, fp in ne_flower_swallow_layout:
        add_city_bldg(PlayerId.THREE, u_id, bx, by, footprint=fp)

    # 7. NW Quarter: House of the Pillar & Tower of Snow (Penlod's Artisans - under heavy siege)
    nw_pillar_layout: list[tuple[int, int, int, int]] = [
        (UNIVERSITY_ID, 42, 86, 4),
        (MARKET_ID, 24, 88, 4),
        (BLACKSMITH_ID, 44, 102, 3),
        (BARRACKS_ID, 24, 100, 3),
        (LUMBER_CAMP_ID, 30, 82, 2),
        (PAVILION_ID, 48, 84, 2),
        (HOUSE_ID, 20, 84, 2),
        (HOUSE_ID, 20, 92, 2),
        (HOUSE_ID, 20, 104, 2),
        (HOUSE_ID, 28, 104, 2),
        (HOUSE_ID, 38, 104, 2),
        (HOUSE_ID, 48, 104, 2),
        (HOUSE_ID, 42, 92, 2),
        (HOUSE_ID, 48, 92, 2),
    ]
    for u_id, bx, by, fp in nw_pillar_layout:
        add_city_bldg(PlayerId.TWO, u_id, bx, by, footprint=fp)

    # Ornamental Statues, Banners, Torches, and Olive/Cypress Gardens along the Grand Avenues
    avenue_ornaments: list[tuple[int, int, int]] = [
        (STATUE_ID, 56, 32),
        (STATUE_ID, 66, 32),
        (STATUE_ID, 56, 44),
        (STATUE_ID, 66, 44),
        (STATUE_ID, 56, 82),
        (STATUE_ID, 66, 82),
        (STATUE_ID, 42, 58),
        (STATUE_ID, 42, 68),
        (STATUE_ID, 80, 58),
        (STATUE_ID, 80, 68),
        (FLAG_A_ID, 57, 49),
        (FLAG_A_ID, 65, 49),
        (FLAG_A_ID, 57, 77),
        (FLAG_A_ID, 65, 77),
        (OLIVE_TREE_ID, 51, 52),
        (OLIVE_TREE_ID, 71, 52),
        (OLIVE_TREE_ID, 51, 74),
        (OLIVE_TREE_ID, 71, 74),
    ]
    for obj_id, ox, oy in avenue_ornaments:
        if grid.can_place_footprint(ox, oy, footprint=1, respect_roads=False):
            grid.place_unit_safe(um, PlayerId.GAIA, obj_id, ox, oy, footprint=1)

    return placed_buildings


def _populate_forests_and_borders(grid: SafeMapGrid, um: Any) -> None:
    """Populate physical tree objects across 0..MAP_SIZE-1 and seal the Balance Sanctuary."""
    for y in range(MAP_SIZE):
        for x in range(MAP_SIZE):
            if (x, y) in grid.occupied_tiles or (x, y) in grid.no_tree_zones:
                continue
            is_border = x in (0, MAP_SIZE - 1) or y in (0, MAP_SIZE - 1)
            if is_border or grid.terrain[y][x] == TerrainId.FOREST_PINE:
                tree_id = PINE_TREE_ID if (x + y) % 3 != 0 else OAK_TREE_ID
                um.add_unit(
                    player=PlayerId.GAIA,
                    unit_const=tree_id,
                    x=float(x) + 0.5,
                    y=float(y) + 0.5,
                )
                grid.occupied_tiles.add((x, y))

    # Surround Balance Sanctuary (X=4..20, Y=220..236) with indestructible rock cliffs
    for x in range(4, 21):
        for y in (220, 236):
            grid.place_unit_safe(
                um, PlayerId.GAIA, ROCK_CLIFF_ID, x, y, clear_trees_around=False
            )
    for y in range(221, 236):
        for x in (4, 20):
            grid.place_unit_safe(
                um, PlayerId.GAIA, ROCK_CLIFF_ID, x, y, clear_trees_around=False
            )


def build_map_and_entities(scenario: Any) -> dict[str, Any]:
    """Build the 240x240 Gondolin map, place initial structures/units for P1-P8, and return context dict."""
    mm = scenario.map_manager
    um = scenario.unit_manager
    pm = scenario.player_manager

    mm.map_size = MAP_SIZE
    _configure_players_and_diplomacy(pm)

    grid = SafeMapGrid(MAP_SIZE)
    _sculpt_world_terrain(grid)

    # Copy terrain and Lipschitz-smoothed elevation to AoE2ScenarioParser tiles
    for y in range(MAP_SIZE):
        for x in range(MAP_SIZE):
            tile = mm.get_tile(x, y)
            tile.terrain_id = grid.terrain[y][x]
            tile.elevation = grid.elevation[y][x]

    destructible_rocks: dict[str, list[int]] = {
        "caragdur_blockade": [],
        "north_fire_objects": [],
        "aqueduct_dry_rocks": [],
        "salgant_gate_rocks": [],
        "tumladen_exit_rocks": [],
        "orfalch_gate_1": [],
        "orfalch_gate_2": [],
        "orfalch_gate_3": [],
        "orfalch_gate_4": [],
        "orfalch_gate_5": [],
        "orfalch_gate_6": [],
        "orfalch_gate_7": [],
        "cirith_exit_rocks": [],
    }
    quest_buildings: dict[str, dict[str, Any]] = {}
    player_bldg_counts: dict[PlayerId, int] = {p: 0 for p in HUMAN_PLAYERS}

    def register_bldg(
        key: str,
        player: PlayerId,
        unit_id: int,
        x: int,
        y: int,
        footprint: int = 3,
    ) -> Any:
        obj = grid.place_unit_safe(um, player, unit_id, x, y, footprint=footprint)
        quest_buildings[key] = {
            "ref_id": obj.reference_id,
            "x": x,
            "y": y,
            "player": player,
            "unit_id": unit_id,
        }
        if player in player_bldg_counts:
            player_bldg_counts[player] += 1
        return obj

    # =========================================================================
    # 1. KEY LANDMARKS & QUEST STRUCTURES IN GONDOLIN
    # =========================================================================
    # Amon Gwareth Royal Acropolis (Wieza Krola Turgona + Fontanna Krolewska + Drzewa Glingal i Belthil)
    register_bldg("tower_of_turgon", PlayerId.ONE, CASTLE_ID, 61, 71, footprint=4)
    grid.place_unit_safe(um, PlayerId.ONE, KEEP_ID, 55, 71, footprint=2)
    grid.place_unit_safe(um, PlayerId.ONE, KEEP_ID, 67, 71, footprint=2)
    player_bldg_counts[PlayerId.ONE] += 2

    register_bldg(
        "royal_fountain_bldg", PlayerId.TWO, MONASTERY_ID, 61, 54, footprint=3
    )

    # Royal Fountain statues, cypresses, and braziers around (61, 61)
    for ox, oy in [(57, 57), (65, 57), (57, 65), (65, 65)]:
        grid.place_unit_safe(um, PlayerId.GAIA, STATUE_ID, ox, oy, footprint=1)
        grid.place_unit_safe(um, PlayerId.GAIA, CYPRESS_TREE_ID, ox, oy + 1, footprint=1)
        grid.place_unit_safe(um, PlayerId.GAIA, TORCH_ID, ox + 1, oy, footprint=1)

    # Sacred Trees Glingal (Gold) & Belthil (Silver) for P4 Idril side quest
    register_bldg("glingal_tree", PlayerId.FOUR, PAVILION_ID, 53, 62, footprint=2)
    register_bldg("belthil_tree", PlayerId.FOUR, PAVILION_ID, 69, 62, footprint=2)

    # Path A (West): Forges of Rog & Royal Armory
    register_bldg("great_forge", PlayerId.ONE, BLACKSMITH_ID, 24, 63, footprint=3)
    register_bldg(
        "forge_workshop", PlayerId.ONE, SIEGE_WORKSHOP_ID, 24, 70, footprint=4
    )
    for cy_off in (59, 63, 67):
        grid.place_unit_safe(
            um, PlayerId.ONE, UNIT_REFUGEE_CART_ID, 29, cy_off, footprint=1
        )

    # Path B (East): Great Market of Penlod & Fountain Aqueduct
    register_bldg("great_market", PlayerId.TWO, MARKET_ID, 94, 63, footprint=4)
    register_bldg(
        "aqueduct_control", PlayerId.EIGHT, UNIVERSITY_ID, 84, 74, footprint=4
    )

    # North Quarter: Tower of Snow (P3 Duilin high vantage point)
    register_bldg("snow_watchtower", PlayerId.THREE, KEEP_ID, 74, 106, footprint=2)

    # Path C (South-East): Court of Salgant (House of the Harp)
    register_bldg("salgant_manor", PlayerId.THREE, CASTLE_ID, 92, 26, footprint=4)
    for bx in range(86, 95, 2):
        r_obj = grid.place_unit_safe(
            um,
            PlayerId.GAIA,
            ROCK_CLIFF_ID,
            bx,
            33,
            footprint=1,
            clear_trees_around=False,
        )
        destructible_rocks["salgant_gate_rocks"].append(r_obj.reference_id)
    for hx in (89, 91, 93):
        grid.place_unit_safe(
            um, PlayerId.THREE, UNIT_HARP_HEALER_ID, hx, 22, footprint=1
        )

    # SW Quarter: House of Tuor & Caragdur Precipice (P4 cut off by P8 Maeglin's Traitors)
    register_bldg("house_of_tuor", PlayerId.FOUR, KREPOST_ID, 24, 24, footprint=4)
    register_bldg("caragdur_keep", PlayerId.EIGHT, KEEP_ID, 18, 42, footprint=2)
    for by in range(22, 31):
        r_obj = grid.place_unit_safe(
            um,
            PlayerId.GAIA,
            ROCK_CLIFF_ID,
            42,
            by,
            footprint=1,
            clear_trees_around=False,
        )
        destructible_rocks["caragdur_blockade"].append(r_obj.reference_id)

    # North Quarter Fire Hazard (hurts P3 until P2 captures aqueduct_control)
    for fx in range(56, 67, 3):
        for fy in (94, 100):
            f_obj = grid.place_unit_safe(
                um,
                PlayerId.GAIA,
                FLAME_EFFECT_ID,
                fx,
                fy,
                footprint=1,
                clear_trees_around=False,
            )
            destructible_rocks["north_fire_objects"].append(f_obj.reference_id)

    # Rocks blocking the Northern Moat shallows (removed when P2 floods the moat)
    for rx in range(48, 75, 3):
        r_obj = grid.place_unit_safe(
            um,
            PlayerId.GAIA,
            ROCK_CLIFF_ID,
            rx,
            114,
            footprint=1,
            clear_trees_around=False,
        )
        destructible_rocks["aqueduct_dry_rocks"].append(r_obj.reference_id)

    # Phase II Exit Gates (Sealed until Phase I defence of Amon Gwareth concludes)
    register_bldg("idril_waygate", PlayerId.FOUR, OUTPOST_ID, 74, 52, footprint=2)
    for ry in range(49, 56):
        r_obj = grid.place_unit_safe(
            um,
            PlayerId.GAIA,
            ROCK_CLIFF_ID,
            78,
            ry,
            footprint=1,
            clear_trees_around=False,
        )
        destructible_rocks["tumladen_exit_rocks"].append(r_obj.reference_id)
    for ry in range(69, 76):
        r_obj = grid.place_unit_safe(
            um,
            PlayerId.GAIA,
            ROCK_CLIFF_ID,
            78,
            ry,
            footprint=1,
            clear_trees_around=False,
        )
        destructible_rocks["tumladen_exit_rocks"].append(r_obj.reference_id)

    # =========================================================================
    # 2. PHASE II & III STRUCTURES: TUMLADEN, ORFALCH ECHOR & CIRITH THORONATH
    # =========================================================================
    register_bldg("wolf_camp_1", PlayerId.FIVE, STABLE_ID, 132, 88, footprint=3)
    register_bldg("wolf_camp_2", PlayerId.FIVE, STABLE_ID, 156, 88, footprint=3)
    register_bldg("balrog_altar", PlayerId.SEVEN, KREPOST_ID, 145, 112, footprint=4)
    register_bldg("cliff_tower_1", PlayerId.FIVE, GUARD_TOWER_ID, 132, 62, footprint=2)
    register_bldg("cliff_tower_2", PlayerId.FIVE, GUARD_TOWER_ID, 156, 62, footprint=2)

    gate_coords: list[tuple[str, int, int]] = [
        ("orfalch_gate_1", 190, 94),   # 1. Wooden Gate
        ("orfalch_gate_2", 198, 108),  # 2. Stone Gate
        ("orfalch_gate_3", 206, 122),  # 3. Bronze Gate
        ("orfalch_gate_4", 208, 138),  # 4. Iron Gate
        ("orfalch_gate_5", 202, 150),  # 5. Silver Gate
        ("orfalch_gate_6", 196, 162),  # 6. Gold Gate
        ("orfalch_gate_7", 190, 174),  # 7. Steel Gate
    ]
    for g_key, gx, gy in gate_coords:
        for dx in range(-2, 3):
            r_obj = grid.place_unit_safe(
                um,
                PlayerId.GAIA,
                ROCK_CLIFF_ID,
                gx + dx,
                gy,
                footprint=1,
                clear_trees_around=False,
            )
            destructible_rocks[g_key].append(r_obj.reference_id)

    register_bldg("winch_bronze", PlayerId.FIVE, OUTPOST_ID, 188, 114, footprint=2)
    register_bldg("winch_silver", PlayerId.FIVE, OUTPOST_ID, 194, 144, footprint=2)
    register_bldg("winch_steel", PlayerId.SEVEN, KEEP_ID, 180, 172, footprint=2)

    for dy in range(-2, 3):
        r_obj = grid.place_unit_safe(
            um,
            PlayerId.GAIA,
            ROCK_CLIFF_ID,
            218,
            222 + dy,
            footprint=1,
            clear_trees_around=False,
        )
        destructible_rocks["cirith_exit_rocks"].append(r_obj.reference_id)

    # =========================================================================
    # 3. PROTECT TRIGGER & SPAWN SECTORS BEFORE BUILDING URBAN DISTRICTS
    # =========================================================================
    starts: dict[PlayerId, tuple[int, int]] = {
        PlayerId.ONE: (61, 24),
        PlayerId.TWO: (82, 58),
        PlayerId.THREE: (68, 92),
        PlayerId.FOUR: (28, 28),
    }
    for sx, sy in starts.values():
        grid.mark_road_box(sx - 6, sy - 4, sx + 6, sy + 8)

    # Protect refugee positions and Caragdur/Aqueduct combat arenas
    refugee_groups: list[dict[str, Any]] = [
        {
            "id": "ref_smiths",
            "name": "Czeladnicy Domu Mlota",
            "x": 32,
            "y": 74,
            "reward_player": PlayerId.ONE,
            "reward_unit": UNIT_HAMMER_SMITH_ID,
            "reward_count": 6,
        },
        {
            "id": "ref_fountain",
            "name": "Straznicy Wody z Polnocy",
            "x": 48,
            "y": 98,
            "reward_player": PlayerId.TWO,
            "reward_unit": UNIT_FOUNTAIN_GUARD_ID,
            "reward_count": 6,
        },
        {
            "id": "ref_archers",
            "name": "Lucznicy z Wielkiego Targu",
            "x": 96,
            "y": 78,
            "reward_player": PlayerId.TWO,
            "reward_unit": UNIT_ARCH_LONGBOW_ID,
            "reward_count": 6,
        },
        {
            "id": "ref_swallows",
            "name": "Zwiadowcy Domu Jaskolki",
            "x": 82,
            "y": 98,
            "reward_player": PlayerId.THREE,
            "reward_unit": UNIT_SWALLOW_SNIPER_ID,
            "reward_count": 6,
        },
        {
            "id": "ref_healers",
            "name": "Uzdrowiciele Domu Harfy",
            "x": 78,
            "y": 32,
            "reward_player": PlayerId.THREE,
            "reward_unit": UNIT_HARP_HEALER_ID,
            "reward_count": 3,
        },
        {
            "id": "ref_wrights",
            "name": "Inzynierowie Domu Drzewa",
            "x": 34,
            "y": 46,
            "reward_player": PlayerId.FOUR,
            "reward_unit": UNIT_TREE_PIKE_ID,
            "reward_count": 8,
        },
    ]
    for rg in refugee_groups:
        grid.mark_road_box(rg["x"] - 3, rg["y"] - 3, rg["x"] + 3, rg["y"] + 3)

    # Build Gondolin's walls, gatehouses, and 7 House urban districts
    _build_gondolin_walls_and_districts(grid, um, player_bldg_counts)

    # =========================================================================
    # 4. PLACE HEROES, RETINUES (P1-P4) & INITIAL GARRISONS FOR AI (P5-P8)
    # =========================================================================
    player_heroes: dict[PlayerId, list[int]] = {
        PlayerId.ONE: [HERO_TUOR_ID, HERO_ROG_ID],
        PlayerId.TWO: [HERO_ECTHELION_ID, HERO_EGALMOTH_ID],
        PlayerId.THREE: [HERO_GLORFINDEL_ID, HERO_DUILIN_ID],
        PlayerId.FOUR: [HERO_IDRIL_ID, HERO_GALDOR_ID, HERO_EARENDIL_ID],
    }

    retinues = get_retinue_configs()
    for p_id in HUMAN_PLAYERS:
        sx, sy = starts[p_id]
        for idx, h_id in enumerate(player_heroes[p_id]):
            grid.place_unit_safe(um, p_id, h_id, sx + idx * 2 - 1, sy, footprint=1)

        offset_idx = 0
        for unit_id, count in retinues[p_id]:
            for _ in range(count):
                dx = (offset_idx % 7) - 3
                dy = (offset_idx // 7) + 2
                grid.place_unit_safe(um, p_id, unit_id, sx + dx, sy + dy, footprint=1)
                offset_idx += 1

    # Place isolated Balance Sanctuary King for Player 1
    grid.place_unit_safe(um, PlayerId.ONE, SANCTUARY_KING_ID, 12, 228, footprint=1)
    grid.place_unit_safe(um, PlayerId.ONE, MAP_REVEALER_ID, 12, 228, footprint=1)
    grid.place_unit_safe(um, PlayerId.ONE, MAP_REVEALER_ID, 61, 63, footprint=1)
    player_bldg_counts[PlayerId.ONE] += 2

    # Place stranded Noldor citizen groups
    for rg in refugee_groups:
        for i in range(4):
            grid.place_unit_safe(
                um,
                PlayerId.GAIA,
                UNIT_REFUGEE_CIV_ID,
                rg["x"] + (i % 2),
                rg["y"] + (i // 2),
                footprint=1,
            )

    # CRITICAL P0 FIX: Ensure P5, P6, P7, and P8 all have active military buildings AND combat units at 0:00
    # so the Genie engine never marks any AI faction as Defeated on match start!
    # P5 (Angband Orc Horde): Northern Siege Camp & Vanguard at North Breach
    grid.place_unit_safe(um, PlayerId.FIVE, BARRACKS_ID, 52, 118, footprint=3)
    grid.place_unit_safe(um, PlayerId.FIVE, ARCHERY_RANGE_ID, 70, 118, footprint=3)
    for i in range(8):
        grid.place_unit_safe(
            um, PlayerId.FIVE, ENEMY_ORC_INFANTRY_ID, 58 + (i % 4), 104 + (i // 4), footprint=1
        )
    for i in range(4):
        grid.place_unit_safe(
            um, PlayerId.FIVE, ENEMY_ORC_ARCHER_ID, 131 + i, 64, footprint=1
        )
        grid.place_unit_safe(
            um, PlayerId.FIVE, ENEMY_ORC_ARCHER_ID, 155 + i, 64, footprint=1
        )

    # P6 (Iron Dragons & Siege Engines): Siege Workshops outside North & East Walls + Scorpion/Dragon vanguard
    grid.place_unit_safe(um, PlayerId.SIX, SIEGE_WORKSHOP_ID, 61, 119, footprint=4)
    grid.place_unit_safe(um, PlayerId.SIX, SIEGE_WORKSHOP_ID, 108, 63, footprint=4)
    grid.place_unit_safe(um, PlayerId.SIX, ENEMY_IRON_DRAGON_RAM_ID, 61, 115, footprint=1)
    grid.place_unit_safe(um, PlayerId.SIX, ENEMY_FIRE_DRAKE_ID, 59, 115, footprint=1)
    grid.place_unit_safe(um, PlayerId.SIX, ENEMY_HEAVY_SCORPION_ID, 63, 115, footprint=1)
    grid.place_unit_safe(um, PlayerId.SIX, ENEMY_IRON_DRAGON_RAM_ID, 105, 63, footprint=1)

    # P7 (Balrogs of Morgoth): Citadel of Flame in Northern Camp + Balrog Lieutenants at Altar & Steel Gate
    grid.place_unit_safe(um, PlayerId.SEVEN, CASTLE_ID, 145, 118, footprint=4)
    grid.place_unit_safe(um, PlayerId.SEVEN, ENEMY_BALROG_BOSS_ID, 145, 109, footprint=1)
    grid.place_unit_safe(um, PlayerId.SEVEN, ENEMY_BALROG_BOSS_ID, 184, 173, footprint=1)

    # P8 (Maeglin's House of the Mole Traitors): Traitor Barracks at Caragdur + Guards at Caragdur & Aqueduct
    grid.place_unit_safe(um, PlayerId.EIGHT, BARRACKS_ID, 19, 47, footprint=3)
    for i in range(4):
        grid.place_unit_safe(
            um, PlayerId.EIGHT, ENEMY_MOLE_TRAITOR_ID, 21 + i, 40, footprint=1
        )
        grid.place_unit_safe(
            um, PlayerId.EIGHT, ENEMY_MOLE_PIKE_ID, 82 + i, 71, footprint=1
        )

    # Populate dense forests and seal map edges
    _populate_forests_and_borders(grid, um)

    return {
        "grid": grid,
        "destructible_rocks": destructible_rocks,
        "quest_buildings": quest_buildings,
        "refugee_groups": refugee_groups,
        "starts": starts,
        "player_bldg_counts": player_bldg_counts,
        "sanctuary": {
            "x1": 5,
            "y1": 221,
            "x2": 19,
            "y2": 235,
            "cx": 12,
            "cy": 228,
            "harder_area": (8, 232, 16, 235),
            "easier_area": (8, 221, 16, 224),
        },
        "checkpoints": {
            "phase1": {
                PlayerId.ONE: (61, 51),
                PlayerId.TWO: (65, 58),
                PlayerId.THREE: (61, 66),
                PlayerId.FOUR: (56, 58),
            },
            "phase2": {
                PlayerId.ONE: (110, 86),
                PlayerId.TWO: (110, 40),
                PlayerId.THREE: (114, 86),
                PlayerId.FOUR: (114, 40),
            },
            "phase3": {
                PlayerId.ONE: (184, 84),
                PlayerId.TWO: (186, 84),
                PlayerId.THREE: (184, 88),
                PlayerId.FOUR: (186, 88),
            },
        },
        "sectors": {
            "caragdur_gate": (38, 20, 46, 32),
            "caragdur_cliff": (14, 36, 26, 48),
            "aqueduct_sluice": (78, 68, 90, 80),
            "north_fire_zone": (52, 90, 70, 104),
            "north_moat": (44, 110, 78, 118),
            "tower_of_snow": (70, 102, 78, 110),
            "enclave_forges": (18, 56, 34, 74),
            "enclave_market": (88, 56, 102, 72),
            "enclave_harp": (84, 18, 98, 34),
            "amon_gwareth": (46, 48, 76, 78),
            "royal_fountain": (55, 55, 67, 67),
            "idril_tunnel_entrance": (70, 48, 80, 56),
            "west_postern_gate": (70, 68, 80, 76),
            "lower_mine_1": (128, 36, 136, 44),
            "lower_mine_2": (152, 36, 160, 44),
            "upper_cliff_1": (128, 58, 136, 66),
            "upper_cliff_2": (152, 58, 160, 66),
            "rog_altar_zone": (138, 106, 152, 118),
            "orfalch_gathering": (178, 78, 192, 92),
            "winch_bronze_zone": (184, 110, 192, 118),
            "winch_silver_zone": (190, 140, 198, 148),
            "winch_steel_zone": (176, 168, 184, 176),
            "cirith_thoronath": (186, 176, 204, 218),
            "glorfindel_duel_ledge": (192, 193, 204, 203),
            "sirion_exit": (218, 216, 232, 230),
        },
        "dragon_corridors": {
            "north_avenue": [
                (55, 102, 67, 114),
                (55, 88, 67, 101),
                (55, 76, 67, 87),
            ],
            "east_avenue": [
                (92, 57, 104, 69),
                (78, 57, 91, 69),
            ],
        },
    }
