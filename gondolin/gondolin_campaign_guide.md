# Silmarillion: Upadek Gondolinu i Odwrót przez Cristhorn
### 4-Osobowy Kooperacyjny Scenariusz Taktyczno-Przygodowy RPG do Age of Empires II: Definitive Edition

---

## 1. Wstęp i Założenia Rozgrywki

Scenariusz wiernie adaptuje opowieść o upadku Ukrytego Królestwa Gondolinu oraz dramatycznym odwrocie uchodźców przez góry Echoriath (*Niedokończone Opowieści*, *Księga Zaginionych Opowieści*, *Silmarillion*). 

W odróżnieniu od klasycznych scenariuszy typu *Tower Defence* lub map ekonomicznych:
* **Brak budowy bazy i ekonomii:** Gracze nie posiadają wieśniaków ani nie stawiają budynków produkcyjnych.
* **Rozproszony start w płonącym mieście:** Gracze zaczynają w czterech różnych dzielnicach i muszą współpracować na odległość (np. otwieranie śluz akweduktu w jednej części miasta gasi pożary i osłabia machiny w innej), aby przebić się do siebie nawzajem.
* **Rozgrywka sterowana wydarzeniami (*Event-Driven*):** Brak sztywnych zegarów odliczających fale. Tempo natarcia zależy od zniszczenia pancernych machin Morgotha (*Żelaznych Smoków*), ratowania mieszkańców i wyboru ścieżek odwrotu.
* **Wybory dróg i nieliniowość:** Gracze stają przed dylematami strategicznymi (ocalenie wybranych enklaw miejskich; wybór między podziemnym tunelem a mglistą równiną w Fazie II).

---

## 2. Sugerowane Cywilizacje (Dla Graczy i AI)

### Czy wybór cywilizacji ma znaczenie w scenariuszu RPG?
W scenariuszu większość parametrów (statystyki bohaterów, elitarne modyfikatory Noldorów, pancerze, technologie kowalskie i zasięg) jest **definiowana bezpośrednio przez skrypty triggerów w silniku Genie**. Jednakże pasywne bonusy cywilizacyjne oraz unikalny styl architektoniczny nadal działają w grze! 

Wybór sugerowanych poniżej cywilizacji gwarantuje optymalną synergię z przydzielonymi jednostkami, właściwy klimat wizualny oraz zgodność z mechaniką:

### Drużyna Noldorów (Gracze 1–4)

| Gracz | Kolor | Domy i Dowódcy | Sugerowana Cywilizacja | Dlaczego ta cywilizacja? |
| :--- | :--- | :--- | :--- | :--- |
| **P1** | **Niebieski** | **Dom Skrzydła (Tuor) & Dom Młota Gniewu (Rog)** | **Polacy (Poles)** *lub* **Wikingowie (Vikings)** | P1 dowodzi kowalami Roga walczącymi młotami bojowymi (*Obuch*) oraz topornikami. Polacy dają naturalny klimat i bonusy do piechoty/Obuchów, natomiast Wikingowie zapewniają dodatkowe punkty życia dla piechoty i styl wojowników z wielkimi toporami (*Dramborleg* Tuora). |
| **P2** | **Czerwony** | **Dom Źródła (Ecthelion) & Dom Niebiańskiego Łuku (Egalmoth)** | **Brytyjczycy (Britons)** *lub* **Włosi (Italians)** | P2 skupia się na formacji włóczników i dalekosiężnych łucznikach Noldorów (*Longbowmen*). Brytyjczycy idealnie podbijają zasięg i precyzję łuczników Egalmotha, a Włosi pasują architekturą do białych tarasów i fontann. |
| **P3** | **Zielony** | **Dom Złotego Kwiatu (Glorfindel) & Dom Jaskółki (Duilin)** | **Frankowie (Franks)** *lub* **Madziarzy (Magyars)** | P3 to mobilna szpica armii: szybka gwardia szturmowa Glorfindela, rycerstwo i strzelcy wyborowi. Cywilizacje te zapewniają wysoką żywotność jazdy oraz szybkość manewrową w wąskich przełęczach. |
| **P4** | **Żółty** | **Dom Drzewa (Galdor) & Strażnicy Tajemnej Ścieżki (Idril)** | **Burgundowie (Burgundians)** *lub* **Celtowie (Celts)** | P4 odpowiada za inżynierię, ochronę małego Eärendila i saperów detonujących podkopy. Burgundowie odpowiadają jednostkom gwardii flamandzkiej (*Flemish Militia* Galdora), a Celtowie zapewniają szybszy chód piechoty i odporność machin. |

