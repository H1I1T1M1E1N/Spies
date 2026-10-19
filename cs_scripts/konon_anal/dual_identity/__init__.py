# __init__.py
from .detector import DualIdentityDetector
from typing import Tuple
import pandas as pd


def detect_dual_identities(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    detector = DualIdentityDetector()
    return detector.detect(df)