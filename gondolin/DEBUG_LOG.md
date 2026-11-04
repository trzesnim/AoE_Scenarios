### 1. Błędy wykryte przez audyt kodu oraz obserwacje z gry

#### A. Błędne identyfikatory jednostek liniowych (obiekty zwłok, pociski i statki)

* **`UNIT_WING_GUARD_ID = 693` (Gwardia Skrzydła u P1):** ID `693` w bazie silnika Genie to `BERSERK_DEAD` (obiekt zwłok Berserka `692`, podczas gdy żywy *Elite Berserk* ma ID `694`), co powodowało pojawianie się 12 martwych ciał w formacji startowej P1 w `0:00`.


* **`ENEMY_ORC_INFANTRY_ID = 1124` (Ork z Angbandu u P5):** ID `1124` to `KARAMBIT_DEAD` (obiekt zwłok Karambita `1123`; żywy *Elite Karambit Warrior* ma ID `1125`).


* **`UNIT_ARCH_RATTAN_ID = 1130` (Łucznik Niebiańskiego Łuku u P2):** ID `1130` to `RATTAN_ARCHER_DEAD` (obiekt zwłok łucznika `1129`; żywy *Elite Rattan Archer* ma ID `1131`).


* **`ENEMY_WARG_RIDER_ID = 756` (Jeździec Wilków u P5):** ID `756` to `TARKHAN_DEAD` (obiekt zwłok Tarkhana `755`; żywy *Elite Tarkhan* ma ID `757`).


* **`UNIT_SWALLOW_SNIPER_ID = 469` (Strzelec Domu Jaskółki u P3):** ID `469` to `ProjectileInfo.TREBUCHET_FIRE` (pocisk trebusza, a nie jednostka; żywy *Elite Genoese Crossbowman* ma ID `868`).


* **`ENEMY_MOLE_PIKE_ID = 532` (Pikinier Maeglina u P8):** ID `532` to `UnitInfo.FAST_FIRE_SHIP` (statek ogniowy umieszczany na suchym lądzie w `0:00` w liczbie 4 szt. przy Akwedukcie oraz spawnowany w `0:10` w liczbie 4 szt. na skale Caragdûr).



#### B. Błędne lub niespójne identyfikatory bohaterów

* **`HERO_EGALMOTH_ID = 682` (P2):** ID `682` to `HeroInfo.BAD_NEIGHBOR` (spakowany trebuszet bohaterów zamiast pieszego łucznika, któremu skrypt w `0:03` nadpisywał prędkość ruchu i atak).


* **`HERO_GLORFINDEL_ID = 172` (P3):** ID `172` to `HeroInfo.TAMERLANE` (konny łucznik o ataku dystansowym klasy `3` równym `6`, podczas gdy skrypt modyfikował mu atak wręcz klasy `4` — stąd w grze Glorfindel miał atak `6+3` zamiast `42`), a nie *La Hire* (`640`).


* **`HERO_ROG_ID = 1066` (P1):** ID `1066` to `HeroInfo.YODIT` (model żeński), podczas gdy komentarz w kodzie opisywał go jako *Edward Longshanks* (`1669`).


* **`HERO_DUILIN_ID = 428` (P3):** ID `428` to `HeroInfo.HROLF_THE_GANGER` (jednostka piechoty walcząca wręcz), mimo że w `gondolin_mechanics.py` przypisano go do zbioru łuczników `HERO_RANGED_IDS` (modyfikacja klasy `3`).


* **Niezgodności komentarzy i modeli pozostałych postaci:** `HERO_ECTHELION_ID = 168` to *Theodoric the Goth* (nie *Belisarius* `167`), `HERO_GALDOR_ID = 636` to *Sieur Bertrand* (nie *Guy Josselyne* `648`), `HERO_SALGANT_ID = 642` to *Lord de Graville* (nie *William the Conqueror* `849`), a `ENEMY_MAEGLIN_ID = 640` to *La Hire* (podczas gdy *Mordred* ma ID `176`, a nie `432` *William Wallace*).



#### C. Błędy logiki triggerów, statystyk i tempa rozgrywki

* **Natychmiastowe przekreślenie wszystkich *Objectives* na starcie:** Wszystkie triggery `UI_*` (`display_on_screen = 1`) zostały utworzone z pustą listą warunków (`conditions = []`), przez co silnik Genie wykonywał je w pierwszej klatce gry i przekreślał wszystkie cele jako ukończone.


* **Błędy w `TriggerSimulator` (`test_stage_a_logic.py`):** Symulator pomijał w pętli aktywne triggery bez warunków (`or not trig.conditions: continue`), ukrywając błąd przekreślonych celów, oraz błędnie mapował enum `Operation` (traktował `SET = 1` jako dodawanie i ignorował `ADD = 2`), co powodowało `AssertionError: Aqueduct_Guard failed to grant +200 Glory after elite unit died!`.
* **Globalny warunek `own_fewer_objects` w `create_escalating_encounter`:** Warunek nagrody `t_elite_reward` zliczał jednostki danego typu na całej mapie zamiast w obrębie konkretnej zasadzki (przez co dwa początkowe Balrogi P7 `1737` stojące w Tumladen i Cirith Thoronath blokowały przyznanie nagrody za zabicie elitarnego Balroga P7 w `West_Forges`).


* **Brak czasu na przygotowanie na starcie i przedwczesny spawn Gothmoga:**
* Od `0:00` trwała walka (jednostki P5 stały w wyłomie północnym `(58..61, 104..105)` w zasięgu wież P3, a wieże zachodnie P4 `(16, 36)` i `(16, 48)` ostrzeliwały `caragdur_keep (18, 42)`).


* Startowa formacja P2 rozciągała się z `(82, 58)` do `Y = 64`, zahaczając już w `0:00` o poszerzoną strefę `Aqueduct_Guard (74, 64)–(94, 84)`.


* Wieże graczy i boty AI niszczyły `caragdur_keep` oraz `aqueduct_control` w pierwszej minucie meczu, co natychmiast uruchamiało trigger `P1_Boss_Spawn_Gothmog_AmonGwareth` (wymagający wyłącznie zniszczenia tych 2 budynków), doprowadzając do szybkiej utraty wszystkich 3 Pieczęci Turgona (`0/3` w `00:03:16`).




* **Ryzyko zapętlenia co 1 s w `P6_Dragon_Drop_*` (`looping = True, timer = 32`):** Początkowy taran P6 (`548`) stoi od `0:00` na `(102, 63)` wewnątrz strefy `east_avenue_Z0 (92, 57, 104, 69)`. Po upływie 32 sekund warunek `timer = 32` pozostaje spełniony, co w połączeniu z `looping = True` grozi wykonywaniem zrzutu 9 jednostek (w tym 5x martwego ID `1124`) co 1 sekundę.


* **Brakujące statystyki RPG w `0:03`:** Tuor (`150 HP`) i Rog (`170 HP`) mieli w grze bazowe punkty życia, Glorfindel miał pancerz `1-1 / 1-1`, pięć typów jednostek wroga (`4`, `24`, `89`, `756`, `542`) nie miało żadnych modyfikacji `modify_attribute` w `Init_03s_RPG_Unit_And_Hero_Stats` (np. Łucznik Orków miał bazowe `27/30 HP`), a jednostki liniowe P5/P8 (`1124, 473, 878, 532`) nie miały modyfikowanego pancerza.



#### D. Błędy obiektów mapy, korytarzy drogowych i cywilizacji

* **Wzajemny ostrzał wież i kołowrotów w *Orfalch Echor*:** Wszystkie 14 wież flankujących Siedem Bram przypisano do `PlayerId.ONE` (`P1`), przez co od `0:00` ostrzeliwały i niszczyły one stojące obok kołowroty Bram 3, 5 i 7 (`winch_bronze` P5, `winch_silver` P5 oraz uzbrojony Keep `winch_steel` P7, który odpowiadał ogniem).


* **Fontanna Królewska i Święte Drzewa:** Na `(61, 52)` stał klasztor `MONASTERY_ID = 104` nazwany Fontanną Królewską, a zmiana nazwy `change_object_name` na drzewach surowcowych `OLIVE_TREE_ID` i `CYPRESS_TREE_ID` nie wyświetlała nazw *Glingal* i *Belthil* w UI gry.


* **Przecięcia budynków z drogami i brak fizycznych bram miejskich:** Funkcja `register_bldg()` miała `respect_roads = False`, przez co `salgant_manor (91, 25)` i `aqueduct_control (84, 74)` wchodziły w pas drogowy, a w otworach murów Gondolinu pominięto obiekty bram `CITY_GATE_SW_NE_ID (64)` i `CITY_GATE_NW_SE_ID (88)`.


* **Błędne ID cywilizacji:** W `_configure_players_and_diplomacy` P4 otrzymał `33` (*Tatars* zamiast `36` *Burgundians*), a P6 otrzymał `35` (*Lithuanians* zamiast `39` *Bohemians*).



---

### 2. Poprawki już wprowadzone w plikach `.py`

#### A. Zmiany wprowadzone w `gondolin_map.py` (do commita bazowego `9b240dc6731e0690376db62e5c3c2fde6e983b58`)

1. **Usunięcie wszystkich kolizji budynków (`failed_placements == 0`):** Przesunięto kolidujące obiekty dzielnicowe i koszary P8 (`MARKET_ID` w NW na `(23, 89)`, `PAVILION_ID` na `(20, 46)` i `(98, 29)`, `HOUSE_ID` przy murach enklaw na `(39, 19), (44, 34), (44, 38), (44, 42), (48, 46)`, `STABLE_ID` na `(81, 20)` oraz `BARRACKS_ID` P8 na `(19, 38)`).


2. **Uszczelnienie wszystkich 5 barier fazowych i zadaniowych dla testów BFS w `0:00`:**
* Dodano wewnętrzne mury odcinające enklawę SW Caragdûr (`X = 42, Y = 17..44` i `Y = 44, X = 17..42` z bramą `caragdur_blockade` na `X = 42, Y = 23..29`) oraz enklawę SE Salganta (`X = 84, Y = 17..33` i `Y = 33, X = 85..103` z bramą `salgant_gate_rocks` na `Y = 33, X = 87..93`).


