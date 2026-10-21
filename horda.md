# Scenariusz 3: Kroniki Rubieży — Horda i Ekspedycje (v3.3 — 4P Co-op RPG/RTS)

**Plik scenariusza:** `Kroniki_Rubiezy_Horda_Coop.aoe2scenario`  
**Typ rozgrywki:** Obrona przed 12 rosnącymi falami zmutowanej Hordy + Eksploracja, 4 Questy poboczne i niszczenie 6 Settlementów (Grades 1–3)  
**Rozmiar mapy:** 200×200 (Olbrzymia)  
**Wymagane mody zewnętrzne:** Brak (wszystkie 6 klas zmodyfikowanych jednostek, lista zadań UI, opisy w menu gry oraz lokalne aury są wbudowane bezpośrednio w plik scenariusza)

---

## 1. Opis rozgrywki i układ Twierdzy Sojuszu

Wszyscy 4 gracze startują na **równych, symetrycznych warunkach** (500 żywności, 600 drewna, 400 złota, 300 kamienia, 200 limitu populacji, 6 wieśniaków i 1 skaut) wewnątrz rozległej Twierdzy Sojuszu w południowo-zachodniej części mapy:

* **Wspólna wizja od 1. sekundy:** Wszyscy gracze mają od startu zbadaną **Kartografię** — widzicie swoje bazy i ruchy sojuszników bez konieczności budowania Targowiska.
* **Przestronne bazy i zapas drewna:** Town Center graczy są oddalone od siebie o 38–45 kratek. Każdy gracz posiada **2 własne lasy bezpośrednio przy TC**, a wzdłuż zachodniej i południowej ściany Twierdzy ciągnie się **Puszcza Zaplecza** dochodząca do samej krawędzi mapy.
* **Trzy ufortyfikowane przełęcze:** Twierdza posiada 3 wejścia:
  1. **Brama Północna** `(48, 100)`
  2. **Brama Centralna** `(104, 114)`
  3. **Brama Wschodnia** `(104, 162)`  
  Na starcie każda przełęcz jest zamknięta **Wzmocnioną Palisadą (+400 HP)** z **Bramą Palisadową** i **2 Wieżami Strażniczymi** po wewnętrznej stronie, szczelnie połączoną ze ścianą lasu.
* **Serce Twierdzy (Cytadela Sojuszu):** W centrum Twierdzy `(54, 146)` stoi **Cytadela Sojuszu (wzmocniona Feitoria +5000 HP)**. Jej utrata oznacza porażkę całej drużyny (budynek nie uruchamia licznika 350 lat jak zwykły Cud).

### Czytelność i nawigacja w trakcie meczu
1. **Kompaktowa lista celów (Objectives w prawym górnym rogu):** Wyświetla we właściwej kolejności 4 Questy poboczne oraz 6 Settlementów Hordy. Zrealizowane cele są automatycznie przekreślane.
2. **Punktowa widoczność celów z zachowaniem Mgły Wojny:** Mapa jest spowita normalną Mgłą Wojny (*Fog of War*), ale nad samymi budynkami 4 Questów i 6 Settlementów znajdują się punktowe odsłaniacze (promień 10 kratek). Od `0:00` widzicie każdy cel, możecie na niego kliknąć i przeczytać jego podpis na dolnym pasku.
3. **Wbudowany poradnik w menu gry:** Pełny opis zasad, bestiariusz i lista nagród są zapisane wewnątrz pliku scenariusza — w każdej chwili możesz je sprawdzić w grze w zakładkach **Instructions / Hints / Scouts**.

---

## 2. Harmonogram fal i stopniowe wprowadzanie jednostek specjalnych

