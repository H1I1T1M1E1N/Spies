# interfaces.py
from abc import ABC, abstractmethod
import pandas as pd
from typing import Set, Tuple


class IPassportClassifier(ABC):
    @abstractmethod
    def is_anomalous_pair(self, doc_lengths: Set[int]) -> bool:
        pass


class IDualIdentityDetector(ABC):
    @abstractmethod
    def detect(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        pass