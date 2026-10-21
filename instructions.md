# INSTRUKCJA TECHNICZNA DLA LLM: Generowanie scenariuszy AoE2: DE w Pythonie (`AoE2ScenarioParser`)

Twoim zadaniem jest napisanie kompletnego skryptu w Pythonie wykorzystującego bibliotekę `AoE2ScenarioParser`, który wczytuje pusty szablon `template.aoe2scenario` i generuje grywalny scenariusz `.aoe2scenario` do *Age of Empires II: Definitive Edition*.

Aby wygenerowany kod zadziałał za pierwszym razem i **nie powodował błędów `AttributeError`/`TypeError` w Pythonie ani zawieszania się (crashy C++) silnika AoE2: DE**, bezwzględnie przestrzegaj poniższych 9 reguł technicznych.

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
   * **POPRAWNIE:** Ustawiaj liczbę aktywnych graczy globalnie na `player_manager`:
     ```python
     pm.active_players = 4  # (lub 8 dla 4P Co-op vs 4 AI)
     ```

---

## 2. Lasy i drzewa (Tekstura podłoża vs Fizyczne obiekty)
1. **BŁĄD KRYTYCZNY:** Ustawienie samego `tile.terrain_id = TerrainId.FOREST_OAK` lub `TerrainId.FOREST_PINE` maluje **wyłącznie teksturę ściółki na ziemi**. Na mapie nie pojawi się ani jedno drzewo do ścinania, a jednostki przejdą przez „las” jak przez łąkę.
2. **POPRAWNIE:** Po ukształtowaniu terenu i wycięciu dróg (`TerrainId.ROAD`) lub przełęczy (`TerrainId.DIRT_1`), musisz przeiterować po wszystkich kafelkach mapy i na każdym kafelku leśnym postawić fizyczny obiekt drzewa należący do `PlayerId.GAIA`:
   * `349` = Dąb (*Oak Tree*)
   * `350` = Sosna (*Pine Tree*)
   ```python
   TREE_OAK_ID = 349
   TREE_PINE_ID = 350


   def populate_forest_trees(mm, um, map_size: int):
       for x in range(map_size):
           for y in range(map_size):
               t_id = mm.get_tile(x, y).terrain_id
               if t_id == TerrainId.FOREST_OAK:
                   um.add_unit(
                       player=PlayerId.GAIA, unit_const=TREE_OAK_ID, x=x + 0.5, y=y + 0.5
                   )
               elif t_id == TerrainId.FOREST_PINE:
                   um.add_unit(
                       player=PlayerId.GAIA, unit_const=TREE_PINE_ID, x=x + 0.5, y=y + 0.5
                   )
   ```
3. Zadbaj, aby każdy gracz miał w pobliżu swojego Town Center dedykowane lasy, jagody (`OtherInfo.FORAGE_BUSH.ID`), złoto (`OtherInfo.GOLD_MINE.ID`), kamień (`OtherInfo.STONE_MINE.ID`), owce (`UnitInfo.SHEEP.ID`), dziki (`UnitInfo.WILD_BOAR.ID`) i jelenie (`UnitInfo.DEER.ID`).

---

## 3. Dodawanie surowców i limitu populacji (ZAKAZ ujemnego `tribute`!)
1. **CRASH GRY:** **NIGDY** nie używaj `new_effect.tribute` z ujemną wartością `quantity=-amount`, aby dodać graczowi surowce lub pasywny dochód (trickle). W silniku AoE2: DE powoduje to błąd przepełnienia bufora.
2. **BŁĄD API (`BONUS_POPULATION_CAP`):** Dodatkowy limit populacji **NIE JEST** atrybutem obiektu w `ObjectAttribute` (wywołanie `ObjectAttribute.BONUS_POPULATION_CAP` rzuci `AttributeError`). Jest to zasób gracza (*Player Resource*) o ID `32`.
3. **POPRAWNIE:** Do dodawania jakichkolwiek surowców, łupów, pasywnego dochodu (trickle) oraz dodatkowego limitu populacji używaj **wyłącznie** efektu `modify_resource` z dodatnią liczbą całkowitą i `Operation.ADD`:
   ```python
   RES_FOOD = 0
   RES_WOOD = 1
   RES_STONE = 2
   RES_GOLD = 3
   RES_BONUS_POP_CAP = 32  # Dodatkowy limit populacji ponad limit ustawiony w lobby


   def add_player_resource(trigger, player: PlayerId, resource_id: int, amount: int):
       trigger.new_effect.modify_resource(
           source_player=player,
           tribute_list=resource_id,
           operation=Operation.ADD,
           quantity=int(amount),
       )
   ```

