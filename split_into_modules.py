import ast
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

SOURCE_FILE = Path("generate_horde_quests_scenario.py")
BACKUP_FILE = Path("generate_horde_quests_scenario_monolith.bak")

CONFIG_FUNCS = {"populate_ingame_scenario_descriptions", "find_scenario_folder"}
MAP_FUNCS_AND_CLASSES = {
    "SafeMapGrid",
    "reveal_building_center_permanent",
    "paint_natural_biome_background",
    "set_circle_terrain",
    "set_box_terrain",
    "paint_organic_forest",
    "build_rocky_cliff_ridge",
    "set_road",
    "populate_forest_trees",
    "build_fortified_pass_defenses",
    "build_balance_sanctuary",
    "spawn_resource_cluster",
    "spawn_symmetrical_player_base",
    "spawn_settlement_buildings",
}
WAVE_HELPER_FUNCS = {
    "safe_call",
    "safe_modify_attribute",
    "add_enemy_combat_buff",
    "set_as_objective",
    "send_highlight_chat",
    "add_player_resource",
    "research_techs",
    "add_guarded_camp_with_leash",
    "add_spawn_and_attack_effect",
    "scale_comp",
}


def get_slice_text(lines: list[str], nodes: list[ast.stmt]) -> str:
    if not nodes:
        return ""
    start_line = nodes[0].lineno - 1
    end_line = nodes[-1].end_lineno
    return "\n".join(lines[start_line:end_line])


def collect_top_level_stores(nodes: list[ast.stmt]) -> set[str]:
    """Zbiera nazwy zmiennych przypisywanych na poziomie funkcji (bez wchodzenia w zagnieżdżone def/comprehension)."""
    stores: set[str] = set()

    class StoreVisitor(ast.NodeVisitor):
        def visit_Name(self, node: ast.Name):
            if isinstance(node.ctx, ast.Store):
                stores.add(node.id)

        def visit_FunctionDef(self, node: ast.FunctionDef):
            stores.add(node.name)

        def visit_ListComp(self, node: ast.ListComp):
            pass

        def visit_SetComp(self, node: ast.SetComp):
            pass

        def visit_DictComp(self, node: ast.DictComp):
            pass

        def visit_GeneratorExp(self, node: ast.GeneratorExp):
            pass

    visitor = StoreVisitor()
    for n in nodes:
        visitor.visit(n)
    return stores


def collect_all_loads(nodes: list[ast.stmt]) -> set[str]:
    """Zbiera wszystkie odczytywane nazwy zmiennych (włącznie z wnętrzem zagnieżdżonych funkcji i pętli)."""
    loads: set[str] = set()
    for n in nodes:
        for sub in ast.walk(n):
            if isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Load):
                loads.add(sub.id)
    return loads


def build_clean_imports(
    module_code: str,
    available_config_names: set[str],
    include_wave_helpers: bool = False,
) -> str:
    """Generuje posortowane alfabetycznie importy (zgodne z Ruff I001 oraz F401) tylko dla używanych symboli."""
    tree = ast.parse(module_code)
    used_names = {
        sub.id
        for sub in ast.walk(tree)
        if isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Load)
    }

    stdlib_lines = []
    if "inspect" in used_names:
        stdlib_lines.append("import inspect")
    if "math" in used_names:
        stdlib_lines.append("import math")
    if "Path" in used_names:
        stdlib_lines.append("from pathlib import Path")

    aoe_map = {
        "BuildingInfo": "from AoE2ScenarioParser.datasets.buildings import BuildingInfo",
        "OtherInfo": "from AoE2ScenarioParser.datasets.other import OtherInfo",
        "PlayerId": "from AoE2ScenarioParser.datasets.players import PlayerId",
        "TerrainId": "from AoE2ScenarioParser.datasets.terrains import TerrainId",
        "UnitInfo": "from AoE2ScenarioParser.datasets.units import UnitInfo",
        "AoE2DEScenario": "from AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario",
    }
    aoe_lines = []
    for sym, imp_line in aoe_map.items():
        if sym in used_names:
            aoe_lines.append(imp_line)

    trig_syms = [s for s in ("DiplomacyState", "Operation") if s in used_names]
    if trig_syms:
        aoe_lines.append(
            f"from AoE2ScenarioParser.datasets.trigger_lists import {', '.join(trig_syms)}"
        )
    aoe_lines.sort()

    local_lines = []
    used_cfg = sorted(
        available_config_names & used_names,
        key=lambda s: (0 if s.isupper() else (1 if s[0].isupper() else 2), s),
    )
    if used_cfg:
        joined = ",\n    ".join(used_cfg)
        local_lines.append(f"from horde_config import (\n    {joined},\n)")

    if include_wave_helpers:
        used_helpers = sorted(
            WAVE_HELPER_FUNCS & used_names,
            key=lambda s: (0 if s.isupper() else (1 if s[0].isupper() else 2), s),
        )
        if used_helpers:
            joined_h = ",\n    ".join(used_helpers)
            local_lines.append(f"from horde_waves import (\n    {joined_h},\n)")

    blocks = []
    if stdlib_lines:
        blocks.append("\n".join(stdlib_lines))
    if aoe_lines:
        blocks.append("\n".join(aoe_lines))
    if local_lines:
        blocks.append("\n".join(local_lines))

    return "\n\n".join(blocks)


