# -*- coding: utf-8 -*-
"""
Moduł silnika backtestingu.

Odpowiedzialny za orkiestrację symulacji.
"""
import pandas as pd
from src.portfolio import Portfolio
from src.strategy import Strategy

class BacktestingEngine:
    """
    Silnik do przeprowadzania historycznych testów strategii inwestycyjnych.
    """
    def __init__(self, portfolio: Portfolio, strategy: Strategy, data: pd.DataFrame):
        """
        Inicjalizuje silnik backtestingu.

        Args:
            portfolio (Portfolio): Obiekt portfela do symulacji.
            strategy (Strategy): Obiekt strategii do testowania.
            data (pd.DataFrame): Ramka danych z historycznymi danymi rynkowymi.
                                 Indeks musi być typu DatetimeIndex.
        """
        self.portfolio = portfolio
        self.strategy = strategy
        self.data = data
        self.equity_curve = None

    def run_backtest(self) -> pd.Series:
        """
        Uruchamia symulację backtestingu.

        Iteruje przez dane dzień po dniu, generuje sygnały, wykonuje transakcje
        i zapisuje dzienną wartość portfela.

        Returns:
            pd.Series: Seria czasowa wartości portfela (equity curve).
        """
        print("Uruchamianie symulacji backtestingu...")

        equity = {}

        for date, row in self.data.iterrows():
            # 1. Generowanie sygnałów przez strategię
            signals = self.strategy.generate_signals(date, self.data, self.portfolio)

            # 2. Wykonanie transakcji na podstawie sygnałów
            if signals:
                for ticker, quantity in signals.items():
                    price_col = f'Close_{ticker}'
                    if price_col in row.index and pd.notna(row[price_col]):
                        price = row[price_col]
                        self.portfolio.execute_transaction(ticker, quantity, price, date)
                    else:
                        print(f"Ostrzeżenie: Brak ceny dla {ticker} w dniu {date.date()}. Transakcja pominięta.")

            # 3. Obliczenie i zapisanie wartości portfela na koniec dnia
            total_value = self.portfolio.get_total_value(row)
            equity[date] = total_value

        self.equity_curve = pd.Series(equity)
        print("Symulacja zakończona.")
        return self.equity_curve
