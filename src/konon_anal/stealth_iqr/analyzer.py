# analyzer.py
import pandas as pd
from typing import Tuple
from .interfaces import IIqrDetector, IStealthVisualizer

class StealthAnalyzer:
    def __init__(self, detector: IIqrDetector, visualizer: IStealthVisualizer):
        self._detector = detector
        self._visualizer = visualizer

    def run(self, df: pd.DataFrame, plot_path: str = "stealth_iqr_distribution.png", top_n: int = 10) -> Tuple[pd.DataFrame, float]:
        outliers, full_stats, threshold = self._detector.detect_outliers(df)
        self._visualizer.plot_distribution(full_stats, threshold, plot_path)
        return outliers.head(top_n), threshold