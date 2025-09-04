# Python Backtesting Engine dla Strategii Inwestycyjnych

## 1. Opis Projektu

Aplikacja ta jest silnikiem do historycznego testowania (backtestingu) strategii inwestycyjnych na rynku akcji oraz funduszy ETF. Głównym celem projektu jest analiza i porównanie wyników **strategii Momentum** przy różnych częstotliwościach rebalansowania portfela (codziennie, tygodniowo, miesięcznie).

Aplikacja pobiera dane historyczne, symuluje działanie strategii, a następnie generuje interaktywne raporty w formacie HTML, które pozwalają na szczegółową analizę wyników w porównaniu do benchmarku rynkowego (S&P 500).

### Kluczowe Funkcjonalności

*   **Pobieranie Danych z yfinance**: Automatyczne pobieranie aktualnych danych historycznych z Yahoo! Finance.
*   **Automatyczna Konwersja Walut**: Silnik automatycznie wykrywa aktywa notowane w EUR (zakończone na `.DE`) i przelicza ich ceny na USD, co pozwala na spójną analizę portfela.
*   **Strategia Momentum**: Zaimplementowana strategia cyklicznie analizuje zwroty z grupy aktywów i inwestuje cały kapitał w ten, który w ostatnim okresie (tzw. `lookback period`) wygenerował najwyższą stopę zwrotu.
*   **Testowanie Wariantów Strategii**: Skrypt `main.py` jest skonfigurowany do jednoczesnego testowania strategii Momentum z różnymi interwałami rebalansowania (dziennym, tygodniowym, miesięcznym), co ułatwia porównanie ich efektywności.
*   **Zaawansowana Wizualizacja Wyników**: Zamiast statycznych obrazów, aplikacja generuje **interaktywne wykresy HTML** przy użyciu biblioteki Plotly. Wykresy te umożliwiają m.in.:
    *   Dynamiczne przeglądanie wartości portfela w czasie.
    *   Porównanie z benchmarkiem (S&P 500).
    *   Analizę poziomu gotówki w portfelu.
    *   Wizualizację punktów kupna i sprzedaży.
    *   Podświetlenie okresów, w których posiadane były konkretne aktywa.

## 2. Architektura Aplikacji

Aplikacja jest zbudowana w sposób modułowy, aby zapewnić elastyczność i łatwość w analizie. Główne komponenty to:

*   **Dostawca Danych (`data_provider.py`)**: Odpowiada za pobieranie i przygotowanie danych, w tym za konwersję walut.
*   **Portfel (`portfolio.py`)**: Zarządza stanem gotówki, listą posiadanych aktywów oraz historią transakcji.
*   **Strategia (`strategy.py`)**: Definiuje logikę decyzyjną. Aktualnie zawiera implementację `MomentumStrategy`, a także `BuyAndHoldStrategy` i `MonthlyInvestmentStrategy` (nieużywane w głównej symulacji).
*   **Silnik Backtestingu (`engine.py`)**: Orkiestruje proces symulacji, iterując dzień po dniu i wykonując zlecenia strategii.
*   **Analiza i Wizualizacja (`analysis.py`)**: Generuje interaktywne raporty w formacie HTML na podstawie wyników symulacji.
*   **Główny Plik Uruchomieniowy (`main.py`)**: Konfiguruje i uruchamia całą symulację. To tutaj zdefiniowane są parametry takie jak data, kapitał, tickery i benchmark.

## 3. Użycie

Aby uruchomić aplikację, należy najpierw zainstalować wymagane zależności:

```bash
pip install -r requirements.txt
```

Następnie, można uruchomić główny skrypt symulacji:

```bash
python main.py
```

Po zakończeniu symulacji, w głównym katalogu projektu zostaną wygenerowane pliki `.html` dla każdego przetestowanego wariantu strategii (np. `performance_Momentum_12M_Daily.html`, `performance_Momentum_12M_Weekly.html` itd.). Pliki te można otworzyć w dowolnej przeglądarce internetowej, aby interaktywnie analizować wyniki.
