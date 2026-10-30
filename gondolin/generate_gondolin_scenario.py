"""Main runner script to generate and validate the 4P Co-op RPG scenario: Fall of Gondolin."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from AoE2ScenarioParser.datasets.players import PlayerId
from AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario
from gondolin_config import (
    BALANCE,
    MAP_REVEALER_ID,
    MAP_SIZE,
    OAK_TREE_ID,
    PINE_TREE_ID,
    populate_ingame_scenario_descriptions,
)
from gondolin_map import build_map_and_entities
from gondolin_mechanics import setup_init_auras_and_mechanics
from gondolin_quests import setup_sanctuary_quests_and_victory

TEMPLATE_FILENAME: str = "template.aoe2scenario"
OUTPUT_FILENAME: str = "Silmarillion_Upadek_Gondolinu_Coop.aoe2scenario"


def find_scenario_folder() -> Path:
    """Locate the AoE2: DE scenario folder containing template.aoe2scenario, or fallback to script dir."""
    aoe_base = Path.home() / "Games" / "Age of Empires 2 DE"
    if aoe_base.exists():
        for folder in aoe_base.glob("*/resources/_common/scenario"):
            if (folder / TEMPLATE_FILENAME).exists():
                return folder
        for folder in aoe_base.glob("*/resources/_common/scenario"):
            if folder.parent.parent.parent.name != "0":
                return folder
    return Path(__file__).parent


def inspect_and_validate_scenario(output_path: Path, ctx: dict[str, Any] | None = None) -> None:
    """Re-read the generated .aoe2scenario file and validate P1-P8, diplomacy, triggers, and object budgets."""
    reloaded = AoE2DEScenario.from_file(str(output_path))
    um = reloaded.unit_manager
    tm = reloaded.trigger_manager
    pm = reloaded.player_manager

    if ctx is not None:
        failed = ctx["grid"].failed_placements
        if failed:
            msg = f"[BLAD KRYTYCZNY SIATKI] Wykryto odrzucone placementy ({len(failed)}): {failed[:5]}"
            raise RuntimeError(msg)

    gaia_units = um.get_player_units(PlayerId.GAIA)
    tree_count = sum(1 for u in gaia_units if u.unit_const in (OAK_TREE_ID, PINE_TREE_ID))

    print("\n" + "=" * 82)
    print(f"RAPORT WALIDACJI INTEGRACYJNEJ PLIKU: {output_path.name}")
    print("=" * 82)
    print(f"Rozmiar mapy: {reloaded.map_manager.map_size}x{reloaded.map_manager.map_size} | Aktywni gracze: {pm.active_players}")
    print(f"Laczna liczba triggerow: {len(tm.triggers)} | Drzewa dekoracyjne Gaia: {tree_count}")
    print("-" * 82)
    print(f"{'Gracz':<12} | {'Rola':<10} | {'Wszystkie':<10} | {'Bez Revealerow':<15} | {'Bohaterowie'}")
    print("-" * 82)

    hero_ids = set(BALANCE["heroes"].keys())
    for p_idx in range(1, 9):
        p_enum = PlayerId(p_idx)
        p_units = um.get_player_units(p_enum)
        non_rev = [u for u in p_units if u.unit_const != MAP_REVEALER_ID]
        heroes_present = [u.unit_const for u in p_units if u.unit_const in hero_ids]
        role = "Czlowiek" if p_idx <= 4 else "AI (Wrog)"
        print(
            f"P{p_idx} ({p_enum.name:<5}) | {role:<10} | {len(p_units):<10} | {len(non_rev):<15} | {heroes_present}"
        )
        if len(non_rev) == 0:
            msg = f"[BLAD KRYTYCZNY P0] Gracz P{p_idx} ma 0 obiektow na starcie!"
            raise RuntimeError(msg)

    # Validate active 0:00 triggers & ensure all objects_in_area conditions have object_list or object_type
    enabled_triggers = [t for t in tm.triggers if t.enabled]
    for trig in tm.triggers:
        for cond in trig.conditions:
            obj_list = getattr(cond, "object_list", -1)
            obj_type = getattr(cond, "object_type", -1)
            qty = getattr(cond, "quantity", -1)
            if trig.enabled and obj_list in hero_ids and qty >= 1 and "HeroLoss" in trig.name:
                msg = f"[BLAD KRYTYCZNY P0] Trigger '{trig.name}' ma quantity={qty} dla bohatera na starcie!"
                raise RuntimeError(msg)
            if "objects_in_area" in str(getattr(cond, "condition_type", "")).lower():
                if obj_list == -1 and obj_type == -1:
                    msg = f"[BLAD KRYTYCZNY P0] Trigger '{trig.name}' ma niefiltrowane objects_in_area!"
                    raise RuntimeError(msg)

    print("-" * 82)
    print(f"[WALIDACJA OK] 0 odrzuconych placementow, {len(enabled_triggers)} triggerow startowych bezpiecznych.")
    print("=" * 82 + "\n")


def generate_scenario() -> None:
    """Load template.aoe2scenario, build Gondolin map/mechanics/quests, write output, and validate."""
    scenario_folder = find_scenario_folder()
    template_path = scenario_folder / TEMPLATE_FILENAME
    if not template_path.exists():
        local_fallback = Path(__file__).parent / TEMPLATE_FILENAME
        if local_fallback.exists():
            template_path = local_fallback
        else:
            msg = (
                f"Brak pliku szablonu: {template_path.resolve()}. "
                "Zapisz pusty scenariusz w edytorze AoE2: DE jako 'template.aoe2scenario'."
            )
            raise FileNotFoundError(msg)

    output_path = scenario_folder / OUTPUT_FILENAME

    print(f"[INFO] Wczytywanie szablonu z: {template_path.resolve()}")
    scenario = AoE2DEScenario.from_file(str(template_path))

    scenario.trigger_manager.triggers = []
    scenario.unit_manager.units = [[] for _ in range(9)]
    scenario.map_manager.map_size = MAP_SIZE

    populate_ingame_scenario_descriptions(scenario)
    ctx = build_map_and_entities(scenario)
    setup_init_auras_and_mechanics(scenario, ctx)
    setup_sanctuary_quests_and_victory(scenario, ctx)

    scenario.write_to_file(str(output_path))
    print(f"[OK] Wygenerowano scenariusz bezposrednio do folderu gry: {output_path.resolve()}")
    inspect_and_validate_scenario(output_path, ctx=ctx)


if __name__ == "__main__":
    generate_scenario()
