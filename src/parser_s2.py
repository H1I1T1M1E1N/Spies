import json
import yaml
import pandas as pd
import numpy as np
import re
import os
from pathlib import Path


# ============================================================
# 1. Парсинг FrequentFlyerForum-Profiles.json
# ============================================================
def parse_forum_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    rows = []
    for profile in data.get("Forum Profiles", []):
        real_name = profile.get("Real Name", {})
        first_name = real_name.get("First Name")
        last_name = real_name.get("Last Name")

        if first_name:
            first_name = str(first_name).upper().strip()
        if last_name:
            last_name = str(last_name).upper().strip()

        ff_number = np.nan
        loyalty_list = profile.get("Loyality Programm", [])
        if loyalty_list and len(loyalty_list) > 0:
            prog = loyalty_list[0].get("programm", "")
            num = loyalty_list[0].get("Number", "")
            if prog and num:
                ff_number = f"{prog} {str(num).strip()}"

        for flight in profile.get("Registered Flights", []):
            dep_airport = flight.get("Departure", {}).get("Airport", "")
            arr_airport = flight.get("Arrival", {}).get("Airport", "")

            rows.append({
                'first_name': first_name if first_name else np.nan,
                'last_name': last_name if last_name else np.nan,
                'flight_date': flight.get("Date", np.nan),
                'flight_number': flight.get("Flight", np.nan),
                'departure': dep_airport[:3].upper() if dep_airport else np.nan,
                'arrival': arr_airport[:3].upper() if arr_airport else np.nan,
                'pnr': np.nan,
                'ticket_number': np.nan,
                'ff_number': ff_number
            })

    return pd.DataFrame(rows)