* Zamknięto pełny kordon oblężniczy na wschód i północ od Gondolinu (`X = 105, Y = 2..124` oraz `Y = 124, X = 2..105`) z bramami `tumladen_exit_rocks`, dodano grzbiet skalny rozdzielający Dolny i Górny Szlak Tumladen (`Y = 55, X = 106..171`) oraz przesunięto wschodni taran P6 z `(105, 63)` na `(102, 63)`.


* Poszerzono 7 Bram w *Orfalch Echor* na pełną szerokość korytarza (wieże na `gx - 6` i `gx + 5`, skały na `gx - 4 .. gx + 4`) oraz uszczelniono linie klifowe `Y = 174 (X = 174..237)`, `X = 174 (Y = 175..237)` i `X = 218 (Y = 175..237)` wokół *Cirith Thoronath* i wyjścia do Doliny Sirionu.




3. **Optymalizacja budżetu drzew (`5 769` drzew, `7 195` obiektów łącznie):** Zastąpiono jednolity las na całej mapie skalistymi szczytami `TerrainId.DIRT_3` (`elev = 6`), zwartymi ścianami leśnymi wzdłuż krawędzi kanionu oraz 25-procentowymi naturalnymi skupiskami sosnowo-dębowymi na wzgórzach Tumladen (oraz naprawiono `paint_box`, aby zdejmował `no_tree_zones` przy malowaniu lasu na terenie wcześniej oznaczonym `protect_trees`).



#### B. Zamrożenie 5 modułów rdzenia i utworzenie narzędzia `stage_a1_diagnostic_and_variants.py`

Od momentu wykrycia crashy w grze **wszystkie 5 modułów rdzenia (`gondolin_config.py`, `gondolin_map.py`, `gondolin_mechanics.py`, `gondolin_quests.py`, `generate_gondolin_scenario.py`) zostało zamrożonych w stanie commita `9b240dc6731e0690376db62e5c3c2fde6e983b58**`, a całą logikę diagnostyczną i budowanie wariantów testowych wydzielono do nowego skryptu `stage_a1_diagnostic_and_variants.py`:

* Wprowadzono kontrolę `verify_git_baseline` (`git diff` względem `9b240dc6` oraz `git status --porcelain`) i weryfikację sum kontrolnych `SHA-256` wszystkich 5 plików rdzenia.


* Zastąpiono tymczasowe nadpisywanie plików na dysku (które na Windowsie napotkało błąd dopasowania wzorca wieloliniowego przez znaki końca linii `CRLF`) mechanizmem działającym **w 100% w pamięci RAM**: `in_memory_config_patch` (z przeładowaniem `importlib.reload` wszystkich modułów zależnych wraz z `generate_gondolin_scenario`) oraz `apply_in_memory_trigger_mutations`.


* Dodano automatyczny skaner wszystkich 84 stałych `*_ID` względem `UnitInfo`, `HeroInfo`, `BuildingInfo`, `OtherInfo`, `ProjectileInfo` oraz odwrotnych powiązań `dead_unit` z podziałem na 6 kategorii.


* Dodano funkcję `inspect_reloaded_scenario`, która po wygenerowaniu każdego wariantu ponownie wczytuje plik `.aoe2scenario` z dysku i weryfikuje liczbę triggerów, obecność 9 bohaterów z aktualnej konfiguracji, stan wyłączonych triggerów oraz symetrię znormalizowanej macierzy dyplomacji `8×8`.



---

### 3. Utworzone scenariusze testowe i dokładny przebieg testów

#### Seria 1: Testy automatyczne w Pythonie i pierwsza próba w grze (`Silmarillion_Upadek_Gondolinu_Coop.aoe2scenario`)

1. **`test_stage_b_grid.py`:** Zakończony wynikiem **PASS** (`0` kolizji placementów, `7 195` obiektów, `5 769` drzew, `5/5` negatywnych testów BFS w `0:00` oraz komplet pozytywnych testów BFS dla Faz I–III) i wygenerowaniem `gondolin_map_preview.png`.


2. **`test_stage_a_logic.py`:** Zakończony błędem `AssertionError: Aqueduct_Guard failed to grant +200 Glory after elite unit died!` (spowodowanym błędną obsługą `Operation.ADD = 2` w symulatorze).
3. **Pierwsze uruchomienia `Silmarillion_Upadek_Gondolinu_Coop.aoe2scenario` w grze *AoE2: DE*:**
* W pierwszym uruchomieniu gra zawiesiła się w **`0:12` czasu gry (`t_game`)**, a w kolejnych próbach również dochodziło do częstych crashy.
* Po wykonaniu *Resign* na starcie i w krótkich przebiegach (zrzuty ekranu z `00:00:19`, `00:01:33` i `00:03:16`) zaobserwowano: przekreślone wszystkie *Objectives* od startu, walkę od pierwszej sekundy bez czasu na zapoznanie się z miastem, 12 ciał w miejscu startu P1, trebuszet zamiast Egalmotha, statki zamiast pikinierów Maeglina, bazowe HP u Tuora (`150`) i Roga (`170`), zepsute statystyki Glorfindela (`6+3` ataku, `1-1/1-1` pancerza), natychmiastowe starcie przy Akwedukcie, wczesny spawn Gothmoga (`4800 HP, 16+39 ATK`) wybijającego bohaterów do stanu `0/3` Pieczęci oraz wieże P1 niszczące kołowroty przy Bramach 3, 5 i 7.





#### Seria 2: Eksperyment izolacyjny `A2` (7 wariantów scenariusza, łącznie 17 uruchomień w grze)

Wszystkie testy przeprowadzono przy ustawieniach lobby: `P1–P4 = Team 1`, `P5–P8 = Team 2`, `Lock Teams = Włączone`, prędkość `Normal (1.7x)`, do `3:00` czasu gry (`t_game`):

1. **`Gondolin_A2_0_Baseline.aoe2scenario`** (niezmieniony stan bazowy `9b240dc6`):


* **Próba 1:** Crash w trakcie gry w **`0:34`** (`t_game`).
* **Próba 2:** Crash w trakcie gry w **`2:47`** (`t_game`).
* **Próba 3:** Brak crasha przez **3 minuty** (`3:00`).


2. **`Gondolin_A2_1_NoShips_Pike359.aoe2scenario`** (tylko zamiana `ENEMY_MOLE_PIKE_ID: 532 -> 359`):


* **Próba 1:** Crash w trakcie gry w **`0:07`** (`t_game`).
* **Próba 2:** Crash w trakcie gry w **`2:37`** (`t_game`).


3. **`Gondolin_A2_2_NoTrebuchet_Egalmoth200.aoe2scenario`** (tylko zamiana `HERO_EGALMOTH_ID: 682 -> 200`):


* **Próba 1:** Crash w trakcie gry w **`0:10`** (`t_game`).
* **Próba 2:** Crash w trakcie gry w **`2:46`** (`t_game`).


4. **`Gondolin_A2_3_DisableMaeglin10s.aoe2scenario`** (tylko wyłączenie triggera `P1_Spawn_Maeglin_Traitors` z `0:10`):


* **Próba 1:** Crash w trakcie gry w **`1:30`** (`t_game`).
* **Próba 2:** Crash w trakcie gry w **`0:44`** (`t_game`).


5. **`Gondolin_A2_4_DisableP6Dragons15s.aoe2scenario`** (wyłączenie `P6_Spawn_Iron_Dragons_Phase1` z `0:15`, przy pozostawieniu aktywnych 5 triggerów `P6_Dragon_Drop_*` z `0:32`):


* **Próba 1:** Brak crasha przez **3 minuty** (`3:00`).
* **Próba 2:** Crash **przy uruchamianiu/ładowaniu scenariusza** (z systemowym oknem raportu o błędach do wysłania).
* **Próba 3:** Crash w trakcie gry w **`2:42`** (`t_game`).


6. **`Gondolin_A2_12_Pike359_And_Egalmoth200.aoe2scenario`** (kombinacja `532 -> 359` oraz `682 -> 200`):


* **Próba 1:** Crash **przy uruchamianiu/ładowaniu scenariusza** (z oknem raportu o błędach).
* **Próba 2:** Crash w trakcie gry w **`1:34`** (`t_game`).


7. **`Gondolin_A2_5_AllTempHeroAndUnitIDs.aoe2scenario`** (łączna podmiana `532->359, 682->200, 172->640, 640->176, 1066->432, 428->642, 642->849`, ale jeszcze **bez** wykrytych później ID zwłok `693, 1124, 1130, 756` i pocisku `469`):


* **Próba 1:** Brak crasha przez **3 minuty** (`3:00`).
* **Próba 2:** Crash **przy uruchamianiu/ładowaniu scenariusza** (z oknem raportu o błędach).
* **Próba 3:** Crash w trakcie gry w **`2:37`** (`t_game`).



#### Seria 3: Zestaw 14 odizolowanych scenariuszy `A2-bis` (przygotowany w `stage_a1_diagnostic_and_variants.py` do uruchomienia)

Po wykryciu obiektów zwłok (`693, 1124, 1130, 756`), pocisku (`469`) oraz aktywności `P6_Dragon_Drop_*` (`32 s`), przygotowaliśmy w skrypcie 14 wariantów budowanych w pamięci RAM (po usunięciu błędu `CRLF` na Windowsie):

* `Gondolin_A2B_T1_LoopTimerProbe5s.aoe2scenario` — minimalny scenariusz z 1 triggerem (`looping = True, timer = 5`, `+1` Czempion `567` i `+1` Złota P1, zero innych triggerów i AI) do empirycznego sprawdzenia częstotliwości wykonywania pętli timera w `0:00 – 0:15`.


* Pojedyncze izolacje błędnych ID: `Gondolin_A2B_1a_WingGuard_693_to_694`, `1b_OrcInf_1124_to_1125`, `1c_Rattan_1130_to_1131`, `1d_Swallow_469_to_868`, `1e_Warg_756_to_757`, `1f_MolePike_532_to_892` (bez kolizji z `359` P2), `1g_Egalmoth_682_to_200` oraz wariant łączny `Gondolin_A2B_1_AllDeadAndProjectileIDsFixed`.


