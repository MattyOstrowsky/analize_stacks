# -*- coding: utf-8 -*-
"""
Główny plik uruchomieniowy dla aplikacji do backtestingu.

Ten skrypt konfiguruje i uruchamia symulację strategii inwestycyjnej.
"""
from src.data_provider import get_data
from src.portfolio import Portfolio
from src.strategy import BuyAndHoldStrategy, MonthlyInvestmentStrategy
from src.engine import BacktestingEngine
from src.analysis import plot_performance

def run_simulation():
    """
    Konfiguruje i uruchamia pełną symulację backtestingu.
    """
    # =========================================================================
    # --- 1. KONFIGURACJA SYMULACJI ---
    # =========================================================================

    # Wybierz strategię: 'BuyAndHold' lub 'MonthlyInvestment'
    STRATEGY_CHOICE = 'MonthlyInvestment'

    # Parametry ogólne
    INITIAL_CASH = 10000.0
    START_DATE = '2020-01-01'
    END_DATE = '2023-12-31'
    BENCHMARK_TICKER = 'SPY' # Benchmark do porównania (np. S&P 500 ETF)

    # Parametry dla strategii 'BuyAndHold'
    B_H_TICKERS = ['AAPL', 'MSFT']

    # Parametry dla strategii 'MonthlyInvestment'
    M_I_TICKER = 'SPY'
    M_I_AMOUNT = 500.0 # Kwota inwestowana co miesiąc

    # =========================================================================
    # --- 2. PRZYGOTOWANIE DO SYMULACJI ---
    # =========================================================================
    print("Inicjalizacja symulacji...")

    portfolio = Portfolio(initial_cash=INITIAL_CASH)

    if STRATEGY_CHOICE == 'BuyAndHold':
        strategy = BuyAndHoldStrategy(tickers=B_H_TICKERS, initial_investment_per_ticker=INITIAL_CASH / len(B_H_TICKERS))
        tickers_to_fetch = list(set(B_H_TICKERS + [BENCHMARK_TICKER]))
        print(f"Wybrano strategię: Kup i Trzymaj dla {B_H_TICKERS}")
    elif STRATEGY_CHOICE == 'MonthlyInvestment':
        strategy = MonthlyInvestmentStrategy(ticker=M_I_TICKER, monthly_investment=M_I_AMOUNT)
        tickers_to_fetch = list(set([M_I_TICKER, BENCHMARK_TICKER]))
        print(f"Wybrano strategię: Comiesięczna inwestycja ${M_I_AMOUNT} w {M_I_TICKER}")
    else:
        raise ValueError(f"Nieznana strategia: {STRATEGY_CHOICE}")

    print("Pobieranie danych rynkowych...")
    market_data = get_data(tickers_to_fetch, START_DATE, END_DATE)

    # =========================================================================
    # --- 3. URUCHOMIENIE SILNIKA BACKTESTINGU ---
    # =========================================================================
    engine = BacktestingEngine(portfolio, strategy, market_data)
    equity_curve = engine.run_backtest()

    # =========================================================================
    # --- 4. ANALIZA I WIZUALIZACJA WYNIKÓW ---
    # =========================================================================
    print("Analiza wyników...")
    if not equity_curve.empty:
        # Przygotowanie danych benchmarku
        benchmark_col = f'Close_{BENCHMARK_TICKER}'
        benchmark_data = market_data[benchmark_col].dropna()

        # Skalowanie benchmarku do wartości początkowej portfela
        benchmark_curve = benchmark_data * (INITIAL_CASH / benchmark_data.iloc[0])

        # Generowanie wykresu
        plot_performance(equity_curve, benchmark_curve, output_filename='performance_chart.png')

        print("\n--- Podsumowanie ---")
        print(f"Początkowa wartość portfela: ${INITIAL_CASH:.2f}")
        print(f"Końcowa wartość portfela: ${equity_curve.iloc[-1]:.2f}")
        print(f"Końcowa wartość benchmarku (z tej samej inwestycji pocz.): ${benchmark_curve.iloc[-1]:.2f}")

    else:
        print("Błąd: Equity curve jest pusta. Nie można przeanalizować wyników.")

    print("\nSymulacja zakończona pomyślnie.")


if __name__ == "__main__":
    run_simulation()
