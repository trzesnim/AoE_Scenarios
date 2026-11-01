# Instrukcje projektowe (AoE2 DE Scenario Generator)
1. Dokumentacja projektu składa się z trzech plików:
   - `SPEC.md`: docelowa specyfikacja scenariusza, mapy i mechanik.
   - `ROADMAP.md`: wieloetapowy plan napraw i ulepszeń (kolejka zadań).
   - `DEBUG_LOG.md`: historia błędów i przetestowanych rozwiązań.
2. Zawsze realizuj tylko JEDEN etap z `ROADMAP.md` w trakcie jednej sesji. Nie łącz naprawy crashy z przebudową mapy.
3. NIGDY nie generuj całych plików `.py` od nowa. Używaj wyłącznie edycji różnicowej (diff) na konkretnych funkcjach.
4. Po każdej modyfikacji kodu uruchom w terminalu skrypt budujący scenariusz oraz testy `pytest validate_scenario.py`.
5. Po ukończeniu zadania oznacz dany punkt jako wykonany `[x]` w `ROADMAP.md` i dopisz krótkie podsumowanie na końcu `DEBUG_LOG.md`.