
import pandas as pd
import numpy as np

# Целевые колонки (твое ТЗ)
TARGET_COLUMNS = [
    'first_name', 'last_name', 'birth_date', 'document_number', 'flight_date', 
    'flight_number', 'departure', 'arrival', 'pnr', 'ticket_number', 'ff_number'
]

def parse_boarding_data(input_path: str, output_path: str) -> pd.DataFrame:
    # 1. Читаем файл. Разделитель - точка с запятой. Пропуски - Not presented.
    df_boarding = pd.read_csv('BoardingData.csv', sep=';', na_values=['Not presented', 'None'])

    # Очищаем названия колонок от невидимых символов (например, ^M в конце Destination)
    df_boarding.columns = df_boarding.columns.str.strip()

    # 2. Имена (переводим в верхний регистр)
    df_boarding['first_name'] = df_boarding['PassengerFirstName'].str.upper()
    df_boarding['last_name'] = df_boarding['PassengerLastName'].str.upper()

    # 3. Даты
    # День рождения в американском формате MM/DD/YYYY (напр., 03/10/1983)
    df_boarding['birth_date'] = pd.to_datetime(df_boarding['PassengerBirthDate'], format='%m/%d/%Y', errors='coerce').dt.strftime('%Y-%m-%d')

    # Дата рейса (судя по скрину) УЖЕ в нормальном формате YYYY-MM-DD (напр. 2017-03-22)
    df_boarding['flight_date'] = pd.to_datetime(df_boarding['FlightDate'], errors='coerce').dt.strftime('%Y-%m-%d')

    # 4. Документы (убираем пробелы, как в ТЗ)
    df_boarding['document_number'] = df_boarding['PassengerDocument'].astype(str).str.replace(r'\s+', '', regex=True)

    # 5. Переименовываем остальные колонки
    df_boarding = df_boarding.rename(columns={
        'BookingCode': 'pnr',
        'TicketNumber': 'ticket_number',
        'FlightNumber': 'flight_number',
        'Destination': 'arrival'
    })

    # 6. Создаем пустые колонки, которых нет в этом датасете
    df_boarding['ff_number'] = np.nan
    df_boarding['departure'] = np.nan

    # 7. Собираем финальный чистый DataFrame
    df_boarding_clean = df_boarding[TARGET_COLUMNS].copy()

    # Смотрим результат
    print("Успешно обработано строк:", len(df_boarding_clean))
    print(df_boarding_clean.head())# Сохраняем результат в новый чистый CSV файл
 #   df_boarding_clean.to_csv('student1_boarding_clean.csv', index=False, encoding='utf-8')
    df_boarding_clean.to_csv(output_path, index=False, encoding='utf-8')
    print("Успех! Файл student1_boarding_clean.csv сохранен в папку со скриптом.")
    return df_boarding_clean


