# Python Backtesting Engine dla Strategii Inwestycyjnych

## 1. Opis Projektu

Aplikacja ta pozwala na historyczne testowanie (backtesting) strategii inwestycyjnych na rynku akcji oraz funduszy ETF. Użytkownik może zdefiniować okres testowania, kapitał początkowy oraz strategię, a aplikacja zasymuluje działanie tej strategii dzień po dniu, generując na koniec raport z wynikami w postaci wykresu porównującego wartość portfela z wybranym indeksem rynkowym (np. S&P 500).

### Kluczowe Funkcjonalności

*   **Elastyczny Okres Testowania**: Możliwość zdefiniowania dowolnego przedziału czasowego dla analizy.
*   **Zarządzanie Portfelem**: Śledzenie gotówki, posiadanych aktywów oraz historii transakcji.
*   **Modułowe Strategie**: Obsługa różnych strategii inwestycyjnych (np. "kup i trzymaj", strategie oparte na średnich kroczących), które mogą być uruchamiane w różnych interwałach (codziennie, tygodniowo, miesięcznie).
*   **Wizualizacja Wyników**: Generowanie wykresu, który porównuje zwrot z portfela z benchmarkiem rynkowym.
*   **Waluta**: Domyślnie operacje będa przeprowadzane w USD, ponieważ jest to standard na międzynarodowych rynkach i większość API dostarcza dane w tej walucie.

## 2. Architektura Aplikacji

Aplikacja zostanie zbudowana w sposób modułowy, aby zapewnić elastyczność i łatwość w rozbudowie. Główne komponenty to:

*   **Dostawca Danych (`data_provider.py`)**: Moduł odpowiedzialny za pobieranie historycznych danych cenowych dla akcji i ETF-ów. Będziemy korzystać z biblioteki `yfinance` do pobierania danych z Yahoo! Finance.

*   **Portfel (`portfolio.py`)**: Klasa reprezentująca portfel inwestycyjny. Będzie zarządzać stanem gotówki, listą posiadanych aktywów (akcji/ETF) oraz rejestrować wszystkie transakcje (kupno/sprzedaż).

*   **Strategia (`strategy.py`)**: Moduł definiujący interfejs dla strategii inwestycyjnych. Stworzymy bazową klasę `Strategy`, z której będą dziedziczyć konkretne implementacje strategii. Umożliwi to łatwe dodawanie nowych algorytmów decyzyjnych.

*   **Silnik Backtestingu (`engine.py`)**: Serce aplikacji. Orkiestruje cały proces symulacji. Iteruje dzień po dniu przez wybrany okres, dostarcza aktualne dane do strategii, wykonuje zlecenia handlowe i zapisuje dzienną wartość portfela.

*   **Analiza i Wizualizacja (`analysis.py`)**: Moduł odpowiedzialny za analizę wyników i generowanie wykresu. Użyjemy bibliotek `pandas` do analizy danych i `matplotlib` do tworzenia wizualizacji.

*   **Główny Plik Uruchomieniowy (`main.py`)**: Skrypt, który łączy wszystkie komponenty. Użytkownik będzie go konfigurował, aby uruchomić symulację z wybranymi parametrami.

## 3. Plan Implementacji (Taski)

Poniżej znajduje się lista zadań, które należy wykonać, aby zbudować aplikację.

### Task 1: Inicjalizacja Projektu i Struktura Katalogów
- [x] Stworzenie głównego folderu projektu.
- [x] Utworzenie pliku `requirements.txt` z listą zależności (`pandas`, `yfinance`, `matplotlib`).
- [x] Stworzenie pustych plików Python dla każdego modułu:
  - `src/data_provider.py`
  - `src/portfolio.py`
  - `src/strategy.py`
  - `src/engine.py`
  - `src/analysis.py`
  - `main.py`

### Task 2: Implementacja Dostawcy Danych (`data_provider.py`)
- [x] Stworzenie funkcji, która pobiera i zwraca historyczne dane dla listy tickerów w zadanym okresie.
- [x] Dodanie mechanizmu cachowania danych (np. do plików CSV), aby unikać wielokrotnego pobierania tych samych danych.

### Task 3: Implementacja Klasy Portfela (`portfolio.py`)
- [x] Stworzenie klasy `Portfolio`.
- [x] Implementacja metod do zarządzania gotówką i aktywami.
- [x] Implementacja metod do wykonywania transakcji (`buy`, `sell`) i zapisywania ich historii.
- [x] Dodanie metody do obliczania całkowitej wartości portfela na dany dzień.

### Task 4: Implementacja Modułu Strategii (`strategy.py`)
- [x] Stworzenie abstrakcyjnej klasy bazowej `Strategy` z metodą `generate_signals`.
- [x] Implementacja prostej, przykładowej strategii, np. `BuyAndHoldStrategy` (kup pierwszego dnia i trzymaj do końca).
- [x] Implementacja strategii, która może działać w różnych interwałach (np. miesięcznej).

### Task 5: Implementacja Silnika Backtestingu (`engine.py`)
- [x] Stworzenie klasy `BacktestingEngine`.
- [x] Implementacja głównej pętli symulacji, która iteruje po dniach.
- [x] Integracja silnika z modułami danych, portfela i strategii.
- [x] Zapisywanie historii wartości portfela każdego dnia.

### Task 6: Implementacja Analizy i Wizualizacji (`analysis.py`)
- [x] Stworzenie funkcji, która przyjmuje historię wartości portfela oraz dane benchmarku.
- [ ] Obliczenie kluczowych metryk (np. zwrot całkowity, zmienność).
- [x] Wygenerowanie i zapisanie wykresu porównującego portfel z benchmarkiem przy użyciu `matplotlib`.

### Task 7: Połączenie Wszystkiego w `main.py`
- [x] Skonfigurowanie parametrów symulacji (daty, kapitał, tickery, benchmark, strategia).
- [x] Inicjalizacja obiektów (Portfolio, Strategy, Engine).
- [x] Uruchomienie silnika backtestingu.
- [x] Wywołanie funkcji generującej raport końcowy.

## 4. Użycie

Aby uruchomić aplikację, należy najpierw zainstalować zależności:
```bash
pip install -r requirements.txt
```

Następnie, skonfigurować i uruchomić główny skrypt:
```bash
python main.py
```
Wynik symulacji (wykres) zostanie zapisany w pliku `performance_chart.png`.
