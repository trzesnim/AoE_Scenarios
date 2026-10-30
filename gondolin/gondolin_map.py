"""Map generation, strict SafeMapGrid, Gondolin urban architecture, and entity placement (Stage B-II)."""

from __future__ import annotations

from typing import Any

from AoE2ScenarioParser.datasets.players import PlayerId
from AoE2ScenarioParser.datasets.terrains import TerrainId
from gondolin_config import (
    ARCHERY_RANGE_ID,
    BARRACKS_ID,
    BLACKSMITH_ID,
    CASTLE_ID,
    CYPRESS_TREE_ID,
    ENEMY_BALROG_BOSS_ID,
    ENEMY_FIRE_DRAKE_ID,
    ENEMY_HEAVY_SCORPION_ID,
    ENEMY_IRON_DRAGON_RAM_ID,
    ENEMY_MOLE_PIKE_ID,
    ENEMY_MOLE_TRAITOR_ID,
    ENEMY_ORC_ARCHER_ID,
    ENEMY_ORC_INFANTRY_ID,
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
    MAP_REVEALER_ID,
    MAP_SIZE,
    MARKET_ID,
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


def footprint_bounds(x: int, y: int, footprint: int) -> tuple[int, int, int, int]:
    """Return exact (xmin, ymin, xmax, ymax) tile bounds for both even and odd footprints."""
    xmin = x - (footprint - 1) // 2
    ymin = y - (footprint - 1) // 2
    xmax = xmin + footprint - 1
    ymax = ymin + footprint - 1
    return xmin, ymin, xmax, ymax


class SafeMapGrid:
    """Strict anti-collision grid tracking occupied tiles, road corridors, and Lipschitz elevations."""

    def __init__(self, size: int = MAP_SIZE) -> None:
        self.size: int = size
        self.occupied_tiles: set[tuple[int, int]] = set()
        self.road_corridors: set[tuple[int, int]] = set()
        self.no_tree_zones: set[tuple[int, int]] = set()
        self.failed_placements: list[dict[str, Any]] = []
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
        for ty in range(ymin, ymax + 1):
            for tx in range(xmin, xmax + 1):
                self.no_tree_zones.add((tx, ty))

    def mark_road_box(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """Reserve a passable street/avenue box where city buildings must not be placed."""
        xmin, xmax = max(0, min(x1, x2)), min(self.size - 1, max(x1, x2))
        ymin, ymax = max(0, min(y1, y2)), min(self.size - 1, max(y1, y2))
        for ty in range(ymin, ymax + 1):
            for tx in range(xmin, xmax + 1):
                self.road_corridors.add((tx, ty))
                self.no_tree_zones.add((tx, ty))

    def can_place_footprint(
        self,
        x: int,
        y: int,
        footprint: int = 1,
        respect_roads: bool = True,
    ) -> bool:
        """Return True if the exact footprint around (x, y) is free of occupied tiles and road corridors."""
        xmin, ymin, xmax, ymax = footprint_bounds(x, y, footprint)
        for ty in range(ymin, ymax + 1):
            for tx in range(xmin, xmax + 1):
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
        """Mark tiles in [x1..x2, y1..y2] as occupied."""
        xmin, xmax = max(0, min(x1, x2)), min(self.size - 1, max(x1, x2))
        ymin, ymax = max(0, min(y1, y2)), min(self.size - 1, max(y1, y2))
        for ty in range(ymin, ymax + 1):
            for tx in range(xmin, xmax + 1):
                self.occupied_tiles.add((tx, ty))
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
        for ty in range(ymin, ymax + 1):
            for tx in range(xmin, xmax + 1):
                self.terrain[ty][tx] = terrain_id
                if elev is not None:
                    self.elevation[ty][tx] = max(0, min(7, elev))
                if protect_trees or is_road:
                    self.no_tree_zones.add((tx, ty))
                elif (tx, ty) not in self.road_corridors:
                    self.no_tree_zones.discard((tx, ty))
                if is_road:
                    self.road_corridors.add((tx, ty))

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
        for ty in range(max(0, cy - radius), min(self.size, cy + radius + 1)):
            for tx in range(max(0, cx - radius), min(self.size, cx + radius + 1)):
                if (tx - cx) ** 2 + (ty - cy) ** 2 <= r2:
                    self.terrain[ty][tx] = terrain_id
                    if elev is not None:
                        self.elevation[ty][tx] = max(0, min(7, elev))
                    if protect_trees:
                        self.no_tree_zones.add((tx, ty))

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
        """Enforce two-pass Lipschitz smoothing (|dh| <= 1 between adjacent tiles)."""
        for _ in range(2):
            for ty in range(self.size):
                for tx in range(self.size):
                    if tx > 0:
                        self.elevation[ty][tx] = min(
                            self.elevation[ty][tx], self.elevation[ty][tx - 1] + 1
                        )
                    if ty > 0:
                        self.elevation[ty][tx] = min(
                            self.elevation[ty][tx], self.elevation[ty - 1][tx] + 1
                        )
            for ty in range(self.size - 1, -1, -1):
                for tx in range(self.size - 1, -1, -1):
                    if tx < self.size - 1:
                        self.elevation[ty][tx] = min(
                            self.elevation[ty][tx], self.elevation[ty][tx + 1] + 1
                        )
                    if ty < self.size - 1:
                        self.elevation[ty][tx] = min(
                            self.elevation[ty][tx], self.elevation[ty + 1][tx] + 1
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
        respect_roads: bool = False,
        strict: bool = True,
        allow_overlap: bool = False,
    ) -> Any:
        """Place a unit or building with exact even/odd footprint bounds and strict collision checking."""
        xmin, ymin, xmax, ymax = footprint_bounds(x, y, footprint)
        if not allow_overlap and not self.can_place_footprint(
            x, y, footprint=footprint, respect_roads=respect_roads
        ):
            failure = {
                "player": player,
                "unit_id": unit_id,
                "x": x,
                "y": y,
                "footprint": footprint,
                "respect_roads": respect_roads,
            }
            self.failed_placements.append(failure)
            if strict:
                msg = f"[KOLIZJA SIATKI] Nie mozna postawic unit_id={unit_id} (fp={footprint}) w ({x}, {y})!"
                raise ValueError(msg)
            return None

        self.mark_occupied_box(xmin, ymin, xmax, ymax, clear_trees_around=clear_trees_around)
        ux = (xmin + xmax + 1) / 2.0
        uy = (ymin + ymax + 1) / 2.0
        return um.add_unit(player=player, unit_const=unit_id, x=ux, y=uy)


def _configure_players_and_diplomacy(pm: Any) -> None:
    """Configure P1-P4 (unified Western European Noldor architecture) and P5-P8 (Morgoth AI) with official diplomacy."""
    pm.active_players = 8

    # Official Genie Civilization IDs:
    # P1-P4 share West European gothic stone architecture (Britons=1, Franks=2, Burgundians=33) for visual cohesion!
    civ_map: dict[int, tuple[int, int]] = {
        1: (1, 1),   # Britons / West European stone architecture
        2: (1, 1),   # Britons / West European stone architecture
        3: (2, 1),   # Franks / West European stone architecture
        4: (33, 1),  # Burgundians / West European stone architecture
        5: (3, 2),   # Goths (Angband Orc Horde)
        6: (35, 3),  # Bohemians (Iron Dragons)
        7: (8, 4),   # Persians / Eastern (Balrogs)
        8: (4, 2),   # Teutons (Maeglin's Traitors)
    }

    noldor_team = [PlayerId.ONE, PlayerId.TWO, PlayerId.THREE, PlayerId.FOUR]
    morgoth_team = [PlayerId.FIVE, PlayerId.SIX, PlayerId.SEVEN, PlayerId.EIGHT]

    # Use official PlayerManager diplomacy API if available
    set_teams_fn = getattr(pm, "set_diplomacy_teams", None)
    if callable(set_teams_fn):
        set_teams_fn(noldor_team, morgoth_team)

    players = getattr(pm, "players", [])
    for idx in range(1, min(9, len(players))):
        p_obj = players[idx]
        if p_obj is None:
            continue
        is_human = idx <= 4
        civ_id, arch_id = civ_map.get(idx, (1, 1))
        for attr_name, val in [
            ("human", is_human),
            ("civilization", civ_id),
            ("architecture_set", arch_id),
            ("food", 0),
            ("wood", 0),
            ("stone", 0),
            ("gold", 0),
        ]:
            if hasattr(p_obj, attr_name) and not isinstance(
                getattr(type(p_obj), attr_name, None), property
            ):
                setattr(p_obj, attr_name, val)
            elif hasattr(p_obj, attr_name):
                prop = getattr(type(p_obj), attr_name, None)
                if prop is not None and prop.fset is not None:
                    setattr(p_obj, attr_name, val)

        # Official per-player diplomacy method (0=Ally, 3=Enemy) or 0-indexed diplomacy array
        set_dip_fn = getattr(p_obj, "set_player_diplomacy", None)
        for other_idx in range(1, 9):
            if other_idx == idx:
                continue
            same_team = (idx <= 4 and other_idx <= 4) or (idx >= 5 and other_idx >= 5)
            state_val = 0 if same_team else 3
            if callable(set_dip_fn):
                set_dip_fn(PlayerId(other_idx), state_val)
            else:
                dip = getattr(p_obj, "diplomacy", None)
                if isinstance(dip, list):
                    if len(dip) == 8:
                        dip[other_idx - 1] = state_val
                    elif len(dip) >= 9:
                        dip[other_idx] = state_val


def _sculpt_world_terrain(grid: SafeMapGrid) -> None:
    """Sculpt the 240x240 landscape: Echoriath Mountains, open green Tumladen Valley, and terraced Gondolin."""
    # 1. Encircling Mountains (Echoriath): rocky alpine peaks (DIRT_3) + solid forested gorges in the East
    grid.paint_box(0, 0, MAP_SIZE - 1, MAP_SIZE - 1, TerrainId.DIRT_3, elev=6, protect_trees=False)
    grid.paint_box(174, 0, MAP_SIZE - 1, MAP_SIZE - 1, TerrainId.FOREST_PINE, elev=6, protect_trees=False)

    # 2. Open, green Hidden Valley of Tumladen (X=10..178, Y=10..168, elev=2..3)
    grid.paint_box(10, 10, 178, 168, TerrainId.GRASS_1, elev=2, protect_trees=True)
    grid.paint_box(96, 66, 175, 155, TerrainId.GRASS_2, elev=3, protect_trees=True)
    # Forested ridge separating Lower Route (Dry Riverbed Y=34..46) from Upper Route (Tumladen Plains Y=60..96)
    grid.paint_box(104, 48, 176, 57, TerrainId.FOREST_PINE, elev=5, protect_trees=False)
    # Natural pine wooded ridges along the northern and southern edges of Tumladen
    grid.paint_box(106, 134, 172, 154, TerrainId.FOREST_PINE, elev=4, protect_trees=False)
    grid.paint_box(106, 16, 174, 28, TerrainId.FOREST_PINE, elev=4, protect_trees=False)

    # 3. Gondolin City Terraces & Amon Gwareth (X=16..104, Y=16..114)
    grid.paint_box(16, 16, 104, 114, TerrainId.GRASS_2, elev=2, protect_trees=True)
    # Northern Moat (Shallows = 4, initially blocked by rocks until P2 opens the Aqueduct)
    grid.paint_box(22, 112, 98, 116, TerrainId.SHALLOWS, elev=1, protect_trees=True)

    # Middle City Terrace: clean white/grey stone paving & green courtyards (NO global ROAD_BROKEN!)
    grid.paint_box(28, 28, 92, 96, TerrainId.ROAD, elev=4, protect_trees=True)
    grid.paint_box(34, 34, 52, 46, TerrainId.GRASS_2, elev=4, protect_trees=True)
    grid.paint_box(68, 34, 86, 46, TerrainId.GRASS_2, elev=4, protect_trees=True)

    # Localized Siege Damage (ROAD_BROKEN only at the Northern & Eastern Breaches)
    grid.paint_box(52, 94, 70, 112, TerrainId.ROAD_BROKEN, elev=3, protect_trees=True)
    grid.paint_box(78, 102, 88, 112, TerrainId.ROAD_BROKEN, elev=3, protect_trees=True)
    grid.paint_box(96, 56, 105, 70, TerrainId.ROAD_BROKEN, elev=3, protect_trees=True)

    # Amon Gwareth - Royal Hill at the heart of Gondolin (X=46..76, Y=48..78, elev=6..7)
    grid.paint_box(46, 48, 76, 78, TerrainId.ROAD, elev=6, protect_trees=True)
    grid.paint_box(52, 66, 70, 76, TerrainId.ROAD, elev=7, protect_trees=True)
    # Royal Fountain water basin in the center of Amon Gwareth (61, 61)
    grid.paint_circle(61, 61, 5, TerrainId.SHALLOWS, elev=6, protect_trees=True)
    grid.paint_circle(61, 61, 2, TerrainId.WATER_AZURE, elev=6, protect_trees=True)

    # Water Reservoir & Aqueduct Channel in P2's Fountain District
    grid.paint_box(80, 66, 90, 71, TerrainId.WATER_AZURE, elev=4, protect_trees=True)
    grid.paint_corridor(76, 64, 65, 62, 2, TerrainId.SHALLOWS, elev=5, protect_trees=True, is_road=True)

    # Grand Avenues of Gondolin (marked as road_corridors so city blocks never obstruct movement)
    grid.paint_corridor(61, 118, 61, 76, 4, TerrainId.ROAD, elev=3, protect_trees=True, is_road=True)
    grid.paint_corridor(61, 16, 61, 48, 4, TerrainId.ROAD, elev=3, protect_trees=True, is_road=True)
    grid.paint_corridor(16, 63, 46, 63, 3, TerrainId.ROAD, elev=3, protect_trees=True, is_road=True)
    grid.paint_corridor(104, 63, 76, 63, 4, TerrainId.ROAD, elev=3, protect_trees=True, is_road=True)
    grid.paint_corridor(24, 26, 61, 26, 3, TerrainId.ROAD, elev=2, protect_trees=True, is_road=True)
    grid.paint_corridor(26, 26, 26, 63, 3, TerrainId.ROAD, elev=2, protect_trees=True, is_road=True)
    grid.paint_corridor(61, 26, 90, 26, 3, TerrainId.ROAD, elev=2, protect_trees=True, is_road=True)
    grid.paint_corridor(90, 26, 90, 63, 3, TerrainId.ROAD, elev=3, protect_trees=True, is_road=True)
    grid.paint_corridor(34, 63, 34, 98, 2, TerrainId.ROAD, elev=3, protect_trees=True, is_road=True)
    grid.paint_corridor(34, 96, 86, 96, 2, TerrainId.ROAD, elev=3, protect_trees=True, is_road=True)
    grid.paint_corridor(82, 63, 82, 98, 2, TerrainId.ROAD, elev=3, protect_trees=True, is_road=True)

    # 4. Phase II Dual Routes across Tumladen:
    # Route A (Lower): Secret Way of Idril (Underground Tunnel & Dry Riverbed, Y=36..46, X=74..185)
    grid.paint_corridor(72, 52, 106, 52, 3, TerrainId.ROAD_FUNGUS, elev=1, protect_trees=True, is_road=True)
    grid.paint_corridor(106, 52, 112, 38, 3, TerrainId.ROAD_FUNGUS, elev=1, protect_trees=True, is_road=True)
    grid.paint_corridor(112, 38, 175, 42, 4, TerrainId.ROAD_BROKEN, elev=1, protect_trees=True, is_road=True)
    grid.paint_corridor(175, 42, 185, 85, 4, TerrainId.DIRT_1, elev=2, protect_trees=True, is_road=True)

    # Route B (Upper): Plains of Tumladen & Cliff Overlook (X=76..185, Y=60..92)
    grid.paint_corridor(76, 72, 106, 65, 3, TerrainId.DIRT_2, elev=3, protect_trees=True, is_road=True)
    grid.paint_corridor(106, 65, 115, 88, 4, TerrainId.DIRT_2, elev=3, protect_trees=True, is_road=True)
    grid.paint_corridor(115, 88, 172, 88, 5, TerrainId.DIRT_2, elev=3, protect_trees=True, is_road=True)
    grid.paint_box(122, 58, 165, 68, TerrainId.DIRT_3, elev=4, protect_trees=True)
    grid.paint_corridor(172, 88, 185, 85, 4, TerrainId.ROAD, elev=3, protect_trees=True, is_road=True)

    # 5. Phase III: Orfalch Echor (Gorge of Seven Gates) & Cirith Thoronath
    grid.paint_corridor(185, 85, 212, 130, 4, TerrainId.ROAD, elev=4, protect_trees=True, is_road=True)
    grid.paint_corridor(212, 130, 190, 175, 4, TerrainId.ROAD, elev=5, protect_trees=True, is_road=True)
    grid.paint_corridor(176, 92, 198, 132, 2, TerrainId.DIRT_3, elev=6, protect_trees=True, is_road=True)
    grid.paint_corridor(198, 132, 178, 175, 2, TerrainId.DIRT_3, elev=7, protect_trees=True, is_road=True)
    grid.paint_corridor(198, 132, 212, 130, 2, TerrainId.DIRT_3, elev=5, protect_trees=True, is_road=True)
    grid.paint_corridor(178, 175, 190, 175, 2, TerrainId.DIRT_3, elev=6, protect_trees=True, is_road=True)

    # Cirith Thoronath (Eagle's Cleft) & Vale of Sirion exit
    grid.paint_box(196, 178, 232, 215, TerrainId.WATER_AZURE, elev=0, protect_trees=True)
    grid.paint_corridor(190, 175, 190, 218, 3, TerrainId.ROAD, elev=7, protect_trees=True, is_road=True)
    grid.paint_corridor(190, 218, 226, 224, 4, TerrainId.ROAD, elev=6, protect_trees=True, is_road=True)
    grid.paint_box(193, 194, 203, 202, TerrainId.ROAD, elev=7, protect_trees=True, is_road=True)

    # 6. Balance Sanctuary & Phase Marker strip in NW corner
    grid.paint_box(1, 220, 20, 236, TerrainId.ROAD, elev=4, protect_trees=True, is_road=True)

    grid.smooth_elevations_lipschitz()


def _build_gondolin_walls_and_districts(
    grid: SafeMapGrid,
    um: Any,
    bldg_counter: dict[PlayerId, int],
) -> int:
    """Construct Gondolin's fortifications (towers first, then walls) and 7 House districts with 0 collisions."""
    placed_buildings = 0

    def place_bldg(
        player: PlayerId,
        unit_id: int,
        x: int,
        y: int,
        footprint: int = 3,
        respect_roads: bool = True,
    ) -> None:
        nonlocal placed_buildings
        grid.place_unit_safe(
            um, player, unit_id, x, y, footprint=footprint, respect_roads=respect_roads, strict=True
        )
        if player in bldg_counter:
            bldg_counter[player] += 1
        placed_buildings += 1

    # =========================================================================
    # A. TOWERS & GATEHOUSE BASTIONS FIRST (2x2 footprint: [x..x+1, y..y+1])
    # =========================================================================
    # Gatehouse Bastions flanking the 4 Grand Gates (leaving 4-tile openings: X=59..62, Y=61..64)
    gate_bastions: list[tuple[PlayerId, int, int]] = [
        (PlayerId.ONE, 57, 16), (PlayerId.ONE, 63, 16),      # South Grand Gate (opening X=59..62)
        (PlayerId.THREE, 53, 110), (PlayerId.THREE, 68, 110),# North Breach Bastions (opening X=55..67)
        (PlayerId.FOUR, 16, 59), (PlayerId.FOUR, 16, 65),    # West Forge Gate (opening Y=61..64)
        (PlayerId.TWO, 103, 55), (PlayerId.TWO, 103, 70),    # East Breach Bastions (opening Y=57..69)
    ]
    for p_id, gx, gy in gate_bastions:
        place_bldg(p_id, KEEP_ID, gx, gy, footprint=2, respect_roads=False)

    # Outer Perimeter Guard Towers (2x2) placed cleanly every 10 tiles along the wall line
    for tx in (16, 26, 36, 46, 72, 88, 96, 103):
        place_bldg(PlayerId.ONE, GUARD_TOWER_ID, tx, 16, footprint=2, respect_roads=False)
    for tx in (16, 26, 36, 46, 74, 90, 98, 103):
        place_bldg(PlayerId.THREE, GUARD_TOWER_ID, tx, 110, footprint=2, respect_roads=False)
    for ty in (26, 36, 48, 74, 86, 98):
        place_bldg(PlayerId.FOUR, GUARD_TOWER_ID, 16, ty, footprint=2, respect_roads=False)
    for ty in (26, 36, 46, 78, 90, 100):
        place_bldg(PlayerId.TWO, GUARD_TOWER_ID, 103, ty, footprint=2, respect_roads=False)

    # Inner Citadel Corner Keeps (2x2) on Amon Gwareth
    for kx, ky in [(46, 48), (75, 48), (46, 77), (75, 77)]:
        place_bldg(PlayerId.ONE, KEEP_ID, kx, ky, footprint=2, respect_roads=False)

    # =========================================================================
    # B. CONTINUOUS STONE WALL SEGMENTS FILLING GAPS BETWEEN TOWERS (1x1)
    # =========================================================================
    for wx in range(16, 105):
        if not (59 <= wx <= 62) and grid.can_place_footprint(wx, 16, footprint=1, respect_roads=False):
            place_bldg(PlayerId.ONE, FORTIFIED_WALL_ID, wx, 16, footprint=1, respect_roads=False)
        if not (55 <= wx <= 67 or 80 <= wx <= 86) and grid.can_place_footprint(wx, 111, footprint=1, respect_roads=False):
            place_bldg(PlayerId.THREE, FORTIFIED_WALL_ID, wx, 111, footprint=1, respect_roads=False)

    for wy in range(16, 112):
        if not (61 <= wy <= 64) and grid.can_place_footprint(16, wy, footprint=1, respect_roads=False):
            place_bldg(PlayerId.FOUR, FORTIFIED_WALL_ID, 16, wy, footprint=1, respect_roads=False)
        if not (50 <= wy <= 54 or 57 <= wy <= 69) and grid.can_place_footprint(104, wy, footprint=1, respect_roads=False):
            place_bldg(PlayerId.TWO, FORTIFIED_WALL_ID, 104, wy, footprint=1, respect_roads=False)

    # Inner Citadel Ring Wall around Amon Gwareth (4-tile openings at N/S X=59..62 and W/E Y=61..64)
    for cx in range(46, 77):
        if not (59 <= cx <= 62):
            if grid.can_place_footprint(cx, 48, footprint=1, respect_roads=False):
                place_bldg(PlayerId.ONE, FORTIFIED_WALL_ID, cx, 48, footprint=1, respect_roads=False)
            if grid.can_place_footprint(cx, 78, footprint=1, respect_roads=False):
                place_bldg(PlayerId.ONE, FORTIFIED_WALL_ID, cx, 78, footprint=1, respect_roads=False)
    for cy in range(48, 79):
        if not (61 <= cy <= 64) and grid.can_place_footprint(46, cy, footprint=1, respect_roads=False):
            place_bldg(PlayerId.ONE, FORTIFIED_WALL_ID, 46, cy, footprint=1, respect_roads=False)
        if not (50 <= cy <= 55 or 61 <= cy <= 64 or 70 <= cy <= 75) and grid.can_place_footprint(76, cy, footprint=1, respect_roads=False):
            place_bldg(PlayerId.TWO, FORTIFIED_WALL_ID, 76, cy, footprint=1, respect_roads=False)

    # =========================================================================
    # C. PLANNED URBAN DISTRICTS OF THE SEVEN HOUSES (Noble Stone Architecture)
    # =========================================================================
    district_buildings: list[tuple[PlayerId, int, int, int, int]] = [
        # 1. West Quarter: House of the Hammer of Wrath (Rog's Smithies & Guildhalls)
        (PlayerId.ONE, BLACKSMITH_ID, 20, 50, 3), (PlayerId.ONE, BLACKSMITH_ID, 20, 76, 3),
        (PlayerId.ONE, BARRACKS_ID, 39, 54, 3), (PlayerId.ONE, BARRACKS_ID, 39, 72, 3),
        (PlayerId.ONE, PAVILION_ID, 20, 46, 2), (PlayerId.ONE, PAVILION_ID, 30, 50, 2),
        (PlayerId.ONE, HOUSE_ID, 20, 82, 2), (PlayerId.ONE, HOUSE_ID, 20, 86, 2),
        (PlayerId.ONE, HOUSE_ID, 38, 46, 2), (PlayerId.ONE, HOUSE_ID, 42, 46, 2),
        (PlayerId.ONE, HOUSE_ID, 38, 78, 2), (PlayerId.ONE, HOUSE_ID, 42, 78, 2),
        # 2. South Quarter: House of the Wing (Tuor's Royal Guard & Noble Mansions)
        (PlayerId.ONE, BARRACKS_ID, 48, 34, 3), (PlayerId.ONE, BARRACKS_ID, 72, 34, 3),
        (PlayerId.ONE, ARCHERY_RANGE_ID, 48, 41, 3), (PlayerId.ONE, ARCHERY_RANGE_ID, 72, 41, 3),
        (PlayerId.ONE, BLACKSMITH_ID, 51, 20, 3), (PlayerId.ONE, BLACKSMITH_ID, 71, 20, 3),
        (PlayerId.ONE, PAVILION_ID, 53, 35, 2), (PlayerId.ONE, PAVILION_ID, 67, 35, 2),
        (PlayerId.ONE, HOUSE_ID, 44, 20, 2), (PlayerId.ONE, HOUSE_ID, 47, 20, 2),
        (PlayerId.ONE, HOUSE_ID, 75, 20, 2), (PlayerId.ONE, HOUSE_ID, 78, 20, 2),
        (PlayerId.ONE, HOUSE_ID, 44, 42, 2), (PlayerId.ONE, HOUSE_ID, 48, 46, 2),
        (PlayerId.ONE, HOUSE_ID, 76, 44, 2), (PlayerId.ONE, HOUSE_ID, 78, 38, 2),
        # 3. SW Quarter: House of the Tree & Wardens of the Secret Way (Idril & Galdor)
        (PlayerId.FOUR, BARRACKS_ID, 35, 19, 3), (PlayerId.FOUR, ARCHERY_RANGE_ID, 38, 35, 3),
        (PlayerId.FOUR, MONASTERY_ID, 20, 33, 3), (PlayerId.FOUR, PAVILION_ID, 20, 19, 2),
        (PlayerId.FOUR, HOUSE_ID, 39, 19, 2), (PlayerId.FOUR, HOUSE_ID, 44, 34, 2),
        (PlayerId.FOUR, HOUSE_ID, 44, 38, 2), (PlayerId.FOUR, HOUSE_ID, 30, 39, 2),
        # 4. East Quarter: House of the Fountain & Heavenly Arch (Ecthelion & Egalmoth)
        (PlayerId.TWO, ARCHERY_RANGE_ID, 99, 84, 3), (PlayerId.TWO, BARRACKS_ID, 95, 84, 3),
        (PlayerId.TWO, MONASTERY_ID, 85, 45, 3), (PlayerId.TWO, MARKET_ID, 97, 44, 4),
        (PlayerId.TWO, PAVILION_ID, 86, 80, 2), (PlayerId.TWO, HOUSE_ID, 79, 40, 2),
        (PlayerId.TWO, HOUSE_ID, 82, 40, 2), (PlayerId.TWO, HOUSE_ID, 98, 36, 2),
        (PlayerId.TWO, HOUSE_ID, 94, 89, 2), (PlayerId.TWO, HOUSE_ID, 98, 89, 2),
        # 5. SE Quarter: Court of Salgant & House of the Harp
        (PlayerId.THREE, STABLE_ID, 81, 20, 3), (PlayerId.THREE, STABLE_ID, 98, 20, 3),
        (PlayerId.THREE, MONASTERY_ID, 28, 88, 3), (PlayerId.THREE, PAVILION_ID, 98, 29, 2),
        (PlayerId.THREE, HOUSE_ID, 86, 19, 2), (PlayerId.THREE, HOUSE_ID, 94, 19, 2),
        (PlayerId.THREE, HOUSE_ID, 98, 26, 2), (PlayerId.THREE, HOUSE_ID, 95, 38, 2),
        # 6. NE Quarter: House of the Golden Flower & Swallow (Glorfindel & Duilin)
        (PlayerId.THREE, STABLE_ID, 88, 76, 3), (PlayerId.THREE, ARCHERY_RANGE_ID, 88, 84, 3),
        (PlayerId.THREE, UNIVERSITY_ID, 96, 94, 4), (PlayerId.THREE, PAVILION_ID, 77, 86, 2),
        (PlayerId.THREE, HOUSE_ID, 76, 102, 2), (PlayerId.THREE, HOUSE_ID, 77, 90, 2),
        (PlayerId.THREE, HOUSE_ID, 88, 90, 2), (PlayerId.THREE, HOUSE_ID, 96, 102, 2),
        (PlayerId.THREE, HOUSE_ID, 96, 106, 2), (PlayerId.THREE, HOUSE_ID, 88, 105, 2),
        # 7. NW Quarter: House of the Pillar & Tower of Snow (Penlod's Quarter)
        (PlayerId.TWO, UNIVERSITY_ID, 42, 84, 4), (PlayerId.TWO, MARKET_ID, 23, 89, 4),
        (PlayerId.TWO, BLACKSMITH_ID, 44, 104, 3), (PlayerId.TWO, BARRACKS_ID, 22, 100, 3),
        (PlayerId.TWO, PAVILION_ID, 28, 82, 2), (PlayerId.TWO, HOUSE_ID, 20, 94, 2),
        (PlayerId.TWO, HOUSE_ID, 20, 105, 2), (PlayerId.TWO, HOUSE_ID, 28, 105, 2),
        (PlayerId.TWO, HOUSE_ID, 36, 105, 2), (PlayerId.TWO, HOUSE_ID, 40, 90, 2),
    ]
    for p_id, u_id, bx, by, fp in district_buildings:
        place_bldg(p_id, u_id, bx, by, footprint=fp, respect_roads=True)

    # Ornamental Colonnades, Statues, Banners, and Olive/Cypress Groves along Avenues & Plazas
    avenue_ornaments: list[tuple[int, int, int]] = [
        (STATUE_ID, 56, 32), (STATUE_ID, 66, 32), (STATUE_ID, 56, 44), (STATUE_ID, 66, 44),
        (STATUE_ID, 56, 82), (STATUE_ID, 66, 82), (STATUE_ID, 42, 58), (STATUE_ID, 42, 68),
        (STATUE_ID, 80, 58), (STATUE_ID, 80, 68), (FLAG_A_ID, 57, 49), (FLAG_A_ID, 65, 49),
        (FLAG_A_ID, 57, 77), (FLAG_A_ID, 65, 77), (OLIVE_TREE_ID, 50, 52), (OLIVE_TREE_ID, 72, 52),
        (OLIVE_TREE_ID, 50, 74), (OLIVE_TREE_ID, 72, 74), (CYPRESS_TREE_ID, 45, 40), (CYPRESS_TREE_ID, 77, 40),
    ]
    for obj_id, ox, oy in avenue_ornaments:
        place_bldg(PlayerId.GAIA, obj_id, ox, oy, footprint=1, respect_roads=False)

    return placed_buildings


def _populate_forests_and_borders(grid: SafeMapGrid, um: Any) -> None:
    """Populate natural mountain forest clusters (~5,500 trees instead of 33,268) and seal map borders."""
    for ty in range(MAP_SIZE):
        for tx in range(MAP_SIZE):
            if (tx, ty) in grid.occupied_tiles or (tx, ty) in grid.no_tree_zones:
                continue
            is_outer_border = tx in (0, 1, MAP_SIZE - 2, MAP_SIZE - 1) or ty in (0, 1, MAP_SIZE - 2, MAP_SIZE - 1)
            # Solid canyon/ridge walls (100% trees) around Orfalch Echor (tx>=174) & tunnel ridge (48<=ty<=57),
            # plus natural 25% pine clusters on the outer Tumladen hills
            is_canyon_wall = grid.terrain[ty][tx] == TerrainId.FOREST_PINE and ((174 <= tx <= 226 and 76 <= ty <= 230 and (tx in (174, 175, 225, 226) or ty in (76, 77, 173, 174, 215, 216, 229, 230))) or 50 <= ty <= 53)
            in_pine_cluster = (
                grid.terrain[ty][tx] == TerrainId.FOREST_PINE
                and (is_canyon_wall or ((tx * 73 + ty * 151 + (tx // 4) * 31) % 100) < 25)
            )
            if is_outer_border or in_pine_cluster:
                tree_id = PINE_TREE_ID if (tx + ty) % 3 != 0 else OAK_TREE_ID
                um.add_unit(player=PlayerId.GAIA, unit_const=tree_id, x=float(tx) + 0.5, y=float(ty) + 0.5)
                grid.occupied_tiles.add((tx, ty))

    # Surround Balance Sanctuary (X=4..20, Y=220..236) with indestructible rock cliffs
    for tx in range(4, 21):
        for ty in (220, 236):
            grid.place_unit_safe(um, PlayerId.GAIA, ROCK_CLIFF_ID, tx, ty, clear_trees_around=False, strict=False)
    for ty in range(221, 236):
        for tx in (4, 20):
            grid.place_unit_safe(um, PlayerId.GAIA, ROCK_CLIFF_ID, tx, ty, clear_trees_around=False, strict=False)


def build_map_and_entities(scenario: Any) -> dict[str, Any]:
    """Build the 240x240 Gondolin map with 0 placement collisions, place P1-P8 entities, and return context dict."""
    mm = scenario.map_manager
    um = scenario.unit_manager
    pm = scenario.player_manager

    mm.map_size = MAP_SIZE
    _configure_players_and_diplomacy(pm)

    grid = SafeMapGrid(MAP_SIZE)
    _sculpt_world_terrain(grid)

    for ty in range(MAP_SIZE):
        for tx in range(MAP_SIZE):
            tile = mm.get_tile(tx, ty)
            tile.terrain_id = grid.terrain[ty][tx]
            tile.elevation = grid.elevation[ty][tx]

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
        obj = grid.place_unit_safe(
            um, player, unit_id, x, y, footprint=footprint, respect_roads=False, strict=True
        )
        quest_buildings[key] = {
            "ref_id": obj.reference_id,
            "x": x,
            "y": y,
            "player": player,
            "unit_id": unit_id,
            "footprint": footprint,
        }
        if player in player_bldg_counts:
            player_bldg_counts[player] += 1
        return obj

    # =========================================================================
    # 1. KEY LANDMARKS, ROYAL FOUNTAIN, GLINGAL & BELTHIL IN GONDOLIN
    # =========================================================================
    # Tower of King Turgon on the high acropolis of Amon Gwareth (elev=7)
    register_bldg("tower_of_turgon", PlayerId.ONE, CASTLE_ID, 60, 71, footprint=4)
    grid.place_unit_safe(um, PlayerId.ONE, KEEP_ID, 54, 71, footprint=2, strict=True)
    grid.place_unit_safe(um, PlayerId.ONE, KEEP_ID, 66, 71, footprint=2, strict=True)
    player_bldg_counts[PlayerId.ONE] += 2

    # Hall of the Fountain south of the water basin, while (61, 61) is a true water/statue fountain!
    register_bldg("royal_fountain_bldg", PlayerId.TWO, MONASTERY_ID, 61, 52, footprint=3)
    for ox, oy in [(57, 58), (65, 58), (57, 64), (65, 64)]:
        grid.place_unit_safe(um, PlayerId.GAIA, STATUE_ID, ox, oy, footprint=1, strict=True)
        grid.place_unit_safe(um, PlayerId.GAIA, TORCH_ID, ox + 1, oy, footprint=1, strict=True)

    # Sacred Trees Glingal (Gold Tree) & Belthil (Silver Tree): actual trees + statues instead of tents!
    register_bldg("glingal_tree", PlayerId.GAIA, OLIVE_TREE_ID, 53, 61, footprint=1)
    grid.place_unit_safe(um, PlayerId.GAIA, STATUE_ID, 53, 60, footprint=1, strict=True)
    grid.place_unit_safe(um, PlayerId.GAIA, TORCH_ID, 52, 61, footprint=1, strict=True)

    register_bldg("belthil_tree", PlayerId.GAIA, CYPRESS_TREE_ID, 69, 61, footprint=1)
    grid.place_unit_safe(um, PlayerId.GAIA, STATUE_ID, 69, 60, footprint=1, strict=True)
    grid.place_unit_safe(um, PlayerId.GAIA, TORCH_ID, 70, 61, footprint=1, strict=True)

    # Path A (West): Forges of Rog moved to (24, 56) & (24, 70) so the West Avenue (Y=61..65) is 100% clear!
    register_bldg("great_forge", PlayerId.ONE, BLACKSMITH_ID, 24, 56, footprint=3)
    register_bldg("forge_workshop", PlayerId.ONE, SIEGE_WORKSHOP_ID, 24, 70, footprint=4)
    for cx_off in (29, 31, 33):
        grid.place_unit_safe(um, PlayerId.ONE, UNIT_REFUGEE_CART_ID, cx_off, 57, footprint=1, strict=True)

    # Path B (East): Great Market of Penlod (north of East Avenue) & Fountain Aqueduct
    register_bldg("great_market", PlayerId.TWO, MARKET_ID, 93, 56, footprint=4)
    register_bldg("aqueduct_control", PlayerId.EIGHT, UNIVERSITY_ID, 84, 74, footprint=4)

    # North Quarter: Tower of Snow (P3 Duilin high vantage point)
    register_bldg("snow_watchtower", PlayerId.THREE, KEEP_ID, 74, 105, footprint=2)

    # Path C (South-East): Court of Salgant (House of the Harp) enclosed by wall + salgant_gate_rocks
    register_bldg("salgant_manor", PlayerId.THREE, CASTLE_ID, 91, 25, footprint=4)
    for wy in range(17, 34):
        if grid.can_place_footprint(84, wy, footprint=1, respect_roads=False):
            grid.place_unit_safe(um, PlayerId.THREE, FORTIFIED_WALL_ID, 84, wy, footprint=1, strict=True)
    for bx in range(85, 104):
        if 87 <= bx <= 93:
            r_obj = grid.place_unit_safe(
                um, PlayerId.GAIA, ROCK_CLIFF_ID, bx, 33, footprint=1, clear_trees_around=False, strict=True
            )
            destructible_rocks["salgant_gate_rocks"].append(r_obj.reference_id)
        elif grid.can_place_footprint(bx, 33, footprint=1, respect_roads=False):
            grid.place_unit_safe(um, PlayerId.THREE, FORTIFIED_WALL_ID, bx, 33, footprint=1, strict=True)
    for hx in (89, 91, 93):
        grid.place_unit_safe(um, PlayerId.THREE, UNIT_HARP_HEALER_ID, hx, 21, footprint=1, strict=True)

    # SW Quarter: House of Tuor & Caragdur Precipice (P4 completely sealed off at 0:00 by P8 Maeglin's wall & blockade!)
    register_bldg("house_of_tuor", PlayerId.FOUR, KREPOST_ID, 24, 24, footprint=4)
    register_bldg("caragdur_keep", PlayerId.EIGHT, KEEP_ID, 18, 42, footprint=2)
    for wx in range(17, 43):
        if grid.can_place_footprint(wx, 44, footprint=1, respect_roads=False):
            grid.place_unit_safe(um, PlayerId.EIGHT, FORTIFIED_WALL_ID, wx, 44, footprint=1, strict=True)
    for by in range(17, 45):
        if 23 <= by <= 29:
            r_obj = grid.place_unit_safe(
                um, PlayerId.GAIA, ROCK_CLIFF_ID, 42, by, footprint=1, clear_trees_around=False, strict=True
            )
            destructible_rocks["caragdur_blockade"].append(r_obj.reference_id)
        elif grid.can_place_footprint(42, by, footprint=1, respect_roads=False):
            grid.place_unit_safe(um, PlayerId.EIGHT, FORTIFIED_WALL_ID, 42, by, footprint=1, strict=True)

    # North Quarter Fire Hazard (hurts units until P2 captures aqueduct_control)
    for fx in range(56, 67, 3):
        for fy in (99, 103):
            f_obj = grid.place_unit_safe(
                um, PlayerId.GAIA, FLAME_EFFECT_ID, fx, fy, footprint=1, clear_trees_around=False, strict=True
            )
            destructible_rocks["north_fire_objects"].append(f_obj.reference_id)

    # Rocks blocking the Northern Moat shallows (removed when P2 floods the moat)
    for rx in range(48, 75, 3):
        r_obj = grid.place_unit_safe(
            um, PlayerId.GAIA, ROCK_CLIFF_ID, rx, 114, footprint=1, clear_trees_around=False, strict=True
        )
        destructible_rocks["aqueduct_dry_rocks"].append(r_obj.reference_id)

    # Phase II Exit Gates & Siege Perimeter (Sealed at X=105 until Gothmog falls on Amon Gwareth!)
    register_bldg("idril_waygate", PlayerId.FOUR, OUTPOST_ID, 73, 52, footprint=2)
    for sx_wall in range(2, 106):
        if grid.can_place_footprint(sx_wall, 124, footprint=1, respect_roads=False):
            grid.place_unit_safe(um, PlayerId.GAIA, ROCK_CLIFF_ID, sx_wall, 124, footprint=1, clear_trees_around=False, strict=True)
    for sy_wall in range(2, 125):
        if 49 <= sy_wall <= 55 or 60 <= sy_wall <= 68:
            r_obj = grid.place_unit_safe(
                um, PlayerId.GAIA, ROCK_CLIFF_ID, 105, sy_wall, footprint=1, clear_trees_around=False, strict=True
            )
            destructible_rocks["tumladen_exit_rocks"].append(r_obj.reference_id)
        elif grid.can_place_footprint(105, sy_wall, footprint=1, respect_roads=False):
            grid.place_unit_safe(um, PlayerId.GAIA, ROCK_CLIFF_ID, 105, sy_wall, footprint=1, clear_trees_around=False, strict=True)
    # Rock ridge spine separating Lower Route (Y=36..44) from Upper Route (Y=60..92) across Tumladen
    for rx_spine in range(106, 172):
        if grid.can_place_footprint(rx_spine, 55, footprint=1, respect_roads=False):
            grid.place_unit_safe(um, PlayerId.GAIA, ROCK_CLIFF_ID, rx_spine, 55, footprint=1, clear_trees_around=False, strict=True)
    for ry in range(50, 56):
        r_obj = grid.place_unit_safe(
            um, PlayerId.GAIA, ROCK_CLIFF_ID, 78, ry, footprint=1, clear_trees_around=False, strict=True
        )
        destructible_rocks["tumladen_exit_rocks"].append(r_obj.reference_id)
    for ry in range(70, 76):
        r_obj = grid.place_unit_safe(
            um, PlayerId.GAIA, ROCK_CLIFF_ID, 78, ry, footprint=1, clear_trees_around=False, strict=True
        )
        destructible_rocks["tumladen_exit_rocks"].append(r_obj.reference_id)

    # =========================================================================
    # 2. PHASE II & III STRUCTURES: TUMLADEN & ARCHITECTURAL SEVEN GATES
    # =========================================================================
    register_bldg("wolf_camp_1", PlayerId.FIVE, STABLE_ID, 132, 94, footprint=3)
    register_bldg("wolf_camp_2", PlayerId.FIVE, STABLE_ID, 156, 94, footprint=3)
    register_bldg("balrog_altar", PlayerId.SEVEN, KREPOST_ID, 145, 112, footprint=4)
    register_bldg("cliff_tower_1", PlayerId.FIVE, GUARD_TOWER_ID, 132, 62, footprint=2)
    register_bldg("cliff_tower_2", PlayerId.FIVE, GUARD_TOWER_ID, 156, 62, footprint=2)

    # Architectural Seven Gates of Orfalch Echor: paired flanking towers + removable rock barrier
    gate_configs: list[tuple[str, int, int, int]] = [
        ("orfalch_gate_1", 190, 94, OUTPOST_ID),      # 1. Gate of Wood
        ("orfalch_gate_2", 198, 108, GUARD_TOWER_ID), # 2. Gate of Stone
        ("orfalch_gate_3", 206, 122, GUARD_TOWER_ID), # 3. Gate of Bronze
        ("orfalch_gate_4", 208, 138, KEEP_ID),        # 4. Gate of Writhen Iron
        ("orfalch_gate_5", 202, 150, KEEP_ID),        # 5. Gate of Silver
        ("orfalch_gate_6", 196, 162, KEEP_ID),        # 6. Gate of Gold
        ("orfalch_gate_7", 190, 174, KEEP_ID),        # 7. Great Gate of Steel
    ]
    for g_key, gx, gy, tower_id in gate_configs:
        grid.place_unit_safe(um, PlayerId.ONE, tower_id, gx - 6, gy, footprint=2, strict=True)
        grid.place_unit_safe(um, PlayerId.ONE, tower_id, gx + 5, gy, footprint=2, strict=True)
        player_bldg_counts[PlayerId.ONE] += 2
        for dx in range(-4, 5):
            r_obj = grid.place_unit_safe(
                um, PlayerId.GAIA, ROCK_CLIFF_ID, gx + dx, gy, footprint=1, clear_trees_around=False, strict=True
            )
            destructible_rocks[g_key].append(r_obj.reference_id)
    # Seal the entire Y=174 canyon line and X=174 western cliff wall so Cirith Thoronath is only reachable via Gate 7
    for gx_canyon in range(174, 238):
        if 176 <= gx_canyon <= 183:
            if grid.can_place_footprint(gx_canyon, 174, footprint=1, respect_roads=False):
                r_obj = grid.place_unit_safe(
                    um, PlayerId.GAIA, ROCK_CLIFF_ID, gx_canyon, 174, footprint=1, clear_trees_around=False, strict=True
                )
                destructible_rocks["orfalch_gate_7"].append(r_obj.reference_id)
        elif grid.can_place_footprint(gx_canyon, 174, footprint=1, respect_roads=False):
            grid.place_unit_safe(um, PlayerId.GAIA, ROCK_CLIFF_ID, gx_canyon, 174, footprint=1, clear_trees_around=False, strict=True)
    for gy_canyon in range(175, 238):
        if grid.can_place_footprint(174, gy_canyon, footprint=1, respect_roads=False):
            grid.place_unit_safe(um, PlayerId.GAIA, ROCK_CLIFF_ID, 174, gy_canyon, footprint=1, clear_trees_around=False, strict=True)

    register_bldg("winch_bronze", PlayerId.FIVE, OUTPOST_ID, 188, 114, footprint=2)
    register_bldg("winch_silver", PlayerId.FIVE, OUTPOST_ID, 194, 144, footprint=2)
    register_bldg("winch_steel", PlayerId.SEVEN, KEEP_ID, 180, 171, footprint=2)

    # Seal the X=218 precipice line across Y=175..238, with cirith_exit_rocks at Y=218..226
    for cy_exit in range(175, 238):
        if 218 <= cy_exit <= 226:
            if grid.can_place_footprint(218, cy_exit, footprint=1, respect_roads=False):
                r_obj = grid.place_unit_safe(
                    um, PlayerId.GAIA, ROCK_CLIFF_ID, 218, cy_exit, footprint=1, clear_trees_around=False, strict=True
                )
                destructible_rocks["cirith_exit_rocks"].append(r_obj.reference_id)
        elif grid.can_place_footprint(218, cy_exit, footprint=1, respect_roads=False):
            grid.place_unit_safe(um, PlayerId.GAIA, ROCK_CLIFF_ID, 218, cy_exit, footprint=1, clear_trees_around=False, strict=True)

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

    refugee_groups: list[dict[str, Any]] = [
        {"id": "ref_smiths", "name": "Czeladnicy Domu Mlota", "x": 32, "y": 74, "reward_player": PlayerId.ONE, "reward_unit": UNIT_HAMMER_SMITH_ID, "reward_count": 6},
        {"id": "ref_fountain", "name": "Straznicy Wody z Polnocy", "x": 48, "y": 98, "reward_player": PlayerId.TWO, "reward_unit": UNIT_FOUNTAIN_GUARD_ID, "reward_count": 6},
        {"id": "ref_archers", "name": "Lucznicy z Wielkiego Targu", "x": 96, "y": 78, "reward_player": PlayerId.TWO, "reward_unit": UNIT_ARCH_LONGBOW_ID, "reward_count": 6},
        {"id": "ref_swallows", "name": "Zwiadowcy Domu Jaskolki", "x": 82, "y": 98, "reward_player": PlayerId.THREE, "reward_unit": UNIT_SWALLOW_SNIPER_ID, "reward_count": 6},
        {"id": "ref_healers", "name": "Uzdrowiciele Domu Harfy", "x": 78, "y": 32, "reward_player": PlayerId.THREE, "reward_unit": UNIT_HARP_HEALER_ID, "reward_count": 3},
        {"id": "ref_wrights", "name": "Inzynierowie Domu Drzewa", "x": 34, "y": 46, "reward_player": PlayerId.FOUR, "reward_unit": UNIT_TREE_PIKE_ID, "reward_count": 8},
    ]
    for rg in refugee_groups:
        grid.mark_road_box(rg["x"] - 3, rg["y"] - 3, rg["x"] + 3, rg["y"] + 3)

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
            grid.place_unit_safe(um, p_id, h_id, sx + idx * 2 - 1, sy, footprint=1, strict=True)

        offset_idx = 0
        for unit_id, count in retinues[p_id]:
            for _ in range(count):
                dx = (offset_idx % 7) - 3
                dy = (offset_idx // 7) + 2
                grid.place_unit_safe(um, p_id, unit_id, sx + dx, sy + dy, footprint=1, strict=True)
                offset_idx += 1

    # Balance Sanctuary King & initial Map Revealers (allow_overlap=True for invisible revealers)
    grid.place_unit_safe(um, PlayerId.ONE, SANCTUARY_KING_ID, 12, 228, footprint=1, strict=True)
    grid.place_unit_safe(um, PlayerId.ONE, MAP_REVEALER_ID, 12, 228, footprint=1, allow_overlap=True)
    grid.place_unit_safe(um, PlayerId.ONE, MAP_REVEALER_ID, 61, 61, footprint=1, allow_overlap=True)
    player_bldg_counts[PlayerId.ONE] += 2

    for rg in refugee_groups:
        for i in range(4):
            grid.place_unit_safe(
                um, PlayerId.GAIA, UNIT_REFUGEE_CIV_ID, rg["x"] + (i % 2), rg["y"] + (i // 2), footprint=1, strict=True
            )

    # P5-P8 initial military buildings & combat units at 0:00 (prevents early Defeat)
    grid.place_unit_safe(um, PlayerId.FIVE, BARRACKS_ID, 52, 118, footprint=3, strict=True)
    grid.place_unit_safe(um, PlayerId.FIVE, ARCHERY_RANGE_ID, 70, 118, footprint=3, strict=True)
    for i in range(8):
        grid.place_unit_safe(
            um, PlayerId.FIVE, ENEMY_ORC_INFANTRY_ID, 58 + (i % 4), 104 + (i // 4), footprint=1, strict=True
        )
    for i in range(4):
        grid.place_unit_safe(um, PlayerId.FIVE, ENEMY_ORC_ARCHER_ID, 131 + i, 65, footprint=1, strict=True)
        grid.place_unit_safe(um, PlayerId.FIVE, ENEMY_ORC_ARCHER_ID, 155 + i, 65, footprint=1, strict=True)

    grid.place_unit_safe(um, PlayerId.SIX, SIEGE_WORKSHOP_ID, 61, 120, footprint=4, strict=True)
    grid.place_unit_safe(um, PlayerId.SIX, SIEGE_WORKSHOP_ID, 109, 63, footprint=4, strict=True)
    grid.place_unit_safe(um, PlayerId.SIX, ENEMY_IRON_DRAGON_RAM_ID, 61, 116, footprint=1, strict=True)
    grid.place_unit_safe(um, PlayerId.SIX, ENEMY_FIRE_DRAKE_ID, 59, 116, footprint=1, strict=True)
    grid.place_unit_safe(um, PlayerId.SIX, ENEMY_HEAVY_SCORPION_ID, 63, 116, footprint=1, strict=True)
    grid.place_unit_safe(um, PlayerId.SIX, ENEMY_IRON_DRAGON_RAM_ID, 102, 63, footprint=1, strict=True)

    grid.place_unit_safe(um, PlayerId.SEVEN, CASTLE_ID, 145, 119, footprint=4, strict=True)
    grid.place_unit_safe(um, PlayerId.SEVEN, ENEMY_BALROG_BOSS_ID, 145, 108, footprint=1, strict=True)
    grid.place_unit_safe(um, PlayerId.SEVEN, ENEMY_BALROG_BOSS_ID, 184, 173, footprint=1, strict=True)

    grid.place_unit_safe(um, PlayerId.EIGHT, BARRACKS_ID, 19, 38, footprint=3, strict=True)
    for i in range(4):
        grid.place_unit_safe(um, PlayerId.EIGHT, ENEMY_MOLE_TRAITOR_ID, 21 + i, 40, footprint=1, strict=True)
        grid.place_unit_safe(um, PlayerId.EIGHT, ENEMY_MOLE_PIKE_ID, 83 + i, 70, footprint=1, strict=True)

    _populate_forests_and_borders(grid, um)

    return {
        "grid": grid,
        "destructible_rocks": destructible_rocks,
        "quest_buildings": quest_buildings,
        "refugee_groups": refugee_groups,
        "starts": starts,
        "player_bldg_counts": player_bldg_counts,
        "sanctuary": {
            "x1": 5, "y1": 221, "x2": 19, "y2": 235, "cx": 12, "cy": 228,
            "harder_area": (8, 232, 16, 235), "easier_area": (8, 221, 16, 224),
        },
        "checkpoints": {
            "phase1": {PlayerId.ONE: (61, 49), PlayerId.TWO: (66, 56), PlayerId.THREE: (61, 66), PlayerId.FOUR: (55, 56)},
            "phase2": {PlayerId.ONE: (110, 86), PlayerId.TWO: (110, 40), PlayerId.THREE: (114, 86), PlayerId.FOUR: (114, 40)},
            "phase3": {PlayerId.ONE: (184, 84), PlayerId.TWO: (186, 84), PlayerId.THREE: (184, 88), PlayerId.FOUR: (186, 88)},
        },
        "sectors": {
            "caragdur_gate": (38, 20, 46, 32),
            "caragdur_cliff": (14, 36, 26, 48),
            "aqueduct_sluice": (78, 68, 90, 80),
            "north_fire_zone": (52, 90, 70, 104),
            "north_moat": (44, 110, 78, 118),
            "tower_of_snow": (70, 102, 78, 110),
            "enclave_forges": (18, 52, 34, 74),
            "enclave_market": (88, 52, 102, 72),
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
            "sirion_exit": (219, 216, 232, 230),
        },
        "dragon_corridors": {
            "north_avenue": [(55, 102, 67, 114), (55, 88, 67, 101), (55, 76, 67, 87)],
            "east_avenue": [(92, 57, 104, 69), (78, 57, 91, 69)],
        },
    }
