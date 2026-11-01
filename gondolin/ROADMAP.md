# ROADMAP.md — Plan Naprawy, Przebudowy i Walidacji Scenariusza *Silmarillion: Upadek Gondolinu (4P Co-op RPG)*

Dokument definiuje kompletny, wieloetapowy plan inżynieryjny naprawy stabilności, korekty geometrii i estetyki mapy oraz przebudowy mechanik i triggerów scenariusza `Silmarillion_Upadek_Gondolinu_Coop.aoe2scenario` względem commita bazowego `9b240dc6731e0690376db62e5c3c2fde6e983b58`.

---

## 1. Plan naprawy stabilności (Diagnostyka i eliminacja zawieszania się gry)

### 1.1. Klasyfikacja zaobserwowanych awarii w silniku *AoE2: DE*

W dotychczasowych 17 uruchomieniach testowych wariantów `A2` zaobserwowano dwa odrębne typy awarii, które wymagają rozdzielnej diagnostyki:

1. **Crashe podczas ładowania/inicjalizacji scenariusza (z oknem raportu błędu):** wystąpiły w 3 z 17 prób (`A2_4` próba 2, `A2_12` próba 1, `A2_5` próba 2).
2. **Crashe i zawieszenia w trakcie trwania rozgrywki (czas gry `t_game`):** wystąpiły w 11 z 17 prób i grupują się w trzech charakterystycznych oknach zegara gry:
* **Okno wczesne (`0:07 – 0:12`):** `A2_1` (`0:07`), `A2_2` (`0:10`), pierwszy test bazowy (`0:12`) — awarie następują przed wykonaniem spawnu P6 z `0:15` oraz przed lub na granicy spawnu Maeglina z `0:10`.


* **Okno po pierwszym zrzucie P6 (`0:34 – 0:44`):** `A2_0_Baseline` (`0:34`), `A2_3` (`0:44`) — awarie następują bezpośrednio po osiągnięciu progu `timer = 32` przez cykliczne triggery `P6_Dragon_Drop_*`.


* **Okno późne (`1:30 – 1:34` oraz `2:37 – 2:47`):** `A2_3` (`1:30`), `A2_12` (`1:34`), `A2_1` (`2:37`), `A2_5` (`2:37`), `A2_4` (`2:42`), `A2_2` (`2:46`), `A2_0_Baseline` (`2:47`) — aż 5 awarii skupionych w wąskim przedziale 10 sekund wokół `2:40` (`160 s = 5 × 32 s`).



### 1.2. Hipotezy badawcze podlegające weryfikacji

Ponieważ wariant bazowy i pojedyncze podmiany `532` lub `682` zachowują się niedeterministycznie (potrafią przetrwać 3 minuty w jednej próbie i zawiesić się w kolejnej), żadnej przyczyny nie uznaje się za udowodnioną przed wykonaniem izolowanych testów `A2-bis`:

* **Hipoteza H1 (Kumulacja obiektów przez `looping = True` + `timer = 32` w `P6_Dragon_Drop_*`) — [ZWERYFIKOWANA NEGATYWNIE 2026-11-01]:**
* W kodzie `gondolin_mechanics.py` pięć triggerów `P6_Dragon_Drop_*` posiada ustawione jednocześnie `looping = True`, warunek `timer = 32` oraz warunek `objects_in_area` badający obecność tarana P6 (`548`).


* Początkowy taran P6 stoi od `0:00` na współrzędnych `(102, 63)` wewnątrz strefy `east_avenue_Z0 (92, 57, 104, 69)`, przez co warunek obecności tarana w tej strefie był spełniony od pierwszej sekundy gry, nawet przy wyłączonym spawnie P6 z `0:15`.


* **Wynik sondy `Gondolin_A2B_T1_LoopTimerProbe5s` (`2026-11-01`):** Silnik Genie poprawnie resetuje licznik `Timer` w trybie `looping = True` (efekt wykonuje się co `N` sekund, a nie co 1 sekundę). Hipoteza awarii przez sam mechanizm `looping + timer` została **odrzucona**; zrzuty w `0:32` powodowały natomiast cykliczne tworzenie obiektów zwłok `1124` i wydawanie im rozkazu `attack_move` (patrz H2). Mimo to w Kroku S4 dodano uzbrojenie zrzutów dopiero od `0:15`, globalny limit populacji P5 (`65`) oraz lokalny limit zatłoczenia strefy (`10`).


* **Hipoteza H2 (Operacje na identyfikatorach zwłok i pocisków w `0:00` i `0:03`):**
* Audyt wykazał, że 4 stałe jednostek w `gondolin_config.py` wskazują na obiekty zwłok (`dead_unit`): `UNIT_WING_GUARD_ID = 693` (*Berserk Dead* — potwierdzona przyczyna 12 ciał u P1 na starcie), `ENEMY_ORC_INFANTRY_ID = 1124` (*Karambit Dead*), `UNIT_ARCH_RATTAN_ID = 1130` (*Rattan Archer Dead*), `ENEMY_WARG_RIDER_ID = 756` (*Tarkhan Dead*), a 1 stała wskazuje na pocisk: `UNIT_SWALLOW_SNIPER_ID = 469` (*Trebuchet Fire*).


* Stawianie tych obiektów na mapie w `0:00`, wykonywanie na nich kilkudziesięciu operacji `modify_attribute` (pancerz, atak, regeneracja) w `Init_03s_RPG_Unit_And_Hero_Stats` (`0:03`) oraz wydawanie im rozkazów `attack_move` w `P6_Dragon_Drop_*` (`0:32`) może prowadzić do uszkodzenia struktur pamięci jednostek w silniku.




* **Hipoteza H3 (Jednostki morskie na lądzie i mutacja spakowanego trebusza):**
* `ENEMY_MOLE_PIKE_ID = 532` (*Fast Fire Ship*) jest umieszczany na suchym lądzie w `0:00` (`83..86, 70`) oraz spawnowany z rozkazem ruchu po górach w `0:10` (`P1_Spawn_Maeglin_Traitors`), natomiast `HERO_EGALMOTH_ID = 682` (*Bad Neighbor*) to spakowany trebuszet otrzymujący w `0:03` prędkość ruchu `1.20`.




