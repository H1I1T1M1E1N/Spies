import pandas as pd
import time
from konon_anal.shadow_matrix import detect_shadow_companions

#TODO: ВОВА, СЮДА ВСТАВЬ СВОЙ ПУТЬ!!
DATASET_PATH = "../MASTER_AIRLINES_DB_sorted.csv"

def main():
    print(f"Загрузка базы данных: {DATASET_PATH} ...")
    start = time.time()
    df = pd.read_csv(DATASET_PATH, dtype=str)
    print(f"Загружено записей: {len(df):,} за {time.time() - start:.2f} сек.")

    print("\n" + "=" * 70)
    print("ЗАДАНИЕ 3: ОПЕРАЦИЯ «ТЕНЬ» (Линейная Алгебра / Scipy Sparse)")
    print("=" * 70)
    
    start_calc = time.time()
    # ТЗ: летали вместе более 3 раз (то есть >= 4)
    shadow_pairs = detect_shadow_companions(df, min_shared=4)
    elapsed_calc = time.time() - start_calc

    print(f"\nАнализ 4.4 млн строк через матрицы завершен за {elapsed_calc:.2f} сек!")

    if shadow_pairs.empty:
        print("Скрытых попутчиков (>= 4 совместных рейсов на разных бронях) не найдено.")
        return

    print(f"\nНАЙДЕНО ПОДОЗРИТЕЛЬНЫХ ПАР: {len(shadow_pairs)}")
    print("-" * 70)
    # Выводим топ-20 самых подозрительных пар
    print(shadow_pairs.head(20).to_string(index=False))

if __name__ == "__main__":
    main()