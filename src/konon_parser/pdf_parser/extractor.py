# extractor.py
import pymupdf
from typing import Iterator
from .interfaces import IPdfTextExtractor

class PyMuPdfExtractor(IPdfTextExtractor):
    #Быстрый потоковый экстрактор строк на базе C-библиотеки MuPDF.#

    def extract_lines(self, pdf_path: str, start_page: int = 4) -> Iterator[str]:
        with pymupdf.open(pdf_path) as doc:
            total_pages = len(doc)
            for page_idx in range(start_page, total_pages):
                page = doc[page_idx]
                text = page.get_text()
                
                # Построчно отдаем стрим
                for line in text.splitlines():
                    cleaned = line.strip()
                    if cleaned:
                        yield cleaned