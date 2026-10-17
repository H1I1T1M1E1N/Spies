# test_pdf.py
from __init__ import parse_pdf_timetable

PDF_PATH = '/home/daniil/DataScience/Skyteam_Timetable.pdf'

print("Тестовый прогон на первых 5 страницах расписания...")
df_timetable_test = parse_pdf_timetable(PDF_PATH, max_pages=5)

print("\n=== ПЕРВЫЕ 10 СТРОК РАСПИСАНИЯ ===")
print(df_timetable_test.head(10))

print("\n=== ПОСЛЕДНИЕ СТРОКИ ===")
print(df_timetable_test.tail())

print(f"\nВсего рейсов извлечено с 5 страниц: {len(df_timetable_test)}")
print("\nПроверка пропусков в ключевых колонках:")
print(df_timetable_test.isna().sum())