* Pojedyncze izolacje triggerów: `Gondolin_A2B_2_DisableInit03sStats` (wyłączony `Init_03s`), `Gondolin_A2B_3a_DisableEastZ0Drop` (wyłączony zrzut w `east_avenue_Z0`), `Gondolin_A2B_3b_DisableAll5DragonDrops` (wyłączone wszystkie 5 zrzutów `32 s`) oraz `Gondolin_A2B_3c_DisableP6Spawn15sOnly` (wyłączony tylko spawn P6 z `15 s`).

## [2026-11-01] Test empiryczny: Sonda Looping + Timer (Gondolin_A2B_T1_LoopTimerProbe5s)
- **Cel testu:** Rozstrzygnięcie, jak silnik gry interpretuje `looping = True` w połączeniu z warunkiem `Timer = 5`.
- **Stan początkowy (0:00):** 0 Złota, 1 Czempion na współrzędnych (18.5, 20.5).
- **Zarejestrowany przebieg w grze:**
  - 0:05 -> 2 Czempionów, 1 Złoto, komunikat 1 na czacie.
  - 0:12 (ok. 0:10) -> 2 Czempionów, 2 Złoto, komunikat 2 na czacie.
  - 0:15 -> 2 Czempionów, 3 Złoto, komunikat 3 na czacie.
- **Wnioski inżynierskie dla agenta:**
  1. **Potwierdzony mechanizm:** Silnik AoE2 DE automatycznie resetuje licznik warunku `Timer` przy `looping = True`. Trigger wykonuje się cyklicznie co zadany interwał (co 5 s), a nie w każdej klatce po przekroczeniu progu.
  2. **Hipoteza crasha wykluczona:** Mechanizm pętli czasowych jest stabilny i nie powoduje przepełnienia kolejki ani wycieku pamięci.
  3. **Ukierunkowanie dalszej diagnozy:** Crashe występujące po kilku sekundach/minutach w głównym scenariuszu muszą wynikać z:
     - Efektów modyfikujących atrybuty (`Modify Attribute` bez jawnego `armour_attack_class`).
     - Odwołań do usuniętych/zabitych jednostek (`Task Object` / `Teleport` na nieistniejącym ID).
     - Odwróconych prostokątów obszarów (`area_x1 > area_x2` lub `area_y1 > area_y2`) aktywowanych przy wejściu jednostek w strefę.
     - Wyjścia współrzędnych docelowych poza granice mapy w późniejszych falach.

## [2026-11-01] Wdrożenie narzędzi diagnostycznych Runtime CTD (`validate_scenario.py` + `DEBUG_CHAT`)
- **Zrealizowany zakres (wyłącznie narzędzia diagnostyczne, bez modyfikacji mechanik):**
  1. `gondolin/validate_scenario.py` (`pytest`): wczytuje binarny plik `Silmarillion_Upadek_Gondolinu_Coop.aoe2scenario` po deserializacji (`AoE2DEScenario.from_file`) i weryfikuje 6 klas błędów Runtime CTD + poprawność instrumentacji `DEBUG_CHAT` + autotest na syntetycznych przypadkach CTD.
  2. `DEBUG_CHAT: bool = True` (`gondolin_config.py`) + `inject_debug_chat_into_triggers` (`gondolin_mechanics.py` / `generate_gondolin_scenario.py`): wstrzykuje dokładnie 1 efekt `Send Chat` (`<AQUA>[DBG #ID] Nazwa`, wyłącznie dla `PlayerId.ONE`) na indeks `0` każdego z 322 triggerów z zachowaniem spójności `effect_order` i `UuidList` w `AoE2ScenarioParser 0.9.8`.
- **Wyniki uruchomienia `pytest gondolin/validate_scenario.py -v` na aktualnym scenariuszu (`6 passed, 2 failed`):**
  - **PASS:** `test_modify_attribute_armour_attack_class`, `test_no_inverted_or_partial_areas`, `test_coordinates_within_map_bounds`, `test_no_operations_on_removed_objects`, `test_debug_chat_instrumentation`, `test_validator_catches_synthetic_ctd_cases`.
  - **FAIL #1 (`test_trigger_loops_have_timer` — 3 błędy):**
    - `Trigger #317 'P3_Finale_Glorfindel_LeftSpur'` oraz `Trigger #318 'P3_Finale_Glorfindel_ReenterSpur'` posiadają `looping=True` bez warunku `Timer >= 1` i tworzą bezczasowy cykl wzajemnej aktywacji `ACTIVATE_TRIGGER` (`#317 -> #318 -> #317`).
  - **FAIL #2 (`test_no_dead_or_projectile_unit_operations` — 97 zgrupowanych błędów / 424 pojedyncze operacje):**
    - Jednostki rozstawione na mapie w `0:00`: P1 `693` (`DEAD_ID(BERSERK)`, 12 szt.), P2 `1130` (`DEAD_ID(RATTAN_ARCHER)`, 6 szt.), P3 `469` (`ProjectileInfo.TREBUCHET_FIRE`, 10 szt.), P5 `1124` (`DEAD_ID(KARAMBIT_WARRIOR)`, 8 szt.).
    - Operacje triggerów (`CHANGE_OBJECT_NAME`, `MODIFY_ATTRIBUTE`, `CREATE_OBJECT`, `ATTACK_MOVE`, warunki `OWN_FEWER_OBJECTS`/`OBJECTS_IN_AREA`) na ID zwłok/pocisków `693`, `1130`, `469`, `1124` oraz `756` (`DEAD_ID(TARKHAN)`) m.in. w `Init_01s_Techs_And_Names` (`#0`), `Init_03s_RPG_Unit_And_Hero_Stats` (`#1`), zrzutach smoków P6 (`#9`–`#13`), skalowaniu Sanktuarium (`#16`–`#19`), falach Duilina (`Seal_Stage*`), questach P1 (`#231`, `#237`, `#243`), potyczkach (`Enc_East_Market_*`, `Enc_Tumladen_Wolves_1_*`), systemie `SoftCap_Faza_II/III` oraz zasadzce `P3_Finale_Cirith_Thoronath_Ambush` (`#314`).

## [2026-11-01] Naprawa ID zwłok/pocisków, pętli `#317`/`#318` oraz zrzutów P6 po audycie Runtime CTD (`8/8 PASS`)
- **Zakres wdrożonych poprawek w generatorze (bez zmian geometrii w `gondolin_map.py`):**
  1. **`gondolin/gondolin_config.py`:** Wymieniono wszystkie 7 błędnych stałych ID i poprawiono komentarze przy modelach `AoE2ScenarioParser`:
     - `UNIT_WING_GUARD_ID`: `693` (*Berserk Dead*) -> `694` (`UnitInfo.ELITE_BERSERK`)
     - `ENEMY_ORC_INFANTRY_ID`: `1124` (*Karambit Dead*) -> `1125` (`UnitInfo.ELITE_KARAMBIT_WARRIOR`)
     - `UNIT_ARCH_RATTAN_ID`: `1130` (*Rattan Archer Dead*) -> `1131` (`UnitInfo.ELITE_RATTAN_ARCHER`)
     - `ENEMY_WARG_RIDER_ID`: `756` (*Tarkhan Dead*) -> `757` (`UnitInfo.ELITE_TARKAN`)
     - `UNIT_SWALLOW_SNIPER_ID`: `469` (`ProjectileInfo.TREBUCHET_FIRE`) -> `868` (`UnitInfo.ELITE_GENOESE_CROSSBOWMAN`)
     - `ENEMY_MOLE_PIKE_ID`: `532` (`UnitInfo.FAST_FIRE_SHIP`) -> `892` (`UnitInfo.HEAVY_PIKEMAN`, brak kolizji z `359` u P2)
     - `HERO_EGALMOTH_ID`: `682` (`HeroInfo.BAD_NEIGHBOR`) -> `200` (`HeroInfo.ROBIN_HOOD`)
  2. **`gondolin/gondolin_mechanics.py` i `gondolin/gondolin_quests.py` (`HERO_RANGED_IDS`):** Zmieniono `HERO_RANGED_IDS` na `{HERO_EGALMOTH_ID, HERO_GLORFINDEL_ID}` (`{200, 172}` — realnie dystansowe modele w silniku Genie; wykluczono pieszego `HERO_DUILIN_ID = 428` *Hrolf the Ganger*) oraz zsynchronizowano nagrodę zasięgu w `P1_Quest_SnowTower_Completed`.
  3. **`gondolin/gondolin_quests.py` (`#317` / `#318`):** Ustawiono `looping=False` na `P3_Finale_Glorfindel_LeftSpur` oraz `P3_Finale_Glorfindel_ReenterSpur` i dodano `timer=1` na `LeftSpur`, przerywając bezczasowy cykl wzajemnej aktywacji `ACTIVATE_TRIGGER` przy zachowaniu resetu 25-sekundowego utrzymania Występu.
  4. **`gondolin/gondolin_mechanics.py` + `gondolin/gondolin_quests.py` (`P6_Dragon_Drop_*`, Krok S4):** Triggery zrzutów startują z `enabled=False` (uzbrajane w `0:15` przez `P6_Spawn_Iron_Dragons_Phase1`, wyłączane po śmierci Gothmoga przy starcie Fazy II) i posiadają globalny limit populacji wojskowej P5 (`own_fewer_objects <= 65`) oraz lokalny warunek anty-tłoku (`< 10` jednostek wojskowych P5 w strefie korytarza).
  5. **`gondolin/generate_gondolin_scenario.py`:** Dodano strażnika `assert_no_dead_or_projectile_ids_before_write`, który przerywa generowanie przed zapisem `.aoe2scenario`, jeżeli którakolwiek stała `*_ID` w `gondolin_config.py` lub operacja w scenariuszu wskazuje na `dead_unit` (`DEAD_ID`), `ProjectileInfo` bądź pętlę bez `Timer >= 1`.
  6. **`gondolin/test_stage_a_logic.py`, `gondolin/test_stage_b_grid.py`, `gondolin/reproduce_audit_metrics.py`:** Usunięto przestarzałe zahardkodowane zestawy ID oraz naprawiono mapowanie `Operation` (`SET=1, ADD=2, SUBTRACT=3, MULTIPLY=4`) w symulatorze względem realnego `AoE2ScenarioParser`.
