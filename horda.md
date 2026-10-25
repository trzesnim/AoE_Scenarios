# Scenariusz 3: Kroniki Rubieży — Horda i Ekspedycje (v6.1 — 4P Co-op RPG/RTS)

**Plik scenariusza:** `Kroniki_Rubiezy_Horda_Coop.aoe2scenario`  
**Typ rozgrywki:** Obrona przed 14 falami Hordy + Sanktuarium Balansu + 4 Questy poboczne i niszczenie 6 Settlementów (Grades 1–3)  
**Horyzont czasowy partii:** 60–90 minut  
**Rozmiar mapy:** 200×200 (Olbrzymia)  

---

## 1. Sanktuarium Balansu — Zmiana trudności na żywo w trakcie meczu `(6, 193)`

W lewym dolnym narożniku mapy `(6, 193)` znajduje się odizolowana skalnymi klifami komnata, w której stoi nieśmiertelny **Inżynier Balansu (Król Gracza 1)**:

* **Ruch Królem w GÓRĘ `(6, 189)` (Pochodnie Północne):** Zwiększa poziom trudności o **+1 stopień**.
* **Ruch Królem w DÓŁ `(6, 197)` (Pochodnie Południowe):** Zmniejsza poziom trudności o **-1 stopień**.
* **Automatyczny powrót i logowanie:** Po wejściu na flagę cała komnata jest czyszczona, a Król pojawia się z powrotem na środku `(6, 193)`. Na czacie wyświetla się wpis `[LOG BALANSU]` z aktualnym poziomem trudności.
* **5 poziomów trudności:**
  * **Poziom `-2` (Bardzo Łatwy):** **-40% liczebności kolejnych fal** oraz **-28% HP** wroga.
  * **Poziom `-1` (Łatwy):** **-20% liczebności kolejnych fal** oraz **-15% HP** wroga.
  * **Poziom `0` (Domyślny):** **100% bazowej liczebności fal** i bazowe statystyki.
  * **Poziom `+1` (Trudny):** **+25% liczebności kolejnych fal** oraz **+15 HP i +2 Ataku** wroga.
  * **Poziom `+2` (Ekstremalny):** **+50% liczebności kolejnych fal** oraz **+30 HP i +4 Ataku** wroga.

---

## 2. Opis rozgrywki i układ Twierdzy Sojuszu

Wszyscy 4 gracze startują na równych warunkach (500 żywności, 600 drewna, 400 złota, 300 kamienia, 6 wieśniaków i 1 skaut) wewnątrz Twierdzy Sojuszu w południowo-zachodniej części mapy:

* **Wspólna wizja i stały podgląd celów (`LOS = 4`):** Wszyscy gracze mają od startu zbadaną **Kartografię**. Nad środkiem każdego budynku Questu i Settlementu wisi stały odsłaniacz (`4` kratki), dzięki czemu w każdej chwili można kliknąć na budynek zadania i sprawdzić jego opis.
* **Cytadela Sojuszu (Feitoria Gracza 2):** W centrum Twierdzy `(54, 146)` stoi wzmocniona **Feitoria należąca do Gracza 2** (+3000 HP oraz +20 limitu populacji dla Gracza 2). Jej utrata oznacza porażkę drużyny.
* **Trzy przełęcze bojowe + Brama Handlowa:** Brama Północna `(48, 100)`, Centralna `(104, 114)`, Wschodnia `(104, 162)` oraz Południowa Brama Handlowa `(104, 193)` są zamknięte pełną **Wzmocnioną Palisadą (+400 HP)** z **Bramą Palisadową** i **2 Wieżami Strażniczymi**.
* **Działanie Mnichów:** Mnisi graczy (`P1–P4`) działają normalnie (leczą i konwertują zwykłe jednostki wroga). Mnisi komputerowi (`P5–P8`) mają zablokowaną konwersję, natomiast Arcymagowie (`P7`) leczą pobliskie jednostki Hordy obszarowo (+15 HP co 3s).

---

## 3. Harmonogram fal i taktyki specjalne po 45. minucie

* **Fala 1 (8:30):** Szturm Feudalny **bez taranów i bez jednostek specjalnych**.
* **Fala 2 (13:00):** Szturm Feudalny **z pierwszym Taranem i Mangonelem, bez jednostek specjalnych**.
* **Fala 3 (18:00) i kolejne fale (4–14) co 5,5 minuty (330 sekund):** Od 18. minuty stopniowo wchodzą jednostki specjalne.
* **Taktyki specjalne Hordy po 45. minucie (Fale 8–14):**
  * **Co druga fala od 45:00 (Fale 8, 10, 12, 14) — Atak na Trade Line:** Wydzielony korpus z Taranami Oblężniczymi, Paladynami i Konnymi Łucznikami uderza na południowy **Mur i Plac Handlowy (`175, 184`)**.
  * **Co trzecia fala od 45:00 (Fale 9, 12, 14) — Przebicie przez Las (Saperzy Oblężniczy):** Na 15 sekund przed Falą 9 (`50:45`) oraz Falą 12 (`67:15`) wrogie Onagery podjeżdżają pod ścianę lasu (z alarmem i flarą), po czym **wycinają 4-kratkową przesiekę w lesie** — w **Północnym Lesie `(78, 100)`** w 51:00 oraz we **Wschodnim Lesie `(104, 140)`** w 67:30.

