# Scenariusz 3: Kroniki Rubieży — Horda i Ekspedycje (v3 — 4P Co-op RPG/RTS)

**Plik scenariusza:** `Kroniki_Rubiezy_Horda_Coop.aoe2scenario`  
**Typ rozgrywki:** Obrona przed 12 rosnącymi falami zmutowanej Hordy + Eksploracja, 4 Questy i niszczenie 6 Settlementów (Grades 1–3)  
**Rozmiar mapy:** 200×200 (Olbrzymia)  
**Wymagane mody zewnętrzne:** Brak (wszystkie 6 klas zmutowanych jednostek, lista zadań UI oraz lokalne aury są wbudowane w plik scenariusza)

---

## 1. Opis rozgrywki i układ Twierdzy

Wszyscy 4 gracze startują na **równych, symetrycznych warunkach** (500 żywności, 600 drewna, 400 złota, 300 kamienia, 200 limitu populacji) wewnątrz rozległej Twierdzy Sojuszu w południowo-zachodniej części mapy:
* Bazy są szeroko rozstawione (38–45 kratek odstępu między Town Center), co daje dużo miejsca na rozbudowę gospodarki.
* Każdy gracz posiada **2 własne lasy bezpośrednio przy TC**, a na zapleczu Twierdzy ciągnie się **Puszcza Zaplecza**, dzięki czemu drewno nie kończy się w późnej fazie gry.
* Twierdza ma **3 wejścia**: Bramę Północną `(48, 100)`, Bramę Centralną `(102, 114)` oraz Bramę Wschodnią `(104, 162)`. Wewnątrz stoi **Cud Sojuszu** `(54, 146)`, którego utrata oznacza porażkę.

### Rytm rozgrywki i czytelność w trakcie gry
* **Stała lista Zadań i Nagród w interfejsie gry (Objectives):** W prawym górnym rogu ekranu przez cały mecz wyświetlana jest lista wszystkich 4 Questów (wraz z nagrodami) oraz 6 Settlementów. Ukończone zadania są automatycznie przekreślane.
* **Podpisane budynki i pełna widoczność od 0:00:** Wszystkie budynki Questów, 6 Settlementów oraz przedpola bram są **odkryte od 1. sekundy gry**. Po kliknięciu na budynek Questu lub Zamek wroga jego nazwa w dolnym panelu informuje, jaki bonus daje jego zburzenie.
* **Harmonogram 12 rosnących fal:** Pierwsza fala uderza w **10:00**, a kolejne **co 3 minuty** (łącznie 12 coraz silniejszych fal aż do 43:00, po czym uruchamia się pętla *Endless*). Po każdym ataku na czacie ogłaszane jest **2,5-minutowe Okno Ekspedycyjne** na wyjście w pole.

---

## 2. Bestiariusz Hordy — 6 klas zmodyfikowanych jednostek wroga

| Jednostka specjalna | Frakcja / Pochodzenie | Zmodyfikowane statystyki i zachowanie | Jak kontrować? |
| :--- | :--- | :--- | :--- |
| **1. Kolosy Oblężnicze** *(Onagery Oblężnicze)* | **P6 (Fioletowy)** — Akademia Artylerii (G2) | **22 zasięgu**, **850 HP**, **+90 ataku**, **promień wybuchu 2,8 kratki**, ale strzelają rzadko (**co 10 s**) i jadą bardzo wolno (`0.4`). | Obserwować lecące pociski i rozpraszać szyk (chwila nieuwagi kasuje pół armii), po czym wjechać jazdą w ich martwą strefę. |
| **2. Fanatycy Kamikaze i Płonące Wielbłądy** *(Petardy / Wielbłądy)* | **P5 (Turkusowy)** — Obozy Przednie (G1) | **+65% prędkości ruchu** (szybsze od rycerzy!), **220 HP**, **promień wybuchu 2,5 kratki**, **+120 obrażeń**. | Wybiegają przed falę prosto w mury i zgrupowania wojsk. Trzeba je zestrzelić na podejściu lub podstawić pojedynczą jednostkę, by wybuchły przed szeregiem. |
| **3. Berserkerzy Szturmowi** *(Elitarni Berserkerzy)* | **P5 (Turkusowy)** — Obóz Północny (G1) | **Prędkość `1.45`**, **320 HP**, **+18 ataku wręcz**, ale **0 pancerza przeciw strzałom**. | Nie dopuszczać do zwarcia — rozstrzeliwać kusznikami/łucznikami zanim dobiegną do piechoty i machin. |
| **4. Snajperzy** *(Elitarni Janczarzy)* | **P6 (Fioletowy)** — Akademia Artylerii (G2) | **20 zasięgu** (więcej niż Zamki), **+110 ataku**, strzał co **6,0 s**, **140 HP**. | Szybki wypad lekką jazdą lub rycerzami na tyły kolumny wroga. |
| **5. Arcymagowie Tarczy i Szamani Krwi** *(Imamowie i Misjonarze)* | **P7 (Szary)** — Klasztor Arcymagów (G2) | **550 HP (Mag) / 280 HP (Szaman)**. **Lokalna Aura Nieśmiertelności (tylko 25 kratek wokół Bramy Centralnej):** daje wojskom P7 **+60/60 Pancerza** (otrzymują tylko 1 dmg) i leczy **+100 HP co 2s** w tej strefie. | Magowie są **zawsze widoczni na mapie** i oznaczani flarą. Wyfokusować i zabić Imamów przed bramą — ich śmierć natychmiast zdejmuje barierę. |
| **6. Tytani Hordy** *(Elitarne Słonie Bojowe)* | **P8 (Pomarańczowy)** — Cytadele Hordy (G3) | **1400 HP**, **+25 ataku wręcz**, **szerokie tratowanie obszarowe (1,5 kratki)**. | Masować halabardników lub mnichów (konwersja). |

