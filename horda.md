# Scenariusz 3: Kroniki Rubieży — Horda i Ekspedycje (v6.0 — 4P Co-op RPG/RTS)

**Plik scenariusza:** `Kroniki_Rubiezy_Horda_Coop.aoe2scenario`  
**Typ rozgrywki:** Obrona przed 14 falami Hordy + Dynamiczne Sanktuarium Balansu + 4 Questy poboczne i niszczenie 6 Settlementów (Grades 1–3)  
**Horyzont czasowy partii:** 60–90 minut  
**Rozmiar mapy:** 200×200 (Olbrzymia)  

---

## 1. Sanktuarium Balansu — Zmiana trudności na żywo w trakcie meczu `(6, 150)`

W zachodnim lesie Twierdzy `(6, 150)` znajduje się odizolowana skalnymi klifami komnata, w której stoi nieśmiertelny **Inżynier Balansu (Król Gracza 1)**:

* **Ruch Królem w GÓRĘ `(6, 146)` (Pochodnie Północne):** Zwiększa poziom trudności o **+1 stopień**.
* **Ruch Królem w DÓŁ `(6, 154)` (Pochodnie Południowe):** Zmniejsza poziom trudności o **-1 stopień**.
* **Automatyczny powrót i logowanie:** Po wejściu na flagę Król jest automatycznie przenoszony z powrotem na środek `(6, 150)`, a na czacie wyświetla się wpis `[LOG BALANSU]` z aktualnym poziomem trudności, co pozwala zapisać, w której minucie i ile razy drużyna korygowała balans.
* **5 poziomów trudności (modyfikujących zarówno liczebność kolejnych fal, jak i statystyki wroga):**
  * **Poziom `-2` (Bardzo Łatwy):** **-40% liczebności kolejnych fal** oraz **-24 HP i -4 Ataku** wroga.
  * **Poziom `-1` (Łatwy):** **-20% liczebności kolejnych fal** oraz **-12 HP i -2 Ataku** wroga.
  * **Poziom `0` (Domyślny):** **100% bazowej liczebności fal** i bazowe statystyki.
  * **Poziom `+1` (Trudny):** **+25% liczebności kolejnych fal** oraz **+15 HP i +2 Ataku** wroga.
  * **Poziom `+2` (Ekstremalny):** **+50% liczebności kolejnych fal** oraz **+30 HP i +4 Ataku** wroga.

---

## 2. Opis rozgrywki i układ Twierdzy Sojuszu

Wszyscy 4 gracze startują na równych warunkach (500 żywności, 600 drewna, 400 złota, 300 kamienia, 6 wieśniaków i 1 skaut) wewnątrz rozległej Twierdzy Sojuszu w południowo-zachodniej części mapy:

* **Wspólna wizja i stały podgląd celów (`LOS = 4`):** Wszyscy gracze mają od startu zbadaną **Kartografię**. Nad samym środkiem każdego budynku Questu i Settlementu wisi stały punktowy odsłaniacz o minimalnym zasięgu (`4` kratki), dzięki czemu w każdej chwili możecie kliknąć na budynek zadania i sprawdzić jego opis, podczas gdy reszta mapy pozostaje pod Mgłą Wojny.
* **Cytadela Sojuszu (Feitoria Gracza 2):** W centrum Twierdzy `(54, 146)` stoi wzmocniona **Feitoria należąca do Gracza 2** (+3000 HP oraz +20 limitu populacji dla Gracza 2). Jej utrata oznacza porażkę drużyny.
* **Trzy przełęcze bojowe + Brama Handlowa:** Brama Północna `(48, 100)`, Centralna `(104, 114)`, Wschodnia `(104, 162)` oraz Południowa Brama Handlowa `(104, 193)` są na starcie zamknięte pełną **Wzmocnioną Palisadą (+400 HP)** z **Bramą Palisadową** i **2 Wieżami Strażniczymi**.
* **Działanie Mnichów:** Mnisi graczy (`P1–P4`) działają w 100% normalnie (mogą leczyć sojuszników i konwertować zwykłe jednostki wroga). Mnisi komputerowi (`P5–P8`) mają zablokowaną konwersję, natomiast Arcymagowie (`P7`) leczą pobliskie jednostki Hordy obszarowo (+15 HP co 3s).

---

## 3. Harmonogram fal i taktyki specjalne po 45. minucie (Trade Line + Przebicia przez Las)

* **Fala 1 (8:30):** Szturm Feudalny **bez taranów i bez jednostek specjalnych**.
* **Fala 2 (13:00):** Szturm Feudalny **z pierwszym Taranem i Mangonelem, ale nadal bez jednostek specjalnych**.
* **Fala 3 (18:00) i kolejne fale (4–14) co 5,5 minuty (330 sekund):** Od 18. minuty stopniowo wchodzą jednostki specjalne.
* **Taktyki specjalne Hordy po 45. minucie (Fale 8–14):**
  * **Główny szturm (~75–80% sił):** Nadal uderza na 3 główne bramy.
  * **Co druga fala od 45:00 (Fale 8, 10, 12, 14) — Atak na Trade Line:** Wydzielony korpus z Taranami Oblężniczymi, Paladynami i Konnymi Łucznikami uderza na południowy **Mur Handlowy (`y = 184`) i Szlak Handlowy (`y = 193`)**.
  * **Co trzecia fala od 45:00 (Fale 9, 12, 14) — Przebicie przez Las (Saperzy Oblężniczy):** Na 15 sekund przed Falą 9 (`50:45`) oraz Falą 12 (`67:15`) wrogie Onagery podjeżdżają pod ścianę lasu (z alarmem i flarą na minimapie), po czym **wycinają 4-kratkową przesiekę w lesie** — w **Północnym Lesie `(78, 100)`** w 51:00 oraz we **Wschodnim Lesie `(104, 140)`** w 67:30 — otwierając nowe wejścia na tyły bazy!

