from AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario

from horde_config import (
    INPUT_TEMPLATE,
    OUTPUT_SCENARIO,
    populate_ingame_scenario_descriptions,
)
from horde_map import build_map_and_entities
from horde_quests import setup_sanctuary_quests_and_victory
from horde_waves import setup_init_aura_and_waves


def build_horde_scenario() -> None:
    if not INPUT_TEMPLATE.exists():
        raise FileNotFoundError(f"Nie znaleziono szablonu: {INPUT_TEMPLATE}")

    scenario = AoE2DEScenario.from_file(str(INPUT_TEMPLATE))
    populate_ingame_scenario_descriptions(scenario)

    ctx = build_map_and_entities(scenario)
    setup_init_aura_and_waves(scenario, ctx)
    setup_sanctuary_quests_and_victory(scenario, ctx)

    scenario.write_to_file(str(OUTPUT_SCENARIO))
    print(f"Gotowe! Modularny scenariusz Hordy zapisano w: {OUTPUT_SCENARIO}")


if __name__ == "__main__":
    build_horde_scenario()
