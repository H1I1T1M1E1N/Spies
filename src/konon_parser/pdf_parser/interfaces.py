# interfaces.py
from abc import ABC, abstractmethod
from typing import Iterator
import pandas as pd

class IPdfTextExtractor(ABC):
    #Интерфейс для извлечения сырого потока строк из PDF.#
    
    @abstractmethod
    def extract_lines(self, pdf_path: str, start_page: int = 4) -> Iterator[str]:
        #Генерирует последовательность непустых текстовых строк.#
        pass


class ITimetableParser(ABC):
    #Интерфейс для сборки расписания из потока строк.#
    
    @abstractmethod
    def parse(self, lines: Iterator[str]) -> pd.DataFrame:
        #Принимает поток строк, возвращает DataFrame справочника.#
        pass