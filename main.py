# -*- coding: utf-8 -*-
"""
Główny plik uruchomieniowy dla aplikacji do backtestingu.

Ten skrypt konfiguruje i uruchamia symulację wielu strategii inwestycyjnych
i porównuje ich wyniki na jednym wykresie.
"""
import itertools
from src.data_provider import get_data, test_ticker
from src.portfolio import Portfolio
from src.strategy import MomentumStrategy
from src.engine import BacktestingEngine
from src.analysis import plot_performance

def run_simulation():
    """
    Konfiguruje i uruchamia pełną symulację backtestingu dla wielu strategii.
    """
    # =========================================================================
    # --- 1. KONFIGURACJA SYMULACJI ---
    # =========================================================================

    # Parametry ogólne
    INITIAL_CASH = 10000.0
    # Data początkowa musi uwzględniać najdłuższy okres 'lookback' (12 miesięcy)
    START_DATE = '2020-01-01'
    END_DATE = '2025-01-01'

    # Definicja benchmarku
    BENCHMARKS = {'S&P 500': 'SPY'}

    # Tickers dla strategii Momentum
    MOMENTUM_TICKERS = ['SXR8.DE', 'IS3N.DE', 'VVSM.DE', 'XAIX.DE']
    # Warianty strategii do przetestowania
    lookback_options = [12]
    frequency_options = ['daily', 'weekly', 'monthly']
    
    # Generowanie wszystkich kombinacji strategii
    strategy_configs = []
    for lookback, frequency in itertools.product(lookback_options, frequency_options):
        strategy_configs.append({
            'lookback_months': lookback,
            'rebalance_frequency': frequency,
            'name': f"Momentum {lookback}M ({frequency.capitalize()})"
        })

    # =========================================================================
    # --- 2. PRZYGOTOWANIE DANYCH ---
    # =========================================================================
    print("Pobieranie i przygotowywanie danych rynkowych...")
    # Pobierz dane dla wszystkich tickerów strategii i benchmarku
    all_tickers = list(set(MOMENTUM_TICKERS + list(BENCHMARKS.values())))
    market_data = get_data(all_tickers, START_DATE, END_DATE)

    # =========================================================================
    # --- 3. URUCHOMIENIE BACKTESTINGU DLA KAŻDEJ STRATEGII ---
    # =========================================================================
    strategy_results = {}

    for config in strategy_configs:
        print(f"\n--- Uruchamianie symulacji dla: {config['name']} ---")
        
        # Inicjalizacja dla każdej symulacji
        portfolio = Portfolio(initial_cash=INITIAL_CASH)
        strategy = MomentumStrategy(
            tickers=MOMENTUM_TICKERS,
            lookback_months=config['lookback_months'],
            rebalance_frequency=config['rebalance_frequency']
        )
        
        engine = BacktestingEngine(portfolio, strategy, market_data)
        equity_curve, transactions_df = engine.run_backtest()
        
        if not equity_curve.empty:
            strategy_results[config['name']] = {
                'equity_curve': equity_curve,
                'transactions': transactions_df
            }
            print(f"Końcowa wartość portfela dla '{config['name']}': ${equity_curve.iloc[-1]:.2f}")
        else:
            print(f"Ostrzeżenie: Pusta krzywa kapitału dla strategii {config['name']}.")

    # =========================================================================
    # --- 4. ANALIZA I WIZUALIZACJA WYNIKÓW ---
    # =========================================================================
    print("\nAnaliza wyników...")
    if strategy_results:
        # Przygotowanie danych benchmarku
        benchmarks_curves = {}
        for name, ticker in BENCHMARKS.items():
            benchmark_col = f'Close_{ticker}'
            if benchmark_col in market_data.columns:
                curve = market_data[benchmark_col].dropna()
                if not curve.empty:
                    # Normalizacja wartości benchmarku do początkowego kapitału
                    benchmarks_curves[name] = curve * (INITIAL_CASH / curve.iloc[0])
                    print(f"Końcowa wartość benchmarku '{name}': ${benchmarks_curves[name].iloc[-1]:.2f}")

        # Generowanie wykresu (zostanie dostosowane w kolejnym kroku)
        plot_performance(strategy_results, benchmarks_curves)

    else:
        print("Błąd: Nie udało się wygenerować żadnej krzywej kapitału.")

    print("\nSymulacja zakończona pomyślnie.")


if __name__ == "__main__":
    # --- Opcjonalny test dla pojedynczego tickera ---
    # Możesz tutaj wpisać dowolny ticker, aby sprawdzić jego dane przed uruchomieniem symulacji
    test_ticker('SPY')
    test_ticker('SXR8.DE')
    test_ticker('NIEPOPRAWNYTICKER') # Test dla niepoprawnego tickera
    print("\n" + "="*80 + "\n")

    run_simulation()
