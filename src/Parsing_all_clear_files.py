
import pandas as pd
import numpy as np

print("Начинаем процесс слияния баз данных...")

# Наш золотой стандарт
TARGET_COLUMNS = [
    'first_name', 'last_name', 'birth_date', 'document_number', 'flight_date', 
    'flight_number', 'departure', 'arrival', 'pnr', 'ticket_number', 'ff_number'
]

def enforce_standard(df, name):
    # Добавляем пустые колонки, если их нет
    for col in TARGET_COLUMNS:
        if col not in df.columns:
            df[col] = np.nan
    
    # Отсекаем лишние колонки и выстраиваем в правильном порядке
    df_clean = df[TARGET_COLUMNS].copy()
    print(f"Файл '{name}' успешно приведен к формату 11 колонок.")
    return df_clean

def merge_all_files(
    boarding_path: str,
    sirena_path: str,
    loyalty_path: str,
    timetable_path: str,
    logs_path: str,
    output_path: str
) -> pd.DataFrame:
    # 1. Загружаем файлы Студента 1
    df_boarding = pd.read_csv(boarding_path, low_memory=False)
    df_sirena = pd.read_csv(sirena_path, low_memory=False)

    # 2. Загружаем файл Студента 2 (Лояльность) - добавили low_memory=False чтобы убрать Warning
    df_loyalty = pd.read_csv(loyalty_path, low_memory=False)

    # 3. Загружаем файлы Студента 3 (Расписание / Логи)
    df_timetable = pd.read_csv(timetable_path, low_memory=False)
    df_logs = pd.read_csv(logs_path, low_memory=False)

    # --- ВАЖНО: Исправляем файлы Студента 3 на лету ---
    df_timetable = enforce_standard(df_timetable, "Расписание (Student 3)")
    df_logs = enforce_standard(df_logs, "Логи XML (Student 3)")

    # 4. СЛИЯНИЕ (Конкатенация)
    print("Склеиваем файлы вместе...")
    all_dataframes = [df_boarding, df_sirena, df_loyalty, df_timetable, df_logs]
    df_master = pd.concat(all_dataframes, ignore_index=True)

    # 5. Очистка после слияния
    initial_rows = len(df_master)
    df_master = df_master.drop_duplicates()
    final_rows = len(df_master)
    print(f"Удалено {initial_rows - final_rows} дубликатов.")

    # 6. Сохраняем финальную Мастер-таблицу РЯДОМ со скриптом
    df_master.to_csv(output_path, index=False, encoding='utf-8')

    print(f"✅ Успех! Мастер-таблица сохранена: {output_path}")
    print(f"Всего записей в итоговой базе: {final_rows}")
    print("Превью данных:")
    print(df_master.head())
    return df_master
