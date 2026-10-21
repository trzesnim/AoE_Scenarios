# INSTRUKCJA TECHNICZNA DLA LLM: Generowanie scenariuszy AoE2: DE w Pythonie (`AoE2ScenarioParser`)

Twoim zadaniem jest napisanie kompletnego skryptu w Pythonie wykorzystującego bibliotekę `AoE2ScenarioParser`, który wczytuje pusty szablon `template.aoe2scenario` i generuje grywalny scenariusz `.aoe2scenario` do *Age of Empires II: Definitive Edition*.

Aby wygenerowany kod zadziałał za pierwszym razem, **nie powodował błędów `AttributeError`/`TypeError` w Pythonie, nie zawieszał silnika AoE2: DE (crashe C++) i przechodził walidację lintera Ruff bez ostrzeżeń**, bezwzględnie przestrzegaj poniższych 13 reguł technicznych.

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
   ```python
   TREE_OAK_ID = 349
   TREE_PINE_ID = 350


   def populate_forest_trees(mm, um, grid):
       for x in range(grid.size):
           for y in range(grid.size):
               if (x, y) in grid.occupied_tiles or (x, y) in grid.no_tree_zones:
                   continue
               t_id = mm.get_tile(x, y).terrain_id
               if t_id == TerrainId.FOREST_OAK:
                   grid.occupied_tiles.add((x, y))
                   um.add_unit(
                       player=PlayerId.GAIA, unit_const=TREE_OAK_ID, x=x + 0.5, y=y + 0.5
                   )
               elif t_id == TerrainId.FOREST_PINE:
                   grid.occupied_tiles.add((x, y))
                   um.add_unit(
                       player=PlayerId.GAIA, unit_const=TREE_PINE_ID, x=x + 0.5, y=y + 0.5
                   )
   ```
3. Zadbaj, aby każdy gracz miał blisko swojego Town Center dedykowane lasy, drzewa pojedyncze (*stragglers*), jagody (`OtherInfo.FORAGE_BUSH.ID`), złoto (`OtherInfo.GOLD_MINE.ID`), kamień (`OtherInfo.STONE_MINE.ID`), owce (`UnitInfo.SHEEP.ID`), dziki (`UnitInfo.WILD_BOAR.ID`) i jelenie (`UnitInfo.DEER.ID`).

---

## 3. Dodawanie surowców i limitu populacji (ZAKAZ ujemnego `tribute`!)
1. **CRASH GRY W 60. SEKUNDZIE:** **NIGDY** nie używaj `new_effect.tribute` z ujemną wartością `quantity=-amount`, aby dodać graczowi surowce lub pasywny dochód (trickle). W silniku AoE2: DE powoduje to przepełnienie bufora (unsigned integer underflow) i zawiesza proces gry.
2. **BŁĄD API (`BONUS_POPULATION_CAP`):** Dodatkowy limit populacji **NIE JEST** atrybutem obiektu w `ObjectAttribute` (wywołanie `ObjectAttribute.BONUS_POPULATION_CAP` rzuci `AttributeError`). Jest to zasób gracza (*Player Resource*) o ID `32`.
3. **POPRAWNIE:** Do dodawania jakichkolwiek surowców, łupów, pasywnego dochodu (trickle) oraz dodatkowego limitu populacji używaj **wyłącznie** efektu `modify_resource` z dodatnią liczbą całkowitą i `Operation.ADD`:
   ```python
   RES_FOOD = 0
   RES_WOOD = 1
   RES_STONE = 2
   RES_GOLD = 3
   RES_BONUS_POP_CAP = 32  # Dodatkowy limit populacji ponad limit ustawiony w lobby


   def add_player_resource(trigger, player: PlayerId, resource_id: int, amount: int):
       safe_call(
           trigger.new_effect.modify_resource,
           source_player=player,
           tribute_list=resource_id,
           operation=Operation.ADD,
           quantity=amount,
       )
   ```

---

