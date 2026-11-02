# Specyfikacja Techniczna Scenariusza: *Silmarillion — Upadek Gondolinu (4P Co-op RPG)*

Dokument stanowi kompletną specyfikację architektoniczną, geometryczną i logiczną scenariusza kooperacyjnego dla czterech graczy w grze *Age of Empires II: Definitive Edition* (plik wyjściowy: `Silmarillion_Upadek_Gondolinu_Coop.aoe2scenario`, punkt odniesienia w repozytorium: commit `9b240dc6731e0690376db62e5c3c2fde6e983b58`). W miejscach, w których audyt wykrył rozbieżności między stanem bazowym a docelową implementacją (Etapy A–G), zestawiono oba stany.

---

## 1. Założenia fabularne, gracze, cywilizacje, kolory i dyplomacja

### 1.1. Koncepcja rozgrywki i założenia fabularne

Scenariusz typu *Tactical Hero RPG / Survival Co-op* (bez klasycznej ekonomii, zbierania surowców i trenowania jednostek) odtwarza obronę i ewakuację Ukrytego Królestwa Gondolinu podczas zdradzieckiego ataku sił Morgotha. Rozgrywka dzieli się na cztery następujące po sobie etapy:

1. **Faza I — Oblężenie Gondolinu i obrona Amon Gwareth:** Odbicie zdradzonych sektorów miasta (Caragdûr, Akwedukt), ewakuacja enklaw rzemieślniczych i uchodźców oraz finałowe starcie z Władcą Balrogów Gothmogiem na wzgórzu królewskim.


2. **Faza II — Odwrót przez Ukrytą Dolinę Tumladen:** Przemarsz dwoma równoległymi szlakami (Podziemnym Tunelem Idril i suchym korytem rzeki na południu oraz równiną i skarpami Tumladen na północy) wraz z niszczeniem obozów wilków i Ołtarza Cienia.


3. **Faza III — Przebicie przez *Orfalch Echor* (Wąwóz Siedmiu Bram):** Walka w górskim kanionie wymagająca niszczenia kołowrotów na bocznych graniach w celu otwarcia kolejnych bram.


4. **Finał — *Cirith Thoronath* (Orla Rozpadlina) i Dolina Sirionu:** Pojedynek Glorfindela z Balrogiem na wąskiej półce nad przepaścią, odsiecz Orłów Thorondora i ewakuacja Tuora, Idril oraz małego Eärendila do Doliny Sirionu.



### 1.2. Konfiguracja graczy, cywilizacji i architektury

W scenariuszu uczestniczy **8 aktywnych graczy** (`active_players = 8`) oraz neutralna frakcja **GAIA**. Wszyscy gracze rozpoczynają w **Erze Imperialnej (Imperial Age)** z zerowym stanem surowców (`Food = 0, Wood = 0, Stone = 0, Gold = 0`), przy czym zasób Złota u Gracza 1 pełni funkcję globalnego licznika **Chwały Domów Gondolinu (Glory)**.

| Gracz | Rola | Domy Noldorów / Frakcja fabularna | Cywilizacja (Stan bazowy `9b240dc6`) | Cywilizacja (Korekta docelowa) | Zestaw architektury (`architecture_set`) | Pozycja startowa `(X, Y)` |
| --- | --- | --- | --- | --- | --- | --- |
| **P1 (ONE)** | Człowiek (Drużyna 1) | Dom Skrzydła i Dom Młota Gniewu (Tuor, Rog) | `1` (*Britons*)

 | `1` (*Britons* — ujednolicone z przewodnikiem) | `1` (Zachodnioeuropejska kamienna)

 | `(61, 24)`

 |
| **P2 (TWO)** | Człowiek (Drużyna 1) | Dom Źródła i Dom Niebiańskiego Łuku (Ecthelion, Egalmoth) | `1` (*Britons*)

 | `1` (*Britons*) | `1` (Zachodnioeuropejska kamienna)

 | Bazowo `(82, 58)` $\rightarrow$ docelowo `(80, 48)`

 |
| **P3 (THREE)** | Człowiek (Drużyna 1) | Dom Złotego Kwiatu, Jaskółki i Harfy (Glorfindel, Duilin) | `2` (*Franks*)

 | `2` (*Franks*) | `1` (Zachodnioeuropejska kamienna)

 | `(68, 92)`

 |
| **P4 (FOUR)** | Człowiek (Drużyna 1) | Ród Królewski i Dom Drzewa (Idril, Galdor, Eärendil) | `33` (*Tatars* — błędne ID w kodzie)

 | `36` (*Burgundians*) | `1` (Zachodnioeuropejska kamienna)

 | `(28, 28)`

 |
| **P5 (FIVE)** | AI (Drużyna 2) | Horda Orków i Wilków z Angbandu | `3` (*Goths*)

 | `3` (*Goths*) | `2` (Środkowoeuropejska)

 | Obozy północne i Tumladen

 |
| **P6 (SIX)** | AI (Drużyna 2) | Żelazne Smoki i Machiny Oblężnicze Morgotha | `35` (*Lithuanians* — błędne ID w kodzie)

 | `39` (*Bohemians*) | `3` (Wschodnioeuropejska)

 | Wyłom północny i wschodni

 |
| **P7 (SEVEN)** | AI (Drużyna 2) | Balrogowie Morgotha i Gothmog | `8` (*Persians*)

 | `8` (*Persians*) | `4` (Bliskowschodnia)

 | Ołtarz w Tumladen i Brama 7

 |
| **P8 (EIGHT)** | AI (Drużyna 2) | Zdrajcy Maeglina (Dom Kreta) | `4` (*Teutons*)

 | `4` (*Teutons*) | `2` (Środkowoeuropejska)

 | Caragdûr i Akwedukt

 |

### 1.3. Macierz dyplomacji i ustawienia Lobby

* **Macierz dyplomacji 8×8 w pliku scenariusza:** Pełna symetryczna macierz 56 relacji kierunkowych poza przekątną:


* Gracze `P1, P2, P3, P4` mają wobec siebie status **Sojusznik (`0 = Ally`)**.


* Gracze `P5, P6, P7, P8` mają wobec siebie status **Sojusznik (`0 = Ally`)**.


* Każda para między zbiorem `{P1..P4}` a zbiorem `{P5..P8}` ma obustronnie status **Wróg (`3 = Enemy`)**.




* **Wymagane ustawienia w Lobby gry:**
* `P1–P4`: **Team 1**
* `P5–P8`: **Team 2**
* **Lock Teams (Zablokuj drużyny):** Włączone
* **Prędkość gry:** Normal (`1.7x`).





### 1.4. Zestawienie bohaterów, jednostek orszaku i przeciwników (wraz z audytem ID)

#### A. Bohaterowie Noldorów (`TRACKED_NOLDOR_HEROES` i `BALANCE["heroes"]`)

| Postać | Gracz | Docelowe statystyki (`HP / ATK / Pancerz M/P / Prędkość / Regen`) | ID w bazie (`9b240dc6`) | Rzeczywisty obiekt w bazie `.dat` / `HeroInfo` | Docelowe ID (po weryfikacji w Edytorze) |
| --- | --- | --- | --- | --- | --- |
| **Tuor** | P1 | `1350 HP / 38 ATK (kl. 4) / 7/7 / 1.25 / 120 HP/min` | `426`

 | `HeroInfo.HARALD_HARDRAADA` (pieszy topornik)

 | **`426`** (bez zmian)

 |
