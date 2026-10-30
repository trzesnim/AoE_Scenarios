"""Stage A1/A2-bis Diagnostic & In-Memory Variant Builder (Zero disk writes to repo .py files)."""

from __future__ import annotations

import argparse
import ast
from contextlib import contextmanager
import hashlib
import importlib
from pathlib import Path
import subprocess
from typing import Any, Iterator

BASELINE_COMMIT: str = "9b240dc6731e0690376db62e5c3c2fde6e983b58"
ALLOWED_COMMITS: set[str] = {
    "9b240dc6731e0690376db62e5c3c2fde6e983b58",
    "44464d059550f507eb0172504b95f5997191c441",
    "44d0943ed4bf4c459bed92e318a7b5ef03dc13d6",
}
CORE_MODULES: tuple[str, ...] = (
    "gondolin_config.py",
    "gondolin_map.py",
    "gondolin_mechanics.py",
    "gondolin_quests.py",
    "generate_gondolin_scenario.py",
)

# Genie .dat dead_unit links for base units in UnitInfo (base_unit_id -> (dead_unit_id, base_unit_name))
KNOWN_GENIE_DEAD_UNIT_LINKS: dict[int, tuple[int, str]] = {
    692: (693, "BERSERK"),
    1123: (1124, "KARAMBIT_WARRIOR"),
    1129: (1130, "RATTAN_ARCHER"),
    755: (756, "TARKHAN"),
    866: (867, "GENOESE_CROSSBOWMAN"),
}

# Corrected classification of audited IDs (Facts from UnitInfo/HeroInfo/ProjectileInfo/.dat vs Editor checks)
AUDIT_ID_CATALOG: dict[int, dict[str, str]] = {
    # Confirmed Dead Objects / Projectiles in current gondolin_config.py
    693: {"const": "UNIT_WING_GUARD_ID", "true_identity": "BERSERK_DEAD (dead_unit dla Berserk 692)", "target": "694 (Elite Berserk)", "category": "OBIEKT_ZWLOK"},
    1124: {"const": "ENEMY_ORC_INFANTRY_ID", "true_identity": "KARAMBIT_DEAD (dead_unit dla Karambit 1123)", "target": "1125 (Elite Karambit)", "category": "OBIEKT_ZWLOK"},
    1130: {"const": "UNIT_ARCH_RATTAN_ID", "true_identity": "RATTAN_ARCHER_DEAD (dead_unit dla Rattan 1129)", "target": "1131 (Elite Rattan Archer)", "category": "OBIEKT_ZWLOK"},
    756: {"const": "ENEMY_WARG_RIDER_ID", "true_identity": "TARKHAN_DEAD (dead_unit dla Tarkhan 755)", "target": "757 (Test usuniecia ID zwlok; model do decyzji)", "category": "OBIEKT_ZWLOK"},
    469: {"const": "UNIT_SWALLOW_SNIPER_ID", "true_identity": "ProjectileInfo.TREBUCHET_FIRE (Pocisk!)", "target": "868 (Elite Genoese Crossbowman)", "category": "POCISK"},
    # Confirmed Wrong Unit Type (Ship / Siege / Wrong Class) in current gondolin_config.py
    532: {"const": "ENEMY_MOLE_PIKE_ID", "true_identity": "UnitInfo.FAST_FIRE_SHIP (Statek ogniowy)", "target": "892 (Heavy Pikeman) / 358 (Pikeman)", "category": "ZYWA_JEDNOSTKA_BLAD_ROLI"},
    682: {"const": "HERO_EGALMOTH_ID", "true_identity": "HeroInfo.BAD_NEIGHBOR (Trebuszet)", "target": "200 (Robin Hood)", "category": "ZYWA_JEDNOSTKA_BLAD_ROLI"},
    172: {"const": "HERO_GLORFINDEL_ID", "true_identity": "HeroInfo.TAMERLANE (Konny lucznik)", "target": "640 (La Hire)", "category": "ZYWA_JEDNOSTKA_BLAD_KLASY"},
    # Confirmed Valid Combat Units (Do NOT replace in crash tests)
    752: {"const": "UNIT_EAGLE_VANGUARD_ID", "true_identity": "UnitInfo.ELITE_EAGLE_WARRIOR", "target": "752 (Bez zmian)", "category": "ZYWA_JEDNOSTKA"},
    1661: {"const": "UNIT_FOUNTAIN_GUARD_ID", "true_identity": "UnitInfo.ELITE_SERJEANT_DONJON", "target": "1661 lub 1659 (Porownac w Edytorze)", "category": "ZYWA_JEDNOSTKA"},
    1737: {"const": "ENEMY_BALROG_BOSS_ID", "true_identity": "UnitInfo.ELITE_URUMI_SWORDSMAN", "target": "1737 (Bez zmian)", "category": "ZYWA_JEDNOSTKA"},
    1703: {"const": "UNIT_HAMMER_SMITH_ID", "true_identity": "UnitInfo.ELITE_OBUCH", "target": "1703 (Bez zmian)", "category": "ZYWA_JEDNOSTKA"},
    1699: {"const": "UNIT_TREE_PIKE_ID", "true_identity": "UnitInfo.FLEMISH_MILITIA", "target": "1699 (Bez zmian)", "category": "ZYWA_JEDNOSTKA"},
    359: {"const": "UNIT_FOUNTAIN_HALB_ID", "true_identity": "UnitInfo.HALBERDIER (Tylko P2!)", "target": "359 (Nie uzywac dla P8!)", "category": "ZYWA_JEDNOSTKA"},
    # Heroes requiring Editor model/animation/class confirmation
    426: {"const": "HERO_TUOR_ID", "true_identity": "HeroInfo.HARALD_HARDRAADA", "target": "426 (Bez zmian)", "category": "ZYWA_JEDNOSTKA"},
    1066: {"const": "HERO_ROG_ID", "true_identity": "HeroInfo.YODIT", "target": "432 (William Wallace) / 1669 / 648", "category": "DO_WERYFIKACJI_W_EDYTORZE"},
    168: {"const": "HERO_ECTHELION_ID", "true_identity": "HeroInfo.THEODORIC_THE_GOTH", "target": "168 (Potwierdzic klase 4)", "category": "DO_WERYFIKACJI_W_EDYTORZE"},
    428: {"const": "HERO_DUILIN_ID", "true_identity": "HeroInfo.HROLF_THE_GANGER", "target": "642 (Lord de Graville) / 200", "category": "DO_WERYFIKACJI_W_EDYTORZE"},
    1292: {"const": "HERO_IDRIL_ID", "true_identity": "UnitInfo.QUEEN", "target": "1292 (Sprawdzic animacje ataku)", "category": "DO_WERYFIKACJI_W_EDYTORZE"},
    636: {"const": "HERO_GALDOR_ID", "true_identity": "HeroInfo.SIEUR_BERTRAND", "target": "636 (Sprawdzic model w Edytorze)", "category": "DO_WERYFIKACJI_W_EDYTORZE"},
    430: {"const": "HERO_EARENDIL_ID", "true_identity": "HeroInfo.JOAN_THE_MAID", "target": "430 (Bez zmian)", "category": "ZYWA_JEDNOSTKA"},
    640: {"const": "ENEMY_MAEGLIN_ID", "true_identity": "HeroInfo.LA_HIRE", "target": "176 (Mordred)", "category": "DO_WERYFIKACJI_W_EDYTORZE"},
}


