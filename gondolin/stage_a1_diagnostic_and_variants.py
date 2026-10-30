"""Stage A1 Diagnostic & Isolated A2 Crash-Variant Builder (Preserves baseline commit 9b240dc6)."""

from __future__ import annotations

import argparse
import ast
from contextlib import contextmanager
import importlib
from pathlib import Path
from typing import Any, Iterator

BASELINE_COMMIT: str = "9b240dc6731e0690376db62e5c3c2fde6e983b58"

# Reference table of current IDs and candidate IDs to inspect in local AoE2ScenarioParser datasets
AUDIT_ID_CATALOG: dict[int, dict[str, str]] = {
    426: {"role": "HERO_TUOR_ID (aktualny)", "dataset_name": "HARALD_HARDRAADA", "status": "POTWIERDZONY_W_GRZE"},
    1066: {"role": "HERO_ROG_ID (aktualny)", "dataset_name": "YODIT", "status": "DO_WERYFIKACJI_MODEL_ZENSKI"},
    168: {"role": "HERO_ECTHELION_ID (aktualny)", "dataset_name": "THEODORIC_THE_GOTH", "status": "NIEPOTWIERDZONY_W_EDYTORZE"},
    682: {"role": "HERO_EGALMOTH_ID (aktualny - BLAD)", "dataset_name": "BAD_NEIGHBOR (Trebuszet)", "status": "POTWIERDZONY_BLAD_W_GRZE"},
    172: {"role": "HERO_GLORFINDEL_ID (aktualny - BLAD)", "dataset_name": "TAMERLANE (Konny lucznik)", "status": "POTWIERDZONY_BLAD_W_GRZE"},
    428: {"role": "HERO_DUILIN_ID (aktualny)", "dataset_name": "HROLF_THE_GANGER", "status": "NIEPOTWIERDZONA_KLASA_ATAKU"},
    1292: {"role": "HERO_IDRIL_ID (aktualny)", "dataset_name": "QUEEN", "status": "NIEPOTWIERDZONA_ANIMACJA_ATAKU"},
    636: {"role": "HERO_GALDOR_ID (aktualny)", "dataset_name": "SIEUR_BERTRAND", "status": "NIEPOTWIERDZONY_W_EDYTORZE"},
    430: {"role": "HERO_EARENDIL_ID (aktualny)", "dataset_name": "JOAN_THE_MAID", "status": "POTWIERDZONY_KOMPROMIS"},
    642: {"role": "HERO_SALGANT_ID (aktualny) / Kandydat Ranged", "dataset_name": "LORD_DE_GRAVILLE", "status": "TYMCZASOWY_KANDYDAT_TESTOWY"},
    640: {"role": "ENEMY_MAEGLIN_ID (aktualny) / Kandydat Glorfindel", "dataset_name": "LA_HIRE", "status": "TYMCZASOWY_KANDYDAT_TESTOWY"},
    532: {"role": "ENEMY_MOLE_PIKE_ID (aktualny - BLAD)", "dataset_name": "FAST_FIRE_SHIP (Statek!)", "status": "POTWIERDZONY_BLAD_KRYTYCZNY"},
    359: {"role": "Kandydat ENEMY_MOLE_PIKE_ID (A2.1)", "dataset_name": "HALBERDIER", "status": "TYMCZASOWY_KANDYDAT_TESTOWY"},
    892: {"role": "Kandydat ENEMY_MOLE_PIKE_ID (alt)", "dataset_name": "HEAVY_PIKEMAN", "status": "TYMCZASOWY_KANDYDAT_TESTOWY"},
    200: {"role": "Kandydat HERO_EGALMOTH_ID (A2.2)", "dataset_name": "ROBIN_HOOD", "status": "TYMCZASOWY_KANDYDAT_TESTOWY"},
    176: {"role": "Kandydat ENEMY_MAEGLIN_ID", "dataset_name": "MORDRED", "status": "TYMCZASOWY_KANDYDAT_TESTOWY"},
    432: {"role": "Kandydat HERO_ROG_ID (pieszy)", "dataset_name": "WILLIAM_WALLACE", "status": "TYMCZASOWY_KANDYDAT_TESTOWY"},
    648: {"role": "Kandydat HERO_ROG_ID / Galdor", "dataset_name": "GUY_JOSSELYNE", "status": "TYMCZASOWY_KANDYDAT_TESTOWY"},
    1669: {"role": "Kandydat HERO_ROG_ID (komentarz)", "dataset_name": "EDWARD_LONGSHANKS", "status": "TYMCZASOWY_KANDYDAT_TESTOWY"},
    849: {"role": "Kandydat HERO_SALGANT_ID", "dataset_name": "WILLIAM_THE_CONQUEROR", "status": "TYMCZASOWY_KANDYDAT_TESTOWY"},
}

