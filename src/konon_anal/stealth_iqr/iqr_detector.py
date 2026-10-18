# iqr_detector.py
import pandas as pd
from typing import Tuple
from .interfaces import IIqrDetector

class IqrOutlierDetector(IIqrDetector):
    def __init__(self, multiplier: float = 1.5):
        self.multiplier = multiplier

    def detect_outliers(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, float]:
        # Фильтруем пассажиров без программы лояльности
        stealth_flights = df[df['ff_number'].isna()].copy()
        
        # Создаем идентификатор пассажира
        stealth_flights['pax_id'] = stealth_flights['document_number'].fillna(
            stealth_flights['first_name'] + '_' + stealth_flights['last_name']
        )

        # Считаем перелеты на каждого пассажира
        stats = stealth_flights.groupby('pax_id').agg(
            first_name=('first_name', 'first'),
            last_name=('last_name', 'first'),
            document_number=('document_number', 'first'),
            flight_count=('flight_number', 'count')
        ).reset_index()

        stats = stats.sort_values(by='flight_count', ascending=False).reset_index(drop=True)

        # Расчет квартилей
        q1 = stats['flight_count'].quantile(0.25)
        q3 = stats['flight_count'].quantile(0.75)
        iqr = q3 - q1
        threshold = q3 + self.multiplier * iqr

        # Расчет накопительного процента (перцентиля) для графика
        n_pax = len(stats)
        stats['percentile'] = (stats.index + 1) / n_pax * 100.0

        # Выделение выбросов
        outliers = stats[stats['flight_count'] > threshold].copy()

        return outliers, stats, threshold