def compute_core_checksums(base_dir: Path) -> dict[str, str]:
    """Compute SHA-256 checksums for all 5 core modules to guarantee zero unintended mutations."""
    sums: dict[str, str] = {}
    for fname in CORE_MODULES:
        fpath = base_dir / fname
        if fpath.exists():
            sums[fname] = hashlib.sha256(fpath.read_bytes()).hexdigest()
    return sums


def verify_git_baseline(base_dir: Path) -> dict[str, Any]:
    """Check git HEAD, uncommitted changes, and git diff against BASELINE_COMMIT for the 5 core modules."""
    info: dict[str, Any] = {
        "git_available": False,
        "head": "UNKNOWN",
        "dirty_core_files": [],
        "core_matches_baseline_commit": False,
        "diff_core_files": [],
    }
    try:
        head_proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=base_dir,
            capture_output=True,
            text=True,
            check=False,
        )
        if head_proc.returncode == 0:
            info["git_available"] = True
            info["head"] = head_proc.stdout.strip()

        st_proc = subprocess.run(
            ["git", "status", "--porcelain", "--", *CORE_MODULES],
            cwd=base_dir,
            capture_output=True,
            text=True,
            check=False,
        )
        if st_proc.returncode == 0 and st_proc.stdout.strip():
            info["dirty_core_files"] = st_proc.stdout.strip().splitlines()

        diff_proc = subprocess.run(
            ["git", "diff", "--name-only", BASELINE_COMMIT, "HEAD", "--", *CORE_MODULES],
            cwd=base_dir,
            capture_output=True,
            text=True,
            check=False,
        )
        if diff_proc.returncode == 0:
            changed = [line.strip() for line in diff_proc.stdout.splitlines() if line.strip()]
            info["diff_core_files"] = changed
            info["core_matches_baseline_commit"] = len(changed) == 0 and len(info["dirty_core_files"]) == 0
    except FileNotFoundError:
        pass
    return info


def scan_all_config_ids_against_local_datasets(
    base_dir: Path,
) -> tuple[bool, list[tuple[str, int, str, list[str]]]]:
    """Extract all *_ID constants from gondolin_config.py and classify them using UnitInfo, HeroInfo, BuildingInfo, OtherInfo, ProjectileInfo, and dead_unit links."""
    cfg_path = base_dir / "gondolin_config.py"
    tree = ast.parse(cfg_path.read_text(encoding="utf-8"))
    constants: list[tuple[str, int]] = []
    for node in tree.body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if (
                node.target.id.endswith("_ID")
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, int)
            ):
                constants.append((node.target.id, int(node.value.value)))
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if (
                    isinstance(t, ast.Name)
                    and t.id.endswith("_ID")
                    and isinstance(node.value, ast.Constant)
                    and isinstance(node.value.value, int)
                ):
                    constants.append((t.id, int(node.value.value)))

    enum_lookup: dict[int, list[str]] = {}
    dead_unit_lookup: dict[int, list[str]] = {}
    parser_available = False

    try:
        from AoE2ScenarioParser.datasets.buildings import BuildingInfo
        from AoE2ScenarioParser.datasets.heroes import HeroInfo
        from AoE2ScenarioParser.datasets.other import OtherInfo
        from AoE2ScenarioParser.datasets.projectiles import ProjectileInfo
        from AoE2ScenarioParser.datasets.units import UnitInfo

        parser_available = True
        for label, enum_cls in [
            ("UnitInfo", UnitInfo),
            ("HeroInfo", HeroInfo),
            ("BuildingInfo", BuildingInfo),
            ("OtherInfo", OtherInfo),
            ("ProjectileInfo", ProjectileInfo),
        ]:
            for item in enum_cls:
                try:
                    vid = int(item.ID)
                except (AttributeError, ValueError, TypeError):
                    continue
                enum_lookup.setdefault(vid, []).append(f"{label}.{item.name}")

                # Check if dataset item exposes dead_unit_id or dead_unit dynamically
                for dead_attr in ("dead_unit_id", "dead_unit"):
                    d_val = getattr(item, dead_attr, None)
                    if d_val is not None:
                        try:
                            d_id = int(getattr(d_val, "ID", d_val))
                            if d_id > 0:
                                dead_unit_lookup.setdefault(d_id, []).append(
                                    f"dead_unit({label}.{item.name}={vid})"
                                )
                        except (ValueError, TypeError):
                            pass

                # Also bind verified Genie .dat dead_unit links for base units present in UnitInfo
                if label == "UnitInfo" and vid in KNOWN_GENIE_DEAD_UNIT_LINKS:
                    dead_id, base_name = KNOWN_GENIE_DEAD_UNIT_LINKS[vid]
                    dead_unit_lookup.setdefault(dead_id, []).append(
                        f"dead_unit(UnitInfo.{item.name}={vid})"
                    )
    except ImportError:
        for base_id, (dead_id, base_name) in KNOWN_GENIE_DEAD_UNIT_LINKS.items():
            dead_unit_lookup.setdefault(dead_id, []).append(f"dead_unit({base_name}={base_id})")

    special_utility_ids = {837, 112, 303, 499, 817, 600, 623, 389, 349, 350, 1347, 1349}
    results: list[tuple[str, int, str, list[str]]] = []

    for cname, cid in constants:
        matches = list(enum_lookup.get(cid, []))
        dead_matches = dead_unit_lookup.get(cid, [])
        if dead_matches:
            matches.extend(dead_matches)

        # Determine category among the 6 required classes
        if dead_matches:
            category = "OBIEKT_ZWLOK"
        elif any(m.startswith("ProjectileInfo.") for m in matches) or cid == 469:
            category = "POCISK"
        elif any(m.startswith(("UnitInfo.", "HeroInfo.")) for m in matches):
            category = "ZYWA_JEDNOSTKA"
        elif any(m.startswith("BuildingInfo.") for m in matches):
            category = "BUDYNEK"
        elif any(m.startswith("OtherInfo.") for m in matches) or cid in special_utility_ids:
            category = "OBIEKT_SPECJALNY"
        else:
            category = "BRAK_DOPASOWANIA_DO_WERYFIKACJI"

        results.append((cname, cid, category, matches))

    return parser_available, results