## 4. Zakaz używania `display_timer` oraz `display_instructions` (Ochrona przed crashami UI)
1. **CRASH GRY (`display_timer` i `display_instructions`):** **NIGDY** nie używaj efektów `new_effect.display_timer` ani `new_effect.display_instructions`! Wygenerowane programowo struktury tych dwóch efektów potrafią zawiesić wątek renderowania C++ (`AoE2DE_s.exe`) przy odświeżaniu lub wygasaniu baneru.
2. **POPRAWNIE:**
   * Do wyświetlania stałych zadań na ekranie używaj właściwości `trigger.short_description` + `trigger.display_on_screen = 1` (patrz Punkt 12).
   * Do komunikatów i odliczania czasu w trakcie gry używaj **wyłącznie** `new_effect.send_chat` (z tagami kolorów `<RED>`, `<GREEN>`, `<YELLOW>`, `<AQUA>`, `<ORANGE>`, `<PURPLE>`) oraz flar na minimapie (`new_effect.flare`).

---

## 5. Modyfikacja statystyk jednostek (`modify_attribute`) i oficjalne ID silnika Genie
1. Nazwy niektórych enumów w `ObjectAttribute` różnią się między wersjami biblioteki. Zawsze używaj oficjalnych identyfikatorów liczbowych silnika Genie:
   * `ATTR_HIT_POINTS = 0` (Punkty życia)
   * `ATTR_LINE_OF_SIGHT = 1` (Zasięg widzenia w mgle wojny)
   * `ATTR_MOVEMENT_SPEED = 5` (Prędkość ruchu)
   * `ATTR_ARMOR = 8` (Pancerz — wymaga podania klasy pancerza!)
   * `ATTR_ATTACK = 9` (Atak — wymaga podania klasy ataku!)
   * `ATTR_ATTACK_RELOAD_TIME = 10` (Czas przeładowania / odstęp między atakami w sekundach)
   * `ATTR_MAXIMUM_RANGE = 12` (Maksymalny zasięg)
   * `ATTR_WORK_RATE = 13` (Tempo pracy / produkcji / leczenia)
   * `ATTR_BLAST_WIDTH = 22` (Promień obrażeń obszarowych / AoE splash!)
   * `ATTR_SEARCH_RADIUS = 23` (Promień wykrywania wroga — przy zwiększaniu zasięgu powyżej 12 zawsze zwiększaj też `SEARCH_RADIUS` oraz `LINE_OF_SIGHT`)
2. **WAŻNE PRZY ATAKU (`9`) I PANCERZU (`8`):** Modyfikacja ataku lub pancerza wymaga podania `armour_attack_class` (gdzie `4` = Base Melee / walka wręcz, `3` = Base Pierce / strzały) oraz `armour_attack_quantity` zamiast zwykłego `quantity`.
3. **KOLEJNOŚĆ BADANIA ER AI A `modify_attribute`:**
   * Zbadanie nowej Ery (`TECH_FEUDAL_AGE = 101`, `TECH_CASTLE_AGE = 102`, `TECH_IMPERIAL_AGE = 103`) przez `research_technology` resetuje statystyki jednostek do wartości z drzewka technologicznego, **kasując wcześniejsze `modify_attribute`**!
   * Zawsze badaj Ery AI w `0:01` (`t_init`), a mutacje statystyk jednostek (`modify_attribute`) nakładaj w osobnym triggerze z warunkiem `timer=3` (w 3. sekundzie gry).

---