# ============================================================
# 2. Парсинг SkyTeam-Exchange.yaml
# ============================================================
def parse_skyteam_yaml(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        yaml_data = yaml.safe_load(f)

    rows = []
    for date, flights in yaml_data.items():
        for flight_num, details in flights.items():
            departure = details.get('FROM', '')
            arrival = details.get('TO', '')

            ff_dict = details.get('FF', {})
            if ff_dict:
                for ff_number_raw, pax_info in ff_dict.items():
                    ff_number_clean = re.sub(r'\s+', ' ', str(ff_number_raw).strip())
                    rows.append({
                        'first_name': np.nan,
                        'last_name': np.nan,
                        'flight_date': str(date),
                        'flight_number': str(flight_num),
                        'departure': str(departure)[:3].upper() if departure else np.nan,
                        'arrival': str(arrival)[:3].upper() if arrival else np.nan,
                        'pnr': np.nan,
                        'ticket_number': np.nan,
                        'ff_number': ff_number_clean
                    })
            else:
                rows.append({
                    'first_name': np.nan,
                    'last_name': np.nan,
                    'flight_date': str(date),
                    'flight_number': str(flight_num),
                    'departure': str(departure)[:3].upper() if departure else np.nan,
                    'arrival': str(arrival)[:3].upper() if arrival else np.nan,
                    'pnr': np.nan,
                    'ticket_number': np.nan,
                    'ff_number': np.nan
                })

    return pd.DataFrame(rows)


# ============================================================
# 3. Парсинг Excel-файлов из папки (вместо ZIP)
# ============================================================
def parse_boarding_folder(folder_path):
    """
    folder_path — путь к папке с распакованными .xlsx файлами.
    Функция рекурсивно обходит папку и читает все .xlsx файлы.
    """
    all_rows = []
    folder = Path(folder_path)

    # Рекурсивно ищем все .xlsx файлы, игнорируем временные файлы Excel (~$...)
    xlsx_files = [f for f in folder.rglob('*.xlsx') if not f.name.startswith('~$')]
    print(f"Найдено .xlsx файлов: {len(xlsx_files)}")

    for file_path in xlsx_files:
        try:
            # Читаем все листы без заголовков
            sheets = pd.read_excel(file_path, sheet_name=None, header=None, engine='openpyxl')

            for sheet_name, df in sheets.items():
                try:
                    # Проверяем, что это действительно boarding pass (есть нужные ячейки)
                    if df.shape[0] < 13 or df.shape[1] < 9:
                        continue

                    # Имя: ячейка A3 (индекс [2, 0])
                    name_raw = str(df.iloc[2, 0]) if pd.notna(df.iloc[2, 0]) else ""
                    # Убираем титулы MR/MRS/MS/DR
                    name_clean = re.sub(r'^(MR|MRS|MS|DR)\.?\s*', '', name_raw, flags=re.IGNORECASE).strip().upper()
                    name_parts = name_clean.split()
                    first_name = name_parts[0] if len(name_parts) > 0 else np.nan
                    last_name = name_parts[1] if len(name_parts) > 1 else np.nan

                    # Рейс: A5 ([4, 0])
                    flight_number = str(df.iloc[4, 0]).strip() if pd.notna(df.iloc[4, 0]) else np.nan

                    # Откуда: E7 ([6, 4]), Куда: I7 ([6, 8])
                    departure = str(df.iloc[6, 4]).strip()[:3].upper() if pd.notna(df.iloc[6, 4]) else np.nan
                    arrival = str(df.iloc[6, 8]).strip()[:3].upper() if pd.notna(df.iloc[6, 8]) else np.nan

                    # Дата: A9 ([8, 0]) — формат "2017-01-03/09:35"
                    date_raw = str(df.iloc[8, 0]) if pd.notna(df.iloc[8, 0]) else ""
                    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', date_raw)
                    flight_date = date_match.group(1) if date_match else np.nan

                    # PNR: B13 ([12, 1])
                    pnr = str(df.iloc[12, 1]).strip() if pd.notna(df.iloc[12, 1]) else np.nan

                    # Ticket: F13 ([12, 5]) — читаем как строку
                    ticket_number = str(df.iloc[12, 5]).strip() if pd.notna(df.iloc[12, 5]) else np.nan

                    # FF number: F3 ([2, 5]) — но там может быть класс обслуживания (Y/P/A/J)
                    ff_number = np.nan
                    if pd.notna(df.iloc[2, 5]):
                        ff_raw = str(df.iloc[2, 5]).strip()
                        # FF number имеет формат "XX 123456789" (2 буквы + пробел + цифры)
                        # Класс обслуживания — это одна буква (Y, P, A, J)
                        if re.match(r'^[A-Z]{2}\s+\d+$', ff_raw):
                            ff_number = ff_raw
                        elif re.match(r'^[A-Z]{2}\s+\d+\s*$', ff_raw):
                            ff_number = ff_raw

                    all_rows.append({
                        'first_name': first_name,
                        'last_name': last_name,
                        'flight_date': flight_date,
                        'flight_number': flight_number,
                        'departure': departure,
                        'arrival': arrival,
                        'pnr': pnr,
                        'ticket_number': ticket_number,
                        'ff_number': ff_number
                    })
                except Exception as e:
                    print(f"  Ошибка в файле {file_path.name}, лист {sheet_name}: {e}")
        except Exception as e:
            print(f"Ошибка чтения файла {file_path}: {e}")

    return pd.DataFrame(all_rows)

def parse_skyteam_yaml_fast(filepath):
    """
    Быстрый построчный парсер YAML без использования yaml-библиотеки.
    Работает в десятки раз быстрее yaml.safe_load() для больших файлов.
    """
    rows = []
    current_date = None
    current_flight = None
    current_from = None
    current_to = None
    current_ff_numbers = []

    def flush_flight():
        """Сохраняем собранные данные о рейсе в список строк."""
        nonlocal current_ff_numbers
        if current_flight and current_date:
            if current_ff_numbers:
                for ff in current_ff_numbers:
                    rows.append({
                        'first_name': np.nan,
                        'last_name': np.nan,
                        'flight_date': current_date,
                        'flight_number': current_flight,
                        'departure': current_from if current_from else np.nan,
                        'arrival': current_to if current_to else np.nan,
                        'pnr': np.nan,
                        'ticket_number': np.nan,
                        'ff_number': ff
                    })
            else:
                # Рейс без FF (если такое бывает)
                rows.append({
                    'first_name': np.nan,
                    'last_name': np.nan,
                    'flight_date': current_date,
                    'flight_number': current_flight,
                    'departure': current_from if current_from else np.nan,
                    'arrival': current_to if current_to else np.nan,
                    'pnr': np.nan,
                    'ticket_number': np.nan,
                    'ff_number': np.nan
                })
        current_ff_numbers = []

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            stripped = line.rstrip()
            if not stripped or stripped == '---':
                continue

            # Определяем уровень вложенности по отступам
            indent = len(line) - len(line.lstrip())
            content = stripped.strip()

            # === Уровень 0: дата (например, '2017-01-01':) ===
            if indent == 0:
                flush_flight()
                current_date = content.strip("'\"").rstrip(':').strip()
                current_flight = None
                current_from = None
                current_to = None

            # === Уровень 2: номер рейса (например, AF1145:) ===
            elif indent == 2:
                if content.endswith(':') and content != 'FF:':
                    flush_flight()
                    current_flight = content.rstrip(':').strip()
                    current_from = None
                    current_to = None

            # === Уровень 4: FROM / TO / STATUS / FF ===
            elif indent == 4:
                if content == 'FF:':
                    pass  # просто маркер начала блока FF
                elif content.startswith('FROM:'):
                    val = content.split(':', 1)[1].strip()
                    current_from = val[:3].upper() if val else np.nan
                elif content.startswith('TO:'):
                    val = content.split(':', 1)[1].strip()
                    current_to = val[:3].upper() if val else np.nan
                # STATUS можно игнорировать — он не нужен в выходном DataFrame

            # === Уровень 6: FF-номера (например, FB 520518073: {...}) ===
            elif indent == 6 and ':' in content:
                ff_key = content.split(':', 1)[0].strip()
                # Нормализуем пробелы: "FB  520518073" → "FB 520518073"
                ff_number = re.sub(r'\s+', ' ', ff_key)
                current_ff_numbers.append(ff_number)

    # Не забываем "сбросить" последний рейс в файле
    flush_flight()

    print(f"  Спарсено {len(rows)} строк из YAML")
    return pd.DataFrame(rows)


import os
from pathlib import Path
from openpyxl import load_workbook
import csv
import re


def parse_boarding_folder_fast(folder_path):
    """
    Быстрый парсер Excel-файлов из папки.
    Читает напрямую через openpyxl, только нужные ячейки.
    """
    folder = Path(folder_path)
    xlsx_files = sorted([f for f in folder.rglob('*.xlsx') if not f.name.startswith('~$')])
    total_files = len(xlsx_files)
    print(f"Найдено .xlsx файлов: {total_files}")

    total_rows = 0
    skipped_sheets = 0

    rows = []
    for file_idx, file_path in enumerate(xlsx_files, 1):
        try:
            wb = load_workbook(file_path, read_only=True, data_only=True)

            for sheet_name in wb.sheetnames:
                ws = wb[sheet_name]

                try:
                    # Читаем имя из B3 (row 3, col 2)
                    name_raw = ws.cell(row=3, column=2).value
                    if name_raw is None:
                        skipped_sheets += 1
                        continue
                    name_raw = str(name_raw).strip()

                    # Убираем титулы MR/MRS/MS/DR
                    name_clean = re.sub(r'^(MR|MRS|MS|DR)\.?\s*', '', name_raw, flags=re.IGNORECASE).strip().upper()
                    name_parts = name_clean.split()
                    first_name = name_parts[0] if len(name_parts) > 0 else ''
                    last_name = name_parts[1] if len(name_parts) > 1 else ''

                    # Если имя не удалось распарсить — пропускаем
                    if not first_name:
                        skipped_sheets += 1
                        continue

                    # A5 = row 5, col 1 (номер рейса)
                    flight_number = ws.cell(row=5, column=1).value
                    flight_number = str(flight_number).strip() if flight_number else ''

                    # D7 = row 7, col 4 (аэропорт вылета)
                    departure = ws.cell(row=7, column=4).value
                    departure = str(departure).strip()[:3].upper() if departure else ''

                    # H7 = row 7, col 8 (аэропорт прилета)
                    arrival = ws.cell(row=7, column=8).value
                    arrival = str(arrival).strip()[:3].upper() if arrival else ''

                    # A9 = row 9, col 1 (дата)
                    date_raw = ws.cell(row=9, column=1).value
                    flight_date = ''
                    if date_raw:
                        date_str = str(date_raw)
                        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', date_str)
                        if date_match:
                            flight_date = date_match.group(1)

                    # B13 = row 13, col 2 (PNR)
                    pnr = ws.cell(row=13, column=2).value
                    pnr = str(pnr).strip() if pnr else ''

                    # E13 = row 13, col 5 (ticket)
                    ticket_number = ws.cell(row=13, column=5).value
                    ticket_number = str(ticket_number).strip() if ticket_number else ''

                    # F3 = row 3, col 6 (FF number)
                    ff_raw = ws.cell(row=3, column=6).value
                    ff_number = ''
                    if ff_raw:
                        ff_str = str(ff_raw).strip()
                        # FF number имеет формат "XX 123456789" (2 буквы + пробел + цифры)
                        if re.match(r'^[A-Z]{2}\s+\d+$', ff_str):
                            ff_number = ff_str

                    rows.append({
                        'first_name': first_name,
                        'last_name': last_name,
                        'flight_date': flight_date,
                        'flight_number': flight_number,
                        'departure': departure,
                        'arrival': arrival,
                        'pnr': pnr,
                        'ticket_number': ticket_number,
                        'ff_number': ff_number
                    })
                    total_rows += 1

                except Exception as e:
                    skipped_sheets += 1
                    continue

            wb.close()

            # Прогресс-бар
            progress = (file_idx / total_files) * 100
            print(
                f"\r[{file_idx}/{total_files}] {progress:.1f}% | строк: {total_rows} | пропущено листов: {skipped_sheets}",
                end='', flush=True)

        except Exception as e:
           print(f"\nОшибка в файле {file_path.name}: {e}")
           continue

    print(f"\n\nГотово! Всего записей: {total_rows}")
    print(f"Пропущено листов: {skipped_sheets}")

    return pd.DataFrame(rows)


def parse_student2(json_path: str, yaml_path: str, boarding_folder: str) -> pd.DataFrame:
    """Парсинг всех данных Student 2."""
    print(f" Парсинг Student 2: JSON + YAML + Excel")

    print("  - JSON (Forum Profiles)...")
    df_json = parse_forum_json(json_path)
    print(f"    JSON: {len(df_json)} строк")

    print("  - YAML (SkyTeam Exchange)...")
    df_yaml = parse_skyteam_yaml_fast(yaml_path)
    print(f"    YAML: {len(df_yaml)} строк")

    print("  - Excel (Boarding Passes)...")
    df_boarding = parse_boarding_folder_fast(boarding_folder)
    print(f"    Excel: {len(df_boarding)} строк")

    df_combined = pd.concat([df_json, df_yaml, df_boarding], ignore_index=True)
    print(f"✅ Student 2: всего {len(df_combined)} строк")
    return df_combined

# ============================================================
# Главная функция
# ============================================================
if __name__ == "__main__":
    json_path = "FrequentFlyerForum-Profiles.json"
    yaml_path = "SkyTeam-Exchange.yaml"
    boarding_folder = "YourBoardingPassDotAero"  # ← твоя папка

    print("Парсинг JSON...")
    df_json = parse_forum_json(json_path)
    print(f"  JSON: {len(df_json)} строк")

    print("Парсинг YAML...")
    df_yaml = parse_skyteam_yaml_fast(yaml_path)
    print(f"  YAML: {len(df_yaml)} строк")

    print("\nПарсинг Excel из папки (быстрый режим)...")
    parse_boarding_folder_fast(boarding_folder, output_csv="boarding_data.csv")

    print("\nЧтение результатов...")
    df_boarding = pd.read_csv("boarding_data.csv")
    print(f"  Excel: {len(df_boarding)} строк")

    # Объединяем
    final_df = pd.concat([df_json, df_yaml, df_boarding], ignore_index=True)
    final_df.to_csv("final_output.csv", index=False, encoding='utf-8-sig')
    print(f"\nИтого: {len(final_df)} строк сохранено в final_output.csv")