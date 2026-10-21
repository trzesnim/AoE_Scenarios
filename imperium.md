# Scenariusz 1: Upadek Imperium (Asymetryczne 1v3)

**Plik scenariusza:** `Upadek_Imperium_1v3.aoe2scenario`  
**Typ rozgrywki:** Asymetryczna potyczka 1v3 (Obrona stolicy vs Podbój koalicyjny)  
**Rozmiar mapy:** 160×160  
**Czas partii:** Maksymalnie 45 minut (czas gry)

---

## 1. Opis rozgrywki z perspektywy gracza

Scenariusz odwraca klasyczną potyczkę 1v3. Zamiast otwartej mapy, na której pojedynczy gracz szybko przegrywa przez niższy limit populacji i brak handlu, najsilniejszy gracz wciela się w **Imperatora** broniącego ufortyfikowanej stolicy w centrum mapy, a pozostali trzej gracze prowadzą **Zbuntowane Prowincje** nacierające z narożników mapy.

### Strona 1: Imperator (Gracz 1 — 1600–1700 ELO)
* **Pozycja startowa:** Centralne wzgórze (80, 80) otoczone kamiennym murem z czterema wejściami i narożnymi wieżami strażniczymi.
* **Przewagi na starcie:**
  * **2 Town Center**, **Zamek** oraz 10 wieśniaków już od 1. sekundy gry.
  * **Limit populacji podniesiony do 280** (+80 ponad standardowy limit 200).
  * Wyższy zapas surowców startowych (600 żywności, 600 drewna, 400 złota, 400 kamienia).
  * **Linie wewnętrzne:** Imperator znajduje się w środku mapy, dzięki czemu może szybko przerzucać armię między zagrożonymi bramami, podczas gdy wojska Koalicji mają długą drogę, aby połączyć siły.
* **Mechanika 4 Faktorii Podatkowych:** Poza murami stolicy (na północy, południu, wschodzie i zachodzie) stoją 4 ufortyfikowane Baszty (*Keeps*) z garnizonem pikinierów i kopalniami złota. Dopóki stoją, każda z nich co 60 sekund wpłaca do skarbca Imperatora **+90 złota, +90 żywności i +60 drewna** (łącznie aż **+360 złota, +360 żywności i +240 drewna na minutę**).

### Strona 2: Koalicja Rebeliantów (Gracze 2, 3 i 4 — 1000–1400 ELO)
* **Pozycje startowe:** Trzy oddzielne bazy poza zasięgiem bezpośredniego ataku w pierwszych minutach:
  * **Gracz 2 (Zachód — 24, 80):** Najbliżej głównej zachodniej bramy Imperatora. Posiada dodatkowe złoża złota i kamienia na swoim przedpolu (46, 70–90). Jego rolą jest wiązanie głównej armii Imperatora.
  * **Gracz 3 (Północny-Wschód — 132, 28) i Gracz 4 (Południowy-Wschód — 132, 132):** Bezpieczniejsze flanki wschodnie. Ich pierwszym celem nie jest szturm na stolicę, lecz **zniszczenie zewnętrznych Faktorii Podatkowych Imperatora**.
* **Mechanika odcinania podatków i łupów:** Zburzenie każdej z 4 Baszt Faktorii:
  1. **Trwale wyłącza** jej strumień podatkowy (osłabiając ekonomię Imperatora o 25% za każdą zburzoną Faktorię),
  2. Wypłaca **każdemu z trzech graczy Koalicji** jednorazowy łup w wysokości **+400 złota i +400 żywności**.

### Warunki zwycięstwa
* **Zwycięstwo Imperatora (Gracz 1):** Utrzymać **Imperialny Monument** w samym środku stolicy przez **45 minut** (zegar odlicza czas u góry ekranu) LUB zniszczyć wszystkie bazy Koalicji.
* **Zwycięstwo Koalicji (Gracze 2, 3, 4):** Zburzyć **Imperialny Monument** w centrum stolicy (80, 80) przed upływem 45 minut.

---

## 2. Warunki uruchomienia w lobby (Konfiguracja)

