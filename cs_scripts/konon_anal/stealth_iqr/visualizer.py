# visualizer.py
import matplotlib.pyplot as plt
import pandas as pd
from .interfaces import IStealthVisualizer

class StealthVisualizer(IStealthVisualizer):
    def plot_distribution(self, stats_df: pd.DataFrame, threshold: float, output_path: str) -> None:
        plt.figure(figsize=(10, 6), dpi=300)
        
        # Основная линия распределения
        plt.plot(stats_df['percentile'], stats_df['flight_count'], color='#2b5c8f', linewidth=2, label='Активность пассажиров')

        # Линия порога IQR
        plt.axhline(y=threshold, color='#d9534f', linestyle='--', linewidth=1.5, label=f'Порог аномалий IQR ({threshold:.1f} перелетов)')

        # Оформление по ТЗ
        plt.title('Распределение перелетов пассажиров без карт лояльности (Stealth)', fontsize=13, pad=12)
        plt.xlabel('Накопительный процент людей (%)', fontsize=11)
        plt.ylabel('Количество перелетов', fontsize=11)
        plt.grid(True, linestyle=':', alpha=0.6)
        plt.legend(loc='upper right')

        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()