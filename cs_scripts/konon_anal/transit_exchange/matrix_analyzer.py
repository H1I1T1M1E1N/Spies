# matrix_analyzer.py
import numpy as np
import pandas as pd
import scipy.sparse as sp
from typing import Tuple, List
from .interfaces import ICrossroadMatrixAnalyzer


class CrossroadMatrixAnalyzer(ICrossroadMatrixAnalyzer):
    # Разреженная линейная алгебра с блочной обработкой для предотвращения OOM

    def build_binary_csr(self, row_indices: pd.Series, col_indices: pd.Series, shape: Tuple[int, int]) -> sp.csr_matrix:
        matrix = sp.csr_matrix(
            (np.ones(len(row_indices), dtype=np.int8), (row_indices, col_indices)), 
            shape=shape
        )
        matrix.data = np.clip(matrix.data, 0, 1)
        return matrix

    def extract_stealth_pairs(self, presence_mat: sp.csr_matrix, flight_mat: sp.csr_matrix, min_meetings: int, chunk_size: int = 2000) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        n_pax = presence_mat.shape[0]
        
        all_rows: List[int] = []
        all_cols: List[int] = []
        all_counts: List[int] = []

        # Транспонируем один раз для ускорения перемножения
        presence_t = presence_mat.T.tocsc()
        flight_csr = flight_mat.tocsr()

        # Блочное перемножение (Chunking) для экономии RAM
        for start_idx in range(0, n_pax, chunk_size):
            end_idx = min(start_idx + chunk_size, n_pax)
            
            # Умножаем только срез строк на всю матрицу
            chunk_p = presence_mat[start_idx:end_idx].dot(presence_t).tocoo()
            
            # Маппим локальный индекс строки среза в глобальный
            global_rows = chunk_p.row + start_idx
            global_cols = chunk_p.col
            
            # Оставляем только верхний треугольник (col > row) и пары >= порога
            mask = (global_cols > global_rows) & (chunk_p.data >= min_meetings)
            
            candidate_rows = global_rows[mask]
            candidate_cols = global_cols[mask]
            candidate_counts = chunk_p.data[mask]

            if len(candidate_counts) == 0:
                continue

            # Проверяем совместные полеты только для найденных кандидатов
            # Векторно перемножаем строки F для отобранных пар
            # (row_i dot col_j)
            shared_flights = np.array([
                flight_csr[r].dot(flight_csr[c].T).data.sum() 
                for r, c in zip(candidate_rows, candidate_cols)
            ])

            # Шпионы: встреч много, но совместных перелетов строго 0
            stealth_mask = shared_flights == 0

            all_rows.extend(candidate_rows[stealth_mask])
            all_cols.extend(candidate_cols[stealth_mask])
            all_counts.extend(candidate_counts[stealth_mask])

        return np.array(all_rows), np.array(all_cols), np.array(all_counts)