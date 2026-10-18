# interfaces.py
from abc import ABC, abstractmethod
import pandas as pd
from typing import Tuple

class IIqrDetector(ABC):
    @abstractmethod
    def detect_outliers(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, float]:
        pass

class IStealthVisualizer(ABC):
    @abstractmethod
    def plot_distribution(self, stats_df: pd.DataFrame, threshold: float, output_path: str) -> None:
        pass