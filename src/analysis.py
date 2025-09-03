# -*- coding: utf-8 -*-
"""
Moduł analizy i wizualizacji wyników.

Generuje raporty i wykresy na podstawie wyników symulacji.
"""
import pandas as pd
import matplotlib.pyplot as plt

from typing import Dict

def plot_performance(strategy_curves: Dict[str, pd.Series], benchmarks: Dict[str, pd.Series], output_filename: str = 'performance_chart.png'):
    """
    Generuje i zapisuje wykres porównujący wyniki wielu strategii z benchmarkami.

    Args:
        strategy_curves (Dict[str, pd.Series]): Słownik z nazwami i seriami czasowymi strategii.
        benchmarks (Dict[str, pd.Series]): Słownik z nazwami i seriami czasowymi benchmarków.
        output_filename (str): Nazwa pliku do zapisu wykresu.
    """
    print(f"Generowanie wykresu wydajności... Zapisywanie do pliku {output_filename}")

    # 1. Tworzenie wykresu
    plt.style.use('seaborn-v0_8-darkgrid')
    fig, ax = plt.subplots(figsize=(16, 10))
    
    # Paleta kolorów dla strategii
    colors = plt.cm.get_cmap('viridis', len(strategy_curves))

    # 2. Rysowanie krzywych kapitału dla każdej strategii
    for i, (name, curve) in enumerate(strategy_curves.items()):
        # Normalizacja danych, aby pokazać skumulowany zwrot
        normalized_curve = curve / curve.iloc[0]
        ax.plot(normalized_curve.index, normalized_curve, label=name, color=colors(i), linewidth=2.0, zorder=10)

    # 3. Dodawanie benchmarków do wykresu
    benchmark_colors = ['gray', 'darkorange', 'red', 'purple']
    for i, (name, curve) in enumerate(benchmarks.items()):
        # Normalizacja danych benchmarku
        benchmark_returns = (curve / curve.iloc[0])
        ax.plot(benchmark_returns.index, benchmark_returns, label=name, color=benchmark_colors[i % len(benchmark_colors)], linestyle='--', linewidth=2.0)


    # 3. Ustawienia wykresu
    ax.set_title('Porównanie Wydajności Strategii z Benchmarkami', fontsize=16)
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
