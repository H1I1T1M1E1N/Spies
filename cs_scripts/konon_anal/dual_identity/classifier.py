# classifier.py
from typing import Set
from .interfaces import IPassportClassifier


class PassportPairClassifier(IPassportClassifier):
    # Классифицирует связку документов: легальная (РФ+Загран) или аномальная

    def is_anomalous_pair(self, doc_lengths: Set[int]) -> bool:
        # Легальный стандарт гражданина РФ: строго один загран (9 знаков) и один внутренний (10 знаков)
        if doc_lengths == {9, 10}:
            return False
        # Все остальные комбинации (два загранника [9], два внутренних [10], иностранные паспорта [7, 8]) - аномалия
        return True