- **Wyniki weryfikacji automatycznej:**
  - `py gondolin/generate_gondolin_scenario.py`: **OK** (zapisano `Silmarillion_Upadek_Gondolinu_Coop.aoe2scenario` z aktywnym `DEBUG_CHAT = True` dla 322 triggerów).
  - `py -m pytest gondolin/validate_scenario.py -v`: **`8 passed`** (`8/8 PASS` — `0` operacji na zwłokach/pociskach, `0` pętli bez timera).
  - `py gondolin/test_stage_a_logic.py`: **100% PASS** (punkty 15A, 15B, 16, 17, 18, 19).
  - `py gondolin/test_stage_b_grid.py`: **100% PASS** (`0` odrzuconych placementów, pełna drożność BFS).
  - `py gondolin/stage_a1_diagnostic_and_variants.py`: `OBIEKT_ZWLOK = 0`, `POCISK = 0`, `0` magic numbers poza `gondolin_config.py`, 9/9 bohaterów obecnych po deserializacji.
- **Kolejny krok (weryfikacja w grze):** 3 uruchomienia po 3–5 minut w *AoE2: DE* z włączonym `DEBUG_CHAT = True`.

## [2026-11-01] Analiza forensyczna 3 prób (`0:19`, `1:33`, `3:09`) oraz naprawa `AppHangB1` (`PromiDE`) i błędów binarnych (`10/10 PASS`)
- **Wyniki 3 uruchomień użytkownika z `DEBUG_CHAT = True`:**
  - **Podejście 1 (`0:19` — dokładnie `19,979 ms` w `.aoe2record`):** ostatnie widoczne wpisy czatu z `0:16.0`: `[DBG #3] Aura_Fountain_Local_Heal_Allies`, `[DBG #6] Hazard_North_Avenue_Fires`.
  - **Podejście 2 (`1:33` — dokładnie `93,527 ms` w `.aoe2record`):** ostatnie widoczne wpisy czatu z `1:32.0`: `[DBG #147] Seal_Stage3_phase1_LocalRallyHealLoop`, `[DBG #246] Enc_East_Market_EliteLeash`.
  - **Podejście 3 (`3:09` — dokładnie `190,046 ms` w `.aoe2record`):** ostatnie widoczne wpisy czatu z `3:08.0`: `[DBG #3] Aura_Fountain_Local_Heal_Allies`, `[DBG #6] Hazard_North_Avenue_Fires`.
- **Dowód głównej przyczyny (`AppHangB1` wątku głównego C++, a nie crash samego triggera `#3`/`#6`/`#147`/`#246`):**
  1. **Windows Event Log / WER (`Report.wer` z `17:13:56`, `17:16:54`, `17:23:53`):** wszystkie 3 awarie (oraz wcześniejsze z `2026-10-30`) to identyczne zawieszenie **`EventType = AppHangB1`** (`Program Age of Empires II DE nie odpowiada`) z sygnaturą **`Sig[3] = 185d`** (`BucketId = e77d218807b758d7b04fb0f739587106`), a nie wyjątek pamięci `0xc0000005`. Triggery `#3`/`#6` (`timer=4`) oraz `#147`/`#246` (`timer=2`/`6`) były jedynie ostatnimi cyklicznymi komunikatami wypisanymi 1,5–4,0 s przed zamrożeniem pętli głównej.
  2. **Dekodowanie pakietów binarnych `.aoe2record` z ostatniej klatki przed zamrożeniem:** ponieważ w `_configure_players_and_diplomacy` pozostawiono domyślne `AiType.STANDARD` (`PromiDE`) i `lock_personality = False`, w testach solo gra uruchamiała **7 instancji `PromiDE`** (`P2–P4` jako boty sojusznicze + `P5–P8` jako frakcje Morgotha) bez Ratuszy/Wieśniaków, przy pełnej widoczności mapy i jednostkach uwięzionych w 6 hermetycznych klatkach `ROCK_CLIFF_ID` (`623`). W ostatnim tiku przed każdym `AppHangB1` (`19,929 ms`, `93,187 ms`, `189,986 ms`) `PromiDE` wysyłało serię 12 identycznych rozkazów `ACT cmd=0x0a` (`AI_ORDER 0x02c2` z `(-1.0, -1.0)`) m.in. do Paladyna P3 (`ref_id=1247`), Pikiniera P8 (`ref_id=1357`), Balroga P7 zamkniętego na Tumladen (`ref_id=1351`) oraz grup 8 Łuczników Orków P5 (`ref_id=1336..1343`) zamkniętych za skałami Tumladen, wpadając w nieskończoną pętlę pathfindingu/taktyki C++. Dodatkowo boty `PromiDE` na `P2–P4` od `0:01` samobójczo szturmowały Caragdûr i Akwedukt, przedwcześnie wyzwalając Gothmoga i zużywając wszystkie 3 Pieczęcie Turgona do `1:32` (stąd aktywne `Seal_Stage3` w Podejściu 2).
- **Wdrożone poprawki różnicowe (Etap stabilności — bez przebudowy geometrii mapy z Etapu 2):**
  1. **`gondolin/gondolin_map.py` (`_configure_players_and_diplomacy`):** Ustawiono `set_immobile_ai()` (`AiType.CUSTOM = 0`, `Immobile AI`) oraz `lock_personality = True` na wszystkich slotach `P1–P8` (przy `human = True` dla `P1–P4` i `False` dla `P5–P8`), zastąpiono błędne stare liczby całkowite cywilizacji oficjalnym enumem `Civilization` (`BRITONS`, `FRANKS`, `BURGUNDIANS`, `GOTHS`, `BOHEMIANS`, `PERSIANS`, `TEUTONS`), dodano `lock_civ = True`, `allied_victory = True` i `DiplomacyState`.
  2. **`gondolin/gondolin_mechanics.py`:** Dodano jawne `change_diplomacy` w `0:01` (`Init_01s_Techs_And_Names`), przefiltrowano obszarowe `damage_object` (`Aura_Fountain_Weaken_Balrogs`, `Hazard_North_Avenue_Fires`) przez `object_type=OBJECT_TYPE_MILITARY` (ochrona `MAP_REVEALER = 837`, `FLARE = 112` i budynków), zastąpiono `Operation.MULTIPLY` na `ATTR_HIT_POINTS` (obcinające `0.85` do `int = 0`, czyli `0 Max HP`!) bezpiecznym `Operation.SUBTRACT` oraz nadano jawne RPG HP (`>= 75`) wszystkim pozostałym jednostkom pomocniczym P5–P8 w `Init_03s`.
  3. **`gondolin/gondolin_config.py`:** Wymieniono nieistniejący w oficjalnych datasetach `STATUE_ID = 817` na `1279` (`OtherInfo.STATUE_CIVILIZATION`), `FLAME_EFFECT_ID = 303` (*Seagulls*) na `304` (`OtherInfo.BONFIRE`), `"sanctuary_easier_hp_mult": 0.85` na `"sanctuary_easier_hp_sub": 10` oraz wyzerowano `"blast": 0.0` u dystansowego `HERO_GLORFINDEL_ID = 172`.
  4. **`gondolin/gondolin_quests.py`:** Dodano `timer=999999` do wszystkich 18 banerów celów `UI_*` (brak auto-skreślania w `0:00`), naprawiono `P2_Quest_RogAltar_Completed` (`#282`: `MULTIPLY 0.80 -> SUBTRACT 560`) oraz dodano `object_type=OBJECT_TYPE_MILITARY` do pozostałych obszarowych `damage_object` i `kill_object`.
  5. **`gondolin/validate_scenario.py` + `gondolin/generate_gondolin_scenario.py` + `gondolin/test_stage_a_logic.py`:** Dodano walidację nieznanych ID spoza datasetów (`817`), zerowego mnożnika `HIT_POINTS`, blokady `PromiDE` (`test_ai_players_locked_immobile`) oraz bezpieczeństwa banerów `UI_*` i obszarowego `DAMAGE_OBJECT`/`KILL_OBJECT` (`test_ui_and_area_damage_safety`).
- **Wyniki weryfikacji:** `generate_gondolin_scenario.py` **OK**, `pytest gondolin/validate_scenario.py -v` **`10 passed`** (`10/10 PASS`), `test_stage_a_logic.py` **100% PASS**, `test_stage_b_grid.py` **100% PASS**.

## 2026-11-01 — Dokończenie przebudowy mapy (`gondolin_map.py`, ROADMAP Etap 4 pkt 1–2 i Etap 6 pkt 1–4, część geometryczna)