def scan_ast_for_magic_id_literals(base_dir: Path) -> list[str]:
    """Scan AST of map, mechanics, quests, and runner for any hardcoded integer IDs in unit/object keyword args."""
    target_kw = {
        "unit_const",
        "object_list",
        "object_list_unit_id",
        "unit_id",
        "technology",
        "object_attributes",
    }
    findings: list[str] = []
    for fname in CORE_MODULES:
        if fname == "gondolin_config.py":
            continue
        fpath = base_dir / fname
        src = fpath.read_text(encoding="utf-8")
        src_lines = src.splitlines()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.keyword) and node.arg in target_kw:
                if isinstance(node.value, ast.Constant) and isinstance(node.value.value, int):
                    val = node.value.value
                    if val != -1:
                        findings.append(
                            f"{fname}:{node.lineno} ({node.arg}={val}): {src_lines[node.lineno - 1].strip()}"
                        )
    return findings


def extract_normalized_diplomacy_matrix(pm: Any) -> tuple[list[list[int]], str]:
    """Extract and normalize the 8x8 diplomacy matrix for P1..P8 (0=Ally, 1=Neutral, 3=Enemy, -1=Self)."""
    matrix: list[list[int]] = [[-1 for _ in range(8)] for _ in range(8)]
    players = getattr(pm, "players", [])
    index_scheme = "0-based (dip[0..7] -> P1..P8)"

    # Detect whether 9-element diplomacy array uses indices 1..8 (index 0=Gaia) or 0..7 (P1..P8)
    if len(players) > 1 and players[1] is not None:
        dip1 = getattr(players[1], "diplomacy", None)
        if isinstance(dip1, list) and len(dip1) >= 9:
            if dip1[4] == 0 and dip1[8] == 3:
                index_scheme = "1-based (dip[1..8] -> P1..P8, dip[0]=Gaia)"

    use_one_based = index_scheme.startswith("1-based")

    for i in range(1, 9):
        if i >= len(players) or players[i] is None:
            continue
        p_obj = players[i]
        dip = getattr(p_obj, "diplomacy", None)
        if not isinstance(dip, list):
            continue
        for j in range(1, 9):
            if i == j:
                matrix[i - 1][j - 1] = -1
                continue
            if use_one_based and len(dip) >= 9:
                val = int(dip[j])
            elif len(dip) >= 8:
                val = int(dip[j - 1])
            else:
                val = -99
            matrix[i - 1][j - 1] = val
    return matrix, index_scheme


