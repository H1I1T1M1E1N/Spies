# detector.py
import pandas as pd
from typing import List
from .interfaces import IGraphBuilder, ICycleAnalyzer
from .models import CourierCandidate

class GraphCourierDetector:
    #Оркестратор процесса детекции курьеров через графовый анализ.#

    def __init__(self, graph_builder: IGraphBuilder, cycle_analyzer: ICycleAnalyzer):
        self._builder = graph_builder
        self._analyzer = cycle_analyzer

    def analyze(self, df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
        cleaned_df = self._prepare_data(df)
        candidates: List[CourierCandidate] = []

        grouped = cleaned_df.groupby('passenger_id')

        for pax_id, group in grouped:
            total_flights = len(group)
            if total_flights < 2:
                continue

            # 1. Сборка графа
            graph = self._builder.build_passenger_graph(group)

            # 2. Поиск циклов
            turnaround_count = self._analyzer.count_turnaround_cycles(graph, max_days_diff=1)

            # 3. Агрегация кандидата
            if turnaround_count > 0:
                ratio = round((turnaround_count * 2) / total_flights, 2)
                candidates.append(
                    CourierCandidate(
                        passenger_id=pax_id,
                        first_name=group['first_name'].iloc[0],
                        last_name=group['last_name'].iloc[0],
                        turnaround_count=turnaround_count,
                        total_flights=total_flights,
                        turnaround_ratio=ratio
                    )
                )

        return self._format_results(candidates, top_n)

    def _prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        work_df = df.copy()
        work_df['passenger_id'] = work_df['document_number'].fillna(
            work_df['first_name'] + '_' + work_df['last_name']
        )
        work_df = work_df.dropna(subset=['flight_date', 'departure', 'arrival', 'passenger_id'])
        work_df['flight_date'] = pd.to_datetime(work_df['flight_date'])
        return work_df.sort_values(by=['passenger_id', 'flight_date'])

    def _format_results(self, candidates: List[CourierCandidate], top_n: int) -> pd.DataFrame:
        if not candidates:
            return pd.DataFrame()

        res_df = pd.DataFrame([vars(c) for c in candidates])
        res_df = res_df.sort_values(
            by=['turnaround_count', 'turnaround_ratio'],
            ascending=[False, False]
        ).reset_index(drop=True)

        return res_df.head(top_n)