* **Hipoteza H4 (Przeciążenie pojedynczego triggera `Init_03s_RPG_Unit_And_Hero_Stats`):**
* Trigger uruchamiany w `0:03` wykonuje w jednej klatce 480 efektów `modify_attribute`, w tym operacje na nieprawidłowych ID oraz klasach ataku/pancerza.





### 1.3. Zaplanowane kroki diagnostyczne i naprawcze stabilności

1. **Krok S1 — Empiryczny pomiar semantyki `Looping + Timer` (`a2_t1_loop_timer_probe`) — [WYKONANO]:**
* Uruchomienie odizolowanego, minimalnego scenariusza `Gondolin_A2B_T1_LoopTimerProbe5s.aoe2scenario` (zawierającego wyłącznie 1 trigger z `looping = True` i `timer = 5`, dodający `+1` Złota P1 i `+1` żywego Czempiona `567` na pustej mapie trawiastej bez AI i bez błędnych ID).


* Pomiar w `0:00 – 0:15` potwierdził wykonywanie efektu co 5 sekund (`0:05`, `0:10`, `0:15`) — licznik `Timer` resetuje się automatycznie.




2. **Krok S2 — Izolacja wpływu zrzutów P6 (`a2_b3a`, `a2_b3b`, `a2_b3c`):**
* Rezerwowy krok izolacyjny na wypadek utrzymywania się CTD w grze po wdrożeniu Kroku S4.




3. **Krok S3 — Pojedyncza izolacja każdego błędnego ID (`a2_b1a` .. `a2_b1g`) oraz triggera `Init_03s` (`a2_b2`):**
* Rezerwowy krok izolacyjny (`Gondolin_A2B_1a..1g` w `stage_a1_diagnostic_and_variants.py`), uruchamiany wyłącznie gdyby po łącznej naprawie w Kroku S4 utrzymał się jakikolwiek crash w grze.




4. **Krok S4 — Przebudowa pętli zrzutów P6, trwała wymiana błędnych ID i strażnik przed zapisem — [WDROŻONO W KODZIE]:**
* Wymieniono wszystkie 7 błędnych ID w `gondolin_config.py` (`693->694`, `1124->1125`, `1130->1131`, `756->757`, `469->868`, `532->892`, `682->200`), zaktualizowano `HERO_RANGED_IDS` (`{200, 172}`), naprawiono bezczasowy cykl `#317`/`#318` w `gondolin_quests.py`, przebudowano `P6_Dragon_Drop_*` (start wyłączony do `0:15`, limit `P5 <= 65`, anty-tłok strefy `< 10`, dezaktywacja w Fazie II) oraz dodano blokadę `assert_no_dead_or_projectile_ids_before_write` w `generate_gondolin_scenario.py` (`8/8 PASS` w `validate_scenario.py`).

5. **Krok S5 — Eliminacja zawieszeń wątku głównego `AppHangB1` (`PromiDE` `Sig[3]=185d`) oraz wtórnych błędów binarnych po analizie 3 testów z `DEBUG_CHAT` (`0:19`, `1:33`, `3:09`) — [WDROŻONO W KODZIE]:**
* Analiza raportów Windows WER (`AppHangB1`, `Sig[3]=185d`, `BucketId=e77d218807b758d7b04fb0f739587106`) oraz strumieni binarnych `.aoe2record` z 3 prób (`19,979 ms`, `93,527 ms`, `190,046 ms`) udowodniła, że główną przyczyną zawieszeń nie były same triggery rytmiczne (`#3`, `#6`, `#147`, `#246`), lecz domyślny silnik `PromiDE` (`AiType.STANDARD`) aktywny na slotach AI (`P2–P8`) na mapie RPG bez TC/wieśniaków, z hermetycznie zamkniętymi sektorami `ROCK_CLIFF_ID` (`623`), który wpadał w nieskończoną pętlę pathfindingu/taktyki C++ (`ACT cmd=0x0a AI_ORDER 0x02c2 (-1, -1)` ×12 w jednej klatce).
* Zablokowano `PromiDE` na wszystkich graczach `P1–P8` poprzez `set_immobile_ai()` (`AiType.CUSTOM`) + `lock_personality = True` (z zachowaniem `human = True` na `P1–P4`), naprawiono mapowanie `Civilization` i wzmocniono dyplomację w `0:01` (`change_diplomacy`), wymieniono brakujący w datasetach obiekt `STATUE_ID = 817 -> 1279` (`OtherInfo.STATUE_CIVILIZATION`) oraz `FLAME_EFFECT_ID = 303 -> 304` (`OtherInfo.BONFIRE`), wyeliminowano obcięcie float->int=`0` przy `Operation.MULTIPLY` na `HIT_POINTS` (`#18`, `#19`, `#282` -> `Operation.SUBTRACT`), dodano `object_type=OBJECT_TYPE_MILITARY` do wszystkich obszarowych `damage_object`/`kill_object` oraz warunek `timer=999999` do wszystkich 18 banerów `UI_*` (`10/10 PASS` w `validate_scenario.py`).



---

## 2. Plan przebudowy mapy (Diagnoza wad obecnej wersji i zaplanowane zmiany algorytmiczne)

Analiza podglądu 2D (`gondolin_map_preview.png`), czterech zrzutów ekranu z gry (`121851.jpg`, `121929.jpg`, `122928.jpg`, `123014.jpg`) oraz kodu `gondolin_map.py` wykazała szereg błędów przestrzennych, funkcjonalnych i estetycznych.

### 2.1. Co w obecnej wersji mapy (`9b240dc6`) jest odwzorowane słabo lub błędnie

#### A. Układ urbanistyczny, proporcje i estetyka miasta Gondolin

