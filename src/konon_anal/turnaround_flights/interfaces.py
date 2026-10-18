# interfaces.py
from abc import ABC, abstractmethod
import pandas as pd
import networkx as nx
from typing import List
from .models import CourierCandidate

class IGraphBuilder(ABC):
    @abstractmethod
    def build_passenger_graph(self, passenger_flights: pd.DataFrame) -> nx.MultiDiGraph:
        #Строит направленный мультиграф перелетов для одного пассажира.#
        pass

class ICycleAnalyzer(ABC):
    @abstractmethod
    def count_turnaround_cycles(self, graph: nx.MultiDiGraph, max_days_diff: int = 1) -> int:
        #Подсчитывает количество зеркальных циклов с ограничением по времени.#
        pass