| **Rog** | P1 | `1450 HP / 44 ATK (kl. 4) / 8/6 / 1.20 / 120 HP/min` | `1066`

 | `HeroInfo.YODIT` (model żeński)

 | **`432`** (*William Wallace*) / `1669` / `648`

 |
| **Ecthelion** | P2 | `1300 HP / 36 ATK (kl. 4) / 8/8 / 1.25 / 120 HP/min` | `168`

 | `HeroInfo.THEODORIC_THE_GOTH` (pieszy miecznik)

 | **`168`** (potwierdzić klasę ataku `4`)

 |
| **Egalmoth** | P2 | `1050 HP / 30 ATK (kl. 3) / 5/7 / 1.20 / 120 HP/min` | `682`

 | `HeroInfo.BAD_NEIGHBOR` (**Błąd: trebuszet!**)

 | **`200`** (*Robin Hood* — pieszy łucznik)

 |
| **Glorfindel** | P3 | `1350 HP / 42 ATK (kl. 4) / 7/7 / 1.38 / 120 HP/min` | `172`

 | `HeroInfo.TAMERLANE` (**Błąd: konny łucznik kl. 3!**)

 | **`640`** (*La Hire* — pieszy szermierz)

 |
| **Duilin** | P3 | `980 HP / 34 ATK (kl. 3) / 4/6 / 1.35 / 120 HP/min` | `428`

 | `HeroInfo.HROLF_THE_GANGER` (piechota wręcz)

 | **`642`** (*Lord de Graville*) / `200`

 |
| **Idril Celebrindal** | P4 | `1150 HP / 28 ATK (kl. 4) / 6/8 / 1.30 / 120 HP/min` | `1292`

 | `UnitInfo.QUEEN` (sprawdzić animację ataku)

 | **`1292`** (lub `1066` *Yodit*, jeśli brak ataku)

 |
| **Galdor** | P4 | `1350 HP / 35 ATK (kl. 4) / 8/7 / 1.22 / 120 HP/min` | `636`

 | `HeroInfo.SIEUR_BERTRAND`

 | **`636`** (sprawdzić w Edytorze)

 |
| **Mały Eärendil** | P4 | `650 HP / 5 ATK (kl. 4) / 5/8 / 1.28 / 120 HP/min` | `430`

 | `HeroInfo.JOAN_THE_MAID` (chroniony VIP)

 | **`430`** (bez zmian)

 |

#### B. Jednostki orszaku graczy (`get_retinue_configs`) oraz wykryte błędy obiektów martwych i pocisków

* **P1 (32 jednostki):**
* `UNIT_HAMMER_SMITH_ID = 1703` (*Elite Obuch* — prawidłowy): `14` szt.


* `UNIT_WING_GUARD_ID = 693` (**Błąd w bazie: `BERSERK_DEAD` — obiekt zwłok powodujący 12 ciał u P1 w `0:00`!**) $\rightarrow$ docelowo **`694`** (*Elite Berserk*): `12` szt.


* `UNIT_WING_CHAMPION_ID = 567` (*Champion* — prawidłowy): `6` szt.




* **P2 (34 jednostki):**
* `UNIT_FOUNTAIN_GUARD_ID = 1661` (*Elite Serjeant Donjon* — prawidłowy, do porównania z `1659`): `10` szt.


* `UNIT_FOUNTAIN_HALB_ID = 359` (*Halberdier* — prawidłowy): `6` szt.


* `UNIT_ARCH_LONGBOW_ID = 530` (*Elite Longbowman* — prawidłowy): `8` szt.
* `UNIT_ARCH_RATTAN_ID = 1130` (**Błąd w bazie: `RATTAN_ARCHER_DEAD` — obiekt zwłok!**) $\rightarrow$ docelowo **`1131`** (*Elite Rattan Archer*): `10` szt.




* **P3 (32 jednostki):**
* `UNIT_FLOWER_BLADE_ID = 882` (*Condottiero* — prawidłowy): `10` szt.
* `UNIT_FLOWER_CAV_ID = 569` (*Paladin* — prawidłowy): `8` szt.
* `UNIT_SWALLOW_SNIPER_ID = 469` (**Błąd w bazie: `ProjectileInfo.TREBUCHET_FIRE` — pocisk trebusza!**) $\rightarrow$ docelowo **`868`** (*Elite Genoese Crossbowman*): `10` szt.


* `UNIT_HARP_HEALER_ID = 125` (*Monk* — prawidłowy): `4` szt. (+ `3` szt. w Dworze Salganta).




* **P4 (26 jednostek):**
* `UNIT_TREE_PIKE_ID = 1699` (*Flemish Militia* — prawidłowy): `12` szt.


* `UNIT_TREE_SLINGER_ID = 185` (*Slinger* — prawidłowy): `10` szt.
* `UNIT_IDRIL_SAPPER_ID = 440` (*Petard* — prawidłowy): `4` szt.


* **Jednostki specjalne i pomocnicze:**
* `UNIT_REFUGEE_CART_ID = 128` (*Trade Cart Empty* — 3 wozy z mithrilem przy Kuźniach Roga).


* `UNIT_REFUGEE_CIV_ID = 293` (*Female Villager* — 6 grup po 4 uchodźców `GAIA`).


* `UNIT_EAGLE_VANGUARD_ID = 752` (*Elite Eagle Warrior* — odsiecz Orłów Thorondora w finale).


* `SANCTUARY_KING_ID = 434` (*King* — selektor trudności w Sanktuarium Balansu).





#### C. Jednostki i Bossowie Sił Morgotha (`P5–P8`)

* **`ENEMY_ORC_INFANTRY_ID` (P5):** w bazie `1124` (**Błąd: `KARAMBIT_DEAD` — obiekt zwłok!**) $\rightarrow$ docelowo **`1125`** (*Elite Karambit Warrior*, `95 HP, 15 ATK`).


* **`ENEMY_ORC_BRUTE_ID = 473` (P5):** *Two-Handed Swordsman* (`185 HP, 22 ATK`).
* **`ENEMY_ORC_ARCHER_ID = 4` (P5):** *Bowman* (w bazie brak modyfikacji w `0:03` — miał bazowe `30 HP`; wymaga dodania do `Init_03s`).


* **`ENEMY_ORC_CROSSBOW_ID = 24` (P5):** *Crossbowman* (w bazie brak modyfikacji w `0:03`; wymaga dodania do `Init_03s`).
* **`ENEMY_DIRE_WOLF_ID = 89` (P5):** *Dire Wolf* (w bazie brak modyfikacji w `0:03`; wymaga dodania do `Init_03s`).
* **`ENEMY_WARG_RIDER_ID` (P5):** w bazie `756` (**Błąd: `TARKHAN_DEAD` — obiekt zwłok!**) $\rightarrow$ w testach `757` (*Elite Tarkhan*), docelowy model do decyzji + dodanie do `Init_03s`.


