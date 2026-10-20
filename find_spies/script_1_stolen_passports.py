import pandas as pd

DATASET_PATH = "datasets/MASTER_AIRLINES_DB_sorted.csv"
OUTPUT_CSV = "datasets/spies_stolen_passports.csv"


def clean_doc_series(series: pd.Series) -> pd.Series:
    return series.astype(str).str.replace(r"\.0$", "", regex=True).str.strip()


def analyze_stolen_passports(df: pd.DataFrame):
    print("🕵️ Проверка безопасности: Поиск одинаковых паспортов у разных людей...")

    df_valid = df.dropna(subset=["document_number", "first_name", "last_name"]).copy()
    df_valid["document_number"] = clean_doc_series(df_valid["document_number"])
    df_valid = df_valid[~df_valid["document_number"].isin(["", "nan", "None"])]

    df_valid["birth_date"] = df_valid["birth_date"].fillna("Неизвестно")

    # Уникальные личности (Паспорт + Имя + Фамилия + Дата рождения)
    unique_identities = df_valid[
        ["document_number", "first_name", "last_name", "birth_date"]
    ].drop_duplicates()

    # Считаем количество уникальных людей на один номер паспорта
    passport_counts = unique_identities["document_number"].value_counts()
    suspicious_passports = passport_counts[passport_counts > 1].index

    if len(suspicious_passports) == 0:
        print("✅ Одинаковых паспортов у разных людей не обнаружено.")
        return

    suspects_df = unique_identities[
        unique_identities["document_number"].isin(suspicious_passports)
    ].copy()

    # Формируем словарь: паспорт -> список всех ФИО, которые его используют
    doc_to_people = (
        suspects_df.groupby("document_number")
        .apply(
            lambda g: [
                f"{r['first_name']} {r['last_name']} (д.р. {r['birth_date']})"
                for _, r in g.iterrows()
            ]
        )
        .to_dict()
    )

    def build_comment(row):
        doc = row["document_number"]
        current_person = f"{row['first_name']} {row['last_name']} (д.р. {row['birth_date']})"
        others = [p for p in doc_to_people.get(doc, []) if p != current_person]
        others_str = ", ".join(others)
        return (
            f"Использует скомпрометированный или клонированный паспорт № {doc}, "
            f"по которому также летали другие лица ({others_str}), что является прямым признаком "
            f"использования поддельных документов или работы под прикрытием."
        )

    suspects_df["comment"] = suspects_df.apply(build_comment, axis=1)
    result_df = suspects_df[
        ["document_number", "first_name", "last_name", "birth_date", "comment"]
    ].sort_values(by=["document_number", "last_name"])

    result_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    print(f"🚨 Найдено записей: {len(result_df)}. Отчет сохранен в '{OUTPUT_CSV}'.")

def main():
    df = pd.read_csv(DATASET_PATH, dtype=str, low_memory=False)
    df.columns = df.columns.str.strip()
    analyze_stolen_passports(df)

if __name__ == "__main__":
    main()