1. **Zbyt rzadka zabudowa i puste trawniki wewnątrz murów (`121929.jpg`, `gondolin_map_preview.png`):**
* W skali mapy `240 × 240` pojedyncze budynki rozrzucone na wielkich zielonych połaciach `TerrainId.GRASS_2` sprawiają, że Gondolin wygląda jak rzadka osada lub obóz, a nie gęsto zabudowana, kamienna stolica Noldorów.




2. **Geometryczna sztuczność prostokątnych tarasów i pasów zniszczeń (`gondolin_map_preview.png`):**
* Tarasy miejskie (`paint_box(16, 16, 104, 114)`, `paint_box(28, 28, 92, 96)`, `paint_box(46, 48, 76, 78)`) oraz strefy wyłomów (`ROAD_BROKEN` na `52..70, 94..112` i `78..88, 102..112`) są wycięte ostrymi prostokątami `paint_box`, co w rzucie izometrycznym i na minimapie tworzy nienaturalne, kanciaste plamy.




3. **Klasztor w miejscu Fontanny Królewskiej i nienazwane drzewa na Amon Gwareth (`121851.jpg`):**
* Na pozycji `(61, 52)` stoi chrześcijański klasztor (`MONASTERY_ID = 104`) podpisany jako `"Fontanna Królewska Ectheliona"`, który zasłania widok na właściwy basen wodny `(61, 61)`.


* Obiekty `glingal_tree` (`OLIVE_TREE_ID = 1349` na `53, 61`) oraz `belthil_tree` (`CYPRESS_TREE_ID = 1347` na `69, 61`) są zwykłymi drzewami surowcowymi `GAIA` (`Tree (Olive)`), na których silnik Genie ignoruje efekt zmiany nazwy `change_object_name`.





#### B. Błędy murów, bram, dróg i kolizji przestrzennych

1. **Wchodzenie budynków zadaniowych w korytarze drogowe (`road_corridors`):**
* Funkcja `register_bldg()` wywołuje `place_unit_safe(..., respect_roads=False)`.


* W efekcie zamek `salgant_manor` (`CASTLE_ID = 82`, `4×4` na `91, 25`) tarasuje południowo-wschodnią aleję (`X = 87..93, Y = 23..29`), a budynek `aqueduct_control` (`UNIVERSITY_ID = 209`, `4×4` na `84, 74`) wchodzi w pas wewnętrznego bulwaru wschodniego (`X = 80..84`).




2. **Brak fizycznych modeli bram miejskich w murach Gondolinu (`121929.jpg`):**
* Choć w `gondolin_config.py` zdefiniowano `CITY_GATE_SW_NE_ID = 64` oraz `CITY_GATE_NW_SE_ID = 88`, w `gondolin_map.py` nie zostały one w ogóle umieszczone — zamiast bram w murach zieją puste 4-kafelkowe dziury (`X = 59..62`, `Y = 61..64`) flankowane przez donżony `KEEP_ID`.




3. **Zbyt bliska odległość startu P2 od Akweduktu i wież P4 od Twierdzy Maeglina (`121929.jpg`):**
* Start P2 na `(82, 58)` rozkłada 34 jednostki orszaku do `Y = 64`, czyli bezpośrednio na granicy strefy aktywacji `Aqueduct_Guard (74, 64)–(94, 84)`, uruchamiając walkę w `0:00`.


* Wieże strażnicze P4 na zachodnim murze `(16, 36)` i `(16, 48)` stoją 6 kafelków od `caragdur_keep (18, 42)` należącego do P8, przez co od pierwszej sekundy ostrzeliwują i niszczą twierdzę Maeglina oraz jego żołnierzy bez udziału graczy.




4. **Kolizje punktów spawnu triggerów z obrysami budynków:**
* W `Balrog_Altar_Tumladen` spawny bazowe `(145, 114)` i elitarne `(148, 114)` wypadają wewnątrz obrysu `4×4` budynku `balrog_altar` (`145, 112` $\rightarrow$ kafelki `X = 144..147, Y = 111..114`), a w `East_Market` spawny elitarne `(102, 64)` zahaczają o linię muru wschodniego `X = 104`.





#### C. Wady przedpola, Doliny Tumladen i wąwozu *Orfalch Echor*

1. **Puste, geometryczne pasy dróg na równinie Tumladen (`123014.jpg`, `gondolin_map_preview.png`):**
* Szlaki odwrotu przez Tumladen wyglądają jak proste, wykreślone od linijki pasy gołej ziemi (`DIRT_2`) na całkowicie pustej zielonej płaszczyźnie bez detali krajobrazowych, skał, ruin i obozowisk oblężniczych.


* Północno-zachodnia ćwiartka mapy (`X = 0..174, Y = 168..239`) to ogromny, pusty brązowy prostokąt `TerrainId.DIRT_3` na wysokości `elev = 6`, a prostokątne bloki lasu na Tumladen (`106..172, 134..154` oraz `106..174, 16..28`) mają sztuczne, proste krawędzie.




2. **Błędna własność wież i uzbrojony kołowrót w *Orfalch Echor* (`122928.jpg`):**
* Wszystkie 14 wież flankujących Siedem Bram należy do `PlayerId.ONE` (`P1`), przez co od `0:00` odsłaniają one cały wąwóz i ostrzeliwują stojące obok kołowroty `winch_bronze` (`P5` na `188, 114`), `winch_silver` (`P5` na `194, 144`) oraz `winch_steel` (`P7` na `180, 171`).


* Kołowroty Bram 3 i 5 (`OUTPOST_ID = 598`, `500 HP`) są niszczone przez wieże P1 w pierwszych kilkudziesięciu sekundach gry, a kołowrót Bramy 7 (`KEEP_ID = 235`) jest uzbrojoną wieżą strzelniczą, która od `0:00` prowadzi pojedynek ogniowy z wieżą P1 na `(184, 174)`.





---

### 2.2. Zaplanowane zmiany w algorytmie generowania mapy (`gondolin_map.py`)

1. **Ochrona korytarzy drogowych i korekta położenia landmarków (`respect_roads = True`):**
* Zmiana domyślnego parametru w `register_bldg()` na `respect_roads = True` (z jawną listą wyjątków wyłącznie dla bram miejskich i styków fortyfikacji).


