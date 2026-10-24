# Scenariusz 3: Kroniki Rubieży — Horda i Ekspedycje (v5.2 — 4P Co-op RPG/RTS)

**Plik scenariusza:** `Kroniki_Rubiezy_Horda_Coop.aoe2scenario`  
**Typ rozgrywki:** Obrona przed 14 falami Hordy + Eksploracja, 4 Questy dające stałe perki cywilizacyjne i niszczenie 6 Settlementów (Grades 1–3)  
**Horyzont czasowy partii:** 60–90 minut  
**Rozmiar mapy:** 200×200 (Olbrzymia)  

---

## 1. Opis rozgrywki i układ Twierdzy Sojuszu

Wszyscy 4 gracze startują na równych warunkach (500 żywności, 600 drewna, 400 złota, 300 kamienia, 6 wieśniaków i 1 skaut) wewnątrz rozległej Twierdzy Sojuszu w południowo-zachodniej części mapy:

* **Wspólna wizja i stały podgląd celów (`LOS = 4`):** Wszyscy gracze mają od startu zbadaną **Kartografię**. Nad samym środkiem każdego budynku Questu i Settlementu wisi stały punktowy odsłaniacz o minimalnym zasięgu (`4` kratki), dzięki czemu w każdej chwili możecie kliknąć na budynek zadania i sprawdzić jego opis, podczas gdy reszta mapy pozostaje pod Mgłą Wojny.
* **Cytadela Sojuszu (Feitoria Gracza 2):** W centrum Twierdzy `(54, 146)` stoi wzmocniona **Feitoria należąca do Gracza 2** (+3000 HP oraz +20 limitu populacji dla Gracza 2). Jej utrata oznacza porażkę drużyny.
* **Trzy przełęcze bojowe + Brama Handlowa:** Brama Północna `(48, 100)`, Centralna `(104, 114)`, Wschodnia `(104, 162)` oraz Południowa Brama Handlowa `(104, 193)` są na starcie zamknięte pełną **Wzmocnioną Palisadą (+400 HP)** z **Bramą Palisadową** i **2 Wieżami Strażniczymi** (bez sztucznych klifów zwężających wejście).
* **Działanie Mnichów:** Mnisi graczy (`P1–P4`) działają w 100% normalnie (mogą leczyć sojuszników i konwertować zwykłe jednostki wroga). Mnisi komputerowi (`P5–P8`) mają zablokowaną konwersję, natomiast Arcymagowie (`P7`) leczą pobliskie jednostki Hordy obszarowo (+15 HP co 3s).

---

## 2. Harmonogram fal i trzystopniowe skalowanie pod grę 60–90 min

* **Fala 1 (8:30):** Szturm Feudalny **bez taranów i bez jednostek specjalnych** (po 11 jednostek piechoty/łuczników/skautów na bramę — wymusza dorobienie pierwszych jednostek, bo same wieże nie utrzymają palisady).
* **Fala 2 (13:00):** Szturm Feudalny **z pierwszym Taranem i Mangonelem, ale nadal bez jednostek specjalnych**.
* **Fala 3 (18:00) i kolejne fale (4–14) co 5,5 minuty (330 sekund):** Od 18. minuty zaczynają stopniowo wchodzić jednostki specjalne.
* **Trzystopniowa Eskalacja Hordy (równoważąca potężne perki z Questów):**
  * **Od 20:00 (Bieg 1):** Co 5 minut jednostki bojowe Hordy otrzymują **+5 HP i +1 Ataku**.
  * **Od 45:00 (Bieg 2 — Late-Game):** Co 5 minut dochodzi dodatkowe **+9 HP i +1 Ataku**.
  * **Od 55:00 (Bieg 3 — Endgame):** Co 5 minut dochodzi kolejne **+10 HP i +2 Ataku**, a każdy ukończony przez Was Quest i zburzony Settlement dodatkowo wzmacnia pozostałe siły Hordy.

---

## 3. Bestiariusz Hordy — 6 wyspecjalizowanych klas jednostek (z Poświatą Bohatera)

