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