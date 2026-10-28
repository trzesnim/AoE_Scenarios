# INSTRUKCJA TECHNICZNA DLA LLM: Generowanie scenariuszy AoE2: DE w Pythonie (`AoE2ScenarioParser`)

Twoim zadaniem jest tworzenie i rozwijanie skryptów w Pythonie wykorzystujących bibliotekę `AoE2ScenarioParser`, które wczytują pusty szablon `template.aoe2scenario` i generują grywalny scenariusz `.aoe2scenario` do *Age of Empires II: Definitive Edition*.

Aby wygenerowany kod zadziałał za pierwszym razem, **nie powodował błędów `AttributeError`/`TypeError` w Pythonie, nie zawieszał silnika AoE2: DE (crashe C++), nie przekraczał limitu tokenów wyjściowych (8192 tokeny) i przechodził walidację lintera Ruff bez ostrzeżeń**, bezwzględnie przestrzegaj poniższych 15 reguł technicznych.

---

## 1. Wczytywanie szablonu, reset struktur i aktywacja graczy
1. `AoE2ScenarioParser` wymaga wczytania istniejącego pliku bazowego: `scenario = AoE2DEScenario.from_file(str(INPUT_TEMPLATE))`.
2. Zawsze na początku czyść triggery i jednostki z szablonu:
   ```python
   tm.triggers = []
   um.units = [[] for _ in range(9)]
   mm.map_size = MAP_SIZE
   ```
3. **BŁĄD KRYTYCZNY (`Player.active`):** Właściwość `p.active` na obiekcie `Player` jest **tylko do odczytu** (brak settera). Próba `p.active = True` rzuci `AttributeError`.
   * **POPRAWNIE:** Ustawiaj liczbę aktywnych graczy globalnie na `player_manager` i nie nadpisuj ręcznie `p.human`:
     ```python
     pm.active_players = 4  # (lub 8 dla 4P Co-op vs 4 AI)
     ```
4. **KARTOGRAFIA DLA SOJUSZNIKÓW:** W scenariuszach drużynowych/Co-op zawsze badaj w `0:01` darmową Kartografię (`TECH_CARTOGRAPHY = 19`) dla wszystkich graczy ludzkich, aby od początku mieli wspólną wizję.

---

## 2. Lasy i drzewa (Tekstura podłoża vs Fizyczne obiekty + Szczelne krawędzie mapy)
1. **BŁĄD KRYTYCZNY:** Ustawienie samego `tile.terrain_id = TerrainId.FOREST_OAK` lub `TerrainId.FOREST_PINE` maluje **wyłącznie teksturę ściółki na ziemi**. Na mapie nie pojawi się ani jedno drzewo do ścinania, a jednostki przejdą przez „las” jak przez łąkę.
2. **POPRAWNIE (Pełny zakres `0..MAP_SIZE-1`):** Po ukształtowaniu terenu i wycięciu dróg (`TerrainId.ROAD`) lub przełęczy (`TerrainId.DIRT_1`), przeiteruj po **wszystkich** kafelkach mapy (`range(MAP_SIZE)`, bez zostawiania pustego marginesu przy krawędziach `0` i `MAP_SIZE - 1`, aby jednostki nie obchodziły lasów po krawędzi ekranu!) i postaw fizyczny obiekt drzewa należący do `PlayerId.GAIA`:
   * `349` = Dąb (*Oak Tree*)
   * `350` = Sosna (*Pine Tree*)

---