* **`ENEMY_IRON_DRAGON_RAM_ID = 548` (P6):** *Siege Ram* (`2400 HP, 45 ATK, 10/25 Armor`).
* **`ENEMY_FIRE_DRAKE_ID = 188` (P6):** *Flamethrower* (`1450 HP, 32 ATK, 8/15 Armor`).
* **`ENEMY_HEAVY_SCORPION_ID = 542` (P6):** *Heavy Scorpion* (wymaga dodania modyfikacji HP/pancerza w `Init_03s`).
* **`ENEMY_BALROG_BOSS_ID = 1737` (P7):** *Elite Urumi Swordsman* (`2800 HP, 48 ATK, 12/12 Armor`, obrażenia obszarowe).


* **`ENEMY_GOTHMOG_ID = 1713` (P7):** *Savar* (`4800 HP, 55 ATK, 14/14 Armor`, obrażenia obszarowe).
* **`ENEMY_MOLE_TRAITOR_ID = 878` (P8):** *Elite Boyar* (`240 HP, 26 ATK`).
* **`ENEMY_MOLE_PIKE_ID` (P8):** w bazie `532` (**Błąd krytyczny: `FAST_FIRE_SHIP` — statek ogniowy na lądzie!**) $\rightarrow$ docelowo **`892`** (*Heavy Pikeman*) lub `358` (*Pikeman*, `240 HP, 26 ATK`).


* **`ENEMY_MAEGLIN_ID` (P8):** w bazie `640` (*La Hire*) $\rightarrow$ docelowo **`176`** (*Mordred*, `2200 HP, 40 ATK, 10/10 Armor`).



---

## 2. Struktura mapy, kluczowe lokacje, strefy i budżet obiektów

### 2.1. Parametry siatki i rzeźby terenu

* **Wymiary mapy:** `240 × 240` kafelków (`57 600` kafelków).


* **Wygładzanie wysokości (Warunek Lipschitza):** Dwuprzebiegowy filtr `smooth_elevations_lipschitz()` wymusza $|\Delta h| \le 1$ pomiędzy sąsiednimi kafelkami w zakresie wysokości `0..7`:


* `elev = 0`: Przepaść wodna pod *Cirith Thoronath*.


* `elev = 1`: Fosa północna Gondolinu oraz podziemny Tunel Idril i suche koryto rzeki.


* `elev = 2..3`: Dolny taras Gondolinu i dno doliny Tumladen.


* `elev = 4`: Środkowy taras miejski Gondolinu, skarpy na Tumladen i dno wąwozu *Orfalch Echor*.


* `elev = 5..6`: Góry *Echoriath*, górne granie kołowrotów i taras wzgórza *Amon Gwareth*.


* `elev = 7`: Akropol Wieży Króla Turgona na *Amon Gwareth* oraz krawędź *Cirith Thoronath*.





### 2.2. Kluczowe regiony, budynki zadaniowe (`quest_buildings`) i bariery skalne (`destructible_rocks`)

#### Region 1: Miasto Gondolin i Wzgórze Królewskie *Amon Gwareth* (`X = 16..104, Y = 16..114`)

1. **Pierścień zewnętrzny murów i wyłomy:**
* Mury `FORTIFIED_WALL_ID (155)` biegną wzdłuż linii `X = 16`, `X = 104`, `Y = 16` i `Y = 111`, wzmocnione co ~10–12 kafelków wieżami `GUARD_TOWER_ID (234)` oraz parach bastionów bramnych `KEEP_ID (235)`.


* **Wyłom Północny:** otwarte odcinki na `Y = 111` (`X = 55..67` oraz `X = 80..86`) z lokalną teksturą zniszczeń `TerrainId.ROAD_BROKEN` i płomieniami `north_fire_objects` (`FLAME_EFFECT_ID = 303` w `X = 56..66, Y = 99..103`).


* **Fosa Północna:** pas `TerrainId.SHALLOWS` (`X = 22..98, Y = 112..116, elev = 1`), zablokowany na starcie skałami `aqueduct_dry_rocks` (`Y = 114, X = 48..74`).


* **Wyłom Wschodni:** otwarte odcinki na `X = 104` (`Y = 50..54` oraz `Y = 57..69`) z teksturą `ROAD_BROKEN`.




2. **Wzgórze *Amon Gwareth* (`amon_gwareth`: `X = 46..76, Y = 48..78`):**
* Otoczone wewnętrznym murem cytadeli z narożnymi donżonami `KEEP_ID (235)` i czterema 4-kafelkowymi wejściami na osiach głównych alei (`X = 59..62`, `Y = 61..64`).


* **Wieża Króla Turgona (`tower_of_turgon`):** `CASTLE_ID (82)`, `P1`, pozycja `(60, 71)`, `footprint = 4`, flankowana dwoma donżonami `KEEP_ID` na `(54, 71)` i `(66, 71)`.


* **Fontanna Królewska Ectheliona (`royal_fountain`: `X = 55..67, Y = 55..67`):** centralny basen wodny na `(61, 61)` (`WATER_AZURE` o promieniu 2 + pierścień `SHALLOWS` o promieniu 5), otoczony 4 posągami (`817`) i koksownikami (`499`). (W stanie bazowym na `(61, 52)` stoi `royal_fountain_bldg` jako `MONASTERY_ID = 104`; w Etapie E zostanie zastąpiony nazwanym monumentem `STATUE_ID = 817` bezpośrednio w centrum basenu `(61, 61)` po przesunięciu `MAP_REVEALER_ID` na `(61, 63)`).


* **Święte Drzewa *Glingal* i *Belthil*:** `glingal_tree` (`OLIVE_TREE_ID = 1349` na `(53, 61)`) oraz `belthil_tree` (`CYPRESS_TREE_ID = 1347` na `(69, 61)`) z sąsiadującymi posągami na `(53, 60)` i `(69, 60)` (w Etapie E posągi otrzymają własne wpisy w `quest_buildings` i własność `P4`, aby wyświetlać nazwy kursora w silniku Genie).




3. **Dzielnice Siedmiu Domów i enklawy zadaniowe:**
* **Enklawa Zachodnia — Kuźnie Roga (`enclave_forges`: `X = 18..34, Y = 52..74`):** `great_forge` (`BLACKSMITH_ID = 103`, `P1` na `(24, 56)`), `forge_workshop` (`SIEGE_WORKSHOP_ID = 49`, `P1` na `(24, 70)`) oraz 3 wozy z mithrilem (`128` na `(29, 57), (31, 57), (33, 57)`). Położenie na `Y = 56` i `Y = 70` pozostawia Aleję Zachodnią (`Y = 60..66`) w 100% drożną.


* **Enklawa Południowo-Zachodnia — Caragdûr i Dom Tuora (`caragdur_cliff`: `X = 14..26, Y = 36..48`, `caragdur_gate`: `X = 38..46, Y = 20..32`):** `house_of_tuor` (`KREPOST_ID = 1251`, `P4` na `(24, 24)`), `caragdur_keep` (`KEEP_ID = 235`, `P8` na `(18, 42)`). Dzielnica jest szczelnie odcięta w `0:00` murem wewnętrznym P8 (`Y = 44, X = 17..42` oraz `X = 42, Y = 17..44`) z bramą skalną `caragdur_blockade` (`ROCK_CLIFF_ID` na `X = 42, Y = 23..29`). *(W Etapie B wieże zachodnie na `(16, 26), (16, 36), (16, 48)` zmieniają właściciela z `P4` na `GAIA`, aby nie ostrzeliwać `caragdur_keep` przed `0:50`).*


