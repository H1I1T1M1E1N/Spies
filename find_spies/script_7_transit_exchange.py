import time
import numpy as np
import pandas as pd
import scipy.sparse as sp
from typing import Tuple, Dict, List

DATASET_PATH = "MASTER_AIRLINES_DB_sorted.csv"
OUTPUT_CSV = "spies_transit_exchange.csv"
MIN_MEETINGS = 4


class PresenceDataPreparer:
    """Преобразование сырых таблиц с ранней фильтрацией низкоактивных пассажиров."""

    @staticmethod
    def prepare(
        df: pd.DataFrame, min_flights: int = 4
    ) -> Tuple[pd.DataFrame, pd.DataFrame, np.ndarray, Dict[str, dict]]:
        work_df = df.dropna(
            subset=["flight_number", "flight_date", "departure", "arrival", "document_number"]
        ).copy()

        work_df["clean_doc"] = (
            work_df["document_number"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
        )
        work_df = work_df[~work_df["clean_doc"].isin(["", "nan", "None"])].copy()
        work_df["birth_date"] = work_df["birth_date"].fillna("Неизвестно")

        work_df["passenger_id"] = work_df["clean_doc"]

        # Раннее отсечение: пассажир с < min_flights рейсов не может иметь min_flights встреч
        flight_counts = work_df["passenger_id"].value_counts()
        active_pax = flight_counts[flight_counts >= min_flights].index
        work_df = work_df[work_df["passenger_id"].isin(active_pax)].copy()

        pax_uniques = work_df["passenger_id"].unique()
        pax_map = {pax: i for i, pax in enumerate(pax_uniques)}
        work_df["pax_idx"] = work_df["passenger_id"].map(pax_map)

        # Выделяем присутствие в аэропортах (вылет и прилет)
        dep_presence = work_df[["pax_idx", "departure", "flight_date"]].rename(
            columns={"departure": "airport"}
        )
        arr_presence = work_df[["pax_idx", "arrival", "flight_date"]].rename(
            columns={"arrival": "airport"}
        )

        presence_df = pd.concat([dep_presence, arr_presence]).drop_duplicates()
        presence_df["token"] = (
            presence_df["airport"].astype(str) + "_" + presence_df["flight_date"].astype(str)
        )

        work_df["flight_token"] = (
            work_df["flight_number"].astype(str) + "_" + work_df["flight_date"].astype(str)
        )

        pax_info = (
            work_df.drop_duplicates(subset=["passenger_id"])
            .set_index("passenger_id")[["first_name", "last_name", "birth_date"]]
            .to_dict("index")
        )

        return work_df, presence_df, pax_uniques, pax_info


class CrossroadMatrixAnalyzer:
    """Разреженная линейная алгебра с блочной обработкой для предотвращения переполнения памяти (OOM)."""

    @staticmethod
    def build_binary_csr(
        row_indices: pd.Series, col_indices: np.ndarray, shape: Tuple[int, int]
    ) -> sp.csr_matrix:
        matrix = sp.csr_matrix(
            (np.ones(len(row_indices), dtype=np.int8), (row_indices, col_indices)),
            shape=shape,
        )
        matrix.data = np.clip(matrix.data, 0, 1)
        return matrix

    @staticmethod
    def extract_stealth_pairs(
        presence_mat: sp.csr_matrix,
        flight_mat: sp.csr_matrix,
        min_meetings: int,
        chunk_size: int = 2000,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        n_pax = presence_mat.shape[0]

        all_rows: List[int] = []
        all_cols: List[int] = []
        all_counts: List[int] = []

        presence_t = presence_mat.T.tocsc()
        flight_csr = flight_mat.tocsr()

        for start_idx in range(0, n_pax, chunk_size):
            end_idx = min(start_idx + chunk_size, n_pax)

            chunk_p = presence_mat[start_idx:end_idx].dot(presence_t).tocoo()

            global_rows = chunk_p.row + start_idx
            global_cols = chunk_p.col

            mask = (global_cols > global_rows) & (chunk_p.data >= min_meetings)

            candidate_rows = global_rows[mask]
            candidate_cols = global_cols[mask]
            candidate_counts = chunk_p.data[mask]

            if len(candidate_counts) == 0:
                continue

            shared_flights = np.array(
                [
                    flight_csr[r].dot(flight_csr[c].T).data.sum()
                    for r, c in zip(candidate_rows, candidate_cols)
                ]
            )

            # Шпионы: встреч в аэропортах >= min_meetings, но совместных перелетов строго 0
            stealth_mask = shared_flights == 0

            all_rows.extend(candidate_rows[stealth_mask])
            all_cols.extend(candidate_cols[stealth_mask])
            all_counts.extend(candidate_counts[stealth_mask])

        return np.array(all_rows), np.array(all_cols), np.array(all_counts)


def detect_transit_exchanges(df: pd.DataFrame, min_meetings: int = 4) -> pd.DataFrame:
    preparer = PresenceDataPreparer()
    analyzer = CrossroadMatrixAnalyzer()

    work_df, presence_df, pax_uniques, pax_info = preparer.prepare(df, min_flights=min_meetings)
    n_passengers = len(pax_uniques)

    if n_passengers == 0:
        return pd.DataFrame()

    presence_codes, presence_uniques = pd.factorize(presence_df["token"])
    flight_codes, flight_uniques = pd.factorize(work_df["flight_token"])

    mat_presence = analyzer.build_binary_csr(
        presence_df["pax_idx"], presence_codes, (n_passengers, len(presence_uniques))
    )
    mat_flights = analyzer.build_binary_csr(
        work_df["pax_idx"], flight_codes, (n_passengers, len(flight_uniques))
    )

    spy_rows, spy_cols, spy_counts = analyzer.extract_stealth_pairs(
        mat_presence, mat_flights, min_meetings
    )

    if len(spy_counts) == 0:
        return pd.DataFrame()

    # Дополнительно находим точные аэропорты и даты встреч для подробного комментария
    presence_sets = (
        presence_df.groupby("pax_idx")["token"].apply(set).to_dict()
    )

    meetings_per_doc: Dict[str, List[str]] = {}
    for r_idx, c_idx, count in zip(spy_rows, spy_cols, spy_counts):
        doc_a = pax_uniques[r_idx]
        doc_b = pax_uniques[c_idx]
        info_a = pax_info.get(doc_a, {"first_name": "Unknown", "last_name": "Unknown", "birth_date": "Неизвестно"})
        info_b = pax_info.get(doc_b, {"first_name": "Unknown", "last_name": "Unknown", "birth_date": "Неизвестно"})

        common_tokens = sorted(list(presence_sets.get(r_idx, set()) & presence_sets.get(c_idx, set())))
        points_preview = ", ".join(
            [f"{tok.split('_')[0]} ({tok.split('_')[1]})" for tok in common_tokens[:4]]
        )
        if len(common_tokens) > 4:
            points_preview += f" и еще {len(common_tokens) - 4}"

        meetings_per_doc.setdefault(doc_a, []).append(
            f"{info_b['first_name']} {info_b['last_name']} (паспорт № {doc_b}, "
            f"транзитных встреч: {count}, точки пересечения: {points_preview})"
        )
        meetings_per_doc.setdefault(doc_b, []).append(
            f"{info_a['first_name']} {info_a['last_name']} (паспорт № {doc_a}, "
            f"транзитных встреч: {count}, точки пересечения: {points_preview})"
        )

    rows = []
    for doc, contacts in meetings_per_doc.items():
        info = pax_info[doc]
        contacts_str = "; ".join(contacts)
        comment = (
            f"Выявлен в ходе операции «Транзитная передача»: неоднократно пересекался(лась) "
            f"в одних и тех же аэропортах в одни и те же даты со связными при полном отсутствии "
            f"совместных перелетов (0 общих рейсов), что указывает на тайные встречи в транзитных "
            f"зонах для передачи разведданных. Зафиксированные контакты: {contacts_str}."
        )
        rows.append(
            {
                "document_number": doc,
                "first_name": info["first_name"],
                "last_name": info["last_name"],
                "birth_date": info["birth_date"],
                "comment": comment,
            }
        )

    return pd.DataFrame(rows)


def main():
    print(f"Загрузка базы данных: {DATASET_PATH} ...")
    start = time.time()
    df = pd.read_csv(DATASET_PATH, dtype=str, low_memory=False)
    df.columns = df.columns.str.strip()
    print(f"Загружено записей: {len(df):,} за {time.time() - start:.2f} сек.")

    print("\nЗапуск операции «Транзитная передача» (Встречи в хабах без совместных полетов)...")
    start_calc = time.time()
    result_df = detect_transit_exchanges(df, min_meetings=MIN_MEETINGS)
    print(f"Анализ завершен за {time.time() - start_calc:.2f} сек.")

    if result_df.empty:
        print("Подозрительных транзитных передач не найдено.")
        return

    result_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    print(f"✅ Найдено агентов транзитной передачи: {len(result_df)}. Сохранено в '{OUTPUT_CSV}'.")


if __name__ == "__main__":
    main()
