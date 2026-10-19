# detector.py
import pandas as pd
from typing import Tuple, List, Dict
from .interfaces import IDualIdentityDetector, IPassportClassifier
from .classifier import PassportPairClassifier


class DualIdentityDetector(IDualIdentityDetector):
    # Поиск оперативников с множественными документами на одном аккаунте лояльности

    def __init__(self, classifier: IPassportClassifier = None):
        self._classifier = classifier or PassportPairClassifier()

    def detect(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        # Подготовка данных
        cols_needed = ['ff_number', 'document_number', 'first_name', 'last_name', 'flight_date']
        work_df = df.dropna(subset=['ff_number', 'document_number']).copy()
        
        work_df['clean_ff'] = work_df['ff_number'].astype(str).str.extract(r'(\d{6,})')[0]
        work_df['clean_doc'] = work_df['document_number'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        
        work_df = work_df[~work_df['clean_doc'].isin(['', 'nan', 'None'])].copy()
        work_df = work_df.dropna(subset=['clean_ff'])
        work_df['doc_len'] = work_df['clean_doc'].str.len()

        # Группировка по карте лояльности
        grouped = work_df.groupby('clean_ff').agg(
            unique_docs=('clean_doc', lambda d: sorted(list(set(d)))),
            doc_lengths=('doc_len', lambda l: sorted(list(set(l)))),
            total_flights=('flight_date', 'count'),
            first_name=('first_name', 'first'),
            last_name=('last_name', 'first')
        ).reset_index()

        # Оставляем владельцев > 1 паспорта
        multi_doc = grouped[grouped['unique_docs'].apply(len) > 1].copy()

        # Классификация аномалий
        multi_doc['is_spy'] = multi_doc['doc_lengths'].apply(
            lambda l_set: self._classifier.is_anomalous_pair(set(l_set))
        )

        spies_df = multi_doc[multi_doc['is_spy']].copy()
        legals_df = multi_doc[~multi_doc['is_spy']].copy()

        # Форматирование для отчета
        spies_df['passports'] = spies_df['unique_docs'].apply(lambda d: ', '.join(d))
        spies_df['passport_types'] = spies_df['doc_lengths'].apply(
            lambda l: 'Два загранпаспорта' if l == [9] else ('Два внутренних РФ' if l == [10] else f'Иностранный + РФ {l}')
        )
        spies_df['full_name'] = spies_df['first_name'] + ' ' + spies_df['last_name']

        result = spies_df[[
            'clean_ff', 'full_name', 'total_flights', 'passport_types', 'passports'
        ]].sort_values(by='total_flights', ascending=False).reset_index(drop=True)

        return result, legals_df