TRACKED_SYMBOL_NAMES: tuple[str, ...] = (
    "HERO_TUOR_ID",
    "HERO_ROG_ID",
    "HERO_ECTHELION_ID",
    "HERO_EGALMOTH_ID",
    "HERO_GLORFINDEL_ID",
    "HERO_DUILIN_ID",
    "HERO_IDRIL_ID",
    "HERO_GALDOR_ID",
    "HERO_EARENDIL_ID",
    "HERO_SALGANT_ID",
    "ENEMY_MAEGLIN_ID",
    "ENEMY_MOLE_PIKE_ID",
    "ENEMY_MOLE_TRAITOR_ID",
    "ENEMY_GOTHMOG_ID",
    "ENEMY_BALROG_BOSS_ID",
    "ENEMY_IRON_DRAGON_RAM_ID",
    "ENEMY_FIRE_DRAKE_ID",
)


def query_local_parser_datasets() -> dict[int, list[str]]:
    """Query local AoE2ScenarioParser HeroInfo, UnitInfo, BuildingInfo, OtherInfo if available."""
    found: dict[int, list[str]] = {uid: [] for uid in AUDIT_ID_CATALOG}
    try:
        from AoE2ScenarioParser.datasets.buildings import BuildingInfo
        from AoE2ScenarioParser.datasets.heroes import HeroInfo
        from AoE2ScenarioParser.datasets.other import OtherInfo
        from AoE2ScenarioParser.datasets.units import UnitInfo

        for label, enum_cls in [
            ("HeroInfo", HeroInfo),
            ("UnitInfo", UnitInfo),
            ("BuildingInfo", BuildingInfo),
            ("OtherInfo", OtherInfo),
        ]:
            for item in enum_cls:
                try:
                    val_id = item.ID
                except AttributeError:
                    continue
                if val_id in found:
                    found[val_id].append(f"{label}.{item.name}")
    except ImportError:
        pass
    return found


def scan_symbol_references(base_dir: Path) -> dict[str, list[str]]:
    """Scan all 5 Python modules for every line referencing each tracked hero/unit constant."""
    modules = [
        "gondolin_config.py",
        "gondolin_map.py",
        "gondolin_mechanics.py",
        "gondolin_quests.py",
        "generate_gondolin_scenario.py",
    ]
    refs: dict[str, list[str]] = {sym: [] for sym in TRACKED_SYMBOL_NAMES}
    for mod_name in modules:
        mod_path = base_dir / mod_name
        if not mod_path.exists():
            continue
        lines_list = mod_path.read_text(encoding="utf-8").splitlines()
        for line_no, line in enumerate(lines_list, start=1):
            for sym in TRACKED_SYMBOL_NAMES:
                if sym in line:
                    refs[sym].append(f"{mod_name}:{line_no}: {line.strip()}")
    return refs


