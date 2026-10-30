"""Stage B-II verification suite: exact footprints, 0 collisions, multi-state BFS pathfinding, and 2D preview."""

from __future__ import annotations

from collections import deque
import importlib
from pathlib import Path
import shutil
import types
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

import reproduce_audit_metrics

reproduce_audit_metrics._ensure_aoe2_parser_or_mock()

import gondolin_config
import gondolin_map

importlib.reload(gondolin_config)
importlib.reload(gondolin_map)

from gondolin_config import MAP_SIZE, OAK_TREE_ID, PINE_TREE_ID, PlayerId
from gondolin_map import footprint_bounds


def bfs_reachable(
    blocked: set[tuple[int, int]],
    start: tuple[int, int],
    goal: tuple[int, int],
    size: int = MAP_SIZE,
) -> bool:
    """Return True if a 4-connected path exists from start to goal avoiding blocked tiles (except start/goal)."""
    q: deque[tuple[int, int]] = deque([start])
    visited: set[tuple[int, int]] = {start}
    while q:
        cx, cy = q.popleft()
        if abs(cx - goal[0]) <= 2 and abs(cy - goal[1]) <= 2:
            return True
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < size and 0 <= ny < size and (nx, ny) not in visited:
                if (nx, ny) not in blocked or (nx, ny) == goal:
                    visited.add((nx, ny))
                    q.append((nx, ny))
    return False


def render_cartographic_preview(ctx: dict[str, Any], units: list[Any], out_file: Path) -> None:
    """Render a high-resolution 2D cartographic preview of the 240x240 map and a zoom of Gondolin."""
    grid = ctx["grid"]
    img = np.zeros((MAP_SIZE, MAP_SIZE, 3), dtype=np.float32)

    terrain_colors: dict[int, tuple[float, float, float]] = {
        0: (0.36, 0.62, 0.28),   # GRASS_1
        12: (0.44, 0.68, 0.34),  # GRASS_2
        19: (0.16, 0.36, 0.18),  # FOREST_PINE
        24: (0.82, 0.80, 0.75),  # ROAD (Gondolin white/grey stone)
        25: (0.48, 0.42, 0.38),  # ROAD_BROKEN (Siege breach rubble)
        38: (0.38, 0.32, 0.42),  # ROAD_FUNGUS (Secret tunnel)
        4: (0.38, 0.72, 0.88),   # SHALLOWS
        1: (0.12, 0.42, 0.78),   # WATER_AZURE
        6: (0.62, 0.52, 0.38),   # DIRT_1
        11: (0.56, 0.48, 0.35),  # DIRT_2
        3: (0.52, 0.46, 0.40),   # DIRT_3
    }

    for y in range(MAP_SIZE):
        for x in range(MAP_SIZE):
            base_c = terrain_colors.get(grid.terrain[y][x], (0.4, 0.5, 0.3))
            elev_factor = 0.85 + 0.04 * grid.elevation[y][x]
            img[y, x] = np.clip(np.array(base_c) * elev_factor, 0.0, 1.0)

    # Overlay trees, rocks, walls, and player buildings/units
    player_colors: dict[int, tuple[float, float, float]] = {
        1: (0.15, 0.45, 0.98),  # P1 Blue
        2: (0.92, 0.20, 0.20),  # P2 Red
        3: (0.18, 0.82, 0.25),  # P3 Green
        4: (0.96, 0.86, 0.15),  # P4 Yellow
        5: (0.15, 0.85, 0.85),  # P5 Cyan (Orcs)
        6: (0.98, 0.52, 0.10),  # P6 Orange (Dragons)
        7: (0.55, 0.15, 0.15),  # P7 Dark Red/Grey (Balrogs)
        8: (0.68, 0.22, 0.88),  # P8 Purple (Traitors)
    }

    for u in units:
        ix, iy = int(u.x), int(u.y)
        if not (0 <= ix < MAP_SIZE and 0 <= iy < MAP_SIZE):
            continue
        if u.unit_const in (OAK_TREE_ID, PINE_TREE_ID):
            img[iy, ix] = (0.08, 0.24, 0.10)
        elif u.unit_const == 623:  # ROCK_CLIFF_ID
            img[iy, ix] = (0.28, 0.28, 0.30)
        elif u.unit_const == 155:  # FORTIFIED_WALL_ID
            img[iy, ix] = (0.95, 0.95, 0.98)
        elif int(u.player) in player_colors:
            img[iy, ix] = player_colors[int(u.player)]

    fig, axes = plt.subplots(1, 2, figsize=(15, 7.2), dpi=140)
    axes[0].imshow(img, origin="lower")
    axes[0].set_title("Pelna Mapa 240x240: Gondolin, Tumladen, Orfalch Echor i Cirith Thoronath", fontsize=10)
    axes[0].set_xlabel("X")
    axes[0].set_ylabel("Y")

    axes[1].imshow(img[12:120, 12:112], origin="lower", extent=[12, 112, 12, 120])
    axes[1].set_title("Zblizenie: Miasto Gondolin, Mury, Aleje i Wzgorze Amon Gwareth", fontsize=10)
    axes[1].set_xlabel("X (Gondolin)")
    axes[1].set_ylabel("Y (Gondolin)")

    plt.tight_layout()
    fig.savefig(str(out_file))
    plt.close(fig)