* **Enklawa Wschodnia — Wielki Targ i Akwedukt (`enclave_market`: `X = 88..102, Y = 52..72`, `aqueduct_sluice`: `X = 78..90, Y = 68..80`):** `great_market` (`MARKET_ID = 84`, `P2` na `(93, 56)`) oraz `aqueduct_control` (`UNIVERSITY_ID = 209`, `P8` — bazowo na `(84, 74)`, docelowo w Etapie B/E na `(90, 78)` poza bulwarem `X = 80..84`).


* **Enklawa Południowo-Wschodnia — Dwór Salganta i Dom Harfy (`enclave_harp`: `X = 84..98, Y = 18..34`):** `salgant_manor` (`CASTLE_ID = 82`, `P3` — bazowo na `(91, 25)`, docelowo w Etapie E na `(95, 22)` poza korytarzem drogi), odgrodzona murem wewnętrznym (`X = 84, Y = 17..33` oraz `Y = 33, X = 85..103`) z bramą skalną `salgant_gate_rocks` (`Y = 33, X = 87..93`) i 3 Uzdrowicielami (`125` na `(89..93, 21)`).


* **Północny Wschód — Wieża ze Śniegu (`tower_of_snow`: `X = 70..78, Y = 102..110`):** `snow_watchtower` (`KEEP_ID = 235`, `P3` na `(74, 105)`).


* **6 Grup Uchodźców (`refugee_groups`, po 4 jednostki `293` `GAIA`):** `ref_smiths` `(32, 74)`, `ref_fountain` `(48, 98)`, `ref_archers` `(96, 78)`, `ref_swallows` `(82, 98)`, `ref_healers` `(78, 32)`, `ref_wrights` `(34, 46)`.




4. **Kordon oblężniczy i wyjścia do Fazy II (`tumladen_exit_rocks`):**
* Kordon skalny `ROCK_CLIFF_ID` zamyka linię `X = 105` (`Y = 2..124`) oraz `Y = 124` (`X = 2..105`), z usuwalnymi bramami skalnymi `tumladen_exit_rocks` na `(78, 50..55)`, `(78, 70..75)`, `(105, 49..55)` i `(105, 60..68)` oraz posterunkiem `idril_waygate` (`OUTPOST_ID = 598`, `P4` na `(73, 52)`).





#### Region 2: Dolina Tumladen (`X = 106..178, Y = 10..168`)

* Przedzielona na wysokości `Y = 48..57` zalesionym grzbietem i ciągłą granią skalną (`Y = 55, X = 106..171`):


* **Szlak Dolny (Południowy — Tajemne Przejście Idril):** korytarz `Y = 36..46, X = 74..185` ze strefami podkopów saperskich `lower_mine_1 (128, 36, 136, 44)` oraz `lower_mine_2 (152, 36, 160, 44)`.


* **Szlak Górny (Północny — Równina i Skarpy Tumladen):** korytarz `Y = 60..92, X = 76..185` ze skarpami `upper_cliff_1 (128, 58, 136, 66)` (`cliff_tower_1` na `132, 62`) i `upper_cliff_2 (152, 58, 160, 66)` (`cliff_tower_2` na `156, 62`), obozami wilków `wolf_camp_1 (132, 94)` i `wolf_camp_2 (156, 94)` (`STABLE_ID = 101`, `P5`) oraz na północy **Ołtarzem Cienia (`rog_altar_zone`: `138, 106, 152, 118`)** z `balrog_altar` (`KREPOST_ID = 1251`, `P7` na `(145, 112)`) i Zamkiem P7 na `(145, 119)`.





#### Region 3: *Orfalch Echor* — Wąwóz Siedmiu Bram (`X = 178..214, Y = 78..175`)

* Punkt zborny u wejścia do wąwozu: `orfalch_gathering (178, 78, 192, 92)`.


* **Siedem Bram (`orfalch_gate_1` .. `orfalch_gate_7`):** rozmieszczone wzdłuż głównej drogi kanionu na współrzędnych:
1. Brama Drewniana (`orfalch_gate_1`): `(190, 94)` — flankowana przez `OUTPOST_ID (598)`.


2. Brama Kamienna (`orfalch_gate_2`): `(198, 108)` — flankowana przez `GUARD_TOWER_ID (234)`.


3. Brama Spiżowa (`orfalch_gate_3`): `(206, 122)` — flankowana przez `GUARD_TOWER_ID (234)`, sterowana kołowrotem **`winch_bronze`** (`(188, 114)`, strefa `winch_bronze_zone: 184, 110, 192, 118`).


4. Brama Kutego Żelaza (`orfalch_gate_4`): `(208, 138)` — flankowana przez `KEEP_ID (235)`.


5. Brama Srebrna (`orfalch_gate_5`): `(202, 150)` — flankowana przez `KEEP_ID (235)`, sterowana kołowrotem **`winch_silver`** (`(194, 144)`, strefa `winch_silver_zone: 190, 140, 198, 148`).


6. Brama Złota (`orfalch_gate_6`): `(196, 162)` — flankowana przez `KEEP_ID (235)`.


7. Wielka Brama Stalowa (`orfalch_gate_7`): `(190, 174)` — flankowana przez `KEEP_ID (235)`, sterowana kołowrotem **`winch_steel`** (`(180, 171)`, strefa `winch_steel_zone: 176, 168, 184, 176`).




* Każda brama posiada parę wież na `gx - 6` i `gx + 5` (w bazie `P1`, docelowo w Etapie E `GAIA`) oraz 9-kafelkowy zator skalny `gx - 4 .. gx + 4`. Linia `Y = 174` (`X = 174..237`) i ściana `X = 174` (`Y = 175..237`) są zamknięte klifami poza `orfalch_gate_7`.



#### Region 4: *Cirith Thoronath* i Dolina Sirionu (`X = 186..232, Y = 175..230`)

* Korytarz grani (`cirith_thoronath: 186, 176, 204, 218`, `elev = 7`) z występem skalnym pojedynku Glorfindela **`glorfindel_duel_ledge (192, 193, 204, 203)`**.


* Bariera wyjściowa **`cirith_exit_rocks`** na linii `X = 218, Y = 218..226` (w ciągu klifu `X = 218, Y = 175..237`), za którą leży strefa ewakuacji **`sirion_exit (219, 216, 232, 230)`**.



#### Region 5: Sanktuarium Balansu i Pas Fazowy (`X = 1..20, Y = 170..236`)