## 3. Dodawanie surowców i limitu populacji (ZAKAZ ujemnego `tribute`!)
1. **CRASH GRY W 60. SEKUNDZIE:** **NIGDY** nie używaj `new_effect.tribute` z ujemną wartością `quantity=-amount`, aby dodać graczowi surowce lub pasywny dochód (trickle). W silniku AoE2: DE powoduje to przepełnienie bufora (unsigned integer underflow) i zawiesza proces gry.
2. **BŁĄD API (`BONUS_POPULATION_CAP`):** Dodatkowy limit populacji **NIE JEST** atrybutem obiektu w `ObjectAttribute` (wywołanie `ObjectAttribute.BONUS_POPULATION_CAP` rzuci `AttributeError`). Jest to zasób gracza (*Player Resource*) o ID `32`.
3. **POPRAWNIE:** Do dodawania jakichkolwiek surowców, łupów, pasywnego dochodu (trickle) oraz dodatkowego limitu populacji używaj **wyłącznie** efektu `modify_resource` z dodatnią liczbą całkowitą i `Operation.ADD`:
   * `RES_FOOD = 0`, `RES_WOOD = 1`, `RES_STONE = 2`, `RES_GOLD = 3`, `RES_BONUS_POP_CAP = 32`.

---

## 4. Zakaz używania `display_timer` oraz `display_instructions` (Ochrona przed crashami UI)
1. **CRASH GRY (`display_timer` i `display_instructions`):** **NIGDY** nie używaj efektów `new_effect.display_timer` ani `new_effect.display_instructions`! Wygenerowane programowo struktury tych dwóch efektów potrafią zawiesić wątek renderowania C++ (`AoE2DE_s.exe`) przy odświeżaniu lub wygasaniu baneru.
2. **POPRAWNIE:**
   * Do wyświetlania stałych zadań na ekranie używaj właściwości `trigger.short_description` + `trigger.display_on_screen = 1`.
   * Do komunikatów i odliczania czasu w trakcie gry używaj **wyłącznie** `new_effect.send_chat` (z tagami kolorów `<RED>`, `<GREEN>`, `<YELLOW>`, `<AQUA>`, `<ORANGE>`, `<PURPLE>`) oraz flar na minimapie (`new_effect.flare` + spawnowanie obiektu `FLARE_UNIT_ID = 112`).

---

## 5. Modyfikacja statystyk jednostek (`modify_attribute`) i oficjalne ID silnika Genie
1. Zawsze używaj oficjalnych identyfikatorów liczbowych silnika Genie:
   * `ATTR_HIT_POINTS = 0` (Punkty życia)
   * `ATTR_LINE_OF_SIGHT = 1` (Zasięg widzenia w mgle wojny)
   * `ATTR_MOVEMENT_SPEED = 5` (Prędkość ruchu)
   * `ATTR_ARMOR = 8` (Pancerz — wymaga podania klasy pancerza!)
   * `ATTR_ATTACK = 9` (Atak — wymaga podania klasy ataku!)
   * `ATTR_ATTACK_RELOAD_TIME = 10` (Czas przeładowania w sekundach)
   * `ATTR_MAXIMUM_RANGE = 12` (Maksymalny zasięg)
   * `ATTR_WORK_RATE = 13` (Tempo pracy / produkcji / konwersji)
   * `ATTR_MINIMUM_RANGE = 20` (Minimalny zasięg — martwa strefa wokół jednostek oblężniczych)
   * `ATTR_BLAST_WIDTH = 22` (Promień obrażeń obszarowych / AoE splash)
   * `ATTR_SEARCH_RADIUS = 23` (Promień wykrywania wroga — zawsze zwiększaj wraz z `MAXIMUM_RANGE`)
   * `ATTR_HERO_STATUS = 40` (`1` = złota poświata Bohatera + odporność na konwersję; `4` = sama odporność na konwersję)
   * `ATTR_REGENERATION_RATE = 109` (Regeneracja HP na minutę, np. `300` = `5 HP/s`)
2. **KOLEJNOŚĆ BADANIA ER AI A `modify_attribute`:**
   * Zbadanie nowej Ery (`TECH_FEUDAL_AGE = 101`, `TECH_CASTLE_AGE = 102`, `TECH_IMPERIAL_AGE = 103`) przez `research_technology` resetuje statystyki jednostek do wartości z drzewka technologicznego, **kasując wcześniejsze `modify_attribute`**!
   * Zawsze badaj Ery AI w `0:01` (`t_init`), a mutacje statystyk jednostek (`modify_attribute`) nakładaj w osobnym triggerze z warunkiem `timer=3` (w 3. sekundzie gry).

