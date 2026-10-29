"""Main runner script to generate the 4P Co-op RPG scenario: Fall of Gondolin."""

from __future__ import annotations

from pathlib import Path

from AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario
from gondolin_config import MAP_SIZE, populate_ingame_scenario_descriptions
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


def generate_scenario() -> None:
    """Load template.aoe2scenario from the AoE2: DE folder, build scenario, and write output there."""
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
    print(
        f"[OK] Wygenerowano scenariusz bezposrednio do folderu gry: {output_path.resolve()}"
    )


if __name__ == "__main__":
    generate_scenario()
