import numpy as np
import scipy.sparse as sp
from .interfaces import ISparseCalculator

class ScipySparseCalculator(ISparseCalculator):
    def build_incidence_matrix(self, rows_idx, cols_idx, shape) -> sp.csr_matrix:
        # Единицы для наличия связи
        data = np.ones(len(rows_idx), dtype=np.int8)
        
        # Создаем матрицу. Если были дубли (человек 2 раза в базе на 1 рейсе), 
        # csr_matrix их просуммирует. Мы обрезаем до 1 (бинарная матрица).
        matrix = sp.csr_matrix((data, (rows_idx, cols_idx)), shape=shape)
        matrix.data = np.clip(matrix.data, 0, 1)
        
        return matrix

    def compute_hidden_connections(self, m_flights: sp.csr_matrix, m_bookings: sp.csr_matrix) -> sp.coo_matrix:
        # 1. Умножаем M * M.T для получения количества совпадений.
        # Берем ТОЛЬКО верхний треугольник (triu, k=1), чтобы избежать:
        # - Диагонали (человек летал сам с собой).
        # - Дубликатов (пара А-Б и пара Б-А - это одно и то же).
        shared_flights = sp.triu(m_flights.dot(m_flights.T), k=1)
        shared_bookings = sp.triu(m_bookings.dot(m_bookings.T), k=1)

        # 2. Математическое вычитание "официальных" совместных полетов
        hidden_connections = shared_flights - shared_bookings
        
        # Переводим в координатный формат (COO) для быстрого извлечения пар
        return hidden_connections.tocoo()