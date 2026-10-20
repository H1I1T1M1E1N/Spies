import pandas as pd
import numpy as np

print("🧹 Начинаем глубокую очистку Мастер-базы от полупустых дубликатов...")

# 1. Загружаем нашу базу
df = pd.read_csv('MASTER_AIRLINES_DB.csv', low_memory=False)
initial_rows = len(df)

# Бонус: исправляем некрасивые номера паспортов вида "461772.0" -> "461772"
# (Pandas добавляет .0, если в колонке есть пустые значения)
df['document_number'] = df['document_number'].astype(str).str.replace('.0', '', regex=False).replace('nan', np.nan)

# 2. Сортируем данные: сначала идут строки с заполненной датой рождения, потом с пустой
df = df.sort_values(by=['document_number', 'birth_date'], na_position='last')

# 3. МАГИЯ PANDAS: Группируем по паспорту и "растягиваем" дату рождения сверху вниз
# ffill() заполняет пустоты значением сверху, а bfill() - значением снизу
cols_to_fill = ['first_name', 'last_name', 'birth_date']
df[cols_to_fill] = df.groupby('document_number')[cols_to_fill].transform(lambda x: x.ffill().bfill())

# 4. Теперь, когда мы заполнили пустоты, у нас появились ИДЕАЛЬНЫЕ дубликаты. Удаляем их!
df = df.drop_duplicates()
final_rows = len(df)

print(f"✅ Успешно! База сжата. Схлопнуто {initial_rows - final_rows} полупустых записей-клонов.")

# 5. Сохраняем чистую базу обратно поверх старой
df.to_csv('MASTER_AIRLINES_DB.csv', index=False, encoding='utf-8')
print("Мастер-база обновлена и сияет чистотой!")
