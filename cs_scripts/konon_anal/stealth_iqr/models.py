# models.py
from dataclasses import dataclass

@dataclass(frozen=True)
class IqrMetrics:
    q1: float
    q3: float
    iqr: float
    threshold: float
    outliers_count: int