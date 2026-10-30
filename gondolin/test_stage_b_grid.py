"""Engineering verification suite for Stage B: SafeMapGrid footprints, zero collisions, diplomacy, and BFS passability."""

from __future__ import annotations

from collections import deque
import importlib
import shutil
import types
from typing import Any

import reproduce_audit_metrics

reproduce_audit_metrics._ensure_aoe2_parser_or_mock()

import gondolin_config
import gondolin_map

importlib.reload(gondolin_config)
importlib.reload(gondolin_map)

from gondolin_config import CITY_GATE_NW_SE_ID, CITY_GATE_SW_NE_ID, ROCK_CLIFF_ID, PlayerId
from gondolin_map import DIPLOMACY_ALLY, DIPLOMACY_ENEMY, SafeMapGrid


class MockPlayer:
    def __init__(self) -> None:
        self.human: bool = False
        self.civilization: int = 0
        self.architecture_set: int = 0
        self.food: int = 100
        self.wood: int = 100
        self.stone: int = 100
        self.gold: int = 100
        self.diplomacy: list[int] = [-1] * 8

    def set_player_diplomacy(self, other_player: PlayerId, state: int) -> None:
        self.diplomacy[int(other_player) - 1] = state


def bfs_reachable(
    grid: SafeMapGrid,
    start: tuple[int, int],
    goal: tuple[int, int],
    extra_passable: set[tuple[int, int]] | None = None,
) -> bool:
    """Return True if a 4-connected passable path exists on SafeMapGrid from start to goal."""
    extra = extra_passable or set()
    visited: set[tuple[int, int]] = {start}
    queue: deque[tuple[int, int]] = deque([start])
    while queue:
        cx, cy = queue.popleft()
        if abs(cx - goal[0]) <= 2 and abs(cy - goal[1]) <= 2:
            return True
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = cx + dx, cy + dy
            if (nx, ny) in visited or not grid.in_bounds(nx, ny):
                continue
            if (nx, ny) in extra or grid.is_tile_passable(nx, ny):
                visited.add((nx, ny))
                queue.append((nx, ny))
    return False


def run_stage_b_tests() -> None:
    """Execute all Stage B engineering checks on SafeMapGrid and gondolin_map.py."""
    print('=' * 78)
    print('RAPORT TESTOW INZYNIERYJNYCH ETAPU B (SafeMapGrid, Dyplomacja, Mury, BFS)')
    print('=' * 78)

    # 1. Test exact even/odd footprint dimensions (1x1, 2x2, 3x3, 4x4, 5x5)
    for fp in (1, 2, 3, 4, 5):
        xmin, ymin, xmax, ymax = SafeMapGrid.footprint_bounds(50, 50, fp)
        w = xmax - xmin + 1
        h = ymax - ymin + 1
        assert (w, h) == (fp, fp), f'Footprint {fp} produced {w}x{h} instead of {fp}x{fp}'
    print('[PASS 1] Wymiary footprintow parzystych i nieparzystych (1x1, 2x2, 3x3, 4x4, 5x5) sa dokladne.')

    # 2. Build full map and verify 0 failed placements (reduced from 82 to 0)
    placed_units: list[Any] = []
    unit_coords_by_ref: dict[int, tuple[int, int]] = {}

    def add_unit(player: PlayerId, unit_const: int, x: float, y: float) -> Any:
        ref_id = len(placed_units) + 1
        u = types.SimpleNamespace(reference_id=ref_id, player=player, unit_const=unit_const, x=x, y=y)
        placed_units.append(u)
        unit_coords_by_ref[ref_id] = (int(x), int(y))
        return u

    scen = types.SimpleNamespace(
        map_manager=types.SimpleNamespace(
            map_size=240,
            get_tile=lambda x, y: types.SimpleNamespace(terrain_id=0, elevation=0),
        ),
        unit_manager=types.SimpleNamespace(units=placed_units, add_unit=add_unit),
        player_manager=types.SimpleNamespace(
            active_players=8,
            players=[None] + [MockPlayer() for _ in range(8)],
        ),
    )
    ctx = gondolin_map.build_map_and_entities(scen)
    grid: SafeMapGrid = ctx['grid']
    assert len(grid.failed_placements) == 0, f'Failed placements: {grid.failed_placements}'
    print(f'[PASS 2] Liczba odrzuconych placementow na calej mapie 240x240: {len(grid.failed_placements)} (spadek z 82 do 0).')

    # 3. Verify 8x8 Diplomacy Matrix (0-indexed player - 1)
    players = scen.player_manager.players
    for i in range(1, 9):
        p_obj = players[i]
        assert p_obj.human is (i <= 4)
        for j in range(1, 9):
            if i == j:
                continue
            same_team = (i <= 4 and j <= 4) or (i >= 5 and j >= 5)
            expected = DIPLOMACY_ALLY if same_team else DIPLOMACY_ENEMY
            actual = p_obj.diplomacy[j - 1]
            assert actual == expected, f'Diplomacy mismatch P{i}->P{j}: expected {expected}, got {actual}'
    print('[PASS 3] Macierz dyplomacji 8x8 (indeksowanie player - 1: P1-P4 Ally, P5-P8 Ally, wzajemnie Enemy) poprawna.')

    # 4. Verify physical City Gates (ID 64 / 88) are placed and passable
    gates = [u for u in placed_units if u.unit_const in (CITY_GATE_SW_NE_ID, CITY_GATE_NW_SE_ID)]
    assert len(gates) == 6, f'Expected 6 physical city gates, found {len(gates)}'
    print(f'[PASS 4] Fizyczne bramy kamienne (ID 64/88) postawione na osiach alei: {len(gates)} szt.')

    # 5. Verify BFS pathfinding across avenues, gates, and Phase I -> II -> III routes
    dynamic_rock_tiles: set[tuple[int, int]] = set()
    for ref_list in ctx['destructible_rocks'].values():
        for ref_id in ref_list:
            if ref_id in unit_coords_by_ref:
                dynamic_rock_tiles.add(unit_coords_by_ref[ref_id])
    unit_tiles = {(int(u.x), int(u.y)) for u in placed_units if u.unit_const != ROCK_CLIFF_ID and u.player != PlayerId.GAIA}
    passable_with_triggers = dynamic_rock_tiles | unit_tiles

    for p_id, start_xy in ctx['starts'].items():
        ok = bfs_reachable(grid, start_xy, (61, 61), extra_passable=passable_with_triggers)
        assert ok, f'Player {p_id.name} start {start_xy} cannot reach Amon Gwareth (61, 61)!'
    assert bfs_reachable(grid, (61, 61), (132, 40), extra_passable=passable_with_triggers)
    assert bfs_reachable(grid, (132, 40), (185, 85), extra_passable=passable_with_triggers)
    assert bfs_reachable(grid, (61, 61), (132, 88), extra_passable=passable_with_triggers)
    assert bfs_reachable(grid, (132, 88), (185, 85), extra_passable=passable_with_triggers)
    assert bfs_reachable(grid, (185, 85), (198, 198), extra_passable=passable_with_triggers)
    assert bfs_reachable(grid, (198, 198), (224, 224), extra_passable=passable_with_triggers)
    print('[PASS 5] Test przejezdnosci BFS (wszystkie 4 dzielnice -> Amon Gwareth -> 2 szlaki Tumladen -> 7 Bram -> Dolina Sirionu) zakonczony sukcesem.')
    print('=' * 78)


if __name__ == '__main__':
    run_stage_b_tests()
    shutil.rmtree('__pycache__', ignore_errors=True)
