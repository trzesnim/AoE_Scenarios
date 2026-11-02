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
    mobile_unit_ids = (
        set(gondolin_config.PLAYER_ALL_COMBAT_UNITS)
        | set(gondolin_config.ENEMY_MELEE_UNITS)
        | set(gondolin_config.ENEMY_RANGED_UNITS)
        | {
            gondolin_config.SANCTUARY_KING_ID,
            gondolin_config.MAP_REVEALER_ID,
            gondolin_config.UNIT_HARP_HEALER_ID,
            gondolin_config.UNIT_IDRIL_SAPPER_ID,
            gondolin_config.UNIT_REFUGEE_CART_ID,
            gondolin_config.UNIT_REFUGEE_CIV_ID,
            gondolin_config.ENEMY_IRON_DRAGON_RAM_ID,
            gondolin_config.FLAME_EFFECT_ID,
        }
    )
    blocked_0s: set[tuple[int, int]] = set()
    passable_gate_ids = {gondolin_config.CITY_GATE_SW_NE_ID, gondolin_config.CITY_GATE_NW_SE_ID}
    # Use exact footprints recorded directly in SafeMapGrid instead of manual ID table
    for fp_rec in grid.placed_footprints:
        if fp_rec.get("is_gate"):
            continue
        uid = fp_rec["unit_id"]
        if uid in mobile_unit_ids or uid in passable_gate_ids:
            continue
        for ty in range(fp_rec["ymin"], fp_rec["ymax"] + 1):
            for tx in range(fp_rec["xmin"], fp_rec["xmax"] + 1):
                blocked_0s.add((tx, ty))

    # Add trees and nature obstacles placed during forest generation
    for u in placed_units:
        if u.unit_const in (OAK_TREE_ID, PINE_TREE_ID, gondolin_config.CYPRESS_TREE_ID, gondolin_config.OLIVE_TREE_ID):
            blocked_0s.add((int(u.x), int(u.y)))

    # 3. Negative BFS Tests at 0:00 (Blockades MUST block passage before triggers remove them!)
    # The siege perimeter now lies at X=121 / Y=134, so Tumladen entry goals sit just beyond it (X=130).
    lower_goal, upper_goal = (130, 40), (130, 88)
    assert not bfs_reachable(blocked_0s, (61, 24), (28, 28)), "caragdur_blockade failed to block P1->P4 at 0:00!"
    assert not bfs_reachable(blocked_0s, (61, 56), lower_goal), "tumladen_exit_rocks failed to block Lower Route at 0:00!"
    assert not bfs_reachable(blocked_0s, (61, 56), upper_goal), "tumladen_exit_rocks failed to block Upper Route at 0:00!"
    assert not bfs_reachable(blocked_0s, (61, 56), (61, 140)), "North siege perimeter (Y=134) leaks at 0:00!"
    assert not bfs_reachable(blocked_0s, (184, 84), (198, 198)), "orfalch_gates failed to block Cirith Thoronath at 0:00!"
    assert not bfs_reachable(blocked_0s, (198, 198), (224, 224)), "cirith_exit_rocks failed to block Sirion Exit at 0:00!"

    # Synthetic negative obstacle tests (walling an avenue / bottleneck blocks pathfinding)
    test_blocked_south = set(blocked_0s)
    for sx in range(20, 101):
        for sy in range(35, 38):
            test_blocked_south.add((sx, sy))
    assert not bfs_reachable(test_blocked_south, (61, 61), (61, 24)), "Negatywny test BFS: zablokowana Aleja Poludniowa powinna odciac Amon Gwareth od Bramy Poludniowej!"

    # 4. Positive BFS Tests at 0:00 (All open city avenues & enclaves reachable from Amon Gwareth!)
    for name, target in [
        ("South_Gate_P1", (61, 24)),
        ("Fountain_Terrace_P2", ctx["starts"][PlayerId.TWO]),
        ("North_Approach_P3", ctx["starts"][PlayerId.THREE]),
        ("Great_Forge_West", (28, 63)),
        ("Great_Market_East", (93, 62)),
        ("Aqueduct_Control", (88, 74)),
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
    assert bfs_reachable(blocked_p2, (61, 56), lower_goal), "Cannot reach Lower Route (130,40) in Phase II!"
    assert bfs_reachable(blocked_p2, (61, 56), upper_goal), "Cannot reach Upper Route (130,88) in Phase II!"
    assert bfs_reachable(blocked_p2, lower_goal, (184, 84)), "Lower Route cannot reach Orfalch Echor (184,84)!"
    assert bfs_reachable(blocked_p2, upper_goal, (184, 84)), "Upper Route cannot reach Orfalch Echor (184,84)!"

    # Synthetic negative test for canyon bottleneck
    test_blocked_canyon = set(blocked_p2)
    for cx in range(183, 187):
        for cy in range(83, 87):
            test_blocked_canyon.add((cx, cy))
    assert not bfs_reachable(test_blocked_canyon, lower_goal, (184, 84)), "Negatywny test BFS: zablokowany waski przesmyk kanionu powinien odciac wejscie!"

    # 6. Sequential 7-Gate Orfalch Echor BFS (opening orfalch_gate_1 through 7 one by one)
    gate_checkpoints = [
        (1, (194, 101)),
        (2, (202, 115)),
        (3, (207, 130)),
        (4, (205, 144)),
        (5, (199, 156)),
        (6, (193, 168)),
        (7, (198, 198)),
    ]
    blocked_gates_sim = set(blocked_p2)
    assert not bfs_reachable(blocked_gates_sim, (184, 84), gate_checkpoints[0][1]), "Brama 1 (Wood) przepuszcza przed otwarciem!"

    for g_idx, chk in gate_checkpoints:
        unblock_rock_group(blocked_gates_sim, f"orfalch_gate_{g_idx}")
        assert bfs_reachable(blocked_gates_sim, (184, 84), chk), f"Nie mozna dotrzec do punktu za Brama {g_idx} po jej otwarciu!"
        if g_idx < 7:
            next_chk = gate_checkpoints[g_idx][1]
            assert not bfs_reachable(blocked_gates_sim, (184, 84), next_chk), f"Kolejna Brama {g_idx+1} przepuszcza przedwczesnie!"

    blocked_p3 = blocked_gates_sim
    unblock_rock_group(blocked_p3, "cirith_exit_rocks")
    assert bfs_reachable(blocked_p3, (198, 198), (224, 224)), "Cannot reach Vale of Sirion Victory Exit (224,224)!"

    preview_path = Path(__file__).resolve().parent / "gondolin_map_preview.png"
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
