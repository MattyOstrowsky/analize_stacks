# -*- coding: utf-8 -*-
"""
Moduł portfela inwestycyjnego.

Definiuje klasę Portfolio do zarządzania gotówką, aktywami i transakcjami.
"""
import pandas as pd
from datetime import datetime

class Portfolio:
    """
    Reprezentuje portfel inwestycyjny, zarządzając gotówką, aktywami i historią transakcji.
    """
    def __init__(self, initial_cash: float = 100000.0):
        """
        Inicjalizuje portfel.

        Args:
            initial_cash (float): Początkowa ilość gotówki.
        """
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.holdings = {}  # Słownik przechowujący {ticker: ilość}
        self.transactions = []  # Lista przechowująca transakcje

    def execute_transaction(self, ticker: str, quantity: int, price: float, transaction_date: datetime):
        """
        Wykonuje transakcję kupna lub sprzedaży.

        Args:
            ticker (str): Ticker akcji/ETF.
            quantity (int): Ilość. Dodatnia dla kupna, ujemna dla sprzedaży.
            price (float): Cena jednostkowa.
            transaction_date (datetime): Data transakcji.
        """
        transaction_cost = quantity * price

        if quantity > 0:  # Kupno
            if self.cash < transaction_cost:
                print(f"Błąd: Brak wystarczającej gotówki do zakupu {quantity} akcji {ticker}.")
                return
            self.holdings[ticker] = self.holdings.get(ticker, 0) + quantity
            self.cash -= transaction_cost
            action = 'BUY'
        elif quantity < 0:  # Sprzedaż
            if self.holdings.get(ticker, 0) < abs(quantity):
                print(f"Błąd: Brak wystarczającej liczby akcji {ticker} do sprzedaży.")
                return
            self.holdings[ticker] += quantity  # quantity jest ujemne
            if self.holdings[ticker] == 0:
                del self.holdings[ticker]
            self.cash -= transaction_cost # transaction_cost jest ujemny, więc dodajemy gotówkę
            action = 'SELL'
        else: # quantity == 0
            return

        self._record_transaction(transaction_date, ticker, quantity, price, action)

    def _record_transaction(self, date: datetime, ticker: str, quantity: int, price: float, action: str):
        """Zapisuje transakcję do historii."""
        self.transactions.append({
            'date': date,
            'ticker': ticker,
            'action': action,
            'quantity': abs(quantity),
            'price': price,
            'cost': abs(quantity) * price
        })
        print(f"Zapisano transakcję: {date.date()} | {action} {abs(quantity)} {ticker} @ {price:.2f}")

    def get_holdings_value(self, current_prices: pd.Series) -> float:
        """
        Oblicza aktualną wartość posiadanych aktywów.

        Args:
            current_prices (pd.Series): Seria zawierająca aktualne ceny aktywów,
                                        indeksowana po tickerach.

        Returns:
            float: Łączna wartość aktywów w portfelu.
        """
        value = 0.0
        for ticker, quantity in self.holdings.items():
            # Nazwy kolumn w danych to np. 'Close_SPY', 'Close_AAPL'
            price_col = f'Close_{ticker}'
            if price_col in current_prices.index:
                value += quantity * current_prices[price_col]
            else:
                print(f"Ostrzeżenie: Brak aktualnej ceny dla {ticker}. Nie wliczono do wartości portfela.")
        return value

    def get_total_value(self, current_prices: pd.Series) -> float:
        """
        Oblicza całkowitą wartość portfela (aktywa + gotówka).

        Args:
            current_prices (pd.Series): Seria z aktualnymi cenami.

        Returns:
            float: Całkowita wartość portfela.
        """
        return self.get_holdings_value(current_prices) + self.cash

    def get_transactions_df(self) -> pd.DataFrame:
        """Zwraca historię transakcji jako DataFrame."""
        return pd.DataFrame(self.transactions)