| Jednostka specjalna (Od której minuty) | Rola i specjalizacja | Sposób pokonania / Kontra |
| :--- | :--- | :--- |
| **1. Taran-Żółw / Żelazny Słoń** *(od 34:30 — Słoń Bojowy P8)* | **Tank i Niszczyciel Budynków:** **1450 HP**, **+10/+12 pancerza**, **odporny na konwersję**. Ma **+220 obrażeń przeciwko budynkom i murom**, ale zadaje **tylko 3 obrażenia jednostkom**! | W walce z Waszą armią jest niegroźny — zignorujcie go, wybijcie resztę fali, a potem otoczcie Halabardnikami (+60 bonus dmg) zanim dojdzie do zamków. |
| **2. Szakale Dywersyjne** *(od 18:00 — Huzarzy P7)* | **Eco-Raiders (Rozproszenie uwagi):** Prędkość **`1.62`**, **+6 pancerza na strzały**, ale **tylko 2 ataku**. Otrzymują rozkaz `Move` prosto w linie drwali i farm pod Waszymi 4 Town Center! | Jeśli brama jest otwarta lub uszkodzona, omijają front i wjeżdżają w wieśniaków. Schowajcie chłopów do TC i cofnijcie kilku rycerzy/pikinierów. |
| **3. Arcymag Tarczy** *(od 23:30 — Imam P7)* | **Globalny Support Hordy:** W promieniu 25 kratek przed Bramą Centralną daje **+30/+30 Pancerza i leczy (+15 HP/3s) wszystkie 4 frakcje Hordy (P5–P8)**! Nie konwertuje. | Ma złotą poświatę, a co 8 sekund gra puszcza **flarę na jego pozycję**. Ma **240 HP**, **3/4 pancerza** i **regenerację 5 HP/s** — skupcie na nim ogień, by go dobić i zdjąć tarczę z całej Hordy. |
| **4. Moździerz Oblężniczy** *(od 29:00 — Onager P6)* | **Artyleria Dalekosiężna:** **350 HP**, **21 zasięgu**, **+75 ataku**, promień wybuchu **2,6 kratki**. | **Martwa strefa 6 kratek (`Minimum Range = 6`)** oraz strzał raz na **10 s**. Nie może strzelać do celów bliższych niż 6 kratek — po dojechaniu jazdą w zwarciu jest bezbronny. |
| **5. Snajperzy Imperialni** *(od 18:00 — Janczarzy P6)* | **Egzekutor pojedynczych celów:** **90 HP**, **19 zasięgu**, **+85 ataku** (~107 dmg w jeden cel). | Strzelają co **6,5 s** i nie mają obrażeń obszarowych — zasypcie ich grupą tanich jednostek lub dojedźcie kawalerią. |
| **6. Berserkerzy i Kamikaze** *(od 18:00 — P5)* | **Szturmowcy i Saperzy:** Szybcy (`1.40–1.50`), wysoki atak wręcz / wybuch obszarowy `2,4`. | Posiadają **0 pancerza przeciw strzałom** — wycinajcie ich łucznikami i kusznikami zanim dobiegną. |

---

## 4. Cztery Questy poboczne (Chronione garnizonem na smyczy terytorialnej)

Każdy Quest jest chroniony przez wieże oraz garnizon, który spawnuje się przy zbliżeniu nawet pojedynczego skauta i trzyma się w promieniu 9 kratek od budynku:

1. **`Q1 - Karawanseraj (Mur Handlowy, +30 Pop, +20% Eko)` — Targowisko `(154, 190)`:**
   * **Automatycznie buduje ciągły Mur Obronny (`Fortified Wall`) z 6 Basztami (`Keep`)** wzdłuż dolnej krawędzi mapy (od ściany lasu Twierdzy `x=105` aż do prawego rogu mapy `x=199`) oraz stawia 2 sojusznicze Targowiska na `(193, 193)`, tworząc bezpieczny, 180-kratkowy korytarz handlowy!
   * Daje **+30 Limit Populacji na stałe** (`230 pop`), **+20% szybszą pracę Wieśniaków**, po 4 szybkie Wozy Handlowe i +500 Złota.
2. **`Q2 - Klif Artylerii (+2 Zasiegu, +4 Ataku, Szybkosc)` — Uniwersytet `(28, 32)`:**
   * Darmowa **Balistyka, Chemia, Inżynierowie Oblężniczy i Thumb Ring**,
   * **+2 Maksymalnego Zasięgu i +4 Ataku** dla wszystkich jednostek strzeleckich,
   * **+12% Prędkości Ruchu i +4 Ataku** dla całej kawalerii.
3. **`Q3 - Skarbiec (+20 Pop i Duzy Staly Dochod)` — Krepost za murami `(142, 118)`:**
   * **+20 Limit Populacji na stałe** (razem z Q1 daje **250 limitu populacji** na osobę!),
   * **Duży stały przychód co minutę:** **+250 Żywności, +250 Drewna, +200 Złota i +40 Kamienia co 60 sekund** dla każdego z 4 graczy.
4. **`Q4 - Krwawy Oltarz (+30% HP Armii i +40% Produkcji)` — Klasztor `(105, 20)`:**
   * **+30% Max HP oraz +2/+2 Pancerza** dla wszystkich jednostek piechoty, jazdy i strzelców graczy,
   * **+40% szybsza produkcja wojska** w Koszarach, Stajniach, Strzelnicach i Zamkach oraz obniżenie HP wrogich Arcymagów do 140 HP.

---

## 5. Sześć Settlementów Hordy (Grades 1–3)

Zburzenie głównego budynku (Wieży lub Zamku) w danym Settlemencie **trwale wyłącza jego jednostki z kolejnych fal**, daje każdemu graczowi **+600 Złota i +600 Żywności**, wywołuje kontratak i wzmacnia pozostałe obozy o **+15 HP oraz +2 Ataku**:

* **`G1 - Polnocny` `(76, 72)` — Wieża Strażnicza:** Usuwa z fal Berserkerów i Petardy.
* **`G1 - Wschodni` `(132, 152)` — Wieża Strażnicza:** Usuwa z fal Huskarlów i Płonące Wielbłądy.
* **`G2 - Akademia` `(68, 34)` — Zamek P6:** **Trwale usuwa z gry Snajperów i Moździerze Oblężnicze!**
* **`G2 - Klasztor` `(148, 72)` — Zamek P7:** **Trwale usuwa z gry Arcymagów Tarczy i Szakale Dywersyjne!**
* **`G3 - Cytadela Pln.` `(142, 24)` oraz `G3 - Cytadela Wsch.` `(176, 56)` — Główne Zamki P8:** Usuwają Żelazne Słonie-Tanki. Zburzenie wszystkich 6 Settlementów daje zwycięstwo!