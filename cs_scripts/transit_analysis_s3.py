import pandas as pd
import time
from konon_anal.transit_exchange import detect_transit_exchanges

#TODO: ВОВА, СЮДА СВОЙ ПУТЬ
DATASET_PATH = "../MASTER_AIRLINES_DB_sorted.csv"

def main():
    print(f"Загрузка базы данных: {DATASET_PATH} ...")
    start = time.time()
    df = pd.read_csv(DATASET_PATH, dtype=str)
    print(f"Загружено записей: {len(df):,} за {time.time() - start:.2f} сек.")

    print("\n" + "=" * 70)
    print("ИДЕЯ 3: ОПЕРАЦИЯ «ТРАНЗИТНАЯ ПЕРЕДАЧА» (Встречи в хабах без полетов)")
    print("=" * 70)
    
    start_calc = time.time()
    # Ищем тех, кто "случайно" пересекался в аэропортах минимум 4 раза
    spy_pairs = detect_transit_exchanges(df, min_meetings=4)
    elapsed_calc = time.time() - start_calc

    print(f"\nАнализ транзитных встреч по 4.4 млн строк завершен за {elapsed_calc:.2f} сек!")

    if spy_pairs.empty:
        print("Подозрительных транзитных передач не найдено.")
        return
    
    print(f"\nНАЙДЕНО АГЕНТУРНЫХ ПАР (Встречи без совместных перелетов): {len(spy_pairs)}")
    print("-" * 70)
    print(spy_pairs.head(20).to_string(index=False))

if __name__ == "__main__":
    main()