* **Zwarta komora Sanktuarium Balansu (`X = 8..16, Y = 222..232`):** całkowicie odsłonięta i wolna od mgły wojny dzięki trzem `MAP_REVEALER_ID` na `(12, 224)`, `(12, 227)`, `(12, 230)`. Otoczona niezniszczalnymi skałami `ROCK_CLIFF_ID`. Król P1 (`SANCTUARY_KING_ID = 434`) stoi pośrodku na `(12, 227)`.
* **Kierunki wyboru trudności:**
  * **Krok w GÓRĘ ekranu (ku pochodniom na `9, 223` i `15, 223`):** strefa `harder_area (9, 223, 15, 225)` — podnosi poziom trudności (+1 / +2), wzmacniając siły Morgotha i przyznając premię `+500` / `+1000 Chwały`.
  * **Krok w DÓŁ ekranu (ku chorągwiom na `9, 231` i `15, 231`):** strefa `easier_area (9, 229, 15, 231)` — obniża poziom trudności (-1 / -2), osłabiając wrogów kosztem kary `-500` / `-1000 Chwały` (odroczonej do epilogu zwycięstwa).
  * **Automatyczna teleportacja:** po każdym wejściu w strefę Król jest natychmiast przenoszony efektem `teleport_object` z powrotem na pozycję wyjściową `(12, 227)` (Król nigdy nie jest niszczony, co pozwala na płynną korektę w obu kierunkach w zakresie `-2 <-> -1 <-> 0 <-> +1 <-> +2` w ciągu pierwszych 50 sekund gry).


* **Fizyczne znaczniki na pasie NW ukrytym w mgle wojny (`X = 1..3`, >20 kafelków od Sanktuarium):**
  * Śledzenie trudności Sanktuarium: pojedyncza pochodnia `TORCH_ID` przemieszczana dynamicznie po polach `SANCTUARY_STATE_COORDS` (`(2, 170)` dla -2, `(2, 174)` dla -1, `(2, 178)` dla 0, `(2, 182)` dla +1, `(2, 186)` dla +2).
  * Śledzenie fazy gry: znaczniki `TORCH_ID` dla `P1` na `(2, 222)` (Faza I), `(2, 226)` (Faza II), `(2, 230)` (Faza III).

### 2.3. Budżet obiektów

* **Łączna liczba wszystkich obiektów na mapie w `0:00`:** `7 024` (docelowy twardy limit: **`< 8 500` obiektów**).
* **Liczba drzew dekoracyjnych (`OAK_TREE_ID = 349`, `PINE_TREE_ID = 350`, `CYPRESS_TREE_ID = 1347`, `OLIVE_TREE_ID = 1349`):** `5 568` (docelowy budżet: **`3 000 .. 8 000` drzew**).
* **Kolizje na siatce (`failed_placements` przy `strict=True`):** `0`.

---

## 3. Mechaniki, fale, timery i logika triggerów

Scenariusz generuje łącznie **334 triggery** podzielone między moduł mechanik systemowych (`gondolin_mechanics.py`) oraz moduł zadań i faz (`gondolin_quests.py`).

### 3.1. Inicjalizacja technologii, nazw i statystyk RPG (`0:01 – 0:04`)

1. **`Init_01s_Techs_And_Names` (`timer = 1`):**
* Bada dla graczy technologie Kuźni, Uniwersytetu i Klasztoru.
* Nadaje polskie nazwy fabularne wszystkim jednostkom z `UNIT_DISPLAY_NAMES` oraz głównym budowlom (`tower_of_turgon`, `royal_fountain_bldg`, `glingal_tree`, `belthil_tree`, `great_forge`, `great_market`, `aqueduct_control`, `salgant_manor`, `snow_watchtower`, `house_of_tuor`, `caragdur_keep`, `balrog_altar`, `winch_bronze`, `winch_silver`, `winch_steel`).


2. **Rozbicie `Init_03s` per kategoria (`timer = 3`):**
* `Init_03s_Noldor_Retinue_Stats`: modyfikacje atrybutów dla jednostek orszaku `P1–P4` (`+85 HP`, `+6 ATK`, `+2/+2 Armor`, `30 HP/min` regeneracji, specjalne premie dla Kowali Młota `1703` i Gwardii Źródła `1661`, HP saperów Idril `240`).
* `Init_03s_Noldor_Hero_Stats`: pętla po 9 bohaterach `BALANCE["heroes"]` (status bohatera, MaxHP, regeneracja `120 HP/min`, atak z podziałem klas — klasa `3 = Pierce` dla `HERO_EGALMOTH_ID (200)` i `HERO_DUILIN_ID (642)` oraz klasa `4 = Melee` dla 7 pozostałych, w tym Glorfindela `640` — pancerz, prędkość, blast width).
* `Init_03s_Morgoth_Enemy_Stats`: pełne statystyki HP, ataku z przypisaną klasą oraz pancerzy melee/pierce dla wszystkich 9 typów jednostek wroga (`1125, 473, 4, 24, 89, 757, 542, 878, 892`).
* `Init_03s_Morgoth_Boss_Stats`: pętla po bossach `BALANCE["bosses"]` (`Gothmog 1713`, `Balrog 1737`, `Maeglin 176`, `Żelazny Smok 548`, `Uruloki 188`).



3. **`Init_04s_Full_Heal_After_MaxHP` (`timer = 4`):**
* Wykonuje pełne leczenie (`heal_object` na `+5000 HP`) wszystkich jednostek wojskowych `P1–P8` oraz bezpośrednią pętlę per bohater Noldorów, podnosząc ich aktualne punkty życia do nowego poziomu maksymalnego (likwidacja startowego ubytku zdrowia, np. 35/1150 HP u Idril).



### 3.2. Aury, zagrożenia środowiskowe i Sanktuarium Balansu

1. **`Aura_Fountain_Local_Heal_Allies` (`timer = 4, looping = True`):** leczy jednostki `P1–P4` stojące w sektorze `royal_fountain (55..67, 55..67)` (zastępując dawny, podatny na błędy układ dodawania i odejmowania globalnej regeneracji).
2. **`Aura_Fountain_Weaken_Balrogs` (`timer = 5, looping = True`)** oraz **`Aura_Fountain_Ecthelion_Blessing`**: osłabiają Balrogów P7 wchodzących w wodę Fontanny i wzmacniają oddziały P2 w obecności Ectheliona (`168`).
3. **`Hazard_North_Avenue_Fires` (`timer = 4, looping = True`):** zadaje obrażenia jednostkom w strefie pożaru `north_fire_zone (55..67, 98..105)` do momentu odbicia Akweduktu przez P2 (co wyłącza ten trigger i usuwa obiekty ognia `north_fire_objects`).
4. **`Aura_Rog_Wrath_Against_Balrogs`:** premia bojowa dla Roga i Kowali Młota w starciu z Balrogami P7.
5. **Sanktuarium Balansu (5-stanowy automat dwukierunkowy `-2 <-> -1 <-> 0 <-> +1 <-> +2`):**
   * Wybór trudności odbywa się za pomocą Króla P1 (`434`) w zwartej komorze `(8..16, 222..232)` w narożniku NW (całkowicie odsłoniętej przez 3 `MAP_REVEALER_ID`).
   * Krok w GÓRĘ ekranu w `harder_area (9..15, 223..225)` ku pochodniom podnosi trudność o +1 (do maks. +2), dodając wrogom HP i atak oraz przyznając `+500` / `+1000 Chwały`.
   * Krok w DÓŁ ekranu w `easier_area (9..15, 229..231)` ku chorągwiom obniża trudność o -1 (do min. -2), redukując statystyki wrogów. Kary punktowe (`-500` / `-1000 Chwały`) są odraczane do momentu zwycięstwa w `Victory_Reached_Vale_Of_Sirion`, aby uniemożliwić exploit z zerowaniem stanu złota w pierwszych sekundach gry.
   * Po każdym kroku Król jest teleportowany (`teleport_object`) na środek `(12, 227)` bez usuwania jednostki. Stan trudności śledzi pojedyncza pochodnia na odizolowanym pasku `X=2, Y=170..186` ukrytym w mgle wojny.

