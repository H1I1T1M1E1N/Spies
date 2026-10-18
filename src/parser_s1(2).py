import pandas as pd
import numpy as np

def transliterate_icao(text):
    if pd.isna(text):
        return np.nan
    mapping = {
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'E', 'Ж': 'ZH',
        'З': 'Z', 'И': 'I', 'Й': 'I', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O',
        'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'KH', 'Ц': 'TS',
        'Ч': 'CH', 'Ш': 'SH', 'Щ': 'SHCH', 'Ъ': 'IE', 'Ы': 'Y', 'Ь': '', 'Э': 'E',
        'Ю': 'IU', 'Я': 'IA'
    }
    text = str(text).upper()
    return ''.join([mapping.get(char, char) for char in text])

TARGET_COLUMNS = [
    'first_name', 'last_name', 'birth_date', 'document_number', 'flight_date', 
    'flight_number', 'departure', 'arrival', 'pnr', 'ticket_number', 'ff_number'
]

# Жесткие границы колонок
fwf_widths = [60, 12, 12, 12, 12, 12, 10, 6, 6, 6, 18, 15, 3, 6, 6, 12, 8, 40, 70]

sirena_columns = [
    'PaxName', 'PaxBirthDate', 'DepartDate', 'DepartTime', 'ArrivalDate', 
    'ArrivalTime', 'FlightCode', 'From', 'Dest', 'Code', 'e-Ticket', 
    'TravelDoc', 'Seat', 'Meal', 'TrvCls', 'Fare', 'Baggage', 
    'PaxAdditionalInfo', 'AgentInfo'
]

df_sirena = pd.read_fwf(
    'Sirena-export-fixed.tab', 
    widths=fwf_widths,
    skiprows=1, 
    names=sirena_columns, 
    na_values=['N/A', '', 'Not presented']
)

# 2. Имена
df_sirena['translit_name'] = df_sirena['PaxName'].apply(transliterate_icao)
df_sirena['translit_name'] = df_sirena['translit_name'].astype(str).str.replace(r'\s+', ' ', regex=True).str.strip()
df_sirena['translit_name'] = df_sirena['translit_name'].replace('NAN', np.nan)

name_split = df_sirena['translit_name'].str.split(' ', expand=True)

df_sirena['last_name'] = name_split[0] if 0 in name_split.columns else np.nan
df_sirena['first_name'] = name_split[1] if 1 in name_split.columns else np.nan

# 3. Даты
df_sirena['flight_date'] = pd.to_datetime(df_sirena['DepartDate'], format='%Y-%m-%d', errors='coerce').dt.strftime('%Y-%m-%d')
df_sirena['birth_date'] = pd.to_datetime(df_sirena['PaxBirthDate'], format='%Y-%m-%d', errors='coerce').dt.strftime('%Y-%m-%d')

# 4. Лояльность
df_sirena['ff_number'] = df_sirena['PaxAdditionalInfo'].astype(str).str.extract(r'FF#(.*?)(?=\s{2,}|$)', expand=False)
df_sirena['ff_number'] = df_sirena['ff_number'].str.strip()

# 5. Маппинг 
df_sirena = df_sirena.rename(columns={
    'Code': 'pnr',
    'e-Ticket': 'ticket_number',
    'From': 'departure',
    'Dest': 'arrival',
    'FlightCode': 'flight_number',
    'TravelDoc': 'document_number'
})

# ИСПРАВЛЕНО: Убираем пробелы, а затем удаляем N/A, N/ или N с конца строки!
df_sirena['document_number'] = df_sirena['document_number'].astype(str).str.replace(r'\s+', '', regex=True)
df_sirena['document_number'] = df_sirena['document_number'].str.replace(r'N/A$|N/$|N$', '', regex=True).replace('nan', np.nan)

# 6. Финализация
for col in TARGET_COLUMNS:
    if col not in df_sirena.columns:
        df_sirena[col] = np.nan

df_sirena_clean = df_sirena[TARGET_COLUMNS].copy()

# Сохраняем!
df_sirena_clean.to_csv('student1_sirena_clean.csv', index=False, encoding='utf-8')

print("Успешно обработано строк:", len(df_sirena_clean))
print("Файл student1_sirena_clean.csv успешно сохранен!")