def inspect_reloaded_scenario(
    output_path: Path,
    variant_cfg: dict[str, Any] | None = None,
) -> None:
    """Re-read the generated .aoe2scenario file and inspect triggers, normalized 8x8 diplomacy, units, heroes, and variant mutations."""
    try:
        from AoE2ScenarioParser.datasets.players import PlayerId
        from AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario
    except ImportError:
        print(
            f"[INFO] AoE2ScenarioParser niedostepny w tym srodowisku - pomijam inspekcje binarna {output_path.name}."
        )
        return

    if not output_path.exists():
        print(f"[INFO] Plik {output_path} nie istnieje - pomijam inspekcje.")
        return

    import gondolin_config

    reloaded = AoE2DEScenario.from_file(str(output_path))
    tm = reloaded.trigger_manager
    pm = reloaded.player_manager
    um = reloaded.unit_manager
    is_minimal = bool(variant_cfg and variant_cfg.get("is_minimal_probe"))

    print("\n" + "=" * 92)
    print(f"INSPEKCJA ZDESERIALIZOWANEGO PLIKU: {output_path.name}")
    print("=" * 92)
    print(
        f"Rozmiar mapy: {reloaded.map_manager.map_size}x{reloaded.map_manager.map_size} | "
        f"Aktywni gracze: {pm.active_players} | Rzeczywista liczba triggerow: {len(tm.triggers)}"
    )

    # 1. Normalized 8x8 Diplomacy Matrix & Symmetry Verification
    matrix, idx_scheme = extract_normalized_diplomacy_matrix(pm)
    label_map = {-1: "SELF", 0: "ALLY", 1: "NEUT", 3: "ENEM"}
    print("-" * 92)
    print(f"1. ZNORMALIZOWANA MACIERZ DYPLOMACJI 8x8 (P1..P8) [Schemat: {idx_scheme}]:")
    header = "      | " + " | ".join(f" P{j} " for j in range(1, 9))
    print(header)
    print("-" * len(header))
    symmetric_ok = True
    teams_ok = True
    for i in range(8):
        row_cells: list[str] = []
        for j in range(8):
            val = matrix[i][j]
            row_cells.append(f"{label_map.get(val, f'{val:>4}'):>4}")
            if i != j:
                if matrix[i][j] != matrix[j][i]:
                    symmetric_ok = False
                same_team = (i < 4 and j < 4) or (i >= 4 and j >= 4)
                expected_val = 0 if same_team else 3
                if val != expected_val:
                    teams_ok = False
        print(f"  P{i + 1}  | " + " | ".join(row_cells))
    print(
        f"Weryfikacja macierzy 8x8 -> Symetria: {'PASS' if symmetric_ok else 'FAIL'} | "
        f"Relacje Team1(P1-P4) vs Team2(P5-P8): {'PASS' if teams_ok else 'FAIL'}"
    )
    if not symmetric_ok or not teams_ok:
        msg = f"[BLAD DYPLOMACJI] Macierz 8x8 w pliku {output_path.name} jest niesymetryczna lub niezgodna z druzynami!"
        raise RuntimeError(msg)

    # 2. Unit count per player & Hero presence from current active gondolin_config
    print("-" * 92)
    print("2. LICZBA OBIEKTOW WEDLUG GRACZA I OBECNOSC BOHATEROW (Z aktualnej konfiguracji w pamieci):")
    expected_heroes = set(gondolin_config.BALANCE["heroes"].keys())
    found_heroes: set[int] = set()
    gaia_units = um.get_player_units(PlayerId.GAIA)
    print(f"  GAIA : {len(gaia_units)} obiektow")
    for p_idx in range(1, 9):
        p_enum = PlayerId(p_idx)
        p_units = um.get_player_units(p_enum)
        p_heroes = [u.unit_const for u in p_units if u.unit_const in expected_heroes]
        found_heroes.update(p_heroes)
        print(f"  P{p_idx}   : {len(p_units):>4} obiektow | Bohaterowie na mapie: {p_heroes}")

    if not is_minimal:
        missing_heroes = expected_heroes - found_heroes
        print(
            f"Weryfikacja 9 bohaterow ({sorted(expected_heroes)}): "
            f"{'PASS (Wszyscy obecni)' if not missing_heroes else f'FAIL (Brak: {missing_heroes})'}"
        )
        if missing_heroes:
            msg = f"[BLAD BOHATEROW] W pliku {output_path.name} brakuje bohaterow z aktualnej konfiguracji: {missing_heroes}"
            raise RuntimeError(msg)

    # 3. Verification of modified triggers (disable_triggers / set_trigger_timers / minimal probe)
    if variant_cfg:
        disable_list = variant_cfg.get("disable_triggers", [])
        timer_dict = variant_cfg.get("set_trigger_timers", {})
        if disable_list or timer_dict or is_minimal:
            print("-" * 92)
            print("3. STAN ZMODYFIKOWANYCH TRIGGEROW PO ODCZYCIE Z PLIKU BINARNEGO:")
            trig_by_name = {t.name: t for t in tm.triggers}
            for t_name in disable_list:
                t_obj = trig_by_name.get(t_name)
                en_val = getattr(t_obj, "enabled", None) if t_obj else None
                print(f"  - Trigger wylaczony '{t_name}': enabled={en_val} (oczekiwano False/0)")
                if t_obj is None or bool(en_val) is not False:
                    msg = f"[BLAD SERIALIZACJI] Trigger '{t_name}' nie zostal poprawnie wylaczony w pliku!"
                    raise RuntimeError(msg)
            for t_name, exp_timer in timer_dict.items():
                t_obj = trig_by_name.get(t_name)
                timers_read = [
                    getattr(c, "timer", None)
                    for c in (t_obj.conditions if t_obj else [])
                    if getattr(c, "timer", None) is not None and getattr(c, "timer", -1) >= 0
                ]
                print(
                    f"  - Trigger ze zmienionym timerem '{t_name}': enabled={getattr(t_obj, 'enabled', None)}, "
                    f"looping={getattr(t_obj, 'looping', None)}, timer={timers_read} (oczekiwano [{exp_timer}])"
                )
                if exp_timer not in timers_read:
                    msg = f"[BLAD SERIALIZACJI] Timer triggera '{t_name}' wynosi {timers_read} zamiast {exp_timer}!"
                    raise RuntimeError(msg)
            if is_minimal:
                for t_obj in tm.triggers:
                    timers_read = [getattr(c, "timer", None) for c in t_obj.conditions]
                    print(
                        f"  - Trigger sondy '{t_obj.name}': enabled={t_obj.enabled}, "
                        f"looping={t_obj.looping}, conditions_timers={timers_read}, effects={len(t_obj.effects)}"
                    )
    print("=" * 92 + "\n")