* Przesunięcie `salgant_manor` z `(91, 25)` na `(95, 22)` (całkowicie poza korytarz drogi SE) oraz `aqueduct_control` z `(84, 74)` na `(90, 78)` (zajmuje kafelki `X = 89..92, Y = 77..80` poza bulwarem `X = 80..84`).


* Przesunięcie startu P2 z `(82, 58)` na `(80, 48)` (orszak zajmuje `X = 77..83, Y = 50..54`, co zapewnia 17 pustych rzędów kafelków bufora do obszaru `t_base` Akweduktu `Y = 72..82` oraz 9 pustych rzędów do obszaru `t_elite` `Y = 64..90`).




2. **Przebudowa Fontanny Królewskiej oraz Świętych Drzew *Glingal* i *Belthil* na Amon Gwareth:**
* Całkowite usunięcie budynku `MONASTERY_ID = 104` z pozycji `(61, 52)`.


* Przesunięcie pomocniczego `MAP_REVEALER_ID` z `(61, 61)` na `(61, 63)` i umieszczenie w samym sercu basenu wodnego `(61, 61)` centralnego monumentu `royal_fountain_bldg` (`STATUE_ID = 817`, właściciel `PlayerId.TWO`), który nosi nazwę `"Fontanna Królewska Ectheliona"`.


* Pozostawienie drzew `OLIVE_TREE_ID (1349)` na `(53, 61)` i `CYPRESS_TREE_ID (1347)` na `(69, 61)` jako warstwy wizualnej oraz zarejestrowanie stojących bezpośrednio obok nich postumentów (`STATUE_ID = 817`, właściciel `PlayerId.FOUR` na `53, 60` i `69, 60`) jako nazwanych obiektów `"Glingal (Złote Drzewo Gondolinu)"` i `"Belthil (Srebrne Drzewo Gondolinu)"`.




3. **Neutralizacja wież w *Orfalch Echor* i Caragdûr oraz nieuzbrojone kołowroty:**
* Zmiana właściciela wszystkich 14 wież flankujących Siedem Bram w *Orfalch Echor* z `PlayerId.ONE` na `PlayerId.GAIA` (wieże stanowią neutralną architekturę obronną wąwozu — nie ostrzeliwują kołowrotów P5/P7 i nie odsłaniają kanionu w `0:00`).


* Zmiana właściciela trzech wież na zachodnim murze Caragdûr (`(16, 26)`, `(16, 36)` oraz `(16, 48)`) z `PlayerId.FOUR` na `PlayerId.GAIA`, aby wyeliminować automatyczny ostrzał `caragdur_keep (18, 42)` przed `0:50`.


* Zastąpienie uzbrojonego `KEEP_ID` w `winch_steel` oraz `OUTPOST_ID` w `winch_bronze` i `winch_silver` nieuzbrojonym modelem mechanizmu zweryfikowanym w Edytorze Scenariuszy, z zachowaniem ich kluczy `reference_id` w słowniku `quest_buildings`.




4. **Przywrócenie fizycznych bram miejskich (`64` / `88`) i rozdzielenie obozów wyjściowych P5/P6:**
* Osadzenie fizycznych bram kamiennych (`CITY_GATE_SW_NE_ID = 64` oraz `CITY_GATE_NW_SE_ID = 88`) w 4-kafelkowych otworach murów Gondolinu po weryfikacji ich orientacji w Edytorze.


* Wycofanie początkowych jednostek szturmowych P5 i P6 w `0:00` poza zasięg widzenia i strzału wież miejskich na rozłączne pozycje obozowe za fosą północną i wschodnią:
* Budynki P5 na `(52, 126)` i `(70, 126)`, piechota P5 na `(54..57, 126..127)` ($\ge 16$ kafelków od wież P3 na `Y = 110`),
* Warsztaty P6 na `(61, 128)` i `(118, 63)`, machiny P6 na `(63..67, 126)` oraz `(114, 63)` (brak nakładania się z piechotą P5 i brak obecności tarana P6 wewnątrz `east_avenue_Z0` w `0:00`!).






5. **Zagęszczenie tkanki miejskiej Gondolinu, organiczne brzegi lasów i obozy oblężnicze na przedpolu:**
* Wprowadzenie w kwartałach 7 Domów zróżnicowanej nawierzchni (kamienne place i dziedzińce wewnętrzne przeplatane ogrodami `GRASS_2`), gęstszych pierzei kamienic (`HOUSE_ID`), pawilonów, kolumnad posągów i budynków cechowych przy zachowaniu otwartych głównych alei i ścisłego `respect_roads = True`.


* Zastąpienie prostokątnych krawędzi lasów na Tumladen i wyłomów `ROAD_BROKEN` kombinacją nakładających się okręgów `paint_circle` o zmiennym promieniu, co nada dolinie i skarpom naturalny, organiczny kontur.


* Uzupełnienie przedpola północnego/wschodniego oraz szlaków na Tumladen o obozowiska oblężnicze sił Morgotha (palisady, namioty dowódców, ogniska, głazy) przy zachowaniu otwartej przestrzeni do manewrowania i twardego limitu **`< 8 500` wszystkich obiektów** oraz **`3 000 .. 8 000` drzew** (liczonych łącznie dla `349, 350, 1347, 1349`).



---

## 3. Zaplanowane poprawki w mechanikach, falach, balansie i triggerach

### 3.1. Spokojne otwarcie scenariusza w przedziale `[0:00, 0:50)` i synchronizacja fal

* **Przedział `[0:00, 0:50)` — całkowita cisza bojowa:** brak jakichkolwiek walk, ostrzału wież i alarmów przez pierwsze 50 sekund gry, dający graczom czas na zapoznanie się z układem miasta, własnymi oddziałami i listą zadań.
* **`0:02` (`timer = 2`):** komunikat wprowadzający dla drużyny Noldorów.
* **`0:30` (`timer = 30`):** ostrzeżenie zwiadowców o zbliżającym się uderzeniu i zdradzie Maeglina (20 sekund do rozpoczęcia walki).
* **`0:50` (`timer = 50`):** `P1_Spawn_Maeglin_Traitors` — wybuch wewnętrznego buntu Maeglina (`P8`) w dzielnicy Caragdûr i atak na Dwór Tuora `(26, 28)`.


