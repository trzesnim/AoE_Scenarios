"""Map generation, SafeMapGrid, elevation smoothing, Gondolin architecture, and entity placement."""

from __future__ import annotations

from typing import Any

from AoE2ScenarioParser.datasets.players import PlayerId
from AoE2ScenarioParser.datasets.terrains import TerrainId
from gondolin_config import (
    BLACKSMITH_ID,
    CASTLE_ID,
    CYPRESS_TREE_ID,
    FEITORIA_ID,
    FLAME_EFFECT_ID,
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
    HUMAN_PLAYERS,
    KEEP_ID,
    KREPOST_ID,
    MAP_REVEALER_ID,
    MAP_SIZE,
    MARKET_ID,
    MONASTERY_ID,
    OAK_TREE_ID,
    OUTPOST_ID,
    PAVILION_ID,
    PINE_TREE_ID,
    ROCK_CLIFF_ID,
    SANCTUARY_KING_ID,
    SIEGE_WORKSHOP_ID,
    STABLE_ID,
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
    """Anti-collision grid tracking occupied tiles, no-tree zones, and Lipschitz-smooth elevations."""

    def __init__(self, size: int = MAP_SIZE) -> None:
        self.size: int = size
        self.occupied_tiles: set[tuple[int, int]] = set()
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
    ) -> None:
        """Paint terrain texture and optional elevation inside a rectangle."""
        xmin, xmax = max(0, min(x1, x2)), min(self.size - 1, max(x1, x2))
        ymin, ymax = max(0, min(y1, y2)), min(self.size - 1, max(y1, y2))
        for y in range(ymin, ymax + 1):
            for x in range(xmin, xmax + 1):
                self.terrain[y][x] = terrain_id
                if elev is not None:
                    self.elevation[y][x] = max(0, min(7, elev))
                if protect_trees:
                    self.no_tree_zones.add((x, y))

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


