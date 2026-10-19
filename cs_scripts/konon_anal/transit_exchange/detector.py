# detector.py
import pandas as pd
import numpy as np
from typing import Dict, List
from .interfaces import ITransitExchangeDetector, IPresenceDataPreparer, ICrossroadMatrixAnalyzer
from .preparer import PresenceDataPreparer
from .matrix_analyzer import CrossroadMatrixAnalyzer


class TransitExchangeDetector(ITransitExchangeDetector):
    # Оркестратор пайплайна поиска транзитных передач

    def __init__(self, preparer: IPresenceDataPreparer = None, analyzer: ICrossroadMatrixAnalyzer = None):
        self._preparer = preparer or PresenceDataPreparer()
        self._analyzer = analyzer or CrossroadMatrixAnalyzer()

    def detect(self, df: pd.DataFrame, min_meetings: int = 4) -> pd.DataFrame:
        work_df, presence_df, pax_uniques, name_map = self._preparer.prepare(df, min_flights=min_meetings)
        n_passengers = len(pax_uniques)

        presence_codes, presence_uniques = pd.factorize(presence_df['token'])
        flight_codes, flight_uniques = pd.factorize(work_df['flight_token'])

        mat_presence = self._analyzer.build_binary_csr(
            presence_df['pax_idx'], presence_codes, (n_passengers, len(presence_uniques))
        )
        mat_flights = self._analyzer.build_binary_csr(
            work_df['pax_idx'], flight_codes, (n_passengers, len(flight_uniques))
        )

        spy_rows, spy_cols, spy_counts = self._analyzer.extract_stealth_pairs(
            mat_presence, mat_flights, min_meetings
        )

        if len(spy_counts) == 0:
            return pd.DataFrame()

        return self._format_results(spy_rows, spy_cols, spy_counts, pax_uniques, name_map)

    def _format_results(self, rows: np.ndarray, cols: np.ndarray, counts: np.ndarray, pax_uniques: np.ndarray, name_map: Dict[str, str]) -> pd.DataFrame:
        records: List[Dict] = []
        for r_idx, c_idx, count in zip(rows, cols, counts):
            id_a = pax_uniques[r_idx]
            id_b = pax_uniques[c_idx]
            records.append({
                'agent_1_id': id_a,
                'agent_1_name': name_map.get(id_a, 'Unknown'),
                'agent_2_id': id_b,
                'agent_2_name': name_map.get(id_b, 'Unknown'),
                'transit_meetings': count
            })

        result_df = pd.DataFrame(records)
        return result_df.sort_values(by='transit_meetings', ascending=False).reset_index(drop=True)