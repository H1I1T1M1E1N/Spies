# run_loyalty_analysis.py
import pandas as pd
import time
from konon_anal.shared_loyalty import detect_shared_loyalty_cards

DATASET_PATH = "/home/daniil/DataScience/MASTER_AIRLINES_DB_sorted.csv"


def main():
    print(f"Загрузка базы данных: {DATASET_PATH} ...")
    start = time.time()
    df = pd.read_csv(DATASET_PATH, dtype=str)
    print(f"Загружено записей: {len(df):,} за {time.time() - start:.2f} сек.")

    print("\n" + "=" * 80)
    print("ОПЕРАЦИЯ «ОБЩАК»: ПОИСК КОЛЛЕКТИВНЫХ КАРТ ЛОЯЛЬНОСТИ И СВЯЗНЫХ НА ФОРУМЕ")
    print("=" * 80)

    start_calc = time.time()
    results = detect_shared_loyalty_cards(df, min_passengers=2)
    elapsed = time.time() - start_calc

    print(f"Анализ завершен за {elapsed:.2f} сек!\n")

    if results.empty:
        print("Коллективных карт не найдено.")
        return

    print("ВЫЯВЛЕНА ЗАКОНСПИРИРОВАННАЯ АГЕНТУРНАЯ СВЯЗКА:")
    print("-" * 80)
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.width', 1000)
    print(results.to_string(index=False))

    output_path = "/home/daniil/DataScience/parsed_data/shared_loyalty_investigation.csv"
    results.to_csv(output_path, index=False, encoding='utf-8')
    print(f"\nОтчет сохранен в: {output_path}")


if __name__ == "__main__":
    main()