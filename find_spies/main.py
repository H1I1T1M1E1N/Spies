import os
import sys
import time
import warnings
import pandas as pd

warnings.filterwarnings("ignore", category=pd.errors.DtypeWarning)

# Импорт функций анализа из скриптов
from script_1_stolen_passports import analyze_stolen_passports
from script_2_world_events import analyze_world_events
from script_3_dual_identity import detect_dual_identities
from script_4_route_anomalies import analyze_route_anomalies
from script_6_shadow_companions import detect_shadow_companions
from script_7_transit_exchange import detect_transit_exchanges
from script_8_couriers_graph import detect_couriers_graph
from script_9_stealth_iqr import analyze_stealth_iqr
from merge_all_spies_csv import merge_all_spies


def get_resource_path(relative_path):
    """Получить путь к ресурсу — ищет рядом с EXE, а не во временной папке."""
    try:
        base_path = os.path.dirname(sys.executable)
    except Exception:
        # Если запущено как обычный Python скрипт
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


DATASET_PATH = get_resource_path("datasets/MASTER_AIRLINES_DB_sorted.csv")
OUTPUT_DIR = get_resource_path("datasets")


def main():
    print("=" * 70)
    print(" 🕵️  КОМПЛЕКСНЫЙ АНАЛИЗ АВИАПЕРЕЛЁТОВ  🕵️ ")
    print("=" * 70)

    if not os.path.exists(DATASET_PATH):
        print(f"❌ Файл не найден: {DATASET_PATH}")
        print("Поместите папку 'datasets' рядом с программой.")
        input("Нажмите Enter для выхода...")
        return

    print(f"\n⏳ Загрузка данных (1 раз на все анализы): {DATASET_PATH}")
    t0 = time.time()
    df = pd.read_csv(DATASET_PATH, dtype=str, low_memory=False)
    df.columns = df.columns.str.strip()
    print(f"✅ Загружено записей: {len(df):,} за {time.time() - t0:.2f} сек.\n")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # === 1. STOLEN PASSPORTS ===
    print(f"\n{'=' * 70}\n🚀 [1/8  Клонированные паспорта]\n{'=' * 70}")
    try:
        analyze_stolen_passports(df)
    except Exception as e:
        print(f"❌ Ошибка: {e}")

    # === 2. WORLD EVENTS ===
    print(f"\n{'=' * 70}\n🚀 [2/8  Мировые события]\n{'=' * 70}")
    try:
        analyze_world_events(df)
    except Exception as e:
        print(f"❌ Ошибка: {e}")

    # === 3. DUAL IDENTITY ===
    print(f"\n{'=' * 70}\n🚀 [3/8  Двойное дно]\n{'=' * 70}")
    try:
        result_df = detect_dual_identities(df)
        if not result_df.empty:
            output_path = os.path.join(OUTPUT_DIR, "spies_dual_identities.csv")
            result_df.to_csv(output_path, index=False, encoding="utf-8")
            print(f"✅ Сохранено: {len(result_df)} записей в '{output_path}'")
        else:
            print("✅ Аномальных связок не найдено.")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

    # === 4. ROUTE ANOMALIES ===
    print(f"\n{'=' * 70}\n🚀 [4/8  Аномалии маршрутов]\n{'=' * 70}")
    try:
        analyze_route_anomalies(df)
    except Exception as e:
        print(f"❌ Ошибка: {e}")

    # === 5. SHADOW COMPANIONS ===
    print(f"\n{'=' * 70}\n🚀 [5/8  Скрытые попутчики (Тень)]\n{'=' * 70}")
    try:
        result_df = detect_shadow_companions(df, min_shared=4)
        if not result_df.empty:
            output_path = os.path.join(OUTPUT_DIR, "spies_shadow_companions.csv")
            result_df.to_csv(output_path, index=False, encoding="utf-8")
            print(f"✅ Сохранено: {len(result_df)} записей в '{output_path}'")
        else:
            print("✅ Скрытых попутчиков не найдено.")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

    # === 6. TRANSIT EXCHANGE ===
    print(f"\n{'=' * 70}\n🚀 [6/8  Транзитные передачи]\n{'=' * 70}")
    try:
        result_df = detect_transit_exchanges(df, min_meetings=4)
        if not result_df.empty:
            output_path = os.path.join(OUTPUT_DIR, "spies_transit_exchange.csv")
            result_df.to_csv(output_path, index=False, encoding="utf-8")
            print(f"✅ Сохранено: {len(result_df)} записей в '{output_path}'")
        else:
            print("✅ Подозрительных транзитных передач не найдено.")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

    # === 7. COURIERS GRAPH ===
    print(f"\n{'=' * 70}\n🚀 [7/8  Курьеры (граф)]\n{'=' * 70}")
    try:
        result_df = detect_couriers_graph(df, top_n=15)
        if not result_df.empty:
            output_path = os.path.join(OUTPUT_DIR, "spies_couriers_turnaround.csv")
            result_df.to_csv(output_path, index=False, encoding="utf-8")
            print(f"✅ Сохранено: {len(result_df)} записей в '{output_path}'")
        else:
            print("✅ Курьеров не обнаружено.")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

    # === 8. STEALTH IQR ===
    print(f"\n{'=' * 70}\n🚀 [8/8  Stealth IQR]\n{'=' * 70}")
    try:
        plot_path = os.path.join(OUTPUT_DIR, "stealth_iqr_plot.png")
        result_df, threshold = analyze_stealth_iqr(df, plot_path=plot_path, top_n=10)

        print("=" * 70)
        print(f"ПОРОГ АНОМАЛИЙ IQR: > {threshold:.1f} перелетов")
        print("=" * 70)

        if not result_df.empty:
            output_path = os.path.join(OUTPUT_DIR, "spies_stealth_iqr.csv")
            result_df.to_csv(output_path, index=False, encoding="utf-8")
            print(f"✅ Сохранено: {len(result_df)} записей в '{output_path}'")
            print(f"📊 График сохранен в: {plot_path}")
        else:
            print("✅ Аномальных пассажиров не найдено.")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

    # === 9. MERGE ALL SPIES ===
    print(f"\n{'=' * 70}\n📚 [9/9  Формирование итогового досье]\n{'=' * 70}")
    try:
        merge_all_spies(OUTPUT_DIR)
    except Exception as e:
        print(f"❌ Ошибка при объединении: {e}")

    print("\n" + "=" * 70)
    print(f"🎉 АНАЛИЗ ЗАВЕРШЁН!")
    print(f"📁 Результаты в папке: {OUTPUT_DIR}")
    print(f"📋 Итоговое досье: {os.path.join(OUTPUT_DIR, 'FINAL_SPIES_DOSSIER.csv')}")
    print("=" * 70)
    input("Нажмите Enter для выхода...")


if __name__ == "__main__":
    main()