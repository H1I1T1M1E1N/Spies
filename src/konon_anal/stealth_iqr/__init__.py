# __init__.py
from .iqr_detector import IqrOutlierDetector
from .visualizer import StealthVisualizer
from .analyzer import StealthAnalyzer
import pandas as pd
from typing import Tuple

def analyze_stealth_iqr(df: pd.DataFrame, plot_path: str = "stealth_distribution.png", top_n: int = 10) -> Tuple[pd.DataFrame, float]:
    detector = IqrOutlierDetector(multiplier=1.5)
    visualizer = StealthVisualizer()
    analyzer = StealthAnalyzer(detector=detector, visualizer=visualizer)
    return analyzer.run(df, plot_path=plot_path, top_n=top_n)