def print_diagnostic_report(base_dir: Path) -> None:
    """Print the corrected Stage A1/A2-bis diagnostic report."""
    git_info = verify_git_baseline(base_dir)
    parser_avail, cfg_ids = scan_all_config_ids_against_local_datasets(base_dir)
    magic_lits = scan_ast_for_magic_id_literals(base_dir)

    print("=" * 92)
    print(f"RAPORT DIAGNOSTYCZNY ETAPU A1 / A2-bis (Commit bazowy: {BASELINE_COMMIT})")
    print("=" * 92)
    print(
        f"Git dostepny: {git_info['git_available']} | HEAD: {git_info['head']} | "
        f"5 modulow rdzenia == BASELINE_COMMIT: {git_info['core_matches_baseline_commit']} | "
        f"Niezacommitowane zmiany rdzenia: {git_info['dirty_core_files']}"
    )
    print("-" * 92)
    print("1. SKORYGOWANA KLASYFIKACJA PODEJRZANYCH ID (UnitInfo / HeroInfo / ProjectileInfo / dead_unit):")
    print("-" * 92)
    print(f"{'ID':<6} | {'Stala w gondolin_config.py':<26} | {'Rzeczywisty obiekt w grze':<42} | {'Kategoria'}")
    print("-" * 92)
    for uid, meta in sorted(AUDIT_ID_CATALOG.items()):
        print(f"{uid:<6} | {meta['const']:<26} | {meta['true_identity']:<42} | {meta['category']}")

    print("-" * 92)
    print("2. KLASYFIKACJA WSZYSTKICH 84 STALYCH *_ID Z gondolin_config.py:")
    print("-" * 92)
    if not parser_avail:
        print(
            "  [UWAGA] Lokalne datasety AoE2ScenarioParser (UnitInfo/HeroInfo/ProjectileInfo) sa niedostepne w tym srodowisku.\n"
            "          Pelen skan enumow wykona sie automatycznie po uruchomieniu skryptu na Twoim komputerze z zainstalowanym AoE2ScenarioParser."
        )
    else:
        by_cat: dict[str, list[str]] = {}
        for cname, cid, cat, matches in cfg_ids:
            match_str = ", ".join(matches) if matches else "BRAK_W_ENUMACH"
            by_cat.setdefault(cat, []).append(f"{cname}={cid} ({match_str})")
            print(f"  {cname:<30} = {cid:>4} | {cat:<32} | {match_str}")
        print("-" * 92)
        print("Podsumowanie kategorii ID w gondolin_config.py:")
        for cat_name, items in sorted(by_cat.items()):
            print(f"  - {cat_name:<32}: {len(items):>2} szt.")

    print("-" * 92)
    print(f"3. SKAN AST NA OBECNOSC MAGIC NUMBERS W ARGUMENTACH ID (Poza config.py): {len(magic_lits)}")
    for ml in magic_lits:
        print(f"  {ml}")
    print("=" * 92)

    try:
        import generate_gondolin_scenario

        default_out = (
            generate_gondolin_scenario.find_scenario_folder()
            / generate_gondolin_scenario.OUTPUT_FILENAME
        )
        if default_out.exists():
            inspect_reloaded_scenario(default_out)
    except ImportError:
        pass