---

## 6. Ochrona przed błędem przepełnienia `uint8` (`5 + 247` ataku!) przy `modify_attribute`
1. **MECHANIZM BŁĘDU W SILNIKU GENIE:** Wartości klas ataku (`ATTR_ATTACK = 9`) i pancerza (`ATTR_ARMOR = 8`) są przechowywane na 8-bitowej liczbie bez znaku (`uint8`, zakres `0..255`). Jednostki strzeleckie (np. `Crossbowman`) mają `0` ataku wręcz (`armor_class=4`), a jednostki wręcz mają `0` ataku strzeleckiego (`armor_class=3`).
   * Jeśli odejmiesz atak (`Operation.SUBTRACT`) lub zmodyfikujesz niewłaściwą klasę ataku o `-4`, wartość zawinie się modulo 256 do `256 - 4 = 252` (wyświetlane w grze jako `5 + 247` ataku, co zabija każdą jednostkę jednym strzałem!).
2. **ZASADY BEZPIECZEŃSTWA (`add_enemy_combat_buff`):**
   * **Zawsze rozdzielaj listy jednostek** na `enemy_melee_units` (modyfikowane wyłącznie na `armor_class=4`) oraz `enemy_ranged_units` (modyfikowane wyłącznie na `armor_class=3`).
   * **Nigdy nie używaj `Operation.SUBTRACT` na ataku lub pancerzu poniżej wartości bazowej `0`!** Do osłabiania wrogów na niższych poziomach trudności używaj skalowania procentowego HP (`Operation.MULTIPLY`, `0.85`). `Operation.SUBTRACT` jest dozwolony wyłącznie do dokładnego cofnięcia bonusu dodanego wcześniej przez `Operation.ADD` (np. zdjęcie tarczy Maga `+30 -> -30`, pod warunkiem że trigger zdejmujący jest aktywowany wyłącznie przez trigger nakładający!).

---

## 7. Pułapki w ID jednostek i budynków (`MONUMENT`, `WONDER`, Palisady, Bramy i `UnitInfo`)
1. **ZAKAZ `BuildingInfo.MONUMENT` (`596`) JAKO CELU DO ZBURZENIA:** Budynek `MONUMENT` jest przejmowalny (*Capturable*) — zmienia właściciela na kolor gracza zamiast zostać zburzonym (`destroy_object` nigdy się nie spełni). Używaj normalnych budynków (`MARKET`, `UNIVERSITY`, `MONASTERY`, `KREPOST = 1251`, `CASTLE`, `GUARD_TOWER`, `KEEP`).
2. **ZAKAZ `BuildingInfo.WONDER` (`276`) W ZWYKŁYCH SCENARIUSZACH:** Postawienie Cudu (`WONDER`) uruchamia 350-letni licznik zwycięstwa. Zamiast Cudu używaj **Feitorii (`FEITORIA_ID = 1021`)** lub **Krepostu (`KREPOST_ID = 1251`)**.
3. **POPRAWNE NAZWY W `UnitInfo` I `BuildingInfo`:**
   * Konny łucznik w Imperialu to **`UnitInfo.HEAVY_CAVALRY_ARCHER.ID`** (a NIE `HEAVY_CAV_ARCHER`).
   * Piechur z długim mieczem to **`UnitInfo.LONG_SWORDSMAN.ID`** (z podkreślnikiem, a NIE `LONGSWORDSMAN`).
   * Wzmocniona Palisada (*Fortified Palisade Wall*) to **`119`** (UWAGA: `155` to kamienny *Fortified Wall*!).
   * Zbudowana Brama Palisadowa to **`789`** (oś X / SW-NE) oraz **`793`** (oś Y / NW-SE).
   * Baszta to **`BuildingInfo.KEEP.ID`** (`235`), a wóz handlowy to **`UnitInfo.TRADE_CART_EMPTY.ID`** (`128`).

