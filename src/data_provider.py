# -*- coding: utf-8 -*-
"""
Moduł dostawcy danych.

Odpowiedzialny za pobieranie i zarządzanie historycznymi danymi rynkowymi.
"""
import yfinance as yf
import pandas as pd
import os
from typing import List

# Katalog do przechowywania pobranych danych w formacie CSV
CACHE_DIR = 'data'

def get_data(tickers: List[str], start_date: str, end_date: str) -> pd.DataFrame:
    """
    Pobiera dane historyczne dla podanych tickerów w zadanym okresie.
    Wykorzystuje mechanizm cache'owania, aby unikać wielokrotnego pobierania tych samych danych.

    Args:
        tickers (List[str]): Lista tickerów do pobrania.
        start_date (str): Data początkowa w formacie 'YYYY-MM-DD'.
        end_date (str): Data końcowa w formacie 'YYYY-MM-DD'.

    Returns:
        pd.DataFrame: Ramka danych zawierająca historyczne ceny (OHLC) i wolumen.
    """
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

    # Tworzenie unikalnej nazwy pliku dla cache'u
    tickers_str = '_'.join(sorted(tickers))
    filename = f"{tickers_str}_{start_date}_{end_date}.csv"
    filepath = os.path.join(CACHE_DIR, filename)

    if os.path.exists(filepath):
        print(f"Wczytywanie danych z cache: {filepath}")
        data = pd.read_csv(filepath, header=[0, 1], index_col=0, parse_dates=True)
    else:
        print("Pobieranie danych z yfinance...")
        data = yf.download(tickers, start=start_date, end=end_date)
        if not data.empty:
            # Zapisywanie danych do pliku CSV
            data.to_csv(filepath)
            print(f"Zapisano dane w cache: {filepath}")
        else:
            print(f"Nie udało się pobrać danych dla tickerów: {tickers}")

    # Konwersja nazw kolumn na stringi, jeśli to konieczne
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.map(lambda x: f"{x[0]}_{x[1]}")

    return data