def audit_trigger_and_map_dependencies() -> dict[str, Any]:
    """Run an offline structural audit of initial placements and triggers without modifying any file."""
    import reproduce_audit_metrics

    reproduce_audit_metrics._ensure_aoe2_parser_or_mock()
    import test_stage_a_logic
    import gondolin_config
    import gondolin_map
    import gondolin_mechanics
    import gondolin_quests

    importlib.reload(gondolin_config)
    importlib.reload(gondolin_map)
    importlib.reload(gondolin_mechanics)
    importlib.reload(gondolin_quests)

    placed_units: list[Any] = []

    def record_unit(player: Any, unit_const: int, x: float, y: float) -> Any:
        u = test_stage_a_logic.types.SimpleNamespace(
            reference_id=len(placed_units) + 1,
            player=player,
            unit_const=unit_const,
            x=x,
            y=y,
        )
        placed_units.append(u)
        return u

    scen = test_stage_a_logic.types.SimpleNamespace(
        map_manager=test_stage_a_logic.types.SimpleNamespace(
            map_size=240,
            get_tile=lambda x, y: test_stage_a_logic.types.SimpleNamespace(terrain_id=0, elevation=0),
        ),
        unit_manager=test_stage_a_logic.types.SimpleNamespace(units=placed_units, add_unit=record_unit),
        player_manager=test_stage_a_logic.types.SimpleNamespace(
            active_players=8,
            players=[None] + [test_stage_a_logic.types.SimpleNamespace(diplomacy=[0] * 9) for _ in range(8)],
        ),
        trigger_manager=test_stage_a_logic.TMObj(),
    )

    ctx = gondolin_map.build_map_and_entities(scen)
    gondolin_mechanics.setup_init_auras_and_mechanics(scen, ctx)
    gondolin_quests.setup_sanctuary_quests_and_victory(scen, ctx)

    trigs = scen.trigger_manager.triggers
    audited_ids = set(AUDIT_ID_CATALOG.keys())

    map_counts: dict[int, list[tuple[int, int, int]]] = {}
    for u in placed_units:
        if u.unit_const in audited_ids:
            map_counts.setdefault(u.unit_const, []).append((int(u.player), int(u.x), int(u.y)))

    cond_refs: dict[int, list[str]] = {}
    eff_refs: dict[int, list[str]] = {}
    early_timers: list[tuple[int, str]] = []

    for t in trigs:
        for c in t.conditions:
            if c.condition_type == "timer" and t.enabled and c.kwargs.get("timer", 999) <= 60:
                early_timers.append((c.kwargs["timer"], t.name))
            oid = c.kwargs.get("object_list", -1)
            if oid in audited_ids:
                cond_refs.setdefault(oid, []).append(f"{t.name} ({c.condition_type})")
        for e in t.effects:
            oid = e.kwargs.get("object_list_unit_id", -1)
            if oid in audited_ids:
                eff_refs.setdefault(oid, []).append(f"{t.name} ({e.effect_type})")

    return {
        "map_counts": map_counts,
        "cond_refs": cond_refs,
        "eff_refs": eff_refs,
        "early_timers": sorted(early_timers),
        "total_units": len(placed_units),
        "total_triggers": len(trigs),
    }


def print_diagnostic_report(base_dir: Path) -> None:
    """Print the complete Stage A1 diagnostic report."""
    dataset_matches = query_local_parser_datasets()
    sym_refs = scan_symbol_references(base_dir)
    dep_info = audit_trigger_and_map_dependencies()

    print("=" * 88)
    print(f"RAPORT DIAGNOSTYCZNY ETAPU A1 (Commit bazowy: {BASELINE_COMMIT})")
    print("=" * 88)
    print("1. TABELA IDENTYFIKATOROW (POTWIERDZONE / NIEPOTWIERDZONE / TYMCZASOWE KANDYDATY):")
    print("-" * 88)
    print(f"{'ID':<6} | {'Rola w scenariuszu':<38} | {'HeroInfo/UnitInfo':<24} | {'Status'}")
    print("-" * 88)
    for uid, meta in sorted(AUDIT_ID_CATALOG.items()):
        local_names = ", ".join(dataset_matches.get(uid, [])) or meta["dataset_name"]
        print(f"{uid:<6} | {meta['role']:<38} | {local_names:<24} | {meta['status']}")

    print("-" * 88)
    print("2. WYSTAPIENIA TESTOWANYCH ID NA MAPIE W 0:00 (player, x, y):")
    print("-" * 88)
    for uid, coords in sorted(dep_info["map_counts"].items()):
        role = AUDIT_ID_CATALOG[uid]["role"]
        print(f"  ID {uid:<4} ({role}): {len(coords)} szt. -> {coords}")

    print("-" * 88)
    print("3. TRIGGERY STARTOWE Z TIMEREM <= 60s (ISTOTNE DLA DIAGNOZY CRASHA 0:12 I CISZY 0:50):")
    print("-" * 88)
    for tm_val, t_name in dep_info["early_timers"]:
        print(f"  t = {tm_val:>2}s -> {t_name}")

    print("-" * 88)
    print("4. ZALEZNOSCI W WARUNKACH I EFEKTACH TRIGGEROW PER ID:")
    print("-" * 88)
    for uid in sorted(AUDIT_ID_CATALOG.keys()):
        c_list = dep_info["cond_refs"].get(uid, [])
        e_list = dep_info["eff_refs"].get(uid, [])
        if c_list or e_list:
            print(f"  ID {uid:<4} ({AUDIT_ID_CATALOG[uid]['role']}):")
            print(f"    - Warunki ({len(c_list)}): {c_list[:6]} {'...' if len(c_list) > 6 else ''}")
            print(f"    - Efekty  ({len(e_list)}): {e_list[:6]} {'...' if len(e_list) > 6 else ''}")

    print("-" * 88)
    print("5. REFERENCJE SYMBOLI W KODZIE ZRODLOWYM (LICZBA WYSTAPIEN W 5 PLIKACH):")
    print("-" * 88)
    for sym, ref_lines in sym_refs.items():
        print(f"  {sym:<28}: {len(ref_lines):>2} wystapien")
    print("=" * 88)