---

## 4. Odliczanie czasu na ekranie (BEZWZGLĘDNY ZAKAZ używania `display_timer`!)
1. **CRASH GRY (`display_timer`):** **NIGDY** nie używaj efektu `new_effect.display_timer`! W `AoE2ScenarioParser` wygenerowanie efektu `display_timer` ze znacznikiem `%d` pozostawia niezainicjalizowane pola (`-1`) w strukturze binarnej efektu, co powoduje twardy crash procesu `AoE2DE_s.exe` podczas odświeżania interfejsu C++.
2. **POPRAWNIE:** Do odmierzania czasu zwycięstwa używaj warunku `new_condition.timer(timer=sekundy)`, a do informowania graczy o pozostałym czasie generuj w pętli Pythona serię prostych triggerów czasowych (`new_condition.timer`), które wyświetlają zwykły, statyczny tekst (bez żadnych `%d` ani `%s`!) za pomocą `display_instructions` (na `instruction_panel_position=1`) oraz `send_chat`:
   ```python
   total_minutes = 45
   for rem_min in [45, 40, 35, 30, 25, 20, 15, 10, 5, 3, 2, 1]:
       elapsed_sec = (total_minutes - rem_min) * 60
       t_tick = tm.add_trigger(f"Countdown_{rem_min}m", enabled=True, looping=False)
       if elapsed_sec > 0:
           t_tick.new_condition.timer(timer=elapsed_sec)
       t_tick.new_effect.display_instructions(
           object_list_unit_id=UnitInfo.KING.ID,
           source_player=PlayerId.ONE,
           display_time=310 if rem_min > 5 else 65,
           instruction_panel_position=1,
           message=f"Pozostaly czas: {rem_min} min",
       )
   ```

---

## 5. Modyfikacja statystyk jednostek (`modify_attribute`) i oficjalne ID silnika
1. Nazwy niektórych enumów w `ObjectAttribute` różnią się między wersjami biblioteki (np. brak `MAX_RANGE` lub `RELOAD_TIME`). Zawsze używaj oficjalnych identyfikatorów liczbowych silnika Genie:
   * `ATTR_HIT_POINTS = 0` (Punkty życia)
   * `ATTR_MOVEMENT_SPEED = 5` (Prędkość ruchu)
   * `ATTR_ARMOR = 8` (Pancerz — wymaga podania klasy pancerza!)
   * `ATTR_ATTACK = 9` (Atak — wymaga podania klasy ataku!)
   * `ATTR_ATTACK_RELOAD_TIME = 10` (Czas przeładowania / odstęp między atakami w sekundach)
   * `ATTR_MAXIMUM_RANGE = 12` (Maksymalny zasięg)
   * `ATTR_WORK_RATE = 13` (Tempo pracy / produkcji / leczenia)
   * `ATTR_SEARCH_RADIUS = 23` (Promień wykrywania wroga — przy zwiększaniu zasięgu powyżej 12 zawsze zwiększaj też `SEARCH_RADIUS`)
2. **WAŻNE PRZY ATAKU (`8`) I PANCERZU (`9`):** Modyfikacja ataku lub pancerza wymaga podania `armour_attack_class` (gdzie `4` = Base Melee / walka wręcz, `3` = Base Pierce / strzały) oraz `armour_attack_quantity` zamiast zwykłego `quantity`.