---

## 8. Ochrona przed `TypeError: unexpected keyword argument` (`safe_call`)
Różne wersje `AoE2ScenarioParser` używają odmiennych nazw niektórych parametrów w `new_effect` i `new_condition`. Zawsze używaj wrappera `safe_call(func, **kwargs)` opartego na `inspect.signature(func)`.

---

## 9. Spawnowanie fal AI, wchodzenie w głąb bazy i zachowania specjalne
1. **WCHODZENIE DO BAZY ZAMIAST BICIA BOCZNYCH MURÓW:** Współrzędne docelowe `attack_move` dla fal ustawiaj zawsze **głęboko wewnątrz bazy graczy** (a nie na samej bramie!), oraz dodaj cykliczny trigger (co 15s), który ponawia rozkaz `attack_move` w głąb bazy dla jednostek stojących w obszarze przełęczy.
2. **JEDNOSTKI DYWERSYJNE (`Eco-Raiders`):** Aby szybkie jednostki dywersyjne (np. Huzarzy o niskim ataku) mijały walkę na froncie i wjeżdżały w chłopów pod TC, wydawaj im rozkaz `new_effect.move` skierowany bezpośrednio na złoża/drwali pod Town Center graczy.
3. **WYRĄB PRZESIEK W LESIE PRZEZ ONAGERY AI:** Ponieważ AI nie używa samodzielnie opcji *Cut Trees* na Onagerach, zapisuj podczas `populate_forest_trees` referencje do drzew w korytarzach saperskich i usuwaj je efektem `remove_object(selected_object_ids=[tree.reference_id])` w momencie uderzenia fali saperskiej (po wcześniejszym 15-sekundowym ostrzeżeniu z flarą).

---

## 10. Siatka antykolizyjna (`SafeMapGrid`), bezpieczna elewacja i szczelne przełęcze
1. Używaj dwóch osobnych zbiorów w `SafeMapGrid`:
   * `occupied_tiles: set[tuple[int, int]]` — dokładny obrys postawionych obiektów.
   * `no_tree_zones: set[tuple[int, int]]` — strefy chronione przed sadzeniem drzew.
2. W przełęczach używaj prostokątnego `mark_no_trees_box(gx - 6, gy - 6, gx + 6, gy + 6)`, a palisadę stawiaj od `gx - 7` do `gx + 7` z `clear_trees_around=False`, aby mur łączył się z lasem bez luk.
3. Przed zapisaniem wysokości do `tile.elevation` zawsze wykonaj dwuprzebiegowe wygładzanie Lipschitza ($|\Delta h| \le 1$).

---

## 11. Stały punktowy `Map Revealer` (`LOS = 4`) + Garnizony na Smyczy Terytorialnej (`Camp Leash`)
1. **ZERO ZASOBÓW I ZERO MOBILNYCH JEDNOSTEK AI W `0:00`:** Graczom AI ustawiaj na starcie `0` zasobów i stawiaj w `0:00` wyłącznie budynki.
2. **STAŁY PUNKTOWY PODGLĄD BUDYNKU ZADANIA (`LOS = 4`):**
   * Stawiaj na środku każdego Questu i Settlementu `(cx, cy)` pojedynczy obiekt `MAP_REVEALER_ID = 837` należący do `PlayerId.ONE` i ustaw mu w `t_init` minimalny zasięg widzenia: `ATTR_LINE_OF_SIGHT = 4`. Dzięki temu budynek jest przez cały mecz widoczny i klikalny pod Mgłą Wojny, a reszta mapy pozostaje zasłonięta.
   * Aby ten pojedynczy Revealer Gracza 1 nie wyzwolił strażników w `0:00`, w detektorze `objects_in_area` (uzbrajanym w 4. sekundzie gry, `radius = 15`) ustaw wymagane `quantity = 2` dla `PlayerId.ONE` (1 Revealer + 1 dowolna jednostka P1) oraz `quantity = 1` dla `PlayerId.TWO..FOUR`.
