import pandas as pd
import warnings

# Игнорируем предупреждения о типах данных для чистоты вывода
warnings.filterwarnings('ignore', category=pd.errors.DtypeWarning)


def find_suspects():
    print("🔄 Загрузка данных...")
    # Загружаем базы данных
    flights = pd.read_csv('../MASTER_AIRLINES_DB.csv', low_memory=False)
    events = pd.read_csv('world_events.csv')

    print("🔄 Преобразование дат...")
    # Преобразуем колонки с датами в формат datetime
    flights['flight_date'] = pd.to_datetime(flights['flight_date'], errors='coerce')
    events['event_date'] = pd.to_datetime(events['event_date'], errors='coerce')

    # Очищаем данные от строк с некорректными датами или отсутствующими ключевыми полями
    flights = flights.dropna(
        subset=['flight_date', 'departure', 'arrival', 'first_name', 'last_name', 'document_number'])

    print("🔄 Поиск пересечений (вылеты)...")
    # Ищем совпадения по аэропорту ВЫЛЕТА (departure)
    matches_dep = pd.merge(
        flights, events,
        left_on='departure', right_on='iata_code',
        how='inner'
    )

    print("🔄 Поиск пересечений (прилеты)...")
    # Ищем совпадения по аэропорту ПРИЛЕТА (arrival)
    matches_arr = pd.merge(
        flights, events,
        left_on='arrival', right_on='iata_code',
        how='inner'
    )

    # Объединяем все найденные совпадения
    all_matches = pd.concat([matches_dep, matches_arr], ignore_index=True)

    print("🔄 Фильтрация по временному окну (0-7 дня до события)...")
    # Вычисляем разницу в днях: сколько дней прошло от рейса до события
    all_matches['days_before'] = (all_matches['event_date'] - all_matches['flight_date']).dt.days

    # Оставляем только тех, кто был в аэропорту от 0 до 7 дней ДО события
    suspects = all_matches[(all_matches['days_before'] >= 0) & (all_matches['days_before'] <= 7)].copy()

    if suspects.empty:
        print("\n❌ Подозреваемых с 3 и более совпадениями не найдено.")
        return

    # Создаем уникальный идентификатор события для корректного подсчета разных инцидентов
    suspects['event_id'] = suspects['event_date'].astype(str) + '_' + suspects['iata_code']

    print("🔄 Агрегация результатов...")
    # Группируем по личности и считаем количество УНИКАЛЬНЫХ событий
    summary = suspects.groupby(['first_name', 'last_name', 'document_number']).agg(
        incident_count=('event_id', 'nunique'),
        events_list=('event_title', lambda x: list(set(x)))  # Собираем список уникальных названий событий
    ).reset_index()

    # Фильтруем только тех, кто "засветился" на 1 и более разных событиях
    top_suspects = summary[summary['incident_count'] >= 3].sort_values(by='incident_count', ascending=False).head(10)

    print("\n" + "=" * 60)
    print("🕵️‍♂️ ТОП ПОДОЗРЕВАЕМЫХ (1 и более совпадения) 🕵️‍♂️")
    print("=" * 60)

    for _, row in top_suspects.iterrows():
        print(f"👤 Имя: {row['first_name']} {row['last_name']}")
        print(f"📄 Документ: {row['document_number']}")
        print(f"⚠️ Уникальных инцидентов: {row['incident_count']}")
        # Показываем первые 3 события из списка для наглядности
        events_preview = ", ".join(row['events_list'][:3])
        if len(row['events_list']) > 3:
            events_preview += f" ... и еще {len(row['events_list']) - 3}"
        print(f"📍 События: {events_preview}")
        print("-" * 60)

    print(f"✅ Всего найдено подозрительных личностей: {len(top_suspects)}")


if __name__ == "__main__":
    find_suspects()