---

## 4. Bestiariusz Hordy — 6 wyspecjalizowanych klas jednostek (z Poświatą Bohatera)

| Jednostka specjalna (Od której minuty) | Rola i specjalizacja | Sposób pokonania / Kontra |
| :--- | :--- | :--- |
| **1. Taran-Żółw / Żelazny Słoń** *(od 34:30 — Słoń Bojowy P8)* | **Tank i Niszczyciel Budynków:** **1450 HP**, **+10/+12 pancerza**, **odporny na konwersję**. Ma **+220 obrażeń przeciwko budynkom i murom**, ale zadaje **tylko 3 obrażenia jednostkom**! | W walce z Waszą armią jest niegroźny — zignorujcie go, wybijcie resztę fali, a potem otoczcie Halabardnikami (+60 bonus dmg) zanim dojdzie do zamków. |
| **2. Szakale Dywersyjne** *(od 18:00 — Huzarzy P7)* | **Eco-Raiders (Rozproszenie uwagi):** Prędkość **`1.62`**, **+6 pancerza na strzały**, ale **tylko 2 ataku**. Otrzymują rozkaz `Move` prosto w linie drwali i farm pod Waszymi 4 Town Center! | Jeśli brama jest otwarta lub uszkodzona, omijają front i wjeżdżają w wieśniaków. Schowajcie chłopów do TC i cofnijcie kilku rycerzy/pikinierów. |
| **3. Arcymag Tarczy** *(od 23:30 — Imam P7)* | **Globalny Support Hordy:** W promieniu 25 kratek przed Bramą Centralną daje **+30/+30 Pancerza i leczy (+15 HP/3s) wszystkie 4 frakcje Hordy (P5–P8)**! Nie konwertuje. | Ma złotą poświatę, a co 8 sekund gra puszcza **flarę na jego pozycję**. Ma **240 HP**, **3/4 pancerza** i **regenerację 5 HP/s** — skupcie na nim ogień, by go dobić i zdjąć tarczę z całej Hordy. |
| **4. Moździerz Oblężniczy** *(od 29:00 — Onager P6)* | **Artyleria Dalekosiężna:** **350 HP**, **21 zasięgu**, **+75 ataku**, promień wybuchu **2,6 kratki**. | **Martwa strefa 6 kratek (`Minimum Range = 6`)** oraz strzał raz na **10 s**. Nie może strzelać do celów bliższych niż 6 kratek — po dojechaniu jazdą w zwarciu jest bezbronny. |
| **5. Snajperzy Imperialni** *(od 18:00 — Janczarzy P6)* | **Egzekutor pojedynczych celów:** **90 HP**, **19 zasięgu**, **+85 ataku** (~107 dmg w jeden cel). | Strzelają co **6,5 s** i nie mają obrażeń obszarowych — zasypcie ich grupą tanich jednostek lub dojedźcie kawalerią. |
| **6. Berserkerzy i Kamikaze** *(od 18:00 — P5)* | **Szturmowcy i Saperzy:** Szybcy (`1.40–1.50`), wysoki atak wręcz / wybuch obszarowy `2,4`. | Posiadają **0 pancerza przeciw strzałom** — wycinajcie ich łucznikami i kusznikami zanim dobiegną. |

---

## 5. Cztery Questy poboczne i Sześć Settlementów Hordy

1. **`Q1 - Karawanseraj (Mur Handlowy, +30 Pop, +20% Eko)` `(154, 190)`:** Buduje ciągły Mur Obronny z 6 Basztami wzdłuż dolnej krawędzi mapy (`x=105..199, y=184`), stawia 2 Targowiska w rogu `(193, 193)`, daje **+30 Limit Populacji na stałe** (`230 pop`), **+20% szybszą pracę Wieśniaków**, 4 szybkie Wozy Handlowe i +500 Złota.
2. **`Q2 - Klif Artylerii (+2 Zasiegu, +4 Ataku, Szybkosc)` `(28, 32)`:** Darmowa Balistyka, Chemia, Inżynierowie Oblężniczy i Thumb Ring, **+2 Zasięgu i +4 Ataku** dla strzelców oraz **+12% prędkości i +4 Ataku** dla jazdy.
3. **`Q3 - Skarbiec (+20 Pop i Duzy Staly Dochod)` `(142, 118)`:** **+20 Limit Populacji na stałe** (`250 pop`) oraz stały dochód co minutę: **+250 Żywności, +250 Drewna, +200 Złota i +40 Kamienia co 60s**.
4. **`Q4 - Krwawy Oltarz (+30% HP Armii i +40% Produkcji)` `(105, 20)`:** **+30% Max HP i +2/+2 Pancerza** dla wojsk graczy, **+40% szybsza produkcja wojska** oraz obniżenie HP Arcymagów do 140 HP.

* **Sześć Settlementów (`G1 Polnocny`, `G1 Wschodni`, `G2 Akademia`, `G2 Klasztor`, `G3 Cytadela Pln.`, `G3 Cytadela Wsch.`):** Zburzenie każdego z nich wyłącza jego jednostki z kolejnych fal i daje po +600 Złota/Żywności, a zniszczenie wszystkich 6 kończy grę zwycięstwem.