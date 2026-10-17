# lexer.py
import xml.etree.ElementTree as ET
from typing import Iterator
from .interfaces import ILexer
from .models import XmlToken, TokenType

class StreamingXmlLexer(ILexer):
    #Потоковый XML-лексер, генерирующий высокоуровневые токены.#

    def tokenize(self, source_path: str) -> Iterator[XmlToken]:
        # Слушаем события входа и выхода из тегов
        context = ET.iterparse(source_path, events=('start', 'end'))

        for event, elem in context:
            if event == 'start':
                yield XmlToken(
                    type=TokenType.START_ELEMENT,
                    tag=elem.tag,
                    attributes=dict(elem.attrib)
                )
            elif event == 'end':
                yield XmlToken(
                    type=TokenType.END_ELEMENT,
                    tag=elem.tag,
                    attributes=dict(elem.attrib),
                    text=elem.text.strip() if elem.text else None
                )
                # Очищаем память обработанного узла
                if elem.tag == 'user':
                    elem.clear()