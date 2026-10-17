# interfaces.py
from abc import ABC, abstractmethod
from typing import Iterator
import pandas as pd
from .models import XmlToken

class ILexer(ABC):
    #преобразование источника данных в поток токенов.#
    
    @abstractmethod
    def tokenize(self, source_path: str) -> Iterator[XmlToken]:
        #Генерирует последовательность токенов.#
        pass


class IParser(ABC):
    #преобразование потока токенов в DataFrame.#
    
    @abstractmethod
    def parse(self, tokens: Iterator[XmlToken]) -> pd.DataFrame:
        #Потребляет токены и формирует итоговый датасет.#
        pass