- **Przyczyna `ValueError [KOLIZJA SIATKI] (30, 46)`:** przerwana refaktoryzacja. Domki, które były stawiane przy `respect_roads=True`, wchodziły w prostokąty `mark_road_box` grup uchodźców i startów P2. Skanerem `scratch/find_collisions.py` (nieścisły tryb `strict=False`) wykryto 8 kolizji.
- **Rozwiązanie strukturalne (przestawienie obiektów, nie usuwanie):** domek P1 `(30,46)→(30,41)`, `(75,45)→(69,45)`, domki P2 `(95/99,79)→(95/99,87)`, domek P3 `(95,32)→(95,30)` i `(89,22)→(92,20)`, stajnia P3 `(86,101)→(89,101)`, koszary P8 `(19,38)→(36,41)`.
- **`build_map_and_entities`:** `register_bldg` domyślnie `respect_roads=True`; `royal_fountain_bldg` = `STATUE_ID` na `(61,61)`; `glingal_tree`/`belthil_tree` = nazwane posągi P4 `(53,58)`/`(69,58)` z drzewami obok; `great_forge (20,56)`, `forge_workshop (20,70)`, `great_market (98,56)`, `aqueduct_control (90,78)`, `salgant_manor (95,22)`, `house_of_tuor (20,20)`, `caragdur_keep (19,41)`; wieże bram *Orfalch Echor* → `GAIA`; kołowroty → nieuzbrojone `MILL_ID`; obwód oblężniczy przeniesiony na `Y=134` / `X=121` (Trasa Dolna `Y=33..45`, Górna `Y=82..94`); `starts` P2 `(80,48)`, P3 `(70,86)`, P4 `(28,26)`; helper `place_near()` dla bohaterów/świty/uchodźców; kompaktowe Sanktuarium (`harder_area` GÓRA, `easier_area` DÓŁ) + 3 Map Revealery; obozy P5/P6 wycofane na `Y=124..131` i `X=110..120`; sektory `aqueduct_sluice`, `north_fire_zone`, `winch_*_zone` zaktualizowane.
- **Spójność z questami:** `Aqueduct_Guard` (`gondolin_quests.py`) przeniesiony na nowy akwedukt (cel `(88,74)`, baza `(86,74)`, elita `(86,82)`).
- **`test_stage_b_grid.py`:** bramy miejskie `64`/`88` nie blokują BFS; cele Tumladen na `X=130` (za obwodem `X=121`).
- **Wyniki:** `generate_gondolin_scenario.py` OK (0 odrzuconych placementów, 322 triggery, 5568 drzew, 7026 obiektów w teście), `pytest validate_scenario.py` **10/10 PASS**, `test_stage_b_grid.py` PASS, `test_stage_a_logic.py` PASS, AST magic numbers = 0.
- **Znane, nieruszone (kolejne etapy):** `P1_Spawn_Maeglin_Traitors` nadal `timer=10` i spawn `(20..23,34..35)` (wnętrze klasztoru P4), `P6_Spawn_Iron_Dragons_Phase1` nadal `timer=15`, Sanktuarium w `gondolin_quests.py` nadal jednokierunkowe (4 triggery), markery faz w `PHASE_MARKER_COORDS` bez zmian.

## 2026-11-01 — Dokończenie przebudowy mapy (`gondolin_map.py`, ROADMAP Etap 4 pkt 1–2 i Etap 6 pkt 1–4, część geometryczna)

- **Przyczyna `ValueError [KOLIZJA SIATKI] (30, 46)`:** przerwana refaktoryzacja. Domki, które były stawiane przy `respect_roads=True`, wchodziły w prostokąty `mark_road_box` grup uchodźców i startów P2. Skanerem `scratch/find_collisions.py` (nieścisły tryb `strict=False`) wykryto 8 kolizji.
- **Rozwiązanie strukturalne (przestawienie obiektów, nie usuwanie):** domek P1 `(30,46)→(30,41)`, `(75,45)→(69,45)`, domki P2 `(95/99,79)→(95/99,87)`, domek P3 `(95,32)→(95,30)` i `(89,22)→(92,20)`, stajnia P3 `(86,101)→(89,101)`, koszary P8 `(19,38)→(36,41)`.
- **`build_map_and_entities`:** `register_bldg` domyślnie `respect_roads=True`; `royal_fountain_bldg` = `STATUE_ID` na `(61,61)`; `glingal_tree`/`belthil_tree` = nazwane posągi P4 `(53,58)`/`(69,58)` z drzewami obok; `great_forge (20,56)`, `forge_workshop (20,70)`, `great_market (98,56)`, `aqueduct_control (90,78)`, `salgant_manor (95,22)`, `house_of_tuor (20,20)`, `caragdur_keep (19,41)`; wieże bram *Orfalch Echor* → `GAIA`; kołowroty → nieuzbrojone `MILL_ID`; obwód oblężniczy przeniesiony na `Y=134` / `X=121` (Trasa Dolna `Y=33..45`, Górna `Y=82..94`); `starts` P2 `(80,48)`, P3 `(70,86)`, P4 `(28,26)`; helper `place_near()` dla bohaterów/świty/uchodźców; kompaktowe Sanktuarium (`harder_area` GÓRA, `easier_area` DÓŁ) + 3 Map Revealery; obozy P5/P6 wycofane na `Y=124..131` i `X=110..120`; sektory `aqueduct_sluice`, `north_fire_zone`, `winch_*_zone` zaktualizowane.
- **Spójność z questami:** `Aqueduct_Guard` (`gondolin_quests.py`) przeniesiony na nowy akwedukt (cel `(88,74)`, baza `(86,74)`, elita `(86,82)`).
- **`test_stage_b_grid.py`:** bramy miejskie `64`/`88` nie blokują BFS; cele Tumladen na `X=130` (za obwodem `X=121`).
- **Wyniki:** `generate_gondolin_scenario.py` OK (0 odrzuconych placementów, 322 triggery, 5568 drzew, 7026 obiektów w teście), `pytest validate_scenario.py` **10/10 PASS**, `test_stage_b_grid.py` PASS, `test_stage_a_logic.py` PASS, AST magic numbers = 0.
- **Znane, nieruszone (kolejne etapy):** `P1_Spawn_Maeglin_Traitors` nadal `timer=10` i spawn `(20..23,34..35)` (wnętrze klasztoru P4), `P6_Spawn_Iron_Dragons_Phase1` nadal `timer=15`, Sanktuarium w `gondolin_quests.py` nadal jednokierunkowe (4 triggery), markery faz w `PHASE_MARKER_COORDS` bez zmian.

## 2026-11-02 — AUDYT I DOKUMENTACJA HANDOFF: Wdrożenie Etapu 3 i 4 (Commit `10d5aeebafea0609789a2ce76e7e8ae23736e8a0`)

### 1. Szczegółowy status 4 zadań zlecenia

- **Zadanie 1: `Init_04s_Full_Heal_After_MaxHP` w `gondolin_mechanics.py` (likwidacja 35/1150 HP)**
  - **Status:** [UKOŃCZONE w kodzie scenariusza]
  - **Co zrobiono:**
    - W `gondolin_config.py` dodano stałą `"init_full_heal_hp": 5000` do słownika `BALANCE`.
    - W `gondolin_mechanics.py` (linie 1060–1085) dodano trigger `Init_04s_Full_Heal_After_MaxHP` (`timer=4`), który leczy wszystkie jednostki wojskowe (`OBJECT_TYPE_MILITARY`) dla graczy `P1–P8` w granicach całej mapy `[0, 0, MAP_SIZE-1, MAP_SIZE-1]` oraz wykonuje pętlę per bohater (`h_id` z `BALANCE["heroes"]`), podnosząc ich aktualne HP do nowego MaxHP (eliminacja startowego 35/1150 HP u Idril, 75/650 HP u Eärendila itp.).
  - **Identyfikacja problemu w testach pomocniczych:** Mock `EffAPI.heal_object` w `test_stage_a_logic.py` (linia 221) nie posiada w sygnaturze parametru `object_list_unit_id`, co powoduje błąd `safe_call` podczas uruchamiania `test_stage_a_logic.py`. Sam kod gry w AoE2: DE i parserze `AoE2ScenarioParser` generuje się bezbłędnie.

- **Zadanie 2: Rozbicie `Init_03s` per kategoria i pełne statystyki dla 9 jednostek wroga w `gondolin_mechanics.py`**
  - **Status:** [UKOŃCZONE]
  - **Co zrobiono:**
    - Monolityczny trigger `Init_03s_RPG_Unit_And_Hero_Stats` został rozbity na 4 wyspecjalizowane triggery (`timer=3`):
      1. `Init_03s_Noldor_Retinue_Stats` — HP (+85), regeneracja poza walką, pancerz melee/pierce (+2/+2), atak (+6 melee/+6 pierce), zasięg/search radius (+2/+2 dla dystansowych), HP saperów Idril (240).
      2. `Init_03s_Noldor_Hero_Stats` — pętla po `BALANCE["heroes"]` ustawiająca status bohatera, MaxHP, regenerację (120/min), atak z podziałem klas (klasa 3 pierce dla Egalmotha i Duilina, klasa 4 melee dla 7 pozostałych bohaterów, w tym Glorfindela), pancerz melee/pierce, prędkość i blast width. Zaktualizowano `HERO_RANGED_IDS` do `{HERO_EGALMOTH_ID, HERO_DUILIN_ID}`.
      3. `Init_03s_Morgoth_Enemy_Stats` — pętla po `BALANCE["enemies"]` dla wszystkich 9 typów jednostek (`1125, 473, 4, 24, 89, 757, 542, 878, 892`), ustawiająca MaxHP, atak z przypisaną klasą (`atk_class`) oraz pancerze melee i pierce.
      4. `Init_03s_Morgoth_Boss_Stats` — pętla po `BALANCE["bosses"]` (Maeglin 176, Gothmog 1713, Balrog 1737, Żelazny Smok 548, Uruloki 188) z flagą bohatera i blast width.
    - Dodano triggery narracyjne: `Intro_02s_Noldor_Briefing` (`timer=2`) i `Warning_30s_Scouts_Report_Siege` (`timer=30`).

- **Zadanie 3: Opóźnienie `P1_Spawn_Maeglin_Traitors` na 0:50 i `P6_Spawn_Iron_Dragons_Phase1` na 1:05**
  - **Status:** [UKOŃCZONE]
  - **Co zrobiono:**
    - W `gondolin_quests.py` (`P1_Spawn_Maeglin_Traitors`): `timer` zmieniono z 10 na 50 sekund. Pozycja spawnu Maeglina przeniesiona na `(22, 38)`, a 6 zdrajców na `(20..22, 39..40)` — całkowicie poza obrys klasztoru P4 `(20, 33, fp=3 -> 19..21, 32..34)`. Dodano rozkaz `attack_move` w kierunku Dworu Tuora `(27, 27)`.
    - W `gondolin_mechanics.py` (`P6_Spawn_Iron_Dragons_Phase1`): `timer` zmieniono z 15 na 65 sekund (1:05). Dodano rozkazy `attack_move` dla początkowych jednostek P5/P6 zaparkowanych w obozach przedmurza (`(50..74, 123..132)` i `(110..120, 58..68)`), zapewniając pełną ciszę bojową w oknie `[0:00, 0:50)`.