A2_VARIANTS: dict[str, dict[str, Any]] = {
    "baseline": {
        "output": "Gondolin_A2_0_Baseline.aoe2scenario",
        "desc": "Niezmieniony stan bazowy (commit 9b240dc6) - do potwierdzenia powtarzalnosci crasha.",
        "config_replacements": [],
        "quests_replacements": [],
        "mechanics_replacements": [],
    },
    "a2_1_pike": {
        "output": "Gondolin_A2_1_NoShips_Pike359.aoe2scenario",
        "desc": "Tylko zamiana ENEMY_MOLE_PIKE_ID: 532 (Fast Fire Ship) -> 359 (Halberdier). [TYMCZASOWY KANDYDAT]",
        "config_replacements": [
            ("ENEMY_MOLE_PIKE_ID: int = 532", "ENEMY_MOLE_PIKE_ID: int = 359"),
        ],
        "quests_replacements": [],
        "mechanics_replacements": [],
    },
    "a2_2_egalmoth": {
        "output": "Gondolin_A2_2_NoTrebuchet_Egalmoth200.aoe2scenario",
        "desc": "Tylko zamiana HERO_EGALMOTH_ID: 682 (Bad Neighbor Trebuchet) -> 200 (Robin Hood). [TYMCZASOWY KANDYDAT]",
        "config_replacements": [
            ("HERO_EGALMOTH_ID: int = 682", "HERO_EGALMOTH_ID: int = 200"),
        ],
        "quests_replacements": [],
        "mechanics_replacements": [],
    },
    "a2_3_no_maeglin_10s": {
        "output": "Gondolin_A2_3_DisableMaeglin10s.aoe2scenario",
        "desc": "Tylko wylaczenie spawnu Maeglina i 8 zdrajcow P8 w 0:10 (P1_Spawn_Maeglin_Traitors enabled=False).",
        "config_replacements": [],
        "quests_replacements": [
            ('name="P1_Spawn_Maeglin_Traitors",\n        enabled=True,', 'name="P1_Spawn_Maeglin_Traitors",\n        enabled=False,'),
        ],
        "mechanics_replacements": [],
    },
    "a2_4_no_p6_15s": {
        "output": "Gondolin_A2_4_DisableP6Dragons15s.aoe2scenario",
        "desc": "Tylko wylaczenie spawnu P6 Zelaznych Smokow w 0:15 (P6_Spawn_Iron_Dragons_Phase1 enabled=False).",
        "config_replacements": [],
        "quests_replacements": [],
        "mechanics_replacements": [
            ('name="P6_Spawn_Iron_Dragons_Phase1",\n        enabled=True,', 'name="P6_Spawn_Iron_Dragons_Phase1",\n        enabled=False,'),
        ],
    },
    "a2_12_pike_and_egalmoth": {
        "output": "Gondolin_A2_12_Pike359_And_Egalmoth200.aoe2scenario",
        "desc": "Kombinacja parowa A2.1 + A2.2: ENEMY_MOLE_PIKE_ID=359 oraz HERO_EGALMOTH_ID=200.",
        "config_replacements": [
            ("ENEMY_MOLE_PIKE_ID: int = 532", "ENEMY_MOLE_PIKE_ID: int = 359"),
            ("HERO_EGALMOTH_ID: int = 682", "HERO_EGALMOTH_ID: int = 200"),
        ],
        "quests_replacements": [],
        "mechanics_replacements": [],
    },
    "a2_5_all_temp_ids": {
        "output": "Gondolin_A2_5_AllTempHeroAndUnitIDs.aoe2scenario",
        "desc": "Wszystkie tymczasowe korekty ID (Pike=359, Egalmoth=200, Glorfindel=640, Maeglin=176, Rog=432, Duilin=642, Salgant=849).",
        "config_replacements": [
            ("ENEMY_MOLE_PIKE_ID: int = 532", "ENEMY_MOLE_PIKE_ID: int = 359"),
            ("HERO_EGALMOTH_ID: int = 682", "HERO_EGALMOTH_ID: int = 200"),
            ("HERO_GLORFINDEL_ID: int = 172", "HERO_GLORFINDEL_ID: int = 640"),
            ("ENEMY_MAEGLIN_ID: int = 640", "ENEMY_MAEGLIN_ID: int = 176"),
            ("HERO_ROG_ID: int = 1066", "HERO_ROG_ID: int = 432"),
            ("HERO_DUILIN_ID: int = 428", "HERO_DUILIN_ID: int = 642"),
            ("HERO_SALGANT_ID: int = 642", "HERO_SALGANT_ID: int = 849"),
        ],
        "quests_replacements": [],
        "mechanics_replacements": [],
    },
}


