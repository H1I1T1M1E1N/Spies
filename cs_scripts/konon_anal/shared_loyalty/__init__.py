# __init__.py
from .detector import SharedLoyaltyDetector
import pandas as pd


def detect_shared_loyalty_cards(df: pd.DataFrame, min_passengers: int = 2) -> pd.DataFrame:
    detector = SharedLoyaltyDetector()
    return detector.detect(df, min_passengers)