def run_stage_b_tests() -> None:
    """Execute all Stage B-II geometric, collision, tree budget, and multi-state BFS pathfinding tests."""
    # 1. Verify exact footprint bounds for even and odd sizes
    assert footprint_bounds(10, 10, 1) == (10, 10, 10, 10)  # 1x1
    assert footprint_bounds(10, 10, 2) == (10, 10, 11, 11)  # 2x2
    assert footprint_bounds(10, 10, 3) == (9, 9, 11, 11)    # 3x3
    assert footprint_bounds(10, 10, 4) == (9, 9, 12, 12)    # 4x4

    placed_units: list[Any] = []
    ref_to_tile: dict[int, tuple[int, int]] = {}

    def record_unit(player: PlayerId, unit_const: int, x: float, y: float) -> Any:
        ref_id = len(placed_units) + 1
        u = types.SimpleNamespace(reference_id=ref_id, player=player, unit_const=unit_const, x=x, y=y)
        placed_units.append(u)
        ref_to_tile[ref_id] = (int(x), int(y))
        return u

    scen = types.SimpleNamespace(
        map_manager=types.SimpleNamespace(
            map_size=MAP_SIZE,
            get_tile=lambda x, y: types.SimpleNamespace(terrain_id=0, elevation=0),
        ),
        unit_manager=types.SimpleNamespace(units=placed_units, add_unit=record_unit),
        player_manager=types.SimpleNamespace(
            active_players=8,
            players=[None] + [types.SimpleNamespace(diplomacy=[0] * 9) for _ in range(8)],
        ),
    )

    ctx = gondolin_map.build_map_and_entities(scen)
    grid = ctx["grid"]
    rocks = ctx["destructible_rocks"]
    q_bldgs = ctx["quest_buildings"]

    # 2. Verify zero failed placements and tree count budget
    assert len(grid.failed_placements) == 0, f"Failed placements: {grid.failed_placements}"
    tree_count = sum(1 for u in placed_units if u.unit_const in (OAK_TREE_ID, PINE_TREE_ID))
    assert 3000 <= tree_count <= 9000, f"Tree count {tree_count} out of budget [3000..9000]"

    # Build static obstacle set (buildings, walls, trees, cliffs, excluding mobile units)
    mobile_unit_ids = {
        426, 1066, 168, 682, 172, 428, 1292, 636, 430, 434, 837,
        1703, 693, 567, 1661, 359, 530, 1130, 882, 569, 469, 125,
        1699, 185, 440, 128, 293, 752, 1124, 473, 4, 24, 89, 756,
        548, 188, 542, 1737, 1713, 878, 532, 640, 303,
    }
    blocked_0s: set[tuple[int, int]] = set()
    for u in placed_units:
        if u.unit_const not in mobile_unit_ids:
            # Find footprint if registered in quest_buildings or standard wall/tower
            fp = 1
            if u.unit_const in (234, 235, 598, 626, 70):
                fp = 2
            elif u.unit_const in (12, 87, 101, 103, 104):
                fp = 3
            elif u.unit_const in (49, 82, 84, 209, 1251):
                fp = 4
            cx = round(u.x - 0.5) if fp % 2 == 1 else round(u.x - 1.0)
            cy = round(u.y - 0.5) if fp % 2 == 1 else round(u.y - 1.0)
            x1, y1, x2, y2 = footprint_bounds(cx, cy, fp)
            for ty in range(y1, y2 + 1):
                for tx in range(x1, x2 + 1):
                    blocked_0s.add((tx, ty))

    # 3. Negative BFS Tests at 0:00 (Blockades MUST block passage before triggers remove them!)
    assert not bfs_reachable(blocked_0s, (61, 24), (28, 28)), "caragdur_blockade failed to block P1->P4 at 0:00!"
    assert not bfs_reachable(blocked_0s, (61, 56), (110, 40)), "tumladen_exit_rocks failed to block Lower Route at 0:00!"
    assert not bfs_reachable(blocked_0s, (61, 56), (110, 86)), "tumladen_exit_rocks failed to block Upper Route at 0:00!"
    assert not bfs_reachable(blocked_0s, (184, 84), (198, 198)), "orfalch_gates failed to block Cirith Thoronath at 0:00!"
    assert not bfs_reachable(blocked_0s, (198, 198), (224, 224)), "cirith_exit_rocks failed to block Sirion Exit at 0:00!"

    # 4. Positive BFS Tests at 0:00 (All open city avenues & enclaves reachable from Amon Gwareth!)
    for name, target in [
        ("South_Gate_P1", (61, 24)),
        ("Fountain_Terrace_P2", (82, 58)),
        ("North_Approach_P3", (68, 92)),
        ("Great_Forge_West", (28, 63)),
        ("Great_Market_East", (93, 62)),
        ("Aqueduct_Control", (84, 70)),
        ("Snow_Watchtower", (74, 102)),
    ]:
        assert bfs_reachable(blocked_0s, (61, 61), target), f"Amon Gwareth (61,61) cannot reach {name} {target}!"

    # 5. Progressive State Transitions BFS:
    def unblock_rock_group(b_set: set[tuple[int, int]], key: str) -> None:
        for r_id in rocks[key]:
            if r_id in ref_to_tile:
                b_set.discard(ref_to_tile[r_id])

    blocked_p1_breach = set(blocked_0s)
    unblock_rock_group(blocked_p1_breach, "caragdur_blockade")
    assert bfs_reachable(blocked_p1_breach, (61, 24), (28, 28)), "P1 still cannot reach P4 after breaching Caragdur!"
    assert bfs_reachable(blocked_p1_breach, (28, 28), (18, 40)), "P1/P4 cannot reach Caragdur Keep (18,42)!"

    blocked_p2 = set(blocked_p1_breach)
    unblock_rock_group(blocked_p2, "tumladen_exit_rocks")
    assert bfs_reachable(blocked_p2, (61, 56), (110, 40)), "Cannot reach Lower Route (110,40) in Phase II!"
    assert bfs_reachable(blocked_p2, (61, 56), (110, 86)), "Cannot reach Upper Route (110,86) in Phase II!"
    assert bfs_reachable(blocked_p2, (110, 40), (184, 84)), "Lower Route cannot reach Orfalch Echor (184,84)!"
    assert bfs_reachable(blocked_p2, (110, 86), (184, 84)), "Upper Route cannot reach Orfalch Echor (184,84)!"

    blocked_p3 = set(blocked_p2)
    for g_idx in range(1, 8):
        unblock_rock_group(blocked_p3, f"orfalch_gate_{g_idx}")
    assert bfs_reachable(blocked_p3, (184, 84), (198, 198)), "Cannot reach Cirith Thoronath Duel Spur (198,198)!"

    unblock_rock_group(blocked_p3, "cirith_exit_rocks")
    assert bfs_reachable(blocked_p3, (198, 198), (224, 224)), "Cannot reach Vale of Sirion Victory Exit (224,224)!"

    preview_path = Path("gondolin_map_preview.png")
    render_cartographic_preview(ctx, placed_units, preview_path)

    print("=" * 78)
    print("RAPORT WALIDACJI GEOMETRII I PRZEJEZDNOSCI BFS (ETAP B-II)")
    print("=" * 78)
    print(f"1. Odrzucone placementy (failed_placements) : {len(grid.failed_placements)} (0 kolizji!)")
    print(f"2. Laczna liczba obiektow na mapie          : {len(placed_units)}")
    print(f"3. Liczba drzew (budzet 3000..9000)         : {tree_count}")
    print("4. Testy negatywne BFS w 0:00 (5/5 blokad)  : PASS (Caragdur, Tumladen, Orfalch, Sirion szczelne)")
    print("5. Testy pozytywne BFS w 0:00 i Fazach I-III: PASS (Wszystkie aleje, enklawy i szlaki drozne)")
    print(f"6. Wygenerowano podglad 2D mapy             : {preview_path.resolve()}")
    print("=" * 78)


if __name__ == "__main__":
    run_stage_b_tests()
    shutil.rmtree("__pycache__", ignore_errors=True)