---

## 4. Bestiariusz Hordy — 6 wyspecjalizowanych klas jednostek (z Poświatą Bohatera)

| Jednostka specjalna (Od której minuty) | Rola i specjalizacja | Sposób pokonania / Kontra |
| :--- | :--- | :--- |
| **1. Taran-Żółw / Żelazny Słoń** *(od 34:30 — Słoń Bojowy P8)* | **Tank i Niszczyciel Budynków:** **1450 HP**, **+10/+12 pancerza**, **odporny na konwersję**. Ma **+220 obrażeń przeciwko budynkom i murom**, ale zadaje **tylko 3 obrażenia jednostkom**! | W walce z armią jest niegroźny — zignorujcie go, wybijcie resztę fali, a potem otoczcie Halabardnikami (+60 bonus dmg) zanim dojdzie do zamków. |
| **2. Szakale Dywersyjne** *(od 18:00 — Huzarzy P7)* | **Eco-Raiders:** Prędkość **`1.62`**, **+6 pancerza na strzały**, **tylko 2 ataku**. Jadą prosto w linie drwali i farm pod Waszymi 4 Town Center! | Schowajcie chłopów do TC i cofnijcie kilku rycerzy/pikinierów. |
| **3. Arcymag Tarczy** *(od 23:30 — Imam P7)* | **Globalny Support Hordy:** W promieniu 25 kratek przed Bramą Centralną daje **+30/+30 Pancerza i leczy (+15 HP/3s) wszystkie 4 frakcje Hordy (P5–P8)**! | Ma złotą poświatę, flarę co 8s, **240 HP**, **3/4 pancerza** i **regenerację 5 HP/s** — skupcie na nim ogień, by zdjąć tarczę z całej Hordy. |
| **4. Moździerz Oblężniczy** *(od 29:00 — Onager P6)* | **Artyleria Dalekosiężna:** **350 HP**, **21 zasięgu**, **+75 ataku**, promień wybuchu **2,6 kratki**. | **Martwa strefa 6 kratek (`Minimum Range = 6`)** oraz strzał raz na **10 s**. Bezbronny w zwarciu. |
| **5. Snajperzy Imperialni** *(od 18:00 — Janczarzy P6)* | **Egzekutor pojedynczych celów:** **90 HP**, **19 zasięgu**, **+85 ataku** (~107 dmg w jeden cel). | Strzelają co **6,5 s** — zasypcie ich grupą tanich jednostek lub dojedźcie kawalerią. |
| **6. Berserkerzy i Kamikaze** *(od 18:00 — P5)* | **Szturmowcy i Saperzy:** Szybcy (`1.40–1.50`), wysoki atak wręcz / wybuch obszarowy `2,4`. | **0 pancerza przeciw strzałom** — wycinajcie ich łucznikami i kusznikami zanim dobiegną. |

---

## 5. Cztery Questy poboczne i Sześć Settlementów Hordy

1. **`Q1 - Karawanseraj (Mur i Plac Handlowy, +30 Pop, +20% Eko)` `(154, 190)`:**
   * Buduje ciągły Mur Obronny z Basztami wzdłuż dolnej krawędzi mapy oraz otwiera na końcu trasy duży **Plac Handlowy `26×26` kratek (`x=173..198, y=174..198`)**, gdzie przy samej prawej krawędzi mapy każdy z 4 graczy ma wolne miejsce na wybudowanie własnych Targowisk (oprócz 2 darmowych Targowisk na `176, 194` i `182, 194`),
   * Daje **+30 Limit Populacji na stałe** (`230 pop`), **+20% szybszą pracę Wieśniaków**, 4 szybkie Wozy Handlowe i +500 Złota.
2. **`Q2 - Klif Artylerii (+2 Zasiegu, +4 Ataku, Szybkosc)` `(28, 32)`:** Darmowa Balistyka, Chemia, Inżynierowie Oblężniczy i Thumb Ring, **+2 Zasięgu i +4 Ataku** dla strzelców oraz **+12% prędkości i +4 Ataku** dla jazdy.
3. **`Q3 - Skarbiec (+20 Pop i Duzy Staly Dochod)` `(142, 118)`:** **+20 Limit Populacji na stałe** (`250 pop`) oraz stały dochód co minutę: **+250 Żywności, +250 Drewna, +200 Złota i +40 Kamienia co 60s**.
4. **`Q4 - Krwawy Oltarz (+30% HP Armii i +40% Produkcji)` `(105, 20)`:** **+30% Max HP i +2/+2 Pancerza** dla wojsk graczy, **+40% szybsza produkcja wojska** oraz obniżenie HP Arcymagów do 140 HP.

* **Sześć Settlementów (`G1 Polnocny`, `G1 Wschodni`, `G2 Akademia`, `G2 Klasztor`, `G3 Cytadela Pln.`, `G3 Cytadela Wsch.`):** Zburzenie każdego z nich wyłącza jego jednostki z kolejnych fal i daje po +600 Złota/Żywności, a zniszczenie wszystkich 6 kończy grę zwycięstwem.