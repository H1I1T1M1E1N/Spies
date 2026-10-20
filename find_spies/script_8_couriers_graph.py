import time
import networkx as nx
import pandas as pd
from dataclasses import dataclass
from typing import List, Set, Tuple

DATASET_PATH = "datasets/MASTER_AIRLINES_DB_sorted.csv"
OUTPUT_CSV = "datasets/spies_couriers_turnaround.csv"
TOP_N = 15


@dataclass
class CourierCandidate:
    document_number: str
    first_name: str
    last_name: str
    birth_date: str
    turnaround_count: int
    total_flights: int
    turnaround_ratio: float
    sample_episodes: str


class PassengerGraphBuilder:
    """Генерация направленного мультиграфа перелетов для одного пассажира."""

    @staticmethod
    def build_passenger_graph(passenger_flights: pd.DataFrame) -> nx.MultiDiGraph:
        graph = nx.MultiDiGraph()
        for row in passenger_flights.itertuples(index=False):
            graph.add_edge(
                row.departure,
                row.arrival,
                date=row.flight_date_dt,
                flight_number=row.flight_number,
            )
        return graph


class TemporalCycleAnalyzer:
    """Анализирует топологию графа на наличие быстрых 2-циклов (A -> B -> A за 0..1 день)."""

    @staticmethod
    def count_turnaround_cycles(
        graph: nx.MultiDiGraph, max_days_diff: int = 1
    ) -> Tuple[int, List[str]]:
        turnarounds = 0
        used_return_edges: Set[str] = set()
        episodes: List[str] = []

        for u in graph.nodes():
            for v in graph.successors(u):
                if not graph.has_edge(v, u):
                    continue

                outbound_edges = graph.get_edge_data(u, v)
                inbound_edges = graph.get_edge_data(v, u)

                for out_key, out_data in outbound_edges.items():
                    out_date = out_data["date"]

                    for in_key, in_data in inbound_edges.items():
                        edge_id = f"{v}_{u}_{in_key}"
                        if edge_id in used_return_edges:
                            continue

                        in_date = in_data["date"]
                        time_diff = (in_date - out_date).days

                        if 0 <= time_diff <= max_days_diff:
                            turnarounds += 1
                            used_return_edges.add(edge_id)
                            episodes.append(
                                f"{u} ➔ {v} ➔ {u} ({out_date.strftime('%Y-%m-%d')} / {in_date.strftime('%Y-%m-%d')})"
                            )
                            break

        return turnarounds, episodes


def detect_couriers_graph(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    work_df = df.copy()
    work_df["clean_doc"] = (
        work_df["document_number"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
    )
    work_df["birth_date"] = work_df["birth_date"].fillna("Неизвестно")

    work_df = work_df.dropna(
        subset=["flight_date", "departure", "arrival", "first_name", "last_name", "clean_doc"]
    )
    work_df = work_df[~work_df["clean_doc"].isin(["", "nan", "None"])].copy()

    work_df["flight_date_dt"] = pd.to_datetime(work_df["flight_date"], errors="coerce")
    work_df = work_df.dropna(subset=["flight_date_dt"])
    work_df = work_df.sort_values(by=["clean_doc", "flight_date_dt"])

    builder = PassengerGraphBuilder()
    analyzer = TemporalCycleAnalyzer()
    candidates: List[CourierCandidate] = []

    for doc_id, group in work_df.groupby("clean_doc"):
        total_flights = len(group)
        if total_flights < 2:
            continue

        graph = builder.build_passenger_graph(group)
        turnaround_count, episodes = analyzer.count_turnaround_cycles(graph, max_days_diff=1)

        if turnaround_count > 0:
            ratio = round((turnaround_count * 2) / total_flights, 2)
            sample_ep = "; ".join(episodes[:3])
            if len(episodes) > 3:
                sample_ep += f" и еще {len(episodes) - 3} разворотов"

            candidates.append(
                CourierCandidate(
                    document_number=doc_id,
                    first_name=group["first_name"].iloc[0],
                    last_name=group["last_name"].iloc[0],
                    birth_date=group["birth_date"].iloc[0],
                    turnaround_count=turnaround_count,
                    total_flights=total_flights,
                    turnaround_ratio=ratio,
                    sample_episodes=sample_ep,
                )
            )

    if not candidates:
        return pd.DataFrame()

    res_df = pd.DataFrame([vars(c) for c in candidates])
    res_df = res_df.sort_values(
        by=["turnaround_count", "turnaround_ratio"], ascending=[False, False]
    ).reset_index(drop=True)

    if top_n is not None:
        res_df = res_df.head(top_n).copy()

    res_df["comment"] = res_df.apply(
        lambda r: (
            f"Выявлен графовым анализом в ходе операции «Курьер»: совершил(а) {r['turnaround_count']} "
            f"быстрых челночных разворотов «туда-обратно» с пребыванием в точке назначения не более 0–1 дня "
            f"(всего рейсов: {r['total_flights']}, доля челночных перелетов: {int(r['turnaround_ratio'] * 100)}%, "
            f"примеры маршрутов: {r['sample_episodes']}), что характерно для связного или курьера по доставке "
            f"секретных материалов."
        ),
        axis=1,
    )

    return res_df[["document_number", "first_name", "last_name", "birth_date", "comment"]]


def main():
    print(f"Загрузка данных из: {DATASET_PATH} ...")
    start_load = time.time()
    df = pd.read_csv(DATASET_PATH, dtype=str, low_memory=False)
    df.columns = df.columns.str.strip()
    print(f"Загружено записей: {len(df):,} за {time.time() - start_load:.2f} сек.")

    print("\nЗапуск графового анализа операции «Курьер»...")
    start_analysis = time.time()
    result_df = detect_couriers_graph(df, top_n=TOP_N)
    print(f"Анализ завершен за {time.time() - start_analysis:.2f} сек.")

    if result_df.empty:
        print("Подозрительных курьеров не обнаружено.")
        return

    result_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    print(f"✅ Найдено курьеров: {len(result_df)}. Отчет сохранен в '{OUTPUT_CSV}'.")


if __name__ == "__main__":
    main()
