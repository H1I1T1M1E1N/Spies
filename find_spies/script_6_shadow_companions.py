import time
import numpy as np
import pandas as pd
import scipy.sparse as sp

DATASET_PATH = "datasets/MASTER_AIRLINES_DB_sorted.csv"
OUTPUT_CSV = "datasets/spies_shadow_companions.csv"
MIN_SHARED_FLIGHTS = 4


class ScipySparseCalculator:
    @staticmethod
    def build_incidence_matrix(rows_idx, cols_idx, shape) -> sp.csr_matrix:
        data = np.ones(len(rows_idx), dtype=np.int8)
        matrix = sp.csr_matrix((data, (rows_idx, cols_idx)), shape=shape)
        matrix.data = np.clip(matrix.data, 0, 1)
        return matrix

    @staticmethod
    def compute_hidden_connections(
        m_flights: sp.csr_matrix, m_bookings: sp.csr_matrix
    ) -> sp.coo_matrix:
        shared_flights = sp.triu(m_flights.dot(m_flights.T), k=1)
        shared_bookings = sp.triu(m_bookings.dot(m_bookings.T), k=1)
        hidden_connections = shared_flights - shared_bookings
        return hidden_connections.tocoo()


def detect_shadow_companions(df: pd.DataFrame, min_shared: int = 4) -> pd.DataFrame:
    print("Подготовка данных для матричного анализа «Тень»...")
    work_df = df.copy()
    work_df["clean_doc"] = (
        work_df["document_number"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
    )
    work_df["birth_date"] = work_df["birth_date"].fillna("Неизвестно")

    mask_valid = (
        work_df["flight_number"].notna()
        & work_df["flight_date"].notna()
        & work_df["first_name"].notna()
        & work_df["last_name"].notna()
        & (~work_df["clean_doc"].isin(["", "nan", "None"]))
    )
    work_df = work_df[mask_valid].copy()

    work_df["passenger_id"] = work_df["clean_doc"]

    work_df["safe_pnr"] = np.where(
        work_df["pnr"].notna() & (~work_df["pnr"].astype(str).isin(["", "nan", "None"])),
        work_df["pnr"],
        "NO_PNR_" + work_df.index.astype(str),
    )

    pax_codes, pax_uniques = pd.factorize(work_df["passenger_id"])
    flight_codes, flight_uniques = pd.factorize(
        work_df["flight_number"].astype(str) + "_" + work_df["flight_date"].astype(str)
    )
    booking_codes, booking_uniques = pd.factorize(
        work_df["flight_number"].astype(str)
        + "_"
        + work_df["flight_date"].astype(str)
        + "_"
        + work_df["safe_pnr"].astype(str)
    )

    n_passengers = len(pax_uniques)
    calc = ScipySparseCalculator()

    print(f"Построение разреженных матриц [{n_passengers:,} x {len(flight_uniques):,}]...")
    m_flights = calc.build_incidence_matrix(
        pax_codes, flight_codes, (n_passengers, len(flight_uniques))
    )
    m_bookings = calc.build_incidence_matrix(
        pax_codes, booking_codes, (n_passengers, len(booking_uniques))
    )

    print("Умножение матриц C = M * M^T (вычисление скрытых пересечений)...")
    hidden_matrix = calc.compute_hidden_connections(m_flights, m_bookings)

    mask = hidden_matrix.data >= min_shared
    pax_a_idx = hidden_matrix.row[mask]
    pax_b_idx = hidden_matrix.col[mask]
    shared_counts = hidden_matrix.data[mask]

    if len(shared_counts) == 0:
        return pd.DataFrame()

    pax_info = (
        work_df.drop_duplicates(subset=["passenger_id"])
        .set_index("passenger_id")[["first_name", "last_name", "birth_date"]]
        .to_dict("index")
    )

    connections_per_doc = {}
    for a_idx, b_idx, count in zip(pax_a_idx, pax_b_idx, shared_counts):
        doc_a = pax_uniques[a_idx]
        doc_b = pax_uniques[b_idx]
        info_a = pax_info.get(doc_a, {"first_name": "Unknown", "last_name": "Unknown", "birth_date": "Неизвестно"})
        info_b = pax_info.get(doc_b, {"first_name": "Unknown", "last_name": "Unknown", "birth_date": "Неизвестно"})

        connections_per_doc.setdefault(doc_a, []).append(
            f"{info_b['first_name']} {info_b['last_name']} (паспорт № {doc_b}, скрытых совместных перелетов: {count})"
        )
        connections_per_doc.setdefault(doc_b, []).append(
            f"{info_a['first_name']} {info_a['last_name']} (паспорт № {doc_a}, скрытых совместных перелетов: {count})"
        )

    rows = []
    for doc, partners_list in connections_per_doc.items():
        info = pax_info[doc]
        partners_str = "; ".join(partners_list)
        comment = (
            f"Выявлен в ходе операции «Тень»: совершал(а) регулярные скрытые совместные перелеты "
            f"на одних и тех же рейсах, но намеренно оформлял(а) билеты в разные брони (разные PNR) "
            f"для имитации отсутствия связи со следующими лицами: {partners_str}."
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

    result_df = detect_shadow_companions(df, min_shared=MIN_SHARED_FLIGHTS)
    if result_df.empty:
        print("Скрытых попутчиков не найдено.")
        return

    result_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    print(f"✅ Найдено подозреваемых: {len(result_df)}. Сохранено в '{OUTPUT_CSV}'.")


if __name__ == "__main__":
    main()
