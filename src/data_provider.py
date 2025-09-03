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
    Ta wersja jest bardziej odporna na problemy z formatowaniem danych z yfinance.
    """
    print("Pobieranie danych rynkowych...")
    
    # Pobieramy dane dla strategii i benchmarku
    data = yf.download(tickers, start=start_date, end=end_date)
    if data.empty:
        raise ConnectionError(f"Nie udało się pobrać danych dla tickerów: {tickers}")

    # Konwersja nazw kolumn z MultiIndex na pojedyncze stringi
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.map(lambda x: f"{x[0]}_{x[1]}")

    # --- KONWERSJA WALUT ---
    eur_tickers = [t for t in tickers if t.endswith('.DE')]
    if eur_tickers:
        print("Wykryto tickery w EUR. Rozpoczynanie konwersji na USD...")
        
        eur_usd_data = yf.download('EURUSD=X', start=start_date, end=end_date, progress=False)
        if eur_usd_data.empty:
            raise ConnectionError("Nie udało się pobrać danych kursu walutowego EUR/USD.")
        
        # Wyodrębnienie serii 'Close' i upewnienie się, że jest to seria (Series)
        eur_usd_series = eur_usd_data['Close']
        if isinstance(eur_usd_series, pd.DataFrame):
            # Jeśli nadal jest to DataFrame (np. z powodu formatowania yfinance), wybierz pierwszą kolumnę
            eur_usd_series = eur_usd_series.iloc[:, 0]
        
        # Dopasowanie indeksu i wypełnienie brakujących danych
        eur_usd_series = eur_usd_series.reindex(data.index).ffill().bfill()
        
        # Ostateczne sprawdzenie, czy nie ma NaN
        if eur_usd_series.isnull().any():
            raise ValueError("Seria kursów walutowych wciąż zawiera wartości NaN po przetworzeniu.")

        # Konwersja cen
        for ticker in eur_tickers:
            for col_type in ['Open', 'High', 'Low', 'Close']:
                col_name = f'{col_type}_{ticker}'
                if col_name in data.columns:
                    data[col_name] = data[col_name] * eur_usd_series
        
        print("Konwersja walut zakończona.")

    return data