# Strictly isolated A2-bis variants (100% in-memory config & trigger mutations, 0 disk writes to .py files!)
A2_BIS_VARIANTS: dict[str, dict[str, Any]] = {
    "baseline": {
        "output": "Gondolin_A2B_0_Baseline.aoe2scenario",
        "desc": "Czysty stan bazowy (commit 9b240dc6) bez zadnych zmian.",
        "is_minimal_probe": False,
        "config_replacements": [],
        "disable_triggers": [],
        "set_trigger_timers": {},
    },
    "a2_t1_loop_timer_probe": {
        "output": "Gondolin_A2B_T1_LoopTimerProbe5s.aoe2scenario",
        "desc": "MINIMALNY SCENARIUSZ DIAGNOSTYCZNY: 1 trigger (looping=True, timer=5), +1 Czempion (ID 567) na (22,20) i +1 Zlota P1. Brak innych triggerow i AI.",
        "is_minimal_probe": True,
        "config_replacements": [],
        "disable_triggers": [],
        "set_trigger_timers": {},
    },
    "a2_b1a_693_to_694": {
        "output": "Gondolin_A2B_1a_WingGuard_693_to_694.aoe2scenario",
        "desc": "Izolacja 1 zmiennej: UNIT_WING_GUARD_ID 693 (Dead Berserk) -> 694 (Elite Berserk). Test 12 cial P1 i stabilnosci.",
        "is_minimal_probe": False,
        "config_replacements": [
            ("UNIT_WING_GUARD_ID: int = 693", "UNIT_WING_GUARD_ID: int = 694"),
        ],
        "disable_triggers": [],
        "set_trigger_timers": {},
    },
    "a2_b1b_1124_to_1125": {
        "output": "Gondolin_A2B_1b_OrcInf_1124_to_1125.aoe2scenario",
        "desc": "Izolacja 1 zmiennej: ENEMY_ORC_INFANTRY_ID 1124 (Dead Karambit) -> 1125 (Elite Karambit).",
        "is_minimal_probe": False,
        "config_replacements": [
            ("ENEMY_ORC_INFANTRY_ID: int = 1124", "ENEMY_ORC_INFANTRY_ID: int = 1125"),
        ],
        "disable_triggers": [],
        "set_trigger_timers": {},
    },
    "a2_b1c_1130_to_1131": {
        "output": "Gondolin_A2B_1c_Rattan_1130_to_1131.aoe2scenario",
        "desc": "Izolacja 1 zmiennej: UNIT_ARCH_RATTAN_ID 1130 (Dead Rattan) -> 1131 (Elite Rattan Archer).",
        "is_minimal_probe": False,
        "config_replacements": [
            ("UNIT_ARCH_RATTAN_ID: int = 1130", "UNIT_ARCH_RATTAN_ID: int = 1131"),
        ],
        "disable_triggers": [],
        "set_trigger_timers": {},
    },
    "a2_b1d_469_to_868": {
        "output": "Gondolin_A2B_1d_Swallow_469_to_868.aoe2scenario",
        "desc": "Izolacja 1 zmiennej: UNIT_SWALLOW_SNIPER_ID 469 (Trebuchet Projectile!) -> 868 (Elite Genoese Crossbowman).",
        "is_minimal_probe": False,
        "config_replacements": [
            ("UNIT_SWALLOW_SNIPER_ID: int = 469", "UNIT_SWALLOW_SNIPER_ID: int = 868"),
        ],
        "disable_triggers": [],
        "set_trigger_timers": {},
    },
    "a2_b1e_756_to_757": {
        "output": "Gondolin_A2B_1e_Warg_756_to_757.aoe2scenario",
        "desc": "Izolacja 1 zmiennej: ENEMY_WARG_RIDER_ID 756 (Dead Tarkhan) -> 757 (Test usuniecia ID zwlok; docelowy model Warg Ridera do osobnej decyzji).",
        "is_minimal_probe": False,
        "config_replacements": [
            ("ENEMY_WARG_RIDER_ID: int = 756", "ENEMY_WARG_RIDER_ID: int = 757"),
        ],
        "disable_triggers": [],
        "set_trigger_timers": {},
    },
    "a2_b1f_532_to_892": {
        "output": "Gondolin_A2B_1f_MolePike_532_to_892.aoe2scenario",
        "desc": "Izolacja 1 zmiennej: ENEMY_MOLE_PIKE_ID 532 (Fast Fire Ship) -> 892 (Heavy Pikeman - brak kolizji z 359 P2).",
        "is_minimal_probe": False,
        "config_replacements": [
            ("ENEMY_MOLE_PIKE_ID: int = 532", "ENEMY_MOLE_PIKE_ID: int = 892"),
        ],
        "disable_triggers": [],
        "set_trigger_timers": {},
    },
    "a2_b1g_682_to_200": {
        "output": "Gondolin_A2B_1g_Egalmoth_682_to_200.aoe2scenario",
        "desc": "Izolacja 1 zmiennej: HERO_EGALMOTH_ID 682 (Bad Neighbor Trebuchet) -> 200 (Robin Hood).",
        "is_minimal_probe": False,
        "config_replacements": [
            ("HERO_EGALMOTH_ID: int = 682", "HERO_EGALMOTH_ID: int = 200"),
        ],
        "disable_triggers": [],
        "set_trigger_timers": {},
    },
    "a2_b2_disable_init03s": {
        "output": "Gondolin_A2B_2_DisableInit03sStats.aoe2scenario",
        "desc": "Izolacja 1 triggera: wylaczenie Init_03s_RPG_Unit_And_Hero_Stats (0:03, 480 efektow modify_attribute).",
        "is_minimal_probe": False,
        "config_replacements": [],
        "disable_triggers": ["Init_03s_RPG_Unit_And_Hero_Stats"],
        "set_trigger_timers": {},
    },
    "a2_b3a_disable_east_z0_drop": {
        "output": "Gondolin_A2B_3a_DisableEastZ0Drop.aoe2scenario",
        "desc": "Izolacja P6_Dragon_Drop_east_avenue_Z0 (wylaczenie zrzutu w strefie, gdzie od 0:00 stoi taran P6 w 102,63).",
        "is_minimal_probe": False,
        "config_replacements": [],
        "disable_triggers": ["P6_Dragon_Drop_east_avenue_Z0"],
        "set_trigger_timers": {},
    },
    "a2_b3b_disable_all_5_drops": {
        "output": "Gondolin_A2B_3b_DisableAll5DragonDrops.aoe2scenario",
        "desc": "Wylaczenie wszystkich 5 cyklicznych triggerow P6_Dragon_Drop_* (32s), przy pozostawieniu spawnu P6 z 15s.",
        "is_minimal_probe": False,
        "config_replacements": [],
        "disable_triggers": [
            "P6_Dragon_Drop_north_avenue_Z0",
            "P6_Dragon_Drop_north_avenue_Z1",
            "P6_Dragon_Drop_north_avenue_Z2",
            "P6_Dragon_Drop_east_avenue_Z0",
            "P6_Dragon_Drop_east_avenue_Z1",
        ],
        "set_trigger_timers": {},
    },
    "a2_b3c_disable_p6_15s_spawn": {
        "output": "Gondolin_A2B_3c_DisableP6Spawn15sOnly.aoe2scenario",
        "desc": "Wylaczenie wylacznie P6_Spawn_Iron_Dragons_Phase1 (15s), przy pozostawieniu 5 triggerow P6_Dragon_Drop_*.",
        "is_minimal_probe": False,
        "config_replacements": [],
        "disable_triggers": ["P6_Spawn_Iron_Dragons_Phase1"],
        "set_trigger_timers": {},
    },
    "a2_b1_all_valid_units": {
        "output": "Gondolin_A2B_1_AllDeadAndProjectileIDsFixed.aoe2scenario",
        "desc": "Wariant kombinowany (tylko do porownania po testach pojedynczych a..g): 693->694, 1124->1125, 1130->1131, 469->868, 756->757, 532->892, 682->200.",
        "is_minimal_probe": False,
        "config_replacements": [
            ("UNIT_WING_GUARD_ID: int = 693", "UNIT_WING_GUARD_ID: int = 694"),
            ("ENEMY_ORC_INFANTRY_ID: int = 1124", "ENEMY_ORC_INFANTRY_ID: int = 1125"),
            ("UNIT_ARCH_RATTAN_ID: int = 1130", "UNIT_ARCH_RATTAN_ID: int = 1131"),
            ("UNIT_SWALLOW_SNIPER_ID: int = 469", "UNIT_SWALLOW_SNIPER_ID: int = 868"),
            ("ENEMY_WARG_RIDER_ID: int = 756", "ENEMY_WARG_RIDER_ID: int = 757"),
            ("ENEMY_MOLE_PIKE_ID: int = 532", "ENEMY_MOLE_PIKE_ID: int = 892"),
            ("HERO_EGALMOTH_ID: int = 682", "HERO_EGALMOTH_ID: int = 200"),
        ],
        "disable_triggers": [],
        "set_trigger_timers": {},
    },
}


