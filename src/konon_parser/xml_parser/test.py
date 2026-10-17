# test.py
from __init__ import parse_text_log

FILEPATH = '/home/daniil/DataScience/PointzAggregator-AirlinesData.xml'

print(f"Запуск парсинга файла: {FILEPATH} ...")
df = parse_text_log(FILEPATH)

print("\n=== ПЕРВЫЕ 5 СТРОК ===")
print(df.head())

print(f"\nВсего записей извлечено: {len(df):,}")

# Проверка ТЗ: баг с маленькими буквами в кодах аэропортов
invalid_airports = df[~df['departure'].str.match(r'^[A-Z]{3}$', na=False)]
print(f"Аэропортов не в верхнем регистре (должно быть 0): {len(invalid_airports)}")