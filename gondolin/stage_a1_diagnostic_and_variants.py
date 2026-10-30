"""Stage A1/A2-bis Diagnostic & Isolated Variant Builder (Strictly preserves baseline commit 9b240dc6)."""

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
}
CORE_MODULES: tuple[str, ...] = (
    "gondolin_config.py",
    "gondolin_map.py",
    "gondolin_mechanics.py",
    "gondolin_quests.py",
    "generate_gondolin_scenario.py",
)

# Corrected classification of all audited IDs (Facts from UnitInfo/HeroInfo vs Editor checks)
AUDIT_ID_CATALOG: dict[int, dict[str, str]] = {
    # Confirmed Dead Objects / Projectiles in current gondolin_config.py
    693: {"const": "UNIT_WING_GUARD_ID", "true_identity": "BERSERK_DEAD (Zwloki Berserka!)", "target": "694 (Elite Berserk)", "category": "BLAD_OBIEKT_MARTWY"},
    1124: {"const": "ENEMY_ORC_INFANTRY_ID", "true_identity": "KARAMBIT_DEAD (Zwloki Karambita!)", "target": "1125 (Elite Karambit)", "category": "BLAD_OBIEKT_MARTWY"},
    1130: {"const": "UNIT_ARCH_RATTAN_ID", "true_identity": "RATTAN_ARCHER_DEAD (Zwloki Lucznika!)", "target": "1131 (Elite Rattan Archer)", "category": "BLAD_OBIEKT_MARTWY"},
    756: {"const": "ENEMY_WARG_RIDER_ID", "true_identity": "TARKHAN_DEAD (Zwloki Tarkhana!)", "target": "757 (Elite Tarkhan)", "category": "BLAD_OBIEKT_MARTWY"},
    469: {"const": "UNIT_SWALLOW_SNIPER_ID", "true_identity": "TREBUCHET_FIRE (Pocisk Trebusza!)", "target": "868 (Elite Genoese Crossbowman)", "category": "BLAD_POCISK"},
    # Confirmed Wrong Unit Type (Ship / Siege / Wrong Class) in current gondolin_config.py
    532: {"const": "ENEMY_MOLE_PIKE_ID", "true_identity": "FAST_FIRE_SHIP (Statek ogniowy)", "target": "892 (Heavy Pikeman) / 358 (Pikeman)", "category": "BLAD_STATEK_NA_LADZIE"},
    682: {"const": "HERO_EGALMOTH_ID", "true_identity": "BAD_NEIGHBOR (Trebuszet)", "target": "200 (Robin Hood)", "category": "BLAD_MACHINA_ZAMIAST_BOHATERA"},
    172: {"const": "HERO_GLORFINDEL_ID", "true_identity": "TAMERLANE (Konny lucznik)", "target": "640 (La Hire)", "category": "BLAD_KLASA_BOHATERA"},
    # Confirmed Valid Combat Units (Do NOT replace in crash tests)
    752: {"const": "UNIT_EAGLE_VANGUARD_ID", "true_identity": "ELITE_EAGLE_WARRIOR", "target": "752 (Bez zmian)", "category": "POPRAWNY_UNITINFO"},
    1661: {"const": "UNIT_FOUNTAIN_GUARD_ID", "true_identity": "ELITE_SERJEANT_DONJON", "target": "1661 lub 1659 (Porownac w Edytorze)", "category": "POPRAWNY_UNITINFO"},
    1737: {"const": "ENEMY_BALROG_BOSS_ID", "true_identity": "ELITE_URUMI_SWORDSMAN", "target": "1737 (Bez zmian)", "category": "POPRAWNY_UNITINFO"},
    1703: {"const": "UNIT_HAMMER_SMITH_ID", "true_identity": "ELITE_OBUCH", "target": "1703 (Bez zmian)", "category": "POPRAWNY_UNITINFO"},
    1699: {"const": "UNIT_TREE_PIKE_ID", "true_identity": "FLEMISH_MILITIA", "target": "1699 (Bez zmian)", "category": "POPRAWNY_UNITINFO"},
    359: {"const": "UNIT_FOUNTAIN_HALB_ID", "true_identity": "HALBERDIER (Tylko P2!)", "target": "359 (Nie uzywac dla P8!)", "category": "POPRAWNY_UNITINFO"},
    # Heroes requiring Editor model/animation/class confirmation
    426: {"const": "HERO_TUOR_ID", "true_identity": "HARALD_HARDRAADA", "target": "426 (Bez zmian)", "category": "POTWIERDZONY_BOHATER"},
    1066: {"const": "HERO_ROG_ID", "true_identity": "YODIT", "target": "432 (William Wallace) / 1669 / 648", "category": "WYMAGA_WERYFIKACJI_W_EDYTORZE"},
    168: {"const": "HERO_ECTHELION_ID", "true_identity": "THEODORIC_THE_GOTH", "target": "168 (Potwierdzic klase 4)", "category": "WYMAGA_WERYFIKACJI_W_EDYTORZE"},
    428: {"const": "HERO_DUILIN_ID", "true_identity": "HROLF_THE_GANGER", "target": "642 (Lord de Graville) / 200", "category": "WYMAGA_WERYFIKACJI_W_EDYTORZE"},
    1292: {"const": "HERO_IDRIL_ID", "true_identity": "QUEEN", "target": "1292 (Sprawdzic animacje ataku)", "category": "WYMAGA_WERYFIKACJI_W_EDYTORZE"},
    636: {"const": "HERO_GALDOR_ID", "true_identity": "SIEUR_BERTRAND", "target": "636 (Sprawdzic model w Edytorze)", "category": "WYMAGA_WERYFIKACJI_W_EDYTORZE"},
    430: {"const": "HERO_EARENDIL_ID", "true_identity": "JOAN_THE_MAID", "target": "430 (Bez zmian)", "category": "POTWIERDZONY_KOMPROMIS"},
    640: {"const": "ENEMY_MAEGLIN_ID", "true_identity": "LA_HIRE", "target": "176 (Mordred)", "category": "WYMAGA_WERYFIKACJI_W_EDYTORZE"},
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
    """Check git HEAD commit and working tree status for the 5 core modules."""
    info: dict[str, Any] = {"git_available": False, "head": "UNKNOWN", "dirty_core_files": []}
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
    except FileNotFoundError:
        pass
    return info


def scan_all_config_ids_against_local_datasets(base_dir: Path) -> list[tuple[str, int, list[str]]]:
    """Extract every *_ID constant from gondolin_config.py and resolve it against AoE2ScenarioParser enums."""
    cfg_path = base_dir / "gondolin_config.py"
    tree = ast.parse(cfg_path.read_text(encoding="utf-8"))
    constants: list[tuple[str, int]] = []
    for node in tree.body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if node.target.id.endswith("_ID") and isinstance(node.value, ast.Constant) and isinstance(node.value.value, int):
                constants.append((node.target.id, int(node.value.value)))
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id.endswith("_ID") and isinstance(node.value, ast.Constant) and isinstance(node.value.value, int):
                    constants.append((t.id, int(node.value.value)))

    enum_lookup: dict[int, list[str]] = {}
    try:
        from AoE2ScenarioParser.datasets.buildings import BuildingInfo
        from AoE2ScenarioParser.datasets.heroes import HeroInfo
        from AoE2ScenarioParser.datasets.other import OtherInfo
        from AoE2ScenarioParser.datasets.units import UnitInfo

        for label, enum_cls in [
            ("UnitInfo", UnitInfo),
            ("HeroInfo", HeroInfo),
            ("BuildingInfo", BuildingInfo),
            ("OtherInfo", OtherInfo),
        ]:
            for item in enum_cls:
                try:
                    vid = int(item.ID)
                except (AttributeError, ValueError, TypeError):
                    continue
                enum_lookup.setdefault(vid, []).append(f"{label}.{item.name}")
    except ImportError:
        pass

    results: list[tuple[str, int, list[str]]] = []
    for cname, cid in constants:
        matches = enum_lookup.get(cid, [])
        results.append((cname, cid, matches))
    return results


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
                        findings.append(f"{fname}:{node.lineno} ({node.arg}={val}): {src_lines[node.lineno - 1].strip()}")
    return findings


def inspect_reloaded_scenario_if_available(base_dir: Path) -> None:
    """If AoE2ScenarioParser and generated .aoe2scenario exist locally, inspect real trigger count & 8x8 diplomacy."""
    try:
        from AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario
        import generate_gondolin_scenario
    except ImportError:
        print("[INFO] AoE2ScenarioParser niedostepny w tym srodowisku - pomijam inspekcje pliku binarnego .aoe2scenario.")
        return

    scen_folder = generate_gondolin_scenario.find_scenario_folder()
    out_path = scen_folder / generate_gondolin_scenario.OUTPUT_FILENAME
    if not out_path.exists():
        print(f"[INFO] Brak wygenerowanego pliku {out_path} - uruchom najpierw generate_gondolin_scenario.py.")
        return

    reloaded = AoE2DEScenario.from_file(str(out_path))
    tm = reloaded.trigger_manager
    pm = reloaded.player_manager
    print("=" * 92)
    print(f"INSPEKCJA ZDESERIALIZOWANEGO PLIKU BINARNEGO: {out_path.name}")
    print("=" * 92)
    print(f"Rzeczywista liczba triggerow w pliku .aoe2scenario: {len(tm.triggers)}")
    print("Macierz dyplomacji 8x8 odczytana z pliku (0=Ally, 1=Neutral, 3=Enemy):")
    players = getattr(pm, "players", [])
    for i in range(1, min(9, len(players))):
        p_obj = players[i]
        dip = getattr(p_obj, "diplomacy", None)
        print(f"  P{i}: human={getattr(p_obj, 'human', None)}, civ={getattr(p_obj, 'civilization', None)}, diplomacy={dip}")


def print_diagnostic_report(base_dir: Path) -> None:
    """Print the corrected Stage A1/A2-bis diagnostic report."""
    git_info = verify_git_baseline(base_dir)
    cfg_ids = scan_all_config_ids_against_local_datasets(base_dir)
    magic_lits = scan_ast_for_magic_id_literals(base_dir)

    print("=" * 92)
    print(f"RAPORT DIAGNOSTYCZNY ETAPU A1 / A2-bis (Oczekiwany commit: {BASELINE_COMMIT})")
    print("=" * 92)
    print(f"Git dostepny: {git_info['git_available']} | HEAD: {git_info['head']} | Zmienione pliki rdzenia: {git_info['dirty_core_files']}")
    print("-" * 92)
    print("1. SKORYGOWANA KLASYFIKACJA PODEJRZANYCH ID (Zgodnie z UnitInfo / HeroInfo i danymi gry):")
    print("-" * 92)
    print(f"{'ID':<6} | {'Stala w gondolin_config.py':<26} | {'Rzeczywisty obiekt w grze':<34} | {'Kandydat do testu'}")
    print("-" * 92)
    for uid, meta in sorted(AUDIT_ID_CATALOG.items()):
        print(f"{uid:<6} | {meta['const']:<26} | {meta['true_identity']:<34} | {meta['target']}")

    print("-" * 92)
    print("2. WERYFIKACJA WSZYSTKICH STALYCH *_ID Z gondolin_config.py W LOKALNYM AoE2ScenarioParser:")
    print("-" * 92)
    unresolved: list[tuple[str, int]] = []
    for cname, cid, matches in cfg_ids:
        if not matches:
            unresolved.append((cname, cid))
        match_str = ", ".join(matches) if matches else "[BRAK W ENUMACH UnitInfo/HeroInfo/BuildingInfo/OtherInfo!]"
        print(f"  {cname:<30} = {cid:>4} -> {match_str}")
    print(f"Liczba stalych bez dopasowania w lokalnych enumach (lub gdy parser offline): {len(unresolved)}")

    print("-" * 92)
    print(f"3. SKAN AST NA OBECNOSC MAGIC NUMBERS W ARGUMENTACH ID (Poza config.py): {len(magic_lits)}")
    for ml in magic_lits:
        print(f"  {ml}")
    print("=" * 92)
    inspect_reloaded_scenario_if_available(base_dir)


# Strictly isolated A2-bis variants (1 variable per variant, no key collision with 359!)
A2_BIS_VARIANTS: dict[str, dict[str, Any]] = {
    "baseline": {
        "output": "Gondolin_A2B_0_Baseline.aoe2scenario",
        "desc": "Czysty stan bazowy (commit 9b240dc6) bez zadnych zmian.",
        "config_replacements": [],
        "quests_replacements": [],
        "mechanics_replacements": [],
    },
    "a2_t1_loop_timer_probe": {
        "output": "Gondolin_A2B_T1_LoopTimerProbe5s.aoe2scenario",
        "desc": "Test semantyki looping=True + timer=5 w P6_Dragon_Drop_east_avenue_Z0 (zmiana timera z 32 na 5s do obserwacji 0..12s).",
        "config_replacements": [],
        "quests_replacements": [],
        "mechanics_replacements": [
            ("safe_call(t_drop.new_condition.timer, timer=32)", "safe_call(t_drop.new_condition.timer, timer=5)"),
        ],
    },
    "a2_b1a_693_to_694": {
        "output": "Gondolin_A2B_1a_WingGuard_693_to_694.aoe2scenario",
        "desc": "Izolacja 1 zmiennej: UNIT_WING_GUARD_ID 693 (Dead Berserk) -> 694 (Elite Berserk). Test 12 cial P1 i stabilnosci.",
        "config_replacements": [
            ("UNIT_WING_GUARD_ID: int = 693", "UNIT_WING_GUARD_ID: int = 694"),
        ],
        "quests_replacements": [],
        "mechanics_replacements": [],
    },
    "a2_b1b_1124_to_1125": {
        "output": "Gondolin_A2B_1b_OrcInf_1124_to_1125.aoe2scenario",
        "desc": "Izolacja 1 zmiennej: ENEMY_ORC_INFANTRY_ID 1124 (Dead Karambit) -> 1125 (Elite Karambit).",
        "config_replacements": [
            ("ENEMY_ORC_INFANTRY_ID: int = 1124", "ENEMY_ORC_INFANTRY_ID: int = 1125"),
        ],
        "quests_replacements": [],
        "mechanics_replacements": [],
    },
    "a2_b1c_1130_to_1131": {
        "output": "Gondolin_A2B_1c_Rattan_1130_to_1131.aoe2scenario",
        "desc": "Izolacja 1 zmiennej: UNIT_ARCH_RATTAN_ID 1130 (Dead Rattan) -> 1131 (Elite Rattan Archer).",
        "config_replacements": [
            ("UNIT_ARCH_RATTAN_ID: int = 1130", "UNIT_ARCH_RATTAN_ID: int = 1131"),
        ],
        "quests_replacements": [],
        "mechanics_replacements": [],
    },
    "a2_b1d_469_to_868": {
        "output": "Gondolin_A2B_1d_Swallow_469_to_868.aoe2scenario",
        "desc": "Izolacja 1 zmiennej: UNIT_SWALLOW_SNIPER_ID 469 (Trebuchet Projectile!) -> 868 (Elite Genoese Crossbowman).",
        "config_replacements": [
            ("UNIT_SWALLOW_SNIPER_ID: int = 469", "UNIT_SWALLOW_SNIPER_ID: int = 868"),
        ],
        "quests_replacements": [],
        "mechanics_replacements": [],
    },
    "a2_b1e_756_to_757": {
        "output": "Gondolin_A2B_1e_Warg_756_to_757.aoe2scenario",
        "desc": "Izolacja 1 zmiennej: ENEMY_WARG_RIDER_ID 756 (Dead Tarkhan) -> 757 (Elite Tarkhan).",
        "config_replacements": [
            ("ENEMY_WARG_RIDER_ID: int = 756", "ENEMY_WARG_RIDER_ID: int = 757"),
        ],
        "quests_replacements": [],
        "mechanics_replacements": [],
    },
    "a2_b1f_532_to_892": {
        "output": "Gondolin_A2B_1f_MolePike_532_to_892.aoe2scenario",
        "desc": "Izolacja 1 zmiennej: ENEMY_MOLE_PIKE_ID 532 (Fast Fire Ship) -> 892 (Heavy Pikeman - brak kolizji z 359 P2).",
        "config_replacements": [
            ("ENEMY_MOLE_PIKE_ID: int = 532", "ENEMY_MOLE_PIKE_ID: int = 892"),
        ],
        "quests_replacements": [],
        "mechanics_replacements": [],
    },
    "a2_b1g_682_to_200": {
        "output": "Gondolin_A2B_1g_Egalmoth_682_to_200.aoe2scenario",
        "desc": "Izolacja 1 zmiennej: HERO_EGALMOTH_ID 682 (Bad Neighbor Trebuchet) -> 200 (Robin Hood).",
        "config_replacements": [
            ("HERO_EGALMOTH_ID: int = 682", "HERO_EGALMOTH_ID: int = 200"),
        ],
        "quests_replacements": [],
        "mechanics_replacements": [],
    },
    "a2_b2_disable_init03s": {
        "output": "Gondolin_A2B_2_DisableInit03sStats.aoe2scenario",
        "desc": "Izolacja 1 triggera: wylaczenie Init_03s_RPG_Unit_And_Hero_Stats (0:03, 480 efektow modify_attribute).",
        "config_replacements": [],
        "quests_replacements": [],
        "mechanics_replacements": [
            ('name="Init_03s_RPG_Unit_And_Hero_Stats",\n        enabled=True,', 'name="Init_03s_RPG_Unit_And_Hero_Stats",\n        enabled=False,'),
        ],
    },
    "a2_b3a_disable_east_z0_drop": {
        "output": "Gondolin_A2B_3a_DisableEastZ0Drop.aoe2scenario",
        "desc": "Izolacja P6_Dragon_Drop_east_avenue_Z0 (wylaczenie zrzutu w strefie, gdzie od 0:00 stoi taran P6 w 102,63).",
        "config_replacements": [],
        "quests_replacements": [],
        "mechanics_replacements": [
            ('name=f"P6_Dragon_Drop_{ave_name}_Z{idx}",\n                enabled=True,', 'name=f"P6_Dragon_Drop_{ave_name}_Z{idx}",\n                enabled=not (ave_name == "east_avenue" and idx == 0),'),
        ],
    },
    "a2_b3b_disable_all_5_drops": {
        "output": "Gondolin_A2B_3b_DisableAll5DragonDrops.aoe2scenario",
        "desc": "Wylaczenie wszystkich 5 cyklicznych triggerow P6_Dragon_Drop_* (32s), przy pozostawieniu spawnu P6 z 15s.",
        "config_replacements": [],
        "quests_replacements": [],
        "mechanics_replacements": [
            ('name=f"P6_Dragon_Drop_{ave_name}_Z{idx}",\n                enabled=True,', 'name=f"P6_Dragon_Drop_{ave_name}_Z{idx}",\n                enabled=False,'),
        ],
    },
    "a2_b3c_disable_p6_15s_spawn": {
        "output": "Gondolin_A2B_3c_DisableP6Spawn15sOnly.aoe2scenario",
        "desc": "Wylaczenie wylacznie P6_Spawn_Iron_Dragons_Phase1 (15s), przy pozostawieniu 5 triggerow P6_Dragon_Drop_*.",
        "config_replacements": [],
        "quests_replacements": [],
        "mechanics_replacements": [
            ('name="P6_Spawn_Iron_Dragons_Phase1",\n        enabled=True,', 'name="P6_Spawn_Iron_Dragons_Phase1",\n        enabled=False,'),
        ],
    },
    "a2_b1_all_valid_units": {
        "output": "Gondolin_A2B_1_AllDeadAndProjectileIDsFixed.aoe2scenario",
        "desc": "Wariant kombinowany (tylko do porownania po testach pojedynczych a..g): 693->694, 1124->1125, 1130->1131, 469->868, 756->757, 532->892, 682->200.",
        "config_replacements": [
            ("UNIT_WING_GUARD_ID: int = 693", "UNIT_WING_GUARD_ID: int = 694"),
            ("ENEMY_ORC_INFANTRY_ID: int = 1124", "ENEMY_ORC_INFANTRY_ID: int = 1125"),
            ("UNIT_ARCH_RATTAN_ID: int = 1130", "UNIT_ARCH_RATTAN_ID: int = 1131"),
            ("UNIT_SWALLOW_SNIPER_ID: int = 469", "UNIT_SWALLOW_SNIPER_ID: int = 868"),
            ("ENEMY_WARG_RIDER_ID: int = 756", "ENEMY_WARG_RIDER_ID: int = 757"),
            ("ENEMY_MOLE_PIKE_ID: int = 532", "ENEMY_MOLE_PIKE_ID: int = 892"),
            ("HERO_EGALMOTH_ID: int = 682", "HERO_EGALMOTH_ID: int = 200"),
        ],
        "quests_replacements": [],
        "mechanics_replacements": [],
    },
}


@contextmanager
def temporary_file_patches(base_dir: Path, variant_cfg: dict[str, Any]) -> Iterator[None]:
    """Temporarily patch source files with backup files (.bak) and verify SHA-256 restoration on exit."""
    target_files = ["gondolin_config.py", "gondolin_quests.py", "gondolin_mechanics.py"]
    pre_sums = compute_core_checksums(base_dir)
    originals: dict[Path, bytes] = {}
    backups: dict[Path, Path] = {}
    for fname in target_files:
        fpath = base_dir / fname
        bak_path = base_dir / f"{fname}.a2bak"
        raw = fpath.read_bytes()
        originals[fpath] = raw
        bak_path.write_bytes(raw)
        backups[fpath] = bak_path

    try:
        for file_key, fname in [
            ("config_replacements", "gondolin_config.py"),
            ("quests_replacements", "gondolin_quests.py"),
            ("mechanics_replacements", "gondolin_mechanics.py"),
        ]:
            fpath = base_dir / fname
            text = originals[fpath].decode("utf-8")
            for old_str, new_str in variant_cfg[file_key]:
                if old_str not in text:
                    msg = f"[BLAD WARIANTU] Nie znaleziono wzorca '{old_str}' w pliku {fname}!"
                    raise RuntimeError(msg)
                text = text.replace(old_str, new_str, 1)
            ast.parse(text)
            fpath.write_text(text, encoding="utf-8")
        yield
    finally:
        for fpath, raw_bytes in originals.items():
            fpath.write_bytes(raw_bytes)
            bak_path = backups[fpath]
            if bak_path.exists():
                bak_path.unlink()
        post_sums = compute_core_checksums(base_dir)
        if pre_sums != post_sums:
            msg = f"[BLAD KRYTYCZNY SUM KONTROLNYCH] Sumy SHA-256 po przywroceniu roznia sie: {pre_sums} != {post_sums}"
            raise RuntimeError(msg)


def build_a2_variants(base_dir: Path, selected_variants: list[str], ignore_git_check: bool = False) -> None:
    """Verify baseline state, build selected A2-bis .aoe2scenario files, and verify SHA-256 restoration."""
    git_info = verify_git_baseline(base_dir)
    if git_info["git_available"] and not ignore_git_check:
        if git_info["dirty_core_files"]:
            msg = (
                f"[BLAD BAZOWY] Pliki rdzenia maja niezacommitowane zmiany: {git_info['dirty_core_files']}. "
                "Przywroc czysty stan przed budowaniem wariantow A2."
            )
            raise RuntimeError(msg)
        if git_info["head"] not in ALLOWED_COMMITS:
            print(f"[OSTRZEZENIE] Aktualny HEAD ({git_info['head']}) rozni sie od {BASELINE_COMMIT}.")

    baseline_sums = compute_core_checksums(base_dir)
    import generate_gondolin_scenario
    import gondolin_config
    import gondolin_map
    import gondolin_mechanics
    import gondolin_quests

    for v_key in selected_variants:
        if v_key not in A2_BIS_VARIANTS:
            msg = f"Nieznany wariant: {v_key}. Dostepne: {list(A2_BIS_VARIANTS.keys())}"
            raise ValueError(msg)
        v_cfg = A2_BIS_VARIANTS[v_key]
        print("=" * 92)
        print(f"[BUDOWANIE WARIANTU A2-bis: {v_key}] -> {v_cfg['output']}")
        print(f"Opis: {v_cfg['desc']}")
        print("=" * 92)

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
    final_sums = compute_core_checksums(base_dir)
    assert baseline_sums == final_sums, "Niezgodnosc SHA-256 po zakonczeniu budowania wariantow!"
    print("[OK] Sumy kontrolne SHA-256 wszystkich 5 plikow rdzenia w 100% zgodne ze stanem bazowym.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Etap A1/A2-bis: Diagnostyka ID, test looping+timer oraz generator odizolowanych wariantow."
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
        help="Pomin blokade czystego git status (przydatne tylko w srodowisku bez git).",
    )
    args = parser.parse_args()
    base_dir = Path(__file__).parent

    print_diagnostic_report(base_dir)

    if args.build_variant:
        targets = list(A2_BIS_VARIANTS.keys()) if "all" in args.build_variant else args.build_variant
        build_a2_variants(base_dir, targets, ignore_git_check=args.ignore_git_check)


if __name__ == "__main__":
    main()
