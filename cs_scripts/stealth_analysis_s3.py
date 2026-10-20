import pandas as pd
import time
from konon_anal.stealth_iqr import analyze_stealth_iqr

#TODO: ВОВА, СЮДА СВОИ ПУТИ!
DATASET_PATH = "../MASTER_AIRLINES_DB_sorted.csv"
PLOT_OUTPUT = "../stealth_iqr_plot.png"

def main():
    print(f"Загрузка данных: {DATASET_PATH} ...")
    start = time.time()
    df = pd.read_csv(DATASET_PATH, dtype=str)
    print(f"Загружено записей: {len(df):,} за {time.time() - start:.2f} сек.")

    print("\nЗапуск детекции аномалий через Межквартильный размах (IQR)...")
    top_stealth, threshold = analyze_stealth_iqr(df, plot_path=PLOT_OUTPUT, top_n=10)

    print("=" * 70)
    print(f"ПОРОГ АНОМАЛИЙ IQR: > {threshold:.1f} перелетов")
    print("=" * 70)
    print(top_stealth[['first_name', 'last_name', 'document_number', 'flight_count']].to_string(index=False))
    print(f"\nГрафик сохранен в: {PLOT_OUTPUT}")

if __name__ == "__main__":
    main()