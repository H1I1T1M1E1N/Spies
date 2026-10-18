# __init__.py
from .graph_builder import PassengerGraphBuilder
from .cycle_analyzer import TemporalCycleAnalyzer
from .detector import GraphCourierDetector
import pandas as pd

def detect_couriers_graph(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    #Фасадная функция для запуска графового детектора с зависимостями по умолчанию.#
    builder = PassengerGraphBuilder()
    analyzer = TemporalCycleAnalyzer()
    detector = GraphCourierDetector(graph_builder=builder, cycle_analyzer=analyzer)
    return detector.analyze(df, top_n=top_n)