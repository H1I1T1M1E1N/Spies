# interfaces.py
from abc import ABC, abstractmethod
import pandas as pd


class ILoyaltyPoolDetector(ABC):
    @abstractmethod
    def detect(self, df: pd.DataFrame, min_passengers: int = 2) -> pd.DataFrame:
        pass