* **`1:05` (`timer = 65`):** `P6_Spawn_Iron_Dragons_Phase1` — główne uderzenie kolumn Orków (`P5`) i Żelaznych Smoków (`P6`) na wyłom północny i wschodni z jawnymi rozkazami `attack_move`.



### 3.2. Kontrolowany, czterowarunkowy spawn Gothmoga na Amon Gwareth

Zamiast natychmiastowego spawnu Gothmoga po samym zniszczeniu `caragdur_keep` i `aqueduct_control`:

1. Zniszczenie `caragdur_keep` oraz `aqueduct_control` uruchamia najpierw trigger ostrzegawczy `P1_Warning_Gothmog_Approaching` (komunikat fabularny + flara na Amon Gwareth + 40-sekundowy timer na przegrupowanie i uleczenie wojsk przy Fontannie Królewskiej).
2. Dopiero po spełnieniu koniunkcji: **(a)** ukończone zadanie Caragdûr, **(b)** ukończone zadanie Akweduktu, **(c)** upływ 40-sekundowego czasu przygotowania, **(d)** fizyczna obecność żywych bohaterów graczy (`HERO_TUOR_ID` oraz `HERO_ECTHELION_ID`) w sektorze `amon_gwareth (46, 48, 76, 78)`, uruchamia się `P1_Boss_Spawn_Gothmog_AmonGwareth` na `(61, 82)`.



### 3.3. Naprawa statystyk bohaterów, uzupełnienie aktualnego HP i balans jednostek wroga

1. **Statystyki bohaterów i aktualne HP w `0:03`:**
* Dopasowanie klasy modyfikowanego ataku (`ARMOR_CLASS_MELEE = 4` vs `ARMOR_CLASS_PIERCE = 3`) do rzeczywistego modelu każdego z 9 bohaterów (np. Glorfindel `640` *La Hire* $\rightarrow$ klasa `4`, Duilin `642` / Egalmoth `200` $\rightarrow$ klasa `3`).


* Dodanie bezpośredniego efektu uzupełniającego aktualne punkty życia (`heal_object` / `change_object_hp`) po podniesieniu maksymalnego HP w `0:03`, aby Tuor (`1350/1350 HP`), Rog (`1450/1450 HP`) i pozostali bohaterowie rozpoczynali grę z pełnym paskiem zdrowia.


2. **Uzupełnienie brakujących statystyk jednostek Morgotha (`P5–P8`):**
* Dodanie do `BALANCE` i `Init_03s_RPG_Unit_And_Hero_Stats` pięciu pominiętych dotąd jednostek wroga: `ENEMY_ORC_ARCHER_ID (4)`, `ENEMY_ORC_CROSSBOW_ID (24)`, `ENEMY_DIRE_WOLF_ID (89)`, `ENEMY_WARG_RIDER_ID (757)` oraz `ENEMY_HEAVY_SCORPION_ID (542)`.
* Dodanie modyfikacji pancerza (`ATTR_ARMOR` klasy `4` i `3`) dla jednostek liniowych P5 i P8 (`1125, 473, 878, 892`), aby nie ginęły błyskawicznie od kilku ciosów Noldorów.
* Przeprowadzenie kontrolowanego testu w grze na jednostce `ENEMY_ORC_BRUTE_ID (473)` tworzonej po `0:03` w celu potwierdzenia dziedziczenia statystyk z `0:03` przez późniejsze spawny (w razie braku dziedziczenia — wdrożenie wspólnego helpera aplikującego statystyki przy spawnie).



### 3.4. Naprawa panelu *Objectives* (`UI_*`), elitarnych zasadzek i symulatora

1. **Warunki na wszystkich triggerach `UI_*` (`display_on_screen = 1`):**
* Wszystkie triggery zadań w Fazach I, II i III (zarówno aktywne na starcie, jak i początkowo wyłączone) otrzymują rzeczywiste warunki ukończenia danego zadania, dzięki czemu w trakcie gry są wyświetlane bez przekreślenia i przekreślają się dokładnie w momencie wykonania misji.


* Triggery statusowe/licznikowe (`UI_Seals_Of_Turgon_3..0`, `UI_P1_Dilemma_Enclaves`, `UI_P2_Dilemma_Routes`) otrzymują warunek zaporowy powiązany ze znacznikiem stanu, uniemożliwiający ich samoczynne wykonanie w `0:00`.


2. **Lokalne śledzenie jednostek elitarnej zasadzki w `create_escalating_encounter`:**
* Zastąpienie globalnego warunku `own_fewer_objects(source_player=ai_p, object_list=unit_id, quantity=0)` rozwiązaniem wolnym od konfliktów z innymi jednostkami tego samego typu na mapie (wyeliminowanie blokowania nagrody `+200 Chwały` w `West_Forges` przez dwa początkowe Balrogi P7 stojące w Tumladen i przy Cirith Thoronath, z zachowaniem pełnej ochrony przed wyciąganiem żywej jednostki poza sektor walki).




3. **Naprawa `TriggerSimulator` w `test_stage_a_logic.py`:**
* Usunięcie błędnego warunku `or not trig.conditions: continue` (włączony trigger bez warunków musi wykonać się w kroku `0`, tak jak w silniku Genie).
* Korekta mapowania enum `Operation` w symulatorze (`SET = 1, ADD = 2, SUBTRACT = 3, MULTIPLY = 4`), co naprawia obsługę `award_glory_gold` i usuwa `AssertionError` dla `Aqueduct_Guard`.