W menu gry wybierz: **Multiplayer -> Host Game -> Game Mode: Custom Scenario -> `Upadek_Imperium_1v3`**.

### Przypisanie slotów i kolorów (Krytyczne!)
W scenariuszach niestandardowych **numer i kolor gracza definiują jego bazę oraz bonusy z triggerów**:

| Slot / Kolor | Rola w scenariuszu | Docelowe ELO | Drużyna | Rekomendowane cywilizacje |
| :--- | :--- | :--- | :--- | :--- |
| **1 (Niebieski)** | **Imperator** (Centrum, 2 TC, 280 pop) | **1600–1700** | Drużyna 1 | Bizancjum, Teutoni, Frankowie, Persowie, Burgundczycy |
| **2 (Czerwony)** | **Front Zachodni** (Główny nacisk) | **1300–1400** | Drużyna 2 | Mongołowie, Hindustańczycy, Węgrzy, Litwini |
| **3 (Zielony)** | **Prowincja Północno-Wschodnia** | **1100–1200** | Drużyna 2 | Brytowie, Celtowie, Polacy, Czechowie |
| **4 (Żółty)** | **Prowincja Południowo-Wschodnia** | **1000–1100** | Drużyna 2 | Frankowie, Hiszpanie, Słowianie, Turcy |

### Pozostałe ustawienia lobby
* **Widoczność mapy (Map Visibility):** **Odkryta (Explored)** — *bardzo ważne*, aby obaj skrzydłowi Koalicji od początku widzieli na minimapie lokalizację 4 Faktorii Podatkowych oraz układ dróg.
* **Limit populacji (Population Limit):** **200** (trigger automatycznie doda +80 limitu wyłącznie Graczowi 1).
* **Zasoby i Era startowa:** **Standard / Domyślne** (zdefiniowane wewnątrz scenariusza).
* **Zablokuj drużyny (Lock Teams):** **Wyłączone (Unchecked)** — pozwala triggerowi `01_Init` poprawnie wymusić dyplomację 1v3.
* **Prędkość gry:** **Normalna (1.7x)**.

---

## 3. Wskazówki taktyczne i lokalizacje na mapie

* **Lokalizacja 4 Faktorii Podatkowych (Baszty Gracza 1):**
  1. *Zachodnia Faktoria:* `(52, 80)` — na drodze między Graczem 2 a stolicą.
  2. *Północna Faktoria:* `(85, 42)` — na szlaku Gracza 3.
  3. *Południowa Faktoria:* `(85, 118)` — na szlaku Gracza 4.
  4. *Wschodnia Faktoria:* `(112, 80)` — pomiędzy bazami Graczy 3 i 4.
* **Dla Imperatora:** Nie oddawaj Faktorii za darmo — każda minuta ich życia to dodatkowe surowce. Wczesny rajd zwiadowcami/rycerzami na bazę Gracza 2 kupi Ci czas na wejście w Imperial Age, ale pamiętaj, że jeśli stracisz wszystkie 4 Faktorie przed 20. minutą, w *late game* zabraknie Ci złota.
* **Dla Koalicji:** Nie rzucajcie się pojedynczo na Zamek w stolicy w 15. minucie. Najpierw w Castle Age (za pomocą taranów lub ulepszonej piechoty/jazdy) zniszczcie 4 Faktorie — zgarniecie po **+1600 złota i +1600 żywności na głowę**, odetniecie Imperatora od pasywnego dochodu i ustawicie bezpieczny handel między bazami P3 i P4 na wschodzie.

### Szybka korekta balansu po meczu (w pliku `generate_1v3_scenario.py`)
* **Jeśli Imperator wygrywa zbyt łatwo:** Zmniejsz `"tax_per_outpost"` z `90` na `65` lub skróć `"p1_bonus_pop"` z `80` na `50`.
* **Jeśli Koalicja zbyt łatwo zalewa stolicę:** Podnieś `"p1_bonus_pop"` do `120` (320 popu) lub skróć `"hold_time_seconds"` z `45 * 60` na `35 * 60` (35 minut).