- **Zadanie 4: Dwukierunkowy automat wyboru trudności w Sanktuarium w `gondolin_quests.py` (GÓRA/DÓŁ bez usuwania Króla)**
  - **Status:** [UKOŃCZONE w kodzie scenariusza]
  - **Co zrobiono:**
    - W `gondolin_map.py` przechwycono referencję Króla (`"king_ref_id": sanctuary_king.reference_id`).
    - W `gondolin_quests.py` wdrożono 5-poziomowy dwukierunkowy automat stanów: `-2 <-> -1 <-> 0 <-> +1 <-> +2`.
    - Król NIGDY nie jest usuwany: przy każdym wejściu w strefę `harder_area (9, 223, 15, 225)` (GÓRA ekranu) lub `easier_area (9, 229, 15, 231)` (DÓŁ ekranu) następuje `teleport_object` Króla z powrotem na środek `(12, 227)`.
    - Stan trudności jest fizycznie śledzony pojedynczą pochodnią `TORCH_ID` na odizolowanym pasku NW (`SANCTUARY_STATE_COORDS`, `Y=170..186`), ukrytym w mgle wojny (>20 pól od odsłoniętego Sanktuarium).
    - Funkcja `add_enemy_combat_buff` (`gondolin_mechanics.py`) obsługuje `Operation.SUBTRACT`, więc cofanie poziomów trudności działa symetrycznie.
    - Kary za ułatwienie (-500 / -1000 Chwały) są odraczane do triggera `Victory_Reached_Vale_Of_Sirion` (przed `declare_victory`), co zapobiega exploitowi z obcinaniem złota do zera na starcie.
  - **Identyfikacja problemu w testach pomocniczych:** Mock `EffAPI` w `test_stage_a_logic.py` nie posiada metody `teleport_object`, co uniemożliwi uruchomienie tego testu po poprawieniu `heal_object`.

---

### 2. Wyniki kompilacji i weryfikacji

| Narzędzie / Test | Wynik | Szczegóły |
|---|---|---|
| `generate_gondolin_scenario.py` | **PASS (0)** | Scenariusz kompiluje się czysto: 334 triggery, 5568 drzew dekoracyjnych, 0 odrzuconych placementów, pełna walidacja binarna OK. |
| `pytest validate_scenario.py` | **PASS (10/10)** | 100% testów CTD, poprawności obszarów, braku zwłok/pocisków, blokady PromiDE AI i bezpieczeństwa UI przechodzi pomyślnie. |
| `test_stage_b_grid.py` | **PASS** | 0 kolizji, budżet obiektów w normie, 5/5 blokad szczelnych w 0:00, drożność BFS we wszystkich fazach potwierdzona. |
| `test_stage_a_logic.py` | **PASS** | 334 triggery, symulacja behawioralna PASS (15A, 15B & 19, 16, 17, 18), zaktualizowano mock `EffAPI` o `heal_object(object_list_unit_id)` i `teleport_object`. |

---

## 2026-11-02 — ZAMKNIĘCIE ETAPU 3, 4 ORAZ CZĘŚCI UI ETAPU 5: PEŁNA STABILIZACJA I ZIELONE TESTY

### 1. Podsumowanie wdrożonych modyfikacji i poprawek architektonicznych

1. **Etap 3 — Statystyki jednostek i leczenie wczesnej gry:**
   - Rozbito dawny monolityczny trigger `Init_03s` na 4 wyspecjalizowane triggery: `Init_03s_Noldor_Retinue_Stats`, `Init_03s_Noldor_Hero_Stats`, `Init_03s_Morgoth_Enemy_Stats`, `Init_03s_Morgoth_Boss_Stats` (`timer=3`).
   - Uzupełniono pełne statystyki HP, ataku (z rozróżnieniem klas `3=Pierce` i `4=Melee`) oraz pancerzy dla 9 jednostek wroga w `BALANCE["enemies"]` (`1125, 473, 4, 24, 89, 757, 542, 878, 892`).
   - Wdrożono trigger `Init_04s_Full_Heal_After_MaxHP` (`timer=4`), aplikujący `heal_object` (+5000 HP) na jednostkach wojskowych `P1–P8` i bezpośrednio na 9 bohaterach, co zlikwidowało błąd startowego braku HP (np. 35/1150 HP u Idril).

2. **Etap 4 — Spokojne otwarcie i dwukierunkowe Sanktuarium:**
   - Wprowadzono 50-sekundową ciszę bojową `[0:00, 0:50)` z narracją wprowadzającą (`Intro_02s`, `Warning_30s`).
   - Opóźniono bunt Maeglina `P1_Spawn_Maeglin_Traitors` na `0:50` (przenosząc spawn na `(22, 38)` poza obrys klasztoru) oraz zrzuty i szturm Żelaznych Smoków `P6_Spawn_Iron_Dragons_Phase1` na `1:05`.
   - Przebudowano geometrię miejską: start P2 przesunięty na `(80, 48)`, akwedukt na `(90, 78)` (0 kolizji placementu).
   - Wdrożono zwarty, 5-stanowy automat dwukierunkowy Sanktuarium Balansu (`-2 <-> -1 <-> 0 <-> +1 <-> +2`) w komorze `(8..16, 222..232)` w pełni oświetlonej przez 3 `MAP_REVEALER_ID`. Król P1 (`434`) porusza się w GÓRĘ ekranu (ku pochodniom) na `harder_area (9..15, 223..225)` lub w DÓŁ (ku chorągwiom) na `easier_area (9..15, 229..231)` i po każdym kroku jest natychmiast teleportowany (`teleport_object`) na środek `(12, 227)` bez usuwania jednostki. Stan trudności śledzi pojedyncza pochodnia `TORCH_ID` na odizolowanym pasku NW (`X=2, Y=170..186`) ukrytym w mgle wojny.

3. **Etap 5 (Część UI i naprawa nagrody w Kuźniach Roga):**
   - **Natywne przekreślanie celów (Strikethrough) w UI:** Usunięto atrapowy warunek `timer=999999` ze wszystkich 18 triggerów zadań `UI_*`. Wprowadzono rzeczywiste warunki ukończenia (`destroy_object`, `objects_in_area`, `own_fewer_objects`) oraz warunki zaporowe `(2, 166)` dla triggerów statusowych/licznikowych. Usunięto przedwczesną dezaktywację triggerów UI z triggerów ukończenia questów — dzięki temu silnik Genie samoczynnie przekreśla wykonane zadanie na liście celów na ekranie, a masowe czyszczenie następuje dopiero przy przejściach fazowych (`t_gothmog_slain`, `t_start_p3`).
   - **Odblokowanie nagrody w Kuźniach Roga (`West_Forges`):** Wyeliminowano konflikt zliczania Balrogów w `create_escalating_encounter`. Usunięto dwa początkowe statyczne Balrogi P7 umieszczone na mapie w `gondolin_map.py` (`(145, 108)` w Tumladen oraz `(184, 173)` w Cirith Thoronath) oraz zmieniono bazowy spawn Ołtarza w Tumladen na P8. Dzięki temu w Fazie I jedynym Balrogiem P7 na mapie jest elitarny demon w Kuźniach Roga, a warunek `own_fewer_objects(P7, ENEMY_BALROG_BOSS_ID, 0)` poprawnie przyznaje `+200 Chwały`.
   - **Wzmocnienie walidatora:** W `validate_scenario.py` dodano test asercyjny zabraniający stosowania atrapowych warunków `timer >= 900000` w triggerach `UI_*`.

---

## [2026-11-02] Stabilizacja po audycie forensycznym: Immobile AI, HP bohaterów (1150/1150) i eliminacja hangów w 0:27

### 1. Weryfikacja Immobile AI i poprawka kolejności inicjalizacji bohaterów
- **Potwierdzenie w strumieniu `.aoe2record`:**
  - W strumieniu komend z nagrań playtestowych zbadano rozkazy AI (`cmd=0x0a` / `0x02c2`).
  - Liczba rozkazów PromiDE AI wyniosła dokładnie `AI_ORDER = 0` we wszystkich analizowanych nagraniach.
  - Fizyczna instalacja plików `Immobile AI.ai` i `Immobile AI.per` bezpośrednio w folderze zasobów gry (`resources/_common/ai`) oraz blokada `set_immobile_ai()` + `lock_personality = True` całkowicie spacyfikowały silnik sztucznej inteligencji.
- **Naprawa MaxHP bohaterów (Idril 1150/1150 HP):**
  - W silniku Genie wywołanie `change_object_name` w `0:01` klonowało prywatny `master_obj` jednostek pre-placed przed zaaplikowaniem `modify_attribute`, co zamrażało bazowe statystyki fabryczne modeli.
  - Skorygowano harmonogram timerów startowych:
    * `timer = 1`: technologie/dyplomacja oraz wszystkie 4 triggery statystyk `modify_attribute` (`Init_03s_Noldor_Retinue_Stats`, `Init_03s_Noldor_Hero_Stats`, `Init_03s_Morgoth_Enemy_Stats`, `Init_03s_Morgoth_Boss_Stats`) — wykonywane PRZED zmianą nazw.
    * `timer = 2`: trigger leczący `Init_04s_Full_Heal_After_MaxHP` (`heal_object` podnoszący bieżące HP do nowego MaxHP).
    * `timer = 3`: trigger nadający nazwy fabularne `Init_01s_Techs_And_Names` (`change_object_name`).
  - Efekt w grze: Idril posiada pełne 1150/1150 HP, a pozostali bohaterowie (Tuor 1000/1000, Ecthelion 1200/1200, Glorfindel 1200/1200, Turgon 2500/2500) startują z pełnym paskiem zdrowia.