## 6. Pułapki w ID jednostek i budynków (`MONUMENT`, `WONDER`, Palisady i Bramy)
1. **ZAKAZ `BuildingInfo.MONUMENT` (`596`) JAKO CELU DO ZBURZENIA:** Budynek `MONUMENT` ma wbudowaną w silnik flagę *Capturable* — gdy gracze podejdą pod niego, Monument zmienia właściciela na kolor gracza zamiast zostać zburzonym, przez co warunek `destroy_object` nigdy się nie spełni! Używaj normalnych budynków (`MARKET`, `UNIVERSITY`, `MONASTERY`, `KREPOST = 1251`, `CASTLE`, `GUARD_TOWER`, `KEEP`).
2. **ZAKAZ `BuildingInfo.WONDER` (`276`) W ZWYKŁYCH SCENARIUSZACH:** Postawienie Cudu (`WONDER`) dla dowolnego gracza automatycznie uruchamia w grze 350-letni licznik zwycięstwa z Cudu. Zamiast Cudu używaj **Feitorii (`FEITORIA_ID = 1021`)** lub **Krepostu (`KREPOST_ID = 1251`)** z podbitym HP.
3. **POPRAWNE ID PALISAD, BRAM I JEDNOSTEK SPECJALNYCH:**
   * **Wzmocniona Palisada (*Fortified Palisade Wall*)** to **`119`** (UWAGA: ID `155` to kamienny *Fortified Wall*!).
   * **Zbudowana Brama Palisadowa** to **`789`** (wzdłuż osi X / SW-NE) oraz **`793`** (wzdłuż osi Y / NW-SE).
   * Ulepszona wieża (Baszta) to **`BuildingInfo.KEEP.ID`** (`235`), a NIE `FORTIFIED_TOWER`.
   * Wóz handlowy to **`UnitInfo.TRADE_CART_EMPTY.ID`** (`128`), a NIE `TRADE_CART`.
   * Sprawdzone ID jednostek pod mutacje: `IMAM_UNIT_ID = 842`, `SIEGE_ONAGER_ID = 588`, `PETARD_ID = 440`, `FLAMING_CAMEL_ID = 1263`, `ELITE_BERSERK_ID = 694`, `ELITE_BATTLE_ELEPHANT_ID = 1134`.

---

## 7. Ochrona przed `TypeError: unexpected keyword argument` (`safe_call`)
Różne wersje `AoE2ScenarioParser` używają odmiennych nazw niektórych parametrów w `new_effect` i `new_condition`. Zawsze definiuj na początku skryptu poniższe funkcje pomocnicze:

```python
import inspect
from AoE2ScenarioParser.datasets.trigger_lists import Operation


def safe_call(func, **kwargs):
    """Przekazuje do metody AoE2ScenarioParser wyłącznie argumenty obsługiwane w jej sygnaturze."""
    sig = inspect.signature(func)
    valid_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
    return func(**valid_kwargs)


def safe_modify_attribute(
    trigger, source_player, unit_id, attr_id, operation, val, armor_class=None
):
    """Bezpiecznie modyfikuje zarówno atrybuty skalarne, jak i klasy ataku/pancerza."""
    fn = trigger.new_effect.modify_attribute
    base_kwargs = {
        "source_player": source_player,
        "object_list_unit_id": unit_id,
        "object_attributes": attr_id,
        "operation": operation,
    }
    if armor_class is not None:
        try:
            return safe_call(
                fn,
                **base_kwargs,
                armour_attack_class=armor_class,
                armour_attack_quantity=int(val),
            )
        except (ValueError, TypeError):
            return safe_call(
                fn, **base_kwargs, armour_attack_class=armor_class, quantity=val
            )
    return safe_call(fn, **base_kwargs, quantity=val)
```

---

## 8. Spawnowanie fal AI i stopniowa progresja trudności
1. Aby jednostki AI atakowały zwartą grupą (bez „węża”), spawnowanie w `create_object` rozmieszczaj na siatce `6x6` wokół `(spawn_x, spawn_y)`, a zaraz po pętli dodaj w tym samym triggerze `attack_move` obejmujący prostokąt `spawn_x - 8` do `spawn_x + 8` skierowany na `(target_x, target_y)`.
2. Zamiast jednej statycznej pętli, generuj 10–12 osobnych fal o rosnącej sile (z ostatnią falą ustawioną na `looping=True` jako tryb *Endless*).
3. **STOPNIOWE WPROWADZANIE JEDNOSTEK SPECJALNYCH:**
   * Do 15. minuty: głównie jednostki Feudalne (pierwsza fala bez mutantów, druga z pojedynczymi słabszymi specjalistami).
   * 16.–25. minuta: głównie jednostki Castle Age + stopniowe dokładanie kolejnych klas mutantów co falę.
   * Po 25. minucie: jednostki Imperialne + pełna skala wszystkich klas mutantów.
