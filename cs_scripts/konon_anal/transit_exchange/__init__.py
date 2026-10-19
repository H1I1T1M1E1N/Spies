# __init__.py
from .detector import TransitExchangeDetector
import pandas as pd


def detect_transit_exchanges(df: pd.DataFrame, min_meetings: int = 4) -> pd.DataFrame:
    detector = TransitExchangeDetector()
    return detector.detect(df, min_meetings)