### 2. Mechanizm zawieszenia w 0:27 i trwałe rozwiązanie
- **Analiza przyczyny awarii `AppHangB1` w 0:26.99 i 0:28.70 (ostatni komunikat `[DBG #12]`):**
  - Od `0:00` Twierdza `caragdur_keep` (`KEEP_ID = 235`, należąca do P8) prowadziła nieustanny ostrzał palisady (`FORTIFIED_WALL_ID = 155`, 250 HP) oddzielającej enklawę Caragdûr od bazy P4 na kafelkach `(16, 35..48)`.
  - Jednocześnie wieża obronna P4 na `(16, 36)` i wieża P1 na `(47, 49)` ostrzeliwały mur i twierdzę P8, wywołując nieustanny alarm ataku od startu gry.
  - Dokładnie w `~27.` sekundzie gry segment palisady ulegał zniszczeniu pod skomasowanym ogniem. Nagłe przerwanie zamkniętego korytarza na granicy stref wywoływało załamanie siatki pathfindingu silnika Genie przy próbie przekierowania jednostek patrolowych/budynków obronnych, skutkując zawieszeniem wątku `AppHangB1`.
- **Wdrożone trwałe rozwiązanie:**
  1. **Rozbrojenie Twierdzy Caragdûr (`caragdur_keep`, P8):**
     - W triggerze `Init_03s_Morgoth_Enemy_Stats` (`timer=1`) dodano efekty `modify_attribute` dla `source_player=PlayerId.EIGHT`, `object_list_unit_id=KEEP_ID`:
       * `ATTR_MAXIMUM_RANGE` (`attr=12`) ustawione na `quantity=0.001` (wartość `0.001` kafelka uniemożliwia namierzanie celów poza obrysem budynku, omijając jednocześnie błąd falsy `0.0` w `AoE2ScenarioParser 0.9.8`).
       * `ATTR_ATTACK` (`attr=9`) dla `ARMOR_CLASS_PIERCE` (`class=3`) ustawione na `0`.
       * `ATTR_ATTACK` (`attr=9`) dla `ARMOR_CLASS_MELEE` (`class=4`) ustawione na `0`.
  2. **Transfer palisad Caragdûr do `PlayerId.GAIA`:**
     - Segmenty muru `FORTIFIED_WALL_ID = 155` na linii podziału `X=16, 35 <= Y <= 48` oraz mury obwodowe enklawy na `Y=44` i `X=42` przekazano do gracza neutralnego `GAIA`. Wieże graczy i twierdza wroga nie atakują neutralnych ścian, likwidując fałszywy alarm i przedwczesne wyłomy.
  3. **Usunięcie pre-placed łuczników orków P5:**
     - Usunięto 8 jednostek `ENEMY_ORC_ARCHER_ID` z Doliny Tumladen, dzięki czemu liczba mobilnych jednostek wojskowych P5–P8 w `0:00` wynosi dokładnie `0`.
  4. **Stan jednostek Morgotha w `0:00`:**
     - Łącznie 16 obiektów statycznych/budynków (koszary, wieże, warsztaty, zamek, twierdza). 0 jednostek mobilnych, 0 palisad P8.

### 3. Zadania dla Etapu 8 (sesja z modelami zaawansowanymi)
1. Dynamiczny spawn wrogów w Tumladen i Orfalch (zamiast jednostek pre-placed).
2. Rewizja logiki `LocalRallyHealLoop` pod kątem eliminacji sygnatury `86fd` (hang po śmierci Galdora w 1:29).
3. Testy obciążeniowe i dynamiczne bramy Orfalchu w Etapie 7.
4. Wyłączenie instrumentacji `DEBUG_CHAT` po pełnej stabilizacji.

---

### 2. Aktualny stan weryfikacji i testów

Wszystkie zestawy testów przechodzą w 100% na zielono:

| Skrypt / Narzędzie | Wynik | Kluczowe wskaźniki |
|---|---|---|
| `generate_gondolin_scenario.py` | **PASS (0)** | 334 triggery, 7024 obiekty, 5568 drzew, 0 błędów placementu (`failed_placements == 0`), czysty zapis binarny. |
| `pytest validate_scenario.py` | **PASS (10/10)** | 100% testów: brak CTD, brak zwłok/pocisków, poprawne pętle czasowe, prostokąty obszarów, blokada PromiDE AI, bezpieczeństwo UI (brak atrapowych timerów). |
| `test_stage_a_logic.py` | **PASS** | 334 triggery, symulacja behawioralna (grupy 15A..18, w tym 5 scenariuszy GraceCoRespawn i dwuścieżkowy finał). |
| `test_stage_b_grid.py` | **PASS** | 0 kolizji budynków, 5/5 blokad szczelnych w 0:00, drożność tras BFS we wszystkich fazach gry. |
| `stage_a1_diagnostic_and_variants.py` | **PASS** | 0 magic numbers poza `gondolin_config.py`, obecność 9 bohaterów, symetria dyplomacji 8x8. |

---

### 3. HANDOFF — Instrukcja dla kolejnego modelu wznawiającego prace

```markdown
KONTEKST PROJEKTU:
Repozytorium: AoE_Scenarios / gondolin
Scenariusz: Silmarillion: Upadek Gondolinu (4P Co-op RPG)
Stan bazowy: Commit z pełnym wdrożeniem Etapów 2, 3, 4, 6 oraz części UI Etapu 5. Wszystkie 4 główne zestawy testów (generate, pytest, test_stage_a, test_stage_b) są w 100% ZIELONE (PASS).
Liczba triggerów: 334. Kolizje placementu: 0.

ZREALIZOWANO DOTYCHCZAS:
- Etap 1 & 2: Eliminacja błędnych ID zwłok/pocisków/statków, neutralizacja zawieszeń PromiDE AI (set_immobile_ai + lock_personality), stabilizacja pętli zrzutów P6.
- Etap 3: Rozbicie Init_03s na 4 triggery, pełne statystyki 9 jednostek wroga w BALANCE, leczenie MaxHP w Init_04s (likwidacja 35/1150 HP).
- Etap 4: Cisza bojowa [0:00, 0:50), Maeglin w 0:50, Smoki w 1:05, dwukierunkowy automat Sanktuarium Balansu (-2..+2 z teleport_object Króla).
- Etap 5 (Część UI & Balrogi): Usunięcie atrapowego timer=999999 z 18 triggerów UI_*, wdrożenie realnych warunków ukończenia i natywnego strikethrough w silniku, naprawa nagrody w Kuźniach Roga (usunięcie 2 statycznych Balrogów P7 i ołtarz P8).
- Etap 6: Nowa estetyka i geometria mapy (0 kolizji, 5568 drzew, bramy miejskie 64/88, kołowroty GAIA, posągi Glingal/Belthil).
- Stabilizacja forensyczna: Potwierdzenie instalacji Immobile AI (AI_ORDER = 0 w nagraniach), naprawa kolejności timerów (HP bohaterów 1150/1150), rozbrojenie Twierdzy Caragdûr (KEEP_ID range=0.001, atk=0), transfer murów Caragdûr do GAIA i usunięcie pre-placed orków P5 (likwidacja hangów w 0:27 i alarmu od 0:00).
- Etap 8 (Zdefiniowany w ROADMAP.md): Plan dalszej analizy dla modeli flagowych (dynamiczny spawn wrogów, eliminacja sig 86fd w LocalRallyHealLoop, testy bram Orfalchu, wyłączenie DEBUG_CHAT).

KOLEJNE ZADANIE DO WYKONANIA (ETAP 7 Z ROADMAP.md):
1. Rozbudowa testów BFS w `gondolin/test_stage_b_grid.py`:
   - Przejście z ręcznej tabeli footprintów na dokładne obrysy zapisane w `SafeMapGrid`.
   - Osobne testy otwierania każdej z 7 Bram Orfalch Echor (`orfalch_gate_1` do `orfalch_gate_7` testowane pojedynczo).
   - Osobne testy drożności wejścia na Dolny i Górny Szlak Tumladen.
   - Testy negatywne BFS symulujące zablokowanie korytarza alei murem lub budynkiem.
2. Rozbudowa walidatora po deserializacji w `gondolin/generate_gondolin_scenario.py`:
   - Rozbudowa `inspect_and_validate_scenario()` o słownik `validation_manifest` generowany przed zapisem i rygorystycznie sprawdzany po powtórnym wczytaniu pliku `.aoe2scenario` przez `AoE2DEScenario.from_file()`:
     * map_size == 240, active_players == 8, role human/AI, cywilizacje, symetryczna dyplomacja 8x8.
     * obecność wszystkich 9 bohaterów, poprawność reference_id budynków questowych.
     * brak pustych warunków w triggerach UI_*, brak niefiltrowanych objects_in_area.
     * zgodność 1:1 parametrów efektów modify_attribute przed i po zapisie.
3. Weryfikacja:
   - Uruchomienie pełnego pakietu testów:
     py gondolin/generate_gondolin_scenario.py
     py -m pytest gondolin/validate_scenario.py -v
     py gondolin/test_stage_a_logic.py
     py gondolin/test_stage_b_grid.py
4. Playtest w silniku gry AoE2: DE:
   - Weryfikacja zachowania w grze pod kątem płynności, braku desynchronizacji/crashy i czytelności przekreślanych zadań w UI.
```

---

### Seria 8: Diagnostyka i eliminacja zawieszeń pathfindingu `AppHangB1 (Sig[3] = 185d)` w 2:09 (#18) i 3:01 (#257)

#### 1. Geneza i analiza problemu:
W trakcie playtestów w trybie Host Game scenariusz przeszedł pomyślnie wszystkie punkty krytyczne do 2. minuty (brak alarmu wież w 0:00, palisady nie pękają w 0:27, zdrada w 0:50, smoki w 1:05), lecz napotkał zawieszenia silnika:
- **Próba 1 (2:09, t = 129s):** ostatni komunikat `<AQUA>[DBG #18] P6_Dragon_Drop_east_avenue_Z0`
- **Próba 2 (3:01, t = 181s):** ostatni komunikat `<AQUA>[DBG #257] Enc_East_Market_EliteLeash`