4. Globalny trigger eskalacji statystyk (`+HP` / `+Atak` co 4 minuty) uruchamiaj dopiero **po pierwszym ataku** (np. aktywowany przez Falę 1 w 10:00, dzięki czemu pierwszy bonus wpada w 14:00, a nie w 4. minucie gry!).

---

## 9. Architektura kodu
Wszystkie parametry liczbowe odpowiedzialne za balans umieszczaj na górze skryptu w jednym słowniku `BALANCE = {...}`, aby można je było łatwo stroić między meczami.

---

## 10. Siatka antykolizyjna (`SafeMapGrid`), bezpieczna elewacja i szczelne mury w przełęczach
1. **ROZDZIAŁ KOLIZJI OBIEKTÓW OD STREF ZAKAZU DRZEW:**
   * `occupied_tiles: set[tuple[int, int]]` — przechowuje **wyłącznie dokładny obrys** postawionych budynków, murów i jednostek. Funkcja `place_unit` w razie kolizji na kafelku `(x, y)` szuka spiralnie najbliższego wolnego kafelka obok (`for r in range(6)`).
   * `no_tree_zones: set[tuple[int, int]]` — przechowuje strefy ochronne wokół baz, dróg i bram sprawdzane wyłącznie przez `populate_forest_trees`.
2. **BRAK DZIUR MIĘDZY MUREM A LASEM W PRZEŁĘCZACH:**
   * Kiedy wycinasz przełęcz w lesie pod mur z bramą o szerokości od `gx - 6` do `gx + 6`, używaj prostokątnego `mark_no_trees_box(gx - 6, gy - 6, gx + 6, gy + 6)` (zamiast kołowego `radius=8`), a palisadę stawiaj od `gx - 7` do `gx + 7` z `clear_trees_around=False`. Dzięki temu palisada styka się bezpośrednio z drzewami i na skrajach przełęczy nie powstają 2-kratkowe luki.
3. **BEZPIECZNA ELEWACJA (`apply_smooth_elevation`):**
   * Silnik Genie wymaga, aby sąsiednie kafelki różniły się wysokością maksymalnie o `1` ($|\Delta h| \le 1$). Zawsze wykonuj dwuprzebiegowe wygładzanie Lipschitza przed zapisaniem wysokości do `tile.elevation`.

---

## 11. Kontrola AI w Co-op oraz pułapka `Map Revealer` vs `Proximity Garrison`
1. **ZERO ZASOBÓW I ZERO MOBILNYCH JEDNOSTEK AI W `0:00`:**
   * Graczom AI opartym na falach ustawiaj na starcie `0` zasobów, a w `0:00` stawiaj dla nich wyłącznie budynki. Gdybyś postawił mobilnych strażników w `0:00`, AI w 1. sekundzie gry wyśle ich na bazy graczy będących w Dark Age!
2. **PUŁAPKA `MAP REVEALER` WYZWALAJĄCEGO GARNIZON W 1. SEKUNDZIE:**
   * **BŁĄD KRYTYCZNY:** Jeśli postawisz `MAP_REVEALER_ID = 837` należący do gracza ludzkiego na środku obozu `(cx, cy)`, a następnie ustawisz na tym obozie trigger zbliżeniowy `objects_in_area(..., source_player=h_p, quantity=1)`, silnik gry potraktuje `Map Revealera` jako jednostkę gracza i **w 1. sekundzie gry zespawnuje wszystkie garnizony z całej mapy**, które AI natychmiast wyśle do ataku na bazy graczy!
   * **POPRAWNE ROZWIĄZANIE (Punktowe odkrycie z zachowaniem Mgły Wojny):**
     1. Stawiaj **tylko 1** `Map Revealer` (dla `PlayerId.ONE` — dzięki Kartografii widzą go wszyscy gracze) przesunięty o `cx + 9` kratek od środka celu i ustaw mu w `t_init` mały zasięg widzenia: `ATTR_LINE_OF_SIGHT = 10`. Odkrywa to wyłącznie sam budynek celu (pozwalając w niego kliknąć), zachowując Mgłę Wojny na reszcie mapy.
     2. Strefę detekcji garnizonu (`objects_in_area`) ogranicz do promienia `detect_radius = 7` (dzięki czemu `Map Revealer` na `cx + 9` leży **poza** prostokątem detekcji!), wymagaj `quantity=5` jednostek gracza i uzbrajaj detektory dopiero w 6. minucie gry (`timer=360`).

