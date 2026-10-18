import pandas as pd

print("🕵️ Проверка безопасности: Поиск одинаковых паспортов у разных людей...\n")

# 1. Загружаем базу
df = pd.read_csv('MASTER_AIRLINES_DB.csv', low_memory=False)

# 2. Отбрасываем строки, где номер паспорта пустой (нам они не нужны для этой проверки)
df_valid_passports = df.dropna(subset=['document_number']).copy()

# 3. Оставляем только уникальные связки "Паспорт - Имя - Фамилия - Дата рождения"
# Это нужно, чтобы игнорировать случаи, когда один и тот же человек летал 100 раз (это нормально)
unique_identities = df_valid_passports[['document_number', 'first_name', 'last_name', 'birth_date']].drop_duplicates()

# 4. Считаем, сколько уникальных личностей привязано к каждому паспорту
passport_counts = unique_identities['document_number'].value_counts()

# 5. Ищем паспорта, у которых больше 1 владельца
suspicious_passports = passport_counts[passport_counts > 1].index

# 6. Выводим результаты
if len(suspicious_passports) > 0:
    print(f"🚨 ВНИМАНИЕ! Найдено {len(suspicious_passports)} паспортов, которые используют РАЗНЫЕ люди!\n")
    
    # Достаем все данные по этим подозрительным паспортам
    suspects_df = unique_identities[unique_identities['document_number'].isin(suspicious_passports)]
    
    # Сортируем по номеру паспорта, чтобы сразу видеть "клонов" рядом друг с другом
    suspects_df = suspects_df.sort_values(by=['document_number', 'first_name'])
    
    # Выводим топ-20 конфликтов на экран
    print(suspects_df.head(20).to_string(index=False))
    
    # Сохраняем всех подозреваемых в отдельный файл для изучения
    suspects_df.to_csv('stolen_passports_alert.csv', index=False)
    print("\n📁 Полный список сохранен в файл: 'stolen_passports_alert.csv'")
    
else:
    print("✅ Всё чисто! Одинаковых паспортов у разных людей не обнаружено.")