---

## 6. Pułapki w nazwach jednostek i budynków (`UnitInfo` / `BuildingInfo`)
* Ulepszona wieża (Baszta) to **`BuildingInfo.KEEP.ID`** (`235`), a NIE `FORTIFIED_TOWER` (taka stała nie istnieje; istnieje tylko `BuildingInfo.FORTIFIED_WALL.ID`).
* Wóz handlowy to **`UnitInfo.TRADE_CART_EMPTY.ID`** (`128`), a NIE `TRADE_CART`.
* Jednostki bohaterów/specjalne (np. `Imam`) nie znajdują się w `UnitInfo`, lecz w `HeroInfo` (lub używaj bezpośrednio ID: `IMAM_UNIT_ID = 842`).

---

## 7. Ochrona przed `TypeError: unexpected keyword argument` (`safe_call`)
Różne wersje `AoE2ScenarioParser` używają odmiennych nazw niektórych parametrów w `new_effect` i `new_condition` (np. `instruction_panel_position` vs `panel_location`, `object_list_unit_id` vs `object_list`). Zawsze definiuj na początku skryptu poniższe funkcje pomocnicze i używaj ich przy wywołaniach triggerów:

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
    """Bezpiecznie modyfikuje zarówno atrybuty skalarne (HP, zasięg, szybkość), jak i klasy ataku/pancerza."""
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

## 8. Spawnowanie fal AI (Unikanie „węża” jednostek)
Aby jednostki AI atakowały zwartą grupą, spawnowanie w pętli `create_object` rozmieszczaj na siatce (np. `5x5` kratek wokół punktu zbiórki `(spawn_x, spawn_y)`), a zaraz po pętli dodaj w tym samym triggerze efekt `attack_move` obejmujący prostokąt `spawn_x - 6` do `spawn_x + 6` skierowany na współrzędne celu `(target_x, target_y)`.

## 9. Architektura kodu
Wszystkie parametry liczbowe odpowiedzialne za balans (zasoby startowe, czasy fal, wysokość podatków/łupów, bonusy HP/ataku) umieszczaj na górze skryptu w jednym słowniku `BALANCE = {...}`, aby można je było łatwo stroić między meczami.

## 10. Siatka antykolizyjna (`SafeMapGrid`), bezpieczna elewacja i urozmaicenie mapy
1. **ROZDZIAŁ KOLIZJI OBIEKTÓW OD STREF ZAKAZU DRZEW:**
   * **BŁĄD KRYTYCZNY:** Nigdy nie używaj jednego zbioru `occupied` do rezerwowania szerokich stref wokół baz (`radius=12`) lub dróg, jeśli funkcja stawiająca wieśniaków, kopalnie i mury sprawdza ten sam zbiór! Spowoduje to pominięcie spawnowania wszystkich wieśniaków, skauta, złota, kamienia, zwierząt oraz dziury w murach.
   * **POPRAWNIE:** Używaj dwóch osobnych zbiorów w `SafeMapGrid`:
     * `occupied_tiles: set[tuple[int, int]]` — przechowuje **wyłącznie dokładny obrys** postawionych budynków i jednostek. Funkcja `place_unit` w razie kolizji na kafelku `(x, y)` powinna szukać spiralnie najbliższego wolnego kafelka obok (`r = 1..5`), aby żadna jednostka ani kopalnia nigdy nie została pominięta.
     * `no_tree_zones: set[tuple[int, int]]` — przechowuje szerokie strefy ochronne wokół baz (`radius=15`), dróg i bram, które są sprawdzane **wyłącznie** przez `populate_forest_trees`.
2. **BEZPIECZNA ELEWACJA (`apply_smooth_elevation`):**
   * Silnik Genie wymaga, aby sąsiednie kafelki (w tym po przekątnej) różniły się wysokością maksymalnie o `1` ($|\Delta h| \le 1$).
   * Po dodaniu wzgórz i płaskowyżów (`add_hill_plateau`), zawsze wykonaj dwuprzebiegowe wygładzanie Lipschitza (przebieg w przód i w tył przycinający `elev[x][y] <= elev[nx][ny] + 1`) przed zapisaniem wysokości do `tile.elevation`.