4. **Uporządkowanie i weryfikacja `GraceCoRespawn`:**
* Zastosowanie fizycznego znacznika okna ochronnego i weryfikacja rzeczywistego zachowania na granicy cyklu zegara bezpośrednio w silniku *AoE2: DE* oraz zsynchronizowanie opisu w `gondolin_config.py` i `gondolin_campaign_guide.md` (w tym jasnej reguły, że 6 strażników otrzymuje wyłącznie pierwszy poległy bohater, który zużył Pieczęć).



---

## 4. Podział prac na etapy (Etapy 1–7) wraz z modyfikowanymi plikami i kryteriami weryfikacji

Każdy etap podlega trójpoziomowej weryfikacji:

* **Poziom 1:** Testy symulatora i siatki geometrycznej w Pythonie (`test_stage_a_logic.py`, `test_stage_b_grid.py`).
* **Poziom 2:** Zapis i ponowny odczyt pliku binarnego `.aoe2scenario` przez `AoE2DEScenario.from_file()` z kontrolą manifestu.


* **Poziom 3:** Rzeczywisty test w Edytorze Scenariuszy i podczas rozgrywki w *Age of Empires II: Definitive Edition*.

---

### Etap 1 (A2-bis): Przeprowadzenie testów izolacyjnych crasha i potwierdzenie modeli w Edytorze

* **Modyfikowane pliki `.py`:** Brak zmian w 5 modułach rdzenia (wykorzystywany jest wyłącznie gotowy skrypt `stage_a1_diagnostic_and_variants.py` budujący warianty w pamięci RAM).


* **Zakres działań:**
1. Wygenerowanie i uruchomienie w grze minimalnej sondy `Gondolin_A2B_T1_LoopTimerProbe5s.aoe2scenario` (`0:00 – 0:15`) w celu ustalenia częstotliwości wykonywania `looping = True` + `timer = 5`.


2. Uruchomienie odizolowanych wariantów `A2B_1a` (`693 -> 694`), `A2B_3a/3b` (wyłączenie zrzutów P6), `A2B_2` (wyłączenie `Init_03s`) oraz pozostałych wariantów pojedynczych ID (`1124 -> 1125`, `469 -> 868`, `532 -> 892`, `682 -> 200`).


3. Sprawdzenie w Edytorze Scenariuszy docelowych modeli i klas ataku dla bohaterów (`Rog 432/1669/648`, `Egalmoth 200`, `Duilin 642`, `Glorfindel 640`, `Maeglin 176`, `Idril 1292/1066`, `Galdor 636`, `Ecthelion 168`) oraz nieuzbrojonego modelu kołowrotów i orientacji bram miejskich (`64` vs `88`).


4. Odczytanie w grze statystyk Ciężkiego Uruka (`473`) zespawnowanego po `0:32` (czy posiada `185 HP / 22 ATK`, czy bazowe `60 HP / 12 ATK`).


* **Kryterium powodzenia Etapu 1:** Jednoznaczne zidentyfikowanie czynników wywołujących crashe, potwierdzenie zniknięcia 12 ciał P1 po zamianie `693 -> 694` oraz zamknięcie ostatecznej tabeli ID wszystkich bohaterów i jednostek.



---

### Etap 2: Wdrożenie docelowych ID jednostek/bohaterów, naprawa `P6_Dragon_Drop_*` i stabilizacja silnika

* **Modyfikowane pliki `.py`:** `gondolin_config.py`, `gondolin_mechanics.py`, `test_stage_a_logic.py` (oraz usunięcie ewentualnego duplikatu `/gondolin_map.py` z katalogu nadrzędnego repozytorium).
* **Zakres działań:**
1. Trwała wymiana wszystkich błędnych ID zwłok (`693 -> 694`, `1124 -> 1125`, `1130 -> 1131`, `756 -> docelowe ID`), pocisku (`469 -> 868`), statku (`532 -> 892/358`) oraz potwierdzonych ID bohaterów (`Egalmoth`, `Glorfindel`, `Duilin`, `Rog`, `Maeglin`, `Salgant`) we wszystkich kolekcjach w `gondolin_config.py` i `HERO_RANGED_IDS` w `gondolin_mechanics.py`.


2. Przebudowa triggerów `P6_Dragon_Drop_*` w `gondolin_mechanics.py` zgodnie z wynikiem sondy z Etapu 1, tak aby zrzuty wykonywały się w kontrolowanych odstępach czasowych i nie kumulowały nieskończonej liczby jednostek.


* **Sposób weryfikacji:**
* *Poziom 1 i 2:* Skaner AST i enumów w `stage_a1_diagnostic_and_variants.py` potwierdza `0` obiektów zwłok, `0` pocisków i `0` statków wśród jednostek bojowych oraz obecność wszystkich 9 bohaterów w zdeserializowanym pliku.


* *Poziom 3 (W grze):* **3 kolejne uruchomienia pełnego scenariusza trwające minimum 3–5 minut bez ani jednego crasha**, brak 12 ciał u P1 na starcie, prawidłowe modele 3D wszystkich 9 bohaterów i oddziałów.



---

### Etap 3: Statystyki bohaterów w `0:03`, uzupełnienie aktualnego HP i balans jednostek Morgotha

* **Modyfikowane pliki `.py`:** `gondolin_config.py`, `gondolin_mechanics.py`, `test_stage_a_logic.py`.
* **Zakres działań:**
1. Podział `Init_03s_RPG_Unit_And_Hero_Stats` na czytelne triggery per gracz/kategoria, korekta kodowania `modify_attribute` dla ataku i pancerza oraz dodanie uzupełnienia aktualnego HP bohaterów (`heal_object` / `change_object_hp`) po zwiększeniu ich maksymalnego HP.
2. Dodanie do `BALANCE` i triggerów `0:03` modyfikacji HP, ataku (klasa `3` lub `4`) i pancerza (`3` i `4`) dla wszystkich jednostek wroga (`1125, 473, 4, 24, 89, 757, 542, 878, 892`) oraz wdrożenie ewentualnego wsparcia po spawnie (zależnie od wyniku testu jednostki `473` z Etapu 1).


