import pandas as pd
import time
from konon_anal.dual_identity import detect_dual_identities

#TODO: ты уже знаешь :)
DATASET_PATH = "/home/daniil/DataScience/MASTER_AIRLINES_DB_sorted.csv"


def main():
    print(f"Загрузка базы данных: {DATASET_PATH} ...")
    start = time.time()
    df = pd.read_csv(DATASET_PATH, dtype=str)
    print(f"Загружено записей: {len(df):,} за {time.time() - start:.2f} сек.")

    print("\n" + "=" * 70)
    print("ОПЕРАЦИЯ «ДВОЙНОЕ ДНО» (Поиск агентов с двумя паспортами под одной картой)")
    print("=" * 70)

    start_calc = time.time()
    spies, legals = detect_dual_identities(df)
    elapsed = time.time() - start_calc

    print(f"\nАнализ завершен за {elapsed:.2f} сек!")
    print(f"Всего выявлено легальных граждан (РФ + Загран): {len(legals):,}")
    print(f"ВЫЯВЛЕНО ШПИОНОВ С АНОМАЛЬНЫМИ ДОКУМЕНТАМИ: {len(spies):,}")
    print("-" * 80)

    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.width', 1000)
    print(spies.head(25).to_string(index=False))

    output_path = "/home/daniil/DataScience/parsed_data/spies_dual_identities.csv"
    spies.to_csv(output_path, index=False, encoding='utf-8')
    print(f"\nСписок 343 шпионов сохранен в: {output_path}")


if __name__ == "__main__":
    main()