### Siły Morgotha i Zdrajcy (AI: Gracze 5–8)

| Gracz | Kolor | Rola w Scenariuszu | Sugerowana Cywilizacja | Uzasadnienie klimatyczne |
| :--- | :--- | :--- | :--- | :--- |
| **P5** | **Turkusowy** | **Hordy Orków i Wilków z Angbandu** | **Goci (Goths)** | Niepowstrzymana, bezlitosna masa lekkiej i średniej piechoty szturmującej ulice i wąwozy. |
| **P6** | **Pomarańczowy** | **Żelazne Smoki i Machiny Morgotha** | **Bohemowie (Bohemians)** | Eksperci od machin oblężniczych, ziejących ogniem konstrukcji i pancernych wozów. |
| **P7** | **Szary** | **Balrogowie pod wodzą Gothmoga** | **Drawidowie (Dravidians)** *lub* **Persowie (Persians)** | Jednostki biczowników Urumi (wykorzystane jako model Balrogów z płonącymi biczami) oraz potężny model Savara dla Gothmoga. |
| **P8** | **Fioletowy** | **Dom Kreta (Zdrajcy Maeglina)** | **Teutoni (Teutons)** | Ciężkozbrojni, opancerzeni zdrajcy z kopalń i lochów Maeglina blokujący pałac Tuora i Caragdûr. |

---

## 3. Konfiguracja Lobby i Warunki Uruchomienia w AoE2: DE

Przed uruchomieniem meczu w trybie Wieloosobowym (Multiplayer) lub Jednoosobowym (Skirmish) ustaw parametry dokładnie według poniższej rozpiski:

* **Game Mode (Tryb gry):** `Custom Scenario`
* **Scenario (Plik scenariusza):** `Silmarillion_Upadek_Gondolinu_Coop`
* **Liczba graczy:** `8` (Gracze 1–4 to Ludzie, Gracze 5–8 to Komputer / AI)
* **Drużyny (Teams):**
  * **Team 1:** Gracz 1, Gracz 2, Gracz 3, Gracz 4 *(Noldorowie)*
  * **Team 2:** Gracz 5, Gracz 6, Gracz 7, Gracz 8 *(Angband & Zdrajcy)*
* **Lock Teams (Zablokowane drużyny):** `ON` (Włączone — zapobiega zmianom sojuszy)
* **Teams Together (Drużyny obok siebie):** `ON` (Włączone)
* **Difficulty (Poziom trudności):** `Moderate` lub `Hard` *(Scenariusz posiada własny system adaptacyjny – patrz Sanktuarium Balansu poniżej)*
* **Starting Age (Era startowa):** `Default` (Scenariusz w 0:01 bada automatycznie Imperial Age oraz technologie)
* **Map Visibility (Widoczność mapy):** `Normal` (Domyślna Mgła Wojny — scenariusz stopniowo odsłania sektory poprzez triggery)
* **All Techs (Wszystkie technologie):** `OFF` (Wyłączone)
* **Allow Cheats (Kody):** `OFF` (Wyłączone w rozgrywce rankingowej/fair play)
* **Pop Cap (Limit populacji):** `Default` (Skrypt dodaje każdemu graczowi +150 do limitu)

---

## 4. Unikalne Mechaniki Rozgrywki

