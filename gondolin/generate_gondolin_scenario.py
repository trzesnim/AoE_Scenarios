"""Main runner script to generate the 4P Co-op RPG scenario: Fall of Gondolin."""

from __future__ import annotations

from pathlib import Path

from AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario

from gondolin_config import MAP_SIZE, populate_ingame_scenario_descriptions
from gondolin_map import build_map_and_entities
from gondolin_mechanics import setup_init_auras_and_mechanics
from gondolin_quests import setup_sanctuary_quests_and_victory

INPUT_TEMPLATE = Path("template.aoe2scenario")
OUTPUT_SCENARIO = Path("Silmarillion_Upadek_Gondolinu_Coop.aoe2scenario")


def generate_scenario(
    template_path: Path = INPUT_TEMPLATE,
    output_path: Path = OUTPUT_SCENARIO,
) -> None:
    """Load template.aoe2scenario, build map, mechanics, quests, and write output scenario."""
    if not template_path.exists():
        msg = (
            f"Brak pliku szablonu: {template_path.resolve()}. "
            "Zapisz pusty scenariusz w edytorze AoE2: DE jako 'template.aoe2scenario' "
            "w tym samym katalogu co skrypty Pythona."
        )
        raise FileNotFoundError(msg)

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
    print(f"[OK] Wygenerowano scenariusz: {output_path.resolve()}")


if __name__ == "__main__":
    generate_scenario()
