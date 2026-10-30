"""Runnable diagnostic script reproducing audit metrics on the current Gondolin map and triggers."""

from __future__ import annotations

from enum import IntEnum
from pathlib import Path
import sys
import types
from typing import Any


def _ensure_aoe2_parser_or_mock() -> bool:
    """Return True if real AoE2ScenarioParser is installed, else register a lightweight mock for offline audit."""
    try:
        import AoE2ScenarioParser  # noqa: F401
    except ImportError:
        aoe_pkg = types.ModuleType("AoE2ScenarioParser")
        datasets_pkg = types.ModuleType("AoE2ScenarioParser.datasets")
        players_mod = types.ModuleType("AoE2ScenarioParser.datasets.players")
        terrains_mod = types.ModuleType("AoE2ScenarioParser.datasets.terrains")
        trigger_lists_mod = types.ModuleType("AoE2ScenarioParser.datasets.trigger_lists")

        class PlayerId(IntEnum):
            GAIA = 0
            ONE = 1
            TWO = 2
            THREE = 3
            FOUR = 4
            FIVE = 5
            SIX = 6
            SEVEN = 7
            EIGHT = 8

        class TerrainId(IntEnum):
            GRASS_1 = 0
            WATER_AZURE = 1
            DIRT_3 = 3
            SHALLOWS = 4
            DIRT_1 = 6
            DIRT_2 = 11
            GRASS_2 = 12
            FOREST_PINE = 19
            ROAD = 24
            ROAD_BROKEN = 25
            ROAD_FUNGUS = 38

        class Operation(IntEnum):
            ADD = 1
            SET = 2
            SUBTRACT = 3
            MULTIPLY = 4

        players_mod.PlayerId = PlayerId  # type: ignore[attr-defined]
        terrains_mod.TerrainId = TerrainId  # type: ignore[attr-defined]
        trigger_lists_mod.Operation = Operation  # type: ignore[attr-defined]
        sys.modules["AoE2ScenarioParser"] = aoe_pkg
        sys.modules["AoE2ScenarioParser.datasets"] = datasets_pkg
        sys.modules["AoE2ScenarioParser.datasets.players"] = players_mod
        sys.modules["AoE2ScenarioParser.datasets.terrains"] = terrains_mod
        sys.modules["AoE2ScenarioParser.datasets.trigger_lists"] = trigger_lists_mod
        return False
    return True


def run_audit_reproduction() -> None:
    """Execute build_map_and_entities with placement tracking to reproduce the 33,268 trees and 82 failed placements."""
    has_real_parser = _ensure_aoe2_parser_or_mock()
    import gondolin_map
    from gondolin_config import OAK_TREE_ID, PINE_TREE_ID, PlayerId

    rejected_placements: list[tuple[int, int, int, bool]] = []
    orig_can_place = gondolin_map.SafeMapGrid.can_place_footprint

    def tracked_can_place(
        self: Any,
        x: int,
        y: int,
        footprint: int = 1,
        respect_roads: bool = True,
    ) -> bool:
        ok = orig_can_place(self, x, y, footprint=footprint, respect_roads=respect_roads)
        if not ok:
            rejected_placements.append((x, y, footprint, respect_roads))
        return ok

    gondolin_map.SafeMapGrid.can_place_footprint = tracked_can_place  # type: ignore[method-assign]

    class AuditTile:
        def __init__(self) -> None:
            self.terrain_id: int = 0
            self.elevation: int = 0

    class AuditMM:
        def __init__(self) -> None:
            self.map_size: int = 240
            self.tiles = [[AuditTile() for _ in range(240)] for _ in range(240)]

        def get_tile(self, x: int, y: int) -> AuditTile:
            return self.tiles[y][x]

    class AuditUnit:
        def __init__(self, ref_id: int, player: PlayerId, unit_const: int, x: float, y: float) -> None:
            self.reference_id = ref_id
            self.player = player
            self.unit_const = unit_const
            self.x = x
            self.y = y

    class AuditUM:
        def __init__(self) -> None:
            self.units: list[AuditUnit] = []
            self._next_id: int = 1

        def add_unit(self, player: PlayerId, unit_const: int, x: float, y: float) -> AuditUnit:
            u = AuditUnit(self._next_id, player, unit_const, x, y)
            self._next_id += 1
            self.units.append(u)
            return u

    class AuditPM:
        def __init__(self) -> None:
            self.active_players: int = 8
            self.players = [None] + [types.SimpleNamespace(diplomacy=[0] * 9) for _ in range(8)]

    class AuditScenario:
        def __init__(self) -> None:
            self.map_manager = AuditMM()
            self.unit_manager = AuditUM()
            self.player_manager = AuditPM()

    scen = AuditScenario()
    ctx = gondolin_map.build_map_and_entities(scen)
    units = scen.unit_manager.units
    trees = [u for u in units if u.unit_const in (OAK_TREE_ID, PINE_TREE_ID)]

    print("=" * 76)
    print(f"RAPORT REPRODUKCJI AUDYTU MAPY (Parser zainstalowany: {has_real_parser})")
    print("=" * 76)
    print(f"1. Laczna liczba postawionych obiektow na mapie : {len(units)}")
    print(f"2. Liczba obiektow drzew (ID 349/350)          : {len(trees)} ({len(trees) / len(units) * 100:.1f}%)")
    print(f"3. Liczba odrzuconych placementow (can_place)  : {len(rejected_placements)}")
    print(f"   Pierwsze 10 odrzuconych (x, y, fp, roads)   : {rejected_placements[:10]}")

    def in_box(p_id: PlayerId, x1: int, y1: int, x2: int, y2: int) -> list[tuple[int, int, int]]:
        return [
            (u.unit_const, int(u.x), int(u.y))
            for u in units
            if u.player == p_id and x1 <= int(u.x) <= x2 and y1 <= int(u.y) <= y2
        ]

    sectors = ctx["sectors"]
    print("-" * 76)
    print("4. Obiekty stojace w 0:00 wewnatrz stref objects_in_area (przed filtracja):")
    print("   - tower_of_snow (P3):", in_box(PlayerId.THREE, *sectors["tower_of_snow"]))
    hx1, hy1, hx2, hy2 = sectors["enclave_harp"]
    print("   - enclave_harp (P3) :", in_box(PlayerId.THREE, hx1, hy1, hx2, hy2 + 6))
    fx1, fy1, fx2, fy2 = sectors["enclave_forges"]
    print("   - West_Forges (P1)  :", in_box(PlayerId.ONE, fx1, fy1, fx2 + 6, fy2))
    for rg in ctx["refugee_groups"]:
        rx, ry, rp = rg["x"], rg["y"], rg["reward_player"]
        found = in_box(rp, rx - 6, ry - 6, rx + 6, ry + 6)
        if found:
            print(f"   - {rg['id']:<12} (P{rp.value}): {found}")
    print("=" * 76)


if __name__ == "__main__":
    run_audit_reproduction()