3. **BOGACTWO WIZUALNE I TAKTYCZNE MAPY:**
   * Maluj organiczne, nieregularne lasy za pomocą funkcji falowej (`sin(3*angle) + cos(5*angle)`), dodawaj pojedyncze drzewa (*straggler trees*) wokół TC, rzeki (`TERRAIN_WATER = 1`) z brodami (`TERRAIN_SHALLOWS = 4`), skaliste granie z głazami (`ROCK_CLIFF_ID = 623`) oraz Relikty (`RELIC_ID = 285`).
4. **ZAKAZ `display_timer` ORAZ `display_instructions`:** Do wszystkich komunikatów i odliczania czasu używaj wyłącznie `new_effect.send_chat`.

## 11. Kontrola zachowania AI w scenariuszach Co-op (Zakaz pre-spawnu mobilnych jednostek AI w `0:00` i Fazowe Technologie)
1. **DLACZEGO AI ATAKUJE W 1. MINUCIE W DARK AGE:**
   * Jeśli postawisz w `0:00` jakiekolwiek mobilne jednostki wojskowe należące do gracza AI (np. strażników obozów lub Questów), domyślny skrypt AI w **1. sekundzie gry** odciągnie je spod chronionych obiektów i wyśle do ataku na graczy będących w Dark Age!
   * Ponadto, jeśli dasz graczom AI bez wieśniaków wysokie zasoby startowe (`5000+`) i budynki produkcyjne, AI od 1. sekundy zacznie produkować i wysyłać jednostki.
2. **POPRAWNE ROZWIĄZANIE (`Proximity Garrison` + `0` zasobów startowych AI):**
   * Graczom AI opartym na falach triggerowych zawsze ustawiaj zasoby startowe na **`0`** (`food=0, wood=0, gold=0, stone=0`).
   * W `0:00` stawiaj dla AI **wyłącznie budynki** (Zamki, Wieże, Monumenty, Mury, Koszary).
   * Mobilnych strażników Questów i Bastionów spawnuj **dynamicznie przez trigger zbliżeniowy (`objects_in_area`)**, który aktywuje się dopiero wtedy, gdy jednostka gracza ludzkiego podejdzie pod dany obóz na odległość `14–20` kratek.
3. **FAZOWA PROGRESJA FAL I SPECJALIZACJA TECHNOLOGICZNA (`research_technology`):**
   * Dopasowuj skład fal i badania w Kuźni/Uniwersytecie do czasu gry:
     * **0:00 – 11:00:** Czas na rozwój ekonomii.
     * **11:00 – 20:00 (Faza Feudalna):** Jednostki Feudalne + technologie Feudalne (`TECH_FEUDAL_AGE = 101`, `Forging = 67`, `Scale Mail = 74`, `Fletching = 199`).
     * **20:00 – 32:00 (Faza Zamkowa):** Jednostki z Castle Age + technologie Zamkowe (`TECH_CASTLE_AGE = 102`, `Iron Casting = 68`, `Chain Mail = 76`, `Bodkin Arrow = 200`, `Ballistics = 93`, `Bloodlines = 435`, `Husbandry = 39`).
     * **Od 32:00 (Faza Imperialna):** Jednostki Imperialne + technologie Imperialne (`TECH_IMPERIAL_AGE = 103`, `Blast Furnace = 75`, `Plate Mail = 77`, `Plate Barding = 80`, `Bracer = 201`, `Chemistry = 47`, `Siege Engineers = 377`).
   * Różnicuj ulepszenia między frakcjami AI (np. jedna frakcja bada tylko pancerz, druga tylko atak i Balistykę, trzecia szybkość jazdy), aby gracze mogli czytać statystyki w UI i dobierać kontry.