import pandas as pd
import re

FLIGHTS_CSV = "/home/daniil/DataScience/parsed_data/flights_data.csv"
TIMETABLE_CSV = "/home/daniil/DataScience/parsed_data/timetable_reference.csv"


def validate_flights_data(df: pd.DataFrame):
    print("=" * 60)
    print("1. ВАЛИДАЦИЯ ПАССАЖИРСКИХ ЛОГОВ (flights_data.csv)")
    print("=" * 60)

    # 1.1 Общие метрики
    print(f"Всего строк: {len(df):,}")
    print(f"Колонки: {list(df.columns)}")

    # 1.2 Проверка пропусков (Null / NaN)
    nulls = df.isnull().sum()
    print("\n[Пропуски по колонкам]:")
    print(nulls[nulls > 0] if nulls.any() else "Пропусков нет (0)")

    # 1.3 Проверка формата кодов аэропортов (строго 3 заглавные латинские буквы)
    iata_regex = re.compile(r'^[A-Z]{3}$')
    bad_dep = df[~df['departure'].astype(str).str.match(iata_regex)]
    bad_arr = df[~df['arrival'].astype(str).str.match(iata_regex)]
    print(f"\n[Аэропорты]: Некорректных departure: {len(bad_dep)}, некорректных arrival: {len(bad_arr)}")

    # 1.4 Проверка дат полета (YYYY-MM-DD)
    date_regex = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    bad_dates = df[~df['flight_date'].astype(str).str.match(date_regex)]
    print(f"[Даты]: Некорректных дат рейса: {len(bad_dates)}")

    # 1.5 Проверка номеров рейсов (код авиакомпании + цифры)
    flight_regex = re.compile(r'^[A-Z0-9]{2}\d{1,4}$')
    bad_flights = df[~df['flight_number'].astype(str).str.match(flight_regex)]
    print(f"[Рейсы]: Нестандартных номеров рейсов: {len(bad_flights)}")
    if len(bad_flights) > 0:
        print("Примеры нестандартных рейсов:", bad_flights['flight_number'].unique()[:5])

    # 1.6 Случайная выборка строк
    print("\n[Пример данных (случайные 3 строки)]:")
    print(df.sample(3, random_state=42)[['first_name', 'last_name', 'flight_date', 'flight_number', 'departure', 'arrival']])


def validate_timetable_data(df: pd.DataFrame):
    print("\n" + "=" * 60)
    print("2. ВАЛИДАЦИЯ СПРАВОЧНИКА РАСПИСАНИЙ (timetable_reference.csv)")
    print("=" * 60)

    # 2.1 Общие метрики
    print(f"Всего строк: {len(df):,}")
    print(f"Уникальных рейсов: {df['flight_number'].nunique():,}")
    print(f"Уникальных маршрутов (откуда-куда): {df.groupby(['departure', 'arrival']).ngroups:,}")

    # 2.2 Проверка пропусков
    nulls = df.isnull().sum()
    print("\n[Пропуски по колонкам]:")
    print(nulls[nulls > 0] if nulls.any() else "Пропусков нет (0)")

    # 2.3 Проверка кодов аэропортов
    iata_regex = re.compile(r'^[A-Z]{3}$')
    bad_dep = df[~df['departure'].astype(str).str.match(iata_regex)]
    bad_arr = df[~df['arrival'].astype(str).str.match(iata_regex)]
    print(f"\n[Аэропорты]: Некорректных departure: {len(bad_dep)}, некорректных arrival: {len(bad_arr)}")
    if len(bad_arr) > 0:
        print("Примеры некорректных arrival:", bad_arr['arrival'].value_counts().head(5))

    # 2.4 Проверка дат действия (valid_from / valid_to, например '01 Nov')
    validity_regex = re.compile(r'^\d{2}\s+[A-Za-z]{3}$')
    bad_vf = df[~df['valid_from'].astype(str).str.match(validity_regex)]
    bad_vt = df[~df['valid_to'].astype(str).str.match(validity_regex)]
    print(f"[Периоды]: Некорректных valid_from: {len(bad_vf)}, valid_to: {len(bad_vt)}")

    # 2.5 Проверка поля дней недели (должно содержать цифры от 1 до 7 и пробелы)
    days_regex = re.compile(r'^[1-7\s]+$')
    bad_days = df[~df['days'].astype(str).str.match(days_regex)]
    print(f"[Дни курсирования]: Некорректных дней: {len(bad_days)}")
    if len(bad_days) > 0:
        print("Примеры битых записей дней:", bad_days['days'].head(5))

    # 2.6 Случайная выборка строк
    print("\n[Пример данных (случайные 3 строки)]:")
    print(df.sample(3, random_state=42))


if __name__ == "__main__":
    df_flights = pd.read_csv(FLIGHTS_CSV)
    validate_flights_data(df_flights)

    df_timetable = pd.read_csv(TIMETABLE_CSV)
    validate_timetable_data(df_timetable)