# Scenariusz 2: Operacja: Żelazny Krąg (Taktyczny 4P Co-op)

**Plik scenariusza:** `Operacja_Zelazny_Krag_Coop.aoe2scenario`  
**Typ rozgrywki:** Kooperacja dla 4 graczy vs 4 wyspecjalizowane frakcje AI (Triggery + Mutatory)  
**Rozmiar mapy:** 180×180  

---

## 1. Opis rozgrywki z perspektywy gracza

Scenariusz eliminuje największą wadę potyczek z komputerem (przewidywalność i wysyłanie jednostek pojedynczo), zastępując je **mechanikami rajdowymi**. Czterech graczy o różnym ELO tworzy symbiotyczny organizm, w którym skrzydła ofensywne nie są w stanie utrzymać armii bez finansowania ze strony obrońców doliny, a obrońcy doliny zostaną zmiażdżeni przez rosnące statystyki wroga, jeśli grupa szturmowa nie zniszczy zewnętrznych Bastionów.

### Asymetryczny podział ról w drużynie (Gracze 1–4)
1. **Gracz 1 (1600–1700 ELO) — Korpus Ekspedycyjny (Północny-Zachód: 30, 52):**
   * Startuje blisko terytorium wroga z gotowymi Koszarami, Stajnią, Kuźnią i Targowiskiem.
   * Posiada **250 limitu populacji** (+50) oraz **+35% szybszą produkcję jednostek** w Koszarach, Stajniach i Strzelnicach.
   * **Ograniczenie:** W bazie ma tylko **4 kafelki złota** (brak kamienia!). Po 15. minucie jest całkowicie uzależniony od trybutów złota/kamienia i handlu z Graczami 3 i 4.
2. **Gracz 2 (1300–1400 ELO) — Dowódca Flanki Zachodniej (Zachód: 28, 98):**
   * Zbalansowana baza z Koszarami na starcie, osłaniająca podejście pod Przełęcz Zachodnią. Wspiera Gracza 1 w niszczeniu Bastionów oraz reaguje na rajdy dywersyjne.
3. **Gracz 3 (1100–1200 ELO — 62, 152) i Gracz 4 (1000–1100 ELO — 118, 152) — Strażnicy Przełęczy i Kwatermistrzowie:**
   * Startują wewnątrz bezpiecznej od południa **Doliny Południowej**, oddzielonej od wroga pasmem górskim z dwoma wąskimi wejściami: **Przełęczą Zachodnią (P3)** i **Przełęczą Wschodnią (P4)**.
   * **Zadanie 1 (Obrona):** Ufortyfikować obie przełęcze i obronić **Wielką Kuźnię Imperium (Cud)** w środku doliny `(90, 148)`.
   * **Zadanie 2 (Ekonomia):** Posiadają w dolinie gigantyczne złoża surowców (po 20 kafelków złota i 8 kamienia na gracza) oraz Targowiska na starcie. Muszą regularnie finansować armie Graczy 1 i 2.

---

### Mechaniki 4 Frakcji Wroga (Gracze AI 5–8)
Na mapie znajdują się 3 zewnętrzne Bastiony (P5, P6, P7) oraz główny cel misji — **Cytadela Główna (P8)**:

1. **Bastion Północny (P5 — Oblężniczy: 82, 32):**
   * Począwszy od 10. minuty gry, co 5 minut wysyła **dwie zsynchronizowane kolumny oblężnicze** uderzające jednocześnie w Przełęcz Zachodnią (Tarany + Halabardy + Huskarlowie) i Przełęcz Wschodnią (Tarany + Kusznicy + Kawaleria).
2. **Bastion Wschodni (P6 — Kuźnia Wojenna / „Zegar Śmierci”: 150, 88):**
   * Co 4 minuty trwale podnosi maksymalne punkty życia **wszystkich jednostek wroga na mapie o +35 HP**. Im dłużej stoi Zamek w Bastionie P6, tym trudniejsze do zabicia stają się fale wroga.