* **Sposób weryfikacji:**
* *Poziom 1 i 2:* Sprawdzenie zgodności liczby i parametrów efektów `modify_attribute` przed zapisem i po ponownym odczycie pliku `.aoe2scenario`.
* *Poziom 3 (W grze):* Po `0:04` wszyscy 9 bohaterowie mają pełny pasek zdrowia (`1350/1350` u Tuora, `1450/1450` u Roga itd.) i dokładne statystyki z `BALANCE` bez ujemnych modyfikatorów typu `1-1`, a jednostki Orków, Uruków i Zdrajców mają docelowe statystyki RPG.



---

### Etap 4: Spokojne otwarcie `[0:00, 0:50)`, geometria Akweduktu/Caragdûr i 4-warunkowy Gothmog

* **Modyfikowane pliki `.py`:** `gondolin_map.py`, `gondolin_quests.py`, `gondolin_mechanics.py`, `gondolin_campaign_guide.md`.
* **Zakres działań:**
1. Wycofanie początkowych jednostek i budynków szturmowych P5/P6 na rozłączne pozycje obozowe za fosą (`Y >= 126`, `X >= 114`), zmiana właściciela wież zachodnich `(16, 26), (16, 36), (16, 48)` na `GAIA` oraz ustawienie harmonogramu: `[0:00, 0:50)` cisza bojowa (`0:02` intro, `0:30` ostrzeżenie), `0:50` bunt Maeglina P8, `1:05` główny szturm P5/P6.


2. Przesunięcie startu P2 na `(80, 48)`, budynku `aqueduct_control` na `(90, 78)`, sektora `Aqueduct_Guard` na `(82, 72, 94, 82)` oraz naprawa współrzędnych spawnów w `Aqueduct_Guard`, `East_Market` i `Balrog_Altar_Tumladen` (zero kolizji z obrysami budynków i murów).


3. Wdrożenie 4-warunkowego wyzwalacza Gothmoga (zniszczenie `caragdur_keep` + zniszczenie `aqueduct_control` $\rightarrow$ ostrzeżenie i 40 s na przegrupowanie $\rightarrow$ obecność żywych bohaterów P1/P2 na Amon Gwareth).


4. Korekta ID cywilizacji w `_configure_players_and_diplomacy`: `P1 = 1` (*Britons*), `P2 = 1` (*Britons*), `P3 = 2` (*Franks*), `P4 = 36` (*Burgundians*), `P5 = 3` (*Goths*), `P6 = 39` (*Bohemians*), `P7 = 8` (*Persians*), `P8 = 4` (*Teutons*).




* **Sposób weryfikacji:**
* *Poziom 1 i 2:* Test w `test_stage_b_grid.py` potwierdzający rozłączność wszystkich prostokątów startowych P1–P4 z obszarami spotkań bojowych, brak obiektów P5–P8 w zasięgu strzału wież P1–P4 w `0:00` oraz `0` kolizji punktów spawnu z budynkami.
* *Poziom 3 (W grze):* Przez pierwsze 50 sekund na mapie panuje całkowity spokój (brak odgłosów walki i ostrzału wież); `Aqueduct_Guard` uruchamia się dopiero po celowym marszu P2 na północ; Gothmog pojawia się wyłącznie po ostrzeżeniu i zebraniu sił na wzgórzu.



---

### Etap 5: Naprawa *Objectives* (`UI_*`), elitarnych zasadzek (`West_Forges`), symulatora i `GraceCoRespawn`

* **Modyfikowane pliki `.py`:** `gondolin_quests.py`, `gondolin_mechanics.py`, `test_stage_a_logic.py`, `gondolin_config.py`, `gondolin_campaign_guide.md`.
* **Zakres działań:**
1. Dodanie warunków utrzymania/ukończenia do wszystkich triggerów z `display_on_screen = 1` (zarówno aktywnych w `0:00`, jak i włączanych w Fazach II i III).
2. Naprawa `TriggerSimulator` w `test_stage_a_logic.py` (obsługa pustych `conditions` w kroku `0` oraz właściwych wartości `Operation.SET = 1, Operation.ADD = 2`).
3. Zastąpienie globalnego `own_fewer_objects` w `create_escalating_encounter` lokalną identyfikacją oddziału zasadzki (odporną na obecność innych Balrogów P7 na mapie oraz na *kiting* poza sektor).
4. Doprecyzowanie i przetestowanie w grze okna ochronnego `GraceCoRespawn`.


* **Sposób weryfikacji:**
* *Poziom 1 i 2:* `test_stage_a_logic.py` przechodzi w 100% (w tym nowe testy regresyjne: `0` odpalonych triggerów `UI_*` w `t = 0`, przyznanie `+200 Chwały` za Balroga w `West_Forges` przy żywych 2 początkowych Balrogach P7, brak nagrody przy odciągnięciu żywego Balroga poza sektor).
* *Poziom 3 (W grze):* Po starcie scenariusza wszystkie cele w prawym górnym rogu są czyste (nieprzekreślone) i przekreślają się pojedynczo w miarę wykonywania zadań.





---

### Etap 6: Przebudowa obiektów mapy (Kołowroty, Fontanna, *Glingal/Belthil*, bramy miejskie) i zagęszczenie wizualne

* **Modyfikowane pliki `.py`:** `gondolin_map.py`, `gondolin_mechanics.py`, `gondolin_quests.py`.
* **Zakres działań:**
1. Zmiana właściciela 14 wież Siedmiu Bram w *Orfalch Echor* na `PlayerId.GAIA` oraz wymiana 3 kołowrotów (`winch_bronze`, `winch_silver`, `winch_steel`) na nieuzbrojone obiekty mechanizmów z zachowaniem ich `reference_id`.


2. Usunięcie klasztoru z `(61, 52)`, umieszczenie nazwanego monumentu Fontanny Królewskiej w centrum basenu `(61, 61)` oraz nazwanych postumentów (`P4`) przy drzewach *Glingal* `(53, 60)` i *Belthil* `(69, 60)`.


