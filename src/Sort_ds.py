import pandas as pd

def sort_master_db(input_path: str, output_path: str) -> pd.DataFrame:
    # 1. Загружаем итоговый файл
    master_df = pd.read_csv(input_path) # укажите правильный путь/расширение

    # 2. Сортируем
    master_df = master_df.sort_values(
        by=['last_name', 'first_name', 'document_number'],
        na_position='last'
    )

    # 3. Сбрасываем индексы
    master_df = master_df.reset_index(drop=True)

    # 4. Перезаписываем файл (или сохраняем под новым именем)
    master_df.to_csv(output_path, index=False, encoding='utf-8')

    print("База MASTER_AIRLINES_DB успешно отсортирована!")
    return master_df
