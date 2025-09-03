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