3. Włączenie domyślnego `respect_roads = True` w `register_bldg()`, przesunięcie `salgant_manor` na `(95, 22)` i osadzenie fizycznych bram kamiennych (`64` / `88`) w murach Gondolinu.


4. Zagęszczenie architektury 7 dzielnic Gondolinu, wygładzenie prostokątnych krawędzi lasów/wyłomów oraz dodanie obozowisk oblężniczych na przedpolu i w Tumladen (przy zachowaniu limitu `< 8 500` obiektów i `3 000 .. 8 000` drzew).




* **Sposób weryfikacji:**
* *Poziom 1 i 2:* `failed_placements == 0`, `0` przecięć budynków z `road_corridors`, budżet drzew `3 000 .. 8 000` (dla sumy `349, 350, 1347, 1349`) i wszystkich obiektów `< 8 500`.
* *Poziom 3 (W grze):* Kołowroty Bram 3, 5 i 7 stoją nienaruszone i nie strzelają do wież; Fontanna Królewska, *Glingal* i *Belthil* wyświetlają poprawne nazwy po najechaniu kursorem i nie są zasłonięte klasztorem; miasto i przedpole wyglądają gęsto i naturalnie przy zachowaniu pełnej płynności ruchu armii.





---

### Etap 7: Rozbudowa testów BFS (7 bram osobno) i końcowy walidator manifestu po deserializacji

* **Modyfikowane pliki `.py`:** `test_stage_b_grid.py`, `generate_gondolin_scenario.py`, `test_stage_a_logic.py`.
* **Zakres działań:**
1. Przebudowa `test_stage_b_grid.py`: wykorzystanie dokładnych footprintów zapisanych w `SafeMapGrid` zamiast ręcznej tabeli ID; osobne testy otwierania każdej z 7 Bram *Orfalch Echor* (`orfalch_gate_1` .. `orfalch_gate_7` pojedynczo); osobne testy wejścia na Dolny i Górny Szlak Tumladen; testy negatywne (zablokowanie alei murem i wąskiego gardła budynkiem).
2. Rozbudowa `inspect_and_validate_scenario()` w `generate_gondolin_scenario.py`: generowanie słownika `validation_manifest` przed zapisem i twarda weryfikacja asercyjna po ponownym wczytaniu pliku z dysku (`AoE2DEScenario.from_file`) obejmująca: `map_size == 240`, `active_players == 8`, role `human/AI`, cywilizacje, symetryczną macierz dyplomacji `8×8`, obecność 9 bohaterów, poprawność `reference_id` wszystkich `quest_buildings`, brak pustych warunków w triggerach `UI_*`, brak niefiltrowanych `objects_in_area` oraz zgodność 1:1 parametrów wszystkich efektów `modify_attribute` przed i po serializacji.




* **Sposób weryfikacji:**
* *Poziom 1, 2 i 3:* 100% PASS w `test_stage_a_logic.py`, `test_stage_b_grid.py` i `generate_gondolin_scenario.py` oraz końcowy test przejścia Faz I–III w grze *AoE2: DE*.

- [x] **Weryfikacja pętli `looping = True` + `Timer`:** Zbadano empirycznie plikiem `Gondolin_A2B_T1_LoopTimerProbe5s`. Mechanizm działa poprawnie, wykonując akcje co 5 sekund. Hipoteza awarii silnika przez pętle czasowe ODRZUCONA.
- [x] **Narzędzia diagnostyczne Runtime CTD (`validate_scenario.py` + `DEBUG_CHAT`):** Wdrożono automatyczny zestaw testów `pytest` (6 klas błędów CTD: `armour_attack_class`, pętle bez `Timer >= 1`, odwrócone prostokąty obszarów, wyjście poza granice mapy, operacje na usuniętych obiektach oraz operacje na obiektach zwłok `DEAD_ID` i pociskach `ProjectileInfo`) oraz instrumentację `inject_debug_chat_into_triggers` (`DEBUG_CHAT = True`, 1 efekt `Send Chat` dla P1 na początku każdego z 322 triggerów).
- [x] **Izolacja i naprawa Runtime CTD w triggerach oraz ID jednostek:** Naprawiono wszystkie błędy wykryte przez `validate_scenario.py` oraz audyt (`8/8 PASS` w `pytest`, `100% PASS` w `test_stage_a_logic.py` i `test_stage_b_grid.py`): wymieniono 7 błędnych ID (`693->694`, `1124->1125`, `1130->1131`, `756->757`, `469->868`, `532->892`, `682->200`), skorygowano `HERO_RANGED_IDS`, usunięto bezczasową pętlę `#317`/`#318`, zabezpieczono `P6_Dragon_Drop_*` limitem populacji i anty-tłokiem oraz dodano strażnika przed zapisem w `generate_gondolin_scenario.py` (pozostawiono `DEBUG_CHAT = True` do weryfikacji 3× 3–5 min w grze), przy pełnej walidacji na:
  1. Brakujących klasach pancerza/ataku w `Modify Attribute` (`armour_attack_class`).
  2. Spójności referencji ID jednostek po ich zniszczeniu/śmierci.
  3. Weryfikacji prostokątów obszarów (`x1 <= x2` oraz `y1 <= y2`).
- [x] **Eliminacja zawieszeń `AppHangB1` (`PromiDE` `Sig[3]=185d`) i błędów binarnych po testach `0:19 / 1:33 / 3:09`:** Po analizie plików `.aoe2record` i raportów WER wdrożono blokadę `set_immobile_ai()` + `lock_personality = True` na `P1–P8`, poprawne enumy `Civilization` i `change_diplomacy` w `0:01`, wymianę nieznanego ID `817 -> 1279` oraz `303 -> 304`, zamianę `Operation.MULTIPLY` (`qty=0` na `HIT_POINTS`) na całkowitoliczbowe `Operation.SUBTRACT`, filtrowanie obszarowego `damage_object`/`kill_object` (`OBJECT_TYPE_MILITARY`), warunki `timer=999999` na 18 banerach `UI_*` oraz rozbudowę walidatora do `10/10 PASS` w `pytest validate_scenario.py`.