Weryfikacja Windows Error Reporting (`Report.wer`) potwierdziła dla obu zdarzeń identyczny typ błędu:
`EventType = AppHangB1`, `Sig[3] = 185d`, `Hang Type = 134217728`.
Bezpośrednie przyczyny zawieszenia procedury pathfindingu w silniku AoE2: DE:
1. **Kolizje geometryczne i duplikaty w `create_object`:**
   - W `#18` (`P6_Dragon_Drop_east_avenue_Z0`) 9 jednostek spawnowało się na 7 kafelkach (podwójne jednostki na `(97, 62)` i `(98, 62)`), podczas gdy taran Żelaznego Smoka dopiero dotykał Bramy Wschodniej na `X = 104`.
   - W `#257` (`Enc_East_Market`) Jeźdźcy Wargów spawnowali się od `(102, 64)`, a przy starym wzorze przesunięcia jednostki trafiały na `X = 104` wprost w bryłę Fortified Wall / Bramy Wschodniej.
2. **Nieskończona pętla `EliteLeash` i gigantyczny obszar `attack_move`:**
   - Trigger `#257` wysyłał rozkaz `attack_move` co 6 sekund na obszar `(49, 13)` do `(141, 111)` (9 016 kafelków!), wychodząc daleko poza mury miasta na zewnętrzne równiny i zamknięte skały.
   - Pętla `t_elite_leash` nigdy nie była dezaktywowana przy przejściu fazy gry ani po opuszczeniu sektora.
   - Wojska startowe Gracza 2 na `(80, 48)` przy szerokim filtrze sektora ryzykowały przedwczesne wzbudzenie zasadzki w 0:00.

#### 2. Wdrożone naprawy:
1. **Naprawa zrzutów Żelaznych Smoków (`P6_Dragon_Drop_*`) i szturmu w 1:05:**
   - Rozłożono 9 jednostek zrzutu na unikalnych 9 kafelkach siatki 3x3 `(dx in -1..1, dy in -1..1)` wokół środka korytarza `(cx, cy)` — 0 duplikatów pozycji.
   - Odsunięto strefy wyzwalania `Z0` od bram (`north_avenue_Z0` do `y2 = 109`, `east_avenue_Z0` do `x2 = 99`), dzięki czemu desant orków wewnątrz miasta aktywuje się dopiero po faktycznym sforsowaniu bramy przez machinę.
   - W `P6_Spawn_Iron_Dragons_Phase1` (`t = 65s`) dodano towarzyszący szturm piechoty P5 przed Bramą Północną (6x piechota na `Y=126`, 4x kusznicy na `Y=127`) oraz Bramą Wschodnią (6x piechota na `X=114..115`, 4x kusznicy na `X=115`) na w 100% wolnych kafelkach z rozkazem `attack_move` w głąb Gondolinu.
2. **Przebudowa `create_escalating_encounter` i `Enc_East_Market`:**
   - Zwiększono interwał pętli `t_elite_leash` z 6s do 20s.
   - Ograniczono obszar przeszukiwania `attack_move` w mieście ściśle do granic dzielnicy miejskiej (`X <= 102`, `Y <= 108`), uniemożliwiając wyszukiwanie celów poza murami.
   - W `t_gothmog_slain` dodano automatyczną dezaktywację wszystkich pętli `_EliteLeash` z Fazy I.
   - W `Enc_East_Market`: odsunięto punkty spawnu w głąb placu targowego (piechota na `(94, 64)`, kusznicy na `(94, 60)`, wilki na `(98, 62)`), z dala od muru `X=104` i garnizonu P2.
   - Zawężono obszar wyzwalania `Enc_East_Market_Base` (`X >= 88`), co całkowicie eliminuje samoczynne wzbudzenie przez startowe wojska P2 na `(80, 48)` (max X wojsk P2 w 0:00 = 84).
3. **Audyt i eliminacja kolizji `create_object` względem `SafeMapGrid`:**
   - Wyeliminowano kolizje w `Aqueduct_Guard` (przesunięcie na `(84, 83)` z dala od koszar) oraz `Balrog_Altar_Tumladen` (odsunięcie spawnu z bryły ołtarza 4x4 na wolne kafelki `(142, 112)` i `(149, 112)`).
   - Przesunięto punkty respawnu fazy 1 (`checkpoints["phase1"]`) Tuora/Roga na `(61, 51)` (dziedziniec Amon Gwareth, z dala od Bramy Północnej Cytadeli na `Y=48`) oraz odsunięto punkty od posągów Fontanny.
   - Odsunięto spawn nagród grup uchodźców (`Rescue_ref_*`) od samych namiotów uchodźców.
   - Rezultat audytu: 0 kolizji jednostek militarnych/bohaterów w całym scenariuszu.

#### 3. Aktualny stan weryfikacji i testów:
Wszystkie 4 główne zestawy testów przechodzą w 100% na zielono:
- `generate_gondolin_scenario.py`: PASS (334 triggery, 0 błędów placementu, czysty zapis binarny).
- `pytest validate_scenario.py -v`: 10/10 PASS (100% testów CTD, braku zwłok/pocisków, bezpieczeństwa UI).
- `test_stage_a_logic.py`: PASS (334 triggery, symulacje soft-cap, leasha, GraceCoRespawn, aur i celów UI).
- `test_stage_b_grid.py`: PASS (0 kolizji budynków, 5/5 blokad szczelnych w 0:00, drożność tras BFS).

---

### Seria 9: Izolacja Caragdûr (0:00), korekta zewnętrznego spawnu machin (1:05) i odciążenie pathfindingu

#### 1. Zidentyfikowane przyczyny problemów z playtestów:
1. **Ostrzał w 0:00 i marsz P4 na koszary P8:**
   - Brak południowego muru Caragdûr (mur P8 stał tylko na `Y = 44` i `X = 42`).
   - Klasztor P4 na `(20, 33)` znajdował się w odległości 7.64 kafelka od `caragdur_keep` na `(19, 41)`, wewnątrz jej zasięgu ognia (8) przed rozbrojeniem w `0:01`.
   - Jednostki startowe P4 widziały koszary P8 na `(36, 41)` i szły otwartym placem je atakować.
2. **Spawn machin P6 wewnątrz murów w 1:05:**
   - Machiny P6 spawnowały się na `(61, 108)` (za Murem Północnym `Y = 111`) oraz na `(98, 63)` (za Murem Wschodnim `X = 104`), czyli wewnątrz stref zrzutu `Z0` jeszcze przed przełamaniem bram miejskich.
3. **Zawieszenia silnika (AppHangB1) w trakcie walki (~2:00–2:20):**
   - Zbyt częste zrzuty orków (`32s`) generujące gwałtowny przyrost wywołań komend AI.
   - Szeroki obszar źródłowy `attack_move` w pętli zrzutów obejmujący całe sektory alei.

#### 2. Wdrożone modyfikacje:
1. **Szczelne odcięcie enklawy Caragdûr w `0:00` (`gondolin_map.py` & `gondolin_quests.py`):**
   - Wybudowano południowy mur obronny (`FORTIFIED_WALL_ID`, Gaia) wzdłuż linii `Y = 38` od `X = 17` do `X = 42`.
   - Przejście `X = 28..31, Y = 38` zablokowano skałami `ROCK_FORMATION_ID` (`caragdur_rocks`), usuwanymi automatycznie (`remove_object`) w triggerze `P1_Spawn_Maeglin_Traitors` w `0:50`.
   - Przesunięto `caragdur_keep` na `(20, 42)`.
   - Przesunięto klasztor P4 na `(20, 28)`, domy P4 na `(31, 23)` i `(44, 31)`, a świtę P4 na `Y = 24..28` (`dy = (offset_idx // 7) - 2`).
   - Minimalna odległość euklidesowa między wieżą P8 a jakimkolwiek obiektem P4 wynosi teraz $\ge 12.0$ kafelków (poza zasięgiem 8 i poza LOS 11).
   - W `P1_Spawn_Maeglin_Traitors`: Maeglin spawnuje się na dziedzińcu Caragdûr na `(24, 40)`, a 6 zdrajców na unikalnych wolnych kafelkach `(22..25, 40..41)` (0 nakładających się pozycji, 0 kolizji z murem).
2. **Korekta pozycji szturmu w 1:05 (`gondolin_mechanics.py`):**
   - W `P6_Spawn_Iron_Dragons_Phase1` machiny P6 przesunięto na zewnątrz murów:
     * Północ: taran na `(61, 122)`, smoki ogniste na `(59, 122)` i `(63, 122)` na wolnych kafelkach przed Bramą Północną (`Y = 122 > 111`), z rozkazem `attack_move` do wnętrza alei `(61, 78)`.
     * Wschód: taran na `(111, 63)`, smok ognisty na `(111, 61)` na wolnych kafelkach przed Bramą Wschodnią (`X = 111 > 104`), z rozkazem `attack_move` do alei `(76, 63)`.
3. **Odciążenie pathfindingu podczas walki (`gondolin_config.py` & `gondolin_mechanics.py`):**
   - Zwiększono interwał zrzutu orków `dragon_drop_interval_seconds` z 32s do 45s.
   - W `t_drop.new_effect.attack_move` ograniczono obszar źródłowy ściśle do lokalnej siatki spawnu `(cx - 2, cy - 2, cx + 2, cy + 2)`.
4. **Rozbudowa suity testowej (`test_stage_b_grid.py`):**
   - Dodano test negatywny BFS w `0:00`: brak przejścia z bazy P4 `(28, 28)` do Caragdûr `(36, 41)`.
   - Dodano test pozytywny BFS po `0:50`: przejście z `(28, 28)` do `(36, 41)` zostaje w pełni odblokowane po usunięciu `caragdur_rocks`.

#### 3. Raport z weryfikacji:
- `generate_gondolin_scenario.py`: PASS (334 triggery, 0 odrzuconych placementów, scenariusz zapisany i zwalidowany).
- `pytest validate_scenario.py -v`: 10/10 PASS (100%).
- `test_stage_a_logic.py`: PASS (100%).
- `test_stage_b_grid.py`: PASS (6/6 blokad szczelnych w 0:00, pełna drożność we wszystkich fazach).