### 3.3. System „Trzech Pieczęci Turgona” i okno ochronne `GraceCoRespawn`

Mechanizm wspólnych żyć drużyny (`_setup_three_seals_of_turgon` w `gondolin_quests.py`):

1. **Śledzenie aktualnej fazy za pomocą fizycznych znaczników:**
* Na pasie NW przechowywany jest fizyczny obiekt `TORCH_ID (499)` należący do `P1`:
* Faza I: `(2, 222)` $\rightarrow$ odrodzenie w `checkpoints["phase1"]` na *Amon Gwareth* (`P1: 61,49`, `P2: 66,56`, `P3: 61,66`, `P4: 55,56`),


* Faza II: `(2, 226)` $\rightarrow$ odrodzenie w `checkpoints["phase2"]` u wejścia na szlaki Tumladen (`P1: 110,86`, `P2: 110,40`, `P3: 114,86`, `P4: 114,40`),


* Faza III: `(2, 230)` $\rightarrow$ odrodzenie w `checkpoints["phase3"]` przed *Orfalch Echor* (`P1: 184,84`, `P2: 186,84`, `P3: 184,88`, `P4: 186,88`).






2. **Uzbrojenie i działanie Pieczęci 1–3 (`Stage 1..3`):**
* W `0:05` trigger `Seal_Arm_Stage1_At_05s` tworzy znacznik Fazy I na `(2, 222)` i aktywuje 27 triggerów `Seal_Stage1_{phase}_HeroLoss_{hero}` (9 bohaterów × 3 fazy).
* Każdy trigger `HeroLoss` wymaga koniunkcji: `own_fewer_objects(source_player=p_id, object_list=h_id, quantity=0)` **ORAZ** obecności `TORCH_ID` w komórce danej fazy.
* Gdy bohater ginie:
1. Trigger natychmiast dezaktywuje wszystkie pozostałe 26 triggerów `HeroLoss` w bieżącym etapie `Stage S`,
2. Odradza poległego bohatera na współrzędnych `checkpoints[phase][p_id]` i nadaje mu imię oraz pełne leczenie,
3. Tworzy dla niego eskortę **6 jednostek gwardii domowej** (`guard_id`),
4. Aktualizuje tablicę `UI_Seals_Of_Turgon_*` (z `3/3` na `2/3`, `1/3`, `0/3`),


5. Aktywuje triggery okna ochronnego `Seal_Stage{S}_{phase}_GraceCoRespawn_{other_hero}` oraz przekaźnik `Seal_Relay_Stage{S}_To_Stage{S+1}` (`timer = 3`).




3. **Okno ochronne `GraceCoRespawn`:**
* Jeżeli w krótkim oknie po śmierci pierwszego bohatera (np. od tego samego wybuchu lub uderzenia obszarowego) zginie drugi bohater, odpowiedni trigger `GraceCoRespawn` odradza go w punkcie kontrolnym bieżącej fazy **bez utraty kolejnej Pieczęci** (i bez dodatkowej 6-osobowej eskorty).
* Po upływie timera przekaźnika (`3 s`) wszystkie triggery `GraceCoRespawn` z etapu `S` są wyłączane i uzbrajany jest etap `Stage S+1`.


4. **Czwarta śmierć (`Stage 4`):** Po wyczerpaniu 3 Pieczęci (`0/3`), śmierć dowolnego z 9 bohaterów (`Seal_Stage4_Final_Defeat_*`) kończy scenariusz porażką wszystkich graczy `P1–P4`.



### 3.4. Wzorzec eskalujących zasadzek (`create_escalating_encounter`)

Siedem kluczowych sektorów bojowych używa trójstopniowego generatora spotkań w `gondolin_mechanics.py`:

1. **`Enc_{name}_Base` (`enabled = True`):** gdy jednostka wojskowa wskazanego gracza wejdzie w obszar sektora, spawnuje oddział bazowy wroga z rozkazem `attack_move` i aktywuje `Enc_{name}_EliteAmbush`.
2. **`Enc_{name}_EliteAmbush` (`enabled = False`, `timer = 20`):** jeśli po 20 sekundach w poszerzonym sektorze (`sector ± 8` kafelków) znajduje się co najmniej 8 jednostek wojskowych graczy (`quantity = 8`), spawnuje elitarny odwód wroga, wyświetla ostrzeżenie z flarą i aktywuje `Enc_{name}_EliteReward`.
3. **`Enc_{name}_EliteReward` (`enabled = False`, `timer = 8`):** po wybiciu oddziału elitarnego i utrzymaniu sektora przez gracza przyznaje **`+200 Chwały` (Złota P1)**. *(Wyeliminowano blokowanie nagrody za Balroga w `West_Forges`: usunięto dwa początkowe statyczne Balrogi P7 stojące na mapie w `gondolin_map.py` oraz zmieniono bazowy spawn Ołtarza w Tumladen na P8, dzięki czemu w Fazie I jedynym Balrogiem P7 na mapie jest elitarny demon w Kuźniach Roga, a warunek `own_fewer_objects(P7, ENEMY_BALROG_BOSS_ID, 0)` działa niezawodnie).*



**Lista wszystkich 7 spotkań `create_escalating_encounter`:**

* `Aqueduct_Guard` (Faza I, P2): baza `6x 878 (P8)`, elita `5x 473 (P5)`.
* `West_Forges` (Faza I, P1 - Rog): baza `7x 473 (P5) + 4x 878 (P8)`, elita `1x Balrog 1737 (P7)`.
* `East_Market` (Faza I, P2): baza `10x 1124/1125 (P5) + 6x 24 (P5)`, elita `6x 756/757 (P5)`.
* `Tumladen_Wolves_1` (Faza II, P1): baza `10x 89 (P5) + 6x 756/757 (P5)`, elita `6x 756/757 (P5)`.
* `Balrog_Altar_Tumladen` (Faza II, P1 - Rog): baza `1x Balrog 1737 (P8) + 8x 473 (P5)`, elita `1x Balrog 1737 (P7)`.
* `Orfalch_orfalch_gate_3` (Faza III, P1): baza `7x 473 (P5) + 5x 24 (P5)`, elita `1x Balrog 1737 (P7)`.
* `Orfalch_orfalch_gate_5` (Faza III, P1): baza `7x 473 (P5) + 5x 24 (P5)`, elita `1x Balrog 1737 (P7)`.
* `Orfalch_orfalch_gate_7` (Faza III, P1): baza `7x 473 (P5) + 5x 24 (P5)`, elita `1x Balrog 1737 (P7)`.

### 3.5. Harmonogram fal szturmowych i zadań w Fazie I–III

