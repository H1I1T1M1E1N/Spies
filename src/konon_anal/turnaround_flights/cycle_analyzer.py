# cycle_analyzer.py
import networkx as nx
from typing import Set
from .interfaces import ICycleAnalyzer

class TemporalCycleAnalyzer(ICycleAnalyzer):
    #Анализирует топологию графа на наличие быстрых 2-циклов (A -> B -> A).#

    def count_turnaround_cycles(self, graph: nx.MultiDiGraph, max_days_diff: int = 1) -> int:
        turnarounds = 0
        used_return_edges: Set[str] = set()

        for u in graph.nodes():
            for v in graph.successors(u):
                # Проверяем наличие встречного ребра
                if not graph.has_edge(v, u):
                    continue

                outbound_edges = graph.get_edge_data(u, v)
                inbound_edges = graph.get_edge_data(v, u)

                for out_key, out_data in outbound_edges.items():
                    out_date = out_data['date']

                    for in_key, in_data in inbound_edges.items():
                        edge_id = f"{v}_{u}_{in_key}"
                        if edge_id in used_return_edges:
                            continue

                        time_diff = (in_data['date'] - out_date).days

                        # Проверка попадания в окно 0..max_days_diff дней
                        if 0 <= time_diff <= max_days_diff:
                            turnarounds += 1
                            used_return_edges.add(edge_id)
                            break

        return turnarounds