3. **SMYCZ TERYTORIALNA (`Camp Leash`):** Po zespawnowaniu garnizonu aktywuj cykliczny trigger (`timer = 3`, `looping = True`), który w 4 pasach granicznych wokół obozu (`9..20` kratek od środka) wydaje jednostkom AI rozkaz `attack_move` z powrotem na środek obozu `(cx, cy)`. Dzięki temu skaut gracza nie może odciągnąć obrońców od chronionego budynku.

---

## 12. Panel Zadań (Objectives UI), Podpisy Budynków i Zakładki Opisów w Grze
1. **MALEJĄCE SORTOWANIE `description_order` W OBJECTIVES:** Silnik AoE2: DE sortuje listę zadań na ekranie **MALEJĄCO** po `description_order` (najwyższa liczba trafia na samą górę listy: `100 -> 96` dla Questów, `90 -> 84` dla Settlementów).
2. Zmieniaj nazwy budynków Questów i Settlementów w `t_init` za pomocą `new_effect.change_object_name`.
3. Zapisuj pełny opis zasad, bestiariusz i wskazówki bezpośrednio do `scenario.message_manager.instructions`, `.hints`, `.scouts` oraz `.history`.

---

## 13. Zgodność z linterem Ruff (Czysty kod Pythona)
Kod musi przechodzić kontrolę **Ruff** z zerową liczbą ostrzeżeń:
* `I001`: Posortowane importy (biblioteka standardowa -> `AoE2ScenarioParser` -> moduły lokalne; wewnątrz `from X import (...)` najpierw `ALL_CAPS`, potem `CamelCase`, na końcu `snake_case`), brak nieużywanych importów (`F401`) i brak `import *` (`F403`).
* `PIE808`: `range(n)` zamiast `range(0, n)`.
* `PLR1730`: `max(...)` / `min(...)` zamiast `if`.
* `SIM102`: Połączone warunki `if cond1 and cond2:`.
* `RUF046`: `round(x)` zamiast `int(round(x))`.
* `SIM210`: Bezpośredni `bool` zamiast `True if cond else False`.
* `S110` / `BLE001`: Zakaz `try: ... except Exception: pass`.

---

## 14. Architektura Modularna (Ochrona przed limitem 8192 tokenów wyjściowych)
Aby uniknąć ucinania długich odpowiedzi przez limit tokenów wyjściowych LLM, duże scenariusze dzielimy na 5 modułów:
1. **`horde_config.py`:** Stałe ID, słownik `BALANCE`, `get_wave_definitions()` oraz opisy `populate_ingame_scenario_descriptions`.
2. **`horde_map.py`:** Klasa `SafeMapGrid`, generatory terenu/lasów/baz oraz `build_map_and_entities(scenario) -> dict`.
3. **`horde_waves.py`:** Funkcje pomocnicze triggerów oraz `setup_init_aura_and_waves(scenario, ctx)`.
4. **`horde_quests.py`:** `setup_sanctuary_quests_and_victory(scenario, ctx)` (Sanktuarium Balansu, Questy, Settlementy, Zwycięstwo).
5. **`generate_horde_quests_scenario.py`:** Krótki skrypt główny wywołujący powyższe moduły.

**ZASADA DLA LLM PRZY KOLEJNYCH ZMIANACH:** Podczas modyfikacji istniejącego scenariusza **drukuj w odpowiedzi wyłącznie te moduły `.py`, które uległy zmianie** (np. sam `horde_config.py` przy zmianach balansu fal/statystyk), nigdy nie drukuj ponownie niezmienionych modułów.