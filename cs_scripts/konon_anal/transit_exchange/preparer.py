# preparer.py
import pandas as pd
import numpy as np
from typing import Tuple, Dict
from .interfaces import IPresenceDataPreparer


class PresenceDataPreparer(IPresenceDataPreparer):
    # Преобразование сырых таблиц с ранней фильтрацией низкоактивных пассажиров

    def prepare(self, df: pd.DataFrame, min_flights: int = 4) -> Tuple[pd.DataFrame, pd.DataFrame, np.ndarray, Dict[str, str]]:
        work_df = df.dropna(subset=['flight_number', 'flight_date', 'departure', 'arrival']).copy()

        work_df['passenger_id'] = work_df['document_number'].fillna(
            work_df['first_name'] + '_' + work_df['last_name']
        )

        # Раннее отсечение: пассажир с < 4 рейсов не может иметь 4 встречи в хабах
        flight_counts = work_df['passenger_id'].value_counts()
        active_pax = flight_counts[flight_counts >= min_flights].index
        work_df = work_df[work_df['passenger_id'].isin(active_pax)].copy()

        pax_uniques = work_df['passenger_id'].unique()
        pax_map = {pax: i for i, pax in enumerate(pax_uniques)}
        work_df['pax_idx'] = work_df['passenger_id'].map(pax_map)

        # Выделяем присутствие в аэропортах
        dep_presence = work_df[['pax_idx', 'departure', 'flight_date']].rename(columns={'departure': 'airport'})
        arr_presence = work_df[['pax_idx', 'arrival', 'flight_date']].rename(columns={'arrival': 'airport'})

        presence_df = pd.concat([dep_presence, arr_presence]).drop_duplicates()
        presence_df['token'] = presence_df['airport'] + '_' + presence_df['flight_date'].astype(str)

        work_df['flight_token'] = work_df['flight_number'].astype(str) + '_' + work_df['flight_date'].astype(str)

        name_map = work_df.drop_duplicates(subset=['passenger_id']).set_index('passenger_id').apply(
            lambda r: f"{r['first_name']} {r['last_name']}", axis=1
        ).to_dict()

        return work_df, presence_df, pax_uniques, name_map