# graph_builder.py
import networkx as nx
import pandas as pd
from .interfaces import IGraphBuilder

class PassengerGraphBuilder(IGraphBuilder):
    #Отвечает исключительно за генерацию мультиграфа из среза DataFrame.#

    def build_passenger_graph(self, passenger_flights: pd.DataFrame) -> nx.MultiDiGraph:
        graph = nx.MultiDiGraph()
        
        # Итерируемся по кортежам (itertuples значительно быстрее iterrows)
        for row in passenger_flights.itertuples(index=False):
            graph.add_edge(
                row.departure,
                row.arrival,
                date=row.flight_date,
                flight_number=row.flight_number
            )
            
        return graph