* **Pierwsza fala:** Uderza w **10:00**. Kolejne fale nadchodzą **co 3 minuty**. Po każdym uderzeniu macie **~2,5 minuty Okna Ekspedycyjnego** na wyjście armią w otwarte pole.
* **Globalna Eskalacja Hordy:** Rozpoczyna się dopiero **po pierwszym ataku** (pierwszy bonus w **14:00**, a potem co 4 minuty) — każdorazowo dodaje wszystkim jednostkom bojowym wroga **+25 HP i +2 Ataku**.
* **Etapowe wprowadzanie jednostek i technologii (Feudal -> Castle -> Imperial):**
  * **Fala 1 (`10:00` — Feudal Age):** Czysto feudalna armia (Zbrojni, Łucznicy, Skauci + 1 zwykły Taran) z ulepszeniami `+1` w Kuźni. **Brak jednostek specjalnych.**
  * **Fala 2 (`13:00` — Późny Feudal):** Armia feudalna wsparta pierwszymi pojedynczymi specjalistami: **2 Berserkerów** (Północ) i **2 Snajperów**.
  * **Fala 3 (`16:00` — Wczesny Castle Age):** Trzon armii przechodzi w Castle Age (Pikinierzy, Kusznicy, Rycerze, Huskarlowie, ulepszenia `+2` i Balistyka) + pierwsze pojedyncze **jednostki Kamikaze** (2 Petardy i 2 Płonące Wielbłądy).
  * **Fala 4 (`19:00` — Środkowy Castle Age):** Debiut pierwszego **Arcymaga Tarczy (1 Imam + 2 Szamanów)** na Bramie Centralnej.
  * **Fala 5 (`22:00` — Późny Castle Age):** Debiut pojedynczego **Kolosa Oblężniczego (22 zasięgu)** na północy.
  * **Fala 6 (`25:00` — Przełom Castle/Imperial):** Debiut pierwszych **Tytanów Hordy (Słonie Bojowe 1400 HP)**.
  * **Fale 7–12 (`28:00 – 43:00+` — Imperial Age + tryb Endless):** Pełna armia Imperialna z ulepszeniami `+3` i rosnącą liczbą wszystkich 6 klas mutantów. Od 43. minuty Fala 12 powtarza się cyklicznie co 3 minuty, a co 4 minuty nadal rośnie HP i atak wroga.

---

## 3. Bestiariusz Hordy — 6 klas zmodyfikowanych jednostek wroga

| Jednostka specjalna (Od której fali) | Frakcja / Pochodzenie | Zmodyfikowane statystyki i zachowanie | Jak kontrować? |
| :--- | :--- | :--- | :--- |
| **1. Berserkerzy Szturmowi** *(od Fali 2 — 13:00)* | **P5 (Turkusowy)** — Obóz Północny (G1) | **Prędkość `1.45`** (biegają jak jazda), **320 HP**, **+18 ataku wręcz**, **0 pancerza na strzały**. | Rozstrzeliwać łucznikami/kusznikami zanim dobiegną do zwarcia. |
| **2. Snajperzy** *(od Fali 2 — 13:00)* | **P6 (Fioletowy)** — Akademia Artylerii (G2) | **20 zasięgu** (więcej niż Zamki), **+110 ataku**, strzał co **6,0 s**, **140 HP**. | Szybki wypad lekką jazdą lub rycerzami na tyły kolumny wroga. |
| **3. Fanatycy Kamikaze i Płonące Wielbłądy** *(od Fali 3 — 16:00)* | **P5 (Turkusowy)** — Obozy Przednie (G1) | **+65% prędkości ruchu**, **220 HP**, **promień wybuchu 2,5 kratki**, **+120 obrażeń**. | Zestrzelić na podejściu lub podstawić pojedynczą tanią jednostkę przed murem/szykiem. |
| **4. Arcymagowie Tarczy i Szamani Krwi** *(od Fali 4 — 19:00)* | **P7 (Szary)** — Klasztor Arcymagów (G2) | **550 HP (Mag) / 280 HP (Szaman)**. **Lokalna Aura (tylko 25 kratek wokół Bramy Centralnej):** daje wojskom P7 **+60/60 Pancerza** (otrzymują tylko 1 dmg) i leczy **+100 HP co 2s**. | Gdy Mag wchodzi w strefę 25 kratek, gra puszcza na niego flarę. Wyfokusować i zabić Imama — jego śmierć natychmiast zdejmuje barierę. |
| **5. Kolosy Oblężnicze** *(od Fali 5 — 22:00)* | **P6 (Fioletowy)** — Akademia Artylerii (G2) | **22 zasięgu**, **850 HP**, **+90 ataku**, **promień wybuchu 2,8 kratki**, ale strzelają raz na **10 s** i jadą wolno (`0.4`). | Obserwować lecące pociski i rozpraszać szyk, po czym wjechać jazdą w ich martwą strefę. |
| **6. Tytani Hordy** *(od Fali 6 — 25:00)* | **P8 (Pomarańczowy)** — Cytadele Hordy (G3) | **1400 HP**, **+25 ataku wręcz**, **tratowanie obszarowe (1,5 kratki)**. | Masować halabardników lub konwertować mnichami. |

---

## 4. Cztery Questy poboczne w otwartym polu

Każdy Quest jest chroniony przez garnizon pojawiający się w momencie podejścia Waszego oddziału (min. 5 jednostek). Aby odebrać nagrodę dla całej czwórki, należy **zburzyć budynek Questu do 0 HP**:

1. **`Q1 - Karawanseraj (zasoby + handel)` — Wrogie Targowisko `(154, 182)`:**
   * **Nagroda:** **+500 Złota** dla każdego, **po 3 darmowe Wozy Handlowe** oraz utworzenie 2 sojuszniczych Targowisk w rogu mapy `(152–158, 190)` pod bezpieczny szlak handlowy.
