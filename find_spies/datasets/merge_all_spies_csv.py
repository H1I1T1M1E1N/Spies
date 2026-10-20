import glob
import os
import pandas as pd

OUTPUT_FINAL_CSV = "FINAL_SPIES_DOSSIER.csv"

# Полный список всех возможных CSV-файлов от отдельных скриптов
CSV_FILES = [
    "spies_stolen_passports.csv",
    "spies_world_events.csv",
    "spies_dual_identities.csv",
    "spies_teleports.csv",
    "spies_eternal_transit.csv",
    "spies_surveillance_tails.csv",
    "spies_shared_loyalty.csv",
    "spies_shadow_companions.csv",
    "spies_transit_exchange.csv",
    "spies_couriers_turnaround.csv",
    "spies_stealth_iqr.csv",
    "spies_mutation_aliases.csv",     
    "spies_pendulum_couriers.csv",
]

def main():
    loaded_dfs = []
    for file_path in CSV_FILES:
        if os.path.exists(file_path):
            df = pd.read_csv(file_path, dtype=str)
            df["source_file"] = file_path
            loaded_dfs.append(df)
            print(f"✔ Загружен '{file_path}': {len(df)} записей")
        else:
            print(f"⚠ Файл '{file_path}' пока не найден (пропущен)")

    if not loaded_dfs:
        print("❌ Нет ни одного сгенерированного CSV файла для объединения.")
        return

    all_spies = pd.concat(loaded_dfs, ignore_index=True)

    # Нормализация ключевых полей
    all_spies["document_number"] = (
        all_spies["document_number"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
    )
    all_spies["first_name"] = all_spies["first_name"].astype(str).str.strip()
    all_spies["last_name"] = all_spies["last_name"].astype(str).str.strip()
    all_spies["birth_date"] = all_spies["birth_date"].fillna("Неизвестно").astype(str).str.strip()
    all_spies["comment"] = all_spies["comment"].fillna("").astype(str).str.strip()

    # Функция выбора наиболее полной даты рождения
    def pick_best_birth_date(series: pd.Series) -> str:
        valid = [v for v in series if v not in ("", "Неизвестно", "nan", "None")]
        return valid[0] if valid else "Неизвестно"

    # Группируем по паспорту и ФИО
    merged_dossier = (
        all_spies.groupby(["document_number", "first_name", "last_name"], as_index=False)
        .agg(
            birth_date=("birth_date", pick_best_birth_date),
            anomalies_count=("source_file", "nunique"), # Считаем количество сработавших критериев!
            comment=("comment", lambda comments: " ".join(list(dict.fromkeys(c for c in comments if c)))),
        )
    )
    
    # СОРТИРОВКА: Сначала по количеству аномалий (по убыванию), затем по фамилии (по алфавиту)
    merged_dossier = merged_dossier.sort_values(by=["anomalies_count", "last_name"], ascending=[False, True]).reset_index(drop=True)

    # Сохраняем итоговый CSV
    final_output = merged_dossier[
        ["anomalies_count", "document_number", "first_name", "last_name", "birth_date", "comment"]
    ]
    final_output.to_csv(OUTPUT_FINAL_CSV, index=False, encoding="utf-8")

    print("\n" + "=" * 75)
    print(f"✅ ИТОГОВОЕ ДОСЬЕ СФОРМИРОВАНО: '{OUTPUT_FINAL_CSV}'")
    print(f"Всего уникальных подозреваемых: {len(final_output)}")
    
    # Вывод Топ-шпионов прямо в консоль
    print("\n🏆 ТОП-5 ГЛАВНЫХ ПОДОЗРЕВАЕМЫХ (Максимум совпадений):")
    top_spies = final_output.head(5)
    for i, row in top_spies.iterrows():
        print(f"{i+1}. {row['first_name']} {row['last_name']} (Паспорт: {row['document_number']}) — Аномалий: {row['anomalies_count']}")
    
    print("=" * 75)


if __name__ == "__main__":
    main()
