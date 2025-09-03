# -*- coding: utf-8 -*-
"""
Moduł strategii inwestycyjnych.

Definiuje bazową klasę dla strategii oraz konkretne implementacje.
"""
from abc import ABC, abstractmethod
import pandas as pd
from src.portfolio import Portfolio

class Strategy(ABC):
    """
    Abstrakcyjna klasa bazowa dla strategii inwestycyjnych.
    """
    @abstractmethod
    def generate_signals(self, date: pd.Timestamp, data: pd.DataFrame, portfolio: Portfolio) -> dict:
        """
        Generuje sygnały transakcyjne na podstawie danych historycznych.

        Args:
            date (pd.Timestamp): Aktualna data symulacji.
            data (pd.DataFrame): Kompletne dane rynkowe dostępne do tej daty.
            portfolio (Portfolio): Obiekt portfela.

        Returns:
            dict: Słownik sygnałów transakcyjnych w formacie {ticker: ilość}.
                  Dodatnia ilość oznacza kupno, ujemna sprzedaż.
        """
        raise NotImplementedError("Należy zaimplementować metodę `generate_signals`!")


class BuyAndHoldStrategy(Strategy):
    """
    Prosta strategia "Kup i Trzymaj".

    Kupuje określone aktywa na początku symulacji i trzyma je do końca.
    """
    def __init__(self, tickers: list, initial_investment_per_ticker: float):
        self.tickers = tickers
        self.initial_investment = initial_investment_per_ticker
        self.invested = False

    def generate_signals(self, date: pd.Timestamp, data: pd.DataFrame, portfolio: Portfolio) -> dict:
        signals = {}
        if not self.invested:
            for ticker in self.tickers:
                price_col = f'Close_{ticker}'
                if price_col in data.columns:
                    current_price = data.loc[date, price_col]
                    if pd.notna(current_price) and current_price > 0:
                        quantity = int(self.initial_investment / current_price)
                        if quantity > 0:
                            signals[ticker] = quantity
            self.invested = True
        return signals


class MomentumStrategy(Strategy):
    """
    Strategia oparta na momentum.

    Rebalansuje portfel z zadaną częstotliwością, wybierając jeden,
    najlepiej radzący sobie ETF na podstawie zwrotu z ostatniego okresu
    (lookback_months) i inwestuje w niego cały kapitał.
    """
    def __init__(self, tickers: list, lookback_months: int, rebalance_frequency: str = 'monthly'):
        if lookback_months <= 0:
            raise ValueError("Okres 'lookback' musi być dodatni.")
        if rebalance_frequency not in ['daily', 'weekly', 'monthly']:
            raise ValueError("Częstotliwość rebalansowania musi być 'daily', 'weekly' lub 'monthly'.")

        self.tickers = tickers
        self.lookback_months = lookback_months
        self.rebalance_frequency = rebalance_frequency

    def generate_signals(self, date: pd.Timestamp, data: pd.DataFrame, portfolio: Portfolio) -> dict:
        # --- Sprawdzenie, czy nadszedł czas na rebalansowanie ---
        is_rebalance_day = False
        if self.rebalance_frequency == 'daily':
            is_rebalance_day = True
        elif self.rebalance_frequency == 'weekly':
            # Sprawdź, czy to pierwszy dzień handlowy w tym tygodniu
            week_data = data[data.index.isocalendar().week == date.isocalendar().week]
            if not week_data.empty and date == week_data.index[0]:
                is_rebalance_day = True
        elif self.rebalance_frequency == 'monthly':
            # Sprawdź, czy to pierwszy dzień handlowy w tym miesiącu
            month_data = data[data.index.month == date.month]
            if not month_data.empty and date == month_data.index[0]:
                is_rebalance_day = True

        if not is_rebalance_day:
            return {}

        print(f"\n--- Rebalansowanie portfela ({self.rebalance_frequency}) w dniu: {date.date()} ---")

        # Obliczanie momentum dla każdego tickera
        momentum = {}
        lookback_start_date = date - pd.DateOffset(months=self.lookback_months)

        # Upewniamy się, że mamy dane do obliczeń
        lookback_data = data.loc[(data.index >= lookback_start_date) & (data.index < date)]
        if lookback_data.empty:
            print("Ostrzeżenie: Brak danych historycznych do obliczenia momentum.")
            return {}

        for ticker in self.tickers:
            price_col = f'Close_{ticker}'
            if price_col not in lookback_data.columns:
                continue

            prices = lookback_data[price_col].dropna()
            if len(prices) > 1:
                # Prosty zwrot: (ostatnia cena - pierwsza cena) / pierwsza cena
                momentum[ticker] = (prices.iloc[-1] - prices.iloc[0]) / prices.iloc[0]

        if not momentum:
            print("Ostrzeżenie: Nie udało się obliczyć momentum dla żadnego tickera.")
            return {}

        # Wybór najlepszego tickera
        winner_ticker = max(momentum, key=momentum.get)
        print(f"Zwycięzca momentum ({self.lookback_months}M): {winner_ticker} (zwrot: {momentum[winner_ticker]:.2%})")

        # Generowanie sygnałów do rebalansowania
        signals = {}

        # 1. Sygnały sprzedaży dla obecnych aktywów
        for holding_ticker, quantity in portfolio.holdings.items():
            if holding_ticker != winner_ticker:
                signals[holding_ticker] = -quantity # Sprzedaj wszystko

        # 2. Sygnał kupna dla zwycięzcy
        current_prices = data.loc[date]
        total_portfolio_value = portfolio.get_total_value(current_prices)
        winner_price = current_prices.get(f'Close_{winner_ticker}')

        if winner_price and pd.notna(winner_price) and winner_price > 0:
            # Użyj całkowitej wartości portfela do obliczenia nowej pozycji
            total_portfolio_value = portfolio.get_total_value(current_prices)

            # Ile akcji zwycięzcy powinniśmy posiadać
            target_quantity = int(total_portfolio_value / winner_price)

            # Ile już posiadamy?
            already_own = portfolio.holdings.get(winner_ticker, 0)

            # Sygnał to różnica między pożądaną a obecną pozycją
            signals[winner_ticker] = target_quantity - already_own

        return {k: v for k, v in signals.items() if v != 0} # Zwróć tylko niezerowe sygnały

class MonthlyInvestmentStrategy(Strategy):
    """
    Strategia comiesięcznego inwestowania stałej kwoty w jeden walor.
    """
    def __init__(self, ticker: str, monthly_investment: float):
        self.ticker = ticker
        self.monthly_investment = monthly_investment
        self.last_investment_month = -1

    def generate_signals(self, date: pd.Timestamp, data: pd.DataFrame, portfolio: Portfolio) -> dict:
        signals = {}
        current_month = date.month

        # Sprawdź, czy to nowy miesiąc i czy już w nim nie inwestowano
        if current_month != self.last_investment_month:
            # Sprawdź, czy to pierwszy dzień handlowy miesiąca
            # (proste założenie: jeśli data istnieje w danych, to jest dniem handlowym)
            current_month_days = data.loc[data.index.month == current_month]
            if not current_month_days.empty and date == current_month_days.index[0]:
                price_col = f'Close_{self.ticker}'
                if price_col in data.columns:
                    current_price = data.loc[date, price_col]
                    if pd.notna(current_price) and current_price > 0:
                        quantity = int(self.monthly_investment / current_price)
                        if quantity > 0:
                            signals[self.ticker] = quantity
                            self.last_investment_month = current_month
        return signals