def split_monolith():
    if not SOURCE_FILE.exists():
        raise FileNotFoundError(f"Nie znaleziono pliku: {SOURCE_FILE}")

    source_text = SOURCE_FILE.read_text(encoding="utf-8")
    lines = source_text.splitlines()
    tree = ast.parse(source_text)

    shutil.copy2(SOURCE_FILE, BACKUP_FILE)
    print(f"[1/6] Utworzono kopię zapasową monolitu: {BACKUP_FILE}")

    config_blocks: list[str] = []
    config_names: set[str] = set()
    map_blocks: list[str] = []
    wave_helper_blocks: list[str] = []
    main_func_node: ast.FunctionDef | None = None

    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    config_names.add(t.id)
            config_blocks.append(get_slice_text(lines, [node]))
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            if node.name in CONFIG_FUNCS:
                config_names.add(node.name)
                config_blocks.append(get_slice_text(lines, [node]))
            elif node.name in MAP_FUNCS_AND_CLASSES:
                map_blocks.append(get_slice_text(lines, [node]))
            elif node.name in WAVE_HELPER_FUNCS:
                wave_helper_blocks.append(get_slice_text(lines, [node]))
            elif node.name == "build_horde_scenario":
                main_func_node = node

    if main_func_node is None:
        raise RuntimeError(
            "Nie znaleziono funkcji build_horde_scenario() w pliku źródłowym."
        )

    # Podział wnętrza build_horde_scenario() na 3 logiczne części + ekstrakcja get_wave_definitions()
    body = main_func_node.body

    # Pomijamy otwarcie szablonu na początku i zapis pliku na końcu (trafią do głównego runnera)
    inner_stmts = [
        s
        for s in body
        if "INPUT_TEMPLATE.exists()" not in get_slice_text(lines, [s])
        and "AoE2DEScenario.from_file" not in get_slice_text(lines, [s])
        and "populate_ingame_scenario_descriptions(" not in get_slice_text(lines, [s])
        and "scenario.write_to_file" not in get_slice_text(lines, [s])
        and "Gotowe! Scenariusz Hordy" not in get_slice_text(lines, [s])
    ]

    idx_p1_end = next(
        i
        for i, s in enumerate(inner_stmts)
        if "populate_forest_trees(" in get_slice_text(lines, [s])
    )
    idx_p3_start = next(
        i
        for i, s in enumerate(inner_stmts)
        if "pad_up_box" in get_slice_text(lines, [s])
    )

    part1_stmts = inner_stmts[: idx_p1_end + 1]
    part2_raw_stmts = inner_stmts[idx_p1_end + 1 : idx_p3_start]
    part3_stmts = inner_stmts[idx_p3_start:]

    # Wydzielenie definicji fal (wave_definitions) do horde_config.py -> get_wave_definitions()
    wave_def_stmts = []
    part2_stmts = []
    for s in part2_raw_stmts:
        txt = get_slice_text(lines, [s])
        if txt.lstrip().startswith("wave_definitions =") or txt.lstrip().startswith(
            "for w_late in range("
        ):
            wave_def_stmts.append(s)
        else:
            if "total_waves = len(wave_definitions)" in txt:
                part2_stmts.append(
                    ast.parse("wave_definitions = get_wave_definitions()").body[0]
                )
            part2_stmts.append(s)

    wave_def_body_str = textwrap.dedent(get_slice_text(lines, wave_def_stmts))
    get_waves_func_str = (
        "def get_wave_definitions() -> list[tuple]:\n"
        + textwrap.indent(wave_def_body_str, "    ")
        + "\n    return wave_definitions\n"
    )
    config_blocks.append(get_waves_func_str)
    config_names.add("get_wave_definitions")

    # Automatyczna analiza zmiennych przekazywanych przez słownik `ctx` między częściami 1, 2 i 3
    stores_p1 = collect_top_level_stores(part1_stmts) - {"scenario"}
    stores_p2 = collect_top_level_stores(part2_stmts) - {"scenario"}
    loads_p2 = collect_all_loads(part2_stmts) - {"scenario", "wave_definitions"}
    loads_p3 = collect_all_loads(part3_stmts) - {"scenario"}

    exports_from_p1 = sorted(stores_p1 & (loads_p2 | loads_p3))
    inputs_to_p2 = sorted(stores_p1 & loads_p2)
    exports_from_p2 = sorted(stores_p2 & loads_p3)
    inputs_to_p3 = sorted((stores_p1 | stores_p2) & loads_p3)

    # 1. Konstrukcja funkcji build_map_and_entities(scenario) w horde_map.py
    p1_body_str = textwrap.dedent(get_slice_text(lines, part1_stmts))
    ctx_return_entries = ",\n        ".join(f'"{k}": {k}' for k in exports_from_p1)
    p1_func_str = (
        "def build_map_and_entities(scenario) -> dict:\n"
        + textwrap.indent(p1_body_str, "    ")
        + f"\n    return {{\n        {ctx_return_entries},\n    }}\n"
    )
    map_blocks.append(p1_func_str)

    # 2. Konstrukcja funkcji setup_init_aura_and_waves(scenario, ctx) w horde_waves.py
    p2_unpack_str = "\n".join(f'    {k} = ctx["{k}"]' for k in inputs_to_p2)
    p2_body_str = textwrap.indent(
        textwrap.dedent(get_slice_text(lines, part2_stmts)), "    "
    )
    p2_body_str = p2_body_str.replace(
        "    total_waves = len(wave_definitions)",
        "    wave_definitions = get_wave_definitions()\n    total_waves = len(wave_definitions)",
    )
    p2_pack_str = "\n".join(f'    ctx["{k}"] = {k}' for k in exports_from_p2)
    p2_func_str = (
        "def setup_init_aura_and_waves(scenario, ctx: dict) -> None:\n"
        f"{p2_unpack_str}\n\n"
        f"{p2_body_str}\n\n"
        f"{p2_pack_str}\n"
    )
    wave_helper_blocks.append(p2_func_str)

    # 3. Konstrukcja funkcji setup_sanctuary_quests_and_victory(scenario, ctx) w horde_quests.py
    p3_unpack_str = "\n".join(f'    {k} = ctx["{k}"]' for k in inputs_to_p3)
    p3_body_str = textwrap.indent(
        textwrap.dedent(get_slice_text(lines, part3_stmts)), "    "
    )
    p3_func_str = (
        "def setup_sanctuary_quests_and_victory(scenario, ctx: dict) -> None:\n"
        f"{p3_unpack_str}\n\n"
        f"{p3_body_str}\n"
    )

    # Złożenie i zapis 4 modułów + nowego pliku głównego
    files_to_write = {
        Path("horde_config.py"): ("\n\n\n".join(config_blocks), set(), False),
        Path("horde_map.py"): ("\n\n\n".join(map_blocks), config_names, False),
        Path("horde_waves.py"): (
            "\n\n\n".join(wave_helper_blocks),
            config_names,
            False,
        ),
        Path("horde_quests.py"): (p3_func_str, config_names, True),
    }

    for idx, (file_path, (body_code, cfg_syms, inc_wave_helpers)) in enumerate(
        files_to_write.items(), start=2
    ):
        imports_header = build_clean_imports(
            body_code, cfg_syms, include_wave_helpers=inc_wave_helpers
        )
        full_text = f"{imports_header}\n\n\n{body_code.strip()}\n"
        file_path.write_text(full_text, encoding="utf-8")
        line_cnt = len(full_text.splitlines())
        print(f"[{idx}/6] Utworzono moduł: {file_path} ({line_cnt} linii)")

    runner_code = (
        "from AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario\n\n"
        "from horde_config import (\n"
        "    INPUT_TEMPLATE,\n"
        "    OUTPUT_SCENARIO,\n"
        "    populate_ingame_scenario_descriptions,\n"
        ")\n"
        "from horde_map import build_map_and_entities\n"
        "from horde_quests import setup_sanctuary_quests_and_victory\n"
        "from horde_waves import setup_init_aura_and_waves\n\n\n"
        "def build_horde_scenario() -> None:\n"
        "    if not INPUT_TEMPLATE.exists():\n"
        '        raise FileNotFoundError(f"Nie znaleziono szablonu: {INPUT_TEMPLATE}")\n\n'
        "    scenario = AoE2DEScenario.from_file(str(INPUT_TEMPLATE))\n"
        "    populate_ingame_scenario_descriptions(scenario)\n\n"
        "    ctx = build_map_and_entities(scenario)\n"
        "    setup_init_aura_and_waves(scenario, ctx)\n"
        "    setup_sanctuary_quests_and_victory(scenario, ctx)\n\n"
        "    scenario.write_to_file(str(OUTPUT_SCENARIO))\n"
        '    print(f"Gotowe! Modularny scenariusz Hordy zapisano w: {OUTPUT_SCENARIO}")\n\n\n'
        'if __name__ == "__main__":\n'
        "    build_horde_scenario()\n"
    )
    SOURCE_FILE.write_text(runner_code, encoding="utf-8")
    print(
        f"[6/6] Zaktualizowano główny plik uruchomieniowy: {SOURCE_FILE} ({len(runner_code.splitlines())} linii)"
    )

    # Opcjonalne automatyczne formatowanie przez Ruff (jeśli jest zainstalowany w środowisku)
    ruff_bin = shutil.which("ruff")
    if ruff_bin:
        target_files = [
            "horde_config.py",
            "horde_map.py",
            "horde_waves.py",
            "horde_quests.py",
            "generate_horde_quests_scenario.py",
        ]
        subprocess.run([ruff_bin, "check", "--fix", *target_files], check=False)
        subprocess.run([ruff_bin, "format", *target_files], check=False)
        print("[Ruff] Automatycznie sformatowano i zweryfikowano wszystkie 5 plików.")


if __name__ == "__main__":
    split_monolith()