2. **`Q2 - Klif Artylerii (ulepszenia + atak)` — Wrogie Uniwersytet `(28, 32)`:**
   * **Nagroda:** Darmowe zbadanie **Balistyki, Chemii, Inżynierów Oblężniczych i Thumb Ring** oraz stały bonus **+4 Ataku i +12% prędkości ruchu** dla jazdy i strzelców wszystkich graczy.
3. **`Q3 - Skarbiec (zasoby + staly dochod)` — Wrogie Krepost za murami `(142, 118)`:**
   * **Nagroda:** **+400 Żywności, Drewna i Złota** od ręki ORAZ uruchomienie pasywnego dochodu (**+120 Żywności, +120 Drewna i +100 Złota co minutę** dla każdego gracza do końca gry).
4. **`Q4 - Krwawy Oltarz (+50 HP i slabsi Magowie)` — Wrogie Klasztor `(105, 20)`:**
   * **Nagroda:** Zmniejsza maksymalne HP wrogich Magów o **80%** (z 550 do 120 HP) i daje Waszym jednostkom bojowym **+50 Max HP**.

---

## 5. Sześć Settlementów Hordy (Grades 1–3) i „Furia Hordy”

Zburzenie głównego budynku (Wieży lub Zamku) w danym Settlemencie **trwale wyłącza jego jednostki z kolejnych fal** i daje każdemu graczowi **+500 Złota i +500 Żywności**, **ALE** uruchamia **Furię Hordy** (pozostałe obozy otrzymują stały bonus **+30 HP i +2 Ataku** oraz wysyłają natychmiastowy kontratak na Bramę Centralną):

* **`G1 - Polnocny` `(76, 72)` — Wieża Strażnicza:** Usuwa z fal Berserkerów i Petardy Kamikaze.
* **`G1 - Wschodni` `(132, 152)` — Wieża Strażnicza:** Usuwa z fal Huskarlów i Płonące Wielbłądy.
* **`G2 - Akademia` `(68, 34)` — Zamek P6:** **Trwale usuwa z gry Snajperów i Kolosy Oblężnicze!**
* **`G2 - Klasztor` `(148, 72)` — Zamek P7:** **Trwale usuwa z gry Magów Tarczy i Szamanów!**
* **`G3 - Cytadela Pln.` `(142, 24)` oraz `G3 - Cytadela Wsch.` `(176, 56)` — Główne Zamki P8:** Usuwają Tytanów Słoniowych. Zburzenie wszystkich 6 Settlementów daje zwycięstwo!

---

## 6. Warunki uruchomienia w lobby (Konfiguracja)

W menu gry wybierz: **Multiplayer -> Host Game -> Game Mode: Custom Scenario -> `Kroniki_Rubiezy_Horda_Coop`**.

| Slot / Kolor | Typ gracza | Pozycja w Twierdzy | Drużyna | Rekomendowana cywilizacja |
| :--- | :--- | :--- | :--- | :--- |
| **1 (Niebieski)** | **Człowiek** | Północny-Wschód Twierdzy `(76, 124)` — blisko Bramy Centralnej | Drużyna 1 | Dowolna (start w pełni symetryczny) |
| **2 (Czerwony)** | **Człowiek** | Południowy-Zachód Twierdzy `(32, 164)` — zaplecze leśne | Drużyna 1 | Dowolna |
| **3 (Zielony)** | **Człowiek** | Północny-Zachód Twierdzy `(32, 122)` — blisko Bramy Północnej | Drużyna 1 | Dowolna |
| **4 (Żółty)** | **Człowiek** | Południowy-Wschód Twierdzy `(76, 168)` — blisko Bramy Wschodniej | Drużyna 1 | Dowolna |
| **5 (Turkusowy)** | **AI (Extreme)** | Obozy Przednie (Grade 1 — Berserkerzy i Kamikaze) | Drużyna 2 | Goci lub Wikingowie |
| **6 (Fioletowy)** | **AI (Extreme)** | Akademia Artylerii (Grade 2 — Snajperzy i Kolosy) | Drużyna 2 | Turcy |
| **7 (Szary)** | **AI (Extreme)** | Klasztor Arcymagów (Grade 2 — Magowie i Szamani) | Drużyna 2 | Saraceni lub Hiszpanie |
| **8 (Pomarańczowy)**| **AI (Extreme)** | Cytadele Hordy (Grade 3 — Tytani i Paladyni) | Drużyna 2 | Persowie lub Khmerzy |

* **Widoczność mapy (Map Visibility):** **Normalna (Normal)** — zachowuje klimatyczną Mgłę Wojny, podczas gdy same budynki Questów i Settlementów są punktowo odsłonięte przez scenariusz.
* **Limit populacji:** **200**.
* **Zablokuj drużyny (Lock Teams):** **Wyłączone** (dyplomację i Kartografię ustawia trigger w 1. sekundzie).