@contextmanager
def temporary_file_patches(base_dir: Path, variant_cfg: dict[str, Any]) -> Iterator[None]:
    """Temporarily patch source files for variant generation and restore exact baseline on exit."""
    target_files = ["gondolin_config.py", "gondolin_quests.py", "gondolin_mechanics.py"]
    originals: dict[Path, str] = {}
    for fname in target_files:
        fpath = base_dir / fname
        originals[fpath] = fpath.read_text(encoding="utf-8")

    try:
        for file_key, fname in [
            ("config_replacements", "gondolin_config.py"),
            ("quests_replacements", "gondolin_quests.py"),
            ("mechanics_replacements", "gondolin_mechanics.py"),
        ]:
            fpath = base_dir / fname
            text = originals[fpath]
            for old_str, new_str in variant_cfg[file_key]:
                if old_str not in text:
                    msg = f"[BLAD WARIANTU] Nie znaleziono wzorca '{old_str}' w pliku {fname}!"
                    raise RuntimeError(msg)
                text = text.replace(old_str, new_str, 1)
            ast.parse(text)
            fpath.write_text(text, encoding="utf-8")
        yield
    finally:
        for fpath, orig_content in originals.items():
            fpath.write_text(orig_content, encoding="utf-8")


def build_a2_variants(base_dir: Path, selected_variants: list[str]) -> None:
    """Build selected A2 .aoe2scenario files into the AoE2: DE scenario folder while preserving baseline code."""
    import generate_gondolin_scenario
    import gondolin_config
    import gondolin_map
    import gondolin_mechanics
    import gondolin_quests

    for v_key in selected_variants:
        if v_key not in A2_VARIANTS:
            msg = f"Nieznany wariant: {v_key}. Dostepne: {list(A2_VARIANTS.keys())}"
            raise ValueError(msg)
        v_cfg = A2_VARIANTS[v_key]
        print("=" * 88)
        print(f"[BUDOWANIE WARIANTU A2: {v_key}] -> {v_cfg['output']}")
        print(f"Opis: {v_cfg['desc']}")
        print("=" * 88)

        with temporary_file_patches(base_dir, v_cfg):
            importlib.reload(gondolin_config)
            importlib.reload(gondolin_map)
            importlib.reload(gondolin_mechanics)
            importlib.reload(gondolin_quests)
            importlib.reload(generate_gondolin_scenario)

            generate_gondolin_scenario.OUTPUT_FILENAME = v_cfg["output"]
            generate_gondolin_scenario.generate_scenario()

    importlib.reload(gondolin_config)
    importlib.reload(gondolin_map)
    importlib.reload(gondolin_mechanics)
    importlib.reload(gondolin_quests)
    print("[OK] Pliki zrodlowe repozytorium przywrocone do 100% zgodnosci z commitem bazowym.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Etap A1: Diagnostyka ID bohaterow/jednostek oraz generator odizolowanych wariantow A2."
    )
    parser.add_argument(
        "--build-variant",
        nargs="*",
        choices=[*A2_VARIANTS.keys(), "all"],
        help="Wygeneruj wskazane pliki .aoe2scenario dla eksperymentu A2.",
    )
    args = parser.parse_args()
    base_dir = Path(__file__).parent

    print_diagnostic_report(base_dir)

    if args.build_variant:
        targets = list(A2_VARIANTS.keys()) if "all" in args.build_variant else args.build_variant
        build_a2_variants(base_dir, targets)


if __name__ == "__main__":
    main()