---

## 3. Cztery Questy w otwartym polu (Niszczalne budynki wroga)

W przeciwieństwie do Monumentów, cele Questów to **zwykłe budynki wroga, które trzeba fizycznie zburzyć do 0 HP**:

1. **[Q1] Karawanseraj Południowy — Wrogie Targowisko `(154, 182)`:**
   * **Wymagania:** Szybki wypad na południe.
   * **Nagroda dla każdego gracza:** **+500 Złota**, **3 darmowe Wozy Handlowe** oraz postawienie 2 sojuszniczych Targowisk na krańcu mapy `(155, 190)` pod bezpieczny handel.
2. **[Q2] Klif Artylerii — Wrogie Uniwersytet `(28, 32)`:**
   * **Wymagania:** Dużo micro pod górę przeciwko Snajperom (20 zasięgu) i Kolosom Oblężniczym (22 zasięgu).
   * **Nagroda dla każdego gracza:** Darmowe zbadanie **Balistyki, Chemii, Inżynierów Oblężniczych i Thumb Ring** oraz stały bonus **+4 Ataku i +12% prędkości ruchu** dla jazdy i strzelców.
3. **[Q3] Skarbiec Krasnoludów — Wrogie Cud za murami `(142, 118)`:**
   * **Wymagania:** Dużo machin oblężniczych (podwójny mur obronny i 4 Baszty).
   * **Nagroda dla każdego gracza:** **+400 Żywności, Drewna i Złota** od ręki ORAZ uruchomienie stałego pasywnego dochodu (**+120 Żywności, +120 Drewna i +100 Złota co minutę** do końca gry).
4. **[Q4] Krwawy Ołtarz — Wrogie Klasztor na dalekiej północy `(105, 20)`:**
   * **Wymagania:** Daleka ekspedycja na północ.
   * **Nagroda dla każdego gracza:** Zmniejsza maksymalne HP wrogich Magów o **80%** i daje Waszym jednostkom **+50 Max HP**.

---

## 4. Sześć Settlementów (Grades 1–3) i mechanika „Furii Hordy”

Zburzenie głównego budynku (Wieży lub Zamku) w danym Settlemencie **trwale wyłącza jego jednostki z kolejnych fal** i daje każdemu graczowi **+500 Złota i +500 Żywności**, **ALE** uruchamia **Furię Hordy** (pozostałe przy życiu obozy otrzymują stały bonus **+30 HP i +2 Ataku** oraz wysyłają natychmiastowy kontratak z Tytanami):

* **Grade 1 (Bliskie):**
  * *Obóz Północny* `(76, 72)` — Wieża Strażnicza (usuwa Berserkerów i Petardy Kamikaze).
  * *Obóz Wschodni* `(132, 152)` — Wieża Strażnicza (usuwa Płonące Wielbłądy i Huskarlów).
* **Grade 2 (Średnie — Specjaliści):**
  * *Akademia Artylerii (P6)* `(68, 34)` — Zamek (**trwale usuwa Snajperów i Kolosy Oblężnicze!**).
  * *Klasztor Arcymagów (P7)* `(148, 72)` — Zamek (**trwale usuwa Magów Tarczy i Szamanów!**).
* **Grade 3 (Dalekie Cytadele Endgame):**
  * *Cytadela Północna* `(142, 24)` oraz *Cytadela Wschodnia* `(176, 56)` — Główne Zamki (usuwają Tytanów Słoniowych i dają zwycięstwo po wycięciu wszystkich 6 Settlementów).

---

## 5. Warunki uruchomienia w lobby

* **Tryb gry:** *Custom Scenario* -> `Kroniki_Rubiezy_Horda_Coop`.
* **Sloty 1–4 (Ludzie — Drużyna 1):** Kolory 1 (Niebieski), 2 (Czerwony), 3 (Zielony), 4 (Żółty) — start w pełni symetryczny.
* **Sloty 5–8 (AI Extreme — Drużyna 2):**
  * **Slot 5 (Turkusowy):** Goci lub Wikingowie (Obozy Grade 1 — Berserkerzy i Kamikaze).
  * **Slot 6 (Fioletowy):** Turcy (Grade 2 — Snajperzy i Kolosy Oblężnicze).
  * **Slot 7 (Szary):** Saraceni lub Hiszpanie (Grade 2 — Arcymagowie i Szamani).
  * **Slot 8 (Pomarańczowy):** Persowie lub Khmerzy (Grade 3 — Tytani Słoniowi i Paladyni).
* **Widoczność mapy:** **Odkryta (Explored)**.
* **Zablokuj drużyny (Lock Teams):** **Wyłączone**.