def _sculpt_world_terrain(grid: SafeMapGrid) -> None:
    """Sculpt the 240x240 landscape: Gondolin, Tumladen, Underground Way, Orfalch Echor, and Cirith Thoronath."""
    # 1. Base highland forest & Encircling Mountains (Echoriath)
    grid.paint_box(0, 0, MAP_SIZE - 1, MAP_SIZE - 1, TerrainId.FOREST_PINE, elev=5)

    # 2. Plains of Tumladen (Central basin, misty grassland, elev=2..3)
    grid.paint_box(95, 70, 175, 165, TerrainId.GRASS_2, elev=3, protect_trees=False)
    grid.paint_box(105, 85, 165, 150, TerrainId.DIRT_3, elev=3, protect_trees=True)

    # 3. Gondolin City Basin & Terraces (SW quadrant: X=12..110, Y=12..120)
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
    grid.paint_circle(61, 63, 5, TerrainId.SHALLOWS, elev=6, protect_trees=True)

    # Water Reservoir & Aqueduct Channel in P2's Fountain District (X=76..96, Y=58..76)
    grid.paint_box(80, 62, 92, 72, TerrainId.WATER_AZURE, elev=4, protect_trees=True)
    grid.paint_corridor(76, 65, 65, 63, 2, TerrainId.SHALLOWS, elev=5, protect_trees=True)

    # Grand Avenues of Gondolin (minimum 5 tiles wide for smooth unit & Iron Dragon movement)
    # North Avenue (Great Gate -> Great Market -> Amon Gwareth)
    grid.paint_corridor(61, 118, 61, 76, 4, TerrainId.ROAD, elev=3, protect_trees=True)
    # South Avenue (South Gate -> Tuor's Quarter -> Amon Gwareth)
    grid.paint_corridor(61, 16, 61, 48, 4, TerrainId.ROAD, elev=3, protect_trees=True)
    # West Avenue (Forges of Rog -> Amon Gwareth)
    grid.paint_corridor(20, 63, 46, 63, 4, TerrainId.ROAD, elev=3, protect_trees=True)
    # East Avenue (East Gate -> Great Market -> Amon Gwareth)
    grid.paint_corridor(104, 63, 76, 63, 4, TerrainId.ROAD, elev=3, protect_trees=True)
    # SW Avenue (Caragdur & House of Tuor/Idril -> South Gate & Forges)
    grid.paint_corridor(26, 26, 61, 26, 3, TerrainId.ROAD, elev=2, protect_trees=True)
    grid.paint_corridor(26, 26, 26, 63, 3, TerrainId.ROAD, elev=2, protect_trees=True)
    # SE Avenue (Court of Salgant / House of the Harp)
    grid.paint_corridor(61, 26, 90, 26, 3, TerrainId.ROAD, elev=2, protect_trees=True)
    grid.paint_corridor(90, 26, 90, 63, 3, TerrainId.ROAD, elev=3, protect_trees=True)

    # 4. Phase II Dual Routes across Tumladen:
    # Route A (Lower): Secret Way of Idril (Underground Tunnel & Dry Riverbed, Y=35..55, X=105..175, elev=1)
    grid.paint_box(102, 22, 182, 58, TerrainId.FOREST_PINE, elev=5, protect_trees=False)
    grid.paint_corridor(72, 52, 112, 38, 3, TerrainId.ROAD_FUNGUS, elev=1, protect_trees=True)
    grid.paint_corridor(112, 38, 175, 42, 4, TerrainId.BEACH_ROCK, elev=1, protect_trees=True)
    grid.paint_corridor(175, 42, 185, 85, 4, TerrainId.DIRT_1, elev=2, protect_trees=True)

    # Route B (Upper): Misty Plains of Tumladen & Cliff Overlook (X=105..175, Y=65..125, elev=3)
    grid.paint_corridor(76, 72, 115, 88, 4, TerrainId.DIRT_2, elev=3, protect_trees=True)
    grid.paint_corridor(115, 88, 172, 88, 5, TerrainId.DIRT_2, elev=3, protect_trees=True)
    # Overlook ledges along Y=60..66 where Orc archers fire down toward the Dry Riverbed
    grid.paint_box(122, 58, 165, 68, TerrainId.GRAVEL, elev=4, protect_trees=True)
    # Connecting ramp between Upper Tumladen and Lower Dry Riverbed at the reunion point (X=178, Y=85)
    grid.paint_corridor(172, 88, 185, 85, 4, TerrainId.ROAD, elev=3, protect_trees=True)

    # 5. Phase III: Orfalch Echor (Gorge of Seven Gates) & Cirith Thoronath (NE Quadrant)
    # Winding gorge climbing from (185, 85) -> (215, 135) -> (190, 185) -> (220, 222)
    grid.paint_corridor(185, 85, 212, 130, 4, TerrainId.ROAD, elev=4, protect_trees=True)
    grid.paint_corridor(212, 130, 190, 175, 4, TerrainId.ROAD, elev=5, protect_trees=True)
    # High goat-paths flanking Orfalch Echor for P3/P4 vertical cooperation
    grid.paint_corridor(176, 92, 198, 132, 2, TerrainId.GRAVEL, elev=6, protect_trees=True)
    grid.paint_corridor(198, 132, 178, 175, 2, TerrainId.GRAVEL, elev=7, protect_trees=True)
    grid.paint_corridor(198, 132, 212, 130, 2, TerrainId.GRAVEL, elev=5, protect_trees=True)
    grid.paint_corridor(178, 175, 190, 175, 2, TerrainId.GRAVEL, elev=6, protect_trees=True)

    # Cirith Thoronath (Eagle's Cleft) - narrow precipice above a deep chasm (X=190..225, Y=175..225)
    # Deep abyss next to the ledge (elev=0, dark water/ice below)
    grid.paint_box(196, 178, 232, 215, TerrainId.WATER_DEEP, elev=0, protect_trees=True)
    # Narrow mountain ledge (elev=7)
    grid.paint_corridor(190, 175, 190, 218, 3, TerrainId.SNOW_ROAD, elev=7, protect_trees=True)
    grid.paint_corridor(190, 218, 224, 224, 4, TerrainId.SNOW_ROAD, elev=6, protect_trees=True)
    # Glorfindel's Duel Spur jutting out over the abyss at (198, 198)
    grid.paint_box(193, 194, 203, 202, TerrainId.GRAVEL, elev=7, protect_trees=True)

    # 6. Balance Sanctuary chamber isolated in NW corner (X=6..18, Y=222..234)
    grid.paint_box(4, 220, 20, 236, TerrainId.ROAD, elev=4, protect_trees=True)

    # Apply two-pass Lipschitz smoothing so all elevation transitions are valid
    grid.smooth_elevations_lipschitz()


