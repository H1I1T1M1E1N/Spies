import pandas as pd
import time
from typing import Set

DATASET_PATH = "datasets/MASTER_AIRLINES_DB_sorted.csv"
OUTPUT_CSV = "datasets/spies_dual_identities.csv"


class PassportPairClassifier:
    """Классифицирует связку документов: легальная (РФ 10 знаков + Загран 9 знаков) или аномальная."""

    @staticmethod
    def is_anomalous_pair(doc_lengths: Set[int]) -> bool:
        if doc_lengths == {9, 10}:
            return False
        return True


def detect_dual_identities(df: pd.DataFrame) -> pd.DataFrame:
    work_df = df.dropna(subset=["ff_number", "document_number"]).copy()

    work_df["clean_ff"] = work_df["ff_number"].astype(str).str.extract(r"(\d{6,})")[0]
    work_df["clean_doc"] = (
        work_df["document_number"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
    )
    work_df["birth_date"] = work_df["birth_date"].fillna("Неизвестно")

    work_df = work_df[~work_df["clean_doc"].isin(["", "nan", "None"])].copy()
    work_df = work_df.dropna(subset=["clean_ff"])
    work_df["doc_len"] = work_df["clean_doc"].str.len()

    # Группировка по номеру карты лояльности
    grouped = (
        work_df.groupby("clean_ff")
        .agg(
            unique_docs=("clean_doc", lambda d: sorted(list(set(d)))),
            doc_lengths=("doc_len", lambda l: sorted(list(set(l)))),
            total_flights=("flight_date", "count"),
            first_name=("first_name", "first"),
            last_name=("last_name", "first"),
            birth_date=("birth_date", "first"),
        )
        .reset_index()
    )

    multi_doc = grouped[grouped["unique_docs"].apply(len) > 1].copy()
    classifier = PassportPairClassifier()

    multi_doc["is_spy"] = multi_doc["doc_lengths"].apply(
        lambda l_set: classifier.is_anomalous_pair(set(l_set))
    )

    spies_df = multi_doc[multi_doc["is_spy"]].copy()
    if spies_df.empty:
        return pd.DataFrame()

    def describe_type(lengths):
        if lengths == [9]:
            return "два загранпаспорта (по 9 цифр)"
        elif lengths == [10]:
            return "два внутренних паспорта РФ (по 10 цифр)"
        else:
            return f"нестандартная комбинация паспортов (длины номеров: {lengths})"

    rows = []
    for _, row in spies_df.iterrows():
        docs_list = row["unique_docs"]
        ptype_desc = describe_type(row["doc_lengths"])
        ff_num = row["clean_ff"]
        flights_cnt = row["total_flights"]

        for doc in docs_list:
            other_docs = [d for d in docs_list if d != doc]
            other_str = ", ".join(other_docs)
            comment = (
                f"Выявлен в ходе операции «Двойное дно»: на одну карту лояльности № {ff_num} "
                f"зарегистрирована аномальная связка документов ({ptype_desc}: текущий паспорт № {doc} "
                f"и дополнительный паспорт № {other_str}), по которым суммарно совершено {flights_cnt} перелетов, "
                f"что характерно для оперативника со множественными документами прикрытия."
            )
            rows.append(
                {
                    "document_number": doc,
                    "first_name": row["first_name"],
                    "last_name": row["last_name"],
                    "birth_date": row["birth_date"],
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

    result_df = detect_dual_identities(df)
    if result_df.empty:
        print("Шпионов с аномальными документами не найдено.")
        return

    result_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    print(f"✅ Найдено записей шпионов: {len(result_df)}. Сохранено в '{OUTPUT_CSV}'.")


if __name__ == "__main__":
    main()