| Czas / Warunek (Stan bazowy `9b240dc6`) | Czas / Warunek (Docelowo po Etapie B/D) | Nazwa triggera | Opis działania |
| --- | --- | --- | --- |
| `0:10` (`timer = 10`) | **`0:50` (`timer = 50`)** po cichym otwarciu `[0:00, 0:50)` | `P1_Spawn_Maeglin_Traitors` | Spawnuje Maeglina (`640`/`176`), 4x `878` i 4x `532`/`892` w Caragdûr z rozkazem ataku na Dwór Tuora `(26, 28)`. |
| `0:15` (`timer = 15`) | **`1:05` (`timer = 65`)** | `P6_Spawn_Iron_Dragons_Phase1` | Spawnuje Żelazne Smoki (`548`) i Uruloki (`188`) w wyłomie północnym i wschodnim z rozkazem `attack_move` w głąb alei.

 |
| `0:32` (`timer = 32, looping = True`) | Przebudowa po teście sondy `a2_t1_loop_timer_probe` | `P6_Dragon_Drop_*` (5 stref: `north_avenue Z0..Z2`, `east_avenue Z0..Z1`) | Dopóki w danej strefie alei znajduje się żywy taran P6 (`548`), zrzuca oddział szturmowy P5 (`5x 1124/1125, 2x 473, 2x 24`) z rozkazem marszu na `(61, 63)`. |
| Wejście P1 w `caragdur_gate (38..46, 20..32)` | Bez zmian | `P1_Tuor_Breaches_Caragdur_Gate` | Usuwa skały `caragdur_blockade`, łącząc siły P1 (Tuora) i P4 (Idril), oraz przyznaje `+150 Chwały`. |
| Zniszczenie `caragdur_keep` (ref `68`) | Bez zmian | `P1_Quest_Caragdur_Completed` | Kończy oblężenie Caragdûr, przyznaje `+300 Chwały` i nagradza P4 dodatkowymi jednostkami. |
| Zniszczenie `aqueduct_control` (ref `25`) | Bez zmian | `P1_Quest_Aqueduct_Completed` | Gasi pożary `north_fire_objects` na północy, usuwa `aqueduct_dry_rocks` (zalewając fosę północną) i przyznaje `+300 Chwały`. |
| Duilin (`428`/`642`) w `tower_of_snow` | Bez zmian | `P1_Quest_SnowTower_Completed` | Odsłania mapę wokół murów, daje `+1` zasięgu łucznikom P2/P3 i `+200 Chwały`. |
| Idril (`1292`) w `royal_fountain` | Bez zmian | `P1_Quest_SacredTrees_Completed` | Zabezpiecza pędy *Glingal* i *Belthil*, daje `+60 HP` bohaterom i `+200 Chwały`. |
| Wóz (`128`) P1 na `amon_gwareth` | Bez zmian | `P1_EnclaveA_Forges_Mithril_Delivered` | Daje `+3 ATK` piechocie Noldorów, spawnuje 12 Kowali (`1703`) dla P1 i `+350 Chwały`. |
| Glorfindel (`172`/`640`) w `enclave_harp` | Bez zmian | `P1_EnclaveC_Harp_Liberated` | Usuwa `salgant_gate_rocks`, spawnuje kawalerię (`569`) i mnichów (`125`) dla P3 oraz `+250 Chwały`. |
| Zniszczenie `caragdur_keep` + `aqueduct_control` | **4-warunkowy:** jw. + ostrzeżenie `40s` + obecność bohaterów P1/P2 na Amon Gwareth | `P1_Boss_Spawn_Gothmog_AmonGwareth` | Spawnuje Gothmoga (`1713`), Balroga (`1737`) i 10 Uruków (`473`) na `(61, 82)` z atakiem na `(61, 60)`. |
| Śmierć Gothmoga (`1713`) po spawnie | Bez zmian | `P1_Phase1_Complete_Open_Tumladen` | Usuwa `tumladen_exit_rocks`, przełącza token fazy na Fazę II `(2, 226)`, przyznaje `+500 Chwały` i aktywuje triggery Fazy II. |
| Wejście P4 w `lower_mine_1 / 2` | Bez zmian | `P2_LowerRoute_Detonate_Mine_1 / 2` | Wysadza podkopy pod obozami wilków `wolf_camp_1 / 2` na Górnym Szlaku, niszcząc je od dołu (`+250 Chwały`). |
| Zniszczenie `cliff_tower_1 + 2` | Bez zmian | `P2_UpperRoute_Cliffs_Cleared` | Oczyszcza skarpy nad szlakiem Tumladen (`+300 Chwały`). |
| Zniszczenie `balrog_altar` (ref `446`) | Bez zmian | `P2_Quest_RogAltar_Completed` | Niszczy Ołtarz Cienia na północy Tumladen (`+400 Chwały`). |
| Wejście 3 jednostek P1 w `orfalch_gathering` | Bez zmian | `P3_Start_Orfalch_Echor` | Przełącza token fazy na Fazę III `(2, 230)` i otwiera pierwsze bramy wąwozu. |
| Zniszczenie `winch_bronze / silver / steel` | Bez zmian | `P3_Winch_*_Destroyed` | Usuwa skały odpowiednio `orfalch_gate_3`, `orfalch_gate_5`, `orfalch_gate_7`, zabija jednostki P5 w strefie lawiny i przyznaje `+250 Chwały`. |
| Glorfindel w `cirith_thoronath` | Bez zmian | `P3_Finale_Cirith_Thoronath_Ambush` | Spawnuje Balroga z Cirith Thoronath (`1737`) i 12 Orków, rozpoczynając pojedynek na półce `(192..204, 193..203)`. |
| Utrzymanie półki przez `25s` + zabicie Balroga **LUB** śmierć Glorfindela w pojedynku | Bez zmian | `P3_Glorfindel_Duel_PathA_Triumph` / `PathB_Sacrifice` | Dwuścieżkowy finał: w obu wariantach ginie Balrog, przybywają Orły Thorondora (`752`) i usuwane są skały `cirith_exit_rocks` (`X = 218`). |
| Tuor (`426`), Idril (`1292`) i Eärendil (`430`) w `sirion_exit` | Bez zmian | `P3_Victory_Sirion_Evacuation` | Wyświetla epilog i ogłasza **Zwycięstwo (`declare_victory`)** dla graczy `P1–P4`. |

---

## 4. Struktura plików `.py` w projekcie, konwencje i ograniczenia

### 4.1. Podział odpowiedzialności modułów w repozytorium

| Plik w repozytorium | Rola w architekturze projektu |
| --- | --- |
| **`gondolin_config.py`** | Centralny moduł konfiguracyjny (zero logiki wykonawczej): definicje wszystkich 84 stałych `*_ID`, grup graczy (`HUMAN_PLAYERS`, `AI_PLAYERS`), słownika `UNIT_DISPLAY_NAMES`, tabel balansu `BALANCE["heroes"]` i `BALANCE["bosses"]`, składów początkowych `get_retinue_configs()` oraz tekstów UI w grze (`populate_ingame_scenario_descriptions`).

 |
| **`gondolin_map.py`** | Generator geometrii 240×240 i obiektów początkowych: funkcja `footprint_bounds()`, klasa antykolizyjna `SafeMapGrid` (śledząca `occupied_tiles`, `road_corridors`, `no_tree_zones`), rzeźbienie terenu `_sculpt_world_terrain()`, wygładzanie wysokości `smooth_elevations_lipschitz()`, budowa murów i 7 dzielnic `_build_gondolin_walls_and_districts()`, lasów `_populate_forests_and_borders()` oraz funkcja główna `build_map_and_entities(scenario)` zwracająca słownik kontekstowy `ctx`.

 |