@contextmanager
def in_memory_config_patch(base_dir: Path, config_replacements: list[tuple[str, str]]) -> Iterator[None]:
    """Patch gondolin_config in memory (0 disk writes!), reload all dependent modules (including generator), and restore on exit."""
    import sys
    import gondolin_config
    import gondolin_map
    import gondolin_mechanics
    import gondolin_quests

    orig_cfg_text = (base_dir / "gondolin_config.py").read_text(encoding="utf-8")
    patched_text = orig_cfg_text
    for old_str, new_str in config_replacements:
        if old_str not in patched_text:
            msg = f"[BLAD WARIANTU] Nie znaleziono wzorca '{old_str}' w gondolin_config.py!"
            raise RuntimeError(msg)
        patched_text = patched_text.replace(old_str, new_str, 1)

    try:
        if config_replacements:
            exec(compile(patched_text, "gondolin_config.py", "exec"), gondolin_config.__dict__)
            importlib.reload(gondolin_map)
            importlib.reload(gondolin_mechanics)
            importlib.reload(gondolin_quests)
            if "generate_gondolin_scenario" in sys.modules:
                importlib.reload(sys.modules["generate_gondolin_scenario"])
        yield
    finally:
        if config_replacements:
            exec(compile(orig_cfg_text, "gondolin_config.py", "exec"), gondolin_config.__dict__)
            importlib.reload(gondolin_map)
            importlib.reload(gondolin_mechanics)
            importlib.reload(gondolin_quests)
            if "generate_gondolin_scenario" in sys.modules:
                importlib.reload(sys.modules["generate_gondolin_scenario"])
                assert sys.modules["generate_gondolin_scenario"].BALANCE["heroes"] == gondolin_config.BALANCE["heroes"]
            assert gondolin_config.UNIT_WING_GUARD_ID == 693
            assert gondolin_config.HERO_EGALMOTH_ID == 682


def build_minimal_loop_timer_probe_scenario(scenario: Any) -> None:
    """Build a minimal standalone scenario with 1 looping=True + timer=5 trigger and 0 invalid IDs or AI combat."""
    from AoE2ScenarioParser.datasets.players import PlayerId
    from AoE2ScenarioParser.datasets.terrains import TerrainId
    import gondolin_config
    import gondolin_map
    from gondolin_mechanics import award_glory_gold, safe_call

    mm = scenario.map_manager
    um = scenario.unit_manager
    pm = scenario.player_manager
    tm = scenario.trigger_manager

    mm.map_size = gondolin_config.MAP_SIZE
    gondolin_map._configure_players_and_diplomacy(pm)

    for ty in range(gondolin_config.MAP_SIZE):
        for tx in range(gondolin_config.MAP_SIZE):
            tile = mm.get_tile(tx, ty)
            tile.terrain_id = TerrainId.GRASS_1
            tile.elevation = 2

    # Place 1 live Champion (ID 567) + 1 Map Revealer for P1 at (20, 20), plus passive buildings for P2-P8 far away
    um.add_unit(player=PlayerId.ONE, unit_const=gondolin_config.UNIT_WING_CHAMPION_ID, x=18.5, y=20.5)
    um.add_unit(player=PlayerId.ONE, unit_const=gondolin_config.MAP_REVEALER_ID, x=22.5, y=20.5)
    for ally_idx in (2, 3, 4):
        um.add_unit(
            player=PlayerId(ally_idx),
            unit_const=gondolin_config.OUTPOST_ID,
            x=15.0,
            y=40.0 + ally_idx * 5.0,
        )
    for enemy_idx in (5, 6, 7, 8):
        um.add_unit(
            player=PlayerId(enemy_idx),
            unit_const=gondolin_config.BARRACKS_ID,
            x=120.0,
            y=120.0 + enemy_idx * 6.0,
        )

    # Single diagnostic trigger: looping=True, timer=5 -> spawns 1 live Champion (567) at (22, 20) and adds +1 Gold to P1
    t_probe = tm.add_trigger(
        name="Probe_Looping_Timer_5s",
        enabled=True,
        looping=True,
    )
    safe_call(t_probe.new_condition.timer, timer=5)
    safe_call(
        t_probe.new_effect.create_object,
        source_player=PlayerId.ONE,
        object_list_unit_id=gondolin_config.UNIT_WING_CHAMPION_ID,
        location_x=22,
        location_y=20,
    )
    award_glory_gold(t_probe, 1, "[SONDA LOOP+TIMER=5s] Wykonano efekt! (+1 Zlota P1, +1 Czempion na 22,20)")


def apply_in_memory_trigger_mutations(scenario: Any, variant_cfg: dict[str, Any]) -> None:
    """Apply trigger disablement or timer overrides directly to the in-memory scenario object."""
    disable_set = set(variant_cfg.get("disable_triggers", []))
    timer_map: dict[str, int] = variant_cfg.get("set_trigger_timers", {})

    disabled_found: set[str] = set()
    timers_found: set[str] = set()

    for trig in scenario.trigger_manager.triggers:
        if trig.name in disable_set:
            trig.enabled = False
            disabled_found.add(trig.name)
        if trig.name in timer_map:
            new_t = timer_map[trig.name]
            for cond in trig.conditions:
                if hasattr(cond, "timer") and getattr(cond, "timer", None) is not None:
                    cond.timer = new_t
                    timers_found.add(trig.name)
                elif hasattr(cond, "kwargs") and "timer" in cond.kwargs:
                    cond.kwargs["timer"] = new_t
                    timers_found.add(trig.name)

    if disabled_found != disable_set:
        missing = disable_set - disabled_found
        msg = f"[BLAD TRIGGERA] Nie znaleziono triggerow do wylaczenia: {missing}"
        raise RuntimeError(msg)
    if timers_found != set(timer_map.keys()):
        missing = set(timer_map.keys()) - timers_found
        msg = f"[BLAD TIMERA] Nie znaleziono warunkow timer w triggerach: {missing}"
        raise RuntimeError(msg)


