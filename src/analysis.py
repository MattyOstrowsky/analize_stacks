# -*- coding: utf-8 -*-
"""
Moduł analizy i wizualizacji wyników.

Generuje raporty i wykresy na podstawie wyników symulacji.
"""
import pandas as pd
import matplotlib.pyplot as plt

def plot_performance(equity_curve: pd.Series, benchmark_curve: pd.Series, output_filename: str = 'performance_chart.png'):
    """
    Generuje i zapisuje wykres porównujący wyniki portfela z benchmarkiem.

    Args:
        equity_curve (pd.Series): Seria czasowa z wartością portfela.
        benchmark_curve (pd.Series): Seria czasowa z wartością benchmarku.
        output_filename (str): Nazwa pliku do zapisu wykresu.
    """
    print(f"Generowanie wykresu wydajności... Zapisywanie do pliku {output_filename}")

    # 1. Normalizacja danych, aby pokazać skumulowany zwrot
    # Dzielimy każdą wartość przez pierwszą wartość, aby obie serie zaczynały się od 1 (lub 100%)
    portfolio_returns = (equity_curve / equity_curve.iloc[0])
    benchmark_returns = (benchmark_curve / benchmark_curve.iloc[0])

    # 2. Tworzenie wykresu
    plt.style.use('seaborn-v0_8-darkgrid')
    fig, ax = plt.subplots(figsize=(12, 8))

    ax.plot(portfolio_returns.index, portfolio_returns, label='Strategia', color='royalblue', linewidth=2)
    ax.plot(benchmark_returns.index, benchmark_returns, label='Benchmark', color='gray', linestyle='--', linewidth=2)

    # 3. Ustawienia wykresu
    ax.set_title('Porównanie Wydajności Strategii z Benchmarkiem', fontsize=16)
    ax.set_xlabel('Data', fontsize=12)
    ax.set_ylabel('Skumulowany Zwrot', fontsize=12)
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True)

    # Formatowanie osi Y jako procent
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.2%}'))

    # Automatyczne formatowanie dat na osi X
    fig.autofmt_xdate()

    # 4. Zapis do pliku
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    plt.close() # Zamykamy figurę, aby nie wyświetlała się w interaktywnych środowiskach

    print("Wykres został pomyślnie wygenerowany.")
