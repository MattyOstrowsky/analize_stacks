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
            a wartości to kolejne słowniki z 'equity_curve', 'transactions' i 'cash_curve'.
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
        cash_curve = results['cash_curve']

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

        # 2. Dodaj linię gotówki
        fig.add_trace(
            go.Scatter(
                x=cash_curve.index,
                y=cash_curve,
                mode='lines',
                name='Gotówka',
                line=dict(color='yellow', width=1, dash='dot')
            ),
            secondary_y=True,
        )

        # 3. Dodaj benchmark do wykresu
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

        # 4. Wizualizacja posiadanych aktywów i transakcji
        if not transactions_df.empty:
            transactions_df = transactions_df.sort_values(by='date').reset_index(drop=True)
            unique_tickers = transactions_df['ticker'].unique()
            for i, ticker in enumerate(unique_tickers):
                if ticker not in ticker_colors:
                    ticker_colors[ticker] = colors[i % len(colors)]

            # Dodaj punkty kupna/sprzedaży
            buys = transactions_df[transactions_df['action'] == 'BUY']
            sells = transactions_df[transactions_df['action'] == 'SELL']

            fig.add_trace(go.Scatter(
                x=buys['date'], y=equity_curve.loc[buys['date']], mode='markers',
                marker=dict(symbol='triangle-up', color='green', size=10),
                name='Kupno', hoverinfo='x+y'
            ), secondary_y=False)

            fig.add_trace(go.Scatter(
                x=sells['date'], y=equity_curve.loc[sells['date']], mode='markers',
                marker=dict(symbol='triangle-down', color='red', size=10),
                name='Sprzedaż', hoverinfo='x+y'
            ), secondary_y=False)

            # Przetwarzaj transakcje, aby znaleźć okresy posiadania
            holdings = {}
            for index, row in transactions_df.iterrows():
                if row['action'] == 'BUY':
                    holdings[row['ticker']] = row['date']
                elif row['action'] == 'SELL':
                    if row['ticker'] in holdings:
                        start_date = holdings.pop(row['ticker'])
                        fig.add_vrect(
                            x0=start_date, x1=row['date'],
                            fillcolor=ticker_colors[row['ticker']],
                            layer="below", line_width=0
                        )

            end_date = equity_curve.index[-1]
            for ticker, start_date in holdings.items():
                fig.add_vrect(
                    x0=start_date, x1=end_date,
                    fillcolor=ticker_colors.get(ticker, 'rgba(128,128,128,0.3)'),
                    layer="below", line_width=0
                )

            # Dodaj legendę dla kolorów tła
            for ticker, color in ticker_colors.items():
                fig.add_trace(go.Scatter(
                    x=[None], y=[None], mode='markers',
                    marker=dict(size=10, color=color, symbol='square'),
                    name=f'Posiadane: {ticker}'
                ))

        # 5. Ustawienia layoutu wykresu
        fig.update_layout(
            title_text=f"Wyniki strategii: {name}",
            xaxis_title="Data",
            yaxis_title="Wartość portfela ($)",
            yaxis2_title="Gotówka ($)",
            legend_title="Legenda",
            template="plotly_dark",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig.update_yaxes(title_text="Wartość portfela ($)", secondary_y=False)
        fig.update_yaxes(title_text="Gotówka ($)", secondary_y=True)

        # 6. Zapisz wykres do pliku HTML
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
