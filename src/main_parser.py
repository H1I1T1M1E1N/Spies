import os
import sys
import time
from pathlib import Path

# Импорт парсеров
from parser_s1_boarding import parse_boarding_data
from parser_s1_sirena import parse_sirena
from parser_s2 import parse_student2
from parser_s3 import S3DataPipeline
from Parsing_all_clear_files import merge_all_files
from Clear_ds import clean_master_db
from Sort_ds import sort_master_db


def get_resource_path(relative_path):
    """Получить абсолютный путь к ресурсу (работает и в dev, и в EXE)."""
    try:
        base_path = os.path.dirname(sys.executable)
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def main():
    print("=" * 70)
    print(" ️  ПАРСИНГ И ПОДГОТОВКА МАСТЕР-БАЗЫ ДАННЫХ  🛠️ ")
    print("=" * 70)

    # === НАСТРОЙКА ПУТЕЙ ===
    # Измените эти пути под вашу структуру
    BASE_DIR = get_resource_path(".")
    INPUT_DIR = os.path.join(BASE_DIR, "input_data")  # Папка с сырыми данными
    OUTPUT_DIR = os.path.join(BASE_DIR, "datasets")  # Папка для результатов

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Входные файлы
    BOARDING_CSV = os.path.join(INPUT_DIR, "BoardingData.csv")
    SIRENA_TAB = os.path.join(INPUT_DIR, "Sirena-export-fixed.tab")
    FORUM_JSON = os.path.join(INPUT_DIR, "FrequentFlyerForum-Profiles.json")
    SKYTEAM_YAML = os.path.join(INPUT_DIR, "SkyTeam-Exchange.yaml")
    BOARDING_FOLDER = os.path.join(INPUT_DIR, "YourBoardingPassDotAero")
    XML_FILE = os.path.join(INPUT_DIR, "PointzAggregator-AirlinesData.xml")
    PDF_FILE = os.path.join(INPUT_DIR, "Skyteam_Timetable.pdf")

    # Промежуточные файлы
    BOARDING_CLEAN = os.path.join(OUTPUT_DIR, "student1_boarding_clean.csv")
    SIRENA_CLEAN = os.path.join(OUTPUT_DIR, "student1_sirena_clean.csv")
    LOYALTY_CSV = os.path.join(OUTPUT_DIR, "student2_loyalty.csv")
    FLIGHTS_CSV = os.path.join(OUTPUT_DIR, "flights_data.csv")
    TIMETABLE_CSV = os.path.join(OUTPUT_DIR, "timetable_reference.csv")

    # Финальные файлы
    MASTER_DB = os.path.join(OUTPUT_DIR, "MASTER_AIRLINES_DB.csv")
    MASTER_DB_SORTED = os.path.join(OUTPUT_DIR, "MASTER_AIRLINES_DB_sorted.csv")

    # Проверка входных файлов
    required_files = [
        BOARDING_CSV, SIRENA_TAB, FORUM_JSON, SKYTEAM_YAML,
        BOARDING_FOLDER, XML_FILE, PDF_FILE
    ]

    missing = [f for f in required_files if not os.path.exists(f)]
    if missing:
        print("❌ ОШИБКА: Не найдены следующие файлы/папки:")
        for f in missing:
            print(f"   - {f}")
        print("\nСоздайте папку 'input_data' рядом с программой и поместите туда все сырые данные.")
        input("Нажмите Enter для выхода...")
        return

    start_total = time.time()

    # === ЭТАП 1: ПАРСИНГ СЫРЫХ ДАННЫХ ===
    print("\n" + "=" * 70)
    print("📥 ЭТАП 1: ПАРСИНГ СЫРЫХ ДАННЫХ")
    print("=" * 70)

    # Student 1
    parse_boarding_data(BOARDING_CSV, BOARDING_CLEAN)
    parse_sirena(SIRENA_TAB, SIRENA_CLEAN)

    # Student 2
    df_student2 = parse_student2(FORUM_JSON, SKYTEAM_YAML, BOARDING_FOLDER)
    df_student2.to_csv(LOYALTY_CSV, index=False, encoding='utf-8')
    print(f"✅ Student 2 сохранён: {LOYALTY_CSV}")

    # Student 3
    s3_pipeline = S3DataPipeline(
        xml_path=XML_FILE,
        pdf_path=PDF_FILE,
        output_dir=OUTPUT_DIR
    )
    s3_pipeline.execute_all()

    # === ЭТАП 2: ОБЪЕДИНЕНИЕ ===
    print("\n" + "=" * 70)
    print(" ЭТАП 2: ОБЪЕДИНЕНИЕ ВСЕХ БАЗ")
    print("=" * 70)

    merge_all_files(
        boarding_path=BOARDING_CLEAN,
        sirena_path=SIRENA_CLEAN,
        loyalty_path=LOYALTY_CSV,
        timetable_path=TIMETABLE_CSV,
        logs_path=FLIGHTS_CSV,
        output_path=MASTER_DB
    )

    # === ЭТАП 3: ОЧИСТКА ===
    print("\n" + "=" * 70)
    print("🧹 ЭТАП 3: ОЧИСТКА ОТ ДУБЛИКАТОВ")
    print("=" * 70)

    clean_master_db(MASTER_DB, MASTER_DB)

    # === ЭТАП 4: СОРТИРОВКА ===
    print("\n" + "=" * 70)
    print("📊 ЭТАП 4: СОРТИРОВКА")
    print("=" * 70)

    sort_master_db(MASTER_DB, MASTER_DB_SORTED)

    # === ИТОГ ===
    print("\n" + "=" * 70)
    print(f"🎉 ПАРСИНГ ЗАВЕРШЁН! Общее время: {time.time() - start_total:.2f} сек.")
    print(f"📁 Итоговый файл: {MASTER_DB_SORTED}")
    print("=" * 70)
    input("Нажмите Enter для выхода...")


if __name__ == "__main__":
    main()