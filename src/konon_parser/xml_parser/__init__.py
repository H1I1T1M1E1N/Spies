# __init__.py
import pandas as pd
from .lexer import StreamingXmlLexer
from .parser import FlightHierarchyParser

def parse_text_log(filepath: str) -> pd.DataFrame:
    #Связывает потоковый Лексер и Автомат-Парсер.
    lexer = StreamingXmlLexer()
    parser = FlightHierarchyParser()
    
    tokens = lexer.tokenize(filepath)
    return parser.parse(tokens)