def build_a2_variants(base_dir: Path, selected_variants: list[str], ignore_git_check: bool = False) -> None:
    """Verify baseline git diff, build selected A2-bis .aoe2scenario files in memory, and inspect every output file."""
    git_info = verify_git_baseline(base_dir)
    if not ignore_git_check:
        if not git_info["git_available"]:
            msg = "[BLAD BAZOWY] Git niedostepny (uzyj --ignore-git-check, jesli uruchamiasz poza repozytorium git)."
            raise RuntimeError(msg)
        if git_info["dirty_core_files"]:
            msg = (
                f"[BLAD BAZOWY] Pliki rdzenia maja niezacommitowane zmiany: {git_info['dirty_core_files']}. "
                "Przywroc czysty stan przed budowaniem wariantow A2."
            )
            raise RuntimeError(msg)
        if not git_info["core_matches_baseline_commit"]:
            msg = (
                f"[BLAD BAZOWY] Pliki rdzenia w HEAD ({git_info['head']}) roznia sie od commita bazowego "
                f"{BASELINE_COMMIT}: {git_info['diff_core_files']}!"
            )
            raise RuntimeError(msg)

    baseline_sums = compute_core_checksums(base_dir)
    from AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario
    import generate_gondolin_scenario
    import gondolin_config
    import gondolin_map
    import gondolin_mechanics
    import gondolin_quests

    scenario_folder = generate_gondolin_scenario.find_scenario_folder()
    template_path = scenario_folder / generate_gondolin_scenario.TEMPLATE_FILENAME
    if not template_path.exists():
        local_fallback = base_dir / generate_gondolin_scenario.TEMPLATE_FILENAME
        if local_fallback.exists():
            template_path = local_fallback
        else:
            msg = f"Brak pliku szablonu: {template_path.resolve()}"
            raise FileNotFoundError(msg)

    for v_key in selected_variants:
        if v_key not in A2_BIS_VARIANTS:
            msg = f"Nieznany wariant: {v_key}. Dostepne: {list(A2_BIS_VARIANTS.keys())}"
            raise ValueError(msg)
        v_cfg = A2_BIS_VARIANTS[v_key]
        output_path = scenario_folder / v_cfg["output"]

        print("=" * 92)
        print(f"[BUDOWANIE WARIANTU A2-bis (W PAMIECI RAM): {v_key}] -> {output_path.name}")
        print(f"Opis: {v_cfg['desc']}")
        print("=" * 92)

        with in_memory_config_patch(base_dir, v_cfg["config_replacements"]):
            scenario = AoE2DEScenario.from_file(str(template_path))
            scenario.trigger_manager.triggers = []
            scenario.unit_manager.units = [[] for _ in range(9)]
            scenario.map_manager.map_size = gondolin_config.MAP_SIZE

            if v_cfg.get("is_minimal_probe"):
                build_minimal_loop_timer_probe_scenario(scenario)
                scenario.write_to_file(str(output_path))
                print(f"[OK] Wygenerowano minimalna sonde: {output_path.resolve()}")
                inspect_reloaded_scenario(output_path, variant_cfg=v_cfg)
            else:
                gondolin_config.populate_ingame_scenario_descriptions(scenario)
                ctx = gondolin_map.build_map_and_entities(scenario)
                gondolin_mechanics.setup_init_auras_and_mechanics(scenario, ctx)
                gondolin_quests.setup_sanctuary_quests_and_victory(scenario, ctx)

                apply_in_memory_trigger_mutations(scenario, v_cfg)

                scenario.write_to_file(str(output_path))
                print(f"[OK] Wygenerowano plik: {output_path.resolve()}")
                generate_gondolin_scenario.inspect_and_validate_scenario(output_path, ctx=ctx)
                inspect_reloaded_scenario(output_path, variant_cfg=v_cfg)

    final_sums = compute_core_checksums(base_dir)
    assert baseline_sums == final_sums, "Niezgodnosc SHA-256 po zakonczeniu budowania wariantow!"
    print("[OK] 0 zapisow do plikow .py na dysku; sumy kontrolne SHA-256 wszystkich 5 modulow rdzenia w 100% nienaruszone.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Etap A1/A2-bis: Diagnostyka ID, minimalna sonda looping+timer oraz generator wariantow w pamieci RAM."
    )
    parser.add_argument(
        "--build-variant",
        nargs="*",
        choices=[*A2_BIS_VARIANTS.keys(), "all"],
        help="Wygeneruj wskazane pliki .aoe2scenario dla eksperymentu A2-bis.",
    )
    parser.add_argument(
        "--ignore-git-check",
        action="store_true",
        help="Pomin blokade czystego git status i git diff wzgledem BASELINE_COMMIT.",
    )
    args = parser.parse_args()
    base_dir = Path(__file__).parent

    print_diagnostic_report(base_dir)

    if args.build_variant:
        targets = list(A2_BIS_VARIANTS.keys()) if "all" in args.build_variant else args.build_variant
        build_a2_variants(base_dir, targets, ignore_git_check=args.ignore_git_check)


if __name__ == "__main__":
    main()