3. **Bastion Centralny (P7 — Obóz Dywersyjny: 88, 84):**
   * Co 4,5 minuty organizuje rajdy dywersyjne (Lekka Kawaleria + Kawalerzyści + Petardy) na zaplecze Gracza 2 oraz szlak handlowy w Dolinie. Na **35 sekund przed uderzeniem** wywiad ostrzega drużynę na czacie.
4. **Cytadela Główna (P8 — Boss: 146, 30):**
   * Na starcie jej Zamki są chronione przez **Tarczę Imperialną (+4500 HP)**.
   * Zniszczenie każdego z zewnętrznych Bastionów (P5, P6, P7) trwale wyłącza jego mechanikę, odejmuje **-1500 HP** z Tarczy Cytadeli P8 i daje każdemu z 4 graczy łup (**+600 złota, +600 żywności, +250 kamienia**).

> **UWAGA — PROTOKÓŁ ODWETOWY:** W sekundzie zniszczenia dowolnego Zamku w Bastionach P5, P6 lub P7, Cytadela P8 natychmiast wysyła ciężki kontratak (Paladyni + Onagery + Halabardnicy) na obie przełęcze Graczy 3 i 4. **Gracze 1 i 2 muszą potwierdzić na czacie głosowym gotowość obrońców przed dobiciem Zamku!**

---

## 2. Warunki uruchomienia w lobby (Konfiguracja)

W menu gry wybierz: **Multiplayer -> Host Game -> Game Mode: Custom Scenario -> `Operacja_Zelazny_Krag_Coop`**.

### Przypisanie slotów (Gracze 1–4 = Ludzie, Gracze 5–8 = AI)

| Slot / Kolor | Typ gracza | Rola w scenariuszu | Drużyna | Rekomendowana cywilizacja |
| :--- | :--- | :--- | :--- | :--- |
| **1 (Niebieski)** | **Człowiek (1650 ELO)** | Korpus Ekspedycyjny (250 pop, brak złota) | Drużyna 1 | Frankowie, Litwini, Węgrzy, Persowie |
| **2 (Czerwony)** | **Człowiek (1350 ELO)** | Dowódca Szpicy Zachodniej | Drużyna 1 | Celtowie, Czechowie, Mongołowie, Słowianie |
| **3 (Zielony)** | **Człowiek (1150 ELO)** | Strażnik Zachodniej Przełęczy + Bankier | Drużyna 1 | Teutoni, Bizancjum, Brytowie, Koreańczycy |
| **4 (Żółty)** | **Człowiek (1050 ELO)** | Strażnik Wschodniej Przełęczy + Bankier | Drużyna 1 | Hiszpanie (bonus do handlu!), Gruzini, Inka |
| **5 (Turkusowy)** | **AI (Extreme)** | Bastion Północny (Kolumny Oblężnicze) | Drużyna 2 | Goci lub Celtowie |
| **6 (Fioletowy)** | **AI (Extreme)** | Bastion Wschodni (Mutator +35 HP) | Drużyna 2 | Teutoni lub Słowianie |
| **7 (Szary)** | **AI (Extreme)** | Bastion Centralny (Rajdy i Petardy) | Drużyna 2 | Węgrzy, Tatarzy lub Mongołowie |
| **8 (Pomarańczowy)**| **AI (Extreme)** | Cytadela Główna (Boss) | Drużyna 2 | Persowie lub Frankowie |

### Pozostałe ustawienia lobby
* **Widoczność mapy:** **Odkryta (Explored)** — pozwala od razu zaplanować obronę przełęczy i trasę marszu na Bastiony.
* **Limit populacji:** **200** (Gracz 1 otrzyma automatycznie +50 z triggera).
* **Zablokuj drużyny (Lock Teams):** **Wyłączone**.
* **Wskazówka cywilizacyjna:** Jeśli Gracz 3 lub 4 wybierze **Hiszpanów**, ich bonus drużynowy (+25% złota z handlu) znacząco ułatwi finansowanie armii Gracza 1 w Imperial Age.