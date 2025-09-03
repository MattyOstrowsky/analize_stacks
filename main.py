# -*- coding: utf-8 -*-
"""
Główny plik uruchomieniowy dla aplikacji do backtestingu.

Ten skrypt konfiguruje i uruchamia symulację strategii inwestycyjnej.
"""
from src.data_provider import get_data
from src.portfolio import Portfolio
from src.strategy import BuyAndHoldStrategy, MonthlyInvestmentStrategy, MomentumStrategy
from src.engine import BacktestingEngine
from src.analysis import plot_performance

def run_simulation():
    """
    Konfiguruje i uruchamia pełną symulację backtestingu.
    """
    # =========================================================================
    # --- 1. KONFIGURACJA SYMULACJI ---
    # =========================================================================

    # Wybierz strategię: 'BuyAndHold', 'MonthlyInvestment', 'Momentum'
    STRATEGY_CHOICE = 'Momentum'

    # Parametry ogólne
    INITIAL_CASH = 10000.0
    # Data początkowa musi uwzględniać okres 'lookback' dla strategii Momentum
    START_DATE = '2020-01-01'
    END_DATE = '2023-12-31'

    # Definicja benchmarków. Klucz to nazwa, wartość to ticker.
    BENCHMARKS = {'S&P 500': 'SPY'}

    # Parametry dla strategii 'BuyAndHold'
    B_H_TICKERS = ['AAPL', 'MSFT']

    # Parametry dla strategii 'MonthlyInvestment'
    M_I_TICKER = 'SPY'
    M_I_AMOUNT = 500.0

    # Parametry dla strategii 'Momentum'
    MOMENTUM_TICKERS = ['SXR8.DE', 'IS3N.DE', 'VVSM.DE', 'XAIX.DE']
    MOMENTUM_LOOKBACK_MONTHS = 6 # Wariant 1: 6 miesięcy
    MOMENTUM_FREQUENCY = 'weekly' # 'daily', 'weekly', or 'monthly'

    # =========================================================================
    # --- 2. PRZYGOTOWANIE DO SYMULACJI ---
    # =========================================================================
    print("Inicjalizacja symulacji...")

    portfolio = Portfolio(initial_cash=INITIAL_CASH)

    if STRATEGY_CHOICE == 'BuyAndHold':
        strategy = BuyAndHoldStrategy(tickers=B_H_TICKERS, initial_investment_per_ticker=INITIAL_CASH / len(B_H_TICKERS))
        tickers_to_fetch = list(set(B_H_TICKERS + list(BENCHMARKS.values())))
        print(f"Wybrano strategię: Kup i Trzymaj dla {B_H_TICKERS}")
    elif STRATEGY_CHOICE == 'MonthlyInvestment':
        strategy = MonthlyInvestmentStrategy(ticker=M_I_TICKER, monthly_investment=M_I_AMOUNT)
        tickers_to_fetch = list(set([M_I_TICKER] + list(BENCHMARKS.values())))
        print(f"Wybrano strategię: Comiesięczna inwestycja ${M_I_AMOUNT} w {M_I_TICKER}")
    elif STRATEGY_CHOICE == 'Momentum':
        strategy = MomentumStrategy(
            tickers=MOMENTUM_TICKERS,
            lookback_months=MOMENTUM_LOOKBACK_MONTHS,
            rebalance_frequency=MOMENTUM_FREQUENCY
        )
        tickers_to_fetch = list(set(MOMENTUM_TICKERS + list(BENCHMARKS.values())))
        print(f"Wybrano strategię: Momentum {MOMENTUM_LOOKBACK_MONTHS}-miesięczne dla {MOMENTUM_TICKERS} z rebalansowaniem '{MOMENTUM_FREQUENCY}'")
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
        benchmarks_curves = {}
        for name, ticker in BENCHMARKS.items():
            benchmark_col = f'Close_{ticker}'
            if benchmark_col in market_data.columns:
                curve = market_data[benchmark_col].dropna()
                if not curve.empty:
                    benchmarks_curves[name] = curve * (INITIAL_CASH / curve.iloc[0])

        # Generowanie wykresu
        if benchmarks_curves:
            plot_performance(equity_curve, benchmarks_curves)

        print("\n--- Podsumowanie ---")
        print(f"Początkowa wartość portfela: ${INITIAL_CASH:.2f}")
        print(f"Końcowa wartość portfela: ${equity_curve.iloc[-1]:.2f}")
        for name, curve in benchmarks_curves.items():
             print(f"Końcowa wartość benchmarku '{name}': ${curve.iloc[-1]:.2f}")

    else:
        print("Błąd: Equity curve jest pusta. Nie można przeanalizować wyników.")

    print("\nSymulacja zakończona pomyślnie.")


if __name__ == "__main__":
    run_simulation()