def _populate_forests_and_borders(grid: SafeMapGrid, um: Any) -> None:
    """Populate physical tree objects across 0..MAP_SIZE-1 and seal the Balance Sanctuary."""
    for y in range(MAP_SIZE):
        for x in range(MAP_SIZE):
            if (x, y) in grid.occupied_tiles or (x, y) in grid.no_tree_zones:
                continue
            # Seal outer map border (0 and MAP_SIZE-1) unless part of Sirion exit
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
            grid.place_unit_safe(um, PlayerId.GAIA, ROCK_CLIFF_ID, x, y, clear_trees_around=False)
    for y in range(221, 236):
        for x in (4, 20):
            grid.place_unit_safe(um, PlayerId.GAIA, ROCK_CLIFF_ID, x, y, clear_trees_around=False)


def build_map_and_entities(scenario: Any) -> dict[str, Any]:
    """Build the 240x240 Gondolin map, place initial structures/units, and return context dict."""
    mm = scenario.map_manager
    um = scenario.unit_manager
    pm = scenario.player_manager

    mm.map_size = MAP_SIZE
    pm.active_players = 8

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
        return obj

    # =========================================================================
    # 1. KEY LANDMARKS & QUEST STRUCTURES IN GONDOLIN
    # =========================================================================
    # Amon Gwareth (Central Royal Square)
    register_bldg("tower_of_turgon", PlayerId.ONE, FEITORIA_ID, 61, 70, footprint=5)
    register_bldg("royal_fountain_bldg", PlayerId.TWO, MONASTERY_ID, 61, 58, footprint=3)

    # Ornamental cypress trees & torches on Amon Gwareth
    for ox, oy in [(53, 55), (69, 55), (53, 68), (69, 68)]:
        grid.place_unit_safe(um, PlayerId.GAIA, CYPRESS_TREE_ID, ox, oy, footprint=1)
        grid.place_unit_safe(um, PlayerId.GAIA, TORCH_ID, ox + 1, oy, footprint=1)

    # Sacred Trees Glingal (Gold) & Belthil (Silver) for P4 Idril side quest
    register_bldg("glingal_tree", PlayerId.FOUR, PAVILION_ID, 55, 63, footprint=2)
    register_bldg("belthil_tree", PlayerId.FOUR, PAVILION_ID, 67, 63, footprint=2)

    # Path A (West): Forges of Rog & Royal Armory
    register_bldg("great_forge", PlayerId.ONE, BLACKSMITH_ID, 24, 63, footprint=3)
    register_bldg("forge_workshop", PlayerId.ONE, SIEGE_WORKSHOP_ID, 24, 70, footprint=4)
    # 3 Mithril Supply Carts waiting at the Great Forge
    for cy_off in (59, 63, 67):
        grid.place_unit_safe(um, PlayerId.ONE, UNIT_REFUGEE_CART_ID, 29, cy_off, footprint=1)

    # Path B (East): Great Market of Penlod & Fountain Aqueduct
    register_bldg("great_market", PlayerId.TWO, MARKET_ID, 94, 63, footprint=4)
    register_bldg("aqueduct_control", PlayerId.EIGHT, UNIVERSITY_ID, 84, 74, footprint=4)

    # North Quarter: Tower of Snow (P3 Duilin high vantage point)
    register_bldg("snow_watchtower", PlayerId.THREE, KEEP_ID, 74, 106, footprint=2)

    # Path C (South-East): Court of Salgant (House of the Harp)
    register_bldg("salgant_manor", PlayerId.THREE, CASTLE_ID, 92, 26, footprint=4)
    # Blockade locking the House of the Harp inside Salgant's courtyard
    for bx in range(86, 95, 2):
        r_obj = grid.place_unit_safe(
            um, PlayerId.GAIA, ROCK_CLIFF_ID, bx, 33, footprint=1, clear_trees_around=False
        )
        destructible_rocks["salgant_gate_rocks"].append(r_obj.reference_id)
    # Trapped House of the Harp healers inside Salgant's court
    for hx in (89, 91, 93):
        grid.place_unit_safe(um, PlayerId.THREE, UNIT_HARP_HEALER_ID, hx, 22, footprint=1)

    # SW Quarter: House of Tuor & Caragdur Precipice (P4 cut off by P8 Maeglin's Traitors)
    register_bldg("house_of_tuor", PlayerId.FOUR, KREPOST_ID, 24, 24, footprint=4)
    register_bldg("caragdur_keep", PlayerId.EIGHT, KEEP_ID, 18, 42, footprint=2)
    # Internal blockade separating P1 (South Gate: 61, 24) from P4 (Caragdur: 24, 24)
    for by in range(22, 31):
        r_obj = grid.place_unit_safe(
            um, PlayerId.GAIA, ROCK_CLIFF_ID, 42, by, footprint=1, clear_trees_around=False
        )
        destructible_rocks["caragdur_blockade"].append(r_obj.reference_id)

    # North Quarter Fire Hazard (hurts P3 until P2 captures aqueduct_control)
    for fx in range(55, 68, 3):
        for fy in (94, 100):
            f_obj = grid.place_unit_safe(
                um, PlayerId.GAIA, FLAME_EFFECT_ID, fx, fy, footprint=1, clear_trees_around=False
            )
            destructible_rocks["north_fire_objects"].append(f_obj.reference_id)

    # Rocks blocking the Northern Moat shallows (removed when P2 floods the moat)
    for rx in range(48, 75, 3):
        r_obj = grid.place_unit_safe(
            um, PlayerId.GAIA, ROCK_CLIFF_ID, rx, 114, footprint=1, clear_trees_around=False
        )
        destructible_rocks["aqueduct_dry_rocks"].append(r_obj.reference_id)

    # Gondolin City Walls & Towers (Visual grandeur around the city perimeter)
    for wx in range(18, 103, 6):
        if abs(wx - 61) > 6:
            grid.place_unit_safe(um, PlayerId.ONE, GUARD_TOWER_ID, wx, 18, footprint=2)
            grid.place_unit_safe(um, PlayerId.THREE, GUARD_TOWER_ID, wx, 110, footprint=2)
    for wy in range(24, 106, 6):
        if abs(wy - 63) > 6:
            grid.place_unit_safe(um, PlayerId.ONE, GUARD_TOWER_ID, 18, wy, footprint=2)
            grid.place_unit_safe(um, PlayerId.TWO, GUARD_TOWER_ID, 102, wy, footprint=2)

    # Phase II Exit Gates (Sealed until Phase I defence of Amon Gwareth concludes)
    register_bldg("idril_waygate", PlayerId.FOUR, OUTPOST_ID, 74, 52, footprint=2)
    for ry in range(49, 56):
        r_obj = grid.place_unit_safe(
            um, PlayerId.GAIA, ROCK_CLIFF_ID, 78, ry, footprint=1, clear_trees_around=False
        )
        destructible_rocks["tumladen_exit_rocks"].append(r_obj.reference_id)
    for ry in range(69, 76):
        r_obj = grid.place_unit_safe(
            um, PlayerId.GAIA, ROCK_CLIFF_ID, 78, ry, footprint=1, clear_trees_around=False
        )
        destructible_rocks["tumladen_exit_rocks"].append(r_obj.reference_id)

    # =========================================================================
    # 2. PHASE II STRUCTURES: TUMLADEN & UNDERGROUND WAY
    # =========================================================================
    # Upper Tumladen wolf camps & Balrog Altar (for Rog's Wrath Quest)
    register_bldg("wolf_camp_1", PlayerId.FIVE, STABLE_ID, 132, 88, footprint=3)
    register_bldg("wolf_camp_2", PlayerId.FIVE, STABLE_ID, 156, 88, footprint=3)
    register_bldg("balrog_altar", PlayerId.SEVEN, KREPOST_ID, 145, 112, footprint=4)
    # Cliff archer watchtowers firing toward the Dry Riverbed
    register_bldg("cliff_tower_1", PlayerId.FIVE, GUARD_TOWER_ID, 132, 62, footprint=2)
    register_bldg("cliff_tower_2", PlayerId.FIVE, GUARD_TOWER_ID, 156, 62, footprint=2)

    # =========================================================================
    # 3. PHASE III STRUCTURES: SEVEN GATES OF ORFALCH ECHOR & CIRITH THORONATH
    # =========================================================================
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
                um, PlayerId.GAIA, ROCK_CLIFF_ID, gx + dx, gy, footprint=1, clear_trees_around=False
            )
            destructible_rocks[g_key].append(r_obj.reference_id)

    # High-ridge winches controlled by P3/P4 to open the toughest gates & trigger rockfalls
    register_bldg("winch_bronze", PlayerId.FIVE, OUTPOST_ID, 188, 114, footprint=2)
    register_bldg("winch_silver", PlayerId.FIVE, OUTPOST_ID, 194, 144, footprint=2)
    register_bldg("winch_steel", PlayerId.SEVEN, KEEP_ID, 180, 172, footprint=2)

    # Final blockade at Cirith Thoronath exit (opens when Balrog of the Pass is defeated)
    for dy in range(-2, 3):
        r_obj = grid.place_unit_safe(
            um, PlayerId.GAIA, ROCK_CLIFF_ID, 218, 222 + dy, footprint=1, clear_trees_around=False
        )
        destructible_rocks["cirith_exit_rocks"].append(r_obj.reference_id)

    # =========================================================================
    # 4. PLACE HEROES & STARTING RETINUES (SCATTERED START IN 4 DISTRICTS)
    # =========================================================================
    starts: dict[PlayerId, tuple[int, int]] = {
        PlayerId.ONE: (61, 24),    # South Gate & Avenue (Tuor & Rog)
        PlayerId.TWO: (82, 58),    # Fountain Terrace (Ecthelion & Egalmoth)
        PlayerId.THREE: (68, 92),  # North-East Market Approach (Glorfindel & Duilin)
        PlayerId.FOUR: (28, 28),   # SW Quarter / House of Tuor (Idril, Galdor & Earendil)
    }

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

    # Progressive Vision at 0:00: ONLY reveal Amon Gwareth & starting districts (NOT the whole map!)
    grid.place_unit_safe(um, PlayerId.ONE, MAP_REVEALER_ID, 61, 63, footprint=1)

    # =========================================================================
    # 5. STRANDED NOLDOR REFUGEE / ARTISAN GROUPS IN GONDOLIN
    # =========================================================================
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
        for i in range(4):
            grid.place_unit_safe(
                um,
                PlayerId.GAIA,
                UNIT_REFUGEE_CIV_ID,
                rg["x"] + (i % 2),
                rg["y"] + (i // 2),
                footprint=1,
            )

    # Populate dense forests and seal map edges
    _populate_forests_and_borders(grid, um)

    # Build context dictionary for mechanics and quests modules
    return {
        "grid": grid,
        "destructible_rocks": destructible_rocks,
        "quest_buildings": quest_buildings,
        "refugee_groups": refugee_groups,
        "starts": starts,
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
                PlayerId.ONE: (61, 54),
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