### A. System 3 Pieczęci Rezerwy Turgona (Ochrona przed nagłym Defeat)
W scenariuszu śmierć kluczowego bohatera nie kończy gry natychmiastową porażką:
* Drużyna rozpoczyna z **3 wspólnymi Pieczęciami Rezerwy**. Stan pieczęci jest na bieżąco widoczny w panelu zadań (*Objectives*).
* Gdy którykolwiek z głównych lordów (Tuor, Ecthelion, Glorfindel, Idril) lub mały Eärendil polegnie:
  1. Zużywana jest **1 Pieczęć Rezerwy** (drużyna traci 500 Punktów Chwały).
  2. Poległy bohater **odradza się w pełnym zdrowiu na aktualnym Punkcie Zbornym** (Checkpoincie danej fazy) w asyście 6-osobowego oddziału Gwardii Ratunkowej.
* **Warunek Porażki:** Dopiero utrata bohatera przy **0/3 Pieczęciach** skutkuje ostateczną klęską Gondolinu.
* *Wyjątek fabularny:* Poświęcenie Glorfindela w pojedynku z Balrogiem nad przepaścią w Fazie III **nie zużywa** Pieczęci Rezerwy (jest to kanoniczne zwycięstwo fabularne!).

### B. Sanktuarium Balansu (-2 do +2)
W lewym górnym rogu mapy `(12, 228)` znajduje się odizolowana komnata z Królem Gracza 1:
* **Wejście na pole północne (+Trudniej):** Zwiększa punkty życia wrogów o +20 HP i atak o +2, nagradzając graczy premią `+1000 Punktów Chwały`.
* **Wejście na pole południowe (-Łatwiej):** Obniża punkty życia wrogów o 15% kosztem `-500 Punktów Chwały`.
* Po dokonaniu wyboru komnata jest automatycznie oczyszczana, a Król powraca na środek po 2-sekundowym resecie.

### C. Zrównoważone Uzupełnienia (Soft-Cap Reinforcements)
Na początku Fazy II oraz Fazy III system analizuje stan armii każdego gracza z osobna:
* **Poczet krytycznie uszkodzony (< 15 jednostek):** Gracz otrzymuje *Pakiet Ratunkowy* (+14 elitarnych jednostek), przywracający go do pełnej gotowości bojowej.
* **Stan normalny (15–28 jednostek):** Gracz otrzymuje standardowe posiłki (+7 jednostek).
* **Stan dominacji (> 28 jednostek):** Zamiast zapełniać wąskie górskie trakty zbędnym tłumem, gracz otrzymuje `+150 Punktów Chwały` oraz trwałe `+15 HP` dla swojego wojska.

### D. Żelazne Smoki Morgotha (P6) jako Mobilne Bunkry
W alejach Gondolinu toczą się pancerne machiny ziejące ogniem (`P6`).
* Dopóki w danym odcinku alei żyje Żelazny Smok, co 32 sekundy wysypuje się z niego desant świeżych oddziałów Orków (`P5`).
* Zniszczenie Smoka (najlepiej za pomocą młotów i toporów Gracza 1) natychmiast zatrzymuje dopływ posiłków w danej ulicy.

---

## 5. Przewodnik Krok po Kroku po Fazach Gry

### FAZA I: Noc Tarnin Austa (Płonące Miasto)
1. **Kooperacja Zdalna P1 + P4 (Caragdûr):** Gracz 4 (Idril) broni swojego dworu przed zdradzieckim Maeglinem (`P8`), który zablokował bramy i próbuje zrzucić małego Eärendila z urwiska Caragdûr. Gracz 1 (Tuor) przebija się przez zewnętrzną barykadę od południa. Wspólne zabicie Maeglina daje `+2 Ataku` dla P1 i P4 oraz `+300 Chwały`.
2. **Kooperacja Zdalna P2 $\rightarrow$ P3 (Wielki Akwedukt):** Północna dzielnica Gracza 3 stoi w płomieniach zadających obrażenia co 4 sekundy. Gracz 2 (Ecthelion) musi szturmem zdobyć Śluzy Akweduktu na wschodzie – ich przejęcie gasi ogień u P3, zalewa północną fosę i zadaje potężne obrażenia Żelaznym Smokom Morgotha.
3. **Zadania Indywidualne:**
   * **P3 (Wieża ze Śniegu):** Wprowadzenie strzelców Duilina na szczyt północnej baszty odsłania położenie enklaw miejskich i daje łucznikom drużyny `+1 Zasięgu`.
   * **P4 (Glingal i Belthil):** Zabezpieczenie pędów Świętych Drzew na wzgórzu Amon Gwareth trwale zwiększa punkty życia wszystkich Bohaterów o `+60 HP`.
