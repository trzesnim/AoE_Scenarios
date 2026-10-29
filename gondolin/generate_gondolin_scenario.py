"""Main runner script to generate and validate the 4P Co-op RPG scenario: Fall of Gondolin."""

from __future__ import annotations

from pathlib import Path

from AoE2ScenarioParser.datasets.players import PlayerId
from AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario
from gondolin_config import (
    BALANCE,
    MAP_REVEALER_ID,
    MAP_SIZE,
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


def inspect_and_validate_scenario(output_path: Path) -> None:
    """Re-read the generated .aoe2scenario file and print a diagnostic report for P1-P8 and 0:00 triggers."""
    reloaded = AoE2DEScenario.from_file(str(output_path))
    um = reloaded.unit_manager
    tm = reloaded.trigger_manager
    pm = reloaded.player_manager

    print("\n" + "=" * 78)
    print(f"RAPORT DIAGNOSTYCZNY WYGENEROWANEGO PLIKU: {output_path.name}")
    print("=" * 78)
    print(f"Rozmiar mapy: {reloaded.map_manager.map_size}x{reloaded.map_manager.map_size}")
    print(f"Aktywni gracze (pm.active_players): {pm.active_players}")
    print(f"Laczna liczba triggerow: {len(tm.triggers)}")
    print("-" * 78)
    print(f"{'Gracz':<12} | {'Rola':<10} | {'Wszystkie Obiekty':<18} | {'Bez Revealerow':<16} | {'Bohaterowie'}")
    print("-" * 78)

    hero_ids = set(BALANCE["heroes"].keys())
    for p_idx in range(1, 9):
        p_enum = PlayerId(p_idx)
        p_units = um.get_player_units(p_enum)
        non_rev = [u for u in p_units if u.unit_const != MAP_REVEALER_ID]
        heroes_present = [u.unit_const for u in p_units if u.unit_const in hero_ids]
        role = "Czlowiek" if p_idx <= 4 else "AI (Wrog)"
        print(
            f"P{p_idx} ({p_enum.name:<5}) | {role:<10} | {len(p_units):<18} | {len(non_rev):<16} | {heroes_present}"
        )
        if len(non_rev) == 0:
            msg = f"[BLAD KRYTYCZNY P0] Gracz P{p_idx} ma 0 obiektow na starcie (zostanie wyeliminowany w 0:00)!"
            raise RuntimeError(msg)

    # Check enabled triggers at 0:00 for premature own_fewer_objects(quantity >= 1) on single heroes
    enabled_triggers = [t for t in tm.triggers if t.enabled]
    for trig in enabled_triggers:
        for cond in trig.conditions:
            c_type = getattr(cond, "condition_type", None)
            obj_list = getattr(cond, "object_list", -1)
            qty = getattr(cond, "quantity", -1)
            if obj_list in hero_ids and qty >= 1 and "HeroLoss" in trig.name:
                msg = (
                    f"[BLAD KRYTYCZNY P0] Trigger '{trig.name}' jest aktywny na starcie i sprawdza "
                    f"bohatera ID={obj_list} z quantity={qty} (spowoduje natychmiastowe zużycie Pieczeci)!"
                )
                raise RuntimeError(msg)

    print("-" * 78)
    print(f"[WALIDACJA OK] Triggery aktywne w 0:00 ({len(enabled_triggers)}) przeszly kontrole bezpieczenstwa.")
    print("=" * 78 + "\n")


def generate_scenario() -> None:
    """Load template.aoe2scenario from the AoE2: DE folder, build scenario, write output, and validate."""
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

    # Rule 1.2: Reset triggers, units, and map size on loaded template
    scenario.trigger_manager.triggers = []
    scenario.unit_manager.units = [[] for _ in range(9)]
    scenario.map_manager.map_size = MAP_SIZE

    populate_ingame_scenario_descriptions(scenario)
    ctx = build_map_and_entities(scenario)
    setup_init_auras_and_mechanics(scenario, ctx)
    setup_sanctuary_quests_and_victory(scenario, ctx)

    scenario.write_to_file(str(output_path))
    print(f"[OK] Wygenerowano scenariusz bezposrednio do folderu gry: {output_path.resolve()}")
    inspect_and_validate_scenario(output_path)


if __name__ == "__main__":
    generate_scenario()