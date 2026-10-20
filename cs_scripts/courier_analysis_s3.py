import time
import pandas as pd
from konon_anal.turnaround_flights import detect_couriers_graph

# Укажи точный путь к общему датасету команды
DATASET_PATH = "../MASTER_AIRLINES_DB_sorted.csv"


def main():
    print(f"Загрузка данных из: {DATASET_PATH} ...")
    start_load = time.time()
    
    # Читаем данные строковыми типами, чтобы избежать потерь нулей в паспортах
    df = pd.read_csv(DATASET_PATH, dtype=str)
    print(f"Загружено записей: {len(df):,} за {time.time() - start_load:.2f} сек.")

    print("\nЗапуск графового анализа операций 'Курьер'...")
    start_analysis = time.time()
    
    top_couriers = detect_couriers_graph(df, top_n=15)
    
    elapsed = time.time() - start_analysis
    print(f"Анализ завершен за {elapsed:.2f} сек.\n")

    if top_couriers.empty:
        print("Подозрительных курьеров не обнаружено.")
        return

    print("=" * 80)
    print("ТОП-15 ПОДОЗРИТЕЛЬНЫХ КУРЬЕРОВ (БЫСТРЫЕ РАЗВОРОТЫ ТУДА-ОБРАТНО)")
    print("=" * 80)
    print(top_couriers.to_string(index=False))

    # Экспорт результатов для отчета
    output_report = "../top_couriers_report.csv"
    top_couriers.to_csv(output_report, index=False, encoding='utf-8')
    print(f"\nОтчет сохранен в: {output_report}")

if __name__ == "__main__":
    main()