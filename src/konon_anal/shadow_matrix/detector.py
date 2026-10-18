# konon_anal/shadow_matrix/detector.py
import pandas as pd
import numpy as np
from .interfaces import ISparseCalculator

class MatrixShadowDetector:
    def __init__(self, calculator: ISparseCalculator):
        self._calc = calculator

    def detect(self, df: pd.DataFrame, min_shared: int = 4) -> pd.DataFrame:
        print("Подготовка данных для матричного анализа...")
        
        # 1. Формируем уникальный ID пассажира
        pax_id_series = df['document_number'].fillna(
            df['first_name'].astype(str) + '_' + df['last_name'].astype(str)
        )
        
        work_df = df.copy()
        work_df['passenger_id'] = pax_id_series

        # 2. ЖЕСТКАЯ ФИЛЬТРАЦИЯ: убираем все строки с пустыми значениями ключевых полей
        # Убираем также случаи, когда имя склеилось в 'nan_nan'
        mask_valid = (
            work_df['flight_number'].notna() &
            work_df['flight_date'].notna() &
            work_df['passenger_id'].notna() &
            (work_df['passenger_id'] != 'nan_nan')
        )
        work_df = work_df[mask_valid].copy()

        # 3. Безопасный PNR: если PNR пустой, задаем уникальный ID, чтобы не склеивать людей
        work_df['safe_pnr'] = np.where(
            work_df['pnr'].notna(),
            work_df['pnr'],
            'NO_PNR_' + work_df.index.astype(str)
            )
        # 4. Факторизация (перевод в целочисленные индексы матрицы)
        # pd.factorize гарантированно не вернет -1, так как мы отфильтровали NaN выше
        pax_codes, pax_uniques = pd.factorize(work_df['passenger_id'])
        
        flight_codes, flight_uniques = pd.factorize(
            work_df['flight_number'].astype(str) + '_' + work_df['flight_date'].astype(str)
        )
        
        booking_codes, booking_uniques = pd.factorize(
            work_df['flight_number'].astype(str) + '_' + work_df['flight_date'].astype(str) + '_' + work_df['safe_pnr'].astype(str)
        )

        n_passengers = len(pax_uniques)

        print(f"Построение разреженных матриц [{n_passengers:,} x {len(flight_uniques):,}]...")
        # 5. Построение матриц инцидентности
        m_flights = self._calc.build_incidence_matrix(pax_codes, flight_codes, (n_passengers, len(flight_uniques)))
        m_bookings = self._calc.build_incidence_matrix(pax_codes, booking_codes, (n_passengers, len(booking_uniques)))

        print("Умножение матриц C = M * M^T (вычисление пересечений)...")
        # 6. Матричное вычисление скрытых связей
        hidden_matrix = self._calc.compute_hidden_connections(m_flights, m_bookings)

        # 7. Фильтрация пар по порогу (>= 4)
        mask = hidden_matrix.data >= min_shared
        
        pax_a_idx = hidden_matrix.row[mask]
        pax_b_idx = hidden_matrix.col[mask]
        shared_counts = hidden_matrix.data[mask]

        if len(shared_counts) == 0:
            return pd.DataFrame()

        print("Формирование итогового списка 'Теней'...")
        # 8. Создаем маппинг ID -> Полное Имя (берем первое встреченное)
        name_map = work_df.drop_duplicates(subset=['passenger_id']).set_index('passenger_id').apply(
            lambda row: f"{row['first_name']} {row['last_name']}", axis=1
        ).to_dict()

        results = []
        for a_idx, b_idx, count in zip(pax_a_idx, pax_b_idx, shared_counts):
            id_a = pax_uniques[a_idx]
            id_b = pax_uniques[b_idx]
            results.append({
                'passenger_1_id': id_a,
                'passenger_1_name': name_map.get(id_a, 'Unknown'),
                'passenger_2_id': id_b,
                'passenger_2_name': name_map.get(id_b, 'Unknown'),
                'shared_stealth_flights': count
            })

        res_df = pd.DataFrame(results)
        return res_df.sort_values(by='shared_stealth_flights', ascending=False).reset_index(drop=True)