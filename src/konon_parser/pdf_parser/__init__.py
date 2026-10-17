# __init__.py
import pandas as pd
import pymupdf
from .extractor import PyMuPdfExtractor
from .parser import TimetableParser

def parse_pdf_timetable(pdf_path: str, max_pages: int = None) -> pd.DataFrame:
    """
    Фасадная функция по ТЗ.
    """
    extractor = PyMuPdfExtractor()
    parser = TimetableParser()

    if max_pages:
        lines = []
        with pymupdf.open(pdf_path) as doc:
            limit = min(4 + max_pages, len(doc))
            for i in range(4, limit):
                for l in doc[i].get_text().splitlines():
                    cleaned = l.strip()
                    if cleaned:
                        lines.append(cleaned)
        stream = iter(lines)
    else:
        stream = extractor.extract_lines(pdf_path)

    return parser.parse(stream)