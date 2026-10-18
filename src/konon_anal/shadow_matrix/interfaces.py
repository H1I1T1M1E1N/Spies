from abc import ABC, abstractmethod
import pandas as pd
import scipy.sparse as sp

class ISparseCalculator(ABC):
    @abstractmethod
    def build_incidence_matrix(self, rows_idx, cols_idx, shape) -> sp.csr_matrix:
        #Строит разреженную бинарную матрицу инцидентности.#
        pass

    @abstractmethod
    def compute_hidden_connections(self, m_flights: sp.csr_matrix, m_bookings: sp.csr_matrix) -> sp.coo_matrix:
        #Вычисляет матрицу скрытых пересечений: (Mf * Mf.T) - (Mb * Mb.T).#
        pass