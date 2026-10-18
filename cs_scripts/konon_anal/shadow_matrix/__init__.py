from .sparse_math import ScipySparseCalculator
from .detector import MatrixShadowDetector
import pandas as pd

def detect_shadow_companions(df: pd.DataFrame, min_shared: int = 4) -> pd.DataFrame:
    calculator = ScipySparseCalculator()
    detector = MatrixShadowDetector(calculator)
    return detector.detect(df, min_shared)