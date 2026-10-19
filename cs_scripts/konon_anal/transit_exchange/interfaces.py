# interfaces.py
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
import scipy.sparse as sp
from typing import Tuple, Dict


class IPresenceDataPreparer(ABC):
    @abstractmethod
    def prepare(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, np.ndarray, Dict[str, str]]:
        pass


class ICrossroadMatrixAnalyzer(ABC):
    @abstractmethod
    def build_binary_csr(self, row_indices: pd.Series, col_indices: pd.Series, shape: Tuple[int, int]) -> sp.csr_matrix:
        pass

    @abstractmethod
    def extract_stealth_pairs(self, presence_mat: sp.csr_matrix, flight_mat: sp.csr_matrix, min_meetings: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        pass


class ITransitExchangeDetector(ABC):
    @abstractmethod
    def detect(self, df: pd.DataFrame, min_meetings: int = 4) -> pd.DataFrame:
        pass