| **`gondolin_mechanics.py`** | Moduł mechanik systemowych i triggerów pomocniczych: uniwersalny adapter `safe_call()`, funkcje `apply_unit_lore_name()`, `add_chat_and_flare()`, `award_glory_gold()`, triggery inicjalizacyjne `Init_01s` i `Init_03s`, aury Fontanny Królewskiej, pożary na północy, spawny i zrzuty Żelaznych Smoków P6 oraz generator `create_escalating_encounter()`.

 |
| **`gondolin_quests.py`** | Moduł głównych osi fabularnych i warunków zwycięstwa/porażki: Sanktuarium Balansu, system „Trzech Pieczęci Turgona” z oknem `GraceCoRespawn` i dynamicznymi punktami kontrolnymi Faz I–III, ratowanie 6 grup uchodźców, zadania Faz I–III, walka z Gothmogiem, mechanizm kołowrotów Siedmiu Bram, dwuścieżkowy pojedynek Glorfindela, triggery `UI_*` oraz ewakuacja do Doliny Sirionu.

 |
| **`generate_gondolin_scenario.py`** | Punkt wejścia generatora: wyszukuje katalog scenariuszy *AoE2: DE* i plik `template.aoe2scenario`, czyści triggery i jednostki szablonu, wywołuje kolejno konfigurację opisów, budowę mapy, mechaniki i questy, zapisuje plik `.aoe2scenario` na dysk i uruchamia walidator po deserializacji `inspect_and_validate_scenario()`.

 |
| **`test_stage_a_logic.py`** | Zestaw testów jednostkowych i symulacyjnych logiki triggerów (Poziom 1): zawiera symulator `TriggerSimulator` weryfikujący filtrowanie `objects_in_area`, przejścia fazowe Pieczęci, 5 scenariuszy `GraceCoRespawn`, dwuścieżkowy finał Glorfindela oraz nagrody za zasadzki. |
| **`test_stage_b_grid.py`** | Zestaw testów geometrycznych i przejezdności (Poziom 1): weryfikuje `failed_placements == 0`, budżet drzew i obiektów, szczelność blokad w `0:00` (5 testów negatywnych BFS) i drożność wszystkich szlaków w Fazach I–III (testy pozytywne BFS) oraz generuje podgląd `gondolin_map_preview.png`.

 |
| **`stage_a1_diagnostic_and_variants.py`** | Narzędzie diagnostyczne Etapu A1/A2-bis: weryfikuje czystość commita bazowego `9b240dc6` przez `git diff` i sumy `SHA-256`, klasyfikuje wszystkie 84 stałe `*_ID` względem lokalnych enumów (`UnitInfo`, `HeroInfo`, `BuildingInfo`, `OtherInfo`, `ProjectileInfo` i relacji `dead_unit`), buduje w pamięci RAM odizolowane warianty testowe `.aoe2scenario` (w tym minimalną sondę `a2_t1_loop_timer_probe`) i przeprowadza inspekcję zdeserializowanych plików binarnych (wraz z macierzą dyplomacji 8×8).

 |
| **`reproduce_audit_metrics.py`** | Skrypt audytu statycznego oraz dostarczyciel struktur zastępczych (mock) dla środowisk CI/offline nieposiadających zainstalowanego `AoE2ScenarioParser`. |
| **`gondolin_campaign_guide.md`** | Dokumentacja projektowa i przewodnik po kampanii dla graczy. |

### 4.2. Ustalone konwencje inżynieryjne i ograniczenia projektowe

1. **Zakaz *magic numbers* poza `gondolin_config.py`:** Wszystkie identyfikatory jednostek, budynków, technologii i atrybutów w plikach mapy, mechanik i zadań muszą pochodzić wyłącznie z nazwanych stałych importowanych z `gondolin_config.py` (weryfikowane skanerem AST `scan_ast_for_magic_id_literals`).


2. **Ścisła kontrola kolizji i ochrona dróg (`SafeMapGrid`):**
* Obrysy obiektów parzystych (`2×2`, `4×4`) i nieparzystych (`1×1`, `3×3`) są wyliczane wyłącznie przez funkcję `footprint_bounds(x, y, footprint)`, a środek obiektu przekazywany do `um.add_unit` wynosi `(xmin + xmax + 1) / 2.0`.


* Wszystkie budynki miejskie i zadaniowe są umieszczane z `strict=True` (każda kolizja zgłasza wyjątek `ValueError`) oraz z poszanowaniem korytarzy drogowych (`respect_roads=True`, z jawnymi wyjątkami wyłącznie dla bram i styków murów obronnych).




3. **Obowiązkowe filtrowanie każdego warunku `objects_in_area`:** Żaden warunek `objects_in_area` w całym scenariuszu nie może mieć jednocześnie `object_list == -1` oraz `object_type == -1` (zapobiega to przypadkowemu wyzwalaniu triggerów przez ptaki `GAIA`, znaczniki `MAP_REVEALER_ID` lub płomienie).


4. **Wymóg warunków podtrzymujących na wszystkich triggerach `UI_*` (`display_on_screen = 1`):** Żaden trigger wyświetlany w panelu *Objectives* (zarówno aktywny w `0:00`, jak i włączany w późniejszych fazach) nie może mieć pustej listy `conditions` ani atrapowego `timer >= 900000`. Triggery zadań posiadają rzeczywiste warunki ich ukończenia (np. `destroy_object`, `objects_in_area`), dzięki czemu silnik Genie przekreśla je dokładnie w momencie spełnienia celów (*strikethrough*), a triggery licznikowe posiadają warunki zaporowe uniemożliwiające samoczynne wyzwolenie. Co kluczowe, triggery ukończenia zadań fabularnych nie dezaktywują powiązanych triggerów UI, pozwalając na pozostanie przekreślonego wpisu na liście celów aż do masowego czyszczenia na granicy faz.


5. **Trójpoziomowa dyscyplina walidacji:**
* **Poziom 1:** Testy symulatora i siatki geometrycznej (`test_stage_a_logic.py`, `test_stage_b_grid.py`).
* **Poziom 2:** Zapis i ponowny odczyt rzeczywistego pliku binarnego przez `AoE2DEScenario.from_file()` z porównaniem względem manifestu przed-serializacyjnego (`inspect_and_validate_scenario`, `inspect_reloaded_scenario`).


* **Poziom 3:** Rzeczywiste uruchomienie i weryfikacja wizualna/czasowa w silniku *Age of Empires II: Definitive Edition* (żaden etap nie jest uznawany za zamknięty wyłącznie na podstawie testów Poziomu 1 lub 2).

### Reguły projektowe triggerów (zweryfikowane empirycznie 2026-11-01):
1. **Dozwolone pętle czasowe:** Dozwolone i zalecane jest stosowanie `looping = True` wraz z warunkiem `Timer = X` (gdzie `X >= 1`). Silnik gry traktuje ten warunek jako interwał i wykonuje akcję periodycznie co `X` sekund.
2. **Zakaz pętli tickowych:** Bezwzględny zakaz tworzenia triggerów z `looping = True` bez warunku `Timer` lub z `Timer = 0`, aby uniknąć zawieszenia wątku głównego silnika w pojedynczej klatce.