---

## 12. Panel Zadań (Objectives UI), Podpisy Budynków i Zakładki Opisów w Grze
1. **MALEJĄCE SORTOWANIE `description_order` W OBJECTIVES:**
   * Silnik AoE2: DE sortuje listę zadań na ekranie **MALEJĄCO** po `description_order` (najwyższa liczba trafia na samą górę listy!).
   * Nadawaj najwyższe numery nagłówkom i pierwszym zadaniom, np.:
     * `order = 100`: `-- QUESTY POBOCZNE --` (`header=1`)
     * `order = 99..96`: `Q1..Q4`
     * `order = 90`: `-- SETTLEMENTY HORDY --` (`header=1`)
     * `order = 89..84`: `G1..G3`
   * Opisy `short_description` muszą być zwięzłe (1 krótka linijka, np. `"Q1 - Karawanseraj (zasoby + handel)"`).
2. **PODPISYWANIE BUDYNKÓW NA MAPIE (`change_object_name`):**
   * Zmieniaj nazwy budynków Questów i Settlementów w `t_init` za pomocą `new_effect.change_object_name(selected_object_ids=[b_unit.reference_id], message="Q1: Karawanseraj (+500 Zlota i 3 Wozy)")`.
3. **WBUDOWANY OPIS W ZAKŁADKACH MENU GRY (`message_manager`):**
   * Zapisuj pełny opis zasad, bestiariusz i wskazówki bezpośrednio do `scenario.message_manager.instructions`, `.hints`, `.scouts` oraz `.history`, aby gracze mieli do nich dostęp w grze pod przyciskiem celów/wskazówek.

---

## 13. Zgodność z linterem Ruff (Czysty kod Pythona)
Wygenerowany skrypt musi przechodzić kontrolę lintera **Ruff** z zerową liczbą ostrzeżeń:
1. **`I001` (Sortowanie importów):** Sortuj importy alfabetycznie (najpierw biblioteka standardowa: `import inspect`, `import math`, `from pathlib import Path`, pusta linia, a następnie posortowane alfabetycznie moduły `from AoE2ScenarioParser...`).
2. **`PIE808` (`range`):** Pisz `range(n)` zamiast `range(0, n)`.
3. **`PLR1730` (`min`/`max`):** Zamiast `if h > self.elev[x][y]: self.elev[x][y] = h` używaj `self.elev[x][y] = max(self.elev[x][y], h)` (analogicznie `min(...)`).
4. **`SIM102` (Zagnieżdżone `if`):** Łącz zagnieżdżone warunki bez `else` w jeden warunek `if cond1 and cond2:`.
5. **`RUF046` (`int(round(...))`):** W Pythonie 3 funkcja `round(x)` z jednym argumentem zwraca już typ `int` — nigdy nie opakowuj jej w nadmiarowe `int(round(x))`.
6. **`SIM210` (`bool`):** Zamiast `True if cond else False` przypisuj bezpośrednio wartość logiczną warunku.
7. **`S110` i `BLE001` (`try-except-pass`):** Nigdy nie używaj konstrukcji `try: ... except Exception: pass`. Sprawdzaj istnienie atrybutów jawnie przez `if hasattr(obj, "attr"):`.