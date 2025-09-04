# -*- coding: utf-8 -*-
"""
Moduł analizy i wizualizacji wyników.

Generuje raporty i wykresy na podstawie wyników symulacji.
"""
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
from typing import Dict, Any

# Ustawienie domyślnego szablonu dla Plotly
pio.templates.default = "plotly_dark"

def plot_performance(
    strategy_results: Dict[str, Dict[str, Any]],
    benchmarks: Dict[str, pd.Series]
):
    """
    Generuje i zapisuje interaktywne wykresy dla każdej strategii,
    pokazując wartość portfela i posiadane aktywa.

    Args:
        strategy_results (Dict): Słownik, gdzie klucze to nazwy strategii,
            a wartości to kolejne słowniki z 'equity_curve' i 'transactions'.
        benchmarks (Dict): Słownik z nazwami i seriami czasowymi benchmarków.
    """
    print("Generowanie interaktywnych wykresów wydajności...")

    # Zdefiniuj paletę kolorów dla różnych tickerów
    colors = ['rgba(255, 165, 0, 0.3)', 'rgba(0, 255, 255, 0.3)',
              'rgba(255, 255, 0, 0.3)', 'rgba(128, 0, 128, 0.3)',
              'rgba(0, 128, 0, 0.3)', 'rgba(255, 0, 0, 0.3)']
    ticker_colors = {}
    
    # Przejdź przez każdą strategię i wygeneruj dla niej osobny wykres
    for name, results in strategy_results.items():
        equity_curve = results['equity_curve']
        transactions_df = results['transactions']

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # 1. Dodaj główną linię wartości portfela (Equity Curve)
        fig.add_trace(
            go.Scatter(
                x=equity_curve.index,
                y=equity_curve,
                mode='lines',
                name='Wartość Portfela',
                line=dict(color='cyan', width=2)
            ),
            secondary_y=False,
        )

        # 2. Dodaj benchmark do wykresu
        for bench_name, bench_curve in benchmarks.items():
            fig.add_trace(
                go.Scatter(
                    x=bench_curve.index,
                    y=bench_curve,
                    mode='lines',
                    name=bench_name,
                    line=dict(color='gray', width=2, dash='dash')
                ),
                secondary_y=False,
            )

        # 3. Wizualizacja posiadanych aktywów w tle
        if not transactions_df.empty:
            # Sortuj transakcje, aby upewnić się, że przetwarzamy je w porządku chronologicznym
            transactions_df = transactions_df.sort_values(by='date').reset_index(drop=True)

            # Znajdź unikalne tickery i przypisz im kolory
            unique_tickers = transactions_df['ticker'].unique()
            for i, ticker in enumerate(unique_tickers):
                if ticker not in ticker_colors:
                    ticker_colors[ticker] = colors[i % len(colors)]

            # Przetwarzaj transakcje, aby znaleźć okresy posiadania
            holdings = {}
            for index, row in transactions_df.iterrows():
                if row['action'] == 'BUY':
                    holdings[row['ticker']] = row['date']
                elif row['action'] == 'SELL':
                    if row['ticker'] in holdings:
                        start_date = holdings.pop(row['ticker'])
                        # Dodaj prostokąt w tle dla okresu posiadania
                        fig.add_vrect(
                            x0=start_date, x1=row['date'],
                            fillcolor=ticker_colors[row['ticker']],
                            layer="below", line_width=0,
                            annotation_text=row['ticker'],
                            annotation_position="top left"
                        )

            # Obsłuż aktywa, które nie zostały sprzedane do końca symulacji
            end_date = equity_curve.index[-1]
            for ticker, start_date in holdings.items():
                fig.add_vrect(
                    x0=start_date, x1=end_date,
                    fillcolor=ticker_colors.get(ticker, 'rgba(128,128,128,0.3)'),
                    layer="below", line_width=0,
                    annotation_text=ticker,
                    annotation_position="top left"
                )

        # 4. Ustawienia layoutu wykresu
        fig.update_layout(
            title_text=f"Wyniki strategii: {name}",
            xaxis_title="Data",
            yaxis_title="Wartość portfela ($)",
            legend_title="Legenda",
            template="plotly_dark",
            hovermode="x unified"
        )

        # 5. Zapisz wykres do pliku HTML
        # Usuń niedozwolone znaki z nazwy pliku
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '_')).rstrip()
        output_filename = f"performance_{safe_name.replace(' ', '_')}.html"

        try:
            fig.write_html(output_filename)
            print(f"Pomyślnie zapisano wykres: {output_filename}")
        except Exception as e:
            print(f"Błąd podczas zapisywania pliku HTML dla '{name}': {e}")

    # Usuń stary plik PNG, jeśli istnieje
    import os
    if os.path.exists('performance_chart.png'):
        os.remove('performance_chart.png')
        print("Usunięto stary plik 'performance_chart.png'.")