4. **Dylemat Trzech Enklaw (Ratunek przed odwrotem):**
   * *Kuźnie Roga (Zachód):* Eskorta 3 wozów z mithrilem na wzgórze królewskie daje całej drużynie `+3 Ataku` oraz `+2/+2 Pancerza`.
   * *Wielki Targ (Wschód):* Odsiecz dla Penloda zasila drużynę oddziałem `+12` halabardników i długodystansowych łuczników.
   * *Dwór Salganta (Południe):* Przełamanie tchórzostwa Salganta uwalnia wojowników Domu Harfy (szybka jazda i mnisi leczący sojuszników).
5. **Starcie z Gothmogiem:** Na placu przed Wieżą Turgona uderza Władca Balrogów. Zwabienie go w wodę Fontanny Królewskiej aktywuje aurę osłabiającą jego pancerz i leczącą Noldorów.

### FAZA II: Odwrót przez Tumladen (Wybór Drogi)
Po upadku Gothmoga Wieża Turgona wali się, tarasując drogę pościgowi z miasta. Gracze stają przed wyborem szlaku przez Równinę Tumladen ku Górom Okrężnym (drużyna może iść razem lub podzielić się na dwie grupy):
* **Szlak Dolny (Tajemna Ścieżka Idril & Koryto Suchej Rzeki):** P4 wysadza wejście do tunelu za plecami armii. Marsz wąskim korytem rzeki pozwala P4 zdetonować 2 podziemne komory minowe znajdujące się bezpośrednio pod obozami wilków na powierzchni!
* **Szlak Górny (Misty Tumladen):** Gracze idący górą likwidują wieże strzeleckie Orków na krawędzi klifów, osłaniając uchodźców idących dnem rzeki. Dodatkowo Gracz 1 może zniszczyć Polowy Ołtarz Balrogów, co trwale osłabia demony w Fazie III o 20% HP.
* Obie ścieżki spotykają się u stóp wąwozu Orfalch Echor `(185, 85)`.

### FAZA III: Wąwóz Siedmiu Bram i Cirith Thoronath
1. **Kołowroty Bram i Lawiny Skalne:** Przejście dnem wąwozu jest zablokowane przez potężne bramy. Gracze P3 i P4 mogą wejść wąskimi ścieżkami na Górną Grań i zniszczyć kołowroty Bramy Brązowej, Srebrnej i Stalowej – każda zniszczona machina strąca lawinę kamieni, która miażdży oddziały Orków czekające w dole.
2. **Pojedynek na Krawędzi Przepaści (Cirith Thoronath):** W najwęższym przesmyku nad otchłanią drogę zagradza Balrog. Glorfindel (P3) staje do pojedynku na Skalnym Występie.
3. **Przybycie Orłów Thorondora:** Po 30 sekundach heroicznej walki nad przełęcz nadlatują Wielkie Orły. Uderzenie z powietrza strąca Balroga i niedobitki Angbandu w przepaść, a do ocalałych dołącza grywalna Straż Przednia Thorondora.
4. **Zwycięstwo:** Wprowadzenie ocalałych do Doliny Sirionu `(224, 224)` kończy kampanię zwycięstwem Noldorów! Końcowy stan Złota Gracza 1 stanowi Wasz Wynik Chwały (High Score).